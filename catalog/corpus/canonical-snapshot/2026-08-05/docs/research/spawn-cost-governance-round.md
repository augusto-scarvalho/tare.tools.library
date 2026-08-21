# Research round — governing dynamic-path spawn cost (failover / retry / fallback / escalation)

Double Diamond over the harness (`.harness/prompts/research-playbook.md`). Orchestrator: this session
(Opus overseer). Executors: **Sonnet 5** (discovery + critique) + **NVIDIA** (`nvidia-compat`, divergence
fan-out — as balanced cross-vendor per the last round; the workflow's `claude`/"plan" leg is Fable, so
Sonnet-5 ideation rides `model:sonnet` subagents, never the claude executor — D032/D032-guard). Started 2026-07-19.

> **Sequencing:** the SPEC-153 v3 (async spawn-guard) `validate --staged` gate is IN FLIGHT. Phases 0-2
> write only `docs/` (safe). Phase 3+ (`workflow plan`, DECISIONS, registry) start ONLY after that gate
> passes and the async-close is committed (SPEC-137: no `.harness/` write or commit while a gate runs).

## The problem (concrete trigger)

The spawn-economy guard (SPEC-153) gates at PLAN/START time on fan-out **width > 1** on a frontier card.
The Sonnet reckon found it is structurally blind to a THIRD path (D033): the SPEC-115 mid-workflow
**failover hop** re-spawns a rate-limited worker on the routing chain's **fallback card** without the
guard — so an N-worker fan-out planned on a CHEAP executor (passes the plan-time gate) can fail its
workers over **individually** (each hop is width-1) onto a frontier fallback → a **cumulative** frontier
fan-out no single check sees. Generalize: **how do you govern the cumulative resource/credit cost of a
multi-agent workflow when the cost accrues through DYNAMIC paths — failover, retry, fallback,
escalation, recursion — that are invisible at plan/start time?** A per-call-site, width-based gate is the
wrong shape for it.

## Question

How do OTHER agent harnesses / multi-agent frameworks handle mid-run spawn-cost governance (failover,
retry, fallback, model-escalation) — did they SOLVE it, or work around it, and how? How do PAPERS study
budget-constrained / cost-aware agent orchestration? Which CLASSIC patterns (retry budgets, token
buckets, admission control, circuit breakers, cost-aware cascades, backpressure) transfer? And how can
OUR reference manuscript (`docs/research/sources/adaptive-project-oriented-multi-agent-harness-
architectures.md`) + the harness's measure-honesty / measure-first DNA contribute to the solution?

## Success criteria

- **Actors:** the workflow runtime (the failover/retry path), the overseer (sets/reads budgets), the
  owner (credit spend), an experiment (measures the leakage + a control's effect).
- **Constraints (our invariants):** harness-native (canonical state in `.harness/`); derived/measured,
  not fabricated (a cost figure is REAL or `—`); cheap-first; the guard must be a DIFFERENT shape than
  width>1 (per-hop or cumulative-per-group), vendor-independent, fail-safe; measure-before-control
  (measure the real failover-frontier leakage before adding a control — D008); reversible.
- **A good answer delivers:** a portfolio of governance patterns (classic + AI) scored novelty × maturity;
  a recommended shape for OUR v4 (per-hop frontier gate vs cumulative-per-group frontier budget vs
  a retry-budget-style ceiling); at least one measurable experiment (the real leakage + the control);
  and an explicit read of what our manuscript contributes.

## Declared budget + width (Phase 0 gate)

- **Phase 1 Discover (now, gate-safe):** 4 background discovery workers, **Sonnet 5 high**, WebSearch/
  WebFetch, EXPLORATORY. Each returns an evidence table (claim | source | type | year | confidence |
  maturity), `[web]`/`[repo]`/`[judgment]` prefixed; bounded to primary sources, no code writes.
- **Width (D010):** EXPLORATORY — scanning a whole field (framework practice + cost-aware-orchestration
  papers + distributed-systems governance + cost-accounting) with no implementation target chosen yet →
  4 perspective-clusters, one worker each; nominal-group diversity pays (Diehl & Stroebe 1987).
- **Phase 3 Develop (post-commit):** 1 divergence wave, 5 ideators, **NVIDIA** (`nvidia-compat`).
  **Phase 4 Refine:** 1 critique wave, **Sonnet 5**, seeded. Cross-vendor per wave (generator ≠ critic).

## Declared design (L18 — this round feeds an experiment)

Measurable claims + methods from `docs/EXPERIMENT_METHODS.md`:
- **Failover-frontier leakage (measure-FIRST):** a measure-only probe over real/replayed workflow runs
  emitting how often failover re-spawns land on a frontier card + the cumulative frontier tokens/credits
  it costs — BEFORE any v4 control acts. **measure-before-control (D008)** + a **noise floor** (baseline
  frontier spend with no failover). Anti-fabrication: real cost or `—`.
- **Control comparison (if pursued):** per-hop gate vs cumulative-group budget vs retry-budget ceiling →
  **matched-budget** + evidence-grades/confidence-sequences for any promotion.

## Phase 0 — prior art in-repo (avoid re-derivation) · `[repo]`

- `[repo] docs/WORKFLOW_TOKEN_ECONOMICS.md` — the harness's token-economics model (charsPerToken
  calibration, per-worker/required-reads cost, budget ceilings). The cost-accounting substrate a v4 budget
  would ride.
- `[repo]` the executor **circuit breaker** (`.harness/routing/executors.json` runtimeLimits +
  `executor-circuit-*.json`; `route_ledger`, `cost_metrics`) — a per-executor breaker EXISTS; the failover
  chain (`model_routing.resolve_role` fallbacks + `workflow_async_run_one_worker` / `workflow_next_failover`)
  is what re-spawns. The seam a per-hop or per-group cost gate would attach to.
- `[repo]` SPEC-153 spawn-economy guard (the plan/start-time width>1 gate) + D033 (the failover residual).
- `[repo]` the reference manuscript `docs/research/sources/adaptive-project-oriented-multi-agent-harness-
  architectures.md` (the source of the methods library: Taguchi, noise floor, evidence grades,
  marginal-contribution Δm, measure-honesty) — front #4 engages it directly.

## Phase 1 discovery perspectives (the 4 workers)

1. **Agent frameworks — mid-run spawn/cost governance (bleeding edge).** How LangGraph, AutoGen (v0.4+),
   CrewAI, OpenAI Agents SDK / Swarm, Anthropic's multi-agent research system + Claude Agent SDK, Devin,
   LlamaIndex, DSPy, Semantic Kernel handle: per-run token/cost BUDGETS, cost ceilings, failover/fallback
   MODEL policies, retry cost, model-escalation. Did they SOLVE mid-run cost governance or WORK AROUND it?
2. **Papers — cost-aware / budget-constrained LLM orchestration.** FrugalGPT + LLM CASCADES, cost-aware
   routing / model-selection under budget, budget-constrained agent planning, "when to escalate to a
   bigger model", resource-bounded / anytime computation, LLM-serving cost control, cascade/speculative
   economics. What's the theory of "spend a bigger model only when justified"?
3. **Classic distributed-systems governance (the strongest analogues).** Google SRE **RETRY BUDGETS** (the
   retry-storm problem — a direct analogue of failover-storm), **token/leaky bucket** rate limiting,
   **admission control**, **circuit breakers + fallback cost**, backpressure/load-shedding, cloud
   **budget/quota** governance (AWS Budgets, GCP quotas), autoscaling cost caps. Map each to the
   cumulative-frontier-via-failover problem.
4. **Cost accounting over dynamic graphs + OUR manuscript's contribution.** Cost attribution/accounting
   across dynamic execution DAGs, per-group/per-workflow budgets, provenance-of-cost; then READ our
   reference manuscript + `WORKFLOW_TOKEN_ECONOMICS.md` + the circuit breaker and say concretely how the
   manuscript's framework (marginal-contribution Δm, measure-honesty, adaptive orchestration) + our
   existing seams inform a v4 design (per-hop gate vs cumulative-group budget vs retry-budget ceiling).

## Phase 1 — evidence synthesis (4 Sonnet 5 workers, WebSearch, 2026-07-19)

Curated cross-worker matrix (load-bearing claims; `[web]` primary-sourced unless marked). NUMBERS
tagged `preliminar` where a worker got them via WebFetch summary (not re-read from the PDF) — do not
cite as verified.

| # | Claim (synthesized) | Source | confidence | maturity |
|---|---|---|---|---|
| E1 | **The industry does NOT govern mid-run cost in the loop — it puts an EXTERNAL cost gateway in front** (LiteLLM/Portkey). Both OpenAI's and Anthropic's own docs point OUTWARD to a proxy for spend enforcement their SDKs lack | OpenAI Agents SDK / Anthropic docs (fetched) | forte | produção (workaround) |
| E2 | Most agent frameworks have NO mid-run cost governance: LangGraph = step-count `recursion_limit`; AutoGen `TokenUsageTermination` = token count post-hoc; CrewAI `max_rpm`/`max_iter` = blunt (own community); OpenAI guardrails = content only; DSPy budget = unmerged PR | framework docs/issues (fetched) | forte | produção |
| E3 | **Claude Agent SDK `max_budget_usd` is the ONLY first-class cumulative $-ceiling** that halts a run + rolls up subagent-tree cost — but it is a CLIENT-SIDE ESTIMATE, "not authoritative billing" | code.claude.com/docs agent-sdk cost-tracking | moderada | produção |
| E4 | **Anthropic's own harness (Claude Code) fallback fires ONLY on overload/unavailable — rate-limit NEVER switches model** ("auth, billing, rate-limit... follow normal retry"). So **failover-onto-a-bigger-model-on-rate-limit is a CUSTOM policy no framework governs natively** — exactly our failover hop | code.claude.com/docs/model-config (quoted) | forte | produção |
| E5 | **The direct analogue is the SRE RETRY BUDGET / retry-storm:** cap retries to ~10% of successful traffic per client per window + max 3 attempts + backend "don't retry" signal; over budget -> fail fast | Google SRE Book ch.21-22 | forte | produção |
| E6 | **THE bug, named:** a circuit breaker caps calls to the FAILING dependency but does NOT cap volume/cost into the FALLBACK path — "a breaker alone routes 100% of denied traffic into the costly fallback unless the fallback is SEPARATELY rate-limited." Our breaker trips on failure-RATE, not cost | Netflix/Hystrix wiki row 8 | forte | produção |
| E7 | **$ budget ALERTS are structurally too slow** for a minutes-long storm: AWS Budget Actions reset per period + 8-24h billing lag; GCP "setting a budget does NOT cap usage" (quoted). Only a SYNCHRONOUS PRE-ADMISSION check (quota) brakes it in time | AWS/GCP docs (fetched) | forte | produção |
| E8 | **Hierarchical hard quota = the group-budget pattern:** cheap LOCAL per-worker token bucket (bursts) + ONE authoritative GLOBAL/group counter = the real ceiling (Envoy local+global; K8s ResourceQuota+LimitRange, admission-time reject) | Envoy / K8s docs | forte | produção |
| E9 | Bulkhead: give the frontier-fallback its own fixed pool/quota per group so one hot worker's storm can't drain the group's frontier allowance | Nygard *Release It!* / Hystrix | forte | produção |
| E10 | **The theory is VOC / rational metareasoning:** gate each escalation with `VOC = E[quality gain] − (cost_frontier − cost_cheap)`; refuse when `VOC ≤ 0`. Known regress: computing VOC can cost as much as the computation → need a cheap proxy | Russell & Wefald 1991; VOI-agent arXiv:2605.05701 | forte (canonical) | conceitual (for LLM) |
| E11 | Cascade decision-theory: a k-model cascade reduces to a 2-model envelope via ONE shared "shadow price" (marginal quality-per-cost) → a SINGLE global cost-per-quality threshold, not ad-hoc per-callsite; and a PROACTIVE router can beat REACTIVE-escalate-on-failure | Bouchard arXiv:2605.06350; FrugalGPT 2305.05176; RouteLLM 2406.18665 | moderada/forte | conceitual/validado |
| E12 | **The gap NO paper closes:** a harness-wide CUMULATIVE budget across MANY independent heterogeneous escalation events. Every paper bounds ONE decision / ONE cascade / ONE loop. Composing many into one enforceable GLOBAL budget is UNVALIDATED territory | judgment (2 workers, absence of evidence) | forte (as a gap) | — |
| E13 | **OUR manuscript already carries the lens** — Δm ("a worker is useful only when its marginal quality justifies the added tokens/cost", :1729-1735); H33 "validation-guided fallback ... judged on cost-to-success under equal budgets" (:2034); the failure taxonomy warns a model-swap risks "indiscriminate cost escalation" (:942). **Caveat:** the manuscript's "frontier" = EFFECT frontier (:1895), NOT "frontier model" — our model-tier mapping is `[judgment]` | `[repo]` adaptive-...-architectures.md | forte (quoted) | conceitual |
| E14 | **The seams a v4 attaches to already exist:** the executor **circuit breaker** (`async_state.py:219-270`, trips on failure-rate only — cost-BLIND); `cost_metrics.py` ledger (a `costUsd` seat + `costBasis: observed\|estimated`, but NULL today — real per-hop $ not wired through failover); `WORKFLOW_TOKEN_ECONOMICS` `tokenBudget` (PLAN-granularity, not instance) | `[repo]` current code | forte | seat exists, substrate incomplete |
| E15 | Counter-evidence to respect: **budget-too-tight STARVES legit work** (no sizing formula in SRE); **denominator collapse** — a ratio budget's "accepts" denominator shrinks toward zero in a systemic incident (all workers fail over) → can over-clamp OR starve a legit escalation; **the governor itself can cause an outage** (Stripe ships every limiter behind a kill-switch); routers PLATEAU below oracle + break on the novel/hard inputs where escalation matters | SRE / Stripe / arXiv:2606.07587 | forte | — |

**The convergent picture.** This is genuinely UNSOLVED at our granularity (E1/E2/E12) — a real
frontier bet. The diagnosis is crisp: our failover is the **circuit-breaker-fallback gap** (E6) — the
breaker trips on failure but routes into the expensive model unguarded — and it's a **CUSTOM
escalate-on-rate-limit policy no framework even does** (E4). The enforcement must be **synchronous
pre-admission** (E7), not a cost-alert; the shape is a **cumulative per-GROUP quota** (E8) checked **at
the failover hop**, denominated in real cost that we must **measure first** (E14 — the ledger seat is
null today). The theory that justifies it is **VOC = Δm** (E10/E13): a failover onto a bigger model must
EARN its marginal cost — our own manuscript already says this. The wedge that makes it OURS: measure-
honesty (real cost or `—`) + Δm + a killable config knob (we already have `spawnEconomy.guard`).

## Phase 2 — Define (problem framing + briefs) · HUMAN GATE

**Jobs-to-be-done:**
- **J1 (don't leak):** "When a worker rate-limits and fails over onto a bigger model, don't let a
  group of them cumulatively run up a frontier bill nobody approved." (the D033 hole.)
- **J2 (measure it first):** "Show me the REAL frontier cost that failover/retry actually leaks today,
  before we build a control." (E14 ledger is null; D008 measure-before-control.)
- **J3 (justify escalation):** "A failover onto a bigger model should only happen when it earns its
  marginal cost — not reflexively on every 429." (E10/E13 VOC=Δm.)
- **J4 (don't starve):** "The cap must not block legit deliberate escalation or a transient one-retry
  blip, and must be instantly killable if mistuned." (E15.)

**Briefs (success criteria + actors + constraints; set-based — keep the set alive):**

- **Brief A — Failover-cost measure-only probe (serves J2; DO FIRST).** *Success:* wire real per-hop
  cost into the `cost_metrics` `costUsd` seat through the failover path, and emit — over real/replayed
  runs — how often failover lands on a frontier card + the cumulative frontier $ it leaks, graded vs a
  noise floor (baseline frontier spend with no failover). Read-only, nothing gated. *Actors:* the
  failover path, the overseer, an experiment. *Constraints:* real cost or `—` (E14); measure-before-
  control (D008); no fabricated $.
- **Brief B — Cumulative per-GROUP frontier budget, synchronous pre-admission (serves J1).** *Success:*
  an instance-scoped accumulator per workflow-run-and-its-failover-descendants; the failover hop checks
  it BEFORE re-spawning (pre-admission, E7) and refuses/downgrades when the group's cumulative frontier
  spend would exceed budget — closing the circuit-breaker-fallback gap (E6). *Actors:* the failover
  path, the circuit breaker, the ledger. *Constraints:* synchronous pre-admission not alert (E7);
  reuse the breaker seam + the ledger (E14); killable knob (E15); vendor-independent (like SPEC-153).
- **Brief C — Per-hop VOC/Δm escalation gate (serves J3).** *Success:* at the failover hop, gate the
  escalation on a CHEAP proxy for `VOC = E[quality gain] − Δcost` (the manuscript's Δm) — escalate only
  when justified; reflexive-escalate-on-429 is refused/logged. *Actors:* the failover path. *Constraints:*
  a cheap VOC proxy (E10 regress); one global shadow-price threshold not per-callsite (E11); the
  manuscript's Δm is for WIDTH, applying to a sequential hop is `[judgment]` (E13) — validate.
- **Brief D — Retry/failover BUDGET ceiling, SRE-style (serves J1+J4).** *Success:* cap failover
  re-spawns to a fraction of successful non-failover spawns per group per window (SRE retry budget, E5),
  with backoff+jitter; sized to not starve (E15 denominator-collapse). *Actors:* the failover path.
  *Constraints:* respect denominator collapse (E15); a count/ratio ceiling is cost-BLIND alone (needs B).

*Staging:* A do-first (measure). B is the core control (closes E6). C + D are complementary shapes
(justify + ceiling) evaluated set-based against B. *Human gate:* owner authorized the round → plans;
briefs surfaced. Develop on **NVIDIA** (divergence), Refine on **Sonnet 5** (critique), cross-vendor per wave.

## Phases 3-5 — Develop / Refine / Deliver (channelled 2026-07-19)

**Divergence (balanced cross-vendor).** NVIDIA (`nvidia-compat` workflow WF-20260719-181302-545811,
5 lenses, all `done`) + Sonnet 5 (3 lenses via `model:sonnet` subagents) = ~35 concept cards. Both
vendors converged INDEPENDENTLY on the core (per-group cumulative accumulator at the failover hop;
measure=control at threshold=∞; reuse the circuit breaker; graceful downgrade; defer VOC). The Sonnet
reliability lens found + the overseer VERIFIED a real bug (`async_runtime.py:585` returns before the
:588 finalize → intermediate failover hops' `observedUsage` is dropped; only the last hop's cost
persists). **No Fable spent** — the NVIDIA run passed the SPEC-153 spawn-economy guard as a cheap tier
(dogfooding: the guard we just shipped protected this very round).

**Deliver.** Portfolio + detailed staged plans (P0 fix the cost-loss bug · P1 measure probe · P2 the
fused control + ops rider · F1-F4 frontier bets) in
**`docs/research/spawn-cost-governance-implementation-plans.md`** — the round's deliverable. Experiment
EXP-27 (two-phase: measure leak → measure control) registered. Decision D034 in DECISIONS.md. The plans
close the SPEC-153 D033 residual; they route through SPEC-116 intake (SPEC-153 v4) when picked up to build.

## Traceability matrix

Filled in the plans doc §"Traceability matrix": `Evidência → Problema → Ideia → Experimento → Plano → Status`.
