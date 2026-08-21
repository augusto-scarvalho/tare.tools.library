# 🏺 Acervo Arqueológico & Memória Fóssil (tare.tools.library)

> [!NOTE]
> **[HISTORICAL RECORD — IMMUTABLE]**
> Todos os arquivos contidos neste diretório e no diretório `corpus/` constituem a memória fóssil e arqueológica da evolução do ecossistema TARE.
> **Status:** `ARCHIVED_IMMUTABLE`

---

## 1. Princípios de Governança (ADR-051 & ADR-052)

1. **Cadeia de Custódia Imutável:** Os documentos presentes neste acervo já foram consolidados, filtrados e sintetizados em dezenas de sessões anteriores. Eles são mantidos de forma estática e imutável para fins de auditoria histórica.
2. **Isolamento de RAG / SpecGraph:** Indexadores de busca semântica marcam todos os nós originados neste diretório com a tag `status: archived_immutable`. Buscas ativas de engenharia priorizam a documentação viva em `docs/` e `experiments/`, evitando poluição de contexto ou alucinações regressivas.
3. **Ponteiros & Tombstones:** Documentos históricos que foram unificados ou substituídos por decisões formais possuem referências diretas para suas respectivas ADRs canônicas em `docs/adr/`.

---

## 2. Mapa do Acervo

* **`archaeology/chats/`:** Transcrições históricas de sessões de design e alinhamento conceitual.
* **`archaeology/architectural-evolution/`:** Registros de transição de arquitetura de versões preliminares.
* **`archaeology/implementation-sessions/`:** Logs e memórias de sessões de implementação.
* **`corpus/canonical-snapshot/`:** Snapshot canônico de 93 documentos consolidados com manifestos SHA-256.
