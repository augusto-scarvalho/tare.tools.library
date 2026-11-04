"""Tombstone Manager for tare.tools.library.

Creates and validates standardized Tombstone markers for superseded documents,
ensuring incoming references are cleanly redirected to the canonical SSOT.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class TombstoneValidationResult:
    total_tombstones: int
    valid_tombstones: int
    broken_pointers: List[Tuple[str, str]]  # (source_file, target_pointer)

    @property
    def is_healthy(self) -> bool:
        return len(self.broken_pointers) == 0


TOMBSTONE_TEMPLATE = """# [TOMBSTONE] {title}

> [!WARNING]
> **DOCUMENT SUPERSEDED & ARCHIVED**
> This document was retired and replaced by its canonical equivalent:
> 👉 **Canonical:** [{canonical_target}]({canonical_target})
> **Reason:** {reason}
> **Status:** `ARCHIVED_SUPERSEDED`

---
*This tombstone pointer is kept so existing links and references still resolve.*
"""


def apply_tombstone(
    target_path: str | Path,
    canonical_target: str,
    reason: str,
    original_title: str = "",
) -> Path:
    """Apply a standardized tombstone banner to a superseded file."""
    path = Path(target_path)
    if not path.exists():
        raise FileNotFoundError(f"Target file does not exist: {target_path}")

    if not original_title:
        original_title = path.stem.replace("-", " ").replace("_", " ").title()

    content = TOMBSTONE_TEMPLATE.format(
        title=original_title,
        canonical_target=canonical_target,
        reason=reason,
    )

    path.write_text(content, encoding="utf-8")
    return path


def verify_tombstones(
    root_dir: str | Path,
    include_extensions: Tuple[str, ...] = (".md", ".markdown"),
) -> TombstoneValidationResult:
    """Audit all tombstone markers in the directory to verify their targets exist."""
    root_path = Path(root_dir)
    total_tombstones = 0
    valid_tombstones = 0
    broken: List[Tuple[str, str]] = []

    for file_path in root_path.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in include_extensions:
            try:
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                if "TOMBSTONE" in text or "ARCHIVED_SUPERSEDED" in text:
                    total_tombstones += 1
                    # Extract target pointer
                    # "Canônico" is the legacy Portuguese label of older tombstones.
                    match = re.search(r"👉\s+\*\*(?:Canonical|Canônico):\*\*\s+\[([^\]]+)\]\(([^)]+)\)", text)
                    if match:
                        target = match.group(2).strip()
                        target_file = root_path / target.lstrip("/")
                        if target_file.exists():
                            valid_tombstones += 1
                        else:
                            broken.append((str(file_path.relative_to(root_path)), target))
                    else:
                        valid_tombstones += 1  # Standard marker without explicit target
            except Exception:
                continue

    return TombstoneValidationResult(
        total_tombstones=total_tombstones,
        valid_tombstones=valid_tombstones,
        broken_pointers=broken,
    )
