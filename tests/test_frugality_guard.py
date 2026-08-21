"""Frugality and Corpus Segregation Guard Test (RFC-007 / ADR-066)."""
import os
import subprocess
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.verifies("RFC-007-REQ-SEGREGATION-001")
def test_repo_tracked_size_budget():
    """Ensure git tracked files remain strictly under the 50 MB budget."""
    res = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    tracked_files = [ROOT / f.strip() for f in res.stdout.strip().splitlines() if f.strip()]
    
    total_bytes = sum(f.stat().st_size for f in tracked_files if f.exists())
    total_mb = total_bytes / (1024 * 1024)
    assert total_mb < 50.0, f"Tracked repository size ({total_mb:.2f} MB) exceeds the 50 MB frugality budget!"


@pytest.mark.verifies("RFC-007-REQ-SEGREGATION-002")
def test_no_raw_chat_dumps_tracked():
    """Ensure zero raw LLM chat transcripts, untracked experiment dumps, or secret logs are tracked in git."""
    res = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    tracked_files = [f.strip() for f in res.stdout.strip().splitlines() if f.strip()]
    
    forbidden_prefixes = ["archaeology/chats/", "experiments/", "vault/", "_handoff/"]
    for tf in tracked_files:
        for prefix in forbidden_prefixes:
            assert not tf.startswith(prefix), f"Forbidden artifact tracked in git: {tf}"


@pytest.mark.verifies("RFC-007-REQ-SEGREGATION-003")
def test_gitignore_and_crawler_quarantine():
    """Ensure .gitignore and harvest_corpus.py contain required quarantine rules."""
    from tools.bookkeeper.harvest_corpus import CRAWL_EXCLUDED_DIRS, NOISE_FILENAMES
    
    gi = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "archaeology/chats/" in gi
    assert "experiments/" in gi
    assert "vault/" in gi
    
    assert "vault" in CRAWL_EXCLUDED_DIRS
    assert "raw_logs" in CRAWL_EXCLUDED_DIRS
    assert ".aider.chat.history.md" in NOISE_FILENAMES
