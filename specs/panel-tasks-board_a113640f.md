# Panel tasks board — A0 read-only derived Kanban (`tasks-board-read`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/tb_tasks_board.py).

Intake (SPEC-116 door NEW): request = "tela de tasks: visão de backlog/roadmap +
raias tipo Kanban, com status do que está rolando e visões por categoria"
(`docs/roadmap/screens-tasks-queue.md` Screen A, phase A0). Covered-check:
`records search tasks board kanban` → no hit; the backlog is one markdown file,
live work is a small Agents strip — nothing renders a board. Decision: **NEW**.
SLICE: A0 read-only DERIVED board ONLY — the canonical `tasks.json` store, lane
moves, enqueue and per-target boards are the tasks-store-cli / tasks-enqueue /
tasks-target-board increments (owner decision 2026-07-13 #3 governs the store).

## Goal

One derived, read-only Kanban over signals already on disk: backlog table rows,
self-review inbox findings, pending escalations, and live workflow workers —
visible in the panel (`▦ Tasks` view polling `GET /api/tasks`) and from the
terminal (`python scripts/harness.py tasks list`), with rows carrying a derived
category (feature/bug/ideation/chore) and lane (backlog/running/review/done).
Nothing is stored; every call re-derives.

## Applicability

Applies to `scripts/harness_lib/tasks_board.py` (`tasks_snapshot(root)`,
`cmd_tasks`), its one-line registration in `cli_registry.py` (zero
`harness.py` edits), the `/api/tasks` route in `scripts/harness_ui.py`, and the
`viewTasks` section in `scripts/harness_ui_page.py`. GUI writes no canonical
state (the view is pure GET); no existing verb, route, or state file changes.

## Requirements / invariants (numbered, testable)

1. **Derived, never stored.** `tasks_snapshot(root)` performs pure reads over
   `docs/IMPLEMENTATION_BACKLOG.md`, `.harness/state/escalations.json`
   (raised minus resolvedIds) and `chat_hud.read_workers`; it writes nothing
   and returns `derived: true`.
2. **Never-crash row parsing.** Only `|`-leading lines parse; separator and
   header rows are skipped; a malformed row is skipped per-row (ui_panel
   never-crash idiom), never an exception.
3. **Lane derivation.** Struck (`~~`/✅) rows → `done`; other backlog rows →
   `backlog`; active workers → `running`, or `review` when their taskProfile
   is review/security. Live lanes are derived per call, never stored.
4. **Category derivation.** Self-review inbox rows → `chore` when the finding
   is budget/burndown/lines-shaped, else `bug`; pending escalations → `bug`;
   Deferred/Ideation sections → `ideation`; other table rows → `feature`.
5. **CLI parity + TE.5 rider.** `tasks list [--category] [--lane] [--json]`
   registers via `cli_registry.register()` and exits 0; under
   `HARNESS_AGENT_OUTPUT=compact` the rows emit as TSV through `common.emit`
   (owner decision 2026-07-13 #3 rider), pretty JSON only for humans.
6. **Panel wiring.** `GET /api/tasks` (token-gated like every route) returns
   the same collector payload; the PAGE carries the `navTasks` button, the
   `viewTasks` section and a `loadTasks()` renderer over the four lanes.
7. **Registry-only surface.** `harness.py` is not edited; the frozen top-level
   surface adds exactly `tasks` before `workflow`
   (`testing/scenarios/cli_registry.py`).

## Gherkin scenarios

```gherkin
Feature: A0 derived read-only tasks board

  Scenario: [tb-1] backlog, inbox, escalations and workers derive rows and lanes
    Given a temp root with a backlog table (one open, one struck row), a
      self-review inbox finding, one pending and one resolved escalation,
      and an active workflow with a review-profile worker
    When tasks_snapshot runs
    Then the struck row is lane done, the open row lane backlog category feature,
      the inbox finding derives its category, the resolved escalation is absent
      and the review worker lands in lane review

  Scenario: [tb-2] malformed rows never crash the collector
    Given a backlog file with garbage pipe-lines and prose between tables
    When tasks_snapshot runs
    Then parsing skips the garbage per-row and returns the valid rows

  Scenario: [tb-3] tasks list exits 0 in both output modes
    Given this repository
    When "harness.py tasks list" runs plain and under HARNESS_AGENT_OUTPUT=compact
    Then both exit 0 and the compact run emits TSV (header + tab-separated rows)

  Scenario: [tb-4] the panel is wired: route and view exist
    Given the server and page sources
    Then harness_ui.py handles /api/tasks via tasks_board.tasks_snapshot
      And the PAGE contains navTasks, viewTasks and the loadTasks renderer
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Derivar tudo, não armazenar (A0) — o store canônico é o próximo incremento | `docs/roadmap/screens-tasks-queue.md` (A0 vs A1); owner decision 2026-07-13 #3 (`tasks.json` canonical, tables freeze post-import) |
| Novo módulo em vez de `ui_panel.py` | roadmap risk #4: ui_panel.py já está acima do budget de 900 linhas |
| Parsing tolerante por linha | never-crash collector idiom (`ui_panel` attention/records collectors) |
| Verbo via `cli_registry.register()`, zero edits em `harness.py` | receita MF.1-r2 (`cli_registry.py` docstring); SPEC-131 provou o caminho |
| TSV compacto sob `HARNESS_AGENT_OUTPUT=compact` | TE.5 (`common.emit`/`to_tsv`); rider da decisão #3 — nunca JSON pretty para agente |
| GUI lê, nunca escreve | invariante do painel (SPEC-114; GUI-writes-no-state) |

## Test strategy

- Behaviors: fabricated temp root (backlog md + escalations.json + a WF dir
  with a review worker) → row/lane/category assertions (tb-1); garbage lines
  skipped (tb-2); live CLI both output modes rc 0 + TSV shape (tb-3,
  subprocess); wiring asserted from source text + PAGE string (tb-4 — the
  Playwright ui_e2e flow for the view rides the existing e2e suite as a
  follow-up, not this scenario).
- Edge cases: missing backlog file → empty board; resolved escalations
  filtered; multiline prose between tables ignored.
- Regression net: `testing/scenarios/cli_registry.py` frozen surface
  (`tasks` before `workflow`) guards rule 7; `m5_ui_panel`/ui_e2e keep the
  untouched panel behaviors green.
- Coverage: deterministic, stdlib-only — `testing/scenarios/tb_tasks_board.py`
  plus the module self-check (`python scripts/harness_lib/tasks_board.py`).

## Validation

- `python testing/scenarios/tb_tasks_board.py` — tb-1..tb-4 green.
- `python testing/scenarios/ttb_tasks_target_board.py` — ttb-1..ttb-3 green
  (SPEC-110 per-target grouping seam; see amendment v3).
- `python scripts/harness_lib/tasks_board.py` — module self-check.
- `python testing/scenarios/cli_registry.py` — frozen surface intact with `tasks`.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.

## Amendments

### v2 (2026-07-13) — A1 store-first read (tasks-store-cli)

`specs/40-features/tasks-store.md` shipped the canonical store (owner decision
#3). Invariant 1 is amended: `tasks_snapshot` still performs pure reads and
stores nothing itself, but once `.harness/state/tasks.json` exists its rows
REPLACE the backlog-markdown parse (the tables are frozen history after
`tasks import`); the markdown parse remains the pre-freeze fallback.
Escalation and live-worker rows stay derived per poll in both modes.

### v3 (2026-07-14) — SPEC-110 per-target grouping (tasks-target-board, A3)

READ-ONLY display increment: the board groups a registered target's own tasks
distinctly from the harness's. No task mutation, no new action, no `/api/action`
entry — pure GET like the rest of the panel.

New requirements (numbered, testable):

8. **Scoped rows.** Every harness row carries `scope: "harness"`;
   `tasks_snapshot` adds `targetGroups` — one entry per registered target
   (`.harness/targets/<name>/target.json`, discovered root-relative) with
   `{name, scope: "target", source, count, laneCounts, categoryCounts, rows}`;
   each target row carries `scope: "target"` and `target: <name>`. The existing
   harness `rows`/`count`/`laneCounts`/`categoryCounts` are unchanged (backward
   compatible; `/api/tasks` stays 200 with harness rows intact).
9. **No fabricated task source (invariant).** The per-target source is the
   roadmap-decided placement `.harness/state/targets/<name>/tasks.json`
   (`docs/roadmap/screens-tasks-queue.md` A3, mirrors quality-state). NO writer
   populates it yet (tasks-store-cli is harness-scoped), so today it is always
   absent → an empty per-target group and `perTargetSource: false`. The grouping
   is a **seam awaiting the source**; the board never invents per-target tasks.
10. **Calm empty-state.** A registered target with no source renders one kanban
    group labelled `target <name>` with a "target has no tasks" empty-state,
    reusing the `.tlanes`/`.tlane`/`.tcard` idiom; a target WITH a store lights
    up its lanes unchanged the day a writer ships.

```gherkin
Feature: SPEC-110 per-target tasks board grouping

  Scenario: [ttb-1] a registered target with a store groups by target scope
    Given a temp root with a backlog row and a target T1 whose
      .harness/state/targets/T1/tasks.json holds two tasks
    When tasks_snapshot runs
    Then the harness rows carry scope harness and are unchanged
      And targetGroups has a T1 group scoped target with its tasks grouped by lane
      And perTargetSource is true

  Scenario: [ttb-2] a registered target with no source degrades calmly
    Given a temp root with a registered target T2 that has no per-target store
    When tasks_snapshot runs
    Then the T2 group is empty with source null and no tasks are fabricated

  Scenario: [ttb-3] the panel renders per-target groups and stays read-only
    Given the page and server sources
    Then viewTasks renders targetGroups via renderLanes labelled target <name>
      And /api/tasks stays a pure read with no mutation or action added
```

## Amendment v4 — source honesty (`backlog-json-canonical`, 2026-07-27)

The snapshot declared `backlogPath: docs/IMPLEMENTATION_BACKLOG.md`
unconditionally while serving 265 of 265 non-derived rows from
`.harness/state/tasks.json`. A surface that names a source it does not read is
how ten days of store/document divergence stayed invisible — the same
"checks that appear to cover" pattern documented in
`docs/research/gate-surface-definition-2026-07-26.md`.

- `backlogPath` is REMOVED from the payload and from `ui/src/api/tasks.ts`.
- `sourcePath` replaces it and names the file actually parsed: the store when
  one exists, the markdown only on the genuine storeless fallback (a fresh root
  or a SPEC-110 target with no store).
- Store rows carry their `deps` through unchanged; `_parse_deps` is demoted to
  the fallback parse. `tasks_board.task_rows` is the ONE authoritative row
  source shared with the SPEC-154/155 guards.
- SPEC-110 per-target grouping (reqs 8-10) is untouched.

Pinned by `tb-8` (both sides: storeless declares the markdown, stored declares
the store, and dep tags survive the round trip).
