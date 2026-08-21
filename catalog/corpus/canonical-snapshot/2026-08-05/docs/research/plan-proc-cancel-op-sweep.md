# PLAN RESULT — operator-cancel joins the cage sweep (Fable xhigh, plan author, 2026-07-27)

Pipeline: overseer brief → adversarial critique (codex gpt-5.6-sol, xhigh) → this plan
(Fable 5, xhigh). Inputs on disk: `.harness/handoff/plan-proc-cancel-graded.CRITIQUE-BRIEF.md`
and `.harness/handoff/critique-proc-cancel-graded-SOL.md` (the critique plus the overseer's
verification of its four load-bearing claims).

**Headline for the owner: the confirmation prompt you asked for is NOT in this plan.** The
sparing you wanted is already enforced by the kernel, so the prompt would guard an empty set.
Section 3 says exactly what is and is not delivered. That section is the one to read if you
read nothing else.

---

# OVERSEER VERIFICATION (2026-07-27, before acceptance)

The plan's central mechanism is a new `source: "operator"` field on the cancellation marker,
used to tell an operator cancel apart from internal settlement. That only works if the other
writers do NOT set it and every reader tolerates its absence. Checked in source, not accepted:

- **Internal settlement writer** (`async_runtime.py:714`) writes
  `{"requested": True, "reason": "await policy … satisfied", "requestedAt": …,
  "graceSeconds": 5, "killAfterGrace": True}` — **no `source` key**. CONFIRMED.
- **`workflow start` initializer** (`async_runtime.py:830`) writes `{"requested": False, …}` —
  no `source`, and `requested` is False anyway. CONFIRMED.
- **All three readers** use `.get("requested")` (`:370`, `:578`, `:683`), so an added key is
  additive and backward-safe. CONFIRMED.
- **The cancel CLI** (`cli_workflow_tree.py:99`) exposes `--worker-id`, `--reason`,
  `--grace-seconds` and no `--force`, matching the plan's claim that no surface change is
  needed. CONFIRMED.

The seam is sound. The four claims the critique rested on were verified earlier and are
recorded in the critique file; three of them were corrections to the overseer's own brief and
row notes, and those corrections have been written back to the row.

Not re-derived and taken as given: EXP-21 P1 (verdict `shipped`), and the two commits that
landed today (`ac6ead6`, `0826f4e`).

**Open for the owner, not for the implementer:** whether to accept the verdict that the
"ask first" prompt has no target. Until the owner answers, this plan is DRAFT — the
implementer must not start.

---

# PLAN proc-cancel-graded-destruction: operator-cancel joins the cage sweep; the graded "ask first" layer is NOT built (its target set is empty)

Plan author: Fable 5 (read-only). All `file:line` anchors re-verified against source
2026-07-27 by direct read.

## 0. The central question, answered first: the verdict is ACCEPTED

The critique's verdict holds and I am planning the smaller honest thing (option a). Grounds,
from source, not intuition:

1. **The only destructive primitive a supervised nt cancel can gain is the Job Object sweep,
   and detached children are not in the job.** `popen_detached` sets
   `CREATE_BREAKAWAY_FROM_JOB` (`scripts/harness_lib/processes.py:300-301`),
   `launch_detached` routes through it (`processes.py:315-331`), and `DEFAULT_JOB_LIMITS`
   permits the breakaway (SPEC-163 v4 invariant 12). `terminate_win_job` reaches "EVERY member
   of a Job Object" and nothing else (`processes.py:509-527`). So the sweep spares the detached
   class *by construction* — there is nothing to ask about before firing it. `exp21-8` already
   proves the partition live (`testing/scenarios/exp21_crash_injection.py:398-410`).
2. **On POSIX the question was already answered before anyone asked it.** Cancel's
   `terminate_pid` → `safe_signal_pid` → `signal_pid_group` runs `killpg`
   (`processes.py:261-266`): the worker's whole group dies today, and `start_new_session`
   children (`processes.py:292`) escape it. POSIX cancel has been "kill the caged, spare the
   detached" all along, silently, and the owner has never been harmed by it. The plan's nt
   change is *parity with the POSIX behaviour the owner already lives with*, not new policy.
3. **The prompt's enumeration cannot be built from the proposed data anyway** — CIM answers
   parentage, the sweep kills membership; membership needs the unnamed job's handle, which the
   cancel process does not hold. A prompt whose list is wrong is worse than no prompt.

The narrow exception (breakaway-DENIED child left caged, `processes.py:305-312`; silent under
the venv launcher, `specs/40-features/sandbox-manifest-honesty.md:259-274`) is a contingency,
not an observed population. It is the named re-open trigger, below.

What the owner's policy gets, stated plainly: **"spare the deliberately-detached child" —
delivered, structurally, and pinned by two behaviour checks. "ASK me first" — not delivered as
a prompt, because in every supported path the set of non-trivial things the destruction can
reach is empty; instead the destruction becomes *observable* (a deterministic
`async_cage_swept` event naming the trigger) and the spec states the per-platform blast radius
honestly.** Section 3 is the owner-readable not-built list with triggers.

## 1. What ships

### 1.1 `workflow_cancel` stamps operator intent on the marker — `async_runtime.py:1003`

Add one key to the cancellation dict written at `:1003-1004`:

```python
cancellation = {"requested": True, "source": "operator", "reason": ..., ...}
```

- This is the deterministic seam that closes the bypass: the internal settlement writer
  (`:712-714`) and the `workflow start` initializer (`:830-831`) do **not** carry `source`, so
  a supervisor-side sweep keyed on `source == "operator"` cannot fire on internal settlement.
  All existing readers use `.get(...)` (`:370`, `:578`, `:683`), so the field is additive and
  backward-safe.
- `workflow await --cancel-on-timeout` reaches `workflow_cancel` at `:971` and therefore
  inherits `source: "operator"` — deliberate: an await-timeout cancel is an explicit
  destruction request and gets timeout-equivalent blast radius.
- GUI cancel builds the same CLI (`ui_actions.py:412-413`) → same seam, no GUI-specific branch.
- D050 status: the classification (job membership, kernel-assigned), the decision (marker
  fields), and the trigger are all deterministic code. **No generative component exists
  anywhere in this plan** — there is no prompt, so there is nothing to translate.

### 1.2 The sweep guard widens — `async_runtime.py:497-520` (`_run_async_task`'s `finally`)

Replace `:518-520` with (shape final; comment block at `:500-517` rewritten to match — L1):

```python
op_cancelled = False
if async_job and not timed_out:
    _cancel = workflow_async_cancellation(wfid)
    op_cancelled = (bool(_cancel.get("requested"))
                    and _cancel.get("source") == "operator"
                    and _cancel.get("workerId") in (None, worker_id)
                    and proc.returncode not in (0, None))
cage_trigger = "timeout" if timed_out else ("operator-cancel" if op_cancelled else None)
if cage_trigger and async_job:
    processes.terminate_win_job(async_job)
processes.close_win_handle(async_job)  # (existing line, unchanged)
if cage_trigger and async_job:
    append_async_event(wfid, "async_cage_swept",
                       {"asyncTaskId": async_task_id, "workerId": worker_id, "trigger": cage_trigger})
```

Decisions inside that shape, made not deferred:

- **Inline, no helper function.** Single caller; a helper would be an unrequested abstraction.
- **Guard order `async_job and not timed_out` first**: `async_job` is only ever non-None after
  `proc` exists (`:449`), so `proc.returncode` is never evaluated unbound (spawn-failure and
  assign-failure paths leave `async_job` None).
- **`proc.returncode not in (0, None)`**: mirrors the settle classifier's clean-exit exception
  (`:578`) — a worker that exits 0 during a group cancel is not treated as destroyed, and its
  breakaway-denied caged child survives (invariant 7). Known divergence from `:578`, accepted:
  `:578` also exempts a nonzero-exit worker whose stdout yields an extractable result
  (extraction runs *after* this `finally`, `:544-548`); that worker's cage is swept here
  anyway. Deliberate ceiling — the operator said stop; a salvaged receipt does not un-say it.
  Recorded in the rewritten comment.
- **`workerId in (None, worker_id)`**: a `cancel --worker-id X` never sweeps bystander worker
  Y's cage.
- **Event after `close_win_handle`** so an event-write failure can never leak the job handle.
  The event is observability, not teeth (deliberately unasserted; see 2).
- **The marker is written before any signal** (`:1004`), so by the time `proc.wait()` returns
  the read here is never stale. No re-check machinery needed — the race the critique flagged
  belongs to the prompt design, which is not built.
- **POSIX: zero behaviour change** — `async_job` is None off nt, so `op_cancelled` is never
  computed and no new branch executes.
- The pinned literal `terminate_win_job(async_job` stays contiguous on its own line (hsb-13
  premise pin, `hsb_sandbox_spawn.py:280`).

Blast-radius table this produces (goes into the spec, 1.5):

| path | today | after |
|---|---|---|
| nt, supervisor alive | worker pid only — under the venv launcher the *real* interpreter (a job member behind the launcher stub, spec v4 caveat `:259-274`) likely survives the cancel as an orphan (high-confidence inference; exp21-10 demonstrates the corrected behaviour) | worker pid + its Job Object (caged tree dies); detached children structurally spared |
| nt, supervisor dead (orphaned) | worker pid only | unchanged — no handle, no sweep, stated honestly |
| POSIX | process group via `killpg`; detached (new session) spared | unchanged, byte-identical |

### 1.3 Stub: `sentinel_exit3` learns the caged grandchild — `_exp21_crash_stub.py:176-179`

Clone the env-gated block from `exit0_no_result` (`:127-130`) into `sentinel_exit3`, spawning
the grandchild **before** `_write_sentinel()` (the sentinel-last discipline,
`exp21_crash_injection.py:383-385`), and update the Modes line in the docstring (`:29`). With
`EXP21_GRANDCHILD_PID` unset the mode is byte-identical, so exp21-5 and exp21-6 are untouched.
`MODES` set unchanged; `--self-check` unchanged.

### 1.4 Two new behaviour checks — `exp21_crash_injection.py`, appended after exp21-9, same `try:` body, docstring list extended

**`exp21-10` — operator cancel sweeps the cage and spares the detached child.**
Rig = exp21-8's verbatim (`hang` mode, sentinel + `EXP21_GRANDCHILD_PID` +
`EXP21_DETACHED_GRANDCHILD`), but `workflow start` with a LONG timeout (e.g. `--timeout 600`
so the timeout branch cannot fire), then after the sentinel and both pid files:
`_run("workflow", "cancel", wfid)`. Because `workflow_cancel` settles the task file itself
(`:1029-1036`), `workflow await` returns before the supervisor's `finally` runs — so **poll**
`not pid_alive(caged_pid)` with a ~20s deadline instead of one fixed sleep, then assert.
Assertions, fingerprint first:

- `task.status == "cancelled"` and `run.timeout is not True` and
  `run.returnCode not in (0, None)` (exact code not pinned: 15 on nt via TerminateProcess,
  -15 on POSIX via killpg — OS-mediated),
- `_cancellation(wfid).get("source") == "operator"` (proves the operator marker, not exp21-6's
  bare marker),
- caged grandchild DEAD; detached grandchild ALIVE.

`finally`: `signal_process_tree` both pids unconditionally + `_clear_sentinel_env()` (clone
exp21-8's cleanup `:411-416`). `_breaker_reset()` first.

**Falsifiable:** nt only for the caged-dead arm (on POSIX it passes today via `killpg` and runs
as regression, same framing as exp21-8). Interpreter: falsifiable under BOTH
`.venv\Scripts\python.exe` (the declared gate interpreter) and the system CPython — the rig is
exp21-8's, whose colour split was already verified under both. The detached-alive arm is green
everywhere by design; its teeth are the future (a tree-kill variant reds it).

**`exp21-11` — an internal (settlement-shaped) marker does NOT sweep.**
Rig = `_start_sentinel_run("no-sweep-on-internal-marker", {"EXP21_GRANDCHILD_PID": <temp pid file>})`
(needs 1.3); await sentinel + pid file; write the marker **directly**, in the settlement
writer's exact shape and WITHOUT `source` (clone `:714`'s dict); write the ACK;
`workflow await --mode all-settled`; `time.sleep(1.0)`. Assertions, fingerprint first:

- `task.status == "cancelled"` and `run.returnCode == 3` and `run.timeout is not True` (the
  marker-classification branch at `:578`, not the timeout branch),
- `"source" not in _cancellation(wfid)`,
- caged grandchild ALIVE.

`finally`: kill the survivor, pop the env var, remove the temp dir (clone exp21-9's
`:449-457`).

**Falsifiable:** nt only (the mutant that keys the sweep on marker-present-alone fires
`terminate_win_job` and kills the survivor; off nt `async_job` is None so no mutant of this
guard can act). This is the check that pins the bypass closed.

`EXP21_GRANDCHILD_PID`/`EXP21_DETACHED_GRANDCHILD` are already in `_clear_sentinel_env`'s tuple
(`:165-166`). No new scenario file; `scripts/spec_test_gate.py` untouched.

### 1.5 SPEC-163 v5 section — `specs/40-features/sandbox-manifest-honesty.md`

Appended after v4 in the established shape (incl. the `| Decisão (v5) | Fontes |` table, header
PT, prose EN — the file's existing convention). Contents:

- Invariant 11's condition becomes: `timed_out` **or** operator-cancel (marker `requested` +
  `source == "operator"` + workerId in scope + nonzero exit). Never normal exit (invariant 7;
  exp21-9), never internal settlement (exp21-11).
- Strike-and-replace the v4 cancel paragraph (`:313-316` "the sweep is deliberately NOT wired
  to the cancellation arm") and note the v4 decision-table row "timed_out only, never normal
  exit or cancel" (`:324`) is superseded by v5 — the same in-place-amendment idiom the overseer
  used for the invariant-11 prose fix.
- The blast-radius table from 1.2, per platform, including the orphaned-supervisor row and the
  venv-launcher cancel finding.
- The verdict record: the graded ask layer was evaluated and NOT built; target set empty;
  triggers listed (mirror of section 3).
- **No matrix change, no `DECLARED_KILL_GAPS` change, no `tree_kill_reach` change**: reach
  stays `"job"`/`"session"`; only the *trigger set* widened. hsb-13 is untouched and must stay
  green unmodified.
- One-line amendment to exp21-9's comment (`exp21_crash_injection.py:418`) where it says
  invariant 11 is "`timed_out` ONLY" — now "timeout or operator-cancel; never normal exit".
  History sentences stay.

### 1.6 Row close-out + owner decision request (commit 2)

- Append a close-out note to the `proc-cancel-graded-destruction` row via the tasks CLI (never
  a raw edit of `.harness/state/tasks.json`): verdict accepted, what shipped, what was not
  built and why, pointer to the critique file. The row's earlier "feasibility ANSWERED via CIM"
  note is already struck by the overseer's correction note — the close-out confirms it stands.
- File ONE new backlog row, `proc-cancel-survivor-notice` (P3): "after cancel, report what is
  still running" — the different feature the critique separated out. Body states the
  deterministic sources it would build on (harness-recorded detached pids: gate-run markers,
  supervisor pid file, services state — never CIM tree walks) and that it is **pending an
  explicit owner yes**. Filing the row IS the "ask the owner" step, done through the backlog
  instead of a runtime prompt.

## 2. Falsification ritual (which mutant turns which check red, and where)

Run with try/finally-restore; assert the anchor exists before replacing it. All mutants are in
`async_runtime.py`'s `finally`.

| # | mutant | red check | falsifiable on |
|---|---|---|---|
| M1 | delete the `terminate_win_job(async_job)` call | exp21-8 arm 1, exp21-10, **and** hsb-13 (premise pin `:280`) | nt, both interpreters |
| M2 | drop the `source == "operator"` term (key on `requested` alone) | exp21-11 | nt |
| M3 | the historical widening: sweep on every settle (`or` mutant) | exp21-9 | nt |
| M4 | swap the sweep for `signal_process_tree(proc.pid, ...)` (the taskkill /T trap) | exp21-8 arm 2 and exp21-10 (detached grandchild dies) | nt |

Declared UNPINNED terms, stated instead of hidden:

- `proc.returncode not in (0, None)`: its falsifying scenario (worker exits 0 in the same
  window an operator cancel lands) is inherently racy to rig; no deterministic check ships.
  Trigger to pin it: any measured clean-exit sweep in the wild.
- `workerId in (None, worker_id)`: a deterministic 2-worker bystander rig is possible (cancel
  `--worker-id` A, sentinel worker B with caged child) but costs a concurrency-2 sentinel rig
  for a term with no current caller in anger. Trigger: first real use of `cancel --worker-id`,
  or the bystander mislabeling finding below being promoted to a fix.
- The `async_cage_swept` event: observability only, unasserted by design.

Findings named, not fixed (pre-existing, out of scope; each a candidate row if the owner
cares): (a) `workflow_cancel` writes task status `cancelled` even when `aliveAfterGrace` is
true (`:1021-1036`) — the honest kill result is already in `signalled[]`; (b) a group-level
marker makes ANY later nonzero-exit no-result worker settle `cancelled` even under
`--worker-id` cancel of a different worker (`:578` checks no workerId) — the same class as
exp21-6's measured shadowing.

## 3. What the owner asked for that is NOT built, with re-open triggers

1. **The confirmation prompt ("ask before destroying").** Not built. In every supported path,
   the destruction primitive available to a supervised cancel (job sweep on nt, killpg on
   POSIX) *cannot reach* a deliberately-detached child — the sparing you asked for is enforced
   by the kernel (breakaway / new session), and exp21-8 + exp21-10 arm 2 keep it enforced. A
   prompt would guard an empty set, and its list could not even be computed correctly (job
   membership is invisible cross-process). Triggers to build it: a measured `launch_detached`
   child found inside a worker job at cancel time (the breakaway-denied contingency becoming
   real on a supported interpreter), or the owner classifying some caged child as
   non-trivial/non-recoverable.
2. **`process_children_map` widening / CIM enumeration.** Not built: it answers parentage, the
   sweep kills membership; it would charge every Windows `signal_process_tree` caller
   (`processes.py:159-200`) and contradict esh-6. Trigger: the survivor-notice row being
   approved AND needing tree data the harness's own records cannot supply.
3. **Survivor notification ("cancelled; these are still running").** A different feature, filed
   as `proc-cancel-survivor-notice` pending an owner yes (1.6).
4. **No-TTY refusal, `--force`, approval-staleness re-check.** All exist only to serve the
   prompt; no prompt, none of them. The cancel CLI keeps its exact surface
   (`cli_workflow_tree.py:99`).
5. **Orphaned-supervisor cancel sweep (named jobs / persistent handle owner).** Cancel with a
   dead supervisor stays pid-reach on nt, and now the spec says so. Trigger: the owner requires
   orphan sweep.

## 4. Phasing

**Commit 1 — behaviour + teeth + spec, one revert unit:** 1.1, 1.2, 1.3, 1.4, 1.5. Spec rides
with behaviour (the v4 precedent) so no commit leaves the spec lying. Reverting commit 1
restores `timed_out`-only exactly; exp21-1..9 and hsb-1..14 are green on both sides of it.

**Commit 2 — state + decision record:** 1.6 only. Pure backlog/close-out; independently
revertable with zero behaviour effect. Never written while a gate run is in flight.

## File footprint (HARD boundary)

Commit 1:
- `scripts/harness_lib/async_runtime.py`
- `testing/scenarios/_exp21_crash_stub.py`
- `testing/scenarios/exp21_crash_injection.py`
- `specs/40-features/sandbox-manifest-honesty.md`

Commit 2:
- `.harness/state/tasks.json` (via `harness.py tasks` verbs only)
- `.harness/handoff/result-proc-cancel-op-sweep.md` (result file)

Explicitly NOT touched: `scripts/harness_lib/processes.py` (`terminate_win_job` already ships
the needed contract, `:509-527`), `scripts/harness_lib/sandbox_spawn.py` (no declaration
moves), `testing/scenarios/hsb_sandbox_spawn.py` (pins stay true unmodified),
`scripts/spec_test_gate.py` (frozen), `scripts/harness_lib/cli_workflow_tree.py`,
`scripts/harness_lib/ui_actions.py`, the EXP-21 experiment record, anything else under
`.harness/`.

## Constraints & verification

- venv python only; stdlib only; EN-only in code/comments/spec prose (the `Decisão` table
  header stays PT per file convention); UTF-8 no BOM; never rewrite whole files; no PowerShell
  Get/Set-Content on source.
- Commands, from repo root, `HARNESS_QUIET=1` (never `HARNESS_AGENT_OUTPUT=compact` around
  scenarios):

```
$env:HARNESS_QUIET='1'
python testing/scenarios/exp21_crash_injection.py      # exp21-1..11 green
python testing/scenarios/hsb_sandbox_spawn.py          # hsb-1..14 green, byte-untouched file
python testing/scenarios/_exp21_crash_stub.py --self-check
python scripts/harness_lib/sandbox_spawn.py            # self-check: gap set still {}
```

- **Interpreter discipline (spec v4 caveat, `:259-274`):** run `exp21_crash_injection.py` under
  BOTH `.venv\Scripts\python.exe` and the system CPython and report both colours per check; a
  colour that differs between interpreters is the defect, not the environment.
- The falsification table in section 2 is part of the deliverable: the result file SHOWS each
  mutant red/green/restored, it does not assert it.
- No `gate-staged`, `validate`, `oracle mutate`, or `verify-status` from the implementer —
  overseer-owned.
- Result path: `.harness/handoff/result-proc-cancel-op-sweep.md` — what shipped per numbered
  clause, mutation table, `planDeviations` (typed, max 10, empty stated), commands + verdicts,
  confirmation the NOT-touched list is untouched.

## Landmines pre-listed

- **L1** `:500-517` comment rewrite: keep `terminate_win_job(async_job` contiguous on one line
  (hsb-13 pin `:280`); never repeat the call text in a comment; do not touch the ladder
  (`safe_signal_pid(proc.pid, signal.SIGTERM)` pin `:268`) or the spawn kwargs (esh-3 pin,
  `esh_spawn_hygiene.py:83`).
- **L2** The comment's current sentence "never on cancellation, whose policy is the still-open
  `proc-cancel-graded-destruction` row" (`:513-514`) must be replaced, not left beside the new
  guard — a comment contradicting the code is how stale premises survive.
- **L3** exp21-10 must NOT synchronize on `workflow await` alone — `workflow_cancel` settles the
  task file cross-process before the supervisor's `finally` runs; poll the caged pid.
- **L4** Stub grandchild before sentinel (sentinel-last discipline); env-gated so exp21-5/6 stay
  byte-identical.
- **L5** `_breaker_reset()` before every new rig (three failures open the circuit,
  `exp21_crash_injection.py:110-122`); every wfid into `wfids` for scrub; leaked 600s sleepers
  killed unconditionally in `finally`.
- **L6** Assert on the pid the stub WROTE, never a rediscovered pid; a venv-launcher respawn
  surviving is a finding to report, not a number to adjust.
- **L7** Do not add hsb-13 premises or touch `DECLARED_KILL_GAPS`: behaviour teeth belong in
  exp21 checks (v4 decision `:328`); strengthening hsb-13 is the rejected move.
- **L8** exp21-6 writes a bare marker on purpose — it must keep settling terminally and must
  never sweep; if exp21-6 changes colour, the guard is wrong.

## Measurements named (none block pricing)

1. Both-interpreter colour run of exp21-10/11 (verification step).
2. The venv-launcher cancel-orphan claim (worker's real interpreter survives today's nt cancel)
   is high-confidence inference from the measured v4 caveat; running exp21-10 once against
   HEAD~ (pre-change) would convert it to a measured fact — optional, one command, worth doing
   for the result file.
3. The 2-worker bystander rig — priced only if its trigger (section 2) fires.
