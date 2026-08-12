# Research Lineage, Influence & Source Graph — 2026-08-11

> Generated from byte-preserved historical artifacts, the 2026-08-11 refresh crosswalk, internal curation map, and observed external citations. Curated influence edges are interpretations and are marked as such.

## 1. Coverage

- Historical artifacts mapped: **93/93**
- Refreshed HTML documents: **20**
- External sources observed in refreshed corpus: **58**
- Curated cross-lineage influence edges: **26**
- Co-citation edges observed in ≥2 refreshed documents: **268**
- External source-family candidates: **2**

### Historical treatments

- `EVIDENCE_ONLY`: 1
- `IMPLEMENTATION_HISTORY`: 16
- `OPERATIONAL_EVIDENCE`: 4
- `RESEARCH_ITERATION_EVIDENCE`: 28
- `SCIENTIFIC_LINEAGE`: 44

## 2. Refreshed lineage map

| Lineage | Historical inputs | Scientific refresh | Technical companion |
|---|---:|---|---|
| Agent OS Foundations | 3 | [`scientific refresh`](../refresh-editions/2026-08-11/agent-os-foundations/agent-os-foundations-scientific-refresh-2026-08-11.html) | [`PROPOSED delta`](../refresh-editions/2026-08-11/agent-os-foundations/agent-os-foundations-implementation-research-delta-2026-08-11.html) |
| Workflow & Procedural Systems | 10 | [`scientific refresh`](../refresh-editions/2026-08-11/workflow-procedural/workflow-procedural-scientific-refresh-2026-08-11.html) | [`PROPOSED delta`](../refresh-editions/2026-08-11/workflow-procedural/workflow-procedural-implementation-research-delta-2026-08-11.html) |
| Context, Memory & Playbooks | 13 | [`scientific refresh`](../refresh-editions/2026-08-11/context-memory-playbooks/context-memory-playbooks-scientific-refresh-2026-08-11.html) | [`PROPOSED delta`](../refresh-editions/2026-08-11/context-memory-playbooks/context-memory-playbooks-implementation-research-delta-2026-08-11.html) |
| Assurance, Governance & Quality | 16 | [`scientific refresh`](../refresh-editions/2026-08-11/assurance-governance-quality/assurance-governance-quality-scientific-refresh-2026-08-11.html) | [`PROPOSED delta`](../refresh-editions/2026-08-11/assurance-governance-quality/assurance-governance-quality-implementation-research-delta-2026-08-11.html) |
| Runtime, Reliability & Sandbox | 15 | [`scientific refresh`](../refresh-editions/2026-08-11/runtime-reliability-sandbox/runtime-reliability-sandbox-scientific-refresh-2026-08-11.html) | [`PROPOSED delta`](../refresh-editions/2026-08-11/runtime-reliability-sandbox/runtime-reliability-sandbox-implementation-research-delta-2026-08-11.html) |
| Routing, Economics & Observability | 9 | [`scientific refresh`](../refresh-editions/2026-08-11/routing-economics-observability/routing-economics-observability-scientific-refresh-2026-08-11.html) | [`PROPOSED delta`](../refresh-editions/2026-08-11/routing-economics-observability/routing-economics-observability-implementation-research-delta-2026-08-11.html) |
| Interoperability & Protocols | 1 | [`scientific refresh`](../refresh-editions/2026-08-11/interoperability-protocols/interoperability-protocols-scientific-refresh-2026-08-11.html) | [`PROPOSED delta`](../refresh-editions/2026-08-11/interoperability-protocols/interoperability-protocols-implementation-research-delta-2026-08-11.html) |
| Experience, TUI & UX | 6 | [`scientific refresh`](../refresh-editions/2026-08-11/experience-ux/experience-ux-scientific-refresh-2026-08-11.html) | [`PROPOSED delta`](../refresh-editions/2026-08-11/experience-ux/experience-ux-implementation-research-delta-2026-08-11.html) |
| Research Methodology & Evidence | 20 | [`scientific refresh`](../refresh-editions/2026-08-11/research-methodology-evidence/research-methodology-evidence-scientific-refresh-2026-08-11.html) | [`PROPOSED delta`](../refresh-editions/2026-08-11/research-methodology-evidence/research-methodology-evidence-implementation-research-delta-2026-08-11.html) |

## 3. Cross-lineage interference / influence

These edges are **curated architectural interpretations** of the refreshed corpus, not causal claims about authorship.

| From | Relation | To | Effect | Confidence |
|---|---|---|---|---|
| Agent OS Foundations | `RECENTERS` | Workflow & Procedural Systems | Moves workflow from agent orchestration toward governed heterogeneous work under canonical ownership. | high |
| Agent OS Foundations | `RECENTERS` | Context, Memory & Playbooks | Moves context/memory/playbooks under bounded-context and minimal-projection discipline rather than parallel control planes. | high |
| Agent OS Foundations | `CONSTRAINS` | Assurance, Governance & Quality | Authority-before-intelligence and evidence-first architecture constrain assurance/audit promotion semantics. | high |
| Agent OS Foundations | `RECENTERS` | Runtime, Reliability & Sandbox | Runtime ownership and capability/effect boundaries replace vendor-specific runtime semantics in the core. | high |
| Agent OS Foundations | `CONSTRAINS` | Routing, Economics & Observability | Routing/reputation/economics remain downstream of authority/eligibility and cannot mint authority. | high |
| Agent OS Foundations | `RECENTERS` | Interoperability & Protocols | Protocols become edge projections/adapters rather than kernel ontologies. | high |
| Agent OS Foundations | `RECENTERS` | Experience, TUI & UX | Experience becomes a projection/steering surface over canonical state, not an owner of runtime/policy state. | high |
| Agent OS Foundations | `CONSTRAINS` | Research Methodology & Evidence | Research remains evidence and cannot silently become canonical architecture. | high |
| Workflow & Procedural Systems | `EMITS_REQUIREMENTS_TO` | Routing, Economics & Observability | Logical work produces routing intents, constraints and budget context for realization. | high |
| Routing, Economics & Observability | `SELECTS_BINDING_IN` | Runtime, Reliability & Sandbox | Routing realizes eligible work through concrete execution bindings/runtime candidates. | high |
| Runtime, Reliability & Sandbox | `CONSTRAINS` | Workflow & Procedural Systems | Effect ambiguity, reconciliation, cancellation and durability constrain retry/replan/workflow lifecycle semantics. | high |
| Interoperability & Protocols | `CONSTRAINS_BOUNDARY_SEMANTICS_OF` | Runtime, Reliability & Sandbox | Boundary qualification and semantic-loss accounting constrain execution through external runtimes/protocols. | high |
| Runtime, Reliability & Sandbox | `SUPPLIES_EFFECT_SEMANTICS_TO` | Interoperability & Protocols | Canonical effect/reconciliation semantics must be preserved when projected across protocol boundaries. | high |
| Context, Memory & Playbooks | `INFORMS` | Workflow & Procedural Systems | Project/context evidence and procedural knowledge inform planning and workflow compilation. | high |
| Context, Memory & Playbooks | `INFORMS` | Routing, Economics & Observability | Project-local context, priors and applicability inform routing without granting authority. | high |
| Context, Memory & Playbooks | `INFORMS_PRESENTATION_OF` | Experience, TUI & UX | Context/memory provenance informs what Experience surfaces and how deeply it discloses operational state. | medium |
| Assurance, Governance & Quality | `QUALIFIES_LEARNING_FOR` | Routing, Economics & Observability | Only qualified outcomes/evidence should update routing/reputation/economic adaptation. | high |
| Assurance, Governance & Quality | `QUALIFIES_PROMOTION_OF` | Workflow & Procedural Systems | Procedural candidates and workflow optimizations require independent/qualified evidence before durable promotion. | high |
| Assurance, Governance & Quality | `VALIDATES` | Runtime, Reliability & Sandbox | Runtime/sandbox/reliability claims require assurance rather than self-reported success. | high |
| Research Methodology & Evidence | `CALIBRATES` | Assurance, Governance & Quality | Metrology, validity, independence and experimental design calibrate assurance instruments. | high |
| Research Methodology & Evidence | `CALIBRATES` | Routing, Economics & Observability | Routing claims require baselines, regret/calibration, paired designs and contamination-aware evidence. | high |
| Research Methodology & Evidence | `CALIBRATES` | Workflow & Procedural Systems | Workflow improvements require cost-to-trust and causal/experimental evaluation, not trace anecdotes alone. | high |
| Workflow & Procedural Systems | `PROJECTS_PROGRESS_TO` | Experience, TUI & UX | Workflow state/progress is projected into human-facing surfaces. | high |
| Experience, TUI & UX | `STEERS` | Workflow & Procedural Systems | Human steering/approval/repair enters work through governed intents rather than UI-owned state mutation. | medium |
| Routing, Economics & Observability | `PROJECTS_DECISIONS_TO` | Experience, TUI & UX | Model/runtime/cost/route decisions are surfaced as operational disclosure. | medium |
| Assurance, Governance & Quality | `PROJECTS_EVIDENCE_TO` | Experience, TUI & UX | Evidence, confidence, approvals and incidents shape operator-facing explanations and review surfaces. | medium |

## 4. Source graph

Every external URL cited by a refreshed document is represented as an observed `CITED_BY` edge. This enables questions such as *which internal lineages depend on this paper?*, *which sources bridge multiple lineages?*, and *what disappears if a source is retired or falsified?*

The machine-readable files are:

- [`RESEARCH_RELATION_GRAPH.json`](RESEARCH_RELATION_GRAPH.json)
- [`SOURCE_CO_CITATION.json`](SOURCE_CO_CITATION.json)
- [`SOURCE_FAMILIES.json`](SOURCE_FAMILIES.json)
- [`RESEARCH_RELATION_GRAPH.mmd`](RESEARCH_RELATION_GRAPH.mmd)

## 5. Strongest bridge sources by document coverage

| Source | Refresh documents |
|---|---:|
| [Agentic Harness Engineering](https://arxiv.org/abs/2604.25850) | 8 |
| [Google Gemini + Temporal durable agent example](https://ai.google.dev/gemini-api/docs/temporal-example) | 6 |
| [Agent libOS: A Library-OS-Inspired Runtime for Long-Running, Capability-Controlled LLM Agents](https://arxiv.org/abs/2606.03895) | 6 |
| [OpenTelemetry GenAI Observability](https://opentelemetry.io/blog/2026/genai-observability/) | 6 |
| [SWE-Mutation: Can LLMs Generate Reliable Test Suites in Software Engineering?](https://aclanthology.org/2026.findings-acl.1976/) | 4 |
| [RepoReason: Benchmarking Agentic Code Reasoning at Repository Level](https://arxiv.org/abs/2601.03731) | 4 |
| [Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers](https://arxiv.org/abs/2603.07670) | 4 |
| [Auditable Agents](https://arxiv.org/abs/2604.05485) | 4 |
| [When the Judge Changes, So Does the Measurement](https://arxiv.org/abs/2607.08535) | 4 |
| [Plover: Steering GUI Agents through Plan-Centric Interaction](https://arxiv.org/abs/2607.15193) | 4 |
| [AgentGUI: An Interface for Observing and Steering Long-Running AI Agents](https://arxiv.org/abs/2607.26300) | 4 |
| [TraceCompiler](https://arxiv.org/abs/2608.02680) | 4 |
| [MCP 2026-07-28 Specification](https://blog.modelcontextprotocol.io/posts/2026-07-28/) | 4 |
| [Microsoft Agent Framework — Durable Extension](https://learn.microsoft.com/en-us/agent-framework/integrations/durable-extension) | 4 |
| [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) | 4 |
| [A2A Protocol Specification 1.0](https://a2a-protocol.org/dev/specification/) | 2 |
| [A2A v1.0 announcement](https://a2a-protocol.org/latest/announcing-1.0/) | 2 |
| [A2A Protocol specification](https://a2a-protocol.org/latest/specification/) | 2 |
| [SWE-Mutation](https://aclanthology.org/2026.acl-long.590/) | 2 |
| [LLMRouterBench: A Massive Benchmark and Unified Framework for LLM Routing](https://aclanthology.org/2026.findings-acl.1881/) | 2 |

## 6. Interpretation rules

1. `CITED_BY` is factual within this corpus; it does not mean the source supports every claim in the document.
2. `CO_CITED_WITH` is bibliographic proximity only.
3. `RECENTERS`, `CONSTRAINS`, `CALIBRATES` and similar edges are curated interpretations and must cite the corpus basis.
4. `SUPERSEDES` is intentionally absent unless explicit version/normative evidence exists.
5. External paper-to-paper lineage is not inferred merely from title similarity; candidates remain `CANDIDATE_UNTIL_VERIFIED`.
6. Negative evidence and falsifications should be represented as first-class `CHALLENGES`/`FALSIFIES` edges rather than removed from history.


## 2026-08-12 live ResearchObject — Information Survival / Demand Lineage

`research_object.information-survival-demand-lineage-2026-08-12` extends the live corpus without creating a new lineage. It **RECENTERS** Project/Agent OS around semantic homes and reconstructability, **REFINES** Workflow/Context/Assurance/Interoperability, **CONSTRAINS** reliability and learning with survival/freshness requirements, and **DOGFOODS** the research substrate's own original→reference→translation→projection policy. See the relationship graph for machine-readable edges.
