# English Translation Queue

> Queue derived only from materialized source bytes. File Library references without exact bytes never enter this queue.

Ready for EN translation: **0**. Source-language review required: **0**.

| Document | Source language | State | Source path |
|---|---|---|---|

_No materialized documents are currently waiting for English translation._

## Translation execution contract

1. Read the exact materialized source, never a search snippet.
2. Translate under `TRANSLATION_POLICY.md`; do not modernize or reconcile historical claims.
3. Write the EN derivative under `corpus/translations/en/<batch>/`.
4. Create a translation provenance sidecar with source/translation hashes and `MACHINE_TRANSLATED_UNREVIEWED`.
5. Run structural Translation QA before removing the item from this queue.
