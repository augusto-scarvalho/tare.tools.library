# SPEC-149 — Ownership epoch (fencing geral de escritores de estado)

Status: SPEC-149, proposed 2026-07-18 (acceptance: `testing/scenarios/oe_ownership_epoch.py`).
Intake: `specs/40-features/ownership-epoch.intake.md`. Artigo §5.7 (C3);
incidentes 2026-07 (4); N3 (fba2fe2-era) fechou os 2 caminhos com incidente.

## Goal

Um run velho nunca commita estado por cima de um dono mais novo. Todo run
escritor carrega `{runId, epoch}` de um contador monotônico único; alvos
contestados gravam o epoch do dono e recusam escritores com epoch menor
(fencing token, artigo §5.7). Migração é ratchet: escritores legados sem
epoch geram advisory, não quebra.

## Applicability

Runs autônomos que escrevem estado canônico: overseers despachados
(`cmd_route`), workflows (start/update), iterações do route-loop, dispatch de
task cards. Não cobre: rooms interativas (exemption SPEC-148), ledgers
append-only (event log, route-ledger — seguros por construção), fencing
por-recurso fino (aposta futura §5.7 CRDT/leases).

## Requirements / invariants (numbered, testable)

1. **Contador atômico monotônico.** `epoch.next_epoch(root)` incrementa
   `.harness/state/epoch.json` via temp+`os.replace` com verificação
   read-back; concorrência local nunca produz epoch duplicado nem regressão.
2. **Emissão no nascimento do run.** Dispatch detached e workflow start
   adquirem epoch e o CARREGAM: env `HARNESS_RUN_EPOCH`, campo `epoch` no
   route-ledger row `dispatched` e no route tuple (C13), evento de start.
3. **Fencing nos alvos com histórico.** `tasks_store.set_dispatch` grava
   `dispatchEpoch` e recusa caller com epoch menor que o gravado;
   `workflow_update` grava `ownerEpoch` no workflow.json e recusa caller de
   epoch menor. Recusa é legível e nomeia o escape.
4. **Escape loud.** `--force-epoch`/kwarg `force_epoch=True` sobrepõe UMA
   recusa com registro no event log (`epoch_fence_overridden`), nunca
   silencioso.
5. **Legado = advisory (ratchet).** Escritor SEM epoch no env não é
   bloqueado; o alvo registra `epochMissing` e o doctor advisory
   (`epoch-conflicts`) lista misses + conflitos observados. Enforcement
   hard-fail só existe onde o epoch dos DOIS lados é conhecido.
6. **Corrupção fail-open-para-advisory.** `epoch.json` ilegível → next_epoch
   reinicia de max(observados)+1 quando derivável, senão timestamp-epoch;
   fencing degrada para advisory naquele run; nunca um deadlock global.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Epoch monotônico como fencing token | Artigo §5.7 (A: leases/fencing, Gray); C3 da matriz de evidências |
| Enforcement só nos alvos com incidente; resto advisory | 4 incidentes 2026-07 (dispatch duplicado a6c9af5, gate-hold, rota inline, dispatch Start morto); disciplina observe-first D008; precedente ratchet SEC.5 |
| Contador único global (não por-subject) | Ponytail: fencing exige só ordem total local; por-subject = complexidade sem incidente que a exija (upgrade path registrado) |
| Escape loud único | Padrão HARNESS_SANDBOX_OVERRIDE (SPEC-148 regra 4) |
| Carriage no route tuple | C13/L9 (bb327dc): a tupla é o registro canônico de identidade do run |

## Ceilings (upgrade paths)

- Contador global, não per-task lease com expiry — upgrade quando houver
  incidente de starvation/contention entre subjects.
- Fencing em 2 alvos; workflow_state/records/experiments ficam advisory —
  promover alvo a hard-fail exige incidente ou decisão owner.
- Sem distribuição (single-host); multi-host = redesign com store real.

## Test strategy

- Behaviors: monotonicidade sob threads concorrentes; recusa de epoch menor
  nos 2 alvos; escape loud registra evento; legado sem epoch passa com
  advisory; corrupção degrada sem travar.
- Edge: epoch.json ausente (primeiro uso); dois next_epoch simultâneos.
- Regression: tb-6 (pid-lock continua), rt/rl/rh/hsb intactos.
- Coverage impact: enforced.

## Validation

- `python testing/scenarios/oe_ownership_epoch.py` (oe-1 contador, oe-2
  fencing tasks, oe-3 fencing workflow, oe-4 escape+advisory+corrupção).
- `python scripts/harness_lib/epoch.py` self-check.
- Cenários vizinhos verdes: tb_tasks_board, rt_route_dispatcher,
  rl_route_ledger, srg_spawn_ratchet.

## Amendments

(none yet)
