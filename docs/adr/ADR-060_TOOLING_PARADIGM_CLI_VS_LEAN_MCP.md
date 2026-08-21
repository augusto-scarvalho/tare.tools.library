# ADR-060: [ENGAVETADO] Taxonomia de Ferramental do Ecossistema: CLI no Modo 1, Lean MCP Gateway Read-Only e Banimento de Fat MCP

## Status
**SHELVED / REVOGADO_POR_LOOP_DISFUNCIONAL** (Engavetado após identificação de deriva de escopo e hipertrofia técnica em `CASE-2026-08-20-TOOLING-PARADIGM-CLI-VS-MCP`)

## Data de Engavetamento
2026-08-20

---

## 1. Motivo do Engavetamento
Esta deliberação foi anulada e engavetada por decisão do operador do ecossistema devido a:
1. **Looping Disfuncional sem Critério de Parada:** O processo dialético estendeu-se por 51 rodadas consecutivas sem convergência pragmática.
2. **Deriva Hipertrófica de Escopo:** O escopo original (estratégia frugal de consumo de ferramentas via CLI vs MCP para economizar tokens em chat) descambou para micro-otimizações de primitives de baixo nível do sistema operacional (Win32 `MoveFileExW`, `F_FULLFSYNC` no APFS, serializadores binários de floats).
3. **Indisponibilidade de Quorum:** O assento da Anthropic encontrava-se indisponível por quota durante a sessão.

---

## 2. Próximos Passos de Governança
1. Reforma estrutural no motor da Mesa Redonda (`relay/round_table_engine.py`) com:
   - Limite absoluto e inflexível de rodadas ($N \le 3$).
   - Detecção automática de deriva de escopo e *bike-shedding*.
   - Mandato estrito de *Via Negativa* para o Mediador barrar complexidade acidental.
2. Nova submissão limpa da pauta de Tooling (CLI vs MCP) após o motor estar devidamente saneado.
> [!NOTE]
> **RESOLUÇÃO HISTÓRICA:** Esta pauta foi reaberta de forma limpa e ratificada formalmente por governança tripartite unânime em 2026-08-21 no [**ADR-063: Paradigma de Ferramentas CLI First, Lean MCP Gateway e Interfaces Frugais de Contexto O(1)**](ADR-063_TOOLING_PARADIGM_CLI_FIRST_LEAN_MCP_GATEWAY_AND_O1_CONTEXT.md).
