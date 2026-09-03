# Changelog

Notable changes to `tare.tools.library` are recorded here, newest first. This file starts with a concise retrospective of the current public baseline; Git history remains authoritative for commit-level detail.

## Unreleased

### Added

- Added a fail-closed federated ontology registry that resolves every concept
  to one repository, commit, path and SHA-256 without copying its payload.
- Added the pinned federated document registry, its fail-closed validator and
  a v3 manifest projection with repository-qualified source identities.
- Added ADR-069 and the practical document-ownership guide.

### Changed

- Limited default lexical and vector retrieval to active Library-owned
  Markdown, with exact-content collapse and explicit historical opt-in.
- Reframed the Library as a catalog and research owner instead of a mirror of
  every satellite's editable documentation.

### Fixed

- Repaired Publication PR workflow validation, credential gating, current incoming-path routing, and repository targeting.

### Removed

- Retired the central six-concept ontology payload after Kernel, SpecGraph and
  OS took ownership of their respective concepts.
- Retired 445 verified payload copies after recording their canonical owner,
  path, full commit and SHA-256; immutable snapshot editions remain available
  outside the default retrieval scope.

## 2026-08-21

### Added

- Ratified RFC-009 / ADR-068 and standardized repository branches and CI pipelines ([fac6af0](https://github.com/augusto-scarvalho/tare.tools.library/commit/fac6af0)).
- Ratified RFC-008 / ADR-067 and established the canonical repository taxonomy ([81df37f](https://github.com/augusto-scarvalho/tare.tools.library/commit/81df37f)).
- Ratified ADR-066 and enforced separation between the distributable library and sovereign corpus ([173efcb](https://github.com/augusto-scarvalho/tare.tools.library/commit/173efcb)).
- Ratified ADR-061 through ADR-065, including the hybrid router, lean MCP gateway, and emergency halt protocol ([55ccaaf](https://github.com/augusto-scarvalho/tare.tools.library/commit/55ccaaf)).

### Changed

- Consolidated root folders and policies into the canonical taxonomy ([f3a1448](https://github.com/augusto-scarvalho/tare.tools.library/commit/f3a1448)).

## 2026-08-19

### Added

- Added the federated multi-source harvester and adversarial mutation suite ([bdceaf3](https://github.com/augusto-scarvalho/tare.tools.library/commit/bdceaf3)).
- Added semantic search, local RAG synthesis, summarization, and translation tools ([4a8e746](https://github.com/augusto-scarvalho/tare.tools.library/commit/4a8e746)).
- Added one-command embedding and summarization to ingestion ([4996697](https://github.com/augusto-scarvalho/tare.tools.library/commit/4996697)).
