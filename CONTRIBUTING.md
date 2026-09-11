# Contributing to tare.tools.library

This repository is a federated catalog, a Library-owned research corpus, and a
bounded retrieval layer. It is not the ecosystem's central article publisher.

## Put each document with its owner

- Tool specifications, architecture, operations, and ontology stay in that
  tool's repository.
- Ecosystem-wide governance, authority, and settlement stay in `tare.tools.os`.
- Library research, Library retrieval policy, and Library tooling stay here.
- External material is represented here only by a pinned pointer in
  `catalog/FEDERATED_DOCUMENTS.json` or `catalog/FEDERATED_ONTOLOGIES.json`.

Do not copy an external document or ontology into this repository for
convenience. A pointer must include the owner repository, full Git revision,
canonical path, and SHA-256 of the exact owner bytes.

## Add Library-owned research

Place new Library research directly in the appropriate `docs/research/`
program. Give it enough metadata and provenance for deterministic indexing,
state its evidence limits, and keep generated indexes out of the source of
truth. Use a new document for a materially new conclusion; do not rewrite an
immutable historical edition.

The website and GitHub Pages projection are discontinued. Existing HTML
articles remain research documents in the catalog. New documents are
searchable through Library indexing; no website build or deployment is needed.

## Add or update an external pointer

1. Commit and push the canonical file in its owner repository.
2. Record that exact commit, path, and blob SHA-256 in the appropriate
   federated catalog.
3. Run the catalog validator and repository tests.
4. Never keep a fallback payload copy in Library.

## Public contributions and local data

The repository is public. Research and reproducible experiments may be shared;
credentials, private conversations and user-specific indexes must stay local.
Distributing the indexer does not require publishing the data a user indexes.
Review actual content before contributing generated results or source bundles.

## Local verification

```powershell
pytest tests
python -m tools.federated_documents --root .
python -m tools.federated_ontologies --root .
python tools/tare_docs.py validate-repo .
python tools/tare_docs.py rebuild-catalog .
git diff --exit-code -- catalog/MASTER_CATALOG.json
python -m tools.bookkeeper.cli audit --root docs
```
