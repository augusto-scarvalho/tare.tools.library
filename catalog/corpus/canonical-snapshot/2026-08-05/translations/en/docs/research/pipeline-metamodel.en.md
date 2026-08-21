# Research Round — Pipeline Metamodel (Short Double Diamond)

Opened: 2026-08-04. Orchestrator: overseer (Fable). Origin: `pipeline-metamodel` row (P1/L, mechanized-audit-pipeline arc item 6; owner ordered ROUTE research first).

## Question

Should the delivery-pipeline blueprint BY workflow type (inline, delegated lane, fork-join, research round) become a canonical object (`.harness/routing/pipeline-metamodel.json`) with derivations — (a) compiled playbook sections, (b) generated delivery bar, (c) conformance check — or is the value already covered by existing mechanisms (ritual-enforcement map + delivery-bar advisor + directive maps)?

## Success criteria

1. **One source of truth per piece of information.** If the object is created, decide what happens to the ritual-enforcement map (derived, retired, or scoped) — never two canons for “who enforces step X.”
2. **Declared direction.** Bottom-up (prose → mapping, directive-map style) vs top-down (object → compiled prose, SPEC-173 style) — with migration cost and drift risk for each direction.
3. **Every derivation has a named consumer** and a delta versus what exists today (explicit YAGNI test per derivation).
4. **Honest blast radius**: is the stage ladder parameterizable by type, or do N divergent types become a configuration swamp?

## Declared budget and width (D010)

- **FOCUSED** research (one shape decision; feature already sketched in the row) → width **2 workers PER wave** (perspectives: simplicity/YAGNI vs reliability/enforcement). Rationale: EXP-15 measured redundancy with five workers on a single theme; two are enough to stress directions per brief.
- **Human gate 2026-08-04: owner approved all 3 briefs** — one divergence wave per brief (A, B, C; width 2 each) + one seeded critique wave. Revised round budget: **≤200k tokens** (60% playbook gate per wave). `workflow token-audit` before every start.
- Experiment design (L18): N/A at this stage — output is a form decision, not a measurable claim; if a derivation is promoted, it receives a scenario (gate), not EXP.

## Phase 1 — Evidence (all [repo], collected 2026-08-04)

| claim | source | type | method | limitations | confidence | maturity |
|---|---|---|---|---|---|---|
| A top-down precedent exists in production: canonical object GENERATED from legacy sources, byte-identical frozen projections, drift check, playbook compiled by ONE assembler | `scripts/harness_lib/role_metamodel.py:1-40`, `playbook_compiler.py:1-25` (SPEC-173) | repo | direct reading | ROLE metamodel, not pipeline stages | strong | production |
| A bottom-up precedent exists in production: prose sources remain canonical, mapping declares enforcement by id-hash, gate fails an item without mapping | `scripts/harness_lib/security_directives.py:1-25` | repo | direct reading | security directives only | strong | production |
| Arc item 5 ALREADY delivers “every overseer-playbook step names who enforces it” — statuses hook/gate/leg/doctor/advisory/gap, `ritual-enforcement-map` gate, id = hash of step prose | `scripts/harness_lib/ritual_map.py:1-25` (a731198) | repo | direct reading | bottom-up: does not DERIVE playbook or delivery bar; scope = 2 overseer playbooks | strong | production |
| Delivery bar today is a hand-written advisory R1-R11 over staged surface; never blocks | `tools/hooks/delivery_bar_advisor.py:1-42` | repo | direct reading | rules have rule-specific logic, not merely “stage present” | strong | production |
| Runner workflow types are `map-reduce`/`fork-join` + profiles; row “types” (inline, lane, fork-join, research round) are DELIVERY-PIPELINE types one level above runner | `.harness/workflows/WORKFLOWS.md:5-15` vs `pipeline-metamodel` row | repo | direct reading | row taxonomy does not exist as an object anywhere | strong | production |
| No prior round/decision record exists for pipeline-metamodel | `records search` (empty) + `doc-find` | repo | search | — | moderate | — |

### Flow A — external state of the art (collected 2026-08-04 after gate, at owner request)

| claim | source | type | limitations | confidence | maturity |
|---|---|---|---|---|---|
| [web] SPEM (OMG) is widely used to MODEL software process but “lacks built-in enactment capabilities — no tool or process engine executes it”; it does not cover execution/monitoring; adoption is scattered. A descriptive metamodel without an ENGINE that executes it drifts from practice | ResearchGate “Software Process Engineering Metamodel (SPEM)”; scirp.org “Comparative Analysis BPMN vs SPEM”; omg.org/spec/SPEM/2.0 (primary) | paper/spec | academic analyses, not industrial measurement | moderate | validated |
| [web] Pipeline-as-code in CI (GitHub Actions/GitLab) WORKS as a canonical object — because the object is ENACTED by an engine (the YAML IS the pipeline, not a description); enforcement is automatic by construction | TechTarget “Pipeline as Code”; harness.io academy | docs/vendor | vendor/promotional sources | moderate | production |
| [web] PaC lesson: object complexity becomes “pipeline debt”; enforcement “is rarely binary” — deviation acceptable in dev may block prod (graded status is necessary) | Puppet “Policy as Code Beyond the Pipeline”; TechTarget | blog/vendor | promotional | preliminary | production |

### Flow A — comparative scientific literature (collected 2026-08-04, owner ordered comparison with scientific work)

| claim | source | type | year | method | limitations | confidence | maturity |
|---|---|---|---|---|---|---|---|
| [web] Original top-down thesis: “software processes are software too” — process encoded in executable language (process programming) should be central to software engineering | Osterweil, ICSE 9 (1987); “Revisited” ICSE 19 (1997), dl.acm.org/doi/10.1145/253228.253440 | paper | 1987/1997 | position + prototypes (Arcadia/Little-JIL) | research thesis, not empirical adoption study | strong (as thesis source) | conceptual demonstration |
| [web] The generation implementing that thesis (PSEEs: Marvel, SPADE, EPOS...) saw LOW industrial adoption; literature cites “lack of flexibility in software process modeling” as a primary cause and “the highly dynamic nature of the software process” as a documented reason for few commercial applications | Fuggetta et al., “PSEEs: A Brief History and Future Challenges”, Annals of SE (2002); “Comparative Review of PSEEs”, Annals of SE (2002); Matinnejad & Ramsin, IEEE ECBS 2012 | survey/review | 1997–2012 | comparative multi-system review | pre-DevOps era; academic systems | strong (3+ survey convergence) | validated |
| [web] Surviving rigidity required DEVIATION as a first-class citizen: formal deviation-tolerance model (accept/reject constraint violation during enactment); “without managing evolution during enactment, PSEEs are doomed to fail in adoption” | Cugola, deviation management (IEEE TSE 1998 / Springer); “Review of Detecting and Correcting Deviations on Software Processes” (2015) | paper | 1998–2015 | formalization + case studies | limited case validation | moderate | prototype→validated |
| [web] The scientific branch that SUCCEEDED for “declared vs practiced” is conformance checking (process mining): normative model × observed event log, alignment and deviation diagnosis — ex-post detection, not ex-ante prescription | van der Aalst, *Process Mining* (Springer, 2nd ed. 2016); “Process Mining in the Large” tutorial | book/paper | 2011–2016 | formal + mature tools (ProM, etc.) | BPM domain, not agent pipelines | strong | production |
| [web] Enacted pipeline-as-code measured at scale: 49K+ repos, 267K+ histories, 3.4M+ workflow versions (2019–2025) — median 3 workflows/repo, **7.3% of workflow files change PER WEEK**, ~3/4 workflow commits contain ONE change, mostly task configuration | Mazrae, Decan, Mens, Wessel, “An Empirical Study of the Evolution of GitHub Actions Workflows”, arXiv:2602.14572 / JSS 2026 | empirical paper | 2026 | large-scale mining | public OSS only | strong | validated |
| [web] Pipeline-object maintenance has real ongoing cost (“hidden costs of automation”; CI/CD bug fixing and improvement are major drivers); workflow complexity/heterogeneity/compliance is itself a research topic | arXiv:2409.02366 (~200 mature projects); arXiv:2507.18062 | empirical papers | 2024–2025 | mining + qualitative analysis | public OSS | moderate | validated |

### Flow A — bleeding edge, last 24–36 months

| claim | source | type | year | method | limitations | confidence | maturity |
|---|---|---|---|---|---|---|---|
| [web] LLM-agent workflow as a declarative OBJECT (DAG, “workflows as data rather than code”) in PayPal production: −60% dev time, 3× deployment speed, 50 DSL lines vs 500+ imperative — canonical object ENACTED by engine, in this repo’s exact domain | Daunis, “A Declarative Language for Building And Orchestrating LLM-Powered Agent Workflows”, arXiv:2512.19769 (Dec 2025) | industrial paper | 2025 | production case | single company; peer review unconfirmed | moderate | production |
| [web] RUNTIME enforcement through declared rules: lightweight DSL with trigger + predicate + enforcement mechanism per rule; prevents >90% unsafe executions in code agents with millisecond overhead — structurally similar to `check:`/`trigger:` vocabulary in this repo’s directive maps | Wang et al., “AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents”, arXiv:2503.18666 | paper | 2025 | multi-domain evaluation | benchmarks, not production | moderate | validated |
| [web] PROCEDURAL conformance of agent trajectories as trace verification (LTL): measure, enforce AND train process compliance in tool-using agents — conformance checking entering the agent domain | “AgentLTL: A Trace-Verification Framework...”, arXiv:2607.02599; PMAx arXiv:2603.15351 (EMMSAD 2026); MANTRA arXiv:2605.06334 | papers | 2026 | formal + benchmarks | preprint/tool-demo | preliminary | prototype |
| [web] Emerging “workflow fidelity” metric beyond task success: the pipeline FOLLOWED matters as much as outcome, measured by replay/alignment against normative model in agentic payments | “Beyond Task Success: Measuring Workflow Fidelity in LLM-Based Agentic Payment Systems”, arXiv:2605.06457 | paper | 2026 | replay/conformance | payments domain | preliminary | prototype |

**Frontier pattern (fact, not opinion):** all THREE forms contested in this round coexist in 2025–26 agent literature: (i) enacted declarative object, (ii) bottom-up enforcement rules with trigger/predicate (AgentSpec), (iii) ex-post trace conformance (AgentLTL/PMAx/MANTRA). None has won; (i) appears only when ENACTED by an engine, never as documentation from which other docs are derived. Added critique question: which of the three is isomorphic to what the row proposes, and what does the repo already have of each?

**Literature → briefs mapping (QUESTIONS for critique wave, not conclusions):**
- Brief A: is Osterweil→PSEE→rigidity-kills-adoption analogous to top-down here, or does the analogy fail because the object consumer would be a deterministic gate rather than humans? Is conformance checking (normative × observed) the scientific analogue of bottom-up mapping + gate, or a genuine third path (ex-post detection) distinct from both directions?
- Brief B: does the GitHub Actions finding (7.3%/week churn, small changes, task-config dominant) transfer to this repo pipeline (~3 measured changes/week)? Does it strengthen or weaken cutting derivations?
- Brief C: does Cugola deviation-tolerance imply that ANY type schema needs graded deviation status (does ritual_map advisory/gap vocabulary cover it?) — and do 2024–26 empirical maintenance costs calibrate the “config swamp”?

**Flow A synthesis (Define, revised):** the external discriminant is **enactment**: a canonical pipeline object works when an ENGINE executes it (CI-as-code) and fails as hand-synchronized documentation (SPEM). The row proposes a DESCRIPTIVE object (derives playbooks/delivery bar) — SPEM regime, not CI regime — independently corroborating the bottom-up verdict of waves A/B. Honest counter-case: if the harness someday ENACTS stages (`route --loop` already executes hard-coded stage choreography), the object would cease being description and become program — that is the external revisit trigger, alongside internal FINDING-010. PaC’s graded-enforcement lesson already exists in `ritual_map` vocabulary (advisory/gap).

**Central finding (Define):** the two precedents point in OPPOSITE directions, and the newly shipped ritual-enforcement map already occupies part of the territory. If a top-down object is created and COMPILES playbook sections, ritual-map ids (hashes of prose) begin tracking generated text — the mechanisms collide. The real decision is not “JSON or no JSON”; it is **direction + reconciliation**.

## Phase 2 — Briefs

### Brief A — direction and reconciliation
Problem: two canonical architectures coexist in the repo (bottom-up directive map, top-down SPEC-173). Which direction minimizes drift and migration cost for the pipeline, and what happens to ritual-enforcement-map in each?
Actors: overseer (consumes playbook), gate (enforces conformance), owner (audits diffs).
Constraints: never two sources of truth; SPEC-173-style migration requires frozen projections + drift check; mapping-file-only requires prose to remain canonical.
Success: one recommended direction with explicit, reversible reconciliation plan.

### Brief B — marginal value per derivation (YAGNI test)
Problem: what does the object deliver that ritual-map + delivery-bar + directive maps do NOT deliver today? For each derivation — (a) role-adaptable playbook sections, (b) generated delivery bar, (c) `spec_conformance`-style conformance check — name the concrete consumer and delta. Derivation with no delta = cut.
Actors: each named consumer. Constraints: R1–R11 have per-rule logic that a “declared stage” does not express; compiled playbook already exists through another path.
Success: derivation → consumer → delta → verdict (worth it/not worth it).

### Brief C — parameterization by type vs config swamp
Problem: is the ladder (route → brief → implement → verify → gate‖reckon‖mutate‖audit → commit → close-out) ONE pipeline with optional stages by type, or do four types diverge enough to become four hand-maintained pipelines? Maintenance cost of each form.
Actors: whoever edits the object whenever ritual changes. Constraints: the arc changed the pipeline three times in one week — overly rigid object becomes friction.
Success: recommended schema form with a concrete example of all four types.

## Human gate (Phase 2 → 3)

**STOPPED HERE for owner approval** before spending the Develop wave (research-divergence, width 2, budget above). Options: approve all three briefs, cut to A+B, or decide inline without wave (evidence already stresses the directions enough that the owner may judge directly and skip to Deliver).

## Phase 4 — Critique and operations (manual join, 2026-08-04)

Critique: WF-20260804-092656-940830, four cross-vendor critics (validity sonnet·xhigh, architecture nvidia·glm-5.2, cost nvidia·glm-5.2 — respawn after Gemini 401, row `gemini-compat-chat-401`; INV-1 vetoed Claude on retry —, security sonnet·xhigh). Zero security blockers.

**Join provenance:** WF reduce artifact silently EXCLUDED workers 002/003 (HTTP seats without `sourceFilesVerified` but with high findings — bug recorded `reduce-drops-repo-blind-highs`, P1). This join was performed by the orchestrator over all FOUR raw results; nothing was lost.

**What critique changed:**
1. (validity, high) 6/6 convergence of generation waves is **corpus-shaped**: same model + evidence PRE-FRAMED by orchestrator briefs. It does not invalidate the direction — cross-vendor critique (Sonnet+GLM) independently endorsed bottom-up — but lowers class: direction = **moderate-strong**, not “unanimous.” Positive control: numerical [repo] claims verified exactly.
2. (validity, high) Literature tables have asymmetric verification: arXiv:2602.14572 verified against primary source by orchestrator (numbers matched); PSEE/rigidity corroborated by 3+ surveys through search; remaining items = search snippets. Confidence classes adjusted to avoid conflating “source agreement” with “verified existence.” No round decision depends on a snippet-only claim.
3. (architecture, high) Wave C shape (base-ladder + overlays) **risks recreating the canonical object through the back door** → C3 operation downgraded to parked.
4. (architecture+cost, high) **Ex-post conformance over traces** (AgentLTL/PMAx/process mining) is a genuine third path not considered by generators — with uncosted observation infrastructure overhead. Becomes frontier bet.
5. (security, medium) Enforcement locators (`hook:`/`gate:`/`check:`/`trigger:`) in EXISTING maps are free-form self-attested text with no liveness check — stale pointer silently passes. Becomes its own task (valuable independently of this round).

**Operations by concept:**

| id | concept | operation | basis |
|---|---|---|---|
| C1 | Bottom-up direction: DO NOT create `.harness/routing/pipeline-metamodel.json`; playbook prose remains canonical | **kept** | waves A/B + architecture/cost critique; PSEE rigidity; no legacy machine taxonomy to consolidate; AgentSpec isomorphism with existing mechanisms |
| C2 | Derivations (a) playbook compiled from object, (b) generated delivery bar, (c) conformance check derived from object | **rejected** | YAGNI (wave B): zero/negative delta per derivation; R1-R11 irreducible; ritual-map already supplies the tooth of (c) |
| C3 | Sparse base-ladder+overlays form (wave C schema) | **parked** | direction-neutral but no consumer today + back-door risk (architecture critique); recorded for the day a consumer appears |
| C4 | Ex-post conformance of pipeline traces (workflow fidelity) | **frontier bet** | genuine third path (AgentLTL/PMAx/MANTRA, 2026); uncosted observation overhead; prototype maturity |
| C5 | Extend SCOPE of ritual-enforcement-map to other pipeline-defining playbooks (route/research/workflow) | **kept → task** | only surviving B/C delta: mechanism is source-generic; extension = RITUAL_SOURCES + mappings in same commit |
| C6 | Liveness check for enforcement locators in existing maps | **kept → task** | security critique finding; applies to shipped ritual-map + security-directive-map |

## Phase 5 — Deliver (portfolio)

- **core:** C5 (`ritual-map-scope-extension`), C6 (`enforcement-locator-liveness`)
- **contingency:** C3 (recorded form; activates IF a per-spawn consumer is born)
- **frontier bet:** C4 (trace conformance; no EXP — no measurable claim yet)
- **parked:** top-down canonical object — revisit triggers: (i) pipeline prose stable <1 structural edit/month (today ~3/week) AND ≥2 named per-spawn consumers; OR (ii) an engine begins to ENACT stages (e.g. generalized `route --loop`) — then object is program, not documentation (CI/PayPal regime, not SPEM)
- **rejected:** derivations (a)/(b)/(c) from a canonical object
- Canonical decision: `DECISIONS.md` **D056**. `pipeline-metamodel` row closes in this round.

## Traceability

| Evidence | Problem | Idea | Decision | Task |
|---|---|---|---|---|
| ritual_map/role_metamodel/security_directives [repo] + PSEE rigidity + AgentSpec [web] | colliding canonical directions | bottom-up, canonical prose | D056 | — |
| irreducible R1-R11 [repo] + zero delta per derivation | speculative derivations | cut (a)(b)(c) | D056 | — |
| B: “extend RITUAL_SOURCES” + 2/8 playbook scope | pipeline steps outside overseer lack enforcement tooth | extend map scope | D056 | ritual-map-scope-extension |
| security critique: stale locator silently passes | self-attested enforcement | locator liveness probe | D056 | enforcement-locator-liveness |
| AgentLTL/PMAx/MANTRA + workflow fidelity [web] | ex-post declared-vs-practiced conformance | trace conformance | D056 (frontier) | — |
| WF-092656 reduce excluded HTTP seats | compat-seat citizenship in reduce | single validator + honest summary | — | reduce-drops-repo-blind-highs |
