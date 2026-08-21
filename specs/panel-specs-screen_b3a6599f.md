# SPEC-134 — panel-specs-screen: read-only 📋 Specs view (SDD inventory at a glance)

Status: SPEC-134, proposed 2026-07-13 (acceptance: `testing/scenarios/pss_panel_specs.py`).

Intake (SPEC-116 door NEW, from `docs/roadmap/screens-specs-research.md` §Specs):
request = a Specs screen in the supervision panel — "especificações do projeto
organizadas por escopo. Leitor/inspetor de specs." The SDD tree is the source of
truth but is only readable via editor/grep today; this makes "which specs exist,
by scope" a click. Covered-check: `spec-index` renders the same inventory in the
terminal but the panel has no view over it; no existing `/api/*` route serves
specs. Decision: **NEW** (read-only slice — the cross-link inspector, target
scope, and the Research screen stay OUT of this slice).

Plan-vs-code correction (pinned to reality, per the overseer plan): the plan
`.harness/handoff/plan-q7-panel-specs-screen.md` labeled this spec "SPEC-116".
SPEC-116 is already `specs/00-universal/sdd-bdd-flow.md` — the two-door flow this
spec is *created through*, not an id. The highest allocated id at authoring time
is SPEC-133 (`panel-chat-qol.md`), so this spec takes the next free id, **134**.
The roadmap's working name `gui-specs-screen` is likewise renamed to
`panel-specs-screen` to match the panel-* file family and the plan's footprint.

## Goal

The supervision panel gains a read-only **📋 Specs** view: the SDD inventory
grouped by scope dir (00-universal / 40-features / templates / …), each spec a
card carrying its title, a legacy-frozen badge, and a gherkin-id count, with a
click opening the full markdown body in a dialog. It renders the SAME inventory
the `spec-index` CLI verb prints — one shared parser (`spec_index.collect`), no
GUI-only capability, no write path.

## Applicability

Applies to the new collector `scripts/harness_lib/ui_specs.py`
(`specs_snapshot` + `spec_file`), two token-gated read routes in
`scripts/harness_ui.py` (`GET /api/specs`, `GET /api/specs/file`), and the panel
front-end string `scripts/harness_ui_page.py` (the `navSpecs` pill, the
`viewSpecs` container + `specDlg`, and the on-demand `loadSpecs`). It does **not**
re-implement spec parsing (it reuses `harness_lib.spec_index.collect`), add any
`ACTIONS` entry (zero write path), poll (a manual refresh button suffices — specs
change on commit), or redact (specs are tracked public docs). Deferred (recorded,
not built): the cross-reference inspector (SPEC-###/path linkification), the
global/harness/target scope distinction and target spec trees, conformance
badges, in-page markdown rendering, and the Research screen — all in
`docs/roadmap/screens-specs-research.md`.

## Requirements / invariants (numbered, testable)

1. **Snapshot reuses the shared parser.** `specs_snapshot(root)` builds its rows
   from `spec_index.collect(root)` — the same scope/title/`Scenario:[id]`/
   legacy-frozen machinery the `spec-index` CLI verb and the SPEC-116 conformance
   gate use — never a second parser.
2. **Row shape.** Each spec row is `{id: <rel-path>, scope, title,
   gherkinIds: <count>, legacyFrozen: <bool>, mtime}`; `gherkinIds` is the COUNT
   of scenario ids, not the list.
3. **Grouped, stable order.** Rows are ordered by `(scope, id)` so every scope
   dir's specs are contiguous and the order is stable across calls; the view
   renders one card group per scope.
4. **Calm degrade.** A spec with broken/absent markdown (no H1, no gherkin block)
   is still listed — empty `title`, `gherkinIds` 0 — never crashing the snapshot;
   an unexpected failure returns `{…, "specs": [], "error": …}`, never a 500.
5. **Closed-set full view.** `spec_file(root, rel)` serves a spec body ONLY when
   `rel` is present in the snapshot inventory; any path not in the inventory
   (traversal `../…`, unknown name, absolute path) returns `{"error": …}` — the
   `/api/records` discipline, never a read outside `specs/`, never a crash.
6. **No redaction, no write path.** Bodies are served verbatim (specs are tracked
   public docs); neither route mutates state and no `ACTIONS` entry is added.
7. **Routes mirror /api/memory.** `GET /api/specs` returns the snapshot and
   `GET /api/specs/file?path=<rel>` returns one body, both behind the existing
   per-session token guard (no token → 403), wired exactly like `/api/memory` +
   `/api/memory/file`.
8. **View wiring.** `PAGE` carries the `navSpecs` pill, a `viewSpecs` container,
   a `specDlg` dialog, and `loadSpecs()` invoked on-demand from `switchView`
   (no poll); a manual refresh button re-runs `loadSpecs`.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Reuse `spec_index.collect` (one parser for CLI + gate + panel) instead of a second walker | `scripts/harness_lib/spec_index.py` (`collect`), `scripts/harness_lib/spec_conformance.py` (`_gherkin_ids`) |
| Clone the Memory view idiom (closed collector, calm degrade, `__main__` self-check; client-side scope grouping; body dialog) | `scripts/harness_lib/ui_memory.py`, `scripts/harness_ui_page.py` (`loadMemory` / `memDlg`), `scripts/harness_ui.py:166` (`/api/memory`) |
| Closed-set membership (not `relative_to`) is the traversal guard — the inventory only holds clean posix relpaths, so a free path simply isn't a member | `scripts/harness_ui.py` `_send_vendor` traversal precedent; `/api/records` `{"error":…}` never-500 shape |
| Read-only, no poll, manual refresh — specs change on commit, not continuously | `docs/roadmap/screens-specs-research.md` §Specs (S0–S2), CLI-first parity |
| Grouping by scope dir is the operator's mental model of the tree | `specs/SPECS.md` (scope layout), roadmap §Specs "GLOBAL scope" |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: panel Specs screen — the SDD inventory at a glance

  Scenario: [pss-1] the snapshot groups specs by scope with badges and gherkin counts
    Given a specs tree with a scenario-carrying spec, a legacy-frozen spec, and a parse-broken spec
    When specs_snapshot runs
    Then rows are grouped by scope dir in stable order, the frozen spec is flagged,
      the scenario spec's gherkinIds is its scenario count, and the parse-broken spec
      degrades to an empty title / 0 ids without crashing

  Scenario: [pss-2] the full view is closed to the inventory
    Given the specs snapshot inventory
    When spec_file is asked for a real inventory path, then for a traversal / unknown / absolute path
    Then the real path returns its body and every non-inventory path returns an error, never a read outside specs/

  Scenario: [pss-3] the routes and the view are wired and CLI parity holds
    Given the built panel sources
    When the harness_ui routes, the PAGE view ids, and the spec-index CLI are inspected
    Then /api/specs + /api/specs/file exist in harness_ui.py, navSpecs/viewSpecs/loadSpecs
      exist in the page, and spec-index --json agrees with specs_snapshot on the live tree
```

## Ceilings (upgrade paths)

- The snapshot carries only `{id, scope, title, gherkinIds, legacyFrozen, mtime}`
  — the seat for the deferred cross-reference graph is `spec_index`'s row, which
  already parses scenario ids; add `outgoingRefs` there (one place) when the
  inspector is built.
- The full view returns raw markdown; in-page rendering (whitelist renderer) and
  SPEC-###/path linkification are the deferred S2 increment — the body payload
  shape does not change when they land.
- Scope is the structural path prefix today; the global/harness/target
  distinction and target spec trees (roadmap §"Harness vs target") layer on top of
  the same `scope` field without reshaping rows.

## Test strategy

- Behaviors to verify: `specs_snapshot` grouping + row shape + gherkin counts +
  legacy flag + calm degrade on a parse-broken file (hermetic temp root seeded
  with 2–3 tiny specs, one with a `Scenario:[x-1]` block, one marked legacy via a
  seeded `project.json` `specConformance.legacy`); `spec_file` closed-set
  serve-vs-refuse for real / traversal / unknown / absolute paths; the two routes
  present in `harness_ui.py` source and `navSpecs`/`viewSpecs`/`loadSpecs` present
  in `harness_ui.PAGE`; and `spec-index --json` CLI parity agreeing with
  `specs_snapshot` on the live tree.
- Edge cases: a scope with no H1 (empty title), a spec with zero gherkin blocks
  (count 0), an absolute path or `..` traversal (refused by inventory membership).
- Regression risks: `testing/scenarios/m5_ui_panel.py` stays green — the page
  edits are purely additive (a new pill/view/dialog/function, no id the panel
  contract asserts absent), and `ui_panel.ACTIONS` is untouched (the composer
  no-write-path check's exact action set is unchanged).
- Coverage impact: enforced via `testing/scenarios/pss_panel_specs.py` (the three
  `pss-*` checks) plus the `ui_specs` module self-check.

## Validation

- `python testing/scenarios/pss_panel_specs.py` — the `pss-1`, `pss-2`, `pss-3`
  checks all green.
- `python scripts/harness_lib/ui_specs.py` — the module self-check (`ui_specs
  self-check: ok`).
- `python testing/scenarios/m5_ui_panel.py` — untouched-green (the page edits ride
  inside the panel contract).
- `spec-pack` feature-spec conformance for this spec (sections + the `pss-*`
  gherkin ids resolving in `testing/scenarios/pss_panel_specs.py`).

## Amendments

(none yet)
