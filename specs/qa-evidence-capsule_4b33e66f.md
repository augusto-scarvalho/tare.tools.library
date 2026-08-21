# SPEC-121 — QA evidence capsule (`oracleEvidence`) in WORKER_RESULT

Status: SPEC-121, proposed 2026-07-12 (acceptance: `testing/scenarios/qe_evidence_capsule.py`).

Door NEW (CQ.2): covered-check ran `records search oracleEvidence` / `doc-find
oracle evidence capsule` — no existing spec owns worker-side QA evidence; the
worker-result contract specs (agentic-map-reduce, worker-live-tail) stop at
findings/graphify. Intake accepted 2026-07-12; its criteria seed rules 1–5 and
scenarios qe-1..qe-4 below.

## Goal

A worker MAY attach an optional QA evidence capsule (`oracleEvidence`) to its
WORKER_RESULT stating which oracle ran, how it exited, a handle to a
pre-scrubbed artifact, and a bounded re-run command — so a reviewer's cost is
O(capsule) instead of O(re-running the oracle).

## Applicability

`scripts/harness_lib/result_contracts.py` (`validate_worker_result`) and
`schemas/worker-result.schema.json`. Does not cover HARNESS_RESULT,
REDUCE_RESULT, or REVIEWER_RESULT. The collect boundary
(`workflow_reduce.py` `secret_scan.scan(data)`) already scrubs new fields
generically and is explicitly out of scope.

## Requirements / invariants (numbered, testable)

1. **Optional.** `oracleEvidence` is never required; a WORKER_RESULT without it
   validates exactly as before this spec (zero new errors).
2. **Shared exit vocabulary.** `exitClass` must be one of
   `result_contracts.EXIT_CLASSES = ("passed","failed","error","timeout","skipped")`,
   defined once and mirrored by the JSON schema enum.
3. **Required core.** A present capsule must carry a non-empty `oracle` string
   and a valid `exitClass`.
4. **Handles, not bodies.** `artifactPath` (optional) must be a RELATIVE path —
   absolute paths (posix or drive-letter) and any `..` segment are validation
   errors.
5. **Bounded re-run.** `rerunCmd` (optional) is a string of at most 400 chars.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Capsule over re-run for review | CQ.2 backlog item: review cost O(capsule) not O(re-run); handles-not-bodies norm (CQ.3, `.harness/prompts/subagent-contract.md` worker constraints) |
| Enum lives once in `result_contracts` | single-source vocabulary; schema mirrors it (same pattern as status enums already duplicated schema↔validator) |
| Relative-only `artifactPath` | path-hygiene precedent (`ph_path_hygiene`, `existing_rel_path` root-escape guard in `scripts/harness.py`) — a capsule must not point outside the repo |
| No scrub logic here | collect boundary already scrubs generically (`workflow_reduce.py:97` `secret_scan.scan(data)`) |

## Gherkin scenarios

```gherkin
Feature: QA evidence capsule in WORKER_RESULT

  Scenario: [qe-1] a valid capsule is accepted
    Given a minimal valid WORKER_RESULT
    When it carries oracleEvidence with an oracle, exitClass "passed", a relative artifactPath and a short rerunCmd
    Then validate_worker_result returns no errors

  Scenario: [qe-2] a bad exitClass is rejected
    Given a capsule whose exitClass is not in EXIT_CLASSES
    When the result is validated
    Then a validation error names oracleEvidence.exitClass

  Scenario: [qe-3] an absolute artifactPath is rejected
    Given a capsule whose artifactPath is absolute or contains a ".." segment
    When the result is validated
    Then a validation error names oracleEvidence.artifactPath

  Scenario: [qe-4] a capsule-less result validates unchanged
    Given a minimal valid WORKER_RESULT without oracleEvidence
    When the result is validated
    Then validate_worker_result returns exactly the same (empty) error list as before this spec
```

## Ceilings (upgrade paths)

- `exitClass` is a closed 5-value enum; CQ.5's `killed`/`survived` extend
  `EXIT_CLASSES` (and the schema enum) when the mutation probe lands.
- `artifactPath` existence is NOT checked (the artifact may live in a scrubbed
  workflow dir by review time); add an existence check only if reviewers hit
  dangling handles in practice.

## Test strategy

- Behaviors to verify: valid capsule accepted; bad exitClass, overlong
  rerunCmd, absolute/`..` artifactPath each rejected; capsule-less result
  unchanged.
- Edge cases: posix-absolute vs drive-letter-absolute vs `..` traversal paths.
- Regression risks: any new error on capsule-less results (rule 1) — guarded by
  qe-4 and the existing worker-result scenarios.
- Coverage impact: enforced via `qe_evidence_capsule.py`.

## Validation

- `python testing/scenarios/qe_evidence_capsule.py` — checks `qe-1`..`qe-4`
  call `validate_worker_result` directly on a minimal result ± capsule variants.
- `feature-spec-conformance:qa-evidence-capsule` green in the spec-pack gate.

## Amendments

### v2 — TEST_QUALITY_SIGNALS joins the shared vocabulary (W29.N4), 2026-07-28

`result_contracts.py` gains, beside `EXIT_CLASSES` and by the same
defined-ONCE precedent, the test-quality signal vocabulary
`TEST_QUALITY_SIGNALS = ("assertionDensity", "edgeCaseHits",
"nullSafetyHits", "flakinessCandidates")` plus
`validate_test_quality_signals` — a shape check that refuses unknown keys
(the drift the single schema exists to prevent), booleans and non-numbers,
while keeping every signal optional. SEPARATE signals, never a composite
score (the W29 round rejected a single quality score by brief and by paper).
Timing is the point: the keys are frozen BEFORE the first producer writes
them — the persistence half already shipped keyed inside `EXIT_CLASSES`
(W29.A3 oracle canary), and the AST proxies (W29.N5) must write exactly
these keys. Consumers: N6 observe-only gate checks, EXP-32. Teeth:
`w29_observe_first.py` (`w29:signal-schema-keys`,
`w29:signal-schema-validates`, `w29:signal-canary-half-no-drift`).

### v4 — the signals gain a reader in the gate report (W29.N6), 2026-07-28

"Sinal existe mas ninguém vê" closes: `test_quality_ast.latest_point` reads
the newest `test-quality`-tagged ledger point (mirrors
`mutation_probe.trend`'s tag-scan, worklog then archive, torn bodies
skipped), and the gate gains `check_test_quality` — ONE always-pass row named
`test-quality` whose detail carries the point's signals (or the honest
"no test-quality points recorded yet"). No threshold, no branching:
observe-only per the W29 doctrine; promotion to anything enforcing is a
future owner decision with EXP-32 data. Teeth: `w29_observe_first.py`
`w29:tq-latest-roundtrip` (hermetic temp-root ledger), `w29:tq-latest-empty-none`,
`w29:tq-gate-check-observe-only` (always-pass shape).

### v3 — the vocabulary gains a producer: AST proxies (W29.N5), 2026-07-28

`scripts/harness_lib/test_quality_ast.py` is the first writer of the v2 keys.
Stdlib-only (`ast`), observe-only, no `harness.py` verb (N6 owns gate/verb
wiring); its callable surface is `analyze_file` / `analyze_diff` / `record`
plus a `--record` module entry point for EXP-32.

**Scoping.** `analyze_diff(root, diff="HEAD")` reuses
`mutation_probe.changed_python` and keeps only test surfaces — rel path (with
backslashes normalized) under `testing/scenarios/`, or a basename starting
`test_` NOT under `scripts/`, always `.py`. The `scripts/` exclusion is an
overseer review catch at integration: the module's own filename
(`test_quality_ast.py`) satisfied the bare `test_` arm, so the producer
selected itself as a test surface — harness library code is never a test
surface. The diff decides WHICH files are analyzed, never which lines: test
quality is a property of the whole file, not of the lines someone happened
to edit.

**Heuristic definitions** (independent counts; NEVER combined into a score):

- `assertionDensity` — assertions per 100 physical lines,
  `round(100 * asserts / max(loc, 1), 2)`. An assertion is an `ast.Assert`, a
  bare `check(...)` call (this repo's scenario idiom), or a call to an
  attribute named `assert*` (unittest style). Per-100-LOC because scenario
  files are `_checks()`/`main()`-shaped, not pytest-shaped.
- `edgeCaseHits` — boundary LITERALS (never names) as operands of an
  `ast.Compare` or as arguments to an assertion call: `0`, `-1`, `""`, and the
  empty containers `[]`, `{}`, `()`, `set()`. `None` is excluded here on
  purpose — it belongs to `nullSafetyHits`, and double counting would blur two
  signals into one.
- `nullSafetyHits` — `ast.Compare` with `Is/IsNot/Eq/NotEq` against
  `Constant(None)`, plus `None` passed as an argument to an assertion call.
- `flakinessCandidates` — total hits across five frozen buckets, module
  constants so each is one editable data line: `FLAKY_CLOCK`
  (`time.sleep`, `time.time`, `*.now`, `*.utcnow`, `*.today`), `FLAKY_RANDOM`
  (`random.*`, `uuid.uuid4`), `FLAKY_NET` (imports of `socket`, `requests`,
  `urllib.request`, `http.client`, `ssl`), `FLAKY_FS` (`os.stat`,
  `os.path.getmtime`, `*.stat`), `FLAKY_ORDER` (`os.listdir`, `os.walk`,
  `glob.glob`, `*.iterdir`). `tempfile` is deliberately NOT a bucket: it is
  this repo's blessed self-check pattern, so counting it would flag every good
  demo. The signal is the numeric total; per-bucket counts live only in the
  per-file breakdown.

**Fail-open.** `analyze_file` returns `None` for an unreadable or unparsable
file and the name lands in `skipped`; a missing git/repo yields no files. A
clean tree reports `signals == {}` — an empty measurement, not a fabricated
`0.0` — which the v2 validator accepts (every signal is optional).

**Ledger point.** `record()` validates `signals` with
`validate_test_quality_signals` BEFORE persisting and writes NOTHING when
validation fails (the errors come back instead). On success it appends one
`records.add_entry` `note`, tags `["test-quality", "w29"]`, body
`{"mode": "diff", "diff", "signals", "fileCount", "skipped"}`, title
`test-quality: files=N assertionDensity=… edgeCaseHits=… nullSafetyHits=…
flakinessCandidates=…`. Ledger failure is swallowed (`_record_point`
precedent): observation must not break the observer.

**Observe-only stance.** These are proxies, not proof — they count shapes,
not semantics. No gate check consumes them, no verb exposes them, and no
threshold exists yet; measurement precedes control (the mutation-probe and
security-baseline idiom). Teeth: `w29_observe_first.py`
(`w29:test_quality_ast-selfcheck`, `w29:tq-keys-frozen`,
`w29:tq-parse-failopen`, `w29:tq-counts-honest`).
