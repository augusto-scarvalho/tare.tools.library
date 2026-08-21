# Round R5 — EXP-20: 3-Lane Comparison of Harness Fork-Join vs Native Codex (Design)

Round 5 of 5 (D012, NVIDIA, sequential, backlog-first). FINAL round. Produces the EXP-20 pre-registration (does not run the experiment). Phase-2 human gate pre-approved.

## Phase 0 — Question, criteria, budget, breadth, design

- **Question:** does NATIVE Codex fork-join (bet D, proven by EXP-19) deliver different quality/cost from harness fork-join on the SAME task class under a matched budget? And does the ranking reverse between the normalized lane (harness-mediated) and native lane (article H31)?
- **Context (from the repo):** EXP-19 proved the machinery (native `spawn_agent` under `codex exec`, underscore names, consolidated result). C13/L9 provides the pinned route tuple. L13 provides the noise floor. The 5 containment primitives (R2) and matched-budget method (EXP-15) are prerequisites for a FAIR test.
- **Criteria:** design must (a) use 3 lanes with NO pooling (`normalized-core / native-worker / governed-hybrid` — §8.4/§9.4-t); (b) use a real matched budget (same snapshot, same token budget — not effort label, C13); (c) use split-plot with vendor/snapshot as whole-plot (expensive switch) and per-task knobs as sub-plot; (d) include a metric that separates quality from ranking-reversal cost; (e) use L13 noise floor as threshold — delta < cross-WF spread = non-evidence.
- **Breadth (D010): FOCUSED-2** — the target is one defined experimental design, not exploration; 2 workers: B1 statistical design (lanes, split-plot, matched-budget, what to pin), B2 instrumentation (which harness seams measure each lane; where native Codex does not expose data and what is an honest proxy). Each worker's Δ_m = its half.
- **Budget:** single wave ≤ 30k. Executor `nvidia-compat`. Override expected.
- **Declared design (L18):** `Matched-budget controls` + `Split-plot` cards from `EXPERIMENT_METHODS.md` are the method; EXP-20 will be registered `status: proposed` citing both cards. Measurement remains OWNER-GATED (if promoted it changes core reduce — SPEC-116 door).

## Execution

Wave: `WF-20260718-223240-760885` (2 workers by construction, GLM, 2/2 valid, 10 design pieces). Coherent and complete design — registered as EXP-20 (`status: proposed`).

## Pre-registered EXP-20 design (3 lanes, split-plot, matched-budget)

**Lanes (never pooled — §8.4):**
1. `normalized-core` — both vendors through the harness normalized worker contract.
2. `native-worker` — harness fork-join vs native Codex `spawn_agent`.
3. `governed-hybrid` — harness orchestrates, delegates to native workers.
Ranking inversion between lanes 1 and 2 = evidence of model×harness interaction (H31), not measurement error.

**Factors (split-plot — Split-plot card):**
- Whole-plot (expensive switch, batch before changing): vendor, modelSnapshot, adapterVersion.
- Sub-plot (cheap, randomize within block): topology (1-worker control vs 3 vs 5), contextPolicy.
- Two error strata, analyzed separately — never pooled.

**Matched-budget (Matched-budget controls card):** budget = sum of OBSERVED provider-native tokens (not planned/estimated, not effort label — H30); same `modelSnapshot` in all lanes. 1-worker control = EXP-15 arm.

**Instrumentation (real seams):**
- Quality oracle: deterministic stdlib checker (diff/parse/compile) on each lane's final artifact; for native lane, score the parent's consolidated result.
- Provider-native tokens: `token-audit` per worker in lanes 1 and 3; lane 2 (native Codex) = **parent-delta proxy labeled EMULATED, never pooled** with real measurement (native/emulated §8.4 discipline — connects to C3/C16b).
- Ranking stability: Kendall tau of per-scenario scores within each lane; abandon if tau variance across the 5 frozen WFs > Floor B (L13).
- Frozen task class: pinned route tuple (same `modelSnapshot`) + deterministic stdlib scenarios (parse/transform/compile).

**Honest gap (§8.4 emulated):** native Codex does NOT expose per-subagent token accounting → every per-subagent number in lane 2 is EMULATED (formula: parent-process total divided) with declared uncertainty; gap table `{metric, lane1-seam, lane2-proxy, lane3-seam}` per metric.

**Threshold (L13):** both floors measured BEFORE comparison, on the same frozen task set; effect < cross-WF spread = unresolved.

## Registry

EXP-20 registered `status: proposed` (measurement OWNER-GATED — changing default topology/reduce is a SPEC-116 door). Cites Matched-budget + Split-plot cards. Activation and execution remain queued until the owner opens implementation.
