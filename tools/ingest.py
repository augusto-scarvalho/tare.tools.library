"""Automated Document Ingestion Tool for tare.tools.library.

Provides unified, zero-friction ingestion of architectural decisions, specifications,
empirical experiments, incident post-mortems, and historical chat transcripts.
Optionally triggers local LLM summarization and dense vector indexing in one step.
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

from tools.bookkeeper.dedup_detector import detect_duplicates, compute_similarity, _normalize_text, EXCLUDE_DIRS


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
    title: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[List[str]] = None,
    force: bool = False,
    overwrite: bool = False,
    root_dir: str | Path = ROOT,
    check_duplicates: bool = True,
) -> IngestionResult:
    """Ingest, validate, classify, route, and auto-catalog a document into the library."""
    src = Path(source_path)
    root = Path(root_dir)

    if not src.exists() or not src.is_file():
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

    # 1. Deduplication check across existing active docs (if requested)
    if not force and check_duplicates:
        src_resolved = src.resolve()
        for existing in root.rglob("*.md"):
            if existing.is_file() and existing.resolve() != src_resolved and not any(part in existing.parts for part in EXCLUDE_DIRS):
                try:
                    ex_bytes = existing.read_bytes()
                    if hashlib.sha256(ex_bytes).hexdigest() == digest:
                        return IngestionResult(
                            success=False,
                            target_path=existing,
                            doc_id=existing.stem,
                            sha256=digest,
                            message=f"Exact duplicate content with existing file '{existing.relative_to(root)}'",
                            is_duplicate=True,
                            duplicate_match=str(existing.relative_to(root)),
                        )
                    ex_text = ex_bytes.decode("utf-8", errors="ignore")
                    sim = compute_similarity(raw_text, ex_text)
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

    # 2. Derive Destination Path & ID with Atomic Exclusive Creation (Zero-TOCTOU Non-Destructive)
    import time
    base_subpath, prefix = TYPE_ROUTING[doc_type]
    dest_dir = root / base_subpath
    if category and doc_type == "experiment":
        dest_dir = dest_dir / category

    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_filename = src.name
    target_file = dest_dir / dest_filename

    if overwrite:
        target_file.write_bytes(raw_bytes)
    else:
        # Atomic non-destructive write loop: attempt exclusive creation ('xb')
        written = False
        candidates = [
            target_file,
            dest_dir / f"{src.stem}_{digest[:8]}{src.suffix}",
            dest_dir / f"{src.stem}_{digest[:12]}{src.suffix}",
        ]
        for candidate in candidates:
            try:
                with candidate.open("xb") as f:
                    f.write(raw_bytes)
                    f.flush()
                target_file = candidate
                written = True
                break
            except FileExistsError:
                continue

        if not written:
            unique_name = f"{src.stem}_{digest[:8]}_{int(time.time()*1000)}{src.suffix}"
            target_file = dest_dir / unique_name
            with target_file.open("xb") as f:
                f.write(raw_bytes)
                f.flush()

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


def auto_index_file(target_file: Path, root_dir: Path) -> int:
    """Vectorize single ingested document into SQLite Vector store."""
    from tools.inference.local_client import LocalInferenceClient
    from tools.indexer.embed_corpus import LibraryVectorDB, chunk_markdown

    client = LocalInferenceClient()
    db = LibraryVectorDB(root_dir / "catalog" / "library_vectors.db")
    content = target_file.read_text(encoding="utf-8", errors="ignore")
    chunks = chunk_markdown(content)
    if not chunks:
        return 0

    rel_path = str(target_file.relative_to(root_dir)).replace("\\", "/")
    sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
    server_online = client.health_check().get("online", False)

    try:
        embs = client.generate_embeddings(chunks) if server_online else None
        prov = "real" if embs else "pseudo"
    except Exception:
        embs = None
        prov = "pseudo"

    chunk_tuples = []
    for idx, chunk in enumerate(chunks):
        if embs and idx < len(embs):
            emb = embs[idx]
        else:
            digest = hashlib.sha256(chunk.encode("utf-8")).digest()
            emb = [float(b) / 255.0 for b in digest]
        chunk_tuples.append((idx, chunk, sha, emb))

    db.upsert_document_chunks(
        doc_id=target_file.stem,
        relative_path=rel_path,
        chunks=chunk_tuples,
        provenance=prov,
        model_name="local-embed",
    )
    return len(chunk_tuples)


def main() -> int:
    parser = argparse.ArgumentParser(description="Automated Ingestion CLI for tare.tools.library")
    parser.add_argument("--file", "-f", required=True, help="Path to markdown document to ingest")
    parser.add_argument("--type", "-t", required=True, choices=list(TYPE_ROUTING.keys()), help="Document type")
    parser.add_argument("--title", help="Human-readable title (defaults to filename)")
    parser.add_argument("--category", "-c", default="", help="Sub-category (e.g. 'local-llm', 'routing' for experiments)")
    parser.add_argument("--embed", "-e", action="store_true", help="Automatically vectorize and index into catalog/library_vectors.db")
    parser.add_argument("--summarize", "-s", action="store_true", help="Automatically generate executive summary & ontology tags via local LLM")
    parser.add_argument("--force", action="store_true", help="Force ingestion even if similarity > 90%")
    parser.add_argument("--root", default=".", help="Root directory of tare.tools.library")

    args = parser.parse_args()
    root_path = Path(args.root).resolve()

    res = ingest_document(
        source_path=args.file,
        doc_type=args.type,
        title=args.title or "",
        category=args.category,
        force=args.force,
        root_dir=root_path,
    )

    if not res.success:
        print(f"[INGESTION ERROR] {res.message}")
        if res.is_duplicate:
            print(f"  - Conflicting File: {res.duplicate_match}")
            print("  - Use --force to override deduplication rejection.")
        return 1

    print(f"[INGESTION SUCCESS] {res.message}")
    print(f"  - Doc ID: {res.doc_id}")
    print(f"  - Path: {res.target_path}")
    print(f"  - SHA-256: {res.sha256}")

    if args.embed and res.target_path:
        count = auto_index_file(res.target_path, root_path)
        print(f"  - Vector DB: {count} chunks embedded and indexed into catalog/library_vectors.db")

    if args.summarize and res.target_path:
        from tools.inference.summarize_reference import summarize_document
        print("\n[*] Generating Architectural Summary via Local LLM...")
        sum_res = summarize_document(res.target_path)
        print(f"  - Resumo: {sum_res.get('executive_summary')}")
        if sum_res.get("matched_concepts"):
            print(f"  - Conceitos: {', '.join(sum_res.get('matched_concepts'))}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
