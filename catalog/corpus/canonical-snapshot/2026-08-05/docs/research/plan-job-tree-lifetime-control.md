# PLAN RESULT — nt job-tree lifetime CONTROL (Fable xhigh, plan-author + critic, 2026-07-27)

Brief: `.harness/handoff/plan-job-tree-lifetime-control.md`. Read-only run; no
files written by the author, no git commands. Overseer verification of the three
load-bearing claims is appended at the end — read it before implementing.

## 1. Verdict on the brief and the source plan

**Direction right; the centrepiece premise is TRUE but the conclusion drawn from
it is wrong, and the drift-lock claim is overstated for this transition.**

**1a. Q1 premise VERIFIED TRUE, then MOOT.** `assign_job_to_pid` creates the job
at `processes.py:449` as `k32.CreateJobObjectW(None, None)` — second argument is
`lpName`, so the job is **unnamed**. No `OpenJobObject` path; the cancel CLI
genuinely cannot reach it. **But the draft assumes the CLI must be the killer.**
The handle owner — the supervisor coroutine `_run_async_task` — is parked in
`await proc.wait()` (`async_runtime.py:482`) and regains control the instant the
CLI's pid-kill fells the worker, with `async_job` still open (the `finally` at
`:497-500` closes it only after). A cage sweep there reaches the job with zero
cross-process machinery. The draft's `signal_process_tree` swap (its 5.3) is
strictly worse:

- **It changes POSIX behavior.** `signal_process_tree` adds the descendant walk on
  linux, newly killing setsid-escapees and `launch_detached` children on operator
  cancel — while the draft's own disparity row 7 admits this and its 5.3 claims
  "POSIX semantics preserved". Internal contradiction, and it violates the brief's
  POSIX-zero-change constraint.
- **It recreates the stranded-gate-hold incident class.** Post-breakaway a detached
  gate runner is still in the VISIBLE tree (breakaway changes job membership, not
  parentage), so `taskkill /T` at cancel kills it mid-gate. The job sweep spares
  breakaway children by construction.
- **It presents an unratified policy as settled.** SPEC-163 v2 says verbatim that
  the operator-cancel seam is NOT declared there and its policy is a separate open
  decision; the draft's section 2 hardcodes cancel-aggressive.

Cost had the premise been wrong: none — the sweep never needed cross-process
access. Named jobs stay the B4 precision path for the genuinely unreachable case
(cancelling an ORPHANED task whose supervisor is dead).

**1b. The brief's hsb-13 claim is overstated.** It holds for the function↔dict
pair (`tree_kill_reach` vs `DECLARED_KILL_GAPS`, both hand-maintained
declarations). The function↔BEHAVIOR link is held by string premise pins, and the
pinned `safe_signal_pid(proc.pid, signal.SIGTERM)` SURVIVES this change, because
the pid ladder stays as the POSIX/fallback path. So the declaration side can move
without the behavior side and stay green. Testing-playbook failure mode 2 on
schedule. The plan therefore treats hsb-13 as the DECLARATION-CONSISTENCY lock
only, and puts the behavior teeth in a new end-to-end check (exp21-8) plus one new
premise pin on the sweep call, all in the same commit.

**1c. Q2 — the coupling is real, but "same commit" is the wrong shape.** Real: the
async worker is already caged (`async_runtime.py:449`), job membership inherits,
and today's pid-only kill is the only reason a caged worker's `launch_detached`
child (gate runner, nested supervisor) survives the timeout. The moment any kill is
job-scoped, those children die with the task — a D045 regression below POSIX and a
live incident class. But bundling breakaway into the kill commit means a breakaway
defect rolls back the ratified control. **Breakaway lands FIRST, as its own
commit**: independently correct (the flag is a no-op outside a job, and nothing
job-kills yet), independently checkable, independently revertable.

**1d. Q3 — answered from the code, stronger than the draft.** On nt the
"job-assign-failed" corner at the timeout kill is UNREACHABLE:
`assign_job_to_pid` with `DEFAULT_JOB_LIMITS` (always non-None) RAISES on failure,
and the except arm at `:451-465` kills the suspended child and RETURNS — the task
settles rejected before the timeout branch can exist. At the timeout branch on nt,
`async_job` is always live. The fallback ladder exists for POSIX and for
`TerminateJobObject` itself failing. No double-kill (`TerminateJobObject` on dead
members is a no-op; `os.kill` on a dead pid is swallowed in `signal_pid_group`), no
hang (every wait is `asyncio.wait_for`-bounded; the give-up branch is preserved,
and the sweep improves it).

**1e. Q4 — confirmed at the classification site.** The verdict keys on flags, not
rc: cancellation at `:557-561`, timeout at `:562-565` (`elif timed_out:`). The
primary kill stays the unchanged ladder (`TerminateProcess(pid, 15)` via `os.kill`
on nt — precisely why P1 measured `returnCode 15`), so rc forensics are
byte-identical; `terminate_win_job` passes 15 anyway for the wedge case.

**1f. Staleness in the source plan** beyond the given line drift: its section 4 /
Phase D already landed (20e098d); its B1 darwin `ps` walk already SHIPPED and
`bounded:darwin` is struck; its B2 step-1 detector shipped; its "invariant 8"
numbering collides with v2's 8-10. Its rejections (KILL_ON_JOB_CLOSE, per-profile
field, SILENT_BREAKAWAY_OK, stub-as-decider) all stand and are carried forward.

## 2. Target design — the contract

> **On nt, a task-kill decision kills the task's cage.** The cage is the Job Object
> the async seam already assigns, held as `async_job`. The primary kill remains
> today's pid ladder (rc forensics unchanged); before the handle owner releases the
> handle it SWEEPS the cage with `TerminateJobObject` whenever a kill decision was
> taken. The one exit is the detached primitive — `CREATE_BREAKAWAY_FROM_JOB`, the
> nt twin of `setsid` — which is harness code, never a per-child judgment, and
> FAILS CLOSED: a denied breakaway retries without the flag, leaving the child
> caged-but-killable with one log line. POSIX ships zero behavior change. The
> declaration (`treeKillReach` async:nt `pid → job`, `DECLARED_KILL_GAPS` emptied)
> moves in the same commit as the sweep, locked by hsb-13 + a new premise pin + a
> behavioral check that is red today on nt.

Testable clauses:

1. `processes.terminate_win_job(handle, exit_code=15) -> bool` exists, mirrors
   `close_win_handle` (no-op False off nt / falsy handle).
2. In `_run_async_task`'s `finally`, before `close_win_handle`:
   `if timed_out and async_job: processes.terminate_win_job(async_job)`. The ladder
   at `:488-496` is untouched. (Phase 3 widens the condition to cancellation.)
3. All detached spawns route through one shared primitive
   (`processes.popen_detached`) carrying `process_group_kwargs()` + (nt)
   `CREATE_BREAKAWAY_FROM_JOB` (0x01000000) with a WinError-5 retry-without-flag and
   one stderr log line. `launch_detached` delegates; the supervisor `Popen` at
   `async_runtime.py:900` is replaced by it. `process_group_kwargs()` itself is
   UNTOUCHED — worker spawns must never break out of a foreign cage.
4. `DEFAULT_JOB_LIMITS` gains `"breakawayOk": True`; `_win_job_set_limits` maps it
   to `JOB_OBJECT_LIMIT_BREAKAWAY_OK` (0x800). `SILENT_BREAKAWAY_OK` never appears.
5. After Phase 2, `tree_kill_reach("async")` returns `"job"` on nt
   (`== tree_kill_target`), `DECLARED_KILL_GAPS` is `{}`, and hsb-13's expectations
   and premise pins are updated in the same commit.
6. The sweep fires only on a kill decision — NEVER on normal exit: a
   breakaway-denied caged gate runner must survive its parent's clean exit (the
   recover sweep owns that frontier, SPEC-163 invariant 7).

## 3. Phased plan

Every phase: nt-gated behavior, POSIX zero change, no new scenario file (both
checks live in existing glob-discovered files — **zero lines added to
`scripts/spec_test_gate.py`; gs-7 stays 1659/1660**). Verification, fresh shell:

```
export HARNESS_QUIET=1 HARNESS_AGENT_OUTPUT=compact
python testing/scenarios/hsb_sandbox_spawn.py
python testing/scenarios/exp21_crash_injection.py
python scripts/harness.py gate-staged        # detached; poll harness.py verify-status
```

### Phase 1 — breakaway (one commit, lands first)

Files: `processes.py`, `sandbox_spawn.py` (one dict line), `async_runtime.py`
(supervisor call-site swap), `hsb_sandbox_spawn.py`.

- `processes.popen_detached(cmd, *, stdin, stdout, stderr, cwd, env)` (~14 lines):
  group kwargs + breakaway flag on nt; `except OSError` with `winerror == 5` → one
  stderr line (`"breakaway denied; child stays in the parent job
  (caged-but-killable)"`) → retry without the flag. `launch_detached` delegates;
  the supervisor spawn calls it.
- `_win_job_set_limits`: `breakawayOk` → `flags |= 0x800`. `DEFAULT_JOB_LIMITS`
  gains `"breakawayOk": True`.

**The ONE falsifiable check — `hsb-14`** (new section in `hsb_sandbox_spawn.py`),
two arms, nt-gated with an honest off-nt skip comment ("breakaway is a Job Object
concept; falsifiable on nt only"):

- Arm A (escape): spawn a helper child, cage it via the REAL
  `processes.assign_job_to_pid(pid, sbx.DEFAULT_JOB_LIMITS)`; the helper calls the
  REAL `processes.launch_detached` for a sleeper grandchild; assert
  `IsProcessInJob(grandchild, job)` is FALSE (ctypes, hermetic; reap both in
  `finally`). **RED today** (no flag → grandchild inherits the job), GREEN after.
- Arm B (fail-closed): same shape but the cage gets limits WITHOUT `breakawayOk`;
  assert the grandchild IS in the job AND the helper's stderr carries the retry
  line. **RED today** (no retry line exists), GREEN after.
- **Call site exercised:** `launch_detached → popen_detached`, the single shared
  wiring all three production callers route through. The supervisor call site is
  additionally exercised LIVE by the existing `exp21-5`, which spawns the real
  detached supervisor through `workflow start` — a broken swap at `:900` turns
  exp21-5 red. Deleting the call-site change, not just the callee, goes red.

Acceptance: hsb-14 red→green on nt; hsb-1..13 and exp21-1..7 untouched and green;
gate green. Rollback: revert the commit. Declaration: no hsb-13 movement —
breakaway changes no kill reach.

### Phase 2 — the cage sweep + the declaration flip (one commit; the ratified control)

Files: `processes.py`, `async_runtime.py`, `sandbox_spawn.py`,
`hsb_sandbox_spawn.py`, `exp21_crash_injection.py` (+ `_exp21_crash_stub.py`
hang-mode extension, env-gated so exp21-1..7 see no change),
`specs/40-features/sandbox-manifest-honesty.md` (v4).

- `processes.terminate_win_job` per clause 1 (~9 lines, beside `close_win_handle`).
- `async_runtime.py` `finally` (`:497-500`): the 2-line sweep per clause 2,
  commented with the P1 numbers and the reason it runs on the handle only this
  coroutine holds. It also fixes the give-up wedge at `:496`: a worker surviving the
  whole ladder is now swept with its tree.
- `sandbox_spawn.py`: `tree_kill_reach("async")` → `"job" if _kill_platform() ==
  "nt" else "session"`; strike `DECLARED_KILL_GAPS["async:nt"]` leaving the comment
  trail like the `bounded:darwin` strike; update the two stale docstrings.
- `hsb_sandbox_spawn.py` hsb-13, same commit: async expectations flip to
  `reach == target == "job"` on nt; **add the premise pin**
  `"terminate_win_job(async_job" in async_src` — the pin that makes 1b's
  green-on-a-lie impossible, since deleting the sweep line reds hsb-13; keep the
  `safe_signal_pid` pin (the ladder legitimately remains).

**The ONE falsifiable check — `exp21-8`** (new section, existing file): stub `hang`
mode through the REAL async seam — `workflow start --timeout 8`, sentinel +
`EXP21_GRANDCHILD_PID` awaited (env passes via the stub executor's
`envKeepList: ["EXP21_*"]`), then `workflow await`. Assertions:

- Branch fingerprint first (P1's own discipline): task status `"timeout"`,
  `run.timeout is True` — proving the TIMEOUT branch fired, not cancellation.
- Arm 1: caged grandchild DEAD post-settle. **RED today on nt** (measured 5,5,5 /
  3,3,3 survivors), GREEN after, re-reds on revert of the sweep line. Comment:
  falsifiable on nt only; POSIX passes today via killpg and runs as regression.
- Arm 2: a second, `EXP21_DETACHED_GRANDCHILD`-gated grandchild spawned by the stub
  via the REAL `processes.launch_detached` is ALIVE post-settle (reaped in
  `finally`). Green on all OSes today and after; its teeth are the future — it reds
  if anyone ships `KILL_ON_JOB_CLOSE` or a blanket tree-kill.
- **Call site exercised:** the real `_run_async_task` timeout branch + `finally`
  sweep, reached through the real supervisor — not a library call. Deleting the
  sweep CALL (not the function) is exactly what arm 1 detects.

Mutation ritual before claiming done: temp-mutate the sweep line out, run exp21-8,
confirm RED, restore, confirm GREEN.

**Declaration/code movement:** together, in this one commit, and safe because every
partial combination is red — sweep without function flip → hsb-13 red (async
manifest still expects `"pid"`); function flip without strike → hsb-13 red
(live_gaps ≠ declared); flip+strike without sweep → hsb-13 red on the new premise
pin AND exp21-8 red. No green window contains a lie.

Acceptance: exp21-8 arm 1 red→green on nt, arm 2 green; hsb-13 green with
`DECLARED_KILL_GAPS == {}`; exp21-1..7 byte-untouched; POSIX suite green (CI legs).
Rollback: revert — code and declaration revert atomically.

### Phase 3 — cancel converges on the cage (one commit, OWNER-GATED, after decision 5.1)

Files: `async_runtime.py`, `exp21_crash_injection.py`,
`specs/40-features/sandbox-manifest-honesty.md` (v4 addendum or v5).

- Widen the sweep condition:
  `if (timed_out or workflow_async_cancellation(wfid).get("requested")) and async_job:`
  (~1 line; the cancellation file is written at `:981` BEFORE the pid-kills at
  `:1005`, so no race). `workflow_cancel` itself — `:987`/`:994` — is UNTOUCHED: no
  `signal_process_tree` swap, no POSIX delta, Q1's cross-process problem never
  arises.
- **The ONE falsifiable check — `exp21-9`:** hang run, sentinel, real
  `workflow cancel <wfid>`, assert task `"cancelled"` (fingerprint — the exp21-6
  shadowing caution applies) and caged grandchild dead on nt. **RED under Phase-2
  code** (cancel → pid-kill → `timed_out` False → no sweep → grandchild survives),
  GREEN after. Comment: nt-only falsifiability. **Call site exercised:** the real
  cancel CLI → `terminate_pid` → supervisor `finally` sweep, the full cross-process
  wiring.
- Declared ceiling in the amendment: cancel of an ORPHANED task (supervisor dead,
  nobody holds the handle) stays pid-reach on nt; B4 (named jobs) is its
  trigger-gated upgrade path.

Rollback: revert; Phase 2 remains whole.

## 4. What I would NOT build

- **The draft's 5.3 `signal_process_tree` cancel swap** — superseded by the sweep.
  Change of mind: an incident requiring cancel to kill an ORPHANED task's tree
  cross-process → that is B4 (named jobs `Local\harness-<wfid>-<task>` +
  `OpenJobObject`), not taskkill /T.
- **The draft's 5.2 TerminateJobObject-as-the-kill** — buys ~0-2s of earlier child
  death over ladder+sweep, costs touching the ladder and the rc-forensics reasoning.
  Change of mind: a measured wedge where `TerminateProcess` fails to fell the vendor
  CLI within the 5s ladder (which the sweep already covers).
- **A supervisor cancellation-poll loop** — the CLI's pid-kill already wakes the
  handle owner.
- **`KILL_ON_JOB_CLOSE`**, **`SILENT_BREAKAWAY_OK`**, **a per-profile lifetime
  field**, **psutil/Toolhelp32** — ratified rejections, carried forward. The first
  two invert recover-salvage and manifest honesty respectively.
- **Any POSIX-side change** — B2 already has its shipped detector awaiting the CI
  leg; B3 stays trigger-gated on a measured setsid-escapee orphan.
- **Re-probing cancel-branch incidence before Phase 3** — the mechanism is identical
  to the measured timeout branch (pid-kill of a caged parent); a second 26-arm
  campaign to re-measure the same mechanism is measurement theater. Change of mind:
  the owner declines decision 5.1's a-fortiori reasoning.

## 5. Open owner decisions (recommendation first)

1. **Cancel converges on the cage (Phase 3) without a new probe — YES.** The kill
   mechanism at cancel is byte-identical to the measured timeout branch; only the
   trigger differs, so P1's incidence carries a fortiori (referência: judgment on the
   carry-over; the mechanism identity is source-verified). The alternative — the
   draft's aggressive visible-tree cancel — changes POSIX, kills breakaway gate
   runners, and was never ratified. Deciding NO leaves Phase 2 complete and honest.
2. **Breakaway-first commit ordering — YES.** If the owner insists on one commit the
   content is identical; only rollback granularity is lost.
3. **Cancel spares breakaway children — YES, declared.** This INVERTS the draft's
   "operator kill outranks background children" for exactly one class:
   harness-detached children (gate runners, nested supervisors). An operator wanting
   scorched earth has `taskkill /PID <pid> /T` at the shell; the harness's own cancel
   should not strand gate-holds.
4. **exp21-8 arm 2 rides Phase 2, not Phase 1 — YES**: before Phase 2 nothing
   job-kills, so "detached survives" is vacuously green everywhere.

## 6. Amendment target (SPEC-116 door)

**Versioned amendment to a covered spec — `specs/40-features/sandbox-manifest-honesty.md`
(SPEC-163), as v4.** No new intake: third exercise of the shelf v2 built (v2 declared
the gap, v3 closed `bounded:darwin`, v4 closes `async:nt`). Contents: two new
invariants — **11** (nt timeout kill sweeps the cage via the held handle before
release; POSIX killpg unchanged; give-up wedge covered) and **12** (detached spawns
break away on nt: `breakawayOk` + `CREATE_BREAKAWAY_FROM_JOB`, fail-closed retry,
`SILENT_BREAKAWAY_OK` rejected) — numbered 11/12 because v2 consumed 8-10 (the source
plan's "invariant 8" is stale); matrix row async:nt `pid → job` citing EXP-21 P1;
the `DECLARED_KILL_GAPS` strike; the cancel paragraph updated from "separate open
decision" to either the Phase-3 convergence or a one-line pointer to it as still-open.
`specs/40-features/harness-own-sandbox.md` (SPEC-151) expected untouched — verify at
amendment time. EXP-21 `measurements[]` and verdict are owner-gated ledger writes, not
spec content; DECISIONS.md needs nothing (this implements D045).

---

# OVERSEER VERIFICATION (2026-07-27, before acceptance)

Three load-bearing claims were checked against source rather than accepted.

**Q1 premise — CONFIRMED.** `processes.py:449` reads
`job = k32.CreateJobObjectW(None, None)`. The second argument IS `lpName`, so the
job is unnamed and has no `OpenJobObject` path. The author's conclusion — sweep
from the handle owner instead of cross-process — is a materially better design
than the source plan's taskkill swap, and it is the reason the POSIX-zero-change
constraint survives.

**Q3 — CONFIRMED.** The job-assign failure arm ends with `return task`
(`async_runtime.py:465`), so on nt the timeout branch cannot be reached with a
None handle. The design's `and async_job` guard makes this moot either way, which
is the right belt-and-braces.

**1b (hsb-13 overstated) — SUBSTANCE CORRECT, EXAMPLE IMPRECISE. Read this before
implementing.** The author writes that flipping `tree_kill_reach("async")` to
`"job"` and striking the gap "leaves hsb-13 fully green". That specific step does
NOT stay green: `hsb_sandbox_spawn.py:271-272` hardcodes
`async_man.get("treeKillReach") == ("pid" if os.name == "nt" else "session")`, so
the flip alone turns hsb-13 RED.

The underlying criticism nevertheless STANDS, and it is a criticism of the
overseer's own morning commit (20e098d). Once the implementer updates that
hardcoded expectation — which the same commit requires — nothing remaining pins
the kill BEHAVIOR: the surviving premise pin is
`"safe_signal_pid(proc.pid, signal.SIGTERM)" in async_src`, which is still true
after the sweep lands, because the ladder legitimately stays. So hsb-13 locks
declarations against declarations and against string premises, never against
behavior. The comment above it calling it a "declaration/code drift lock"
OVERCLAIMS, in exactly the way the testing playbook warns about.

The author's remedy is accepted as-is: hsb-13 keeps the declaration-consistency
job, gains the `terminate_win_job(async_job` premise pin, and the behavior teeth
live in exp21-8, which reaches the real seam. Implementers must not treat hsb-13
green as evidence that a kill behaves as declared.

# OWNER DECISIONS (2026-07-27) — READ BEFORE IMPLEMENTING PHASE 3

**Phases 1 and 2 are ACCEPTED as written.** Decisions 2 and 4 (breakaway-first
ordering; exp21-8 arm 2 rides Phase 2) are taken as recommended.

**Decision 1 is OVERRIDDEN. Phase 3 as designed is only its lower half.** Asked
in plain terms what "cancel" should mean for processes the harness deliberately
detached — the live example being a gate started four minutes ago — the owner
chose **"spare it, but ASK me first"**, over both silent-spare (the plan's
recommendation) and kill-everything (the source draft's policy).

So the cage sweep at cancel is still wanted; what the plan omits is the layer
above it. That layer is the existing row `proc-cancel-graded-destruction`, whose
feasibility blocker is now ANSWERED — see that row's note. Summary: two questions
were fused in the blocker. REACHING the unnamed job cross-process is genuinely
impossible (and unnecessary, per section 1a). ENUMERATING what would die is a
different question, and `Get-CimInstance Win32_Process` answers it — demonstrated
at scale by today's P1 probe rig, which built the full cross-process pid/ppid/cmd
map every 3 seconds for an hour. The proposed shape is to evolve
`process_children_map` UP on nt (D045, the same move that gave darwin its `ps`
fallback) rather than special-case the cancel path.

D050 binds how that layer is built: the class of each child, the decision to ask,
the refusal without a tty, and the enumeration are DETERMINISTIC CODE. A
generative agent may only TRANSLATE the list into human language, and the
translation never alters the classification.

**Phase 3 must therefore be re-planned before implementation.** Phases 1 and 2
are unaffected and may proceed.
