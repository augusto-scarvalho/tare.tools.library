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
> Este documento foi descontinuado e substituído pelo seu equivalente canônico:
> 👉 **Canônico:** [{canonical_target}]({canonical_target})
> **Motivo:** {reason}
> **Status:** `ARCHIVED_SUPERSEDED`

---
*Este ponteiro tombstone é mantido para preservar a integridade de links e referências históricas.*
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
                is_tombstone = bool(
                    re.search(r"^#\s+\[TOMBSTONE\]", text, flags=re.MULTILINE)
                    and re.search(
                        r"\*\*Status:\*\*\s+`?ARCHIVED_SUPERSEDED`?",
                        text,
                        flags=re.IGNORECASE,
                    )
                )
                if is_tombstone:
                    total_tombstones += 1
                    # Extract target pointer
                    match = re.search(
                        r"\*\*Canônico:\*\*\s+\[[^\]]+\]\(([^)]+)\)",
                        text,
                        flags=re.IGNORECASE,
                    )
                    if match:
                        target = match.group(1).strip()
                        relative_target = target.lstrip("/")
                        candidates = (
                            root_path / relative_target,
                            file_path.parent / relative_target,
                        )
                        if any(candidate.exists() for candidate in candidates):
                            valid_tombstones += 1
                        else:
                            broken.append((str(file_path.relative_to(root_path)), target))
                    else:
                        broken.append(
                            (str(file_path.relative_to(root_path)), "<missing canonical target>")
                        )
            except Exception:
                continue

    return TombstoneValidationResult(
        total_tombstones=total_tombstones,
        valid_tombstones=valid_tombstones,
        broken_pointers=broken,
    )
