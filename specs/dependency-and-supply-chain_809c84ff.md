# Universal Spec — Dependency and Supply Chain

## Goal

Keep dependencies, build inputs, generated code, and third-party execution surfaces deliberate, auditable, and low-risk.

## Applies to

Packages, lockfiles, package managers, build tools, CI actions, plugins, templates, generators, container images, binary downloads, model/provider integrations, remote scripts, vendored code, and generated artifacts.

## Invariants

- Do not add dependencies for trivial functionality.
- Prefer maintained dependencies with clear ownership, release history, licensing, and ecosystem fit.
- Preserve package-manager conventions and lockfiles.
- Do not remove, regenerate, or mass-update lockfiles unless explicitly required.
- Do not run unknown installers, remote scripts, post-install hooks, or binary downloads without review.
- Treat build tooling, CI plugins, code generators, container base images, and transitive dependency churn as supply-chain risk.
- New runtime dependencies need a short justification and validation path.
- Pin or constrain versions according to the project ecosystem.
- Avoid depending on abandoned, unofficial, typo-squatted, or single-maintainer packages for critical paths unless reviewed.

## Agent behavior

- Record new or changed dependencies in `HARNESS_RESULT.summary`.
- Include lockfile/package-manager changes in `filesChanged`.
- Put unresolved license, maintenance, binary, or install-script concerns in `universalSpecDeviations`.
- Prefer asking for `review` over silently accepting opaque generated changes.

## Validation evidence

When tooling exists, run or request:

- package manager install/lockfile validation;
- dependency audit or vulnerability scan;
- license check for production/commercial projects;
- build/test gate after dependency changes;
- diff review for generated files.

## Escalation triggers

Request `review` or `security` when:

- adding runtime dependencies or changing package manager behavior;
- changing lockfiles, CI actions, plugins, generators, native modules, binaries, or container base images;
- introducing remote installers, post-install scripts, model/tool providers, or vendored code;
- dependency changes affect auth, crypto, parsing, deserialization, sandboxing, networking, or build/release.

## Reference anchors

- OWASP SCVS: supply-chain risk and component verification.
- NIST SSDF: protect code and verify third-party components.
- OWASP SAMM: governance and risk-tailored security practices.

## Installer protection for agent instruction files

Any dependency, plugin, skill, MCP, template, or script installer that can write repository files must treat `AGENTS.md`, `CLAUDE.md`, root handoff shims, and harness prompt contracts as protected files. Capture a snapshot with `tools/hooks/protect_canonical_files.py snapshot` before setup and verify it with `tools/hooks/protect_canonical_files.py check` after setup. A drift failure is a supply-chain/security finding, not a normal post-install side effect.


### Market-recognized agent instruction file protection

The protected-file policy covers not only root `AGENTS.md`/`CLAUDE.md` shims, but also market-recognized instruction files and rule directories used by Codex, Claude Code, GitHub Copilot/VS Code, Cursor, Gemini CLI, Cline, Devin/Windsurf, Roo Code, and harness-owned adapter shims. Optional files are snapshot-if-present: installer creation or overwrite is drift until reviewed and added to `.harness/protected-files.snapshot.json`.
