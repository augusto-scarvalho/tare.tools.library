"""Tests for Compute Guard & Thin-Client Protection Policy Engine (ADR-053)."""

import unittest
from unittest.mock import patch

from tools.policy.compute_guard import (
    ComputeProfile,
    assert_compute_guard,
    detect_compute_profile,
)


class TestComputeGuard(unittest.TestCase):
    def test_detect_compute_profile_thin_client(self):
        with patch("socket.gethostname", return_value="acer-augusto"):
            with patch("subprocess.run") as mock_run:
                mock_run.return_value.returncode = 1
                profile = detect_compute_profile()
                self.assertTrue(profile.is_thin_client)
                self.assertFalse(profile.has_local_cuda)
                self.assertEqual(profile.recommended_action, "OFFLOAD_TO_AAAAA")

    def test_assert_compute_guard_blocks_heavy_task_on_thin_client(self):
        with patch("tools.policy.compute_guard.detect_compute_profile") as mock_detect:
            mock_detect.return_value = ComputeProfile(
                hostname="acer-augusto",
                is_thin_client=True,
                has_local_cuda=False,
                recommended_action="OFFLOAD_TO_AAAAA",
            )
            can_run, msg = assert_compute_guard(task_name="embed_corpus", item_count=100, threshold=50)
            self.assertFalse(can_run)
            self.assertIn("ADR-053 COMPUTE GUARD", msg)
            self.assertIn("Auto-dispatching workload", msg)

    def test_assert_compute_guard_allows_light_task(self):
        with patch("tools.policy.compute_guard.detect_compute_profile") as mock_detect:
            mock_detect.return_value = ComputeProfile(
                hostname="acer-augusto",
                is_thin_client=True,
                has_local_cuda=False,
                recommended_action="OFFLOAD_TO_AAAAA",
            )
            can_run, msg = assert_compute_guard(task_name="quick_check", item_count=10, threshold=50)
            self.assertTrue(can_run)
            self.assertIsNone(msg)

    def test_assert_compute_guard_allows_override(self):
        can_run, msg = assert_compute_guard(task_name="embed_corpus", item_count=1000, force_local=True)
        self.assertTrue(can_run)
        self.assertIn("Forced local execution", msg)


if __name__ == "__main__":
    unittest.main()
