# SPEC-101 — Legible Failures (Backlog M1)

Part of the supervision series (SPEC-101…105), scheduled in `docs/IMPLEMENTATION_BACKLOG.md`.
Evidence base: `docs/HARNESS_IMPROVEMENT_IDEAS.md` §F4/§F2.

## Goal

Every failure message the harness emits — gate checks, hook blocks, workflow CLI refusals —
answers three questions in ≤3 lines: *what failed*, *which policy/state caused it*, *what is the
sanctioned fix (exact command when one exists)*. An agent or human reading a failure must be able
to remediate from the message alone, with zero repository exploration.

## Grounding (research and evidence)

- **Local incident (2026-07-09):** the `py-run.sh` interpreter error already named a remediation
  (`set HARNESS_PYTHON`) yet diagnosis still cost a full exploration cycle, because it omitted the
  *cause* (MS-Store alias stubs failing the version probe) and the *forbidden* fallback. Partial
  self-announcement is still a mute error. Token economics: a complete error ≈ 50 tokens of
  reading; a mute one ≈ an entire Explore cycle.
- **Anthropic long-running-apps article:** harness legibility work compounds — every later
  component is built and debugged on top of failure output.
- **Dark-patterns oversight study (arXiv 2509.10723):** over-verbose alerts create cognitive-load
  failure modes; hence the 3-line cap, not a manual.

## Applicability

All failure paths in `scripts/spec_test_gate.py`, `scripts/harness.py` workflow refusals, and
`tools/hooks/*` block messages. Does not cover agent-authored messages (those are contract
territory, SPEC-103).

## Scope

In scope:
- Remediation map keyed by check-name prefix, consulted by the gate's single output choke point.
- Cause/fix lines on workflow CLI refusals (locks, blocked reduce, missing approval token).
- Fixture failure details stating expected vs. actual contract.
- Wording audit for near-miss ambiguity in hook messages and `.harness/prompts/`.
- `OPERATOR_GUIDE.md` §8 updated to state fixes are inline; table demoted to fallback index.

Out of scope: new checks, new gates, GUI rendering (SPEC-104/105), message localization.

## Requirements / invariants

- Fail-line format: `✗ <name>: fail — <detail>` gains a suffix ` | fix: <command>` when the map
  has an entry. Pass/skip lines unchanged.
- The map is data (dict of name-prefix → command), not per-check code; unknown prefixes degrade to
  today's output.
- ≤3 lines per failure. No stack traces in operator-facing refusals.
- Exit codes unchanged everywhere.

## Design anchors (verified 2026-07-09 — re-verify lines before editing)

- `scripts/spec_test_gate.py:66` — `result(name, status, detail)` prints every one of the ~266
  check outcomes. Sole edit point for M1.1. Check names are namespaced (`protected-files:*`,
  `runtime-portability:*`, `release-hygiene:*`, `json:*`…).
- Seed the map from the troubleshooting table at `docs/OPERATOR_GUIDE.md` §8 — proof the
  remediation knowledge exists but lives far from the error.
- `tools/hooks/protect_files.py:126-130` — already emits per-path `replacementPattern` notes;
  reference implementation for message style. Keep the literal prefix
  `Blocked protected file write: ` and exit code 2 (fixture relies on the code, not the text —
  `spec_test_gate.py:1567` asserts `returncode != 0` only).

### Landmines

- `check_runtime_portability` (`spec_test_gate.py:648-654`) fails if these literal substrings
  appear in `py-run.sh`, `AGENT_SYNC.md`, `README.md`, `AGENTS.md`, `docs/RUNTIME_PORTABILITY.md`:
  `codex-runtimes`, `codex-primary-runtime`, `.cache/codex`, `Microsoft Store execution-alias`,
  `bundled Codex runtime`. Never write these into remediation text destined for those files.
- `tools/agent-sync/py-run.sh` is in the protected registry: edits exit 2 via hook. It should not
  need changes in M1; if it ever does: `HARNESS_ALLOW_PROTECTED_WRITE=1`, then regenerate
  `.harness/protected-files.snapshot.json` via `tools/hooks/protect_canonical_files.py snapshot`,
  or `protected-files:snapshot-match` fails.
- The bare `spec_test_gate.py` run is the **smoke** gate; `protected-files:*` checks live in the
  fixture (`--fixture protected-files`) and the workflow/product-release gate sets. Verify against
  the right gate.

## Acceptance criteria

- [ ] `protected-files:snapshot-match` failure line carries
      `fix: python tools/hooks/protect_canonical_files.py snapshot`.
- [ ] `release-hygiene:*` failures carry the `release_integrity.py generate` remediation.
- [ ] `workflow unlock` hint appears in the lock-refusal message; blocked-reduce refusal names
      `workflow status` and `collect --recover`.
- [ ] Missing-approval-token refusal names the exact token and the doc that governs it.
- [ ] No failure message exceeds 3 lines.
- [ ] All exit codes identical to pre-change behavior.

## Test strategy

- Behaviors: break the snapshot deliberately → assert fix line; lock a workflow → assert unlock
  hint; run gate with no failures → output byte-identical to today for pass/skip lines.
- Edge cases: check name matching no prefix (no fix line, no crash); multiple failures (each gets
  its own fix line).
- Regression risks: fixtures that parse gate output; anything asserting exact stderr.
- Coverage impact: informational.

## Validation (MVP gate for the milestone)

Deliberately break the protected-files snapshot and one workflow lock. A fresh agent must fix
both **using only the error output** — if it greps gate source or reads docs to remediate, M1 is
not done. Then: `python scripts/harness-test.py spec-pack` and `--fixture protected-files` green.

## Universal baseline impact

`specs/00-universal/observability-and-operability.md` (failure legibility),
`specs/00-universal/testing-and-quality-gates.md` (gate output contract).

## Escalation triggers

Any need to change exit codes, check names, or fixture assertions → stop and escalate; those are
external contracts.
