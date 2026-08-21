# Nielsen Heuristics × Generative-AI and Agent UX (Round 2026-07-13)

Owner ask: background round — divergence on simple models (Gemini free tier), critique on smarter NVIDIA Build models (`glm-5.2` / `nemotron-ultra` / `step-flash`, surveyed in `nvidia-smart-models.md`).

## Question

How do Nielsen's 10 usability heuristics **translate, break, or need extension** when the interface includes generative AI (non-deterministic output, uncertainty, open-ended generation) and agents (autonomous actions on behalf of the user, human supervision, HITL)? Which new or reformulated heuristics should the harness adopt in its supervision dashboards (SPEC-114) and operator chat?

## Success criteria

1. Every candidate heuristic explicitly maps to a Nielsen heuristic (kept / reformulated / new), with WHY it changes.
2. Every normative claim carries source + date + confidence class (`strong…promotional`); no verifiable source → `reference: judgment`.
3. At least 3 candidates are actionable in the harness (panel/chat/escalations), each with a corresponding anti-pattern.
4. Novelty and maturity are scored on separate axes (playbook principle 2).

## Declared budget

- Wave 1 (divergence, 5 ideators, `gemini-compat` / `gemini-2.5-flash-lite`, interactive free tier — no batch, see `nvidia-smart-models.md` §A): ≤30k estimated tokens (packet-only: HTTP workers do not read the repo).
- Wave 2 (seeded critique, 4 critics, `nvidia-compat`: validity/architecture → `glm-5.2`, cost → `step-3.7-flash`, security → `nemotron-3-ultra`): ≤30k tokens (~4–6 NVIDIA credits).
- 60% gate: no wave 3 unless strong signal + headroom.

## Anchor evidence (Phase 1, Flow A — 2026-07-13)

| claim | source | type | year | confidence |
|---|---|---|---|---|
| The 10 heuristics remain canonical and actively maintained by NN/g | nngroup.com/articles (Ten Usability Heuristics) | docs | 2024+ | strong |
| Dedicated analysis of the heuristics for GenAI agents exists (Agent Experience) | Goldenberg & Goldenberg, ResearchGate 392368707 | paper | 2025 | moderate (peer review not confirmed) |
| Design principles for GenAI applications have been formalized (IBM) | arXiv:2401.14484 | paper | 2024 | strong |
| Augmented heuristics for computer-use agents have been proposed | arXiv:2605.02729 | paper | 2026 | preliminary |
| Synthetic heuristic evaluation (AI evaluator) has been compared with humans | arXiv:2507.02306 | paper | 2025 | preliminary |

## Phases 3–4 (filled by orchestrator while collecting waves)

- Wave 1 (ABORTED, process lesson): `WF-20260713-122514-240276` — 2 compound failures: (a) Gemini free tier during a 503 episode (health probe recovered in ~4 min; 3 retries consumed maxRounds); (b) **all 4 results were empty (0 findings)** — root cause: packet rule "scope with no material → done with empty findings" (correct for code analysis) instructed lazy output on pure knowledge briefs, which have no files in scope. Fix: new wave with explicit brief override (task = GENERATION; 4–8 `category: concept` findings required; empty = failure). Harness follow-up recorded: knowledge-domain divergence profile deserves its own packet without the empty-scope rule.
- Wave 1b: `WF-20260713-123540-504689` — the brief override WORKED (worker-001/simplicity: 5 real findings), but Gemini free tier entered sustained throttle (25-min probe: mostly 429, intermittent 503/200 — probes themselves consumed RPM). One valid result reused.
- Wave 1c: `WF-20260713-130602-119672` — divergence moved to `nvidia-compat` (cheap-provider outage). RECORDED DEVIATION: `plan` profile branches route to `glm-5.2` (ideation on smart model, not cheap); mitigation of rule "generator is never the sole evaluator": critics on `nemotron-ultra` (security) + `step-flash` (cost) + synthesis by orchestrator (Fable), with Gemini result from 1b included in synthesis (cross-provider blood).
- Wave 2 (critique): `WF-20260713-131740-274585` — 4/4 critics delivered (validity/architecture on `glm-5.2`, cost on `step-3.7-flash`, security on `nemotron-3-ultra`). Reduce invalidated all 4 due to a code-oriented rule (`sourceFilesVerified` required on high findings) — same family as the empty-scope bug; orchestrator synthesized directly from WORKER_RESULTs.

## Synthesis (orchestrator, 2026-07-13)

Sources: 25 concepts from 4 GLM ideators (wave 1c) + 5 from the Gemini ideator (wave 1b) + 23 findings from 4 critics. Strong convergence: 4/4 independent ideators proposed variants of "probabilistic-state visibility" and "layered approval by reversibility" — robustness signal (nominal groups). Critic caveat, accepted: candidate references are mostly `judgment` (seed digest compresses evidence; HTTP workers have no web access) — Phase-1 bibliography anchors support the Nielsen mapping, not each candidate individually.

### Portfolio (operations by card)

**Core** (adopt in SPEC-114 panels / operator chat):
1. `H-probabilistic-visibility` (reformulates Nielsen #1) — system state includes uncertainty + source, with explicit CALIBRATION (security critic: uncalibrated confidence creates false trust). Ops: reformulated.
2. `H-approval-by-reversibility` (reformulates #3+#5; merge of 3 overlapping candidates flagged by validity critic) — approval granularity proportional to action irreversibility; anti-pattern: constant dialogs. Ops: combined.
3. `H-persistent-audit` (reformulates #6, recognition>recall) — harness ALREADY HAS records ledger; heuristic is to expose it as a supervision timeline. Ops: kept (low cost, existing infra).
4. `H-visible-cost` (new, derives from #1) — cost critic asked for "nonexistent" telemetry; it EXISTS in harness (cost ledger R26) — critic could not see repo (packet with no scope, recorded limitation). Ops: kept.
5. `H-severity-calibrated-load` (new, #6+#8; EHR analogue) — boundary alerts separated from operational noise (panel already groups by tier). Ops: kept.
6. `H-template-consistency` (reformulates #4) — stable voice/format over variable content. Ops: kept.

**Contingency:** `H-autonomy-presets` (depends on reliable data classification — security critic); `H-boundary-validation` (pre-send data consent; partially covered by `classify_command` HITL).

**Experiments** (hypothesis/baseline/metrics template in doc before adoption):
`H-emergency-stop-with-revocation` (1 cost blocker from cost critic; revocation mechanism unspecified — hypothesis: suspend + revoke without context loss; baseline: current taskkill; metric: time-to-stop and post-stop integrity); `H-semantic-undo-checkpoint` (requires transactional state; external rollback infeasible → compensating transactions).

**Already production (kept, recognized in harness):** circuit breaker with cooldown (safe-action breaker) — financial analogy from ideator describes what SPEC-109 already does; output validation pre-commit (SDD gates).

**Rejected:** granular rollback of external surfaces as a standalone heuristic (security critic: infeasible; becomes part of compensating-transactions experiment).

### Harness follow-ups from this round (process, not theme)

1. **Knowledge-domain profiles:** "empty scope → empty findings" rule and lint "sourceFilesVerified on high findings" are code-oriented and invalidate knowledge rounds (3 occurrences today). Candidate: `knowledgeDomain: true` profile flag that swaps both rules.
2. **Seed digest compresses evidence** — validity critics cannot see concept references; carry evidence in seed (cap per item).
3. Gemini free tier: 429/503 under burst even at concurrency 1; health probe + resume worked (recovered 3 workers), but morning RPM is fragile — prefer NVIDIA for waves >3 workers on free tier.

### Traceability

Evidence (Phase 1, 5 anchors) → Problem (agent supervision violates/extends Nielsen) → Ideas (30 concepts, genealogy by workerRole/wave in WFs) → Critique (23 findings, 4 models) → Portfolio above → Next: intake SPEC-116 for core heuristics into panel backlog (owner decision).
