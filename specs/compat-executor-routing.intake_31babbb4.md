# Intake refinement -- compat-executor routing (door NEW)

SPEC-116 invariant 2 checklist. Seeds a future spec (`specs/40-features/compat-executor-routing.md`).

## Request (verbatim)

> queria que a gente conseguisse consumir esses modelos também como workers nos
> nossos workflows. também passarmos a adotar o uso de workers e cadeia de
> fallback oficial e configurável (lá na GUI como as outras) para soluções que
> hoje usam esses open AI compatible models como: graphify, research

(Context: "esses modelos" = the OpenAI-compatible executor family surfaced in
the fallback-chain status review this session: `openai-compat`, `nvidia-compat`,
`gemini-compat`, all SPEC-119 `tools/openai_worker.py` workers.)

## Owner decisions (2026-07-21, this session)

1. **Nomenclature.** "OpenAI-compatible" stops being a model category; it
   names only the wire protocol. Executor taxonomy is ONE axis — integration
   shape: `cli-agent` (vendor binary owns the loop: claude, codex, future
   kimi/zai CLIs) vs `http` (harness-owned loop via `openai_worker.py`).
   Orthogonal fields, not categories: `wire` (`openai` | `anthropic` |
   `gemini`) on http executors; `trustTier` gains `self-hosted` (local
   inference = `http` + localhost base_url, NOT a third category);
   open/closed weights = card tag for governance only. Today's
   `type: "cli"` on the HTTP workers is part of the mess and gets renamed.
2. **Graphify roles.** SPLIT by modality: `discovery-text` and
   `discovery-image`, each with its own fallback chain.
3. **Research.** FULL migration: wave executor+card selection resolves through
   routing roles; manual per-run pinning is no longer the interface for
   research waves.
4. **Chat mid-run failover.** Follow-up spec, out of scope here.
5. **Self-hosted executor ships in scope** *(v2, same session — owner
   environment facts)*. A `http` + `trustTier: self-hosted` executor is part
   of this spec. Owner setup: `llama.cpp` `llama-server` (fork
   `thecodacus/llama.cpp`, CUDA, WSL Ubuntu 24.04), OpenAI wire
   (`/v1/chat/completions`), currently keyless. base_url is NOT literally
   loopback: same-desktop = `http://127.0.0.1:<port>/v1`, harness-on-notebook
   = `http://<desktop-LAN-IP>:<port>/v1`. Keyless auth is accepted ONLY for
   loopback or explicitly allow-listed LAN hosts; external endpoints keep the
   credential requirement. First card: `qwen36-fast` =
   `unsloth/Qwen3.6-35B-A3B-GGUF` (quant `UD-Q5_K_M`, MoE, contextWindow
   65536, open-weights tag; intended: coding, general agentic execution,
   analysis, planning, debugging). Further local models = new cards only, no
   executor-spec change. The owner also runs **Hermes Agent** (Dockerized,
   tools, own loop) — `cli-agent` + `self-hosted`, slot = the existing
   `generic` placeholder; its non-interactive commandTemplate is unconfirmed
   and stays deferred config, NOT a spec blocker.
6. **`openai-compat` executor retired.** The cheap-http-fan-out niche is
   covered three times over (NVIDIA Build free credits, Gemini flash-lite,
   local `qwen36-fast` at zero cost); direct per-token api.openai.com adds a
   fourth provider for the same tier. Prune the executor + the empty `openai`
   card group; re-adding later is pure config (executor + cards), no spec
   change.

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search openai-compat routing fallback` | no hit -- `[]` |
| doc-find | `python scripts/harness.py doc-find openai compat worker fallback research` | top hit `specs/40-features/research-admin.md` (SPEC-125, round admin CRUD) -- adjacent, does not own routing |
| doc-find | `python scripts/harness.py doc-find spawn fallback worker executor circuit breaker` | `harness-sandbox` / `spawn-economy-guard` (spawn mediation + economy) -- not chain failover |

Adjacent specs EXIST but none owns this ground:

- **SPEC-115 model-routing** owns roles/chains, but consumption is chat
  construction (`build_engine` walk) + same-executor spawn override
  (`route_spawn`). No cross-executor failover for workers; the `openai` card
  group in `model-cards.json` is empty, so no chain hop can reference that
  executor today.
- **SPEC-119 openai worker**: the executors are runnable and already spawnable
  in workflows (task-profile spawn blocks carry `nvidia-compat`;
  `spawn_guard` points at `--executor nvidia-compat` as the cheap path) --
  but selection is manual per run; no official chain.
- **Graphify LLM-assisted discovery** has its own bespoke chain
  (`knowledgeGraph.apiAssistedProviders.order` in `.harness/project.json`,
  default `gemini-api -> nvidia-build`, models hardcoded in
  `tools/graphify/*_extract_fallback.py`) -- invisible to the routing GUI.
- **Research waves** map branches to task profiles (`review`/`scan`/`security`
  in `workflow-profiles.json`), so card/effort already flow through
  `route_spawn` -- but the executor per wave is pinned by hand and there is no
  failover when a circuit trips.

Decision: **NEW** -- making the compat family first-class in the official
routing (chain hops + worker failover + graphify/research adoption + GUI) is
unspecified anywhere a check can regress against.

## Goal

One sentence: `http` executors (the family formerly mislabeled "OpenAI
compatible") become first-class in the official model routing -- referable as
fallback-chain hops, walked at worker-spawn time when a hop is unusable, and
adopted as the ONLY model-selection seam for graphify discovery (text + image
roles) and research waves -- all configurable in the GUI like the existing
roles, under the cli-agent/http taxonomy.

## Scope

In scope:
- Executor taxonomy rename (owner decision 1): `executors.json` `type`
  becomes `cli-agent` | `http` (today everything says `"cli"`, including the
  HTTP workers); http executors carry a `wire` field; `trustTier` gains
  `self-hosted`; cards may carry an open-weights tag. Consumers that branch on
  the family (`agent_parity_conformance`'s detected `openai-compat-http`
  family) read the declared type instead of sniffing command templates.
- Cards for every runnable http executor: prune the `openai-compat` executor
  + its empty `openai` card group (owner decision 6); add a `gemini-compat`
  card (model today is pinned in the commandTemplate); `nvidia-compat`
  already has 5.
- A self-hosted `http` executor (owner decision 5): loopback OR allow-listed
  LAN base_url (the harness may run on a different machine than the inference
  server), OpenAI wire, `trustTier: self-hosted`, API key optional ONLY for
  loopback/allow-listed LAN hosts (the auth-failure classification must not
  misfire on keyless local config; external hosts keep requiring a key),
  plus the `qwen36-fast` card (later local models = new cards, no spec
  change); usable as a chain hop like any other http executor.
- Chain entries naming http executors: `_validate_entry` accepts them, GUI
  chain editor offers them (executor + card + effort, like claude/codex).
- Spawn-time chain walk for workers (`workflow run` / route loop): primary hop
  unusable (missing key, circuit `executor-circuit-*.json` open, spawn attempt
  classified by `runtimeLimits` patterns) -> next hop, one notice per hop, the
  workflow record carries `{fellBackTo, reason}` (mirror graph_providers' loud
  fallback); chain exhausted -> legible refusal. Canonical profile stays
  byte-compat (single attempt, exactly today's behavior).
- TWO routing roles for graphify LLM-assisted discovery (owner decision 2):
  `discovery-text` and `discovery-image`, each with its own chain; canonical
  derivation for both IS today's `gemini-api -> nvidia-build` order (image
  hops only on vision-capable cards); `discovery.py` consumes the roles
  instead of its bespoke `knowledgeGraph.apiAssistedProviders` chain.
- Research waves (owner decision 3): FULL migration — per-branch
  executor+card resolves through routing roles; the playbook's manual
  executor pinning is retired as an interface (the routing profile IS the
  knob).

Out of scope:
- Mid-conversation chat runtime failover (owner decision 4: follow-up spec).
- Extending the chat OpenAIEngine UX beyond what exists.
- trustTier gating/denial (stays declared-only, DW.1).
- Provider throughput/batch management beyond existing `runtimeLimits`.
- Adopting kimi/zai agentic CLIs (the taxonomy names the slot; adoption is
  its own ask).

## Actors & surfaces

- Actors: workflow spawn runner (`run_one_worker` seam), `model_routing`,
  `discovery.py`, research wave planner, spawn_guard, the GUI routing page.
- Surfaces (CLI / GUI / API / internal): CLI (`workflow plan/run`, `discover`,
  `models set-role`), GUI (routing page chain editor), internal (spawn +
  discovery seams).
- UI surface? **yes** -> Gherkin required in the resulting spec.

## Proposed acceptance criteria

- [ ] `executors.json` declares `type: cli-agent | http` (+ `wire` on http
  executors, `self-hosted` allowed in `trustTier`); family-branching consumers
  read the declared type; a migration shim or one-shot rewrite covers existing
  configs — no consumer left sniffing command templates.
- [ ] Every runnable executor in `executors.json` has >=1 card in
  `model-cards.json` or is explicitly marked non-routable; an empty card group
  can no longer make a configured chain hop silently unbuildable.
- [ ] `models set-role <role> --fallback nvidia-compat:z-ai/glm-5.2:high`
  validates, persists, and shows in `fallback_annotation`; the GUI chain
  editor offers http executors and their cards.
- [ ] Worker spawn walks the role chain: unusable primary -> next hop spawns
  with one notice, record carries `{fellBackTo, reason}`; exhausted chain ->
  legible refusal, zero silent downgrades.
- [ ] Canonical profile keeps byte-identical spawn behavior (SPEC-115
  invariant preserved; no chain = single attempt).
- [ ] spawn_guard evaluates the ACTUAL hop card (a fallback hop cannot smuggle
  a frontier card past the `--allow-frontier` ack).
- [ ] `discover` resolves text extraction via role `discovery-text` and image
  extraction via `discovery-image`, each walking its own chain; with no
  override, behavior is exactly today's `gemini-api -> nvidia-build`; an
  image hop never lands on a card without vision capability.
- [ ] Research wave planning resolves per-branch executor+card from routing
  roles alone (no manual pinning path remains in the playbook); a wave on a
  tripped circuit fails over per chain and the workflow record shows the hop.
- [ ] A self-hosted http executor spawns a worker keyless when its base_url
  host is loopback or on the executor's explicit LAN allow-list, and
  participates in chains as a hop; a keyless config pointing at any OTHER
  host is refused legibly (credential still required for external
  endpoints); the auth-failure classifier never misfires on permitted
  keyless config.
- [ ] The `qwen36-fast` card (`unsloth/Qwen3.6-35B-A3B-GGUF`, contextWindow
  65536, open-weights tag) resolves through the self-hosted executor and is
  selectable in GUI chain dropdowns like any card.
- [ ] Gherkin scenarios cover the GUI chain-editing flow for http executors.

## Risks / blast radius

Medium-high: touches the central worker spawn seam (`run_one_worker` /
`executor_profile_spawn`), spawn_guard interplay (frontier ack per actual hop),
circuit-breaker interplay (reuse `executor-circuit-*.json` as the "hop
unusable" signal -- do not invent a second detector), `discovery.py`, and the
GUI routing page. `accountingSemantics` differs per executor (gemini =
emulated) -- cost records must attribute the hop that actually ran. The
`type` rename touches every consumer that reads `executors.json` (parity
conformance, sandbox_spawn vendor branch, GUI executor list) -- inventory
them in the spec. Pruning `openai-compat` (decision 6) touches fixtures and
tests that name it (`route_tuple`, `scenario_isolation` circuit files,
`sandbox_spawn` self-checks, the research-skill stub scenario, the
`openai-compat-http` family label) -- rename/repoint, don't orphan. Research FULL migration rewrites the playbook's budget &
executors section; rollback there = restore the pinning table. Otherwise:
chains without http hops behave exactly as today; role consumption stays
behind the canonical byte-compat invariant.

## Open questions for the human

None — all six owner decisions recorded above (2026-07-21). Intake CLOSED;
next step is the spec from `specs/SPEC_TEMPLATE.md` seeded by the acceptance
criteria (Gherkin required — GUI surface).
