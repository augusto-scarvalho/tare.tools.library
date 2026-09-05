"""Authority guards must survive repository-owned document federation."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools.bookkeeper.ssot_registry import audit_ssot_registry
from tools.build_manifest import build_library_manifest


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


@pytest.mark.parametrize("directory,name", [("docs/adr", "ADR-999"), ("specs", "SPEC-999")])
@pytest.mark.parametrize("status", ["DRAFT", "SUPERSEDED", "SUPERSEDED_RATIFIED"])
def test_inactive_status_is_preserved_and_not_selectable(tmp_path, directory, name, status):
    document(tmp_path, f"{directory}/{name}.md", status)
    manifest = build_library_manifest(tmp_path)
    entry = (manifest.adrs + manifest.specs)[0]
    assert entry.status == status
    assert entry.authority_state == "EXCLUDED"
    assert entry.target_repositories == []
    assert entry.source_paths[0]["editorial_status"] == status
    assert manifest.canonical_ssot_count == 0


@pytest.mark.parametrize("status", ["Aceito", "NOT_APPROVED"])
def test_unknown_status_blocks_both_manifest_and_audit(tmp_path, status):
    document(tmp_path, "docs/adr/ADR-999.md", status)
    with pytest.raises(ValueError, match="unrecognized document status.*vocabulary"):
        build_library_manifest(tmp_path)
    report = audit_ssot_registry(tmp_path)
    assert not report.is_valid
    assert "status" in report.violations[0].description.lower()


@pytest.mark.parametrize("status", ["RATIFICADO", "APROVADA", "OWNER_ADOPTED"])
def test_declared_status_is_not_rewritten_as_ratification(tmp_path, status):
    document(tmp_path, "docs/adr/ADR-999.md", status)
    entry = build_library_manifest(tmp_path).adrs[0]
    assert entry.status == status
    assert entry.authority_state == "DECLARED_ACTIVE"
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
    with pytest.raises(ValueError, match="conflicting active identity"):
        build_library_manifest(tmp_path)
    assert not audit_ssot_registry(tmp_path).is_valid


def test_hash_suffixed_legacy_specs_do_not_evade_conflict(tmp_path):
    document(tmp_path, "specs/SPEC-999_aaaaaaaa.md", body="first")
    document(tmp_path, "specs/SPEC-999_bbbbbbbb.md", body="second")
    with pytest.raises(ValueError, match="conflicting active identity"):
        build_library_manifest(tmp_path)


def test_legacy_spec_remains_unmanaged_and_unclassified_adr_is_excluded(tmp_path):
    document(tmp_path, "specs/SPEC-999.md")
    document(tmp_path, "docs/adr/ADR-999.md", body="ADR without declared authority")
    manifest = build_library_manifest(tmp_path)
    assert manifest.specs[0].authority_state == "UNMANAGED_ACTIVE"
    assert manifest.specs[0].status == "UNCLASSIFIED"
    assert manifest.adrs[0].authority_state == "EXCLUDED"


def federated_registry(root, other_owner=False):
    records = []
    for index in range(2):
        records.append({
            "repository": "acme.other" if index and other_owner else "acme.billing",
            "revision": "a" * 40,
            "documents": [{
                "semantic_document_id": "SPEC-001", "document_type": "spec",
                "title": "Contract", "canonical_path": f"docs/contract-{index}.md",
                "canonical_sha256": str(index + 1) * 64,
                "retired_library_paths": [f"specs/old-{index}.md"],
            }],
        })
    catalog = root / "catalog"
    catalog.mkdir()
    (catalog / "FEDERATED_DOCUMENTS.json").write_text(json.dumps({
        "schema": "tare.tools/federated-document-index/1.0",
        "source_library": {"repository": "catalog-service", "revision": "b" * 40},
        "retired_library_path_count": 2, "repositories": records,
    }), encoding="utf-8")


def test_federated_same_owner_conflict_blocks(tmp_path):
    federated_registry(tmp_path)
    with pytest.raises(ValueError, match="conflicting active identity"):
        build_library_manifest(tmp_path)


def test_bare_id_is_not_global_across_federated_owners(tmp_path):
    federated_registry(tmp_path, other_owner=True)
    manifest = build_library_manifest(tmp_path)
    assert len(manifest.specs) == 2
    assert all(e.status == "REPOSITORY_OWNED" for e in manifest.specs)
    assert all(e.authority_state == "DECLARED_ACTIVE" for e in manifest.specs)


def test_excluded_revision_does_not_conflict_with_active_revision(tmp_path):
    document(tmp_path, "docs/adr/ADR-998_old.md", "SUPERSEDED", "contract", "old")
    document(tmp_path, "docs/adr/ADR-999_new.md", "RATIFIED", "contract", "new")
    manifest = build_library_manifest(tmp_path)
    assert [e.authority_state for e in manifest.adrs].count("DECLARED_ACTIVE") == 1
    assert audit_ssot_registry(tmp_path).is_valid


def test_failed_compile_does_not_replace_previous_manifest(tmp_path):
    document(tmp_path, "docs/adr/ADR-999.md", "Aceito")
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    previous = catalog / "LIBRARY_MANIFEST.json"
    previous.write_bytes(b'{"previous": true}\n')
    result = subprocess.run(
        [sys.executable, "-B", "-m", "tools.build_manifest", "--root", str(tmp_path)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, timeout=15,
    )
    assert result.returncode != 0
    assert previous.read_bytes() == b'{"previous": true}\n'


def test_exact_copies_are_not_authority_conflicts(tmp_path):
    first = document(tmp_path, "docs/adr/ADR-999_aaaaaaaa.md", "RATIFIED")
    (first.parent / "ADR-999_bbbbbbbb.md").write_bytes(first.read_bytes())
    assert len(build_library_manifest(tmp_path).adrs) == 1
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
    assert len(build_library_manifest(tmp_path).adrs) == 2
    assert audit_ssot_registry(tmp_path).is_valid


def test_mixed_exact_group_keeps_legacy_spec_identity_and_source_states(tmp_path):
    document(tmp_path, "docs/adr/ADR-999.md")
    document(tmp_path, "specs/SPEC-999.md")
    manifest = build_library_manifest(tmp_path)
    entry = (manifest.adrs + manifest.specs)[0]
    assert manifest.total_documents == 1
    assert entry.semantic_document_id == "SPEC-999"
    assert entry.authority_state == "UNMANAGED_ACTIVE"
    assert {s["authority_state"] for s in entry.source_paths} == {"EXCLUDED", "UNMANAGED_ACTIVE"}
    assert manifest.projection_receipt["mixed_state_groups"] == 1
