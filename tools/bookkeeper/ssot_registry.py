"""SSOT Registry Auditor for tare.tools.library.

Enforces that every active canonical document has a unique doc_id, and that there is
never more than one file claiming CANONICAL_SSOT status for the same conceptual topic.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


STATUS_VOCABULARY_VERSION = "1.1"
_CANONICAL = {
    "ACCEPTED", "APPROVED", "APROVADO", "APROVADA", "CANONICAL",
    "CANONICAL_SSOT", "CANONICA", "CANONICO", "RATIFIED", "RATIFICADA",
    "RATIFICADO", "OFFICIAL_SOURCE_OF_TRUTH", "SSOT",
}
_NON_CANONICAL = {
    "ACTIVE", "ADAPTED", "ADOPTED", "ARCHIVED", "ARCHIVED_SUPERSEDED",
    "CODE_AUDITED", "DRAFT", "PROPOSTA", "PROPOSTO", "PROPOSED", "RESEARCH",
    "RESOLVED", "RESOLVIDO", "RETIRED", "RUNNING", "SUPERSEDED", "UNCLASSIFIED",
}


def classify_status(status: Optional[str]) -> str:
    """Closed EN/PT vocabulary; ownership adoption is not renamed ratification."""
    if status is None or not status.strip():
        return "UNCLASSIFIED"
    normalized = unicodedata.normalize("NFKD", status).encode("ascii", "ignore").decode().upper()
    normalized = re.sub(r"[^A-Z0-9]+", "_", normalized).strip("_")
    terms = set(normalized.split("_"))
    if terms & {"NOT", "NAO", "NON"}:
        return "UNKNOWN"
    if normalized == "OWNER_ADOPTED":
        return "CANONICAL"
    if normalized in _NON_CANONICAL or terms & _NON_CANONICAL:
        return "NON_CANONICAL"
    if normalized in _CANONICAL or terms & _CANONICAL:
        return "CANONICAL"
    return "UNKNOWN"


def derive_semantic_document_id(file_path: Path, metadata: Dict[str, str]) -> str:
    """Explicit identity wins; a content-hash suffix does not create a new one."""
    explicit = metadata.get("doc_id") or metadata.get("id")
    return (explicit or re.sub(r"_[0-9a-fA-F]{8,64}$", "", file_path.stem)).strip().upper()


@dataclass
class SSOTDocument:
    file_path: str
    doc_id: str
    title: str
    status: str
    is_canonical: bool
    superseded_by: Optional[str] = None
    content_sha256: str = ""


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


def parse_document_metadata(content: str) -> Dict[str, str]:
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
    status_match = re.search(
        r"^[ \t]*(?:>[ \t]*)?(?:-[ \t]*)?\*\*Status:\*\*[ \t]+([^\n]+)",
        content, flags=re.IGNORECASE | re.MULTILINE,
    )
    if not status_match:
        status_match = re.search(
            r"^#{1,6}[ \t]+Status[ \t]*\n\s*([^\n]+)",
            content, flags=re.IGNORECASE | re.MULTILINE,
        )
    if status_match and "status" not in metadata:
        metadata["status"] = status_match.group(1).strip()

    return metadata


_parse_frontmatter_or_headers = parse_document_metadata


def audit_ssot_registry(
    root_dir: str | Path,
    include_extensions: Tuple[str, ...] = (".md", ".markdown"),
    exclude_dirs: Tuple[str, ...] = (".git", ".pytest_cache", "__pycache__", "site", "_site", "archaeology", "archive", "corpus"),
) -> SSOTReport:
    """Audit the repository to ensure exactly one CANONICAL_SSOT document exists per doc_id."""
    root_path = Path(root_dir)
    registry: Dict[str, List[SSOTDocument]] = {}
    total_docs = 0
    canonical_count = 0
    violations: List[SSOTViolation] = []

    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in include_extensions:
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            try:
                raw_bytes = file_path.read_bytes()
                raw_text = raw_bytes.decode("utf-8").replace("\r\n", "\n")
                meta = parse_document_metadata(raw_text)
                rel_path = str(file_path.relative_to(root_path)).replace("\\", "/")

                doc_id = derive_semantic_document_id(file_path, meta)
                status = meta.get("status", "UNCLASSIFIED")
                classification = classify_status(status if "status" in meta else None)
                is_canonical = classification == "CANONICAL"
                if classification == "UNKNOWN":
                    violations.append(SSOTViolation(
                        doc_id=doc_id, files=[rel_path],
                        description=f"Unrecognized document status under vocabulary {STATUS_VOCABULARY_VERSION}: {status!r}",
                    ))
                if is_canonical:
                    canonical_count += 1

                doc = SSOTDocument(
                    file_path=rel_path,
                    doc_id=doc_id,
                    title=meta.get("title", file_path.stem),
                    status=status,
                    is_canonical=is_canonical,
                    superseded_by=meta.get("superseded_by"),
                    content_sha256=hashlib.sha256(raw_bytes).hexdigest(),
                )

                registry.setdefault(doc_id, []).append(doc)
                total_docs += 1
            except (OSError, UnicodeError) as exc:
                violations.append(SSOTViolation(
                    doc_id=str(file_path), files=[str(file_path)],
                    description=f"Cannot read document: {exc}",
                ))

    for doc_id, docs in registry.items():
        canonicals = [d for d in docs if d.is_canonical]
        if len({doc.content_sha256 for doc in canonicals}) > 1:
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
