# Corpus Review Status

> Review is deliberately split into archival/identity review, translation structural QA, and architectural reconciliation. Translation never implies architectural ratification.

## Current seed review

| Document | Archival placement | Translation | Architectural reconciliation |
|---|---|---|---|
| Programa formal / arquitetura multiagente e roteamento | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Auditoria no tare.tools | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Endpoints e Agentes CLI | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Plano de implementação Google | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Revisão da arquitetura Kimi | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Reliability Semantics | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Task & Workflow Lifecycle | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Protocolos e interoperabilidade | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Resources e containers | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Sessão de implementer 2 | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |
| Testes e gates | `PASS` | `MACHINE_TRANSLATED_UNREVIEWED` | `PENDING_CANONICAL_REPO_RECONCILIATION` |

## Rehydration review

- File Library references discovered: **66**.
- Exact-byte identity crosswalks: **0**.
- Reference-only artifacts still pending materialization: **66**.
- Translation blocked until exact source materialization: **44**.
- Native-English reference artifacts: **22**.
- References with expected SHA-256 constraints from independent manifests: **11** (reported, not locally verified source hashes).
- No reference-only artifact is allowed to claim local source bytes or a locally verified SHA-256.
- Lineage order/version metadata may establish ordering, but semantic supersession requires exact content comparison; see [LINEAGE_RECONCILIATION.md](LINEAGE_RECONCILIATION.md).
- Normalized external-source navigation is generated from materialized originals only; see [SOURCE_INDEX.md](../sources/SOURCE_INDEX.md).

## Interpretation

- `PASS` under archival placement means the item has a stable document ID, byte-preserved source, SHA-256 provenance and bounded-context placement in the catalog.
- Translation state describes the English derivative only. See [TRANSLATION_QA.md](TRANSLATION_QA.md) for machine-checkable fidelity checks.
- `PENDING_CANONICAL_REPO_RECONCILIATION` is intentional: CURRENT/TARGET reconciliation must be performed against the actual canonical repository/Git/specs/gates, not inferred from historical documents or chat summaries.

## Recommended read-only reconciliation order

1. North Star / formal research programme and harness architecture history.
2. Workflow lifecycle and Reliability Semantics.
3. Governance/Audit and Validation/Assurance/tests-gates.
4. Protocols/Interoperability and Runtime/CLI archaeology.
5. Resources/containers and vendor-specific historical studies.
