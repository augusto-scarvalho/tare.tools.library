# SPEC-XXX: [Nome Sucinto da Especificação]

- **Status:** CANONICAL_SSOT
- **Governing ADR:** [ADR-XXX](docs/adr/ADR-XXX.md)
- **Target Repository:** `tare.tools.<satellite>`
- **Version:** 1.0.0
- **Authors:** Google Deepmind Antigravity Agent & Augusto S. Carvalho

---

## 1. Contexto & Objetivo
[Descrição sucinta da necessidade arquitetural e por que esta especificação existe.]

---

## 2. Contrato de Interface & Estruturas de Dados

```python
# Exemplo de assinatura ou contrato
```

---

## 3. Critérios de Aceitação Verificáveis (Acceptance Criteria)

* **`AC-01`**: [Descrição determinística do primeiro critério de aceitação]
* **`AC-02`**: [Descrição determinística do segundo critério de aceitação]
* **`AC-03`**: [Critério de erro, timeout ou fallback]
* **`AC-04`**: [Invariante de persistência, concorrência ou isolamento]

---

## 4. Ancoragem de Rastreabilidade Causal (SpecGraph)

* **ADR Mãe:** `docs/adr/ADR-XXX.md`
* **Marcadores de Teste Pytest:** `@pytest.mark.verifies("SPEC-XXX", "AC-01")`
* **Arquivos Alvo:** `src/...`
