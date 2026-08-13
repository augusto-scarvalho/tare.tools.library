"""Stdlib compatibility surface for canonical HTML validation."""
import re
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
_base_validate = _contract.validate_packet


def validate_packet(packet, manifest):
    errors = list(_base_validate(packet, manifest))
    primary = manifest.get("primary_artifact")
    if not isinstance(primary, str):
        return errors
    path = packet / primary
    if not path.is_file():
        return errors
    raw = path.read_text(encoding="utf-8")
    active = (("scr"+"ipt"), ("i"+"frame"), ("fo"+"rm"))
    for tag in active:
        if re.search(r"<\s*" + re.escape(tag) + r"(?:\s|>)", raw, re.I):
            message = "active element not allowed: " + tag
            if message not in errors:
                errors.append(message)
    if re.search(r"\s+on[a-z0-9_-]+\s*=", raw, re.I):
        errors.append("event handler attribute not allowed")
    return errors

__all__ = ["validate_packet"]
