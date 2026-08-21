# RD-CRASH Round — Deterministic Crash Injection at the Adapter Boundary (Windows)

Research-gated backlog item RD-CRASH. Second of 3 implementation-research rounds (owner 2026-07-19).
Orchestrator = this session. Divergence via **NVIDIA** (`nvidia-compat`, glm-5.2).

## Why this round exists

**EXP-21** (measure recovery: duplicate-effect, orphaned work, time-to-resume) and the recovery fixture need
a way to MAKE the worker/adapter crash **deterministically and reproducibly** — otherwise recovery
measurement is flaky (a crash that only sometimes happens is not an experiment). The harness runs on
**Windows** (PowerShell + subprocess), where POSIX signals (SIGKILL/SIGSEGV) do not work the same way.
Research on HOW TO IMPLEMENT the injector, not measurement.

## Round question

> How do we inject a **deterministic, reproducible** crash at the harness adapter/worker boundary on
> **Windows** (subprocess created via `harness_lib/processes.py` / `sandbox_spawn.py`) so EXP-21 can measure
> recovery without flakiness — covering the crash modes that matter (abrupt process death, hang/timeout,
> partial/truncated output, non-zero exit code) without contaminating the parent harness?

## Success criteria

- **Actors:** EXP-21 (triggers crash at a controlled point and measures recovery), recovery fixture
  (regression), parent harness (must survive + recover).
- **Deterministic:** same trigger produces same crash at same point — “crash on call N” or “crash after
  emitting K bytes,” not random kill.
- **Windows-real:** works with Windows process model (no dependence on POSIX SIGKILL/SIGSEGV). Reuses
  subprocess/Job Object already created by `sandbox_spawn` (SPEC-148/151).
- **Covers relevant modes:** (a) abrupt death (process disappears), (b) hang (never returns → timeout),
  (c) partial output (stdout truncated in middle of WORKER_RESULT), (d) dirty exit code. Each exercises a
  different recovery path.
- **Does not contaminate:** crash remains CONTAINED in worker; parent harness does not die, injector is
  opt-in (only EXP-21/fixture, never production). Reuses breaker + existing gate-hold auto-recovery.

## Budget + breadth + declared design

- **Wave 1:** 5 NVIDIA ideators, ceiling ~65k tokens (free tier). Gate at 60%.
- **Breadth (D010): EXPLORATORY → 5.** Fault injection crosses chaos engineering, Windows process model
  (Job Objects, TerminateProcess, exit codes), deterministic test seams/fault points, and signal emulation —
  broad technical field.
- **Design (L18):** round FEEDS EXP-21 (owner-gated recovery measurement). Candidate method card
  (advisory fires post-e5a1a4b): crash/recovery family has no own card yet; EXP-21 experimental design uses
  noise floor + matched controls. Final card enters synthesis.

## Phase 3 — wave-1 brief

> Design the deterministic crash-injection mechanism at the harness adapter/worker boundary on Windows. The
> harness creates workers through subprocess (Python/PowerShell, with sandbox_spawn SPEC-148/151 Job Object).
> It must: (1) be DETERMINISTIC — same trigger crashes at same point (e.g. “dies on call N,” “dies after K
> stdout bytes”), reproducible across runs; (2) work in WINDOWS process model without POSIX
> SIGKILL/SIGSEGV (use TerminateProcess/Job Object/exit codes, or a cooperative fault point inside worker via
> env var); (3) cover 4 modes: abrupt death, hang/timeout, partial/truncated output, dirty exit code — each
> exercises a different recovery path; (4) remain CONTAINED (parent harness survives and recovers) and be
> opt-in (EXP-21/fixture only, never production); (5) reuse existing breaker + gate-hold auto-recovery +
> sandbox Job Object. Deliver: MECHANISM (cooperative env fault point vs external Job Object kill — trade-off),
> deterministic triggering of all 4 modes, and exact instrumentation point in processes.py/sandbox_spawn.py.

---

# Phases 3–5 — Result and Synthesis (RD-CRASH)

Wave 1: `WF-20260719-055620-000806`, 5 NVIDIA ideators (glm-5.2).

## Independent convergence

**Mechanism = HYBRID** (w-001, w-003, w-004, w-005 converge):
- **COOPERATIVE fault point via `HARNESS_CRASH_AT` env** INSIDE worker for modes (a) abrupt death,
  (c) truncation, (d) dirty exit — because only cooperative injection guarantees the EXACT POINT. Hard
  technical reason (w-002): an EXTERNAL kill does **not** guarantee truncation in the middle of JSON — OS
  may flush pipe buffer before TerminateProcess lands. Determinism requires worker to kill itself at point.
- **EXTERNAL kill via Job Object** (sandbox_spawn SPEC-151) only for (b) hang — a hung worker cannot kill
  itself; parent Job Object reaps it at timeout. Zero new process runtime.

**Deterministic triggers — ALL counter-based, never probabilistic** (w-005 explicitly contrasts Linux
kernel probabilistic `FAIL_MAKE_REQUEST`):

| mode | trigger | worker action |
|---|---|---|
| (a) abrupt | `HARNESS_CRASH_AT=abrupt:call=N` | `os._exit()`/`os.abort()` on call N, no flush |
| (b) hang | `HARNESS_CRASH_AT=hang:after=N` | block forever → parent Job Object kills on timeout |
| (c) truncated | `HARNESS_CRASH_AT=partial:bytes=K` | write K stdout bytes, then `os._exit()` — JSON cut in middle |
| (d) dirty exit | `HARNESS_CRASH_AT=dirty:code=N` | non-zero `sys.exit(N)` + stderr |

## Instrumentation point — tension exposed (and resolved) by round

Workers DISAGREED on guard ownership (honest signal):
- w-002: “processes.py is PRODUCTION path — instrumenting there leaks crash logic into production.”
  w-003: “worker bootstrap, NOT processes.py.”
- **Resolution (synthesis):** cooperative crash lives in **worker entrypoint** (reads `HARNESS_CRASH_AT`
  at startup — self-contained, ZERO cost when env absent). `processes.py` only **propagates** env var
  (~3 lines) and reads exit/stdout as it already does. `sandbox_spawn.py` **does not change** — only supplies
  Job Object for mode (b). This satisfies w-002 (no crash logic in shared production path) AND “NEVER in
  production” (guarded by absence of env).

## Real traps (w-004 security + w-002 scale)

- **Exit codes (w-004):** mode (d) MUST NOT collide with real Windows failure codes (e.g.
  `0xC0000005` = access violation) — otherwise parent reads FAKE crash as real OS failure. Use reserved,
  non-colliding harness codes.
- **Truncated scrub (w-004):** mode (c) cuts stdout in middle of JSON, which may contain PARTIAL secret
  field — parent MUST NOT persist raw truncated buffer; scrub before logging. Reuse existing secret scan.
- **Env scoping (w-002):** Windows inherits env by default — `HARNESS_CRASH_AT` in PARENT process would
  crash ALL parallel workers. Must be scoped to env dict of SPECIFIC subprocess, never parent.
- **maxWorkerOutputChars (w-002):** truncation point in mode (c) must be INSIDE limit, otherwise recovery
  cannot distinguish crash-truncation from normal oversize rejection.
- **Job Object in mode (b) (w-004):** external kill must go through Job Object (kills entire tree), not
  TerminateProcess directly on worker PID.

## Proven analogies (w-005)

- **SQLite crash-injection VFS shim** (`sqlite3_crash.c` intercepts I/O at deterministic offsets) =
  cooperative fault point at byte K. Strong reference (SQLite crash testing is legendary).
- **Netflix Chaos Monkey** opt-in by flag, test environment only = `HARNESS_CRASH_AT` gate (never production).
- **Circuit breaker + electrical fuse:** breaker protects upstream (parent), fuse is deliberate failure
  (worker) — maps to existing breaker.

## Operation

| card | operation | why |
|---|---|---|
| **CRASH-HYBRID** (cooperative a/c/d + Job-Object b) | **kept** — core | only hybrid covers all 4 modes with real determinism |
| **CRASH-COOP-WORKER** (guard in worker entrypoint) | **kept** | keeps crash logic OUT of production path (resolves w-002/w-003 tension) |
| **non-colliding exit code + truncated scrub** | **split (security rules)** | fold into injector spec; w-004 finding |
| **probabilistic injector** | **rejected** | EXP-21 needs determinism; probabilistic Linux-kernel pattern is anti-pattern here |

## Buildable vs owner-gated

- **Buildable (test infrastructure) when owner opens EXP-21:** cooperative `HARNESS_CRASH_AT` module in
  worker entrypoint + 3-line propagation in processes.py + recovery fixture. Opt-in test tooling, zero prod
  cost. But only useful WITH measurement.
- **Owner-gated:** EXP-21 itself (measure duplicate-effect/orphaned-work/time-to-resume) was already
  owner-gated. RD-CRASH supplies injector it needs.

## Traceability

| Evidence | Idea | Experiment | Task | Status |
|---|---|---|---|---|
| 4/5 (hybrid) + w-002 (flush race) + SQLite VFS (w-005) | CRASH-HYBRID + CRASH-COOP-WORKER | enables EXP-21 | RD-CRASH→injector | designed (build with EXP-21, owner-gated) |
| w-004 (exit-code/scrub/Job-Object) | injector security rules | — | part of spec | designed |
