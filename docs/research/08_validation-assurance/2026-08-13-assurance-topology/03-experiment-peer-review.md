# 3 — Programa experimental, falsificadores e peer review

**Status:** `RESEARCH / PROSPECTIVE PROTOCOL`  
**Parent:** [Assurance Topology](README.md)

## Hipóteses

- **H1:** evidence-qualified selection reduz median time-to-first-actionable-failure sem reduzir recall dos failures materialmente relevantes do CURRENT corpus.
- **H2:** separar qualification/reliability de ordinary PR regression reduz false blocking por nondeterminism sem apagar negative evidence.
- **H3:** metadata de ownership/hermeticity/determinism reduz corrective burden ao revelar fixture debt antes de cross-platform promotion.
- **H4:** mandatory Evidence Families oferecem um piso de assurance mais robusto que “execute todos os arquivos do diretório”.
- **H5:** scheduling por critical path/time-to-trust melhora promotion throughput mais que otimizar apenas duração total da suíte.

## Design inicial

**Baseline:** `CURRENT_FULL` — topologia histórica completa.  
**Treatment:** `SHADOW_EVIDENCE_PLAN` — mesma exact candidate identity, GatePlan read-only, sem autoridade sobre o verdict.

Dataset inicial deve incluir commits/PR states verdes e vermelhos, BASELINE-CI, CI-REGRESSION fixture debt, NOT_CURRENT evidence, platform-specific failures, fault/timing failures, Authority/Capability/runtime boundary changes e docs-only/low-risk changes.

Registrar por subject:

- exact commit/tree;
- changed surfaces;
- GatePlan version;
- selected/deferred evidence producers e justification;
- mandatory Evidence Families;
- CURRENT outcomes;
- shadow outcomes;
- OS/runtime identity;
- duration/cost;
- first actionable failure;
- final independent audit/promotion decision.

## Falsificadores

Rejeitar/enfraquecer a proposta se:

1. GatePlan não seleciona antes da decisão um failure histórico que deveria protegê-la;
2. lane split aumenta escaped regressions;
3. stale/missing Graph metadata consegue reduzir mandatory floor;
4. unknown metadata compra skip/nonblocking;
5. candidate consegue auto-classificar um CURRENT regression como harmless evidence;
6. cross-platform bugs aparecem sistematicamente apenas no full-suite depois de retirados do PR path;
7. planner overhead supera o tempo/evidência economizados;
8. reviewers não conseguem explicar deterministicamente seleção/deferment.

## Outcomes

Primários:

- historical/prospective failure recall;
- false-negative / escaped-regression rate;
- time-to-required-evidence;
- time-to-promotable-state / time-to-trust;
- runner-minutes / cost-to-trust.

Secundários:

- flake/nondeterminism rate;
- duplicate/wasted evidence;
- platform coverage;
- explanation coverage;
- corrective burden.

## Peer review / independence

O auditor/autor desta linha participou da criação da taxonomy e da investigação dos incidents. Antes de claims fortes:

1. congelar codebook;
2. segundo reviewer classifica uma amostra de evidence producers sem participar da implementação;
3. medir/resolver disagreements;
4. reviewer verifica sample de raw CI/run evidence;
5. prospective canary é analisado antes de alterar blocking authority;
6. publicar negative results e escaped failures.

## Threats to validity

- **Construct:** feedback mais rápido pode esconder assurance menor; por isso recall/family coverage são outcomes obrigatórios.
- **Internal:** repo e fixtures evoluem durante o estudo; matched exact-subject replay é preferível.
- **External:** um harness Python/Windows-first não generaliza automaticamente.
- **Researcher coupling:** taxonomy e audit compartilham autor.
- **Instrumentation drift:** CI-REGRESSION-01 está alterando o próprio measurement substrate.
- **Survivorship:** CURRENT full-suite failures não cobrem bugs que nenhuma suíte detecta.
- **Temporal:** runner load pode confundir fault-injection conclusions.

## Literatura e corpus de apoio

1. Spieker, H. et al. (2018). *Reinforcement Learning for Automatic Test Case Prioritization and Selection in Continuous Integration*. arXiv:1811.04122.
2. Abbondante, L.; Canfora, G. (2026). *Commit-Aware Learning-Based Test Case Prioritization for Continuous Integration*. arXiv:2604.25363.
3. Plyusnin, P. et al. (2025). *Targeted Test Selection Approach in Continuous Integration*. arXiv:2509.10279.
4. Sayedsalehi, A.; Rigby, P.; Mierzwinski, G. (2026). *Risk-Aware Batch Testing for Performance Regression Detection*. arXiv:2604.00222.
5. pytest-dev/pytest-xdist — work-stealing scheduler implementation/history.
6. NASA — *Understanding and Evaluating Assurance Cases*.
7. Messick / ETS — construct underrepresentation and construct-irrelevant variance.
8. tare.tools — *Resource Management, Scheduling, Sandbox & Assurance* (2026-08-09), `RESEARCH`.
9. tare.tools — *Assurance & Evolution* (2026-08-09), `RESEARCH`.
10. tare.tools formal research programme v1.6 (2026-07-14), `HISTORICAL/RESEARCH`.
11. tare.tools canonical private repo PR #16 / Issue #17 / GitHub Actions — `INTERNAL OPERATIONAL EVIDENCE`.

## Publication plan

Working title:

> **From Regression Treasury to Evidence Acquisition: Designing Promotion-Safe Assurance for an Agent Operating System**

Versão publicável exige sanitized/reproducible subject dataset, frozen codebook, independent second-review coding, historical replay, prospective canary e publicação explícita de failures/negative evidence.

Claim ceiling atual: **design-science + longitudinal internal case evidence**. Não é ainda benchmark causal nem validação externa.
