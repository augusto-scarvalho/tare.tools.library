"""Bookkeeper authority guards over Library-owned decisions and specifications."""

import pytest

from tools.bookkeeper.ssot_registry import audit_ssot_registry


def document(root, path, status=None, identity=None, body="Body"):
    destination = root / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    metadata = ""
    if status is not None:
        metadata += f"status: {status}\n"
    if identity:
        metadata += f"doc_id: {identity}\n"
    destination.write_text(f"---\n{metadata}---\n# Test\n{body}\n", encoding="utf-8")
    return destination


@pytest.mark.parametrize("status", ["Aceito", "NOT_APPROVED"])
def test_unknown_status_blocks_audit(tmp_path, status):
    document(tmp_path, "docs/adr/ADR-999.md", status)
    report = audit_ssot_registry(tmp_path)
    assert not report.is_valid
    assert "status" in report.violations[0].description.lower()


@pytest.mark.parametrize("status", ["RATIFICADO", "APROVADA", "OWNER_ADOPTED"])
def test_declared_status_counts_as_canonical(tmp_path, status):
    document(tmp_path, "docs/adr/ADR-999.md", status)
    assert audit_ssot_registry(tmp_path).canonical_documents == 1


@pytest.mark.parametrize("header", [
    "- **Status:** Ratificado", "**Status:** `APPROVED`",
    "## Status\n\n**RATIFIED / RATIFICADO_POR_GOVERNANÇA_TRIPARTITE** (Homologado)",
])
def test_bookkeeper_understands_existing_markdown_status_formats(tmp_path, header):
    (tmp_path / "ADR-999.md").write_text(f"# Decision\n\n{header}\n", encoding="utf-8")
    assert audit_ssot_registry(tmp_path).canonical_documents == 1


def test_exclusion_wins_over_canonical_marker_in_audit(tmp_path):
    document(tmp_path, "docs/adr/ADR-999.md", "SUPERSEDED_RATIFIED")
    assert audit_ssot_registry(tmp_path).canonical_documents == 0


@pytest.mark.parametrize("status", ["RATIFIED", "RATIFICADO", "OWNER_ADOPTED"])
def test_different_bytes_with_same_explicit_identity_block(tmp_path, status):
    document(tmp_path, "docs/adr/ADR-998_first.md", status, "contract", "first")
    document(tmp_path, "docs/adr/ADR-999_second.md", status, "contract", "second")
    assert not audit_ssot_registry(tmp_path).is_valid


def test_excluded_revision_does_not_conflict_with_active_revision(tmp_path):
    document(tmp_path, "docs/adr/ADR-998_old.md", "SUPERSEDED", "contract", "old")
    document(tmp_path, "docs/adr/ADR-999_new.md", "RATIFIED", "contract", "new")
    assert audit_ssot_registry(tmp_path).is_valid


def test_exact_copies_are_not_authority_conflicts(tmp_path):
    first = document(tmp_path, "docs/adr/ADR-999_aaaaaaaa.md", "RATIFIED")
    (first.parent / "ADR-999_bbbbbbbb.md").write_bytes(first.read_bytes())
    assert audit_ssot_registry(tmp_path).is_valid


def test_history_is_not_current_authority(tmp_path):
    document(tmp_path, "docs/adr/ADR-999.md", "RATIFIED", "contract")
    document(tmp_path, "docs/archive/ADR-999.md", "UNKNOWN_HISTORICAL", "contract")
    report = audit_ssot_registry(tmp_path / "docs")
    assert report.is_valid
    assert report.total_documents == report.canonical_documents == 1


def test_different_full_stems_are_not_merged_by_bare_adr_number(tmp_path):
    document(tmp_path, "docs/adr/ADR-001_taxonomy.md", "RATIFIED", body="taxonomy")
    document(tmp_path, "docs/adr/ADR-001_indexing.md", "RATIFIED", body="indexing")
    assert audit_ssot_registry(tmp_path).is_valid
