# ADR-045: North Star do Ecossistema tare.tools & tare-kernel (Agent OS 2.0) — Arquitetura Modular em 4 Repositórios

- **Status:** Ratificado e Aprovado pela Mesa Redonda Tripartite (`CASE-2026-08-17-ECOSYSTEM-AND-KERNEL-NORTH-STAR`)
- **Data:** 2026-08-17
- **Autores:** Antigravity Mediator (sob direcionamento do Operador Humano e consenso da Mesa Tripartite: Google Gemini 3.7 Flash High, Anthropic Claude Fable 5 High, OpenAI GPT-5.6 Sol High)
- **Escopo:** Ecossistema Global `tare.tools` & `tare-kernel`

---

## 1. Contexto e Motivação

O programa `tare.tools` evoluiu ao longo de mais de 80 sessões de engenharia catalogadas no ChatGPT, provando a viabilidade de swarms multi-agente assíncronos. Contudo, o protótipo v1 revelou o gargalo do **monólito acidental**:
* O motor de tarefas (DAG), o executor de ferramentas (harness), a indexação de código e a governança de releases conviviam no mesmo repositório;
* Múltiplos processos concorrentes colidiam na escrita do arquivo de grafo compartilhado (`work-graph.json`);
* A amnésia de decisões (*documentation drift*) ocorria por falta de amarração causal entre specs e código.

Este ADR estabelece a **North Star definitiva de Produto e Arquitetura do Ecossistema tare.tools e do `tare-kernel` (Agent OS 2.0)**, superando o viés puramente adversarial para entregar uma plataforma modular, ergonômica e veloz.

---

### 1.2 Não-Objetivos Explícitos (Via Negativa / Fora de Escopo)
1. **Sem Monólito Acidental:** Os componentes de backlog, indexação AST e orquestração de kernel residem em repositórios separados com fronteiras de estado estritas.
2. **Sem Escrita Concorrente Não-Coordenada:** O kernel nunca edita diretamente o arquivo `work-graph.json`, operando exclusivamente através de transações de API e CAS com lockfile.
3. **Sem Amarras a Provedores Específicos de LLM:** O ecossistema suporta modelos abertos locais (vLLM, llama.cpp) e APIs comerciais com dynamic model binding.

---

## 2. Decisão Arquitetural: O Ecossistema em 4 Repositórios Modulares

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       ECOSSISTEMA TARE.TOOLS                                      │
└───────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                  │
         ┌────────────────────────┬───────────────┴───────────────┬────────────────────────┐
         │                        │                               │                        │
         ▼                        ▼                               ▼                        ▼
┌──────────────────┐    ┌──────────────────┐            ┌──────────────────┐    ┌──────────────────┐
│   tare-kernel    │    │  tare-specgraph  │            │tare-backlog-graph│    │tare.tools.research│
│  (Agent OS Core) │    │(Project Intel/SDD│            │  (Task DAG Engine│    │(Papers, ADRs &   │
│                  │    │  & Traceability) │            │  & Topology)     │    │ Research Memory) │
│ • 5 Planos       │    │ • CPG AST Parser │            │ • DAG Acíclico   │    │ • Artigos IEEE   │
│ • Relay Mesh     │    │ • Matriz Causal  │            │ • Cálculo de     │    │ • ADRs Formais   │
│ • Sandboxes      │    │ • Drift Detection│            │   Fronteira      │    │ • GitHub Pages   │
│ • Orquestração   │    │ • Context Engine │            │ • 79 Testes Unit.│    │ • Benchmarks     │
└──────────────────┘    └──────────────────┘            └──────────────────┘    └──────────────────┘
```

### Matriz de Propriedade de Estado Estrita:
1. **`tare-backlog-graph`:** Dono exclusivo do `work-graph.json` (DAG de tarefas). Zero dependência externa.
2. **`tare-kernel`:** Dono do ciclo de vida de trens e FSM de execução. Consome o backlog via API transacional.
3. **`tare.tools-specgraph`:** Dono da matriz causal de rastreabilidade (Specs $\leftrightarrow$ Code $\leftrightarrow$ Tests).
4. **`tare.tools.research`:** Acervo público de artigos científicos, benchmarks e ADRs formais no GitHub Pages.

---

## 3. Protocolo de Landing Idempotente e Recuperável

O `tare-kernel` nunca edita diretamente o arquivo de grafo. A aterrissagem de releases segue 4 etapas recuperáveis:
1. **Prepare:** O kernel gera o `ReleaseEnvelope` assinado e bloqueia a revisão esperada do DAG (`expected_dag_rev`).
2. **Git Land:** O commit e push atômico são executados com `--force-with-lease`.
3. **DAG Update:** O kernel invoca a API transacional do backlog:
   ```bash
   python graph_ops.py land --train <TRAIN_ID> --tasks <TASK_IDS> --expect-rev <REVISION_HASH>
   ```
4. **Crash Recovery:** Em caso de interrupção entre os passos 2 e 3, a reinicialização do daemon reconcilia deterministicamente o estado do backlog com base no commit pousado no Git.

---

## 4. O Happy Path de Desenvolvimento em 3 Comandos

A experiência do desenvolvedor humano e dos agentes de IA é rápida e intuitiva:

```
[ 1. `tare task new "Título" --spec SPEC-XX` ] ──► [ 2. `tare run` ] ──► [ 3. `tare approve <ID>` ]
• Cria a tarefa no DAG e associa à spec.           • O swarm despacha o Relay      • Operador revisa o diff no Cockpit
• Valida dependências no backlog.                    Mesh (Plan → Code → Test).      e aterrissa o release em 1 clique.
```

---

## 5. Release Envelope & Amarração Causal Imutável

Todo release gerenciado pelo kernel empacota um **Release Envelope** canônico:
$$\text{ReleaseEnvelope} = \langle \text{train\_id},\ \text{spec\_ids},\ \text{task\_ids},\ \text{base\_tree\_hash},\ \text{patch\_sha256},\ \text{resulting\_tree\_hash},\ \text{test\_evidence\_hash},\ \text{expected\_dag\_rev} \rangle$$
O botão de aprovação no Web Cockpit (:8765 em `127.0.0.1`) vincula todos esses campos, garantindo que o Operador aprove exatamente o artefato testado e atestado.

---

## 6. Estratégia de Coexistência Suave & Replay de Paridade

1. **Coexistência Inicial:** O `tare-tools-relay` v1 permanece como o ambiente ativo de produção.
2. **Replay de Paridade por Invariantes:** O `tare-kernel` v2 reexecuta 10 trens históricos do v1 e valida **equivalência exata de resultado determinístico** (árvore Git resultante idêntica, tarefas concluídas e atestação de testes aprovada).
3. **Cutover Definitivo:** O corte ocorre somente após a paridade comprovada no replay.

---

## 7. Roadmap de Lançamento em 4 Fases

1. **Fase 1 (Greenfield & P0 Engine):** Inicialização dos repositórios limpos, CAS SQLite, Ingress Gatekeeper, Notary Ed25519 e extração do `tare-backlog-graph`.
2. **Fase 2 (CLI & Cockpit Unificado):** CLI unificada `tare` e Web Cockpit visual com monitoramento do swarm.
3. **Fase 3 (SpecGraph Integration):** Integração com Context Envelopes e Drift Gate em PRs.
4. **Fase 4 (Multi-Node Compute):** Workers remotos via Tailscale para despacho de tarefas pesadas.
