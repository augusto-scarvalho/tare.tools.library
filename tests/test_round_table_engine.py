import json
import os
import sys
import tempfile
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.governance.round_table_engine import (
    CaseLock,
    DeliberationStatus,
    QuorumMode,
    compute_quorum_mode,
    evaluate_round_verdict,
    generate_compact_delta,
    get_vault_key,
    is_pid_alive,
    parse_vote_json,
    split_markdown_sections,
    write_json_atomic,
    write_text_atomic,
)


def test_is_pid_alive():
    """Current process PID must be alive; invalid PID must be dead."""
    assert is_pid_alive(os.getpid()) is True
    assert is_pid_alive(9999999) is False
    assert is_pid_alive(-1) is False


def test_atomic_writes():
    """Atomic writers must persist JSON and text safely."""
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "test.json"
        txt_path = Path(tmpdir) / "test.txt"

        data = {"foo": "bar", "num": 42}
        write_json_atomic(json_path, data)
        assert json.loads(json_path.read_text(encoding="utf-8")) == data

        text = "Hello World\nLine 2"
        write_text_atomic(txt_path, text)
        assert txt_path.read_text(encoding="utf-8") == text


def test_case_lock_and_stale_healing():
    """CaseLock must provide mutual exclusion and auto-heal stale locks from dead PIDs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        lock_file = Path(tmpdir) / ".lock"

        # 1. Normal acquire and release
        with CaseLock(lock_file):
            assert lock_file.exists()
            content = json.loads(lock_file.read_text(encoding="utf-8"))
            assert content["pid"] == os.getpid()
        assert not lock_file.exists()

        # 2. Stale lock healing (simulating a dead PID)
        stale_data = {"pid": 9999999, "timestamp": time.time() - 1000}
        lock_file.write_text(json.dumps(stale_data), encoding="utf-8")

        with CaseLock(lock_file):
            assert lock_file.exists()
            content = json.loads(lock_file.read_text(encoding="utf-8"))
            assert content["pid"] == os.getpid()
        assert not lock_file.exists()


def test_split_markdown_sections_with_code_fences():
    """Markdown section splitter must ignore ## inside code blocks."""
    md_content = """# Master Document
Preamble text.

## 1. Escopo Principal
Texto da seção 1.

```python
## Isto é um comentário em python, não uma seção
def foo():
    pass
```

## 2. Invariantes
Texto da seção 2.
"""
    sections = split_markdown_sections(md_content)
    
    assert "Preamble" in sections
    assert "1. Escopo Principal" in sections
    assert "2. Invariantes" in sections
    assert "Isto é um comentário em python, não uma seção" not in sections
    
    sec1_text, sec1_hash = sections["1. Escopo Principal"]
    assert "def foo():" in sec1_text
    assert len(sec1_hash) == 64


def test_generate_compact_delta():
    """Compact delta must detect added, modified, and deleted sections."""
    prev_md = """## 1. Escopo
Texto original.

## 2. Removida
Texto a ser removido.
"""
    curr_md = """## 1. Escopo
Texto modificado com novas diretrizes.

## 3. Nova Secao
Texto recém adicionado.
"""
    delta = generate_compact_delta(prev_md, curr_md)

    assert delta["1. Escopo"]["change_type"] == "MODIFIED"
    assert "prev_hash" in delta["1. Escopo"]
    assert "curr_hash" in delta["1. Escopo"]

    assert delta["2. Removida"]["change_type"] == "DELETED"
    assert delta["3. Nova Secao"]["change_type"] == "ADDED"


def test_parse_vote_json_with_nonce():
    """Vote parser must extract valid JSON and verify Sentinel Nonce correlation."""
    nonce = "123e4567-e89b-12d3-a456-426614174000"
    raw_response = f"""Aqui está a análise técnica:
```json
{{
  "seat": "google",
  "execution_nonce": "{nonce}",
  "verdict": "APPROVE",
  "summary": "Tudo validado com sucesso."
}}
```
Fim do parecer.
"""
    parsed = parse_vote_json(raw_response, nonce)
    assert parsed is not None
    assert parsed["seat"] == "google"
    assert parsed["verdict"] == "APPROVE"
    assert parsed["execution_nonce"] == nonce

    # Invalid nonce -> must return None
    assert parse_vote_json(raw_response, "invalid-nonce") is None


def test_compute_quorum_mode():
    """Quorum calculation must distinguish frontier, degraded, and local advisory."""
    # 1. 3 Titulares (Google, Anthropic, OpenAI)
    votes_frontier = {
        "google": {"provider": "google", "status": "OK"},
        "anthropic": {"provider": "anthropic", "status": "OK"},
        "openai": {"provider": "openai", "status": "OK"},
    }
    assert compute_quorum_mode(votes_frontier) == QuorumMode.FRONTIER_UNANIMOUS

    # 2. 2 Titulares + 1 Backup Comercial (Kimi)
    votes_degraded = {
        "google": {"provider": "google", "status": "OK"},
        "anthropic": {"provider": "kimi_backup", "status": "OK"},
        "openai": {"provider": "openai", "status": "OK"},
    }
    assert compute_quorum_mode(votes_degraded) == QuorumMode.DEGRADED_MIXED

    # 3. Presença de GPU local
    votes_local = {
        "google": {"provider": "google", "status": "OK"},
        "anthropic": {"provider": "local_gpu", "status": "OK"},
        "openai": {"provider": "openai", "status": "OK"},
    }
    assert compute_quorum_mode(votes_local) == QuorumMode.LOCAL_ADVISORY

    # 4. Falha de Quórum (<2 assentos)
    votes_failed = {
        "google": {"provider": "google", "status": "OK"},
        "anthropic": {"provider": "anthropic", "status": "FAILED"},
        "openai": {"provider": "openai", "status": "TIMEOUT"},
    }
    assert compute_quorum_mode(votes_failed) == QuorumMode.HELD_UNAVAILABLE


def test_evaluate_round_verdict_limits():
    """Evaluate FSM state transitions and mechanical limits (N <= 3, Overtime N=4)."""
    approve_votes = {
        "s1": {"status": "OK", "vote": {"verdict": "APPROVE"}},
        "s2": {"status": "OK", "vote": {"verdict": "APPROVE"}},
        "s3": {"status": "OK", "vote": {"verdict": "APPROVE"}},
    }
    status, reason = evaluate_round_verdict(approve_votes, current_round=1)
    assert status == DeliberationStatus.APPROVED

    split_votes = {
        "s1": {"status": "OK", "vote": {"verdict": "APPROVE"}},
        "s2": {"status": "OK", "vote": {"verdict": "REJECT"}},
        "s3": {"status": "OK", "vote": {"verdict": "APPROVE"}},
    }
    # Round 1 with split -> REVISED
    status, _ = evaluate_round_verdict(split_votes, current_round=1)
    assert status == DeliberationStatus.REVISED

    # Round 3 with split -> HELD_PROGRESS_REVIEW (Human Scorecard)
    status, _ = evaluate_round_verdict(split_votes, current_round=3, overtime_granted=False)
    assert status == DeliberationStatus.HELD_PROGRESS_REVIEW

    # Round 3 with overtime_granted -> Still REVISED (Allows round 4)
    status, _ = evaluate_round_verdict(split_votes, current_round=3, overtime_granted=True)
    assert status == DeliberationStatus.REVISED

    # Round 4 with overtime_granted -> HELD_OVERTIME_EXHAUSTED
    status, _ = evaluate_round_verdict(split_votes, current_round=4, overtime_granted=True)
    assert status == DeliberationStatus.HELD_OVERTIME_EXHAUSTED


def test_generate_dialectical_brief():
    """Dialectical brief generator must separate consensuses, tensions with falsifiers, and discards."""
    from tools.governance.round_table_engine import generate_dialectical_brief

    votes = {
        "google": {
            "status": "OK",
            "vote": {
                "verdict": "APPROVE",
                "strengths": ["Zero alucinação", "Performance O(n)"],
                "issues": [],
                "recommendations": ["Adicionar telemetria"]
            }
        },
        "anthropic": {
            "status": "OK",
            "vote": {
                "verdict": "REVISE",
                "strengths": ["Boa cobertura"],
                "issues": [
                    {
                        "severity": "blocking",
                        "claim": "Condição de corrida no WAL",
                        "falsifier": "Dois leitores simultâneos"
                    },
                    {
                        "severity": "non-blocking",
                        "claim": "Formatação de tabela",
                        "falsifier": "Quebra de linha no markdown"
                    }
                ],
                "recommendations": []
            }
        },
        "openai": {
            "status": "OK",
            "vote": {
                "verdict": "APPROVE",
                "strengths": ["Frugalidade de tokens"],
                "issues": [],
                "recommendations": []
            }
        }
    }

    brief = generate_dialectical_brief(votes)
    assert len(brief["dialectical_tensions"]) == 1
    assert brief["dialectical_tensions"][0]["claim"] == "Condição de corrida no WAL"
    assert brief["dialectical_tensions"][0]["falsifier"] == "Dois leitores simultâneos"
    assert len(brief["discard_candidates"]) == 1
    assert "Formatação de tabela" in brief["discard_candidates"][0]


def test_execute_mediator_synthesis():
    """Mediator synthesis must render 3-pillar structured markdown with Via Negativa."""
    from tools.governance.round_table_engine import execute_mediator_synthesis

    brief = {
        "established_consensuses": ["Parser de AST validado"],
        "dialectical_tensions": [
            {"seat": "anthropic", "claim": "Lock órfão em kill -9", "falsifier": "Matar processo e verificar"}
        ],
        "discard_candidates": ["[google] Trocar cor de log (Classificado como não-bloqueante)"],
        "recommendations": []
    }

    synthesis = execute_mediator_synthesis(
        anchor_md="# Master Anchor",
        dialectical_brief=brief,
        compact_delta={},
        round_num=2
    )

    assert "SÍNTESE DO MEDIADOR CONSTITUCIONAL — RODADA 2" in synthesis
    assert "Parser de AST validado" in synthesis
    assert "Lock órfão em kill -9" in synthesis
    assert "Trocar cor de log" in synthesis


def test_evaluate_audit_verdict_and_report():
    """Audit mode must evaluate critical findings and render standard AUDIT_REPORT.md."""
    from tools.governance.round_table_engine import (
        AuditStatus,
        evaluate_audit_verdict,
        generate_audit_report,
    )

    # 1. Test Clean Pass
    clean_votes = {
        "google": {"status": "OK", "provider": "google", "model": "gemini-3.7-flash", "vote": {"verdict": "PASS", "summary": "Tudo ok", "issues": []}},
        "openai": {"status": "OK", "provider": "openai", "model": "gpt-5.6-sol", "vote": {"verdict": "PASS", "summary": "Conforme", "issues": []}},
    }
    status, findings, reason = evaluate_audit_verdict(clean_votes)
    assert status == AuditStatus.AUDIT_APPROVED
    assert len(findings) == 0

    report_clean = generate_audit_report(
        case_id="AUDIT-2026-08-20-001",
        target_artifacts=["tools/mesh/lean_mcp_gateway.py"],
        audit_votes=clean_votes,
        status=status,
        reason=reason,
        critical_findings=findings
    )
    assert "LAUDO DE AUDITORIA FORMAL: AUDIT-2026-08-20-001" in report_clean
    assert "AUDIT_APPROVED" in report_clean
    assert "Nenhuma inconformidade crítica" in report_clean

    # 2. Test Critical Finding with Reproduction Test
    failing_votes = {
        "google": {"status": "OK", "provider": "google", "model": "gemini-3.7-flash", "vote": {"verdict": "PASS", "summary": "Tudo ok", "issues": []}},
        "red_team": {
            "status": "OK",
            "provider": "local_gpu",
            "model": "qwen36-fable-tc.gguf",
            "vote": {
                "verdict": "FAIL",
                "summary": "Vulnerabilidade identificada",
                "issues": [
                    {
                        "severity": "critical",
                        "claim": "Path Traversal em read_resource",
                        "falsifier": "Passar ../../etc/passwd deve ser rejeitado",
                        "reproduction_test": "pytest tests/test_security.py",
                        "remedy": "Adicionar os.path.realpath"
                    }
                ]
            }
        }
    }
    status_fail, findings_fail, reason_fail = evaluate_audit_verdict(failing_votes)
    assert status_fail == AuditStatus.AUDIT_HELD_REMEDIATION_REQUIRED
    assert len(findings_fail) == 1
    assert findings_fail[0]["claim"] == "Path Traversal em read_resource"

    report_fail = generate_audit_report(
        case_id="AUDIT-2026-08-20-002",
        target_artifacts=["tools/mesh/lean_mcp_gateway.py"],
        audit_votes=failing_votes,
        status=status_fail,
        reason=reason_fail,
        critical_findings=findings_fail
    )
    assert "AUDIT_HELD_REMEDIATION_REQUIRED" in report_fail
    assert "Path Traversal em read_resource" in report_fail
    assert "pytest tests/test_security.py" in report_fail


def test_anti_sybil_quorum_rejection_on_duplicate_model():
    """compute_quorum_mode MUST return HELD_UNAVAILABLE if two seats share the exact same model."""
    from tools.governance.round_table_engine import QuorumMode, compute_quorum_mode

    # Sybil attack: 2 seats answered by the same backup model (e.g. z-ai/glm-5.2)
    sybil_votes = {
        "google": {"status": "OK", "provider": "google", "model": "gemini-3.7-flash", "vote": {"verdict": "APPROVE"}},
        "openai": {"status": "OK", "provider": "nim_backup_openai", "model": "z-ai/glm-5.2", "vote": {"verdict": "APPROVE"}},
        "anthropic": {"status": "OK", "provider": "nim_backup_anthropic", "model": "z-ai/glm-5.2", "vote": {"verdict": "APPROVE"}},
    }
    mode = compute_quorum_mode(sybil_votes)
    assert mode == QuorumMode.HELD_UNAVAILABLE, "Quorum mode MUST fail to HELD_UNAVAILABLE when duplicate models are present"

    # Legitimate distinct models:
    distinct_votes = {
        "google": {"status": "OK", "provider": "google", "model": "gemini-3.7-flash", "vote": {"verdict": "APPROVE"}},
        "openai": {"status": "OK", "provider": "openai", "model": "gpt-5.6-sol", "vote": {"verdict": "APPROVE"}},
        "anthropic": {"status": "OK", "provider": "anthropic", "model": "claude-fable-5-high", "vote": {"verdict": "APPROVE"}},
    }
    distinct_mode = compute_quorum_mode(distinct_votes)
    assert distinct_mode == QuorumMode.FRONTIER_UNANIMOUS


def test_anti_sybil_verdict_rejection_on_duplicate_model():
    """evaluate_round_verdict MUST return HELD_UNAVAILABLE and identify duplicate model on Sybil collision."""
    from tools.governance.round_table_engine import (
        DeliberationStatus,
        evaluate_round_verdict,
    )

    sybil_votes = {
        "google": {"status": "OK", "provider": "google", "model": "gemini-3.7-flash", "vote": {"verdict": "APPROVE"}},
        "openai": {"status": "OK", "provider": "nim_backup_openai", "model": "z-ai/glm-5.2", "vote": {"verdict": "APPROVE"}},
        "anthropic": {"status": "OK", "provider": "nim_backup_anthropic", "model": "z-ai/glm-5.2", "vote": {"verdict": "APPROVE"}},
    }
    status, reason = evaluate_round_verdict(sybil_votes, current_round=1)
    assert status == DeliberationStatus.HELD_UNAVAILABLE
    assert "Violação Anti-Sybil" in reason
    assert "z-ai/glm-5.2" in reason


def test_anti_sybil_model_exclusion_in_dispatch():
    """dispatch_seat_universal MUST respect excluded_models to avoid Sybil collisions."""
    from tools.governance.round_table_engine import (
        PIN_LOCAL_RED_TEAM,
        dispatch_seat_universal,
    )

    # When z-ai/glm-5.2 and qwen38 are excluded, local fallback uses PIN_LOCAL_RED_TEAM
    res = dispatch_seat_universal(
        seat_name="anthropic",
        prompt_text="test",
        nonce="nonced",
        offline_mode=True,
        local_gpu_url="http://invalid-local-url:9999/v1",
        excluded_models={"qwen38-27b.gguf"}
    )
    # Even if offline fails to connect, the attempted model pin must be the alternate Red Team pin!
    assert res.get("provider") == "local_gpu"
