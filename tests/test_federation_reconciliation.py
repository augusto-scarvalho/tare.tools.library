"""Contracts for reusing the federated Library outside the TARE workspace."""

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from tools.build_manifest import build_library_manifest
from tools.federated_documents import load_federated_index, validate_repository_name, verify_owner_content
from tools.federated_ontologies import load_federated_ontologies


def test_external_repository_can_own_a_federated_document(tmp_path: Path):
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    (catalog / "FEDERATED_DOCUMENTS.json").write_text(json.dumps({
        "schema": "tare.tools/federated-document-index/1.0",
        "source_library": {"repository": "catalog-service", "revision": "a" * 40},
        "retired_library_path_count": 1,
        "repositories": [{
            "repository": "acme.billing", "revision": "b" * 40,
            "documents": [{
                "semantic_document_id": "acme.billing:docs/SPEC-001.md",
                "document_type": "spec", "title": "Billing contract",
                "canonical_path": "docs/SPEC-001.md",
                "canonical_sha256": hashlib.sha256(b"billing contract").hexdigest(),
                "retired_library_paths": ["specs/old-billing.md"],
            }],
        }],
    }), encoding="utf-8")

    assert load_federated_index(tmp_path)["repositories"][0]["repository"] == "acme.billing"
    entry = build_library_manifest(tmp_path).specs[0]
    assert entry.target_repositories == ["acme.billing"]
    assert entry.relative_path.startswith("acme.billing@")
    assert any(source["relative_path"].startswith("catalog-service@") for source in entry.source_paths)


def test_external_repository_can_own_a_federated_ontology(tmp_path: Path):
    catalog = tmp_path / "catalog"
    catalog.mkdir()
    (catalog / "FEDERATED_ONTOLOGIES.json").write_text(json.dumps({
        "schema": "tare.tools/federated-ontology-index/1.0",
        "source_library": {"repository": "tare.tools.library", "revision": "a" * 40},
        "retired_library_paths": ["catalog/ontology/old.yaml"],
        "ontologies": [{
            "repository": "acme.billing", "revision": "b" * 40,
            "canonical_path": "ontology/domain_ontology.yaml",
            "canonical_sha256": "c" * 64, "version": "1.0.0",
            "concept_ids": ["InvoiceSettlement"],
        }],
    }), encoding="utf-8")

    result = load_federated_ontologies(tmp_path)
    assert result["ontologies"][0]["repository"] == "acme.billing"


def test_explicit_external_target_is_preserved(tmp_path: Path):
    specs = tmp_path / "specs"
    specs.mkdir()
    (specs / "SPEC-001.md").write_text(
        "# Billing contract\n\n- **Canonical repository:** `acme.billing`\n"
        "\nAC-01: Return the exact invoice total.\n",
        encoding="utf-8",
    )
    entry = build_library_manifest(tmp_path).specs[0]
    assert entry.target_repositories == ["acme.billing"]


def test_manifest_exact_copies_preserve_all_source_paths(tmp_path: Path):
    specs = tmp_path / "specs"
    specs.mkdir()
    content = "# Billing contract\n\nAC-01: Return the exact invoice total.\n"
    first = specs / "SPEC-001.md"
    second = specs / "SPEC-001-copy.md"
    first.write_text(content, encoding="utf-8")
    second.write_bytes(first.read_bytes())
    before = {p.name: p.read_bytes() for p in (first, second)}

    manifest = build_library_manifest(tmp_path)
    assert manifest.total_documents == 1
    assert len(manifest.specs) == 1
    entry = manifest.specs[0]
    assert entry.id == hashlib.sha256(first.read_bytes()).hexdigest()
    assert [source["relative_path"] for source in entry.source_paths] == [
        "specs/SPEC-001-copy.md", "specs/SPEC-001.md",
    ]
    assert {p.name: p.read_bytes() for p in (first, second)} == before
    assert manifest.projection_receipt["consolidated_groups"] == 1
    assert manifest.projection_receipt["source_paths_preserved"] == 2


@pytest.mark.parametrize("name", ["", "../billing", "acme/billing/extra", "acme@billing", "acme:billing", "a" * 257, None])
def test_repository_identity_rejects_paths_and_ambiguous_separators(name):
    with pytest.raises(ValueError, match="invalid repository name"):
        validate_repository_name(name)


def test_repository_identity_preserves_namespace_and_case():
    assert validate_repository_name("Acme/Billing") == "Acme/Billing"


def test_exact_payload_does_not_merge_distinct_declared_identities(tmp_path: Path):
    test_external_repository_can_own_a_federated_document(tmp_path)
    path = tmp_path / "catalog/FEDERATED_DOCUMENTS.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    original = registry["repositories"][0]["documents"][0]
    registry["repositories"][0]["documents"].append({
        **original,
        "semantic_document_id": "acme.billing:docs/SPEC-002.md",
        "canonical_path": "docs/SPEC-002.md",
        "retired_library_paths": ["specs/second-billing.md"],
    })
    registry["retired_library_path_count"] = 2
    path.write_text(json.dumps(registry), encoding="utf-8")
    with pytest.raises(ValueError, match="conflicting declared identities"):
        build_library_manifest(tmp_path)


def test_owner_verification_uses_git_blob_bytes_and_rejects_checkout_hash(tmp_path: Path):
    test_external_repository_can_own_a_federated_document(tmp_path)
    owner = tmp_path / "owner"
    owner.mkdir()

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(owner), "-c", "core.hooksPath=.git/no-hooks", *args],
            capture_output=True, check=True, timeout=10,
        ).stdout.decode().strip()

    git("init")
    git("config", "core.autocrlf", "false")
    (owner / "docs").mkdir()
    raw = b"# Billing\n\nAC-01: Verify exact bytes.\n"
    (owner / "docs/SPEC-001.md").write_bytes(raw)
    git("add", ".")
    git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "-m", "fixture")
    path = tmp_path / "catalog/FEDERATED_DOCUMENTS.json"
    registry = json.loads(path.read_text(encoding="utf-8"))
    record = registry["repositories"][0]
    record["revision"] = git("rev-parse", "HEAD")
    document = record["documents"][0]
    document["canonical_sha256"] = hashlib.sha256(raw).hexdigest()
    path.write_text(json.dumps(registry), encoding="utf-8")
    (owner / "docs/SPEC-001.md").write_bytes(raw.replace(b"\n", b"\r\n"))
    assert verify_owner_content(tmp_path, {"acme.billing": owner}) == 1
    document["canonical_sha256"] = hashlib.sha256((owner / "docs/SPEC-001.md").read_bytes()).hexdigest()
    path.write_text(json.dumps(registry), encoding="utf-8")
    with pytest.raises(ValueError, match="content hash mismatch"):
        verify_owner_content(tmp_path, {"acme.billing": owner})
    with pytest.raises(ValueError, match="missing explicit owner"):
        verify_owner_content(tmp_path, {})
