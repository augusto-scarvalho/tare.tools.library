# Universal Spec — Secrets and Configuration

## Goal

Keep secrets out of source control and make configuration explicit, safe, portable, and reviewable.

## Applies to

Environment variables, config files, CI/CD variables, credentials, keys, tokens, certificates, service accounts, local settings, examples, logs, docs, tests, fixtures, and runtime manifests.

## Invariants

- Never commit real secrets, tokens, credentials, private keys, session cookies, production credentials, or credential-bearing URLs.
- Example values must use placeholders that cannot be mistaken for real secrets.
- Do not print secrets in logs, tests, traces, telemetry, screenshots, exceptions, or `HARNESS_RESULT`.
- Configuration defaults must be safe for local development and must not accidentally expose production-like behavior.
- Required configuration should be validated before use when practical.
- Environment-specific settings belong in local/user/runtime config, not hardcoded source.
- Do not weaken `.gitignore`, secret scanning, permission boundaries, or config safety without review.
- Prefer least-privilege credentials and explicit scopes.

## Agent behavior

- Redact any sensitive values encountered.
- Add `.example`, template, or documentation files with placeholders when introducing configuration.
- Do not inspect private/local secret stores unless explicitly required and permitted.
- If secret exposure is suspected, stop and request `security`; do not quote the secret back.

## Validation evidence

Use available checks:

- secret scanning, if configured;
- grep/manual inspection for newly added config/docs/log examples;
- startup/config validation tests;
- CI or deployment config validation.

## Escalation triggers

Request `security` when:

- adding/changing `.env`, credentials, keys, tokens, certificates, secret stores, service accounts;
- touching deployment config, CI variables, cloud permissions, production endpoints;
- changing how secrets are loaded, stored, encrypted, rotated, masked, or logged;
- finding a suspected committed secret.

## Reference anchors

- OWASP ASVS: secrets, authentication, cryptographic storage, and configuration expectations.
- NIST SSDF: protecting development and deployment credentials.
