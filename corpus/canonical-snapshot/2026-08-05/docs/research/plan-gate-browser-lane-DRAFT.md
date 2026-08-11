# Gate browser lane — CONSOLIDATED PLAN

Author: `planner-xhigh` spawn (Fable, effort `xhigh`), 2026-07-27, read-only;
written to disk by the overseer. Brief: `.harness/handoff/plan-gate-browser-lane.READY`.
Overseer verification of the load-bearing claims is at the end — **two of the
overseer's own positions were defects and were corrected before any code existed.**

## 0. The demand

`ui_e2e` fails inside the parallel scenarios gate often enough to block commits;
it passes standalone. Stop the browser lane losing a CPU fight — without
weakening the gate and without widening a deadline.

**The contention in one number:** `os.cpu_count() == 8` and `_MAX_WORKERS = 8`.
Eight shard workers on eight cores, zero headroom, alongside ~55 desktop
Edge/WebView2 processes. Browser checks need scheduling *responsiveness*
(`wait_for_selector`), not throughput.

## 1. Corrections to the overseer's brief

**P1 — right seam, two shipping defects.**

1. *"Reuse the same `run_isolated` that `recover_copy_skips` uses"* is a SINGLE
   attempt (`gate_parallel.py:423`). Both the serial loop
   (`spec_test_gate.py:1537-1547`) and the copy path (`_scenario_run_in_copy`)
   carry **retry-once**. A lane built as the brief stated would have been the
   STRICTEST path in the gate for its FLAKIEST scenario — one transient failure
   reds the gate where every other path retries. It reintroduces the very symptom
   the demand names, at a lower rate. The lane needs its own serial-parity
   mini-loop: retry-once, `recovered-on-retry` labelling, SCENARIO-SKIP protocol.
2. The partition must live in `run_default_parallel`, NOT inside
   `run_parallel_scenarios`. That keeps the purity boundary clean (lane stems
   never enter `verdicts_parallel`), leaves `run_parallel_scenarios`
   byte-identical (gps-5 + the module self-check untouched), and — decisive —
   costs **zero lines in `spec_test_gate.py`**, which sits at 1659 against the
   `< 1660` gs-7 ceiling.

**P2 — confirmed directionally; instrument instead of arguing.** Wall is the MAX
shard, not mean work (319s actual vs 287s ideal = 32s straggler gap). Pulling the
2nd-heaviest item out of round-robin likely shrinks the straggler too, so +60s is
an upper bound; call it **+40-70s**. Ship a `_serial_lane` perf row so the real
cost lands in `.harness/runs/gate-perf.jsonl` and the prediction is checked from
the ledger after two runs.

**P3 — right property, WRONG mechanism; as written it breaks the fail-safe law.**
The brief said the completeness assertion should "raise `ParallelInfraError` so
the gate falls back to serial". But `run_default_parallel` has no exception net
and neither does its caller: `spec_test_gate.py:1525` invokes it inside a
`try`/**`finally`** (:1565), not a `try`/`except`. Anything raised there
**propagates and crashes the entire gate**, violating *"parallel machinery must
never fail the gate"*. The assertion must be raised AND caught inside
`run_default_parallel`, converting to `return None` plus a `_parallel_abort` perf
row — because `gate-staged` retains almost none of the inner stdout, so the
ledger is the only surface the operator actually reads.

**P4 — moot; it comes free.** `_run_isolated_scenario` builds env from
`os.environ` minus the scrub set and adds only `HARNESS_SCENARIO_ISOLATED=1`
(`spec_test_gate.py:1387-1391`). `HARNESS_E2E_TIMEOUT_SCALE=3` exists only in the
dict handed to worker-copy subprocesses. The lane therefore runs at **base scale
by default** of the chosen seam — the same regime as standalone (40/40) and every
pre-flip serial gate. Build no scale plumbing. Note for the record: the lane at
base scale **narrows** ui_e2e's effective deadlines from 24s back to 8s — the
opposite of widening.

**The one-line alternative (`resolve_workers` headroom) — rejection CONFIRMED,
on cost dominance rather than the overseer's stated reason.**

- `cores-1` (N=7): +41s/gate, and the contention ratio barely moves against a
  24000ms scheduled-wait timeout. Mechanism: weak.
- `cores-2` (N=6): the only variant with a plausible mechanism — and it costs
  **+95s/gate, MORE than the lane's +60s**, forever, for a probabilistic outcome.
- A pre-measurement is cheap to run and expensive to trust: against p≈0.5-0.75
  you need ~6-10 consecutive clean runs (40-60 min) under an uncontrolled
  covariate (the owner's desktop load is not constant). A false clean streak
  ships the flake straight back into the commit path.

**Recommendation: no pre-measurement; ship the lane.**

## 2. New finding — 4 checks have not run in the gate since the D041 flip

`vendor/tree-sitter/.gitignore:4` gitignores `tree-sitter-python.wasm`, and the
file is untracked. `testing/ui/test_panel_e2e.py` gates exactly four checks on its
presence (guards at `:210` and `:664`): `e2e:hl-renders`, `e2e:hl-on-demand`,
`e2e:hl-scroll`, `e2e:chip-code-hl`.

A detached worktree copy checks out **tracked content only**, so the wasm is
ALWAYS absent in a worker. **40 − 4 = 36**, matching the observed discrepancy
exactly. This is not contention and not the moving-check flake: it is a silent
**per-CHECK** coverage loss that scenario-level completeness cannot see, because
the scenario still reports pass.

Running the lane on the REAL root restores all four as a side effect. An
uncontended worktree copy would preserve the hole — which is what decides open
question 3.

## 3. The design

All in `scripts/harness_lib/gate_parallel.py` + the gps scenario. Zero lines in
`spec_test_gate.py`.

**Seam 1 — the lane constant.** `_SERIAL_LANE = ("ui_e2e",)`. Rollback for the
entire feature is `_SERIAL_LANE = ()`, which degenerates to today's flow
byte-equivalently.

**Seam 2 — `run_serial_lane(lane_paths, run_isolated, result_fn, perf_rows)`**, a
~15-line serial-parity mini-loop mirroring `spec_test_gate.py:1535-1562`: attempt,
retry-once on `rc != 0` with `attempt="-retry"` so retry forensics land in their
own dir; `skip` = rc 0 + `SCENARIO-SKIP:`; `recovered` printed loudly; rows
prefixed `"serial-lane | "`; one `_serial_lane` perf row carrying the lane wall.
Per-scenario perf rows come free from `_run_isolated_scenario`.

**Seam 3 — the partition + merge in `run_default_parallel`** (the only modified
function): partition `scenario_paths` into lane/pool; run the pool exactly as
today (its own net intact, `recover_copy_skips` over pool rows only); then run the
lane; then merge with a **completeness assertion against `scenario_paths` itself**
(the gate's own input, not a copy of the partition logic — so a bug in the
partition cannot also hide in the assertion), plus a length check so a duplicate
cannot mask a drop; emit in ORIGINAL scenario order. Any violation is **caught
here**, logs loudly, appends `_parallel_abort`, and returns None → serial loop.

**Purity contract:** the partition happens BEFORE the contract boundary.
`verdicts_serial(X) == verdicts_parallel(X)` continues to hold with X = the pool.
Lane stems never enter `verdicts_parallel`; gps-3 untouched.

**Edge cases:** ui_e2e cache-skipped → lane empty → byte-identical to today.
`run_isolated is None` (self-check/gps callers) → lane empty → backward
compatible. Pool empty → `run_parallel_scenarios` returns None → full serial loop.

**Isolation the lane inherits, and the dirt risk:** three nested layers — the
gate-level `hold_dirty_baseline` envelope, the per-scenario
`snapshot_volatile_state`/`restore_volatile_state` inside `_run_isolated_scenario`,
and ui_e2e's own MUTABLE snapshot + fixture scrub. Residual: a hard-kill mid-lane
strands the per-scenario hold — the SAME class the serial loop and
`recover_copy_skips` already carry, recovered by `_recover_stale_holds` next run.
**No new risk class.**

## 4. The completeness proof

A chain where every link either preserves rows by construction or raises into a
fallback: `shard` partitions losslessly (gps-1); `verdicts_parallel` raises on
incomplete merge (gps-2) → caught → serial; `recover_copy_skips` is row-preserving
by construction (gps-7); the **new merge is the only new drop point** and carries
the name-set + length assertion above.

**What makes the enforcement itself falsifiable:** gps-10 injects a sabotaged lane
runner that loses one row and asserts `run_default_parallel` returns None AND the
abort row carries the reason. Delete the assertion and gps-10 goes red.

**Declared limit:** this proves scenario-level completeness, NOT check-level. The
wasm finding is the standing counterexample — a scenario can pass while silently
emitting fewer checks. The lane closes the known instance; the CLASS gets a
backlog row, not machinery here.

## 5. Phased plan

- **Phase 1 — the lane.** `gate_parallel.py` (`_SERIAL_LANE`, `run_serial_lane`,
  the `run_default_parallel` partition/merge/net, self-check extended) + gps.
  Check **gps-9**: injected fakes assert lane stems run via `run_isolated` and
  never the pool, retry-once fires and labels, SCENARIO-SKIP becomes a skip, rows
  carry `serial-lane |`, final rows are the full name set in original order, and
  the `_serial_lane` perf row lands. Rollback: `_SERIAL_LANE = ()`.
- **Phase 2 — completeness teeth.** gps only. Check **gps-10**: a sabotaged lane
  runner (drops a row) → None + `_parallel_abort` with the reason; a raising lane
  runner → None likewise.
- **Phase 3 — spec amendment + validation on the real battery.** SPEC-160
  invariant 11, membership rule under Ceilings, dated Amendments entry citing the
  092504-095443 gate record and the wasm finding; plus a backlog row for the
  check-level coverage class. Then two `gate-staged` runs: the `_serial_lane` perf
  row checks the +40-70s prediction, and ui_e2e reporting **40** checks confirms
  the restored wasm coverage. Success metric over ~10 gates: zero ui_e2e
  fail-through-retry.

## 6. What would NOT be built

`resolve_workers` headroom (cost-dominated); a pre-fix N=7/N=6 measurement
campaign (40-60 min under an uncontrolled covariate); a `project.json` lane knob
(a module constant with the principle in a comment); a general check-level
completeness verifier (one known instance, backlog row for the class);
lane/pool overlap scheduling to reclaim the +60s (no deadline breached today);
moving `pw_ui_smoke` into the lane (its copy self-skip is deterministic, so
`recover_copy_skips` already reaches the real root for it).

Each carries the condition that changes the verdict — the headroom one being:
**the lane ships and ui_e2e STILL fails in-gate**, which would mean contention was
never the cause and the lane run becomes the controlled experiment that reopens
the headroom and deadline theories on data.

## 7. Owner decisions (recommendation first)

1. **Membership: `("ui_e2e",)` only**, admitted by a two-part rule — (a) drives a
   real browser (mechanism: event-loop scheduling latency), AND (b) forensics show
   contention-shaped fail-through-retry that passes standalone. `worker_live_tail`
   stays OUT despite being HEAVIER (126.9s): it is not a browser scenario, shows no
   fail-through-retry in today's record, and pulling the pool's heaviest item into
   the lane adds its full weight to the wall for no evidenced benefit. Its 22
   forensics dirs vs ui_e2e's 54 warrant a watch, not a seat.
2. **Placement: AFTER the pool drains.** The gate never short-circuits on a
   scenario failure, so fail-fast buys nothing; after-the-pool matches the
   established `recover_copy_skips` seam, guarantees the machine is provably idle,
   and avoids overlap between lane mutations on the real root and the worktree/
   `write-tree` reads at pool start.
3. **Real root, not a lone worktree copy.** Decisive: the wasm finding — a copy
   structurally cannot run 4 of the 40 checks. Supporting: invariant 10 already
   runs real-root serial recoveries; staged==worktree parity under `gate-staged`.
4. **36-vs-40: root-caused, fixed for ui_e2e here, CLASS gets its own row.**
5. **Framing: SPEC-160 amendment (invariant 11), not a new decision record** — the
   honest narrative (D041 shipped without a latency-class carve-out) belongs IN the
   amendment text, but mechanically this is the same shape as invariant 10.

## 8. Amendment target

`specs/40-features/parallel-scenarios.md` — verified: it is SPEC-160, owns the
invariants this composes with (7/9/10), names
`testing/scenarios/gps_gate_parallel_scenarios.py` as acceptance, and has a live
Amendments section.

---

## Overseer verification (2026-07-27, independent of the author)

| claim | verdict | evidence |
|---|---|---|
| P3 as briefed would CRASH the gate | **CONFIRMED — the overseer's own position was a defect** | `spec_test_gate.py:1565` is `finally:`, not `except:`; `run_default_parallel` is invoked bare at `:1525`, so a raise propagates past the hold release |
| P1 as briefed loses retry-once parity | **CONFIRMED — second overseer defect** | the serial loop retries at `spec_test_gate.py:1543` (`attempt="-retry"`); `recover_copy_skips` calls `run_isolated` exactly once (`gate_parallel.py:423`) |
| P4 is moot; base scale is free | **CONFIRMED** | `spec_test_gate.py:1387-1391` — env is `os.environ` minus scrub plus only `HARNESS_SCENARIO_ISOLATED=1`; no `HARNESS_E2E_TIMEOUT_SCALE` |
| the wasm coverage loss is real | **CONFIRMED** | `git check-ignore -v` → `vendor/tree-sitter/.gitignore:4`; `git ls-files vendor/tree-sitter/grammars/` returns EMPTY (untracked); guards at `test_panel_e2e.py:210,664` |

Not re-verified, carried at the author's confidence: the `_MAX_WORKERS`/straggler
cost refinement (arithmetic over the brief's own measured numbers), the
`worker_live_tail` forensics count, and the claim that nothing downstream indexes
rows by position.
