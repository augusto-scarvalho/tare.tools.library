"""Library Manifest Compiler for tare.tools.library.

Aggregates all canonical ADRs, OpenSDD Specifications, Experiments, and Post-Mortems
into a single, machine-readable, cryptographically verified catalog/LIBRARY_MANIFEST.json
consumed by SpecGraph (Substrate Admission Gate) and Backlog-Graph (DAG Engine).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from tools.bookkeeper.ssot_registry import (
    STATUS_CANONICAL,
    STATUS_NON_CANONICAL,
    STATUS_UNCLASSIFIED,
    STATUS_VOCABULARY_VERSION,
    classify_status,
    derive_semantic_document_id,
    parse_document_metadata,
)
from tools.bookkeeper.tombstone_manager import verify_tombstones

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ManifestSource:
    relative_path: str
    semantic_document_id: str
    authority_state: str
    editorial_status: str


@dataclass
class ManifestEntry:
    id: str
    semantic_document_id: str
    doc_type: str  # "adr", "spec", "experiment", "post_mortem", "archaeology"
    title: str
    status: str
    relative_path: str
    sha256: str
    authority_state: str
    source_paths: List[ManifestSource]
    target_repositories: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


@dataclass
class LibraryManifest:
    version: str
    total_documents: int
    canonical_ssot_count: int
    projection_receipt: Dict[str, object]
    adrs: List[ManifestEntry] = field(default_factory=list)
    specs: List[ManifestEntry] = field(default_factory=list)
    experiments: List[ManifestEntry] = field(default_factory=list)
    post_mortems: List[ManifestEntry] = field(default_factory=list)


def compute_sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_acceptance_criteria(text: str) -> List[str]:
    """Extract AC items like AC-01, AC-02 or bullet points under Acceptance Criteria header."""
    criteria = []
    for line in text.splitlines():
        ac_match = re.search(r"\b(AC-\d+[:\s][^\n]+)", line)
        if ac_match:
            criteria.append(ac_match.group(1).strip())
    return criteria


def _extract_target_repos(text: str) -> List[str]:
    """Extract targeted satellite repos from text or headers."""
    repos = set()
    for repo in ["tare.tools.kernel", "tare.tools.specgraph", "tare.tools.backlog-graph", "tare.tools.dialog-engine", "tare.tools.os"]:
        if repo in text:
            repos.add(repo)
    return sorted(list(repos))


AUTHORITY_DECLARED = "DECLARED_ACTIVE"
AUTHORITY_UNMANAGED = "UNMANAGED_ACTIVE"
AUTHORITY_CONFLICT = "CONFLICT"
AUTHORITY_EXCLUDED = "EXCLUDED"
AUTHORITY_VOCABULARY_VERSION = "authority_state/v1"
_AUTHORITY_PRECEDENCE = {
    AUTHORITY_EXCLUDED: 0,
    AUTHORITY_UNMANAGED: 1,
    AUTHORITY_DECLARED: 2,
    AUTHORITY_CONFLICT: 3,
}


@dataclass
class _SourceDocument:
    semantic_document_id: str
    doc_type: str
    title: str
    editorial_status: str
    relative_path: str
    sha256: str
    authority_state: str
    target_repositories: List[str]
    acceptance_criteria: List[str]


class ManifestConflictError(ValueError):
    """Raised with a bounded receipt when projection authority is ambiguous."""

    def __init__(self, conflicts: List[str], receipt: Dict[str, object]) -> None:
        self.conflicts = tuple(conflicts)
        self.receipt = receipt
        super().__init__(
            "active canonical authority conflict; manifest not published:\n- "
            + "\n- ".join(conflicts)
        )


def _manifest_status(raw_status: Optional[str], classification: str) -> str:
    if classification == STATUS_CANONICAL:
        return "RATIFIED"
    if classification == STATUS_UNCLASSIFIED:
        return STATUS_UNCLASSIFIED
    if classification == STATUS_NON_CANONICAL:
        return raw_status.strip().strip("`").upper() if raw_status else STATUS_NON_CANONICAL
    raise ValueError(
        f"unrecognized document status under vocabulary {STATUS_VOCABULARY_VERSION}: "
        f"{raw_status!r}"
    )


def _path_key(path: str) -> bytes:
    return path.replace("\\", "/").encode("utf-8")


def _projection_receipt(
    sources: List[_SourceDocument],
    groups: Dict[str, List[_SourceDocument]],
    *,
    conflicts: List[str],
    tombstones_total: int,
    tombstones_valid: int,
    tombstones_broken: int,
) -> Dict[str, object]:
    state_counts = {
        state: sum(source.authority_state == state for source in sources)
        for state in _AUTHORITY_PRECEDENCE
    }
    mixed_groups = sum(
        len({source.authority_state for source in group}) > 1
        for group in groups.values()
    )
    return {
        "schema": "tare.tools/library-projection-receipt/1",
        "status": "BLOCKED" if conflicts or tombstones_broken else "COMPLETE",
        "source_count": len(sources),
        "payload_count": len(groups),
        "exact_groups_consolidated": sum(len(group) > 1 for group in groups.values()),
        "consolidated_source_count": sum(
            len(group) - 1 for group in groups.values() if len(group) > 1
        ),
        "authority_source_counts": state_counts,
        "mixed_state_groups": mixed_groups,
        "semantic_conflict_count": len(conflicts),
        "tombstones_total": tombstones_total,
        "tombstones_valid": tombstones_valid,
        "tombstones_broken": tombstones_broken,
    }


def _group_sources(
    sources: List[_SourceDocument], root: Path
) -> tuple[List[ManifestEntry], Dict[str, object]]:
    active_by_semantic: Dict[str, Dict[str, List[_SourceDocument]]] = {}
    for source in sources:
        if source.authority_state in {AUTHORITY_DECLARED, AUTHORITY_UNMANAGED}:
            active_by_semantic.setdefault(source.semantic_document_id, {}).setdefault(
                source.sha256, []
            ).append(source)

    conflicts: List[str] = []
    conflicting_semantic_ids = {
        semantic_id
        for semantic_id, hashes in active_by_semantic.items()
        if len(hashes) > 1
    }
    for semantic_id in sorted(conflicting_semantic_ids):
        paths = sorted(
            (
                source.relative_path
                for group in active_by_semantic[semantic_id].values()
                for source in group
            ),
            key=_path_key,
        )
        conflicts.append(f"semantic document ID {semantic_id!r}: {paths}")

    for source in sources:
        if source.semantic_document_id in conflicting_semantic_ids:
            source.authority_state = AUTHORITY_CONFLICT
            source.target_repositories = []

    groups: Dict[str, List[_SourceDocument]] = {}
    for source in sources:
        groups.setdefault(source.sha256, []).append(source)

    for content_hash, group in sorted(groups.items()):
        declared_ids = {
            source.semantic_document_id
            for source in group
            if source.authority_state == AUTHORITY_DECLARED
        }
        if len(declared_ids) > 1:
            conflicts.append(
                f"content hash {content_hash} has multiple declared identities: "
                f"{sorted(declared_ids)}"
            )
            for source in group:
                if source.authority_state != AUTHORITY_EXCLUDED:
                    source.authority_state = AUTHORITY_CONFLICT
                    source.target_repositories = []

    tombstones = verify_tombstones(root / "docs")
    if tombstones.broken_pointers:
        conflicts.extend(
            f"broken tombstone {source!r} -> {target!r}"
            for source, target in tombstones.broken_pointers
        )

    receipt = _projection_receipt(
        sources,
        groups,
        conflicts=conflicts,
        tombstones_total=tombstones.total_tombstones,
        tombstones_valid=tombstones.valid_tombstones,
        tombstones_broken=len(tombstones.broken_pointers),
    )
    if conflicts:
        raise ManifestConflictError(conflicts, receipt)

    entries: List[ManifestEntry] = []
    for content_hash, group in sorted(groups.items()):
        ordered = sorted(group, key=lambda source: _path_key(source.relative_path))
        representative = ordered[0]
        group_state = max(
            (source.authority_state for source in ordered),
            key=_AUTHORITY_PRECEDENCE.__getitem__,
        )
        active = group_state in {AUTHORITY_DECLARED, AUTHORITY_UNMANAGED}
        semantic_ids = sorted(
            {
                source.semantic_document_id
                for source in ordered
                if source.authority_state == group_state
            }
        )
        entries.append(
            ManifestEntry(
                id=content_hash,
                semantic_document_id=semantic_ids[0]
                if semantic_ids
                else representative.semantic_document_id,
                doc_type=representative.doc_type,
                title=representative.title,
                status=representative.editorial_status,
                relative_path=representative.relative_path,
                sha256=content_hash,
                authority_state=group_state,
                source_paths=[
                    ManifestSource(
                        relative_path=source.relative_path,
                        semantic_document_id=source.semantic_document_id,
                        authority_state=source.authority_state,
                        editorial_status=source.editorial_status,
                    )
                    for source in ordered
                ],
                target_repositories=sorted(
                    {
                        target
                        for source in ordered
                        if active
                        for target in source.target_repositories
                    }
                ),
                acceptance_criteria=representative.acceptance_criteria,
            )
        )
    return entries, receipt


def build_library_manifest(root_dir: str | Path = ROOT) -> LibraryManifest:
    """Build the complete, verified LibraryManifest object from the filesystem."""
    root = Path(root_dir)
    sources: List[_SourceDocument] = []

    # 1. Process ADRs (docs/adr/)
    adr_dir = root / "docs" / "adr"
    if adr_dir.exists():
        for adr_file in sorted(adr_dir.glob("*.md")):
            text = adr_file.read_text(encoding="utf-8", errors="ignore")
            sha = compute_sha256_file(adr_file)
            title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else adr_file.stem
            metadata = parse_document_metadata(text)
            raw_status = metadata.get("status")
            status_classification = classify_status(raw_status)

            authority_state = (
                AUTHORITY_DECLARED
                if status_classification == STATUS_CANONICAL
                else AUTHORITY_EXCLUDED
            )
            sources.append(_SourceDocument(
                semantic_document_id=derive_semantic_document_id(
                    adr_file, metadata, root
                ),
                doc_type="adr",
                title=title,
                editorial_status=_manifest_status(raw_status, status_classification),
                relative_path=str(adr_file.relative_to(root)).replace("\\", "/"),
                sha256=sha,
                authority_state=authority_state,
                target_repositories=(
                    _extract_target_repos(text)
                    if authority_state == AUTHORITY_DECLARED
                    else []
                ),
                acceptance_criteria=_extract_acceptance_criteria(text),
            ))

    # 2. Process OpenSDD Specs (specs/)
    spec_dir = root / "specs"
    if spec_dir.exists():
        for spec_file in sorted(spec_dir.rglob("*.md")):
            text = spec_file.read_text(encoding="utf-8", errors="ignore")
            sha = compute_sha256_file(spec_file)
            title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else spec_file.stem

            metadata = parse_document_metadata(text)
            sources.append(_SourceDocument(
                semantic_document_id=derive_semantic_document_id(
                    spec_file, metadata, root
                ),
                doc_type="spec",
                title=title,
                editorial_status="UNMANAGED",
                relative_path=str(spec_file.relative_to(root)).replace("\\", "/"),
                sha256=sha,
                authority_state=AUTHORITY_UNMANAGED,
                target_repositories=_extract_target_repos(text),
                acceptance_criteria=_extract_acceptance_criteria(text),
            ))

    # 3. Process Experiments (experiments/)
    exp_dir = root / "experiments"
    if exp_dir.exists():
        for exp_file in sorted(exp_dir.rglob("*.md")):
            if exp_file.name.upper() == "README.MD":
                continue
            text = exp_file.read_text(encoding="utf-8", errors="ignore")
            sha = compute_sha256_file(exp_file)
            title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else exp_file.stem

            metadata = parse_document_metadata(text)
            sources.append(_SourceDocument(
                semantic_document_id=derive_semantic_document_id(
                    exp_file, metadata, root
                ),
                doc_type="experiment",
                title=title,
                editorial_status="CONCLUDED",
                relative_path=str(exp_file.relative_to(root)).replace("\\", "/"),
                sha256=sha,
                authority_state=AUTHORITY_EXCLUDED,
                target_repositories=[],
                acceptance_criteria=_extract_acceptance_criteria(text),
            ))

    # 4. Process Post-Mortems (docs/post-mortems/)
    pm_dir = root / "docs" / "post-mortems"
    if pm_dir.exists():
        for pm_file in sorted(pm_dir.rglob("*.md")):
            if pm_file.name.upper() == "README.MD":
                continue
            text = pm_file.read_text(encoding="utf-8", errors="ignore")
            sha = compute_sha256_file(pm_file)
            title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else pm_file.stem

            metadata = parse_document_metadata(text)
            sources.append(_SourceDocument(
                semantic_document_id=derive_semantic_document_id(
                    pm_file, metadata, root
                ),
                doc_type="post_mortem",
                title=title,
                editorial_status="RESOLVED",
                relative_path=str(pm_file.relative_to(root)).replace("\\", "/"),
                sha256=sha,
                authority_state=AUTHORITY_EXCLUDED,
                target_repositories=[],
                acceptance_criteria=_extract_acceptance_criteria(text),
            ))

    entries, receipt = _group_sources(sources, root)
    collections: Dict[str, List[ManifestEntry]] = {
        "adr": [],
        "spec": [],
        "experiment": [],
        "post_mortem": [],
    }
    for entry in entries:
        collections[entry.doc_type].append(entry)
    canonical_count = sum(
        entry.authority_state == AUTHORITY_DECLARED for entry in entries
    )

    return LibraryManifest(
        version="3.0.0",
        total_documents=len(sources),
        canonical_ssot_count=canonical_count,
        projection_receipt=receipt,
        adrs=collections["adr"],
        specs=collections["spec"],
        experiments=collections["experiment"],
        post_mortems=collections["post_mortem"],
    )


def save_manifest(manifest: LibraryManifest, root_dir: str | Path = ROOT) -> Path:
    """Save manifest to catalog/LIBRARY_MANIFEST.json atomically to prevent partial reads."""
    root = Path(root_dir)
    catalog_dir = root / "catalog"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = catalog_dir / "LIBRARY_MANIFEST.json"

    # Convert dataclasses to dict
    data = {
        "version": manifest.version,
        "total_documents": manifest.total_documents,
        "canonical_ssot_count": manifest.canonical_ssot_count,
        "authority_vocabulary": AUTHORITY_VOCABULARY_VERSION,
        "projection_receipt": manifest.projection_receipt,
        "adrs": [asdict(e) for e in manifest.adrs],
        "specs": [asdict(e) for e in manifest.specs],
        "experiments": [asdict(e) for e in manifest.experiments],
        "post_mortems": [asdict(e) for e in manifest.post_mortems],
    }

    import tempfile
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=catalog_dir, delete=False, encoding="utf-8", suffix=".tmp") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False, sort_keys=True)
            tf.flush()
            os.fsync(tf.fileno())
            temp_path = Path(tf.name)
        os.replace(temp_path, manifest_file)
        # Attempt directory fsync on platforms that support it (POSIX durability)
        try:
            dir_fd = os.open(str(catalog_dir), os.O_RDONLY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        except Exception:
            pass
    except Exception:
        if temp_path and temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise
    return manifest_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile and verify catalog/LIBRARY_MANIFEST.json for tare.tools.library")
    parser.add_argument("--root", default=".", help="Root directory of the library")
    args = parser.parse_args()

    print(f"[MANIFEST] Compiling Library Manifest for '{args.root}'...")
    try:
        manifest = build_library_manifest(args.root)
    except ManifestConflictError as exc:
        print(
            json.dumps(
                {
                    "error": "MANIFEST_AUTHORITY_CONFLICT",
                    "conflicts": list(exc.conflicts),
                    "projection_receipt": exc.receipt,
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 1
    out_file = save_manifest(manifest, args.root)

    print(f"[SUCCESS] Wrote '{out_file}'")
    print(f"  - Total Documents: {manifest.total_documents}")
    print(f"  - Canonical SSOT: {manifest.canonical_ssot_count}")
    print(f"  - Projected payloads: {manifest.projection_receipt['payload_count']}")
    print(
        "  - Exact groups consolidated: "
        f"{manifest.projection_receipt['exact_groups_consolidated']}"
    )
    print(f"  - ADRs: {len(manifest.adrs)}")
    print(f"  - SPECs: {len(manifest.specs)}")
    print(f"  - Experiments: {len(manifest.experiments)}")
    print(f"  - Post-Mortems: {len(manifest.post_mortems)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
