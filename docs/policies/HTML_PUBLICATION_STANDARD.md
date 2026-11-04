# HTML research article profile

Some Library research is written as a self-contained HTML article with a `PUBLISH_MANIFEST.json` and a
`document-metadata.json` next to it, for example
[hierarchical work planning](../research/11_project-workspace/hierarchical-work-planning-cross-task-optimization-2026-08-13/).
The `tare-research-html/1.0` profile keeps those articles indexable and safe to open offline:

- one `main > article[data-tare-document]`, a document header with the `h1` title and an abstract that match the
  metadata, an authority-boundary note, and exactly one section each for `scope`, `evidence`, `findings`,
  `limitations` and `references`;
- `html lang` equal to the metadata language;
- no scripts, forms, iframes, event handlers or remote assets; images need alt text, figures a caption, tables a
  caption or `aria-label`.

Check an article with:

```powershell
python tools/validate_canonical_html.py <article-folder>/PUBLISH_MANIFEST.json
```

The Library website and its GitHub Pages projection were discontinued on 2026-09-11; this profile is not a
publication step and new research may also be plain Markdown.
