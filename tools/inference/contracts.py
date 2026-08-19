"""Operational Contract and Canonical Response Schemas for Node aaaaa Inference Substrate.

Defines the formal API specifications and validation primitives for llama-server / slop.cpp
runtimes running on the dedicated RTX 3090 inference node (ADR-048 / CASE-2026-08-19).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


MIN_SUPPORTED_LLAMA_SERVER_BUILD = "b3000"
CANONICAL_INFERENCE_ENGINE = "slop.cpp"


@dataclass(frozen=True)
class LlamaServerProps:
    """Validated representation of /props endpoint from llama-server / slop.cpp."""
    n_gpu_layers: int
    device: str
    build: Optional[str] = None
    total_slots: int = 1
    has_cuda: bool = False

    def is_cuda_accelerated(self) -> bool:
        return self.n_gpu_layers > 0 and self.device.lower() != "cpu"


@dataclass(frozen=True)
class ModelEntry:
    """Model descriptor entry in /v1/models response."""
    id: str
    object: str = "model"
    created: Optional[int] = None
    owned_by: Optional[str] = None


@dataclass(frozen=True)
class ModelsResponse:
    """Validated /v1/models payload response."""
    data: List[ModelEntry] = field(default_factory=list)

    def contains_model(self, model_id: str) -> bool:
        if not model_id:
            return False
        return any(model_id == m.id or model_id in m.id for m in self.data)

    def get_model_ids(self) -> List[str]:
        return [m.id for m in self.data]


# ==============================================================================
# CANONICAL VERSIONED FIXTURES (For offline integration tests and verification)
# ==============================================================================

CANONICAL_FIXTURE_PROPS_CUDA: Dict[str, Any] = {
    "n_gpu_layers": 99,
    "device": "cuda",
    "build": "b3520",
    "total_slots": 4,
    "flash_attn": True,
    "ctx_size": 16384,
}

CANONICAL_FIXTURE_PROPS_CPU_INVALID: Dict[str, Any] = {
    "n_gpu_layers": 0,
    "device": "cpu",
    "build": "b3520",
    "total_slots": 1,
    "flash_attn": False,
    "ctx_size": 4096,
}

CANONICAL_FIXTURE_MODELS: Dict[str, Any] = {
    "object": "list",
    "data": [
        {
            "id": "qwen2.5-coder-32b-instruct",
            "object": "model",
            "created": 1724000000,
            "owned_by": "local-aaaaa",
        },
        {
            "id": "bge-large-en-v1.5",
            "object": "model",
            "created": 1724000000,
            "owned_by": "local-aaaaa",
        },
    ],
}


def validate_props_payload(payload: Dict[str, Any]) -> LlamaServerProps:
    """Strictly validate and coerce the /props endpoint dictionary into a typed contract."""
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid /props payload: expected dict, got {type(payload).__name__}")

    n_gpu = payload.get("n_gpu_layers")
    if n_gpu is None or not isinstance(n_gpu, int):
        raise ValueError(f"Invalid /props: 'n_gpu_layers' must be integer, got {n_gpu}")

    device = str(payload.get("device", "")).strip().lower()
    if not device:
        # Fallback to cpu if not specified
        device = "cuda" if n_gpu > 0 else "cpu"

    build = str(payload.get("build")) if payload.get("build") else None
    total_slots = int(payload.get("total_slots", 1))

    return LlamaServerProps(
        n_gpu_layers=n_gpu,
        device=device,
        build=build,
        total_slots=total_slots,
        has_cuda=(n_gpu > 0 and device != "cpu"),
    )


def validate_models_payload(payload: Dict[str, Any]) -> ModelsResponse:
    """Strictly validate and coerce /v1/models dictionary into a typed contract."""
    if not isinstance(payload, dict):
        raise ValueError(f"Invalid /v1/models payload: expected dict, got {type(payload).__name__}")

    raw_data = payload.get("data")
    if not isinstance(raw_data, list):
        raise ValueError(f"Invalid /v1/models: 'data' must be a list, got {type(raw_data).__name__}")

    models: List[ModelEntry] = []
    for item in raw_data:
        if isinstance(item, dict) and "id" in item:
            models.append(
                ModelEntry(
                    id=str(item["id"]),
                    object=str(item.get("object", "model")),
                    created=item.get("created"),
                    owned_by=item.get("owned_by"),
                )
            )
        elif isinstance(item, str):
            models.append(ModelEntry(id=item))

    return ModelsResponse(data=models)
