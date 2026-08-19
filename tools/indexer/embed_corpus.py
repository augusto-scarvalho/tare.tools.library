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
                    dimensions INTEGER NOT NULL,
                    provenance TEXT NOT NULL,
                    embedding_json TEXT NOT NULL,
                    UNIQUE(relative_path, chunk_index)
                )
            """)
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
        max_retries: int = 3,
    ):
        import time
        for attempt in range(max_retries):
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            try:
                conn.execute("""
                    INSERT INTO document_chunks (doc_id, relative_path, chunk_index, chunk_text, sha256, dimensions, provenance, embedding_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(relative_path, chunk_index) DO UPDATE SET
                        chunk_text=excluded.chunk_text,
                        sha256=excluded.sha256,
                        dimensions=excluded.dimensions,
                        provenance=excluded.provenance,
                        embedding_json=excluded.embedding_json
                """, (doc_id, relative_path, chunk_index, chunk_text, sha256, len(embedding), provenance, json.dumps(embedding)))
                conn.commit()
                return
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(0.05 * (2 ** attempt))
                    continue
                raise
            finally:
                conn.close()

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[VectorSearchResult]:
        results = []
        q_dim = len(query_embedding)
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT doc_id, relative_path, chunk_index, chunk_text, dimensions, provenance, embedding_json FROM document_chunks")
            for row in cursor.fetchall():
                doc_id, rel_path, c_idx, text, dim, prov, emb_json = row
                if dim != q_dim:
                    continue  # Fail-safe skip on dimension mismatch
                emb = json.loads(emb_json)
                sim = cosine_similarity(query_embedding, emb)
                results.append(VectorSearchResult(
                    doc_id=doc_id,
                    relative_path=rel_path,
                    chunk_index=c_idx,
                    text_snippet=f"[{prov.upper()}] " + text[:300] + ("..." if len(text) > 300 else ""),
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
            return cursor.fetchone()[0]
        finally:
            conn.close()


def chunk_markdown(text: str, chunk_size: int = 1500) -> List[str]:
    """Split markdown text into logical paragraph-bounded chunks."""
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = []
    current_len = 0

    for p in paragraphs:
        p_len = len(p)
        if current_len + p_len > chunk_size and current_chunk:
            chunks.append("\n\n".join(current_chunk).strip())
            current_chunk = [p]
            current_len = p_len
        else:
            current_chunk.append(p)
            current_len += p_len

    if current_chunk:
        chunks.append("\n\n".join(current_chunk).strip())
    return [c for c in chunks if len(c.strip()) > 30]


def index_corpus(
    root_dir: Path = ROOT,
    client: Optional[LocalInferenceClient] = None,
    db: Optional[LibraryVectorDB] = None,
) -> int:
    """Index active markdown documents in the library."""
    client = client or LocalInferenceClient()
    db = db or LibraryVectorDB()

    # Check if local server is online
    status = client.health_check()
    is_online = status.get("online", False)

    target_dirs = [root_dir / "docs", root_dir / "specs", root_dir / "experiments"]
    total_indexed = 0

    print(f"[INDEXER] Scanning corpus in '{root_dir}'...")
    if not is_online:
        print("⚠️ [WARNING] Local inference server (slop.cpp @ aaaaa) is offline.")
        print("  Generating fallback deterministic pseudo-embeddings for offline validation.")

    for base_dir in target_dirs:
        if not base_dir.exists():
            continue
        for file_path in base_dir.rglob("*.md"):
            if file_path.name.upper() == "README.MD" or ".git" in file_path.parts:
                continue

            rel_path = str(file_path.relative_to(root_dir)).replace("\\", "/")
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                chunks = chunk_markdown(text)
                sha = hashlib.sha256(text.encode("utf-8")).hexdigest()

                for idx, chunk in enumerate(chunks):
                    prov = "real"
                    if is_online:
                        try:
                            embs = client.generate_embeddings([chunk])
                            emb = embs[0]
                        except Exception:
                            # Fallback if server error
                            prov = "pseudo"
                            emb = [float(b) / 255.0 for b in hashlib.sha256(chunk.encode("utf-8")).digest()]
                    else:
                        # Deterministic mock embedding
                        prov = "pseudo"
                        digest = hashlib.sha256(chunk.encode("utf-8")).digest()
                        emb = [float(b) / 255.0 for b in digest]

                    db.upsert_chunk(
                        doc_id=file_path.stem,
                        relative_path=rel_path,
                        chunk_index=idx,
                        chunk_text=chunk,
                        sha256=sha,
                        embedding=emb,
                        provenance=prov,
                    )
                    total_indexed += 1
            except Exception as e:
                print(f"  Error indexing '{rel_path}': {e}")

    print(f"✅ [INDEXER COMPLETE] Indexed {total_indexed} chunks into '{db.db_path}' (Total in DB: {db.count_chunks()})")
    return total_indexed


def main() -> int:
    parser = argparse.ArgumentParser(description="Zero-Cost Vector Indexer for tare.tools.library")
    parser.add_argument("--root", default=".", help="Root directory")
    parser.add_argument("--query", "-q", help="Search vector database with query string")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of results")

    args = parser.parse_args()
    root_path = Path(args.root).resolve()
    db = LibraryVectorDB(root_path / "catalog" / "library_vectors.db")
    client = LocalInferenceClient()

    if args.query:
        print(f"[SEARCH] Querying: '{args.query}'...")
        if client.health_check().get("online"):
            q_emb = client.generate_embeddings([args.query])[0]
        else:
            q_emb = [float(b) / 255.0 for b in hashlib.sha256(args.query.encode("utf-8")).digest()]

        results = db.search(q_emb, top_k=args.top_k)
        if not results:
            print("No matching vector results.")
            return 0
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r.doc_id}] ({r.relative_path}#chunk{r.chunk_index}) [Score: {r.score:.3f}]")
            print(f"   Excerpt: {r.text_snippet}\n")
        return 0

    else:
        index_corpus(root_dir=root_path, client=client, db=db)
        return 0


if __name__ == "__main__":
    sys.exit(main())
