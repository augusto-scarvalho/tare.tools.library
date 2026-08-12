# Document Policy

## 1. Purpose

Define deterministic rules for document identity, status, routing, provenance, lineage, retention and promotion boundaries.

## 2. Precedence

```text
Git / source / canonical architecture / ADR / SPEC / BDD / gates
    > canonical summaries
    > findings
    > proposals
    > research
    > historical chat summaries
```

## 3. Status semantics

| Status | Meaning | Default repository |
|---|---|---|
| RESEARCH | evidence/hypothesis/investigation | tare.tools.research |
| PROPOSED | proposal not ratified | tare.tools.research |
| EXPERIMENTAL | experimental protocol/result | tare.tools.research |
| HISTORICAL | immutable historical evidence | tare.tools.research |
| TARGET | ratified desired architecture | tare-tools only |
| CURRENT | proven implementation/state | tare-tools/Git/evidence |

The research repository may quote/reference CURRENT/TARGET, but does not mint them.

## 4. Deterministic routing

- `document_type=research` → `research/<primary-context>/...`
- `document_type=proposal` → `proposals/<primary-context>/...`
- `document_type=experiment` → `experiments/<primary-context>/...`
- `document_type=archaeology|handoff` → `archaeology/...`
- `document_type=source` → `sources/...`
- `status=TARGET|CURRENT` with destination `tare.tools.research` → DENY.
- canonical types (`adr`, `spec`, `bdd`, `implementation_packet`) → require promotion flow and canonical repository.

LLMs may propose metadata; the validator/router owns routing decisions.

## 5. Originals and irreversible evidence

Files under `corpus/original/`, exact historical snapshots, source bundles and their provenance manifests are append-only evidence. Corrections create a new file/version; they never silently replace or delete the original merely to make the corpus cleaner.

## 6. Derived projections and live-tree retention

A derived artifact is retained in Git HEAD only when it carries semantic value not reconstructible from its declared inputs, for example scientific synthesis, reconciliation, findings, implementation-research deltas, provenance decisions, human review or governed translation corrections.

Pure presentation projections — format-only HTML renderings, generated navigation and equivalent build outputs — SHOULD be reproducible from tracked source identity + tooling and MAY be excluded from the live tree. Their prior committed versions remain recoverable through Git history.

Removing a projection MUST NOT:

- delete or rewrite its source/original;
- erase provenance required to reconstruct it;
- remove the only copy of a scientific finding or review decision;
- convert historical absence into an assertion that the artifact never existed.

Do not create a second `/archive` merely to duplicate bytes already retained by Git history. Evidence subject to the append-only rule remains live even when large.

## 7. Lineage

Every substantial derived document SHOULD record `supersedes`, `superseded_by`, and/or `derived_from` where known. A refresh may recenter or refine historical research without rewriting the historical source.

## 8. Promotion

Publication != ratification.

Research promotion requires a separate Promotion Packet with canonical references, decision authority and required assurance. The publisher intentionally does not auto-promote.
