# Backlog groom — 2026-07-29 (queue slice, wind-down do loop AFK)

Rodada queue-slice do playbook de groom (§1 miner → §2 audit → apply), executada
no wind-down do overseer-loop AFK de 2026-07-28→29. Fila de entrada: **364
pendentes** (reacumulados desde a rodada de 2026-07-22). Miner: 1× Sonnet
report-only (~160k tokens, 35 tool uses); ledger completo em anexo de sessão
(scratchpad `groom-ledger.md`; clusters e top-10 reproduzidos abaixo).

## Auditoria (§2, obrigatória) — VEREDITO: aplicável

- **Citações de shas**: 28/28 commits citados existem e os subjects casam com
  os claims (verificados um a um via `git log -1`). Zero fabricação.
- **CL23 (o maior lote de discard, ~85 entradas)**: as duas falas do dono que
  autorizam o descarte são VERBATIM nas entradas citadas
  (`caf64c195108` "isso é um side project que não tem nada a ver com o
  harness"; `1f151af60c68` "pode criar em uma pasta fora daqui, é side
  project"). Cluster = bancada de LLM local no desktop, fora do escopo do repo.
- **Claims que geram trabalho** (top-3): âncoras reais conferidas —
  rule-6 (`harness.py:1447/1775, async_state.py:362, chat_setup.py:128`),
  hold-swap deny (3 incidentes nomeados em 2026-07-23), ACCESS-CLASS
  (`result_contracts.validate_worker_result:321-322`).
- Perfil de erro esperado (existência ~100%, live-behavior ~75%) respeitado:
  linhas com claim de comportamento vivo NÃO auditável ficaram `keep-pending`
  por decisão do orquestrador (autoscroll CL10, tile GLM, wave-2 do diet CL28).

## Aplicação

**307 decisões aplicadas, 0 falhas**: 278 `discard` (ruído conversacional,
packets mecânicos de WF, side-project CL23, boilerplate de resume), 26
`backlog`, 3 `spec`. **57 seguem pendentes DELIBERADAMENTE** (keep-pending:
verificação viva ou decisão do dono — nunca por omissão).

## Top-10 para o dono (triagem §3 é SUA, com o orquestrador)

1. **SPEC-170 rule-6**: 4 spawn builders sem `enforce_spawn()` — gap citado.
2. **Deny `.harness/` writes com gate-hold ocupado** — classe de perda de dado
   3x num dia; o próprio loop desta noite re-mediu a classe (leitura de intake
   mascarada pelo hold da sonda serial).
3. **ACCESS-CLASS no worker-result** — workers packet-only estruturalmente
   reprovados por `sourceFilesVerified`; onda inteira descartada.
4. **Worker permission tier** — intake spec já aberto; falta ratificar.
5. **Precedência de routing do overseer** — checagem viva de 1 turno.
6. **Ledger de disparidade vendor/OS** (evoluir cada vendor, não achatar).
7. **local-model-config** — DRAFT + READY existem; falta sua ratificação.
8. **Backlog GUI undercounting** — repro vivo rápido.
9. **Aposentar GUI legacy** — gate "polish da nova terminou?" é seu.
10. **Auto-allowlist de hooks próprios** — você já convergiu no design.

Rows de backlog para os 26 `backlog`-decididos: NÃO criadas nesta rodada — a
§3 manda a triagem ser conjunta (dono + orquestrador); os títulos propostos
pelo miner estão no ledger, prontos para `tasks add` na sua volta.

## Clusters (40, resumo)

Entregues/discard-done com sha: worker-result pipeline (9ae4f91), ide-shard
W1-W3 (00312f2/ac5517d/01be458), gas-balancer/fuel (512a68a/6afb0eb), FormDialog
(32b320f), .env→vault (a151cc2), kimi (13a31f4..f5c9aa4), react-smoke (0572c18),
sandbox chokepoint (8206fe9), graph async (10894d3/f9e8f40), compaction research
(c2f6097), chat chips (802cd8b), ambient-core (6975fc0), context diet (3350ae5).
Ruído: filler conversacional (~40), packets WF mecânicos (32), side-project
(~85), resume/checkpoint boilerplate (~19), probes one-shot (~20).

Proveniência: miner Sonnet queue-slice (report-only, leitura via TSV do JSON —
a própria ideia `CL-jsontsv` da fila, usada antes de ser aprovada); auditoria e
aplicação pelo overseer (Fable). Próxima rodada nunca re-minera este chão:
este arquivo é o CLOSED log da fatia.
