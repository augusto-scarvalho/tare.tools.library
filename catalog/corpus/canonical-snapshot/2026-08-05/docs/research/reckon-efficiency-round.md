# Research round — making the reckon (independent review) faster / cheaper / parallel

Orchestrator: this session (Opus overseer). **Executor: NVIDIA ONLY** (`nvidia-compat`, owner directive
"só de nvidia" — cheapest tier, free credits). Started 2026-07-19.

> **NVIDIA-only constraint (honest):** NVIDIA workers (`tools/openai_worker.py`) are one-shot HTTP
> completions — NO WebSearch, NO repo reads. So this round is an ANALYSIS/DIVERGENCE round: the
> orchestrator supplies the rich context (the problem + our reckon's real shape + seeded analogues from
> CI/review-bot practice) inline; NVIDIA generates/expands/reasons. "How other systems do it" comes from
> NVIDIA's parametric knowledge (NOT web-verified) — flagged; web-verification is a light follow-up if
> the owner wants it.

## The problem (concrete)

Our overseer loop runs a **RECKON** — an independent LLM reviewer (today **Sonnet 5 high**) that verifies
a risk-bearing change BEFORE commit: reads the diff, hunts defects / gaming / regressions / missed blast
radius, returns findings + a SHIP/FIX/BLOCK verdict. It is thorough and has repeatedly earned its keep
(caught the D033 failover residual, the ds-2/ds-4 landmines, the SPEC-137 hook regressions). BUT:
- It is **SLOW** (~10-15 min wall) and **TOKEN-HEAVY** (~100-150k tokens each). Over a multi-item loop
  that is a large, recurring spend — and for some user profiles (frequent small changes, budget-tight)
  it can dominate cost.
- The loop is **SEQUENTIAL**: implementer → own-review → **RECKON** → gate (`validate --staged`, runs
  scenarios/spec-pack) → commit. The reckon and the gate are INDEPENDENT (the reckon reads the diff
  read-only; the gate runs tests) yet run one-after-the-other.

## Questions

1. How do we make the reckon **faster / cheaper / more efficient** without losing the defect-catching it
   earns its keep on?
2. Can the reckon run **IN PARALLEL with the gate/testing step** (they seem independent — both must pass
   before commit, neither feeds the other)? What's the cheapest way to do that?
3. How do OTHER systems (CI, code-review bots, merge queues) do this?

## Our reckon's real shape (orchestrator-supplied grounding)

- Dispatched as a Sonnet `reviewer` subagent AFTER the implementer returns + after the overseer's own-
  review; the overseer WAITS for it, THEN runs `validate --staged` (the gate), THEN commits.
- Already RISK-SCOPED (the reckon-scoping decision): pure/low-risk transcription → own-review only;
  risk-bearing (routing/actions/engine/new-deps/frozen-surface) → the full Sonnet reckon. So the reckon
  is already conditional — the question is making the reckon-WHEN-IT-RUNS cheaper + parallel.
- The reckon RE-READS the same seams each time (the diff + the neighbors + the exemplars) and re-runs the
  verification (the scenario, the self-check) itself — much of it overlaps the gate's own scenario run.

## Seeded analogues (orchestrator-supplied, for the NVIDIA packet — expand/reason on these)

- **CI parallel required-checks:** lint / test / type-check / security-scan run as PARALLEL jobs; the PR
  merges only when ALL are green. Review is a check, not a pre-test gate.
- **Async review bots parallel to CI** (CodeRabbit, Codium PR-Agent, Graphite, Danger, reviewdog): the
  bot reviews the diff WHILE CI runs the tests — two independent lanes, both must pass.
- **Diff-scoped / incremental review:** review ONLY the changed hunks + their blast radius, not the whole
  feature (reviewdog, danger.js, test-impact-analysis's review analogue).
- **Test-impact-analysis:** run only the tests a change can affect — the "reckon only the real risk
  surface" analogue.
- **Tiered / two-pass review:** a CHEAP first pass (static analysis, or a small/fast model) triages;
  escalate to the EXPENSIVE reviewer only on flagged risk. (We already own-review low-risk.)
- **Cheaper reviewer model / cheaper tier:** run the reckon on a cheap fast model (NVIDIA glm) for the
  bulk, reserve Sonnet for the flagged/hard parts (a cheap-triage → expensive-on-flag cascade — note the
  cost-governance round's FrugalGPT cascade lens applies here too).
- **Prompt caching / context reuse:** the reckon re-reads the same seams; cache the shared context.
- **Sampling:** review a sample of findings/files rather than exhaustive, with confidence bounds.
- **Merge queue / speculative:** run review + tests speculatively in parallel; commit on both-green.

## Divergence lenses (the NVIDIA research-divergence profile, 5 branches)

- **simplicidade:** the cheapest change — is "run the reckon subagent and the gate in parallel, commit on
  both-green" just a scheduling change in the loop, ~free? What is the 80/20?
- **performance/escala:** the token/latency economics — tiering, cheaper-model triage, diff-scoping,
  sampling, caching; where does the token spend actually go, and what cuts it most per unit risk lost?
- **confiabilidade/ops:** don't trade away the defect-catching — a cheaper reckon that misses a defect is
  worse than a slow one; how to keep the SHIP/FIX/BLOCK quality while cheaper (tiered escalation, the
  gate-as-a-first-filter so the reckon only sees test-green diffs).
- **trust-boundary:** the reckon IS the trust gate before commit — parallelizing it with tests must NOT
  let a change commit before BOTH clear; the ordering/consistency invariant.
- **analogia cross-domain:** transfer a mechanism from CI/review-bot/merge-queue/test-impact practice.

## Phase 3-5 — the answer (NVIDIA divergence WF-20260719-184710-556194, 4/5 workers, channelled 2026-07-19)

NVIDIA-only (owner directive). 4 lenses landed (simplicity/performance/trust-boundary/analogy;
reliability worker didn't settle — minSuccess 3, covered by the others). STRONG convergence. Caveat:
"how others do it" is NVIDIA parametric knowledge, `[judgment]`, not web-verified.

### The answers

- **Q2 (parallel with the gate): YES — it's the cheapest structural win, and it's ~free.** The reckon
  (read-only diff review) and the gate (`validate --staged`: scenarios + spec-pack) have NO data
  dependency; today they run sequentially only by habit. Reorder the loop: after own-review, dispatch the
  reckon AND the gate CONCURRENTLY; **join barrier — commit ONLY if BOTH return green** (the invariant:
  a change never commits before both the review lane and the test lane clear). Wall-clock drops from
  `reckon + gate` to `max(reckon, gate)`. Token cost unchanged, latency ~halved. (Analogy: aviation
  ETOPS dual-engine — two independently-certified engines, both must run, in parallel; CI parallel
  required-checks; async review bots parallel to CI.)
- **Q1 (cheaper/faster): the single biggest token cut is the NON-OVERLAP CONTRACT.** Today the reckon
  RE-RUNS the scenarios/self-check that the GATE already runs — duplicate work. Split cleanly: **gate =
  deterministic correctness (runs the tests); reckon = SEMANTIC judgment (defects, gaming, missed
  blast-radius, spec-violations — what tests CANNOT catch); the reckon is FORBIDDEN from re-running
  scenarios** and instead consumes the gate's results. ~30-40% token cut, immediately. (Nuclear
  defense-in-depth diverse channels; MVCC snapshot review.) Then **pass the pre-assembled seam bundle**
  (the overseer already has the diff+neighbors+exemplars after own-review — hand them over instead of
  letting the reckon re-discover): ~50-60k instead of ~100-150k combined.
- **Q3 (how others do it):** CI runs ALL checks as PARALLEL required-jobs (review is one lane, tests
  another; merge only when all green); async review bots (CodeRabbit/Codium/Graphite/reviewdog/Danger)
  review the diff WHILE CI runs tests; review is DIFF-SCOPED (changed hunks + small neighbors);
  test-impact-analysis runs only affected tests; merge queues batch + parallelize + fast-fail. `[judgment]`

### The KEY meta-insight

**The highest-impact wins are OVERSEER-BEHAVIOR changes, not new infrastructure** — I can adopt them in
HOW I run the loop starting now, no code build: (1) run the reckon and the gate in parallel; (2) the
non-overlap contract (stop re-running in the reckon what the gate already runs; scope the reckon prompt
to pure judgment); (3) pass the seam bundle. That is the 80/20.

### Portfolio (prioritized)

| Bucket | Item | Win | How |
|---|---|---|---|
| **DO-NOW (overseer behavior, zero build)** | Parallel reckon ‖ gate + join barrier | ~half wall-clock | reorder the loop (dispatch both, commit on both-green) |
| **DO-NOW (overseer behavior, zero build)** | Non-overlap contract | ~30-40% tokens | reckon prompt = pure judgment; DROP the scenario re-run (the gate owns tests) |
| **DO-NOW (overseer behavior, zero build)** | Pass the pre-assembled seam bundle | more tokens | hand the reckon the diff+neighbors+exemplars I already have |
| **next (small build)** | Tiered cheaper-model cascade | 60-80% on low/med | cheap fast-path (Haiku/NVIDIA) triage → Sonnet only on flag/high-risk; 1-in-N Sonnet audit for drift |
| **profile-specific (budget-tight)** | AQL statistical sampling | ~60-70% for stable users | full reckon every Nth risk-bearing change, lightweight on others, escalate the ramp on a defect-found |
| **finer (build)** | Trust-tiered reckon depth | ~40-60% on trust-standard | secret/PII/external-surface → deep+expanded blast-radius; other risk-bearing → hunk-only |
| **aposta-de-fronteira (park)** | Async post-commit deep reckon (fast-path commits; slow deep reckon runs async, reverts on a blocker) | latency→0 sync | financial post-trade surveillance — trades the "no bad commit ever" invariant for speed; owner-gated (weakens the pre-commit gate) |
| **estacionada** | Seam-context cache service (.harness/seam-cache) | tokens | heavier than "just pass what you have"; only if the bundle-pass proves insufficient |

### The measure (if pursued)

An experiment could measure reckon tokens/wall-clock before/after the non-overlap contract + parallel
lanes, and the defect-catch rate under the cheaper-model cascade + AQL sampling (the abandon criterion:
any defect the sampled/cheap reckon MISSES that a full reckon caught → tighten the ramp / don't cheapen).
Register when a build is picked up.

## Traceability

`Evidência (NVIDIA cards) → Pergunta → Ideia → Plano → Status` — the portfolio table above IS it; the
DO-NOW rows are adoptable immediately (overseer behavior), the build rows route SPEC-116 when picked up.
