# SPEC-114 — Supervision panel with embedded chat

Status: implemented 2026-07-10 (acceptance: `testing/scenarios/m5_ui_panel.py`; backend `scripts/harness_lib/ui_panel.py`, server + page `scripts/harness_ui.py`, CLI `harness.py ui`). Re-scopes the M4-era interactive-panel spec around the SPEC-111 chat REPL and the SPEC-104 snapshot renderer.

## Goal

A single-file local browser panel where a supervisor watches harness state and acts on it — resolve escalations, re-run a gate, search the records ledger, and drive the operator chat — without any capability the terminal lacks. The panel is a *view plus an allowlisted trigger*, never a second write path: every action shells out to an existing `harness.py` subcommand, and the chat tab is pipes to `harness.py chat`, so both inherit the harness's own gates.

## Applicability

Applies to `scripts/harness_ui.py` (server + inline page), `scripts/harness_lib/ui_panel.py` (collectors, gated actions, chat bridge), and the `harness.py ui` CLI wiring. Does not add a resident daemon, remote access, accounts, or persisted panel state; the panel is started on demand and dies with its process.

## Scope

In scope: a stdlib `ThreadingHTTPServer` bound to loopback; four tabs (Dashboard, Escalations, Records & Metrics, Chat); GET snapshot/records/metrics endpoints; a POST action endpoint over an allowlist; an SSE chat stream + POST send/restart bridged to the REPL.

Out of scope: WebSockets, PTY/xterm.js terminals, non-loopback binds, multi-user auth, controlled-write *merge* approval flows (those stay human-only and are structurally refused here), and any new harness capability (if a button needs one, that capability ships as its own subcommand first).

## Requirements / invariants (numbered, testable)

1. **Single write path.** Every mutating panel action is an existing allowlisted subcommand executed via `subprocess` (argv arrays, never shell strings). The panel never edits `.harness/` state files directly. `ui_panel.ACTIONS` is the whole surface; growing it means the subcommand already exists.
2. **Loopback + per-session token.** The server binds `127.0.0.1` only. A `secrets.token_urlsafe` token is generated at startup and required on *every* route via `?token=` or `X-Harness-Token`; missing/wrong → `403`, nothing served or executed.
3. **HITL is structural, not cosmetic.** Server-side `classify_command` refuses any built argv carrying `--approval-token`/`--send` (`human-only`) before it can run; controlled/mutating actions additionally require the browser's deliberate confirm (`params.confirm == true`) — the same consent-at-the-moment rule the REPL enforces.
4. **Stream only while a client is present.** SSE drains the chat bridge and heartbeats every 15 s; a client disconnect (broken pipe) ends the stream. State polling runs only while `document.visibilityState === 'visible'` and the active tab needs it (R27: no client, no work).
5. **Chat inherits the REPL gate ladder untouched.** The chat tab is a `ChatBridge` piping stdin/stdout/stderr to `harness.py chat`; piped stdin puts the REPL in SPEC-111 R1/R15 no-input mode. The panel adds no engine, prompt, or gate of its own.
6. **Terminal parity.** Nothing is panel-only: Dashboard = `status`/`metrics`, Escalations = `escalations --resolve`, Records = `records`, gate re-run = `harness-test.py <gate>`, Chat = `chat`. Every action has a documented terminal equivalent.

## Acceptance criteria

- [x] Request without token → `403`; with token → snapshot JSON carrying `escalations` + `generatedAt`.
- [x] Unknown action refused; mutating action without `confirm` refused; `records-search` with a `--send` term refused as `human-only` — none executes.
- [x] Chat send `status` in manual mode round-trips real command output (`"root"`) through the bridge to the stream.
- [x] Killing the server terminates the bridge subprocess tree (no orphan), with no state mutation beyond actions explicitly taken.

## Gherkin scenarios (UI surfaces only)

SPEC-116 E retrofit pilot (added 2026-07-11; maps existing content, rewrites no
history). Declarative behavior for the v5 panel flows. Each `[<id>]` resolves to a
named check in the scenario files the Validation section references — the gate
(`feature-spec-conformance`) enforces the mapping, so renaming a check without
updating this block fails the build.

```gherkin
Feature: Supervision panel — onboarding and chat

  Scenario: [page:onboarding] first visit greets with the onboarding dialog
    Given a supervisor opens the panel for the first time
    When the page loads
    Then a welcome dialog offers a repository and a routing-profile choice

  Scenario: [routing:onboarding-snapshot] the dialog is seeded with governed repos and the active profile
    Given governed targets and a saved active profile
    When the panel fetches its onboarding data
    Then the snapshot carries the selectable targets and the active target

  Scenario: [chat:status-roundtrip] a command sent in the chat round-trips through the bridge
    Given the chat bridge is running in manual mode
    When the supervisor sends a status command
    Then the command output appears in the transcript

  Scenario: [chat:reconnect-replay] a reconnecting stream replays the transcript
    Given a chat session already produced a transcript
    When the browser reconnects to the stream
    Then the prior history is replayed instead of being lost
```

## Test strategy

- Behaviors: `testing/scenarios/m5_ui_panel.py` starts the server in-process on an ephemeral port and asserts token enforcement, snapshot shape, the three refusals, the manual chat round-trip, and orphan-free shutdown. `ui_panel.py`'s `__main__` self-check covers the collector shapes/criticality sort, the refusal matrix, and the bridge lifecycle deterministically (no LLM).
- Edge cases: torn/corrupt state files (each collector degrades to `{}`/`[]`); bare root; bridge restart with a new engine; SSE client disconnect.
- Regression risks: none to harness core (read-only collectors + existing subcommands); watch Windows subprocess env inheritance (UTF-8, `PYTHONUNBUFFERED`) and process-tree kill.
- Coverage impact: enforced for `ui_panel.py` via the scenario + self-check.

## Validation

`./.venv/Scripts/python.exe scripts/harness_lib/ui_panel.py`, `./.venv/Scripts/python.exe testing/scenarios/m5_ui_panel.py`, `./.venv/Scripts/python.exe testing/scenarios/ui_e2e.py` (self-skipping Playwright layer, v5.3 R39), `./.venv/Scripts/python.exe testing/scenarios/worker_live_tail.py` (v6 drill-in data source, SPEC-118), and `scripts/harness-test.py smoke spec-pack scenarios --no-project-commands` all green; plus a live `harness.py ui` smoke check that a token-bearing `GET /` returns the four-tab page. The Gherkin ids above (through the v9 recovery-console block: `recovery:verbs-allowlisted`, `recovery:scrub-excluded`, `recovery:id-validated`, `recovery:needs-confirm`; the v10 discard block: `discard:stopped-allowed`, `discard:running-refused`, `discard:needs-confirm`; the v11 chat-redesign block: `chat:no-engine-selector`, `chat:sessions-new-and-list`, `chat:sessions-independent`, `chat:bypass-local`; and the v12 panel-UX block: `panel:no-costchip`, `panel:branch-shown`, `panel:gates-section`, `panel:confirm-modal`, `panel:card-overflow-guarded`) map to named checks in `testing/scenarios/m5_ui_panel.py` and `testing/scenarios/ui_e2e.py`; the `spec-pack` `feature-spec-conformance` gate enforces the mapping. The chat tab's sessions, the `!` local-command bypass, and engine/overseer selection via `/config` (including an `openai` overseer, which renders cost/ctx `n/a`) are documented in `docs/PANEL_CHAT.md`.

*(amended 2026-07-13, spec-recovery hardening)* `./.venv/Scripts/python.exe testing/scenarios/rh_gui_hardening.py` pins three archaeology-recovered rules: the worker drill-in drawer redacts stdout/stderr tails server-side via `secret_scan.redact_text` (rec-gui-1 — every panel byte crosses the redaction seam, the drawer was the one exception, fixed `48f21fd`); the `rerun-gate` allowlist is exactly `{smoke, spec-pack, scenarios}` with legible refusal (rec-gui-2); every panel action is bounded by `ACTION_TIMEOUT=900s` / `OUTPUT_CAP=8000` chars (rec-gui-6).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Painel servido pelo próprio harness; superfícies convergem num backend | OpenClaw Control UI/Dashboard (docs.openclaw.ai/web/control-ui); OpenHands SDK (arXiv:2511.03690) |
| Python + vanilla JS, zero build | Hermes WebUI (github.com/nesquena/hermes-webui) |
| Chat tab via pipes do REPL, sem PTY/xterm.js | SPEC-111 R1/R15 mode ladder; OpenClaw WebChat como modelo; xterm.js/ttyd exigem PTY+WS |
| SSE + POST, não WebSocket | germano.dev/sse-websockets; Ably SSE vs WS; stdlib http.server serve chunked |
| Stream só com cliente presente | SPEC-111 R27 (teto = ticker do HUD) |
| Fila por criticidade | SPEC-111 R28 tiers; M5.3 human-factors original |
| Protocolo de eventos por pipe (NDJSON, sentinela `\x1e`) | docs.anthropic.com Claude Code SDK (headless `-p --output-format stream-json`); jsonlines.org; RFC 7464 (JSON text sequences usam `\x1e` como separador de registro) |
| Modais nativos `<dialog>` para records/metrics | MDN `<dialog>` (developer.mozilla.org) — foco/Esc/backdrop sem JS de biblioteca |
| Transcrição terminal-parity (um scrollpane monospace) | Hermes WebUI terminal parity (github.com/nesquena/hermes-webui) |
| Spinner "respondendo…" no browser | paridade com o HUD do próprio `chat_hud` (SPEC-111 R22) |

## v2 redesign (2026-07-10) — single-screen panel

Fixes six UX criticisms of the MVP tab layout. Backend routes, token auth, the
allowlist, and `run_action`'s HITL refusal are all unchanged; only the inline
`PAGE`, the chat bridge's stdout handling, and `read_workers` grow. Numbered
requirements continue the list above.

7. **Chat pipe-event protocol.** With env var `HARNESS_CHAT_EVENTS=1`, `harness.py chat` writes machine events to **stdout only** as lines prefixed by the ASCII record separator `\x1e` followed by one compact JSON object. Events: `ready` (idle marker at the top of every REPL loop iteration; carries `mode`/`engine`/`target`), `turn-start` (immediately before `agent.send`), `turn-end` (carries raw `usage` + `session`; `usage: null` on the engine-error path — numbers are passed through, never invented), and `exit` (synthesised by `ChatBridge` when the child's stdout closes and it is dead; carries `rc`). `ChatBridge` sets the env var, parses `\x1e` lines into `{"stream":"evt","data":{…}}`, and passes non-JSON `\x1e` lines through as ordinary output. `harness.py` gains no flag and is byte-for-byte unchanged.
8. **Live busy indicator.** From the moment the supervisor sends a line until the next `ready` event, the transcript shows an animated last line (`⠋ respondendo… <n>s`) driven by a JS interval; `ready` removes it. An `exit` event replaces it with a dimmed `bridge encerrado (rc N) — Restart` affordance. This is the browser peer of the terminal HUD spinner (SPEC-111 R22).
9. **Single-screen layout.** One `100vh` CSS-grid/flex shell with **no page scroll**: header bar, left ledger-head column, centre terminal transcript (one monospace `white-space: pre-wrap` scrollpane — not per-line bubbles; consecutive blank lines collapse; autoscroll only when already at the bottom) with a bottom-pinned input row, and a right column of Agents + Escalations cards. Each region scrolls internally. Records and Metrics open as native `<dialog>` modals (Esc/backdrop close); Metrics renders human-readable sections (chat turns, delegations, workflows, records, top-expensive) instead of raw JSON.
10. **Segmented telemetry chips.** Between transcript and input, a chip bar reads from the last `turn-end` event: context bar+percent, `in`/`out` tokens, `$cost`, duration, and `sessão $X/N turns`. Any missing field renders a dimmed `n/a` chip — the panel never fabricates a number (R24 parity).
11. **Workers include finished.** The snapshot calls `chat_hud.read_workers(root, now, include_done=True)`, so the Agents column shows finished workers (dimmed, five most recent, each carrying `finishedAt` = `run.finishedAt` or `updatedAt`) alongside active ones. Existing HUD callers omit the flag and keep active-only behaviour.
12. **Mode visible + Shift+Tab.** A header mode badge shows the current REPL mode from the last `ready` event. Clicking it, or pressing **Shift+Tab** anywhere on the page, sends `/mode <next>` over `POST /api/chat/send`, cycling the hardcoded `chat_engines.MODES` order (`manual → plan → auto → accept-edits`); the badge follows the resulting `ready` event, so it reflects what the REPL actually accepted (e.g. the manual engine refuses non-manual modes).

**Ceilings (upgrade paths).** No intra-turn token streaming: `turn-end` telemetry lands only after the agent reply completes — the upgrade path is parsing `claude -p --output-format stream-json` inside `ClaudeEngine`. Vendor-CLI internal subagents expose no per-session data, so only harness workers (from workflow state) appear in the Agents column; a vendor CLI's own nested agents stay invisible by design.

### v2 test strategy

`ui_panel.py` and `chat_operator.py` `__main__` self-checks assert the emit-lambda shape and that a real manual-engine bridge round-trip yields a `ready` evt and, after `/exit`, an `exit` evt. `chat_hud.py`'s self-check covers `include_done` + `finishedAt`. `testing/scenarios/m5_ui_panel.py` adds: the SSE round-trip surfaces a `ready` evt, `/exit` produces an `exit` evt, `read_workers(include_done=True)` returns a synthetic finished worker the default call excludes, and `harness_ui.PAGE` contains `<dialog` and the mode-badge element. All headless and deterministic (bridge in `--engine manual`, no LLM).

## v3 (2026-07-10) — engine identity, layout polish, resizable columns, metrics panel

Live-dogfeeding feedback on the v2 single-screen panel, plus a root-cause fix for
an operator that got stuck in plan mode. Backend routes, token auth, the
allowlist, and `run_action`'s HITL refusal are unchanged; the `PAGE` string, two
engine telemetry dicts, and the `ready` emit grow, and `ClaudeEngine` gains a
per-turn permission-mode. Numbered requirements continue the list above.

13. **Engine identity chip.** First `#chips` chip renders `⚙ provider · model · effort`; provider derives from engine (claude→anthropic, codex→openai, openai→endpoint host, manual/absent→manual); model is the measured id from the last `turn-end` when present, else the configured value from `ready`, else a dimmed `default`; the tooltip states engine/endpoint and whether the model is configured or measured. Backend: the `ready` emit gains `model`/`effort`/`endpoint` (from `cfg`, may be null); `turn-end` usage gains the actual `model` — Claude from the dominant `modelUsage` key, OpenAI from `self.model`. Honest-n/a holds (R24): never fabricate, dim the unknown.
14. **Mode badge re-homed** from the header to the right of the `#chips` bar (a `.spacer` pushes it above the Send button); same id, click handler, and Shift+Tab cycle as v2 — it is now a persistent child of `#chips` that `renderTelemetry` never rebuilds (telemetry writes into an inner `#telchips`).
15. **Snapshot timestamp off the header** — the `gen …` span is deleted; `renderHeader` instead sets `title="snapshot <generatedAt>"` on `<h1 id="h1t">`, keeping the metadata inspectable at zero pixels.
16. **Resizable column dividers** — two 6px `.split` handles (left|center, center|right) driven by native pointer events + `setPointerCapture`; drag clamps the adjacent column to 12rem..~45vw, both widths persist in `localStorage` (`harness.panel.leftW`/`rightW`) and restore on load; double-click a handle resets that column to the CSS default.
17. **Metrics summary under the ledger** — the left column becomes a flex column with an internally-scrolling `Ledger head` (flex 1) and `Metrics` (`flex: 0 0 50%`). The modal's rendering is extracted into a shared `metricsHtml(m, topN)` used by both the panel section (compact core, top-3) and the modal (full view, top-5). `refresh()` fetches `/api/metrics` only every 3rd tick (~9s, it re-reads the records ledger); the modal still fetches fresh on open.
18. **Input history + target label** — an in-memory list of sent lines with ArrowUp/ArrowDown recall in `#chatin` (classic REPL, resets on send, no persistence); a dim `→ <target>` header label from the `ready` event when non-null (parity with the HUD's `repo→target`).
19. **REPL mode governs the vendor session.** The Claude engine's per-turn argv (built by the pure `ClaudeEngine._argv`) ALWAYS passes an explicit `--permission-mode`: `plan` in plan mode, `acceptEdits` in accept-edits mode, `auto` otherwise — never omitted — and always passes `--disallowedTools EnterPlanMode ExitPlanMode`. The `MODE_TAGS` prompt text stays for cross-engine parity. *Incident (2026-07-10):* `/mode` was a prompt tag plus an internal gate only — the underlying `claude -p` session never received `--permission-mode`, so the agent self-entered plan mode via `EnterPlanMode`, and leaving plan mode needs an interactive approval that a headless `-p --resume` turn cannot give; the session and its spawned subagent stayed stuck. *Second incident (2026-07-10, same day):* the first fix omitted the flag outside plan/accept-edits "to preserve the CLI default" — but the CLI default IS user-scope config: this machine's `~/.claude/settings.json` sets `permissions.defaultMode: "plan"` (the user's deliberate plan-first preference for interactive sessions), so in auto mode the headless session was born in plan mode, now with `ExitPlanMode` disallowed — the panel badge said `auto` while the model answered "estou em plan mode". The same inherited default explains the earlier "subagents spawn in plan mode" observations. Rule: a headless engine session must never inherit interactive permission defaults — the REPL mode is the single source of truth and is always stated explicitly.
20. **Codex engine — real session against the installed CLI.** `CodexEngine` finds the binary via `shutil.which("codex")` or, when codex ships off PATH (the Windows installer drops it at `%LOCALAPPDATA%\Programs\OpenAI\Codex\bin\codex.exe`), that install path — the prior code raised a false "not found on PATH" despite codex being installed and authenticated. Every turn runs `codex exec --json` and the pure `_parse` folds the JSONL stream: `thread.started` → the session `thread_id` (resume is `exec resume <thread_id>`, *not* `resume --last`, which kills the wrong-session race when a human drives codex in parallel); `item.completed`/`agent_message` → the reply (blank-line joined); `item.completed`/`error` → surfaced inline as `[codex: …]` (not swallowed); `turn.completed`/`usage` → telemetry with raw `input_tokens`/`output_tokens` (honest-n/a: reasoning tokens are *not* summed into out, cost is null, model is the configured `-m` value or null since events carry no id). No agent_message → raw stdout fallback. The REPL mode governs codex's real sandbox (R19 parity) via the pure `CodexEngine._argv`: fresh exec adds `-s read-only` (plan) / `-s workspace-write` (accept-edits) / no flag otherwise (CLI default preserved); resume has no `-s`, so the same modes map to `-c sandbox_mode="…"` — **validated live 2026-07-10**: a read-only session resumed with `-c sandbox_mode="workspace-write"` created a file it had just been refused (`item.type == "file_change"` emitted), proving the override re-enforces mid-session. The panel's engine `<select>` and the `/api/chat/restart` engine allowlist gain `codex`.

21. **Resolved engine identity — no bare "default" for a card-backed engine.** Config resolution order becomes flag > env > saved prefs > **model-card default** > vendor default (`chat_setup._resolve_config`, which gains a `root` param to read the registry). When nothing above chooses a model and the engine is card-backed (`claude`→`fable`, `codex`→`gpt-5.5`, via the `"default": true` card), the model resolves to that card id (source `card default`) and, if no effort was set, to the card's new `defaultReasoning` field (fable `high` — repo policy; gpt-5.5 `medium` — the codex CLI's own observed banner default). These resolved values flow through `build_engine` into the real CLI invocation (`--model fable --effort high` for claude; `-c model_reasoning_effort="…"` for codex), so **what the chip shows is what runs** (honest-visibility). Cardless engines (openai without cards, manual) keep the vendor default; the chip renders a dimmed `vendor default` instead of a bare `default`, and the tooltip names the source (`card default` / `saved default` / `flag` / `vendor default`) via a new `modelSource` key on the `ready` emit. *Root cause of the "⚙ anthropic · default · default" feedback (2026-07-10):* with no prefs file the resolver stopped at `(None, "default")` and passed nothing to the CLI, so the vendor's invisible default ran while the registry's declared defaults were never consulted. **Codex effort — validated live 2026-07-10:** `'' | codex.exe exec -c model_reasoning_effort="low" "…"` prints banner `reasoning effort: low` (model gpt-5.5), so codex honors the config override despite having no `--effort` flag; `CodexEngine` now takes `effort` and emits `-c model_reasoning_effort="{effort}"` on both fresh exec and resume (parity with the R20 sandbox `-c` override).

22. **Bridge auto-connects on panel open.** `_stream_chat` starts the bridge (under `server.bridge_lock`; `bridge.start` is idempotent under its own `bridge._lock` — different locks, consistent acquire order, no nesting hazard with `stop()`) before entering the SSE loop, so the GET `/api/chat/stream` that every page load issues boots `harness.py chat` with the default/prefs engine: banner lines + the first `ready` event flow immediately, populating the chip and mode badge with no manual "Restart bridge". The Restart button stays — it remains the way to switch engine (POST `/api/chat/restart` stops then restarts with the chosen one). SSE is a terminal response, so the handler sets `close_connection` and `PanelServer.handle_error` swallows the routine `ConnectionError` a disconnecting client raises (no stdlib traceback on tab close / stream drop). *Root cause of the "must click Restart before chatting" feedback (2026-07-10):* the bridge previously started only on the first POST `/api/chat/send`, so a fresh page's SSE stream attached to a dead bridge and no `ready`/banner ever arrived.

**Ceilings (upgrade paths).** No per-keystroke width throttle and localStorage-only persistence for column widths; the panel metrics fetch is a coarse 3-tick counter, not event-driven. Codex telemetry (R20) reports raw `input_tokens`/`output_tokens` but no cost, no context window, and no model id (codex events carry none — the configured `-m` value is echoed, else null). The openai mode stays tag-only — its CLI exposes no `--permission-mode`/sandbox flag to wire, so structural mode enforcement is Claude-and-codex only. R21 resolves openai/manual to `vendor default` (they have no card to fall through to); wiring an openai default would need per-endpoint cards.

| Decisão | Fontes |
|---|---|
| Colunas redimensionáveis via pointer events nativos + `localStorage` | MDN Pointer Events / `setPointerCapture` (developer.mozilla.org) |
| Chip de identidade do engine (provider·model·effort) | paridade com o HUD do terminal (`chat_operator.py` mostra `engine·model·effort`) |
| R19: o modo do REPL governa a sessão vendor via `--permission-mode` por turno | `claude --help` nesta máquina lista `--permission-mode <mode>` (choices incluem `plan`, `acceptEdits`) e `--disallowedTools <tools...>`; cada turno é uma invocação `-p --resume` nova, então a flag por turno troca o modo REAL; incidente 2026-07-10 (planos salvos em `~/.claude/plans` + relato do usuário) |
| R20: engine codex roda contra o CLI instalado — descoberta com fallback fora do PATH, resume por `thread_id`, telemetria via `exec --json`, modo→sandbox (`-s` no fresh / `-c sandbox_mode` no resume) | `codex exec --help` / `exec resume --help` nesta máquina (codex-cli 0.144.1): fresh tem `-s <read-only\|workspace-write\|danger-full-access>`, resume não tem `-s` mas aceita `-c <key=value>`; fixture JSONL real 2026-07-10 (`thread.started`/`item.completed`/`turn.completed`); recon do incidente (binário fora do PATH → `which` falha; stdin sem `-` trava esperando EOF); validação live 2026-07-10: sessão read-only retomada com `-c sandbox_mode="workspace-write"` escreveu o arquivo antes recusado |
| R21: resolução cai para o default do model-card (fable/gpt-5.5) e os valores resolvidos vão para o CLI (displayed == executed); codex-effort via `-c model_reasoning_effort` | registro de model-cards SPEC-111 R17/R18 (`.harness/routing/model-cards.json`, campos `default`/`defaultReasoning`); banner do codex 2026-07-10 (`reasoning effort: low` com `-c model_reasoning_effort="low"`, model gpt-5.5); feedback do usuário 2026-07-10 ("⚙ anthropic · default · default"); prova live claude 2026-07-10 (ready evt → `fable`/`high`/`card default`, sem turno). **SPEC-115:** a cadeia de resolução é INALTERADA (fall-through ao card default sob canônico); o dono VISÍVEL do "default" passa a ser o papel `overseer` (o card `default` vira só fallback de pré-seleção do wizard). |
| R22: o connect do SSE auto-inicia o bridge com o engine default/prefs; Restart continua para troca de engine | feedback do usuário 2026-07-10 ("Restart antes de conversar"); paridade com POST `/api/chat/send`, que já iniciava o bridge de forma idempotente sob o mesmo `bridge_lock` |

### v3 test strategy

`chat_operator.py`'s self-check asserts the `ready` emit carries `model`/`effort`/`endpoint` and updates the `_telemetry` expectation to include the measured `model`. `testing/scenarios/m5_ui_panel.py` adds: the SSE `ready` evt carries the identity keys; `PAGE` contains the engine chip, a `.split` handle, the metrics panel, and the mode badge *inside* `#chips` (not the header); and `engine:plan-permission-mode` builds a `ClaudeEngine` via `__new__` (no binary) and asserts plan mode yields `--permission-mode plan` + disallowed Enter/ExitPlanMode while auto omits the flag. R20 adds three more, all via `CodexEngine.__new__` (no binary): `codex:argv-plan` (fresh plan → `-s read-only`, auto omits `-s`), `codex:jsonl-parse` (the verbatim `exec --json` fixture folds to a `pong` reply with the error surfaced inline and `input_tokens`/`output_tokens`/`thread_id` captured), and `page:codex-option`. The live engine round-trip and sandbox-on-resume proofs are one-time validations, *not* scenario checks — they burn real codex tokens. All deterministic, no LLM. The existing v1/v2 checks stay green.

R21/R22 add four more deterministic checks (no LLM): `config:card-default` (a synthetic registry on a tmp root → `_resolve_config(engine=claude, no prefs)` resolves model + effort to the card default with source `card default`), `config:flag-wins` (an explicit `--model` still beats the card), `chat:autostart` (a GET `/api/chat/stream` on a fresh, never-POSTed `--engine manual` server yields a `ready` evt — the SSE connect itself booted the REPL, proving R22), and `page:vendor-default-label` (`PAGE` carries the `vendor default` wording); `codex:argv-plan` also asserts the effort override `-c model_reasoning_effort="low"`. The live claude identity proof (boot the default bridge with no prefs, read `ready` → `fable`/`high`/`card default`, `/exit` — the `ready` event precedes any turn, so no tokens) and the codex `reasoning effort: low` banner check are one-time validations, not scenario checks.

## v4 (2026-07-10) — mode-in-input, real reconnection, auto-open, visual ledger/metrics

Five dogfeeding points on the v3 panel. Backend routes, token auth, the allowlist,
and `run_action`'s HITL refusal are unchanged; the `PAGE` string, `ChatBridge`
(a bounded replay log), `_stream_chat` (replay + single-reader takeover), `serve`
(auto-open), and one `records` helper grow. Numbered requirements continue the list.

23. **Mode badge on the input row.** The `#modeBadge` moves out of `#chips` to the
    left of `#chatin` (input row `[#modeBadge][#chatin][Send]`), matching where other
    agent CLIs put the mode indicator; `#chips` keeps only the engine chip + `#telchips`.
    Same element id, click handler, and Shift+Tab cycle — markup + CSS only. *Root cause:*
    v3 R14 parked the badge at the end of the chips bar, which by v3 also carried the
    engine chip plus six telemetry chips — on narrower windows the bar overflowed and
    "the Send button didn't fit".

24. **Real reconnection (the load-bearing fix).** `ChatBridge` gains a bounded
    `history` (`deque(maxlen=400)`): every item `_drain` queues is also appended to
    history, and `send()` appends the user's own line as `{"stream":"you", …}` to
    **history only** (the front echoes live sends locally). `start()` clears history
    (new session = fresh transcript). `_stream_chat`, under `bridge_lock`, increments a
    `PanelServer.sse_gen` and remembers its own generation; after the SSE headers it
    discards the queued backlog (all already in history) and replays `list(history)` as
    normal SSE frames, then enters the live loop, returning immediately once
    `sse_gen != my_gen`. The front renders replayed `you` items as `❯ line` and wipes
    the pane on every EventSource `onopen` so a (re)connect rebuilds the transcript from
    the replay instead of stacking a duplicate. *Root cause (2026-07-10, "I keep having
    to press Restart bridge"):* v3 R22 only covered the first connect. The stream drained
    a **single shared queue with no replay** — if the bridge was already alive (page
    reload, second tab, server already running) the banner/`ready` of that session had
    **already been consumed**, so the new client got silence until the next event; worse,
    the previous connection's **zombie reader kept stealing events off the shared queue**
    for up to the 15 s heartbeat. Restart "fixed" it only because it killed and recreated
    the bridge, minting a fresh banner. *Single-viewer ceiling:* the last-opened tab owns
    the live stream; the `sse_gen` bump stops older readers stealing events, so an older
    tab's stream freezes (state polling continues). Two tabs kept open can slow-alternate
    ownership as EventSource reconnects — acceptable for a loopback single-user panel.
    *Residual race:* an item appended to history but not yet queued at the instant of a
    connect can be both replayed and delivered live once (harmless duplicate; loss cannot
    happen because history is appended before the queue).

25. **Auto-open the browser.** `serve()` builds the token URL, prints it, then calls
    `webbrowser.open(url)` (best-effort, try/except) unless `open_browser=False`; `main()`
    gains `--no-open` to opt out. `make_server` (used by the scenario/tests) opens nothing,
    so gates and CI stay popup-free. *Root cause:* the per-session token is minted in
    Python inside `serve()`, so `ui.bat` cannot know the URL — the auto-open belongs to
    `serve()`, not the launcher.

25b. **A spawned panel cannot outlive the run that spawned it (amendment 2026-07-24).**
    `serve()` accepts `exit_after`, exposed as `--exit-after-seconds N` on `main()` and on
    the `ui` verb; omitted means serve forever, so the owner's own panel is untouched.
    When set, a daemon `threading.Timer` calls `server.shutdown()` — not `os._exit` — so
    the existing `finally` and the `atexit` reapers still run and the autostart services
    go down exactly as on a clean stop.

    *Root cause:* requirement 25's cleanup is correct on every path the caller controls,
    and none of it survives a hard kill — `finally` does not run under SIGKILL, and
    neither does `atexit`. Measured 2026-07-24: two panels spawned by `pw_ui_smoke` on
    2026-07-22 were still serving two days later, ~30s CPU each, holding their ephemeral
    ports. The only bound that survives the parent's death is one the child imposes on
    itself. A reaper matching on argv was rejected: it could not distinguish a leaked
    test panel from the owner's live one, and killing the owner's panel is a worse bug
    than leaking a test's. `pw_ui_smoke` passes 900s, far beyond its own budget (40s
    ready + two 180s node runs), so the bound can only ever fire on an abandoned server.

26. **Structured ledger cards.** The snapshot gains a `ledger` field =
    `records.tail(root)` (the last worklog entries as `{kind,title,refs,tags,at}` handles,
    reusing the canonical `_load`), and the left column renders compact cards: a colored
    kind badge (milestone→blue, decision→purple, note→gray, fix/incident→amber; unknown→
    neutral), a two-line ellipsised title, a dim 7-char mono ref, and tag micro-badges;
    empty → "sem registros". *Root cause:* v3 sent the rendered markdown head string
    (`ledgerHead`) and the browser showed it as monospace text; the structured source is
    the worklog JSON (SPEC-112 canonical), so the panel consumes that directly rather than
    parsing a projection's markdown. `ledgerHead` stays in the snapshot for API consumers;
    the front no longer reads it.

27. **Metrics mini-dashboard.** `metricsHtml(m, topN)` is replaced by a shared
    `metricsTiles(m, compact)` used by both the left panel (compact) and the modal (full):
    a stat-tile grid (big number + small label + tone accent — Sessão $, Turns, Delegações
    with a ~tokens sub-label, Workflows, Records) and `topExpensive` as horizontal CSS
    mini-bars (width % relative to the max entry; label = kind badge + short id + $/~tok).
    Honest-n/a holds (R24 parity): a missing number renders a dimmed `n/a`, never invented.
    Pure CSS on the existing tone palette — no canvas, no libraries (CSP self-contained).
    *Root cause:* v3 R17 rendered `<h3>` + paragraphs with no visual hierarchy; the ask was
    a real mini-dashboard in the style of agent GUIs.

| Decisão | Fontes |
|---|---|
| R24: replay do histórico no connect + consumidor vivo único (última aba vence) | modelo mental do SSE `Last-Event-ID`/replay ([MDN Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)) simplificado para replay-completo-no-connect (painel loopback, transcript bounded); incidente reproduzível: v3 `chat:autostart` só cobria bridge morto — o caso vivo (fila compartilhada já consumida + zumbi roubando eventos) não tinha check |
| R25: `webbrowser.open` no `serve()` com opt-out `--no-open` | stdlib ([docs.python.org/3/library/webbrowser](https://docs.python.org/3/library/webbrowser.html)) — abre o navegador default em qualquer OS; o `.bat` não conhece o token |
| R25b: teto de vida OPT-IN no próprio servidor, em vez de reaper por argv | dois painéis vazados de 2026-07-22 ainda servindo em 2026-07-24: nenhum cleanup de userspace sobrevive a SIGKILL do pai, então só um limite auto-imposto vale; opt-in porque um reaper não distingue painel de teste vazado do painel VIVO do dono, e matar o do dono é bug pior que o vazamento |
| R26: snapshot entrega o worklog estruturado (fonte), não o parse da projeção markdown no browser | worklog.json é canônico (SPEC-112); parsear markdown renderizado acoplaria no formato da projeção |
| R27: stat tiles + mini-bars CSS puros | dashboards de agente ([OpenClaw Control UI](https://docs.openclaw.ai/web/control-ui) — cards de status; Hermes WebUI — parity minimalista); zero libs (CSP self-contained) |
| R23: badge de modo à esquerda do input | paridade com Claude Code/Codex CLIs (indicador de modo junto ao prompt), pedido literal |

### v4 test strategy

`ui_panel.py`'s self-check adds a synthetic worklog entry (asserting `state_snapshot`
carries a structured `ledger[0].kind == "milestone"`) and asserts the bridge round-trip
leaves both a `you` line and the `ready` evt in `history` (the replay source).
`testing/scenarios/m5_ui_panel.py` replaces `page:modebadge-in-chips` with
`page:modebadge-input-row` (badge in the input row, left of `#chatin`, out of header/chips)
and adds: `page:stat-tiles` (the `metricsTiles` grid), `bridge:history-you`,
`state:ledger-structured`, `ui:no-open-flag` (a real `main(["--no-open"])` round-trip
threads `open_browser=False` into a stubbed `serve`, and `webbrowser.open` is present only
in `serve`), `ui:exit-after` (R25b — a REAL subprocess panel with `--exit-after-seconds 3`
must exit on its own; a process cannot demonstrate its own exit in-process. There is
deliberately no wall-clock assertion — a timed ceiling in a scenario is a flake generator
under shard contention — so the bound is the tree-bounded runner's timeout, which also
means a FAILING run of this check cannot leak the server it is testing. Mutant removing
the timer KILLED: `selfStopped=False rc=None after=90.3s`), and the critical
`chat:reconnect-replay` — a fresh stream GET against an
already-alive bridge whose queue was drained still delivers a `ready` via history replay,
the direct repro of the user's bug. All headless and deterministic (bridge in
`--engine manual`, no LLM); the v1/v2/v3 checks stay green (29/29 total).

## v5 (2026-07-10) — onboarding: repository + routing-profile choice on open

The panel opened straight into implicit state (target from prefs, global active
profile) and switching either was undiscoverable ("how do I change my profile in
the GUI?"). v5 adds a first-run `<dialog>` and an always-reopenable header chip.
No new backend route, no new harness state file (the flag is `localStorage`, pure
UI state like the R16 column widths). Numbered requirements continue the list.

28. **`/repo <name>` works in no-input (piped) mode.** The chat REPL's `/repo`
    handler refused the whole command in `--no-input`; the refusal now fires **only
    when there is no argument** (the interactive picker is the only part that needs a
    prompt). `/repo <name>` resolves via `targets_lib.resolve` — an unknown target
    already surfaces as `harness error: …`. `/repo .` clears the target ("back to this
    repo"), the piped-safe form the GUI uses (an argless `/repo` still opens the picker,
    which no-input cannot). *Root cause:* the blanket refusal existed for the picker
    prompt, not for the deterministic resolve — the bridge is the panel's only path to
    switch repo (invariant nº1/nº6: nothing panel-only; the terminal already has `/repo`).

29. **Onboarding snapshot.** `routing_snapshot` (`/api/routing`) gains `targets`
    (sorted `targets_lib.load_targets()` names, never-crash → `[]`) and `activeTarget`
    (the chat prefs' saved target via `chat_setup._load_prefs`, never-crash → `null`) —
    the dialog's repository preselect. No new route.

30. **Onboarding dialog + header chip.** A welcome `<dialog>` auto-opens when
    `localStorage["harness.panel.onboarded"]` is absent and is always reopenable via a
    permanent header chip `📁 <repo|target> · perfil <ativo>` (the discoverability fix).
    It offers: (1) a repository `<select>` — "este repo (<name>)" + governed targets,
    preselecting `activeTarget`; applying sends `/repo <name>` (or `/repo .` to clear)
    through the chat bridge; (2) a routing-profile `<select>` (canonical + saved,
    marking the active) → the existing `routing-profile-use` action; (3) an optional
    "vincular este perfil a este repositório" checkbox (enabled when a target is chosen
    and profile ≠ canonical) → `routing-target-assign`; (4) an info line when the chosen
    repo has a perTarget binding; (5) `começar` (apply + set the flag) and `pular` (flag
    only). The chip is fed by the `ready` evt (target) and `/api/routing` (active profile).
    esc() on every interpolated name; CSP self-contained. *Ceiling:* switching repo via
    the dialog requires an already-governed target — registering a **new** target stays
    in the terminal/interactive REPL (the argless picker no-input cannot run).

| Decisão | Fontes |
|---|---|
| Onboarding como `<dialog>` de primeira abertura + reabrível por um chip permanente (repo · perfil) | Paridade com o onboarding do REPL (SPEC-111 R11/R25); feedback direto ("como mudo o perfil?" = affordance fraca); padrão first-run dialog + settings entry point ([OpenClaw Control UI](https://docs.openclaw.ai/web/control-ui) onboarding/config) |
| Troca de repo via `/repo <nome>`/`/repo .` pelo bridge (não uma rota nova) | Invariante SPEC-114 nº1/nº6 (nada painel-only; o terminal já tem `/repo`); destravar só o caso com argumento explícito em no-input — o bloqueio existia pelo picker interativo, não pelo resolve |
| "Não mostrar de novo" em `localStorage` (client-side) | Estado de UI puro, não estado do harness (mesmo padrão das larguras de coluna R16); o harness não ganha arquivo novo |
| Vínculo opcional perfil↔repo no mesmo diálogo | `routing target assign` já existe (SPEC-115); o onboarding é o momento natural de oferecer |

### v5 test strategy

`chat_operator.py`'s `/repo` unlock is proven end-to-end by the bridge (loop-internal
branch, not unit-extractable). `ui_panel.py`'s self-check asserts `routing_snapshot`
carries `activeTarget` (→ `None` on a bare root, → the saved target after `_save_prefs`).
`testing/scenarios/m5_ui_panel.py` adds three (29 → 32): `chat:repo-arg-piped` (the bridge
sends `/repo nome-inexistente-xyz` in no-input and the output is `harness error`, **not**
"prompts are disabled" — proves R28 without a real target), `routing:onboarding-snapshot`
(`/api/routing` carries a `targets` list + an `activeTarget` key), and `page:onboarding`
(PAGE contains the `onboardDlg` dialog + `onboardChip` header chip). Headless/deterministic;
all prior checks stay green.

## v5.1 (2026-07-10) — onboarding corrections + native folder picker

Dogfood feedback on v5: the "vincular perfil↔repo" checkbox appeared inert, and the
repository `<select>` only offered already-governed targets — no way to reach a project
outside `.harness/targets/`, and same-named repos were indistinguishable.

31. **Bind flow fixed at the root.** The checkbox is enabled only when a real target is
    chosen **and** the profile ≠ canonical (a binding to canonical is meaningless). The
    v5 code already wired `obRefreshBind` to both selects' `onchange` and called it after
    populating them — so the enable/disable is live. The two genuine defects were: (a) the
    info line double-escaped (`textContent = … esc(value)` — `textContent` already escapes,
    so a `&`/`<` in a profile name rendered as `&amp;`); fixed to pass the raw value. (b) The
    perceived "does nothing" root cause was the **dead-end**: on a fresh setup there is no
    governed target and no non-canonical profile, so the box is (correctly) permanently
    disabled — the user has nothing to enable it with. R32 removes the dead-end by letting
    the user register a target from the dialog. The `começar` bind round-trip
    (`routing-target-assign` with the dialog's exact `{target, profile, confirm:true}`)
    is proven landing in `model-routing.json` on a tmp root (`routing:bind-roundtrip`).

32. **OS-native folder picker + `targets add`.** A `procurar pasta…` button opens a native
    directory dialog. Browsers cannot expose OS absolute paths (the File System Access API's
    `showDirectoryPicker` yields opaque handles, not filesystem paths), but the panel server
    is loopback-local, so the **server** opens the dialog: `ui_panel.pick_folder()` runs
    `tkinter.filedialog.askdirectory` in a short-lived **subprocess** (Tk cannot run inside the
    handler thread) and returns the chosen path or `""` (cancel/headless). It never raises and
    mutates nothing — a pure UI affordance behind the token-guarded `POST /api/pick-folder`. The
    actual **registration** is the allowlisted `targets add <name> <path>` subcommand
    (`targets-add` action, mutating→confirm), keeping the single write path. Registration lives
    in `targets_lib.register(root, name, path)` (validates: dir exists, has `.git` — a governed
    target is a repo — refuses duplicates naming the existing path); `chat_setup._register_target`
    now delegates to it, so target registration has exactly one writer.

33. **Full paths in the selector.** `routing_snapshot.targets` is now `[{name, root}]`
    (`targets_lib.target_root`, never-crash per entry) and the repo `<select>` renders
    `nome — C:\caminho\completo` (path also in the `title` tooltip); "este repo" shows the
    server root path (`__HARNESS_ROOT__`, JSON-encoded at injection so Windows backslashes
    stay a valid JS string). Same-named repos in different directories are now distinguishable.

| Decisão | Fontes |
|---|---|
| Picker nativo aberto pelo **servidor** (não pelo browser) | Browsers não expõem caminhos OS absolutos — File System Access API `showDirectoryPicker` retorna handles opacos ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/Window/showDirectoryPicker)); servidor é loopback-local, então abre o diálogo do stdlib ([`tkinter.filedialog`](https://docs.python.org/3/library/tkinter.filedialog.html)) |
| Tk em **subprocess**, timeout 300s, nunca levanta | Tk exige a main thread e um display; rodá-lo no handler thread trava o servidor. Subprocess isola o loop de eventos; timeout largo porque há interação humana; falha/headless → `""` |
| Registro via `targets add` (subcomando allowlisted), não uma escrita nova no handler | Invariante SPEC-114 nº1/nº6 (nada painel-only; caminho de escrita único); picker apenas devolve string, `targets add` grava |
| `register()` exige `.git` e recusa duplicata | Um target governado é um repositório (SPEC-110); falhar cedo e legível (nomeando o caminho) evita registrar pastas arbitrárias |
| Caminhos completos no `<select>` (`nome — caminho`) | Feedback: repos homônimos em diretórios diferentes eram indistinguíveis; `__HARNESS_ROOT__` JSON-encoded evita quebrar a string JS no Windows |

*Ceiling:* the picker requires a desktop session — a headless/SSH server returns `""`
(the terminal/interactive REPL browse-and-register path remains for those). `load_targets`
is fixed to the harness root, so the panel governs the server's own repo (by design).

`testing/scenarios/m5_ui_panel.py` adds three (32 → 35): `action:targets-add` (build shape,
unconfirmed refusal, `register` lands a profile + refuses a duplicate on a tmp root),
`routing:bind-roundtrip` (the dialog payload lands a perTarget binding on a tmp root), and
`page:folder-picker` (PAGE carries the browse button + `/api/pick-folder`); the snapshot check
also asserts each `targets` entry carries `name`+`root`. `ui_panel`'s self-check covers
`pick_folder` by faking the Tk subprocess (never popping a real dialog).

## v5.2 (2026-07-10) — path caption, last-used-per-repo policy, target-aware resolution

Feedback on v5.1: (a) the full paths appended to each repo `<option>` (R33) blew up the
`<select>` width; (b) the bind checkbox still "did nothing", and the user proposed replacing
it with a policy — *use the last profile the user selected when running in this repo*.

34. **Path caption below the select.** Repo `<option>`s show the **name only** now; the full
    path moves to a dim `#obRepoPath` caption line **below** the select (and stays in the
    `title` tooltip). `obSyncRepo` sets the caption from the selected option's `.title` on
    every change — covering "este repo" too. Option markup keeps `esc()` (innerHTML); the
    caption and info line use `textContent` (no double-escape). Applies to the onboarding
    dialog; the config-view keeps its per-target **chips**, which already show names only with
    the path in the `title` tooltip (no option-text width bug there).

35. **Last-used-per-repo replaces the bind checkbox.** The `#obBind` checkbox and its
    enable/disable logic are removed. On `começar`, when a governed target X is selected and
    profile P applied: P ≠ canonical → `routing-target-assign {target:X, profile:P}`; P ==
    canonical → `routing-target-clear {target:X}` (clears a stale binding); no target → neither.
    Selecting a repo in the dialog auto-syncs the profile `<select>` to what that repo remembers
    (`perTarget[X]`, else the active profile) with the info line *"este repo lembra o perfil
    &lt;Y&gt;"*. The config-view per-target chips stay the explicit management surface; the dialog
    is the ergonomic one.

    **Two-layer root cause (recorded honestly).** The v5.1 binding *did* land in
    `model-routing.json.perTarget`, but **nothing read it on the live paths** — the state was
    written and never consumed, so the checkbox was simultaneously "working" and useless.
    `chat_setup._resolve_config`'s routing rung called `resolve_role(root, OVERSEER, executor=…)`
    with **no `target=`**, and `harness.py`'s `route_spawn` call sites passed no target either.
    R36 closes the read side; the spawn side is a documented ceiling.

36. **Target-aware resolution (the true fix).** `_resolve_config` gains `target: str | None =
    None` and derives the effective target as `flag > prefs["target"]` (read **before** the
    engine-switch strip can drop it), threading it into the overseer routing rung. `run_chat`
    hoists the same hint above `cfg` (cfg resolves before the target block) and passes it to
    `_resolve_config` and `build_engine`; `build_engine` → `model_routing.chat_fallbacks` forward
    it so the construction-failover walk resolves the same perTarget overseer chain.
    **Effect:** with `prefs.target = X` and `perTarget[X] = P` (P defines overseer), a piped
    `chat` resolves the overseer model from P (`source == "routing"`) — the user-visible proof
    that binding a profile to a repo now means something.

    *Spawn ceiling.* `model_routing.route_spawn`/`resolve_role`/`chat_fallbacks` already accept
    and forward a `target`, but **no `harness.py` spawn caller has one to give** today:
    `spawn-command` (`cmd_spawn`) has no `--target`, and workflow-worker spawn
    (`run_one_worker` → `workflow_spawn_command_for_prompt` → `executor_profile_spawn`) is not
    target-parameterized. Rather than invent plumbing, we leave it: **workflow/spawn commands
    honor `perTarget` only once the caller passes a `--target`.** `harness.py` is unchanged
    (0 lines).

| Decisão | Fontes |
|---|---|
| Nome só no `<option>`; caminho na legenda abaixo + tooltip | Feedback 2026-07-10: caminhos completos no texto do `<option>` estouravam a largura do select |
| Política *último perfil usado por repo* substitui o checkbox de vínculo | Proposta do usuário (2026-07-10); precedente: configurações lembradas por projeto em IDEs/editores (ex.: workspace settings do VS Code) |
| `_resolve_config`/`build_engine` recebem o alvo da sessão; o rung de roteamento resolve `perTarget` | Causa-raiz de duas camadas: o estado era gravado mas nunca lido nas rotas vivas (`resolve_role` sem `target=`) |
| `harness.py` inalterado; teto documentado | Nenhum call site de spawn conhece um alvo hoje; não inventar plumbing (YAGNI) |

`testing/scenarios/m5_ui_panel.py` (35 → 38): `routing:bind-roundtrip` is replaced by the policy
pair `routing:policy-assign` (non-canonical → assign lands) and `routing:policy-clear` (canonical
→ clear removes the binding); `page:path-caption` (the `#obRepoPath` caption exists and repo
options are name-only, path only in the tooltip) and `page:no-obbind` (no `obBind` identifier
survives in PAGE) are added. `testing/scenarios/mr_model_routing.py` (17 → 18) adds
`module:pertarget-drives-chat-rung`: `_resolve_config` with `prefs.target=X` + `perTarget[X]=P`
resolves the overseer model from P (`source "routing"`) and `chat_fallbacks(target=X)` walks P's
chain; without the target the active profile is unchanged. `ux_repl_onboarding` stays 26/26 (the
`_resolve_config` signature change is a defaulted trailing param).

## v5.3 (2026-07-10) — mid-session engine re-resolution + Playwright browser E2E

Two dogfeeding findings on v5.2. First, a live incident: the header chip read
`repo=printintel · perfil=personalizado`, but the overseer answered "fable 5" and
the engine chip agreed — the honest chip against a stale session. Second, the four
consecutive GUI correction rounds justified a real browser test layer. Backend
routes, token auth, the allowlist, and `run_action`'s HITL refusal are unchanged;
`chat_operator.run_chat`'s `/repo` handler and the onboarding `obStart` handler grow,
and an optional Playwright test layer is added outside the runtime. Numbered
requirements continue the list.

37. **Mid-session engine re-resolution on target switch.** `run_chat` resolved the
    config and built the engine ONCE at boot. The onboarding apply sent `/repo <name>`
    (target switch + `_save_prefs` + a context note) and ran `routing profile use`
    (registry), but nothing re-resolved the config or rebuilt the engine mid-session —
    so the perTarget overseer binding (R36) only bound the NEXT session. The chip was
    honest; the session was stale. The `/repo` handler now, after the switch + save,
    re-runs `_resolve_config` with the new target hint; the pure `_reresolve_needed(cfg,
    new_cfg)` gate rebuilds via `build_engine(…, target=target_name)` **only** when the
    effective engine/model/effort changed AND the current model/effort were not
    explicitly pinned (`flag`/`session` sources are deliberate pins — CLI `--model`,
    `/config`, `/engine` — and a routing rebinding must never silently override them).
    On rebuild it swaps `agent`, rewires `agent.chat_mode`/`say`/`pause_cm`, updates
    `cfg` + the HUD `engine_label`, appends a context note (a rebuild is a FRESH vendor
    session with no memory of the conversation — same mechanism as the target-switch
    note), and says one line `engine agora: <engine> · <model> · <effort> (<source>)`.
    No change → silent (the session is not disrupted). `/config` already rebuilt with
    the target (its wizard picks explicitly), so it needed no change. *Root cause of the
    printintel/fable incident (2026-07-10):* resolution was boot-only; state changed
    mid-flight (the `/repo` switch), and the engine kept its boot model until the next
    session.

38. **Profile-only apply restarts the bridge.** When `começar` changes the profile but
    NOT the repo, no `/repo` reaches the REPL, so R37 has no live signal to re-resolve
    on — the dialog now calls the existing `POST /api/chat/restart` (same engine) so the
    fresh session resolves the new profile's overseer. When `/repo` WAS sent, R37 covers
    it live and no restart fires. The onboarding hint text states that applying a
    profile-only change restarts the chat session.

39. **Playwright browser E2E layer (optional, self-skipping).** The four corrective GUI
    rounds justify a browser truth check for the flows that regressed. Playwright is an
    OPTIONAL dev dependency — the harness runtime stays stdlib-only; it lives only in the
    test layer (`testing/ui/test_panel_e2e.py`, real chromium headless). The scenario
    wrapper `testing/scenarios/ui_e2e.py` follows the scenario conventions but GREEN-SKIPS
    with a clear message when `import playwright` fails, chromium isn't installed, or
    `PLAYWRIGHT_SKIP=1` — the gates stay green on machines without it. The suite is
    deterministic (`--engine manual`, ephemeral port, token in the URL, NO LLM) and
    covers: onboarding auto-open on first visit + `pular` flag + reload-no-dialog; header
    chip reopen with name-only repo options and a path caption; a profile fork via the
    role-edit modal reflected in `/api/routing`; the R38 profile-only restart (asserts
    the `/api/chat/restart` request); the chat transcript round-trip + reload replay (R24);
    and the mode-badge refusal on a manual engine (proves the click wiring). Real routing/
    prefs state it touches on the repo root is snapshotted and restored; the chromium
    browser cache installs to the user profile, nothing lands in-repo.

| Decisão | Fontes |
|---|---|
| R37: `/repo` re-resolve o config e rebuild o engine no meio da sessão; pins flag/session nunca sobrescritos | Incidente 2026-07-10 (chip `printintel·personalizado`, overseer respondia "fable 5" — resolução era só no boot, estado mudou em voo); paridade com R36 (perTarget lido nas rotas vivas) |
| R38: troca só-de-perfil reinicia o bridge (mesmo engine) via `/api/chat/restart` | O REPL não recebe sinal sem `/repo`; a rota de restart já existia (reuso in-place do `ChatBridge`, o SSE sobrevive) |
| R39: camada E2E Playwright opcional, auto-skip; verdade de navegador para fluxos que regrediram 4 rodadas seguidas | Pedido do usuário 2026-07-10; [playwright.dev/python](https://playwright.dev/python/docs/intro); histórico de regressão do próprio painel (v2→v5.2) |

### v5.3 test strategy

`chat_operator.py`'s self-check asserts the `_reresolve_needed` pin matrix (unpinned
change → rebuild; `flag`/`session` pin → never; no change → silent). `testing/scenarios/
m5_ui_panel.py` (38 → 39) adds `engine:reresolve-on-target`: a tmp routing world with an
active overseer (sonnet) and a `perTarget` binding (opus) proves `_resolve_config(target=…)`
flips the model and `_reresolve_needed` rebuilds only when unpinned — the unit path, chosen
over a disproportionate full tmp-harness-root bridge round-trip. `testing/scenarios/ui_e2e.py`
is the new self-skipping Playwright scenario (6 checks when the browser is present, one green
`ui_e2e:skipped` otherwise). `mr` stays 18/18, `ux` 26/26. R38 is a front-end handler branch,
proven end-to-end by the E2E `e2e:profile-only-restart` (the `/api/chat/restart` request fires
on a profile-only apply). Playwright 1.61.0 + chromium-headless-shell 149.0.7827.55.

## v6 (2026-07-11) — worker drill-in: on-demand live output

The Agents column showed status cards only — no way to see *what* a worker is
doing (the documented v2 ceiling: "only harness workers appear; no intra-turn
streaming"). SPEC-118 lifts the runtime half (workers now write stdout/stderr
live to their run-logs; a read-only `workflow tail` exposes them); this amendment
adds the panel half — a click-opened drawer with human-initiated polling. No new
backend write path, no ambient streaming (M5.3 "panels categorize, never stream"
still governs the dashboard); the live output appears only in a drawer a human
deliberately opens. Numbered requirements continue the list.

40. **Drill-in by click.** Cards stay categorized on the dashboard; clicking a
    worker card opens a drawer with that worker's live output — streaming initiated
    by the human, scoped to the open drawer (the sanctioned reconciliation with
    M5.3, which restricts *ambient* defaults, not deliberate inspection).
41. **`/api/worker` validated.** Token-gated (the existing `_authed` precedes
    routing); `wf`/`worker` are validated against state (id regex + existence in
    `workflow.json`) BEFORE any path is built; malformed/unknown input → an `error`
    payload, never a 500 and never a read outside `.harness/workflows/active/<WF>/`.
42. **Poll only while open.** The 1.5s poll runs only while the drawer is open AND
    the tab is visible; closing the drawer stops the timer; a settled worker gets
    one final render, then polling stops.
43. **Progressive render.** A line that parses as claude `stream-json` becomes a
    structured activity line (`tool: Read <path>`, a text snippet, `result (…)`);
    everything else renders as escaped raw text; the renderer never throws.
44. **Post-mortem.** A finished worker still opens — with capped logs, the task
    record, and its events — without polling.
45. **Rows addressable.** Worker rows in `/api/state` carry the id of their
    `workflow`, so a card can address the drill-in.

```gherkin
Feature: Supervision panel — worker drill-in

  Scenario: [worker:drilldown-open] clicking a running agent card opens a live output drawer
    Given a worker is running and its card shows in the Agents column
    When the supervisor clicks the card
    Then a drawer opens with the worker's live output, task record, and events

  Scenario: [worker:drilldown-postmortem] a finished worker still opens with its capped logs
    Given a worker has already settled
    When the supervisor opens its drawer
    Then the capped logs and events are shown without any live polling

  Scenario: [worker:api-validated] malformed or unknown wf/worker ids are refused with an error payload
    Given a request to the worker endpoint with a traversal or unknown id
    When the panel handles it
    Then an error payload is returned instead of a 500 or a read outside the workflow
```

| Decisão | Fontes |
|---|---|
| Output ao vivo só num drill-in iniciado pelo humano; dashboard segue categorizado | Reconciliação sancionada com M5.3 "panels categorize, never stream" (`docs/IMPLEMENTATION_BACKLOG.md`); a regra restringe defaults ambientes, não inspeção deliberada |
| Redirect de log ao vivo + `workflow tail` como fonte de dados (não SSE) | SPEC-118 (`worker-live-tail.md`); polling 1.5s já existente (gated por visibilidade), sem canal novo |
| `/api/worker` valida id por regex + existência antes de montar path; degrada pra `error` | padrão do `/api/records` (degrade-to-`{"error":…}`); superfície read-only, zero mudança em `ACTIONS` |
| Render progressivo do `stream-json`, nunca lança | claude `-p --output-format stream-json` (docs.anthropic.com Claude Code SDK); teto do v2 (subagentes de vendor sem dados) fica aberto pra este upgrade opt-in |

### v6 test strategy

`testing/scenarios/worker_live_tail.py` (SPEC-118) is the runtime/CLI acceptance
net — a synthetic executor runs a `python -u` fixture child so the log-grows-live,
mid-run tail, follow, truncation, timeout, cancel, and read-only checks are
deterministic (no LLM). `testing/scenarios/m5_ui_panel.py` adds the panel half:
`worker:api-validated` (traversal / unknown WF / missing params → 200 + `error`;
no token → 403), `worker:drilldown-open` (`/api/worker` returns lines/task/worker
and `PAGE` carries `id="wkDlg"` + `openWorker`), `worker:drilldown-postmortem` (a
`succeeded` fixture worker still returns lines + events), and
`worker:rows-carry-workflow` (rule 45 — `/api/state` rows include `"workflow"`),
all against a throwaway `WF-UITEST-TAIL` fixture. The Playwright layer adds
`e2e:worker-drilldown` (click card → `#wkDlg` open → `#wkOut` shows a raw fixture
line and a structured `tool:` line → close) — an EXTRA browser truth check, not
Gherkin-bound because it green-skips without chromium (v5.3 R39 precedent).

## v7 (2026-07-11) — last-activity on agent cards

An agent card showed status + elapsed + tokens, but a `running` worker that had
gone quiet looked identical to one still emitting — the "travou?" case forced a
click into the drawer to tell. This amendment surfaces per-worker activity on the
card itself at no polling cost: the mtime of the worker's stdout run-log is a free
proxy for "when did this worker last produce output". No new poll, no new endpoint —
`read_workers` already runs each `/api/state` tick; it now carries one extra stat.
Numbered requirements continue the list.

46. **Last activity.** Each `/api/state` worker row carries `lastOutputAt` — the
    ISO-8601 mtime of its `run-logs/<workerId>.stdout.log`, or `null` when no log
    exists yet. The card renders a dim "output há Ns" line computed client-side from
    `lastOutputAt` vs now; a null value renders as `—`, never an error. The cost is
    one `stat` per worker per tick (try/except → `null`), no new polling.

```gherkin
Feature: Supervision panel — worker last-activity

  Scenario: [worker:last-activity] an agent card shows when the worker last produced output
    Given a worker with a stdout run-log on disk
    When the panel polls /api/state
    Then the worker row carries a lastOutputAt timestamp and the card shows a dim "output há Ns" line
```

| Decisão | Fontes |
|---|---|
| Indicador de atividade por instância no card (não só status/elapsed) | dashboards multi-agente OpenRig / claude-squad mostram atividade por instância; custo = 1 `stat`/worker/tick, sem novo poll |
| mtime do stdout run-log como proxy de "última saída"; ausência → `null` → `—` | SPEC-118 run-logs ao vivo (`worker-live-tail.md`); `read_workers` já roda por tick e degrada per-row (try/except) |

### v7 test strategy

`testing/scenarios/m5_ui_panel.py` adds `worker:last-activity`: against the
`WF-UITEST-TAIL` fixture (which writes run-logs on disk), `/api/state` worker rows
carry a truthy `lastOutputAt` and `/api/worker` still returns the worker. The null
path (no log) is the render default (`—`) and is exercised implicitly by every row
without a log — no card ever errors on a missing `lastOutputAt`.

## v8 (2026-07-12) — flight-strip attention bay + alarm rationalization

The right column stacked its supervision signals by SOURCE (Agents, then
Escalations), each internally ordered but with no cross-source sense of *what to
act on next* — a critical escalation, a red gate, and a worker that went quiet all
looked equally (un)urgent. This amendment adds an air-traffic-control "flight-strip
bay" at the top of the panel's supervision column: one list of strips ordered by
**attention required, not status or arrival**, and every strip NAMES the operator
action it demands (the "dark board" rule — a signal with no action is noise). It
generalizes the panel's existing criticality-sorted idiom (`_TIER_ORDER`, already
used to sort `_escalations`) across sources instead of inventing a parallel system.
No new backend write path, no new mutating action, no new endpoint, no new state
file — it is a pure read/presentation layer over data `state_snapshot` already
collects. Numbered requirements continue the list.

47. **Attention-ordered, derived per refresh, never cached.** `state_snapshot`
    gains an `attention` key: `ui_panel.attention_strips(escalations, workers,
    lastValidation, now)` — a pure function of the already-collected snapshot
    sources (no new reads). It returns strips sorted by attention tier (critical
    first), ties broken by recency, and is recomputed on **every** `/api/state`
    poll. A fully derived ordering cannot go stale, so **no ordering index/cache is
    stored anywhere** (the K4 binding condition). Each strip is `{source:
    "escalation"|"gate"|"worker", rank: int (the `_TIER_ORDER` attention tier),
    label, detail, nextAction}` (worker strips also carry `wf`/`worker` to address
    the drill-in; every strip carries `at` for the recency tiebreak). The collector
    degrades to `[]` on any error.

48. **Every strip names an operator action.** Ordering rule (derived every call,
    deterministic): escalations by `_TIER_ORDER` → `nextAction` "resolver escalation
    ou editar handoff"; a red/failed last gate → high rank → "re-rodar smoke / ver
    falhas"; a running worker gone quiet (its SPEC-118 v7 `lastOutputAt` older than
    `QUIET_SECONDS` = 90s vs now) → watch rank → "drill-in / workflow tail". A
    still-emitting worker (or one with no log yet) is **not** an alarm. *Ceiling:*
    protected-file drift is a declared strip source but not emitted — it is not in
    `state_snapshot`'s sources today and the K4 condition forbids spawning a new
    subprocess for it; add the drift strip only once a cheap drift signal already
    lands in the snapshot.

49. **Calm-board rendering, reuse over new surface.** The front-end renders the
    "Atenção" bay at the top of the right column, showing each strip's source +
    label + detail + a dim "→ &lt;nextAction&gt;", in the order the backend gave
    (the JS never sorts or caches beyond rendering the given order — the no-drift
    proof is that the order is a pull from `/api/state`). An empty bay renders
    "quadro calmo" — a calm board is the goal. A worker strip opens the existing
    drill-in drawer; an escalation strip scrolls to the Escalations card (reuse
    existing affordances, no new endpoint).

```gherkin
Feature: Supervision panel — flight-strip attention bay

  Scenario: [attention:ordered] signals are ordered by attention tier, not by source or arrival
    Given escalations, a failed gate, and a worker that went quiet
    When the panel derives the attention bay from the state snapshot
    Then a higher-tier source sorts above a lower-tier one (critical escalation, then failed gate, then quiet worker)

  Scenario: [attention:names-action] every surfaced strip names the operator's next action
    Given the attention bay has strips to show
    When the panel renders them
    Then each strip carries a concrete nextAction string, never just a status

  Scenario: [attention:no-cache] the ordering is a pure function of the snapshot with no stored index
    Given the same state snapshot
    When the attention bay is derived twice
    Then both derivations yield the identical order and an empty state yields an empty bay
```

### v8 test strategy

`ui_panel.py`'s `__main__` self-check asserts the ranking (attention-ordered,
critical leads, source order critical-esc → failed-gate → quiet-worker → info-esc),
that every strip names an action, and the no-cache property (same state → identical
order; empty state → empty bay; dropping the critical escalation re-derives without a
stale rank-0 lead). `testing/scenarios/m5_ui_panel.py` adds the three Gherkin-mapped
checks — `attention:ordered`, `attention:names-action`, `attention:no-cache` — by
calling `attention_strips` against a constructed state (the deterministic no-cache
proof) and asserting the `attention` key flows through `/api/state`. The Playwright
layer adds `e2e:attention-bay` (a running+quiet fixture worker surfaces a strip
naming "drill-in / workflow tail" in the `#atten` bay) — an EXTRA browser truth
check, not Gherkin-bound because it green-skips without chromium (v5.3 R39 precedent).
All deterministic, no LLM.

| Decisão | Fontes |
|---|---|
| Bay ordenado por atenção (não por status/chegada); ordem derivada a cada refresh, sem cache | Flight strips de ATC (tiras ordenadas por ação requerida, não por status) — CSCW '92 (transferência cross-domain da rodada de pesquisa, `docs/research/agent-gui-cli-features.md` Fase 4 K4); generaliza o idioma `_TIER_ORDER` já usado em `_escalations` |
| Todo sinal nomeia uma ação do operador (regra do "quadro escuro") | Estudo de dark-patterns em supervisão (K4): um alarme sem ação é ruído; ANSI/ISA-18.2 (racionalização de alarmes) — anexado como `[judgment]` honesto na rodada |

## v9 (2026-07-12) — recovery console + approval-as-record generalization

The panel could inspect a stalled/failed worker (v6 drill-in) and rank it in the
attention bay (v8), but the only way to *act* — retry a worker, mark it, recover a
crashed async supervisor, cancel a workflow — was to drop to the CLI. This amendment
surfaces the workflow recovery verbs as panel actions, EXPANDING `ui_panel.ACTIONS`
(the panel's single mutating write path) for the first time since the config surface —
so the trust-boundary discipline is the whole point (K5). It adds **no new endpoint**:
the recovery buttons reuse the existing `POST /api/action` allowlist + browser-confirm.
Numbered requirements continue the list.

50. **Recovery verbs allowlisted as argv tails.** `ui_panel.ACTIONS` gains exactly four
    recovery entries, each `{"mutating": True, "recovery": True, "build": lambda p: […]}`
    mapping to a REAL `harness.py workflow` subcommand: `workflow-retry` →
    `workflow retry <wfid> <workerId>`; `workflow-cancel` → `workflow cancel <wfid>`;
    `workflow-mark` → `workflow mark <wfid> <workerId> <status>`; `workflow-recover` →
    `workflow async-recover <wfid>`. (The PLAN's `recover` verb maps to the real
    `async-recover`; `mark` exists as a real subcommand and is included with its `status`
    constrained per R52.) No other recovery/lifecycle verb (`unlock`, `resume`,
    `finalize`, `promote`, `rollback`) is exposed — only these four.

51. **`scrub` and every `--force` variant stay CLI-only.** `scrub` — the sole irreversible
    verb in the workflow set — is absent from `ACTIONS` entirely, and no recovery build
    can emit a `--force` / `--force-round` / `--force-lock` / `--clear-result` token: the
    build lambdas never append one, and the R52 gate forecloses smuggling one through a
    `workerId`/`status` param (a `--force`-shaped value is refused before it can reach argv).
    `unlock --stale-only` was considered as the fourth verb and dropped once `mark` was
    confirmed real; `unlock --force` is never reachable. This is the K5 non-negotiable.

52. **Approval-as-record: recovery ids are validated against state.** Every recovery action
    is `recovery: True`; `run_action` calls `_recovery_reason(root, params)` BEFORE the
    build lambda. The browser-supplied `wfid` must match the `WF-` id shape AND name a live
    directory under `.harness/workflows/active/` (`_active_wfid`) — an unknown/foreign id is
    refused with no subcommand run (generalizing the `resolve-escalation` approval-as-record
    shape: a recovery references an id that exists in state, never an arbitrary browser
    string); a present `workerId` must match the worker-id regex; a present `status` must be
    in the closed worker-status set. The id regex also forecloses path traversal and argv
    flag-injection. Because each action is `mutating`, it also inherits the existing
    `params.confirm == true` requirement AND the `classify_command` human-only backstop
    (`--approval-token`/`--send` refused) — the recovery verbs add no exception to either.

```gherkin
Feature: Supervision panel — recovery console

  Scenario: [recovery:verbs-allowlisted] the workflow recovery verbs are mutating panel actions with real argv tails
    Given the recovery console
    When the panel builds a recovery action
    Then retry, cancel, mark, and recover map to their real workflow subcommand argv tails as mutating actions

  Scenario: [recovery:scrub-excluded] scrub and every force variant stay CLI-only
    Given the recovery action set
    When the allowlist is inspected
    Then scrub is absent and no recovery action can build a --force variant

  Scenario: [recovery:id-validated] a foreign or unknown workflow id is refused before any subcommand runs
    Given a recovery request naming a workflow id not present under active/
    When the panel handles it
    Then the action is refused and no subcommand is executed

  Scenario: [recovery:needs-confirm] a recovery action without a confirm is refused
    Given a recovery request for a valid workflow but without the browser confirm
    When the panel handles it
    Then the action is refused for missing confirmation and nothing runs
```

| Decisão | Fontes |
|---|---|
| Verbos de recuperação como ações do painel (mesmo write-path + confirm), sem endpoint novo | K5 (`docs/research/agent-gui-cli-features.md` Fase 4/5): approval-as-record é o padrão `ACTIONS` já entregue, generalizado; paridade OpenClaw Control UI (exec approvals) sob a invariante nº1/nº6 (nada painel-only; o CLI já tem `workflow retry\|cancel\|mark\|async-recover`) |
| `scrub` + toda variante `--force` ficam CLI-only | K5 não-negociável: scrub é a única ação irreversível do conjunto; `workflow --help` desta máquina lista `scrub`/`retry --force-round`/`unlock --force`/`resume --force-lock` — nenhum é exposto; o gate `_recovery_reason` impede injeção via `status`/`workerId` |
| wfid validado contra `.harness/workflows/active/` antes de virar argv (approval-as-record) | Regra "o compilador é a fronteira de confiança" (K1/K5); reuso do id-gate do `worker_detail` (regex + existência) + o conjunto fechado de status de `workflow_mark` |

### v9 test strategy

`ui_panel.py`'s `__main__` self-check asserts the four verbs are mutating+recovery
ACTIONS with the exact argv tails, that `scrub` is absent and no build emits a
`--force*` token, and — against a tmp `active/WF-OK-1` fixture with `subprocess.run`
monkeypatched to a call-counter — that a foreign wfid, a `--force`-shaped `workerId`,
and a `--force` `status` are each refused with **zero** subprocess calls, and that a
valid-wfid-without-confirm is refused at the confirm gate (still zero). `testing/
scenarios/m5_ui_panel.py` adds the four Gherkin-mapped checks — `recovery:verbs-allowlisted`,
`recovery:scrub-excluded`, `recovery:id-validated`, `recovery:needs-confirm` — exercising
`run_action` in-process against the real `WF-UITEST-TAIL` fixture (the one valid wfid) and
the build lambdas for argv shape; it also extends the `composer:no-write-path` HEAD action
set with the four verbs. NOTHING destructive is executed — every assertion is on a refusal
path or an argv shape, never a live recovery. The Playwright layer adds
`e2e:recovery-confirm` (a recovery button in the drawer opens a confirm dialog naming the
verb and, when dismissed, POSTs no `/api/action`) — an EXTRA browser truth check, not
Gherkin-bound (green-skips without chromium, v5.3 R39 precedent). All deterministic, no LLM.

## v10 (2026-07-12) — discard a stopped workflow (closing the create→discard gap)

The N2b composer gained **Criar** (SPEC-120 v2): it materializes a `planned`
workflow — worker cards on the dashboard — but never starts it. The panel had no
way to *remove* one. `workflow cancel` only signals a RUNNING workflow's async
task PIDs, so a never-started/`planned` WF (no live process) makes cancel a no-op
and its cards stay stuck; `scrub` (the only verb that deletes the `active/WF-*`
dir) was CLI-only by N4 decision. So a created-but-unwanted workflow was stranded
on the board — the panel got CREATE without DISCARD. This amendment adds the
missing DISCARD, scoped exactly like the v9 recovery verbs (same `POST /api/action`
allowlist + browser-confirm, **no new endpoint**). Numbered requirements continue.

53. **Discard = `scrub` restricted to not-running workflows.** `ui_panel.ACTIONS`
    gains one entry `workflow-discard` `{"mutating": True, "discard": True,
    "build": lambda p: ["workflow", "scrub", <wfid>]}` — `workflow scrub <wfid>`
    with **no `--force`**. Discard is scrub, restricted to a *stopped* workflow;
    it is the only removal affordance in the panel and the single closing verb for
    the composer's create→discard lifecycle.

54. **The not-running gate (approval-as-record).** `discard: True` routes the
    action through `_discard_reason(root, params)` in `run_action` BEFORE the build
    lambda (mirrors `_recovery_reason`): (1) the `wfid` must pass `_active_wfid` —
    the `WF-` id shape AND a live directory under `.harness/workflows/active/` — so
    a foreign/unknown id is refused with no subprocess (the id regex also forecloses
    path traversal and argv flag-injection); (2) the workflow must NOT be running —
    a live supervising process (`async/supervisor.pid` alive, or a `.run.lock` /
    `workflow.lock` whose recorded PID is alive via the cross-platform, zombie-safe
    `workflow_process_alive`, NOT `os.kill`) → refused with *"workflow em execução —
    cancele antes de descartar"*. Only a STOPPED WF (planned / settled / failed /
    cancelled, no live PID) may be discarded from the browser. `scrub --force`
    (which would bypass the CLI's own run-lock and scrub-safe-phase guards) is never
    built — it stays CLI-only; bare `scrub` itself also refuses a locked/running WF
    or a non-scrub-safe phase at the CLI (belt-and-suspenders). Being `mutating`, it
    inherits the `params.confirm == true` requirement AND the `classify_command`
    human-only backstop — discard adds no exception to either.

```gherkin
Feature: Supervision panel — discard a stopped workflow

  Scenario: [discard:stopped-allowed] a stopped workflow can be discarded from the panel
    Given a materialized workflow that is not running
    When the operator confirms Descartar
    Then the panel runs `workflow scrub <id>` without --force and the workflow directory is removed

  Scenario: [discard:running-refused] a running workflow cannot be discarded from the panel
    Given a workflow with a live supervising process
    When a discard is requested
    Then the action is refused and no scrub subcommand is executed

  Scenario: [discard:needs-confirm] a discard without the browser confirm is refused
    Given a discard request for a stopped workflow but without the confirm
    When the panel handles it
    Then the action is refused for missing confirmation and nothing runs
```

| Decisão | Fontes |
|---|---|
| Descartar = `scrub` restrito a workflows não-em-execução (mesmo write-path + confirm), sem endpoint novo | Fecha o gap CREATE→DISCARD que o dono encontrou: N2b (SPEC-120 v2) cria `planned`; `workflow cancel` só sinaliza PIDs de task async EM EXECUÇÃO, então um WF que nunca iniciou fica com os cards presos; K5 approval-as-record generalizado do v9 |
| WF em execução → recusado ANTES de qualquer scrub; `--force` nunca construído | Preserva a intenção do N4 (scrub de trabalho vivo + `--force` ficam CLI-only); liveness via `workflow_process_alive` (OpenProcess/GetExitCodeProcess no Windows, à prova de zumbi) em vez de `os.kill`; belt-and-suspenders com o próprio `scrub` (recusa lock ativo + fase não-scrub-safe no CLI) |
| wfid validado contra `.harness/workflows/active/` antes de virar argv | Regra "o compilador é a fronteira de confiança" (K1/K5); reuso de `_active_wfid` (regex + existência), id da state e nunca string arbitrária do browser |

### v10 test strategy

`ui_panel.py`'s `__main__` self-check asserts `workflow-discard` is
mutating+discard, its build argv is exactly `["workflow", "scrub", <wfid>]` with no
`--force`, a stopped `WF-OK-1` fixture passes `_discard_reason` (None), and — with
`subprocess.run` monkeypatched to a call-counter — a RUNNING WF (a `workflow.lock`
naming `os.getpid()`), a foreign id, and a valid-id-without-confirm are each refused
with **zero** subprocess calls. `testing/scenarios/m5_ui_panel.py` adds the three
Gherkin-mapped checks: `discard:running-refused` (a live-pid `workflow.lock` fixture
plus a foreign id, the counter proving no scrub ran), `discard:needs-confirm` (an
unconfirmed discard of a real composer-created `planned` WF → refused, dir intact,
no subprocess), and `discard:stopped-allowed` (the same WF, confirmed → the plain
`workflow scrub <id>` argv AND the directory actually removed; scrub-safe cleanup in
the finally). It also extends the `composer:no-write-path` HEAD action set with
`workflow-discard`. The Playwright layer adds `e2e:discard-confirm` (the Descartar
button opens a confirm naming `workflow scrub <wf>` and, when dismissed, POSTs no
`/api/action`) — an EXTRA browser truth check, not Gherkin-bound (green-skips without
chromium, v5.3 R39 precedent). NOTHING nukes live work — every discard assertion is a
refusal path, an argv shape, or a throwaway WF the test itself created. Deterministic, no LLM.

## v11 (2026-07-12) — chat redesign: no engine picker, surfaced `!` bypass, multi-session

The chat tab carried an engine `<select>` + a "Restart bridge" button that were
confusing and under-powered (they couldn't even pick `openai`), while the REPL's
existing local-command bypass was invisible and there was only ever one session.
This amendment removes the picker, surfaces the bypass, and adds multi-session —
all on the **same** SSE + `POST /api/action`/`chat/*` surface, no new write path.
The owner's decision: **every session uses the overseer default engine** (engine
is chosen only through `/config`/chat-prefs; there is no per-session engine picker
anywhere). Numbered requirements continue the list.

55. **Engine selection lives only in `/config`/prefs.** The chat header's engine
    `<select id="engine">` and the `<button id="restart">` ("Restart bridge") are
    deleted from `PAGE`. `POST /api/chat/restart {session}` restarts a session **in
    place** reusing that session's stored engine (the server default) — it no longer
    carries or swaps an engine, and no longer mutates `server.engine`. The dead-bridge
    "bridge encerrado — Restart" affordance and the onboarding profile-only restart both
    POST restart with no engine. `updateEngineDefaultOption` and its calls are removed.
    The overseer engine is resolved from routing/prefs (the `/config` wizard, chat-prefs,
    the Config tab) — the one path that already supports `openai` — so setting the overseer
    to `openai` there applies to **all** panel sessions.

56. **The `!` local-command bypass is surfaced (front-end only).** `!records search X`
    (and every `/`-command) already runs locally through the REPL without an LLM turn
    (`chat_operator.py:551`, the `line.startswith("!")` branch) — no REPL/route change.
    The panel adds: (a) an input hint (`#inputHint` + the placeholder) — *"`!comando`
    roda um comando do harness local (não vai pra LLM) · `/help` lista comandos"*; (b) in
    `sendLine`, a line starting with `!` or `/` does **not** call `busyOn()` — a local
    command emits no `turn-start`/`turn-end`, so the spinner would otherwise hang forever.

57. **Multi-session.** A new `ui_panel.ChatSessions` registry (a lock + a `dict[str,
    ChatBridge]`; `ChatBridge` itself is UNCHANGED — already per-instance clean) holds the
    sessions: `new(root, engine) → id` (creates+starts a `ChatBridge`, short id + label +
    `createdAt`), `ensure(id, root, engine)` (the lazy `main` back-compat path), `get(id)`,
    `list()`, `restart(id, root)`, `close(id)` (stop+remove), `stop_all()`; every session
    starts with the passed engine (the server default). `PanelServer` replaces the single
    `bridge`/`bridge_lock`/`sse_gen`/single-engine fields with `self.sessions`, a
    **per-session** `sse_gen` dict, and a lock; `self.engine` remains the DEFAULT engine
    every new session starts with. Routes carry a `session` id defaulting to `"main"` (lazily
    created on first use — a session-less request still works): `GET /api/chat/stream?session=…`
    (per-session SSE — bumping session B's generation must NOT stop session A's stream; the
    cursor-based lossless delivery of R24 v2 is preserved per session), `POST /api/chat/send
    {session,line}`, `POST /api/chat/restart {session}`, `POST /api/chat/new` → `{id,label}`,
    `GET /api/chat/sessions`, `POST /api/chat/close {session}`. `atexit` + `serve()`'s finally
    call `stop_all()`. The front-end adds a session bar (tabs + "Nova sessão" + a ✕ per
    session); selecting a session re-points the `EventSource` (close + reopen with `?session=id`)
    and the send/restart target, clearing + replaying the transcript on switch (the existing
    clear-on-SSE-open); on first load it attaches/creates `"main"`. **openai telemetry honesty
    (already R24):** an `openai` overseer emits the same `ready`/`turn-*` events (they come from
    `run_chat`, not the engine), so it renders like claude EXCEPT cost `$n/a` (openai reports no
    cost) and `ctx n/a` (no openai model-card context window) — `renderTelemetry` already treats
    both as first-class dimmed chips, so no chip change is needed.

```gherkin
Feature: Supervision panel — chat redesign (no engine picker, ! bypass, multi-session)

  Scenario: [chat:no-engine-selector] the chat engine picker and Restart button are gone
    Given the supervision panel page
    When it is rendered
    Then it carries no engine <select> and no Restart-bridge button (engine is chosen via /config)

  Scenario: [chat:sessions-new-and-list] a new session can be created and appears in the list
    Given the chat tab
    When the supervisor creates a new session
    Then the new session id is returned and the active-session list includes it

  Scenario: [chat:sessions-independent] two sessions are independent bridges
    Given two chat sessions
    When a line is sent to each
    Then each session's transcript carries only its own line

  Scenario: [chat:bypass-local] a ! line runs a local command with no LLM turn
    Given the chat tab
    When the supervisor sends a line starting with !
    Then the harness command output appears with no turn-start/turn-end event and the input hint surfaces the bypass
```

| Decisão | Fontes |
|---|---|
| Tirar o seletor de engine + "Restart bridge"; engine só via `/config`/prefs | Feedback do dono (2026-07-12): o seletor confundia e nem alcançava `openai`; o caminho canônico (wizard `/config`, chat-prefs, aba Config) já resolve overseer incluindo openai (SPEC-115) — invariante nº1/nº6 (nada painel-only) |
| Surfacar o bypass `!`/`/` (só front-end; REPL/rota inalterados) | O bypass já existe (`chat_operator.py:551`, prefixo `!`); um comando local não emite `turn-start`/`turn-end`, então o spinner prenderia — não chamar `busyOn()` para `!`/`/` |
| Multi-sessão via `ChatSessions` (registry sobre `ChatBridge` inalterado); `sse_gen` por-sessão | `ChatBridge` já é limpo por-instância (proc/queue/history/cursor próprios); `sse_gen` global mataria o stream de A ao abrir B — por-sessão preserva o fix lossless R24 v2 (cursor-based) por sessão; `main` lazy = back-compat de request sem `session` |
| Toda sessão no engine overseer padrão (sem picker por-sessão) | Decisão do dono (2026-07-12): troca de engine só via `/config`; um overseer openai lá aplica a TODAS as sessões do painel |

### v11 test strategy

`ui_panel.py`'s `__main__` self-check adds a `ChatSessions` block (manual engine, no
LLM): `new()` creates a live session, `list()` shows it, two sessions are independent
bridges (a send to each lands in that bridge's `history` only), `close()` stops+removes,
`stop_all()` clears the registry — with `stop_all()` in a finally so no `harness.py chat`
subprocess leaks. `testing/scenarios/m5_ui_panel.py` adds the four Gherkin-mapped checks —
`chat:no-engine-selector` (PAGE carries no `id="engine"`/`id="restart"`), `chat:sessions-new-and-list`
(`POST /api/chat/new` returns an id that `GET /api/chat/sessions` lists), `chat:sessions-independent`
(two HTTP-created sessions, a line to each, independent `history` via the registry), and
`chat:bypass-local` (a `!status` line through a manual bridge produces command output with no
`turn-start`/`turn-end` evt, and the `!comando` hint is in PAGE) — and swaps the removed
`page:codex-option` for `chat:no-engine-selector`; the finally uses `server.sessions.stop_all()`.
`testing/scenarios/ui_e2e.py` adds `e2e:chat-sessions` (the "Nova sessão" button creates a
session, the bar shows 2 tabs, switching re-points the stream, and a `!` line shows local
output) and drops the `#engine` `select_option` from `e2e:profile-only-restart` (the restart
reuses the overseer default). All deterministic (`--engine manual`, no LLM); prior checks stay
green (64/64 in-process; 16/16 Playwright when chromium is present).

## v12 (2026-07-12) — header/gates/branch, overflow, confirm modal, layout, diff colorizer

A batch of seven panel UI/UX corrections, almost all in the inline `PAGE` string
plus one small `state_snapshot` addition. No new backend write path, no new mutating
action, no new endpoint — `state_snapshot` gains two read-only keys (`branch`,
`gates`) and the front-end grows the presentation. Numbered requirements continue.

58. **Header cost chip removed.** The `<span id="costChip">` and the two writer lines
    in `renderHeader` are deleted — the session cost already lives in the Metrics panel
    and the telemetry `sessão $` chip, so the header chip was redundant. The `.chip.cost`
    CSS class stays (telemetry/metrics still use it). The now-dead `liveSessionCost`
    variable (its only reader was the cost chip) is removed with it.
59. **Gates section (flow order) replaces the single header gate badge.** The header
    `#gateBadge` (last gate only) is replaced by a compact `.sec.gates` section in the
    right column. `state_snapshot` gains a `gates` key `{order: <the canonical
    spec_test_gate.GATES ladder>, last: <the existing lastValidation>, target: {name,
    last}|null}`. `order` is hardcoded (the 11 tiers, with a comment pointing at
    `spec_test_gate.GATES`) to avoid importing the heavy CLI module from `harness_lib`;
    `last` reuses the already-collected `lastValidation` (no new read); `target.last`
    reads the active target's `quality-state.json` via `targets_lib.state_dir(name)` when
    `prefs.target` is set, degrading to `None` (never-crash, like every collector).
    `renderGates` lists the tiers in order, highlights the last-run tier + its status/
    counts (`.badge2 .ok/.bad`), and adds a "target `<name>`: `<gate> <status>`" line
    when a target gate exists. The right column's max-heights are re-budgeted so
    atten/agents/gates/escs all fit.
60. **Current git branch in the header.** `state_snapshot` adds `("branch",
    chat_hud._git_branch, "")` to its never-crash collector loop (the helper already
    existed; `ui_panel` already imports `chat_hud`); it returns the `git rev-parse
    --abbrev-ref HEAD` value, `""` off a non-git root. The header renders a `#branchChip`
    (`⎇ <branch>`) updated on the 3s poll, so it reflects commits/branch switches.
61. **Card overflow guarded.** A long escalation id / `suggestedProfile` (or worker id/
    meta) no longer overflows its card: a shared rule adds `min-width:0`+`overflow:hidden`
    to the `.ecard`/`.wcard` wrappers and `.etop`/`.wtop` rows (so the flex rows can
    shrink) and `overflow-wrap:anywhere` to `.eid`/`.eprof`/`.wid`/`.wmeta`/`.ereason`.
62. **Native `alert`/`confirm`/`prompt` → in-page modal.** A new `<dialog id="confirmDlg">`
    backs three awaitable helpers — `confirmModal(text)→Promise<bool>`,
    `alertModal(text)→Promise<void>`, `promptModal(text,{options?|value?})→Promise<string|
    null>` — sharing one dialog (Cancel/Esc/✕/backdrop resolve negatively via the `close`
    event). All 14 native call sites migrate: the 8 `confirm()`, the 4 `alert()` result
    toasts, and the 3 `prompt()` (the worker-`mark` prompt becomes a `<select>` of the 9
    valid worker statuses instead of free text). Each migrated call site's handler is
    `async` and `await`s the helper; the confirm-gated action flow is unchanged (the
    server still requires `confirm:true` — the modal only replaces the native dialog
    before the `jpost`). This also makes the confirm flow Playwright-assertable (a native
    `confirm()` is not a DOM element).
63. **Layout: metrics above the ledger, ledger fixed-height.** The left column swaps the
    order so Metrics sits on top at natural height (`flex:0 0 auto`) and the Records
    ledger sits below at a fixed `max-height` (~2.5 `.lcard`) with `overflow-y:auto`, so
    the metrics get top billing and the ledger scrolls the rest.
64. **Conservative git-diff colorizer (diff-only).** `colorizeDiff(text)→html` colorizes
    a block ONLY when it looks like a real unified diff (a `diff --git` line, an `@@ … @@`
    hunk header, or paired `---`/`+++` file headers); then per line `+add` green, `-del`
    red, `@@` hunk cyan, `diff --git`/`index`/`+++`/`---` bold-dim, everything else plain.
    `esc()` runs on every line BEFORE wrapping, so browser input can never inject HTML.
    Non-diff output stays clean monospace (no language tokenizer — a deliberate scope
    limit). Applied to the mono blocks that can hold a diff: the worker drawer `#wkOut`
    (a raw stdout tail, colorized whole when it looks like a diff, else the existing
    per-line `fmtStreamLine` render), the composer `<pre class="cmout">` result blocks,
    and the action-output that (after R62) lands in `alertModal`.

*Deferred (owner decision, focused next delivery):* chat-verbose with per-message
tool-calls/shell output + per-message agent attribution (the original items 1+8) — they
require rewriting `ClaudeEngine`'s chat path to `stream-json`, risky and hard to test
deterministically; tracked as a follow-up. **Delivered in v13 below.** The diff colorizer
is intentionally diff-only (no language tokenizer) for the same test-surface reason.

```gherkin
Feature: Supervision panel — header, gates, branch, overflow, confirm modal

  Scenario: [panel:no-costchip] the redundant header cost chip is removed
    Given the supervision panel page
    When it is rendered
    Then it carries no cost chip in the header (cost stays in the metrics panel)

  Scenario: [panel:branch-shown] the header shows the current git branch
    Given the panel polls its state snapshot on a git repository
    When the snapshot is rendered
    Then the snapshot carries the current branch and the header renders a branch chip

  Scenario: [panel:gates-section] the gate ladder renders in flow order with the last run highlighted
    Given the panel polls its state snapshot
    When the gates section is rendered
    Then the canonical gate ladder is listed in order with the last-run tier and its status

  Scenario: [panel:confirm-modal] a mutating action confirms through an in-page modal, not a native dialog
    Given a mutating panel action
    When the operator triggers it
    Then an in-page confirm modal opens (no native dialog) and cancelling runs nothing

  Scenario: [panel:card-overflow-guarded] a long id cannot overflow an escalation or worker card
    Given an escalation card with a long id or suggested profile
    When the card is rendered
    Then the overflow guard keeps the text inside the card
```

### v12 test strategy

`ui_panel.py`'s `__main__` self-check asserts `state_snapshot` now carries `branch` (a
string, `""` off a non-git tmp root) and `gates` (the canonical 11-tier `order` with
`smoke` first, the collected `last`, `target` `None` without a `prefs.target`).
`testing/scenarios/m5_ui_panel.py` adds the five Gherkin-mapped checks —
`panel:no-costchip` (no `id="costChip"` in `PAGE`), `panel:branch-shown` (`/api/state`
carries a truthy `branch` + `PAGE` has `#branchChip`), `panel:gates-section` (`/api/state`
`gates.order` is the 11-tier ladder + `PAGE` has `renderGates`/`.sec.gates`),
`panel:confirm-modal` (`PAGE` has `#confirmDlg`+`confirmModal`/`alertModal`/`promptModal`+
`colorizeDiff` and ZERO native `confirm(`/`alert(`/`prompt(` calls survive), and
`panel:card-overflow-guarded` (the shared overflow-guard CSS rule is present). The
Playwright layer swaps the native-dialog-based `e2e:recovery-confirm` for the modal-based
`e2e:confirm-modal` (a recovery button opens `#confirmDlg` — asserted as a DOM element,
with the native-dialog handler proven to never fire — and Cancel POSTs no `/api/action`),
keeps `e2e:discard-confirm` (now modal-based), and adds `e2e:gates-and-branch` (the gate
ladder renders ≥11 tier chips and the branch chip shows `⎇ <branch>`); the profile-fork and
composer-create flows gain a `#confirmOk` click for the migrated confirm. All deterministic
(`--engine manual`, no LLM); prior checks stay green (69/69 in-process; 17/17 Playwright
when chromium is present).

| Decisão | Fontes |
|---|---|
| Remover o cost chip do header (custo já no painel de métricas + chip de sessão) | Redundância visível no header; `.chip.cost` mantida para telemetria/métricas |
| Seção de gates em ordem de fluxo substitui o badge único | Ladder canônico `spec_test_gate.GATES` (hardcoded p/ evitar import do módulo CLI pesado em `harness_lib`); target gate via `targets_lib.state_dir` (mesma fonte que `self_review`/`gate_generic`), degrada a None |
| Branch git no header via `chat_hud._git_branch` já existente | `git rev-parse --abbrev-ref HEAD` (o helper já existia; `ui_panel` já importa `chat_hud`); reflete commits/trocas no poll de 3s |
| Modal em vez de `alert`/`confirm`/`prompt` nativos | Consistência estética + os confirms viram testáveis por Playwright (um `confirm()` nativo não é elemento DOM); `<dialog>`/`showModal` nativo (MDN) — mesmo padrão dos dialogs existentes |
| Colorizer de diff conservador (só-diff, sem tokenizer) | Escopo deliberado: só colore blocos com marcadores de diff reais (`diff --git`/`@@`/`---`+`+++`); `esc()` antes de colorir (CSP self-contained, zero libs); não-diff fica monospace limpo |
| Deferido: chat verboso com tool-calls + atribuição por agente | Exige reescrever o `ClaudeEngine` de chat para `stream-json` — arriscado e difícil de testar de forma determinística; follow-up |

## v13 (2026-07-12) — verbose chat: live tool calls + light model attribution

Delivers the v12-deferred items 1+8. The chat `ClaudeEngine` streamed a single
buffered `-p --output-format json` blob, so intermediate `tool_use`/shell calls were
discarded and the transcript showed only the final answer. v13 switches it to the
**same** stream-json adapter the worker path already uses (`executors.json`), streams
per-tool activity through the existing pipe-event protocol, and renders it in the panel
with the renderer the worker drawer already has. Backend routes, token auth, the
allowlist, and `run_action`'s HITL refusal are unchanged; `ClaudeEngine._argv`/`send`,
a pure parser in `stream_json.py`, the `run_chat` emit injection, and the `PAGE`
`handleEvt`/CSS grow. Numbered requirements continue the list.

65. **ClaudeEngine chat streams stream-json.** `ClaudeEngine._argv` swaps
    `--output-format json` → `stream-json` and adds `--verbose` (claude requires it with
    `-p stream-json`); `send` replaces the buffered `subprocess.run` + `json.loads` with a
    streaming `Popen` whose stdout is parsed line-by-line. Everything else is preserved:
    session resume (`--resume <session_id>`), the per-turn `--permission-mode` (R19),
    allowed/disallowed tools, message-via-stdin, and telemetry — the terminal `result`
    event is fed to the EXISTING `_telemetry`, so cost/ctx-window/in-out tokens are intact.
    stderr is drained on a daemon thread (a chatty child can't deadlock the stdout read)
    and a watchdog `threading.Timer` enforces `TURN_TIMEOUT` (parity with the prior
    `subprocess.run(timeout=…)` — direct-child kill).
66. **Pure, importable parser.** `stream_json.parse_chat_stream(lines, on_tool)` is
    stdlib-only and testable without a live LLM: it fires `on_tool({name,arg})` per
    `tool_use` block IN ORDER (primary arg by the `file_path/path/command/pattern/url`
    precedence shared with the drawer's `fmtStreamLine` via `stream_json.tool_descriptor`),
    accumulates assistant text, and returns `{text, session_id, result}` (`result` = the
    raw terminal event for `_telemetry`). Tolerant: blank/torn/garbage lines are skipped;
    finalText prefers the result event's `result`, else the concatenated assistant text.
    The worker `stream_json.parse` is byte-unchanged.
67. **`tool` pipe-event + panel render + light attribution.** When `HARNESS_CHAT_EVENTS=1`,
    `run_chat` injects `agent.on_activity = on_tool`; ClaudeEngine calls it per `tool_use`,
    emitting a compact `{"event":"tool","name","arg"}` MID-turn (getattr-guarded → the
    injection is inert for codex/openai/manual, which never read `on_activity`). The
    panel's `handleEvt` renders it as a distinct `.ln.tool` transcript line
    (`🔧 <name> <arg>`) prefixed with a dim `.tmodel` tag = the overseer model from
    `readyInfo` (item 8, kept light — the chat is a SINGLE overseer; per-worker attribution
    stays in the drawer). It does NOT toggle the busy spinner — the turn stays busy until
    `turn-end`/`ready`.

```gherkin
Feature: Supervision panel — verbose chat (live tool calls + model attribution)

  Scenario: [chat:tool-events-parsed] the chat stream parser surfaces tool calls and the final answer
    Given a canned claude stream-json transcript with tool_use blocks and a result event
    When the pure parser consumes it with a tool callback
    Then the tool descriptors fire in order and the final text, session id, and usage are extracted

  Scenario: [chat:tool-render] the panel renders a tool event as a live activity line
    Given the chat emits a tool event mid-turn
    When the panel handles it
    Then a distinct tool line is appended with the overseer model, without stopping the busy spinner
```

| Decisão | Fontes |
|---|---|
| ClaudeEngine de chat migra para `stream-json` + `--verbose` (o mesmo adapter de worker) | `.harness/routing/executors.json` (worker já usa `-p --output-format stream-json --verbose`, SPEC-118 v3); `claude --help` nesta máquina lista ambos; teto documentado no v2/v12 ("upgrade path é parsear stream-json dentro do ClaudeEngine") |
| Parser puro `parse_chat_stream` testável com transcript enlatado (sem LLM vivo) | paridade com `stream_json.parse` (worker) + `fmtStreamLine` (drawer); NDJSON linha-a-linha (docs.anthropic.com Claude Code SDK); descritor de tool compartilhado (`tool_descriptor`) |
| Evento `tool` por pipe + linha `.ln.tool`; atribuição leve pelo `readyInfo.model` | protocolo de eventos por pipe já existente (v2 R7, sentinela `\x1e`); item 8 mantido leve — chat é um único overseer, sem atribuição por-worker (essa vive no drawer v6) |

*Ceiling.* Only ClaudeEngine streams; codex/openai already surface their own tool text
via `say` and stay as-is; manual has no engine. Verbose tool lines reach the panel via the
`\x1e` pipe events (`HARNESS_CHAT_EVENTS=1`); a terminal-HUD tool render is a documented
follow-up. The live claude round-trip (real tool lines streaming into the panel) is the
owner's one-time manual verification — it burns a real turn, so it is NOT a gate check.

### v13 test strategy

`stream_json.py`'s `__main__` self-check drives `parse_chat_stream` (tool order, final
text, session id, blank/torn-line tolerance, no-result fallback) — the pure logic's
runnable proof. `testing/scenarios/m5_ui_panel.py` adds three deterministic checks (no
LLM): `chat:argv-stream-json` (`ClaudeEngine._argv` carries `--output-format stream-json`
+ `--verbose`), `chat:tool-events-parsed` (a canned stream-json transcript → ordered
`Read`/`Bash` descriptors + final text + session id, with `_telemetry` recovering
cost `$0.02`/4 out-tokens — telemetry preserved), and `chat:tool-render` (`PAGE` carries
the `handleEvt` `tool` branch + the `.ln.tool` CSS + the `.tmodel` attribution span). The
Gherkin ids map to the last two. `worker_live_tail.py`/`wf_failover.py` remain the
worker-path regression net (unchanged: `stream_json.parse` and the worker spawn are
byte-identical). Prior checks stay green.

### v14 — Alerts modal + Metrics-button removal (2026-07-15)

Owner's visual pass round 2: the right column carried three low-frequency
supervision signals (risk summary, Attention bay, Escalations) that only matter
when something is wrong, and a header `Metrics` button that duplicated the
left-aside metrics panel. Both are consolidated. Numbered requirements continue.

68. **One Alerts modal for risk summary + attention + escalations.** The three
    right-column sections (`.sec risksum`, `.sec atten`, `.sec escs`) move into a
    single native `<dialog id="alertsDlg">` opened by a new header button
    (`id="openAlerts"`, `⚠ Alerts`, next to `openRec`), mirroring the existing
    dialog idiom (`.dlghead` + `✕` `data-close`). The inner ids `riskSum`,
    `atten`, `escs` are byte-identical, so every render function (`renderRisk`,
    `renderAtten`, `renderEsc`) keeps writing into them via `el(...)` with zero
    logic changes — the nodes exist whether the dialog is open or not. `.right`
    keeps Agents, Gates, and Decisions.
69. **Red-state alerts button.** On every state poll (in `refresh`, alongside
    `renderEsc`) the button recomputes: gray `⚠ Alerts` when calm; the red
    `.pillbtn.alert` modifier (border+text `#a33b38` family) plus a count
    `⚠ Alerts (N)` when `escalations.length + attention.length > 0`. No new
    endpoint or snapshot key — it reads the same `st.escalations`/`st.attention`
    the sections already consume.
70. **Metrics header button removed.** The `openMet` button, the `metDlg` dialog,
    and `openMetrics()` + its wiring are deleted as duplicated info. The LEFT-aside
    metrics panel (`id="metPanel"`, fed by `metricsTiles(m, true)` on the throttled
    poll) STAYS — that is where the owner says the info already lives. `metricsTiles`
    is untouched (still the compact left-panel renderer).

```gherkin
Feature: Supervision panel — Alerts modal + Metrics-button removal

  Scenario: [ui_e2e:risk-summary] the risk summary renders inside the Alerts modal above Attention
    Given the panel with the Alerts modal
    When the owner opens the Alerts modal
    Then the risk-summary strip renders above the Attention bay inside the dialog
```

*Ceiling.* The moved sections lose their `.right .sec` scoped styling inside the
dialog (default `.dlgbody` layout); tuning that is the owner's visual pass, not a
gate concern. The `renderAtten` esc-jump strip still targets `.right .escs`, which
no longer matches once `.escs` lives in the dialog, so that intra-column scroll
degrades to a guarded no-op (both sections are visible together in the modal
anyway) — restore it by rescoping the selector if the owner asks. No frozen
registry moves: no new panel action, CLI verb, or TSV opt-in.

### v14 test strategy

`testing/scenarios/ui_e2e.py` (optional, self-skipping Playwright layer) opens
`#openAlerts` before its `#riskSum` assertions and checks DOM order
`riskSum → atten` inside `#alertsDlg` — the moved sections still satisfy the
"risk summary above the Attention bay" check. `m5_ui_panel.py` stays green
untouched: `page:metrics-panel` (`id="metPanel"`), `page:stat-tiles`
(`metricsTiles`), and the frozen `head_actions`/dialog-presence checks are all
unaffected (no ACTIONS/verb/TSV change). Prior checks stay green.

## Universal baseline impact

`specs/00-universal/api-and-interface-security.md` (loopback bind, per-session token, allowlist — this spec is stricter), `secrets-and-configuration.md` (token never in a GET body, log, or page source beyond the authed page's own JS), `observability-and-operability.md`, `ai-agent-safety.md` (HITL flags structurally refused), `testing-and-quality-gates.md` (the Playwright E2E is an optional, self-skipping dev layer — the runtime stays stdlib-only and the gates green without it).

## Escalation triggers

Any request to bind beyond loopback, add auth/accounts, persist panel state, or expose a controlled-write merge through the panel → human decision. Any button needing a capability the CLI lacks → ship the subcommand first, do not add a second write path in the panel.

## Amendments

- **2026-07-20 (api-events-endpoint, SPEC-116 versioned amendment):** the panel gains
  read-only `GET /api/events` — the redacted tail of `.harness/runs/events.jsonl`
  (`limit` capped 500, `event`/`workflow` filters), closing the GUI-plan §12 backend gap
  the WB5 deterministic-transitions timeline and the GUI-OP3 workflow drill depend on.
  Implementation `harness_lib/ui_events.py` (never-crash line parsing, malformed skipped
  + counted; every string value through `secret_scan.redact_text` before egress — the P5
  pre-egress discipline). Same loopback+token gating as every GET. Acceptance:
  `m5_ui_panel.py` check `events:tail-filtered-redacted` (fixture lines incl. a planted
  key-shaped token that must never egress). GUI-writes-no-state: pure read.
- **2026-07-20 (/api/runtime, OP-δ pre-req, SPEC-116 versioned amendment):** read-only
  `GET /api/runtime` — the live resource/lock surface: executor circuit breakers
  (`.harness/runtime/executor-circuit-*.json`), gate-holds (incl. `*-recovered`
  orphans) and workflow `.run.lock`s, as FACTS (pidAlive/ageSeconds computed; no
  fabricated staleness verdict) with every string value redacted
  (`harness_lib/ui_runtime.py`). Acceptance: `m5_ui_panel.py` check
  `runtime:snapshot-facts-redacted` (planted key never egresses). Feeds GUI-OP4
  (resources/locks) + GUI-OP5 (incidents: open circuits + recovered holds).

### v15 — IDE shard write path (owner-approved 2026-07-23)

**Workspace writes are shard-only.** The `ws-file-*` verbs mutate ONLY the
IDE shard worktree (`harness/ide-shard`), never the live tree; the live tree
changes exclusively through the Integrate action, which stages the shard
diff on main and consolidates it through the same `gate-staged` + `reckon`
flow (and the same `protected-path-modified` merge scan, SPEC-148 rule 11)
that governs agent-authored code. "GUI writes no state" is unchanged for
`.harness/`; for the workspace it sharpens to "GUI writes shard-only".
