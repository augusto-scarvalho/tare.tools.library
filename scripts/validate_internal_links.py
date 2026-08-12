#!/usr/bin/env python3
"""Validate repository-relative Markdown links without deciding document semantics."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', '_site', 'vendor'}
LINK_RE = re.compile(r'(?<!!)\[[^\]]*\]\(([^)]+)\)')
FENCE_RE = re.compile(r'^\s*```')


def markdown_files():
    for path in ROOT.rglob('*.md'):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def strip_fenced_code(text: str) -> str:
    out = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return '\n'.join(out)


def normalize_target(raw: str) -> str | None:
    raw = raw.strip()
    if raw.startswith('<') and raw.endswith('>'):
        raw = raw[1:-1]
    if not raw or raw.startswith('#'):
        return None
    if ' "' in raw or " '" in raw:
        raw = raw.split(' ', 1)[0]
    parts = urlsplit(raw)
    if parts.scheme or parts.netloc:
        return None
    path = unquote(parts.path)
    return path or None


def resolves(source: Path, target: str) -> bool:
    if target.startswith('/'):
        candidate = ROOT / target.lstrip('/')
    else:
        candidate = source.parent / target
    candidate = candidate.resolve()
    try:
        candidate.relative_to(ROOT.resolve())
    except ValueError:
        return False
    if candidate.exists():
        return True
    # Directory index convention used throughout the repo.
    if candidate.suffix == '' and (candidate / 'README.md').exists():
        return True
    return False


def main() -> int:
    missing: list[tuple[str, str]] = []
    checked = 0
    for source in markdown_files():
        text = strip_fenced_code(source.read_text(encoding='utf-8'))
        for match in LINK_RE.finditer(text):
            target = normalize_target(match.group(1))
            if target is None:
                continue
            checked += 1
            if not resolves(source, target):
                missing.append((str(source.relative_to(ROOT)), target))
    print(f'Checked {checked} repository-relative Markdown links.')
    if missing:
        print('Broken internal links:')
        for source, target in missing:
            print(f'  {source} -> {target}')
        return 1
    print('Internal link validation: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
