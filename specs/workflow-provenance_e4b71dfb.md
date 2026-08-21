# CQ.3 — workflow finalize provenance record

Status: Active (retrofit spec, 2026-07-12; behavior landed pre spec-per-item rule).

Door NEW (SPEC-116, retrofit of landed behavior): covered-check ran
`records search provenance` — hits are only pre-existing change/commit
records — and no spec under `specs/40-features/` owns finalize-time
provenance (`records-ledger.md` owns the ledger itself, not this producer;
`doc-find` unavailable in this worktree: no graphify-out). The landed
acceptance scenario is the acceptance record; this spec maps to its existing
checks. Zero behavior change.

## Goal

Finalizing a workflow leaves one queryable provenance record: a `records`
entry stating which workflow finished, with what status and profile, whether
it demands security review, and a handle (not a body) to the HARNESS_RESULT.

## Applicability

`workflow_finalize` (workflow lifecycle) calling
`harness_lib/records.add_entry` once per finalize. Covers the argument shape
of that single call site; the ledger's own storage/search semantics belong to
`records-ledger.md`.

## Requirements / invariants

1. **Queryable.** The finalize entry is found by `records.search` on the
   workflow id (kind `change`, title `workflow <wfid> finalized: <status>`,
   tags `workflow`, `provenance`).
2. **Subject only when targeted.** `subject` is stamped with the workflow's
   target when one is set; a self-workflow entry carries NO stored `subject`
   field and defaults to `self` on search.
3. **One-line body.** The body is a single line
   (`profile=… taskProfile=… status=… requiresSecurityReview=…`) — compact
   provenance, no embedded documents.
4. **Handles, not bodies.** `refs` carries exactly the `harnessResultPath`
   handle; the HARNESS_RESULT content is never inlined.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| One records entry per finalize | CQ.3 backlog item: workflow outcomes must be discoverable after the workflow dir is scrubbed |
| Handles-not-bodies | `.harness/prompts/subagent-contract.md` worker constraints; same norm as `qa-evidence-capsule.md` |
| Reuse the records ledger | no parallel provenance store — `records-ledger.md` is the single ledger |
| Subject stamped only for targets | keeps self-history unpolluted while target work stays attributable |

## Gherkin scenarios

```gherkin
Feature: finalize writes one provenance record

  Scenario: [search:finds-finalize-entry] the entry is queryable
    Given a finalized workflow
    When records.search runs on its workflow id
    Then the finalize entry is returned

  Scenario: [subject:stamped-when-target] target workflows are attributed
    Given a workflow with a target set
    Then the entry's subject is that target

  Scenario: [subject:absent-when-self] self workflows stay unstamped
    Given a workflow with no target
    Then the stored entry has no subject field

  Scenario: [search:self-defaults-subject] self defaults on search
    Given the unstamped self entry
    When it is searched
    Then its subject reads as self

  Scenario: [body:one-line] the body is compact
    Then the entry body contains no newline

  Scenario: [refs:handle-not-body] refs carry the handle
    Then refs equal exactly [harnessResultPath]
```

## Test strategy

- Behaviors: `records.add_entry` driven in a temp root with byte-for-byte the
  argument shape of the `workflow_finalize` call site — once with a target,
  once without — then asserted via `records.search` and the returned entries.
- Regression risk guarded: drift between the finalize call shape and what the
  ledger stores/searches (the scenario pins the shape).
- Temp-root only; the real ledger is untouched.

## Validation

- `python testing/scenarios/cq_provenance.py` — checks
  `search:finds-finalize-entry`, `subject:stamped-when-target`,
  `subject:absent-when-self`, `search:self-defaults-subject`, `body:one-line`,
  `refs:handle-not-body`.
- `feature-spec-conformance:workflow-provenance` green in the spec-pack gate.

## Amendments

(none yet)
