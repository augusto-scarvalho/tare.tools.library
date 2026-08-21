# 🏺 Acervo Arqueológico & Memória Histórica (tare.tools.library)

> [!NOTE]
> **[HISTORICAL RECORD — IMMUTABLE]**
> Todos os arquivos contidos neste diretório e no acervo de transição constituem a memória histórica da evolução do ecossistema TARE.
> **Status:** `ARCHIVED_IMMUTABLE`

---

## 1. Princípios de Governança (ADR-051, ADR-052 & ADR-066 / RFC-007)

1. **Cadeia de Custódia Imutável:** Os documentos presentes neste acervo já foram consolidados, filtrados e sintetizados em dezenas de sessões anteriores.
2. **Segregação do Sovereign Vault (ADR-066 / RFC-007):** Transcrições brutas de chats e notas privadas do Operador Humano foram permanentemente expurgadas do Git e são mantidas sob custódia criptográfica exclusiva no Sovereign Vault do nó `aaaaa`.
3. **Isolamento de RAG / SpecGraph:** Indexadores de busca semântica marcam todos os nós originados neste diretório com a tag `status: archived_immutable`. Buscas ativas de engenharia priorizam a documentação viva em `docs/` e `catalog/`, evitando poluição de contexto ou alucinações regressivas.
4. **Ponteiros & Tombstones:** Documentos históricos que foram unificados ou substituídos por decisões formais possuem referências diretas para suas respectivas ADRs canônicas em `docs/adr/`.

---

## 2. Estrutura do Acervo

* **`docs/archive/archaeology/`:** Metadados e recibos históricos de bootstrap.
* **`docs/archive/editorial-editions/`:** Snapshots de edições editoriais passadas.
* **`docs/archive/refresh-editions/`:** Edições consolidadas de refresh científico.
* **`catalog/corpus/`:** Corpus de artefatos canônicos ingeridos com manifestos SHA-256.
