# Rodada: performance da engine de testes/gates + fail-fast (2026-07-16)

Owner ask (intake via prompt-hook 2026-07-16): revisar código dos testes e a engine
que os roda; atrito/lentidão; onde vale cpp/PyO3/rust em pontos fixos; sugestões
automatizadas escaladas como decision com base em métricas; mocks suficientes vs
insuficientes; specs+BDD genéricas demais; técnicas clássicas de fail-fast (rápidos
primeiro, propensos-a-falha primeiro). Válido também para repos-alvo do harness,
porém CONTIDO/SEPARADO (métricas e decisões não se misturam).

## Pergunta

Como reduzir o tempo-até-primeira-falha e o tempo total do gate SPEC-137 (hoje
7–10 min) sem perder hermeticidade, retry anti-flake nem completude da bateria — e
como transformar essa vigilância de performance em rotina automática (métrica →
sugestão → decision), replicável de forma isolada nos repos-alvo?

## Critérios de sucesso

- Completude preservada: o gate de commit continua rodando TODOS os cenários
  (constraint do owner: "não deixem de rodar nossos testes em sua completude" —
  seleção preditiva que PULA testes só entra como camada opt-in de inner-loop,
  nunca no gate de commit).
- Hermeticidade preservada: snapshot/restore por cenário e retry-once continuam
  garantidos (foram a correção da flakiness — memória do projeto).
- Tempo-até-primeira-falha (TTFF) cai de "posição alfabética" para minutos iniciais.
- Qualquer skip/reordenação é determinística e auditável (sem ML opaco na v1).
- Métricas harness × repo-alvo separadas (o gate já tagueia `subject: self` vs
  target — usar essa costura).
- Toda proposta vira experimento registrado (EXP-N, docs/EXPERIMENT_METHODOLOGY.md)
  com baseline, métrica e critério de decisão ANTES de virar default.

## Orçamento declarado (regra do owner: waves só em modelo barato)

- Executores de wave: `nvidia-compat` (glm-5.2 primário, step-3.7-flash cheap) e
  `gemini-compat` (gemini-2.5-flash-lite). NENHUM wave em claude/codex.
- 1 wave de divergência (5 ideators) + 1 wave de crítica (4 críticos) no máximo;
  `workflow token-audit` antes de cada start; teto da rodada ≈ 150k tokens
  calibrados (chars/3.1). Gate de orçamento a 60%.
- Braçal de leitura em massa: `harness.py discover` (chain Gemini→NVIDIA), nunca
  leitura crua pelo orquestrador.

## Fase 0/1 — Evidência

### Medições [repo] (fonte: .harness/state/cost-metrics.json, gate records; runner: scripts/spec_test_gate.py)

| claim | fonte | tipo | confiança |
|---|---|---|---|
| Gate scenarios = 440–595s wall; spec-pack = 9–12s (irrelevante p/ otimizar) | cost-metrics gate records 2026-07-16 | measurement | forte |
| Runner é SERIAL e em ORDEM ALFABÉTICA (`sorted(glob)`), 1 subprocesso/cenário, snapshot+restore de estado volátil POR cenário, retry-once em falha | spec_test_gate.py:1546-1565, _run_isolated_scenario | repo | forte |
| Top-5 cenários ≈ 35% do wall: m4_status_html 59–73s, worker_live_tail 33–76s (alta variância sob carga), rs_research_skill 26–63s, cli_registry 23–27s, se_self_review 21–27s | gate records (últimas 4 rodadas) | measurement | forte |
| 128 arquivos de cenário, ~550 checks; cauda de ~123 cenários ≈ 350s ⇒ ~2,8s/cenário médio — parcela relevante é overhead fixo (spawn de interpretador + snapshot/restore), não assert | gate records + contagem; split exato não medido | measurement + judgment | moderada |
| `durationMs` por cenário já é emitido por rodada; `cost_metrics.record_gate` já guarda top-5 lentos por rodada (150 registros) — a matéria-prima de ordenação e de alerta automático JÁ EXISTE | spec_test_gate.py:94-95,1645-1651; cost_metrics.py:98 | repo | forte |
| Cenário que recupera em ≥2 de 5 rodadas = bug reaberto, não ruído (regra do owner); worker_live_tail e rs_research_skill são os flake-prone conhecidos | intake 583ff705e3ca; forensics .harness/runs/scenario-forensics | repo | forte |
| Separação harness×alvo já tem costura estrutural: linhas do ledger de validação são `subject: "self"`; runs --target passam por run_target_gate com stamp próprio | spec_test_gate.py:1608-1614 | repo | forte |

### Técnicas clássicas [web] (verificadas 2026-07-16)

| claim | fonte | ano | confiança | maturidade |
|---|---|---|---|---|
| Priorizar casos de teste por "mais importantes primeiro" maximiza taxa de detecção precoce; métrica APFD; família de técnicas por cobertura total/adicional | Rothermel/Elbaum, Test Case Prioritization: A Family of Empirical Studies (IEEE TSE ~2000-02), digitalcommons.unl.edu | 2002 | forte | produção |
| Pipeline em estágios: estágio 1 rápido (<10 min) com dublês/mocks para serviços lentos; estágios lentos depois — "cada minuto raspado do build é um minuto salvo por dev por commit" | martinfowler.com/bliki/DeploymentPipeline.html + articles/continuousIntegration.html | 2013/2024 | forte | produção |
| Paralelização de suíte: armadilhas = estado mutável compartilhado, portas fixas, ordem-dependência; port 0, namespacing por worker, random-order para caçar dependências | pytest-xdist docs + pythoneer.substack.com | 2024-25 | forte | produção |
| Seleção preditiva: Meta pega 99,9% das regressões rodando ~33% dos testes; Google TAP Transition Prediction reduziu mediana de detecção ~65% (107→37 min) — MAS pula testes, viola nossa completude no gate de commit | ICSE-SEIP 2019 (mpapad.github.io) + browserstack.com/guide/predictive-test-selection | 2019-25 | moderada | produção (fora) / contingência (aqui) |
| PyO3/maturin para hot paths fixos em Python é prática estabelecida; ganho real depende do perfil (I/O-bound não ganha) | referência: judgment (não verificada nesta rodada; probe local decide) | — | teórica | protótipo |

## Fase 2 — Briefs (GATE HUMANO — aprovar antes de qualquer wave)

- **B1 — Tempo-até-primeira-falha.** Ator: owner esperando commit. Problema: a
  ordem alfabética ignora duração e propensão a falha; uma falha em `w*` só aparece
  no minuto ~8. Critério: TTFF esperado < 2 min usando SÓ dados que o ledger já tem
  (durationMs + histórico de falha/recovered). Constraint: bateria completa sempre.
- **B2 — Custo fixo por cenário.** Ator: a engine. Problema: ~123 cenários "baratos"
  custam ~350s, muito disso overhead (spawn + snapshot/restore por cenário) e não
  asserção. Critério: cortar ≥30% do wall da cauda sem perder isolamento; medir
  split real overhead×assert antes de otimizar (probe determinística). Inclui: onde
  paralelizar com segurança (armadilhas pytest-xdist), onde rust/PyO3 pagaria
  (só ponto fixo/estável, sem recompilar a bateria), onde um mock basta (ex.:
  m4_status_html sobe servidor HTTP real — suficiente ou excessivo?).
- **B3 — Assertividade das checagens.** Ator: revisor de spec. Problema: checks
  genéricos demais (que nunca falham) dão falsa confiança; mocks insuficientes
  escondem integração real. Critério: inventário checks-que-nunca-falharam ×
  histórico; proposta de aperto por spec/BDD com evidência, não vibe.
- **B4 — Governança automática de performance.** Ator: owner (decisões) + harness.
  Problema: essa revisão foi manual ("sou eu quem está iniciando o pedido").
  Critério: regra determinística métrica→sugestão→decision (ex.: gate >X s por N
  rodadas, cenário >Y s, flake ≥2/5 ⇒ item em decisions/intake), com métricas de
  repo-alvo em espaço separado (subject-tag), zero mistura.

## Fases 3-4 — Waves executadas (2026-07-16, 100% nvidia-compat/glm-5.2)

- B1: SEM wave (aprovação do owner) — experimento direto EXP-11, implementado.
- B2 divergência: `WF-20260716-162149-026669` (5 perspectivas, 23 achados dedup;
  1 worker inválido; run tropeçou em PermissionError WinError 5 no workflow.json
  — lock Windows — e retomou limpo com um segundo `workflow run`).
- B3 divergência: `WF-20260716-162849-270831` (nunca-falhados via left-join,
  detector regex de assert fraco, matriz mock-vs-real por classe, BDD
  evidence-anchored, informação-por-check via amostragem leve de mutação).
- B4 divergência: `WF-20260716-162857-157371` (hook pós-gate, regras flat com
  cooldown/dedup, ledgers separados por subject NA COLETA, advisory-first,
  nunca auto-aplicar; segurança: redaction de env + limiares como trust surface).
- Crítica (seeded B2): `WF-20260716-164059-957736` (4 críticos; 2 partial).
  Achados decisivos: premissa de overhead NÃO MEDIDA (medição vira pré-requisito
  duro); in-process runner é hermeticidade ASSERIDA vs a estrutural do
  subprocess; fork/CoW inválido em win32; tier-promotion precisa de limiar com
  dados + drift-detector; PyO3 só se profile mostrar >5% do wall no chokepoint.

## Fase 5 — Operações por card e portfólio

| Card | Operação | Bucket | Destino |
|---|---|---|---|
| B1 fail-fast ordering | experimento → engavetada (v1) → **reaberta e shipped (v2)** | núcleo | **EXP-11 v2 shipped** — v1 (−87% TTFF replay) morreu por clusterizar pesados-flaky: só conhecia 9 durações. Reopen-trigger atendido pelo EXP-12 (126/126 durações no sidecar): v2 promove SÓ flaky<10s (19 cenários), pesados mantêm posição alfabética (espaçamento preservado). TTFF replay 201s→24s (−88%); live 3/3 rodadas verdes, contagens idênticas, zero double-fail/recovered. Reversão continua 1 linha |
| B2 medição overhead×assert | mantida (pré-requisito de TODA otimização B2) | experimentos | **EXP-12 shipped** — medido em 2 rodadas (spread 0,8 p.p.): spawn+boot real 0,08s (premissa 1,5–2s refutada ~20×), snapshot+restore 57s/rodada (12%), 10 pesados = 240s (51%). Cauda 26–27% = zona cinzenta. Consequência: spawn-opt DESPRIORIZADA (teto 9–46s), alavancas reais = EXP-13 (m4) e snapshot/restore. Crítica nvidia: warm-cache + 2 rodadas mesmo dia = não é morte definitiva; reopen-trigger registrado |
| B2 mock m4_status_html | premissa refutada → **fix de causa-raiz shipped** | núcleo | **EXP-13 shipped** — m4 NÃO tem servidor HTTP (2ª premissa falsa da wave B2). Custo real: `protected_files._glob_matches` fazia rglob do repo inteiro POR PATTERN (~44 walks/`compare_snapshot`) no drift scan do `status --html` (4 gerações × 13s). Fix: 1 varredura podada, paridade byte-idêntica (58×/chamada). m4 66-71s→7,3s (9×), `status --html` 13,1s→0,72s, gate ~406s (−60s+). Zero mudança em cenário — nenhum mock, tudo e2e real. rs:e2e-smoke reaberto à parte (intake d92c2144d5ab) |
| B2 in-process runner / pool / batch | adiada | contingência | só se EXP-12 provar overhead ≥40% E com protocolo de auditoria de purga de estado (crítica) |
| B2 fork/CoW batch | rejeitada | rejeitadas | win32 não tem fork; multiprocessing-spawn não dá CoW |
| B2 paralelização @parallel-safe | adiada | estacionadas | depende de EXP-12 + mapa de hazards; armadilhas clássicas documentadas |
| B2 PyO3/rust em chokepoints | estacionada | estacionadas | maioria das perspectivas: custo>benefício; reabrir só com cProfile mostrando >5% wall em ponto fixo |
| B3 inventário de assertividade | combinada → **shipped** | núcleo | **EXP-14 shipped** — probe `tools/check_assert_audit.py` (AST dos call-sites + join com forensics): 833 checks, 79% forte, 54 weak-shaped ranqueados. Julgamento em wave opus 4.8 xhigh (4 workers, regra de custo do owner): 11 asserts apertados em 8 cenários (destaque: `workflow:finalized`, rc-only E com falha histórica) + ~18 ok-as-is fundamentados. Fase 2 (spec-pack/BDD) aberta com reopen-trigger |
| B3 aperto BDD/specs | adiada | estacionadas | fase 2 do EXP-14 (só para os piores, com evidência) |
| B4 governança métrica→decision | mantida | núcleo | intake `020dfc7b4e7c` → spec SPEC-116 (advisory-first) |
| B4 seleção preditiva estilo Meta/Google | rejeitada (para o gate de commit) | rejeitadas | viola completude (constraint do owner); revisitável só como inner-loop opt-in |

## Rastreabilidade

Evidência → Problema → Ideia → Experimento/Decisão:
- cost-metrics 440-595s + serial alfabético → TTFF ruim → tiers fail-fast → EXP-11 (shelved: replay −87% mas clusterização de pesados dobrou flakes live; a metodologia funcionou — o critério de abandono pegou antes de virar default)
- EXP-11 live runs → NOVO achado de medição: a ordem alfabética estava fazendo espaçamento acidental de recursos entre cenários pesados — qualquer reordenação futura precisa preservar espaçamento (input direto pro EXP-12)
- média 2,8s/cauda [judgment não-medido] → overhead fixo? → crítica: medir primeiro → EXP-12
- top-5 lentos (m4 59-73s) → custo unitário → mock loopback → EXP-13
- checks nunca-falhados (suspeita) → assertividade → probe determinístico → EXP-14
- pedido manual do owner → governança → hook pós-gate advisory → intake 020dfc7b4e7c
- separação harness×alvo → subject-tag existente → ledgers separados na coleta (design B4)

## Status

- [x] Fase 0/1: evidência (medições locais + fontes clássicas)
- [x] Gate humano: owner aprovou B1 direto + waves B2/B3/B4 (2026-07-16)
- [x] Fase 3: 3 waves divergência + [x] Fase 4: 1 wave crítica (tudo nvidia)
- [x] Fase 5: EXP-11 ativo; EXP-12/13/14 proposed; intake B4; portfólio acima
