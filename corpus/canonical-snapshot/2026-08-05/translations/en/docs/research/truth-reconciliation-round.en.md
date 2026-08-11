# Round #3 — Truth-Source Reconciliation Engine (N-TRUTHRECON)

Research round for owner item #3 (2026-07-19): “the ‘source of truth’ — let’s research and build it, it is
important.” Basis: D015 + GM-5 finding. Orchestrator = this session (not worker). Phase 0 here; divergence
wave through **NVIDIA** (`nvidia-compat`, glm-5.2 smart tier — winner of race-mode test #1).

## The problem (framed as problem, not solution — Phase-2 job-to-be-done)

Owner (D015): “multiple sources of truth — code, documentation, accumulated history, third-party docs. A
system always fails; what matters is being prepared for when it fails.” The real pain is not “choose the
right source” — it is **what the harness does when sources DIVERGE or one goes down**, without an arbitrary
or silent decision.

Sources of truth in today’s harness (real inventory, `[repo]`):
- **code** — git is the source of truth for code (CONTEXT.md).
- **harness** — source of truth for task state/continuity/routing/handoff.
- **documentation** — specs (`specs/`), AGENTS.md/CLAUDE.md, research docs.
- **accumulated history** — records ledger (SPEC-112), git log, event log (now hash-chained + causal DAG:
  T-HASHCHAIN/T-CAUSALPARENT).
- **third-party documentation** — vendor docs (round #5 showed often wrong/absent — e.g. balance API
  returning 404).

One slice already exists: **GM-3 provenance firewall** (governed memory retrieval trusts only items with
`authority >= signed_policy`) and **GM-5** shadow challenge (measures doc↔code divergence by commit).
N-TRUTHRECON is the **parent direction**: GM-3 becomes one slice of it.

## Round question

> When two or more harness sources of truth (code, doc, history, vendor) **disagree** about the same fact —
> or one source becomes **unavailable** — what mechanism produces an **auditable, deterministic,
> degradable** answer, preferring documentation by default but never trusting it blindly?

## Success criteria

- **Actors:** harness (fact reader), owner (ratifier for unresolved divergence), workers (producers of
  potentially conflicting facts).
- **Deterministic:** same source inputs produce same verdict + same audit trace (no LLM “vibes” in path).
- **Degradable (owner’s CORE requirement):** with N−1 sources available, engine still answers, marks response
  degraded and says WHICH source is missing. “Prepared for failure” = a missing source is first-class state,
  not unhandled exception.
- **Doc-preferred but auditable:** when doc wins over code, engine records WHY (applied precedence rule),
  not only outcome.
- **Does not reinvent:** reuse subject dimension, hash chain (T-HASHCHAIN), GM-3 provenance, research
  confidence classes. Measure before control (D008): if real divergence is ~zero (like C9 churn), engine gets
  no enforcement — instrumentation only.

## Declared budget (per wave)

- **Wave 1 (divergence):** 5 NVIDIA ideators, ~12k required-read tokens/worker + ~740 packet ⇒ ceiling ~65k
  tokens. NVIDIA free tier (negligible $; real cost is time/RPM ~40/min per model). Budget gate at 60%.
- **Wave 2 (critique/convergence):** only with strong signal + headroom. 4 critics (validity, architecture,
  cost, security). Likely Claude Max-window (critique must read actual repo), NOT NVIDIA.

## Declared breadth (D010)

**EXPLORATORY → 5 ideators.** Rationale: scanning a field (divergent-source reconciliation crosses
distributed systems, provenance, CRDT/consensus, source-of-truth patterns, fault tolerance) WITHOUT fixed
implementation target yet. Exactly where nominal-group diversity pays (Diehl & Stroebe 1987) — opposite of
EXP-15, which penalized over-fan on one already-defined topic. Each ideator attacks a distinct perspective
(research-divergence profile: simplicity, performance, reliability, trust boundary, cross-domain analogy).

## Declared design (L18)

The round FEEDS an experiment (EXP-22): measure real divergence among sources before enforcement. Method card
(**corrected 2026-07-19 after owner challenge** — earlier citation “measure-before-control + noise floor” was
PRINCIPLE D008, not a book card): **Confidence sequences**
(`docs/EXPERIMENT_METHODS.md#confidence-sequences`) + **Evidence grades** (`#evidence-grades`). This fits
because probe is a SHADOW experiment: anytime-valid confidence sequence, **alpha budget α=0.05**, updated
every `experiment record` batch, settles verdict when interval lies ENTIRELY below L13 noise floor (abandon →
measure-only forever, C9 destination) or entirely above enforce-worthy level — no peeking penalty. Current
grade 2 (attributive); flip to enforcement requires confirmatory-or-better + clearing noise floor. Primary
deliverable is DESIGN + decision of measure-only vs enforce slice.

> Process note: L18 advisory (`experiment_registry._METHOD_HINTS`) did NOT fire for this experiment — keyword
> table lacked family for shadow/measure pattern. Fixed in commit `e5a1a4b` (shadow/measure/canary/divergen/
> noise-floor → confidence-sequences+evidence-grades+noise-floor); `exl-5` covers regression.

## Phase 1 — Evidence (prep)

`doc-find "truth source reconciliation divergence"` → 0 hits (nothing re-derived). Source inventory above
is `[repo]`. External evidence to gather in post-wave synthesis (Flow A/B): source-of-truth patterns,
event-sourcing/CQRS reconciliation, CRDT merge, W3C PROV for divergent provenance, degradable quorum/consensus.

## Phase 3 — Divergence wave (to run)

`workflow plan --profile research-divergence --task "<brief truth-recon>"` →
`workflow run --executor nvidia-compat` → `collect` → `reduce --agent`.

### Wave-1 brief

> Design the mechanism by which the harness reconciles divergent sources of truth (code, docs, accumulated
> history, third-party docs) and keeps responding when a source fails. Constraints: deterministic and
> auditable (same input → same verdict + trace); docs preferred by default but with deduction recorded;
> first-class degradation (N−1 sources → response marked degraded naming missing source); reuse subject
> dimension + hash chain + GM-3 provenance; measure divergence before enforcement. Deliver precedence model,
> reconciliation-record format, and measure-only instrumentation point proving whether enforcement is worth it.

## Next steps

Wave 1 → reduce → synthesize into backlog increments (new N-* / N-TRUTHRECON slices) → bring portfolio to
owner (build is owner-gated: item #3 says “research AND build,” and building depends on joint review).

---

# Phases 3–5 — Result, Convergence and Portfolio (Orchestrator Synthesis)

Wave 1 ran: `WF-20260719-050502-817281`, 5 NVIDIA ideators (glm-5.2). All 5 delivered strong DISTINCT ideas
(nominal-group diversity paid off, as predicted for exploratory case). Auto-reduce was blocked
(`canReduce=false`) for two reasons that DO NOT invalidate content — orchestrator synthesizes manually (its
role) and documents why:
- worker-003: `sourceFilesVerified required when high/blocker findings present` — divergence ideator marked a
  “high” finding without verifying file (expected: it does not read repo). Content valid; strict reduce gate.
- worker-004 and worker-005: **secret-scan false positive** — `openai-style-key` pattern (`sk-…`) matched
  INSIDE word “ta**sk-**reconciliation-…” / “ta**sk-**truth-source-…” (task ID slug, not key). See derived
  N-SCANNER-FP below. Results are clean; they were read and judged.

## Independent convergence (strongest signal — 3+ workers, unseen by each other)

1. **Precedence = PURE FUNCTION, no LLM in path** (w-001, w-003, w-005). Same source input → same verdict +
   same trace. Core: `(sources: Map<SourceId, SourceState>) -> ReconciliationRecord`, zero state, zero effect.
2. **Measure-only probe BEFORE enforcement** (ALL 5). Counter `divergenceCount`, zero blocking. Empirically
   proves whether enforcement is justified — confirms D008/measure-before-control. Became **EXP-22**.
3. **Degradation is EMERGENT, not a feature** (w-001, w-003, w-005). Missing source is simply skipped
   (absent Map key) and degraded is marked naming it — no separate handler. Answers owner’s core criterion.
4. **Reuse T-HASHCHAIN + GM-3 provenance firewall** (w-001, w-003, w-004, w-005). GM-3
   `authority>=signed_policy` is same “validate before accept” pattern — GM-3 becomes reconciliation trust slice.

## Concept cards + operation (Phase 4 — set-based, no collapse into one score)

| card | source | operation | why |
|---|---|---|---|
| **TR-CORE** — pure-function PrecedenceResolver, 2 tiers | w-001+w-003 | **kept+simplified** | Core. Simplification from w-001: collapse 4 sources into **2 tiers** — AUTHORITATIVE = git+records (share hash chain/T-HASHCHAIN) · ADVISORY = specs/AGENTS+vendor (no crypto provenance). “doc-preferred” becomes a **tier mapping** (specs in high tier), not runtime rule. |
| **TR-RECORD** — reconciliation record format | w-001(7 fields)+w-003(9)+w-004 | **combined** | Converged fields: `{fact, winningSource, loserSources[], precedenceRuleApplied, tier, degraded:bool, absentSources[], inputHashes{}, at, subject}` + inherits provenance-firewall metadata (w-004). `precedenceRuleApplied` is “never blind”: records WHY doc won. |
| **TR-PROBE** — measure-only instrumentation (`divergenceCount`) | all | **experiment → EXP-22** | Measures real divergence per commit/retrieval before enforcement. If ≤ L13 noise floor, engine remains measure-only forever (C9 destination). GM-5 already measures one slice (doc↔code). |
| **TR-DNS** — DNS as reference architecture | w-005 | **kept (design skeleton)** | DNS already solved THIS: reconcile authoritative zones + cache + resolver history + upstream, deterministically and degradably, RFC-grounded. 1:1 map → DNSSEC=GM-3; SOA-serial-compare=TR-PROBE (measure drift); TTL-freshness=confidence classes (degradation label); NXDOMAIN negative-cache=never silently record doc>code precedence. De-risks whole design. |
| **TR-TRUST** — trust-boundary hardening | w-004 | **split (feeds N-SECREVIEWER)** | 3 real findings: (a) `absentSourceName` is a **side channel** revealing which subsystem failed → expose only to authorized roles; (b) **vendor/third-party docs = untrusted input** → sandbox parsing; (c) TR-PROBE becomes sensitive-data sink if logging divergence CONTENT → log counts/hashes, never content. |
| **TR-PERF** — O(S×R) pipeline + cache + parallel + backpressure | w-002 | **deferred (YAGNI until volume measured)** | performance only matters if TR-PROBE shows volume. Same measure-first: do not optimize a path whose volume is unmeasured. Preserved as upgrade path. |
| **N-SCANNER-FP** — secret scan matches `sk-` inside “task-…” | round finding | **experiment/task** | Real bug: `openai-style-key` needs word-boundary anchor before `sk-` to avoid “ta**sk-**slug”. Cost 2 valid results. Own fix (security path → isolated review), not inline. |

## Portfolio (Phase 5)

- **core:** TR-CORE (pure 2-tier resolver) + TR-RECORD + TR-DNS (reference skeleton/naming).
- **experiments:** TR-PROBE = **EXP-22** (measure-before-control; only thing buildable immediately because
  it is measurement, not control).
- **contingency:** TR-TRUST (hardening) — folds into N-SECREVIEWER when owner opens that role (D014).
- **parked:** TR-PERF (volume unmeasured).
- **derived:** N-SCANNER-FP (bonus security bug, like oracle in #4).
- **rejected:** none — all 5 perspectives complementary, not competing (validates exploratory breadth D010).

## What is owner-gated vs buildable now

- **Buildable now (measurement):** TR-PROBE/EXP-22 — measure-only probe measuring divergence among sources
  (extends GM-5 to 4 sources). No enforcement.
- **Owner-gated (“build” part of #3):** TR-CORE + TR-RECORD as ACTIVE reconciliation mechanism (control —
  requires EXP-22 measurement first, exactly like C9). And N-SCANNER-FP (touches security path).

## Traceability matrix

| Evidence | Problem | Idea | Experiment/ADR | Spec | Task | Status |
|---|---|---|---|---|---|---|
| w-001/003/005 (pure function) + DNS RFC1035/2181/4035/2308 (w-005) | sources diverge/fail, answer must be deterministic+degradable | TR-CORE 2-tier + TR-DNS | D020 | (owner-gated) | N-TRUTHRECON-CORE | designed |
| all 5 (measure-first) + GM-5 | do not build control without measuring divergence | TR-PROBE | **EXP-22** | — | N-TRUTHRECON-PROBE | registered, buildable |
| w-004 (trust boundary) | record/probe/degradation are sensitive surfaces | TR-TRUST | D020 | (contingency) | folds into N-SECREVIEWER | designed |
| round finding | secret scan matches `sk-` in “task-…” | N-SCANNER-FP | — | (owner-gated, security) | N-SCANNER-FP | found |

## Sources (Phase 1 post-wave, `[web]` to verify against primary)

- DNS as deterministic degradable reconciler: RFC 1035 (iterative resolution), RFC 2181 §9 (trust ranking),
  RFC 4035 (DNSSEC validation), RFC 2308 (negative caching). `[web]` cited by w-005 — strong primary anchors
  (IETF), to reconfirm on promotion. Confidence: moderate; maturity: **production** (DNS has run the world for
  40 years).
- Internal `[repo]`: T-HASHCHAIN, GM-3 provenance firewall, GM-5 shadow challenge,
  D008 measure-before-control, L13 noise floor.
