# PROPOSTA FORMAL DE GOVERNANÇA: RFC-001 (Hardening da Mesa Redonda, State Anchors e Pinos Soberanos)

## 🎯 1. Objetivo Raiz & Escopo Nuclear (Âncora Imutável)
- **Pergunta Fundamental:** Como blindar matematicamente a Mesa Redonda contra loops infinitos de deliberação, perda de foco arquitetural e estouro de tokens, garantindo soberania local na RTX 3090 e resiliência de quórum?
- **Critério de Sucesso:** Aprovação unânime de 3/3 dos assentos de fronteira com quórum estrito, limites mecânicos de $N \le 3$ rodadas e deltas compactos $O(n)$.
- **Não-Objetivos (Via Negativa):** 
  - Proibir qualquer tribunal burocrático de apelação entre IAs.
  - Proibir criação de PKI interna, certificados TLS ou bancos de dados distribuídos para persistência de votos locais.
  - Proibir complexidade acidental (gravações atômicas e locks devem ser feitos em <5 linhas de Python).

---

## 📋 2. O Incidente Prévia (Post-Mortem Resumido)
Durante a deliberação de Tooling (CLI vs. MCP), a Mesa anterior executou **51 rodadas consecutivas** (>1 hora de execução inútil), descarrilando para detalhes de `MoveFileExW` no Windows e serialização de zeros negativos em JSON.
- **Causas Raízes:**
  1. *Ausência de Hard Limit no comando `conduct`.*
  2. *Complacência do Mediador* (aceitava qualquer issue teórica sem falsificador).
  3. *Perda da Âncora Raiz* (os modelos esqueceram a pergunta original).
  4. *Quórum quebrado* (Anthropic sem quota travou o sistema em loop).

---

## 🏛️ 3. As 4 Soluções Arquiteturais do RFC-001

### A. Limite Mecânico de Rodadas ($N \le 3$) e FSM Anti-Loop
- Teto normativo rígido de **3 rodadas**.
- Se a 3ª rodada terminar sem consenso, o motor transita para **`HELD_PROGRESS_REVIEW`** e emite um scorecard de 1 página para decisão humana.
- Rodada 4 só é permitida se o humano conceder explicitamente `overtime_granted = true`.

### B. Âncoras de Estado & Deltas Compactos ($O(n)$)
- O prompt carrega sempre a **Âncora Raiz Imutável** no topo.
- Rodadas subsequentes não reenviam o texto integral da proposta, mas apenas as seções alteradas (`ADDED`, `MODIFIED`, `DELETED`) com hashes SHA-256 de seção.

### C. Pinos Formais do Substrato Físico Local (Workstation aaaaa / RTX 3090)
- **`PIN_LOCAL_SOVEREIGN_GENERAL` (`qwen38-27b.gguf` / Qwen 3.8):** Deliberação Soberana Geral (mais fiel e poderoso).
- **`PIN_LOCAL_COMPACTOR` (`qwen38-27b.gguf` / Qwen 3.8):** Escriba Semântico de Compactação Dialética (destila votos em Consensos, Tensões e Descartes a custo zero).
- **`PIN_LOCAL_RED_TEAM` (`qwen36-fable-tc.gguf` / Qwen 3.6 Fable TC):** Cadeira de Red Team para auditoria adversarial sem censura suave ou viés de alinhamento corporativo.

### D. Matriz de Quórum Estrita & Cascata de Fallback
- **`FRONTIER_UNANIMOUS`:** 3 assentos comerciais titulares (Google Gemini 3.7 Flash · high + Anthropic Claude Fable 5 · high + OpenAI GPT-5.6 Sol high).
- **`DEGRADED_MIXED`:** 2 titulares + 1 backup comercial independente (Kimi k3 ou NIM GLM 5.2).
- **`LOCAL_ADVISORY`:** Parecer emitido com assento local na RTX 3090 (exige ratificação humana).
- **`HELD_UNAVAILABLE`:** Menos de 2 assentos válidos.

---

## 📜 4. Formato de Parecer Exigido para Cada Assento
Cada assento deve emitir um parecer JSON estrito com o seguinte schema:
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
