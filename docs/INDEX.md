# Acervo Documental e Governança tare.tools

- [**`DOCUMENT_OWNERSHIP.md`**](DOCUMENT_OWNERSHIP.md): regra de propriedade por repositório, catálogo federado e busca histórica opcional.
- [**`ENGINEERING_DOCTRINE.md`**](https://github.com/augusto-scarvalho/tare.tools.os/blob/main/docs/governance/ENGINEERING_DOCTRINE.md): **Doutrina Soberana de Engenharia Frugal**, mantida pelo `tare.tools.os` (os 5 princípios canônicos).
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

## 🏛️ 2. Registros históricos de governança (mantidos pelo `tare.tools.os`)
* **[`RFC-001_MASTER_IDEATION_AND_GOVERNANCE_WHITEPAPER.md`](https://github.com/augusto-scarvalho/tare.tools.os/blob/main/docs/governance/library-era-rfcs/RFC-001_MASTER_IDEATION_AND_GOVERNANCE_WHITEPAPER.md):** Whitepaper Master e registro histórico de ideação, preservado pelo `tare.tools.os`.
* **[`RFC-001_LOCAL_LLM_DIALECTICAL_COMPACTION_AND_STATE_ANCHORS.md`](https://github.com/augusto-scarvalho/tare.tools.os/blob/main/docs/governance/library-era-rfcs/RFC-001_LOCAL_LLM_DIALECTICAL_COMPACTION_AND_STATE_ANCHORS.md):** Especificação histórica dos pilares de governança, State Anchors e escriba local.
* **[`RFC-001_IMPLEMENTATION_PLAN.md`](https://github.com/augusto-scarvalho/tare.tools.os/blob/main/docs/governance/library-era-rfcs/RFC-001_IMPLEMENTATION_PLAN.md):** Roteiro histórico de implementação em seis fases.
* **[`RFC-002_TOOLING_PARADIGM_CLI_FIRST_AND_LEAN_MCP.md`](https://github.com/augusto-scarvalho/tare.tools.os/blob/main/docs/governance/library-era-rfcs/RFC-002_TOOLING_PARADIGM_CLI_FIRST_AND_LEAN_MCP.md):** Registro histórico da escolha entre CLI e Lean MCP.
* **[`POST_MORTEM_ROUND_TABLE_LOOPING_AND_STATE_ANCHOR_ARCHITECTURE_2026-08-20.md`](https://github.com/augusto-scarvalho/tare.tools.os/blob/main/docs/operations/POST_MORTEM_ROUND_TABLE_LOOPING_AND_STATE_ANCHOR_ARCHITECTURE_2026-08-20.md):** Autópsia do incidente de 51 rodadas e diagnóstico de descarrilamento de escopo.

---

## 📋 3. Políticas Editoriais e Padrões de Publicação
* **[`DOCUMENT_POLICY.md`](policies/DOCUMENT_POLICY.md):** Política de integridade e ciclo de vida de documentos de pesquisa.
* **[`HTML_PUBLICATION_STANDARD.md`](policies/HTML_PUBLICATION_STANDARD.md):** Padrão canônico de publicação e semântica HTML para o GitHub Pages.
* **[`TRANSLATION_POLICY.md`](policies/TRANSLATION_POLICY.md):** Regras de paridade e registro criptográfico de traduções multilíngues.
* **[`PAGES_CUTOVER_READINESS.md`](policies/PAGES_CUTOVER_READINESS.md):** Critérios formais de cutover e gates de autoridade de publicação.

## Casos Deliberativos Notáveis
- [`CASE-2026-08-20-RFC-001-GOVERNANCE-HARDENING`](../cases/CASE-2026-08-20-RFC-001-GOVERNANCE-HARDENING/DECISION.md): **Marco Histórico** — Primeira aprovação unânime tripartite em 1ª rodada (FSM Frugal, State Anchors e Pinos Soberanos).
- [`CASE-2026-08-20-TOOLING-PARADIGM-CLI-VS-MCP`](../cases/CASE-2026-08-20-TOOLING-PARADIGM-CLI-VS-MCP/DECISION.md): **RFC-002 Ratificado** — Paradigma de Ferramentas (CLI First, Lean MCP Gateway e Banimento de Fat MCP).
- [`CASE-2026-08-20-ENGINEERING-DOCTRINE-AND-BYOC`](../cases/CASE-2026-08-20-ENGINEERING-DOCTRINE-AND-BYOC/DECISION.md): **RFC-003 Ratificado** — Doutrina Universal de Engenharia Frugal e Liberdade de Computação (BYOC).
- [`CASE-2026-08-20-SPECGRAPH-HARVEST-AND-ALIGNMENT`](../cases/CASE-2026-08-20-SPECGRAPH-HARVEST-AND-ALIGNMENT/DECISION.md): **RFC-004 Ratificado** — Colheita Arquitetural do SpecGraph Histórico e Alinhamento Frugal.
