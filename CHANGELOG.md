# Changelog

Notable changes to `tare.tools.library` are recorded here, newest first. This file starts with a concise retrospective of the current public baseline; Git history remains authoritative for commit-level detail.

## Unreleased

### Changed

- Added a shared, tested changelog guard for local pre-push and GitHub CI. It
  requires meaningful `Unreleased` entries for material changes, validates
  committed content, and prevents silent deletion or rewriting of history.
- Admitted repository-owned `.githooks` in the canonical root taxonomy.
- Routed satellite-agent pre-task grounding through the bounded SpecGraph
  projection while retaining direct `tools.query` use for Library-local
  editorial and diagnostic work.
- Implemented the ADR-060 exact-content projection contract: payload IDs are
  content hashes, provenance retains ordered per-source authority, exact copies
  collapse in linear time, mixed authority stays explicit, and byte-distinct
  semantic conflicts fail closed with a machine-readable receipt. The current
  catalog remains intentionally unpublished while nine measured authority
  conflicts await explicit source disposition.
- Bounded the full Bookkeeper audit by excluding preserved `docs/archive`
  material from its quadratic near-duplicate scan, while SSOT and tombstone
  integrity checks still cover the governed document set.

### Fixed

- Repaired Publication PR workflow validation, credential gating, current incoming-path routing, and repository targeting.

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
