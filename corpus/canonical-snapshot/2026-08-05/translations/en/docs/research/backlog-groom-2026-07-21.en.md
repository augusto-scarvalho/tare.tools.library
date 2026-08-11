# Backlog groom — intake queue, 2026-07-21

Queue-slice round (playbook `.harness/prompts/backlog-groom-playbook.md` §1,
variant documented on this same date). Sonnet 5 medium report-only miner
(draft: `docs/spec-recovery/intake-groom-2026-07-21-DRAFT.md`), audited and
applied by the Fable overseer. **115 pending → 115 decided, 0 remaining**
(queue cleared; first round under the new wind-down step of the
overseeer-loop-playbook installed by this session).

## Applied totals (actual ledger count; miner §1 had a ±2 slip)

| Decision | N |
|---|---|
| discard | 74 |
| discard (done, with evidence) | 39 |
| backlog | 2 |
| spec / experiment / keep-pending | 0 |

The only spec candidate in the window (openai-compat → compat-executor-routing)
had already been ingested and decided in the same session (`5fa854d6e56d` →
spec, one-pager `specs/40-features/compat-executor-routing.intake.md`); the 6
pending items in cluster N are Q&A covered by it.

## Audit (overseer, mandatory)

- **Done-claim shas**: 10/10 sample verified with `git log -1`
  (7a13e21, 4f36439, c085ec1, f48b3df, 539f81f, 8ec7625, 5486d3e, 0129a35,
  84b8d83, c2f6097) — all exist and match the description. Zero fabrication.
- **Promotions (items that create work) read at source by the auditor**:
  `QueueTab.tsx:16-36` read — columns confirmed 100% read-only;
  `model-routing.json` role plan = fable/xhigh confirmed (read in this session)
  and SPEC-153 width-1 permission confirmed in the spawn-economy intake.
- **Arithmetic correction**: miner subtotals (60/51) did not close against the
  115/115 ledger; actual count 74/39/2 applied.

## Promotions → rows created in docs/IMPLEMENTATION_BACKLOG.md

1. `gui-queue-job-remove` (intake 11d53f79b03e) — QueueTab has no remove/cancel
   action; resolves the deliberately pending item from round 07-18 (confirmed
   real, not fixed). S/P2.
2. `spawn-plan-profile-guard` (intake bd7bedd5cdff) — `workflow run` with
   profile `plan` and no `--executor` falls into fable·xhigh width-1, silently
   under SPEC-153. S/P2.

The second deliberately pending item from round 07-18 (`c1eb5b0da00c`,
screenshot in legacy chat) was discarded as MOOT — the component was replaced
by React Workbench and no attachment renderer exists in `ui/src`. The miner's
honest note is preserved: if image attachments are desired in the new
Workbench, that is a NEW ask.

## Errata / limits

- Cluster K (inline Q&A, 28 items): evidence is indirect by nature (the answer
  lives in the conversation, not the repo) — discarded by precedent from round
  07-18, not by transcript reading.
- 3 items (39b84a5f1d3c, fe533e4acf8a, 7bacd7849e28) matched to
  `event-log-integrity-under-compaction.md` by timestamp window + content; exact
  question→doc correspondence was marked `inferred` by the miner.

## Durable change installed in this same session

- `overseer-loop-playbook.md` (wind-down): INTAKE-QUEUE GROOM step — every loop
  closeout runs the queue-slice round; "a loop never closes leaving the queue
  un-groomed".
- `backlog-groom-playbook.md`: cadence + template for the queue-slice variant.

Round cost: 1 Sonnet medium miner ≈ 98k tokens / 42 tool uses / ~8 min;
overseeer audit + apply ≈ 15 min.
