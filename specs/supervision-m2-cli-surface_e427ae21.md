# SPEC-102 — CLI as a Complete Supervision Surface (Backlog M2)

Supervision series (SPEC-101…105). Depends on SPEC-101 (its failures must already be legible).
Evidence base: `docs/HARNESS_IMPROVEMENT_IDEAS.md` §G2/§D3/§D2/§G1, `docs/SUPERVISION_UI_IDEATION.md` §8.

## Goal

A human can supervise a complete workflow from the terminal alone — see state, preview cost,
approve, spot escalations, diagnose — with no hand-opened JSON. This is the load-bearing phase of
the CLI-first strategy: every future GUI button maps 1:1 to a subcommand delivered here.

## Grounding (research and evidence)

- **CLI-first is a dependency order, not a preference** (`SUPERVISION_UI_IDEATION.md` §8): our
  design premise forbids the GUI from writing state, so any capability a panel needs must exist
  as a subcommand first. CLI improvements also serve agents; a GUI serves only the human.
- **OpenRig CLI pattern:** every command reports outcome + current state + suggested next action,
  designed for dual human/agent consumption. The "next action" line is the future GUI's primary
  button, designed in text first.
- **OpenHarness dry-run:** previewing resolved configuration before execution converts "trust me"
  into "see for yourself" at zero runtime risk. Academic support for consent-at-the-moment-of-risk:
  arXiv 2504.17934.
- **Hive budget enforcement:** spend limits per workflow with refusal, not just reporting. Our
  `token-audit` reports; nothing enforces.
- **MAST (arXiv 2503.13657):** three root-cause classes (specification / inter-agent misalignment
  / task verification), κ=0.88 — legible enough for agents to self-tag at report time.

## Applicability

`scripts/harness.py` subcommands and the result contracts in `.harness/prompts/subagent-contract.md`.
Not the GUI (SPEC-104/105), not evaluator behavior (SPEC-103).

## Scope

In scope:
1. Uniform closing block (outcome + state + next action) on every subcommand.
2. `harness.py escalations` — list pending `requiresEscalation` results from `.harness/runs/`
   with suggested profile and age; `--resolve <id>`.
3. `--dry-run` on `workflow execute` (resolved packets, spawn commands, token estimate) and
   `workflow apply-merge` (merge plan, locks, backups) — print and exit.
4. `budget` per workflow in `workflow-profiles.json`; checked at `start` and between workers;
   refusal past limit with explicit override flag.
5. Optional `failureClass` (`specification` | `inter-agent-misalignment` | `verification`) in
   `HARNESS_RESULT`/`WORKER_RESULT`; `escalations` groups by it.

Out of scope: any rendering; intervention nodes (deferred, needs demand signal); per-item merge
approval (SPEC-103-adjacent, revisit after M3).

## Requirements / invariants

- Closing block is plain text, stable field order, parseable by both humans and agents; JSON
  output modes (if any) gain the same fields, never lose existing ones.
- `escalations` is read-only over `.harness/runs/`; `--resolve` writes only through existing
  state-update paths — no new state files.
- `--dry-run` must not mutate anything: no locks taken, no WF state transitions, no backups made.
- Budget refusal is a refusal, not a warning; override is an explicit flag, logged in run state.
- `failureClass` is optional in the schema: absent field never fails validation of old results.

## Design anchors (verified 2026-07-09)

- Result contracts live in `.harness/prompts/subagent-contract.md` — **protected file** (registry
  `.harness/protected-files.json`). Editing it requires `HARNESS_ALLOW_PROTECTED_WRITE=1` and then
  `python tools/hooks/protect_canonical_files.py snapshot`, else `protected-files:snapshot-match`
  fails. This is intentional friction: the contract change (M2.5) is reviewed, not casual.
- `HARNESS_RESULT` shape in the wild includes `requiresEscalation`, `suggestedProfile` (see
  `HARNESS_ARCHITECTURE.md` supervision matrix); `escalations` consumes exactly these.
- The gate check `static-integrity:workflow-async-id-schema-patterns` asserts runtime ids match
  schemas under `schemas/` — if `failureClass` touches any schema file, keep patterns in sync.
- `workflow token-audit` already computes cost estimates — `--dry-run`'s token estimate reuses it,
  no new estimator.
- Env note for local runs: no system Python; use `HARNESS_PYTHON` (set in
  `.claude/settings.local.json`) or `bash tools/agent-sync/py-run.sh`.

## Acceptance criteria

- [ ] Every `harness.py` subcommand ends with the closing block; `status` and `workflow status`
      verified explicitly.
- [ ] `escalations` lists a seeded pending escalation with profile + age; empty state prints a
      calm "nothing pending" (not an error).
- [ ] `workflow execute --dry-run` on a planned WF prints packets/commands/estimate and leaves
      `workflow-state.json` byte-identical.
- [ ] `apply-merge --dry-run` prints plan/locks/backups, takes no locks, writes nothing.
- [ ] A WF with `budget` under the estimate refuses to start; `--override-budget` starts it and
      the override is recorded.
- [ ] A result carrying `failureClass` round-trips; one without it still validates.

## Test strategy

- Behaviors: each acceptance criterion is one scenario; dry-run idempotence proven by hashing
  state files before/after.
- Edge cases: `escalations` with corrupted run JSON (skip + warn, don't crash); budget exactly at
  the limit (allowed); unknown `failureClass` value (rejected with legible error per SPEC-101).
- Regression risks: output parsers in fixtures; `cli-contract.json` golden
  (`testing/golden/cli-contract.json`) — check whether new flags/commands must be registered.
- Coverage impact: enforced for the new subcommand paths.

## Validation (MVP gate)

Scripted scenario: workflow with one forced escalation and a low budget cap. Operator must — from
the terminal only — hit the budget refusal, override deliberately, preview via `--dry-run`,
execute, find the escalation via `escalations`, re-spawn with the suggested profile, finish. No
JSON opened by hand. Then `python scripts/harness-test.py commit` green.

## Universal baseline impact

`specs/00-universal/agentic-map-reduce.md`, `agentic-fork-join.md` (workflow semantics unchanged),
`observability-and-operability.md`, `api-and-interface-security.md` (no new write paths).

## Escalation triggers

Contract-file edits beyond adding optional fields; any need for a resident process; budget
semantics conflicting with an existing profile — human decision.
