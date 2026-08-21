---
id: ADR-059
title: Matriz de Curadoria do Acervo Histórico do SpecGraph, Escopo Operacional e Isolamento de Snapshot
status: Ratificado
date: 2026-08-20
authors: Antigravity Mediator (Consenso Tripartite: Google Gemini 3.7 Flash High, Anthropic Claude Fable 5 High, OpenAI GPT-5.6 Sol Pro; sob governança do Operador Humano)
scope: tare.tools.specgraph & tare.tools.library
round_table_case: CASE-2026-08-20-SPECGRAPH-CURATION-AND-SCOPE
round_table_sha256: e2c2b01abae3b8c71516fbaa3ae6e4b90c993112a004fb84f3a2f5da0fbf6e4d
---

# ADR-059: Matriz de Curadoria do Acervo Histórico do SpecGraph, Escopo Operacional e Isolamento de Snapshot

## 1. Contexto e Motivação
A análise forense do acervo histórico do SpecGraph (`C:\Users\augus\OneDrive\Documentos\projetos\SpecGraph`, Julho/2026) revelou 70 documentos de pesquisa, 9 estágios OpenSDD/EARS e 10 protótipos de interface, contrastando com a implementação operacional em Python puro (`C:\projects\tare.tools.specgraph`, Agosto/2026) com 68 testes unitários passando.

Este ADR consolida a deliberação soberana de 4 rodadas da Mesa Redonda Tripartite (`CASE-2026-08-20-SPECGRAPH-CURATION-AND-SCOPE`), estabelecendo a **Matriz Normativa de Curadoria**, as **Invariantes Transacionais de Leitura e Publicação** e o **Plano de Implementação em 4 Passos** sob o princípio de **Zero Hipertrofia Técnica & Zero Burocracia Cartorial**.

---

## 2. Decisão Arquitetural

### 2.1. Matriz Canônica de Curadoria do Acervo Histórico

| Artefato / Decisão | Origem (OneDrive) | Classificação Normativa | Justificativa Técnica & Ação Canônica |
| :--- | :--- | :---: | :--- |
| **D1 (Rust-Core / PyO3)** | Doc 08 / ADR-024 | **DIFERIDO** (*Deferred*) | Python puro atende $< 50	ext{ms}$ em 100k LOC. **Gatilho de promoção:** `specgraph bench` p95 $> 500	ext{ms}$ sobre 100 amostras em 2 execuções consecutivas no perfil de referência. |
| **D2 (Model2Vec / ONNX EP)** | Doc 08 / ADR-025 | **PESQUISA_DOCUMENTAL** | Sem caso de uso semântico ativo. Arquivado em `docs/research/` até spec de busca vetorial. |
| **D3 (DuckDB & LanceDB)** | Doc 08 / ADR-025 | **PESQUISA_DOCUMENTAL** | SQLite WAL atende 100% da escala ($10^3$–$10^4$ símbolos). LanceDB diferido para $> 1	ext{M}$ vetores. |
| **Estágios 000 a 030** | `specs/000..030` | **VIGENTE / ATIVO** | Importados em `specs/` (Constituição, Benchmark, Repo Map, Context Compiler). |
| **Estágio 040 (Reviewer Bundle)**| `specs/040` | **PROXIMA_FATIA** | Rascunho ativo para implementação imediata via dogfooding interno. |
| **Estágios 050 a 080** | `specs/050..080` | **PESQUISA_DOCUMENTAL** | Curation Brier, Agent Control Plane e Memória Temporal arquivados em `docs/research/`. |
| **Protótipos de UI 01 a 05** | `assets/prototypes/` | **PROXIMA_FATIA** | Referência visual para o visualizador Single-File HTML do Passo 4. |
| **Protótipos de UI 06 a 08** | `assets/prototypes/` | **PESQUISA_DOCUMENTAL** | Arquivados em `assets/prototypes/archived/`. |

---

### 2.2. Invariantes Transacionais de Leitura e Publicação (SQLite WAL & MCP)

1. **Publicação Atômica Monotônica (Escrita):**
   Toda reindexação (`specgraph index` ou `sync-cache`) executa em transação exclusiva `BEGIN IMMEDIATE`:
   - Aloca `revision_seq = COALESCE(MAX(revision_seq), 0) + 1` (inteiro monotônico).
   - Insere nós e arestas e calcula `content_hash = sha256(canonical_graph_jcs)`.
   - Remove a geração antiga mantendo histórico $K=1$.
   - Executa `PRAGMA wal_checkpoint(TRUNCATE)` como manutenção pós-commit *best-effort* (degradando para PASSIVE sob contenção sem invalidar o commit).

2. **Isolamento Estrito de Snapshot no MCP Server (Leitura):**
   Toda chamada MCP (`get_context_envelope`, `query_causal_graph`, `check_drift`) é encapsulada em transação explícita `BEGIN DEFERRED ... COMMIT/ROLLBACK`:
   - Todas as leituras ocorrem sob o mesmo snapshot imutável de WAL.
   - Toda resposta anexa obrigatoriamente `revision_seq` (ordenação causal) e `content_hash` (identidade de conteúdo).

---

### 2.3. Ordem Linear de Implementação (4 Passos)

1. **Passo 1: Servidor MCP Nativo (`src/specgraph/mcp_server.py`):**
   * Ferramentas read-only com envoltório transacional: `get_context_envelope`, `query_causal_graph`, `check_drift`.
2. **Passo 2: Reviewer Context Bundle (`specgraph review-bundle <GIT_REF>`):**
   * Validado primeiro no repositório `tare.tools.specgraph` via dogfooding com specs 000–030.
3. **Passo 3: Mapeamento da Library (`specgraph.yaml` em `tare.tools.library`):**
   * Vinculação das specs canônicas aos módulos reais.
4. **Passo 4: Visualizador Single-File HTML (`specgraph report --html`):**
   * Dashboard interativo 100% offline (zero CDN).

---

## 3. Via Negativa Ratificada
* **Zero compilação nativa:** Instalação e execução permanecem em Python puro sem C/Rust compilers no Windows 11.
* **Storage único:** SQLite WAL + JSON em disco. Zero DuckDB/LanceDB/Neo4j no runtime operacional.
* **Zero ceremony:** Apenas 4 estágios ativos; o restante é preservado como patrimônio histórico consultivo.
