# SPEC-158 — Gate observability: the `gate-perf` read verb

Status: SPEC-158, proposed 2026-07-20 (acceptance: `testing/scenarios/wfo_gate_perf.py`).
Origin: backlog `wf-gate-observability` (WF roadmap, research round 2026-07-20,
`docs/research/loop-workflow-efficiency-round.md`). Door: covered surface —
`spec_test_gate` already records the sidecar; this spec adds only a read verb
over it (SPEC-116 flow, existing-spec-neighbour `gate-perf-governance.md`).

## Goal

Surface WHERE the 7-15min scenarios gate spends its time so every later WF item
(cache, affected-selection, parallelism, pipelining, the speculative
experiment) can be measured against a real baseline. Theory of Constraints: you
cannot exploit a constraint you cannot see. The verb is a pure read/summary over
the sidecar the gate already writes — it captures no new timing and changes no
gate logic (correctness-neutral).

## Applicability

`harness.py gate-perf` (handler `harness_lib/gate_perf.py`, registered via
`cli_registry.register`). It reads only `.harness/runs/gate-perf.jsonl` — the
per-attempt `{scenario,attempt,snapshotS,subprocessS,restoreS,rc}` rows written
by `spec_test_gate._run_isolated_scenario` and flushed per run. It does NOT
instrument scenarios, spawn processes, call a model, or write any file. It does
not evaluate target-repo data (target gate runs write their own rows; a
per-target view is future work, mirroring `gate-perf-governance.md`).

## Requirements / invariants (numbered, testable)

1. **Read-only over existing data.** The verb never writes, spawns, or calls a
   model; it only aggregates existing sidecar rows. No timing capture is added.
2. **Per-scenario aggregate.** Over the last N runs each scenario reports
   `count`, `p50S` and `maxS` of `subprocessS`, `totalS` (summed attributed
   time), and `sharePct` (its `totalS` / the total `subprocessS`).
3. **Ranked slowest-first.** Scenarios sort by `totalS` descending (the drum's
   hot spots), ties broken by name for determinism.
4. **Isolation tax.** The output reports summed `snapshotS` + `restoreS`
   (overhead) against summed `subprocessS` (body), and the overhead share of
   attributed wall.
5. **`--last N` window.** Aggregation covers the last N runs (default 10);
   `--json` emits the full machine object (all scenarios), the plain table caps
   at the hottest few with a "more" footer.
6. **Fail-open empty state.** A missing, empty, or partly-corrupt sidecar yields
   a clean empty-state result (`runs=0`, no scenarios) and rc 0 — never a raise
   and never a partial-parse crash.
7. **Reserved counters, no fabrication.** `cacheHit`, `cacheMiss`, and
   `speculativeMisprediction` are documented and carried through a `reserved`
   block IF a row already has them, but this reader never invents them (their
   producers are later WF items: `wf-gate-result-cache`, `wf-speculative-gate`).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Measure the drum before optimizing it | Theory of Constraints (Goldratt); WF research round 2026-07-20 build order (observability first) |
| Read verb over the existing sidecar, no new capture | EXP-11 lesson (instrumentation perturbs); the EXP-12 sidecar (`spec_test_gate._PERF_ROWS`) already exists |
| p50 + max + share, ranked | DORA / CI-analytics practice [web]: percentiles over means, rank by contribution |
| Reserve cache/speculation counters, do not fabricate | Backlog `wf-gate-observability` scope + YAGNI (no producer exists yet) |

## Gherkin scenarios (UI surfaces only)

The verb is a CLI read surface; its Gherkin ids resolve to the named checks in
`testing/scenarios/wfo_gate_perf.py`.

```gherkin
Feature: See where the gate spends its time

  Scenario: [wfo-1] the slowest scenario ranks first
    Given a gate-perf sidecar where one scenario dominates subprocess time
    When the operator asks for the gate-perf aggregate
    Then that scenario ranks first with its p50, max, total and share-of-gate

  Scenario: [wfo-2] the machine view carries the aggregate shape
    Given the same sidecar
    When the operator asks for the JSON aggregate
    Then it carries runs, attempts, scenarios and the isolation tax, shares sum to 100%, and no fabricated cache counters appear

  Scenario: [wfo-3] an empty sidecar fails open
    Given a missing or empty gate-perf sidecar
    When the operator asks for the gate-perf aggregate
    Then the result is a clean empty state with no scenarios and never raises
```

## Ceilings (upgrade paths)

- Plain-file JSONL read of the whole sidecar (log-rotation already spills it);
  move to an indexed store only if the sidecar outgrows a full read.
- Table caps at the 20 hottest scenarios; `--json` returns all. Add paging only
  if a real need appears.
- Self-only. A `--target` per-repo view lands when the multi-repo era does
  (same code, different root), exactly as `gate-perf-governance.md` describes.

## Test strategy

- Behaviors to verify: slowest-first ranking with correct p50/max/total/share;
  `--json` shape and share-sum; `--last N` window narrowing; isolation-tax math;
  reserved counters absent by default and carried through when present.
- Edge cases: empty file, missing file, corrupt line (all fail open).
- Regression risks: none — no gate logic or timing capture is touched.
- Coverage impact: enforced via `testing/scenarios/wfo_gate_perf.py`.

## Validation

- `python testing/scenarios/wfo_gate_perf.py` green (checks `wfo-1`, `wfo-2`,
  `wfo-last`, `wfo-3`).
- `python scripts/harness_lib/gate_perf.py` self-check green.
- `python scripts/harness.py gate-perf --json` emits valid JSON on the real
  repo; `python scripts/harness.py gate-perf` prints the ranked table.
- `spec-pack` (feature-spec-conformance) green; `cli_registry` +
  `cc_cli_catalog` scenarios green with `gate-perf` added to `FROZEN_TOP_LEVEL`.

## Amendments

- 2026-08-03 — Incremental partial stream (hard-kill survival). The sidecar was
  flushed ONLY at settle, so the two 1800s hard-kills of 2026-08-03 left zero
  per-scenario rows for exactly the runs worth reading (dossier
  `.harness/handoff/gate-latency-dossier.md`). `gate_perf.PartialRows` — the type
  the gate's `_PERF_ROWS` accumulator now is — streams each row to
  `.harness/runs/gate-perf-partial.jsonl` as it is produced (thread-safe append,
  lazy first-write so importing the gate is still side-effect-free);
  `recover_orphan` folds a dead run's orphan into the canonical sidecar as one
  `{at, rows, partial: true}` line on the next run's first row, and `flush_run`
  removes the file at settle. The stream is only as incremental as PRODUCTION is:
  the serial path and the abort rows are produced per attempt (streamed one by
  one), but the parallel pool emits all its rows in one batch after
  `verdicts_parallel` returns, so a kill mid-pool still loses pool-phase
  telemetry. Residual window: an external 1800s kill racing a contention-degraded
  pool (the ~20+ min outliers) — NOT the 2026-08-03 incident shape, which the
  dossier proves were serial-fallback grinds. Per-shard streaming is the upgrade
  path if that window ever bites. Invariant 1 is unchanged for the VERB (still a
  pure reader); the writer lives beside the existing `flush_run`/`log_tier_level`
  writers in the same module. The gate's start-of-run artifact cleanup now spares
  this file and `gate-parallel-aborts.jsonl` — both are hard-kill survivors that
  the very next run must read before wiping. Teeth: `gate_perf` self-check
  (registered in `testing/scenarios/hk_hook_selfchecks.py`).
