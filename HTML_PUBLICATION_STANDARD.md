# Canonical HTML Publication Standard

Profile: `tare-research-html/1.0`.

The primary research publication is a complete UTF-8 HTML document. It is the
canonical editorial artifact in this repository; a Signal Pages document is a
derived projection and never replaces it. Do not reduce rich HTML to Markdown
as an intermediate publication format.

The required submission packet is defined in [CONTRIBUTING.md](CONTRIBUTING.md).
Use [canonical-article.html](templates/canonical-article.html) as its starting
point and keep `article.html` paired with `document-metadata.json`.

## Required semantic surface

- HTML5 doctype, `lang`, UTF-8 and a title;
- `main > article[data-tare-document]`;
- a document header, `h1` and abstract;
- explicit authority boundary;
- uniquely identified `scope`, `evidence`, `findings`, `limitations` and
  `references` sections;
- accessible tables, figures, captions, alt text and stable anchors;
- provenance, lineage, status and authority in the metadata sidecar.

Rich semantic HTML is allowed: tables, figures, captions, details, code,
MathML, SVG and `data-*` metadata. CSS is presentation only and must not be
the sole carrier of meaning.

Scripts, forms, iframes, event handlers and remote assets are not accepted in
new canonical packets. Preserve a historical artifact unchanged when needed;
its later Pages adapter must record any safe projection limitation.

## Signal Pages derivation

Pages will parse an approved canonical HTML copy, validate its hash, and place
its semantic tree inside a versioned Signal shell. The projection records its
source hash, build commit, Signal profile, link rewrites and every deliberate
omission. Publication status remains `RESEARCH`, `PROPOSED`, `EXPERIMENTAL` or
`HISTORICAL`; the renderer never upgrades it.
