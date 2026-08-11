# Research Round: Adoption of the Study “Context Governance in Multi-Agent Harnesses” (v2)

Date: 2026-07-28 | Orchestrator: Fable session (overseer) | Current phase: 0→2 (Discover/Define)

## Question

What should we adopt from the study `docs/research/estudo-governanca-contexto-v2.md` (uploaded by the owner, 2026-07-26, structured narrative review with ~60 sources) to make harness context management more efficient — given that the owner describes the current management as “not very efficient”?

## Success criteria

1. Every proposed adoption maps to a REAL harness gap (evidence: path, measurement or recorded incident) — nothing is adopted “because the study says so.”
2. Every claim carries a provenance prefix: `[study] §N`, `[repo] path`, `[judgment]`.
3. Output is a portfolio (core | experiments | parked | rejected) with effort and risk declared per item.
4. A mechanism that ALREADY exists in the harness (even partially) is recognized before proposing a replacement.
5. Stop at the human gate (Phase 2): briefs for owner approval, no Develop wave in this round.

## Declared breadth (D010)

2 lenses, explicit owner request (“you and Codex, using different biases”) and FOCUSED research (one fixed source, defined target — EXP-15 measured that higher fan-out here produces redundancy, not coverage):

- **Lens A — Claude/Fable (orchestrator, inline):** architecture & accidental-complexity risk. Conservative bias: what we already have, what is a real gap, what is YAGNI for a harness of this size (study §18.1/§18.11 admits that the full Control Plane may cost more than it saves).
- **Lens B — Codex (`gpt-5.6-sol` high, read-only lane):** token efficiency & operations. Aggressive adoption bias: where the harness wastes context TODAY, gain/effort ranking, skeptical of protecting current design.

## Declared budget

- Codex lane: 1 worker, no fan-out; ceiling ~80k tokens (study ~41k tokens calibrated at 3.1 chars/token + repo reads + output ≤500 lines).
- Lens A: inline in orchestrator (session already paid).
- No waves 2–3; convergence is manual orchestrator synthesis (2 workers fit in one context — single-pass reduce unnecessary).

## Declared design (L18)

Discover/Define round — no experiment produced in this phase. Cards landing in `experiments` follow the hypothesis/baseline/metrics/criteria template and only exist after registration through `harness.py experiment add` (Phase 5, after human gate).

## Phase 0 — What the repo already knows (records/doc-find, 2026-07-28)

`records search` is empty for the terms; `doc-find context compaction checkpoint reinjection` returns the live surfaces:

- `[repo] scripts/harness_lib/context_checkpoint.py` — in-flight checkpoint + post-compact reinjection (the study calls this canonical checkpoint + rehydration).
- `[repo] scripts/harness_lib/context_diet.py` — SPEC-118 context diet by role (the study calls this least context privilege, §5.7).
- `[repo] tools/hooks/reload_context_after_compact.py` — reinjection with protected parts never trimmed (the study calls this constraint pinning, §17.3); budget 9.8k chars, two margin exhaustions (2026-07-24, 2026-07-27).
- `[repo] .harness/handoff/plan-reinj-recalibrate.READY` — reinjection-budget check cries wolf in projected state — pending.
- `[repo] scripts/harness_lib/result_contracts.py` + `worker-result.schema.json` — typed return capsule with ceilings (the study calls this fold contract §7.4).
- `[repo] .harness/prompts/research-playbook.md §Budget` — required reads ≈12.1k tokens PER WORKER duplicated in each fork-join (~60k in a 5-worker wave); `sharedContextDigest` exists as opt-in mitigation.
- `[repo] harness.py workflow fold` (F1) — non-destructive fold manifest for FINALIZED workflow; `workflow evidence` — deterministic evidence bundles.

## Round artifacts

- Study (input): `docs/research/estudo-governanca-contexto-v2.md`
- Lens-B packet: `.harness/handoff/packet-analise-codex-governanca.md`
- Lens-B result: `.harness/handoff/analise-codex-governanca-contexto.md`
- Synthesis + portfolio: final section of this document (filled at convergence)

## Lens A — Architecture & complexity risk (Claude/Fable, inline)

### A1. What the study prescribes and ALREADY EXISTS here (do not rebuild)

| Study mechanism | Where it already lives | State |
|---|---|---|
| Canonical state outside the window (§3.3, §5.5) | git + backlog JSON + records + NEXT_STEPS/STATE/LEDGER_HEAD + handoff + `.harness/runs/` | exists |
| Constraint pinning (§17.3, Governance Decay) | `[repo] tools/hooks/reload_context_after_compact.py::_fit` — discipline parts are NEVER trimmed; only state yields | exists |
| Canonical checkpoint + rehydration (§6.4) | `[repo] scripts/harness_lib/context_checkpoint.py` — inflight block + per-file render with caps | exists |
| Typed return capsule (§7.4) | `[repo] scripts/harness_lib/result_contracts.py` + `schemas/worker-result.schema.json` (caps: ≤50 findings, evidence ≤20×500, recommendation ≤1000) | exists |
| Least context privilege (§5.7) | `[repo] scripts/harness_lib/context_diet.py` SPEC-118 — measured 40,264→16,520 tok/turn (-59%) with full diet | exists |
| Delegation contract (§7.7) | `[repo] .harness/prompts/subagent-contract.md` + plan briefs with HARD footprint | exists |
| Shared wave digest (anti required-reads, §11) | `sharedContextDigest: true` in most `.harness/workflows/workflow-profiles.json` profiles | exists |
| Non-textual resource GC (§8.15) | workspace cleanup post-gate, `kill-audit.jsonl`, gate-hold, cleanup-worktrees | exists |
| Claim provenance (§17.4) | `[web]/[repo]/[judgment]` prefixes (SPEC-119 v5) | exists |
| Honest budget (§14.2) | token-audit + 3.1 chars/token calibration + fuel show | exists |
| Fold of completed workflow (§10) | `harness.py workflow fold` (F1, non-destructive manifest) + `workflow evidence` | partial |

A1 conclusion: the harness already implements, in embryonic form, ~60% of what the study calls roadmap Phases 0–5 (§19). The gap is not “build the Control Plane”; it is to close 4–5 specific holes.

### A2. Real gaps, with measured pain

- **G1 — Reinjection pushes STATE into the window as dumps and loses the ceiling war.** `[repo]` FILE_CAP 1400 bytes/file (head+tail), vendor ceiling 10k, TOTAL_BUDGET 9,800; two margin exhaustions (2026-07-24 at 9.5k; 2026-07-27 at 9,933; untrimmed today 10,746). The study says the window is a materialized view and hydration should be minimal with pointers (§3.3, §6.3, §5.5.1 — “a summary.md is not enough,” and a head+tail dump is WORSE than a summary). Adoption: pointer-first reinjection — FULL inflight block + next action + typed pointers per file; stop inlining head+tail of CONTEXT/STATE/LEDGER_HEAD (stable content, readable on demand). Effort M. Note: `plan-reinj-recalibrate.READY` already attacks the symptom (cry-wolf check); G1 attacks the cause.
- **G2 — No PreCompact exists.** `[repo] tools/hooks/` has no PreCompact hook; checkpoint is agent discipline (`harness.py checkpoint` per phase). Compact in the middle of a phase ⇒ reinjection presents an OLD checkpoint as if current (§3.5.2 temporal mixing, exactly the failure described by the study). Minimal adoption: TELEMETRIC PreCompact — stamps compaction_count per session + warns if checkpoint is stale (age > current phase); feeds `DELEGATION_TOO_COARSE` signal (§14.13) for free. DO NOT block compact (a session stuck in a full window is worse). Effort S.
- **G3 — Overseer runs as a long multi-item session; study recommends reset per item (§6.1, H2).** Infra exists (checkpoint, reinjection, handoff, manual `resume-*.md` in `.harness/handoff/`). Missing formal rule: item closed → completion capsule → new session. Honest tension: 1h prompt cache pushes the other way (§8.13 cache economics) — reset throws away hot prefix. Do not decide by faith: this is experiment H2 (cheap baseline: compare cost/quality of N items in continuous session vs N items with reset, using existing records). Effort S in playbook + 1 experiment.
- **G4 — Lessons become prose, not typed memory (§11.4, H7).** Checkpoint trail carries narrative entries of ~2.5k chars (free-form PT-BR); render cuts at BLOCK_CAP 1300 — newest lesson competes with cap and old ones disappear. Typed negative memory (rejected claim + `evidence_refs` + reopen condition) costs one field in checkpoint/backlog row. Effort S–M. Experiment H7 later.
- **G5 — Zero context-pressure telemetry per lane (§14.1; roadmap Phase 0 §19).** `fuel show` gives Claude session `usedPct` and Codex gas, but no per-lane record stores pressure/compaction_count/peak-tokens. The study itself orders: telemetry BEFORE any policy. Without G5, G1–G4 have no baseline. Surfaces already exist (Codex rollout JSONL, Claude transcript, runner stamps). Effort S.

### A3. YAGNI — reject for our scale (study agrees in §18.1/§18.11)

- **Context Object Model + dependency graph + mark-and-sweep (§5.4, §8.5, §14.9):** we consume vendor CLIs; the live window exposes no object-level GC seam. Huge cost, inaccessible gain. Only real seam is HTTP family (`tools/openai_worker.py`) — one POST, no long-lived session.
- **Compaction Profile Compiler + semantic Integrity Gate (§14.3/14.4):** native compaction is opaque and outside our control; our countermeasure (reinjection + checkpoint + protected kernel) is already the cheap version. Recovery probe = more model calls to validate a summary the vendor will rewrite on next compact.
- **Own positional benchmark (§11.7, §16.4):** expensive eval waves; adopt Appendix-C defaults and recalibrate on real incident.
- **Learned policies / curator model (§9.5, Phases 8–9):** research frontier, no current pain justifying it.

### A4. Study × current-design tensions

1. Study: minimal hydration with retrieval by phase (§6.3). Harness: FIXED reinjection of 5 files (REINJECT_RELS) every time, independent of phase — a miniature “always everything.” Diet cuts by ROLE, not PHASE.
2. Study: reset-per-item as default (§6.1). Harness: long AFK session + compact — and vendor prompt-cache economics reward this (§8.13 admits trade-off; only experiment resolves it).
3. Study: typed capsule > narrative (§10.7). Harness: the most valuable continuity artifact (inflight trail) is free-form narrative.

### Lens-A prioritization (gain ÷ complexity)

G5 telemetry (S) → G2 telemetric PreCompact (S) → G3 reset-per-item as experiment H2 (S+EXP) → G1 pointer-first reinjection (M) → G4 typed negative memory (M, EXP H7).

## Lens B — Token efficiency & operations (Codex gpt-5.6-sol high)

Full result: `.harness/handoff/analise-codex-governanca-contexto.md` (ended with `ANALISE-COMPLETA`; claims anchored with `[repo]/[study]/[judgment]` per packet). Findings Lens A did NOT have:

- **B1 (waste #1, measured):** `WF-20260727-010246` paid ~42,979 stdout tokens + ~14,125 result-JSON tokens and accepted **0 of 3 capsules** — all exceeded `maxWorkerOutputChars` and were INVALIDATED whole. Today the return contract is a discard gate, not folding/offload mechanism (direct tension with study §7.4/§10.8).
- **B2:** wave digest is shared ON DISK but duplicated in each worker's window (~5,115 tokens × N workers), and carries contract content the role does not consume (~956 tokens/worker removable just from inapplicable contracts).
- **B3:** full parent task + seed interpolated into EVERY packet (`worker_prompt.py:60-75`) — ~7,944 tokens repeated in 3-worker wave.
- **B4:** owner session pays DOUBLE hydration: reinjection (~3,205 measured tokens) AND mandatory full reread of 6 AGENTS.md files (~8,415 tokens) — ~11.6k tokens per session start across both channels.
- **B5:** `context_diet` is no-op on Codex path (no keepTools knob) — -59% diet only exists on Claude vendor path.
- **Proposed baseline (deterministic, zero model calls):** estimated tokens per VALID WORKER_RESULT, computable from artifacts already present (`token-audit.json` + `validation.json` + stdout logs), with denominator-zero rule.

Lens-B rejections coincide with Lens A: full Control Plane, learned policies/RL, semantic compaction with validator, object registry + dependency graph.

## Convergence of the two lenses

| Theme | Lens A | Lens B | Verdict |
|---|---|---|---|
| Telemetry/baseline first | G5 | ranking #6 + §5 baseline | CONVERGE — first adoption |
| Checkpoint trail is expensive history | G4 (prose) | waste #5 (~2.5k foldable tok) | CONVERGE |
| Double hydration / reinjection dump | G1 | waste #6 + adoption #4 | CONVERGE (sequence after reinj-recalibrate) |
| Reset per item | G3 (experiment) | adoption #7 (no estimate) | CONVERGE — becomes EXP, not faith |
| Capsule discards instead of degrades | — | B1 (measured pain #1) | B ONLY — enters core |
| Digest by role | — | B2 | B ONLY — core (S/M) |
| Telemetric PreCompact | G2 | — | A ONLY — core (S, telemetry) |
| YAGNI: Control Plane, RL, COM | A3 | §3 | CONVERGE — rejected |

## Portfolio (Phase 2 — STOPPED AT HUMAN GATE)

### Core (proposals for approval — briefs below)

1. **BRIEF-1 Context baseline & telemetry.** Cost-per-valid-capsule metric computed from existing artifacts + PreCompact stamp (`compaction_count` per session, stale-checkpoint warning). Success: every completed workflow gets metric in records; no new model call. Actors: implementer S. Constraint: read only existing surfaces (token-audit, validation, rollout/transcript).
2. **BRIEF-2 Capsule degrades, does not discard.** Result above cap is offloaded to file + pointer and capsule becomes truncated-valid (marked `degraded`), never invalidated whole. Success: replay of `WF-20260727-010246` yields 3 usable degraded capsules. Actors: implementer S/M. Constraint: additive schema, do not break reduce.
3. **BRIEF-3 Trail fold.** Only newest trail entry stays inline; previous entries go to trail file with pointer. Success: NEXT_STEPS falls from ~4.1k to <1.5k tokens full-read without loss of access. Actors: implementer S. Constraint: `checkpoint` CLI contract retained.
4. **BRIEF-4 Digest by role.** Digest materializes common authority + only the contract consumed by the role. Success: ≥956 tokens/worker saved in measured 3-worker wave, no new invalid worker. Actors: implementer S/M.

### Experiments (register via `experiment add` ONLY after approval)

- **EXP reset-per-item (study H2):** hypothesis: physical reset per item reduces cost-to-success vs continuous session with compact. Baseline: BRIEF-1 metric on N items in each mode. Metrics: tokens/item, rereads, rework. Decision: adopt reset as default overseer-loop if cost ≤ +10% and quality ≥ equal. Method card: matched-budget.
- **EXP typed negative memory (H7):** hypothesis: typed rejected-hypothesis field reduces rework vs prose in trail. Depends on BRIEF-3.

### Parked (reevaluate when baseline exists / vendor surface unlocks)

- Pointer-first single hydration of owner session (A-G1 + B4) — M; sequence AFTER `plan-reinj-recalibrate` and after BRIEF-1 proves cost.
- Branch-specific briefing (B3) — M; touches `worker_prompt`, measure first.
- Positional packing by phase (B #8) — utilization gain not measurable without baseline.
- Diet on Codex path (B5) — blocked by vendor surface.

### Rejected (both lenses; study §18 agrees)

- Context Object Model + dependency graph + agentic mark-and-sweep.
- Compaction Profile Compiler + semantic Integrity Gate + recovery probes.
- Learned policies / RL / on-the-fly curator (roadmap Phases 8–9).
- Full custom positional benchmark (use Appendix-C defaults).

## Traceability

`Evidence → Problem → Proposal`:

- token-audit + `validation.json` from `WF-20260727-010246` → 43k tokens/0 capsules → BRIEF-2 (study §7.4, §10.8).
- Codex measurements in NEXT_STEPS.md (~3.4k trail tokens) → expensive canonical reading → BRIEF-3 (study §8.3, §8.12).
- token-audit digest (14,997 tok with digest in a 3-worker wave) + inapplicable contract excerpt (~956 tok/worker) → BRIEF-4 (study §6.3, §9.10).
- Reinjection exhaustions 2026-07-24/27 + double hydration (~11.6k tok) → parked single hydration (study §3.3, §6.3) — after BRIEF-1.
- Absence of PreCompact + stale-checkpoint risk (§3.5.2) → BRIEF-1.

## Round status

Phase 2 completed on 2026-07-28. HUMAN GATE PASSED (questionnaire, 2026-07-28):

- BRIEF-1..4 approved; execution DELEGATED (plan-role drafts → overseer finalizes → lanes with full ritual).
- EXP-35 (reset-per-item, H2) and EXP-36 (negative memory, H7) registered.
- Deferred items KEPT deferred, but CHAINED in backlog immediately after: `ctx-hidratacao-unica` and `ctx-briefing-por-ramo` (depends-on `ctx-medidor-custo`); Codex diet remains vendor-blocked.

Phase 5 executed: decision D053 in `.harness/context/DECISIONS.md`; backlog rows `ctx-medidor-custo` (P1), `ctx-capsule-degrada` (P1), `ctx-trail-fold` (P2), `ctx-digest-por-papel` (P2) + the two chained items above.
