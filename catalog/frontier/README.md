# Research Frontier Registry

> The Frontier Registry preserves the **boundary of unfinished knowledge** in `tare.tools.research`.

A Research Pointer is a research-continuity object: it records a question, adjacent branch, contradiction, experiment opportunity or bridge that may deserve later work. It is **not** a CURRENT gap, TARGET architecture, backlog item, ADR, SPEC, Implementation Packet, or authorization.

## Start here

- [Frontier Index](FRONTIER_INDEX.md)
- [Open Questions](OPEN_QUESTIONS.md)
- [Research Radar](RESEARCH_RADAR.md)
- [August 2026 Digest](RESEARCH_DIGEST-2026-08.md)
- [Possible overlap candidates](POSSIBLE_OVERLAPS.md)
- [Thematic clusters](THEMATIC_CLUSTERS.md)

## Canonical vs projections

- `RESEARCH_POINTERS.jsonl` — canonical simple registry representation.
- `RESEARCH_CLUSTERS.json` — canonical cluster membership metadata for this experimental layer.
- `pointers/*.md`, indexes, radar and digest — rebuildable human projections.

## Lifecycle

`DISCOVERED → NORMALIZED → TRIAGED → ACTIVE_RESEARCH → EVIDENCE_ACCUMULATING → SYNTHESIZED → FINDING_CANDIDATE`

Side exits: `DORMANT`, `DUPLICATE`, `SUBSUMED`, `REJECTED`, `INCONCLUSIVE`, `RESOLVED`, `OPEN`.

## Promotion boundary

A pointer may lead to a Research Question, hypothesis, study, evidence and finding. Only after that work exists may a separate promotion path consider `ADOPT / ADAPT / RETIRE / OPEN`, ADR/SPEC/BDD or an Implementation Packet.

## Harvesting policy

The v0.16 harvester imports only **explicit pointer surfaces**: the curated historical pointer crosswalk, the nine scientific-refresh pointer sections, and the supplemental Research Knowledge Substrate future-research section. It deliberately does not turn every occurrence of “unresolved”, “question”, or “future” in prose/logs into a pointer.
