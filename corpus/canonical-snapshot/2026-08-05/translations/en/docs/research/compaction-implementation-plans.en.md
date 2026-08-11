# Implementation Plans — Automatic Context Compaction (N-COMPACTION-*)

Plans parked in the backlog (owner 2026-07-19: "create plans for each one and leave them in backlog"). Derived from `compaction-round.md` (4 waves) + D029. Each plan is implementer-ready: reuse of existing machinery, approach, footprint, acceptance, gate (measure-vs-control), dependency, size.

**Existing machinery to reuse (DO NOT reinvent):**
- `tools/hooks/reload_context_after_compact.py` — reinjects canonical context after compact.
- `scripts/harness_lib/context_checkpoint.py` + `docs/CONTEXT_CHECKPOINT.md` — state checkpoint.
- `scripts/harness_lib/context_diet.py` — classifies pinned/read-only/schema-trim (acts as the tier sorter).
- EXP-16 (evidence loss) + A_ctx (effective vs declared context) — base measurement.
- `append_event` (hash chain) + experiment registry — to log measure-only events.
- `records`/delegation ledger — cost/latency/cache-hit per call.

---

## N-COMPACTION-CFP (EXP-23) — Context Fill Probe · BUILDABLE NOW (measure-only) · size M

**Goal:** measure the quality×fill curve while NEVER compacting, producing the table `(model, role, task, fill%) → (quality, stdev, N, verdict: safe|degraded)` with noise-floor gating. This is the instrument that justifies (or does not justify) the controller — measure-before-control (D008).

**Reuse:** EXP-16 (evidence-loss = natural y-axis); A_ctx (effective denominator); `append_event` (log each event); experiment registry (EXP-23 already registered, method = confidence-sequences); delegation ledger (cost/latency/cache-hit per call).

**Approach:**
1. **Passive per-turn probe** (`testing/probes/context_fill_probe.py`, sibling of truth-divergence/GM-5): logs per turn/tool call — `model, role, task_id, task_type, task_phase, fill%(declared), fill%(A_ctx if bucket known), latency, tokenCost, cacheHit/miss, compactionEvent(if triggered, at what fill%), evidenceDensity(=pinned/total via context_diet)`. Deterministic, stdlib, writes ONE timestamped JSON under `.harness/runs/`. NEVER compacts.
2. **Cheap canary recall:** every M turns, inject a known fact and check whether the agent still retrieves it K turns later (or whether the next tool call correctly uses state that should still be visible). This is the cheap quality signal (expensive RULER-like grid remains for synthetic evaluation).
3. **Reduction by bucket:** for `(model, role, task_type)`, aggregate production `quality(fill%)`; noise floor = stdev of repetitions at the SAME low fill%; cliff = first fill% whose drop > L13 noise floor for ≥2 consecutive buckets + replicated. Emit table + verdict.
4. **A_ctx as a SURFACE** (fill × position, due to lost-in-the-middle): report by position bucket, collapse by worst-case when one number is required (harness does not control where reinjected content lands). Extend EXP-16 to vary position × fill if it does not already.

**Footprint:** `testing/probes/context_fill_probe.py` (new, with self-check); one lightweight per-turn logging hook in driver (or `append_event` at an existing point); perhaps a field in delegation ledger for cacheHit. DOES NOT touch production compaction path (it does not exist yet).

**Acceptance:** probe runs ≥20 real turns/tasks + synthetic grid, produces bucket table with noise-floor gating, ZERO compactions triggered. Self-check (assert monotonic-ish curve, empty→zeros). Records first data point in EXP-23.

**Gate:** measure-only, within measure-first authority (like truth-divergence probe). Buildable without owner gate. **Abandon (EXP-23):** if quality does not fall beyond noise floor until near overflow (A_ctx ≈ declared) → model can use entire window; controller becomes trivial (hard ceiling only).

**Dependency:** EXP-16 (exists). **Honest ceiling:** long-transcript LLM judge itself degrades (measurement-of-measurement); injected canary perturbs what it measures (sampling rate is a real tradeoff).

---

## N-COMPACTION-CTRL — Active Compact Controller · OWNER-GATED (control) · size L

**Goal:** engine that DECIDES when/what to compact, parameterized by model×role×task, with hysteresis, tier preservation, depth-bounded re-summarization, and fail-safe. This is CONTROL → only after CFP (EXP-23) measures the threshold that justifies it (same pattern as C9 / N-TRUTHRECON-CORE).

**Reuse:** CFP table (threshold comes from it, not a constant); `context_diet` (keep/summarize/drop tier sorter); `context_checkpoint` (rollback anchor); reload hook (belt-and-suspenders, NOT load-bearing — Tier-0 is excluded during prompt assembly, not "recovered later").

**Approach:**
1. **Trigger** = pure pre-turn function in driver (LLM NEVER decides to compact; it only summarizes afterward): `shouldCompact(fillPct/A_ctx, model, role, phase, evidenceDensity, state)` → hard ceiling (0.92) OR (fill ≥ θ(role,phase,model) AND outside hysteresis cooldown AND at a subtask boundary). θ comes from CFP table; judgment defaults (overseer 0.85×, worker 1.05×, research 0.7×).
2. **Tier preservation** (`context_diet` classifies): Tier-0 verbatim never-summarize (canonical `.harness`, goal, plan/seam, last N turns by role, pinned) — STRUCTURALLY excluded from summarizer input; Tier-1 summarize incrementally (summary + delta, NEVER re-summarize from scratch); Tier-2 drop (already-captured falsified material, duplicated tool reads, content already in checkpoint).
3. **Re-summarization depth-bound=1:** always from latest checkpoint + raw delta, never from previous summary (anti-telephone-game).
4. **Summarizer decoupled from task model**, gated by measured evidence loss per content class (cheap model summarizes IF measured loss < ceiling; otherwise canonical model; otherwise Tier-0-only).
5. **Fail-safe:** checkpoint BEFORE summarization; deterministic post-compact validation (do pinned Tier-0/1 keys/paths still appear in summary? if not fail-closed → rollback → escalate one rung → escalation structure, never loop or silent truncation). Re-expand a specific checkpoint span when compacted information becomes necessary (locally reversible compaction).

**Footprint (when opened):** `harness_lib/compaction.py` (controller + pure trigger function + tiers); pre-turn call point in driver (where token-budget check already lives); reuse checkpoint/diet/reload hook; NEW spec door (SPEC-116) + scenario (trigger fires at correct boundary; Tier-0 never enters summarizer; fail-safe recovers).

**Acceptance:** controller compacts at the correct boundary when CFP says worthwhile, preserves Tier-0 verbatim, validates deterministically, and survives a failed compaction (rollback). Regression measurement: post-compact quality does not fall below baseline (CFP measures it).

**Gate:** OWNER-GATED. Prerequisite: EXP-23 measured threshold. Guiding analogies: TCP (ECN/BDP/SACK/RTO) + paging (working-set/fault-rate).

**Dependency:** N-COMPACTION-CFP (EXP-23). **Size:** L.

---

## N-COMPACTION-SECRET — Secret-Tier Isolation · OWNER-GATED (security) · size M

**Goal:** ensure compaction does NOT become a secret-egress surface (NVIDIA w-004 finding). Summarizer reads context that may contain secrets/PII; checkpoint must not persist summary+secret together. Extends RD-TAINT (D023).

**Reuse:** existing secret scan (detects shapes at boundary); RD-TAINT/D023 taint envelope (marks provenance); `context_checkpoint`.

**Approach:**
1. **Secret tier = never-summarize/never-persist:** data marked `secret-read` (D023 taint envelope) is Tier-0-secret — NEVER enters summarizer input NOR persisted checkpoint summary. Summarizer is a SINK in taint model (D023): tainted data cannot egress into a summary.
2. **Trigger accounts for sensitive-density:** a research worker accumulating secrets should compact EARLIER/differently (do not let secrets linger in context that will be summarized).
3. **Layer isolation in checkpoint:** if checkpoint persists a summary, summary is scrubbed (reuse secret scan) — never one file containing summary + raw secret.
4. **Anti-thrash is anti-leakage:** every compaction cycle is another LLM pass over context — CTRL hysteresis also reduces exposure surface.

**Footprint (when opened):** integrate into N-COMPACTION-CTRL (tier sorter marks secret tier) + RD-TAINT taint envelope; one security scenario (marked secret never appears in summarizer input nor persisted checkpoint). Isolated security review (security path).

**Acceptance:** a marked secret in context NEVER appears (a) in summarizer input, (b) in persisted summary; boundary test proves it. Fail-closed.

**Gate:** OWNER-GATED + security review. **Dependency:** N-COMPACTION-CTRL + RD-TAINT/D023. **Size:** M.

---

## Suggested order
1. **N-COMPACTION-CFP (EXP-23)** — buildable now; measure threshold. Without it, everything else is guesswork.
2. **N-COMPACTION-CTRL** — only when CFP shows a cliff worth controlling (otherwise trivial).
3. **N-COMPACTION-SECRET** — together/after CTRL, behind RD-TAINT, with security review.

> Note: the same treatment (parked implementer-ready plan) can be extended to other research items (N-TRUTHRECON-*, RD-U→U, RD-CRASH→injector, RD-TAINT→taint) when requested.
