# Experiment-lifecycle registry (`exl`) — SPEC-116 pack

Status: proposed 2026-07-13 (acceptance: testing/scenarios/exl_experiment_lifecycle.py).

Intake (SPEC-116 door NEW): owner mandate 2026-07-13 — *"implementar uma
metodologia formal para os nossos testes e experimentos, medição de variáveis,
aferir resultados, quando e como engavetar os experimentos que falharam … para
não ficarmos presos com features ruins aplicadas no projeto"*. Covered-check
result: no registry existed — the research-playbook prescribes the experiment
card template (`hipótese | baseline | métricas | critérios de decisão`) but
nothing enforced a lifecycle, so a failed experiment stayed applied as a bad
feature instead of being shelved. This registry is the enforcing half.

## Goal

`harness.py experiment` makes a hypothesis a first-class, state-machined
object: PROPOSED (pre-registered, complete card) → ACTIVE (owner-activated,
reviewBy nag stamped) → SHIPPED | SHELVED (a permanent tombstone with the
evidence a verdict demands). Measurements are append-only and active-only; one
extension is allowed; `doctor` nags when an active experiment ages past its
reviewBy. Canonical state lives only in `.harness/state/experiments.json` via
the verb — a card without a registry row does not exist.

## Applicability

Applies to `harness_lib/experiment_registry.py` (store + `experiment` CLI verb
registered via `cli_registry`), `repo_health.py` doctor check (6)
`experiment-overdue`, and `intake_queue.py` (the `experiment` decision routes a
triaged ask here). Writes only `.harness/state/experiments.json`. The
normative protocol narrative is `docs/EXPERIMENT_METHODOLOGY.md`.

## Requirements / invariants (numbered, testable)

1. **Pre-registration is a closed set.** `add` refuses an id not matching
   `^EXP-\d+$`, a duplicate id, and any card missing/empty one of the six
   REQUIRED fields (`hypothesis, metric, baseline, successCriteria,
   abandonCriteria, reversalPlan`) — naming the missing keys. A proposed entry
   rejects `record`/`extend`/`verdict`.
2. **Activation stamps a reviewBy nag.** `activate` (proposed-only) sets
   `activatedAt` and `reviewBy` = an explicit ISO override or now + 14 days.
3. **Measurements are append-only and active-only.** `record` appends
   `{at, value, note}` to `measurements` only while active; a settled
   tombstone rejects further records.
4. **One extension maximum.** `extend` (active-only) pushes `reviewBy` out
   once; a second `extend` refuses ("already extended once; decide a verdict or
   escalate to the owner").
5. **Verdict evidence is asymmetric.** `verdict` (active-only) demands a
   decision in `shipped | shelved`; `shipped` requires ≥1 measurement ("no
   shipping without data"); `shelved` requires non-empty `evidence` AND
   `reopenTrigger` (the reversal is proven, and "não é 'não', é 'quando'").
6. **Tombstones are permanent; corrupt reads are calm.** A verdict writes
   `verdict, verdictAt, evidence, note, reopenTrigger` and is never trimmed; a
   missing or corrupt registry reads as empty and repairs on the next write.
   All stored free text is secret-redacted and machine-local-path-scrubbed.
7. **Doctor is an advisory nag, always rc 0.** `experiment-overdue` warns
   (never fails) listing active experiments past their reviewBy, naming the id;
   a clean registry reads ok.

## Gherkin scenarios

```gherkin
Feature: experiment-lifecycle registry

  Scenario: [exl-1] pre-registration is a closed door
    Given an incomplete card, a bad id, a duplicate id, a verb on a proposed
      entry, and an unknown-id activation
    Then each one refuses legibly

  Scenario: [exl-2] lifecycle and the single extension
    Given a proposed experiment activated with a reviewBy about 14 days out
    When a measurement is recorded and the review is extended once
    Then a second extension refuses, shipping without data refuses, shipping
      with a measurement succeeds, and the shipped tombstone rejects records

  Scenario: [exl-3] shelving asymmetry and tombstone permanence
    Given an active experiment shelved without evidence or a reopen trigger
    Then it refuses; with both, the tombstone keeps verdict/verdictAt/evidence/
      reopenTrigger, a planted secret is redacted, a machine-local path is
      scrubbed, and the entry stays listed

  Scenario: [exl-4] doctor nag and the frozen surface
    Given an active experiment whose reviewBy is in the past
    Then doctor reports experiment-overdue as warn naming the id, a clean
      registry reads ok, and experiment answers --help with rc 0
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Pré-registro com conjunto fechado de campos | research-playbook experiment template (`hipótese\|baseline\|métricas\|critérios de decisão`) + prática de registered reports (pré-comprometer hipótese e critérios antes de medir) |
| Medir antes de controlar (probe active = zero mudança de comportamento) | idiom do repo medição-antes-de-controle (security-baseline, mpo/ort observe-only); controle só entra via SPEC-116 citando o EXP-id |
| Uma extensão só, segunda vira escalação | anti-sunk-cost / anti-zombie-retry; pedido do dono: "quando e como engavetar os experimentos que falharam" |
| Assimetria de evidência (shipped precisa de dado, shelved precisa de prova+gatilho) | "no shipping without data"; reversão executada e verificada antes do veredito; reopenTrigger = "não é 'não', é 'quando'" |
| Tombstones permanentes; leitura calma de corrupção | anti-zombie-retry; mesmo idiom da intake-queue (_load degrada corrupção pra vazio) |
| Redação/scrub de todo texto livre | prompts e evidências podem colar segredos/paths locais; mesmo seam secret_scan + scrub da intake-queue |
| Evidência | owner mandate 2026-07-13; docs/EXPERIMENT_METHODOLOGY.md; os 9 EXPs semeados em docs/research/weekly-monitor-w28-*-extract.md |

## Test strategy

- Behaviors: closed pre-registration (exl-1); lifecycle + single extension +
  ship-needs-data (exl-2); shelve asymmetry + redaction/scrub + tombstone
  permanence (exl-3); doctor nag + frozen surface (exl-4).
- Edge cases: verb on a proposed/settled entry refuses; missing/corrupt
  registry reads as empty and `stale_active` returns `[]`; reviewBy override
  honored; `--review-by` parsed with `common.parse_iso_datetime`.
- Regression net: rh_repo_health (doctor IDS drift guard), cli_registry (frozen
  surface +experiment), iq_intake_queue (decision-vocabulary +experiment).
- Coverage: hermetic temp roots, stdlib-only —
  `testing/scenarios/exl_experiment_lifecycle.py`.

## Validation

- `python testing/scenarios/exl_experiment_lifecycle.py` — exl-1..exl-4 green.
- `python scripts/harness_lib/experiment_registry.py` — module self-check.
- `python testing/scenarios/rh_repo_health.py` — doctor IDS drift net (+experiment-overdue).
- `python testing/scenarios/cli_registry.py` — frozen surface (+experiment).
- `python testing/scenarios/iq_intake_queue.py` — intake decision-vocabulary regression.
- `python scripts/harness_lib/intake_queue.py` — intake self-check.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.

## Amendments

### v2 — evidenceGrade field (App H) + methodology decision constants (2026-07-18)

LQ7-C1 (article-coverage backlog C1: §6.6, §9.10-g, App E/H): the normative
protocol (`docs/EXPERIMENT_METHODOLOGY.md`) gains the article's decision
constants (α/power/δ thresholds, tighten-free/loosen-pre-registered rule),
the lexicographic decision rule, the 1-4 evidence grades (App H, with
downgrade + promotion gate), and factor typing (App E-2). The registry gains a
matching **optional** field.

8. **`evidenceGrade` is optional and additive.** `add` and `verdict` accept an
   `evidenceGrade`; when present it MUST be in the closed set `{1,2,3,4}` (App
   H) or the call refuses legibly — there is no inference and no retroactive
   mandate, so existing gradeless cards stay valid. The grade is shown in the
   card (`_card_lines`); on a `verdict` that carries no grade, the advisory
   prints one line pointing at the methodology's App H section (a pointer, not
   a heuristic).

```gherkin
Feature: experiment-lifecycle registry (v2)

  Scenario: [exl-6] evidenceGrade is an optional, closed-set field
    Given an experiment added or a verdict decided with an evidenceGrade
    Then an out-of-set grade (e.g. 7) refuses legibly, a valid grade (1-4)
      persists on add and on the verdict and shows in the card, and a card
      added without a grade stays valid
```

Frozen surfaces: no new CLI verb, panel action, or TSV opt-in — only an
optional `--grade` flag on the existing `experiment` verb. Acceptance: exl-6 in
`testing/scenarios/exl_experiment_lifecycle.py`.
