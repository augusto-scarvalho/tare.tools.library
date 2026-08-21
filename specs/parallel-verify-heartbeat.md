# SPEC-157 — Parallel verify + reckon join: commit gated on the ledger

Status: SPEC-157, proposed 2026-07-20 (acceptance: `testing/scenarios/pvr_parallel_verify.py`).

## Goal

Make the overseer's "run the gate AND a reviewer reckon in parallel, then commit
only if BOTH passed" ritual a MECHANICAL guardrail instead of memory. The GATE
half of the commit-ledger already exists (SPEC-137: a commit is blocked unless
the staged-surface fingerprint matches a recorded `lastValidation` pass). This
spec ADDS the RECKON half by MIRRORING that machine: a reviewer's `no-blocker`
verdict, keyed on the SAME staged fingerprint, recorded as `lastReckon`; the
pre-commit hook joins the two dimensions and blocks a risk-bearing commit unless
gate=pass AND reckon=no-blocker for the same fingerprint. "Both passed?" becomes
enforced, not remembered.

## Applicability

- `scripts/harness_lib/validation_stamp.py` — `stamp_reckon` / `check_reckon` /
  `reckon_required` / the reckon override auditors, mirroring the existing
  `stamp_staged` / `check_staged` / `detect_override`. The fingerprint, manifest,
  lock, CAS and profile map are REUSED, never reimplemented.
- `tools/hooks/precommit_validation_gate.py` — runs BOTH `check_staged` and
  `check_reckon`; blocks if either blocks; the `--post-commit-audit` path records
  a `--no-verify` bypass in either dimension.
- `.harness/project.json#/precommitValidation.profiles.<name>.reckon` — a boolean
  opt-in flag on the risk-bearing profile(s) only.
- CLI: `harness.py reckon --record --verdict no-blocker|blocker [--note …]` and
  `harness.py verify-status [--json]` (via `cli_registry`).

Does NOT cover: running the gate or spawning the reckon reviewer (that is the
overseer's ritual — this spec only enforces the JOIN at commit time); a codex
mirror of the hook (the pre-commit hook is git-level and vendor-neutral); the
heartbeat/wakeup orchestration (a playbook ritual + ScheduleWakeup fallback, not
enforced code).

## Requirements / invariants (numbered, testable)

1. **Reckon record keyed on the staged fingerprint.** `stamp_reckon(root, payload)`
   mirrors `stamp_staged` (same lock/CAS/merge) and writes `lastReckon` (a sibling
   of `lastValidation`) into `quality-state.json` plus one row in
   `.harness/runs/reckon-results.jsonl`, carrying
   `{stagedFingerprint.sha256, verdict, at, note}`.
2. **Reckon required only for risk-bearing surfaces.** A reckon is required iff the
   staged change matches a profile flagged `reckon: true` in the policy. A change
   that touches only non-flagged profiles (tests, specs/docs) requires no reckon —
   the common path stays zero-friction.
3. **Block on a missing/blocker/stale reckon.** With a reckon required and the
   staged surface changed, `check_reckon` BLOCKS when there is no `lastReckon`, when
   its verdict is not `no-blocker`, or when its fingerprint does not match the
   current staged fingerprint. A matching `no-blocker` reckon passes.
4. **Fingerprint binding stales a resolved reckon for free.** If the reviewer says
   FIX and the fix changes the surface, the new fingerprint no longer matches the
   old reckon record, so a fresh reckon is required — no extra bookkeeping.
5. **Commit-gate join.** The pre-commit hook runs both `check_staged` and
   `check_reckon` and blocks (exit 1) if EITHER blocks; warns from either surface
   print but do not block.
6. **Fail-open on the reckon gate's own error.** `check_reckon` degrades to
   warn/pass when the policy is absent/disabled, when no profile is flagged
   `reckon: true` (migration window), or when `quality-state.json` is missing or
   corrupt. It blocks ONLY when it positively confirms a risk-bearing changed
   surface AND the absence of a matching no-blocker reckon. A broken reckon gate
   never wedges a commit.
7. **`--no-verify` escape is audited.** A `--no-verify` bypass of a risk-bearing
   commit without a matching reckon is recorded append-only by the post-commit
   audit (a `dimension: "reckon"` row); the auditor never raises and never blocks.
8. **Status verbs.** `reckon --record --verdict no-blocker|blocker` stamps the
   verdict against the CURRENT staged fingerprint; `verify-status [--json]` reports
   the gate decision, the reckon decision, the staged fingerprint, and
   `readyToCommit` (both dimensions non-blocking).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Mirror the proven SPEC-137 gate machine for the reckon half | `validation_stamp.check_staged/stamp_staged` already blocks a commit on the staged fingerprint; a second dimension that reuses the same fingerprint/lock/CAS cannot drift from it |
| "Both passed?" must be mechanical, not memory | Owner decision 2026-07-20 (Option A, HARD commit-gate on the ledger); the gate‖reckon join was manual prose in the overseer-loop playbook |
| Reckon required only for risk-bearing roots (conservative) | The common path (docs/tests) must stay zero-friction; only the engine / gate-internals / hooks (the `code` profile: `scripts` + `tools`) carry real ship-blocking risk |
| Fail-open on the reckon gate's own error | A broken guard must never wedge the agent — mirrors the SPEC-137 migration-window degrade and `gate_hold_guard.py`'s fail-open-by-design; the validation gate still fails closed on missing state, so this half stays additive |
| Extend the gate-hold-guard commit-interception seam | `depends-on: gate-hold-guard` (SPEC-156); the commit-gate-on-ledger is the natural extension of that guard |

## Gherkin scenarios (UI surfaces only)

Included per the plan brief to map each reckon check; the spec-pack gate enforces
that every id resolves to a named check in the Validation scenario.

```gherkin
Feature: The reckon dimension gates a risk-bearing commit on the ledger

  Scenario: [pvr-1] a risk-bearing change with a passing gate but no reckon is blocked
    Given a staged change to the risk-bearing surface and a recorded gate pass
    When the reckon gate evaluates the commit
    Then it blocks because no reckon is on record for the staged surface

  Scenario: [pvr-2] a matching no-blocker reckon clears the reckon gate
    Given a recorded no-blocker reckon for the current staged fingerprint
    When the reckon gate evaluates the commit
    Then it passes

  Scenario: [pvr-3] a blocker verdict blocks the commit
    Given a recorded reckon whose verdict is blocker
    When the reckon gate evaluates the commit
    Then it blocks

  Scenario: [pvr-4] a stale reckon record does not match the staged fingerprint
    Given a no-blocker reckon recorded against a different fingerprint
    When the reckon gate evaluates the commit
    Then it blocks because the fingerprint does not match

  Scenario: [pvr-5] a non-risk surface needs no reckon
    Given a staged change that touches only a non-risk-bearing profile
    When the reckon gate evaluates the commit
    Then it passes without requiring a reckon

  Scenario: [pvr-6] the reckon gate fails open when not adopted
    Given no profile is flagged reckon or the policy is disabled
    When the reckon gate evaluates a risk-bearing change
    Then it degrades to pass or warn rather than blocking

  Scenario: [pvr-7] the commit-gate joins both dimensions
    Given a passing gate but a missing reckon
    When the pre-commit hook runs
    Then it blocks, and it passes only once both the gate and the reckon clear

  Scenario: [pvr-9] the no-verify escape is recorded by the post-commit audit
    Given an unreckoned risk-surface commit made with --no-verify
    When the post-commit audit runs
    Then a dimension "reckon" row lands in commit-audit.jsonl, while a properly
    reckoned or docs-only commit stays silent
```

## Ceilings (upgrade paths)

- Risk-scoping is a single boolean flag on the profile map. Today only the `code`
  profile (`scripts` + `tools`) is flagged; if a project needs finer risk roots,
  split the profile in `project.json` — no code change. If no profile is flagged,
  the reckon gate is dormant (migration window).
- The reckon verdict is a single `no-blocker`/`blocker` value recorded by the
  overseer after reading the reviewer's output; the reviewer content itself is not
  parsed. Upgrade to a structured reviewer-result binding only if a consumer needs
  the findings, not the verdict.
- The heartbeat that reconciles the parallel gate‖reckon launch is a playbook
  ritual + a ScheduleWakeup fallback, not enforced code. The commit-gate is the
  teeth; the heartbeat is convenience.

## Test strategy

- Behaviors to verify: invariants 1-8, driven hermetically against scratch git
  repos with a seeded quality-state; the JOIN (invariant 5) drives the real
  pre-commit hook.
- Edge cases: missing vs blocker vs stale reckon; non-risk surface; no-marked-
  profile and disabled-policy fail-open; `lastReckon` co-existing with
  `lastValidation` (neither clobbers the other).
- Regression risks: the reckon gate must never fail closed on its own error;
  docs/tests-only changes must never require a reckon; `stamp_reckon` must not
  disturb `check_staged`.
- Coverage impact: enforced via `testing/scenarios/pvr_parallel_verify.py`.

## Validation

- `python testing/scenarios/pvr_parallel_verify.py` — the hermetic acceptance
  scenario; every Gherkin id above resolves to a `check("pvr-…")` there.
- `python scripts/harness.py verify-status --json` — the join view shape.
- Registry lockstep: `python testing/scenarios/cli_registry.py` (FROZEN_TOP_LEVEL
  bumped with `reckon` + `verify-status`) and `python testing/scenarios/cc_cli_catalog.py`.
- `python testing/scenarios/pvg_precommit_gate.py` — the SPEC-137 gate half still
  green (the reckon addition is a sibling, not a change to it).

## Amendments

### A1 — the third leg: `mutate` joins gate‖reckon on the commit ledger, 2026-07-30

The mutation-probe oracle (SPEC mutation-probe-oracle) shipped observe-only and
reserved its control phase: "the verb never fails; a future gate check is the
control phase". This is that phase, added as a THIRD dimension of the same
ledger rather than as teeth inside the verb.

- **Evidence.** `oracle mutate` now appends ONE run-level row per run to the
  shared defect sink `.harness/state/defect-telemetry.jsonl`:
  `{kind: "mutate-run", diff, stagedFingerprint, counts{killed,survived,error,
  timeout,skipped}, scenario}`. The fingerprint is `manifest_fingerprint(
  staged_manifest(...))` — the SAME key the gate and reckon legs use, so all
  three dimensions stale together when the surface moves. Survivor rows
  (`kind: "mutate-survivor"`) are unchanged; they could never answer "was this
  surface probed at all?", which is precisely what the leg must know.
- **Decision.** `validation_stamp.check_mutate(root)` mirrors `check_reckon`:
  same manifest/fingerprint/profile map, and the SAME conservative scope — a
  mutation probe is required only where a reckon is required (`reckon: true`
  profiles). Matrix: not required → **pass**; newest `mutate-run` row for the
  current fingerprint with `counts.survived == 0` → **pass**; survivors with a
  `mutate-waiver` row for the same fingerprint → **warn** carrying the waiver's
  reason; survivors without one → **block**; no fingerprint-matching run row →
  **block** ("no oracle mutate run against the staged surface").
- **Waiver.** `harness.py oracle waive --reason "<text>"` appends
  `{kind: "mutate-waiver", stagedFingerprint, reason}`. An empty/whitespace
  reason is REFUSED (`HarnessError`, rc 2) and writes nothing: a waiver without
  a stated judgement is a silent bypass. The two standing tolerated classes are
  `_demo`/test-code-assert survivors and `(fallback)` pre-existing-code
  survivors. The waiver is fingerprint-keyed, so it stales with the surface.
- **Fail-open.** ANY internal error (unreadable or malformed sink, git failure)
  degrades to **warn**, never block — the invariant-6 rule extended verbatim to
  the third leg. `check_mutate` deliberately does NOT write the bypass ledger:
  the gate/reckon rows already record every waved-through commit, and the
  ledger's kind-set is asserted exactly (pvg-6).
- **Join.** Both consumers gained the leg: `verify-status` payload carries
  `mutate`/`mutateReason` and `readyToCommit` is now gate ∧ reckon ∧ mutate all
  non-blocking; `tools/hooks/precommit_validation_gate.py` runs `check_mutate`
  in the same loop (import-light: no new import, `validation_stamp` already
  loaded). Invariants 5 and 8 read with three dimensions instead of two.

Known consequences (documented landmines, deliberately not code):

1. The ship commit of this leg touches `scripts/` — the leg is live for its own
   integration. The overseer runs `oracle mutate` (and waives the judged
   classes) before committing it.
2. Rows written to the sink DURING a gate run land in the swapped tree and are
   discarded with the gate-hold (`.harness/state` is moved aside). The ritual
   already runs `oracle mutate` BEFORE `gate-staged`, so the ordering protects
   the row; running the probe inside a live gate window silently loses it.

Teeth: `pvr-11a..f` (the six-cell `check_mutate` matrix, divergent fixtures per
cell) and `pvr-7` (the real hook now blocks on the mutate leg alone and passes
only when all three clear); the producer side is `mpo-4`.
