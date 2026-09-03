import hashlib
import json
from pathlib import Path

import pytest

from tools.federated_documents import iter_manifest_entries, load_federated_index


def _registry(root: Path) -> Path:
    target = root / "catalog" / "FEDERATED_DOCUMENTS.json"
    target.parent.mkdir(parents=True)
    digest = hashlib.sha256(b"owner bytes").hexdigest()
    target.write_text(
        json.dumps(
            {
                "schema": "tare.tools/federated-document-index/1.0",
                "source_library": {
                    "repository": "tare.tools.library",
                    "revision": "a" * 40,
                },
                "retired_library_path_count": 1,
                "repositories": [
                    {
                        "repository": "tare.tools.kernel",
                        "url": "https://example.invalid/kernel",
                        "default_branch": "main",
                        "revision": "b" * 40,
                        "documents": [
                            {
                                "semantic_document_id": "tare.tools.kernel:docs/SPEC.md",
                                "document_type": "spec",
                                "title": "Kernel spec",
                                "canonical_path": "docs/SPEC.md",
                                "canonical_sha256": digest,
                                "migration": "exact-content",
                                "retired_library_paths": ["specs/SPEC.md"],
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    return target


def test_registry_projects_repo_qualified_v3_entry(tmp_path: Path):
    _registry(tmp_path)
    payload = load_federated_index(tmp_path)
    assert payload is not None
    entries = list(iter_manifest_entries(tmp_path))
    assert len(entries) == 1
    entry = entries[0]
    assert entry["id"] == entry["sha256"]
    assert entry["authority_state"] == "DECLARED_ACTIVE"
    assert entry["relative_path"].startswith("tare.tools.kernel@")
    assert {source["authority_state"] for source in entry["source_paths"]} == {
        "DECLARED_ACTIVE",
        "EXCLUDED",
    }


def test_registry_rejects_a_copy_that_still_exists(tmp_path: Path):
    _registry(tmp_path)
    copy = tmp_path / "specs" / "SPEC.md"
    copy.parent.mkdir(parents=True)
    copy.write_text("copy", encoding="utf-8")
    with pytest.raises(ValueError, match="still exists"):
        load_federated_index(tmp_path)
