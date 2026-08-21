# Mutation-probe oracle (`mpo`) — CQ.5 slice, observe-only

Status: proposed 2026-07-13 (acceptance: testing/scenarios/mpo_mutation_probe.py).

Intake (SPEC-116 door NEW, un-deferring backlog CQ.5 by owner mandate): the
code-quality research round's #2 hole — the only per-change functional oracle
is a self-check written by the SAME implementer ("the author's test
formalizes the author's misreading"). The reserved seams
(`result_contracts.py` EXIT_CLASSES ponytail note,
`qa-evidence-capsule.md`) planned exactly this landing. Live proof on day
one: the probe's first real run returned 3 SURVIVED against a surface-only
scenario — a correct weak-oracle verdict.

## Goal

`harness.py oracle mutate` plants at most 3 deterministic AST mutants in the
diff's changed functions and demands the diff's OWN scenario fail: `killed`
(oracle has teeth), `survived` (weak oracle — the headline finding), plus
honest `error`/`timeout`/`skipped`. Observe-only: the verb never fails; a
future gate check is the control phase.

## Applicability

Applies to `harness_lib/mutation_probe.py` (+ `oracle` verb, frozen surface
+1 alongside `review`), `result_contracts.EXIT_CLASSES` (+killed/+survived)
and the `oracleEvidence.exitClass` schema enum. Test/scenario/hook files are
never mutation targets; untracked new files count whole-file (loop workers
never `git add`).

## Requirements / invariants (numbered, testable)

1. **One mutant per function, deterministic menu, cap 3 exercised.**
   Priority: comparison flip > and/or swap > if-negation > return-None;
   first applicable wins; no mutable site → `skipped`.
2. **Byte-identical restore, always.** The original file bytes are restored
   in a finally block and asserted equal — a crashed or timed-out scenario
   run never leaves a mutant in the tree.
3. **Diff-linked oracle.** The scenario is the diff's own added/modified
   `testing/scenarios/*.py` (untracked included via `-uall`); `--scenario`
   overrides; none linked → skipped rows, never a guess.
4. **Honest verdicts.** Scenario rc 1 → killed; rc 0 → survived (surfaced
   as ORACLE-WEAK in the verdict line); other rc → error; bound exceeded →
   timeout. `EXIT_CLASSES` and the schema enum carry killed/survived as the
   reserved seams planned.

## Gherkin scenarios

```gherkin
Feature: mutation-probe oracle

  Scenario: [mpo-1] a strong oracle kills the mutant
    Given a changed function and a same-diff scenario that asserts its behavior
    When oracle mutate runs
    Then at least one mutant is killed and the file is restored byte-identical

  Scenario: [mpo-2] a weak oracle is caught surviving
    Given the same change with a scenario that asserts nothing
    Then the mutant survives, the verdict says ORACLE-WEAK, and the restore
      still holds

  Scenario: [mpo-3] calm paths and the extended vocabulary
    Given a diff with no linked scenario
    Then rows report skipped, and EXIT_CLASSES plus the schema enum include
      killed and survived
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Observe-only primeiro | idiom medição-antes-de-controle; CQ.5 do backlog previa gate check como fase 2 |
| Mutante único por função, cap 3 | CQ.5: "capped mutants+runtime, ≤3 mutants NOT a mutation score" |
| ast.unparse no arquivo temporariamente mutado | formatação perdida é irrelevante num artefato que vive só durante UM run e é restaurado byte-a-byte |
| Untracked = whole-file changed | workers do loop nunca dão git add; sem `-uall` o elo diff→cenário não existe (bug pego no primeiro self-check) |
| Evidência | docs/research/code-quality-agents.md CQ1; backlog CQ.5; primeiro run live: 3 SURVIVED corretos |

## Test strategy

- Behaviors: killed com oráculo forte (mpo-1); survived + restore honesto
  (mpo-2); skipped + vocabulário estendido (mpo-3).
- Edge cases: função sem sítio mutável → skipped; cenário que crasha →
  error; restore assertado mesmo sob exceção.
- Regression net: cli_registry (superfície), qa-evidence capsule consumers
  (enum estendido é aditivo).
- Coverage: hermetic temp git repos —
  `testing/scenarios/mpo_mutation_probe.py`.

## Validation

- `python testing/scenarios/mpo_mutation_probe.py` — mpo-1..mpo-3 green.
- `python scripts/harness_lib/mutation_probe.py` — module self-check.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.

## Amendments

### v2 — the probe prefers the diff's own lines and names what it mutated (row oracle-mutate-probes-one-site-per-change), 2026-07-29

`_Mutator` stopped at the FIRST mutable site in a changed function, so the
probed line was often a pre-existing one hundreds of lines from the hunk —
false alarms on lines the author never wrote AND false comfort ("oracle
exercised") while the added operator went unprobed; measured live 2026-07-27
(`if timed_out and async_job:` unprobed, hand-mutant stayed green until
exp21-9). Two of the row's three candidate shapes shipped together:

- **Prefer-in-diff.** `mutate_source(source, func, prefer_lines)` first
  restricts every mutation site to the diff's NEW-side line numbers
  (`changed_python`); only when the hunk offers no mutable site does it fall
  back to the old first-site-anywhere.
- **Named site.** Every probe row and console line now carries the mutated
  line and its provenance: `<mutation>@L<line>(in-diff|fallback)` — a reader
  tells a diff-relevant survivor from a pre-existing one in a second.

The third shape (one mutant per site up to a cap) stays NOT built — the cap-3
philosophy holds and the preference removes the need in the common case.
Teeth: `_demo()` asserts the three arms (in-diff wins; bare call = labeled
fallback; no-site-on-hunk = honest fallback) plus site/line in the probe
report; run via mpo + `w29_observe_first`'s self-check subprocess.

### v3 — the reserved control phase lands OUTSIDE the verb (SPEC-157 A1), 2026-07-30

The Goal's "a future gate check is the control phase" is now built, as the
THIRD leg of the commit ledger (`validation_stamp.check_mutate`, amendment A1
of `specs/40-features/parallel-verify-heartbeat.md`). This module gained only
the EVIDENCE and the waiver:

- **Run-level row.** Every `oracle mutate` appends one
  `{kind: "mutate-run", diff, stagedFingerprint, counts, scenario}` row to
  `.harness/state/defect-telemetry.jsonl`, next to the existing
  `mutate-survivor` rows. `counts` is keyed by EXACTLY the exitClass names
  (`MUTATE_CLASSES`: killed | survived | error | timeout | skipped), zero-filled,
  because the consumer reads `counts["survived"]`. `stagedFingerprint` comes
  from `validation_stamp` (never a second implementation) and is `null` when no
  `precommitValidation` policy is adopted — the probe never fails over a ledger
  it only annotates.
- **`oracle waive --reason "<text>"`.** Appends
  `{kind: "mutate-waiver", stagedFingerprint, reason}` — the overseer's judged
  tolerance for the survivors on the CURRENT staged surface, which turns the
  third leg's block into a warn carrying the reason. An empty/whitespace reason
  is REFUSED (`HarnessError`, rc 2) and writes nothing.
- **Observe-only, amended precisely.** The VERB still never fails: `mutate`,
  `canary` and `waive` all exit 0 (the waive refusal is an argument error, not
  a verdict). Enforcement lives in the commit join, never in the probe. The old
  wording "a future gate check is the control phase" reads as built.
- **Landmine.** Sink rows written DURING a gate run land in the swapped tree
  and are discarded with the gate-hold; the ritual runs `oracle mutate` BEFORE
  `gate-staged`, which is what protects the row.

Teeth: `mpo-4` (run row with the ledger fingerprint + the full counts
vocabulary, null fingerprint without a policy; waive refuses an empty reason
and writes exactly one row for a real one); the consumer matrix is `pvr-11a..f`.
