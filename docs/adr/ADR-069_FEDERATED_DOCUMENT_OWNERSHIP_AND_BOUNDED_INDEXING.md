# ADR-069: Federated document ownership and bounded indexing

- **Status:** `OWNER_ADOPTED`
- **Decision date:** 2026-09-02
- **Authority:** explicit Human Operator direction
- **Scope:** document location, catalog identity and default retrieval scope

## Context

The Library accumulated editable copies of specifications, ADRs, operating
guides and historical material owned by other `tare.tools` repositories. Both
the lexical and vector paths could rediscover those copies, so agents spent
context on the same bytes more than once and document IDs such as `ADR-001`
became ambiguous across repositories.

## Decision

1. A document's editable payload lives in the repository that owns its subject.
2. The Library stores a machine-readable pointer in
   `catalog/FEDERATED_DOCUMENTS.json`, not a second editable payload.
3. Cross-repository identity is the tuple `(repository, canonical_path,
   revision, canonical_sha256)`. A filename or bare ADR number is not a global
   identity.
4. Default lexical and vector indexing includes active Library-owned Markdown
   and collapses equal SHA-256 payloads to one path.
5. `docs/archive/**` and `catalog/corpus/**` are immutable history and are
   indexed only when `--include-history` is explicitly requested.
6. Generated catalog projections are not document payloads and are excluded
   from the default embedding corpus.
7. A Library copy may be retired only after its owner path, full Git revision
   and SHA-256 are recorded and the owner repository has passed CI.

This decision changes the repository-location rules in ADR-051, ADR-052 and
ADR-067. Those earlier records remain available through the federated catalog
and Git history; they are not silently rewritten.

## Ownership boundary

- Runtime, API, CLI and tool-specific specifications belong to that tool.
- Ecosystem orchestration and shared operational governance belong to
  `tare.tools.os`.
- Library research methods, ontology, curation, publication policy and the
  Library's own implementation remain here.
- Historical snapshots remain immutable but outside normal retrieval.

## Verification

```powershell
python -m tools.federated_documents --root .
python -m tools.build_manifest --root .
python -m pytest -q
```

The validator fails if a retired path still exists, an identity is duplicated,
a pin is not a full commit or a digest is not a lowercase SHA-256.
