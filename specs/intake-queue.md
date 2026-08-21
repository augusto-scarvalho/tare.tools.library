# Durable requirement-intake queue (`iq`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/iq_intake_queue.py).

Intake (SPEC-116 door NEW): chat-mined cm-6 — owner: *"quero que pesquise como
seria feito um hook de marcação pra escrita de specs quando o usuário faz
pedidos... nem todo pedido vira uma spec, ele deve ser triado."* The SPEC-117
triage hook shipped the DETECTION half (advisory packet per feature-shaped
prompt); the archaeology proved advice alone fails — 8 owner asks evaporated
with the hook running. Owner decision (this session): durable queue, no LLM
auto-classification, no discipline-only. Companion amendment: SPEC-117
invariant 1 (v2) sanctions this one sidecar write.

## Goal

A feature-shaped ask survives the conversation that carried it: captured
durably (redacted, deduped, capped), listed until a human/overseer records an
explicit triage decision (`spec` | `backlog` | `discard`), and nagged by
`doctor` when pending entries age past 7 days.

## Applicability

Applies to `harness_lib/intake_queue.py` (store + `intake` CLI verb),
`tools/hooks/spec_intake_triage.py` (guarded append on feature-shaped
prompts), and `repo_health.py` doctor check (5), `intake-staleness`. Writes
only `.harness/state/intake-queue.json`.

## Requirements / invariants (numbered, testable)

1. **Capture is redacted, deduped and capped.** Asks pass
   `secret_scan.redact_text` before storage, are capped at 400 chars,
   dedupe by normalized-content hash (lowercase + whitespace-collapse,
   sha1/12 — GLM spec-QA clarification) while pending, and the queue trims
   only DECIDED entries past 200 — pending asks never silently drop.
   *(v2, same day — both caught live by the release-hygiene gate)*:
   system-shaped payloads (leading `<`, e.g. task-notifications reaching the
   hook as "prompts") are SKIPPED, never captured as owner asks; and
   machine-local absolute paths are scrubbed to `<local-path>` — the queue is
   a tracked durable ledger and inherits the repo-wide no-local-paths rule.
2. **Triage is explicit and closed.** `intake decide <id>
   spec|backlog|discard [--note]` is the only state transition; unknown ids
   and decisions refuse legibly.
   *(v2, same day — SPEC-116 experiment-lifecycle pack)*: the decision
   vocabulary gains `experiment` = the ask is routed to the experiment registry
   (`harness.py experiment add EXP-N …`, per docs/EXPERIMENT_METHODOLOGY.md) and
   the `--note` carries the EXP-id back-reference; `spec|backlog|discard|experiment`
   is the closed set.
3. **The hook captures without blocking.** A feature-shaped prompt (non-empty
   triage packet) is appended with source `prompt-hook` inside its own
   guard; chatter/command prompts (silent packet) are never captured; hook
   exit stays 0 in every case (SPEC-117 v2).
4. **Staleness is visible.** `doctor` warns (never fails) listing pending
   entries older than 7 days; corrupt queue files read as empty and repair
   on the next write.

## Gherkin scenarios

```gherkin
Feature: durable requirement-intake queue

  Scenario: [iq-1] lifecycle — capture, dedupe, redact, decide
    Given an ask carrying a planted key added twice
    When it is decided into backlog with a note
    Then one redacted pending entry existed, the decision is recorded, and
      unknown ids/decisions refuse legibly

  Scenario: [iq-2] the hook captures feature-shaped prompts only
    Given the real UserPromptSubmit hook fed a feature-shaped prompt and a
      command-shaped one
    Then the first lands in the queue with source prompt-hook, the second
      does not, and both hook runs exit 0

  Scenario: [iq-3] doctor nags stale pending asks
    Given a pending entry older than seven days
    Then doctor reports intake-staleness as warn naming the entry

  Scenario: [iq-4] the verb is on the frozen surface
    Given the live CLI
    Then intake answers --help with rc 0 and the frozen top-level order
      includes it
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Fila durável, sem auto-classificação LLM | decisão do dono 2026-07-13 (AskUserQuestion cm-6); custo zero por prompt, zero falso-positivo mágico |
| Emenda explícita do invariante SPEC-117, não write contrabandeado | o invariante "router never writer" é testado (st_intake_triage); emendas versionadas > exceções silenciosas |
| Redação na captura | prompts podem conter segredos colados; mesmo seam secret_scan (ui_commits/ui_memory/checkpoint) |
| Pending nunca cai no trim | perder um pedido pendente silenciosamente reproduziria o bug que a fila existe pra matar |
| Evidência | chat-mined cm-6 (sessão f7f54eb1); 8 asks perdidos como prova de falha do advisory-only |

## Test strategy

- Behaviors: lifecycle completo (iq-1); hook real via subprocess com prompt
  feature-shaped vs comando (iq-2); doctor warn (iq-3); superfície (iq-4).
- Edge cases: fila corrupta lê vazia e se repara; decide sem params refusa.
- Regression net: st_intake_triage (hook contract), cli_registry (frozen
  surface), spec-pack.
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/iq_intake_queue.py`.

## Validation

- `python testing/scenarios/iq_intake_queue.py` — iq-1..iq-4 green.
- `python scripts/harness_lib/intake_queue.py` — module self-check.
- `python testing/scenarios/st_intake_triage.py` — SPEC-117 v2 regression net.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.
