# Research round — what the harness should adopt from multi-agent deep-research pipelines

Round opened 2026-07-11 by the `research` skill (SPEC-119, playbook
`.harness/prompts/research-playbook.md`). Orchestrator: overseer session; workers:
harness fork-join waves on the `claude` executor (Max window). First real run of the
skill — this round also validates the playbook end-to-end.

## Phase 0 — Question, criteria, budget

**Question.** Which mechanisms from deep-research pipelines (Anthropic research
system, STORM, GPT-Researcher, Deep Research-class products) should this harness
adopt to improve the quality and cost of its own multi-agent research rounds?

**Success criteria.**
- Portfolio with ≥3 genuinely distinct mechanisms (not tool variations), each
  traceable to an evidence row below.
- Every `núcleo`/`experimentos` item names its concrete harness integration point
  (file/module/config).
- Counter-evidence considered (MAD-overvalued, diversity collapse).
- ≥2 actionable outcomes (tasks/experiments promoted or SPEC-116 intakes).
- Round cost within declared budget.

**Declared budget (claude executor, Max window; real cost ≈ estimate × 1.3).**
- Wave 1 divergence (5 workers): ≤ ~90k input + ~10k output tokens.
- Agentic reduce: ≤ ~30k.
- Wave 2 critique (4 workers): ≤ ~75k input + ~7k output.
- Hard stop: no wave beyond these two (plan-approved scope: 1 divergence + 1 critique).

**Internal baseline** (records search: no prior entries on this topic; sources:
workflow-machinery audit 2026-07-11, session evidence):
- Required-reads block ≈ 9,371 tokens/worker at the old `chars/4` (~16× the packet;
  ~46,855 tokens per 5-worker wave). **Reproduced (TASK-002 E1):** the multiplier is a
  char ratio — 37,484 required-read chars ÷ ~2,285 packet chars = **16.4×**, so the "16×"
  claim holds and is estimator-invariant; at the calibrated `charsPerToken 3.1` it is
  ≈ 12,092 tokens/worker (~60,460 per 5-worker wave). The E1 wave-shared digest cuts
  required-reads ~63% to ≈ 4,477 tokens/worker (≈ 22,385 per wave) — measured in
  `token-audit.json` (`requiredReads` with/without digest).
- `chars/4` token estimator underestimated ~30% (measured 1.29-1.35×). **Calibrated
  (TASK-002 E2):** `charsPerToken` is now `3.1`; a punctuation/path-aware heuristic vs
  `chars/4` on real packets+required-reads measured 1.31× overall (3.05 chars/token) and
  budgets were rebased ~1.3× so effective ceilings are unchanged.
- `round` = retry of the same plan; seeded next waves require a NEW plan.
- Reduce is single-pass (no hierarchical/tree reduce); best-attempt selection exists.
- One executor per group (cross-vendor per wave only); circuit breaker is global
  per-executor; `minSuccess` gates settlement, not reduce status.
- Machinery correctness: audited sound (3 suspected bugs refuted, truth net green).

## Phase 1 — Evidence matrix

| claim | source | type | year | method | limitations | confidence | maturity |
|---|---|---|---|---|---|---|---|
| Orchestrator-worker with 3-5 parallel search subagents beats single-agent research by 90.2% on internal evals | [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system) | blog (primary, vendor) | 2025 | internal eval | vendor-reported, not replicated externally | moderada | produção |
| A separate citation pass (CitationAgent) after synthesis improves attribution | [Anthropic engineering](https://www.anthropic.com/engineering/multi-agent-research-system) | blog (primary, vendor) | 2025 | system description | no isolated ablation published | preliminar | produção |
| Perspective-guided question asking (mined personas) broadens coverage; +25% organization, +10% breadth vs baseline | [STORM, NAACL 2024](https://github.com/stanford-oval/storm) | paper + repo | 2024 | human+auto eval vs baselines | Wikipedia-article domain | forte | validado |
| Planner→parallel executors→publisher separation gives stable, faster research | [GPT-Researcher](https://github.com/assafelovic/gpt-researcher) | repo | 2023-26 | architecture + adoption (28k★) | no controlled eval | relato | produção |
| Recursive depth/breadth exploration ("deep research" tree) reaches subtopics flat fan-out misses | [GPT-Researcher deep mode](https://github.com/assafelovic/gpt-researcher) | repo | 2025 | feature description | no controlled eval | relato | protótipo |
| Independent (nominal) generation ≈2× ideas vs interacting groups — production blocking | [Diehl & Stroebe, JPSP 53(3)](https://homepages.se.edu/cvonbergen/files/2013/01/Productivity-Loss-In-Brainstorming_Toward-the-Solution-of-a-Riddle.pdf) | paper | 1987 | 4 controlled experiments | human groups, pre-LLM | forte | validado |
| Multiagent debate improves factuality/reasoning | [Du et al., ICML 2024](https://composable-models.github.io/llm_debate/) | paper | 2023 | benchmark evals | same-model instances; cost ↑ | moderada | validado |
| MAD is overvalued when model heterogeneity is ignored | [arXiv:2502.08788](https://arxiv.org/abs/2502.08788) | paper | 2025 | re-evaluation study | — | moderada | validado |
| Structural coupling between agents collapses idea diversity in open-ended generation | [arXiv:2604.18005](https://arxiv.org/pdf/2604.18005) | paper | 2026 | controlled generation study | recent, limited replication | preliminar | demonstração conceitual |
| LLMs cannot reliably self-correct reasoning without external feedback | [Huang et al., ICLR 2024](https://arxiv.org/abs/2310.01798) | paper | 2024 | controlled evals | reasoning tasks | forte | validado |
| Set-based convergence (keep option sets, eliminate by evidence) outperforms early commitment | [Sobek, Ward & Liker, SMR 40](https://sloanreview.mit.edu/article/toyotas-principles-of-setbased-concurrent-engineering/) | paper | 1999 | 5-year field study (Toyota) | manufacturing domain | forte | produção |

## Phase 2 — Brief and gate

**Brief (drives Wave 1).** How might we raise the quality and lower the cost of a
harness research round — for the human supervisor and the overseer — under these
constraints: stdlib-only runtime, no resident processes, enforced token budgets,
read-only workers, single-pass reduce, and full traceability — knowing that
required-reads dominate cost 16× and estimates run ~30% low?

- Actors: human supervisor; overseer/orchestrator; fork-join workers.
- Constraints: as above; changes must be reversible and auditable.
- Success: mechanisms with named integration points; measurable cost/quality effect;
  no new always-on infrastructure.

**Parked brief** (future round): scaling worker counts beyond a single reducer's
context (hierarchical reduce) — deferred, depends on Wave 1 signal.

**Gate.** Pre-approved by the human at plan approval (plan step 11: topic, executor
claude/Max, wave sizes 5+4, budgets above). Recorded here per playbook Phase 2.

## Phase 3 — Wave 1 (divergence) — done

`WF-20260711-202902-946083`, profile `research-divergence`, executor `claude`
(Max window), 5/5 ideators settled (~15 min wall, sequential), token-audit pass.
Reduce: deterministic (25 deduplicated concept findings, 0 conflicts); semantic
clustering done by the orchestrator (playbook allows overseer-as-reducer) — one
model call saved.

**Independent convergence** (strong signal): 4/5 ideators independently proposed a
wave-shared context digest for the 16× required-reads cost; 4/5 proposed estimator
calibration. **Real divergence:** the simplicity ideator explicitly recommended
REJECTING hierarchical reduce + recursive deep mode at current scale (≤5 workers).

**Consolidated clusters (genealogy: wave-1 worker findings → cluster):**
- C1 wave-shared-context-digest (broadcast prelude / orchestrator-prepared reads
  digest / shared required-reads digest — workers 1, 2, 5)
- C2 estimator-calibration chars/4 → ×1.3 (workers 1, 2, 5)
- C3 seeded-next-wave: `plan --seed <WF>` + REDUCE_RESULT as Delphi facilitator
  summary, depth-bounded (workers 3, 5)
- C4 checkpoint-resume for workers (worker 3; Anthropic pattern)
- C5 citation-verification folded into the critique wave (worker 4)
- C6 research-worker sandbox: least-privilege env + egress allowlist + provenance
  quarantine + secret-scrub at reduce boundary (worker 4)
- C7 effort-scaling + early-stopping (workers 3, 5)
- C8 hierarchical reduce — contested (proposed by worker 2, rejected by worker 1)
- C9 decision-pattern telemetry (worker 4)

**Machinery findings exposed by running the round (evidence for the round itself):**
1. `existing_rel_path` used `lstrip("./")` — a char-set strip that removed the
   leading dot of dot-dirs (`.harness/...` → `harness/...`), failing existence
   validation for every dot-dir path; and its URL guard ran AFTER the `:`-split,
   making it dead code — every URL in evidence was rejected as a missing path.
   Both fixed (harness.py `existing_rel_path`, result_contracts `_pathish`).
2. `claude` executor could not spawn headless on Windows: npm shim not resolvable
   by CreateProcess (fixed: `_resolve_argv0` via `shutil.which` at the single
   spawn choke point) and the template lacked `-p` (fixed in executors.json).
3. Profile output caps were miscalibrated for concept-card payloads: 3/5 valid
   results exceeded `maxWorkerOutputChars: 5000` by ~6-60%; recalibrated to 9000
   (divergence) / 8000→10000 (critique — all 4 honest critics exceeded 8000) in
   the profile and in the WFs' frozen limits (operator action, disclosed; worker
   outputs untouched).
4. `generate_handoff` emits context packs that violate its own budget: the
   canonical required-read set is ~25.4KB ≈ 6.3k tokens vs `maxRequiredReadTokens
   5000`, and the generator only demotes *conditional* reads — any freshly
   regenerated handoff fails `workflow:handoff-context-pack`. Same defect class as
   the audit's required-reads finding (E1/C1 evidence). Not fixed this round
   (restored the passing committed handoff); recorded as a draft task.

## Phase 4 — Wave 2 (critique) — done

`WF-20260711-204952-828293`, profile `research-critique`, 4 critics with explicit
branch roles (validity → `review`, architecture → `review`, cost/ops → `scan`,
security/product-risk → `security`), seeded with C1-C9. 4/4 settled; 36 deduplicated
critique findings; token-audit pass. Calibration note: all 4 honest critic results
exceeded the 8000-char cap (8.4-9k) — recalibrated to 10000 (operator action,
disclosed; outputs untouched).

**Consolidated verdicts (explicit operations per card):**
| Cluster | Verdict | Operation | Key critique |
|---|---|---|---|
| C1 digest | viável com condições | mantida | multiplier must be reproduced; digest stays NON-authoritative (canonical files remain source of truth); correlated-failure risk; required-reads list is a hardcoded choke point |
| C2 calibration | viável | simplificada | "mostly already built — run it, not build it" (knob at `token_economics.charsPerToken`) |
| C3 seeded waves | experimento | limitada | convergence-only (seeding divergence waves contradicts this round's own independence evidence); dangling seeds after scrub; injection-laundering / autonomy-creep risk; no direct evidence for REDUCE-as-Delphi |
| C4 checkpoint-resume | rejeitar | rejeitada | 3/4 critics: contradicts the stateless read-only worker contract; premise does not transfer at current worker sizes |
| C5 citation verification | viável | mantida | "already operational this round" — the validity critic did exactly this; formalize in the playbook, not a new agent |
| C6 sandbox | experimento (split) | dividida | full-env inheritance is a REAL gap today (high — workers inherit parent env incl. API keys); but 2 of 4 bundled mechanisms unsourced → split: least-privilege env + secret-scrub slice first; egress allowlist + provenance quarantine parked |
| C7 effort-scaling / early-stopping | split | dividida | effort-scaling viável (plan-time knob exists); early-stopping rejeitar (needs a mid-wave judge; borrows statistical rigor without its assumptions) |
| C8 hierarchical reduce | rejeitar | rejeitada | wave-1 rejection adjudicated CORRECT: semantic join is not associative; revisit trigger: workers per wave > one reducer context |
| C9 decision telemetry | rejeitar | rejeitada | unfalsifiable as stated — no definition, no source, no consumer |

## Phase 5 — Portfolio & traceability

**Núcleo (próximo incremento):**
- N1 Estimator calibration (C2): measure observed chars/token on this round's two
  real waves, set `charsPerToken` (~3) in `.harness/project.json` tokenBudget.
- N2 Citation-verification duty (C5): playbook amendment — the validity critic's
  branch text gains an explicit "verify every evidence URL/claim" duty. No new agent.
- N3 Effort-scaling guidance (C7a): playbook budget section — size waves (3-5) to
  question complexity via existing `--max-workers`.

**Contingência:** digest experiment fails (quality drop / correlated failures) →
keep per-worker required-reads (config revert, zero migration).

**Aposta de fronteira:** C3 seeded-next-wave, convergence-only (`plan --seed <WF>`),
depth-bounded, packets marked as seeded (injection-laundering mitigation).

**Experimentos:**
- E1 (C1) digest A/B: same brief, 5-worker wave with vs without wave-shared digest;
  metrics: input tokens/worker, findings count/quality, failure correlation.
  Decision: adopt if ≥40% input-token cut with no quality drop.
- E2 (C2) calibration measurement: compute real tokens vs chars/4 on WF-202902 +
  WF-204952 logs; decision: set charsPerToken to measured value.
- E3 (C6a) least-privilege env slice: spawn research workers with allowlisted env
  (strip API keys not needed by the executor) + deterministic secret-scrub check at
  collect; decision: adopt if zero worker breakage.

**Estacionadas:** C6b egress allowlist + provenance quarantine (needs platform
support); C9 reworked with a falsifiable definition and a named consumer.

**Rejeitadas (com motivo):** C4 checkpoint-resume (stateless contract; scale); C7b
mid-wave early-stopping (judge cost > wave cost at 3-5 workers); C8 hierarchical
reduce (join non-associative; trigger recorded).

**Draft tasks:** 10 promoted to `tasks/generated/` (runtime), curated 2026-07-11
into `tasks/research-portfolio/PLAN.md` (TASK-002: E1/E2/E3 + seeded-wave bet +
handoff-budget defect; the 3 checkpoint-resume drafts closed as recorded rejections).

### Traceability matrix

| Evidência | Problema | Ideia/Decisão | Experimento/ADR | Spec | Task | Status |
|---|---|---|---|---|---|---|
| audit 2026-07-11: required-reads 16×/wave | custo por onda | C1 digest → D004 | E1 | SPEC-119 v2 (pendente) | draft tasks | experimento |
| audit: chars/4 −30%; Phase-1 row 6 | orçamento irreal | C2 → D003/D004 | E2 | — | draft tasks | núcleo |
| Anthropic citation pass (Phase-1 row 2) | evidência não verificada | C5 → playbook duty | rodada (operacional) | SPEC-119 v2 | — | núcleo |
| Diehl & Stroebe; Diversity Collapse | independência das ondas | C3 convergence-only | aposta | — | draft | fronteira |
| crítico de segurança: full-env inheritance | vazamento potencial de chaves | C6a slice | E3 | follow-up security | draft | experimento |
| críticos 1-4 (C4/C8/C9) | complexidade especulativa | rejeições D004 | — | — | — | rejeitadas |
| bugs de validador/executor achados ao vivo | máquina vs pesquisa | fixes desta rodada | regressões rs:* | SPEC-119 v2 | — | corrigido |

**Round cost:** 2 waves (9 workers claude, Max window) + 1 smoke worker; wall ~35
min; well under the declared budget (no wave beyond the approved two).

## E4 — spawn-context diet & payload audit (2026-07-11, SPEC-118 v4)

Continues the cost thread (E1 digest, E2 calibration, E3 env slice). E1-E3 cut the
harness-authored *payload*; E4 also attacks the vendor *session* a claude worker loads,
and audits every byte the harness itself hands a worker.

### Phase A — session-diet measurement (live, 4 minimal calls, `claude -p stream-json`)

`context` = the turn's full input the model saw = `input + cache_creation + cache_read`
(cache only splits cost, not context size). Single-turn, so no turn-count confound.

| variant | input | cache_creation | cache_read | **context** | cost |
|---|---:|---:|---:|---:|---:|
| 1 baseline (v3 flags) | 2 | 15,853 | 20,986 | **36,841** | $0.101 |
| 2 + `--strict-mcp-config` | 2 | 9,912 | 26,789 | **36,703** | $0.068 |
| 3 + `--setting-sources project,local` | 10 | 8,875 | 15,309 | **24,194** | $0.019 |
| 4 + all four diet flags | 10 | 21,769 | 0 | **21,779** | $0.044 |

`--setting-sources project,local` is the lever (**−12,647**, −34%); `--strict-mcp-config`
alone ≈ 0 on total (kept anyway: cost-split + no user-MCP leak). Full set: **−41%/turn**.
The Figma/obsidian MCP + user skills ride USER settings, so dropping user scope (not
strict-mcp) is what removes them. Variant 4's `cache_read 0` is a cold prefix (the flags
changed the cached prefix), not a real cost — steady-state a wave shares that 21.8k prefix.

### Phase B — 1-worker live smoke, before vs after (same packet, haiku low)

| run | observedTokens | input | cache_creation | cache_read | turns | tools | cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| before (baseline template) | 117,578 | 6 | 15,326 | 102,246 | 6 | 2 | $0.138 |
| after (diet template) | 134,496 | 42 | 12,507 | 121,947 | 15 | 7 | $0.050 |

**observedTokens is turn-count-bound, not a clean acceptance metric.** The diet run
happened to take 15 turns vs 6, so its summed usage *rose* despite a smaller per-turn
prefix (`cache_creation` 15,326 → 12,507). The ≤50k target (vs the recorded historical
151,216, a different model/turn-count) is **not met and not soundly measurable this way**;
the real, transferable win is the Phase A per-turn context cut. Both runs authenticated
(rc=0) under `--setting-sources project,local`, so the diet does not break subscription
auth. Verdict: keep the flags on the per-turn cut + cache-prefix stability + security, and
retire `observedTokens ≤ target` as an acceptance gate (record per-turn context instead).

### Payload audit — every byte the harness hands a worker (chars → tok @ 3.1)

| piece | chars | tok | consumed by | verdict |
|---|---:|---:|---|---|
| spawn prompt ("Read `X` and execute…") | 168 | 54 | claude/HTTP (1st user msg) | essencial |
| packet header (10 fields) | 378 | 122 | LLM; HTTP reads Role + WF-id | essencial (no zero-consumer field) |
| Parent task | 54 | 17 | all | essencial |
| Worker scope + paths | 145 | 47 | all | essencial |
| Required reads — non-digest | 203 | 65 | CLI worker; DEAD for HTTP | só-alguns → **stripped for HTTP** |
| Required reads — digest | 727 | 235 | research CLI worker | essencial (digest-first) |
| Rules block | 1,227 | 396 | all | essencial (largest section; shared, byte-guarded) |
| WORKER_RESULT reminder — non-digest | 177 | 57 | all | essencial |
| WORKER_RESULT reminder — digest | 177→~90 | 57→~29 | research | **dedupe applied** (pointer to verbatim contract) |
| context digest (research only) | 13,877 | 4,476 | research workers | essencial (replaces 12,092-tok reads) |
| └ verbatim WORKER_RESULT contract in digest | 2,257 | 728 | research | essencial (lossless contract) |
| required-read FILES if obeyed — non-digest | 37,484 | 12,092 | CLI worker | **formato-subótimo** (16×; digest fixes only research today) |
| HTTP inlined contract `subagent-contract.md[:8000]` | 8,000 | 2,581 | HTTP worker | **formato-subótimo** (needs only the 485-tok WR slice) |
| env `HARNESS_*` | — | n/a | worker process | essencial (not model tokens) |

### Changes applied (safe now)

- **Session diet** (D005): four flags on the claude template — −41%/turn context.
- **Research reminder → pointer** (2a): the digest already carries the WORKER_RESULT
  contract verbatim; the packet stops re-listing the keys. Marginal (~28 tok/worker) —
  the real research-side win was already E1's digest, not this.
- **HTTP packet trim** (4): `openai_worker` drops the `Required reads` block a single-POST
  worker can't act on — −65 tok/call and removes a misleading instruction.

### Recommendations (measured, NOT applied — need their own scoped change)

- **Digest for non-research profiles** — biggest packet-side lever: −7,615 tok/worker
  (required-reads 12,092 → 4,477). Guarded by `rs:digest-optout` deliberate byte-identity;
  warrants its own spec decision (which analysis profiles opt in).
- **HTTP contract slice** — return only the `WORKER_RESULT` section from `_read_contract`:
  −2,096 tok/call (2,581 → 485). The rest (HARNESS_RESULT / REDUCE / REVIEWER /
  controlled-write / verification policy) is dead weight for a single-shot HTTP worker.
- **Phase C `--tools` read-only allowlist** — residual ~21.8k/turn after the diet; built-in
  tool schemas are the largest remaining lever, but the cut needs a live measurement +
  write-workflow safety review before adding the seam.

Live-call budget: 4 Phase-A + 2 smoke (before/after) = 6; no commit (per task).
