# Assurance Topology — Regression Treasury → Evidence Acquisition

**Status:** `RESEARCH / ACTIVE / PEER-REVIEW DRAFT`

**Cutoff date:** 2026-08-13

**Primary bounded context:** Validation / Assurance

**Related:** Evidence / Provenance; Observability / Economics / Resources; Project / Workspace

**Authority:** research; it does not ratify TARGET and does not change the canonical repository.

## Problem

The operational case BASELINE-CI / CI-REGRESSION-01 revealed that the historical scenario treasury is being used at the same time as PR regression suite, conformance, platform qualification, NOT_CURRENT evidence, reliability/fault injection and system/integration assurance. The problem is not "having too many tests": it is a topology that treats semantically different evidence producers as a single blocking aggregate.

The hypothesis of the dossier is to preserve the treasury as an executable specification of the stable incumbent and to evolve, by retrofit, toward **Evidence Acquisition**: claims and mandatory Evidence Families determine the assurance floor; candidate impact, platform and cost determine when/where to produce the evidence. Model/router/reputation can never lower the deterministic floor.

## Dossier

1. [Empirical evidence and diagnosis](01-empirical-evidence.md)
2. [Proposed architecture and migration](02-proposed-assurance-topology.md)
3. [Experimental program, falsifiers and peer review](03-experiment-peer-review.md)

## Research questions

- RQ1 — does the current treasury mix evidence classes to the point of increasing cost/false blocking without proportional assurance strength?
- RQ2 — does classifying evidence producers by claim/family/layer/platform/hermeticity/determinism reduce time-to-trust while preserving failure detection?
- RQ3 — can a deterministic GatePlan based on risk/policy + impact + mandatory Evidence Families operate in shadow without transferring Authority to the router/model?
- RQ4 — which producers belong to PR, promotion, qualification, reliability/scheduled and release?
- RQ5 — does the change reduce corrective burden and fixture-aging, or does it only move failures to later?

## North Star mapping

```text
deterministic Authority/Assurance policy
        ↓ mandatory evidence floor
candidate + impact + runtime/platform facts
        ↓
reconstructable GatePlan
        ↓
evidence producers
        ↓
OutcomeEvidence / sufficiency
        ↓
authorized decision
```

The economic goal is not to minimize the number of tests. It is to **minimize time/cost until there is sufficient evidence for an authorized decision**, preserving fail-closed behavior, cross-platform obligations, negative evidence and rollback.

## Epistemological state

`PEER_REVIEWABLE_DESIGN_DRAFT_WITH_ACTIVE_EMPIRICAL_CASE`

Do not yet claim that selective testing is production-safe in tare.tools, that lane splitting reduces regressions, that CI-REGRESSION-01 is already settled while its corrective is running, or that green CI implies strict proof.
