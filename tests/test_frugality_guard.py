"""Frugality, taxonomy, and document ownership guard tests."""
import json
import os
import subprocess
import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_ROOT_DIRS = {
    ".githooks",
    ".github",
    "cases",
    "catalog",
    "docs",
    "specs",
    "tools",
    "tests",
}

ALLOWED_ROOT_FILES = {
    ".gitignore",
    ".gitattributes",
    "AGENTS.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "README.md",
    "README.pt-BR.md",
    "pytest.ini",
    "requirements-editorial.txt",
    "requirements.txt",
}

FORBIDDEN_PREFIXES = [
    "archaeology/chats/",
    "experiments/",
    "vault/",
    "_handoff/",
    "docs/archive/archaeology/historical/",
    "cases/",
    "docs/ARCHITECTURAL_QA_LEDGER.md",
]


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
    
    for tf in tracked_files:
        for prefix in FORBIDDEN_PREFIXES:
            assert not tf.startswith(prefix), f"Forbidden artifact tracked in git: {tf}"


def test_ingest_never_targets_a_forbidden_path(tmp_path):
    """Every ingest route lands in an allowed, trackable directory, and a category cannot escape it."""
    from tools.ingest import TYPE_ROUTING, ingest_document

    root = tmp_path / "library"
    for doc_type in TYPE_ROUTING:
        src = tmp_path / f"{doc_type}.md"
        src.write_text(f"# {doc_type}\n", encoding="utf-8")
        res = ingest_document(src, doc_type, category="program", root_dir=root, check_duplicates=False)
        assert res.success, res.message
        rel = res.target_path.relative_to(root).as_posix()
        assert rel.split("/")[0] in ALLOWED_ROOT_DIRS, rel
        assert not any(rel.startswith(prefix) for prefix in FORBIDDEN_PREFIXES), rel

    escape = ingest_document(src, "experiment", category="../../experiments", root_dir=root, check_duplicates=False)
    assert not escape.success
    assert not (root / "experiments").exists()


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
        ROOT / "docs/assurance",
        ROOT / "docs/guides",
        ROOT / "docs/policies",
        ROOT / "catalog/schemas",
        ROOT / "specs",
        ROOT / "tools",
        ROOT / "tests",
    ]
    for cd in canonical_dirs:
        assert cd.exists() and cd.is_dir(), f"Missing canonical directory: {cd.relative_to(ROOT)}"

@pytest.mark.verifies("RFC-009-REQ-BRANCH-CI-001")
def test_branch_and_ci_standardization():
    """Ensure CI remains present and ADR-068 stays only in its owner, tare.tools.os."""
    workflows_dir = ROOT / ".github/workflows"
    assert workflows_dir.exists(), "Workflows directory missing"

    assert not (
        ROOT / "docs/adr/ADR-068_UNIVERSAL_BRANCH_STANDARDIZATION_AND_CI_PIPELINES.md"
    ).exists()

    # Original deliberations have private custody; normal CI validates their
    # immutable reference, not a locally restored case or a fresh approval.
    archive = json.loads((ROOT / "docs/RECORDS_ARCHIVE.json").read_text(encoding="utf-8"))
    assert archive["repository"] == "tare.tools.library"
    assert len(archive["commit"]) == 40
    decision = archive["files"]["cases/CASE-2026-08-21-RFC-009-UNIVERSAL-BRANCH-STANDARDIZATION-AND-CI-PIPELINES/DECISION.md"]
    assert len(decision["sha256"]) == 64 and len(decision["git_blob"]) == 40

    # Verify CI workflow triggers
    for wf in workflows_dir.glob("*.yml"):
        text = wf.read_text(encoding="utf-8")
        if "branches:" in text:
            assert "main" in text, f"Workflow {wf.name} does not target canonical branch 'main'"


@pytest.mark.verifies("ADR-070")
def test_central_publication_automation_stays_retired():
    """External owners keep documents; Library must not recreate the copy pipeline."""
    retired = [
        ROOT / "tools/editorial_decision.py",
        ROOT / ".github/workflows/create-publication-pr.yml",
        ROOT / ".github/workflows/editorial-accept.yml",
    ]
    assert all(not path.exists() for path in retired), retired
    publisher = ROOT / "tools/publisher"
    assert not publisher.exists() or not any(path.is_file() for path in publisher.rglob("*"))
