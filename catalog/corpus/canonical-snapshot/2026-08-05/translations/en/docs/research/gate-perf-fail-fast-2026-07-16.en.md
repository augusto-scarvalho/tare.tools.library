# Round: Test/Gate Engine Performance + Fail-Fast (2026-07-16)

Owner ask (intake via prompt hook 2026-07-16): review test code and the engine that runs it; friction/slowness; where C++/PyO3/Rust is worth it at fixed hot spots; automated suggestions escalated as decisions based on metrics; mocks that are sufficient vs insufficient; specs+BDD that are too generic; classical fail-fast techniques (fast tests first, failure-prone tests first). Also valid for harness target repositories, but CONTAINED/SEPARATE (metrics and decisions do not mix).

## Question

How can we reduce time-to-first-failure and total SPEC-137 gate time (currently 7–10 min) without losing hermeticity, anti-flake retry, or full-suite completeness — and how can we turn this performance vigilance into an automated routine (metric → suggestion → decision), replicated in isolation for target repositories?

## Success criteria

- Completeness preserved: commit gate continues to run ALL scenarios (owner constraint: "do not stop running our tests in full" — predictive selection that SKIPS tests can only appear as an opt-in inner-loop layer, never in the commit gate).
- Hermeticity preserved: snapshot/restore per scenario and retry-once remain guaranteed (they were the flakiness fix — project memory).
- Time-to-first-failure (TTFF) falls from "alphabetical position" to early minutes.
- Any skipping/reordering is deterministic and auditable (no opaque ML in v1).
- Harness × target-repo metrics separated (gate already tags `subject: self` vs target — use that seam).
- Every proposal becomes a registered experiment (EXP-N, `docs/EXPERIMENT_METHODOLOGY.md`) with baseline, metric, and decision criterion BEFORE becoming default.

## Declared budget (owner rule: waves only on cheap models)

- Wave executors: `nvidia-compat` (`glm-5.2` primary, `step-3.7-flash` cheap) and `gemini-compat` (`gemini-2.5-flash-lite`). NO Claude/Codex waves.
- At most 1 divergence wave (5 ideators) + 1 critique wave (4 critics); `workflow token-audit` before each start; round ceiling ≈150k calibrated tokens (chars/3.1). Budget gate at 60%.
- Bulk-reading grunt work: `harness.py discover` (Gemini→NVIDIA chain), never raw reading by orchestrator.

## Phase 0/1 — Evidence

### Measurements [repo] (source: `.harness/state/cost-metrics.json`, gate records; runner: `scripts/spec_test_gate.py`)

| claim | source | type | confidence |
|---|---|---|---|
| Gate scenarios = 440–595s wall; spec-pack = 9–12s (irrelevant for optimization) | cost-metrics gate records 2026-07-16 | measurement | strong |
| Runner is SERIAL and ALPHABETICAL (`sorted(glob)`), 1 subprocess/scenario, volatile-state snapshot+restore PER scenario, retry-once on failure | `spec_test_gate.py:1546-1565`, `_run_isolated_scenario` | repo | strong |
| Top-5 scenarios ≈35% of wall: `m4_status_html` 59–73s, `worker_live_tail` 33–76s (high variance under load), `rs_research_skill` 26–63s, `cli_registry` 23–27s, `se_self_review` 21–27s | gate records (last 4 rounds) | measurement | strong |
| 128 scenario files, ~550 checks; tail of ~123 scenarios ≈350s ⇒ ~2.8s/scenario average — relevant portion may be fixed overhead (interpreter spawn + snapshot/restore), not assertions | gate records + count; exact split unmeasured | measurement + judgment | moderate |
| `durationMs` per scenario already emitted each round; `cost_metrics.record_gate` already stores top-5 slowest per round (150 records) — ordering and automatic-alert raw material ALREADY EXISTS | `spec_test_gate.py:94-95,1645-1651`; `cost_metrics.py:98` | repo | strong |
| Scenario that recovers in ≥2 of 5 rounds = reopened bug, not noise (owner rule); `worker_live_tail` and `rs_research_skill` are known flake-prone scenarios | intake `583ff705e3ca`; `.harness/runs/scenario-forensics` | repo | strong |
| Harness×target separation already has structural seam: validation-ledger lines use `subject: "self"`; `runs --target` goes through `run_target_gate` with its own stamp | `spec_test_gate.py:1608-1614` | repo | strong |

### Classical techniques [web] (verified 2026-07-16)

| claim | source | year | confidence | maturity |
|---|---|---|---|---|
| Prioritizing test cases "most important first" maximizes early fault detection rate; APFD metric; family of total/additional-coverage techniques | Rothermel/Elbaum, *Test Case Prioritization: A Family of Empirical Studies* (IEEE TSE ~2000–02), digitalcommons.unl.edu | 2002 | strong | production |
| Staged pipeline: fast stage 1 (<10 min) with doubles/mocks for slow services; slow stages later — "every minute shaved from the build is a minute saved per developer per commit" | martinfowler.com/bliki/DeploymentPipeline.html + articles/continuousIntegration.html | 2013/2024 | strong | production |
| Suite parallelization pitfalls = shared mutable state, fixed ports, order dependence; port 0, namespacing per worker, random order to hunt dependencies | pytest-xdist docs + pythoneer.substack.com | 2024–25 | strong | production |
| Predictive selection: Meta catches 99.9% of regressions while running ~33% of tests; Google TAP Transition Prediction cut median detection ~65% (107→37 min) — BUT skips tests, violating our commit-gate completeness | ICSE-SEIP 2019 (mpapad.github.io) + browserstack.com/guide/predictive-test-selection | 2019–25 | moderate | production elsewhere / contingency here |
| PyO3/maturin for fixed Python hot paths is established practice; real gain depends on profile (I/O-bound does not benefit) | reference: judgment (not verified this round; local probe decides) | — | theoretical | prototype |

## Phase 2 — Briefs (HUMAN GATE — approve before any wave)

- **B1 — Time-to-first-failure.** Actor: owner waiting for commit. Problem: alphabetical order ignores duration and failure propensity; failure in `w*` appears only around minute 8. Criterion: expected TTFF <2 min using ONLY data ledger already has (`durationMs` + failure/recovered history). Constraint: full suite always.
- **B2 — Fixed cost per scenario.** Actor: engine. Problem: ~123 "cheap" scenarios cost ~350s, much of it potentially overhead (spawn + snapshot/restore per scenario) rather than assertions. Criterion: cut ≥30% of tail wall without losing isolation; measure real overhead×assert split before optimizing (deterministic probe). Includes: where safe parallelization works (pytest-xdist pitfalls), where Rust/PyO3 pays (only fixed/stable point, no recompiling suite), where a mock is enough (e.g. does `m4_status_html` start a real HTTP server — sufficient or excessive?).
- **B3 — Assertion strength.** Actor: spec reviewer. Problem: overly generic checks (that never fail) create false confidence; insufficient mocks hide real integration. Criterion: inventory never-failed checks × history; evidence-backed tightening proposal per spec/BDD, not vibes.
- **B4 — Automatic performance governance.** Actor: owner (decisions) + harness. Problem: this review was manual ("I am the one initiating the request"). Criterion: deterministic metric→suggestion→decision rule (e.g. gate >X s for N rounds, scenario >Y s, flake ≥2/5 ⇒ item in decisions/intake), with target-repo metrics in separate space (subject tag), zero mixing.

## Phases 3–4 — Waves executed (2026-07-16, 100% `nvidia-compat/glm-5.2`)

- B1: NO wave (owner approval) — direct experiment EXP-11, implemented.
- B2 divergence: `WF-20260716-162149-026669` (5 perspectives, 23 deduped findings; 1 invalid worker; run hit PermissionError WinError 5 on `workflow.json` — Windows lock — and resumed cleanly with a second `workflow run`).
- B3 divergence: `WF-20260716-162849-270831` (never-failed via left join, regex detector for weak assertions, mock-vs-real matrix by class, evidence-anchored BDD, information-per-check via lightweight mutation sampling).
- B4 divergence: `WF-20260716-162857-157371` (post-gate hook, flat rules with cooldown/dedup, ledgers separated by subject AT COLLECTION, advisory-first, never auto-apply; security: env redaction + thresholds as trust surface).
- Critique (seeded B2): `WF-20260716-164059-957736` (4 critics; 2 partial). Decisive findings: overhead premise UNMEASURED (measurement becomes hard prerequisite); in-process runner offers ASSERTED hermeticity vs structural hermeticity of subprocess; fork/CoW invalid on Win32; tier promotion needs data threshold + drift detector; PyO3 only if profile shows >5% wall at chokepoint.

## Phase 5 — Operations by card and portfolio

| Card | Operation | Bucket | Destination |
|---|---|---|---|
| B1 fail-fast ordering | experiment → shelved (v1) → **reopened and shipped (v2)** | core | **EXP-11 v2 shipped** — v1 (−87% replay TTFF) died because clustering heavy-flaky tests knew only 9 durations. Reopen trigger satisfied by EXP-12 (126/126 durations in sidecar): v2 promotes ONLY flaky<10s (19 scenarios), heavy tests keep alphabetical position (spacing preserved). Replay TTFF 201s→24s (−88%); live 3/3 green rounds, identical counts, zero double-fail/recovered. Reversal remains one line |
| B2 overhead×assert measurement | kept (prerequisite for ALL B2 optimization) | experiments | **EXP-12 shipped** — measured in 2 rounds (0.8 p.p. spread): real spawn+boot 0.08s (1.5–2s premise refuted ~20×), snapshot+restore 57s/round (12%), 10 heavy = 240s (51%). Tail 26–27% = gray zone. Consequence: spawn optimization DEPRIORITIZED (ceiling 9–46s), real levers = EXP-13 (m4) and snapshot/restore. NVIDIA critique: warm cache + 2 same-day rounds ≠ definitive death; reopen trigger registered |
| B2 mock `m4_status_html` | premise refuted → **root-cause fix shipped** | core | **EXP-13 shipped** — m4 has NO HTTP server (second false B2 premise). Real cost: `protected_files._glob_matches` performed repo-wide `rglob` PER PATTERN (~44 walks/`compare_snapshot`) in `status --html` drift scan (4 generations × 13s). Fix: 1 pruned traversal, byte-identical parity (58×/call). m4 66–71s→7.3s (9×), `status --html` 13.1s→0.72s, gate ~406s (−60s+). Zero scenario behavior change — no mock, all real e2e. `rs:e2e-smoke` reopened separately (intake `d92c2144d5ab`) |
| B2 in-process runner / pool / batch | deferred | contingency | only if EXP-12 proves overhead ≥40% AND with state-purge audit protocol (critique) |
| B2 fork/CoW batch | rejected | rejected | Win32 has no fork; multiprocessing-spawn gives no CoW |
| B2 `@parallel-safe` parallelization | deferred | parked | depends on EXP-12 + hazard map; classical pitfalls documented |
| B2 PyO3/Rust at chokepoints | parked | parked | majority view: cost>benefit; reopen only if cProfile shows >5% wall at fixed point |
| B3 assertion inventory | combined → **shipped** | core | **EXP-14 shipped** — `tools/check_assert_audit.py` probe (AST call sites + forensics join): 833 checks, 79% strong, 54 weak-shaped ranked. Judgment in Opus 4.8 xhigh wave (4 workers, owner cost rule): 11 tightened assertions in 8 scenarios (notably `workflow:finalized`, rc-only E with historical failure) + ~18 evidence-backed ok-as-is. Phase 2 (spec-pack/BDD) open with reopen trigger |
| B3 BDD/spec tightening | deferred | parked | EXP-14 phase 2 (only worst cases, with evidence) |
| B4 metric→decision governance | kept | core | intake `020dfc7b4e7c` → SPEC-116 (advisory-first) |
| B4 Meta/Google-style predictive selection | rejected (for commit gate) | rejected | violates completeness (owner constraint); revisit only as opt-in inner loop |

## Traceability

Evidence → Problem → Idea → Experiment/Decision:
- cost-metrics 440–595s + serial alphabetical → poor TTFF → fail-fast tiers → EXP-11 (shelved: replay −87% but heavy-test clustering doubled live flakes; methodology worked — abandonment criterion stopped it before default)
- EXP-11 live runs → NEW measurement finding: alphabetical order accidentally spaced resource-heavy scenarios — future reordering must preserve spacing (direct input to EXP-12)
- 2.8s/tail average [unmeasured judgment] → fixed overhead? → critique: measure first → EXP-12
- top-5 slow (m4 59–73s) → unit cost → loopback mock hypothesis → EXP-13
- never-failed checks (suspicion) → assertiveness → deterministic probe → EXP-14
- manual owner request → governance → advisory post-gate hook → intake `020dfc7b4e7c`
- harness×target separation → existing subject tag → separated ledgers at collection (B4 design)

## Status

- [x] Phase 0/1: evidence (local measurements + classical sources)
- [x] Human gate: owner approved direct B1 + B2/B3/B4 waves (2026-07-16)
- [x] Phase 3: 3 divergence waves + [x] Phase 4: 1 critique wave (all NVIDIA)
- [x] Phase 5: EXP-11 active; EXP-12/13/14 proposed; B4 intake; portfolio above
