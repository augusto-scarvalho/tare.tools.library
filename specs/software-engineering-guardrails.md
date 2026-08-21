# Software engineering guardrails

## Goal

Keep the reusable harness maintainable as it grows by turning modularity, bounded validation, and startup-context economy into executable product contracts.

## Applies to

This spec applies to the universal harness runtime, validation gate, release package, CI matrix, documentation handoffs, and any future internal module under `scripts/harness_lib/`.

## Invariants

- `scripts/harness.py` remains the public CLI compatibility wrapper, not the permanent home for every runtime responsibility.
- Stable, cohesive, dependency-light domains must be extracted behind `scripts/harness_lib/` modules before they become hard to audit.
- Validation gates must stay bounded, diagnosable, and split into smoke gates plus standalone deep fixtures when a check is slow or process-sensitive.
- Root handoff files must stay small shims that point to canonical generated handoff artifacts.
- Required startup reads must remain below the configured required-read token budget; overflow belongs in conditional/deferred reads.
- The harness must not add third-party runtime dependencies merely to enforce these guardrails.
- Universal baseline catalogs must stay synchronized across `specs/MANIFEST.yaml`, `.harness/project.json`, and `specs/00-universal/UNIVERSAL_BASELINE.md`.
- Reference anchors should point to stable public releases; drafts may be tracked as watch items but must not silently replace stable anchors.

## Agent behavior

Agents working on the harness must:

1. Run the engineering guardrail gate before and after modularization work.
2. Prefer extracting cohesive helper modules over adding more unrelated code to `scripts/harness.py` or `scripts/spec_test_gate.py`.
3. Add or update fixtures with the extraction, not after the fact.
4. Keep product-release as a bounded smoke gate and place deep/process-sensitive checks in explicit standalone fixtures.
5. Update baseline indexes when adding/removing universal specs; do not leave only one index current.
6. Update `testing/engineering-guardrails.json` only when a threshold or required-anchor change is intentional and documented in the technical-debt register.
7. Regenerate release integrity artifacts after changing scripts, specs, docs, CI, or manifest files.

## Validation evidence

Minimum evidence for changes touching runtime, validation, handoff, or release boundaries:

```bash
python -m py_compile scripts/harness.py scripts/spec_test_gate.py scripts/harness_lib/*.py
python scripts/harness-test.py --fixture engineering-guardrails
python scripts/harness-test.py workflow --no-project-commands
python scripts/harness-test.py product-release --no-project-commands
python scripts/release_integrity.py verify
```

## Escalation triggers

Escalate to a technical-debt entry when any of the following happens:

- `scripts/harness.py` or `scripts/spec_test_gate.py` exceeds the configured hard line budget.
- Any function exceeds the configured hard function-size budget.
- Required handoff reads exceed the configured required-read token budget.
- A deep fixture is added to an aggregate smoke gate without a timeout/diagnostic reason.
- A root handoff file starts carrying task state instead of pointing to canonical generated artifacts.

## Reference anchors

- `testing/engineering-guardrails.json`
- `scripts/harness_lib/engineering_guardrails.py`
- `docs/HARNESS_ARCHITECTURE.md`
- `docs/WORKFLOW_TOKEN_ECONOMICS.md`
- `testing/CI_MATRIX.md`

## Canonical instruction-file protection

Canonical root instruction and handoff shim files are part of the harness control plane. They must stay protected by `.harness/protected-files.json`, `.harness/protected-files.snapshot.json`, `scripts/harness_lib/protected_files.py`, and the `protected-files` fixture. Installers, skill/plugin sync steps, and adapter setup scripts must preserve these files unless a reviewed harness change explicitly updates the snapshot.


### Market-recognized agent instruction file protection

The protected-file policy covers not only root `AGENTS.md`/`CLAUDE.md` shims, but also market-recognized instruction files and rule directories used by Codex, Claude Code, GitHub Copilot/VS Code, Cursor, Gemini CLI, Cline, Devin/Windsurf, Roo Code, and harness-owned adapter shims. Optional files are snapshot-if-present: installer creation or overwrite is drift until reviewed and added to `.harness/protected-files.snapshot.json`.


## Deprecation hygiene gate

The harness must keep retired aliases and stale active documentation out of the release surface. When a command, config key, module, or policy name is retired, add it to `testing/deprecation-hygiene.json` and keep `deprecation-hygiene` green before packaging. Historical changelog/debt entries may mention retired names; active specs/docs/code/config must not depend on them.
