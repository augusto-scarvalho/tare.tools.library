# Current Project Corpus Curation Map — 2026-08-11

> Project documents below are conceptual/evidence anchors for the refresh. They retain their original status. They do not become CURRENT merely by being cited here. Repo Git / code / canonical architecture / ADR / SPEC / BDD / gates remain stronger sources of truth.

| Project corpus lineage | Status in this refresh | Primary refreshed lineages | Curated use |
|---|---|---|---|
| Harness → Agent Operating System scientific architecture (2026-08-09) | TARGET/RESEARCH anchor | all, especially Agent OS foundations | North Star, bounded contexts, user-space OS framing, migration strategy |
| Agent OS SDD + BDD (2026-08-09) | TARGET anchor | all implementation deltas | canonical vocabulary and migration constraints |
| Workflow as Governed Work (2026-08-11) | RESEARCH | workflow; context; UX | replaces agent-centric workflow framing with heterogeneous governed work |
| Reliability Semantics & Effect Reconciliation (2026-08-10) | RESEARCH | runtime; workflow; interoperability | ambiguous effects, reconciliation, authority freshness, qualified outcomes |
| Governance Assurance & Audit (2026-08-10) | RESEARCH | assurance; methodology | evidence families, audit independence, evaluator metrology, governance lifecycle |
| Assurance & Evolution (2026-08-09) | RESEARCH | assurance; methodology; routing | evidence sufficiency, deterministic reuse, held-outs, controlled evolution |
| Interoperability, Learning & Evolution (2026-08-10) | RESEARCH | interoperability; runtime; routing | qualified boundary semantics, scoped learning, protocol pluralism |
| Runtime/Vendors + TUI/REPL archaeology (2026-08-09) | HISTORICAL/RESEARCH | runtime; interoperability; UX | runtime ownership, adapters, Experience projections, false-green parity lesson |
| Project Admission & Adoption (2026-08-09) | RESEARCH/TARGET candidate | Agent OS; methodology; context | Proof of Understanding before write eligibility; project truth vs tare governance |
| MXC-Q1 / FSV validation handoff (2026-08-10) | CURRENT EVIDENCE for a narrow implementation line | runtime; assurance; methodology | candidate/judge separation, staged candidate identity, strict-proof blockers |

## Curation rules

1. Preserve the original conclusion and date of every cited project document.
2. If a newer project document supersedes the conceptual framing, record that as ADAPT/RETIRE in the refresh; do not edit history.
3. If a project document conflicts with current repo truth, repo truth wins and the document becomes historical evidence of architectural evolution.
4. Research pointers do not imply canonical gaps until a read-only reconciliation against current source confirms them.
