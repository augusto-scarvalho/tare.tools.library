# Research Lineage & Influence Relationship Standard

Status: **PROPOSED RESEARCH-METADATA CONTRACT — v1.0 (2026-08-11)**. It governs research provenance/relationship metadata only; it does not grant architectural authority.

## 1. Why two graphs are necessary

`tare.tools.research` must distinguish **lineage** from **influence/interference**. Lineage answers *what was derived from, refreshed from, translated from, or used as evidence for what*. Influence answers *how one body of work changes the interpretation, constraints, confidence, scope, or design of another*.

A citation is observed. An influence classification is often curated. Neither by itself proves causation.

## 2. Relationship families

### Lineage / provenance
- `TRANSLATION_OF` — language derivative, no scientific refresh implied.
- `EDITORIAL_DERIVATIVE_OF` — rendering/layout derivative.
- `REFRESHED_INTO` — historical scientific lineage absorbed into a dated refresh.
- `IMPLEMENTATION_HISTORY_FOR` — historical implementation proposal/plan informing a lineage.
- `ITERATION_EVIDENCE_FOR` — research round/monitor/backlog supporting a lineage.
- `OPERATIONAL_EVIDENCE_FOR` — logs/forensics/measurements supporting or challenging a lineage.
- `OPERATIONALIZED_BY` — scientific refresh translated into a separate PROPOSED technical delta.
- `SUPERSEDES` — use only when explicit evidence proves normative/version succession.

### Influence / interference
- `SUPPORTS` — strengthens a claim or design hypothesis.
- `CHALLENGES` / `FALSIFIES` — weakens or directly falsifies a claim.
- `CONSTRAINS` — narrows allowed design/interpretation without necessarily disagreeing.
- `RECENTERS` — preserves much of the content but changes architectural ownership/framing.
- `REFINES` — adds precision while retaining the earlier thesis.
- `OPERATIONALIZES` — translates a conceptual result into contracts/experiments.
- `CALIBRATES` / `QUALIFIES` — changes how evidence or outcomes may legitimately be interpreted.
- `PROJECTS_*` / `STEERS` — directional cross-context interaction without ownership transfer.

### Source relations
- `CITED_BY` is an observed edge from an external source to a document.
- `CO_CITED_WITH` means two sources occur in the same documents; it **does not** prove intellectual lineage.
- `OFFICIAL_SPECIFICATION_VERSION_FAMILY` can be curated when official version/representation identity is explicit.
- `POSSIBLE_SAME_WORK_OR_VERSION_FAMILY` is a discovery candidate and must be verified before becoming lineage.

## 3. Mandatory edge metadata

Every non-trivial relationship should carry: `from`, `to`, `relation`, `basis`, `confidence`, optional `polarity`, `weight`, `effect`, `description`, and `evidence_refs`.

`basis=observed_*` means mechanically grounded. `basis=curated` means an explicit research interpretation. `basis=inferred` must never be silently upgraded to fact.

## 4. Authority rule

Relationship metadata never upgrades `RESEARCH`, `PROPOSED`, historical evidence or an external paper into CURRENT/TARGET authority. Git, code, canonical Architecture, ADR, SPEC, BDD and gates remain stronger sources of truth.
