# tare.tools.research — Corpus Compaction Record — 2026-08-12

**Scope:** repository maintenance on `agent/research-corpus-compaction-1`  
**Architectural status:** not a TARGET/CURRENT architecture decision  
**Base commit:** `7ad1a71ebbad99e69bd6ba97b2ed29d78faf08de`  
**Base tree:** `13d746c2ec6cfef73a5c0baa97b89818b0ade67b`  
**Rollback / historical anchor:** parent commit above; `bootstrap-v0.19.0` remains an additional frozen baseline.

## 1. Problem

The live tree mixed four different things: immutable evidence, historical exact snapshots, semantically valuable research/refreshes, and large reconstructible presentation projections. This made navigation and repository size worse without increasing epistemic strength.

The repository's own `AGENTS.md` forbids deleting historical originals merely to make the corpus cleaner. Therefore compaction cannot mean deleting the 93 exact historical artifacts or other primary evidence.

## 2. Decision

Apply **negative archive for derivatives, append-only for evidence**.

### RETAIN — evidence / source identity

- `corpus/original/`
- `corpus/canonical-snapshot/`
- `corpus/source-bundles/`
- `corpus/manifests/`
- `canonical-references/`
- source/library identity metadata and archaeology required for provenance

### RETAIN — semantically valuable research

- `refresh-editions/2026-08-11/`
- newer research ingestions
- findings, proposals and experiments with independent semantic content
- Research Frontier and relation/lineage data
- tools, schemas and tests required to reconstruct projections

### RETIRE FROM LIVE TREE — reconstructible projection bulk

- `editorial-editions/2026-08-05-private-github-snapshot/`
  - 93 source-language editorial HTMLs
  - 93 English editorial HTMLs
- `catalog/EDITORIAL_BILINGUAL_INDEX.md`
- `catalog/EDITORIAL_QA.md`
- `catalog/EDITORIAL_QA.json`

The 186 HTMLs were derivatives of exact historical sources; they were not a scientific refresh and did not mint architectural authority.

## 3. Preserve before retire

Two unique metadocuments from the editorial layer were retained unchanged beside the Scientific Refresh:

- `refresh-editions/2026-08-11/EDITORIAL_STANDARD.md`
- `refresh-editions/2026-08-11/EDITORIAL_MIGRATION_GAP_REPORT.md`

`RESEARCH_DOCUMENT_STANDARD.md` already existed in the refresh tree with the same content-addressed blob, so no duplicate was needed.

## 4. Consolidated reading surface

The 2026-08-11 Scientific Refresh is now the preferred historical reading surface. It maps all **93** historical artifacts into **9** scientific lineages and contains **20** HTML research documents (18 lineage documents plus 2 cross-lineage syntheses), while preserving a full crosswalk to historical evidence.

This is a reading/curation decision, not an assertion that the refresh supersedes source evidence or canonical architecture.

## 5. Recovery

No Git history was rewritten. Removed projections can be recovered exactly from the parent commit, for example:

```bash
git show 7ad1a71ebbad99e69bd6ba97b2ed29d78faf08de:editorial-editions/2026-08-05-private-github-snapshot/en/RESEARCH.en.html
```

or by checking out the pre-compaction commit/tag into an independent worktree.

## 6. Rebuild policy

`editorial-editions/` is now ignored by default. Rendering tooling and dependencies remain tracked so editorial projections can be generated on demand. If a regenerated edition gains non-reconstructible semantic content, that content must be promoted into a proper research/findings/review artifact rather than hidden inside presentation output.

## 7. ADOPT / ADAPT / RETIRE / OPEN

- **ADOPT:** Scientific Refresh as the compact historical research reading surface.
- **ADAPT:** editorial renderer from committed corpus producer to on-demand projection generator.
- **RETIRE:** committed 186-file bilingual editorial projection corpus and its generated index/QA views.
- **OPEN:** whether large immutable source bundles should later move behind a qualified content-addressed artifact backend. Do not move them in this compaction because they are evidence and the current repository policy is append-only.

## 8. Safety / rollback invariants

- `main` is not modified by this packet.
- historical originals are not modified or deleted.
- source bundles are not modified or deleted.
- no architecture proposal is promoted.
- no Git history is rewritten.
- rollback is a normal branch reset/revert to the parent commit.
