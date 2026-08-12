# Adaptive Routing, Reputation & Qualification

[← Protocols & Interoperability](../runtime/protocols-interoperability.md) · [Navigation](../../NAVIGATION.md) · [All Research](../README.md)

**Status:** RESEARCH; adaptive policy remains subordinate to Authority.

**HTML/source edition:** [Routing / Economics / Observability scientific refresh — 2026-08-11](../../bridge-editions/2026-08-11/routing-economics-observability-scientific-refresh.html)

## Decision order

```text
Policy / Authority
 → eligibility
 → capability fit
 → runtime availability/suppression
 → budgets/quotas/resources
 → project-local predicted utility/reputation
 → bounded exploration if allowed
 → RouteDecision persisted before spawn
```

Reputation never creates eligibility.

## Evidence model

Route decisions should pin candidate/context/evidence epoch before execution. Outcomes may arrive later. Reputation is a materialized view over evidence, not an autonomous source of truth.

## Local versus global

Global priors support cold start; Project-local posteriors should dominate with sufficient evidence. Cross-project transfer requires applicability/transportability and explicit negative-transfer measurement.

## Temporal routing

Early execution trajectory can contain signal absent from the initial task. Re-routing may exploit this, but evaluation must include cost of acquiring the signal and must preserve Authority/work identity.

## Experiment discipline

Always compare with simple baselines: random, cheapest, strongest and static heuristic. During exploration persist propensities/context for off-policy evaluation; learned policy improvement must not be judged solely by the policy itself.

## OPEN

CandidateKey dimensions for local quantized/runtime configs; delayed route regret; OPE instrumentation; exploration policy; multi-objective constrained routing; causal attribution of routing choices.

---

## Continue this trail

**Previous:** [Protocols & Interoperability](../runtime/protocols-interoperability.md)  
**Next:** [Economics, Resources & Observability →](economics-resources-observability.md)  
**Implementation hypothesis:** [Adaptive Routing proposal](../../proposals/adaptive-routing.md)  
**Learning boundary:** [Adaptive Learning / Cross-Project Evolution](../context/adaptive-learning-cross-project-evolution.md)
