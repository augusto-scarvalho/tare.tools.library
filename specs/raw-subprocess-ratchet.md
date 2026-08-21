# Raw-subprocess ratchet — no new unmediated spawn sites (`no-raw-subprocess-gate`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/srg_spawn_ratchet.py).

Intake (SPEC-116 door NEW): request = "gate forbidding raw `subprocess.*`/
`create_subprocess_exec` outside `processes.py`"
(`docs/roadmap/black-terminal-windows.md`). Covered-check: `processes.py` is
the mediation layer (hidden consoles, bounded timeouts, tree-kill) but ~48
legacy call sites bypass it and nothing stops a 49th — the black-terminal
incident came from exactly one such site. Decision: **NEW**. Honest posture:
a RATCHET (baseline today, block growth), not a purge.

## Goal

A new unmediated `subprocess.*` / `asyncio.create_subprocess_*` call site
under `scripts/` fails the gate with a route-or-rebaseline fix line; the
legacy sites are baselined write-once (day-one green) and burn down on their
own schedule.

## Applicability

Applies to `scripts/harness_lib/spawn_ratchet.py` (`findings`, `evaluate`),
the gitignored write-once snapshot `.harness/state/raw-subprocess-baseline.json`
(seeded: 28 (kind, file) sites) and one enforcing gate check
(`raw-subprocess-ratchet`) in `spec_test_gate.main()`. `processes.py` itself
is exempt (it IS the mediation layer). No runtime behavior changes.

## Requirements / invariants (numbered, testable)

1. **AST scan, (kind, file) granularity.** Finding ids are
   `spawn:<kind>:<rel>` — `subprocess.{run,Popen,call,check_call,check_output}`
   and `asyncio.create_subprocess_{exec,shell}` attribute calls; moving lines
   inside a file never creates a new finding; a new kind in a file, or a
   first site in a new file, does.
2. **Mediation layer exempt.** `scripts/harness_lib/processes.py` never
   contributes findings.
3. **Write-once baseline.** The first evaluate records ALL findings and
   returns `new == []`; later runs report only findings absent from the
   snapshot (the security-baseline snapshot idiom, same escape hatch: delete
   the snapshot to consciously re-baseline).
4. **Enforcing check.** `raw-subprocess-ratchet` fails on any new finding,
   naming the sites and the fix (route through `processes.py` helpers, or
   re-baseline); a clean run reports the baselined count.

## Gherkin scenarios

```gherkin
Feature: raw-subprocess spawn ratchet

  Scenario: [srg-1] the scan finds spawn sites and exempts the mediation layer
    Given a tree with subprocess and asyncio spawn calls plus processes.py
    When the scan runs
    Then both call sites surface with kind+file ids and processes.py does not

  Scenario: [srg-2] the baseline ratchets on new files and kinds only
    Given a day-one baseline
    When a second call lands in the same file and then a new file appears
    Then the same-file call is not new and the new file is

  Scenario: [srg-3] the live repo is baselined and the gate enforces
    Given this repository's seeded snapshot
    When evaluate runs and the gate source is inspected
    Then there are no new sites and the enforcing check carries the
      route-or-rebaseline fix line
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Ratchet com baseline write-once, não purge | SEC.5 audit (~48 sites legados); security-baseline snapshot precedent |
| Granularidade (kind, file), nunca lineno | `security_baseline._sink_findings` ponytail note (linha inserida ≠ finding novo) |
| `processes.py` isento | é a camada de mediação (CREATE_NO_WINDOW/timeout/tree-kill vivem lá) |
| Escape hatch = deletar snapshot conscientemente | mesmo contrato do security-baseline; re-baseline é diff-visível |

## Test strategy

- Behaviors: scan + exemption (srg-1); same-file tolerance + new-file/kind
  detection (srg-2); live baselined state + gate wiring (srg-3).
- Edge cases: unparsable .py skipped; missing scripts/ dir → empty; alias
  imports of asyncio still match by attribute name.
- Regression net: the enforcing check runs on every gate; module self-check.
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/srg_spawn_ratchet.py`.

## Validation

- `python testing/scenarios/srg_spawn_ratchet.py` — srg-1..srg-3 green.
- `python scripts/harness_lib/spawn_ratchet.py` — module self-check.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` — the
  enforcing check green on the seeded baseline.
