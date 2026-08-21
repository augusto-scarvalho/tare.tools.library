# TOTAL Coverage Backlog for the Reference Article (Manuscript v1.6)

Exhaustive sweep of `docs/research/sources/adaptive-project-oriented-multi-agent-harness-architectures.md` (3,218 lines, §§1–15 + appendices A–I) → every actionable item in the article mapped to the REAL state of the repo. Owner request 2026-07-18: “break this entire article down into a huge backlog — what we have already done, what we have not done, what goes to research.”

**Method:** six Sonnet extractors (disjoint manuscript slices, extraction blind to repo) + Fable overseer consolidation cross-checking the adoption round (`harness-reference-architecture-adoption.md`, C1–C16/N/S/E/A), DECISIONS D008–D011, experiment registry EXP-1..19, milestone records, LOOP QUEUEs 1–6. The adoption round was SELECTIVE reading (what closes critical gaps); this is COVERAGE (nothing in the article is left without a line). It supersedes the selective round where they conflict.

**Status legend:**

| status | meaning |
|---|---|
| ✅ done | mechanism delivered with evidence (commit/spec/check) |
| 🟡 partial | slice delivered; missing remainder named |
| ⬜ open | buildable today without research; LOOP QUEUE candidate |
| 🔬 research | needs research/experiment round before building |
| 📏 rule | discipline adopted as living law (playbook/spec/gate), not an artifact |
| 🚫 counter-signal | article says DO NOT build; registered as guard |
| ⛔ rejected | rejected by our counter-evidence (recorded decision) |
| 🅿️ parked | parked with named revisit trigger |
| — n/a | outside our envelope (single tenant, local, two vendors) |

## §3 — Conceptual foundations

| ref | item | status | evidence / next step |
|---|---|---|---|
| §3.1 | Ownership: one owner per task | ✅ done | SPEC-149 ownership epoch (75ccda1) + pid-lock dispatch + gate hold |
| §3.1 | Explicit handoff vs agent-as-tool | 📏 rule | subagent contract + WORKER_RESULT; transfers through versioned briefs |
| §3.1 | Role taxonomy | ✅ done | 9 `.claude/agents/` profiles with S2 ceiling + Codex mirrors (L17 413965a) |
| §3.2 | Harness metamodel H=⟨I,C,P,R,W,X,S,M,O,E⟩ | 📏 rule | maps 1:1 to `.harness/` architecture (descriptive; no new artifact) |
| §3.3 | Four degrees of workflow dynamism | 🟡 partial | static+selected ✅ (profiles/composer); generated/runtime-edited 🅿️ (SF-4: only with evidence of need) |
| §3.4 | Separate MAPE-K / inner-outer loops | ✅ done | SPEC-109 anti-Hive invariant (C9 aligned in round) |
| §3.5 | Versioned operational envelope | 🟡 partial | route tuple C13 (L9 8732dbb) + risk tiers; missing single versioned envelope doc → ⬜ cheap candidate |
| §3.5 | Indeterminate state → deny | ✅ done | N1 receipts (CE.1): no valid receipt ≠ success; escalation on unknown |
| §3.5 | Predictability profile Π | 🔬 research | composite metric; prerequisites noise floor (L13 ✅) + trace completeness (L4 ✅); round to define five components on our corpus |
| §3.5 | Metric constructs (autonomy, governance, route churn, context footprint, delegation economy, contention, trace completeness…) | 🟡→**DESIGNED R4** | measured context footprint (CE.2), delegation economy (OB.2), trace completeness (L4), regret (EXP-17 probe); R4 preregistered measure-only formulas for route churn/CTS/Π-lite/recovery and named missing state for regret/ECE/A_ctx. See `construct-metrics.md` |
| §3.5 | Risk tiers R0–R3 | ✅ done | L1 (fba2fe2) + `riskTier` in dispatch emit (L4); R3 pinned unreachable at current scale |
| §3.5 | Project Context Profile per run | ⬜ open | have project.json + model cards; missing per-target profile in article form — cheap through SPEC-110 targets |
| §3.5 | Transfer compatibility predicate | 🅿️ parked | trigger: second real production target |
| §3.5 | Route tuple r (9 fields) | ✅ done | C13/L9 pinned in delegation records |
| §3.5 | Effort labels not comparable across vendors | 📏 rule | vendor model cards; L17 explicitly does not map Claude effort to Codex |
| §3.5 | Resource manifest per parallel node | 🟡 partial | HARD footprints in briefs + write choreography; missing typed per-worker manifest in workflow.json |
| §3.5 | Manifest conservatism (only expands) | 📏 rule | review ritual: change outside footprint = revert |

## §4 — Critical synthesis of the state of the art

### §4.1 Context, instructions, and experimental discipline

- Harness pinned as experimental treatment → 📏 D008 + EXPERIMENT_METHODOLOGY with noise blocks and pinned snapshots.
- Context ≠ enforcement → ✅ C14, SPEC-137 gate, protected files, PreToolUse hooks.
- Effective Constitution Compiler → 🅿️ parked as over-engineering at this stage; multi-tenant trigger.
- Deny-overrides precedence → 🟡 protected-files + deny hooks exist; no formal precedence compiler.
- Auto-generated context harm → 🚫 counter-signal; C6 makes curated minimal CONTEXT.md living law. Never generate it via LLM.
- Context minimization with claim expiry → 🟡 budget policy exists; lifecycle/valid-until (N6) deferred until first stale claim misleads a run.
- Relevance compression / LongLLMLingua → ⛔ rejected for now: EXP-1 head+tail measured and reverted because it lost more decisive lines; retest only with enriched corpus.
- Context diet → ✅ SPEC-118 v6 tool-schema trim, measured −2,670 tokens/turn.
- Matched-budget single-agent baseline → 🔬 EXP-15 ACTIVE; dedup/convergence measured, real matched-budget arm still missing.
- Explicit delegation briefs → ✅ overseer playbook plan-brief template (footprint/decisions/verify).
- Confirmatory 4×2 context experiment → 🔬 future large round; prerequisite EXP-16 evidence loss.
- Separate billed-token vs logical-byte ledgers → 🟡 token-audit + CE.2; logical bytes still research, tied to A_ctx.

### §4.2 Routing

- Learned/LLM router now → ⛔ rejected; C4 + counter-signal 1: simple rule/kNN comparable, SPEC-144 remains rule+floor.
- Route-outcome ledger + regret → ✅ N4 + L7 durable route ledger + EXP-17 probe.
- Deterministic filtering stage → ✅ `deterministic_floor` + rule-of-two S6 (raise-only).
- Task classifier → ✅ SPEC-144 tier-1 router.
- Calibration/abstention → 🟡 escalation ledger exists; no router calibration measurement yet, feeds EXP-17.
- Hysteresis / anti route-churn → ⬜ cheap, but measure churn first.
- Counterfactual logging → 🟡 route ledger stores candidates; missing unchosen routes + propensity.
- Per-step effort routing (Ares) → 🅿️ trigger: measured cost pressure in long sessions.
- C3VR gated fallback ladder → 🟡 failover chains + escalation; missing explicit “abstain/escalate effort before model.”
- Exploration banned in R2/R3 → 📏 rule.
- Co-failure ceiling β_C → ⛔ honestly rejected: no oracle + role-differentiated workers; EXP-15 measures co-detection instead.

### §4.3 Workflows

- Typed workflow IR + compiler checks → 🟡 DW.2 IR and schema/budget/secret/permission checks exist; cycles/reachability not relevant to current restricted graph forms; compensation parked.
- Search-generated workflows (AFlow/EvoAgentX) → 🚫 counter-signal until M1/M2 are mature; otherwise misevolution.
- Trajectory-based model scheduling (EvoRoute) → 🅿️ trigger when one model dominates wave cost.
- Lightweight intensity scheduler → 🅿️ same trigger as per-step effort.
- Progressive dynamism escalation → 📏 composer = selected; generated/runtime-edited requires evidence under D008.

### §4.4 Multi-agent topology and execution

- Topology taxonomy → ✅ map-reduce, fork-join, multi-vendor rooms, native Codex fork-join (EXP-19/D009).
- Evidence envelope per agent → ✅ WORKER_RESULT + oracleEvidence; loss measured in EXP-16.
- Lease + fencing epoch → ✅ SPEC-149 single `workflow_update` chokepoint.
- Single committer + idempotency + external-effect receipt → ✅ N1 receipts + merge choreography + SF-5b.
- CRDTs / formal coordination avoidance → — n/a at current scale.
- LLM does not authorize commit → 📏 SPEC-137 + owner gates + C12 approval digest.
- Topology by stage → ✅ D010 parametric width + independent critique waves + decide inbox.
- Dynamic topology reconstruction per round → 🅿️ multi-tenant/scale trigger.

### §4.5 Human interaction and effective autonomy

- Single façade + inspectable workers → ✅ gatekeeper + rooms + `[live rooms]` + decide inbox + task cards.
- Compact state account → ✅ U2 L0 takeover card + plan HUD.
- Task-scoped interaction profile → 🟡 headless governance + postPlanMode prefs; dynamic task profile parked.
- Evolving local rules (Hedwig/ZORO) → 🔬 ties to N6 claim lifecycle and memory research.
- Action guards + approval digest → ✅ C12 closes TOCTOU in decide inbox.
- Fine lifecycle authorization (SAGA) → 🅿️ multi-tenant trigger.
- “Hide until failure” unsafe → 📏 visible lifecycle states U1; “disappeared from chat is not a state.”
- Effective autonomy = min(desire, policy, evidence) → 📏 non-waivable owner gates; containment over fatigue.

## §5 — Proposed reference architecture

### §5.1–§5.3 planes and invariants

The article’s ten planes map largely to existing repo concepts: control (`project.json`+hooks+gates), routing (SPEC-144), workflow compiler (DW.2), runtime (async+SPEC-148), capability (executors+SPEC-113), trajectory (events+records), experimental (SPEC-116+methods), interaction (panel/rooms), evolution (SPEC-109). Runtime-plane gap was **DESIGNED in R2** as harness-owned sandbox SB-1/2/3; constitution compiler remains parked.

DGIOTS / formal transition kernel stays 🅿️ parked; current DW.2 IR + deterministic gates are the lite version. The pre-execution deterministic policy point is **vendor-dependent**: Claude hooks honor deny ✅; Codex hooks are advisory and containment comes from native sandbox S3 ✅; open HTTP models have none → harness-owned sandbox ⬜.

Article invariants map as follows:
- final deny + pre-action authorization → 🟡 due open-model gap;
- proposer ≠ approver → ✅ workers never commit, overseer reviews, owner gates;
- replay before persistence → 🟡 deterministic gate/probes but no formal replay kernel;
- kernel changes human-only → ✅ protected files + hook + OS lock;
- unique ownership → ✅ SPEC-149;
- handoff evidence contract → ✅ WORKER_RESULT + M1 handoff budget;
- hard budgets outside model context → ✅ enforced in plan/start;
- risk-proportional gate → ✅ R0–R3 + rule-of-two + owner gates;
- memory→policy only by promotion pipeline → 🟡 D008 exists, memory lifecycle deferred;
- sensitive-log discipline → ✅ secret scan/redaction + name-only records;
- replay classes → ✅ L3 `exact|approximate|external`;
- experiment discipline / no auto-promotion / frozen design / causal-claim care → ✅ D008 + L18 methods + live preregistration;
- deterministic reducer + fail-closed rule collision → 🅿️ formal DGIOTS body; current gate is deterministic;
- receipt-gated effect truth → ✅ N1/CE.1;
- UI cannot inflate authority; controls are typed events → ✅ GUI-writes-no-state + allowlist + approval digest.

### §5.4–§5.9 coordination, adapters, lifecycle, interaction

- Session coordinator ≠ root of trust → 📏 façade coordinates; gates/owner retain authority.
- 12 stable adapter boundaries → 🟡 capabilities.json + SPEC-113 cover hooks/MCP/skills/agents; cheap missing accounting-semantics disclosure.
- Capability delegation contract → ✅ briefs carry footprint/tools/verify/budget/return schema.
- Return = evidence delta, never transcript → ✅ bounded WORKER_RESULT + OUTPUT_CAP + S4.
- ECA signed compiled constitution → 🅿️ parked; existing version is precedence across protected-files/hooks/specs.
- Ownership machine with lease + two-phase transfer → 🟡 epoch/recovery done; explicit two-phase transfer absent, trigger on first transfer incident.
- Runtime-only reclamation → ✅ `_recover_stale_holds` refuses live pid.
- Concurrency by resource semantics → ✅ isolated worktrees + conditional merge + single committer + write choreography.
- Effect lifecycle + outbox/idempotency keys → 🟡 receipts/records exist; formal outbox currently n/a due rare effects + single committer.
- Crash points + reconciliation → 🟡 gate-hold recovery, scenario forensics, breaker, unknown-state escalation.
- Recovery metrics → 🔬 construct-metrics round.
- Interaction modes Assist→Orchestrator → 🟡 current rooms/panel/composer cover guided/delegated/orchestrator de facto.
- Progressive disclosure L0–L3 → ✅ takeover card / plan HUD / task cards+queue / evidence drill-in.
- Typed attention inbox + batching → ✅ decide inbox + blast-radius escalations.
- Approval state machine + single-use + invalidation → ✅ C12 digest + SLO/expiry + mismatch refusal.
- Durable `interaction_profile` → 🅿️ multi-tenant trigger.
- Plane table as minimum contract + tests per plane → 🔬 proposed self-assessment round mapping gates/scenarios to §5.9 + App F.

## §6 — Self-correction, project memory, governed self-evolution

- 11-class failure taxonomy + symptom router → 🟡 SPEC-126 covers part; align to all 11 classes.
- Recovery utility + no repeat without new evidence → 🟡 breaker/maxRounds and `--force-round` diagnosis; formal utility remains research.
- Correction modes: self-critique ≠ evidence; tool feedback = evidence → 📏 C8 review/oracle/gate ritual.
- Seven memory layers with trust rules → 🟡 layers exist de facto; per-layer trust rules need cheap documentation.
- ContextLedger → 🅿️ A_ctx deferred; CE.2 proxy exists.
- Context metrics (F_logical, A_ctx, D_ctx, precision/recall, evidence loss) → 🔬 EXP-16 active; rest construct-metrics.
- Memory lifecycle candidate→validated→active→challenged→expired → 🔬→**DESIGNED R2/R3**: N6 design uses scope-matched trigger anchored to Git HEAD SHA ∩ diff + provenance firewall + measure-only shadow ledger; enforcement remains owner-gated. GM-1..6 in `memory-context-management.md`.
- Memory poisoning never becomes policy → ✅ untrusted-derived marks + D008 + anti-Hive.
- Four-condition adversarial memory eval → 🔬→**DESIGNED R3** with GM-5 shadow challenge ledger.
- Seven-layer memory trust rules → 🟡→**DESIGNED R3** via GM-3 provenance firewall (`active_memory.authority < signed_policy`).
- Constrained ProjectRoutingProfile/bandit → ⛔ rejected for now pending EXP-17 corpus.
- Shadow priors + drift to shadow-only → 📏 D008.
- Evolution ladder levels 0–5 + candidate registry → ✅ SPEC-109 + experiment registry + intake + decisions; kernel level 5 protected+owner.
- Promotion pipeline + delayed monitoring → ✅ SPEC-116 doors + reviewBy + doctor `experiment-overdue`.
- AHE prediction before observation → ✅ preregistration is living practice.
- Full EDC → 🅿️ current EDC-lite = method library + registry + noise floor + Taguchi.
- Search vs inference separation → 📏 method library.
- Default α=.05, power=.80, δ_Q/δ_C/δ_L/δ_V, ECE≤.05 → ⬜ cheap, valuable promotion defaults.
- Eight promotion requirements + staged rollout + rollback triggers → 🟡 core pieces exist; sequential/alpha-spending only if experiment volume grows.
- No self-modification of evidence/rollback → ✅ anti-Hive + protected files + proposer≠approver.

## §7 — Governance, formal methods, security

- Deny in protected directories → ✅ protected-files hook + OS lock + `apply_patch` parser building block.
- Approval-gated sensitive flow secret→egress → 🟡 SEC.1 pre-egress + scrubbing exist; general egress remains declare-only until harness-owned sandbox.
- Combination limits on tools → ✅ S6 rule-of-two (2 of 3 untrusted/sensitive/external → escalate).
- Delegation cannot escalate privilege → ✅ env allowlist + sandbox tiers + spawn economy.
- Independent validator before merge → ✅ review ritual + SPEC-137 + oracle mutate.
- Cumulative cost/agent limits → ✅ token budgets + maxWorkers + delegation ledger.
- Proposer does not approve own proposal → ✅.
- PATH policies / temporal obligations → 🟡 o1/o3/o4/o5 covered; o2 `secret_read → never egress until declassified` still lacks taint tracking and belongs to sandbox design.
- Formal methods (Petri/TL/types/refinement) → 🅿️ with DGIOTS; current layer uses scenario/property behavior + mutation.
- Eight verifiable properties → 🟡 safety/non-bypass/separation/termination covered; liveness via watchdog/timeout; formal proofs parked.
- Policy mutation testing → 🟡 code mutation exists; policy mutation (deny guards, epoch spoof) open extension to red-team fixture.
- Statistical estimate never overrides deny → 📏 OB.3 anomaly card advisory-only.
- Ten trust zones, repo content UNTRUSTED → ✅ trustTier + untrusted-derived marks + seed provenance + prompt-injection posture.
- Ten-layer defense stack → 🟡 substantial coverage; harness-owned sandbox designed R2 is missing core for open models/egress.
- Rule of Two → ✅ S6.
- CaMeL trusted-control/untrusted-data separation → 🟡 full realization = harness-owned sandbox.
- Task-bearing adversarial eval (AgentDojo etc.) → 🔬 continuous red-team; today point fixtures.
- Seven-adversary threat model + prevention/detection/response/owner coverage → 🟡 cheap gap: residual-risk register per threat.
- SLSA/in-toto → — n/a until harness distribution becomes product concern.
- Data classification + non-exfiltration flow invariant → 🟡 secret scrub/vault/redaction exist; formal per-item classification parked.
- Approval = comprehension + real chance to reject; anti-fatigue → ✅ typed decide inbox + digest + expiry/SLO + containment-over-fatigue.
- Invalid approval forms (blanket/retroactive/self/no expiry) → ✅ C12+L2 close all four.
- Approval-service metrics → ⬜ cheap decide-inbox volume/latency/override stats.
- Human oversight studies → — n/a to current envelope.

## §8 — Provenance, observability, interoperability

| ref | item | status | evidence / next step |
|---|---|---|---|
| §8.1 | ATP typed event, causal DAG, append-only | 🟡 partial | events.jsonl + N2 append-only class + quarantine; explicit parent IDs open; signature/hash-chain parked |
| ir1 | immutable events, correction by supersession | ✅ done | N2 + G3a record supersession |
| ir6 | orphan event quarantine | ✅ done | N2 CE.8 security alert/failure survive wipe |
| ir8 | trace completeness by risk tier | ✅ done | L4 doctor check 9 + riskTier in emit |
| ir9 | model-call usage reconciliation | 🟡 partial | delegation ledger + token audit; per-call field open |
| ir2-5,10-14 | remaining integrity rules | 🟡 partial | merge/failover/decision refs exist; full cluster in self-assessment |
| §8.2 | declared replay classes | ✅ done | L3 |
| §8.2 | one-variable counterfactual replay | 🔬 research | candidate EXP over frozen workflow |
| §8.3 | MCP boundary; A2A | 🟡 / n/a | MCP declared; no A2A use case |
| §8.3 | adapter capability matrix + conformance suite | 🟡 partial | capabilities.json; suite joins self-assessment |
| §8.4 | native/emulated/degraded/unsupported support states | ⬜ open | cheap, useful vocabulary for capability cards |
| §8.4 c1-c14 | 14 adapter conformance tests | 🔬 research | applicable subset in self-assessment; ESH covers c2 partially |
| §8.4 | three-lane cross-vendor evaluation | 🔬→**DESIGNED R5 = EXP-20 proposed** | 3 lanes without pooling, split-plot vendor whole-plot, matched observed-token budget, Codex native gap as EMULATED; owner-gated measurement |

## §9 — Scientific evaluation and experimental program

The bulk of §9 is the ARTICLE’s research program (academic benchmarks, human studies A–L, hierarchical models). We adopt the DISCIPLINE, not the whole program.

- Experimental configuration tuple; no single benchmark sufficient → ✅ C13 route tuple + D008.
- Matched-budget baseline mandatory for multi-agent claims → 🔬 EXP-15 active, missing matched-budget arm.
- Baseline families → 📏 future reference; many currently out of envelope.
- Public benchmarks → — n/a; our frozen tasks are deterministic scenarios/fixtures.
- Frozen task snapshot + development-data exclusion → ✅ deterministic scenarios + frozen WFs.
- Factor classes control/noise/hard-to-change/nuisance/prohibited → 🟡 L18 has Taguchi/screening; formal typing cheap addition to methodology.
- ≥5 repetitions / simulated power; discovery/confirmation/promotion partitions → 🟡 preregistration exists; floor/partitions open.
- Metric families → 🔬 some measured (regret, evidence loss, noise floor, Δ_m); CTS cheap; rest construct-metrics.
- β_C → ⛔ honestly rejected.
- Hierarchical/split-plot/confidence sequences → — n/a until experiment rate is much higher.
- Local noise floor + published negative results → ✅ L13 + living practice.
- Full reproduction package → 🅿️ external publication/multi-org trigger.
- Oracle hierarchy O1–O5, LLM judge never sole oracle → ✅.
- Double registration agent-reported vs oracle-observed → ✅ CE.1/N1.
- Counterfactual replay degrees; only 1–2 sustain causal claim → 📏 method rule.
- TCO + lexicographic safety-first rule → 🟡 cost ledger exists; cheap methodology declaration open.
- Human/large simulator studies A–L → — n/a except Study G ≈ EXP-15/16 and Study K feeding self-assessment.

## §10 — RQs and falsifiable hypotheses touching us

- H1 hybrid router < regret → 🟡 SPEC-144 rules+floor, EXP-17 regret; adaptive phase owner-gated.
- H4 unique ownership reduces conflict/rework → ✅ internal incident evidence.
- H6 separate two loops prevents persistent mutation → ✅ SPEC-109 anti-Hive.
- H7 executable enforcement > prose → ✅ C14 + Codex finding strengthens need for correct substrate.
- H14 curated minimum context ≥ generated context → ✅ living law.
- H15 small diverse catalog ≥ large correlated catalog → 🔬 if catalog pressure arises.
- H16 governed memory lifecycle > append-only → 🔬 memory round.
- H17 external evidence correction > self-critique → 📏 ritual law.
- H19 durable ledger + receipts eliminates duplicate/unknown effects → ✅ N1 + dispatch/stale-hold fixes.
- H20 differences below noise floor do not replicate → ✅ L13.
- H21 state grading ≠ self-report → ✅ CE.1.
- H24–H29 EDC family → 🟡 first live Taguchi instance; full EDC parked.
- H30 effort labels not vendor-equivalent → ✅.
- H31 ranking inversion between normalized and native lanes → 🔬 EXP-20 designed.
- H32 per-step effort controller → 🅿️ cost trigger.
- H35 scoped delegation ≥ transcript inheritance → ✅ multiple measured mechanisms.
- H36 trajectory reduction without evidence loss → 🔬 EXP-1/EXP-16.
- H37 resource-semantic concurrency prevents stale/conflict → ✅ worktrees + choreography + epoch.
- H38 semantic repair advisory, deterministic validator commits → 🟡 EXP-18 shadow detector is instance.
- H39–H46 AHHI/DGIOTS → mostly n/a/parked; App I invariants already living law where they match.

## §11 — Architectural quality, trade-offs, maturity

- Ten quality attributes → 📏 rubric for self-assessment.
- ATAM 1–24 scenarios → 🔬 direct input to self-assessment; several already likely pass.
- M0–M7 cumulative maturity → ✅ D008 internal frame; D011 product version parked; current ≈ solid M2–M3, partial M5, embryonic M6.
- Evidence scale 0–3 per capability → ⬜ cheap column for self-assessment.
- Two-rater/multi-org validation → — n/a today.
- SDK/runtime/protocol vs harness coverage matrix → ✅ supports “harness engineering” business category.

## §§12–15 — Discussion, roadmap, threats, conclusion

- Seven anti-patterns for when NOT to use multi-agent → ✅ D010 + EXP-15 operationalize them.
- Ownership transfer + durable state + envelopes → ✅ briefs/WORKER_RESULT/records.
- Self-regulation ≠ sovereignty; verifiable improvement > change rate → 📏 anti-Hive + D008.
- Repo machine-readable for agents → ✅ specs+gates+Graphify+records.
- Façade cannot erase independent review / false consensus → 📏 reduce preserves conflicts + sourceWorkerIds.
- P1–P28 principles → ✅ most are living law; P12 diversity-by-failure and P19 reconciled ledger remain open/research.
- Program phases 0–10 → 📏 positioning ruler: we are roughly phases 0–6 “lite”; 7–10 are academic program.
- Validity threats + mitigation bundles → ✅ subset: noise floor, D-level labeling, preregistration, frozen corpus; cheap gap = residual-risk register.
- Limited assurance claim + residual-risk register → ⬜ one state file + doctor advisory.
- Central principle “probabilistic where judging, deterministic where limiting” → ✅ already thesis of architecture; external validation.

## Appendices A–I

- App A living-review extraction form → n/a; equivalent is research playbook + records.
- App B full evidence envelope → 🟡 WORKER_RESULT covers claims/artifacts/validations; cheap add costs + approval refs; signatures parked.
- App C typed evidence graph → 🅿️ records ledger + doc-find are lite form; scale trigger.
- App D constitution compilation → 🅿️ with ECA; deny-overrides already real in enforcement.
- App E preregistration + evidence partitions → 🟡 registry covers hypothesis/baseline/criteria/reversal; cheap factor typing + discovery/confirmation partitions.
- App F sixteen conformance suites → 🔬 backbone of proposed self-assessment; F17/18 “suite failure caps maturity dimension” adopted as rule.
- App G closure criteria for bounded-control thesis → 📏 reference; G5 third-party decision reconstruction is north star for records.
- App H EDC selection triggers + evidence grades 1–4 → ⬜ cheap vocabulary addition to methodology/registry.
- App I normative AHHI-DGIOTS profile → 🅿️ formal kernel; 8 of 11 final invariants already living law and should be documented in self-assessment.

## Rollup

| status | approx. items | reading |
|---|---:|---|
| ✅ done | ~78 | article core (ownership, receipts, enforcement, envelopes, tiers, approval, noise floor, anti-Hive, minimal context) already exists in repo |
| 📏 rule | ~24 | discipline adopted as living law |
| 🟡 partial | ~38 | slice delivered, rest named |
| ⬜ open | ~16 | cheap buildables, direct LOOP QUEUE 7 candidates |
| 🔬 research | ~18 | need round/experiment before build |
| 🅿️ parked | ~17 | trigger recorded, mostly multi-tenant/scale/formal kernel |
| ⛔ rejected | 4 | learned router; head+tail compression; β_C; §6.3 bandit for now |
| 🚫 counter-signal | 3 | generated context; auto-generated workflow; append-only memory |
| — n/a | ~12 | outside envelope |

## Proposed research rounds

Ordered by value × unlock:

1. **Conformance self-assessment** (§5.9 + App F 16 suites + ATAM 1–24 + §11.3-c scale 0–3). Question: what fraction of article’s minimum contract do our gates/scenarios ALREADY prove, and where are real gaps? Product: suite×evidence matrix 0–3; gaps become intake. Internal, no web, ~2 focused workers.
2. **Harness-owned sandbox design round** (§5.9 runtime plane, §7.4 s5, CaMeL, requirement from Codex investigation). Question: what vendor-agnostic fs/proc/net containment at spawn covers open models and reinforces Claude/Codex? Product: SPEC through NEW door + `apply_patch` parser as building block. **P0.**
3. **Governed memory** (§6.2 + H16 + four-condition adversarial eval). Refine `memory-context-management.md` lifecycle/trust/eval; N6 trigger remains for enforcement.
4. **Construct metrics** (§3.5 + §9.5): route churn, CTS, Π-lite, observable autonomy/governance. Product: 2–3 measure-only probes + preregistered definition round.
5. **Three-lane cross-vendor / EXP-20**: harness fork-join vs native Codex fork-join vs governed hybrid on SAME task class and equal budget.

## LOOP QUEUE 7 candidates — cheap open items

- C1 decision constants + lexicographic rule + evidence grades + factor typing → EXPERIMENT_METHODOLOGY + registry field.
- C2 residual-risk register + doctor advisory.
- C3 native/emulated/degraded/unsupported capability states.
- C4 WORKER_RESULT costs + approval refs.
- C5 decide-inbox metrics.
- C6 CTS from delegation ledger.
- C7 trust rules by memory layer.
- C8 experiment-overdue advisory was already SHIPPED and removed as phantom item.
- C9 route-loop hysteresis — only after churn measurement; R4 formula preregistered.
- C18 measure-only route churn probe.
- C19 measure-only Π-lite probe.
- C20 recovery probes (orphaned work, time-to-resume, provenance continuity, recovery-point error).
- C10 typed resource manifest per worker in workflow.json.
- C11 single versioned operational-envelope doc.
- C12b per-call usage reconciliation.
- C13b align SPEC-126 failure patterns to 11 classes.
- C14b policy mutation red-team fixture.
- C15b causal parent ids in events.
- C16b accounting-semantics disclosure in executor card.
- C17 ATAM table-test checklist for the 15 “unknown” R1 scenarios.

## R1 increment — self-assessment executed (2026-07-18, D012)

Round 1 COMPLETED via NVIDIA (`docs/research/conformance-selfassessment.md`; WFs `...215453` + follow-up B3 `...220210`). One-line result: **score 2 (implemented+internally tested) across ~70% of minimum contract; score 3 in NOTHING; five named holes are the already parked ECA, hash-chain, formal privacy, interop conformance plus one favorable correction (F15 promotion = 2).**

- App F rollup: 11 suites score 2; 5 suites score 1 (F1, F12, F13, F15→2 corrected, F16).
- §5.9/I.8 planes: most 2; gaps P5 (per-call accounting → C12b) and I10 formal parked.
- ATAM: 9 likely-pass, 15 unknown → C17; zero confirmed fail.
- F17/18 cap rule adopted: internal M-frame confirmed M2–M3; raising requires named F1/F12 slices, not average.
- New research: crash injection at adapter boundary (A13/§5.7) → candidate fixture, enters R4 recovery design.

# ENTIRE BACKLOG EXECUTION ORDER (architect, 2026-07-18)

Owner: derive more research, insert it into backlog, then order the ENTIRE backlog for most efficient execution — no feature before dependencies; do not prioritize work that would become much faster after the right prerequisite tasks.

## Part 1 — New items derived from R1–R5

### Enablers

| id | item | unlocks | source | size |
|---|---|---|---|---|
| **E-ROUTESCORES** | persist router `scores` already emitted into route-ledger row + normalized `predictedP` | ECE + route regret + RF.1 phase 2 | R4 | S |
| **E-SCOPETAG** | `scopeTag` (paths/deps referenced by memory) per memory item | governed-memory track GM-1/2/5, N6, scope match | R3 | S |
| **E-UNIQTOK** | token count per UNIQUE item in `context_digest` | A_ctx + context recall + ContextLedger + true CE.2 amplification | R4 | S |
| **E-3LANE** | 3-lane test instrument: frozen task set + stdlib oracle + gap table | EXP-20 + EXP-15 matched-budget | R5 | M |
| **E-EFFECTID** | effect-id/idempotency-key in external-effect records | duplicate effect + compensation metrics + effect lifecycle | R4 | M |

### Tasks closing score-1 R1 gaps

- **T-HASHCHAIN** — hash chain + signatures on critical events → App F F12 1→2.
- **T-ADAPTERCONF** — adapter conformance suite + C16b accounting semantics → F16 1→2.
- **T-CAUSALPARENT** — C15b causal parent IDs → §8.1 DAG + enables counterfactual replay.

### New experiments

- **EXP-21** proposed — deterministic crash injection at adapter boundary (A13/A6).
- **EXP-20** proposed — three-lane harness vs native Codex.

### New research rounds

- **RD-U** — what is harness utility function `U(route,outcome,cost)`? Unlocks regret + ECE.
- **RD-CRASH** — deterministic crash injection at adapter boundary on Windows? Unlocks EXP-21.
- **RD-TAINT** — untrusted-data taint / CaMeL, especially `secret_read` never egresses. After Q7-1.
- **RD-ECA** — does ECA-lite compiled precedence pay at our scale? Trigger: second real precedence dispute.

## Part 2 — Backlog phases by dependency

### PHASE 0 — real near-bugs + cheap enablers

Overseer correction: three inherited near-bugs were ALREADY SHIPPED (path hygiene, hidden Windows spawn helper, target gate env filter). Actual Phase 0 work:

4. **C1** constants + `evidenceGrade` — experimental-governance foundation.
5. **E-ROUTESCORES** — scores already exist, persist them.
6. **C3** capability support states — enabler for EXP-20 and sandbox manifest/F16.

### PHASE 1 — security P0

7. **Q7-1 harness-owned sandbox SB-1/2/3 (SPEC-151)** — extend existing `sandbox_spawn` (SPEC-148 with `risk_tier`, Windows `fs_confine_nt` via icacls, Job Object caps) to open-model HTTP worker + manifest + honest egress. `/verify` on real Windows.
8. **C2 residual-risk register** consuming Q7-1 result.

### PHASE 2 — measure-only probes

9. C18 route churn → prereq C9.
10. C6 CTS.
11. C19 Π-lite + C20 recovery.
12. C5 decide-inbox metrics.
13. E-UNIQTOK → A_ctx probe.

### PHASE 3 — governed memory, rescoped

No governed memory-item store exists today; `ui_memory` is read-only snapshot and auto-memory is runtime-written. Therefore E-SCOPETAG cannot be “field in existing store.” First committable artifact must bootstrap minimum record:

14. **GM-5 shadow-challenge ledger (measure-only)** including minimum item registry + `scopeTag`; measure items that WOULD be challenged by each commit, zero enforcement.
15. **GM-3 provenance firewall** when governed retrieval exists; owner-gated enforcement.

### PHASE 4 — trajectory/adapter hardening + instrument

17. **T-HASHCHAIN**, **T-CAUSALPARENT/C15b**, **T-ADAPTERCONF+C16b**, then **E-3LANE**.

### PHASE 5 — controls justified by measurement

19. **C9 hysteresis DEFERRED with trigger**: C18 measured route churn ~zero (transient/empty route-ledger corpus). Building control now would violate measure-before-control. Revisit on first churn measurement above L13 noise floor.
20. Whatever Phase 2 proves valuable, same signal trigger.

### LOOP QUEUE 7 CLOSED 2026-07-19

Phases 0–4 delivered (14 items, 13 kept delegations ~1.66M tokens). Remaining are owner-gated + N-* design dependent on owner decision + C9 deferred by measurement.

### Research status

RD-U ✅ complete (D021 weighted-linear U) → regret/ECE buildable measure-only. RD-CRASH ✅ complete (D022 hybrid injector) → EXP-21 enabled. RD-TAINT ✅ complete (D023 non-forgeable envelope at secret-scan seam) → closes o2 with buildable probe, enforcement owner-gated+security review. Only RD-ECA remains behind second-precedence-dispute trigger.

## New items derived from owner decisions D013–D017

- **N-AUTHCHAIN (C2-v2)**: typed chain of decision/approval responsibility `{actorType,user|worker|overseer, identity, at, sessionRef?}`; M.
- **N-SECREVIEWER**: `security-reviewer` agent profile + human ratification flow; M.
- **N-TRUTHRECON**: truth-source reconciliation engine across code/docs/history/third parties; L research→spec.
- **N-RACEMODE**: opt-in race-mode workflow topology; EXP-20 validates; M.
- **N-VENDORCREDIT**: vendor quota/credit remaining + scarcity-weighted U; M.

### N-TRUTHRECON decomposition (round #3, 2026-07-19)

`truth-reconciliation-round.md` and detailed `truth-reconciliation-implementation-plans.md`.
- **N-TRUTHRECON-PROBE / EXP-22** already built: measure-only divergence count among four sources; hashes/counts only, never content.
- **N-TRUTHRECON-CORE** owner-gated: pure two-tier PrecedenceResolver (authoritative=git+records; advisory=specs+vendor) + ReconciliationRecord with fact/winner/losers/rule/tier/degraded/absent/inputHashes/time/subject.
- **N-TRUTHRECON-TRUST**: absent-source side channel and vendor-doc untrusted input hardening; inherits GM-3 provenance firewall.
- **N-SCANNER-FP**: secret-scan `openai-style-key` false positive matching `sk-` inside “task-slug”; word-boundary fix, owner-gated due security path.
- Performance pipeline parked until EXP-22 measures volume.

### N-COMPACTION (2026-07-19)

Four-wave convergence: A_ctx watermark+hysteresis, tiered GC, measure-first. Detailed plans in `compaction-implementation-plans.md`.
- **N-COMPACTION-CFP / EXP-23**: measure fill% / canary recall / latency / cost / cache hit / compaction events and outcomes. Never compacts.
- **N-COMPACTION-CTRL**: A_ctx×role×task trigger + hysteresis + boundary snap; keep/summarize/drop tiers; resummarization depth 1; checkpoint + deterministic validation. Owner-gated after EXP-23.
- **N-COMPACTION-SECRET**: secret tier never summarize/persist; integrates RD-TAINT.

### N-PTC — Programmatic Tool Calling

Detailed `ptc-implementation-plans.md`.
- **N-PTC-PROBE / EXP-24** measure-only traditional vs emulated-PTC chain under matched budget.
- **N-PTC-ENGINE** harness_tools + pause/resume loop + code extraction + AST gate + filtered return, all executors routed through our sandbox; owner-gated after EXP-24 + security review.
- **N-PTC-TAINT4** fourth taint sink = sandbox stdout/stderr; extends D023 + lethal-trifecta invariant.
- **N-PTC-CONFORMANCE** capability/supportState + PTC token scope + no-amplification (stub set ⊆ declared tools).
- **N-TOOLSEARCH** frontier: tool-search/RAG over tool schemas; can be tested independently of PTC engine.

### N-U — utility function

D021. `U = w_q·Q·τ − w_c·C·S − w_t·T` pure over route ledger → measure-only regret probe (EXP-17), with reverted=0.5 calibration. Routing-driving U is owner-gated; variance/Sharpe term deferred until per-route corpus exists.

### N-CRASH — deterministic crash injection

D022. Hybrid injector: cooperative `HARNESS_CRASH_AT` plus Job Object for hang, deterministic counter, worker-entry guard, real Windows. EXP-21 measures duplicate effect/orphaned work/time-to-resume.

### N-TAINT — taint / CaMeL

D023 and prerequisite for PTC.
- **N-TAINT-PROBE** measure would-block count for tainted values reaching sinks; reuse secret_scan; never enforce.
- **N-TAINT-ENVELOPE** non-forgeable harness-injected source stamp at three origins.
- **N-TAINT-SINKS** fail-closed enforcement on prompt/persisted/log + fourth PTC stdout sink; rate-limited break-glass; owner-gated security.
- **N-TAINT-CAMEL** control-plane capabilities through trust tiers + GM-3, not full runtime per-value IFC.

### Classic non-article backlog

CE.2/CE.3/OB.1/OB.2 verified already shipped. Open groups remain P1 terminology/security baseline; P2 workflow/security/quality/Codex/UI/records/workspace/MCP wiring; P3/parked wiki/docs/consolidation/PyO3/UX and deferred CE/DW/SEC/CAP tasks.

## Why this order

1. **Enablers cost an afternoon and pay for weeks.** E-ROUTESCORES unlocks regret+ECE; scope tagging unlocks governed memory; E-3LANE serves two experiments.
2. **Sandbox looked greenfield and is NOT** — `sandbox_spawn` (SPEC-148) already has tier+icacls+Job Object. Recon changed Q7-1 from “build L from zero” to “extend M.”
3. **Measure before control** (C18→C9, GM-5→enforcement, A_ctx→CE.7): control without evidence is exactly the anti-pattern this research condemns.
4. **Owner gates and research stay behind prerequisites, never ahead** — regret does not enter queue until U exists; EXP-21 does not run before crash-injection design. This is literally “do not create a feature before its dependency is ready.”
