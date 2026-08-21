# Intake refinement -- spawn-economy guard (door NEW)

SPEC-116 invariant 2 checklist. Seeds SPEC-153 (`specs/40-features/spawn-economy-guard.md`).

## Request (verbatim)

> um hook que nao deixe a gente spawnar agentes sem perfil ou qualquer
> informacao que acabe prejudicando a execucao, que funcione independente de
> vendor... blinda o harness de dar bypass nas regras de spawn e fazer o owner
> gastar creditos com trabalho bracal usando modelos frontier

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search spawn economy frontier fan-out` | no hit -- `[]`, no record owns the decision |
| doc-find | `python scripts/harness.py doc-find spawn economy frontier workflow run allow-frontier` | hits are planning docs (`tasks/harness-self-improvement/PLAN.md`), not a spec that owns this |

Two adjacent registers of the rule EXIST but neither is a spec that a check can
regress against:

- `AGENTS.md` "Model/reasoning policy" -- the spawn-economy narrative (cost
  incident 2026-07-15), a control-plane instruction, not a testable spec.
- `tools/hooks/agent_spawn_economy.py` -- the ADVISORY hook (funnel 1 only:
  built-in Agent/spawn_agent without a model pin), which does NOT cover the
  `workflow run` funnel (D032) and is advisory (codex ignores deny).

Decision: **NEW** -- the vendor-independent block on under-specified /
frontier-for-grunt spawns (both funnels, with real teeth) is unspecified; a
narrative + an advisory hook describe intent, they do not pin an enforced rule.

## Goal

One sentence: no under-specified or default spawn can land grunt/fan-out work on
a frontier model and burn the owner's credits -- enforced vendor-independently in
the harness's own spawn code (the `workflow run` teeth), seeded advisorily on
both vendors, with an explicit single acknowledgement (`--allow-frontier`).

## Scope

In scope:
- A pure, stdlib core (`spawn_guard`) that classifies a card's tier and decides
  one spawn (brawn fan-out on frontier without ack -> deny; under-specified ->
  fail-closed deny; else allow).
- Vendor-independent TEETH in `scripts/harness.py` `workflow_run`: resolve each
  worker's real card and REFUSE the run (zero workers spawned) before spawning.
- Config knob `spawnEconomy.guard` (block|warn|off) + `frontierCards`.
- The advisory hook widened to also seed the rule on Bash `workflow run`.
- `--allow-frontier` / `HARNESS_ALLOW_FRONTIER=1` as the ONLY acknowledgement.

Out of scope:
- Changing `model_routing.resolve_role` or the routing tables (model-cards.json /
  model-routing.json / executors.json) -- consumed/read only.
- The async `workflow start` path (only blocking `workflow run` carries the teeth
  in this spec; async fan-out is a separate follow-up).
- Making codex honor the hook deny (hooks on codex stay advisory, SPEC-150).

## Actors & surfaces

- Actors: the `workflow run` runner, the Agent/spawn_agent/Bash spawn hook, the
  spec-pack + scenarios gates.
- Surfaces (CLI / GUI / API / internal): CLI (`workflow run --allow-frontier`) +
  internal (routing consumption + hook registry). UI surface? **no** -> Gherkin
  optional.

## Proposed acceptance criteria

- [ ] `spawn_guard.guard_spawn` denies a fork-join/map-reduce fan-out (>1) on a
  frontier card without ack, and allows it with ack / at width 1 / on a cheap card.
- [ ] `spawn_guard.guard_spawn` fail-closed denies an under-specified spawn (no
  resolvable card or profile); fails open on an internal error.
- [ ] `workflow run` refuses (non-zero exit, ZERO workers spawned) a frontier
  fan-out without ack, naming the card + the acknowledgement.
- [ ] `spawnEconomy.guard` is block|warn|off (default block) and owner-tunable.
- [ ] The advisory hook seeds the rule on Bash `workflow run` for both vendors.
- [ ] `--allow-frontier` / `HARNESS_ALLOW_FRONTIER=1` is the only ack; choosing
  `--executor claude` is NOT one.

## Risks / blast radius

Medium: touches the workflow spawn runner (central). The card is resolved via the
exact seam `run_one_worker` uses (`executor_profile_spawn`), so legit
nvidia/gemini/generic/openai-compat runs (cheap or deferred cards) are NOT
refused. Rollback = revert the teeth block + the flag + the two spec files.
Downstream note: `route_loop`'s multi-branch implement stage on a frontier
executor now requires `HARNESS_ALLOW_FRONTIER=1` (single-worker stages are
unaffected) -- surfaced, not silently changed.

## Open questions for the human

- Should the async `workflow start` path carry the same teeth? (Deferred here;
  only blocking `workflow run` is covered.)
