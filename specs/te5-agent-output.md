# TE.5 agent-facing output contract (`te5`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/te_compact_output.py).

Intake (SPEC-116 door NEW): spec-recovery rec-cli-4/5/6 — TE.5 shipped as
rider lines inside four unrelated feature specs; the TSV-eligible verb
allowlist and the cell-flattening rule had no home and no test. This spec IS
the home: the riders elsewhere now defer here.

## Goal

One written contract for `common.emit` / `HARNESS_AGENT_OUTPUT=compact`:
humans and existing parsers keep byte-identical indent=2 JSON; agent
consumers get compact JSON, and — for a CLOSED allowlist of flat-list verbs —
TSV; malformed candidates degrade to compact JSON, never to a broken table.

## Applicability

Applies to `harness_lib/common.py` (`agent_output_compact`, `_tsv_cell`,
`to_tsv`, `emit`) and every `emit(..., tsv=True)` call site. The env flag is
set by chat-engine agent paths; absence means human/legacy consumer.

## Requirements / invariants (numbered, testable)

1. **Default is byte-identical legacy.** Env absent → `indent=2` JSON
   exactly as before TE.5 (TTY-only colorization changes nothing when
   redirected).
2. **Closed TSV allowlist.** Only these verbs opt in (one `emit(...,
   tsv=True)` site each unless noted): `records` (flat handle list),
   `agents skills` + `agents mcp`, `catalog`, `keys list`, `models list` +
   `models catalog`, `services list` + `services status`, `experiment list`,
   `intake list`, `tasks list` (the last three added by SPEC-139),
   `decide --list` (SPEC-145), `artifacts` (worker-result pipeline, owner GO
   2026-07-23). Adding or removing an opt-in REQUIRES updating this table and
   the scenario's source-derived count in the same commit.
3. **Cell flattening.** TSV cells flatten embedded tab/CR/LF to spaces and
   render nested values as compact JSON — one record per line is a data
   integrity guarantee, not cosmetics.
4. **Calm degradation.** Under compact, an empty list or a non-homogeneous
   list (any non-dict row) falls back to compact-separator JSON — never a
   TSV header with no rows, never a crash.
5. **Compact wins over --json.** Per-verb pattern: the compact branch
   returns before the `--json` branch, so an agent env never receives
   pretty JSON by accident.

## Gherkin scenarios

```gherkin
Feature: TE.5 agent-facing output contract

  Scenario: [te5-1] the TSV opt-in allowlist is closed and source-pinned
    Given every emit(..., tsv=True) call site in scripts/
    Then the per-file site counts match the spec's allowlist exactly

  Scenario: [te5-2] embedded newlines and tabs never break the table
    Given a row whose body carries newline, tab and CR characters
    When to_tsv renders it
    Then the record stays on one line with the characters flattened to spaces

  Scenario: [te5-3] malformed candidates degrade to compact JSON
    Given an empty list and a non-homogeneous list under compact
    When emit runs with tsv requested
    Then both print compact JSON, never a broken TSV header
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Allowlist FECHADA, pinada por contagem derivada do fonte | rec-cli-5: "which verbs emit TSV is scattered/undefined"; o pin de contagem força spec+código a moverem juntos (idiom do security-directive-map) |
| Flattening é integridade de dados, não cosmética | rec-cli-6: corpo multiline em records/log quebraria o contrato uma-linha-por-registro |
| Home spec própria em vez de 5º rider | rec-cli-4: riders em cli-tool-catalog/panel-tasks/keys/services já citavam TE.5 sem dono |
| Evidência prévia mantida | checks `compact:*` existentes em te_compact_output.py (ratios medidos, byte-identical guard) |

## Test strategy

- Behaviors: allowlist pin (te5-1); flattening (te5-2); degradação calma
  (te5-3); mais os cinco checks `compact:*` pré-existentes (byte-identical
  default, ratios, round-trips).
- Edge cases: célula None → vazia; valor aninhado → JSON compacto.
- Regression net: cli_registry, cc_cli_catalog, spec-pack.
- Coverage: `testing/scenarios/te_compact_output.py` (estendido).

## Validation

- `python testing/scenarios/te_compact_output.py` — te5-1..te5-3 + compact:* green.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.
