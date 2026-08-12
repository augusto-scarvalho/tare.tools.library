# tare.tools — Identity, Lineage, Learning & Evolution

> **DERIVED ENGLISH TRANSLATION — MACHINE_TRANSLATED_UNREVIEWED.** The PT-BR source remains the historical authority. This translation does not reconcile or silently modernize claims.

I completed the research as a **thematic pack**, rather than a single document. The intent was to preserve the richness of the discussion without turning “Identity” into another monolithic subsystem or allowing external research to replace tare.tools architecture. The corpus hierarchy remains explicit: research and proposals are evidence; ratified architecture, specs, gates, Git and code remain stronger authorities.

The pack contains **131 numbered sections across four core documents**, plus a five-section master index. The generated HTMLs were reported as structurally validated with no UTF-8 replacement corruption, duplicate IDs or broken internal anchors.

## Deliverables

- Master index — Identity, Lineage, Learning & Evolution.
- Scientific research — Canonical Lineage, Identity, Governance & Audit: compositional identity, Subject/Work/Execution/Authority, provenance, observability, temporality, metrology, audit, chain of custody, governance, security identity, causality and cross-plane invariants.
- Scientific research — Adaptive Learning, Cross-Project Experience & Governed Self-Evolution: trajectories/experience, attribution, Project-local learning, transportability, procedural memory, agent feedback, causal replay, OPE, drift, autonomous experimentation, evolution candidates and self-evolution.
- Technology landscape — W3C PROV, OpenLineage, OpenTelemetry/OpenInference, SPIFFE/SPIRE, SLSA, in-toto, Sigstore, Temporal, Cedar, OpenFGA, OpenFeature, MLflow, Argo Rollouts, Backstage, Dagster and related mechanisms, classified as ADOPT / ADAPT / INSPIRE / EXPERIMENT / DEFER.
- Technical proposal — Canonical Lineage & Adaptive Experience: architecture, contracts, SDD/BDD, invariants, derived views, candidate contracts, golden lineage queries, temporal semantics, migration slices, BDDs, gates, rollback and future Implementation Packets. It remains **PROPOSED TARGET / reconciliation required**.

## What the research changed or refined

The main result was not a justification for an Identity Plane. The stronger thesis is:

> **tare.tools should be lineage-preserving rather than identity-centric.**

Relevant identity emerges compositionally:

```text
Subject
  → Subject state / revision
  → Work / Workflow / durable work
  → RouteIntent / RouteDecision
  → ExecutionBinding / attempt
  → ActionRequest
  → Authority / Policy epoch
  → Permit
  → Logical effect / attempts / reconciliation
  → EffectReceipt
  → OutcomeEvidence
  → Attribution
  → Memory / Reputation / Qualification
  → Evolution Candidate
  → independent evaluation
  → promotion / rejection / revocation
```

Bounded contexts continue to own the semantics of each segment; no single component owns the whole history. Derived objects should remain reconstructable from sources and projections should be disposable/rebuildable rather than becoming a new source of kernel authority.

## Trace is not sufficient provenance

Recent work distinguishes chronological execution traces from provenance capable of relating activities, evidence, causal dependencies and responsibility. This supports a separation in tare.tools:

```text
Observability  → observes / projects
Canonical lineage → identifies / relates
Evidence → supports claims
Audit → challenges claims
Attribution → interprets causality
```

OpenTelemetry can be useful for propagation and visualization, but should not own canonical history.

## Correlation is not Attribution

Even a perfect lineage `A → B → C → outcome` does not prove that A caused the outcome. The proposed attribution ladder is:

```text
observational
contrastive
intervention-supported
causal-qualified
```

A causation ID alone is not causal inference.

## Workflow and procedural learning

The research strengthens the connection between trajectories and governed procedural learning. Repeated experience can become a procedural hypothesis, then be replayed/compared, compiled into a candidate workflow, exercised in shadow/canary, and only then promoted. The most valuable memory may therefore become deterministic machinery rather than more text in a prompt.

## Cross-project learning

A candidate invariant is:

> **The scope of evidence bounds the scope of learning.**

```text
1 execution → execution-local adaptation
multiple comparable executions → Project-local posterior
multiple similar Projects → Project-class prior
replicated transportable evidence → platform prior
```

Experience Transportability is therefore distinct from simply storing Memory: reuse requires evidence that the target Project is sufficiently comparable along effect-modifying dimensions.

## Agent feedback

Agents can be distributed sensors of friction and opportunity, but their feedback is not learned truth. Preferred flow:

```text
Agentic feedback
 → FindingClaim / hypothesis
 → linked trajectory
 → corroboration / contradiction
 → candidate improvement
 → experiment
```

## Governed self-evolution

Experience does not directly mutate production:

```text
Experience → Finding → Hypothesis → Candidate
```

For tare.tools itself, incumbent, candidate, evaluator and promotion authority must remain distinguishable.

## Technology reuse

The landscape reinforces a boundary-oriented strategy:

- OpenTelemetry/OpenInference → observability projection.
- W3C PROV/OpenLineage → provenance interchange/projection.
- SPIFFE/SPIRE → workload/security identity evidence.
- SLSA/in-toto/Sigstore → artifact/candidate provenance and attestations.
- Temporal → durable execution backend / semantic reference.
- Cedar/OPA/OpenFGA → qualified policy/relationship backends.
- MLflow → experiment/evolution laboratory.
- OpenFeature → adaptive/shadow configuration surface.
- Argo Rollouts → progressive exposure inspiration/backend.
- Backstage/Dagster → Project/asset/lineage Experience inspiration.

The principle remains: **tare owns meaning; external systems provide mechanisms.**

## Read-only Canonical Lineage View first

The technical proposal begins with a read-only reconstruction:

```text
existing canonical state
+ events
+ receipts
+ bindings
+ artifacts
+ evidence
      ↓
lineage reconstruction
      ↓
golden queries
```

Examples include: Which governed work caused an effect? Under which Authority/policy epoch? Which physical execution produced an artifact? Which Project revision was acted upon? Which evaluator produced evidence? Which evidence changed a ReputationSnapshot? Which experiences generated a candidate? Who evaluated/promoted it? Can a Project-local finding legitimately affect another Project?

Only when these questions cannot be answered compositionally should a new primitive or canonical relationship be proposed.

## Candidate invariant families

- Identity completeness.
- Causal completeness.
- Authority traceability.
- Effect traceability.
- Evidence traceability.
- Subject isolation.
- Temporal/revision integrity.
- Evaluator independence traceability.
- Learning applicability.
- Evolution separation.

The hypothesis is that governability, auditability and learnability may become different queries over one durable lineage rather than three systems maintaining incompatible histories.

## Future research pointers

Highest-priority branches identified in this round include Temporal/Bitemporal Semantics, Causal Attribution & Counterfactual Learning, Experience Transportability, Metrology of Agentic Evidence, Procedural Memory & Workflow Evolution, Autonomous Experimental Design / Value of Information, Effect Accounting & Operational Settlement, Principal/Workload Identity & Federation, Safe Adaptive Control, and Typed Canonical Lineage / typestate/effect systems.

## Rehydration thesis

> **tare.tools should preserve a canonical, temporal and evidence-backed lineage from governed Subject and Work through decision, execution and effects to evidence, attribution and evolution. Bounded contexts own their semantics but not the whole story. Observability and capsules are projections; agents and models are causal participants rather than roots of authority; learning remains scoped by provenance and applicability; and persistent evolution requires independently qualified evidence and promotion authority.**
