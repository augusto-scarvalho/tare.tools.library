"""Remote Job Dispatcher over Tailscale WireGuard Mesh (ADR-053).

Dispatches heavy batch indexing, vector ingestion, and mutation tests from
thin clients to the configured compute substrate.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


def dispatch_remote_task(
    command: str,
    target_host: str | None = None,
    user: str | None = None,
    timeout_seconds: int = 300,
) -> int:
    """Execute on the configured SSH substrate using MeshClient."""
    from tools.mesh.mesh import MeshClient

    client = MeshClient(substrate_host=target_host, substrate_user=user)
    print("================================================================================")
    print(f" 🛰️ DISPATCHING JOB TO HEAVY SUBSTRATE (Node {client.substrate_host})")
    print(f"  Command: {command}")
    print("================================================================================")

    start_time = time.time()
    rc = client.exec(command=command, stream=True, timeout_seconds=timeout_seconds)
    elapsed = time.time() - start_time
    print(f"✅ [REMOTE JOB COMPLETE] Finished in {elapsed:.2f}s with code {rc}")
    return rc


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch heavy compute tasks to the configured substrate")
    parser.add_argument("--task", default="embed-corpus", help="Task name")
    parser.add_argument("--cmd", help="Custom command to run on the substrate")
    parser.add_argument("--target", help="Target hostname or IP (default: TARE_MESH_HOST)")

    args = parser.parse_args()

    if args.cmd:
        cmd = args.cmd
    elif args.task == "embed-corpus":
        from tools.mesh.config import project_command
        cmd = project_command("python3 tools/indexer/embed_corpus.py --root . --force-local")
    else:
        cmd = f"echo 'Running {args.task}'"

    return dispatch_remote_task(cmd, target_host=args.target)


if __name__ == "__main__":
    sys.exit(main())
