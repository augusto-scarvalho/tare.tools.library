# Capability, Sandbox, Resources & Isolation

[← Vendor Runtime Landscape](vendor-cli-runtime-landscape.md) · [Navigation](../../NAVIGATION.md) · [All Research](../README.md)

**Status:** RESEARCH / PROPOSED boundary refinement.

**HTML/source edition:** [Runtime / Reliability / Sandbox scientific refresh](../../bridge-editions/2026-08-11/runtime-reliability-sandbox-scientific-refresh.html)

## Capability/Effect principle

Models propose actions. Authority/policy authorize. Capability infrastructure executes. Receipts prove.

Filesystem, shell, Git, browser, DB, MCP, artifacts and external services should converge semantically without requiring one mechanism.

## Sandbox

Sandbox/containers/process supervisors are isolation mechanisms behind the capability/workspace boundary. A sandbox does not grant Authority and a configuration label does not prove confinement.

## Workspace

WorkspaceLease is the conceptual bridge between identity/ownership, allowed roots and lifetime. Stale owners and commit races connect directly to Reliability/fencing.

## Resource governance

Tokens, API quotas, latency, CPU, GPU, RAM/VRAM, disk, network and human attention are competing resources. Resource policy can constrain eligible execution, but resource availability does not grant authority.

## Local-first research

Consumer GPU constraints expose useful tradeoffs that cloud-only architecture can hide: memory headroom, quantization identity, cache semantics, local durable state and Windows path/process behavior.

## Qualification

A backend needs semantic conformance, failure/degraded-mode tests, version drift, offline behavior, Windows/POSIX matrix, trust boundary, replaceability and evidence of actual enforcement/effect.

## OPEN

Filesystem confinement proof; secret materialization; portable capability components/WASM; container backend matrix; GPU/resource scheduling; remote workspace lease/fencing.

---

## Continue this trail

**Previous:** [Vendor Runtime Landscape](vendor-cli-runtime-landscape.md)  
**Next:** [Protocols & Interoperability →](protocols-interoperability.md)  
**Implementation hypothesis:** [Resource / Sandbox / Assurance proposal](../../proposals/resource-sandbox-assurance.md)  
**Reliability coupling:** [Effect Reconciliation](../work/reliability-effect-reconciliation.md)
