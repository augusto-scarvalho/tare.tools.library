# RD-CRASH — Deterministic Crash Injection at the Adapter Boundary (Windows)

Research dossier (scanner lane, 2026-07-21), prerequisite for EXP-21
(crash-injection recovery without orphans/duplicates, ATAM A13/A6). Everything verified against source.
Persisted here so it does not live in transient memory (owner principle: structures bind the process, not
agent memory).

## (a) Exact boundary by seam

All 3 seams share the shape: **spawn → await termination → read returnCode → extract/validate
WORKER_RESULT → classify**. A crash is observed at await + the “no result / rc≠0” branch.

- **SEAM 1 bounded** (`harness.py:1511 run_one_worker`): await at `processes.py:440
  proc.communicate(timeout=...)`; parse `harness.py:1560 extract_worker_result`; downstream
  “died without receipt” classification at `harness.py:1628-1629` (`result_path.exists()` +
  `validate_worker_result`).
- **SEAM 2 async** (`async_runtime.py:351`): spawn `:431 create_subprocess_exec`; await `:448
  wait_for(proc.wait())`; decision tree `:523-561` — `:531 result_path.exists()` → validate;
  `:554 rc==0` → `missing`; `:558 else` → `failed` rc≠0 (**the crash branch**).
- **SEAM 3 detached** (`async_runtime.py:840 Popen` via `processes.py:226 launch_detached`): NO await;
  boundary is `workflow_async_recover` (`:296`) — `supervisor_alive` (:305), per task
  `not process_alive(pid)` (:321), valid result → fulfilled (:314-320), dead supervisor without result →
  `orphaned` (:329); guard :327 avoids racing its own settle.

## (b) Recommended mechanism: env-var-gated stub worker (merges 3a+3b)

Existing pattern: `testing/scenarios/_rt6_stub_worker.py` spawned through the real seam using executor
`commandTemplate`. A sibling `_exp21_crash_stub.py` reads `HARNESS_CRASH_AT` and crashes at a point in
its **own code**:
- `pre_result` → `sys.exit(3)` before WORKER_RESULT → async:558 (rc≠0 without receipt), A13
  “crash-before-receipt”.
- `exit0_no_result` → `sys.exit(0)` without receipt → async:554 (`missing`).
- `post_result` → write valid result, then `sys.exit(3)` → idempotency (recover marks fulfilled without
  re-spawn).
- `partial_write` → truncated JSON → `validate_worker_result` rejects it.

**Deterministic on Windows** because the crash point is a LINE in the worker flow, triggered by env var —
no scheduler race; `sys.exit(rc≠0)` produces a clean stable return code read identically by parent
`wait()`/`communicate()` in all 3 seams, reproducible in CI. Worker is a real child of the real seam (no mock).

**Variant** `os.abort()` (hard native crash, 0xC0000409): downgraded because return code is less clean for
assertion AND it triggers Windows Error Reporting — CI would require `SEM_NOGPFAULTERRORBOX`/SetErrorMode.
`sys.exit` is the default.

**Rejected:** (1) killing the tree with `signal_process_tree` at a point chosen by the PARENT = timing race
(parent does not know when to kill) — retained ONLY for SEAM 3, and even there deterministic only with a
**sentinel-file gate** (worker writes sentinel; test waits; then kills supervisor). (2) timeout as crash proxy =
already covered and tests timing, not A13.

## (c) Orphan/duplicate detection (verifiable seams)

**No orphans:** registered pids (`task["pid"]`, `group["supervisorPid"]`) →
`processes.pid_alive(pid) is False` (`:135`, nt via OpenProcess — Windows has no /proc, so registered pid is
the seam). `git worktree list` clean (write worker uses `controlled_writes.create_temp_workspace :189`).
Locks/holds: `.harness/workflows/active` + `workflow_lock_path` + `scenario_isolation._recover_stale_holds
:248` (N3/F2 branch :280 refuses live pid, recovers dead pid). Group settled after `workflow_async_recover`.

**No duplicates:** idempotency is already encoded by `result_path.exists()` (failover `:585`; recover
`:314-320` marks fulfilled without re-spawn). Prove: `post_result` + recover → result written exactly once
(stable mtime); external effect once even with re-spawn; `_record_executor_outcome :336` records once in
breaker (:343 guarantees no-double-count).

## (d) EXP-21 skeleton

`testing/scenarios/exp21_crash_injection.py` (+ `_exp21_crash_stub.py`, `_` prefix outside gate glob): for
each seam × phase → construct one-worker WF with executor=crash-stub, run through REAL seam, assert
classification, run recover (assert idempotency), assert no orphans (pid/worktree/hold/settle) and no
duplicates (effect once, stable mtime, breaker count 1), self-check in `__main__`.

## Open questions BEFORE coding EXP-21 (owner-gated)

1. **[POSSIBLE PREREQUISITE] Effect ledger to count duplicates.** There is no explicit unique-effect counter
   in code — test would use result-file mtime + record refs. Is that sufficient, OR does EXP-21 require the
   enabler **E-EFFECTID** (idempotency key, `article-coverage-backlog.md:393`) FIRST? Sequencing decision.
2. `sys.exit(3)` default vs `os.abort` variant (native crash) — include in EXP-21 or leave for later?
   Confirm WER suppression in CI.
3. SEAM 3 determinism: supervisor kill needs sentinel gate + `signal_process_tree`. Does that count as
   “deterministic,” or is A13 targeting only bounded+async (100% code-local worker crash, zero external signal)?
4. Who prunes temp workspace/worktree of a worker killed before merge (R1 pruner)? That is what the
   “no orphaned worktree” assertion verifies.
5. **Primary A13 target:** all 3 seams parameterized, or only async boundary (hottest production path)?

## Recommendation (architect)

Mechanism (b) is ready to code for bounded+async with NO new prerequisite — crash is 100% in worker code
and idempotency via `result_path.exists()` already exists. Question 1 (E-EFFECTID) only affects the “no
duplicate” assertion if we want a STRONG counter rather than mtime+refs; for a first measure-only EXP-21,
mtime+refs are enough and E-EFFECTID becomes follow-up if measurement shows ambiguity. SEAM 3 (detached)
is the only one that needs sentinel gate — propose EXP-21 phase 1 = bounded+async (pure determinism), SEAM 3
= phase 2 with sentinel.
