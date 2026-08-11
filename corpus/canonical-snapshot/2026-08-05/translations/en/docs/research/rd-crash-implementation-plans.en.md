# Implementation Plans — Deterministic Crash Injection (RD-CRASH)

Parked in the backlog. Derived from `rd-crash-injection-round.md` (5 NVIDIA ideators) + D022.
Enables **EXP-21** (measure recovery: duplicate-effect, orphaned-work, time-to-resume) + the recovery
fixture. Windows-real (no POSIX SIGKILL/SIGSEGV).

**Reuse:** `scripts/harness_lib/processes.py` (subprocess spawn — propagates env); `sandbox_spawn.py`
(the SPEC-151 Job Object — kills hang mode); circuit breaker + gate-hold auto-recovery (already react);
secret scan (scrub truncated stdout). Analogy: SQLite crash VFS + Chaos Monkey + circuit breaker/fuse.

---

## N-CRASH-INJECTOR — hybrid injector · BUILDABLE (test infra, with EXP-21) · size M

**Goal:** crash the worker DETERMINISTICALLY and reproducibly on Windows, covering 4 opt-in modes
(EXP-21/fixture only, NEVER production). It is measurement-supporting test infrastructure — buildable
when the owner opens EXP-21 (the measurement itself is owner-gated).

**Approach (hybrid, D022):**
- **Cooperative via `HARNESS_CRASH_AT` env** INSIDE the worker (modes a/c/d — only cooperative injection
guarantees the EXACT point; external kill races pipe flush):
  - (a) abrupt: `abrupt:call=N` → `os._exit()` on call N, no flush.
  - (c) truncated: `partial:bytes=K` → write K stdout bytes, then `os._exit()` (JSON cut in the middle).
  - (d) dirty exit: `dirty:code=N` → non-zero `sys.exit(N)` + stderr.
- **External kill through Job Object** (the sandbox_spawn one) only for (b) hang: `hang:after=N` → block
forever → parent Job Object reaps it on timeout.
- **COUNTER-based triggers, never probabilistic** (contrast with Linux kernel FAIL_MAKE_REQUEST).
- **Guard lives at the worker ENTRYPOINT** (reads `HARNESS_CRASH_AT` at startup — ZERO cost without env).
`processes.py` only PROPAGATES the env (~3 lines). `sandbox_spawn.py` does NOT change (only supplies Job Object).

**Mandatory traps (w-004):** exit codes MUST NOT collide with `0xC0000005` (access violation) — otherwise
the parent mistakes a FAKE crash for a real OS fault; **scrub truncated stdout** (it may contain a partial
secret — reuse secret scan); env scoped to the SPECIFIC subprocess (Windows inherits env → otherwise ALL
workers crash); truncation INSIDE `maxWorkerOutputChars` (otherwise recovery cannot distinguish crash from
oversize rejection); mode (b) kill goes through the Job Object (kills the process tree), not TerminateProcess
on one PID.

**Footprint (when opened):** cooperative `HARNESS_CRASH_AT` module at the worker entrypoint + ~3-line
propagation in `processes.py` + recovery fixture; scenario (each mode triggers deterministically; parent
SURVIVES and recovers; guard off without env).

**Acceptance:** each of the 4 modes crashes at the exact reproducible point; parent harness survives +
recovers; without `HARNESS_CRASH_AT` the guard is a no-op (zero production cost); exit codes do not collide
with OS codes.

**Gate:** buildable test infra WHEN owner opens EXP-21 (only makes sense WITH measurement). EXP-21
(recovery measurement) remains OWNER-GATED. **Dependency:** processes.py + sandbox_spawn (exist). **Size:** M.

---

## N-CRASH-EXP21 — recovery measurement · OWNER-GATED · size M

**Goal:** with the injector, measure duplicate-effect / orphaned-work / time-to-resume for each crash mode — EXP-21.

**Approach:** trigger each N-CRASH-INJECTOR mode in a controlled WF and measure: duplicated effect
(did task run twice?), orphaned work (did killed worker leave garbage?), time-to-resume (how long until
existing gate-hold auto-recovery resumed?). Reuse the breaker + gate-hold that already react.

**Footprint (when opened):** register EXP-21; run injector + measure through event log + existing recovery.
**Acceptance:** table `(crash mode) → (duplicate-effect, orphaned-work, time-to-resume)`.
**Gate:** OWNER-GATED (measurement). **Dependency:** N-CRASH-INJECTOR. **Size:** M.

---

## Suggested order
1. **N-CRASH-INJECTOR** — test infrastructure; build when owner opens EXP-21 (not earlier — without the
   measurement, the injector is code with no consumer).
2. **N-CRASH-EXP21** — owner-gated recovery measurement immediately afterward.

> Note: a probabilistic injector is rejected — EXP-21 needs DETERMINISM (Linux kernel
> FAIL_MAKE_REQUEST is the counterexample).
