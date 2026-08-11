# Chat Translation Workflow

Status: operational contract for this corpus; it is not an Agent OS primitive.

When a historical document becomes byte-materialized and `catalog/TRANSLATION_QUEUE.json` marks it `READY_FOR_TRANSLATION`, a ChatGPT research session may generate the English derivative under these rules:

1. the exact local source is the translation basis;
2. search snippets, summaries, archaeology notes, or later architecture must not fill gaps in the source;
3. preserve headings, claims, uncertainty, CURRENT/TARGET/PROPOSED/RESEARCH labels, URLs, citation tokens, hashes, identifiers and code;
4. preserve historical mistakes/obsolete conclusions as historical claims; record corrections separately in review/findings;
5. store English as a derivative and create the translation sidecar required by `TRANSLATION_POLICY.md`;
6. mark it `MACHINE_TRANSLATED_UNREVIEWED`;
7. run translation QA, navigation, repository validation, and checkpointing.

This allows translation to happen during corpus review without allowing translation to become architectural reconciliation.
