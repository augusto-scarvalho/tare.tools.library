# SPEC-142 — Delegation output-cap contract line (worker-facing, via the seam)

Status: SPEC-142, proposed 2026-07-13 (acceptance: `testing/scenarios/doc_delegation_output_cap.py`).

## Goal

Add the last per-profile token lever to the spawn packet: a single worker-facing
CONTRACT line asking the delegated worker to bound its own output. When a
profile's `tokenEconomy.outputCapChars` is set, `compose_spawn` returns one
`promptSuffix` line naming the cap and telling the worker to keep the decisive
tail (file paths, error/traceback lines) rather than the head if it must
truncate; `spawn_command` folds that line into the built prompt. This is a
request TO the worker, not truncation OF the worker's output — real output
truncation is EXP-1 phase-2 and stays owner-gated.

## Applicability

Applies to `scripts/harness_lib/packet_economy.py` (`compose_spawn` gains
`promptSuffix` in its returned dict) and `scripts/harness.py` `spawn_command`
(appends the suffix to the built prompt before the argv is rendered; the 4-tuple
return signature is unchanged). The existing `tokenEconomy` blocks in
`.harness/routing/task-profiles.json` gain an `outputCapChars` int (scan 12000;
implementation/review/security 20000). It does NOT truncate any text, does NOT
touch `common.truncate_text` / `result_contracts.maxWorkerOutputChars`, and does
NOT touch `.harness/state/experiments.json` or the EXP-1 registry.

## Requirements / invariants (numbered, testable)

1. **Cap set → one contract line naming N + the keep-the-tail rule.** When
   `tokenEconomy.outputCapChars` is an int, `compose_spawn(...)["promptSuffix"]`
   is exactly one line that names the char cap N and instructs the worker to keep
   the decisive tail (file paths, error/traceback lines), not the head, if it
   must truncate.
2. **Absent field → byte-identical prompt.** With no `outputCapChars`,
   `promptSuffix` is `""`; `spawn_command` appends nothing, so the built prompt
   and the rendered argv are byte-identical to the pre-feature spawn.
3. **Contract line, not truncation.** The line is worker-facing guidance only. No
   code here truncates worker output; real truncation is EXP-1 phase-2,
   owner-gated. `compose_spawn` stays pure over `profile` + `task`.
4. **Independent of EXP-1 — no registry coupling.** Shipping the cap writes
   nothing to `.harness/state/experiments.json`. The EXP-1 phase-1 finding
   (head-preserving truncation drops the decisive tail) is cited as MOTIVATION
   for the keep-the-tail wording only, not adopted as EXP-1's control change.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| A worker-facing cap line, composed through the SAME seam as the other levers | `.harness/handoff/plan-token-economy.md` (the output cap is the last lever `spawn_command` should compose); SPEC-141 `compose_spawn` seam |
| "Keep the decisive tail, not the head" wording | EXP-1 phase-1 measurement — head-preserving `truncate_text` drops ~85% of the decisive path lines on the one large gate surface (`.harness/handoff/result-exp1-probe.md`); cited as motivation only |
| Cap is a request to the worker, not truncation of its output | Real output truncation is EXP-1 phase-2 and owner-gated; this shard must not pre-empt that owner decision |
| Absent `outputCapChars` = byte-identical | Every token lever in `task-profiles.json` is opt-in per profile (SPEC-140/141 precedent) |
| Cap the cap in chars, matching repo vocabulary | `result_contracts.maxWorkerOutputChars` and `OUTPUT_CAP` are char-denominated; the worker reasons in the same unit |

## Gherkin scenarios

```gherkin
Feature: SPEC-142 delegation output-cap contract line

  Scenario: [doc-1] a capped profile composes one keep-the-tail line
    Given a profile whose tokenEconomy sets outputCapChars
    When the spawn packet is composed
    Then the prompt suffix is one line naming the char cap
    And it tells the worker to keep the decisive tail, not the head
    And a profile without outputCapChars composes an empty suffix

  Scenario: [doc-2] the cap line folds into the prompt, byte-identical when absent
    Given a capped profile and an uncapped profile
    When each spawn command is built
    Then the capped worker prompt contains the cap line
    And the uncapped worker prompt omits it byte-identically

  Scenario: [doc-3] the cap is independent of the EXP-1 registry
    Given the output cap ships as this spec's own decision
    When the spawn packet is composed and the spawn command is built
    Then no write is made to the experiment-lifecycle registry
```

## Ceilings (upgrade paths)

The cap is advisory: it asks the worker to self-bound, it does not enforce a
byte limit. If measurement shows workers routinely overrun the request, escalate
to EXP-1 phase-2 (an owner-gated tail-preserving truncator on the read side,
`common.truncate_text`) — one seam, one revert — rather than hardening this
contract line.

## Test strategy

- Behaviors to verify: cap set yields one N-naming keep-the-tail line and absent
  yields `""` (doc-1); `spawn_command` folds the line in when capped and stays
  byte-identical when uncapped (doc-2); no `experiments.json` write (doc-3).
- Edge cases: `outputCapChars` absent ⇒ empty suffix; a `tokenEconomy` block with
  a budget but no cap still composes an empty suffix (byte-identical argv).
- Regression risks: the suffix must not alter the argv when uncapped (byte
  identity — shared with `pes_packet_economy.py` pes-3); `compose_spawn` stays
  pure over its args; the 4-tuple `spawn_command` signature is unchanged.
- Coverage impact: enforced via `testing/scenarios/doc_delegation_output_cap.py`.

## Validation

- `python testing/scenarios/doc_delegation_output_cap.py` — doc-1..doc-3 green.
- `python scripts/harness_lib/packet_economy.py` — module self-check (now covers
  the suffix present/absent).
- `python scripts/harness.py spawn-command --task "implement a feature with tests"`
  shows the cap line in the built prompt (implementation opts in); a no-cap
  profile (`--task "plan the architecture"`) shows none.
- `python testing/scenarios/pes_packet_economy.py` — pes-1..pes-4 still green
  (the seam extension is byte-identical for uncapped profiles).
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` — template
  conformance + Gherkin id mapping.

## Amendments

(none yet)
