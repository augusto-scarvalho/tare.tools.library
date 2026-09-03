"""Fast Query & Retrieval Engine for tare.tools.library.

Provides instant CLI and programmatic lookups of ADRs, OpenSDD Specifications,
Acceptance Criteria (AC), and Empirical Benchmarks with token-efficient output envelopes.
Supports Lexical Keyword Search, Dense Semantic Vector Search, and Local RAG Synthesis via LLM.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig
from tools.document_scope import collect_indexable_markdown


@dataclass
class QueryResult:
    doc_id: str
    doc_type: str
    title: str
    relative_path: str
    snippet: str
    score: float


def get_adr(adr_id: str, root_dir: str | Path = ROOT) -> Optional[str]:
    """Retrieve full text of an ADR by ID (e.g. 'ADR-051' or '051')."""
    root = Path(root_dir).resolve()
    adr_dir = root / "docs" / "adr"
    if not adr_dir.exists():
        return None

    clean_id = adr_id.upper().strip()
    if not clean_id.startswith("ADR-"):
        clean_id = f"ADR-{clean_id.zfill(3)}"

    for adr_file in adr_dir.glob("*.md"):
        if clean_id in adr_file.stem.upper():
            return adr_file.read_text(encoding="utf-8", errors="ignore")
    return None


def get_spec(spec_id: str, root_dir: str | Path = ROOT) -> Optional[str]:
    """Retrieve full text of a SPEC by ID (e.g. 'SPEC-KERNEL-001')."""
    root = Path(root_dir)
    spec_dir = root / "specs"
    if not spec_dir.exists():
        return None

    clean_id = spec_id.upper().strip()
    for spec_file in spec_dir.glob("*.md"):
        if clean_id in spec_file.stem.upper():
            return spec_file.read_text(encoding="utf-8", errors="ignore")
    return None


def search_library(
    query: str,
    max_results: int = 5,
    filter_type: Optional[str] = None,
    root_dir: str | Path = ROOT,
    include_history: bool = False,
) -> List[QueryResult]:
    """Search the active Library corpus; immutable history is opt-in."""
    root = Path(root_dir).resolve()
    query_terms = [t.lower() for t in query.split() if len(t) > 2]
    if not query_terms:
        query_terms = [query.lower()]

    results: List[QueryResult] = []
    for file_path in collect_indexable_markdown(
        root, include_history=include_history, deduplicate=True
    ):
        rel = str(file_path.relative_to(root)).replace("\\", "/")
        if rel.startswith("docs/adr/"):
            dtype = "adr"
        elif rel.startswith("specs/"):
            dtype = "spec"
        elif rel.startswith("experiments/"):
            dtype = "experiment"
        elif rel.startswith("findings/post-mortems/") or rel.startswith(
            "docs/post-mortems/"
        ):
            dtype = "post_mortem"
        elif include_history and rel.startswith(("docs/archive/", "catalog/corpus/")):
            dtype = "history"
        else:
            dtype = "doc"
        if filter_type and dtype != filter_type:
            continue

        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            text_lower = text.lower()

            # Calculate score based on term matches
            score = 0.0
            for t in query_terms:
                score += text_lower.count(t) * 1.0

            if score > 0:
                # Extract title
                title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
                title = title_match.group(1).strip() if title_match else file_path.stem

                # Extract best matching paragraph
                paragraphs = text.split("\n\n")
                best_para = paragraphs[0]
                best_para_score = 0
                for paragraph in paragraphs:
                    paragraph_lower = paragraph.lower()
                    paragraph_score = sum(
                        paragraph_lower.count(term) for term in query_terms
                    )
                    if paragraph_score > best_para_score:
                        best_para_score = paragraph_score
                        best_para = paragraph.strip()

                snippet = best_para[:400] + ("..." if len(best_para) > 400 else "")

                results.append(
                    QueryResult(
                        doc_id=file_path.stem,
                        doc_type=dtype,
                        title=title,
                        relative_path=rel,
                        snippet=snippet,
                        score=score,
                    )
                )
        except Exception:
            continue

    results.sort(key=lambda r: r.score, reverse=True)
    return results[:max_results]


def semantic_search_library(
    query: str,
    max_results: int = 5,
    client: Optional[LocalInferenceClient] = None,
    root_dir: str | Path = ROOT,
) -> List[QueryResult]:
    """Dense vector semantic search using SQLite LibraryVectorDB and local embedding endpoint."""
    from tools.indexer.embed_corpus import LibraryVectorDB

    root = Path(root_dir)
    db_path = root / "catalog" / "library_vectors.db"
    if not db_path.exists():
        # Fallback to lexical if vector DB has not been materialized yet
        return search_library(query, max_results=max_results, root_dir=root_dir)

    db = LibraryVectorDB(db_path)
    client = client or LocalInferenceClient()

    # Generate query embedding via dedicated embedding host
    try:
        if client.health_check(target="embed").get("online"):
            embs = client.generate_embeddings([query])
            if embs:
                vec_results = db.search(embs[0], top_k=max_results, provenance="real", model_name="local-embed")
                if not vec_results:
                    vec_results = db.search(embs[0], top_k=max_results, allow_any_namespace=True)
                if vec_results:
                    return [
                        QueryResult(
                            doc_id=vr.doc_id,
                            doc_type="vector_semantic",
                            title=vr.relative_path,
                            relative_path=vr.relative_path,
                            snippet=vr.text_snippet,
                            score=vr.score,
                        )
                        for vr in vec_results
                    ]
    except Exception as e:
        sys.stderr.write(f"[WARN] Semantic vector search unavailable ({e}). Falling back to lexical keyword search.\n")

    # Explicit Fallback to keyword search with tagged doc_type
    lexical_results = search_library(query, max_results=max_results, root_dir=root_dir)
    return [
        QueryResult(
            doc_id=lr.doc_id,
            doc_type="lexical_fallback",
            title=lr.title,
            relative_path=lr.relative_path,
            snippet=lr.snippet,
            score=lr.score,
        )
        for lr in lexical_results
    ]


def ask_library(
    question: str,
    max_context_chunks: int = 3,
    client: Optional[LocalInferenceClient] = None,
    root_dir: str | Path = ROOT,
) -> Dict[str, Any]:
    """Full RAG pipeline: retrieves relevant context and synthesizes an answer via Local LLM."""
    client = client or LocalInferenceClient()
    
    # 1. Retrieve most relevant context chunks
    matches = semantic_search_library(question, max_results=max_context_chunks, client=client, root_dir=root_dir)
    
    if not matches:
        return {
            "answer": "No relevant documents found in the library to answer this question.",
            "sources": [],
        }

    context_str = "\n\n---\n\n".join(
        f"Source: {m.relative_path}\nExcerpt: {m.snippet}" for m in matches
    )

    prompt = (
        f"You are the architectural intelligence assistant for tare.tools.library.\n"
        f"Answer the user question accurately and concisely, citing specific ADRs, SPECs, or sources.\n\n"
        f"=== CONTEXT FROM LIBRARY ===\n{context_str}\n\n"
        f"=== USER QUESTION ===\n{question}\n\n"
        f"=== ANSWER ==="
    )

    messages = [
        {"role": "system", "content": "You are a precise technical architecture assistant."},
        {"role": "user", "content": prompt},
    ]

    try:
        if client.health_check().get("online"):
            answer = client.chat_completion(messages, max_tokens=1024, temperature=0.1)
        else:
            answer = (
                f"[OFFLINE SYNTHESIS - Server Offline]\n\n"
                f"Most relevant excerpts found in the library:\n\n{context_str}"
            )
    except Exception as e:
        answer = f"[ERROR querying local LLM]: {e}\n\nRelevant excerpts:\n{context_str}"

    return {
        "answer": answer,
        "sources": [m.relative_path for m in matches],
        "matches": matches,
    }


def lookup_concept(concept_name: str, root_dir: str | Path = ROOT) -> Optional[Dict[str, Any]]:
    """Lookup architectural concept in catalog/ontology/domain_ontology.yaml."""
    root = Path(root_dir)
    onto_path = root / "catalog/ontology" / "domain_ontology.yaml"
    if not onto_path.exists():
        return None

    raw_text = onto_path.read_text(encoding="utf-8", errors="ignore")
    clean_target = concept_name.lower().replace("-", "").replace("_", "").replace(" ", "")

    blocks = raw_text.split("- id:")
    for b in blocks[1:]:
        lines = b.splitlines()
        first_line = lines[0].strip().strip('"').strip("'")
        clean_id = first_line.lower().replace("-", "").replace("_", "").replace(" ", "")
        if clean_target in clean_id or clean_id in clean_target:
            return {"id": first_line, "raw": "- id:" + b}
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Query CLI for tare.tools.library")
    parser.add_argument("--search", "-s", help="Free-form lexical keyword search")
    parser.add_argument("--semantic", "-v", help="Dense semantic vector search across embeddings")
    parser.add_argument("--ask", "-a", help="Ask a question to the library with local LLM RAG synthesis")
    parser.add_argument("--adr", help="Fetch specific ADR by ID (e.g. 'ADR-051')")
    parser.add_argument("--spec", help="Fetch specific SPEC by ID (e.g. 'SPEC-KERNEL-001')")
    parser.add_argument("--concept", "-c", help="Lookup architectural concept in domain ontology")
    parser.add_argument("--type", "-t", choices=["adr", "spec", "experiment", "post_mortem", "doc", "canonical"], help="Filter by document type")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Max results to return")
    parser.add_argument("--force-local", action="store_true", help="Force local query execution")
    parser.add_argument(
        "--include-history",
        action="store_true",
        help="Include immutable archive/snapshot documents in lexical search",
    )
    parser.add_argument("--root", default=".", help="Root directory of the library")

    args = parser.parse_args()

    # ADR-055: Adaptive Latency-Aware Query Routing on Thin Clients
    if args.semantic and not args.force_local:
        try:
            from tools.mesh.router import LatencyAwareRouter
            from tools.policy.compute_guard import is_thin_client

            if is_thin_client():
                router = LatencyAwareRouter()
                rtt = router.probe_substrate_latency()
                if rtt is not None and rtt <= router.latency_threshold_ms:
                    route_res = router.route_query(args.semantic, top_k=args.limit)
                    print(f"🛰️ [QUERY ROUTED VIA {route_res.route}] Latency: {route_res.latency_ms} ms (Execution: {route_res.execution_time_s}s)")
                    for res in route_res.results:
                        print(res.get("raw_output", ""))
                    return 0
        except ImportError:
            pass

    if args.ask:
        print(f"[*] Querying tare.tools.library RAG with question: '{args.ask}'...\n")
        rag_res = ask_library(args.ask, max_context_chunks=args.limit, root_dir=args.root)
        print("=" * 70)
        print(rag_res["answer"])
        print("=" * 70)
        print("\n📚 Fontes Consultadas:")
        for s in rag_res["sources"]:
            print(f"  • {s}")
        return 0

    elif args.semantic:
        results = semantic_search_library(args.semantic, max_results=args.limit, root_dir=args.root)
        if not results:
            print(f"[QUERY] No matching records found for '{args.semantic}'.")
            return 0

        is_fallback = any(r.doc_type == "lexical_fallback" for r in results)
        header = "⚠️ [FALLBACK: LEXICAL KEYWORD SEARCH (Embedding Endpoint Offline)]" if is_fallback else "✨ [SEMANTIC DENSE VECTOR SEARCH (Cosine Similarity)]"
        print(f"{header} Found {len(results)} matches for '{args.semantic}':\n")
        for i, r in enumerate(results, 1):
            score_label = f"Term Matches: {r.score:.1f}" if is_fallback else f"Cosine Score: {r.score:.3f}"
            print(f"{i}. [{r.doc_type.upper()}] {r.title} ({r.relative_path}) [{score_label}]")
            print(f"   Excerpt: {r.snippet}\n")
        return 0

    elif args.concept:
        res = lookup_concept(args.concept, args.root)
        if res:
            print(f"[FOUND CONCEPT: {res['id']}]\n")
            print(res["raw"].strip())
            return 0
        else:
            print(f"[ERROR] Concept '{args.concept}' not found in domain ontology.")
            return 1

    elif args.adr:
        content = get_adr(args.adr, args.root)
        if content:
            print(f"[FOUND ADR: {args.adr}]\n")
            print(content)
            return 0
        else:
            print(f"[ERROR] ADR '{args.adr}' not found.")
            return 1

    elif args.spec:
        content = get_spec(args.spec, args.root)
        if content:
            print(f"[FOUND SPEC: {args.spec}]\n")
            print(content)
            return 0
        else:
            print(f"[ERROR] SPEC '{args.spec}' not found.")
            return 1

    elif args.search:
        results = search_library(
            args.search,
            max_results=args.limit,
            filter_type=args.type,
            root_dir=args.root,
            include_history=args.include_history,
        )
        if not results:
            print(f"[QUERY] No matching records found for '{args.search}'.")
            return 0

        print(f"[QUERY RESULTS] Found {len(results)} matches for '{args.search}':\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. [{r.doc_type.upper()}] {r.title} ({r.relative_path}) [Score: {r.score:.1f}]")
            print(f"   Excerpt: {r.snippet}\n")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
