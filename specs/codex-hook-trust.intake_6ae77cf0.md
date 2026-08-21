# Intake refinement -- codex hook-trust decision (door NEW)

SPEC-116 invariant 2 checklist. Seeds SPEC-150 (`specs/40-features/codex-hook-trust.md`).

## Request (verbatim)

> Groom promotion d77116ead917 (2026-07-18): the experimentally verified
> security finding (8 codex execs) is that `codex exec` only fires hooks with a
> persisted/flagged trust, and EVEN with trust the deny is ignored under
> bypassPermissions -- hooks on codex are advisory, never write enforcement. The
> decision (already operating, never specified): the codex hook-trust flag stays
> OFF (turning it on = false security); real containment = SPEC-148 + S3. Specify
> and PIN the decision.

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search codex hook trust advisory` | no hit -- no spec owns the decision |
| doc-find | `python scripts/harness.py doc-find codex hook trust bypassPermissions deny` | hit on registers only, not specs (see below) |

Two registers of the finding EXIST but neither is a spec:

- `.harness/capabilities.json` protect-files `note` -- a TERMINAL-STATE
  description (ADVISORY on codex), a runtime register, not a normative spec.
- `docs/research/harness-reference-architecture-adoption.md` section
  "Investigacao experimental 2026-07-18" -- research evidence, not a spec.

Decision: **NEW** -- the OFF-by-default decision is operant but unspecified; a
register describes state, it does not pin a rule a check can regress against.

## Goal

One sentence: pin the operant decision that codex worker templates never carry
`--dangerously-bypass-hook-trust` (hooks on codex are advisory; real write
containment is native S3 sandbox + SPEC-148), and require re-evaluation only if
codex changes its deny semantics.

## Scope

In scope:
- Pin the OFF-by-default hook-trust decision as numbered, testable rules.
- Freeze the capabilities.json protect-files note as the canonical ADVISORY
  description (no regression to the pre-2026-07-18 3-gap wording).
- Point to S3 + SPEC-148 as the normative write-containment reference.
- Name the mandatory re-evaluation trigger (codex changelog honoring deny).

Out of scope:
- Any change to executors.json, capabilities.json, `.codex/*`, `.claude/*`, or
  hooks (this spec pins the existing state, it does not move it).
- Duplicating SPEC-148 containment mechanics (referenced, not restated).

## Actors & surfaces

- Actors: codex worker spawns, the protect-files hook, the spec-pack gate.
- Surfaces (CLI / GUI / API / internal): internal (routing/executors + hook
  registry) + spec pack. UI surface? **no** -> Gherkin optional.

## Proposed acceptance criteria

- [ ] No codex commandTemplate carries `--dangerously-bypass-hook-trust`.
- [ ] The capabilities protect-files note stays ADVISORY and cites SPEC-148.
- [ ] SPEC-150 exists and R1 names the `--dangerously-bypass-hook-trust` flag.
- [ ] Write containment is delegated to S3 + SPEC-148, not re-specified.
- [ ] The re-evaluation trigger (deny honored under bypassPermissions) is stated.

## Risks / blast radius

Low: pins existing state. Risk is a future edit silently re-enabling the flag
or regressing the note to false-security wording -> the sc-5 check turns each
into a red gate. No runtime code touched; rollback = delete the two spec files
and the sc-5 block.

## Open questions for the human

- (none -- decision already made by the owner; this intake only pins it)
