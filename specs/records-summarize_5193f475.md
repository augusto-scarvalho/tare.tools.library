# M5.sum - Deterministic records digest

Status: implemented 2026-07-13 (acceptance: `testing/scenarios/rsm_records_summarize.py`).

## Goal

Provide a compact, deterministic summary of matching ledger records without an
LLM call or network access.

## Applicability

Applies to `records.summarize` and the `records summarize` CLI action. It does
not add judgment, generated prose, remote storage, or an LLM-backed path.

## Requirements / invariants (numbered, testable)

1. **Deterministic digest.** Matching records produce total, kind, subject, and
   date-range counts plus at most ten newest-first source handles.
2. **Existing query semantics.** Terms, kind, and limit use the ledger's
   existing search path; the digest echoes those inputs.
3. **Calm empty result.** No matches produce zero and empty aggregates without
   raising.
4. **Additive CLI action.** `records summarize` emits the digest as JSON and is
   listed by `records --help` without adding a top-level verb.
5. **Offline stub.** Summarization is stdlib-only, deterministic, and makes no
   LLM or network call.

## Rationale & sources

| Decision | Sources |
|---|---|
| Fold existing search results | M5.sum overseer plan; SPEC-112 query path |
| Keep the path deterministic and offline | Gate-approved backlog stub decision |
| Add an action, not a top-level verb | Frozen top-level CLI surface |

## Gherkin scenarios

```gherkin
Feature: Deterministic records digest

  Scenario: [rsm-1] seeded records produce a bounded digest
    Given ledger records across two kinds and dates
    When the operator summarizes all records
    Then counts, kinds, date range, and source ordering are correct

  Scenario: [rsm-2] filters narrow the digest and empty matches stay calm
    Given ledger records with distinct terms and kinds
    When the operator summarizes with term and kind filters
    Then only matching records are counted and no match returns calm zeros

  Scenario: [rsm-3] the records summarize CLI action is wired
    Given the records command
    When the operator requests a summary and command help
    Then summary exits successfully and help lists the action
```

## Test strategy

- Behaviors: aggregate counts, date range, subject counts, newest-first source
  handles, term/kind filters, calm empty results, and real CLI wiring.
- Edge cases: no timestamps and no matching rows.
- Regression risks: changing search semantics or the frozen top-level CLI.
- Coverage impact: deterministic scenario coverage; no configured line metric.

## Validation

- `.venv\Scripts\python.exe testing/scenarios/rsm_records_summarize.py`
  verifies checks `rsm-1`, `rsm-2`, and `rsm-3`.
- `.venv\Scripts\python.exe testing/scenarios/cli_registry.py` guards the
  frozen top-level CLI surface.
- `.venv\Scripts\python.exe scripts/spec_test_gate.py spec-pack --no-project-commands`
  validates spec and scenario conformance.
