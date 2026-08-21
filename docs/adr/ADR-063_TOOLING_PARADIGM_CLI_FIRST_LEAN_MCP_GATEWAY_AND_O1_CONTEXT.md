# ADR-063: Paradigma de Ferramentas CLI First, Lean MCP Gateway e Interfaces Frugais de Contexto O(1)

## Status
**RATIFIED / RATIFICADO_POR_GOVERNANÇA_TRIPARTITE** (Concluído e Homologado via `CASE-2026-08-20-TOOLING-PARADIGM-CLI-VS-MCP`)

## Data de Ratificação
2026-08-21

## Quórum de Deliberação
- **Modo de Quórum:** `FRONTIER_UNANIMOUS`
- **Assento Google:** `Gemini 3.7 Flash · high` via Antigravity CLI (`agy.EXE`)
- **Assento OpenAI:** `GPT-5.6 Sol · high` via OpenAI Codex CLI (`codex.exe`)
- **Assento Anthropic:** `Claude Fable 5 · high` via Claude Code CLI (`claude.exe`)
- **Mediador Independente:** `z-ai/glm-5.2` (Via Negativa & Síntese Dialética Autônoma)

---

## 1. Contexto & Diagnóstico da "Síndrome do Fat MCP"

Servidores MCP monolíticos tradicionais exigem o registro estático de dezenas de schemas JSON complexos de function-calling, injetando de **3.000 a 8.000 tokens** no contexto inicial de cada turno de conversação. Isso:
1. Consome grande parte da janela de atenção útil do modelo.
2. Aumenta drasticamente o custo e a latência de inferência ($O(N)$ em relação ao número de ferramentas).
3. Induz alucinações e falhas de parsing em modelos compactos locais (SLMs).

---

## 2. A Taxonomia Tripartite de Ferramentas

Fica ratificada a arquitetura de 3 camadas para consumo e desenvolvimento de ferramentas no ecossistema `tare.tools`:

### 2.1 Camada 1: CLI First (Padrão Ouro Nativo para Agentes)
- Todas as ferramentas do ecossistema são primariamente utilitários CLI ou scripts Python executáveis via terminal (ex: `round_table_engine.py`, `specgraph`, `pytest`, `git`, `rg`).
- Componibilidade nativa via pipes (`|`), redirecionamento de arquivos e suporte obrigatório a flags estruturadas (`--format=json` / `--format=jsonl`) para consumo determinístico.
- Custo de injeção no system prompt: **0 tokens**.

### 2.2 Camada 2: Lean MCP Gateway (Dispatcher Seguro para Sandboxes & IDEs)
- Para clientes sem acesso direto ao shell do host ou sandboxes isoladas, adota-se o **Lean MCP Gateway** (`tools/mesh/lean_mcp_gateway.py`) com no máximo 2 endpoints genéricos:
  1. `exec_command(command: list[str], cwd: str, timeout_seconds: float = 30.0)`
  2. `read_resource(uri: str)`
- **Contratos de Segurança & Confinamento:**
  - *Vetor de Argumentos Estrito (`list[str]`):* Execução via `argv` direto (`shell=False`), prevenindo injeção acidental de operadores de shell.
  - *Confinamento de Workspace:* `cwd` estritamente contido no workspace do projeto com validação de caminho canônico.
  - *Envelope Estruturado:* Retorno com telemetria determinística contendo `stdout`, `stderr`, `exit_code`, `duration_ms` e `timed_out`.
- Tamanho total do schema injetado: **<150 tokens**.

### 2.3 Camada 3: Regra de Frugalidade de Contexto $O(1)$
- É vedada a injeção estática e linear de schemas de ferramentas no contexto ($O(N)$).
- Qualquer extensão MCP deve comprovar por medição empírica custo constante de contexto ($O(1)$) através de paginação sob demanda e isolamento de falhas.

---

## 3. Consequências & Implementação

1. **Economia de Contexto:** Redução imediata de >80% de tokens de sistema por turno em todos os clientes.
2. **Interoperabilidade Total:** Novos utilitários adicionados à CLI tornam-se imediatamente acessíveis para sandboxes e subagentes sem necessidade de reconfiguração de schemas MCP.
3. **Validação:** Cobertura de testes implementada e validada em [`tests/test_lean_mcp_gateway.py`](file:///C:/projects/tare.tools.library/tests/test_lean_mcp_gateway.py).
