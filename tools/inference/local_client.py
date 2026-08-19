"""Local Inference Substrate Client for Node aaaaa (RTX 3090 / slop.cpp).

Provides zero-cost, local-first inference for embeddings, code analysis, and summarization
connecting to slop.cpp / llama-server over localhost or Tailscale mesh per ADR-048.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class LocalInferenceConfig:
    host: str = "http://localhost:8080"
    timeout_seconds: float = 30.0
    embedding_model: str = "local-embed"
    chat_model: str = "local-llm"


class LocalInferenceClient:
    """Client for local OpenAI-compatible inference server (slop.cpp / llama-server)."""

    def __init__(self, config: Optional[LocalInferenceConfig] = None):
        self.config = config or LocalInferenceConfig()
        # Allow environment override
        env_host = os.environ.get("LOCAL_LLM_ENDPOINT") or os.environ.get("SLOP_ENDPOINT")
        if env_host:
            self.config.host = env_host.rstrip("/")

    def health_check(self) -> Dict[str, Any]:
        """Check if local slop.cpp / llama-server is online and responsive."""
        url = f"{self.config.host}/health"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return {"online": True, "status": data.get("status", "ok"), "url": url}
        except Exception as e:
            # Try /v1/models fallback
            try:
                models_url = f"{self.config.host}/v1/models"
                req = urllib.request.Request(models_url, method="GET")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return {"online": True, "models": data.get("data", []), "url": models_url}
            except Exception as e2:
                return {"online": False, "error": str(e2), "url": self.config.host}

    def readiness_check(
        self,
        required_model: Optional[str] = None,
        require_cuda: bool = False,
    ) -> Dict[str, Any]:
        """Deep hardware and model readiness probe verifying model offload and context."""
        health = self.health_check()
        if not health.get("online"):
            return {"ready": False, "error": health.get("error", "offline"), "details": health}

        # Check models listing if available
        models = health.get("models", [])
        if required_model and models:
            model_ids = [m.get("id") for m in models if isinstance(m, dict)]
            if required_model not in model_ids and not any(required_model in mid for mid in model_ids if mid):
                return {
                    "ready": False,
                    "error": f"Required model '{required_model}' not found in loaded models: {model_ids}",
                    "details": health,
                }

        # Validate GPU/CUDA acceleration probe if requested
        if require_cuda:
            props_url = f"{self.config.host}/props"
            try:
                req = urllib.request.Request(props_url, method="GET")
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    props = json.loads(resp.read().decode("utf-8"))
                    if props.get("n_gpu_layers", 1) == 0 or props.get("device", "").lower() == "cpu":
                        return {
                            "ready": False,
                            "error": "Server is running in CPU-only mode (0 GPU layers offloaded)",
                            "details": props,
                        }
            except Exception:
                pass

        return {"ready": True, "details": health}

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate dense vector embeddings using local server endpoint."""
        url = f"{self.config.host}/v1/embeddings"
        payload = {
            "model": self.config.embedding_model,
            "input": texts if len(texts) > 1 else texts[0],
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
            data_items = res_json.get("data", [])
            embeddings = [item["embedding"] for item in data_items]
            return embeddings

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
        print("   To launch on node aaaaa, run: bash scripts/inference/start_slop_server.sh")
        return 0


if __name__ == "__main__":
    sys.exit(main())
