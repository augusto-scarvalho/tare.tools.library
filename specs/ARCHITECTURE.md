# Architecture Specs

> Scope: section index for adopting-project specs; this file is an index, not a specification.

Use this folder for current-state architectural decisions and boundaries that agents must preserve or intentionally change.

Architecture specs should help an agent answer:

- What are the major components or modules?
- Which dependencies are allowed or forbidden?
- Where are data, control, trust, and failure boundaries?
- Which interfaces are public, internal, or experimental?
- What consistency, performance, availability, or resilience assumptions matter?
- Which decisions require review before changing?

## Recommended files

- system-overview.md — short current-state component map.
- boundaries.md — module/service/package ownership and dependency direction.
- data-flow.md — important data movement and storage responsibilities.
- integration-contracts.md — stable contracts with external or internal systems.
- architecture-decisions.md — active ADR-style decisions that agents should respect.

## Agent guidance

- Keep architecture specs current-state focused and concise.
- Do not put long history or roadmap speculation here.
- If a task changes a boundary, public contract, persistence model, deployment topology, or trust boundary, escalate to `review`; escalate to `security` if the boundary involves auth, secrets, sensitive data, sandboxing, external writes, or execution.
