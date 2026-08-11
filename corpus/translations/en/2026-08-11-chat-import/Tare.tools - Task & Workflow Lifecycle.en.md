I closed this round as a **new formal tare.tools research lineage**, recentered on the North Star and without turning the findings into automatic architectural authority.

The research started from the **verifiable historical CURRENT** — where the incumbent still has `workflow_plan/run/reduce/lifecycle/writes` and its own workflow lifecycle fileciteturn33file0 — and confronted it with the **TARGET Agent OS**, which already anticipates a Workflow Compiler, Durable Runtime, Routing, ExecutionBinding, Capability/Effects, Evidence, and Evolution Control. fileciteturn34file6turn34file7 From that point onward, everything else is explicitly classified as ADOPT/ADAPT/OPEN/RESEARCH before any implementation.

### Deliverables

**[Scientific and exploratory research — Workflow as Governed Work in the tare.tools Agent OS](sandbox:/mnt/data/tare_tools_workflow_governed_work_scientific_research_2026-08-11.html)**

There are **36 content chapters + bibliography**, with **81 references/sources**. The document crosses workflow science, Statecharts, Petri/WF-nets, GSM/CMMN, structured concurrency, Sagas, durable execution, query optimizers, compilers/PGO, Compound AI, metareasoning, ontologies, AST/LSP/SCIP, process mining, procedural memory, self-evolution, safety engineering, metrology, and current vendors/frameworks.

**[Separate technical proposal — Workflow as a Durable Work Program: Architecture, Contracts and BDD](sandbox:/mnt/data/tare_tools_workflow_governed_work_implementation_proposal_2026-08-11.html)**

There are **42 chapters + references**, explicitly marked **PROPOSED TARGET / IMPLEMENTATION RESEARCH — do not implement before read-only reconciliation with canonical CURRENT**. It includes a semantic model, heterogeneous nodes, compiler passes, subworkflow contracts, structured concurrency, multidimensional lifecycle, terminality, GraphPatch/revisions, invalidation, freshness, durable waits, effect reconciliation, Assurance, event history, economics, Workflow PGO, procedural learning, BDDs, and Strangler migration.

**[Complete bundle — two HTML files + manifest](sandbox:/mnt/data/tare_tools_workflow_governed_work_research_bundle_2026-08-11.zip)**

**[Validation and SHA-256 manifest](sandbox:/mnt/data/tare_tools_workflow_governed_work_manifest_2026-08-11.json)**

Both HTML files passed UTF-8 validation, parsing, unique-ID checks, and resolution of all internal anchors.

### Some findings I consider particularly important

Recent workflow-optimization literature independently reached a distinction almost identical to ours: **a reusable template, a graph realized for a run, and an execution trace are different objects**. This provides strong support for our `WorkflowTemplate → CompiledWorkflow/Instance → WorkflowTrace` separation, although it does not ratify our specific contracts. ([arxiv.org](https://arxiv.org/abs/2603.22386))

GSM/CMMN turned out to be an extremely fertile source. Rather than seeing workflow only as a sequence, this tradition works with **durable artifacts/cases, stages, guards, milestones, and planning-at-runtime**; CMMN even allows discretionary work to be added during a Case as new facts emerge. This significantly reinforced our hypothesis that a future tare `WorkflowInstance` may semantically resemble a **durable governed case** more than “a DAG that is running.” ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The thesis of **heterogeneous workflows** also became stronger. Compound AI in 2026 already recenters design on systems that compose models, algorithms, and tools, with topology and configuration as distinct decisions; LangGraph now explicitly documents graphs mixing deterministic and agentic steps; Google ADK preserves deterministic workflow control outside the model. ([arxiv.org](https://arxiv.org/abs/2606.14350)) Our extension is more ambitious: apply this under Authority, EffectReceipt, Evidence, Project Model, and Evolution Control.

And the bleeding edge brought a finding particularly aligned with our idea of procedural learning: **TraceCompiler**, published on August 3, 2026, mines noisy traces and compiles them into mostly deterministic workflows; it only creates hard dependencies when it can justify them through data dependency and, in one case involving an insufficiently determined irreversible side effect, refuses compilation rather than improvising. This is practically a natural experiment for our `trajectory → qualified procedural candidate` thesis, although the paper itself is careful not to claim net cost reduction including the cost of offline compilation. ([arxiv.org](https://arxiv.org/abs/2608.02680))

Another important convergence is that **durable execution must not own our ontology**. Temporal demonstrates the value of Event History/replay and the Workflow ID/Run ID separation, but these mechanisms serve as backend references; tare still needs to own its own semantics for Authority, logical effects, reconciliation, and evidence. ([docs.temporal.io](https://docs.temporal.io/workflow-execution))

For that reason, the technical proposal does not select Temporal, Restate, or DBOS. It proposes a future **identical qualification/conformance pack** to compare them, preserving the incumbent and Windows as first-class.

### Pointers I explicitly prepared

- **`Workflow Lifecycle Semantics`** — recover this chat + `WorkflowInstance`, `WorkflowRevision`, desired×observed, terminality, GraphPatch, structured concurrency, retry/reroute/resume/replan/reconcile.
- **`Workflow Compiler as Query Optimizer`** — logical×physical workflow, cost model, plan alternatives, adaptive reoptimization, receding horizon, and `cost-to-trust`.
- **`Workflow Formal Semantics Federation`** — Statecharts/SCXML + Petri/WF-nets + GSM/CMMN + HTN + constraint models as different projections, not competing ontologies.
- **`Procedural Memory & Workflow Evolution`** — AWM, SkillOpt, GEPA, AFlow, TraceCompiler, process mining, and Workflow Profile-Guided Optimization.
- **`Project Model → Workflow Planning`** — `specgraph-estudo-ideacao-refinamento`, AST/CST, SCIP, LSP, ontology, Evidence Graph, and planning compilation.
- **`Causal Workflow Learning`** — attribution, off-policy evaluation, counterfactual replay, experimental design, compiler regret, and selection bias.
- **`Metrology of Agentic Systems`** — judges/tests/scanners/humans as calibratable instruments; EvidenceFamily and evaluator drift.
- **`Safety Engineering for Agent OS`** — STPA, unsafe control actions, stale world models, timing/freshness, near misses, and Effect Torture Lab.
- **`Executable System Reconstruction & Procedural Knowledge Extraction`** — expanded branch of `Cognitive Systems Reconstruction`: Watson/Dialogflow, SCXML, BPM/RPA, case systems, process/conversation mining, and automata learning.
- **`Cross-Project Learning & Transfer`** — Project→domain→global scopes, ontology alignment, negative transfer, procedural applicability, and conservative generalization.
- **`Workflow-first Experience Plane`** — TUI/GUI, cheap semantic routing, small models as semantic glue, Economy/Balanced/Max-Assurance as realization strategies.

The most important result of the research, in my view, is that it **does not ask for a new North Star**. It makes the current one more precise.

The main shift is this:

> **tare.tools stops thinking of Workflow as a mechanism that organizes agents and starts thinking of it as the representation of the progression of governed work.**

The other consequences then follow naturally: deterministic work becomes first-class, agents become one possible executor, the Project Model becomes the epistemic substrate for planning, subworkflows become procedural memory, durable identity sits above sessions/runtimes, effects are reconciled before retry, traces become raw material for learning, and Evolution Control becomes the barrier between “I discovered something” and “I permanently changed the system.”

And perhaps the most compact formulation recorded in the documents is:

> **tare.tools should not be optimized to choose good agents; it should be optimized to compile good systems of work — choosing agents only at the points where agency is actually the appropriate instrument.**

This also directly connects the architectural refinement to what motivated much of the conversation: **cost × benefit stops being only the router's responsibility and becomes a property of compiling the entire body of work**. ([arxiv.org](https://arxiv.org/abs/2606.00774)) memcite
