# Universal Spec — Secure Engineering

## Goal

Prevent avoidable vulnerabilities while remaining independent of language, platform, and application type.

## Applies to

Any change involving untrusted input, identity, permissions, data access, storage, network access, command execution, plugins, file paths, serialization, parsing, cryptography, or runtime isolation.

## Invariants

- Treat external input as untrusted until validated, constrained, or safely encoded for its destination.
- Authorization must fail closed and be checked at the resource/action level where applicable.
- Authentication, session, token, permission, and identity changes require explicit review.
- Do not implement custom cryptography, token formats, password storage, or signing protocols when maintained primitives exist.
- Do not weaken security controls to make tests pass.
- Do not expose secrets, tokens, stack internals, sensitive business data, or personal data in logs/errors/output.
- Do not add network exposure, shell execution, dynamic evaluation, deserialization, plugin loading, file-system access, or sandbox relaxation without explicit scope.
- Use least privilege for users, processes, files, tokens, roles, services, CI jobs, containers, and agents.
- Security-sensitive defaults must be safe by default.
- Prefer allow-lists and explicit constraints over broad block-lists.

## Agent behavior

- State security assumptions in `HARNESS_RESULT`.
- Mark unresolved assumptions as deviations.
- Do not infer that a missing security requirement means no security requirement exists.
- Stop and request escalation when security impact is plausible but under-specified.

## Validation evidence

Use the strongest available evidence for the project:

- focused tests for authorization, validation, and failure paths;
- project SAST/dependency/secrets/container scans when configured;
- manual threat notes for greenfield or early-stage projects;
- explicit statement of checks not available yet.

## Escalation triggers

Request `security` when touching:

- auth, sessions, tokens, roles, permissions, identity, OAuth, SSO, API keys;
- cryptography, signing, hashing, certificates, passwords, secrets;
- payments, financial data, personal data, regulated data;
- containers, sandboxing, networking, exposed services, CI/CD permissions;
- command execution, dynamic code execution, plugin loading, deserialization;
- file access, uploads/downloads, user-controlled paths, tenant boundaries.

## Reference anchors

- OWASP Top 10: awareness baseline for common application risks.
- OWASP ASVS: verification requirements for application security.
- OWASP API Security Top 10: authorization, authentication, and object/property exposure risks.
- NIST SSDF: secure design and implementation practices.

## Agent control-plane file protection

Agent instruction files and harness prompt contracts are security-sensitive control-plane inputs. Do not let plugin installers, skill sync, MCP setup, or executor adapters overwrite them silently. Any change to protected instructions must be reviewed as source, reflected in the protected-file snapshot, and validated through the `protected-files` and `engineering-guardrails` fixtures.


### Market-recognized agent instruction file protection

The protected-file policy covers not only root `AGENTS.md`/`CLAUDE.md` shims, but also market-recognized instruction files and rule directories used by Codex, Claude Code, GitHub Copilot/VS Code, Cursor, Gemini CLI, Cline, Devin/Windsurf, Roo Code, and harness-owned adapter shims. Optional files are snapshot-if-present: installer creation or overwrite is drift until reviewed and added to `.harness/protected-files.snapshot.json`.
