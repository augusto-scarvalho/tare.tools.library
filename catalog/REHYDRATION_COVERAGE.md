# Rehydration Coverage

> Coverage is intentionally conservative. Counts from different discovery surfaces are not added unless identity has been reconciled.

## Reported historical baseline

| Measure | Reported value | Verification in current runtime |
|---|---:|---|
| Archive files | 126 | report only |
| Catalogued artifacts | 102 | report only |
| Version lineages | 21 | report only |
| Materialized originals in historical ZIP | 50 | report only |
| File Library references in historical ZIP | 52 | report only |
| Historical ZIP SHA-256 | `7b655e2879a3033d2d2162fa82f77bb4e8ffc38f365d24ed7a00b077b0cd5ce3` | archive bytes not currently recovered |

## Current bootstrap state

- **11** seed source artifacts are materialized byte-for-byte and have English derivatives.
- **72** File Library artifacts are registered as discovery references.
- **0** discovery references have exact-byte identity crosswalks.
- **16** references already have expected SHA-256/size constraints reported by independent validation manifests (not locally verified source bytes yet).
- **72** still require exact-byte materialization.
- **49** translations remain blocked on missing exact source bytes.
- **0** newly materialized sources are ready for English translation.
- **23** discovery references are marked native English.
- **19** multi-item lineage families are visible in the discovery projection.

## Why there is no corpus recovery percentage yet

`materialized seeds + File Library discovery references` is not a valid recovered-artifact count. Records may overlap the historical corpus, represent later versions, duplicate exports, or multiple artifacts with the same title. Coverage remains:

`NOT_COMPUTABLE_UNTIL_IDENTITY_CROSSWALK`

The valid path is exact-byte materialization plus identity crosswalk using File Library ID, content hash, reported historical hash, filename, creation time and lineage metadata.
