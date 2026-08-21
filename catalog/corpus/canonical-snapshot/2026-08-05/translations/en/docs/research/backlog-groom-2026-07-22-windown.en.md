> MINER LEDGER — PENDING OVERSEER AUDIT (playbook §2) — NON-CANONICAL until
> applied through `intake decide`. Report-only: no intake decisions were made,
> no files outside this report were touched.
>
> **Postscript (20:48-03:00, after this ledger was written):** the in-flight
> `validate --staged` gate (pid 8432, hold `20260722T232457Z-8432`) whose snapshot
> this report read finished with **status: fail** (2 scenario checks:
> `m4_status_html` empty:seeds-gone, `pw_ui_smoke` incidents-drill; +1
> release-hygiene:generated-artifacts on `.harness/runs/events.jsonl` — out of scope
> for this report, belongs to the session owning the gate). Its own
> `rule_scenario_hot` governance check raised ONE new pending entry AFTER this
> ledger’s 27/27 was written: `f1650a011189` `[gov:scenario-hot:rt6_route_writechain]`
> (48s >45s), asked 20:47:51 — same cluster V treatment as `9199cf58fc57` above
> (auto-reincident tracker artifact, `discard`). Live queue is now 28 pending;
> this ledger covers 27/28 (all except the one that arrived after submission).

# Intake Groom — Intake Queue, 2026-07-22 (Wind-down, Loop Session 1)

Queue-slice round (playbook `.harness/prompts/backlog-groom-playbook.md` §1). Sonnet 5 miner,
report-only. Third window of the day — previous two closed queue at zero
(`docs/research/backlog-groom-2026-07-22.md` 16→0 around 06:00 6h-loop;
`docs/research/backlog-groom-2026-07-22b.md` 8→0 around 10:02); this window covers exhaustion of
`gui-react-parity` session that followed (11:51–20:24), the same referred in checkpoint
`.harness/context/NEXT_STEPS.md` (“SONNET groom-miner report-only (26 pending intakes...)” — actual queue
had 27 at capture time, expected off-by-one due seconds between checkpoint note and gate-hold capture).

**Vocabulary note:** task prompt requested labels `done-in-git / duplicate / still-valid /
needs-live-verification / stale`, but real playbook §1 contract (queue-slice variant) defines
`discard / discard (done, with sha) / backlog / spec / experiment / keep-pending`. I followed the real
playbook contract (explicit instruction: “read ... and follow its ledger contract”), not prompt wording.
Approximate mapping: `done-in-git` ≈ `discard (done)`; `duplicate` ≈ `discard` (state dump / repeated
instruction); `still-valid` ≈ `backlog`; `needs-live-verification` — I live-verified ALL backlog candidates
this round (current source-code reading, not existence grep), so no item remains unresolved in that category;
`stale` did not apply (no pending older than 7 days — entire window is today).

**Access note:** `.harness/state/intake-queue.json` does not exist at root at this read — an in-progress
gate hold exists (pid 8432 alive, confirmed via `tasklist`), created `20260722T232457Z`
(`.harness/runs/gate-hold/20260722T232457Z-8432/hold.json`). I read the live queue copy inside hold snapshot
(`.harness/runs/gate-hold/20260722T232457Z-8432/e0/intake-queue.json`), read-only — no `.harness/` writes,
no git operation, no `intake decide`.

## 1. Totals

- Pending (live queue under in-progress gate hold): **27** at original read; see postscript — rose to 28
after gate finished, 28th item listed in §3 but outside original count.
- Proposed:
  - discard: 20 (+1 postscript = 21)
    - **discard (done, with SHA/evidence):** 9
    - simple discard (Q&A/steering/heartbeat/tracker artifact, no persistent ask): 11 (+1 postscript)
  - backlog (still-open candidates, live-verified): **7**
  - spec / experiment / keep-pending: 0

(20 + 7 = 27; +1 postscript = 28.)

## 2. Cluster table

| Cluster | N | Dominant decision |
|---|---:|---|
| Q. One-off Q&A/steering without persistent ask | 4 | discard |
| W. Worker brief text pasted by hook (not owner ask) | 4 | discard |
| H. Heartbeat/state dump of loop itself | 3 | 2 discard (done, executed within minutes) · 1 discard (dump) |
| T. TSV boundary policy + hook/guard request | 3 | discard (done) — `a9f453d` + `6710f3d` |
| R. Q&A reckon skips↔reach | 1 | discard (done) — `aa6c285`/`8cd4198` |
| D. Model-distribution directives (codex/opus) | 3 | discard (done/codified) — `1acc0f1`, `1b2941b`, checkpoint trail |
| G. Trigger complaint “GUI incomplete” (remediation loop) | 1 | discard (steering; loop IN FLIGHT, not new ask) |
| B. Honest Workbench backend gaps (Preview/Terminal/Artifacts/Releases) | 4 | **backlog** (4×, live-verified) |
| P. `/api/state` COLD performance defect | 1 | **backlog** |
| A. Audit trail gap (rotated file outside window) | 1 | **backlog** |
| E. Encoding-audit residual (cp1252 without `encoding=`) | 1 | **backlog** |

## 3. Ledger by entry (27/27)

`09de5548ecb4` | Q | discard | 11:51 “can this subprocessedges thing run while we work?” — one-off question about in-flight work concurrency | inline Q&A, no persistent ask

`1d983501b5a7` | Q | discard | 11:53 “weren’t we processing AST then?” — question about existing Graphify AST capability | inline Q&A

`ac7ae80b3a70` | T | discard (done) | 12:29 policy TSV-for-agent-traffic/JSON-for-internal-communication — `a9f453d` (13:38) “feat(harness): TSV boundary P1 — findings/reviewFindings accept TSV table string”, body cites “closes 4-leg matrix: P3 emit / P4 scrub (`6710f3d`) / P2 contract / P1 this commit” | policy shipped same day, minutes later

`bc3e30772c45` | T | discard (done) | 12:33 TSV-flow elaboration (same cluster) — same `a9f453d`/`6710f3d` evidence | same policy detail, same delivery

`f99443c2b651` | T | discard (done) | 12:36 “do we need to create some hook/structure to guarantee this TSV traffic and parsing? do that next” — `a9f453d` adds `common.tsv_table` as ingestion adapter BEFORE schema check in `WORKER_RESULT.findings`/`REVIEWER_RESULT.reviewFindings` (requested “structure”) | literal ask fulfilled in same commit, 62min later

`9943b8d73c98` | R | discard (done) | 14:41 “do skips also help reckon understand where not to look?” — `aa6c285` (14:51) body: “radius of staged surface by SAME gate_affected map used by skips” — answer YES, confirmed by shipped commit 10min later | Q&A answered by real feature

`948c81a2ac6f` | Q | discard | 14:44 “how about prioritizing now? or do we have a blocker?” | steering/Q&A, no isolatable ask

`df5f5c1e5bbc` | G | discard | 17:37 “you said front-end tasks were finished, but I opened it and several pages are missing... where is the rest of the new GUI?” — trigger for remediation loop; `1b2941b` (18:56) “remediation loop iteration 1 — 5 React lanes (fixes D1-D12...)” and `1acc0f1` (20:23) iteration 2; checkpoint `.harness/context/NEXT_STEPS.md` records “IN FLIGHT iteration 3” at read time | real ask, PARTIALLY addressed — loop remains open (not “done,” but driver of entire session already tracked by checkpoint; no new backlog row needed)

`b098ff7efade` | D | discard (done) | 18:05 “put Codex to program too, GPT-5.6 Sol high” — `1acc0f1` body: “gui-port-activity-tail (codex gpt-5.6-sol, kept, 240994tk)” | codex lane ran same day

`0bb45d35f00f` | W | discard | 18:07 full worker brief (“Read .harness/handoff/plan-gui-port-research.md and implement EXACTLY...”) captured verbatim by hook — not owner ask, prompt overseer gave subagent (hook filter only blocks payload beginning with `<`) | capture noise, precedent cluster A/K from prior rounds

`0e3124724ded` | D | discard (done) | 18:09 “let’s work in loop until parity... add Codex to loop as implementer too” — codified in checkpoint `NEXT_STEPS.md` (“PERMANENT ORDERS”) and executed in commits `1b2941b`/`1acc0f1` (mixed opus+codex lanes) | directive actively executed

`25a3516a42d8` | D | discard (done) | 18:16 “2 opus and 2 codex per iteration... whoever builds GUI tests can be sonnet 5 xhigh” — `1acc0f1` body: “gui-tests-interactions (sonnet xhigh, kept, 324944tk)” | model mix applied literally same commit

`f4b8d773b806` | W | discard | 18:19 full brief (“Read .harness/handoff/plan-gui-port-board.md and implement EXACTLY...”) | same W capture noise

`04e412bd5ac7` | H | discard (done) | 18:55 heartbeat “detached gate-staged (marker ...20260722T184539.marker) should have completed — read... If PASS: ... commit batch of 5 lanes” — `1b2941b` committed 18:56:02, one minute later, message matches description (5 lanes, D1-D12) | loop note, executed next minute

`31c545d2b923` | W | discard | 18:58 full brief (“Read .harness/handoff/plan-gui-port-activity-tail.md and implement EXACTLY...”) | same W capture noise

`b442ca000668` | H | discard | 19:24 descriptive heartbeat (“Overseer-loop heartbeat... Lanes in flight: gui-port-activity-tail (codex)...”) truncated to 400 chars by ASK_CAP itself | state dump, no isolatable ask

`f8ac2160b5e6` | B | **backlog** | 19:24 (source=manual) “Workbench Preview needs endpoint serving rendered target-app output (none /api/* exists); without source section stays honest EmptyState” — LIVE verified: `ui/src/domains/workbench/WorkbenchScreen.tsx:126` renders `<EmptyState ... hint="Nativizes in a later Workbench slice." />` for every `route.section` outside `conversation`/`changes`; preview/render `/api/` grep = 0 hits | real gap, confirmed in current code, no `docs/IMPLEMENTATION_BACKLOG.md` row covers it

`0687a668c8e3` | B | **backlog** | 19:24 “Workbench Terminal would require interactive exec channel — conflicts GUI-writes-no-state (SPEC-114); owner design decision before endpoint” | same `WorkbenchScreen.tsx:126` verification (Terminal falls into same generic EmptyState); owner decision explicitly pending, no backlog row

`7708a32b426d` | B | **backlog** | 19:24 “Workbench Artifacts lacks data source... candidate derive from .harness/runs + evidence” | same verification; no backlog row

`8611d7ae8c57` | B | **backlog** | 19:24 “Activity Releases lacks source... decide whether section dies or gets verb” | same verification (Releases section does not exist in `ui/src/domains/activity`); no backlog row

`7b50b3ee2561` | P | **backlog** | 19:57 “Backend defect (measured 2026-07-22): /api/state COLD takes ~11.8s... warm 293ms... investigate state_snapshot (profile + incremental cache per source, adjacent SPEC-133)” — `docs/IMPLEMENTATION_BACKLOG.md` grep for `state_snapshot`/`api/state` = 0 hits | measured defect with concrete numbers, no row covers it; real perf candidate

`9199cf58fc57` | V | discard | 20:06 `[gov:scenario-hot:pw_ui_smoke] Scenario pw_ui_smoke: subprocess 73s >45s` — auto-generated by `gate_governance.rule_scenario_hot` (`scripts/harness_lib/gate_governance.py:64,119-120`), with own cooldown (`_blocked_by_queue`); cluster-G precedent from 07-18/07-21 treats these pings as auto-reincident tracker artifacts, not new ask | no specific `pw_ui_smoke` backlog row yet, but mechanism re-raises itself if condition persists — no dedicated intake row needed

`efa57b02b0ad` | A | **backlog** | 20:12 “GUI-AC3 gap discovered by owner (‘only one?’): /api/audit reads only LIVE events.jsonl, which rotates into archive/... Audit screen shows minutes-long window (1 event) instead of rich hash-chained trail” — LIVE verified in `scripts/harness_ui.py:546-569` (`_events_raw` reads only `.harness/runs/events.jsonl`, no `archive/` merge); `012c7e7` (16:55, BEFORE ask) and `1acc0f1` (20:23, AFTER) touch AC3/AC4 but neither modifies `_events_raw` | gap confirmed still open after both Activity deliveries; design decision needed (endpoint aggregates archive vs honest copy)

`253dba67046b` | H | discard (done) | 20:13 heartbeat “iteration-2 detached gate-staged (marker ...20260722T200202.marker)... Commit iteration-2 batch” — `1acc0f1` committed 20:23:09, ~10min later, message matches (act-tail codex, encoding audit, tests interactions) | loop note, executed minutes later

`9424773b48eb` | E | **backlog** | 20:14 “encoding-audit residual: run_bounded_command (spec_test_gate.py) decodes scenario stdout as cp1252 on Windows (text=True without encoding)... 3-line fix collides with gs-7 ratchet (<1660 lines)” — LIVE verified: `scripts/spec_test_gate.py:120` `kwargs.setdefault("text", True)` without `encoding=`; `testing/scenarios/gs_gate_structure.py:60` `PRE_MOVE_LINES_R3 = 1660`; `wc -l scripts/spec_test_gate.py` = **1659** (1-line headroom — confirms described footgun) | defect and ratchet confirmed in current code, no backlog row

`d75adc20c676` | Q | discard | 20:22 “in the interface no shell or agent appears in progress; are you actually waiting for something?” — question about process state at that moment, not GUI feature request | inline Q&A

`e7876a0379a8` | W | discard | 20:24 full brief (“Read .harness/handoff/plan-gui-port-code.md and implement EXACTLY...”) | same W capture noise; last entry before gate hold (20:24:57)

`f1650a011189` | V | discard | 20:47 (source=governance, arrived AFTER original ledger read — see postscript) `[gov:scenario-hot:rt6_route_writechain] Scenario rt6_route_writechain: subprocess 48s >45s in last round` — auto-generated by same `gate_governance.rule_scenario_hot` as `9199cf58fc57`, produced by gate itself (pid 8432, status fail) | same cluster-V treatment: auto-reincident tracker artifact, no dedicated intake row

## 4. Ranked top candidates for owner (7 backlog)

1. **f8ac2160b5e6 / 0687a668c8e3 / 7708a32b426d / 8611d7ae8c57 — honest Workbench/Activity gaps
   (Preview, Terminal, Artifacts, Releases).** All 4 sections fall into same generic `EmptyState`
   (`WorkbenchScreen.tsx:126`); each needs a DIFFERENT design decision from owner before any endpoint
   (Terminal especially hits SPEC-114 GUI-writes-no-state). Already cited as “Wave 7” in loop checkpoint,
   but no formal `docs/IMPLEMENTATION_BACKLOG.md` row — candidates for 1 consolidated row with 4 subdecisions,
   or 4 independent rows.
2. **7b50b3ee2561 — `/api/state` COLD ~11.8s.** Performance defect measured with concrete numbers
   (293ms warm vs 11.8s cold); related to SPEC-133; no backlog row.
3. **efa57b02b0ad — Audit trail only sees live window.** Gap confirmed in current code even after both
   Activity deliveries; needs decision (archive-aggregating endpoint vs honest copy).
4. **9424773b48eb — cp1252 encoding in `run_bounded_command`.** 3-line fix, but collides with gs-7 ratchet
   (1659/1660 lines, no room); needs a door (ratchet spec-door amendment or net-negative refactor financing lines).

## 5. Honest errata

- Q/W/H clusters (11 items) have no recoverable answer SHA — Q&A/steering/heartbeat/brief-text evaporate from
  conversation; marked `discard` by form classification (same precedent as 07-18/07-21/07-22b rounds), not
  session transcript reading (no access).
- `df5f5c1e5bbc` (“where’s rest of GUI?”) is the one item where `discard` is simplification: ask is REAL and
  only partially served (remediation loop remains `IN FLIGHT` iteration 3 at read time). It did not become
  `backlog` because it is already the live checkpoint driver, not a new item — but next overseer must confirm
  iteration 3 closes gap before treating pending as resolved.
- `9199cf58fc57` (gov:scenario-hot pw_ui_smoke) is `discard` by precedent (auto-reincident tracker artifact),
  not because problem is resolved — if 73s persists, `gate_governance` will raise again.
- I did not touch `.harness/state/intake-queue.json` nor copy under `.harness/runs/gate-hold/` (read-only),
  nor `specs/`, `testing/`, protected files. No `intake decide`, no git operation.
