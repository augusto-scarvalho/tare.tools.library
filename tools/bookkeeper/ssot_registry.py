"""SSOT Registry Auditor for tare.tools.library.

Enforces that every active canonical document has a unique doc_id, and that there is
never more than one file claiming CANONICAL_SSOT status for the same conceptual topic.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class SSOTDocument:
    file_path: str
    doc_id: str
    title: str
    status: str
    is_canonical: bool
    superseded_by: Optional[str] = None


@dataclass
class SSOTViolation:
    doc_id: str
    files: List[str]
    description: str


@dataclass
class SSOTReport:
    total_documents: int
    canonical_documents: int
    violations: List[SSOTViolation] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.violations) == 0


def _parse_frontmatter_or_headers(content: str) -> Dict[str, str]:
    """Extract metadata from YAML frontmatter or top markdown headers."""
    metadata: Dict[str, str] = {}
    
    # Try YAML frontmatter
    fm_match = re.match(r"^---\n(.*?)\n---\n", content, flags=re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                metadata[key.strip().lower()] = val.strip().strip("\"'")

    # Extract title from first # Header if missing
    title_match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
    if title_match and "title" not in metadata:
        metadata["title"] = title_match.group(1).strip()

    # Extract status if inline
    status_match = re.search(r"-\s+\*\*Status:\*\*\s+([^\n]+)", content, flags=re.IGNORECASE)
    if status_match and "status" not in metadata:
        metadata["status"] = status_match.group(1).strip()

    return metadata


def audit_ssot_registry(
    root_dir: str | Path,
    include_extensions: Tuple[str, ...] = (".md", ".markdown"),
    exclude_dirs: Tuple[str, ...] = (".git", ".pytest_cache", "__pycache__", "site", "_site", "archaeology"),
) -> SSOTReport:
    """Audit the repository to ensure exactly one CANONICAL_SSOT document exists per doc_id."""
    root_path = Path(root_dir)
    registry: Dict[str, List[SSOTDocument]] = {}
    total_docs = 0
    canonical_count = 0

    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in include_extensions:
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            try:
                raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
                meta = _parse_frontmatter_or_headers(raw_text)
                rel_path = str(file_path.relative_to(root_path)).replace("\\", "/")

                # Derive doc_id from metadata or filename stem
                doc_id = meta.get("doc_id") or meta.get("id")
                if not doc_id:
                    # e.g., ADR-051_... -> ADR-051
                    stem = file_path.stem.upper()
                    adr_match = re.match(r"(ADR-\d+)", stem)
                    exp_match = re.match(r"(EXP-\d+)", stem)
                    if adr_match:
                        doc_id = adr_match.group(1)
                    elif exp_match:
                        doc_id = exp_match.group(1)
                    else:
                        doc_id = rel_path

                status = meta.get("status", "DRAFT").upper()
                is_canonical = ("CANONICAL" in status or "RATIFIED" in status or "APPROVED" in status or "SSOT" in status)
                if is_canonical:
                    canonical_count += 1

                doc = SSOTDocument(
                    file_path=rel_path,
                    doc_id=doc_id,
                    title=meta.get("title", file_path.stem),
                    status=status,
                    is_canonical=is_canonical,
                    superseded_by=meta.get("superseded_by"),
                )

                registry.setdefault(doc_id, []).append(doc)
                total_docs += 1
            except Exception:
                continue

    violations: List[SSOTViolation] = []
    for doc_id, docs in registry.items():
        canonicals = [d for d in docs if d.is_canonical]
        if len(canonicals) > 1:
            violations.append(
                SSOTViolation(
                    doc_id=doc_id,
                    files=[d.file_path for d in canonicals],
                    description=f"Multiple documents claim CANONICAL_SSOT status for '{doc_id}'",
                )
            )

    return SSOTReport(
        total_documents=total_docs,
        canonical_documents=canonical_count,
        violations=violations,
    )
