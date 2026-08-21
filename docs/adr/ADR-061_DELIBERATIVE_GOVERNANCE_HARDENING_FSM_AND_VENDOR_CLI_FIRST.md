# ADR-061: Hardening de Governança Deliberativa, FSM Anti-Looping, Invariante Anti-Sybil e Topologia Vendor CLI First

## Status
**RATIFIED / RATIFICADO_POR_GOVERNANÇA_TRIPARTITE** (Concluído e Homologado via `CASE-2026-08-20-RFC-001-GOVERNANCE-HARDENING`)

## Data de Ratificação
2026-08-20

## Quórum de Deliberação
- **Modo de Quórum:** `FRONTIER_UNANIMOUS`
- **Assento Google:** `Gemini 3.7 Flash · high` via Antigravity CLI (`agy.EXE`) — *Zero Custo de API*
- **Assento OpenAI:** `GPT-5.6 Sol · high` via OpenAI Codex CLI (`codex.exe`) — *Zero Custo de API*
- **Assento Anthropic:** `Claude Fable 5 · high` via Claude Code CLI (`claude.exe`) — *Zero Custo de API*

---

## 1. Contexto & Diagnóstico Histórico

O incidente prévio de governança registrou 51 rodadas consecutivas de deliberação sem convergência, acarretando gasto excessivo de tokens e deriva de escopo (*bike-shedding*). A investigação pós-incidente identificou quatro vulnerabilidades estruturais no motor dialético:
1. Ausência de teto mecânico rígido de rodadas na máquina de estados (FSM).
2. Acúmulo descontrolado do histórico completo no prompt, inflando a janela de contexto.
3. Risco de falso consenso por efeito Sybil (o mesmo modelo de failover respondendo por assentos distintos).
4. Ambiguidade na regra de agregação de votos e falta de precedência formal para issues bloqueantes.

---

## 2. Decisão Arquitetural: Os 6 Pilares de Hardening

Fica estabelecida e ratificada a nova arquitetura soberana do motor de governança ([`tools/governance/round_table_engine.py`](file:///C:/projects/tare.tools.library/tools/governance/round_table_engine.py)):

### 2.1 Teto Mecânico Inflexível ($N \le 3$) e FSM com Escalonamento Humano
- A deliberação normativa possui teto fixo de **$N \le 3$ rodadas**.
- Se ao término da Rodada 3 não houver consenso unânime tripartite, o motor transita obrigatoriamente para o estado `HELD_PROGRESS_REVIEW`, parando qualquer execução automatizada e escalando a decisão para o Operador Humano.
- O Operador Humano pode conceder uma **única prorrogação formal (`overtime_granted = True`)**, elevando o teto terminal para **$N = 4$ rodadas**.
- A Rodada 4 é terminal absoluta: caso não haja consenso na Rodada 4, o motor finaliza irreversivelmente no estado `HELD_OVERTIME_EXHAUSTED`. É proibida qualquer 5ª rodada.

### 2.2 Invariante Anti-Sybil (Cardinalidade Estrita de Modelos)
- É vedado que um mesmo modelo (ou identificador de modelo) ocupe mais de uma cadeira na Mesa Redonda, mesmo em situações de failover/contingência.
- O motor valida formalmente: `len(models) == len(set(models))`.
- Em caso de colisão de modelo, o quórum é desqualificado imediatamente e a deliberação transita para `HELD_UNAVAILABLE`.
- O despachante universal suporta `excluded_models: Set[str]` dinâmico, garantindo que modelos já reivindicados por um assento sejam excluídos da cascata dos assentos restantes.

### 2.3 Topologia Soberana Vendor CLI First (Zero API Credit Burn)
- As 3 cadeiras titulares operam exclusivamente via CLIs oficiais instaladas no host:
  - **Google:** `agy.EXE -p <prompt> --effort high --dangerously-skip-permissions`
  - **OpenAI:** `codex.exe exec -m gpt-5.6-sol -c model_reasoning_effort="high" --dangerously-bypass-approvals-and-sandbox --skip-git-repo-check -`
  - **Anthropic:** `claude.exe -p -` (via PowerShell UTF-8 pipe com `tempfile`)
- Zero queima de créditos pagos de API HTTP; utilização integral das assinaturas Pro/Plus do usuário.

### 2.4 Aparato de Compactação $O(n)$ de Contexto & Âncoras Imutáveis
- A proposta inicial recebe hash SHA-256 por seção e Âncora Raiz Imutável no topo.
- A partir da Rodada 2, as seções já aprovadas/mantidas tornam-se preclusas.
- O motor gera e transmite apenas o **Compact Delta (`ADDED`, `MODIFIED`, `DELETED`)** das seções alteradas junto com a Síntese Dialética do Mediador, reduzindo o tráfego de contexto em >75%.

### 2.5 Função Total Determinística de Agregação
A apuração dos votos segue ordem estrita de precedência:
1. **Precedência 1 (Quórum & Anti-Sybil):** Se `< 2` assentos válidos ou colisão Sybil $\to$ `HELD_UNAVAILABLE`.
2. **Precedência 2 (Issues Bloqueantes):** A presença de $\ge 1$ issue com `severity: blocking` impede o veredito `APPROVED`, mesmo que o texto do voto seja `APPROVE`.
3. **Precedência 3 (Unanimidade):** Exatamente 3 votos `APPROVE` sem issues bloqueantes $\to$ `APPROVED`.
4. **Precedência 4 (FSM & Rodadas):**
   - $N < 3 \to \text{REVISED}$ (avança rodada).
   - $N = 3$ sem overtime $\to \text{HELD_PROGRESS_REVIEW}$ (escalonamento humano).
   - $N = 3$ com overtime $\to \text{REVISED}$ (avança para R4).
   - $N = 4$ com overtime $\to \text{HELD_OVERTIME_EXHAUSTED}$ (terminal).

### 2.6 Substrato Físico (RTX 3090) e Atomicidade de I/O
- A inferência local opera sob **serialização estrita de turnos** para garantir zero estouro de VRAM na RTX 3090 (24GB).
- O I/O de artefatos utiliza gravação atômica (`write_text_atomic`, `write_json_atomic`) via escrita em `.tmp` seguida de `os.replace`.
- Concorrência protegida por `CaseLock` com identificação de PID ativo para autocura de processos órfãos.

---

## 3. Conformidade & Testes de Mutação (100% Kill Rate)

A solidez dos invariantes foi submetida a bateria de testes de mutação adversarial em [`tests/test_library_mutants.py`](file:///C:/projects/tare.tools.library/tests/test_library_mutants.py) (Mutantes M1 a M11), obtendo **100% de taxa de eliminação (11/11 mutantes eliminados)**:
- **M7 (Anti-Sybil Mutation):** Mutante que tentou forçar quórum com modelos duplicados foi eliminado.
- **M8 (Boundary Mutation):** Mutante que tentou executar além da Rodada 3 sem overtime ou além da Rodada 4 foi eliminado.
- **M9 (Header Injection Mutation):** Mutante de parsing em code fences Python foi eliminado.
- **M10 (Stale Lock Healing Mutation):** Mutante de contenção concorrente e PID morto foi eliminado.
- **M11 (Audit Falsifier Bypass):** Mutante que tentou burlar laudo de auditoria sem falsificador foi eliminado.

---

## 4. Consequências

- **Positivas:**
  - Imunidade matemática a loops infinitos e runaway token spend.
  - Custo de operação nulo ($0.00 de API) utilizando CLIs oficiais homologadas.
  - Dialética autêntica e não-complacente entre as três maiores famílias de fronteira do mercado.
  - Janelas de contexto compactas, determinísticas e auditáveis por hash.
- **Limitações:**
  - Exige a presença dos executáveis CLI locais (`agy`, `codex`, `claude`) no PATH do host para quórum `FRONTIER_UNANIMOUS`.
