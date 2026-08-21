# SPEC-174 — agy accept-edits / coding lane (cli-agent write transport)

Status: SPEC-174, proposed 2026-08-06 (acceptance: `testing/scenarios/antigravity_coding.py`).

Supersedes the DEFERRED parking lot in `harness-exec-transport.intake.md` (door
NEW). The intake's un-defer conditions were met 2026-08-06 (owner directive:
full parity; ToS risk owner-accepted; Windows accept-edits probe PASSED), and
the security gate was owner-resolved in-chat (escalation `route-72eb64c2`,
profile `security`, rule-of-two). This spec freezes what that lane must hold.

## Goal

Give the `agy` (Google Antigravity) cli-agent executor an accept-edits / coding
lane at parity with the codex/kimi/claude write lanes: it reads a
harness-assigned workspace, makes real file edits inside it, and returns them to
the harness under the SAME confinement + accounting boundary every other vendor
rides — without ever trusting agy's own permission gate and without a billed
Gemini API key. Inference stays available; coding is the added capability.

## Applicability

- `tools/agy_worker.py` (`_run_agy`, `_agy_cmd`, `main`) — the worker gains a
  coding mode; the inference path is unchanged.
- `.harness/routing/executors.json` `antigravity` card — `repoAccess`,
  `commandTemplate`, and a coding spawn profile.
- The existing spawn seam it reuses, NOT rebuilds: `run_one_worker`
  (`scripts/harness_lib/workflow_run.py`) already spawns the worker in
  `cwd = workspacePath` under `sandbox_spawn` (icacls confinement); edits return
  via `workflow_merge_plan` diff/rollback.
- Promotion surface: production coding/implementer task-profiles, gated by
  `spawn_guard` / trust-tier.

Does NOT cover: the inference lane (shipped in shadow, c12babe); rebuilding
codex's apply_patch sandbox (reuse its lessons); widening `trustTier` gating
semantics (declared-only today, DW.1); a live-`agy` integration test (the
binary/SEAT is not present in CI — the acceptance stubs the `_run_agy` seam, as
the inference scenario already does).

## Requirements / invariants (numbered, testable)

1. **The harness is the write boundary, never agy's self-gate.** agy's own
   `--mode accept-edits` / require-review gate is NOT trusted (it reportedly
   lands edits even when review is configured — discuss.ai.google.dev 169250).
   The write boundary is the harness: `sandbox_spawn` icacls deny-ACE
   confinement to the assigned workspace, plus `workflow_merge_plan` diff +
   rollback at merge time. A coding-lane worker MUST run through that seam.
2. **Coding lane runs in the assigned workspace cwd, not a private tempdir.**
   For a write-allowed spawn, `_run_agy` runs agy in the harness-assigned cwd
   (`run_one_worker`'s `workspacePath`, a git worktree / temp-copy), NOT the
   `tempfile.mkdtemp` the inference lane uses. The inference lane keeps its
   throwaway cwd unchanged.
3. **`--add-dir <workspace>` is mandatory for the coding lane.** Headless agy
   auto-denies EVERY tool (read_file, write_file, command) when it cannot prompt
   and no workspace is declared; `--mode accept-edits` alone is not enough
   (probe 2026-08-06). The coding argv MUST pass `--add-dir <assigned-cwd>` so
   file read/write inside the workspace is auto-allowed. Absent it, no edit lands.
4. **`--mode accept-edits` for the coding lane; inference passes neither flag.**
   The coding argv carries `--mode accept-edits`; the inference argv carries
   neither `--mode accept-edits` nor `--add-dir` (so it stays pure prompt
   inference — agy auto-denies file tools with no workspace).
5. **Shell stays denied; `--dangerously-skip-permissions` is never passed.** In
   both lanes the flag is forbidden (existing invariant). agy's headless
   `command(...)` tool stays auto-denied by default; the lane does NOT add a
   blanket shell allow-rule to `~/.gemini/antigravity-cli/settings.json`. File
   edits allowed, shell denied — the posture the probe confirmed.
6. **Deletions land via the merge plan, not an agy allow-rule.** `--add-dir`
   auto-allows write but NOT delete (probe finding: deletion is not "writing").
   The lane does NOT widen agy's permissions to allow `delete`; a worker that
   needs a file gone leaves it, and `workflow_merge_plan` applies the deletion
   at merge time from the workspace diff.
7. **`repoAccess: repo` on the antigravity card.** Flipped from `none` so the
   result validator (`result_contracts.executor_repo_access`) permits a coding
   worker to claim file reads/edits — the same declaration codex/claude/kimi
   carry. Single card; the inference use simply spawns write-disallowed.
8. **Auth boundary unchanged: OS-keyring SEAT, no key in argv, no billed key.**
   The coding lane keeps the inference lane's auth posture exactly — the
   Antigravity SEAT via OS keyring, no secret in argv, no `*_API_KEY` env.
9. **Third-party trust tier preserved; promotion is spawn-gated.** agy stays
   `trustTier: third-party`. A production coding/implementer task-profile that
   may spawn agy is gated behind `spawn_guard` / trust-tier / frontier-ack
   (DW.1 fork boundary). Out of shadow ≠ ungated.
10. **`--print-timeout` carries a Go duration unit.** The argv passes
    `f"{print_timeout}s"`, never a bare int (which fails `missing unit in
    duration`, rc=2, before the model runs). Already fixed (c45c7f6); pinned
    here as a standing regression guard against the shipped bug.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Harness ACL is the boundary, agy's gate untrusted (R1) | discuss.ai.google.dev thread 169250 (agy lands edits under require-review); same posture as every other vendor card |
| Reuse `run_one_worker` cwd + `sandbox_spawn` seam, don't rebuild (R2) | Intake Q2 verdict (option ii, harness-owned worktree); `workflow_run.py:142-179` (cwd=workspacePath, sandbox_spawn chokepoint, SPEC-148) |
| `--add-dir` load-bearing, `--mode` alone insufficient (R3, R4) | Windows accept-edits probe 2026-08-06; antigravity.google/docs/cli/headless |
| Shell denied, no skip-permissions (R5) | Probe: `command(...)` auto-denied unless allow-listed; standing agy_worker invariant |
| Deletions via merge plan, not agy permission (R6) | Probe: `delete` did not execute under `--add-dir`; `workflow_merge_plan` already applies workspace diffs |
| `repoAccess: repo` mirrors codex/kimi/claude (R7) | `result_contracts.executor_repo_access` (strict default; relaxation earned by declaration, owner decision 2026-07-27) |
| SEAT auth, no billed key (R8) | OAuth ban-wave (gemini-cli #20632) targeted OAuth-token harvesting, NOT scripting the official binary; `agy_worker.py` module docstring |
| third-party + spawn_guard gate (R9) | DW.1 fork boundary; intake "Promotion path out of SHADOW-ONLY" |
| duration unit (R10) | Shipped bug c45c7f6; `missing unit in duration` (Go time.ParseDuration) |

## Ceilings (upgrade paths)

- **Prose-only envelope.** agy's JSON envelope has no diff field
  (`{conversation_id, status, response, duration_seconds, num_turns, usage}`),
  so edits are surfaced by the workspace diff, not the envelope. If agy later
  ships a structured patch field, revisit whether the merge plan reads it.
- **Argv length ceiling** (inherited): a packet larger than the ~32KB Windows
  argv limit needs a temp-file prompt channel agy has no flag for today; add
  when a packet overflows (existing `agy_worker.py` ponytail note).
- **ToS unconfirmed in writing.** Owner accepted the risk; if a
  seat-agreement / support answer ever lands, record it against R8. Quota-cut
  business-continuity risk is mitigated by `maxConcurrency: 1` — keep it.

## Test strategy

- Behaviors to verify: coding argv includes `--add-dir <cwd>` + `--mode
  accept-edits` (R3, R4) and still never `--dangerously-skip-permissions` (R5);
  inference argv includes neither `--add-dir` nor `--mode accept-edits` (R4);
  coding lane runs in the assigned cwd, inference lane in a tempdir (R2);
  `--print-timeout` carries the `s` unit (R10); the antigravity card declares
  `repoAccess: repo` and `trustTier: third-party` (R7, R9).
- Edge cases: write-allowed flag absent → inference argv shape (no leakage of
  coding flags into the read-only lane).
- Regression risks: the shipped inference lane (`antigravity_inference.py` 6
  checks) must stay green — coding is additive, inference argv unchanged.
- Coverage impact: enforced via `antigravity_coding.py` + the unchanged
  `antigravity_inference.py`.

## Validation

- `python testing/scenarios/antigravity_coding.py` — the new coding-lane smoke:
  stubs the `agy` binary (no live binary, no SEAT, no network) and asserts the
  coding vs inference argv split (`agy-coding-argv-add-dir-mode`,
  `agy-coding-no-skip-perms`, `agy-coding-cwd-is-assigned`,
  `agy-inference-argv-unchanged`); that the REAL `_run_agy` coding branch runs in
  the assigned workspace cwd, subprocess helper stubbed
  (`agy-coding-run-agy-real-cwd`, R2); that the argv adds no permission-widening
  / delete flag (`agy-coding-no-delete-permission`, R6); plus a config assertion
  that the antigravity card is `repoAccess: repo` + `trustTier: third-party`
  (`agy-card-repo-access`, R7/R9).
- `python testing/scenarios/antigravity_inference.py` — 6 checks stay green
  (regression guard for the inference lane); its `_run` helper now also clears
  the two write-lane env vars so the read-only lane is hermetic against an
  ambient coding-lane env (argv + behavior otherwise unchanged).
- `spec-pack` (feature-spec-conformance) green; staged gate via
  `python scripts/harness.py gate-staged`.

## Amendments

(none yet)
