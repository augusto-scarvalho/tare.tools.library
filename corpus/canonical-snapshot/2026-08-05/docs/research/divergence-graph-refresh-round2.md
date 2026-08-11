# Divergence round (3x codex gpt-5.6-sol, high) — the queue thesis was rejected 3-0

Launched 2026-07-24 by the session overseer after 4 NVIDIA ideators validated the
thesis (29 findings). Three DISTINCT divergence mandates — attachment point, state
substrate, ownership of the work. All three returned `VERDICT — YOURS`, i.e. each
rejected the queue thesis in favour of its own alternative, and they converged.

Lanes ran `--sandbox read-only` (deliverable is the final message; no file writes).

## Lane 1 — diverge on the ATTACHMENT POINT

# 1. THE ALTERNATIVE — content-addressed, refresh-on-read graph

Remove graph refresh from the commit lifecycle entirely.

A commit should neither refresh a graph nor record that a graph might need refreshing. There is no post-commit subprocess, enqueue, detached drainer, queue file, queue lock, skip clause, or background failure state.

The graph becomes a derived artifact selected by the content it represents.

## Mechanism

Add one shared resolver, for example:

`script/harness_lib/graph_freshness.py`

Its central operation is conceptually:

```python
resolve_code_graph(root, *, build_if_missing: bool) -> Path
```

It performs these steps:

1. Select the input files using the existing `graph-build-code-ast` inclusion and exclusion logic. Do not duplicate that logic.
2. Compute a SHA-256 input key over:

   - a graph-format/schema version;
   - the normalized `.harness/project.json.knowledgeGraph` configuration relevant to the AST graph;
   - each selected repository-relative path, normalized with `/`;
   - the bytes of each selected file.

3. Resolve the immutable artifact:

   ```text
   graphify-out/objects/<input-key>/graph.json
   graphify-out/objects/<input-key>/GRAPH_REPORT.md
   graphify-out/objects/<input-key>/manifest.json
   ```

4. If the object exists and its manifest matches the requested key, return it.
5. If it does not exist:

   - a normal graph consumer synchronously runs the dependency-free AST builder;
   - a status-only consumer reports `missing`;
   - a consumer requiring API enrichment reports an actionable error instead of silently making network calls.

The build protocol is:

```text
compute key K
build into graphify-out/.tmp/<unique-id>/
recompute K after the build
if the key changed: discard and retry once, then fail as graph-inputs-changing
rename the completed directory to graphify-out/objects/K/
if another process published K first: use the winner
```

The destination is immutable. There is no long-lived or stale-recovery lock. Concurrent readers may duplicate one local AST build, but they cannot interleave writes into one graph.

The second key calculation prevents a graph built across a changing source tree from being published under the wrong identity.

## Consumer behavior

Every internal reader of `graphify-out/graph.json` must instead go through `resolve_code_graph()`. Direct reads become invalid because they bypass freshness validation.

The command shapes become:

```text
python scripts/harness.py graph-status
```

Computes the current input key without building and reports:

```text
fresh   <key> <artifact-path>
missing <key>
```

```text
python scripts/harness.py graph-build-code-ast --if-missing
```

Builds the current local AST object only when absent.

```text
python scripts/harness.py discover <paths>
```

Remains the explicit API-assisted operation. It may use Gemini/NVIDIA, block, consume quota, and fail visibly because the operator explicitly requested it. Its output should carry the source input key and provider configuration key.

A graph consumer requiring enrichment must not start `discover` implicitly. It fails synchronously with:

```text
graph-enrichment-missing: run `python scripts/harness.py discover <paths>`
```

A consumer needing only structural discovery automatically builds or reuses the stdlib-only AST graph.

## Gate and worktree behavior

Graph-dependent gate code calls the same resolver for the exact filesystem tree it is examining.

- A disposable shard may build a local AST object in its own `graphify-out/`; its deletion is harmless.
- No API discovery runs automatically in a shard.
- No graph state is written under `.harness/`, so gate-hold swapping cannot lose a queue entry.
- A gate that does not consume the graph performs no graph work.
- A graph-dependent gate may prebuild its AST object before fan-out to avoid duplicate shard work, but this is an optimization, not a correctness mechanism.

No linked-worktree detection is needed. A normal developer worktree and a disposable shard follow the same content rule.

## Existing attachment removal

- Remove the versioned post-commit invocation of `tools/hooks/refresh_graphs_post_commit.py`.
- Retire `tools/hooks/refresh_graphs_post_commit.py`; leaving an enqueue-only version preserves an attachment that no longer has a purpose.
- Do not add `graph-refresh-queue.jsonl`, a drainer, a queue lock, queue health state, or queue-related `.gitignore` entries.
- Route `scripts/harness.py`, the existing `cli_registry.py`, `graph-status`, `repo_health.py`, and every graph consumer through the resolver.
- Add one focused scenario such as `testing/scenarios/gfr_graph_freshness.py`.

The acceptance scenario should prove:

1. Commits touching zero, one, and many files invoke no graph code and no network provider.
2. Commit duration and result remain unchanged with a provider that would hang, fail, or succeed.
3. Changing an included file, relevant graph configuration, or schema version changes the input key.
4. Changing an excluded file does not change the key.
5. A consumer cannot return a graph whose key differs from the current input key.
6. Concurrent builders produce one valid immutable object or equivalent identical winners—never a mixed artifact.
7. Windows path separators and case handling produce the documented canonical key.
8. API enrichment is invoked only by an explicit command.
9. No `.harness/` write is attempted while resolving or building a graph.

# 2. WHY IT IS DIFFERENT

The thesis treats a commit as the event that creates graph-refresh debt. It records that debt immediately and pays it later.

This design rejects that attachment. A commit has no graph consequence at all.

Freshness is a read precondition:

```text
consumer requests graph
        ↓
compute identity of required inputs
        ↓
exact artifact exists? ── yes → read it
        │
        no
        ↓
build locally, or require an explicit enrichment command
```

There is no temporal proposition such as “commit X has not been drained.” There is only a verifiable content proposition: “artifact K does or does not represent inputs K.”

The distinction is structural:

- Thesis: event-driven invalidation plus mutable pending state.
- Alternative: demand-driven selection of immutable derived state.

# 3. WHAT IT BUYS

## Findings made moot by construction

The following 21 findings disappear in their stated form.

| Finding | Why it disappears |
|---|---|
| Lens 2 #1 | No concurrent JSONL enqueue exists. |
| Lens 2 #2 | There is no enqueue-versus-drain race. |
| Lens 2 #3 | There is no detached drainer or stale drainer lock. Immutable publication replaces mutual exclusion. |
| Lens 2 #4 | Persistent discovery failure cannot grow a queue. Content objects may require separate disk cleanup, but failed refresh debt does not accumulate. |
| Lens 2 #5 | No per-commit entries are coalesced, so no commit provenance is lost by unioning them. |
| Lens 2 #6 | Linked-worktree detection is unnecessary. |
| Lens 2 #7 | No queued absolute `root` exists. Inputs are repository-relative and keyed to the tree being read. |
| Lens 2 #9 | There are no competing detached and opportunistic drain triggers. |
| Lens 2 #10 | There is no post-commit work ceiling to relate to `route_loop`’s commit timeout. |
| Lens 3 #1 | Legitimate developer worktrees are not skipped. |
| Lens 3 #2 | No queue write can race with gate-hold acquisition. |
| Lens 3 #3 | Human, CI, submodule, bare-clone, and automation commit taxonomy is irrelevant because commits do not trigger graph work. |
| Lens 3 #4 | No `--git-common-dir` versus `--git-dir` detection is used. |
| Lens 3 #5 | No queued entry can outlive its root. |
| Lens 3 #6 | A legitimate linked worktree follows the same content-freshness rule as the main worktree. |
| Lens 4 #1 | Failure occurs synchronously at the graph consumer or explicit command; it cannot hide behind an optional `doctor` invocation. |
| Lens 4 #2 | There is no repeatedly failing background drainer to classify. |
| Lens 4 #3 | Automatic reads build only the local AST graph. Network quota is consumed only by an explicit `discover` command. |
| Lens 4 #5 | There is no asynchronous `skipped-no-key` state. Explicit enrichment without a key fails directly and visibly. |
| Lens 4 #6 | There is no asynchronous failure loop or alarm-clearing state machine. |
| Lens 4 #7 | There is no detached process whose output needs a separate recovery log. |

## Findings that still require an answer

Eight findings remain relevant.

### Lens 1 #1–#5: forensic accuracy

The alternative does not repair claims in the forensic record.

- Lens 1 #1 still requires evidence before claiming that rollback actually ran against the moved `HEAD`. “Caller reported failure after the ref moved” is already sufficient to justify removing the attachment.
- Lens 1 #2 still requires separating the shard guard blind spot from the unverified key-rotation timing hypothesis.
- Lens 1 #3 still requires source verification if the report retains the precise attribution of the 120-second budget.
- Lens 1 #4 still requires careful wording about whether the 302 seconds were network time, cold-cache work, or both. The alternative is correct under every cause.
- Lens 1 #5 should remain explicitly quarantined as an unverified hypothesis.

None is load-bearing for this design: any potentially blocking graph action is absent from the commit path regardless of why discovery was slow.

### Lens 1 #6 and Lens 2 #8: acceptance of the original invariant

These should be answered with a stronger absence test, not simulated background failure:

- Install a provider spy that fails the test if graph or network code is invoked.
- Commit zero, one, and many changed files.
- Repeat with network unreachable and with a reachable provider stub that would sleep longer than the caller budget.
- Assert that commits succeed, `HEAD` and caller belief agree, elapsed time remains in the same local-operation class, and the provider spy was never touched.

The precise two-second ceiling is secondary. The important assertion is zero attachment.

### Lens 4 #4: stale graph consumption

This is the central obligation of the alternative.

Every graph consumer must compute the required input key and resolve that exact object. It must never fall back to an older object because it happens to be present.

For API-enriched consumers:

- matching AST/source key plus matching provider-configuration key means usable;
- missing enrichment means a named synchronous refusal with an explicit command;
- stale enrichment is never treated as current;
- no key or provider failure can be silently downgraded to a fresh graph.

`graph-status` and `doctor` may expose this for humans, but consumer-side validation is authoritative.

# 4. WHAT IT COSTS

The thesis gives eventual automatic refresh after every commit. This design deliberately gives that up.

Its concrete disadvantages are:

1. **First-read latency.** The first structural graph consumer after a source change pays for input hashing and a local AST build. The commit stays fast because the cost moves to the operation that needs the graph.

2. **No automatic API enrichment.** A repository can remain unenriched indefinitely if nobody explicitly runs `discover`. That is worse than the thesis for operators who expect enrichment to appear automatically after commits.

3. **Consumer migration.** Every direct graph read must use the resolver. One forgotten direct open can silently reintroduce stale consumption. This is a broader migration than adding a queue beside the existing behavior.

4. **Hashing cost.** The simplest correct implementation hashes all selected input bytes on each graph read. That is O(repository input size). A metadata cache could reduce it later, but adding one immediately would recreate mutable invalidation state before measurement justifies it.

5. **Duplicate builds.** Concurrent consumers can perform the same local AST build. Immutable publication prevents corruption but does not prevent duplicate CPU work. A lock can be added later if measurement shows this matters.

6. **Artifact retention.** Content objects consume disk across distinct input keys. Start with an explicit command such as:

   ```text
   python scripts/harness.py graph-prune --keep 3
   ```

   Automatic cache policy is unnecessary for correctness and should wait for measured growth.

7. **Schema discipline.** Builder-semantic changes must bump the graph format version included in the key. Forgetting that bump can reuse an artifact built under old semantics.

8. **Failure moves to point of use.** A graph-dependent command can now stop while hashing or building. That is operationally less convenient than having a fresh artifact waiting, but it is truthful: the failure is reported by the operation that actually requires the graph.

The thesis is better when immediate, unattended, API-enriched eventual consistency is a product requirement. This alternative is better when commit correctness, explicit network spending, and freshness at the consumer boundary matter more.

# 5. VERDICT — YOURS

Choose the content-addressed, refresh-on-read design.

Graph freshness is a property that a graph consumer can compute exactly. Attaching mutable refresh debt to every commit creates a queue, concurrency protocol, worktree taxonomy, hold race, retry policy, quota policy, alarm system, and stale-consumer problem without improving the commit itself.

Remove graph work from commits completely. Build the dependency-free AST graph when it is requested, validate it by content identity, and keep network enrichment explicit.

## Lane 2 — diverge on the STATE SUBSTRATE

# 1. THE ALTERNATIVE — Git history is the pending set

Delete graph refresh from the post-commit execution path entirely. Do not enqueue anything and do not launch a detached process from the hook.

A graph refresh becomes deferred, demand-driven work. The pending set is reconstructed from Git’s existing commit history relative to one per-worktree success marker:

```text
refs/worktree/harness/graph-refresh/processed
```

`refs/worktree/` is important: each legitimate linked worktree gets its own marker and its own `graphify-out/` freshness state. A disposable shard’s marker disappears with its Git worktree administration directory. Nothing under `.harness/` records pending commits.

## Freshness calculation

At the start of a graph-dependent command:

```text
git rev-parse HEAD
git rev-parse --verify --quiet refs/worktree/harness/graph-refresh/processed
```

Call the results `HEAD` and `PROCESSED`.

There are three cases:

1. `PROCESSED == HEAD`: the graph is fresh.
2. `PROCESSED` is an ancestor of `HEAD`:

   ```text
   git merge-base --is-ancestor PROCESSED HEAD
   git diff --name-status -z PROCESSED..HEAD -- <graph-relevant-scopes>
   ```

   The net tree difference is the pending work. Multiple commits are inherently coalesced.
3. The marker is absent, unreachable, or not an ancestor—for example after rebase, reset, or branch switch:

   ```text
   git ls-tree -r --name-only -z HEAD -- <graph-relevant-scopes>
   ```

   Perform a full refresh from the current committed snapshot.

If the diff contains no graph-relevant change, advance the marker without making an API call:

```text
git update-ref refs/worktree/harness/graph-refresh/processed HEAD OLD_PROCESSED
```

Otherwise run the existing discovery implementation in the foreground. Do not recursively invoke `scripts/harness.py`; call its existing Python handler directly. Advance the ref only when:

- discovery succeeded;
- eligible working-tree paths still match the captured `HEAD`;
- `HEAD` has not changed during discovery;
- no gate hold intervened;
- the compare-and-swap `git update-ref ... HEAD OLD_PROCESSED` succeeds.

Failure, missing keys, a concurrent branch change, or an active gate hold leaves the marker untouched. Therefore pending work cannot be lost: the next attempt derives it again.

## Trigger policy

There is no detached automatic drainer.

- Every graph consumer checks the marker before trusting `graphify-out/`.
- A stale graph consumer either performs the foreground refresh or returns a named `graph-stale` outcome. It never silently consumes stale output.
- `python scripts/harness.py graph-refresh` provides an explicit foreground refresh.
- Non-graph harness commands perform only the cheap `HEAD`/marker comparison and print one warning when stale. They do not spend API quota.
- `graph-status` and `doctor` report `HEAD`, processed SHA, relationship, and pending path count.
- With `HARNESS_DISPOSABLE_WORKTREE=1`, API-assisted refresh is refused. The gate runner supplies this explicit marker; ordinary developer worktrees are not suppressed.
- During a gate hold, refresh returns `graph-refresh-deferred: gate-hold`. It writes neither `.harness/` state nor the processed ref.

This is asynchronous relative to committing—the refresh is removed from the commit transaction—but it is intentionally not unattended background execution.

## Concurrency

Foreground refreshes still need to protect `graphify-out/`. Use a process-held advisory lock at the path returned by:

```text
git rev-parse --git-path harness/graph-refresh.lock
```

Use Python stdlib:

- Windows: `msvcrt.locking`;
- POSIX/Git Bash environments using POSIX Python: `fcntl.flock`.

The file may remain after exit, but its existence means nothing. The operating system releases the lock when the process exits, including after a crash. There is no PID record, age threshold, or stale-lock reclamation.

A second graph consumer returns `graph-refresh-busy`; it does not start another discovery process.

## Concrete implementation seams

- `tools/hooks/refresh_graphs_post_commit.py`: remove discovery and detached-launch behavior. Prefer removing the graph-refresh hook registration entirely; a no-op compatibility script is acceptable only if installation currently requires the path.
- `scripts/harness_lib/graph_refresh.py`: calculate freshness, derive pending paths, hold the advisory lock, invoke the existing discovery handler, and advance the per-worktree ref.
- `scripts/harness.py` and `cli_registry.py`: expose `graph-refresh` and require freshness before graph-consuming commands.
- `scripts/harness_lib/repo_health.py`: report marker/HEAD divergence without reading a queue.
- `testing/scenarios/grq_graph_refresh_history.py`: cover commit independence, incremental history, history rewrite, linked worktrees, disposable shards, gate holds, concurrent consumers, failure, and missing keys.

No queue file, queue directory, queue compactor, background launcher, retry scheduler, PID lease, or stale-lock recovery is needed.

# 2. WHY IT IS DIFFERENT

The thesis treats every commit as an event that must be durably captured and later consumed. This design treats the graph as a materialized view of a Git tree.

Git already contains the ordered, durable commit history. The only additional correctness state is “which tree snapshot produced this worktree’s graph?” A single success marker answers that. Pending work is a derived query:

```text
current committed tree − last successfully processed committed tree
```

Consequences follow directly:

- commits do not produce queue records;
- skipping work during a gate hold loses nothing;
- repeated commits require no compaction;
- a failed refresh consumes no pending state;
- branch changes are detected as ancestry changes;
- legitimate linked worktrees remain independent;
- no process is launched merely because a commit occurred.

The structural choice is not a better queue substrate. It is eliminating event queuing in favor of snapshot reconciliation.

# 3. WHAT IT BUYS

## Findings made moot by construction

- **Lens 2 #1 — Windows JSONL append atomicity:** there is no append operation.
- **Lens 2 #2 — drain-while-enqueue race:** there is neither enqueue nor queue truncation.
- **Lens 2 #3 — unsafe stale-lock recovery:** the lock is process-held and automatically released by the OS; file age and PID reuse are irrelevant.
- **Lens 2 #4 — unbounded queue growth:** persistent failure leaves one old ref, not an accumulating backlog.
- **Lens 2 #6 — fragile linked-worktree comparison:** no `--git-common-dir` versus `--git-dir` classification is used.
- **Lens 2 #7 — ambiguous entry root:** there are no entries or stored roots; commands operate in the invoking worktree.
- **Lens 2 #9 — two competing drain triggers:** there is one trigger class—explicit demand from a graph-aware command.
- **Lens 2 #10 — post-commit timeout versus caller budget:** graph refresh has no post-commit duration to compare with the commit caller’s budget.
- **Lens 3 #1 — suppressing legitimate developer worktrees:** every worktree naturally has its own `refs/worktree/.../processed` marker.
- **Lens 3 #2 — gate-hold check/append TOCTOU:** no append can be discarded. If a hold wins the race, the success marker remains old and the work is rediscovered later.
- **Lens 3 #4 — platform-sensitive worktree detection:** no path equality, casing, junction, or common-directory test is required.
- **Lens 3 #5 — queued root vanishes before drain:** no root is queued. Deleting a disposable worktree deletes its local refresh state.
- **Lens 3 #6 — missing negative test for legitimate worktrees:** legitimate worktrees are the ordinary path, not an exception to a blanket skip.
- **Lens 4 #3 — unattended quota consumption:** no background process is allowed to make vendor calls.

## Findings still requiring an answer

- **Lens 1 #1–#4 and #6:** the new substrate does not repair gaps in the forensic proof. Tests must still pin the exact timeout/reporting sequence, isolate shard behavior from key availability, verify the caller’s real budget, distinguish network delay from other discovery work, and reproduce timeout-shaped failure—not merely a non-zero exit.
- **Lens 1 #5:** the key-rotation explanation remains explicitly unverified and non-load-bearing.
- **Lens 2 #5:** implementers must confirm that the graph is a tree-snapshot artifact, not a per-commit provenance ledger. Net diff is correct only under snapshot semantics. If deleted or renamed paths cannot be reconciled incrementally, those cases must trigger a full refresh.
- **Lens 2 #8:** retain an acceptance test proving commits have baseline duration with reachable and unreachable networks. The implementation is structurally independent, but the test prevents graph work from being reintroduced into a hook.
- **Lens 3 #3:** CI, submodules, bare repositories, and disposable automation still need declared behavior. Recommended default: graph consumers refresh their own repository; bare repositories report unsupported; disposable shards refuse API enrichment through the explicit environment marker.
- **Lens 4 #1:** ambient stale warnings on ordinary harness commands and mandatory freshness checks on graph consumers must be implemented; `doctor` alone remains insufficient.
- **Lens 4 #2 and #6:** failure categories and persistence still need a small policy. At minimum, `auth`, `quota`, `network`, `busy`, `dirty-tree`, and `gate-hold` must remain distinguishable, and only successful marker advancement clears staleness.
- **Lens 4 #4:** every graph consumer—not just `graph-status`—must enforce the processed-ref contract.
- **Lens 4 #5:** missing credentials must return a named failure, leave the ref untouched, and prevent a graph-dependent command from treating stale output as fresh.
- **Lens 4 #7:** foreground execution makes the error immediately visible, but durable detailed diagnostics still need a home. Reuse the existing harness event channel if it preserves full errors; otherwise keep one atomically replaced, bounded last-result record in the worktree Git administration directory. It must not become another queue.

# 4. WHAT IT COSTS

The graph is not refreshed promptly after every commit. It remains stale until another harness command notices, and an operator who commits and never invokes the harness gets no refreshed graph. Under “no resident daemon,” that is unavoidable unless commit launches unattended work.

The first graph-dependent command after several commits may pay the entire discovery cost synchronously. The thesis can often finish that work in the background before a consumer arrives.

A history rewrite or switch to an unrelated branch forces a full refresh. A queue containing precise paths could sometimes preserve more incremental information across that transition.

The design depends on the semantics and supported Git versions of per-worktree refs. That must be validated on the project’s Windows Git distribution before adoption.

Foreground-only execution sacrifices automatic retry. Transient network failure remains visible and pending, but nothing retries until the operator or another graph consumer asks again.

Finally, this design only works if Graphify output represents the current tree snapshot. If per-commit provenance is a real requirement, Git history can identify the commits, but replacing the event queue with a net diff would lose required information.

# 5. VERDICT — YOURS

Choose the history-derived, demand-driven design.

The invariant becomes structural because graph refresh no longer has any post-commit execution path. Git already stores the durable sequence the JSONL queue would duplicate, while one per-worktree success ref supplies enough reconciliation state. The thesis offers faster eventual refresh, but pays for it with enqueue atomicity, queue lifecycle, detached-process coordination, stale-lock recovery, unattended quota policy, gate-hold races, and substantially more failure machinery.

The foreground latency is the honest cost. Given the declared no-daemon constraint, it is preferable to make graph consumers pay for freshness when they actually need it than to build a second job system beside Git.

## Lane 3 — diverge on the OWNERSHIP of the work

# 1. THE ALTERNATIVE — hookless commits, Git-history refresh ledger

Remove graph maintenance from the Git lifecycle entirely. A commit records source history; graph freshness is reconciled only when the graph is about to be consumed.

## A. Retire the graph-refresh post-commit hook

`tools/hooks/refresh_graphs_post_commit.py` must no longer run `discover`, enqueue work, spawn a process, inspect changed files, or write state.

Implementation shape:

- Remove its invocation from the checked-in post-commit hook installer/template.
- For one migration release, retain `tools/hooks/refresh_graphs_post_commit.py` as an immediate compatibility no-op so already-installed wrappers cannot invoke the old blocking behavior.
- Update the hook installer so a subsequent sync removes the obsolete invocation.
- Assert that no repository-owned post-commit hook invokes Python, network-capable code, Graphify, or another subprocess.

There is no replacement post-commit queue.

## B. Make harness-managed commits hermetic

Change `scripts/harness_lib/route_loop.py`, at `_default_commit_stage`, so a harness-managed commit never executes ambient Git hooks:

```text
git -c core.hooksPath=<absolute-empty-temporary-directory> commit -m <message>
```

Construct the temporary directory with Python `tempfile.TemporaryDirectory` and pass the command as an argv list without a shell. This is portable to Windows and Git Bash.

Do not rely on:

```text
git commit --no-verify
```

`--no-verify` skips selected verification hooks but does not suppress `post-commit`. The existing `--no-verify` audit machinery should instead record that this commit used the explicit hermetic hook policy.

Repository-owned validation currently reached through pre-commit must become an explicit route pipeline stage before `_default_commit_stage`. Reuse the same checked-in validator implementation; do not duplicate hook logic. The order becomes:

```text
route validation
→ explicit repository validation
→ hermetic git commit
→ seal commit result
→ optional later graph reconciliation
```

Once `git commit` returns zero, `route_loop` captures the resulting SHA and permanently records `commitStatus=success`. No later graph result may alter that field or enter the commit rollback branch.

On `TimeoutExpired`, `route_loop` must reconcile Git truth before deciding that the commit failed:

```text
parent_before = git rev-parse HEAD
run hermetic git commit
if timeout:
    head_after = git rev-parse HEAD
    inspect whether HEAD advanced from parent_before as the intended commit
```

If the ref advanced, the result is “commit succeeded; caller lost the process response,” not “commit failed.” This closes the general `headMoved=True` divergence even without hooks.

## C. Use Git history as the coalescing ledger

Persist one freshness marker beside the graph artifact, for example:

```json
{
  "sourceSha": "<HEAD incorporated by the last successful graph build>",
  "builtAt": "<UTC timestamp>",
  "status": "ok"
}
```

The marker belongs with `graphify-out/`, not in a commit-time queue under `.harness/state/`.

Before any Graphify query/path/explain handler reads the graph, the existing graph command layer reached through `scripts/harness.py` and `cli_registry.py` must run an `ensure_graph_current` check:

```text
git rev-parse HEAD
git merge-base --is-ancestor <sourceSha> HEAD
git diff --name-only --diff-filter=ACMRD <sourceSha>..HEAD -- <configured graph inputs>
```

Behavior:

1. Marker SHA equals `HEAD`: use the graph immediately.
2. Marker is an ancestor and no relevant paths differ: atomically advance the marker to `HEAD` without network work.
3. Relevant paths differ: run one reconciliation over their deduplicated final-tree set:

   ```text
   python scripts/harness.py discover <changed-paths...>
   ```

   Run the code-AST rebuild too when the changed-path classification requires it:

   ```text
   python scripts/harness.py graph-build-code-ast
   ```

4. Marker is missing or is not an ancestor of `HEAD`, as after rebase/history replacement: perform a full configured rebuild.
5. Refresh fails: leave the previous marker untouched and return an explicit `graph-stale` or documented degraded result. Never silently consume the graph as current.

Many commits naturally coalesce into one comparison from `sourceSha` to current `HEAD`. There are no per-commit records to append, compact, relocate, or recover.

The final graph and freshness marker must publish atomically. Concurrent graph consumers still need the existing graph-writer exclusion mechanism—or one narrow cross-platform writer lock if none exists—but that lock protects graph publication only. It is not part of committing.

## D. Gate holds and disposable worktrees

A commit performs no `.harness/` write, so gate holds cannot discard commit-generated refresh state. Git history remains the durable evidence that reconciliation is needed.

Graph reconciliation itself follows these rules:

- During an active gate hold, do not publish a canonical graph or advance its marker.
- A disposable scenario worktree must be identified by an explicit gate-provided marker/environment value, not merely by being a linked worktree.
- In a disposable shard, use the pinned graph only when its marker matches the shard’s `HEAD`; otherwise report graph unavailable or build an isolated disposable graph if that scenario explicitly requires one.
- A normal developer-created linked worktree remains supported.

If a gate-hold race discards a graph publication, the old freshness marker remains. The next consumer detects the same stale range and retries; no commit information is lost.

## E. Acceptance shape

The scenario replacing `grq-*` should prove:

- A deliberately slow, failing, network-using local `post-commit` hook is installed, but a `route_loop` commit still completes with unchanged timing because `core.hooksPath` points to an empty directory.
- A normal commit using repository-managed hooks performs no graph or network work.
- Commits touching one and many documents have equivalent repository-hook overhead, with both reachable and unreachable networks.
- Three commits since the freshness marker cause one reconciliation over the final deduplicated path set.
- Failed discovery does not advance `sourceSha`; a graph consumer reports stale state instead of trusting the old graph.
- A history rewrite makes the marker non-ancestral and triggers a full rebuild.
- A graph publish lost during a gate hold remains detectable because the marker stays behind `HEAD`.
- A legitimate linked worktree is not suppressed; an explicitly marked disposable shard cannot publish canonical graph state.
- A simulated timeout after `HEAD` advances is reconciled as commit success and never enters rollback.

# 2. WHY IT IS DIFFERENT

The thesis retains Git’s post-commit hook as the graph scheduler and tries to make that scheduler safe with enqueueing, detachment, locking, coalescing, stale-lock recovery, skip detection, retries, health reporting, and queue lifecycle rules.

This design removes Git hooks from graph scheduling altogether.

The structural choices are:

- Git commits produce only Git history.
- Harness-managed commits execute with no hooks.
- Git history, not JSONL, is the durable backlog.
- Graph work is triggered by graph consumption, not commit completion.
- Freshness is a checked precondition of every graph consumer, not a background promise.
- There is no detached drainer, queue, retry loop, or unattended API call.

The transaction boundary is therefore exact: commit handling ends when Git truth has been reconciled. Graph maintenance is a separate operation with a separate result.

# 3. WHAT IT BUYS

| Review findings | Result under this design |
|---|---|
| Lens 1 #1 | Still must answer. The exact timeout-to-rollback sequence remains an evidence gap, and the route scenario must demonstrate it. The new timeout reconciliation removes reliance on the inference for future behavior. |
| Lens 1 #2 | Moot for commit correctness. Shards, keys, and cold caches cannot alter a hookless commit. The separate `rt6` dirty-surface blind spot still needs its own fix. |
| Lens 1 #3 | Moot. There is no 300-second post-commit budget nested inside the 120-second commit budget. The ordinary commit timeout still needs independent justification. |
| Lens 1 #4–5 | Moot. Whether discovery was slow because of network, cache state, or key rotation is irrelevant to commit duration because discovery is absent from that path. |
| Lens 1 #6 | Still must answer. A timeout after a ref move remains theoretically possible even without hooks, so the caller must reconcile `HEAD` before reporting failure or rolling back. |
| Lens 2 #1–2 | Moot. There is no concurrently appended queue and no enqueue-versus-drain snapshot race. |
| Lens 2 #3 | Queue stale-lock recovery is moot. Concurrent graph publication still requires single-writer exclusion and atomic output replacement. |
| Lens 2 #4 | Moot. No queue can grow during persistent failure. Git history already contains the outstanding range without duplicating records. |
| Lens 2 #5 | Still must answer in a simpler form. The implementer must confirm that final-tree path reconciliation is sufficient and that no required graph provenance is per-commit. If per-commit provenance exists, Git-range coalescing is unsuitable. |
| Lens 2 #6–7 | Moot. No linked-worktree enqueue heuristic, absolute entry root, or foreign-root queue record exists. |
| Lens 2 #8 | Moot by isolation. A poisoned or reachable network cannot enter the commit subprocess. The acceptance test should still prove this directly. |
| Lens 2 #9 | Moot. There are not two competing drain triggers. |
| Lens 2 #10 | Moot. There is no post-commit ceiling that must fit below the caller’s commit budget. |
| Lens 3 #1 | Moot. Normal linked worktrees are not denied commit-time refresh because there is no commit-time refresh. Disposable behavior is identified explicitly only when graph consumption occurs. |
| Lens 3 #2 | Moot as a data-loss race. A gate hold cannot erase Git history. If it discards a graph publication, the unchanged freshness marker makes the missing work detectable. |
| Lens 3 #3–4 | Moot. Human, CI, submodule, bare-repository, and unknown committers do not need a graph-refresh classification, and no platform-fragile `--git-common-dir` comparison controls enqueueing. |
| Lens 3 #5 | Moot. There are no queued absolute roots that can vanish. |
| Lens 3 #6 | Moot. A normal linked worktree is not conflated with a disposable shard. |
| Lens 4 #1 | Moot under the new contract. An unused stale graph requires no alarm; every actual graph consumer checks freshness before use and reports staleness synchronously. |
| Lens 4 #2 | The repeated-background-failure problem is moot. Exact failure classification is still required in the foreground result so auth, quota, network, and parse failures remain distinguishable. |
| Lens 4 #3 | Moot. Discovery is never started unattended, so there is no background quota burn, retry storm, backoff policy, or circuit breaker. |
| Lens 4 #4 | Still must answer and becomes the central acceptance condition. No graph consumer may bypass the freshness marker. |
| Lens 4 #5 | Still must answer. Missing keys must produce an explicit foreground error or declared degradation, and must not advance the freshness marker. |
| Lens 4 #6 | Background escalation is moot. The remaining rule is simpler: only a successful atomic graph publication advances the marker. |
| Lens 4 #7 | Moot. There is no detached process whose output needs a recoverable log. |

The largest simplification is that Git already provides the durable, ordered, crash-safe history the thesis proposes rebuilding as JSONL. A freshness SHA turns that history into a naturally coalescing backlog.

# 4. WHAT IT COSTS

The first graph-dependent command after one or more commits pays the full refresh latency. If discovery takes five minutes, that command waits five minutes. The thesis can potentially make the graph ready before anyone asks for it.

The graph artifact is no longer promised to be eagerly current. It is only guaranteed current at a guarded consumption boundary. Any tool that reads `graphify-out/graph.json` directly, bypassing the harness graph layer, becomes unsafe and must be migrated or made to check the marker.

Hermetic route commits bypass all hooks, including legitimate user or organization hooks. Every repository-owned validation relied on for correctness or security must therefore be an explicit, audited route stage. Unknown third-party hooks cannot be silently treated as required harness policy.

Existing installations may retain the old post-commit wrapper until they synchronize hooks. The compatibility no-op and installer migration are necessary; merely changing the installer does not protect already-installed clones.

Git-history reconciliation needs defined behavior for rebases, orphaned marker SHAs, shallow clones, renames, deletions, and merges. A non-ancestral marker must trigger a full rebuild. This is simpler than queue recovery but not free.

Concurrent graph consumers still require safe serialization and atomic publication. This design removes commit/queue races, not graph-writer races.

Finally, this rejects the owner’s stated preference for proactive asynchronous recalculation. It replaces “eventually refreshed in the background” with “provably refreshed before trusted use.” That is less immediate, but substantially easier to make truthful.

# 5. VERDICT — YOURS

Use hookless managed commits plus Git-history, consumption-time graph reconciliation.

The thesis preserves the wrong owner of the work: Git hooks remain responsible for launching a distributed-state mechanism, and most of the 29 findings are consequences of that choice. Git history already supplies the durable coalescing ledger, while graph consumers are the only places where freshness is actually required. Removing graph work from hooks satisfies the invariant by construction and leaves a much smaller correctness surface.
