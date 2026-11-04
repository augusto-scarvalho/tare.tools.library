# Repository content and private records

The repository distributes the Library's own research (`docs/research/`), its decisions and policies, its
specification and its tools. Documents owned by other repositories stay in their owners' trees; the Library keeps no
copy or catalog entry for them, and its index reads them from owner checkouts
([ADR-070](../adr/ADR-070_LIBRARY_AS_DERIVED_RETRIEVAL_INDEX.md)).

Obsolete history is not kept in the tree. Archived editions, dated snapshots, imported chat transcripts and the
generated catalog projections built from them were deleted on 2026-11-03; Git history is their record. Do not
restore them. When a document becomes obsolete, delete it and fix the references to it; do not move it to an
archive folder.

Raw round-table cases and the architectural question ledger belong to the operator's private custody.
[RECORDS_ARCHIVE.json](../RECORDS_ARCHIVE.json) keeps their original commit, path, SHA-256, blob identity and size,
and the original editions of a few maintained documents whose links were later made portable. A reference to a case
is not a new ratification, and verifying it does not verify its quorum or approve any work.

Keep private records in their ignored local paths (`cases/`, `docs/ARCHITECTURAL_QA_LEDGER.md`). Back them up before
updating a checkout and never overwrite a locally modified record. Ordinary tests never read these records or old
Git objects.

Default lexical and vector retrieval reads only active Library documents (see `tools/document_scope.py`). The
retrieval code still treats `docs/archive/**` and `catalog/corpus/**` as history that `--include-history` opts into;
the repository no longer tracks either directory, so the flag only matters for a local checkout that keeps such
material. Lexical search and Bookkeeper audits run offline; indexing and inference need a configured endpoint and
never download models.
