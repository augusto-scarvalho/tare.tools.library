"""Unit tests for tare.tools.discovery (ADR-056)."""

import unittest
from pathlib import Path
from tools.discovery.discovery import DiscoveryEngine


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

    def test_resolve_mesh_returns_mesh_tool_and_adrs(self):
        res = self.engine.resolve("mesh")
        tool_names = [t["name"] for t in res.matched_tools]
        self.assertIn("mesh", tool_names)
        self.assertTrue(any("ADR-054" in p or "ADR-055" in p for p in res.matched_memory_anchors))

    def test_resolve_query_returns_query_tool(self):
        res = self.engine.resolve("query")
        tool_names = [t["name"] for t in res.matched_tools]
        self.assertIn("query", tool_names)

    def test_export_mcp_config_format(self):
        mcp_cfg = self.engine.export_mcp_config()
        self.assertIn("mcpServers", mcp_cfg)
        self.assertIn("tare-tools-library", mcp_cfg["mcpServers"])


if __name__ == "__main__":
    unittest.main()
