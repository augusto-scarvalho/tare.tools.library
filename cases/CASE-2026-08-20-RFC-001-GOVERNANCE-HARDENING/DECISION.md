# DECISÃO RATIFICADA: RFC-001 (Hardening de Governança, State Anchors, FSM N <= 3 e Vendor CLI First)

- **Caso:** `CASE-2026-08-20-RFC-001-GOVERNANCE-HARDENING`
- **Data de Ratificação:** 2026-08-20 21:01:13 UTC
- **Status:** RATIFICADO / HOMOLOGADO POR GOVERNANÇA TRIPARTITE
- **Referência Arquitetural:** [ADR-061](https://github.com/augusto-scarvalho/tare.tools.os/blob/main/docs/adr/ADR-061_DELIBERATIVE_GOVERNANCE_HARDENING_FSM_AND_VENDOR_CLI_FIRST.md)
- **Topologia de Quórum:** `FRONTIER_UNANIMOUS` (100% Vendor CLI First: Google AI Pro, ChatGPT Pro, Claude Pro)

---

## 1. Síntese do Processo Deliberativo das 4 Rodadas

A proposta passou por 4 rodadas rigorosas de auditoria dialética tripartite:

1. **Rodada 1 (Diagnóstico & Tensões Iniciais):**
   - **Google (`agy.EXE`):** `APPROVE`
   - **OpenAI (`codex.exe`):** `REVISE` (Exigiu limite estrito para prorrogações, validação de deltas e pinning formal).
   - **Anthropic (`claude.exe`):** `REVISE` (Exigiu regra determinística de agregação de votos e política de VRAM na RTX 3090).
   - *Resultado:* FSM transita para `REVISED` com geração de `MEDIATOR_SYNTHESIS.md`.

2. **Rodada 2 (Aplicação do Aparato de Compact Delta):**
   - Incorporou a Seção 5 (Teto N=4 e Serialização de VRAM). O tráfego de contexto foi reduzido em >75% via hash SHA-256 de seção.
   - **OpenAI & Anthropic:** Detectaram que a Tabela de Agregação precisava ser formalmente uma **Função Total** sobre o espaço de votos e issues bloqueantes.
   - *Resultado:* `REVISED`.

3. **Rodada 3 (Teto Normativo N=3 & Acionamento da Trava Anti-Looping):**
   - Executada com aviso explícito de Rodada Final da FSM.
   - O motor parou no limite estrito de 3 rodadas e transitou deterministicamente para `HELD_PROGRESS_REVIEW`, escalando a decisão para o Operador Humano.

4. **Rodada 4 (Overtime Homologado pelo Operador Humano & Prova Terminal):**
   - O Operador Humano concedeu formalmente a prorrogação única (`overtime_granted = True`).
   - A FSM executou a 4ª rodada terminal, demonstrou a terminação determinística e encerrou o processo sem qualquer possibilidade de looping infinito.

---

## 2. Invariantes Arquiteturais Homologados

1. **Teto Mecânico N <= 3 (Normativo) e N = 4 (Overtime Terminal):** Trava absoluta contra loops e runaway token spend.
2. **Invariante Anti-Sybil:** Proibição estrita de o mesmo modelo ocupar múltiplas cadeiras; falha fechada para `HELD_UNAVAILABLE`.
3. **Vendor CLI First ($0.00 de API):** Despacho prioritário via `agy.EXE`, `codex.exe` e `claude.exe`.
4. **Precedência Total de Agregação:** Quórum & Sybil $\to$ Issues Bloqueantes $\to$ Votos $\to$ Rodadas.
5. **Compact Delta O(n) & Âncoras Imutáveis:** Preclusão por hash de seções aprovadas.
6. **Substrato Soberano:** Serialização de turnos na RTX 3090, I/O atômico com `os.replace` e lock PID-aware.
