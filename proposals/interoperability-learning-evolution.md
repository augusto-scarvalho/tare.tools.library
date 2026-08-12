# Interoperability, Learning & Evolution — technical proposal

**Status:** PROPOSED.

## Boundary model

Task/Workflow required semantics → Authority/eligibility → Qualification → RouteDecision → ExecutionBinding → vendor-local / harness-owned / vendor-remote / capability-protocol binding → effect/events → evidence → attribution.

## Anti-duplication rule

Before new `BoundaryContract`, `SemanticFidelity` or `BoundaryFingerprint`, test composition of ExecutionBinding + QualificationSnapshot + Authority/Permit refs + adapter/protocol/version metadata.

## BDD themes

Semantic downgrade must be explicit; boundary cannot amplify delegated authority; stale qualification blocks or degrades eligibility according to policy; MCP discovery does not auto-admit Capability; A2A peer does not inherit local Authority; ambiguous remote effect reconciles before retry; tare↔tare version mismatch produces qualified compatibility result; boundary experience remains Project-scoped until transportability evidence exists; agent feedback cannot promote its own adaptation.

## Migration

Instrumentation/read-only normalization first; semantic fidelity/qualification in shadow; one adapter vertical slice; only later allow learned boundary preferences or adaptive capability materialization.
