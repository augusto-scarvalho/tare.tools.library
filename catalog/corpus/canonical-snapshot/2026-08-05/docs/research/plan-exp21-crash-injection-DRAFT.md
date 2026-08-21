# EXP-21 (DRAFT) — deterministic crash injection across the three spawn seams

Author: `planner-xhigh` spawn (Fable, effort `xhigh`), 2026-07-27. Read-only run;
plan returned as result text and written to disk by the overseer, unmodified
except for HTML-entity unescaping.

Brief: `.harness/handoff/plan-exp21-crash-injection.READY`. Owner scope decision
**D043** (2026-07-21, reconfirmed 2026-07-27) is binding: all three seams, async
first, `mtime`+refs rather than E-EFFECTID. Overseer re-verification of the
load-bearing findings is at the end.

---

All `file:line` anchors below were re-verified by symbol against the live tree on 2026-07-27 (confidence: high unless marked). Measured facts from the brief are taken as given.

## 1. Verdict on the brief and the two documents

### 1.1 The contradiction, resolved: the "worker entrypoint" the earlier plan instruments does not exist

`rd-crash-implementation-plans.md` puts the `HARNESS_CRASH_AT` guard "no ENTRYPOINT do worker" with ~3 lines of env propagation in `processes.py`. On this repo's three seams, **the production worker's entrypoint is a vendor binary the harness does not own**. Worker argv is resolved from `commandTemplate` in `.harness/routing/executors.json` (`workflow_spawn_command_for_prompt` — the persisted `task["command"]` at `scripts/harness_lib/async_runtime.py:377-379` and `:815-825`; bounded twin at `scripts/harness.py:1644-1668`). There is no repo-owned Python entrypoint between `create_subprocess_exec` and `claude.exe`/`codex` to host a crash guard. The only harness-owned processes on these seams are the router, the async supervisor, and the spawn library — and the round's own synthesis (w-002, `rd-crash-injection-round.md:100-108`) forbids crash logic in the shared production path. So the entrypoint variant is unimplementable as written: pushed to its only possible homes, it either lands in the orchestrator (self-refuting by w-002) or in a worker whose entrypoint we own — **which is a stub**.

That dissolves the contradiction rather than adjudicating a preference. Both documents agree on the mechanism that matters: a **cooperative, env-triggered, deterministic crash inside the worker's own code** (the round's convergence, 4/5 ideators). They disagree only on which file hosts the guard, and the earlier document names a file that does not exist. The dossier's `_exp21_crash_stub.py` twin **is** the entrypoint plan correctly instantiated against the real seam map: the crash point is a line of the child's own flow (no scheduler race, per the SQLite-VFS analogy), and the child is spawned by the **real** seam with the **real** machinery — `sandbox_prepare` chokepoint, CREATE_SUSPENDED + Job Object assign (`async_runtime.py:424, :437-462`), least-privilege env filter (`harness.py:1567-1577` → `processes.py:721-738`). Decision: **stub**. Carried forward verbatim from the earlier plan: the w-004 trap list (section 5), the hang mode, and the never-probabilistic rule.

**What the stub proves:** every parent-side property — classification-tree landing, recover idempotency, breaker single-count (`async_runtime.py:336-349`), reap mechanics, lock/settle hygiene. EXP-21's hypothesis (`.harness/state/experiments.json:451`) is entirely a parent-side property ("a recuperação do harness ... não deixa trabalho órfão nem efeito duplicado"), so the stub covers the experiment's full claim surface.

**What the stub cannot prove, honestly:** vendor-specific death shapes — the real claude/codex CLI's own crash exit codes, a real stream-json envelope truncated mid-stream by a dying vendor process, vendor-binary WER interaction, and cost accounting for a crash mid-model-turn. The entrypoint variant could not prove these either (it cannot exist inside the vendor binary). The only test of vendor death shape is killing a real vendor worker, which the round correctly rejected as non-deterministic except via sentinel-gate — and even that proves kill-shape, not crash-shape. This residual is priced into section 6.

### 1.2 Where the brief is wrong: the hang-mode claim

"Only the entrypoint variant reaches the `hang` mode at all" — **false**. Hang is a property of the child's behavior, not of where the guard lives: a stub blocks forever exactly as well as an instrumented entrypoint (`while True: time.sleep(...)` after a sentinel write). The dossier omitted hang by *choice* ("timeout como proxy de crash = já coberto", `rd-crash-adapter-boundary.md:52-53`), not by capability. I overrule the dossier's omission and include hang, because of the next finding. (referência: source reading + judgment, high)

### 1.3 New finding: the w-004 "hang reaped through the Job Object" trap describes behavior the async seam does not have

Verified today: the async timeout reap is `safe_signal_pid` → `processes.signal_pid_group` (`async_runtime.py:485-489` → `async_state.py:227-228` → `processes.py:207-228`), which on Windows is `os.kill(pid, sig)` = TerminateProcess **on the pid only** — its own docstring disclaims grandchildren. The worker's Job Object carries **no KILL_ON_JOB_CLOSE** (`sandbox_spawn.py:42-43` — `DEFAULT_JOB_LIMITS` is `activeProcesses` + `jobMemoryBytes` only; `processes.py:443-447` states the no-kill-on-close design), so closing the handle in the `finally` (`async_runtime.py:497`) frees a surviving grandchild rather than reaping it. The **bounded** seam, by contrast, tree-kills via `signal_process_tree` = `taskkill /PID .. /T /F` (`processes.py:129-141`, used at `processes.py:606-610`). So a hang worker that spawned a grandchild **orphans the grandchild on the async seam and not on the bounded seam** — a measurable orphaned-work differential that is precisely EXP-21's A6 metric. The trap as written in both research docs is aspiration, not description; the measurement decides whether it becomes a SPEC-163 amendment (section 8). (source: code reading 2026-07-27, high)

### 1.4 Fact 3, given full weight

Verified in source: the cancellation branch at `async_runtime.py:555` sits ahead of the crash fall-through at `:593-596` and matches the identical observable shape (rc∉{0,None}, no result). It fires only when `cancellation.get("requested")` is true — which the consumer's cancel-rest path can set mid-wave (`:688-691`) and `workflow_cancel` sets any time. Two consequences drive the design: (a) the primary crash cases run with `requested=False`, so they *cannot* land on `:555` — but a lazy assertion ("not fulfilled") would stay green even if they did, so **every crash case asserts the branch fingerprint, not the absence of success**: `task.error == f"worker exited with return code 3"` is produced by no other branch in the tree (`:596`); any future branch inserted ahead that steals the crash produces a different error string and turns the scenario red. (b) The shadowing itself (a genuine self-crash during a cancellation window recorded as `cancelled`) is real and currently unavoidable — phase 2 carries a deterministic **canary** that measures it instead of asserting it away.

### 1.5 Q4, established loudly: the "R1 pruner" does not exist as an automatic pruner

Inventory, verified today:

- `tools/prune_worktrees.py` exists — **manual**, dry-run by default, and prunes only `.git/worktrees/*` **admin metadata dirs** (OneDrive-lock cruft), never workflow workspaces or working trees (`tools/prune_worktrees.py:1-20, :54-74`).
- `workflow cleanup-write` / `cleanup-worktrees` — **manual CLI**, `--force`-guarded (`scripts/harness_lib/workflow_writes.py:568-582, :619-652`).
- The only automatic caller is `route_loop._default_cleanup` (`scripts/harness_lib/route_loop.py:462-467`) — end-of-demand, route path only, best-effort.
- `workflow_async_recover` prunes **nothing** — it settles task state and never touches `workspaces/`/`worktrees/` (`async_runtime.py:296-334`).
- `gate_parallel`'s `git worktree prune` (`gate_parallel.py:317-318`) covers only the gate's own detached copies.

A worker that dies before merge in a plain (non-route) write workflow leaves its workspace until an operator runs cleanup. The dossier's "no orphan worktree" assertion, phrased as an invariant, **tests something nobody implements**; `article-coverage-backlog.md:268`'s claim that a "worktree pruner ... já passa" is overstated on the same evidence. The design converts this from a doomed assertion into the experiment's first pre-registered expected finding: the scenario *measures* workspace persistence after a pre-merge crash (expected: **persists**) and the post-verdict control is a spec door (section 8). (high)

### 1.6 Smaller corrections

- `extract_worker_result` is an alias (`harness.py:1515` → `result_contracts`); any plan step naming "the parse at harness.py" must anchor in `result_contracts` — the dossier was wrong on line *and* module.
- The dossier's seam-3 anchor `async_runtime.py:840 Popen` is today the supervisor `Popen` at `:897`; `launch_detached` (`processes.py:251`) is additionally used by `gate_staged.py:107` and `sandbox_spawn.py:363` — the detached-worker seam is broader than the dossier drew it, but the recovery frontier under test remains `workflow_async_recover`.
- D043's scope decision is sound and this plan does not reopen it; the dossier's own async-only recommendation (its closing section) is overridden by D043 and rightly so — the bounded/async reap asymmetry in 1.3 is only visible with all three seams in scope.

## 2. Target design (contract)

### 2.1 Footprint

Two new files, zero production-code changes:

- `testing/scenarios/_exp21_crash_stub.py` — the crash stub (stdlib only, `_` prefix = outside the gate glob).
- `testing/scenarios/exp21_crash_injection.py` — the scenario (auto-discovered by `gate_scenario_order.fail_fast_order`'s `glob("*.py")` at `gate_scenario_order.py:104`; `_`-skip at `spec_test_gate.py:1531`). **Gate wiring cost in `spec_test_gate.py`: zero lines — confirmed**; the file sits at 1659 of the 1660 `gs-7` ceiling, so zero is also the only affordable number.

### 2.2 Executor injection: on-disk, not monkeypatch — and why

rt6 injects its stub executor by monkeypatching `harness.load_executors` in-process (`rt6_route_writechain.py:169-174`). That pattern **cannot** serve EXP-21 phase 1: `workflow start` spawns the supervisor as a *separate process* (`async_runtime.py:897`), which re-reads `.harness/routing/executors.json` (`harness.py:77-81`) and calls `executor_config(executor_name)` inside `build_worker_spawn_env` (`async_runtime.py:392` → `harness.py:1576` → raise at `:886-890`). The persisted `task["command"]` survives the hop (`:377-379`), but the env-keep-list lookup does not. Therefore: the scenario **temporarily registers** `exp21-stub` in `.harness/routing/executors.json` (add key, write, restore byte-identical in `finally`). Backstop: the gate snapshots and restores `.harness/routing` around every scenario (`scenario_isolation.py:48-59`), so even a hard-killed in-gate run cannot leak the registration. One mechanism, all three seams. Residual: a hard-killed *standalone* run leaves the registration until manual restore or the next gate run — named and accepted (same residue class as any scenario).

Executor shape (mirror of `rt6_route_writechain.py:43-51`):

```json
"exp21-stub": {"type": "cli", "runnable": true, "trustTier": "third-party",
  "envKeepList": ["EXP21_*"],
  "commandTemplate": ["{python}", "{root}/testing/scenarios/_exp21_crash_stub.py", "{prompt}"],
  "defaultSpawn": {"profile": "scan", "model": "stub", "effort": "low", "agent": "stub"}}
```

### 2.3 Trigger surface

`EXP21_CRASH_AT=<mode>` (+ `EXP21_SENTINEL` / `EXP21_ACK` absolute paths under the WF dir), set in the scenario's own environment around each 1-worker workflow. Propagation is exact and Windows-safe by construction: the supervisor inherits the scenario env (Popen at `:897`, no `env=` override), and the worker spawn re-applies `filter_spawn_env`, which passes `EXP21_*` **only** for an executor whose `envKeepList` names it (`processes.py:730-732`, wildcard support proven in production by `RT6_*`). No production executor carries `EXP21_*`.

**Counter triggers are dropped.** `abrupt:call=N` exists to select a point inside a long *real* execution; a purpose-built stub encodes the point structurally — same determinism, no parser. The one byte-knob that earns its keep: `partial_write:bytes=K` (default 150; the SQLite crash-at-offset analogy).

### 2.4 Modes and their target branches (async numbers; bounded/detached in section 4)

| mode | stub action | lands on | proves |
|---|---|---|---|
| `pre_result` | `os._exit(3)` before any write | `:593-596` "worker exited with return code 3", task `rejected` | A13 crash-before-receipt |
| `exit0_no_result` | `sys.exit(0)`, no receipt | `:589-592` worker `missing` | clean-exit-no-receipt is not a crash |
| `post_result` | write valid WORKER_RESULT file, `os._exit(3)` | `:563-583` `fulfilled` despite rc=3 | idempotency: receipt beats rc; recover no-op |
| `partial_write:bytes=K` | write K bytes of the receipt JSON, flush+fsync, `os._exit(3)` | `:563-579` `rejected` with `validationErrors` | garbage receipt ≠ missing receipt |
| `hang` | spawn one grandchild (`sleep`), write sentinel, block forever | `:559-562` `timeout` | reap mechanics + grandchild-orphan differential (1.3) |
| `sentinel_exit3` | write sentinel, poll for ACK, `os._exit(3)` | phase-2 orchestration primitive | detached kill-gate + cancellation canary |

`os._exit` for the abrupt modes (no interpreter cleanup, faithful "morte abrupta", and guarantees the partial write is exactly K durable bytes after fsync); `sys.exit(0)` only for the clean-exit mode.

### 2.5 The never-reach-production guard, structurally

Three independent layers, each sufficient: (1) crash logic lives in a test-only file no production code imports or spawns — production argv comes only from committed `executors.json` templates, and no *committed* executor references the stub (the registration exists only inside a scenario run, finally-restored + gate-snapshot-restored); (2) the trigger env survives `filter_spawn_env` only via an `envKeepList` that only the transient stub executor carries — a leaked `EXP21_CRASH_AT` in anyone's parent env is dropped for every real executor; (3) the `_` prefix keeps the stub out of the scenarios glob. Reaching production would require committing an executor-config change — a reviewed, diffable act, not an accident.

### 2.6 Exit-code contract

Crash rc = **3**. Reserved-avoid set, asserted in the stub's self-check: `0` (success), `0xC0000005`/`0xC0000409` (real OS failure statuses — w-004), **`259`** (STILL_ACTIVE: a process exiting 259 is reported alive forever by `pid_alive`'s `GetExitCodeProcess` poll, `processes.py:170-186` — a new trap, mine), `124` (the harness's internal timeout-marker convention, `workflow_writes.py:609`), `15`/`1` (kill-path codes, keeps crash distinguishable from the cancel/timeout kills in forensics).

## 3. Phased plan

Phases are commit boundaries; each independently shippable, each leaving one falsifiable check measured against live code. All phases: gate only via `gate-staged`, no `.harness/` writes while a gate is in flight.

### Phase 1 — async seam (D043: first), receipt-boundary modes

**Files:** `_exp21_crash_stub.py` (new), `exp21_crash_injection.py` (new, async section).
**Shape:** for each of `pre_result | exit0_no_result | post_result | partial_write`: plan a 1-worker scan workflow (the proven cheap recipe, `gate_fixtures_workflow.py:234`, in-process via `import harness`), register executor, set env, real `workflow start` → real detached supervisor → `workflow await`; then `workflow_async_recover`; scrub WF in `finally` (rt6 `_lib.scrub` pattern). Small `workerTimeoutSeconds` throughout.
**The ONE falsifiable check** — the branch fingerprint: for `pre_result`, `task.status=="rejected"` AND `task.error=="worker exited with return code 3"` AND `run.rateLimitDetected is False` AND cancellation file `requested is False`; plus, for `post_result`: result-file mtime identical across settle→recover→second `workflow start` (which must report "No runnable workers", `async_runtime.py:758-759`), task count still 1, no `failoverHistory`, breaker recorded exactly one outcome (`_record_executor_outcome`, `:336-349`). Red today? The *scenario* is the new artifact; its falsifiability is against mutations of live code it names: reordering/widening the `:555` cancellation branch, recover re-spawning, a second effect write — each flips a named assertion. A fixture the check itself wrote is never consulted: every assert reads live task/state/result files produced by the real seam.
**Acceptance:** scenario green in the scenarios gate on nt and POSIX (branch fingerprints are OS-neutral); no residue in `.harness/workflows/active` or routing after run.
**Rollback:** delete two files. No production surface touched.

### Phase 2 — detached seam: sentinel-gated supervisor death + the fact-3 canary

**Files:** `exp21_crash_injection.py` only (new section).
**(a) Orphan path:** mode `sentinel_exit3`; wait for sentinel; `signal_process_tree(supervisorPid)` (`processes.py:129` — taskkill /T reaps supervisor *and* worker); assert task still recorded `running` with a dead pid; run `workflow_async_recover` → task `orphaned` with the `:329` error string, group settled, `workflow_doctor` (`:1040-1116`) transitions from "would orphan" verdict to healthy/`unlock --stale-only`; unlock if stale.
**(b) Cancellation canary (fact 3, measured not asserted):** mode `sentinel_exit3`; wait sentinel; write the cancellation file `{"requested": true, ...}` directly; write ACK; worker self-crashes rc=3; **record** that the settle lands `cancelled` (`:555-558`) — the branch-shadowing number for the EXP-21 report; assert only that the group settles terminally. A green assertion here would be the "wrong-branch green test" the overseer warns about; a recorded measurement is the honest artifact.
**The ONE falsifiable check:** (a)'s recover-classification chain — it fails if recover ever re-spawns, mis-states the supervisor-alive guard (`:327`), or stops marking orphans.
**Acceptance:** deterministic across 3 consecutive runs (sentinel-gate removes the timing race — the dossier's own condition for calling seam 3 deterministic).
**Rollback:** delete the section.

### Phase 3 — bounded seam + the two pre-registered findings (workspace orphan, hang differential)

Bounded goes last, and here is the argument the brief asked for: it is the *coldest* seam (blocking `workflow run`, gate fixtures), it shares the decision-tree shape minus the cancellation branch (`harness.py:1913-1926` — note: **no** cancellation branch and no error-string; assert `status=="failed"` + `run.returnCode==3`, and `"missing"` for rc=0 at `:1924-1926`), so its marginal A13 evidence is the smallest — but it is the *control arm* for the reap differential, which is why it belongs in scope (D043) yet not on the critical path.
**(a)** bounded `pre_result`/`exit0_no_result` via `workflow run` (registration already on disk; empty spawn chain for an unrouted executor guarantees exactly one attempt, `harness.py:1729-1731` — no failover duplicate hazard).
**(b) Workspace-orphan measurement (Q4):** one write-mode case — `prepare-write --mode temp-copy`, `pre_result` crash before merge — **record** that the workspace persists after crash + recover (expected: persists; nobody prunes, section 1.5). Not asserted as invariant in either direction: measure-only per the phase law. git-worktree mode is the same missing-pruner class; not built (section 6).
**(c) Hang differential:** `hang` mode with grandchild on bounded (assert grandchild dead post-timeout — taskkill /T) vs async (**record** grandchild alive — the expected orphaned-work non-zero; scenario reaps it in `finally`). nt-gated; on POSIX record the `killpg` behavior instead.
**The ONE falsifiable check:** (c)'s bounded arm — fails if `run_process_tree_bounded` stops tree-killing.
**Acceptance:** measurements emitted as one compact JSON summary line for the owner-gated registry append.
**Rollback:** delete the section.

**Measurement step (owner-gated, D043.4):** owner runs the scenario (or reads its gate output), appends `measurements[]` to the EXP-21 entry in `.harness/state/experiments.json`. Not automated by this plan.

## 4. The three seams, one table

| | crash observed at | must land on | "no orphan" there means | "no duplicate" there means | scenario asserts / records | cancellation hazard |
|---|---|---|---|---|---|---|
| **bounded** (`harness.py:1626 run_one_worker`, await `processes.py:600 communicate`) | rc read post-`communicate`; classify at caller `harness.py:1913-1926` | `failed` (default fall-through; rc≠0, no receipt) — no error string exists to pin, so pin `run.returnCode==3` + absence of `validationErrors` | pids reaped by `signal_process_tree` incl. grandchildren; temp workspace: **nobody prunes — measured, not asserted** | one attempt (empty chain `:1729-1731`); `only_missing` re-run skips a valid result (`:1817-1823`) | assert status+rc; record workspace persistence | **none** — no cancellation branch on this seam |
| **async** (`async_runtime.py:351`, spawn `:437`, await `:479`) | decision tree `:555-596` | `rejected` + error `worker exited with return code 3` (`:596`); rc=0→`missing` `:589`; garbage receipt→`validationErrors` `:563-579`; hang→`timeout` `:559` | pid dead post-settle; **grandchild NOT reaped today (`signal_pid_group` + no KILL_ON_JOB_CLOSE) — recorded**; lock released by supervisor `finally` `:710-714` | result mtime stable across settle/recover/restart; 1 task, no `failoverHistory`, breaker outcome recorded once `:336-349`; recover never spawns (`:296-334` has no spawn) | assert branch fingerprint quad (sec. 3 ph. 1) | **the `:555` branch**: fires iff `requested` — primary cases pin `requested is False` + the error string; the shadowing is measured by the phase-2 canary |
| **detached** (supervisor `Popen :897`; frontier `workflow_async_recover :296`) | recover: supervisor dead (`:305`) + pid dead (`:321`) + no result → `orphaned :329` | `orphaned`, error "registered process is no longer alive…"; valid result found → `fulfilled :314-320` (idempotent) | no live pid for task or supervisor; stale lock recoverable (`doctor :1095-1097` → `unlock --stale-only`); workspace: same missing pruner | recover marks, never re-spawns; `:327` guard prevents racing a live supervisor's own settle | assert orphaned chain + doctor verdict transition | `:327` supervisor-alive guard means recover *defers* to the cancellation path while the supervisor lives — the scenario kills the tree first, so the guard is provably passed |

## 5. Trap handling (w-004 verbatim + additions), one line each

1. **Exit-code collision (w-004):** rc=3; avoid-set includes `0xC0000005`/`0xC0000409` per w-004, plus my additions `259` (STILL_ACTIVE would make `pid_alive` report the exited worker alive forever, `processes.py:170-186`) and `124`/`15`/`1`.
2. **Truncated-stdout secret scrub (w-004):** the stub's entire output is canned ASCII containing no secret and no secret-shaped token, so no partial secret can exist to survive a cut; the production scrub path is untouched (measure-only probe), and the partial bytes go to the result *file*, not stdout.
3. **Env scoping on inheriting Windows (w-004):** `EXP21_CRASH_AT` crosses `filter_spawn_env` only via the transient stub executor's `envKeepList` (`processes.py:730-732`) — parallel or unrelated workers of any real executor never see it, even if the var leaks into a parent env globally.
4. **Truncation inside `maxWorkerOutputChars` (w-004):** `partial_write` default K=150 « the 4000 default read at every `validate_worker_result` call site, so the reject is a parse/shape reject, never an oversize reject.
5. **Hang reaped via Job Object, never TerminateProcess-on-pid (w-004):** **cannot be "handled" — it is untrue of the async seam today (section 1.3)**; the scenario measures the consequence (grandchild orphan differential) instead of pretending the trap is satisfied; the fix is a post-verdict SPEC-163 amendment.
6. **Rate-limit needle (new):** a stub output matching `rate_limit_detected` would reroute classification to `blocked` and trigger the SPEC-115 failover **re-spawn** (`async_runtime.py:584-587, :602-620`) — a duplicate created by the test itself; stub output contains no quota/rate strings and every case asserts `run.rateLimitDetected is False`.
7. **Soft-warnings rewrite vs the mtime probe (new):** the ingest rewrites the result file when soft fields were bounded (`:571-574`); the stub result mirrors rt6's clean shape so the mtime probe measures duplicates, not the harness's own bounding rewrite.
8. **POSIX portability (new):** CI runs ubuntu/macos (`gate_checks_release.py:147`); branch-fingerprint asserts are OS-neutral, Job-Object/grandchild assertions are `os.name`-gated with per-OS recording.
9. **WER (constraint item):** not applicable — no `os.abort()` in scope (Q2, section 7).

## 6. What I would NOT build, and what would change my mind

- **The entrypoint/`processes.py` propagation variant** — no harness-owned worker entrypoint exists to host it (1.1). Changes my mind: the harness ever ships its own worker shim binary/wrapper on the production seams.
- **E-EFFECTID as prerequisite** — already decided conditional (D043.3); mtime+refs+breaker-count triangulate a duplicate without it. Changes my mind: the measurement shows an ambiguous duplicate that mtime+refs cannot adjudicate.
- **`os.abort()` mode (Q2)** — see section 7.
- **Counter triggers (`call=N` etc.)** — select points in long real executions; the stub encodes its point structurally. Changes my mind: instrumenting a real long-running harness-owned child (e.g., the supervisor itself) becomes in-scope.
- **A workspace pruner or any classification-tree change inside EXP-21** — the phase law forbids control changes under an `active` experiment (`docs/EXPERIMENT_METHODOLOGY.md:48-56`); measure first. Changes my mind: a `shipped` verdict.
- **The git-worktree-mode orphan case** — same missing-pruner equivalence class as temp-copy at ~3× the ceremony (branch + admin-dir cleanup). Changes my mind: the owner wants the EXP-21 report to speak to `git worktree list` hygiene specifically.
- **stdout-ingest crash variants** (truncated WORKER_RESULT on stdout exercising `extract_worker_result` instead of the file path) — second ingest seam, same branch family. Changes my mind: the measurement shows file-path and stdout-path classification diverging.
- **Asserting "no orphan worktree"** — tests a pruner nobody implements (1.5). Changes my mind: the pruner exists.

## 7. Open owner decisions (recommendation first)

- **Q2 — `os.abort()`: DEFER.** The parent's observation channel is `GetExitCodeProcess` via returncode on every seam; `os._exit(3)` and a native `0xC0000409` are indistinguishable to every branch under test (all read only `rc != 0`), so abort adds zero parent-side coverage. Priced anyway: if revived, WER suppression is two lines *in the stub itself* (`ctypes` `SetErrorMode(SEM_NOGPFAULTERRORBOX|SEM_FAILCRITICALERRORS)` pre-abort — per-process, no CI config) — the reason to defer is uselessness, not cost. Revive-condition: a measured death-shape gap (e.g., a future WER-hang class on real vendor crashes).
- **Q4 — the pruner: record, do not build.** The missing automatic pruner is the experiment's first finding (1.5), pre-registered in phase 3(b) with an expected-persists outcome. Post-verdict control: the SPEC-116 intake in section 8. Do not extend `route_loop._default_cleanup`'s reach or auto-invoke `cleanup-write` inside this experiment.
- **New decision surfaced — fact-3 semantics:** is a self-crash during a cancellation window *correctly* `cancelled` (operator intent dominates) or a classification-fidelity bug (crash counts leak into cancelled)? The phase-2 canary produces the evidence; the call is the owner's at verdict time. My recommendation: intended-but-documented — Windows offers no reliable signal-vs-self-exit discrimination, so "fixing" it would buy an unreliable distinction. (referência: judgment)
- **New decision surfaced — async hang reap:** whether the grandchild-orphan differential (1.3), once measured non-zero, warrants moving the async timeout reap to Job-Object termination (or KILL_ON_JOB_CLOSE at the worker job). Recommendation: yes, as the SPEC-163 amendment below — it is the cheapest true fulfillment of the w-004 trap.

## 8. Amendment targets (SPEC-116 door, named exactly)

**Now (probe phase — no spec, by law):** `docs/EXPERIMENT_METHODOLOGY.md:48-56` — an `active` experiment admits only zero-behavior-change probes; the two test files land without any spec change. Registry: owner-gated `measurements[]` append to the EXP-21 entry (`.harness/state/experiments.json:439-459`), citing this plan and D043/D046 (`.harness/context/DECISIONS.md:702, :763`).

**Post-verdict controls (each requires `shipped` + measured numbers):**

1. **NEW intake** (door: *not covered* — no spec today defines the async classification tree or crash-recovery pruning; SPEC-117/118/119 numbers in code comments have no spec files beyond `specs/40-features/research-skill.md` = SPEC-119, verified by search): `specs/templates/intake-refinement.md` → new spec under `specs/40-features/` (working name `crash-recovery-classification.md`) covering the decision-tree contract, the cancellation-shadowing semantics, and the orphan-workspace pruning obligation — citing `EXP-21` and the measured duplicate/orphan numbers, per the methodology's "ordem inegociável".
2. **Versioned amendment** (door: *covered*): `specs/40-features/sandbox-manifest-honesty.md` (SPEC-163) — if the hang-reap moves to Job-Object termination on the async seam (the honest fulfillment of w-004 trap 5).
3. **Versioned amendment** (door: *covered*, only if seam containment text changes): `specs/40-features/harness-own-sandbox.md` (SPEC-151).
4. **Conditional follow-up, unchanged:** E-EFFECTID stays a backlog item (`docs/research/article-coverage-backlog.md:393`) per D043.3.

---

## Overseer verification (2026-07-27, independent of the author)

Six load-bearing claims re-checked in source before accepting this plan:

| claim | verdict | evidence |
|---|---|---|
| 1.2 — the brief's hang-mode claim is false | **CONFIRMED, and it was my error.** Hang is child behaviour; a stub blocks as well as an instrumented entrypoint. | reasoning, plus the dossier omitting hang by choice (`:52-53`), not by capability |
| 1.3 — async reaps pid-only, bounded tree-kills | **CONFIRMED** | `async_runtime.py:485-489` → `safe_signal_pid`; `processes.signal_pid_group` docstring says *"without scanning for descendants… callers that need grandchild cleanup should use `signal_process_tree`"*; bounded uses `signal_process_tree` at `processes.py:606-610` |
| 1.3 — no KILL_ON_JOB_CLOSE | **CONFIRMED** | `DEFAULT_JOB_LIMITS` = `activeProcesses` + `jobMemoryBytes` only (`sandbox_spawn.py:42-43`); three separate comments state the no-kill-on-close design (`async_runtime.py:894`, `processes.py:444`, `:456`) |
| 2.6 — exit code 259 is a real trap | **CONFIRMED** | `pid_alive` sets `STILL_ACTIVE = 259` and returns `code.value == STILL_ACTIVE`; a process exiting 259 reads as alive forever |
| 1.5 — no automatic pruner exists | **CONFIRMED** | `tools/prune_worktrees.py` docstring: *"One-shot pruner for dead git worktree **admin dirs**"*; `cleanup-write`/`cleanup-worktrees` appear only as `--force` CLI registrations; `workflow_async_recover` body has zero matches for workspace/worktree/rmtree/prune |
| 2.1 — gate wiring costs zero lines | **CONFIRMED** | `spec_test_gate.py` is **1659** lines against the `< 1660` gs-7 ceiling; scenarios are glob-discovered |

Not re-verified by the overseer, carried at the author's confidence: the phase-1
branch-fingerprint assertion set, the executor-registration mechanism's residue
analysis, and the SPEC-116 door classification in section 8.
