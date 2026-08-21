# Translation Policy

## Authority

The Portuguese source document is the historical source artifact. English translations are derived representations and **do not acquire architectural authority by translation**.

In any conflict between a translation and its source, the source wins. In conflicts about CURRENT/TARGET architecture, the canonical `tare-tools` repository, Git, source, ratified architecture, ADRs, SPECs, BDDs and gates take precedence over both source research and translations.

## Translation rules

1. Preserve claims, uncertainty, status markers (`CURRENT`, `TARGET`, `PROPOSED`, `RESEARCH`), dates, citations, URLs, identifiers, hashes and code blocks.
2. Do not silently correct, reconcile, modernize or supersede historical content while translating it.
3. Preserve project-specific canonical nouns (`TaskEnvelope`, `ExecutionBinding`, `Authority`, `Permit`, `EffectReceipt`, etc.) exactly unless the source itself uses a translated descriptive phrase.
4. Translate explanatory prose faithfully, keeping the original structure and level of detail.
5. Keep citations and artifact links byte-for-byte where practical; only human-readable link labels may be translated.
6. Record `translation_of`, source SHA-256, translation SHA-256, translator/model, date and review state in a sidecar manifest.
7. Default review state is `MACHINE_TRANSLATED_UNREVIEWED` until independently checked against the Portuguese source.
8. Translation review may fix translation errors but must not change the historical claim made by the source. Architectural disagreement belongs in findings/lineage, not in the translation.

## Storage

- Historical originals: `corpus/original/`
- English derivatives: `corpus/translations/en/`
- Translation provenance: `corpus/manifests/translations/en/`

Translations are linked from the catalog and thematic READMEs instead of replacing or duplicating source identity.

## Pages requirement

New `pt-BR` packets requesting Pages must include a current English derivative
in the same packet: `article.en.html`, `document-metadata.en.json`, and
`TRANSLATION_MANIFEST.en.json`. All three are declared artifacts. The manifest
uses `schemas/translation-manifest.schema.json`, binds the exact Portuguese
primary artifact and English derivative hashes, and may be machine translated
or human reviewed, but not superseded. Pages projects the English derivative;
the Portuguese evidence remains preserved and authoritative.

Packets already accepted with an editorial decision `decision_version: "1.0"`
remain historical evidence. They are not rewritten; publish a linked English
derivative to remediate them.
