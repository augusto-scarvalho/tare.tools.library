# 2 — Arquitetura proposta e migração

**Status:** `PROPOSED / RESEARCH`  
**Parent:** [Assurance Topology](README.md)

## Princípio

Preservar o Scenario Regression Treasury como especificação executável histórica do stable incumbent, mas deixar de assumir que todo evidence producer precisa bloquear todo PR.

A unidade conceitual passa de “teste” para:

```text
Change / Subject
  -> claims que importam
  -> required assurance
  -> mandatory Evidence Families
  -> evidence producers
  -> sufficiency
  -> authorized decision
```

A menor proof layer capaz de sustentar o claim deve vencer, salvo quando policy exigir families independentes/adicionais:

`static → unit → contract → scenario → system → adversarial → agentic eval → operational evidence`.

## Evidence producer descriptor

Shape de pesquisa; **não é primitive canônica** antes de reconciliation/ADR:

```yaml
id: stable-id
owner_context: ...
claims: [...]
evidence_family: ...
proof_layer: static|unit|contract|scenario|system|adversarial|agentic_eval|operational
subject_scope: ...
change_surfaces: [...]
platform_requirements: [...]
hermeticity: hermetic|host_bound|external
determinism: deterministic|bounded_timing|stochastic
cost_class: cheap|medium|expensive
historical_duration_ms: ...
blocking_policy:
  pr_fast: ...
  pr_impacted: ...
  promotion: ...
  qualification: ...
  reliability_scheduled: ...
  release: ...
provenance: ...
```

Unknown/unclassified metadata permanece dívida visível. Ausência de metadata nunca compra `skip`.

## GatePlan em shadow

```text
Candidate identity
+ changed surfaces (Graph/AST/contracts + source verification)
+ risk/policy floor
+ mandatory Evidence Families
+ platform/runtime capability
+ duration/failure/flakiness history
        ↓
reconstructable GatePlan
```

O GatePlan é projection de obrigação/execução, **não Authority**. Model/router pode futuramente ordenar evidence adicional, mas não reduzir o deterministic policy floor.

## Lanes candidatas

- **PR_FAST** — compile/static/spec/product hygiene e cheap deterministic contracts.
- **PR_IMPACTED** — affected scenarios e platform subset exigido pelo impact/risk.
- **PROMOTION_DETERMINISTIC** — broad deterministic treasury, parity e boundary invariants.
- **QUALIFICATION** — `NOT_CURRENT`, candidate experiments, runtime/model/sandbox qualification.
- **RELIABILITY_SCHEDULED** — fault/process/network/timing evidence e long-running soak quando não adequados ao fast path.
- **RELEASE** — ship/readiness, supply chain e release-specific closure.

“Scheduled” não significa ignored: policy pode exigir esse evidence antes de promotion/release.

## Multi-target sem produto cartesiano

Adotar a distinção já pesquisada:

1. **anchor targets** — always required para classes críticas;
2. **impacted targets** — expandidos por change impact;
3. **sampled/combinatorial targets** — pairwise/risk sampling;
4. **full parity triggers** — Authority, Capability, runtime e contratos canônicos.

Windows continua first-class; Linux/macOS/CI continuam requisitos. A proposta torna explícito quando cada target é claim-relevant.

## Migration — Strangler

**S0 Inventory:** classificar evidence producers, sem mudar execução.  
**S1 Shadow:** produzir GatePlan, CURRENT mega-suite permanece autoridade.  
**S2 Historical replay:** comparar GatePlan vs failures conhecidos.  
**S3 Canary lanes:** lane split em paralelo, com full-suite fallback.  
**S4 Selective PR:** somente após ADR/SPEC + independent review + thresholds prospectivos.  
**S5 Adaptive scheduling:** apenas após telemetry/dataset; policy floor permanece determinístico.

Rollback: switch determinístico retorna à topologia CURRENT enquanto parity/coverage ainda estiverem em qualificação.

## Scheduling / economics

Objetivo:

> **minimizar tempo até existir evidência suficiente para uma decisão autorizada.**

Métricas: time-to-first-actionable-failure, time-to-required-evidence, time-to-trust, assurance queue latency, duplicate/wasted evidence, runner-minutes e cost-to-trust.

Após instrumentação confiável, considerar historical duration/LPT-like ordering → compatible work stealing → resource/evidence-aware priority. Active evidence acquisition permanece pesquisa posterior, não requisito do primeiro GatePlan.

## ADOPT / ADAPT / RETIRE / OPEN

**ADOPT:** treasury histórico, independent audit, fail-closed unknowns, cross-platform qualification, deterministic policy floor.  
**ADAPT:** universal PR treasury → evidence-qualified lanes; OS matrix → anchor/impact/full-parity triggers.  
**RETIRE:** “todo FAIL = candidate regression”, blanket waiver, “todo teste importante bloqueia todo PR”.  
**OPEN:** exact registry/schema, trusted authority para nonblocking policy, shadow exit threshold, impact-graph confidence, placement de intrinsically nondeterministic fault tests.
