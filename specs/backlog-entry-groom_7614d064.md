# SPEC-155 -- Backlog-entry-groom guard (groom a task AT ENTRY, in lockstep)

Status: SPEC-155, proposed 2026-07-19 (acceptance: `testing/scenarios/eg_entry_groom.py`).
Door: SPEC-116 NEW (owner decision 2026-07-19 -- gate ratchet: every open item carries a
dependency assessment). The ENTRY bookend to SPEC-154 (closure): SPEC-154 ties ship ->
close, SPEC-155 ties enter -> groomed. Mirrors the SPEC-154 shape
(`specs/40-features/backlog-closure-guard.md`): a gate scenario (the teeth) + a delivery-bar
advisory (the early nudge) + an entry hook on the task-store `add` path.

## Goal

Ensure a task ENTERING the backlog is GROOMED -- its dependencies ASSESSED --
deterministically, so debt does not accumulate as un-assessed rows (half the
cause of the backlog rot the closure guard addresses from the other end). An
assessment is either a deps-as-tags edge (`depends-on:`/`blocks:`/`relates-to:`/
`duplicates:`, the `tasks_board` convention) OR an explicit standalone `no-deps`
marker. The gate refuses an open item that carries NEITHER. Together with
SPEC-154 the cycle is fenced: a task enters groomed and closes in lockstep.

## Applicability

Applies to `testing/scenarios/eg_entry_groom.py` (the enforcement, `eg-1`),
`tools/hooks/delivery_bar_advisor.py` R6 (the advisory nudge, never blocks), and
`scripts/harness_lib/tasks_store.py` `add` (the entry hook: default `no-deps` +
a shipped-check warning). Reads `docs/IMPLEMENTATION_BACKLOG.md` and REUSES
`scripts/harness_lib/tasks_board.py` (`_backlog_rows` for open-row derivation,
`_parse_deps` for the deps-as-tags convention) -- never reimplemented. Does NOT
auto-map dependencies (mapping is the human groom action; the gate only REQUIRES
the assessment), does NOT edit the backlog itself, and does NOT edit the shared
`tasks_board` parser (the GUI phase-matrix mis-parse is a noted follow-up; see
Ceilings). Does not restate the baseline
(`specs/00-universal/testing-and-quality-gates.md` is referenced).

## Requirements / invariants (numbered, testable)

1. **The assessment convention.** An open backlog item carries a dependency
   assessment: at least one deps-as-tags marker
   (`depends-on:<id>`/`blocks:<id>`/`relates-to:<id>`/`duplicates:<id>`, parsed
   by `tasks_board._parse_deps`) OR a standalone `no-deps` marker (same slug
   charset family `[A-Za-z0-9._-]`, whole-token, so `depends-on` and prose never
   satisfy it). `no-deps` is the explicit "assessed, has no dependencies"
   declaration -- it is the assessment, not the absence of one.
2. **eg-1 -- groomed-on-entry.** Every OPEN backlog row (via
   `tasks_board._backlog_rows`, lane != `done`) that is a real item carries an
   assessment. An open item with neither a dep tag nor a `no-deps` marker FAILS
   `eg-1`, listing the un-groomed rows. Open-ness + deps-as-tags are derived by
   REUSING `_backlog_rows` / `_parse_deps`; the `no-deps` marker is read from the
   RAW backlog line (the parser truncates a row's title to 160 chars, so a
   trailing marker -- e.g. RF.1 -- would be lost via the parsed title alone).
3. **Assessment required, never auto-mapped.** The guard only DETECTS a missing
   assessment; it never maps dependencies itself (mapping is human/groom) and
   never edits the backlog. Same inputs yield the same result; stdlib only.
4. **Advisory nudges, gate is the teeth.** `delivery_bar_advisor.py` R6 emits, on
   a STAGED `docs/IMPLEMENTATION_BACKLOG.md` diff, one reminder when a NEW row
   lacks an assessment ("groom on entry: map deps or mark no-deps"), plus a
   heuristic shipped-check nudge when a new item's slug matches an existing
   `testing/scenarios/*.py` or `harness_lib/*.py` ("may already be shipped --
   verify + close via SPEC-154"). It NEVER blocks (exit 0) and is fail-open.
5. **Entry hook on `tasks add`.** `tasks_store.add` DEFAULTS a task added without
   any deps-as-tag to `no-deps` (nothing enters un-assessed) and emits a
   shipped-check WARNING when the new slug matches an existing scenario/module.
   Additive: the existing `add` behavior and its self-check stay green.

## Gherkin scenarios

```gherkin
Scenario: [eg-1] an open backlog item must carry a dependency assessment
  Given an open backlog row in docs/IMPLEMENTATION_BACKLOG.md
  When the guard derives open rows via tasks_board and scans for an assessment
  Then eg-1 fails if the row has no deps-as-tag and no no-deps marker
  And eg-1 passes when the row has a depends-on/blocks/relates-to/duplicates tag
  And eg-1 passes when the row carries a standalone no-deps marker
  And a GUI phase-matrix pseudo-row (digit-prefixed id or the GUI section) is excluded
```

## Rationale & sources

| Decision | Sources |
|---|---|
| Groom on entry (assessment required) as the entry bookend to closure (R1, R2) | owner decision 2026-07-19 (`.harness/handoff/plan-entry-groom.md`); SPEC-154 closure-guard precedent |
| Reuse the backlog parser + deps-as-tags, never reimplement (R2) | `scripts/harness_lib/tasks_board.py` `_backlog_rows` / `_parse_deps` (backlog-groom P1 deps-as-tags) |
| Assessment required, mapping is human (R3) | plan MUST-NOT (no auto-map); the backfill of the existing open rows is a separate overseer step |
| Advisory early, gate is the teeth (R4) | `specs/40-features/backlog-closure-guard.md` (advisory-seed + gate-teeth shape); `tools/hooks/delivery_bar_advisor.py` R1/R4/R5 pattern |
| Entry hook defaults no-deps + shipped-check (R5) | `scripts/harness_lib/tasks_store.py` `add` (single-write-path); shipped-check heuristic mirrors SPEC-154 close intent |

## Ceilings (upgrade paths)

- **GUI phase-matrix scope-out.** The `## GUI / front-end track` table is a
  phase-MATRIX pointer into `docs/GUI_IMPLEMENTATION_PLAN.md`, not backlog items,
  but `tasks_board` mis-parses it as ~10 phantom rows (ids `0 Fundacao`..`7
  Activity`, header `Fase` -- `Fase` is absent from the parser's `_HEADER_CELLS`).
  `eg-1` EXCLUDES them by the digit-prefixed id shape `^\**\s*\d+\s` (no real slug
  or item title has it) OR the GUI section, and does NOT edit the shared parser.
  **Follow-up (NOTED, not this cycle):** fix the `tasks_board` parser so the
  phase-matrix stops minting phantom rows (they also inflate the open count and
  add ghost nodes to the dep-graph) -- a separate parser amendment with its own
  scenario, since the parser is consumed by bc-1 / dep_graph / the board.
- **Assessment is a marker convention, not a schema.** `no-deps` and the
  deps-as-tags live in the row's free text. Once the canonical task store
  replaces the markdown tables (`tasks_board` A1), eg-1 follows the store's
  derivation automatically because it reuses the same parser seam.
- The advisory is nudge-only; the gate is the enforcement of record.

## Test strategy

- Behaviors to verify: eg-1 passes on the current tree (post backfill, every real
  open row has a tag or `no-deps`; the phase-matrix is scoped out); an open item
  with no assessment turns eg-1 red; a `depends-on:X` item passes; a `no-deps`
  item passes (including one whose marker sits past the 160-char title cap); a
  phase-matrix-shaped id is excluded. Proven by the scenario's hermetic
  `_selfcheck` over an injected backlog fixture (deterministic).
- Edge cases: the `no-deps` marker is whole-token (prose "no per-role" and the
  `depends-on` tag never satisfy it); a done/struck row is ignored; the GUI
  phase-matrix rows never false-fail.
- Regression risks: a new open item added without an assessment turns eg-1 red;
  the R6 advisory nudges the same condition earlier without ever blocking; the
  `tasks add` entry hook defaults `no-deps` so a manual add never enters un-assessed.
- Coverage impact: enforced via `testing/scenarios/eg_entry_groom.py` (eg-1),
  `tools/hooks/delivery_bar_advisor.py --self-check` (R6), and
  `scripts/harness_lib/tasks_store.py` self-check (add default + shipped-check).

## Validation

- `python testing/scenarios/eg_entry_groom.py` (eg-1 green on the current tree;
  the hermetic self-check proves an un-assessed item fails, a dep-tag or a
  `no-deps` item passes, and a phase-matrix-shaped id is excluded).
- `python tools/hooks/delivery_bar_advisor.py --self-check` (OK, R6 fires on a
  staged new backlog row without an assessment and on a slug matching a shipped
  scenario/module, and never blocks).
- `python scripts/harness_lib/tasks_store.py` (self-check green; a `tasks add`
  with no deps enters with `no-deps` and emits a shipped-check line when the slug
  matches an existing scenario/module).
- Spec-pack `feature-spec-conformance` green on this file (six required sections
  present; the Gherkin `[eg-1]` id resolves to `check("eg-1")` in
  `testing/scenarios/eg_entry_groom.py`).

## Amendments

(none yet)

## Amendment — assessment is structural (`backlog-json-canonical`, 2026-07-27)

eg-1 reads `tasks_board.task_rows` (the store) instead of parsing the document,
and a row is assessed when it carries a dep edge, the structural `noDeps` field
(`harness.py tasks dep <id> no-deps`), or a `no-deps` token in its own `body`.

Two workarounds are DELETED because their causes are gone:

- the raw-document-line scan existed only because the parsed title was capped at
  160 chars; `body` has carried the full row since the store gained the field;
- eg-1's private copy of "is this a task" is replaced by the shared
  `tasks_board.is_task_row`. That copy also excluded the whole
  `GUI / front-end track` SECTION, and since the document has no `##` header
  between line 12 and line 118, it silently scoped out every row registered
  after 2026-07-20 — the entry guard was blind to the newest work it exists to
  check. Coverage went from ~50 to 91 open rows on the switch and immediately
  found one un-groomed row.

A store-only row (created by `tasks add`) has no document prose to carry a
marker, which is why the assessment needed a structural home.
