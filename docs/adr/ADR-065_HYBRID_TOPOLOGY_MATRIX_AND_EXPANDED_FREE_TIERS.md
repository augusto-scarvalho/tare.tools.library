# ADR-065: Matriz Topológica de Inferência Híbrida, Quotas Gratuitas Expandidas e Pinos Canônicos Auditados

## Status
**RATIFIED / RATIFICADO_POR_GOVERNANÇA_TRIPARTITE** (Homologado via `CASE-2026-08-21-RFC-006-HYBRID-TOPOLOGY-AND-FREE-TIER-AMENDMENTS`)

## Data de Ratificação
2026-08-21

## Quórum de Deliberação
- **Modo de Quórum:** `FRONTIER_UNANIMOUS`
- **Assentos Participantes:**
  - Google (`gemini-3.7-flash` via `agy.EXE`)
  - OpenAI (`gpt-5.6-sol` via `codex.exe`)
  - Anthropic (`claude-fable-5-high` via `claude.exe`)
  - Mediador Independente (`meta/llama-3.3-70b` / `z-ai/glm-5.2` via Síntese Dialética Autônoma)

---

## 1. Contexto & Motivação
A evolução do Roteador Soberano BYOC (ADR-064) exigiu suporte formal a alocações heterogêneas e granulares de inferência onde diferentes papéis operam sob diferentes camadas de custo e hardware.

---

## 2. Decisão Arquitetural

### 2.1 Perfil `hybrid` (Matriz de Topologia Dinâmica por Papéis)
O roteador BYOC passa a suportar oficialmente o perfil `hybrid`, que mapeia cascatas ordenadas de inferência por papel:
- **`seat_google`**: `[agy (gemini-3.7-flash) -> Google API -> Qwen 3.8 27B local]`
- **`seat_openai`**: `[codex (gpt-5.6-sol) -> NVIDIA NIM Free -> Qwen 3.8 27B local]`
- **`seat_anthropic`**: `[claude (claude-fable-5) -> Qwen 3.8 27B local]`
- **`scribe_compactor`**: `[Qwen 3.8 27B local ($0.00) -> Gemini 2.5 Flash Free ($0.00)]`
- **`mediator`**: `[NVIDIA NIM Free ($0.00) -> Qwen 3.8 27B local ($0.00)]`
- **`indexer_embeddings`**: `[llama-server nomic-embed 32k local na porta 8081]`

### 2.2 Inclusão do Free Tier do NVIDIA Build / NIM
Formalizado o provedor `nvidia-build-free` (`integrate.api.nvidia.com/v1`) como componente de custo $0.00 (1.000 requisições de avaliação) no ecossistema ao lado do Google Gemini Free e CPU local.

### 2.3 Fact-Check e Fixação Canônica do Qwen 3.8 27B
Auditado e comprovado no inventário físico do nó `aaaaa` (RTX 3090) o modelo **Qwen 3.8 27B** (`qwen38-27b` / `Qwen3.8-27B-Q4_K_M.gguf` / `Qwen3.8-27B-UD-Q4_K_XL.gguf`) como o pino soberano padrão de inferência local.

### 2.4 Isolamento de Estado
Garantido isolamento estrito via `copy.deepcopy` em todas as instâncias e métodos de pino dinâmico (`pin_role_target`), prevenindo poluição de estado global.

---

## 3. Consequências
- 158/158 testes unitários passando verde.
- O usuário possui total flexibilidade para compor e reconfigurar as fontes de inferência em tempo de execução com garantias estritas de soberania e custo.
