# SPEC-LIBRARY-001: Central SSOT Library, Bookkeeper & Hybrid Substrate

- **Status:** CANONICAL_SSOT
- **Governing ADR:** [ADR-051](docs/adr/ADR-051_RESEARCH_TRIPLE_AXIS_AND_BOOKKEEPING_GOVERNANCE.md) / [ADR-052](docs/adr/ADR-052_IDENTITY_TRANSITION_TO_LIBRARY_AND_CORPUS_GOVERNANCE.md)
- **Target Repository:** `tare.tools.library`
- **Version:** 1.0.0

---

## 1. Contexto & Objetivo
Estabelece a governança da biblioteca técnica central, ferramentas automatizadas de higiene documental (Bookkeeper) e exportação do manifesto canônico para a federação.

---

## 2. Critérios de Aceitação Verificáveis

* **`AC-01: Zero Duplicate Tolerance`**: O detector de duplicatas deve auditar todo novo documento ingerido, rejeitando similaridades $>90\%$ sem autorização forçada.
* **`AC-02: SSOT Uniqueness Enforcement`**: A biblioteca nunca pode conter mais de 1 documento ativo com status `CANONICAL_SSOT` para o mesmo identificador de tópico.
* **`AC-03: Machine-Readable Manifest Export`**: O compilador de manifesto deve gerar `catalog/LIBRARY_MANIFEST.json` com hashes SHA-256 e critérios de aceitação extraídos em $O(1)$.
* **`AC-04: Zero-Cost Substrate Compatibility`**: As operações de auditoria, busca e catalogação não podem depender de APIs pagas em ambiente de desenvolvimento local.
