# SPEC-144 — route-dispatcher: opt-in two-tier router + specialized overseer

Status: SPEC-144, proposed 2026-07-14. Acceptance scenarios land per build phase
(`testing/scenarios/rt_route_dispatcher.py`, ids `rt-*`). Phases 1-2 wire the formal Gherkin block
below (ids `rt-1`..`rt-4`, resolving into that scenario file); the remaining `rt-*` ids are added to
the block as their phases land.

Intake (SPEC-116 door NEW, from the overseer design `.harness/handoff/plan-route-dispatcher.md`):
request = replace the single fat-overseer loop (which re-derives context per item -> triple/quad
reads, cost scaling with session length, and no heartbeat) with an **opt-in** two-tier topology: a
cheap **router** semantically triages each demand and dispatches it to a right-sized **specialized
overseer** that owns that one demand end to end (plan -> implement inline|workers -> audit -> commit)
and returns control to the router for the next demand.

## Goal

An opt-in `/route` surface that, when invoked (standalone or in a loop), runs a two-tier flow:
(1) a **model-first router** (Sonnet 5 high, fallback gpt-5.6-terra high) does first-contact semantic
triage of a demand — deciding dynamic-workflow vs pre-defined profile vs inline, inline-vs-delegate,
and escalation — bounded below by the deterministic `intake_triage` guardrail it must honor; and
(2) a **specialized overseer** (Fable 5 high, generic for now) that writes the detailed
implementation plan, decides inline-vs-workers, audits after implementation, and commits, then
returns a verdict to the router. NOT invoking `/route` leaves today's inline flow byte-identical —
the opt-in command IS the reversibility.

## Applicability

Applies to a new `/route` skill (`.claude/skills/route/`) and a `harness.py route` verb (single
demand in Phase 1; `--loop` in Phase 3); a new **execution workflow profile** (`feature-delivery`,
`writeAllowed:true`, `overseerRole` = Fable 5 high) in `.harness/workflows/workflow-profiles.json`;
the router built on the existing deterministic classifier (`scripts/harness_lib/intake_triage.py`
+ `classify` in `scripts/harness.py`) as a GUARDRAIL floor plus a cheap-model triage layer; the
workflow engine (`scripts/harness_lib/workflow_lifecycle.py`: `workflow_execute`,
`workflow_finalize`, `update_context_from_workflow`) for spawn+reduce+return; the routing tables
(`.harness/routing/task-profiles.json`, `model-routing.json`) for the router/overseer model pins;
and `ScheduleWakeup` as the loop heartbeat (Phase 3).

It does **not** change any of the 10 existing (`writeAllowed:false`) analysis workflow profiles,
alter today's inline flow when `/route` is not called, move plan authorship out of the overseer tier
(the specialized overseer owns the plan; the router never plans), or auto-decide protected-file or
security escalations (those still bubble to the owner). memoryScope per-role is out of scope
(tracked separately, blocked on a memory subsystem).

## Requirements / invariants (numbered, testable)

1. **Opt-in reversibility.** With `/route` never invoked, every existing code path is byte-identical
   to today; the router/overseer topology is reachable ONLY through the `/route` skill or the
   `harness.py route` verb. Removing the profile + skill fully reverts the feature.
2. **Model-first router with a deterministic floor.** The router's dispatch decision is made by a
   model (Sonnet 5 high; fallback gpt-5.6-terra high). The deterministic `intake_triage` layer
   supplies flags/gates/escalation triggers the router MUST honor: a security/risk flag forces
   escalation regardless of model judgment (the model can raise severity, never lower it).
3. **Router decision space.** For each demand the router emits exactly one route —
   `dynamic-workflow` (a DAG computed on the fly), `pre-defined-profile` (one of the existing
   workflow profiles), or `inline` — plus an inline-vs-delegate hint and any escalation. The router
   performs NO heavy file reads (triage on demand text + deterministic hints + doc-find handles).
4. **Specialized overseer ownership.** The specialized overseer (Fable 5 high) receives the compact
   brief, WRITES the detailed implementation plan, decides inline-vs-workers (final call, even when
   the router hinted `inline`), AUDITS after implementation, and COMMITS. The router never plans.
5. **Compact handoff contract.** router -> overseer is a compact brief (demand text + classified
   route + covered-doc handles + inline hint; NO pre-read file dumps). overseer -> router is a
   committed-state + typed verdict, which advances the router to the next demand.
6. **Bounded loop + heartbeat.** `/route --loop` drains the demand feed one demand at a time with a
   `ScheduleWakeup` heartbeat, SKIPS the SPEC-116 "no behavior change -> no artifact" class, and has
   an explicit stop condition (empty actionable feed OR owner interrupt) — the heartbeat is a bounded
   fallback, never an unbounded spawner.
7. **Execution profile isolation.** The new `feature-delivery` profile is the only `writeAllowed:true`
   profile; the 10 existing analysis profiles are unchanged and remain read-only.
8. **Measured (EXP-10).** Reads and tokens per demand are recorded so the flat-loop vs routed-loop
   comparison is a keep/revert gate, not a vibe.

## Rationale & sources

| Decision | Source |
|---|---|
| Router promotes the existing deterministic classifier rather than a new one | `scripts/harness_lib/intake_triage.py` (SPEC-117); `classify` in `scripts/harness.py` ("the router itself") |
| Deterministic-first router REJECTED — first-contact triage incl. dynamic-workflow decision is a reasoning task | owner 2026-07-14; `.harness/handoff/plan-route-dispatcher.md` D-b |
| Router = Sonnet 5 high / fallback gpt-5.6-terra high; specialized overseer = Fable 5 high | owner 2026-07-14; `.harness/routing/model-routing.json` roles |
| Execution needs a new `writeAllowed:true` profile — all 10 existing profiles are analysis-only | `.harness/workflows/workflow-profiles.json` (every profile `writeAllowed:false`) |
| Heartbeat via ScheduleWakeup — the AFK loop died because it was never armed | overseer playbook non-negotiable #5; the flat-loop wind-down 2026-07-14 |
| Opt-in command is the reversibility + the kill switch | owner 2026-07-14; SPEC-116 door NEW |

## Test strategy

Acceptance scenarios (hermetic, `testing/scenarios/rt_route_dispatcher.py`, landing per phase; ids
wired into a `gherkin` block in Phase 1):
- `rt-1` router decision: canned demands -> exactly one route (dynamic-workflow | pre-defined-profile
  | inline) + inline hint; a security-flagged demand escalates even against a benign model verdict
  (invariant 2, 3).
- `rt-2` guardrail floor: the deterministic `intake_triage` flags are honored as a floor (severity
  can rise, never fall) (invariant 2).
- `rt-3` handoff contract: the router->overseer brief is compact (no file-dump payload) and the
  overseer->router return carries a typed verdict advancing the feed (invariant 5).
- `rt-4` execution profile: `feature-delivery` is the only `writeAllowed:true` profile and the 10
  analysis profiles are unchanged (invariant 7).
- `rt-5` bounded loop: the feed skips the "no-artifact" class and stops on empty/interrupt; the
  heartbeat does not spawn past the stop condition (invariant 6).
- `rt-6` reversibility: with `/route` unused, a representative inline path is byte-identical
  (invariant 1).
Edge cases: ambiguous classification (router escalates to the model, never silently guesses); a demand
the router routes `inline` but the specialized overseer chooses to fan out (invariant 4); an empty or
fully-conversational feed (loop exits cleanly).

## Gherkin scenarios

Phase 1 ids (`rt-1`..`rt-3`) resolve into `testing/scenarios/rt_route_dispatcher.py`; later phases
append their ids as they land.

```gherkin
Scenario: [rt-1] router decision -- exactly one route + compact brief; a security-flagged demand escalates against a benign verdict
  Given a canned demand and an injected benign triage_fn
  Then route_decision returns exactly one route (dynamic-workflow | pre-defined-profile | inline) plus a compact brief
  And a demand carrying a deterministic security flag escalates even though the injected triage_fn returned a benign verdict

Scenario: [rt-2] guardrail floor -- severity rises, never falls
  Given an injected triage_fn and a deterministic floor
  Then a floor risk flag raises escalation even when the triage_fn says no escalation
  And the triage_fn may raise severity with no floor flag, and the floor never lowers it
  And an ambiguous/empty triage escalates rather than silently guessing

Scenario: [rt-3] handoff contract -- the router->overseer brief is compact
  Given a route decision and covered-doc handles
  Then compose_brief carries handles only, no file-content dump, and stays compact

Scenario: [rt-4] execution profile isolation -- feature-delivery is the only writeAllowed:true profile
  Given the workflow-profiles registry after Phase 2
  Then feature-delivery is the only writeAllowed:true profile (overseerRole route-overseer, phases plan->implement->audit->commit)
  And the 10 analysis profiles are present and unchanged (writeAllowed:false)
  And consume_verdict normalizes a kept/rejected overseer verdict into the router's next-step state

Scenario: [rt-5] bounded loop -- skips the no-artifact class and stops on empty/interrupt; the heartbeat never spawns past the stop condition
  Given an injected triage_fn and injected stage seams (no model, no git, no real workflow)
  Then a skip:true verdict with no risk flag discards the entry and dispatch is never invoked
  And the loop stops on an empty feed and on the stop sentinel, and honors --max-demands
  And the heartbeat returns shouldResume:false past a stop condition (sentinel or empty feed)
  And an apply-merge that rolls back never invokes the commit stage and leaves a clean tree

Scenario: [rt-7] router capability panel -- classify-neutral and spawn-path-inert
  Given the router task-profile with empty triggers and empty fileGlobs
  Then harness.classify never routes any demand -- including "route"/"router"/"dispatch" wording -- to router, and the plan and security baselines are unchanged
  And the router spawn cards match the model-routing router role (sonnet/high primary, gpt-5.6-terra/high codex fallback)
  And tokenEconomy.allowedSkills and tokenEconomy.allowedMcp are both empty

Scenario: [rt-8] router rulebook + conductor-A spawn profile -- the model-driven router's rulebook lands within budget
  Given the router playbook .harness/prompts/router-playbook.md and the conductor-A spawn profile .claude/agents/router.md
  Then the playbook exists, is ASCII, and is within budget (<=60 lines and <=4800 bytes)
  And it states the three routes (dynamic-workflow, pre-defined-profile, inline), the loop-only skip class, the floor-only-raises rule, that the router never plans, that it returns STRICT JSON, and that delegate is advisory
  And the conductor-A spawn profile .claude/agents/router.md points to the playbook

Scenario: [rt-11] conductor-B honors the route -- dynamic fan-out, analysis lane, single-worker fallback, --only
  Given injected stage seams (no model, no git, no real workflow)
  Then a dynamic-workflow route whose plan-worker decomposition passes the deterministic branch gate fans out N confined branches in ONE feature-delivery workflow and the outcome records branches=N
  And a gate violation (branch count outside 2..maxWorkers, path outside the union footprint, modify overlap, empty branch) or a non-dynamic route falls back to the single-worker choreography with the reason recorded
  And a pre-defined-profile route naming an existing writeAllowed:false profile runs the analysis lane (plan -> run -> reduce; findings), never the write chain -- reduce done advances the queue, anything else escalates and stays pending
  And a write or unknown workflowProfile falls through to today's choreography, and --only restricts the loop's pull to one intake entry id

Scenario: [rt-10] per-role context diet -- the front-desk and triage router run dieted sessions (SPEC-118 v5)
  Given the router and overseer roles declare a vendor-neutral contextDiet in model-routing.json
  Then resolve_role passes the intent through and the claude chat argv realizes it: the v4 layer flags, ONE merged --disallowedTools keeping the chat floor (Bash/TodoWrite), and the reinjection-skip env
  And an engine without a diet builds a byte-compatible argv (no layer flags, lockout pair only)
  And the triage spawn splices the tool trim before the prompt without doubling the worker template's own layer flags
  And the codex adapter maps best-effort (project_doc_max_bytes=0) while openai/generic are no-ops

Scenario: [rt-9] front-desk default -- chat/GUI open on the router role's model with the front-desk prompt; the route verb is gated
  Given the chat surface (harness.py chat, which the GUI panel pipes into)
  Then run_chat's role default is router and the router role resolves sonnet/high from the routing rung
  And --role overseer (and a roleless resolution) restores opus/xhigh, proving the reversion path
  And the front-desk prompt .harness/prompts/front-desk.md is selected for the router role, is ASCII within budget (<=60 lines and <=4800 bytes), and anchors the porteiro contract (answers chitchat itself; never codes, edits, or reads project files/memories; dispatches change demands via route --task)
  And the route verb is gated in chat: single-demand route --task is read-only auto, route --loop requires confirm, and --approve-writes is human-only

Scenario: [rt-12] classifier word-boundary floor -- 'ci'/accent-saturated demands and the harness-vocabulary cluster no longer false-flag security
  Given classify matches profile triggers and riskTerms on word boundaries (re.escape + \b) against the real task-profiles.json and project riskTerms
  Then a Portuguese demand carrying 'monotonicidade'/'decisao'/'funcionar' and the word 'workflow' raises NO security flag and does not escalate
  And a demand with a genuine standalone security term (oauth jwt session, or the word password) still classifies security and escalates

Scenario: [rt-13] honest dispatch refusal -- the generic echo stub is refused, a real executor produces the command
  Given the route verb resolves a non-inline dispatch through dispatch_command, which surfaces the resolved executor
  Then resolving to the 'generic' stub prints a dispatch REFUSED line instead of a runnable echo argv
  And --executor claude produces the specialized-overseer dispatch command byte-identically to before

Scenario: [rt-14] routed-profile spawn -- the routed profile is honored on a dirty tree, not re-classified
  Given a demand the deterministic floor classifies plan and a dirty working tree
  Then spawn_command with profile_name=plan builds a prompt carrying "Task profile: plan" and classify is skipped
  And dispatch_command threads the routed profile so the produced argv says plan even though the tree is dirty, and an unknown profile raises
  And with no profile hint spawn_command still classifies the demand (byte-compat)

Scenario: [rt-15] porteiro auto-dispatch -- --dispatch launches detached; the generic stub and escalations never launch
  Given route --task ... --dispatch with launch_detached stubbed
  Then a real-executor route launches detached, prints "dispatched (detached): pid N", logs under .harness/runs/, and the launched argv is the produced spawn argv
  And --executor generic prints the dispatch REFUSED line and the launch stub is never called
  And a security-escalated demand prints the dispatch WITHHELD line pointing at the decision inbox and the launch stub is never called
```

## Validation

- Phase 0 (this spec + `.harness/handoff/plan-route-dispatcher.md`): `spec-pack
  --no-project-commands` green (this spec's `:sections` pass; `:gherkin` passes as "no gherkin
  scenarios" until Phase 1 wires the block).
- Phase 1+: `python testing/scenarios/rt_route_dispatcher.py` green for the ids landed that phase;
  the `gherkin` block added in Phase 1 resolves each `rt-*` id into that file (spec-pack `:gherkin`).
- Phase 3: `rt-5` (bounded loop) resolves into `rt_route_dispatcher.py` and is hermetic (injected
  triage + stage seams -- no model, no git, no real workflow); `route --loop --dry-run` runs the
  loop read-only; `route --heartbeat` prints a bounded resume verdict and never spawns.
- Each phase: `python scripts/harness.py --help` shows the `route` verb (Phase 1); the 10 existing
  workflow profiles unchanged (Phase 2); `ScheduleWakeup` heartbeat bounded (Phase 3); EXP-10 metric
  recorded (Phase 4).
- Reversibility check: with `/route` unused, the pre-existing scenario suite stays green (no inline
  path changed).

## Amendments

### v2 -- 2026-07-14 (SPEC-144 Phase 0+1)

- **Router capability panel.** Adds the `router` profile to `.harness/routing/task-profiles.json`:
  `risk: low`, **empty `triggers` and `fileGlobs`**, empty `tokenEconomy.allowedSkills`/`allowedMcp`,
  `compactOutput: true`, and Graphify `not-permitted` (the router triages on demand text plus the
  deterministic floor plus doc-find handles only -- invariant 3, no heavy reads).
- **Empty triggers are load-bearing.** `harness.classify` scores an empty-trigger profile at 0, and a
  0-max falls back to `defaultProfile` (`plan`), so the router can never win a classification. Adding
  it leaves every existing `classify` result and all non-`/route` behavior byte-identical (invariant 1).
- **Spawn-path-inert.** `route_loop._model_triage` builds the router spawn from
  `model_routing.resolve_role` (the `router` role: Sonnet 5 high, fallback gpt-5.6-terra high), never
  from this task-profile block. The panel is a declaration plus a consistency guard, not live plumbing.
- **Deferred to Phase 2.** The router rulebook (`.harness/prompts/router-playbook.md`), the conductor-A
  spawn profile (`.claude/agents/router.md`), and acceptance id `rt-8`.
- **Acceptance.** Declares `rt-7` (router capability panel; in the Gherkin block above); `rt-8` is
  deferred to Phase 2.

### v2.1 -- 2026-07-14 (SPEC-144 Phase 2)

- **Router rulebook.** Adds `.harness/prompts/router-playbook.md` -- the model-driven router's
  rulebook (who-you-are; the three exits + skip; the floor is a floor; MUST; MUST NOT; return
  contract). Budgeted <=60 lines / 4800 bytes (rt-8 enforced), ASCII only, and the return-contract
  JSON is copied verbatim from `route_dispatcher.triage_prompt` so the two never drift.
- **Conductor-A spawn profile.** Adds the thin `.claude/agents/router.md` (model sonnet, effort
  high, tools Read only) that points to the playbook -- the Claude vendor surface for the tier-1
  router, kept thin per the CLAUDE.md vendor-surface rule.
- **Skill pointer.** The `/route` SKILL.md gains one pointer line to the playbook.
- **Acceptance.** Declares `rt-8` (router rulebook + conductor-A profile; in the Gherkin block above).

### v2.2 -- 2026-07-14 (front-desk: chat/GUI open on the router tier)

- **Owner decision (2026-07-14).** Opening the harness GUI still talked to the overseer
  (opus/xhigh) -- the SPEC-115 `overseer` role was "what chat + the GUI open with". The owner ruled
  the chat front (GUI **and** CLI) now opens on the **router role's model** (sonnet/high, fallback
  gpt-5.6-terra/high) acting as the system's **front-desk / porteiro**: it answers chitchat,
  greetings, and everyday questions itself (SPEC-116 no-behavior-change class -> no artifact),
  answers harness-status questions through the read-only subcommand allowlist, and for any change
  demand runs `harness.py route --task "..."` and hands back the brief + specialized-overseer spawn
  command. It never plans, implements, edits, or reads project files/memories.
- **Invariant 1 narrowed.** "Byte-identical without /route" now applies to the delegated-work
  surfaces (spawns, workflows, inline flow); the chat/GUI default model+prompt deliberately change.
  `harness.py chat --role overseer` is the reversion switch back to the opus operator.
- **Mechanism.** `chat --role <role>` (default `router`) picks the routing rung role in
  `chat_setup._resolve_config` (for non-overseer roles the canonical task-profile spawn cards count
  -- rt-7 pins router == sonnet/high) and the system prompt via `chat_engines.PROMPT_BY_ROLE`
  (`router` -> `.harness/prompts/front-desk.md`; others keep `harness-operator.md`). The GUI panel
  pipes into `harness.py chat`, so it inherits the default with zero GUI change. The front-desk is
  NOT the strict-JSON tier-1 router of `router-playbook.md`; it shares that playbook's triage
  semantics but converses.
- **Route-verb gating in chat.** Single-demand `route --task` is read-only (`auto`); `route --loop`
  stays gated (`confirm`); `--approve-writes` joins `--approval-token`/`--send` as human-only, in
  both the chat gate ladder and the `deny_hitl_flags` PreToolUse hook. The Claude allowlist gets the
  narrow `route --task *` pattern, never the bare `route *`.
- **Acceptance.** Declares `rt-9` (front-desk default + prompt anchors + route gating; in the
  Gherkin block above).

### v2.3 -- 2026-07-15 (front-desk + triage run dieted sessions)

- **Cross-ref.** The front-desk chat AND the tier-1 triage spawn now run per-role dieted
  sessions — vendor-neutral `contextDiet` on the `router` (and `overseer`) roles in
  `model-routing.json`, translated by `scripts/harness_lib/context_diet.py`. Mechanism, role
  evaluation, and measurements (40.3K → 16.5K tok/turn, −59%) are owned by **SPEC-118 v5**
  (`specs/40-features/worker-live-tail.md`); acceptance is `rt-10` (Gherkin block above).
- **Structural MUST NOT.** With `keepTools: []`, the router playbook's "never read files /
  use tools" and the front-desk's "never code/read project files" stop being prose: the tool
  schemas are not in the session at all (the chat keeps only its Bash/TodoWrite floor).

### v3 -- 2026-07-15 (conductor-B honors the route: dynamic fan-out + analysis lane)

The router's three routes were emitted but not EXECUTED: `conductor_b_dispatch` ignored
`decision["route"]` (everything ran the fixed 1-plan-worker -> 1-implement-worker
choreography) and analysis-profile routes fell into the write chain. Owner decision
2026-07-15: implement both lanes; live validation is a full owner-tokened write run.

- **Dynamic fan-out (route `dynamic-workflow`).** The plan-worker packet additionally asks
  for an optional `branches: [{title, modify, create, delete}]` decomposition (slices of
  the footprint). A **deterministic branch gate** (S6-style; no model can widen it) admits
  it only when: 2..maxWorkers branches (cap = `feature-delivery.maxWorkers`, 4), no empty
  branch, every path inside the union footprint, ZERO modify overlap between branches.
  Admitted -> `_default_implement_stage` fans out N confined workers in ONE
  feature-delivery workflow (per-worker `paths` + `worker-00N:path` create/delete locks);
  refused/absent -> the single-worker choreography with the reason recorded (invariant 4
  preserved: the overseer tier still owns the final inline-vs-workers call). S2/merge/
  commit stages unchanged -- apply-merge already reduces multi-worker.
- **Analysis lane (route `pre-defined-profile`).** A verdict naming an EXISTING
  `writeAllowed:false` profile runs that workflow (`plan_workflow(profile.type,
  profile_name)` -> run -> reduce) via the injected `analysis_stage` seam: outcome
  `analyzed`, reduce `done` advances the queue (note = findings wfid), anything else
  escalates and stays pending; planning errors escalate with the reason (never guess).
  Unknown or write profiles fall through to the write choreography (today's behavior).
- **`--only <entryId>`.** `route --loop` can restrict the pull to ONE intake entry
  (controlled/targeted runs against a long oldest-first feed); composes with
  `--max-demands`.
- **Acceptance.** `rt-11` (Gherkin above) + `route_loop.demo()` additions; rt-1..rt-10 and
  the rt6 write chain stay green (seam signatures grew kwargs; injected lambdas updated).

### v4 -- 2026-07-15 (classifier word-boundary floor + honest dispatch refusal)

The router "never routed, never helped": three confirmed root causes made the front desk
useless. Owner approved the fix 2026-07-15.

- **Word-boundary trigger/riskTerm matching.** `score_profile` (triggers) and
  `project_risk_score` (riskTerms) in `scripts/harness.py` matched with plain substring
  (`term in text`), so the security trigger `ci` fired INSIDE Portuguese words
  ("monotoni**ci**dade", "de**ci**sao", "fun**ci**onar") and forced escalation via the
  risk-flag floor on nearly every Portuguese demand. Both now match on word boundaries
  (`re.search(rf"\b{re.escape(term_n)}\b", text)`); normalization, weights, tie-breakers
  and fileGlobs are unchanged. Multi-word terms ("api key", "supply chain", "rm -rf") keep
  working (the `\b` anchors the outer edges; inner spaces are literal).
- **Harness vocabulary out of the security triggers.** The SECURITY profile in
  `.harness/routing/task-profiles.json` carried non-security terms (`ci`, `cd`, `workflow`,
  `graphify`, `knowledge graph`, `dependency path`, `call path`, `architecture map`,
  `impact graph`, `concept path`, `graph report`); `workflow` -- the single most common word
  in this repo's demands -- scored security+3 on every mention. That cluster is removed; every
  genuine security term stays.
- **Honest dispatch refusal.** `route --task` without `--executor` resolved the ACTIVE
  executor (`generic`, whose template is `echo '<prompt>'`) and printed a giant echo command
  as if it were a real overseer spawn. `route_dispatcher.dispatch_command` now returns the
  resolved executor alongside the argv, and `cmd_route` prints a `dispatch REFUSED` line when
  it is the `generic` stub (re-run with `--executor claude`, or configure
  `executors.json`); a real executor keeps today's output byte-identical. `route --loop` is
  unchanged.
- **Front-desk prompt.** `.harness/prompts/front-desk.md` now dispatches change demands with
  `route --task "<the demand>" --executor claude` (the porteiro's own engine) and points
  escalations at the decision inbox (`harness.py decide` / the panel's Alerts / Decisions
  card) as well as raw `escalations`.
- **Acceptance.** `rt-12` (word-boundary floor) and `rt-13` (honest dispatch refusal), Gherkin
  block above; rt-1..rt-11 and rt-7's `oauth jwt session` security baseline stay green.

### v5 -- 2026-07-15 (owner decision: porteiro auto-dispatch + routed-profile spawn)

The front desk still acted "dumb" -- two distinct defects, neither covered by v4. Owner
approved both fixes 2026-07-15.

- **Bug A -- routed profile discarded (code bug), now honored.** `cmd_route` classified
  correctly (`plan`, via the deterministic floor with `files=[]`), but `dispatch_command`
  ignored `decision["workflowProfile"]` and called `spawn_command(demand, executor)`, which
  RE-classified via `classify(task)` with `files=changed_files()`. The `review` profile's
  `**/*` fileGlob matches ANY dirty working tree, so `review` (risk high) hijacked the packet
  (`Task profile: review` + acceptance-contract blocker + `skills=[code-review]`) for a simple
  UI change. Fix: `spawn_command` gains an optional `profile_name` -- when set it looks the
  profile up in task-profiles (unknown -> `HarnessError`) and SKIPS `classify`;
  `dispatch_command` threads it through (3-tuple return now also carries the packet-economy
  env). `cmd_route` computes the hint as `decision.workflowProfile or floor.profile`; a Phase-2
  WORKFLOW-profile name that is not a task profile falls back to the floor's task profile, and
  both-unknown falls through to today's re-classification (byte-compat). The acceptance contract
  still fires for `plan` (risk medium) -- deliberate; it is reviewer-approvable (the overseer's
  own audit phase satisfies `approvedBy: "reviewer"`). Do not relax it.
- **Bug B -- dispatch dead-end (design gap), now auto-dispatch (`--dispatch`).** The single-demand
  form PRODUCED the spawn but never executed it, and chat's `!` escape only runs `harness.py
  <args>`, never a raw `claude` command -- so nobody could dispatch from chat. Owner decision:
  the porteiro auto-dispatches. `route --task ... --executor claude --dispatch` routes AND launches
  the specialized overseer DETACHED (no human confirm) via `processes.launch_detached` (the raw
  `subprocess.Popen` lives in `processes.py`; `spawn_ratchet` blocks new subprocess sites
  elsewhere), logging to `.harness/runs/route-dispatch-<UTCts>-<slug>.log` (gitignored) and
  printing `dispatched (detached): pid N`. This OVERRIDES invariant 5's "PRODUCED, not executed"
  for the single-demand form ONLY; `--loop` is unaffected and ignores the flag. Guardrails survive
  auto-dispatch: the `generic` echo stub is REFUSED (never launched), and an ESCALATED decision is
  WITHHELD (the command prints, the owner is pointed at `harness.py decide`, nothing launches --
  the security floor must not auto-launch). Chat integration is zero-code: `("route","--task")` is
  already `auto` and the `Bash(... route --task *)` allowlist covers the trailing flag. Orphan-reaping
  of a hung detached overseer is an accepted ceiling (pid+log recorded; async-supervisor pattern
  exists if it ever matters).
- **Front-desk prompt.** Lane 3 now dispatches (`--dispatch`) and reports the route + compact brief
  + `dispatched -- log at <path>, pid <n>`; a REFUSED/WITHHELD line is relayed and pointed at the
  decision inbox. The dead-end "hand the owner the spawn command" path is deleted. rt-9 anchors and
  the ASCII / <=60-line / <=4800-byte budget are preserved.
- **Acceptance.** `rt-14` (routed-profile spawn: `spawn_command`/`dispatch_command` honor
  `profile_name` on a dirty tree, unknown raises, no-hint still classifies) and `rt-15`
  (auto-dispatch: detached launch stubbed, pid + `.harness/runs/` log + launched-argv match, generic
  refusal and escalation withhold never launch), Gherkin block above; rt-1..rt-13 stay green.

### v6 -- 2026-07-15 (packet-to-file launch: cmd.exe cannot carry the prompt argv)

First live `--dispatch` (owner-run) died instantly: the log held only cmd.exe's "The
filename, directory name, or volume label syntax is incorrect". Root cause: `claude` on
Windows resolves to the npm `claude.CMD` shim, batch files execute through cmd.exe, and
cmd.exe cannot parse a multi-line prompt as an argv element -- the exact gotcha
`chat_engines.py` already documents ("the user's free text must never be an argv
element") and workflow workers already cure via `workflow_spawn_command_for_prompt`
(packet in a file, argv carries a one-line pointer). Fix, same cure: on the `--dispatch`
launch path ONLY, `cmd_route` re-renders the spawn with `prompt_file =
.harness/runs/route-dispatch-<UTCts>-<slug>.prompt.md` -- `spawn_command` writes the full
composed packet there and substitutes the `{prompt}` argv element with
``Read `<relpath>` and execute that packet exactly.`` (gitignored alongside the `.log`).
The PRODUCED (no `--dispatch`), REFUSED, and WITHHELD paths still render the full inline
prompt -- byte-identical. rt-15 now pins the pointer argv + packet-file content
(`Task profile: plan`) and cleans up the files it writes.

### v7 -- 2026-07-15 (interactive rooms sibling: SPEC-146)

The detached `--dispatch` path had no conversational counterpart. **SPEC-146
(`specs/40-features/chat-rooms.md`)** adds interactive chat ROOMS: the front-desk
porteiro runs `route --task` (no `--dispatch`) and the chat HANDS OFF, in the same
window, to a write-capable overseer room (converse + implement + commit). It also
adds the cheap **`ui-delivery`** task profile (pt-BR/EN front-end triggers ->
`ui-overseer` room, Opus xhigh, structurally confined to the front-end surfaces);
the deterministic floor routes it `pre-defined-profile`/`ui-delivery` like any other
task profile. This spec is unchanged: `route_decision`, the deterministic floor, the
`--dispatch`/`--loop` paths, and every `rt-*` acceptance stay as-is EXCEPT `rt-15`,
whose "tela"-bearing demand now classifies `ui-delivery` (the poster child of the new
profile) instead of falling through to `plan` -- the packet pin moves from
`Task profile: plan` to `Task profile: ui-delivery`.

### v8 -- 2026-07-18 (durable route ledger + demandId: EXP-17 measurement substrate)

EXP-17 ("regret retrospectivo do porteiro") returned **insufficient-data** for a
STRUCTURAL reason the probe itself states: route events are TRANSIENT (the SPEC-137
gate truncates `events.jsonl`) and the triage / dispatch / outcome rows shared NO
correlation id, so no per-demand trajectory could be reconstructed. Owner directive
(2026-07-18): build the measurement substrate and re-run.

- **Durable route ledger.** `scripts/harness_lib/route_ledger.py` is the single-writer,
  append-only twin of the transient route events -- the N2/escalations survival pattern
  applied to routing. It lives at `.harness/state/route-ledger.jsonl` (class B: a
  born-at-runtime, absence-tolerant internal journal, mirrored whole to the private
  state home by `tools/state_home_sync.py`, whose `SYNC_PATHS` already covers
  `.harness/state`). `record(root, phase, payload)` appends `{phase, at, **payload}` for
  phase in {triage, dispatched, withheld, done} and **NEVER raises** -- routing must not
  break on a ledger failure (errors are swallowed with a stderr one-liner).
  `read_ledger` and `backfill_from_logs` (an idempotent one-time fold of surviving
  `route-dispatch-*.log` HARNESS_RESULT tails into outcome-only `done` rows) round out
  the module.
- **One id, everywhere.** `demand_id(demand) = "route-" + sha256(demand)[:8]` is EXACTLY
  the existing withheld idempotent id form (the `cmd_route` `esc_id`; by construction the
  withheld escalation id IS the demand id). `cmd_route` records `triage`, `withheld`, and
  `dispatched` rows keyed by `demandId`, and adds the same `demandId` key to the
  `route_triage` / `route_withheld_escalation` / `route_dispatched` EVENT payloads
  (additive) so event-side tools can join WHILE the events survive.
- **Events vs ledger (the split).** Events remain the TRANSIENT VIEW (gate-truncated,
  count-level, unkeyed); the ledger is the DURABLE MEASUREMENT SUBSTRATE (survives the
  wipe, keyed per demand). The `route_loop` `route_demand_done` emit records a `done` row
  too, keyed by `entryId` -- the raw demand text (from which `demand_id` derives) is not
  threaded into that EXP-10 hook, so the loop's done rows join on `entryId` rather than
  `demandId` (an accepted, reported limitation; the CLI `cmd_route` path is fully
  demandId-keyed).
- **Probe upgrade.** `testing/probes/exp17_route_regret_probe.py` stays ADDITIVE (every
  published metric/line preserved) and, when the ledger is non-empty, folds the surviving
  logs and prints a `corpus: ledger (keyed)` section: joinable demands, per-route outcome
  distribution (keyed triage<->done), and reroute count. An empty ledger falls back to the
  existing `corpus: events/logs (count-level)` line.
- **Acceptance.** `rl_route_ledger.py` (rl-1 module round-trip + keyed join, rl-2
  idempotent backfill + never-raises, rl-3 source pins); `rt-1..rt-18`, `rht-1`, and the
  probe self-check stay green.

### v9 -- 2026-07-18 (route tuple pinned on the records: C13/A2 comparability substrate)

Article 3.5/SF-3b (C13): a route is a VERSIONED TUPLE, not a bare effort label.
`{vendor, model, effort, taskProfile, topology, writeAllowed, sandbox, harnessSha,
adapterSchema, at}` -- an effort label ("high", "xhigh") is not comparable BETWEEN
vendors without the surrounding pin. Trigger A2 ("a 2nd vendor in production in the
rooms") is REACHED: rooms have been multi-vendor since 925daea. This amendment is
ADDITIVE + OBSERVATIONAL -- no consumer changes behavior on the tuple; it exists so
future C3VR comparability and drift detection have a real substrate.

- **The builder.** `scripts/harness_lib/route_tuple.py` is pure stdlib:
  `route_tuple(*, executor, model=None, effort=None, task_profile=None, topology,
  write_allowed=False, root)` returns the tuple dict. `topology` is one of
  {`workflow-worker`, `detached-dispatch`, `room`, `inline`}. `sandbox` is DERIVED
  from vendor + writeAllowed -- codex maps writeAllowed to `workspace-write`/`read-only`
  (its `--sandbox` flag), claude confines via the `allowedTools-ceiling`, an HTTP
  open-model worker has `none` (no fs tool). `harnessSha` is the short git HEAD sha,
  read via `processes.run_quiet` (the ONE git touch in the builder) and **fail-open
  "unknown"** on a git-less root or any error; `adapterSchema` is the `schemaVersion`
  of `.harness/routing/executors.json`, **null** when unreadable. Absent fields
  (model/effort/taskProfile unresolved at the call site) stay **null, never invented**.
- **Where it is stamped (additive, 2 points).** `cmd_route`'s durable `dispatched`
  ledger row gains `tuple` (vendor=resolved executor, taskProfile=profile hint,
  topology=`detached-dispatch`, writeAllowed=False); `run_one_worker`'s
  `workflow_worker_started` worker event gains `tuple` (vendor=executor, the worker's
  taskProfile, its writeAllowed, topology=`workflow-worker`). The async workflow twin is
  NOT wired in this leg (accepted, reported deviation). Room-session start has no single
  event/record emission point (the `enter_room` handoff is a user-facing `say()` in
  `chat_operator.py`, out of this footprint) -- so no room tuple is emitted here
  (reported deviation, nothing improvised).
- **Acceptance.** `rtp_route_tuple.py` (rtp-1 builder purity: full shape, null-safe
  fields, vendor sandbox matrix, sha fail-open on a git-less root; rtp-2 source pins on
  both wire points); `rt-1..rt-18`, `rl-*`, `rht-1`, and the spawn-ratchet stay green.

### v10 -- 2026-07-18 (router scores + predictedP on the ledger: route regret + ECE enabler)

R4 (`construct-metrics.md`) blocked route regret + ECE + RF.1 phase 2 as "needs-new-state"
for ONE missing field: the router's predicted probability was never persisted, so no
prev-vs-realized calibration could be computed. This amendment persists it. ADDITIVE and
never load-bearing -- no route DECISION changes, `record()` still swallows, and old rows
with neither field stay valid.

- **The helper.** `route_ledger.normalized_predicted_p(scores, chosen_profile) -> float | None`
  is pure stdlib and deterministic: the R4 pre-registered `predictedP =
  score(chosen_profile) / sum(scores.values())` when `sum > 0`, else `None`. It NEVER
  divides by zero -- an empty/all-zero score dict, a missing chosen profile, or any
  non-numeric value yields `None`. `scores` are the `harness.classify` per-profile scores
  (keyed by profile name); `chosen_profile` is the classifier's picked profile
  (`floor["profile"]`). The value is always in `[0,1]` (classifier scores are non-negative).
- **Where it is persisted (additive, 2 fields).** The `route_loop` `route_demand_done`
  emit's durable `done` row (`_demand_event`) gains `scores` (the classify passthrough) and
  `predictedP` (the helper on `floor`). That row is entryId-keyed and NOT join-able to the
  demandId triage rows, so keeping `predictedP` alongside the realized `outcome` in ONE row
  is what the ECE probe needs (prediction + realized, no cross-row join). A bad/absent floor
  degrades to empty `scores` + `null` predictedP -- never an error.
- **Reported deviation (footprint).** The CLI `cmd_route` `triage` row -- the plan's stated
  first-choice site -- lives in `harness.py`, OUTSIDE this leg's `route_ledger` / route-loop
  footprint. Per the plan's "if record is called from outside, pin and report" rule it was
  NOT edited here; wiring the CLI triage row with the same helper is a follow-up. The
  `done`-row landing is the plan's Q2-sanctioned alternative.
- **Acceptance.** `rl_route_ledger.py` `rl-4-scores-persisted` (helper formula + null-on-sum=0
  + range, a done row round-trips `scores`/`predictedP` matching the helper, the kill switch
  `HARNESS_ROUTE_LEDGER_DISABLE=1` is honored, and a source pin that `_demand_event` threads
  both fields); `route_ledger.py` self-check and `rl-1..rl-3` stay green.

### v11 -- 2026-08-01 (conductor-B refuses to run under a gate-hold)

`route_loop.run_loop` (conductor-B) dispatches workflows, commits, and calls
`intake_queue.decide()` -- all writes the SPEC-137 gate protects. Under a gate-hold the tree is
swapped to materialized HEAD, so those writes land on the wrong state and are discarded on
release, while the loop still reported `committed`/`analyzed`/`skipped` and left the entry
pending (its per-run `seen` set then re-pulled it next run). `decide()` already refuses under a
hold (R1, `intake_queue.py`), but the loop DISCARDED the held return at all three call sites, so
the refusal was invisible. This brings conductor-B into compliance with the
`delegation-cost-trends.md` v5.1 invariant ("held writes REFUSE VISIBLY; `common.gate_holding` is
the SINGLE predicate for every enforcement point").

- **The guard.** `run_loop` checks `gate_holding(root)` at entry (before the lock and the drain
  loop) and, when the tree is held, returns `{held: True, stopReason: "gate-hold", demands: 0,
  results: []}` with a note -- a visible refusal, never a false success. `dry_run` is NOT exempt:
  the loop emits per-demand telemetry (`_emit` -> `append_event`) unconditionally in every
  branch and reads a stale HEAD tree, so a "preview" under a hold both writes discarded events
  and reads the wrong state. Refusing the whole run is the honest behavior.
- **Not a nucleo regression.** Pre-diff, a `decide()` write under a hold was discarded on release
  anyway, so the entry already ended up pending; this closes a PRE-EXISTING robustness gap -- the
  loop no longer misreports the outcome, and it stops doing the dispatches/commits the hold exists
  to prevent.
- **Acceptance.** `rt_route_dispatcher.py` `rt-5-gate-hold` (under a synthetic
  `.harness/runs/gate-hold/`, a non-dry-run loop returns `held`/`gate-hold`, never invokes
  dispatch, and leaves the entry pending; a dry_run also refuses). Mutant: disabling the guard
  lets the loop dispatch and re-report `committed` while the entry stays pending -> RED.
