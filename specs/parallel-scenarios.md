# SPEC-160 — Parallel scenarios: sharded execution for the scenarios gate (DEFAULT)

Status: SPEC-160, proposed 2026-07-20; parallel made the DEFAULT 2026-07-21 (owner
flip, D041, on EXP-30 real-battery equivalence — see Amendments)
(acceptance: `testing/scenarios/gps_gate_parallel_scenarios.py`).
Origin: backlog `wf-parallel-scenarios` (WF roadmap). Door: covered surface —
`spec_test_gate` already owns the scenarios gate and its per-scenario isolation;
this spec adds only an OPT-IN sharded run path plus the equivalence contract
(SPEC-116 flow, existing-spec-neighbour `gate-observability.md`).
relates-to: `wf-gate-observability`.

## Goal

Attack the scenarios gate's serialization: today `spec_test_gate` loops
`_run_isolated_scenario`, a per-scenario `snapshot_volatile_state` /
`restore_volatile_state` on the SHARED ROOT/.harness — measured at ~35% of gate
wall (isolation tax) and the single serialization point. Add an OPT-IN
sharded-parallel path: N workers, each running a SERIAL SHARD of the scenarios
against its OWN disposable repo copy, verdicts merged. Parallel became the
DEFAULT on 2026-07-21 (owner flip, D041) after EXP-30 proved real-battery
equivalence; `--serial` forces the preserved serial loop, which also remains the
automatic fallback on any parallel-infra error. Correctness is paramount — a
scenario run against a wrong or shared copy is a FALSE GATE, so equivalence and
fail-safety are the teeth, not the speedup.

## Applicability

`scripts/spec_test_gate.py` (the `scenarios` gate) gains a `--parallel[=N]` flag;
the orchestration lives in `scripts/harness_lib/gate_parallel.py`
(shard / run / merge / serial-fallback + the equivalence property). It REUSES the
existing isolation/copy infra — `controlled_writes.workflow_runtime_ignore` (the
temp-copy exclusion policy) for the per-worker disposable copy, and
`scenario_isolation.snapshot_volatile_state`/`restore_volatile_state` for
per-scenario isolation WITHIN a worker's copy — and the mediated bounded spawn
(`processes.run_process_tree_bounded`). The serial loop is PRESERVED
byte-unchanged behind `--serial` and as the automatic infra-error fallback (the
flip's reversal path). It does NOT touch target-repo gates, and never lets a
parallel worker mutate the real ROOT/.harness.

## Requirements / invariants (numbered, testable)

1. **Parallel is the default; serial is preserved byte-unchanged.** (Amended
   2026-07-21, D041.) The gate runs the sharded-parallel path by default;
   `--serial` forces the existing serial `_run_isolated_scenario` loop, whose
   per-scenario output and isolation are unchanged, and ANY parallel-infra error
   falls back to that same loop (invariant 7). Reversal = flip the default back;
   no state to unwind.
2. **Bounded shards.** `--parallel[=N]` tunes the worker count (N omitted ->
   cores) for the default sharded run, capped at a fixed oversubscription
   ceiling and at the scenario count; independent of the unrelated workflow
   `max_workers`.
3. **Per-worker isolated copy — no shared-state race.** Each shard worker runs
   inside its OWN disposable full-repo copy built by the reused temp-copy
   exclusion policy; workers never read or write the real ROOT/.harness, so
   concurrent shards cannot race on shared state. Within a worker, scenarios run
   serially under the existing per-scenario snapshot/restore on the copy's root.
4. **Shard split is lossless and balanced.** The scenario list partitions into
   shards with no scenario dropped or duplicated, and shard sizes differ by at
   most one.
5. **Merge preserves per-scenario verdicts.** Merging shard results yields one
   verdict per scenario; a scenario appearing twice with conflicting verdicts, or
   a merge missing/adding a scenario, is an inconsistency that raises (-> serial
   fallback, invariant 7).
6. **Equivalence — parallel verdicts == serial verdicts.** For a given scenario
   set and runner, `verdicts_parallel` returns an IDENTICAL per-scenario pass/fail
   map to `verdicts_serial` for every worker count. This is the acceptance
   property; a divergence blocks. (The gps teeth prove it on a fixture set; the
   default-flip follow-up runs the same property over the real battery.)
7. **Fail-safe to serial.** ANY parallel-infra error (copy fails, worker raises,
   merge inconsistent/incomplete) makes `run_parallel_scenarios` return None and
   the gate falls back to its serial loop and still completes. The parallel
   machinery must never fail the gate. This covers the whole default dispatch
   (`run_default_parallel`): the post-merge shadow annotation is fail-open — a
   shadow bug neither fails the gate nor loses the already-merged verdict rows.
8. **Measured, not silent.** The parallel wall time is emitted into the gate-perf
   sidecar (reusing the existing `_PERF_ROWS` plumbing) so the speedup and the
   isolation-tax reduction are visible.
9. **Serial parity of the worker path** (2026-07-20 audit): per-scenario
   duration, retry-once + recovered-on-retry reporting, failure forensics
   (stdout+rc into the real root's sidecar) and the SCENARIO-SKIP protocol all
   carry through to the result and perf rows. The SPEC-159 shadow never runs
   INSIDE a worker; since the 2026-07-21 flip (D041 — the owner judgment this
   wiring was gated on) the GATE annotates the shadow from the MERGED verdicts
   on the real root: skip verdicts never annotate and never reach the
   scenario-verdict cache (same rule as serial).
10. **Skip-recovery — the default gate never silently loses serial coverage.**
   (Owner direction 2026-07-21: serial divergences matter.) A scenario that
   self-skipped INSIDE a worker copy gets ONE serial re-run on the REAL root
   (standard per-scenario isolation) at the end of the parallel pass
   (`recover_copy_skips`): a pass/fail REPLACES the row (loudly labeled
   `serial-recovery |`), a fail fails the gate, a serial re-skip stays an
   honest skip, and any recovery error keeps the original row (fail-open,
   never worse than before). Recovered verdicts feed the shadow like serial
   ones. Acceptance: `gps-7`.
11. **The latency class runs outside the pool** (v4, 2026-07-27). Shards are
   sized for THROUGHPUT (N workers on N cores); a scenario driving a real
   browser needs event-loop RESPONSIVENESS and loses that fight deterministically.
   Members of `_SERIAL_LANE` are partitioned out in `run_default_parallel`
   — BEFORE the purity boundary, so `verdicts_serial(X) == verdicts_parallel(X)`
   still holds for X = the pool and `run_parallel_scenarios` is unchanged — and
   run serially on the REAL root after the pool drains (`run_serial_lane`), with
   the GATE's serial semantics: retry-once via `attempt="-retry"`, a loud
   `recovered-on-retry` label, the SCENARIO-SKIP protocol, and rows labeled
   `serial-lane |`. Membership requires BOTH (a) it drives a real browser and
   (b) forensics showing contention-shaped fail-through-retry that passes
   standalone. The merged row set is asserted COMPLETE against the gate's own
   `scenario_paths` (name set + length, so a duplicate cannot mask a drop) and
   emitted in original order; a violation is caught IN PLACE — never raised past
   this frame, which the gate calls inside a `try`/**`finally`** — and degrades to
   `return None` plus a `_parallel_abort` ledger row. Acceptance: `gps-9`, `gps-10`.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Shard N workers, not 150 per-scenario copies | Plan brief measurement — per-scenario copy cost would exceed the win; the isolation tax is 35% of gate wall (gate-perf, 10 runs) |
| Serial stays the default until equivalence is proven on the real battery | Correctness-first: a scenario against a wrong/shared copy is a FALSE GATE; opt-in de-risks the rollout (pytest-xdist adoption pattern [web]) |
| Reuse temp-copy exclusion policy + per-scenario isolation, do not invent a copy mechanism | `controlled_writes.create_temp_workspace`/`workflow_runtime_ignore` and `scenario_isolation` already exist and are gate-proven; a hand-rolled copy is the risky path the brief forbids |
| Fail-open to serial on any parallel-infra error | The gate must never go red because of the optimizer; mirrors `gate_perf.flush_run` / `gate_hold_guard` fail-open discipline |
| Equivalence as a pure, injectable property | The orchestration is testable without real copies; the same property is the guard the default-flip follow-up runs over all scenarios |

## Ceilings (upgrade paths)

- **Copy fidelity (the residual before default-flip).** The per-worker copy is a
  DETACHED `git worktree` pinned to the run's HEAD sha — or, when the INDEX
  differs from HEAD (a `validate --staged` run), to a DANGLING commit of the
  index tree (`write-tree`+`commit-tree`, 2026-07-21), so shards exercise the
  exact STAGED code the staged stamp certifies; no ref ever moves — (2026-07-20,
  EXP-30 prerequisite): the `.git` + HEAD-materialized `.harness/state` fidelity gap is
  CLOSED — the worktree carries a real `.git` and the HEAD-tracked tree, and the
  volatile live dirs serial's in-gate hold materializes (`.harness/state`,
  `context`, `runtime`, `routing`, `workflows/active`, `runs`) are created empty
  to match serial's hold baseline. Each copy is ATTESTED after checkout (HEAD ==
  pinned sha AND `git status --porcelain` empty); an attestation mismatch raises
  `ParallelInfraError` -> serial fallback, never a silent unfaithful copy. The
  REMAINING declared residue is branch-NAME display: a detached worktree reports a
  detached HEAD, so a check that reads the branch NAME diverges from serial. That
  residue is the DECLARED EXP-30 quarantine candidate for the owner's flip
  judgment — measured by EXP-30 pairs, not hidden. **Safety property (non-negotiable,
  tested):** worktrees are ALWAYS `--detach`, so a commit inside a copy (scenarios
  run real git) is a dangling object that can NEVER move the real repo's
  `refs/heads/*` — a hard-kill mid-scenario cannot move the owner's branch
  (`gps-6` + the module self-check assert the branch ref is unchanged after a
  detached-copy commit). Disposal is `git worktree remove --force` from ROOT with
  an rmtree fallback; a `git worktree prune` at each parallel run's start sweeps
  entries leaked by a hard-killed prior run. The default flip happened 2026-07-21
  (D041) on EXP-30's measured real-battery equivalence; the predicted branch-name
  residue never materialized in pairs 2-5.
- **Declared quarantine (owner decision (a), 2026-07-20, EXP-30 pairs 2-3):** the
  ONLY systematic copy divergence root-caused across the faithful-copy pairs is
  m4's `empty:seeds-gone` noDrift clause — `protected_files.compare_snapshot`
  hashes RAW bytes, and a fresh worktree checkout normalizes EOLs vs the live
  tree's as-written bytes (false environmental drift on the canonical files).
  Remedy (a): the clause is quarantined ONLY under `HARNESS_PARALLEL_COPY=1`
  (set exclusively by the parallel worker env), loudly labeled in the check
  detail; live/serial runs keep the byte-exact protection teeth (remedy (b),
  EOL-normalized hashing, was rejected to keep the canonical-file guard strict).
  The predicted branch-name residue never materialized in pairs 2-3.
- **Worker count** is a fixed oversubscription ceiling; make it a project.json knob
  only if a host measurably benefits from more.
- **Within-worker isolation** keeps the per-scenario snapshot/restore; drop it to
  one-copy-per-scenario only if a shard's scenarios prove to leak into each other
  despite the snapshot (not observed).

## Test strategy

- Behaviors to verify: shard split (lossless, balanced); merge preserves verdicts;
  conflicting/incomplete merge raises; the equivalence property (serial == parallel
  for every N); forced worker error -> serial fallback with the full verdict map.
- Edge cases: single worker; workers > scenarios; a shard that drops or conflicts a
  verdict; a shard that crashes.
- Regression risks: the preserved serial loop (`--serial` + infra-error fallback)
  must stay byte-unchanged (`si_scenario_isolation` green); `spec_test_gate.py`
  must stay under the gs-7 line ratchet (logic lives in `gate_parallel.py`).
- Coverage impact: enforced via `testing/scenarios/gps_gate_parallel_scenarios.py`.

## Validation

- `python testing/scenarios/gps_gate_parallel_scenarios.py` green (checks `gps-1`
  shard split, `gps-2` merge, `gps-3` equivalence, `gps-4` fallback, `gps-5`
  serial-parity of the integration glue: order, verdict/skip, duration,
  recovered-on-retry, perf rows; `gps-7` skip-recovery semantics; `gps-9` the
  latency-class serial lane; `gps-10` the completeness net's teeth and fail-safe).
- `python scripts/harness_lib/gate_parallel.py` self-check green.
- `python testing/scenarios/si_scenario_isolation.py` green (serial isolation path
  unchanged).
- `python testing/scenarios/gs_gate_structure.py` green — `gs-7` confirms
  `spec_test_gate.py` under the frozen line ratchet.
- `spec-pack` (feature-spec-conformance) green.

## Amendments

- 2026-07-20 — HEAD-faithful worktree copy (EXP-30 prerequisite). The per-worker
  copy mechanism changes from a `workflow_runtime_ignore` copytree to a DETACHED
  `git worktree` pinned to the run's HEAD sha, closing the `.git`/HEAD-state
  fidelity gap (see Ceilings). Adds the post-checkout attestation seam
  (`attest_worker_copy`, raising `ParallelInfraError` on HEAD/porcelain mismatch),
  volatile-dir materialization, `git worktree prune` crash hygiene, and the
  non-negotiable detached-commit ref-safety property. Acceptance gains `gps-6`
  (real-git scratch-repo teeth: faithful attestation, detached-commit ref-safety,
  sabotage rejection, clean dispose). The default stays serial; the flip stays
  owner-gated on EXP-30's measured equivalence and the branch-name-display residue.
- 2026-07-21 — DEFAULT FLIP (owner decision D041, "bora fazer o flip e ir
  ajustando as inconsistências conforme aparecerem"). EXP-30 closed: pairs 3-5 on
  the faithful worktree copy show zero non-quarantined SYSTEMATIC divergences
  (pair 5: per-scenario rc identical across all 151; the single rt6 pass->skip was
  load-transient, fail-safe, and is tracked by the copy-env-flake-hunter hunt);
  stable wall win ~3.5-4x (178-227s vs ~11.8min). Changes: parallel is the gate
  default; `--parallel[=N]` now only tunes worker count; new `--serial` forces the
  preserved serial loop (also the automatic infra-error fallback); invariants 1, 2
  and 9 amended in place. The SPEC-159 shadow — wiring gated on exactly this owner
  judgment — now feeds from the MERGED verdicts, annotated by the GATE on the real
  root (never inside a worker; skips still never reach the verdict cache), so
  EXP-29 falseSkip evidence keeps accumulating on default runs. Flip-review
  hardening (same day): (i) the shadow annotation is fail-open inside
  `run_default_parallel` (a ledger bug can neither fail the gate nor lose merged
  rows); (ii) STAGED-PIN — when the index differs from HEAD (`validate --staged`),
  workers pin to a dangling `commit-tree` of the index so the battery exercises
  the exact staged code (pin-to-HEAD would have validated the PREVIOUS commit and
  stamped a fingerprint whose code never ran); (iii) the module self-check gains
  dispatch teeth (--serial precedence, merged-shadow skip/wall exclusion,
  annotate-crash survival) and a real-git staged-pin case. Same day, second
  hardening (owner: "divergências seriais no final dos loops importam"):
  invariant 10 SKIP-RECOVERY — copy-skips re-run serially on the real root at
  the end of the parallel pass, so scenarios with environmental copy-absence
  (e.g. pw_ui_smoke's gitignored node_modules) keep their serial-gate coverage
  under the parallel default; `gps-7` teeth. Reversal: flip the
  default back to serial; no state to unwind.
- 2026-07-27 (v4) — **LATENCY-CLASS SERIAL LANE (invariant 11), and a silent
  per-check coverage loss found while measuring it.** The D041 flip shipped
  without a latency-class carve-out. That is the honest framing of this
  amendment: throughput sharding is right for the battery and wrong for a
  browser.

  **The demand, measured.** `ui_e2e` blocked 2 of 4 gates on 2026-07-27 and
  passed standalone 40/40 the same hour. The failing CHECK moves — `plan-approve`,
  `chip-prev-diff`, `chip-diff`, `gate-tracker` — across exactly TWO error shapes
  (`wait_for_selector: Timeout 24000ms exceeded`, and a `TypeError` on an
  undefined element). A localized regression hits one check; this does not.
  `.harness/runs/scenario-forensics/` holds **54** `ui_e2e` failure dirs, so
  "flake" understated it. Root cause in one number: `os.cpu_count() == 8` and
  `_MAX_WORKERS = 8` — eight shards on eight cores, zero headroom, beside a
  desktop. The in-gate retry stopped rescuing it (gates 094543 and 095443 failed
  attempt AND retry), which is why no deadline is widened here: widening no
  longer even reaches, and every widening hides a real regression longer. Running
  in the lane at BASE scale in fact NARROWS ui_e2e's deadlines from 24s to 8s.

  **Rejected: `resolve_workers` headroom** (one line vs ~25). `cores-1` barely
  moves the contention ratio against a 24s scheduled-wait timeout; `cores-2` is
  the only variant with a real mechanism and costs **+95s/gate — more than the
  lane's measured +40-70s** — forever, for a probabilistic outcome. A
  pre-measurement is cheap to run and expensive to trust: against p≈0.5-0.75 it
  needs 6-10 consecutive clean runs under an uncontrolled covariate (desktop
  load), and a false clean streak ships the flake straight back into the commit
  path. Reopen if the lane ships and `ui_e2e` still fails in-gate — that would
  mean contention was never the cause, and the lane becomes the controlled
  experiment that revives the headroom and deadline theories on data.

  **The lane runs on the REAL root, and that is load-bearing, not incidental.**
  `vendor/tree-sitter/.gitignore:4` gitignores `tree-sitter-python.wasm` and the
  file is untracked; `testing/ui/test_panel_e2e.py:210,664` gate four checks on
  its presence (`hl-renders`, `hl-on-demand`, `hl-scroll`, `chip-code-hl`). A
  detached worktree carries TRACKED content only, so **those four checks have not
  run in the gate since the D041 flip** — 40 standalone − 4 = the 36 the parallel
  path reported. This is a per-CHECK coverage loss that scenario-level
  completeness structurally cannot see: the scenario still reports pass. The lane
  restores them; the CLASS is registered as `gate-check-level-coverage-loss`.

  **Correctness notes that cost real defects in review.** (i) The lane needs the
  GATE's retry-once, not `recover_copy_skips`' single shot — otherwise the gate's
  flakiest scenario becomes its only un-netted path, reintroducing the symptom at
  a lower rate. (ii) The completeness assertion must be caught IN `run_default_
  parallel`: the gate calls it inside a `try`/`finally`, so a raise there crashes
  the whole gate instead of falling back, violating the fail-safe law. (iii) The
  net's LENGTH guard is not redundant with its name-set check — a drop is already
  caught by the name-keyed reorder, but a lane row DUPLICATING a pool scenario
  collapses in the dict and would silently overwrite that scenario's verdict.
  Measured 2026-07-27: with the assertion mutated out, a drop-only sabotage still
  went red, i.e. the first version of `gps-10` claimed teeth it did not have.

  **Membership is a RULE, not a list (added same day).** `gps-9` asserts every
  `_SERIAL_LANE` member resolves to a scenario that actually drives a browser.
  Without it the lane silently becomes a "slow scenarios" dumping ground and each
  addition serializes the gate further. Only the mechanism half is checkable — the
  forensics half stays a documented judgment, because forensics are local and
  gitignored. The counter-example is proven, not assumed: `worker_live_tail` is
  HEAVIER than `ui_e2e` (126.9s vs 124.3s) and carries zero browser markers, so
  adding it goes red.

  Reversal: `_SERIAL_LANE = ()` — the partition degenerates to the pre-v4 flow
  byte-equivalently. No state to unwind.

### v5 (2026-07-28) — the rc alone was never evidence

A codex sol-xhigh lane, with the PID split re-measured 3/3 by the overseer
before acceptance, proved the gate could certify a FAILING scenario as pass. On
Windows the venv `python.exe` that `Popen` returns is a LAUNCHER; the
interpreter that writes the scorecard is a DIFFERENT PID (4/4 lane, 3/3
overseer). `run_process_tree_bounded` combines the LAUNCHER's `returncode` with
the DESCENDANT's captured pipe, and both gate paths classified from that
returncode alone. Controlled inversion, 3/3: interpreter prints failed checks
and exits 1, launcher terminates 0 → row recorded PASS, no retry, and no
forensics (they fired only on a non-zero rc).

12. **Two channels must agree.** A scenario passes only when the rc says 0 AND
    the terminal scorecard reports every check passed. A disagreement in either
    direction is a failure — `scenario_verdict.classify` is the single place
    both the parallel and the serial path ask, so they cannot drift apart.
13. **The disagreement is reported, not swallowed.** A contradiction is
    prefixed to the row's detail, so the gate says what happened instead of
    showing a bare tail.
14. **Forensics follow the verdict, not the rc.** An rc-0 attempt whose
    scorecard reports failures now keeps its stdout/stderr — that case
    previously left nothing to look at.

| Decisão | Fontes |
|---|---|
| Bind the verdict to the scorecard writer | measured launcher/interpreter PID split, 3/3 controlled false-green inversions |
| A missing scorecard is NOT a failure | measured: 198 of 204 scenarios emit the canonical line, but `ce1_containment` and two private-summary scenarios legitimately never do — failing on absence would redden healthy scenarios |
| Accept the text coupling | a format change degrades to today's rc-only behaviour, never to a false green; a structured receipt is the upgrade path |

Ceiling: absence of a scorecard still trusts the rc. Upgrade path: a structured
per-scenario receipt written by the interpreter itself, which also removes the
text coupling. NOT closed here: `recovered-on-retry` can still let a retry
certify over a first-attempt failure — a separate policy decision tracked in the
backlog, since tightening it would redden genuinely flaky infrastructure
(`pw_ui_smoke`'s socket exhaustion) rather than a defect.

15. **One retry net, one verdict, both paths.** `scenario_verdict.run_with_retry`
    owns the retry-once net for the serial AND the parallel path. The extraction
    is not cosmetic: wiring the verdict inline pushed `spec_test_gate.py` past
    the `gs-7` line budget, and the ratchet is there precisely to force logic
    out of that file rather than into it.

Validation: `gps-11` drives the REAL `_scenario_run_in_copy` (not an injected
fake — the defect lived inside it) on a throwaway root: a failed scorecard with
rc 0 is refused, the contradiction is visible in the row, forensics exist for
it, an honest green still passes, and a fixture that fails once then passes is
recovered by the retry net. Mutation evidence: false-green branch stubbed →
gps-11 red (its output reproduces the original bug verbatim); forensics reverted
to the rc condition → gps-11 red on the forensics conjunct; retry net removed →
SURVIVED at first, which is why the flaky-fixture conjunct exists — it now goes
red. `python scripts/harness_lib/scenario_verdict.py` — 9-case module
self-check.

### Amendment 2026-08-03: abort retry, bounded fail-fast, durable abort ledger

Two `gate-staged` runs were hard-killed at the 1800s `cmd_validate` cap on
2026-08-03 (09:06, 10:51). Root cause (`.harness/handoff/gate-latency-dossier.md`):
`run_parallel_scenarios` aborted (`ParallelInfraError`, trigger unknown), the gate
fell back to the SERIAL loop, and the serial loop cannot finish the battery inside
1800s (a healthy run needs a 1450s subprocess for 131 of 223 scenarios, before
snapshot/restore overhead). So the fallback did not degrade the gate — it
GUARANTEED a timeout, burning ~30min to certify nothing. The aborts were
transient: the same parallel path passed at 08:43 and 09:51 the same day.

Both aborts left NO recoverable reason — the second occurrence of this exact
blind spot (first: 2026-07-26, 27min lost, trigger unrecoverable from any
artifact). The `_parallel_abort` perf row that invariants 7 and 11 lean on only
reaches disk at SETTLE (`gate_perf.flush_run`, in the gate's `finally`), and an
external hard-kill runs no `finally`: both kills left ZERO abort rows.

Changes (`scripts/harness_lib/gate_parallel.py`, plus ONE env line in
`scripts/harness_lib/validation_stamp.py`):

16. **Durable abort ledger.** `_persist_abort_row(root, stage, exc)` appends
    `{at, stage, error}` to `<root>/.harness/runs/gate-parallel-aborts.jsonl` AT
    ABORT TIME, from BOTH abort sites (`parallel`, `serial-lane-merge`). Fail-open
    — telemetry must never break the gate. The settle-time `_parallel_abort` perf
    row STAYS: it remains the operator surface for runs that do settle.
17. **One retry before any fallback.** In `run_default_parallel`, an abort retries
    the sharded path ONCE (the observed aborts were transient; the `git worktree
    prune` crash hygiene runs inside the retry already). Abort -> a ~6min re-run
    instead of a doomed serial fallback.
18. **Bounded runs fail FAST instead of falling back.** `cmd_validate` marks its
    scenarios subprocess `HARNESS_GATE_TIME_BOUNDED=1`. Under that marker a SECOND
    abort returns one failing row, `scenarios:_parallel_infra`, pointing at the
    ledger and naming the manual escape (`--serial`), because serial provably
    cannot finish inside the cap. Without the marker (foreground
    `harness-test.py scenarios`) invariant 7 is unchanged: a second abort still
    returns None and the gate runs its serial loop.

Invariant 7 is amended in scope, not in spirit: the parallel machinery still never
fails the gate on its own — it fails fast ONLY where the alternative is a
guaranteed timeout, and says why in a file that survives a `kill -9`.

Validation: the module self-check gains abort-then-recover, double-abort +
bounded, double-abort unbounded, and a ledger round-trip against a tmp root (same
injected-rps idiom — no repo copies, no subprocesses). Reversal: drop the retry
and the marker; the ledger is additive telemetry.
