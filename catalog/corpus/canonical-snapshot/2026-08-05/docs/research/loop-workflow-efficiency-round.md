# Research round — loop / single-demand WORKFLOW efficiency via parallelism

**Slug:** loop-workflow-efficiency-round · **Opened:** 2026-07-20 · **Orchestrator:** overseer session.
**Trigger (owner 2026-07-20):** "nossas etapas hoje ... são muito sequenciais ... uma task que antes
levava 10-20min agora leva de 20min a >1h. ... mapeamento de processo completo ... quais são
interdependentes, quais podem rodar em paralelo, quais são sequenciais ... máquina(s) de estado ...
planos para tudo que for prospectado." LEAF-TASKS DEFERIDAS; esta é a prioridade.

## Question
How do we cut the END-TO-END cycle time of a single demand (and a loop iteration) — from
gatekeeper/intake to backlog-row closure — by increasing concurrency/parallelism and removing
sequential waste, WITHOUT weakening the correctness guarantees (gate, reckon, closure lockstep)
we just built?

## Success criteria (what a good answer must satisfy)
- A COMPLETE process map, gatekeeper→close, each step tagged: `sequential` (hard dependency),
  `parallelizable` (can overlap), or `interdependent` (shared state / sync barrier).
- A ranked BOTTLENECK diagnosis grounded in observation (why 10-20min → 20min-1h+), not vibes.
- A portfolio of SOLUTIONS spanning the tech frontier (agent orchestration) AND market agile/lean
  frameworks (ToC, CPM, WIP, Kanban, queueing), each with maturity + confidence + a real-world analogy.
- One or more STATE-MACHINE models of the loop + single-demand, marking parallel-fireable transitions.
- Every prospected improvement → a groomed backlog row (deps mapped), ranked by cycle-time impact.
- Anti-fabrication: claim → source + date + confidence; unverifiable = judgment.

## Declared budget / width / design (Phase 0 gate)
- **Budget:** Discover ≤ light (repo reads + 1 external WebSearch pass). Develop = 1 divergence wave
  (5 ideators) + 1 critique wave (4 critics). Stop-reduce at 60% budget.
- **Width:** EXPLORATORY (scanning a field, no single implementation target yet) → 5 ideators justified
  (D010: exploratory scales width; nominal-group diversity pays — Diehl & Stroebe 1987). Critique 4.
- **Design:** the round FEEDS experiments (cycle-time is a measurable claim). Cite EXPERIMENT_METHODS
  cards at Deliver: cycle-time reduction → before/after with a matched task-class baseline; any gate-scope
  change → the noise-floor + matched-budget cards. A measurable claim with no design is Phase-0 incomplete.

## Prior art (seed — do NOT re-derive)
- `[repo] docs/research/reckon-efficiency-round.md` — prior round on reckon cost/efficiency.
- `[repo] docs/research/spawn-cost-governance-round.md` (+ implementation-plans) — subagent spawn cost.
- `[repo] docs/AGENTIC_WORKFLOWS.md`, `WORKFLOW_OPERATIONS_RUNBOOK.md`, `WORKFLOW_TOKEN_ECONOMICS.md`.
- `[repo] .harness/prompts/overseer-loop-playbook.md` — the ritual this round optimizes.
- `[repo] CLAUDE.md` SPEC-137 note — "validate --staged takes 7-15 minutes" (the gate duration, primary source).

---

## Phase 1 — Discover (repo + firsthand; external pass pending)

### 1a. The process map (firsthand [judgment] from running the workflow all session + [repo])
End-to-end states of a single demand. Duration = observed this session; class = sync nature.

| # | Step | Owner | Observed duration | Class | Notes / sync barrier |
|---|---|---|---|---|---|
| 1 | Intake/triage (porteiro) | UserPromptSubmit intake-triage hook + SPEC-144 router | ~seconds | sequential (entry) | classifies profile/route; cheap |
| 2 | Plan-brief (HARD footprint) | overseer | 2-8 min | sequential | must precede implement |
| 3 | Implement | implementer subagent (Opus xhigh) | 10-20 min | sequential-ish | COLD SPAWN re-derives ctx (~12k tok required-reads/worker); blocks review |
| 4 | Own-review (re-run verification) | overseer | 2-5 min | interdependent | reads impl output |
| 5 | Reckon | reviewer subagent (Sonnet) | 10-15 min | **parallelizable** | now runs ‖ gate (SPEC-157); was serial |
| 6 | Gate `validate --staged` | overseer (bg) | **7-15 min** | **the DRUM (constraint)** | scenarios+spec-pack; on critical path |
| 7 | Commit (+ pre-commit hook) | overseer | ~seconds | sequential (join) | check_staged ∧ check_reckon must pass |
| 8 | Close backlog row | overseer | ~seconds | sequential | SPEC-154 lockstep |

### 1b. Bottleneck diagnosis (ranked; [judgment] from direct observation this session)
1. **RE-GATE CHURN is the dominant amplifier.** Each small follow-up fix (si-3d; the git.exe
   hardening) forced a full re-stage + full re-gate (7-15 min EACH). This session, fix A alone gated
   ~3×. A 15-min task becomes 45min+ purely from repeated full gates on tiny deltas. Analogy: a CPU
   pipeline FLUSH on every one-line change. Confidence: forte (observed repeatedly).
2. **The gate is the CONSTRAINT (ToC drum), 7-15 min, on the critical path.** Even one clean pass
   dominates. It re-runs the FULL scenario+spec-pack surface regardless of what changed. Confidence: forte
   ([repo] CLAUDE.md states the duration; observed every commit).
3. **Serial spawn chain + cold context.** implement → (wait) → review → reckon‖gate. The implementer
   spawn is serial before review can start; each subagent cold-spawns and re-derives ~12k tokens of
   required-reads (WORKFLOW_TOKEN_ECONOMICS). No pipelining of item N+1 while item N gates. Confidence: moderada.
4. **Wait-without-overlap.** During a 7-15 min gate the overseer idles (SPEC-137 forbids writes/commits);
   the NEXT item's plan/implement could overlap but doesn't. Confidence: moderada.

### 1c. State-machine sketch ([judgment], to refine in Develop)
`INTAKE → PLANNED → IMPLEMENTING → {REVIEWING ∥ RECKONING ∥ GATING} → JOIN(verify-ledger ready) →
COMMITTED → CLOSED`. Parallel-fireable transitions: REVIEW ∥ RECKON ∥ GATE (fan-out after IMPLEMENTING);
the JOIN barrier = the verify-ledger (gate=pass ∧ reckon=no-blocker for the staged fingerprint, SPEC-157).
Cross-item: item N in GATING could overlap item N+1 in PLANNED/IMPLEMENTING (pipelining) — today it doesn't.

### 1d. External frontier (Flow A) — PENDING (WebSearch pass in Develop or a discover worker)
Targets: incremental/affected-only test selection (Bazel/test-impact analysis), result caching keyed on
content hash (we ALREADY have the staged fingerprint — strong lead), speculative/pipelined agent
orchestration, DAG schedulers, Theory of Constraints (Goldratt), Critical Path Method, WIP limits /
Kanban flow, queueing theory (Little's Law). Verify each against a primary source before it drives a decision.

---

## Phase 2 — Define (briefs for the divergence wave) — HUMAN GATE

Problem-framed (not tech-shaped). Each is a brief for the Develop ideators.

- **Brief A — Kill the re-gate churn (the #1 amplifier).** HMW avoid a full 7-15 min gate on a tiny
  delta? Jobs: validate the about-to-commit tree correctly, but pay only for what changed. Leads:
  affected-scenario selection (map changed paths → the scenarios that cover them); gate-result cache
  keyed on the staged fingerprint (we already compute it — a matching fingerprint skips the re-run);
  batch fixes before gating. Constraint: must not weaken correctness (fingerprint binding already exists).
- **Brief B — Compress / parallelize the constraint (the gate itself).** HMW make one gate pass shorter
  or overlap it? Leads: parallelize scenarios across cores; split spec-pack vs scenarios to run
  concurrently; run the gate speculatively on the staged tree while review/reckon proceed. Constraint:
  deterministic result + the gate-hold isolation must hold.
- **Brief C — Pipeline the loop across items (throughput, not just latency).** HMW start item N+1 while
  item N gates? Leads: a scheduler that overlaps PLANNED/IMPLEMENTING(N+1) with GATING(N); WIP limit = 1
  in the COMMIT stage but >1 upstream; the verify-ledger as the per-item join token. Constraint: disjoint
  footprints (the existing "one integration at a time" rule) + the gate-hold guard.
- **Brief D — Warm the spawns / cut cold-context re-derivation.** HMW stop each subagent re-reading ~12k
  tokens? Leads: shared context digest (E1 sharedContextDigest already exists), warm pools, seeding.
  Constraint: independence for divergence (Diversity Collapse) — warm-sharing is fine for implement/review,
  forbidden for divergence generation.

**GATE:** stop for owner approval of these briefs before spending the Develop wave (the expensive part).

## Phase 3 — Develop (divergence wave, adopted)
`WF-20260720-123636-825682` — 5 NVIDIA ideators (nvidia-compat), 4 valid (worker-004 invalid on a
validation nit; minSuccess 3 met). 25 findings → agent-reduced to **9 concepts with genealogy**
(`reduce/agent-reducer.candidate.json`). Strong convergence: 4/4 ideators independently proposed the
fingerprint-keyed gate cache + affected-scenario selection as the top attack on re-gate churn.
External Flow-A evidence (`docs/research/loop-workflow-efficiency-evidence.md`, Sonnet, ~34 primary-source
rows) ran IN PARALLEL and GROUNDS each concept — top external leads map 1:1 to the concepts (Bazel/Nx/
Turborepo cache→C1; Google TAP/Ekstazi/pytest-testmon→C2; pytest-xdist→C3; Little's Law/ToC→C4/C5;
LLMCompiler dependency-aware dispatch→C5; Speculative Actions arXiv 2510.04371 "watch-not-now"→C6).

## Phase 5 — Deliver (portfolio + plans)

Convergence by orchestrator judgment (set-based; novelty ≠ maturity kept separate). Ranked by impact on
the diagnosed bottlenecks (#1 re-gate churn, #2 gate-is-constraint, #3 cold serial spawns).

**núcleo (build first — high impact × high maturity, external-validated):**
- **C8 gate-observability** — measure the drum FIRST (ToC: can't exploit a constraint you can't see).
  Per-scenario timing + cache/speculation counters. Cheap; unblocks measuring everything else. → `wf-gate-observability`
- **C1 fingerprint-keyed gate-result cache** — smallest delta (SPEC-157 already computes the fingerprint);
  kills re-gate churn on unchanged surface. Bazel/Nx/Turborepo-proven. → `wf-gate-result-cache`
- **C2 affected-scenario selection (TIA via Graphify)** — run only scenarios intersecting changed-paths;
  conservative full-gate fallback. Google TAP/Ekstazi-proven. → `wf-affected-scenario-selection`

**contingência (correctness-neutral, turn on when cores idle / ritual):**
- **C3 parallel scenarios** (pytest-xdist pattern) — compress one gate pass, once independence is proven. → `wf-parallel-scenarios`
- **C4 batch-fix accumulator** (Drum-Buffer-Rope) — mostly a playbook change + a small buffer + bisect-on-fail. → `wf-batch-fix-accumulator`
- **C7 warm-spawn / digest seed** — minimal form (seed the existing sharedContextDigest), measure, escalate only if large. → `wf-warm-spawn-digest`

**aposta-de-fronteira (higher novelty, throughput lever):**
- **C5 WIP-limited cross-item pipelining** (Little's Law + verify-ledger as join token; LLMCompiler is the
  frontier reference) — overlap N+1 upstream with N's gate; WIP=2; respect disjoint footprints + gate-hold guard. → `wf-wip-pipelining`

**experimentos (measure before controlling):**
- **C6 speculative gate** — value = P(review approves unchanged); register EXP, opt-in flag, ship control only
  if hit-rate clears a threshold. Frontier match (Speculative Actions) too immature to pick today. → EXP + `wf-speculative-gate`

**estacionadas (needs an audit first):**
- **C9 spec-pack ‖ scenario overlap** — audit coverage overlap before acting (the overlap is a hypothesis). → `wf-specpack-overlap-audit`

**Sequencing insight (the meta-plan):** C8 (observability) → then C1+C2 (kill churn) are THE cycle-time win
for our #1 bottleneck; C3 compresses the constraint; C5 adds throughput; C6 is the measured bet. Build in
that order — each earns its cost against measured gate time (article Δ_m lens).

## Traceability
| Evidência | Problema | Ideia | Experimento/ADR | Spec | Task | Status |
|---|---|---|---|---|---|---|
| firsthand re-gate churn + Bazel/Nx cache [web] | #1 churn | C1 fingerprint cache | — | (SPEC intake) | wf-gate-result-cache | groomed |
| Google TAP/Ekstazi [web] | #1+#2 | C2 affected-scenario | — | (SPEC intake) | wf-affected-scenario-selection | groomed |
| pytest-xdist [web] | #2 duration | C3 parallel scenarios | — | (SPEC intake) | wf-parallel-scenarios | groomed |
| ToC drum-buffer-rope [web] | #1 churn | C4 batch-fix | — | (SPEC intake) | wf-batch-fix-accumulator | groomed |
| Little's Law + LLMCompiler [web] | throughput | C5 WIP pipelining | — | (SPEC intake) | wf-wip-pipelining | groomed |
| Speculative Actions arXiv [web] | #2 overlap | C6 speculative gate | EXP (register) | (SPEC intake) | wf-speculative-gate | experiment |
| WORKFLOW_TOKEN_ECONOMICS [repo] | #3 cold spawn | C7 warm/digest | — | (SPEC intake) | wf-warm-spawn-digest | groomed |
| DORA/CI analytics [web] | measure drum | C8 observability | — | (SPEC intake) | wf-gate-observability | groomed (build first) |
| [judgment] | #2 overlap | C9 spec/scenario overlap | — | — | wf-specpack-overlap-audit | parked |
