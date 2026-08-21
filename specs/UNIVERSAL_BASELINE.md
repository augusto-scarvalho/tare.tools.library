# Universal Baseline Specs

This folder contains the mandatory quality, security, testing, software-engineering, and agent-safety baseline for every repository that adopts the harness.

The baseline is independent of programming language, framework, architecture, deployment model, country, business domain, and product type. It applies to greenfield repositories, existing systems, libraries, services, apps, infrastructure, data pipelines, documentation-heavy projects, and agentic workflows.

## Required files

- `specs/00-universal/code-quality.md` — maintainability, scope control, reviewability, and safe change design.
- `specs/00-universal/software-engineering-guardrails.md` — executable limits for modularity, bounded gates, startup context, and release hygiene.
- `specs/00-universal/canonical-file-protection.md` — protection for canonical agent instruction files against installer/plugin/skill overwrites.
- `specs/00-universal/secure-engineering.md` — secure defaults, abuse resistance, and vulnerability prevention.
- `specs/00-universal/dependency-and-supply-chain.md` — dependency, generator, artifact, build, and provenance risk.
- `specs/00-universal/secrets-and-configuration.md` — secret handling, configuration hygiene, and safe defaults.
- `specs/00-universal/testing-and-quality-gates.md` — proportional validation, gate tiers, SDD evidence, and duplication control.
- `specs/00-universal/coverage-and-regression.md` — regression expectations, coverage posture, exceptions, and release confidence.
- `specs/00-universal/observability-and-operability.md` — diagnosability, runtime behavior, supportability, and recovery.
- `specs/00-universal/data-protection-and-privacy.md` — data minimization, sensitivity, retention, and exposure control.
- `specs/00-universal/api-and-interface-security.md` — external and cross-component boundary safety.
- `specs/00-universal/ai-agent-safety.md` — bounded agent execution, escalation, handoff, and tool-use guardrails.
- `specs/00-universal/structural-discovery.md` — Graphify-first repository discovery, source verification, and search-bloat control.
- `specs/00-universal/agentic-map-reduce.md` — bounded sharding/reduction for large homogeneous tasks.
- `specs/00-universal/agentic-fork-join.md` — bounded multi-perspective branch/join workflows.
- `specs/00-universal/agentic-async-await.md` — durable async task orchestration, await policies, cancellation, recovery, and backpressure.
- `specs/00-universal/sdd-bdd-flow.md` — the SPEC-116 two-door flow: how feature-shaped requests become (or amend) specs, with BDD scenarios as executable evidence.

## Loading policy

Agents should not load every baseline file for every task.

- `cheap` and `scan` tasks usually need only the handoff plus one relevant baseline file.
- `implementation` and `debug` tasks normally need code quality plus testing/regression specs.
- `review` tasks should consider quality, tests, coverage, dependency, interface, and change-management impact.
- `security` tasks should load all security-relevant baseline files for the changed surface.
- `plan` tasks that propose parallelization should load the relevant agentic workflow spec, not all workflow specs by default.

The generated handoff selects the most relevant baseline files by profile to reduce token use. Structural discovery tasks should load `specs/00-universal/structural-discovery.md` before broad repository search.

## Evidence requirements

Non-trivial work should report:

- which universal specs were applied;
- which checks were run or skipped;
- any deviations, risks, or incomplete validation;
- whether escalation to `review` or `security` is needed;
- which validation evidence supports closing a technical-debt item.

Use `HARNESS_RESULT.universalSpecsApplied` and `HARNESS_RESULT.universalSpecDeviations` for this evidence.

## Reference anchors

These specs use established engineering references as anchors, including OWASP ASVS 5.0.0, OWASP Top 10 2025, OWASP API Security Top 10 2023, OWASP Top 10 for LLM Applications 2025, OWASP SCVS, OWASP SAMM, NIST SSDF SP 800-218, Graphify code AST-first structural discovery, Gemini API text/image free tier only, Canonical agent file protection, the Market agent instruction file registry with Snapshot-if-present installer write protection and Market instruction file documentation references, and the Deprecation hygiene gate. They are engineering guardrails, not a formal compliance certification program.

## Catalog consistency

The canonical required-baseline list is `specs/MANIFEST.yaml` and `.harness/project.json`. This document must list every required baseline spec so agents and reviewers do not drift toward stale or incomplete baseline guidance.


## Agent instruction protection anchors

- Market agent instruction file registry
- Snapshot-if-present installer write protection

These anchors require `.harness/protected-files.json` to track both exact protected harness files and market-recognized optional instruction files by pattern.
