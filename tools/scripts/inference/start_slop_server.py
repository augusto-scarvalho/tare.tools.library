"""Python Cross-Platform Launcher for Local Inference Substrate (Node aaaaa / RTX 3090)."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig


def find_llama_binary() -> str:
    candidates = ["llama-server", "llama-server.exe", "slop-server", "slop-server.exe"]
    for c in candidates:
        p = shutil.which(c)
        if p:
            return p
    return "llama-server"


def start_server(
    model_path: str,
    port: int = 8080,
    host: str = "0.0.0.0",
    ctx_size: int = 16384,
    gpu_layers: int = 99,
) -> int:
    bin_path = find_llama_binary()
    cmd = [
        bin_path,
        "--model", model_path,
        "--host", host,
        "--port", str(port),
        "--ctx-size", str(ctx_size),
        "--n-gpu-layers", str(gpu_layers),
        "--flash-attn",
        "--cont-batching",
        "--embedding",
        "--metrics",
    ]

    print("================================================================================")
    print(f" 🚀 LAUNCHING LOCAL INFERENCE SUBSTRATE ON NODE aaaaa")
    print(f"  Command: {' '.join(cmd)}")
    print("================================================================================")

    try:
        proc = subprocess.Popen(cmd)
        print(f"[PID {proc.pid}] Server process spawned. Waiting for health check...")
        
        client = LocalInferenceClient(LocalInferenceConfig(host=f"http://127.0.0.1:{port}"))
        for attempt in range(15):
            time.sleep(1)
            status = client.health_check()
            if status.get("online"):
                print(f"✅ Local inference server ONLINE on port {port}!")
                break
            print(f"  ... waiting for startup (attempt {attempt+1}/15)")

        proc.wait()
        return proc.returncode
    except FileNotFoundError:
        print(f"❌ Error: '{bin_path}' executable not found. Ensure llama.cpp / slop.cpp is built.")
        return 1
    except KeyboardInterrupt:
        print("\n[STOPPING] Local inference server gracefully shutting down...")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Launcher for slop.cpp on Node aaaaa")
    parser.add_argument("--model", "-m", default="/models/qwen2.5-coder-32b-instruct-q4_k_m.gguf", help="Path to GGUF model")
    parser.add_argument("--port", "-p", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface")
    parser.add_argument("--ctx-size", "-c", type=int, default=16384, help="Context size")
    parser.add_argument("--gpu-layers", "-ngl", type=int, default=99, help="Number of GPU layers to offload")

    args = parser.parse_args()
    return start_server(
        model_path=args.model,
        port=args.port,
        host=args.host,
        ctx_size=args.ctx_size,
        gpu_layers=args.gpu_layers,
    )


if __name__ == "__main__":
    sys.exit(main())
