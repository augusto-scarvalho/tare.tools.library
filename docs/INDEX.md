# 📚 ÍNDICE DE PESQUISA & POLÍTICAS — TARE.TOOLS.RESEARCH

> **Hub de Publicação Científica, Decisões de Arquitetura (ADRs), Experimentos de Modelos Locais e Políticas Editoriais.**

---

## 🔬 1. Experimentos Científicos de Hardware & Modelos Locais (`experiments/`)
* **[`experiments/local-llm/README.md`](../experiments/local-llm/README.md):** Suíte de Experimentos Locais de Inferência e Harness de GPU RTX 3090 (`ADR-048`).
  * **[`EXP-01`](../experiments/local-llm/EXP-01-local-llm-runtime-qualification.md):** Qualificação do runtime local e limites de throughput CUDA.
  * **[`EXP-02`](../experiments/local-llm/EXP-02-thinking-retention-kv-cache.md):** Retenção de `<think>` e compactação de cache KV.
  * **[`EXP-03`](../experiments/local-llm/EXP-03-locality-aware-placement.md):** Posicionamento topológico e canal Tailscale.
  * **[`EXP-04`](../experiments/local-llm/EXP-04-sandboxed-execution-isolation.md):** Sandboxes herméticas de execução `bwrap`.
  * **[`EXP-05`](../experiments/local-llm/EXP-05-scheduling-admission-backpressure.md):** Admissão de tarefas e controle de backpressure.

---

## 🏛️ 2. Propostas Arquiteturais & ADRs (`proposals/`)
* **[`proposals/ADR-048_LOCAL_INFERENCE_SUBSTRATE_AND_AGENT_HARNESS.md`](../proposals/ADR-048_LOCAL_INFERENCE_SUBSTRATE_AND_AGENT_HARNESS.md):** Decisão arquitetural de inferência local e auto-reparo.

---

## 📋 3. Políticas Editoriais e Padrões de Publicação
* **[`DOCUMENT_POLICY.md`](../DOCUMENT_POLICY.md):** Política de integridade e ciclo de vida de documentos de pesquisa.
* **[`HTML_PUBLICATION_STANDARD.md`](../HTML_PUBLICATION_STANDARD.md):** Padrão canônico de publicação e semântica HTML para o GitHub Pages.
* **[`TRANSLATION_POLICY.md`](../TRANSLATION_POLICY.md):** Regras de paridade e registro criptográfico de traduções multilíngues.
* **[`PAGES_CUTOVER_READINESS.md`](../PAGES_CUTOVER_READINESS.md):** Critérios formais de cutover e gates de autoridade de publicação.
