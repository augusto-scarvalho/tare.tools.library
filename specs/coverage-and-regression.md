# Universal Spec — Coverage and Regression

## Goal

Keep coverage meaningful and risk-focused without forcing a single language, framework, metric, or threshold onto every project.

## Applies to

Any task that adds, changes, removes, or validates behavior; fixes bugs; changes tests; changes coverage tooling; changes public interfaces; changes security/privacy logic; or prepares a feature/release gate.

## Invariants

- Coverage is evidence, not a goal by itself. High coverage does not replace behavioral validation, review, or security analysis.
- Regression coverage should be added for fixed bugs whenever practical.
- Critical behavior needs stronger coverage evidence than low-risk internal helpers.
- Coverage thresholds, commands, report paths, and enforcement gates must be configured per project in `.harness/project.json`.
- Coverage exceptions must be explicit, scoped, and recorded in `HARNESS_RESULT.universalSpecDeviations`.
- Do not lower thresholds, ignore files, snapshot broad outputs, or delete assertions just to pass a gate.
- Generated code, vendored code, fixture-only files, and prototypes may be excluded only if the project policy says so.

## Coverage policy model

Projects should configure coverage gradually:

1. `disabled`: no executable code or no coverage tool yet; manual validation and follow-up task required.
2. `informational`: coverage command runs but failures do not block gates.
3. `enforced`: configured thresholds block selected gates such as `feature` or `release`.
4. `risk-targeted`: critical modules or changed files have stricter expectations than the global project average.

The harness template starts with coverage disabled so it remains language-agnostic. Adopted projects should enable project-specific commands when tooling exists.

## Agent behavior

- For bug fixes, identify the missing regression and add or request a test that fails before the fix when practical.
- For new features, map tests to acceptance criteria and edge cases.
- For refactors, prefer characterization tests or existing suite evidence that behavior is unchanged.
- For security/privacy changes, include negative tests where feasible: unauthorized, malformed, boundary, failure, and redaction paths.
- For docs-only changes, coverage usually does not apply; say so rather than loading coverage tooling.
- If coverage cannot run, record why and whether this is acceptable for the current gate.

## Validation evidence

Good evidence can include:

- configured coverage command output;
- changed-file or package-level coverage report;
- regression test added for a bug;
- acceptance criteria mapped to tests;
- contract/API test covering public behavior;
- manual note that coverage is not yet configured plus a concrete task to add it.

## Escalation triggers

Request `review` when:

- coverage threshold, ignore/exclude list, or report command changes;
- tests are deleted, skipped, weakened, or converted to snapshots without justification;
- coverage drops for changed or critical behavior;
- the project has executable code but no configured test/coverage path;
- a release gate has no coverage evidence and no accepted exception.

Request `security` when coverage gaps affect auth, permissions, secrets, tenant/data boundaries, cryptography, payments, sandboxing, dependency integrity, or external writes.

## Reference anchors

- NIST SSDF: verify software security and respond to vulnerabilities.
- OWASP SAMM: security testing and verification maturity.
- OWASP ASVS: verification of security controls, error handling, sessions, authorization, and interface behavior.
