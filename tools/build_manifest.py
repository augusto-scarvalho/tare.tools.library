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
from typing import Any, Dict, List, Optional

from tools.federated_documents import iter_manifest_entries

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
    repo_name = re.compile(r"\btare\.tools\.[a-z0-9-]+\b", re.IGNORECASE)

    for line in text.splitlines():
        match = ownership_line.match(line)
        if match:
            repos.update(repo.lower() for repo in repo_name.findall(match.group(1)))

    # Documents physically owned by Library remain Library-owned unless their
    # front matter says otherwise. Merely discussing another repository does
    # not transfer authority to it.
    return sorted(repos) if repos else ["tare.tools.library"]


def build_library_manifest(root_dir: str | Path = ROOT) -> LibraryManifest:
    """Build the complete, verified LibraryManifest object from the filesystem."""
    root = Path(root_dir)
    adrs: List[ManifestEntry] = []
    specs: List[ManifestEntry] = []
    exps: List[ManifestEntry] = []
    pms: List[ManifestEntry] = []
    canonical_count = 0

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
            
            semantic_id_match = re.search(
                r"(?<![A-Za-z0-9])ADR-\d+(?!\d)",
                adr_file.stem,
                re.IGNORECASE,
            )
            semantic_id = semantic_id_match.group(0).upper() if semantic_id_match else adr_file.stem
            relative_path = str(adr_file.relative_to(root)).replace("\\", "/")
            entry = ManifestEntry(
                id=sha,
                semantic_document_id=semantic_id,
                doc_type="adr",
                title=title,
                status="RATIFIED",
                relative_path=relative_path,
                sha256=sha,
                authority_state="UNMANAGED_ACTIVE",
                source_paths=[{
                    "relative_path": relative_path,
                    "semantic_document_id": semantic_id,
                    "authority_state": "UNMANAGED_ACTIVE",
                    "editorial_status": "RATIFIED",
                }],
                target_repositories=_extract_target_repos(text),
                acceptance_criteria=_extract_acceptance_criteria(text),
            )
            adrs.append(entry)
            canonical_count += 1

    # 2. Process OpenSDD Specs (specs/)
    spec_dir = root / "specs"
    if spec_dir.exists():
        for spec_file in sorted(spec_dir.rglob("*.md")):
            text = spec_file.read_text(encoding="utf-8", errors="ignore")
            sha = compute_sha256_file(spec_file)
            title_match = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
            title = title_match.group(1).strip() if title_match else spec_file.stem

            relative_path = str(spec_file.relative_to(root)).replace("\\", "/")
            entry = ManifestEntry(
                id=sha,
                semantic_document_id=spec_file.stem,
                doc_type="spec",
                title=title,
                status="CANONICAL_SSOT",
                relative_path=relative_path,
                sha256=sha,
                authority_state="UNMANAGED_ACTIVE",
                source_paths=[{
                    "relative_path": relative_path,
                    "semantic_document_id": spec_file.stem,
                    "authority_state": "UNMANAGED_ACTIVE",
                    "editorial_status": "CANONICAL_SSOT",
                }],
                target_repositories=_extract_target_repos(text),
                acceptance_criteria=_extract_acceptance_criteria(text),
            )
            specs.append(entry)
            canonical_count += 1

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

            relative_path = str(exp_file.relative_to(root)).replace("\\", "/")
            entry = ManifestEntry(
                id=sha,
                semantic_document_id=exp_file.stem,
                doc_type="experiment",
                title=title,
                status="CONCLUDED",
                relative_path=relative_path,
                sha256=sha,
                authority_state="UNMANAGED_ACTIVE",
                source_paths=[{
                    "relative_path": relative_path,
                    "semantic_document_id": exp_file.stem,
                    "authority_state": "UNMANAGED_ACTIVE",
                    "editorial_status": "CONCLUDED",
                }],
                target_repositories=_extract_target_repos(text),
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

            relative_path = str(pm_file.relative_to(root)).replace("\\", "/")
            entry = ManifestEntry(
                id=sha,
                semantic_document_id=pm_file.stem,
                doc_type="post_mortem",
                title=title,
                status="RESOLVED",
                relative_path=relative_path,
                sha256=sha,
                authority_state="UNMANAGED_ACTIVE",
                source_paths=[{
                    "relative_path": relative_path,
                    "semantic_document_id": pm_file.stem,
                    "authority_state": "UNMANAGED_ACTIVE",
                    "editorial_status": "RESOLVED",
                }],
                target_repositories=_extract_target_repos(text),
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

    for entries in (adrs, specs, exps, pms):
        entries.sort(key=lambda item: (item.semantic_document_id.casefold(), item.relative_path.encode("utf-8")))
    all_entries = adrs + specs + exps + pms
    payload_ids = [entry.id for entry in all_entries]
    if len(payload_ids) != len(set(payload_ids)):
        raise ValueError("manifest contains duplicate content payloads")
    total = len(all_entries)
    canonical_count = len(adrs) + len(specs)

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
