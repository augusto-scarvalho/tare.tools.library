# Rodada R4 — Métricas de construto (definições pré-registradas + probes)

Rodada 4 de 5 (D012, NVIDIA, sequencial, backlog-first). Gate humano fase 2
pré-aprovado pela D012.

## Fase 0 — Pergunta, critérios, budget, largura, design

- **Pergunta:** quais construtos do artigo (§3.5, §5.7, §6.2, §9.5) ainda NÃO
  medimos podem virar probe measure-only determinístico sobre o estado que já
  temos, e qual a definição pré-registrada de cada um (fórmula, corpus, o que
  conta como sinal vs ruído)?
- **Alvos (do backlog):** route churn (§3.5, pré-req da histerese C9); CTS
  (§9.5-b, quase de graça do delegation ledger — já tem brief C6); Π-lite (§3.5,
  depende de noise floor L13 ✅ + trace completeness L4 ✅); métricas de recovery
  (§5.7: duplicate-effect, orphaned work, time-to-resume); precision/recall de
  contexto e used-context ratio (§6.2).
- **Critérios:** cada métrica sai com (a) fórmula, (b) corpus/seam no repo hoje,
  (c) definição de ruído (delta < floor = não-evidência, regra L13), (d) veredito
  measure-only vs precisa-de-novo-estado. Nada de enforcement.
- **Largura (D010): FOCADA-3** — o tema é definido (métricas nomeadas), não
  exploração aberta; 3 workers particionados: B1 routing (churn/regret/calibração),
  B2 recovery+efeitos (§5.7), B3 contexto+economia (§6.2/§3.5 + Π-lite). Δ_m de
  cada = sua fatia.
- **Budget:** wave única ≤ 40k. Executor `nvidia-compat`. Override esperado.
- **Design (L18):** produz DEFINIÇÕES pré-registradas + desenhos de probe. Cada
  probe futuro que vira EXP cita o cartão de métodos na hora (noise floor p/ os
  spreads; matched-budget p/ os que comparam). Não roda medição nesta rodada —
  desenha as medições.

## Execução

Wave: `WF-20260718-222420-548481` (3 workers por construção, GLM, 3/3 válidos após
2 re-dispatches — breaker global reabriu por herança de falha de crítica anterior;
lição: resetar/aguardar breaker entre rodadas). 15 métricas desenhadas.

## Síntese — métricas de construto (measure-only vs needs-new-state)

Veredito por métrica, auditado contra os seams reais. **measure-only-hoje** = todos
os inputs existem → probe determinístico committável já. **needs-new-state** = falta
um campo/denominador, nomeado.

| métrica | ref | veredito | fórmula (resumo) | corpus | falta (se needs-new-state) |
|---|---|---|---|---|---|
| **CTS** | §9.5-b | ✅ measure-only | Σ estTokens ÷ count(outcome=kept); +byModel | delegation ledger | — (confirma o brief C6 buildável) |
| **route churn** | §3.5 | ✅ measure-only | count(chosenRoute_i≠_{i-1} sem evidência nova)÷count(demandId) | route ledger L7 | — (spread por Floor B/L13) |
| **Π-lite** | §3.5 | ✅ measure-only | ⟨1−viol, 1−overrun, 1−replay_div, recovery, 1−unknown⟩ | route ledger + cost + replay-class L3 | — (avg não compensa violação crítica) |
| **ctx precision** | §6.2 | ✅ measure-only | objetos apresentados ligados a uso ÷ apresentados | E1 context-digest | — |
| **used-context ratio** | §6.2 | ✅ measure-only | objetos ligados por relação tipada ÷ apresentados | E1 context-digest | — |
| **orphaned work** | §5.7 | ✅ measure-only | workers sem transição terminal | records ledger lifecycle | — |
| **provenance continuity** | §5.7 | ✅ measure-only | cadeia causal intacta pós-recovery | records + replay-class | — |
| **recovery-point error** | §5.7 | ✅ measure-only | desvio estado recuperado vs último-bom | records + gate results | — |
| **time-to-resume** | §5.7 | ✅ measure-only | latência até retomar pós-crash | records lifecycle | — |
| route regret | §9.5-a | 🔬 needs-new-state | U(melhor rota retrospectiva) − U(escolhida) | route ledger | **função U(rota,outcome,custo)** + cálculo retrospectivo — decisão do owner sobre U |
| routing calibration/ECE | §9.5 | 🔬 needs-new-state | Σ_bins \|pred − realizado\| | route ledger | **campo predictedP** por decisão de rota (router não emite confiança) |
| ctx recall | §6.2 | 🔬 needs-new-state | evidência requerida recuperada ÷ requerida | E1 digest | **conjunto "requerido" gold** por decisão |
| A_ctx | §6.2 | 🔬 needs-new-state | tokens apresentados ÷ tokens lógicos únicos | cost_metrics (numerador) | **denominador "unique logical tokens"** (já diferido na rodada de memória) |
| duplicate-effect rate | §5.7 | 🔬 needs-new-state | efeitos externos duplicados ÷ efeitos | records | **effect-id/idempotency-key** nos records (efeitos externos raros hoje) |
| compensation outcome | §5.7 | 🔬 needs-new-state | classe exact/business-eq/partial/impossible | records | **registros de compensação** (não há saga hoje) |

### Achados que fecham loops
1. **CTS confirmado buildável AGORA** — o brief LQ7-C6 estava certo; esta rodada
   dá a fórmula pré-registrada (denominador = outcome kept; variante byModel).
2. **route churn é o pré-requisito medível da histerese C9** — buildável já; o
   backlog dizia "medir antes de controlar", e agora há a fórmula + o Floor L13
   como régua de ruído. C9 (cooldown no route-loop) só depois desta medição.
3. **Π-lite é o perfil de previsibilidade do §3.5** — buildável, e a regra
   "média alta não compensa 1 violação crítica" é o mesmo espírito da lexicográfica
   (brief C1). Casa as duas.
4. Os 5 needs-new-state se agrupam: 2 são de router (U + predictedP — uma decisão
   de owner sobre função de utilidade destrava regret+ECE juntos); 2 são de efeito
   externo (effect-id + compensação — só valem quando efeitos externos crescerem);
   1 é o A_ctx já diferido com gatilho.
