# UX-GA.1 — Risk-summary strip above the Attention bay

Status: UX-GA.1, proposed 2026-07-12 (acceptance: `testing/scenarios/ux_risk_summary.py`).

## Goal

The operator gets a one-glance deterministic risk rollup ABOVE the N3 Attention
bay: open escalations by attention tier, the open-escalation total, whether the
last validation is failing, the top blast-radius strip title, and the
`requiresSecurityReview` flag when the snapshot carries it. It is a pure VIEW
over snapshot fields the panel already collects — no second dashboard, no new
state store, no render-loop LLM, no client-side aggregation.

## Applicability

`scripts/harness_lib/ui_panel.py` (the `risk_summary` collector + the
`state_snapshot` stamp) and `scripts/harness_ui_page.py` (the strip rendered
above the Attention section, fed by the existing 3s `/api/state` poll). Does not
cover new data sources, alerting, or any write path — the GUI writes no state.

## Requirements / invariants (numbered, testable)

1. **Pure view over collected fields.** `risk_summary(out)` derives ONLY from the
   snapshot sections `attention_strips` already fed (`attention`, `escalations`,
   `lastValidation`) — computed on every call, no cache, no new reads.
2. **Never crash, calm = zeros.** Every missing/None key is tolerated; an empty
   board yields all-zero tier counts, `openEscalations 0`, `gateFailing False`,
   empty `topStrip`, `requiresSecurityReview False`.
3. **Additive snapshot key.** `state_snapshot` stamps `riskSummary` beside
   `attention`; every pre-existing snapshot key (including `attention` and its
   ordering) is byte-identical to before — a panel with no data renders "calm"
   exactly as today.
4. **Backend-computed, rendered as-is.** The page renders `st.riskSummary`
   without sorting, counting, or re-deriving in JS (the renderAtten discipline),
   and adds no polling.
5. **Top blast radius.** `topStrip` is the label of the first attention strip —
   the bay is already tier-sorted, so index 0 IS the highest-attention item.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Rollup derived from already-collected sections, no new reads | N3/K4 no-cache condition in `ui_panel.py` (`attention_strips` docstring); memory "observation must pay for itself" |
| Backend computes, browser renders as-is | SPEC-114 N3 render discipline (`renderAtten` comment: never sort/cache in JS) |
| `requiresSecurityReview` read-if-present only | the flag lives in quality-state `qualityGates` (spec `security-baseline.md`); `_last_validation` does not ship it today — no new read is added for it |
| Calm board = zeros, never crash | `state_snapshot` never-crash-per-source contract (SPEC-114) |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: One-glance risk rollup above the Attention bay

  Scenario: [rs-1] escalations and a failing gate roll up into tier counts
    Given a snapshot with two open escalations, one of them critical
    And the last validation failed
    When the risk summary is derived
    Then it counts one critical and one info escalation strip
    And it reports two open escalations and a failing gate
    And it names the critical escalation as the top blast-radius item

  Scenario: [rs-2] a calm board rolls up to zeros
    Given a snapshot with no escalations, no workers and no validation record
    When the risk summary is derived
    Then every tier count is zero and no flag is raised
    And missing snapshot fields never crash the panel

  Scenario: [rs-3] the state snapshot carries the derived summary
    Given the state collector runs against a bare root
    When the snapshot is produced
    Then it carries riskSummary beside attention as an additive key
    And recomputing the summary from the same snapshot yields the same value
```

## Ceilings (upgrade paths)

`requiresSecurityReview` surfaces only if a collector ever lands it in
`lastValidation`; today it reports `False` (the flag lives in quality-state's
`qualityGates`, which the snapshot does not ship). Wire it through a collector —
never a new read inside `risk_summary` — if the operator needs it live.

## Test strategy

- Behaviors to verify: tier counts, open-escalation total, failing-gate flag,
  top-strip title, purity (same input → same output), derived-not-cached stamp.
- Edge cases: empty/None snapshot, strips with unknown ranks, missing keys.
- Regression risks: an existing snapshot key changing shape (guarded by the
  additive key-set assert in rs-3 and the `ui_panel` inline self-check).
- Coverage impact: enforced via `ux_risk_summary.py` + the `ui_panel.py`
  inline self-check; browser render asserted in `ui_e2e.py` when chromium is
  available (green-skip otherwise).

## Validation

- `python testing/scenarios/ux_risk_summary.py` — the `rs-1`, `rs-2`, `rs-3`
  checks map 1:1 to the scenarios above.
- `python scripts/harness_lib/ui_panel.py` — inline self-check (purity, calm
  zeros, derived-not-cached stamp).
- `python testing/scenarios/ui_e2e.py` — `ui_e2e:risk-summary` renders the strip
  above the Attention bay in a real browser (auto-skips without one).
- `python testing/scenarios/m5_ui_panel.py` — the panel scenario stays green
  (snapshot shape unchanged plus the additive key).

## Amendments

(none yet)
