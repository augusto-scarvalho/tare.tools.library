# Assurance Topology — Regression Treasury → Evidence Acquisition

**Status:** `RESEARCH / ACTIVE / PEER-REVIEW DRAFT`  
**Data de corte:** 2026-08-13  
**Bounded context primário:** Validation / Assurance  
**Relacionados:** Evidence / Provenance; Observability / Economics / Resources; Project / Workspace  
**Autoridade:** pesquisa; não ratifica TARGET e não altera o repositório canônico.

## Problema

O caso operacional BASELINE-CI / CI-REGRESSION-01 revelou que o treasury histórico de scenarios está sendo usado simultaneamente como regression suite de PR, conformance, platform qualification, NOT_CURRENT evidence, reliability/fault injection e system/integration assurance. O problema não é “ter testes demais”: é uma topologia que trata evidence producers semanticamente diferentes como um único agregado bloqueante.

A hipótese do dossiê é preservar o treasury como especificação executável do stable incumbent e evoluir por retrofit para **Evidence Acquisition**: claims e Evidence Families obrigatórias determinam o piso de assurance; candidate impact, platform e custo determinam quando/onde produzir a evidência. Modelo/router/reputation nunca podem reduzir o piso determinístico.

## Dossiê

1. [Evidência empírica e diagnóstico](01-empirical-evidence.md)
2. [Arquitetura proposta e migração](02-proposed-assurance-topology.md)
3. [Programa experimental, falsificadores e peer review](03-experiment-peer-review.md)

## Research questions

- RQ1 — o treasury atual mistura evidence classes a ponto de aumentar custo/false blocking sem força proporcional de assurance?
- RQ2 — classificar evidence producers por claim/family/layer/platform/hermeticity/determinism reduz time-to-trust preservando failure detection?
- RQ3 — um GatePlan determinístico baseado em risk/policy + impact + mandatory Evidence Families pode operar em shadow sem transferir Authority ao router/modelo?
- RQ4 — quais producers pertencem a PR, promotion, qualification, reliability/scheduled e release?
- RQ5 — a mudança reduz corrective burden e fixture-aging, ou apenas desloca failures para mais tarde?

## North Star mapping

```text
deterministic Authority/Assurance policy
        ↓ mandatory evidence floor
candidate + impact + runtime/platform facts
        ↓
reconstructable GatePlan
        ↓
evidence producers
        ↓
OutcomeEvidence / sufficiency
        ↓
authorized decision
```

O objetivo econômico não é minimizar quantidade de testes. É **minimizar tempo/custo até existir evidência suficiente para uma decisão autorizada**, preservando fail-closed behavior, cross-platform obligations, negative evidence e rollback.

## Estado epistemológico

`PEER_REVIEWABLE_DESIGN_DRAFT_WITH_ACTIVE_EMPIRICAL_CASE`

Não afirmar ainda que selective testing é production-safe no tare.tools, que lane splitting reduz regressões, que CI-REGRESSION-01 já está settled enquanto seu corrective roda, ou que green CI implica strict proof.
