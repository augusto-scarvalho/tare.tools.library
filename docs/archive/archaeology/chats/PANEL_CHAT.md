# Chat tab (the supervision panel's operator chat)

The **Chat** tab is a browser peer of `harness.py chat`: each session is a real
`harness.py chat` subprocess the panel pipes to (stdin/stdout/stderr), so it
inherits the REPL's gate ladder untouched — the panel adds no engine, prompt, or
gate of its own. It talks to the browser over SSE (server → browser) + small POSTs
(browser → server); there is no PTY and no WebSocket.

## Sessions

A session bar sits above the transcript: one tab per active session, a **Nova
sessão** button, and a ✕ to close a session (when more than one is open).

- **New** — *Nova sessão* (`POST /api/chat/new`) starts a fresh `harness.py chat`
  subprocess and switches to it.
- **List** — the bar is fed by `GET /api/chat/sessions`; a dimmed `•` marks a
  session whose bridge has exited.
- **Select** — clicking a tab re-points the SSE stream (`?session=<id>`) and the
  send/restart target; the transcript clears and replays that session's history.
- **Close** — ✕ (`POST /api/chat/close`) stops the subprocess and removes the tab.

The first load attaches (or creates) the `main` session, so the chat works out of
the box; a session-less request also lands on `main`. Sessions are independent
`ChatBridge` instances — a line sent to one appears only in that session's
transcript. Every session dies with the panel process (no resident daemon), and the
server's `atexit`/shutdown path stops them all.

## The `!` local-command bypass

A line starting with `!` runs a **harness command locally** and prints its output
**without sending a turn to the LLM** — e.g. `!records search onboarding` runs
`harness.py records search onboarding` right in the transcript. `/`-commands
(`/help`, `/mode`, `/repo`, `/config`, `/exit`, …) are handled locally by the REPL
the same way. Because a local command emits no turn, the "respondendo…" spinner is
intentionally not shown for `!`/`/` lines. Type `/help` to list the commands.

This replaces the old *manual* engine option in the (now-removed) engine picker:
you no longer switch the whole session to run one command — you prefix it with `!`.

## Engine / overseer selection

There is **no engine picker in the chat tab** (the old `<select>` and "Restart
bridge" button are gone). Every session uses the **overseer default engine**,
resolved from routing/prefs. Change it through the `/config` wizard (typed in the
chat), the chat-prefs, or the **Config** tab — the one path that supports every
engine, including `openai`. Restart (the "bridge encerrado — Restart" affordance,
or an onboarding profile-only apply) restarts the current session in place with the
same overseer default; it never carries an engine.

Setting the overseer to `openai` there makes **all** panel sessions run `openai`.
Its telemetry renders honestly: in/out tokens and duration fill in, but the cost
chip shows `$n/a` (openai reports no cost) and the context chip shows `ctx n/a`
(there is no openai model-card context window) — both are first-class dimmed chips,
never fabricated numbers.

## Chat workspace layout (declutter, 2026-07-17)

The chat screen is the conversation, full-width. Everything else moved to the
screen it belongs to (SPEC-133 v4): **Decisions/intakes → Tasks**, **Records
ledger → Changelog**, **worker cards → Queue**; the static **Gates section was
removed** (the chat gate sub-tracker remains). The per-turn chips (engine ·
ctx · tokens · cost · session) stay in their bar above the input row. Project
stats live in a floating **HUD** in the transcript's top-RIGHT corner (it
never covers the left-aligned messages): minimized by default it is one
compact `📊 $today · $total` pill (max-width 15rem); `▸` expands it to the
Metrics tiles; the mode persists per browser. The freed side columns are
reserved for the file-tree / diff+editor workspace
(`docs/roadmap/chat-workspace.md`).

## Panel: risk-summary strip (UX-GA.1)

The right column shows a compact **risk-summary strip above the Attention bay**:
open escalations counted by attention tier (critical / high / watch / info), the
open-escalation total, a `gate failing/ok` chip from the last validation, a
`security review` chip when the snapshot carries `requiresSecurityReview`, and
the top blast-radius strip title. It is computed **server-side** in
`ui_panel.risk_summary` from snapshot fields the panel already collects and
rendered as-is by the browser — no client-side aggregation, no extra polling, no
state written (a view, like the attention bay itself). A calm board shows all
zeros. Spec: `specs/40-features/attention-risk-summary.md`.

## Panel: grouped fan-out worker cards (UX-GA.2)

When more than one workflow has workers on the board, the **Agents** section
groups the cards **per workflow/wave**: each group shows a header with the
workflow id and its status counts (e.g. `running 2 · failed 1`), with the
existing worker cards nested inside — fan-out stays legible without streaming
(categorize, not stream). The groups are computed **server-side** in
`ui_panel.group_workers` (stamped as the additive `workerGroups` snapshot key;
`"adhoc"` collects rows without a workflow, most recently active group first)
and rendered as-is by the browser — no client-side aggregation, no extra
polling, no state written. With a single workflow (or none) the section keeps
today's flat card list unchanged. Spec:
`specs/40-features/worker-group-cards.md`.

## Panel: evidence drill-in (UX-GA.3)

The worker drawer carries an **evidence** button that opens the SPEC-129
reviewer evidence bundle for the drawer's workflow in one dialog — instead of
re-opening N files. It is one token-gated fetch of
`GET /api/evidence?workflow_id=&worker_id=` (the exact bundle
`harness.py workflow evidence <wfid>` emits, assembled server-side by
`evidence_bundle.bundle`) rendered **as-is**: per worker the status,
`failureClass`, result path and the CQ.2 `oracleEvidence` capsule (oracle,
exitClass, artifactPath, rerunCmd), plus the HARNESS_RESULT path, risk flags
and records refs. Every path is plain **text** — the view never fetches
artifact bodies (handles-not-bodies) — and there is no polling and no state
written (a view, like the risk-summary strip). A bad workflow id renders the
same `{"error": …}` shape the other read routes use. Spec:
`specs/40-features/evidence-bundle.md` (v2 amendment).

## Panel-chat QoL batch (SPEC-133)

### Multi-line input

The chat input is a `<textarea id="chatin">`: **Enter sends**, **Shift+Enter
inserts a newline**, and history recall (Arrow Up/Down) only fires while the value
has no newline. A message containing a newline is sent as a single POST framed as
one `/paste\n<text>\n/end` REPL block — the REPL's `_read_paste_block` consumes it
as one block (no protocol or CLI change), and `stripPaste` unframes it on the
`you` replay branch so the transcript shows the raw text. In the CLI the two paste
stderr hints are suppressed under the panel bridge (`HARNESS_CHAT_EVENTS=1`) so the
transcript stays clean; a TTY CLI is unchanged.

### Attachments (📎 / drag-and-drop / clipboard image / @path)

One mechanism — the REPL's `@mention` — with four entrances:

- **GUI picker/drop**: the 📎 button (left edge of the input row) or dropping
  files onto the composer uploads each file via `POST /api/chat/upload` to
  `.harness/runtime/chat-uploads/` (sanitized name, 8MB cap, gitignored +
  export-excluded) and inserts the returned `@path` into the input — visible
  and editable before sending.
- **GUI clipboard image**: pasting an `image/*` item in the textarea uses the
  same upload route and names it `clipboard-image.png`, `.jpg`, `.webp`, `.gif`,
  or `.bin` for another image MIME type. Text-only paste remains native.
- **CLI typed**: `@path`, `@"path with spaces"`, `@C:\abs\path.txt`, or `@?`
  for the fuzzy finder (SPEC-111 R20/R21).
- **CLI drag-and-drop**: dropping a file on the terminal pastes its absolute
  path; the REPL rewrites it into an `@"…"` mention automatically (absolute
  paths only — a typed relative path stays prose).

Upload success means only **uploaded / path inserted**; upload never sends the
message. On send, text files inline as capped `[file: …]` blocks; binary files
become a `[file attached (binary): <abs path>]` note. Claude or Codex can then
use its file tools to inspect the path; the current chat has no Kimi engine,
and the UI never claims that any agent saw an image. Spec: SPEC-133 v2/v5.

### Stopping a turn (⏹ / Esc Esc)

Same behavior as the claude/codex UIs: stopping keeps the partial reply and
the session (`--resume` continues normally); the turn ends with
`[turn interrupted by user]`.

- **GUI**: a red **⏹ Stop** appears left of Send while a turn is running.
  It POSTs `/api/chat/stop`; the bridge touches the per-session
  `chat-stop-*.flag` file and the engine's watcher kills the turn's child
  within ~0.25s (the REPL is blocked in `agent.send()`, so a piped line could
  not do this). A click that lands after the turn ended is harmless — the
  stale flag is consumed unread at the next turn start.
- **CLI**: press **Esc twice** (within 2s) while the agent is thinking.
  Windows TTY only for now; the first Esc prints a confirmation hint.
- `openai` engine: single-shot HTTP request, cannot be stopped mid-flight.

### Markdown rendering (GUI + CLI)

Assistant replies render as markdown, reusing the shipped tree-sitter highlighter
rather than a new one:

- **GUI** — `scripts/harness_ui_page_md.py` exports `MD_JS`, a self-contained IIFE
  assigning `const MD` with the single API `MD.renderInto(container, text)`. It is
  spliced into `PAGE` at the `/*__MD_JS__*/` placeholder **after** the page's
  `esc()` and `HL` globals are defined, so every text node is escaped via `esc()`
  first (no raw HTML from input reaches `innerHTML`) and fenced code routes through
  `HL.highlightBlock`. Mid-turn assistant text arrives as `text` events and renders
  immediately through the same `MD.renderInto` (see the render contract below);
  plain SSE reply lines still buffer on `turn-end` and flush into one `.ln md` div
  on `ready`/`exit` — but the REPL skips the end-of-turn reply when it merely
  repeats what already streamed, so nothing renders twice. `err`/`you`/`tool` lines
  bypass the buffer. Replay renders identically.
- **CLI** — `scripts/harness_lib/md_ansi.py` `render(text, stream)`. **Degradation
  rule:** when `highlight.color_enabled()` is false (the piped panel bridge,
  `NO_COLOR`, or any redirect) the text is returned **byte-identical** — the
  transcript the browser reads never sees an escape byte. With color it is a line
  state machine: bold headings, `•` bullets, cyan inline code, and fenced bodies
  routed through `highlight.highlight(force=True)`.

### Plan / question event contract

Chat engines are one-shot per turn in headless mode (`claude -p --resume` with
`--permission-mode` always passed; `Enter/ExitPlanMode` disallowed), so "plan
approval" and "choose an option" are **not** engine events — the harness DERIVES
them deterministically. That derivation IS the contract. Both are additive events
on the existing `\x1e` emit channel + `bridge.history`, and are the **stable
capture surface for any future UI** (nothing in the contract is chat-tab-specific):

- **`{"event":"plan","text":<reply>,"mode":"plan","source":"derived"}`** — emitted
  at turn-end when `chat_mode == "plan"` (the reply IS the plan).
- **`{"event":"question","tool":"AskUserQuestion","questions":[{"q":…,"options":[…]}],"source":"tool_use"}`**
  — derived when a `tool_use` block named `AskUserQuestion` streams by; the raw
  structured input flows through `stream_json.tool_descriptor` and
  `chat_operator._extract_questions` pulls the `{q, options}` pairs.

`source` semantics: `"derived"` / `"tool_use"` mark that the harness synthesized
the event, reserving room for an engine-native plan/approval signal (claude
`control_request`, codex approval requests) to feed the **same** events later
without breaking consumers. Honest note: headless `-p` may never fire
`AskUserQuestion`; the contract is defined and tested with a synthetic frame either
way.

### Mid-turn text + tool-chip render contract (2026-07-16 batch)

Long turns (SPEC-146 rooms) narrate for minutes between tool calls; that text used
to vanish until the final reply. Two additive extensions on the same `\x1e` channel:

- **`{"event":"text","text":<block>}`** — one per assistant text block, fired by
  `stream_json.parse_chat_stream(on_text=…)` as it streams. The GUI renders it
  immediately via `MD.renderInto` (outside the turn-end buffer); the plain CLI
  prints it as it arrives. The REPL tracks the turn's blocks and skips the
  end-of-turn `say(reply)` when claude's `result` merely repeats them (dedupe
  window = one turn).
- **`tool` event render fields** — `stream_json.tool_descriptor` derives, stdlib
  only: Edit → `diff` (unified `difflib` diff, `DIGEST_CAP`-capped) + `language`;
  Write/NotebookEdit → `code` + `language`; Read → `language` (rides the chip so
  the matching tool-result digest can highlight). Absent for every other tool —
  those events stay byte-identical to the pre-batch shape.

Chip rendering rules (GUI): a `diff` colorizes via `colorizeDiff` (esc()'d per
line); `code` and language-tagged result digests highlight through
`HL.highlightBlock` on **first expand only** (`hlWhenOpen` — collapsed chips pay
nothing); raw input is never `innerHTML`'d. Each **collapsed** chip also carries
one indented `.tprev` preview line inside its `<summary>` (CSS-hidden once open):
Edit previews the first 6 hunk lines colorized, Write its first code line, Bash its
own `description`, and the tool-result flips the line to the CLI-style
`⎿ first line (+N lines)` (diff chips keep the hunk). `PREV_DIFF_LINES` in
`harness_ui_page.py` is the preview-size knob.

**Vendor-neutral by contract** (codex parity, 2026-07-17): the callbacks are the
seam — an engine only needs a stream parser that maps its output onto
`on_tool/on_tool_result/on_plan/on_text` and returns `{text, session_id, result}`.
`parse_chat_stream` (claude stream-json) and `parse_codex_stream` (codex `exec
--json` JSONL, schema `exec_events.rs`) both live in `stream_json.py`. What each
engine emits today:

| engine | text | tool chips | plan | edit diffs | notes |
|---|---|---|---|---|---|
| claude | mid-turn | all tools | TodoWrite | full unified diff | reference |
| codex (exec, default) | mid-turn (`agent_message`) | `command_execution`→Bash, `file_change`→Write/Edit, `web_search`, `mcp_tool_call` | `todo_list` | **derived** (M1): engine snapshots paths at item.started, difflib at completed, `git diff HEAD` fallback — rides the `tool-result` event | rooms map write-capability to the directory sandbox; ui-overseer on codex is read-only (owner decision — no per-path grants in codex) |
| codex (app-server, `HARNESS_CODEX_TRANSPORT=app-server`) | mid-turn | same + live `tool-delta` command output | `turn/plan/updated` | **native** per-file diff (v2 `FileUpdateChange.diff`) + the aggregated `turn-diff` block | JSON-RPC to `codex app-server` (`codex_appserver.py`); real `ctx_window` in usage; approval server-requests auto-answered per mode and surfaced as text notes; construction failure falls back to exec |
| openai | final reply only | run_harness calls only | — | — | own tool loop; parser seam ready |

Two additive M3 events: **`{"event":"tool-delta","id","chunk"}`** appends live
command output into the chip; **`{"event":"turn-diff","diff"}`** renders one
collapsible colorized "diff do turno" block per turn (latest wins, reset at
turn-end). Wire quirks pinned by `rh_codex_appserver.py`: v2 `kind` is a
serde-tagged object and an add's `diff` field is raw content (the engine
synthesizes the unified shape).

Rooms (SPEC-146) inherit the SESSION's engine — routing resolves the role's card
per executor — so a codex porteiro hands off to a codex room with live chips.

Encoding discipline (Windows): `ChatBridge.start`, `ClaudeEngine.send` and
`CodexEngine.send` pin `PYTHONIOENCODING=utf-8` + `PYTHONUTF8=1` in their child envs, and the REPL
reconfigures its own stdio to UTF-8 under `HARNESS_CHAT_EVENTS=1` — both U+FFFD
vectors (bridge plain lines, python descendants of engine Bash calls) are killed at
the source. Non-python tools that emit a legacy code page are outside this fix.

### `/approve` + `postPlanMode`

- **CLI** — `/approve [message]` flips `chat_mode` to the `postPlanMode` chat-pref
  (reusing the `/mode` machinery) and sends the approval message (default
  `"approved, proceed"`) as the next turn. `postPlanMode` lives in
  `.harness/runtime/chat-prefs.json` (default `accept-edits`, allowed
  `auto|accept-edits`, validated) and round-trips across unrelated saves — an
  approved plan should run its edits.
- **GUI** — `handleEvt`'s `plan` case renders the plan as a markdown message plus
  an approval strip (**Approve** / **Keep planning**). Approve POSTs the existing
  pipe `POST /api/chat/send {line:"/approve"}`; Keep planning dismisses. The
  `question` case reuses `promptModal`'s `<select>` (one question at a time,
  rendered sequentially); the chosen answer is sent as the next user message
  (`answer: <choice>`). No new modal, POST endpoint, or run-action change — messages
  are not mutations, so the engine's own permission mode governs what they cause.

Deferred (recorded, not built): a dedicated approvals tab; codex approval-request
passthrough; multi-select / free-text question forms; auto-approve policies; and a
per-session cost filter over the additive `session` field
`cost_metrics.record_turn` now stamps from `HARNESS_CHAT_SESSION`.

Spec: [SPEC-133 — panel-chat QoL](../specs/40-features/panel-chat-qol.md).

## See also

- [SPEC-114 — supervision panel](../specs/40-features/supervision-m5-interactive-panel.md) (v11: this chat redesign; v12: panel-wide confirm/alert/prompt modal, gates section, branch chip)
- [SPEC-111 — REPL interactive UX and onboarding](../specs/40-features/repl-ux-onboarding.md) (the chat REPL + `!`/`/` commands)
- [SPEC-115 — model-card management + role-based routing](../specs/40-features/model-routing.md) (where the overseer engine is chosen)
- [Flow composer (the Compose screen)](FLOW_COMPOSER.md)
