# Round R2 — Harness-owned sandbox (design round)

Round 2 of 5 under directive **D012** (NVIDIA, sequential, backlog-first). P0 from the article queue. Phase-2 human gate pre-approved by D012.

## Phase 0 — Question, criteria, budget, breadth

- **Question:** what vendor-agnostic fs/proc/net containment design at SPAWN (the "runtime plane" §5.9; layer s5 of the defense stack §7.4; CaMeL separation of trusted-control/untrusted-data) makes open-model workers safe (HTTP, zero built-in containment) while STRENGTHENING Claude (deny honored) and Codex (native S3 sandbox), on single-tenant Windows 11, without breaking live flows (workflows, rooms, gate)?
- **Hard context (from the Codex investigation on 2026-07-18, adoption round document):** containment matrix — Claude: deny hooks ✅; Codex: hooks are ADVISORY (deny ignored), native sandbox is the only trusted control; open models: NOTHING. Already-committed building block: `apply_patch_paths` parser (a feed of what the worker tries to write). Related deferred items: generic egress is declare-only (rule 27), Bash is not path-confined, raw HTTP workers.
- **Success criteria:** (a) covers all 3 vendors with ONE declared semantics (native/emulated/degraded per capability — C3 vocabulary); (b) REAL enforcement for the open-model case (not advisory); (c) Windows-first (no chroot; available primitives: AppContainer/Job Objects/restricted tokens/firewall rules/worktree+ACL); (d) integrates at the 3 existing spawn points without rewriting executors; (e) deterministic test plan (red-team escape fixture).
- **Breadth (D010): EXPLORATORY — 5 ideators** (full research-divergence). Rationale: open design space (OS-level vs process-level vs proxy-level vs fs-overlay), multiple possible sources, no closed implementation target — exactly D010 case (b); nominal diversity pays off (Diehl & Stroebe).
- **Declared budget:** divergence wave ≤ 40k tokens + seeded critique wave ≤ 30k (4 critics). Executor `nvidia-compat`. Prompt-cap override expected (embedded content, D012 — R1 precedent).
- **Declared design (L18):** the round produces DESIGN + a NEW spec door (it is not a measurement experiment); the escape fixture cited in the criteria will use the red-team/fault-injection card when implemented.

## Execution

- Divergence: `WF-20260718-220802-675372` (5 ideators, GLM, 5/5 valid, 15 concepts). Natural convergence on 5 primitives: Job Object, WFP/netsh (egress), restricted token, NTFS ACL, `sys.audit` hook.
- Seeded critique: `WF-20260718-221100-955934` (4 critics). INVALID under the transport contract (they hallucinated paths in `sourceFilesVerified` — this is design for something that does not exist, so there is no real file to cite; lesson: DESIGN critique should not require `sourceFilesVerified`). Content extracted directly from results — consistent across the 4 critics, with no material contradiction. `securityBlockerBlocksWorkflow` did not trigger because the wave became invalid before reduce, but 3 critics raised a security `blocker` about the SAME issue (egress) — treated as a design blocker below.

## Design portfolio (locally audited; Windows primitives verified)

Local verification of the primitives (marked `[repo]/[judgment]`):
- Job Object via ctypes `CreateJobObjectW`/`AssignProcessToJobObject` + `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` — `[judgment]` stable Win32 API, no admin required, kills the process tree on close. Reference: Microsoft Job Objects docs.
- NTFS ACL via `icacls` (subprocess) — `[judgment]` deny-write ACE on scoped paths, allow only in result/worktree; no admin if the user owns the directory.
- WFP (`FwpmEngineOpen`…) — `[judgment]` kernel-enforced but requires admin + driver; rejected by the security critic for the common case.
- `netsh advfirewall` — `[judgment]` user-mode, but the rule is PER IMAGE PATH, not per PID → advisory-by-image, not per-process containment.
- `sys.addaudithook` (stdlib) — `[repo]` available since Python 3.8+; intercepts `open`/`socket`/`subprocess` INSIDE the Python worker, but the worker is a child process (it does not trust itself) → observability, not enforcement.

### Core (the design that closes P0)
| card | primitive | covers | strength | where |
|---|---|---|---|---|
| **SB-1 Job Object baseline** | ctypes Job Object + KILL_ON_JOB_CLOSE, BREAKAWAY_OK=0 | all 3 vendors (wraps spawn) | real-block (lifecycle/process tree), no admin | all 3 spawn seams |
| **SB-2 NTFS ACL fs confinement** | `icacls` deny-write in scope + allow in result; dual mode (read worker = scope read-only + writable result; write worker = dedicated worktree) | all 3 vendors | real-block (writes), no admin | spawn wrapper, post-worktree |
| **SB-3 confinement manifest + readable degradation** | `{fsEnforced, egressEnforced, reason}` field recorded per spawn; capability probe at workflow start | all 3 | honest declaration | async_state/records |

### Contingency (egress — the hard, admin-dependent point)
| card | primitive | critique verdict |
|---|---|---|
| SB-4 WFP per-spawn egress | FwpmEngine (admin+driver) | real-block, but admin-only — use only when elevated; degrade to SB-5 |
| SB-5 netsh firewall by image path | `netsh advfirewall` (user-mode) | advisory-by-image, crash-safe teardown mandatory (`SetConsoleCtrlHandler` + `atexit`, idempotent name) |
| SB-6 CaMeL capability-token gate | token in worker | **RECLASSIFIED**: defense-in-depth/observability, NEVER the primary egress boundary (3 critics agree) |

### Boundary / detection
- SB-7 post-execution reconciliation (already-committed `apply_patch_paths` + worktree diff) = detection; complements but does NOT replace pre-spawn containment.

### Operations by card (set-based)
SB-1 **kept** (foundation, unanimous) · SB-2 **kept** (dual mode solves the "do not break write worker" concern) · SB-3 **kept** (this is the readable-degradation requirement) · SB-4 **experiment/deferred** (admin-only; gated) · SB-5 **simplified** (accepted as a readable-degradation layer, not the boundary) · SB-6 **rejected as enforcement**, retained as observability · SB-7 **kept** as detection.

**Honest design blocker (the same ceiling the article has):** real per-process egress blocking on Windows WITHOUT admin is not available in stdlib — a trusted network boundary requires WFP (admin). For an HTTP open-model worker, the TRUSTED control available today is: **deny spawn** when egress cannot be confined AND the task requires network, OR run under SB-1+SB-2 with declared `egressEnforced:false` + SB-5 advisory + SB-7 detection. This is the honest way to close P0; kernel egress remains behind the admin trigger.

## Delivery — intake prepared (WITHOUT implementation)

A NEW SPEC-116 door was drafted in `specs/40-features/harness-own-sandbox.intake.md` (SB-1/2/3 core; SB-4..7 contingency/detection with triggers). Implementation only after D012 (owner directive). Closes the ⬜ P0 "harness-own sandbox" item and the runtime-plane (§5.9) / defense-stack s5 (§7.4) gap in the coverage backlog.
