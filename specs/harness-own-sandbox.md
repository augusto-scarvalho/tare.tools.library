# SPEC-151 — Harness-own sandbox (vendor-agnostic spawn containment)

Status: SPEC-151, proposed 2026-07-18 (acceptance: `testing/scenarios/hos_harness_sandbox.py`).
Intake: `specs/40-features/harness-own-sandbox.intake.md` (door NEW, D012 R2).
Design portfolio: `docs/research/harness-own-sandbox.md` (SB-1..7).

## Goal

A vendor-agnostic containment layer applied at worker spawn so that an
open-model HTTP worker — which has NO native hooks and NO native sandbox, and
today can read/write/spawn/network anything the parent process can — runs
confined, and claude/codex workers gain the same lifecycle containment (parity,
D009). The admin-free core (Job Object process containment + NTFS ACL filesystem
confinement + a legible confinement manifest) closes the P0 hole; egress
kernel-blocking, which needs admin on Windows, stays behind a trigger and
degrades legibly (never silently unconfined).

## Applicability

Applies to the three worker-spawn seams that build a child env + argv today:
- blocking `run_one_worker` (`scripts/harness.py`),
- async `workflow_async_run_one_worker` (`scripts/harness_lib/async_runtime.py`),
- detached dispatch (`route` path).

It wraps those seams; it does NOT redesign the executor `commandTemplate`, the
`processes.filter_spawn_env` allowlist (S1/E3), or the codex native `sandbox_mode`
(S3 — which stays the codex write control). It does not cover interactive owner
chat rooms (those are top-level sessions, not confined workers). Target OS is
Windows 11 single-tenant; a non-Windows host degrades to declared-unconfined.

## Requirements / invariants (numbered, testable)

1. **Job Object process containment (SB-1).** Every confined worker is spawned
   into a Windows Job Object (ctypes `CreateJobObjectW` +
   `AssignProcessToJobObject`) with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` and
   `JOB_OBJECT_LIMIT_BREAKAWAY_OK` cleared, so no child process survives the
   workflow. Applies to all three vendor classes (claude/codex/open-model).
2. **NTFS ACL filesystem confinement (SB-2), dual-mode.** A read worker gets a
   deny-write ACE (via `icacls`) on its scope paths and an allow-write only on
   its result-file path; a write worker keeps write access to its dedicated git
   worktree. A read worker that attempts a write outside its result path is
   blocked by the OS, not by a hook.
3. **Confinement manifest + legible degradation (SB-3).** Every spawn records a
   manifest `{fsEnforced: bool, egressEnforced: bool, procEnforced: bool,
   reason: str}`. When a primitive is unavailable (no Job Object support, no
   admin for egress), the spawn either degrades with the reason recorded OR
   refuses — it MUST NOT proceed as if confined. A capability probe runs at
   workflow start and stamps what is enforceable on this host.
4. **Egress is honest, not faked.** Per-process egress kernel-blocking needs
   admin (WFP). Without admin, `egressEnforced` is `false` with a reason; netsh
   image-path rules (SB-5) are advisory-only and never counted as enforcement;
   the CaMeL capability token (SB-6) is observability/defense-in-depth, never the
   primary egress boundary. A worker whose task DECLARES an egress need and whose
   egress cannot be enforced is refused (not silently run).
5. **Break-glass, declared.** `project.json workflows.workerSandbox=false`
   disables the layer wholesale (parity with `workerEnvFilter`); the bypass is
   recorded in the manifest as `{sandboxBypassed: true}`, never silent.
6. **Zero live-flow breakage.** A read worker still reads its scope and writes
   its result; a write worker still writes its worktree; a fork-join of read +
   write workers still completes green under the layer.
7. **Reconciliation feed (SB-7), detection-only.** The committed
   `protect_files.apply_patch_paths` + a worktree diff feed post-execution
   detection; this complements but never substitutes the pre-spawn containment
   of rules 1-2 (a detection-only signal is never counted toward the boundary).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Contenção no spawn é o único controle confiável p/ open-model worker (sem hook/sandbox nativo) | investigação codex 2026-07-18 (`harness-reference-architecture-adoption.md`, matriz de contenção); artigo §5.9 runtime plane, §7.4 s5 |
| Job Object como fundação sem-admin | R2 divergência+crítica (`harness-own-sandbox.md` SB-1); 3 críticos unânimes; docs Microsoft Job Objects (`referencia: judgment`) |
| NTFS ACL dual-mode p/ não quebrar write worker | R2 crítica (SB-2; o gap "junction overlay quebra worktree" que o crítico de segurança pegou) |
| Egress kernel exige admin → atrás de gatilho, degradação legível | R2 crítica (SB-4/5/6; blocker de 3 críticos sobre egress); artigo §7.4 (contenção em profundidade), SPEC-111 R23/R24 (degradação explícita, nunca silêncio) |
| CaMeL = observability, nunca enforcement primário | R2 crítica (reclassificação unânime); artigo §7.4 CaMeL |
| Break-glass declarado | precedente interno `workflows.workerEnvFilter=false` (S1) |

## Gherkin scenarios (UI surfaces only)

N/A — internal spawn wrapper + CLI probe/manifest. No UI surface (Gherkin optional).

## Ceilings (upgrade paths)

- Egress real-block por-processo sem admin não existe com stdlib no Windows —
  teto aceito; upgrade = WFP (SB-4) quando a sessão for elevada ou multi-tenant.
- ctypes Win32 é frágil a versões — isolar num módulo com probe + fallback;
  upgrade = AppContainer/restricted-token pool (SB-4 R2) sob gatilho.
- Contêiner/VM real fica como aposta futura (gatilho: multi-tenant ou incidente
  de escape provado).

## Test strategy

Behaviors to verify (acceptance `testing/scenarios/hos_harness_sandbox.py`,
stdlib, deterministic; the Win32 pieces probe-and-skip on an unsupported host so
the gate stays green cross-platform):
- SB-1: a worker spawned into a Job Object dies on job close (no zombie child).
- SB-2: a read worker's write outside the result path is denied; a write
  worker's worktree write succeeds.
- SB-3: probe on a host without a primitive stamps `enforced:false` + reason;
  the spawn refuses or degrades declared, never runs as-if-confined.
- Rule 4: a task declaring egress with no enforceable egress is refused.
- Rule 5: `workerSandbox=false` records `sandboxBypassed:true`.
- Rule 6: a mixed read+write fork-join completes green under the layer.
- Edge: unsupported OS → all `*Enforced` false with reason, no crash.

Regression risks: the three spawn seams are runtime-core; a Job Object that kills
legitimate workers breaks fan-out (mitigated by probe + break-glass). Coverage:
informational (stdlib module self-check + the scenario).

## Validation

- `python scripts/harness_lib/sandbox_spawn.py` (module self-check — extend the
  existing SPEC-148 sandbox_spawn module rather than a new one where possible).
- `python testing/scenarios/hos_harness_sandbox.py`.
- Gate: `smoke`, `spec-pack`, `scenarios`, `workflow`.

## Amendments

### v5 (2026-08-09) — strict backend capability spikes, no fallback claim

`STRICT_CANDIDATE_READONLY` is a separate, future proof-producing profile. It
does not upgrade the existing `nt-icacls` plus Job Object worker controls into
host filesystem confinement.

- Windows probes the documented, experimental
  `processmodel.dll!Experimental_CreateProcessInSandbox` export dynamically.
  A strict Windows launch is permitted only after an authoritative compiler for
  Microsoft's `SandboxSpec.fbs` (`SBOX`) contract is available. The current
  harness has no such compiler/schema, therefore the capability is recorded as
  `API_INCOMPATIBLE` and the child is refused before launch. There is no
  fallback to the earlier manual AppContainer experiment, `icacls`, or a Job
  Object for this profile.
- Linux has an allowlist-only Bubblewrap adapter: user/PID/network namespaces,
  a read-only subject bind, an explicit writable scratch bind, and only the
  interpreter/runtime roots needed by the process. It is `AVAILABLE` only after
  the namespace probe succeeds; missing Bubblewrap or blocked user namespaces
  are `NOT_AVAILABLE`/`FAILED` and refuse strict execution.
- The receipt binds candidate tree/fingerprint/snapshot, permit identity,
  profile, backend identity, scratch class, execution id, and actual result.
  Physical temporary paths remain evidence metadata only.

Acceptance: `testing/scenarios/sbi_sandbox_backend_spikes.py`. On a host
without a qualifying backend, the acceptance proves refusal/no unconfined
launch, not filesystem confinement. The real path and child-process attacks
run only where the corresponding backend is available.

- v2 (2026-07-18) — implementation mapping onto the shipped SPEC-148
  `scripts/harness_lib/sandbox_spawn.py` (this was a delta, not greenfield). The
  invariants are unchanged; these notes record how each is satisfied and the
  three ceilings where SPEC-148 reality is narrower than an invariant's letter:
  - Invariant 1 (Job Object) is satisfied by SPEC-148's `run_process_tree_bounded`
    (ctypes `CreateJobObjectW` + `AssignProcessToJobObject` + tree-kill on timeout
    via `signal_process_tree`). **Ceiling:** the shipped code does not hold the job
    handle with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`; process containment is proved
    via the Job Object memory cap kill (`hos-6`), and the tree-kill guarantees no
    zombie survives a timeout. Kill-on-job-close is a follow-up hardening.
  - Invariant 2 (NTFS ACL dual-mode) is satisfied for **write** workers: R1+ gets
    an icacls deny on the protected canonical paths inside its isolated workspace
    while its worktree stays writable (`hos-7`). **Ceiling:** SPEC-148 does NOT put
    an OS-level deny-write ACE on a **read** worker's scope; read workers are
    confined by the least-privilege spawn env + no write tool + the merge/footprint
    gate. The confinement manifest is honest about this: `fsEnforced` is a
    host-capability stamp from the probe, and `fsApplied` lists the per-spawn ACEs
    (write-worker protected paths only). Read-worker scope deny-write is a ceiling.
  - Invariant 3 (manifest + probe): the receipt from `sandbox_prepare` now carries
    `{procEnforced, fsEnforced, egressEnforced, reason}` (+ `sandboxBypassed`,
    `egressDeclared`) stamped from `sandbox_capabilities()`. **Note:** the probe
    runs per-spawn (every worker start) rather than as a single workflow-start
    event; the manifest is recorded on the `async_task_started`,
    `workflow_worker_finished`, and `route_dispatched` events.
  - Invariant 4 (egress honesty): `egressEnforced` is `false` with a reason absent
    admin (WFP); the open-model worker's `--allow-hosts` (SPEC-148 P3) is advisory
    defense-in-depth and is never counted. A task setting `worker.declaresEgress`
    on a host without enforceable egress is refused.
  - Invariant 5 (break-glass): `workflows.workerSandbox=false` short-circuits
    `sandbox_prepare` to a `{sandboxBypassed: true}` receipt (parity with
    `workerEnvFilter`), threaded from all three seams.

## Open questions for the human (saved from the intake — answer at implementation)

- Q1: escape hatch `workerSandbox=false` no project.json (paridade com
  `workerEnvFilter`)? (proposta do design: sim — rule 5 assume que sim.)
- Q2: sem admin, task open-model que EXIGE rede → recusar spawn (rule 4) ou
  rodar com egress advisory + SB-7 detecção? (proposta: recusar se a task
  declara egress; senão rodar declarado. Rule 4 assume recusar-se-declara.)
- Q3: SB-1 aplica a claude/codex também (reforço, paridade D009) ou só
  open-model (o buraco)? (proposta e rule 1: os 3 — lifecycle de graça.)
- Q4: SB-1/2/3 juntos como MVP ou SB-1 sozinho primeiro? (proposta: SB-1+SB-2+
  SB-3 juntos — o manifest SB-3 sem as duas contenções não tem o que declarar.)
