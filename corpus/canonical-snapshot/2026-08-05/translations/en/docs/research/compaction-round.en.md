# Research Round — Automatic Context Compaction

Owner 2026-07-19: broad research (NVIDIA + Sonnet 5 medium) to define an AUTOMATIC context-compaction mechanism: models/roles, ideal compaction percentage, problems with not compacting / compacting too early / too late, and how to find the sweet spot by model × capacity × task × role. Orchestrator = this session. Cross-vendor divergence.

## What the harness ALREADY has (plumbing, not policy)
- `tools/hooks/reload_context_after_compact.py` — reinjects canonical context after a compact.
- `scripts/harness_lib/context_checkpoint.py` + `docs/CONTEXT_CHECKPOINT.md` — state checkpoint.
- `scripts/harness_lib/context_diet.py` — trims tool schemas for read-only workers (economy).
- EXP-16 (evidence loss) + A_ctx (effective vs declared context) — we already MEASURE evidence loss and effective context (`construct-metrics.md`, `memory-context-management.md`).
- **Missing: the POLICY** — WHEN to auto-compact, WHAT to preserve, and the sweet spot by model/role/task.

## The question
> What AUTOMATIC context-compaction mechanism should the harness implement — one that decides WHEN to compact (the ideal fill % as TRIGGER), WHAT to preserve vs summarize, and how to find the SWEET SPOT by (a) model [declared window + EFFECTIVE processing capacity], (b) role [long-lived overseer / bounded worker / research one-shot / chat], (c) current task [phase, evidence density] — minimizing the costs of NOT compacting, compacting TOO EARLY, and compacting TOO LATE?

## Sub-questions (explicitly requested by owner)
1. **Ideal trigger %:** at what fill fraction should compaction happen? Fixed, or a function of model/role/task?
2. **Problems with NOT compacting:** overflow/truncation, quality degradation ("lost in the middle"), rising per-token cost, quality cliff.
3. **Problems with compacting TOO EARLY:** losing still-needed context, thrash (compact then re-expand), repeated re-summarization cost, evidence loss (EXP-16).
4. **Problems with compacting TOO LATE:** hard truncation, quality cliff, overflow crash.
5. **Sweet spot by dimension:** how to parameterize by model (window + effective A_ctx), role, task.

## Success criteria (harness DNA)
- **Measure-before-control:** sweet spot comes from MEASUREMENT (quality × fill curve, evidence loss), not guessing. Reuse EXP-16 (evidence loss) + A_ctx + L13 noise floor.
- **Deterministic where possible:** trigger is a reproducible rule/measurement; an LLM may summarize, but the DECISION to compact is a computable function.
- **Parameterizable** by model × role × task (as U(route) is parameterized by terms).
- **Reuse** checkpoint + reload hook + context_diet already present — not a new subsystem.
- **Anti-fabrication:** where a model's effective capacity is unmeasured, mark it estimated.
- **First-class degradation:** failed compaction must not bring the agent down (fail-safe).

## Waves
- Wave A (NVIDIA, wide): 5 `glm-5.2` ideators, research-divergence.
- Wave B (Sonnet 5 medium): 3 ideators — (1) empirical/sweet-spot measurement; (2) decision POLICY design (when/what by model×role×task); (3) failure modes + cross-domain analogies (OS paging/GC, DB checkpointing, video keyframe/delta, human working memory).

## Convergence (Phase 5)
Cluster mechanisms; isolate trigger (%/function), preservation model (what stays), sweet-spot method (measure-first), and what is buildable now (measure-only quality×fill probe) vs active engine (owner-gated). Synthesize into a design + backlog increments.

---

# Phase 5 — Convergence (4 waves: NVIDIA 5 + Sonnet 3)

## UNANIMOUS convergence (all 4 independent waves)
1. **Normalize fill by the EFFECTIVE window (A_ctx), NOT the declared one.** Reframe #1 — prevents "guessing a percentage of the vendor number." A_ctx is a SURFACE (fill × position, because of Lost-in-the-Middle), not a scalar; collapse by worst-case position when one number is required.
2. **Trigger = watermark/threshold on fillRatio, parameterized by model×role×task** — not a global constant. Default ~72–75% (`judgment`), tuned against the EXP-16 quality×fill curve.
3. **Hysteresis / dual-zone (soft+hard, or H/L band)** to prevent thrash. Universal.
4. **Measure-before-control:** sweet spot comes from MEASURING the quality×fill curve (EXP-16 + noise floor), not guessing. **Build a measure-only probe FIRST** — that is the immediately buildable piece.
5. **TIERED preservation:** keep-verbatim (canonical/plan/decision-records/pinned = GC roots, NEVER summarized — structurally enforced: they do not enter summarizer input) / summarize / drop.
6. **Re-summarization depth-bound=1** (from checkpoint, NEVER from previous summary → anti-telephone-game).
7. **Checkpoint fail-safe** (rollback anchor BEFORE compaction) + deterministic validation (did pinned keys survive in summary?).
8. **Snap at subtask boundary** (do not trigger in the middle of a tool-call sequence).

## Converged parameterization
- **By model:** A_ctx (effective). **By role:** overseer earlier (~0.85–0.9× — its evidence IS the deliverable), worker later/rarely (~1.05× — near the end, let it finish), research aggressively (~0.7× — low-density filler), chat N wider (coherence loss bothers user). **By phase:** executing = later (do not interrupt a transaction), reporting = free.
- **Evidence density** = citations/tokens: high density requires a LARGER noise-floor margin (asymmetric cost — dropping load-bearing evidence is a correctness bug, not merely a quality issue).

## UNIQUE high-value findings
- **🔒 Compaction is a SECRET EGRESS SURFACE (NVIDIA w-004).** Summarizer READS context that may contain secrets/PII; if the checkpoint PERSISTS summary + secrets together it becomes a high-risk file. Secrets tier is NEVER summarized/persisted; trigger considers sensitive-data density; thrash MULTIPLIES leak surface (every cycle = another LLM pass over secrets). **Directly connects to RD-TAINT (D023):** summarizer is a SINK — tainted data cannot egress into a persisted summary. D023 taint envelope should mark Tier-0-secret as `never-summarize`.
- **💸 Cache invalidation cost (empirical).** Every compact resets the prompt-cache prefix — the DOMINANT hidden cost of compacting early in a chatty many-short-turn harness (larger than summarization call itself). Measure cache-hit before/after each compact.
- **🔗 Cross-hop compounding (empirical).** Multi-agent specific: a worker that compacts late produces degraded output that becomes overseer input (which may itself be full). New metric: "evidence survival rate across N hops." No published baseline — first measurement = low confidence.

## Two PROVEN reference architectures (control loops)
- **OS paging / working-set (Sonnet failure-modes):** working set = guaranteed residency; page fault = re-expand something compacted (cheap binary event); thrashing = compact too early. Classical fix: size from real working set, detect via fault rate (not fixed schedule).
- **TCP congestion control / CUBIC (NVIDIA w-005):** adapts window to OBSERVED capacity, not declared. Map: **ECN (mark before overflow) = EXP-16 evidence-loss as early signal**; **BDP (bw×RTT) = A_ctx**; **SACK (retransmit only gap) = re-expand only required span**; **RTO (conservative reset) = fail-safe**. Very tight fit — literally measure-before-control.

## Portfolio / what is buildable
- **BUILDABLE NOW (measure-only) — Context Fill Probe (CFP):** logs per turn fill% (declared+A_ctx), canary recall, latency, cost, cache hit, compact events + outcome; produces `(model,role,task,fill%) → (quality, verdict: safe/degraded)` with noise-floor gating. **NEVER compacts.** It is the measure-first instrument (like truth-divergence probe / GM-5). → **EXP-23**.
- **OWNER-GATED (active control):** Compact Controller (A_ctx×role×task trigger + hysteresis + boundary snapping), tiered preservation + summarizer, checkpoint fail-safe. It is CONTROL → needs CFP measurements that justify threshold (same discipline as C9 / N-TRUTHRECON-CORE). + secret-tier isolation (security → security review, aligns with RD-TAINT).

## Traceability
| Evidence | Idea | Experiment | Task | Status |
|---|---|---|---|---|
| 4/4 (A_ctx + watermark+hysteresis) + TCP/paging | CFP + Compact Controller | CFP = EXP-23 | N-COMPACTION | designed; CFP buildable, controller owner-gated |
| NVIDIA w-004 (secret egress) | secret-tier `never-summarize` | — | folds into RD-TAINT/D023 | designed |
| empirical (cache invalidation, cross-hop) | hidden costs + multi-hop metric | enters CFP | — | measure |
