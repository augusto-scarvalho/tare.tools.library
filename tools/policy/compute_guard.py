"""Compute Guard & Thin-Client Protection Policy Engine (ADR-053).

Prevents heavy batch indexing, vector serialization, and mutation thrashing on
lightweight developer machines by automatically intercepting
heavy workloads and routing them to the configured compute substrate.
"""

from __future__ import annotations

import os
import platform
import socket
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ComputeProfile:
    hostname: str
    is_thin_client: bool
    has_local_cuda: bool
    recommended_action: str


def detect_compute_profile() -> ComputeProfile:
    """Analyze current host hardware and policy profile."""
    hostname = socket.gethostname().lower()
    thin_clients = {name.strip().lower() for name in os.environ.get("TARE_THIN_CLIENT_HOSTNAMES", "").split(",") if name.strip()}
    is_thin = hostname in thin_clients
    
    has_cuda = False
    try:
        res = subprocess.run(["nvidia-smi"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        has_cuda = (res.returncode == 0)
    except Exception:
        has_cuda = False

    if not has_cuda and not is_thin:
        # Fallback heuristic: If no dedicated GPU is detected, classify as thin client
        is_thin = True

    action = "OFFLOAD_TO_SUBSTRATE" if is_thin else "LOCAL_DIRECT"
    return ComputeProfile(
        hostname=hostname,
        is_thin_client=is_thin,
        has_local_cuda=has_cuda,
        recommended_action=action,
    )


def assert_compute_guard(
    task_name: str,
    item_count: int = 1,
    threshold: int = 50,
    force_local: bool = False,
) -> Tuple[bool, Optional[str]]:
    """Enforce ADR-053 guard before executing compute or I/O intensive tasks.
    
    Returns:
        (can_run_local: bool, message: Optional[str])
    """
    if force_local:
        return True, "[OVERRIDE] Forced local execution with throttling active."

    profile = detect_compute_profile()
    if profile.is_thin_client and item_count > threshold:
        msg = (
            f"🛡️ [ADR-053 COMPUTE GUARD] Heavy task '{task_name}' ({item_count} items > threshold {threshold}) "
            f"blocked on Thin-Client '{profile.hostname}'.\n"
            f"👉 Auto-dispatching workload to the configured compute substrate (TARE_MESH_HOST)."
        )
        return False, msg

    return True, None
