# Information Survival, Repository Boundaries & Reconstructive Assurance

[← Reliability](reliability-effect-reconciliation.md) · [Navigation](../../NAVIGATION.md) · [All Research](../README.md)

**Status:** RESEARCH · preservation edition of the 2026-08-12 deep study.

**Exact HTML/source status:** [Deep-Artifact Rehydration Gaps](../../catalog/REHYDRATION_GAPS.md) · [Provenance Index](../../sources/PROVENANCE_INDEX.md)

## Problem

“Keep everything in Git” and “clean the repository” are both inadequate. The real problem is: which information must survive, where, with what identity/retention/privacy properties, and which representations may be reconstructed?

## Reconstructive Closure

A Project revision has reconstructive closure when an operationally equivalent system can be materialized from declared seed/inputs without relying on hidden agent memory, a stale HOME or an opaque historical projection. This is deliberately weaker than universal bit-for-bit reproducibility.

Separate:

- reconstructible;
- deterministically reproducible;
- bit reproducible;
- independently reproducible.

## Information classes

1. durable facts/decisions/lineage needed for governance;
2. evidence payloads needed to support claims;
3. projections/materializations that should be rebuildable;
4. scratch/ephemera that may expire.

Physical store does not own semantic meaning. Git, DB, CAS/artifact store, research repo and observability systems have different homes.

## Temporal truth

Historical truth must not be overwritten by current belief. Preserve at least the conceptual difference between valid-at-world-time, recorded/known-at-time and current qualification/freshness.

## Research retained

Records management/appraisal, W3C PROV, reproducible builds, CAS/build systems, supply-chain attestations, OpenLineage, secure distribution and recent evidence-anchoring/reconstruction work all contribute. Technology landscapes remain mechanisms, not kernel semantics.

## Reconstructive Torture Lab

For representative Project archetypes, restore from a clean environment using only declared inputs; enumerate hidden dependencies, unreconstructible evidence, path/time/env leakage and divergence from golden queries.

## Connection to this repository

This V2 applies the same principle: Git preserves archaeology; HEAD preserves the best living study surface. Raw duplicates are removed only after semantic successors are mapped.

---

## Continue this trail

**Previous:** [Reliability](reliability-effect-reconciliation.md)  
**Next:** [Canonical Lineage & Identity →](../context/canonical-lineage-identity.md)  
**Implementation hypothesis:** [Information Survival proposal](../../proposals/information-survival.md)  
**Operational case:** [Agent Relay Q0](../../case-studies/evidence-exchange/agent-relay-q0.md) · [Curation V1 failure](../../case-studies/research-repository/semantic-curation-v1-failure.md)
