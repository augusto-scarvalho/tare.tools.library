# Canonical Lineage — technical proposal

[← Interoperability proposal](interoperability-learning-evolution.md) · [Research basis](../research/context/canonical-lineage-identity.md) · [Navigation](../NAVIGATION.md)

**Status:** PROPOSED / reconciliation-first.

## First seam: derived view, not new service

Build a read-only lineage projection from existing Project/Work/Workflow, RouteDecision/ExecutionBinding, Authority/Permit, ActionRequest/EffectReceipt, HarnessEvents, artifacts, OutcomeEvidence and Attribution.

## Golden queries

- Which governed work caused Effect E?
- Under which Project revision and policy/Authority epoch?
- Which execution attempt produced Artifact A?
- Which evaluator produced Evidence X?
- Which evidence changed ReputationSnapshot R?
- Which experiences produced Evolution Candidate C?
- Who evaluated/promoted/revoked it?

If these are answerable unambiguously, avoid a new lineage primitive. If not, record concrete ADR gaps.

## Temporal semantics

Preserve subject identity, revision, event/record time, relevant valid time/freshness, policy epoch and evidence-method version without forcing every bounded context into one mega-schema.

## BDD

Cross-boundary IDs round-trip; deletion/compaction of projections does not lose required lineage; delayed evidence attaches without rewriting history; observer/evaluator identity is reconstructible; trace order alone never becomes causal proof.

---

**Previous:** [Interoperability proposal](interoperability-learning-evolution.md) · **Next:** [Information Survival proposal →](information-survival.md) · **Validation case:** [FSV/MXC](../case-studies/validation/fsv-mxc-staged-candidate-enumeration.md)
