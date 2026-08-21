# Implementation Plans — U(route, outcome, cost) (RD-U)

Parked in the backlog. Derived from `rd-u-utility-function-round.md` (5 NVIDIA ideators) + D021.
Unlocks route **regret (EXP-17)** + **ECE/calibration** (currently blocked by the absence of U).

**Reuse:** `route_ledger.py` (kept/rejected outcome, token cost, latency by route); `cost_metrics.py`
(price); model cards (price per token); N-VENDORCREDIT (scarcity S); `accountingSemantics`
(T-ADAPTERCONF: which vendors MEASURE tokens vs ESTIMATE = τ); E-ROUTESCORES (latency baseline);
L13 noise floor. EXP-17 = the regret consumer.

---

## N-U-FUNCTION — U as a pure measure-only function · BUILDABLE NOW · size M

**Goal:** compute `U(route) = w_q·Q·τ − w_c·C·S − w_t·T` over the existing route ledger, feeding
a measure-only regret probe (EXP-17). It does not change routing (that is owner-gated) — it only MEASURES.

**Approach (the function, D021):**
- **Q** = ledger outcome (kept=1, reverted=0.5*, rejected=0). *`reverted=0.5` is the ONLY subjective
  constant → calibrate it (candidate EXP: if revert ≈ near-failure, 0.25).
- **τ** = trust discount from `accountingSemantics` (vendor that MEASURES tokens τ=1; one that ESTIMATES τ<1).
- **C** = tokens × vendor price, normalized by route class (ledger + model cards).
- **S** = scarcity = `max(1, 1/(remaining/initial))` from N-VENDORCREDIT (until it exists, S=1 and marked as such).
- **T** = latency normalized by the route-class p99 (ledger + E-ROUTESCORES).
- **weighted-linear** form (rationale: the only one that yields a comparable scalar + O(1) + per-term
  comparison against the noise floor; lexicographic form gives no ΔU; Cobb–Douglas breaks L13 + collapses at Q=0).
- **regret = U(best) − U(chosen)**; `|ΔU| < noiseFloor L13 → tie`. **ECE** using Q·τ as the predicted
  probability (Brier score, w-005).

**Footprint:** `harness_lib/utility.py` (the pure U function + regret + confidence-for-ECE); one probe
`testing/probes/regret_probe.py` that runs U over the route ledger and emits the regret distribution
(measure-only, sibling of truth-divergence). Feeds EXP-17.

**Acceptance:** U computes deterministically over the ledger; regret = subtraction of 2 scalars; `|ΔU|<L13` =
tie; confidence-for-ECE comes from Q·τ. Self-check (U monotonic in its terms; empty→0). ZERO routing changes.

**Gate:** measure-only (computes a number from the existing ledger; does not drive route selection) — measure-first authority.
**Dependency:** route ledger (exists); S degrades to 1 without N-VENDORCREDIT. **Size:** M.

---

## N-U-VARIANCE (v2) — variance term (Sharpe) · DEFERRED · size M

**Goal:** the w-005 insight (Sharpe) — penalize route OUTCOME VARIANCE (variance IS the L13 noise floor;
a high-variance route is riskier). `U = ... − (λ/2)·σ²`.

**Approach:** needs N observations per route to estimate σ² — linear v1 does not. Defer until the
route-ledger corpus has enough N per route. Preserve the upgrade path.

**Gate:** deferred (measure-first: no corpus, no σ²). **Dependency:** N-U-FUNCTION + corpus. **Size:** M.

---

## N-U-DRIVING — U driving routing · OWNER-GATED (control) · size L

**Goal:** use U to SELECT/evaluate a route (bandit/C4/RF.1 phase 2). This is control → it was already
owner-gated; requires N-U-FUNCTION + measured regret (EXP-17) as justification.

**Footprint (when opened):** connect U to the router (SPEC-144); integrate with GUI Simulate-route (GUI-RG3).
**Gate:** OWNER-GATED. **Dependency:** N-U-FUNCTION + EXP-17 corpus. **Size:** L.

---

## Suggested order
1. **N-U-FUNCTION** — buildable; unlocks regret+ECE (EXP-17) without touching routing. + calibrate reverted=0.5.
2. **N-U-DRIVING** — only when measured regret justifies it (owner-gated).
3. **N-U-VARIANCE** — v2, once a per-route corpus exists.
