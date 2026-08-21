# DECISÃO RATIFICADA: RFC-002 (Paradigma de Ferramentas CLI First, Lean MCP Gateway e Interfaces Frugais)

- **Caso:** `CASE-2026-08-20-TOOLING-PARADIGM-CLI-VS-MCP`
- **Data de Homologação:** 2026-08-21
- **Status:** RATIFICADO POR GOVERNANÇA TRIPARTITE
- **Referência Arquitetural Canônica:** [`docs/adr/ADR-063_TOOLING_PARADIGM_CLI_FIRST_LEAN_MCP_GATEWAY_AND_O1_CONTEXT.md`](file:///C:/projects/tare.tools.library/docs/adr/ADR-063_TOOLING_PARADIGM_CLI_FIRST_LEAN_MCP_GATEWAY_AND_O1_CONTEXT.md)
- **Modo de Quórum:** `FRONTIER_UNANIMOUS`
- **Assentos Participantes:**
  - Google (`gemini-3.7-flash` via `agy.EXE`)
  - OpenAI (`gpt-5.6-sol` via `codex.exe`)
  - Anthropic (`claude-fable-5-high` via `claude.exe`)
  - Mediador Independente (`z-ai/glm-5.2` via Síntese Dialética Autônoma)

---

## 1. Síntese Dialética da Deliberação

### Rodada 1:
- A proposta inicial estabeleceu a taxonomia CLI First vs Lean MCP vs Banimento de Fat MCP.
- **Votos:** Google (`APPROVE`), OpenAI (`REVISE`), Anthropic (`REVISE`).
- **Tensões:** Identificada a necessidade de envelope estruturado de retorno (`stdout`, `stderr`, `exit_code`, `duration_ms`), saída JSON nas CLIs e segurança contra command injection.

### Rodada 2 (Refinamento Contratual de Segurança):
- Atualizados os contratos de confinamento de workspace, timeout padrão e envelope determinístico.
- **Votos:** Google (`REVISE`), OpenAI (`REVISE`), Anthropic (`REVISE`).
- **Tensão Central:** Claude e OpenAI exigiram a eliminação de `str` na assinatura de `exec_command` para fechar o tipo estrito `list[str]` com `shell=False`, e converter a proibição de Fat MCP em critério de contexto $O(1)$.

### Rodada 3 (Convergência e Teto FSM):
- Atingido o teto normativo com quórum unânime de fronteira.
- Ratificada a arquitetura final no **ADR-063**.

---

## 2. Veredito Final & Ratificação

O Paradigma de Ferramentas CLI First e Lean MCP Gateway está formalmente homologado e consagrado no ecossistema através do **ADR-063**.
