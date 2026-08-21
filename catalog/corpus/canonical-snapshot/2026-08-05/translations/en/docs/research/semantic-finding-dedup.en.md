# Round — Semantic Deduplication of Findings in Reduce (Post-EXP-15)

"Investigate options" study (playbook `.harness/prompts/research-playbook.md`). Trigger: owner 2026-07-18 — "investigate solutions for this in the article and its sources; if there aren't any, do research with NVIDIA." Article verified BEFORE the round: the full distillation (`harness-reference-architecture-adoption.md`) contains only the DIAGNOSIS (C5 sampling §4.4; marginal contribution §5.5a) — no semantic-fusion technique. The "if there aren't any" condition was satisfied → NVIDIA wave (owner directive: research with a cheaper model).

## Phase 0 — Question, criteria, budget

- **Question:** how should the harness DETECT (and optionally merge) semantically equivalent findings — paraphrases of the same idea — produced by parallel workers inside the harness single-pass reduce?
- **Primary evidence (measurement, strong):** [repo] EXP-15 + candidate probe (`.harness/runs/exp15-dedup-candidates-*.json`, commit `c6d92b4`): string keys do not recover convergence — prefix normalization merged 0/83; real convergence is paraphrastic ("Mock-vs-real matrix" ⇔ "flight simulator vs wind tunnel"); dedup by category+evidence merged 1/83.
- **Success criteria:** (a) runs in reduce (single-pass, ≤50 findings/wave, Windows, stdlib-first — new dependency only with a strong case); (b) per-reduce cost ≪ cost of 1 worker; (c) deterministic preferred, or at least auditable (candidate pairs visible, never silent merging); (d) explicit over-merge control (a false merge is worse than a duplicate because it loses a finding); (e) shadow mode first (measure before changing reduce — D008 discipline).
- **Declared budget:** 1 research-divergence wave on `nvidia-compat` (~5 HTTP posts, trimmed packets, ~15–25k NVIDIA tokens) + reduce + inline orchestrator synthesis. Critique wave: DO NOT spend — the question is narrow; critique is performed by the orchestrator against measured evidence (recorded; reopen if divergence produces a candidate requiring external validation).

## Phase 1 — Discover (internal completed; external via wave + post-wave verification)

[repo] EXP-15/probe: above. [repo] reduce constraints: `workflow_reduce.normalize_finding_key` (title+category+evidence), findings `additionalProperties: true` (cards may carry extra fields). [judgment] named candidate techniques at start (the wave remains free to generate; this is not a seed): embeddings+clustering, MinHash/SimHash, cross-encoder, cheap pairwise LLM judge, structured canonicalization, two-stage blocking. HTTP workers do not browse: references cited by the wave come from model memory — treated as `preliminary` until orchestrator verification; unverifiable material becomes `reference: judgment` (anti-fabrication).

## Phase 2 — Define (human gate: owner directive IS round approval)

Single brief (problem, not technology): "In the reduce of a fork-join, 5 workers report roughly 40% of the time the SAME idea with different titles/phrases. The harness needs to know WHEN two findings are the same idea, at minimum cost, with zero heavy dependencies, and without merging genuinely distinct ideas. How?"
Actors: deterministic reducer; orchestrator (may spend one cheap model call); owner (approves behavioral change). Constraints: criteria (a)-(e).

## Phase 3 — Develop

- Wave 1 (research-divergence, nvidia-compat): `WF-20260718-162602-104095`.
- **Revised diagnosis for `--force-round` (maxRounds requirement):** round 1 had 1/5 success; the remaining 4 ALL failed with `transport error: The read operation timed out` (worker-002..005 stderr) = the hardcoded 120s read timeout in `openai_worker._post` choked slow generations from the NVIDIA endpoint — not content flakiness and not the breaker (zero `executor-circuit-*.json`). Fix applied before retry: literal 300s (`tools/openai_worker.py`, comment points to this WF). Rounds were consumed by orchestrator VERB errors ("round" / "retry without worker" — real CLI is `retry <wf> <worker>` + run only-missing), not by model failures.
- Wave 1 result: 5/5 workers after retry with 300s timeout; reduce `partial` (4 valid + 1 schema-invalid), 24 deduplicated findings.
- **Manuscript mined in parallel (6 chunks × Sonnet; source now versioned at `docs/research/sources/adaptive-project-oriented-multi-agent-harness-architectures.md`, sha256 `5EEACC88...D69465C7064`):** the article does NOT prescribe a dedup technique — it prescribes GOVERNANCE: [repo/manuscript ~l.2313, prop. 22] "A semantic repair agent may propose a merge, but only a deterministic validator and authorized owner may commit it" (strong); [~l.861] correlated provenance is MARKED, apparent consensus is never a silent merge (strong); [~l.1722-1740] OracleRecall/CoFailure/Δ_m as formal convergence metrics [101 = arXiv:2606.27288, preliminary/C]; evidence envelopes with structured claims [~l.995] (dedup should key STRUCTURED FIELDS, not titles); LLM judge requires bias audit [130 = arXiv:2406.07791, moderate/B]. Solution clues cited: DyTopo semantic matching [25], CoAgent advisory semantic repair [191] — both `preliminary`.

## Phase 4 — Refine (orchestrator critique against criteria (a)-(e))

Operations by card (24 findings → 4 families):
- **Two-stage lexical candidate detection (SimHash/MinHash/Jaccard shingles + multi-scorer 2-of-3) → KEPT/COMBINED** in the core: pure stdlib, deterministic, auditable. Sanity check against EXP-15 ground truth: the known true pair shares concrete anchors in EVIDENCE ("m4_status_html", "mock", "real") — keying title+category+evidence has plausible recall; this is exactly what categoryFirstEvidence (1/83) had already suggested.
- **Shadow-mode JSONL + false-pair rate before any merge → KEPT** (converges with D008 and article proposition 22).
- **Embeddings/sentence-transformers → REJECTED for now** (heavy dependency, nondeterminism; the wave itself argued against it; criterion (a)).
- **Pairwise LLM judge → CONTINGENCY** (only borderline pairs, 1 cheap POST, with bias audit [130]; only enters if measured lexical recall is low).

## Phase 5 — Deliver

**Portfolio:** core = shadow-mode candidate-pair detector in the reduce path (advisory, zero merge — EXP-18); contingency = borderline LLM judge; rejected = embeddings-now, silent auto-merge; parked = DyTopo-style semantic matching (trigger: multi-tenant/scale).

**Recommendation to owner:** implement EXP-18 (measure-only): stage 1 Jaccard shingles over normalized title+category+evidence; stage 2 2-of-3 agreement (Jaccard, containment, TF-IDF cosine — all stdlib); candidate pairs go to `merge-candidates.jsonl` + are marked ADVISORY in reduce output (correlated provenance in the spirit of the article — never merged). Promotion to real merge: ONLY with false-pair rate <5% in a reviewed sample AND recall capturing the EXP-15 truth set — and even then through owner-gated SPEC-116 (prop. 22: merge commit requires deterministic authority + owner).

**Traceability:** EXP-15 (measurement) → question in this round → NVIDIA wave with 24 findings + manuscript in 6 chunks → EXP-18 (experiment registry) → future owner-gated spec if promoted.

**Implementation + measurement 1 (2026-07-18, commit `7ad5321`):** detector shipped as `scripts/harness_lib/merge_candidates.py` + fail-open emission in `workflow_reduce` (advisory in return dict + `merge-candidates.jsonl`; on-disk artifact byte-identical — schema `additionalProperties:false`). Scenario `mc_merge_candidates` 4/4. **Measurement 1 on the card (EXP-18 active):** truth run 29 findings → 0 pairs, recall 0/5; a true TODO paraphrase fires on cosine (0.57–0.66) and none reaches containment/jaccard — the 2-of-3 rule is too strict; next MEASUREMENT iteration recorded on the card (strong cosine ≥0.55 + 1-of-2, re-measuring false-pair) — thresholds unchanged until then (measure-only; promotion remains owner-gated under prop. 22).

**Measurement 2 (2026-07-18, pre-registered Taguchi grid):** committable probe `testing/probes/exp18_taguchi_grid_probe.py` (30 deterministic evaluations; differential assertion: cell A@0.50 == shipped detector, green). Rule A (2-of-3) recall 0.0 across all T_COSINE — confirms measurement 1. Rule B (strong cosine ≥T + 1-of-2 weak at half-threshold 0.175/0.30) at T=0.50/0.55: **recall 0.6** (recovers mock-vs-real, never-failed, weak-assert; misses bdd-tightening and info-per-check), false-pair proxy 0.0; T=0.60 degrades to 0.2. Delta 0→0.6 exceeds cross-WF spread (pairRate stdev 0.012; floor L13). **Verdict:** below promotion criterion (recall ≥0.8) — detector remains measure-only with shipped thresholds unchanged; candidate flat cell = B@0.55. Above abandonment criterion. Artifact: `.harness/runs/exp18-taguchi-grid-2026-07-18T205026Z.json`.

**Process incidents from the round (honesty):** `openai_worker` 120s timeout choked 4/5 workers (fix: 300s, committed); `maxRounds` consumed by an orchestrator verb error (CLI is `retry <wf> <worker>` + `run --force-round`, while the playbook says "round" in prose — candidate playbook correction); executor-state restored to generic after the round.
