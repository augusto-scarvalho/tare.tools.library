# Estudo Arquitetural: Arquitetura de Microkernel Desacoplado em 5 Planos para o tare.tools Agent OS

- **Status:** `RESEARCH / ACTIVE / PEER-REVIEW RATIFIED DRAFT`
- **Data de Publicação:** 2026-08-17
- **Autores:** Augusto & Antigravity (Mediador Independente)
- **Bancada de Peer Review Tripartite:** Google Chair (`Gemini 3.7 Flash High`), Anthropic Chair (`Fable 5 High`), OpenAI Chair (`GPT Sol 5.6 High`)
- **Bounded Contexts:** `Harness Architecture`, `Control Plane`, `Governance / Audit`, `Validation / Assurance`, `Reliability`, `Runtime / Model Inference`, `Identity / Authority`.
- **Genealogia & Proveniência:** Derivado do **ADR-042** ([`docs/DECOUPLED_MICROKERNEL_ARCHITECTURE.md`](file:///C:/projects/tare-tools-relay/docs/DECOUPLED_MICROKERNEL_ARCHITECTURE.md)), ratificado sob o protocolo de deliberação tripartite `RT-ADR-042-PROD` (hash SHA-256 e recibos criptográficos imutáveis).
- **Relação com Material Histórico:** Este documento sintetiza e formaliza a transição de estado da North Star do tare.tools, superando a hipótese inicial de acoplamento em núcleo monolítico.
- **Classificação de Autoridade:** `RESEARCH / RATIFIED STUDY` (Fundamentação teórica e desenho estrutural para o Agent OS).

---

## 1. Resumo Executivo & Contribuição Fundamental

Durante a evolução dos protótipos `universal-agent-harness-prototype` (`harness`) e `tare-tools-relay` (`relay`), emergiu a hipótese de unificação das capacidades agênticas e de coordenação em um **"núcleo único monolítico"**. 

Este estudo formaliza a **refutação analítica e empírica da hipótese do núcleo monolítico** e estabelece a especificação canônica da **Arquitetura de Microkernel Desacoplado em 5 Planos** para o `tare.tools Agent OS`.

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 1. EXPERIENCE PLANE (Interface Humana & Observabilidade)                 │
│    • Web Cockpit (:8765), CLI (`relay_mesh.py`), TUI, Modo Executivo     │
└────────────────────────────────────┬─────────────────────────────────────┘
                                     │ (Scoped 1-Time Nonce vinculado ao Release)
┌────────────────────────────────────▼─────────────────────────────────────┐
│ 2. CONTROL PLANE (O Microkernel de Governança & FSM — Arquitetura CP)    │
│    • Singleton Leader Lease com Fencing Monotônico (`lease_epoch`)       │
│    • Landing Queue (Merge Train) com Rebase Semântico Anti-Starvation    │
│    • Transactional Landing Journal (WAL) reconciliando Git & Grafo       │
└───────────────┬───────────────────┬──────────────────────────────────────┘
                │                   │ (Despacho Direto em Sandbox Isolado)
┌───────────────▼──────────────┐    │    ┌─────────────────────────────────┐
│ 3. DATA PLANE (Grafo & Armaz)│    └───►│ 5. ASSURANCE PLANE (Oráculos)   │
│    • `work-graph.json`       │         │    • Pytest, Linters, AST       │
│    • Strict Single-Writer    │         │    • Candidate Tree Hash & AST  │
│    • Check-and-Write Atômico │         │    • Recibo Criptográfico       │
└──────────────────────────────┘         └────────────────┬────────────────┘
                ▲                                         │ (Attestation Receipt)
                │ (Proposta de Transição + Patch)         ▼
┌───────────────┴──────────────────────────────────────────────────────────┐
│ 4. COMPUTE PLANE (Workers Descartáveis & Adaptadores de IA)              │
│    • Workers nos nós (Desktop / Notebook / Cloud via Tailscale)          │
│    • Vendor Chairs (Cadeiras Frontier com Circuit Breakers)              │
│    • Zero Mutação Canônica: Saídas tratadas como dados não confiáveis   │
└──────────────────────────────────────────────────────────────────────────┘
```

### Contribuições Centrais:
1. **Teorema da Separação Estrita de Autoridade:** Prova formal de que a integridade de um Agent OS requer a segregação total entre *inteligência probabilística geradora* (Compute Plane) e *árbitros determinísticos de mutação* (Control e Assurance Planes).
2. **Propriedade CP Estrita do Microkernel:** Formalização do Control Plane como um sistema CP (*Consistency & Partition Tolerance*), garantindo tolerância a falhas sem risco de *split-brain* ou liderança dual.
3. **Mecanismo de Merge Train com Rebase Semântico:** Eliminação do risco de *livelock* e inanição (*starvation*) no gate humano sob alta concorrência multi-worker.
4. **Recibo Criptográfico Expandido de Atestação:** Vinculação matemática de `candidate_tree_hash`, digest de sandbox estéril e política de testes imutável ao release final.

---

## 2. Perguntas de Pesquisa (Research Questions)

- **RQ1 (Contenção de Blast Radius):** Como desacoplar a execução de modelos de IA não confiáveis de modo que alucinações, loops de execução ou falhas de rede nunca corrompam a base de dados canônica do grafo de trabalho?
- **RQ2 (Consistência em Redes Assimétricas):** Como garantir linearizabilidade e consistência estrita em um cluster heterogêneo multi-host (Desktop, Notebook, Cloud) sem incorrer em sobrecarga pesada de consenso distribuído em workers descartáveis?
- **RQ3 (Deliberação Dialética Multi-Vendor):** É possível alcançar decisões de arquitetura e segurança demonstráveis e auditáveis utilizando comitês de LLMs frontier concorrentes como oráculos adversariais?

---

## 3. Modelo Formal dos 5 Planos

### 3.1. Experience Plane $\mathcal{E}$
- **Definição:** Ponto de contato e projeção para o operador humano.
- **Superfície:** Web Cockpit em tempo real (`:8765`), CLI unificado (`relay_mesh.py`) e modo executivo sem jargões.
- **Protocolo de Autoridade:** A aprovação humana emite um nonce de uso único $N_{\text{human}}$ com expiração finita ($t \le 3600s$), criptograficamente vinculado ao hash do release a ser aterrado:
  $$N_{\text{human}} = \text{HMAC}_{K}(H(\text{Release}) \parallel \text{lease\_epoch} \parallel \text{exp\_time})$$

### 3.2. Control Plane $\mathcal{C}$ (O Microkernel de Governança)
- **Definição:** Núcleo determinístico, hiperleve (zero inferência de IA) e responsável pelo ciclo de vida da FSM.
- **Classificação CAP:** Sistema **CP** (Consistência e Tolerância a Partições). Sob partição de rede, a mutação é suspensa em partições sem lease do líder.
- **Fencing Token Monotônico:** A cada lease concedido a um worker, o Control Plane incrementa o epoch global:
  $$\text{lease\_epoch}_{k+1} > \text{lease\_epoch}_k$$
- **Transactional Landing Journal (WAL):** Reconciliação atômica entre o repositório Git e o arquivo `work-graph.json`. Antes de qualquer merge, o Control Plane persiste a intenção no journal; falhas de processo no meio do caminho recuperam deterministicamente o estado do grafo no bootup.

### 3.3. Data Plane $\mathcal{D}$ (Grafo de Trabalho & Armazenamento Canônico)
- **Invariante Strict Single-Writer:**
  $$\forall w \in \text{ComputePlane}, \quad \text{write\_permission}(w, \mathcal{D}) = \emptyset$$
  Nenhum worker escreve diretamente no disco canônico. Workers apenas emitem propostas assinaladas como `TransitionProposal`.
- **Prevenção Atômica de Ciclos:** Validação de aciclicidade $G' = (V, E \cup \{e\})$ e gravação de aresta encapsuladas em uma única operação *check-and-write* sob mutex exclusivo.

### 3.4. Compute Plane $\mathcal{K}$ (Workers Descartáveis & Cadeiras Frontier)
- **Definição:** Unidades elásticas de computação cognitiva (Desktop `aaaaa`, Notebook `Acer`, instâncias efêmeras).
- **Tratamento de Saída:** Todas as mutações de código, planos ou respostas geradas por LLMs são tipadas como *dados não confiáveis* até atestação mecânica formal.
- **Revogação Instantânea:** Se a conexão de um worker for interrompida, seu lease expira e seu `lease_epoch` é revogado sem impacto residual no estado canônico.

### 3.5. Assurance Plane $\mathcal{A}$ (Oráculos Mecânicos de Validação)
- **Definição:** Conjunto de oráculos de verificação lógica, sintática e dinâmica (Pytest, Linters, AST diffs, Falsificadores U-7D).
- **Inversão de Autoridade:** O Assurance Plane é invocado exclusivamente pelo Control Plane, operando em sandbox isolado (container rootless com rede desabilitada).
- **Recibo Criptográfico Expandido:**
  $$\text{Receipt}_{\mathcal{A}} = \text{Sign}_{K_{\mathcal{A}}}\Big(H(\text{patch}) \parallel H(\text{base\_commit}) \parallel \text{TreeHash}_{\text{candidate}} \parallel \text{Digest}(\text{Sandbox}) \parallel \text{task\_id} \parallel \text{lease\_epoch}\Big)$$

---

## 4. Análise de Propriedades de Sistemas Distribuídos

| Propriedade | Mecanismo Arquitetural | Garantia Formal |
|---|---|---|
| **Zero Split-Brain** | Singleton Leader Lease + Fencing Monotônico | Impossibilidade matemática de dois workers aplicarem mutações conflitantes. |
| **Imunidade a Zombie Workers** | Rejeição atômica de `lease_epoch` desatualizado no Control Plane | Mensagens ou patches de workers atrasados são descartados imediatamente. |
| **Consistência Dual-Write** | Transactional Landing Journal (WAL) | O estado do `work-graph.json` é perfeitamente espelhado na árvore Git mesmo pós-crash. |
| **Prevenção de Livelock** | Landing Queue (Merge Train) + Rebase Delta Automático | Workers aprovados não sofrem inanição quando outros releases aterrissam primeiro. |
| **Contenção de RCE** | Sandbox desprivilegiado sem rede no Assurance Plane | Código de teste malicioso gerado por IA não pode exfiltrar credenciais nem persistir no host. |

---

## 5. A Deliberação Tripartite Dialética como Oráculo de Consenso

O estudo e a ratificação do ADR-042 foram submetidos ao motor dialético de Mesa Redonda (`round_table_engine.py`), estabelecendo um marco metodológico no `tare.tools`:

```
                    ┌────────────────────────┐
                    │ Proposta Arquitetural  │
                    │      (ADR-042)         │
                    └───────────┬────────────┘
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
          ┌─────────────┐┌─────────────┐┌─────────────┐
          │Google Chair ││Anthropic Ch.││OpenAI Chair │
          │(Gemini 3.7) ││ (Fable 5)   ││(GPT Sol 5.6)│
          └──────┬──────┘└──────┬──────┘└──────┬──────┘
                 │              │              │
                 └──────────────┼──────────────┘
                                ▼
                    ┌────────────────────────┐
                    │ Mediador Independente  │
                    │     (Antigravity)      │
                    │  Síntese & Emendas FSM │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │    Decisão Canônica    │
                    │ (Quórum Fail-Closed)   │
                    └────────────────────────┘
```

### Resultados da Deliberação do ADR-042:
- **Rodada 1:** 3x `REVISE` (9 blockers identificados: carência de Fencing Tokens, indefinição de Single-Writer no Data Plane, acoplamento indevido no Assurance).
- **Rodada 2:** 3x `REVISE` (10 blockers identificados: exigência de sandbox rootless, Base Hash Fencing anti-drift de Git, recibos de atestação criptográfica).
- **Rodada 3:** 3x `REVISE` $\rightarrow$ Síntese de Emendas Críticas (Transactional Landing Journal, Landing Queue anti-starvation, especificação CP estrita e Tree Hash no recibo).
- **Resultado:** O consórcio tripartite convergiu na especificação formal completa, selando a versão canônica `v003`.

---

## 6. Alinhamento com a North Star do tare.tools

A North Star do `tare.tools` estabelece um princípio inegociável:

> **"Controle determinístico estrito, formalmente auditável e matematicamente fechado sobre inteligência probabilística elástica."**

A publicação deste estudo e a ratificação do **ADR-042** completam a evolução conceitual da North Star:
1. **Superação do Monolito:** O Universal Agent Harness não é um executável monolítico, mas a orquestração desacoplada dos 5 Planos.
2. **Workers como Peças Descartáveis:** Nenhuma IA possui autoridade intrínseca; a autoridade reside exclusivamente nas regras de transição da FSM do Control Plane e nos oráculos mecânicos do Assurance Plane.
3. **Escalabilidade Multi-Host Nativa:** A malha de nós heterogêneos opera de forma segura e confiável sob partição, garantida por contratos de fencing e atestação criptográfica.

---

## 7. Ameaças à Validade & Limitações Operacionais

1. **Dependência de Sandboxing Efêmero:** Ambientes Windows sem containers Linux rootless nativos exigem isolamento por processos desprivilegiados com job objects e ACLs estritas de sistema de arquivos.
2. **Latência de Merge Train:** Em momentos de pico de releases concorrentes, a fila sequencial de aterrissagem impõe uma latência de rebase proporcional ao tempo de execução dos testes de regressão no Assurance Plane.
3. **Custos de Quórum Tripartite:** A execução de deliberações dialéticas com 3 assentos frontier em alta complexidade cognitiva consome tokens substanciais, devendo ser reservada para decisões estruturais, ADRs e destravamento de impasses críticos pelo Overseer.

---

## 8. Referências & Proveniência Canônica

1. **ADR-042 Canônico:** [`docs/DECOUPLED_MICROKERNEL_ARCHITECTURE.md`](file:///C:/projects/tare-tools-relay/docs/DECOUPLED_MICROKERNEL_ARCHITECTURE.md) (Commit `28ebd60`).
2. **Artefato de Decisão da Mesa Redonda:** [`relay/round_tables/RT-ADR-042-PROD/decision/DECISION.md`](file:///C:/projects/tare-tools-relay/relay/round_tables/RT-ADR-042-PROD/decision/DECISION.md).
3. **Motor de Consenso & Mesa Redonda:** [`relay/round_table_engine.py`](file:///C:/projects/tare-tools-relay/relay/round_table_engine.py).
4. **Relatórios de Auditoria Adversarial Cruzada:**
   - OpenAI Chair: [`docs/CODEX_ADVERSARIAL_AUDIT_REPORT.md`](file:///C:/projects/tare-tools-relay/docs/CODEX_ADVERSARIAL_AUDIT_REPORT.md)
   - Anthropic Chair: [`docs/CLAUDE_ADVERSARIAL_AUDIT_REPORT.md`](file:///C:/projects/tare-tools-relay/docs/CLAUDE_ADVERSARIAL_AUDIT_REPORT.md)
   - Google Chair: [`docs/GEMINI_ADVERSARIAL_AUDIT_REPORT.md`](file:///C:/projects/tare-tools-relay/docs/GEMINI_ADVERSARIAL_AUDIT_REPORT.md)
5. **Estudo Metodológico de Implementadores:** [`research/01_methodology-research-program/2026-08-13-bounded-implementer-profile-longitudinal-study.md`](file:///C:/projects/tare.tools.research/research/01_methodology-research-program/2026-08-13-bounded-implementer-profile-longitudinal-study.md).
