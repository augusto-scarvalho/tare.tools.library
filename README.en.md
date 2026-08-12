# tare.tools Research Corpus

> **THIS REPOSITORY IS RESEARCH/EVIDENCE MEMORY, NOT ARCHITECTURAL AUTHORITY.**

When sources conflict, the canonical `tare-tools` repository, Git, code, ratified architecture, ADRs, SPECs, BDDs and gates prevail.

## Start here

1. **[Scientific Refresh 2026-08-11](refresh-editions/2026-08-11/README.md)** — compact reading surface for the historical corpus: 93 artifacts reconciled into 9 lineages with scientific refreshes and implementation-research deltas.
2. **[Research Frontier](frontier/README.md)** — research continuity; it is neither a backlog nor implementation authority.
3. **[Document index](catalog/DOCUMENT_INDEX.md)** and **[master catalog](catalog/MASTER_CATALOG.md)** — navigation and document identity.
4. **[Canonical Snapshot Research Index](catalog/CANONICAL_SNAPSHOT_RESEARCH_INDEX.md)** — index of preserved historical bytes from the 2026-08-05 snapshot.
5. **[Research lineage & influence](catalog/RESEARCH_LINEAGE_AND_INFLUENCE.md)** — relationships between studies and lineages.

## Three classes that must not be conflated

### 1. Evidence / originals — append-only

Primary and historical bytes remain preserved, especially `corpus/original/`, `corpus/canonical-snapshot/`, `corpus/source-bundles/`, `corpus/manifests/`, and `canonical-references/`. They are not rewritten or deleted merely to make the corpus cleaner.

### 2. Research synthesis / refresh — tracked

Scientific syntheses and technical deltas stay versioned when they carry interpretation, reconciliation, `ADOPT / ADAPT / RETIRE / OPEN` decisions, provenance, or new findings. The primary consolidated historical surface is `refresh-editions/2026-08-11/`.

### 3. Presentation projections — reconstructible

Editorial HTML that only reformats or translates already-preserved bytes is a **reconstructible build artifact**. It may be generated locally by repository tooling without being committed to the live tree.

The former `editorial-editions/2026-08-05-private-github-snapshot/` tree was removed on the compaction branch for this reason. Its bytes remain recoverable from Git history; the editorial standard and migration-gap report were preserved next to the Scientific Refresh.

## Operational structure

- `research/` — thematic indexes/projections.
- `refresh-editions/` — consolidated research and scientific refreshes.
- `findings/`, `proposals/`, `experiments/`, `archaeology/` — research lifecycle artifacts.
- `sources/`, `corpus/`, `canonical-references/` — evidence, provenance and source identity.
- `frontier/` — Research Pointers and scientific continuity.
- `catalog/` — identity, lineage, indexes, provenance and maintenance records.
- `schemas/`, `tools/`, `tests/` — deterministic contracts and automation.

## Authority rule

`RESEARCH`, `EXPERIMENTAL`, `HISTORICAL`, and `PROPOSED` inform; they do not ratify architecture. `TARGET` and `CURRENT` belong to the canonical `tare-tools` flow and supporting evidence.

## Compaction

The 2026-08-12 rule is **negative archive for derivatives, append-only for evidence**: do not create a duplicate `/archive`; use Git history to recover removed projections while keeping irreversible evidence, semantically valuable research, and reconstruction machinery live.

See [`catalog/CORPUS_COMPACTION_2026-08-12.md`](catalog/CORPUS_COMPACTION_2026-08-12.md).
