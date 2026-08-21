# Refinement — IDE shard: confine GUI edits to a worker-style workspace (2026-07-23)

Status: refinement round for owner design decisions. Owner idea (2026-07-23):
"isolamento da IDE ... acontecem em um shard específico pra coisas da IDE, que é
consolidado pelos mesmos fluxos que hoje checam o código feito pelos agentes ...
Confinarmos a IDE, edição de arquivos e tudo que acontece ali a um shard como é
feito com os workers." Overseer assessment (shared): right layer — fs +
consolidation, not browser (`docs/research/ide-embedded-gui.md` picked the
editor lib; write discipline was always server-side); reuses SPEC-148; the
genuinely new piece is shard lifecycle. Recon spot-checked by the overseer
(ensure_pylsp venv path, gate-in-flight guard, ws_files root-parametrization).

## 1. Context

Today the GUI editor writes DIRECTLY into the live tree: CodeScreen `Mod-s`
(`ui/src/domains/workbench/CodeEditor.tsx:75`) → `saveFile` posts the
`ws-file-save` action with `confirm: true` (`ui/src/api/workspace.ts:99-108`) →
`ui_actions.run_action` applies confirm + human-only backstop + gate-in-flight
guard, then dispatches in-process (`scripts/harness_lib/ui_actions.py:672-684`)
→ `ws_files.save_file` writes bytes at `root / rel`
(`scripts/harness_lib/ws_files.py:98-117`). The owner's edits therefore land on
main with NO consolidation ritual, while agent edits pay workspace isolation +
merge plan + gate. The proposal inverts that: the GUI writes into a shard, and
one explicit **Integrate** action pushes the shard through the same
gate+reckon consolidation the agents' code passes.

## 2. Recon findings (source-verified)

### 2.1 SPEC-148 write-worker machinery (the reuse backbone)

| Piece | Where | IDE-shard role |
|---|---|---|
| Spec: tiers, rule 6 (OS lock), rule 11 (merge scan) | `specs/40-features/harness-sandbox.md:38-71,135-145` | contract to mirror or consciously relax (Q5) |
| Workspace creation, modes `temp-copy` / `git-worktree` | `workflow_prepare_write`, `scripts/harness_lib/workflow_writes.py:58-110`; worktrees at `:584-617` (`git worktree add -b harness/<wfid>/<wid> ... HEAD`) | precedent for shard creation; shard = one long-lived analogue |
| OS lock on protected files: read-only attr + specific-rights deny ACE (WD,AD,WA,WEA,DE; never generic W) | `harness-sandbox.md:53-60`; release via `sandbox_spawn.fs_release` before disposal (`workflow_writes.py:576,601,629`) | optional in the shard (Q5) |
| `protected-path-modified` at merge | `protected_workspace_mutations` (`workflow_writes.py:112-119`) feeding conflicts in `workflow_merge_plan` (`:197-198`); rule 11 (`harness-sandbox.md:142-145`) | reuse verbatim in Integrate — detection layer regardless of Q5 |
| Merge = copy into ROOT with backups, per-worker + final validation gate, optional rollback | `workflow_apply_merge` (`workflow_writes.py:354-507`), `workflow_rollback` (`:509`) | the batch analogue; Integrate is a simpler single-shard version |
| Worktree cleanup discipline (fs_release → `git worktree remove --force` → prune) | `workflow_cleanup_worktrees` (`workflow_writes.py:619-652`), `dispose_worker_copy` (`gate_parallel.py:215-229`) | shard dispose/refresh |

### 2.2 GUI write path today

- Trust boundary is ONE function: `ws_files.resolve_confined(root, rel)`
  (`ws_files.py:55-75`) — repo-relative POSIX only, symlink-resolved under
  `root`, deny `.harness/`, `.git/`, `vendor/`, secrets denylist, protected
  registry. **Already root-parametrized**: every ws_files function takes
  `root` as its first argument; `run_ws_action(root, action, params)`
  (`:187-200`) too.
- The server passes `self.root` everywhere: reads at `harness_ui.py:1318-1327`,
  actions at `:1359`, lint/format at `:1361-1367`.
- **What changes if the root is a shard: one line per route** — pass
  `shard_root` instead of `self.root` for the ws-file/lsp routes. The
  confinement, baseSha conflict (`save_file:110-113`), confirm and
  gate-in-flight guard all ride along unchanged. This is the cheapest possible
  re-rooting; no new trust boundary.
- Bonus: the gate-in-flight refusal (`ui_actions.py:679-682`) exists because a
  mid-gate live-tree save is clobbered by the per-scenario restore. A shard
  save touches nothing the restore holds — the guard can be RELAXED for shard
  writes (owner can keep editing during a 7-15 min gate). Integrate itself must
  keep the guard.

### 2.3 LSP shard-readiness (Lane A)

`uri_guard(root, uri)` (`scripts/harness_lib/lsp_ws.py:170-187`) and the whole
URI seam (`to_client_uri:202`, `to_server_message:232`) are root-parametrized
and delegate confinement to `ws_files.resolve_confined` (reused, never copied).
`serve_ws` takes `handler.root` (`lsp_ws.py:479,489`). Re-rooting = handing the
shard root to the connection. Two residual repo-root assumptions:

1. `ensure_pylsp` installs into `root / ".venv"` (`lsp_ws.py:283`) — the shard
   worktree has NO `.venv` (untracked). Fix: keep venv/interpreter pinned to
   the MAIN root; only the workspace `rootUri` moves.
2. Single global connection, last-tab-wins (`_current`, `:326-397`) — fine,
   the editor is the only consumer; ONE pylsp rooted at the shard, no
   duplication (see Q3).

### 2.4 Consolidation flow today — order of operations

Two flows exist; they answer "does the shard merge first or gate first"
differently:

- **Owner/manual discipline (the one commits actually pass):** stage →
  `gate-staged` detached (`gate_staged.py:99-131`; gate-while-dirty guard
  `:81-96` refuses staged-but-superseded copies) → `validate --staged` stamps
  the staged fingerprint (`validation_stamp.py:205-234,397`) → `reckon --record
  --verdict` keyed to the SAME fingerprint (`:328-370`) → commit (pre-commit
  enforces gate=pass AND reckon=no-blocker). **Merge (staging) first, then
  gate, with the index as the staging area.**
- **Worker batch flow:** merge-plan (footprint + protected scan) → apply =
  copy into ROOT with backups → gate after each worker + final gate, rollback
  on failure (`workflow_writes.py:354-507`). Operating discipline on top:
  review in worktree, hold, batch-integrate, ONE staged gate.

So "Integrate the IDE shard" should be: **apply shard diff to main's index →
gate-staged → reckon → commit**. Literally today's owner flow with the shard as
the durable edit buffer. It does NOT need `workflow_apply_merge`'s multi-worker
machinery — only its protected scan.

### 2.5 Worktree mechanics + the smw-2 lesson (long-lived shard pitfalls)

- gate-par worktrees are EPHEMERAL: detached, pinned to one sha (staged index
  pinned via dangling `commit-tree`, `gate_parallel.py:167-181`), attested
  clean (`:184-195`), disposed with force-remove + prune (`:215-229`). No
  rebase/refresh helper exists anywhere; the repo's refresh strategy is
  dispose-and-recreate.
- Worktree checkouts carry TRACKED content only (`gate_parallel.py:141-142`):
  no `.venv`, no `node_modules`, no `graphify-out/`, no `ui/dist`, no live
  `.harness/state`. The smw-2 lesson (`testing/scenarios/smw_svc_mcp_wiring.py:41-51`):
  a scenario writing untracked outputs doesn't round-trip in a worktree copy →
  honest SCENARIO-SKIP, recovered serially on the real root. **A long-lived
  shard inherits all of this: it is a fine EDIT surface and a poor EXECUTION
  surface.** That single fact drives Q3 and Q2's "gate on main, not in shard".

## 3. Design questions

### Q1 — Shard lifecycle

- **A. Create-on-first-edit, dispose-after-integrate (ephemeral like gate-par).**
  Cheap, always fresh; the worktree survives panel restarts, so only Integrate
  (or explicit Discard) disposes it.
- **B. Always-on long-lived worktree with rebase-on-advance.** Maximal
  availability; buys a rebase-conflict machine the repo has zero helpers for.
- **C. Per-session shards.** Multiplies disk and confusion; no consumer needs it.

**Recommendation: A-plus.** ONE shard (`git worktree add -b harness/ide-shard
<dir> HEAD`), created lazily on first `ws-file-*` mutation, persistent until
Integrate or explicit Discard, then dispose-and-recreate at the new HEAD (the
repo's only proven refresh idiom, `gate_parallel.py:198-229`). No rebase ever:
the shard is a staging buffer, not a branch with history. If main advances
while the shard is dirty, per-file `baseSha` (`save_file:110`) already
detects staleness at the file level; Integrate detects it wholesale (diff
against the shard's pinned base sha) and offers refresh-after-integrate or
discard. Placement: under the system tempdir or `.harness/runs/ide-shard/`
(deny-listed from itself) — gate-par precedent says tempdir, never under ROOT
in a listable place.

### Q2 — Integrate UX (end-to-end)

- **A. One-click pipeline: diff summary → confirm → stage-on-main → detached
  gate with visible progress → reckon prompt → commit.**
- **B. Stage-only button; owner finishes gate/reckon/commit in the terminal.**
- **C. Full workflow_apply_merge reuse (merge-plan artifact + apply + rollback).**

**Recommendation: A.** Concretely: (1) GUI shows `git diff <base>..shard`
summary (files + counts; per-file diff via the diff pane — see §3.7 legacy
merge-view salvage); (2) confirm dialog (existing mutating-action confirm);
(3) server applies shard files onto main's worktree+index
(`git restore --source=<shard-branch> -- <paths>` + `git add`), running
`protected_workspace_mutations` first — any hit refuses with
`protected-path-modified` exactly like rule 11; (4) launches `gate-staged`
(already detached, log+marker) — this is the SAME surface backlog item
5115c47c (detached-gates GUI visibility) needs, so the progress panel (marker
poll + log tail) pays for two items at once; (5) verdict shown; PASS → reckon
verdict dialog (`no-blocker`/`blocker` + note) → commit; FAIL → main's
worktree+index restored from HEAD, and — spelled out in the UI — **the shard
is untouched: every edit is still there, committed on `harness/ide-shard`;
fix and integrate again. Nothing is ever lost on a gate FAIL.**
Gate-while-dirty guard (`gate_staged.py:117-126`) may refuse when main has
unrelated dirt; surface that refusal verbatim.

### Q3 — What runs in the shard

- **A. Everything re-roots (edit + lint + format + LSP + tests/gate).**
- **B. Edit surfaces re-root; execution stays on main.**
- **C. Nothing re-roots except writes (reads from main).**

**Recommendation: B.** Re-root: `ws/file` read, `ws/list`, `ws-file-*` writes,
`/api/lint`, `/api/format`, `/api/lsp`. Lint/format are stdin-shaped
(`ws_files.py:206-275`) — cwd only selects the ruff config, which is tracked,
so they work in the shard as-is. LSP: shard root into `uri_guard`, venv pinned
to main (2.3). Tests and the gate NEVER run in the shard — smw-2 (2.5) proved
worktree copies are unfaithful execution environments for untracked-state
scenarios, and the owner flow gates on main's index anyway. Reading from the
shard (not split-brain main-reads/shard-writes) keeps the editor coherent:
what you see is what you save. Cost honesty: pylsp is NOT doubled (one
instance, last-tab-wins, re-rooted); disk IS roughly doubled for tracked
content (~one extra checkout; no `.venv`/`node_modules`, so far less than 2x
the working directory).

### Q4 — Proportional ritual for owner edits

- **A. Full worker ritual (merge-reviewer packet + gate + reckon).**
- **B. Gate + reckon only.**
- **C. Gate only.**

**Recommendation: B.** C is not actually available: the pre-commit hook
enforces gate=pass AND reckon=no-blocker on risk-bearing surfaces
(`validation_stamp.py:328-370`) — changing that for human edits would weaken
the floor for everyone. A adds a review step whose reviewer would be reviewing
the owner's own decisions — ceremony without information. Evidence trail for
human edits: the reckon row (verdict + `--note`, keyed to the staged
fingerprint, durable ledger `validation_stamp.py:275-294`) IS the changelog
ref; the Integrate dialog should pre-fill the note with the file list so the
ledger entry names what was touched.

### Q5 — Protected files inside the shard

- **A. Full SPEC-148 lock (RO attr + deny ACE) on shard protected files.**
- **B. API-layer refusal + merge-time scan only.**

**Recommendation: B.** The shard's ONLY writer is the GUI, and every GUI write
already passes `resolve_confined`, which refuses protected-registry paths
before any byte moves (`ws_files.py:71-74`) — the OS lock would defend against
a writer that cannot exist on this surface. Keep `protected_workspace_mutations`
at Integrate as the rule-11 backstop. Recorded ceiling: the moment any NON-GUI
writer gets shard access (a terminal-in-shard feature, an agent pointed at it),
apply `fs_confine` at shard creation — one call; the release path in disposal
helpers already exists (`workflow_writes.py:576`).

### Q6 — SPEC-114 amendment sentence

Current rule 1 (`specs/40-features/supervision-m5-interactive-panel.md:21`):
"Every mutating panel action is an existing allowlisted subcommand ... The
panel never edits `.harness/` state files directly." Plus SPEC-147 inv 6-8
(`specs/40-features/chat-workspace.md:59-73`). Proposed amendment:

> **Workspace writes are shard-only.** The `ws-file-*` verbs mutate ONLY the
> IDE shard worktree (`harness/ide-shard`), never the live tree; the live tree
> changes exclusively through the Integrate action, which stages the shard
> diff on main and consolidates it through the same `gate-staged` + `reckon`
> flow (and the same `protected-path-modified` merge scan, SPEC-148 rule 11)
> that governs agent-authored code. "GUI writes no state" is unchanged for
> `.harness/`; for the workspace it sharpens to "GUI writes shard-only".

### 3.7 Legacy-IDE salvage (inventory lane, 2026-07-23, overseer-verified)

Three findings feed the waves directly:

1. **`ws-file-create/-rename/-delete`** — server verbs exist, allow-listed and
   scenario-pinned (`m5_ui_panel.py:902`); the React explorer never calls them
   (verified: zero hits in CodeExplorer.tsx). Wiring buttons = effort S; lands
   naturally in W1 (the shard makes tree ops safe to expose).
2. **Diff/merge view** — `@codemirror/merge` 6.12.2 is vendored for the legacy
   panel (`vendor/codemirror/manifest.json`) but ABSENT from ui/package.json
   (verified). Porting it gives the Integrate dialog (Q2 step 1) a real
   side-by-side diff instead of parsed text rows; exact version already pinned
   = zero compat guesswork. Effort M; lands in W2.
3. **Already ported 1:1, nothing to do**: sha-conflict save flow, ruff
   lint/format, read-only explorer; the React side EXCEEDS legacy with the LSP
   (9ae4f91). Dead weight (mode-splitter chrome, floating-overlay math, vendor
   bundle except merge) dies with the legacy retirement (separate kill-list,
   intake filed, owner-gated on GUI polish completion).

## 4. Proposed wave split

| Wave | Size | Content |
|---|---|---|
| W1 shard lifecycle + re-root | M | `ide_shard.py` (create-lazy / status / dispose-recreate, reusing gate_parallel `_run_git`/dispose idioms); `harness_ui.py` ws-file/lsp/lint/format routes take the shard root; `ensure_pylsp` venv pinned to main; relax gate-in-flight guard for shard-only writes; + legacy salvage 1 (ws-file-* buttons in CodeExplorer); scenarios: shard confinement table, save-in-shard, live tree untouched |
| W2 Integrate | M | diff-summary endpoint; apply-to-index + `protected_workspace_mutations` refusal; `gate-staged` launch + marker-poll/log-tail progress (co-delivers 5115c47c); FAIL restore path; PASS reckon dialog + commit; + legacy salvage 2 (@codemirror/merge port for the diff pane); scenarios: integrate-pass, integrate-fail-keeps-shard, protected-path refusal |
| W3 spec + polish | S | SPEC-114/147 amendments (Q6 text); Discard-shard action; stale-shard banner (main advanced); docs |

## 5. Risks (honest costs)

- **Disk:** one extra full checkout of tracked content. Bounded, real on small disks.
- **Stale shard:** owner edits an old copy after main advances → Integrate
  stages a regression. Mitigation: shard pins its base sha; Integrate refuses
  when base != main HEAD and offers refresh (dispose-recreate preserves
  nothing — so refuse-then-owner-chooses, never auto).
- **Gate-while-dirty interplay:** Integrate stages onto a main worktree that
  may carry unrelated dirt; `gate_staged` refuses MM rows. The UX must surface
  that refusal legibly, not swallow it.
- **Two-truths confusion:** editor shows shard, terminal shows main. Mitigated
  by reading from the shard everywhere in the Code screen and a visible
  "shard" badge + pending-integration count.
- **Worktree leak on crash:** mitigated by the existing prune-at-next-run
  idiom; the shard module should prune on panel start.
- **pylsp cross-root nav:** go-to-def into main-root absolute paths renders
  "outside workspace" (existing coherent behavior) — acceptable, noted.

## 6. OWNER-DECISIONS — RATIFIED 2026-07-23 (all 8)

1. **Q1 lifecycle: RATIFIED** — single lazy persistent shard, dispose-recreate
   refresh, no rebase.
2. **Q2: full Integrate pipeline WITH auto-commit toggle** — toggle lives in
   the Integrate dialog, remembered across uses, **default OFF** (PASS+reckon
   lights a Commit button; toggling ON makes it a one-click pipeline). Owner
   also asked about gate parallelism: clarified — the gate ALREADY parallelizes
   via its own ephemeral gate-par worktrees from the staged snapshot; the IDE
   shard is the EDIT buffer (1, durable), not the execution shards (N,
   ephemeral). No new parallel machinery needed.
3. **Q3: CONFIRMED via the worker mirror** — edit surfaces re-root to the
   shard (read/save/lint/format/LSP), authoritative gate/tests stay on main at
   Integrate — exactly how workers edit in isolated workspaces while the gate
   runs on main's staged index. Owner's vision NAMES future non-GUI writers in
   the shard (chat increments, agentic autocomplete — "humano segurando o
   volante"), which re-decides Q5.
4. **Q4: gate + reckon baseline + REVIEW-PASS auto-ON for mixed authorship** —
   the shard tracks the writer of each save (GUI vs agent); Integrate turns
   the agentic review-pass on automatically when an agent contributed
   (owner can force/dismiss in the dialog); owner-only shards go straight to
   gate+reckon. Rationale: author ≠ judge is what makes worker review valuable;
   owner-only edits make the owner the judge already.
5. **Q5: OS LOCK FROM DAY 1** (changed from the original rec by the Q3
   ruling): `fs_confine` at shard creation + rule-11 scan at Integrate —
   because non-GUI writers are already in the product vision, the ceiling
   condition is met before launch. Symmetric with SPEC-148 rule 6.
6. **Q6: amendment sentence APPROVED as drafted** (default, no objection).
7. **Q7: gate-in-flight guard RELAXED for shard-only writes** in W1 (default,
   no objection — the edit-during-gate UX win).
8. **Q8: shard lives at `.harness/runs/ide-shard/`** — durable edits must
   survive tempdir cleaners; already deny-listed from the GUI; gate-hold
   already ignores runs/.

Scope deltas vs the original waves: W1 gains fs_confine-at-creation (Q5) and
per-save writer attribution (Q4); W2 gains the review-pass hook + auto-commit
toggle. Sizes hold at M / M / S.
