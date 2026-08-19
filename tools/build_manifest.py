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

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ManifestEntry:
    id: str
    doc_type: str  # "adr", "spec", "experiment", "post_mortem", "archaeology"
    title: str
    status: str
    relative_path: str
    sha256: str
    target_repositories: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


@dataclass
class LibraryManifest:
    version: str
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
    """Extract targeted satellite repos from text or headers."""
    repos = set()
    for repo in ["tare.tools.kernel", "tare.tools.specgraph", "tare.tools.backlog-graph", "tare.tools.dialog-engine", "tare.tools.os"]:
        if repo in text:
            repos.add(repo)
    return sorted(list(repos))


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
            
            entry = ManifestEntry(
                id=adr_file.stem.split("_")[0],
                doc_type="adr",
                title=title,
                status="RATIFIED",
                relative_path=str(adr_file.relative_to(root)).replace("\\", "/"),
                sha256=sha,
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

            entry = ManifestEntry(
                id=spec_file.stem,
                doc_type="spec",
                title=title,
                status="CANONICAL_SSOT",
                relative_path=str(spec_file.relative_to(root)).replace("\\", "/"),
                sha256=sha,
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

            entry = ManifestEntry(
                id=exp_file.stem,
                doc_type="experiment",
                title=title,
                status="CONCLUDED",
                relative_path=str(exp_file.relative_to(root)).replace("\\", "/"),
                sha256=sha,
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

            entry = ManifestEntry(
                id=pm_file.stem,
                doc_type="post_mortem",
                title=title,
                status="RESOLVED",
                relative_path=str(pm_file.relative_to(root)).replace("\\", "/"),
                sha256=sha,
                target_repositories=_extract_target_repos(text),
            )
            pms.append(entry)

    total = len(adrs) + len(specs) + len(exps) + len(pms)

    return LibraryManifest(
        version="2.0.0",
        generated_at=now_iso,
        total_documents=total,
        canonical_ssot_count=canonical_count,
        adrs=adrs,
        specs=specs,
        experiments=exps,
        post_mortems=pms,
    )


def save_manifest(manifest: LibraryManifest, root_dir: str | Path = ROOT) -> Path:
    """Save manifest to catalog/LIBRARY_MANIFEST.json."""
    root = Path(root_dir)
    catalog_dir = root / "catalog"
    catalog_dir.mkdir(parents=True, exist_ok=True)
    manifest_file = catalog_dir / "LIBRARY_MANIFEST.json"

    # Convert dataclasses to dict
    data = {
        "version": manifest.version,
        "generated_at": manifest.generated_at,
        "total_documents": manifest.total_documents,
        "canonical_ssot_count": manifest.canonical_ssot_count,
        "adrs": [asdict(e) for e in manifest.adrs],
        "specs": [asdict(e) for e in manifest.specs],
        "experiments": [asdict(e) for e in manifest.experiments],
        "post_mortems": [asdict(e) for e in manifest.post_mortems],
    }

    manifest_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
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
