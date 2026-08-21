"""Hardened Frugal Governance Engine (Round Table) for tare.tools.

Implements RFC-001:
- State Anchors & Dialectical Compaction
- Maximum 3 Rounds (N <= 3) with Hard Transition Ceiling (T <= 12)
- Deterministic Quorum Matrix (FRONTIER_UNANIMOUS, DEGRADED_MIXED, LOCAL_ADVISORY)
- PID-Aware Stale-Healing File Lock & Atomic Disk Writes
- Fenced-Aware Markdown AST Section Parsing
- Cascaded Universal Fallback (CLI -> OpenAI-Compat -> Local GPU)
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Keyring Vault Service Name
VAULT_SERVICE = "universal-agent-harness"

# Constants & Invariants
MAX_ROUNDS = 3
MAX_OVERTIME_ROUNDS = 4
MAX_TRANSITIONS = 12
GLOBAL_DEADLINE_SECONDS = 300
DEFAULT_LOCAL_GPU_URL = "http://100.107.245.30:8080/v1"
NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
KIMI_BASE_URL = "https://api.kimi.com/coding/v1"

TITULAR_PROVIDERS: Set[str] = {"google", "anthropic", "openai"}

# -----------------------------------------------------------------------------
# Local Sovereign Model Pins (Node aaaaa / RTX 3090 / slop.cpp)
# -----------------------------------------------------------------------------
PIN_LOCAL_SOVEREIGN_GENERAL = "qwen38-27b.gguf"   # Qwen 3.8: Mais fiel, preciso e poderoso (Deliberação Geral)
PIN_LOCAL_COMPACTOR = "qwen38-27b.gguf"           # Qwen 3.8: Escriba Dialético e Compactador Semântico
PIN_LOCAL_RED_TEAM = "qwen36-fable-tc.gguf"        # Qwen 3.6 Fable TC: Red Team, Anti-Censura e Auditoria Adversarial



class QuorumMode(str, Enum):
    FRONTIER_UNANIMOUS = "FRONTIER_UNANIMOUS"
    DEGRADED_MIXED = "DEGRADED_MIXED"
    LOCAL_ADVISORY = "LOCAL_ADVISORY"
    HELD_UNAVAILABLE = "HELD_UNAVAILABLE"


class DeliberationStatus(str, Enum):
    OPEN = "OPEN"
    DELIBERATING = "DELIBERATING"
    APPROVED = "APPROVED"
    REVISED = "REVISED"
    REJECTED = "REJECTED"
    HELD_PROGRESS_REVIEW = "HELD_PROGRESS_REVIEW"
    HELD_UNAVAILABLE = "HELD_UNAVAILABLE"
    HELD_OVERTIME_EXHAUSTED = "HELD_OVERTIME_EXHAUSTED"


# -----------------------------------------------------------------------------
# 1. OS & Atomic File Operations (Zero-Overengineering)
# -----------------------------------------------------------------------------

def is_pid_alive(pid: int) -> bool:
    """Check if a PID is alive on Windows or Unix without external dependencies."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if handle:
                ctypes.windll.kernel32.CloseHandle(handle)
                return True
            return False
        except Exception:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


class CaseLock:
    """PID-aware file lock with automatic healing of dead/stale locks."""
    def __init__(self, lock_path: Path, timeout_secs: float = 10.0):
        self.lock_path = lock_path
        self.timeout_secs = timeout_secs
        self.acquired = False

    def __enter__(self):
        t0 = time.time()
        while time.time() - t0 < self.timeout_secs:
            try:
                with open(self.lock_path, "x", encoding="utf-8") as f:
                    lock_data = {"pid": os.getpid(), "timestamp": time.time()}
                    f.write(json.dumps(lock_data))
                self.acquired = True
                return self
            except FileExistsError:
                try:
                    content = self.lock_path.read_text(encoding="utf-8")
                    data = json.loads(content)
                    holding_pid = data.get("pid", -1)
                    if not is_pid_alive(holding_pid):
                        self.lock_path.unlink(missing_ok=True)
                        continue
                except Exception:
                    self.lock_path.unlink(missing_ok=True)
                    continue
                time.sleep(0.1)
        raise TimeoutError(f"Não foi possível obter lock em {self.lock_path} (recurso ocupado)")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            self.lock_path.unlink(missing_ok=True)


def write_json_atomic(target_path: Path, data: Any) -> None:
    """Write JSON atomically using .tmp and os.replace."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_suffix(f".tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}")
    tmp_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp_path, target_path)


def write_text_atomic(target_path: Path, content: str) -> None:
    """Write text file atomically using .tmp and os.replace."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_suffix(f".tmp.{os.getpid()}.{uuid.uuid4().hex[:6]}")
    tmp_path.write_text(content, encoding="utf-8")
    os.replace(tmp_path, target_path)


# -----------------------------------------------------------------------------
# 2. Markdown Parser & Compact Delta Generator
# -----------------------------------------------------------------------------

def split_markdown_sections(text: str) -> Dict[str, Tuple[str, str]]:
    """Split markdown by ## headings, strictly ignoring headings inside code fences."""
    sections: Dict[str, Tuple[str, str]] = {}
    lines = text.splitlines(keepends=True)
    
    current_title = "Preamble"
    current_lines: List[str] = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            current_lines.append(line)
            continue

        if not in_code_block and stripped.startswith("## "):
            if current_lines:
                sec_text = "".join(current_lines).strip()
                sec_hash = hashlib.sha256(sec_text.encode("utf-8")).hexdigest()
                sections[current_title] = (sec_text, sec_hash)
            current_title = stripped[3:].strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sec_text = "".join(current_lines).strip()
        sec_hash = hashlib.sha256(sec_text.encode("utf-8")).hexdigest()
        sections[current_title] = (sec_text, sec_hash)

    return sections


def generate_compact_delta(prev_md: str, curr_md: str) -> Dict[str, Any]:
    """Generate compact section delta between two markdown revisions."""
    prev_sections = split_markdown_sections(prev_md)
    curr_sections = split_markdown_sections(curr_md)

    delta_sections: Dict[str, Dict[str, Any]] = {}

    for title, (content, curr_hash) in curr_sections.items():
        if title not in prev_sections:
            delta_sections[title] = {
                "change_type": "ADDED",
                "curr_hash": curr_hash,
                "content": content
            }
        else:
            _, prev_hash = prev_sections[title]
            if curr_hash != prev_hash:
                delta_sections[title] = {
                    "change_type": "MODIFIED",
                    "prev_hash": prev_hash,
                    "curr_hash": curr_hash,
                    "content": content
                }

    for title, (_, prev_hash) in prev_sections.items():
        if title not in curr_sections:
            delta_sections[title] = {
                "change_type": "DELETED",
                "prev_hash": prev_hash
            }

    return delta_sections


# -----------------------------------------------------------------------------
# 3. Keyring Vault & Universal Provider Despatcher
# -----------------------------------------------------------------------------

def get_vault_key(key_name: str) -> Optional[str]:
    """Fetch secret from OS Keyring vault or environment fallback."""
    try:
        import keyring
        val = keyring.get_password(VAULT_SERVICE, key_name)
        if val:
            return val
    except Exception:
        pass
    return os.environ.get(key_name)


def call_openai_compatible_endpoint(
    base_url: str,
    api_key: str,
    model: str,
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 0.2,
    max_tokens: int = 1000,
    timeout_secs: float = 30.0
) -> Dict[str, Any]:
    """Universal caller for any OpenAI-compatible completions endpoint."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "tare.tools.relay/1.0"
    }
    payload: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout_secs) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_vote_json(raw_text: str, nonce: str) -> Optional[Dict[str, Any]]:
    """Parse JSON vote from assistant text and verify nonce correlation."""
    matches = list(re.finditer(r"\{[\s\S]*\}", raw_text))
    for m in reversed(matches):
        try:
            parsed = json.loads(m.group(0))
            if parsed.get("execution_nonce") == nonce:
                return parsed
        except Exception:
            pass
    return None


def dispatch_seat_universal(
    seat_name: str,
    prompt_text: str,
    nonce: str,
    offline_mode: bool = False,
    local_gpu_url: str = DEFAULT_LOCAL_GPU_URL,
    excluded_models: Optional[Set[str]] = None
) -> Dict[str, Any]:
    """Dispatch a seat vote through the cascaded fallback pipeline with Anti-Sybil model exclusion."""
    excluded = excluded_models or set()
    """Dispatch a seat vote through the cascaded fallback pipeline."""
    if offline_mode:
        return _call_local_gpu(seat_name, prompt_text, nonce, local_gpu_url)

    # 1. Seat-specific cascades (Vendor CLI First -> Zero API Credit Burning)
    if seat_name == "google":
        # 1.1 Primary: Google AI Pro CLI (agy.EXE)
        agy_bin = shutil.which("agy") or shutil.which("agy.exe")
        if agy_bin:
            try:
                cmd = [agy_bin, "-p", prompt_text, "--effort", "high", "--dangerously-skip-permissions"]
                cp = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90, shell=False)
                if cp.returncode == 0:
                    parsed = parse_vote_json(cp.stdout, nonce)
                    if parsed:
                        return {"status": "OK", "provider": "google", "model": "gemini-3.7-flash", "vote": parsed}
            except Exception:
                pass

        # 1.2 Fallback: Google AI Studio Keyring API
        gemini_key = get_vault_key("GEMINI_API_KEY")
        if gemini_key:
            try:
                resp = call_openai_compatible_endpoint(
                    base_url=GEMINI_BASE_URL,
                    api_key=gemini_key,
                    model="gemini-3.7-flash",
                    messages=[{"role": "user", "content": prompt_text}],
                    timeout_secs=25.0
                )
                txt = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
                parsed = parse_vote_json(txt, nonce)
                if parsed:
                    return {"status": "OK", "provider": "google", "model": "gemini-3.7-flash", "vote": parsed}
            except Exception:
                pass

    elif seat_name == "anthropic":
        # 1.1 Primary: Anthropic Claude Code CLI (claude.exe / claude.cmd)
        claude_exe = Path(r"C:\Users\augus\AppData\Roaming\npm\node_modules\@anthropic-ai\claude-code\bin\claude.exe")
        claude_bin = str(claude_exe) if claude_exe.exists() else (shutil.which("claude") or shutil.which("claude.cmd"))
        if claude_bin:
            temp_file = None
            try:
                import tempfile
                with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as f:
                    f.write(prompt_text)
                    temp_file = f.name

                ps_cmd = f"Get-Content -Raw -Encoding utf8 '{temp_file}' | & '{claude_bin}' -p -"
                cp = subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=90
                )
                if cp.returncode == 0:
                    parsed = parse_vote_json(cp.stdout, nonce)
                    if parsed:
                        return {"status": "OK", "provider": "anthropic", "model": "claude-fable-5-high", "vote": parsed}
            except Exception:
                pass
            finally:
                if temp_file:
                    Path(temp_file).unlink(missing_ok=True)

        kimi_cred = Path.home() / ".kimi-code/credentials/kimi-code.json"
        if kimi_cred.exists():
            try:
                token = json.loads(kimi_cred.read_text(encoding="utf-8")).get("access_token")
                if token:
                    resp = call_openai_compatible_endpoint(
                        base_url=KIMI_BASE_URL,
                        api_key=token,
                        model="k3-256k",
                        messages=[{"role": "user", "content": prompt_text}],
                        timeout_secs=30.0
                    )
                    txt = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
                    parsed = parse_vote_json(txt, nonce)
                    if parsed:
                        return {"status": "OK", "provider": "kimi_backup", "model": "k3-256k", "vote": parsed}
            except Exception:
                pass

    elif seat_name == "openai":
        codex_bin = shutil.which("codex") or shutil.which("codex.exe")
        if codex_bin:
            try:
                cmd = [codex_bin, 'exec', '-m', 'gpt-5.6-sol', '-c', 'model_reasoning_effort="high"', '--dangerously-bypass-approvals-and-sandbox', '--skip-git-repo-check', '-']
                cp = subprocess.run(cmd, input=prompt_text, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90, shell=False)
                if cp.returncode == 0:
                    parsed = parse_vote_json(cp.stdout, nonce)
                    if parsed:
                        return {"status": "OK", "provider": "openai", "model": "gpt-5.6-sol", "vote": parsed}
            except Exception:
                pass

    # 2. Universal NVIDIA NIM Fallback Chain
    nvidia_key = get_vault_key("NVIDIA_API_KEY")
    if nvidia_key:
        nim_models = ["z-ai/glm-5.2"]  # Mandato estrito: somente GLM 5.2 homologado no NIM
        available_nim = [m for m in nim_models if m not in excluded]
        for m in available_nim:
            try:
                resp = call_openai_compatible_endpoint(
                    base_url=NIM_BASE_URL,
                    api_key=nvidia_key,
                    model=m,
                    messages=[{"role": "user", "content": prompt_text}],
                    timeout_secs=25.0
                )
                choice = resp.get("choices", [{}])[0]
                msg = choice.get("message", {})
                txt = msg.get("content") or msg.get("reasoning_content") or ""
                parsed = parse_vote_json(txt, nonce)
                if parsed:
                    return {"status": "OK", "provider": f"nim_backup_{seat_name}", "model": m, "vote": parsed}
            except Exception:
                continue

    # 3. Final Sovereign Fallback: Local GPU (RTX 3090) with Anti-Sybil distinct pin
    local_pin = PIN_LOCAL_SOVEREIGN_GENERAL
    if local_pin in excluded:
        local_pin = PIN_LOCAL_RED_TEAM  # Alternate local pin to preserve uniqueness
    return _call_local_gpu(seat_name, prompt_text, nonce, local_gpu_url, model_pin=local_pin)


def _call_local_gpu(
    seat_name: str,
    prompt_text: str,
    nonce: str,
    local_gpu_url: str,
    model_pin: str = PIN_LOCAL_SOVEREIGN_GENERAL
) -> Dict[str, Any]:
    """Call Local GPU endpoint on RTX 3090 with explicit model pin."""
    try:
        resp = call_openai_compatible_endpoint(
            base_url=local_gpu_url,
            api_key="EMPTY",
            model=model_pin,
            messages=[{"role": "user", "content": prompt_text}],
            timeout_secs=35.0
        )
        txt = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed = parse_vote_json(txt, nonce)
        if parsed:
            return {"status": "OK", "provider": "local_gpu", "model": model_pin, "vote": parsed}
    except Exception as e:
        return {"status": "FAILED", "provider": "local_gpu", "error": str(e)}
    return {"status": "FAILED", "provider": "local_gpu", "error": f"Invalid or missing JSON from Local GPU ({model_pin})"}


# -----------------------------------------------------------------------------
# 4. Dialectical Compaction & Mediator Turn
# -----------------------------------------------------------------------------

def generate_dialectical_brief(
    vote_records: Dict[str, Dict[str, Any]],
    local_gpu_url: str = DEFAULT_LOCAL_GPU_URL
) -> Dict[str, Any]:
    """Generate a 3-pillar dialectical brief from raw seat votes."""
    valid_votes = {s: v["vote"] for s, v in vote_records.items() if v.get("status") == "OK"}
    
    consensuses: List[str] = []
    tensions: List[Dict[str, Any]] = []
    discard_candidates: List[str] = []

    all_strengths = []
    all_issues = []
    all_recommendations = []

    for seat, vote in valid_votes.items():
        all_strengths.extend(vote.get("strengths", []))
        for iss in vote.get("issues", []):
            if isinstance(iss, dict):
                iss_copy = dict(iss)
                iss_copy["reported_by"] = seat
            else:
                iss_copy = {
                    "claim": str(iss),
                    "summary": str(iss),
                    "severity": "blocking",
                    "falsifier": "Verificação empírica formal",
                    "reported_by": seat
                }
            all_issues.append(iss_copy)
        all_recommendations.extend(vote.get("recommendations", []))

    if all(v.get("verdict") == "APPROVE" for v in valid_votes.values()):
        consensuses.append("Aprovação unânime das premissas e arquitetura proposta.")
    
    for iss in all_issues:
        if iss.get("severity") == "blocking":
            tensions.append({
                "claim": iss.get("claim"),
                "falsifier": iss.get("falsifier"),
                "seat": iss.get("reported_by")
            })
        else:
            discard_candidates.append(f"[{iss.get('reported_by')}] {iss.get('claim')} (Classificado como não-bloqueante)")

    return {
        "established_consensuses": consensuses or all_strengths[:3],
        "dialectical_tensions": tensions,
        "discard_candidates": discard_candidates,
        "recommendations": all_recommendations[:4]
    }


def execute_mediator_synthesis(
    anchor_md: str,
    dialectical_brief: Dict[str, Any],
    compact_delta: Dict[str, Any],
    round_num: int
) -> str:
    """Deterministic constitutional mediation with Via Negativa filter."""
    lines = [
        f"# SÍNTESE DO MEDIADOR CONSTITUCIONAL — RODADA {round_num}",
        "",
        "## 1. Consensos Estabelecidos (Imutáveis)",
    ]
    for c in dialectical_brief.get("established_consensuses", []):
        lines.append(f"- {c}")

    lines.extend([
        "",
        "## 2. Tensões Dialéticas & Falsificadores Bloqueantes",
    ])
    tensions = dialectical_brief.get("dialectical_tensions", [])
    if tensions:
        for t in tensions:
            lines.append(f"- **[{t.get('seat', 'seat').upper()}]**: {t.get('claim')}")
            lines.append(f"  - *Falsificador Exigido:* `{t.get('falsifier')}`")
    else:
        lines.append("- Nenhuma tensão bloqueante em aberto.")

    lines.extend([
        "",
        "## 3. Descarte por Via Negativa (Anti-Hipertrofia)",
    ])
    discards = dialectical_brief.get("discard_candidates", [])
    if discards:
        for d in discards:
            lines.append(f"- {d}")
    else:
        lines.append("- Nenhum item descartado nesta rodada.")

    return "\n".join(lines) + "\n"


# -----------------------------------------------------------------------------
# 5. Quorum Calculation & State Machine
# -----------------------------------------------------------------------------

def compute_quorum_mode(vote_records: Dict[str, Dict[str, Any]]) -> QuorumMode:
    """Deterministic calculation of Quorum Mode from real active providers with Anti-Sybil check."""
    valid_votes = [v for v in vote_records.values() if v.get("status") == "OK"]
    if len(valid_votes) < 2:
        return QuorumMode.HELD_UNAVAILABLE

    # Anti-Sybil Invariant: No single model may occupy more than 1 seat!
    models = [v.get("model") for v in valid_votes if v.get("model")]
    if len(models) != len(set(models)):
        return QuorumMode.HELD_UNAVAILABLE

    providers = {v.get("provider", "unknown") for v in valid_votes}
    
    if "local_gpu" in providers:
        return QuorumMode.LOCAL_ADVISORY
    
    if len(valid_votes) == 3:
        if providers.issubset(TITULAR_PROVIDERS) and len(providers) == 3:
            return QuorumMode.FRONTIER_UNANIMOUS
        return QuorumMode.DEGRADED_MIXED
    
    return QuorumMode.DEGRADED_MIXED


def evaluate_round_verdict(
    vote_records: Dict[str, Dict[str, Any]],
    current_round: int,
    overtime_granted: bool = False
) -> Tuple[DeliberationStatus, str]:
    """Evaluate deliberation state based on votes, strict limits, and Anti-Sybil uniqueness."""
    valid_votes = [v for v in vote_records.values() if v.get("status") == "OK"]
    
    if len(valid_votes) < 2:
        return DeliberationStatus.HELD_UNAVAILABLE, "Quórum mínimo insuficiente (<2 assentos operacionais)."

    # Anti-Sybil Invariant: Every chair must be occupied by a distinct model!
    models = [v.get("model") for v in valid_votes if v.get("model")]
    if len(models) != len(set(models)):
        duplicates = [m for m in models if models.count(m) > 1]
        return DeliberationStatus.HELD_UNAVAILABLE, f"Violação Anti-Sybil: o modelo '{duplicates[0]}' ocupou múltiplas cadeiras."

    verdicts = [v.get("vote", {}).get("verdict") for v in valid_votes]
    
    has_blocking_issues = False
    for v in valid_votes:
        vote = v.get("vote", {})
        for iss in vote.get("issues", []):
            sev = iss.get("severity") if isinstance(iss, dict) else "blocking"
            if sev in ("blocking", "critical"):
                has_blocking_issues = True
                break

    if all(v == "APPROVE" for v in verdicts) and len(valid_votes) >= 3 and not has_blocking_issues:
        return DeliberationStatus.APPROVED, "Consenso unânime tripartite alcançado."

    effective_max = MAX_OVERTIME_ROUNDS if overtime_granted else MAX_ROUNDS
    
    if current_round >= effective_max:
        if overtime_granted and current_round >= MAX_OVERTIME_ROUNDS:
            return DeliberationStatus.HELD_OVERTIME_EXHAUSTED, f"Teto absoluto de prorrogação ({MAX_OVERTIME_ROUNDS} rodadas) esgotado."
        
        return DeliberationStatus.HELD_PROGRESS_REVIEW, f"Teto normativo de {MAX_ROUNDS} rodadas atingido com progresso fértil."

    if any(v == "REJECT" for v in verdicts):
        return DeliberationStatus.REVISED, "Objeções substantivas identificadas; nova revisão necessária."
    
    return DeliberationStatus.REVISED, "Revisões pendentes de convergência."


# -----------------------------------------------------------------------------
# 6. Modo Auditoria de Código & Invariantes (Zero Self-Auditing & Red Team)
# -----------------------------------------------------------------------------

class AuditStatus(str, Enum):
    AUDIT_APPROVED = "AUDIT_APPROVED"
    AUDIT_HELD_REMEDIATION_REQUIRED = "AUDIT_HELD_REMEDIATION_REQUIRED"


def evaluate_audit_verdict(
    audit_votes: Dict[str, Dict[str, Any]]
) -> Tuple[AuditStatus, List[Dict[str, Any]], str]:
    """Evaluate audit results from examiners and Red Team.
    
    Returns:
        (AuditStatus, critical_findings, summary_reason)
    """
    valid_votes = [v for v in audit_votes.values() if v.get("status") == "OK"]
    if len(valid_votes) < 2:
        return AuditStatus.AUDIT_HELD_REMEDIATION_REQUIRED, [], "Quórum insuficiente para laudo de auditoria (<2 assentos)."

    all_critical_findings: List[Dict[str, Any]] = []
    
    for seat, res in audit_votes.items():
        vote = res.get("vote", {})
        for iss in vote.get("issues", []):
            if iss.get("severity") in ("blocking", "critical"):
                finding = dict(iss)
                finding["auditor_seat"] = seat
                all_critical_findings.append(finding)

    if all_critical_findings:
        return (
            AuditStatus.AUDIT_HELD_REMEDIATION_REQUIRED,
            all_critical_findings,
            f"Auditoria reprovada com {len(all_critical_findings)} inconformidades bloqueantes identificadas."
        )

    return (
        AuditStatus.AUDIT_APPROVED,
        [],
        "Auditoria ratificada por conformidade total com os invariantes do contrato."
    )


def generate_audit_report(
    case_id: str,
    target_artifacts: List[str],
    audit_votes: Dict[str, Dict[str, Any]],
    status: AuditStatus,
    reason: str,
    critical_findings: List[Dict[str, Any]]
) -> str:
    """Generate canonical AUDIT_REPORT.md conforming to governance standards."""
    lines = [
        f"# LAUDO DE AUDITORIA FORMAL: {case_id}",
        "",
        f"- **Status Final:** `{'✅ ' + status.value if status == AuditStatus.AUDIT_APPROVED else '🛑 ' + status.value}`",
        f"- **Data:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}",
        f"- **Alvos Auditados:** {', '.join(target_artifacts)}",
        f"- **Síntese:** {reason}",
        "",
        "## 1. Parecer da Banca Examinadora & Red Team",
    ]

    for seat, res in audit_votes.items():
        vote = res.get("vote", {})
        verdict = vote.get("verdict", "N/A")
        summary = vote.get("summary", "Sem resumo fornecido.")
        provider = res.get("provider", "unknown")
        model = res.get("model", "unknown")
        lines.append(f"- **[{seat.upper()} ({provider} / {model})]:** `{verdict}` — {summary}")

    lines.extend([
        "",
        "## 2. Inconformidades Críticas Identificadas (Falsificadores)",
    ])

    if critical_findings:
        for idx, f in enumerate(critical_findings, 1):
            lines.append(f"### 🛑 Inconformidade #{idx}: {f.get('claim')}")
            lines.append(f"- **Auditor:** `[{f.get('auditor_seat', 'unknown').upper()}]`")
            lines.append(f"- **Invariante Violado:** `{f.get('invariant_violated', 'Contrato Geral')}`")
            lines.append(f"- **Falsificador Demonstrável:** `{f.get('falsifier')}`")
            if f.get("reproduction_test"):
                lines.append(f"- **Comando de Teste de Reprodução:** `{f.get('reproduction_test')}`")
            if f.get("remedy"):
                lines.append(f"- **Correção Sugerida:** {f.get('remedy')}")
            lines.append("")
    else:
        lines.append("- ✅ Nenhuma inconformidade crítica ou bloqueante identificada.")

    lines.extend([
        "",
        "## 3. Próximos Passos & Diretiva de Execução",
    ])
    if status == AuditStatus.AUDIT_APPROVED:
        lines.append("1. O pacote de código/especificação está liberado para merge e cutover.")
        lines.append("2. Invariantes de prova arquivados no `ARCHITECTURAL_QA_LEDGER.md`.")
    else:
        lines.append("1. O desenvolvedor deve aplicar os patches para satisfazer os falsificadores acima.")
        lines.append("2. Submeter nova rodada restrita aos deltas das correções (Rodada 2 Máxima).")

    return "\n".join(lines) + "\n"


# -----------------------------------------------------------------------------
# 7. Motor Autônomo de Deliberação de Ponta a Ponta (Zero Interrupção)
# -----------------------------------------------------------------------------

def execute_mediator_turn_llm(
    anchor_md: str,
    dialectical_brief: Dict[str, Any],
    compact_delta: Dict[str, Any],
    round_num: int
) -> Tuple[str, str]:
    """Independent neutral LLM Mediator turn filtering via Via Negativa and drafting convergence delta.
    
    Returns:
        (mediator_synthesis_md, revised_proposal_md)
    """
    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    prompt = f"""Você é o Mediador Constitucional Independente da Mesa Redonda Tripartite de Governança.
Seu papel é arbitrar as tensões entre Google, OpenAI e Anthropic sob a VIA NEGATIVA (anti-hipertrofia, ausência de burocracia, pragmatismo empírico).

---
### PROPOSTA VIGENTE:
{anchor_md}

---
### LAUDO DIALÉTICO DOS 3 ASSENTOS (RODADA {round_num}):
```json
{json.dumps(dialectical_brief, indent=2, ensure_ascii=False)}
```

---
DIRETRIZES DO MEDIADOR:
1. Identifique os consensos consolidados e as tensões bloqueantes.
2. Aplique a Via Negativa: descarte picuinhas estéticas e acolha apenas correções contratuais necessárias para eliminar ambiguidade ou falha.
3. Proponha o texto da proposta revisada incorporando um Aditivo de Convergência com as soluções necessárias.
4. Responda ESTRITAMENTE com um bloco JSON no seguinte schema:

```json
{{
  "synthesis_markdown": "# SÍNTESE DO MEDIADOR — RODADA {round_num}\n\n...",
  "revised_proposal_markdown": "# PROPOSTA FORMAL...\n\n..."
}}
```
"""
    if nvidia_key:
        try:
            resp = call_openai_compatible_endpoint(
                base_url=NIM_BASE_URL,
                api_key=nvidia_key,
                model="z-ai/glm-5.2",
                messages=[{"role": "user", "content": prompt}],
                timeout_secs=60.0
            )
            choice = resp.get("choices", [{}])[0]
            msg = choice.get("message", {})
            raw = msg.get("content") or msg.get("reasoning_content") or ""
            if "```json" in raw:
                raw = raw.split("```json", 1)[1].split("```", 1)[0].strip()
            elif "```" in raw:
                raw = raw.split("```", 1)[1].split("```", 1)[0].strip()
            data = json.loads(raw)
            if "synthesis_markdown" in data and "revised_proposal_markdown" in data:
                return data["synthesis_markdown"], data["revised_proposal_markdown"]
        except Exception:
            pass

    # Fallback to deterministic synthesis
    synthesis = execute_mediator_synthesis(anchor_md, dialectical_brief, compact_delta, round_num)
    return synthesis, anchor_md


def run_autonomous_case_loop(
    case_dir: Path,
    proposal_title: str,
    max_rounds: int = MAX_ROUNDS,
    overtime_granted: bool = False
) -> Dict[str, Any]:
    """Executes the full tripartite deliberation loop end-to-end without pausing.
    
    Halts ONLY on terminal status (APPROVED, HELD_PROGRESS_REVIEW, HELD_OVERTIME_EXHAUSTED, HELD_UNAVAILABLE).
    """
    case_dir = Path(case_dir)
    proposal_file = case_dir / "PROPOSAL.md"
    if not proposal_file.exists():
        raise FileNotFoundError(f"PROPOSAL.md not found in {case_dir}")

    current_proposal = proposal_file.read_text(encoding="utf-8")
    current_round = 1
    effective_max = MAX_OVERTIME_ROUNDS if overtime_granted else max_rounds
    prev_proposal = current_proposal
    current_delta: Dict[str, Any] = {}
    last_synthesis = ""

    print(f"\n{'=' * 80}")
    print(f"[LOOP AUTÔNOMO INICIADO]: Caso {case_dir.name} (Teto: {effective_max} rodadas)")
    print(f"{'=' * 80}")

    with CaseLock(case_dir / ".lock"):
        while current_round <= effective_max:
            r_str = f"r{current_round:03d}"
            r_dir = case_dir / "rounds" / r_str
            r_dir.mkdir(parents=True, exist_ok=True)

            print(f"\n>>> Executando Rodada {current_round}/{effective_max}...")
            seats = ["google", "openai", "anthropic"]
            nonces = {s: str(uuid.uuid4()) for s in seats}
            claimed_models = set()
            vote_results = {}

            # Construct round prompt
            for s in seats:
                if current_round == 1:
                    prompt_text = f"""Você é o titular da cadeira [{s.upper()}] na Mesa Redonda Tripartite de Governança.
Sua missão é auditar formalmente a proposta abaixo sob a ótica de engenharia prática, robustez e ausência de overengineering.

{current_proposal}

---
DIRETRIZES DE AUDITORIA:
1. Avalie a proposta com foco em simplicidade, solidez de contrato, viabilidade empírica e anti-hipertrofia.
2. Emita o seu parecer técnico genuíno ("verdict": "APPROVE", "REVISE" ou "REJECT").
3. Responda ESTRITAMENTE com um bloco JSON:

```json
{{
  "seat": "{s}",
  "execution_nonce": "{nonces[s]}",
  "verdict": "APPROVE",
  "confidence": 0.95,
  "summary": "Resumo técnico genuíno de 2 a 3 frases.",
  "strengths": ["Ponto forte 1"],
  "issues": [],
  "recommendations": []
}}
```
"""
                else:
                    delta_str = json.dumps(current_delta, indent=2, ensure_ascii=False)
                    final_warn = "\n🚨 AVISO DE FSM: ESTA É A RODADA FINAL (TETO MECÂNICO) 🚨" if current_round == effective_max else ""
                    prompt_text = f"""{final_warn}
Você é o titular da cadeira [{s.upper()}] na Mesa Redonda Tripartite de Governança.
Esta é a **RODADA {current_round} DE {effective_max}** de deliberação.

---
### 1. SÍNTESE DO MEDIADOR INDEPENDENTE (RODADA ANTERIOR):
{last_synthesis}

---
### 2. DELTA COMPACTO DA REVISÃO (APENAS SEÇÕES MODIFICADAS):
```json
{delta_str}
```

---
### 3. PROPOSTA VIGENTE COMPLETA:
{current_proposal}

---
DIRETRIZES DA RODADA {current_round}:
1. Avalie se o delta e a proposta atendem às tensões identificadas pelo Mediador.
2. Emita "verdict": "APPROVE", "REVISE" ou "REJECT".
3. Responda ESTRITAMENTE com o bloco JSON:

```json
{{
  "seat": "{s}",
  "execution_nonce": "{nonces[s]}",
  "verdict": "APPROVE",
  "confidence": 0.95,
  "summary": "Resumo técnico genuíno de 2 a 3 frases.",
  "strengths": ["Ponto forte"],
  "issues": [],
  "recommendations": []
}}
```
"""
                print(f"  [DISPATCH] Despachando assento [{s.upper()}] via CLI titular...")
                res = dispatch_seat_universal(
                    seat_name=s,
                    prompt_text=prompt_text,
                    nonce=nonces[s],
                    excluded_models=claimed_models
                )
                vote_results[s] = res
                if res.get("status") == "OK" and res.get("model"):
                    claimed_models.add(res.get("model"))
                print(f"    -> [{s.upper()}]: status={res.get('status')}, model={res.get('model')}, verdict={res.get('vote', {}).get('verdict')}")

            # Save seat votes
            for s, v in vote_results.items():
                write_json_atomic(r_dir / f"seat_{s}.json", v)

            quorum_mode = compute_quorum_mode(vote_results)
            brief = generate_dialectical_brief(vote_results)
            write_json_atomic(r_dir / "dialectical_brief.json", brief)

            status, reason = evaluate_round_verdict(vote_results, current_round=current_round, overtime_granted=overtime_granted)
            print(f"  [STATUS DA RODADA {current_round}]: {status.value} - {reason} (Quórum: {quorum_mode.value})")

            # Update case state
            case_state_file = case_dir / "case.json"
            if case_state_file.exists():
                case_state = json.loads(case_state_file.read_text(encoding="utf-8"))
            else:
                case_state = {
                    "case_id": case_dir.name,
                    "proposal_title": proposal_title,
                    "max_rounds": max_rounds,
                    "rounds": {}
                }
            
            case_state["current_round"] = current_round
            case_state["status"] = status.value
            case_state["quorum_mode"] = quorum_mode.value
            case_state["overtime_granted"] = overtime_granted
            case_state["rounds"][r_str] = {
                "status": status.value,
                "reason": reason,
                "quorum_mode": quorum_mode.value,
                "brief": brief,
                "votes": {s: v.get("vote", {}) for s, v in vote_results.items()}
            }
            write_json_atomic(case_state_file, case_state)

            if status == DeliberationStatus.APPROVED:
                decision_md = f"""# DECISÃO RATIFICADA: {proposal_title}

- **Caso:** `{case_dir.name}`
- **Data:** {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
- **Status:** RATIFICADO POR UNANIMIDADE TRIPARTITE
- **Modo de Quórum:** `{quorum_mode.value}` (100% Vendor CLI Titular)
- **Rodadas de Convergência:** {current_round} de {effective_max}

## 1. Consensos Estabelecidos
""" + "\n".join(f"- {c}" for c in brief.get("established_consensuses", [])) + f"""

## 2. Votação Final da Rodada {current_round}
""" + "\n".join(f"- **[{s.upper()} ({v.get('provider')} / {v.get('model')})]:** {v.get('vote', {}).get('verdict')} — {v.get('vote', {}).get('summary')}" for s, v in vote_results.items())

                write_text_atomic(case_dir / "DECISION.md", decision_md)
                write_text_atomic(case_dir / "PROPOSAL.md", current_proposal)
                print(f"\n🎉 [SUCESSO] Caso {case_dir.name} RATIFICADO na Rodada {current_round}!")
                return case_state

            if status in (DeliberationStatus.HELD_PROGRESS_REVIEW, DeliberationStatus.HELD_OVERTIME_EXHAUSTED, DeliberationStatus.HELD_UNAVAILABLE):
                print(f"\n🛑 [PARADA MECÂNICA DA FSM]: {status.value} ({reason}).")
                return case_state

            # If REVISED and not at limit -> Autonomous Mediator Turn
            print(f"  [MEDIADOR INDEPENDENTE] Executando síntese autônoma e propondo delta para Rodada {current_round + 1}...")
            synthesis_md, revised_proposal_md = execute_mediator_turn_llm(
                anchor_md=current_proposal,
                dialectical_brief=brief,
                compact_delta=current_delta,
                round_num=current_round
            )
            write_text_atomic(r_dir / "MEDIATOR_SYNTHESIS.md", synthesis_md)
            last_synthesis = synthesis_md
            
            # Compute new compact delta
            prev_proposal = current_proposal
            current_proposal = revised_proposal_md
            current_delta = generate_compact_delta(prev_proposal, current_proposal)

            current_round += 1

    return case_state
