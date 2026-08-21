# Cross-project isolation audit — dual-subject gate (`isolation-audit-gate`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/ia_isolation_audit.py).

Intake (SPEC-116 door NEW): request = "auditar se ARQUIVOS, DIFFS, dados não
estão vazando de um projeto pra outro que o harness está operando… Cada um deve
ter seu MUNDO e VISÃO" (isolation round,
`docs/roadmap/cross-project-isolation-data.md` Phase 0). Covered-check: the
enforcement pieces landed one by one (target-gate-env-filter,
records-subject-dimension, workspace-state-exclusion, esc-subject-scope) but
NOTHING asserts the invariant end-to-end — no gate builds two subjects and
proves no bleed. Decision: **NEW**. SLICE: the deterministic AUDIT gate only —
per-target-token-calibration, subject-tagged-events and target-worker-world
stay OPEN in the backlog (the fixture names the calibration gap observe-only).

## Goal

One deterministic, dual-subject gate fixture that proves — with two real
throwaway git targets and A's real target-gate run — that the isolation
invariant holds from the outside: sibling trees untouched, no cross-subject
tokens/paths in harness-side artifacts, the env filter live, records credited
to their subject; and that the one remaining audited gap stays NAMED in every
run instead of silently forgotten.

## Applicability

Applies to `scripts/harness_lib/gate_fixtures_isolation.py`
(`check_isolation_audit_fixture`, bind idiom) and its registration in
`scripts/spec_test_gate.py` (`WORKFLOW_FIXTURE_FUNCTIONS["isolation-audit"]`,
run inside the `workflow` gate list and standalone via
`--fixture isolation-audit`). The fixture registers targets
`iso-fixture-a`/`iso-fixture-b` via the real single write path
(`targets.register`) and removes every trace of them in `finally`. No
production seam changes.

## Requirements / invariants (numbered, testable)

1. **Real flows, not mocks.** The fixture runs `gate_generic.run_target_gate`
   over two real temp git repos registered through `targets.register`; probes
   ride the target's own `validation.smoke.commands`.
2. **Sibling cleanliness.** After A's gate, B's `git status --porcelain` is
   empty and B's file list is unchanged (`b-tree-clean`).
3. **No artifact cross-bleed.** After both gates, neither subject's
   `graphify-out/targets/<n>/` nor `.harness/state/targets/<n>/` contains the
   OTHER subject's sentinel token or root path (`cross-bleed`).
4. **Env filter proven live.** A canary var exported in the harness process is
   invisible to the target's own gate command (`env-canary` — the
   target-gate-env-filter regression probe).
5. **Records credited.** `records.add_entry(root, …, subject=<target>)`
   stores the subject structurally (`records-credit`, temp harness root).
6. **Known gap stays named.** `calibration-scope` is an observe-only pass row
   whose detail names the global charsPerToken override and points at the OPEN
   `per-target-token-calibration` backlog row — the audit documents what it
   does NOT yet enforce.
7. **Self-cleaning.** The fixture deletes its registrations, per-target state,
   graph outputs, temp repos and the canary env var in `finally`; a crashed
   prior run is cleaned at entry.

## Gherkin scenarios

```gherkin
Feature: dual-subject isolation audit gate

  Scenario: [iso-01] no cross-subject bleed in harness-side artifacts
    Given two registered temp targets with unique sentinel tokens
    When both targets' gates run
    Then neither subject's artifact dirs contain the other's token or root path

  Scenario: [iso-02] a sibling target's tree is untouched by another's flow
    Given target B's file list and git status snapshotted
    When target A's gate runs
    Then B's porcelain stays empty and its file list is unchanged

  Scenario: [iso-03] the env canary is invisible to target commands
    Given a canary variable exported in the harness process
    When the target's own validation command inspects its environment
    Then the command prints ENVCLEAN and passes

  Scenario: [iso-04] records written during target work carry their subject
    Given a temp harness root
    When add_entry runs with subject=iso-fixture-a
    Then the stored entry and worklog carry that subject structurally

  Scenario: [iso-05] the remaining calibration gap is named on every run
    Given the audit fixture
    When it reports
    Then calibration-scope passes observe-only and its detail names the OPEN
      per-target-token-calibration row
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Auditoria dual-subject com repos reais, não mocks | roadmap Phase 0 (`cross-project-isolation-data.md:78-93`); "adversarial assumption: data WANTS to leak" |
| Probes viram xfail→hard conforme as fases aterrissam — env e records já são HARD | `gate_generic.run_target_commands` filter_spawn_env (target-gate-env-filter, landed); `records.add_entry(subject=)` (records-subject-dimension, landed) |
| Gap restante vira linha observe-only NOMEADA, nunca omitida | honest-labeling (CQ round); slice discipline do backlog |
| Fixture no gate `workflow` + standalone `--fixture` | fixture families precedent (`gate_fixtures_workflow/trace/graphify`, MF.2 bind idiom) |
| Cleanup fail-safe (entry + finally) | fixtures precedent (`cleanup_test_artifacts`); OneDrive rmtree lessons (`common.rmtree_robust`) |

## Test strategy

- Behaviors: the five fixture rows above, driven end-to-end by the scenario
  through `WORKFLOW_FIXTURE_FUNCTIONS["isolation-audit"]` (iso-01..iso-05 map
  1:1 to fixture row names).
- Edge cases: a crashed prior run leaves stale registrations → cleaned at
  entry; a fixture exception yields one failing `isolation-audit:fixture` row,
  never a crash; temp repos live under the system temp dir (never the repo).
- Regression net: `ht_targets` scenario (registration path),
  `cli_registry`/gate suites unchanged; the fixture is additive.
- Coverage: deterministic, stdlib-only, no LLM —
  `testing/scenarios/ia_isolation_audit.py`.

## Validation

- `python testing/scenarios/ia_isolation_audit.py` — iso-01..iso-05 green.
- `python testing/scenarios/ste_subject_events.py` — the v3 subject-tagged
  log scenarios (ste-1..ste-3) green.
- `python scripts/spec_test_gate.py --fixture isolation-audit` — standalone run.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity (the workflow gate carries the
  fixture in its fixed list).

## Amendments

### v2 (2026-07-13) — per-target-token-calibration: the last audited gap closes

`token_calibration` gained a per-subject dimension: a target's learned
charsPerToken lives under `state_dir(<target>)/token-calibration.json`
(`read_override`/`write_override` `subject=` param; None/"self" keeps every
existing caller byte-unchanged), workflow budget sizing prefers the
workflow's OWN subject value (cascade target → harness → seed) at the one
call site where the workflow is in scope, and `summarize().estimator` gains
`byTargetCpt` — per-subject observed CPT, report-only, the feed a future
per-target recalibration WRITER would consume (that writer stays OPEN; no
auto-recalibration per target yet).

The `calibration-scope` fixture row is therefore no longer observe-only: it
now WRITES a calibration for one fixture target and FAILS unless the value
resolves per-subject with the harness's own file (and the sibling target)
byte-untouched. Invariant 6 (named observe-only gap) is superseded — the gap
is closed and enforced; iso-05's wording moves with it in the same commit.

### v3 (2026-07-13) — subject-tagged-events: logs get worlds (Phase 4)

Every `append_event` row now carries a structural `subject` field with the
documented precedence — explicit param > a `target` the payload already
carries > `"self"` — so harness-work and target-work events are
distinguishable without payload archaeology. The harness validation-run
writer stamps `subject: "self"` (structural: a `--target` run never reaches
it — it returns earlier through `run_target_gate`), and `run_target_gate`
stamps `subject: <name>` on every result row it persists, replacing the
check-name-prefix convention with a field. Pooled-but-attributed stays the
design (per-subject FILES remain deferred until a consumer needs them, per
the roadmap).

```gherkin
Feature: subject-tagged events and validation rows (phase 4)

  Scenario: [ste-1] every event row is subject-attributable by precedence
    Given events appended bare, with a payload target, and with an explicit
      subject param
    When the rows land
    Then their subjects are self, the payload target, and the param winner

  Scenario: [ste-2] harness validation runs stamp self structurally
    Given the gate's RUNS writer
    Then its row shape carries subject self

  Scenario: [ste-3] target gate rows carry their subject as a field
    Given a registered temp target
    When its gate runs
    Then every persisted result row carries subject = the target name
```

v3 scenarios resolve in `testing/scenarios/ste_subject_events.py`.
