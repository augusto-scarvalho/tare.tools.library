"""Validate pointers to repository-owned ontologies without copying payloads."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SCHEMA = "tare.tools/federated-ontology-index/1.0"
REGISTRY_PATH = Path("catalog/FEDERATED_ONTOLOGIES.json")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_CONCEPT_ID = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")


def _safe_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"{label} must be a non-empty POSIX path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} escapes its repository")
    return value


def load_federated_ontologies(
    root_dir: str | Path, *, require_retired_absent: bool = True
) -> dict[str, Any]:
    root = Path(root_dir)
    payload = json.loads((root / REGISTRY_PATH).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError("unsupported federated ontology registry schema")

    source = payload.get("source_library")
    if not isinstance(source, dict) or not _COMMIT.fullmatch(
        str(source.get("revision", ""))
    ):
        raise ValueError("source_library.revision must be a full Git commit")

    retired = payload.get("retired_library_paths")
    if not isinstance(retired, list) or not retired:
        raise ValueError("retired_library_paths must be non-empty")
    retired_paths: set[str] = set()
    for raw_path in retired:
        path = _safe_path(raw_path, "retired_library_path")
        if path in retired_paths:
            raise ValueError(f"retired Library path appears twice: {path}")
        retired_paths.add(path)
        if require_retired_absent and (root / path).exists():
            raise ValueError(f"retired Library ontology copy still exists: {path}")

    ontologies = payload.get("ontologies")
    if not isinstance(ontologies, list) or not ontologies:
        raise ValueError("ontologies must be a non-empty list")
    repositories: set[str] = set()
    identities: set[tuple[str, str, str]] = set()
    concepts: set[str] = set()
    for ontology in ontologies:
        if not isinstance(ontology, dict):
            raise ValueError("ontology records must be objects")
        repository = ontology.get("repository")
        if not isinstance(repository, str) or not repository.startswith("tare.tools."):
            raise ValueError("invalid ontology repository name")
        if repository in repositories:
            raise ValueError(f"repository appears twice: {repository}")
        repositories.add(repository)
        revision = ontology.get("revision")
        if not isinstance(revision, str) or not _COMMIT.fullmatch(revision):
            raise ValueError(f"{repository} revision must be a full Git commit")
        canonical_path = _safe_path(ontology.get("canonical_path"), "canonical_path")
        identity = (repository, revision, canonical_path)
        if identity in identities:
            raise ValueError(f"duplicate canonical ontology identity: {identity}")
        identities.add(identity)
        digest = ontology.get("canonical_sha256")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError("canonical_sha256 must be lowercase SHA-256")
        version = ontology.get("version")
        if not isinstance(version, str) or not version:
            raise ValueError("ontology version must be a non-empty string")
        concept_ids = ontology.get("concept_ids")
        if not isinstance(concept_ids, list) or not concept_ids:
            raise ValueError(f"{repository} concept_ids must be a non-empty list")
        if concept_ids != sorted(concept_ids):
            raise ValueError(f"{repository} concept_ids must be sorted")
        for concept_id in concept_ids:
            if not isinstance(concept_id, str) or not _CONCEPT_ID.fullmatch(concept_id):
                raise ValueError(f"invalid concept id: {concept_id!r}")
            if concept_id in concepts:
                raise ValueError(f"concept has multiple owners: {concept_id}")
            concepts.add(concept_id)
    return payload


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate federated ontologies")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    payload = load_federated_ontologies(args.root)
    print(
        json.dumps(
            {
                "status": "PASS",
                "ontology_owners": len(payload["ontologies"]),
                "concepts": sum(
                    len(item["concept_ids"]) for item in payload["ontologies"]
                ),
                "retired_library_paths": len(payload["retired_library_paths"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
