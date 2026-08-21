# SPEC-117 — Intake-triage hook: SPEC-116 routing at the moment of the request

Status: adopted 2026-07-11 (door NEW; intake recorded in the commit body and the
plan record). The first spec born entirely inside the SPEC-116 engine.

## Goal

When the user submits a request, the agent receives — before it starts thinking —
a deterministic, pre-computed SPEC-116 triage: the classified task profile and the
covered-doc evidence (records/doc-find hits). Not every request becomes a spec:
the hook routes and informs; the door decision stays with the agent and the human.

## Applicability

All three chat surfaces: Claude sessions in the repo (`UserPromptSubmit` hook),
Codex sessions (same event via `.codex/hooks.json`, SPEC-113 parity), and the
OpenAI-compatible engine (in-process pre-send in the REPL — it has no hook
system). Governed targets inherit via the packaged hook + adapters.

## Requirements / invariants (numbered, testable)

1. **Router, never a writer.** *(amended v2, 2026-07-13 — owner decision cm-6,
   see specs/40-features/intake-queue.md)*: the hook creates or updates no
   CANONICAL artifact and never blocks a prompt: it always exits 0; on any
   internal failure it emits nothing (silent pass-through). Blocking exit
   codes are forbidden. ONE sanctioned sidecar write exists: a feature-shaped
   prompt is also appended to the durable intake queue
   (`.harness/state/intake-queue.json`), inside its own guard so capture
   failure can never block a prompt — advisory-only triage let 8 owner asks
   evaporate (chat-mined archaeology 2026-07-13).
2. **Noise filter first.** Command-shaped prompts (starting with `/` or `!`),
   prompts shorter than a configured minimum, and prompts whose classification
   lands on non-feature profiles (`scan`, `debug`, `cheap`) produce ZERO injected
   context — silence is the default, injection is the exception.
3. **Feature-shaped prompts get the triage packet**: classified profile (from the
   existing `harness.py classify` scorer), top covered-doc candidates
   (`records search` + `doc-find` over the prompt's salient terms, compact
   output), and the three-exit reminder (no behavior change → no artifact;
   covered → recap + versioned amendment; new → intake template). Total injection
   ≤ ~10 lines.
4. **One implementation, three wire points.** The logic lives in ONE harness_lib
   function; `tools/hooks/spec_intake_triage.py` is a thin stdin/stdout wrapper
   wired in `.claude/settings.json` and `.codex/hooks.json` (parity visible in
   `agents audit`), and the OpenAI engine path calls the same function in-process
   before `agent.send`.
5. **Deterministic and cheap.** No LLM calls inside the hook; at most two local
   subprocess/library lookups, and only for prompts that pass the filter (R27:
   observation pays for itself). Thresholds (minimum length, profile allowlist,
   hit count) are config, not code.
6. **The door decision is never automated.** The injected text is advisory
   context; conformance of whatever artifact results is enforced downstream by
   the `feature-spec-conformance` gate (SPEC-116 invariant 3), not by this hook.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| `UserPromptSubmit` como ponto de injeção (exit 0 + stdout/additionalContext vira contexto visível ao agente; cap 10k chars; timeout 30s) | [Claude Code hooks reference](https://code.claude.com/docs/en/hooks); [hook schemas](https://gist.github.com/FrancisBourre/50dca37124ecc43eaf08328cdcccdb34); [guia 2026 de eventos](https://www.morphllm.com/claude-code-hooks) |
| Nunca bloquear o prompt (exit 2 rejeitaria — proibido aqui) | Mesma referência (semântica do exit 2); princípio do harness: triagem informa, humano decide (SPEC-109 governança) |
| Paridade codex pelo mesmo evento | Observado ao vivo nesta máquina (banner `hook: UserPromptSubmit` no ping codex de 2026-07-10); SPEC-113 capability parity |
| OpenAI in-process (sem hooks) | Arquitetura do engine (tool loop roda comandos via `run_harness_command`); precedente `deny_hitl_flags` (uma lógica, fiação por superfície) |
| Filtro determinístico antes de qualquer custo | Memória R27 (observação paga a si mesma); classify já existe como scorer local |
| Lookup de cobertura pré-computado no momento do pedido | SPEC-116 invariante 1 (porta COBERTO exige a busca) — o hook entrega a evidência de graça, no ponto de decisão |

## Ceilings (upgrade paths)

- The classifier inherits the known `review`-glob quirk on dirty trees; trigger
  tuning is config. If misrouting becomes frequent, revisit trigger lists — not
  the hook.
- No semantic matching of covered docs (lexical records/doc-find only); the
  semantic-retrieval trigger from the I5 re-triage applies here too.
- Injection is per-prompt with no memory of previous injections in the session;
  a session-aware "already triaged this thread" suppression is a follow-up if
  repetition proves noisy.

## Test strategy

Deterministic scenario over the shared library function (no LLM, no real hook
process): feature-shaped prompt → packet with profile + hits + three-exit
reminder; command/short/non-feature prompts → empty string; internal failure
(corrupt state) → empty string, no raise. Wiring checks: hook file present and
referenced in both vendor configs; `agents audit` matrix includes it; the
OpenAI pre-send call site exists. Gate: this spec itself must pass
`feature-spec-conformance` (first NEW spec through the engine).

## Validation

- `testing/scenarios/st_intake_triage.py` — the scenario above.
- `HARNESS_TEST_QUIET=1 python scripts/harness-test.py spec-pack --no-project-commands`
  (conformance of this spec + wiring fixtures).
- `python scripts/harness.py agents audit` — parity matrix carries the new hook.

## Amendments

(None yet — versioned sections v2+ append here.)
