# Canonical HTML Publication Standard

Profile: `tare-research-html/1.0`.

The primary research publication is a complete UTF-8 HTML document. It is the
canonical editorial artifact in this repository; a SIGNAL Pages document is a
derived projection and never replaces it. Do not reduce rich HTML to Markdown
as an intermediate publication format.

The required submission packet is defined in [CONTRIBUTING.md](CONTRIBUTING.md).
Use [canonical-article.html](templates/canonical-article.html) as its starting
point and keep `article.html` paired with `document-metadata.json`.

## Required semantic surface

- HTML5 doctype, `lang`, UTF-8 and a title;
- exactly one `main > article[data-tare-document]`;
- a document header containing the `h1` and abstract;
- explicit authority boundary inside the canonical article;
- exactly one `scope`, `evidence`, `findings`, `limitations` and `references`
  section inside the canonical article, each using its stable matching `id`;
- globally unique IDs;
- accessible images, figures and tables;
- provenance, lineage, status and authority in the metadata sidecar;
- HTML language/title/abstract fidelity with the metadata sidecar.

Rich semantic HTML is allowed: tables, figures, captions, details, code,
MathML, SVG and `data-*` metadata. CSS is presentation only and must not be
the sole carrier of meaning.

Scripts, forms, iframes, event handlers and remote assets are not accepted in
new canonical packets. Preserve a historical artifact unchanged when needed;
its later Pages adapter must record any safe projection limitation.

## Publication authority

The canonical HTML and `PUBLISH_MANIFEST.json` may request a publication
channel but may not grant it. `pages_approved` is not a manifest field.

When Pages is requested, publication requires a separate
`EDITORIAL_DECISION.json` bound to the exact manifest SHA-256. Only an accepted
editorial decision may produce `pages_approved: true` in
`PUBLICATION_RECORD.json`. The decision digest and reviewer provenance are
carried into the publication record.

## SIGNAL Pages derivation

Pages parses an approved canonical HTML copy, validates its exact hash, and
places its semantic tree inside a versioned SIGNAL shell. The projection:

- inherits the source document language;
- uses the explicit GitHub Project Pages base path;
- copies only declared local media assets;
- deterministically resolves relative/internal/cross-publication links;
- fails closed on unresolved internal targets;
- records every link and asset rewrite in `PROJECTION_RECORD.json`;
- records the source hash, build commit, SIGNAL profile and editorial decision;
- computes normalized semantic fingerprints before and after projection and
  requires equality for transformations classified as presentation/navigation;
- never upgrades `RESEARCH`, `PROPOSED`, `EXPERIMENTAL` or `HISTORICAL`.

The semantic fingerprint intentionally protects content-bearing structure,
text, headings, roles, anchors, figures, tables, link labels, media meaning and
code while navigation target rewrites are evidenced separately. Presence of a
hash field alone is not parity evidence; the generated article is independently
fingerprinted by the Pages contract validator.

## Migration and incumbent preservation

The publication renderer is introduced through a Strangler path. During the
migration, the currently deployed reader is rebuilt from a pinned source ref
and copied byte-for-byte into the shadow output. New publisher paths are
additive (`/publications/`, `/p/<document-id>/`, publisher assets and projection
records).

The shadow build fails if any incumbent file changes or disappears. Routine
pull-request and `main` push builds do not deploy. Cutover is a separate,
explicit Pages workflow dispatch after parity evidence is accepted, with the
pinned incumbent retained as the rollback source until a later retirement
change.
