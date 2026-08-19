# SPEC-SPECGRAPH-001: Living Causal Matrix & Substrate Admission Gate

- **Status:** CANONICAL_SSOT
- **Governing ADR:** [ADR-044](docs/adr/ADR-044_SPECGRAPH_NORTH_STAR_UNIVERSAL_PROJECT_INTELLIGENCE.md) / [ADR-051](docs/adr/ADR-051_RESEARCH_TRIPLE_AXIS_AND_BOOKKEEPING_GOVERNANCE.md)
- **Target Repository:** `tare.tools.specgraph`
- **Version:** 1.0.0

---

## 1. Contexto & Objetivo
Estabelece a indexação causal de código baseada em Tree-Sitter, cálculo incremental de raio de explosão (*Blast Radius*) e o Substrate Admission Gate (SAG).

---

## 2. Critérios de Aceitação Verificáveis

* **`AC-01: Causal AST Traceability`**: Indexa símbolos de código e decorações `@spec` conectando-os biunivocamente aos nós de especificação em `tare.tools.library`.
* **`AC-02: Incremental Blast Radius Cache`**: O cálculo de impacto de mudanças de arquivo deve retornar em tempo sub-5ms através de cache de dependências de símbolos.
* **`AC-03: Substrate Admission Gate (SAG)`**: Rejeita despacho de tarefas agênticas se o `code_tree_hash` divergir dos critérios de aceitação formalizados na SSOT.
* **`AC-04: Surgical Context Envelopes`**: O gerador de envelopes de contexto deve produzir payloads com menos de 4.000 tokens focados exclusivamente no grafo causal da tarefa.
