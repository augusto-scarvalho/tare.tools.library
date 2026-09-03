"""Zero-Cost Corpus Embedding & Semantic Vector Indexer for tare.tools.library.

Vectorizes Markdown files into a local SQLite database (catalog/library_vectors.db)
using the local GPU node aaaaa (RTX 3090 / slop.cpp) with zero cloud API costs per ADR-048 & ADR-051.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig
from tools.document_scope import collect_indexable_markdown


@dataclass
class VectorSearchResult:
    doc_id: str
    relative_path: str
    chunk_index: int
    text_snippet: str
    score: float


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two vector embeddings with strict dimension equality."""
    if len(v1) != len(v2):
        raise ValueError(f"Vector dimension mismatch: query dimension ({len(v1)}) != target dimension ({len(v2)})")
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)


class LibraryVectorDB:
    """SQLite-backed vector store for local embeddings with provenance & dimension guards."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or (ROOT / "catalog" / "library_vectors.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA busy_timeout=5000;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doc_id TEXT NOT NULL,
                    relative_path TEXT NOT NULL,
                    chunk_index INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    dimensions INTEGER NOT NULL DEFAULT 32,
                    provenance TEXT NOT NULL DEFAULT 'real',
                    model_name TEXT NOT NULL DEFAULT 'local-embed',
                    embedding_json TEXT NOT NULL,
                    UNIQUE(relative_path, chunk_index)
                )
            """)
            # Check existing columns for auto-migration
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(document_chunks);")
            cols = {row[1] for row in cursor.fetchall()}
            if "dimensions" not in cols:
                conn.execute("ALTER TABLE document_chunks ADD COLUMN dimensions INTEGER NOT NULL DEFAULT 32;")
            if "provenance" not in cols:
                conn.execute("ALTER TABLE document_chunks ADD COLUMN provenance TEXT NOT NULL DEFAULT 'real';")
            if "model_name" not in cols:
                conn.execute("ALTER TABLE document_chunks ADD COLUMN model_name TEXT NOT NULL DEFAULT 'local-embed';")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_ns ON document_chunks(dimensions, provenance, model_name);")
            conn.commit()
        finally:
            conn.close()

    def upsert_chunk(
        self,
        doc_id: str,
        relative_path: str,
        chunk_index: int,
        chunk_text: str,
        sha256: str,
        embedding: List[float],
        provenance: str = "real",
        model_name: str = "local-embed",
        max_retries: int = 3,
    ):
        import time
        for attempt in range(max_retries):
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            try:
                conn.execute("""
                    INSERT INTO document_chunks (doc_id, relative_path, chunk_index, chunk_text, sha256, dimensions, provenance, model_name, embedding_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(relative_path, chunk_index) DO UPDATE SET
                        chunk_text=excluded.chunk_text,
                        sha256=excluded.sha256,
                        dimensions=excluded.dimensions,
                        provenance=excluded.provenance,
                        model_name=excluded.model_name,
                        embedding_json=excluded.embedding_json
                """, (doc_id, relative_path, chunk_index, chunk_text, sha256, len(embedding), provenance, model_name, json.dumps(embedding)))
                conn.commit()
                return
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(0.05 * (2 ** attempt))
                    continue
                raise
            finally:
                conn.close()

    def upsert_document_chunks(
        self,
        doc_id: str,
        relative_path: str,
        chunks: List[Tuple[int, str, str, List[float]]],
        provenance: str = "real",
        model_name: str = "local-embed",
        max_retries: int = 5,
    ) -> bool:
        """Atomically upsert all chunks for a document in a single transaction (all-or-nothing)."""
        import time
        for attempt in range(max_retries):
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            try:
                conn.execute("PRAGMA busy_timeout=10000;")
                with conn:
                    # Invariant: Never allow pseudo/hash vectors to overwrite existing real embeddings
                    if provenance == "pseudo":
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM document_chunks WHERE relative_path = ? AND provenance = 'real'", (relative_path,))
                        row = cursor.fetchone()
                        if row and row[0] > 0:
                            # Real vectors already exist; preserve them and abort pseudo overwrite
                            return True

                    conn.execute("DELETE FROM document_chunks WHERE relative_path = ? AND model_name = ?", (relative_path, model_name))
                    for chunk_idx, chunk_text, sha, emb in chunks:
                        conn.execute("""
                            INSERT INTO document_chunks (doc_id, relative_path, chunk_index, chunk_text, sha256, dimensions, provenance, model_name, embedding_json)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (doc_id, relative_path, chunk_idx, chunk_text, sha, len(emb), provenance, model_name, json.dumps(emb)))
                return True
            except sqlite3.OperationalError as e:
                if ("locked" in str(e).lower() or "busy" in str(e).lower()) and attempt < max_retries - 1:
                    time.sleep(0.05 * (2 ** attempt))
                    continue
                raise
            finally:
                conn.close()
        return False

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        provenance: Optional[str] = "real",
        model_name: Optional[str] = "local-embed",
        allow_any_namespace: bool = False,
    ) -> List[VectorSearchResult]:
        results = []
        q_dim = len(query_embedding)
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            cursor = conn.cursor()
            if allow_any_namespace:
                cursor.execute("SELECT doc_id, relative_path, chunk_index, chunk_text, dimensions, provenance, model_name, embedding_json FROM document_chunks WHERE dimensions = ?", (q_dim,))
            else:
                cursor.execute("SELECT doc_id, relative_path, chunk_index, chunk_text, dimensions, provenance, model_name, embedding_json FROM document_chunks WHERE dimensions = ? AND provenance = ? AND model_name = ?", (q_dim, provenance, model_name))
            for row in cursor.fetchall():
                doc_id, rel_path, c_idx, text, dim, prov, mod_name, emb_json = row
                emb = json.loads(emb_json)
                sim = cosine_similarity(query_embedding, emb)
                results.append(VectorSearchResult(
                    doc_id=doc_id,
                    relative_path=rel_path,
                    chunk_index=c_idx,
                    text_snippet=f"[{prov.upper()}|{mod_name}] " + text[:300] + ("..." if len(text) > 300 else ""),
                    score=sim,
                ))
        finally:
            conn.close()

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def count_chunks(self) -> int:
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM document_chunks")
            row = cursor.fetchone()
            return row[0] if row else 0
        finally:
            conn.close()

    def get_indexed_file_hashes(self, model_name: str = "local-embed") -> Dict[str, str]:
        """Return mapping of relative_path -> sha256 for all indexed documents in this model namespace."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT relative_path, sha256 FROM document_chunks WHERE model_name = ?", (model_name,))
            return {row[0]: row[1] for row in cursor.fetchall()}
        finally:
            conn.close()

    def remove_stale_documents(self, active_relative_paths: set, model_name: str = "local-embed") -> int:
        """Remove vector records for files that have been deleted or renamed."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT relative_path FROM document_chunks WHERE model_name = ?", (model_name,))
            existing = {row[0] for row in cursor.fetchall()}
            stale = existing - active_relative_paths
            if stale:
                with conn:
                    for rel_path in stale:
                        conn.execute("DELETE FROM document_chunks WHERE relative_path = ? AND model_name = ?", (rel_path, model_name))
            return len(stale)
        finally:
            conn.close()


def chunk_markdown(content: str, max_chunk_tokens: int = 250) -> List[str]:
    """Split markdown into roughly paragraph-sized chunks for dense embedding."""
    paragraphs = re.split(r"\n\s*\n", content)
    chunks = []
    current_chunk = []
    current_len = 0

    for p in paragraphs:
        p_clean = p.strip()
        if not p_clean:
            continue
        p_len = len(p_clean.split())
        if current_len + p_len > max_chunk_tokens and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [p_clean]
            current_len = p_len
        else:
            current_chunk.append(p_clean)
            current_len += p_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    return chunks


def index_corpus(
    root_dir: Path,
    client: Optional[LocalInferenceClient] = None,
    db: Optional[LibraryVectorDB] = None,
    model_name: str = "local-embed",
    force_reindex: bool = False,
    include_history: bool = False,
) -> int:
    """Incrementally index the active, exact-content-deduplicated corpus."""
    client = client or LocalInferenceClient()
    db = db or LibraryVectorDB(root_dir / "catalog" / "library_vectors.db")
    server_online = client.health_check(target="embed").get("online", False)

    all_files = collect_indexable_markdown(
        root_dir, include_history=include_history, deduplicate=True
    )
    total_files = len(all_files)
    active_paths = {str(f.relative_to(root_dir)).replace("\\", "/") for f in all_files}

    # 1. Clean up deleted/renamed documents
    stale_count = db.remove_stale_documents(active_paths, model_name=model_name)
    if stale_count:
        print(f"[INDEXER] Removed {stale_count} stale documents from vector store.")

    # 2. Get existing hashes for incremental skip
    existing_hashes = {} if force_reindex else db.get_indexed_file_hashes(model_name=model_name)

    # 3. Identify modified/new files
    files_to_index = []
    for f in all_files:
        rel_path = str(f.relative_to(root_dir)).replace("\\", "/")
        content = f.read_text(encoding="utf-8", errors="ignore")
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        if rel_path not in existing_hashes or existing_hashes[rel_path] != sha:
            files_to_index.append((f, rel_path, content, sha))

    skipped = total_files - len(files_to_index)
    print(f"[INDEXER] Starting incremental vector indexing. Server online: {server_online} (Mode: {'DENSE NEURAL (RTX 3090)' if server_online else 'PSEUDO-HASH'})")
    print(f"[INDEXER] Total: {total_files} docs | Unchanged (Skipped): {skipped} | Need Vectorizing: {len(files_to_index)}")

    if not files_to_index:
        print(f"✅ [INDEXER COMPLETE] All {total_files} documents are already up to date in '{db.db_path}'! (0 embeddings computed)", flush=True)
        return 0

    total_indexed_chunks = 0
    for idx, (file_path, rel_path, content, sha) in enumerate(files_to_index, 1):
        chunks = chunk_markdown(content)
        if not chunks:
            continue

        try:
            if server_online:
                embs = client.generate_embeddings(chunks)
                prov = "real"
            else:
                embs = None
                prov = "pseudo"

            doc_chunk_tuples = []
            for c_idx, chunk in enumerate(chunks):
                if embs and c_idx < len(embs):
                    emb = embs[c_idx]
                else:
                    digest = hashlib.sha256(chunk.encode("utf-8")).digest()
                    emb = [float(b) / 255.0 for b in digest]
                doc_chunk_tuples.append((c_idx, chunk, sha, emb))

            db.upsert_document_chunks(
                doc_id=file_path.stem,
                relative_path=rel_path,
                chunks=doc_chunk_tuples,
                provenance=prov,
                model_name=model_name,
            )
            total_indexed_chunks += len(doc_chunk_tuples)
            print(f"  [EMBED {idx}/{len(files_to_index)}] Ingerido: {rel_path} ({len(chunks)} chunks)", flush=True)
        except Exception as e:
            print(f"  Error indexing '{rel_path}': {e}", flush=True)

    print(f"✅ [INDEXER COMPLETE] Incrementally indexed {total_indexed_chunks} new/updated chunks into '{db.db_path}' (Total in DB: {db.count_chunks()})", flush=True)
    return total_indexed_chunks


def main() -> int:
    parser = argparse.ArgumentParser(description="Zero-Cost Vector Indexer for tare.tools.library")
    parser.add_argument("--root", default=".", help="Root directory")
    parser.add_argument("--query", "-q", help="Search vector database with query string")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of results")
    parser.add_argument("--model", default="local-embed", help="Model namespace")
    parser.add_argument("--force-local", action="store_true", help="Force execution on thin client despite ADR-053")
    parser.add_argument("--reindex-all", action="store_true", help="Force reindexing all files, bypassing incremental cache")
    parser.add_argument(
        "--include-history",
        action="store_true",
        help="Also index immutable archive/snapshot documents (still exact-content deduplicated)",
    )

    args = parser.parse_args()
    root_path = Path(args.root).resolve()
    db = LibraryVectorDB(root_path / "catalog" / "library_vectors.db")
    client = LocalInferenceClient()

    if args.query:
        print(f"[SEARCH] Querying: '{args.query}'...")
        if client.health_check().get("online"):
            q_emb = client.generate_embeddings([args.query])[0]
            prov = "real"
        else:
            q_digest = hashlib.sha256(args.query.encode("utf-8")).digest()
            q_emb = [float(b) / 255.0 for b in q_digest]
            prov = args.provenance or "pseudo"

        results = db.search(q_emb, top_k=args.top_k, provenance=prov, model_name=args.model)
        print(f"\n[RESULTS] Found {len(results)} matches in namespace ({args.model}, {prov}):")
        for i, res in enumerate(results, 1):
            print(f"{i}. [{res.score:.4f}] {res.doc_id} ({res.relative_path}#chunk-{res.chunk_index})")
            print(f"   {res.text_snippet}\n")
        return 0

    # ADR-053 Guard: Thin-clients automatically offload to Node aaaaa
    try:
        from tools.policy.compute_guard import assert_compute_guard
        from tools.bookkeeper.dispatch_job import dispatch_remote_task

        can_run_local, guard_msg = assert_compute_guard(
            task_name="embed_corpus",
            item_count=1000,
            threshold=50,
            force_local=args.force_local,
        )
        if not can_run_local:
            print(guard_msg)
            return dispatch_remote_task(
                "cd /home/augus/src/tare.tools.library && python3 tools/indexer/embed_corpus.py --root ."
            )
    except ImportError:
        pass

    indexed = index_corpus(
        root_path,
        client,
        db,
        model_name=args.model,
        force_reindex=args.reindex_all,
        include_history=args.include_history,
    )
    return 0 if indexed >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
