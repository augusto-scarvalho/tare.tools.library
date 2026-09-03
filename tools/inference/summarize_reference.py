"""Reference Summarizer & Ontology Extractor for tare.tools.library.

Uses local LLM inference (Qwen 2.5/3.x 32B on node aaaaa) to analyze papers, ADRs,
and reference documents, generating executive summaries and ontology cross-links with zero cloud spend.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig


def load_ontology_keywords(root_dir: Path = ROOT) -> List[str]:
    """Read concept IDs from owner pointers without copying ontology payloads."""
    from tools.federated_ontologies import load_federated_ontologies

    try:
        payload = load_federated_ontologies(root_dir)
    except (OSError, ValueError, json.JSONDecodeError):
        return []
    return [
        concept_id
        for ontology in payload["ontologies"]
        for concept_id in ontology["concept_ids"]
    ]


def summarize_document(
    file_path: Path,
    client: Optional[LocalInferenceClient] = None,
    ontology_concepts: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Extract summary, key architectural insights and ontology tags using local LLM."""
    client = client or LocalInferenceClient()
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    concepts = ontology_concepts or load_ontology_keywords()

    # Truncate content to first 12,000 chars (~3,000 tokens) for prompt envelope
    truncated_content = content[:12000]

    system_prompt = (
        "You are an expert software and AI systems architect analyzing research papers and engineering specifications.\n"
        "Analyze the provided document and produce a strict JSON object with these exact keys:\n"
        "{\n"
        '  "title": "<document title>",\n'
        '  "executive_summary": "<2-3 sentence technical summary>",\n'
        '  "key_findings": ["<finding 1>", "<finding 2>", "<finding 3>"],\n'
        '  "matched_concepts": ["<concept_id from ontology if relevant>"],\n'
        '  "suggested_tags": ["<tag1>", "<tag2>"]\n'
        "}\n"
        "Return ONLY the JSON object, with no markdown fences or preambles."
    )

    user_prompt = (
        f"=== AVAILABLE ONTOLOGY CONCEPTS ===\n{json.dumps(concepts[:50])}\n\n"
        f"=== DOCUMENT: {file_path.name} ===\n{truncated_content}\n\n"
        "=== EXTRACTED ARCHITECTURAL SUMMARY JSON ==="
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    try:
        response_text = client.chat_completion(messages, max_tokens=1024, temperature=0.1)
        # Parse JSON
        clean_text = response_text.strip()
        if clean_text.startswith("```"):
            clean_text = clean_text.split("```")[1]
            if clean_text.startswith("json"):
                clean_text = clean_text[4:]
        data = json.loads(clean_text)
        data["file"] = str(file_path.name)
        return data
    except Exception as e:
        return {
            "file": str(file_path.name),
            "title": file_path.stem,
            "executive_summary": f"Extraction failed or server offline: {e}",
            "key_findings": [],
            "matched_concepts": [],
            "suggested_tags": [],
            "error": str(e),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize references using local LLM")
    parser.add_argument("file", help="Path to markdown document to summarize")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--endpoint", help="Custom local LLM endpoint (e.g. http://100.107.245.30:8080)")

    args = parser.parse_args()
    target_path = Path(args.file)
    if not target_path.exists():
        print(f"[ERROR] File '{args.file}' not found.")
        return 1

    cfg = LocalInferenceConfig()
    if args.endpoint:
        cfg.host = args.endpoint.rstrip("/")
    client = LocalInferenceClient(cfg)

    print(f"[*] Analyzing document '{target_path.name}' via Local LLM ({client.config.host})...\n")
    res = summarize_document(target_path, client=client)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0

    print("=" * 70)
    print(f"📄 Título: {res.get('title', target_path.stem)}")
    print("=" * 70)
    print(f"\n📌 Resumo Executivo:\n{res.get('executive_summary', 'N/A')}\n")
    print("🎯 Principais Achados / Insights:")
    for kf in res.get("key_findings", []):
        print(f"  • {kf}")
    print("\n🏷️ Conceitos Ontológicos Identificados:")
    for mc in res.get("matched_concepts", []):
        print(f"  • {mc}")
    print("\n🏷️ Tags Sugeridas:")
    print(f"  {', '.join(res.get('suggested_tags', []))}")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
