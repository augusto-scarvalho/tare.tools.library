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
