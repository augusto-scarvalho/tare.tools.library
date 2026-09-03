# Frozen HTML projection contract

Profile: `tare-research-html/1.0`.

The central article publisher is retired. This compatibility contract applies
only to the four records in `site/LEGACY_PAGES_PROJECTIONS.json`; it is not an
intake or publication path for new documents.

## Retained semantic surface

Each retained source must have:

- an HTML5 document with language, UTF-8 metadata, and title;
- exactly one `main > article[data-tare-document]`;
- a document header with the title and abstract;
- an explicit authority boundary;
- stable `scope`, `evidence`, `findings`, `limitations`, and `references`
  sections;
- globally unique IDs and accessible media;
- metadata that agrees with its language, title, abstract, provenance, status,
  and lineage.

Rich semantic HTML remains allowed. Scripts, forms, iframes, event handlers,
and remote assets remain forbidden in the retained projection.

## Read-only SIGNAL derivation

The builder validates the exact retained source hash and places its semantic
tree inside the SIGNAL shell. It copies only declared local assets, resolves
links deterministically, fails on unresolved local targets, records every
rewrite, and requires equal semantic fingerprints before and after the allowed
presentation transform.

The derived page never changes document authority or status. Historical
`EDITORIAL_DECISION.json`, `PUBLISH_MANIFEST.json`, and
`PUBLICATION_RECORD.json` files are evidence consumed by the rebuild; no tool
in this repository creates new ones.

The pinned incumbent is rebuilt and preserved byte-for-byte. Historical URL
and asset names remain stable for compatibility. See
`PAGES_CUTOVER_READINESS.md` for the closed-inventory and deployment boundary.
