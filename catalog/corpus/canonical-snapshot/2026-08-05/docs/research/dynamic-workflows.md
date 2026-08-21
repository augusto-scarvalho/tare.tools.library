# Research round — dynamic workflows in generative-AI agents

Round opened 2026-07-12 by the `research` skill (SPEC-119). Orchestrator: overseer session
(running in parallel with the 4 CE-batch worktree implementers). Primary evidence: the owner's
study (2026-07-12) applied to a multi-agent/multi-vendor harness — thesis: the field is moving
from hand-written **static** workflows to **Agentic Computation Graphs** that can be selected /
synthesized / pruned / routed / replanned; the template vs realized-graph vs trace distinction
is the evaluative axis; "more agents = better" is **false** (single-agent matches or beats
multi-agent under equal budget except when subtasks are genuinely independent / parallel / the
context-isolation win outweighs coordination) → **topology must be routable** (single ↔ multi ↔
specialized-workflow). Central recommendation: a **hybrid, restricted orchestrator** — a
deterministic, durable, auditable core runs a typed graph; the LLM only fills/chooses/revises
explicitly-dynamic "slots" inside policies/budgets/gates (Blueprint-First-Model-Second).

## Phase 0 — Question, criteria, budget

**Question.** Which dynamic-workflow capabilities should THIS harness adopt, given it already
owns a strong deterministic control plane (DAG fork-join/map-reduce, async supervisor, circuit
breaker, locks/leases, SPEC-115 mid-workflow failover, model routing, token-audit/budgets), and
given the study's OWN deterministic-first thesis (the runtime owns graph/schedule/budget/policy;
the LLM only the semantically-hard slot)?

**Success criteria.**
- Backlog of buildable items, each mapped to a NAMED gap + a concrete integration seam
  (file/module) + ONE metric (graph-shape / cost / risk / result).
- Deterministic-first: prefer a typed IR, a deterministic router with an LLM-only estimate,
  decompose-on-demand (only when the executor fails), dependency-DAG dispatch, shadow-mode
  promotion — over free-running runtime improvisation or learned self-modification.
- Every item respects our invariants: eviction ≠ deletion, no resident daemon, stdlib-only
  core, GUI writes no state, verify-on-demand, summaries are a view not the source of truth,
  a new/adapted workflow is a **software change** (test/review/rollback — ties SPEC-116).
- Critique must reject over-engineering: single-agent is ALWAYS the baseline (the study's own
  finding); topology/decomposition adaptation must pay for its coordination cost; replanning ≠
  guaranteed self-correction; LLM-as-judge ≠ ground truth; observation must pay for itself.

**Declared budget.** claude executor; 1 divergence wave (5 ideators) + 1 critique wave (4
critics); research-profile budgets; no wave 3.

## Phase 1 — Evidence matrix (verified 2026-07-12)

| claim | source | prov | conf | maturity |
|---|---|---|---|---|
| Template vs realized-graph vs trace is the right decomposition of "dynamic"; Agentic Computation Graph (ACG) formalization | [web] Yue et al. 2026, arXiv:2603.22386 | web | moderada | preprint |
| Single-agent matches/beats multi-agent under equal reasoning budget on multi-hop; MAS wins only with independent subtasks / real specialization / useful parallelism / context-isolation payoff | [web] Tran & Kiela 2026 (arXiv:2604.02460); Su & Wu 2026 (arXiv:2602.08272) | web | moderada | preprint |
| A hybrid router single-agent↔multi-agent improved accuracy AND cut cost in the authors' scenarios → topology should be routable | [web] Gao et al. 2025, arXiv:2505.18286 | web | moderada | preprint |
| Decompose only when the executor can't complete a subtask (recursive, on-demand) beats max decomposition | [web] ADaPT, Prasad et al. 2024, Findings NAACL | web | forte | protótipo reproduzível |
| Compile a plan into a dependency DAG, dispatch independent ops in parallel; separate planner/dispatch/executor; ~3.7× latency, ~6.7× cost, ~9% acc vs ReAct (authors' tests) | [web] LLMCompiler, Kim et al. 2024, ICML | web | forte | protótipo sólido |
| Decouple deterministic procedure (blueprint) from LLM generation in bounded subtasks; +10.1pp over authors' baseline on τ-bench (benchmark-specific) | [web] Blueprint-First-Model-Second, Qiu et al. 2025, arXiv:2508.02721 | web | moderada | preprint |
| Agents as computation graphs whose edges are info flow; prompts/connectivity optimizable | [web] GPTSwarm, Zhuge et al. 2024, ICLR | web | forte | validado |
| Workflow patterns + Petri-net soundness/deadlock/reachability transfer; agents only make transition conditions probabilistic | [web] van der Aalst et al. 2003 | web | forte | consolidado |
| Distributed-systems primitives (event sourcing, leases, bulkheads, circuit breakers, idempotency, sagas/compensation, structured cancellation, per-tenant isolation) are the durable core | [web] study §3.5 | web | forte | consolidado |
| Autonomous persistent workflow changes must be treated as software: test, review, rollback, shadow/promote — not free self-improvement | [web] study §2/§5; risk list | web | forte | judgment (norma) |

**Baseline — what the harness ALREADY has (do NOT rebuild):** workflow DAG (fork-join / map-
reduce) + `workflow plan` packet (a plan JSON) + async supervisor (schedule/execute) + circuit
breaker (containment gap **just fixed**, CE.1) + locks/leases + SPEC-115 mid-workflow failover
(swap executor on rate-limit/block); **model routing** (cards/effort/profiles) = per-node model
selection; token-audit + budgets per profile; **cost_metrics + the CE.2 economy meter** (token/
amplification trace, landing now); `validate-results` + `reduce` + `review-reduce` (verify);
`self-review` + `spec_test_gate` (policy); `workflow resume`/`unlock`/`async-recover` (durable/
resumable); typed WORKER_RESULT/REDUCE_RESULT node contracts; the **two-door SDD+BDD flow**
(SPEC-116: intake→template/Gherkin) = the "workflow-change-is-software" gate already exists for
UI features; `trace`/`trace-export`/`trace-push`.

**Named gaps (candidate backlog anchors):**
- **DW1 — no topology router (single ↔ multi ↔ specialized).** Fan-out (worker count) is fixed
  at plan time; there is no single-agent-baseline → "decompose only if subtasks are genuinely
  independent" decision. The study's #2 priority and its strongest evidence ("more agents ≠
  better"). Deterministic classifier + budget gate; LLM only for the decomposability estimate.
  Ties the comm-round G4/CE.9 (adaptive fan-out) — reuses CE.2's useful-fan-out signal.
- **DW2 — no on-demand re-decomposition (ADaPT).** A failing/partial worker triggers executor
  *failover* (SPEC-115) but never *task re-decomposition* (split the hard subtask into sub-
  subtasks). Deterministic trigger (worker status failed/partial), bounded depth, idempotent.
- **DW3 — no canonical workflow IR / blueprint with authorized dynamic slots.** The plan packet
  fixes topology; there is no ONE typed graph IR that plan/schedule/execute/verify/policy all
  read, and no "dynamic slot" the LLM may fill *within* a deterministic blueprint (Blueprint-
  First). This is the structural foundation the other items stand on.
- **DW4 — scheduler is fixed map-reduce, not dependency-DAG dispatch.** Fan-out is uniform
  branches; there is no critical-path parallelism / dispatch-by-readiness across heterogeneous
  nodes (LLMCompiler's separation of planner/dispatch/executor). Deterministic scheduler gain.
- **DW5 — no graph/risk trace metrics; no shadow-mode promotion.** CE.2 covers token/cost but
  not graph-shape (topology, decomposition depth, critical path) or per-node risk; and a new/
  adapted workflow template goes straight to prod with no replay/shadow/promote gate. Ties the
  two-door SDD flow (SPEC-116): an adaptation is a software change.
- **DW6 (likely PARK) — inter-run evolution / learned router.** Learning a router or promoting
  templates from traces — overfitting/regression risk; the study warns against self-improvement
  without external evaluation. Needs DW5's metrics + shadow mode as a precondition.

## Phase 2 — Briefs and gate

**Brief 1 — route the topology, decompose on demand (DW1+DW2; highest-leverage, evidence-backed).**
How might the harness pick single-agent vs multi-agent vs a specialized workflow per request,
deterministically (a cheap classifier + budget gate; the LLM only estimates decomposability),
with single-agent as the hard baseline — and re-decompose a subtask ONLY when its worker fails/
returns partial (ADaPT trigger), bounded-depth and idempotent, reusing SPEC-115's settle seam
and CE.2's fan-out signal — WITHOUT letting fan-out inflate cost or loop?

**Brief 2 — a typed workflow IR + dependency-DAG dispatch + shadow-mode promotion (DW3+DW4+DW5).**
How might we give the harness ONE canonical typed workflow IR (that plan/schedule/execute/verify/
policy all read) with explicit LLM-fillable "slots" inside a deterministic blueprint, a scheduler
that dispatches by dependency-readiness/critical-path instead of uniform map-reduce, and graph/
risk trace metrics + a shadow-mode replay-and-promote gate so a NEW or ADAPTED workflow is
treated as a software change (test/review/rollback, ties SPEC-116) — all stdlib-only, durable,
summaries-are-a-view, no resident daemon?

**Parked (future round / needs a signal):** DW6 inter-run learned router (needs DW5 metrics +
shadow mode + an external evaluator, else overfitting/regression); full runtime graph-rewrite
(irreproducibility risk — confine to authorized slots first).

**Gate.** Scope/waves/budget pre-approved by the owner (this invocation). Deterministic-first +
single-agent-baseline + net-cost-positive + adaptation-is-software are hard constraints on the
critique wave.

## Phase 3 — Wave 1 (divergence)

`WF-20260712-183958-135463`, `research-divergence`, 5 ideators (simplicity, performance,
reliability, trust-boundary, analogy), claude executor. All 5 fulfilled (no length-rejections).
Heavy convergence on the 6 gaps; every concept is deterministic-first, no daemon/new-state-family.
Standout convergences: **workflow.json IS already the IR** (schemaVersion 1.1, read by plan/
schedule/execute/policy — all 5 landed here for DW3); a **plan-time verdict that defaults to
single-agent** (DW1); **depth-1 scope-split at the settle seam** adjacent to CE.1 (DW2); **graph-
shape fields that EXTEND cost_metrics/CE.2** + **shadow = deterministic plan-level replay-diff on
archived WF dirs** (DW5). Cross-domain transfers: DB cost-based optimizer EXPLAIN→DW1; delta-
debugging ddmin→DW2; compiler IR/SSA→DW3; Tomasulo dataflow→DW4; SRE dark-launch→DW5. The
trust-boundary lens surfaced **2 verified source holes**: generated worker prompts + context-
digest.md are never secret-scanned yet fan out N× across possibly-different-vendor executors;
executor/model cards carry no trust tier.

Orchestrator consolidated the 25 concepts into **6 candidates**:
- **D1 topology router** (DW1) — a deterministic verdict in the plan compile loop that DEFAULTS
  to single-agent (N=1), forking only when a token-audit budget gate + independence check +
  operational health (circuit state, CE.2 cost-per-finding) justify it. Seam: `harness.py` plan
  compile + token-audit. Analogy: cost-based query optimizer.
- **D2 depth-1 re-decomposition at settle** (DW2) — recovery action on worker failed/partial:
  deterministic scope-split (split shard paths, reuse round/maxRounds), depth-1, breaker-
  integrated (ties CE.1), LLM split only as escalation. Seam: `async_runtime.py` worker-settle.
- **D3 formalize workflow.json as the typed IR + slots** (DW3) — stdlib schema validated at
  plan, explicit LLM-fillable "slots", unify the 3 budget locations into one typed section.
  Zero migration. Seam: workflow.json schema + plan/validate. Analogy: compiler IR/SSA.
- **D4 graph-shape metrics + shadow-mode plan-replay promotion** (DW5) — 4 deterministic graph
  fields (fan-out/depth/makespan/critical-path) into `cost_metrics.record_workflow` (extends
  CE.2, zero new state); shadow = plan-level replay-diff (topology + token-audit) of old-vs-new
  profile on ARCHIVED WF dirs (zero execution/prod exposure) as the promote gate, ties SPEC-116.
- **D5 the fork boundary is a trust boundary** (trust-lens, cross-cutting) — secret_scan the
  generated worker prompts + context-digest before they fan out; add an executor/model-card
  trust tier; wire sealed-fold + trace-push allowlist into D1-D4 as cheap deterministic gates.
  Seam: `secret_scan` seams + executor cards.
- **D6 (mostly PARK)** — reserve a `dependsOn` field + ship LPT (longest-prompt-first) queue
  ordering for makespan now (cheap, offline-replayable); PARK the full critical-path scheduler
  (no dependent workloads yet, DW4) and the inter-run learned router (DW6; needs D4 + external
  evaluator).

## Phase 4 — Wave 2 (critique) — done

`WF-20260712-190529-589401`, `research-critique`, 4 critics (validity/architecture/cost/
security), `--seed` = the divergence reduce. All 4 fulfilled. Verified anchors: the "3 budget
places" premise of D3 CONFIRMED (`harness.py:1448`, `workflow_token_audit.py:217`,
`workflow_writes.py:208` — three separate schemaVersion-1.1 docs); D5's two holes CONFIRMED in
source (`plan_workflow` at `harness.py:1636-1666` writes worker prompts + context-digest with
NO secret_scan; the K1 scan at `harness.py:1589-1593` runs only on `--validate-only` over argv;
`context_digest.py` has zero scan calls; fold scan at `workflow_lifecycle.py:224` only scans
`*.result.json` POST-dispatch, after prompts already fanned out N×; `executors.json` has no
trust/tier field); D2's settle seam real at `async_runtime.py:337`; D4's data already in
`record_workflow` (cost_metrics.py:108). Load-bearing caveat (validity): ALL external evidence
is preprint + benchmark-specific, none measured on THIS harness → **D4 is the epistemic keystone**
(the mechanism that converts priors into local evidence).

**Cross-lens verdicts:**

| cand | validity | architecture | cost | security | net |
|---|---|---|---|---|---|
| D1 topology router | keep-w/-ch (thresholds unsourced → --explain first) | keep-w/-ch (record router inputs+verdict in workflow.json or plans aren't replayable) | keep-w/-ch (observe-only first; sparse data early) | keep-w/-ch (trust-term) | **KEEP-CHANGES** — ship as observe-only `--explain` verdict, record inputs+verdict, NO auto-fork yet |
| D2 depth-1 re-decomp | keep-w/-ch (needs failure-class precondition) | keep-w/-ch (reuse plan-time packet builder; mid-flight children can double-/never-settle) | keep-w/-ch (children MUST inherit remaining wave budget) | keep-w/-ch (subset-scope invariant) | **KEEP-CHANGES, LATER** — hard preconditions: failure-class gate, budget inheritance, subset scope, one generator, no double-settle |
| D3 workflow.json IR | keep (verify 3-budget claim) | **keep, build EARLY** (D1/D2/D4 all write into it) | keep (near-zero cost; closes silent budget bypass) | keep | **KEEP, FOUNDATION** — 3-budget premise CONFIRMED; fold D6's dependsOn reservation in |
| D4 graph metrics + shadow | **keep (epistemic keystone)** | **SPLIT** (metrics now; replay-gate defer until D3) | keep-w/-ch (replay must be provably LLM-free) | keep-w/-ch (sealed-only replay corpus) | **KEEP, SPLIT** — metrics now (extends CE.2, ~0 cost); shadow-replay deferred, LLM-free + sealed-only |
| D5 fork=trust boundary | **keep (only CONFIRMED load-bearing claim)** | keep (fix at prompt/digest generation seam, before fan-out) | keep (scan once; gate cost << incident cost, GEMINI-leak precedent) | **keep, build FIRST** | **KEEP, BUILD FIRST** — scan prompts+digest at `harness.py:1636-1666` pre-fan-out; add card trust tier |
| D6 dependsOn/LPT/learned | PARK-mostly, swap order | park LPT; fold dependsOn into D3 | dependsOn-reserve only (concurrency=1 → LPT nil today) | keep-w/-ch (PARK learned router: feedback-poisoning) | **FOLD+PARK** — dependsOn reservation → D3; PARK LPT + learned router |

**Unanimous-ish build order:** **D5 → D3 → D4-metrics → D1-explain → D2** (D6's dependsOn folded
into D3; LPT + learned router parked). D5 and D3 are the two "build-first" anchors (a confirmed
cheap security fix + the IR foundation everything writes into); D4-metrics is the zero-cost
keystone that makes the rest measurable; D1 ships observe-only; D2 last, gated by preconditions.

## Phase 5 — Portfolio & backlog

Deterministic-first held under critique: every survivor is a plan-time/settle-time/finalize-time
extension of an existing seam — no daemon, no new state family, no LLM in a control loop (D1's
LLM estimate is observe-only; D2's LLM split is escalation-only behind a deterministic failure
gate). The critique's sharpest correction: **measurement before control** — D4's graph metrics
and D1's `--explain` verdict must exist and be trusted BEFORE any auto-fork/auto-split flips on,
because all the pro-adaptation evidence is preprint-grade and none is measured on this harness
yet. Portfolio → the **Dynamic workflows roadmap** section in `docs/IMPLEMENTATION_BACKLOG.md`
(DW.1–DW.8), each row = named gap + a verified seam + the metric it moves + ship/defer/PARK.

**Ship spine:** DW.1 secret-scan the fan-out surface + card trust tier (D5, build first) ·
DW.2 formalize workflow.json as the typed IR + slots + dependsOn reservation (D3, foundation) ·
DW.3 graph-shape metrics into cost_metrics (D4-metrics, extends CE.2) · DW.4 topology-router
`--explain` observe-only (D1) · DW.5 depth-1 re-decomposition at settle, precondition-gated (D2).
**Deferred/parked with an explicit signal:** DW.6 shadow-mode plan-replay promotion (needs DW.2;
LLM-free + sealed-only) · DW.7 LPT queue ordering (needs concurrency>1 to matter) · DW.8 inter-
run learned router (needs DW.3 + external evaluator; feedback-poisoning risk).
