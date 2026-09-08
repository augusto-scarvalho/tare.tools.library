# Changelog

Notable changes to `tare.tools.library` are recorded here, newest first. This file starts with a concise retrospective of the current public baseline; Git history remains authoritative for commit-level detail.

## Unreleased

### Historical recovery

- Preserved distinct candidate research and curation editions from pending
  branches under a hash-bound, history-only archive. Default retrieval and
  active authority remain unchanged; obsolete repository controls and
  proposed deletions were not replayed.

### Integration qualification

- Integrated the pending grouped indexer with explicit owner checkout selection,
  preserved model namespaces and conservative pseudo provenance for incomplete
  embedding responses. Failed owner acquisition preserves existing vectors;
  remote endpoints require explicit configuration.
- Reconciled the useful changelog guard and repository-hook delta from PR #76
  with the current federated ownership model. Exact-content projection is
  already implemented by the newer main; retired payloads and publisher stay
  retired instead of returning with the old branch snapshot.
- The earlier six-owner ontology entry below described a local checkout.
  Publication qualifies five owners: the new Harness pointer is deferred
  because its commit is unavailable remotely and the owner remains frozen.
  Offline tests qualify mechanisms; previous throughput and live-service
  observations were not reproduced by this integration.

### Changed

- Vector index moved to Qwen3-Embedding-4B (namespace `qwen3-embedding-4b`, 2560 dims)
  served from node `aaaaa` over the tailnet; the client batches documents per request,
  adds the Qwen3 query instruction, and never disguises a rejected chunk as a vector.
- The indexer now covers the federated catalog (`--federated`): owner documents are read
  from the pinned Git blobs of sibling checkouts and indexed under `repo@revision:path`.
- Chunks embed with context: a document identity header, the enclosing heading path, and
  ontology triples from the federated domain ontologies (concept anchored by governing
  ADR, id or name); anchored concept ids are stored per chunk. The ontology digest is
  folded into document hashes, so an ontology change re-embeds only what it re-anchors.
- Governing-ADR anchoring is scoped to the concept's owner repository (every satellite has
  an ADR-001) and tolerates zero-padded ids (`ADR-0007`, `adr/0007-...`). Documents are
  embedded in groups of 256 chunks per request instead of one request per document.
- `catalog/FEDERATED_ONTOLOGIES.json` re-pinned to owner HEADs: Kernel and OS ontologies
  expanded (7 and 8 concepts), Dialog Engine (6) and the frozen Harness (7) registered as
  new owners; 35 concepts across 6 repositories.
- Vector DB uniqueness now includes the namespace (migrated in place); paragraphs are
  capped at 1,200 characters; pseudo vectors no longer block incremental re-embedding
  once the server is online.

### Fixed

- Reconciled local editorial authority with federated ownership: preserved
  EN/PT statuses and `OWNER_ADOPTED`, excluded inactive documents, and refused
  unknown statuses before replacing the manifest. Legacy status-less specs
  remain `UNMANAGED_ACTIVE` without being labelled ratified.
- Blocked byte-distinct active semantic identities within each repository,
  while retaining exact-content collapse and independent federated owners.
  Bookkeeper now shares metadata classification, recognizes existing Markdown
  status formats, and excludes archived history from current authority audits.
- Accepted explicit repository identities outside `tare.tools.*` in document
  and ontology catalogs and ownership metadata, retaining bounded identity
  validation and the source catalog's name in retired-copy provenance.
- Consolidated exact manifest payloads by SHA-256 with ordered source
  provenance and a count receipt. Sources remain untouched, and byte-identical
  payloads with conflicting declared identities still block generation.
- Corrected 76 federated document digests to their existing pinned Git blob
  bytes after proving that every mismatch was a newline-only difference.
  Optional `tools.federated_documents --owner REPOSITORY=PATH` verification
  now checks exact pinned content and distinguishes it from structural checks.

### Added

- Registered 20 owner-origin SpecGraph completion contracts (18 SpecGraph,
  two OS) using exact Git document pins without inventing retired Library
  copies. The validator distinguishes these new documents from migrations
  and preserves all 467 historical retired aliases.
- Registered the BacklogGraph repository-owned ontology and advanced the
  SpecGraph pointer to its federated-consumer revision.
- Advanced Kernel and OS ontology pointers to revisions that preserve their
  canonical payload bytes identically on Windows and Linux checkouts.
- Added a closed inventory for the four retained legacy Pages projections.
- Added a fail-closed federated ontology registry that resolves every concept
  to one repository, commit, path and SHA-256 without copying its payload.
- Added the pinned federated document registry, its fail-closed validator and
  a v3 manifest projection with repository-qualified source identities.
- Added ADR-069 and the practical document-ownership guide.

### Changed

- Converted Pages into a read-only compatibility projection over that closed
  inventory; it no longer discovers publication records by broad directory
  scanning and its workflow no longer has GitHub Pages deployment capability.
- Limited default lexical and vector retrieval to active Library-owned
  Markdown, with exact-content collapse and explicit historical opt-in.
- Reframed the Library as a catalog and research owner instead of a mirror of
  every satellite's editable documentation.

### Fixed

- Pointed hosted-runner pip caching at the repository's real dependency file
  so CI reaches validation instead of failing during Python setup.

### Removed

- Retired the central article publisher, its submission/editorial workflows,
  routing backends and packet-preparation commands. New external documents now
  remain exclusively in their owner repository and enter Library by pointer.
- Removed superseded cutover authority/readiness machinery and its stale audit
  receipt after the Pages workflow became a deploy-incapable preview build.
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
