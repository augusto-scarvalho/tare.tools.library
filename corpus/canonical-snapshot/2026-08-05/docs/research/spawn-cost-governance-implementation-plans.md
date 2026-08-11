# Spawn cost governance (failover/retry frontier leakage) — v4 implementation plans

Deliverable of `docs/research/spawn-cost-governance-round.md`. Phase 3 divergence ran **balanced
cross-vendor**: NVIDIA (`nvidia-compat` workflow WF-20260719-181302-545811, 5 lenses) + Sonnet 5
(3 lenses via `model:sonnet` subagents) = ~35 concept cards. Both vendors converged INDEPENDENTLY.
Channelled by the overseer (this session). Closes the SPEC-153 D033 residual: the SPEC-115 failover hop
re-spawns a rate-limited worker on a bigger fallback card without the spawn-economy guard.

## The convergent thesis (both vendors, all lenses)

1. **Governance must move from PER-FLIGHT to AIRLINE-DISPATCH level** (NVIDIA analogy 005-F, FAA
   ground-stop): the plan-time guard checks fan-out WIDTH — the wrong coordination level; it is
   structurally blind to failover descendants. **The control plane is a per-GROUP (workflow-run +
   its failover descendants) cumulative frontier accumulator, checked SYNCHRONOUSLY at the failover
   hop before re-spawn** (SIMP-1/4, R2, A1/A2, 005-A). Not a $-alert (E7: alerts lag hours).
2. **Measure and control are ONE mechanism at different thresholds** (SIMP-2 + 005-E velocity-check):
   Brief A (measure) = Brief B (control) with `budget=∞` and the gate off. Ship ONE code path behind
   a `block|warn|off` knob — `warn`/`off` IS the probe, lower the threshold to enforce. No separate probe.
3. **The denominator-collapse answer is COVERAGE-GATED FAIL-OPEN** (Sonnet REL-3): a ratio budget's
   "successful" denominator shrinks toward zero in a systemic incident (all workers fail over at once),
   so DON'T key on a success ratio — key on **observed-cost COVERAGE**. Below a coverage floor (e.g.
   <50% of the group's hops have observed $), the guard FAILS OPEN (widens tolerance) instead of
   clamping. Low trust in the number → don't act on it.
4. **Graceful DOWNGRADE not binary refuse** (005-D smart-grid brownout, PERF-01 hysteresis): frontier →
   mid-tier → cheap → fail; a per-worker hop floor keeps a transient 1-2-hop retry structurally exempt.
   Answers J4 (don't starve). Reuse the failover chain's existing "skip to next cheaper entry" (A1).
5. **Reuse the shipped seams** — the executor circuit breaker (extend with a COST trip: R5/C4), the
   `cost_metrics` ledger (a `costUsd` seat, null today), `spawn_guard`'s ack + the `spawnEconomy.guard`
   kill-switch idiom. **Defer VOC/Δm** (SIMP-3, A4): no quality oracle exists; the accumulator alone
   stops the bleed; VOC is v2 once the ledger accrues outcome data. Our manuscript's Δm IS the VOC the
   theory names (E13) — but WIDTH-scoped; applying to a sequential hop is `[judgment]`.

## Portfolio (Phase 5 buckets)

| Bucket | Items |
|---|---|
| **núcleo** (staged) | P0 fix the per-hop cost-loss bug · P1 measure probe + honest ledger (Brief A) · P2 the fused control (Brief B+C+D) |
| **contingência / ops rider** | atomic/lock-free accumulator · bulkhead pool · staged rollout · track TOKENS too · sample telemetry |
| **experimentos** | EXP-BDG-cost: two-phase (measure leak → measure control), hard non-starving abandon criteria |
| **aposta-de-fronteira** (park + trigger) | F1 dose-escalation cohort (correlated storm) · F2 surge-priced VOC · F3 decision-inbox re-authorization · F4 trust-boundary re-auth at the hop |
| **estacionadas** | continuous cost dashboard/alerting (R6 — alerts too slow, E7); a standalone VOC quality oracle |
| **rejeitadas** | a per-TASK retry-count cap ALONE (SIMP-1: cost cap subsumes it; A2: N workers hopping once each = N frontier hops, zero per-task violation — misses D033); a $-alert as the control (E7 too slow) |

---

## P0 — Fix the per-hop cost-loss bug  [PREREQUISITE; without it all measurement lies]

**Verified bug (overseer read `async_runtime.py:505-599`).** Each hop computes its real `observedUsage`
(:513-516), but on failover the current invocation `return await workflow_async_run_one_worker(...)`
(:585) BEFORE the `task.update({"run": run_payload})` finalize (:588) — so an intermediate hop's
`observedUsage` is DISCARDED, and the `worker_failover` event (:583-584) carries only `{from,to,card,
reason}`, no cost. **Only the LAST (non-failing-over) hop's cost ever reaches disk** — multi-hop chains
undercount exactly when leakage is worst (Sonnet REL-5).
**Fix (minimal).** Inject the current hop's cost into the `worker_failover` event at :583 BEFORE the
recursion: add `costUsd`/`observedUsage` (from `run_payload.get("observedUsage")`, or `—` when the
vendor isn't stream-json) + `cardTier: card_tier(ROOT, nxt["card"])`. The async-events JSONL becomes the
durable per-hop cost record the probe reads. (Fuller alt: thread a `hop_usage` accumulator alongside
`failover_history` at :580 into the final `run_payload["cumulativeUsage"]` — reuses the exact pattern
`failover_history` already uses. Pick one; the event-injection is smaller.)
**Footprint.** `scripts/harness_lib/async_runtime.py` — the event dict at :583 (+ maybe the :580 thread).
**Honesty.** Real observed $ or `—`, never a zeroed/guessed number (measure-honesty). **Novelty** baixa ·
**Maturity** conceitual (bug verified, fix unwritten). **Descends from** REL-5, D033.

## P1 — Failover-cost measure probe + honest ledger (Brief A)  [ship gate-OFF; = the control at budget=∞]

**Goal.** Measure the REAL frontier $ that failover leaks, graded vs a noise floor, before anything gates.
**Mechanism.** (a) a sibling probe `testing/probes/exp_failover_leakage_probe.py` (same contract as
`noise_floor_probe.py` — deterministic, zero-LLM, stdlib): read every workflow's async-events JSONL, sum
per-group frontier `costUsd` from the P0-enriched `worker_failover` events, and report `unknownHopCount/
totalHopCount` COVERAGE alongside the $ — never the $ alone (REL-1/REL-2). **Noise floor** = frontier $
in workflows with EMPTY `failoverHistory` (frontier spent on purpose), reusing EXP-15's matched-budget
corpus as the pinned control (like `noise_floor_probe` Floor B). (b) optionally a `failover-hop` record
kind in `cost_metrics.py` (mirror the 4 existing kinds + the `GATE_RECORDS_MAX` per-kind trim; `summarize`
reports "$X observed over N/M hops", never a false total — REL-2).
**Footprint.** new `testing/probes/exp_failover_leakage_probe.py`; optional `cost_metrics.py` new kind.
Read-only, OUTSIDE the control loop (a probe bug can't block a spawn). **Depends on** P0. **Novelty** baixa
· **Maturity** protótipo (the sibling pattern is shipped). **Descends from** REL-1/REL-2, A3, 005-E, D008.

## P2 — The fused failover-cost control (Brief B+C+D fused)  [warn → block; the core]

**Goal.** Stop a cheap-planned group from cumulatively running up an unapproved frontier bill via
failover — without starving legit transient retries or deliberate escalation.
**Mechanism (Sonnet REL-3, the fusion of both v4 candidates D033 names).** A synchronous check at
`async_runtime.py:571` (right before the failover branch builds `new_cmd`) — reuse the circuit-breaker
state machine template, keyed by `(workflowId, role)`. Config `.harness/project.json →
spawnEconomy.failoverGuard` = `block|warn|off` (same enum as `spawnEconomy.guard`, default **warn**):
- **off**: no-op, byte-identical to today.
- **warn**: always allows, emits `worker_failover_warned` with the P0 cost fields — a full observability
  phase before anything blocks (this IS Brief A running live).
- **block**, two checks IN ORDER:
  1. **FIRST, unconditional per-worker hop floor:** `hops_so_far ≥ maxHopsPerWorker` (default 2) → this
     alone bounds one runaway worker's OWN chain and NEVER needs the group signal, so a transient 1-2-hop
     retry is structurally EXEMPT (answers J4/E15 starvation).
  2. **SECOND, group cumulative OBSERVED $ ceiling, gated by a COVERAGE floor:** if the group's observed
     frontier $ (from P1's ledger) exceeds the ceiling AND observed-coverage ≥ (e.g.) 50% → refuse.
     **Below the coverage floor → FAIL OPEN** (the denominator-collapse answer, E15). On a deny, DOWNGRADE
     down the tiered ladder (frontier → mid-tier → cheap → fail, 005-D) via the chain's existing
     skip-to-next-cheaper-entry (A1) — not a hard fail.
- **Fail-open on internal error** (copies `guard_spawn`'s try/except): a guard bug can't cause an outage.
  Every denial names the actual number (hop count, or $ + coverage%) or `—`, never a bare "denied".
**Footprint.** `async_runtime.py` (the guard call at :571 + the downgrade path); a small
`spawn_guard`-style `guard_failover(...)` helper (leaf, reuses `card_tier`); `project.json`
`spawnEconomy.failoverGuard`. **Depends on** P0 + P1 (needs real per-hop cost + the ledger). **Novelty**
média (coverage-gated group budget fused with an unconditional per-hop floor is a genuine new shape from
proven primitives) · **Maturity** conceitual. **Descends from** REL-3, SIMP-1/2/4, R2/R5, C4, 005-A/D/F,
E5-E11, D033. Kill-switch = `failoverGuard:off` (E15/Stripe).

## Ops-hardening rider (fold into P2 as it ships)

- **Atomic/lock-free accumulator** — N parallel failovers hit N concurrent checks; a naive lock
  serializes exactly under stress. Use an atomic CAS counter + **hysteresis** (80% → downgrade-all,
  100% → refuse) to prevent flapping (PERF-01).
- **Bulkhead** — a separate provider-concurrency pool for failover spawns vs plan-time spawns, so a
  failover storm can't starve plan-time work and re-trigger more failovers (the positive feedback
  loop) (PERF-05, C6 Little's-Law sizing from `cost_metrics` medians).
- **Track TOKENS too, not just $** — TPM rate-limit cascades independently of $, and token volume is a
  data-egress proxy (PERF-02, IC-2).
- **Staged rollout** — measure (warn) → validate accumulator under parallelism → enable block at a
  conservative ceiling (2× observed P99), each stage gated on an SLO (PERF-06, REL-4 Phase B).

## Experiment — EXP: two-phase (register per methods library)

**Phase A (measure-only, buildable now, D008):** hypothesis "SPEC-115 failover hops move a measurable
share of frontier $ outside any width>1 guard, beyond the matched-budget noise floor"; baseline =
EXP-15 corpus restricted to empty-`failoverHistory` workflows (noise floor); metric = P1's per-group
observed $ + mandatory COVERAGE (unknown/total hops); decision = leakage (coverage ≥50%) clears the
floor on ≥N workflows → proceed; else park + keep the probe running. **Phase B (control's effect,
owner-gated):** hypothesis "`failoverGuard=block` cuts observed frontier-failover $ per group WITHOUT
raising the blocked-rate for ≤2-hop chains"; metrics = $ before/after + **blocked-rate for
hops≤maxHops (must stay ~0 — any nonzero = starvation)** + group completion-rate (non-inferiority
margin). Abandon `block`-as-default on ANY transient-retry block or a completion regression. Methods:
matched-budget + noise-floor + non-inferiority + confidence-sequences. (REL-4.)

## Frontier bets (park with a trigger)

- **F1 — Dose-escalation canary cohort** (Sonnet C3, 3+3 oncology). The storm is CORRELATED (N workers
  hitting the SAME rate-limit event); admit a small cohort onto the frontier tier, HOLD the rest until
  the cohort's outcome is observed, then open or deny. A SEQUENCING mechanism no capacity ceiling can
  express. Novelty ALTA / maturity conceitual — needs a cohort-rendezvous the async scheduler lacks.
  **Trigger:** P1 data shows failover storms are frequently correlated (many workers, same reason, near-
  simultaneous) AND the P2 per-group ceiling proves too coarse (blocks the whole group at once).
- **F2 — Surge-priced VOC threshold** (Sonnet C2). Make the escalation bar a function of group budget
  utilization (`base/(1-util)`) — graceful vs a cliff. Novelty ALTA / conceitual — needs a LIVE mid-run
  cost signal (P1 gives per-hop; live cumulative is more). **Trigger:** VOC (v2) is picked up + P1 wires
  live cumulative cost.
- **F3 — Decision-inbox re-authorization** (Sonnet C5, reinsurance reinstatement). On ceiling breach,
  route a re-auth request to the EXISTING `decision_inbox` (async human ack) instead of a silent
  default — an auditable, SLO-tracked decision row. Novelty ALTA / conceitual. **Trigger:** owners want a
  renewable ceiling (not a hard cap) with an audit trail.
- **F4 — Trust-boundary re-auth at the hop** (NVIDIA IC-1/CC-2). NEW security angle: failover onto a
  different card silently expands the DATA-exposure surface (retention/jurisdiction) without re-auth.
  Gate the hop on a data-handling-scope re-check, not just cost. Novelty média / conceitual.
  **Trigger:** a threat-model review flags cross-card data-surface as in scope (owner-gated, security).

## Traceability matrix

| Evidência | Problema (JTBD) | Ideia (cards) | Experimento | Plano | Status |
|---|---|---|---|---|---|
| REL-5 + `async_runtime.py:505-599` (read) | measurement lies on multi-hop | REL-5 | — | P0 | plano (bug verified) |
| E7/E14, D008, EXP-15 | J2 measure the leak | REL-1/2, A3, 005-E, SIMP-2 | Phase A | P1 | plano |
| E5-E11, E6, D033 | J1/J3/J4 govern the cost | REL-3, R2/R5, C4, 005-A/D/F, SIMP-1/4 | Phase B | P2 | plano |
| PERF-01/02/05/06, C6, IC-2 | scale/ops | ops rider | Phase B SLOs | P2 rider | plano |
| C3/C2/C5/IC-1 | frontier | F1-F4 | (park) | F1-F4 | estacionado |

## Sequencing

`P0 (fix the cost-loss bug) FIRST` — else P1/P2 undercount. `P1 (measure, gate-off)` needs P0. `P2 (the
fused control)` needs P0+P1 (real cost + ledger) and ships **warn-first**, `block` only after Phase A
supports it + Phase B clears the non-starving abandon criteria. Frontier F1-F4 park behind their triggers.
The whole thing is one mechanism (SIMP-2): P1 is P2 at `budget=∞`/gate-off.
