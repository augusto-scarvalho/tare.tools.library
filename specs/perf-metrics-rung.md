# Perf-metrics rung — gate wall-time ledger (Phase 1 of the PyO3 roadmap)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/pm_perf_metrics.py).

Intake (SPEC-116 door NEW): request = "seria bom ter MÉTRICAS dos processos
para fazer TRACKING daquilo que pode ser otimizado com o tempo… de preferência
DETERMINISTICAMENTE" (`docs/roadmap/pyo3-optimization.md`). Covered-check: the
gate/test path — exactly the surface expected to grow heavy — has zero
structured timing (fixture elapsed lives in prose detail strings; the run log
carries counts only). Decision: **NEW**. SLICE: Phase 1 ONLY — measurement.
`perf-hotspot-watch-rule` (Phase 2) and `pyo3-accel-prototype` (Phase 3,
parked until the rule fires on real data) stay OPEN in the backlog.

## Goal

Every gate run leaves one small deterministic ledger record — total wall time,
check count, top-5 slowest coarse blocks — and `summarize()` exposes the
trendable view (`gates`: stats, byGate, bySlowest recurrence, series) that the
future watch rule consumes. Measurement before control: nothing here flags or
rewrites anything.

## Applicability

Applies to `scripts/spec_test_gate.py` (`result()` durationMs, coarse-block
timing in `main()`, the `record_gate` call), `scripts/harness_lib/
cost_metrics.py` (`record_gate`, `GATE_RECORDS_MAX`, the `gates` summarize
section, `_slowest_recurring`) and `scripts/harness_lib/graphify_code_ast.py`
(stats `durationS`). No behavior of any check changes — timing is additive;
no daemon, no polling, no LLM. Phases 2/3 of the roadmap are NOT implemented
here.

## Requirements / invariants (numbered, testable)

1. **Machine-readable timing at the units that grow.** `result()` accepts an
   optional `durationMs`; every treasury scenario row carries it; isolated
   fixtures and coarse main() blocks (`core-checks`, `fixture:*`,
   `scenario:*`, `tail-checks`) are timed via `time.monotonic()` wraps.
   ponytail: block granularity on cheap structural checks — split a block into
   per-check timing only if it recurs in the slowest table.
2. **One ledger record per gate run.** `cost_metrics.record_gate(root, gate=,
   status=, total_s=, checks=, slowest=)` stores
   `{kind:"gate", durationS, checks, slowest[:5] sorted desc}`; called once at
   the end of `spec_test_gate.main()`; never-crash like every ledger writer.
3. **Per-kind trim (the Phase-1 crowding decision).** Gate records land on
   every run, so `GATE_RECORDS_MAX=150` trims oldest gate records BEFORE the
   shared `MAX_RECORDS` cap — gate telemetry can never evict chat/workflow
   history.
4. **Trendable view.** `summarize()["gates"]` = runs, `durationS` stats,
   `byGate` grouping, `bySlowest` (per-block recurrence count + medianS) and a
   ≤20-row chronological `series` — the same shape the delegation trend family
   already consumes.
5. **Module self-timing at the one plausible PyO3 seam.**
   `build_graphify_code_ast` stamps `durationS` into `graph["stats"]` and its
   return payload.
6. **Pays for itself.** The capture is monotonic wraps + one JSON append per
   gate run against a capped ledger; the existing `summarizeMs` sentinel stays
   the overhead watchdog (<1% of gate wall budget).

## Gherkin scenarios

```gherkin
Feature: perf-metrics rung (measurement before control)

  Scenario: [pm-1] a gate run records its shape
    Given record_gate with seven timed blocks
    When the record lands
    Then it carries kind gate, rounded durationS, the check count and the
      top five blocks sorted descending

  Scenario: [pm-2] summarize exposes the trendable gates view
    Given four gate records across two gates naming a recurring block
    When summarize runs
    Then gates.runs/durationS/byGate/bySlowest (count + medianS) and the
      chronological series are all present and bounded

  Scenario: [pm-3] gate telemetry never evicts other history
    Given a chat-turn record and more gate records than the per-kind cap
    When record_gate keeps appending (and the ledger is later corrupted)
    Then gate records stay at the cap, the chat-turn survives, and the
      corrupt-ledger write never raises

  Scenario: [pm-4] the wiring is live
    Given the gate source and a tiny temp tree
    When inspected and graph-built
    Then treasury rows are stamped with durationMs, record_gate is called at
      the end of main(), and graphify stats carry a measured durationS
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Medição antes de controle; a regra (fase 2) e o PyO3 (fase 3) ficam ABERTOS | roadmap `pyo3-optimization.md` ("masking-before-measurement inverts the cost equation"); memória net-cost-positive |
| Espelho de `record_workflow` + rung M1 stdoutBytes | `cost_metrics.py record_workflow`; `self_review_rules.py` M1 rung |
| Trim por-kind em vez de subir o cap global | roadmap open decision resolvida aqui: gate records ~vários/dia × cap 500 compartilhado |
| Blocos grosseiros, não por-check | os pesados reais são scenarios/fixtures (roadmap ground-truth table); overhead <1% |
| `bySlowest`/`series` no shape da família delegation-trend | `cost_metrics.py` `_group`/`series` precedent (OB.2) |
| Graphify é o único candidato PyO3 plausível — auto-mede primeiro | roadmap candidate shortlist #1 |

## Test strategy

- Behaviors: record shape + top-5 bound (pm-1); the summarize view incl.
  bySlowest median (pm-2); per-kind trim + other-kind survival + corrupt
  ledger never-crash (pm-3); wiring source-assert + real graphify build timing
  on a temp tree (pm-4).
- Edge cases: empty gates list → empty stats (summarize's `_stats([])`);
  slowest omitted → empty list; timings are synthetic in tests (wall-time
  nondeterminism stays out of assertions, per the roadmap).
- Regression net: `cost_metrics` module self-check (`python
  scripts/harness_lib/cost_metrics.py`) keeps every pre-existing summarize
  assertion green; the live gate run itself writes the first real record.
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/pm_perf_metrics.py`.

## Validation

- `python testing/scenarios/pm_perf_metrics.py` — pm-1..pm-4 green.
- `python scripts/harness_lib/cost_metrics.py` — ledger self-check intact.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  conformance + a real `kind:"gate"` record lands in the ledger.
