# Race-mode test #1 (item #4, 2026-07-19)

Owner: "pode rodar algo pra testar" (race-mode / D016). Primeira corrida real
usando o instrumento E-3LANE (tarefas congeladas + oráculo stdlib) — 3 modelos
NVIDIA competindo nas mesmas tarefas, custo/tempo/acerto medidos.

## Setup
- Tarefas: `parse-json-total` (extrair int de JSON) + `compile-add-function`
  (escrever `def add(a,b)`), do E-3LANE. Oráculo determinístico stdlib.
- Modelos (NVIDIA Build, free-tier): glm-5.2, llama-3.3-70b, deepseek-coder-6.7b.
- temperature=0, max_tokens=400. Free-tier (custo desprezível).

## Resultado (2ª rodada, pós-fix do oráculo)
| modelo | acertos | tokens | tempo total | nota |
|---|---|---|---|---|
| **z-ai/glm-5.2** | **2/2** | 91 | **6.5s** | vencedor — rápido e certo |
| meta/llama-3.3-70b | 1/2 | 80 | **53.7s** | lentíssimo no endpoint; 1 timeout |
| deepseek-ai/deepseek-coder-6.7b | 0/2 | 0 | — | HTTP 404 (id não servível por este endpoint) |

**Veredito:** pra micro-tarefas determinísticas, o glm-5.2 domina (nossa escolha
primária de smart-tier já estava certa). O race-mode funciona: mesma tarefa, N
cérebros, oráculo neutro decide, custo/tempo comparáveis lado a lado.

## O achado que valeu mais que o resultado
A 1ª rodada marcou o glm como "fail" no compile — mas a resposta dele estava
CERTA (`def add(a,b): return a+b`), só embrulhada em ` ```python `. **O oráculo do
E-3LANE não tirava a cerca de markdown antes de compilar.** A corrida expôs uma
fraqueza no instrumento que EU construí. Consertado: `_strip_code_fence` no
`oracle` (testing/probes/three_lane_probe.py); self-check verde; re-corrida → glm
2/2. É exatamente o que testar de verdade faz — o modelo estava certo, o juiz
estava errado.

## Limites honestos desta corrida
- 402/erro por modelo indisponível (deepseek 404, llama timeout) vira "perdeu" —
  o runner distingue ERR de fail, mas um race sério precisa de retry/timeout-budget
  por modelo (não penalizar o modelo pela lentidão do endpoint free-tier).
- 2 tarefas × 3 modelos é anedótico — um race-mode de produção precisa de N
  tarefas por classe + repetição (o noise floor L13 se aplica: diferença menor
  que o jitter não é sinal).
- Runner ficou no scratchpad (measure-only, throwaway). Promover a um verbo/probe
  de verdade é o item de race-mode (D016) quando você quiser — o instrumento
  E-3LANE + este runner são a base.

## Próximo (race-mode de verdade, se você quiser)
Um `--live` de verdade no E-3LANE (hoje recusa) que: roda N tarefas × M modelos
com retry/timeout por modelo, aplica o noise floor, e emite a tabela de vencedor
por classe de tarefa. É a medição owner-gated do EXP-20. Este teste provou o
maquinário e já pagou um bug do oráculo.
