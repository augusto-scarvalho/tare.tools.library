"""Emergency Halt Protocol (RFC-003 & RFC-005 / ADR-062 & ADR-064)."""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class EmergencyHaltReceipt:
    case_id: str
    reason: str
    violation_class: str  # e.g., "SECURITY_HAZARD", "PHYSICAL_IMPOSSIBILITY", "CONTRACT_CONTRADICTION"
    falsifier_evidence: str
    recommendation: str
    timestamp_utc: str = ""
    agent_seat: str = "executor"

    def __post_init__(self) -> None:
        if not self.timestamp_utc:
            self.timestamp_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def write_to_file(self, target_path: Path) -> Path:
        target_path = Path(target_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return target_path

    @classmethod
    def load_from_file(cls, path: Path) -> EmergencyHaltReceipt:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)


def emit_halt(
    case_id: str,
    reason: str,
    violation_class: str,
    falsifier_evidence: str,
    recommendation: str,
    output_dir: Path = Path("."),
) -> Path:
    receipt = EmergencyHaltReceipt(
        case_id=case_id,
        reason=reason,
        violation_class=violation_class,
        falsifier_evidence=falsifier_evidence,
        recommendation=recommendation,
    )
    receipt_file = Path(output_dir) / "HALT_RECEIPT.json"
    return receipt.write_to_file(receipt_file)
