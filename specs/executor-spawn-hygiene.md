# Executor spawn hygiene — closed stdin + explicit model pinning (`esh`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/esh_spawn_hygiene.py).

Intake (SPEC-116 door NEW): request = "resolva esses problemas com o codex
antes... queria que você adicionasse ele ao nosso loop de implementação"
(owner, 2026-07-13). Two defects found while delegating the line-budget
burndown to codex: (1) `codex exec` under a background pipe blocked forever
on "Reading additional input from stdin..." — the harness spawn helpers let
children inherit the parent's stdin; (2) codex ≥0.144 ignores project-local
`.codex/config.toml` `profiles` keys, so the adapter's `--profile` pinning
silently no-op'd — a review-profile run intended as gpt-5.5/xhigh actually
ran the user's default (gpt-5.6-terra/medium). Covered-check: the
raw-subprocess-ratchet spec governs WHERE spawns happen (mediation layer),
not the stdin/pinning contract of the spawn itself. Decision: **NEW**.

## Goal

A worker spawned by the harness can never hang on an inherited stdin, and
the model/effort the routing layer chose is what the executor actually runs:
stdin defaults to DEVNULL (immediate EOF) at every mediation-layer spawn,
and the codex card pins `--model {model} -c model_reasoning_effort={effort}`
from the task-profile spawn mapping instead of relying on config profiles a
newer CLI ignores.

## Applicability

Applies to `harness_lib/processes.py` (`run_process_tree_bounded`,
`run_quiet`), the async supervisor spawn in `harness_lib/async_runtime.py`
(workers inherit the supervisor's stdio — DEVNULL there protects the chain),
and the `codex` card in `.harness/routing/executors.json`. Explicit caller
kwargs always win (`setdefault`); `input=` still routes through a real PIPE.

## Requirements / invariants (numbered, testable)

1. **No inherited stdin.** A spawn through `run_process_tree_bounded` or
   `run_quiet` without `input=` gets `stdin=DEVNULL`: a stdin-reading child
   sees EOF immediately and completes even while the harness's own stdin is
   an open pipe with no EOF.
2. **`input=` unaffected.** Passing `input=` still feeds the child through a
   PIPE that closes after write; explicit `stdin=` kwargs are respected.
3. **The supervisor closes the chain.** The async-supervisor Popen sets
   `stdin=DEVNULL` explicitly — every workflow worker below it inherits a
   closed stdin, not the panel/service pipe that launched the runtime.
4. **Codex model pinning is CLI-explicit.** The codex commandTemplate
   carries `--model {model}` and `-c model_reasoning_effort={effort}`
   (values from the task-profile spawn mapping via SPEC-115 routing) and no
   longer passes `--profile` — codex ≥0.144 ignores project-local profiles,
   and a pin that can silently no-op is not a pin.

## Gherkin scenarios

```gherkin
Feature: executor spawn hygiene

  Scenario: [esh-1] a stdin-reading child cannot hang the bounded spawn
    Given a parent process whose stdin is an open pipe with no EOF
    When it spawns a stdin-reading child through run_process_tree_bounded
    Then the child reads EOF immediately and the tree completes fast

  Scenario: [esh-2] run_quiet shares the hygiene and input= still works
    Given the same open-stdin parent using run_quiet
    And direct spawns passing input= through both helpers
    Then the quiet child completes fast and the input reaches the children

  Scenario: [esh-3] the supervisor spawn pins DEVNULL for the whole chain
    Given the async runtime source
    Then the supervisor Popen sets stdin=DEVNULL explicitly

  Scenario: [esh-4] the codex card pins model and effort on the CLI
    Given the executors registry and the live spawn-command renderer
    Then the codex template carries --model and model_reasoning_effort=
      and no --profile flag, and the rendered command shows the routed values
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| DEVNULL como default no seam, não por-caller | ponytail root-cause: um guard onde TODOS os spawns passam; o hang reproduziu no launch manual E ameaçava o runtime async |
| `setdefault` (caller explícito vence) | chat/stream paths que escrevem stdin de propósito continuam donos do fd |
| Pinning via `--model` + `-c model_reasoning_effort=` | codex v0.144.1: "Ignored unsupported project-local config keys: profiles"; `--profile` agora resolve em $CODEX_HOME/<name>.config.toml (mecanismo novo, user-scope) |
| `.codex/config.toml` [profiles] vira documentação | valores canônicos já moram em task-profiles.json spawn mappings; duplicar contrato executável em dois lugares foi a causa do no-op silencioso |
| Smoke real fora do gate | provado 1× no fix (gpt-5.5/low header + 6.6s wall); o gate não gasta tokens de vendor |

## Test strategy

- Behaviors: open-pipe parent → fast completion (esh-1, esh-2); input=
  round-trip (esh-2); supervisor literal (esh-3); template + live render
  (esh-4).
- Edge cases: wrapper deadline chosen so a regression (child blocking on the
  inner 30s timeout) fails the check, not the suite.
- Regression net: spec-pack (raw-subprocess-ratchet unchanged — no new
  unmediated sites), mr_model_routing (spawn routing), workflow gate.
- Coverage: deterministic, stdlib-only, no vendor tokens —
  `testing/scenarios/esh_spawn_hygiene.py`.

## Validation

- `python testing/scenarios/esh_spawn_hygiene.py` — esh-1..esh-4 green.
- One-time real-binary smoke (documented above, not in the gate): codex
  header shows the pinned model/effort; wall seconds, not timeout.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.
