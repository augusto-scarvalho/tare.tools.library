# Assurance, Testing Science & Governed Evolution

[← Governance Assurance & Audit](governance-assurance-audit-metrology.md) · [Navigation](../../NAVIGATION.md) · [All Research](../README.md)

**Status:** RESEARCH / PROPOSED integration.

**HTML/source context:** [Assurance / Governance / Quality scientific refresh](../../bridge-editions/2026-08-11/assurance-governance-quality-scientific-refresh.html)

## Problem

A gate that passes can still be a weak instrument. A test suite may overfit visible behavior, miss semantic faults, or be controlled by the candidate it judges. Evolution amplifies these risks because the system can learn to optimize the evaluator rather than the real objective.

## Claim-centered assurance

```text
Requirement / risk
 → claim
 → oracle / evidence producer
 → EvidenceFamily
 → validity / freshness / independence
 → sufficiency decision
 → Authority
```

Coverage and check count are secondary to construct validity and discriminative power. Mutation testing/meta-assurance are useful because they test whether the tests can reject known faults.

## Deterministic evidence reuse

Evidence may be reused only when subject identity, relevant dependencies/environment and oracle/version remain sufficiently pinned. Freshness and strength are separate: an old valid result may become stale without becoming historically false.

## Evolution control

Learning loop must not promote itself. Candidates progress through replay/holdout/shadow/canary/rollback according to risk. Protected/rotating evaluation helps resist Goodhart/reward hacking. Evaluator changes are themselves measurement-system changes.

## Economics

Optimize time/cost-to-trust, not raw test count. Dynamic scheduling, impact graphs and Value of Information should decide which evidence is worth acquiring next.

## OPEN

Assurance-case projection; claim graph; evaluator qualification; control retirement; community/federated evaluation; delayed OutcomeEvidence; causal attribution from outcomes back to candidate changes.

---

## Continue this trail

**Previous:** [Governance Assurance & Audit](governance-assurance-audit-metrology.md)  
**Next:** [Test Engineering / Scenario Gates →](../assurance/test-engineering-scenario-gates.md)  
**Related learning boundary:** [Adaptive Learning / Evolution](../context/adaptive-learning-cross-project-evolution.md)  
**Current findings:** [Curated Findings](../../findings/CURATED_FINDINGS.md)
