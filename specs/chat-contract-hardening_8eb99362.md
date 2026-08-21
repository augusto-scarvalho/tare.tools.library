# Chat contract hardening (`rhc`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/rh_chat_contracts.py).

Intake (SPEC-116 door NEW): spec-recovery batch, rec-chat-4/5/6/7/8 — five
shipped-but-untested chat rules across the operator REPL's engine layer. Each
governs whether an agent engine may run, propose, or be blocked from a harness
command, or how a mode maps onto the REAL vendor session (not just a prompt
tag). None had a spec pinning the contract or a scenario exercising it; all are
offline-testable pure builders / gate ladders, so the risk is a silent
regression in the security-relevant gating with no failing check.

## Goal

The five chat contracts are written and permanently exercised: the Claude
argv always pins an explicit permission mode and forbids the plan-mode tools;
accept-edits (and only accept-edits) widens the Claude allowlist to all harness
commands; the OpenAI engine's gate ladder blocks human-only flags, proposes in
plan mode, confirms in auto/manual, and auto-runs in accept-edits; and the
intake-triage packet is injected on exactly one path (openai) while the
`/repo`-session escalations rewrite scopes a bare `!escalations` to its subject.

## Applicability

Applies to `scripts/harness_lib/chat_engines.py` — `ClaudeEngine._argv`
(`146-170`), `ClaudeEngine.send` (`172-177`), `OpenAIEngine._run_tool_call`
(`436-464`) — and to the inline guards in
`scripts/harness_lib/chat_operator.py` `run_chat` (triage prepend `751-755`;
escalations `--target` rewrite `725-727`). Coverage is offline via `__new__`
object surgery (the `rh_codex_engine.py` idiom): the argv builders and the gate
ladder are pure, one `subprocess.Popen` seam and one `run_harness_command`
executor are stubbed, and the two inline `run_chat` guards — which have no
callable helper — are pinned by a function-scoped `inspect.getsource` assertion
on the guard expression. No engine binary is spawned, no HTTP is made, the repo
is never mutated.

## Requirements / invariants (numbered, testable)

1. **Claude argv pins mode and forbids plan tools.** `ClaudeEngine._argv`
   emits an explicit `--permission-mode` for every `chat_mode`
   (`plan`->`plan`, `accept-edits`->`acceptEdits`, `auto`/`manual`->`auto`) and
   always lists `EnterPlanMode` and `ExitPlanMode` under `--disallowedTools`;
   the read-only allowlist never contains either tool
   (`chat_engines.py:158, 162-163`; `_allowed_tool_patterns` `118-126`).
2. **accept-edits widens the allowlist, nothing else does.**
   `ClaudeEngine.send` appends `Bash(<project-python> scripts/harness.py *)` to
   the allowed tools when and only when `chat_mode == "accept-edits"`; the
   `manual`/`plan`/`auto` argv omit that wildcard
   (`chat_engines.py:173-177`, SPEC-111 R23).
3. **OpenAI gate ladder.** `OpenAIEngine._run_tool_call` blocks a command
   carrying a human-only flag (`--approval-token`/`--send`) with the
   `human-in-the-loop flag` message; in `plan` mode a mutating command returns
   `blocked: plan mode — propose this command instead of running it`; in
   `auto`/`manual` it routes through the `y/N` confirm and returns
   `user declined to run this command` when declined; in `accept-edits` it
   auto-executes via `run_harness_command` (`chat_engines.py:436-464`).
4. **Triage packet is single-path.** `run_chat` prepends the SPEC-117
   intake-triage packet to the turn message ONLY when the active engine is
   `openai`; `claude`/`codex` receive it through their own `UserPromptSubmit`
   hook, so a second injection here would be double-counting
   (`chat_operator.py:751-755`, SPEC-117 inv.4).
5. **`/repo`-session escalations scoping.** Inside a `/repo <target>` session, a
   human-typed bare `!escalations` (no explicit `--target`) is rewritten to
   append `--target <subject>`; an explicit `--target` passes through untouched
   (`chat_operator.py:725-727`, SPEC-109 esc-scoped-hitl-view).

## Gherkin scenarios

```gherkin
Feature: chat contract hardening

  Scenario: [rhc-1] Claude argv pins an explicit mode and forbids plan tools
    Given a headless Claude engine in each interaction mode
    When the argv is built
    Then it carries the mode's explicit permission mode
    And EnterPlanMode and ExitPlanMode are disallowed and never allowed

  Scenario: [rhc-2] only accept-edits widens the Claude allowlist
    Given a headless Claude engine
    When it prepares a turn in accept-edits versus manual, plan and auto
    Then only accept-edits adds the `harness.py *` allowed-tools wildcard

  Scenario: [rhc-3] the OpenAI engine gate ladder
    Given the OpenAI engine faced with a run_harness tool call
    When the command is human-only, or the mode is plan, auto, or accept-edits
    Then it is blocked, proposed, declined on confirm, or auto-executed in turn

  Scenario: [rhc-4] the triage packet is injected on the openai path only
    Given the per-turn send path in run_chat
    When the active engine is openai
    Then the intake-triage packet is prepended, and not for claude or codex

  Scenario: [rhc-5] a bare escalations is scoped to the repo session subject
    Given a /repo session on a target with no explicit --target typed
    When the human runs a bare escalations command
    Then it is rewritten to append --target for that subject
```

## Rationale & sources

| Decision | Sources |
|---|---|
| Pin the per-mode permission mode and the plan-tool ban | headless `--resume` cannot approve its own plan-mode exit and a machine's user-scope `defaultMode` can silently pin plan (incident 2026-07-10: badge said auto, session answered in plan) — `chat_engines.py:158, 161-163` |
| Assert the accept-edits widening in `send`, not `_argv` | the wildcard append is inline in `send` (`174-177`), not the pure `_argv` builder; the scenario stubs `subprocess.Popen` to capture the constructed argv (the allowlist is embedded via `--allowedTools`) rather than re-run the pure builder |
| Drive the gate ladder at `_run_tool_call` with stubs | the ladder combines `classify_command` + `gate_for`; the executor (`run_harness_command`) and the `y/N` prompt (`prompt_kit.confirm`) are the only I/O and are stubbed — no HTTP, `_chat` is never reached — `chat_engines.py:436-464` |
| Pin the two inline `run_chat` guards by source, not behavior | both live in the REPL loop with no callable helper (plan named a "command-rewrite helper" for rhc-5 that does not exist; rhc-4's prepend is likewise inline) — a function-scoped `inspect.getsource(run_chat)` assertion on the guard expression is the honest pin, not a whole-file grep — `chat_operator.py:725-727, 751-755` |
| Door NEW (not amendment) | no existing spec documents these five chat contracts (rec-chat-4/5/6/7/8: shipped, no spec, no scenario) |
| Evidence | code line ranges above; sibling batch `testing/scenarios/rh_codex_engine.py` (rec-chat-1/2/3) |

## Plan-vs-code corrections

Pinned against the source, as the overseer plan directed:

- **rhc-2 seam.** The plan cites the accept-edits append at `174-177` and says
  "assert the constructed allowedTools list". That list is built inside `send`,
  which spawns `claude`; the scenario drives `send` with `subprocess.Popen`
  stubbed to capture the real argv (allowlist embedded via `--allowedTools`),
  which exercises the actual append rather than a re-implementation.
- **rhc-4 / rhc-5 have no callable helper.** The plan describes rhc-5's rewrite
  as "the command-rewrite helper" to "call directly with a fake session state".
  No such helper exists — the rewrite is three inline lines in `run_chat`'s
  `!`-escape branch (`725-727`), just as rhc-4's triage prepend is inline
  (`751-755`). Neither is callable in isolation (both need the full REPL loop,
  stdin, and a live engine), so both are pinned with a function-scoped source
  assertion on the exact guard expression — the fallback the plan itself allows
  for rhc-4 ("otherwise pin with a precise source assertion").

## Ceilings (upgrade paths)

The rhc-4/rhc-5 source pins assert the guard text, not runtime behavior; if
`run_chat`'s `!`-escape and triage-prepend logic is ever extracted into a
callable helper (`chat_operator` shrink), upgrade those two checks to drive the
helper directly with a fake session state and drop the `getsource` pins.

## Test strategy

- Behaviors: per-mode permission-mode + plan-tool ban (rhc-1); accept-edits-only
  allowlist widening (rhc-2); the four-rung OpenAI gate ladder (rhc-3);
  openai-only triage injection (rhc-4); repo-session escalations `--target`
  rewrite (rhc-5).
- Edge cases: `manual` and `auto` both map to the `auto` permission mode; a
  declined confirm returns the decline string and the prompt was actually
  invoked; the wildcard is absent from every non-accept-edits argv.
- Regression risks: silent loss of the plan-tool ban or the human-only block is
  a gating regression with security impact — hence the permanent scenario.
- Coverage impact: enforced via `testing/scenarios/rh_chat_contracts.py`
  (stdlib-only, offline, repo read-only).

## Validation

- `python testing/scenarios/rh_chat_contracts.py` — rhc-1..rhc-5 green.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.

## Amendments

(none yet)
