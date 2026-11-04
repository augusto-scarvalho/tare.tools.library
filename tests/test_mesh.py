"""Unit tests for tare.tools.mesh (ADR-054)."""

import unittest
from unittest.mock import MagicMock, patch

from tools.mesh.mesh import GpuTelemetry, MeshClient, MeshNodeInfo


class TestMeshClient(unittest.TestCase):
    def setUp(self):
        self.client = MeshClient(substrate_host="198.51.100.20", substrate_user="operator")

    @patch("subprocess.check_output")
    def test_status_discovery(self, mock_subp):
        fake_tailscale = {
            "Self": {
                "HostName": "thin-client",
                "TailscaleIPs": ["198.51.100.10"],
                "OS": "windows",
                "Active": True,
            },
            "Peer": {
                "node1": {
                    "HostName": "compute-node",
                    "TailscaleIPs": ["198.51.100.20"],
                    "OS": "windows",
                    "Active": True,
                }
            },
        }
        import json
        mock_subp.return_value = json.dumps(fake_tailscale).encode("utf-8")

        with patch.object(self.client, "_measure_ping", return_value=15.2):
            with patch.object(self.client, "_probe_port", return_value=True):
                nodes = self.client.status()
                self.assertEqual(len(nodes), 2)
                self.assertEqual(nodes[0].hostname, "thin-client")
                self.assertEqual(nodes[1].hostname, "compute-node")
                self.assertEqual(nodes[1].ping_ms, 15.2)

    @patch("subprocess.check_output")
    def test_gpu_telemetry_parser(self, mock_subp):
        mock_subp.return_value = b"NVIDIA GeForce RTX 3090, 38, 65, 95.5, 420.0, 30, 18500, 24576\n"
        gpu_stat = self.client.gpu()
        self.assertIsNotNone(gpu_stat)
        self.assertEqual(gpu_stat.gpu_name, "NVIDIA GeForce RTX 3090")
        self.assertEqual(gpu_stat.temperature_c, 38)
        self.assertEqual(gpu_stat.fan_speed_pct, 65)
        self.assertEqual(gpu_stat.power_draw_w, 95.5)
        self.assertEqual(gpu_stat.gpu_util_pct, 30)
        self.assertEqual(gpu_stat.status, "COLD")

    @patch("subprocess.Popen")
    def test_exec_streaming(self, mock_popen):
        mock_proc = MagicMock()
        mock_proc.stdout = ["line 1\n", "line 2\n"]
        mock_proc.returncode = 0
        mock_popen.return_value = mock_proc

        rc = self.client.exec("echo test", stream=True)
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
