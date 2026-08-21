# SPEC-146 — Chat rooms: porteiro -> overseer room + a cheap ui-overseer

Status: SPEC-146, proposed 2026-07-15 (acceptance: `testing/scenarios/rm_chat_rooms.py`).

Intake (SPEC-116 door NEW, owner decisions 2026-07-15): the front-desk porteiro
(SPEC-144 v2.2) could only DISPATCH change demands to a detached AFK worker — there
was no way to converse with the specialist while it worked. The building metaphor:
the porteiro routes you to the right room, then you talk to the specialist directly,
in the same window. Sibling of the detached `route --task ... --dispatch` path
(SPEC-144 v5/v6), which stays for AFK.

## Goal

An in-chat handoff: the chat (CLI REPL + GUI tab, one code path) opens on the
porteiro (router role, sonnet/high). On a change demand the porteiro runs
`route --task` and the chat HANDS OFF to a specialized overseer ROOM in the SAME
window — a different role with a write-capable model/effort/prompt/toolset. The
owner converses (approves plans, answers, intervenes); the overseer implements and
commits (SPEC-137 stays structural); then a farewell + `/back` returns to the
porteiro, and `/room` re-enters a live room with context intact. A new cheap
`ui-delivery` task profile routes plain-language front-end demands to a
`ui-overseer` room (Opus 5 xhigh, structurally confined to the front-end
surfaces); everything else enters the fable `route-overseer` room.

## Applicability

`scripts/harness_lib/chat_operator.py` (the `run_chat` REPL, its `/room` /`/back`
commands, the `route_handoff` handoff detector, `_switch_room`) and
`scripts/harness_lib/chat_engines.py` (`PROMPT_BY_ROLE`, `UI_SURFACES`,
`room_tool_patterns`, the send-time room allowlist). The room roles + models live in
`.harness/routing/model-routing.json` (`ui-overseer`, existing `route-overseer`);
the `ui-delivery` task profile in `.harness/routing/task-profiles.json`; the shared
room prompt in `.harness/prompts/room-overseer.md`. It does NOT change the detached
`--dispatch`/`--loop` paths, the router's classify/deterministic-floor logic, or any
non-chat spawn. Rooms are claude sessions; codex/openai fall back to prompt-level.

## Requirements / invariants (numbered, testable)

1. **Opt-in / reversible.** Absent a `route --task` handoff, the chat is
   byte-identical to today: `room_tools` defaults to `[]`, so the send-time
   allowlist is unchanged, and `/room`/`/back` are no-ops until a room is entered.
2. **Shared room prompt.** `route-overseer` and `ui-overseer` both resolve to
   `.harness/prompts/room-overseer.md` (converse + implement + commit; complexity
   ladder; SPEC-137 commit ritual; farewell + `/back`). ASCII, <=60 lines, <=4800
   bytes.
3. **Complexity-tiered write authorization (by prompt).** Trivial demand -> proceed
   narrating (owner watching); non-trivial / unsure -> compact plan first, WAIT for
   explicit in-chat approval.
4. **Structural UI confinement.** The `ui-overseer` room's Edit/Write patterns are
   ALL path-scoped to `UI_SURFACES` (no bare Edit/Write); `route-overseer` gets bare
   Edit/Write. Both carry harness/pytest/scenario Bash + git staging and NEVER
   `git push`; non-room roles get `[]`.
5. **Handoff is pure + guarded.** `route_handoff` fires only for a porteiro `Bash`
   `route --task` (not `--dispatch`) whose printed decision is a real, non-escalated
   route; inline / escalated / `--dispatch` / non-Bash never open a room (the
   porteiro relays those itself).
6. **ui-delivery routing.** The pt-BR/EN front-end triggers classify `ui-delivery`
   (files=[]) -> `route_decision` routes `pre-defined-profile`/`ui-delivery` -> the
   `ui-overseer` room; the plan/security baselines and the ui-validation lane are
   unchanged.
7. **Role rung wins in a room.** A room resolves through the routing role rung with
   empty prefs, so a saved model/effort pref or `--model` never pins a room off its
   role (`ui-overseer` -> opus/xhigh, `route-overseer` -> fable/high).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Two engine instances = two free resumable sessions (rooms live in one window) | `chat_engines.py` `ClaudeEngine.session_id`; SPEC-114 R19 |
| Path-scoped `Edit(<glob>)` structurally confines the UI room | Step-1 live probe 2026-07-15 (scoped-allow / out-of-scope-deny honored) |
| Porteiro prints the decision JSON first, so the capped tool-result digest parses | `harness.py` `cmd_route`; `stream_json.DIGEST_CAP` (2000) |
| Cheap Opus-xhigh UI room over fable for simple screen demands | owner decision 2026-07-15 (fable too expensive for tela/botao/cor) |
| Rooms are claude; codex/openai prompt-level | `room_tools` read only by `ClaudeEngine.send` |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: Chat rooms — porteiro hands the owner into an overseer room

  Scenario: [rm-1] the two overseer rooms share one budgeted room prompt
    Given the room-overseer prompt and PROMPT_BY_ROLE
    Then route-overseer and ui-overseer both map to room-overseer.md
    And it is ASCII within budget and anchors plan/approval/commit//back + the ui-overseer confinement

  Scenario: [rm-2] route_handoff opens a room only for a real, non-escalated route
    Given a porteiro route --task tool result carrying a decision JSON
    Then a ui-delivery route hands off to the ui-overseer room and a plan route to the default route-overseer
    And inline, escalated, --dispatch, and non-Bash results open no room

  Scenario: [rm-3] the room toolsets confine writes and never push
    Given room_tool_patterns for each role and a room-carrying engine
    Then ui-overseer Edit/Write are all path-scoped, route-overseer gets bare Edit/Write, neither can git push, a non-room role gets []
    And the room engine splices its patterns into the send-time allowlist while a roomless engine's allowlist is byte-identical

  Scenario: [rm-4] a room resolves its role's model pin
    Given the routing rung with empty prefs
    Then role ui-overseer resolves opus/xhigh and route-overseer resolves fable/high

  Scenario: [rm-5] a plain-language front-end demand routes ui-delivery
    Given the pt-BR demand "muda a cor do botao do painel"
    Then classify returns ui-delivery and route_decision routes pre-defined-profile/ui-delivery
    And the plan/security baselines and the ui-validation lane are unchanged

  Scenario: [rm-6] the REPL wires the room handoff inline
    Given the run_chat source
    Then it carries the /back and /room branches, the route_handoff call, the ready-event role, and the queued auto-turn
```

## Ceilings (upgrade paths)

- **Bash not path-confined in a room** (git add/commit reach anything): the Edit/Write
  scoping + the room prompt + SPEC-137's structural gate + the watching owner are the
  layers; add a Bash path guard if a room is ever run unattended.
- **Rooms do not survive a process restart** (in-memory `rooms` dict); persist the
  session map if resuming rooms across restarts is ever needed.
- **Codex rooms are prompt-level only** (`room_tools` is claude-read); wire a codex
  sandbox-mode confinement if a codex room needs structural limits.
- **Ctrl+C during a room turn exits the chat** (existing REPL behavior, unchanged).
- **A `/repo` target switch inside a room re-resolves the boot role** (an accepted
  edge); `/back` first if you want to keep the room.

## Test strategy

- Behaviors to verify: shared prompt + budget (rm-1); handoff matrix (rm-2); toolset
  confinement + send-time splice + roomless byte-compat (rm-3); routing role pins
  (rm-4); ui-delivery classify/route + baselines (rm-5); inline REPL wiring (rm-6).
- Edge cases: --dispatch and non-Bash never open a room; escalated/inline relayed by
  the porteiro; empty prefs so the role rung wins.
- Regression risks: the `_wire` refactor of `run_chat` (rh_chat_contracts /
  rh_chat_tail source pins stay green); rt-15's routed profile is now `ui-delivery`.
- Coverage impact: enforced via `rm_chat_rooms.py`.

## Validation

- `python testing/scenarios/rm_chat_rooms.py` (checks `rm-1`..`rm-6`) + `spec-pack`
  green (this spec's `:sections` and `:gherkin` mapping into `rm_chat_rooms.py`).
- `python testing/scenarios/rt_route_dispatcher.py` green (rt-15 now routes
  `ui-delivery`; rt-7/9/10/12 baselines unchanged).
- `python scripts/harness.py route --task "muda a cor do botao do painel"` ->
  `pre-defined-profile`/`ui-delivery`; `--role overseer` still restores the operator.
- Regression: `rh_chat_contracts.py`, `rh_chat_tail.py` (run_chat source pins survive
  the `_wire` refactor); `protected-files` fixture green.

## Amendments

(none yet)
