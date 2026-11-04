# Library documentation index

## Research

Library-owned research. These documents are `RESEARCH`: they do not create `CURRENT` or `TARGET` architecture.

- Methodology and research program
  - [Bounded implementer profiles: longitudinal study](research/01_methodology-research-program/2026-08-13-bounded-implementer-profile-longitudinal-study.md)
    and its [evidence annex](research/01_methodology-research-program/2026-08-13-implementer-observed-evidence-ledger.md)
  - [CURRENT to North Star: a time-to-trust portfolio](research/01_methodology-research-program/2026-08-13-current-to-north-star-portfolio/README.md)
  - [Cyclic multi-role research protocol](research/01_methodology-research-program/cyclic-multi-role-research-protocol/README.md),
    with its first run recorded in [docs/assurance](assurance/cyclic-multi-role-research-protocol/2026-08-11-run-001/)
- Validation and assurance
  - [Assurance topology and evidence acquisition](research/08_validation-assurance/2026-08-13-assurance-topology/README.md)
- Project and workspace
  - [Hierarchical work planning and cross-task optimization](research/11_project-workspace/hierarchical-work-planning-cross-task-optimization-2026-08-13/article.html)

## Decisions and specification

- [SPEC-LIBRARY-001](../specs/SPEC-LIBRARY-001.md): the Library's acceptance criteria.
- [ADR-070](adr/ADR-070_LIBRARY_AS_DERIVED_RETRIEVAL_INDEX.md): the Library is a derived retrieval index and
  documents stay with their owners (the live ownership rule). It supersedes
  [ADR-069](adr/ADR-069_FEDERATED_DOCUMENT_OWNERSHIP_AND_BOUNDED_INDEXING.md), the pinned pointer catalog.
- [ADR-058](adr/ADR-058_INCREMENTAL_CONTENT_ADDRESSED_VECTOR_INDEXING.md): incremental content-addressed vector
  indexing.
- [ADR-066](adr/ADR-066_CORPUS_SEGREGATION_DISTRIBUTABLE_LIBRARY_VS_SOVEREIGN_VAULT.md) and
  [ADR-067](adr/ADR-067_CANONICAL_REPOSITORY_TAXONOMY_AND_GHOST_PURGE.md): repository content and layout.
- Ecosystem decisions, including the engineering doctrine
  ([ADR-062](https://github.com/augusto-scarvalho/tare.tools.os/blob/main/docs/adr/ADR-062_UNIVERSAL_FRUGAL_ENGINEERING_DOCTRINE_AND_SOVEREIGN_BYOC.md)),
  live in `tare.tools.os`.

## Guides and policies

- [Document ownership and retrieval](DOCUMENT_OWNERSHIP.md)
- [Repository content and private records](guides/REPOSITORY_CONTENT.md)
- [Document policy](policies/DOCUMENT_POLICY.md), [promotion policy](policies/PROMOTION_POLICY.md),
  [translation policy](policies/TRANSLATION_POLICY.md), [HTML research article profile](policies/HTML_PUBLICATION_STANDARD.md)
- [Changelog policy](CHANGELOG_POLICY.md)
- [Experiment template](templates/EXP-template.md), [specification template](templates/SPEC-template.md)
- [References to private round-table records](RECORDS_ARCHIVE.json) (pointers only; no new ratification)
