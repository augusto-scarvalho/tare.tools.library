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
from typing import Any, Dict, List, Optional, Tuple

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

DEFAULT_NAMESPACE = LocalInferenceConfig().embedding_model  # one vector namespace per model family


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
                    concepts TEXT NOT NULL DEFAULT '[]',
                    UNIQUE(relative_path, chunk_index, model_name)
                )
            """)
            # Check existing columns for auto-migration
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(document_chunks);")
            cols = {row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'document_chunks'")
            if "model_name" in cols and "UNIQUE(relative_path, chunk_index)" in (cursor.fetchone() or [""])[0]:
                # Old uniqueness ignored the namespace, so two model families could not coexist. Rebuild.
                conn.executescript("""
                    ALTER TABLE document_chunks RENAME TO document_chunks_old;
                    CREATE TABLE document_chunks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, doc_id TEXT NOT NULL, relative_path TEXT NOT NULL,
                        chunk_index INTEGER NOT NULL, chunk_text TEXT NOT NULL, sha256 TEXT NOT NULL,
                        dimensions INTEGER NOT NULL DEFAULT 32, provenance TEXT NOT NULL DEFAULT 'real',
                        model_name TEXT NOT NULL DEFAULT 'local-embed', embedding_json TEXT NOT NULL,
                        concepts TEXT NOT NULL DEFAULT '[]',
                        UNIQUE(relative_path, chunk_index, model_name));
                    INSERT INTO document_chunks (doc_id, relative_path, chunk_index, chunk_text, sha256, dimensions, provenance, model_name, embedding_json)
                        SELECT doc_id, relative_path, chunk_index, chunk_text, sha256, dimensions, provenance, model_name, embedding_json FROM document_chunks_old;
                    DROP TABLE document_chunks_old;
                """)
                cols.add("concepts")
            if "concepts" not in cols:
                conn.execute("ALTER TABLE document_chunks ADD COLUMN concepts TEXT NOT NULL DEFAULT '[]';")
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
        model_name: str = DEFAULT_NAMESPACE,
        max_retries: int = 3,
    ):
        import time
        for attempt in range(max_retries):
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            try:
                conn.execute("""
                    INSERT INTO document_chunks (doc_id, relative_path, chunk_index, chunk_text, sha256, dimensions, provenance, model_name, embedding_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(relative_path, chunk_index, model_name) DO UPDATE SET
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
        model_name: str = DEFAULT_NAMESPACE,
        max_retries: int = 5,
        concepts: Optional[List[str]] = None,
    ) -> bool:
        """Atomically upsert all chunks for a document in a single transaction (all-or-nothing)."""
        concepts_json = json.dumps(sorted(concepts or []))
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
                            INSERT INTO document_chunks (doc_id, relative_path, chunk_index, chunk_text, sha256, dimensions, provenance, model_name, embedding_json, concepts)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (doc_id, relative_path, chunk_idx, chunk_text, sha, len(emb), provenance, model_name, json.dumps(emb), concepts_json))
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
        model_name: Optional[str] = DEFAULT_NAMESPACE,
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

    def get_indexed_file_hashes(self, model_name: str = DEFAULT_NAMESPACE, include_pseudo: bool = True) -> Dict[str, str]:
        """Return mapping of relative_path -> sha256 for indexed documents in this model namespace.

        With include_pseudo=False, pseudo-hash rows are left out: they are placeholders written
        while the embedding server was down, so an online pass must re-vectorize them."""
        conn = sqlite3.connect(self.db_path, timeout=5.0)
        try:
            cursor = conn.cursor()
            clause = "" if include_pseudo else " AND provenance != 'pseudo'"
            cursor.execute("SELECT DISTINCT relative_path, sha256 FROM document_chunks WHERE model_name = ?" + clause, (model_name,))
            return {row[0]: row[1] for row in cursor.fetchall()}
        finally:
            conn.close()

    def remove_stale_documents(self, active_relative_paths: set, model_name: str = DEFAULT_NAMESPACE) -> int:
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


MAX_PARAGRAPH_CHARS = 1200  # ~300-400 tokens: under the embedding server's per-input limit (nomic: 2048)
# Documents are embedded in groups of this many chunks so one request fills the server's batch and its
# parallel slots instead of one short request per document. ponytail: fixed size, tune if the server changes.
EMBED_GROUP_CHUNKS = 256


def _bounded_paragraphs(paragraphs: List[str]) -> List[str]:
    """Split paragraphs that never break on blank lines (tables, long lists) at line boundaries."""
    bounded = []
    for p in paragraphs:
        if len(p) <= MAX_PARAGRAPH_CHARS:
            bounded.append(p)
            continue
        piece = ""
        for line in p.splitlines(keepends=True):
            while len(line) > MAX_PARAGRAPH_CHARS:  # one line longer than the cap: hard cut
                bounded.append(piece + line[:MAX_PARAGRAPH_CHARS]); piece, line = "", line[MAX_PARAGRAPH_CHARS:]
            if len(piece) + len(line) > MAX_PARAGRAPH_CHARS:
                bounded.append(piece); piece = ""
            piece += line
        if piece.strip():
            bounded.append(piece)
    return bounded


_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_ADR_REF = re.compile(r"ADR-\d{3}")
MAX_HEADER_CHARS = 360  # identity + triples; never lets the header outweigh the chunk body


def chunk_markdown(content: str, max_chunk_tokens: int = 250, header: str = "") -> List[str]:
    """Split markdown into roughly paragraph-sized chunks for dense embedding.

    Every chunk is prefixed with `header` (document identity and ontology triples) and the path
    of its enclosing markdown headings, so it embeds with its context, not as an orphan paragraph
    (ARCHITECTURAL_QA_LEDGER Perguntas 18 and 35)."""
    paragraphs = re.split(r"\n\s*\n", content)
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_len = 0
    headings: List[Tuple[int, str]] = []
    section = ""

    def flush() -> None:
        prefix = " | ".join(part for part in (header.strip()[:MAX_HEADER_CHARS], section) if part)
        chunks.append((prefix + "\n" if prefix else "") + "\n\n".join(current_chunk))

    for p in _bounded_paragraphs(paragraphs):
        p_clean = p.strip()
        if not p_clean:
            continue
        match = _HEADING.match(p_clean.splitlines()[0])
        if match:
            level = len(match.group(1))
            headings = [h for h in headings if h[0] < level] + [(level, match.group(2))]
            section = " > ".join(text for _, text in headings)
        p_len = len(p_clean.split())
        if current_len + p_len > max_chunk_tokens and current_chunk:
            flush()
            current_chunk = [p_clean]
            current_len = p_len
        else:
            current_chunk.append(p_clean)
            current_len += p_len

    if current_chunk:
        flush()
    return chunks


def ontology_concepts(root_dir: Path, owner_roots: Dict[str, Path]) -> Tuple[List[Dict[str, Any]], str]:
    """Concepts of the federated domain ontologies (pinned owner blobs) and a digest of the payloads.

    The digest is folded into every document hash, so an ontology change re-embeds only the
    documents it re-anchors (living ontology, selective O(delta) re-embedding)."""
    import subprocess

    import yaml

    registry = root_dir / "catalog" / "FEDERATED_ONTOLOGIES.json"
    if not registry.exists():
        return [], ""
    payload = json.loads(registry.read_text(encoding="utf-8"))
    concepts: List[Dict[str, Any]] = []
    digests: List[str] = []
    for ontology in payload.get("ontologies", []):
        repository, revision, path = ontology["repository"], ontology["revision"], ontology["canonical_path"]
        checkout = owner_roots.get(repository)
        if checkout is None or not (Path(checkout) / ".git").exists():
            print(f"  [ONTOLOGY] no checkout for {repository}; ontology skipped", flush=True)
            continue
        result = subprocess.run(["git", "-C", str(checkout), "show", f"{revision}:{path}"],
                                capture_output=True, check=False, timeout=30)
        if result.returncode or hashlib.sha256(result.stdout).hexdigest() != ontology["canonical_sha256"]:
            print(f"  [ONTOLOGY] {repository}@{revision[:10]}:{path} unavailable or hash mismatch; skipped", flush=True)
            continue
        digests.append(ontology["canonical_sha256"])
        document = yaml.safe_load(result.stdout.decode("utf-8", errors="ignore")) or {}
        for concept in document.get("concepts", []) or []:
            if isinstance(concept, dict) and concept.get("id"):
                concepts.append({**concept, "repository": repository})
    return concepts, hashlib.sha256("".join(sorted(digests)).encode("utf-8")).hexdigest()


def _adr_numbers(value: str) -> set:
    """ADR references as integers, so ADR-007, ADR-0007 and ADR 7 name the same decision."""
    return {int(n) for n in re.findall(r"(?i)ADR[-_ /]?0*(\d{1,4})(?!\d)", value or "")}


def document_repository(rel_path: str) -> str:
    """Owner of an indexed path: `repo@rev:path` for federated rows, the Library otherwise."""
    return rel_path.split("@", 1)[0] if "@" in rel_path else "tare.tools.library"


def anchor_concepts(text: str, document_id: str, concepts: List[Dict[str, Any]],
                    repository: Optional[str] = None) -> List[Dict[str, Any]]:
    """Deterministic entity/concept anchoring: governing ADR, concept id or concept name in the text.

    The governing-ADR rule only fires inside the concept's own repository: every satellite has an
    ADR-001, so a bare number would anchor the Backlog Graph concepts onto the SpecGraph north star."""
    lowered = text.casefold()
    adrs = _adr_numbers(document_id)
    head = document_id + "\n" + text[:600]  # identity plus the status/header block where a spec names itself
    anchored = []
    for concept in concepts:
        cid, name = str(concept.get("id", "")), str(concept.get("name", ""))
        spec = str(concept.get("governing_spec") or "")
        same_owner = repository is None or concept.get("repository") in (None, repository)
        if ((same_owner and _adr_numbers(str(concept.get("governing_adr") or "")) & adrs)
                or (same_owner and spec and re.search(r"(?<![A-Za-z0-9-])" + re.escape(spec) + r"(?![A-Za-z0-9-])", head))
                or (cid and re.search(r"(?<![A-Za-z0-9_])" + re.escape(cid) + r"(?![A-Za-z0-9_])", text))
                or (len(name) >= 8 and name.casefold() in lowered)):
            anchored.append(concept)
    return anchored


def concept_header(anchored: List[Dict[str, Any]], limit: int = 3) -> str:
    """Compact triples for the chunk header: id (name; domain; relation: targets)."""
    parts = []
    for concept in anchored[:limit]:
        bits = [str(concept.get("name") or "")]
        if concept.get("domain"):
            bits.append("dominio: " + str(concept["domain"]))
        for relation, targets in (concept.get("relationships") or {}).items():
            if isinstance(targets, list) and targets:
                bits.append(f"{relation}: {', '.join(map(str, targets[:3]))}")
        parts.append(f"{concept['id']} ({'; '.join(b for b in bits if b)})")
    return "conceitos: " + " ; ".join(parts) if parts else ""


def document_header(doc_id: str, rel_path: str, content: str) -> str:
    """Identity line: kind, id and title, so a chunk carries what it belongs to."""
    kind = "adr" if "/adr/" in rel_path.casefold() or doc_id.upper().startswith("ADR-") else (
        "spec" if "spec" in rel_path.casefold() else "doc")
    title = next((line[2:].strip() for line in content.splitlines() if line.startswith("# ")), "")
    return f"[{kind}] {doc_id}" + (f" | {title}" if title else "")


def federated_documents(root_dir: Path, owner_roots: Dict[str, Path]) -> List[Tuple[str, str, str, str]]:
    """(doc_id, canonical_path, content, sha256) for every catalog document owned by another repository.

    Content comes from the owner's pinned Git blob (`git show <revision>:<path>`), so the index
    matches the catalog's canonical_sha256 regardless of checkout EOL or local edits."""
    import subprocess
    from tools.federated_documents import load_federated_index

    payload = load_federated_index(root_dir, require_retired_absent=False)
    if payload is None:
        return []
    documents: List[Tuple[str, str, str, str]] = []
    for owner in payload["repositories"]:
        repository, revision = owner["repository"], owner["revision"]
        checkout = owner_roots.get(repository)
        if checkout is None or not (Path(checkout) / ".git").exists():
            print(f"  [FEDERATED] no checkout for {repository}; {len(owner['documents'])} documents skipped", flush=True)
            continue
        for document in owner["documents"]:
            identity = f"{revision}:{document['canonical_path']}"
            result = subprocess.run(["git", "-C", str(checkout), "show", identity], capture_output=True, check=False, timeout=30)
            if result.returncode:
                print(f"  [FEDERATED] {repository}@{identity} unavailable in checkout", flush=True)
                continue
            if hashlib.sha256(result.stdout).hexdigest() != document["canonical_sha256"]:
                print(f"  [FEDERATED] {repository}@{identity} hash mismatch; skipped", flush=True)
                continue
            documents.append((document["semantic_document_id"], f"{repository}@{revision}:{document['canonical_path']}",
                              result.stdout.decode("utf-8", errors="ignore"), document["canonical_sha256"]))
    return documents


def index_corpus(
    root_dir: Path,
    client: Optional[LocalInferenceClient] = None,
    db: Optional[LibraryVectorDB] = None,
    model_name: str = DEFAULT_NAMESPACE,
    force_reindex: bool = False,
    include_history: bool = False,
    owner_roots: Optional[Dict[str, Path]] = None,
) -> int:
    """Incrementally index the active, exact-content-deduplicated corpus (plus federated owners when given)."""
    client = client or LocalInferenceClient()
    db = db or LibraryVectorDB(root_dir / "catalog" / "library_vectors.db")
    server_online = client.health_check(target="embed").get("online", False)

    all_files = collect_indexable_markdown(
        root_dir, include_history=include_history, deduplicate=True
    )
    total_files = len(all_files)
    active_paths = {str(f.relative_to(root_dir)).replace("\\", "/") for f in all_files}
    federated = federated_documents(root_dir, owner_roots) if owner_roots is not None else []
    concepts, ontology_digest = ontology_concepts(root_dir, owner_roots) if owner_roots is not None else ([], "")
    if concepts:
        print(f"[ONTOLOGY] {len(concepts)} concepts loaded for anchoring (digest {ontology_digest[:12]})", flush=True)

    def indexed_sha(base: str) -> str:  # content identity plus the ontology that annotates it
        return hashlib.sha256((base + ontology_digest).encode("utf-8")).hexdigest() if ontology_digest else base
    if owner_roots is not None:
        active_paths |= {canonical for _, canonical, _, _ in federated}
    else:  # not a federated run: keep whatever federated rows exist instead of purging them
        active_paths |= {p for p in db.get_indexed_file_hashes(model_name=model_name) if "@" in p}
    total_files += len(federated)

    # 1. Clean up deleted/renamed documents
    stale_count = db.remove_stale_documents(active_paths, model_name=model_name)
    if stale_count:
        print(f"[INDEXER] Removed {stale_count} stale documents from vector store.")

    # 2. Get existing hashes for incremental skip
    # Online: pseudo placeholders do not count as indexed, so they get upgraded to real vectors.
    existing_hashes = {} if force_reindex else db.get_indexed_file_hashes(model_name=model_name, include_pseudo=not server_online)

    # 3. Identify modified/new files
    files_to_index = []
    for f in all_files:
        rel_path = str(f.relative_to(root_dir)).replace("\\", "/")
        content = f.read_text(encoding="utf-8", errors="ignore")
        sha = indexed_sha(hashlib.sha256(content.encode("utf-8")).hexdigest())
        if rel_path not in existing_hashes or existing_hashes[rel_path] != sha:
            files_to_index.append((f.stem, rel_path, content, sha))
    for doc_id, canonical, content, sha in federated:
        sha = indexed_sha(sha)
        if canonical not in existing_hashes or existing_hashes[canonical] != sha:
            files_to_index.append((doc_id, canonical, content, sha))

    skipped = total_files - len(files_to_index)
    print(f"[INDEXER] Starting incremental vector indexing. Server online: {server_online} (Mode: {'DENSE NEURAL (RTX 3090)' if server_online else 'PSEUDO-HASH'})")
    print(f"[INDEXER] Total: {total_files} docs | Unchanged (Skipped): {skipped} | Need Vectorizing: {len(files_to_index)}")

    if not files_to_index:
        print(f"✅ [INDEXER COMPLETE] All {total_files} documents are already up to date in '{db.db_path}'! (0 embeddings computed)", flush=True)
        return 0

    total_indexed_chunks = 0

    def store(group: List[Tuple[int, str, str, str, List[str], List[Dict[str, Any]]]]) -> int:
        """One embeddings call for every chunk of the group, then one atomic upsert per document."""
        flat = [chunk for _, _, _, _, chunks, _ in group for chunk in chunks]
        embs_all = client.generate_embeddings(flat) if server_online else [None] * len(flat)
        stored, offset = 0, 0
        for idx, doc_id, rel_path, sha, chunks, anchored in group:
            embs, offset = embs_all[offset:offset + len(chunks)], offset + len(chunks)
            prov = "real"
            if not server_online or any(e is None for e in embs):  # server rejected input: keep it upgradeable
                if server_online:
                    print(f"  [EMBED] server rejected chunks of '{rel_path}'; stored as pseudo", flush=True)
                embs, prov = [None] * len(chunks), "pseudo"
            try:
                doc_chunk_tuples = []
                for c_idx, (chunk, emb) in enumerate(zip(chunks, embs)):
                    if emb is None:
                        digest = hashlib.sha256(chunk.encode("utf-8")).digest()
                        emb = [float(b) / 255.0 for b in digest]
                    doc_chunk_tuples.append((c_idx, chunk, sha, emb))
                db.upsert_document_chunks(
                    doc_id=doc_id,
                    relative_path=rel_path,
                    chunks=doc_chunk_tuples,
                    provenance=prov,
                    model_name=model_name,
                    concepts=[c["id"] for c in anchored],
                )
                stored += len(doc_chunk_tuples)
                tags = f", conceitos: {', '.join(c['id'] for c in anchored)}" if anchored else ""
                print(f"  [EMBED {idx}/{len(files_to_index)}] Ingerido: {rel_path} ({len(chunks)} chunks{tags})", flush=True)
            except Exception as e:
                print(f"  Error indexing '{rel_path}': {e}", flush=True)
        return stored

    group: List[Tuple[int, str, str, str, List[str], List[Dict[str, Any]]]] = []
    pending = 0
    for idx, (doc_id, rel_path, content, sha) in enumerate(files_to_index, 1):
        anchored = anchor_concepts(content, doc_id, concepts, repository=document_repository(rel_path))
        header = " | ".join(h for h in (document_header(doc_id, rel_path, content), concept_header(anchored)) if h)
        chunks = chunk_markdown(content, header=header)
        if not chunks:
            continue
        group.append((idx, doc_id, rel_path, sha, chunks, anchored))
        pending += len(chunks)
        if pending >= EMBED_GROUP_CHUNKS:
            total_indexed_chunks += store(group)
            group, pending = [], 0
    if group:
        total_indexed_chunks += store(group)

    print(f"✅ [INDEXER COMPLETE] Incrementally indexed {total_indexed_chunks} new/updated chunks into '{db.db_path}' (Total in DB: {db.count_chunks()})", flush=True)
    return total_indexed_chunks


def main() -> int:
    parser = argparse.ArgumentParser(description="Zero-Cost Vector Indexer for tare.tools.library")
    parser.add_argument("--root", default=".", help="Root directory")
    parser.add_argument("--query", "-q", help="Search vector database with query string")
    parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of results")
    parser.add_argument("--model", default=DEFAULT_NAMESPACE, help="Vector namespace (model family)")
    parser.add_argument("--force-local", action="store_true", help="Force execution on thin client despite ADR-053")
    parser.add_argument("--reindex-all", action="store_true", help="Force reindexing all files, bypassing incremental cache")
    parser.add_argument("--federated", action="store_true",
                        help="Also index documents owned by other repositories (catalog federated index), read from sibling checkouts")
    parser.add_argument("--owner-root", action="append", default=[], metavar="REPO=PATH",
                        help="Override the checkout of an owner repository (default: <library root parent>/<repo>)")
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
            q_emb = client.generate_embeddings([args.query], is_query=True)[0]
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

    owner_roots = None
    if args.federated:
        from tools.federated_documents import load_federated_index
        payload = load_federated_index(root_path, require_retired_absent=False) or {"repositories": []}
        owner_roots = {r["repository"]: root_path.parent / r["repository"] for r in payload["repositories"]}
        owner_roots.update({k: Path(v) for k, v in (item.split("=", 1) for item in args.owner_root)})
    indexed = index_corpus(
        root_path,
        client,
        db,
        model_name=args.model,
        force_reindex=args.reindex_all,
        include_history=args.include_history,
        owner_roots=owner_roots,
    )
    return 0 if indexed >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
