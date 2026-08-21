# SPEC-135 — panel-research-screen: read-only 🔬 Research view (research rounds at a glance)

Status: SPEC-135, proposed 2026-07-13 (acceptance: `testing/scenarios/prs_panel_research.py`).

Intake (SPEC-116 door NEW, from `docs/roadmap/screens-specs-research.md` §Research,
and sibling of SPEC-134/panel-specs-screen): request = a Research screen in the
supervision panel — the throwaway Double-Diamond rounds under `docs/research/`
(`research list` inventory) as a click-through gallery instead of an editor/grep
walk. Covered-check: `research list` renders the same inventory in the terminal but
the panel has no view over it; no existing `/api/*` route serves research rounds.
Decision: **NEW** (read-only slice — the parsed round inspector, live-workflow
join, and the delete flow stay OUT of this slice).

Plan-vs-code correction (pinned to reality, per the overseer plan
`.harness/handoff/plan-q8-panel-research-screen.md`, which says "read code first;
pin reality; corrections in the spec (Q7 style)"): the plan sources the gallery
from "the EXISTING `harness_lib/research_index.py` collector". Reality: that
module's `research_snapshot()` returns rich PARSED rounds (title / phases /
evidence / waves) but DROPS the two fields the card and the `prs-1` check require —
`recordsRefs` and `path` — keeping only `tracked` + `linkedWfs` from the admin
inventory it wraps. The card the plan specifies (slug, tracked?, workflow count,
records count, doc path) and the `prs-3` CLI-parity anchor (`research list`) are
BOTH exactly `research_admin.rounds()` — the admin inventory `research_snapshot`
itself wraps and `research list --json` prints. So the panel reuses
`research_admin.rounds()` AS-IS (no re-implementation); `research_index.research_snapshot`
stays the seat for the deferred rich round inspector. The next free spec id at
authoring time is **135** (SPEC-134 is the sibling panel-specs-screen).

## Goal

The supervision panel gains a read-only **🔬 Research** view: the throwaway
research rounds under `docs/research/` as a flat card gallery, each card carrying
its slug, a tracked-in-git flag, its linked-workflow count, its records-reference
count, and its doc path, with a click opening the full round markdown body in a
dialog. It renders the SAME inventory the `research list` CLI verb prints — one
shared collector (`research_admin.rounds`), no GUI-only capability, no write path
(the guarded `research delete` stays CLI-only).

## Applicability

Applies to two token-gated read routes in `scripts/harness_ui.py`
(`GET /api/research`, `GET /api/research/file`) fed by two thin module-level
helpers there (`research_snapshot` envelope + calm-degrade, `research_file`
closed-set body), and the panel front-end string `scripts/harness_ui_page.py` (the
`navResearch` pill, the `viewResearch` container + `researchDlg`, and the on-demand
`loadResearch`). It does **not** re-implement round parsing or inventory walking
(it reuses `harness_lib.research_admin.rounds`), add any `ACTIONS` entry (zero
write path — no delete from the panel), poll (a manual refresh button suffices —
rounds change on commit), or redact (research rounds are tracked public docs).
Deferred (recorded, not built): the parsed round inspector
(`research_index.research_snapshot`'s phases / evidence-matrix / waves view), the
live-workflow join, the guarded delete flow, and in-page markdown rendering — all
in `docs/roadmap/screens-specs-research.md`.

## Requirements / invariants (numbered, testable)

1. **Snapshot reuses the shared inventory.** `research_snapshot(root)` builds its
   rows from `research_admin.rounds(root)` — the same slug / tracked-in-git /
   linked-WF / records-reference machinery the `research list` CLI verb uses —
   never a second walker or parser.
2. **Row shape.** Each round row is `{slug, path, tracked: <bool>,
   linkedWfs: <list>, recordsRefs: <count>}`; the `RESEARCH.md` index doc is never
   a row (it is the index, not a round).
3. **Stable order.** Rows are ordered by slug (the collector globs sorted) so the
   gallery order is stable across calls; the view renders one flat card row.
4. **Calm degrade.** A root with no `docs/research/` tree is an empty gallery
   (`{"rounds": []}`), never a crash; an unexpected failure returns
   `{"rounds": [], "error": …}`, never a 500.
5. **Closed-set full view.** `research_file(root, slug)` serves a round body ONLY
   when `slug` is present in the snapshot inventory; any slug not in the inventory
   (traversal `../…`, unknown name, absolute path) returns `{"error": …}` — the
   `/api/specs/file` + `/api/records` discipline, never a read outside
   `docs/research/`, never a crash.
6. **No redaction, no write path.** Bodies are served verbatim (rounds are tracked
   public docs); neither route mutates state and no `ACTIONS` entry is added (the
   guarded `research delete` stays a CLI-only human decision).
7. **Routes mirror /api/specs.** `GET /api/research` returns the snapshot and
   `GET /api/research/file?slug=<slug>` returns one body, both behind the existing
   per-session token guard (no token → 403), wired exactly like `/api/specs` +
   `/api/specs/file`.
8. **View wiring.** `PAGE` carries the `navResearch` pill, a `viewResearch`
   container, a `researchDlg` dialog, and `loadResearch()` invoked on-demand from
   `switchView` (no poll); a manual refresh button re-runs `loadResearch`.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Reuse `research_admin.rounds` (one inventory for the CLI + panel) instead of a second walker | `scripts/harness_lib/research_admin.py` (`rounds`, `cmd_research` `research list`) |
| Serve the admin inventory, not `research_index.research_snapshot` — the card + `prs-1` need the `recordsRefs` + `path` that `research_snapshot` drops, and `research list` is the parity anchor | `scripts/harness_lib/research_index.py` (`research_snapshot` keeps only `tracked`+`linkedWfs`), overseer plan §"corrections in the spec" |
| Clone the Specs view idiom (closed collector, calm degrade; body dialog; manual refresh) | `scripts/harness_lib/ui_specs.py`, `scripts/harness_ui_page.py` (`loadSpecs` / `specDlg`), `scripts/harness_ui.py` (`/api/specs`) |
| Closed-set membership (not `relative_to`) is the traversal guard — the inventory only holds clean round slugs, so a free path simply isn't a member | `scripts/harness_lib/ui_specs.py` `spec_file`; `/api/records` `{"error":…}` never-500 shape |
| Read-only, no poll, no delete — the panel is a reader; `research delete` is a guarded human decision | `scripts/harness_lib/research_admin.py` (`delete_round` dry-run-by-default), `docs/roadmap/screens-specs-research.md` §Research |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: panel Research screen — research rounds at a glance

  Scenario: [prs-1] the snapshot lists rounds with tracked, workflow and records fields
    Given a docs/research tree with two rounds and the RESEARCH.md index
    When research_snapshot runs
    Then each round row carries its slug, path, tracked flag, linked-workflow list and
      records-reference count, the RESEARCH.md index is not a row, and a tree with no
      research rounds is an empty gallery without crashing

  Scenario: [prs-2] the full view is closed to the inventory
    Given the research snapshot inventory
    When research_file is asked for a real round slug, then for a traversal / unknown / absolute path
    Then the real slug returns its body and every non-inventory path returns an error, never a read outside docs/research/

  Scenario: [prs-3] the routes and the view are wired and CLI parity holds
    Given the built panel sources
    When the harness_ui routes, the PAGE view ids, and the research list CLI are inspected
    Then /api/research + /api/research/file exist in harness_ui.py, navResearch/viewResearch/loadResearch
      exist in the page, and research list --json agrees with research_snapshot on the live tree
```

## Ceilings (upgrade paths)

- The snapshot carries only `{slug, path, tracked, linkedWfs, recordsRefs}` — the
  seat for the deferred parsed inspector (phases / evidence-matrix / waves /
  experiments) is `research_index.research_snapshot`, which already parses those;
  the panel switches its collector there (one place) when the inspector is built,
  without reshaping the card contract.
- The full view returns raw markdown; in-page rendering (whitelist renderer) is
  the deferred increment — the body payload shape does not change when it lands.
- The panel is read-only; the guarded `research delete` (dry-run-by-default,
  `--allow-committed` for tracked rounds) layers on as a confirmed mutating
  `ACTIONS` entry when the delete flow is built — not in this slice.

## Test strategy

- Behaviors to verify: `research_snapshot` row shape + tracked/linkedWfs/recordsRefs
  fields + `RESEARCH.md` exclusion + calm degrade on a missing `docs/research/`
  tree (hermetic temp root seeded with two tiny rounds + the index doc);
  `research_file` closed-set serve-vs-refuse for real / traversal / unknown /
  absolute slugs; the two routes present in `harness_ui.py` source and
  `navResearch`/`viewResearch`/`loadResearch` present in `harness_ui.PAGE`; and
  `research list --json` CLI parity agreeing with `research_snapshot` on the live
  tree.
- Edge cases: a research root with no rounds (empty gallery), the `RESEARCH.md`
  index (never a round), an absolute path or `..` traversal (refused by inventory
  membership).
- Regression risks: `testing/scenarios/m5_ui_panel.py` stays green — the page edits
  are purely additive (a new pill/view/dialog/function, no id the panel contract
  asserts absent, no native `confirm`/`alert`/`prompt` call), and `ui_panel.ACTIONS`
  is untouched (the no-write-path check's exact action set is unchanged).
- Coverage impact: enforced via `testing/scenarios/prs_panel_research.py` (the three
  `prs-*` checks).

## Validation

- `python testing/scenarios/prs_panel_research.py` — the `prs-1`, `prs-2`, `prs-3`
  checks all green.
- `python testing/scenarios/m5_ui_panel.py` — untouched-green (the page edits ride
  inside the panel contract).
- `spec-pack` feature-spec conformance for this spec (sections + the `prs-*`
  gherkin ids resolving in `testing/scenarios/prs_panel_research.py`).

## Amendments

(none yet)
