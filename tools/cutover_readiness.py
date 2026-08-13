#!/usr/bin/env python3
"""Derive Pages migration readiness without granting production authority.

The receipt composes existing projection/parity/editorial evidence.  It is a
local migration artifact, not a new tare.tools kernel primitive.  Open rollout
conditions are recorded without weakening integrity gates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from cutover_readiness_support import canary_evidence, rollback_evidence, workflow_ownership
from pages_common import normalize_base_path
from validate_pages_contract import validate as validate_pages_contract

RECORD_VERSION = "1.0"
DEFAULT_CANARY_ID = "research.pages.canary.v1"


def generate(
    root: Path,
    output: Path,
    incumbent: Path,
    *,
    base_path: str,
    candidate_sha: str,
    canary_id: str = DEFAULT_CANARY_ID,
) -> tuple[dict[str, Any], list[str]]:
    root = root.resolve()
    output = output.resolve()
    incumbent = incumbent.resolve()
    base_path = normalize_base_path(base_path)

    contract_errors = validate_pages_contract(output, root, incumbent, base_path)
    errors = list(contract_errors)
    profile_path = root / "site" / "INCUMBENT_PROFILE.json"
    parity_path = output / "publication-meta" / "PARITY_REPORT.json"

    profile: dict[str, Any] = {}
    parity: dict[str, Any] = {}
    if not profile_path.is_file():
        errors.append("missing site/INCUMBENT_PROFILE.json")
    else:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if not parity_path.is_file():
        errors.append("missing publication-meta/PARITY_REPORT.json")
    else:
        parity = json.loads(parity_path.read_text(encoding="utf-8"))

    rollback = rollback_evidence(incumbent, profile, parity)
    expected_count = profile.get("expected_materialized_file_count")
    expected_digest = profile.get("expected_materialized_inventory_digest")
    actual_inventory = rollback.get("materialized_incumbent", {})
    baseline_match = bool(
        isinstance(expected_count, int)
        and isinstance(expected_digest, str)
        and actual_inventory.get("file_count") == expected_count
        and actual_inventory.get("digest") == expected_digest
    )
    rollback["audited_baseline"] = {
        "expected_file_count": expected_count,
        "expected_inventory_digest": expected_digest,
        "match": baseline_match,
    }
    if not baseline_match:
        rollback["rollback_ready"] = False
        rollback["status"] = "FAIL"
        errors.append("materialized incumbent does not match audited baseline digest")
    if not rollback["rollback_ready"]:
        errors.append("incumbent rollback drill is not ready")

    ownership = workflow_ownership(root, profile.get("deploy_owner"))
    if ownership["candidate_deploy_capable"]:
        errors.append("shadow candidate unexpectedly has Pages deploy capability")
    if ownership["dual_owner"]:
        errors.append("dual Pages deploy owners detected")

    canary = canary_evidence(root, output, canary_id)
    open_conditions: list[str] = []
    if canary.get("status") != "PROJECTED_APPROVED":
        open_conditions.append(f"CANARY_{canary.get('status', 'UNKNOWN')}")
    open_conditions.append("VISUAL_VALIDATION_NOT_RUN")
    open_conditions.append("OWNER_CUTOVER_AUTHORITY_NOT_GRANTED")

    safeguards_pass = not errors
    technical_ready = safeguards_pass and canary.get("status") == "PROJECTED_APPROVED" and not any(
        item == "VISUAL_VALIDATION_NOT_RUN" for item in open_conditions
    )
    receipt = {
        "record_version": RECORD_VERSION,
        "record_kind": "pages-cutover-readiness-evidence",
        "authority_note": "migration evidence only; not a kernel authority primitive",
        "repository": "augusto-scarvalho/tare.tools.research",
        "candidate_commit": candidate_sha,
        "incumbent_commit": profile.get("source_ref"),
        "base_path": base_path,
        "pages_contract_validation": {
            "status": "PASS" if not contract_errors else "FAIL",
            "errors": contract_errors,
        },
        "incumbent_parity": parity,
        "rollback_drill": rollback,
        "deploy_ownership": ownership,
        "canary": canary,
        "visual_validation": {
            "status": "NOT_RUN",
            "note": "browser/render evidence remains an explicit pre-cutover gate",
        },
        "safeguards_status": "PASS" if safeguards_pass else "FAIL",
        "technical_readiness": "READY" if technical_ready else "BLOCKED",
        "production_effect_performed": False,
        "cutover_authorized": False,
        "open_conditions": open_conditions,
        "integrity_errors": errors,
    }
    return receipt, errors


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

    receipt, errors = generate(
        args.root,
        args.site,
        args.incumbent,
        base_path=args.base_path,
        candidate_sha=args.candidate_sha,
        canary_id=args.canary_id,
    )
    target = args.output or args.site / "publication-meta" / "CUTOVER_READINESS.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"{'PASS' if not errors else 'FAIL'} cutover-readiness safeguards; "
        f"technical={receipt['technical_readiness']}; authority=false"
    )
    for blocker in receipt["open_conditions"]:
        print(f"OPEN {blocker}")
    for error in errors:
        print(f"ERROR {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
