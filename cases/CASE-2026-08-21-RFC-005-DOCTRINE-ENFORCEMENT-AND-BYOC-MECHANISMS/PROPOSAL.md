# PROPOSTA FORMAL DE GOVERNANÇA: RFC-005 (Mecanismos Executáveis de Enforcement da Doutrina Frugal, Ambidestria e BYOC)

## 🎯 1. Objetivo Raiz & Escopo Nuclear (Âncora Imutável)
- **Pergunta Fundamental:** Como materializar e auditar os 6 Princípios da Doutrina Universal de Engenharia Frugal e BYOC (ADR-062 e ADR-063) através de ferramentas de software automatizadas, verificadores de conformidade estática, roteador agnóstico de computação e protocolo de parada segura no ecossistema `tare.tools`?
- **Critério de Sucesso:** Implementação de 100% dos 6 mecanismos executáveis com suíte de testes passando verde, validação de schema <150 tokens e auditoria tripartite conclusiva.
- **Não-Objetivos (Via Negativa):**
  - Proibir a criação de dependências externas pesadas quando a biblioteca padrão resolver o problema.
  - Proibir abstrações de microsserviços ou middlewares complexos fora do padrão Unix.
  - Proibir execução cega sem falsificadores verificáveis.

---

## 📋 2. Os 6 Mecanismos Executáveis da Arquitetura

### 1. Frugality & Dependency Guard (`tools/guards/frugality_guard.py`)
- Validador estático em CI que audita imports do projeto contra dependências infladas desnecessárias (*Via Negativa*).
- Garante prioridade para `pathlib`, `subprocess`, `json`, `urllib`, `dataclasses` da biblioteca padrão.
- Medição e trava de teto de contexto para schemas JSON-RPC ($O(1)$ < 150 tokens).

### 2. Fluxo Ambidestro de Git & Ciclo de Vida de Spikes
- Protocolo formal de bifurcação:
  - *Área de Exploração Livre:* Repositório `tare.tools.local-labs` e branches `spike/*` operam com liberdade criativa total sem barreiras de cobertura estrita para testar hipóteses ousadas de IA.
  - *Área de Consolidação & Purga:* Código promovido para `tare.tools.library` e `tare.tools.specgraph` passa obrigatoriamente por refatoração pela Via Negativa e 100% de testes unitários.

### 3. Rastreabilidade de Falsificadores (`specgraph trace` & `@pytest.mark.verifies`)
- O comando `specgraph trace` verifica a cobertura bidirecional entre requisitos EARS nos arquivos de especificação e os testes `@pytest.mark.verifies("SPEC-REQ-ID")`.
- Falha o build caso exista código normativo em produção sem falsificador empírico associado.

### 4. Roteador Soberano BYOC (`tools/mesh/byoc_router.py`)
- Suporte nativo e desacoplado a 3 perfis de computação via `~/.tare/config.yaml`:
  - `profile: free` (Gemini API free tier + CPU fallback em llama.cpp local).
  - `profile: pro` (Chaves de API lidas de forma segura via OS Keyring).
  - `profile: local` (Endpoint OpenAI-compatível apontando para GPU soberana local ex: `http://100.107.245.30:8080/v1`).
- Degradação graciosa de contexto via `specgraph bundle` quando o perfil operar com SLMs compactos.

### 5. Protocolo de Parada de Emergência & Laudo de Inconformidade (`EmergencyHaltReceipt`)
- Padronização do contrato `HALT_RECEIPT.json`: se o agente executor identificar risco de integridade de dados, brecha de segurança ou impossibilidade física de execução, emite o recibo e suspende a execução imediatamente sem improvisos ou insubordinação.

### 6. Lean MCP Gateway Confinado com Vetor Argv (`list[str]`)
- O gateway expõe estritamente `exec_command(command: list[str], cwd: str, timeout_seconds: float = 30.0)`.
- Execução por `argv` puro com `shell=False`, validação de contenção de diretório canônico e retorno de telemetria estruturada (`stdout`, `stderr`, `exit_code`, `duration_ms`, `timed_out`).

---

## 📜 3. Plano de Implementação e Auditoria Pós-Ratificação
1. **Fase 1 (Deliberação & Ratificação):** Aprovação tripartite do plano na Mesa Redonda.
2. **Fase 2 (Codificação & Testes):** Implementação dos módulos e testes unitários cobrindo todos os 6 mecanismos.
3. **Fase 3 (Auditoria Tripartite Final):** Submissão do bundle de evidências e diff para chancela e auditoria da Mesa Redonda.

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
