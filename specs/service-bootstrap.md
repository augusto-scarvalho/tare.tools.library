# Service bootstrap — registry + lifecycle P0 (`svc-registry-mvp`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/sv_services.py).

Intake (SPEC-116 door NEW): request = "se o projeto que estivermos operando
tiver alguma dependência que precise de start — tipo servidor MCP — precisamos
que o harness faça esse BOOTSTRAP… caso do MCP server do ponytail"
(`docs/roadmap/dependency-bootstrap.md`). Covered-check: no lifecycle manager
exists — `capabilities.json mcpServers` is empty, the generated
`adapter/mcp-config.json` has zero consumers, nothing starts/stops a declared
dependency. Decision: **NEW**. SLICE: P0 ONLY — declare + idempotent start +
ready probe + orphan-free stop + reap. `svc-autostart-owners` (P1) and
`svc-mcp-wiring` (P2) stay OPEN; the ponytail entry itself waits on the OPEN
MCP-transport owner decision (stdio cannot be shared across sessions).

## Goal

Declare a long-lived dependency once (harness scope `.harness/services.json`,
or a target's `target.json` `services` key), then `services start <name>`
idempotently spawns it with a hidden console, blocks on its ready probe,
records a pidfile with an owner, and `services stop <name>` kills the whole
tree verifiably. Services are NOT daemons the harness babysits: dead pids and
live services whose owner died are reaped at the next `services status` — no
watchdog, no polling loop.

## Applicability

Applies to `scripts/harness_lib/services.py` (`load_registry`, `ensure`,
`stop`, `status`, `cmd_services`), the seeded empty
`.harness/services.json`, and one `cli_registry` line (zero `harness.py`
edits). Reuses `processes.py` primitives exclusively (`pid_alive`,
`signal_process_tree`, `process_group_kwargs` — which on Windows already
carries CREATE_NO_WINDOW: a service never flashes a console). No auto-start
wiring, no MCP consumption, no daemon.

## Requirements / invariants (numbered, testable)

1. **Declarative registry, two scopes, one schema.** Harness scope reads
   `.harness/services.json` `services{}`; target scope reads the target's
   `target.json` `services` key. An undeclared name fails legibly (exit 2).
2. **Idempotent start.** `ensure` returns `already-running` with the SAME pid
   when the pidfile's process is alive; a stale pidfile restarts; every spawn
   uses `process_group_kwargs()` (hidden console + group isolation) with
   stdout/stderr appended to a per-service log.
3. **Ready probe, fail-closed.** `ready.type` tcp/http polls up to
   `timeoutSeconds`; probe-less entries settle on pid-alive. A probe timeout
   or early exit STOPS the spawned tree, leaves no state file, and raises a
   legible cause/fix error naming the log.
4. **Orphan-free stop.** `stop` signals the process TREE (taskkill /T /F on
   nt, killpg on posix), waits `stopGraceSeconds`, escalates, verifies
   `pid_alive` false and only then deletes the state file — a child spawned
   by the service dies with it.
5. **Reap on observation.** `status()` removes state files whose pid is dead
   and stops live services whose `ownerPid` is dead — orphan recovery happens
   at the next invocation, never via a resident watcher.
6. **Least-privilege target env.** A target-scope service receives
   `targets.spawn_env` (deny-by-default) + subject coordinates + minimal OS
   base, never the full harness environment.
7. **Registry-only surface.** `services` registers via
   `cli_registry.register()`; the frozen top-level list gains exactly
   `services` (disclosed in `testing/scenarios/cli_registry.py`).

## Gherkin scenarios

```gherkin
Feature: service registry + lifecycle (P0)

  Scenario: [svc-idempotent] double ensure returns the same pid
    Given a declared probe-less service
    When ensure runs twice and stop runs once
    Then the second ensure reports already-running with the first pid and
      stop leaves the pid dead and the state file gone

  Scenario: [svc-ready-timeout] a never-ready probe fails legibly
    Given a service whose tcp ready port never opens
    When ensure runs
    Then it raises naming the timeout and the log, kills the tree and leaves
      no state file

  Scenario: [svc-orphan-free] stop kills the whole tree
    Given a running service that spawned its own child process
    When stop runs
    Then both the service pid and its child pid are dead

  Scenario: [svc-owner-reap] status reaps the dead and the ownerless
    Given a live service whose ownerPid is dead and a state file whose pid is dead
    When status runs
    Then the live one is stopped-orphan and the dead one reaped-dead

  Scenario: [svc-cli] the CLI guards its surface
    Given this repository with an empty registry
    When "services list" and "services start ghost" run
    Then list exits 0 and the undeclared start exits 2
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Owner-scoped on-demand + reap, nunca daemon residente | roadmap design ("no resident daemon", `docs/PANEL_CHAT.md`); memória observation-pays |
| Reuso integral de `processes.py` (pid_alive/tree-kill/group+NO_WINDOW) | roadmap precedents table; win-hidden-spawn-helper landed |
| Pidfile + log-handle pattern | async supervisor precedent (`async_runtime.py` pidfile/log) |
| Ponytail NÃO seedado: transporte stdio não compartilha entre sessões | roadmap risk #1 + ops-hygiene open decision #1 (owner) |
| Porta fixa declarada; conflito falha legível (sem auto-port) | roadmap risk #4 (P2+ idea) |
| Env de serviço de target = deny-by-default | `targets.spawn_env` (target-gate-env-filter round) |

## Test strategy

- Behaviors: real spawns on a temp root — idempotence + verified kill
  (svc-idempotent); probe timeout kills + no state (svc-ready-timeout);
  parent+child tree death (svc-orphan-free, child pid read from a file the
  service writes); dead-owner stop + dead-pid reap (svc-owner-reap); live CLI
  list/refusal (svc-cli, subprocess).
- Edge cases: stale pidfile restarts (covered by ensure's pid_alive gate);
  probe-less early exit raises; stop of a never-started service returns
  not-running.
- Regression net: `cli_registry.py` frozen surface; module self-check
  (`python scripts/harness_lib/services.py`) covers registry/probe logic
  without spawns.
- Coverage: deterministic, stdlib-only — `testing/scenarios/sv_services.py`.

## Validation

- `python testing/scenarios/sv_services.py` — svc-* all green.
- `python testing/scenarios/sao_autostart.py` — the v2 owner-lifecycle
  scenarios (sao-1..sao-3) green.
- `python scripts/harness_lib/services.py` — module self-check.
- `python testing/scenarios/cli_registry.py` — frozen surface intact.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.

## Amendments

### v2 (2026-07-13) — svc-autostart-owners (P1): owner-scoped lifecycles

`services.ensure_autostart(root, entry_point, target=None)` starts every
declared service whose `autoStart` names the entry point (never-crash: a
failing service reports and the owner still opens), and
`services.stop_owned(root, owner_pid=None)` stops exactly THIS owner's
services — the explicit counterpart of the `status()` reap, which remains the
safety net for hard kills. Wired owners:

- **panel** (`harness_ui.serve`): `autoStart:["ui"]` ensured after bind,
  `stop_owned` registered beside the existing sessions atexit;
- **chat REPL** (`chat_operator.run_chat`): `autoStart:["chat"]` ensured at
  session start, `stop_owned` at interpreter exit.

The **workflow(target)** owner hook stays a NAMED follow-up: it needs the
settle/collect stop counterpart to be leak-free, which lives in the async
runtime seam (svc-mcp-wiring territory) — not wired silently here.

```gherkin
Feature: owner-scoped service lifecycles (P1)

  Scenario: [sao-1] autostart starts only the entry point's services
    Given a registry with ui, manual and broken entries
    When ensure_autostart runs for ui and stop_owned runs after
    Then only the ui service starts, the broken one reports failed without
      raising, chat matches nothing, and this owner's service dies verified

  Scenario: [sao-2] stop_owned never touches another owner's service
    Given one service owned by a foreign pid and one by this process
    When stop_owned runs
    Then only this owner's service stops and the foreign one stays alive
      for the reap

  Scenario: [sao-3] the panel and chat owners are wired
    Given the server and REPL sources
    Then both ensure their autoStart scope and register stop_owned at exit
```

v2 scenarios resolve in `testing/scenarios/sao_autostart.py`.
