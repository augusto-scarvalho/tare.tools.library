# Project Specs

> Scope: section index for adopting-project specs; this file is an index, not a specification.

Use this folder for product, domain, user, policy, terminology, and business-rule specs that are specific to the adopted project.

This folder should answer questions such as:

- What problem does the project solve?
- Who are the users, actors, systems, or operators?
- What terms have project-specific meaning?
- What behavior must remain true across features?
- What business rules, workflow constraints, or non-technical requirements affect implementation?
- What acceptance criteria are shared by multiple features?

## What belongs here

- Glossaries and domain language.
- Product invariants and business rules.
- User roles, personas, actors, or system participants.
- Regulatory or organizational constraints that are project-specific.
- Cross-feature acceptance criteria.
- Data classification decisions that belong to the project, not the generic harness.

## What does not belong here

- Language/framework coding conventions; use `specs/30-stack/STACK.md` or stack specs.
- Deployment/runbook details; use `specs/90-operations/OPERATIONS.md`.
- Feature-level scenarios; use `specs/40-features/FEATURES.md`.
- Historical implementation notes; use changelogs or decision archives.

## Adoption guidance

For greenfield projects, start with a short project overview spec and expand only when a rule affects implementation. For existing projects, write specs from observed behavior and current contracts instead of inventing idealized rules that the code does not follow yet.
