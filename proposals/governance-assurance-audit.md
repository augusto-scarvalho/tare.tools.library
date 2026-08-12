# Governance Assurance & Audit — technical proposal

[← Reliability proposal](reliability-effect-reconciliation.md) · [Research basis](../research/governance/governance-assurance-audit-metrology.md) · [Navigation](../NAVIGATION.md)

**Status:** PROPOSED. Audit-specific roles are not automatically new primitives.

## Candidate roles

AuditSubjectRef, AuditEngagement/Profile, FindingClaim, method/evaluator qualification snapshot, sampling frame, control-effectiveness observation and meta-audit result. Attempt composition over Project/Candidate/HarnessEvent/OutcomeEvidence/EvidenceFamily/Authority first.

## BDD themes preserved

- agent finding is not proof;
- deterministic process audit can detect effect-before-Permit;
- manual verdict cannot mint mechanized proof;
- three vendors may remain one EvidenceFamily;
- method/environment diversity can matter more than vendor count;
- Audit may be zero-LLM or human-led;
- external scanner output is evidence input, not automatic CONFIRMED finding;
- auditor candidate in shadow has zero Authority;
- candidate cannot control promotion tests;
- evidence loses current strength if its method is invalidated without deleting history;
- random re-audit estimates false negatives;
- policy engine cannot mint tare Permit;
- expensive ineffective control can be recommended for retirement.

## Adapters, not foundations

PM4Py/process mining, OSCAL/trestle, OPA/Cedar/OpenFGA, OTel, W3C PROV, in-toto/SLSA/Sigstore, CodeQL/Semgrep/Trivy/OSV, OpenLineage and rollout/experiment systems should remain qualified mechanisms/projections.

---

**Previous:** [Reliability proposal](reliability-effect-reconciliation.md) · **Next:** [Interoperability / Learning / Evolution →](interoperability-learning-evolution.md) · **Test evidence:** [Scenario Gates](../research/assurance/test-engineering-scenario-gates.md)
