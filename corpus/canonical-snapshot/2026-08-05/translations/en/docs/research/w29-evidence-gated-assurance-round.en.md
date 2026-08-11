# Research Round — W29: Evidence-Gated Assurance (Weekly Monitor, Jul 13–20, 2026)

Owner 2026-07-21: Double Diamond round over the weekly agentic-code-quality monitor feed. Executors: **NVIDIA (`nvidia-compat`) + Sonnet 5** (D012 / compaction-round pattern). Orchestrator = this session (Fable). Primary sources VERIFIED via WebFetch against arXiv abstracts on 2026-07-21 (digest numbers match).

## Phase 1 — Evidence (verified)

| claim | source | prov | conf | maturity |
|---|---|---|---|---|
| State transitions gated by mechanical evidence reduce false-pass 31→2 across 1,800 injected cells; 18 tampering classes rejected; reviewer without a gate ≠ gate (14 vs 2 failures) | Proof-or-Stop, arXiv:2607.14890 (2026-07-16) | [web] verified | moderate (1 model family; self-hosted corpus) | prototype |
| Agentic tests: better edge-case variety (0.62 vs 0.32) and null-safety (13.4% vs 8.3%), BUT more flakiness candidates (0.41 vs 0.30) and slightly weaker assertions (85.4% vs 88.1%); 204,673 artifacts, static AST proxies, Python-only | Beyond Test Presence, arXiv:2607.12068 (2026-07-13) | [web] verified | strong (scale) / moderate (proxies, not execution) | validated (static) |
| E3 (Estimate→Execute→Expand-on-failure): −85% cost, −91% tokens, −92% files read while maintaining 100% success on MSE-Bench (121 edits, simulator; real validation = 1 agent/1 library) | E3, arXiv:2607.13034 (2026-07-14) | [web] verified | moderate (controlled benchmark, simple tasks) | prototype |
| Evaluate the artifact CHAIN (requirements→model→validation→report) rather than only final output: 56.8%→88.6% pass across 10 agent-model combinations | StructureClaw, arXiv:2607.14896 (2026-07-16) | [web] verified | moderate (structural-engineering domain) | prototype |
| Layered quality (static→functional→semantic→hardening); specialized skill +10.31pp average rubric pass rate, 6 models | Alipay-PIBench, arXiv:2607.14573 (2026-07-16/17) | [web] verified | moderate (18 instances, 1 ecosystem; rubric partly LLM = pseudo-oracle) | prototype |
| Full digest (analyses, impact tables, recommended experiments) | owner’s GPT monitor, 2026-07-21 | [web] NOT verified beyond the five primaries | report | — |

## What the harness ALREADY has (feed-portfolio → real state; do not re-propose)

- **Risk-adaptive gates** → CQ.1 risk-tier gate selection SHIPPED (consumes `security['new']`; fail-closed unknown→medium); intake triage by request profile.
- **Evidence bundles** → CQ.2 QA evidence capsule + `rerunCmd` SHIPPED (handles-not-bodies); fold/handles/digest. Missing: FRESHNESS/invalidation and a gate that BLOCKS transition.
- **Quality-debt ledger** → CQ.3 provenance record SHIPPED (records + subject). Missing: flakiness/assertion quality as recorded debt; post-merge tracking.
- **Oracle mesh** → heterogeneous `spec_test_gate` + `oracle mutate`/`mutation_probe.py` SHIPPED (observe-only, cap 3, honest exit classes). CQ.4 (oracle replay) and CQ.5 DEFER in shared oracle runner (not built).
- **Proof-carrying patches** → SEC.7 admitter DEFER (deterministic recompute at finalize; “reviewer.result.json is testimony, not proof”).
- **E3-adjacent** → TE.1–TE.5 economy, doc-find-first (search guard), context diet (−59%/turn), D010 declared width. Missing: minimum-execution ladder PER TASK with expand-on-failure; effort is currently chosen by the overseer, not estimated/escalated.
- **Temporal validity of evidence** → independent INTERNAL convergence: wave WF-20260720-175712 (THEME1 safe-skip) already proposed invalidation events (gate-version bump, graph rebuild, flaky scenario) + gate-state manifest — the feed converges to the same place.
- **Shadow benchmark / hidden checks** → DOES NOT exist (earlier park: private benchmark is its own round).
- **Architectural sentinel** → partial (Graphify + `spec_test_gate` structural checks).

## Phase 0 — Question, criteria, budget, width, design

**Question.** Given what is already shipped above, WHAT should the harness adopt from W29: (a) state transitions gated by fresh/bound evidence (Proof-or-Stop), (b) test quality as separate signals feeding the ledger (Beyond Test Presence), (c) minimum sufficient execution with expand-on-failure (E3) — and how, without violating invariants (deterministic-first, no daemon, stdlib-core, observe→enforce, fail-closed, net-cost-positive, evidence≠formal proof)?

**Success criteria.** Buildable items mapped to a VERIFIED seam (file/module); each moves ONE named metric; honest distinction between evidence-carrying and proof-carrying; nothing re-proposes shipped work; critiques cite source/measurement; uncertainty recorded.

**Declared budget.** One dual-vendor divergence wave: NVIDIA 5 ideators (research-divergence, free credits, D012) + Sonnet 5 with 3 ideators (bounded subagents, one per brief). Convergence by orchestrator with deterministic seam verification. Critique wave only with headroom + strong signal (default: no).

**Declared width (D010).** Exploratory — three independent themes from five papers, without a single implementation target; NVIDIA five lenses + Sonnet three lenses; Δm justified by vendor-independent cross-verification (compaction/PTC round pattern).

**Declared design (L18).** Likely experiments → `EXPERIMENT_METHODS.md` cards: false-DONE probe → **Oracle recall**; E3-ladder vs full comparison → **Matched-budget controls**; repetition-based flakiness → **Noise floor** + **Confidence sequences**; observe→enforce gate promotion → **Evidence grades**.

## Phase 2 — Briefs (gate: scope/waves/budget pre-approved by the owner invocation)

**Brief 1 — Transition only with evidence (Proof-or-Stop → harness).** How could workflow state transitions (fulfilled → reviewed → finalize/DONE) REQUIRE current, commit-bound, mechanically re-checkable evidence (CQ.2 capsule + rerunCmd + SEC.7 recompute), with explicit invalidation events (rebase, dependency change, test edit — overlaps THEME1 safe-skip) — actors: overseer/reviewer/gate; constraints: deterministic recompute, no claim of formal proof, fail-closed, O(capsule) cost?

**Brief 2 — Test quality as signal, not presence (Beyond Test Presence → harness).** How to measure quality of tests/self-checks written by agents — assertion strength, hermeticity (fs/network/clock/order), flakiness under repetition, mutant kill — as SEPARATE signals (never a single score) feeding CQ.3 provenance record as debt — stdlib AST proxies first, bounded repetition, observe-first?

**Brief 3 — Minimum sufficient execution with guardrails (E3 → harness).** How to escalate effort per task (estimate → minimum path → expand ONLY on verification failure) in a ladder that preserves a small set of cheap ALWAYS-ON global invariants (E3 × sentinel tension) — fit: intake triage, CQ.1 tiers, spawn economy effort/model; metric: cost/round without higher rework?

---

# Phase 3 — Waves (dual-vendor, independent)

- **Wave A (NVIDIA)**: `WF-20260721-205509-246398`, research-divergence, five GLM ideators (`nvidia-compat`), self-contained packet. Round 1: 3/5 valid; retry: worker-004 (trust-boundary) recovered; worker-004 had failed contract (high finding without `sourceFilesVerified`), worker-005 (analogy) was WITHHELD twice by collect’s secret scan (it wrote examples matching API-key format; boundary WITHHOLDS by design — not bypassed). Partial reduce: **4/5 valid, 22 deduped findings, 0 conflicts**.
- **Wave B (Sonnet 5)**: three independent ideators (one per brief), read-only with seam verification line by line against real code. 18 concept cards (B1-1..6, B2-1..6, B3-1..6).
- **Load-bearing correction from Wave B** to Phase 0 baseline: CQ.1 is shipped **observe-only** (`spec_test_gate.py:1226` emits tier; no consumer decides execution from it) — becomes the central F3 argument.

## Wave 2 (speculative, owner 2026-07-21: “without the anchor, do not re-propose”)

Waves 2–3 of the playbook (structured generation techniques; WITHOUT `--seed`, generation remains independent). **Declared width (D010):** exploratory — NVIDIA five technique branches (assumption inversion, TRIZ contradiction, provocation, analogical transfer, morphological recombination) + Sonnet three free lenses (inversion/future, wild analogy, self-evolution). Δm: each branch is a distinct TECHNIQUE, not a perspective — expected overlap low. **Budget:** research-divergence + three bounded subagents; convergence by orchestrator. Deliberately loose rules: may collide with what exists (dedup in convergence), seam not mandatory, marked [judgment] speculation welcome; maturity declared per idea.

### Wave 2 result (2026-07-21)

`WF-20260721-212457-539637`: 5/5 NVIDIA technique branches (25 deduped findings, reduce done; morphology worker needed one retry for missing result) + three Sonnet workers (21 ideas). Total 46 raw ideas. **Vendor-independent convergence clusters:**

1. **Evidence that rots** — mark-to-market (Sonnet analogy) + PROOF-THAT-ROTS (NVIDIA morphology) + temporal validity from the feed: freshness CONTINUOUSLY priced (churn distance), not only binary invalidation. Direct conceptual upgrade of N2/N3.
2. **Trust as dynamic currency** — largest cluster: betting market + code insurance (NVIDIA provocation), 2028 trust market (Sonnet), shifting burden of proof (Sonnet analogy), REPUTATIONAL-DEPRECIATION/EXPIRING-VETO/CONTESTED-IMMUNITY (morphology), cost-quality curve (self-evolution). Rigor by track record, not static rule.
3. **Author ≠ attestor, radically** — third-party-captured evidence (NVIDIA inversion), GHOST-AUDITOR (adversary during execution), agent tribunal, agent thymus.
4. **Gate dissolved across time** — continuous gate-ahead (mid-generation), ambient gate (invariants LSP), staged gate/pre-validation in cache (TRIZ).
5. **Staged promotion with surveillance** — clinical phases I–IV (NVIDIA) ↔ automatic rule probation + metric-based reversal (Sonnet self-evolution, with safeguards named for deliberate limits).
6. **Invalid state made unrepresentable** — walled garden (constrained decoding), repo-that-refuses (footprint as OS capability — seed ALREADY exists: SPEC-148 OS locks), deterministic counter-power, transactional vault.
7. **Memory/immunity of a long-lived harness** — acquired immunity (failure-class signatures), adaptive self/non-self tolerance of findings, configuration ancestor archive (best ancestor ≠ newest, Darwin Gödel).

**Notable singletons:** double-entry ledger (every event with reconcilable debit+credit); gate MEL (declared degradation with deadline+compensation, never silent); andon cord (any worker may stop the line); blameless postmortem (ledger records discarded attempts); intermediate perturbation (calibrated chaos); time-to-triage as KPI of the loop itself; contractive context with fidelity-gated semantic GC; spectral trust with risk budget per workflow.

**Status:** harvest delivered; owner chose three bets (2026-07-21) and they SHIPPED observe-first the same day: **proof-that-rots** (`evidence_decay.py` + `headSha` in plan + sha in finalize provenance = closes W29.N1), **rigor by track record** (`track_record.py` + `trackRecord` section in `metrics`, info-only), **permanent adversarial canary** (`oracle canary`/`--trend`/`mutate --record` = closes the persistence half of W29.N4). Backlog: W29.A1–A3. Remaining ideas stay parked here awaiting selection.

# Phase 4 — Cross-vendor convergence + explicit operations

## Convergences (vendor-independent = round validation signal)

1. **ONE enum for invalidation events** — three independent sources: NVIDIA (F1-INCR-01 registry; model-swap/secret-rotation events from trust-boundary), Sonnet B1-3 (promote taxonomy from `gate-affected-cache.md:57-60` to shared module), and prior INTERNAL convergence (WF-20260720-175712 THEME1). Strongest convergence of the round.
2. **Evidence bound to commit by content hash + SHA** — NVIDIA F1-PERF (verdict cache keyed by content-hash+SHA) + F1-INCR-02 (staleness TTL) ↔ Sonnet B1-1 (`capsuleHeadSha` in review gate), B1-2 (close sha TODO in CQ.3, `workflow_lifecycle.py:108`), B1-4 (hash test edited after execution).
3. **stdlib AST proxies as ledger debt, SEPARATE signals** — unanimous (NVIDIA w-001/002/003 + Sonnet B2-1/2/5). Sonnet sees what blind worker does not: CQ.5→CQ.3 wire is LOOSE (`mutation_probe` computes killed/survived and persists nothing; `cli_registry.py:96` is the only caller).
4. **Flakiness: static candidate → bounded dynamic confirmation (cap ~3)** — NVIDIA F2-INCR-02 ↔ Sonnet B2-2/B2-3 (same philosophy as MAX_MUTANTS=3).
5. **E3 ladder with a SMALL set of always-active invariants, using an EXISTING DETERMINISTIC estimator** — NVIDIA F3 (ladder + invariants as pre-fixed checkpoint) ↔ Sonnet B3-1 (CQ.1 tier consumer), B3-4 (invariants = three already-existing non-skippable mechanisms; do not invent a new list), B3-5 (TE.7 is expand-on-failure already designed). Both vendors: DO NOT add an LLM estimator.

## Conflicts/tensions (recorded, not hidden)

- **C1**: owner of `executionLevel` — downstream CQ.1 consumer (B3-1, loose coupling) vs field in SPEC-144 router wire contract (B3-2). Decision: B3-1 first; B3-2 parked (same light-vs-heavy pattern as prior rounds).
- **C2**: statistical-sampling flakiness (NVIDIA F2-PERF) vs fixed deterministic cap (Sonnet B2-3). Deterministic-first DNA → fixed cap; sampling parked.
- **C3**: evidence-verdict cache (NVIDIA F1-PERF) is an OPTIMIZATION over simple freshness check (B1-1) — only if freshness check measures expensive. Contingency.
- **C4** (from the wave itself): B1-5 (testimony×capsule cross-check) risks scope creep into total recompute (= SEC.7, deferred). Kept as cross-check ONLY.

## Explicit operations by concept

| Concept | Operation | Destination |
|---|---|---|
| B1-2 close sha TODO in provenance (CQ.3) | kept | core N1 |
| B1-3 + NVIDIA registry + w-004 model-swap → single invalidation enum | combined | core N2 |
| B1-1 capsuleHeadSha + B1-5 testimony×exitClass cross-check | combined | core N3 |
| B1-4 post-execution test hash | combined (event in N2, check in N3) | core N2/N3 |
| B2-4 mutation-probe→ledger wire + B2-5 single signal schema | combined | core N4 |
| B2-1 + B2-2 AST proxies (+ unanimous NVIDIA F2) | kept | core N5 |
| B2-6 observe-only surface in gate | kept (depends N4/N5) | core N6 |
| B3-1 tier→level consumer (+ NVIDIA F3 ladder) | kept | core N7 |
| B3-4 name/freeze the three existing invariants as floor | simplified (doc, not code) | core N8 |
| false-DONE probe (feed + Proof-or-Stop) | experiment | EXP-31 |
| B2-3 bounded repetition for flakiness | experiment | EXP-32 |
| B3-5 promote TE.7 as ladder (A/B already prescribed) | experiment | EXP-33 |
| NVIDIA F1-PERF verdict cache | deferred | contingency (trigger: freshness check is expensive) |
| B3-3 diff_scope axis (size) | deferred | contingency (trigger: EXP-33 shows underestimation on broad diff) |
| B1-6 servedModel as invalidation | deferred | frontier bet (prerequisite: classify LLM-judged vs deterministic evidence; overlaps EXP-5) |
| B3-2 executionLevel in router wire | deferred | parked (C1) |
| NVIDIA F2-PERF statistical sampling | deferred | parked (C2) |
| B3-6 no-downgrade rule (ESI) | deferred | parked (until ladder exists) |
| w-004 egress hermeticity + secret-in-fixture | deferred | parked (overlaps SEC agenda; no new trigger) |
| PERF-CROSS token-bound early exit | deferred | parked (TE territory; requires own measurement) |
| single test-quality score | rejected | (by brief instruction + paper) |
| LLM complexity estimator | rejected | (both vendors: computable function) |

# Phase 5 — Portfolio

- **Core** (build order; all observe-first, seams verified): N1 sha in CQ.3 (`workflow_lifecycle.py:108`, marked TODO) → N2 shared invalidation-events enum (combines gate-affected-cache + THEME1) → N3 freshness in review gate (`capsuleHeadSha` + exitClass cross-check, `workflow_reduce.py:488-528`) → N4 mutation-probe→records wire + single signal schema (`result_contracts.py:18` reused) → N5 `test_quality_ast.py` proxies (assertion/edge/null/flaky-candidate, separate signals) → N6 check_* observe-only in gate → N7 tier→level consumer (`spec_test_gate.py:1226`) → N8 “universal floor” doc (router floor + `_RISK_HIGH_FILES` + HARD footprints).
- **Experiments** (registered): EXP-31 false-DONE probe (method card: Oracle recall), EXP-32 bounded flakiness repetition (cards: Noise floor + Confidence sequences), EXP-33 TE.7 ladder A/B (card: Matched-budget controls).
- **Contingency**: verdict cache; diff_scope.
- **Frontier bet**: servedModel/model-swap enforcement (overlaps EXP-5).
- **Parked**: B3-2, statistical sampling, ESI no-downgrade, egress/fixture hermeticity, token early-exit.
- **Rejected**: single score; LLM estimator.

## Traceability

`Evidence → Problem → Idea → Experiment/ADR → Spec → Task → Status`:
- arXiv:2607.14890 → transition by testimony → N2/N3 (+EXP-31) → DECISIONS D-w29 → backlog EG.* → proposed
- arXiv:2607.12068 → invisible test quality → N4/N5/N6 (+EXP-32) → DECISIONS D-w29 → backlog TQ.* → proposed
- arXiv:2607.13034 → maximum effort by default → N7/N8 (+EXP-33) → DECISIONS D-w29 → backlog EL.* → proposed
- StructureClaw/PIBench → reinforcement (artifact chain; layered quality) → no own item (already covered by capsules/tiers) → — → covered
