# SPEC-126 — `failure-patterns`: repeat-failure rollup verb (OB.1)

Status: proposed 2026-07-12 (acceptance: testing/scenarios/fp_failure_patterns.py).

Intake (SPEC-116 door NEW, from specs/templates/intake-refinement.md): request =
"failure-pattern clustering — a deterministic rollup over the escalations +
records ledgers surfacing repeat failures (same failureClass/role/executor)"
(OB.1, P1). Covered-check: `records search failure patterns rollup` → no hit
(`[]`); `doc-find failure patterns clustering` → no enrichment hit
(graphify-out absent in the worktree). Decision: **NEW**. Surface is CLI-only.

## Goal

A supervisor can see repeat failures in one deterministic command:
`python scripts/harness.py failure-patterns` clusters every durable failure
event by `(failureClass, role, executor)` — count, last occurrence, source
ledgers — and always exits 0. Verify-on-demand: pure reads, zero writes, no
LLM, no daemon; the rollup is recomputed only when someone asks.

## Applicability

Applies to `scripts/harness_lib/failure_patterns.py` (`rollup(root)`,
`cmd_failure_patterns`) and its one-line registration in
`scripts/harness_lib/cli_registry.py` (MF.1-r2 registry path, **zero
`scripts/harness.py` edits**). Does not change any existing verb, the workflow
tree, gates, or state; no polling (observation must pay for itself).

## Requirements / invariants (numbered, testable)

1. **Two durable sources.** `rollup(root)` enumerates (a) the escalations
   ledger `.harness/state/escalations.json` — `raised` AND `resolvedRecords`
   values, the same enumeration `records.collect_records` uses (resolved
   escalations are precisely the repeat-failure history) — and (b) worklog +
   archive entries (via `records._load`) whose kind or tags contain
   `failure` (case-insensitive).
2. **Grouping key.** Events group by `(failureClass, role, executor)`; each
   missing/falsy field buckets as `"(none)"`, mirroring
   `cost_metrics._group`'s tolerance — a field-less entry can never crash the
   rollup.
3. **Group shape.** Each group is
   `{failureClass, role, executor, count, lastAt, sources}`; `lastAt` is the
   max event timestamp (`resolvedAt`/`raisedAt` for escalations, `at` for
   records; missing → `""`), `sources` the ledger relpaths that contributed.
4. **Ordering.** Groups sort by `count` desc, then `lastAt` desc.
5. **Read-only, rc 0.** `failure-patterns` prints a text table (or JSON with
   `--json`) and exits 0; it never writes — it deliberately reads the ledger
   file directly instead of `escalations_lib.list_escalations()`, whose
   read path compacts (writes) `events.jsonl` into the ledger and drops
   resolved records.
6. **Registry-only surface.** The verb registers in `cli_registry.register()`;
   existing verbs' order and help text are unchanged and `harness.py` is not
   edited (frozen surface: `testing/scenarios/cli_registry.py`).
7. **No LLM, no daemon.** The rollup is stdlib-deterministic and runs only on
   demand; nothing polls, watches, or schedules it.

## Gherkin scenarios

```gherkin
Feature: failure-patterns repeat-failure rollup

  Scenario: [fp-1] repeat failure classes cluster with honest counts
    Given a temp escalations ledger with 3 escalations, 2 sharing a failureClass
    When rollup() runs against it
    Then it returns two groups with counts 2 and 1, sorted count-first,
      and the repeat group carries the latest raisedAt as lastAt

  Scenario: [fp-2] missing fields land in "(none)" buckets, never crash
    Given ledger entries missing role, executor or failureClass
      And a failure-tagged worklog record with no routing fields at all
    When rollup() runs against it
    Then each missing field groups under "(none)"
      And the "(none)" bucket lists both contributing source ledgers

  Scenario: [fp-3] failure-patterns exits 0 on this repo
    Given this repository
    When "python scripts/harness.py failure-patterns" runs
    Then it prints the rollup table and exits 0, and --json parses as a list
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Ler o ledger durável direto (`read_json` + `records.ESCALATIONS_REL`), não `escalations_lib.list_escalations()` | `scripts/harness_lib/escalations_lib.py:101-132` — o loader existente é bound (`bind(env)`), compacta (ESCREVE) `events.jsonl` na leitura e retorna só pendentes; `scripts/harness_lib/records.py:236-243` é a enumeração de leitura pura já existente |
| Tolerância a campos ausentes = `"(none)"` | `scripts/harness_lib/cost_metrics.py:229-235` (`_group`), mesmo idioma |
| Registro via `cli_registry.register()`, zero edits em `harness.py` | `scripts/harness_lib/cli_registry.py` docstring (receita MF.1-r2); `specs/40-features/spec-index.md` (o verbo `spec-index` provou o caminho) |
| Read-only, verify-on-demand, sem LLM/daemon | memória "observation must pay for itself"; espelha `spec-index`/`doctor` |

## Test strategy

- Behaviors: fabricated temp ledger → counts/ordering/lastAt/sources (fp-1);
  field-less entries across both sources → "(none)" buckets, no crash (fp-2);
  live CLI run exits 0 and `--json` parses (fp-3 — no hard row asserts, the
  real ledger evolves concurrently).
- Edge cases: missing `escalations.json`/`worklog.json` → empty rollup (the
  `read_json`/`_load` defaults, exercised implicitly by each temp root before
  its files exist); non-dict ledger values are skipped.
- Regression net: `testing/scenarios/cli_registry.py` frozen top-level surface
  (order preserved, `failure-patterns` appended before `workflow`) guards
  rule 6.
- Coverage: deterministic, stdlib-only, no LLM —
  `testing/scenarios/fp_failure_patterns.py`.

## Validation

- `python testing/scenarios/fp_failure_patterns.py` — fp-1/fp-2/fp-3 all green.
- `python testing/scenarios/cli_registry.py` — registry surface intact with the
  new verb.
- `python scripts/harness-test.py smoke` and `spec-pack --no-project-commands` —
  template conformance + static integrity.
