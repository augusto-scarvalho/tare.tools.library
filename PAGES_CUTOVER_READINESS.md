# Pages Canary and Cutover Readiness

Status: migration contract for `tare.tools.research`. This document does not grant production authority.

## CURRENT

The stable public Pages reader remains the incumbent identified by `site/INCUMBENT_PROFILE.json`. The SIGNAL publisher is a derived reading projection. Canonical HTML, metadata, editorial decision evidence, publication records, projection records and incumbent parity remain the existing contracts.

The `pages-shadow` workflow is read-only with respect to GitHub Pages. It rebuilds the pinned incumbent, overlays additive publication namespaces, validates the result and uploads an ordinary Actions artifact.

## Readiness evidence

`tools/cutover_readiness.py` produces `publication-meta/CUTOVER_READINESS.json` inside the shadow artifact. The receipt is a local migration/evidence projection, not a new tare.tools kernel primitive.

It composes rather than replaces existing evidence:

1. `validate_pages_contract.py` independently rechecks base path, internal links/fragments, semantic-surface fingerprints, editorial evidence and incumbent byte parity.
2. `PARITY_REPORT.json` binds the candidate to the pinned incumbent.
3. the rollback drill inventories the materialized incumbent, verifies every critical path from `INCUMBENT_PROFILE.json`, and requires parity to bind to the same incumbent source ref.
4. workflow ownership inspection fails the shadow gate if the candidate acquires Pages deployment capability while the incumbent owner is still recorded.
5. canary evidence reports the real publication lifecycle state without synthesizing editorial authority.

A green shadow build is evidence. It is never cutover authority.

## Canary lifecycle

The real canary uses document ID `research.pages.canary.v1`.

The canary must follow the normal repository lifecycle:

`submission -> editorial decision -> publication -> SIGNAL projection -> independent validation`

The infrastructure PR must not fabricate `EDITORIAL_DECISION.json` merely to obtain a green result. Before a legitimate decision exists, the receipt reports `MISSING` or `PENDING_OWNER_DECISION`. After an accepted, Pages-approved decision but before publication/projection it reports the corresponding pending state. Only an actually projected approved publication can report `PROJECTED_APPROVED`.

The canary submission should therefore be reviewed as a separate submission PR. Its content must remain explicitly RESEARCH/evidence unless separately promoted through the canonical tare.tools process.

## Rollback semantics

`rollback_ready=true` means the pinned incumbent was materially rebuilt in the current run, its deterministic file inventory was captured, all critical paths exist, and the candidate parity report proves the rebuilt incumbent is preserved without missing or modified incumbent paths.

A remembered SHA alone is not rollback readiness.

This drill does not modify the public site.

## Semantic-surface parity

The protected semantic surface is versioned in `tools/pages_common.py`. It covers document text, IDs, headings, tare roles/sections, paragraphs, lists/list items, blockquotes, emphasis, details/summary, figures, tables, link labels, image alt/asset identity, and code/pre text.

It intentionally does not claim full DOM equivalence. Navigation destinations are validated separately through the link rewrite ledger and final-site link/fragment validation.

## Visual evidence

DOM and semantic checks are not relabeled as visual proof. Until a real browser/render validation is captured for the approved canary, `CUTOVER_READINESS.json` reports `VISUAL_VALIDATION_NOT_RUN` as an open condition.

A future browser check should cover at least desktop and mobile rendering, SIGNAL asset loading under the Project Pages base path, visible article sections, figure/table/code legibility and navigation. Prefer existing tooling if available rather than introducing a large browser framework solely for this migration.

## Authority boundary

The readiness receipt always records:

- `production_effect_performed: false`
- `cutover_authorized: false`

Neither a manifest, a PR input, a green CI result nor the model may flip those fields to true.

A later cutover requires a separate reviewed change that, at minimum, has an approved real canary, browser/render evidence, a green rollback drill, green parity/contract evidence, explicit owner authority, incumbent deploy-owner disablement, single-owner transfer under the shared `github-pages` serialization domain, observation and a rollback path.

There must be no interval with two active deploy owners.

## Migration sequence

```text
stable incumbent
  -> shadow publisher merged
  -> readiness/rollback evidence
  -> separate real canary submission
  -> legitimate editorial decision
  -> publication + shadow projection
  -> independent validation + visual evidence
  -> independent audit
  -> explicit owner authority
  -> separate single-owner cutover change
  -> observe / rollback if required
```

The cutover remains blocked until those later gates are satisfied.