> APPLIED 2026-07-23 by overseer (post-audit): 33 `discard` + 11 `done` + 9 `backlog` =
> 53 decided through `intake decide`; pending 53→0. Audit confirmed every done-in-git SHA
> in `git log` and the 3 still-valid live claims (encoding residual, rt6 timing, SSE) by
> reading code/telemetry. +2 entries arrived after the miner's slice (`11686fc57f09`
> codex-fuel-followup → backlog; `898ffa513164` groom-hook ask → done in b309625).

# Backlog Groom — Intake Queue, 2026-07-23 (Queue Slice)

Queue-slice round (playbook `.harness/prompts/backlog-groom-playbook.md` §1-2), wind-down of AFK loop
`gui-react-parity` + 4 backlog AFK waves. Queue read through
`python scripts/harness.py intake list --json` (HARNESS_QUIET=1): **51 pending**.

The queue was heavily polluted by the UserPromptSubmit intake-triage hook: most of the 51 entries are raw
conversation messages captured from an interactive session (owner questions, orchestration/resource
instructions, raw plan-spawn commands “Read .harness/handoff/plan-X.md and implement EXACTLY...”), not
isolatable backlog requests. Every entry was read and classified individually against the playbook
vocabulary; every done claim was verified in `git log` (never assumed), and the 3 “scenario-hot”/encoding
gaps were re-verified by reading LIVE code/telemetry, not only commit messages.

## Ledger (51/51)

| id | summary | verdict | evidence |
|---|---|---|---|
| 09de5548ecb4 | Question: “can subprocessedges run while we work?” | discard-noise | Session Q&A about feature already shipped at 07:48 (5268938); no isolatable ask |
| 1d983501b5a7 | Question: “weren’t we processing AST then?” | discard-noise | Session technical Q&A about Graphify AST policy; no isolatable ask |
| ac7ae80b3a70 | Ask: invest in fixing broken TSV-vs-JSON traffic | done-in-git | `6710f3d` (phase 6, “structural TSV/JSON boundary”) + `a9f453d` (“TSV boundary P1... closes 4-leg matrix”), both ~40–70 min after ask (12:29 → 13:17/13:38) |
| bc3e30772c45 | Informal spec: 4-leg matrix agent-tsv / app-json + parser between | done-in-git | `6710f3d`: “TSV/JSON boundary (owner 4-leg matrix): canonical from_tsv in common.py...” literally cites owner matrix |
| f99443c2b651 | Ask: hook/structure to guarantee TSV traffic+parsing | done-in-git | `a9f453d`: “live-seams clause in subagent-contract (canonical valve)” + tj-6/tj-7 scenario — requested structure |
| 9943b8d73c98 | Question: do skips help reckon know where not to look? | discard-noise | Session technical Q&A, no artifact to produce |
| 948c81a2ac6f | “how about prioritizing now? or do we have a blocker?” | discard-noise | Pure session steering |
| df5f5c1e5bbc | Complaint: incomplete front end, “where is the rest of the new GUI?” | discard-noise | Session message kicking off gui-react-parity loop; not an item by itself |
| b098ff7efade | “put Codex to program too” | discard-noise | Resource-allocation instruction, not feature ask |
| 0bb45d35f00f | Raw spawn: “Read plan-gui-port-research.md and implement...” | discard-noise | Mechanical spawn command; plan already exists as own artifact in `.harness/handoff/` |
| 0e3124724ded | “let’s work in a loop until parity with legacy GUI...” | discard-noise | Loop kickoff steering, not isolatable item |
| 25a3516a42d8 | “2 opus and 2 codex per iteration, sonnet xhigh for tests” | discard-noise | Resource-allocation instruction |
| f4b8d773b806 | Raw spawn: “Read plan-gui-port-board.md and implement...” | discard-noise | Mechanical spawn command |
| 04e412bd5ac7 | Overseer-loop: post gate-staged commit instruction (it.1) | discard-noise | Heartbeat/orchestration instruction, not item |
| 31c545d2b923 | Raw spawn: “Read plan-gui-port-activity-tail.md and implement...” | discard-noise | Mechanical spawn command |
| b442ca000668 | Overseer-loop heartbeat (gui-react-parity, it.2) | discard-noise | Status heartbeat, not item |
| f8ac2160b5e6 | GUI backend gap: Workbench Preview lacks rendered-output endpoint | still-valid-backlog | 1 of “4 SPEC-116 backend-gap intakes” recorded in `1acc0f1`; live-verified: `ui/src` has no Preview screen/endpoint (grep only finds Terminal-follow scroll, unrelated) — EmptyState gap remains open, owner decision pending |
| 0687a668c8e3 | GUI backend gap: Workbench Terminal would require interactive exec (conflicts SPEC-114) | still-valid-backlog | Same set of 4 intakes `1acc0f1`; owner design decision explicitly pending, no commit resolves |
| 7708a32b426d | GUI backend gap: Workbench Artifacts lacks data source | still-valid-backlog | Same set; no new verb lists session/worker artifacts in current code |
| 8611d7ae8c57 | GUI backend gap: Activity Releases has no harness concept | still-valid-backlog | Same set; harness still lacks release concept beyond commits/tags |
| 7b50b3ee2561 | Defect: `/api/state` COLD ~11.8s (instrumented curl) | done-in-git | `1aaf676` AFK wave 1: “api-state-cold-latency... summarize(include_disk=False)... 531ms→16ms (97%)” — root cause `cost_metrics._dir_mb` (os.walk ~12k files) |
| 9199cf58fc57 | [gov:scenario-hot] pw_ui_smoke subprocess 73s >45s | done-in-git | Resolved as side effect of above fix; `4cfa607` explicitly confirms (“serial-div-pw-incidents RESOLVED... pw_ui_smoke no longer appears in gate-divergence”); `.harness/runs/gate-perf.jsonl` last 5 rounds show first attempt ~23–26s, well below 45s |
| efa57b02b0ad | GUI-AC3 gap: `/api/audit` only shows live tail (minutes), not hash-chained archive trail | done-in-git | Flagged as intake in `1acc0f1` (“audit-window gap found by owner (‘only one?’) → intake + copy fix in polish lane”); fix shipped `2c42481` (“gui-polish-1... audit window copy”). Note: resolved by minimal option (b) honest copy, NOT option (a) archive aggregation endpoint — if owner wants (a), that is a new ask |
| 253dba67046b | Overseer-loop: post gate-staged commit instruction (it.2) | discard-noise | Heartbeat/orchestration instruction |
| 9424773b48eb | Residual encoding audit: `run_bounded_command` (spec_test_gate.py) decodes stdout with cp1252 on Windows | still-valid-backlog (live-verified) | LIVE `scripts/spec_test_gate.py:120`: `kwargs.setdefault("text", True)` WITHOUT `encoding=` — bug remains. `1acc0f1` fixed 20 OTHER sites (`processes.run_quiet`/`run_process_tree_bounded`) but reverted this file’s hunk because it collided with gs-7 ratchet (“hunk reverted, forensics-decode residual becomes intake with spec door” — this intake IS that residual) |
| d75adc20c676 | “no shell or agent running appears, are we waiting on something?” | duplicate-of 5115c47c4941 | Same topic (detached runs invisible in GUI), raised ~1h30 before structured manual intake; no own fix, covered by structured entry |
| e7876a0379a8 | Raw spawn: “Read plan-gui-port-code.md and implement...” | discard-noise | Mechanical spawn command |
| f1650a011189 | [gov:scenario-hot] rt6_route_writechain subprocess 48s >45s | still-valid-backlog (live-verified) | `.harness/runs/gate-perf.jsonl` last 5 rounds: parallel attempt still 65–84s (WORSE than 48s that triggered flag); no commit cites timing fix for this scenario (`ae3e89a` fixed another bug — false-skip guard, not duration) |
| fec6caf9a052 | Raw spawn: “Read plan-gui-port-code.md and implement...” (retry, preconditions verified) | discard-noise | Mechanical spawn command (retry of same plan e7876a0379a8) |
| 0b91d8abed03 | Confirmed by measurement: Chromium 6-conn/host cap + SSE serializes fetches (4116ms vs 824ms) | still-valid-backlog | This intake AND “→ intake SSE” cited as output of polish-lane item7 in `2c42481`; `git log --all --grep=SSE` only finds DISCOVERY commit, no teardown/pooling fix |
| 5115c47c4941 | GUI Operations gap: detached gates (gate-staged/validate) invisible in GUI | still-valid-backlog | Live-verified: `grep -r "gate-staged\|detached" ui/src` = zero results; no `gates[]` in `/api/runtime`; owner item (`detached-gates-GUI-visibility`) remains open |
| 850c0fe7bacf | Error: “bash: tools/agent-sync/py-run.sh: No such file or directory” | done-in-git | `2c42481`: “cwd-robust guard layer (owner report ‘py-run.sh not found’): 15 hooks... absolute $CLAUDE_PROJECT_DIR form”; commit 22:32:37, ask 21:55:19, same session |
| 245c6eb86982 | Overseer-loop: final gate instruction (it.3) | discard-noise | Heartbeat/orchestration instruction |
| 6f907190fcd7 | Ask: non-prose mechanisms (hooks) + implement “fuel gauge” | done-in-git | `64b5ed8` literally cites: “MECHANISMS (owner order: ‘not pure prose; hooks and mechanisms’)” (cwd_guard.py, spawn_hold_guard.py, gate_staged dirty-guard, hcs scenario) + “FUEL GAUGE v1 (SPEC-168, live owner refinement)” |
| 79c88cbfc042 | Overseer-loop: final commit instruction (it.3) | discard-noise | Heartbeat/orchestration instruction |
| 30e3eb2692aa | Raw spawn: “Read plan-loop-guards.md and implement...” | discard-noise | Mechanical spawn command; work landed in `64b5ed8` (same as 6f907190fcd7) |
| 434ad4336180 | “let’s flip, but first workers spec-by-spec + visual confirmation” | discard-noise | Orchestration instruction for pre-flip round; substance covered by `64b5ed8` (4 audits) + `2c42481` (polish round), but message itself is steering |
| 847f841e5de4 | Overseer-loop: pre-flip sequence (accidental gate in flight) | discard-noise | Heartbeat/orchestration instruction |
| f2644195d7dc | Proposal: OS-keyring write-only for vendor keys | done-in-git | `63db787`: “keys-keyring (opus kept, security-review PASS): SPEC-169... write-only... keyring-first... `keys migrate`... React Keys screen” |
| 6ab68187a87c | Overseer-loop: post-verdict commit (pre-flip) | discard-noise | Heartbeat/orchestration instruction |
| d490dcd759f8 | “are you in the right directory? what are you doing now?” | discard-noise | Session check question, no ask |
| 8707a8c4db63 | Raw spawn: “Read plan-test-debt-code-extract.md and implement...” | discard-noise | Mechanical spawn command (work landed `63db787`, row closed) |
| 70e7bcab4901 | Raw spawn: “Read plan-ui-e2e-deadlines.md and implement...” | discard-noise | Mechanical spawn command (work landed `1aaf676`, ui-e2e-deadline-widening) |
| 1a23ed816882 | Raw spawn: “Read plan-perf-hotspot-watch.md and implement...” | discard-noise | Mechanical spawn command (work landed `63db787`, SPEC-109 Phase 2) |
| 429e6f9905f9 | Overseer-loop AFK wave 2: in-flight status + reconciliation plan | discard-noise | Heartbeat/orchestration instruction |
| ec9acfff0911 | reckon-hold fix PARTIAL: durable ledger reduced but did not eliminate 100% | duplicate-of 1ce62bb00fd0 | Explicitly cited as resolved: `1ce62bb00fd0` says “intakes ec9acfff0911+46f571bd1c69 RESOLVED by this”; actual root cause closed in `cfb16da` |
| 6e223a4f4184 | Raw spawn: “Read plan-docs-audit-refs.md and implement...” | discard-noise | Mechanical spawn command (work landed `c0bba2f`, docs-audit-refs) |
| 52b08fffd67b | Raw spawn: “Read plan-svc-mcp-wiring.md and implement...” | discard-noise | Mechanical spawn command (work landed `c0bba2f` + follow-up `fae00e7`) |
| 46f571bd1c69 | Confirmation: reckon-hold fix INEFFECTIVE in live gate (3/3 integrations) | duplicate-of 1ce62bb00fd0 | Same case; `1ce62bb00fd0` also cites this ID nominally as resolved |
| 1ce62bb00fd0 | reckon-hold REALLY CLOSED: actual cause was cleanup_test_artifacts deleting ledger | done-in-git | `cfb16da`: “reckon-hold real ROOT CAUSE — gate runner deleted its own reckon ledger... FIX (1 line)... LIVE PROOF... no re-record” — exact match with intake text |
| efa1d53c9bf4 | “wasn’t groom supposed to run at the end of the AFK loop?” | discard-noise | Session meta-question — literally the trigger for this round |

## SUMMARY

- **discard-noise:** 30
- **done-in-git:** 10
- **still-valid-backlog:** 8
- **duplicate-of:** 3
- **needs-live-verification:** 0 (3 ambiguous candidates — 9424773b48eb, f1650a011189, 5115c47c4941 —
  resolved by reading live code/telemetry rather than leaving pending)
- **Total:** 51/51

### Recommended apply list

**Immediate discard (33 IDs)** — 30 discard-noise + 3 duplicate-of (covered by another entry, no own decision):
`09de5548ecb4, 1d983501b5a7, 9943b8d73c98, 948c81a2ac6f, df5f5c1e5bbc, b098ff7efade, 0bb45d35f00f, 0e3124724ded, 25a3516a42d8, f4b8d773b806, 04e412bd5ac7, 31c545d2b923, b442ca000668, 253dba67046b, e7876a0379a8, fec6caf9a052, 245c6eb86982, 79c88cbfc042, 30e3eb2692aa, 434ad4336180, 847f841e5de4, 6ab68187a87c, d490dcd759f8, 8707a8c4db63, 70e7bcab4901, 1a23ed816882, 429e6f9905f9, 6e223a4f4184, 52b08fffd67b, efa1d53c9bf4, d75adc20c676, ec9acfff0911, 46f571bd1c69`

**Discard-done, with SHA (10 IDs)** — `ac7ae80b3a70`(6710f3d/a9f453d), `bc3e30772c45`(6710f3d),
`f99443c2b651`(a9f453d), `7b50b3ee2561`(1aaf676), `9199cf58fc57`(1aaf676/4cfa607),
`efa57b02b0ad`(2c42481), `850c0fe7bacf`(2c42481), `6f907190fcd7`(64b5ed8),
`f2644195d7dc`(63db787), `1ce62bb00fd0`(cfb16da)

**Keep in backlog / owner decision (8 IDs)** — 4 Wave-7 backend gaps (`f8ac2160b5e6`, `0687a668c8e3`,
`7708a32b426d`, `8611d7ae8c57`), real encoding residual (`9424773b48eb`), still-hot scenario
(`f1650a011189`), SSE pool starvation (`0b91d8abed03`) and detached-gates GUI visibility
(`5115c47c4941`). All already contain enough context to become `docs/IMPLEMENTATION_BACKLOG.md` rows directly,
without a spec door — except `9424773b48eb`, which names its own door (ratchet amendment or net-negative refactor).

No writes were made: queue, `specs/`, `testing/`, and protected files untouched; zero `git` ops; zero
`intake decide`.
