# SPEC-140 — Per-role resource allowlist (tokenEconomy skills/mcp)

Status: SPEC-140, proposed 2026-07-13 (acceptance: `testing/scenarios/rra_role_resource_allowlist.py`).

## Goal

Give each task profile a declared, per-role resource allowlist so a spawned
worker is told which skills and MCP servers it may load — the biggest untied
token lever, since today only `contextDiscovery.graphify` is role-gated and
nothing scopes the skill/MCP surface. This shard owns the resource-scoping
fields only: an optional `tokenEconomy` block on a profile and a single prompt
line that renders it. It does not build the compose seam or any budget.

## Applicability

Applies to `.harness/routing/task-profiles.json` (an optional `tokenEconomy`
block, sibling of `contextDiscovery`) and `scripts/harness.py` `build_prompt`
(the render). It does NOT touch `spawn_command`, cost/token budgets,
`compactOutput`, or a `memoryScope` field — those are later shards. Claude
adapter frontmatter (`.claude/agents/*.md`) may additionally tighten its
`tools:` list to match a role's allowlist where safe.

This shard ships two `tokenEconomy` sub-fields only: `allowedSkills` and
`allowedMcp`. `compactOutput` (s3), `outputCapChars`/`delegationBudgetTokens`
(s3/s4) and `memoryScope` (deferred, no per-role memory store exists) are out
of scope and must not be added here.

## Requirements / invariants (numbered, testable)

1. **Absent block = byte-identical prompt.** A profile without a `tokenEconomy`
   block produces exactly the prompt it produced before this feature existed —
   `build_prompt` renders no resource line (the `contextDiscovery`/TE.5
   opt-in precedent).
2. **Present block renders exactly one resource line.** When the resolved
   profile has a `tokenEconomy` block, `build_prompt` appends exactly one line
   naming both allowlists:
   `Resources for this role: skills=[...]; mcp=[...] - do not load others.`
3. **Enforcement tier is honest, not asserted.** For non-claude executors
   (codex/GLM/generic) the allowlist is CONTRACTUAL: prompt text a reviewer can
   check in the worker's output — the harness cannot strip an external
   executor's tools. Claude workers additionally enforce via agent frontmatter.
   The spec states this tier rather than claiming runtime enforcement it cannot
   provide for external executors.
4. **The field is inert for classification.** `tokenEconomy` is a resource
   declaration only; it never participates in profile scoring, so adding or
   removing it leaves `classify` output (chosen profile and scores) unchanged.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Resource scoping is the biggest untied token lever | `.harness/handoff/plan-token-economy.md` gap #2; this shard's plan brief |
| Opt-in block, absent = byte-identical | `contextDiscovery`/TE.5 precedent already sibling-scoped in `task-profiles.json` |
| One rendered contract line, not a schema handshake | `build_prompt` already threads guardrail/contract lines the same way (single string interpolation) |
| Non-claude enforcement is contractual, not runtime | owner decision Q3: the harness prints the argv but cannot strip an external executor's loaded tools |
| No `memoryScope` field | owner decision Q4: no per-role memory store exists yet (backlogged) |

## Gherkin scenarios

```gherkin
Feature: SPEC-140 per-role resource allowlist

  Scenario: [rra-1] a profile with a tokenEconomy block gets one resource line
    Given a profile whose tokenEconomy allows some skills and no mcp
    When build_prompt renders that profile's spawn prompt
    Then the prompt carries exactly one resource line naming both allowlists

  Scenario: [rra-2] a profile without the block keeps the legacy prompt
    Given a profile with no tokenEconomy block
    When build_prompt renders its spawn prompt
    Then no resource line appears and the prompt is byte-identical to the
      pre-feature prompt

  Scenario: [rra-3] the block never changes classification
    Given two profile sets identical except one adds a tokenEconomy block
    When the same task is classified against each
    Then the chosen profile and the scores are identical
```

## Ceilings (upgrade paths)

The line is advisory text for external executors (contractual tier); when a
per-executor tool-stripping seam exists (s3+), non-claude enforcement can move
from prompt-text to runtime. `allowedMcp` is declared but empty for the seeded
roles today — populate it when an MCP server is actually granted to a role.

## Test strategy

- Behaviors to verify: present block renders exactly one line (rra-1); absent
  block renders nothing and stays byte-identical (rra-2); the field is inert for
  classification (rra-3).
- Edge cases: empty `allowedSkills`/`allowedMcp` still render the line with
  empty brackets; a block missing both keys renders nothing.
- Regression risks: the render must not perturb the acceptance-contract or
  planner-guardrail lines already threaded through `build_prompt`; seeding
  sibling `tokenEconomy` keys must not affect model routing derived from
  `task-profiles.json`.
- Coverage impact: enforced via `testing/scenarios/rra_role_resource_allowlist.py`.

## Validation

- `python testing/scenarios/rra_role_resource_allowlist.py` — rra-1..rra-3 green.
- `python scripts/harness.py spawn-command --task "implement a feature with tests"`
  shows the resource line; a profile without the block shows none.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` — template
  conformance + Gherkin id mapping.

## Amendments

(none yet)
