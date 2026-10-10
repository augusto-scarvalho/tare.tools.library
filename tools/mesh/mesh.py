"""tare.tools.mesh — Ergonomic Tailscale Mesh CLI & Node SDK (ADR-054).

Minimalist, dependency-free utility to manage and access distributed nodes,
GPU telemetry, remote command execution, fast sync, and inference daemons.
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import socket
import subprocess
import sys
import time
import tempfile
import urllib.request
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.mesh.config import project_command, remote_shell, ssh_target

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_SUBSTRATE_HOST = "localhost"
DEFAULT_SUBSTRATE_USER = None


@dataclass
class MeshNodeInfo:
    hostname: str
    ip: str
    os: str
    is_active: bool
    ping_ms: Optional[float] = None
    chat_port_online: bool = False
    embed_port_online: bool = False


@dataclass
class GpuTelemetry:
    gpu_name: str
    temperature_c: int
    fan_speed_pct: int
    power_draw_w: float
    power_limit_w: float
    gpu_util_pct: int
    vram_used_mib: int
    vram_total_mib: int
    status: str = "HEALTHY"


class MeshClient:
    """Minimalist Python SDK for the Tailscale Distributed Mesh."""

    def __init__(
        self,
        substrate_host: Optional[str] = None,
        substrate_user: Optional[str] = None,
        *,
        remote_root: Optional[str] = None,
        wsl_distro: Optional[str] = None,
    ):
        self.substrate_host = substrate_host or os.environ.get("TARE_MESH_HOST") or DEFAULT_SUBSTRATE_HOST
        self.substrate_user = substrate_user if substrate_user is not None else os.environ.get("TARE_MESH_USER") or DEFAULT_SUBSTRATE_USER
        self.remote_root = remote_root or os.environ.get("TARE_MESH_REMOTE_ROOT")
        self.wsl_distro = wsl_distro if wsl_distro is not None else os.environ.get("TARE_MESH_WSL_DISTRO")

    def _host(self, node):
        return self.substrate_host if node in (None, "substrate") else node

    def project_command(self, command):
        return project_command(command, self.remote_root)

    def _ssh_command(self, command, node=None):
        return [
            "ssh", "-o", "ConnectTimeout=5", "-o", "ServerAliveInterval=15",
            ssh_target(self._host(node), self.substrate_user),
            remote_shell(command, self.wsl_distro),
        ]

    def status(self) -> List[MeshNodeInfo]:
        """Discover active nodes in the Tailscale mesh and check their health."""
        nodes: List[MeshNodeInfo] = []
        try:
            out = subprocess.check_output(["tailscale", "status", "--json"], timeout=5)
            data = json.loads(out.decode("utf-8", errors="ignore"))
            peers = data.get("Peer", {})
            self_node = data.get("Self", {})

            all_raw = [self_node] + list(peers.values())
            for p in all_raw:
                h = p.get("HostName", "unknown")
                ips = p.get("TailscaleIPs", [""])
                ip = ips[0] if ips else ""
                os_type = p.get("OS", "unknown")
                active = p.get("Active", False) or (p == self_node)

                node_info = MeshNodeInfo(
                    hostname=h,
                    ip=ip,
                    os=os_type,
                    is_active=active,
                )

                if ip and ip != self_node.get("TailscaleIPs", [""])[0]:
                    node_info.ping_ms = self._measure_ping(ip)

                if ip == self.substrate_host or h == self.substrate_host:
                    node_info.chat_port_online = self._probe_port(ip or "127.0.0.1", 8080)
                    node_info.embed_port_online = self._probe_port(ip or "127.0.0.1", 8081)

                nodes.append(node_info)
        except Exception:
            # Fallback if tailscale CLI is not in path
            nodes.append(
                MeshNodeInfo(
                    hostname=self.substrate_host,
                    ip=self.substrate_host,
                    os="windows/wsl2" if self.wsl_distro else "unknown",
                    is_active=True,
                    ping_ms=self._measure_ping(self.substrate_host),
                    chat_port_online=self._probe_port(self.substrate_host, 8080),
                    embed_port_online=self._probe_port(self.substrate_host, 8081),
                )
            )
        return nodes

    def gpu(self, node: Optional[str] = None) -> Optional[GpuTelemetry]:
        """Read real-time GPU telemetry from the selected substrate."""
        host = self._host(node)
        cmd = [
            "ssh",
            "-o", "ConnectTimeout=3",
            ssh_target(host, self.substrate_user),
            "nvidia-smi --query-gpu=name,temperature.gpu,fan.speed,power.draw,power.limit,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits",
        ]
        try:
            out = subprocess.check_output(cmd, timeout=5).decode("utf-8", errors="ignore").strip()
            parts = [p.strip() for p in out.split(",")]
            if len(parts) >= 8:
                return GpuTelemetry(
                    gpu_name=parts[0],
                    temperature_c=int(float(parts[1])),
                    fan_speed_pct=int(float(parts[2])),
                    power_draw_w=float(parts[3]),
                    power_limit_w=float(parts[4]),
                    gpu_util_pct=int(float(parts[5])),
                    vram_used_mib=int(float(parts[6])),
                    vram_total_mib=int(float(parts[7])),
                    status="COLD" if int(float(parts[1])) < 45 else "OPTIMAL" if int(float(parts[1])) < 70 else "HOT",
                )
        except Exception as e:
            return None
        return None

    def exec(
        self,
        command: str,
        node: Optional[str] = None,
        stream: bool = True,
        timeout_seconds: int = 600,
    ) -> int:
        """Execute a command on the selected SSH host, optionally through WSL."""
        ssh_cmd = self._ssh_command(command, node)
        start_t = time.time()
        try:
            if stream:
                proc = subprocess.Popen(
                    ssh_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                for line in proc.stdout:
                    print(f"  [{self._host(node)}] {line.strip()}", flush=True)
                proc.wait(timeout=timeout_seconds)
                rc = proc.returncode
            else:
                res = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout_seconds)
                rc = res.returncode
            return rc
        except Exception as e:
            print(f"❌ [MESH EXEC ERROR] {e}", file=sys.stderr)
            return 1

    def sync(
        self,
        target_node: Optional[str] = None,
        source_dir: str = ".",
    ) -> bool:
        """Stream an uncompressed snapshot into the configured remote checkout."""
        root = Path(source_dir).resolve()
        host = self._host(target_node)
        allowed_exts = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ".toml", ".sh", ".rst", ".html", ".css", ".js", ".ts"}
        ignored_parts = {".git", "__pycache__", ".pytest_cache", "site", "_site", ".venv", "venv", ".idea", ".vscode", "source-bundles", "_archives", ".private", ".internal", ".reconciliation", ".credentials", ".secrets", ".ssh", ".aws"}
        receiver = "import io,sys,zipfile; from pathlib import Path; "
        receiver += (f"root=Path({self.remote_root!r}).expanduser()" if self.remote_root else
                     "root=Path.home()/'src'/'tare.tools.library'")
        receiver += "; root.mkdir(parents=True,exist_ok=True); zipfile.ZipFile(io.BytesIO(sys.stdin.buffer.read())).extractall(root)"
        remote_cmd = "python3 -c " + shlex.quote(receiver)
        try:
            with tempfile.TemporaryFile() as archive:
                with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as zf:
                    for file in root.rglob("*"):
                        relative = file.relative_to(root)
                        if any(part in ignored_parts for part in relative.parts) or file.suffix.lower() not in allowed_exts:
                            continue
                        if file.name.startswith("credentials.local.") or file.name.endswith(".local.json"):
                            continue
                        if file.is_file() and file.stat().st_size < 2 * 1024 * 1024:
                            zf.write(file, relative.as_posix())
                size_kb = archive.tell() / 1024
                archive.seek(0)
                print(f"[MESH SYNC] Sending {size_kb:.1f} KB to {host}...", flush=True)
                subprocess.run(self._ssh_command(remote_cmd, target_node), stdin=archive, check=True)
            print("[OK] Sincronização concluída!", flush=True)
            return True
        except Exception as e:
            print(f"[ERROR] Sync failed: {e}", file=sys.stderr)
            return False

    def daemon(self, action: str = "status", node: Optional[str] = None) -> Dict[str, Any]:
        """Manage or inspect llama-server neural inference daemons."""
        host = self._host(node)
        if action == "status":
            chat_ok = self._probe_port(host, 8080)
            embed_ok = self._probe_port(host, 8081)
            return {"chat_server_8080": "ONLINE" if chat_ok else "OFFLINE", "embed_server_8081": "ONLINE" if embed_ok else "OFFLINE"}
        elif action == "start":
            cmd = os.environ.get("TARE_MESH_DAEMON_START")
            if not cmd:
                return {"error": "Set TARE_MESH_DAEMON_START to the server command, including the existing model path."}
            if self.exec(cmd, node=node, stream=False):
                return {"error": "The inference server command failed."}
            time.sleep(2)
            return self.daemon("status", node=node)
        elif action == "stop":
            cmd = "pkill -f llama-server"
            self.exec(cmd, node=node, stream=False)
            return {"status": "STOPPED"}
        return {"error": f"Unknown daemon action '{action}'"}

    def doctor(self) -> Dict[str, Any]:
        """Run complete health check and diagnostic on local and remote nodes."""
        report = {
            "local_host": socket.gethostname(),
            "substrate_reachable": False,
            "ssh_auth": False,
            "gpu_detected": False,
            "embed_daemon_online": False,
            "chat_daemon_online": False,
        }
        # 1. Ping
        ping = self._measure_ping(self.substrate_host)
        report["substrate_reachable"] = (ping is not None)
        report["latency_ms"] = ping

        # 2. SSH
        try:
            out = subprocess.check_output(["ssh", "-o", "ConnectTimeout=3", ssh_target(self.substrate_host, self.substrate_user), "hostname"], timeout=4)
            report["ssh_auth"] = (out.decode().strip() != "")
        except Exception:
            report["ssh_auth"] = False

        # 3. GPU
        gpu_stat = self.gpu()
        report["gpu_detected"] = (gpu_stat is not None)
        if gpu_stat:
            report["gpu_details"] = asdict(gpu_stat)

        # 4. Ports
        report["chat_daemon_online"] = self._probe_port(self.substrate_host, 8080)
        report["embed_daemon_online"] = self._probe_port(self.substrate_host, 8081)
        return report

    def _measure_ping(self, ip: str) -> Optional[float]:
        try:
            t0 = time.time()
            s = socket.create_connection((ip, 22), timeout=1.5)
            s.close()
            return round((time.time() - t0) * 1000, 1)
        except Exception:
            return None

    def _probe_port(self, host: str, port: int) -> bool:
        try:
            s = socket.create_connection((host, port), timeout=1.0)
            s.close()
            return True
        except Exception:
            return False


def main() -> int:
    parser = argparse.ArgumentParser(description="tare.tools.mesh — Minimalist Tailscale & GPU CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available mesh commands")

    # status
    p_status = subparsers.add_parser("status", help="Show all nodes in the mesh and their health")
    p_status.add_argument("--json", action="store_true", help="Output raw JSON")

    # gpu
    p_gpu = subparsers.add_parser("gpu", help="Show real-time GPU metrics")
    p_gpu.add_argument("--node", help="Target node (default: configured substrate)")
    p_gpu.add_argument("--json", action="store_true", help="Output raw JSON")

    # sync
    p_sync = subparsers.add_parser("sync", help="Fast sync repository to remote node")
    p_sync.add_argument("target", nargs="?", help="Target node (default: configured substrate)")
    p_sync.add_argument("--dir", default=".", help="Source directory")

    # exec
    p_exec = subparsers.add_parser("exec", help="Run a remote command over SSH")
    p_exec.add_argument("target", help="Target hostname or substrate")
    p_exec.add_argument("cmd", help="Command to run")

    # daemon
    p_daemon = subparsers.add_parser("daemon", help="Manage llama-server inference daemons")
    p_daemon.add_argument("action", choices=["status", "start", "stop"], default="status", nargs="?")
    p_daemon.add_argument("--node", help="Target node (default: configured substrate)")
    p_daemon.add_argument("--json", action="store_true", help="Output raw JSON")

    # doctor
    p_doc = subparsers.add_parser("doctor", help="Run mesh diagnostics")
    p_doc.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()
    client = MeshClient()

    if args.command == "status":
        nodes = client.status()
        if args.json:
            print(json.dumps([asdict(n) for n in nodes], indent=2))
        else:
            print("=" * 80)
            print(" 🛰️ TARE.TOOLS TAILSCALE MESH TOPOLOGY & ENDPOINTS")
            print("=" * 80)
            print(f"{'HOSTNAME':<18} {'IP':<16} {'STATUS':<10} {'PING':<10} {'CHAT :8080':<12} {'EMBED :8081'}")
            print("-" * 80)
            for n in nodes:
                st = "🟢 ACTIVE" if n.is_active else "⚪ IDLE"
                p_str = f"{n.ping_ms} ms" if n.ping_ms else "-"
                c_str = "🟢 ONLINE" if n.chat_port_online else "⚪ OFFLINE"
                e_str = "🟢 ONLINE" if n.embed_port_online else "⚪ OFFLINE"
                print(f"{n.hostname:<18} {n.ip:<16} {st:<10} {p_str:<10} {c_str:<12} {e_str}")
        return 0

    elif args.command == "gpu":
        telemetry = client.gpu(args.node)
        if not telemetry:
            print(f"❌ [GPU] Could not query GPU on node '{args.node}'. Ensure SSH is reachable.", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(asdict(telemetry), indent=2))
        else:
            print("=" * 70)
            print(f" 🎮 GPU TELEMETRY — NODE {args.node.upper()} ({telemetry.gpu_name})")
            print("=" * 70)
            print(f"  • Temperatura:       {telemetry.temperature_c} °C ({telemetry.status})")
            print(f"  • Ventoinhas:        {telemetry.fan_speed_pct} %")
            print(f"  • Potência:          {telemetry.power_draw_w:.1f} W / {telemetry.power_limit_w:.1f} W")
            print(f"  • Carga CUDA:        {telemetry.gpu_util_pct} %")
            print(f"  • VRAM Utilizada:    {telemetry.vram_used_mib} MiB / {telemetry.vram_total_mib} MiB ({telemetry.vram_total_mib - telemetry.vram_used_mib} MiB livres)")
            print("=" * 70)
        return 0

    elif args.command == "sync":
        ok = client.sync(target_node=args.target, source_dir=args.dir)
        return 0 if ok else 1

    elif args.command == "exec":
        return client.exec(command=args.cmd, node=args.target, stream=True)

    elif args.command == "daemon":
        res = client.daemon(action=args.action, node=args.node)
        print(json.dumps(res, indent=2))
        return 1 if "error" in res else 0

    elif args.command == "doctor":
        doc = client.doctor()
        if args.json:
            print(json.dumps(doc, indent=2))
        else:
            print("=" * 70)
            print(" 🩺 MESH DOCTOR DIAGNOSTIC REPORT")
            print("=" * 70)
            for k, v in doc.items():
                icon = "✅" if v is True or (isinstance(v, (int, float)) and v > 0) else "❌" if v is False else "ℹ️"
                print(f"  {icon} {k:<25}: {v}")
            print("=" * 70)
        return 0

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
