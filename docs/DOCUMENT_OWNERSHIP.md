# Document ownership and retrieval guide

The Library is a home for Library-owned knowledge and a derived, rebuildable
retrieval index ([ADR-070](adr/ADR-070_LIBRARY_AS_DERIVED_RETRIEVAL_INDEX.md)).
It is not a mirror of every document in the ecosystem, and it is never an
authority for grounding.

## Where a document goes

| Subject | Canonical repository |
| --- | --- |
| Work graph, task DAG and backlog lifecycle | `tare.tools.backlog-graph` |
| Specification traceability and impact analysis | `tare.tools.specgraph` |
| Providers, processes, sandboxes and five-plane runtime | `tare.tools.kernel` |
| Tactical agent loop | `tare.tools.agent-runtime` |
| Ecosystem orchestration, authority and settlement | `tare.tools.os` |
| Experiments tied to local inference campaigns | `tare.tools.local-labs` |
| Research curation, publication and Library tooling | `tare.tools.library` |

A document stays in its owner's tree. The Library keeps no copy, catalog entry,
pin or manifest for it: to read it, open the owner repository at its path.

In the index, an owner document is `repository:path`. Repository identities are
explicit names, optionally namespaced (for example, `acme.billing` or
`acme/billing`); they do not require the `tare.tools.` prefix.

## Editorial status

The Bookkeeper audit (`python -m tools.bookkeeper.cli audit --root docs`) reads
Library-owned decisions and specifications with the shared EN/PT status
vocabulary (`1.1`). YAML frontmatter, inline `**Status:**` and a `## Status`
section are recognized, and the source status is never rewritten.

- Ratified/approved documents and explicit `OWNER_ADOPTED` decisions count as
  canonical. Owner adoption is not relabelled as Round Table ratification.
- Draft, superseded and other explicitly non-canonical documents do not count.
  Exclusion wins over canonical markers in composite statuses.
- Unknown statuses fail the audit, and so do different active bytes with the
  same explicit identity. Byte-identical copies are not a conflict, and a bare
  ADR number never merges two different full filename stems.

## Search behavior

Normal search reads active Library-owned documents once per unique content
hash:

```powershell
python -m tools.query --search "CAS"
python -m tools.indexer.embed_corpus --root .
```

The repository no longer tracks history, but the tools still treat
`docs/archive/**` and `catalog/corpus/**` as history that a local checkout may
hold; reading it is opt-in:

```powershell
python -m tools.query --search "old decision" --include-history
python -m tools.indexer.embed_corpus --root . --include-history
```

## Indexing owner checkouts

The incremental indexer reads another repository's documents only from a
checkout passed as `--owner-root REPOSITORY=PATH`; repeat the flag per
repository. There is no sibling-checkout discovery. It indexes the checkout's
tracked Markdown (`git ls-files`) as it is on disk, with the same history and
generated-catalog exclusions, and anchors concepts from the owner's
`ontology/domain_ontology.yaml` when it has one. A run removes stale rows only
for the roots it read; an unavailable checkout refuses the run before any row
is removed. Real indexing remains subject to the workstation/offload policy in
AGENTS.md.

```powershell
python -m tools.indexer.embed_corpus --root . --owner-root tare.tools.os=../tare.tools.os
python -m tools.query --concept CASPersistence --owner-root tare.tools.kernel=../tare.tools.kernel
```

Configure remote embeddings explicitly with `LOCAL_EMBED_ENDPOINT`; the
default remains localhost. The current model namespace is
`qwen3-embedding-4b`. Index and query must select the same model family;
quantization changes do not establish equivalence automatically. Ontology
anchors carry document identity and owner-scoped ADR/SPEC references. Changing
the combined selected ontology digest conservatively invalidates that run's
documents; this does not promise selective per-concept invalidation.

Failed or incomplete embedding batches are stored as explicitly pseudo,
upgradeable rows, never as real embedding evidence. Namespaces coexist in
SQLite and legacy rows survive migration. These are retrieval annotations,
not proof that a specification was implemented or that an acceptance
criterion passed.
