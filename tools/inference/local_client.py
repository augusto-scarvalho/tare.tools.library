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
    # Select a remote mesh endpoint explicitly with LOCAL_EMBED_ENDPOINT.
    embedding_host: str = "http://localhost:8081"
    timeout_seconds: float = 120.0
    # Vector namespace: index and queries must share the model family (quantization may differ).
    embedding_model: str = "qwen3-embedding-4b"
    # Qwen3-Embedding queries carry an instruction; no retrieval-gain claim is inferred.
    query_instruction: str = "Given a question, retrieve documents that answer it"
    embedding_batch_chars: int = 12000  # ~3-4k tokens per request: fills a 4096-token ubatch
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

    def generate_embeddings(self, texts: List[str], *, is_query: bool = False) -> List[Optional[List[float]]]:
        """Dense vectors from the local server, one per text; None where the server failed or rejected the input.

        Texts are sent in batches (by character budget) so the server fills its ubatch; a few
        batches run concurrently against the server's slots."""
        from concurrent.futures import ThreadPoolExecutor

        url = f"{self.config.embedding_host}/v1/embeddings"

        def prepare(text: str) -> Optional[str]:
            clean = text.strip()
            if not clean:
                return None
            clean = clean[:8000]
            return "Instruct: " + self.config.query_instruction + chr(10) + "Query: " + clean if is_query else clean

        prepared = [prepare(t) for t in texts]
        batches: List[List[int]] = []
        current: List[int] = []
        used = 0
        for index, text in enumerate(prepared):
            if text is None:
                continue
            if current and used + len(text) > self.config.embedding_batch_chars:
                batches.append(current); current, used = [], 0
            current.append(index); used += len(text)
        if current:
            batches.append(current)

        def embed_batch(indices: List[int]) -> List[Optional[List[float]]]:
            payload = {"model": self.config.embedding_model, "input": [prepared[i] for i in indices]}
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                         headers={"Content-Type": "application/json"}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as resp:
                    items = json.loads(resp.read().decode("utf-8")).get("data", [])
                by_index = {item.get("index", k): item.get("embedding") for k, item in enumerate(items)}
                return [by_index.get(k) for k in range(len(indices))]
            except Exception:
                return [None] * len(indices)  # never disguise a failure as a vector

        results: List[Optional[List[float]]] = [None] * len(texts)
        with ThreadPoolExecutor(max_workers=4) as pool:  # matches the server's --parallel slots
            for indices, vectors in zip(batches, pool.map(embed_batch, batches)):
                for k, index in enumerate(indices):
                    results[index] = vectors[k]
        return results

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
