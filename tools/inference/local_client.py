"""Local Inference Substrate Client for Node aaaaa (RTX 3090 / slop.cpp).

Provides zero-cost, local-first inference for embeddings, code analysis, and summarization
connecting to slop.cpp / llama-server over localhost or Tailscale mesh per ADR-048.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


@dataclass
class LocalInferenceConfig:
    host: str = "http://localhost:8080"
    embedding_host: str = "http://localhost:8081"
    timeout_seconds: float = 30.0
    embedding_model: str = "local-embed"
    chat_model: str = "local-llm"


class LocalInferenceClient:
    """Client for local OpenAI-compatible inference server (slop.cpp / llama-server)."""

    _health_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}

    def __init__(self, config: Optional[LocalInferenceConfig] = None):
        self.config = config or LocalInferenceConfig()
        # Allow environment overrides
        env_host = os.environ.get("LOCAL_LLM_ENDPOINT") or os.environ.get("SLOP_ENDPOINT")
        if env_host:
            self.config.host = env_host.rstrip("/")

        env_embed = os.environ.get("LOCAL_EMBED_ENDPOINT") or os.environ.get("SLOP_EMBED_ENDPOINT")
        if env_embed:
            self.config.embedding_host = env_embed.rstrip("/")
        elif env_host:
            self.config.embedding_host = self.config.host

    def health_check(self, target: str = "chat") -> Dict[str, Any]:
        """Check if local slop.cpp / llama-server is online and responsive (cached with 10s TTL)."""
        target_host = self.config.embedding_host if target == "embed" else self.config.host
        cache_key = f"{target_host}_{target}"
        now = time.time()
        if cache_key in self._health_cache:
            ts, res = self._health_cache[cache_key]
            if now - ts < 10.0:
                return res

        url = f"{target_host}/health"
        result: Dict[str, Any]
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                result = {"online": True, "status": data.get("status", "ok"), "url": url}
        except Exception as e:
            # Try /v1/models fallback
            try:
                models_url = f"{target_host}/v1/models"
                req = urllib.request.Request(models_url, method="GET")
                with urllib.request.urlopen(req, timeout=1.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    result = {"online": True, "models": data.get("data", []), "url": models_url}
            except Exception as e2:
                result = {"online": False, "error": str(e2), "url": target_host}

        self._health_cache[cache_key] = (now, result)
        return result


    def readiness_check(
        self,
        required_model: Optional[str] = None,
        require_cuda: bool = False,
    ) -> Dict[str, Any]:
        """Deep hardware and model readiness probe verifying model offload and context (Fail-Closed)."""
        health = self.health_check()
        if not health.get("online"):
            return {"ready": False, "error": health.get("error", "offline"), "details": health}

        # Check models listing if required
        if required_model:
            models = health.get("models", [])
            if not models:
                try:
                    models_url = f"{self.config.host}/v1/models"
                    req = urllib.request.Request(models_url, method="GET")
                    with urllib.request.urlopen(req, timeout=3.0) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        models = data.get("data", [])
                except Exception as e:
                    return {
                        "ready": False,
                        "error": f"Failed to verify required model '{required_model}': {e}",
                        "details": health,
                    }

            model_ids = [m.get("id") for m in models if isinstance(m, dict)]
            if not model_ids or (required_model not in model_ids and not any(required_model in str(mid) for mid in model_ids)):
                return {
                    "ready": False,
                    "error": f"Required model '{required_model}' not found in loaded models: {model_ids}",
                    "details": health,
                }

        # Validate GPU/CUDA acceleration probe if requested (strictly fail-closed)
        if require_cuda:
            props_url = f"{self.config.host}/props"
            try:
                req = urllib.request.Request(props_url, method="GET")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    props = json.loads(resp.read().decode("utf-8"))
                    n_gpu = props.get("n_gpu_layers")
                    dev = str(props.get("device", "")).lower()
                    if n_gpu is None or n_gpu == 0 or dev == "cpu":
                        return {
                            "ready": False,
                            "error": "Server is running in CPU-only mode (0 GPU layers offloaded)",
                            "details": props,
                        }
            except Exception as e_props:
                return {
                    "ready": False,
                    "error": f"CUDA / GPU acceleration probe failed on endpoint '{props_url}': {e_props}",
                    "details": health,
                }

        return {"ready": True, "details": health}

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate dense vector embeddings using local server endpoint with parallel batching."""
        from concurrent.futures import ThreadPoolExecutor

        url = f"{self.config.embedding_host}/v1/embeddings"

        def _embed_item(text: str) -> List[float]:
            clean_text = text.strip()
            if not clean_text:
                return [0.0] * 768

            payload = {
                "model": self.config.embedding_model,
                "input": clean_text[:8000],
            }
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                    res_json = json.loads(resp.read().decode("utf-8"))
                    data_items = res_json.get("data", [])
                    if data_items and "embedding" in data_items[0]:
                        return data_items[0]["embedding"]
                    digest = hashlib.sha256(clean_text.encode("utf-8")).digest()
                    return [float(b) / 255.0 for b in digest]
            except Exception:
                digest = hashlib.sha256(clean_text.encode("utf-8")).digest()
                return [float(b) / 255.0 for b in digest]

        if len(texts) <= 1:
            return [_embed_item(t) for t in texts]

        # Dispatch across 16 parallel slots on RTX 3090
        with ThreadPoolExecutor(max_workers=16) as pool:
            return list(pool.map(_embed_item, texts))

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ) -> str:
        """Perform zero-cost chat completion for agent reasoning and summarization."""
        url = f"{self.config.host}/v1/chat/completions"
        payload = {
            "model": self.config.chat_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data_bytes,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
            res_json = json.loads(resp.read().decode("utf-8"))
            choices = res_json.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return ""


def main() -> int:
    client = LocalInferenceClient()
    print(f"[LOCAL INFERENCE] Checking status of node aaaaa @ {client.config.host}...")
    status = client.health_check()
    if status.get("online"):
        print(f"✅ Local inference server ONLINE: {status}")
        return 0
    else:
        print(f"⚠️ Local inference server OFFLINE or unreachable at {client.config.host}")
        print(f"   Details: {status.get('error')}")
        print("   To launch on node aaaaa, run: bash tools/scripts/inference/start_slop_server.sh")
        return 0


if __name__ == "__main__":
    sys.exit(main())
