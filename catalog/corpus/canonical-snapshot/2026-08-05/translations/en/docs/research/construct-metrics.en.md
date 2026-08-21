# Round R4 — Construct Metrics (Pre-registered Definitions + Probes)

Round 4 of 5 (D012, NVIDIA, sequential, backlog-first). Phase-2 human gate pre-approved by D012.

## Phase 0 — Question, criteria, budget, breadth, design

- **Question:** which constructs from the article (§3.5, §5.7, §6.2, §9.5) that we still DO NOT measure can become deterministic measure-only probes over state we already have, and what is the pre-registered definition of each (formula, corpus, what counts as signal vs noise)?
- **Targets (from backlog):** route churn (§3.5, prerequisite for C9 hysteresis); CTS (§9.5-b, nearly free from the delegation ledger — already has brief C6); Π-lite (§3.5, depends on noise floor L13 ✅ + trace completeness L4 ✅); recovery metrics (§5.7: duplicate-effect, orphaned work, time-to-resume); context precision/recall and used-context ratio (§6.2).
- **Criteria:** every metric must include (a) formula, (b) corpus/seam available in the repository today, (c) noise definition (delta < floor = non-evidence, rule L13), (d) verdict: measure-only vs needs-new-state. No enforcement.
- **Breadth (D010): FOCUSED-3** — the topic is defined (named metrics), not open exploration; 3 partitioned workers: B1 routing (churn/regret/calibration), B2 recovery+effects (§5.7), B3 context+economics (§6.2/§3.5 + Π-lite). Each worker's Δ_m = its slice.
- **Budget:** single wave ≤ 40k. Executor `nvidia-compat`. Override expected.
- **Design (L18):** produces PRE-REGISTERED DEFINITIONS + probe designs. Every future probe that becomes an EXP cites the methods card at that time (noise floor for spreads; matched-budget for comparisons). No measurement is run in this round — the measurements are designed here.

## Execution

Wave: `WF-20260718-222420-548481` (3 workers by construction, GLM, 3/3 valid after 2 re-dispatches — global breaker reopened due to inheritance from a previous critique failure; lesson: reset/wait for breaker between rounds). 15 metrics designed.

## Synthesis — construct metrics (measure-only vs needs-new-state)

Verdict per metric, audited against the real seams. **measure-only-today** = all inputs exist → deterministic committable probe now. **needs-new-state** = a named field/denominator is missing.

| metric | ref | verdict | formula (summary) | corpus | missing (if needs-new-state) |
|---|---|---|---|---|---|
| **CTS** | §9.5-b | ✅ measure-only | Σ estTokens ÷ count(outcome=kept); +byModel | delegation ledger | — (confirms brief C6 is buildable) |
| **route churn** | §3.5 | ✅ measure-only | count(chosenRoute_i≠_{i-1} without new evidence) ÷ count(demandId) | route ledger L7 | — (spread judged by Floor B/L13) |
| **Π-lite** | §3.5 | ✅ measure-only | ⟨1−viol, 1−overrun, 1−replay_div, recovery, 1−unknown⟩ | route ledger + cost + replay-class L3 | — (average must not compensate for a critical violation) |
| **ctx precision** | §6.2 | ✅ measure-only | presented objects linked to usage ÷ presented objects | E1 context-digest | — |
| **used-context ratio** | §6.2 | ✅ measure-only | objects linked by typed relation ÷ presented objects | E1 context-digest | — |
| **orphaned work** | §5.7 | ✅ measure-only | workers with no terminal transition | records ledger lifecycle | — |
| **provenance continuity** | §5.7 | ✅ measure-only | causal chain intact after recovery | records + replay-class | — |
| **recovery-point error** | §5.7 | ✅ measure-only | deviation of recovered state vs last-good | records + gate results | — |
| **time-to-resume** | §5.7 | ✅ measure-only | latency until work resumes post-crash | records lifecycle | — |
| route regret | §9.5-a | 🔬 needs-new-state | U(best retrospective route) − U(chosen) | route ledger | **U(route,outcome,cost) function** + retrospective calculation — owner decision about U |
| routing calibration/ECE | §9.5 | 🔬 needs-new-state | Σ_bins \|pred − realized\| | route ledger | **predictedP field** per route decision (router emits no confidence) |
| ctx recall | §6.2 | 🔬 needs-new-state | required evidence retrieved ÷ required | E1 digest | **gold "required" set** per decision |
| A_ctx | §6.2 | 🔬 needs-new-state | presented tokens ÷ unique logical tokens | cost_metrics (numerator) | **"unique logical tokens" denominator** (already deferred in memory round) |
| duplicate-effect rate | §5.7 | 🔬 needs-new-state | duplicated external effects ÷ effects | records | **effect-id/idempotency-key** in records (external effects are rare today) |
| compensation outcome | §5.7 | 🔬 needs-new-state | exact/business-eq/partial/impossible class | records | **compensation records** (no saga today) |

### Findings that close loops
1. **CTS confirmed buildable NOW** — brief LQ7-C6 was correct; this round provides the pre-registered formula (denominator = outcome kept; byModel variant).
2. **route churn is the measurable prerequisite for C9 hysteresis** — buildable now; backlog said "measure before controlling", and now there is a formula + Floor L13 as noise ruler. C9 (route-loop cooldown) only after this measurement.
3. **Π-lite is the predictability profile from §3.5** — buildable, and the rule "high average does not compensate for one critical violation" follows the same spirit as the lexicographic rule (brief C1). They fit together.
4. The five needs-new-state items cluster into: 2 router items (U + predictedP — one owner decision about utility function unlocks regret+ECE together); 2 external-effect items (effect-id + compensation — relevant only when external effects grow); 1 A_ctx item already deferred behind a trigger.
