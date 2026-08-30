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


STATUS_VOCABULARY_VERSION = "1.0"
STATUS_CANONICAL = "CANONICAL"
STATUS_NON_CANONICAL = "NON_CANONICAL"
STATUS_UNCLASSIFIED = "UNCLASSIFIED"
STATUS_UNKNOWN = "UNKNOWN"

_CANONICAL_STATUS_MARKERS = frozenset(
    {
        "ACCEPTED",
        "APPROVED",
        "APROVADO",
        "APROVADA",
        "CANONICAL",
        "CANONICAL_SSOT",
        "CANONICA",
        "CANONICO",
        "RATIFIED",
        "RATIFICADA",
        "RATIFICADO",
        "OFFICIAL_SOURCE_OF_TRUTH",
        "SSOT",
    }
)
_NON_CANONICAL_STATUS_MARKERS = frozenset(
    {
        "ACTIVE",
        "ADAPTED",
        "ADOPTED",
        "ARCHIVED",
        "ARCHIVED_SUPERSEDED",
        "CODE_AUDITED",
        "DRAFT",
        "PROPOSTA",
        "PROPOSTO",
        "PROPOSED",
        "RESEARCH",
        "RESOLVED",
        "RESOLVIDO",
        "RETIRED",
        "RUNNING",
        "SUPERSEDED",
        "UNCLASSIFIED",
    }
)


@dataclass
class SSOTDocument:
    file_path: str
    doc_id: str
    title: str
    status: str
    is_canonical: bool
    content_sha256: str
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
    unclassified_documents: List[str] = field(default_factory=list)
    unknown_status_documents: List[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.violations) == 0


def _normalize_status(status: str) -> str:
    decomposed = unicodedata.normalize("NFKD", status)
    ascii_status = decomposed.encode("ascii", "ignore").decode("ascii").upper()
    return re.sub(r"[^A-Z0-9]+", "_", ascii_status).strip("_")


def classify_status(status: Optional[str]) -> str:
    """Classify the closed EN/PT status vocabulary used by Library documents."""
    if status is None or not status.strip():
        return STATUS_UNCLASSIFIED

    normalized = _normalize_status(status)
    terms = set(normalized.split("_"))

    if normalized in _NON_CANONICAL_STATUS_MARKERS or terms & _NON_CANONICAL_STATUS_MARKERS:
        return STATUS_NON_CANONICAL
    if normalized in _CANONICAL_STATUS_MARKERS or terms & _CANONICAL_STATUS_MARKERS:
        return STATUS_CANONICAL
    return STATUS_UNKNOWN


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
        r"^\s*(?:>\s*)?(?:-\s*)?\*\*Status:\*\*\s+([^\n]+)",
        content,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    if status_match and "status" not in metadata:
        metadata["status"] = status_match.group(1).strip()

    return metadata


def derive_semantic_document_id(
    file_path: Path, metadata: Dict[str, str], root_path: Path
) -> str:
    """Derive editorial identity without treating a hash-suffixed copy as new."""
    explicit = metadata.get("doc_id") or metadata.get("id")
    if explicit:
        return explicit.strip().upper()

    stem = re.sub(r"_[0-9a-fA-F]{8,64}$", "", file_path.stem)
    upper_stem = stem.upper()
    if re.fullmatch(r"(?:DECISION|V\d{3,4}|PROPOSAL(?:_ADR\d+)?)", upper_stem):
        title = metadata.get("title", "")
        normalized_title = _normalize_status(title)
        if normalized_title:
            return normalized_title
    if file_path.parent.name.lower() == "adr" or upper_stem.startswith(("ADR-", "DECISION")):
        return upper_stem
    if "specs" in {part.lower() for part in file_path.parts} or upper_stem.startswith("SPEC-"):
        return upper_stem
    if upper_stem.startswith("EXP-"):
        return upper_stem
    return str(file_path.relative_to(root_path)).replace("\\", "/")


# Backward-compatible private alias for callers that imported the old helper.
_parse_frontmatter_or_headers = parse_document_metadata


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
    unclassified_documents: List[str] = []
    unknown_status_documents: List[str] = []
    status_violations: List[SSOTViolation] = []

    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in include_extensions:
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue

            try:
                raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
                meta = parse_document_metadata(raw_text)
                rel_path = str(file_path.relative_to(root_path)).replace("\\", "/")

                doc_id = derive_semantic_document_id(file_path, meta, root_path)
                raw_status = meta.get("status")
                classification = classify_status(raw_status)
                status = raw_status.upper() if raw_status else STATUS_UNCLASSIFIED
                is_canonical = classification == STATUS_CANONICAL
                if is_canonical:
                    canonical_count += 1
                elif classification == STATUS_UNCLASSIFIED:
                    unclassified_documents.append(rel_path)
                elif classification == STATUS_UNKNOWN:
                    unknown_status_documents.append(rel_path)
                    status_violations.append(
                        SSOTViolation(
                            doc_id=doc_id,
                            files=[rel_path],
                            description=(
                                f"Unrecognized status under vocabulary "
                                f"{STATUS_VOCABULARY_VERSION}: {raw_status!r}"
                            ),
                        )
                    )

                doc = SSOTDocument(
                    file_path=rel_path,
                    doc_id=doc_id,
                    title=meta.get("title", file_path.stem),
                    status=status,
                    is_canonical=is_canonical,
                    content_sha256=hashlib.sha256(file_path.read_bytes()).hexdigest(),
                    superseded_by=meta.get("superseded_by"),
                )

                registry.setdefault(doc_id, []).append(doc)
                total_docs += 1
            except Exception:
                continue

    violations: List[SSOTViolation] = list(status_violations)
    for doc_id, docs in registry.items():
        canonicals = [d for d in docs if d.is_canonical]
        canonical_hashes = {doc.content_sha256 for doc in canonicals}
        if len(canonical_hashes) > 1:
            violations.append(
                SSOTViolation(
                    doc_id=doc_id,
                    files=[d.file_path for d in canonicals],
                    description=(
                        "Byte-distinct documents claim CANONICAL_SSOT status for "
                        f"'{doc_id}'"
                    ),
                )
            )

    canonical_by_hash: Dict[str, List[SSOTDocument]] = {}
    for docs in registry.values():
        for doc in docs:
            if doc.is_canonical:
                canonical_by_hash.setdefault(doc.content_sha256, []).append(doc)
    for content_hash, docs in sorted(canonical_by_hash.items()):
        semantic_ids = {doc.doc_id for doc in docs}
        if len(semantic_ids) > 1:
            violations.append(
                SSOTViolation(
                    doc_id=f"SHA256:{content_hash}",
                    files=sorted(doc.file_path for doc in docs),
                    description=(
                        "Identical bytes claim multiple active canonical identities"
                    ),
                )
            )

    return SSOTReport(
        total_documents=total_docs,
        canonical_documents=canonical_count,
        violations=violations,
        unclassified_documents=unclassified_documents,
        unknown_status_documents=unknown_status_documents,
    )
