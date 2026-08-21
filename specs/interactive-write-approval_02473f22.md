# Interactive per-item write approval (`iwa`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/iwa_interactive_apply.py).

Intake (SPEC-116 door NEW): plan-mined P-2, owner decision "construir agora"
(2026-07-13). The controlled-write track approves INTENT up front
(`--approval-token` at plan/prepare, before any diff exists) and had no
content-level gate: the riskiest track carried the coarsest approval.
Promised in `SUPERVISION_UI_IDEATION.md §5`, never landed, escaped every
tracking surface until phase-3 archaeology.

## Goal

`workflow apply-merge --interactive` steps the operator through EVERY planned
operation — diff preview for modifies, head for creates, explicit
delete/rename descriptors — collecting y/n/all/quit decisions in a first
phase that touches nothing; only the approved subset enters the existing
apply machinery (backups, gates, rollback all unchanged). Denials are
recorded, aborts apply nothing.

## Applicability

Applies to `workflow_writes.collect_interactive_decisions`, `_op_preview`,
`_tty_decider` and the `interactive=`/`decider=` parameters of
`workflow_apply_merge`; CLI flag on `workflow apply-merge`
(cli_workflow_tree). Non-interactive callers are byte-identical (default
off; `interactive` field in the result is null).

## Requirements / invariants (numbered, testable)

1. **Two phases, nothing applies during phase 1.** All decisions are
   collected over the whole plan BEFORE any file operation; `quit` at any
   point aborts with a legible error and an untouched tree.
2. **Denials are exclusions, recorded.** A denied operation is removed from
   the apply set; the merge-apply result carries
   `interactive.deniedByOperator` (worker, type, path) and the approved
   count. `all` approves the remainder without further prompts.
3. **Previews are bounded.** Modify = unified diff capped at 40 lines;
   create = 20-line head; delete/rename = descriptor only.
4. **Headless contexts refuse legibly.** `--interactive` without a real TTY
   (`sys.stdin.isatty()` — GLM spec-QA clarification; panel actions and
   workers run with stdin closed since esh) refuses with the fix line; `--interactive --dry-run` refuses as exclusive. The token
   requirement (intent approval) is unchanged and still required.

## Gherkin scenarios

```gherkin
Feature: per-item interactive write approval

  Scenario: [iwa-1] approved items apply, denied items are excluded and recorded
    Given a merge plan with a modify, a create and a delete
    When the operator approves two and denies the delete
    Then the tree shows exactly the approved changes, the denied file
      survives, and the result records the denial and the approved count

  Scenario: [iwa-2] quit aborts untouched and all approves the remainder
    Given the same plan
    When the operator quits on the first item
    Then nothing applied and the error is legible
    When the operator answers all on the first item
    Then every operation applies with a single prompt

  Scenario: [iwa-3] headless and conflicting invocations refuse
    Given no TTY on stdin and no injected decider
    Then interactive refuses with the fix line, and interactive+dry-run
      refuses as exclusive
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Fase de decisão separada da fase de aplicação | abort no meio de um apply interagiria com o rollback journal; coletar-tudo-antes mantém o rollback intacto e o abort trivial (nada aplicado) |
| `decider` injetável | contexto headless não tem TTY (esh fechou stdin de workers); o seam torna o contrato testável offline e abre o caminho GUI futuro |
| Token continua obrigatório | intenção (token) e conteúdo (interactive) são aprovações distintas — a ideação §5 pedia a segunda, não a substituição da primeira |
| Evidência | plan-mined P-2; `SUPERVISION_UI_IDEATION.md §5`; decisão do dono 2026-07-13 |

## Test strategy

- Behaviors: apply parcial com denial registrado (iwa-1); quit-untouched +
  all-single-prompt (iwa-2); recusas headless/exclusivas (iwa-3).
- Edge cases: preview de modify contém linhas de diff; stdin não-TTY simulado.
- Regression net: fixture controlled-write do workflow gate (caminho
  não-interativo byte-idêntico); wt_workflow_tree (superfície).
- Coverage: deterministic, hermetic via bind() —
  `testing/scenarios/iwa_interactive_apply.py`.

## Validation

- `python testing/scenarios/iwa_interactive_apply.py` — iwa-1..iwa-3 green.
- `python testing/scenarios/wt_workflow_tree.py` — workflow surface intact.
- `python scripts/spec_test_gate.py workflow --no-project-commands` —
  controlled-write fixtures green (non-interactive path unchanged).
