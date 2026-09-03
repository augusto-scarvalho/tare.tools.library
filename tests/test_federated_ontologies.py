import json
from pathlib import Path

import pytest

from tools.federated_ontologies import load_federated_ontologies


def _write_registry(root: Path) -> None:
    target = root / "catalog" / "FEDERATED_ONTOLOGIES.json"
    target.parent.mkdir(parents=True)
    target.write_text(
        json.dumps(
            {
                "schema": "tare.tools/federated-ontology-index/1.0",
                "source_library": {
                    "repository": "tare.tools.library",
                    "revision": "a" * 40,
                },
                "retired_library_paths": [
                    "catalog/ontology/domain_ontology.yaml"
                ],
                "ontologies": [
                    {
                        "repository": "tare.tools.kernel",
                        "url": "https://example.invalid/kernel",
                        "revision": "b" * 40,
                        "canonical_path": "ontology/domain_ontology.yaml",
                        "canonical_sha256": "c" * 64,
                        "version": "1.0.0",
                        "concept_ids": ["CASPersistence"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_registry_accepts_owner_pointers_without_payload_copies(tmp_path: Path):
    _write_registry(tmp_path)
    payload = load_federated_ontologies(tmp_path)
    assert payload["ontologies"][0]["repository"] == "tare.tools.kernel"


def test_repository_catalog_includes_backlog_graph_owner():
    payload = load_federated_ontologies(Path(__file__).resolve().parents[1])
    backlog = next(
        item for item in payload["ontologies"]
        if item["repository"] == "tare.tools.backlog-graph"
    )
    assert backlog["concept_ids"] == [
        "AtomicReopenCascade",
        "CasLeasedGraphMutation",
        "DeterministicExecutionFrontier",
        "TypedDependencySemantics",
    ]


def test_registry_rejects_retired_library_payload_copy(tmp_path: Path):
    _write_registry(tmp_path)
    copy = tmp_path / "catalog" / "ontology" / "domain_ontology.yaml"
    copy.parent.mkdir(parents=True)
    copy.write_text("concepts: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="copy still exists"):
        load_federated_ontologies(tmp_path)


def test_registry_rejects_one_concept_with_two_owners(tmp_path: Path):
    _write_registry(tmp_path)
    registry_path = tmp_path / "catalog" / "FEDERATED_ONTOLOGIES.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    second = dict(payload["ontologies"][0])
    second["repository"] = "tare.tools.specgraph"
    second["revision"] = "d" * 40
    payload["ontologies"].append(second)
    registry_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="multiple owners"):
        load_federated_ontologies(tmp_path)
