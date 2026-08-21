# Universal Spec — Testing and Quality Gates

## Goal

Make validation proportional, traceable, and inexpensive enough to run often while still giving strong evidence for risky changes.

## Applies to

All code, test, spec, documentation, configuration, infrastructure, schema, dependency, generated-artifact, and harness changes.

## Invariants

- Specs and acceptance criteria are the source of test intent; implementation tasks should state which behavior is being validated.
- Every non-trivial change needs validation proportional to its risk and blast radius.
- Bug fixes should include regression coverage when practical, or an explicit reason why coverage is deferred.
- Security, auth, data, migration, dependency, configuration, generated-code, and public-interface changes require stronger validation than isolated internal edits.
- Do not mark work complete if relevant checks were not run and no reason is recorded.
- Validation commands live in `.harness/project.json`; they may start empty for greenfield projects, but adoption should create at least one concrete smoke or commit gate as soon as executable code exists.
- Avoid repeating the same expensive gate when no new files or risk signals changed since the previous successful validation.
- Failing, skipped, partial, or manually deferred validation must be captured in `HARNESS_RESULT` and/or `.harness/state/quality-state.json`.
- A greenfield project with no automated tests yet still needs concrete manual validation evidence and a follow-up task to add the first automated gate.

## Gate tiers

| Gate | Intended cost | Purpose | Typical evidence |
|---|---:|---|---|
| `smoke` | seconds | Harness/core sanity and tiny change confidence | JSON/YAML syntax, Python compile for harness scripts, minimal configured commands |
| `spec-pack` | seconds/minutes | Specs/tasks/docs/schema consistency and universal baseline integrity | manifest checks, markdown links, required sections, project validation config sanity |
| `commit` | minutes | Pre-commit confidence for changed code | lint/typecheck/unit tests or equivalent configured checks |
| `feature` | minutes/tens of minutes | Feature/story readiness | targeted unit/integration/contract checks plus coverage expectations when configured |
| `release` | broadest | Merge/release readiness | full configured validation, release scope manifest, security/review gates when applicable |
| `coverage` | project-defined | Coverage reporting or enforcement | configured coverage command and report/threshold notes |

## SDD alignment

- Requirements/specs define behavior before or alongside implementation.
- Tasks link to relevant specs and acceptance criteria.
- Tests derive from acceptance criteria, edge cases, regression history, and universal baseline risks.
- `HARNESS_RESULT.testsRun` records evidence, not just intent.
- `HARNESS_RESULT.universalSpecDeviations` records any gap between the spec baseline and actual validation.
- Quality state records the last gate summary; detailed validation history belongs in `.harness/runs/validation-results.jsonl` and should not be loaded by default.

## Agent behavior

- Run the narrowest useful gate first.
- Escalate to broader gates only after meaningful changes or before handoff/merge.
- Prefer targeted tests for the changed behavior before broad suites.
- Do not hide, skip, delete, or weaken failing tests to make a gate pass.
- Do not claim validation passed unless the command actually ran or the evidence is explicitly manual.
- Record command, status, and relevant failures in `testsRun` and `failedTests`.
- If validation is impossible, explain why, record the risk, and identify the next validation task.
- When changing the harness itself, run at least `smoke`; run `spec-pack` when specs, docs, schemas, routing, or test policy change.

## Validation evidence

Acceptable evidence can include:

- passing configured commands from `.harness/project.json`;
- targeted tests for changed behavior;
- syntax/format/schema checks;
- contract/API/interface tests when public behavior changes;
- coverage command output when configured;
- manual verification with explicit files, inputs, expected outputs, and limitations;
- documented deferral with risk and next step.

Weak evidence:

- “Looks good” with no command or artifact;
- broad claims without command output or inspected files;
- passing unrelated tests;
- stale validation from before the current diff.

## Duplication control

- `smoke` and `spec-pack` may run frequently because they are cheap.
- `commit`, `feature`, `release`, and `coverage` should not be repeated just to produce reassuring logs.
- If the same command appears in multiple gates, document why the duplication is intentional or move it to the narrowest useful gate.
- Hooks should nudge, not repeatedly run expensive validation on every file edit.

## Escalation triggers

Request `review` when:

- validation is incomplete for a risky change;
- a gate fails after reasonable local attempts;
- coverage drops or cannot be measured for critical behavior;
- a task requires creating, changing, or bypassing core gates;
- release/merge readiness is uncertain;
- a test was removed, skipped, weakened, or made less deterministic.

Request `security` when validation touches or fails around auth, secrets, permissions, tenant boundaries, data protection, sandboxing, dependency integrity, cryptography, payments, external writes, or exposed interfaces.

## Reference anchors

- NIST SSDF: verification, vulnerability response, and secure development practices.
- OWASP SAMM: security testing and verification maturity.
- OWASP ASVS: verification-oriented requirements for application behavior and controls.
