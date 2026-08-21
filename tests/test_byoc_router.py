"""Tests for Sovereign BYOC Profile Router & Hybrid Dynamic Topology (RFC-006)."""
import os
import pytest

from tools.mesh.byoc_router import (
    BYOCRouter,
    ComputeProfile,
    ProviderTarget,
    PIN_LOCAL_SOVEREIGN_BEST,
    DEFAULT_LOCAL_GPU_URL,
)


@pytest.mark.verifies("RFC-006-REQ-BYOC-001")
def test_byoc_router_profiles_and_offline():
    router = BYOCRouter(active_profile="local")
    assert router.current.name == "local"
    assert router.is_offline_capable() is True
    assert router.current.endpoint == DEFAULT_LOCAL_GPU_URL
    assert router.current.model == PIN_LOCAL_SOVEREIGN_BEST

    # Free Tier (Google Free API)
    router.set_profile("free")
    assert router.current.name == "free"
    assert router.current.context_budget_mode == "compact"
    assert router.is_offline_capable() is False

    # Free Tier (NVIDIA Build / NIM Free Evaluation Tier)
    router.set_profile("free-nvidia")
    assert router.current.name == "free-nvidia"
    assert router.current.provider == "nvidia-build-free"
    assert router.current.key_env_var == "NVIDIA_API_KEY"
    assert router.is_offline_capable() is False

    # Free Tier (CPU Local llama.cpp $0.00 / Offline)
    router.set_profile("free-cpu")
    assert router.current.name == "free-cpu"
    assert router.is_offline_capable() is True

    # Pro API (Commercial)
    router.set_profile("pro")
    assert router.current.name == "pro"
    assert router.current.context_budget_mode == "standard"


@pytest.mark.verifies("RFC-006-REQ-BYOC-002")
def test_byoc_router_invalid_profile():
    router = BYOCRouter()
    with pytest.raises(ValueError):
        router.set_profile("nonexistent_profile")


@pytest.mark.verifies("RFC-006-REQ-BYOC-003")
def test_byoc_hybrid_role_matrix_and_pinning():
    """Verify hybrid dynamic matrix resolution, canary model pinning, and state isolation."""
    router1 = BYOCRouter(active_profile="hybrid")
    router2 = BYOCRouter(active_profile="hybrid")

    # Check default cascades for core roles
    google_cascade = router1.get_role_cascade("seat_google")
    assert len(google_cascade) >= 2
    assert google_cascade[0].kind == "vendor_cli"
    assert google_cascade[0].cli_bin == "agy"

    openai_cascade = router1.get_role_cascade("seat_openai")
    assert openai_cascade[0].cli_bin == "codex"
    assert any(t.kind == "nim_free" for t in openai_cascade)

    scribe_cascade = router1.get_role_cascade("scribe_compactor")
    assert scribe_cascade[0].kind == "local_gpu"
    assert scribe_cascade[0].model == PIN_LOCAL_SOVEREIGN_BEST

    # Test role offline capability
    assert router1.is_offline_capable(role="scribe_compactor") is True

    # Test dynamic pinning with CANARY target (proves prepend and non-pollution)
    canary_target = ProviderTarget(
        kind="local_gpu",
        provider="openai-compatible",
        model="canary-sentinel-v1.0",
        endpoint=DEFAULT_LOCAL_GPU_URL,
        requires_network=False,
    )
    router1.pin_role_target("seat_google", canary_target, prepend=True)
    updated_google = router1.get_role_cascade("seat_google")
    assert updated_google[0].model == "canary-sentinel-v1.0"

    # State Isolation Assertion: router2 must NOT be contaminated
    router2_google = router2.get_role_cascade("seat_google")
    assert router2_google[0].model != "canary-sentinel-v1.0"
    assert router2_google[0].model == "gemini-3.7-flash"
