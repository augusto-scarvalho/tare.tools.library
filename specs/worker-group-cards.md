# UX-GA.2 — Grouped fan-out worker cards

Status: UX-GA.2, proposed 2026-07-12 (acceptance: `testing/scenarios/ux_worker_groups.py`).

## Goal

When N parallel workers run, the operator sees one card-group per workflow/wave
instead of a flat list — fan-out stays legible without streaming
(categorize-not-stream). Grouping is a pure VIEW computed server-side over the
worker rows the panel already collects: no second dashboard, no new state
store, no render-loop LLM, no client-side aggregation, and the GUI writes no
state.

## Applicability

`scripts/harness_lib/ui_panel.py` (the `group_workers` view + the
`state_snapshot` stamp) and `scripts/harness_ui_page.py` (`renderAgents` in the
Agents section, fed by the existing 3s `/api/state` poll). Does not cover new
data sources, worker actions, or any write path.

## Requirements / invariants (numbered, testable)

1. **Pure grouping.** `group_workers(workers)` returns
   `[{workflowId, statusCounts, workers}]` grouped by each row's `workflow`
   (`"adhoc"` when absent) — computed on every call, no cache, no new reads,
   rows never mutated. Same input → same output.
2. **Calm board = [].** No workers (or any trouble) yields `[]`, never a crash.
3. **Stable order, most-recent first.** Groups sort by the most recent
   `lastOutputAt`/`finishedAt` inside the group, ties keeping first-appearance
   order; worker order INSIDE a group is the input order, untouched.
4. **Additive snapshot key.** `state_snapshot` stamps `workerGroups` beside the
   existing keys; `workers` and every other pre-existing key stay byte-identical.
5. **Grouped only on real fan-out.** The page renders group cards (header:
   workflowId + status counts, the existing `wcard` markup nested inside) only
   when `st.workerGroups` has more than one group; one group (or none) renders
   today's flat list byte-identically.
6. **Backend-computed, rendered as-is.** The browser renders `st.workerGroups`
   without grouping, sorting or counting in JS, and adds no polling. Section id
   `agents` and the existing card DOM classes are preserved.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Categorize, not stream | M5 human-factors requirement (SPEC-114 flight-strip bay; `attention_strips` docstring); docs/SUPERVISION_UI_IDEATION.md |
| A view over already-collected rows, no new reads | N3/K4 no-cache condition in `ui_panel.py`; memory "observation must pay for itself" |
| Backend computes, browser renders as-is | SPEC-114 N3 render discipline (`renderAtten`/`renderRisk` comments: never aggregate in JS) |
| Additive key, flat render preserved | UX-GA.1 additive-key precedent (`riskSummary`, spec `attention-risk-summary.md`); m5_ui_panel + ui_e2e assert the existing DOM |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: Grouped fan-out worker cards in the Agents section

  Scenario: [wg-1] two workflows' workers group into two cards with correct counts
    Given worker rows from two workflows and one ad-hoc worker
    When the rows are grouped
    Then one group per workflow plus an adhoc group is returned
    And each group counts its workers by status
    And the most recently active group comes first

  Scenario: [wg-2] a single group renders flat
    Given a board where every worker belongs to one workflow
    When the snapshot is produced
    Then workerGroups carries exactly one group preserving the worker order
    And the pre-existing snapshot keys are byte-identical siblings
    So the page keeps today's flat card list unchanged

  Scenario: [wg-3] the state snapshot carries workerGroups
    Given the state collector runs against a bare root
    When the snapshot is produced
    Then it carries workerGroups as an additive key beside workers
    And a calm board yields an empty list, never a crash
```

## Ceilings (upgrade paths)

Group recency is the max activity ISO string in the group; rows with no
timestamp sort last. Good enough for supervision glances — add an explicit
wave/startedAt key only if a real board proves misleading. The flat done-cap
(5 most-recent finished workers) applies per group in grouped mode; revisit if
groups grow past a screen.

## Test strategy

- Behaviors to verify: per-workflow grouping, adhoc fallback, status counts,
  most-recent-first stable order, purity (same input → same output), rows never
  mutated, single-group flat parity, additive snapshot key.
- Edge cases: empty/None worker list, rows without workflow/status/timestamps.
- Regression risks: the flat render or an existing snapshot key changing shape
  (guarded by wg-2/wg-3 and the `ui_panel.py` inline self-check); the Agents
  DOM contract (guarded by `m5_ui_panel.py` + `ui_e2e.py`).
- Coverage impact: enforced via `ux_worker_groups.py` + the `ui_panel.py`
  inline self-check; browser render asserted in `ui_e2e.py` when chromium is
  available (green-skip otherwise).

## Validation

- `python testing/scenarios/ux_worker_groups.py` — the `wg-1`, `wg-2`, `wg-3`
  checks map 1:1 to the scenarios above.
- `python scripts/harness_lib/ui_panel.py` — inline self-check (purity, calm
  [], single-group order, snapshot stamp).
- `python testing/scenarios/ui_e2e.py` — `ui_e2e:worker-groups` renders a group
  header in a real browser (auto-skips without one).
- `python testing/scenarios/m5_ui_panel.py` — the panel scenario stays green
  (snapshot shape unchanged plus the additive key).

## Amendments

(none yet)
