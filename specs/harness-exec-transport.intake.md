# Intake refinement -- harness exec transport (door NEW, DEFERRED)

SPEC-116 invariant 2 checklist. Parks a deferral so it stops living only in a
checkpoint comment. **Status: DEFERRED -- decision recorded KEEP PARKED
(2026-08-06 research pass; owner-ratified).** No spec is authored and no
acceptance criteria are frozen; the sections below scope the ask and record why
it stays parked, they do not commit a build. See "Decision" below for re-entry.

## Request (verbatim)

Origin is not a user quote but the standing deferral recorded when the
Antigravity (`agy`) executor landed in shadow (commit c12babe, executors.json
`antigravity` card):

> agy OWNS its agent loop (=> cli-agent) [...] Read-only inference;
> accept-edits/coding lane deferred. SHADOW-ONLY: not wired into any production
> task-profile.

And the checkpoint thread that names the parking lot:

> agy accept-edits/coding lane deferred -> HARNESS-EXEC-TRANSPORT.

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search "exec transport" "agy coding" "accept-edits worker write"` | no hit -- `[]` |
| doc-find | `python scripts/harness.py doc-find "worker repo write transport" "coding lane" "apply edits sandbox"` | no hit -- 0 files, `[]` |

Adjacent but does NOT own this ground:

- **compat-executor-routing.intake** (`specs/40-features/`) already parks
  "Adopting kimi/zai agentic CLIs" as its own ask -- same shape (a `cli-agent`
  adoption) but that intake is about **http workers + fallback chains**, not
  about giving a cli-agent a WRITE transport.
- **codex** executor description (executors.json) documents the ONLY existing
  cli-agent write path today: codex's own restricted-token sandbox + apply_patch,
  including the Windows split-writable-root failure
  (`docs/research/forensics-2026-07-25-codex-applypatch-split-writable-roots.md`).
  That is codex-specific transport knowledge, not a general seam agy can reuse.
- `agy_worker.py` is inference-only (positional-argv prompt, reads the JSON
  envelope status, `repoAccess: none`); nothing wires it to a repo.

Decision: **NEW** -- how the harness hands a `cli-agent` worker (agy) a
repo-write transport under the sandbox/confinement model is unspecified
anywhere a check can regress against.

## Goal

One sentence: give the `agy` executor an accept-edits / coding lane -- a
transport that lets a cli-agent worker read a repo, make edits, and surface
them back to the harness under the same confinement + accounting discipline the
codex lane already carries -- so agy can graduate from shadow inference to a
production coding worker.

## Scope

In scope (when picked up):
- The write transport for the `agy` cli-agent: how it gets `repoAccess: repo`
  (today `none`), what confinement wraps its edits, and how edits return to the
  harness (apply-patch style vs worktree diff vs envelope payload).
- Auth boundary carried forward: agy authenticates via the OS-keyring
  Antigravity SEAT, NOT a billed Gemini API key; `--dangerously-skip-permissions`
  stays forbidden. Whatever transport is chosen keeps that intact.
- Promotion path out of SHADOW-ONLY: which task-profile(s) may spawn agy for
  coding, gated behind the usual spawn_guard / trust-tier checks
  (`third-party` trustTier -- DW.1 fork boundary applies).

Out of scope:
- Building it now (this intake is a parking lot; deferred).
- The inference lane (already shipped in shadow, c12babe).
- Re-solving codex's transport; reuse its lessons, don't rebuild its sandbox.
- Widening trustTier gating semantics (declared-only today, DW.1).

## Actors & surfaces

- Actors: `agy_worker.py`, the spawn runner (`run_one_worker` seam), spawn_guard
  (trust-tier + frontier ack), the sandbox/confinement layer, task-profiles.
- Surfaces: internal (worker spawn + edit-return seam); config
  (`executors.json` `repoAccess`/`defaultSpawn`, task-profiles). No new user CLI
  surface anticipated; confirm at spec time.
- UI surface? not anticipated -- confirm when picked up.

## Decision (2026-08-06 research pass, owner-ratified): KEEP PARKED

Two Sonnet-5 research workers + a Fable-5 synthesis investigated the three
questions below. Verdict: **KEEP PARKED.** The write-worker niche is already
double-covered and the ToS gap is unverified, so building the transport buys
nothing that codex/kimi don't already give. The three questions are now
answered enough to make re-entry a decision, not an investigation.

**Q1 -- wanted? NO, not yet (YAGNI).** The repo already has two `repoAccess:
repo` write lanes that cover this niche: **codex** (apply_patch under a
restricted-token sandbox) and **kimi** (`-p` auto-executes writes with no
permission flag -- an unattended-write cli-agent, the closest structural analog
to agy's `--mode=accept-edits`). `agy`'s shadow card offers nothing
differentiated except SEAT-auth economics, which nobody has quantified.
CORRECTION: an earlier draft of this intake named "codex + local-llama" as the
covering pair -- that is wrong. `local-llama` is `repoAccess: none` (http
inference-only); the real second write lane is **kimi**. Only codex, claude,
kimi and the `generic` placeholder carry `repoAccess: repo`.

**Q2 -- transport shape (pre-answered for any future un-defer): option (ii),
harness-owned worktree.** The worker runs in the `run_one_worker`-assigned cwd
(temp-copy / `git worktree`, `workflow_writes.py`); the harness diff/ACL layer
(`sandbox_spawn` icacls deny-ACE confinement + `workflow_merge_plan`
diff/rollback) is the write boundary -- the SAME seam codex/claude/kimi ride, so
wiring agy is ~3 steps, not new machinery: (1) flip `repoAccess` to `repo` on
the antigravity card; (2) point `agy_worker.py::_run_agy` at the assigned cwd
instead of its own throwaway `mkdtemp`; (3) add `--mode=accept-edits` to the
command template. Rejected alternatives: (i) agy's own `--mode=accept-edits`
gate as the SOLE boundary -- rejected because agy reportedly lands edits even
when require-review is configured (discuss.ai.google.dev thread 169250), so its
self-gate is not trustworthy; the harness ACL layer must remain the boundary
(same posture as every other vendor). (iii) envelope-carried patch -- rejected:
agy's JSON envelope is prose-only (`{conversation_id, status, response,
duration_seconds, num_turns, usage}`), no diff field; parsing a free-text diff
reinvents apply_patch and loses the merge-plan safety net.

**Q3 -- ToS: OPEN, and now the LEAD blocker.** Known: Antigravity ToS
contemplates autonomous AI-agent operation ("supervised or autonomous manner",
user "solely responsible"); Google's own headless docs show a sanctioned CI
example; the OAuth ban-wave (gemini-cli discussion #20632) targeted third-party
clients harvesting the SEAT's OAuth token (OpenClaw et al.), NOT scripting the
official binary -- which is what `agy_worker.py` does. But no standalone
Antigravity AUP was found, and nothing in the public ToS explicitly blesses
unattended repo-write of a personal SEAT. Unblocking evidence = a support-ticket
answer or seat-agreement text. Secondary risk: forum reports of unpredictable
quota cuts / bans even for compliant heavy use (business-continuity, partly
mitigated by `maxConcurrency: 1`).

## Un-defer conditions (all three must hold to re-open)

1. **Demand signal** -- codex/kimi write-lane saturation, OR a quantified
   SEAT-vs-billed-key cost win that justifies a third write lane.
2. **Q3 answered in writing** -- ToS/seat-agreement confirmation that unattended
   repo-write on a personal SEAT is permitted.
3. **Windows probe passes** -- a codex-forensics-style probe: create/update/
   delete under `--mode=accept-edits` inside a harness workspace with icacls
   confinement active, ruling out a split-writable-root/reparse-point analog to
   the codex apply_patch failure. (Deliberately NOT the next action -- probing
   before condition 1 is build-effort on a YAGNI-failed lane.)

Next step: NONE. Re-open only when all three conditions above hold; then author
the spec from `specs/SPEC_TEMPLATE.md`, seeded by the Q2 transport answer.

## Update 2026-08-06 (post-probe): UN-DEFER CONDITIONS MET -> ready to spec

The KEEP PARKED verdict above rested on YAGNI (condition 1). The owner then
directed that agy reach FULL PARITY with the other CLI vendors (do everything
codex/kimi/claude do), accepted the ToS risk (condition 2), and authorized a
technical probe. All three un-defer conditions are now satisfied:

1. **Demand -- MET.** Owner directive 2026-08-06: agy at full write parity.
2. **ToS -- risk accepted by owner** (low per research: scripting the official
   binary with keyring auth is distinct from the banned OAuth-harvesting
   pattern). Written confirmation still not obtained; owner owns this risk.
3. **Windows accept-edits probe -- PASSED (2026-08-06).** Live probe of
   `agy v1.1.10` (model gemini-3.6-flash-high) in a throwaway git workspace
   OUTSIDE the real repo. Findings:
   - Headless `agy -p ... --mode accept-edits --add-dir <workspace>` performs
     real file **create + edit** inside the declared workspace, envelope
     `status: SUCCESS`, WITHOUT `--dangerously-skip-permissions`.
   - **`--add-dir <workspace>` is load-bearing**: without it, headless agy
     auto-denies EVERY tool (read_file, write_file, command) because it cannot
     prompt -- `--mode accept-edits` alone is NOT enough. With `--add-dir`,
     "reading and writing files inside your active workspace is auto-allowed"
     (antigravity.google/docs/cli/headless).
   - **Shell stays denied by default** -- a `command(...)` tool auto-denies
     unless explicitly allowed in `~/.gemini/antigravity-cli/settings.json`
     (`{"permissions":{"allow":["command(git)","write_file(src/)"]}}`). This is
     the security posture we want: file edits allowed, shell denied, no blanket
     skip-permissions.
   - **No leak**: writes stayed inside the workspace; the real repo's git status
     was byte-identical before/after -- no codex-style split-writable-root leak
     observed.
   - **Nuance -- delete**: `delete` did NOT execute (deletion is not "writing",
     so it is not auto-allowed by --add-dir). Needs an explicit allow-rule OR
     let the harness `workflow_merge_plan` diff apply deletions at merge time.

**BLOCKER BUG found during the probe (fix regardless of the coding lane):**
`tools/agy_worker.py:130` passes `str(print_timeout)` (a bare int) to agy's
`--print-timeout`, which requires a Go duration WITH a unit (`"300s"`). Every
live invocation fails `rc=2: missing unit in duration "300"` BEFORE the model
runs. Masked because the `antigravity_inference` scenario monkeypatches
`_run_agy` and the lane is shadow-only -- so the existing INFERENCE lane does
not actually work live today. One-line fix: `f"{print_timeout}s"`.

## Refined transport plan (option ii + probe learnings)

1. **Fix the `--print-timeout` unit bug** (`agy_worker.py:130`) -- prerequisite,
   the lane cannot run live without it.
2. **Wire the write path**: flip `repoAccess` to `repo` on the antigravity card;
   run agy in the `run_one_worker`-assigned workspace cwd (git worktree /
   temp-copy) instead of `_run_agy`'s private `mkdtemp`; pass
   `--add-dir <workspace> --mode accept-edits`.
3. **Deletions**: add a scoped `permissions.allow` rule (delete) OR rely on the
   harness merge-plan to apply worker deletions -- decide at spec time.
4. **Keep the boundary in the harness**: `sandbox_spawn` icacls confinement +
   `workflow_merge_plan` diff/rollback stay the write boundary (agy's own gate
   is not trusted -- reliability bug on record). NEVER `--dangerously-skip-permissions`.
5. **Promote out of shadow**: add agy to production coding/implementer
   task-profiles behind spawn_guard / trust-tier.

Next step: author the spec (`specs/SPEC_TEMPLATE.md`) via `harness.py route` --
the technical unknown is retired, this is now a bounded build.

## Update 2026-08-06 (SPEC AUTHORED): superseded by SPEC-174

Spec authored: `specs/40-features/harness-exec-transport.md` (**SPEC-174 — agy
accept-edits / coding lane**). Security gate (`route-72eb64c2`, profile
`security`, rule-of-two) owner-resolved in-chat. This intake is now history; the
normative rules + acceptance live in SPEC-174, verified by
`testing/scenarios/antigravity_coding.py`. Remaining follow-up (R9): promote agy
out of shadow into a production coding task-profile behind `spawn_guard`.
