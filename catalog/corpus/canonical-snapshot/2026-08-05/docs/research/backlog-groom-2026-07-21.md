# Backlog groom — fila de intake, 2026-07-21

Rodada queue-slice (playbook `.harness/prompts/backlog-groom-playbook.md` §1,
variante documentada nesta mesma data). Miner Sonnet 5 medium report-only
(draft: `docs/spec-recovery/intake-groom-2026-07-21-DRAFT.md`), auditado e
aplicado pelo overseer Fable. **115 pendentes → 115 decididos, 0 restantes**
(fila zerada; primeira rodada sob o novo passo de wind-down do
overseer-loop-playbook, que esta sessão instalou).

## Totais aplicados (contagem real do ledger; o §1 do miner tinha slip de ±2)

| Decisão | N |
|---|---|
| discard | 74 |
| discard (done, com evidência) | 39 |
| backlog | 2 |
| spec / experiment / keep-pending | 0 |

O único candidato a spec da janela (openai-compat → compat-executor-routing)
já havia sido intakado e decidido na própria sessão (`5fa854d6e56d` → spec,
one-pager `specs/40-features/compat-executor-routing.intake.md`); os 6
pendentes do cluster N são Q&A coberto por ela.

## Auditoria (overseer, obrigatória)

- **Shas de done-claims**: amostra de 10/10 verificada em `git log -1`
  (7a13e21, 4f36439, c085ec1, f48b3df, 539f81f, 8ec7625, 5486d3e, 0129a35,
  84b8d83, c2f6097) — todas existem e batem com a descrição. Zero fabricação.
- **Promoções (o que gera trabalho) lidas na fonte pelo auditor**:
  `QueueTab.tsx:16-36` lido — colunas 100% leitura confirmado;
  `model-routing.json` role plan = fable/xhigh confirmado (lido nesta sessão)
  e a permissão width-1 do SPEC-153 confirmada na intake do spawn-economy.
- **Correção de aritmética**: subtotais do miner (60/51) não fechavam com o
  ledger 115/115; contagem real 74/39/2 aplicada.

## Promoções → rows criadas em docs/IMPLEMENTATION_BACKLOG.md

1. `gui-queue-job-remove` (intake 11d53f79b03e) — QueueTab sem ação de
   remoção/cancel; resolve o pendente deliberado do round 07-18 (confirmado
   real, não fixado). S/P2.
2. `spawn-plan-profile-guard` (intake bd7bedd5cdff) — `workflow run` perfil
   `plan` sem `--executor` cai em fable·xhigh width-1, silencioso sob
   SPEC-153. S/P2.

O segundo pendente deliberado do round 07-18 (`c1eb5b0da00c`, screenshot no
chat legado) foi descartado como MOOT — o componente foi substituído pelo
Workbench React e nenhum renderer de anexo existe em `ui/src`. Nota honesta
do miner mantida: se anexos de imagem forem desejados no Workbench novo, é
ask NOVO.

## Errata / limites

- Cluster K (Q&A inline, 28 itens): evidência indireta por natureza (a
  resposta vive na conversa, não no repo) — descartados por precedente do
  round 07-18, não por leitura de transcript.
- 3 itens (39b84a5f1d3c, fe533e4acf8a, 7bacd7849e28) casados com
  `event-log-integrity-under-compaction.md` por janela de timestamp +
  conteúdo; correspondência exata pergunta→doc marcada `inferred` pelo miner.

## Mudança duradoura instalada nesta mesma sessão

- `overseer-loop-playbook.md` (wind-down): passo INTAKE-QUEUE GROOM — todo
  fechamento de loop roda a rodada queue-slice; "a loop never closes leaving
  the queue un-groomed".
- `backlog-groom-playbook.md`: cadência + template da variante queue-slice.

Custo da rodada: 1 miner Sonnet medium ≈ 98k tokens / 42 tool uses / ~8min;
auditoria + apply do overseer ≈ 15 min.
