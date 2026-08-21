# Forensic report — a blocking post-commit hook turned a successful commit into a reported failure

Date: 2026-07-24. Author: session overseer (Opus 4.8). Trigger: `gate-staged` went
red twice while gating the keys-keyring v2 package.

## Summary

A git post-commit hook runs the API-assisted discovery chain synchronously with a
300-second timeout. Git holds `git commit` open until post-commit exits, and
`route_loop` allows the commit 120 seconds. The budgets are structurally
incompatible. The consequence is not slowness: a commit that SUCCEEDS and moves
`HEAD` is reported to the caller as a failure, after which the caller attempts a
rollback against a tree that has already committed.

Cost of diagnosis: roughly one hour, most of it spent on two wrong hypotheses that
an 80-character truncation made attractive.

## Timeline of what was believed, and what was true

| # | Hypothesis | Verdict | What settled it |
|---|---|---|---|
| 1 | Machine contention (a leaked python process was pegging a core for 23h) | **WRONG** | Killed the orphan (81,395s CPU), re-gated on a free machine, identical failure |
| 2 | The keys-keyring v2 change broke it | **WRONG** | Reproduced in a detached worktree at HEAD containing none of the work — verified inside it: `.env.example` present, `keys migrate` still registered, no `requirements.txt`, no `load_ambient_keys` |
| 3 | The pre-commit validation gate was blocking | **WRONG** | Ran the hook directly in the worktree against a docs-only stage: exit 0 in ~1s. A manual `git commit` there also succeeded |
| 4 | Post-commit graph refresh blocks the commit | **CORRECT** | Instrumented the exception, then timed empty vs one-file commits |

Two of the three wrong hypotheses were asserted before being tested. That pattern is
the process finding of this report, separate from the technical one.

## How the root cause was actually found

The scenario reported:

```
reason=commit stage failed: Command '['git', 'commit', '-m', 'route: rt6-1 add-rt6-writ
```

`rt6` formats that reason with `[:80]`, which cut the sentence exactly before the
operative word. Everything downstream of that truncation — including two of the wrong
hypotheses — was reasoning about a *non-zero exit code* that never happened.

Wrapping `processes.run_quiet` in a spy that printed the full `CalledProcessError`
gave the real message:

```
Command '['git', 'commit', '-m', 'route: rt6-1 ...']' timed out after 120 seconds
```

Then direct measurement in a detached worktree at HEAD:

| operation | time |
|---|---|
| `git commit --allow-empty` | 2s |
| `git commit` touching ONE doc file | **302s** |
| `route_loop._default_commit_stage:420` budget | **120s** |

And the hook's own message, captured verbatim, naming the culprit:

```
[graph-refresh] skip: TimeoutExpired: Command '[... 'scripts/harness.py',
'discover', 'docs/notes/timing-probe2.md']' timed out after 300 seconds
```

Localizing further: the pre-commit hook via `py-run.sh` took 1s; the graph refresh
with nothing new to do took 5s; an empty commit took 2s. The entire cost is the
`discover` subprocess in `refresh_graphs_post_commit.py:90-91`, which makes real
network calls to Gemini and then NVIDIA Build.

## The actual defect

```python
proc = subprocess.run([sys.executable, "scripts/harness.py", "discover", *docs],
                      cwd=str(root), capture_output=True, text=True, timeout=300)
```

Three separate problems in one call:

1. **It blocks the commit.** Git waits for post-commit. A human committing a doc can
   watch git hang for five minutes with no explanation, because the hook's failure
   path is `|| true` and its own message goes to a stream nobody is reading.
2. **Its timeout exceeds any caller's patience.** 300s inside an operation that
   `route_loop` allows 120s. Both numbers were chosen independently; nothing asserts
   a relation between them.
3. **The skip is an exception handler, not a precondition.** The hook does print
   `[graph-refresh] skip: TimeoutExpired`, but only after burning the full 300
   seconds. It never asks "would this need the network?" beforehand.

## Why this is a correctness bug, not a performance bug

From the rt6 forensics:

```
rt6-committed — outcome=escalated  shaMatch=False  headMoved=True
```

`headMoved=True` means the commit object was written and the ref advanced. The commit
worked. The orchestrator, having timed out at 120s, recorded `escalated`. Git's truth
and the orchestrator's belief diverged.

**Correction (round-1 review, lens 1 finding #1).** An earlier draft of this report
said the orchestrator "moved to its rollback path against a repository that had
already committed". That was inferred from reading `_default_commit_stage`, NOT
observed — the forensics show `escalated`, not a rollback. The claim is withdrawn to
what the evidence supports: **the caller reported failure after the ref had already
moved.** That alone is sufficient to justify removing the blocking attachment, and
the reviewer noted the same.

Any post-commit work that can block is therefore able to manufacture a phantom
failure out of a real success. That is the invariant to encode, and it is stronger
than "make the hook faster".

## Why the shards are the trigger and not the cause

Nothing regressed in the sharding. The 2026-07-21 parallel default EXPOSED a
pre-existing collision.

`rt6` self-skips on a dirty SPEC-137 validation surface — by design, because it
cannot safely drive a real write-chain while a commit is in flight. Its guard is:

```python
staged = _git("diff", "--cached", "--name-only", "--", "scripts", "tools", "testing", "specs")
```

evaluated against `ROOT`. Before the flip, `ROOT` was the real root: during a
`gate-staged` run the index is dirty, the guard fired, rt6 skipped, and the
collision stayed hidden. Since the flip each shard is a **disposable detached
worktree pinned to HEAD**, whose index is EMPTY — so the guard sees nothing staged,
does not fire, and rt6 runs the very write-chain its precondition exists to prevent.
A cold worktree also gives discovery no warm cache, maximizing the work.

`gate_parallel.py` already documents a neighbouring symptom ("a scenario's own
dirty-surface guard may self-skip under shard load (rt6, pair 5)"). That entry
describes a spurious self-SKIP; this is a spurious self-RUN — the same blind spot,
opposite direction.

## Unverified hypothesis, kept explicitly as one

The owner rotated every vendor key into the OS vault earlier the same day.
Discovery with no usable key refuses fast — the gate's own refusal fixture depends
on that path. With working keys it makes real API calls that legitimately take
minutes. That would explain why this fires today rather than since 2026-07-21.
**Not measured.** It is recorded so a future reader can test it, not rely on it.

## Collateral findings

- **A leaked harness process.** `python -c "import tempfile; print(tempfile.mkdtemp(dir=r'C:\tmp'))"`
  had been running since the previous day, 81,395 seconds of CPU — roughly a full
  core for 23 hours — for a command that should take milliseconds. Killed on owner
  authorization. The spawn site was NOT found by grep in `scripts/`, `tools/` or
  `testing/`; the owner states the harness created it. Open item: a probe that can
  hang spinning is exactly what the repo's own no-raw-subprocess ratchet exists to
  mediate.

  **CORRECTION 2026-07-24 (later the same day, root-caused — 4e30e63).** The
  closing sentence above is wrong on both counts and is retained only to show what
  was believed. It is NOT a spawn problem and the ratchet could never have
  mediated it: the burn happens INSIDE the stdlib call, in-process. Measured on one
  directory with three calls — `os.access(dir, W_OK)` returns True while
  `os.mkdir` raises PermissionError in 0.0003s, and `mkdtemp` is still running
  after 6s. `mkdtemp`'s PermissionError branch does `continue` whenever `os.access`
  claims the directory is writable, and on Windows `os.access` reads only the
  read-only ATTRIBUTE, never the ACL; with `TMP_MAX = 2147483647` a directory
  carrying a deny-write ACE without the read-only bit loops ~2.1 billion times
  burning a core. "The spawn site was not found" is also not a gap in the search:
  a `python -c` one-liner with a raw string is an ad-hoc agent shell command and
  never passes through repo source at all. Fixed by bounding `tempfile.TMP_MAX`
  once in `common.py`, which covers all 30+ call sites. What remains genuinely
  unknown: that specific process died before the analysis and `C:\tmp` grants
  Modify today, so the mechanism is proven but its ATTRIBUTION to that process is
  not.
- **Stale release artifacts.** `release/` regenerated with a large diff when
  `release_integrity.py` was run. Initially reported as scratch files leaking into
  the SBOM; that was **wrong** and corrected — the exclusions filter them. The diff
  was large because the committed artifacts were stale against the tree. Reverted;
  regenerating them deliberately is its own item.

  **CORRECTION 2026-07-24 (later the same day).** Two errors here.
  (a) "Reverted" did not happen. The regenerated artifacts were still sitting
  uncommitted in the tree hours later, mtime 11:49:47 — 16,539 lines of
  SBOM/checksums/provenance. A record that says a thing was undone, while the thing
  sits undone in the tree, is worse than no record: the next reader trusts it.
  (b) `release_integrity.py` DOES verify. The claim that it "generates, not
  verifies" was read off the module docstring (`"""Generate deterministic release
  SBOM..."""`) without running `--help`; the CLI is
  `{generate,verify,external-preflight}` and `verify` is read-only. Run that day it
  is RED, and correctly so.
  The real gap is narrower and was never a regression: the gate's
  `release-integrity` fixture runs `generate` and THEN `verify`, so it checks its
  own freshly written output and is structurally blind to a stale committed
  inventory. It has been that way since the 2026-07-08 baseline import and its
  docstring only ever claimed "internally consistent" — an honest scope, just not
  the one a reader assumed. Measured: the committed inventory listed 631 files for
  a tree of 1183, last refreshed 2026-07-16. Closed by a `release-staleness`
  doctor check (WARN, never a gate — gating it would make every commit that adds a
  file regenerate a release artifact, the exact coupling this document's own
  post-commit finding exists to condemn). Regeneration itself stays an owner act.
- **`keys-meta.json` was untracked and un-ignored.** Operator-specific rotation
  timestamps (no secret values) that would conflict on every clone. Added to
  `.gitignore` alongside its siblings.

## Process findings (the part worth keeping)

1. **An 80-character truncation cost most of the hour.** The word "timed" was cut
   off, and every hypothesis built on the remaining fragment reasoned about a
   non-zero exit code that never occurred. Truncating an exception in a failure
   report is not economy; the first fix in the plan is observability for this reason.
2. **Two hypotheses were asserted before being tested.** Contention and
   keys-keyring were both stated as likely before any measurement. Both were wrong.
   The one that held was the one where a measurement came first. The HEAD-worktree
   reproduction — proving the failure exists in a tree containing none of the
   suspect work — is the shape of evidence that should have come first, not third.
3. **A red gate was, this time, telling the truth about something else.** The
   package under test was clean; the gate was red for an unrelated pre-existing
   defect. That is the most dangerous kind of red, because it trains the habit of
   discounting them. It also means the gate did its job: it surfaced a real bug
   nobody had reported.

## Status at the time of writing

The keys-keyring v2 package is staged (39 files) and fully verified — kv 5/5,
kk 5/5, ck 5/5, ux 34/34, m5 90/90, pc 5/5, qol 13/13, cli_registry 6/6, `oracle
mutate` judged with each survivor traced to its AST node. It is NOT committed,
blocked only by this defect, at the owner's instruction to fix the structural
problem first.

Artifacts: `specs/40-features/rt6-parallel-worktree-blindspot.intake.md` (the
intake), `.harness/handoff/plan-graph-refresh-queue-DRAFT.md` (the proposed fix,
pending multi-model validation).
