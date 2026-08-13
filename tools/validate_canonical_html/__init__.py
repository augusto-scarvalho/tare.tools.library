"""Compatibility import surface for the canonical HTML contract validator.

The implementation is stdlib-only so repository integrity checks do not depend
on the Pages renderer dependency set.
"""
import validate_canonical_contract as _contract

_original_init = _contract.ContractParser.__init__

def _compat_init(self):
    _original_init(self)
    self.capture_abstract = False

_contract.ContractParser.__init__ = _compat_init
validate_packet = _contract.validate_packet

__all__ = ["validate_packet"]
