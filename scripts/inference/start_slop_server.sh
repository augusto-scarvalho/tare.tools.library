#!/usr/bin/env bash
# ==============================================================================
# slop.cpp / llama-server Launcher for Node aaaaa (NVIDIA RTX 3090 24GB VRAM)
# Ratified under ADR-048 (Local Inference Substrate & Agent Harness)
# ==============================================================================

set -euo pipefail

MODEL_PATH="${1:-/models/qwen2.5-coder-32b-instruct-q4_k_m.gguf}"
PORT="${PORT:-8080}"
HOST="${HOST:-0.0.0.0}"
CTX_SIZE="${CTX_SIZE:-16384}"
GPU_LAYERS="${GPU_LAYERS:-99}"

echo "================================================================================"
echo " 🚀 LAUNCHING LOCAL INFERENCE SUBSTRATE ON NODE aaaaa (RTX 3090)"
echo "================================================================================"
echo "  - Model:      ${MODEL_PATH}"
echo "  - Host/Port:  http://${HOST}:${PORT}"
echo "  - Context:    ${CTX_SIZE} tokens"
echo "  - GPU Offload: ${GPU_LAYERS} layers (CUDA/FlashAttention)"
echo "================================================================================"

if command -v llama-server &> /dev/null; then
    BIN="llama-server"
elif [ -f "./llama-server" ]; then
    BIN="./llama-server"
elif [ -f "/usr/local/bin/llama-server" ]; then
    BIN="/usr/local/bin/llama-server"
else
    echo "⚠️ llama-server binary not found in standard PATH. Please compile or install slop.cpp / llama.cpp."
    exit 1
fi

exec "$BIN" \
    --model "$MODEL_PATH" \
    --host "$HOST" \
    --port "$PORT" \
    --ctx-size "$CTX_SIZE" \
    --n-gpu-layers "$GPU_LAYERS" \
    --flash-attn \
    --cont-batching \
    --embedding \
    --metrics \
    --log-format json
