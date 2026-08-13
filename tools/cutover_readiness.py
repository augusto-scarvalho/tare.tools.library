#!/usr/bin/env python3
"""Deterministic migration-readiness evidence for the Pages shadow pipeline.

This file produces evidence only. It never grants production authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from pages_common import normalize_base_path, sha256_file
from validate_pages_contract import validate as validate_pages_contract

RECORD_VERSION = "1.0"
DEFAULT_CANARY_ID = "research.pages.canary.v1"


def _canonical_digest(rows: list[dict[str, str]]) -> str:
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _inventory(root: Path) -> dict[str, Any]:
    rows = [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}
        for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix())
        if path.is_file()
    ]
    return {"file_count": len(rows), "digest": _canonical_digest(rows), "files": rows}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--site", type=Path, required=True)
    ap.add_argument("--incumbent", type=Path, required=True)
    ap.add_argument("--base-path", default="/tare.tools.research/")
    ap.add_argument("--candidate-sha", required=True)
    ap.add_argument("--canary-id", default=DEFAULT_CANARY_ID)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    base_path = normalize_base_path(args.base_path)
    errors = validate_pages_contract(args.site, args.root, args.incumbent, base_path)
    receipt = {
        "record_version": RECORD_VERSION,
        "record_kind": "pages-cutover-readiness-evidence",
        "candidate_commit": args.candidate_sha,
        "incumbent_inventory": _inventory(args.incumbent.resolve()),
        "safeguards_status": "PASS" if not errors else "FAIL",
        "production_effect_performed": False,
        "cutover_authorized": False,
        "integrity_errors": errors,
    }
    target = args.output or args.site / "publication-meta" / "CUTOVER_READINESS.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
