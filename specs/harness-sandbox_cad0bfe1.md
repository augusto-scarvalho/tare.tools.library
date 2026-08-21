# SPEC-148 — Harness-owned sandbox (`sandbox_spawn` chokepoint)

Status: SPEC-148, proposed 2026-07-18 (acceptance: `testing/scenarios/hsb_sandbox_spawn.py`).
Intake: `specs/40-features/harness-sandbox.intake.md`. Architecture:
`docs/HARNESS_SANDBOX_DESIGN.md` (owner decisions §8, 2026-07-18).

## Goal

Every worker/engine the harness spawns runs inside a harness-owned, vendor-agnostic
confinement wrapper that bounds filesystem writes, process tree, and credentials at
spawn time. Vendor-native sandboxes are heterogeneous — codex has a reliable
`sandbox_mode`, claude honors permission-mode/allowedTools, open-model HTTP workers
have **nothing** — so containment cannot be delegated to vendors; the harness owns
the floor and composes vendor layers inside it.

## Applicability

All harness-initiated AUTONOMOUS worker spawns: workflow workers
(`scripts/harness.py` run path and the async twin), detached route dispatch,
and — through those templates — the open-model HTTP worker
(`tools/openai_worker.py`). Interactive owner-present rooms (`chat_engines`)
are a RECORDED exemption, not a covered surface: their env inheritance is the
Trilha S deferral (breaks engines without per-engine tests), their write
control stays vendor-native (S2/S3), and the chokepoint's `inherit_reason`
receipt is the mechanism a future migration uses.
Explicitly not covered: gate/fixture plumbing spawns (governed by the existing
raw-subprocess ratchet), model output correctness, approval/authorization flows
(complementary — article §7.4), and kernel-grade isolation claims on Windows.
P1 ships dimensions D1 (fs) + D3 (env) + D2 (process floor); D2 hard caps, the
codex pre-write validator (P2) and D4 egress (P3) are phased follow-ups.

## Requirements / invariants (numbered, testable)

1. **One chokepoint.** Every worker/engine spawn routes through
   `sandbox_spawn(...)` (`scripts/harness_lib/sandbox_spawn.py`). A worker/engine
   spawn site that bypasses it is a gate failure (spawn-mediation ratchet
   extended), not a silent hole.
2. **Tier-scaled composition.** Read-only spawns (R0: `writeAllowed` false) get
   env-scope + process-bound only. Write/effect spawns (R1+) additionally get an
   isolated workspace cwd and OS-level deny-write on protected paths. Cost scales
   with risk; cheap fan-outs stay cheap.
3. **Fail closed.** A sandbox-setup error, or a missing per-OS backend for a
   dimension the tier requires, REFUSES the spawn with a legible reason. R0 may
   proceed on env+process layers alone; R1+ never runs unconfined. Indeterminate
   → deny (article §3.5).
4. **Loud, owner-tokened override only.** The only bypass of rule 3 is an
   explicit owner-tokened override, visibly recorded with the refusal reason it
   overrides. No silent downgrade paths.
5. **Least-privilege env everywhere.** Every spawn — including the open-model
   HTTP worker, previously unfiltered — passes `filter_spawn_env` with a
   per-vendor keep-list carrying at most the one endpoint credential that vendor
   needs, plus HARNESS_* vars.
6. **Protected paths physically unwritable for write workers.** In a write
   worker's workspace, protected canonical files are present and readable but
   unwritable AND undeletable at the OS level (owner decision: Option A). The
   Windows backend composes the read-only attribute (blocks DeleteFile even
   via parent-dir FILE_DELETE_CHILD) with a specific-rights deny ACE
   (WD,AD,WA,WEA,DE — blocks writes and clearing the RO bit; never generic W,
   which denies SYNCHRONIZE and breaks reads). The attempt fails at write
   time, not merge time; disposal paths release ACLs first (`fs_release`).
7. **Vendor inner layers composed, never replaced.** codex spawns keep native
   `--sandbox` driven by `writeAllowed` (S3); claude spawns keep the tools
   ceiling (S2). `sandbox_spawn` takes only (manifest, vendor tag); vendor
   specifics never leak into callers.
8. **Cross-OS interface, per-OS backends.** Confinement dimensions live behind
   an OS-agnostic interface (`fs_confine`, `proc_bound`, `env_scope`); each OS
   implements with native primitives (Windows: worktree + `icacls` + Job Object).
   A missing backend behaves per rule 3 — "no backend" ≠ "no sandbox".
9. **Merge-gate backstop unchanged.** The merge-time footprint check
   (CONTROLLED_PARALLEL_WRITES) remains in force under every backend — a write
   outside the declared footprint never integrates even where fs ACL is weak.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Harness must own the sandbox; vendors can't be delegated to | Live experiment 2026-07-18 (8 codex execs): codex ignores hook deny under `bypassPermissions` — edited protected AGENTS.md through fully-wired hooks; `--sandbox read-only` DID block. Open-model workers: no hook runtime, no sandbox. `docs/research/harness-reference-architecture-adoption.md` (containment table) |
| Sandbox is mandatory runtime-plane component | Reference article §5.9 (leased scheduler + sandbox), §7.4 defense-in-depth layer 5, §7.5 (compromised worker / malicious adapter threat) |
| Single chokepoint with explicit consequences | `docs/HARNESS_SANDBOX_DESIGN.md` §11 (owner Q4): SPOF → fail-closed; migration debt → ratchet; latency → tier scaling; coupling → manifest-only inputs |
| Fail closed on missing backend | Article §3.5 (indeterminate → deny); owner decision Q3: cross-OS equivalence, no Windows-only hack |
| Option A (deny-write ACL, files present) | Owner decision Q2, 2026-07-18 |
| Tier-scaled cost | Design §11.3; cost incident 2026-07-15 (expensive fan-outs) — R0 lookups must not pay worktree+ACL setup |
| Ratchet over purge for migration | SEC.5 precedent (`spawn_ratchet.py`): baseline + fail-on-new is the honest posture for ~48 legacy sites |
| Env least-privilege at every surface | SPEC-119 v5 `filter_spawn_env` (S1 closed workflow+dispatch; HTTP worker gap documented in design §3) |
| RO-attribute + specific-rights deny composition (rule 6) | Measured 2026-07-18 (module self-check, live icacls): bare deny-DE ACE did NOT block `DeleteFile` (parent-dir FILE_DELETE_CHILD bypass → delete+recreate); generic-W deny DID block read opens (SYNCHRONIZE/READ_CONTROL in FILE_GENERIC_WRITE) |
| Rooms as recorded exemption, not covered surface | Trilha S deferral (research doc, 2026-07-18): filtering interactive-room env breaks engines without per-engine tests; rooms are owner-present, write control vendor-native |

## Ceilings (upgrade paths)

- Windows fs confinement = worktree + `icacls` deny-write + merge gate, not a
  filesystem namespace; upgrade path: restricted token / AppContainer (backlog,
  trigger: multi-tenant or an escape incident).
- D2 process floor = Job Object membership (tree-kill + accounting); memory/
  child-count/wall caps are P2 wiring on the same handle.
- Linux/macOS backends = fail-closed stubs in P1; implement on first non-Windows
  operator (design §10 table is the contract).
- Egress = unconfined in P1 (SEC.1 covers only `discover`); P3 = in-client
  allowlist in `openai_worker.py`, broker on backlog.
- Interactive rooms outside the chokepoint (recorded exemption); migrate via
  `inherit_reason` receipts when per-engine env tests exist.
- ACL confinement covers the worker's workspace copies; a direct absolute-path
  write to the LIVE tree stays covered by vendor layers (codex workspace-write
  scoping, claude hooks, HTTP worker has no fs tool) + the merge/footprint gate
  + protected-files snapshot — not by this ACL. Upgrade: restricted token.

## Test strategy

- Behaviors: chokepoint refusal (fail-closed) paths; tier scaling (R0 skips
  worktree/ACL, R1+ gets them); env filtering per vendor; ACL deny actually
  blocks a write to a protected path inside a write workspace; ratchet flags a
  new unmediated worker spawn site.
- Red-team (design §7 / `testing/RED_TEAM_FIXTURES.md` pattern): write worker
  attempts protected-file edit → blocked at fs layer, per vendor class incl.
  open-model; worker env contains no foreign vendor credential.
- Edge cases: missing backend OS (simulated) refuses R1+ but allows R0;
  owner-token override records loudly; ACL cleanup on worktree disposal.
- Regression risks: existing workflow worker spawns keep working (bounded run,
  logs, WORKER_RESULT extraction); dispatch lock/pid semantics unchanged.
- Coverage impact: enforced.

## Validation

- `python testing/scenarios/hsb_sandbox_spawn.py` — acceptance checks for rules
  1–3, 5–6 (chokepoint routing, tier scaling, fail-closed refusal, env filter,
  ACL deny).
- `python scripts/harness_lib/sandbox_spawn.py` — module self-check.
- `testing/scenarios/srg_spawn_ratchet.py` — ratchet still green, extended
  coverage for the chokepoint.
- SPEC-137 `validate --staged` gate green.

## Amendments

### v2 (2026-07-18) — P2 (D2 caps + pre-merge validator) + P3 (egress in-client)

10. **Job caps on bounded sandbox spawns.** Bounded chokepoint spawns carry
    Job Object caps (`DEFAULT_JOB_LIMITS`: 64 active processes, 4 GiB job
    memory; explicit `job_limits=None` opts out). A cap requested but not
    applied kills the still-suspended child and raises — never a silently
    uncapped run that claimed to be capped. nt-only; the asyncio twin has no
    Job Object (timeout + group kill only) — a recorded ceiling, upgrade when
    an incident shows a runaway async worker.
11. **Pre-merge protected scan.** `workflow_merge_plan` reports any protected
    path whose workspace copy differs from the live tree as conflict
    `protected-path-modified` and blocks the merge. Detection layer under the
    rule-6 ACL: a hit is evidence containment was bypassed, not routine.
12. **Egress allowlist is argv-pinned.** `tools/openai_worker.py` refuses a
    base-url host outside `--allow-hosts` (exit 6, before any network I/O).
    The allowlist rides in the executor `commandTemplate` (gate-protected
    config), NEVER in env — a repointed env var is exactly the exfil threat
    this closes. CLI-vendor tool-driven egress stays uncovered (broker =
    backlog, owner decision Q1).

| Decisão (v2) | Fontes |
|---|---|
| Caps de Job Object com aplicação fail-closed | Design §6 P2; recon 2026-07-18: zero `SetInformationJobObject` existia no repo (só assign + CPU accounting); §11.1 (setup error → refuse) |
| Validador pre-write virou scan pre-merge vendor-agnóstico | Design P2 previa parser apply_patch em hook; hooks codex são advisory (deny ignorado, trust off por decisão) e a ACL P1 já bloqueia no OS — o ponto de detecção honesto e vendor-agnóstico é o merge plan |
| Allowlist in-client agora; broker no backlog | Owner decisão Q1 (2026-07-18); env como canal não-confiável (S1/D3) |

### v3 (2026-07-18) — N5 risk tiers R0-R3 (closed vocabulary, two consumers)

13. **Risk tiers are a closed vocabulary.** `risk_tier(*, write_allowed,
    risk_flags=None)` in `scripts/harness_lib/sandbox_spawn.py` maps a spawn to
    exactly one tier from `RISK_TIERS`. No flags → R1 (write) or R0 (read-only);
    any flag in `{payment, secrets, destructive}` → R3; any other non-empty flag
    → R2. Pure (stdlib only). Article §3.5 / N5's deferral (2026-07-18, "lacks a
    consumer") is lifted: the sandbox is the consumer.

    | Tier | Meaning |
    |---|---|
    | R0 | observational (read-only) |
    | R1 | reversible write (isolated workspace + merge gate) |
    | R2 | material (protected-path adjacent, external effect) |
    | R3 | critical (secrets, payments, destructive) |

    Two consumers, no behavior change beyond the two fields:
    * **sandbox receipt** — `sandbox_prepare` sets `receipt["tier"] =
      risk_tier(write_allowed=write_allowed)` (semantics identical to the prior
      inline `"R1" if write_allowed else "R0"`; future call-site flags ride free).
    * **route decision** — `route_decision` adds an ADDITIVE sibling `riskTier =
      risk_tier(write_allowed=False, risk_flags=<floor flags>)`. The deterministic
      floor emits only `security`/`rule-of-two` today, so a flagged routed
      decision is R2; R3 needs one of the critical flags. No consumer changes its
      behavior on `riskTier` in L1 (observe-first, EXP discipline).

| Decisão (v3) | Fontes |
|---|---|
| Enum canônico R0-R3 com dois consumidores existentes | Article §3.5 / N5 (deferido 2026-07-18 por falta de consumidor); `sandbox_spawn` já falava "R0"/"R1" ad hoc; plano L1 `.harness/handoff/plan-l1-risk-tiers.md` |
| `riskTier` aditivo, observe-first | Disciplina EXP: campo aditivo primeiro; comportamento só depois de observar (nenhum consumidor muda em L1) |
