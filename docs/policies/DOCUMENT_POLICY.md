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
| RESEARCH | evidence/hypothesis/investigation | owning repository |
| PROPOSED | proposal not ratified | owning repository |
| EXPERIMENTAL | experimental protocol/result | owning repository |
| HISTORICAL | immutable historical evidence | owning repository |
| TARGET | ratified desired architecture | canonical owner only |
| CURRENT | proven implementation/state | canonical owner/Git/evidence |

Library research may **quote/reference** CURRENT/TARGET, but does not mint them.

## 4. Repository ownership

- Tool-specific material stays in that tool's repository.
- Ecosystem governance and settlement stay in `tare.tools.os`.
- Library-owned research stays under this repository's `docs/research/`.
- External documents and ontologies enter Library only as pinned catalog
  pointers; their payloads are never routed or copied here.
- Canonical types (`adr`, `spec`, `bdd`, `implementation_packet`) require the
  owning repository's governed lifecycle.

## 5. Originals

Files under `corpus/original/` are immutable evidence. Corrections create a new file/version; they never silently replace the original.

## 6. Lineage

Every substantial derived document SHOULD record `supersedes`, `superseded_by`, and/or `derived_from` where known.

## 7. Promotion

Indexing or a research record is not ratification.

Research promotion requires the owner repository's governed change, canonical
references, decision authority, and required assurance. Library indexing has no
promotion authority.
