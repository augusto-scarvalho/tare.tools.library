# Weekly monitor W28 (qualidade de código agêntico) — extrato para o harness

Fonte: digest semanal GPT fornecido pelo dono (2026-07-13). NÃO é uma rodada
de research (mesma ordem do extrato de memória: não rodar o skill); citações
são `[web]` não-verificadas — ideias avaliadas pelo mérito interno contra o
estado real do harness. Companheiro de
`weekly-monitor-w28-memory-extract.md`; numeração de experimentos continua
(EXP-4..6).

## Onde o harness JÁ cobre o digest (sem trabalho novo)

| Achado do digest | Equivalente já operante aqui |
|---|---|
| #1 Patchwork Problem (grafos + invariantes estruturais) | Parcial: Graphify é a representação em grafo (AST/imports); verificadores declarado-vs-real já vivos: spec_test_gate (`Scenario: [id]` ↔ literal `check("id")`), superfície CLI congelada (FROZEN_TOP_LEVEL), schema WORKER_RESULT vs payload real, registry de protected-files, agent_parity. O que NÃO existe é o inventário sistemático dos pares → EXP-4 |
| #2 Failure as a Process (erro epistêmico cedo, intervenção na trajetória) | O modelo overseer-plans É intervenção precoce institucionalizada: premissas resolvidas ANTES do worker gastar (plano com decisões FINAIS + footprint HARD); `planDeviations` tipado é o canal "a premissa era falsa"; `harness.py review` roda antes do commit (meio da trajetória, não pós-merge). Residual: o erro epistêmico do PRÓPRIO plano (incidente Q10) → EXP-6 |
| #3 SCATE / lazy generation | `oracle mutate` recém-shipped detecta exatamente o sintoma (SURVIVED → ORACLE-WEAK; 1ª rodada live: 3 survived corretos). O bandit router fica estacionado (telemetria tem 1 dia) |
| Agentic Rubrics (ACL) | Os Gherkin dos specs SÃO rubricas contextuais; a onda GLM spec-QA foi rubric-checking barato multi-vendor |
| SWE-Mutation (ACL) | `mutation_probe.py` shipped hoje: mutantes AST determinísticos, cap 3, restore byte-idêntico — a versão observe-only sem custo LLM |
| SecureVibeBench (segurança não-compensável) | security-baseline existe observe-only por decisão do dono (#1); ir além é OWNER-GATED — pendente de decisão, não de gatilho |
| RuBench (fallback silencioso de modelo) | Vivemos o incidente: codex ≥0.144 ignorando profiles do projeto (spec esh) — flags explícitas foram o band-aid. Proveniência REAL não é registrada em lugar nenhum → EXP-5 |
| SLBench (skills com pré-condições lógicas) | Parcial: skills registradas em capabilities.json; pré-condições em prosa. 3 skills hoje — estacionado |

## Experimentos extraídos (reversíveis; template do research-playbook)

### EXP-4 — Patchwork replay probe (declarado-vs-real) · prioridade ALTA
- **Hipótese**: o harness tem N pares declarado-vs-real e só parte tem
  verificador; violações reais passam por gates verdes (o placebo compact
  hook viveu semanas com tudo verde — nosso patchwork problem de estimação).
- **Inventário candidato** (calibrado por incidentes históricos, como o
  digest manda): chaves de `model-routing.json` declaradas vs lidas pelo
  código; skills em `capabilities.json` vs `SKILL.md` presentes; eventos
  emitidos vs consumidores existentes; spawn mappings de task-profiles vs
  executor cards; hooks registrados vs efeito observável (o placebo);
  trustTier declarado vs ações do worker.
- **Baseline**: rodar o inventário UMA vez; contar pares sem verificador +
  violações vivas hoje (probe determinístico, zero LLM).
- **Métrica**: recall de violações reais por custo — não volume de alertas
  (regra do digest que adotamos integralmente).
- **Fase 2 (só pares com violação encontrada)**: cada par vira check
  advisory do doctor (padrão intake-staleness). **Reversão**: checks
  advisory, remove-se uma linha cada.

### EXP-5 — Auditoria de proveniência de modelo (RuBench-lite) · prioridade ALTA, barata
- **Hipótese**: o modelo REAL que atendeu cada delegação não é registrado:
  o ledger grava o modelo PEDIDO (auto-declarado pelo overseer), o
  WORKER_RESULT não tem campo de modelo, e `tools/openai_worker.py` descarta
  o campo `model` da resposta da API (verificado 2026-07-13). A unidade real
  de avaliação é produto+harness+política de fallback+modelo.
- **Fase 1 (zero risco)**: openai_worker anexa `response.model` ao resultado;
  codex: parsear o banner do `exec`; ledger de delegação ganha campo opcional
  `servedModel` (aditivo, `(none)` para registros antigos — padrão byOutcome).
- **Métrica**: % de delegações com requested≠served; qualquer valor >0 é
  achado acionável.
- **Reversão**: campos aditivos, ignoráveis.

### EXP-6 — Pré-flight epistêmico do plan brief · prioridade MÉDIA
- **Hipótese**: o erro epistêmico residual do loop mora no plano do
  overseer, não no worker (Q10: o plano mandou latin-1, os artefatos eram
  CP1252 — 1 defeito de plano em 12 briefs ≈ 8%).
- **Fase 1**: seção "Premissas verificadas (com evidência)" no template de
  plan-brief do playbook — cada premissa não-trivial cita o comando/leitura
  que a confirmou ANTES do brief ser entregue.
- **Fase 2 (determinística, opcional)**: `review --preflight <brief>` —
  paths do footprint existem ou estão marcados `(new)`; comandos de verify
  citados existem na superfície CLI. Advisory, rc 0.
- **Métrica**: taxa de planDeviations atribuíveis a defeito de plano por
  sessão de loop, antes/depois.
- **Reversão**: seção de template + modo advisory.

## Estacionados (com gatilho explícito)

- **Oracle Action Router (SCATE)**: gatilho = semanas de telemetria
  byOutcome + oracle acumuladas; a recompensa composta exige medir o que
  ainda não medimos. A política fixa atual É o baseline que o router terá
  de bater.
- **Diversify2Verify**: gatilho = primeira função crítica exigindo
  verificação formal; custo n-variantes alto demais para o perfil atual.
- **Mutantes LLM calibrados (SWE-Mutation completo)**: gatilho = o menu
  determinístico do mutation probe saturar (survivors caindo a zero sem
  bugs reais aparecendo).
- **SLBench interno (pré-condições de skill compiladas)**: gatilho =
  primeira falha operacional de skill por pré-condição violada; hoje são 3
  skills e prosa cobre.
- **SecureVibeBench gate não-compensável**: sem gatilho — é OWNER-GATED
  (security-baseline além da decisão #1); aguarda decisão do dono, não
  evidência.

## Veredito crítico do digest

Este digest, sem saber, valida com literatura o lote que shippamos HOJE:
review verb = intervenção na trajetória (#2), mutation probe = detecção de
oráculo fraco (#3/SWE-Mutation), planDeviations = erro epistêmico tipado
(#2), byOutcome = economia mensurável (#3). A novidade genuinamente
acionável são dois probes de medição baratos: EXP-4 (inventário
declarado-vs-real) e EXP-5 (proveniência de modelo — lacuna confirmada no
código). O EXP-6 ataca o único ponto do nosso loop que o digest ilumina e
nós ainda não instrumentamos: o plano do overseer como fonte de premissa
falsa. Nada aqui justifica router adaptativo ou geração de variantes antes
dessas medições existirem.
