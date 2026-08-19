# 📓 DIÁRIO DE DIRETRIZES, PERGUNTAS & DECISÕES ARQUITETURAIS — TARE.TOOLS

> **Registro contínuo, cronológico e auditável de todas as perguntas do Operador Humano e formulações arquiteturais alinhadas durante as sessões de evolução do ecossistema `tare.tools`.**

---

## 📅 Sessão: 19 de Agosto de 2026

### ❓ Pergunta 1: *“ficou meio confuso o diagrama. poderia ser mais reto, horizontal. também poderia generalizar os modelos das cadeiras”*
* **Contexto:** Diagramas de governança da Mesa Redonda Tripartite nos READMEs.
* **Decisão & Resposta:** 
  * Convertidos os fluxogramas verticais para `flowchart LR` (horizontais, mais legíveis).
  * Generalizados os nomes das cadeiras para seus papéis funcionais (*Google Chair / Frontier Reasoning*, *Anthropic Chair / Frontier Safety & AST*, *OpenAI Chair / Frontier Architecture*) sem amarrar a sub-versões efêmeras dos modelos.

---

### ❓ Pergunta 2: *“o readme do nosso tare.tools.kernel tá meio que duplicando informações do OS... quero que você atualize ele com conteúdo relevante e diagramas mais bonitos”*
* **Contexto:** README do `tare.tools.kernel` com responsabilidade sobreposta ao `tare.tools.os`.
* **Decisão & Resposta:**
  * O `tare.tools.kernel` foi refocado estritamente na sua responsabilidade: **Microkernel em 5 Planos** (`control`, `compute`, `data`, `assurance`, `experience`), persistência CAS em SQLite WAL e sandboxing `bwrap`.
  * Toda a orquestração do enxame foi mantida como prerrogativa exclusiva do `tare.tools.os`.

---

### ❓ Pergunta 3: *“e o specgraph, não podemos dar um banho de loja no readme e adicionar diagramas relevantes?”*
* **Contexto:** README do `tare.tools.specgraph` com caixas ASCII antigas.
* **Decisão & Resposta:**
  * Modernizado com diagramas Mermaid da **Matriz Causal Viva**, cálculo incremental de **Blast Radius (sub-5ms)** e empacotamento de **Context Envelopes** para LLMs.

---

### ❓ Pergunta 4: *“nosso dialog-engine merece o mesmo tratamento”*
* **Contexto:** Documentação e diagramas do `tare.tools.dialog-engine`.
* **Decisão & Resposta:**
  * Reescrito com Mermaid destacando o **Schema Adapter Universal**, validação estática em 12 fases e fuzzer de mutação simbólica.

---

### ❓ Pergunta 5: *“um deu erro — Unable to render rich display. Cannot read properties of undefined (reading 'render')”*
* **Contexto:** Falha do renderizador de Mermaid no GitHub.
* **Causa Raiz Identificada:** 
  1. Uso de tags HTML não-fechadas ou brutas (`<code>`, `<b>`) dentro de rótulos de nós.
  2. Atribuição de classes CSS a identificadores de `subgraph`.
  3. Uso do tipo experimental `timeline` (não suportado pelo GitHub).
* **Decisão & Resposta:**
  * Saneados 100% dos blocos Mermaid em todos os 6 repositórios; convertidas timelines para `flowchart LR` e tags para `<br/>` estrito.

---

### ❓ Pergunta 6: *“aqui em Enterprise Hierarchical (nos, filhos, condicao, slots) . não usa assim... tem que ser algo mais genérico, tipo Custom Enterprise Schemas e aí você inventa um schema”*
* **Contexto:** Chaves proprietárias de produção no exemplo do Schema Adapter do Dialog Engine.
* **Decisão & Resposta:**
  * Substituído por nomenclatura canônica e agnóstica: **`Custom Enterprise Schemas (flow_nodes, subflows, predicates, memory_frame)`** em inglês e português.

---

### ❓ Pergunta 7: *“o nosso tare.tools.harness também merece banho de loja, mesmo estando congelado... leve pra dentro do readme um resumo do post mortem e da análise do que vai ser reaproveitado ou não”*
* **Contexto:** Repositório legado do protótipo monolítico.
* **Decisão & Resposta:**
  * Adicionado badge e aviso de **FROZEN & ARCHIVED**.
  * Criada a **Matriz de Herança Dourada**:
    - *Reaproveitado:* SDD (`specgraph`), DAG Backlog (`backlog-graph`), AST Statecharts (`dialog-engine`), Sandboxing (`kernel`), Mesa Redonda (`os`).
    - *Aposentado:* Monolito de 186 módulos, hooks de terminal por vendor CLI, prompt stuffing no `AGENTS.md`, JSON em disco sem CAS.
  * Publicado PR #42 e #43 com post-mortem forense completo em `docs/POST_MORTEM_AND_ARCHITECTURAL_PIVOT.md`.

---

### ❓ Pergunta 8: *“a parte de GPU tá errado. a gente tem 2 projetos específicos pra isso agora e não tinha nada disso acoplado no harness antigo, sempre foi side project. os experimentos ficavam orquestrados e documentados no harness e talvez isso seja vocação pro research”*
* **Contexto:** Correção conceitual sobre o papel do laboratório de GPU vs orquestração de pesquisas.
* **Decisão & Resposta:**
  * Desacoplado 100% o laboratório de GPU do histórico do harness.
  * Definida a verdadeira vocação do `tare.tools.research`: receber a **orquestração de pesquisas empíricas**, protocolos de benchmark (CMRP, auditorias de tokens) e a memória científica do ecossistema.

---

### ❓ Pergunta 9: *“qual seria a vocação do tare.tools.research? hoje lá tem um viés mais de relatório científico e publicação, mas a gente pode ser mais flexível... não seria o lugar certo para documentos importantes?”*
* **Contexto:** Fragmentação documental e rigidez excessiva do repositório de pesquisa.
* **Decisão & Resposta:**
  * O `tare.tools.research` torna-se a **Biblioteca Central de Conhecimento, Memória e Arquivo (Knowledge Hub)** de todo o ecossistema.
  * Abriga: ADRs globais (001 a 050), post-mortems de incidentes, whitepapers de arquitetura, benchmarks empíricos e arquivo histórico.
  * Libera os satélites de código para terem apenas documentação operacional leve.

---

### ❓ Pergunta 10: *“hoje a gente tem documentos fragmentados, duplicados ou com pouquíssimas diferenças... como o tare.tools.research poderia resolver esse problema? talvez com módulos de book keeping?”*
* **Contexto:** Drift documental e versões conflitantes espalhadas.
* **Decisão & Resposta:**
  * Criação do **Motor de Bookkeeping** (`tools/bookkeeper/`) no `tare.tools.research`:
    1. **`dedup_detector.py`:** Detecta quase-duplicatas (>70% de similaridade) e alerta sobre drifts.
    2. **`ssot_registry.py`:** Garante 1 único documento canônico ativo por `doc_id`.
    3. **`tombstone_manager.py`:** Substitui duplicatas por ponteiros inteligentes sem quebrar links.
    4. **`freshness_audit.py`:** Audita se as especificações estão sincronizadas com os commits dos satélites.

---

### ❓ Pergunta 11: *“e como fonte do conhecimento histórica, como ele funcionaria? vai anotando minhas perguntas e suas respostas ai mano :<”*
* **Contexto:** Modelo de funcionamento como repositório de memória viva e geologia do conhecimento.
* **Decisão & Resposta:** 
  * Estruturação em **3 Camadas Geológicas**:
    1. *Camada 1 (Memória Fóssil Imutável):* Transcrições brutas e handoffs históricos em `archaeology/raw/` com hashes SHA-256.
    2. *Camada 2 (Linhagem & Rastreabilidade):* Árvore genealógica de decisões em `catalog/lineage/`.
    3. *Camada 3 (Oráculo Histórico):* CLI de consulta `query_history.py` com tarja automática `[HISTORICAL RECORD]` para evitar alucinações regressivas dos agentes.
  * Criação do **Diário de Sessão Contínuo** (`ARCHITECTURAL_QA_LEDGER.md`).

---

### ❓ Pergunta 12: *“quais problemas você consegue perceber quando olha para os documentos dentro dos nossos repositórios?”*
* **Contexto:** Análise crítica e forense das patologias documentais no ecossistema (1078 docs no OS, 463 no Research, 721 no Harness).
* **Decisão & Resposta:** Identificadas **7 patologias documentais concretas**:
  1. *Anarquia de Metadados:* Falta de schema único de frontmatter.
  2. *Dilema do Gêmeo Bilíngue:* Descompasso entre versões PT-BR e EN.
  3. *Poluição por Rascunhos Intermediários:* `v001..v003` competindo com o `DECISION.md` canônico.
  4. *Hiper-Fragmentação (Micro-Docs):* 7 mini-políticas de 1 página em vez de 1 manual coeso.
  5. *Links Quebrados & Caminhos Hardcoded:* Referências relativas e absolutas desatualizadas.
  6. *Histórico Presentificado:* Transcrições antigas sem tarja de arquivo induzindo agentes a erro.
  7. *Desconexão Teoria vs Realidade:* Rigor acadêmico excessivo afastando a documentação do ritmo de engenharia.

---

### ❓ Pergunta 13: *“tem experimentos mas não tem papers pra algo mais formal”*
* **Contexto:** Constatação da falta de sintetização dos dados brutos em artigos estruturados.
* **Decisão & Resposta:** 
  * Criação de pasta `papers/` sob demanda do operador humano para consolidar os dados empíricos em artigos no padrão internacional.
  * Mapeados 4 grandes temas fundacionais: Governança & Deadlocks, Dieta de Contexto AST, Substratos Locais de Custo Zero e Teste Metamórfico de Statecharts.

---

### ❓ Pergunta 14: *“a gente não é obrigado a publicar as coisas em formato de papers. eles seriam produzidos sob demanda, por mim. a obrigação dos agentes é documentar a coisa certa, no lugar certo na hora certa”*
* **Contexto:** Definição do Mandato Primário dos Agentes de IA vs. Papel do Operador Humano.
* **Decisão & Resposta (Invariante Constitucional):**
  * **Regra Inviolável:** Papers acadêmicos/formais são prerrogativa humana produzidos sob demanda pelo Operador.
  * **O Mandato Primário dos Agentes:** *“Documentar a coisa certa, no lugar certo, na hora certa”*:
    1. *No Satélite:* Documentação operacional enxuta de APIs, CLI e testes.
    2. *Nos Incidentes/Post-Mortems:* Registrar fatos, métricas e lições em `research/docs/post-mortems/`.
    3. *Nos Benchmarks:* Registrar evidências e logs em `research/experiments/`.
    4. *Nas Decisões Globais:* Registrar ADRs canônicas em `research/docs/adr/`.
    5. *Na Higiene:* Eliminar duplicatas e manter o Bookkeeper rodando sem gerar overhead burocrático.

---

### ❓ Pergunta 15: *“como o tare.tools.research se interliga com o nosso ecossistema agora. consegue ter essa visão?”*
* **Contexto:** Mapeamento holístico das interconexões operacionais, de dados e de governança entre o `tare.tools.research` e todos os repositórios/nós do ecossistema.
* **Decisão & Resposta:** O `tare.tools.research` atua como o **Sistema Nervoso de Memória & Rastreabilidade** conectado a cada componente:
  1. *Com tare.tools.os:* Arquiva deliberações ratificadas da Mesa Redonda e histórico de telemetria agêntica.
  2. *Com tare.tools.kernel:* Fornece as especificações dos 5 planos e recebe receipts de auditoria/segurança.
  3. *Com tare.tools.specgraph:* Alimenta a Matriz Causal viva (ligando ADRs a nós de AST) e fornece métricas de dieta de contexto.
  4. *Com tare.tools.backlog-graph:* Origina os pacotes de tarefas (*DoD*) derivados de ADRs e post-mortems.
  5. *Com tare.tools.dialog-engine:* Preserva os benchmarks de teste metamórfico e validação estática.
  6. *Com o Nó Físico aaaaa (RTX 3090 / slop.cpp):* Registra os dados empíricos de benchmarks CUDA (EXP-01..05).
  7. *Com o Operador Humano:* Interface visual única via GitHub Pages.

---

### ❓ Pergunta 16: *“nosso specgraph aqui não tá muito mais poderoso como uma ferramenta de indexação, inclusive semântica?”*
* **Contexto:** Reconhecimento do SpecGraph não apenas como analisador de código, mas como o **Motor Unificado de Indexação Causal & Semântica** de todo o ecossistema.
* **Decisão & Resposta:**
  * O SpecGraph já possui os parsers de `adr_parser.py`, `spec_parser.py`, `schema_parser.py`, `code_parser.py` e `graph.py`.
  * **O Papel Unificado do SpecGraph:** Indexar tanto o código dos satélites quanto o acervo documental do `tare.tools.research`.
  * Cria o **Grafo Causal Contínuo:** `ADR / Post-Mortem ➔ Contrato ➔ AST de Código ➔ Teste Falsificador`.
  * Permite que agentes façam consultas de impacto (*Blast Radius*) e recuperem fatias cirúrgicas de conhecimento em $<5\text{ms}$ sem desperdício de tokens.

---

### ❓ Pergunta 17: *“como a indexação semântica é feita?”*
* **Contexto:** Explicação técnica e arquitetural dos mecanismos internos de indexação semântica e causal no SpecGraph.
* **Decisão & Resposta:** A indexação semântica opera em **4 Camadas Integradas**:
  1. *Camada 1 (Parsing Estrutural AST):* Extrai o significado de blocos em Markdown (Objetivos, Não-Objetivos, Status) e código via AST/Tree-Sitter (Classes, Funções, Docstrings, Anotações `@spec`).
  2. *Camada 2 (Síntese Causal em Grafo):* Conecta nós com arestas tipadas (`GOVERNS`, `IMPLEMENTS`, `VERIFIES`, `SUPERSEDES`).
  3. *Camada 3 (Recuperação Híbrida Léxica + Vetorial):* Combina busca densa por significado conceitual com travessia de grafo.
  4. *Camada 4 (Cache Incremental CAS sub-1ms):* Indexação incremental baseada em hash SHA-256.

---

### ❓ Pergunta 18: *“não utilizaremos ontologias, grafos ontológicos e nem indexação vetorial? imagine que nem todo documento será uma spec / adr”*
* **Contexto:** Necessidade de indexar documentos livres, rascunhos, transcrições de chat, papers externos e pesquisas que não seguem o formato rígido de spec/ADR.
* **Decisão & Resposta (Arquitetura de Grafo Ontológico Híbrido):**
  * **Sim, utilizaremos Ontologias, Grafos Ontológicos e Indexação Vetorial Densa!**
  * A arquitetura de indexação opera em um **Substrato Híbrido Tripartite**:
    1. *Camada Vetorial Densa (Vector Embeddings):* Indexa qualquer texto livre, chats e notas exploratórias por significado latente.
    2. *Grafo Ontológico do Ecossistema (Knowledge Graph):* Mapeia conceitos universais (`Concorrência`, `Isolamento`, `Token Diet`, `Deadlocks`) e suas relações semânticas (`is-a`, `mitigates`, `implements`, `motivates`).
    3. *Grafo Causal AST (SpecGraph):* Subgrafo de alta precisão que ancora os conceitos abstratos em código executável e testes.
  * Todo e qualquer documento livre é ancorado no Grafo Ontológico através de *Entity & Concept Extraction*, permitindo consultas semânticas holísticas.

---

### ❓ Pergunta 19: *“tá anotando aí?”*
* **Contexto:** Confirmação da persistência contínua de todas as perguntas, diretrizes e respostas no Livro Mestre.
* **Decisão & Resposta:** 
  * 100% de todas as 19 perguntas e formulações da sessão foram catalogadas cronologicamente, com contexto e decisão formal no [`ARCHITECTURAL_QA_LEDGER.md`](file:///C:/projects/tare.tools.research/docs/ARCHITECTURAL_QA_LEDGER.md).

---

### ❓ Pergunta 20: *“nós temos LLMs locais e a camada free da gemini API e NVIDIA BUILD API para gerar resumos ou processar documentações também viu.”*
* **Contexto:** Alavancagem do arsenal de computação e inferência de custo zero para processamento em lote, geração de embeddings, resumos e manutenção do Bookkeeper.
* **Decisão & Resposta (Orquestração do Triplo Substrato de Custo Zero):**
  1. *Substrato Local (Workstation aaaaa / RTX 3090 / slop.cpp):* Processamento offline 24/7, verificação contínua de drifts e deduplicação sem limites de rate ou custo financeiro.
  2. *Gemini API Free Tier (Janela de 1M+ tokens):* Ingestão em lote de transcrições massivas de chats e extração de entidades ontológicas.
  3. *NVIDIA Build API (NIMs & NV-Embed):* Geração de embeddings vetoriais densos de alta dimensão e reranking semântico.
### ❓ Pergunta 21: *“com esse novo refinamento, como ficaria o eixo triplo de tare.tools.specgraph + tare.tools.backlog-graph + tare.tools.research ?”*
* **Contexto:** Definição da sinergia operacional e do fluxo fechado entre os três pilares de inteligência do ecossistema.
* **Decisão & Resposta (O Eixo Triplo da Engenharia Agêntica):**
  1. *🔬 tare.tools.research (O "Porquê" / Memória & Conhecimento):* O repositório canônico de ADRs, decisões, post-mortems, experimentos e ontologia.
  2. *📊 tare.tools.backlog-graph (O "Quando" e "O Quê" / Ordem & Execução):* O motor de DAG determinístico que decompõe ADRs em nós executáveis com pré-requisitos matemáticos e transições atômicas CAS.
### ❓ Pergunta 22: *“como isso se alinha com nossos north stars atuais?”*
* **Contexto:** Mapeamento de conformidade total do novo modelo refinado com as 7 North Stars constitucionais (ADRs 044 a 050).
* **Decisão & Resposta (Matriz de Alinhamento Constitucional com as 7 North Stars):**
  1. *ADR-044 (SpecGraph):* Fortalece a Matriz Causal viva ligando ADRs do `research` ao código AST dos satélites.
  2. *ADR-045 (Microkernel 5-Planos):* Mantém os contratos imutáveis v1 e isolamento de planos; o `research` documenta a arquitetura sem acoplamento de runtime.
  3. *ADR-046 (Backlog Graph):* O DAG consome os requisitos das ADRs para gerar a fronteira de execução $O(1)$ via CAS.
  4. *ADR-047 (Dialog Engine):* Preserva o motor agnóstico de esquemas e o fuzzer de mutação formal.
  5. *ADR-048 (Local Inference & slop.cpp):* Usa a RTX 3090 no nó `aaaaa` para rodar o Bookkeeper e os implementers a custo zero de tokens.
### ❓ Pergunta 23: *“ótimo. bora mandar pra mesa redonda correta avaliar”*
* **Contexto:** Submissão formal da proposta ADR-051 à Mesa Redonda Tripartite (`CASE-2026-08-19-RESEARCH-TRIPLE-AXIS-AND-BOOKKEEPER`) com quórum Google Chair, Anthropic Chair e OpenAI Chair sob o perfil `north_star`.
* **Decisão & Resposta (Síntese Canônica Ratificada v004):**
  * A Mesa Redonda concluiu os 3 ciclos de auditoria adversarial e refinou a proposta para a versão canônica **`v004` (SHA-256: `d3ca7c4e...`)**, integrando 4 proteções críticas:
    1. **Substrate Admission Gate (SAG):** O SpecGraph atua como gatekeeper que impede transição de tarefas se o hash da árvore de código divergir da especificação ativa no `research`.
    2. **TrustedKeyRegistry:** Resolução criptográfica Ed25519 com checagem de escopo e revogação de chaves.
    3. **FSM Estrita & Atomic Reopen Cascade:** O Backlog Graph formaliza matriz de transição finita e cascata atômica de invalidação caso nós pais sejam reabertos.
### ❓ Pergunta 24: *“mais uma questão para a round table... Vamos manter o nome tare.tools.research (acho o nome tare.tools.library mais adequado)? vamos reutilizar esse mesmo repositório ou criar outro? o que vamos fazer com os documentos e estudos do tare.tools.research atual? e sobre formatos de experimento e publicação, vamos reutilizar ou criar algo novo?”*
* **Contexto:** Alinhamento estratégico sobre a identidade (`tare.tools.library` vs `research`), preservação do acervo já pré-consolidado, ciclo de vida do repositório Git e reutilização de formatos enxutos sem hipertrofia técnica.
* **Teses Ratificadas (ADR-052):**
  1. *Identidade & Naming:* Transição para `tare.tools.library` (reflete com fidelidade a Biblioteca Central de Conhecimento e SSOT).
  2. *Ciclo de Vida do Repositório:* Reutilização in-place do repositório Git existente renomeado no GitHub (preservando todos os PRs, testes e histórico).
  3. *Governança do Acervo Atual:* Os 93 documentos do acervo histórico ficam em `archaeology/corpus/` sob cadeia de custódia (`PRE_MIGRATION_MANIFEST.sha256`) com tag `status: archived_immutable`, sem retrabalho redundante.
  4. *Formatos de Experimento:* Padrão enxuto `EXP-XXX-slug.md` (Hipótese, Setup, Métricas, Veredito) e Markdown/Mermaid no GitHub Pages.

---

### ❓ Pergunta 25: *“bora. aproveita e dá aquele banho de loja no repositório e já coloca as propostas em prática”*
* **Contexto:** Execução imediata da reestruturação completa e modernização do repositório conforme as diretrizes ratificadas nas ADRs 051 e 052.
* **Execução & Implementação Concluída:**
  1. *Renomeação Oficial no GitHub:* Repositório renomeado com sucesso para [`https://github.com/augusto-scarvalho/tare.tools.library`](https://github.com/augusto-scarvalho/tare.tools.library).
  2. *Motor de Bookkeeping Implementado:* Criado o pacote `tools/bookkeeper/` (`dedup_detector.py`, `ssot_registry.py`, `tombstone_manager.py`, `cli.py`) e suíte de testes 100% green (`tests/test_bookkeeper.py`).
  3. *Acervo e Arqueologia Estruturados:* Criados `archaeology/README.md`, `experiments/README.md` (tabela de ensaios com vereditos) e template oficial `docs/templates/EXP-template.md`.
  4. *Modernização Completa dos READMEs:* `README.md` e `README.en.md` reescritos com o Eixo Triplo, badges de CI e mapa de navegação moderno.
  5. *Federação Sincronizada:* Submódulo do Agent OS atualizado e validado via `bump_satellite.py` (71/71 testes passando green).
