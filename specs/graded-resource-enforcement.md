# SPEC-143 — Graded resource enforcement (resourcesRespected)

Status: SPEC-143, proposed 2026-07-13 (acceptance: `testing/scenarios/gre_graded_enforcement.py`).

## Goal

Upgrade the s2 role-resource allowlist from a contractual request to a GRADED
one. When a spawn prompt carries a `Resources for this role: skills=[...];
mcp=[...]` line (rendered from a profile's `tokenEconomy.allowedSkills` /
`allowedMcp`), the worker self-reports whether it honored the allowlist in a new
optional `resourcesRespected` field of HARNESS_RESULT, and the overseer reads
that field when grading the run. This is a CONTRACT + schema + grading
convention only — no code path enforces or blocks on the allowlist.

## Applicability

Applies to the HARNESS_RESULT contract: `schemas/harness-result.schema.json` (the
optional `resourcesRespected` object) and `.harness/prompts/subagent-contract.md`
(the worker instruction). It grades the allowlist line that
`scripts/harness.py` already renders from `tokenEconomy` (s2); it does NOT change
that rendering, does NOT add any runtime enforcement, sandbox, or block, and does
NOT touch the profiles in `.harness/routing/task-profiles.json`.

## Requirements / invariants (numbered, testable)

1. **Optional field, back-compat.** `resourcesRespected` is optional. An existing
   HARNESS_RESULT that omits it still validates against
   `schemas/harness-result.schema.json` (absent = ungraded).
2. **Shape.** When present, `resourcesRespected` is an object with a required
   boolean `respected` and an optional `loadedOutsideAllowlist` array of strings
   (the skills/MCPs loaded outside the role allowlist; empty when respected).
3. **False requires the escape list.** When `respected` is `false`,
   `loadedOutsideAllowlist` MUST be non-empty — a worker that broke the allowlist
   names what it loaded, so the overseer grades the escape instead of discovering
   it. `respected: true` carries an empty (or omitted) list.
4. **Graded by the overseer, not enforced by code.** The field is self-reported
   telemetry the overseer review reads; nothing in the harness blocks a spawn or
   truncates a load based on it.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Grade the allowlist rather than enforce it in code | `.harness/handoff/plan-q3-graded-enforcement.md` (gap #2: contractual → graded, no code-path change) |
| Reuse the s2 `Resources for this role` line as the trigger | `scripts/harness.py` `build_prompt` renders it from `tokenEconomy.allowedSkills`/`allowedMcp` (s2, `.harness/handoff/plan-s2-role-resource-allowlist.md`) |
| `respected:false` must name the offending items | An escape the overseer cannot see is ungraded; the list turns a silent breach into a reviewable one |
| Optional field = back-compat | Every result-contract addition in this harness is optional so prior results keep validating (SPEC-142 precedent) |

## Gherkin scenarios

```gherkin
Feature: SPEC-143 graded resource enforcement

  Scenario: [gre-1] a graded result matches the resourcesRespected shape
    Given the harness-result schema's resourcesRespected definition
    When a worker reports respected with a string list of any escapes
    Then the field validates against that shape
    And a non-boolean respected or a missing respected is rejected

  Scenario: [gre-2] respected:false requires the escape list
    Given a worker that reports it broke the role allowlist
    When it sets respected to false
    Then loadedOutsideAllowlist must be non-empty
    And respected:true with an empty list stays consistent

  Scenario: [gre-3] an ungraded result stays back-compatible
    Given an existing harness-result that omits resourcesRespected
    When it is validated against the harness-result schema
    Then it still validates green
```

## Ceilings (upgrade paths)

Grading is self-reported honesty, not enforcement: a worker can under-report an
escape. That is deliberate (the plan forbids code-path changes). If self-report
proves unreliable, the upgrade path is an owner-gated runtime observer that
records actually-loaded skills/MCPs and cross-checks the field — one new
seam, not a hardening of this contract.

## Test strategy

- Behaviors to verify: the field shape validates and rejects a bad-typed/missing
  `respected` (gre-1); `respected:false` requires a non-empty
  `loadedOutsideAllowlist` while `respected:true` allows empty (gre-2); a result
  omitting the field still validates (gre-3).
- Edge cases: `loadedOutsideAllowlist` omitted entirely with `respected:true`
  (consistent); `respected:false` with an empty list (inconsistent — must fail
  the invariant).
- Regression risks: the addition is optional, so no existing HARNESS_RESULT can
  be invalidated; the schema stays lenient (`additionalProperties`).
- Coverage impact: enforced via `testing/scenarios/gre_graded_enforcement.py`.

## Validation

- `python testing/scenarios/gre_graded_enforcement.py` — gre-1..gre-3 green (the
  scenario validates the field shape against `schemas/harness-result.schema.json`
  and checks the respected/false consistency invariant plus absent-field
  back-compat).
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` — template
  conformance + Gherkin id mapping + the schema still validates existing results.
- `python tools/hooks/protect_canonical_files.py check` — the ADD-only edit to
  the protected `subagent-contract.md` is reflected in the snapshot.

## Amendments

(none yet)
