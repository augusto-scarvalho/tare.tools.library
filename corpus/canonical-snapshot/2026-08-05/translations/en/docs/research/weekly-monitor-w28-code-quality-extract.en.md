# Weekly Monitor W28 (Agentic Code Quality) — Harness Extract

Source: weekly GPT digest supplied by the owner (2026-07-13). This is NOT a research round (same instruction
as memory extract: do not run the skill); citations are unverified `[web]` references — ideas evaluated on
internal merit against the real harness state. Companion to `weekly-monitor-w28-memory-extract.md`;
experiment numbering continues (EXP-4..6).

## Where the harness ALREADY covers the digest (no new work)

| Digest finding | Equivalent already operating here |
|---|---|
| #1 Patchwork Problem (graphs + structural invariants) | Partial: Graphify is graph representation (AST/imports); declared-vs-real verifiers already live: spec_test_gate (`Scenario: [id]` ↔ literal `check("id")`), frozen CLI surface (FROZEN_TOP_LEVEL), WORKER_RESULT schema vs actual payload, protected-files registry, agent_parity. What does NOT exist is systematic inventory of pairs → EXP-4 |
| #2 Failure as a Process (early epistemic error, trajectory intervention) | Overseer-plans model IS institutionalized early intervention: premises resolved BEFORE worker spends (plan with FINAL decisions + HARD footprint); typed `planDeviations` is the “premise was false” channel; `harness.py review` runs before commit (mid-trajectory, not post-merge). Residual: epistemic error in the plan ITSELF (Q10 incident) → EXP-6 |
| #3 SCATE / lazy generation | newly shipped `oracle mutate` detects exactly the symptom (SURVIVED → ORACLE-WEAK; first live round: 3 correct survivors). Bandit router remains parked (telemetry is 1 day old) |
| Agentic Rubrics (ACL) | Spec Gherkin ARE contextual rubrics; GLM spec-QA wave was cheap multi-vendor rubric checking |
| SWE-Mutation (ACL) | `mutation_probe.py` shipped today: deterministic AST mutants, cap 3, byte-identical restore — observe-only version with zero LLM cost |
| SecureVibeBench (non-compensable security) | security-baseline exists observe-only by owner decision (#1); beyond that is OWNER-GATED — pending a decision, not a trigger |
| RuBench (silent model fallback) | We lived the incident: codex ≥0.144 ignoring project profiles (spec esh) — explicit flags were the band-aid. REAL provenance is recorded nowhere → EXP-5 |
| SLBench (skills with logical preconditions) | Partial: skills registered in capabilities.json; preconditions in prose. 3 skills today — parked |

## Extracted experiments (reversible; research-playbook template)

### EXP-4 — Patchwork replay probe (declared-vs-real) · HIGH priority
- **Hypothesis:** harness has N declared-vs-real pairs and only some have a verifier; real violations pass
  green gates (placebo compact hook lived for weeks with everything green — our estimation Patchwork Problem).
- **Candidate inventory** (calibrated by historical incidents, as digest asks): keys in `model-routing.json`
  declared vs read by code; skills in `capabilities.json` vs `SKILL.md` present; emitted events vs existing
  consumers; task-profile spawn mappings vs executor cards; registered hooks vs observable effect (placebo);
  declared trustTier vs worker actions.
- **Baseline:** run inventory ONCE; count pairs without verifier + live violations today (deterministic probe,
  zero LLM).
- **Metric:** recall of real violations per cost — not alert volume (digest rule adopted wholesale).
- **Phase 2 (only pairs where a violation is found):** each pair becomes an advisory doctor check
  (intake-staleness pattern). **Reversal:** advisory checks, one line removed each.

### EXP-5 — Model-provenance audit (RuBench-lite) · HIGH priority, cheap
- **Hypothesis:** REAL model that served each delegation is not recorded: ledger stores REQUESTED model
  (self-declared by overseer), WORKER_RESULT has no model field, and `tools/openai_worker.py` discards the
  API response `model` field (verified 2026-07-13). Real evaluation unit is
  product+harness+fallback-policy+model.
- **Phase 1 (zero risk):** openai_worker appends `response.model` to result; codex: parse `exec` banner;
  delegation ledger gains optional `servedModel` field (additive, `(none)` for old records — byOutcome pattern).
- **Metric:** % delegations with requested≠served; any value >0 is actionable finding.
- **Reversal:** additive ignorable fields.

### EXP-6 — Epistemic preflight for plan brief · MEDIUM priority
- **Hypothesis:** residual epistemic error in the loop lives in the overseer plan, not worker (Q10: plan said
  latin-1, artifacts were CP1252 — 1 plan defect in 12 briefs ≈ 8%).
- **Phase 1:** “Verified assumptions (with evidence)” section in playbook plan-brief template — every
  non-trivial premise cites command/read that confirmed it BEFORE brief delivery.
- **Phase 2 (deterministic, optional):** `review --preflight <brief>` — footprint paths exist or are marked
  `(new)`; cited verify commands exist on CLI surface. Advisory, rc 0.
- **Metric:** rate of planDeviations attributable to plan defects per loop session, before/after.
- **Reversal:** template section + advisory mode.

## Parked (with explicit trigger)

- **Oracle Action Router (SCATE):** trigger = weeks of accumulated byOutcome + oracle telemetry; composite
  reward needs metrics we still do not measure. Current fixed policy IS the baseline router must beat.
- **Diversify2Verify:** trigger = first critical function requiring formal verification; n-variant cost too
  high for current profile.
- **Calibrated LLM mutants (full SWE-Mutation):** trigger = deterministic mutation-probe menu saturates
  (survivors drop to zero while real bugs still appear).
- **Internal SLBench (compiled skill preconditions):** trigger = first operational skill failure caused by
  violated precondition; today only 3 skills and prose is sufficient.
- **Non-compensable SecureVibeBench gate:** no trigger — OWNER-GATED (security-baseline beyond decision #1);
  awaits owner decision, not evidence.

## Critical verdict on the digest

Without knowing it, this digest validates with literature the batch we shipped TODAY: review verb = trajectory
intervention (#2), mutation probe = weak-oracle detection (#3/SWE-Mutation), planDeviations = typed epistemic
error (#2), byOutcome = measurable economics (#3). Genuine actionable novelty is two cheap measurement
probes: EXP-4 (declared-vs-real inventory) and EXP-5 (model provenance — gap confirmed in code). EXP-6 attacks
the only part of our loop illuminated by the digest that we still do not instrument: overseer plan as source
of false premise. Nothing here justifies adaptive routing or variant generation before these measurements exist.
