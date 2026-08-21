# Research Round — Dynamic Audit Quorum

Owner-requested (2026-08-03, in-session): decision (b) from `plan-audit-gate-leg.md` — the VERDICT schema + quorum — was judged to be “not that simple” and sent to research. Cohorts FIXED by the owner: generation with 2× Sonnet 5 High + 2× GLM-5.2 (NVIDIA free); INVERTED critique between cohorts (GLM critiques Sonnet material and vice versa).

## Phase 0 — Question, criteria, budget, design

**Question.** How should N (the number of audit seats) and the quorum rule for the `audit` leg of the commit join (`gate ‖ reckon ‖ mutate ‖ audit`) be sized dynamically as a function of demand complexity/size/risk, with the overseer as a PARTICIPANT that may agree or disagree with the audit (arbitration as part of the model), under controlled cost and with fuel awareness?

**Success criteria** (what a good answer must satisfy):
1. A concrete, deterministic N(signals) function using ONLY signals already computable from the staged index (risk profile(s), `gate_affected` reach, diff size) — with no human classification step on the commit path.
2. A quorum rule defined for EVERY reachable N (what constitutes a split, who breaks ties, semantics of overseer-as-participant vs the manual `audit record` fallback).
3. Cost bands by configuration (tokens/latency), with explicit degradation when a vendor is out of fuel.
4. Compatibility with the already-decided leg design: fingerprint-keyed, `verify-status`, `audit waive --reason`, seats through the `review` profile, configuration in `.harness/audit-policy.json`.
5. Every normative recommendation carries `claim → source + date + confidence class`; it feeds decision (b) AND the dependent `audit-seat-sizing` item (do not design sizing twice).

**Declared budget.** Round maximum 160k planned tokens (develop ≤ 80k, refine ≤ 80k, stop-ratio 0.6). Rationale: 8 workers × ~12.1k calibrated required-read tokens + packets + reduces; one divergence wave + one critique wave, with no waves 2–3 unless there is a strong signal.

**Declared width.** 4 + 4, custom mode — NOT the D010 focused default (1–2): the owner FIXED fan-out (2 Sonnet + 2 GLM per phase) to obtain the cross-vendor disagreement signal that found real defects in the P6 gauntlet and in today’s double audit (`audit-dlm2m3-close`: two independent lenses converged on the same finding). Heterogeneity is itself an object of study in addition to method (arXiv:2502.08788: MAD is overrated when heterogeneity is ignored).

**Declared experiment design.** `matched-budget` card (`docs/EXPERIMENT_METHODS.md`): the round produces a candidate N(signals)+quorum policy whose fine-tuning will come from a matched-cost advice-only bakeoff (planned as RF.1 in the body of `audit-seat-sizing`). Measurable outcome: defects-caught per cost, by configuration.

## Phase 1 — Evidence register

`claim | source | type | year | method | limitations | confidence | maturity`

- [repo] Two independent Sonnet 5 High lenses converged on the SAME single finding (store scope in the packet), and neither found a defect in the code itself | `.harness/handoff/audit-dlm2m3-close-s{1,2}-VERDICT.md` | measurement | 2026-08-03 | real double audit | n=1 round | strong | production.
- [repo] The manual two-seat pattern (opus5+sonnet5; terra+fable) found real defects across 5/5 layers of the defect-ledger arc (“a fresh-eyes audit caught a real bug in 5/5 layers”) | `.harness/handoff/brief-defect-ledger-enforcement.md` §6 | measurement | 2026-08-01 | audit history of the arc | selection-biased (only audited arcs) | moderate | production.
- [repo] BLOCK→fix→re-audit with the SAME seat converged (re-audit quorum per cohort) | `.harness/handoff/audit-p6s4-terra-refix-*-VERDICT.md` | measurement | 2026-08-02 | P6 gauntlet | one vendor only | moderate | prototype.
- [repo] Reckon (SPEC-157) proves that a fingerprint-keyed leg with a single human verdict can already hold the join without seat cost | `scripts/harness_lib/validation_stamp.py` `check_reckon`/`stamp_reckon` | repo | 2026-07 | production code | not multi-seat audit | strong | production.
- [repo] Mechanical signals available from staged state: risk profile(s) via `required_profile`, reach via `reckon_reach` (223/223 on today’s commit — high reach does NOT imply deep review when the diff is test-only), diff via numstat | `validation_stamp.py:169/:338` | repo | 2026-08 | — | reach overestimates on test-only surfaces | strong | production.
- [web] Multi-agent debate improves factuality relative to a single agent | Du et al. 2023 (ICML 2024), composable-models.github.io/llm_debate | paper | 2023 | factuality benchmarks | tasks ≠ code review | moderate | validated.
- [web] MAD is overrated when model heterogeneity is ignored — gain comes from HETEROGENEITY, not debate itself | arXiv:2502.08788 | paper | 2025 | ablations | academic benchmarks | moderate | validated.
- [web] LLMs do not reliably self-correct without an external signal — critique needs reproducible verification, not more rounds of the same model | Huang et al., ICLR 2024, arXiv:2310.01798 | paper | 2024 | ablations | — | strong | validated.
- [web] Structural coupling collapses diversity of ideas → independent generation before exposure (supports inverted critique) | arXiv:2604.18005 | paper | 2026 | — | — | moderate | validated.
- [judgment] Overseer-as-seat creates a conflict of interest (it authored the brief the audit judges); overseer-as-ARBITER after verdicts preserves seat independence and is what `audit record` already implements | reference: judgment | — | — | — | opinion | conceptual.

## Phase 2 — Define (briefs)

**B1 — dynamic quorum policy for the audit leg.**
Problem (not tech-shaped): fixed review counts cost too much for trivial demand and do not scale confidence for risky demand; how do we calibrate how many independent eyes a change deserves, and how do potentially divergent opinions become an auditable commit decision — including the voice of the integration owner?
Actors: overseer (integrates and arbitrates), audit seats (independent), owner (policy), the `check_audit` leg (consumes the verdict).
Constraints: signals only from staged index; zero friction below the triviality floor; fuel-aware cost; typed SHIP|BLOCK verdicts with file:line findings; result is a POLICY in `.harness/audit-policy.json`, not a new consensus engine.
Success criteria: the five criteria from Phase 0.

**Human gate:** required by the process; SATISFIED in conversation — the owner designed the round (2026-08-03): fixed cohorts, inverted critique, “that’s good as is.” The DELIVER gate remains human: `research round approve`.

## Phase 3/4 — compiled by `research round audit-quorum-dinamico compile|advance`

```json
{
  "schemaVersion": "1.0",
  "slug": "audit-quorum-dinamico",
  "question": "How should N audit seats and the quorum rule of the commit-join audit leg be sized dynamically, with an overseer participant and fuel-aware cost, from staged-index signals?",
  "successCriteria": [
    "deterministic N(signals) function over risk profile + reach + diff size, without human classification",
    "quorum rule and split/arbitration semantics defined for each reachable N",
    "cost bands by configuration with fuel-aware degradation",
    "compatible with fingerprint-keyed record, verify-status, audit waive and seats via the review profile",
    "normative claims with source+date+confidence; feeds decision (b) and audit-seat-sizing"
  ],
  "experimentDesign": {
    "card": "matched-budget",
    "why": "the candidate policy will be calibrated by an advice-only matched-cost bakeoff (RF.1 of audit-seat-sizing); the round defines the design, the experiment measures defects-caught per cost"
  },
  "budget": {"roundMaxPlannedTokens": 160000, "developStopRatio": 0.6},
  "discover": {"flows": ["repo", "web"], "evidenceSection": "Phase 1 — Evidence register"},
  "define": {
    "briefs": [
      {
        "id": "B1",
        "problem": "fixed review counts cost too much for trivial demand and do not scale confidence for risky demand; calibrate how many independent eyes a change deserves and how disagreement becomes an auditable commit decision, including the integrator's voice",
        "actors": ["overseer-arbiter", "audit-seats", "policy-owner", "check_audit"],
        "constraints": [
          "signals only from staged index",
          "zero friction below the triviality floor",
          "fuel-aware cost",
          "typed SHIP|BLOCK verdict with file:line findings",
          "result is policy in .harness/audit-policy.json, not a new consensus engine"
        ],
        "successCriteria": ["the five Phase 0 criteria"]
      }
    ],
    "humanApprovalRequired": true
  },
  "develop": {
    "profile": "research-divergence",
    "briefs": ["B1"],
    "width": {"mode": "custom", "count": 4, "why": "owner-fixed 2026-08-03: 2x sonnet-5 high + 2x GLM-5.2 for cross-vendor disagreement signal; heterogeneity is an object of study (arXiv:2502.08788)"},
    "budget": {"maxPlannedTokens": 80000},
    "assignment": "zip",
    "fleet": [
      {"id": "sonnet", "executor": "claude", "model": "sonnet", "effort": "high", "count": 2},
      {"id": "glm", "executor": "nvidia-compat", "model": "z-ai/glm-5.2", "effort": "high", "count": 2}
    ],
    "perspectives": [
      {"id": "cost-benefit", "taskProfile": "plan", "title": "Marginal contribution of each extra seat: cost bands, diminishing-return point, fuel-aware degradation"},
      {"id": "reliability-arbitration", "taskProfile": "plan", "title": "Quorum rules under variable N: split, tie-breaking, overseer participant vs arbiter, correlated errors among same-vendor seats"},
      {"id": "mechanical-signals", "taskProfile": "plan", "title": "Deterministic N(signals) from staged index: risk profile, gate_affected reach, diff size; threshold ladder and degenerate cases (reach 223/223 test-only)"},
      {"id": "cross-domain-analogy", "taskProfile": "plan", "title": "Transfer: human code review (Google/SmartBear), aviation redundancy, acceptance sampling (statistical QC), Byzantine quorums — what survives in a commit-gate context?"}
    ]
  },
  "refine": {
    "profile": "research-critique",
    "width": {"mode": "custom", "count": 4, "why": "owner-fixed inverted critique: GLM critiques Sonnet material and vice versa; excludeSameExecutor guarantees inversion"},
    "budget": {"maxPlannedTokens": 80000},
    "assignment": "zip",
    "fleet": [
      {"id": "glm-critic", "executor": "nvidia-compat", "model": "z-ai/glm-5.2", "effort": "high", "count": 2},
      {"id": "sonnet-critic", "executor": "claude", "model": "sonnet", "effort": "high", "count": 2}
    ],
    "lenses": [
      {"id": "evidence-validity", "taskProfile": "review", "title": "Validity and references of Sonnet material"},
      {"id": "operational-cost", "taskProfile": "scan", "title": "Cost/operation of Sonnet material"},
      {"id": "architecture-integration", "taskProfile": "review", "title": "Architecture/integration of GLM material into the audit leg"},
      {"id": "security-risk", "taskProfile": "security", "title": "Risk/security of GLM material (quorum gaming, compromised seat, waive abuse)"}
    ],
    "seedPolicy": {"mode": "cross-vendor", "coverage": "balanced", "excludeSameExecutor": true, "maxFindingsPerSource": 12}
  },
  "deliver": {
    "requireOneOperationPerConcept": true,
    "requireExactlyOnePortfolioBucket": true,
    "autoPromote": false
  }
}
```

## Phase 5 — Deliver

Waves: develop `WF-20260803-060425-620300` (reduce: 15 findings, 0 blockers), refine `WF-20260803-061139-064720` (reduce: 14 findings, 0 blockers, 4/4 valid critics after retry — two RESULT-CONTRACT failures on the first pass, class `wr-schema-discards-work`; the `advance` resume gap was recorded on the board as `research-round-advance-nao-recupera-coho`).

### Operations by concept card

- **C1 — N(signals) ladder by BANDS** (mechanical-signals ideator + architecture critique): **simplified** — the weighted-sum formula is dropped (critique: `required_profile()` returns a SET of names, not a scalar risk; `reachWeight` is undefined in the fail-open `None` case of `reckon_reach`). It becomes a deterministic band table in `.harness/audit-policy.json`: N=0 (n/a) below the floor; N=1 small-risk surface; N=2 risk default; N=3 large diff/high reach (excluding test-only). Signals: `reckon_required`, numstat, changedFiles, affectedScenarios.
- **C2 — Quorum table by N** (reliability ideator): **kept** — N=1: SHIP closes, BLOCK → fix or arbitration; N=2: unanimity for SHIP, any BLOCK blocks; N=3: any BLOCK with a blocker finding blocks (never simple majority over a blocker); every split names the dissenting seat in the record.
- **C3 — Overseer is an ARBITER after verdicts, never a seat**: **kept** — `audit collect` computes the verdict BEFORE the overseer sees the VERDICTs; overseer disagreement = `audit record` (typed override, SPEC-161 actor, never auto-rescued). This answers the owner’s direction: agreement/disagreement exists as a recorded override — not a vote. (Critique rejected the analogy ideator’s BFT model that treated the overseer as an untrusted node.)
- **C4 — Vendor diversity mandatory when N≥2**: **combined** with C1 — interim decision (d) alone reproduces the same-vendor blind spot flagged by the round’s own evidence (two Sonnet seats converging on the same finding). N≥2 ⇒ seats from ≥2 executors (cross-vendor idiom from research_round rule 7); unavailability becomes a RECORDED single-vendor fallback.
- **C5 — Fuel-aware degradation reuses SPEC-165 R13** (`gas_balance`/`_gas_pcts`): **kept** — no new logic; dropping below planned N is RECORDED (reckon override idiom).
- **C6 — `dissent` field in the ledger even for resolved SHIP**: **kept** — this makes the RF.1 cost×defects-caught bakeoff measurable.
- **C7 — Formal Byzantine quorum**: **parked** — conceptual backbone only; the security critique showed that it assumes honest/independent seats and that `f` derived from staged signals is influenceable by the author of the diff itself.
- **C8 — Acceptance sampling (QC) as a sample-size heuristic**: **deferred** — enters as the RF.1 bakeoff design inside `audit-seat-sizing`.
- **C9 — “reach 223/223 test-only ⇒ Nmax + supermajority”** (mechanical-signals ideator): **rejected** — contradicts repo evidence (today’s commit: reach 223/223 with a test-only diff is the DEGENERATE overestimation case; escalation by reach EXCLUDES test-only).
- **C10 — Anti-gaming of signals** (security critique: signals influenceable by the audited diff; salami-slicing to remain below the floor): **deferred** — real risk, minimal mitigation now (floor by fingerprint makes slicing visible in the ledger); dedicated hardening once the leg exists.

### Portfolio

- **core**: C1, C2, C3, C4, C5, C6 — together they answer decision (b).
- **contingency**: recorded single-vendor fallback (C4) when only one vendor has fuel.
- **frontier bet**: —
- **experiments**: RF.1 matched-budget bakeoff (cost×defects-caught by configuration); formal registration through `experiment add` happens when `audit-seat-sizing` opens (owner of the bakeoff), citing this round.
- **parked**: C7, C8.
- **rejected**: C9; weighted-sum formula (wrong signal shape); overseer-as-seat/BFT-node; Nmax 7–9 (not anchored in manual precedent — interim ceiling is 3).

### Experiment (RF.1, declared design)

`hypothesis`: the C1 ladder with C2 quorum catches ≥ the defects of fixed N=2 at lower average cost. `baseline`: N=2 unanimity (manual precedent). `metrics`: defects-caught/round, cost/round (tokens+USD), split rate. `decision criteria`: adopt the ladder if cost falls ≥20% with no detection loss over ~10 real audits; otherwise retain fixed N=2.

### Traceability (Evidence → … → Status)

| Evidence | Problem | Idea | Experiment/ADR | Spec/Task | Status |
|---|---|---|---|---|---|
| VERDICTs dlm2m3 s1/s2 (same-vendor convergence) | vendor blind spot | C4 diversity N≥2 | — | decision (b) of plan-audit-gate-leg | core |
| brief-defect-ledger §6 (2 seats, 5/5 layers) | how many eyes | C1 ladder + ceiling 3 | RF.1 | plan-audit-gate-leg + audit-seat-sizing | core |
| validation_stamp reckon/override idiom | how to record degradation/dissent | C5, C6 | — | decision (b) | core |
| arXiv:2502.08788 + Diversity Collapse | heterogeneity > count | C4; inverted critique | — | — | applied |
| Huang ICLR 2024 (no self-correction) | critique needs external signal | C3 recorded arbiter | — | decision (b) | core |
| reach 223/223 test-only (commit ba21da3) | degenerate signal | C9 rejected; test-only exclusion in C1 | — | decision (b) | rejected/absorbed |
| discarded critic cost (USD 0.98, contract) | seats fail by contract | robustness of collect to invalid seat (re-spawn once, then recorded N-1) | — | plan-audit-gate-leg | core (note) |

### Proposed decision for (b) — awaiting `research round approve` (human gate)

VERDICT schema: as in the brief draft (first line `VERDICT: SHIP|BLOCK`; findings `F<n> — severity — file:line — evidence`; BLOCK without a finding is refused by collect).
Quorum: C1 ladder (0/1/2/3, versioned bands in `audit-policy.json`, interim ceiling 3), C2 rule by N, C4 diversity when N≥2, C5 recorded degradation, C6 dissent in the ledger, C3 overseer-arbiter via `audit record`. After approval: amendment to section (b) of `.harness/handoff/plan-audit-gate-leg.md`, and the brief unlocks implementation.

<!-- round-state:start -->
```json
{
  "cohorts": [
    {"cohortId":"develop-sonnet","phase":"develop","declaredExecutor":"claude","executor":"claude","model":"sonnet","wfid":"WF-20260803-060425-620300","status":"done"},
    {"cohortId":"develop-glm","phase":"develop","declaredExecutor":"nvidia-compat","executor":"nvidia-compat","model":"z-ai/glm-5.2","wfid":"WF-20260803-060425-620300","status":"done"},
    {"cohortId":"refine-glm-critic","phase":"refine","declaredExecutor":"nvidia-compat","executor":"nvidia-compat","model":"z-ai/glm-5.2","wfid":"WF-20260803-061139-064720","status":"done","seed":"WF-20260803-060425-620300","sourceCohortId":"develop-sonnet","workerExecutors":{"worker-001":"nvidia-compat","worker-002":"nvidia-compat"},"minSuccessConfigured":2,"minSuccessEffective":2,"successes":2,"minSuccessMet":true},
    {"cohortId":"refine-sonnet-critic","phase":"refine","declaredExecutor":"claude","executor":"claude","model":"sonnet","wfid":"WF-20260803-061139-064720","status":"done","seed":"WF-20260803-060425-620300","sourceCohortId":"develop-glm","workerExecutors":{"worker-003":"claude","worker-004":"claude"},"minSuccessConfigured":2,"minSuccessEffective":2,"successes":2,"minSuccessMet":true}
  ],
  "deliver": {
    "approvedBy": "human",
    "at": "2026-08-03T10:19:44.195203+00:00",
    "note": "Owner approved in-session (2026-08-03): N ladder 0-3 by bands in audit-policy.json (interim ceiling 3), unanimity for SHIP, any blocker BLOCK blocks, vendor diversity mandatory N>=2 with recorded single-vendor fallback, fuel degradation via R13 recorded, dissent in ledger, overseer-arbiter via audit record. RF.1 matched-budget calibrates bands in audit-seat-sizing.",
    "checks": {"stateComplete":true,"sections":{"operations":true,"portfolio":true,"experiment":true,"traceability":true}}
  }
}
```
<!-- round-state:end -->
