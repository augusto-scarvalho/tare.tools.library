# Contributing to tare.tools.library

This repository is a Library-owned research corpus and a derived, rebuildable
retrieval index (ADR-070). It is not the ecosystem's central article publisher,
and it is not an authority for grounding.

## Put each document with its owner

- Tool specifications, architecture, operations, and ontology stay in that
  tool's repository.
- Ecosystem-wide governance, authority, and settlement stay in `tare.tools.os`.
- Library research, Library retrieval policy, and Library tooling stay here.
- External material stays with its owner: no copy, catalog entry or pinned revision here.

Do not copy an external document or ontology into this repository for
convenience. To search it, index its owner's checkout with
`--owner-root REPOSITORY=PATH` (see `docs/DOCUMENT_OWNERSHIP.md`).

## Add Library-owned research

Place new Library research directly in the appropriate `docs/research/`
program. Give it enough metadata and provenance for deterministic indexing,
state its evidence limits, and add it to `docs/INDEX.md`. Write it in English
(see `docs/policies/TRANSLATION_POLICY.md`). Use a new document for a materially
new conclusion. When a document becomes obsolete, delete it and fix the links to
it; Git history keeps it, and the repository has no archive folder.

There is no website: new documents are searchable through Library indexing and
need no build or deployment.

## Public contributions and local data

The repository is public. Research and reproducible experiments may be shared;
credentials, private conversations and user-specific indexes must stay local.
Distributing the indexer does not require publishing the data a user indexes.
Review actual content before contributing generated results.

## Local verification

```powershell
pytest tests
python -m tools.bookkeeper.cli audit --root docs
python tools/changelog_guard.py origin/main HEAD --repo .
```
