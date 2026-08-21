# Operations Specs

> Scope: section index for adopting-project specs; this file is an index, not a specification.

Use this folder for runtime, deployment, release, observability, migration, backup, incident, and support constraints.

Operations specs should make production-impacting changes explicit before agents edit deploy, infra, data, or runtime behavior.

## What belongs here

- Deployment environments and promotion rules.
- Runtime configuration and environment-variable policy.
- Observability expectations: logs, metrics, traces, health checks, audit events.
- Backup, restore, migration, rollback, and data-retention rules.
- Release checklists and release-scope definitions.
- Incident response and operational runbooks.
- Resource constraints and performance budgets when relevant.

## Agent guidance

- Escalate to `review` for deployment, migration, CI/CD, persistence, scheduling, or runtime-topology changes.
- Escalate to `security` when operational changes affect secrets, permissions, network exposure, sandboxing, sensitive data, or external writes.
- Keep large logs, generated reports, and environment-specific secrets out of this folder. Store only concise, reusable guidance and links to ignored/generated evidence when needed.
