# SPEC-KERNEL-001: 5-Plane Decoupled Microkernel & CAS State Engine

- **Status:** CANONICAL_SSOT
- **Governing ADR:** [ADR-045](docs/adr/ADR-045_ECOSYSTEM_AND_KERNEL_NORTH_STAR.md)
- **Target Repository:** `tare.tools.kernel`
- **Version:** 1.0.0

---

## 1. Contexto & Objetivo
Define a arquitetura do microkernel desacoplado em 5 planos (Control, Compute, Data, Assurance, Experience) com persistência atômica Compare-And-Swap (CAS) em SQLite WAL.

---

## 2. Critérios de Aceitação Verificáveis

* **`AC-01: 5-Plane Boundary Enforcement`**: Nenhuma chamada do Compute Plane pode acessar credenciais de rede ou o Data Plane diretamente sem mediação do Control Plane.
* **`AC-02: Single-Writer Atomic CAS`**: Todas as mutações de estado devem usar transações `BEGIN IMMEDIATE` com verificação de `rowcount == 1` garantindo zero split-brain sob concorrência.
* **`AC-03: Hermetic Sandboxed Execution`**: Processos em execução no Compute Plane devem rodar em ambiente isolado (Windows Job Objects / bwrap) com limites de memória e timeout estritos.
* **`AC-04: Cryptographic Envelope Attestation`**: Toda saída de execução deve ser acompanhada de digest SHA-256 e recibo de atestação.
