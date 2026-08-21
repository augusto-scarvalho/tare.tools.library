# SPEC-165 — Compat-executor routing: http executors first-class in model routing

Status: SPEC-165, proposed 2026-07-21 (acceptance: `testing/scenarios/cer_compat_routing.py`,
lands with slice 1 — see Validation).

Intake (SPEC-116 door NEW, from `specs/40-features/compat-executor-routing.intake.md`):
owner request 2026-07-21 — consume the OpenAI-compatible model family as workflow
workers under the OFFICIAL, GUI-configurable fallback-chain routing, and migrate
the solutions that use them ad hoc today (graphify discovery, research waves).
Six owner decisions recorded in the intake one-pager govern this spec.

## Goal

`http` executors (the family formerly mislabeled "OpenAI compatible") become
first-class citizens of SPEC-115 model routing: declarable as fallback-chain
hops, walked at worker-spawn time when a hop is unusable, and the ONLY
model-selection seam for graphify LLM-assisted discovery (text + image roles)
and research waves — all configurable in the GUI like the existing roles,
under a declared `cli-agent`/`http` executor taxonomy that includes the
owner's self-hosted llama.cpp endpoint.

## Applicability

`.harness/routing/executors.json` + `model-cards.json` + `model-routing.json`
(schema), `harness_lib/model_routing.py` (validation/resolution),
`tools/openai_worker.py` (keyless policy), the worker spawn seam in
`scripts/harness.py` (`executor_profile_spawn`/`run_one_worker`),
`harness_lib/spawn_guard.py`, `harness_lib/discovery.py`, the research
playbook executor section, `harness_lib/agent_parity_conformance.py` (family
detection), and the GUI routing page. Explicitly NOT covered: mid-conversation
chat runtime failover (owner decision 4 — follow-up spec); adopting zai
agentic CLIs (taxonomy names the slot only; kimi adopted — amendment v3);
trustTier gating/denial (stays
declared-only, DW.1); provider throughput/batch management beyond existing
`runtimeLimits`.

## Requirements / invariants (numbered, testable)

1. **Declared taxonomy.** Every executor declares `type: "cli-agent" | "http"`
   (today's `"cli"` is retired). `http` executors additionally declare
   `wire: "openai" | "anthropic" | "gemini"`. `trustTier` admits
   `"self-hosted"` alongside `first-party`/`third-party`. Family-branching
   consumers (`agent_parity_conformance._family`, sandbox vendor derivation)
   read the declared `type` first; command-template sniffing survives only as
   fallback for undeclared/legacy entries.
2. **Routability guard.** Every `runnable: true` executor has ≥1 card in
   `model-cards.json` under its group, OR is explicitly marked
   `nonRoutable: true`. A chain entry naming an executor with no cards fails
   validation legibly — an empty card group can never make a configured hop
   silently unbuildable.
3. **Http hops in chains.** `models set-role <role> --fallback
   <http-exec>:<card>:<effort>` validates, persists, and renders in
   `fallback_annotation`; `resolve_role`/`chat_fallbacks` return http hops
   like any other.
4. **`openai-compat` retired.** No `openai-compat` executor and no empty
   `openai` card group remain; every fixture/test that named it is repointed
   (rename, never orphaned). Direct per-token api.openai.com returns, if
   ever, as pure config — no spec change.
5. **Self-hosted executor.** A `type: http, wire: openai,
   trustTier: self-hosted` executor exists for the owner's llama.cpp
   `llama-server` (OpenAI wire, `/v1/chat/completions`). Its base_url may be
   loopback OR an explicitly configured LAN host (harness-on-notebook →
   inference-on-desktop); allow-hosts is exactly loopback + the configured
   LAN hosts, nothing else. First card: `qwen36-fast`
   (`unsloth/Qwen3.6-35B-A3B-GGUF`, quant UD-Q5_K_M, MoE, contextWindow
   65536, open-weights tag). Further local models = new cards only.
6. **Keyless only where permitted.** `tools/openai_worker.py` proceeds
   without an API key ONLY when the target host is loopback or on the
   executor's explicit allow-list; keyless config pointing anywhere else is
   refused legibly BEFORE any request. The auth-failure classifier
   (`runtimeLimits.authFailurePatterns`) never fires on permitted keyless
   config; external endpoints keep requiring a credential.
7. **Spawn-time chain walk.** Worker spawn resolves the role's chain: an
   unusable hop (missing key/env, open `executor-circuit-<name>.json`
   breaker, or a spawn attempt classified by `runtimeLimits` patterns) falls
   to the next hop with ONE notice; the workflow record carries
   `{fellBackTo, reason}` (graph_providers' loud-fallback shape). An
   exhausted chain refuses legibly — zero silent downgrades. Under the
   canonical profile the chain is empty and spawn behavior stays
   byte-identical (SPEC-115 invariant preserved).
8. **Guard the actual hop.** `spawn_guard` evaluates the card of the hop
   that actually spawns — a fallback hop cannot smuggle a frontier card past
   the `--allow-frontier` ack (SPEC-153 composition).
9. **Discovery roles.** Graphify LLM-assisted discovery resolves through TWO
   routing roles — `discovery-text` and `discovery-image` — each with its
   own chain; canonical derivation for both IS today's
   `gemini-api -> nvidia-build` order, so no-override behavior is
   byte-compatible. An image hop never lands on a card without the
   vision-capability tag. `discovery.py` stops reading its bespoke
   `knowledgeGraph.apiAssistedProviders` chain once the roles resolve.
10. **Research full migration.** Research wave planning resolves per-branch
    executor+card from routing roles alone; the playbook's manual pinning
    table is retired as an interface. A wave hitting a tripped circuit fails
    over per rule 7 and the workflow record shows the hop.
11. **GUI chain editor parity.** The routing page offers http executors and
    their cards in role chain dropdowns exactly like claude/codex entries.
    Gherkin scenarios for this flow are appended as a versioned amendment
    when the GUI slice ships (SPEC-116 inv. 4 satisfied at that point; the
    scenarios were drafted at refinement time in the intake's acceptance
    criteria).
12. **Accounting attributes the real hop.** Cost/usage records attribute the
    executor+card that actually ran (per-executor `accountingSemantics`,
    e.g. gemini = emulated), never the primary that was skipped.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Fallback-chain pattern extended from chat construction to worker spawn | SPEC-115 grounding (LiteLLM Router fallbacks, OpenRouter provider routing); `build_engine` walk (`chat_engines.py:842-881`); groom 2026-07-21 finding: `route_spawn` overrides same-executor only |
| One taxonomy axis (who owns the loop), orthogonal fields for wire/hosting/license | Owner decision 1 (2026-07-21): the proposed 3-way vendor split double-boxed Anthropic/Zai/Kimi; `agent_parity_conformance.py:84-88` already invented the `openai-compat-http` family by template-sniffing — this spec makes it declared |
| Reuse the circuit breaker as the "hop unusable" signal | `executor-circuit-*.json` exists and is scenario-covered (`scenario_isolation.py:375-405`); a second detector would drift |
| Split discovery text/image roles | Owner decision 2; `discovery.py:48-74` provider chain hardcodes gemini→nvidia with per-provider scripts (text/image differ in capability requirements) |
| Research full migration (no manual pinning) | Owner decision 3; research playbook §Budget & executors pins executors by hand today; `workflow-profiles.json` branches already map to task profiles = routing roles |
| Retire `openai-compat` | Owner decision 6: the cheap-http niche is covered 3× (NVIDIA free credits, Gemini flash-lite, local qwen36-fast at zero cost); codex CLI already covers GPT under subscription |
| Self-hosted = http + trustTier, not a category; LAN reachable; keyless scoped | Owner decisions 1+5 + environment facts (llama.cpp thecodacus fork, CUDA, WSL Ubuntu 24.04; desktop 127.0.0.1 vs notebook→LAN-IP); keyless-only-for-permitted-hosts keeps the credential requirement for external endpoints (security triage 2026-07-21) |
| Guard evaluates the actual hop | Cost incident 2026-07-15 + SPEC-153: a chain must not become a frontier-smuggling path |
| Spawn-guard/cards groundwork | Spawn-economy audit: `spawn_guard.py:37-116` already reasons over nvidia-compat namespaced cards |

## Ceilings (upgrade paths)

- LAN allow-list is a static config list; no discovery/mDNS. Add only if the
  owner's topology grows beyond desktop+notebook.
- Vision capability is a card TAG, not probed; a mistagged card fails at call
  time with the provider's own error. Probe-on-add only if mistags recur.
- Failover detects at the SPAWN boundary; a worker dying mid-run is the
  workflow layer's retry concern, not a chain hop. Revisit only with
  evidence of mid-run provider flaps.
- Chat mid-run failover: deliberately out (owner decision 4) — follow-up
  spec.

## Test strategy

- Behaviors: taxonomy fields validate; routability guard refuses cardless
  hops; http chain entries round-trip set-role→resolve→annotation; keyless
  loopback/LAN accepted vs external refused; spawn walk falls over on open
  circuit + missing key, records `{fellBackTo, reason}`, refuses on
  exhaustion; canonical byte-compat (spawn output identical with routing
  file absent); guard-on-actual-hop; discovery roles canonical derivation
  byte-compat; research wave resolution.
- Edge cases: executor with `nonRoutable: true`; keyless config on
  non-loopback non-listed host; chain where EVERY hop is unusable; circuit
  file present but `closed`; role with contextDiet riding a http hop
  (structurally no-op, must not crash).
- Regression risks: SPEC-115 byte-compat under canonical (existing
  `model_routing.py` self-check asserts it); rs_research_skill stub flows
  after the openai-compat rename; hos/route_tuple vendor strings; SPEC-153
  guard behavior on width-1 spawns.
- Coverage impact: enforced (new scenario + existing mr/rs/ap/hos batteries).

## Validation

- `python testing/scenarios/cer_compat_routing.py` and
  `testing/scenarios/cer5_gui_chains.py` — the acceptance scenarios,
  landing WITH slice 1 (checks `cer-1..cer-n` cover rules 1-6; slices 2-4 add
  checks for rules 7-10, 12; the GUI slice adds rule 11's Gherkin + checks).
- Existing batteries named in Test strategy rerun green per slice:
  `model_routing.py` self-check (canonical byte-compat), `rs_research_skill`,
  `ap_agent_parity`, `hos_harness_sandbox`, `spawn_guard` self-check.
- Slice plan (each slice = one committable green batch; rows in
  `docs/IMPLEMENTATION_BACKLOG.md`):
  1. `cer-slice1-taxonomy-selfhosted` — rules 1-6 (schema rename, cards,
     openai-compat→local-llama rename with test repointing, keyless policy,
     acceptance scenario file).
  2. `cer-slice2-spawn-failover` — rules 7, 8, 12.
  3. `cer-slice3-discovery-roles` — rule 9.
  4. `cer-slice4-research-migration` — rule 10.
  5. `cer-slice5-gui-chains` — rule 11 + Gherkin amendment.

## Amendments

### v2 (2026-07-21) — GUI chain editor Gherkin (slice 5)

```gherkin
Feature: fallback chains configurable over http executors in the GUI

  Scenario: [cer5-snapshot-http-cards] http executor cards reach the chain dropdowns
    Given the routing config view is loaded
    When the owner opens a role's chain editor
    Then the card selector offers the self-hosted and third-party http cards grouped by executor

  Scenario: [cer5-set-role-http-hop] saving a chain with an http fallback persists it
    Given a role chain with a claude primary
    When the owner adds the local qwen card as a fallback and saves
    Then the routing profile persists the http hop and the chain annotation shows it
```

### v3 (2026-07-28) — kimi cli-agent adoption (the named slot, kimi half)

Owner request 2026-07-28: adopt the Kimi Code CLI (MoonshotAI kimi-code) as a
worker executor — the subscription already exists and idle capacity should
absorb queue work. This fills the kimi half of the "adopting kimi/zai agentic
CLIs" slot that Applicability had explicitly left open; zai remains open.

Adoption is PURE CONFIG within the declared R1 taxonomy plus one gauge probe —
no new mechanism, so it lands as this amendment, not a new spec:

- `executors.json`: `kimi` card, `type: cli-agent`, `trustTier: first-party`
  (vendor-owned CLI, same class as claude/codex). Template
  `kimi -m {model} -p {prompt}` — measured: `-p` auto-executes tool calls by
  itself, and `--auto`/`-y` REFUSE to combine with `-p`, so there is no
  permission flag to carry. Text output — stream-json exists but no parser is
  wired.
- `model-cards.json`: `kimi` group — `kimi-code/k3-256k` (smart, default) and
  `kimi-code/kimi-for-coding` (cheap/fast K2.7), satisfying the R2 routability
  guard. Aliases mirror the operator's `~/.kimi-code/config.toml`. The
  highspeed sibling 401s on the current plan (measured) and ships no card.
- `task-profiles.json`: a `kimi` spawn block in every profile — cheap-by-
  construction profiles (scan, cheap, ui-validation, router) ride
  kimi-for-coding, the rest ride k3-256k.
- `vendor_fuel.py`: `kimi` joins `VENDORS`. Same-day correction: the first cut
  shipped `--version` liveness ("quota not exposed") because the CLI exposes no
  usage surface — but the SUBSCRIPTION API does: `GET /coding/v1/usages` with
  the CLI's OAuth token (endpoint surfaced by the community tracker
  Golden0Voyager/kimi-code-usage; upstream feature request
  MoonshotAI/kimi-cli#2169 confirms the TUI-only gap). The probe now reads a
  REAL weekly pct (binding window, claude's week-all rule) + 5h window +
  membership; 401 stale-token stays fresh/pct=null (codex no-current-reading
  rule); userId/businessId are PII-stripped; no token -> `--version` liveness.
  Auth/quota exhaustion still classifies at spawn time via `runtimeLimits`.

Measured ceilings (kimi-code 0.29.2, recorded on the executor card): no
per-invocation effort flag — thinking effort rides the operator config's
`[thinking]` default (high), so spawn mappings pin model only; upgrade path is
a template flag when the CLI grows one. `maxConcurrency: 1` until subscription
rate behavior is observed under load.

### v4 (2026-07-28) — R13: opt-in gas balancer for the spawn chain walk

Owner request 2026-07-28: during delegations, optionally prioritize vendors
with the most gas remaining. SPEC-116 covered door: this extends R7's declared
walk with an ordering mode — no new walk, no new detector — so it lands as a
numbered rule via amendment.

13. **Gas-balanced fallback order (opt-in).** `spawn_chain` re-ranks a role's
    FALLBACKS by fresh fuel reading before the R7 walk when — and only when —
    the strategy resolves to `gas`. Resolution: `HARNESS_SPAWN_BALANCE`
    (`gas` | `quality`, per-run, wins both ways) > the role's `strategy`
    field in `model-routing.json` (set via `routing set-role --strategy gas`;
    `quality` clears; omitted preserves — the contextDiet rule) > default
    `quality`. Ordering (owner decisions 2026-07-28): the PRIMARY is never
    moved (the chain's head stays the quality choice); fallbacks with a
    FRESH numeric pct (`vendor_fuel.show` + `effectiveStatus`) sort most-gas
    first, ties keep chain order; stale/unavailable/pct-null readings are
    excluded (the 54h-rollout lesson — an expired number routes worse than
    none) and those hops follow in chain order. Default (no env, no field)
    is byte-identical to the pre-R13 chain (SPEC-115 invariant). A reorder
    that changes the order announces itself on stderr. Acceptance:
    `cer2-9:gas-balancer` in `testing/scenarios/cer2_spawn_failover.py`.

### v5 (2026-08-01) — R14: uniform operator spawn pin (`--model/--effort`) on `workflow run/start`

DD-mechanization P1 (design study `.harness/handoff/design-dd-mechanization.md` §4/§8).
A homogeneous per-executor wave needs to declare its seat once, instead of the
`ui-validation`→sonnet taskProfile hack (which conflated task semantics with model
choice). SPEC-116 covered door: this rides the EXISTING `resolved_spawn`
`spawn_override` seam (`workflow_spawn.py:38-53`, the SPEC-115 failover pin) — no new
resolution path — so it lands as a numbered rule via amendment.

14. **Uniform operator spawn pin.** `workflow run` and `workflow start` accept
    `--model M` / `--effort E`. When present, the pin overrides the routed/profile
    spawn UNIFORMLY for every runnable worker, riding `resolved_spawn`'s
    `spawn_override` so each worker's spawn COMMAND and its `HARNESS_SESSION_*` seat
    derive from ONE resolution and cannot drift. The override sets `model` and
    `effort` (the shipped claude/codex templates render `{effort}`, and both the
    seat and the `{effort}` slot read `effort` before `reasoning`, so the pin reaches
    command and seat on every executor; no executor renders `{reasoning}`, so the
    `resolved_spawn` `{reasoning}` symmetry is dormant and the pin does NOT set it —
    a `{reasoning}`-rendering executor would add the key WITH its tooth). The pin is
    EXACT with no fallback: an invalid executor/card combo fails legibly at the
    executor; the harness never re-resolves or substitutes it. Precedence: explicit
    `--model/--effort` > routed/profile spawn. On an R7 chain walk the pin governs the
    PRIMARY hop (`i == 0`) only; failover hops keep their chain card — the per-hop
    Rule-8 guard likewise judges the pin at the primary hop and the chain card at
    fallbacks (it always judges the card that hop will run). `--model` without
    `--executor` applies to whatever executor each worker
    resolves under R10. `workflow resume` does NOT carry the flags in this version
    (deferred; one-kwarg follow-up at the `workflow_resume`→`workflow_run` delegation).
    Omitting both flags is byte-identical to the pre-R14 spawn (`spawn_override=None`
    is falsy at every consumer). Teeth: `dlc-l1-user-pin-seat`
    (`testing/scenarios/dlc_session_seat.py`), `sg-19`/`sg-20`
    (`testing/scenarios/sg_spawn_economy.py`). See also SPEC-153 v4 (the guard judges
    the pin).

### v6 (2026-08-02) -- R15: per-branch `spawn` seats on blocking workflow runs

DD-mechanization P6 Slice 1 (`.harness/handoff/brief-ddmech-p6s1.md`). This is a
versioned COVERED-door amendment of R10/R14: it adds no spawn seam and changes no
result contract.

15. **Per-branch seat on the blocking path.** A fork-join branch may declare
    `spawn: {executor?, model?, effort?}`. Planning carries the object into the
    worker packet and its scope, rejects a non-object, unknown keys, or an unknown
    executor before materialization, and leaves spawn-free packets byte-compatible
    (no `spawn` key). `workflow run` resolves each runnable worker exactly once with
    executor precedence `--executor` > `branch.spawn.executor` > non-canonical
    routing primary > active default. Model/effort precedence is the uniform run
    pin > the branch pin > the routed/profile spawn; the merged per-worker override
    rides the existing `resolved_spawn` seam, so command and `HARNESS_SESSION_*`
    seat still derive from one resolution. The blocking concurrency is clamped by
    every distinct resolved executor's declared limit, emitting the existing cap
    event. `workflow start` refuses every worker packet carrying `branch.spawn`
    until Slice 2 adds per-executor async scheduling; it must never silently run a
    heterogeneous declaration as one homogeneous async group.

**Research isolation invariant (INV-1).** This seat/config resolution moves no
worker finding. The driver continues to aggregate only workflow handles and status;
worker results reach it only through the final reduce, and a reduced result seeds the
next workflow directly. The result-collection half of `workflow_run` never reads
`branch.spawn`, so no same-executor material crosses through the overseer.

| Decision | Sources |
|---|---|
| Reuse `resolved_spawn`; merge only at the caller | R14's command/seat single-resolution invariant; live seam `workflow_spawn.resolved_spawn` |
| Run flag > branch > route/default | Owner precedence in `brief-ddmech-p6s1.md` and the existing explicit-override behavior in R10/R14 |
| Refuse async until per-executor scheduling exists | P6 Slice 1 scope boundary; the current async group stores one executor for every task |
| Clamp the blocking run over distinct seats | OD-2: a mixed blocking run must not exceed any participating executor's declared cap |
| Preserve INV-1 | OD-5: double-diamond results remain isolated until final reduce |

Test strategy: `testing/scenarios/bs_branch_spawn.py` checks plan carry/refusal,
materialization, seat and override precedence, blocking cap events, zero-spawn
frontier refusal, per-worker reducer access, async refusal, and INV-1. Existing
`cer4_research_migration.py` remains the R10 blocking-path regression. Validation:
run both scenarios plus `sg_spawn_economy.py`, `wt_workflow_tree.py`, and the
`spec-pack` gate. Async per-executor semaphores/scheduler remain Slice 2.

### v7 (2026-08-02) -- R16: physically heterogeneous async workflow starts

DD-mechanization P6 Slice 2 (`.harness/handoff/brief-ddmech-p6s2.md`). This is a
versioned COVERED-door amendment of R15: it removes the temporary async refusal
after adding the per-worker materialization and per-executor throttle it required.

16. **Per-branch seats on the async path.** `workflow start` resolves each runnable
    worker once with the R15 executor and model/effort precedence, persists that
    origin executor with the task, and uses it for queued status and events. The
    async group retains its start-level `executor` as the compatibility fallback and
    additionally records the participating `executors`, independent `executorCaps`,
    and round `workerExecutors`. The global consumer pool remains the total in-flight
    ceiling. Below it, one `asyncio.Semaphore` per persisted task executor applies
    that executor's own runtime/configured cap; one executor's small cap never clamps
    another executor's semaphore. The supervisor re-derives the cap map from persisted
    tasks and existing policy, without a new transport or state file. A failover hop
    looks up `throttles.get(executor_name)`, where the parameter is the current hop;
    the stable task `executor` remains origin attribution. A missing throttle acquires
    nothing. The current-hop semaphore is released before failover recursion begins,
    so a worker holds at most one executor semaphore. Together with monotonic,
    acyclic failover-chain advancement, this removes hold-and-wait cycles and is the
    OD-3 deadlock-freedom guarantee. `executor_resolver=None` preserves legacy
    spawn-free task and group JSON, and research isolation INV-1 remains unchanged:
    the supervisor aggregates task status and handles only; findings still cross only
    through `WORKER_RESULT` -> reducer -> `REDUCE_RESULT`.

| Decision | Sources |
|---|---|
| Separate executor semaphores below the unchanged global pool | P6 Slice 2 OD-2; the prior async runtime had only a fixed consumer pool and a one-executor clamp |
| Key acquisition by the current-hop parameter | P6 Slice 2 round-2 R1; failover recursion passes the next executor while task executor remains the origin |
| Release before failover recursion | P6 Slice 2 round-2 R2 / OD-3; holding origin and fallback semaphores would permit deadlock |
| Preserve legacy JSON and INV-1 | P6 Slice 2 OD-5; existing reducer-only findings boundary |

Test strategy: `bs-7` materializes two branch executors and independent caps in
dry-run; `bs-8` checks cap independence, persisted-executor semaphore construction,
current-hop acquisition, and proves failover recursion is lexically outside the
`async with`. `sg-20` pins per-worker seat and branch-aware guard wiring while `bs-6`
continues to cover INV-1 unchanged. Validation: run `bs_branch_spawn.py`,
`sg_spawn_economy.py`, `wt_workflow_tree.py`, `sv_autostart_workflow.py`,
`rs_research_skill.py`, and the `spec-pack` gate.
