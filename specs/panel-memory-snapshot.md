# Panel memory snapshot — scope × purpose, every byte redacted (`M5.mem`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/mem_snapshot_panel.py).

Intake (SPEC-116 door NEW): request = "tela de snapshot de memórias: memórias
e ledgers que os agentes têm acesso, organizados por ESCOPO e FINALIDADE, com
conteúdo atual" (`docs/roadmap/screens-memory-records.md` §A). Covered-check:
the panel shows only the ledger tail/head + a search dialog — nothing shows,
in one place, what an agent will actually find and where each piece lives.
Decision: **NEW**. SLICE: M-A1 + the M-A2 user-scope resolver — target-scope
cards (M-A3) and change pulses (M-A4) stay OPEN.

## Goal

One Memory panel view: a card grid grouped scope (user / harness) × purpose,
one card per source in a CLOSED registry (auto-memory index, CONTEXT head,
worklog + archive, escalations, cost, calibration, self-review,
quality-state, the derived records index) with redacted previews and a
click-through full view — plus `records sources` as the terminal parity.
Every preview and full body passes `secret_scan.redact_text` server-side
before leaving the process; the client is never trusted (MEMORY.md has
already carried a leaked key once).

## Applicability

Applies to `scripts/harness_lib/ui_memory.py` (`memory_snapshot`,
`memory_file`, `user_memory_dir`, `render_sources`), `secret_scan.redact_text`
(promoted from the commits viewer — one redaction seam, two consumers), the
`GET /api/memory` + `/api/memory/file` routes, the Memory PAGE view and the
`records sources` action. Read-only everywhere; no ACTIONS entry.

## Requirements / invariants (numbered, testable)

1. **Closed registry, no free paths.** `memory_file` serves only registered
   source ids; unknown ids, the binary records index (metadata only) and
   absent sources refuse legibly.
2. **Redaction at the trust boundary.** Every preview and full body is
   rewritten by `secret_scan.redact_text` BEFORE it leaves the server —
   nothing key-shaped appears anywhere in any payload.
3. **Scope × purpose is the data model.** Rows carry scope (user/harness),
   purpose, path, exists/mtime/size and a bounded first+last-lines preview;
   per-source degrade, calm absences.
4. **User scope is machine-local and says so.** The auto-memory dir derives
   from the repo path slug (each `[:\\/]` char → `-`, never collapsed);
   absence is normal (CI) and the card is badged "not repo state".
5. **CLI parity.** `records sources` prints the same table, exit 0.

## Gherkin scenarios

```gherkin
Feature: memory snapshot (scope × purpose, redacted)

  Scenario: [mem-1] the snapshot groups sources and never leaks
    Given seeded state files including a planted key and a user memory dir
    When memory_snapshot runs
    Then rows group by scope with calm absences and the serialized payload
      contains the redacted marker, never the key

  Scenario: [mem-2] the full view is closed-set and redacted
    Given the registered sources
    When memory_file runs for a real, unknown, binary and absent id
    Then the real body is redacted and the other three refuse legibly

  Scenario: [mem-3] the user-scope resolver degrades calmly
    Given the repo path and a home without auto-memory
    When the slug resolves
    Then it matches the per-char convention and absence reads as not present

  Scenario: [mem-4] the panel and CLI are wired
    Given the server, page and live CLI
    Then both memory routes exist, the Memory view renders, and records
      sources exits 0 with the table
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Registro FECHADO de fontes (sem paths livres) | `_safe_log` discipline (roadmap §A MVP); trust boundary |
| Redação server-side em TODO byte, cliente nunca confiável | roadmap top risk (MEMORY.md já vazou GEMINI_API_KEY uma vez — incidente PrintIntel) |
| `redact_text` promovido pro secret_scan (um seam, dois consumidores) | ladder rung 2 (ui_commits já tinha a mesma sub) |
| Slug per-char do auto-memory dir | convenção real do Claude Code (`C--projects-…` verificado nesta máquina) |
| Poll = o tick de 3s existente; mtime cache | roadmap ("that IS the tempo-real; no daemon") |
| M-A3/M-A4 fora | slice discipline; YAGNI até alguém assistir a tela ao vivo |

## Test strategy

- Behaviors: grouped snapshot + planted-key redaction over the WHOLE payload
  (mem-1); closed-set refusals + full-body redaction (mem-2); slug + calm
  degrade (mem-3); routes/view/CLI wiring (mem-4).
- Edge cases: corrupt source file → per-source degrade (error field, others
  render); short files preview whole; binary index metadata-only.
- Regression net: m5_ui_panel + ui_e2e rc0; secret_scan + ui_commits
  self-checks (the shared redaction seam).
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/mem_snapshot_panel.py`.

## Validation

- `python testing/scenarios/mem_snapshot_panel.py` — mem-1..mem-4 green.
- `python scripts/harness_lib/ui_memory.py` — module self-check.
- `python testing/scenarios/m5_ui_panel.py` + ui_e2e rc0 — panel regression net.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.
