# SPEC-136 — panel-experiments-screen: read-only 🧪 Experiments view (experiment-lifecycle board at a glance)

Status: SPEC-136, proposed 2026-07-13 (acceptance: `testing/scenarios/pxe_panel_experiments.py`).

Intake (SPEC-116 door NEW, from the experiment-lifecycle registry pack and sibling
of SPEC-134/panel-specs-screen + SPEC-135/panel-research-screen): request = a read-only
Experiments screen in the supervision panel — the experiment-lifecycle cards
(`experiment list` inventory) as a proposed → active → shipped/shelved board with a
reviewBy staleness nag, instead of an editor/grep walk over
`.harness/state/experiments.json`. Covered-check: `experiment list` renders the same
inventory in the terminal but the panel had no view over it; the board view + its
`/api/experiments` route already shipped (committed ec22f61) — this slice adds only
the SDD spec + hermetic scenario that pin the contract. Decision: **NEW spec/test
for already-shipped code** (the write path — activate/record/verdict — stays in the
REPL/CLI; the board is strictly read-only, no `ACTIONS` entry).

Plan-vs-code correction (pinned to reality, per the overseer plan
`.harness/handoff/plan-exp-spec.md`, which says "read the cited code and the two
template files FIRST; pin reality; document any plan-vs-code correction in the spec's
corrections section"): the plan labels this spec **"SPEC-116"**. SPEC-116 is not a
free feature id — it is the SDD/BDD two-door flow (`specs/00-universal/sdd-bdd-flow.md`),
referenced in the intake line of every feature spec and as the "SPEC-116 pack" label
of the experiment-lifecycle registry (`experiment-lifecycle.md`) — the door this spec
is created *through*, not its id. The highest allocated id at authoring time is
**SPEC-135** (`panel-research-screen.md`; SPEC-134 is `panel-specs-screen.md`), so this
spec takes the next free id, **136** — the exact convention the two sibling panel
specs already applied to the same "SPEC-116" plan label.

## Goal

The supervision panel gains a read-only **🧪 Experiments** view: the
experiment-lifecycle registry grouped into the four lifecycle lanes
(proposed / active / shipped / shelved), each experiment a card carrying its title,
hypothesis, measurement count, and a `reviewBy` badge that turns overdue when an
active card has aged past its review date, with a click opening the full card
(hypothesis, metric, baseline, success/abandon criteria, reversalPlan, measurements,
and the verdict/evidence once settled) in a dialog. It renders the SAME inventory the
`experiment list` CLI verb prints — one shared registry (`experiment_registry`), no
GUI-only capability, no write path.

## Applicability

Applies to the collector `scripts/harness_lib/ui_panel.py` (`experiments_snapshot`),
one token-gated read route in `scripts/harness_ui.py` (`GET /api/experiments`), and
the panel front-end string `scripts/harness_ui_page.py` (the `navExperiments` pill,
the `viewExperiments` container + `expBoard`, the `expDlgBody` dialog, and the
on-demand `loadExperiments` / `openExperiment` handlers). It does **not** re-implement
lifecycle parsing (it reuses `experiment_registry.experiments` + `stale_active`), add
any `ACTIONS` entry (zero write path — activation, measurement, and verdict stay CLI/
REPL verbs), poll (a manual refresh button suffices — the registry changes on commit),
or redact beyond the registry's own `_clean` at write time. Deferred (recorded, not
built): inline measurement charts, in-panel activate/record/verdict actions, a
per-status filter, and a reviewBy nag that pushes an escalation strip — all future
increments over the same snapshot shape.

## Requirements / invariants (numbered, testable)

1. **Snapshot reuses the registry.** `experiments_snapshot(root)` builds its rows from
   `experiment_registry.experiments(root)` and its overdue flag from
   `experiment_registry.stale_active(root)` — the same machinery the `experiment list`
   / `doctor` CLI surfaces use, never a second parser.
2. **Grouped-ready payload.** The snapshot is `{experiments, counts, order}`: `order`
   is `experiment_registry.STATUSES` == `("proposed","active","shipped","shelved")`
   (the lane order the view groups by), and `counts` is the per-status rollup of the
   rows. Rows keep their registry insertion order; the view groups by `order` lane.
3. **Overdue flag.** Every row carries an `overdueDays` int; it is `> 0` ONLY on an
   active card whose `reviewBy` is in the past (from `stale_active`), and `0` on every
   proposed / settled / on-time card.
4. **Full lifecycle fields for the dialog.** Each row exposes the full card the
   click-through dialog renders — `hypothesis`, `metric`, `baseline`,
   `successCriteria`, `abandonCriteria`, `reversalPlan`, `measurements`, and, once
   settled, `verdict`/`evidence`/`reopenTrigger` — verbatim from the registry entry
   (the registry already scrubs/caps each field at write time).
5. **Calm degrade.** A missing or corrupt `.harness/state/experiments.json` degrades to
   an empty board — `{"experiments": [], "counts": {}, "order": STATUSES}` — never a
   raise, never a 500 (the registry's `_load` and `stale_active` both read a broken
   registry as empty).
6. **No write path.** The board is read-only: no `ACTIONS` entry is added, and neither
   the route nor the collector mutates state; activation / measurement / verdict remain
   the `experiment` CLI verbs.
7. **Route mirrors the read-only panel routes.** `GET /api/experiments` returns the
   snapshot behind the existing per-session token guard (no token → 403), wired exactly
   like the other read-only `/api/*` collectors.
8. **View wiring.** `PAGE` carries the `navExperiments` pill, a `viewExperiments`
   container with an `expBoard`, an `expDlgBody` dialog, and `loadExperiments()` invoked
   on-demand from `switchView` (no poll); a manual refresh button re-runs
   `loadExperiments`.

## Rationale & sources

| Decision | Sources |
|---|---|
| Reuse `experiment_registry.experiments` + `stale_active` (one registry for CLI + doctor + panel) instead of a second walker | `scripts/harness_lib/experiment_registry.py` (`experiments`, `stale_active`, `STATUSES`), `scripts/harness_lib/ui_panel.py` (`experiments_snapshot`) |
| Clone the read-only panel-view idiom (closed collector, calm degrade to an empty board, client-side lane grouping, body dialog) | `scripts/harness_lib/ui_panel.py` (`experiments_snapshot`), `scripts/harness_ui_page.py` (`loadExperiments` / `openExperiment` / `expDlgBody`), `scripts/harness_ui.py` (`/api/experiments`) |
| `order` == `STATUSES` is the lifecycle's own lane order; grouping by status is the operator's mental model of the board | `experiment_registry.STATUSES`, `specs/40-features/experiment-lifecycle.md` |
| Read-only, no poll, manual refresh — the registry changes on commit, not continuously; the write path stays a governed CLI verb | `experiment-lifecycle.md` (lifecycle write verbs), CLI-first parity (`experiment list`) |
| `overdueDays` surfaces the `reviewBy` nag `doctor` already computes, so the board and the CLI agree on staleness | `experiment_registry.stale_active`, `ui_panel.experiments_snapshot` |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: panel Experiments screen — the experiment-lifecycle board at a glance

  Scenario: [pxe-1] the snapshot is a grouped-ready board with counts and an overdue flag
    Given a registry with one card per lifecycle status and an active card past its reviewBy
    When experiments_snapshot runs
    Then order is STATUSES, counts is the per-status rollup, the past-reviewBy active card
      carries overdueDays > 0, and a missing or corrupt registry degrades to an empty board
      without crashing

  Scenario: [pxe-2] each card exposes the full lifecycle fields for the dialog
    Given the experiments snapshot
    When a proposed card and a settled (shipped) card are inspected
    Then the proposed card carries hypothesis/metric/baseline/success/abandon/reversal and
      a measurements list, and the shipped card additionally carries its verdict and evidence

  Scenario: [pxe-3] the route and the view are wired
    Given the built panel sources
    When harness_ui.py and harness_ui_page.py are inspected
    Then /api/experiments + ui_panel.experiments_snapshot exist in harness_ui.py and
      navExperiments/viewExperiments/loadExperiments exist in the page source
```

## Ceilings (upgrade paths)

- The snapshot carries `{experiments, counts, order}` with `overdueDays` per row — the
  seat for a per-status filter or a reviewBy-nag escalation strip is `counts`/`order`,
  which already partition the board; add the filter client-side without reshaping rows.
- The dialog renders the raw registry fields; inline measurement charts layer on top of
  the existing `measurements` list without changing the payload shape.
- The board is read-only today; in-panel activate/record/verdict would each be a new
  governed `ACTIONS` entry (a confirm-gated CLI wrapper), never a second write path in
  the collector — the snapshot shape does not change when they land.

## Test strategy

- Behaviors to verify: `experiments_snapshot` lane order (`order` == `STATUSES`),
  per-status `counts`, the `overdueDays > 0` flag on an active card seeded with a past
  `reviewBy`, and the full lifecycle fields (proposed card's
  hypothesis/metric/baseline/criteria/reversal + measurements; a shipped card's
  verdict/evidence) — hermetic temp root seeded via the `experiment_registry` write
  path (`add`/`activate`/`record`/`verdict`), one card per status; plus calm degrade on
  a corrupt and a wholly missing registry; and the wiring — `/api/experiments` +
  `ui_panel.experiments_snapshot` in `harness_ui.py` source and
  `navExperiments`/`viewExperiments`/`loadExperiments` in `harness_ui_page.py` source.
- Edge cases: an active card exactly on-time (`overdueDays` 0, not flagged), a settled
  card (never overdue regardless of `reviewBy`), a corrupt registry (empty board, no
  raise), and a missing registry (empty board).
- Regression risks: `ui_panel.ACTIONS` is untouched (the board adds no write path); the
  page edits are purely additive (a new pill/view/dialog/function), so the existing
  panel contract scenarios stay green.
- Coverage impact: enforced via `testing/scenarios/pxe_panel_experiments.py` (the three
  `pxe-*` checks) plus the `experiment_registry` and `ui_panel` module self-checks.

## Validation

- `python testing/scenarios/pxe_panel_experiments.py` — the `pxe-1`, `pxe-2`, `pxe-3`
  checks all green (the `pxe-3` wiring check asserts `/api/experiments` +
  `ui_panel.experiments_snapshot` in `harness_ui.py` and
  `navExperiments`/`viewExperiments`/`loadExperiments` in `harness_ui_page.py`).
- `python scripts/harness_lib/ui_panel.py` — the module self-check (`ui_panel
  self-check ok`), which covers the read-only collectors.
- `python testing/scenarios/pss_panel_specs.py` — the sibling panel-spec scenario stays
  green (the shared read-only panel idiom).
- `spec-pack` feature-spec conformance for this spec (sections + the `pxe-*` gherkin ids
  resolving in `testing/scenarios/pxe_panel_experiments.py`).
- `testing/scenarios/ui_e2e.py` (real-chromium browser net, green-skips without Playwright):
  `e2e:experiments-kanban` asserts the four lifecycle columns render side by side and
  `e2e:experiments-card-dialog` asserts a card opens `#expDlg` with the lifecycle fields —
  the browser regression net that makes the ui-validation cheap tier safe for this view.

## Amendments

- 2026-07-13: added browser E2E coverage (`e2e:experiments-kanban`,
  `e2e:experiments-card-dialog` in `testing/ui/test_panel_e2e.py`, run via
  `testing/scenarios/ui_e2e.py`) after the board was reworked into kanban status
  columns. Closes the original gap where the view had a data/wiring net (pxe) but
  no browser-rendering net — the safety premise the `ui-validation` tier assumes.
