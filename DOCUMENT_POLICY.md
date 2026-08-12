# Document Policy — Semantic Curation Epoch 2026-08-12

## 1. Goal

Keep `tare.tools.research` useful as a living scientific/engineering library rather than a warehouse of every intermediate artifact.

## 2. Admission classes

- **LIVE STUDY** — current best synthesis of a research problem.
- **EXPERIMENT** — empirical record whose observations, protocol or negative evidence deserve direct access.
- **FINDING** — compact cross-study conclusion with provenance and status.
- **FRONTIER** — unresolved scientific question or experiment opportunity.
- **PROPOSED** — implementation/architecture proposal only when it contains genuinely problem-specific contracts; boilerplate companions are not admitted.
- **HISTORY ONLY** — superseded/intermediate material recoverable through Git.

## 3. What does not qualify by itself

Recency, file size, bibliography count, HTML formatting, translation, passing a structural template, number of reviewers, or being produced by an LLM.

## 4. Supersession

When a living study absorbs older material, record the absorbed lineage in `catalog/CURATION_LEDGER.md`. Do not keep both generations in HEAD unless the older artifact remains independently useful.

## 5. Evidence and provenance

Provenance must survive. Raw bytes need not remain in the current tree when Git history/content hashes provide reliable recovery. Evidence required for an active experiment may remain directly accessible.

## 6. Promotion boundary

Research publication is not architecture ratification. `CURRENT` and `TARGET` remain governed by the canonical tare.tools repository and its authority/evidence chain.
