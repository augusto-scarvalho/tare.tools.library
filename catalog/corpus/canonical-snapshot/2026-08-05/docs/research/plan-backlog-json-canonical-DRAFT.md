# Plan (DRAFT) — the backlog becomes the JSON store; the markdown tables retire

Author: `planner` spawn (Fable, effort `high`), 2026-07-27. Read-only run; plan
returned as result text and written to disk by the overseer, unmodified except
for HTML-entity unescaping.

Brief: `.harness/handoff/plan-backlog-json-canonical.READY`. Measured facts taken
as GIVEN (2026-07-27, HEAD `a91b85f`). Code anchors verified by the author by
reading source; the overseer independently re-verified V2, V3, V4 and the
phantom-row counts (see "Overseer verification" at the end).

---

## 1. Verdict on the brief

**The direction is right, and the numbers prove it more strongly than the brief argues.** Fact 1 (0 of 284 board rows come from the markdown) means the markdown is *already* not the operational backlog — every operational consumer (board, `/api/tasks`, GUI views, `dep_graph`, `provenance`) is store-fed today. The only markdown readers left are the two guards, the advisor, and the manual import seam (brief's "two universes" table, verified at `testing/scenarios/bc_backlog_closure.py:103`, `testing/scenarios/eg_entry_groom.py:100,106`, `tools/hooks/delivery_bar_advisor.py:128`). Retiring the tables is not a migration of the operational system; it is a migration of the *writers* and the *guards*. That reframing drives the phasing below. (fonte: brief facts 1-2 + verified anchors, 2026-07-27, alta confiança)

Where the brief is wrong or under-weighted:

**V1 — Fact 8 must lead the plan, not sit at question #2.** The empty dep graph is not a design question; it is a two-site import bug: `import_backlog`'s `meta` dict (`tasks_store.py:102-104`) drops the `deps` that `_backlog_rows` *already parses* (`tasks_board.py:128`), and `board_rows` (`tasks_store.py:271-282`) doesn't emit them, so `tasks_snapshot:308` `setdefault`s an empty map onto every store row. Consequence: `topo_order` (284 nodes, 0 edges), `dep_graph.derive_graph` (`dep_graph.py:216,298`), `harness.py provenance`, and the *rationale* of SPEC-155 all run on empty input — a whole shipped subsystem dead-armed by ~4 missing lines. This fix is shippable today, independent of retirement, and is the highest value-per-line item in the entire plan. Phase 1 below is exactly this, and it would be Phase 1 even if the owner reversed the retirement decision tomorrow. (fonte: código verificado nas linhas citadas, 2026-07-27, alta confiança)

**V2 — The brief's root-cause sentence is incomplete, and it matters for migration.** "We froze the reader without freezing the writer" explains the 16 missing rows, but NOT the 15 lane drifts. Those are caused by shipped invariant 2 itself: `import_backlog` PRESERVES an existing row's lane on re-import (`tasks_store.py:111`, spec `tasks-store.md` inv 2 — "a manual move survives re-import"). That preservation is correct for manual moves and *wrong* for markdown strikes made while the markdown was still the live writer: re-running today's import fixes 0 of the 15 drifts. Any migration that "just re-imports" — even with the deps/prose fix — leaves closed items rendering as open. The migration import needs a one-time done-propagation override (Phase 2). The brief's Risk "Import reuse" names the cap and the deps but misses this third inherited defect. (fonte: `tasks_store.py:105-111` + brief fact 6, alta confiança)

**V3 — The regrowth lever is misnamed: AGENTS.md contains no backlog instruction at all.** Verified: zero matches for `backlog`/`IMPLEMENTATION_BACKLOG`/`table row` in the 153-line `AGENTS.md`. The row-add discipline lives in the playbook chain and in the guards' own error text: `overseer-playbook.md:79` (row-strikes), `:205-207` (SPEC-154 lockstep — "the row struck in the SAME commit"), `overseer-loop-playbook.md:122` ("gets a backlog row"), `backlog-groom-playbook.md:36` (groom route `backlog`), plus `bc-1`'s message "mark the row done/archive" (`bc_backlog_closure.py:128`) and `eg-1`'s "map deps ... or mark no-deps" (`eg_entry_groom.py:112-113`). Open Q3's "corresponding change to AGENTS.md" targets the wrong file — and adding it there would violate AGENTS.md's own content-hygiene rule (project-specific process belongs in the playbook chain; SPEC-170 Q3 thin-shim). The Phase 4 write-path edits target the playbooks and the guard messages. (fonte: grep + leitura integral de AGENTS.md, 2026-07-27, alta confiança)

**V4 — A missing risk that is a hard deadlock, not a data-loss footnote.** The brief lists "the hold" only as write-erasure risk (fact 12). The sharper problem: `scenario_isolation.hold_dirty_baseline` special-cases the backlog with `git checkout-index` so SPEC-154/155 validate the **STAGED** rows during the gate (`scenario_isolation.py:197-204` — the comment says exactly why). If the guards are repointed to the store WITHOUT extending that special case to `.harness/state/tasks.json`, then during `gate-staged` the guards read the store at **HEAD** — and the commit that ships a scenario plus its `tasks close` can *never* pass bc-1, because the close is staged, not at HEAD. SPEC-154's closure-lockstep becomes structurally unsatisfiable. Phase 3 carries this as a required change with its own check. (fonte: `scenario_isolation.py:169-204` lido hoje, alta confiança)

**V5 — Decided #2 keeps one live table in a "tables retire" document; make the exception structural, and note its corollary.** The self-review inbox is a marker-delimited auto-generated *table* (`self_review.py:462-486`, `INBOX_START/END` at :38-39). Keeping it is right (it is triage, not tasks; eg-1 already excludes it). But two consequences the brief doesn't draw: (a) the retirement tripwire and any residual parse must exclude the marker block; (b) `tasks import` must RETIRE with the tables — today it happily imports inbox findings as store rows (they are `_backlog_rows` output and not in a "loop queue" section), which means the live store almost certainly carries inbox-finding phantom rows plus the GUI phase-matrix phantoms eg-1 papers over (`eg_entry_groom.py:19-24`). Migration purges both classes (Phase 2, owner-confirmable list). Not a disagreement with Decided #2 — a required tightening.

**V6 — Decided items I examined and accept without reservation.** #1 (direction — argued above), #3 (no renderer — `write_json` emits `indent=2` (`common.py:141-150`), so a one-row change is a small per-field git diff, not an opaque 149 KB blob; the review-surface risk is real but mild), #4 (no-loss migration — it is the whole point). On open Q8 I recommend *closing* concurrency now rather than deferring: this plan's explicit purpose is to multiply writers onto the single RMW path (`load`→mutate→`_save`), which converts today's theoretical race into the expected steady state. Deferring it would be deferring a defect into the traffic the plan itself creates. It costs ~15 lines (Phase 5).

## 2. Target design

Stated as a testable contract.

**Source of truth.** `.harness/state/tasks.json` is THE backlog. `docs/IMPLEMENTATION_BACKLOG.md` survives as prose: section headers, the numbered owner-decision list, the marker-delimited self-review inbox block. It contains zero task-table rows outside the inbox markers. `docs/backlog-archive.md` stays as frozen history. The store stays git-tracked.

**Schema (`schemaVersion: "2.0"`).** Per task:

| field | contract |
|---|---|
| `id` | slug, unique (enforced at `add`, at migration import, and by the parity check) |
| `title` | display line, ≤160 chars, required |
| `body` | full prose (multi-KB). New. `BODY_CAP = 16000` (= existing `NOTES_CAP`); a write over cap is **refused** (exit 2, "split or move to plan") — never truncated. Largest migrated row is 8,959 (fact 7): fits. |
| `notes` | unchanged — owner's complementary notes only (`tasks_store.py:188-195`). Migration does NOT write into it; row prose is provenance-distinct from owner notes. |
| `plan` | unchanged (`PLAN_CAP` 64000, append-only) |
| `deps` | **structured, first-class**: `{"dependsOn": [], "blocks": [], "relatesTo": [], "duplicates": []}`. Written at migration (parsed once from the raw Item cell via `_parse_deps`) and afterward only by `tasks dep` / `tasks add --dep`. Never re-parsed from free text on read: `tasks_snapshot` and `board_rows` pass the stored map through; `topo_order` and `dep_graph` consume `row["deps"]` **unchanged** — they already read exactly this shape (`tasks_board.py:267-273`, `dep_graph.py:216`). |
| `noDeps` | boolean — the explicit SPEC-155 assessment marker, replacing the `" no-deps"` string appended to titles (`tasks_store.py:137-141`). Assessment := `any(deps values) or noDeps`. |
| rest | `category,size,priority,section,source,lane,wfid,createdAt,updatedAt,closedAt,dispatch*` unchanged |

**Write path.** All writes via the `tasks` verb, whole-doc mutation under a lockfile (Phase 5):

- `tasks add <title> [--id] [--category] [--size] [--priority] [--dep <kind>:<id> ...] [--no-deps] [--body -]` — body is read from **stdin only** (`keys set` precedent, owner decision 2026-07-13 #2 wording); never argv.
- `tasks note <id> -` gains the same stdin form (today's `--text` argv stays for short notes).
- `tasks dep <id> <depends-on|blocks|relates-to|duplicates> <otherId>` and `tasks dep <id> --none`. Unknown `<otherId>` warns (topo already ignores ghost edges, `tasks_board.py:261-263`) but is allowed — cross-referencing future work is legitimate.
- `tasks import` **retires** after migration (Phase 4): the seam it bridges no longer exists, and leaving it live re-imports inbox findings from the residual doc.
- `move/close/delete/plan/refine/dispatch` unchanged.

**Snapshot honesty.** `tasks_snapshot` declares the source it actually read: `sourcePath: ".harness/state/tasks.json"` (or the markdown path only in the genuine pre-store fallback, which remains for storeless roots/targets — `tb-1`/A0 behavior and the SPEC-110 seam are untouched). `backlogPath` is removed from the payload and from `ui/src/api/tasks.ts:62`. This kills the fact-2 declared-vs-real lie.

**Guards.** SPEC-154 open-ness and SPEC-155 assessment read the store; during `gate-staged` they read the **staged** store via the same checkout-index mechanism the backlog uses today (V4). Exact invariant deltas in §7.

## 3. Phased plan

Each phase independently shippable; each check runs against the LIVE store/doc (not its own fixture), fails today, passes after. Gate wiring: prefer extending existing scenarios; exactly one new scenario file (`sp_store_parity.py`), one line in `spec_test_gate.py` (ratchet safe).

**Phase 1 — Import/row fidelity (the fact-8 fix).**

- Touches: `scripts/harness_lib/tasks_store.py` (`import_backlog` meta gains `deps` + `body`; duplicate-id-in-one-parse detection → collected and reported loudly; `board_rows` emits `deps`/`body`), `scripts/harness_lib/tasks_board.py` (`_backlog_rows` rows gain `"body"`: the raw Item cell before the `[:160]` cap — additive key, no consumer breaks), `testing/scenarios/ts_tasks_store.py`.
- Check (fails today): live-corpus round-trip — parse the LIVE `docs/IMPLEMENTATION_BACKLOG.md`, import into a **temp** store, assert (a) count of rows carrying ≥1 dep tag in the doc == count carrying structured deps in the temp store (today: 77 → 0), (b) per-id `len(body)` ≥ len of the cleaned Item cell (today: 151 rows truncated), (c) the duplicate id (`wf-parallel-default-flip`) is *reported*. Live read + hermetic write — this is the brief's own fact-4 proof method, and it is not the import-then-read-a-fixture tautology because its input is the live document.
- Acceptance: check green; existing ts-1..ts-4 green; live store untouched (repo import remains owner-triggered, tasks-store.md Applicability).
- Rollback: revert the commit; store schema untouched (fields are additive).

**Phase 2 — Migration execution + the parity guard.** (Details in §4.)

- Touches: `docs/IMPLEMENTATION_BACKLOG.md` (dup-id rename only), `.harness/state/tasks.json` (via the migration import), new `testing/scenarios/sp_store_parity.py`, one gate line.
- Check (fails today in four directions): `sp_store_parity` against the LIVE pair — every open doc row id exists in the store (16 missing today); every store id exists in doc or archive (84 ghosts today); lane parity for shared ids (15+1 drifts today); doc dep-tag rows ⊆ store structured-deps rows (77→0 today); no duplicate store ids. This scenario is the standing anti-divergence teeth for the whole window between Phase 2 and Phase 4 — while both surfaces exist, any writer touching only one of them turns the gate red, which forcibly ends the dual-writer era *before* the tables leave.
- Acceptance: parity green; reconciliation report printed with the §4 numbers.
- Rollback: `git revert` of the store+doc commit (both tracked — fact 11 is the recovery surface).

**Phase 3 — Guards repoint + staged-store seam + source honesty.**

- Touches: `testing/scenarios/bc_backlog_closure.py` (`open_slugs` → store lanes; bc-2 existence → store ids ∪ archive text), `testing/scenarios/eg_entry_groom.py` (assessment → structured `deps`/`noDeps`; delete the phase-matrix and inbox scope-out ceilings and the raw-line `no-deps` scan — all three exist only because the source was free text), `tools/hooks/delivery_bar_advisor.py:120-130` (same one-function swap, still fail-open), `scripts/harness_lib/scenario_isolation.py` (generalize the `_BACKLOG_REL` checkout-index special case at :197-204 into a two-entry validated-docs list including `.harness/state/tasks.json` — V4), `scripts/harness_lib/tasks_board.py` (`sourcePath` honesty), `ui/src/api/tasks.ts`.
- Check (fails today): `bc.open_slugs(ROOT) ⊆ {store ids}` — false today because the 16 post-07-24 rows are open in the markdown and absent from the store; plus snapshot honesty: the payload's declared source is a file whose parsed rows == the payload's non-derived rows (false today, fact 2). The staged-seam gets its own assertion in the isolation self-check (staged store content visible under a hold).
- Acceptance: bc/eg/advisor produce identical verdicts from the store as from the (now-parity) markdown; gate green including a simulated staged `tasks close`.
- Rollback: revert; markdown is still intact and parity-true, so guards can point back.
- Ordering constraint (hard): must land AFTER Phase 2 — repointing before reconciliation makes bc-1 red on ghost-open store rows and eg-1 red on 265 dep-less rows.

**Phase 4 — Agent write path, playbooks, and table retirement.**

- 4a (write path, shippable alone): `tasks add --body -` / `--dep` / `--no-deps` structural, `tasks note <id> -`, new `tasks dep` sub-action, `BODY_CAP` refusal; playbook edits (V3 targets: `overseer-playbook.md:205-207` lockstep now says "run `tasks close <slug>` in the same commit", `overseer-loop-playbook.md:122`, `backlog-groom-playbook.md` route `backlog` → `tasks add`; guard messages updated) via `protect_canonical_files.py edit` where protected. Check (fails today): `tasks add` with a 5 KB stdin body stores it un-truncated and dep tags land structured — today there is no body field at all and `add` caps title at 160.
- 4b (retirement, requires 4a+P3): delete the task tables from the doc (prose/decisions/inbox stay); retire `tasks import` (surface delta registered in `testing/scenarios/cli_registry.py`); morph `sp_store_parity` into the regrowth tripwire: `_backlog_rows(live doc)` minus the inbox marker block == 0 rows (fails today: 198). Check = that tripwire.
- Acceptance: tripwire green; bc-2 still resolves archived slugs; GUI unchanged (it never read the markdown).
- Rollback: 4b is a single doc+scenario commit; `git revert` restores the tables byte-identically.

**Phase 5 — Concurrency close (Q8).**

- Touches: `tasks_store.py` only — an `O_CREAT|O_EXCL` lockfile (`tasks.json.lock`) context manager wrapping each verb's load→mutate→`_save`; retry ~10 s; stale-lock break after 30 s with a loud print naming the holder pid. ~15 lines. `# ponytail: single-host file lock; upgrade to per-id merge only if lock contention is ever measured.`
- Check: deterministic self-check — with the lock held by a live pid, a second acquire waits then raises cleanly; with a dead-pid stale lock, it breaks through. (An 8-way subprocess add smoke is optional color, not the gate check — probabilistic failure is not falsifiable.)
- Acceptance: all verbs route through the lock; `write_json` atomic-replace behavior unchanged.
- Rollback: revert; behavior degrades to today's RMW.

## 4. Migration (Phase 2 detail)

Baseline numbers = facts 4-8. Order:

1. **Pre-step (owner, markdown edit):** rename the open L574 duplicate to `wf-parallel-default-flip-phase2` (recommendation; owner may pick the slug). This is the only doc edit before the final import — resolving fact 9 at the source, where a human can still see the collision.
2. **Final import** (`tasks import --migrate`, a one-time flag on the Phase-1 importer) over the live pair, with three one-time overrides that the steady-state importer never had: (a) done-propagation — a struck doc row forces `lane: done` on its store row (fixes the 15 drifts; V2); (b) body/deps backfill onto EXISTING rows, not just new ones; (c) refuse to write if any unresolved duplicate id remains.
3. **Ghost reconciliation (groom, not code — Q9):** store rows absent from the doc AND whole-token-present in `docs/backlog-archive.md` → `lane: done` + `archivedAt` stamp. **Keep, don't delete** — done rows are invisible operationally, preserve id-existence for bc-2, and deletion buys nothing. Expected: 84. Rows absent from BOTH → printed for owner triage (expected ≈ the phantom classes below, else ~0).
4. **Phantom purge (owner-confirmed list):** GUI phase-matrix pseudo-rows (`0 Fundacao`…) and self-review-inbox findings that earlier imports minted as tasks → `tasks delete` (they are re-derivable / not tasks by design; V5).
5. **Reconciliation proof, printed and kept in the migration commit message:**
   - rows: every one of the 16 fact-4 ids present and open in the store; store total == (doc open+done rows − loop-queue − phantoms) + archived-done ghosts;
   - prose: Σ store `body` chars ≥ 130,030 minus strike-markup chars; per-id `len(body)` ≥ cleaned Item-cell length; zero truncation warnings;
   - deps: structured-deps row count == 77 (doc dep-tag rows), tag-for-tag per id;
   - lanes: 0 drifts (the 15+1 resolved); duplicate ids: 0.
6. `sp_store_parity` goes green and stays in the gate.

**One-way steps and sufficiency of git.** The table deletion (Phase 4b) and the phantom purge are the only one-way steps, and both are single tracked-file commits — git history holds the tables byte-identically, the archive doc survives untouched, and post-migration the store's `body` carries the full prose. That is sufficient: three independent copies of the history (git log of the doc, archive doc, store bodies), versus today's one truncated copy. `frozenBacklogAt` becomes a historical stamp; the migration import updates it once, then the concept retires with the verb.

## 5. What I would NOT build

- **JSON→markdown renderer** (Decided #3, agreed). Change condition: a real incident where a bad store change passed review because the diff was unreadable.
- **Per-task files / directory-sharded store** (one file per task for diff ergonomics and lock-free concurrency). Condition: measured merge conflicts or lock contention on `tasks.json` across concurrent branches/agents.
- **SQLite or any non-JSON backend.** Condition: store size > ~2 MB or measured GUI read latency. 149 KB indent-2 JSON read whole per poll is nothing.
- **A schema-migration framework.** The `schemaVersion` string flips to `"2.0"`; all new fields are additive; `load()`'s empty-shell default already tolerates absence. Nothing else.
- **A generic dep editor / graph GUI, or the PROPOSED→VERIFIED promotion audit** (`dep_graph.py:234-237`'s named deferred piece). Condition: the dep graph being non-empty for a while and someone actually consuming `provenance` in anger.
- **Moving the store out of `.harness/state/` (Q5 answer).** It stays. Consequences accepted, named: (a) gate-held — a task write during a gate run is erased; that is the existing repo-wide rule ("never write `.harness/` while a gate is in flight") and the store is git-tracked, so the loss has a recovery surface; the guards' staged-view need is solved by the Phase-3 checkout-index seam, not by relocation. (b) It stays outside `precommitValidation.surfaceRoots` — exactly like `docs/` today; tracked as `gate-surface-definition`, not fixed or worsened here. (c) "state means transient" semantics bend — accepted; relocation would touch `STORE_REL`, isolation targets, two specs, and the SPEC-110 per-target mirror (`.harness/state/targets/<name>/tasks.json`, `panel-tasks-board.md` req 9) for purely semantic gain, and would *lose* the free scenario-isolation coverage the state dir already provides (`scenario_isolation.py:49`).

## 6. Open owner decisions

1. **Ghost policy (Q9):** recommendation — keep all 84 as `done`+`archivedAt` (step 3 above); delete nothing. Alternative (delete) only saves ~45 KB of file.
2. **Duplicate-id rename (Q4/fact 9):** recommendation — `wf-parallel-default-flip-phase2`; any slug works, but it must happen before the final import (the importer will refuse otherwise).
3. **Phantom purge list:** recommendation — purge GUI phase-matrix rows and imported inbox findings from the store; the owner confirms the printed list before deletion since `tasks delete` is destructive.
4. **Concurrency now vs deferred (Q8):** recommendation — now (Phase 5, ~15 lines). If deferred, the recorded ceiling is: "whole-doc RMW; two concurrent `tasks` writes can lose one; single-writer discipline is contractual only" — and it must be written into the tasks-store spec amendment, not left implicit.
5. **Decision-list amendment text:** the owner appends the superseding decision under `docs/IMPLEMENTATION_BACKLOG.md` L183-195 (the list survives per Decided #2); the plan cannot write the owner's decision for them. Proposed wording is in §7.

## 7. Amendment targets (SPEC-116 — versioned amendment door, no new intake)

- **`specs/40-features/tasks-store.md` — amendment v2.** Inv 1: single write path stands, now lock-enforced (Phase 5), and gains `body`/`deps`/`noDeps` fields with the cap-refusal rule (no silent truncation — Decided #4, house precedent `result_contracts.bound_soft_fields`, commit `a91b85f`). Inv 2 (idempotent import): **retired** after the one-time `--migrate` run; the import verb leaves the surface (cli_registry delta). Inv 3 (freeze semantics): reworded from "tables freeze after import" to "the store IS the backlog; the markdown parse survives only as the storeless-root fallback (A0/targets)". Inv 5 (`add`): dup-refusal unchanged; assessment becomes structural (`--dep`/`--no-deps`), stdin body.
- **`specs/40-features/panel-tasks-board.md` — amendment v4.** Req 1/v2: source honesty — the payload declares `sourcePath` = the file actually read; `backlogPath` removed (with `ui/src/api/tasks.ts:62`). Deps for store rows come from the structured field, `_parse_deps` demoted to the fallback parse only. Reqs 8-10 (SPEC-110) untouched.
- **`specs/40-features/backlog-closure-guard.md` (SPEC-154) — amendment.** bc-1 open-ness source: store lanes (staged content under the gate hold); bc-2 existence: store ids ∪ `docs/backlog-archive.md`; invariant meaning unchanged ("shipping a scenario obliges closing the task in the same commit" — now via `tasks close`). The doc-based "absent = archived = closed" clause is restated store-side.
- **`specs/40-features/backlog-entry-groom.md` (SPEC-155) — amendment.** eg-1 source: open store rows must satisfy `any(deps) or noDeps`; the phase-matrix ceiling, the inbox scope-out, and the raw-line `no-deps` scan are deleted (their causes — free-text source and phantom imports — no longer exist).
- **`scripts/harness_lib/scenario_isolation.py`** — not a spec, but the gate-hold contract change (validated-docs checkout-index list gains the store) should be named inside the tasks-store amendment so the staged-view behavior is contractual, not incidental (V4).
- **Owner decision list** (`docs/IMPLEMENTATION_BACKLOG.md` L183-190): proposed appended decision — "2026-07-xx: supersedes #3's freeze clause — the tables retire; `.harness/state/tasks.json` is the backlog; the markdown survives as prose + decisions + the self-review inbox block; writes only via `tasks` verbs (body via stdin); SPEC-154/155 enforce against the store."
- **Playbook chain** (V3): `overseer-playbook.md`, `overseer-loop-playbook.md`, `backlog-groom-playbook.md` — the write-path sentences; edits through `tools/hooks/protect_canonical_files.py edit` (protected files).

Fontes: all `file:line` anchors above read directly by the author (alta confiança); all counts/dates from the brief's measured facts (given); recommendations marked as such are `referência: judgment`.

---

## Overseer verification (2026-07-27, independent of the author)

Four load-bearing claims re-checked directly before accepting this plan:

| claim | verdict | evidence |
|---|---|---|
| V3 — `AGENTS.md` has no backlog instruction | **CONFIRMED** | `grep -cE "backlog\|IMPLEMENTATION_BACKLOG" AGENTS.md` → `0` (153 lines). Discipline found instead at `overseer-loop-playbook.md:122`, `overseer-playbook.md:207`. |
| V4 — the backlog is re-materialized from the index during the gate, so the guards see STAGED rows | **CONFIRMED** | `scenario_isolation.py:197-204`, `git checkout-index -f -- <backlog>`, with the comment naming SPEC-154/155 explicitly. The deadlock V4 predicts for a store-backed guard is real. |
| V2 — a plain re-import fixes 0 of the 15 lane drifts | **CONFIRMED** | `tasks_store.py:105-111` — `continue  # lane/wfid/createdAt preserved`. |
| V5 — the live store already carries phantom rows | **CONFIRMED, quantified** | 13 rows whose `section` contains "inbox" (`delegation-cost-trend`, `self-lib-file-budget`, `workflow-cost-outlier`, the 10 `mf-*` triage rows) + 9 GUI phase-matrix pseudo-rows (`'0 Fundação'`, `'1 Shell'`, `'1 X-cutting'`, `'2 Workbench'`, `'3 Operations'`, `'4 Experiments'`, …). |

Consequence for the brief: open question 3 targeted the wrong file (V3), the root-cause sentence was incomplete (V2), and fact 12 understated the gate-hold problem — it is a deadlock, not only a data-loss window (V4). The brief is superseded by this document on those three points.

Not yet verified by the overseer, carried at the author's confidence: the `sp_store_parity` design, the `BODY_CAP` refusal semantics, and the §4 reconciliation arithmetic.
