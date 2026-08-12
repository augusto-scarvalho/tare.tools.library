# Protocols & Interoperability — boundary semantics preservation edition

**Status:** RESEARCH / strong architectural direction.

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
