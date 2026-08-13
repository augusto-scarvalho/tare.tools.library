"""Compatibility import surface for the canonical HTML contract validator.

The implementation is stdlib-only so repository integrity checks do not depend
on the Pages renderer dependency set.
"""
from validate_canonical_contract import validate_packet

__all__ = ["validate_packet"]
