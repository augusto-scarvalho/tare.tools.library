# SPEC-132 — workflow CLI tree extracted to `harness_lib/cli_workflow_tree.py`

Status: proposed 2026-07-12 (acceptance: testing/scenarios/wt_workflow_tree.py).

Intake (SPEC-116 door NEW, from specs/templates/intake-refinement.md): request =
"move the `workflow` subcommand tree (the last parser mass pinned in
scripts/harness.py) to a harness_lib home, VERBATIM, changing nothing
behavioral" (workflow-block r2, P1, harness-lines burndown). Covered-check:
MF.1-r2 already moved the NON-workflow verbs to `cli_registry.py`; the
workflow tree stayed inline only because the `workflow-command-surface` gate
regex scanned harness.py alone. Decision: **NEW** (the regex widens; the tree
moves). Surface is CLI-internal refactoring — the command set, help text, and
handlers do not change.

## Goal

`scripts/harness.py` stops being the CLI bottleneck: every
`wsub.add_parser(...)` line of the `workflow` subcommand tree lives in
`scripts/harness_lib/cli_workflow_tree.py`, moved byte-identical (order
preserved, help output golden-pinned), while harness.py keeps the `workflow`
parent parser, every `cmd_workflow_*` handler function, and dispatch. Adding a
future workflow subcommand is one line in cli_workflow_tree.py plus its
handler — zero parser edits in harness.py.

## Applicability

Applies to `scripts/harness_lib/cli_workflow_tree.py` (`register(wsub, h)`),
the one `cli_workflow_tree.register(wsub, sys.modules[__name__])` call in
harness.py's main(), and the `workflow-command-surface` check in
`scripts/spec_test_gate.py` (its scanned text widens from harness.py-only to
harness.py + cli_workflow_tree.py). Does NOT move the `cmd_workflow_*`
handlers, does not change `.harness/project.json` (the command SET is
unchanged), and does not touch `cli_registry.py`.

## Requirements / invariants (numbered, testable)

1. **Verbatim move.** Every `wsub.add_parser` line registers in
   `cli_workflow_tree.register(wsub, h)` in the same order as the original
   main() block; handlers resolve as `h.cmd_workflow_*`; `AWAIT_MODES`
   resolves via `h`; `observability_exporters` constants import from their
   harness_lib home. `workflow <cmd> --help` is byte-identical for every
   command and the `workflow` parent.
2. **Full-surface gate.** The `workflow-command-surface` check compares the
   union of `wsub.add_parser` name literals across harness.py AND
   cli_workflow_tree.py against project.json's
   `supportedWorkflowCommands` + `internalWorkflowCommands` — both
   directions still fail on drift.
3. **Handlers stay home.** `cmd_workflow_*` functions, the modular-boundary
   literals (`allocate_workflow_id`, `workflow_state_lib.summary`,
   `handoff_lib.generate_handoff`) and dispatch remain in harness.py;
   `harness-modular-boundary` stays green.
4. **No circular import.** cli_workflow_tree never imports harness; the
   runtime module arrives as the `h` parameter (the cli_registry pattern).
5. **Mass actually moved.** harness.py contains zero `wsub.add_parser` lines
   and its line count dropped below the pre-move 3235.

## Gherkin scenarios

```gherkin
Feature: workflow CLI tree module

  Scenario: [wt-1] registered command set equals the declared set
    Given cli_workflow_tree.py's wsub.add_parser name literals
    When compared against project.json supported + internal workflow commands
    Then the two sets are equal in both directions

  Scenario: [wt-2] moved parsers still answer --help through the real CLI
    Given this repository
    When "workflow plan --help" and "workflow evidence --help" run
    Then both exit 0

  Scenario: [wt-3] harness.py shed the parser mass
    Given scripts/harness.py after the move
    When scanned for wsub.add_parser and its line count measured
    Then no wsub.add_parser line exists and the count is below 3235
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Mover só o wiring, handlers ficam | brief workflow-block r2; literais de fronteira `allocate_workflow_id`/`workflow_state_lib.summary`/`handoff_lib.generate_handoff` são pinados em harness.py pelo `harness-modular-boundary` (spec_test_gate.py) |
| `register(wsub, h)` sem importar harness | receita MF.1-r2 provada em `cli_registry.py` (sem import circular) |
| Gate escaneia harness.py + cli_workflow_tree.py concatenados | `workflow-command-surface` deve continuar comparando o conjunto COMPLETO vs project.json; regex `wsub\.add_parser\("([^"]+)"` inalterada |
| project.json intocado | o SET de comandos não muda; só o arquivo-fonte dos literais |
| Help byte-idêntico como prova | fixture cli-golden + diff pré/pós de todos os 44 `workflow <cmd> --help` |

## Test strategy

- Behaviors: set-equality CLI↔config nas duas direções (wt-1); `--help` rc 0
  via subprocess pelo router real (wt-2); ausência de `wsub.add_parser` +
  queda de linhas em harness.py (wt-3).
- Edge cases: docstrings não podem conter `wsub.add_parser("` seguido de nome
  falso (o regex do gate as escanearia); ordem de registro preservada garante
  `workflow --help` byte-idêntico.
- Regression net: fixture cli-golden (contrato público), checks
  `workflow-command-surface`, `harness-modular-boundary`,
  `workflow-doc-runtime-consistency`.
- Coverage: deterministic, stdlib-only, no LLM —
  `testing/scenarios/wt_workflow_tree.py`.

## Validation

- `python testing/scenarios/wt_workflow_tree.py` — wt-1/wt-2/wt-3 all green.
- `python scripts/spec_test_gate.py smoke` and `spec-pack` — template
  conformance + `workflow-command-surface` + `harness-modular-boundary` +
  cli-golden fixture green.
