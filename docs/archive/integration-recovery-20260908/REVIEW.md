# Disposition of pending Library branches

Status: **HISTORY_ONLY**. Authority: **NONE**. Recovery grants no editorial
approval, architecture authority or execution evidence.

## Distinct Library research

`RECOVERY.json` lists exact source repository, commit, path and SHA-256 for
84 recovered files (279,659 bytes): 17 V1/compaction files and 67 V2 files.
Original text is unchanged, including original claims and caveats. V1 records
and eight synthesis candidates are under `semantic-curation-v1/`; later
authored preservation editions are under `semantic-curation-v2/`. Two proposed
compaction receipts are under `corpus-compaction/`. No deletion is replayed.

The branches `agent/pages-incumbent-retirement` and
`agent/semantic-preservation-curation-v2` point to the same source commit
`eddf901`; their research is recovered once. `V2_DISPOSITION.json` records
every source-side changed path, nine existing LF-equivalent files, newly
recovered files and excluded old controls/presentation. Current federated
ownership and the closed read-only Pages projection supersede those old
repository controls operationally; their Git identities remain recorded.
Old AGENTS instructions, workflows, publisher scripts, root layouts and
proposed deletions are not replayed.

## Attempted publication branches

`PUBLICATION_COMPARISON.json` compares inspected historical publication
artifacts with current `docs/research/` counterparts where they exist.
Eight of ten comparable HTML bodies have equal visible text after the
explicit presentation normalization recorded there. This is **not byte
equivalence**; both SHA-256 values remain distinct. These eight bodies are
not duplicated here. Different editorial/translation receipts describe
older publication attempts and do not establish new approval.

Two microkernel HTML bodies are different historical editions. They and
seven attempted publication packets lacking a current counterpart are
assigned to technical owners for separate history-only recovery: OS
(ecosystem decisions, audit and microkernel), SpecGraph (ADR-044) and
Backlog Graph (ADR-046 and its study). The implementer-profile draft also
belongs to OS. Separate receipts preserve their exact original claims.

The SpecGraph archive was merged through
[SpecGraph PR #3](https://github.com/augusto-scarvalho/tare.tools.specgraph/pull/3)
from head `b871462`; its eight source files are under
`docs/archive/integration-recovery-20260908/adr-044_specgraph_north_star_universal_project_intelligence-2026-08-18/`.
Backlog Graph's 16 source files were merged through
[Backlog Graph PR #2](https://github.com/augusto-scarvalho/tare.tools.backlog-graph/pull/2)
from head `02e3836`, under the corresponding `adr-046_backlog_graph_north_star-2026-08-18/`
and `study_backlog_graph_topological_execution_engine-2026-08-18/` directories
below the same archive prefix. Each package includes `RECOVERY_RECEIPT.json`.
These locators support explicit historical retrieval; no active catalog
entry or authority promotion is implied. OS package integration is tracked
separately by that owner.

The hierarchical-planning article bytes are already present; historical
publication/decision records differ as recorded in the comparison. Existing
current projections remain authoritative for location.

## Integrated mechanisms and retrieval

PR #83 integrated the pending indexer and reconciled the useful hook and
changelog-guard delta from PR #76. Newer federated projection and Bookkeeper
behavior supersedes its central-copy approach. PR #76 was closed with its
tested successor linked; no branch was deleted.

The existing `docs/archive/` boundary excludes this packet from default
lexical/vector selection and active manifest promotion. `--include-history`
is explicit. Historical links refer to the old layout and are resolved via
recorded Git commits rather than rewritten to pretend current availability.

Verify bytes against `RECOVERY.json`, then use the existing catalog
validators, manifest compiler and Bookkeeper. No embeddings, LLM, GPU job,
publisher or frozen Harness is needed for that verification.

Bookkeeper passes SSOT and tombstone checks. It reports three similarity
pairs: two pre-existing pairs and the V1/V2 `SELECTED_EVIDENCE.md` versions
at 94.41% similarity. Those bibliographies have distinct source bytes and
remain explicitly historical versions. Original Markdown hard-break spaces
are preserved even when `git diff --check` reports trailing whitespace.
