# PROPOSTA FORMAL DE GOVERNANÇA: RFC-002 (Paradigma de Ferramentas: CLI First, Lean MCP Gateway com Sandbox Confinado e Interfaces Frugais)

## 🎯 1. Objetivo Raiz & Escopo Nuclear (Âncora Imutável)
- **Pergunta Fundamental:** Qual é o paradigma arquitetural ótimo para consumo de ferramentas por agentes de código no ecossistema `tare.tools`, maximizando a frugalidade de tokens, a componibilidade Unix, a segurança de execução e a velocidade de inferência?
- **Critério de Sucesso:** Eliminar o overhead de injeção de schemas monolíticos no system prompt (>80% de redução de tokens de sistema), garantindo ergonomia para Aider, Claude Code, Codex e subagentes Antigravity com contenção estrita de sandbox.
- **Não-Objetivos (Via Negativa):**
  - Proibir servidores MCP monolíticos com dezenas de schemas estáticos que violam o orçamento de contexto $O(1)$ ("Fat MCP").
  - Proibir execução de comandos arbitrários fora do workspace do projeto sem isolamento ou timeouts.
  - Proibir discussões de baixo nível de SO que pertencem à camada de implementação.

---

## 📋 2. Contexto & Motivação (A Síndrome do Fat MCP)
- **O Problema do Fat MCP:** Servidores MCP tradicionais registram dezenas de schemas JSON complexos de function-calling, injetando de **3.000 a 8.000 tokens** no contexto inicial de cada turno. Isso encarece a inferência, reduz a janela útil de raciocínio e induz alucinações em modelos menores.
- **A Solução CLI First & Lean Gateway:** Agentes de código operam com máxima precisão através do terminal Unix padrão (`stdout`, `stdin`, `exit codes`, pipes e scripts CLI). O custo de injeção de schema na CLI é **zero tokens**, e a ponte para sandboxes opera com custo constante $O(1)$.

---

## 🏛️ 3. A Taxonomia Tripartite de Ferramentas

### Camada 1: CLI First (Padrão Ouro / Nativo para Agentes)
- Todas as ferramentas do ecossistema são primariamente utilitários CLI ou scripts Python executáveis via terminal (ex: `round_table_engine.py`, `specgraph`, `pytest`, `git`, `rg`).
- Componibilidade nativa via pipes (`|`), redirecionamento de arquivos e suporte obrigatório a saídas estruturadas (`--format=json` ou `--format=jsonl`) para consumo determinístico por agentes leves.
- Custo de injeção de contexto no prompt: **0 tokens**.

### Camada 2: Lean MCP Gateway (Dispatcher Seguro para Sandboxes & IDEs)
- Para clientes sem acesso direto ao shell do host ou sandboxes isoladas, adota-se o **Lean MCP Gateway** com no máximo 2 endpoints genéricos:
  1. `exec_command(command: list[str] | str, cwd: str, timeout_seconds: float = 30.0)`
  2. `read_resource(uri: str)`
- **Contrato de Segurança & Confinamento:**
  - *Isolamento de Diretório:* `cwd` estritamente contido no workspace do projeto (falha fechada para caminhos fora da raiz).
  - *Execução Segura:* Preferência por passagem de argumentos como lista de strings (`shell=False`) para mitigar injeção de comandos.
  - *Envelope Estruturado:* Retorno obrigatório em envelope JSON contendo: `stdout`, `stderr`, `exit_code`, `duration_ms` e `timed_out: bool`.
- Tamanho total do schema injetado: **<150 tokens**.

### Camada 3: Regra de Frugalidade de Contexto $O(1)$ (Filtro Via Negativa)
- É vedada qualquer integração ou servidor de ferramentas que imponha injeção estática e linear de dezenas de schemas no prompt ($O(N)$).
- Qualquer extensão MCP deve comprovar por medição empírica conformidade com o teto de contexto $O(1)$ e paginação de ferramentas sob demanda.

---

## 📜 4. Formato de Parecer Exigido para Cada Assento
```json
{
  "seat": "<google | anthropic | openai>",
  "execution_nonce": "<sentinel_nonce>",
  "verdict": "<APPROVE | REJECT | REVISE>",
  "confidence": 0.95,
  "summary": "<Resumo técnico de 2 a 3 frases>",
  "strengths": ["<Ponto forte 1>", "<Ponto forte 2>"],
  "issues": [
    {
      "severity": "<blocking | non-blocking>",
      "claim": "<Afirmação técnica>",
      "falsifier": "<Condição empírica que falsifica a proposta>"
    }
  ],
  "recommendations": ["<Recomendação 1>"]
}
```
