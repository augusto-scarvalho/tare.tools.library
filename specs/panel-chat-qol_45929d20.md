# SPEC-133 — panel-chat QoL batch: markdown, honest indicators, multi-line, plan/approve contract

Status: SPEC-133, proposed 2026-07-13 (acceptance: `testing/scenarios/qol_panel_chat.py`).

Intake (SPEC-116 door NEW): an owner quality-of-life batch on the supervision
panel + chat, ahead of the backlog queue — (1) markdown rendering of chat
replies in GUI+CLI, mimicking the shipped tree-sitter highlighter; (2) explain
the always-`main` branch chip (answered: the loop commits to `main`; the build
is only chip enrichment); (3) gates/metrics indicators look frozen and the
"session $" tile is mislabeled; (4) the Records ledger section is stale and its
purpose forgotten; (5) multi-line chat input (Shift+Enter); (6) remove the
duplicated disclaimer under the input; plus (P8) a stable plan/question event
contract with a chat-tab `/approve` flow. Covered-check: `records search panel
chat qol` → no hit; no existing verb/section renders these. Decision: **NEW**.

## Goal

The supervision panel's chat renders assistant replies as markdown (GUI DOM +
CLI ANSI, both degrading to plain text), its gates/metrics/ledger indicators
carry an honest age and label instead of looking frozen, the input accepts
multi-line messages framed as one REPL block, and plan-mode turns plus
`AskUserQuestion` tool calls surface as a stable, additive `\x1e` event contract
(`plan` / `question`) that a chat-tab `/approve` flow — and any future UI —
consumes without re-deriving anything chat-specific.

## Applicability

Applies to the panel front-end string `scripts/harness_ui_page.py` (P1–P6 view
fixes + the P8 approval strip / question modal), the injected markdown module
`scripts/harness_ui_page_md.py` (`MD.renderInto`), the CLI renderer
`scripts/harness_lib/md_ansi.py`, the chat REPL loop `chat_operator.py` (P5 hint
gating, P6 render call, the P8 `plan` emit + `/approve` command + `question`
derivation), the stream parser `stream_json.py` (`AskUserQuestion` descriptor),
the prefs owner `chat_setup.py` (`postPlanMode`), `cost_metrics.record_turn`
(additive `session` field), and the escalation-resolve producer in `harness.py`.
It does **not** change the gate ladder, the pipe-event transport, any engine's
permission-mode wiring, or add a chat-tab-specific endpoint. Deferred (recorded,
not built): a dedicated approvals tab; codex approval-request passthrough;
multi-select / free-text question forms; auto-approve policies; a per-session
cost filter over the new `session` field.

## Requirements / invariants (numbered, testable)

1. **No duplicated hint.** The `#inputHint` div is gone; the chat input is a
   `<textarea id="chatin">` whose placeholder carries the affordances.
2. **Gates carry age.** `renderGates` stamps a relative "· ran … ago" from the
   last run's `at`, ISO in the title, amber `stale` when older than 24h — the
   section can no longer look frozen.
3. **Honest metrics labels.** The all-time cost tile is labeled `total $`
   ("all-time · last 500 records"), and a new `today $` tile renders the current
   UTC day's spend; the mislabeled `session $` tile is retired.
4. **Ledger legibility.** `renderLedger` shows the purpose header `project
   ledger — milestones · decisions · changes` plus a "last entry … ago" line.
   **v2 note (2026-07-13):** the Records ledger heading now names its worklog source and `harness.py log` producer in a tooltip (`qol:ledger-tooltip`).
5. **Ledger producer.** Resolving an escalation writes one queryable ledger
   record: `records.add_entry(ROOT, "decision", "escalation <id> resolved",
   tags=["escalation"])`, in a never-crash guard around the resolve path.
6. **Branch chip enrichment.** `renderHeader` enriches the branch chip with a
   short sha (`@<sha>`) and a dirty marker (`●<n>`) from an additive `st.gitInfo`
   `{branch, sha, dirty}`, falling back to `st.branch` so the chip never
   regresses when `gitInfo` is empty.
7. **Multi-line input.** A message containing a newline is framed as a single
   `/paste\n…\n/end` REPL block (one POST); `stripPaste` unframes it on replay.
8. **Markdown in the GUI.** The `MD` renderer IIFE (`MD.renderInto`) is spliced
   into `PAGE` at the `/*__MD_JS__*/` placeholder; it escapes every text node via
   `esc()` first and routes fenced code through `HL.highlightBlock` (degrading to
   a plain `<pre>`).
9. **Markdown in the CLI.** `md_ansi.render(text)` returns the text
   BYTE-IDENTICAL when color is disabled (the piped panel bridge never sees an
   escape byte) and emits ANSI (bold headings, cyan inline code, highlighted
   fences) when color is forced.
10. **Plan event.** At turn-end, when `chat_mode == "plan"` and a reply exists,
    the loop emits `{"event":"plan","text":<reply>,"mode":"plan","source":"derived"}`
    on the `\x1e` channel — the reply IS the plan; `source` reserves room for a
    future engine-native plan signal.
11. **Question event.** A claude `tool_use` block named `AskUserQuestion` carries
    its raw structured `input` through `stream_json.tool_descriptor`, from which
    `chat_operator._extract_questions` derives `[{q, options}]` for a
    `{"event":"question","tool":"AskUserQuestion",…,"source":"tool_use"}` event.
12. **Approve flow.** `/approve [message]` flips `chat_mode` to the validated
    `postPlanMode` chat-pref (default `accept-edits`, allowed `auto|accept-edits`)
    and sends the approval message (default "approved, proceed") as the next turn;
    the pref round-trips and survives unrelated saves.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Reuse the shipped highlighter for chat markdown (GUI `HL.highlightBlock`, CLI `highlight.highlight`) instead of a new renderer | `scripts/harness_ui_page.py:1034` (`HL.highlightBlock`), `scripts/harness_lib/highlight.py`; `specs/40-features/syntax-highlighting.md` |
| Multi-line as `/paste…/end`: zero protocol/CLI work — the REPL already frames pasted blocks | `scripts/harness_lib/chat_operator.py` `_read_paste_block`/`_read_message` self-check; verified in the approved plan |
| Plan/approval and question are DERIVED, not engine events (headless `-p --resume` is one-shot; `Enter/ExitPlanMode` disallowed) | `scripts/harness_lib/chat_engines.py:142-166` (`--permission-mode` always passed), `:154` (disallowedTools); the approved plan's P8 verified reality |
| `session $` tile was really the all-time total; `byDay` was computed but unrendered | `scripts/harness_lib/cost_metrics.py` (`byDay`); approved-plan verified fact |
| Escalation-resolve is the natural new ledger producer (it wrote no record before) | `scripts/harness.py` `cmd_escalations`; `specs/40-features/records-ledger.md` (SPEC-112) |
| Additive `\x1e` events on the existing pipe channel + `bridge.history` (a future tab consumes the same frames) | `scripts/harness_lib/chat_operator.py:408-421` (emit protocol); `specs/40-features/supervision-m5-interactive-panel.md` (SPEC-114 v2 pipe-event protocol) |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: panel-chat quality-of-life batch

  Scenario: [qol:no-input-hint] the duplicated disclaimer is gone
    Given the supervision panel page
    When it renders the chat input row
    Then there is no #inputHint element and the input is a textarea

  Scenario: [qol:gates-section-removed] the static gates section is gone (v4 declutter)
    Given the chat-workspace declutter (v4 amendment, owner call)
    When the PAGE is inspected
    Then renderGates and the sec-gates markup are absent while the chat
      gate sub-tracker (renderGateSub) stays wired

  Scenario: [qol:metrics-honest-labels] the cost tiles are labeled honestly
    Given the metrics tiles
    When they render
    Then the all-time total reads "total $" and a "today $" tile is present

  Scenario: [qol:ledger-header] the ledger names its purpose
    Given the records-ledger section
    When it renders
    Then it shows the "project ledger — milestones · decisions · changes" header

  Scenario: [qol:ledger-producer] resolving an escalation writes a ledger record
    Given a resolved escalation
    When the ledger tail is read
    Then a "decision" record titled "escalation <id> resolved" tagged escalation is on top

  Scenario: [qol:branch-chip-sha] the branch chip carries the commit sha
    Given a git snapshot with a short sha and dirty count
    When the header renders the branch chip
    Then the chip appends "@<sha>" and a "●<dirty>" marker from st.gitInfo

  Scenario: [qol:multiline-input] a multi-line message is one framed block
    Given a chat message spanning two lines
    When it is sent
    Then it is framed as a single /paste…/end block that stripPaste can unframe

  Scenario: [qol:md-gui] the GUI renders markdown replies
    Given the panel page
    When the MD renderer is spliced in
    Then const MD / MD.renderInto is present and the placeholder is consumed

  Scenario: [qol:md-cli] the CLI renders markdown only when color is on
    Given an assistant reply in markdown
    When md_ansi.render runs with color disabled then forced
    Then disabled is byte-identical and forced emits an ANSI heading

  Scenario: [qol:plan-event] a plan-mode turn emits the plan frame
    Given a chat session in plan mode
    When a turn completes with a reply
    Then a plan event with mode plan and source derived is emitted after turn-end

  Scenario: [qol:question-event] an AskUserQuestion tool call surfaces structured questions
    Given a claude tool_use block named AskUserQuestion with questions and options
    When the stream is parsed
    Then the descriptor carries the raw input and the derived [{q, options}] questions

  Scenario: [qol:approve-flow] approving a plan flips the mode and proceeds
    Given a postPlanMode preference
    When /approve runs after a plan
    Then the chat mode flips to the post-plan mode and the approval turn is sent
```

## Ceilings (upgrade paths)

- The `plan`/`question` events are DERIVED deterministically; the `source` field
  (`"derived"` / `"tool_use"`) is the seat for an engine-native plan/approval
  signal (claude `control_request`, codex approval requests) — wire those to the
  same events when an engine emits them.
- The additive `session` field on cost-turn records enables a future per-session
  cost filter; nothing renders it yet (3 lines when a tab needs it).
- `md_ansi` is a line state machine (headings, lists, inline code/bold, fences) —
  add tables/nested lists only when a real reply needs them.

## Test strategy

- Behaviors to verify: the six view fixes as PAGE-string assertions on the built
  `harness_ui.PAGE` (P1–P6 + the P4 chip render + the P8 approval strip); the CLI
  renderer's disabled-identity / forced-ANSI contract; the escalation-resolve
  producer (temp-root `records.add_entry` round-trip + the `cmd_escalations`
  wiring); the `AskUserQuestion` descriptor + `_extract_questions` derivation
  through the real parser; and the `plan` + `/approve` `\x1e` contract driven
  end-to-end through a real `harness.py chat` subprocess (an `openai` turn against
  a local HTTP stub — deterministic, no LLM).
- Edge cases: empty `gitInfo` (chip falls back to `st.branch`); an invalid
  `postPlanMode` degrades to the default; a torn stream line is skipped by the
  parser; color disabled → byte-identical markdown.
- Regression risks: `m5_ui_panel.py` stays green (the textarea keeps id `chatin`
  inside `.inputrow`; `panel:branch-shown` still reads `st.branch`); the
  `\x1e`/`bridge.history` transport is unchanged (additive events only).
- Coverage impact: enforced via `testing/scenarios/qol_panel_chat.py` +
  Playwright flows in `testing/ui/test_panel_e2e.py`.
- Known gap (reported, not fixed here): `ui_panel.state_snapshot` does not yet
  emit the `gitInfo` key the header consumes, so `@sha`/`●dirty` never render at
  runtime (`harness.py:current_commit` exists but is unwired). The
  `qol:branch-chip-sha` check asserts the landed front-end render contract; the
  backend wiring is a one-line follow-up.

## Validation

- `python testing/scenarios/qol_panel_chat.py` — the 12 `qol:*` checks
  (`qol:no-input-hint`, `qol:gates-section-removed` (v4 — replaced
  `qol:gates-age` when the section was removed), `qol:metrics-honest-labels`,
  `qol:ledger-header`, `qol:ledger-producer`, `qol:branch-chip-sha`,
  `qol:multiline-input`, `qol:md-gui`, `qol:md-cli`, `qol:plan-event`,
  `qol:question-event`, `qol:approve-flow`) all green.
- `python testing/ui/test_panel_e2e.py` — the additive `e2e:chat-multiline`,
  `e2e:chat-markdown`, `e2e:plan-approve` flows (real chromium; green-skips
  without a browser).
- `python scripts/harness_lib/md_ansi.py` and
  `python scripts/harness_lib/harness_ui_page_md.py` module self-checks.
- `python testing/scenarios/m5_ui_panel.py` untouched-green; `spec-pack`
  feature-spec conformance for this spec.
- v5 composer attachments: `python testing/scenarios/pw_ui_smoke.py` —
  `composer-attach-picker`, `composer-file-drop`, `composer-image-paste`,
  `composer-upload-failure` (headless teeth authored in `ui/tests/pw-smoke.mjs`,
  forwarded as scenario checks and pinned present BY NAME there, so deleting one
  goes red instead of shrinking the count). The server half stays proven by
  `m5_ui_panel.py` `chat:upload-roundtrip` + `chat:upload-bad-b64-refused` — this
  amendment leaves it byte-identical.

## Amendments

### v2 (2026-07-17) — chat attachments: GUI 📎/drag-and-drop + CLI dropped paths

One attachment mechanism, the REPL's existing `@mention` (SPEC-111 R20/R21);
the GUI and the terminal are two entrances to it:

- **GUI** — a 📎 button at the left edge of the input row (plus drag-and-drop
  onto the transcript/textarea) POSTs `{session, name, data:<base64>}` to the
  new token-gated `POST /api/chat/upload`; `ui_panel.save_upload` writes it to
  `.harness/runtime/chat-uploads/<ts>-<name>` (basename sanitized to `[\w.-]`,
  8MB cap, base64 validated) and the browser inserts the returned relative
  path as `@path` into the input. Uploads are class-D local: gitignored +
  `PRIVATE_PREFIXES` (never exported).
- **CLI** — `MENTION_RE` now admits leading `.` (upload paths) and `:`
  (absolute Windows paths); `@"path with spaces"` is a quoted mention; and
  `_absorb_dropped_paths` rewrites a dragged-in ABSOLUTE path (quoted or bare)
  into an `@"…"` mention — relative paths stay prose, never a surprise
  attachment.
- **Binary files** (NUL sniff) attach as a `[file attached (binary, N bytes):
  <abs path> — read it with your file tools]` note instead of being skipped —
  the engine's own Read tool handles images/PDFs.

Validation: `m5_ui_panel.py` `chat:upload-roundtrip` + `chat:upload-bad-b64-refused`;
`chat_operator.py` + `ui_panel.py` module self-checks (quoted/absolute/dropped
mention cases; sanitization, cap, collision cases).

### v3 (2026-07-17) — turn stop (⏹ / Esc Esc) + view scroll + markdown modals

- **Turn stop, one mechanism per surface** over one engine seam:
  `ClaudeEngine`/`CodexEngine` gain `interrupt()` — the per-turn child is
  killed and the turn returns the PARTIAL streamed text plus
  `[turn interrupted by user]` (session id kept, `--resume` unaffected); the
  app-server transport uses the native `turn/interrupt` notification with an
  8s drain grace. Triggers: **GUI** — a red `⏹ Stop` button left of Send,
  visible only while a turn runs (`busyOn`/`busyOff`), POSTs
  `/api/chat/stop {session}`; the bridge writes
  `.harness/runtime/chat-stop-<session>.flag` (env
  `HARNESS_CHAT_STOP_FILE`) because the REPL blocks inside `agent.send()`
  during a turn — the engine-side watcher (`_watch_interrupt`, 0.25s poll)
  consumes the flag and kills the child. A STALE flag (clicked between turns)
  is consumed harmlessly at the next turn start. **CLI** — Esc Esc within 2s
  on a Windows TTY (`_esc_watcher`, msvcrt; first Esc prints a hint).
  `openai` engine: single-shot HTTP, no stop (honest limitation).
- **View scroll**: every full-page view (`#viewTasks` kanban, Queue,
  Changelog, Memory, Specs, Research, Experiments) now carries the same
  `flex:1 1 auto; overflow-y:auto` the Config/Compose views had — the body is
  `overflow:hidden`, so a view without its own scroll silently clipped
  anything below the fold.
- **Markdown modals**: the spec / memory / research / skill dialogs render
  their (markdown) bodies through `MD.renderInto` (`fillDocDlg`) instead of a
  raw `<pre>` dump; the MCP capability card renders its JSON through
  `HL.highlightBlock` (js grammar). Commit dialog already colorized diffs.

Validation: `m5_ui_panel.py` `chat:stop-writes-flag` +
`chat:stop-unknown-session-refused`; `chat_operator.py` self-check
(stale-flag consumed / live-flag kills / interrupt path / `_esc_watcher`
degradation); `ui_panel.py` self-check (`stop_turn` live/dead bridge);
`codex_appserver.py` self-check; chromium sweep (all 10 tabs
`overflow-y:auto`, spec modal renders md nodes, stop button
idle-hidden→busy-visible→click-writes-flag).

### v4 (2026-07-17) — chat-workspace declutter: widgets rehomed by affinity + session-stats HUD

Owner call: the chat screen sheds its side columns; every widget moves to the
screen it belongs to, and session telemetry becomes a floating HUD.

- **Moves (ids unchanged — the render functions and the `/api/state` poll are
  untouched; only the DOM homes changed):** Decisions/intakes (`#decs`) → the
  **Tasks** view (below the kanban); Records ledger (`#ledger` + `#ledgerHead`)
  → the **Changelog** view; worker cards (`#agents`) → the **Queue** view
  (tiled grid). Risk summary / attention / escalations were already in the
  Alerts dialog.
- **Removed:** the static right-column **Gates** section (`renderGates`) —
  owner: "não tem ajudado muito". The snapshot still carries `st.gates`; the
  chat gate SUB-TRACKER (v3 of chat-overlays) keeps consuming it.
- **Stats HUD** (`#hud`): floats top-RIGHT over the transcript (messages are
  left-aligned, so the right corner covers nothing — owner correction; the
  per-turn chips (engine / ctx / tokens / cost) STAYED in the `#chips` bar
  above the input row, where they were). **min (default, max-width 15rem)**:
  one compact line — `📊 $today · $total` (from the same throttled
  `/api/metrics` fetch). **Expanded** (`▸`/`▾` toggle, persisted in
  `localStorage.hudMin`): the Metrics tiles (`#metPanel`) + top expensive.
  `chip()` keeps the semantic class alongside `na` (styling hook).
- **Freed space stays free** — the chat is full-width; the side columns are
  reserved for the file-tree / diff+editor workspace
  (`docs/roadmap/chat-workspace.md`), deliberately not built in this slice.

Validation: `m5_ui_panel.py` `page:hud` + reworked `page:modebadge-input-row`
/ `panel:gates-section` (absence proof); `qol_panel_chat.py`
`qol:gates-section-removed` + retargeted ledger-tooltip split;
`test_panel_e2e.py` drill-in/recovery flows navigate to Queue,
`e2e:gates-and-branch` asserts the section is gone + HUD min default.

### v5 (2026-07-31) — React attachment parity + clipboard images

The React composer restores the existing attachment entrance without changing
the server boundary:

- Picker and composer-wide file drop POST `{name, data:<base64>}` to the
  existing `POST /api/chat/upload`; image paste in the textarea normalizes the
  browser blob to `clipboard-image.png`, `.jpg`, `.webp`, `.gif`, or `.bin`.
- A successful response inserts the server-returned `@path` into the editable
  textarea. Nothing is sent automatically, and the UI claims only upload/path
  insertion — never that an agent saw an image.
- While a POST is active, the composer shows `Status running` and blocks Send,
  Enter, picker, drop, and image paste — and a blocked drop/paste SAYS so on the
  same status row, beside the running line (v5.1, audit 2026-07-31: the refusal
  was silent, so the file simply never went and nothing said why). A read,
  network, or server failure shows
  `Status failed` in `aria-live` and leaves the textarea byte-identical, with no
  mention or other success affordance.
- The client rejects files above 8 MiB before base64 encoding; server
  sanitization, cap, upload directory, authentication, and route remain
  authoritative and unchanged.

| Decision | Authoritative source |
|---|---|
| Existing upload route and response path | `scripts/harness_ui.py`; `scripts/harness_lib/ui_panel.py` |
| Attachment delivery through editable `@path` | SPEC-133 v2; `scripts/harness_lib/chat_operator.py` |
| No visual-consumption claim | Current text-only chat transport and per-engine file-tool behavior |
| React picker/drop/paste behavior | `ui/src/domains/workbench/Composer.tsx`; checks below |


#### Gherkin scenarios

```gherkin
Scenario: [composer-attach-picker] Picker uploads before inserting a mention
  Given the React workbench has an active session
  When the owner chooses a file with the attachment picker
  Then Uploading is visible while the request is pending
  And the request contains the file name and base64 bytes
  And the returned path is inserted without sending the message

Scenario: [composer-file-drop] Dropping a file uses the same upload seam
  Given the React composer is ready
  When the owner drops a file on the composer
  Then the existing upload route receives that file
  And the returned path is inserted into the textarea

Scenario: [composer-image-paste] Image paste uploads a normalized clipboard file
  Given the textarea contains editable text
  When the owner pastes a PNG image
  Then the upload name is clipboard-image.png
  And no mention appears before the upload response
  And text-only paste remains native

Scenario: [composer-upload-failure] Failed upload preserves the draft
  Given the textarea contains a draft
  When the upload route returns an error
  Then Upload failed is visible in an aria-live region
  And the textarea is byte-identical to the draft
  And no new mention appears
```
