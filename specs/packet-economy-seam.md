# SPEC-141 — Packet-economy compose seam (compact-output env + per-delegation budget)

Status: SPEC-141, proposed 2026-07-13 (acceptance: `testing/scenarios/pes_packet_economy.py`).

## Goal

Give `spawn_command` one place that folds the remaining per-profile token levers
into the spawn path. SPEC-140 tied the resource allowlist into `build_prompt`;
this seam composes the OTHER two levers — compact agent output (a spawn env var)
and a per-delegation token budget — through a single pure function,
`packet_economy.compose_spawn`. It does not move SPEC-140's resource line and does
not add an output cap (a later shard). Both levers are opt-in per profile so a
profile without a `tokenEconomy` block spawns byte-identically to before.

## Applicability

Applies to `scripts/harness_lib/packet_economy.py` (new: `compose_spawn` +
`budget_for_agent`), `scripts/harness.py` `spawn_command` (calls the seam, threads
the composed env through its return, prints the over-budget WARN) and its sole
caller `cmd_spawn`, `.harness/routing/task-profiles.json` (the existing
`tokenEconomy` blocks gain `compactOutput` + `delegationBudgetTokens`), and the
`delegation-cost-outlier` threshold in `scripts/harness_lib/self_review*.py`. It
does NOT touch `build_prompt`'s resource line, `common.emit` (reused as-is), the
cost-metrics ledger, or add `outputCapChars` (a later shard owns the cap).

## Requirements / invariants (numbered, testable)

1. **Pure compose over its args, reusing existing levers.** `compose_spawn(root,
   profile_name, profile, task)` returns `{"env": {...}, "budget": {"estTokens",
   "budgetTokens", "over"}}` computed only from `profile` + `task`; it reuses the
   `token_economics` chars-divisor estimator (the workflow token-audit's) and the
   TE.5 env `common.emit` already reads — it reimplements neither.
2. **compactOutput opt-in gates the env.** `env` is
   `{"HARNESS_AGENT_OUTPUT": "compact"}` only when
   `tokenEconomy.compactOutput` is true; otherwise `{}`. Default absent/false =
   today's indent=2 output.
3. **Budget over → warn, never block (owner Q1).** When the estimated packet
   exceeds `tokenEconomy.delegationBudgetTokens`, `budget["over"]` is true and
   `spawn_command` prints exactly one stderr WARN naming estTokens vs
   budgetTokens; the spawn still proceeds. Absent budget field ⇒ never over.
4. **Absent tokenEconomy = byte-identical spawn.** A profile with no
   `tokenEconomy` block yields `{env: {}, budget over False}`: no env exported, no
   warn — the same argv the pre-feature `spawn_command` produced.
5. **One budget number, two checkpoints.** The `delegation-cost-outlier`
   self-review flag uses the delegation's profile `delegationBudgetTokens` as its
   ceiling (mapped from the recorded `agentType`) so the pre-spawn warn and the
   post-hoc flag share one number; the existing median/absolute ceiling remains
   the fallback when no budget is configured.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| One compose seam, no lever reimplemented | `.harness/handoff/plan-token-economy.md` ("every lever exists, but `spawn_command` composes NONE of them") |
| compactOutput per-profile opt-in, default byte-identical | owner decision Q2; the `contextDiscovery`/TE.5/SPEC-140 opt-in precedent in `task-profiles.json` |
| Budget breach warns, never blocks | owner decision Q1 (no `--override` flag; a hard block would stall a legitimately large delegation) |
| Reuse the chars-divisor estimator, not a tokenizer | `token_economics` is the same deterministic estimator the workflow token-audit budgets against |
| One number across pre-spawn + post-hoc | `delegation-cost-outlier` was the driver signal (plan-token-economy.md); sharing the budget avoids two drifting thresholds |

## Ceilings (upgrade paths)

The pre-spawn estimate sizes only the built packet (prompt), not the executor's
whole run — it is a floor that catches an already-oversized brief; the post-hoc
`delegation-cost-outlier` flag catches the realized run cost against the same
number. `agentType → budget` resolves via the profile's claude spawn agent (or
profile name); if two budgeted profiles ever share one agent name, add an
explicit profile tag to the delegation record. `compactOutput` is opted in for
`scan` only today (machine-consumed discovery output); widen per role as each
role's output is confirmed agent-consumed.

## Test strategy

- Behaviors to verify: compactOutput gates the env (pes-1); over-budget flags and
  `spawn_command` warns (pes-2); absent tokenEconomy is byte-identical, env-less,
  warn-less (pes-3); the outlier ceiling equals the profile budget (pes-4).
- Edge cases: absent `delegationBudgetTokens` ⇒ `over` False and `budgetTokens`
  None; `agentType` unknown/None ⇒ `budget_for_agent` None (median fallback).
- Regression risks: the env must NOT change spawn argv (byte-identity); the
  ceiling change must keep the se_self_review median/absolute paths green (that
  scenario builds cost directly, so `latest` carries no budget and falls back).
- Coverage impact: enforced via `testing/scenarios/pes_packet_economy.py`.

## Validation

- `python testing/scenarios/pes_packet_economy.py` — pes-1..pes-4 green.
- `python scripts/harness_lib/packet_economy.py` — module self-check.
- `python scripts/harness.py spawn-command --task "find the auth call path"` shows
  the `-- agent env: HARNESS_AGENT_OUTPUT=compact` intent (scan opts in); a bare
  profile (`--task "implement a feature with tests"`) shows none.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` — template
  conformance + Gherkin id mapping.

## Gherkin scenarios

```gherkin
Feature: SPEC-141 packet-economy compose seam

  Scenario: [pes-1] compactOutput opt-in gates the compact env
    Given a profile whose tokenEconomy sets compactOutput true
    When the spawn packet is composed
    Then the composed env requests compact agent output
    And a profile without compactOutput composes an empty env

  Scenario: [pes-2] an over-budget packet warns but does not block
    Given a profile whose delegation budget is smaller than the packet
    When spawn-command composes that spawn
    Then the budget is marked over and one stderr warn names est vs budget tokens
    And the spawn command is still produced

  Scenario: [pes-3] a profile without tokenEconomy spawns byte-identically
    Given a profile with no tokenEconomy block
    When the spawn packet is composed
    Then the env is empty, the budget is never over, and no warn is printed

  Scenario: [pes-4] the outlier ceiling equals the profile budget
    Given the latest delegation maps to a profile with a delegation budget
    When self-review evaluates delegation cost
    Then the outlier ceiling is that profile budget, not the absolute default
```

## Amendments

(none yet)
