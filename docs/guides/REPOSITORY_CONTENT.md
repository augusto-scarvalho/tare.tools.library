# Product corpus and private records

Library owns its adopted research corpus, specifications, vocabulary, curation
and retrieval tools. Those research payloads remain distributed, including the
historical editions explicitly retained by `SPEC-LIBRARY-001`. External owners'
documents remain pinned references in the federated catalog. A blanket removal
of `docs/archive/` would remove product content and is not this policy.

Raw round-table cases and the architectural question ledger belong to private
operator custody. [RECORDS_ARCHIVE.json](../RECORDS_ARCHIVE.json) retains their
original commit, path, SHA-256, blob identity and size. It also identifies the
original editions of maintained documents whose local links or operator examples
were made portable. Case bytes, votes and historical outcomes are not rewritten.
Editorial link/example corrections do not constitute new ratification.

Before integrating record deletions, back up local files and verify their hashes.
Restore private records to their original, ignored paths after updating. Do not
overwrite a locally modified record. Historical owner links may require access
to private custody; ordinary tests must not retrieve those records or old Git
objects. Verifying a case reference does not verify its quorum or approve a Work.

Normal lexical/vector retrieval excludes historical and generated material.
`--include-history` is explicit. Source validation, federated catalog checks,
manifest compilation and Bookkeeper audits are offline and independent of local
deliberation records. Live indexing and inference require their own authorization;
this preparation does not install or download models.
