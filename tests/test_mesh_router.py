"""Unit tests for LatencyAwareRouter (ADR-055)."""

import unittest
from unittest.mock import MagicMock, patch

from tools.mesh.router import LatencyAwareRouter, QueryRouteResult


class TestLatencyAwareRouter(unittest.TestCase):
    def setUp(self):
        self.router = LatencyAwareRouter(
            substrate_host="100.107.245.30",
            substrate_user="augus",
            latency_threshold_ms=150.0,
        )

    @patch.object(LatencyAwareRouter, "probe_substrate_latency", return_value=12.5)
    @patch("subprocess.check_output")
    def test_low_latency_routes_to_remote_substrate(self, mock_subp, mock_probe):
        mock_subp.return_value = b"[QUERY RESULTS] Found 5 matches\n1. [ADR] SpecGraph\n"
        res = self.router.route_query("SpecGraph", top_k=3)
        self.assertIn("REMOTE_SUBSTRATE", res.route)
        self.assertEqual(res.latency_ms, 12.5)
        self.assertIn("[QUERY RESULTS]", res.results[0]["raw_output"])

    @patch.object(LatencyAwareRouter, "probe_substrate_latency", return_value=250.0)
    def test_high_latency_routes_to_local_fallback(self, mock_probe):
        res = self.router.route_query("SpecGraph", top_k=3)
        self.assertIn("LOCAL_FALLBACK", res.route)
        self.assertEqual(res.latency_ms, 250.0)

    @patch.object(LatencyAwareRouter, "probe_substrate_latency", return_value=None)
    def test_offline_routes_to_local_fallback(self, mock_probe):
        res = self.router.route_query("SpecGraph", top_k=3)
        self.assertIn("LOCAL_FALLBACK", res.route)
        self.assertIsNone(res.latency_ms)


if __name__ == "__main__":
    unittest.main()
