# tare.tools Research Documentation Standard — 2026-08-11

Status: **TARGET EDITORIAL STANDARD**. This governs presentation and research hygiene; it does **not** grant architectural authority to document claims.

## A. Scientific & Exploratory Research document

1. Numbered table of contents.
2. Problem definition, assumptions and objectives.
3. CURRENT × TARGET × PROPOSED × RESEARCH framing when tare.tools is discussed.
4. Reliable sources: peer-reviewed papers, established scientific literature, standards, official vendor engineering/docs, influential practitioners where appropriate, and mainline repositories.
5. Bleeding edge: recent preprints, mainline issues/PRs/discussions/experiments and well-provenanced emerging work.
6. Critical comparison of evidence quality; research is evidence, never automatic normative authority.
7. Consolidated proposal for the studied problem, including promising emerging experiments/evolutions.
8. Inline bibliographic references.
9. Bibliography at the end.
10. Explicit limitations, falsifiable hypotheses, experimental program and research pointers when useful.
11. HTML editorial delivery: fixed sidebar/index, editorial hero, strong hierarchy, callouts/cards, responsive tables, UTF-8, unique IDs and valid internal anchors.

## B. Technical Implementation Research companion

A separate document should be produced when the research yields implementable architecture. It must be marked **PROPOSED / IMPLEMENTATION RESEARCH** until reconciled with repo truth.

Required sections: bounded-context ownership; canonical equivalents before new primitives; CURRENT/TARGET gap; contracts and invariants; migration/compatibility/rollback; Windows + POSIX/CI requirements; evidence/gates; candidate BDD scenarios; dependencies and transverse impacts; explicit non-goals; Implementation Packet candidates.

It must not silently redesign ratified architecture during implementation.

## C. Historical migration rule

Historical documents are immutable evidence. Editorial migration may translate, re-render, add provenance banners and indexes, but must not silently update claims or pretend older TARGET/PROPOSED ideas became CURRENT. Scientific refresh is a separate derivative operation with its own date and sources.
