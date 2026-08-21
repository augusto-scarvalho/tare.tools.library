# DW.4 — topology router (observe-only fork verdict)

Status: Active (retrofit spec, 2026-07-12; behavior landed pre spec-per-item rule).

Door NEW (SPEC-116, retrofit of landed behavior): covered-check ran
`records search "topology router"` — hits are only the landed batch's commit
records — and no spec under `specs/40-features/` owns topology routing
(`doc-find` unavailable in this worktree: no graphify-out). The landed
acceptance scenario is the acceptance record; this spec maps to its existing
checks. Zero behavior change.

## Goal

At plan time, stamp every workflow with an observe-only topology verdict —
whether the work COULD fork across workers and why — while pinning the actual
worker count to 1, so fork-eligibility is measured before anyone routes on it.

## Applicability

`scripts/harness_lib/topology_router.py` (`verdict`) plus the plan-time stamp
(`topologyRouter` key in `workflow.json`) written by `harness.plan_workflow`.
Deterministic, stdlib-only, no LLM. Observe-only: nothing consumes the verdict
to spawn workers yet.

## Requirements / invariants

1. **Exact fork rule.** `wouldFork` is EXACTLY
   `shard_count > 1 and maxWorkers > 1 and not open_circuits`.
2. **Named blockers.** An open circuit blocks the fork AND is named in
   `reasons` (`circuit open: <provider>`); `maxWorkers == 1` also blocks.
3. **Pinned to 1.** `recommendedWorkers` is 1 in EVERY case
   (measurement-before-control) — eligible or not.
4. **Stamped and schema-clean.** `workflow plan` writes a `topologyRouter`
   verdict (`wouldFork` bool, `reasons` list, `inputs` dict,
   `recommendedWorkers == 1`) into `workflow.json`, and the DW.2 schema gate
   accepts the stamped packet.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Observe-only verdict, workers pinned to 1 | DW.4 backlog item + measurement-before-control precedent (`security-baseline.md`, CQ.1) |
| Reasons name the blocker | legible failures norm (supervision M1): a verdict nobody can explain routes nothing |
| Stamp lives in the typed IR | `workflow-typed-ir.md` (DW.2): plan-time facts belong in the validated packet, not a side file |

## Gherkin scenarios

```gherkin
Feature: observe-only topology-router verdict

  Scenario: [dw4:would-fork-when-eligible] eligible work would fork
    Given shards > 1, maxWorkers > 1 and no open circuits
    When verdict runs
    Then wouldFork is true and recommendedWorkers is still 1

  Scenario: [dw4:open-circuit-blocks-fork] an open circuit blocks the fork
    Given an open provider circuit
    When verdict runs
    Then wouldFork is false and reasons name "circuit open: <provider>"

  Scenario: [dw4:max-workers-1-blocks-fork] maxWorkers 1 blocks the fork
    Given maxWorkers of 1
    When verdict runs
    Then wouldFork is false and recommendedWorkers is 1

  Scenario: [dw4:plan-stamps-observe-only-verdict] plan stamps the packet
    Given the cheapest workflow plan
    Then workflow.json carries a topologyRouter verdict with
      recommendedWorkers 1, a bool wouldFork, a reasons list and an inputs dict,
      and the packet still validates against the DW.2 schema gate
```

## Test strategy

- Behaviors: `verdict` driven directly on the three rule cases (unit), then a
  real cheapest `workflow plan` asserted for the on-disk stamp (integration).
- Regression risk guarded: any consumer accidentally raising
  `recommendedWorkers` above 1 while the feature is observe-only (rule 3 is
  asserted in every case).
- Scenario leaves the repo clean (workflows scrubbed, logs restored).

## Validation

- `python testing/scenarios/dw_topology_router.py` — checks
  `dw4:would-fork-when-eligible`, `dw4:open-circuit-blocks-fork`,
  `dw4:max-workers-1-blocks-fork`, `dw4:plan-stamps-observe-only-verdict`.
- `feature-spec-conformance:topology-router` green in the spec-pack gate.

## Amendments

(none yet)
