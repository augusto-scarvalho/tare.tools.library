# Tasks canonical store — A1 `tasks import/add/move/close` (`tasks-store-cli`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/ts_tasks_store.py).

Intake (SPEC-116 door NEW): owner decision 2026-07-13 #3 — "`tasks.json`
canonical: `.harness/state/tasks.json` is the operational truth
(lanes/status/priority/wfid), written ONLY by the `tasks` CLI verb; the backlog
markdown stays the human prose document, its tables FREEZE after `tasks import`
(history, not state); in-execution lanes stay derived-per-poll, never stored."
Covered-check: `panel-tasks-board.md` ships only the A0 DERIVED board and names
this store as the next increment. Decision: **NEW** (A1). SLICE: store + CLI
verbs + board integration ONLY — `tasks enqueue` (A2), per-target stores (A3)
and the GUI `tasks-move` allowlisted action stay OPEN in the backlog.

## Goal

Give tasks an operational truth the markdown cannot be: a single JSON store
whose lanes survive re-imports, written through exactly one path (the `tasks`
CLI), with the backlog markdown demoted to frozen history at the moment the
owner runs `tasks import`.

## Applicability

Applies to `scripts/harness_lib/tasks_store.py` (store + verbs),
`tasks_board.cmd_tasks` dispatch + store-first `tasks_snapshot`, and the
extended `tasks` parser registration in `cli_registry.py` (zero `harness.py`
edits). Nothing writes the store outside the `tasks` verb; the panel keeps
writing no canonical state (a GUI lane-move action is NOT part of this slice).
This spec does not run `tasks import` on the harness repo — the freeze is an
owner-triggered operational act.

## Requirements / invariants (numbered, testable)

1. **Single write path.** `.harness/state/tasks.json` is written only by
   `tasks import|add|move|close` (via `tasks_store._save`). The board
   collector and panel route stay pure reads.
2. **Idempotent import, preserved state.** `tasks import` parses the backlog
   tables (reusing `tasks_board._backlog_rows`); re-import adds no duplicates
   (keyed by id), updates row metadata, and PRESERVES an existing row's
   lane/wfid/createdAt — a manual move survives re-import. Struck rows import
   as `done`; rows from the transient "LOOP QUEUE" section are skipped.
   The first import stamps `frozenBacklogAt`.
3. **Freeze semantics.** Once the store exists, `tasks_snapshot` reads rows
   from the store INSTEAD of the markdown (structural freeze — tables are
   history); escalation and live-worker rows stay derived per poll.
4. **Derived lanes never stored.** Manual lanes are
   `idea|backlog|ready|queued|done`; `move` refuses `running`/`review`
   (derived from live workers) and unknown lanes; refusals and unknown ids
   exit 2 through `HarnessError`, never a traceback.
5. **Lifecycle.** `add` refuses duplicate ids and derives a slug id from the
   title when `--id` is absent; `close <id>` = move to `done` + `closedAt`.
6. **Registry-only surface.** The `tasks` verb keeps its position in the
   frozen top-level surface; only its parser arguments grew
   (`testing/scenarios/cli_registry.py`).

## Gherkin scenarios

```gherkin
Feature: canonical tasks store (owner decision #3)

  Scenario: [ts-1] import is idempotent and skips the transient queue section
    Given a temp root whose backlog has one open row, one struck row and a
      LOOP QUEUE table
    When tasks import runs twice with a manual lane move in between
    Then the store holds exactly the two rows, the struck one in done,
      the queue row skipped, and the moved row keeps its manual lane

  Scenario: [ts-2] lifecycle verbs enforce the lane rules
    Given a store with a manually added task
    When move targets a derived lane, add reuses the id, or move names an
      unknown id
    Then each refusal raises (exit 2 via HarnessError) and close moves the
      task to done with closedAt

  Scenario: [ts-3] the markdown freezes once the store exists
    Given an imported store and a backlog markdown edited afterwards
    When tasks_snapshot runs
    Then rows come from the store (the markdown edit is invisible) and live
      worker rows are still derived per poll

  Scenario: [ts-4] the repo store is never created as a side effect
    Given this repository without .harness/state/tasks.json
    When "tasks move nope backlog" runs
    Then it exits 2 with a clean error and the store file still does not exist
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Store canônico + freeze das tabelas + lanes derivadas nunca armazenadas | owner decision 2026-07-13 #3 (`docs/IMPLEMENTATION_BACKLOG.md` open-decisions) |
| Single-write-path pelo verbo CLI | regra do `targets register` (`targets.py`); GUI-writes-no-state (SPEC-114) |
| Reuso do parser de tabelas do A0 (um parser, não dois) | `tasks_board._backlog_rows`; ladder rung 2 (reuse) |
| Import idempotente preservando lane/wfid | roadmap `screens-tasks-queue.md` A1 ("idempotent, keyed by ID/slug") |
| Erros via `HarnessError` (exit 2) | `research_admin.py` precedent; `main()` ignora return codes de handler |
| Freeze estrutural (board lê o store) em vez de reescrever o markdown | decisão #3 "history, not state"; nada reescreve o documento humano |

## Test strategy

- Behaviors: fabricated temp roots — double import with an interleaved move
  (ts-1); add/move/close + the three refusals (ts-2); post-import markdown
  edit invisible + worker rows still derived (ts-3); live CLI refusal on this
  repo proves no side-effect store creation (ts-4, subprocess).
- Edge cases: missing store → board falls back to markdown (A0 behavior,
  covered by tb-1); empty title/id refused; close of unknown id exits 2.
- Regression net: `tb_tasks_board.py` keeps the A0 fallback green;
  `cli_registry.py` scenario keeps the frozen surface.
- Coverage: deterministic, stdlib-only — `testing/scenarios/ts_tasks_store.py`
  plus the module self-check (`python scripts/harness_lib/tasks_store.py`).

## Validation

- `python testing/scenarios/ts_tasks_store.py` — ts-1..ts-4 green.
- `python scripts/harness_lib/tasks_store.py` — module self-check.
- `python testing/scenarios/tb_tasks_board.py` — A0 fallback intact.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.

## Amendment v2 — `backlog-json-canonical` (2026-07-27)

Shipped in five phases (`d0de54c`, `10a50cf`, `16c0c48`, `69cb2ae`, `3ed29f6`);
plan + critique in `docs/research/plan-backlog-json-canonical-DRAFT.md`.

**Why.** Half of decision #3 shipped in 2026-07: `tasks_snapshot` began reading
the store INSTEAD of the markdown, but the tables never froze in practice —
every writer kept registering rows in the document. The reader was frozen and
the writer was not, and the payload declared `backlogPath` while serving the
store, so ten days of divergence went unseen: 16 document rows invisible on
every derived surface, 84 rows archived in the 2026-07-19 grooms still on the
board, 15 closures the store never learned, and 77 dep-tagged rows importing as
**zero** graph edges (`topo_order` was sorting 284 nodes and 0 arcs).

**Invariant deltas.**

1. **Inv 1 (single write path)** stands and is now ENFORCED, not merely stated:
   every mutating verb runs under `store_lock` (`O_CREAT|O_EXCL`, re-entrant by
   depth because `close` calls `move`, stale-break at 30 s). Whole-document
   read-modify-write loses one of two concurrent writes; the markdown tolerated
   concurrent writers only because two agents edited different LINES.
2. **Inv 2 (idempotent import)** keeps preserving a manual lane move — correct
   while the document mirrored the store. `import --migrate` is the ONE-TIME
   exception: it refuses to write on a duplicate id, propagates a struck
   document row onto a store row still open, and retires what the document
   dropped (archived → `done`+`archivedAt`; parse artifacts purged; an OPEN
   document-sourced stray reported). The verb itself is NOT retired — it still
   serves a storeless root and SPEC-110 targets.
3. **Inv 3 (freeze semantics)** is superseded. The store IS the backlog;
   `docs/IMPLEMENTATION_BACKLOG.md` carries zero task rows and the markdown
   parse survives only as the storeless-root fallback. `sp_store_parity` sp-1
   fails the gate if a task table regrows.
4. **New fields.** `body` (the row's full prose, EVERY cell after the id,
   `BODY_CAP` 16000, over-cap REFUSED never truncated), `deps` (structured,
   consumed as-is by `topo_order`/`dep_graph`, never re-parsed from free text)
   and `noDeps` (the SPEC-155 assessment marker, replacing the `" no-deps"`
   title suffix — a store-only row has no document prose to carry it).
5. **New surface.** `tasks show <id>` (one row with its prose; without it the
   retirement would make a body unreadable in a terminal), `tasks dep <id>
   <kind> <otherId>|no-deps`, and `--body -` / `--text -` reading from STDIN —
   never argv (the `keys set NAME` precedent; bodies are routinely kilobytes).

**Lesson recorded in the tests.** The first `body` carried only cell 1, so the
`| Item | Why | Signal |` tables lost a whole column while the reconciliation —
`len(body) >= len(title)` — passed. A length check cannot see a column vanish.
ts-6 now reconciles CELL by cell against a real corpus (`docs/backlog-archive.md`).

**Validation delta.** `ts-1..ts-8` (ts-6 real-corpus fidelity, ts-7 the write
path, ts-8 the lock, deterministic not probabilistic); `sp_store_parity` sp-1/2;
`tb-8` source honesty; `si-3e` the staged store under the gate hold.
