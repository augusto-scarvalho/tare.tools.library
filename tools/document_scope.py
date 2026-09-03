"""Deterministic Markdown scope for the active Library corpus.

The repository contains active knowledge, generated catalogs and immutable
historical snapshots.  Only active Library-owned documents belong in the
default lexical/vector corpus.  History is an explicit opt-in, and identical
bytes are indexed once.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Iterable


ACTIVE_ROOTS = frozenset({"docs", "experiments", "findings", "specs"})
HISTORY_PREFIXES = (
    ("catalog", "corpus"),
    ("docs", "archive"),
)
IGNORED_PARTS = frozenset(
    {".git", ".pytest_cache", "__pycache__", "site", "_site"}
)
_HASH_SUFFIX = re.compile(r"_[0-9a-f]{8,12}(?=\.md$)", re.IGNORECASE)


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


def collect_indexable_markdown(
    root_dir: str | Path,
    *,
    include_history: bool = False,
    deduplicate: bool = True,
) -> list[Path]:
    """Collect a deterministic, content-deduplicated Markdown corpus."""

    root = Path(root_dir).resolve()
    candidates: list[tuple[str, Path]] = []
    for path in root.rglob("*.md"):
        if not path.is_file():
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
