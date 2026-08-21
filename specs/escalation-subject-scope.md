# Escalation subject scope — every ask belongs to one world (`esc-subject-scope`)

Status: Active (v2 — scoped HITL surfaces amendment, 2026-07-13; acceptance:
testing/scenarios/es_subject_scope.py + testing/scenarios/ehv_scoped_hitl.py).

Intake (SPEC-116 door NEW): request = "auditar se PEDIDOS DE ESCALAR PRA
HUMANO/USUÁRIO/LLM não estão vazando de um projeto pra outro… Cada um deve ter
seu MUNDO e VISÃO" (isolation round, `docs/roadmap/cross-project-isolation-escalation.md`
G1–G3). Covered-check: the ledger schema has no subject anywhere (`records
search escalation subject scope` → no hit); the records ledger got its subject
dimension, escalations did not. Decision: **NEW**. SLICE: phase 1 ONLY —
subject field + producer stamping + scoped list/resolve + dual-subject test.
Phase 2 (panel/chat scoped views, `esc-scoped-hitl-view`) and phase 3
(`handoff-subject-confinement`) stay OPEN in the backlog.

## Goal

Every escalation record carries a structured `subject` — `"self"` (the
harness) or one target name — stamped where the escalation is BORN, so the
human queue can be scoped to one world and a scoped resolve cannot touch
another subject's record. One global ledger file stays (SPEC-109 durability);
scoping is a field plus mandatory filters, never a file split.

## Applicability

Applies to `scripts/harness_lib/escalations_lib.py` (compactor branches,
`list_escalations(subject=, root=)`, `scoped_resolve_check`), the three
pre-existing producers (`result_contracts.py` validated-event payload,
`workflow_reduce.py` harness-result payload, `self_review.py` finding
emission) plus the `security_routing_escalation` branch (always `self`), the
`escalations --target` CLI argument (cli_registry) and the guarded
`cmd_escalations` resolve. Panel/chat surfaces are NOT touched in this slice.

## Requirements / invariants (numbered, testable)

1. **Structured subject, legacy-safe.** Every raised record carries
   `subject: "self" | <target-name>`; a record without the field reads as
   `"self"` at view time (no migration, resolved ids frozen).
2. **Stamped at birth.** `harness_result_validated` events and folded
   `WF-*/reduce/harness-result.json` results carry the workflow's `target`
   (payloads now include it at the producers); `self_review_finding` events
   derive the subject structurally (finding `subject` annotation or the
   `target/<name>/…` id), never by human parsing; `security_routing_escalation`
   is always `self` (the gate scans the harness tree).
3. **Scoped view.** `list_escalations(subject=…)` filters pending to one
   world; the unfiltered payload always carries `bySubject` counts and each
   row its `subject`; `root=` parameterizes the paths for dual-subject tests.
4. **Scoped resolve refuses cross-subject.** `scoped_resolve_check` returns
   the pending record only when the requested scope matches (or no scope was
   given — the bare-CLI operator escape hatch stays legal, disclosed); a
   mismatch raises a legible error naming the actual subject; unknown ids keep
   the existing legible refusal.
5. **CLI parity.** `escalations --target <name|self>` scopes the list AND
   guards `--resolve`; exit 2 on refusal via HarnessError.

## Gherkin scenarios

```gherkin
Feature: escalation subject scope (phase 1)

  Scenario: [essc-1] a mixed ledger filters by subject and counts by subject
    Given raised records for self, tA, tB and one legacy record without the field
    When the queue is listed unfiltered and scoped to tA
    Then bySubject counts all four (legacy as self) and the tA view contains
      only tA's record with no other subject's reason text

  Scenario: [essc-2] all producers stamp the subject at compaction
    Given a harness-result event with target tA, a self-review finding for tB
      and a security-routing event
    When the compactor folds them into the ledger
    Then their raised records carry subjects tA, tB and self respectively

  Scenario: [essc-3] scoped resolve refuses cross-subject
    Given pending records for tA and tB
    When tB's id is resolved under scope tA
    Then the guard raises naming tB as the actual subject, while a matching
      scope, an unscoped resolve and an unknown id behave legibly

  Scenario: [essc-4] a target workflow's folded escalation is attributed
    Given a WF harness-result with requiresEscalation and target tA
    When the queue folds it
    Then the pending row's subject is tA

  Scenario: [essc-5] the CLI exposes the scoped view
    Given this repository
    When "escalations --target self" runs
    Then it exits 0 and the payload carries subjectFilter and bySubject
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Campo + filtros, não split de arquivo | roadmap D1: split multiplica compaction/monotonicity sem ganho de MVP; SPEC-109 durabilidade |
| Legacy sem campo = `self`, sem migração | roadmap risk: histórico pequeno, resolved ids congelados |
| Stamp nos produtores, não parse de prefixo | G2 ("attribution only as a string convention"); `self_review_rules.annotate_criticality:66-68` já deriva o par |
| Resolve sem escopo continua legal no CLI puro | roadmap D2: escape hatch deliberado do operador; superfícies painel/chat são as fail-closed (fase 2) |
| `target` no payload do harness-result | roadmap risk "verify workflow_harness_result carries target" — verificado ausente; adicionado em `workflow_reduce.py` |

## Test strategy

- Behaviors: mixed-ledger filter + counts + legacy default (essc-1); the four
  compactor branches stamp (essc-2); guard refusal/match/unscoped/unknown
  (essc-3); WF fold attribution (essc-4); live scoped CLI (essc-5,
  subprocess).
- Edge cases: legacy record without field; `subject=None` = unfiltered;
  workflow result without `target` reads as self.
- Regression net: `sdr_security_routing.py` (routing escalations),
  `se_self_review` (emission), `m5_ui_panel` (panel reads the ledger
  unchanged — subject is additive).
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/es_subject_scope.py`.

## Validation

- `python testing/scenarios/es_subject_scope.py` — essc-1..essc-5 green.
- `python testing/scenarios/ehv_scoped_hitl.py` — the v2 scoped-surface
  scenarios (ehv-1..ehv-4) green.
- `python testing/scenarios/sdr_security_routing.py` and
  `python testing/scenarios/m5_ui_panel.py` — additive-field regression net.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.

## Amendments

### v2 (2026-07-13) — esc-scoped-hitl-view: the human surfaces get worlds

Phase 2 lands on the phase-1 primitive:

- **Panel**: escalation rows and attention strips carry `subject` (legacy
  reads as self; non-self subjects label the strip `[<name>]`); the
  Escalations card renders a subject badge + filter chips (all/self/targets
  seen); the Resolve button ALWAYS forwards the card's subject as `--target`,
  so a cross-subject resolve is refused server-side by `scoped_resolve_check`
  — the panel is a fail-closed surface, the bare CLI keeps the unscoped
  operator escape hatch.
- **Chat**: the high/critical nag counts only the SESSION's subject
  (`_pending_critical(root, subject)`; target session → that target, else
  self, unscoped still available for tooling); inside a `/repo <name>`
  session a bare `!escalations` defaults to `--target <name>` with a printed
  note (an explicitly typed `--target` always wins).
- Phase 3 (`handoff-subject-confinement`) stays OPEN.

```gherkin
Feature: scoped HITL escalation surfaces (phase 2)

  Scenario: [ehv-1] panel rows and strips carry the subject
    Given a mixed ledger with self, target and legacy records
    When the panel collectors run
    Then every row carries its subject, legacy reads as self and non-self
      strips are labeled with their world

  Scenario: [ehv-2] the chat nag counts one world only
    Given the same ledger
    When _pending_critical runs scoped to tA, self and unscoped
    Then the counts are per-world with the unscoped total still available

  Scenario: [ehv-3] panel resolve is subject-scoped by construction
    Given the resolve-escalation action builder
    When built with and without a subject param
    Then the scoped argv carries --target and the bare shape stays the CLI
      escape hatch

  Scenario: [ehv-4] the surfaces are wired
    Given the page and REPL sources
    Then the subject chips/badges render, resolve forwards the card subject
      and a /repo session's bare !escalations defaults to its world
```
