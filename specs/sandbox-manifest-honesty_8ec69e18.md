# SPEC-163 — Sandbox manifest honesty + Job-Object containment across all spawn seams

Status: SPEC-163, proposed 2026-07-21 (acceptance: `testing/scenarios/hsb_sandbox_spawn.py`
+ `hos_harness_sandbox.py` extensions). Origin: /security-review SECREV-2026-07-21
findings H1+M2, owner-ratified D043. relates-to: SPEC-151 (harness sandbox), SPEC-148
(bounded spawn / Job Objects).

## Goal

Close the two ratified security findings, in two phases (measure-then-control, the
repo's own discipline):

- **M2 (Phase 1 — honesty).** The recorded `sandboxManifest` conflates "the host CAN
  enforce this" (`procEnforced`/`fsEnforced`/`egressEnforced` = host capability) with
  "THIS spawn actually applied it". A worker records `procEnforced:true` even when no
  Job Object was assigned to it. Phase 1 adds the per-spawn APPLICATION fact
  (`procApplied`, and surfaces `fsApplied`) so the overseer auditing a receipt can tell
  a genuinely-confined spawn from an unconfined one. NO behavior change — only the
  manifest stops overstating.
- **H1 (Phase 2 — control).** With the gap now visible/measured, route the async and
  detached spawn seams through Job-Object assignment so `procApplied` becomes true for
  all three vendor classes (today only the bounded seam assigns a Job Object). Phase 2
  is a separate batch, gated on Phase 1 landing.

## Applicability

`scripts/harness_lib/sandbox_spawn.py` (the receipt + manifest), `processes.py`
(`run_process_tree_bounded` reports whether a Job Object was assigned), and the three
seams that stamp `sandboxManifest`: bounded (`harness.py:1599` run_one_worker), async
(`async_runtime.py:440`), detached route (`harness.py:2372`). Phase 2 also touches the
async/detached spawn primitives. Phase 1 is ADDITIVE (new manifest keys, honest
defaults); no existing consumer breaks.

## Requirements / invariants (numbered, testable)

### Phase 1 (M2 — this spec's first batch)
1. **Per-spawn application fact.** The receipt carries `procApplied: bool` (default
   FALSE — application is a fact CONFIRMED after the spawn, not a host capability), and
   `MANIFEST_KEYS` includes `procApplied` and `fsApplied` so both surface in the
   projected manifest. `procEnforced`/`fsEnforced`/`egressEnforced` keep their meaning:
   host CAPABILITY (enforceable), not per-spawn application.
2. **Bounded seam confirms application.** `run_process_tree_bounded` reports whether a
   Job Object was actually assigned (a `proc_applied`/`jobApplied` attribute on the
   returned CompletedProcess, additive like `cpu_seconds`; true iff `_win_job_assign`
   returned a job). The bounded seam sets `receipt["procApplied"]` from that fact.
3. **Async/detached seams tell the truth.** Until Phase 2, the async and detached seams
   do NOT assign a Job Object, so their `procApplied` stays FALSE — the manifest now
   states the real gap instead of `procEnforced:true` masking it.
4. **Honesty invariant (the teeth).** For every seam, a recorded manifest with
   `procApplied:true` MUST correspond to an actually-assigned Job Object; a spawn with
   no Job Object MUST record `procApplied:false`. `fsApplied` non-empty iff fs-confine
   ACEs were applied (R0 read workers keep `fsApplied:[]`).
5. **Additive.** No existing manifest consumer breaks; break-glass
   (`sandboxBypassed:true`) still forces every `*Applied`/`*Enforced` false.

### Phase 2 (H1 — follow-up batch, gated on Phase 1)
6. **Job Object on all seams.** The async (`create_subprocess_exec`) and detached
   (`launch_detached`) seams assign a Job Object (or the platform's equivalent tree cap)
   so `procApplied` becomes true for all three vendor classes; the fork-bomb / memory
   cap and job-scoped kill apply to the async fan-out, not just the bounded seam.
7. **No orphan on normal exit** *(amended v2 — the mechanism named here was wrong)*.
   A detached worker that outlives its parent's normal (non-timeout) exit is reaped
   by the **recover sweep**. `KILL_ON_JOB_CLOSE` is REJECTED as the mechanism, here
   and on every seam: it couples worker lifetime to HANDLE lifetime, so a supervisor
   crash would close its handles and kill every in-flight worker — destroying exactly
   the work `workflow_async_recover` exists to salvage. (This composes with EXP-21's
   crash-recovery teeth.)

## Rationale & sources

| Decisão | Fontes |
|---|---|
| M2 before H1 (honest manifest first, then close the gap) | measure-before-control (SPEC-159/EXP-18); a visible/measured gap de-risks the behavior change |
| `procApplied` distinct from `procEnforced` | SECREV M2: the manifest must not claim host-capability as per-spawn enforcement (SB-3's own "a False MUST NOT be claimed as enforced", inverted for True) |
| Route async/detached through job-assign | SECREV H1 owner-ratified; invariant 1 ("all three vendor classes") is unmet on 2 of 3 seams today |

## Ceilings (upgrade paths)

- Phase 1 does NOT change confinement — it only stops the manifest lying. The async
  fan-out stays uncapped until Phase 2; that is now DECLARED and MEASURED, not hidden.
- Non-Windows hosts have no Job Object; `procEnforced` is already false there, so
  `procApplied` is false too — honest on every platform.

## Test strategy

- `hsb`/`hos`: a bounded spawn records `procApplied:true` AND the Job Object memory cap
  actually fires (existing hos-6/hsb-6 prove the cap; add the manifest-honesty
  assertion); an async/detached receipt records `procApplied:false` (Phase 1); the
  `fsApplied` surfaces in the manifest; break-glass forces all false.
- Phase 2 acceptance: async/detached spawn assigns a job (memory cap fires on those
  seams too); added when Phase 2 lands.

## Validation

- `python testing/scenarios/hsb_sandbox_spawn.py` green.
- `python testing/scenarios/hos_harness_sandbox.py` green.
- `python scripts/harness_lib/sandbox_spawn.py` self-check green.
- `spec-pack` green.

## Amendments

### v2 (2026-07-27) — M4: the manifest declares kill REACH, and the objective beside it

The manifest answered "was this spawn confined?" but never "**if we kill this task,
who dies?**". Measured live on this nt machine (parent → child → grandchild, child in
a Job Object): after `TerminateProcess` on the child the **grandchild survived**;
after closing the job handle it died. The async timeout seam does exactly the former
(`safe_signal_pid` → `signal_pid_group`, whose `os.name != "nt"` guard skips the
killpg) **while holding that worker's job handle in scope, unused**
(`async_runtime.py`). POSIX has shipped the right semantics for months
(`process_group_kwargs()` → `start_new_session=True`, reaped by `killpg`), so this is
not a Windows feature to invent — it is Windows catching up, and until it does the
manifest must say so out loud.

Owner direction (2026-07-27): *"parar de mentir primeiro, mas declarando nosso
objetivo final, depois a gente ajusta quando chegarmos lá e também conforme formos
evoluindo."* So the declaration carries **two** values, not one.

8. **Reach is declared per seam, per host.** `sandbox_prepare(..., mode=...)` stamps
   `treeKillReach` — what a kill decision for that seam would actually HIT here —
   from the closed vocabulary `none | pid | session | job | tree` (`TREE_KILL_REACH`).
   It is a pure function of the primitive each seam issues, not a capability probe and
   not a promise. Omitting `mode` omits the keys: **no claim beats a wrong claim.**
   Break-glass does not alter it (the kill primitive is unchanged by it).
9. **The objective is declared beside the fact.** `treeKillTarget` states where the
   seam is going: bounded → `tree` on every OS; async → the task's **cage** (`job` on
   nt, `session` on POSIX — the cage is what inheritance fills, so reaching it needs
   no per-child bookkeeping and no per-profile field); detached → `none` **by design**,
   since outliving its launcher is its purpose.
10. **Every divergence is a declared gap, and the set is exact.** `DECLARED_KILL_GAPS`
    maps each `mode:platform` where reach ≠ target to the row that closes it. `hsb-13`
    asserts this set is EXACTLY the live divergence on the running platform, so a new
    undeclared gap goes red and a gap closed without striking its entry goes red. It
    additionally pins the **source premises** the matrix is derived from, so a kill-site
    change cannot land without updating the declaration in the same commit.

**ONE vocabulary for this axis** (owner decision, 2026-07-27). D045 rule 3 names
SPEC-113's `supportState` (`native/emulated/degraded/unsupported`) as the declaration
vocabulary for vendor/OS gaps, and reach is a strictly richer fact than a support
tier — `degraded` cannot say whether a kill hits the pid, the session or the tree.
So this axis declares **reach, and only reach**: no parallel `supportState` field is
minted alongside `treeKillReach`, because two vocabularies for one dimension is the
drift D045 is guarding against. A consumer that needs a tier derives it
(`tree`/`job` → native; `session`/`pid` → degraded; `none` → n/a); the reach value
stays the single source of truth.

Matrix at v2 landing time — today's truth, with the objective beside it:

| seam | nt | linux | darwin | objective |
|---|---|---|---|---|
| bounded | `tree` | `tree` | **`session`** (gap: no `/proc`) | `tree` |
| async | **`pid`** (gap: the defect above) | `session` | `session` | cage (`job` / `session`) |
| detached | `none` | `none` | `none` | `none` (by design) |

The platform label's discriminator is **procfs presence, not the OS name**
(`process_children_map` reads `/proc`), so a POSIX host without one honestly gets
darwin's row.

Deliberately NOT in v2: any change to a kill site. Reach `pid` on async-nt stays the
live behavior — declared, not fixed. The control is gated on EXP-21 probe P1
(incidence: do real vendor workers actually leave a grandchild?), whose zero rule was
committed before running. `KILL_ON_JOB_CLOSE` is struck from invariant 7 as part of
this amendment. The operator-cancel seam is NOT declared here: cancel runs
cross-process from another actor, so it is not a per-spawn receipt fact — its policy is
a separate open decision.

| Decisão (v2) | Fontes |
|---|---|
| Reach belongs on the SPEC-163 shelf, not a new surface | It is the third column of a discipline already ratified here (`*Enforced` = host CAN, `*Applied` = this spawn DID); `MANIFEST_KEYS` already carries the scope qualifier `procAppliedScope` |
| Declare before controlling | measure-before-control (EXP-21 `active`, `docs/EXPERIMENT_METHODOLOGY.md`); the mechanism is measured, the INCIDENCE is not — and only incidence justifies a kill-site change |
| Target declared alongside the fact | Owner 2026-07-27; without it a permanent honest gap reads as an accepted end-state |
| The gap set is machine-checked, not prose | D045 (`DECISIONS.md`) — "não regredir, não nivelar por baixo, declarar o gap"; a markdown table nobody executes rots |
| One vocabulary for the axis: reach, no parallel `supportState` | Owner 2026-07-27 ("um vocabulário"); D045 rule 3 names `supportState` as THE declaration vocabulary, so minting a second field for the same dimension is precisely the drift it guards against — the tier is derivable from the reach, not stored beside it |

### v3 (2026-07-27) — darwin reaches the tree; the first gap closes, and the ratchet made it

The `bounded:darwin` gap declared hours earlier in v2 is **closed**, not merely
scheduled. Owner 2026-07-27, on learning the CI matrix already carries a macOS
runner (`.github/workflows/harness-ci.yml:18`): *"bora fazer um mac e testar também
e o Ubuntu também."* No Mac hardware was needed — the gap was declared, the verifier
already existed.

- `process_children_map` (`processes.py`) no longer returns `{}` where there is no
  procfs: it asks `ps -axo pid=,ppid=`. linux keeps the `/proc` path, nt keeps its
  early return, and any failure degrades to the previous empty map — **the blind-write
  fail direction is toward today's behavior, never worse** (this was written from an
  nt host and is verified by the CI darwin leg, not locally).
- The parsing half is a pure function (`_parse_ps_ppid`), so it is exercised on
  **every** OS from canned output; only the exec itself needs darwin.
- `tree_kill_reach("bounded")` now reads a CAPABILITY — `descendants_enumerable()`
  (procfs OR `ps`) — instead of the OS name. A POSIX host with neither honestly
  declares `session`, and `hsb-13` then goes red for an UNDECLARED gap. Verified by
  simulating all four platform shapes: linux green, darwin green, posix-without-`ps`
  **red as designed**, nt green with `async:nt` still declared.
- Amended matrix: **bounded is `tree` on all three columns.** `DECLARED_KILL_GAPS`
  retains `async:nt` alone.

The ratchet worked as specified on its first real exercise: closing the gap without
striking its entry turns `hsb-13` red, so the declaration could not lag the code.

Still OPEN and deliberately unfixed: `proc-darwin-pid-alive-procfs`. `pid_alive` reads
`/proc/<pid>/stat` and returns False on `FileNotFoundError` — correct on linux, but
darwin has no `/proc` at all, so every pid may read dead, and `workflow_async_recover`
keys on it. `esh-5` ships as a **measurement with no guard beside it**: a fix landing
in the same commit would make the suspicion unfalsifiable. The CI macOS leg answers it.

| Decisão (v3) | Fontes |
|---|---|
| Evolve darwin UP rather than level linux down | D045; `signal_process_tree` has 31 call sites, and the "Form A" subtraction was rejected |
| Reach reads capability, not OS name | A host with neither procfs nor `ps` would otherwise be told it reaches the tree — exactly the class of lie SPEC-163 exists to end |
| `esh-5` ships WITHOUT its guard | measure-before-control: a suspected defect fixed in the same commit as its detector can never be confirmed or dismissed |
| `ps` exec over a ctypes libproc walker | ponytail — one stdlib exec on a path that runs only where procfs is absent; the walker earns its keep only if the exec ever measures hot |
| No per-profile lifetime field | One worker tree simultaneously holds members that must die with the task and members that exist to outlive it; no profile boolean can split a tree. The declaration already exists in code as WHICH SPAWN PRIMITIVE created the child — deterministic, OS-assigned by inheritance, never a model judgment |
| `KILL_ON_JOB_CLOSE` rejected | It couples worker lifetime to handle lifetime; a supervisor crash would kill every in-flight worker, inverting `workflow_async_recover` |

### v4 (2026-07-27) — the cage is reached: nt sweeps the job, detached breaks out of it

v2 declared the `async:nt` gap and refused to fix it, on purpose: the control was
gated on **incidence**, not on mechanism. EXP-21 probe P1 answered it (owner-ratified,
verdict `shipped`, grade 2): per timed-out async worker, codex left **3, 3, 3** and
claude **5, 5, 5** live GRANDCHILDREN, against **0, 0, 0** on the bounded control —
three reps per cell, zero within-cell variance. The kill was verified as the TIMEOUT
branch (`returnCode 15`, `timeout: true`, `cancellation.requested: false`), not
cancellation. The gap was real, vendor-independent, and measured before it was closed.

11. **An nt timeout kill sweeps the CAGE, then releases it.** On the async seam, the
    kill ladder is unchanged and stays the primary kill — `safe_signal_pid` →
    `TerminateProcess(pid, 15)` on nt, `killpg` on POSIX, which is why the P1 forensic
    `returnCode 15` is preserved byte-identically. What is added is one call in the
    SAME `finally`, before `close_win_handle`: `processes.terminate_win_job(async_job)`,
    guarded on `timed_out`. The supervisor coroutine already holds that worker's Job
    Object handle — the job is created UNNAMED (`CreateJobObjectW(None, None)`), so no
    other process could reach it, and none has to: `await proc.wait()` returns control
    the instant the worker dies with the handle still open. No pid enumeration, no
    cross-process machinery, no new state. Ordering is load-bearing: closing the last
    handle DESTROYS the job, so sweeping after the close is a silent no-op — MEASURED,
    with a split that matters: `hsb-13` stays GREEN (a source-string pin cannot see
    statement order) while `exp21-8` goes RED. See the decision table below; an earlier
    draft of this sentence claimed every check would pass, which is the stale, more
    pessimistic version and would have argued against the behavioural check that in fact
    catches it. This also covers the **give-up wedge** at the end of the
    ladder — a worker that survives both SIGTERM and SIGKILL used to leave its whole
    tree behind and now dies with it. **POSIX ships zero behavior change** (the sweep
    is a no-op off nt, and killpg already reached the session).
    The condition is `timed_out` **only**. Not normal exit: a breakaway-denied caged
    gate runner must survive its parent's clean exit (invariant 7 — the recover sweep
    owns that frontier). Not cancellation: see the pointer below.
12. **Detached spawns break away from the cage on nt.** `processes.popen_detached` is
    the single detached primitive (`launch_detached` routes through it) and adds
    `CREATE_BREAKAWAY_FROM_JOB`; `DEFAULT_JOB_LIMITS` carries `breakawayOk` so the
    cages we create permit it. It is **fail-closed, not fail-open**: a denied breakaway
    (`WinError 5`) is logged and retried WITHOUT the flag, leaving the child
    caged-but-killable rather than unspawned. `SILENT_BREAKAWAY_OK` on our own jobs is
    a **ratified rejection** — it would exempt every descendant of every caged process,
    including the ones invariant 11 exists to reach. Without invariant 12, invariant 11
    would be a regression: a harness-detached gate runner spawned from inside a caged
    worker would be swept along with it.

**A caveat on invariant 11 that was checked, not assumed — the cage is often an OUTER
job.** `.venv/Scripts/python.exe`, the declared `HARNESS_PYTHON` and therefore the
interpreter the gate runs, is a launcher stub that respawns the real interpreter inside
a NESTED Job Object of its own carrying `JOB_OBJECT_LIMIT_SILENT_BREAKAWAY_OK`
(measured 2026-07-27: a caged process's IMMEDIATE job reads LimitFlags `0x3000` under
the venv against `0x8` — our own cage — under the system CPython). So when the caged
process is a venv python, `assign_job_to_pid` cages a job ABOVE the one doing the work.
`TerminateJobObject` still reaches it, because job containment is hierarchical — and
that is exactly what `exp21-8` exercises, since its `hang` worker IS a venv python and
its caged grandchild dies. Two consequences for anyone extending this: never assume the
pid you caged is the pid doing the work, and never read a Job Object check's colour
without knowing which interpreter produced it. `hsb-14` carries the same lesson on the
breakaway side — under the venv the denial is swallowed silently and never raises
`WinError 5`, so that arm reports which interpreter it ran under rather than passing
quietly. This is NOT a flag we set: the rejection of `SILENT_BREAKAWAY_OK` in invariant
12 binds the jobs the harness creates.

Amended matrix — `async:nt` moves `pid → job`, citing EXP-21 P1:

| seam | nt | linux | darwin | objective |
|---|---|---|---|---|
| bounded | `tree` | `tree` | `tree` | `tree` |
| async | **`job`** (was `pid`; EXP-21 P1) | `session` | `session` | cage (`job` / `session`) |
| detached | `none` | `none` | `none` | `none` (by design) |

**`DECLARED_KILL_GAPS` is now `{}`.** `async:nt` was the last entry and is struck here,
the way `bounded:darwin` was struck in v3. Empty is the honest state, not a forgotten
declaration: `hsb-13` asserts the dict is EXACTLY the live divergence on the running
platform, so the moment reach and target part again on any platform it goes red.

**Where the teeth actually are.** `hsb-13` locks declarations against declarations and
against source STRINGS; it never observes a kill, so a kill site that still compiles and
still misses the tree would pass it. That scope is now stated in its own docstring
instead of being claimed as a "declaration/code drift lock". The behaviour teeth are
**`exp21-8`**, which drives the real detached supervisor → `_run_async_task` → the
TIMEOUT branch with an 8s worker timeout and a `hang` worker, asserts the branch
FINGERPRINT first (`status == "timeout"`, `run.timeout is True`, cancellation not
requested — so it cannot pass off the cancellation branch), and then asks the OS: the
CAGED grandchild must be dead (arm 1, falsifiable on nt; POSIX passes today via killpg
and runs as regression) and the DETACHED grandchild must be alive (arm 2 — vacuous-
looking today by design, it reds the day anyone ships `KILL_ON_JOB_CLOSE` or widens
this into a blanket tree-kill). Deleting the sweep call turns arm 1 red on both
interpreters; that was verified, not assumed.

And **`exp21-9` guards the GUARD.** The `timed_out` condition had no check at all until
`oracle mutate` widened `if timed_out and async_job` to `or` and every check stayed
green: on nt `async_job` is always truthy, so the mutant swept on EVERY settle, and
`exp21-8`'s worker times out anyway so it never noticed. A sweep on normal exit would
kill a caged gate runner that invariant 7 requires to survive its parent's clean exit —
the exact regression invariant 12 exists to prevent, reintroduced through the back door.
`exp21-9` runs a worker that exits 0 CLEANLY with a caged grandchild behind it and
asserts that child is ALIVE, fingerprinting the clean-exit branch (`rejected`, rc 0,
`timeout` not True) so it cannot pass off the timeout branch. It kills that mutant.

**Cancel** — ~~the sweep is deliberately NOT wired to the cancellation arm here~~
**SUPERSEDED BY v5**, which wires it. The v4 text read: "the owner chose *'spare the
detached child, but ASK me first'*, which became the row
`proc-cancel-graded-destruction` — still open and being re-planned". That row is now
decided; v5 records what was and was not built for it.

| Decisão (v4) | Fontes |
|---|---|
| Close the gap now, not later | EXP-21 P1 (owner-ratified, `shipped` grade 2): incidence measured 3,3,3 / 5,5,5 against a 0,0,0 bounded control — the exact evidence v2 said it was waiting for |
| The handle owner is the killer | The job is UNNAMED, so cross-process reach is impossible; it is also unnecessary — the supervisor coroutine is awake with the handle open the instant the worker dies |
| Sweep AFTER the ladder, not instead of it | `TerminateProcess(pid, 15)` is what produced P1's `returnCode 15`; replacing it would silently rewrite kill forensics, and POSIX would lose a path that is already correct |
| Sweep BEFORE `close_win_handle` | Closing the last handle destroys the job, so the reversed order is a silent no-op. MEASURED, not assumed: with the sweep moved below the close, `hsb-13` stays GREEN (the pinned literal is still there — a source-string pin cannot see statement ORDER) while `exp21-8` goes RED with `cagedAlive=True`. That split is the whole argument for putting the behaviour teeth in `exp21-8`: hsb-13 alone would have been the green window containing a lie |
| ~~`timed_out` only, never normal exit or cancel~~ **SUPERSEDED BY v5**: timeout **or** operator cancel, still never normal exit | Invariant 7 (a detached worker must outlive its parent's clean exit) survives intact; the "never cancel" half rested on the then-open `proc-cancel-graded-destruction` row, decided in v5 |
| `exit_code=15` on the sweep | Matches the pid ladder's SIGTERM, so a swept tree and a laddered pid carry the same code and forensics stay uniform |
| Breakaway is fail-closed | A denied breakaway leaves the child caged-but-killable, never unspawned; the alternative fails toward a worker that never starts |
| `SILENT_BREAKAWAY_OK` rejected | It exempts every descendant of every caged process — precisely the ones invariant 11 exists to reach |
| Behaviour teeth in `exp21-8`, not in a stronger `hsb-13` | Testing playbook failure mode 2: a check that pins source text cannot be strengthened into a check that pins behaviour; hsb-13's honest scope is declared instead of inflated |

### v5 (2026-07-27) — operator cancel joins the cage sweep; the graded "ask first" layer is NOT built

v4 left cancel out on purpose, pointing at the open row
`proc-cancel-graded-destruction`. That row asked for *"spare the deliberately-detached
child, but ASK me first"*. Half of it was already true and the other half has no target:

**Invariant 11's condition widens (reach unchanged).** The sweep now fires when the
worker `timed_out` **or** when the cancellation marker carries all of: `requested`,
`source == "operator"`, a `workerId` that is null or this worker's, and a nonzero,
non-None exit code. Never on normal exit (invariant 7, `exp21-9`). Never on internal
settlement (`exp21-11`). `workflow_cancel` is the only writer of `source` —
the await-policy `cancelRest*` writer and the `workflow start` initializer do not carry
it, which is what makes the trigger deterministic rather than a heuristic on
"something set `requested`". All readers use `.get`, so the key is additive.
`workflow await --cancel-on-timeout` routes through `workflow_cancel` and therefore
inherits `source: "operator"` — deliberate: an await-timeout cancel IS an explicit
destruction request and gets timeout-equivalent blast radius. The GUI cancel builds the
same CLI, so there is no GUI-specific branch.

**Blast radius, per platform, stated instead of implied:**

| path | before v5 | after v5 |
|---|---|---|
| nt, supervisor alive | worker pid only — and under the venv launcher the *real* interpreter is a job member BEHIND the launcher stub (the v4 caveat above), so it survived the cancel as an orphan | worker pid + its Job Object: the caged tree dies; deliberately-detached children structurally spared (invariant 12) |
| nt, supervisor dead (orphaned) | worker pid only | unchanged — the job handle died with the supervisor and the job is unnamed, so nothing can reach it. Stated, not fixed |
| POSIX | process group via `killpg`; `start_new_session` children spared | unchanged, byte-identical (`async_job` is None off nt, so no new branch executes) |

The nt "before" row is the sharp end: on the interpreter the gate actually runs, cancel
already left the process doing the work behind. v5 is nt catching up to the behaviour
POSIX has had since the first `killpg` — kill the caged, spare the detached — not new
policy the owner has never lived with.

**The destruction is now observable**: a deterministic `async_cage_swept` event
(`asyncTaskId`, `workerId`, `trigger` ∈ {`timeout`, `operator-cancel`}) is appended after
the handle is closed, so an event-write failure can never leak a handle. It is
observability, not teeth, and is deliberately unasserted.

**What the row asked for and did NOT get, with re-open triggers.** The confirmation
prompt is not built, because its target set is empty: the only destructive primitive a
supervised cancel can gain is the Job Object sweep, and `CREATE_BREAKAWAY_FROM_JOB`
(invariant 12) keeps detached children out of that job *by construction* — the sparing
the owner asked for is enforced by the kernel, and `exp21-8` + `exp21-10` arm 2 keep it
enforced. A prompt would guard nothing, and its list could not even be computed: job
membership is invisible cross-process, and CIM answers parentage, which is a different
question. Triggers to build it: a MEASURED `launch_detached` child found inside a worker
job at cancel time (the breakaway-denied contingency of invariant 12 becoming real on a
supported interpreter), or the owner classifying some caged child as
non-trivial/non-recoverable. Also not built and gated on the same evidence: CIM/
`process_children_map` enumeration (would charge every Windows `signal_process_tree`
caller and contradict `esh-6`), survivor notification after a cancel (a different
feature, filed separately as a backlog row pending an explicit owner yes), no-TTY
refusal / `--force` / approval-staleness re-check (all exist only to serve the prompt —
the cancel CLI keeps its exact surface), and an orphaned-supervisor sweep (trigger: the
owner requires it).

**Unpinned on purpose, declared rather than hidden:** the `returncode not in (0, None)`
term (its falsifying scenario — a worker exiting 0 in the same window a cancel lands — is
inherently racy to rig; trigger to pin it: any measured clean-exit sweep in the wild) and
the `workerId` scope term (a deterministic 2-worker bystander rig is possible but costs a
concurrency-2 sentinel rig for a term with no caller in anger; trigger: first real use of
`cancel --worker-id`).

**And arm 2 of `exp21-8`/`exp21-10` is STILL vacuous — the mutation table does not give it
teeth, which was measured rather than assumed.** The obvious mutant (swap the sweep for
`signal_process_tree(proc.pid, …)`, the `taskkill /T` trap) does turn both checks red, but by
ARM 1 (`cagedAlive=True`), never arm 2: by the time that `finally` runs the worker is already
dead, so a tree walk rooted at its pid reaches nothing at all and the detached child survives
either way. Read that as the warning it is — "a mutant went red" is not evidence that the
assertion you had in mind went red, and this repo has already shipped one check that passed
for a neighbouring mechanism's reason. A mutant that genuinely exercises arm 2 must fire a
tree kill while the worker is still ALIVE, or ship `KILL_ON_JOB_CLOSE`. Until one exists, arm
2's teeth are entirely prospective and this paragraph is the only thing saying so.

**No manifest change.** The matrix, `DECLARED_KILL_GAPS` (still `{}`), `tree_kill_reach`
and `tree_kill_target` are untouched: reach stays `job` / `session`; only the TRIGGER SET
widened. `hsb-13` must stay green unmodified — strengthening it is the rejected move
(v4's last decision row).

| Decisão (v5) | Fontes |
|---|---|
| Wire cancel to the sweep, do not build the prompt | The sparing is kernel-enforced (invariant 12 + `start_new_session`), so the prompt's target set is empty; a prompt whose list is wrong is worse than no prompt |
| `source: "operator"` on the marker, not "any `requested`" | The await-policy `cancelRest*` writer sets `requested` too; keying on it alone would let internal group bookkeeping destroy caged trees nobody asked to destroy. `exp21-11` pins that bypass closed |
| Nonzero-exit term kept | Mirrors the settle classifier's clean-exit exception: a worker that exits 0 during a group cancel is not destroyed, and its breakaway-denied caged child survives (invariant 7) |
| Divergence from the settle classifier accepted | That branch also spares a nonzero-exit worker whose stdout still yields an extractable result; extraction runs AFTER this `finally`, so such a cage is swept anyway. The operator said stop, and a salvaged receipt does not un-say it |
| `--cancel-on-timeout` inherits operator blast radius | It reaches the same `workflow_cancel`; an await-timeout cancel is an explicit destruction request, and giving it a quieter radius than a worker timeout would be the inconsistency |
| Event after `close_win_handle` | The handle release must not depend on an event write succeeding; the event is observability, not teeth |
| No new scenario file, no `spec_test_gate` change | The teeth belong beside the sweep's existing behaviour checks (`exp21-8`/`-9`), which already drive the real supervisor seam |
