# Research round — improving the quality of agent-written code

Round opened 2026-07-12 by the `research` skill (SPEC-119). Orchestrator: overseer session
(running in parallel with the batch N+2 worktree implementers). Primary evidence: the owner's
study (2026-07-12) applied to a multi-agent/multi-model/multi-vendor harness — thesis: **code
quality from agents is a control-and-assurance-SYSTEM problem, not just a model-capability
problem.** Reliable gains come from coupling generation to verifiable specs, sandboxed
execution, INDEPENDENT tests, static/security analyzers, review separated from authorship,
BOUNDED repair cycles, and explicit accept/abandon criteria. Tests are necessary but not
sufficient; verifier INDEPENDENCE beats raw reflection; more agents ≠ more quality.

## Phase 0 — Question, criteria, budget

**Question.** Which code-quality assurances should THIS harness adopt, given it already owns a
strong deterministic QA spine (separated roles + no-self-waiver, sandbox isolation, proportional
gates, per-item scenario self-checks, records ledger, fold/handles/digest evidence capsules,
budgets + circuit breaker), and given the study's own biases (verifier independence, risk-
adaptive gates, heterogeneous oracles, evidence-not-logs, single-agent baseline)?

**Success criteria.**
- Backlog of buildable items, each mapped to a NAMED gap + a concrete integration seam
  (file/module) + ONE quality dimension it moves (correctness/security/maintainability/test-
  strength/provenance/review-cost).
- Deterministic-first: prefer an independent deterministic oracle (mutation/property/metamorphic/
  static), a risk classifier that SELECTS gates, and a provenance ledger — over more LLM
  reflection, bigger agent societies, or bleeding-edge formal verification.
- Every item respects our invariants: eviction ≠ deletion, no resident daemon, stdlib-only core,
  GUI writes no state, verify-on-demand, summaries are a view, evidence capsules not full logs,
  an agent must NOT be the sole judge of its own code (independence).
- Critique must reject over-engineering: single-agent is the baseline; the study's own warnings
  bind — author-written tests can formalize the author's misreading; reflection ≠ verification;
  benchmark/coverage scores ≠ real quality; observation must pay for itself.

**Declared budget.** claude executor; 1 divergence wave (5 ideators) + 1 critique wave (4
critics); research-profile budgets; no wave 3.

## Phase 1 — Evidence matrix (verified 2026-07-12)

| claim | source | prov | conf | maturity |
|---|---|---|---|---|
| Code quality is a control/assurance-system problem; execution signals + external verifiers select better programs | [web] CodeT (arXiv:2207.10397), LEVER (arXiv:2302.08468) | web | forte | validado |
| A lean pipeline can beat complex agentic systems at lower cost (localize→repair→validate) | [web] Agentless (arXiv:2407.01489) | web | forte | validado |
| Tests are necessary but NOT sufficient; SWE-bench Verified retired as a frontier metric (defective tests + contamination) | [web] study §2.1; OpenAI statement Feb-2026 | web | forte | produção (relato) |
| Verifier independence > raw reflection; author-generated tests can fail as oracles (shared blind spots) | [web] Self-Debugging (arXiv:2304.05128); AgentCoder | web | forte | validado |
| More agents ≠ more quality; a minimal driver/navigator pair saves tokens vs heavy multi-agent; coordination errors documented | [web] PairCoder; RTADev | web | moderada | preliminar |
| Public benchmarks can't be the sole decision mechanism (contamination; none represents a specific org's software/risk/architecture) | [web] LiveCodeBench (arXiv:2403.07974); BigCodeBench | web | forte | validado |
| Maintainability impact uncertain; academia focuses security/perf while devs care about readability/maintenance; long-trajectory degradation | [web] study §2.5; SlopCodeBench | web | moderada | preliminar (preprint) |
| Security does NOT emerge from functional code; passing tests must not auto-release auth/crypto/authz/serialization/parsing/infra/deps | [web] study §2.6; CyberSecEval | web | forte | validado |
| Reflection (Self-Refine/Reflexion/LATS) complements but does not substitute for independent verification | [web] Self-Refine (arXiv:2303.17651); Reflexion | web | forte | validado |
| Context = "evidence capsules" (failure + location + violated property + minimal snippet), not re-injected logs | [web] study §3.8; Anthropic effective-context-engineering | web | forte | judgment (norma) |
| Mutation score is closer to oracle strength than coverage; property-based testing (QuickCheck) catches shallow tests | [web] QuickCheck (ICFP'00); mutation-testing literature | web | forte | consolidado |
| Policy frameworks (NIST SSDF, OWASP ASVS, SLSA) convert into agent/pipeline-consumable rules | [web] study §3.5; NIST SSDF, OWASP ASVS, SLSA | web | forte | validado |
| Selective formal verification is plausible but costly/narrow | [web] AlphaVerus; DafnyBench | web | moderada | demonstração conceitual |

**Baseline — what the harness ALREADY has (do NOT rebuild):** separated roles (implementer /
reviewer / critic) + **no-self-waiver** + reviewer contract (= author≠approver, one of the
study's top "adopt now" items); sandbox isolation (worktrees, controlled-writes with scoped
write-paths, target SPEC-110 harness-vs-target); the **intake-triage hook** (classifies a
request profile: security/review/plan/docs) + proportional gates; per-item WORKER_RESULT /
HARNESS_RESULT with a **scenario self-check**; `spec_test_gate` (a fixed heterogeneous check
set: static-integrity, release-hygiene, path-hygiene, handles-lint, en-default-guard, and the
**security-baseline** landing now = secret-scan + AST sink-scan + config-hygiene); records
ledger + `subject` dimension; **fold F1 + handles + context digest = the study's "evidence
capsules"**; token-audit + budgets + maxRounds + circuit breaker (CE.1, bounded repair); the
two-door SDD+BDD flow (SPEC-116) = verifiable spec attached to a change.

**Named gaps (candidate backlog anchors):**
- **CQ1 — no INDEPENDENT-oracle portfolio.** The only per-change functional oracle is a scenario
  self-check WRITTEN BY THE SAME implementer — the study's #2 hole (author tests formalize the
  author's misreading). No mutation testing (does the check kill a planted mutant?), no property/
  metamorphic oracle. `spec_test_gate` checks are structural, not per-patch functional. Gap: a
  cheap deterministic independent oracle (start: mutation-probe a changed function's self-check).
- **CQ2 — gate selection is not RISK-ADAPTIVE per patch.** intake-triage classifies the REQUEST;
  there is no per-PATCH classifier that routes a diff touching auth/crypto/authz/serialization/
  parsing/subprocess/deps to deeper gates + human approval (study #6). security-baseline exists
  but is observe-only and not risk-routed. Gap: a deterministic diff-risk classifier → gate depth.
- **CQ3 — no agentic-code PROVENANCE/DEBT ledger that follows a patch post-merge.** The records
  ledger logs events, but there's no per-merged-hunk record of (which agent/model authored it,
  what oracle proved it, later human touch/regression) — the study's #5 opportunity. Ties records
  + `subject`. Gap.
- **CQ4 — the acceptance oracle is author-written (independence hole).** no-self-waiver covers the
  REVIEW verdict, but the TEST/oracle that gates acceptance is authored by the same agent that
  wrote the code. Study #2. Gap: an oracle authored/mutated by a DIFFERENT role or `--seed`.
- **CQ5 — evidence capsules are partial for QA.** fold/handles/digest are strong, but the QA
  evidence attached to a patch (which oracle ran, what property it proved, the minimal failing
  snippet) is not a structured capsule a reviewer can trust without re-running. Partial — may
  fold into CQ1/CQ3.
- **CQ6 (likely PARK) — selective formal verification for critical kernels.** Bleeding-edge
  (AlphaVerus/Dafny), heavy spec investment, does not fit stdlib-only today.

## Phase 2 — Briefs and gate

**Brief 1 — an independent oracle + author≠tester (CQ1+CQ4; the study's #1 leverage).** How might
the harness add a CHEAP deterministic independent oracle for a change — e.g. mutation-probe the
implementer's own scenario self-check (flip a boolean / drop a return in the changed function,
assert the self-check now FAILS → proves the test has teeth), and/or route oracle authorship to a
different role/`--seed` — so acceptance no longer rests on author-written tests alone, reusing the
existing scenario runner + spec_test_gate seam, deterministic, net-cost-positive, no LLM-in-loop?

**Brief 2 — risk-adaptive gates + agentic provenance/debt (CQ2+CQ3).** How might a DETERMINISTIC
per-patch risk classifier (diff touches auth/crypto/authz/serialization/parsing/subprocess/deps/
infra → higher tier) SELECT gate depth + force human approval on the highest tier (study #2/#6),
and how might a provenance/debt record follow each merged change (author agent/model, oracle
evidence, risk tier, later human maintenance) via the records ledger + `subject` — so the harness
sees where agentic debt accrues, WITHOUT a daemon, summaries-are-a-view, single-agent baseline?

**Parked (future round / needs a signal):** CQ6 selective formal verification (bleeding-edge;
needs a critical-kernel + spec investment); a full private/temporal benchmark (study #4 — needs
a real workload corpus + eval harness, a round of its own); heterogeneous multi-vendor oracle
diversity (needs the CQ1 oracle seam first).

**Gate.** Scope/waves/budget pre-approved by the owner (this invocation). Deterministic-first +
verifier-independence + risk-adaptive + net-cost-positive + single-agent-baseline are hard
constraints on the critique wave.

## Phase 3 — Wave 1 (divergence)

`WF-20260712-212058-051387`, `research-divergence`, 5 ideators (simplicity, performance,
reliability, trust-boundary, analogy), claude executor. All 5 fulfilled. Strong deterministic
convergence on the 6 gaps; every concept stdlib-only, no daemon, no LLM-in-loop. Standout
convergences: **mutation-probe** the author's own self-check (flip a bool / drop a return in
the CHANGED function, assert the check now FAILS → the test has teeth) — a deterministic
mutator, NOT a second agent; **`security_baseline.evaluate` already computes a `new` diff that
NOTHING consumes** (observe-only at spec_test_gate.py:1778) → a per-patch risk classifier can
consume it for near-zero marginal cost; **oracle-replay** — the reviewer re-runs the author's
declared self-check from a CLEAN worktree and records the exit class, closing author-grades-own-
work cheaply. Cross-domain transfers (analogy lens): aviation NDT inspector calibration → Q1;
double-blind clinical / incoming-inspection-against-PO → Q4; DO-178C DAL / HACCP CCP → Q2;
pharma DSCSA lot-traceability → Q3; GSN assurance-case → Q5.

Orchestrator consolidated the 25 concepts into **6 candidates**:
- **Q1 mutation-probe gate** (CQ1) — a diff-scoped stdlib gate check: mutate the CHANGED
  function (flip bool / drop return / swap comparator), assert the author's scenario self-check
  now FAILS (killed); 5-state exit class (killed/survived/error/timeout/skipped) so "couldn't
  run" never reads "passed"; observe-only first. Seam: `spec_test_gate` check via bind(env).
- **Q2 per-patch risk-tier gate selection** (CQ2) — a deterministic diff-glob + sink-token
  classifier (reusing security_baseline's sink patterns) that SELECTS gate depth, and CONSUMES
  the security-baseline `new` diff currently unconsumed at `spec_test_gate.py:1778`; observe→
  enforce rollout; critical tier adds revert-cleanliness (`git apply -R --check`) + human
  approval. Seam: `intake_triage.py` + spec_test_gate.
- **Q3 provenance / agentic-debt record** (CQ3) — one `records.add_entry` at finalize (author
  agent/model, oracle evidence, risk tier); agentic-debt is a LAZY on-demand git-derived VIEW
  (blame/log), never a daemon. PARK hunk-level ledger. Seam: `records.py` + workflow finalize.
- **Q4 oracle-replay (author≠tester)** (CQ4) — the reviewer replays the author's declared self-
  check from a clean worktree and records `oracleReplay.exitClass`; composes with Q1 (Q1 fixes
  WEAK tests, Q4 fixes UNGRADED tests). Stronger later: spec-first oracle from SPEC-116 Gherkin
  by a different role. Seam: reviewer role / workflow finalize.
- **Q5 QA evidence capsule** (CQ5) — a capped, structured `oracleEvidence` capsule (which oracle
  ran, exitClass, minimal failing snippet) in WORKER_RESULT, scrubbed through the secret_scan
  collect boundary; review cost O(capsule) not O(re-run). Seam: WORKER_RESULT schema + collect.
- **Q6 (PARK)** — selective formal verification, N-version oracle voting, entropy/DLP-grade
  secret detection, per-patch LLM security review (unbounded cost / bleeding-edge).

## Phase 4 — Wave 2 (critique) — done

`WF-20260712-214047-864247`, `research-critique`, 4 critics (validity/architecture/cost/
security), `--seed` = the divergence reduce. All 4 fulfilled. Verified anchors: `security['new']`
computed and only REPORTED at `spec_test_gate.py:1778-1783` (Q2's dangling signal — real);
`security_baseline._classify_sink` reusable at `security_baseline.py:81`; `records.add_entry` at
`records.py:128`; the collect secret boundary WITHHOLDS secret-shaped results at
`workflow_reduce.py:97-105` (it does not redact-and-pass — decisive for Q5). Literature: Q1
mutation testing is well-founded (DeMillo/Lipton/Sayward 1978; diff-scoped probing at Google,
Petrovic & Ivankovic ICSE-SEIP 2018) BUT ≤3 mutants is NOT a "mutation score" (undefined
denominator); Q4 replaying the AUTHOR's own check is REPRODUCTION, not verifier independence
(IEEE 1012) → rename the metric; N-version voting CUT (Knight & Leveson: correlated failures).

**Cross-lens verdicts:**

| cand | validity | architecture | cost | security | net |
|---|---|---|---|---|---|
| Q2 risk-tier selection | keep (observe→enforce sound) | keep-w/-ch (reuse `_classify_sink`, NOT evaluate()/intake_triage) | **keep, build FIRST (cost allocator)** | **keep, build first (fail-closed: unknown→medium)** | **KEEP, #1** — pure fn consuming the dangling `security['new']`; a cost allocator, zero new exec surface |
| Q5 QA capsule | keep-w/-ch (testimony unless bound to Q4) | keep (schema-only) | keep (~0 cost; cap size, handles-not-bodies) | keep-w/-ch (collect WITHHOLDS secrets → carry a handle to a pre-scrubbed artifact, not inline) | **KEEP** — schema-only capsule + `rerunCmd`; handles not bodies; foundation for Q4/Q1 |
| Q3 provenance record | keep-w/-ch ('agentic-debt' = coinage → label exploratory; aligns SLSA/in-toto/SSDF) | keep (one add_entry, optional fields) | keep-w/-ch (ship view only after backfill proves it's queried) | keep-w/-ch (payload = handles + commit sha, never raw output; add tamper-evidence) | **KEEP-CHANGES** — one `records.add_entry` at finalize; handles+sha payload |
| Q4 oracle-replay | keep-w/-ch (REPRODUCTION not independence → rename) | keep-w/-ch (consume Q5's `rerunCmd`; scope to reviewPolicy) | keep-w/-ch (doubles exec; subprocess replay, tier-gated by Q2) | keep (author-declared cmd = untrusted exec surface) | **KEEP-CHANGES, LATE** — reproduction integrity; on the shared oracle runner |
| Q1 mutation-probe | keep-w/-ch (≤3 mutants ≠ "mutation score") | keep-w/-ch (never mutate the LIVE tree; gate runtime risk) | keep-w/-ch (cap mutants+runtime; finalize-time; honest 'skipped') | keep-w/-ch (untrusted-command exec surface) | **KEEP-CHANGES, LAST** — clean-worktree mutation, capped, honest exit-classes |
| Q6 formal/N-version | park; **CUT N-version** | park | park (each violates budget) | park | **PARK; N-version CUT** |

**Unanimous-ish build order:** **Q2 → Q5 → Q3 → (build ONE allowlisted isolated-worktree oracle
runner) → Q4 → Q1.** Cross-cutting: define the `exitClass` enum ONCE (in `result_contracts`) —
Q1/Q4/Q5 all use it or they drift.

## Phase 5 — Portfolio & backlog

Deterministic-first held: Q2 is a pure classifier over an already-computed signal (a cost
allocator, not adder); Q5/Q3 are schema/ledger extensions; Q4/Q1 are the only executing items
and the critique forced them onto ONE shared, allowlisted, isolated-worktree oracle runner
(untrusted-command containment) and to LAST. The governing corrections: **fail-closed**
(unknown diffs → medium tier), **handles-not-bodies** (the collect boundary withholds secrets,
so evidence is a handle to a pre-scrubbed artifact, never an inline snippet), and **honest
naming** (≤3 mutants is not a "mutation score"; replaying your own test is reproduction, not
independence). Portfolio → the **Code quality roadmap** section in `docs/IMPLEMENTATION_BACKLOG.md`
(CQ.1–CQ.6), each row = named gap + a verified seam + the metric it moves + ship/defer/PARK.

**Ship spine:** CQ.1 risk-tier gate selection (Q2, build first, consumes the dangling
security-baseline `new`) · CQ.2 QA evidence capsule + `rerunCmd` (Q5, handles-not-bodies) ·
CQ.3 provenance record (Q3, one add_entry). **Deferred, on the shared oracle runner:** CQ.4
oracle-replay / reproduction integrity (Q4) · CQ.5 mutation-probe (Q1, capped, clean-worktree).
**PARK:** CQ.6 formal verification; N-version voting CUT.
