# Adaptive Routing & Reputation — technical proposal

[← Information Survival proposal](information-survival.md) · [Research basis](../research/routing/adaptive-routing-reputation.md) · [Navigation](../NAVIGATION.md)

**Status:** PROPOSED; preserve policy-first order.

## Contracts retained from routing research

RouteContract (workflow requirement), RouteIntent (runtime decision request), CandidateKey, RouteDecision, RuntimeContext/State, RuntimeSuppressionOverlay, OutcomeEvidence/EvidenceFamily, Attribution, Reputation reducer/snapshot and FailureClassifier roles.

## Invariants

RouteDecision persisted before spawn; gate/Authority does not consult reputation to mint eligibility; workflow contract does not freeze concrete model too early; GraphPatch returns through normal routing; runtime suppression can act immediately without deleting historical reputation; hot path is read-only; delayed evidence can update future reputation; fork/join respects quota/diversity constraints.

## Experiment path

Static heuristic baselines → shadow evidence collection → project-local reputation projection → OPE → low-risk canary → bounded exploration only under explicit policy.

## Qualification

Evaluate completion, cost-to-trust, route regret, calibration, fallback causal correctness, delayed outcomes, project-local improvement and negative transfer. Never claim improvement from benchmark leaderboard alone.

---

**Previous:** [Information Survival proposal](information-survival.md) · **Next:** [Resource / Sandbox proposal →](resource-sandbox-assurance.md) · **Deep economics:** [Economics / Resources](../research/routing/economics-resources-observability.md)
