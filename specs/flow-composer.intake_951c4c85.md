# Intake refinement — door NEW checklist (renderer-first flow composer)

## Request (verbatim)

> Implement item N2 of TASK-004 — a renderer-first flow composer in the panel: a
> READ-ONLY derived SVG DAG view of a workflow profile + structured FORMS to edit the
> branch composition, whose "Compile" button calls `workflow plan --validate-only` (N1)
> and shows the validation inline. Explicitly NOT a draggable node canvas (litegraph
> rejected, D007). The profile JSON stays the single source of truth; the GUI writes
> NOTHING.

## Covered-check (which door?)

Commands run on 2026-07-12 (HEAD 01b5715); outcomes recorded verbatim.

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search flow composer dag validate-only` | **no covering spec** — one hit, the commit `3bedcbda2` "Research round 2: … flow composer portfolio" (the provenance for THIS work, not a spec covering it) |
| doc-find | `python scripts/harness.py doc-find flow composer node canvas svg dag` | **no covering spec** — top hits are `tasks/harness-self-improvement/PLAN.md` + workflow docs (workflow machinery), none a flow-composer feature spec |

Interpretation: the composer is a genuinely NEW UI surface — no `specs/40-features/*`
owns it. The compile primitive it calls (`workflow plan --validate-only`) is SPEC-119
v6 rules 28-30 (N1, already shipped), and the panel it lives in is SPEC-114; but the
derived-DAG-plus-forms composer view is uncovered ground. Provenance: the round doc
`docs/research/agent-gui-cli-features.md` Phase 5 (K1) + decision `D007`.

Decision: **NEW → SPEC-120** (`specs/40-features/flow-composer.md`).

## Goal

Let a user visually read any workflow profile as a derived SVG DAG and edit its branch
composition through structured forms, then compile-validate the candidate inline via
`workflow plan --validate-only` — the profile JSON stays the single source of truth and
the GUI writes nothing.

## Scope

In scope:
- Read collector `ui_panel.composer_snapshot` — closed vocabularies (profiles,
  executors, taskProfiles) + a normalized DAG view per profile (derived, no layout state).
- `GET /api/composer` (token-gated, read-only) and `POST /api/compile` (read-shaped
  validate-only compile; not an ACTIONS entry; builds no subcommand argv).
- A "Compose" nav view: profile picker, derived SVG DAG (source → branch → reduce, seed
  edges when the profile shares a digest), branch-row forms, and an inline compile report.

Out of scope:
- Apply / materialize / start (the mutating plan/start flow) — N2 is compile-validate only.
- A draggable node canvas / persisted layout (litegraph rejected, D007; editable canvas
  deferred until measured N2 editing friction).
- Per-branch object overrides for map-reduce profiles (shards are derived at compile).

## Actors & surfaces

- Actors: a human supervisor composing/validating a workflow flow in the panel.
- Surfaces (CLI / GUI / API / internal): GUI (Compose view), API (`GET /api/composer`,
  `POST /api/compile`), internal (`ui_panel.composer_snapshot`/`compile_candidate`);
  the compile primitive is the existing N1 CLI (`workflow plan --validate-only`).
- UI surface? **yes** → Gherkin required.

## Proposed acceptance criteria

- [x] `/api/composer` returns the closed vocabularies + a derived DAG (nodes/edges) per
      profile; the PAGE carries the `navCompose` nav + the SVG render functions.
- [x] "Compile" POSTs a composed candidate to `/api/compile`, which runs
      `validate_workflow_plan` in-process and returns the N1 report inline (valid ✓/✗,
      per-worker tokens, tokenAudit, errors/warnings).
- [x] A profile (or composed taskProfile) outside the closed set is rejected BEFORE any
      compile; no subcommand argv is ever built from browser input.
- [x] The composer writes no state: `/api/compile` is not in `ui_panel.ACTIONS`, the
      mutating ACTIONS set is unchanged, and a compile materializes no `active/WF-*` dir.
- [x] The DAG layout is computed at render from the (edited) form state every time —
      no coordinates stored — so the view cannot drift from the composition.
- [x] Every route is token-gated (`_authed` precedes routing).

## Risks / blast radius

- New endpoint taking browser input (`/api/compile`) — the K1 trust boundary. Mitigated
  by an in-process call to N1 (no argv construction possible) plus server-side
  closed-vocabulary validation before compiling; `validate_workflow_plan` itself
  re-enforces the vocabularies and secret-scans the candidate content.
- Touches `scripts/harness_ui.py` (routes), `scripts/harness_lib/ui_panel.py` (collector +
  compile core), `scripts/harness_ui_page.py` (front-end). Regression net: `m5_ui_panel.py`,
  `ui_e2e.py`, and `wv_validate_only.py` (N1, reused by the compile).

## Open questions for the human

- Should the deferred editable canvas be reopened only on the D007 trigger (real graphs
  > ~12 nodes or measured editing friction), or sooner if forms prove clumsy at 5 branches?
