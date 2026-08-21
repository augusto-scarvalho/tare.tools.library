# SPEC-110 — Harness-Target Governance (Milestone HT)

Status: **Done** (executed 2026-07-09; commits 46086a0, edf2278, 69f0b93 + batch 4).
Acceptance: `testing/scenarios/ht_targets.py` (15/15). **T5 re-scoped** (see below). User principle: the harness and its
capabilities do not operate only on their own code — gates, specs, tests, critique and
self-improvement run **over the files of the target project** agents are working on, using
the same structure the harness uses to check and define itself. Prior user decisions kept:
multi-repo direct; state centralized in the harness; per-project config without file sprawl.

## Goal

The harness is a **governance engine parameterized by subject** — `self` (its own repo) or
`target(<name>)` (any repository agents work on). Every capability that runs on `self` runs
on targets: the proportional gate ladder (generic structural checks + the target's own
build/test/lint commands), knowledge structure (AST graph, discover, doc-find), the
self-review MAPE-K loop with per-target ratchets, the supervision funnel, workflows/spawns
with target-scoped env/MCP, and canonical-file protection. Only the root, the state location,
and the layered config change between subjects; the engine is one.

## Grounding

- User principle (2026-07-09): "o harness se mantém e aplica as regras a si mesmo, mas também
  aplica as regras ao código que está sendo gerado em outros repositórios"; the critique must
  use "a própria estrutura que o checa e define", including "testes, gates, specs".
- MF fragmentation made the libs root-parameterized (`graphify_code_ast(root)`,
  `protected_files.*(root)`, `collect_metrics(root)`) — subject routing is wiring.
- `PROJECT_ADOPTION_GUIDE.md` "Keeping it generic" + project.json `validation.<gate>.commands`
  already model per-project commands; `target.json` replicates that per target.
- MAPE-K per subject (SPEC-109 / SELF_EVOLUTION_IDEATION §1b): the same loop, N knowledge
  scopes.

## Capability × subject contract (the milestone's definition of done)

| Capability | self (today) | target (this milestone) |
|---|---|---|
| Proportional gates | `harness-test.py <gate>` | `harness-test.py <gate> --target <n>`: generic structural checks over the target tree + `validation.<gate>.commands` (cwd=target) → `.harness/state/targets/<n>/quality-state.json`, SPEC-101 fix-lines |
| Specs | universal baseline + project layers | universal baseline applies; optional per-target overlay `.harness/targets/<n>/specs/` |
| Knowledge (graph/symbols/modules, discover, doc-find) | `graphify-out/` | `--target` flag → `graphify-out/targets/<n>/` |
| Self-review (MAPE-K) | metrics/rules/ratchets over self | per-target metrics (gate history incl. red-recurring, budgets, staleness, env), rules `self-review/target/<n>/*`, per-target ratchets; layered thresholds; scoped customRules |
| Supervision funnel | escalations + M4 page + inbox | same funnel, target-prefixed ids |
| Workflows/spawns | repo files | `--target`: shards from the target graph, env deny-by-default from `requiresEnv`, MCP/skills adapter from `targets sync` (T5) |
| Canonical-file protection | registry + snapshot | market registry + `protectedFiles` extras, snapshot under target state (T6) |

## Config without sprawl (user constraint)

One directory per target, ONE canonical tracked file:
`.harness/targets/<name>/target.json` = `{name, path, enabled, sourceGlobs, lineBudgets,
validation{<gate>:{commands}}, requiresEnv[], mcp{servers}, skills[], plugins[],
selfReview{thresholds overrides}, protectedFiles[], notes}`. Optional subdirs (`specs/`,
`prompts/`) exist only when used. Secrets stay in the single root `.env`; the target declares
names only. Adapter artifacts (MCP config, env block) are **generated on demand** by
`targets sync` under `graphify-out/targets/<name>/adapter/` (gitignored, regenerable) —
nothing persisted per project beyond the profile.

## Scenario analysis (recorded)

- **Self-modifications good for A, bad for B — real?** Real but bounded to parameters/rules
  (anti-Hive excludes code). Answer: layering + scope — effective thresholds = global merged
  with `target.selfReview`; `customRules.target` field (`<name>|self|*`); budgets/ratchets are
  per-target by construction; the I9 audit covers each target.json hash.
- **Secret leakage across targets**: spawn env is deny-by-default (`requiresEnv` only).
- **Target gate red vs harness gate**: independent subjects — the harness commit gate is not
  hostage to a target, but an agent working ON a target is blocked by the TARGET's gate
  (same proportional discipline).
- **Target moved/no git/OneDrive**: `target-missing` finding / calm degrade / retried IO.
- **Two harnesses on one target**: out of scope — one brain per target.

## Landmines (verified)

- Release hygiene forbids `graphify-out/*` and `.jsonl` — target state prefixes
  (`graphify-out/targets/`, `.harness/state/targets/`) must be allowlisted and spared by
  `cleanup_test_artifacts` (the MF.4 cache lesson).
- Target commands: `cwd=<target>`, absolute executable paths (Windows CreateProcess lesson),
  bounded timeouts, never network in generic checks.
- `changed_files` on targets = `git -C <path>` with calm degrade when not a git repo.
- Contracts (WORKER/HARNESS_RESULT) are repo-agnostic — unchanged.

## Acceptance criteria

- [x] A registered fake target runs the proportional gate: its failing test command turns the
      target gate red with an SPEC-101 fix-line; fixing turns it green; per-target
      quality-state is written and versioned.
- [x] Generic structural checks (syntax, compile, links, line budgets with offenders,
      market-file integrity, hygiene-lite) run over the target tree with zero network.
- [x] `graph-build-code-ast/discover/doc-find --target` produce per-target knowledge under
      `graphify-out/targets/<n>/`.
- [x] Self-review raises `target-*` findings into the existing funnel; a customRule scoped to
      another target does not fire; per-target ratchet tightens and never loosens.
- [x] `targets sync` generates the adapter with deny-by-default env (a key not in
      `requiresEnv` is absent).
- [x] Harness gates stay green throughout; target state survives cleanup and hygiene.
- [x] T6 delivered (protected-instruction snapshots per target, drift caught in the target
      gate). T5 **re-scoped** (size M): depends on MF.1 round 2 — parameterizing the workflow
      lifecycle by subject requires extracting it from harness.py first; tracked on the
      backlog as HT-T5.

## Validation (MVP gate)

`testing/scenarios/ht_targets.py` green end-to-end; manual run against a real local repo
(read/analyze + its own test command); SE (18/18), M4 (11/11), cli-golden regressions green;
harness commit gate green per batch.

## Escalation triggers

Any pressure to auto-execute changes in target code (critique proposes; agents/humans
execute); any need for harness state inside the target repo; network in gates.
