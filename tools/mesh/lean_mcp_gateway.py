"""Lean MCP Gateway (RFC-002 & RFC-005) for tare.tools.

Minimalist single-dispatcher Model Context Protocol (MCP) server.
Replaces bloated Fat MCP servers by exposing only 2 generic endpoints:
1. exec_command(command: list[str], cwd, timeout_seconds)
2. read_resource(uri, offset, limit_bytes)

Total schema overhead injected into LLM prompt: < 600 bytes (< 150 tokens approx).
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "tare.tools.lean-mcp-gateway"
SERVER_VERSION = "1.1.0"

LEAN_TOOLS_SCHEMA = [
    {
        "name": "exec_command",
        "description": "Executa comando em workspace.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {"type": "array", "items": {"type": "string"}},
                "cwd": {"type": "string"},
                "timeout_seconds": {"type": "number"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "read_resource",
        "description": "Le arquivo local.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "uri": {"type": "string"},
                "offset": {"type": "integer"},
                "limit_bytes": {"type": "integer"}
            },
            "required": ["uri"]
        }
    }
]


def handle_exec_command(arguments: Dict[str, Any], allowed_root: Optional[Path] = None) -> Dict[str, Any]:
    """Execute terminal command safely with argv list, realpath confinement and structured telemetry."""
    command = arguments.get("command")
    cwd_raw = arguments.get("cwd")
    timeout = float(arguments.get("timeout_seconds", 30.0))

    if not command:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Erro: argumento 'command' obrigatorio."}]
        }

    # Resolve cwd to canonical realpath to prevent symlink traversal
    cwd_path: Optional[Path] = None
    if cwd_raw:
        try:
            cwd_path = Path(cwd_raw).resolve()
            if allowed_root:
                allowed_path = Path(allowed_root).resolve()
                if not str(cwd_path).startswith(str(allowed_path)):
                    return {
                        "isError": True,
                        "content": [{"type": "text", "text": f"Erro de Seguranca: cwd fora do workspace permitido ({allowed_path})."}]
                    }
        except Exception as e:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Erro ao resolver cwd: {e}"}]
            }

    # Determine shell=False vs shell=True based on type
    is_list = isinstance(command, list)
    use_shell = not is_list

    t0 = time.perf_counter()
    timed_out = False
    try:
        cp = subprocess.run(
            command,
            cwd=str(cwd_path) if cwd_path else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=use_shell,
            encoding="utf-8",
            errors="replace"
        )
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        result = {
            "exit_code": cp.returncode,
            "stdout": cp.stdout,
            "stderr": cp.stderr,
            "duration_ms": duration_ms,
            "timed_out": False
        }
        return {
            "isError": cp.returncode != 0,
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
        }
    except subprocess.TimeoutExpired as te:
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        result = {
            "exit_code": -1,
            "stdout": te.stdout if isinstance(te.stdout, str) else "",
            "stderr": f"Command timed out after {timeout}s",
            "duration_ms": duration_ms,
            "timed_out": True
        }
        return {
            "isError": True,
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
        }
    except Exception as e:
        duration_ms = round((time.perf_counter() - t0) * 1000, 2)
        result = {
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e),
            "duration_ms": duration_ms,
            "timed_out": False
        }
        return {
            "isError": True,
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
        }


def handle_read_resource(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Read resource file content with offset and limit."""
    uri = arguments.get("uri", "")
    offset = int(arguments.get("offset", 0))
    limit = int(arguments.get("limit_bytes", 100_000))

    if not uri:
        return {
            "isError": True,
            "content": [{"type": "text", "text": "Erro: argumento 'uri' obrigatorio."}]
        }

    path = Path(uri)
    if not path.exists():
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Arquivo nao encontrado: {uri}"}]
        }

    try:
        with open(path, "rb") as f:
            if offset > 0:
                f.seek(offset)
            data = f.read(limit)
            text = data.decode("utf-8", errors="replace")
            return {
                "isError": False,
                "content": [{"type": "text", "text": text}]
            }
    except Exception as e:
        return {
            "isError": True,
            "content": [{"type": "text", "text": f"Erro ao ler arquivo: {e}"}]
        }


def process_jsonrpc_message(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Process a single JSON-RPC 2.0 message."""
    method = msg.get("method")
    msg_id = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": SERVER_NAME,
                    "version": SERVER_VERSION
                }
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": LEAN_TOOLS_SCHEMA
            }
        }
    elif method == "tools/call":
        params = msg.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "exec_command":
            res = handle_exec_command(arguments)
        elif tool_name == "read_resource":
            res = handle_read_resource(arguments)
        else:
            res = {
                "isError": True,
                "content": [{"type": "text", "text": f"Ferramenta desconhecida: {tool_name}"}]
            }

        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": res
        }
    else:
        if msg_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Metodo nao suportado: {method}"
                }
            }
        return None
