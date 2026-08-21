# SPEC-000 — Title

<!--
SPEC-116 template (the rich de-facto format the strong specs already use, e.g.
specs/40-features/model-routing.md). Door NEW starts from
specs/templates/intake-refinement.md; the accepted intake seeds the numbered
rules AND the Gherkin scenarios below. The spec-pack gate
(feature-spec-conformance) checks the REQUIRED sections deterministically:
Goal, Applicability, "Requirements / invariants", "Rationale & sources",
"Test strategy", "Validation". Keep those heading names. Amendments are
appended as versioned sections (v2, v3, …) — never rewrite an earlier one.

Delete these comments and the mini example at the bottom before shipping.
-->

Status: SPEC-000, proposed <date> (acceptance: `testing/scenarios/<file>.py`).

## Goal

Describe the behavior, constraint, or capability this spec owns — one paragraph.

## Applicability

State where this applies (modules, surfaces, call sites) and what it explicitly
does not cover.

## Requirements / invariants (numbered, testable)

Numbered normative rules. Each must be independently testable — an implementer
reports deviations against these numbers.

1. **Short name.** The rule, stated so a check can pass or fail on it.
2. **Short name.** …

## Rationale & sources

Every normative decision carries a source — external literature, an in-repo
incident, or a measured fact. "Seemed good" is not a source (SPEC-116 inv. 7).

| Decisão | Fontes |
|---|---|
| The decision this spec makes | The paper / incident / measurement that grounds it |

## Gherkin scenarios (UI surfaces only)

Include this section only when the rules touch a UI surface (SPEC-116 inv. 4;
the UI-required judgment stays human). Grammar the gate enforces:

- One ` ```gherkin ` fenced block.
- Each scenario line: `Scenario: [<check-id>] <title>`.
- `<check-id>` MUST resolve to a named check (a `check("<id>", …)` string
  literal) in a `testing/scenarios/*.py` file this spec's **Validation** section
  references — an orphan id fails the gate.
- Declarative, business-readable Given/When/Then, **< 10 steps**, no
  keystroke/CSS-selector detail. Written at refinement time with the human,
  never generated post-hoc from the implementation (SPEC-116 inv. 5).

```gherkin
Feature: <the capability, in one line>

  Scenario: [<check-id>] <behavior title>
    Given <a business precondition>
    When <the actor does one thing>
    Then <the observable outcome>
```

## Ceilings (upgrade paths)

Deliberate simplifications and their upgrade path (the `ponytail:` ceiling in
prose). "Naive X now; do Y when Z is measured."

## Test strategy

- Behaviors to verify:
- Edge cases:
- Regression risks:
- Coverage impact: none | informational | enforced | needs project decision

## Validation

- Command, gate, manual check, coverage report, or review evidence. **Name the
  `testing/scenarios/*.py` file(s)** the Gherkin ids resolve against — the gate
  reads this section to map scenarios to checks.

## Amendments

Versioned sections appended as the spec evolves; never rewrite history.

<!-- ### v2 (<date>) — <what changed>
     New numbered rules continue the list; add rationale rows for each. -->

<!-- ============================ MINI EXAMPLE ============================
# SPEC-042 — Escalation queue ordered by blast radius

Status: SPEC-042, proposed 2026-07-11 (acceptance: `testing/scenarios/eq_queue.py`).

## Goal
The supervisor sees escalations ranked by blast radius, not arrival order.

## Applicability
`scripts/harness_ui.py` escalation column + `escalations` CLI. Not remote/multi-user.

## Requirements / invariants (numbered, testable)
1. **Rank by tier.** The queue sorts by `failureClass` tier, ties broken by recency.
2. **No stream.** Items are categorized, never streamed line-by-line (human-factors).

## Rationale & sources
| Decisão | Fontes |
|---|---|
| Rank by blast radius | SPEC-111 R28 tiers; M5.3 human-factors requirement |

## Gherkin scenarios (UI surfaces only)
```gherkin
Feature: Escalation queue ordering
  Scenario: [eq:tier-order] a critical escalation sorts above an older warning
    Given a warning raised an hour ago and a critical raised just now
    When the supervisor opens the panel
    Then the critical escalation appears first
```

## Ceilings (upgrade paths)
In-memory sort per snapshot; move to a persisted priority index if the ledger grows.

## Test strategy
- Behaviors: tier order, recency tiebreak. Edge: empty queue. Regression: none.
- Coverage impact: enforced via `eq_queue.py`.

## Validation
`python testing/scenarios/eq_queue.py` (the `eq:tier-order` check) + `spec-pack` green.

## Amendments
(none yet)
===================================================================== -->
