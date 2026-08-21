> MINER LEDGER — PENDING OVERSEER AUDIT (playbook §2) — NON-CANONICAL until
> applied via `intake decide`. Report-only: no intake decisions were made, no
> files outside this report were touched.
>
> **Postscript (20:48-03:00, after this ledger was written)**: the in-flight
> `validate --staged` gate (pid 8432, hold `20260722T232457Z-8432`) this
> report read its snapshot from finished with **status: fail** (2 scenario
> checks: `m4_status_html` empty:seeds-gone, `pw_ui_smoke` incidents-drill;
> + 1 release-hygiene:generated-artifacts on `.harness/runs/events.jsonl` —
> out of scope for this report, belongs to the session that owns the gate).
> Its own `rule_scenario_hot` governance check raised ONE new pending entry
> AFTER this ledger's 27/27 was written: `f1650a011189`
> `[gov:scenario-hot:rt6_route_writechain]` (48s > 45s), asked 20:47:51 —
> same cluster V treatment as `9199cf58fc57` above (auto-reincident tracker
> artifact, `discard`). Live queue is now 28 pending; this ledger covers
> 27/28 (all but the one that arrived after submission).

# Intake groom — fila de intake, 2026-07-22 (wind-down, sessão 1 do loop)

Rodada queue-slice (playbook `.harness/prompts/backlog-groom-playbook.md`
§1). Miner Sonnet 5, report-only. Terceira janela do dia — as duas
anteriores fecharam a fila em zero (`docs/research/backlog-groom-2026-07-22.md`
16→0 às ~06:00 loop-6h; `docs/research/backlog-groom-2026-07-22b.md` 8→0 às
~10:02); esta janela cobre a exaustão da sessão `gui-react-parity` que
seguiu (11:51–20:24), a mesma referida no checkpoint
`.harness/context/NEXT_STEPS.md` ("SONNET groom-miner report-only (26
intakes pendentes...)" — a fila real tinha 27 no momento da leitura, off-by-
one esperado pela janela de segundos entre a nota do checkpoint e a captura
do gate-hold).

**Nota de vocabulário**: o prompt desta tarefa pediu os rótulos
`done-in-git / duplicate / still-valid / needs-live-verification / stale`,
mas o contrato real do playbook §1 (variante queue-slice) define
`discard / discard (done, com sha) / backlog / spec / experiment /
keep-pending`. Segui o contrato real do playbook (instrução explícita: "read
... and follow its ledger contract"), não o rótulo do prompt. Mapeamento
aproximado para quem espera o outro vocabulário: `done-in-git` ≈ `discard
(done)`; `duplicate` ≈ `discard` (dump de estado / instrução repetida);
`still-valid` ≈ `backlog`; `needs-live-verification` — verifiquei ao vivo
TODOS os candidatos a `backlog` desta rodada (leitura de código-fonte atual,
não apenas grep de existência), então nenhum item ficou nessa categoria sem
resolução; `stale` não se aplicou (nenhum pendente teve idade > 7 dias — a
janela inteira é de hoje).

**Nota de acesso**: `.harness/state/intake-queue.json` não existe na raiz no
momento desta leitura — há um gate-hold EM CURSO (pid 8432 vivo, confirmado
via `tasklist`), criado `20260722T232457Z` (`.harness/runs/gate-hold/20260722T232457Z-8432/hold.json`).
Li a cópia live da fila dentro do snapshot do hold
(`.harness/runs/gate-hold/20260722T232457Z-8432/e0/intake-queue.json`),
somente leitura — nenhuma escrita em `.harness/`, nenhuma operação de git,
nenhum `intake decide`.

## 1. Totais

- Pending (fila live sob o gate-hold em curso): **27** (na leitura original;
  ver postscript acima — subiu para 28 depois do gate terminar, o 28º item
  está listado em §3 mas fora da contagem original desta seção)
- Proposto:
  - discard: 20 (+1 pós-postscript = 21)
    - dos quais **discard (done, com sha/evidência)**: 9
    - dos quais discard simples (Q&A/steering/heartbeat/tracker-artifact,
      sem ask persistente): 11 (+1 pós-postscript)
  - backlog (candidatos ainda abertos, verificados ao vivo): **7**
  - spec / experiment / keep-pending: 0

(20 + 7 = 27; +1 pós-postscript = 28.)

## 2. Cluster table

| Cluster | N | Decisão dominante |
|---|---|---|
| Q. Q&A/steering pontual sem ask persistente | 4 | discard |
| W. Texto de brief de worker colado pelo hook (não é ask do owner) | 4 | discard |
| H. Heartbeat/dump de estado do próprio loop | 3 | 2 discard (done, executado em minutos) · 1 discard (dump) |
| T. Política TSV boundary + pedido de hook/guard | 3 | discard (done) — `a9f453d` + `6710f3d` |
| R. Q&A reckon skips↔reach | 1 | discard (done) — `aa6c285`/`8cd4198` |
| D. Diretrizes de distribuição de modelo (codex/opus) | 3 | discard (done/codificado) — `1acc0f1`, `1b2941b`, checkpoint trail |
| G. Gatilho da queixa "GUI incompleta" (remediation loop) | 1 | discard (steering; loop EM VOO, não é ask novo) |
| B. Gaps honestos de backend do Workbench (Preview/Terminal/Artifacts/Releases) | 4 | **backlog** (4×, verificados ao vivo) |
| P. Defeito de performance /api/state COLD | 1 | **backlog** |
| A. Gap do Audit trail (arquivo rotacionado fora da janela) | 1 | **backlog** |
| E. Resíduo do encoding-audit (cp1252 sem `encoding=`) | 1 | **backlog** |

## 3. Ledger por entrada (27/27)

09de5548ecb4 | Q | discard | 11:51 "esse negócio do subprocessedges pode rodar enquanto a gente trabalha?" — pergunta pontual sobre concorrência de trabalho em voo | Q&A inline, sem ask persistente

1d983501b5a7 | Q | discard | 11:53 "a gente não estava processando o ast então?" — pergunta sobre capacidade já existente (Graphify AST) | Q&A inline

ac7ae80b3a70 | T | discard (done) | 12:29 política TSV-para-tráfego-de-agente/JSON-para-comunicação-interna — `a9f453d` (13:38) "feat(harness): TSV boundary P1 — findings/reviewFindings aceitam TSV table string", corpo cita "fecha a matriz 4 pernas: P3 emit / P4 scrub (`6710f3d`) / P2 contrato / P1 este commit" | política shipped no mesmo dia, minutos depois

bc3e30772c45 | T | discard (done) | 12:33 elaboração do fluxo TSV (mesmo cluster) — mesmo cite `a9f453d`/`6710f3d` | detalhe da mesma política, mesma entrega

f99443c2b651 | T | discard (done) | 12:36 "precisa criação de algum hook ou estrutura pra garantir esse tráfego e parsing de tsv? faz isso pra gente em seguida" — `a9f453d` adiciona `common.tsv_table` como adapter de ingestão ANTES do schema-check em `WORKER_RESULT.findings`/`REVIEWER_RESULT.reviewFindings` (a "estrutura" pedida) | ask literal atendido no mesmo commit, 62min depois

9943b8d73c98 | R | discard (done) | 14:41 "os skips também servem para o reckon entender onde não olhar?" — `aa6c285` (14:51) corpo: "raio do surface staged pelo MESMO mapa gate_affected dos skips" — resposta é SIM, confirmada pelo próprio texto do commit shipado 10min depois | Q&A respondida por feature real

948c81a2ac6f | Q | discard | 14:44 "que tal priorizar agora? ou temos impedimento?" | steering/Q&A, sem ask isolável

df5f5c1e5bbc | G | discard | 17:37 "você disse que terminou as tarefas do front end, mas abri aqui e não tem várias páginas... cadê o resto da GUI nova?" — gatilho do remediation loop; `1b2941b` (18:56) "iteracao 1 do remediation loop — 5 lanes React (fixes D1-D12...)" e `1acc0f1` (20:23) iteração 2; checkpoint `.harness/context/NEXT_STEPS.md` (linha "In-flight checkpoint", não commitado) registra "EM VOO iteracao 3" no momento desta leitura | ask real, PARCIALMENTE endereçado — loop segue aberto (não é "done", é o driver da sessão inteira já rastreado no checkpoint; não precisa de row nova de backlog)

b098ff7efade | D | discard (done) | 18:05 "vai colocando o codex pra programar também, gpt 5.6 sol high" — `1acc0f1` corpo: "gui-port-activity-tail (codex gpt-5.6-sol, kept, 240994tk)" | lane codex rodando no mesmo dia

0bb45d35f00f | W | discard | 18:07 texto integral de brief de worker ("Read .harness/handoff/plan-gui-port-research.md and implement EXACTLY...") capturado verbatim pelo hook — não é ask do owner, é o prompt que o overseer deu a um subagente (o filtro do hook só bloqueia payload que começa com `<`) | ruído de captura, precedente cluster A/K das rodadas anteriores

0e3124724ded | D | discard (done) | 18:09 "vamos trabalhar em loop até finalizar a paridade... Vai adicionando o Codex no loop como implementer também" — codificado no checkpoint `NEXT_STEPS.md` ("ORDENS PERMANENTES") e executado nos commits `1b2941b`/`1acc0f1` (lanes mistas opus+codex) | diretriz em execução ativa

25a3516a42d8 | D | discard (done) | 18:16 "2 opus e 2 codex por iteração... quem for construir os testes de GUI, pode ser sonnet 5 xhigh" — `1acc0f1` corpo: "gui-tests-interactions (sonnet xhigh, kept, 324944tk)" | mix de modelo aplicado literalmente no mesmo commit

f4b8d773b806 | W | discard | 18:19 texto integral de brief ("Read .harness/handoff/plan-gui-port-board.md and implement EXACTLY...") | mesmo ruído de captura de W

04e412bd5ac7 | H | discard (done) | 18:55 heartbeat "o gate-staged detached (marker ...20260722T184539.marker) deve ter concluído — leia... Se PASS: ... commit do lote das 5 lanes" — `1b2941b` commitado às 18:56:02, 1 minuto depois, mensagem bate com a descrição (5 lanes, D1-D12) | nota do próprio loop, executada no minuto seguinte

31c545d2b923 | W | discard | 18:58 texto integral de brief ("Read .harness/handoff/plan-gui-port-activity-tail.md and implement EXACTLY...") | mesmo ruído de captura de W

b442ca000668 | H | discard | 19:24 heartbeat descritivo ("Overseer-loop heartbeat... Lanes em voo: gui-port-activity-tail (codex)...") truncado em 400 char pelo próprio ASK_CAP | dump de estado, sem ask isolável

f8ac2160b5e6 | B | **backlog** | 19:24 (source=manual) "Workbench Preview precisa de endpoint que sirva output renderizado do app-alvo (nenhum /api/* existe); sem fonte a secao fica EmptyState honesto" — verificado AO VIVO: `ui/src/domains/workbench/WorkbenchScreen.tsx:126` renderiza `<EmptyState ... hint="Nativizes in a later Workbench slice." />` para qualquer `route.section` fora de `conversation`/`changes`; grep por `/api/` relacionado a preview/render = 0 hits | gap real, confirmado no código atual, nenhuma row em `docs/IMPLEMENTATION_BACKLOG.md` cobre isso

0687a668c8e3 | B | **backlog** | 19:24 (source=manual) "Workbench Terminal exigiria canal de exec interativo — conflita com GUI-writes-no-state (SPEC-114); decisao de design do owner antes de qualquer endpoint" | mesma verificação de `WorkbenchScreen.tsx:126` acima (Terminal cai no mesmo EmptyState genérico); decisão de design explicitamente pendente do owner, sem row no backlog

7708a32b426d | B | **backlog** | 19:24 (source=manual) "Workbench Artifacts sem fonte de dado... candidato: derivar de .harness/runs + evidence" | mesma verificação; sem row no backlog

8611d7ae8c57 | B | **backlog** | 19:24 (source=manual) "Activity Releases sem fonte... decidir se a secao morre ou ganha verbo" | mesma verificação (seção Releases não existe em `ui/src/domains/activity`); sem row no backlog

7b50b3ee2561 | P | **backlog** | 19:57 (source=manual) "Backend defect (medido 2026-07-22): /api/state COLD leva ~11.8s... quente 293ms... investigar state_snapshot (perfil + cache incremental por fonte, SPEC-133 adjacente)" — grep em `docs/IMPLEMENTATION_BACKLOG.md` por `state_snapshot`/`api/state` = 0 hits | defeito medido e citado com números concretos, nenhuma row cobre; candidato de perf real

9199cf58fc57 | V | discard | 20:06 `[gov:scenario-hot:pw_ui_smoke] Cenario pw_ui_smoke: subprocess 73s > 45s` — auto-gerado por `gate_governance.rule_scenario_hot` (`scripts/harness_lib/gate_governance.py:64,119-120`), com cooldown próprio (`_blocked_by_queue`); precedente cluster G das rodadas 07-18/07-21 trata esses pings como artefato de tracker auto-reincidente, não como ask nova | nenhuma row específica de `pw_ui_smoke` existe no backlog ainda, mas o mecanismo se re-levanta sozinho quando a condição persistir — não precisa de row de intake dedicada

efa57b02b0ad | A | **backlog** | 20:12 (source=manual) "GUI-AC3 gap descoberto pelo owner ('so uma?'): /api/audit le so o events.jsonl VIVO, que rotaciona pro archive/... Audit screen mostra janela de minutos (1 evento) em vez da trilha hash-chained rica" — verificado AO VIVO em `scripts/harness_ui.py:546-569` (`_events_raw` lê só `.harness/runs/events.jsonl`, sem merge de `archive/`); `012c7e7` (16:55, ANTES deste ask) e `1acc0f1` (20:23, DEPOIS) tocam AC3/AC4 mas nenhum dos dois altera `_events_raw` | gap confirmado ainda aberto no código atual, pós as duas entregas de Activity do dia; precisa de decisão de design (endpoint agrega archive, ou copy honesto na tela)

253dba67046b | H | discard (done) | 20:13 heartbeat "gate-staged da iteração 2 detached (marker ...20260722T200202.marker)... Commitar o lote da iteração 2" — `1acc0f1` commitado às 20:23:09, ~10min depois, mensagem bate (act-tail codex, encoding-audit, tests-interactions) | nota do loop, executada minutos depois

9424773b48eb | E | **backlog** | 20:14 (source=manual) "Residual do encoding-audit: run_bounded_command (spec_test_gate.py) decodifica stdout de cenario com cp1252 no Windows (text=True sem encoding)... Fix de 3 linhas colide com o ratchet gs-7 (<1660 linhas)" — verificado AO VIVO: `scripts/spec_test_gate.py:120` `kwargs.setdefault("text", True)` sem `encoding=`; `testing/scenarios/gs_gate_structure.py:60` `PRE_MOVE_LINES_R3 = 1660`; `wc -l scripts/spec_test_gate.py` = **1659** (1 linha de folga — confirma o footgun descrito) | defeito e ratchet ambos confirmados no código atual, sem row no backlog

d75adc20c676 | Q | discard | 20:22 "aqui na interface não aparece nenhum shell ou agente em andamento, você está esperando algo mesmo?" — pergunta sobre estado do processo no momento, não pedido de feature de GUI | Q&A inline

e7876a0379a8 | W | discard | 20:24 texto integral de brief ("Read .harness/handoff/plan-gui-port-code.md and implement EXACTLY...") | mesmo ruído de captura de W; última entrada antes do gate-hold (20:24:57)

f1650a011189 | V | discard | 20:47 (source=governance, chegou APÓS a leitura original desta ledger — ver postscript) `[gov:scenario-hot:rt6_route_writechain] Cenario rt6_route_writechain: subprocess 48s > 45s na ultima rodada` — auto-gerado pelo mesmo `gate_governance.rule_scenario_hot` do item `9199cf58fc57`, produzido pelo PRÓPRIO gate que acabou de rodar (pid 8432, status fail) | mesmo tratamento de cluster V: artefato de tracker auto-reincidente, sem row de intake dedicada

## 4. Ranked top candidates para o owner (7 backlog)

1. **f8ac2160b5e6 / 0687a668c8e3 / 7708a32b426d / 8611d7ae8c57 — Workbench/Activity
   gaps honestos (Preview, Terminal, Artifacts, Releases).** As 4 seções
   caem no mesmo `EmptyState` genérico (`WorkbenchScreen.tsx:126`); cada
   uma precisa de UMA decisão de design distinta do owner antes de qualquer
   endpoint (Terminal em particular esbarra em SPEC-114 GUI-writes-no-state).
   Já aparecem citadas como "Onda 7" no checkpoint do loop, mas sem row
   formal em `docs/IMPLEMENTATION_BACKLOG.md` — candidatas a 1 row
   consolidada com 4 sub-decisões, ou 4 rows independentes.
2. **7b50b3ee2561 — /api/state COLD ~11.8s.** Defeito de performance medido
   com números concretos (293ms quente vs 11.8s frio); relacionado a
   SPEC-133; sem row no backlog.
3. **efa57b02b0ad — Audit trail só vê a janela viva.** Gap confirmado no
   código atual mesmo após as duas entregas de Activity do dia; precisa de
   decisão (endpoint agrega archive vs copy honesto).
4. **9424773b48eb — encoding cp1252 no `run_bounded_command`.** Fix de 3
   linhas, mas colide com o ratchet gs-7 (1659/1660 linhas, sem folga);
   precisa de porta (spec-door amendment do ratchet, ou refactor
   net-negativo que financie as linhas).

## 5. Errata honesta

- Os clusters Q/W/H (11 itens) não têm sha de resposta recuperável — são
  Q&A/steering/heartbeat/texto-de-brief que evaporam da conversa; marcados
  `discard` por classificação de forma (mesmo precedente das rodadas
  07-18/07-21/07-22b), não por leitura de transcript de sessão (sem acesso).
- `df5f5c1e5bbc` (queixa "cadê o resto da GUI") é o único item onde
  "discard" é uma simplificação: o ask é REAL e só parcialmente atendido (o
  loop de remediação segue `EM VOO` na iteração 3 no momento desta leitura).
  Não virou `backlog` porque já é o driver rastreado do checkpoint vivo, não
  um item novo — mas o próximo overseer deve confirmar que a iteração 3
  fecha o gap antes de tratar este pendente como resolvido.
- `9199cf58fc57` (gov:scenario-hot pw_ui_smoke) ficou `discard` por
  precedente (artefato de tracker auto-reincidente), não porque o problema
  esteja resolvido — se 73s persistir, o próprio `gate_governance` vai
  relevantar.
- Não toquei `.harness/state/intake-queue.json` nem a cópia sob
  `.harness/runs/gate-hold/` (somente leitura), nem `specs/`, `testing/`,
  arquivos protegidos. Nenhum `intake decide`, nenhuma operação de git.
