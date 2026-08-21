# Round R1 — Conformance Self-Assessment (Article §5.9 + App F + ATAM)

Round 1 of 5 under directive **D012** (owner 2026-07-18: all rounds via NVIDIA, sequential, incrementing `docs/research/article-coverage-backlog.md` before any implementation). Phase-2 human gate pre-approved by D012.

## Phase 0 — Question, criteria, budget, breadth

- **Question:** what fraction of the article's minimum contract (16 App F suites, per-plane tests §5.9, 24 ATAM scenarios, App I.8 invariants) do our gates/scenarios/hooks/probes ALREADY prove, with what score on the 0–3 evidence scale (§11.3-c), and where are the real gaps?
- **Success criteria:** (a) every article requirement gets a 0–3 score + an evidence item from the inventory OR a named gap; (b) worker claims about the repo are HYPOTHESES until local orchestrator audit (D012; miner precision ~75%); (c) adopt App F-17/18 rule: failed/missing suite CAPS the maturity dimension — no compensating average; (d) output = coverage-backlog increment (new lines/status corrections/intakes).
- **Breadth (D010):** 3 workers BY CONSTRUCTION — mapping partitioned into 3 disjoint slices (B1 App F F1–F16; B2 §5.9 planes + App I.8; B3 ATAM 1–24). This is coverage by partition, not redundancy — focused mode does not apply to disjoint split; each worker's Δ_m = its entire slice.
- **Declared budget:** single wave ≤45k tokens (3 × ~10k input + ~5k output). Executor `openai-compat` (NVIDIA Build, D012). No critique wave: convergence is LOCAL orchestrator audit (evidence is deterministically verifiable in repo — model-criticizing-model does not pay here).
- **Declared design (L18):** not a measurement experiment — an audit with closed rubric (0–3 scale from §11.3-c + F-17/18 cap rule). Methods card: n/a; output feeds internal M-frame (D008/D011).

## Phases 1–2 — Embedded evidence

NVIDIA workers cannot read the repo (D012): packet embeds (a) requirement side (one-liners extracted from manuscript by 2026-07-18 scan, 6 extractors) and (b) evidence side (deterministic inventory generated in this session: 138 scenarios with check IDs, 32 gate fixtures, 13 hooks, 7 probes, 11 gate kinds). Provenance: requirements `[repo]` (audited extraction), inventory `[repo]` (script-generated), worker mappings `[judgment]` until audit.

## Execution

- Wave 1 attempt 1: `WF-20260718-215103-726280` — 3/3 workers responded but INVALID under transport contract: fork-join without profile capped `maxWorkerOutputChars=4000` (audit produces 7–10k) and GLM marked severity `high` without required evidence fields. Lesson for NVIDIA audit waves: use profile with cap 12000 + rubric fixing `severity: info`. Preserved for forensics; not reduced.
- Wave 1 v2: `WF-20260718-215453-361908` (profile `research-divergence` with EXPLICIT branches — first live use of L16 by-construction rule; `slots.declaredWidth` auto-stamped custom/3). Executor `nvidia-compat` (GLM `z-ai/glm-5.2`). Embedded task: 13.4k chars (~4.3k tok) — B1/B2/B3 requirements + inventory (138 scenarios, 32 fixtures, 13 hooks, 7 probes) + 0–3 rubric + severity=info rule.
- Follow-up B3: `WF-20260718-220210-201111` (1 worker by construction) — v2 wave had a coverage hole: w2 AND w3 processed B2 (block instruction by branch title has weak adherence on low-effort GLM); B3 rerun in isolation, 24/24 verdicts. Lesson for NVIDIA waves: 1 BLOCK PER WAVE when partition matters, or repeat the block at top of task (done in follow-up).
- **Declared budget override:** `maxWorkerPromptTokens=3900` assumes worker that READS repo (required-reads outside prompt). HTTP NVIDIA worker does not read files (D012) → content embedded by design, ~4.3k tok/worker. Total wave (~15k in + ~9k out) remains WITHIN `maxTotalPlannedTokens` (42k). Honest override via `workflow start --override-budget` (recorded trail; path tested by `budget:override-recorded` in m2).

## Synthesis (audited by orchestrator — mappings verified against real inventory)

Anti-fabrication audit: 8 out-of-vocabulary names in 63 findings — ALL legitimate abbreviations of embedded machinery block (e.g. `noise_floor` vs `noise_floor_probe`, `N1 receipts`); citation precision ≈100% on material items. GLM score verdicts adjusted by orchestrator where noted.

**App F (16 suites):** score 2 in 11 suites (F2–F11, F14); score 1 in 5:
- F1 Constitution — no compiled/signed constitution (🅿️ ECA); reality is protected-files+deny hooks (deny-overrides slice).
- F12 Trajectory — ir1/ir6/ir8 are worth 2 (N2, L3, L4); hash-chain/signature = 0 (🅿️).
- F13 Privacy — real scrub/redaction/vault; formal per-item classification absent.
- F15 Promotion — ORCHESTRATOR CORRECTION: 1→**2** (registry D008 + SPEC-116 doors + exl 5/5 + gg governance are real internal tests; GLM mapped only gg).
- F16 Interop — esh covers spawn hygiene; conformance suite per adapter absent (→ C3/C16b already ⬜ in backlog).
- **ZERO score 3 across entire assessment** — honest: nothing has independent/external longitudinal evidence (multi-org is D011 trigger).

**§5.9 planes + App I.8 (23 lines):** most score 2; score 1 concentrated in P5 context-economy (per-call accounting reconciliation — C12b ⬜) and I10 (counterexamples as trace — formal 🅿️).

**ATAM (24 scenarios):** 9 likely-pass (A1 router swap, A2 provider outage [r15 failover], A6 crash-resume, A10 reproduction [records+route tuple], A12 catalog, A20 stale approval [C12], A21 pause worker [qcw], A22*, A23*) | 15 unknown | 0 confirmed fail-today. The 15 unknowns are the product: they become a tabletop-test checklist (below).

**Coverage-backlog increments applied:**
1. New ⬜ line "ATAM tabletop-test checklist" (15 unknowns → 15 cheap tabletop tests, 1 doc; prioritize A13 crash-before-receipt and A14 poisoned-memory revocation).
2. New 🔬 line "crash injection at adapter boundary" (A13/§5.7: no test crashes between external effect and receipt; candidate fixture).
3. F15 corrected to 🟡→score 2 in self-assessment (registry/door evidence).
4. App F-17/18 rule adopted: maturity dimension capped by worst mandatory suite → internal M remains M2–M3 (F1/F12 score 1 cap M2 "governed" in constitution/trajectory dimension until named slices rise).
