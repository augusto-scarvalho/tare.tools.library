# Backlog groom — intake queue, 2026-07-18

Report-only round executed by a Sonnet worker (playbook
`.harness/prompts/backlog-groom-playbook.md`), audited and applied by the
overseer with digest binding (`apply_decision --expected-digest` per row;
`allow_expired` for the 2 SLO-breached items). 125 pending asks → **123 decided,
2 kept pending** (live verification before deciding). Audit spot-check: 8/8
evidence shas for "done" verified in git log before the batch.

## Clusters (12) and decision pattern

| Cluster | N | Dominant decision |
|---|---|---|
| A. Execution packets pasted as asks | 15 | discard (instruction, not feature) |
| B. Model/cost directives | 6 | discard (encoded in CLAUDE.md) |
| C. Chat/rooms GUI bugs/requests | 22 | ~12 done · 5 backlog · remainder discard |
| D. IDE-mode / design system | 10 | done (SPEC-147 + phase 1 ce1dc54) |
| E. Experiments-page UX | 9 | done (2f056bb, 1c4b091, 51e9686) |
| F. Sandbox/isolation | 7 | done (SPEC-148 today) |
| G. Automatic gov:flake-reopen pings | 4 | discard (tracker artifact, not ask) |
| H. Article loop / EXPs | 12 | done (LOOP QUEUE 4 + EXP-15/16/17/18) |
| I. Hook/parity/graph findings | 8 | 3 done · 4 backlog/spec · 1 discard |
| J. Backlog/architecture meta | 8 | 2 backlog · rest discard |
| K. Pure Q&A | 12 | discard (answered inline) |
| L. Render/append smoke tests | 4 | discard |

## Promoted (backlog/spec) — items worth attention

1. **SPEC candidate — codex hook-trust + write-enforcement gap** (d77116ead917):
   experimentally verified security finding, still unfixed (real containment
   today is SPEC-148 + S3; this is the hooks leg).
2. `agents pair --apply` loses untracked fields (timeout/statusMessage) —
   data-loss bug in sync (46afc2ccdca3).
3. Backlog unification (dual JSON/MD → sqlite?) — structural debt identified by
   the owner (1a45713b7104).
4. GUI Stop button + CLI Esc-Esc + streaming-does-not-stop bug
   (d303a18496c1 + 01983640330b; duplicate 806964ccefab discarded).
5. Drag-drop/upload in chat compose (a06ba0abcc30).
6. codex app-server as default transport + interactive approvals
   (e86672c43942); upstream unified_diff issue (3f2eeb5a6b2a).
7. Real graph-navigation enforcement for workers + audit of codex grep usage
   (bc19d9361c04, af2eb9143447).
8. Gatekeeper latency/liveness indicator (9ebfa6c638b9 — recurring complaint).

## Deliberately pending (verify live before deciding)

- 11d53f79b03e — orphan scheduled jobs with no UI removal (may already be fixed).
- c1eb5b0da00c — screenshot attachment rendering strangely (same caveat).

## Honest errata

- The overseer swapped two ids in the batch: 9619f9bed62b (Q&A, should have
  been discard) received `backlog`; corrected on the intended target
  (9ebfa6c638b9 → backlog). The queue journal carries both records; impact: one
  extra Q&A item in the backlog bucket.
- Miner precision guard applied: only "done" with a verifiable sha; 8/8 sampled
  entries matched.
