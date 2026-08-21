# Formal research plan

## Adaptive, governed, project-oriented multi-agent harnesses

**Provisional research title:**

> **Multi-Agent Harness Architectures with Project-Adaptive Routing, Dynamic Workflows, Self-Correction, and Self-Evolution under Deterministic Control**

**Protocol start date:** July 14, 2026.

The object of study is not simply a multi-agent framework. We are studying an intermediate layer between models, agents, tools, repositories, and users that simultaneously acts as:

- execution environment;
- agentic IDE;
- agent operating system;
- governance control plane;
- compiler of global and local instructions;
- workflow engine;
- evaluation and observability system;
- self-correction mechanism;
- controlled-evolution platform.

The central architectural hypothesis is:

> A harness can allow project-adaptive routing, workflows, and strategies without losing predictability, provided probabilistic intelligence operates inside an action space compiled and validated by deterministic policies.

---

# 1. Research objectives

## 1.1 General objective

Investigate, design, implement, and evaluate a multi-agent harness architecture capable of:

1. operating over different repositories;
2. combining global, organizational, local, and path-specific rules;
3. dynamically selecting overseers, agents, tools, models, and topologies;
4. building and modifying workflows during execution;
5. self-correcting unsuccessful executions;
6. learning project-specific patterns;
7. proposing evolutions of the harness itself;
8. preventing the adaptive layer from violating deterministic invariants;
9. producing traceability and evidence sufficient for audit;
10. working with multiple vendors and protocols.

## 1.2 Expected scientific outcome

The research should generate more than an implementation. It should produce:

- a taxonomy of harness engineering;
- a conceptual model;
- a reference architecture;
- a maturity model;
- a set of architectural patterns;
- an evaluation protocol;
- benchmarks and trajectory datasets;
- experimental evidence;
- a reference implementation;
- recommendations for industrial adoption.

---

# 2. Methodological strategy

The research should combine methods, because no single approach adequately covers literature review, artifact creation, and empirical validation.

## 2.1 Systematic Mapping Study

We will begin with a **systematic mapping study** to identify:

- research communities;
- terminology;
- trends;
- architectural approaches;
- datasets;
- benchmarks;
- gaps;
- relationships between historically separate fields.

The mapping is necessary because the relevant literature is scattered across multi-agent systems, workflow management, autonomic computing, reinforcement learning, software architecture, AI safety, coding agents, and empirical software engineering.

## 2.2 Systematic Literature Review

After the mapping, we will conduct smaller systematic reviews for specific questions, following primarily Kitchenham and Charters for software engineering. We will use PRISMA 2020 for transparency in reporting selection, remembering that PRISMA is primarily a reporting guideline and does not replace the methodological review protocol. ([legacyfileshare.elsevier.com](https://legacyfileshare.elsevier.com/promis_misc/525444systematicreviewsguide.pdf?utm_source=chatgpt.com))

The search should combine:

- queries in academic databases;
- backward snowballing;
- forward snowballing;
- searches by authors and groups;
- manual conference searches;
- periodic corpus updates.

Wohlin provides the methodological reference for snowballing; later studies indicate that hybrid strategies may recover more relevant work than a single search method. ([dl.acm.org](https://dl.acm.org/doi/10.1145/2601248.2601268?utm_source=chatgpt.com))

## 2.3 Design Science Research

Because we intend to build a technological artifact, the main creation axis will be **Design Science Research — DSR**.

The cycle will follow:

1. problem identification and motivation;
2. definition of solution objectives;
3. design and development;
4. demonstration;
5. evaluation;
6. communication.

These steps follow the Hevner tradition and the process proposed by Peffers. DSR is appropriate when knowledge is produced through the construction and evaluation of an artifact in its context of use. ([wise.vub.ac.be](https://wise.vub.ac.be/sites/default/files/thesis_info/design_science.pdf?utm_source=chatgpt.com))

## 2.4 Action research and case studies

The development of the harness itself will be used as the first longitudinal case: the harness will operate on external repositories and also on its own repository.

After that, cases with different properties will be used:

- multi-agent harness;
- smart-contract scanner;
- RAG system;
- SaaS application;
- small greenfield project;
- legacy project with incomplete tests.

Case studies are appropriate for studying contemporary phenomena in their real contexts, provided that protocol, units of analysis, data collection, and threats to validity are explicit. ([researchgate.net](https://www.researchgate.net/publication/220277640_Hst_M_Guidelines_for_Conducting_and_Reporting_Case_Study_Research_in_Software_Engineering_Empirical_Software_Engineering_14_131-164?utm_source=chatgpt.com))

## 2.5 Controlled experiments and quasi-experiments

For more bounded decisions, we will perform A/B or factorial experiments:

- LLM router versus deterministic router;
- static versus dynamic workflow;
- generalist versus specialized overseer;
- global learning versus project-level learning;
- one instance versus multiple agents;
- same model family versus heterogeneous models;
- self-correction without memory versus with memory;
- free evolution versus governed evolution;
- review by the same model versus independent model.

## 2.6 ATAM and architectural evaluation

We will apply the **Architecture Tradeoff Analysis Method** to identify risks, sensitivity points, and trade-offs among:

- autonomy;
- security;
- predictability;
- cost;
- latency;
- scalability;
- adaptability;
- auditability;
- interoperability;
- maintainability.

ATAM was created to evaluate architectures against quality goals and make explicit the interactions among competing attributes. ([sei.cmu.edu](https://www.sei.cmu.edu/library/architecture-tradeoff-analysis-method-collection/?utm_source=chatgpt.com))

## 2.7 Goal–Question–Metric

Each experimental objective should be decomposed using GQM:

```text id="sb8yrz"
Goal
  → Questions
      → Metrics
```

Example:

```text id="q2o681"
Goal:
Evaluate the effectiveness of the project-adaptive router.

Questions:
Does the router improve completion rate?
Does it reduce cost?
Does it increase route churn?
Does it generalize to new tasks?

Metrics:
task success rate
route regret
cost-to-success
reroute count
calibration error
out-of-distribution success
```

GQM was proposed as a systematic mechanism for defining and evaluating operational objectives through contextualized measurement. ([cs.umd.edu](https://www.cs.umd.edu/~basili/publications/technical/T89.pdf?utm_source=chatgpt.com))

---

# 3. Evidence hierarchy

The research should avoid treating a recent preprint, a vendor blog, and a seminal article as equivalent evidence.

| Level | Type of evidence | Main use |
|---|---|---|
| A | Standards, formal specifications, seminal papers, and broadly validated work | Foundations and constraints |
| B | Recent peer-reviewed papers, surveys, and reproducible benchmarks | State of the art |
| C | Recent preprints with code, datasets, or clear evaluation | Bleeding edge |
| D | Technical documentation and vendor engineering blogs | State of practice |
| E | Wikis, communities, posts, and individual experiences | Hypothesis discovery |

A relevant architectural claim should not be supported only by D- or E-level sources. Ideally, we will triangulate:

```text id="czsjw0"
academic foundation
    + recent experimental evidence
    + industrial implementation
```

We will also need to record:

- whether the work was peer-reviewed;
- whether code is available;
- whether a dataset is available;
- whether there is independent reproduction;
- benchmark size and representativeness;
- omitted costs;
- conflicts of interest;
- the difference between demonstration and production.

---

# 4. Interconnected map of research fields

```text id="c930ct"
Multi-Agent Systems
        │
        ├──► hierarchies, roles, and coordination
        │
Agent Routing ──────────────► overseers and model selection
        │                              │
        ▼                              ▼
Dynamic Workflows ─────────► workflow compiler/runtime
        │                              │
        ▼                              ▼
Autonomic Computing ───────► self-correction and MAPE-K
        │                              │
        ▼                              ▼
Self-Evolving Agents ──────► outer evolution loop
        │                              │
        ▼                              ▼
Policy as Code ────────────► deterministic control plane
        │                              │
        ▼                              ▼
Formal Methods ────────────► invariants and verification
        │
        ├──► security, trust zones, and permissions
        │
Context/Memory ────────────► project-level learning
        │
        ▼
Provenance/Observability ──► trajectories, evals, and audit
        │
        ▼
Empirical SE ──────────────► evidence and comparison
        │
        ▼
Harness Engineering ──────► reference architecture
```

---

# 5. Research tracks

## Track 1 — Foundations of agents and multi-agent systems

### Questions

- What constitutes an agent, worker, supervisor, and overseer?
- Which responsibilities should belong to each level?
- When should hierarchy, market, federation, or peer-to-peer coordination be used?
- How should beliefs, goals, commitments, and intentions be represented?
- What is the difference between an agent and a function wrapping an LLM call?

### Solid foundations

The work of Wooldridge and Jennings provides classic foundations for autonomy, reactivity, proactivity, and social interaction. The BDI architecture provides a language for representing beliefs, desires, intentions, and commitments, and can help separate observed state, desired goals, and plans actually committed to by the overseer. ([cs.ox.ac.uk](https://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/ker95.pdf?utm_source=chatgpt.com))

### State of the art

Study:

- orchestrator–worker;
- supervisor–specialists;
- agents-as-tools;
- handoffs;
- blackboard systems;
- hierarchical MAS;
- centralized versus decentralized coordination;
- role-based versus model-based coordination;
- error propagation;
- false consensus.

Recent surveys classify collaborative mechanisms by actors, structure, strategy, collaboration type, and protocol; a specific taxonomy of hierarchical multi-agent systems has also been proposed. ([arxiv.org](https://arxiv.org/html/2501.06322v1?utm_source=chatgpt.com))

### Bleeding edge

- hierarchies reconstructed during execution;
- reputation among agents;
- dynamic creation and removal of agents;
- specialized overseers triggered by stage;
- ad hoc topologies;
- co-evolution of capabilities and communication.

### Expected artifact

A **taxonomy of harness roles**, distinguishing:

```text id="3rnwzg"
Session Coordinator
Meta-Router
Overseer
Planner
Worker
Tool
Reviewer
Validator
Evolution Agent
Governance Authority
```

---

## Track 2 — Harness engineering and software agents

### Questions

- What belongs to the model and what belongs to the harness?
- How does the harness differ from an IDE, framework, and agent runtime?
- How should it represent a workspace?
- How should state be preserved across sessions and models?
- How should Codex, Claude Code, Copilot, and future agents be supported?

### State of practice

OpenAI describes the harness as the contract around instructions, tools, routing, output requirements, and validations; its improvement flow uses traces, feedback, and evals to guide changes. Anthropic also treats harnesses as an essential part of long-running work and has investigated the separation between stable interfaces and harness implementations that evolve with models. ([developers.openai.com](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop?utm_source=chatgpt.com))

### Research lines

- minimalist versus prescriptive harness;
- how much behavior should remain in the prompt;
- progressively loaded tools;
- resumable sessions;
- context ownership;
- long-horizon planning;
- checkpoints;
- rollback;
- worktree isolation;
- coordination of parallel agents over a repository;
- cross-vendor compatibility.

### Expected artifact

A formal definition and **harness metamodel**:

```text id="4defga"
Harness =
  Instructions
+ Capabilities
+ Policies
+ Runtime
+ State
+ Memory
+ Routing
+ Evaluation
+ Evolution
```

---

## Track 3 — Global, local, and project-specific instructions

### Questions

- How should global and local instructions be combined?
- Should conflicts be resolved by proximity, authority, or restrictiveness?
- Can natural-language instructions be considered policies?
- How should vendor-specific configurations be generated without divergence?
- How should directory-specific rules be handled?

### State of practice

Codex builds an instruction chain from global, repository, and directory files, giving precedence to more specific guidance. Claude Code distinguishes user, project, and local settings, but makes clear that `CLAUDE.md` is context and not enforcement; for effective blocking it recommends pre-tool hooks. GitHub Copilot also combines repository instructions with path-specific instructions. ([developers.openai.com](https://developers.openai.com/codex/agent-configuration/agents-md?utm_source=chatgpt.com))

### Topics

- constitution compiler;
- instruction precedence;
- deny-overrides versus specificity-overrides;
- canonical harness language;
- adapters for `AGENTS.md`, `CLAUDE.md`, and Copilot;
- semantic rules versus executable rules;
- conflicting-instruction detection;
- versioning;
- configuration signing and trust;
- workspace trust;
- path-scoped capabilities.

### Hypothesis to test

> Natural language should guide agents, while executable policies should constrain actions.

### Expected artifact

An **Effective Constitution Compiler** that generates:

- effective constitution;
- effective permissions;
- instructions by agent;
- path-scoped rules;
- gates;
- vendor-specific configuration.

---

## Track 4 — Multi-level routing

Routing should be decomposed into different problems.

```text id="tkq1en"
Workspace routing
Project routing
Overseer routing
Capability routing
Tool routing
Model routing
Reasoning-effort routing
Recovery routing
```

### Questions

- Single router or router hierarchy?
- Deterministic classifier, embeddings, LLM, or a combination?
- How should confidence and calibration be measured?
- When should multiple routers be consulted?
- How can route churn be avoided?
- How can the system learn without overfitting to the repository?
- How should multi-domain tasks be routed?
- How should cost, latency, risk, and availability be included?

### Consolidated base

RouteLLM studies routing among models using preference data and demonstrates the potential to balance cost and quality. More recent benchmarks, however, show that many sophisticated routers do not consistently beat simple baselines, that model recall remains a problem, and that indiscriminately increasing the ensemble has diminishing returns. ([arxiv.org](https://arxiv.org/html/2406.18665v4?utm_source=chatgpt.com))

### State of the art

- supervised routers;
- embedding-based routers;
- pairwise preference routing;
- quality-cost Pareto routing;
- cascades;
- difficulty estimation;
- contextual bandits;
- calibrated routers;
- policy-aware routing;
- budgeted routing;
- marginal-gain routing.

### Bleeding edge

- graph-memory routing;
- reasoning-aware routing;
- routing agents, not only models;
- joint selection of roles, models, and topology;
- routers using previous trajectories;
- project-specific routers;
- meta-routing;
- per-query selected agent architecture.

GraphPlanner extends routing to agentic environments with planning, memory, and multi-round cooperation. MaAS treats multi-agent architecture as a search space and selects query-specific systems. ([arxiv.org](https://arxiv.org/pdf/2604.23626?utm_source=chatgpt.com))

### Priority experiments

1. rules only;
2. Sonnet router;
3. rules + Sonnet;
4. rules + Sonnet + project priors;
5. router trained on trajectories;
6. contextual bandit;
7. router ensemble;
8. retrospective oracle.

### Expected artifacts

- `ProjectRoutingProfile`;
- internal routing benchmark;
- confusion matrix among overseers;
- route-regret model;
- hysteresis policy;
- fallback protocol.

---

## Track 5 — Static, dynamic, and adaptive workflows

### Questions

- When should a workflow be fixed?
- When should it be assembled before execution?
- When may it be modified during execution?
- How can soundness, termination, and cancellation be guaranteed?
- How should parallelism, join, retry, and compensation be modeled?
- Should the LLM generate workflow code or a declarative representation?

### Solid foundations

Workflow Patterns and Petri nets provide vocabulary and techniques for sequence, parallel split, synchronization, choice, loops, cancellation, and multiple instances. Petri nets also allow workflow properties to be analyzed rather than merely executed. ([vdaalst.com](https://www.vdaalst.com/publications/p108.pdf?utm_source=chatgpt.com))

### State of practice

LangGraph distinguishes workflows with predetermined paths from agents that dynamically define their own processes. Google ADK offers sequential, parallel, and iterative agents whose external flow may remain deterministic even when subagents use models. ([docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/workflows-agents?utm_source=chatgpt.com))

### State of the art

- declarative DAGs;
- state machines;
- durable execution;
- subgraphs;
- workflow templates;
- planner–executor;
- reflection loops;
- structured concurrency;
- event sourcing;
- compensating actions;
- deterministic replay.

### Bleeding edge

AFlow automates generation and optimization of agentic workflows. EvoAgentX includes evolutionary optimization of prompts, configurations, and topologies. Recent surveys distinguish static workflows, workflows selected before execution, and workflows dynamically changed during execution. ([arxiv.org](https://arxiv.org/pdf/2410.10762?utm_source=chatgpt.com))

### Expected artifact

A safe DSL:

```yaml id="7odsgl"
workflow:
  nodes: []
  edges: []
  gates: []
  invariants: []
  compensation: []
  termination: {}
```

And a compiler that checks:

- schema;
- types;
- cycles;
- dependencies;
- permissions;
- concurrency;
- budget;
- side effects;
- termination conditions;
- mandatory gates.

---

## Track 6 — Dynamic communication topologies

### Questions

- Who can talk to whom?
- Does the overseer need to receive every message?
- When should blackboard, broadcast, point-to-point, or pub/sub be used?
- How can evidence loss in long chains be prevented?
- How can communication cost be reduced?
- Should topology change by phase?

### State of the art

The literature already recognizes communication as a central problem rather than merely a detail of multi-agent architecture. ([arxiv.org](https://arxiv.org/html/2502.14321v3?utm_source=chatgpt.com))

### Bleeding edge

DyTopo reconstructs a sparse communication graph at every round. Guided Topology Diffusion formulates topology creation as graph generation conditioned on performance, cost, and robustness. TacoMAS explores online co-evolution of capability and topology, including adding and removing agents. ([arxiv.org](https://arxiv.org/html/2602.06039v1?utm_source=chatgpt.com))

### Hypothesis

> The optimal topology depends on the workflow stage, not only on the task's general class.

### Experiments

- star with overseer;
- hierarchical tree;
- mesh;
- blackboard;
- dynamic topology;
- bounded dynamic topology;
- learned topology;
- full communication versus referenced evidence.

### Metrics

- communication tokens;
- duplicated information;
- propagated error;
- convergence time;
- route churn;
- context dilution;
- robustness under agent failure;
- marginal contribution per agent.

---

## Track 7 — Autonomic computing and self-correction

### Questions

- What does it mean for an execution to self-correct?
- Which signals trigger diagnosis?
- How many attempts are acceptable?
- How do we distinguish a code, tool, model, context, or workflow problem?
- When should rollback occur?
- When should the issue be escalated?

### Foundation

The MAPE-K cycle organizes adaptation into:

```text id="azmty5"
Monitor
Analyze
Plan
Execute
Knowledge
```

This model has already been applied to adaptive workflows and proposed as a basis for self-adaptive LLM agents. ([wi2.uni-trier.de](https://www.wi2.uni-trier.de/shared/publications/2023_MalburgEtAl_MAPEK_Loops.pdf?utm_source=chatgpt.com))

### Application to the harness

```text id="98hb8z"
Monitor:
traces, tests, cost, progress, errors

Analyze:
failure classification and root cause

Plan:
retry, replan, reroute, model swap, rollback

Execute:
controlled corrective action

Knowledge:
trajectories, decisions, policies, experiences
```

### Expected artifact

A failure taxonomy:

- failure of understanding;
- failure of decomposition;
- routing failure;
- workflow failure;
- tool failure;
- model failure;
- context failure;
- implementation failure;
- validation failure;
- environmental failure;
- governance failure.

---

## Track 8 — Self-evolving agents and harness evolution

### Questions

- What can evolve?
- When does evolution occur?
- How is the candidate evaluated?
- How can reward hacking be prevented?
- How should delayed regressions be handled?
- How do we separate transient self-correction from persistent evolution?
- How can self-approval be prevented?

### State of the art

Recent surveys organize self-evolving agents around **what**, **when**, and **how** to evolve, covering model, memory, tools, prompts, architecture, and workflows. ([arxiv.org](https://arxiv.org/abs/2507.21046?utm_source=chatgpt.com))

EvolveR proposes a closed experience cycle. SEW investigates self-evolving workflows for code generation. EvoAgentX integrates different techniques for optimizing prompts and topologies. ([arxiv.org](https://arxiv.org/abs/2510.16079?utm_source=chatgpt.com))

### Bleeding edge

Work from 2026 discusses an **evolution control plane** that decides when to update weights or the harness itself based on production trajectories. Other work explores offline inner loops and outer loops with delayed metrics. ([arxiv.org](https://arxiv.org/abs/2607.01120?utm_source=chatgpt.com))

### Risks

“Misevolution” describes the case where the self-evolution process deviates from its objective and produces undesirable behavior. ([arxiv.org](https://arxiv.org/abs/2509.26354?utm_source=chatgpt.com))

### Proposed model

```text id="nol8gm"
Level 0 — no persistence
Level 1 — adaptation within a run
Level 2 — learning project preferences
Level 3 — changing workflows and agents
Level 4 — changing the router
Level 5 — changing the governance kernel
```

The higher the level, the stronger the requirement for:

- replay;
- evals;
- shadow mode;
- canary;
- independent review;
- human approval.

---

## Track 9 — Deterministic control plane and policy as code

### Questions

- Which invariants must never be decided by an LLM?
- How should global and local rules be compiled?
- How can we prove that a route is allowed?
- How should tools be controlled before execution?
- May policies change at runtime?
- How should policies be tested?

### Consolidated base

OPA separates policy decisions from application logic through a declarative language and its own APIs. It also includes testing mechanisms and applications in CI/CD pipelines. ([openpolicyagent.org](https://openpolicyagent.org/docs?utm_source=chatgpt.com))

### Rule categories

```text id="9104ve"
Invariants
Permissions
Prohibitions
Obligations
Gates
Budgets
Trust zones
Data handling
Routing constraints
Workflow constraints
Evolution constraints
```

### Bleeding edge

Recent work argues for authorization before tool calls and governance of the complete trajectory. A specific preprint on coding agents proposes that the control plane be deterministic and vendor-independent, but it still requires external validation and broader industrial results. ([arxiv.org](https://arxiv.org/html/2603.20953v1?utm_source=chatgpt.com))

### Expected artifact

```text id="id7s89"
Policy Decision:
allow | deny | require_approval | transform | constrain
```

Each decision should record:

- applied policy;
- version;
- input;
- outcome;
- justification;
- affected execution.

---

## Track 10 — Formal methods and verification

### Questions

- How should generated workflows be verified?
- How should safety invariants be represented?
- How should deadlocks, livelocks, and starvation be analyzed?
- How can we verify that a change does not reduce protections?
- How should temporal behavior be modeled?
- How far is applying formal methods economically justified?

### Topics

- Petri nets;
- temporal logic;
- model checking;
- finite-state machines;
- type systems;
- contracts;
- proof-carrying actions;
- theorem proving;
- property-based testing;
- runtime verification;
- deterministic replay.

### Research strategy

We will not attempt to formalize all intelligence. The focus will be to formalize:

- boundaries;
- states;
- transitions;
- permissions;
- side effects;
- invariants;
- promotion of changes.

The semantic content of the task may remain probabilistic.

---

## Track 11 — Security, trust, and governance

### Questions

- How does a malicious instruction in a repository affect the harness?
- How should prompt injection in documentation and code be handled?
- How can exfiltration through tools be prevented?
- How should trust zones be defined?
- How should the harness be protected when it works on itself?
- How should agents that generate tools be constrained?
- How can improper communication or collusion be detected?

### References

The NIST AI RMF organizes risk management around Govern, Map, Measure, and Manage; its Generative AI profile complements the framework with risks specific to these systems. ([nist.gov](https://www.nist.gov/itl/ai-risk-management-framework?utm_source=chatgpt.com))

OWASP maintains an initiative dedicated to agentic security and published the Top 10 for Agentic Applications for 2026. MITRE ATLAS provides a living base of adversarial tactics and techniques against AI systems. ([genai.owasp.org](https://genai.owasp.org/initiatives/agentic-security-initiative/?utm_source=chatgpt.com))

ISO/IEC 42001 should be included as an organizational reference for management and continuous improvement of AI systems, although it does not replace technical runtime controls. ([iso.org](https://www.iso.org/standard/42001?utm_source=chatgpt.com))

### Trust model to investigate

```text id="xeatgi"
External repository
Internal repository
Trusted project configuration
Untrusted repository content
Generated code
Generated policy
Harness core
Evolution subsystem
Human authority
```

### Mandatory principle

```text id="7wjnva"
proposal_agent != approval_authority
```

---

## Track 12 — Memory, context, and project-level learning

### Questions

- What should be stored per session, project, and organization?
- How should factual, episodic, and procedural memory be distinguished?
- When does an experience cease to be valid?
- How can previous errors be prevented from contaminating the router?
- How should obsolete experiences be forgotten?
- How can knowledge be shared without sharing sensitive data?

### Layers

```text id="ta5wpm"
Working memory
Session memory
Run state
Project memory
Cross-project memory
Experience store
Policy memory
Artifact history
```

### Topics

- context compression;
- selective recall;
- experience replay;
- trajectory summarization;
- temporal decay;
- semantic cache;
- negative experiences;
- confidence and provenance;
- memory poisoning;
- catastrophic forgetting;
- project embeddings;
- retrieval policies.

### State of practice

LangGraph, for example, treats short-term memory as a persistent part of thread state retrieved through checkpoints. Anthropic highlights compaction, note-taking, and multi-agent architectures as distinct strategies for long-running tasks. ([docs.langchain.com](https://docs.langchain.com/oss/python/concepts/memory?utm_source=chatgpt.com))

---

## Track 13 — Provenance, observability, and trajectory

### Questions

- What is the unit of observation: call, node, task, run, or session?
- How should decisions and artifacts be correlated?
- How should an execution be reproduced?
- How should evidence be stored without retaining sensitive content?
- How should dependency among decisions be represented?

### References

OpenTelemetry defines common semantic conventions for traces, metrics, and events and has been expanding conventions aimed at generative-AI operations. W3C PROV-O provides classes and properties for representing and exchanging provenance between systems. ([opentelemetry.io](https://opentelemetry.io/docs/specs/semconv/?utm_source=chatgpt.com))

### Event schema to investigate

```json id="l8g44u"
{
  "run_id": "...",
  "task_id": "...",
  "node_id": "...",
  "agent_id": "...",
  "model": "...",
  "route_decision": "...",
  "policy_decisions": [],
  "inputs": [],
  "outputs": [],
  "artifacts": [],
  "metrics": {},
  "parent_events": []
}
```

### Expected artifact

An **Agent Trajectory Protocol** compatible, where possible, with:

- OpenTelemetry;
- W3C PROV;
- MCP;
- A2A;
- internal eval formats.

---

## Track 14 — Evaluation of agents, workflows, and architecture

### Questions

- How should partial success be measured?
- How should two workflows with semantically different results be compared?
- How should an agent's marginal contribution be measured?
- How can we identify when a multi-agent system is worse than a single agent?
- How should long-duration tasks be evaluated?
- How should router reliability be measured?

### Current state

Agent evaluation remains a rapidly evolving area, especially for long-running, subjective, and multi-agent tasks. Google ADK notes that agent variability requires more than traditional tests; Anthropic also treats agent evals as a still-emerging field. ([google.github.io](https://google.github.io/adk-docs/evaluate/?utm_source=chatgpt.com))

### Proposed metrics

#### Outcome

- task success;
- acceptance rate;
- requirements satisfied;
- tests passed;
- regression rate;
- security findings;
- human rework.

#### Routing

- route accuracy;
- top-k recall;
- regret;
- calibration;
- churn;
- unnecessary escalation;
- fan-out waste.

#### Workflow

- node success;
- critical path duration;
- deadlocks;
- retries;
- replans;
- structural complexity;
- graph edit distance;
- cancellation correctness.

#### Economics

- tokens;
- calls;
- monetary cost;
- latency;
- cost-to-success;
- marginal gain per agent.

#### Evolution

- improvement over baseline;
- transferability;
- regression rate;
- rollback rate;
- time-to-detection;
- stability across versions.

#### Governance

- denied actions;
- bypass attempts;
- policy coverage;
- approval frequency;
- false positive/negative policies;
- trace completeness.

---

## Track 15 — Protocols and interoperability

### Questions

- How should agent–tool communication be separated from agent–agent communication?
- How should capabilities be discovered?
- How should versions be negotiated?
- How should large artifacts be transmitted?
- How should asynchronous tasks be represented?
- How should agents and models be swapped without changing the workflow?

### Protocols to study

MCP standardizes the connection of LLM applications to tools and context sources. A2A seeks interoperability among independent agents, including those built with different frameworks and vendors. ([modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2025-11-25?utm_source=chatgpt.com))

The following should also be studied:

- OpenAPI;
- JSON Schema;
- AsyncAPI;
- CloudEvents;
- OpenTelemetry;
- W3C PROV;
- OCI artifacts;
- Git;
- LSP;
- DAP.

### Architectural hypothesis

> MCP should primarily serve the agent–tool/context boundary; A2A or an equivalent internal protocol should serve the agent–agent boundary.

### Expected artifact

A stable interface layer:

```text id="u5f96n"
Agent Interface
Tool Interface
Artifact Interface
State Interface
Policy Interface
Evaluation Interface
```

---

## Track 16 — Software architecture and quality

### Questions

- Which quality attributes define a good harness?
- How should modifiability and portability across vendors be measured?
- How should accidental complexity be controlled?
- When is multi-agent architecture excessive?
- How should vendor lock-in be avoided?

### References

ISO/IEC 25010 provides a vocabulary for software product quality; we will use especially:

- functional suitability;
- performance efficiency;
- compatibility;
- reliability;
- security;
- maintainability;
- portability.

The 2023 version updates the quality model applicable to software and ICT products. ([iso.org](https://www.iso.org/obp/ui/en/?utm_source=chatgpt.com))

### Priority ATAM scenarios

1. replace Sonnet with another router;
2. disable a provider;
3. add a new protocol;
4. execute two thousand tasks in parallel;
5. modify the policy engine itself;
6. resume a run after a crash;
7. discover that project memory is contaminated;
8. revoke a tool during execution;
9. roll back an evolution;
10. reproduce a decision six months later.

---

# 6. Formal research questions

## Group A — Architecture

**RQ-A1:** Which components and responsibilities are required in an adaptive multi-agent harness architecture?

**RQ-A2:** Which separation between deterministic control plane and probabilistic intelligence plane produces the best balance between autonomy and governance?

**RQ-A3:** Which overseer and agent topologies are most appropriate for different task classes?

**RQ-A4:** Does a specialized overseer improve quality compared with a generalist supervisor?

## Group B — Routing

**RQ-B1:** Do LLM routers outperform rules and conventional classifiers in task routing?

**RQ-B2:** Do project-specific priors improve routing without reducing generalization?

**RQ-B3:** Which strategy reduces route churn and unnecessary escalation?

**RQ-B4:** Is it better to jointly select overseer, workflow, and model or execute separate decisions?

## Group C — Workflows

**RQ-C1:** In which tasks do dynamic workflows outperform static templates?

**RQ-C2:** Which representations allow workflows to be generated without losing verifiability?

**RQ-C3:** Do workflow modifications during execution improve failure recovery?

**RQ-C4:** How does communication topology affect quality, cost, and error propagation?

## Group D — Adaptation

**RQ-D1:** Which trajectory information is most useful for self-correction?

**RQ-D2:** Which separation between inner and outer loop reduces regressions?

**RQ-D3:** When should a transient adaptation be promoted to a persistent project policy?

**RQ-D4:** How can misevolution be detected and mitigated?

## Group E — Governance

**RQ-E1:** Which decisions necessarily need to be deterministic?

**RQ-E2:** Does policy as code reduce violations without excessively blocking legitimate tasks?

**RQ-E3:** Which mechanisms prevent the harness from approving changes to its own controls?

**RQ-E4:** How should global, local, and path-specific rules be compiled without ambiguity?

## Group F — Evidence and operations

**RQ-F1:** Which metrics best predict real success in coding agents?

**RQ-F2:** How should multi-agent workflows be evaluated without privileging only the final result?

**RQ-F3:** What minimum data is required for reproducibility?

**RQ-F4:** How should observability be balanced against privacy, cost, and volume?

---

# 7. Search protocol

## 7.1 Academic databases

- ACM Digital Library;
- IEEE Xplore;
- SpringerLink;
- ScienceDirect;
- Scopus;
- Web of Science;
- Google Scholar;
- arXiv;
- Semantic Scholar;
- dblp.

## 7.2 Conferences and communities

### Agents and AI

- AAMAS;
- AAAI;
- IJCAI;
- NeurIPS;
- ICML;
- ICLR;
- ACL;
- EMNLP.

### Software engineering

- ICSE;
- FSE;
- ASE;
- ESEM;
- EASE;
- SANER;
- MSR;
- ISSTA;
- ICSME.

### Systems and workflows

- BPM;
- CAiSE;
- Middleware;
- OSDI;
- SOSP;
- EuroSys;
- USENIX ATC.

### Security

- IEEE S&P;
- USENIX Security;
- ACM CCS;
- NDSS;
- ACSAC.

## 7.3 Initial search string

```text id="rn9ifv"
("LLM agent" OR "language model agent" OR "agentic AI")
AND
(
  harness OR orchestration OR router OR routing OR supervisor
  OR overseer OR "dynamic workflow" OR "workflow optimization"
  OR "self-evolving" OR "self-adaptive" OR "multi-agent"
)
AND
(
  governance OR policy OR deterministic OR guardrail
  OR repository OR coding OR software engineering
)
```

We will then create track-specific strings.

## 7.4 Inclusion criteria

- direct relationship to one or more RQs;
- sufficient description of the architecture or method;
- identifiable evaluation method;
- published in English or Portuguese;
- complete version accessible;
- identifiable date and version;
- for bleeding edge, preference for code or dataset.

## 7.5 Exclusion criteria

- use of “agent” only as a marketing term;
- opinion without architecture, method, or evidence;
- duplicate or earlier version without additional contribution;
- benchmarks without reproducible description;
- work focused only on a simple chatbot;
- production claims without minimally verifiable data.

---

# 8. Study extraction and coding

Each source will receive a record:

```yaml id="cx7aku"
study:
  title:
  year:
  venue:
  peer_reviewed:
  evidence_level:
  field:
  research_problem:
  architecture:
  routing_method:
  workflow_type:
  adaptation_type:
  deterministic_controls:
  models:
  datasets:
  baselines:
  metrics:
  results:
  threats_to_validity:
  artifacts_available:
  relevance_to_harness:
  replication_priority:
```

We will also build an **evidence graph**:

```text id="2m5nsk"
Paper
  ├── supports Claim
  ├── contradicts Claim
  ├── extends Method
  ├── uses Benchmark
  ├── implements Pattern
  └── evaluated by Experiment
```

This will allow interconnected syntheses rather than merely a linear bibliography.

---

# 9. Harness experimental program

## 9.1 Baselines

- single frontier agent;
- single mid-tier agent;
- deterministic workflow;
- generalist supervisor;
- supervisor + workers;
- specialized overseers;
- rule-based router;
- LLM router;
- project-adaptive router.

## 9.2 Task classes

- bug fix;
- feature implementation;
- refactoring;
- architectural migration;
- test creation;
- security audit;
- technical research;
- documentation generation;
- tech-debt resolution;
- CI diagnosis;
- modification of the harness itself.

## 9.3 Experimental factors

```text id="4bh91i"
router type
overseer topology
workflow type
model family
reasoning effort
memory strategy
communication topology
policy strictness
project adaptation
task complexity
repository maturity
```

## 9.4 Recommended design

A full factorial design would be expensive. We will use:

1. exploratory experiments;
2. fractional factorial design;
3. ablation studies;
4. paired evaluation;
5. deterministic replays;
6. longitudinal studies.

## 9.5 Variable control

Record:

- repository commit;
- harness version;
- prompt version;
- policy version;
- model and snapshot;
- tools;
- seeds when available;
- budget;
- timeout;
- initial state;
- environment;
- external availability.

## 9.6 Statistical analysis

As the data permits:

- confidence intervals;
- bootstrap;
- paired tests;
- Mann–Whitney or Wilcoxon;
- ANOVA or mixed models;
- effect size;
- survival analysis for time-to-success;
- Pareto frontier for cost versus quality;
- calibration;
- sensitivity analysis.

We should not interpret statistical significance without practical relevance.

---

# 10. Research roadmap

## Phase 0 — Protocol and infrastructure

**Objective:** make the research reproducible before accumulating sources.

Deliverables:

- protocol;
- glossary;
- study-record schema;
- bibliographic repository;
- evidence criteria;
- initial concept graph;
- ADR template;
- experiment template.

## Phase 1 — Systematic mapping

**Objective:** understand the territory.

Priority tracks:

1. routing;
2. workflows;
3. self-adaptation;
4. self-evolution;
5. deterministic governance;
6. coding harnesses.

Deliverables:

- community map;
- preliminary taxonomy;
- timeline;
- maturity matrix;
- research gaps.

## Phase 2 — Foundations and reference architecture

**Objective:** consolidate the theoretical base.

Deliverables:

- metamodel;
- control/intelligence plane separation;
- overseer model;
- effective constitution;
- trust zones;
- inner/outer loop model;
- ATAM scenarios.

## Phase 3 — Routing benchmark

**Objective:** evaluate global and project-level routing.

Deliverables:

- task dataset;
- human labels;
- baselines;
- hybrid router;
- metrics;
- comparative report.

## Phase 4 — Workflow DSL and compiler

**Objective:** support verifiable dynamism.

Deliverables:

- DSL;
- type system;
- policy checks;
- runtime;
- replay;
- DAG visualization;
- deadlock and cancellation tests.

## Phase 5 — Self-correction

**Objective:** create the inner loop.

Deliverables:

- fault taxonomy;
- diagnostic router;
- recovery policies;
- retry budgets;
- rollback;
- escalation protocol.

## Phase 6 — Project-level learning

**Objective:** test local self-regulation.

Deliverables:

- experience store;
- project priors;
- decay;
- negative memory;
- shadow routing;
- global-versus-local comparison.

## Phase 7 — Controlled evolution

**Objective:** create the outer loop.

Deliverables:

- proposal generation;
- replay suite;
- candidate registry;
- promotion pipeline;
- shadow/canary;
- evolution rollback;
- separation of duties.

## Phase 8 — Harness meta-evolution

**Objective:** allow the harness to work on itself with reduced autonomy.

Deliverables:

- meta-evolution trust zone;
- immutable approval kernel;
- independent evaluation;
- adversarial suite;
- governance report.

## Phase 9 — External case studies

**Objective:** test generalization.

Deliverables:

- multiple repositories;
- cross-project transfer;
- cost analysis;
- threats to validity;
- replications.

## Phase 10 — Final synthesis

Deliverables:

- reference architecture;
- patterns;
- anti-patterns;
- maturity model;
- open benchmark;
- corpus;
- scientific report;
- product roadmap.

---

# 11. Recommended initial corpus

## Foundations

1. Wooldridge and Jennings — intelligent agents. ([cs.ox.ac.uk](https://www.cs.ox.ac.uk/people/michael.wooldridge/pubs/ker95.pdf?utm_source=chatgpt.com))  
2. Rao and Georgeff — BDI Agents. ([cdn.aaai.org](https://cdn.aaai.org/ICMAS/1995/ICMAS95-042.pdf?utm_source=chatgpt.com))  
3. Van der Aalst et al. — Workflow Patterns. ([vdaalst.com](https://www.vdaalst.com/publications/p108.pdf?utm_source=chatgpt.com))  
4. Van der Aalst — Petri nets in workflow management. ([users.cs.northwestern.edu](https://users.cs.northwestern.edu/~robby/courses/395-495-2017-winter/Van%20Der%20Aalst%201998%20The%20Application%20of%20Petri%20Nets%20to%20Workflow%20Management.pdf?utm_source=chatgpt.com))  
5. Hevner et al. — Design Science. ([wise.vub.ac.be](https://wise.vub.ac.be/sites/default/files/thesis_info/design_science.pdf?utm_source=chatgpt.com))  
6. Kitchenham and Charters — SLR in software engineering. ([legacyfileshare.elsevier.com](https://legacyfileshare.elsevier.com/promis_misc/525444systematicreviewsguide.pdf?utm_source=chatgpt.com))  
7. Wohlin — snowballing. ([dl.acm.org](https://dl.acm.org/doi/10.1145/2601248.2601268?utm_source=chatgpt.com))  
8. Basili — GQM. ([ntrs.nasa.gov](https://ntrs.nasa.gov/api/citations/19900010450/downloads/19900010450.pdf?utm_source=chatgpt.com))  

## State of the art

1. Survey of multi-agent collaboration. ([arxiv.org](https://arxiv.org/html/2501.06322v1?utm_source=chatgpt.com))  
2. Survey of workflow optimization. ([arxiv.org](https://arxiv.org/html/2603.22386v1?utm_source=chatgpt.com))  
3. Survey of self-evolving agents. ([arxiv.org](https://arxiv.org/abs/2507.21046?utm_source=chatgpt.com))  
4. RouteLLM. ([arxiv.org](https://arxiv.org/html/2406.18665v4?utm_source=chatgpt.com))  
5. LLMRouterBench. ([arxiv.org](https://arxiv.org/abs/2601.07206?utm_source=chatgpt.com))  
6. AFlow. ([arxiv.org](https://arxiv.org/pdf/2410.10762?utm_source=chatgpt.com))  
7. MaAS. ([arxiv.org](https://arxiv.org/pdf/2502.04180?utm_source=chatgpt.com))  
8. EvoAgentX. ([arxiv.org](https://arxiv.org/html/2507.03616v1?utm_source=chatgpt.com))  

## Bleeding edge

1. GraphPlanner. ([arxiv.org](https://arxiv.org/pdf/2604.23626?utm_source=chatgpt.com))  
2. DyTopo. ([arxiv.org](https://arxiv.org/html/2602.06039v1?utm_source=chatgpt.com))  
3. Guided Topology Diffusion. ([arxiv.org](https://arxiv.org/abs/2510.07799?utm_source=chatgpt.com))  
4. TacoMAS. ([arxiv.org](https://arxiv.org/html/2605.09539v1?utm_source=chatgpt.com))  
5. EvolveR. ([arxiv.org](https://arxiv.org/abs/2510.16079?utm_source=chatgpt.com))  
6. Agentic evolution control plane. ([arxiv.org](https://arxiv.org/abs/2607.01120?utm_source=chatgpt.com))  
7. Runtime governance on execution paths. ([arxiv.org](https://arxiv.org/html/2603.16586v1?utm_source=chatgpt.com))  
8. Deterministic control plane for coding agents, treated as a recent hypothesis to reproduce. ([arxiv.org](https://arxiv.org/html/2606.26924v1?utm_source=chatgpt.com))  

## Vendors and state of practice

1. OpenAI Agents SDK and orchestration. ([developers.openai.com](https://developers.openai.com/api/docs/guides/agents?utm_source=chatgpt.com))  
2. Anthropic multi-agent research system. ([anthropic.com](https://www.anthropic.com/engineering/multi-agent-research-system?utm_source=chatgpt.com))  
3. Anthropic long-running harnesses. ([anthropic.com](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents?utm_source=chatgpt.com))  
4. LangGraph workflows, agents, and subgraphs. ([docs.langchain.com](https://docs.langchain.com/oss/python/langgraph/workflows-agents?utm_source=chatgpt.com))  
5. Google ADK multi-agent workflows. ([google.github.io](https://google.github.io/adk-docs/agents/multi-agents/?utm_source=chatgpt.com))  
6. Codex `AGENTS.md`. ([developers.openai.com](https://developers.openai.com/codex/agent-configuration/agents-md?utm_source=chatgpt.com))  
7. Claude Code settings, memory, hooks, and subagents. ([docs.anthropic.com](https://docs.anthropic.com/en/docs/claude-code/settings?utm_source=chatgpt.com))  
8. GitHub Copilot path-specific instructions. ([docs.github.com](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot?utm_source=chatgpt.com))  

## Governance and interoperability

1. OPA/Rego. ([openpolicyagent.org](https://openpolicyagent.org/docs?utm_source=chatgpt.com))  
2. NIST AI RMF. ([nist.gov](https://www.nist.gov/itl/ai-risk-management-framework?utm_source=chatgpt.com))  
3. OWASP Agentic Security. ([genai.owasp.org](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/?utm_source=chatgpt.com))  
4. MITRE ATLAS. ([atlas.mitre.org](https://atlas.mitre.org/?utm_source=chatgpt.com))  
5. ISO/IEC 42001. ([iso.org](https://www.iso.org/standard/42001?utm_source=chatgpt.com))  
6. MCP. ([modelcontextprotocol.io](https://modelcontextprotocol.io/specification/2025-11-25?utm_source=chatgpt.com))  
7. A2A. ([a2a-protocol.org](https://a2a-protocol.org/latest/specification/?utm_source=chatgpt.com))  
8. OpenTelemetry GenAI. ([opentelemetry.io](https://opentelemetry.io/blog/2026/genai-observability/?utm_source=chatgpt.com))  
9. W3C PROV-O. ([w3.org](https://www.w3.org/TR/prov-o/?utm_source=chatgpt.com))  

---

# 12. Main hypotheses to validate

1. **A hybrid router outperforms a purely LLM router** because it removes trivial and illegal decisions before inference.

2. **Project-level adaptation improves outcomes**, but only when experiences have provenance, decay, and subsequent validation.

3. **Dynamic workflows are more useful in ambiguous and long-duration tasks**, while static workflows remain superior for recurring and high-risk tasks.

4. **A single owner per task reduces conflict and context loss**, even when multiple overseers participate as reviewers.

5. **Stage-specific topologies reduce communication cost** without significantly reducing quality.

6. **Self-correction and self-evolution need to be separate loops**; mixing them creates persistent changes based on transient failures.

7. **Prompts are not security controls**; enforcement should occur in hooks, runtimes, sandboxes, and policy engines.

8. **The harness should have a special trust zone when modifying itself**.

9. **The trajectory is the primary unit of learning and governance**, not merely the prompt and final response.

10. **The best harness will become progressively adaptive, rather than maximally autonomous from the beginning**.

---

# 13. Recommended first research round

The first formal round should produce four interconnected documents:

### Document 1 — Taxonomy and glossary

- harness;
- agent;
- overseer;
- supervisor;
- router;
- workflow;
- control plane;
- adaptation;
- evolution;
- policy;
- trajectory;
- project constitution.

### Document 2 — Systematic Mapping

Map of publications, communities, approaches, and maturity.

### Document 3 — Reference architecture v0.1

```text id="q5s5qh"
Global Control Plane
Project Adaptive Plane
Routing Hierarchy
Overseer Layer
Workflow Compiler
Runtime
Experience/Evolution Plane
Observability and Governance
```

### Document 4 — Experimental protocol

- RQs;
- hypotheses;
- datasets;
- tasks;
- baselines;
- metrics;
- threats to validity;
- promotion criteria.

The ideal investigation sequence is:

```text id="rkdohd"
Foundations
    ↓
Taxonomy
    ↓
Systematic Mapping
    ↓
Preliminary architecture
    ↓
Routing benchmark
    ↓
Workflow compiler
    ↓
Inner correction loop
    ↓
Project adaptation
    ↓
Outer evolution loop
    ↓
Meta-evolution
```

This roadmap avoids starting with the riskiest capability — self-evolution — before observability, baselines, policies, and evals exist that can judge its proposals.
