"""Deduplication Detector for markdown documents in tare.tools.library."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Dict, Set


@dataclass
class DuplicateMatch:
    file_a: str
    file_b: str
    similarity_score: float
    is_exact: bool
    overlap_tokens: int


@dataclass
class DuplicateReport:
    total_files_scanned: int
    duplicates_found: List[DuplicateMatch] = field(default_factory=list)
    has_exact_duplicates: bool = False
    has_near_duplicates: bool = False

    @property
    def is_clean(self) -> bool:
        return len(self.duplicates_found) == 0


def _normalize_text(content: str) -> str:
    """Strip YAML frontmatter, markdown codeblocks, links, and normalize whitespace."""
    # Remove YAML frontmatter if present
    content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.DOTALL)
    # Remove code blocks
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    # Remove markdown link URLs
    content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content)
    # Lowercase and keep alphanumeric and spaces
    content = re.sub(r"[^\w\s]", " ", content.lower())
    # Collapse multiple whitespaces
    return " ".join(content.split())


def _get_shingles(text: str, k: int = 3) -> Set[str]:
    """Generate k-word shingles for Jaccard similarity computation."""
    words = text.split()
    if len(words) < k:
        return set(words)
    return {" ".join(words[i : i + k]) for i in range(len(words) - k + 1)}


def compute_similarity(text_a: str, text_b: str) -> float:
    """Compute Jaccard similarity between two texts based on word 3-shingles."""
    if text_a == text_b:
        return 1.0
    shingles_a = _get_shingles(text_a)
    shingles_b = _get_shingles(text_b)
    if not shingles_a or not shingles_b:
        return 0.0
    intersection = len(shingles_a.intersection(shingles_b))
    union = len(shingles_a.union(shingles_b))
    return intersection / union if union > 0 else 0.0


def detect_duplicates(
    root_dir: str | Path,
    similarity_threshold: float = 0.70,
    include_extensions: Tuple[str, ...] = (".md", ".markdown"),
    exclude_dirs: Tuple[str, ...] = (".git", ".pytest_cache", "__pycache__", "site", "_site"),
) -> DuplicateReport:
    """Scan a directory for markdown files and identify exact or near duplicates."""
    root_path = Path(root_dir)
    file_contents: Dict[str, str] = {}

    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in include_extensions:
            # Check exclusions
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            try:
                raw_text = file_path.read_text(encoding="utf-8", errors="ignore")
                normalized = _normalize_text(raw_text)
                if len(normalized) > 50:  # Ignore tiny stub files
                    rel_path = str(file_path.relative_to(root_path)).replace("\\", "/")
                    file_contents[rel_path] = normalized
            except Exception:
                continue

    file_keys = sorted(file_contents.keys())
    duplicates: List[DuplicateMatch] = []
    has_exact = False
    has_near = False

    for i in range(len(file_keys)):
        for j in range(i + 1, len(file_keys)):
            fa = file_keys[i]
            fb = file_keys[j]
            content_a = file_contents[fa]
            content_b = file_contents[fb]

            score = compute_similarity(content_a, content_b)
            if score >= similarity_threshold:
                is_exact = (score >= 0.99)
                if is_exact:
                    has_exact = True
                else:
                    has_near = True

                shingles_a = _get_shingles(content_a)
                shingles_b = _get_shingles(content_b)
                overlap = len(shingles_a.intersection(shingles_b))

                duplicates.append(
                    DuplicateMatch(
                        file_a=fa,
                        file_b=fb,
                        similarity_score=round(score, 4),
                        is_exact=is_exact,
                        overlap_tokens=overlap,
                    )
                )

    return DuplicateReport(
        total_files_scanned=len(file_contents),
        duplicates_found=duplicates,
        has_exact_duplicates=has_exact,
        has_near_duplicates=has_near,
    )
