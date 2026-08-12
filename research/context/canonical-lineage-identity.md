# Canonical Lineage & Compositional Identity

**Status:** RESEARCH / PROPOSED synthesis; no Identity Plane is ratified.

## Problem

Project → Workflow → Routing → Runtime → Effect → Evidence → Learning can fragment semantically if each subsystem invents IDs, actor labels and lifecycle states.

## Thesis

Prefer **lineage-preserving** architecture over identity-centric architecture. Identity emerges compositionally across owners rather than through a monolithic IdentityService.

## Distinctions

- Subject identity ≠ Subject revision.
- Durable Work identity ≠ execution attempt identity.
- Actor ≠ principal ≠ model ≠ workload/runtime.
- logical effect ≠ attempt.
- provenance ≠ Evidence ≠ causal attribution.
- trace chronology ≠ proof of causation.
- security identity/authentication ≠ tare decision Authority.

## Golden lineage questions

Which governed work caused Effect E? Under which Authority/policy epoch? Which attempt produced Artifact A? Which Project revision was acted upon? Which evaluator produced Evidence X? Which evidence changed ReputationSnapshot R? Which experiences produced Evolution Candidate C and who evaluated/promoted it?

Build a read-only derived lineage view from existing canonical refs/events first. Only ambiguous golden queries justify new primitives.

## Temporal semantics

Delayed evidence and policy/runtime revisions require historical identity plus freshness/qualification. Do not rewrite past facts when current assessment changes.

## Learning

Canonical lineage enables comparable Experience episodes, but correlation is not Attribution. Causal claims need stronger intervention/contrastive/counterfactual support.
