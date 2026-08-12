# Semantic Curation Ledger — 2026-08-12

**Branch:** `agent/semantic-research-curation-v1`  
**Historical parent:** `7ad1a71ebbad99e69bd6ba97b2ed29d78faf08de`  
**Frozen bootstrap anchor:** `bootstrap-v0.19.0`

## 1. Why this curation exists

The previous corpus mixed substantive research, old repo snapshots, chat dumps, translations, format-only HTML, generated indexes, implementation drafts, forensics and real experiments. Structural automation made the collection navigable but did not decide what knowledge still deserved to be live.

This pass uses **semantic disposition**. Git is the archive; HEAD is the library.

## 2. Disposition vocabulary

- `LIVE STUDY` — rewritten/merged into a current high-density study.
- `EXPERIMENT` — empirical result remains directly readable.
- `ABSORBED` — ideas retained in a stronger successor; source becomes HISTORY ONLY.
- `RETIRE` — superseded, redundant, procedural or low-value for current reading.
- `OPEN` — unresolved claim retained in Research Frontier.

## 3. Historical 93-file snapshot

The entire exact 2026-08-05 snapshot is **HISTORY ONLY** in the new live tree. Its knowledge was reviewed by thematic lineage, not blindly discarded.

### Agent OS / architecture → Study 01

ABSORBED: `RESEARCH.md`, `acceptance-authority-proposals.md`, `conformance-selfassessment.md`, `harness-reference-architecture-adoption.md`, `sources/adaptive-project-oriented-multi-agent-harness-architectures.md`, `naming-round.md`.

### Governed work / effects / reliability → Study 02

ABSORBED: `dynamic-workflows.md`, `pipeline-metamodel.md`, `backlog-dependency-graph-round.md`, `backlog-dependency-graph-implementation-plans.md`, `loop-workflow-efficiency-evidence.md`, `loop-workflow-efficiency-round.md`, `defect-decide-materialize-bridge.md`, `rd-crash-adapter-boundary.md`, `rd-crash-injection-round.md`, `rd-crash-implementation-plans.md`, `plan-exp21-crash-injection-DRAFT.md`, `plan-job-lifetime-DRAFT.md`, `plan-job-tree-lifetime-control.md`, `plan-proc-cancel-op-sweep.md`, `race-mode-test-1.md`, `ptc-round.md`, `ptc-implementation-plans.md`, `forensics-2026-07-24-postcommit-blocking-commit.md`, `forensics-2026-07-25-codex-applypatch-split-writable-roots.md`, `exp21-p1-orphan-probe-2026-07-27.md`.

### Governance / assurance / quality → Study 03

ABSORBED: `code-quality-agents.md`, `code-security-agents.md`, `audit-playbook-injection-surfaces.md`, `audit-playbook-metrics-baseline.md`, `audit-quorum-dinamico.md`, `construct-metrics.md`, `truth-reconciliation-round.md`, `truth-reconciliation-implementation-plans.md`, `gate-phase2-safety-round.md`, `gate-surface-definition-2026-07-26.md`, `gate-perf-fail-fast-2026-07-16.md`, `w29-evidence-gated-assurance-round.md`, `semantic-finding-dedup.md`, `opus-overseer-quality-2026-07-23.md`.

### Runtime / protocols / isolation → Study 04

ABSORBED: `agent-communication-protocols.md`, `harness-own-sandbox.md`, `exp20-three-lane-design.md`, `plan-gate-browser-lane-DRAFT.md`, process/job-lifetime material shared with Study 02, and protocol/runtime research that followed the snapshot.

### Routing / economics / observability → Study 05

ABSORBED: `nvidia-smart-models.md`, `observability-generative.md`, `vendor-credit-tracking-log.md`, `rd-u-utility-function-round.md`, `rd-u-implementation-plans.md`, `spawn-cost-governance-round.md`, `spawn-cost-governance-implementation-plans.md`, `plan-local-model-config-DRAFT.md`, `reckon-efficiency-round.md`.

### Context / playbooks / learning → Study 06

ABSORBED: `memory-context-management.md`, `estudo-governanca-contexto-v2.md`, `adocao-governanca-contexto.md`, `compaction-round.md`, `compaction-implementation-plans.md`, `event-log-integrity-under-compaction.md`, `guia-playbooks-engineering-2026-07-29.html`, `playbook-hierarchy-refinement-2026-07-23.md`, `playbook-inheritance-article-2026-07-23.md`, `playbook-inheritance-round-2026-07-23.md`, `rd-taint-camel-round.md`, `rd-taint-implementation-plans.md`.

### Experience / UI → Study 07

ABSORBED: `agent-gui-cli-features.md`, `ide-embedded-gui.md`, `ide-shard-refinement-2026-07-23.md`, `nielsen-genai-agent-ux.md`, `ux-agents-consolidated-2026-07-13.md`, `ux-agents-consolidated-analysis.md`, `ux-ui-generative.md`.

### Research methodology → Study 08

ABSORBED: `deep-research-pipelines.md`, `experiment-result-format.md`, `article-coverage-backlog.md`, `empirical-pin-verification-2026-07-23.md`, `weekly-monitor-w28-code-quality-extract.md`, `weekly-monitor-w28-dynamic-workflows-extract.md`, `weekly-monitor-w28-memory-extract.md`, `weekly-monitor-w28-multiagent-extract.md`, `graph-round2-ideation-divergence.md`, `ideators-graph-refresh-queue-round1.md`.

### Pure implementation/backlog artifacts → RETIRE from research HEAD

`backlog-groom-2026-07-18.md`, `backlog-groom-2026-07-21.md`, `backlog-groom-2026-07-22.md`, `backlog-groom-2026-07-22b.md`, `backlog-groom-2026-07-22-windown.md`, `backlog-groom-2026-07-23.md`, `backlog-groom-2026-07-29.md`, `baseline-delegations-frozen-2026-07-30.json`, `lq7-implementation-briefs.md`, `plan-backlog-json-canonical-DRAFT.md` and other one-off implementation drafts are recoverable from Git but are not living research.

## 4. 2026-08-11 Scientific Refresh generation

- Nine scientific refreshes: `ABSORBED`. Their thematic syntheses informed Studies 01–08.
- Nine implementation-research deltas: `RETIRE`. They duplicated generic invariants, S0–S6 migration and Packet A/B/C/D structure with insufficient problem-specific value.
- Cross-lineage synthesis: `ABSORBED`. Its canonical spine survives mainly in Study 01 and the cross-study Findings ledger.
- 186 bilingual editorial HTML renderings + editorial QA/indexes: `RETIRE`. They were presentation/translation projections of historical sources.

## 5. 2026-08-10/12 deep research packs

- Canonical Lineage / Identity: `ABSORBED` into Studies 02 and 06; identity-as-lineage finding retained.
- Demand Lineage / Context / Learning: `ABSORBED` into Studies 02 and 06.
- Information Survival / Reconstructability: `ABSORBED` into Study 02 and repo policy.
- Reliability / Effect Reconciliation: `ABSORBED` into Study 02; Effect Torture Lab remains OPEN.
- Governance Assurance & Audit: `ABSORBED` into Study 03; metrology/control-effectiveness findings retained.
- Interoperability / technology landscapes: `ABSORBED` into Study 04.
- Workflow as Governed Work: `ABSORBED` into Study 02.
- Adaptive Routing/Reputation: `ABSORBED` into Study 05.
- Context/Memory/Playbooks and Evolution: `ABSORBED` into Study 06.
- Experience/TUI/REPL + NLU reconstruction: `ABSORBED` into Study 07.
- Research methodology/CMRP: `ABSORBED` into Study 08.

## 6. Experiments

- Local AI Lab recurrent-memory line: `EXPERIMENT`; retained as a dedicated consolidated document because it contains empirical results/falsifications independent of Agent OS architecture.
- Implementation-session transcripts/forensics: `HISTORY ONLY` unless a future empirical study extracts a durable dataset from them.
- Implementer Profiles seed study: `OPEN FOR INGESTION`; worth a future dedicated experiment document after its episode ledger is reconciled, rather than copying the current File Library artifact blindly.

## 7. Large/raw repository material

`corpus/`, `canonical-references/`, `archaeology/`, `editorial-editions/`, `refresh-editions/`, translation trees, source bundles, ZIPs, chat dumps, sidecars, generated graphs/indexes and mechanical QA reports are `HISTORY ONLY` after this curation. They remain reachable through the parent commit/tag and are not duplicated into an `/archive` directory.

## 8. Known incompleteness

This is a semantic curation candidate, not a claim that every external citation was reverified on 2026-08-12. The living studies explicitly inherit external-source evidence from the reviewed research lineages. A later source-freshness pass may update bibliographies without changing this curation decision automatically.
