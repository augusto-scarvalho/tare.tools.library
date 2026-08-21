# SPEC-131 — `anomaly-card`: deterministic anomaly feature card (OB.3, deterministic half)

Status: proposed 2026-07-12 (acceptance: testing/scenarios/ac_anomaly_card.py).

Intake (SPEC-116 door NEW): request = "when the cost-outlier escalation fires,
the operator gets a number with no shape — a DETERMINISTIC card naming likely
factors (fan-out/depth/makespan from DW.3 fields, per-worker cost, profile) +
SPEC-129 evidence handles" (OB.3, P2). Covered-check: `records search anomaly
card` → no hit; no existing verb renders a per-workflow diagnosis. Decision:
**NEW**. Surface is CLI-only. SLICE: deterministic card ONLY — the opt-in LLM
explanation half of OB.3 stays OUT (deferred with UX-GA.4; its seat is the
card's `llmExplanation: null` field).

## Goal

A supervisor investigating a `workflow-cost-outlier` escalation runs
`python scripts/harness.py anomaly-card <workflow_id>` and gets the number's
shape in one deterministic command: the workflow's cost-ledger record (tokens,
cost, costBasis, DW.3 graph shape), a FIXED rule list of named likely factors
with their numbers, and SPEC-129 evidence handles when the WF dir still
exists. Always exits 0; pure reads; no LLM, no daemon.

## Applicability

Applies to `scripts/harness_lib/anomaly_card.py` (`card(root, workflow_id)`,
`cmd_anomaly_card`) and its one-line registration in
`scripts/harness_lib/cli_registry.py` (MF.1-r2 registry path, **zero
`scripts/harness.py` edits**). Does not change any existing verb, the workflow
tree, the ledger writers, gates, or state. The OB.3 LLM explanation is NOT
implemented here.

## Requirements / invariants (numbered, testable)

1. **Ledger-primary.** `card(root, workflow_id)` reads
   `.harness/state/cost-metrics.json` via `cost_metrics._load` (the ledger's
   existing reader) and keys off the most recent `kind == "workflow"` record
   for that `workflowId`. The ledger survives WF-dir scrubbing, so the card
   renders after `workflow scrub`.
2. **Graceful-null enrichment.** WHEN
   `.harness/workflows/active/<wfid>/` still exists (path via
   `workflow_ids.safe_workflow_path`), the card enriches with (a) per-worker
   estimated tokens from the token-audit report `reduce/token-audit.json` and
   (b) SPEC-129 `evidence_bundle.bundle` handles (imported, never
   re-implemented). A missing/half-scrubbed dir yields
   `workflowDirPresent: false` / `perWorkerTokens: null` / `evidence: null` —
   never a crash.
3. **Fixed factor rules.** `factors` is a FIXED deterministic list — no
   scoring model, no LLM. Each hit is a named string carrying its numbers:
   (i) fan-out above the same-profile ledger median (`graph.fanOut`, DW.3);
   (ii) a single worker holding > 50% of estimated tokens (needs the WF-dir
   report and >= 2 workers); (iii) duration > 3.0x the same-profile ledger
   median (mirroring self-review's `workflowCostOutlierFactor`). Median rules
   need >= 3 same-profile peers; rules whose inputs are absent stay silent.
4. **Unknown wfid is clean.** A `workflowId` with no ledger record returns
   `{found: false, error: ...}`; the verb prints a one-line "not found"
   message (or the `--json` error object) and still exits 0.
5. **Read-only, rc 0.** `anomaly-card` performs pure reads (ledger, WF dir,
   evidence bundle) and always exits 0; it writes nothing.
6. **Registry-only surface.** The verb registers in `cli_registry.register()`;
   existing verbs' order and help text are unchanged and `harness.py` is not
   edited (frozen surface: `testing/scenarios/cli_registry.py`).
7. **LLM half deferred.** The card carries `llmExplanation: null` as the
   documented seat for OB.3's opt-in, view-only LLM explanation — deferred
   with UX-GA.4; this spec's surface never calls a model.

## Gherkin scenarios

```gherkin
Feature: anomaly-card deterministic feature card

  Scenario: [ac-1] a dominating worker yields that named factor
    Given a temp ledger record for a workflow with same-profile peers
      And its WF dir's token-audit report shows one worker holding 90% of tokens
    When card() runs against it
    Then factors include the named dominant-worker string with its numbers
      And the fan-out-above-median and duration-outlier rules fire from the
      ledger's DW.3 graph fields and same-profile peer medians

  Scenario: [ac-2] missing WF dir → card still renders from the ledger
    Given a temp ledger record whose WF dir does not exist (scrubbed)
    When card() runs against it
    Then found is true and the ledger fields render
      And enrichment is gracefully null: workflowDirPresent false,
      perWorkerTokens null, evidence null

  Scenario: [ac-3] anomaly-card exits 0 on this repo
    Given this repository
    When "python scripts/harness.py anomaly-card <unknown-wfid>" runs
    Then it prints a clean not-found line and exits 0
      And --json exits 0 with a parseable error object (found: false)
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Ledger como input PRIMÁRIO (sobrevive ao scrub do WF dir) | `scripts/harness_lib/cost_metrics.py:108-202` (`record_workflow`: estTokens/observedTokens/costUsd/costBasis + DW.3 `graph`), `:46-53` (`_load`, o reader existente) |
| Enriquecimento graceful-null do WF dir | `scripts/harness_lib/workflow_token_audit.py:229-236` (report em `reduce/token-audit.json`, `workers[]` com estimatedPrompt/ResultTokens); `scripts/harness_lib/evidence_bundle.py:53-90` (SPEC-129 `bundle`, importado) |
| Fator de duração 3.0x = o mesmo idioma do detector que dispara a escalação | `scripts/harness_lib/self_review_rules.py:166-178` (`workflowCostOutlierFactor` 3.0) |
| Registro via `cli_registry.register()`, zero edits em `harness.py` | `scripts/harness_lib/cli_registry.py` docstring (receita MF.1-r2); `specs/40-features/failure-patterns.md` (OB.1 provou o caminho) |
| Read-only, sem LLM/daemon; metade LLM adiada | memória "observation must pay for itself"; `docs/IMPLEMENTATION_BACKLOG.md` OB.3 (a explicação LLM é opt-in, view-only, em cima do card) |

## Test strategy

- Behaviors: fabricated temp root — ledger record + peers + WF-dir token-audit
  report with a 90% worker → dominant/fan-out/duration factors named with
  numbers (ac-1); same ledger, no WF dir → card renders, enrichment null
  (ac-2 — the ledger-survives-scrub proof); live CLI run with an unknown wfid
  exits 0, text and `--json` both clean (ac-3, subprocess).
- Edge cases: missing/corrupt ledger → `found: false` (via `_load`'s empty
  default); half-scrubbed dir (dir exists, no reports) → null enrichment;
  fewer than 3 same-profile peers → median rules silent.
- Regression net: `testing/scenarios/cli_registry.py` frozen top-level surface
  (order preserved, `anomaly-card` appended before `workflow`) guards rule 6.
- Coverage: deterministic, stdlib-only, no LLM —
  `testing/scenarios/ac_anomaly_card.py`.

## Validation

- `python testing/scenarios/ac_anomaly_card.py` — ac-1/ac-2/ac-3 all green.
- `python testing/scenarios/cli_registry.py` — registry surface intact with the
  new verb.
- `python scripts/harness-test.py smoke` and `spec-pack --no-project-commands` —
  template conformance + static integrity.
