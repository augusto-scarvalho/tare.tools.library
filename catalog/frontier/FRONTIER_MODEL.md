# Research Frontier Model — v0.16 Experimental

> **RESEARCH METADATA / OPERATIONAL CONVENTION — NOT AGENT OS AUTHORITY.**

## Purpose

The Research Frontier preserves unfinished intellectual work discovered across chats, documents, experiments and scientific refreshes without turning every interesting idea into roadmap, architecture or implementation work.

## Core distinctions

`Pointer != Research Question != Hypothesis != Study != Finding != Gap != Task`.

A pointer is the lightest continuity object. It preserves *why this branch exists*, where it came from, which lineages it touches, and how it may be reopened.

## Lifecycle

`DISCOVERED → NORMALIZED → TRIAGED → ACTIVE_RESEARCH → EVIDENCE_ACCUMULATING → SYNTHESIZED → FINDING_CANDIDATE`

Side states: `DORMANT`, `DUPLICATE`, `SUBSUMED`, `REJECTED`, `INCONCLUSIVE`, `RESOLVED`, `OPEN`.

No transition in this lifecycle creates TARGET architecture or implementation authority.

## Pointer types

- `research_branch` — scientific/technical question worth deeper study.
- `bridge` — connects otherwise separate disciplines or lineages.
- `experiment_pointer` — points to a concrete qualification/benchmark/test opportunity.
- future extensions may include `contradiction`, `external_signal`, `architectural_question`, and `negative_evidence_pointer` after observed examples justify them.

## Canonical representation and projections

- `RESEARCH_POINTERS.jsonl` is the simple canonical registry for the experimental Frontier layer.
- `RESEARCH_CLUSTERS.json` stores cluster membership.
- Markdown pointer pages, lineage views, radar, digest, HTML dashboard and capsule sections are rebuildable projections.

## Harvesting

Only explicit pointer surfaces are harvested automatically in v0.16:

1. `catalog/FUTURE_RESEARCH_POINTERS.md`;
2. the explicit Research Pointers sections of the nine scientific refresh lineages;
3. the supplemental Research Knowledge Substrate future-research section.

Generic words such as “unresolved”, “future” or “question” inside prose, logs or forensic evidence are deliberately not harvested.

## Deduplication

Exact normalized titles may share one pointer identity while retaining every origin. Lexical similarity only produces `POSSIBLE_OVERLAP_CANDIDATE`; it never merges pointers or claims semantic equivalence.

## Clustering

Clusters are navigational research-program views. They never replace pointer identity and never become bounded contexts automatically.

## Research Radar

Radar buckets are generated attention projections (`WATCH`, `EXPLORE`, `INVESTIGATE`, `EXPERIMENT`, `SYNTHESIZE`, `READY_FOR_RECONCILIATION`). They are explicitly **not roadmap priority**.

## Reopening contract

When a pointer is reopened:

1. recover origins and relevant lineages;
2. establish current canonical architecture epoch/repo truth;
3. classify historical ideas as `ADOPT / ADAPT / RETIRE / OPEN`;
4. refresh external evidence separately;
5. formulate RQs/hypotheses/experiments;
6. synthesize findings;
7. only then cross the separate Research → Architecture promotion boundary if warranted.

## Organic loop

`Corpus → Graph → Frontier → Research → Evidence/Findings → Graph → Frontier`.

This lets the corpus generate its own research agenda signals while preserving human/governed promotion boundaries.
