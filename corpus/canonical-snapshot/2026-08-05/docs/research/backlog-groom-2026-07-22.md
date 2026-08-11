# Backlog groom — fila de intake, wind-down do loop-6h, 2026-07-22

Rodada queue-slice do wind-down (o passo obrigatório instalado em
2026-07-21 no overseer-loop-playbook). Miner Sonnet medium report-only
(draft `docs/spec-recovery/intake-groom-2026-07-22-DRAFT.md`), auditado e
aplicado pelo overseer. **16 pendentes → 16 decididos, 0 restantes.**

| Decisão | N |
|---|---|
| discard (steering/heartbeat/packets/ping) | 12 |
| discard (done, sha citado) | 4 |
| promoções | 0 |

Todos os 16 eram fragmentos do próprio loop (capturas do hook sobre
steering, heartbeats e pacotes de execução) ou um ping de tracker já coberto
pela row `copy-env-flake-hunter`. Nenhum ask de feature novo — o backlog do
loop foi lançado diretamente nas rows durante a execução, não via fila.

Auditoria: os 4 done-shas são os próprios commits do loop
(ddd3390..5248a3f, 3125936/90920ea/6e08b83) — verificação trivial.
Custo: miner 41k tokens / ~3min.
