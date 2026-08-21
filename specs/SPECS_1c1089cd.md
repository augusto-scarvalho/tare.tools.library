# Specs Directory

This directory defines the behavior, constraints, and validation expectations that agents must use when changing a project.

Specs are intentionally split by stability and scope so agents can load only what matters for the current task:

```text
specs/
  00-universal/        # mandatory baseline for every project
  10-project/          # product/domain terminology, actors, rules, and constraints
  20-architecture/     # boundaries, components, data flow, integration contracts
  30-stack/            # language/framework/runtime/package-manager conventions
  40-features/         # feature behavior, scenarios, acceptance criteria
  90-operations/       # deployment, observability, migration, backup, release
```

## How agents should use this directory

- Always inherit `specs/00-universal/` for non-trivial work.
- Load project-specific specs only when the task, changed files, or handoff points to them.
- Prefer linking exact spec files in task files instead of asking agents to read the whole tree.
- Do not weaken universal requirements from a project spec without recording a decision in `.harness/context/DECISIONS.md`.
- Keep specs current-state focused. Historical notes belong in changelogs, ADR archives, or external project documentation.

## Adding a spec

1. Copy `SPEC_TEMPLATE.md`.
2. Place the new file in the most specific applicable folder.
3. Add acceptance criteria and validation expectations.
4. Reference applicable universal specs.
5. Update `specs/MANIFEST.yaml` when the spec becomes part of the required project baseline.
