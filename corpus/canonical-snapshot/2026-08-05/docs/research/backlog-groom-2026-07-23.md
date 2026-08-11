> APPLIED 2026-07-23 by overseer (post-audit): 33 `discard` + 11 `done` + 9 `backlog` =
> 53 decided via `intake decide`; pending 53->0. Audit confirmed every done-in-git sha
> in `git log` and the 3 still-valid live claims (encoding residual, rt6 timing, SSE) by
> reading code/telemetry. +2 entries arrived after the miner's slice (`11686fc57f09`
> codex-fuel-followup -> backlog; `898ffa513164` groom-hook ask -> done in b309625).

# Backlog groom -- fila de intake, 2026-07-23 (queue-slice)

Rodada queue-slice (playbook `.harness/prompts/backlog-groom-playbook.md` §1-2),
wind-down do loop AFK `gui-react-parity` + 4 ondas de backlog AFK. Fila lida via
`python scripts/harness.py intake list --json` (HARNESS_QUIET=1): **51 pendentes**.

A fila estava heavily poluida pelo hook UserPromptSubmit intake-triage: a maioria
das 51 entradas sao mensagens de conversa cruas capturadas de uma sessao
interativa (perguntas do owner, instrucoes de orquestracao/recursos, comandos
raw de plan-spawn "Read .harness/handoff/plan-X.md and implement EXACTLY..."),
nao pedidos de backlog isolaveis. Cada uma foi lida e classificada
individualmente contra o vocabulario do playbook; toda done-claim foi verificada
em `git log` (nunca assumida) e os 3 gaps de "scenario-hot"/encoding foram
re-verificados lendo o codigo/telemetria AO VIVO, nao so o commit message.

## Ledger (51/51)

| id | summary | verdict | evidence |
|---|---|---|---|
| 09de5548ecb4 | Pergunta: "subprocessedges pode rodar enquanto trabalhamos?" | discard-noise | Q&A de sessao sobre feature ja shipada as 07:48 (5268938); sem ask isolavel |
| 1d983501b5a7 | Pergunta: "a gente não estava processando o ast então?" | discard-noise | Q&A de sessao sobre o Graphify AST policy; sem ask isolavel |
| ac7ae80b3a70 | Ask: investir em corrigir tráfego TSV vs JSON quebrado | done-in-git | `6710f3d` (fase 6, "fronteira TSV/JSON estrutural") + `a9f453d` ("TSV boundary P1... fecha a matriz 4 pernas"), ambos ~40-70min depois do ask (12:29 -> 13:17/13:38) |
| bc3e30772c45 | Spec informal: matriz 4-pernas agente-tsv / app-json + parser no meio | done-in-git | `6710f3d`: "TSV/JSON boundary (matriz 4 pernas do owner): from_tsv canonico em common.py..."; cita literalmente a matriz do owner |
| f99443c2b651 | Ask: hook/estrutura pra garantir tráfego+parsing TSV | done-in-git | `a9f453d`: "clausula das seams vivas no subagent-contract (valvula canonica)" + cenario tj-6/tj-7 -- a estrutura pedida |
| 9943b8d73c98 | Pergunta: skips servem pro reckon entender onde não olhar? | discard-noise | Q&A tecnica de sessao, sem artefato a produzir |
| 948c81a2ac6f | "que tal priorizar agora? ou temos impedimento?" | discard-noise | steering puro de sessao |
| df5f5c1e5bbc | Reclamação: front-end incompleto, "cadê o resto da GUI nova?" | discard-noise | mensagem de sessao que da o kickoff do loop gui-react-parity; não é item em si |
| b098ff7efade | "vai colocando o codex pra programar também" | discard-noise | instrucao de alocacao de recursos, nao ask de feature |
| 0bb45d35f00f | Spawn raw: "Read plan-gui-port-research.md and implement..." | discard-noise | comando mecanico de spawn, plano ja existe como artefato proprio em `.harness/handoff/` |
| 0e3124724ded | "vamos trabalhar em loop até paridade com GUI legado..." | discard-noise | steering de kickoff do loop, nao item isolavel |
| 25a3516a42d8 | "2 opus e 2 codex por iteração, sonnet xhigh p/ testes" | discard-noise | instrucao de alocacao de recursos |
| f4b8d773b806 | Spawn raw: "Read plan-gui-port-board.md and implement..." | discard-noise | comando mecanico de spawn |
| 04e412bd5ac7 | Overseer-loop: instrucao de commit pos gate-staged (it.1) | discard-noise | heartbeat/instrucao de orquestracao, nao item |
| 31c545d2b923 | Spawn raw: "Read plan-gui-port-activity-tail.md and implement..." | discard-noise | comando mecanico de spawn |
| b442ca000668 | Overseer-loop heartbeat (gui-react-parity, it.2) | discard-noise | heartbeat de status, nao item |
| f8ac2160b5e6 | GUI backend gap: Workbench Preview sem endpoint de output renderizado | still-valid-backlog | 1 dos "4 intakes SPEC-116 de backend-gap" registrados em `1acc0f1`; verificado ao vivo: `ui/src` nao tem tela/endpoint de Preview (grep so acha "Terminal-follow" scroll, sem relacao) -- EmptyState gap segue aberto, decisao do owner pendente |
| 0687a668c8e3 | GUI backend gap: Workbench Terminal exigiria exec interativo (conflita SPEC-114) | still-valid-backlog | mesmo lote de 4 intakes `1acc0f1`; decisao de design do owner explicitamente pendente, nenhum commit resolve |
| 7708a32b426d | GUI backend gap: Workbench Artifacts sem fonte de dado | still-valid-backlog | mesmo lote; nenhum verbo novo lista artefatos de sessao/worker no codigo atual |
| 8611d7ae8c57 | GUI backend gap: Activity Releases sem conceito no harness | still-valid-backlog | mesmo lote; harness segue sem conceito de release alem de commits/tags |
| 7b50b3ee2561 | Defeito: /api/state COLD ~11.8s (curl instrumentado) | done-in-git | `1aaf676` onda 1 AFK: "api-state-cold-latency... summarize(include_disk=False)... 531ms→16ms (97%)" -- root-cause era `cost_metrics._dir_mb` (os.walk ~12k arquivos) |
| 9199cf58fc57 | [gov:scenario-hot] pw_ui_smoke subprocess 73s > 45s | done-in-git | resolvido como efeito colateral do fix acima; `4cfa607` confirma explicitamente ("serial-div-pw-incidents RESOLVIDO... pw_ui_smoke ja nao aparece em gate-divergence"); `.harness/runs/gate-perf.jsonl` (5 rodadas mais recentes) mostra first-attempt em ~23-26s, bem abaixo do limite de 45s |
| efa57b02b0ad | GUI-AC3 gap: /api/audit só mostra tail vivo (janela de minutos), não a trilha hash-chained do archive | done-in-git | flagrado como intake em `1acc0f1` ("gap do audit-window achado pelo owner ('so uma?') -> intake + copy fix na polish lane"); fix shipado em `2c42481` ("gui-polish-1... audit window copy"). Nota: resolvido pela opcao (b) minima (copy honesto), NAO pela opcao (a) (endpoint agregando o archive) -- se o owner quer (a), e ask novo |
| 253dba67046b | Overseer-loop: instrucao de commit pos gate-staged (it.2) | discard-noise | heartbeat/instrucao de orquestracao |
| 9424773b48eb | Residual encoding-audit: `run_bounded_command` (spec_test_gate.py) decodifica stdout com cp1252 no Windows | still-valid-backlog (verificado ao vivo) | LI `scripts/spec_test_gate.py:120` agora: `kwargs.setdefault("text", True)` SEM `encoding=` -- bug ainda presente. `1acc0f1` corrigiu 20 OUTROS sites (`processes.run_quiet`/`run_process_tree_bounded`) mas reverteu o hunk deste arquivo especifico por colidir com o ratchet gs-7 ("hunk revertido, residual de forensics-decode vira intake com porta de spec" -- este intake E esse residual) |
| d75adc20c676 | "não aparece nenhum shell ou agente em andamento, esperando algo?" | duplicate-of 5115c47c4941 | mesmo topico (runs detached invisiveis na GUI), levantado ~1h30 antes do intake manual estruturado; sem fix proprio, coberto pela entrada estruturada |
| e7876a0379a8 | Spawn raw: "Read plan-gui-port-code.md and implement..." | discard-noise | comando mecanico de spawn |
| f1650a011189 | [gov:scenario-hot] rt6_route_writechain subprocess 48s > 45s | still-valid-backlog (verificado ao vivo) | `.harness/runs/gate-perf.jsonl` (5 rodadas mais recentes): attempt=parallel de rt6_route_writechain segue em 65-84s (PIOR que o 48s que disparou o flag); nenhum commit cita fix de timing para este cenario (o fix em `ae3e89a` era outro bug -- false-skip do guard, nao duracao) |
| fec6caf9a052 | Spawn raw: "Read plan-gui-port-code.md and implement..." (retry, preconditions verificadas) | discard-noise | comando mecanico de spawn (retry do mesmo plano de e7876a0379a8) |
| 0b91d8abed03 | Confirmado com medição: Chromium 6-conn/host cap + SSE serializa fetches (4116ms vs 824ms) | still-valid-backlog | este intake E o "-> intake SSE" citado como output do proprio polish-lane item7 em `2c42481`; `git log --all --grep=SSE` só acha o commit de DESCOBERTA, nenhum fix de teardown/pooling |
| 5115c47c4941 | GUI Operations gap: gates detached (gate-staged/validate) invisíveis na GUI | still-valid-backlog | verificado ao vivo: `grep -r "gate-staged\|detached" ui/src` = zero resultados; nenhum `gates[]` em `/api/runtime`; item do owner (`detached-gates-GUI-visibility`) segue aberto |
| 850c0fe7bacf | Erro: "bash: tools/agent-sync/py-run.sh: No such file or directory" | done-in-git | `2c42481`: "Guard-layer cwd-robusto (owner report 'py-run.sh not found'): 15 hooks... forma $CLAUDE_PROJECT_DIR absoluta"; commit as 22:32:37, ask as 21:55:19, mesma sessao |
| 245c6eb86982 | Overseer-loop: instrucao de gate final (it.3) | discard-noise | heartbeat/instrucao de orquestracao |
| 6f907190fcd7 | Ask: mecanismos não-prosa (hooks) + implementar "gasômetro" | done-in-git | `64b5ed8` cita literalmente: "MECANISMOS (ordem do owner: 'não pura prosa; hooks e mecanismos')" (cwd_guard.py, spawn_hold_guard.py, gate_staged dirty-guard, cenario hcs) + "GASÔMETRO v1 (SPEC-168, owner refinement ao vivo)" |
| 79c88cbfc042 | Overseer-loop: instrucao de commit final (it.3) | discard-noise | heartbeat/instrucao de orquestracao |
| 30e3eb2692aa | Spawn raw: "Read plan-loop-guards.md and implement..." | discard-noise | comando mecanico de spawn; trabalho landed em `64b5ed8` (mesmo de 6f907190fcd7) |
| 434ad4336180 | "bora flipar, mas antes workers spec-por-spec + confirmação visual" | discard-noise | instrucao de orquestracao para a rodada pre-flip; substancia coberta por `64b5ed8` (4 auditorias) + `2c42481` (polish round), mas a mensagem em si e steering |
| 847f841e5de4 | Overseer-loop: sequência pré-flip (gate acidental em voo) | discard-noise | heartbeat/instrucao de orquestracao |
| f2644195d7dc | Proposta: OS-keyring write-only p/ chaves de vendor | done-in-git | `63db787`: "keys-keyring (opus kept, security-review PASS): SPEC-169... write-only... keyring-first... `keys migrate`... Tela React Keys" |
| 6ab68187a87c | Overseer-loop: commit pós-veredito (pre-flip) | discard-noise | heartbeat/instrucao de orquestracao |
| d490dcd759f8 | "você está no diretório certo? o que você tá fazendo agora?" | discard-noise | pergunta de checagem de sessao, sem ask |
| 8707a8c4db63 | Spawn raw: "Read plan-test-debt-code-extract.md and implement..." | discard-noise | comando mecanico de spawn (trabalho landed em `63db787`, row fechada) |
| 70e7bcab4901 | Spawn raw: "Read plan-ui-e2e-deadlines.md and implement..." | discard-noise | comando mecanico de spawn (trabalho landed em `1aaf676`, ui-e2e-deadline-widening) |
| 1a23ed816882 | Spawn raw: "Read plan-perf-hotspot-watch.md and implement..." | discard-noise | comando mecanico de spawn (trabalho landed em `63db787`, SPEC-109 Phase 2) |
| 429e6f9905f9 | Overseer-loop AFK onda 2: status em-voo + plano de recon | discard-noise | heartbeat/instrucao de orquestracao |
| ec9acfff0911 | reckon-hold fix PARCIAL: ledger-durável reduziu mas não eliminou 100% | duplicate-of 1ce62bb00fd0 | citado nominalmente como resolvido: `1ce62bb00fd0` diz "intakes ec9acfff0911+46f571bd1c69 RESOLVIDOS por este"; causa raiz real fechada em `cfb16da` |
| 6e223a4f4184 | Spawn raw: "Read plan-docs-audit-refs.md and implement..." | discard-noise | comando mecanico de spawn (trabalho landed em `c0bba2f`, docs-audit-refs) |
| 52b08fffd67b | Spawn raw: "Read plan-svc-mcp-wiring.md and implement..." | discard-noise | comando mecanico de spawn (trabalho landed em `c0bba2f` + follow-up `fae00e7`) |
| 46f571bd1c69 | Confirmação: reckon-hold fix INEFICAZ no gate vivo (3/3 integrações) | duplicate-of 1ce62bb00fd0 | mesmo caso; `1ce62bb00fd0` cita nominalmente esta id tambem como resolvida |
| 1ce62bb00fd0 | reckon-hold FECHADO DE VERDADE: causa real era cleanup_test_artifacts apagando o ledger | done-in-git | `cfb16da`: "reckon-hold ROOT-CAUSE real — o gate-runner apagava o próprio ledger de reckon... FIX (1 linha)... PROVA VIVA... sem re-record" -- match exato com o texto do intake |
| efa1d53c9bf4 | "não era pro groom ter rodado no final do afk loop?" | discard-noise | pergunta meta de sessao -- e literalmente o gatilho desta rodada |

## SUMMARY

- **discard-noise**: 30
- **done-in-git**: 10
- **still-valid-backlog**: 8
- **duplicate-of**: 3
- **needs-live-verification**: 0 (os 3 candidatos ambíguos -- 9424773b48eb, f1650a011189, 5115c47c4941 -- foram resolvidos lendo código/telemetria ao vivo em vez de ficarem pendentes)
- **Total**: 51/51

### Apply-list recomendada

**Discard imediato (33 ids)** -- os 30 discard-noise + os 3 duplicate-of (cobertos por outra entrada, nao precisam de decisao propria):
`09de5548ecb4, 1d983501b5a7, 9943b8d73c98, 948c81a2ac6f, df5f5c1e5bbc, b098ff7efade, 0bb45d35f00f, 0e3124724ded, 25a3516a42d8, f4b8d773b806, 04e412bd5ac7, 31c545d2b923, b442ca000668, 253dba67046b, e7876a0379a8, fec6caf9a052, 245c6eb86982, 79c88cbfc042, 30e3eb2692aa, 434ad4336180, 847f841e5de4, 6ab68187a87c, d490dcd759f8, 8707a8c4db63, 70e7bcab4901, 1a23ed816882, 429e6f9905f9, 6e223a4f4184, 52b08fffd67b, efa1d53c9bf4, d75adc20c676, ec9acfff0911, 46f571bd1c69`

**Discard-done, com sha (10 ids)** -- `ac7ae80b3a70`(6710f3d/a9f453d), `bc3e30772c45`(6710f3d), `f99443c2b651`(a9f453d), `7b50b3ee2561`(1aaf676), `9199cf58fc57`(1aaf676/4cfa607), `efa57b02b0ad`(2c42481), `850c0fe7bacf`(2c42481), `6f907190fcd7`(64b5ed8), `f2644195d7dc`(63db787), `1ce62bb00fd0`(cfb16da)

**Manter em backlog / decisão do owner (8 ids)** -- os 4 backend-gaps de Onda 7 (`f8ac2160b5e6`, `0687a668c8e3`, `7708a32b426d`, `8611d7ae8c57`), o residual de encoding real (`9424773b48eb`), o scenario-hot ainda quente (`f1650a011189`), o pool-starvation de SSE (`0b91d8abed03`) e a visibilidade de gates detached na GUI (`5115c47c4941`). Todos ja tem contexto suficiente pra virar `docs/IMPLEMENTATION_BACKLOG.md` rows direto, sem precisar de spec door -- exceto `9424773b48eb`, que ja nomeia a propria porta (ratchet amendment ou refactor net-negativo).

Nenhuma escrita foi feita: fila, `specs/`, `testing/` e arquivos protegidos intocados; zero `git` ops; zero `intake decide`.
