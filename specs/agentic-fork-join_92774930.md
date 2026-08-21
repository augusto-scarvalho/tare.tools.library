# Agentic Fork-Join

## Goal

Provide a safe workflow pattern for complex tasks that require multiple specialized perspectives. Fork-join creates bounded branches, lets each branch analyze the same problem through a different lens, and joins the results into one decision-quality synthesis.

## Applies to

Use fork-join when the task is complex but not homogeneous. Examples include pre-release review, architecture migration planning, incident analysis, security review, multi-perspective design review, compatibility analysis, or a major refactor plan.

Do not use fork-join for simple edits, one-dimensional scans, or work that can be handled by a single bounded subagent.

## Invariants

- Branches are independent analysis lanes, not free-form autonomous agents.
- Branches are read-only by default.
- Each branch has a role, scope, allowed reads, forbidden actions, and output schema.
- Join must compare perspectives, not merely concatenate them.
- The join step must surface conflicts, confidence, blockers, and recommended next actions.
- Any implementation after fork-join should be a separate bounded task, usually sequential unless file-disjoint locks are explicit.
- The harness remains the orchestrator. A worker may suggest escalation, but must not spawn additional branches on its own.
- The harness may execute branch packets with controlled concurrency, but concurrency does not authorize edits or additional branches.

## Agent behavior

The planner should choose fork-join when a task benefits from specialized branches such as:

- security and privacy;
- testing and coverage;
- architecture and coupling;
- documentation/spec consistency;
- dependency and supply-chain review;
- runtime/operations readiness;
- compatibility and migration risk.

Branch workers must:

1. Read the branch packet and relevant universal specs.
2. Use Graphify when the branch needs cross-file structure or dependency paths.
3. Verify findings in source/spec/test/config files.
4. Return concise `WORKER_RESULT` output.
5. Avoid editing unless explicitly allowed by workflow policy.

The join worker must:

1. Validate all branch results.
2. Identify agreement, conflict, and missing coverage.
3. Rank findings by severity and decision impact.
4. Produce a `REDUCE_RESULT` suitable for the next harness task or final `HARNESS_RESULT`.

## Validation evidence

A fork-join workflow is valid when it has:

- a `workflow.json` with type `fork-join`;
- a branch list with clear roles and scopes;
- branch worker packets;
- branch results using `WORKER_RESULT`;
- a join result using `REDUCE_RESULT`;
- explicit conflict handling and next-task recommendations.
- if `workflow run` was used, worker lifecycle status and stdout/stderr logs are recorded as runtime artifacts outside Git.

## Escalation triggers

Escalate when:

- branches disagree on high-risk behavior;
- security/privacy findings are high or blocker severity;
- test evidence is missing for critical changed behavior;
- architecture and implementation branches produce incompatible recommendations;
- the join result proposes parallel writes without explicit locks.

## Reference anchors

- `specs/00-universal/agentic-map-reduce.md`
- `specs/00-universal/structural-discovery.md`
- `specs/00-universal/secure-engineering.md`
- `specs/00-universal/coverage-and-regression.md`
- `.harness/workflows/WORKFLOWS.md`
- `schemas/worker-result.schema.json`
- `schemas/reduce-result.schema.json`
