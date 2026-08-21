# Chat contract hardening — tail batch (`rct`)

Status: proposed 2026-07-13 (acceptance: `testing/scenarios/rh_chat_tail.py`).

Intake (SPEC-116 door NEW): spec-recovery tail batch, rec-chat-9..17,19 — the
remaining shipped-but-untested chat rules across the operator REPL, its live HUD,
the panel chat bridge, and the Claude engine's telemetry/watchdog. This extends
`chat-contract-hardening.md` (rec-chat-4..8) with the same offline discipline:
pure builders and stateful objects driven via `__new__` object surgery with a
captured say/print seam, one stubbed `subprocess.Popen` (bridge session env; the
turn watchdog), and — for the two rules whose logic is inline in `run_chat` with
no callable helper — a function-scoped `inspect.getsource` pin on the exact
guard/emit expression. No engine binary is spawned, no HTTP is made, the repo is
never mutated.

## Goal

The tail chat contracts are permanently exercised: the live plan HUD flushes a
finished plan exactly once and the plain terminal prints only step transitions;
a mid-session target switch re-resolves the engine only when routing actually
changed and nothing was pinned; the panel bridge threads a session dimension
into the child, resets a stale replay cursor, and stays quiet under the panel;
the Claude engine reports a per-turn cost delta and enforces a turn watchdog; and
one plan-mode turn co-emits both plan frames while the emoji chips degrade to
ASCII when the console cannot encode them.

## Applicability

Applies to `scripts/harness_lib/chat_hud.py` (`Hud.set_plan` `333-345`, `_glyphs`
`41-49`), `scripts/harness_lib/chat_operator.py` (`run_chat.on_plan` `485-500`,
`_reresolve_needed` `327-336` and its caller `604-625`, `_read_paste_block` /
`_finish_block` `102-132`, `format_tool_line` `344-354`, the `plan-steps` /
SPEC-133 `plan` emits `486, 771-772`), `scripts/harness_lib/ui_chat_bridge.py`
(`ChatBridge.start` `88-110`, `read_since` `68-82`), and
`scripts/harness_lib/chat_engines.py` (`ClaudeEngine._telemetry` `236-265`, the
`send` turn watchdog `203-227`). Coverage is offline: the argv/telemetry builders
and the bridge cursor are pure and driven directly; the two `run_chat` inline
guards (the co-emit pair and the transition-only print) have no callable helper
and are pinned by source. It does not cover the real ANSI drawing, a live claude
process, or the SSE transport.

## Requirements / invariants (numbered, testable)

1. **Plan HUD flushes once; the plain terminal prints transitions.**
   `Hud.set_plan` flushes an all-completed plan (`all(status == "completed")`)
   into the scrollback EXACTLY once via `say` as a `plan complete (n/n):`
   checklist and drops the bottom rows (`self._plan = []`); a plan carrying any
   `in_progress`/`pending` step is kept as bottom rows (`self._plan = steps`)
   and says nothing. The non-HUD path in `run_chat.on_plan` prints only the
   current step TRANSITION (`> plan (done/total): <current>`), never the
   rewritten list (`chat_hud.py:333-345`, `chat_operator.py:485-500`).
2. **Target-switch re-resolve gate.** `_reresolve_needed(cfg, new_cfg)` returns
   True only when the re-resolved engine/model/effort differs AND the current
   model/effort source is neither `flag` nor `session`; an identical config or a
   flag/session pin returns False. `run_chat` rebuilds the engine on a
   mid-session `/repo` switch only under this gate — a `perTarget` routing
   binding never silently overrides a deliberate pin (`chat_operator.py:327-336,
   604-625`, SPEC-114 R37 Fix A).
3. **Bridge/session riders.** `ChatBridge.start` adds `HARNESS_CHAT_SESSION` to
   the child env only when a session id is handed in (the additive cost-ledger
   dimension, P2); `read_since` resets a stale cursor (`cursor > total`, e.g. a
   restarted bridge) to a full replay from history; the P5 paste hints (`paste
   mode …`, `[captured N pasted lines]`) are suppressed under
   `HARNESS_CHAT_EVENTS=1` (`ui_chat_bridge.py:88-106, 68-82`,
   `chat_operator.py:102-132`).
4. **Claude telemetry fold + turn watchdog.** `ClaudeEngine._telemetry` reports
   `total_cost_usd` as a per-turn delta from the previous cumulative value and
   falls back to the raw cost when the delta is negative (a fresh `--resume`
   session lowers the cumulative); `ClaudeEngine.send` arms a `TURN_TIMEOUT`
   watchdog that kills the child and returns the timeout string
   (`chat_engines.py:236-248, 203-227`).
5. **Plan frames co-emit; emoji probe degrades.** One plan-mode turn in
   `run_chat` emits both the `plan-steps` frame (TodoWrite HUD) and the SPEC-133
   derived `plan` approval frame; `format_tool_line` and `chat_hud._glyphs` fall
   back to `[tool]` / ASCII glyphs when the console encoding rejects emoji
   (`chat_operator.py:486, 771-772, 344-354`, `chat_hud.py:41-49`).

## Gherkin scenarios

```gherkin
Feature: chat contract hardening — tail

  Scenario: [rct-1] the plan HUD flushes a finished plan once and drops the rows
    Given a live plan with unfinished steps and then an all-completed plan
    When the HUD receives each update
    Then the unfinished plan stays as bottom rows and says nothing
    And the completed plan is flushed once as a checklist and the rows are dropped

  Scenario: [rct-2] a target switch re-resolves only an unpinned, changed engine
    Given a mid-session target switch
    When the re-resolved routing differs and the model/effort were not pinned
    Then the engine is rebuilt, and it is left alone when identical or pinned

  Scenario: [rct-3] the panel bridge threads a session, resets a stale cursor, and stays quiet
    Given a chat bridge started with and without a session id
    When a stale replay cursor and a panel paste both occur
    Then the session env rides only the session start, the cursor replays in full, and the hints are suppressed

  Scenario: [rct-4] the Claude engine reports a delta cost and enforces a watchdog
    Given multi-turn cumulative cost payloads and a hung child
    When telemetry is folded and a turn exceeds the timeout
    Then each turn reports its delta with a raw fallback, and the child is killed

  Scenario: [rct-5] plan frames co-emit and emoji chips degrade to ASCII
    Given a plan-mode turn and a console that cannot encode emoji
    When the turn ends and a tool chip is rendered
    Then both plan frames are emitted and the chip degrades to a text label
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Flush a finished plan once, drop the rows | `chat_hud.py:334-342` ("a FINISHED plan flushes once as a checklist into the scrollback and drops the rows") — rewriting the whole list every TodoWrite update is human-factors spam |
| Non-HUD prints transitions, never the list | `chat_operator.py:480-500` (`on_plan` says only the current in_progress step on a transition; a plain terminal has no bottom region to rewrite) |
| Rebuild only on a changed, unpinned engine | SPEC-114 R37 Fix A; `chat_operator.py:329-336` — `flag`/`session` sources (CLI `--model`, `/config`, `/engine`) are deliberate pins a `perTarget` binding must not silently override |
| Session env is additive | P2 cost-ledger session dimension (`ui_chat_bridge.py:100-102`) — absent when no session is handed in |
| Stale cursor resets to full replay | flake root cause 2026-07-11 (`ui_chat_bridge.py:50-54, 70-71`): a restarted bridge lowers `total`, so a cursor beyond it must replay from 0 or the transcript vanishes |
| Cost reported as a per-turn delta | E2E 2026-07-10: turn1 $0.033 → turn2 $0.057 under `--resume` cumulative billing (`chat_engines.py:244-245`); negative delta ⇒ fresh session ⇒ raw fallback |
| A turn watchdog kills a hung child | `chat_engines.py:36, 203-227` — a chatty/stuck child must not deadlock the REPL; `TURN_TIMEOUT` is env-tunable |
| Both plan frames co-emit; emoji degrades | SPEC-133 derived `plan` event (`chat_operator.py:769-772`) rides the same plan-mode turn as the TodoWrite `plan-steps` frame (`486`); encode-probe fallback (`chat_hud.py:42-49`, `chat_operator.py:348-352`) keeps a cp1252/ascii console readable |
| Door NEW (not amendment) | no existing spec documents these tail chat contracts (rec-chat-9..17,19: shipped, no spec, no scenario) |
| Evidence | code line ranges above; sibling batch `testing/scenarios/rh_chat_contracts.py` (rec-chat-4..8) |

## Plan-vs-code corrections

Pinned against the source, as the overseer plan directed:

- **rct-1 has one callable half.** The plan says "drive the stateful Hud object …
  with scripted plan updates + a captured say/print seam" for both the flush and
  the transition-only behavior. Only the HUD half is a callable object method
  (`Hud.set_plan`), driven here via `__new__` with `live=False` so no terminal,
  ANSI, or `git` subprocess is touched. The transition-only print lives in the
  `on_plan` closure INSIDE `run_chat` with no callable helper (identical to the
  sibling batch's rhc-4/rhc-5), so it is pinned by a function-scoped source
  assertion on the exact `emit`/guard/`say` expressions.
- **rct-2 fixtures are inline, the caller has no entry point.** The plan says
  "promote the existing self-check into scenario checks (reuse its fixtures if
  importable; else replicate minimally)". The fixtures live inline in
  `chat_operator.__main__`, not an importable function, so they are replicated
  minimally; and the re-resolve caller (`604-625`) needs the full REPL loop, so
  its wiring is pinned by a source assertion that `run_chat` gates the rebuild on
  `if _reresolve_needed(cfg, new_cfg):`.
- **rct-3 bridge env via the Popen seam.** The session dimension is captured
  through a stubbed `subprocess.Popen` (the `env` kwarg) rather than by spawning
  `harness.py chat`; `read_since`'s reset branch is driven directly on an
  in-memory `ChatBridge`; and the P5 guard is exercised on the callable
  `_read_paste_block` AND `_finish_block` (both in the cited `102-132`), the
  latter without needing to stub `input()`.
- **rct-5 co-emit is inline.** Both plan emits live in `run_chat` (the `plan-steps`
  frame in `on_plan`, the SPEC-133 `plan` frame right after `turn-end`) with no
  callable helper, so the co-emit is a source pin; the emoji fallback IS driven —
  `format_tool_line` and `_glyphs` are pure and probed by swapping the captured
  stream's `encoding`.

## Ceilings (upgrade paths)

The rct-1 transition-only pin and the rct-5 co-emit pin assert guard text, not
runtime behavior; if `run_chat`'s `on_plan` closure and its plan-frame emits are
ever extracted into callable helpers (a `chat_operator` shrink), upgrade those
two pins to drive the helpers directly with a fake session state and drop the
`getsource` assertions. The watchdog check uses a 5s hard ceiling on its hanging
stub so a broken kill path fails loudly instead of hanging the gate.

## Test strategy

- Behaviors to verify: one-shot plan flush + row drop and transition-only print
  (rct-1); the four-case re-resolve truth table + caller wiring (rct-2); session
  env additivity, stale-cursor full replay, P5 hint suppression (rct-3); the
  cumulative→delta fold with negative-delta raw fallback + the turn watchdog kill
  (rct-4); the plan-frame co-emit + emoji-to-ASCII degrade (rct-5).
- Edge cases: an empty/mixed plan says nothing and keeps the rows; a flag AND a
  session pin both veto the rebuild; a cursor exactly at `total` returns nothing;
  a negative cost delta returns the raw cumulative; an `ascii` vs `utf-8` console
  encoding flips the chip icon and glyph set.
- Regression risks: a silent loss of the re-resolve pin (a `perTarget` binding
  overriding a human pin) or the watchdog (a hung turn deadlocking the REPL) is a
  behavior regression with no failing check — hence the permanent scenario.
- Coverage impact: enforced via `testing/scenarios/rh_chat_tail.py` (stdlib-only,
  offline, repo read-only).

## Validation

- `python testing/scenarios/rh_chat_tail.py` — rct-1..rct-5 green.
- `python testing/scenarios/rh_chat_contracts.py` — the sibling rhc batch still
  green (shared module surfaces).
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.

## Amendments

(none yet)
