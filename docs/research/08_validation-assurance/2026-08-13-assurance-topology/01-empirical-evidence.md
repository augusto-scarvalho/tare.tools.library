# 1 — Empirical evidence and diagnosis

**Status:** `RESEARCH / INTERNAL EMPIRICAL EVIDENCE`

**Parent:** [Assurance Topology](README.md)

## Operational case

The empirical seed is the sequence PR #16 → Issue #17 in the private canonical repository. After the baseline repairs allowed CI to reach the aggregate scenario gate, all three OSes went red. The investigation showed that `scenario FAIL` did not have a single interpretation.

The same treasury contained:

- CURRENT regressions;
- conformance/architecture checks;
- `NOT_CURRENT` negative evidence by design;
- candidate/qualification experiments;
- platform fixtures;
- process/crash/recovery probes;
- system/integration scenarios;
- historical fixtures incompatible with newer contracts.

CI-REGRESSION-01 was created to classify before fixing or deciding blocking semantics.

## Negative evidence ≠ candidate regression

P2/P3/P5 already contained intentionally negative checks for as long as capabilities remained `NOT_CURRENT`. The old aggregate treated every non-zero rc as a blocking regression. The corrective now preserves the real FAIL and only recognizes `expected-negative` when declaration + failed-count consistency + reviewed policy row coincide. Ordinary/legacy failure, unknown tag, malformed policy and partial declaration remain fail-closed.

Independent audit accepted the mechanism only for the exact subject and recorded a limit: policy bytes modifiable by the candidate do not become Authority. Future autonomous promotion will need trusted provenance for changes that alter blocking semantics.

## Observed fixture debt

Examples were found of:

- governance fixtures predating current receipts/producer semantics;
- fixture artifacts that did not exercise CURRENT settlement;
- incomplete import closure;
- incorrect POSIX process-group;
- path string equality instead of resolved identity;
- missing executable bit;
- worktree against read-only Git state;
- stat metadata confused with content mutation;
- test pins pointing to the old owner after module extraction;
- generated projection drift;
- fault injection with timing-sensitive behavior.

Therefore some reds were product defects, others stale fixtures, others negative evidence and others reliability evidence that was still inconclusive.

## Structural diagnosis

At the studied checkpoint, every PR runs Ubuntu/Windows/macOS on Python 3.13, each leg with compile → product-release → spec-pack → aggregate scenarios + many standalone fixtures; soak runs separately. `.harness/project.json` describes `scenarios` as all `testing/scenarios/*.py` aggregated.

At the same time, `testing/QUALITY_GATES.md` already recommends the narrowest gate capable of producing new information and separates bounded release hygiene from deep fixtures/soak.

**Research finding:** the incumbent preserves a valuable evidence treasury, but PR CI grew until it operates as an almost universal system-qualification matrix.

## Mandatory contrary evidence

A future publication must also preserve falsified hypotheses, residual reds, nondeterminism, implementer claims corrected by the audit, corrective cost and failures detected only by the full treasury. Without this, the study would suffer from survivorship/favorable-closure bias.

The private canonical repository remains the source of truth; this document does not replace Git/code/gates.
