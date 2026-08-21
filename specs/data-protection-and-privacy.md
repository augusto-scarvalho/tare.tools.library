# Universal Spec — Data Protection and Privacy

## Goal

Minimize and protect sensitive data even before a project-specific regulatory model is known.

## Applies to

Personal data, credentials, financial data, health data, private messages, user content, telemetry identifiers, proprietary data, logs, analytics, exports, backups, test fixtures, migrations, and model/agent context.

## Invariants

- Collect, store, expose, and retain only data needed for the task.
- Treat personal data, credentials, financial data, health data, private communications, telemetry identifiers, user content, and proprietary data as sensitive.
- Do not log or echo sensitive data unless explicitly required, minimized, and redacted.
- Preserve tenant/account/user boundaries.
- Avoid exposing internal identifiers when they create enumeration, correlation, or authorization risk.
- Do not add analytics, tracking, telemetry, exports, retention, deletion, or anonymization behavior without explicit scope.
- Test data and fixtures must not contain real personal or confidential data.
- Agent handoffs must not include secrets or unnecessary sensitive data.

## Agent behavior

- Identify new or changed sensitive data fields in `HARNESS_RESULT`.
- Redact sensitive examples.
- Request `security` when data handling scope is unclear.
- Do not infer compliance requirements; record uncertainty and let the project define stricter rules.

## Validation evidence

Use available checks:

- tests for access boundaries, redaction, deletion/export behavior when applicable;
- review of logs/errors/examples/fixtures;
- schema or migration review for sensitive fields;
- manual privacy impact note for early-stage projects.

## Escalation triggers

Request `security` when touching:

- personal, financial, health, credential, private, tenant, or proprietary data;
- analytics, telemetry, tracking, profiling, exports, deletion, retention, anonymization;
- data migrations or schema changes involving sensitive fields;
- cross-account, cross-tenant, or bulk data access.

## Reference anchors

- OWASP ASVS: data protection, privacy, and access-control verification.
- OWASP API Security Top 10: object/property exposure and authorization risks.
- NIST SSDF: secure handling of development and operational data.
