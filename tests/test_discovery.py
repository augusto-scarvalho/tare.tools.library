"""Unit tests for tare.tools.discovery (ADR-056)."""

import importlib.util
import unittest
from pathlib import Path
from tools.discovery.discovery import DiscoveryEngine

ROOT = Path(__file__).resolve().parents[1]


class TestDiscoveryEngine(unittest.TestCase):
    def setUp(self):
        self.engine = DiscoveryEngine()

    def test_list_all_contains_essential_sections(self):
        data = self.engine.list_all()
        self.assertIn("tools", data)
        self.assertIn("mcps", data)
        self.assertIn("hooks", data)
        self.assertIn("memory_anchors", data)
        self.assertIn("endpoints", data)

    def test_resolve_mesh_returns_mesh_tool(self):
        res = self.engine.resolve("mesh")
        tool_names = [t["name"] for t in res.matched_tools]
        self.assertIn("mesh", tool_names)

    def test_resolve_query_returns_query_tool(self):
        res = self.engine.resolve("query")
        tool_names = [t["name"] for t in res.matched_tools]
        self.assertIn("query", tool_names)

    def test_export_mcp_config_format(self):
        mcp_cfg = self.engine.export_mcp_config()
        self.assertIn("mcpServers", mcp_cfg)

    def test_registry_names_only_paths_and_modules_that_exist(self):
        # Library-local paths must exist; "<repo>:<path>" pointers belong to another repository.
        data = self.engine.list_all()
        paths = [item["path"] for item in data["tools"] + data["hooks"]]
        paths += [p for anchors in data["memory_anchors"].values() for p in anchors]
        for path in paths:
            if ":" not in path:
                self.assertTrue((ROOT / path).exists(), path)
        for server in data["mcps"]:
            args = server.get("args", [])
            if "-m" in args:
                module = args[args.index("-m") + 1]
                self.assertIsNotNone(importlib.util.find_spec(module), module)


if __name__ == "__main__":
    unittest.main()
