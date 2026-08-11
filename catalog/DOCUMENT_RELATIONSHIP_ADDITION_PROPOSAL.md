# Proposal — Add Research Lineage, Influence & Provenance to Every Research Document

> **Decision — 2026-08-11:** Accepted by the project owner **for refinement**. The seven-part human-readable section is approved as the direction of travel; machine-readable fields, schemas and automation remain **PROPOSED** until piloted and reconciled.


Status: **PROPOSED EDITORIAL / RESEARCH-METADATA DELTA — 2026-08-11**.

## 1. Proposed new mandatory section

Every future Scientific Research and Technical Implementation Research document should include a **Research Lineage, Influence & Provenance** section. It should be generated from the central graph where possible, not maintained independently in prose.

Minimum content:

1. **Historical ancestors** — byte-preserved artifacts or earlier studies absorbed by this work.
2. **Direct derivatives** — translation/editorial/scientific-refresh relationships.
3. **Internal corpus anchors** — North Star, newer research lineages, current implementation evidence.
4. **Cross-lineage interference** — `SUPPORTS`, `CONSTRAINS`, `RECENTERS`, `CHALLENGES`, `CALIBRATES`, etc., with basis/confidence.
5. **External source families** — papers/specs/repos materially used by the document; distinguish observed citation from verified source lineage.
6. **Downstream influence** — technical delta, ADR candidate, experiment, implementation packet or future research pointer.
7. **Authority note** — research relationships never mint CURRENT/TARGET authority.

## 2. Proposed compact metadata capsule

```yaml
research_relationships:
  lineage_id: workflow-procedural
  historical_ancestors:
    - dynamic-workflows.md
  refresh_of:
    - historical:dynamic-workflows
  influenced_by:
    - relation: CONSTRAINS
      target: runtime-reliability-sandbox
      basis: curated
      confidence: high
  external_sources:
    - source: arxiv:2608.02680
      relation: SUPPORTS
      claim_scope: procedural-compilation
  downstream:
    - implementation_delta: workflow-procedural-implementation-research-delta-2026-08-11
```

## 3. Placement

For scientific documents, place this section **after North Star reconciliation and before evidence synthesis**, so the reader knows the document's ancestry before interpreting claims. For technical companions, place it after bounded-context ownership / authority note.

## 4. Generated vs authored content

The relationship capsule should be generated from `catalog/RESEARCH_RELATION_GRAPH.json`. Authors may propose new edges, but a curation step must classify them as observed, curated or inferred. This avoids divergent relationship claims across documents.

## 5. Negative evidence

A document that invalidates an earlier hypothesis must add a `CHALLENGES` or `FALSIFIES` edge rather than silently rewriting or removing the earlier work.

## 6. Promotion boundary

No graph edge can promote research into canonical architecture. Promotion remains a separate path through findings → ADR/architecture/SPEC/BDD/gates.
