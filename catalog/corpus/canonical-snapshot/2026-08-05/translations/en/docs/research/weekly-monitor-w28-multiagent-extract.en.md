# Weekly Monitor W28 (multi-agent communication) — Harness Extract

Source: weekly GPT digest supplied by the owner (2026-07-13). This is NOT a research round; citations are
unverified `[web]` references — ideas were evaluated on internal merit against the real harness state. Third
in the series (`weekly-monitor-w28-memory-extract.md`, `weekly-monitor-w28-code-quality-extract.md`);
numbering continues (EXP-7..8).

## Where the harness ALREADY covers the digest (no new work)

| Digest finding | Equivalent already operating here |
|---|---|
| #1 Shared Selective Persistent Memory (Apple) | SAME paper already mapped in the memory extract: specs/ = task specifications, schemas/ = data schemas, .harness/routing + capabilities.json = tool configurations, subagent-contract + WORKER_RESULT schema = output constraints; session traces deliberately NOT promoted (checkpoint is bounded). The 5 suggested namespaces already exist under other names |
| LDT-Coord (“LLM proposes; runtime coordinates”) | This is the architecture thesis: workers return typed WORKER_RESULT, reduce is deterministic, plan briefs declare HARD footprint and overseer imposes disjointness for parallelism. What remains manual is disjointness checking → EXP-7 |
| AutoWorldBuilder (semantic locality in context assembly) | Packets embed only task spec/constraints; requiredReads with demotion by budget; context digest per workflow. What we NEVER measured is actual utilization of sent context → EXP-8 |
| ARCANA (structured blackboard) | Workflow directory (workers/, reduce/, trace.jsonl, seed-context.md) IS the blackboard: typed shared artifacts, not dialogue. Learned meta-controller is outside current profile (no own training) |
| GRACE (locally verified deltas instead of revalidating monolith) | Partial: instruction pack is validated by cheap deterministic gates (spec-pack in seconds) — the pain GRACE solves (LLM revalidation of monolithic prompt) does not exist here. Useful part (cross-references among instruction files) becomes a rider on EXP-4, not a new experiment |

## Extracted experiments (reversible; research-playbook template)

### EXP-7 — Footprint conflict preflight (LDT-Coord-inspired) · HIGH priority, tiny
- **Hypothesis:** the only coordination step in the parallel loop still done mentally is footprint
  disjointness among simultaneous briefs; one mistake here is exactly the class “parallelization breaks
  something” that the owner vetoed. Mechanizing it is nearly free: `parse_footprint` already exists
  (`overseer_review.py:50`).
- **Single phase:** `review --plans <briefA> <briefB> [...]` — intersect footprints for every pair; any
  common path → WARN naming the conflicting pair. Advisory rc 0 (overseer decides). Same seam as EXP-6
  `--preflight` — if both graduate, make it one mode.
- **Baseline/metric:** run against 12+ historical briefs from 2026-07-13 in the actual pairs launched
  together — expected 0 conflicts (waves were planned disjoint); anything >0 is a retroactive bug found.
- **Reversal:** advisory flag on an existing verb.

### EXP-8 — Semantic-locality audit (AutoWorldBuilder-inspired) · MEDIUM/HIGH priority
- **Hypothesis:** a material fraction of context embedded in packets is never cited by the worker — we pay
  assembly tokens for no return. The digest calls this “semantic locality”; we never measured it (token-audit
  measures COST of what was sent, not USE).
- **Baseline:** pairs already retained on disk per workflow — `workers/worker-NNN.prompt.md` (embedded
  files/sections) vs `worker-NNN.result.json` (`sourceFilesVerified` + `itemsAnalyzed`). Deterministic probe,
  zero LLM, only existing artifacts.
- **Metric:** % of embedded files/sections never cited, by worker profile and workflow; distribution, not
  average (a research worker legitimately cites less).
- **Phase 2 (only if waste is large):** assembly policy by workstream (packet receives only subset of declared
  scope) — behavior change decided with measured numbers.
- **Reversal:** phase 1 read-only; phase 2 would be reversible assembly config.

## Parked (with explicit trigger)

- **KV-PRM (verification via KV cache):** requires serving access; we are multi-vendor closed API. Trigger =
  self-hosted serving lane with open weights. Digest itself notes direct inapplicability.
- **GRACE as typed instruction graph:** trigger = instruction-pack validation becomes expensive or LLM-based;
  today deterministic pack runs in seconds — neighborhood verification would solve a cost we do not pay.
  Immediate rider: instruction files (.harness/context, prompts, playbooks) enter EXP-4 declared-vs-real
  inventory as a pair class (cited paths/commands exist).
- **ARCANA (differentiable blackboard + learned meta-controller):** trigger = harness learning phase
  (SELF_EVOLUTION I4 family, Deferred) — same bucket as retention reward from memory extract.
- **MCP revision of 2026-07-28** (stateless core, capability discovery, multi round-trip): known date — check
  impact on our MCP usage when released; nothing to do before then.

## Critical verdict on the digest

The week’s thesis — “do not transport conversations; transport selected memory, structured deltas,
constraints and references to already-computed state” — is literally the production architecture here:
packets + typed WORKER_RESULT + git-versioned canon + deterministic reduce. Of six papers, four confirm
already-made decisions (one repeats the memory digest). The genuinely useful pieces are two measurements:
EXP-7 mechanizes the last manual check in parallel coordination (near-zero cost, parser ready), and EXP-8
measures the semantic locality we always assumed and never counted — using artifacts already retained per
workflow. No new protocol in the window; nothing justifies an instruction graph or KV sharing before these
numbers exist.
