# Document ownership and retrieval guide

The Library is a federated catalog and a home for Library-owned knowledge. It
is not a mirror of every document in the ecosystem.

## Where a document goes

| Subject | Canonical repository |
| --- | --- |
| Work graph, task DAG and backlog lifecycle | `tare.tools.backlog-graph` |
| Specification traceability and impact analysis | `tare.tools.specgraph` |
| Dialogue parsing and protocol testing | `tare.tools.dialog-engine` |
| Providers, processes, sandboxes and five-plane runtime | `tare.tools.kernel` |
| Tactical agent loop | `tare.tools.agent-runtime` |
| Ecosystem orchestration, authority and settlement | `tare.tools.os` |
| Experiments tied to local inference campaigns | `tare.tools.local-labs` |
| Ontology, research curation, publication and Library tooling | `tare.tools.library` |

The authoritative external paths and exact revisions are recorded in
[`catalog/FEDERATED_DOCUMENTS.json`](../catalog/FEDERATED_DOCUMENTS.json).

Repository identities are explicit names, optionally namespaced (for example,
`acme.billing` or `acme/billing`); they do not require the `tare.tools.` prefix.
Ownership metadata preserves these identities, and retired-source provenance
uses the source catalog's recorded repository name.

Validate catalog structure with `python -m tools.federated_documents --root .`.
To verify content too, supply one `--owner REPOSITORY=PATH` argument for every
owner in the document catalog. Verification reads each path from its recorded
Git commit and checks SHA-256 against those exact blob bytes. A working copy's
LF/CRLF conversion must not redefine the pinned document identity. The verifier
does not fetch repositories or modify their files.

New documents created directly in their owner repository use
`migration: owner-origin` and an empty `retired_library_paths` list. They never
had a Library payload to retire. Existing migrations must retain their actual
retired paths; `owner-origin` cannot claim historical aliases. Both cases still
require a full Git revision, canonical path and exact blob SHA-256.

The SpecGraph completion contracts add 18 SpecGraph-owned and two OS-owned
pointers through qualification branches. Their bodies remain in those owners.
The pinned commits identify documentation snapshots, not implementation
releases, main-branch adoption, executed acceptance criteria or attestation.
Catalog metadata availability also does not imply that a consumer read the
body or passed its owner's source-admission checks.

Exact manifest copies produce one payload per SHA-256 with ordered
`source_paths` and consolidation counts in `projection_receipt`. This preserves
individual source identities and does not resolve competing declared authority.

## Editorial authority in the manifest

Local metadata uses the shared EN/PT status vocabulary (`1.1`) in Bookkeeper
and the manifest compiler. YAML frontmatter, inline `**Status:**` and a
`## Status` section are recognized. The source status is preserved, not
replaced with a synthetic `RATIFIED` label.

- Ratified/approved documents and explicit `OWNER_ADOPTED` decisions are
  `DECLARED_ACTIVE`. Owner adoption is not relabelled as Round Table ratification.
- Draft, superseded and other explicitly non-canonical documents are
  `EXCLUDED`, with no selectable target repositories. Exclusion wins over
  canonical markers in composite statuses.
- Missing status on legacy specs, experiments and post-mortems retains
  `UNMANAGED_ACTIVE`; an ADR without declared authority is `EXCLUDED`.
- Unknown statuses block generation and fail the authority audit. A failed
  compilation does not replace the last successfully generated manifest.

Local semantic identity uses explicit `doc_id`/`id`, otherwise the full filename
stem without a content-hash suffix. IDs are normalized to uppercase; a bare ADR
number is not substituted for that full identity. Different active bytes with
the same identity and target repository block generation. Federated owner
identities remain repository-qualified, and their `REPOSITORY_OWNED` marker is
catalog provenance, not a parsed editorial status or a new ratification.

Byte-identical sources remain one payload with their individual authority
states preserved. The transport path does not determine authority or the
active semantic identity. `canonical_ssot_count` counts declared-active
payloads rather than every file found in an ADR/spec directory.

## Search behavior

Normal search reads active Library-owned documents once per unique content
hash:

```powershell
python -m tools.query --search "CAS"
python -m tools.indexer.embed_corpus --root .
```

Historical snapshots and archives are deliberately opt-in:

```powershell
python -m tools.query --search "old decision" --include-history
python -m tools.indexer.embed_corpus --root . --include-history
```

To find an externally owned payload, consult the federated catalog and open
the recorded repository, path and revision. Do not copy it back into Library.

## Explicit federated vector indexing

The incremental indexer accepts `--federated` only with repeated
`--owner-root REPOSITORY=PATH` selections for the catalog owners. There is no
sibling-checkout discovery. It reads and verifies pinned Git blobs before
removing stale rows; an unavailable selected owner or hash mismatch refuses
the run and preserves previously indexed rows. Real indexing remains subject
to the workstation/offload policy in AGENTS.md.

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
