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
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Dict, List, Optional

from tools.federated_documents import iter_manifest_entries, validate_repository_name
from tools.bookkeeper.ssot_registry import (
    STATUS_VOCABULARY_VERSION, classify_status, derive_semantic_document_id,
    parse_document_metadata,
)

ROOT = Path(__file__).resolve().parents[1]


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
    source_paths: List[Dict[str, str]] = field(default_factory=list)
    target_repositories: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


@dataclass
class LibraryManifest:
    version: str
    authority_vocabulary: str
    generated_at: str
    total_documents: int
    canonical_ssot_count: int
    adrs: List[ManifestEntry] = field(default_factory=list)
    specs: List[ManifestEntry] = field(default_factory=list)
    experiments: List[ManifestEntry] = field(default_factory=list)
    post_mortems: List[ManifestEntry] = field(default_factory=list)
    projection_receipt: Dict[str, Any] = field(default_factory=dict)


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
    """Read explicit ownership metadata without inferring ownership from prose."""
    repos = set()
    ownership_line = re.compile(
        r"^\s*(?:[-*>]\s*)?(?:\*\*)?"
        r"(?:canonical\s+repository|target\s+repository|target\s+repositories)"
        r"(?:\*\*)?\s*:\s*(.+?)\s*$",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        match = ownership_line.match(line)
        if match:
            for token in re.split(r"[,;\s]+", match.group(1)):
                name = token.strip("*`[]\"'")
                if name:
                    repos.add(validate_repository_name(name))

    # Documents physically owned by Library remain Library-owned unless their
    # front matter says otherwise. Merely discussing another repository does
    # not transfer authority to it.
    return sorted(repos) if repos else ["tare.tools.library"]


def _collapse_exact_entries(entries: List[ManifestEntry]) -> tuple[List[ManifestEntry], Dict[str, Any]]:
    """Consolidate transport bytes while preserving each source's ownership."""
    groups: Dict[str, List[ManifestEntry]] = {}
    active_identities = {}
    for entry in entries:
        if entry.authority_state in {"DECLARED_ACTIVE", "UNMANAGED_ACTIVE"}:
            for repository in entry.target_repositories:
                identity = (repository, entry.semantic_document_id)
                previous = active_identities.setdefault(identity, entry)
                if previous.sha256 != entry.sha256:
                    raise ValueError(
                        f"conflicting active identity {identity}: "
                        f"{previous.relative_path} and {entry.relative_path}"
                    )
        groups.setdefault(entry.sha256, []).append(entry)
    collapsed = []
    mixed = 0
    precedence = {"EXCLUDED": 0, "UNMANAGED_ACTIVE": 1, "DECLARED_ACTIVE": 2}
    for digest, group in groups.items():
        sources = {}
        for entry in group:
            for source in entry.source_paths:
                path = source["relative_path"]
                if path in sources and sources[path] != source:
                    raise ValueError(f"conflicting source provenance: {path}")
                sources[path] = source
        declared = {
            (repository, source["semantic_document_id"])
            for entry in group
            for repository in entry.target_repositories
            for source in entry.source_paths
            if source["authority_state"] == "DECLARED_ACTIVE"
        }
        if len(declared) > 1:
            raise ValueError(f"conflicting declared identities for payload: {digest}")
        states = {entry.authority_state for entry in group}
        mixed += len(states) > 1
        authority = max(states, key=precedence.__getitem__)
        representative = min(group, key=lambda entry: entry.relative_path.encode("utf-8"))
        authoritative = min(
            (entry for entry in group if entry.authority_state == authority),
            key=lambda entry: entry.relative_path.encode("utf-8"),
        )
        collapsed.append(replace(
            representative,
            semantic_document_id=authoritative.semantic_document_id,
            status=authoritative.status,
            authority_state=authority,
            source_paths=[sources[path] for path in sorted(sources, key=lambda path: path.encode("utf-8"))],
            target_repositories=sorted({repo for entry in group for repo in entry.target_repositories}),
            acceptance_criteria=sorted({ac for entry in group for ac in entry.acceptance_criteria}),
            references=sorted({ref for entry in group for ref in entry.references}),
        ))
    return collapsed, {
        "source_entries": len(entries),
        "unique_payloads": len(collapsed),
        "consolidated_groups": sum(len(group) > 1 for group in groups.values()),
        "source_paths_preserved": sum(len(entry.source_paths) for entry in collapsed),
        "mixed_state_groups": mixed,
    }


def _local_metadata(path: Path, text: str, *, legacy_active: bool = False) -> tuple[str, str, str]:
    metadata = parse_document_metadata(text)
    raw_status = metadata.get("status")
    classification = classify_status(raw_status)
    if classification == "UNKNOWN":
        raise ValueError(
            f"unrecognized document status under vocabulary {STATUS_VOCABULARY_VERSION} "
            f"in {path}: {raw_status!r}"
        )
    authority = "EXCLUDED"
    if classification == "CANONICAL":
        authority = "DECLARED_ACTIVE"
    elif classification == "UNCLASSIFIED" and legacy_active:
        authority = "UNMANAGED_ACTIVE"
    status = raw_status.strip().strip("`") if raw_status and raw_status.strip() else "UNCLASSIFIED"
    return derive_semantic_document_id(path, metadata), status, authority


def build_library_manifest(root_dir: str | Path = ROOT) -> LibraryManifest:
    """Build the complete, verified LibraryManifest object from the filesystem."""
    root = Path(root_dir)
    adrs: List[ManifestEntry] = []
    specs: List[ManifestEntry] = []
    exps: List[ManifestEntry] = []
    pms: List[ManifestEntry] = []

    import datetime
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # 1. Process ADRs (docs/adr/)
    adr_dir = root / "docs" / "adr"
    if adr_dir.exists():
        for adr_file in sorted(adr_dir.glob("*.md")):
            text = adr_file.read_text(encoding="utf-8", errors="ignore")
            sha = compute_sha256_file(adr_file)
            title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else adr_file.stem
            
            semantic_id, status, authority = _local_metadata(adr_file, text)
            relative_path = str(adr_file.relative_to(root)).replace("\\", "/")
            entry = ManifestEntry(
                id=sha,
                semantic_document_id=semantic_id,
                doc_type="adr",
                title=title,
                status=status,
                relative_path=relative_path,
                sha256=sha,
                authority_state=authority,
                source_paths=[{
                    "relative_path": relative_path,
                    "semantic_document_id": semantic_id,
                    "authority_state": authority,
                    "editorial_status": status,
                }],
                target_repositories=_extract_target_repos(text) if authority != "EXCLUDED" else [],
                acceptance_criteria=_extract_acceptance_criteria(text),
            )
            adrs.append(entry)

    # 2. Process OpenSDD Specs (specs/)
    spec_dir = root / "specs"
    if spec_dir.exists():
        for spec_file in sorted(spec_dir.rglob("*.md")):
            text = spec_file.read_text(encoding="utf-8", errors="ignore")
            sha = compute_sha256_file(spec_file)
            title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else spec_file.stem
            semantic_id, status, authority = _local_metadata(spec_file, text, legacy_active=True)

            relative_path = str(spec_file.relative_to(root)).replace("\\", "/")
            entry = ManifestEntry(
                id=sha,
                semantic_document_id=semantic_id,
                doc_type="spec",
                title=title,
                status=status,
                relative_path=relative_path,
                sha256=sha,
                authority_state=authority,
                source_paths=[{
                    "relative_path": relative_path,
                    "semantic_document_id": semantic_id,
                    "authority_state": authority,
                    "editorial_status": status,
                }],
                target_repositories=_extract_target_repos(text) if authority != "EXCLUDED" else [],
                acceptance_criteria=_extract_acceptance_criteria(text),
            )
            specs.append(entry)

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
            semantic_id, status, authority = _local_metadata(exp_file, text, legacy_active=True)

            relative_path = str(exp_file.relative_to(root)).replace("\\", "/")
            entry = ManifestEntry(
                id=sha,
                semantic_document_id=semantic_id,
                doc_type="experiment",
                title=title,
                status=status,
                relative_path=relative_path,
                sha256=sha,
                authority_state=authority,
                source_paths=[{
                    "relative_path": relative_path,
                    "semantic_document_id": semantic_id,
                    "authority_state": authority,
                    "editorial_status": status,
                }],
                target_repositories=_extract_target_repos(text) if authority != "EXCLUDED" else [],
            )
            exps.append(entry)

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
            semantic_id, status, authority = _local_metadata(pm_file, text, legacy_active=True)

            relative_path = str(pm_file.relative_to(root)).replace("\\", "/")
            entry = ManifestEntry(
                id=sha,
                semantic_document_id=semantic_id,
                doc_type="post_mortem",
                title=title,
                status=status,
                relative_path=relative_path,
                sha256=sha,
                authority_state=authority,
                source_paths=[{
                    "relative_path": relative_path,
                    "semantic_document_id": semantic_id,
                    "authority_state": authority,
                    "editorial_status": status,
                }],
                target_repositories=_extract_target_repos(text) if authority != "EXCLUDED" else [],
            )
            pms.append(entry)

    for raw in iter_manifest_entries(root):
        entry = ManifestEntry(**raw)
        if entry.doc_type == "adr":
            adrs.append(entry)
        elif entry.doc_type == "spec":
            specs.append(entry)
        elif entry.doc_type == "experiment":
            exps.append(entry)
        elif entry.doc_type == "post_mortem":
            pms.append(entry)

    all_entries, receipt = _collapse_exact_entries(adrs + specs + exps + pms)
    adrs = [entry for entry in all_entries if entry.doc_type == "adr"]
    specs = [entry for entry in all_entries if entry.doc_type == "spec"]
    exps = [entry for entry in all_entries if entry.doc_type == "experiment"]
    pms = [entry for entry in all_entries if entry.doc_type == "post_mortem"]
    for entries in (adrs, specs, exps, pms):
        entries.sort(key=lambda item: (item.semantic_document_id.casefold(), item.relative_path.encode("utf-8")))
    total = len(all_entries)
    canonical_count = sum(entry.authority_state == "DECLARED_ACTIVE" for entry in all_entries)

    return LibraryManifest(
        version="3.0.0",
        authority_vocabulary="authority_state/v1",
        generated_at=now_iso,
        total_documents=total,
        canonical_ssot_count=canonical_count,
        adrs=adrs,
        specs=specs,
        experiments=exps,
        post_mortems=pms,
        projection_receipt=receipt,
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
        "authority_vocabulary": manifest.authority_vocabulary,
        "generated_at": manifest.generated_at,
        "total_documents": manifest.total_documents,
        "canonical_ssot_count": manifest.canonical_ssot_count,
        "adrs": [asdict(e) for e in manifest.adrs],
        "specs": [asdict(e) for e in manifest.specs],
        "experiments": [asdict(e) for e in manifest.experiments],
        "post_mortems": [asdict(e) for e in manifest.post_mortems],
        "projection_receipt": manifest.projection_receipt,
    }

    import tempfile
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", dir=catalog_dir, delete=False, encoding="utf-8", suffix=".tmp") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
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
    manifest = build_library_manifest(args.root)
    out_file = save_manifest(manifest, args.root)

    print(f"[SUCCESS] Wrote '{out_file}'")
    print(f"  - Total Documents: {manifest.total_documents}")
    print(f"  - Canonical SSOT: {manifest.canonical_ssot_count}")
    print(f"  - ADRs: {len(manifest.adrs)}")
    print(f"  - SPECs: {len(manifest.specs)}")
    print(f"  - Experiments: {len(manifest.experiments)}")
    print(f"  - Post-Mortems: {len(manifest.post_mortems)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
