# Universal Spec — Code Quality

## Goal

Keep changes easy to understand, review, test, and maintain in any codebase.

## Applies to

All tasks that create, edit, delete, generate, or reorganize source code, tests, configuration, scripts, docs, specs, schemas, infrastructure, or generated artifacts.

## Invariants

- Prefer the smallest change that satisfies the task and acceptance criteria.
- Preserve public behavior and contracts unless the task explicitly changes them.
- Keep one responsibility per module/function/class/config block where practical.
- Make names reflect domain intent, not implementation accidents.
- Avoid hidden side effects, implicit global state, and surprising dependency direction.
- Handle expected errors explicitly; do not silently swallow failures.
- Do not mix broad refactors with feature/bugfix work unless the task is a refactor.
- Do not add generated files, caches, local logs, build outputs, or runtime state to source control unless explicitly required.
- Remove dead code only when it is clearly safe and inside scope.
- Prefer explicit tradeoffs over clever code. If a tradeoff matters, record it.

## Agent behavior

- Explain scope in `HARNESS_RESULT.summary`.
- List any intentionally preserved debt or deferred cleanup in `universalSpecDeviations`.
- Avoid touching unrelated files just to satisfy personal style preferences.
- If a requested change requires a broader design change, stop or request escalation instead of smuggling a refactor into the diff.

## Validation evidence

At least one of the following should be present for non-trivial changes:

- configured test/lint/typecheck/build gate;
- focused manual check with concrete files/paths;
- review note explaining why no executable validation exists yet.

## Escalation triggers

Request `review` when:

- many modules or public contracts are affected;
- the smallest safe change is no longer small;
- compatibility is uncertain;
- tests cannot cover meaningful risk;
- generated artifacts or formatting churn dominate the diff.

## Reference anchors

- NIST SSDF: prepare, protect, produce, and respond practices.
- OWASP ASVS: verification-oriented security and quality requirements.
- OWASP SAMM: risk-tailored secure software process.
