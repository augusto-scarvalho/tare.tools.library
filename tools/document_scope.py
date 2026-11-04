"""Deterministic Markdown scope for the active Library corpus and for owner checkouts.

The repository contains active knowledge, generated catalogs and immutable
historical snapshots.  Only active Library-owned documents belong in the
default lexical/vector corpus.  History is an explicit opt-in, and identical
bytes are indexed once.  Documents owned by other repositories are read where
they live, from checkouts named explicitly as `REPOSITORY=PATH`.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


ACTIVE_ROOTS = frozenset({"docs", "experiments", "findings", "specs"})
HISTORY_PREFIXES = (
    ("catalog", "corpus"),
    ("docs", "archive"),
)
IGNORED_PARTS = frozenset(
    {".git", ".pytest_cache", "__pycache__", "site", "_site"}
)
_HASH_SUFFIX = re.compile(r"_[0-9a-f]{8,12}(?=\.md$)", re.IGNORECASE)
_OWNED = re.compile(r"([^:]+):(.+)")
_REPOSITORY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*)?")


def validate_repository_name(value: Any) -> str:
    """Validate an explicit repository identity, independent of its ecosystem."""
    if not isinstance(value, str) or len(value) > 256 or not _REPOSITORY.fullmatch(value):
        raise ValueError("invalid repository name")
    return value


def relative_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def is_history_path(relative_path: str) -> bool:
    parts = tuple(Path(relative_path).parts)
    return any(parts[: len(prefix)] == prefix for prefix in HISTORY_PREFIXES)


def is_default_index_path(relative_path: str) -> bool:
    """Return whether a Markdown path belongs in the default active corpus."""

    parts = Path(relative_path).parts
    if not parts or any(part in IGNORED_PARTS for part in parts):
        return False
    if is_history_path(relative_path):
        return False
    if len(parts) == 1:
        return relative_path.lower().endswith(".md")
    return parts[0] in ACTIVE_ROOTS and relative_path.lower().endswith(".md")


def _rank(relative_path: str) -> tuple[int, int, bytes]:
    """Prefer stable unsuffixed, shorter paths when equal bytes are present."""

    filename = Path(relative_path).name
    return (
        1 if _HASH_SUFFIX.search(filename) else 0,
        len(relative_path.encode("utf-8")),
        relative_path.encode("utf-8"),
    )


def is_retrievable_document_path(relative_path: str, *, include_history: bool = False) -> bool:
    """Scope existing index rows without loading, deleting or reindexing payloads.

    Owner documents keep their repository-qualified identity, `repository:path`.
    Their owner may use different active roots; this checks scope, not freshness
    or provenance.
    """
    match = _OWNED.fullmatch(relative_path)
    path = relative_path
    if match:
        try:
            validate_repository_name(match[1])
        except ValueError:
            return False
        path = match[2]
    path = path.replace("\\", "/")
    parts = PurePosixPath(path).parts
    if (not parts or ":" in path or "\0" in path
            or any(part in ("", ".", "..") for part in path.split("/"))
            or not path.lower().endswith(".md")
            or any(part in IGNORED_PARTS for part in parts)):
        return False
    if is_history_path(path):
        return include_history
    if match:
        return parts[0] != "catalog"  # Generated projections are never payloads.
    return is_default_index_path(path)


def collect_indexable_markdown(
    root_dir: str | Path,
    *,
    include_history: bool = False,
    deduplicate: bool = True,
) -> list[Path]:
    """Collect a deterministic, content-deduplicated Markdown corpus."""

    root = Path(root_dir).resolve()
    candidates: list[tuple[str, Path]] = []
    for path in root.rglob("*"):
        if path.suffix.lower() != ".md" or not path.is_file():
            continue
        relative = relative_posix(path, root)
        parts = Path(relative).parts
        if any(part in IGNORED_PARTS for part in parts):
            continue
        if is_default_index_path(relative) or (
            include_history and is_history_path(relative)
        ):
            candidates.append((relative, path))

    candidates.sort(key=lambda item: _rank(item[0]))
    if not deduplicate:
        return [path for _, path in candidates]

    selected: list[tuple[str, Path]] = []
    seen_hashes: set[str] = set()
    for relative, path in candidates:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen_hashes:
            continue
        seen_hashes.add(digest)
        selected.append((relative, path))
    selected.sort(key=lambda item: item[0].encode("utf-8"))
    return [path for _, path in selected]


def indexed_relative_paths(
    root_dir: str | Path, *, include_history: bool = False
) -> list[str]:
    root = Path(root_dir).resolve()
    return [
        relative_posix(path, root)
        for path in collect_indexable_markdown(root, include_history=include_history)
    ]


def parse_owner_roots(values: Iterable[str]) -> dict[str, Path]:
    """Owner checkouts selected as `REPOSITORY=PATH`, one per repository."""
    roots: dict[str, Path] = {}
    for item in values:
        repository, separator, path = item.partition("=")
        if not separator or not path or repository in roots:
            raise ValueError("--owner-root requires unique REPOSITORY=PATH selections")
        roots[validate_repository_name(repository)] = Path(path)
    return roots


def owner_markdown(
    repository: str, root: str | Path, *, include_history: bool = False
) -> list[tuple[str, Path]]:
    """`(repository:path, file)` for the tracked Markdown of an owner checkout, read where it lives."""

    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=False, timeout=60
    )
    if result.returncode:
        raise ValueError(f"Owner checkout unavailable: {repository}")
    documents = []
    for name in sorted(result.stdout.decode("utf-8").split("\0")):
        identity, path = f"{repository}:{name}", Path(root) / name
        if name and is_retrievable_document_path(identity, include_history=include_history) and path.is_file():
            documents.append((identity, path))
    return documents
