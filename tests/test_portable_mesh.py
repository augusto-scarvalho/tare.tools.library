"""Offline regression coverage for operator-configured mesh installations."""

import io
import json
import os
import shlex
import subprocess
import sys
import zipfile
from unittest.mock import Mock

import pytest

from tools.discovery.discovery import DiscoveryEngine
from tools.mesh.byoc_router import BYOCRouter
from tools.mesh.mesh import MeshClient
from tools.mesh.router import LatencyAwareRouter
from tools.policy.compute_guard import assert_compute_guard, detect_compute_profile


@pytest.fixture(autouse=True)
def isolate_operator_environment(monkeypatch):
    for name in ("TARE_MESH_HOST", "TARE_MESH_USER", "TARE_MESH_REMOTE_ROOT",
                 "TARE_MESH_WSL_DISTRO", "TARE_MESH_DAEMON_START", "TARE_THIN_CLIENT_HOSTNAMES",
                 "LOCAL_LLM_ENDPOINT", "SLOP_ENDPOINT", "LOCAL_EMBED_ENDPOINT", "SLOP_EMBED_ENDPOINT"):
        monkeypatch.delenv(name, raising=False)


def test_mesh_configuration_resolved_at_construction(monkeypatch):
    first = MeshClient()
    monkeypatch.setenv("TARE_MESH_HOST", "compute.example")
    monkeypatch.setenv("TARE_MESH_USER", "operator")
    monkeypatch.setenv("TARE_MESH_REMOTE_ROOT", "/srv/Library checkout")
    monkeypatch.setenv("TARE_MESH_WSL_DISTRO", "Research Linux")
    configured = MeshClient()
    assert first.substrate_host == "localhost"
    assert first.substrate_user is None
    assert configured.substrate_host == "compute.example"
    assert configured.substrate_user == "operator"
    assert configured.remote_root == "/srv/Library checkout"
    assert configured.wsl_distro == "Research Linux"
    selected = MeshClient("other.example", "", remote_root="/opt/library", wsl_distro="")
    assert selected.substrate_user == ""
    assert selected._ssh_command("echo ok")[5] == "other.example"
    assert selected.remote_root == "/opt/library"
    assert selected.wsl_distro == ""


def test_remote_execution_keeps_quotes_and_selected_target(monkeypatch):
    run = Mock(return_value=Mock(returncode=0))
    monkeypatch.setattr(subprocess, "run", run)
    command = 'python3 -c "print(\"a\")"; echo "reader\'s directory"'
    client = MeshClient("compute.example", "operator")
    assert client.exec(command, stream=False) == 0
    args = run.call_args.args[0]
    assert args[5] == "operator@compute.example"
    assert shlex.split(args[-1]) == ["bash", "-lc", command]
    client.exec("echo ok", node="other.example", stream=False)
    assert run.call_args.args[0][5] == "operator@other.example"


@pytest.mark.skipif(os.name != "nt", reason="Windows command-line parsing")
def test_wsl_execution_passes_one_complete_shell_command():
    import ctypes
    from ctypes import wintypes

    command = 'echo "reader\'s directory" && python3 -c "print(123)"'
    client = MeshClient("compute.example", wsl_distro="Research Linux")
    argc = ctypes.c_int()
    parse = ctypes.windll.shell32.CommandLineToArgvW
    parse.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_int)]
    parse.restype = ctypes.POINTER(wintypes.LPWSTR)
    parsed = parse(client._ssh_command(command)[-1], ctypes.byref(argc))
    try:
        assert [parsed[i] for i in range(argc.value)] == ["wsl", "-d", "Research Linux", "--", "bash", "-lc", command]
    finally:
        ctypes.windll.kernel32.LocalFree(ctypes.cast(parsed, ctypes.c_void_p))


def test_sync_stream_roundtrip_and_private_exclusions(tmp_path, monkeypatch):
    source = tmp_path / "source"
    source.mkdir()
    (source / "code.py").write_text("print('portable')\n", encoding="utf-8")
    (source / "credentials.local.json").write_text('{"fixture": true}', encoding="utf-8")
    (source / ".private").mkdir()
    (source / ".private" / "notes.md").write_text("private fixture", encoding="utf-8")
    destination = tmp_path / "remote 'checkout' with spaces"
    real_run = subprocess.run

    def transport(args, *, stdin, check):
        assert args[5] == "operator@compute.example"
        outer = shlex.split(args[-1])
        assert outer[:2] == ["bash", "-lc"]
        receiver = shlex.split(outer[2])
        assert receiver[:2] == ["python3", "-c"]
        payload = stdin.read()
        with zipfile.ZipFile(io.BytesIO(payload)) as packed:
            assert packed.namelist() == ["code.py"]
        return real_run([sys.executable, "-c", receiver[2]], input=payload, check=check)

    monkeypatch.setattr(subprocess, "run", transport)
    client = MeshClient("compute.example", "operator", remote_root=str(destination))
    assert client.sync(source_dir=str(source)) is True
    assert (destination / "code.py").read_bytes() == (source / "code.py").read_bytes()
    assert not (destination / "credentials.local.json").exists()


def test_sync_failure_closes_local_archive(tmp_path, monkeypatch):
    streams = []

    def transport(args, *, stdin, check):
        streams.append(stdin)
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(subprocess, "run", transport)
    assert MeshClient("compute.example").sync(source_dir=str(tmp_path)) is False
    assert streams[0].closed is True


def test_remote_search_preserves_query_and_remote_checkout(monkeypatch):
    query = 'reader\'s "quoted" question'
    router = LatencyAwareRouter("compute.example", "operator", remote_root="/srv/reader's Library")
    monkeypatch.setattr(router, "probe_substrate_latency", lambda: 10.0)
    output = Mock(return_value=b"results")
    monkeypatch.setattr(subprocess, "check_output", output)
    result = router.route_query(query, top_k=3)
    assert "REMOTE_SUBSTRATE" in result.route
    args = output.call_args.args[0]
    shell_command = shlex.split(args[-1])[2]
    tokens = shlex.split(shell_command)
    assert tokens[:3] == ["cd", "/srv/reader's Library", "&&"]
    assert tokens[3:] == ["python3", "tools/query.py", "--search", query, "--limit", "3", "--force-local"]


def test_explicit_thin_client_with_cuda_is_still_protected(monkeypatch):
    monkeypatch.setenv("TARE_THIN_CLIENT_HOSTNAMES", "another-laptop, MOBILE-LAPTOP")
    monkeypatch.setattr("socket.gethostname", lambda: "mobile-laptop")
    monkeypatch.setattr(subprocess, "run", Mock(return_value=Mock(returncode=0)))
    profile = detect_compute_profile()
    assert profile.is_thin_client and profile.has_local_cuda
    assert profile.recommended_action == "OFFLOAD_TO_SUBSTRATE"
    allowed, message = assert_compute_guard("index", item_count=100)
    assert not allowed
    assert "TARE_MESH_HOST" in message


def test_byoc_and_discovery_resolve_endpoints_after_import(monkeypatch):
    original = BYOCRouter("local")
    monkeypatch.setenv("LOCAL_LLM_ENDPOINT", "http://chat.example:8080/")
    monkeypatch.setenv("LOCAL_EMBED_ENDPOINT", "http://embed.example:8081/")
    router = BYOCRouter("hybrid")
    assert original.current.endpoint == "http://localhost:8080/v1"
    assert BYOCRouter("local").current.endpoint == "http://chat.example:8080/v1"
    assert router.get_role_cascade("indexer_embeddings")[0].endpoint == "http://embed.example:8081"
    assert {target.endpoint for target in router.get_role_cascade("seat_google") if target.kind == "local_gpu"} == {"http://chat.example:8080/v1"}
    endpoints = DiscoveryEngine().list_all()["endpoints"]
    assert endpoints["local_chat_model"]["url"] == "http://chat.example:8080"
    assert endpoints["local_embed_model"]["url"] == "http://embed.example:8081"


def test_shared_server_does_not_get_duplicate_api_prefix(monkeypatch):
    monkeypatch.setenv("LOCAL_LLM_ENDPOINT", "http://chat.example:8080/v1/")
    assert BYOCRouter("local").current.endpoint == "http://chat.example:8080/v1"


def test_governance_endpoint_uses_configuration_without_a_live_vote(monkeypatch):
    from tools.governance import round_table_engine as engine

    monkeypatch.setenv("LOCAL_LLM_ENDPOINT", "http://chat.example:8080")
    call = Mock(return_value={"status": "unavailable-fixture"})
    monkeypatch.setattr(engine, "_call_local_gpu", call)
    engine.dispatch_seat_universal("fixture", "fixture", "fixture", offline_mode=True)
    assert call.call_args.args[-1] == "http://chat.example:8080/v1"


def test_daemon_requires_existing_model_command_before_remote_execution(monkeypatch):
    client = MeshClient("compute.example")
    execute = Mock()
    monkeypatch.setattr(client, "exec", execute)
    assert "TARE_MESH_DAEMON_START" in client.daemon("start")["error"]
    execute.assert_not_called()
