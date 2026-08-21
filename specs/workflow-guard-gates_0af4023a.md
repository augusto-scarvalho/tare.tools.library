# Workflow guard gates (`wfg`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/rh_wf_gates.py).

Intake (SPEC-116 door NEW): spec-recovery batch E, rec-wf-4/13/14 — three
shipped guard behaviors that decide whether a workflow may reduce, merge, or
finalize had NO spec documenting the contract and NO scenario exercising the
refusal path. Each is a safety gate that fires exactly when something is wrong
(workers still running, an unauthorized file appeared, a merge went in without
semantic review) — the worst place to discover a silent regression.

## Goal

The three guard contracts are written and permanently exercised: reduce
refuses while a run is live, merge-plan blocks an unauthorized new file, and
finalize refuses an unresolved semantic merge-review — each with its legible
message and each with its documented release path (`--allow-partial`, a
create/rename lock, `--skip-review` or a recorded approval).

## Applicability

Applies to `workflow_reduce.workflow_reduce`
(`scripts/harness_lib/workflow_reduce.py:242-256`),
`workflow_writes.workflow_merge_plan`
(`scripts/harness_lib/workflow_writes.py:110-260`, conflict detection at
`174-190`), and `workflow_lifecycle.workflow_finalize`
(`scripts/harness_lib/workflow_lifecycle.py:55-74`). Coverage is hermetic via
each module's `bind()` seam (wfrb/iwa pattern): test-local ROOT and helpers,
the real repo is never touched. wfg-1 and wfg-3 use the sentinel-probe idiom —
downstream helpers are no-ops and the first call past the guard raises a
caught sentinel, proving the guard was cleared without running the whole body.

## Requirements / invariants (numbered, testable)

1. **Reduce refuses on a live run.** `workflow_reduce` raises `HarnessError`
   containing `active run lock` while the run lock is active, and containing
   `queued/running` (plus the offending worker ids) while any worker is queued
   or running. `allow_partial=True` passes BOTH guards and proceeds into the
   reduce body (`workflow_reduce.py:244-256`).
2. **Merge-plan blocks unauthorized creates.** A file present in a worker's
   workspace that is covered by NO create-lock and NO rename `newPath`, is not
   excluded, and does not already exist at ROOT, is recorded as a
   `created-without-create-or-rename-lock` conflict; a write-locked file that
   exists at ROOT is NOT flagged. Any conflict sets the worker `readyForMerge`
   to false, sets plan `blocked` true and plan `status` to `blocked`
   (`workflow_writes.py:177-190, 214`).
3. **Finalize refuses an unresolved merge review.** When the semantic
   merge-review gate is `required` and `enforced` and not `approved`,
   `workflow_finalize` raises `HarnessError` containing `semantic merge review`
   before any finalize side effect; a recorded approval (`approved`) or
   `skip_review=True` clears it and finalize proceeds
   (`workflow_lifecycle.py:68-74`).

## Gherkin scenarios

```gherkin
Feature: workflow guard gates

  Scenario: [wfg-1] reduce refuses on a live run, allow_partial bypasses
    Given an active run lock, then a queued worker
    When workflow_reduce runs without allow_partial in each state
    Then it refuses with the active-run-lock and the queued/running messages
    When workflow_reduce runs with allow_partial while both hold
    Then both guards clear and the reduce body is reached

  Scenario: [wfg-2] merge-plan blocks a file with no create or rename lock
    Given a workspace with a write-locked modify and an extra unlocked new file
    When workflow_merge_plan runs
    Then the extra file is a created-without-create-or-rename-lock conflict,
      the write-locked file is not flagged, and the plan is blocked

  Scenario: [wfg-3] finalize refuses an unresolved semantic merge review
    Given a merge-review gate that is required, enforced and unapproved
    When workflow_finalize runs without skip_review
    Then it refuses requiring semantic merge review before any side effect
    When the review is approved, or skip_review is passed
    Then the gate clears and finalize proceeds
```

## Rationale & sources

| Decision | Sources |
|---|---|
| Cover the reduce guards via the bind() seam + sentinel probe | the guards raise before any side effect; the probe proves the bypass without running reduce — `workflow_reduce.py:242-256` |
| Assert the merge-plan conflict as the code actually computes it | the unauthorized-create branch keys off `workspace_files - allowed_new` and skips paths that exist at ROOT — verified at `workflow_writes.py:177-190`; `blocked`/`status` at `188-190, 214` |
| Drive finalize's enforcement block, cite the gate-status source | finalize enforces at `workflow_lifecycle.py:68-74`; the `required`/`approved` decision is computed by `workflow_reduce.workflow_merge_review_gate_status` (`workflow_reduce.py:457-476`) from `policy.writeAllowed` + a merge-apply result + the controlled-write config — the reduce result itself does not carry the flag |
| Door NEW (not amendment) | no existing spec documents these three guard contracts (rec-wf-4/13/14: "no spec, no scenario") |
| Evidence | spec-recovery INDEX rec-wf-4/13/14; code line ranges above |

## Test strategy

- Behaviors: reduce lock + queued refusals and the allow_partial bypass
  (wfg-1); unauthorized-create conflict + blocked plan, write-locked file left
  alone (wfg-2); finalize refusal + approval/skip-review release (wfg-3).
- Edge cases: bypass reaches exactly the first downstream call (probe hit once);
  a write-locked path that exists at ROOT is not mistaken for an unauthorized
  create.
- Regression net: gate_fixtures_workflow (controlled-write / lifecycle
  fixtures), spec-pack.
- Coverage: deterministic, stdlib-only, temp roots —
  `testing/scenarios/rh_wf_gates.py`.

## Validation

- `python testing/scenarios/rh_wf_gates.py` — wfg-1..wfg-3 green.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.
