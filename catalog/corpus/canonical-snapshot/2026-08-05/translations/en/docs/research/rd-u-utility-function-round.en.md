# RD-U Round — Harness Utility Function U(route, outcome, cost)

Research-gated backlog item RD-U (`article-coverage-backlog.md`). Owner 2026-07-19:
“make a list and run the research using NVIDIA sequentially.” First of 3 implementation-research rounds.
Orchestrator = this session. Divergence through **NVIDIA** (`nvidia-compat`, glm-5.2).

## Why this round exists

Route **regret** (EXP-17) and **ECE/calibration** are currently NEEDS-NEW-STATE: regret cannot be computed
without a utility function `U` saying how good a routing decision was. Without U, “route A was better than B”
is opinion. RD-U unlocks both at once. This is research on HOW TO IMPLEMENT (which terms, which form, how to
estimate), not academic measurement.

## Round question

> What is the harness utility function `U(route, outcome, cost)` — which terms does it combine, in what
> form (linear/weighted/lexicographic/...), and how do we estimate every term FROM WHAT WE ALREADY HAVE
> (delegation ledger: token cost, latency, kept/rejected outcome; vendor scarcity from N-VENDORCREDIT;
> T-ADAPTERCONF accountingSemantics indicating measured vs estimated tokens)?

## Success criteria

- **Actors:** router (uses U to select/evaluate route), EXP-17 (computes regret = U(optimal) − U(chosen)),
  ECE calibration (route confidence vs outcome).
- **Estimable from current corpus:** every U term must map to a field already produced by delegation ledger /
  model cards / vendor credit — nothing requiring expensive new instrumentation. Owner (D017): “what weighs
  most is tokens spent and time; token and time are money” — U must honor that.
- **Honest about uncertainty:** where outcome is subjective (quality), U marks the term as estimated/proxy;
  it does not pretend to measure. accountingSemantics: vendors that do not truly measure tokens enter with
  lower confidence weight.
- **Deterministic to compute:** given (route, outcome, cost), U(...) is reproducible — no LLM in the
  computation path (LLM may have helped DESIGN U, never compute it in production).
- **Does not reinvent:** reuse delegation ledger (route_ledger), cost_metrics, route scores
  (E-ROUTESCORES), L13 noise floor (difference smaller than jitter is not regret signal).

## Budget + breadth + declared design

- **Wave 1:** 5 NVIDIA ideators, ceiling ~65k tokens (free tier). Gate at 60%.
- **Breadth (D010): EXPLORATORY → 5.** Utility-function design crosses decision theory, MAUT/multi-attribute
  utility, bandit reward design, RL reward shaping, cost econometrics — broad field, no fixed form yet.
  Nominal group pays off.
- **Design (L18):** round FEEDS EXP-17 (regret) and ECE calibration. Candidate method cards (advisory now
  fires — commit e5a1a4b): **evidence-grades** (how strong is evidence that U reflects reality) +
  **matched-budget controls** (compare routes under equalized budget, otherwise U confounds “better” with
  “spent more”). Final card enters synthesis.

## Phase 3 — wave-1 brief

> Design the harness utility function `U(route, outcome, cost)`. It must combine token cost (weighted by
> vendor price), time/latency, and outcome quality (kept vs rejected/reverted) into a number comparable
> across routes; justify its form (why weighted rather than lexicographic, or vice versa); estimate EACH
> term from fields already produced by delegation ledger / model cards / vendor credit; honor
> accountingSemantics (lower confidence weight for vendors estimating rather than measuring tokens) and
> vendor scarcity (scarce tokens are worth more); and be deterministic to compute (no LLM in the calculation
> chain). Deliver: U TERMS, FORM (with rationale), term→ledger-field MAP, and how regret =
> U(optimal)−U(chosen) and confidence for ECE derive from U.

---

# Phases 3–5 — Result and Synthesis (RD-U)

Wave 1: `WF-20260719-054755-523380`, 5 NVIDIA ideators (glm-5.2).

## Independent convergence (strong signal — ALL 5)

**Form = WEIGHTED-LINEAR, normalized/bounded.** All 5 chose linear over lexicographic AND Cobb–Douglas,
with the SAME triple rationale (w-001, w-004): linear is the only form that (a) gives a scalar comparable
across routes, (b) is deterministic O(1), and (c) permits per-term comparison against noise floor.
Lexicographic form produces no scalar ΔU for ECE; Cobb–Douglas (multiplicative) breaks comparison with L13
and collapses U→0 when Q=0 (rejected route) — w-005 itself refuted the Cobb–Douglas form it initially
suggested (ideator honesty).

## Converged function

```text
U(route) = w_q·Q·τ  −  w_c·C·S  −  w_t·T
```

| term | meaning | corpus field (zero new instrumentation) |
|---|---|---|
| **Q** | outcome quality: kept=1, reverted=0.5*, rejected=0 | `route_ledger` outcome enum |
| **τ** (w-004) | accountingSemantics trust discount: vendor MEASURING tokens τ=1, ESTIMATING τ<1 | T-ADAPTERCONF `accountingSemantics` |
| **C** | cost = tokens × vendor price, normalized by route class | ledger token-cost + model-card price |
| **S** | scarcity = `max(1, 1/(remainingCredit/initialCredit))` — near-exhausted vendor token costs more | N-VENDORCREDIT |
| **T** | latency normalized by route-class budget/p99 | ledger latency + E-ROUTESCORES/cost_metrics |

\* `reverted=0.5` is U’s ONLY subjective constant (w-001 flagged it: validate; if revert ≈ near-failure,
0.25 may be better). Recorded as the only parameter to calibrate.

## What each perspective added

- **w-001 (simplicity):** S and τ as MULTIPLIERS inside cost/quality terms, not separate terms — keeps 3
  terms. `regret = U(best)−U(chosen)`; ECE through sigmoid-normalized U-gap; `|ΔU| < noiseFloor L13 → tie`
  (no regret signal).
- **w-002 (scale):** bounded [0,1] normalization for cross-route comparability; T normalized by route-class
  p99 (from cost_metrics).
- **w-003 (reliability):** OPS edge case — define U for **timeout/partial failure** (U=0 or explicit penalty),
  otherwise a route that hangs becomes noise.
- **w-004 (trust boundary):** τ (trust discount) — without it, U treats a vendor that GUESSES token count
  like one that MEASURES. + **privacy:** U touches only AGGREGATES (cost/latency/outcome), NEVER payload
  content; computed inside ledger trust zone, WITHOUT vendor API call (otherwise vendor observes routing
  decision and can infer competitor usage). ECE uses Q·τ as predicted probability.
- **w-005 (analogy): Sharpe ratio / mean-variance finance** — `U = E[R] − (λ/2)·σ²·scarcity`:
  return=quality, RISK=variance, cost=fees. **Sharpe variance IS L13 noise floor** — a route with high
  outcome variance is riskier. + **Brier score (meteorology)** decomposes reliability = ECE. Variance term
  remains for v2 (linear is v1).

## Concept cards + operation

| card | operation | why |
|---|---|---|
| **U-LINEAR** (function above) | **kept** — core | proven form, deterministic, all terms available in current corpus |
| **U-TAU** (accountingSemantics trust discount) | **kept** | closes “vendor that guesses = vendor that measures” gap |
| **U-SCARCITY** (S from N-VENDORCREDIT) | **kept** | honors D017 (scarce token is worth more) — depends on N-VENDORCREDIT `remainingCredit` |
| **U-VARIANCE** (Sharpe: penalize outcome variance) | **deferred (v2)** | needs N observations per route to estimate σ²; linear v1 does not. Upgrade when corpus exists |
| **U-OPS** (U on timeout/failure) | **split** | defines U=0/penalty for failure — becomes part of U spec |
| **reverted=0.5** | **experiment** | only subjective parameter; calibrate against real revert data |

## Buildable vs owner-gated

- **Buildable now (measurement):** U as a PURE FUNCTION computed over existing route ledger, feeding a
  measure-only regret probe (EXP-17). Does not change routing, only measures — within measure-first
  authority, like other probes.
- **Owner-gated:** using U to DRIVE routing (bandit/C4/RF.1 phase 2) — already owner-gated. N-VENDORCREDIT
  must also exist for S to have real data (until then S=1, honestly marked).

## Traceability

| Evidence | Idea | Experiment | Task | Status |
|---|---|---|---|---|
| 5/5 (weighted-linear) + w-005 Sharpe/Brier | U-LINEAR + U-TAU + U-SCARCITY | feeds EXP-17 regret + ECE | RD-U→U-function | designed, buildable (measure-only) |
| w-001 (`reverted=0.5`) | calibrate constant | candidate EXP | reverted-calibration | open |
| w-005 (variance=L13) | U-VARIANCE v2 | — | parked | deferred |
