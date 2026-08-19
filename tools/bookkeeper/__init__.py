"""Bookkeeper Package for tare.tools.library.

Provides automated bookkeeping, duplicate detection, SSOT registry validation,
and tombstone lifecycle management across markdown documents.
"""

from .dedup_detector import detect_duplicates, DuplicateReport
from .ssot_registry import audit_ssot_registry, SSOTReport
from .tombstone_manager import apply_tombstone, verify_tombstones

__all__ = [
    "detect_duplicates",
    "DuplicateReport",
    "audit_ssot_registry",
    "SSOTReport",
    "apply_tombstone",
    "verify_tombstones",
]
