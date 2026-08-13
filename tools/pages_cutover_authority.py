#!/usr/bin/env python3
"""Validate a durable, owner-authored Pages activation record.

Absence is a normal pre-activation state and returns authorized=false. A present
but invalid record fails closed. This is a repository-local migration contract,
not a tare.tools kernel authority primitive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

AUTHORITY_PATH = Path("site/PAGES_CUTOVER_AUTHORITY.json")
PROFILE_PATH = Path("site/INCUMBENT_PROFILE.json")
CANDIDATE_OWNER = ".github/workflows/pages.yml@main"
REPOSITORY = "augusto-scarvalho/tare.tools.research"
CANARY_ID = "research.pages.canary.v1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
CRITICAL_BINDINGS = {
    "owner_workflow_sha256": Path(".github/workflows/pages.yml"),
    "visual_evidence_sha256": Path("site/PAGES_VISUAL_EVIDENCE.json"),
    "build_pages_sha256": Path("tools/build_pages.py"),
    "pages_validator_sha256": Path("tools/validate_pages_contract.py"),
    "readiness_sha256": Path("tools/cutover_readiness.py"),
    "readiness_support_sha256": Path("tools/cutover_readiness_support.py"),
    "authority_validator_sha256": Path("tools/pages_cutover_authority.py"),
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluate(root: Path, mode: str = "candidate") -> tuple[dict[str, Any], list[str]]:
    root = root.resolve()
    if mode not in {"candidate", "rollback"}:
        return {"authorized": False, "mode": mode, "reason": "invalid_mode"}, ["mode must be candidate or rollback"]

    authority_path = root / AUTHORITY_PATH
    if not authority_path.is_file():
        return {
            "authorized": False,
            "mode": mode,
            "reason": "authority_absent",
            "authority_path": AUTHORITY_PATH.as_posix(),
        }, []

    try:
        authority = json.loads(authority_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {"authorized": False, "mode": mode, "reason": "invalid_authority_json"}, [str(exc)]

    errors: list[str] = []
    if authority.get("record_version") != "1.0": errors.append("record_version must be 1.0")
    if authority.get("record_kind") != "pages-cutover-owner-authority": errors.append("record_kind mismatch")
    if authority.get("repository") != REPOSITORY: errors.append("repository mismatch")
    if authority.get("decision") != "authorize-cutover": errors.append("decision must be authorize-cutover")
    if authority.get("canary_id") != CANARY_ID: errors.append("canary_id mismatch")
    if authority.get("candidate_deploy_owner") != CANDIDATE_OWNER: errors.append("candidate_deploy_owner mismatch")
    if not isinstance(authority.get("decision_id"), str) or not authority["decision_id"].strip(): errors.append("decision_id required")
    if not isinstance(authority.get("authorized_at"), str) or not authority["authorized_at"].strip(): errors.append("authorized_at required")
    qualified = authority.get("qualified_owner_commit")
    if not isinstance(qualified, str) or not HEX40.fullmatch(qualified): errors.append("qualified_owner_commit must be 40 lowercase hex")

    owner = authority.get("owner")
    if not isinstance(owner, dict):
        errors.append("owner required")
    else:
        if owner.get("identity_ref") != "github:augusto-scarvalho": errors.append("owner identity_ref mismatch")
        if owner.get("role") != "repository-owner": errors.append("owner role mismatch")

    profile_path = root / PROFILE_PATH
    if not profile_path.is_file():
        errors.append("missing INCUMBENT_PROFILE.json")
        profile: dict[str, Any] = {}
    else:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if profile.get("deploy_owner") is not None: errors.append("legacy deploy_owner must remain null")
    if profile.get("candidate_deploy_owner") != CANDIDATE_OWNER: errors.append("profile candidate_deploy_owner mismatch")
    if profile.get("ownership_state") != "CANDIDATE_ONLY": errors.append("profile ownership_state must be CANDIDATE_ONLY")
    retired = profile.get("retired_deploy_owner")
    if not isinstance(retired, dict) or not retired.get("retired_branch_commit"): errors.append("retired deploy owner evidence required")

    observed: dict[str, str] = {}
    bindings = authority.get("bindings")
    if not isinstance(bindings, dict):
        errors.append("bindings required")
        bindings = {}
    for field, rel in CRITICAL_BINDINGS.items():
        expected = bindings.get(field)
        path = root / rel
        if not path.is_file():
            errors.append(f"missing bound file: {rel.as_posix()}")
            continue
        actual = sha256_file(path)
        observed[field] = actual
        if not isinstance(expected, str) or not HEX64.fullmatch(expected):
            errors.append(f"{field} must be 64 lowercase hex")
        elif expected != actual:
            errors.append(f"binding mismatch: {field}")

    if mode == "rollback" and authority.get("rollback_allowed") is not True:
        errors.append("rollback mode requires rollback_allowed=true")

    result = {
        "authorized": not errors,
        "mode": mode,
        "reason": "authorized" if not errors else "authority_invalid",
        "authority_path": AUTHORITY_PATH.as_posix(),
        "decision_id": authority.get("decision_id"),
        "qualified_owner_commit": qualified,
        "rollback_allowed": authority.get("rollback_allowed") is True,
        "observed_bindings": observed,
    }
    return result, errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--mode", choices=["candidate", "rollback"], default="candidate")
    ap.add_argument("--github-output", type=Path)
    args = ap.parse_args()

    result, errors = evaluate(args.root, args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    for error in errors:
        print(f"ERROR {error}")

    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as fh:
            fh.write(f"authorized={'true' if result['authorized'] else 'false'}\n")
            fh.write(f"mode={args.mode}\n")
            fh.write(f"reason={result['reason']}\n")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
