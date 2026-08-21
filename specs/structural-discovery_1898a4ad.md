# Structural Discovery and Source Verification

## Goal

Make repository navigation efficient, repeatable, secure, and low-bloat by using Graphify-owned local code AST graphing as the first-pass structural discovery layer for non-trivial search, while preserving source files, specs, tests, and Git as the authoritative record. External/API-assisted graph enrichment is optional and cost-controlled.

## Applies to

This spec applies to any task that involves broad repository search, architecture analysis, impact mapping, dependency tracing, call-path exploration, cross-file reasoning, review of unfamiliar code, or investigation of behavior that may span multiple files.

It applies across programming languages, frameworks, operating systems, executors, and project types.

## Invariants

- Graphify code AST-first structural discovery is mandatory when a task requires broad or cross-file repository understanding; Graphify artifacts and adapters are the structural discovery layer.
- Graphify output is an index/navigation aid, not an authoritative source of truth.
- Agents must verify graph findings in the actual source, spec, task, test, or configuration files before editing code, making claims, or closing work.
- Raw broad search should not be the first step when a Graphify code AST graph can be built cheaply or a current Graphify report exists and the task is structural, architectural, or cross-file.
- Raw search remains allowed for exact-string lookup, newly created/unindexed files, log or test-output investigation, source verification after graph use, and cases where Graphify is unavailable or stale.
- Generated graph artifacts must not become canonical harness state.
- External Graphify runtime must be project/operator-managed, never provided by a private executor virtual environment. The built-in Graphify code AST graph builder is dependency-free and may run inside the harness.

## Agent behavior

For non-trivial structural discovery:

1. Check the handoff knowledge-graph status and `.harness/project.json.knowledgeGraph`.
2. If `graphify-out/graph.json` is missing and Graphify code AST build is enabled, build a Graphify code AST graph before broad `grep`, `glob`, or repository-wide file reads.
3. If `graphify-out/GRAPH_REPORT.md` exists, read it before broad search.
4. Use Graphify query/path/explain capabilities, when available, to narrow the search space before opening files.
5. Open the identified source/spec/test/config files and verify the findings directly.
6. Record Graphify/Graphify code AST/Gemini text-image assist usage in `HARNESS_RESULT.contextDiscovery.graphify`.
7. If Graphify is missing, stale, disabled, or not applicable, say so explicitly and proceed with focused source discovery.

Agents must not regenerate, install, or update Graphify during an implementation task unless the task explicitly authorizes tooling setup. Tooling setup is a project/operator action and may require a `docs`, `plan`, or `review` profile depending on scope.

## Validation evidence

A completed non-trivial task should include evidence such as:

- `contextDiscovery.graphify.status`: `used`, `not_available`, `stale`, `not_applicable`, or `skipped`;
- whether the report was read;
- Graphify queries/path/explain operations used, if any;
- the source/spec/test/config files opened to verify graph-derived findings;
- any reason raw search was used before or instead of Graphify.

`spec-pack` should validate that the harness declares Graphify policy, that generated graph artifacts are ignored by default, and that the `HARNESS_RESULT` contract can capture Graphify evidence.

## Escalation triggers

Escalate or pause when:

- the graph is missing but the task requires high-confidence cross-file impact mapping;
- the graph appears stale relative to changed files or the current branch;
- graph findings contradict source files;
- the task requires changing Graphify installation/runtime/configuration;
- a broad review/security task lacks enough graph/source evidence to support conclusions.

Suggested profiles:

- `scan` for graph-assisted repository discovery;
- `plan` for architecture or dependency mapping before implementation;
- `review` when graph/source evidence indicates broad impact;
- `security` when graph paths touch trust boundaries, secrets, auth, network, sandboxing, or external interfaces.

## Reference anchors

- Graph-first, source-verified repository discovery.
- SDD traceability: use specs/tasks/gates as source of intent, not generated indexes.
- NIST SSDF SP 800-218 practices for maintaining development environment integrity and producing verifiable evidence.
- OWASP SAMM practices for architecture, design review, implementation review, and verification activities.


## API/cost controls

- Graphify code AST-first structural discovery is the default because it is offline, deterministic, and dependency-free.
- Gemini API assistance is optional and disabled by default. Projects may enable it only for text/image summarization or semantic enrichment after Graphify code AST/Graphify discovery; never for primary code graph generation.
- Gemini API use must be text/image-only and free-tier-only by default, require explicit opt-in and `GEMINI_API_KEY`, use configurable budget/free-tier models, and never silently switch to paid tier, broad network search, or primary code graph generation.
- Additional cheap API providers (NVIDIA Build via `NVIDIA_API_KEY`, free credits) follow the same rules: disabled by default, explicit opt-in, text/image only, never primary code graphing, configured under `knowledgeGraph.apiAssistedProviders`.
- The discovery wrapper (`python scripts/harness.py discover <paths>`) routes code to the local AST graph and text/images through the cheap provider chain; when no provider is available it refuses with an actionable dependency message. The expensive coder LLM must never become the bulk reader of text/image corpora.
- API-assisted output is untrusted navigation evidence and must be verified against source/spec/test/config files.

## Reference anchors

- Graphify code AST-first structural discovery.
- Gemini API text/image free tier only.
