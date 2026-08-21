# Document Policy

## 1. Purpose

Define deterministic rules for document identity, status, routing, provenance, lineage and promotion boundaries.

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

The research repository may **quote/reference** CURRENT/TARGET, but does not mint them.

## 4. Deterministic routing

- `document_type=research` → `research/<primary-context>/...`
- `document_type=proposal` → `proposals/<primary-context>/...`
- `document_type=experiment` → `experiments/<primary-context>/...`
- `document_type=archaeology|handoff` → `archaeology/...`
- `document_type=source` → `sources/...`
- `status=TARGET|CURRENT` with destination `tare.tools.research` → DENY.
- canonical types (`adr`, `spec`, `bdd`, `implementation_packet`) → require promotion flow and canonical repository.

LLMs may propose metadata; the validator/router owns routing decisions.

## 5. Originals

Files under `corpus/original/` are immutable evidence. Corrections create a new file/version; they never silently replace the original.

## 6. Lineage

Every substantial derived document SHOULD record `supersedes`, `superseded_by`, and/or `derived_from` where known.

## 7. Promotion

Publication != ratification.

Research promotion requires a separate Promotion Packet with canonical references, decision authority and required assurance. The publisher implemented here intentionally does not auto-promote.
