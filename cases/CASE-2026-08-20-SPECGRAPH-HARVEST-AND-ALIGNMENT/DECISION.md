# DECISÃO RATIFICADA: RFC-004: Colheita Arquitetural do SpecGraph Histórico e Alinhamento Frugal

- **Caso:** `CASE-2026-08-20-SPECGRAPH-HARVEST-AND-ALIGNMENT`
- **Data:** 2026-08-20 20:23:59 UTC
- **Status:** RATIFICADO POR UNANIMIDADE TRIPARTITE
- **Modo de Quórum:** `DEGRADED_MIXED` (100% Vendor CLI Titular: agy, codex, claude)
- **Rodadas:** 1 de 3

## 1. Consensos Estabelecidos
- Aprovação unânime das premissas e arquitetura proposta.

## 2. Votação dos Assentos Titulares
- **[GOOGLE (google / gemini-3.7-flash)]:** APPROVE — A proposta RFC-004 consolida uma arquitetura altamente pragmática ao preservar os artefatos conceituais de maior valor (rastreabilidade EARS, cálculo de blast radius e context bundling) enquanto elimina complexidade acidental desnecessária. A substituição de pipelines de compilação externa (Rust/PyO3) e bancos analíticos (DuckDB) por AST nativo em Python e manifestos atômicos em JSONL assegura portabilidade universal, baixa latência e perfeita aderência à Doutrina Frugal.
- **[OPENAI (nim_backup_openai / z-ai/glm-5.2)]:** APPROVE — A proposta RFC-004 demonstra uma maturidade excepcional ao aplicar a Via Negativa, eliminando complexidade acidental (Rust/PyO3, DuckDB, Gherkin) em favor de uma stack Python pura e nativa. A preservação das 'joias arquiteturais' garante a rastreabilidade causal e a frugalidade de contexto sem onerar o sistema com dependências externas pesadas. É um modelo exemplar de engenharia pragmática focada em contratos sólidos e baixo overhead computacional.
- **[ANTHROPIC (anthropic / claude-fable-5-high)]:** APPROVE — A Via Negativa está tecnicamente correta: descartar Rust/PyO3, Gherkin e DuckDB em favor de AST puro da stdlib, pytest marks e JSON Lines com SHA-256 é a escolha frugal certa e reduz fricção de build a zero. A direção é aprovada, mas as 'joias' resgatadas são descritas como conceitos sem contratos de aceitação falsificáveis, e a joia nº1 (rastreabilidade bidirecional de 6 camadas) é o vetor mais provável de reintrodução da complexidade acidental que a própria RFC promete purgar.