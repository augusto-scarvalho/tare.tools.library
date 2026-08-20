"""Local Neural Translation Engine for tare.tools.library.

Translates English architectural references, papers, and specs to Brazilian Portuguese (pt-BR)
using local LLM inference (Qwen 2.5/3.x 32B on node aaaaa) with zero cloud spend.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.inference.local_client import LocalInferenceClient, LocalInferenceConfig


def translate_markdown(
    content: str,
    client: Optional[LocalInferenceClient] = None,
    target_lang: str = "pt-BR",
) -> str:
    """Translate technical markdown content preserving code blocks, equations and frontmatter."""
    client = client or LocalInferenceClient()

    system_prompt = (
        "You are an expert technical translator specializing in computer science, software architecture, and distributed systems.\n"
        "Translate the provided Markdown document into natural, idiomatic Brazilian Portuguese (pt-BR).\n"
        "STRICT INVARIANTS:\n"
        "1. Preserve all Markdown structure, headers (#, ##), bullets, bold, and italics exactly.\n"
        "2. Do NOT translate code blocks (```...```) or inline code (`...`) unless it is a comment inside code.\n"
        "3. Preserve technical terms where appropriate in standard Brazilian computing vernacular (e.g. 'worktree', 'pipeline', 'hash', 'socket', 'driver', 'lease', 'prefill', 'cache').\n"
        "4. Do NOT add preambles, greetings, or explanations. Output ONLY the translated Markdown."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Translate this document to {target_lang}:\n\n{content}"},
    ]

    try:
        translated = client.chat_completion(messages, max_tokens=4096, temperature=0.2)
        return translated.strip()
    except Exception as e:
        raise RuntimeError(f"Local translation failed: {e}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate technical markdown via local LLM")
    parser.add_argument("file", help="Path to input markdown file to translate")
    parser.add_argument("--output", "-o", help="Optional output file path (default: <file>.pt-BR.md)")
    parser.add_argument("--endpoint", help="Custom local LLM endpoint (e.g. http://100.107.245.30:8080)")

    args = parser.parse_args()
    input_path = Path(args.file)
    if not input_path.exists():
        print(f"[ERROR] Input file '{args.file}' not found.")
        return 1

    cfg = LocalInferenceConfig()
    if args.endpoint:
        cfg.host = args.endpoint.rstrip("/")
    client = LocalInferenceClient(cfg)

    print(f"[*] Reading '{input_path.name}'...")
    content = input_path.read_text(encoding="utf-8", errors="ignore")

    print(f"[*] Translating to pt-BR using local LLM @ {client.config.host}...")
    try:
        translated_text = translate_markdown(content, client=client)
    except Exception as e:
        print(f"[ERROR] {e}")
        return 1

    out_path = Path(args.output) if args.output else input_path.with_name(f"{input_path.stem}.pt-BR.md")
    out_path.write_text(translated_text, encoding="utf-8")
    print(f"✅ Arquivo traduzido salvo com sucesso em: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
