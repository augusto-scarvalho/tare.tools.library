# wf-regen-manifest — the declared regen contract

SPEC-116 door NEW, 2026-07-20. From research round `docs/research/gate-phase2-safety-round.md`
(concept C6, 2/2 ideator convergence) after the 2026-07-20 audit's rt6 forensics.

## Goal

Scenarios that drive the REAL harness machinery while asserting working-tree
cleanliness (the rt6 class) previously discovered which files the harness
regenerates by archaeology — a hardcoded exclusion set that rots silently the
day a writer gains a new target. This feature makes the regen set a DECLARED,
gate-defended contract: `harness_lib.regen_manifest.REGEN_PATHS` is the single
source of truth, scenarios import it, and an acceptance scenario proves the
declaration matches real writer behavior BOTH ways.

## Applicability

- Producers: `workflow_lifecycle.update_context_from_workflow` (NEXT_STEPS +
  workflow/task state), `harness.generate_handoff` (handoff.json/md +
  next-agent-prompt), `validation_stamp.stamp_staged`/`stamp_reckon`
  (quality-state).
- Consumers: `testing/scenarios/rt6_route_writechain.py` (porcelain-delta
  exclusions) and any future machinery-driving scenario.
- Out of scope: class-D runtime sidecars (`.harness/runs/**`,
  `.harness/workflows/**`, `.harness/state-store/**`) and per-target scopes
  (`.harness/state/targets/**`) — `scenario_isolation._targets` owns those at
  dir granularity (a complementary, coarser net).

## Requirements / invariants (numbered, testable)

1. `REGEN_PATHS` is a flat tuple of repo-relative POSIX paths; unique entries;
   `porcelain_exclusions()` returns it as a frozenset.
2. **Writes ⊆ manifest:** driving the finalize-regen pair + the validation stamp
   on a redirected tmp tree creates no non-runtime file outside `REGEN_PATHS`.
3. **Manifest ⊆ writers:** every `REGEN_PATHS` entry is produced by those real
   writers — a dead entry fails the scenario.
4. `is_runtime()` classifies class-D prefixes (both separators) and never
   matches a declared doc path.
5. rt6 consumes `porcelain_exclusions()` — no scenario-local hardcoded regen
   set survives.
6. The contract is code (a python constant versioned with the writers), not a
   generated file: no JSON export until a non-python consumer exists
   (simplificada vs the research's manifest-file proposal; recorded in D036).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Declared registry over per-scenario archaeology | research round C6 (2/2 ideators: worker-001 THEME3, worker-002 P4); rt6 audit forensics 2026-07-20 |
| Python constant, not regen-manifest.json | ponytail rung 6 + D036 (one source of truth, atomically versioned; a JSON file adds a sync surface with its own drift check) |
| Both-ways gate defense | research C6 recommendation: "diff actual-writes vs manifest"; rm-1/rm-2 implement it over the hsc redirect pattern |
| Runtime prefixes excluded | scenario_isolation dir-granularity snapshot already owns class-D state |

## Gherkin scenarios (UI surfaces only)

```gherkin
Scenario: [rm-1] every machinery write is declared
  Given the finalize-regen pair and the validation stamp run on a redirected tmp tree
  When the created non-runtime files are diffed against REGEN_PATHS
  Then no undeclared write exists

Scenario: [rm-2] every declared path has a real writer
  Given the same driven writers
  When REGEN_PATHS is diffed against the created files
  Then no dead manifest entry exists

Scenario: [rm-3] the rt6 cleanliness check imports the contract
  Given testing/scenarios/rt6_route_writechain.py
  When its source is inspected
  Then it imports regen_manifest and carries no hardcoded exclusion set
```

## Test strategy

- Acceptance: `testing/scenarios/rm_regen_manifest.py` (rm-1..rm-3) — hermetic,
  repo read-only, drives the REAL writers via the hsc path-redirect pattern.
- Module self-check: `python scripts/harness_lib/regen_manifest.py`.
- Integration: rt6 itself runs in the battery with the imported exclusions.

## Validation

- `python scripts/harness_lib/regen_manifest.py` → self-check OK.
- `python testing/scenarios/rm_regen_manifest.py` → 3/3.
- Scenarios gate green with rt6 consuming the manifest.

## Ceilings (upgrade paths)

- A writer gaining a CONDITIONAL target that the rm drivers do not exercise
  would pass rm-1 (write absent in the fixture run) — extend `_drive_writers`
  when a new writer mode ships; rm-2 catches the inverse.
- JSON export for non-python consumers: add only on demand.
- Per-entry metadata (owner/trigger/stabilityClass, the research's richer
  registry): add when a consumer needs it, not before.

## Amendments

(none)
