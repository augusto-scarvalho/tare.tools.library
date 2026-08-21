# Research round — gate Phase-2 safety theory (safe-skip, default-flip, cleanliness contract)

Opened 2026-07-20 by the audit session (owner directive: "tudo que precisar de refinamento
teórico/experimentação ainda não ideada, faça um research usando nvidia"). Double Diamond
per `.harness/prompts/research-playbook.md`.

## Question

The 2026-07-20 audit shipped the mechanical fixes (SCENARIO-SKIP protocol, hold-set
symmetry, guard teeth) but left three THEORY gaps that gate the Phase-2 wins:

1. **SPEC-159 safe-skip enablement** — under what conditions is skipping a cached,
   unaffected scenario PROVABLY safe? Sub-questions: verdict-cache semantics after
   skip≠pass (a LIVE falseSkip happened today: rt6's 0.4s self-skips were cached as
   passes for 10 runs, then its first real in-gate run failed — the shadow caught it);
   the enablement rule (falseSkip==0 over N runs — what N, with what statistical
   backing? what events must INVALIDATE the accumulated evidence?); and modeling the
   import-graph's subprocess blind spot beyond the `_GLOBAL_TRIGGERS` allowlist floor.
2. **SPEC-160 default-flip equivalence** — what protocol PROVES parallel == serial
   over the real 150-scenario battery (not the pure-orchestration fixture)? What must
   a HEAD-faithful worker copy contain (.git, HEAD .harness state) and how is
   faithfulness itself verified? Under what conditions can the SPEC-159 shadow be
   re-included in the worker path (today: deliberately excluded — copy-divergent
   verdicts must never feed the cache)?
3. **Scenario↔gate-isolation cleanliness contract (the rt6 class)** — what contract
   may a scenario that drives the REAL machinery assume about harness-regenerated
   docs inside the hold? Today rt6 hardcodes a `_REGEN` exclusion set; the writer set
   is discovered by archaeology, not declared by the harness.

## Success criteria

- Each brief yields decision-ready options with named invalidation/failure conditions,
  not "do X": an enablement RULE for (1), a verifiable PROTOCOL for (2), a stated
  CONTRACT for (3).
- Every normative claim: `claim → source + date + confidence`; unverifiable → `judgment`.
- Novelty and maturity scored separately (playbook principle 2).
- Output feeds: EXP registration for (1)/(2) thresholds, backlog rows, and possibly a
  SPEC-116 amendment for (3).

## Declared budget & width (D010)

- **Budget:** 1 divergence wave on NVIDIA free-tier (`nvidia-compat`, credit cost ~0;
  declared ceiling ~70k est tokens incl. shared digest) + 1 agent-reduce. Critique wave
  only if the reduce shows contradictory or high-risk concepts (budget gate 60%).
- **Width: 4, mode custom.** Focused-to-in-between per D010: the three sub-themes are
  coupled (all are "when is a gate shortcut trustworthy"), a defined feature set exists
  (SPEC-159/160 Phase 2), but the safety-proof space is genuinely open. One perspective
  per theme + one adversarial/cross-domain lens; EXP-15's over-fanning failure mode
  (5 workers, same 5 ideas) is the reason this is 4 and not 5.

## Declared experiment design (L18)

The round feeds measurable claims (enablement thresholds), so per L18:
- Safe-skip enablement (falseSkip==0 over N runs) → **Confidence sequences** card
  (`docs/EXPERIMENT_METHODS.md` §Confidence sequences): anytime-valid monitoring fits
  "keep watching shadow runs until the bound clears"; plus **Noise floor** (a falseSkip
  caused by scenario flakiness, not cache wrongness, must not count against the cache —
  today's rt6 event is exactly a non-cache-fault falseSkip).
- Default-flip equivalence → **Non-inferiority** card (parallel must be proven
  not-worse than serial within a stated margin, sustained) + **Matched-budget controls**
  (same battery, same order, paired runs).
- Cleanliness contract → no experiment; a design decision (SPEC-116 exit).

## Phase 1 evidence (register)

Prior art is largely in-repo (Flow B); the 2026-07-20 WF round already verified the
external corpus this builds on.

| claim | source | type | year | method | limitations | confidence | maturity |
|---|---|---|---|---|---|---|---|
| [repo] Test-impact selection with conservative fallbacks (FB-0..4, every doubt runs) shipped shadow-only; falseSkip detector is the safety proof mechanism | `scripts/harness_lib/gate_affected.py`; `specs/40-features/gate-affected-cache.md` | repo | 2026 | code + spec | Phase 1 only; subprocess blind spot floored by `_GLOBAL_TRIGGERS` | forte | protótipo |
| [repo] A REAL falseSkip occurred: skip-recorded-as-pass poisoned the cache (rt6, 10 runs at 0.4s), first real run failed, shadow SHOUTED | gate-perf.jsonl rows 2026-07-19..20; audit session 2026-07-20 | measurement | 2026 | ledger forensics | single event; root cause (skip≠pass) FIXED in the audit batch | forte | validado |
| [repo] Ekstazi/pytest-testmon/Bazel/TAP external evidence for dependency-based test selection + its false-negative risk | `docs/research/loop-workflow-efficiency-evidence.md` | repo(digest of web) | 2026 | prior round, primary sources | web rows verified in that round, not re-fetched here | moderada | produção (external) |
| [repo] Parallel worker copies omit .git + HEAD .harness state; divergence documented; equivalence proven only for pure orchestration (gps) | `scripts/harness_lib/gate_parallel.py` docstring; `specs/40-features/parallel-scenarios.md` | repo | 2026 | code + spec | real-battery equivalence unmeasured | forte | protótipo |
| [repo] The hold-set asymmetry class: regenerated docs (handoff/context) written mid-gate from live state | audit session 2026-07-20 (fix A′: scenario_isolation.py `_targets`) | measurement | 2026 | reproduced replica (1/5→5/5) | writer set discovered by archaeology; no declared registry | forte | validado |
| Anytime-valid inference (confidence sequences) suits sequential "watch until safe" monitoring | `docs/EXPERIMENT_METHODS.md` §Confidence sequences | repo(methods) | 2026 | methods card | applied here by analogy | moderada | validado (method) |

## Phase 2 — briefs (problem-framed)

- **B1 (safe-skip):** "How does the gate KNOW a skip cannot ship a false green?"
  Actors: gate, verdict cache, owner. Constraints: never false-green; skip evidence must
  be invalidated by the right events (gate-version bump, graph rebuild, scenario flake,
  cache-key scheme change); the subprocess blind spot must be modeled, not assumed away.
- **B2 (default-flip proof):** "How do we PROVE the parallel battery is the same gate?"
  Actors: gate, worker copies, owner. Constraints: proof over the REAL battery;
  copy faithfulness verifiable; shadow re-inclusion must not poison the cache.
- **B3 (cleanliness contract):** "What may a machinery-driving scenario assume about
  harness writes during the gate?" Actors: scenarios, isolation layer, harness writers.
  Constraints: no per-scenario archaeology; contract enforceable/testable.

Human gate: the owner pre-authorized this round explicitly ("pode atacar tudo…faça um
research usando nvidia", 2026-07-20); proceeding to one divergence wave.

## Phase 3 — divergence wave (ran 2026-07-20)

`WF-20260720-175712-339749`, fork-join, research-divergence, 4 ideators on
`nvidia-compat`, shared digest (per-worker required-reads 13,871 → 4,893 tokens;
wave 19,572 + packets ≈ 21.7k est, inside the 70k ceiling; free-tier credit cost ~0).

**Wave health (recorded honestly):** 2/4 ideators VALID (simplicidade, performance/
escala). ideator-reliability and ideator-trust-boundary were REJECTED by the result
contract — twice each (initial + one retry): findings at severity high/blocker without
`sourceFilesVerified` (a text-only HTTP worker cannot verify files), and the
trust-boundary draft additionally withheld by the pre-egress secret scan (it wrote
literal `sk-…` example keys; the P5 guard fired correctly). Same failure class as the
2026-07-20 WF round's worker-004. Rejected drafts are NOT cited below (anti-fabrication:
rejected = out). Systemic fix promoted as a backlog row (`wf-research-packet-severity-cap`).
An initially suspected validation race (result files present but classified failed) was
investigated and REFUTED — the classifications were contract-correct.

Agent-reduce (adopted): 6 concepts, 4 explicit conflicts — every conflict is the same
axis: worker-001's deterministic/lighter design vs worker-002's statistical/layered
design for the same sub-problem.

## Phase 4 — operations per concept (set-based)

| Concept | Genealogy | Operation | Rationale |
|---|---|---|---|
| C1 Deterministic skip invariant: skip ⇔ cached non-skip verdict AND zero invalidation events since (exhaustive enumerated set: gate-version bump, graph rebuild, closure-blob change, observed flake for that scenario, key-scheme change) | w1-THEME1 | **mantida (núcleo)** | The skip CONDITION must be deterministic — a probabilistic condition can ship a false green by construction |
| C2 Statistical enablement (N≥20 window, confidence sequences / always-valid bounds; bounded shard concurrency during evidence accumulation) | w2-P1 | **experimento (EXP-29)** | Resolves CONFLICT-001 set-based: C1 is the runtime condition, C2 is the EVIDENCE BAR for turning Phase 2 on; noise floor excludes flake-caused falseSkips (today's rt6 event is the worked example) |
| C3 Subprocess blind spot: static AST subprocess-edge extraction feeding a DECLARED edges manifest; an undeclared subprocess call ⇒ scenario stays affected (fail-to-run, never fail-the-gate) | w1-THEME1b + w2-P3 | **combinada** | Static tier is cheap and auditable; `_GLOBAL_TRIGGERS` stays as the floor; dynamic tracing tier estacionada (cost unproven) |
| C4 Equivalence protocol: K≥3 paired serial‖parallel full-battery runs; ACCEPTANCE = verdict-map exact equality outside a declared flake-quarantine; durations advisory; verdict-vector hash as the comparison primitive | w1-THEME2 + w2-P2 | **experimento (EXP-30), simplificada** | Duration equality dropped from acceptance (noise); hash primitive kept for cheap comparison |
| C5 HEAD-faithful copy + attestation: content-hash manifest (tracked files + HEAD .harness state + gate version) computed at fork = faithfulnessRoot; every worker copy must reproduce it; SPEC-159 shadow re-inclusion ONLY behind attestation + a copy-fidelity component in the cache key | w2-P2/P5 | **mantida** | Faithfulness becomes verifiable instead of assumed; keys copy-run verdicts separately so they can never poison live-cache entries |
| C6 regen-manifest contract: harness publishes `regen-manifest.json` (every path it regenerates); scenarios import it (rt6's hardcoded `_REGEN` dies); a gate check diffs ACTUAL gate-run writes vs the manifest both ways | w1-THEME3 + w2-P4 (2/2 convergence) | **mantida (núcleo)** | Replaces archaeology with a declared, tested contract; the audit's fix A′ exclusion set becomes one import |
| Cross-theme `gate-state.json` unification (single manifest for all three) | w1-cross | **estacionada** | Unify only if the three stores measurably rot apart — premature coupling today (ponytail) |
| Write-suppression inside scenarios (alternative for THEME 3) | w2-P4 alt | **rejeitada** | Runtime magic; the manifest + isolation targets already close the leak |

## Phase 5 — portfolio & delivery

- **núcleo:** C1 (skip invariant), C6 (regen manifest → row `wf-regen-manifest`)
- **contingência:** `_GLOBAL_TRIGGERS` floor stays if C3's extraction underdelivers
- **experimentos:** EXP-29 (safe-skip enablement bound), EXP-30 (default-flip equivalence) — registered 2026-07-20, status proposed
- **estacionadas:** dynamic subprocess tracing tier; gate-state unification
- **rejeitadas:** write-suppression; statistics-as-skip-condition (either extreme alone)

Backlog rows promoted (WF table): `wf-regen-manifest` (C6), `wf-subprocess-edges` (C3),
`wf-research-packet-severity-cap` (wave-health fix); `wf-gate-cache-enable-skip` and
`wf-parallel-default-flip` augmented with EXP-29/EXP-30 as their evidence bars.
Decisions appended to `.harness/context/DECISIONS.md` (D-entries with trade-offs).

## Traceability

| Evidência | Problema | Ideia | Experimento/ADR | Spec | Task | Status |
|---|---|---|---|---|---|---|
| falseSkip real 2026-07-20 (gate-perf.jsonl) + FB-0..4 | quando skip é seguro | C1+C2 | EXP-29 | SPEC-159 (fase 2 amendment futura) | wf-gate-cache-enable-skip | owner-gated, evidence bar declarada |
| subprocess blind spot (`_GLOBAL_TRIGGERS`) | TIA além do floor | C3 | — | amendment futuro | wf-subprocess-edges | promovida |
| gps fixture-only equivalence; copy omite .git/HEAD | prova do flip | C4+C5 | EXP-30 | SPEC-160 (amendment futuro) | wf-parallel-default-flip | owner-gated, protocolo declarado |
| fix A′ + `_REGEN` hardcoded (audit 2026-07-20) | contrato de limpeza | C6 | — | SPEC-116 door NEW ao construir | wf-regen-manifest | promovida |
| 2×2 rejeições de contrato (esta wave + round anterior) | saúde das waves NVIDIA | severity cap no packet | — | — | wf-research-packet-severity-cap | promovida |
