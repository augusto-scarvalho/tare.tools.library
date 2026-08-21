# SPEC — graph refresh is decoupled from the commit path

Status: proposed 2026-07-24 (acceptance: the `refresh_graphs_post_commit.py`
self-check, `doctor`'s `graph-staleness`, and `testing/scenarios/gra_graph_atomic.py`).
Round 2 (T1/T2, 2026-07-24) added atomic publication, an accumulated content key, and
freshness on `graph-status`; the design was refined by 4 NVIDIA ideators + 4 NVIDIA
divergences + a 4-lane Sonnet relay (`docs/research/graph-round2-ideation-divergence.md`,
`.harness/handoff/plan-graph-round2.md`).

SPEC-116 door: NEW. No spec owned `tools/hooks/refresh_graphs_post_commit.py` before
this — it existed only as a hook plus prose in `docs/OPERATOR_GUIDE.md`, which is part
of why a 300-second network call inside `git commit` survived unexamined.

Intake / evidence: `specs/40-features/rt6-parallel-worktree-blindspot.intake.md`,
`docs/research/forensics-2026-07-24-postcommit-blocking-commit.md`.

## Goal

Committing costs what committing costs. Graph freshness is a separate, explicit,
visible concern — never a hidden network call that the person typing `git commit` is
silently paying for, and never something that can make a successful commit look failed
to whoever is orchestrating it.

## Applicability

Applies to `tools/hooks/refresh_graphs_post_commit.py` (the hook itself),
`tools/git-hooks/post-commit` (its invocation), and the `graph-staleness` check in
`scripts/harness_lib/repo_health.py` with its id list in
`testing/scenarios/rh_repo_health.py`.

Widened 2026-07-24 (rule 11): freshness is answered in `graph_providers.staleness`
too, which serves the gate's rebuild trigger (`gate_checks_policy.py`,
`gate_generic.py`), the `graph metrics` CLI and the Graphs screen tile. The first cut
of this spec scoped applicability to the surfaces it had just built and missed the
older one, which is how a second rule survived rule 10.

It does NOT change `harness.py discover`, `harness.py graph-build-code-ast`, or
`graphify_code_ast` — those keep their behavior and become the only refresh paths. It
does not change `route_loop`'s 120s commit budget: once post-commit is milliseconds,
the collision is gone, and tightening that number is tracked separately.

## The defect

`refresh_graphs_post_commit.py` ran the AST rebuild AND `harness.py discover` (the
Gemini → NVIDIA chain) synchronously inside the git post-commit hook, with a 300s
timeout. Git holds `git commit` open until post-commit returns, and
`route_loop._default_commit_stage` allows the commit 120s.

Measured in a detached worktree at HEAD:

| operation | before | after |
|---|---|---|
| `git commit --allow-empty` | 2s | 2s |
| `git commit` touching ONE doc file | **302s** | **2s** |
| `route_loop` budget for `git commit` | 120s | 120s |

The damage was not slowness. `rt6` forensics recorded `headMoved=True` alongside
`outcome=escalated`: the commit SUCCEEDED and the ref advanced while the caller,
having timed out, reported failure. A blocking post-commit can manufacture a phantom
failure out of a real success.

## Requirements / invariants (numbered, testable)

1. **Post-commit is REPORT-ONLY.** The hook builds no graph, spawns no
   `harness.py` subprocess, and makes no network call. It prints what changed and
   what the human may run. Enforced by the self-check, which spies on
   `subprocess.run` and asserts no argv contains `discover` or `harness.py`, and that
   `harness_lib.graphify_code_ast` is never imported.
2. **Commit cost is independent of change size and of network reachability.** A
   commit touching N files costs the same order of magnitude as an empty one.
3. **Post-commit work cannot influence the caller's view of the commit.** This is the
   invariant the defect violated, and it is stronger than "make the hook fast": no
   amount of post-commit work may make a successful commit look failed.
4. **Refresh is explicit.** `harness.py graph-build-code-ast` and
   `harness.py discover <paths>` are the refresh paths. Nothing refreshes implicitly,
   so nothing spends API quota unattended.
5. **Staleness is visible, and answered by CONTENT.** `doctor` carries
   `graph-staleness`. The graph records an `inputKey` — SHA-256 over a schema version
   plus each selected file's repo-relative path and bytes
   (`graphify_code_ast.input_key`) — and the check compares it against a freshly
   computed key. Removing an automatic refresh without a staleness signal would trade
   a loud problem for a silent one: this check IS the counterweight, not hygiene.

   Four states, all pinned by `rh-graph-key`: no graph → ok; key matches → ok; bytes
   changed → WARN naming both key prefixes and the rebuild command; graph without an
   `inputKey` (built before this shipped) → WARN `unkeyed`, which is honest rather than
   guessing.

6. **The counterweight must not cry wolf.** The first cut of rule 5 compared mtimes,
   and mtimes lie constantly in this repo: a `git checkout`, a branch switch, or any of
   the gate's disposable worktrees rewrites timestamps without changing a byte, so the
   check reported stale on an identical tree. An alarm nobody trusts is a disabled
   alarm — the same failure the decoupling exists to avoid, arriving by another door.
   Two behaviours are therefore normative and tested: touching a file without changing
   it stays ok, and reverting an edit back to identical bytes returns to ok WITHOUT a
   rebuild.

7. **Publication is atomic and crash-safe (T1).** All four artifacts (`graph.json`,
   `symbols.json`, `modules.json`, `GRAPH_REPORT.md`) publish via a sibling temp +
   `os.replace` — `os.rename` fails onto an existing path on Windows. `graph.json`
   publishes LAST: it carries the key the freshness surface reads, so a crash before it
   leaves the OLD `graph.json` (old key) reading honestly STALE, never a new key over
   stale sidecars. Windows has no rename-over-open-file, so a concurrent reader can raise
   a transient sharing violation on the replace (bounded-retried) — but a SUCCESSFUL read
   is never torn.

8. **The key ACCUMULATES from parsed bytes, never a re-scan (T1).** The stamped
   `inputKey` is hashed from the exact bytes the build loop reads for parsing. A
   post-build re-scan would re-read a file mutated mid-build and stamp a key matching
   current disk over a graph built from old bytes — a false FRESH. Accumulation makes a
   post-parse edit report STALE, correctly.

9. **An unreadable input FAILS LOUD (T1, plan Q2).** `input_key` raises `UnreadableInput`
   rather than folding an unreadable file in as a marker; freshness reports state
   `unreadable`. v1 hashed a `<unreadable>` marker, so a transiently locked file changed
   the key and reported a FALSE STALE — the noise class the content key exists to kill.
   An honest non-answer, never a wrong one. OPEN, per the plan: if gate-time locking on
   Windows proves common, the fix is a bounded read-retry before reporting `unreadable`;
   the deciding measurement (lock frequency during a real gate) is not yet taken.

10. **Freshness is on the surface the operator uses (T2).** `graph-status` carries an
    additive `freshness` object — `state` (`fresh|stale|no_graph|unkeyed|unreadable`),
    `inputKey`, `storedKey`, `detail`. It reuses the ONE freshness computation `doctor`
    uses (`graphify_code_ast.freshness`); never a second comparison that can disagree.
    Exit code stays 0 in every state — staleness is a report, not a failure. The `T3`
    consumption-time seam that would PREVENT (not just report) a stale read was CUT: two
    independent rounds found its only named caller already served by T2. Its trigger — a
    second genuine new-code caller — is recorded in the backlog, not deferred to "later".

11. **There is ONE freshness rule, and "one" is checked, not asserted (2026-07-24).**
    Rule 10 said `graph-status` must never introduce "a second comparison that can
    disagree". It was enforced only among the surfaces built that day. Meanwhile
    `graph_providers.staleness` — older, and documented in its own docstring as *"THE
    freshness rule … so they can never disagree"* — was still comparing `graph.json`'s
    mtime against the newest `.py`. Two functions, each claiming in prose to be the only
    one.

    Measured divergence, exactly on rule 6's two normative cases:

    | case | clock rule | content rule |
    |---|---|---|
    | touch a file, identical bytes | stale | fresh |
    | revert an edit to identical bytes | stale | fresh |
    | bytes genuinely changed | stale | stale |

    They agreed wherever correctness was at stake, so this was never a wrong answer —
    the clock rule was conservative, false-STALE and never false-FRESH. The damage was
    (a) an unnecessary 3.67s rebuild (measured on this repo: 400 files, 1463 edges; the
    code comment claimed "~1s"), and (b) two surfaces contradicting each other in front
    of one person: after any checkout, branch switch or disposable gate worktree,
    `doctor` reported OK while the Graphs screen showed a red `STALE — graph.json older
    than newest .py` tile about the same graph. That is rule 6's own thesis — "an alarm
    nobody trusts is a disabled alarm" — arriving through the GUI instead of the CLI.

    A third defect was structural rather than temporal: the clock rule scanned its own
    skip-list, a strict SUBSET of the builder's `DEFAULT_EXCLUDE_DIRS`, so it could
    report stale over a `.py` under `coverage/` or `.pytest_cache/` that never enters
    the graph. Content keying answers over exactly the file set the graph was built
    from, because it is the same function the builder stamps with.

    `staleness` now delegates to `graphify_code_ast.freshness` and maps
    `no_graph|unkeyed|unreadable` to stale — every doubt still rebuilds, so the verdict
    got quieter, never blinder. `gm-4` pins the two surfaces EQUAL on all three cases
    rather than pinning either one alone; `gm-3` pins the delegation itself, so a second
    rule cannot regrow inside `graph_providers`.

12. **The one consumer whose staleness changes a DECISION asks for itself (2026-07-24).**
    Rules 5/10/11 make staleness *visible*. Exactly one consumer turns the graph into a
    decision rather than a display: SPEC-159 Phase-2 skipping, live since the owner's
    2026-07-22 flip (`validation.scenarioSkipEnabled`). Its key is
    `scenario_cache_key = sid + closure_h + gate_version`, and `closure_h` comes from the
    graph's edges — so a stale graph returns a scenario's OLD closure, and a scenario
    that just gained an import keeps its old key, still reads "unaffected", and is
    SKIPPED. The false-skip detector cannot catch it, because the detector only observes
    scenarios that RUN. `load_graph`'s fail-open note covers the file ABSENT from the
    graph (FB-3 attributability); it does not cover the file whose EDGES moved.

    This was not reachable in practice, and the reason is the point: the gate rebuilds
    the graph (`check_knowledge_graph_policy`, core-checks) before it partitions skips
    (`gate == "scenarios"`). But that ordering is not a safety property — it is
    `knowledgeGraph.enabled` and `graphifyAst.enabled` happening to be on, while
    `scenarioSkipEnabled` is a third, independent flag. Three flags, one undeclared
    coupling: turn graphify off and the skips ride a frozen graph.

    `ShadowLedger` therefore derives `graph_fresh` in the same breath as it loads the
    graph — a property of the graph THIS ledger read, not of whatever is on disk when a
    later caller happens to ask — and `partition_skips` skips NOTHING unless it is true.
    Every other state, a failure to compute it, and an ABSENT attribute all read as
    untrusted and fall back to the exhaustive order; the default is `False` so that
    forgetting to set it can only cost time, never coverage. Behaviour today is
    byte-identical (the graph IS fresh by then); what changes is that the safety no
    longer depends on someone else's refresh.

    `gac-skip-needs-fresh-graph` pins both directions on a real scratch repo — an
    unjudgeable graph skips nothing, and stamping the key (what a rebuild does) restores
    the skip — so the check cannot pass by the skip being broken generally. The module
    self-check adds the two degenerate cases: `graph_fresh = False`, and the attribute
    deleted entirely. Mutant (drop the guard) KILLED, reporting `unjudgeable=(1 skip/1
    run)` — a skip taken off a graph nobody could vouch for.

## Rationale & sources

| Decision | Source |
|---|---|
| Remove graph work from the commit path entirely | Three independent codex-sol divergence lanes (attachment point / state substrate / ownership) rejected an async-queue fix **3-0** and converged on this — `docs/research/divergence-graph-refresh-round2.md` |
| NOT an async queue with a lock and a drainer | The overseer's own thesis, reviewed by 4 NVIDIA ideators (29 findings, `docs/research/ideators-graph-refresh-queue-round1.md`) and then rejected by all three divergence lanes: it builds a second job system beside git and inherits enqueue atomicity, TOCTOU vs the gate hold, stale locks, unbounded growth and unattended quota |
| Explicit-only `discover` | Kills the "unattended API quota with nobody watching" finding (lens 4 #3) by construction |
| Content key (`inputKey`) rather than mtime | Shipped as mtime first, then replaced the same day: mtime cried stale on an identical tree after any checkout/worktree/branch switch, and a noisy counterweight is not a counterweight. This is the first half of the content-addressed identity the divergence round converged on — the key exists and is authoritative; what remains is the object store and consumer resolution |
| Key stored INSIDE `graph.json`, not a sidecar | One artifact, one identity; a sidecar can be lost or go out of sync with the graph it describes |
| Unkeyed graph WARNs rather than passing | A graph built before the key existed cannot be judged; saying so is honest, assuming freshness is not |
| "One rule" is a TEST (`gm-4`), not a docstring | Both functions already claimed uniqueness in prose and both were sincere; prose cannot see the other file. The same shape as the release leak fixed the same day — two derivations of one decision, drifting silently — so the fix has the same shape too: one callee, and a check that the callers agree |
| `staleness` delegates rather than the reverse | The content key is the authoritative identity (rule 5) and is already what the builder stamps; the clock was a proxy for it. Delegating also costs almost nothing — measured 587ms → 719ms, because the tree walk always dominated — against the 3.67s spurious rebuild it removes |
| Invariant stated as "cannot influence the caller's view" | The measured `headMoved=True` + `escalated` divergence; "make it fast" would not have forbidden the failure mode |

## Test strategy

The teeth live where the defect lived, not in a new suite.

- `tools/hooks/refresh_graphs_post_commit.py --self-check` is the load-bearing one.
  It spies on `subprocess.run` while `run()` executes against a fixture with BOTH
  changed code and changed doc files — the exact input that used to spend 300s — and
  asserts no argv contains `discover` or `harness.py`, and that
  `harness_lib.graphify_code_ast` is never imported. It also asserts the output names
  the explicit rebuild command, so the human is not left guessing.
  This replaces the previous assertion, which only checked that the dry-run printed
  the words "would rebuild"/"would discover" — wording, not behavior, which is why a
  300s network call inside a commit passed it for as long as it existed.
- `testing/scenarios/rh_repo_health.py` pins the ordered check-id list, so
  `graph-staleness` cannot be dropped silently.
- `testing/scenarios/gm_graph_metrics.py` pins rule 11: `gm-4` asserts the gate/screen
  verdict EQUALS `doctor`'s on all three cases (touch, revert, real change) — pinning
  either surface alone is what let them drift — and `gm-3` asserts the delegation
  exists in `graph_providers`. Mutant (restore the mtime body) KILLED on both `gm-1`
  and `gm-4`, with `gm-4` naming the divergence in its failure message:
  `touch=('stale', 'fresh'), revert=('stale', 'fresh')`.
- Timing is verified by measurement rather than a timed assertion (a wall-clock
  ceiling in a scenario is a flake generator under shard contention): a doc-touching
  commit in a detached worktree went 302s → 2s, equal to an empty commit.

## Validation

- `python tools/hooks/refresh_graphs_post_commit.py --self-check` → OK.
- `python testing/scenarios/rh_repo_health.py` → 7/7, with `graph-staleness` in the
  pinned id list and `rh-graph-key` pinning all four key states (including the
  touch-without-change and revert-to-identical cases that mtime got wrong).
- Measured live on the real repo: unkeyed graph → WARN; rebuild → OK; `os.utime`
  bump with identical bytes → still OK; one added line → WARN naming both key
  prefixes; reverting that line → OK again with no rebuild.
- `python scripts/harness.py doctor` → shows `graph-staleness`, WARN when the graph is
  older than its inputs (observed live), OK otherwise.
- `python testing/scenarios/gm_graph_metrics.py` → 4/4; `gp_graph_providers` 4/4 and
  `gr_graphs_screen` 4/4 unaffected. Observed live after rule 11: `graph metrics` and
  `doctor` print the SAME sentence with the SAME key prefixes
  (`0ec8a7fdd268 -> 3b1b8ba12bc6`) about the same graph — previously one spoke of
  clocks and the other of content.
- `rt6_route_writechain` recovers its write-chain semantics: `outcome=committed`,
  `shaMatch=True`, rollback → `rolled_back` + `cleanAfterRollback=True`, out-of-
  footprint write → `escalated` + `rootUntouched=True`.

## What this does NOT do

- It does not make the graph fresh. It makes staleness **visible and explicit**
  instead of automatic-and-blocking. Someone must run the refresh.
- It does not build the immutable object store, and that is a DECISION, not a debt.
  This section previously described `graphify-out/objects/<key>/` plus rewiring every
  consumer as "the open half" still owed. That text was written from the divergence
  round's converged design and never reconciled with the plan round that followed and
  attacked it. `.harness/handoff/plan-graph-round2.md` is the later, more specific
  record and it CUT both pieces, each with a trigger:

  | cut | reason recorded | trigger to revisit |
  |---|---|---|
  | object store `objects/<key>/` + reaper | "buys multi-version retention nobody asked for", needs a disk-growth policy with no daemon to enforce it; T1's atomic publication already captures the correctness half | something needs a HISTORICAL graph |
  | migrating the ~42 existing `graph.json` readers | divergence 2 called it ceremony, divergence 3 disproportionate; old readers keep reading a file T1 makes atomic and self-consistent | — |
  | the `resolve_code_graph` seam (T3) | its one named caller was already served by T2 | a SECOND genuine new-code caller |

  Leaving the spec asking for work two independent rounds had rejected is the same
  defect rule 11 fixes in code — one decision, two records, drifting — so it is
  corrected here rather than carried. What a consumer CAN still do is read a graph
  older than the tree; after rules 11 and 12 that is reported honestly on every
  surface, and prevented in the one place where it would change a decision instead of
  a display.
- It does not fix `rt6`'s guard blind spot inside a shard (the guard reads the copy's
  empty index and cannot fire). That survives the timeout fix and is tracked
  separately as `rt6-shard-guard-blindspot`.
