from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
sys.path.insert(0, str(SRC))

from tare_tools_publisher.git_backend import GitBackendError, plan, publish


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=True)
    return p.stdout.strip()


class GitLocalBackendTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.repo = root / "repo"
        self.packet_dir = root / "packet"
        self.repo.mkdir()
        self.packet_dir.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)
        (self.repo / "README.md").write_text("seed\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(self.repo), "add", "README.md"], check=True)
        subprocess.run([
            "git", "-C", str(self.repo),
            "-c", "user.name=test", "-c", "user.email=test@example.invalid",
            "commit", "-q", "-m", "seed"
        ], check=True)
        (self.packet_dir / "study.md").write_text("# Study\n", encoding="utf-8")
        manifest = {
            "packet_version": "1.0",
            "document_id": "research.workflow.local-git-test",
            "document_type": "research",
            "status": "RESEARCH",
            "repository": "tare.tools.research",
            "bounded_contexts": ["Workflow"],
            "artifacts": ["study.md"],
            "canonical_change": False,
        }
        self.packet = self.packet_dir / "PUBLISH_MANIFEST.json"
        self.packet.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_dry_run_does_not_create_branch_or_touch_main_index(self):
        head_before = git(self.repo, "rev-parse", "HEAD")
        status_before = git(self.repo, "status", "--porcelain=v1")
        receipt = publish(self.packet, self.repo, apply=False)
        self.assertFalse(receipt.applied)
        self.assertFalse(receipt.changed)
        self.assertEqual(receipt.outcome, "PLANNED")
        self.assertIsNone(receipt.commit_sha)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head_before)
        self.assertEqual(git(self.repo, "status", "--porcelain=v1"), status_before)
        p = subprocess.run(["git", "-C", str(self.repo), "show-ref", "--verify", f"refs/heads/{receipt.branch}"], capture_output=True)
        self.assertNotEqual(p.returncode, 0)

    def test_apply_creates_local_branch_commit_without_touching_main_worktree(self):
        head_before = git(self.repo, "rev-parse", "HEAD")
        status_before = git(self.repo, "status", "--porcelain=v1")
        receipt = publish(self.packet, self.repo, apply=True)
        self.assertTrue(receipt.applied)
        self.assertTrue(receipt.changed)
        self.assertEqual(receipt.outcome, "PUBLISHED")
        self.assertIsNotNone(receipt.commit_sha)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head_before)
        self.assertEqual(git(self.repo, "status", "--porcelain=v1"), status_before)
        self.assertEqual(git(self.repo, "rev-parse", receipt.branch), receipt.commit_sha)
        files = git(self.repo, "ls-tree", "-r", "--name-only", receipt.commit_sha).splitlines()
        prefix = "research/03_workflow/research-workflow-local-git-test/"
        self.assertIn(prefix + "study.md", files)
        self.assertIn(prefix + "PUBLISH_MANIFEST.json", files)
        self.assertIn(prefix + "PUBLICATION_RECORD.json", files)

    def test_same_packet_is_idempotent_after_apply(self):
        first = publish(self.packet, self.repo, apply=True)
        second = publish(self.packet, self.repo, apply=True)
        self.assertTrue(first.applied)
        self.assertTrue(first.changed)
        self.assertTrue(second.applied)
        self.assertFalse(second.changed)
        self.assertEqual(second.outcome, "ALREADY_PUBLISHED")
        self.assertEqual(second.commit_sha, first.commit_sha)
        self.assertEqual(git(self.repo, "rev-parse", second.branch), first.commit_sha)


if __name__ == "__main__":
    unittest.main()
