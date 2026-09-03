# Frozen Pages projection

The former Pages cutover is complete and the central article publisher is
retired. This file records the small compatibility surface that remains.

## Closed inventory

`site/LEGACY_PAGES_PROJECTIONS.json` is the only source of projected article
records. It lists four already accepted Library-owned research pages. The
builder fails when the list is missing, malformed, duplicated, unsafe, points
to a missing record, or when it discovers an unlisted active publication
record.

New documents do not enter this inventory. They remain in their owner
repository and become discoverable through normal Library indexing or a
federated pointer.

## Rebuild contract

`tools/build_pages.py` may only rebuild the closed inventory. It continues to
verify exact source and decision hashes, retained translation bindings,
semantic fingerprints, deterministic link rewrites, and byte-for-byte
preservation of the pinned incumbent. `tools/validate_pages_contract.py`
independently checks the generated result.

The historical route names (`/publications/`, `/p/<id>/`, and
`assets/publisher/`) remain unchanged solely for link compatibility. Their
names do not imply that a publisher service still exists.

## Authority

The projection is read-only and cannot create research, approve an article, or
promote a claim. Its workflow has no Pages write permission, deployment action,
or deploy owner; it uploads only an ordinary short-lived CI preview artifact. A
green rebuild proves only that the frozen reader is internally consistent.
