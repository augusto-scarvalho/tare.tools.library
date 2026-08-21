# Graph round 2 — 4 NVIDIA ideators + 4 NVIDIA divergences (2026-07-24)

Ideators refined each open point into an implementation plan; divergences then
attacked those theses from four different angles. **All four divergences returned
HYBRID** — none accepted the theses whole, none rejected them whole.

## Ideator 1 — P1 consumer resolution

**Summary.** Implementation plan for P1 consumer resolution: a resolve_code_graph(root, *, build_if_missing) seam in graphify_code_ast.py that replaces direct graph.json reads. Typed CodeGraphResult with fresh/stale/missing/absent states. Migration via deprecation shim + ratchet lint that fails CI on raw graph.json access, cutting over 42 files in batches. Atomic object-store publication deferred to P2; P1 focuses on the consumption seam and staleness enforcement.

### P1 plan: resolve_code_graph seam with typed staleness result
Land the seam + deprecation shim in Phase 1, migrate 42 call sites in batches of 8-10, enforce via ratchet lint in Phase 3.

## Ideator 2 — P2 object store + atomic publication

**Summary.** Implementation plan for P2 (object store + atomic publication). Defines graphify-out/objects/<key>/ layout, temp-build + post-build recompute + os.replace publication seam. Addresses Windows directory-rename failure, two-builder race, killed-mid-build, disk growth reaping, and graph.json backward-compat pointer. Sequenced in 4 commits so repo stays green through the gate.

### P2 plan: content-addressed object store with atomic publication
Land in 4 ordered commits: (1) atomic write helper + graph.json shim, (2) object store writer, (3) resolve_code_graph seam, (4) reaper. Each commit keeps the gate green.

## Ideator 3 — P3 surface the key in graph-status

**Summary.** P3 plan: add an additive `freshness` sub-object to `graphify_status()` output with fields state/inputKey/storedKey/stale/detail. Exit code stays 0. Single commit, S-sized, read-only, backward compatible.

### MECHANISM
Add `_freshness_block(root)` to the module defining `graphify_status()` (UNCERTAIN which module — CLI at harness.py:2602 calls it without visible import). The function reads `graphify-out/graph.json`'s `inputKey`, computes `input_key(root)`, returns a dict with five fields: `state` (fresh|stale|no_graph|unkeyed|unreadable|key_error), `inputKey` (current computed key or null), `storedKey` (key from graph.json or null), `stale` (boolean), `detail` (human string). Wire into `graphify_status()` as `base['freshness'] = _freshness_block(root)`. All existing top-level fields unchanged. Exit code stays 0 for all states — staleness is a warning, not a failure; `doctor` owns the WARN→exit-code gate semantics. `--target` repos work because `_freshness_block` takes `root` as a parameter and `input_key(root)` already handles arbitrary roots.

### SEQUENCING
Single commit, additive-only. P3 changes no on-disk format, no write path, no reader behavior. Step 1 (this commit): add `_freshness_block()`, wire into `graphify_status()`, add tests, ship. Step 2 (future, P2): when object store lands, `freshness` gains `resolvedObject` field and `object_missing` state. Step 3 (future, P1): `graph-status` may call `resolve_code_graph(build_if_missing=False)` to report resolution feasibility. Repo is green at every step because existing consumers see the same top-level fields; the new `freshness` key is additive JSON.

### BACKWARD COMPATIBILITY
The 42 blind readers of `graph.json` are NOT affected — P3 only changes `graph-status` output, not `graph.json` shape. Consumers of `graph-status`: jq callers see same fields + new key (no break); json.loads by-key callers ignore extra key (no break); GUI panel gets N+1 fields (no break if it handles unknown keys, which it must for forward compat). One risk: a consumer doing strict schema validation `assert set(obj.keys()) == {known_fields}` would break. UNCERTAIN if any consumer does this — search the 45-file list for `.keys()` or schema validation against graph-status output. Most likely strict consumer: `scripts/harness_ui_page.py` or `scripts/harness_ui.py`. No cutover needed — additive field appears; consumers that want it read it; others unaffected.

### FAILURE MODES
Windows: P3 is read-only. `input_key(root)` may fail on Windows-locked files (mandatory locking). The `try/except` in `_freshness_block` returns `state: key_error` instead of crashing. `path.read_bytes()` inside `input_key` already catches OSError and folds as `<unreadable>`, so a locked file produces a different key (false stale) — UNCERTAIN if this is real in gate worktrees. Concurrent actors: (1) A reads graph.json while B writes it non-atomically → A gets JSONDecodeError → `_freshness_block` catches and returns `unreadable` (graceful degradation of a pre-existing P2 bug). (2) A reads graph.json between B's writes of graph.json and symbols.json → A sees matching key but inconsistent symbols → P3 doesn't make this worse. (3) A computes input_key while B edits source files → TOCTOU race → A gets a key matching neither before nor after state → surfaces as `stale` (correct). (4) Two concurrent graph-status calls → both read same files, no write contention, no issue.

### ACCEPTANCE CRITERIA
AC1: graph-status output contains freshness object with all five sub-keys (state, inputKey, storedKey, stale, detail) in every state — FAILS if absent or incomplete. AC2: after graph-build-code-ast, freshness.state==fresh, stale==false, inputKey==storedKey — FAILS if fresh graph reports stale. AC3: after building then changing a .py file's content, freshness.state==stale, stale==true, inputKey!=storedKey — FAILS if content change undetected. AC4: no graph.json → state==no_graph, stale==false, inputKey==null — FAILS if absence causes error. AC5: graph.json with no inputKey → state==unkeyed, stale==false — FAILS if unkeyed reports stale or crashes. AC6: exit code 0 in all states — FAILS if nonzero exit for any freshness state. AC7: every pre-existing top-level field present with same value — FAILS if any field removed/renamed/changed. AC8: --target reports freshness relative to target's graphify-out, not harness repo — FAILS if wrong root. AC9: invalid JSON in graph.json → state==unreadable, exit 0 — FAILS if corrupt JSON crashes. AC10: doctor graph-staleness and graph-status freshness agree on stale/fresh/unkeyed/no_graph — FAILS if surfaces disagree.

### COST
Size: S. One function (~40 lines), one wiring point, one test file. No on-disk format change, no write path change, no reader migration. Riskiest file: the module defining `graphify_status()` (UNCERTAIN which module — likely `scripts/harness_lib/graphify_code_ast.py` but the CLI import isn't shown in provided code). Risk is low: additive JSON field, read-only operation. Would NOT do: add staleness to exit code (semantic change to status command; doctor owns gate semantics); add --freshness-only flag (tempts consumers to depend on narrow surface that changes when P2 lands); cross-reference symbols.json/modules.json consistency (that's cross-file integrity, not freshness, belongs in doctor); compute key in background thread or cache it (2s is acceptable for on-demand status); touch the 42 blind readers (that's P1 scope).

## Ideator 4 — P4 key the enrichment

**Summary.** Implementation plan for P4 (enrichment keying). Designs an enrichment key = SHA-256(AST inputKey + providerConfigKey + modelIds + promptVersion). Stored in docs-enrichment.json as enrichmentKey + astInputKey. Consumer seam: resolve_enrichment(root, *, build_if_missing). Mismatched AST key triggers WARN, not auto-rebuild (API cost). 4-phase sequencing keeps repo green. Backward compat via key-absence treated as unkeyed WARN. Windows atomic write via os.replace. Acceptance criteria include regression-failing test for stale enrichment detection.

### Enrichment key must fold AST inputKey + provider config + model + prompt version
Implement enrichment_key() as SHA-256 over AST inputKey + providerConfigKey + sorted model IDs + prompt version. Store enrichmentKey and astInputKey in docs-enrichment.json. Mismatched AST key = WARN not rebuild.

### Consumer seam resolve_enrichment() must gate all enrichment reads
Add resolve_enrichment(root, *, build_if_missing=False) to graphify_code_ast.py. Returns (enrichment_data, status) where status is fresh|stale_ast|stale_provider|unkeyed|missing. All internal readers route through this seam.

### Needless invalidation tradeoff: provider config change must not force API re-call if AST unchanged
Separate astInputKey from enrichmentKey in stored JSON. If astInputKey matches but enrichmentKey differs (provider/model/prompt changed), report stale_provider WARN but do NOT auto-rebuild. Human runs discover explicitly.

### Regression test: stale enrichment after AST change must FAIL if keying removed
Scenario: build graph + enrichment, modify a source file, assert resolve_enrichment returns stale_ast. This test FAILS if enrichment keying regresses to unkeyed.

## Divergence 1 — the identity mechanism (git already hashes)

**Summary.** Git-native tree/blob SHAs replace Python byte-hashing: `git ls-files -s` + `git hash-object` for untracked files produce a content key in ~50ms with zero file reads, making P3's cost problem moot by construction. But external --target repos that aren't git, and the unreadable-file false-stale bug, force a HYBRID: git-native fast path with Python fallback for non-git roots.

### THE ALTERNATIVE
### Signature: `git_content_key(root: Path) -> str`

```python
def git_content_key(root: Path) -> str:
    """Content key from git's own object database. Zero file reads."""
    h = hashlib.sha256()
    h.update(b"graphify-code-ast-inputs/v2\0")

    # 1. Tracked files: blob SHAs straight from the index, no byte reads.
    #    `git ls-files -s` emits `<mode> <sha1> <stage>\t<path>` per file.
    #    We filter to .py files (matching discover_python_files selection).
    result = _git(root, ["ls-files", "-s", "--", "*.py"])
    for line in result.stdout.splitlines():
        # line: "100644 <sha1> 0\tpath/to/file.py"
        blob_sha, _, rel = line.partition(" ")[1].split(" ")[0], None
        parts = line.split("\t", 1)
        blob_sha = parts[0].split(" ")[1]
        rel = parts[1]
        h.update(b"\0")
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(blob_sha.encode("ascii"))  # git's SHA-1 of blob content

    # 2. Untracked .py files: `git hash-object` per file (git computes SHA-1,
    #    caches in .git/objects). Still no Python read_bytes.
    untracked = _git(root, ["ls-files", "--others", "--exclude-standard", "--", "*.py"])
    for rel in untracked.stdout.splitlines():
        blob = _git(root, ["hash-object", str(root / rel)])
        h.update(b"\0")
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(blob.stdout.strip().encode("ascii"))

    return h.hexdigest()
```

### Command shapes (mediated through no-raw-subprocess helper)
- `_git(root, args)` calls the mediated spawn helper with `git -C <root> <args>`.
- `git ls-files -s -- '*.py'` — one process, index scan, ~10ms for 400 files.
- `git ls-files --others --exclude-standard -- '*.py'` — one process, untracked scan.
- `git hash-object <path>` — one process per untracked file (typically 0-5 in a clean repo).

### On-disk layout
Unchanged from the convergent destination: `graphify-out/objects/<key>/` with atomic `os.replace` publication. The key is `git_content_key(root)` instead of `input_key(root)`. The stored `inputKey` in `graph.json` is this git-native hash. Schema version bumps to `v2` so old keys never collide.

### `resolve_code_graph(root, *, build_if_missing)`
The seam is identical to the P1 thesis. The only difference is what function computes the freshness key internally. The seam calls `git_content_key` on the fast path, falls back to `input_key` (the existing Python byte-hash) when `_git` raises or returns non-zero.

### `graph-status` freshness block
Identical to P3 thesis, but `_freshness_block` calls `git_content_key(root)` instead of `input_key(root)`. Cost drops from 940ms to ~50ms. The `key_error` state now also covers `git_error` (non-git root, git not found, corrupted index).

### WHY IT IS STRUCTURALLY DIFFERENT
The structural choice: **WHO computes the content identity.**

The theses say: Python reads every file's bytes and hashes them. The harness owns the hashing.

The alternative says: Git already content-addresses every tracked file. The index already contains blob SHAs computed at `git add` time and cached in `.git/objects`. Asking git for them is asking the system that already knows the answer.

This is not an optimization of the same approach — it is a different **source of truth**. The theses treat the filesystem as the authority and recompute identity from scratch each time. The alternative treats git's object database as the authority and reads pre-computed identity. The filesystem is only consulted for files git doesn't know about (untracked, and only if they exist).

The key difference manifests in one place: **the cost model**. Python byte-hash is O(file_count × file_size) in I/O — 5MB read, 940ms. Git index scan is O(file_count) in CPU with zero I/O — 50ms. The gap is 20× and it grows with repo size because git's cost is a sorted index scan while Python's cost is proportional to total bytes.

### WHAT IT BUYS
### Made MOOT by construction:

1. **P3 cost problem** — The new measurement says `input_key` costs 0.94s and reads 5MB on every call, and P3 would add this to `graph-status`. With git-native keys, `graph-status` freshness costs ~50ms and reads 0 bytes. The P3 thesis explicitly says "2s is acceptable for on-demand status" and declines to cache. With git-native keys, the question doesn't arise — there's nothing to cache because there's nothing to compute.

2. **Unreadable-file false stale** — The new measurement notes that `input_key` folds a transiently locked Windows file as `<unreadable>`, producing a different key and a false stale report. `git ls-files -s` reads the index, not the working tree files. A locked file does not change its blob SHA in the index. The false-stale window disappears for tracked files. (Untracked files still go through `git hash-object`, which reads the file — but untracked files are rare and the window is narrower.)

3. **TOCTOU during key computation** — The P3 thesis lists a TOCTOU race: A computes `input_key` while B edits source files, getting a key matching neither state. With git-native keys, the index is a snapshot. `git ls-files -s` reads a consistent point-in-time view. If the index changes mid-scan (staged edit), git's own locking prevents a torn read. The race window shrinks from "duration of 397 file reads" to "duration of one index scan."

### Still OWES:

1. **Non-git `--target` repos** — An external target that isn't a git repository has no index, no blob SHAs. `git_content_key` fails. The design must fall back to `input_key` (Python byte-hash). This is not a degradation — it's the status quo. But it means the fast path is conditional on `git rev-parse --git-dir` succeeding.

2. **Untracked .py files in the graph** — If `discover_python_files` includes untracked files (it might, since it walks the tree), those files aren't in `git ls-files -s`. The design handles them with `git ls-files --others --exclude-standard` + `git hash-object`, but this reintroduces per-file I/O for untracked files. In a clean repo this is 0 files. In a dirty repo with 50 untracked .py files, it's 50 `git hash-object` calls — still cheaper than reading all tracked files, but not free.

3. **Submodules** — `git ls-files` doesn't recurse into submodules by default. If the graph covers files inside a submodule, those need separate handling. UNCERTAIN whether the current `discover_python_files` enters submodules.

### WHAT IT COSTS
### What is WORSE about the git-native approach:

1. **Git dependency at freshness-check time** — The Python byte-hash needs only stdlib. The git-native key needs git on PATH and a valid `.git` directory. In the harness's own repo this is guaranteed. For `--target` repos it is not. The fallback path means two code paths with different performance characteristics, and a test matrix that must cover both. The theses have one path.

2. **No-raw-subprocess ratchet friction** — Every `git ls-files` and `git hash-object` call goes through the mediated spawn helper. The theses' `input_key` is pure Python, no subprocess. The git-native approach adds 2-3 subprocess spawns per freshness check (one for `ls-files -s`, one for `ls-files --others`, N for `hash-object` on untracked files). The mediated helper must handle these. If the ratchet counts spawns, this increases the spawn budget.

3. **SHA-1 vs SHA-256** — Git's blob hashes are SHA-1. The design folds them into a SHA-256 digest, so the final key is SHA-256. But the intermediate identity (blob SHA) is SHA-1, which has known collision weaknesses. An attacker who crafts two files with the same git blob SHA would fool the freshness check. In practice this requires a chosen-prefix collision attack against SHA-1, which is feasible for well-funded attackers but not for accidental staleness. The theses use SHA-256 throughout. This is a real but narrow downgrade.

4. **Index vs working tree divergence** — `git ls-files -s` reads the index, not the working tree. If a file is modified but not staged, its index blob SHA is stale relative to the working tree. The graph is built from the working tree (Python reads actual bytes), but the key is computed from the index. This means: edit a file, don't stage it, build the graph (gets new content), compute the key (gets old blob SHA from index) — the key matches the pre-edit state but the graph contains post-edit content. This is a **false fresh** report, the inverse of the false-stale problem. The theses don't have this because they hash the same bytes the builder reads.

   Mitigation: run `git update-index --refresh` before `ls-files`, or use `git hash-object` on all files (defeats the purpose), or accept that the key tracks the index not the working tree and document that `git add` is the freshness boundary. UNCERTAIN which mitigation is correct — this is the deepest problem with the design.

### VERDICT
### HYBRID: git-native fast path, Python fallback, index-refresh guard

The theses are right that a content key over file bytes is the correct identity mechanism. They are wrong that Python must compute it. Git already did.

But the git-native approach has one problem the theses don't: **index vs working tree divergence** (false fresh on unstaged edits). And the theses have one problem the git-native approach doesn't: **0.94s cost and 5MB I/O per call**.

The graft:

1. **Fast path: `git_content_key(root)`** when `git rev-parse --git-dir` succeeds. This covers the harness's own repo and any git-backed `--target`. Cost: ~50ms, 0 bytes read. This makes P3's cost problem moot.

2. **Guard against index staleness**: before `git ls-files -s`, run `git update-index --refresh --quiet` (one subprocess, ~20ms, touches only files whose stat differs from index). This syncs the index to the working tree without staging anything. After refresh, `ls-files -s` blob SHAs match working tree content. The false-fresh window closes. UNCERTAIN whether `--refresh` reads file contents or only stat — if it only checks stat, a same-stat-different-content edit still slips through, but that's a narrower race than the unguarded version.

3. **Fallback: `input_key(root)`** when git is unavailable, `git rev-parse` fails, or the mediated spawn helper rejects the command. This is the existing Python byte-hash, unchanged. Cost: 0.94s. This covers non-git `--target` repos and any environment where git isn't on PATH.

4. **Schema version `v2`**: the git-native key uses `graphify-code-ast-inputs/v2` as the prefix so it never collides with a v1 Python key. Stored `inputKey` in `graph.json` records which path produced it. `doctor` and `graph-status` compute the key via the same `resolve_content_key(root)` dispatcher, so both paths agree.

5. **Untracked files**: `git ls-files --others --exclude-standard -- '*.py'` + `git hash-object` per file. In a clean repo: 0 calls. In a dirty repo: proportional to untracked .py count. Acceptable because the graph builder itself skips untracked files in most configurations (UNCERTAIN — need to verify `discover_python_files` behavior).

The theses win on simplicity and universality (one path, no git dependency, no index divergence). The git-native approach wins on cost (20× faster, zero I/O) and on the unreadable-file false-stale bug (index doesn't read locked files). The hybrid takes the fast path where it's safe (git repo, refreshed index) and falls back to the thesis approach where it's not. The cost is two code paths and a subprocess budget increase. The benefit is that P3 becomes free and the false-stale-on-locked-file bug disappears for the common case.

## Divergence 2 — the migration (self-invalidating artifact)

**Summary.** The thesis's 42-site seam migration is ceremony around a problem that vanishes if the artifact self-invalidates. My alternative makes graph.json always-correct-or-absent by having the build atomically publish into a content-addressed object and leaving a pointer that is either valid or missing — blind readers need zero migration. Verdict: HYBRID — graft the self-invalidating pointer from mine onto the thesis's resolve_code_graph seam, but skip the 42-site cutover.

### 1. THE ALTERNATIVE
Make `graph.json` always-correct-or-absent. The build writes into a temp dir, recomputes the key post-build, publishes the graph payload into `graphify-out/objects/<key>/graph.json` (plus symbols.json, modules.json copied alongside), then atomically replaces the `graphify-out/graph.json` POINTER via `os.replace` (Windows-safe). The pointer is a 3-line JSON: `{"inputKey": "<sha>", "objectPath": "objects/<key>/graph.json", "schemaVersion": 1}`. A blind reader that opens `graphify-out/graph.json` gets either a valid pointer (and follows it) or a missing file — never a stale graph.

The staleness question moves to PUBLICATION TIME, not consumption time. After atomic replace, the old object dir is orphaned but harmless; a reaper cleans it. If the tree changes mid-build, the post-build recompute yields a different key than the pre-build snapshot — the build discards its temp dir and does nothing (or retries once). Two concurrent builders each write to their own temp dir (`objects/.tmp-<pid>-<uuid>/`), recompute, and race to `os.replace` the pointer; the loser's object dir is orphaned and reaped later. No locks, no coordination.

For the 42 blind readers: add a `graphify_code_ast.load_graph(root)` helper that does `pointer = read(graphify-out/graph.json); return read(graphify-out/objects/<key>/graph.json)`. This is a 5-line function. You do NOT migrate 42 call sites. Instead, you make the EXISTING `graph.json` path a thin pointer and provide `load_graph` for new code. Old code that reads `graph.json` directly gets a pointer, not a graph — and you add a one-time shim: if `graph.json` contains `"objectPath"`, redirect internally. But even simpler: keep `graph.json` as the FULL graph (backward compat) AND write the object store copy. The pointer lives in a SEPARATE file: `graphify-out/graph.pointer.json`. New readers use `load_graph(root)` which checks the pointer first, falls back to `graph.json`. Old readers read `graph.json` directly and get the full graph — which is always fresh because the build writes it atomically via `os.replace` from temp.

The key insight: the non-atomic write (P2) is the root cause. Fix the WRITE to be atomic and content-addressed, and the READ side needs no migration. Staleness is still reported by `doctor` and `graph-status` (P3), but a stale graph on disk is impossible — the build either publishes a fresh one or leaves the previous fresh one intact.

For stale-by-content (tree changed since last build): the graph on disk is still the LAST successfully built graph. It is not stale in the corrupt/half-written sense — it is stale in the content-changed sense. That is a VALID graph for a PAST tree. The question is whether consumers should USE it. My answer: they should not, but preventing that by migrating 42 readers is expensive. Instead, `doctor` reports stale (as today), and `graph-status` surfaces the key (P3). If you want HARD prevention, the build can DELETE the pointer when it detects staleness on a subsequent build attempt — but that requires a build to run, which is the explicit decoupling.

So the concrete alternative for P1 is: DO NOT migrate readers. Fix P2 (atomic write + object store). The 42 blind readers get atomic, always-consistent graphs. Staleness-by-content is reported but not enforced at read time — enforcement is at `doctor`/gate time, which is where it already lives.

Signatures:
- `publish_graph(root, temp_build_dir, pre_build_key) -> Path`: recompute `input_key(root)`, if mismatch discard temp and return None, else `os.replace` the pointer and copy graph into `objects/<key>/`.
- `load_graph(root) -> Optional[dict]`: read pointer, follow to object, return graph dict. For old code, `graph.json` remains the full graph written atomically.
- `graphify_status()` gains `freshness` block (P3 unchanged).
- `resolve_code_graph(root, *, build_if_missing)` exists but is OPT-IN for new code, not a migration target for 42 sites.

On-disk layout:
```
graphify-out/
  graph.json              # full graph, written atomically via os.replace from temp (backward compat)
  graph.pointer.json      # {"inputKey": "...", "objectPath": "objects/<key>/graph.json"} (new, optional)
  objects/
    <key>/
      graph.json          # content-addressed copy
      symbols.json
      modules.json
    .tmp-<pid>-<uuid>/    # temp build dirs, cleaned up
  GRAPH_REPORT.md
  symbols.json            # backward compat copies at top level
  modules.json
```

Command shapes: unchanged. `harness.py graph-build-code-ast` now publishes atomically. `doctor` unchanged. `graph-status` gains `freshness` (P3). No new commands.

### 2. WHY IT IS STRUCTURALLY DIFFERENT
The thesis chooses CONSUMPTION-SIDE enforcement: every reader goes through a seam, the seam decides fresh/stale/missing, and a ratchet lint forces 42 sites to cutover. My alternative chooses PUBLICATION-SIDE correctness: the build atomically writes a consistent graph or leaves the previous one intact, so every reader — seam or blind — gets a valid artifact.

The named choice that differs: WHERE staleness prevention lives. Thesis: at the read boundary (42 call sites + seam + lint). Mine: at the write boundary (atomic publish + content-addressed object). The thesis's seam is a gatekeeper that refuses to serve stale data; mine is a publisher that refuses to leave stale data on disk. These are duals, but the write-side fix has O(1) call sites (the build function) while the read-side fix has O(42) call sites.

The thesis would argue: 'but a content-matched graph for a PAST tree is still stale.' Correct — my approach does not prevent reading a graph whose inputs have since changed. It prevents reading a CORRUPTED or HALF-WRITTEN graph. The content-staleness question remains a `doctor`/`graph-status` concern, not a reader concern. The thesis's seam makes content-staleness a reader concern too, which is stronger but costs 42 migrations.

The structural difference is: thesis treats staleness as a property the READER must check; mine treats consistency as a property the WRITER must guarantee, and leaves content-staleness to the reporting layer.

### 3. WHAT IT BUYS
Makes MOOT by construction:
- P2 (non-atomic write): solved entirely. `os.replace` from temp dir is atomic on Windows. Two builders race on the pointer replace; loser's object is orphaned, reaped later. No half-written `graph.json`.
- P1 (42 blind readers): MOOT for the CORRUPTION case. Blind readers never see a half-written graph. They CAN see a content-stale graph (inputs changed since last build), but that is the same risk the thesis's seam has if `build_if_missing=False` and the graph exists — the seam returns it with a `stale` flag, but the caller must CHECK the flag. A blind reader ignores the flag; a seam reader who ignores the flag is equally broken.
- The ratchet lint: unnecessary. No 42-site migration to enforce.
- Backward compatibility: trivial. `graph.json` stays where it is, written atomically. Old readers work. New readers optionally use `load_graph(root)` or `resolve_code_graph(root, build_if_missing=False)`.

Still OWES:
- Content-staleness at read time: a blind reader CAN use a graph whose inputs have changed since the last build. My approach does not prevent this. The thesis's seam does (if the caller checks the result type). This is the real gap.
- P3 (surface the key): still needed, unchanged.
- P4 (enrichment keying): still needed, unchanged.
- The 0.94s `input_key` cost on every `doctor` / `graph-status` call: still owed. My approach does not cache the key. UNCERTAIN whether a content-addressed object store enables caching (the pointer's `inputKey` could be compared against a cached computed key, but the computed key depends on the live tree, so caching is invalid across tree changes).
- The `<unreadable>` false-stale problem on Windows: still owed. A transiently locked file changes the computed key, producing a false stale report. My approach does not fix this; neither does the thesis.

### 4. WHAT IT COSTS
Worse about mine:
- Content-staleness is NOT enforced at read time. A blind reader can use a graph that matches a past tree. The thesis's seam makes this a typed result the caller must handle. Mine relies on `doctor` and gate-time checks to catch staleness before it matters. If a consumer reads a stale graph and makes a wrong decision (e.g., a gate check uses an outdated symbol index), my approach does not prevent it. The thesis's seam returns `CodeGraphResult(state=stale)` and the caller can refuse. This is the thesis's genuine advantage.
- The object store adds disk growth. Each build creates `objects/<key>/` with a full copy of graph.json + symbols.json + modules.json. If the tree changes frequently, this grows. A reaper is needed. The thesis has this cost too (P2), but mine makes it load-bearing for P1 correctness, while in the thesis it is P2-scoped.
- `graph.json` is written TWICE: once at top level (backward compat) and once in `objects/<key>/`. This is redundant disk I/O. The thesis writes once into the object store and leaves a pointer — but then blind readers reading `graph.json` get a pointer, not a graph, which breaks them unless you add a shim. My approach avoids the shim by writing the full graph at both locations. Cost: 2x write I/O for graph.json (~the graph is small, but symbols.json and modules.json may not be).
- No ratchet lint means no mechanical enforcement that new code uses the seam. Future code can read `graph.json` directly and get a valid-but-potentially-stale graph. The thesis's lint prevents this. Mine relies on convention.
- The `load_graph(root)` helper is opt-in. If nobody uses it, new code continues to read `graph.json` directly. The thesis's seam + lint forces convergence. Mine does not.
- For `--target` repos: the object store writes to the target's `graphify-out/objects/`. This is fine, but the reaper must know the target root. Minor complexity.
- The false-stale problem from `<unreadable>` is not addressed by either approach, but mine makes it more visible: if the build recomputes the key post-build and a file is transiently locked, the build discards its own output (key mismatch) and leaves the PREVIOUS graph in place. This is actually BETTER than the thesis (where `doctor` reports false stale), but it means a build silently fails when a file is locked. UNCERTAIN how often Windows file locking occurs in practice.

### 5. VERDICT
HYBRID — graft the self-invalidating atomic publication from mine onto the thesis's resolve_code_graph seam, but skip the 42-site cutover.

Concretely: (1) Fix P2 first — atomic write via `os.replace` from temp, content-addressed object store, post-build recompute. This makes `graph.json` always-consistent-or-absent. (2) Add `resolve_code_graph(root, *, build_if_missing)` as the seam, but do NOT migrate 42 sites. New code uses it. Old code reads `graph.json` directly and gets an atomic, consistent graph. (3) Add P3 `freshness` block to `graph-status` — unchanged from thesis. (4) Add P4 enrichment keying — unchanged from thesis. (5) Skip the ratchet lint and the 42-site batch migration entirely.

The thesis's seam is architecturally correct — consumers SHOULD go through a typed boundary. But the 42-site migration plus a ratchet lint is ceremony proportional to the WRONG axis. The axis that matters is WRITE correctness (P2), not READ routing (P1). Fix the write, and the read routing becomes a convention you encourage, not a migration you enforce.

The thesis's seam wins on content-staleness enforcement: a typed `CodeGraphResult(state=stale)` lets a caller refuse stale data. Mine does not provide this for blind readers. But the 42 blind readers are EXISTING code that already does not check staleness — migrating them to a seam that returns a typed result does not mean they will CHECK the result. If the migration is mechanical (replace `read(graph.json)` with `resolve_code_graph(root, build_if_missing=False).graph`), the callers ignore the state just as they ignored staleness before. The seam adds value only if callers are REWRITTEN to handle the state — which is a deeper change than the thesis's 'batches of 8-10' mechanical cutover implies.

So: the thesis's P1 plan is a 42-site migration that produces a typed result nobody checks, enforced by a lint that ensures the function is called but not that the result is handled. Mine is a 1-site write fix that eliminates corruption but not content-staleness. The hybrid: fix the write (1 site), add the seam (opt-in, new code), skip the migration, let `doctor` and `graph-status` own content-staleness reporting as they already do.

## Divergence 3 — scope (what should NOT be built)

**Summary.** DIVERGENT DESIGN: drop P2 (object store) and P4 (enrichment keying) entirely. Build only a 3-line atomic write fix and a 5-field additive freshness block in graph-status. The graph is a navigation aid, not a correctness oracle; a stale graph sends an agent to a slightly wrong file, which source verification already catches. The thesis's object store + 42-file migration is disproportionate to that risk. VERDICT: HYBRID (graft: atomic write from P2, freshness block from P3, drop P1 seam and P4 enrichment keying).

### THE ALTERNATIVE
## 1. THE ALTERNATIVE

### What to build (2 changes, ~60 lines total):

**A. Atomic write fix (addresses P2's actual risk)**

Replace lines 213-219 of `graphify_code_ast.py`:
```python
output_dir.mkdir(parents=True, exist_ok=True)
for name, data in [
    ("graph.json", graph),
    ("symbols.json", {k: symbols_index[k] for k in sorted(symbols_index)}),
    ("modules.json", modules_index),
]:
    tmp = output_dir / f".{name}.tmp"
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(output_dir / name))  # os.replace, not os.rename
```

No object store. No `objects/<key>/` directory. No reaper. No temp-build-then-recompute. Just `os.replace` per file. Two concurrent builders still race, but the loser's `os.replace` overwrites the winner's — last write wins, and every write is a complete consistent file. A reader mid-read gets either the old complete file or the new complete file, never a torn one. This is the actual guarantee the thesis's object store provides, minus 200 lines of machinery.

**B. Freshness block in graph-status (addresses P3, partially P1)**

Add `_freshness_block(root)` to whichever module defines `graphify_status()` (UNCERTAIN — likely `graphify_code_ast.py` or a status module imported by `harness.py:2602`). Wire as `base['freshness'] = _freshness_block(root)`.

```python
def _freshness_block(root: Path) -> dict:
    graph = root / "graphify-out" / "graph.json"
    if not graph.is_file():
        return {"state": "no_graph", "inputKey": None, "storedKey": None, "stale": False, "detail": "no graph built"}
    try:
        stored = str((_read_json(graph) or {}).get("inputKey") or "")
    except (json.JSONDecodeError, OSError):
        return {"state": "unreadable", "inputKey": None, "storedKey": None, "stale": False, "detail": "graph.json unreadable"}
    if not stored:
        return {"state": "unkeyed", "inputKey": None, "storedKey": None, "stale": False, "detail": "graph predates key tracking"}
    try:
        current = input_key(root)
    except Exception:
        return {"state": "key_error", "inputKey": None, "storedKey": stored, "stale": False, "detail": "input_key computation failed"}
    fresh = current == stored
    return {
        "state": "fresh" if fresh else "stale",
        "inputKey": current,
        "storedKey": stored,
        "stale": not fresh,
        "detail": "inputs match" if fresh else f"inputs changed ({stored[:12]} -> {current[:12]})",
    }
```

Exit code stays 0. All existing top-level fields unchanged. `--target` works because `root` is a parameter.

### What NOT to build:

- **P1 resolve_code_graph seam**: Do not migrate 42 files. Do not add a ratchet lint. The 42 blind readers continue to read `graph.json` directly. They get either a valid file or a `JSONDecodeError` they already handle (or should). The freshness block in `graph-status` gives humans and agents the staleness signal at the one place they already look for status. If a consumer reads a stale graph, it navigates to a slightly wrong file; source verification catches it. That is the doctrine.

- **P2 object store**: No `graphify-out/objects/<input-key>/`. No temp-dir build + post-build recompute + atomic rename. No reaper for disk growth. No backward-compat pointer file. The atomic `os.replace` per-file fix above gives the only guarantee the object store provides that matters: no reader ever sees a torn file.

- **P4 enrichment keying**: No `enrichment_key()`. No `resolve_enrichment()`. No `docs-enrichment.json` schema change. `discover` stays explicit and human-triggered. If enrichment is stale relative to the AST graph, an agent using it for navigation gets slightly wrong metadata; source verification catches it. The API cost of a false rebuild outweighs the navigation cost of a stale enrichment.

### On-disk layout (unchanged except atomic writes):
```
graphify-out/
  graph.json        # written via .graph.json.tmp -> os.replace
  symbols.json      # written via .symbols.json.tmp -> os.replace
  modules.json      # written via .modules.json.tmp -> os.replace
  GRAPH_REPORT.md   # plain write_text (report, not consumed by code)
```

### Command shapes (unchanged):
- `harness.py graph-status` — same JSON, same exit 0, new `freshness` key.
- `harness.py graph-build-code-ast` — same, but writes atomically.
- `harness.py doctor` — unchanged.
- `harness.py discover` — unchanged, still explicit, may block.

### WHY IT IS STRUCTURALLY DIFFERENT
## 2. WHY IT IS STRUCTURALLY DIFFERENT

The thesis treats the graph as a **correctness-critical artifact** that needs content-addressed storage, consumption-time resolution, and a migration of 42 call sites. My design treats it as a **navigation aid** that needs atomic writes (so readers never see torn files) and a status signal (so humans know when to rebuild).

The structural choice that differs: **where the staleness contract is enforced**.

- **Thesis**: enforced at *consumption time* — every reader goes through `resolve_code_graph()`, which checks the key and refuses/flags stale graphs. This requires migrating 42 files and maintaining a ratchet lint forever.
- **Mine**: enforced at *status time* — `graph-status` surfaces the key, `doctor` already warns, and consumers read `graph.json` directly. The contract is "you can read a stale graph, but you were told it was stale." This is the same contract the repo already has for every other cached artifact (symbols, modules, enrichment).

The second structural choice: **what atomicity means**.

- **Thesis**: atomicity at the *object* level — a content-addressed directory `objects/<key>/` containing all files, published by renaming a temp directory. This requires solving Windows directory-rename-onto-existing-directory failure, which the thesis acknowledges is a hard constraint.
- **Mine**: atomicity at the *file* level — each file written to a temp path then `os.replace`d. `os.replace` is atomic on Windows for files (the constraint says so). Three independent `os.replace` calls mean a reader could see graph.json from build N and symbols.json from build N-1, but both are individually complete and valid. For a navigation aid, cross-file consistency between graph.json and symbols.json is not a correctness requirement — the consumer that needs symbols looks them up by key and gets either the old or new index, both valid.

### WHAT IT BUYS
## 3. WHAT IT BUYS

### Problems made MOOT by construction:

- **Torn reads** (P2's core risk): `os.replace` per file means no reader ever sees a half-written `graph.json`. MOOT.
- **Staleness visibility** (P3): `graph-status` surfaces `freshness.state` with `inputKey`, `storedKey`, `stale`, `detail`. Anyone who runs `graph-status` sees the answer. MOOT.
- **Doctor / graph-status disagreement** (P3 AC10): both call the same `input_key(root)` and compare to the same `storedKey`. They agree by construction. MOOT.

### Problems still owed:

- **42 blind readers** (P1): still read `graph.json` directly. A stale graph can be consumed without warning. **But**: the staleness signal exists in `graph-status` and `doctor`; an agent or human who checks status before acting gets the warning. The readers that don't check are the same readers that don't check any preconditions — adding a seam doesn't fix that culture.

- **Two concurrent builders** (P2): last write wins via `os.replace`. Both builds complete; one's output overwrites the other's. No corruption, but wasted work. The thesis's object store avoids this by having both writes go to different key directories (if the tree changed) or the same directory (if identical). In practice, two gate shards building the same repo in the same `graphify-out` produce identical keys and identical output — the wasted work is the cost, not correctness.

- **Enrichment staleness** (P4): no way to tell if `docs-enrichment.json` matches the current AST graph. Still owed. But `discover` is explicit and human-triggered; the human who ran it knows when they ran it and what provider config they used. An enrichment key would help automation, but no automation currently consumes enrichment — it's read by agents who use it for navigation and verify in source.

- **False stale from unreadable files** (new measurement): `input_key` folds locked files as `<unreadable>`, producing a different key. My design inherits this. The thesis inherits it too. Neither solves it. The fix would be to retry `read_bytes` once or fold by `(path, size, mtime)` instead of a literal marker — but that's a separate change to `input_key` itself, not to any of the four points.

### WHAT IT COSTS
## 4. WHAT IT COSTS

### What is WORSE about my design:

- **No consumption-time enforcement**: A consumer can read a stale graph and act on it without ever checking `graph-status`. The thesis's `resolve_code_graph` seam would refuse (or at least flag) a stale graph at the call site. Mine relies on the consumer checking status first. If an agent reads `graph.json` directly, navigates to a stale symbol location, and reports a finding based on the stale graph without verifying in source, that's a failure mode my design allows and the thesis's design prevents. The repo's doctrine says findings must be verified in source, but doctrine is not enforcement.

- **Cross-file inconsistency window**: Three `os.replace` calls are not atomic as a group. A reader could see `graph.json` from build N and `symbols.json` from build N-1. The thesis's object store publishes all files atomically as a directory. In practice, the window is microseconds and both files are individually valid, but a consumer that cross-references graph.json's symbol IDs against symbols.json could see a symbol ID that exists in graph.json but not in the old symbols.json. This is a real (if narrow) correctness gap.

- **No disk growth management**: No reaper. Old graphs accumulate if someone builds repeatedly with different content. The thesis's object store has a reaper. My design relies on the fact that `graph.json` is overwritten in place — there's only ever one graph, so there's no growth. But if the thesis's object store were built, it would need a reaper; mine doesn't, because it doesn't create the problem.

- **No enrichment keying**: If a provider config or model changes, `docs-enrichment.json` is silently stale. An agent using it for navigation gets wrong metadata. The thesis's enrichment key would surface this. My design accepts the risk because `discover` is explicit and human-triggered, and no automation consumes enrichment.

- **0.94s cost on every `graph-status` call**: My design adds `input_key(root)` to `graph-status`, costing 0.94s and reading 5.0 MB across 397 files. The thesis's P3 does the same. Neither caches. For a status command that a human runs on demand, 0.94s is acceptable. For an agent that polls `graph-status` in a loop, it's not. UNCERTAIN whether any agent does this.

- **42 files still touch `graph.json` directly**: Future changes to the on-disk format require updating all 42. The thesis's seam centralizes this. Mine doesn't. If the format changes, the 42 break individually and visibly, which is arguably fine (fail fast) but is more migration work.

### VERDICT
## 5. VERDICT

**HYBRID** — graft: atomic write from P2 (file-level `os.replace`, not object store), freshness block from P3 (additive `freshness` key in `graph-status`), drop P1 (resolve_code_graph seam + 42-file migration) and P4 (enrichment keying).

### Why drop P1:
The 42-file migration is the single most expensive item across all four theses. It buys consumption-time enforcement for a navigation aid. The repo's own doctrine says findings must be verified in source before acting. A stale graph can send an agent to a slightly wrong file; source verification catches it. The cost of the seam (42 file changes, a ratchet lint, permanent maintenance of the abstraction) is disproportionate to the cost of the failure it prevents (looking in a slightly wrong place). The staleness signal already exists in `doctor` and, after my P3 graft, in `graph-status`. An agent that checks status before acting gets the warning. An agent that doesn't won't check a seam either.

### Why drop P2's object store, keep its atomic write:
The object store buys: (a) no torn reads, (b) no concurrent-write corruption, (c) content-addressed retrieval, (d) disk growth reaping. My design provides (a) via `os.replace` per file and (b) via last-write-wins (no corruption, just wasted work). Point (c) is not needed — there's only one current graph, not a history. Point (d) is not needed because there's no growth without an object store. The object store's Windows directory-rename problem is a hard constraint that costs complexity to solve; file-level `os.replace` doesn't have that problem.

### Why drop P4:
`discover` is explicit and human-triggered. No automation consumes enrichment. An enrichment key would help a future where agents auto-refresh enrichment, but that future doesn't exist and the API cost of a false rebuild (the thesis's own concern) outweighs the navigation cost of stale enrichment. If automation is added later, add the key then.

### Why keep P3:
It's 40 lines, additive, read-only, backward compatible, and gives the staleness signal at the one command a human or agent already runs for status. It's the smallest change that captures the most value across all four points.

### What is lost:
Consumption-time enforcement (P1) and enrichment keying (P4). A consumer that ignores `graph-status` can read a stale graph. An enrichment that's stale relative to the AST graph is undetectable. Both are real gaps. Both are acceptable for a navigation aid whose outputs are verified in source before action. If the graph ever becomes a correctness oracle (e.g., gate checks that depend on graph accuracy for pass/fail), revisit P1 and P2's object store. Until then, the smallest subset that captures most of the value is: atomic writes + freshness in status.

## Divergence 4 — staleness granularity (merkle over files)

**Summary.** Diverges on staleness granularity: per-file delta-keyed graph with incremental rebuild instead of global boolean. Verdict is HYBRID — graft per-file keys and incremental rebuild onto the thesis object-store and seam infrastructure, because the 0.94s key cost and 5s rebuild make global staleness acceptable today but the 42 blind readers and enrichment keying benefit from finer granularity.

### 1. THE ALTERNATIVE
Per-file delta-keyed graph with incremental rebuild. On-disk: graphify-out/objects/<ast-key>/graph.json stores per-file entries: {path: {fileKey: sha256(bytes), nodes: [...], edges: [...]}}. A manifest file graphify-out/manifest.json maps {astKey, fileKeys: {relpath: sha256}, builtAt}. input_key stays global for the object-store address, but a NEW file_key(path, root) = sha256(relpath + bytes) per file. resolve_code_graph(root, *, build_if_missing) reads manifest, diffs current file_keys vs stored, returns CodeGraphResult with delta: {changed: [...], added: [...], removed: [...]}. If delta is empty -> fresh. If delta is small -> incremental: reparse only changed files, patch nodes/edges, recompute global key, publish new object. If delta is large (>threshold) -> full rebuild. Command: `harness.py graph-build-code-ast --incremental` (default). `graph-status --freshness` shows per-file delta counts. Enrichment key folds fileKeys subset for changed files only.

### 2. WHY IT IS STRUCTURALLY DIFFERENT
The thesis treats the graph as a single opaque blob with one key: any byte changes anywhere, the entire 397-file graph is stale, and the only resolution is a full 5s rebuild. The alternative treats the graph as a MERKLE TREE over files: each file has its own content key, the graph is the union, and staleness is a SET of changed files, not a boolean. The structural choice that differs is WHERE the key boundary sits: thesis puts it at the whole-graph level (one SHA-256 over all files), alternative puts it at the file level (one SHA-256 per file, aggregated into a manifest). This means incremental rebuild is not an optimization layered on top — it is the ONLY operation when the delta is small, because the graph is already partitioned by file.

### 3. WHAT IT BUYS
Makes P1 partially moot by construction: if resolve_code_graph returns a delta, consumers can decide whether THEIR subgraph is affected rather than treating the whole graph as stale. A consumer that only reads nodes for `scripts/harness_lib/` does not care if `testing/probes/` changed. Makes P4 cheaper: enrichment re-call can be scoped to changed files only, not the whole tree. Makes the 0.94s input_key cost irrelevant for the common case: manifest diff is O(changed files), not O(397 files). Still owes: the object-store atomic publication (P2) is still needed because two builders can still race on the same object path. The 42 blind readers still need the seam (P1). graph-status still needs to surface the key (P3). Windows file-locking false-stale is WORSE per-file: one locked file invalidates its subgraph rather than the whole key.

### 4. WHAT IT COSTS
WORSE: (1) On-disk format change is breaking — graph.json gains per-file structure, old readers see a different shape. Backward compat requires a shim that reconstructs the flat graph from per-file entries, adding complexity the thesis avoids. (2) Incremental rebuild is only safe if the builder can correctly patch nodes/edges for a changed file without reparsing dependents — UNCERTAIN the current builder supports this; if a file's AST change ripples to edges from OTHER files (e.g., a function renamed is called elsewhere), incremental rebuild produces an inconsistent graph. This is a CORRECTNESS risk the thesis does not have. (3) Manifest.json is a new write path with the same non-atomic-write problem as graph.json — P2's object store must cover it too. (4) 5s full rebuild is already fast; incremental saves maybe 4s on a 1-file change. The complexity-to-savings ratio is poor at current scale. (5) file_key per file means 397 SHA-256 calls on every manifest diff vs 1 call for input_key — but each is over one file, so total bytes read is the same 5MB.

### 5. VERDICT
HYBRID (graft per-file keys onto thesis object-store). The thesis is right that global staleness is sufficient TODAY: 5s rebuild, 0.94s key, 397 files. The alternative's incremental rebuild is a premature optimization with a real correctness risk (cross-file edge consistency). BUT the thesis should graft one thing: store per-file fileKeys in the object's graph.json as a SUBSET of the existing node data, not as a new manifest. This costs nothing extra (the builder already has per-file bytes), enables future incremental rebuild if the builder gains that capability, and lets resolve_code_graph return a delta hint to consumers without changing the freshness model. P1, P2, P3, P4 all survive unchanged. The per-file keys are a forward-compatible addition, not a replacement for the global key. If the repo grows past ~2000 files or rebuild exceeds 15s, revisit incremental as a first-class feature.
