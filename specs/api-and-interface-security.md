# Universal Spec — API and Interface Security

## Goal

Secure boundaries where external or cross-component input enters the system, regardless of interface style.

## Applies to

HTTP APIs, RPC, GraphQL, CLIs, SDKs, file formats, UI forms, event streams, webhooks, plugins, extension points, model/tool calls, import/export flows, uploads/downloads, and internal service contracts.

## Invariants

- Validate inputs and outputs against an explicit or inferred contract.
- Authorization must be enforced at the object/resource/action level when relevant.
- Prevent mass assignment, over-posting, over-fetching, and accidental exposure of internal fields.
- Bound pagination, query limits, recursion, file sizes, payload sizes, batch sizes, and streaming output.
- Do not expose internal errors, stack traces, sensitive fields, or implementation details through public interfaces.
- Preserve backwards compatibility unless contract changes are explicit and documented.
- Changes to public interfaces require docs/spec/task updates.
- Consider rate limiting, throttling, replay protection, idempotency, and concurrency controls where abuse or duplication is plausible.
- Treat tool/plugin/model-call interfaces as security boundaries, not just function calls.

## Agent behavior

- Identify changed interfaces in `HARNESS_RESULT`.
- Record whether contract docs/specs were updated or intentionally unchanged.
- Add or request tests for authorization, validation, error handling, limits, and compatibility.
- Escalate if the interface affects auth, sensitive data, payments, filesystem, network, execution, or tenant boundaries.

## Validation evidence

Use available checks:

- contract/schema validation;
- focused tests for valid/invalid inputs and authorization;
- error-output inspection;
- backwards-compatibility review;
- abuse-limit/idempotency checks where relevant.

## Escalation triggers

Request `security` or `review` when changing:

- public API routes, CLI commands, event schemas, plugin interfaces, upload/download flows;
- authentication/authorization on an interface;
- object-level access, tenant boundaries, pagination, filters, exports, imports, bulk operations;
- model/tool invocation surfaces or external callbacks/webhooks.

## Reference anchors

- OWASP API Security Top 10: API authorization, authentication, and exposure risks.
- OWASP ASVS: interface validation, encoding, session, and access-control controls.
- OWASP Top 10 for LLM Applications: tool invocation and prompt/input boundary risks for AI-enabled systems.
