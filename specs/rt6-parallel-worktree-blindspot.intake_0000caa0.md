# Intake — rt6's dirty-surface guard is blind inside the parallel gate's worktree

> ## RESOLUTION 2026-07-24 (measured) — READ THIS BEFORE ACTING ON ANYTHING BELOW
>
> **Fix 1 shipped** (`a151cc2`): post-commit is report-only, the 302s wall is gone.
> That was the entire cause of the red gate.
>
> **Fix 3 is REJECTED — do NOT implement it.** Passing the real root into rt6's
> guard would be a regression. Evidence:
>
> - rt6's `ROOT` resolves to the shard's own worktree, which is the tree it
>   actually drives. The guard already keys on the correct root.
> - `gate_parallel._pin_sha` checks a shard out at a **dangling commit of the index
>   tree** whenever the index differs from HEAD. Staged content is materialized as
>   committed content, so the empty index is the TRUE answer, not a blind reading —
>   there is no mid-flight commit in that tree to collide with.
> - Routing the real root in would restore the pre-flip behavior: rt6 self-skips on
>   every `gate-staged` run of harness work. That LOSES coverage the parallel flip
>   won by accident — a pristine detached worktree is the ideal hermetic
>   environment for a write-chain proof.
>
> **Repro that settled it:** detached worktree at `HEAD` (`f9e8f40`), shard env
> (`HARNESS_SCENARIO_ISOLATED=1`, `HARNESS_E2E_TIMEOUT_SCALE=3`,
> `HARNESS_PARALLEL_COPY=1`), empty index confirmed → **rt6 5/5 green in 28.6s**.
> The same worktree is where this intake originally reproduced the failure.
>
> **Fix 4 shipped**: both `reason=` truncations widened `[:80]` → `[:400]`, so the
> next failure names itself instead of costing an hour. `route_loop` was checked
> and does NOT truncate upstream (`route_loop.py:629` interpolates the full `{exc}`),
> so rt6's f-strings were the only site.
>
> **Fix 2 (budget consistency) NOT taken** and left open deliberately: with
> post-commit report-only there is no longer a 300s-inside-120s contradiction to
> reconcile. Revisit if any post-commit work ever becomes synchronous again.
>
> Everything below is the ORIGINAL 2026-07-24 investigation, kept verbatim as the
> record of how the timeout was found. Its framing of the guard as a defect is
> superseded by this block.

Raised by the overseer 2026-07-24 while gating the keys-keyring v2 package. The
item failed the gate TWICE, which the overseer playbook makes an escalation
trigger rather than a retry-until-green situation.

## Symptom

`gate-staged` fails on `rt6_route_writechain` — 3 of 5 checks
(`rt6-committed`, `rt6-gate-fail-rollback`, `rt6-unauthorized-create-blocked`),
deterministic across two runs 18 minutes apart. Root failure is the first one;
the other two cascade from the polluted workflow state it leaves
(`implement stage failed: Write lock conflicts detected for workflow WF-...`).

Forensic reason (truncated at 80 chars by rt6's own f-string):

```
rt6-committed — outcome=escalated shaMatch=False headMoved=True docBytes=True
newDirt=[] reason=commit stage failed: Command '['git', 'commit', '-m', 'route: rt6-1 add-rt6-writ
```

## PROOF it is not the keys-keyring change (this is the load-bearing evidence)

Reproduced in a detached worktree created at `HEAD` — i.e. containing NONE of the
v2 work. Verified by inspection inside that worktree: `.env.example` still
present, `keys migrate` still in `cli_registry.py`, no `requirements.txt`, no
`load_ambient_keys` in `common.py`. rt6 failed there with the identical error.

A pre-existing failure reproducing on unmodified HEAD content cannot be caused by
uncommitted work that is absent from that tree.

## Mechanism (partly established, partly open)

`rt6` self-skips on a dirty SPEC-137 validation surface — by design, because it
cannot safely drive a real write-chain while a commit is mid-flight. The guard is:

```python
staged = _git("diff", "--cached", "--name-only", "--", "scripts", "tools", "testing", "specs")
```

evaluated against `ROOT`. Under the 2026-07-21 parallel default, each shard runs
in a **disposable detached `git worktree` pinned to the run's HEAD sha**
(`gate_parallel.py`), where the index is empty — so the guard sees nothing staged
and rt6 RUNS, in exactly the state it declares unsafe. Standalone on the real root
with a dirty index it correctly prints `SCENARIO-SKIP`.

Established:
- rt6 passes 5/5 standalone on the real root with a clean staged surface;
- rt6 fails identically in a HEAD worktree and in the gate's shard copy;
- the `pre-commit` hook is NOT the blocker — run directly in the worktree against
  a docs-only staged file it exits 0, and a manual `git commit` there succeeds.

## ROOT CAUSE (established 2026-07-24 by instrumented repro — no longer open)

`git commit` does not return non-zero. **It TIMES OUT.** The truncated message hid
the word: instrumenting `processes.run_quiet` and printing the full exception gives

```
Command '['git', 'commit', '-m', 'route: rt6-1 ...']' timed out after 120 seconds
```

Measured in a HEAD worktree:

| operation | time |
|---|---|
| `git commit --allow-empty` | 2s |
| `git commit` touching ONE doc file | **302s** |
| `route_loop` budget for `git commit` | **120s** |

The cost is the POST-COMMIT hook, and git holds the commit open until it returns.
`tools/hooks/refresh_graphs_post_commit.py:90-91` runs, SYNCHRONOUSLY:

```python
proc = subprocess.run([sys.executable, "scripts/harness.py", "discover", *docs],
                      cwd=str(root), capture_output=True, text=True, timeout=300)
```

`discover` is the API-assisted chain — real network calls to Gemini, then NVIDIA
Build. Captured verbatim from the probe:

```
[graph-refresh] skip: TimeoutExpired: Command '[... 'scripts/harness.py',
'discover', 'docs/notes/timing-probe2.md']' timed out after 300 seconds
```

**Two budgets that cannot both be right: a post-commit hook allowed 300s inside a
commit the caller allows 120s.** 120 < 300, so a doc-touching commit driven by
route_loop can never survive a cold discovery. The hook's `skip` path exists but
fires only AFTER burning the full 300s — it is an exception handler, not a
precondition check.

Note the hook's skip is also silent from git's perspective (`|| true` on the audit
line, `exec` on the refresh), so a human committing a doc simply watches git hang
for five minutes with no explanation.

### Why the shards are the trigger, not the cause

Nothing broke in the sharding. The 2026-07-21 parallel flip EXPOSED a pre-existing
collision: before it, rt6 ran on the real root, where its dirty-surface guard could
see the staged index and self-skip during any real commit. Each shard is now a
detached worktree with an EMPTY index, so the guard cannot fire, rt6 runs, drives a
real commit, and meets the 300s-vs-120s wall. A cold worktree also gives discovery
no warm cache, so it does maximum work.

### HYPOTHESIS, explicitly unverified — why it surfaced today

The owner rotated all vendor keys into the OS vault on 2026-07-24. If discovery
previously found no usable key it would REFUSE fast (the gate's own refusal fixture
depends on that path); with working keys it makes real API calls that legitimately
take minutes. That would explain why this fires now rather than since the July 21
flip. NOT MEASURED — verify before relying on it.

Note `gate_parallel.py` already documents a related symptom as a known transient
("a scenario's own dirty-surface guard may self-skip under shard load (rt6, pair
5)"). That entry describes a self-SKIP; this is a self-RUN-then-FAIL, the opposite
direction of the same blind spot.

## Why it matters beyond one red gate

Any commit whose staged surface touches `scripts`/`tools`/`testing`/`specs` — the
normal shape of harness work — makes rt6's guard relevant, and the guard cannot
fire in parallel mode. So the gate is red for a reason unrelated to the change
under test, which trains exactly the habit the harness exists to prevent:
treating a red gate as noise.

## The structural fix, in priority order

**1. A post-commit hook must never block a commit on a network call.** This is the
real defect and it hurts humans too — any doc commit today can hang git for five
minutes with no message. Options: detach the discovery step (fire-and-forget, the
harness already has `processes.launch_detached`), or cap it at a few seconds and
let the graph go stale, or make it a pre-check ("would this need the network? then
skip") instead of an exception handler that fires after the full timeout. Fixing
this alone unblocks rt6 and removes a five-minute tax on every doc commit.

**2. Make the two budgets explicit and consistent.** `route_loop`'s 120s for
`git commit` and the hook's 300s for discovery were chosen independently and
contradict each other. Whatever ceiling post-commit work gets must be strictly
below what any caller allows for the commit itself, and that relation deserves a
test rather than a comment.

**3. Give the guard the real root.** Independently of the timeout, rt6's
dirty-surface precondition is unevaluable inside a shard: it reads the copy's
empty index. `_scenario_run_in_copy(..., real_root)` already receives the real
root — pass it through so surface-sensitive scenarios can check the condition
they actually mean. Without this, rt6 keeps running in a state it declares unsafe
even once the timeout is fixed.

**4. Observability** — rt6 truncates the exception at 80 chars, which is why the
word "timed" was invisible and this cost an hour. Widen it, or have route_loop log
the child's full error.

Not recommended: marking rt6 serial-only. It hides the collision instead of fixing
it, and leaves the five-minute commit tax in place for humans.

## Immediate operational question for the owner

The keys-keyring v2 package is staged, fully verified (kv 5/5, kk 5/5, ck 5/5,
ux 34/34, m5 90/90, pc 5/5, qol 13/13, cli_registry 6/6, oracle judged), and
blocked only by this. Options: (a) run the gate `--serial`, where rt6's guard
functions correctly and self-skips, and commit on that verdict; (b) fix rt6 first;
(c) commit with a recorded bypass. The overseer recommends (a) plus this intake,
and did NOT take it unilaterally.
