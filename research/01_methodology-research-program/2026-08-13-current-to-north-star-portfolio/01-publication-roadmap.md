# Publication roadmap — trabalhos estruturantes desta sessão

**Status:** `RESEARCH / PUBLICATION PLANNING`  
**Parent:** [CURRENT → North Star portfolio](README.md)

## 1. Princípio editorial

Nem todo implementation train vira paper. Publicar quando o episódio produz uma pergunta generalizável, um treatment/contrast identificável, provenance suficiente e negative evidence que permita falsificação.

Internal operational evidence pode iniciar um case study, mas não deve ser apresentado como causal benchmark sem matched controls/replication.

## 2. Linha A — ImplementerProfile / bounded autonomy

**Já ativa:** estudo longitudinal + Evidence Annex em `research/01_methodology-research-program/`.

Próximo evidence point: CI-REGRESSION-01 somente após settlement independente. O interesse científico é transferibilidade de A2 para Validation/Assurance, corrective responsiveness e cost-to-trust — não “Fable ganhou do Sonnet”.

Para peer review: matched packet, Fable low×higher effort, second reviewer coding, token/time/audit-cost instrumentation e task-class replication.

## 3. Linha B — Regression Treasury → Evidence Acquisition

**Nova:** dossiê em `research/08_validation-assurance/2026-08-13-assurance-topology/`.

Empirical seed: PR #16 / Issue #17. Publicação deve combinar incident report + design proposal + shadow experiment. Métricas: failure recall, time-to-required-evidence, runner-minutes, flake, corrective burden, EvidenceFamily coverage.

Candidate title: *From Regression Treasury to Evidence Acquisition: Designing Promotion-Safe Assurance for an Agent Operating System*.

## 4. Linha C — Negative evidence is not candidate regression

Technical note menor e potencialmente publicável separadamente.

Pergunta: como preservar deliberate failing tests/qualification evidence sem normalizá-los para PASS nem confundi-los com candidate regressions?

Contribution candidate: two-channel negative evidence + reviewed blocking policy + fail-closed declaration/policy consistency + candidate-policy authority caveat.

Requer: independent threat model, mutation/falsifier suite e comparação com xfail/skip/quarantine practices sem alegar novidade prematuramente.

## 5. Linha D — Governed semi-cyclic Relay

Usar Relay Q0–Q8 como longitudinal systems case study somente quando houver stable activation evidence.

Outcomes interessantes:

- human interruptions/train;
- owner effect authorizations;
- ambiguous launch/recovery events;
- evidence latency;
- corrective loop latency;
- vendor/runtime substitution;
- authority escalations;
- cost-to-trust.

Research claim possível: transport automation pode reduzir coordination burden sem converter message bus/model em Authority quando exact subject identity, bounded envelopes, durable attempt reconciliation e independent settlement permanecem externos.

## 6. Linha E — Durable Task/Run/Work identity retrofit

Q8 oferece seed, mas publicar após promotion/replay evidence.

Pergunta: como introduzir durable execution identity em um incumbent sem criar WorkRegistry/ExecutionAttempt paralelo?

Design pattern: operational TaskStore + first-class RunEnvelope + derived Work projection + later canonical lineage adapters.

Requer cross-run replay/reconstruction e evidence de que projections permanecem derivadas/single-writer-safe.

## 7. Linha F — Trusted Judge / candidate-evaluator-promoter separation

Conectar a arqueologia FSV/Judge Provenance, `TRUSTED_INVOCATION_SEAM_MISSING`, candidate tree scenario enumeration e promotion incidents.

Pergunta central:

> como um agentic developer tool prova propriedades sobre um candidate quando parte do próprio validation stack pode ser candidate-controlled?

Não publicar strict-proof claims antes de trusted invocation, filesystem confinement/Genesis prerequisites e independent security review apropriados.

## 8. Linha G — CURRENT→North-Star prioritization

Este próprio portfolio é uma design-science artifact.

Potential contribution: priorizar não pelo valor isolado da feature, mas pelo **multiplicative reduction in time-to-trust** de descendants, mantendo hard safety/authority constraints.

Para validar: comparar throughput/corrective burden antes/depois da estabilização de Assurance; estudar queueing/WIP; registrar tasks que foram reordenadas e outcomes. Se não houver efeito mensurável, manter como engineering method, não research claim.

## 9. Linha H — Research repository as evidence-connected architecture memory

A evolução do `tare.tools.research` também pode virar systems/research-method case:

- raw source preservation;
- provenance sidecars;
- historical vs current authority;
- rehydration queue;
- active derived studies;
- Findings→ADR handoff;
- peer-review evidence annexes.

Publicar somente após demonstrar reconstruction/review workflows e evitar confundir corpus graph com architectural authority.

## 10. Linha I — Decoupled Microkernel Architecture (5 Planes) & Tripartite Dialectic Deliberation (ADR-042)

**Publicação Canônica Ratificada:** [`research/02_harness-architecture/2026-08-17-decoupled-microkernel-5-plane-architecture-study.md`](../../02_harness-architecture/2026-08-17-decoupled-microkernel-5-plane-architecture-study.md).

Formalização da superação do "núcleo único monolítico" em prol do Microkernel Desacoplado em 5 Planos (`Experience`, `Control`, `Data`, `Compute`, `Assurance`), incorporando:
- Invariantes de Fencing Monotônico (`lease_epoch`) e Single-Writer estrito no Data Plane;
- Classificação CP estrita com Transactional Landing Journal (WAL) reconciliando Git & Grafo;
- Landing Queue (Merge Train) com rebase semântico delta anti-starvation;
- Recibo Criptográfico Expandido vinculando `candidate_tree_hash` e digest do sandbox;
- Motor de Mesa Redonda com protocolo dialético FSM como oráculo tripartite de consenso.

## 11. Prioridade editorial

1. **Decoupled Microkernel 5-Plane Architecture (Linha I)** — ratificado por consenso tripartite da Mesa Redonda e publicado como estudo canônico;
2. continuar ImplementerProfile longitudinal porque já possui protocol/evidence;
3. Assurance Topology porque existe um natural experiment/incident ativo;
4. Negative Evidence note como spin-off curto após CI settlement;
5. Trusted Judge quando houver novo implementation evidence;
6. Relay e Task/Run/Work após promotion/activation evidence;
7. Portfolio method após dados de before/after time-to-trust;
8. Evolution/memory somente depois de evidence backbone mais maduro.

## 12. Release criteria para qualquer paper/draft externo

- provenance de internal evidence;
- reproducible/sanitized artifacts ou disclosure claro de access limitation;
- negative results;
- CURRENT×TARGET labels preservados;
- threats to validity;
- second review quando o autor também foi auditor/designer;
- bibliografia primária e bleeding-edge separadas;
- no vendor/model leaderboard causal sem matched experiment;
- no architecture claim promoted por recency do research document.
