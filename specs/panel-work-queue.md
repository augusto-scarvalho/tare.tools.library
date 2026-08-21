# Panel work queue — B0 live view (`queue-view-live`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/wq_queue_view.py).

Intake (SPEC-116 door NEW): request = "fila de trabalho atual: tasks que o
harness está trabalhando, em tempo real, em que parte do processo de trabalho
está" (`docs/roadmap/screens-tasks-queue.md` Screen B, phase B0).
Covered-check: live work today is the small Agents strip on the Painel + CLI
`workflow watch/tail` — no queue-level view exists. Decision: **NEW**. SLICE:
B0 read-only view ONLY — `queue-cancel-worker` (B1), `queue-reorder` (B2) and
`queue-start-action` (B3, decision #1 approved) stay OPEN in the backlog.

## Goal

One live panel view (`▶ Queue`, 3s poll while visible) showing every active
workflow — id, phase label, task, target scope, per-status counts — and one
row per worker with a STAGE chip. Honest labeling: the stage is the declared
`taskProfile` (scan→research, plan→refining, implementation→coding,
debug→debugging, review/security→reviewing, docs→documenting), not observed
activity, and the view says so. Derived per poll; nothing stored.

## Applicability

Applies to `scripts/harness_lib/ui_queue.py` (`queue_snapshot(root)`,
`stage_label`), the `GET /api/queue` route (`harness_ui.py`) and the
`viewQueue` PAGE section (visible-only 3s interval). CLI parity is the
EXISTING `workflow list` / `workflow async-status` verbs — no new verb. GUI
writes no canonical state; no SSE/streaming (panels categorize, never stream).

## Requirements / invariants (numbered, testable)

1. **Derived per poll.** `queue_snapshot` performs pure reads over
   `.harness/workflows/active/*/workflow.json`; per-status counts and stage
   labels are recomputed every call; nothing is written or cached.
2. **Stage = declared profile, said honestly.** `stage_label` maps the
   taskProfile vocabulary to EN stage labels; an unknown profile passes
   through verbatim; the view's header names the chip as the declared
   profile.
3. **Phase labels.** `planned/running_workers/awaiting_reduce/reducing/
   finalized` map to `planned/running/consolidating/finalized`; unknown
   phases pass through.
4. **Never-crash collector.** A corrupt `workflow.json` skips that workflow;
   a missing active dir yields an empty snapshot; task text is truncated.
5. **Live only while visible.** The PAGE polls `/api/queue` every 3s ONLY
   while the Queue view is selected (interval cleared on switch-away) — no
   background polling, no render-loop LLM, no push.
6. **Target scope carried structurally.** A workflow's `target` renders as a
   distinct scope chip; scope is never inferred from text.

## Gherkin scenarios

```gherkin
Feature: live work-queue view (B0)

  Scenario: [wq-1] an active workflow derives phase, counts and stage chips
    Given a WF with awaiting_reduce phase, a target, and three workers across
      profiles and statuses
    When queue_snapshot runs
    Then the phase label is consolidating, counts group by status, the task
      truncates and each worker carries its EN stage label (unknown profile
      passes through)

  Scenario: [wq-2] garbage never crashes the queue
    Given a corrupt workflow.json beside a valid one and a missing active dir
    When queue_snapshot runs on each
    Then the corrupt workflow is skipped and the missing dir yields empty

  Scenario: [wq-3] the panel is wired with a visible-only poll
    Given the server and page sources
    Then /api/queue routes to the collector and the PAGE carries
      navQueue/viewQueue/loadQueue with a 3s interval cleared on view switch
      and the honest profile labeling
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Derivar por poll, nunca armazenar; 3s só com a view visível | roadmap B0 (`screens-tasks-queue.md`); "panels categorize, never stream" |
| Stage chip = perfil declarado, rotulado honestamente | roadmap risk #4 (honest labeling); vocabulário `tasks/TASK_TEMPLATE.md` |
| Novo módulo `ui_queue.py` em vez de `ui_panel.py` | ui_panel.py acima do budget de 900 linhas (inbox finding) |
| CLI parity = verbos existentes, sem alias novo | ladder rung 2 (`workflow list`/`async-status` já cobrem) |
| Cancel/reorder/start ficam fora | fatias B1/B2/B3 abertas; B3 tem spawn-por-clique (decisão #1) com trilha própria |

## Test strategy

- Behaviors: full derivation on a fabricated WF (wq-1); corrupt/missing
  tolerance (wq-2); route + view + poll-lifecycle wiring asserts (wq-3).
- Edge cases: unknown profile/phase pass through; workers without ids render
  "?"; empty active dir.
- Regression net: `m5_ui_panel.py` (panel untouched behaviors) + ui_e2e rc0;
  module self-check (`python scripts/harness_lib/ui_queue.py`).
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/wq_queue_view.py`.

## Validation

- `python testing/scenarios/wq_queue_view.py` — wq-1..wq-3 green.
- `python testing/scenarios/qcw_cancel_worker.py` — the v2 per-worker cancel
  scenarios (qcw-1..qcw-3) green.
- `python scripts/harness_lib/ui_queue.py` — module self-check.
- `python testing/scenarios/m5_ui_panel.py` + ui_e2e rc0 — panel regression net.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.

## Amendments

### v2 (2026-07-13) — queue-cancel-worker (B1): per-worker cancel

The `workflow-cancel` action builder gains an OPTIONAL `workerId`, mapping to
the existing CLI `workflow cancel <wf> --worker-id <id>` — whole-WF cancel is
byte-unchanged. The recovery gate (`_recovery_reason`) already regex-validates
any present `workerId` BEFORE the builder runs, so a `--force`-shaped
injection never reaches argv. The Queue view renders a per-row ✕ on
pending/queued/running workers → confirm dialog naming the exact command →
the same recovery-gated `/api/action` path. Reorder (B2) and start (B3) stay
OPEN.

```gherkin
Feature: per-worker cancel from the queue view (B1)

  Scenario: [qcw-1] the cancel builder narrows to one worker when asked
    Given the workflow-cancel action builder
    When built with and without a workerId
    Then the scoped argv carries --worker-id and the bare shape is unchanged

  Scenario: [qcw-2] a hostile workerId is refused before argv
    Given the recovery gate over a real active workflow fixture
    When the params carry a --force-shaped workerId
    Then the gate returns a refusal reason and the builder never runs

  Scenario: [qcw-3] the queue view wires the per-row cancel
    Given the page source
    Then pending/queued/running rows carry the cancel button posting the
      recovery-gated action with the row's ids and a confirm dialog
```

v2 scenarios resolve in `testing/scenarios/qcw_cancel_worker.py`.
