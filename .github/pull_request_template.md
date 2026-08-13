## PR type

- [ ] Submission — draft packet in `incoming/<document-id>/`
- [ ] Publication — router-produced output from an accepted submission
- [ ] Maintenance — no change to evidence meaning or authority

## Editorial scope

- Document ID:
- Document type / status:
- Requested editorial decision: `accept | revise | reject | park`
- This PR does not mint `CURRENT` or `TARGET`: [ ]
- Canonical `tare-tools` commit / architecture epoch (required for substantial research):

## Packet and provenance

- `PUBLISH_MANIFEST.json` path:
- `document-metadata.json` path:
- Artifacts proposed for publication:
- Sources, hashes, and availability:
- Exact source bytes materialized? If not, state the reproducibility limit:
- Lineage (`derived_from`, `supersedes`, `superseded_by`):

## Research boundary

- Results / load-bearing evidence:
- Hypotheses or proposals:
- Negative evidence, caveats, and unresolved questions:
- Derived editions regenerated from the current evidence state: [ ] / N/A

## Validation

- [ ] `python tools/tare_docs.py validate-repo .`
- [ ] `python tools/tare_docs.py rebuild-catalog .`
- [ ] `git diff --exit-code -- catalog/MASTER_CATALOG.json`
- Additional validation or reason it is N/A:

## Reviewer note

Review publication scope, provenance, lineage, and authority before evaluating
style. Promotion to canonical architecture requires the separate canonical
process.
