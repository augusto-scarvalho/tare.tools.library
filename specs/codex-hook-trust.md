# SPEC-150 -- Codex hook-trust stays off (hooks on codex are advisory)

Status: SPEC-150, proposed 2026-07-18 (acceptance: `testing/scenarios/sc_security_ceilings.py`).
Intake: `specs/40-features/codex-hook-trust.intake.md`. Promoted by groom
d77116ead917; experimentally verified 2026-07-18 across 8 codex execs.

## Goal

Pin the operant, previously-unspecified decision that the codex hook-trust flag
stays OFF. `codex exec` only fires hooks with a persisted/flagged trust, and
even with trust it does NOT honor a hook deny under bypassPermissions -- so
hooks on codex are ADVISORY, never write enforcement. Enabling the flag would
buy false security (deny-ignored hooks that look enforcing). Real codex write
containment lives elsewhere (native S3 sandbox + the harness-owned sandbox of
SPEC-148); this spec freezes that decision as testable rules and names the one
trigger that reopens it.

## Applicability

Applies to codex worker spawn templates in `.harness/routing/executors.json`,
the protect-files hook register in `.harness/capabilities.json`, and the
spec-pack gate. Does not cover the claude leg (deny is honored there -- hooks are
enforcement on claude, unchanged) and does not restate SPEC-148 containment
mechanics (referenced normatively, not duplicated).

## Requirements / invariants (numbered, testable)

1. **No hook-trust flag on codex.** No codex worker `commandTemplate` in
   `executors.json` carries `--dangerously-bypass-hook-trust`. Turning hooks on
   without honored enforcement is false security; the flag stays off.
2. **Note frozen as ADVISORY.** The protect-files terminal-state note in
   `capabilities.json` remains the canonical description -- it states hooks on
   codex are ADVISORY and cites SPEC-148 -- and must not regress to the
   pre-2026-07-18 "3-gap" wording (which implied a fix was pending rather than a
   terminal advisory verdict).
3. **Containment is S3 + SPEC-148 (reference, not duplication).** Codex write
   containment is native `--sandbox` derived from `writeAllowed` (S3) plus the
   harness-owned spawn-time OS lock of SPEC-148. This spec references those; it
   does not re-specify them.
4. **Mandatory re-evaluation trigger.** If codex changes its deny semantics --
   concretely, a codex changelog declaring the hook deny honored under
   bypassPermissions -- this decision MUST be re-evaluated via a versioned
   amendment. Absent that trigger, the flag stays off.

## Rationale & sources

| Decision | Sources |
|---|---|
| Hook-trust flag off (R1) | 3 measured gaps 2026-07-18 (mute trust / matcher / payload-shape); 8 codex execs; deny-ignored-under-bypassPermissions verdict |
| Parser + matcher shipped but insufficient (R1, R2) | commit 76b5965 (apply_patch path parser), commit a882081 (protect-files matcher parity) -- needed but not sufficient: deny still ignored |
| Advisory verdict is terminal, not a pending fix (R2) | `docs/research/harness-reference-architecture-adoption.md`, "Investigacao experimental 2026-07-18" section |
| Containment lives in S3 + SPEC-148 (R3) | SPEC-148 (harness-owned sandbox, spawn-time OS lock on protected paths); native codex `--sandbox` from writeAllowed |
| Reopen only on changed deny semantics (R4) | Disciplina observe-first: pin the decision, gate the reversal, reopen on evidence not vibes (SPEC-116 inv. 7) |

## Ceilings (upgrade paths)

- Decision pinned as OFF, not adaptive -- if a future codex honors deny under
  bypassPermissions (R4 trigger), amend to re-enable the flag with enforcement
  restored; do not silently flip it.
- Enforcement of R1/R2 is a source/register scan (sc-5), not a live codex exec --
  upgrade to an empirical exec probe only if a text scan proves too coarse.

## Test strategy

- Behaviors to verify: no codex commandTemplate carries the flag (R1); the
  capabilities note contains ADVISORY and SPEC-148 (R2); SPEC-150 exists and R1
  names the flag literal (spec-and-check linked).
- Edge cases: a future edit adding the flag to any executor, or regressing the
  note wording, must turn sc-5 red.
- Regression risks: none -- pins existing state; touches no runtime code.
- Coverage impact: enforced via `sc_security_ceilings.py` check `sc-5`.

## Validation

- `python testing/scenarios/sc_security_ceilings.py` (5/5, including the new
  `sc-5` covering R1/R2 and the spec-and-check link).
- Neighbor scenario green: `python testing/scenarios/srg_spawn_ratchet.py`.
- Spec-pack `feature-spec-conformance` green on this file (six required
  headings present; non-UI, no Gherkin).

## Amendments

(none yet)
