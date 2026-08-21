# OB.4 - Failure-focused trace digest

Status: proposed 2026-07-13 (acceptance: `testing/scenarios/obd_trace_digest.py`).

## Goal

Provide a compact, deterministic `workflow trace <wfid> --digest` view that
shows what happened and where a workflow broke without re-dumping its logs.

## Applicability

Applies to the existing `workflow trace` CLI command and workflow trace spans.
It is read-only and does not cover trace export, network delivery, log content,
or automated diagnosis.

## Requirements / invariants (numbered, testable)

1. **Bounded timeline.** The digest selects the first and last spans, error-ish
   spans, and `harness.workflow*` phase spans in chronological order, capped at
   20 entries with error spans prioritized when the cap is reached.
2. **Failure evidence.** Each worker with an error-ish span reports its last
   status, first error span, and existing stdout/stderr log paths relative to
   the repository root.
3. **Existing summary.** The digest reuses the trace summary and adds error span
   and affected-worker counts.
4. **Calm absence.** An empty or absent trace returns zero spans with empty
   timeline and failure lists.
5. **Additive CLI.** `--digest` is a flag on the existing `workflow trace`
   command; the default trace output remains unchanged.

## Rationale & sources

| Decision | Sources |
|---|---|
| Fold existing spans instead of logs | OB.4 overseer plan; existing `workflow_trace()` contract |
| Keep the timeline bounded and failure-focused | OB.4 review-cost goal and 20-entry ceiling |
| Return only relative evidence paths | OB.4 portability and data-minimization constraints |
| Add a flag instead of a subcommand | Frozen workflow command surface guarded by `wt_workflow_tree.py` |

## Gherkin scenarios

```gherkin
Feature: Failure-focused workflow trace digest

  Scenario: [obd-1] a failed worker is visible with bounded evidence
    Given a workflow trace with phase changes and a worker error
    When the operator requests the trace digest
    Then the timeline is bounded and the worker failure links to its log evidence

  Scenario: [obd-2] an absent trace is calm
    Given a workflow without a trace file
    When the operator requests the trace digest
    Then it reports zero spans with no timeline or failures

  Scenario: [obd-3] the digest flag is available on the existing command
    Given the workflow trace command
    When the operator requests help
    Then help exits successfully and lists the digest flag
```

## Test strategy

- Behaviors: seeded span folding, error summary, relative evidence paths, empty
  trace handling, and real CLI help wiring.
- Edge cases: more than 20 timeline candidates and a missing stdout log.
- Regression risks: changing default trace output or adding a workflow command.
- Coverage impact: deterministic scenario coverage; no configured line metric.

## Validation

- `.venv\Scripts\python.exe testing/scenarios/obd_trace_digest.py` verifies
  checks `obd-1`, `obd-2`, and `obd-3`.
- `.venv\Scripts\python.exe testing/scenarios/wt_workflow_tree.py` guards the
  frozen workflow command surface.
- `.venv\Scripts\python.exe scripts/spec_test_gate.py spec-pack --no-project-commands`
  validates spec and scenario conformance.
