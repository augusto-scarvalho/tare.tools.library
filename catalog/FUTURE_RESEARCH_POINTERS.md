# Future Research Pointers — Historical Corpus Crosswalk

> These are **RESEARCH pointers**, not automatically CURRENT gaps, TARGET architecture, or implementation authorization. They are preserved so later chats can rehydrate unfinished or adjacent lines of inquiry. Before implementation, reconcile against current Git, ADRs, SPECs, BDDs, gates, and code.
>
> **v0.16 note:** this curated historical list is now an input surface to the [Research Frontier Registry](../frontier/FRONTIER_INDEX.md). The registry preserves each pointer origin and lifecycle without replacing this historical crosswalk.

## 1. Workflow and procedural systems

- **Workflow lifecycle semantics** — desired vs observed state, terminality, revisions/GraphPatch, structured concurrency, cancellation, retry, resume, replan, reconciliation.
- **Workflow Compiler as query optimizer** — logical vs physical plans, cost-to-trust, adaptive reoptimization, receding-horizon planning.
- **Formal workflow semantics federation** — Statecharts/SCXML, Petri/WF-nets, GSM/CMMN, HTN, constraint models as projections rather than competing kernel ontologies.
- **Procedural memory and workflow evolution** — trace mining, process mining, AFlow/SkillOpt-like optimization, deterministic compilation of recurring procedures.
- **Causal workflow learning** — counterfactual replay, off-policy evaluation, selection bias, attribution and compiler regret.

## 2. Reliability, effects, and durable runtime

- **Durable runtime qualification** — compare Temporal, Restate, DBOS and other backends using the same tare-owned conformance pack.
- **Effect Torture Lab** — commit-then-drop-reply, duplicate delivery, stale observer, cancel/commit race, failed compensation, supersession and ambiguous completion.
- **Authority freshness / fencing** — historical Permit validity vs present commit eligibility, lease epochs, CAS/project revision and stale-owner protection.
- **Partial observability and active sensing** — POMDP/Value-of-Information approaches for deciding when reconciliation needs more evidence.
- **Operational effect accounting** — materiality, settlement, multi-effect transactions and independently observable postconditions.

## 3. Assurance, audit, and evaluator metrology

- **Evaluator metrology** — sensitivity, specificity, calibration, drift and fitness-for-purpose of judges, scanners, humans and agent reviewers.
- **Meta-assurance / protected held-outs** — independent tests of the tests, mutation testing, random re-audit and anti-reward-hacking design.
- **Evidence reuse and invalidation** — deterministic evidence reuse, freshness, applicability, provenance and EvidenceFamily independence.
- **Community Lab / distributed falsification** — challenge-central / evidence-local models inspired by ecosystem regression testing and federated evaluation.
- **Control effectiveness** — distinguish control design, implementation, operating coverage and actual reduction of material risk.

## 4. Governance and constitutional questions

- **Constitutional governance** — root authority, mandates, delegation, amendment, emergency authority, non-retroactivity and contestability.
- **Decision rights vs capability vs authority** — legitimate right to choose desired state, execution permission, accountability, responsibility and assurance.
- **Governance debt** — stale waivers, ownerless controls, policy conflicts, approval fatigue, cargo-cult compliance and ineffective controls.
- **Risk aggregation** — portfolio/systemic risk across many individually low-risk actions, vendors, datasets and resources.
- **Policy / waiver / deprecation lifecycle** — proposed→ratified→effective→challenged→amended→deprecated→retired with explicit evidence and expiry.
- **Operating posture / governance regime** — incident- or error-budget-driven freezing of evolution, vendors or capabilities without rewriting history.

## 5. Routing, reputation, and economics

- **Causal routing attribution and OPE** — propensity logging, route regret, counterfactual evaluation and delayed outcomes.
- **Exploration without incumbent lock-in** — minimum opportunity, bounded exploration, requalification and reputation decay.
- **Resource governance and scheduling** — priority/fairness across projects, GPUs, budgets, human attention and production incidents.
- **Capability/context economics** — deferred schemas, tool discovery, semantic waste, token budgets and marginal value of information.

## 6. Runtime, interoperability, and identity

- **Identity, trust, and federation** — workload identity, tare↔tare trust, delegated credentials and attestations while keeping Authority tare-owned.
- **Temporal interoperability** — upgrades as boundary compatibility; architecture epochs, migrations, replay and pinned protocol/adapter versions.
- **Portable capability components** — WASM Component Model/WIT, explicit imports/exports and plugin isolation.
- **Semantic fidelity at boundaries** — qualified semantic loss across MCP, A2A, CLI, HTTP, OS backends and remote runtimes.
- **Runtime capability evidence levels** — declared→rendered→loadable→enforced→effective, preserving the Kimi/Antigravity false-green lesson.

## 7. Context, memory, and project understanding

- **Context governance** — object/dependency-aware compaction, folding, GC, safe rehydration and vendor-neutral session lifecycle.
- **Project Model / SpecGraph as planning substrate** — deterministic facts, provenance, impact graph and task-specific context compilation without becoming Authority.
- **Cross-project learning / negative transfer** — global priors, local posteriors, applicability, project archetypes and conservative knowledge transfer.
- **Executable system reconstruction** — infer semantics/procedures from legacy NLU, state machines, BPM/RPA, logs and observed journeys.

## 8. UX / Experience Plane

- **Interaction-aware UI generation and testing** — executable state/transition inference and state coverage, not screenshot fidelity alone.
- **Semantic visual regression** — explain and localize UI differences before repair.
- **Contextual confinement for reference/browser agents** — least privilege, taint, prompt-injection resilience and trajectory safety.
- **Creativity, seeding and fixation** — staged/diverse inspiration and explicit diversity budgets.
- **Operational originality and provenance** — multi-source proximity, common conventions and defensible abstention thresholds.
- **Preference learning with uncertainty** — personal taste vs brand identity, decay, disagreement and poisoning.
- **Workflow-level UI safety** — harmful outcomes composed from individually benign tool/action steps.
- **Dual-audience interfaces** — human-friendly plus stable machine-consumable CLI/TUI/REPL contracts.
- **Causal UX outcomes** — link aesthetics and interaction changes to task success, trust, retention and business outcomes.

## 9. Local models and empirical harness evaluation

- **Harness-dependent agentic benchmarking** — separate model capability from harness contribution and quantization effects.
- **Robust repeated-measures experimentation** — paired tasks, multiple seeds/runs, confidence intervals, failure taxonomy and delayed outcomes.
- **Local inference qualification** — consumer-GPU resource headroom, quantization sensitivity, tool-calling reliability and long-context behavior.

## 10. Cross-disciplinary research bridges

- Cybernetics and control theory for observability/controllability/stability.
- High Reliability Organizations and resilience engineering for near misses, recovery and operating posture.
- Computational immunology/ecology for quarantine, diversity, tolerance and systemic risk.
- Organizational learning and double-loop learning for changing governing assumptions instead of only fixing runs.
- Mechanism design for incentive-compatible agent/vendor ecosystems.
- Metrology and psychometrics for trustworthy measurement of agentic systems.

## Rehydration rule for future chats

When a pointer is reopened: (1) locate the historical source/lineage; (2) identify the current canonical architecture epoch; (3) classify ADOPT / ADAPT / RETIRE / OPEN; (4) refresh scientific evidence separately; (5) produce a new dated research edition; and only then (6) propose ADR/SPEC/BDD/Implementation Packets.

## Research Knowledge Substrate / scholarly data enrichment

- bitemporal epistemic graph and architecture-epoch queries;
- source identity resolution and version-family reconciliation;
- selective claim/evidence extraction and contradiction graphs;
- active curation / Value of Information;
- RO-Crate/JSON-LD export qualification;
- CiTO/DataCite/PROV mapping;
- claim-to-code/SWHID traceability;
- retraction/correction watchers with downstream impact propagation;
- human cognitive interoperability for research graphs;
- calibrated LLM-assisted curation.
