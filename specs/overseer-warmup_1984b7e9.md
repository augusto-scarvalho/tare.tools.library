# SPEC-138 — Overseer session warm-up (ambient discipline + cost rules)

Status: SPEC-138, proposed 2026-07-13 (acceptance: `testing/scenarios/osw_overseer_warmup.py`).

Intake (SPEC-116 door NEW): request = make the overseer's operating discipline
and token-cost rules ambient at every session start, not only inside AFK loops.
Covered-check: the SessionStart hook
(`tools/hooks/reload_context_after_compact.py`) reinjects the canonical STATE
files but carries ZERO operating discipline; the ritual + cost rules live in
`.harness/prompts/overseer-loop-playbook.md`, loaded only for AFK loops.
Decision: **NEW** — a small committed warm-up doc the existing hook prints every
session, composed of POINTERS to the canonical files, never restatements.

## Goal

Every session (Claude or Codex, wired through the same SessionStart hook) opens
with the overseer discipline + token-cost rules in-context as anchors: a
committed `.harness/prompts/overseer-warmup.md`, printed by the existing hook
AFTER the state reinjection payload. The doc points at the canonical sources
(playbook, subagent-contract, capability-panels + task-profiles, WORKFLOWS +
agentic-map-reduce) so it stays a stable index, not a second copy that rots.

## Applicability

Applies to `.harness/prompts/overseer-warmup.md` (the committed doc) and
`tools/hooks/reload_context_after_compact.py` (the SessionStart hook, both
vendors via `.harness/capabilities.json`). The hook appends the doc AFTER
`context_checkpoint.render_reinjection` so the in-flight checkpoint stays the
highest-value head. Does NOT change `context_checkpoint.py`: `REINJECT_RELS`
stays state-only and `checkpoint --render` keeps meaning "state reinjection
payload" (see `context-checkpoint.md` req 5, amended v2). A delegated worker
obeys its packet + subagent-contract; the doc's discipline is the overseer's.

## Requirements / invariants (numbered, testable)

1. **Committed, within budget, ASCII.** `.harness/prompts/overseer-warmup.md`
   exists, is <=40 lines AND <=3200 bytes, and is ASCII-only. The cap is
   scenario-enforced, not runtime-capped (the doc is committed and gated).
2. **Role-scoped, not disclaimed.** RETIRED by SPEC-173 rule 17 (Phase 4b,
   D055/OQ4b-2): the doc is a member of the OVERSEER chain, so a delegated
   worker never receives it and the "ignore this if you are a worker" line it
   used to open with was addressing a reader who cannot arrive. The mechanism is
   the chain, not a disclaimer.
3. **Anchors, not restatements.** The doc cites all five canonical anchor paths
   (overseer-loop-playbook.md; subagent-contract.md; capability-panels.md +
   task-profiles.json; WORKFLOWS.md + agentic-map-reduce.md) and records that
   per-role resource ENFORCEMENT is a tracked gap (only graphify is role-gated
   today).
4. **State first, discipline second.** The SessionStart hook prints the
   reinjection payload FIRST, then a `## .harness/prompts/overseer-warmup.md`
   header + the doc body; rc 0.
5. **Absence is calm.** A missing warm-up doc is a guarded skip: the hook's
   existence guard leaves the reinjection payload and return code unchanged.

## Rationale & sources

| Decision | Sources |
|---|---|
| Warm-up printed by the EXISTING hook (option i), not a new hook | the hook is already wired for Claude+Codex via `.harness/capabilities.json`; a hook-level append gets dual-vendor parity for free |
| State first, discipline second | the in-flight checkpoint is the highest-value post-compact head (`context-checkpoint.md`); discipline is ambient, not urgent |
| Pointers, not restatements; hard budget | a second copy of the playbook rots out of sync; an index that points at canonical files does not |
| ~~Worker disclaimer as the first line~~ | superseded: the same hook fired for worker sessions too, so the line was insurance against mis-reading. SPEC-173 rule 17 chain-scopes the injection instead, so no worker sees the doc at all |
| Budget scenario-enforced, not runtime-capped | the doc is committed and gated, so a runtime cap would be dead code |

## Gherkin scenarios

```gherkin
Feature: overseer session warm-up (ambient discipline + cost rules)

  Scenario: [osw-1] the committed warm-up is a budgeted, anchored index
    Given the repository's .harness/prompts/overseer-warmup.md
    When the acceptance scenario reads it
    Then it is ASCII, within 40 lines and 3200 bytes, carries no worker
      disclaimer (SPEC-173 rule 17 scopes it by chain), cites all five anchor
      paths, and notes the enforcement gap

  Scenario: [osw-2] the hook injects state first, discipline second
    Given the repository's SessionStart hook
    When the hook runs
    Then its stdout carries the reinjection payload before the warm-up header
      and body, and returns rc 0

  Scenario: [osw-3] a missing warm-up doc degrades calmly
    Given a hook whose warm-up append is guarded on file existence
    When the doc is absent
    Then the reinjection payload and return code are unchanged
```

## Ceilings (upgrade paths)

Budget + anchor coverage are asserted by substring/length checks, not a Markdown
parser; if the doc grows structured sections, upgrade osw-1 to structural
assertions. A one-line pointer in `docs/CONTEXT_CHECKPOINT.md` is a fine later
follow-up, deliberately skipped for v1 to keep the footprint at five files.

## Test strategy

- Behaviors: budget + ASCII + anchor coverage + gap note (osw-1);
  hook payload order and rc (osw-2); guarded absence asserted in source (osw-3).
- Edge cases: absent doc (source-asserted, since the repo doc is committed); the
  append must not break context-checkpoint's ckpt-4 substring/length checks.
- Regression risks: `context_checkpoint.py` stays untouched; ckpt-4 rerun green.
- Coverage impact: enforced via `testing/scenarios/osw_overseer_warmup.py`.

## Validation

- `python testing/scenarios/osw_overseer_warmup.py` — osw-1..osw-3 green.
- `python testing/scenarios/context_checkpoint.py` — ckpt-4 stays green under
  the hook append (sibling regression net).
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` — template
  conformance (SPEC-138 + the `context-checkpoint.md` v2 amendment).

## Amendments

### v2 (2026-07-23) — warm-up slimmed against the injected role chain

Since SPEC-170 v4 the SessionStart hook also injects the session role's
ambient core, so the warm-up's restated discipline pointers became the
second copy req 3 warned about. The doc now carries: the four token-cost anchors (all five anchor paths
kept, enforcement-gap note kept — req 3 intact), and a one-line /route
pointer replacing the former section (the playbook chain carries /route in
full). Budget unchanged (osw-1 asserts the same caps; the doc simply sits
further under them, ~1.1k). The hook payload's AGGREGATE fit is hib-1..3
(`testing/scenarios/hib_hook_inline_budget.py`) — the vendor's 10k inline
ceiling was discovered 2026-07-23 when the composed payload (36.8KB) was
persisted-to-file and nothing ambient actually loaded.
