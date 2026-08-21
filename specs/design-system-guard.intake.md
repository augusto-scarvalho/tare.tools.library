# Intake refinement -- design-system-guard (door NEW)

SPEC-116 invariant 2 checklist. Seeds SPEC-152
(`specs/40-features/design-system-guard.md`).

## Request (verbatim)

> bora, manda o hook + gate + porta SPEC-116 pra amarrar a lei de UI
> (docs/DESIGN_SYSTEM.md / SIGNAL) a MAQUINA e nao a memoria do agente.

Precedent (owner, prior turn): "criar um hook e amarrar o processo aos workers de
UI" -- seed the SIGNAL contract at every ui/ edit, and enforce it mechanically in
the gate so acceptance does not depend on an agent remembering to read the md.

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search design system guard` | no hit -- no spec owns a design-system hook or gate |
| doc-find | `python scripts/harness.py doc-find design system guard hook gate` | hit on `docs/DESIGN_SYSTEM.md` (the LAW/source) only, no spec |

`docs/DESIGN_SYSTEM.md` is the design LAW (a doc, the contract source), not a
normative harness spec, and it is enforced only by a human PR checklist (its
section 7). No spec pins the machine-enforced tie.

Decision: **NEW** -- the law exists as a doc; no spec/check ties it to the
machine. This spec pins the hook-seed + gate-enforcement rule a check regresses
against.

## Goal

One sentence: tie the SIGNAL UI design law (docs/DESIGN_SYSTEM.md) to the machine
via an advisory PreToolUse seed on ui/ edits plus a deterministic gate scenario
that mechanically enforces it, so conformance does not depend on the agent
remembering to read the doc.

## Scope

In scope:
- An advisory PreToolUse hook that seeds the SIGNAL contract on ui/ source edits.
- A gate scenario (`testing/scenarios/ds_design_system.py`) that enforces the 7
  ds-checks on every `validate --staged`.
- The `designSystem.guard` off|advise config knob (default advise).
- Registering the hook in `.harness/capabilities.json` (rendered to the vendors).

Out of scope:
- Editing `docs/DESIGN_SYSTEM.md` (the law/source -- owner-gated; the section-7
  doc<->reality allowlist divergence is surfaced, not reconciled here).
- Any change under `ui/` (this feature is the guard, not a screen).
- Restating the testing/quality-gate baseline (referenced, not duplicated).

## Actors & surfaces

- Actors: UI workers (whose ui/ edits are seeded), the gate scenario, the
  spec-pack gate.
- Surfaces (CLI / GUI / API / internal): internal (the gate scenario + the hook
  registry) + the hook. The guard GOVERNS ui/ files; it is not itself a screen.
- UI surface? **no** -> Gherkin optional (the guard is CLI/internal + hook, not a
  GUI view).

## Proposed acceptance criteria

- [ ] ds-1: no raw color literal in ui/src/** outside the theme base allowlist
      (HTML entities and non-hex runs excluded; inline SVG fill=/stroke= exempt).
- [ ] ds-2: no anti-slop font family (Inter/Roboto/Arial/Space Grotesk/Helvetica)
      anywhere in ui/src/**.
- [ ] ds-3: ui/dist/** carries no runtime network reference.
- [ ] ds-4: every GUI POST targets /api/action (GUI-writes-no-state).
- [ ] ds-5: harness_ui.py serves the vanilla panel at "/", not the dist React.
- [ ] ds-6: ui/dist/index.html exists and is git-tracked.
- [ ] ds-7: the design-system-guard advisory seed is registered in capabilities.json.

## Risks / blast radius

Low. Adds one hook + one gate scenario and touches `.harness/capabilities.json`
(add the hook) and `.harness/project.json` (add the knob). The hook is advisory
and fail-open (cannot break a tool call); the gate scenario is read-only. Rollback
= delete the two new files, revert the two config edits, re-run `agents pair`.
Calibration risk: the ds-1 allowlist tracks the shipped tree, not the doc; a color
base file added later without allowlisting turns ds-1 red until reconciled.

## Open questions for the human

- Reconcile DESIGN_SYSTEM.md section 7 (3-file allowlist) with the shipped 6-file
  + logo-SVG reality? Owner-gated -- the gate enforces the real allowlist; the doc
  text is unchanged here.
