# DW.2 — workflow.json as the typed workflow IR (plan-time schema gate)

Status: Active (retrofit spec, 2026-07-12; behavior landed pre spec-per-item rule).

Door NEW (SPEC-116, retrofit of landed behavior): covered-check ran
`records search "typed IR"` — hits are only the landed batch's commit records —
and no spec under `specs/40-features/` owns the workflow packet schema
(`doc-find` unavailable in this worktree: no graphify-out). The landed
acceptance scenario is the acceptance record; this spec maps to its existing
checks. Zero behavior change.

## Goal

Every planned workflow materializes a `workflow.json` that is a typed IR:
validated at plan time against `schemas/workflow.schema.json`, so a malformed
packet is rejected with a named JSON path instead of failing later downstream.

## Applicability

`scripts/harness_lib/workflow_schema.py` (`validate_packet`) called from
`harness.plan_workflow` for every workflow type. Deterministic, stdlib-only,
no LLM. Does not cover worker/reduce result contracts (those have their own
validators).

## Requirements / invariants

1. **Zero migration.** Planning EACH workflow type (`map-reduce`, `fork-join`)
   materializes a `workflow.json` that validates green against
   `schemas/workflow.schema.json` — pre-existing packets pass unchanged.
2. **Closed top level.** An unknown top-level key trips
   `additionalProperties: false`; the raised `HarnessError` names the bad key
   and its JSON path (`$.` prefix).
3. **Typed workflowId.** A `workflowId` that does not match the schema's
   (byte-identical) pattern is rejected, and the error names both the field
   and the pattern.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Validate at plan time, not consume time | DW.2 backlog item: fail at the door with a JSON path, not deep in lifecycle code |
| Schema as the single IR contract | `schemas/workflow.schema.json` already existed as documentation; activating it removes schema↔code drift |
| Zero-migration guard | rule 1 proves activation broke no existing packet shape |

## Gherkin scenarios

```gherkin
Feature: workflow.json activated as the typed IR

  Scenario: [dw2:zero-migration-all-types-green] every planned type validates
    Given a workflow planned for each workflow type
    When its materialized workflow.json is validated against workflow.schema.json
    Then every packet validates green with no migration

  Scenario: [dw2:typo-key-rejected] an unknown top-level key is rejected
    Given a valid packet with a typo'd extra top-level key
    When the packet is validated
    Then a HarnessError names the bad key and its $.-prefixed JSON path

  Scenario: [dw2:bad-workflowId-rejected] a malformed workflowId is rejected
    Given a valid packet whose workflowId violates the schema pattern
    When the packet is validated
    Then a HarnessError names workflowId and the pattern
```

## Test strategy

- Behaviors: plan each type and validate on-disk packets (positive); mutate a
  real packet with a bogus key and a bad `workflowId` (negative).
- Regression risk guarded: schema drift that rejects packets the planner
  itself produces (rule 1 catches it on every run).
- Scenario leaves the repo clean (workflows scrubbed, logs restored).

## Validation

- `python testing/scenarios/dw_workflow_schema.py` — checks
  `dw2:zero-migration-all-types-green`, `dw2:typo-key-rejected`,
  `dw2:bad-workflowId-rejected`.
- `feature-spec-conformance:workflow-typed-ir` green in the spec-pack gate.

## Amendments

(none yet)
