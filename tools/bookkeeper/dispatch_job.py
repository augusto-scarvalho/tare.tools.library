"""Remote Job Dispatcher over Tailscale WireGuard Mesh (ADR-053).

Dispatches heavy batch indexing, vector ingestion, and mutation tests from
thin clients (acer-augusto) to the heavy compute substrate (Node aaaaa).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def dispatch_remote_task(
    command: str,
    target_host: str = "100.107.245.30",
    user: str = "augus",
    timeout_seconds: int = 300,
) -> int:
    """Execute remote command on node aaaaa inside WSL2 with CUDA support using MeshClient."""
    from tools.mesh.mesh import MeshClient

    client = MeshClient(substrate_host=target_host, substrate_user=user)
    print("================================================================================")
    print(f" 🛰️ DISPATCHING JOB TO HEAVY SUBSTRATE (Node {target_host} / RTX 3090)")
    print(f"  Command: {command}")
    print("================================================================================")

    start_time = time.time()
    rc = client.exec(command=command, node="aaaaa", stream=True, timeout_seconds=timeout_seconds)
    elapsed = time.time() - start_time
    print(f"✅ [REMOTE JOB COMPLETE] Finished in {elapsed:.2f}s with code {rc}")
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch heavy compute tasks to Node aaaaa")
    parser.add_argument("--task", default="embed-corpus", help="Task name")
    parser.add_argument("--cmd", help="Custom command to run on node aaaaa")
    parser.add_argument("--target", default="100.107.245.30", help="Target node IP")

    args = parser.parse_args()

    if args.cmd:
        cmd = args.cmd
    elif args.task == "embed-corpus":
        cmd = "cd /home/augus/src && python3 -c \"print('Remote embed corpus ready')\""
    else:
        cmd = f"echo 'Running {args.task}'"

    return dispatch_remote_task(cmd, target_host=args.target)


if __name__ == "__main__":
    sys.exit(main())
