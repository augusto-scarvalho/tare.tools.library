# Rodada RD-U — a função de utilidade U(rota, outcome, custo) do harness

Research-gated backlog item RD-U (article-coverage-backlog.md). Owner 2026-07-19:
"faça uma lista e rode o research usando nvidia sequencialmente". 1ª das 3 rodadas
de implementação-research. Orquestrador = esta sessão. Divergência via **NVIDIA**
(`nvidia-compat`, glm-5.2).

## Por que esta rodada existe

Route **regret** (EXP-17) e **ECE/calibração** hoje são NEEDS-NEW-STATE: não dá
pra computar regret sem uma função de utilidade `U` que diga o quão boa foi uma
decisão de rota. Sem U, "a rota A foi melhor que a B" é opinião. RD-U destrava os
dois de uma vez. Isto é research de COMO IMPLEMENTAR (que termos, que forma, como
estimar), não de medição acadêmica.

## Pergunta da rodada

> Qual é a função de utilidade `U(rota, outcome, custo)` do harness — quais termos
> ela combina, que forma (linear/ponderada/lexicográfica/...), e como estimar cada
> termo A PARTIR DO QUE JÁ TEMOS (delegation ledger: custo em tokens, latência,
> outcome kept/rejected; escassez por vendor do N-VENDORCREDIT; accountingSemantics
> do T-ADAPTERCONF dizendo quais tokens são medidos vs estimados)?

## Critérios de sucesso

- **Atores:** o router (usa U pra escolher/avaliar rota), o EXP-17 (computa regret =
  U(ótima) − U(escolhida)), a calibração ECE (confiança da rota vs outcome).
- **Estimável do corpus atual:** cada termo de U tem que mapear pra um campo que o
  delegation ledger / model-cards / vendor-credit JÁ produzem — nada que exija
  instrumentação nova cara. O owner (D017): "o que pesa mais são tokens gastos e
  tempo; token e tempo são dinheiro" — U tem que honrar isso.
- **Honesta sobre incerteza:** onde o outcome é subjetivo (qualidade), U marca o
  termo como estimado/proxy, não finge medir. accountingSemantics: vendors que
  não medem token de verdade entram com peso de confiança menor.
- **Determinística de computar:** dado (rota, outcome, custo), U(...) é um número
  reproduzível — sem LLM no caminho de cálculo (LLM pode ter ajudado a DESENHAR U,
  nunca a computá-la em produção).
- **Não reinventa:** reusa delegation ledger (route_ledger), cost_metrics, os
  route scores (E-ROUTESCORES), o noise floor L13 (diferença menor que jitter não
  é sinal de regret).

## Orçamento + largura + design declarado

- **Onda 1:** 5 ideadores NVIDIA, teto ~65k tok (free-tier). Gate a 60%.
- **Largura (D010): EXPLORATÓRIA → 5.** Desenho de função de utilidade cruza
  teoria de decisão, MAUT/utilidade multi-atributo, bandit reward design, RL
  reward shaping, econometria de custo — campo amplo, sem forma fixa ainda. Grupo
  nominal paga.
- **Design (L18):** a rodada FEEDA o EXP-17 (regret) e a calibração ECE. Cartas de
  método candidatas (o advisory agora dispara — commit e5a1a4b): **evidence-grades**
  (o quão forte a evidência de que U reflete a realidade) + **matched-budget
  controls** (comparar rotas com orçamento igualado, senão U confunde "melhor" com
  "gastou mais"). A carta final entra na síntese.

## Fase 3 — brief da onda 1

> Projete a função de utilidade `U(rota, outcome, custo)` do harness. Ela precisa:
> combinar custo-em-tokens (ponderado por preço/vendor), tempo/latência, e
> qualidade-de-outcome (kept vs rejected/reverted) num número comparável entre
> rotas; ter forma justificada (por que ponderada e não lexicográfica, ou
> vice-versa); estimar CADA termo de campos que o delegation ledger / model-cards /
> vendor-credit JÁ produzem; honrar o accountingSemantics (peso de confiança menor
> pra vendor que estima token em vez de medir) e a escassez por vendor (token
> escasso vale mais); e ser determinística de computar (sem LLM no cadeia de
> cálculo). Entregue: os TERMOS de U, a FORMA (com a justificativa), o MAPA
> termo→campo-do-ledger, e como regret = U(ótima)−U(escolhida) e a confiança pra
> ECE saem de U.

---

# Fase 3-5 — resultado e síntese (RD-U)

Onda 1: `WF-20260719-054755-523380`, 5 ideadores NVIDIA (glm-5.2).

## Convergência independente (o sinal forte — TODOS os 5)

**Forma = WEIGHTED-LINEAR, normalizada/bounded.** Os 5 escolheram linear sobre
lexicográfica E sobre Cobb-Douglas, com a MESMA justificativa tripla (w-001, w-004):
linear é a única forma que (a) dá um escalar comparável entre rotas, (b) é O(1)
determinística, (c) permite comparação por-termo contra o noise floor. Lexicográfica
não produz um ΔU escalar pra ECE; Cobb-Douglas (multiplicativa) quebra a comparação
com o L13 e colapsa U→0 quando Q=0 (rota rejeitada) — o próprio w-005 refutou a
Cobb-Douglas que ele mesmo sugeriu (honestidade de ideador).

## A função convergida

```
U(rota) = w_q·Q·τ  −  w_c·C·S  −  w_t·T
```
| termo | o quê | campo do corpus (zero instrumentação nova) |
|---|---|---|
| **Q** | qualidade do outcome: kept=1, reverted=0.5*, rejected=0 | `route_ledger` outcome enum |
| **τ** (w-004) | trust-discount do accountingSemantics: vendor que MEDE token τ=1, que ESTIMA τ<1 | T-ADAPTERCONF `accountingSemantics` |
| **C** | custo = tokens × preço-do-vendor, normalizado por route-class | ledger token-cost + model-cards price |
| **S** | escassez = `max(1, 1/(remainingCredit/initialCredit))` — token de vendor quase esgotado vale mais | N-VENDORCREDIT |
| **T** | latência normalizada pelo budget/p99 da route-class | ledger latency + E-ROUTESCORES/cost_metrics |

\* `reverted=0.5` é a ÚNICA constante subjetiva de U (w-001 sinalizou: validar; se
revert ≈ near-failure, 0.25 é melhor). Registrado como o único parâmetro a calibrar.

## O que cada perspectiva adicionou

- **w-001 (simplicidade):** S e τ como MULTIPLICADORES no termo de custo/qualidade,
  não termos separados — mantém 3 termos. `regret = U(best)−U(chosen)`; ECE via
  U-gap sigmoid-normalizado; `|ΔU| < noiseFloor L13 → empate` (sem sinal de regret).
- **w-002 (escala):** normalização bounded [0,1] pra comparabilidade cross-route;
  T normalizado pelo p99 da route-class (do cost_metrics).
- **w-003 (confiabilidade):** edge-case de OPS — definir U para **timeout/falha
  parcial** (U=0 ou penalidade explícita), senão uma rota que trava vira ruído.
- **w-004 (trust-boundary):** o τ (trust-discount) — sem ele, U trata um vendor que
  CHUTA token igual a um que MEDE. + **privacidade:** U toca só AGREGADOS (custo/
  latência/outcome), NUNCA conteúdo de payload; computada na trust-zone do ledger,
  SEM chamar API de vendor (senão o vendor observa a decisão de routing e infere uso
  do concorrente). ECE usa Q·τ como probabilidade prevista.
- **w-005 (analogia): Sharpe ratio / mean-variance de finanças** — `U = E[R] −
  (λ/2)·σ²·scarcity`: retorno=qualidade, RISCO=variância, custo=fees. **A variância
  do Sharpe É o noise floor L13** — uma rota de alta variância de outcome é mais
  arriscada. + **Brier score (meteorologia)** decompõe em reliability = ECE. O termo
  de variância fica pra v2 (a linear é v1).

## Cartas de conceito + operação

| carta | operação | por quê |
|---|---|---|
| **U-LINEAR** (a função acima) | **mantida** — o núcleo | forma comprovada, determinística, todos os termos do corpus atual |
| **U-TAU** (trust-discount accountingSemantics) | **mantida** | fecha o buraco "vendor que chuta = vendor que mede" |
| **U-SCARCITY** (S do N-VENDORCREDIT) | **mantida** | honra o D017 (token escasso vale mais) — mas depende do N-VENDORCREDIT ter o `remainingCredit` |
| **U-VARIANCE** (Sharpe: penalizar variância de outcome) | **adiada (v2)** | precisa de N observações por rota pra estimar σ²; a linear v1 não precisa. Upgrade quando houver corpus |
| **U-OPS** (U em timeout/falha) | **dividida** | define U=0/penalidade pra falha — vira parte do spec de U |
| **reverted=0.5** | **experimento** | o único parâmetro subjetivo; calibrar contra dados reais de revert |

## Buildável vs owner-gated

- **Buildável já (medição):** U como FUNÇÃO PURA computada sobre o route_ledger
  existente, alimentando um probe de regret measure-only (EXP-17). Não muda routing,
  só mede — dentro da alçada measure-first, como os outros probes.
- **Owner-gated:** usar U pra DIRIGIR routing (bandit/C4/RF.1 fase 2) — já é
  owner-gated. E o N-VENDORCREDIT precisa existir pro termo S ter dados reais (até
  lá, S=1, honestamente marcado).

## Rastreabilidade

| Evidência | Ideia | Experimento | Task | Status |
|---|---|---|---|---|
| 5/5 (weighted-linear) + w-005 Sharpe/Brier | U-LINEAR + U-TAU + U-SCARCITY | alimenta EXP-17 regret + ECE | RD-U→U-função | desenhado, buildável (measure-only) |
| w-001 (reverted=0.5) | calibrar a constante | EXP candidato | reverted-calibration | aberto |
| w-005 (variância=L13) | U-VARIANCE v2 | — | parked | adiada |
