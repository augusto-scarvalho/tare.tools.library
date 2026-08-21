# Intake refinement — harness-owned sandbox (door NEW)

SPEC-116 invariant 2 checklist. Seeds SPEC-148 (`specs/40-features/harness-sandbox.md`).
Architecture pre-work: `docs/HARNESS_SANDBOX_DESIGN.md` (owner-approved 2026-07-18,
4 decisions closed).

## Request (verbatim)

> Owner, 2026-07-18: "um sandbox próprio do harness é um **requisito** para
> multi-vendor + open models trabalharem juntos"; pediu **arquitetura antes de
> código**, fechou as 4 decisões (§8 do design doc) e mandou seguir para
> "SPEC-116 door-NEW + P1 (sandbox_spawn chokepoint)".

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search sandbox spawn confinement` | no hit (`[]`) |
| doc-find | `python scripts/harness.py doc-find sandbox spawn confinement worker` | hits are the design doc itself (`docs/HARNESS_SANDBOX_DESIGN.md`, not a spec) plus unrelated specs (fork-join, packet-economy). No spec owns harness-side spawn confinement. |

Decision: **NEW** — no existing spec covers a harness-owned sandbox. Nearest
neighbors govern single dimensions only (SPEC-119 env filter, SPEC-137 gate,
protected-files hook) and are composed by, not replaced by, this spec.

## Goal

Every worker/engine the harness spawns runs inside a harness-owned confinement
wrapper (`sandbox_spawn`) that bounds filesystem writes, process tree, and
credentials regardless of vendor — closing the open-model gap (today: zero
confinement) and the codex hook-advisory gap (deny ignored under
bypassPermissions; native `sandbox_mode` is the only reliable write control).

## Scope

In scope (P1):
- One spawn chokepoint (`sandbox_spawn`) composing: isolated cwd/worktree,
  per-vendor env scoping (`filter_spawn_env`), OS-level deny-write ACL on
  protected paths for write workers, `esh` Job Object process bounding.
- OS-agnostic interface with per-OS backends; Windows backend implemented,
  Linux/macOS stubbed **fail-closed** for R1+ (write/effect) spawns.
- Migration of every worker/engine spawn surface to the chokepoint; the
  no-raw-subprocess ratchet extended so bypassing it is a gate failure.
- Risk-tier cost scaling: read-only spawns get env+process layers only.

Out of scope (deferred, registered):
- P2: Job Object memory/child/wall caps; codex pre-write validator (consumes the
  shipped `apply_patch_paths` parser).
- P3: egress — in-client allowlist for HTTP workers, then general broker (backlog).
- Restricted tokens / AppContainer (backlog); kernel-grade isolation claims.

## Actors & surfaces

- Actors: harness runtime (workflow workers, dispatch, chat engines, HTTP
  open-model workers, route dispatcher); vendors claude/codex/openai-compat.
- Surfaces (CLI / GUI / API / internal): internal spawn layer + CLI verbs that
  spawn; no new user-facing surface.
- UI surface? **no** → Gherkin optional (omitted).

## Proposed acceptance criteria

- [ ] Every worker/engine spawn routes through `sandbox_spawn`; a new unmediated
      spawn site fails the gate (ratchet).
- [ ] A write worker's attempt to modify a protected canonical file fails at the
      OS/fs layer (not merge-time only), for each vendor class incl. open model.
- [ ] Every spawned worker env is least-privilege: only OS base + the one
      vendor credential + HARNESS_* vars (S1 gap sites closed, incl. HTTP worker).
- [ ] On an OS/dimension without a backend, an R1+ spawn is REFUSED loudly with
      reason; R0 proceeds with env+process layers; no silent unconfined spawn.
- [ ] A sandbox-setup error refuses the spawn (fail closed), never spawns
      unconfined; override only via explicit owner token, visibly recorded.
- [ ] codex spawns keep native `sandbox_mode` (S3) composed as inner layer.
- [ ] Merge-time footprint gate unchanged (backstop under all backends).

## Risks / blast radius

- Chokepoint is a single point of failure → fail-closed + small + self-checked
  (design §11.1).
- Touches every spawn call site (`harness.py` run_one_worker/dispatch,
  `async_runtime`, chat engines, `openai_worker`, route dispatcher) → migrate
  behind the existing helpers, ratchet catches strays.
- ACL (`icacls`) mistakes could lock the OWNER's tree → ACLs applied only inside
  disposable worker worktrees, never the live tree; rollback = delete worktree.
- Latency tax on cheap fan-outs → tier-scaled composition (R0 skips worktree/ACL).
- Fail-closed can block work on unsupported OS → loud refusal + owner-tokened
  escape hatch (design §11.5); accepted trade-off.

## Open questions for the human

- (none — the four design questions were decided by the owner 2026-07-18;
  recorded in `docs/HARNESS_SANDBOX_DESIGN.md` §8.)
