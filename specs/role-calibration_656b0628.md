# RF.1 — per-role (model, effort) bake-off runner (observe-only, phase 1)

Status: RF.1 phase 1, proposed 2026-07-12 (acceptance: `testing/scenarios/rc_role_calibration.py`).

Door NEW (SPEC-116): no spec under `specs/40-features/` owns empirical role
calibration — `model-routing.md` owns the routing registry and its byte-compat
consumption, not how a (model, effort) choice is measured. This spec seeds the
measurement side only.

## Goal

Give role -> (model, effort) routing an empirical basis without touching it: a
deterministic matrix runner executes one operator-supplied task command per
(model, effort) cell, scores each cell by exit code, and writes a value table
that RECOMMENDS a cell — it never flips routing.

## Applicability

`scripts/harness_lib/role_calibration.py` (`plan_cells`, `run`) and the
`routing bake-off` action of the `scripts/harness_lib/model_routing.py` hub
(thin dispatch only). Explicitly out of scope: any write to
`.harness/routing/model-routing.json` or `model-cards.json`, and any automatic
routing change — that is phase 2 (owner-gated, still OPEN).

## Requirements / invariants (numbered, testable)

1. **Full validated matrix.** `plan_cells(role, models, efforts, cards)` is
   pure and yields one cell per (model, effort) pair; every model must exist in
   the model-cards rows and every effort must be a known level supported by
   that card, else it raises (no partial silent matrices).
2. **Dry-run by default.** `run(...)` without `execute=True` prints the planned
   table and spawns NOTHING — the runner is never invoked, no report is
   written. The CLI mirrors this: `--execute` is required for any spend.
3. **Deterministic quality signal.** A cell passes iff its command exits 0.
   No LLM judge, ever (CQ independence: a model must not grade its own
   bake-off). tokens come from the task's stdout result JSON when reported,
   else null.
4. **Observe-only report.** Execute writes exactly one
   `.harness/state/bakeoff/<utc-ts>.json` = `{role, cells:[{model, effort,
   pass, durationS, tokens}]}` and prints the table pass-first/cheapest-first
   plus a `recommended:` line. Nothing writes routing config.
5. **Phase-2 boundary.** Feeding the recommendation into routing is a separate
   owner-gated item and stays OPEN; this spec closes only the measurement
   phase. No gate or scenario may ever pass `--execute` (real token spend is
   operator-only; scenario stubs use `python -c`).
6. **Hub byte-compat.** Every pre-existing `routing` action and the
   `routing show` output are unchanged by the `bake-off` addition.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Empirical bake-off before routing changes | RF.1 backlog item: role->(model,effort) hand-tuned with zero empirical basis |
| Deterministic rc==0 signal, no LLM judge | CQ independence warning (a model grading its own output); deterministic-first directive (observation must pay for itself) |
| Observe-only phase 1, recommendation never flips routing | measurement-before-control precedent (`security-baseline.md`, `risk-tier-routing.md`) |
| `--execute` operator-only, never in gates/scenarios | token-economy directive; cheap-models-for-LLM-tests rule (zero spend in CI paths) |
| tokens from stdout result JSON, ledger join deferred | phase-2 `cost_metrics` ledger delta (ponytail ceiling in `role_calibration.py`) |

## Gherkin scenarios

```gherkin
Feature: per-role (model, effort) bake-off — observe-only phase 1

  Scenario: [rc-1] plan_cells yields the full validated matrix
    Given the model-cards registry declares the requested cards and efforts
    When the operator plans a bake-off over 2 models and 2 efforts
    Then exactly 4 cells come back, one per (model, effort) pair
    And an unknown card or unsupported effort raises instead of planning

  Scenario: [rc-2] execute scores each cell deterministically and writes the report
    Given a stub task command that exits 0 or 1 depending on the model
    When the bake-off runs with execute
    Then each cell records pass by exit code plus wall duration
    And the value table lands in .harness/state/bakeoff/ with a recommended line

  Scenario: [rc-3] dry-run spawns nothing
    Given a runner that fails the scenario if it is ever invoked
    When the bake-off runs without execute
    Then the planned table prints and no command is spawned and no report is written
```

## Ceilings (upgrade paths)

- Cost signal is duration + optional stdout-reported tokens; phase 2 joins the
  `cost_metrics` ledger delta for real spend per cell.
- Report filenames are second-resolution UTC timestamps; add a counter suffix
  if concurrent same-root executes ever become a real workflow.
- The task command runs WITHOUT a shell (no `shell=True` sink): the raw string
  on Windows (CreateProcess parses it), `shlex.split` argv on POSIX — so it
  must name a real executable, not a shell builtin. No templating beyond
  `{model}`/`{effort}` string replacement.

## Test strategy

- Behaviors: full-matrix planning and validation raises (rc-1); execute path
  pass/fail scoring, report write, ranking and `recommended:` line (rc-2);
  dry-run inertness with an assert-not-called runner (rc-3); tokens joined from
  a stub result JSON; CLI dry-run against the real repo writes nothing.
- Edge cases: unknown card, effort outside the card's reasoning list, unknown
  effort level, task stdout that is not JSON, runner timeout/OSError marks the
  cell failed instead of aborting the matrix.
- Regression risks guarded: `routing show` shape unchanged; no report appears
  at the repo root from a dry-run.
- Coverage impact: enforced via `rc_role_calibration.py` (scenarios gate) +
  the module `__main__` self-check.

## Validation

- `python testing/scenarios/rc_role_calibration.py` — the Gherkin ids resolve
  as the literal check names `rc-1`, `rc-2`, `rc-3` (plus the supporting
  `rc-tokens-from-result-json`, `rc-cli:dry-run-default`,
  `rc-routing:show-intact` checks).
- `python scripts/harness_lib/role_calibration.py` — deterministic self-check.
- `feature-spec-conformance:role-calibration` green in the spec-pack gate.

## Amendments

(none yet — phase 2, feeding the recommendation into routing, will arrive as a
versioned amendment or its own spec once owner-approved)
