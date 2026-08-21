"""Sovereign BYOC Profile & Hybrid Dynamic Topology Router (RFC-006 / ADR-064)."""
from __future__ import annotations

import copy
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# Sovereign Local Node Endpoints (Node aaaaa / RTX 3090 / slop.cpp)
DEFAULT_LOCAL_GPU_URL = "http://100.107.245.30:8080/v1"
DEFAULT_LOCAL_EMBED_URL = "http://100.107.245.30:8081"

# Sovereign Local GPU Model Pin (Fact-checked on Node aaaaa)
PIN_LOCAL_SOVEREIGN_BEST = "qwen38-27b"
PIN_LOCAL_GGUF_PRIMARY = "Qwen3.8-27B-Q4_K_M.gguf"
PIN_LOCAL_GGUF_FALLBACK = "Qwen3.8-27B-UD-Q4_K_XL.gguf"


@dataclass
class ProviderTarget:
    kind: str  # "vendor_cli" | "api_key" | "nim_free" | "google_free" | "local_gpu" | "cpu_local"
    provider: str
    model: str
    endpoint: Optional[str] = None
    key_env_var: Optional[str] = None
    cli_bin: Optional[str] = None
    requires_network: bool = True


@dataclass
class ComputeProfile:
    name: str  # "free" | "free-nvidia" | "free-cpu" | "pro" | "local" | "hybrid"
    provider: str
    endpoint: Optional[str] = None
    model: Optional[str] = None
    key_env_var: Optional[str] = None
    requires_network: bool = True
    context_budget_mode: str = "standard"  # "standard" | "compact"
    role_matrix: Dict[str, List[ProviderTarget]] = field(default_factory=dict)


class BYOCRouter:
    """Agnostic Router supporting Free-Tier, Pro API, Sovereign Local GPU, and Hybrid Dynamic Topologies."""

    DEFAULT_HYBRID_ROLE_MATRIX = {
        "seat_google": [
            ProviderTarget(kind="vendor_cli", provider="google", model="gemini-3.7-flash", cli_bin="agy"),
            ProviderTarget(kind="api_key", provider="google", model="gemini-3.7-flash", key_env_var="GEMINI_API_KEY", endpoint="https://generativelanguage.googleapis.com/v1beta/openai"),
            ProviderTarget(kind="local_gpu", provider="openai-compatible", model=PIN_LOCAL_SOVEREIGN_BEST, endpoint=DEFAULT_LOCAL_GPU_URL, requires_network=False),
        ],
        "seat_openai": [
            ProviderTarget(kind="vendor_cli", provider="openai", model="gpt-5.6-sol", cli_bin="codex"),
            ProviderTarget(kind="nim_free", provider="nvidia", model="meta/llama-3.3-70b-instruct", endpoint="https://integrate.api.nvidia.com/v1", key_env_var="NVIDIA_API_KEY"),
            ProviderTarget(kind="local_gpu", provider="openai-compatible", model=PIN_LOCAL_SOVEREIGN_BEST, endpoint=DEFAULT_LOCAL_GPU_URL, requires_network=False),
        ],
        "seat_anthropic": [
            ProviderTarget(kind="vendor_cli", provider="anthropic", model="claude-fable-5-high", cli_bin="claude"),
            ProviderTarget(kind="local_gpu", provider="openai-compatible", model=PIN_LOCAL_SOVEREIGN_BEST, endpoint=DEFAULT_LOCAL_GPU_URL, requires_network=False),
        ],
        "scribe_compactor": [
            ProviderTarget(kind="local_gpu", provider="openai-compatible", model=PIN_LOCAL_SOVEREIGN_BEST, endpoint=DEFAULT_LOCAL_GPU_URL, requires_network=False),
            ProviderTarget(kind="google_free", provider="google", model="gemini-2.5-flash", key_env_var="GEMINI_API_KEY", endpoint="https://generativelanguage.googleapis.com/v1beta/openai"),
        ],
        "mediator": [
            ProviderTarget(kind="nim_free", provider="nvidia", model="meta/llama-3.3-70b-instruct", endpoint="https://integrate.api.nvidia.com/v1", key_env_var="NVIDIA_API_KEY"),
            ProviderTarget(kind="local_gpu", provider="openai-compatible", model=PIN_LOCAL_SOVEREIGN_BEST, endpoint=DEFAULT_LOCAL_GPU_URL, requires_network=False),
        ],
        "indexer_embeddings": [
            ProviderTarget(kind="local_gpu", provider="llama-server", model="nomic-embed-text-v1.5.Q8_0.gguf", endpoint=DEFAULT_LOCAL_EMBED_URL, requires_network=False),
        ],
    }

    DEFAULT_PROFILES = {
        "free": ComputeProfile(
            name="free",
            provider="google-free",
            model="gemini-2.5-flash",
            key_env_var="GEMINI_API_KEY",
            requires_network=True,
            context_budget_mode="compact",
        ),
        "free-nvidia": ComputeProfile(
            name="free-nvidia",
            provider="nvidia-build-free",
            endpoint="https://integrate.api.nvidia.com/v1",
            model="meta/llama-3.3-70b-instruct",
            key_env_var="NVIDIA_API_KEY",
            requires_network=True,
            context_budget_mode="compact",
        ),
        "free-cpu": ComputeProfile(
            name="free-cpu",
            provider="llama.cpp-cpu",
            endpoint="http://localhost:8080/v1",
            model="qwen2.5-3b-cpu",
            requires_network=False,
            context_budget_mode="compact",
        ),
        "pro": ComputeProfile(
            name="pro",
            provider="anthropic",
            model="claude-3-7-sonnet",
            key_env_var="ANTHROPIC_API_KEY",
            requires_network=True,
            context_budget_mode="standard",
        ),
        "local": ComputeProfile(
            name="local",
            provider="openai-compatible",
            endpoint=DEFAULT_LOCAL_GPU_URL,
            model=PIN_LOCAL_SOVEREIGN_BEST,
            requires_network=False,
            context_budget_mode="compact",
        ),
        "hybrid": ComputeProfile(
            name="hybrid",
            provider="dynamic-matrix",
            model="role-routed",
            requires_network=True,
            context_budget_mode="standard",
            role_matrix=DEFAULT_HYBRID_ROLE_MATRIX,
        ),
    }

    def __init__(self, active_profile: str = "hybrid", custom_profiles: Optional[Dict[str, ComputeProfile]] = None) -> None:
        self.profiles = copy.deepcopy(self.DEFAULT_PROFILES)
        if custom_profiles:
            self.profiles.update(copy.deepcopy(custom_profiles))
        self.active_profile_name = active_profile

    @property
    def current(self) -> ComputeProfile:
        if self.active_profile_name not in self.profiles:
            raise KeyError(f"Unknown BYOC profile: {self.active_profile_name}. Available: {list(self.profiles.keys())}")
        return self.profiles[self.active_profile_name]

    def set_profile(self, profile_name: str) -> None:
        if profile_name not in self.profiles:
            raise ValueError(f"Invalid profile '{profile_name}'. Must be one of {list(self.profiles.keys())}")
        self.active_profile_name = profile_name

    def get_role_cascade(self, role_name: str) -> List[ProviderTarget]:
        """Returns the ordered provider cascade for a specific role in hybrid mode."""
        matrix = self.current.role_matrix or self.DEFAULT_HYBRID_ROLE_MATRIX
        if role_name not in matrix:
            raise KeyError(f"Role '{role_name}' not configured in topology matrix. Available roles: {list(matrix.keys())}")
        return matrix[role_name]

    def pin_role_target(self, role_name: str, target: ProviderTarget, prepend: bool = True) -> None:
        """Dynamically pin or override a provider target for a specific role with strict instance isolation."""
        if not self.current.role_matrix:
            self.current.role_matrix = copy.deepcopy(self.DEFAULT_HYBRID_ROLE_MATRIX)
        if role_name not in self.current.role_matrix:
            self.current.role_matrix[role_name] = []
        if prepend:
            self.current.role_matrix[role_name].insert(0, copy.deepcopy(target))
        else:
            self.current.role_matrix[role_name].append(copy.deepcopy(target))

    def resolve_api_key(self) -> Optional[str]:
        """Resolves secret safely from environment or keyring."""
        prof = self.current
        if not prof.key_env_var:
            return None
        return os.getenv(prof.key_env_var)

    def is_offline_capable(self, role: Optional[str] = None) -> bool:
        """Checks offline capability globally or for a specific role in hybrid mode."""
        if not self.current.requires_network:
            return True
        if self.active_profile_name == "hybrid" and role:
            try:
                cascade = self.get_role_cascade(role)
                return any(not t.requires_network for t in cascade)
            except KeyError:
                return False
        return False
