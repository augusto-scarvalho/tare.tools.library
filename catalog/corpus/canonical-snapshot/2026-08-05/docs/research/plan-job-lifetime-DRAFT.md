# Per-task process-tree lifetime — CONSOLIDATED PLAN (supersedes all prior drafts)

Author: `planner-xhigh` spawn (Fable, effort `xhigh`), 2026-07-27, over three
review rounds. Read-only run; written to disk by the overseer. Supersedes the
original plan and its delta, both of which lived at this path.

Governing principle: **D045** (`.harness/context/DECISIONS.md:741-754`, owner,
2026-07-21) — never regress, never level down, declare the gap, pursue parity
when it pays. This plan is that ratified decision applied to *who dies when a
task is killed*. Overseer verification of the load-bearing claims is at the end.

---

## 1. The settled core (accepted across review; restated standalone)

1. **The lifetime axis is per-CHILD and seam-keyed, not per-profile and not `risk`-keyed.** One real worker tree simultaneously holds members that must die with the task (MCP servers, shell tool children) and members that exist to outlive it (a `gate-staged` runner via `launch_detached`, `gate_staged.py:107`; a nested supervisor, `async_runtime.py:897`). No profile boolean can split a tree; `risk` already drives sandbox tier and routing and must not be overloaded. The declaration the owner asked "where to put" already exists in code as **which spawn primitive creates the child**. No new profile field; the per-spawn opt-out is the existing `job_limits=None` (`sandbox_spawn.py:41,:350`).
2. **Determinism (the owner's "o modelo decide?" objection, answered):** the model never decides — or even declares — lifetime. It decides *what to run*; the kernel assigns the lifetime class by **inheritance**: every child, grandchild, or process nobody anticipated is born inside the task's cage (Job Object on nt, session on POSIX) because its parent was. Default = caged, enforced by the OS with zero harness bookkeeping. The only exit is a fixed harness code path — `launch_detached` / the supervisor spawn — whose semantics never vary per call. Deterministic, child-aware, zero micro-decisions accumulating on the worker.
3. **`KILL_ON_JOB_CLOSE` is rejected everywhere.** It couples worker lifetime to handle lifetime; a supervisor crash would close handles and kill every in-flight worker — destroying exactly the work `workflow_async_recover` salvages (`async_runtime.py:314-320`). SPEC-163 invariant 7 (`sandbox-manifest-honesty.md:61-63`) currently names it as an acceptable mechanism; that parenthetical is struck (section 4). `TerminateJobObject` at the kill decision is the correct primitive.
4. **Two pid-only kill sites on the async seam**, not one: the timeout reap (`async_runtime.py:485-489`, job handle in scope) and `workflow_cancel.terminate_pid` (`:984,:991`, different process, unnamed job unreachable). Both covered below.
5. **Measure-before-control binds** (EXP-21 `active`; `docs/EXPERIMENT_METHODOLOGY.md:48-56`). Two measurements were being conflated: **mechanism** (a grandchild CAN survive — already measured) and **incidence** (real vendor workers DO leave one — unmeasured). The stub differential manufactures its own orphan (rate = 1 by construction) and cannot output zero, so it is demoted to regression check; the decider is probe P1 (section 3).

## 2. The policy, stated symmetrically

> **The task's cage is the session (POSIX) / the Job Object (nt). Everything born inside it dies at the task's timeout kill. The one exit is the detached primitive — `start_new_session=True` today, `CREATE_BREAKAWAY_FROM_JOB` as its missing Windows twin — which is harness code, not a per-child judgment. Operator cancel is deliberately more aggressive (visible-tree kill): a human "stop this" outranks a background child's plans. Every reach difference between OS/seam is DECLARED machine-readably and audited (section 4), and every gap is an evolve-UP item or an intentional difference — never a subtraction (D045).**

POSIX already ships the timeout half: async workers spawn via `process_group_kwargs()` (`async_runtime.py:419` → `processes.py:248` `start_new_session=True`), so `killpg` reaps the cage and only a deliberate new session escapes — which `launch_detached` takes through the same function (`processes.py:265`). Windows is where the policy is silently not honored: `CREATE_NEW_PROCESS_GROUP` affects Ctrl-C only; the async kill is pid-only; detached children stay in the parent's job. The control is nt catching up to shipped POSIX semantics — evolve-up, per D045.

## 3. The measurement — probe P1, the decider (owner-run, zero repo code)

**Population (verified):** MCP grandchildren exist only when a workflow carries a `target` whose `graphify-out/targets/<t>/adapter/mcp-config.json` exists (`harness.py:1427-1439`); none exists on disk today, so the MCP class is a future-live population — claude-only (`codex`'s template has no MCP wiring; its `--sandbox {sandbox}` runs its own sandboxed tool children, a second live tool-child shape). Tool children are live today on both vendors. The three `type: http` executors have no children (measured NEGATIVE).

**Arms: 2 vendors × 2 seams** (claude/codex × async/bounded), ×3 repetitions, on this nt machine. Per arm: 1-worker workflow, small `workerTimeoutSeconds` (~60), prompt instructing the agent to run a long *silent* command (`python -c "import time;time.sleep(600)"`) via its own shell tool; claude arms additionally carry a fabricated probe target mcp-config naming one real stdio server (the spawn is fully vendor-real; only the config file is fabricated, deleted after). Before the timeout: snapshot the task pid's descendant closure via PowerShell `Get-CimInstance Win32_Process`, classifying each pid `mcp | tool-child | vendor-internal`. After settle: re-snapshot; **survivors = orphans, per class per vendor per seam.** Kill leftovers. Bounded arms are the control (expect zero); a bounded survivor is a separate new finding.

**Pre-registered expectations (so either result is believed):** MCP class likely 0 — stdio children self-reap on stdin EOF when the vendor dies; tool-child class likely ≥1 — a silent sleeper never reads its dead pipe. Codex may differ (its sandbox may reap its own children). (referência: judgment; the probe exists to test it.)

**Decision rule, committed before running:**
- **Zero across both vendors and all classes, all repetitions → the control is DEAD.** Owner appends the zero to EXP-21 `measurements[]`; a dossier note records "vendor children self-reap via stdio EOF at measured incidence zero"; the declaration (section 4) still lands and permanently shows async-nt reach = `pid` as a declared, intentional-until-reopen gap. Reopen triggers: the first production MCP target config, or any vendor/tool whose children hold no stdio tether.
- **Any nonzero on async with bounded zero → control justified**; number to `measurements[]`, verdict `shipped`, sections 5-6 proceed.

**Why nt-only is sufficient to decide:** every line of the control diff is nt-gated; the POSIX side ships zero behavior change — POSIX is the *reference semantics being copied*, in production for months. A probe cannot justify or kill a diff that does not exist on its OS. The POSIX-side items are separate evolve-up rows with their own checks, exercised by the real CI matrix.

## 4. The declaration — SPEC-163 extension `treeKillReach` (landable NOW, before P1 concludes)

**Where:** the sandbox manifest. Not a new surface — the third column of a discipline SPEC-163 already ratified: `*Enforced` = host capability, `*Applied` = per-spawn application fact, and now **reach** = what the owner's kill decision would actually hit. The shelf has precedent for scope qualifiers: `procAppliedScope="parent-process-lifetime"` (`harness.py:2580`, in `MANIFEST_KEYS` at `sandbox_spawn.py:224-226`).

**What:** `treeKillReach: "job" | "session" | "tree" | "pid" | "none"` — a deterministic pure function of (seam mode, `os.name`, job-assigned), ~10 lines in `sandbox_spawn.py`, stamped into the receipt where each seam already stamps `procApplied` (bounded `sandbox_spawn.py:357`; async `async_runtime.py:447`; detached `harness.py:2571` → `"none"`, since nothing kills a detached spawn; its frontier is the recover sweep). `MANIFEST_KEYS` gains the key. Declared matrix at landing time — today's truth, disparities visible on purpose:

| seam | nt | linux | darwin |
|---|---|---|---|
| bounded | `tree` (taskkill /T) | `tree` (killpg + /proc walk) | `session` (killpg; no /proc) |
| async | **`pid`** (the defect, now declared) | `session` | `session` |
| detached | `none` | `none` | `none` |

**The honesty check (the teeth):** extend `testing/scenarios/hsb_sandbox_spawn.py` (existing, glob-discovered — zero `spec_test_gate.py` lines against the 1659/1660 gs-7 ceiling) with the matrix assertion: a spawn on each reachable seam must stamp exactly the matrix value for the running OS. CI's three-OS matrix runs all three columns. When Phase C changes the async-nt kill to job-scoped, this check FORCES the declaration update in the same commit (red otherwise) — declaration and code cannot drift. Behavioral reach is proven by exp21-8 (section 5); the two are complementary teeth.

**Phase-law argument for landing early:** this is exactly the SPEC-163 Phase-1 shape — "no behavior change, the manifest stops overstating" — a measurement/honesty artifact, admissible under the `active` EXP-21 the same way `procApplied:false` was. It lands as a versioned amendment to a covered spec, bundled with the **invariant-7 strike**. Landing it before P1 strengthens the probe: P1's expected values become declared values.

## 5. The control — conditional on P1 nonzero, one commit, nt-only behavior change

1. `processes.py`: new `terminate_win_job(handle, exit_code=15) -> bool` — ctypes `TerminateJobObject`, no-op/False off nt or falsy handle (mirrors `close_win_handle:434-440`). ~10 lines. Exit code 15 matches today's kill forensics; classification is unaffected (the `timed_out` flag, not rc, lands `timeout` at `:559-562`).
2. `async_runtime.py:485-489` (timeout): nt with `async_job` → `terminate_win_job(async_job)` as the kill; else the current `safe_signal_pid` ladder unchanged (POSIX; nt job-assign-failed corner). `await proc.wait()` completes; the `finally:497` still closes the handle. ~4 lines.
3. `async_runtime.py:984,:991` (cancel): swap `safe_signal_pid` → `processes.signal_process_tree`. The job is unreachable cross-process (unnamed); `taskkill /T` on a live pid is the primitive bounded already trusts; POSIX semantics preserved. 2 words. Cancel's aggressive reach is the **intentional** operator-kill policy of section 2, declared in the amendment; the precision upgrade path is row B4.
4. **Breakaway — the nt twin of `setsid`, in-increment as OS parity (D045 rule 1: the control must not regress nt's detached seam below POSIX's):** `DEFAULT_JOB_LIMITS` gains `"breakawayOk": True` mapped to `JOB_OBJECT_LIMIT_BREAKAWAY_OK` (0x800) in `_win_job_set_limits` (`processes.py:334-341`, ~3 lines); the two detached spawn sites — `launch_detached` (`processes.py:263`) and the supervisor `Popen` (`async_runtime.py:897`) — add `CREATE_BREAKAWAY_FROM_JOB` (0x01000000) with an ACCESS_DENIED (WinError 5) retry-without-flag, failing **closed to containment** (a foreign deny-breakaway job leaves the child caged-but-killable, one log line). ~5 lines each. NOT added to `process_group_kwargs()` wholesale: its worker-spawn consumers must not break out of foreign jobs. `SILENT_BREAKAWAY_OK` stays rejected (would exempt every grandchild and falsify `procApplied`).
5. Declaration update rides the same commit: async-nt row `pid → job`; the hsb matrix check enforces it.

**The falsifiable check — exp21-8**, one new section in the existing `testing/scenarios/exp21_crash_injection.py` (zero gate-wiring lines). The stub's `hang` mode (`_exp21_crash_stub.py:129-141`, `EXP21_GRANDCHILD_PID` hook shipped) gains a second grandchild spawned via the real `processes.launch_detached`. Post-timeout assertions, identical on every OS: **caged grandchild dead** (nt: job; POSIX: killpg) — red today on nt, green after, re-reds on revert; **detached grandchild alive** (nt: breakaway; POSIX: setsid), reaped by the scenario's `finally`. Arm 1's falsifiability is nt-only (POSIX already passes — recorded honestly); arm 2 is falsifiable on all three OSes and turns red if anyone ever "fixes" reaping with `KILL_ON_JOB_CLOSE` or a blanket walk.

## 6. The disparity ledger — every gap as EVOLVE-UP or INTENTIONAL (never subtraction)

The "Form A" idea (dropping Linux's descendant walk to match macOS) is rejected on D045 grounds and is additionally expensive: `signal_process_tree` has 31 call sites. Nothing below removes capability from anywhere.

| # | disparity | resolution | route |
|---|---|---|---|
| 1 | async-nt kill reach `pid` (the orphan defect) | evolve nt up to `job` (5.1-2) | **attack now** (post-P1-nonzero) |
| 2 | nt has no detached breakaway; POSIX has `setsid` | evolve nt up: `CREATE_BREAKAWAY_FROM_JOB` + `breakawayOk` (5.4) | **attack now** (same commit) |
| 3 | async cancel reach `pid` (second orphan site) | evolve up to `tree` (5.3) | **attack now** (same commit) |
| 4 | darwin `tree` reach missing at bounded/cancel: `process_children_map` reads `/proc` only | evolve darwin up: `ps -axo pid,ppid` fallback — blast radius one function (zero external callers), Linux unchanged (/proc wins), nt unchanged (early return), exercised by the macOS CI leg | **queue** (B1); recommend riding Phase C |
| 5 | **suspected darwin defect (new this pass):** `pid_alive` (`processes.py:187-193`) returns False on `FileNotFoundError` from `/proc/<pid>/stat` — correct on Linux, but darwin has no `/proc` at all, so every pid may read as dead, mis-orphaning live workers | verify on the macOS CI leg, then guard the `/proc` read (fall through to `os.kill(pid,0)` when `/proc` is absent) — one function | **queue** (B2, verify-first, elevated) |
| 6 | POSIX cage is escapable by a child's own `setsid`; the nt job is deny-able and stronger | **intentional platform ceiling**, declared: closing it is cgroup/PID-namespace territory | **queue** (B3, distant) |
| 7 | cancel kills detached children (nt/linux) while timeout spares them | **intentional policy** (operator kill is aggressive), declared in the amendment | **queue** (B4, trigger-gated) |
| 8 | MCP plumbing exists only in the claude template; codex has none | vendor gap, declared | **queue** (B5) |
| 9 | detached supervisor runs uncapped (D044 option-b ceiling) | already declared (`procAppliedScope` precedent) | declared — no new row |
| 10 | http executors spawn no children | intentional no-op | declared |

## 7. Backlog rows (registerable verbatim via `tasks add --body -`)

**B1** — id `proc-darwin-descendants-walk`, S/P2 — *darwin tree-kill reach: ps-based process_children_map fallback (D045 evolve-up)*: `process_children_map` (`processes.py:89-112`) reads `/proc` and returns `{}` on darwin, so the descendants walk in `signal_process_tree` is empty there: bounded/cancel reach is `session` on macOS vs `tree` on linux/nt (declared in the SPEC-163 `treeKillReach` matrix). Evolve darwin UP: when `/proc` is absent and `os.name != "nt"`, build the PPID map from `ps -axo pid,ppid` (stdlib subprocess, ~10 lines). Blast radius: one function, zero callers outside `processes.py` (verified 2026-07-27); linux keeps the `/proc` path, nt keeps the early return. Teeth: the hsb `treeKillReach` matrix flips darwin bounded/cancel to `tree` in the same commit; the CI macos leg exercises it. Dep: land after the SPEC-163 amendment.

**B2** — id `proc-darwin-pid-alive-procfs`, S/P1 — *SUSPECTED darwin defect: `pid_alive` conflates "no /proc filesystem" with "process dead"*: `pid_alive` (`processes.py:187-193`) returns False on `FileNotFoundError` reading `/proc/<pid>/stat`. Correct on linux (entry gone = dead); darwin has no `/proc` at all, so every pid may read dead — and `workflow_async_recover` keys on it (`async_runtime.py:321`), so recover would mis-orphan LIVE workers on macOS; `supervisor_alive` (`:305`) and lock-staleness (`:1080`) read from the same function. Unverified on real darwin (source reading 2026-07-27 on an nt machine). Step 1: one CI-macos assertion that `pid_alive(os.getpid())` is True — would fail today if the defect is real. Step 2 (if confirmed): guard the `/proc` read (attempt zombie detection only when `Path("/proc").exists()`, else fall through to the existing `os.kill(pid,0)` path). One function.

**B3** — id `proc-linux-cgroup-cage`, L/P3 — *POSIX task cage that survives setsid (cgroup/PID-ns), declared platform ceiling*: the POSIX cage is the session; a child calling `setsid()` escapes `killpg`. The nt Job Object is deny-able and stronger. Closing the gap is linux-only cgroup v2 / PID-namespace territory — unjustified until a measured POSIX orphan exists. Reopen trigger: any measured setsid-escapee orphan on a POSIX host, or deployment to a linux prod runner.

**B4** — id `proc-cancel-named-jobs`, M/P3 — *precise operator-cancel reach via named Job Objects (spare detached children)*: `workflow_cancel` kills the visible tree; on nt/linux this includes breakaway/setsid detached children. Declared INTENTIONAL operator-kill policy. If ever rejected: name the per-task jobs (`Local\harness-<wfid>-<task>`), let the cancel CLI `OpenJobObject` + `TerminateJobObject` cross-process, fallback `signal_process_tree`. Trigger: first real incident of a cancel stranding a wanted detached child.

**B5** — id `vendor-codex-mcp-parity`, M/P3 — *codex MCP parity: `{mcpConfig}` plumbing exists only in the claude template (D045 vendor gap)*: `harness.py:1427-1439` renders `{mcpConfig}` for claude's `--strict-mcp-config`; codex's template has no MCP slot, so target-scoped MCP tooling is claude-only. Declared vendor disparity; evolve codex up when the first production MCP target config ships. Until then this row IS the declaration.

## 8. Phased plan

- **Phase D (declaration — now, parallel with P1):** SPEC-163 amendment part 1 (invariant-7 strike + `treeKillReach` vocabulary + today's matrix incl. the declared `pid` defect) + ~12 stamping lines + `MANIFEST_KEYS` entry + hsb matrix assertions + register B1-B5. Check: hsb/hos green on all three CI OSes. Rollback: revert one commit.
- **Phase 0 (probe P1 — owner-run, no repo code):** section 3. Acceptance: per-class/vendor/seam counts ×3 into EXP-21 `measurements[]` (owner-gated).
- **Phase Z (zero branch):** dossier note + reopen triggers; nothing else — the Phase-D declaration remains the permanent honest record of the gap. Done.
- **Phase B (nonzero):** SPEC-163 amendment part 2 — invariant 8: async kill decisions are job-scoped on nt / session-scoped on POSIX; detached breaks away on both OSes; cites EXP-21 + P1 numbers. Check: `spec-pack` green.
- **Phase C (nonzero, one commit):** section 5 diffs (~25 production lines) + exp21-8 (~45 scenario lines) + matrix update (`pid → job`, forced red-to-green by hsb). Acceptance: exp21-8 arm 1 red→green on nt, arm 2 green everywhere; exp21-1..7 untouched; suite green on POSIX. Rollback: revert the commit.
- **Phase C2 (optional, owner call):** B1 riding the same verdict batch.

## 9. What I would NOT build

`KILL_ON_JOB_CLOSE` anywhere (inverts recover salvage); a per-profile lifetime field (per-child property; 12 identical values; the feared "micro-decision chain" is what the field would create); the stub differential as decider (cannot output zero); Toolhelp32 walker or psutil (job + taskkill + B1's `ps` fallback cover every seam); passive production telemetry at the timeout branch (P1 decides; ~25 probe-admissible lines only if the owner wants an ongoing rate); `SILENT_BREAKAWAY_OK`; any Form-A subtraction (D045); the workspace-pruner track in this increment (separate metric, separate control, separate spec door).

## 10. Open owner decisions (recommendation first)

1. **Go on Phase D now** (declaration + invariant-7 strike + backlog rows, before P1 concludes). Recommend: yes — it is the M2 shape, and it makes P1's expectations declared values.
2. **Ratify P1** (2 vendors × 2 seams, decision rule and zero rule as written, pre-committed). Recommend: yes.
3. **Cancel-policy distinction** (operator kill = aggressive visible-tree, declared intentional; B4 is the precision path). Recommend: accept as stated.
4. **B1 scope call**: does widening darwin's bounded/cancel reach fall under the EXP-21 verdict (ride Phase C) or stand alone after it? Recommend: ride Phase C.
5. **B2 priority**: confirm P1 (a suspected live-correctness defect on a CI-supported OS). Recommend: yes; the verify-first step is one CI assertion.

## 11. Amendment targets (SPEC-116 door)

- **`specs/40-features/sandbox-manifest-honesty.md` (SPEC-163) — covered, versioned amendment in two parts:** part 1 (Phase D): `treeKillReach` vocabulary + matrix + invariant-7 strike; part 2 (Phase B): invariant 8, citing EXP-21 and the P1 numbers.
- **`specs/40-features/harness-own-sandbox.md` (SPEC-151) — covered; expected untouched** (verify at amendment time).
- **Not specs:** EXP-21 `measurements[]` append (owner-gated); rows B1-B5 via the tasks CLI; `DECISIONS.md` needs no new entry — this plan implements D045, it does not amend it.

---

## Overseer verification (2026-07-27, independent of the author)

| claim | verdict | evidence |
|---|---|---|
| D045 ratifies the owner's principle already | **CONFIRMED, verbatim** | `DECISIONS.md:741-754`: *"não regredir, não nivelar por baixo, declarar o gap, perseguir quando vale"* — and it names SPEC-113's `supportState` as the declaration vocabulary, generalized from vendors to OS |
| B2 — darwin `pid_alive` reads every pid as dead | **CONFIRMED AS READ** (cannot be run on this nt machine) | `processes.py:187-193`: `except FileNotFoundError: return False` on the `/proc/<pid>/stat` read; darwin has no `/proc`, so the `os.kill(pid,0)` fallback below is unreachable there |
| B2 blast radius | **CONFIRMED, and it is severe** | `workflow_process_alive` is a one-line wrapper (`async_state.py:224-225`); consumers include the orphan decision (`async_runtime.py:321`), the supervisor-alive guard (`:305`), the cancel grace loop (`:986-993`), doctor (`:1066`) and lock staleness (`:1080`) |
| the `treeKillReach` shelf has precedent | **CONFIRMED** | `MANIFEST_KEYS` (`sandbox_spawn.py:224-226`) already carries `procAppliedScope` |

Not re-verified by the overseer, carried at the author's confidence: the P1
recording procedure, the stdio-EOF self-reap mechanism (marked
`referência: judgment` by the author), and the BREAKAWAY WinAPI mechanics.

**One overseer note the owner should weigh:** D045 rule 3 names SPEC-113's
`supportState` (`native/emulated/degraded/unsupported`) as *the* declaration
vocabulary, generalized to OS. The plan proposes a new `treeKillReach` enum in
the SPEC-163 manifest instead. Both are defensible — reach is a richer fact than
a support tier — but if the owner wants one declaration vocabulary rather than
two, that is a design call to make before Phase D lands.
