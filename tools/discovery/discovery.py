"""Universal Capability Discovery Engine (ADR-056).

Enables AI agents and human developers to discover tools, endpoints, MCPs,
hooks, and domain memory anchors on-demand in < 5ms.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


REGISTRY_PATH = Path(__file__).resolve().parents[2] / "catalog" / "CAPABILITIES_REGISTRY.json"


@dataclass
class ResolvedContext:
    query: str
    matched_tools: List[Dict[str, Any]]
    matched_hooks: List[Dict[str, Any]]
    matched_memory_anchors: List[str]
    endpoints: Dict[str, Any]


class DiscoveryEngine:
    """Zero-overhead discovery engine for distributed capabilities."""

    def __init__(self, registry_file: Path = REGISTRY_PATH):
        self.registry_file = registry_file
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self.registry_file.exists():
            try:
                self.data = json.loads(self.registry_file.read_text(encoding="utf-8"))
            except Exception:
                self.data = {}
        else:
            self.data = {}

    def list_all(self) -> Dict[str, Any]:
        """Return the complete capabilities registry."""
        return self.data

    def resolve(self, query: str) -> ResolvedContext:
        """Resolve relevant tools, hooks, and memory anchors for a specific task or query."""
        q = query.lower().strip()
        tools = self.data.get("tools", [])
        hooks = self.data.get("hooks", [])
        anchors = self.data.get("memory_anchors", {})
        endpoints = self.data.get("endpoints", {})

        matched_tools = []
        for t in tools:
            name = t.get("name", "").lower()
            desc = t.get("description", "").lower()
            domain = t.get("domain", "").lower()
            if q in name or q in desc or q in domain or any(q in cmd.lower() for cmd in t.get("commands", [])):
                matched_tools.append(t)

        matched_hooks = []
        for h in hooks:
            name = h.get("name", "").lower()
            desc = h.get("description", "").lower()
            if q in name or q in desc:
                matched_hooks.append(h)

        matched_anchors = []
        for key, paths in anchors.items():
            if q in key.lower():
                matched_anchors.extend(paths)
            else:
                for p in paths:
                    if q in p.lower():
                        matched_anchors.append(p)

        # Fallback if specific search yielded nothing: return top essential tools
        if not matched_tools and not matched_hooks and not matched_anchors:
            matched_tools = tools[:3]
            matched_anchors = anchors.get("mesh_and_compute", []) + anchors.get("governance_and_agents", [])

        return ResolvedContext(
            query=query,
            matched_tools=matched_tools,
            matched_hooks=matched_hooks,
            matched_memory_anchors=list(dict.fromkeys(matched_anchors)),
            endpoints=endpoints,
        )

    def export_mcp_config(self) -> Dict[str, Any]:
        """Export standardized MCP config JSON for Antigravity, Claude Code, and Cursor."""
        mcps = self.data.get("mcps", [])
        mcp_servers = {}
        for m in mcps:
            name = m.get("name", "library-mcp")
            mcp_servers[name] = {
                "command": m.get("command", "python"),
                "args": m.get("args", []),
                "env": {},
            }
        return {"mcpServers": mcp_servers}


def main() -> int:
    parser = argparse.ArgumentParser(description="Universal Capability Discovery Engine (ADR-056)")
    subparsers = parser.add_subparsers(dest="command", help="Discovery commands")

    # list
    p_list = subparsers.add_parser("list", help="List all registered tools, endpoints, and hooks")
    p_list.add_argument("--json", action="store_true", help="Output raw JSON")

    # resolve
    p_res = subparsers.add_parser("resolve", help="Resolve tools and context for a specific task")
    p_res.add_argument("query", help="Search term or task description (e.g. 'gpu', 'rag', 'mesh')")
    p_res.add_argument("--json", action="store_true", help="Output raw JSON")

    # mcp-export
    p_mcp = subparsers.add_parser("mcp-export", help="Export universal MCP configuration")
    p_mcp.add_argument("--json", action="store_true", default=True, help="Output JSON (default: True)")

    args = parser.parse_args()
    engine = DiscoveryEngine()

    if args.command == "list":
        data = engine.list_all()
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print("=" * 80)
            print(" 🌟 UNIVERSAL CAPABILITIES REGISTRY (ADR-056)")
            print("=" * 80)
            print(f"Version: {data.get('version')} | Last Updated: {data.get('last_updated')}")
            print("\n🤖 LOCAL AI ENDPOINTS:")
            for k, v in data.get("endpoints", {}).items():
                print(f"  • [{k}] {v.get('model')} @ {v.get('url')} ({v.get('purpose')})")

            print("\n🛠️ REGISTERED TOOLS:")
            for t in data.get("tools", []):
                print(f"  • {t.get('name'):<15} ({t.get('domain')}): {t.get('description')}")
                for cmd in t.get("commands", [])[:2]:
                    print(f"      -> {cmd}")

            print("\n🛡️ GOVERNANCE HOOKS:")
            for h in data.get("hooks", []):
                print(f"  • {h.get('name'):<15} [{h.get('trigger')}]: {h.get('description')}")
            print("=" * 80)
        return 0

    elif args.command == "resolve":
        resolved = engine.resolve(args.query)
        if args.json:
            print(json.dumps(asdict(resolved), indent=2, ensure_ascii=False))
        else:
            print("=" * 80)
            print(f" 🔍 RESOLVED CAPABILITIES & CONTEXT FOR: '{args.query}'")
            print("=" * 80)
            print("🛠️ MATCHED TOOLS:")
            for t in resolved.matched_tools:
                print(f"  • {t.get('name'):<15} -> {t.get('description')}")
                for cmd in t.get("commands", []):
                    print(f"      {cmd}")

            if resolved.matched_hooks:
                print("\n🛡️ MATCHED HOOKS:")
                for h in resolved.matched_hooks:
                    print(f"  • {h.get('name')}: {h.get('description')}")

            if resolved.matched_memory_anchors:
                print("\n🧠 RELEVANT MEMORY ANCHORS (ADRs / SPECs):")
                for a in resolved.matched_memory_anchors:
                    print(f"  • {a}")
            print("=" * 80)
        return 0

    elif args.command == "mcp-export":
        mcp_cfg = engine.export_mcp_config()
        print(json.dumps(mcp_cfg, indent=2))
        return 0

    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
