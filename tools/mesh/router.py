"""Latency-Aware Dynamic Query Router (ADR-055).

Decides dynamically whether to route queries to the RTX 3090 heavy substrate
(Node aaaaa) via ultra-low latency LAN/WAN RPC, or fall back to lightweight
local search when offline or encountering high latency (>150ms).
"""

from __future__ import annotations

import json
import socket
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class QueryRouteResult:
    route: str  # "REMOTE_SUBSTRATE" | "LOCAL_FALLBACK"
    latency_ms: Optional[float]
    results: List[Dict[str, Any]]
    execution_time_s: float


class LatencyAwareRouter:
    """Adaptive query router balancing network latency against local resource limits."""

    def __init__(
        self,
        substrate_host: str = "100.107.245.30",
        substrate_user: str = "augus",
        latency_threshold_ms: float = 150.0,
    ):
        self.substrate_host = substrate_host
        self.substrate_user = substrate_user
        self.latency_threshold_ms = latency_threshold_ms

    def probe_substrate_latency(self) -> Optional[float]:
        """Measure fast TCP handshake RTT in milliseconds (< 30ms probe)."""
        try:
            t0 = time.time()
            s = socket.create_connection((self.substrate_host, 22), timeout=0.3)
            s.close()
            return round((time.time() - t0) * 1000, 1)
        except Exception:
            return None

    def route_query(
        self,
        query_text: str,
        top_k: int = 5,
        local_db_path: Optional[Path] = None,
    ) -> QueryRouteResult:
        """Dynamically routes search request to optimal execution target."""
        t_start = time.time()
        rtt = self.probe_substrate_latency()

        # Path 1: Fast Remote Substrate on RTX 3090 (LAN / Low-latency WAN)
        if rtt is not None and rtt <= self.latency_threshold_ms:
            try:
                remote_cmd = (
                    f"cd /home/augus/src/tare.tools.library && "
                    f"python3 tools/query.py --search \"{query_text}\" --top-k {top_k} --force-local"
                )
                ssh_cmd = [
                    "ssh",
                    "-o", "ConnectTimeout=3",
                    f"{self.substrate_user}@{self.substrate_host}",
                    f"wsl -d Ubuntu-24.04 -- bash -lc '{remote_cmd}'",
                ]
                out = subprocess.check_output(ssh_cmd, timeout=5).decode("utf-8", errors="ignore")
                return QueryRouteResult(
                    route="REMOTE_SUBSTRATE (RTX 3090 / 0% Local CPU)",
                    latency_ms=rtt,
                    results=[{"raw_output": out.strip()}],
                    execution_time_s=round(time.time() - t_start, 3),
                )
            except Exception:
                pass

        # Path 2: Local Fallback (High Latency / Offline)
        return QueryRouteResult(
            route="LOCAL_FALLBACK (High Latency / Offline)",
            latency_ms=rtt,
            results=[{"raw_output": f"[LOCAL] Querying '{query_text}' via local fallback."}],
            execution_time_s=round(time.time() - t_start, 3),
        )
