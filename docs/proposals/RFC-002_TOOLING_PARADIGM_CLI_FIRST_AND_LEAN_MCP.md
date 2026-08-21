# RFC-002: Paradigma de Ferramentas (CLI First, Lean MCP Gateway e Banimento de Fat MCP)

- **Caso:** [`CASE-2026-08-20-TOOLING-PARADIGM-CLI-VS-MCP`](file:///C:/projects/tare.tools.library/cases/CASE-2026-08-20-TOOLING-PARADIGM-CLI-VS-MCP)
- **Status:** ✅ RATIFICADO POR UNANIMIDADE TRIPARTITE (1ª Rodada)
- **Data:** 2026-08-20

## 1. Resumo Executivo
Define a taxonomia oficial de consumo de ferramentas para todos os agentes do ecossistema `tare.tools`:
1. **`CLI First` (Padrão Ouro):** 0 tokens de injeção de schema; máxima componibilidade Unix via terminal.
2. **`Lean MCP Gateway` (Ponte de Sandbox / IDE):** Dispatcher genérico expondo apenas `exec_command` e `read_resource` (<150 tokens).
3. **`Fat MCP Banido` (Via Negativa):** Proibição expressa de servidores MCP com dezenas de schemas atomizados.
