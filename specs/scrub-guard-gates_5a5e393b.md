# Scrub guard gates (`wsg`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/rh_scrub_gates.py).

Intake (SPEC-116 door NEW): coverage recovery for rec-wf-15/16. The shipped
secret collection boundary, reduce defense scan, and destructive workflow scrub
guards had no dedicated scenario proving their refusal and release paths.

## Goal

Secret-shaped worker results are withheld without echoing the raw value, and
workflow scrub cannot delete an active or unsafe workflow accidentally. The
release paths are explicit: a safe lifecycle phase, or deliberate `force=True`.

## Applicability

Applies to `workflow_reduce.workflow_validate_results`
(`scripts/harness_lib/workflow_reduce.py:67-140`), the reduce-output rescan in
`workflow_reduce.workflow_reduce` (`workflow_reduce.py:336-341`), and
`workflow_lifecycle.workflow_scrub`
(`scripts/harness_lib/workflow_lifecycle.py:267-313`). Coverage is hermetic via
the modules' `bind()` seams: all workflow roots are temporary, callbacks are
test-local, and `_rmtree_robust` is a sentinel probe that raises at the first
deletion boundary instead of deleting anything.

## Requirements / invariants (numbered, testable)

1. **Collect withholds secret-shaped results.** Before schema validation,
   `workflow_validate_results` scans each decoded worker result. A hit records
   only its pattern, location, and redacted marker in an `invalid` failure whose
   message says `withheld`; it marks the worker failed, excludes it from valid
   results, and sets `requiresSecurityReview` (`workflow_reduce.py:93-105,
   119-140`). The raw key is absent from validation output. The completed reduce
   object is scanned again; any hit sets `requiresSecurityReview` and adds the
   scanner's redacted hit records as `secretScanFindings`
   (`workflow_reduce.py:336-341`).
2. **Scrub refuses unsafe state.** `SCRUB_SAFE_PHASES` is exactly `planned`,
   `finalized`, and `rolled_back` (`workflow_lifecycle.py:28`). Without force,
   scrub refuses an active workflow lock before considering phase
   (`278-283`), refuses any populated workflow outside the safe phases
   (`284-289`), and reaches `_rmtree_robust` only after those guards clear
   (`290-294`).
3. **Scrub has legible calm paths.** If neither the active workflow directory
   nor state-store mirror exists, scrub raises a message containing `has nothing
   to scrub` and the `workflow list` recovery command (`workflow_lifecycle.py:
   267-275`). `force=True` bypasses both lock and phase refusals and reaches the
   deletion boundary even from a forbidden phase (`278-294`).

## Gherkin scenarios

```gherkin
Feature: secret and workflow scrub guard gates

  Scenario: [wsg-1] collect withholds and redacts a secret-shaped worker result
    Given a worker result containing a fake OpenAI-shaped key
    When workflow_validate_results collects it
    Then the result is invalid and withheld, security review is required,
      and the raw key appears in no validation output
    When workflow_reduce constructs its completed output
    Then it consumes the reduce scanner's redacted findings and requires security review

  Scenario: [wsg-2] workflow scrub refuses unsafe state without force
    Given workflows in a forbidden phase, under an active lock, and in a safe phase
    When workflow_scrub runs without force
    Then the forbidden phase and active lock refuse before deletion
    And the safe phase reaches the deletion-boundary sentinel

  Scenario: [wsg-3] workflow scrub handles missing and forced workflows
    Given a nonexistent workflow and a workflow in a forbidden phase
    When scrub runs normally for the missing workflow and with force for the other
    Then the missing workflow refuses with a recovery command
    And force reaches the deletion-boundary sentinel
```

## Rationale & sources

| Decision | Sources |
|---|---|
| Collect through the real scanner before validation | The scan precedes `validate_worker_result`; hits are redacted, withheld, and security-signaled at `workflow_reduce.py:93-105`. |
| Exercise the reduce rescan through its scanner contract | The completed result is scanned without its existing review flag; returned redacted hits set the flag and are attached at `workflow_reduce.py:336-341`. The scan reports hits; it does not rewrite arbitrary originating fields, so the scenario does not claim that it does. |
| Probe `_rmtree_robust` rather than deletion | The helper is the first destructive call after both guards (`workflow_lifecycle.py:290-294`); a caught sentinel proves progress without touching real state. |
| Plan line-range correction | The plan's `278-289` range covers the lock and phase guards. The missing-workflow calm path is earlier at `270-275`, and successful deletion starts at `290-294`; the scenario and requirements cite the actual ranges. |
| Door NEW (coverage spec) | Per the overseer plan, this allocates no feature id and follows the existing `workflow-guard-gates.md` coverage-spec shape. |

## Test strategy

- Behaviors: actual secret-shape scan, withholding/redaction/security flag, and
  reduce rescan contract (`wsg-1`); active-lock and forbidden-phase refusals plus
  safe-phase release (`wsg-2`); missing-workflow recovery plus forced release
  (`wsg-3`).
- Negative evidence: the fake raw key is absent from every produced validation
  and reduce artifact inspected by the scenario; deletion is never executed.
- Coverage: deterministic, EN-only, stdlib-only, temporary roots, bind seams,
  and sentinel probes in `testing/scenarios/rh_scrub_gates.py`.

## Validation

- `.venv\Scripts\python.exe testing/scenarios/rh_scrub_gates.py` — `wsg-1`
  through `wsg-3` green.
- `.venv\Scripts\python.exe scripts/spec_test_gate.py spec-pack --no-project-commands`
  — feature-spec sections and Gherkin ids resolve; gate green.
