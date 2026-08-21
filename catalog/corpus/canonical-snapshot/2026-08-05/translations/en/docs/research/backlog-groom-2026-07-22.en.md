# Backlog groom — intake queue, loop-6h wind-down, 2026-07-22

Queue-slice round during wind-down (the mandatory step installed on
2026-07-21 in `overseer-loop-playbook`). Sonnet medium report-only miner
(draft `docs/spec-recovery/intake-groom-2026-07-22-DRAFT.md`), audited and
applied by the overseer. **16 pending → 16 decided, 0 remaining.**

| Decision | N |
|---|---|
| discard (steering/heartbeat/packets/ping) | 12 |
| discard (done, cited sha) | 4 |
| promotions | 0 |

All 16 were fragments of the loop itself (hook captures over steering,
heartbeats, and execution packets) or a tracker ping already covered by the
`copy-env-flake-hunter` row. There were no new feature asks — the loop backlog
was written directly into rows during execution, not through the queue.

Audit: the 4 done-shas are the loop's own commits
(ddd3390..5248a3f, 3125936/90920ea/6e08b83) — trivial verification.
Cost: miner 41k tokens / ~3 min.
