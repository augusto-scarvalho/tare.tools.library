"""Frugality, Taxonomy, and Clean Root Guard Test (RFC-007 / RFC-008 / ADR-067)."""
import os
import subprocess
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_ROOT_DIRS = {
    ".github",
    "cases",
    "catalog",
    "docs",
    "site",
    "specs",
    "tools",
    "tests",
}

ALLOWED_ROOT_FILES = {
    ".gitignore",
    ".gitattributes",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "README.pt-BR.md",
    "pytest.ini",
    "requirements-editorial.txt",
    "requirements.txt",
}


@pytest.mark.verifies("RFC-007-REQ-SEGREGATION-001")
def test_repo_tracked_size_budget():
    """Ensure git tracked files remain strictly under the 50 MB budget."""
    res = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    tracked_files = [ROOT / f.strip().strip('"') for f in res.stdout.strip().splitlines() if f.strip()]
    
    total_bytes = sum(f.stat().st_size for f in tracked_files if f.exists())
    total_mb = total_bytes / (1024 * 1024)
    assert total_mb < 50.0, f"Tracked repository size ({total_mb:.2f} MB) exceeds the 50 MB frugality budget!"


@pytest.mark.verifies("RFC-007-REQ-SEGREGATION-002")
def test_no_raw_chat_dumps_tracked():
    """Ensure zero raw LLM chat transcripts, untracked experiment dumps, or secret logs are tracked in git."""
    res = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    tracked_files = [f.strip().strip('"') for f in res.stdout.strip().splitlines() if f.strip()]
    
    forbidden_prefixes = ["archaeology/chats/", "experiments/", "vault/", "_handoff/", "docs/archive/archaeology/historical/"]
    for tf in tracked_files:
        for prefix in forbidden_prefixes:
            assert not tf.startswith(prefix), f"Forbidden artifact tracked in git: {tf}"


@pytest.mark.verifies("RFC-008-REQ-TAXONOMY-001")
def test_clean_root_directory_structure():
    """Ensure ONLY allowed canonical folders and root config files exist in the repository root."""
    res = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    tracked_files = [f.strip().strip('"') for f in res.stdout.strip().splitlines() if f.strip()]
    
    for tf in tracked_files:
        parts = Path(tf).parts
        if len(parts) == 1:
            assert parts[0] in ALLOWED_ROOT_FILES, f"Disallowed root file tracked in git: {parts[0]}"
        else:
            top_dir = parts[0]
            assert top_dir in ALLOWED_ROOT_DIRS, f"Disallowed root directory tracked in git: {top_dir} (from {tf})"


@pytest.mark.verifies("RFC-008-REQ-TAXONOMY-002")
def test_canonical_directory_structure_exists():
    """Ensure canonical directories exist and contain valid assets."""
    canonical_dirs = [
        ROOT / "docs/adr",
        ROOT / "docs/architecture",
        ROOT / "docs/assurance",
        ROOT / "docs/guides",
        ROOT / "docs/archive",
        ROOT / "docs/policies",
        ROOT / "catalog/frontier",
        ROOT / "catalog/schemas",
        ROOT / "catalog/ontology",
        ROOT / "catalog/corpus",
        ROOT / "specs",
        ROOT / "tools",
        ROOT / "tests",
        ROOT / "cases",
    ]
    for cd in canonical_dirs:
        assert cd.exists() and cd.is_dir(), f"Missing canonical directory: {cd.relative_to(ROOT)}"
