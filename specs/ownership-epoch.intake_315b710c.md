# Intake refinement — ownership epoch geral (door NEW)

SPEC-116 invariant 2 checklist. Seeds SPEC-149 (`specs/40-features/ownership-epoch.md`).

## Request (verbatim)

> Owner 2026-07-18: "faz um loop e implementa todas [as 3 apostas], começando
> da que deixar as próximas mais fáceis" — C3 primeiro (vocabulário de
> identidade que os demais escritores de estado herdam). Origem: artigo §5.7
> (C3) + 4 incidentes 2026-07 de run velho commitando estado; N3 fechou só os
> 2 caminhos COM incidente e descartou honestamente o "epoch geral" por falta
> de identidade compartilhada entre os ledgers.

## Covered-check (which door?)

| Query | Command | Outcome |
|---|---|---|
| records search | `records search ownership epoch fencing` | `[]` |
| doc-find | `doc-find ownership epoch fencing stale run` | nenhum spec; só menções em docs de contexto |

Decision: **NEW** — N3 vive como fixes pontuais (tasks_board pid-lock,
gate-hold live-pid) sem spec própria; nenhum doc define epoch/fencing geral.

## Goal

Todo run que ESCREVE estado canônico carrega uma identidade com epoch
monotônico; um escritor com epoch mais velho que o dono atual do alvo é
recusado (fencing), nunca sobrescreve silenciosamente.

## Scope

In: contador monotônico atômico; emissão no dispatch/workflow-start/loop;
carriage (env + route tuple + eventos); enforcement em 2 alvos com histórico
de incidente (tasks dispatch, workflow_update); advisory observe-first no
restante. Out: fencing por-recurso fino (CRDT/leases do artigo §5.7 — apostas
futuras), rooms interativas (exemption existente), rewrites de ledger
append-only (já seguros por construção).

## Actors & surfaces

- Actors: overseers despachados, supervisor async, route-loop, tasks dispatch.
- Surfaces: internal (harness_lib) + env de spawn. UI surface? **no** → Gherkin opcional.

## Proposed acceptance criteria

- [ ] `next_epoch()` é atômico e estritamente monotônico sob concorrência local.
- [ ] Dispatch detached e workflow start emitem epoch (env + ledger/evento).
- [ ] `tasks_store.set_dispatch` recusa caller com epoch < epoch do card.
- [ ] `workflow_update` recusa caller com epoch < epoch gravado no workflow.
- [ ] Escritor sem epoch (legado) = advisory, nunca hard-fail (migração ratchet).
- [ ] Doctor advisory lista conflitos de epoch observados.

## Risks / blast radius

Falso-positivo de fencing bloqueando run legítimo → escape `--force-epoch`
com registro loud; contador corrompido → fail-open para advisory (nunca
bloquear tudo); arquivos tocados: epoch módulo novo + tasks_store +
workflow_state/lifecycle + cmd_route.

## Open questions for the human

- (nenhuma — ordem e escopo decididos pelo owner no pedido do loop)
