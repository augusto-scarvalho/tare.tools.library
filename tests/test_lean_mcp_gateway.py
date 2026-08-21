"""Unit tests for Lean MCP Gateway (RFC-002 & RFC-005 / ADR-063 & ADR-064)."""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.mesh.lean_mcp_gateway import (
    LEAN_TOOLS_SCHEMA,
    handle_exec_command,
    handle_read_resource,
    process_jsonrpc_message,
)


@pytest.mark.verifies("RFC-005-REQ-MCP-001")
def test_lean_tools_schema_byte_budget():
    """Schema must contain strictly 2 tools and be frugal (<600 bytes physical budget)."""
    assert len(LEAN_TOOLS_SCHEMA) == 2
    tool_names = {t["name"] for t in LEAN_TOOLS_SCHEMA}
    assert tool_names == {"exec_command", "read_resource"}

    serialized = json.dumps(LEAN_TOOLS_SCHEMA, ensure_ascii=False)
    # Physical size in bytes:
    assert len(serialized.encode("utf-8")) < 600


@pytest.mark.verifies("RFC-005-REQ-MCP-002")
def test_initialize_handshake():
    """Server must respond to MCP initialize request."""
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    resp = process_jsonrpc_message(req)
    assert resp is not None
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "tare.tools.lean-mcp-gateway"
    assert "tools" in resp["result"]["capabilities"]


@pytest.mark.verifies("RFC-005-REQ-MCP-003")
def test_tools_list():
    """Server must return the 2 lean tools on tools/list."""
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    resp = process_jsonrpc_message(req)
    assert resp is not None
    assert resp["id"] == 2
    tools = resp["result"]["tools"]
    assert len(tools) == 2


@pytest.mark.verifies("RFC-005-REQ-MCP-004")
def test_exec_command_argv_list_telemetry():
    """Command execution via argv list returns structured telemetry envelope."""
    cmd = [sys.executable, "-c", "print('hello lean mcp')"]
    resp = handle_exec_command({"command": cmd})
    assert resp["isError"] is False
    telemetry = json.loads(resp["content"][0]["text"])
    assert telemetry["exit_code"] == 0
    assert "hello lean mcp" in telemetry["stdout"]
    assert "duration_ms" in telemetry
    assert telemetry["timed_out"] is False


@pytest.mark.verifies("RFC-005-REQ-MCP-005")
def test_exec_command_realpath_confinement():
    """CWD validation fails closed if outside allowed workspace root."""
    with tempfile.TemporaryDirectory() as root_dir, tempfile.TemporaryDirectory() as outside_dir:
        cmd = [sys.executable, "-c", "print('confinement test')"]
        
        # Valid inside root
        resp_ok = handle_exec_command({"command": cmd, "cwd": root_dir}, allowed_root=Path(root_dir))
        assert resp_ok["isError"] is False

        # Invalid outside root
        resp_err = handle_exec_command({"command": cmd, "cwd": outside_dir}, allowed_root=Path(root_dir))
        assert resp_err["isError"] is True
        assert "fora do workspace" in resp_err["content"][0]["text"]


@pytest.mark.verifies("RFC-005-REQ-MCP-006")
def test_exec_command_timeout():
    """Command timeout triggers error and timed_out flag."""
    cmd = [sys.executable, "-c", "import time; time.sleep(2)"]
    resp = handle_exec_command({"command": cmd, "timeout_seconds": 0.1})
    assert resp["isError"] is True
    telemetry = json.loads(resp["content"][0]["text"])
    assert telemetry["timed_out"] is True
    assert telemetry["exit_code"] == -1
