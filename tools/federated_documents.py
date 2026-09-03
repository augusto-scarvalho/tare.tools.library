"""Validation and manifest projection for repository-owned documents."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterator


SCHEMA = "tare.tools/federated-document-index/1.0"
REGISTRY_PATH = Path("catalog/FEDERATED_DOCUMENTS.json")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_COMMIT = re.compile(r"^[0-9a-f]{40}$")
_MANIFEST_TYPES = {"adr", "spec", "experiment", "post_mortem"}


def _safe_path(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"{label} must be a non-empty POSIX path")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{label} escapes its repository")
    return value


def load_federated_index(
    root_dir: str | Path, *, require_retired_absent: bool = True
) -> dict[str, Any] | None:
    root = Path(root_dir)
    registry_path = root / REGISTRY_PATH
    if not registry_path.exists():
        return None
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError("unsupported federated document registry schema")
    source = payload.get("source_library")
    if not isinstance(source, dict) or not _COMMIT.fullmatch(
        str(source.get("revision", ""))
    ):
        raise ValueError("source_library.revision must be a full Git commit")
    repositories = payload.get("repositories")
    if not isinstance(repositories, list):
        raise ValueError("repositories must be a list")

    identities: set[tuple[str, str, str]] = set()
    retired_paths: set[str] = set()
    for repository in repositories:
        if not isinstance(repository, dict):
            raise ValueError("repository records must be objects")
        name = repository.get("repository")
        revision = repository.get("revision")
        if not isinstance(name, str) or not name.startswith("tare.tools."):
            raise ValueError("invalid repository name")
        if not isinstance(revision, str) or not _COMMIT.fullmatch(revision):
            raise ValueError(f"{name} revision must be a full Git commit")
        documents = repository.get("documents")
        if not isinstance(documents, list):
            raise ValueError(f"{name} documents must be a list")
        for document in documents:
            if not isinstance(document, dict):
                raise ValueError("document records must be objects")
            canonical = _safe_path(document.get("canonical_path"), "canonical_path")
            digest = document.get("canonical_sha256")
            if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
                raise ValueError("canonical_sha256 must be lowercase SHA-256")
            identity = (name, canonical, revision)
            if identity in identities:
                raise ValueError(f"duplicate canonical identity: {identity}")
            identities.add(identity)
            aliases = document.get("retired_library_paths")
            if not isinstance(aliases, list) or not aliases:
                raise ValueError("retired_library_paths must be non-empty")
            for alias_value in aliases:
                alias = _safe_path(alias_value, "retired_library_path")
                if alias in retired_paths:
                    raise ValueError(f"retired Library path appears twice: {alias}")
                retired_paths.add(alias)
                if require_retired_absent and (root / alias).exists():
                    raise ValueError(f"retired Library copy still exists: {alias}")

    declared_count = payload.get("retired_library_path_count")
    if declared_count != len(retired_paths):
        raise ValueError(
            f"retired path count mismatch: declared {declared_count}, actual {len(retired_paths)}"
        )
    for retirement in payload.get("local_retirements", []):
        if not isinstance(retirement, dict):
            raise ValueError("local retirements must be objects")
        retired = _safe_path(retirement.get("retired_path"), "retired_path")
        canonical = _safe_path(
            retirement.get("canonical_path"), "local canonical_path"
        )
        digest = retirement.get("sha256")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise ValueError("local retirement sha256 must be lowercase SHA-256")
        if require_retired_absent and (root / retired).exists():
            raise ValueError(f"retired Library copy still exists: {retired}")
        if require_retired_absent and not (root / canonical).exists():
            raise ValueError(f"local canonical document is missing: {canonical}")
    return payload


def iter_manifest_entries(root_dir: str | Path) -> Iterator[dict[str, Any]]:
    """Yield active v3 manifest entries without copying external payloads."""

    payload = load_federated_index(root_dir)
    if payload is None:
        return
    library_revision = payload["source_library"]["revision"]
    seen_payloads: set[str] = set()
    for repository in payload["repositories"]:
        repo_name = repository["repository"]
        revision = repository["revision"]
        for document in repository["documents"]:
            doc_type = document["document_type"]
            if doc_type not in _MANIFEST_TYPES:
                continue
            digest = document["canonical_sha256"]
            if digest in seen_payloads:
                raise ValueError(f"duplicate active payload in federation: {digest}")
            seen_payloads.add(digest)
            canonical = f"{repo_name}@{revision}:{document['canonical_path']}"
            semantic_id = document["semantic_document_id"]
            sources = [
                {
                    "relative_path": canonical,
                    "semantic_document_id": semantic_id,
                    "authority_state": "DECLARED_ACTIVE",
                    "editorial_status": "REPOSITORY_OWNED",
                }
            ]
            sources.extend(
                {
                    "relative_path": f"tare.tools.library@{library_revision}:{path}",
                    "semantic_document_id": semantic_id,
                    "authority_state": "EXCLUDED",
                    "editorial_status": "RETIRED_COPY",
                }
                for path in document["retired_library_paths"]
            )
            sources.sort(key=lambda item: item["relative_path"].encode("utf-8"))
            yield {
                "id": digest,
                "semantic_document_id": semantic_id,
                "doc_type": doc_type,
                "title": document["title"],
                "status": "REPOSITORY_OWNED",
                "relative_path": canonical,
                "sha256": digest,
                "authority_state": "DECLARED_ACTIVE",
                "source_paths": sources,
                "target_repositories": [repo_name],
                "acceptance_criteria": [],
                "references": [],
            }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Validate federated documents")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    payload = load_federated_index(args.root)
    count = 0 if payload is None else payload["retired_library_path_count"]
    print(json.dumps({"status": "PASS", "retired_library_paths": count}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
