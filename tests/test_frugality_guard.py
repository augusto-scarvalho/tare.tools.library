"""Unit tests for Frugality Guard policy engine."""
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.policy.frugality_guard import (
    check_audit_findings_falsifiers,
    check_case_round_limits,
    check_mcp_schema_frugality,
    run_repository_frugality_audit,
)


def test_check_mcp_schema_frugality():
    """Lean schemas must pass; bloated schemas must fail."""
    lean = [{"name": "exec", "description": "run", "inputSchema": {"type": "object"}}]
    ok, msg = check_mcp_schema_frugality(lean)
    assert ok is True

    fat = [{"name": "bloated", "description": "a" * 1000, "inputSchema": {"type": "object", "properties": {f"prop_{i}": {"type": "string"} for i in range(50)}}}]
    ok_fat, msg_fat = check_mcp_schema_frugality(fat, max_tokens_per_tool=150)
    assert ok_fat is False
    assert "excede limite de frugalidade" in msg_fat


def test_check_case_round_limits():
    """Cases with <= 3 rounds must pass; cases > 3 without overtime must fail."""
    case_ok = {"current_round": 3, "overtime_granted": False}
    ok, _ = check_case_round_limits(case_ok)
    assert ok is True

    case_fail = {"current_round": 4, "overtime_granted": False}
    ok_fail, msg_fail = check_case_round_limits(case_fail)
    assert ok_fail is False
    assert "violou limite mecânico" in msg_fail

    case_overtime = {"current_round": 4, "overtime_granted": True}
    ok_ot, _ = check_case_round_limits(case_overtime)
    assert ok_ot is True


def test_check_audit_findings_falsifiers():
    """Blocking findings without actionable falsifiers must fail."""
    valid_findings = [
        {"severity": "blocking", "claim": "Lock órfão", "falsifier": "Processo morto deixa lock"}
    ]
    ok, _ = check_audit_findings_falsifiers(valid_findings)
    assert ok is True

    invalid_findings = [
        {"severity": "blocking", "claim": "Estilo feio", "falsifier": ""}
    ]
    ok_inv, msg_inv = check_audit_findings_falsifiers(invalid_findings)
    assert ok_inv is False
    assert "não possui falsificador" in msg_inv


def test_run_repository_frugality_audit():
    """Full repository scan must pass with 100% compliance."""
    res = run_repository_frugality_audit(ROOT)
    assert res["passed"] is True
    assert len(res["checks"]) >= 2
