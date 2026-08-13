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
    dual_owner = bool(current_owner and candidate_capable)
    return {
        "current_deploy_owner": current_owner,
        "candidate_deploy_capable": candidate_capable,
        "candidate_deploy_markers": findings,
        "dual_owner": dual_owner,
        "status": "PASS" if not candidate_capable and not dual_owner else "FAIL",
    }


def _find_metadata(root: Path, canary_id: str) -> Path | None:
    for path in sorted(root.rglob("document-metadata.json")):
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        try:
            metadata = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if metadata.get("document_id") == canary_id:
            return path
    return None


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
