# ADR-070: The Library is a derived retrieval index; documents stay with their owners

- **Status:** `OWNER_ADOPTED`
- **Decision date:** 2026-11-03
- **Authority:** explicit Human Operator direction
- **Scope:** the Library's role, owner-document identity and the inputs of the vector index
- **Supersedes:** [ADR-069](ADR-069_FEDERATED_DOCUMENT_OWNERSHIP_AND_BOUNDED_INDEXING.md)

## Context

ADR-069 moved editable payloads to the repositories that own them and kept a pinned pointer per document in
`catalog/FEDERATED_DOCUMENTS.json` and `catalog/FEDERATED_ONTOLOGIES.json`, compiled into
`catalog/LIBRARY_MANIFEST.json` for the OS to ground work on. Those pins repeated what the OS commit and its
satellite gitlinks already fix, needed a Library change for every owner edit, drifted out of date, and named
commits that a fresh-history republish of the repositories would not keep. The OS now reads specifications and
ADRs from its own tree and from `satellites/<repo>` at the gitlink, and no longer reads the Library.

## Decision

1. A document lives only in the repository that owns its subject. The Library keeps no copy, catalog entry, pin
   or compiled manifest for it.
2. The Library is a derived, rebuildable index for research and retrieval. It reads documents where they live, by
   path: its own corpus, and the owner checkouts passed as `--owner-root REPOSITORY=PATH`. Deleting the index
   loses nothing.
3. The Library is never an authority for grounding. An index row is a retrieval hint, not evidence that a document
   is current, adopted or implemented.
4. An owner document's identity is `repository:path`; a bare ADR number is not a global identity. Content identity
   is SHA-256 (ADR-058), so the index pins no commit. A run removes stale rows only for the roots it read.
5. ADR-069's rules on the default corpus stay: active Library Markdown only, equal payloads indexed once, history
   opt-in, generated catalogs excluded.
6. The Library keeps owning its research under `docs/research/`, its decisions, its specification and its tools.

## Consequences

- The catalogs, the manifest, their validators and the manifest compiler are deleted, with the indexer's
  `--federated` mode. Concept anchoring and `tools.query --concept` read `ontology/domain_ontology.yaml` from each
  owner root.
- Retrieval is lexical today. Embeddings and vector search resume later, with indexing workers over the same owner
  roots.

## Verification

```powershell
python -m pytest tests -q
```
