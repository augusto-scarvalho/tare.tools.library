# Workflow rollback restores data (`wfrb`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/wfrb_rollback_restore.py).

Intake (SPEC-116 door NEW): spec-recovery rec-wf-12 — the highest-risk gap of
the archaeology round: `workflow_writes.workflow_rollback` replays each
worker's `__actions.json` journal in reverse (create→remove, modify/delete→
restore from backup, rename→reverse) and NO spec documented the contract and
NO scenario ever executed the data-restore path. A silent regression here is
a data-loss surface: rollback runs exactly when a gate already failed — the
worst moment to discover the safety net has a hole.

## Goal

The reverse-replay contract is written and permanently exercised: after a
rollback, modified and deleted files carry their original bytes, created
files are gone, renames are reversed, the rollback result artifact and event
are emitted, and degenerate states (no backups, double rollback, legacy
backup layout) stay calm.

## Applicability

Applies to `workflow_writes.workflow_rollback` (whole-workflow and
`worker_id`-scoped) and the harness-bound helpers it replays through
(`restore_backup_file` with the `before/<relpath>` layout, `remove_path`).
Scenario coverage is hermetic via the module's `bind()` seam (test-local
ROOT; the real repo is never touched).

## Requirements / invariants (numbered, testable)

1. **Reverse replay restores bytes.** modify → original content restored from
   backup; delete → file restored; create → file removed; rename → old path
   restored (when `hadOld`) and the new path removed (when not `hadNew`).
2. **Scoped rollback.** `worker_id=` limits the replay to that worker's
   backup dir; other workers' journals are untouched.
3. **Evidence emitted.** `reduce/rollback-result.json` is written with
   `restored`/`removedCreated` lists and a `workflow_rollback` event fires.
4. **Calm degradation.** Missing backups dir returns the no-backups message;
   a second rollback is a calm no-op for already-reversed creates; a legacy
   backup dir without `__actions.json` still restores via the recursive copy.

## Gherkin scenarios

```gherkin
Feature: workflow rollback data restore

  Scenario: [wfrb-1] the journal replays in reverse and restores bytes
    Given a worker journal with create, modify, delete and rename actions and
      their before/ backups
    When workflow_rollback runs
    Then original bytes are back, created and renamed-new files are gone, and
      the result artifact and event are emitted

  Scenario: [wfrb-2] scoped rollback and the legacy layout both restore
    Given a second worker with a legacy backup dir (no journal)
    When rollback runs scoped to worker one, then unscoped
    Then the legacy worker's files are only restored by the unscoped run

  Scenario: [wfrb-3] degenerate states stay calm
    Given no backups dir, then an already-rolled-back workflow
    When rollback runs in each state
    Then it reports no-backups calmly and the double rollback does not crash
      or corrupt restored content
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Cenário hermético via bind() com ROOT de teste | rollback escreve em `ROOT/...`; o seam já existe (MF discipline) e os cenários dual-subject usam o mesmo truque |
| Cobrir o layout legacy (rglob before/) | branch vivo em `workflow_writes.py:440-450`; backups antigos existem em árvores reais |
| Porta NEW (não amendment) | nenhuma spec existente documenta o contrato de rollback (rec-wf-12: "no spec, no scenario") |
| Evidência | spec-recovery INDEX rec-wf-12; código `workflow_writes.py:398-455` |

## Test strategy

- Behaviors: byte-level restore nas 4 classes de ação (wfrb-1); escopo por
  worker + legacy (wfrb-2); no-backups + rollback duplo (wfrb-3).
- Edge cases: rename com `hadOld`/`hadNew`; create cujo arquivo já sumiu.
- Regression net: gate_fixtures_workflow (merge/apply fixtures), spec-pack.
- Coverage: deterministic, stdlib-only, temp roots —
  `testing/scenarios/wfrb_rollback_restore.py`.

## Validation

- `python testing/scenarios/wfrb_rollback_restore.py` — wfrb-1..wfrb-3 green.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.
