# Agentic Map-Reduce

## Goal

Provide a safe workflow pattern for repository-scale or document-scale work that cannot fit comfortably in one agent context window. The pattern splits a large homogeneous task into bounded shards, runs the same analysis contract against each shard, and reduces the normalized results into a compact synthesis.

## Applies to

Use this spec when a task must process many files, specs, tasks, logs, documents, modules, packages, or Graphify communities with the same evaluation lens. Common examples include codebase-wide quality review, security triage across many modules, large documentation consistency checks, coverage-gap inventory, dependency review, API inventory, or migration impact analysis.

Do not use map-reduce for small edits, single-file changes, tasks requiring one coherent design decision, or tasks where workers would need to edit overlapping files.

## Invariants

- Map-reduce is read-only by default.
- Workers receive small work packets, not the full project context.
- Worker outputs must use `WORKER_RESULT`, not a full `HARNESS_RESULT`.
- Reducers must deduplicate, group, and rank findings instead of concatenating raw worker outputs.
- Source files remain authoritative. Graphify may guide splitting and discovery, but workers must verify relevant findings in source/spec/test/config files.
- Parallel writes are forbidden unless the harness controlled-write policy explicitly enables file-disjoint locks, isolated workspaces, merge planning, rollback, and validation for the workflow.
- A reducer must preserve conflicts and disagreement; it must not hide uncertainty.
- A workflow must have finite limits: max workers, max rounds, max output size, timeout, and explicit escalation after partial/failed rounds.
- The harness may execute worker packets with controlled concurrency, but concurrency does not grant write access.

## Agent behavior

The planner should propose map-reduce only when the task is too broad for a normal bounded subagent. It should choose shards by one or more of:

- Graphify communities or dependency clusters;
- source roots, test roots, docs roots, spec roots, or task roots;
- changed-file groups;
- feature/domain folders;
- package/module boundaries;
- explicit user-provided item lists.

Workers must:

1. Read only the worker packet, required specs, and the shard's relevant source files.
2. Use Graphify before broad shard discovery when applicable.
3. Avoid editing files unless the worker packet explicitly allows it.
4. Return a concise `WORKER_RESULT` JSON file.
5. Reference evidence by path and short reason instead of pasting long content.

Reducers must:

1. Validate worker result shape before synthesis.
2. Deduplicate repeated findings.
3. Rank blockers and high-risk issues first.
4. Preserve conflicts, partial coverage, and failed shards.
5. Emit a `REDUCE_RESULT` plus a final short recommendation for the harness.

## Validation evidence

A map-reduce workflow is valid when it has:

- a `workflow.json` describing type, task, policy, and limits;
- a `shards.json` listing bounded shards;
- one worker packet per shard;
- one normalized worker result per completed shard;
- a reducer result with counts, grouped findings, conflicts, blockers, and next tasks;
- lifecycle evidence for planning, queued/running/completed worker states, validation, reduction, and finalization.
- if `workflow run` was used, stdout/stderr logs remain runtime artifacts outside Git.

## Escalation triggers

Escalate to `review` or `security` when map-reduce discovers:

- findings touching authentication, authorization, secrets, privacy, payments, or destructive operations;
- conflicting worker conclusions about the same critical component;
- stale or missing Graphify data for architecture-wide conclusions;
- failed shards that cover high-risk paths;
- any proposed write step that would modify overlapping files.

## Reference anchors

- `specs/00-universal/agentic-fork-join.md`
- `specs/00-universal/structural-discovery.md`
- `specs/00-universal/testing-and-quality-gates.md`
- `.harness/workflows/WORKFLOWS.md`
- `schemas/worker-result.schema.json`
- `schemas/reduce-result.schema.json`
