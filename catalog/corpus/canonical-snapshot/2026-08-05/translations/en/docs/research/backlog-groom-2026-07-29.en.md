# Backlog groom — 2026-07-29 (queue slice, AFK loop wind-down)

Queue-slice round of the groom playbook (§1 miner → §2 audit → apply), executed
during the 2026-07-28→29 AFK overseer-loop wind-down. Input queue: **364
pending** (reaccumulated since the 2026-07-22 round). Miner: 1× Sonnet
report-only (~160k tokens, 35 tool uses); complete ledger attached to the
session (scratchpad `groom-ledger.md`; clusters and top-10 reproduced below).

## Audit (§2, mandatory) — VERDICT: applicable

- **SHA citations**: 28/28 cited commits exist and subjects match the claims
  (checked one by one via `git log -1`). Zero fabrication.
- **CL23 (largest discard batch, ~85 entries)**: the two owner statements that
  authorize discard are VERBATIM in the cited entries (`caf64c195108` "this is
  a side project that has nothing to do with the harness"; `1f151af60c68`
  "you can create it in a folder outside here, it is a side project"). Cluster
  = local LLM desktop bench, outside repo scope.
- **Claims that create work** (top-3): real anchors checked — rule-6
  (`harness.py:1447/1775, async_state.py:362, chat_setup.py:128`), hold-swap deny
  (3 named incidents on 2026-07-23), ACCESS-CLASS
  (`result_contracts.validate_worker_result:321-322`).
- Expected error profile (existence ~100%, live-behavior ~75%) respected: rows
  with non-auditable live-behavior claims remained `keep-pending` by orchestrator
  decision (CL10 autoscroll, GLM tile, CL28 diet wave-2).

## Application

**307 decisions applied, 0 failures**: 278 `discard` (conversational noise,
mechanical WF packets, CL23 side-project, resume boilerplate), 26 `backlog`, 3
`spec`. **57 remain pending DELIBERATELY** (keep-pending: live verification or
owner decision — never by omission).

## Top-10 for the owner (triage §3 is YOURS, with the orchestrator)

1. **SPEC-170 rule-6**: 4 spawn builders without `enforce_spawn()` — cited gap.
2. **Deny `.harness/` writes while gate-hold is occupied** — data-loss class 3x
   in one day; this night's loop re-measured the class (intake read masked by
   the serial probe's hold).
3. **ACCESS-CLASS in worker-result** — packet-only workers structurally rejected
   by `sourceFilesVerified`; whole wave discarded.
4. **Worker permission tier** — intake spec already open; ratification pending.
5. **Overseer routing precedence** — live one-turn check.
6. **Vendor/OS disparity ledger** (evolve each vendor, do not flatten them).
7. **local-model-config** — DRAFT + READY exist; awaiting your ratification.
8. **Backlog GUI undercounting** — quick live repro.
9. **Retire legacy GUI** — gate "is polish of the new one finished?" is yours.
10. **Auto-allowlist own hooks** — you already converged on the design.

Backlog rows for the 26 `backlog` decisions were NOT created in this round — §3
requires joint triage (owner + orchestrator); miner-proposed titles are in the
ledger, ready for `tasks add` when you return.

## Clusters (40, summary)

Delivered/discard-done with sha: worker-result pipeline (9ae4f91), ide-shard
W1-W3 (00312f2/ac5517d/01be458), gas-balancer/fuel (512a68a/6afb0eb), FormDialog
(32b320f), .env→vault (a151cc2), kimi (13a31f4..f5c9aa4), react-smoke (0572c18),
sandbox chokepoint (8206fe9), graph async (10894d3/f9e8f40), compaction research
(c2f6097), chat chips (802cd8b), ambient-core (6975fc0), context diet (3350ae5).
Noise: conversational filler (~40), mechanical WF packets (32), side-project
(~85), resume/checkpoint boilerplate (~19), one-shot probes (~20).

Provenance: Sonnet queue-slice miner (report-only, reading via TSV from JSON —
the queue's own `CL-jsontsv` idea, used before approval); audit and application
by the overseer (Fable). The next round never re-mines this ground: this file is
the CLOSED log for the slice.
