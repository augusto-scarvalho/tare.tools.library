"""Compatibility import surface for the canonical HTML contract validator.

The implementation is stdlib-only so repository integrity checks do not depend
on the Pages renderer dependency set.
"""
import validate_canonical_contract as _contract

_VOID = {"area","base","br","col","embed","hr","img","input","link","meta","param","source","track","wbr"}

class _CompatParser(_contract.ContractParser):
    def __init__(self):
        super().__init__()
        self.capture_abstract = False

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        if tag in _VOID and self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_startendtag(self, tag, attrs):
        if tag in _VOID:
            self.handle_starttag(tag, attrs)
        else:
            super().handle_startendtag(tag, attrs)

_contract.ContractParser = _CompatParser
validate_packet = _contract.validate_packet

__all__ = ["validate_packet"]
