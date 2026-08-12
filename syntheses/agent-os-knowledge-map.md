# Agent OS Knowledge Map

[← Home](../README.md) · [Repository Navigation](../NAVIGATION.md) · [Reading Guide](research-reading-guide.md) · [All Research](../research/README.md)

**Status:** RESEARCH synthesis. This page connects the library; it does not replace the deep studies.

## North Star

The tare.tools research program treats the project as a **user-space Agent Operating System** rather than a monolithic super-agent:

> probabilistic in interpretation, dynamic in planning, durable in execution, deterministic in authority, capability-mediated in effects, evidence-driven in learning, and conservative in self-evolution.

## Conceptual spine

```text
[Project / Subject / Demand]
          │
          ▼
[Governed Work / Workflow]
          │
          ▼
[Policy / Authority / Permit]
          │
          ▼
[RouteIntent → RouteDecision → ExecutionBinding]
          │
          ▼
[Runtime + Capability / ActionRequest]
          │
          ▼
[Logical Effect → Reconciliation → EffectReceipt]
          │
          ▼
[Validation / Assurance / OutcomeEvidence]
          │
          ▼
[Attribution / Qualification / Reputation]
          │
          ▼
[Context / Memory / Procedure candidate]
          │
          ▼
[Evolution candidate → independent evaluation → governed promotion]
```

## Follow the concepts into the studies

- **Project / admission:** [Agent OS Foundations](../research/foundations/agent-os-foundations.md) → [Project Admission & Adoption](../research/project/project-admission-adoption.md)
- **Demand / settlement:** [Demand Lineage, Context Reconstruction & Settlement](../research/work/demand-lineage-settlement.md)
- **Workflow / durable work:** [Workflow as Governed Work](../research/work/workflow-governed-work.md)
- **Effects / reliability:** [Reliability Semantics & Effect Reconciliation](../research/work/reliability-effect-reconciliation.md)
- **Information survival:** [Information Survival & Reconstructive Assurance](../research/work/information-survival-reconstructability.md)
- **Governance / decision rights:** [Constitutional Governance](../research/governance/constitutional-governance-decision-rights.md)
- **Audit / assurance:** [Governance Assurance & Audit](../research/governance/governance-assurance-audit-metrology.md) → [Assurance & Governed Evolution](../research/governance/assurance-evolution-testing.md)
- **Testing instruments:** [Test Engineering & Scenario Gates](../research/assurance/test-engineering-scenario-gates.md)
- **Runtime ownership:** [Runtime Ownership & Vendor Integration](../research/runtime/runtime-ownership-vendor-integration.md)
- **Capabilities / sandbox:** [Capability, Sandbox, Resources & Isolation](../research/runtime/capability-sandbox-resources.md)
- **Protocols / federation:** [Protocols & Interoperability](../research/runtime/protocols-interoperability.md)
- **Vendor runtime archaeology:** [Vendor CLI / Agent Runtime Landscape](../research/runtime/vendor-cli-runtime-landscape.md)
- **Routing / reputation:** [Adaptive Routing, Reputation & Qualification](../research/routing/adaptive-routing-reputation.md)
- **Economics / resources:** [Economics, Resources & Observability](../research/routing/economics-resources-observability.md)
- **Context / playbooks:** [Context, Memory & Playbooks](../research/context/context-memory-playbooks.md)
- **Identity / provenance:** [Canonical Lineage & Compositional Identity](../research/context/canonical-lineage-identity.md)
- **Learning / evolution:** [Adaptive Learning, Cross-Project Experience & Self-Evolution](../research/context/adaptive-learning-cross-project-evolution.md)
- **Human experience:** [TUI / REPL / Human-Agent Experience](../research/experience/tui-repl-experience.md)
- **Legacy reconstruction:** [Executable / Cognitive System Reconstruction](../research/experience/legacy-system-reconstruction.md)
- **Local inference:** [Local Model Lab Methodology](../research/local-inference/local-model-lab-methodology.md)
- **Research method:** [Formal Research Program](../research/methodology/formal-research-program.md) → [CMRP & Epistemic Independence](../research/methodology/cmrp-and-epistemic-independence.md)

## Cross-cutting lines

### Canonical Lineage

[Canonical Lineage](../research/context/canonical-lineage-identity.md) asks whether identities and causality remain reconstructible across Project → Work → RouteDecision → ExecutionBinding → Effect → Evidence → Learning.

### Information Survival

[Information Survival](../research/work/information-survival-reconstructability.md) asks what must remain durable, what may be reconstructed, and which physical storage system should hold each class without owning semantics.

### Authority before intelligence

[Constitutional Governance](../research/governance/constitutional-governance-decision-rights.md), [Runtime Ownership](../research/runtime/runtime-ownership-vendor-integration.md), and [Adaptive Routing](../research/routing/adaptive-routing-reputation.md) together preserve the ordering:

`Policy/Authority → eligibility → capability/runtime availability → routing/economics → execution → validation → evidence`.

## From research to architecture

```text
Research
  ↓
Findings
  ↓
ADR / Canonical Architecture   ← outside this repository
  ↓
SPEC → BDD → Implementation Packet → Code/Gates
  ↓
Outcome Evidence
  └────────────► Research
```

Use [Technical Proposals](../proposals/README.md) as hypotheses, not as shortcuts around canonical reconciliation.

---

**Continue:** [Research Reading Guide →](research-reading-guide.md) · [HTML/source editions](../sources/README.md)
