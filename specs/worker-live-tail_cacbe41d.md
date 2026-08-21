# SPEC-118 — Live worker output: runtime redirect + `workflow tail`

Status: SPEC-118, proposed 2026-07-11 (acceptance: testing/scenarios/worker_live_tail.py).

## Goal

A background worker's stdout/stderr is observable *while it runs*, not only after
it settles. The runtime writes each worker's stdio straight into its run-log files
at spawn time, and a read-only `workflow tail` command exposes the last N lines
(optionally following new lines) per worker. This is the data source the panel
drill-in (SPEC-114 v6) consumes; the CLI is the first-class surface.

## Applicability

Applies to `scripts/harness_lib/async_runtime.py`
(`workflow_async_run_one_worker` spawn/settle path, `workflow_tail`),
`scripts/harness_lib/async_state.py` (`tail_lines`), and the `workflow tail` CLI
in `scripts/harness.py`. Does not change await policy, cancellation, scheduling,
failover, or any worker-result contract; does not add streaming to the ambient
dashboard (that stays SPEC-114's categorized cards) and does not expose
vendor-CLI internal subagents (no per-session data source).

## Requirements / invariants (numbered, testable)

1. **Live logs.** A worker writes stdout/stderr directly into
   `run-logs/*.log`, opened at spawn and inherited as the child's stdio; the files
   exist and grow while `status == "running"`.
2. **Settle intact.** Result extraction from stdout, rate-limit detection, the
   `returnCode`, and all status transitions read the same text the in-memory PIPE
   produced — settle semantics are byte-compatible with the pre-change path.
3. **Budget kept.** The post-settle `maxStdoutChars`/`maxStderrChars` cap and the
   `stdoutTruncated`/`stderrTruncated` flags are preserved; a timeout appends the
   `TIMEOUT after Ns` marker to the stderr file and escalates TERM → KILL as before.
4. **`workflow tail` JSON.** Returns the last N stdout/stderr lines per worker; an
   unknown workflow or worker is a `HarnessError` (exit ≠ 0) and never probes
   outside the workflow's own directory.
5. **`--follow`.** Streams new lines (prefixed per worker: `[id]` stdout, `[id!]`
   stderr) until the group reaches a terminal state or `--timeout`; the poll
   interval is clamped to ≥ 0.1s.
6. **Read-only.** `tail` never writes state, events, or locks and never blocks the
   supervisor; a hash of `workflow.json` + `async/` is identical before and after.
7. **Absence is a state.** A missing log (a queued/never-started worker) returns
   `exists:false` with empty lines at exit 0 — not an error.
8. **Bounded reads.** Every reader decodes `errors="replace"` and reads at most a
   bounded tail of bytes from the end of the file; no reader loads an unbounded log
   into memory, and a byte-torn first line at the seek boundary is discarded.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Causa-raiz: worker era `stdout=PIPE` + `await communicate()` — bufferizado em memória até settle, sem arquivo para tailar | `scripts/harness_lib/async_runtime.py` (bloco PIPE+communicate ~349/362/383 pré-mudança) |
| Redirecionar stdio do filho direto pros arquivos de log (handles abertos no spawn, herdados) | padrão já provado do `supervisor.stdout.log` (`async_runtime.py` ~688-694: `open`→`Popen(stdout=fh)`→close no finally) |
| Teto: só workers do harness aparecem; sem streaming intra-turno de subagentes de CLI vendor | SPEC-114 (`supervision-m5-interactive-panel.md` ceiling R107) |
| Reconciliação com "panels categorize, never stream" (regra restringe defaults ambientes, não inspeção deliberada) | `docs/IMPLEMENTATION_BACKLOG.md` M5.3 human-factors (dark-pattern / tunelamento atencional) |
| CLI-first (attach tmux-style rejeitado; harness é async-by-contract, GUI é casca sobre a CLI) | `docs/SUPERVISION_UI_IDEATION.md` §7-8 |
| Leitura só do fim, `errors="replace"`, descarte da primeira linha parcial | leitura concorrente segura sob Windows (o escritor mantém o handle; `open("rb")` não trava) — mesmo racional do log do supervisor |

## Ceilings (upgrade paths)

- **Child buffering.** stdout redirected to a file is block-buffered in many CLIs,
  so live growth shows only flushed bytes (the fixture uses `python -u`; the real
  claude fix is the `--output-format stream-json` follow-up — see SPEC-114 v6).
- **Polling, not SSE.** `--follow` and the panel drawer poll; the upgrade path is a
  dedicated SSE channel in the chat's pattern once log volume justifies it.
- **Inkillable child on timeout.** The wait ladder may return without reaping; the
  handles close in `finally` and read-back proceeds from what was flushed — strictly
  better than the pre-change `b"", b""`.

## Test strategy

- Behaviors to verify: log grows while running; `tail` last-N and mid-run; missing
  log → `exists:false`; unknown WF/worker → non-zero exit; `--follow` captures new
  lines; result extraction from stdout via read-back; timeout marker; cancel
  unaffected; read-only invariance.
- Edge cases: worker printing > cap (truncation preserved); never-started worker;
  byte-torn line at the seek boundary (covered by `tail_lines` decode/discard).
- Regression risks: the shared settle path — `testing/scenarios/wf_failover.py`
  and the async-workflow fixture are the net; field/event/status names unchanged.
- Coverage impact: enforced via `testing/scenarios/worker_live_tail.py` (deterministic,
  no LLM — a synthetic executor running a `python -u` fixture child).

## Validation

- `python testing/scenarios/worker_live_tail.py` — the SPEC-118 acceptance checks
  (`tail:*`) all green, including the v2 amendment: `tail:follow-footer` (the
  `--follow` capture ends with the footer JSON line) and the extended `tail:read-only`
  (a `--follow --timeout 2` on a settled WF leaves state byte-identical — the
  `recover=False` regression net).
- `python testing/scenarios/wf_failover.py` — settle-semantics regression net stays
  green after the runtime redirect.
- `python scripts/harness-test.py spec-pack --no-project-commands` — template
  conformance (this spec has no Gherkin: CLI/runtime surface, non-UI).

## Amendments

### v2 (2026-07-11)

Numbered requirements continue the list.

9. **Exit footer.** `workflow tail --follow` ends by printing one final JSON line
   naming the group's state and a suggested next command —
   `{"asyncGroup": <status>, "next": "python scripts/harness.py workflow <collect|await> <WF>"}`
   (`collect` when the group is terminal, `await` otherwise). The supervisor is never
   left guessing what happened or what to run next.

**Conformance note (rule 6).** The `--follow` loop polled
`workflow_async_status(..., recover=True)` every tick; `recover` lists tasks, checks
pids, and can WRITE state (mark orphaned) — a read-only violation of rule 6. Corrected
to `recover=False`. No new rule: rule 6 ("tail never writes state") already covered it;
this is a conformance correction, and `tail:read-only` now also exercises the
`--follow` path as its regression net.

### v3 (2026-07-11) — stream-json executor

Lifts the v1 "Child buffering" ceiling. The `claude` executor template now carries
`-p --output-format stream-json --verbose` (verified flags, claude 2.1.207): output
is NDJSON, **line-flushed** by the CLI, so the live tail (rule 1) shows individual
events mid-run — no more block-buffering wait — and the panel drawer's `fmtStreamLine`
(SPEC-114 v6) renders structured activity (tool calls, assistant text, result) live
instead of opaque text. Numbered requirements continue.

10. **stream-json parser.** `scripts/harness_lib/stream_json.py:parse(stdout)` derives a
    COMPACT summary from the NDJSON — never a second stored copy of the event stream.
    Detection: the first non-empty line parses as a JSON object with a `type` key.
    Tolerant: torn/garbage lines are skipped; missing usage → `None`. It returns
    `isStreamJson`, `finalText` (the final `result` event's `result` field; fallback:
    concatenated assistant text blocks), `usage` (`inputTokens` = input + cache-creation
    + cache-read, `outputTokens`, `costUsd` from `total_cost_usd`), `activity`
    (`toolCalls`, `assistantTurns`, `model`, `durationMs`), `errorText`, and
    `finalResultLine` (raw last result line).
11. **Settle uses the parse, byte-identical otherwise.** When `isStreamJson`, result
    extraction and rate-limit detection read `finalText` (exact — no more substring
    re-scan of prose); rate-limit also scans `errorText` (is_error result events,
    non-`allowed` rate_limit_events) — NOT the raw envelope, whose benign
    `rateLimitType` key would false-positive the `ratelimit` needle. `observedUsage`
    and `activity` ride the run payload AND the async task JSON. When not stream-json
    (synthetic, codex, openai-compat, plain claude), the raw-text path is unchanged.
12. **Observed vs estimated cost.** `cost_metrics.record_workflow` sums worker
    `observedUsage` into real `observedTokens`/`costUsd` when present and stamps
    `costBasis: "observed"`; otherwise it keeps the chars/4 estimate and
    `costBasis: "estimated"`. `expense()` already prefers `costUsd`, so real spend
    now lands in the cost ledger and `topExpensive`; `summarize` exposes
    `workflows.costBasisShare` and `workflows.costUsd` so the panel is honest about
    which basis it is reading.
13. **Truncation preserves the result event.** The log cap is unchanged, but because
    `truncate_text` keeps the HEAD and the `result` event lives at the END, a
    head-truncated stream-json log appends `finalResultLine` after the truncation
    marker — one line, preserving the load-bearing event for post-mortem drawers.

**Ceiling update (v1 "Child buffering").** Superseded for the `claude` executor by
requirement 10 above; the fixture's `python -u` remains the deterministic-test stand-in
and non-stream-json executors keep the original block-buffering ceiling.

**Validation (v3).** `testing/scenarios/worker_live_tail.py` adds `tail:streamjson-extract`
(parsed, not substring), `tail:streamjson-usage` (observedUsage + activity on run payload
and task JSON), `tail:streamjson-fallback` (raw-text worker settles with no observed
fields — regression net), and `tail:streamjson-truncation` (head-truncated log ends with
marker + the result-event line). `stream_json.py` and `cost_metrics.py` carry `__main__`
self-checks. Live: one real claude fork-join worker — NDJSON grows line-by-line, result
valid, `observedUsage` present with real numbers.

### v4 (2026-07-11) — worker session diet + per-role payload tailoring

Two cost cuts to what a worker loads: the vendor **session** (flags on the template) and
the harness-authored **payload** (packet/digest/contract). Numbered requirements continue.

14. **Session-diet flags (template-only).** The `claude` executor template carries
    `--strict-mcp-config --setting-sources project,local --disable-slash-commands
    --exclude-dynamic-system-prompt-sections` (verified in CLI 2.1.207; min CLI 2.1.x).
    They strip USER-scope MCP servers/settings/skills and per-machine system-prompt
    sections a workflow worker never uses, while leaving built-in tools (write workflows
    keep Edit/Write), project hooks (guardrails), and CLAUDE.md intact. Non-claude
    executors are untouched. Measured cut (Phase A, single-turn context =
    input+cache_creation+cache_read): **36,841 → 21,779 tok/turn, −41%**;
    `--setting-sources project,local` is the dominant lever (−12,647). Subscription auth
    survives (a live smoke authenticated and produced a WORKER_RESULT under the flags,
    because auth reads `~/.claude`, not settings sources).

    **Honest metric caveat.** `observedTokens` (the result event's usage summed over ALL
    turns) is dominated by turn count, which is nondeterministic and NOT controlled by
    these flags: a diet smoke that took 15 turns billed more than a 6-turn baseline of the
    same packet. The sound, transferable metric is per-turn context size (requirement above)
    and the stability of the cacheable prefix across a wave, not a single worker's total.
    The ≤50k `observedTokens` target from the original plan is therefore recorded as
    unsound; the diet is justified on the per-turn cut, auth-safety, cache-prefix stability,
    and the security/privacy win of no user-scope config in workers.

15. **Per-role payload tailoring.** The harness-authored payload is trimmed where a role
    cannot use a piece. (a) When `sharedContextDigest` is on, the packet's WORKER_RESULT
    reminder is a terse pointer to the digest's verbatim contract instead of a re-listing of
    the schema keys (the contract already reaches the worker verbatim via the digest —
    triple-mention removed). (b) `tools/openai_worker.py` strips the packet's `Required reads`
    section before the single POST: an HTTP single-shot worker has no filesystem/tools, so
    the 5-file list is dead weight and actively misleading. **Non-research CLI-worker packets
    stay byte-identical** (guarded by `rs:digest-optout`); only opted-in research packets and
    the HTTP path change.

**Phase C — deferred, conditional.** A `--tools` read-only allowlist for read-only workers
(drop built-in tool schemas a non-write worker never invokes) was NOT implemented: the
residual per-turn context after the diet is ~21.8k and the built-in schemas are the largest
remaining lever, but the cut needs its own live measurement and a write-workflow safety
review before the seam (`{tools}` placeholder) is worth adding. Recorded as a ceiling.

**Deferred payload wins (measured, not applied — see `docs/research/deep-research-pipelines.md`
§E4).** Extend the digest (or a slim inline) to non-research analysis profiles:
−7,615 tok/worker (required-reads 12,092 → 4,477). Slice the HTTP worker's inlined contract
to the WORKER_RESULT section only: −2,096 tok/call (2,581 → 485). Both are guarded/scoped
changes that warrant their own amendment.

**Validation (v4).** `worker_live_tail.py` adds `tail:template-diet` (the four flags are on
the claude template and ONLY there); `rs_research_skill.py` adds `rs:packet-dedupe` (research
reminder is a pointer, key-list gone) and `rs:openai-packet-trim` (HTTP packet drops Required
reads, keeps Rules + reminder). `rs:digest-optout` and `rs:worker-stub-roundtrip` stay green
(non-digest byte-identity; HTTP end-to-end intact). Live: Phase A 4-variant measurement + a
1-worker before/after smoke (throwaway job scripts, not committed).

### v5 (2026-07-15) — per-role context diet, vendor-neutral intent, chat + triage surfaces

Owner decisions 2026-07-15: apply the session diet to the SPEC-144 front-desk (`router` chat
role), make the intent **vendor-independent**, and evaluate every role. Numbered requirements
continue.

16. **Vendor-neutral intent (`contextDiet` per role).** A role in
    `.harness/routing/model-routing.json` may declare
    `contextDiet: {vendorUserLayer:false, canonicalReinject:false, keepTools:[...]}`;
    `model_routing.resolve_role` passes it through verbatim. ONE home serves both consuming
    surfaces (the chat resolves roles there, and `route_loop._model_triage` resolves the same
    `router` role). `keepTools` speaks in capabilities (`exec`, `todo`, `read`, `edit`, `web`,
    `agents`, `skills`, `plan`), never vendor tool ids.

17. **One translator (`scripts/harness_lib/context_diet.py`).** The only place that knows how
    each vendor spells the cut: `layer_flags` (claude → the four v4 flags; codex →
    `-c project_doc_max_bytes=0`, best-effort AGENTS.md skip on codex ≥0.144), `denied_tools` /
    `tool_flags` (claude `--disallowedTools` complement of keepTools; codex/openai no knob →
    honest no-op), `env_for` (`canonicalReinject:false` → `HARNESS_SKIP_REINJECT=1`, vendor-
    neutral because the reinjection hook is OURS), `flags_for` = layer + trim. Unknown
    executors and absent diets translate to nothing — byte-compat.

18. **Chat surface adoption.** `chat_engines.build_engine` resolves the role's diet and hands
    it to every fallback hop; `ClaudeEngine` merges diet-denied tools into its ONE existing
    `--disallowedTools` (a repeated flag risks last-one-wins overriding the plan-mode lockout)
    and unions the chat surface floor `{exec, todo}` (the REPL needs Bash for harness commands
    and TodoWrite for the plan HUD); `CodexEngine` appends its `-c` knob; `OpenAIEngine` is
    documented no-op (already minimal). Roles enabled: `router` (front-desk) and `overseer`
    (operator) — both converse via commands only, so user-scope plugins/pack/tool schemas are
    dead weight. Reverting a role = deleting its `contextDiet` key.

19. **Triage spawn adoption (narrow Phase-C lift).** `route_loop._model_triage` splices
    `tool_flags` (trim ONLY — the claude template already carries the v4 layer flags; adding
    `flags_for` would double them) before the rendered `{prompt}` and merges `env_for`. With
    `keepTools: []` the router playbook's "MUST NOT use tools" becomes structural. The worker
    template stays byte-identical (`tail:template-diet`). The v4 Phase-C ceiling is lifted ONLY
    for no-write surfaces (chat, triage); analysis/write workers remain deferred pending their
    own measurement + write-safety review.

**Measured (v5, haiku probes, single-turn context).** Chat child in this repo: user layer
−12.0K tok (dominant: the user-scope ponytail plugin), unused tool schemas −7.0K, canonical
pack −3.8K; full diet **40,264 → 16,520 tok/turn (−59%)**. Same honest-metric caveat as v4:
per-turn context is the sound metric, not multi-turn observedTokens.

**Validation (v5).** `rt-10` in `testing/scenarios/rt_route_dispatcher.py` (intent on both
roles; claude argv realization with ONE merged `--disallowedTools` + skip env; dietless
byte-compat; triage trim splice with the template's layer flags never doubled; codex/openai
mapping); `context_diet.demo()` self-check; `tail:template-diet` stays green. Live: a dieted
front-desk chitchat turn ≈17K ctx vs 40.7K before, with `route --task` dispatch still working.

### v6 (2026-07-15) — Phase C resolved: read-only worker tool trim + owner-editable diets

The v4 Phase-C ceiling ("a tools allowlist for read-only workers... needs its own live
measurement and a write-workflow safety review") is resolved with evidence, and the diet
becomes owner-editable per role in non-canonical profiles (CLI + GUI).

**Evidence (haiku probes, worker session = v4 template flags + `HARNESS_SKIP_REINJECT=1`).**
W0 baseline 21,647 tok/turn; deny {Task, WebFetch, WebSearch, EnterPlanMode, ExitPlanMode}
→ 18,977 (**−2,670, adopted**); further deny {Edit, Write, NotebookEdit} → −722 more
(**measured-and-REJECTED**: the contract's primary result path is saving to `resultPath` —
subagent-contract.md:72's stdout capture is the fallback, and trading extraction robustness
for 0.7K loses); further deny {Skill} → **±0 (REJECTED**: no token win, and review/security/
implementation declare skills in their capability panels). Graphify is a CLI flow (no skill
dir), unaffected.

20. **Read-only worker trim.** `workflow_spawn_command_for_prompt` takes
    `write_allowed: bool = False`; when falsy it splices
    `context_diet.tool_flags(executor, diet)` before the rendered `{prompt}`, where `diet`
    is the profile's model-routing role `contextDiet` if declared, else
    `context_diet.READONLY_WORKER_DIET` (keepTools exec/todo/read/edit/skills = deny
    web/agents/plan only). Worker-dict callers (`run_one_worker`, spawn-commands CLI,
    `async_runtime` start/failover/group) pass `worker.writeAllowed`; reviewer/reducer
    spawns ride the read-only default. **A writeAllowed worker is NEVER trimmed.** The
    executor templates stay byte-identical; non-claude executors are no-ops.
21. **Owner-editable diets (non-canonical profiles).** CLI: `routing diet --profile <p>
    --role <r> [--keep <caps|off|''>] [--user-layer on|off] [--reinject on|off] [--clear]`
    (`model_routing.set_role_diet`; canonical refused, unknown capabilities refused, role
    must exist). `routing show` surfaces `contextDiet` per role. `set_role` PRESERVES an
    existing diet on model edits; `profile save` carries diets into the new profile. GUI:
    the "Routing by role" matrix shows a ✂ diet badge and the role editor gains a "Context
    diet" section (user-layer / pack toggles + capability checkboxes) that fires the
    allowlisted `routing-diet` action; the canonical fork flow carries the diet edit.
    An explicit keep-all diet is the off-switch (empty denial → no flag).

**Validation (v6).** `tail:readonly-trim` (trim on read-only claude spawn argv with the
exact denied set; writeAllowed argv byte-identical; generic untrimmed; keep-all role diet
disables the trim), `mr:module:diet-roundtrip` (set/resolve/show/preserve-on-set-role/
carry-on-profile-save/clear + 4 guards), `m5:routing:diet-action` (action argv incl.
`--keep off` sentinel and `--clear`; page DIET_CAPS cannot drift from
`CLAUDE_CAPABILITY_TOOLS`), `context_diet.demo()`. Live: a real 1-worker claude scan
workflow spawned with the trim and returned a valid WORKER_RESULT.
