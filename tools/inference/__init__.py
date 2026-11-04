"""Inference package for tare.tools.library."""
from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig
from tools.inference.contracts import (
    LlamaServerProps,
    ModelEntry,
    ModelsResponse,
    validate_props_payload,
    validate_models_payload,
    CANONICAL_FIXTURE_PROPS_CUDA,
    CANONICAL_FIXTURE_PROPS_CPU_INVALID,
    CANONICAL_FIXTURE_MODELS,
    MIN_SUPPORTED_LLAMA_SERVER_BUILD,
)

__all__ = [
    "LocalInferenceClient",
    "LocalInferenceConfig",
    "LlamaServerProps",
    "ModelEntry",
    "ModelsResponse",
    "validate_props_payload",
    "validate_models_payload",
    "CANONICAL_FIXTURE_PROPS_CUDA",
    "CANONICAL_FIXTURE_PROPS_CPU_INVALID",
    "CANONICAL_FIXTURE_MODELS",
    "MIN_SUPPORTED_LLAMA_SERVER_BUILD",
]
