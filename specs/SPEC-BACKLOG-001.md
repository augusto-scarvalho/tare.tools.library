# SPEC-BACKLOG-001: Mathematical Task DAG & Atomic CAS Concurrency

- **Status:** CANONICAL_SSOT
- **Governing ADR:** [ADR-046](docs/adr/ADR-046_BACKLOG_GRAPH_NORTH_STAR.md) / [ADR-051](docs/adr/ADR-051_RESEARCH_TRIPLE_AXIS_AND_BOOKKEEPING_GOVERNANCE.md)
- **Target Repository:** `tare.tools.backlog-graph`
- **Version:** 1.0.0

---

## 1. Contexto & Objetivo
Implementa o motor matemático de DAG de tarefas com cálculo de fronteira $O(1)$ e FSM finita com propagação atômica de reabertura em cascata (*Atomic Reopen Cascade*).

---

## 2. Critérios de Aceitação Verificáveis

* **`AC-01: Pure Python Stdlib Core`**: O motor de grafo de tarefas não possui dependências externas pesadas (sem NetworkX em runtime crítico).
* **`AC-02: O(1) Execution Frontier`**: O cálculo de tarefas elegíveis para despacho é indexado em $O(1)$ mantendo a lista de dependências resolvidas atualizada a cada mutação.
* **`AC-03: Atomic Reopen Cascade`**: Se um nó pai for reaberto (`status -> IN_PROGRESS`), todos os nós descendentes já concluídos são automaticamente e atomicamente invalidados.
* **`AC-04: CAS Leased Transitions`**: Transições de estado exigem `task_version` compatível (CAS), impedindo concorrência desordenada entre agentes em paralelo.
