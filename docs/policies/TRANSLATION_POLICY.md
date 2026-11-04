# Translation policy

The repository is written in English: code, comments, prompts, documentation, decisions and research. The only
Portuguese file is `README.pt-BR.md`, a faithful mirror of `README.md` for Brazilian readers; update it whenever
`README.md` changes.

When research written in another language is added, translate it into English in place before it is committed.
A translation:

1. keeps every claim, hedge, status marker (`CURRENT`, `TARGET`, `PROPOSED`, `RESEARCH`), date, number, citation,
   URL, identifier, hash and code block;
2. does not correct, reconcile or modernize the research while translating it; disagreement belongs in a new
   document, not in the translation;
3. keeps project nouns (`TaskEnvelope`, `ExecutionBinding`, `Authority`, `Permit`, `EffectReceipt`, ...) unchanged;
4. keeps the document structure (headings, tables, lists, HTML sections and ids).

A translation never gains architectural authority. In a conflict about current or target architecture, the owner
repository's code, decisions and specifications win over any research text.

The Library no longer keeps separate original-language copies, translation sidecars or translation queues; those
belonged to the imported historical corpus deleted on 2026-11-03.
