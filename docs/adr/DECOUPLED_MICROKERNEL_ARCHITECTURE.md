# ADR-042: Arquitetura de Microkernel Desacoplado para o tare.tools Agent OS

> **Status:** SUPERSEDED BY [ADR-045: North Star do Ecossistema tare.tools & tare-kernel (Agent OS 2.0)](ADR-045_ECOSYSTEM_AND_KERNEL_NORTH_STAR.md)
> **Nota:** Decisão original dos 5 planos. Suas premissas de quorum Raft e isolamento pesado foram formalmente substituídas pela arquitetura pragmática do ADR-045.

**Document ID:** `research.architecture.decoupled-microkernel-architecture.2026-08-17`  
**Status:** `RESEARCH / RATIFIED ARCHITECTURAL SPECIFICATION`  
**Data:** 2026-08-17  
**Autores:** Augusto Carvalho, Antigravity Mediator & Mesa Redonda Tripartite (Gemini 3.7 High, GPT-5.6 Sol / Codex, Claude Fable 5 High)  
**Contexto Temático:** `02_harness-architecture`  
**Repositórios de Referência:** `tare-research/tare.tools`, `tare.tools.research`  
**Fundamentação Canônica:** [Linha I: Decoupled Microkernel Architecture](https://github.com/augusto-scarvalho/tare.tools.research/tree/main/research/02_harness-architecture), Linhas A–H.

---

## Resumo (Abstract)

Este Registro de Decisão Arquitetural (ADR-042) formaliza a transição estrutural do `tare.tools Agent OS` de um núcleo monolítico para uma **Arquitetura de Microkernel Desacoplado em 5 Planos Independentes** (Experience, Control, Data, Compute e Assurance). Baseando-se em evidências empíricas de 9 linhas de pesquisa e na deliberação adversarial tripartite da Mesa Redonda (Gemini 3.7 High, GPT-5.6 Sol / Codex, Claude Fable 5 High), o estudo estabelece as fronteiras físicas de autoridade: isolamento total do *Compute Plane* com zero permissão de mutação direta, governança CP estrita com *fencing tokens* monotônicos emitidos por consenso Raft de 3 nós, *Landing Saga* de 5 estados com reconciliador contínuo e push atômico fast-forward verificado via Egress Service dedicado, processo Notário isolado para emissão de *Attestation Receipts* imunes a adulteração de testes, e *Landing Reservation Lease* com TTL e heartbeat pós-aprovação humana para eliminar starvation no merge train.

---

## 1. Escopo & Formulação do Problema (Scope)

Durante a fase inicial de experimentação e integração do `tare.tools`, dois protótipos principais foram desenvolvidos:
1. **Universal Agent Harness Prototype (`harness`):** Focado em execução de ferramentas, extração de AST, sandboxing e adaptadores de modelos.
2. **Multi-Agent Relay Mesh (`relay`):** Focado em coordenação multiagente, máquinas de estado de leases (FSM), filas de auditoria e sincronização distribuída entre múltiplos hosts.

À medida que esses dois protótipos convergiram, surgiu a hipótese de unificá-los em um **"núcleo único monolítico"**. A deliberação adversarial tripartite da Mesa Redonda concluiu que um monolito criaria severos riscos de concorrência, split-brain e blast radius descontrolado. A solução formal é o desacoplamento em 5 planos com governança determinística e propriedades CP rigorosas.

---

## 2. Método & Trilha de Evidências (Evidence)

A decisão fundamenta-se nas seguintes trilhas de evidência empírica:
1. **Deliberação Dialética Tripartite:** Submissão do caso `CASE-2026-08-17-DECOUPLED-MICROKERNEL-CORE` a três bancadas independentes (*Claude Fable 5*, *OpenAI GPT-5.6 Sol*, *Google Gemini 3.7 High*), convergindo em 3 rodadas com 100% de consenso.
2. **Provas Negativas & Falsificadores Mecânicos:** Simulação de partições de rede e falhas de workers comprovando que a ausência de fencing monotônico permitia escritas zumbis em arquivos planos.
3. **Isolamento de Oráculos no Assurance Plane:** Demonstração de que a separação física do processo Notário impede que agentes alterem asserções de teste para forçar aprovações falsas.

---

## 3. Decisão Arquitetural & Especificação dos 5 Planos (Findings)

Fica formalmente decidido que a arquitetura do `tare.tools` é um **Microkernel Desacoplado baseado em 5 Planos Independentes**, comunicando-se exclusivamente através de contratos estritos, fencing tokens, recibos criptográficos e Landing Journals atômicos:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 1. EXPERIENCE PLANE (Interface Humana & Observabilidade)                 │
│    • Web Cockpit (:8765), CLI (`relay_mesh.py`), TUI, Modo Executivo     │
│    • 1-Click Human Approval com Nonce Descartável de Uso Único           │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ (Scoped 1-Time Nonce vinculado ao Release)
┌────────────────────────────────────▼─────────────────────────────────────┐
│ 2. CONTROL PLANE (O Microkernel de Governança & FSM — Arquitetura CP)    │
│    • Singleton Leader Lease com Fencing Monotônico CAS                   │
│    • Landing Queue (Merge Train) com Monotonic Aging & Anti-Starvation   │
│    • Landing Saga WAL (PREPARED → PUSHING → COMMITTED | RECONCILING)     │
│    • Egress Service Dedicado (Push Fast-Forward Verificado)              │
└───────┬──────────────────────┬───────────────────────────────────▲───────┘
        │ (Single-Writer CAS)  │ (Dispatch em Sandbox Efêmero)     │
┌───────▼───────────────────┐  │                                   │ (Signed Attestation Receipt)
│ 3. DATA PLANE (Estado)    │  │                                   │
│    • Raft Quorum 3 Nós    │  │                                   │
│    • Strict Single-Writer │  │                                   │
│    • CAS & Fenced Commits │  │                                   │
└───────────────────────────┘  │                                   │
                               │  ┌────────────────────────────────┴───────┐
                               └──► 5. ASSURANCE PLANE (Oráculos & Notário)│
                                  │    • Pinned Oracles (Pytest Hermético) │
                                  │    • Processo Notário Separado         │
                                  │    • Signed Attestation Receipt        │
                                  └────────────────────────────────────────┘
                ▲
                │ (Ingress RPC Proposta)    ┌──────────────────────────────┐
                └───────────────────────────┤ 4. COMPUTE PLANE (Workers)   │
                                            │    • Desktop / Laptop Nodes  │
                                            │    • Zero Escrita em Disco   │
                                            │    • TaskEnvelope Confinado  │
                                            └──────────────────────────────┘
```

### 3.1. Invariantes dos 5 Planos

| Plano | Responsabilidade Primária | Invariante de Segurança e Integridade |
|---|---|---|
| **1. Experience Plane** | Interface do operador (Cockpit, CLI, TUI). | Nonce de aprovação humana de uso único vinculado criptograficamente ao release. |
| **2. Control Plane** | Microkernel de governança, FSM e Merge Train. | Arquitetura CP estrita; fencing monotônico CAS e Egress Service dedicado. |
| **3. Data Plane** | Armazenamento de estado durável e grafos. | Quórum Raft de 3 nós com pre-vote; Single-Writer CAS incondicional. |
| **4. Compute Plane** | Execução de IA e raciocínio de agentes. | Sandbox efêmero com zero acesso a disco ou Git; propostas via Ingress RPC. |
| **5. Assurance Plane** | Oráculos de validação mecânica e linters. | Execução em sandbox hermético e assinatura exclusiva por processo Notário isolado. |

---

## 4. Limitações & Ameaças à Validade (Limitations)

1. **Quórum Distribuído Obrigatório:** Em ambientes com dois nós físicos, a integridade do Data Plane exige um terceiro nó árbitro/testemunha (*Cloud Witness* com pre-vote e non-candidate).
2. **Latência de Deliberação Tripartite:** A invocação síncrona de múltiplos modelos frontier impõe latência de 2 a 5 minutos por ADR, sendo restrita a mudanças estruturais de arquitetura.
3. **Clock Skew:** O sistema tolera divergência de relógio de até $\epsilon_{\text{skew}} = 5.0\,\text{s}$ entre o líder e o provedor de credenciais efêmeras.

---

## 5. Referências & Genealogia Canônica (References)

1. **North Star 2.0:** *Arquitetura de Microkernel Desacoplado em 5 Planos e Bússola Estrutural de Backlog* (2026).
2. **Liedtke, J. (1995):** *On µ-Kernel Construction*. 15th ACM SOSP.
3. **Ongaro, D., & Ousterhout, J. (2014):** *In Search of an Understandable Consensus Algorithm (Raft)*. USENIX ATC.
4. **tare.tools.research:** Linhas de Pesquisa A–I e Repositório Canônico `tare-research/tare.tools`.
