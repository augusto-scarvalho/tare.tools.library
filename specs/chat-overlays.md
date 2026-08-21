# Chat overlays — tool-call chips + expand-to-inspect (`chat-tool-chips`)

Status: Active (v3 — chat-gate-tracker amendment, 2026-07-14; acceptance:
testing/scenarios/ct_tool_chips.py + testing/scenarios/cp_plan_hud.py +
testing/scenarios/cgt_chat_gate_tracker.py).

Intake (SPEC-116 door NEW): request = "tool highlighter nos chats, algo que
resuma a tool e mostre um ícone ao lado, dando a opção de inspecionar
expandindo a mensagem na GUI (se possível, fazer no CLI também)"
(`docs/roadmap/chat-overlays.md` Request 1). Covered-check: today a tool call
is one plain `🔧 name arg` line in the panel and INVISIBLE in a plain CLI
turn; full input and all output are dropped at the parser. Decision: **NEW**.
SLICE: Request 1 (MVP + output inspector + CLI parity) ONLY — `chat-plan-hud`
(the SPEC-133 `plan` frames grew the capture surface), `chat-gate-tracker`
and `codex-stream-parity` stay OPEN as their own backlog rows; this spec is
the surface they will amend.

## Goal

Every mid-turn tool call becomes an inspectable unit on both chat surfaces:
the panel renders a native `<details>` chip (emoji icon + name + primary arg;
expanding shows the capped input digest and, once the matching `tool_result`
arrives, the capped output); the CLI prints a collapsed dim activity line per
call and `/tool [n]` lists/inspects the current turn's calls from an
in-memory buffer. Nothing is persisted; digests are capped at the producer.

## Applicability

Applies to `scripts/harness_lib/stream_json.py` (`tool_descriptor` grows
`id`/`input_digest`; new `tool_result_descriptor`; `parse_chat_stream`
`on_tool_result`), `chat_engines.ClaudeEngine.send` (threads the getattr-
guarded callback — codex/openai/manual unaffected), `chat_operator.run_chat`
(extended `tool` emit + new `tool-result` emit + per-turn `tool_log` + CLI
line + `/tool`), and the PAGE (`handleEvt` chip + `tool-result` case + CSS).
GUI writes no canonical state; the overlay is render-only.

## Requirements / invariants (numbered, testable)

1. **Back-compatible descriptor.** `tool_descriptor` keeps `{name, arg}`
   byte-identical for existing callers and adds `id` (tool_use id) and
   `input_digest` — compact JSON capped at `DIGEST_CAP` with an honest
   `…[truncated]` marker.
2. **Results ride the same pipe.** `parse_chat_stream(on_tool_result=…)`
   fires `{id, digest}` per `tool_result` block in `user` events (string and
   block-list content shapes both reduce to capped text); no second copy of
   the stream is stored.
3. **Event vocabulary.** The bridge emits `tool` (now with `id` +
   `inputDigest`) and `tool-result` (`id` + `digest`) as `\x1e` frames —
   additive fields, older consumers unaffected.
4. **GUI chip.** The panel renders a `<details class="tchip">` chip per call
   (icon map, model attribution prefix preserved); the expanded body shows
   the input digest and an output section filled by id when the result
   arrives; chips reset with the transcript (SSE replay rebuilds them).
5. **CLI parity.** Outside the panel bridge, each call prints one collapsed
   dim line (`format_tool_line`, emoji with encode-probe fallback); `/tool`
   lists the CURRENT turn's calls and `/tool <n>` prints one call's
   input+output (`format_tool_entry`) from a buffer cleared at turn-start
   and never persisted.
6. **Engines beyond claude degrade silently.** The callback is getattr-
   guarded; codex/openai/manual set nothing and behave exactly as before
   (codex chips arrive with `codex-stream-parity`).

## Gherkin scenarios

```gherkin
Feature: chat tool chips (expand-to-inspect)

  Scenario: [ct-1] the descriptor carries an id and a capped input digest
    Given a tool_use block with a 5000-char input
    When tool_descriptor reduces it
    Then name and arg are unchanged, id is present and the digest ends with
      the truncated marker within the cap

  Scenario: [ct-2] tool results fire with their matching ids
    Given a stream with one block-list result and one plain-string result
    When parse_chat_stream runs with on_tool_result
    Then both fire in order as {id, digest} with the capped text

  Scenario: [ct-3] the CLI surface is a line plus /tool inspector
    Given the pure formatters and the REPL surface
    When a call renders collapsed and /tool n expands it
    Then the line carries icon+name+arg, the entry shows input and output
      (or none captured), /tool is in HELP_TEXT and the buffer clears at
      turn-start

  Scenario: [ct-4] the pipe is wired end to end
    Given the engine and PAGE sources
    Then ClaudeEngine threads on_tool_result into the parser and the PAGE
      renders tchip details and fills tchip-out by id on tool-result
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Um pipe de eventos, dois renderers (chip GUI ≡ linha+`/tool` CLI) | roadmap `chat-overlays.md` unifying design decision |
| `<details>` nativo, sem máquina de estado JS | roadmap MVP item 3; CSP self-contained (emoji, sem assets) |
| Digest capado NO PRODUTOR com marcador honesto | roadmap risk #1; handles-not-bodies (CQ round) |
| Buffer por turno em memória, nunca persistido | roadmap increment 3 ("no state file"); render-only invariant |
| Callback getattr-guarded (só claude consome) | precedente `on_activity` (`chat_engines.py`); codex fica para codex-stream-parity |
| Emoji com fallback por encode-probe no CLI | `chat_hud._glyphs` pattern; legacy Windows consoles |

## Test strategy

- Behaviors: descriptor cap/id + back-compat (ct-1); result firing for both
  content shapes (ct-2); pure formatters + HELP/clear surface (ct-3); engine
  + PAGE wiring source-assert (ct-4). The stream_json module self-check
  gained the same canned coverage (producer-level regression net).
- Edge cases: result for an unknown id (GUI: no chip → ignored; CLI: no
  buffer match → dropped); empty input → "(no input captured)"; `/tool` with
  an empty buffer says so.
- Regression net: qol_panel_chat + m5_ui_panel keep the untouched chat
  behaviors green; the ui_e2e suite exercises the live panel (a dedicated
  canned-chip e2e flow rides the existing suite as a follow-up).
- Coverage: deterministic, stdlib-only — `testing/scenarios/ct_tool_chips.py`.

## Validation

- `python testing/scenarios/ct_tool_chips.py` — ct-1..ct-4 green.
- `python testing/scenarios/cp_plan_hud.py` — the v2 plan-hud scenarios
  (cp-1..cp-4) green.
- `python testing/scenarios/cgt_chat_gate_tracker.py` — the v3 gate-tracker
  scenarios (cgt-1..cgt-3) green.
- `python scripts/harness_lib/stream_json.py` — producer self-check.
- `python testing/scenarios/qol_panel_chat.py` and ui_e2e rc0 — chat surface
  regression net.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.

## Amendments

### v2 (2026-07-13) — chat-plan-hud: TodoWrite live plan on both surfaces

Owner decision 2026-07-13 #5 (PERMIT) unblocked TodoWrite in headless chat
spawns — plan-annotation only, added to the engine's `--allowedTools`. The
overlay pipe grows one frame, `plan-steps` (DISTINCT from the SPEC-133 `plan`
approval frame, which is untouched):

- `stream_json.plan_steps` normalizes a TodoWrite block to `[{text, status}]`
  (pending/in_progress/completed, tolerant of garbage);
  `parse_chat_stream(on_plan=…)` fires per TodoWrite update — the model
  rewrites the whole list mid-turn, so LAST FRAME WINS, no diffing.
- CLI: `chat_hud.set_plan` renders capped bottom rows
  (`format_plan_rows` — summary + current + upcoming, `MAX_PLAN_ROWS`);
  a FINISHED plan flushes once as a checklist into the scrollback (history)
  and drops the rows. A plain non-HUD terminal prints step TRANSITIONS only.
- GUI: a floating minimizable card above the input row (`#planCard`);
  a finished plan appends the checklist to the transcript and hides the card;
  SSE replay rebuilds the card naturally; the card resets with the transcript.
- Render-only everywhere: plans are never persisted (stale-plan hygiene
  beyond turn boundaries stays a named follow-up).

```gherkin
Feature: chat plan HUD (TodoWrite live steps)

  Scenario: [cp-1] TodoWrite updates normalize and fire in order
    Given TodoWrite blocks with mixed statuses and garbage entries
    When parse_chat_stream runs with on_plan
    Then steps normalize to text+status and each update fires (last wins)

  Scenario: [cp-2] the HUD renders capped plan rows and drops a finished plan
    Given a plan with one current and many upcoming steps
    When format_plan_rows renders at a fixed width
    Then rows are summary + current + upcoming within the cap

  Scenario: [cp-3] TodoWrite is permitted and threaded (owner decision #5)
    Given the headless chat allowlist and the engine source
    Then TodoWrite is allowed and on_plan reaches the parser

  Scenario: [cp-4] the plan-steps frame is distinct and both surfaces render
    Given the operator and PAGE sources
    Then plan-steps emits beside the SPEC-133 plan frame and the card
      renders, minimizes and resets
```

### v3 (2026-07-14) — chat-gate-tracker: gate sub-tracker (harness ≠ target)

READ-ONLY display overlay (roadmap `chat-overlays.md` Request 3 MVP). Under the
plan HUD, a gate SUB-TRACKER shows the gates a feature is passing through, with
harness-ladder gates styled DISTINCTLY from target-repo gates. It DETECTS gate
events and READS authoritative status; it never runs or mutates a gate.

- **Detection is deterministic, no LLM.** `harness_ui_page.gate_from_cmd` (and its
  PAGE-JS twin `gateFromCmd`) normalize a Bash tool command matching
  `spec_test_gate.py` / `harness.py test` / `harness-test.py` into
  `{event:"gate", scope:"harness"|"target", target:name?, gate, status:"running"}`;
  `--target <name>` (either ordering) ⇒ target scope. A non-gate command → None.
- **Status comes from quality-state, never invented.** `gateStatus` resolves a
  detected gate against the SAME `st.gates` snapshot `ui_panel._gates` feeds
  `renderGates` (`last` for harness, `target.last` for the active target), with a
  freshness guard so a stale prior run cannot settle the gate early. Until the
  authoritative run settles, the chip stays `running`.
- **Harness ≠ target, structurally.** Harness gates reuse the ladder `.gtier` chip;
  target gates render a `target <name>` mono prefix + a distinct `.gsub.tgt`
  border/hue (extends the right-column `renderGates` precedent). Scope is carried
  IN the event, sourced from two state files that never merge — the UI never infers
  scope from text.
- **Terminal → history.** A settled gate flushes one `↳ gate <g> ✓|✗ <scope>` line
  into the transcript and drops off the sub-tracker; the card resets with the
  transcript (client-side only, like the plan HUD). No gate-running action is added
  and no canonical state is written.

```gherkin
Feature: chat gate tracker (harness vs target sub-tracker)

  Scenario: [cgt-1] the normalizer classifies harness gate commands
    Given Bash gate commands (spec_test_gate.py / harness.py test /
      harness-test.py) and a non-gate command
    When gate_from_cmd normalizes each
    Then harness commands yield scope harness with the right gate and a
      non-gate command yields None

  Scenario: [cgt-2] target gates are parsed and rendered distinctly
    Given a --target gate command and the built PAGE
    When gate_from_cmd normalizes it and the sub-tracker renders
    Then scope is target with target+gate parsed, harness chips reuse the
      ladder .gtier chip and target chips use the target mono prefix + .gsub.tgt

  Scenario: [cgt-3] status is authoritative and the overlay is read-only
    Given the PAGE gate-status + render sources
    Then gateStatus reads st.gates (last / target.last) with a freshness
      guard, renderGateSub POSTs nothing and no gate-running action is added
```
