"""Automated Document Ingestion Tool for tare.tools.library.

Provides unified, zero-friction ingestion of architectural decisions, specifications,
empirical experiments, incident post-mortems, and historical chat transcripts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.bookkeeper.dedup_detector import detect_duplicates, compute_similarity


@dataclass
class IngestionResult:
    success: bool
    target_path: Optional[Path]
    doc_id: str
    sha256: str
    message: str
    is_duplicate: bool = False
    duplicate_match: Optional[str] = None


TYPE_ROUTING = {
    "adr": ("docs/adr", "ADR"),
    "spec": ("specs", "SPEC"),
    "experiment": ("experiments", "EXP"),
    "post-mortem": ("docs/post-mortems", "PM"),
    "chat": ("archaeology/chats", "CHAT"),
    "historical": ("archaeology/historical", "HIST"),
}


def compute_sha256(data: bytes) -> str:
    """Compute SHA-256 digest of bytes."""
    return hashlib.sha256(data).hexdigest()


def ingest_document(
    source_path: str | Path,
    doc_type: str,
    title: str = "",
    category: str = "",
    force: bool = False,
    root_dir: str | Path = ROOT,
) -> IngestionResult:
    """Ingest a markdown document into the library with automated deduplication and cataloging."""
    src = Path(source_path)
    root = Path(root_dir)

    if not src.exists():
        return IngestionResult(
            success=False,
            target_path=None,
            doc_id="",
            sha256="",
            message=f"Source file does not exist: {source_path}",
        )

    doc_type = doc_type.lower().strip()
    if doc_type not in TYPE_ROUTING:
        return IngestionResult(
            success=False,
            target_path=None,
            doc_id="",
            sha256="",
            message=f"Invalid document type '{doc_type}'. Allowed: {list(TYPE_ROUTING.keys())}",
        )

    raw_bytes = src.read_bytes()
    raw_text = raw_bytes.decode("utf-8", errors="ignore")
    digest = compute_sha256(raw_bytes)

    # 1. Deduplication check across existing active docs
    if not force:
        # Check against existing docs (excluding the source file itself)
        src_resolved = src.resolve()
        for existing in root.rglob("*.md"):
            if existing.is_file() and existing.resolve() != src_resolved and not any(part in existing.parts for part in (".git", ".pytest_cache", "__pycache__")):
                try:
                    existing_text = existing.read_text(encoding="utf-8", errors="ignore")
                    sim = compute_similarity(raw_text, existing_text)
                    if sim >= 0.90:
                        return IngestionResult(
                            success=False,
                            target_path=existing,
                            doc_id=existing.stem,
                            sha256=digest,
                            message=f"Duplicate content detected (similarity: {sim*100:.1f}%) with existing file '{existing.relative_to(root)}'",
                            is_duplicate=True,
                            duplicate_match=str(existing.relative_to(root)),
                        )
                except Exception:
                    continue

    # 2. Derive Destination Path & ID
    base_subpath, prefix = TYPE_ROUTING[doc_type]
    dest_dir = root / base_subpath
    if category and doc_type == "experiment":
        dest_dir = dest_dir / category

    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_filename = src.name
    target_file = dest_dir / dest_filename

    # If target exists and not forcing, create a timestamped or indexed name
    if target_file.exists() and not force:
        stem = src.stem
        suffix = src.suffix
        target_file = dest_dir / f"{stem}_{digest[:8]}{suffix}"

    target_file.write_bytes(raw_bytes)

    doc_id = target_file.stem
    rel_path = str(target_file.relative_to(root)).replace("\\", "/")

    # 3. Update or Append to Master Catalog JSON if present
    catalog_json_path = root / "catalog" / "MASTER_CATALOG.json"
    if catalog_json_path.exists():
        try:
            catalog = json.loads(catalog_json_path.read_text(encoding="utf-8"))
            if isinstance(catalog, list):
                # Check if already present
                existing_entry = next((e for e in catalog if e.get("path") == rel_path or e.get("id") == doc_id), None)
                if not existing_entry:
                    catalog.append({
                        "id": doc_id,
                        "title": title or src.stem.replace("-", " ").replace("_", " ").title(),
                        "type": doc_type,
                        "path": rel_path,
                        "sha256": digest,
                        "status": "CANONICAL_SSOT" if doc_type in ("adr", "spec") else "RECORDED",
                    })
                    catalog_json_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    return IngestionResult(
        success=True,
        target_path=target_file,
        doc_id=doc_id,
        sha256=digest,
        message=f"Successfully ingested as '{rel_path}' [SHA-256: {digest[:12]}...]",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated Ingestion CLI for tare.tools.library")
    parser.add_argument("--file", "-f", required=True, help="Path to markdown document to ingest")
    parser.add_argument("--type", "-t", required=True, choices=list(TYPE_ROUTING.keys()), help="Document type")
    parser.add_argument("--title", help="Human-readable title (defaults to filename)")
    parser.add_argument("--category", "-c", default="", help="Sub-category (e.g. 'local-llm', 'routing' for experiments)")
    parser.add_argument("--force", action="store_true", help="Force ingestion even if similarity > 90%")
    parser.add_argument("--root", default=".", help="Root directory of tare.tools.library")

    args = parser.parse_args()
    res = ingest_document(
        source_path=args.file,
        doc_type=args.type,
        title=args.title or "",
        category=args.category,
        force=args.force,
        root_dir=args.root,
    )

    if res.success:
        print(f"[INGESTION SUCCESS] {res.message}")
        print(f"  - Doc ID: {res.doc_id}")
        print(f"  - Path: {res.target_path}")
        print(f"  - SHA-256: {res.sha256}")
        return 0
    else:
        print(f"[INGESTION ERROR] {res.message}")
        if res.is_duplicate:
            print(f"  - Conflicting File: {res.duplicate_match}")
            print("  - Use --force to override deduplication rejection.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
