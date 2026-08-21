# ADR-064: Mecanismos Executáveis de Enforcement da Doutrina Frugal, Roteador BYOC e Protocolo de Parada Segura

## Status
**RATIFIED / RATIFICADO_POR_GOVERNANÇA_TRIPARTITE** (Concluído e Homologado via `CASE-2026-08-21-RFC-005-DOCTRINE-ENFORCEMENT-AND-BYOC-MECHANISMS`)

## Data de Ratificação
2026-08-21

## Quórum de Deliberação
- **Modo de Quórum:** `FRONTIER_UNANIMOUS`
- **Assento Google:** `Gemini 3.7 Flash · high` via Antigravity CLI (`agy.EXE`)
- **Assento OpenAI:** `GPT-5.6 Sol · high` via OpenAI Codex CLI (`codex.exe`)
- **Assento Anthropic:** `Claude Fable 5 · high` via Claude Code CLI (`claude.exe`)
- **Mediador Independente:** `z-ai/glm-5.2` (Via Negativa & Síntese Dialética Autônoma)

---

## 1. Contexto & Diagnóstico

Para garantir que a Doutrina Universal de Engenharia Frugal e BYOC (ADR-062 e ADR-063) seja um hábito mecânico do ecossistema, estabeleceu-se a especificação e codificação de 6 mecanismos executáveis automatizados.

---

## 2. A Arquitetura dos 6 Mecanismos de Enforcement

### 2.1 Mecanismo 1: Teto Métrico de Schema e Frugalidade de Dependências
- **Teto Físico de Schema:** O payload JSON-RPC do Lean MCP Gateway é limitado a **< 600 bytes serializados** (equivalente a < 150 tokens) em teste unitário determinístico agnóstico de tokenizador.
- **Prioridade de Stdlib:** Verificação AST leve no CI que previne adição de dependências pesadas quando primitivos nativos de `pathlib`, `subprocess`, `json`, `urllib` e `dataclasses` atendem o requisito.

### 2.2 Mecanismo 2: Ciclo de Vida Ambidestro (Spikes vs Core)
- **Área de Inovação Livre:** Repositório `tare.tools.local-labs` e branches `spike/*` operam sem restrições de cobertura estrita para pesquisa e testes arrojados de IA/GPU.
- **Purga pela Via Negativa:** Promoção para repositórios estáveis (`tare.tools.library`, `tare.tools.specgraph`, `tare.tools.os`) exige destilação e 100% de testes unitários.

### 2.3 Mecanismo 3: Rastreabilidade de Falsificadores (`specgraph trace`)
- O comando `specgraph trace` mapeia cada requisito EARS das especificações em `specs/` ao seu respectivo teste decorado com `@pytest.mark.verifies("REQ-ID")`.
- Código normativo é definido mecanicamente como qualquer símbolo público sob `src/` associado a requisitos de especificação.

### 2.4 Mecanismo 4: Roteador BYOC Soberano e Matriz Dinâmica Híbrida (`tools/mesh/byoc_router.py`)
- Configuração agnóstica via `~/.tare/config.yaml` suportando 4 perfis fundamentais:
  1. `free`: Google Gemini Free API, NVIDIA NIM / Build Free Evaluation Tier (1.000 requisições free) e CPU local ($0.00).
  2. `pro`: Chaves de API comerciais com extração segura via OS Keyring.
  3. `local`: GPU Local Soberana no nó `aaaaa` com **`qwen38-27b.gguf` (Qwen 3.8 27B)** (100% offline).
  4. `hybrid` (Matriz Dinâmica por Papéis): Roteamento granular onde o usuário escolhe e pina a fonte de inferência para cada função:
     - **Cadeiras Tripartites:** Vendor CLIs (`agy`, `codex`, `claude`) com fallback dinâmico para APIs / NIM Free / Local GPU.
     - **Escriba Compactador:** GPU Local (`qwen38-27b.gguf`) ou Gemini Free para sínteses sem custo.
     - **Mediador Independente:** NIM Free (`meta/llama-3.3-70b`) ou GPU Local (`qwen38-27b.gguf`).
     - **Embeddings/Indexador:** `llama-server` local na porta 8081 (`nomic-embed-text-v1.5.Q8_0.gguf`).
- Suporte a **Pinos Dinâmicos (`pin_role_target`)** em tempo de execução sem recompilação.

### 2.5 Mecanismo 5: Protocolo de Parada de Emergência (`HALT_RECEIPT.json`)
- Se durante a execução for detectada contradição física, falha de integridade ou risco de segurança, o agente executor gera um recibo estruturado `HALT_RECEIPT.json` e suspende o turno para re-deliberação rápida.

### 2.6 Mecanismo 6: Lean MCP Gateway Confinado com Resolução de Symlinks
- Execução obrigatória via `command: list[str]` com `shell=False`.
- Confinamento estrito de diretório validado via `Path(cwd).resolve()` (realpath) para neutralizar escapes por symlink fora da raiz do projeto.

---

## 3. Consequências & Próximos Passos
Fica autorizada e mandada a implementação imediata dos 6 mecanismos de código, seguida por auditoria e verificação completa da suíte de testes.
