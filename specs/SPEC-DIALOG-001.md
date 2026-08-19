# SPEC-DIALOG-001: Topological Dialogue Engine & Statechart Protocol

- **Status:** CANONICAL_SSOT
- **Governing ADR:** [ADR-047](docs/adr/ADR-047_DIALOG_ENGINE_NORTH_STAR.md)
- **Target Repository:** `tare.tools.dialog-engine`
- **Version:** 1.0.0

---

## 1. Contexto & Objetivo
Especifica o motor topológico de conversação, máquinas de estado hierárquicas (Statecharts) e fuzzer de protocolo de diálogo agnóstico a schemas.

---

## 2. Critérios de Aceitação Verificáveis

* **`AC-01: Schema-Agnostic Ingestion`**: O parser de diálogo converte transcrições brutas em AST canônico sem acoplamento a formatos proprietários de fornecedores.
* **`AC-02: Statechart Turn Transitions`**: Estados conversacionais (Dispute, Convergence, Questioning, Consensus) seguem matriz de transição finita e determinística.
* **`AC-03: Multi-Seat Quorum Evaluation`**: Vereditos de deliberação agêntica exigem quórum configurável com pontuações de confiança explícitas.
