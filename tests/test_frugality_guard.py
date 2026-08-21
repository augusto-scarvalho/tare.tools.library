"""Frugality, Taxonomy, and Corpus Segregation Guard Test (RFC-007 / RFC-008 / ADR-067)."""
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


@pytest.mark.verifies("RFC-008-REQ-TAXONOMY-001")
def test_no_ghost_gitkeeps_tracked():
    """Ensure zero ghost .gitkeep files exist in legacy/purged directory paths."""
    res = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    tracked_files = [f.strip() for f in res.stdout.strip().splitlines() if f.strip()]
    
    purged_patterns = [
        "sources/", "proposals/architecture", "proposals/experiments",
        "research/00_", "research/01_", "refresh-editions/", "incoming/"
    ]
    for tf in tracked_files:
        for pat in purged_patterns:
            assert not tf.startswith(pat), f"Purged legacy path still tracked in git: {tf}"


@pytest.mark.verifies("RFC-008-REQ-TAXONOMY-002")
def test_canonical_directory_structure_exists():
    """Ensure canonical directories exist and contain valid assets."""
    canonical_dirs = [
        ROOT / "docs/adr",
        ROOT / "docs/architecture",
        ROOT / "docs/assurance",
        ROOT / "docs/guides",
        ROOT / "docs/archive",
        ROOT / "specs",
        ROOT / "tools",
        ROOT / "tests",
        ROOT / "cases",
        ROOT / "catalog",
    ]
    for cd in canonical_dirs:
        assert cd.exists() and cd.is_dir(), f"Missing canonical directory: {cd.relative_to(ROOT)}"
