# SPEC-159 — Affected-scenario selection + per-scenario gate cache (Phase 1: SHADOW)

Status: SPEC-159, proposed 2026-07-20 (acceptance: `testing/scenarios/gac_gate_affected.py`).
Origin: backlog `wf-gate-result-cache` + `wf-affected-scenario-selection` (WF
roadmap, research round 2026-07-20, `docs/research/loop-workflow-efficiency-round.md`).
Door: covered surface — reuses the SPEC-137 staged fingerprint/manifest and the
SPEC-158 `gate-perf` sidecar; this spec adds the affected-set computation, a
per-scenario cache store, and SHADOW instrumentation over them. depends-on:
`wf-gate-observability` (SPEC-158, shipped).

## Goal

Kill the re-gate churn where any change re-runs all 150 scenarios by learning
which scenarios a change actually affects (test-impact analysis over the Graphify
import graph) and caching the per-scenario verdict for the rest. **Phase 1 is
SHADOW / MEASURE-ONLY**: the gate still runs EVERY scenario; the machinery only
computes what a future scenario-level cache WOULD skip and PROVES it is safe
(`falseSkip == 0`) before Phase 2 ever turns skipping on. A wrong affected-map
that actually skipped a scenario would be a false green (a regression shipped),
so Phase 1 carries zero correctness risk by construction.

## Applicability

- `harness_lib/gate_affected.py`: affected-set computation, the per-scenario
  closure key, the pure false-skip decision (`shadow_row`), and the `ShadowLedger`
  used by the gate.
- `harness_lib/validation_stamp.py`: an additive per-scenario verdict store
  (`read_scenario_verdicts` / `write_scenario_verdicts`) — a separate class-D file
  (`.harness/runs/scenario-verdicts.json`). `check_staged` / `check_reckon` are
  untouched.
- `scripts/spec_test_gate.py`: the `scenarios` run loop gains ONLY shadow
  instrumentation (build the ledger, annotate each scenario's perf row, persist
  fresh verdicts). The loop still runs every scenario.
- `harness_lib/gate_perf.py`: an additive `shadow` rollup block over the new row
  fields; `cacheHit`/`cacheMiss` ride the pre-existing `reserved` block.

Does not cover: actually skipping a scenario (Phase 2), subprocess-level
dependencies that are not import edges (see Ceilings), or target-repo gates.

## Requirements / invariants (numbered, testable)

1. **Never skip (Phase 1).** The scenarios gate runs every scenario. No shadow
   field, affected verdict, or cache hit removes, short-circuits, or reorders a
   run. The only skip in the loop is the pre-existing `_`-prefix helper skip.
2. **Import-closure affected-set.** A scenario is AFFECTED iff a changed path is
   in its transitive import closure (Graphify `imports` edges) OR the scenario
   file itself changed. Only `imports` edges are used; the closure includes the
   scenario file's own node.
3. **Conservative fallback (RUN on any doubt).** Every uncertainty resolves to
   AFFECTED: a missing/stale/malformed graph (FB-1) → ALL affected; a
   global-trigger change (FB-2, the subprocess-reached entry points) → ALL
   affected; a changed path not attributable to an import-graph module under
   `scripts/` or `testing/scenarios/` — a data file, spec, config, tool, or a path
   absent from the graph (FB-3) → ALL affected; a scenario whose closure is
   unknown (FB-4) → affected. An empty change set (FB-0) affects nothing (a legit
   no-op, not a doubt).
4. **Per-scenario cache key.** key = `hash(scenario-id + closure-hash + gate-version)`
   where closure-hash is over the git index blob shas of the closure files and
   gate-version reuses `validation_stamp.validator_version`. A changed closure
   blob or a changed gate-version moves the key (→ miss → run); a missing blob
   hashes as `?` (→ miss → run).
5. **Additive store.** The per-scenario verdict store is a separate class-D file
   written under a lock (mirroring `stamp_staged`); it never touches
   quality-state, `check_staged`, or `check_reckon`. A missing/corrupt store reads
   as empty (→ all misses → all run).
6. **wouldSkip is double-guarded.** A scenario is would-skip ONLY when it is NOT
   affected AND has a matching cache hit. `affected` alone forces a run even on a
   cache hit.
7. **False-skip detector.** For each would-skip scenario (which still ran), if its
   ACTUAL verdict differs from the cached verdict, record `falseSkip: true` and
   emit a LOUD stderr warning. `falseSkip` is the safety signal Phase 2 is gated
   on.
8. **Fail-open shadow.** Any error building or running the shadow layer leaves it
   idle (no annotation) and never raises into the gate. Measurement must never
   break the gate.
9. **gate-perf rollup.** `gate-perf` surfaces `cacheHit`/`cacheMiss` (the
   pre-existing `reserved` block) and a `shadow` block (`wouldSkip`, `falseSkip`
   counts + `wouldSaveS` seconds) — present only when a producer emits the fields,
   preserving back-compat with pre-SPEC-159 sidecars.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Test-impact analysis via the dependency graph, conservative full-run fallback | Google TAP, Ekstazi, pytest-testmon [web]; backlog `wf-affected-scenario-selection` |
| Content-addressed per-scenario cache key (fingerprint + id + gate-version) | Bazel / Nx / Turborepo remote-cache design [web]; backlog `wf-gate-result-cache` |
| Shadow/measure-only Phase 1 with a false-skip detector before any skip | A wrong affected-map = a skipped regression = false green (the single highest-stakes WF item); shadow-then-enforce is the safe rollout for a correctness-critical optimization |
| Reuse SPEC-137 manifest/fingerprint + SPEC-158 sidecar, add no new capture | Do-not-reinvent; the fingerprint, index read, and per-scenario timing already exist |
| Global-trigger floor under the import-graph blind spot | Scenarios reach the CLI via subprocess, not import edges; a change to `harness.py`/gate entry points must force full-run until Phase 2 models subprocess deps |

## Gherkin scenarios (UI surfaces only)

This is a gate-internal mechanism with no UI surface; its checks resolve to the
named checks in `testing/scenarios/gac_gate_affected.py` (`gac-1`..`gac-9`). No
Gherkin block is required (SPEC-116 inv. 4: the UI-required judgment is that there
is no UI here).

## Ceilings (upgrade paths)

- **Import-graph blind spot (the reason Phase 1 is shadow).** A scenario that
  drives the CLI via subprocess has no import edge to the code it exercises, so
  the import closure can under-approximate its true dependencies. Phase 1 covers
  this with the global-trigger floor (FB-2) AND measures the residual risk with
  the false-skip detector. Phase 2 must model subprocess dependencies (or keep the
  global-trigger floor permanently) before it may skip.
- **Whole-file closure granularity.** The key is over whole-file blobs, not
  symbols. Move to symbol-level impact only if whole-file churn proves too coarse.
- **Plain-JSON store, capped at `_SCENARIO_CACHE_CAP` newest entries.** Move to an
  indexed store only if the cache outgrows a full read.
- **Self-only.** A `--target` per-repo view lands with the multi-repo era.

## Phase 2 (owner-gated follow-up — NOT in this spec's build)

Phase 2 turns skipping on: an unaffected scenario with a matching cache hit is
SKIPPED and its cached PASS reused. It is a separate, owner-gated task, admissible
ONLY after the shadow data shows `falseSkip == 0` over N real gate runs (the
threshold is the owner's call) AND the subprocess blind spot above is resolved.
The ledger stays authoritative (the cache is advisory); a cache miss always runs.

## Test strategy

- Behaviors to verify: import-closure intersection (incl. transitive) marks only
  dependents affected; a changed scenario marks itself; every conservative
  fallback (FB-0..FB-4) resolves to ALL-affected/none; cache-key stability +
  change sensitivity; the store round-trips additively; the false-skip detector
  fires on a verdict divergence; `affected` overrides a cache hit; `gate-perf`
  rolls up the shadow fields; the gate loop never skips.
- Edge cases: empty change set, missing graph, missing blob, missing/corrupt
  store, shadow-construction error (fail-open).
- Regression risks: none — `check_staged`/`check_reckon` untouched; the gate still
  runs every scenario; `gate-perf` shadow block is additive and absent on old
  sidecars.
- Coverage impact: enforced via `testing/scenarios/gac_gate_affected.py`.

## Validation

- `python testing/scenarios/gac_gate_affected.py` green (`gac-1`..`gac-9`,
  incl. the false-skip detector + every conservative fallback).
- `python scripts/harness_lib/gate_affected.py` self-check green.
- `python scripts/harness_lib/gate_perf.py` self-check green (shadow rollup).
- `python scripts/harness.py gate-perf --json` after a scenarios run surfaces
  `reserved.cacheHit`/`cacheMiss` and the `shadow` block, with `shadow.falseSkip == 0`.
- `pvg`/`pvr` scenarios green (the per-scenario store is additive; the stamp
  pattern is unchanged).
- `spec-pack` (feature-spec-conformance) green.

## Amendments

### v2 — Phase 2 enablement (enforced skip), owner GO 2026-07-22 (f134af2)

Phase 2 goes live behind a single reversible flag. Prereq m5 falseSkip was
reclassified an environment-flake after root-cause (5248a3f); EXP-29 re-arms in
enforced mode. Semantics (additive to the Phase-1 invariants above; none are
weakened):

- **A1 — Flag.** `.harness/project.json` → `validation.scenarioSkipEnabled`
  (default absent/false = the Phase-1 shadow-only behavior, byte-compatible). Read
  ONCE in the scenarios gate where the ledger is built.
- **A2 — Parallel-only enforcement.** Skips apply ONLY in the parallel path (the
  SPEC-160 D041 default). The serial loop stays EXHAUSTIVE by design: the
  wind-down `--serial` probe is the standing drift control and must run
  everything; the serial fallback stays conservative. `flag on + --serial` = zero
  skips. Zero new CLI flags.
- **A3 — `ShadowLedger.wants_skip(sid) → dict | None`.** The deterministic
  pre-run skip decision: returns the cached entry IFF `self.ok` AND the scenario is
  NOT affected AND the cache key is stable AND the cached verdict == `pass` AND
  `not self.skip_disabled`. ANY doubt → None (runs). Pure read; never mutates the
  store, so a skip can never feed the verdict cache.
- **A4 — Pre-filter at the call site.** `spec_test_gate` partitions the run order
  BEFORE `gate_parallel.run_default_parallel` (gate_parallel unchanged): each
  skipped sid emits `result("scenarios:<sid>", "skip", "cache-skip …")` — a skip is
  a SKIP, NEVER a pass (the rt6 2026-07-20 pseudo-pass poisoning precedent) — plus a
  `{skipped, savedS}` perf row; only the remainder is sharded. Skipped scenarios are
  not annotated and their cached verdicts are not rewritten (the store refresh only
  ever comes from real runs). If `run_default_parallel` returns None (`--serial` or a
  parallel-infra fallback), the serial loop runs the FULL original order and the
  pre-emitted skip rows are dropped — a fallback never loses coverage.
- **A5 — Detector auto-disable.** The ledger gains `skip_disabled`; the first
  falseSkip in a run (a cached PASS that actually FAILED) latches it True, so
  `wants_skip` returns None for the rest of that run. Already-emitted skips stay
  skipped (bounded exposure); the fresh FAIL verdict invalidates the cache for the
  next run. The Phase-1 LOUD stderr SHOUT is preserved.
- **EXP-29 citation + reversal.** Enforced measurement begins under EXP-29; review
  checkpoint = 20 enforced runs or 7 days → owner verdict. Reversal is one flag:
  set `scenarioSkipEnabled` false (or absent) → the gate returns to run-everything;
  the ledger stays authoritative and a cache miss always runs.

Teeth: `testing/scenarios/gac_gate_affected.py` adds `gac-skip-ne-pass`,
`gac-detector-disables`, `gac-serial-exhaustive` alongside the Phase-1 checks.

### v3 — subprocess/source-read edges + a second SHADOW map (wf-subprocess-edges), 2026-07-22

The affected-set's structural blind spot (Ceilings §1) is the reason the floor is
global for `harness.py`/`common.py`/… : a scenario reaches those through a
SUBPROCESS or a `read_text`, not an import edge, so the import closure cannot trace
them. This amendment recovers those edges STATICALLY and measures — in SHADOW, no
skip behavior changes — whether a narrower floor would still be safe. **The
narrowing FLIP (making affectedV2 the map `wants_skip` consults) is a later,
separate owner decision; this ship is subtasks 1+2 only: the extractor and the
second shadow map.** Additive to every Phase-1/Phase-2 invariant; none weakened.

- **B1 — Static edge extractor.** `harness_lib/gate_subprocess_edges.py` (pure
  stdlib `ast`) extracts, for each `.py` graph node under `scripts/` +
  `testing/scenarios/`, an edge to every OTHER graph node whose repo-relative path
  it resolves at rest — ONE collection rule covering subprocess argv literals,
  `read_text()` targets, and the `bash py-run.sh scripts/harness.py …` literal.
  Resolution follows `ROOT/"a"/"b"` chains, `str()`/`Path()` wraps, and Name
  assignments (incl. a `HARNESS = […]` list and its `[*HARNESS, …]` splat). Output
  `{path: {edges, unresolved}}`; functions take `root` + an injected graph (no
  module-level ROOT). It lives at `gate_subprocess_edges.py` so it matches the
  `gate_*.py` `VALIDATOR_INPUTS` glob DELIBERATELY: an extractor edit stales every
  cache key (conservative-correct).
- **B2 — Wrapper exception.** No edges attach to `testing/scenarios/_lib.py`
  itself; a `run(…)`/`scrub(…)`/`_lib.run(…)` call INSIDE a scenario adds that
  scenario → `scripts/harness.py`. `_lib` is imported by every scenario but only
  run-callers reach the CLI; attaching the edge at the call site keeps non-callers
  narrow. Upgrade path: a real call graph following `_lib.run` into `subprocess`.
- **B3 — Fail-open unresolved.** A subprocess call whose PROGRAM element is opaque
  (an f-string or an unfollowable variable) marks the file `unresolved`; an
  `ast.parse` failure or unreadable file does too (never raises). `-c`/`-m` inline
  runs and literal non-node paths are resolved-no-edge. An unresolved scenario, or
  ANY transitively-reached unresolved module, gives closure `None` → FB-4 →
  always-affected, never a skip. A broken extractor ⇒ all-unresolved ⇒ all-affected.
- **B4 — affectedV2 = merged closure + shrunk floor.** `scenario_closures` unions
  imports ∪ subprocess edges before the closure walk; `affected_scenarios(…,
  sub_edges=…, triggers=_GLOBAL_TRIGGERS_V2)` computes the second map. The v2 floor
  drops `harness.py`, `cli_registry.py`, `cli_catalog.py`, `common.py`, and `_lib.py`
  (all now edge-reachable — harness.py via the wrapper edge, the rest via harness.py's
  import closure or the plain `_lib` import) and KEEPS `spec_test_gate.py` +
  `harness-test.py` (the gate runners — nothing edges TO them). Every FB-0..FB-4
  doubt still RUNS.
- **B5 — Flag + second shadow row.** `.harness/project.json` →
  `validation.subprocessEdgesEnabled` (default absent/false = today's map stays THE
  map, byte-compatible; affectedV2 stays None and no V2 fields are stamped). Read
  once in `ShadowLedger._build_v2` (own fail-open — a V2 bug never disables the
  today's-map shadow). When on, `annotate` additionally stamps `affectedV2`,
  `wouldSkipV2`, `falseSkipV2`, `wouldSaveV2S` (reusing `shadow_row` against today's
  cache key — a not-affectedV2 scenario has an unchanged import closure too, so the
  key still hits) and SHOUTS on a V2 divergence. MEASURE-ONLY: never latches
  `skip_disabled`, never feeds `wants_skip`. `gate-perf` gains an additive `shadowV2`
  rollup mirroring `shadow` (present only when a producer emits the fields).
- **B6 — Flip criterion (owner-gated, NOT in this build).** The narrowing flip
  (affectedV2 replaces affected in `wants_skip` under the v2 floor) is admissible
  ONLY after the shadow data shows `falseSkipV2 == 0` over ≥20 runs / 7 days AND no
  new-orphan regressions — the owner's verdict, mirroring the v2 flip gate. EXP
  candidate (the affected-vs-affectedV2 narrowing count is the effect size to
  register). Reversal stays one flag: `subprocessEdgesEnabled` false → no V2 stamping.

Teeth: `testing/scenarios/gac_gate_affected.py` adds `gac-sub-edges`,
`gac-sub-wrapper`, `gac-sub-readtext` (the anti-orphan tooth), `gac-sub-unresolved`,
`gac-floor-v2`, `gac-v2-shadow`; `gate_subprocess_edges.py` + `gate_affected.py` +
`gate_perf.py` carry extended stdlib self-checks.

### v4 — invalidation-events vocabulary folded into a shared enum (W29.N2), 2026-07-28

The §4 key components (closure-hash, gate-version) were one of 2+ taxonomies
drifting apart while naming "the event that voids accepted evidence" — the
others being THEME1 CONCEPT-002's invalidation list (WF-20260720-175712) and
the W29 round's trust-boundary events (model-swap, secret-rotation, test-edit
post-execution). `harness_lib/invalidation_events.py` is now the single
canonical vocabulary: this spec's key components appear there sourced
"gate-affected-cache §4", and future producers/consumers (N3 review-gate
freshness, N6 observe-only gate checks) import those names instead of minting
new strings. Observe-only — no cache-key, shadow, or skip behavior changes.
Teeth: `w29_observe_first.py` runs the module self-check and adds
`w29:invalidation-tamper-covered` (every named Proof-or-Stop tamper class maps
to a defined event) + `w29:invalidation-spec-fold` (renaming a §4 key component
here without updating the enum — or vice versa — goes red).
