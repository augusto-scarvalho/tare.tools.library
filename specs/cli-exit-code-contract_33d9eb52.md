# CLI exit-code contract (`cec`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/cec_exit_codes.py).

Intake (SPEC-116 door NEW): spec-recovery rec-cli-1/2 — every scenario in the
treasury asserted the in-process `raise HarnessError`, never the subprocess
`returncode == 2` a real caller (CI, panel actions, other scripts) actually
sees; and argparse usage errors share code 2 with harness refusals with the
collision undocumented. This spec writes the contract down and pins it at the
subprocess level, where callers live.

## Goal

A caller shelling out to `python scripts/harness.py …` can rely on: rc 0 =
success (stdout machine-parseable, SPEC-102 closing block on stderr), rc 2 =
deliberate refusal or usage error (disambiguated by stderr shape), anything
else = a bug worth escalating, never a designed outcome.

## Applicability

Applies to `scripts/harness.py` `main()` (the `HarnessError → 2` handler and
the SPEC-102 `closing_block`), and argparse's own error path. Gates keep
their separate pass/fail rc contract (`spec_test_gate.py`: 0/1) — out of
scope here.

## Requirements / invariants (numbered, testable)

1. **Refusal contract.** A `HarnessError` exits the process with rc 2;
   stderr carries `harness error: <message>` (plus the fix line when the
   raiser provides one); the closing block (`-- ok:`) is suppressed —
   error output never claims success.
2. **Usage-error contract.** argparse errors (unknown verb, bad flag) also
   exit rc 2. The collision with (1) is INTENTIONAL — POSIX/argparse
   convention — and disambiguation is the stderr shape: `usage:` /
   `harness.py: error:` prefix, never `harness error:`. Callers needing the
   distinction parse the first stderr line, not the code.
3. **Success contract.** rc 0; stdout stays machine-parseable (JSON for
   `--json`/emit verbs); the SPEC-102 closing block (`-- ok: <verb>` +
   state + next) goes to stderr only.
4. **Everything else is a bug.** An unhandled exception (traceback, Python's
   default rc 1) is never a designed outcome — it is escalation material.
   (Prose invariant: exercised by the whole scenario treasury rather than a
   deliberate crash here.)

## Gherkin scenarios

```gherkin
Feature: CLI exit-code contract at the subprocess boundary

  Scenario: [cec-1] a harness refusal is rc 2 with the refusal shape
    Given a real subprocess running a verb that raises HarnessError
    Then returncode is 2, stderr starts with harness error: and carries the
      fix line, and no closing ok-block is printed

  Scenario: [cec-2] a usage error is rc 2 with the argparse shape
    Given a real subprocess running an unknown verb
    Then returncode is 2 and stderr carries usage: but never harness error:

  Scenario: [cec-3] success is rc 0 with parseable stdout
    Given a real subprocess running a JSON-emitting verb
    Then returncode is 0, stdout parses as JSON, and the closing ok-block
      rides on stderr
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Manter rc 2 compartilhado (refusal + usage) | convenção argparse/POSIX; mudar quebraria todo caller existente; a forma do stderr já é o discriminador |
| Pinar no nível subprocess | rec-cli-1: nenhum teste via subprocess existia; é onde CI/painel/scripts vivem |
| Closing block suprimido em erro (rec-cli-13) | `harness.py` main: bloco roda só no caminho rc 0 — output de erro nunca alega sucesso |
| Evidência | spec-recovery INDEX rec-cli-1/2/13; probe live 2026-07-13 (3 formas calibradas) |

## Test strategy

- Behaviors: as três formas no nível subprocess (cec-1..3).
- Edge cases: fix line presente na refusal; stdout de verbo JSON parseia.
- Regression net: cli_registry (superfície), cc_cli_catalog, spec-pack.
- Coverage: deterministic, stdlib-only — `testing/scenarios/cec_exit_codes.py`.

## Validation

- `python testing/scenarios/cec_exit_codes.py` — cec-1..cec-3 green.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.
