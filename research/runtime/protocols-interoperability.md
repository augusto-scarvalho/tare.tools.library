# Protocols & Interoperability — boundary semantics preservation edition

[← Capability / Sandbox / Resources](capability-sandbox-resources.md) · [Navigation](../../NAVIGATION.md) · [All Research](../README.md)

**Status:** RESEARCH / strong architectural direction.

**HTML/source edition:** [Interoperability / Protocols scientific refresh — 2026-08-11](../../bridge-editions/2026-08-11/interoperability-protocols-scientific-refresh.html)

## Thesis

Interoperability means preserving — or explicitly declaring the loss of — identity, authority, causality, lifecycle, artifacts, effects and evidence when canonical objects cross a boundary.

Protocol nouns should not automatically become kernel nouns.

## Placement

- MCP: external capability/resource protocol/backend; not internal bus or Authority.
- A2A: useful for independent/opaque remote agents; not tare internal runtime model.
- CLI/ACP-like surfaces: vendor-local transport/runtime adapters.
- HTTP inference: ModelProviderAdapter input for harness-owned agents.
- OTel/OpenLineage: projections/sensors; not canonical EffectReceipt/Evidence.

## Smallest sufficient view

Compile only the context, capability schemas, authority ceiling, artifact refs and evidence metadata required at a boundary. This reduces context bloat, data leakage and authority leakage.

## ExecutionBinding hypothesis

Before inventing `BoundaryContract`, `InteropProfile` or `SemanticFidelity` primitives, test whether ExecutionBinding + QualificationSnapshot + Authority/Permit refs + adapter/version metadata already express the need.

## Learning from boundaries

Bindings produce evidence about semantic loss, reliability, token overhead, capability usefulness and reconciliation cost. Such experience may update qualification/routing only after attribution and evidence eligibility.

## OPEN

Cross-version tare↔tare profile; semantic-fidelity metrics; federation trust; artifact transfer; downgrade semantics; protocol negotiation and temporal compatibility.

---

## Continue this trail

**Previous:** [Capability / Sandbox / Resources](capability-sandbox-resources.md)  
**Next:** [Adaptive Routing / Reputation →](../routing/adaptive-routing-reputation.md)  
**Implementation hypothesis:** [Interoperability / Learning / Evolution proposal](../../proposals/interoperability-learning-evolution.md)  
**Source/evidence index:** [Study Editions](../../sources/README.md)
