# SPEC-153 -- Spawn-economy guard: vendor-independent block on under-specified / frontier-for-grunt spawns

Status: SPEC-153, proposed 2026-07-19 (acceptance: `testing/scenarios/sg_spawn_economy.py`).
Intake: `specs/40-features/spawn-economy-guard.intake.md`. Generalizes D032 (the
`workflow run` Fable footgun) + the AGENTS.md spawn-economy incident (2026-07-15)
into ONE guard, mirroring the design-system-guard precedent (advisory hook + code
teeth; commit c085ec1).

## Goal

No under-specified or default spawn may land grunt/fan-out work on a FRONTIER
model and burn the owner's credits. The decision is made once, vendor-independent,
in the harness's own spawn code -- the `workflow run` teeth all spawns funnel
through, running before any subprocess -- and seeded advisorily on both vendors.
The rule does not depend on any agent "remembering" the economy policy.

## Applicability

Applies to the shared core `scripts/harness_lib/spawn_guard.py`, BOTH spawn funnels
-- the blocking `workflow run` runner in `scripts/harness.py` (`workflow_run`) and
the async `workflow start` runner in `scripts/harness_lib/async_runtime.py`
(`workflow_start`), which since v3 route through the SAME shared helper
`spawn_guard.first_denied_worker` -- the config knob `.harness/project.json`
`spawnEconomy`, and the advisory hook `tools/hooks/agent_spawn_economy.py`
(registered in `.harness/capabilities.json`, rendered to `.claude/settings.json` +
`.codex/hooks.json` by `agents pair`). It does NOT change
`model_routing.resolve_role` or the routing tables (model-cards / model-routing /
executors -- consumed/read only).

## Requirements / invariants (numbered, testable)

1. **Core decision (`spawn_guard`).** `card_tier(root, card)` classifies a card as
   `frontier` (the configurable set, default `{fable, opus, gpt-5.6-sol,
   gpt-5.6-terra, gpt-5.5}`), else `cheap` (nvidia-compat/gemini-compat
   `provider/model` cards + `{haiku, sonnet, gpt-5.4-mini, gpt-5.6-luna}`) or
   `mid`. `guard_spawn(spec)` (spec = `{kind, workers, card, profile,
   hasExplicitAck}`) denies a `fork-join`/`map-reduce` fan-out with `workers > 1`
   on a frontier card without ack; a single deliberate frontier spawn (`workers ==
   1`) passes; a cheap-tier fan-out passes at any width.
2. **The teeth REFUSE in BOTH spawn funnels (vendor-independent).** Before any
   worker spawns (and before the run lock / before any async task is written),
   `workflow_run` AND `workflow_start` route through the shared helper
   `spawn_guard.first_denied_worker`, which resolves each runnable worker's REAL
   card (via `executor_profile_spawn` -- the exact seam `run_one_worker` uses, so
   defaultSpawn-backed executors read truly, not as unresolvable) and, on a
   `guard_spawn` deny under `guard == block`, raises with a non-zero exit and ZERO
   workers/async-tasks spawned; the message names the frontier card and the
   acknowledgement. The async funnel receives the resolver by injection from its
   single caller `cmd_workflow_start` (keeping `async_runtime` router-free).
3. **Config knob `spawnEconomy.guard`.** `block` (default) refuses; `warn` logs a
   `workflow_spawn_economy_warned` event and proceeds; `off` skips the guard
   entirely. `spawnEconomy.frontierCards` overrides the default frontier set.
   Owner-tunable without touching code.
4. **Advisory hook on both vendors.** `agent-spawn-economy` keeps the funnel-1
   deny (built-in Agent / codex `spawn_agent` without a model pin) AND, with its
   matcher widened to include `Bash` for both vendors, seeds a `workflow run`
   advisory (a run with no `--allow-frontier` and no cheap `--executor
   nvidia-compat|gemini-compat`). The hook is ADVISORY for the run (it never
   denies the Bash call -- the R2 teeth do the refusing; codex ignores deny
   anyway, SPEC-150).
5. **`--allow-frontier` is the ONLY acknowledgement.** `--allow-frontier` (or
   `HARNESS_ALLOW_FRONTIER=1`) sets `hasExplicitAck`. Choosing `--executor claude`
   is NOT an acknowledgement -- a plan-profile on claude still resolves to `fable`
   and is refused. Fail discipline: under-specification is fail-CLOSED (deny), an
   internal guard error is fail-OPEN (allow, never break legit tooling).

## Rationale & sources

| Decision | Sources |
|---|---|
| One guard for both funnels (R1) | D032 (the `workflow run --executor claude` plan -> fable xhigh footgun across a 5-way fork-join) + AGENTS.md "Model/reasoning policy" spawn-economy incident 2026-07-15 |
| Teeth in the harness spawn code, not the hook (R2, R4) | design-system-guard precedent (commit c085ec1): a hook is an advisory seed; the vendor-independent teeth live in the code all spawns funnel through (codex ignores hook deny, SPEC-150) |
| Card resolved via `executor_profile_spawn` (R2) | it is the exact seam `run_one_worker` uses; `resolve_role` returns None for defaultSpawn-backed executors (openai-compat/generic), which would false-deny legit cheap runs |
| block/warn/off knob (R3) | mirrors `designSystem.guard`; owner-tunable routing/economy policy stays out of code |
| `--allow-frontier` the sole ack (R5) | the owner's framing: `--executor claude` on a plan profile is itself the footgun, so executor choice cannot be the ack -- the ack is a separate, explicit decision |

## Ceilings (upgrade paths)

- Cheap-tier detection uses a `provider/model` "/" heuristic + a small bare-card
  set; every current nvidia-compat/gemini-compat card is namespaced. A future
  bare-id cheap card just joins `CHEAP_CARDS` -- no file read added. Only the
  frontier set is load-bearing for the deny decision.
- BOTH `workflow run` and `workflow start` now carry the TEETH via the shared
  helper (v3 closed the async gap: `workflow_start` gates at its choke point BEFORE
  writing any async task, with the resolver injected from `cmd_workflow_start`). One
  residue: `workflow resume`/`execute` funnel into `workflow_run` but reach the ack
  only via `HARNESS_ALLOW_FRONTIER=1` today, not a per-subcommand `--allow-frontier`
  flag -- they still hit the run teeth, so this is UX, not a bypass. A SEPARATE
  pre-existing residual (the SPEC-115 mid-run failover re-spawn) is NOT yet closed --
  see Amendments v3-v4, tracked v5.
- `route_loop`'s multi-branch implement stage self-acknowledges via
  `allow_frontier=bool(approval_token)` (v2) -- the branch-gate write approval IS the
  ack, so legit deliberate implementation is not over-blocked; the plan/analysis read
  lanes stay unacked (exactly what the guard is meant to catch).

## Test strategy

- Behaviors to verify: the core deny/allow matrix (D032 literal, single frontier,
  cheap fan-out, under-specified); `card_tier` classification; the teeth are wired
  (`--allow-frontier` flag, `spawn_guard.guard_spawn` called before the spawn
  loop, `allow_frontier` threaded); the hook matcher includes `Bash` on both
  vendors and is rendered; the knob exists; the D032 case is COVERED (the real
  research-divergence `--executor claude` card resolves to `fable` and is refused).
- Edge cases: a cheap/deferred executor (nvidia/generic/openai-compat) fan-out is
  NOT refused; the acked spec passes; flipping `guard: off` turns the deny into an
  allow (knob proof).
- Regression risks: over-broad denial breaking legit runs -- guarded by resolving
  the real card and by sg-8 asserting generic/openai-compat pass.
- Coverage impact: enforced via `sg_spawn_economy.py` (sg-1..sg-11, incl. sg-9 the
  route_loop feature-delivery ack, sg-10 the `workflow start` advisory + sg-11 the
  async `workflow start` HARD teeth wired before the async-task loop) +
  `spawn_guard.py --self-check` (incl. the `first_denied_worker` case) +
  `agent_spawn_economy.py --self-check`.

## Validation

- `python testing/scenarios/sg_spawn_economy.py` (11/11, sg-1..sg-11).
- `python scripts/harness_lib/spawn_guard.py --self-check` -> OK.
- `python tools/hooks/agent_spawn_economy.py --self-check` -> OK.
- The RUN teeth proof: `workflow run --executor claude <research-divergence WF>`
  without `--allow-frontier` is REFUSED (non-zero exit, zero workers spawned,
  message naming fable + the ack).
- The START teeth proof (v3): `workflow start --executor claude <research-divergence
  WF>` without `--allow-frontier` is REFUSED (non-zero exit, ZERO async tasks
  written, message naming fable + the ack) -- the async bypass is closed.
- Spec-pack `feature-spec-conformance` green on this file (six required headings
  present; non-UI, no Gherkin).

## Amendments

### v2 (2026-07-19) -- review-driven fixes (Sonnet reckon)

- **route_loop over-block fixed.** `_default_implement_stage` now calls
  `workflow_run(..., allow_frontier=bool(approval_token))`: the SPEC-144 v3
  multi-branch write fan-out (route-overseer -> fable) was being refused as if it
  were accidental grunt work; the branch-gate `approval_token` (a validated secret,
  already checked before `plan_workflow`) IS the acknowledgement. Plan/analysis read
  lanes stay unacked. Covered by sg-9.
- **`workflow start` advisory nudge.** The hook regex widened to `workflow (run|
  start)`; the async path is still NOT hard-guarded (teeth are a follow-up, closable
  at the single `cmd_workflow_start` caller via an injected resolver). Covered by sg-10.
- **`card_tier` conservative default.** The claude `defaultSpawn.model` placeholder
  `"default"` is classified frontier (it resolves to fable), closing a latent
  under-block; `gemini-2.5-flash-lite` labelled cheap for accuracy.

### v3 (2026-07-19) -- close the async `workflow start` bypass

- **Shared funnel gate.** `spawn_guard.first_denied_worker(root, kind, workers,
  runnable, executor, card_resolver, ack)` is the single source of truth both funnels
  now call: it walks `runnable`, resolves each real card via the injected
  `card_resolver` (fail-CLOSED on a resolver error), and returns the first
  `guard_spawn` deny. `workflow_run` was refactored to call it -- behavior-EQUIVALENT
  (same events, same raise message, same block/warn/off flow), with one deliberate
  broadening: the shared helper catches any resolver `Exception` (not only
  `HarnessError`) as `card=None`, so a resolver bug fails CLOSED (deny) rather than
  crashing -- strictly safer, not byte-identical. The module stays leaf (the resolver
  is injected, never imported).
- **`workflow start` HARD-guarded.** The known gap (v2 Ceilings) is closed:
  `workflow_start` gains `allow_frontier` + `card_resolver` params and gates at its
  choke point (after `if not runnable`, BEFORE the async-task write loop), raising
  `workflow_spawn_economy_refused` + a `Zero async tasks were started.` error on a
  block deny. Its single caller `cmd_workflow_start` injects
  `card_resolver=executor_profile_spawn` and threads `--allow-frontier`
  (`cli_workflow_tree` start subparser). A `None` resolver skips the gate
  (backward-safe for any future internal caller). Covered by sg-11.
- **Residue.** `workflow resume`/`execute` still reach the ack only via
  `HARNESS_ALLOW_FRONTIER=1` (they funnel into the `workflow_run` teeth, so this is a
  UX flag gap, not a bypass).
- **Known residual bypass (tracked v5, NOT yet closed).** The SPEC-115 mid-workflow
  FAILOVER hop (`async_runtime.workflow_async_run_one_worker`) re-spawns a rate-limited
  worker on the routing chain's fallback card WITHOUT calling `spawn_guard` -- so an
  N-worker fan-out planned on a CHEAP executor (which passes the plan-time gate) can
  fail its workers over INDIVIDUALLY onto a frontier fallback: a cumulative frontier
  fan-out the per-call-site `workers>1` rule is structurally blind to. Pre-existing
  (SPEC-115, before SPEC-153), out of v3's footprint. **So "zero bypass" is not yet
  literal:** v3 closes both PLAN-TIME spawn funnels (`run` + `start`); the mid-run
  failover re-spawn is a v5 item needing a DIFFERENT check (a per-hop frontier gate,
  or a cumulative per-group frontier budget, since each failover hop is width-1).

### v4 (2026-08-01) — the guard judges the operator's `--model` pin (DD-mechanization P1)

- **`first_denied_worker` evaluates the PINNED card.** `first_denied_worker` gains a
  `spawn_override` param (tri-state after `pins`): when the operator's uniform
  `workflow run/start --model M` pin sets `model`, the verdict judges `M` for EVERY
  runnable worker — the card each will actually spawn (SPEC-165 R14) — instead of the
  profile default, and a refusal NAMES the pin. So `--model <frontier>` at width>1
  without ack is REFUSED naming the frontier pin, while a pinned CHEAP card proceeds at
  any width over a frontier-default profile. `spawn_override=None` is falsy → the gate
  is byte-identical to v3 for every legacy caller (the async funnel, the blocking run,
  the self-check). The ack surface is UNCHANGED: `--allow-frontier` /
  `HARNESS_ALLOW_FRONTIER=1` only; `--executor claude` is still NOT an ack. Both funnels
  thread the override: the blocking `workflow_run` →
  `first_denied_worker(..., spawn_override=)` and the per-hop Rule-8 guard (primary hop
  only, matching the R14 `_attempt`); the async `workflow_start` → the same shared gate.
  Covered by `sg-19` (functional) + `sg-20` (wiring) in
  `testing/scenarios/sg_spawn_economy.py`, plus the `spawn_guard --self-check` pinned leg.
- **Scope.** This is the plan-time gate judging the pin; it is INDEPENDENT of the
  "tracked v5" mid-run failover-bypass residual named in v3 above (the async
  `workflow_async_run_one_worker` re-spawn) — that per-hop frontier gate remains OPEN
  and is a separate item, NOT closed here.

### v5 (2026-08-02) -- per-branch card and executor judgment (P6 Slice 1)

6. **The blocking guard judges each branch's effective seat.**
   `first_denied_worker` accepts optional tri-state maps `worker_executors` and
   `branch_spawn_pins`. For each worker the card precedence is uniform run
   `--model` > `branch.spawn.model` > `card_resolver(taskProfile,
   resolved-worker-executor)`. A branch executor is a deliberate pin for Rule 1b.
   A denied branch verdict names both the effective card and the pinning `workerId`,
   and fires before the blocking pool, proving zero workers spawned. Both new maps
   default to `None`, preserving every legacy caller byte-for-byte. The async funnel
   does not consume these maps in Slice 1: SPEC-165 R15 refuses `branch.spawn`
   workflows before async task creation until Slice 2 implements heterogeneous
   scheduling.

| Decision | Sources |
|---|---|
| Judge the branch model on its resolved executor | SPEC-165 R15 precedence; the guard must evaluate the card the worker will actually spawn |
| Keep the uniform run pin last | v4/R14 established the operator pin as the highest model/effort override |
| Optional maps, not a second guard | Existing `first_denied_worker` is the shared funnel and `None` is its compatibility discipline |

Test strategy and validation: `sg-21` in
`testing/scenarios/sg_spawn_economy.py` locks branch-pin and run-override
precedence; `bs-5` in `testing/scenarios/bs_branch_spawn.py` drives the real
blocking refusal, asserting card + workerId + zero spawns, then proves acked and
cheap branch seats proceed without real subprocesses. `spawn_guard.py --self-check`
covers the same tri-state matrix at module level.
