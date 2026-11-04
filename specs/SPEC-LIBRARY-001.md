# SPEC-LIBRARY-001: Library research corpus and derived retrieval index

- **Status:** `OWNER_ADOPTED`
- **Governing decision:** [ADR-070](../docs/adr/ADR-070_LIBRARY_AS_DERIVED_RETRIEVAL_INDEX.md)
- **Canonical repository:** `tare.tools.library`
- **Version:** 3.0.0

## Purpose

Hold Library-owned research and provide deterministic, rebuildable retrieval over documents that stay in the
repositories that own them. The Library is not an authority for grounding.

## Product boundary

The Library remains a publicly distributed research corpus and indexing/retrieval tool.
The repository website and GitHub Pages projection were discontinued by the
owner on 2026-09-11. Hosting or generating a blog is outside this product.
Library research in `docs/research/` is part of the product; obsolete history
is deleted from the tree (ADR-069 amendment of 2026-11-03).

## Verifiable acceptance criteria

- **AC-01 — No foreign payload:** the Library tracks no copy, catalog entry or
  pinned revision of a document another repository owns; that document is read
  only from its owner's checkout.
- **AC-02 — Repository-qualified identity:** an index row for an owner document
  is `repository:path`; bare document numbers never identify an ecosystem-wide
  record.
- **AC-03 — Bounded default corpus:** default lexical and vector retrieval omit
  history paths and generated catalog projections.
- **AC-04 — Exact-content collapse:** equal SHA-256 payloads of the Library
  corpus are indexed once.
- **AC-05 — Derived, rebuildable index:** the vector index is built only from
  the Library corpus and the owner checkouts passed as
  `--owner-root REPOSITORY=PATH`; a run removes stale rows only for the roots it
  read, and an unavailable owner checkout refuses the run without removing rows.
- **AC-06 — Zero-cost validation:** the tests and lexical search need no paid
  API.

## Amendment (2026-11-03)

Version 3.0.0 follows ADR-070, which supersedes ADR-069. AC-05 no longer
requires a machine-readable federation (the v3 Library manifest with canonical
external sources); it requires a derived index that reads owners where they
live. AC-01 and AC-02 no longer require a pinned revision, and AC-06 no longer
names catalog validation: the catalogs, the manifest and their validators were
deleted.
