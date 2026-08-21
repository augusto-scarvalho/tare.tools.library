# SPEC-156 — Gate-hold guard: mechanize SPEC-137 during the gate window

Status: SPEC-156, proposed 2026-07-20 (acceptance: `testing/scenarios/ghg_gate_hold_guard.py`).

## Goal

Make SPEC-137 ("never commit / mutate git / write `.harness` while a gate is in
flight") a MECHANICAL guardrail instead of memory. A PreToolUse hook keys on the
deterministic signal "an active gate-hold exists" and denies the dangerous
actions for the gate's duration; a companion `gate-staged` verb detaches the
gate at the source so a foreground timeout hard-kill can no longer strand an
orphaned hold. The guard is GENERAL — it applies to any context (the overseer
loop, a manual dev session, another workflow), because it knows nothing about
who launched the gate, only that a hold is present.

## Applicability

- `tools/hooks/gate_hold_guard.py` — a PreToolUse hook on `Bash|Edit|Write|MultiEdit`
  (registered in `.harness/capabilities.json` + `.claude/settings.json`).
- `harness.py gate-staged` — the detached-launch verb (`scripts/harness_lib/gate_staged.py`,
  registered via `scripts/harness_lib/cli_registry.py`).
- The signal is `scenario_isolation.hold_dirty_baseline`'s hold:
  `.harness/runs/gate-hold/<name>/hold.json` (its `created` stamp + `entries`),
  which exists for the WHOLE scenarios phase and is released in a `finally`.

Does NOT cover: the spec-pack phase (runs AFTER the hold releases, when the tree
is already back to the owner's real content — no strand risk); the gate
subprocess's own file writes (not tool calls, so PreToolUse never sees them);
reads (never blocked). It is not a security boundary against a malicious actor —
it mechanizes a discipline against accidental corruption, and fails open.

## Requirements / invariants (numbered, testable)

1. **Active-hold signal.** A hold is active when `.harness/runs/gate-hold/<name>/hold.json`
   exists, `<name>` does NOT end in `-recovered`, and the manifest's `created`
   stamp is fresher than the staleness ceiling. Nothing overseer-loop-specific.
2. **Deny mutating git under a hold.** With an active hold, a Bash command whose
   git invocation mutates the worktree/index/HEAD
   (`commit|add|reset|restore|checkout|merge|rebase|cherry-pick|stash|am|revert`,
   including `git -C x commit` and `git commit --amend`) is DENIED.
3. **Allow read-only git + push under a hold.** `git status|log|diff|show` and
   `git push` are ALLOWED — they carry no mutating verb and cannot corrupt the
   held baseline.
4. **Deny held-path writes under a hold.** With an active hold, a Write/Edit
   whose target is under `.harness/`, is `docs/IMPLEMENTATION_BACKLOG.md`, or is
   listed in the hold's `entries` is DENIED. Unrelated writes are ALLOWED.
5. **No hold → allow.** With no active hold the hook is a near-zero-overhead
   no-op (one directory existence check).
6. **Fail-open on stale.** A hold whose `created` stamp is older than the
   staleness ceiling is treated as an orphan: the action is ALLOWED with a
   stderr warning to run the scenarios gate to recover it.
7. **Fail-open on the hook's own error.** Any exception in the hook's own logic
   (unparseable payload, unreadable manifest, unexpected shape) → ALLOW. The hook
   fails CLOSED (exit 2 + stderr, the `protect_files.py` deny protocol) ONLY when
   it positively confirms an active fresh hold AND a dangerous action.
8. **Detached gate.** `harness.py gate-staged` launches `validate --staged`
   through the mediated `processes.launch_detached` spawn, tees to
   `.harness/runs/gate-staged-<ts>.log`, writes a completion marker with the exit
   code, and returns immediately with the log path + PID — the foreground gate
   can no longer be hard-killed mid-run.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| SPEC-137 must be mechanical, not memory | SPEC-137 (CLAUDE.md); two concrete incidents — foreground hard-kill → orphan hold; a write to a held path lost when the gate released its copy |
| Key on the gate-hold signal only (general, deterministic) | `scenario_isolation.hold_dirty_baseline` creates the hold for the whole scenarios phase (`spec_test_gate.py` baseline_hold create-before-loop / release-in-finally) — true for any `validate --staged`, any context |
| Staleness by the `created` stamp, 30-min ceiling | hold.json's own `created` field (crash-adjacent ref used by `_recover_stale_holds`); gate caps at ~15 min, so 30 min is safely past a real run |
| Fail-open always; fail-closed only on confirmed hold + danger | a broken guard must never wedge the agent (mirrors `subagent_gate_wait.py`'s fail-open-by-design) |
| Reuse `processes.launch_detached` for the detached gate | it is the sanctioned mediated detached spawn (spawn-ratchet home); Windows CREATE_NEW_PROCESS_GROUP + hidden console, POSIX start_new_session, log tee, immediate pid return |

## Gherkin scenarios (UI surfaces only)

Included per the plan brief to map each guard check; the spec-pack gate enforces
that every id resolves to a named check in the Validation scenario.

```gherkin
Feature: Gate-hold guard mechanizes SPEC-137 during the gate window

  Scenario: [ghg-active-blocks-commit] a commit is denied while the gate holds the baseline
    Given an active fresh gate-hold exists
    When any context tries a tree-mutating git command
    Then the guard denies it and names the hold and the held paths

  Scenario: [ghg-active-blocks-held-write] a write to a held path is denied under a hold
    Given an active fresh gate-hold exists
    When any context tries to write under .harness/ or the backlog
    Then the guard denies it

  Scenario: [ghg-readonly-git-allowed] read-only git and push pass under a hold
    Given an active fresh gate-hold exists
    When the context runs git status / log / diff / show or git push
    Then the guard allows it

  Scenario: [ghg-no-hold-allows] with no hold the guard is a no-op
    Given no active gate-hold exists
    When the context commits or writes anything
    Then the guard allows it

  Scenario: [ghg-stale-fail-open] a stale hold fails open with a warning
    Given a gate-hold whose created stamp is older than the staleness ceiling
    When the context tries a mutating action
    Then the guard allows it and warns to recover the orphaned hold

  Scenario: [ghg-dead-pid-fail-open] a crashed gate's hold fails open immediately
    Given a fresh gate-hold whose recorded gate pid is provably not running
    When the context tries a mutating action
    Then the guard treats the hold as stale and allows it with the recover warning

  Scenario: [ghg-broken-payload-fail-open] a broken payload never wedges the agent
    Given a malformed hook payload
    When the guard evaluates it
    Then the guard allows the action rather than failing closed

  Scenario: [ghg-producer-contract] the guard reads the real producer's manifest
    Given a hold created by the real scenario_isolation.hold_dirty_baseline on a scratch repo
    When the context tries a commit or a held write during the hold and again after release
    Then the guard denies during the hold and allows after release with the owner dirt restored
```

## Ceilings (upgrade paths)

- Staleness is judged by age of the `created` stamp with a 30-min ceiling, plus a
  dead-pid short-circuit (2026-07-20 audit): a hold whose recorded gate pid is
  provably not running is treated as stale immediately, so a crashed gate no
  longer false-blocks commits for up to the ceiling. An unprobeable pid falls
  back to age-only. A genuine gate running >30 min would
  false-release; safe because the gate caps at ~15 min. Upgrade to a pid-liveness
  probe only if a legitimate long gate ever bites.
- The signal is ONLY the gate-hold. Other in-flight markers (e.g. a future
  verify-ledger) are a deliberate non-goal here — add them as new signals when a
  consumer exists, never a speculative generic in-flight registry.
- Codex hook deny is advisory (see the capabilities `protect-files` note), so the
  guard is claude-enforced for now; a codex mirror is a tracked follow-up.

## Test strategy

- Behaviors to verify: invariants 1-8 above, driven hermetically against a scratch
  `.harness/runs/gate-hold` and synthetic hook payloads.
- Edge cases: `*-recovered` holds ignored; unparseable `created` treated as
  unconfirmable (not fail-closed); read-only git + push allowed under a hold;
  garbage payload → fail-open.
- Regression risks: the git-mutation regex must not false-block read-only git or
  `git push`, and must not false-allow `git -C x commit` / `git commit --amend`.
- Coverage impact: enforced via `testing/scenarios/ghg_gate_hold_guard.py` +
  the hook/verb module self-checks.

## Validation

- `python testing/scenarios/ghg_gate_hold_guard.py` — the hermetic acceptance
  scenario; every Gherkin id above resolves to a `check("ghg-…")` there.
- `python tools/hooks/gate_hold_guard.py --self-check` — the hook's own logic.
- `python scripts/harness_lib/gate_staged.py` — the detached-launch verb self-check.
- Registry lockstep: `python testing/scenarios/cli_registry.py` (FROZEN_TOP_LEVEL
  bumped with `gate-staged`) and `python testing/scenarios/cap_capabilities.py`
  (cap-5: the hook script is in the capabilities manifest).

## Amendments

- 2026-07-28 (row `gate-hold-abandoned-detector`): the abandoned hold becomes
  VISIBLE to the owner, not only to the next gate run. Owner report (unprompted,
  2026-07-27): a power loss mid-gate leaves the live tree at the HEAD baseline
  and the owner's edits parked inside the hold — safe, but indistinguishable
  from data loss to the person at the screen. Shipped, all read-only detection:
  - `scenario_isolation.abandoned_holds(root)` — a hold is reported abandoned
    ONLY when its recorded pid is provably dead (`*-recovered`, live/unprobeable
    pids and unreadable manifests are skipped; a recycled pid false-quiets the
    advisory, bounded by this guard's 30-min staleness warning).
  - `warn_abandoned_holds` fires on EVERY `harness.py` CLI entry (stderr,
    fail-open, one existence check when no hold exists) naming the hold path and
    the restore command.
  - `harness.py hold-recover` — recovery as a DELIBERATE verb (never a side
    effect of an unrelated command): runs the same `_recover_stale_holds` the
    next gate would; refuses when the detector sees nothing; a live-pid hold
    still raises (running gate). Registered in `cli_registry` + frozen surface.
  - GUI: `IncidentsTab` derives a `hold-abandoned` incident card from
    `/api/runtime` (`pidAlive === false && !recovered` — the server already
    computed the fact) with the same parked-not-lost instruction text.
  - Teeth: `testing/scenarios/ghd_hold_abandoned_detector.py` (detector,
    producer-format integration via a real `hold_dirty_baseline` hold with the
    pid rewritten dead, CLI + GUI wiring incl. built-dist string). Ceiling: the
    React predicate itself is source+dist-string checked, not executed — a
    Playwright leg joins `pw_ui_smoke` only if the card ever regresses.

### Amendment v3 — CLI write guard: honest refusal at the dispatch funnel (row cli-gate-hold-write-guard), 2026-07-29

Owner-approved in the 2026-07-29 Q&A (with the drawer-INVERSION recorded as
the preferred end-state in row `gate-hold-inversion`; this guard is the cheap
honest step 1). A write verb during a LIVE hold used to land on the
materialized-HEAD tree and be silently discarded on release — the 2026-07-23
3x loss class, re-measured 2026-07-29 when a mid-hold `intake list` read the
materialized tree as "0 pending" with 364 entries parked in the hold.

- `scenario_isolation.HOLD_WRITE_SENSITIVE` + `live_holds()` +
  `hold_write_guard(verb, root)`: the verb list and logic live with the
  hold's owner (single source; the GUI's `_gate_in_flight` action-flag guard
  is the same doctrine on its own surface). Live = manifest pid alive and
  foreign; abandoned (dead-pid) holds never block (the `hold-recover` flow
  owns those). `HARNESS_SCENARIO_ISOLATED=1` exempts in-gate scenario runs
  (the snapshot/restore IS the contract there). Fail-open: any guard error
  reads as no hold.
- `harness.py main()` consults the guard ONCE before dispatch: a sensitive
  verb under a live hold exits 3 with a reason that names the hold, the pid,
  the discard consequence AND warns that reads during the hold may reflect
  the materialized tree. `gate-staged`/`validate`, `hold-recover`,
  `verify-status`/`status`/`doctor` and every read verb are never guarded.

Teeth: `scenario_isolation` self-check (fires on foreign-live pid; silent on
read verbs, recovery verb, in-gate env, dead pid, no hold — the env is popped
for the fires-arm because the self-check itself runs inside gate scenarios)
+ `ghg-cli-write-guard` (behavior arms + the dispatch wiring pin).
