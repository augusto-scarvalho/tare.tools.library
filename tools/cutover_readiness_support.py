from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from pages_common import sha256_file

DEPLOY_MARKERS = (
    "actions/deploy-pages",
    "actions/upload-pages-artifact",
    "pages: write",
    "id-token: write",
)
VISUAL_EVIDENCE_PATH = Path("site/PAGES_VISUAL_EVIDENCE.json")


def canonical_digest(rows: list[dict[str, str]]) -> str:
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def inventory(root: Path) -> dict[str, Any]:
    rows = [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256_file(path)}
        for path in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix())
        if path.is_file()
    ]
    return {"file_count": len(rows), "digest": canonical_digest(rows), "files": rows}


def rollback_evidence(incumbent: Path, profile: dict[str, Any], parity: dict[str, Any]) -> dict[str, Any]:
    critical = list(profile.get("critical_paths", []))
    critical_missing = [rel for rel in critical if not (incumbent / rel).is_file()]
    materialized = inventory(incumbent) if incumbent.is_dir() else {"file_count": 0, "digest": None, "files": []}
    parity_bound = (
        parity.get("status") == "PASS"
        and parity.get("incumbent_source_ref") == profile.get("source_ref")
        and not parity.get("missing_incumbent_paths", [])
        and not parity.get("modified_incumbent_paths", [])
        and not parity.get("critical_missing", [])
    )
    ready = bool(incumbent.is_dir() and materialized["file_count"] and not critical_missing and parity_bound)
    return {
        "status": "PASS" if ready else "FAIL",
        "rollback_ready": ready,
        "source_ref": profile.get("source_ref"),
        "critical_paths": critical,
        "critical_missing": critical_missing,
        "materialized_incumbent": materialized,
        "candidate_parity_bound": parity_bound,
    }


def workflow_ownership(root: Path, current_owner: str | None) -> dict[str, Any]:
    workflow_root = root / ".github" / "workflows"
    findings: list[dict[str, Any]] = []
    paths = sorted([*workflow_root.glob("*.yml"), *workflow_root.glob("*.yaml")])
    for path in paths:
        text = path.read_text(encoding="utf-8")
        markers = [marker for marker in DEPLOY_MARKERS if marker in text]
        if markers:
            findings.append({"path": path.relative_to(root).as_posix(), "markers": markers})

    candidate_capable = bool(findings)
    incumbent_recorded = bool(current_owner)
    active_owner_count = int(incumbent_recorded) + int(candidate_capable)
    dual_owner = active_owner_count > 1
    if dual_owner:
        state = "DUAL_OWNER"
    elif incumbent_recorded:
        state = "INCUMBENT_ONLY"
    elif candidate_capable:
        state = "CANDIDATE_ONLY"
    else:
        state = "NO_OWNER"

    return {
        "current_deploy_owner": current_owner,
        "incumbent_owner_recorded": incumbent_recorded,
        "candidate_deploy_capable": candidate_capable,
        "candidate_deploy_markers": findings,
        "active_owner_count": active_owner_count,
        "single_owner_invariant": not dual_owner,
        "dual_owner": dual_owner,
        "state": state,
        "status": "FAIL" if dual_owner else "PASS",
    }


def visual_evidence(root: Path, output: Path, canary_id: str) -> dict[str, Any]:
    evidence_path = root / VISUAL_EVIDENCE_PATH
    if not evidence_path.is_file():
        return {
            "status": "NOT_RUN",
            "document_id": canary_id,
            "evidence_path": VISUAL_EVIDENCE_PATH.as_posix(),
            "errors": ["visual evidence record is absent"],
        }

    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {
            "status": "FAIL",
            "document_id": canary_id,
            "evidence_path": VISUAL_EVIDENCE_PATH.as_posix(),
            "errors": [f"invalid visual evidence: {exc}"],
        }

    errors: list[str] = []
    if evidence.get("record_version") != "1.0":
        errors.append("visual evidence record_version must be 1.0")
    if evidence.get("record_kind") != "pages-visual-validation-evidence":
        errors.append("visual evidence record_kind mismatch")
    if evidence.get("document_id") != canary_id:
        errors.append("visual evidence document_id mismatch")

    validated = evidence.get("validated_projection")
    if not isinstance(validated, dict):
        errors.append("validated_projection required")
        validated = {}
    checks = (
        ("page_path", "page_sha256"),
        ("signal_css_path", "signal_css_sha256"),
        ("signal_js_path", "signal_js_sha256"),
    )
    observed: dict[str, Any] = {}
    for path_key, digest_key in checks:
        rel = validated.get(path_key)
        expected = validated.get(digest_key)
        if not isinstance(rel, str) or not rel:
            errors.append(f"{path_key} required")
            continue
        path = output / rel
        if not path.is_file():
            errors.append(f"visual evidence target missing: {rel}")
            continue
        actual = sha256_file(path)
        observed[digest_key] = actual
        if actual != expected:
            errors.append(f"visual evidence stale for {rel}")

    viewports = evidence.get("viewports")
    if not isinstance(viewports, list):
        errors.append("viewports required")
        viewports = []
    by_name = {row.get("name"): row for row in viewports if isinstance(row, dict)}
    for name in ("desktop", "mobile"):
        row = by_name.get(name)
        if not isinstance(row, dict):
            errors.append(f"missing {name} visual evidence")
            continue
        for key in (
            "no_horizontal_overflow",
            "image_loaded",
            "table_visible",
            "code_visible",
            "figure_visible",
            "details_visible",
        ):
            if row.get(key) is not True:
                errors.append(f"{name} visual assertion failed: {key}")
        screenshot_digest = row.get("screenshot_sha256")
        if not isinstance(screenshot_digest, str) or len(screenshot_digest) != 64:
            errors.append(f"{name} screenshot_sha256 required")

    return {
        "status": "PASS" if not errors else "FAIL",
        "document_id": canary_id,
        "evidence_path": VISUAL_EVIDENCE_PATH.as_posix(),
        "renderer": evidence.get("renderer"),
        "validated_projection": validated,
        "observed_sha256": observed,
        "viewports": viewports,
        "errors": errors,
    }


def _find_metadata(root: Path, canary_id: str) -> Path | None:
    matches: list[Path] = []
    for path in sorted(root.rglob("document-metadata.json")):
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        try:
            metadata = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if metadata.get("document_id") == canary_id:
            matches.append(path)
    if not matches:
        return None
    # The accepted incoming packet is intentionally retained. Once a routed
    # publication exists, prefer the materialization carrying PUBLICATION_RECORD
    # so provenance staging cannot shadow the actual published source.
    matches.sort(key=lambda path: (not (path.parent / "PUBLICATION_RECORD.json").is_file(), path.as_posix()))
    return matches[0]


def canary_evidence(root: Path, output: Path, canary_id: str) -> dict[str, Any]:
    metadata_path = _find_metadata(root, canary_id)
    slug = canary_id.replace(".", "-")
    projection_path = output / "p" / slug / "PROJECTION_RECORD.json"
    if metadata_path is None:
        return {
            "document_id": canary_id,
            "status": "MISSING",
            "projected": False,
            "blocker": "real canonical canary submission is not present on this ref",
        }
    packet = metadata_path.parent
    decision_path = packet / "EDITORIAL_DECISION.json"
    record_path = packet / "PUBLICATION_RECORD.json"
    result: dict[str, Any] = {
        "document_id": canary_id,
        "metadata_path": metadata_path.relative_to(root).as_posix(),
        "decision_present": decision_path.is_file(),
        "publication_record_present": record_path.is_file(),
        "projected": projection_path.is_file(),
    }
    if not decision_path.is_file():
        result.update(status="PENDING_OWNER_DECISION", blocker="editorial authority has not been materialized")
        return result
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    result["editorial_decision"] = {
        "decision_id": decision.get("decision_id"),
        "decision": decision.get("decision"),
        "pages_approved": decision.get("pages_approved"),
        "sha256": sha256_file(decision_path),
    }
    if decision.get("decision") != "accept" or decision.get("pages_approved") is not True:
        result.update(status="NOT_AUTHORIZED", blocker="editorial decision does not authorize Pages publication")
        return result
    if not record_path.is_file():
        result.update(status="PENDING_PUBLICATION", blocker="approved canary has no publication record")
        return result
    if not projection_path.is_file():
        result.update(status="PENDING_PROJECTION", blocker="approved publication is absent from the shadow projection")
        return result
    projection = json.loads(projection_path.read_text(encoding="utf-8"))
    result.update(
        status="PROJECTED_APPROVED",
        blocker=None,
        projection_record=projection_path.relative_to(output).as_posix(),
        source_sha256=projection.get("source_sha256"),
        source_semantic_fingerprint=projection.get("source_semantic_fingerprint"),
        projected_semantic_fingerprint=projection.get("projected_semantic_fingerprint"),
        semantic_surface_parity=projection.get("semantic_parity") is True,
        projected_url=projection.get("output_path"),
    )
    return result
