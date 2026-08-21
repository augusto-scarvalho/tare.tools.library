# SPEC-111 — REPL Interactive UX and Onboarding

Status: implemented (first consumer: `harness.py chat`); base TUI checklist passed 2026-07-10; manual checks pending: paste capture, fuzzy-finder live filtering, HUD/Shift+Tab (R22/R23)

## Goal

One standard for every interactive surface of the harness CLI — menus, text
prompts, confirmations, and first-run onboarding — so the REPL feels
consistent and polished on any terminal. The standard is owned by
`scripts/harness_lib/prompt_kit.py`; `harness.py chat` is the first consumer.

## Applicability

Applies to any subcommand that prompts a human being at a terminal. Does not
cover agent-facing output (stdout JSON contracts stay untouched), the
supervision HTML page, or full-screen/curses UIs.

## Scope

In scope:
- Prompt primitives: single-select, multi-select, confirm, text (incl. secret).
- The interaction-mode ladder (tui / numbered / no-input) and its detection.
- Glyph and ASCII-fallback rules.
- Chat preference persistence (`.harness/runtime/chat-prefs.json`).
- Onboarding journey 1: first launch of the chat REPL.
- Onboarding journey 2: project missing local configuration.
- REPL slash-commands.
- The model-cards registry (`.harness/routing/model-cards.json`) that feeds
  the model/reasoning selectors.

Out of scope:
- Color theming beyond on/off (no palette; ANSI is used for cursor movement
  and emphasis only).
- Adoption by non-chat subcommands (future work; R4 keeps it possible).

## Requirements / invariants

- R1 (mode ladder): every primitive resolves exactly one of three modes, in
  this order: `no-input` when `--no-input` was passed, `HARNESS_NO_INPUT=1`
  is set, or stdin is not a TTY; `numbered` when stdin is a TTY but stderr is
  not a TTY, `NO_COLOR` is set and non-empty, `TERM=dumb`, or VT/raw-key
  setup fails; otherwise `tui`.
- R2 (no-input semantics): in no-input mode a prompt with a default returns
  the default silently; a prompt without a default raises `HarnessError`
  (exit 2) whose message names the flag or env var that supplies the value.
  - Amendment (B1): `--engine openai` in `--no-input` with `--model` or
    `--endpoint` missing fails closed (rc 2, flag named) *before* build_engine,
    so the SPEC-115 cross-engine fallback can't mask the explicit engine's gap.
- R3 (defaults visible): every prompt renders its default in `[...]`; Enter
  accepts it. TUI select pre-highlights the default row.
- R4 (stderr only): all prompt rendering and hints go to stderr; prompt_kit
  never writes to stdout, so stdout stays parseable for any subcommand.
- R5 (escape route): Ctrl-C cancels any prompt with terminal attributes
  restored, cursor re-shown, and a newline printed; `KeyboardInterrupt`
  propagates. The TUI footer shows the key hints
  (`up/down move · enter select · ctrl-c cancel`, plus `space toggle` on
  multi-select).
- R6 (glyphs): TUI uses `?` marker, `❯` cursor, `◉`/`◯` multi-select marks;
  when the stderr encoding cannot encode them, the ASCII set `>`, `[x]`/`[ ]`
  is used. Numbered mode is always plain ASCII.
- R7 (disabled options): options may carry a disabled reason, rendered as an
  annotation (e.g. `[not found on PATH]`); the TUI cursor skips them; picking
  one in numbered mode re-prompts showing the reason.
- R8 (confirmation ladder): mild actions get no prompt; moderate actions get
  `confirm()` rendering `[y/N]` (default no); severe actions require typing a
  stated word exactly (case-sensitive). No flag bypasses a severe confirm; in
  no-input mode a severe confirm raises `HarnessError`.
- R9 (config precedence): resolved value = CLI flag > environment (including
  `.env` loaded with setdefault semantics) > `.harness/runtime/chat-prefs.json`
  > built-in default. The chat banner names which source won for
  engine/model/endpoint.
- R10 (prefs file): `.harness/runtime/chat-prefs.json`, gitignored, schema
  `{"schemaVersion": 1, "engine": str, "model": str|null, "effort": str|null,
  "endpoint": str|null}`. Written only after the user confirms saving.
  An unknown or corrupt file is treated as absent and never crashes chat.
- R11 (onboarding non-blocking): first run = prefs file absent, stdin a TTY,
  and no `--engine` flag → the wizard runs. Every step is skippable; the REPL
  is always reachable. `/config` and `chat --reconfigure` re-run the wizard;
  `chat --reset-prefs` deletes the prefs file.
- R12 (project checklist): after the wizard (and on `--reconfigure`), chat
  shows a local-setup checklist: `.venv` present; `.env` present when
  `.env.example` exists; each enabled provider's `requiresEnv` key set
  (checked after `.env` loading). Missing items are offered as a multi-select
  of fixes; entering a key uses a secret prompt (never echoed) and appending
  to `.env` sits behind a severe confirm naming the file. Skipping prints the
  manual instruction and continues.
- R13 (secrets): secret input is never echoed, never logged, and never
  persisted anywhere except the explicit `.env` append of R12.
- R14 (slash commands): the REPL accepts `/exit`, `/quit`, `/config`,
  `/engine`, `/help`, `/paste` (with its `/end` terminator), and the `!<args>`
  escape; `/help` lists all of them with one-line descriptions; an unknown
  `/x` prints a hint instead of being sent to the agent.
- R15 (piped runs unchanged): with non-TTY stdin there is no wizard and the
  engine defaults to `claude`; prefs still apply as defaults per R9.
- R16 (ANSI discipline): escape sequences are emitted only in tui mode;
  numbered and no-input output is plain text (safe for cp1252 consoles and
  log capture).
- R17 (selector over free text): whenever the set of valid values is
  enumerable — model cards, endpoint `/models` listings, fixed effort levels —
  the prompt is a selector (single-select with the default pre-highlighted, or
  multi-select with preselections), never bare free text. A final `custom…`
  option provides the free-text escape; free text is the whole prompt only
  when no enumerable choices exist.
- R18 (model cards): `.harness/routing/model-cards.json` drives the model and
  reasoning selectors. Schema: `{"schemaVersion": 1, "engines": {<engine>:
  {"models": [{"id" (required), "name", "provider", "reasoning": [levels],
  "description", "default": bool}]}}}`. The wizard builds the model menu from
  the engine's cards (card marked `default` is preselected), merges
  endpoint-listed models after them (deduped by id), and offers the effort
  menu from the chosen card's `reasoning` list (union of all cards when the
  choice has no card). A missing, corrupt, or empty registry degrades to the
  free-text prompt; entries without `id` are dropped. Editing the file changes
  the menus — no code change.
- R19 (multi-line input): on a TTY, a multi-line paste is captured as one
  block — after the first line is read, input already buffered on stdin is
  drained and joined — echoing `[captured N pasted lines]`. `/paste` … `/end`
  (or Ctrl+Z / Ctrl+D) is the explicit block mode; a line ending in `\`
  continues on the next line. A captured block prompts for one optional note
  ("add a note to send with it", Enter = send as-is; skipped in no-input
  mode) and note + block go out as a single message. Command lines (`/`, `!`)
  are never drained or expanded; piped stdin never drains (R15). Known
  limitation: keystrokes arriving in the same buffer window as the Enter may
  join the block — the capture echo makes this visible.
- R20 (@file mentions): a message token starting `@` at a word boundary that
  resolves to an existing file (repo-relative, absolute, or `~`) is attached
  to the outgoing message as a `[file: <path>]…[end of <path>]` block, capped
  at 64 000 chars with the harness truncation marker; the original `@token`
  stays inline. Binary files (NUL byte in the first 8 KB) are skipped with a
  stderr note; unresolved tokens remain plain text; e-mail-style `a@b` never
  matches. Expansion applies only to agent-bound messages (never `/` or `!`
  lines) and is uniform across engines — the claude engine's allowlist blocks
  it from reading files itself, so inlining is the single path.
- R21 (fuzzy file finder): in interactive modes, `@?` and any typed-line
  `@token` that does not resolve to a file open a type-to-filter picker
  seeded with the token. Candidates come from `git ls-files` (fallback: a
  bounded directory walk skipping `.git`, `.venv`, `__pycache__`,
  `node_modules`, `graphify-out`). Matching is ordered subsequence, ranked by
  span, position, then path length. TUI: typing filters live, arrows move,
  Enter picks, Esc skips (token stays as typed), Ctrl-C cancels the search
  without discarding the message. Numbered fallback: query prompt, then the
  top matches as a select with a `(skip — keep as typed)` row. The picked
  path replaces the token (`@token` → `@picked/path`) and R20 then attaches
  it. Pasted blocks never trigger the finder (an `@decorator` in pasted code
  is not a mention); no-input mode never opens it.
- R22 (bottom HUD): in tui mode the REPL keeps fixed bottom blocks drawn on
  stderr inside a DECSTBM scroll region — separator; engine telemetry row
  (context bar, last-turn tokens/cost/duration, session cost/turns, spinner +
  elapsed while a turn runs); agents panel (up to 4 rows: workerId, status,
  unit/profile, elapsed, ~tokens; "…and N more" beyond); status row
  (repo·branch │ engine·model·effort │ mode — segments drop right-to-left
  under width pressure, the mode always stays); input row (raw line editor).
  The HUD is fail-open: any exception disables it permanently and the REPL
  continues as plain tui; `HARNESS_CHAT_NO_HUD=1` is the kill switch;
  terminals under 10 rows never get a HUD; numbered/no-input modes are
  unaffected (R1/R15/R16 hold).
- R23 (interaction modes): `manual → plan → auto → accept-edits`, cycled by
  Shift+Tab (raw editor, VT input) and set by `/mode <name>`; default `auto`;
  session-only. Semantics on top of classify_command: plan — read-only
  commands run, mutating requests are refused with a "propose instead"
  reply; auto — today's behavior (read-only auto, mutations y/N or `!`);
  accept-edits — mutations pre-approved in ALL engines; manual — every plain
  line is a harness command (the engine session is preserved). The four HITL
  categories (`--approval-token`/`--send`) stay human-only in EVERY mode,
  enforced structurally by the PreToolUse hook `tools/hooks/deny_hitl_flags.py`
  (claude engine; applies to every claude session in this repo) and by the
  in-process gate (openai engine); the human paths (`!`, manual mode) set
  `HARNESS_CHAT_HITL_OK=1`. Engine parity: claude = per-turn `--allowedTools`
  sets + mode tag; openai = full in-process parity; codex = mode tag only
  until its sandbox flags are validated (documented gap, not a surprise).
- R24 (telemetry honesty): engine-reported numbers render as-is — claude from
  `claude -p` JSON (`total_cost_usd` is cumulative under `--resume`; the REPL
  reports per-turn deltas), openai from response `usage` (+ optional
  `contextWindow` in the model card), codex `n/a` until parsed. Harness
  worker tokens are chars/4 estimates and always carry `~`. Missing data
  renders `n/a`, never a guess. Outside the HUD, every turn prints one plain
  stderr summary line (`[turn: … · session …]`).
- R25 (project picker / session target): the working project resolves as
  `--target` flag > saved prefs `target` > interactive fuzzy picker on
  first-run (or `/repo`). Picker sources: the harness repo itself, registered
  governed targets (`.harness/targets/*/target.json`, SPEC-110), and
  `browse…` — sibling directories containing `.git`, where picking an
  unregistered repo writes a minimal `target.json` behind a confirm. An
  unknown `--target` fails closed (exit 2, legible fix); a saved target that
  no longer resolves warns and continues untargeted; piped runs never prompt
  (fuzzy_select returns None headless). With a session target: the HUD status
  row shows `repo→target`, every agent-bound message is prefixed with a
  `[target: <name> — pass --target …]` tag, and the `@` finder also lists the
  target repo's files as harness-root-relative paths (`../repo/src/x.py`);
  targets on another drive skip the listing with a note.
- R26 (cost ledger): `.harness/state/cost-metrics.json` (single JSON, never
  `.jsonl`; gitignored; survives gate wipes) keeps the last 500 records —
  chat turns with REAL engine-reported tokens/cost/duration, workflow
  summaries with chars/4 estimates plus real wall-clock durations and a
  `costUsd: null` seat for future executor-reported cost, and subagent
  delegations (`harness.py delegation <model> --tokens N --agent-type <type>` — planner→
  implementer/explore runs are real spend the loop must see). Writers are
  never-crash (telemetry loss must not break a turn or a finalize).
  `harness.py metrics` (read-only, agent-allowlisted) summarizes spend by
  model/target/day, top expensive runs, and estimator calibration
  (`observedCharsPerToken` = median replyChars/outTokens over real turns).
  The self-review loop consumes the summary: `workflow-cost-outlier` and
  `estimator-drift` findings (routing/model changes stay human-gated), and
  one safe action — `recalibrate_chars_per_token` steps
  `tokenBudget.charsPerToken` one bounded increment (≤0.5, clamped to
  [2.0, 8.0], ≥20 samples) toward the observed value, byte-backed-up and
  replay-verified like the ratchets. TE.2 adds the delegation stream, the one
  spend stream previously without a rule: `delegation-cost-outlier` fires when
  the latest delegation's estTokens exceed 1.5× the median of the previous 10
  (min 3 samples) or 250,000 absolute, and `delegation-cost-trend` fires when
  the median of the last 5 delegations exceeds 1.3× the median of the previous
  5 (min 10 samples). Both are base criticality `high` (no usage boost — they
  route straight through the R28 funnel as ⚠ in the HUD/panel), diagnose-only.
  The 2026 re-triage (`docs/SELF_EVOLUTION_IDEATION.md` §5) registers two more
  self-review guard rules alongside these findings, both base criticality
  `high`. `safe-action-rate-breaker` (I3-adj): when more than
  `safeActionMaxPerWindow` (default 5) safe actions have EXECUTED within the
  trailing `safeActionWindowHours` (default 24) — counted from
  `self_review_safe_action` events the loop now emits per executed action — the
  finding fires AND acts as a structural circuit breaker: `run_self_review`
  halts further auto-action EXECUTION (proposals/findings still flow) while the
  escalation is unresolved; a human resolve re-opens it. Source: 2026
  automated-remediation circuit-breaker guidance
  (aurorasre.ai/blog/automated-incident-remediation,
  safeguard.sh/resources/blog/the-case-for-autonomous-remediation-now),
  mirroring the executor circuit breaker (`workflow_executor_circuit_*`).
  `evolving-store-zombie-scan` (I11): a deterministic, report-only regex scan
  (`zombieScanPatterns`, case-insensitive, config-tunable) over the evolving
  memory stores (escalations `frictionLog`, `worklog.json`/records
  titles+bodies) flagging persisted instruction-like content, one finding per
  store hit (id carries store + entry ref), NEVER modifying the stores — the
  human inspects. The default `--approval-token`/fenced-shell patterns are
  narrowed to the smuggled-command form so legitimate worklog entries
  documenting those flags do not fire. Source: Zombie Agents
  (arxiv.org/pdf/2602.15654), MemAudit (arxiv.org/pdf/2605.23723).
  The final two re-triage picks (`docs/SELF_EVOLUTION_IDEATION.md` §5) add:
  `rule-proposal/*` provenance (I2-adj): the loop's "rules-that-propose-rules"
  move (a finding whose `proposedRule` is a concrete customRule a human may
  accept into the table) now REQUIRES `provenance` (`{sourceFinding, evidence,
  generatedAt}`) — the real path is friction recurrence, always provenanced.
  An auto-proposed rule (`proposedBy: self-review`) that reaches the acceptance
  path (the `customRules` evaluator) without valid provenance is REFUSED at
  apply and surfaced as `custom-<id>-unprovenanced` marked
  `[sem proveniência — não aprovar]`, so the human never approves blind against
  locally-correct-but-non-transferable (poisoned) experiences. Source: OEP
  (arxiv.org/pdf/2605.18930). `evolving-store-anomaly/*` (I9-adj): a
  deterministic, report-only audit over the evolving memory stores beyond the
  I11 zombie-scan — (a) entry-rate spike (a store gaining more than
  `storeEntryRateMax` entries, default 72 ≈ 3× the measured worklog baseline of
  ~24/24h, within `storeRateWindowHours`), (b) single-writer violation (a
  `worklog.json` entry whose top-level keys stray outside the `records.add_entry`
  contract `{at,kind,title,body,refs,tags}` = a foreign writer), (c) orphan
  resolutions (`resolvedIds` beyond `orphanResolvedMax`, default 20 vs the
  measured 4 legacy orphans, with no matching raised/resolved record =
  resolved-spam). One `high` finding per anomaly class per store; NEVER mutates
  a store. Source: MemAudit (arxiv.org/pdf/2605.23723), SSGM
  (arxiv.org/html/2603.11768v1).
- R27 (observation must pay for itself): metric-driven adaptations must be
  net-cost-positive INCLUDING the overhead of observing (collecting, storing,
  deciding). Where a deterministic solution matches or beats an LLM one, the
  deterministic one is used. Observation is event-driven (at process reap) or
  on-demand (when `metrics`/self-review run) — never a daemon or continuous
  polling; the chat HUD's 1s ticker (active only while the REPL is open) is
  the ceiling. Ledgers stay bounded. The observation stack measures itself:
  `metrics` publishes an `observability` section (ledger bytes, summarize
  self-timing, last self-review duration, state-file sizes) and self-review's
  `observability-overhead` rule raises a finding when its own run exceeds
  `selfReviewMaxDurationS`.
- R28 (machine impact + criticality tiers): per-worker tree CPU is captured
  deterministically at reap (Windows: Job Object accounting via
  suspend-assign-resume, covering launcher-respawned interpreters; POSIX:
  RUSAGE_CHILDREN delta) — one API call, no polling — and flows into the
  ledger (`cpuS`). `metrics` exposes `machine`: `harnessDiskMB` and
  `byStack` (harness-stack = untargeted records vs project-stack = targeted),
  the two requested views. Self-review findings carry
  `criticality: info | watch | high | critical` — deterministic base tier per
  rule family (ledger/HITL/protection integrity = critical; cost/burn-down/
  staleness = high; recurring friction/aging = watch; informational = info),
  raised one tier when the finding's subject (workflow type or target)
  accounts for ≥ `usageBoostShare` of ledger records (heavily used = review
  first). Routing: info = report only; watch = report + backlog inbox;
  high/critical = escalation (criticality persisted into
  `escalations.json.raised`). Warnings surface without new polling: the REPL
  prints a `[!] self-review: N high/critical...` line at startup (one state
  read) and the HUD status row shows a `⚠N` badge refreshed on the existing
  2s snapshot cadence.
- R29 (agent-facing compact output — TE.5): command output is a per-turn agent
  cost, so when `HARNESS_AGENT_OUTPUT=compact` is set — only by chat engines on
  the agent path (`run_harness_command` with `human=False`, and the Claude/Codex
  session subprocess env; never the `!`-escape/human path, never worker packets,
  whose char budgets are already calibrated) — harness.py emits
  compact-separator JSON, and the allowlisted flat-list commands (`models list`,
  `models catalog`, `records search`, `records recent`) emit TSV: header = union
  of keys in first-seen order, one tab-separated row per record, nested/None
  cells fall back to compact JSON with tabs/newlines flattened to keep one line
  per record. `targets list` is a dict envelope (count/hint), so it stays
  compact JSON, not TSV. With the env absent (humans, existing JSON parsers,
  every scenario) output is byte-identical to the legacy `indent=2` form.

## Acceptance criteria

- [x] Mode ladder resolves per R1 (verified by the prompt_kit self-check matrix).
- [x] No-input prompts return defaults silently and raise `HarnessError` naming the missing flag when required (R2).
- [x] Defaults are rendered in `[...]` and Enter accepts them in every mode (R3).
- [x] prompt_kit writes only to stderr (R4).
- [x] Ctrl-C cancels cleanly at any prompt with terminal restored (R5 — manual TUI checklist passed 2026-07-10).
- [x] Unicode glyphs fall back to ASCII off a real `encode()` probe (R6).
- [x] Disabled options show their reason and cannot be selected (R7).
- [x] Severe confirms require the typed word and fail closed in no-input mode (R8).
- [x] flag > env > prefs > default, with sources shown in the banner (R9).
- [x] Prefs are written only on confirm; corrupt prefs never crash chat (R10).
- [x] First interactive launch runs the wizard; second launch shows the banner and no wizard; `--reconfigure` / `/config` behave per R11 (wizard path confirmed in the 2026-07-10 manual checklist; `--reset-prefs` and the no-wizard second launch are covered headless).
- [x] The project checklist detects `.venv`, `.env`, and provider keys, offers multi-select fixes, and never blocks the REPL (R12).
- [x] Secrets are collected via getpass and only land in `.env` behind a typed confirm (R13).
- [x] Slash commands per R14, including the unknown-command guard.
- [x] Piped `chat` invocations behave exactly as before (R15).
- [x] No ANSI escapes outside tui mode (R16).
- [x] Enumerable choices render as selectors with a `custom…` escape (R17).
- [x] Model cards feed the model/effort menus, dedupe against endpoint listings, preselect the card default, and degrade to free text when missing or corrupt (R18).
- [x] `/paste`…`/end`, backslash continuation, the optional note, and the no-input/manual-mode guards behave per R19 (headless-verifiable parts).
- [ ] A real multi-line paste in a terminal is captured as one block with the `[captured N pasted lines]` echo (R19 — manual checklist).
- [x] `@file` mentions attach capped file content, skip binaries, ignore e-mails and unresolved tokens (R20).
- [x] `@?` and unresolved typed `@tokens` open the fuzzy finder; skip keeps the text; blocks and no-input never trigger it (R21 — headless-verifiable parts).
- [ ] TUI finder filters live as you type, Esc skips, Enter picks (R21 — manual checklist).
- [x] Mode machine, `/mode`, gate_for table, per-turn tags and allowedTools sets behave per R23 (headless: self-checks + piped scenario).
- [x] The HITL hook denies `--approval-token`/`--send` for agents and passes the human paths (R23 — subprocess-tested).
- [x] Telemetry: per-turn summary line with real claude tokens/cost deltas, honest `n/a`, `~` on worker estimates (R24).
- [ ] HUD renders and updates live: scroll region, spinner+elapsed during turns, agents panel during a workflow, resize degradation, clean restore on exit (R22 — manual checklist).
- [ ] Shift+Tab cycles the four modes in the raw editor (R23 — manual checklist).
- [x] Project target resolves flag > prefs > picker; unknown `--target` exits 2; saved-but-gone target degrades with a warning; piped runs never prompt (R25 — headless parts).
- [ ] Interactive picker lists targets + browse/register and the HUD shows `repo→target` (R25 — manual checklist).
- [x] Ledger records land per turn and per workflow finalize, bounded to 500, never crashing; `metrics` summarizes; self-review raises cost findings and the bounded recalibration verifies-or-reverts (R26).
- [x] Delegation spend is watched: `delegation-cost-outlier` (latest > 1.5× median of previous 10, min 3, or 250k absolute) and `delegation-cost-trend` (median last 5 > 1.3× previous 5, min 10) fire at criticality `high` into the one funnel (R26/TE.2; proven retroactively on the 309k SPEC-115 delegation).
- [x] Safe-action rate circuit breaker (I3-adj): > `safeActionMaxPerWindow` (5) executed safe actions in `safeActionWindowHours` (24) raises `safe-action-rate-breaker` at criticality `high` and structurally halts auto-action EXECUTION (proposals still flow) until the escalation is resolved; a human resolve re-opens it. Executed actions are event-logged as `self_review_safe_action` (se_self_review: fires/quiet/window + refused/allowed/latch/reopen).
- [x] Deterministic zombie-scan (I11): `evolving-store-zombie-scan` regex-scans the evolving stores (frictionLog, worklog/records) for persisted instruction-like content, one `high` finding per store hit, report-only (never mutates the stores); `zombieScanPatterns` is config; the real stores baseline clean (se_self_review: imperative/smuggled flagged, legit-grep/doc-mention not, real-stores-clean).
- [x] Rule-proposal provenance (I2-adj): auto-proposed rules carry `provenance` (`{sourceFinding, evidence, generatedAt}`); the real path (friction recurrence) is always provenanced, and the acceptance path (`customRules` evaluator) REFUSES a `proposedBy: self-review` rule with no valid provenance, surfacing `custom-<id>-unprovenanced` marked `[sem proveniência — não aprovar]` (OEP poisoning, arxiv.org/pdf/2605.18930; se_self_review: real-path-carries-provenance, unprovenanced-refused/marked, provenanced-applies).
- [x] Evolving-store anomaly audit (I9-adj): `evolving-store-anomaly/*` deterministic, report-only checks over worklog/frictionLog/resolvedIds — entry-rate spike (`storeEntryRateMax` 72 ≈ 3× measured 24/24h baseline), single-writer violation (foreign top-level keys vs the `records.add_entry` contract), orphan resolvedIds (`orphanResolvedMax` 20 vs 4 real legacy); one `high` finding per class per store, never mutating a store; real stores baseline clean (MemAudit 2605.23723, SSGM 2603.11768; se_self_review: rate-spike/quiet, writer-violation, orphan-resolved, criticality-high, real-stores-clean).
- [x] Observation stack self-measures (`observability` section; `observability-overhead` rule) and adds no daemon/polling (R27).
- [x] Worker tree CPU captured at reap lands in the ledger; `machine.byStack` separates harness vs project views (R28).
- [x] Findings carry criticality tiers with usage boost; only high/critical escalate; REPL startup warning and HUD `⚠N` badge read existing state (R28 — headless parts).
- [x] Agent-consumed output compacts under `HARNESS_AGENT_OUTPUT=compact` (compact JSON + TSV allowlist), default byte-identical, both modes round-trip (R29/TE.5 — `te_compact_output.py`: `routing show` 73.3%, `models list` TSV 43.9% of pretty chars).

## Test strategy

- Behaviors to verify: mode-detection matrix; numbered-mode parity with TUI
  semantics; precedence resolution; onboarding detection (prefs
  present/absent × flags × TTY); prefs save/load round-trip.
- Edge cases: corrupt prefs JSON; corrupt or absent model-cards registry;
  card entries without `id`; endpoint `/models` unreachable; cp1252
  stream encoding; Ctrl-C mid-prompt; option list where every entry is
  disabled; empty multi-select accept; empty paste block; `/end` missing
  (EOF terminates the block); oversized `@file` capped; binary `@file`
  skipped.
- Regression risks: scripted/piped `chat` runs (R15); existing `--engine`
  flag behavior; OpenAI engine y/N tool gate.
- Coverage impact: informational.

### Amendment (2026-07-12) — ClaudeEngine chat streams stream-json

The chat `ClaudeEngine` (R23 engine, `scripts/harness_lib/chat_engines.py`) migrated
from a buffered `-p --output-format json` blob to streaming `stream-json --verbose` (the
same adapter the worker path uses). `send` now spawns a streaming `Popen` and delegates
per-line handling to the pure `stream_json.parse_chat_stream(lines, on_tool)`, which fires
a tool descriptor per `tool_use` block so the operator sees tool/shell calls live; the
terminal `result` event still feeds the EXISTING `_telemetry`, so cost/ctx/tokens are
preserved, and `--resume <session_id>` / per-turn `--permission-mode` are unchanged.
Codex/OpenAI/manual engines are untouched. The panel-render half + the light per-turn
model attribution live in **SPEC-114 v13** (`supervision-m5-interactive-panel.md`);
deterministic coverage is `stream_json.py`'s self-check plus `chat:tool-events-parsed`
in `testing/scenarios/m5_ui_panel.py`. No LLM in gates — the canned transcript is the test.

## Validation

- `./.venv/Scripts/python.exe scripts/harness_lib/prompt_kit.py` — self-check.
- `./.venv/Scripts/python.exe scripts/harness_lib/chat_operator.py` — self-check.
- `./.venv/Scripts/python.exe testing/scenarios/ux_repl_onboarding.py` — headless acceptance scenario.
- `./.venv/Scripts/python.exe scripts/harness-test.py smoke --no-project-commands` and `spec-pack`.
- Manual TUI checklist:
  - Windows Terminal: arrows move the cursor, Enter selects, space toggles
    multi-select, Ctrl-C exits each prompt cleanly (cursor visible), second
    launch shows the saved-defaults banner without the wizard, `/config`
    re-runs the wizard.
  - Legacy conhost: VT enables on Win10+; if glyphs render wrong the ASCII
    fallback engages.
  - Git Bash mintty: plain `python scripts/harness.py chat` has pipe stdin →
    no-input mode (no wizard, R15); under `winpty` expect numbered mode
    (msvcrt/VT probes fail off a real console — the probes decide, never
    `TERM` sniffing).
  - `echo /exit | python scripts/harness.py chat --engine manual` stays
    scriptable.
  - Paste a real multi-line block in Windows Terminal: captured as one block
    with the `[captured N pasted lines]` echo and the optional-note prompt;
    a line ending in `\` continues on the next line (R19).
  - Type `@?` (or a wrong `@path`) in a message: the fuzzy finder opens,
    typing filters the list live, Esc keeps the text as typed, Enter picks
    and the chosen file is attached (R21).
  - HUD (R22/R23): blocks render at the bottom and the conversation scrolls
    above; Shift+Tab cycles manual→plan→auto→accept-edits in the status row;
    spinner + elapsed tick during an engine turn; agents rows appear during a
    `workflow execute`; narrow (<50 cols) hides the agents panel and short
    (<10 rows) disables the HUD; Ctrl+C and `/exit` restore full-screen
    scrolling and the cursor; legacy conhost either renders or falls back
    silently to plain tui.
  - accept-edits + claude: a mutating harness command runs unprompted, a
    `--approval-token` command is hook-blocked with the HITL message, and
    `!<same command>` still runs (human path).
- LLM-backed checks run on the cheapest capable model — `--model sonnet
  --effort low` (or `haiku` for trivial checks) — never Fable/Opus for
  plumbing verification.

## Universal baseline impact

- Software-engineering guardrails: `prompt_kit.py` is a new side-effect-free
  module boundary; `.env` writes stay in `chat_operator.py`.
- Canonical-file protection: `.env` is agent-write-blocked by hooks; only the
  human-facing CLI appends to it, behind the R8 severe confirm.

## Escalation triggers

- Any change that writes secrets anywhere other than the `.env` append (R12/R13).
- Any prompt added to a non-chat subcommand that could break stdout JSON contracts (R4).
- Any weakening of the confirmation ladder (R8) or of the no-input fail-closed rule (R2).
