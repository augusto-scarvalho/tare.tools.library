# tare.tools Research Corpus

> **THIS REPOSITORY IS EVIDENCE, NOT ARCHITECTURAL AUTHORITY.**

This repository preserves tare.tools research, sources, experiments, archaeology, proposals, and historical versions.

In case of conflict, the canonical `tare-tools` repository, Git, source code, ratified architecture, ADRs, SPECs, BDDs, and gates take precedence.

## Start here

- **[Index of all documents and studies](catalog/DOCUMENT_INDEX.md)** — bilingual PT-BR | EN navigation by document and topic.
- **[Master catalog](catalog/MASTER_CATALOG.md)** — complete table with IDs, status, contexts, links, hashes, and translation coverage.
- **[Rehydration queue](catalog/REHYDRATION_QUEUE.md)** — exact-byte materialization backlog.
- **[Lineage reconciliation](catalog/LINEAGE_RECONCILIATION.md)** — metadata-confirmed order/sibling structure without unproven supersession.
- **[Expected identity assertions](catalog/IDENTITY_ASSERTIONS.md)** — SHA-256/size constraints reported by independent manifests.
- **[Source index](sources/SOURCE_INDEX.md)** — normalized external URLs from materialized originals.
- **[Translation status](catalog/TRANSLATION_STATUS.md)** — English translation coverage and review state.
- **[Translation queue](catalog/TRANSLATION_QUEUE.md)** — materialized sources still waiting for an English derivative.
- **[Translation QA](catalog/TRANSLATION_QA.md)** — structural fidelity/provenance checks for EN derivatives.
- **[Review status](catalog/REVIEW_STATUS.md)** — separates archival review, translation QA, and canonical architectural reconciliation.
- **[Translation policy](TRANSLATION_POLICY.md)** — source/derivative authority and fidelity rules.
- **[Chat translation workflow](CHAT_TRANSLATION_WORKFLOW.md)** — how review-time translation is registered without becoming architectural reconciliation.
- **[Chronology](catalog/CHRONOLOGY.md)** — temporal view.
- **[Version families](catalog/VERSION_FAMILIES.md)** — known/pending lineages.
- **[Research Graph](catalog/RESEARCH_GRAPH.json)** — structured relationships.
- **[Coverage](catalog/COVERAGE.md)** — corpus coverage.

## Authority rule

Research / experiment / archaeology / proposal artifacts **inform** architecture but do not ratify it. English translations are derived representations of the Portuguese historical originals and never gain additional authority by translation.

## Current seed status

The initial 11-document seed is **11/11 translated to English** and **11/11 passing structural fidelity QA**. Human translation review and canonical architecture reconciliation remain separate, explicit stages.

## Rehydration queue

File Library artifacts that have been discovered but whose exact bytes are not mounted locally are tracked in [catalog/REHYDRATION_QUEUE.md](catalog/REHYDRATION_QUEUE.md). Reference metadata is not treated as source content. Translation is blocked until exact source materialization unless the artifact is already natively English.

Current discovery projection: **60 reference-only artifacts**; **41** translation-blocked pending exact bytes; **19** native-English; **17** multi-item lineage families. Lineage ordering is review-only until content comparison establishes supersession. See [Library lineages](catalog/LIBRARY_LINEAGES.md) and [Rehydration coverage](catalog/REHYDRATION_COVERAGE.md). Historical Master Corpus counts are preserved as a reported baseline, not locally verified source bytes.
