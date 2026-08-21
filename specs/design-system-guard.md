# SPEC-152 -- Design-system guard (tie the SIGNAL UI law to the machine)

Status: SPEC-152, proposed 2026-07-19 (acceptance: `testing/scenarios/ds_design_system.py`).
Intake: `specs/40-features/design-system-guard.intake.md` (door NEW, D026/D028).
Law source: `docs/DESIGN_SYSTEM.md` (SIGNAL) -- the contract this spec ties to the machine.

## Goal

Tie the SIGNAL UI design law (`docs/DESIGN_SYSTEM.md`, D026/D028) to the MACHINE,
not to the agent's memory: an advisory PreToolUse hook SEEDS the contract at every
`ui/` source edit, and a deterministic gate scenario ENFORCES it mechanically on
every `validate --staged`. Acceptance stops depending on an agent remembering to
read the doc -- the seed is advisory, the gate is the teeth.

## Applicability

Applies to `tools/hooks/design_system_guard.py` (the advisory seed),
`testing/scenarios/ds_design_system.py` (the enforcement), the hook registration
in `.harness/capabilities.json`, the `designSystem.guard` knob in
`.harness/project.json`, and `ui/**` as the surface the guard governs. Does not
restate the baseline (`specs/00-universal/testing-and-quality-gates.md` is
referenced, not duplicated) and does not modify `docs/DESIGN_SYSTEM.md` (the
law/source is owner-gated).

## Requirements / invariants (numbered, testable)

1. **Advisory seed on ui/ edits, fail-open.** The hook fires PreToolUse on
   `Edit|Write|MultiEdit|apply_patch`; when a target path is under `ui/` but not
   `ui/dist/` or `ui/node_modules/`, it prints the SIGNAL reminder (the 5 laws +
   "consult docs/DESIGN_SYSTEM.md" + the D028 signature-moment). It reuses
   `protect_files.candidate_paths` for path parsing (Edit/Write/MultiEdit
   `file_path` and codex `apply_patch` bodies), is fail-open (any error => silent,
   exit 0, never breaks the tool call), and is rendered to both vendors from
   `.harness/capabilities.json`.
2. **Gate enforces the 7 ds-checks.** `ds_design_system.py` runs in every gate
   (the runner globs `testing/scenarios/*.py`) and blocks a `ui/` diff that
   violates the law: ds-1 token-driven (no raw color literal in `ui/src/**`
   outside the theme-base allowlist; HTML entities and non-hex runs never match;
   inline SVG `fill=`/`stroke=` exempt), ds-2 anti-slop fonts, ds-3 offline
   bundle, ds-4 GUI-writes-no-state (POST -> `/api/action`), ds-5 `/` vanilla
   (D025), ds-6 committed `ui/dist` (D024), ds-7 hook wired.
3. **Config knob.** `.harness/project.json` -> `designSystem.guard` is
   `"off" | "advise"`, default `"advise"`; `"off"` silences the hook. The gate
   is independent of the knob (enforcement is not opt-out).
4. **Hook is ADVISORY, never blocks -- the gate is the teeth.** The hook never
   exits 2 / denies. Hooks on codex are advisory anyway (codex ignores the deny
   under bypassPermissions -- see the protect-files note in `capabilities.json`
   and SPEC-150), so mechanical enforcement lives in the gate scenario, not the
   hook. The ds-1 allowlist is calibrated to the shipped tree, not to the literal
   `DESIGN_SYSTEM.md` section 7 (which predates the shell CSS); reconciling that
   text is owner-gated.

## Rationale & sources

| Decision | Sources |
|---|---|
| Seed the contract at the edit site (R1) | `docs/DESIGN_SYSTEM.md` (SIGNAL law); D026 (anti-slop), D028 (signature moment / this rulebook) |
| Path parsing reused, not reinvented (R1) | `tools/hooks/protect_files.py` `candidate_paths`/`apply_patch_paths` (Edit/Write/MultiEdit + codex apply_patch bodies) |
| Machine enforcement in the gate (R2, R4) | `docs/DESIGN_SYSTEM.md` section 0 (the 5 laws) + section 7 (PR checklist, now mechanized); `specs/00-universal/testing-and-quality-gates.md` |
| Hook advisory, gate is the teeth (R4) | protect-files terminal-state note in `.harness/capabilities.json`; SPEC-150 (codex hook deny ignored under bypassPermissions -> hooks advisory) |
| Allowlist calibrated to reality (R2, R4) | overseer recon 2026-07-19 (grep `ui/src`): 6 CSS base files + logo SVG carry the raw palette; section-7's 3-file list predates the shell CSS |

## Ceilings (upgrade paths)

- ds-1 allowlist is a static set of grandfathered theme-base files -- if the theme
  is refactored so a new base file legitimately carries the palette, extend the
  set (do not relax the regex). A color literal in a NEW `.tsx`/`.css` (screens,
  components) is a real violation, by design.
- The hook is advisory-only; if a future engine honors a hook deny AND the owner
  wants hard pre-edit blocking of ui/ slop, that is a separate amendment -- the
  gate stays the enforcement of record.
- The doc<->reality section-7 divergence is surfaced, not fixed here; reconciling
  the `DESIGN_SYSTEM.md` allowlist text is owner-gated.

## Test strategy

- Behaviors to verify: the hook seeds on a ui/ edit and stays silent off-ui / off
  / on broken input (its `--self-check`); the 7 ds-checks pass on the current tree
  (R2); a planted hex outside the allowlist turns ds-1 red (the teeth); the hook
  id is registered (ds-7).
- Edge cases: HTML entities (`&#9671;`) and non-3/6/8 hex runs must NOT match ds-1;
  inline SVG `fill=`/`stroke=` in `.tsx` is exempt; `ui/dist`/`ui/node_modules`
  edits do not trigger the seed.
- Regression risks: a new POST URL other than `/api/action`, a CDN reference in
  the bundle, a forbidden font, or flipping `/` to React each turns a ds-check red.
- Coverage impact: enforced via `testing/scenarios/ds_design_system.py` (ds-1..ds-7)
  and the hook's `--self-check`.

## Validation

- `python testing/scenarios/ds_design_system.py` (7/7, ds-1..ds-7 green on the
  current tree; a planted stray hex outside the allowlist turns ds-1 red).
- `python tools/hooks/design_system_guard.py --self-check` (OK).
- Spec-pack `feature-spec-conformance` green on this file (six required headings
  present; non-UI, no Gherkin).

## Amendments

(none yet)
