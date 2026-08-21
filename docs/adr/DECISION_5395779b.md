# DECISÃO CANÔNICA DA MESA REDONDA: RT-ADR-042

**Título:** ADR-042: Arquitetura de Microkernel Desacoplado para o tare.tools Agent OS  
**Veredito Final:** `APPROVED`  
**Versão Ratificada:** `v003` (SHA-256: `f3179a70dbef0454e65fecd0ba228becad084ef8fe8bc88eca9d6042d34bba2e`)  
**Data da Decisão:** 2026-08-17T14:00:17.898587+00:00  
**Mediador:** Antigravity Mediator  

---

## 🏛️ Composição da Mesa & Votos Finais:
- **Google Chair (`gemini 3.7 flash high`):** Participação validada.
- **Anthropic Chair (`fable 5 high`):** Participação validada.
- **OpenAI Chair (`gpt sol 5.6 high`):** Participação validada.

---

## 📋 Sumário da Deliberação:
Aprovado por consenso unânime após 2 rodadas de mediação e incorporação das emendas de Fencing Tokens, Single-Writer, Sandbox Isolado para Testes, Base Hash Fencing e Recibos Criptográficos.

---

## 📜 Texto Ratificado por Consenso:
```markdown
# ADR-042: Arquitetura de Microkernel Desacoplado para o tare.tools Agent OS

**Status:** RATIFICADO POR CONSENSO UNÂNIME DA MESA REDONDA (v003)  
**Data:** 17 de Agosto de 2026  
**Autores:** Augusto & Antigravity (Mediador Independente)  
**Revisores Titulares:** Google Chair (`gemini 3.7 flash high`), Anthropic Chair (`fable 5 high`), OpenAI Chair (`gpt sol 5.6 high`)  
**Contexto:** Evolução do Multi-Agent Relay Mesh (MARM) e Universal Agent Harness Prototype.

---

## 1. Contexto & Problema

Durante a fase inicial de experimentação e integração do `tare.tools`, dois protótipos principais foram desenvolvidos:
1. **Universal Agent Harness Prototype (`harness`):** Focado em execução de ferramentas, extração de AST, sandboxing e adaptadores de modelos.
2. **Multi-Agent Relay Mesh (`relay`):** Focado em coordenação multiagente, máquinas de estado de leases (FSM), filas de auditoria e sincronização distribuída entre múltiplos hosts.

À medida que esses dois protótipos convergiram, surgiu a hipótese de unificá-los em um **"núcleo único monolítico"**. A deliberação adversarial tripartite da Mesa Redonda concluiu que um monolito criaria severos riscos de concorrência, split-brain e blast radius descontrolado. A solução formal é o desacoplamento em 5 planos com governança determinística.

---

## 2. Decisão Arquitetural: Arquitetura de Microkernel em 5 Planos

Fica formalmente decidido que a arquitetura do `tare.tools` é um **Microkernel Desacoplado baseado em 5 Planos Independentes**, comunicando-se exclusivamente através de contratos estritos, fencing tokens e recibos criptográficos de atestação.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 1. EXPERIENCE PLANE (Interface Humana & Observabilidade)                 │
│    • Web Cockpit (:8765), CLI (`relay_mesh.py`), TUI, Modo Executivo     │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ (Scoped 1-Time Nonce vinculado ao Release)
┌────────────────────────────────────▼─────────────────────────────────────┐
│ 2. CONTROL PLANE (O Microkernel de Governança & FSM)                     │
│    • Scheduler de Leases com Fencing Tokens (Monotonic `lease_epoch`)    │
│    • Lock Manager, Transições de Estado, Single-Writer Orchestration     │
│    • Hiperleve, 100% determinístico, zero-IA, tolerante a partição       │
└───────────────┬───────────────────┬──────────────────────────────────────┘
                │                   │ (Despacho Direto em Sandbox Isolado)
┌───────────────▼──────────────┐    │    ┌─────────────────────────────────┐
│ 3. DATA PLANE (Grafo & Armaz)│    └───►│ 5. ASSURANCE PLANE (Oráculos)   │
│    • `work-graph.json`       │         │    • Pytest, Linters, AST       │
│    • Strict Single-Writer    │         │    • Falsificadores U-7D        │
│    • Check-and-Write Atômico │         │    • Recibos Criptográficos     │
└──────────────────────────────┘         └────────────────┬────────────────┘
                ▲                                         │ (Attestation Receipt)
                │ (Proposta de Transição + Patch)         ▼
┌───────────────┴──────────────────────────────────────────────────────────┐
│ 4. COMPUTE PLANE (Workers Descartáveis & Adaptadores de IA)              │
│    • Workers nos nós (Desktop / Notebook / Cloud via Tailscale)          │
│    • Vendor Chairs (Cadeiras Frontier com Circuit Breakers)              │
│    • Inputs não-confiáveis submetidos à prova do Assurance Plane         │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Especificação dos 5 Planos & Emendas Formais da Mesa Redonda

### 3.1. Control Plane (O Microkernel)
- **Responsabilidade:** Agendamento de tarefas, gestão de concorrência e posse (Leases), transições de estado da máquina FSM.
- **Invariante de Fencing Token (Emenda ISS-01 Google / ISS-06 OpenAI):** Todo lease emitido carrega um `lease_epoch` estritamente monotônico. Qualquer transição de estado, publicação de artefato ou proposta de escrita com `lease_epoch` desatualizado é **rejeitada atomicamente** pelo Control Plane, blindando o cluster contra *Zombie Workers*.
- **Invariante Base Hash Fencing (Emenda ISS-02 Google / ISS-07 OpenAI):** A transição final para `LANDED` exige estritamente que `current_base_commit == audited_base_commit`. Caso a árvore canônica tenha avançado durante o gate humano, a atestação é invalidada e a tarefa retorna a `AUDIT_PENDING` para rebase automático.
- **FSM Canônica com Gate Humano (Emenda ISS-03 Google):**
  $$\text{CLAIMED} \rightarrow \text{DISPATCHED} \rightarrow \text{AUDIT\_PENDING} \rightarrow \text{GATED\_FOR\_APPROVAL} \rightarrow \text{LANDED}$$
  Nenhuma tarefa transiciona para `LANDED` sem o recibo de atestação do Assurance Plane e o nonce de uso único do operador.

### 3.2. Data Plane (Grafo de Trabalho & Armazenamento Canônico)
- **Invariante Strict Single-Writer (Emenda ISS-01 Anthropic / ISS-05 OpenAI):** **Nenhum worker do Compute Plane escreve diretamente no `work-graph.json`**. Workers apenas emitem propostas de transição via API. A serialização no disco canônico é feita exclusivamente pelo processo host do Control Plane / Bookkeeper através de escrita atômica (`write-tmp + fsync + rename`).
- **Prevenção Atômica de Ciclos (Emenda ISS-03 Anthropic):** A verificação de aciclicidade e a persistência de novas arestas são encapsuladas em uma única operação atômica *check-and-write* sob mutex, eliminando janelas TOCTOU (*Time-of-Check to Time-of-Use*).

### 3.3. Compute Plane (Workers & Cadeiras Frontier)
- **Responsabilidade:** Execução física de raciocínio, escrita de código e propostas de plano.
- **Características:** Totalmente descartável e sem privilégios de escrita canônica. Trata saídas de IA como *dados não confiáveis* até a validação mecânica.
- **Autenticação de Nós (Emenda ISS-04 Anthropic):** A adesão de workers à malha exige token de autenticação de nó e escopo explícito de permissões por papel.

### 3.4. Assurance Plane (Oráculos Mecânicos de Validação)
- **Inversão de Limite de Autoridade (Emenda ISS-02 Google):** O Assurance Plane é invocado e inspecionado **diretamente pelo Control Plane**, e não comandado pelo worker do Compute Plane.
- **Isolamento em Sandbox Estéril (Emenda ISS-01 Google):** Toda execução dinâmica de testes (Pytest, fuzzing, falsificadores) ocorre dentro de um sandbox efêmero e desprivilegiado (rootless container/microVM) com rede desabilitada, prevenindo RCE no host do microkernel.
- **Recibo Criptográfico de Atestação (Emenda ISS-07 OpenAI):** O Assurance Plane emite um recibo assinado vinculando `hash(patch) + hash(base_commit) + task_id + lease_epoch = PASS`.

### 3.5. Experience Plane (Interface do Operador)
- **Responsabilidade:** Cockpit Web em tempo real (`:8765`), CLI unificado, aprovação em 1 clique (`aprovar`), alternância de visualização Executiva (sem jargões) vs. Técnica.
- **Nonce Criptográfico de Uso Único (Emenda ISS-08 OpenAI):** A aprovação humana gera um nonce de uso único, com expiração curta (1 hora) e vinculado ao hash da atestação do release, impedindo ataques de replay.

---

## 4. Benefícios Arquiteturais & Limites de Contenção

1. **Blast Radius Rigorosamente Contido:** Falhas em APIs externas, timeouts de LLMs ou erros de sintaxe nos workers nunca corrompem o grafo nem desestabilizam o agendador.
2. **Linearizabilidade & Zero Split-Brain:** Fencing tokens, Single-Writer e Base Hash Fencing garantem consistência sequencial mesmo durante partições de rede.
3. **Escalabilidade Horizontal Segura:** Múltiplos nós heterogêneos (Desktops, Notebooks, Cloud) operam como recursos elásticos sem privilégios de mutação direta.
4. **Conformidade Total com o Corpus Científico:** Alinhamento estrito com o princípio de controle determinístico sobre inteligência probabilística (`tare.tools.research`).

```
