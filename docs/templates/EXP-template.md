# EXP-XXX: [Título Sucinto do Experimento]

- **Status:** [PROPOSED | RUNNING | ADOPTED | ADAPTED | RETIRED]
- **Data de Execução:** YYYY-MM-DD
- **Executor:** [Nome do Operador ou Agente]
- **Commit / Versão do Código:** `@ <hash-ou-branch>`
- **Hardware / Substrato:** Ex: RTX 3090 @ `aaaaa` (24GB VRAM) / Gemini Flash Free Tier / NVIDIA NIMs

---

## 1. Hipótese & Objetivo
* **Pergunta Central:** O que estamos tentando provar ou falsificar?
* **Hipótese Nula ($H_0$):** O que aconteceria sem essa mudança?
* **Hipótese Alternativa ($H_1$):** O ganho esperado mensurável.

---

## 2. Metodologia & Setup
* **Cenário de Teste:** Descrição objetiva dos passos de execução.
* **Comandos Executados:**
  ```powershell
  # Exemplo de comando de benchmark
  python -m pytest tests/benchmarks/
  ```

---

## 3. Dados & Métricas Observadas

| Parâmetro / Métrica | Baseline (Anterior) | Novo Resultado | Delta (%) |
| :--- | :--- | :--- | :--- |
| **Latência Média ($p_{50}$)** | 250ms | 45ms | -82.0% |
| **Consumo de Tokens** | 12.000 tokens | 2.100 tokens | -82.5% |
| **Throughput (req/s)** | 4.2 req/s | 22.1 req/s | +426% |
| **Taxa de Erro / Drift** | 0.0% | 0.0% | 0.0% |

---

## 4. Veredito Arquitetural & Próximos Passos
* **Veredito:** `[ADOPT | ADAPT | RETIRE]`
* **Racional:** Por que essa decisão foi tomada com base nos números acima?
* **Impacto em ADRs:** Requer nova ADR ou emenda?
