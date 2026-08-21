# SPEC-139 — TE.5 compact adoption on flat-list emitters (`te5a`)

Status: SPEC-139, proposed 2026-07-13 (acceptance: `testing/scenarios/te5_compact_adoption.py`).

Intake (SPEC-116 door NEW): plan-token-economy S1 — the TE.5 engine
(`te5-agent-output.md`, `common.emit(..., tsv=True)`) shipped and was adopted at
nine call sites, but several agent-facing `list` verbs in `harness_lib/` still
emitted verbose indent=2 JSON to agent consumers. This spec owns the ADOPTION
step: which additional flat-list emitters opt into TSV, and the byte-identical
guarantee that makes the opt-in safe.

## Goal

Extend the TE.5 compact/tabular contract to the remaining agent-facing
flat-`list[dict]` emitters in `harness_lib/` (`experiment list`, `intake list`,
`services status`) so an agent consumer (`HARNESS_AGENT_OUTPUT=compact`) receives
a compact TSV table instead of pretty JSON, while humans and existing JSON
parsers (env absent) keep byte-identical indent=2 output. The engine is
unchanged (SPEC te5-agent-output); this spec only wires `tsv=True` on genuine
flat-list payloads and pins the behavior with a scenario.

## Applicability

Applies to the flat-`list[dict]` `emit()` sites in
`scripts/harness_lib/experiment_registry.py` (`experiment list`),
`intake_queue.py` (`intake list`), and `services.py` (`services status`),
which reuse `common.emit`/`common.to_tsv` (SPEC te5-agent-output) with no
engine change. It explicitly does NOT cover nested/dict or scalar payloads
(`experiment show`, `overseer review`, `oracle`, checkpoint results, chat/UI
stream events): those keep compact-separator JSON, never a table.

## Requirements / invariants (numbered, testable)

1. **TSV under compact for flat lists.** When `HARNESS_AGENT_OUTPUT=compact`
   and the payload is a non-empty flat `list[dict]`, an adopted command emits a
   TSV block whose first line is the tab-separated header (union of row keys,
   first-seen order) — one row per line thereafter.
2. **Byte-identical default.** With the env absent, an adopted command emits
   exactly the pre-adoption `indent=2` JSON (the wrapped `{...}` object for the
   human/`--json` path); the `tsv=True` flag is inert whenever
   `agent_output_compact()` is false.
3. **Nested payloads stay compact-JSON.** A sibling command whose payload is a
   dict (or otherwise not a homogeneous `list[dict]`) prints compact-separator
   JSON under compact — never a malformed TSV header; an empty list degrades to
   `[]`, never a header with no rows.

## Gherkin scenarios

```gherkin
Feature: TE.5 compact adoption on flat-list emitters

  Scenario: [te5a-1] an adopted flat-list command emits a TSV header under compact
    Given an agent consumer with HARNESS_AGENT_OUTPUT=compact
    When it runs an adopted list command with rows present
    Then the first output line is the tab-separated header of the row keys

  Scenario: [te5a-2] the env-absent default stays byte-identical indent=2 JSON
    Given no HARNESS_AGENT_OUTPUT in the environment
    When a human runs the same adopted list command
    Then the output is the pre-adoption indent=2 JSON, unchanged

  Scenario: [te5a-3] nested and empty payloads never become a broken table
    Given a nested-dict command and an empty list under compact
    When each is emitted
    Then both print compact JSON, never a TSV header with no rows
```

## Rationale & sources

| Decision | Sources |
|---|---|
| Adopt TSV only on genuine flat `list[dict]` verbs | te5-agent-output inv. 2 (closed allowlist) + inv. 4 (calm degradation): forcing TSV on a dict/scalar would break the one-record-per-line contract |
| `experiment list` / `intake list` / `services status` are the eligible sites | source audit of every `emit(...)` in the S1 module set: these three are the only remaining non-empty-flat-list emitters (others are single-dict results or stream events) |
| Byte-identical default is non-negotiable | te5-agent-output inv. 1: `agent_output_compact()` gates the compact branch, so `tsv=True` is inert when the env is absent — no human/parser regression |
| Reuse the engine, add no code path | plan-token-economy S1: TE.5 engine (`common.emit`/`to_tsv`) is done; adoption is a one-argument opt-in per site |

## Ceilings (upgrade paths)

`services status` only reaches `emit()` under `--json`; it has no
`agent_output_compact()` short-circuit like `experiment/intake list`. Left as-is
(the `--json` path is the agent's structured surface); add a compact
short-circuit only if agents call `services status` without `--json` and the
human table is measured as wasted tokens.

## Test strategy

- Behaviors to verify: TSV header under compact (te5a-1); byte-identical
  indent=2 default (te5a-2); nested/empty degrade to compact JSON (te5a-3).
- Edge cases: empty list → `[]`; nested cell (`measurements`) → compact-JSON
  cell inside the TSV row.
- Regression risks: none for env-absent consumers (default branch unchanged);
  the closed-allowlist count pin in `te_compact_output.py` (te5-agent-output
  inv. 2) must move in the same integration.
- Coverage impact: enforced via `testing/scenarios/te5_compact_adoption.py`.

## Validation

- `python testing/scenarios/te5_compact_adoption.py` — the `te5a-1`, `te5a-2`,
  `te5a-3` checks green.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green
  (this spec's sections + Gherkin mapping conform).

## Amendments

(none yet)
