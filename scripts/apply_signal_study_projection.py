#!/usr/bin/env python3
"""Apply SIGNAL styling to generated bridge-edition HTML without mutating Git sources.

The source HTML under bridge-editions/ remains byte-preserved. This script only
modifies files inside the generated _site tree after Jekyll has copied them.
"""
from __future__ import annotations

from pathlib import Path
import os

SITE = Path("_site")
BRIDGES = SITE / "bridge-editions"
STYLESHEET = SITE / "assets" / "signal-study.css"
MARKER = 'data-signal-projection="true"'


def project(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        return False
    if "</head>" not in text or "<html" not in text:
        raise RuntimeError(f"unexpected HTML structure: {path}")
    rel_css = os.path.relpath(STYLESHEET, path.parent).replace(os.sep, "/")
    text = text.replace("<html", f'<html {MARKER}', 1)
    text = text.replace("</head>", f'<link rel="stylesheet" href="{rel_css}"></head>', 1)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    if not STYLESHEET.is_file():
        raise SystemExit(f"missing projection stylesheet: {STYLESHEET}")
    if not BRIDGES.is_dir():
        raise SystemExit(f"missing generated bridge directory: {BRIDGES}")
    files = sorted(BRIDGES.rglob("*.html"))
    if not files:
        raise SystemExit("no generated bridge HTML files found")
    changed = sum(project(path) for path in files)
    print(f"SIGNAL study projection: {changed}/{len(files)} HTML files themed")


if __name__ == "__main__":
    main()
