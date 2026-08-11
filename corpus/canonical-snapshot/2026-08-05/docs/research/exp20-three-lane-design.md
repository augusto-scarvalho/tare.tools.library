# Rodada R5 — EXP-20: comparação 3-lanes fork-join harness vs codex nativo (design)

Rodada 5 de 5 (D012, NVIDIA, sequencial, backlog-first). ÚLTIMA. Produz o
pré-registro do EXP-20 (não roda o experimento). Gate humano fase 2 pré-aprovado.

## Fase 0 — Pergunta, critérios, budget, largura, design

- **Pergunta:** o fork-join NATIVO do codex (aposta D, provado pelo EXP-19)
  entrega qualidade/custo diferente do fork-join do harness na MESMA classe de
  task com budget igualado? E o ranking inverte entre o lane normalizado
  (harness-mediado) e o lane nativo (H31 do artigo)?
- **Contexto (do repo):** EXP-19 provou o maquinário (spawn_agent nativo sob
  `codex exec`, nomes underscore, resultado consolidado). C13/L9 dá a tupla de
  rota pinada. L13 dá o noise floor. As 5 primitivas de contenção (R2) e o
  matched-budget (EXP-15) são pré-requisitos de um teste JUSTO.
- **Critérios:** o desenho tem que (a) ser 3-lanes SEM pooling (normalized-core /
  native-worker / governed-hybrid — §8.4/§9.4-t); (b) matched-budget real (mesmo
  snapshot, mesmo budget de token — não label de effort, C13); (c) split-plot com
  vendor/snapshot como whole-plot (troca cara) e knobs por-task como sub-plot;
  (d) métrica que separa qualidade de custo de ranking-reversal; (e) noise floor
  L13 como piso — delta < spread cross-WF = não-evidência.
- **Largura (D010): FOCADA-2** — o alvo é 1 desenho experimental definido, não
  exploração; 2 workers: B1 desenho estatístico (lanes, split-plot, matched-budget,
  o que pinar), B2 instrumentação (que seams do harness medem cada lane; onde o
  codex nativo não dá o dado e o que é proxy honesto). Δ_m de cada = sua metade.
- **Budget:** wave única ≤ 30k. Executor `nvidia-compat`. Override esperado.
- **Design declarado (L18):** cartões `Matched-budget controls` + `Split-plot`
  de EXPERIMENT_METHODS.md são o método; o EXP-20 será registrado
  `status: proposed` citando os dois cartões. A medição fica OWNER-GATED (muda
  o core reduce se promovida — porta SPEC-116).

## Execução

Wave: `WF-20260718-223240-760885` (2 workers por construção, GLM, 2/2 válidos,
10 peças de design). Desenho coerente e completo — registrado como EXP-20
(`status: proposed`).

## Desenho pré-registrado do EXP-20 (3 lanes, split-plot, matched-budget)

**Lanes (nunca pooled — §8.4):**
1. `normalized-core` — ambos vendors pelo contrato de worker normalizado do harness.
2. `native-worker` — fork-join do harness vs `spawn_agent` nativo do codex.
3. `governed-hybrid` — harness orquestra, delega a workers nativos.
Inversão de ranking entre lane 1 e 2 = evidência de interação model×harness (H31),
não erro de medição.

**Fatores (split-plot — cartão Split-plot):**
- Whole-plot (troca cara, batch antes de trocar): vendor, modelSnapshot,
  adapterVersion.
- Sub-plot (barato, randomiza dentro do bloco): topologia (1-worker control vs
  3 vs 5), contextPolicy.
- Dois estratos de erro, analisados separados — nunca pool.

**Matched-budget (cartão Matched-budget controls):** budget = soma de tokens
provider-native OBSERVADOS (não planned/estimated, não label de effort — H30);
mesmo modelSnapshot em todas as lanes. O control 1-worker é o braço EXP-15.

**Instrumentação (seams reais):**
- Oráculo de qualidade: checker determinístico stdlib (diff/parse/compile) no
  artefato final de cada lane; para o lane nativo, pontua o resultado consolidado
  do parent.
- Tokens provider-native: `token-audit` por worker nas lanes 1 e 3; lane 2
  (codex nativo) = **proxy parent-delta rotulado EMULATED, nunca pooled** com
  medição real (disciplina native/emulated §8.4 — liga em C3/C16b).
- Estabilidade de ranking: Kendall tau dos scores por-cenário dentro de cada
  lane; abandona se a variância do tau entre os 5 WFs congelados > Floor B (L13).
- Task-class congelada: route tuple pinada (mesmo modelSnapshot) + cenários
  determinísticos stdlib (parse/transform/compile).

**Gap honesto (§8.4 emulated):** codex nativo NÃO expõe contabilidade de token
por-subagente → toda figura por-subagente do lane 2 é EMULATED (fórmula:
parent-process total dividido) com incerteza declarada; tabela de gap
`{métrica, lane1-seam, lane2-proxy, lane3-seam}` por métrica.

**Piso (L13):** ambos os floors medidos ANTES da comparação, no mesmo task set
congelado; efeito < spread cross-WF = não-resolvido.

## Registro

EXP-20 registrado `status: proposed` (medição OWNER-GATED — mudar o default de
topologia/reduce é porta SPEC-116). Cita os cartões Matched-budget + Split-plot.
Ativação e execução ficam para quando o owner abrir a fila de implementação.
