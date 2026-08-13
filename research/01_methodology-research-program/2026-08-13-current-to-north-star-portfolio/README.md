# CURRENT → North Star — portfolio orientado a time-to-trust

**Status:** `RESEARCH / ACTIVE / DESIGN-SCIENCE ROADMAP DRAFT`  
**Data:** 2026-08-13  
**Escopo:** metodologia de priorização e sequencing do backlog tare.tools  
**Autoridade:** pesquisa. A ordem operacional proposta só se torna canônica via TaskStore/Architecture/ADR/SPEC no repositório principal.

## 1. Problema

O tare.tools possui muitas linhas arquiteturais válidas em paralelo. A otimização ingênua seria maximizar quantidade de features fechadas. A hipótese deste draft é que isso é subótimo enquanto a esteira de validation/promotion/evidence ainda produz alta corrective burden.

Objetivo de portfolio:

> **minimizar time-to-trust e cost-to-trust de CURRENT até a North Star, sujeito a Authority, safety, evidence, portability, rollback e stable-incumbent compatibility como hard constraints.**

Isso transforma “qual feature vem depois?” em “qual mudança reduz mais o custo/risco de qualificar todas as mudanças posteriores?”.

## 2. North Star como função de restrição

```text
probabilistic interpretation
+ dynamic planning
+ durable execution
+ deterministic authority
+ capability-mediated effects
+ evidence-driven learning
+ conservative evolution
```

A priorização não pode adiantar adaptation/memory/evolution se os mecanismos que limitam autoridade, provam efeitos e qualificam outcomes ainda forem circulares ou ambíguos.

## 3. Critical-path portfolio

```text
P0.0 truthful incumbent promotion
   ↓
P0.1 Assurance Topology / Evidence Acquisition
   ↓
P0.2 Trusted Judge / promotion provenance
   ↓
P0.3 Capability/Effect + reliability closure
   ↓
P1.0 Durable Work + Evidence backbone
   ├──────────────┐
   ↓              ↓
P1.1 Relay       P1.2 Routing/ExecutionBinding shadow
   └──────┬───────┘
          ↓
P2 Adaptive Assurance/Resources + Reputation/Qualification
          ↓
P3 Memory / Experience / Evolution Control
```

A ordem é dependency-oriented, não um julgamento de valor de produto.

### P0.0 — truthful promotion

Finish active CI corrective, promote accepted baseline through protected PR only after exact-head evidence, then re-evaluate Q7/Q8 on the repaired baseline. Enquanto promotion evidence estiver ambígua, novos broad feature trains aumentam rebase/audit debt.

### P0.1 — Assurance Topology

Transformar o mega-treasury em evidence-qualified planning primeiro em shadow. Essa etapa reduz um custo que incide sobre todo train futuro. Ver dossiê `research/08_validation-assurance/2026-08-13-assurance-topology/`.

### P0.2 — Trusted Judge

Separar ordinary green CI de strict proof. Fechar trusted invocation / candidate-evaluator-promoter provenance / incumbent-N-judges-N+1 sem fingir que filesystem confinement ou Genesis estão provados.

### P0.3 — Effects / reliability

Priorizar reconciliation-before-retry, idempotency, process/session ownership, WorkspaceLease/Permit/EffectReceipt e sandbox/confinement por risco. Isso torna runtime fallback e autonomia futura economicamente seguros.

### P1.0 — Durable Work + Evidence

Construir sobre TaskStore + RunEnvelope + Q8. Não criar WorkRegistry/ExecutionAttempt paralelo sem ADR. O objetivo é reconstruir task → decision → execution → effect → validation/evidence.

### P1.1 — Relay

Automatizar wake-up/corrective loops apenas depois de validation/effect semantics estáveis. Git/GitHub/Drive são transport/projections; comentários/modelos não mintam Authority.

### P1.2 — Routing

Promover Q7 shadow semantics e convergir RouteIntent/Decision→binding sem ativação prematura. Routing/reputation não concedem Authority.

### P2/P3

Adaptive scheduling, reputation/qualification, memory e evolution só ganham valor seguro quando o evidence backbone que alimenta aprendizado é confiável.

## 4. WIP policy

- no máximo **um critical implementation/promotion train** consumindo staging critical path;
- uma research/documentation stream pode rodar em paralelo se não mutar o subject;
- same-scope bounded correctives permanecem no train em vez de criar issue/branch a cada pequeno finding;
- experiments podem continuar isolados, mas não devem reivindicar CURRENT antes dos prerequisites.

Essa política busca reduzir queueing, rebase debt, owner interruptions e audit context switching.

## 5. Definition of Ready para structural work

Um train só entra no critical path quando possui:

1. exact subject/base/ref;
2. CURRENT owner/seam archaeology;
3. bounded-context owner;
4. CURRENT × TARGET × PROPOSED × RESEARCH;
5. contracts e no-duplicate-primitive check;
6. evidence obligations/falsifiers;
7. Authority/effect ceiling;
8. compatibility + rollback;
9. dependency explícita neste portfolio;
10. small Implementation Packet boundary.

## 6. Definition of Done

Local green não basta. Structural Done exige exact remote reconstruction, independent audit, risk-appropriate CI/cross-platform evidence, preserved negative evidence, no unauthorized effect, migration/rollback evidence e update pelos canonical single writers.

## 7. Falsificadores da priorização

Reordenar se evidence mostrar que:

- Assurance P0 não reduz time-to-trust/corrective burden;
- shadow selection perde failures do CURRENT treasury;
- trusted-judge source archaeology exige prerequisite diferente;
- Work/Run já possui incumbent equivalente suficiente;
- Relay automation aumenta ambiguous effects;
- adaptive scheduling reduz compute mas piora critical-path trust latency;
- outra dependency domina empiricamente o portfolio.

## 8. Relação com o backlog canônico

No repositório principal foi criada a Issue #18 como `PROPOSED / BACKLOG INTAKE / PORTFOLIO REPRIORITIZATION` e a Issue #19 como candidate específico de Assurance Topology. Isso **não substitui `.harness/state/tasks.json`**.

Após o active CI train, um `BACKLOG-ALIGN-01` deve usar o incumbent `harness.py tasks ...` para ADOPT/ADAPT tasks existentes, criar somente gaps genuínos e gravar dependency/priority via single writer. Raw JSON edit é anti-pattern.

## 9. Research-to-architecture path

```text
operational evidence
 -> Research draft
 -> Findings (ADOPT/ADAPT/RETIRE/OPEN)
 -> ADR
 -> canonical architecture / SPEC
 -> BDD
 -> Implementation Packet
 -> code/gates
 -> new evidence
```

Este roadmap não pode pular essa cadeia por ser “mais novo” que arquitetura já ratificada.

## 10. Claim ceiling

A contribuição atual é **design-science roadmap informado por incidentes operacionais internos**. Não há ainda experimento demonstrando que esta ordem global é ótima. A tese mais defensável é local: quando uma capability de assurance/promotion reduz custo de qualificação de muitos descendants, ela merece prioridade por efeito multiplicativo, desde que não vire big-bang/platform rewrite.
