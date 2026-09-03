# SPEC-LIBRARY-001: Federated technical catalog and bounded retrieval

- **Status:** `OWNER_ADOPTED`
- **Governing decision:** [ADR-069](../docs/adr/ADR-069_FEDERATED_DOCUMENT_OWNERSHIP_AND_BOUNDED_INDEXING.md)
- **Canonical repository:** `tare.tools.library`
- **Version:** 2.0.0

## Purpose

Provide content-addressed cataloging, Library-owned research and deterministic
retrieval without storing editable copies of documents owned by other tools.

## Verifiable acceptance criteria

- **AC-01 — One owner payload:** every retired Library copy resolves to one
  repository-qualified canonical path and pinned revision.
- **AC-02 — Repository-qualified identity:** external identity includes
  repository, path, revision and SHA-256; bare document numbers never identify
  an ecosystem-wide record.
- **AC-03 — Bounded default corpus:** default lexical and vector retrieval omit
  immutable history and generated catalog projections.
- **AC-04 — Exact-content collapse:** equal SHA-256 payloads are indexed once.
- **AC-05 — Machine-readable federation:** the v3 Library manifest carries
  canonical external sources and marks retired Library paths `EXCLUDED`.
- **AC-06 — Zero-cost validation:** catalog validation and lexical search need
  no paid API.
