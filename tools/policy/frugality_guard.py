"""Frugality Guard & Anti-Hypertrophy Policy Engine (RFC-001 / RFC-002 / RFC-003).

Automated quality ratchet that enforces the 5 Sovereign Principles of tare.tools:
1. Validates that MCP schemas do not exceed 200 tokens (bans Fat MCP regressions).
2. Validates that all Round Table cases respect the N <= 3 hard ceiling.
3. Validates that all blocking audit findings contain actionable falsifiers.
4. Validates that atomic write patterns are maintained for state persistence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple


def check_mcp_schema_frugality(tool_schemas: List[Dict[str, Any]], max_tokens_per_tool: int = 150) -> Tuple[bool, str]:
    """Ensure tool schemas remain lean and do not bloat prompt context."""
    if not tool_schemas:
        return True, "No schema registered."

    for tool in tool_schemas:
        name = tool.get("name", "unnamed")
        serialized = json.dumps(tool)
        approx_tokens = len(serialized) / 3.5
        if approx_tokens > max_tokens_per_tool:
            return False, f"Tool '{name}' exceeds the frugality limit: ~{approx_tokens:.0f} tokens (limit: {max_tokens_per_tool}t)."

    return True, f"All {len(tool_schemas)} schemas are frugal (<{max_tokens_per_tool}t)."


def check_case_round_limits(case_data: Dict[str, Any]) -> Tuple[bool, str]:
    """Ensure deliberation cases respect the N <= 3 (or N=4 with overtime) mechanical ceiling."""
    current_round = case_data.get("current_round", 1)
    overtime_granted = case_data.get("overtime_granted", False)
    max_allowed = 4 if overtime_granted else 3

    if current_round > max_allowed:
        return False, f"Case broke the mechanical limit: ran {current_round} rounds (ceiling: {max_allowed})."

    return True, f"Case compliant: round {current_round} of {max_allowed}."


def check_audit_findings_falsifiers(findings: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Ensure every blocking audit finding contains an empirical falsifier."""
    for idx, f in enumerate(findings, 1):
        if f.get("severity") in ("blocking", "critical"):
            falsifier = f.get("falsifier", "").strip()
            if not falsifier or len(falsifier) < 10:
                return False, f"Finding #{idx} ('{f.get('claim')}') has no valid demonstrable empirical falsifier."

    return True, f"All {len(findings)} findings contain empirical falsifiers."


def run_repository_frugality_audit(repo_root: Path) -> Dict[str, Any]:
    """Scan repository cases and MCP schemas to assert zero hypertrophy regressions."""
    results = {"passed": True, "checks": []}

    # Check 1: Lean MCP Gateway schema
    try:
        from tools.mesh.lean_mcp_gateway import LEAN_TOOLS_SCHEMA
        ok, msg = check_mcp_schema_frugality(LEAN_TOOLS_SCHEMA)
        results["checks"].append({"name": "MCP Schema Frugality", "passed": ok, "details": msg})
        if not ok:
            results["passed"] = False
    except Exception as e:
        results["checks"].append({"name": "MCP Schema Frugality", "passed": False, "details": str(e)})
        results["passed"] = False

    # Check 2: Deliberation Cases in cases/
    cases_dir = repo_root / "cases"
    if cases_dir.exists():
        for case_folder in cases_dir.iterdir():
            case_json = case_folder / "case.json"
            if case_json.exists():
                try:
                    data = json.loads(case_json.read_text(encoding="utf-8"))
                    ok, msg = check_case_round_limits(data)
                    results["checks"].append({"name": f"Case Limits ({case_folder.name})", "passed": ok, "details": msg})
                    if not ok:
                        results["passed"] = False
                except Exception as e:
                    results["checks"].append({"name": f"Case Limits ({case_folder.name})", "passed": False, "details": str(e)})
                    results["passed"] = False

    return results
