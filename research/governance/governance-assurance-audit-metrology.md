# Governance Assurance & Audit — metrology preservation edition

**Status:** RESEARCH. Preserves the 38-section Governance/Audit study and related assurance lineage at a studyable level.

## Central thesis

Auditability is a system property. A fluent auditor is not sufficient: findings, evidence, instruments, independence, chain of custody and decision legitimacy must be separately inspectable.

## Separations

- Validation executes checks/oracles.
- Assurance evaluates evidence quality/sufficiency/residual risk.
- Audit challenges processes, controls, claims and history.
- Evidence/Provenance supports claims.
- Authority makes legitimate decisions.
- Observability supplies signals/projections.

## Finding lifecycle

An agent finding is a **hypothesis**, not proof. Prefer `suspected → supported → confirmed/refuted`, with confirmation proportional to materiality/risk.

## Audit subject/universe

Audit need not be triggered only by a code change. Subjects include Projects, workflows, controls, policies, runtimes, datasets, evidence producers and long-lived processes. Preserve three clocks: subject change, evidence freshness and audit cadence.

## Risk-based audit

Combine criticality, uncertainty, novelty, evidence freshness, irreversibility, systemic exposure and cost. Deterministic population methods are preferable when cheap; sampling needs explicit population identity/seed/strata/exceptions.

## Metrology

Auditor/judge/test suite/scanner/human review are measurement instruments. Agreement is not validity. Maintain calibration/perturbation sets, sensitivity/specificity where meaningful, false-positive traps, delayed misses, drift and replacement studies.

## EvidenceFamily

Vendor count is not epistemic independence. Correlated prompts, data, method, environment or common failure mode may mean nominally different reviewers belong to the same EvidenceFamily.

## Preserved negative evidence

- manual `VERDICT.md` cannot mint mechanized proof;
- static/config parity did not prove runtime-loaded/enforced/effective capability;
- passing test count does not establish discriminative power;
- candidate-controlled judge/proof path is not independent assurance.

## Research program

Process-mining audits; seeded auditor qualification; random re-audit to measure misses; method-correlation studies; control-effectiveness retirement experiments; meta-audit of judge drift and override patterns.
