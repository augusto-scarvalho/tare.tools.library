"""Fast Query & Retrieval Engine for tare.tools.library.

Provides instant CLI and programmatic lookups of ADRs, OpenSDD Specifications,
Acceptance Criteria (AC), and Empirical Benchmarks with token-efficient output envelopes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parents[1]


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
    root = Path(root_dir)
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
    for spec_file in spec_dir.rglob("*.md"):
        if clean_id in spec_file.stem.upper():
            return spec_file.read_text(encoding="utf-8", errors="ignore")
    return None


def search_library(
    query: str,
    max_results: int = 5,
    filter_type: Optional[str] = None,
    root_dir: str | Path = ROOT,
) -> List[QueryResult]:
    """Perform keyword and regex search across active docs, ranking results by relevance."""
    root = Path(root_dir)
    query_terms = [t.lower() for t in query.split() if len(t) > 2]
    results: List[QueryResult] = []

    target_dirs = [root / "docs", root / "specs", root / "experiments"]
    for base_dir in target_dirs:
        if not base_dir.exists():
            continue
        for file_path in base_dir.rglob("*.md"):
            if file_path.name.upper() == "README.MD" or ".git" in file_path.parts:
                continue

            # Determine doc type
            rel = str(file_path.relative_to(root)).replace("\\", "/")
            if "docs/adr" in rel:
                dtype = "adr"
            elif "specs" in rel:
                dtype = "spec"
            elif "experiments" in rel:
                dtype = "experiment"
            elif "post-mortems" in rel:
                dtype = "post_mortem"
            else:
                dtype = "doc"

            if filter_type and dtype != filter_type.lower():
                continue

            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                text_lower = text.lower()

                # Score matching terms
                score = 0.0
                title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
                title = title_match.group(1).strip() if title_match else file_path.stem

                # Title match weighting
                for t in query_terms:
                    if t in title.lower():
                        score += 10.0
                    if t in text_lower:
                        score += text_lower.count(t) * 1.0

                if score > 0.0:
                    # Extract best matching paragraph for context envelope
                    paragraphs = text.split("\n\n")
                    best_para = paragraphs[0]
                    best_para_score = 0
                    for p in paragraphs:
                        p_lower = p.lower()
                        p_score = sum(p_lower.count(t) for t in query_terms)
                        if p_score > best_para_score:
                            best_para_score = p_score
                            best_para = p.strip()

                    # Truncate snippet to 300 chars
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


def lookup_concept(concept_name: str, root_dir: str | Path = ROOT) -> Optional[Dict[str, Any]]:
    """Lookup architectural concept in ontology/domain_ontology.yaml."""
    root = Path(root_dir)
    onto_path = root / "ontology" / "domain_ontology.yaml"
    if not onto_path.exists():
        return None

    raw_text = onto_path.read_text(encoding="utf-8", errors="ignore")
    # Quick simple parser for YAML concepts
    clean_target = concept_name.lower().replace("-", "").replace("_", "").replace(" ", "")
    
    # Split into concept blocks
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
    parser.add_argument("--search", "-s", help="Free-form query string")
    parser.add_argument("--adr", help="Fetch specific ADR by ID (e.g. 'ADR-051')")
    parser.add_argument("--spec", help="Fetch specific SPEC by ID (e.g. 'SPEC-KERNEL-001')")
    parser.add_argument("--concept", "-c", help="Lookup architectural concept in domain ontology")
    parser.add_argument("--type", "-t", choices=["adr", "spec", "experiment", "post_mortem", "doc"], help="Filter by document type")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Max results to return")
    parser.add_argument("--root", default=".", help="Root directory of the library")

    args = parser.parse_args()

    if args.concept:
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
        results = search_library(args.search, max_results=args.limit, filter_type=args.type, root_dir=args.root)
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
