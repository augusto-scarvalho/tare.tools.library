# Selected Evidence Registry — semantic curation 2026-08-12

[← Sources & Provenance](README.md) · [Repository Navigation](../NAVIGATION.md) · [Curated Findings](../findings/CURATED_FINDINGS.md) · [Living Research](../research/README.md)

**Status:** RESEARCH bibliography / provenance aid.  
**Purpose:** preserve the smallest useful set of external sources that materially support, challenge or operationalize the living studies.  
**Important:** this registry is curated from the source lineages already researched in tare.tools. This curation pass did **not** freshly re-verify every external URL/version on 2026-08-12; freshness must be checked before normative promotion or implementation where recency matters.

## Evidence classes

- **E1 — consolidated / peer-reviewed / seminal:** strongest conceptual or empirical foundation.
- **E2 — reproducible benchmark / mature system evidence:** supports comparative or operational claims.
- **E3 — recent preprint with relevant evaluation/artifact:** frontier evidence; hypothesis-shaping, not automatic authority.
- **E4 — official specification / mainline / vendor engineering:** describes mechanisms and current interfaces; does not prove superiority.
- **E5 — field signal / issue / discussion:** useful for failure classes and hypotheses, not prevalence estimates.

The registry deliberately avoids a score based on source count. One source may support several studies; a prestigious source may still be weak evidence for a project-specific claim.

---

## Study 01 — Agent OS Foundations & Canonical Spine

**Living research:** [Agent OS Foundations](../research/foundations/agent-os-foundations.md) · [Project Admission](../research/project/project-admission-adoption.md)

### S01-E01 — Exokernel: An Operating System Architecture for Application-Level Resource Management
- Class: **E1 / seminal systems**
- Engler et al., SOSP 1995.
- https://dl.acm.org/doi/10.1145/224056.224076
- Supports: user-space ownership split; mechanism below, policy/semantics above.
- Applies to: F01, F02.
- Limitation: OS architecture analogy, not evidence that tare.tools should copy exokernel primitives.

### S01-E02 — AIOS: LLM Agent Operating System
- Class: **E3 / agentic systems**
- https://arxiv.org/abs/2403.16971
- Supports: empirical existence of agent-OS framing around scheduling, memory, storage, access control and tools.
- Applies to: F01.
- Limitation: alternative architecture; its ontology is not tare.tools authority.

### S01-E03 — Agent libOS: A Library-OS-Inspired Runtime for Long-Running, Capability-Controlled LLM Agents
- Class: **E3 / 2026 frontier**
- https://arxiv.org/abs/2606.03895
- Supports: user-space/library-OS framing, explicit capabilities, long-running lifecycle.
- Applies to: F01, F03, F05.
- Limitation: useful convergence signal, not proof that its primitive set should be adopted.

### S01-E04 — Agentic Harness Engineering
- Class: **E3 / harness engineering**
- https://arxiv.org/abs/2604.25850
- Supports: harness as an engineering asset that can be measured/evolved independently of the base model.
- Applies to: F02, F38.
- Limitation: harness optimization does not grant evolution authority.

### S01-E05 — OS Agents: A Survey on MLLM-based Agents for Computer, Phone and Browser Use
- Class: **E1 / peer-reviewed survey**
- ACL 2025.
- https://aclanthology.org/2025.acl-long.369/
- Supports: observation/action/runtime/safety distinctions in OS-facing agents.
- Applies to: F01, F05.

---

## Study 02 — Governed Work, Effects, Lineage & Reconstructability

**Living research:** [Workflow](../research/work/workflow-governed-work.md) · [Reliability](../research/work/reliability-effect-reconciliation.md) · [Information Survival](../research/work/information-survival-reconstructability.md) · [Canonical Lineage](../research/context/canonical-lineage-identity.md)

### S02-E01 — Sagas
- Class: **E1 / seminal distributed systems**
- Garcia-Molina & Salem, SIGMOD 1987.
- https://doi.org/10.1145/38713.38742
- Supports: long-lived work, compensation, partial failure, application-level semantics.
- Applies to: F09, F10.
- Limitation: compensation is not perfect rollback and does not by itself solve external-effect uncertainty.

### S02-E02 — TraceCompiler
- Class: **E3 / 2026 frontier**
- https://arxiv.org/abs/2608.02680
- Supports: recurring trajectories can be compiled into mostly deterministic workflows when producer→consumer dependencies are evidenced; unsafe/underdetermined structure may be refused.
- Applies to: F07, F08, F29.
- Limitation: recent evidence; needs tare-specific replay/qualification.

### S02-E03 — PROV-AGENT: Unified Provenance for Tracking AI Agent Interactions in Agentic Workflows
- Class: **E3 / provenance research**
- https://arxiv.org/abs/2508.02866
- Supports: typed provenance over prompts/actions/tool interactions/decisions.
- Applies to: F06, F09, F12.
- Limitation: provenance schema does not replace tare Authority, EvidenceFamily or effect semantics.

### S02-E04 — Google Gemini + Temporal durable agent example
- Class: **E4 / vendor engineering**
- https://ai.google.dev/gemini-api/docs/temporal-example
- Supports: practical composition of agent logic with durable workflow execution.
- Applies to: F07, F10.
- Limitation: example/mechanism evidence, not backend qualification for tare.tools.

### S02-E05 — Automata Learning versus Process Mining for User Journeys
- Class: **E3 / 2026 frontier**
- https://arxiv.org/abs/2604.03686
- Supports: reconstructing observed procedural behavior from event logs rather than trusting configured graphs alone.
- Applies to: F07, F36.

---

## Study 03 — Governance, Assurance, Audit & Evidence

**Living research:** [Constitutional Governance](../research/governance/constitutional-governance-decision-rights.md) · [Audit / Metrology](../research/governance/governance-assurance-audit-metrology.md) · [Assurance / Evolution](../research/governance/assurance-evolution-testing.md) · [Test Engineering](../research/assurance/test-engineering-scenario-gates.md)

### S03-E01 — Auditable Agents
- Class: **E3 / 2026 auditability research**
- https://arxiv.org/abs/2604.05485
- Supports: auditability as a systems property spanning policy checkability, attribution, lifecycle and evidence integrity.
- Applies to: F14, F15, F16.

### S03-E02 — SWE-Mutation
- Class: **E1/E2 / peer-reviewed empirical assurance**
- https://aclanthology.org/2026.findings-acl.1976/
- Supports: test-suite presence/coverage is weaker than discriminative fault-detection evidence; mutation is useful meta-assurance.
- Applies to: F15, F17, F37, F38.
- Limitation: coding-agent test adequacy does not transfer automatically to every assurance domain.

### S03-E03 — Beyond Component Testing: Validating Agentic AI Systems
- Class: **E3 / 2026 validation research**
- https://arxiv.org/abs/2607.29405
- Supports: agentic-system validation needs trajectory/system-level evidence beyond component tests.
- Applies to: F15, F38.

### S03-E04 — When the Judge Changes, So Does the Measurement
- Class: **E3 / evaluator metrology**
- https://arxiv.org/abs/2607.08535
- Supports: evaluator choice/drift changes measurement and therefore needs calibration/versioning.
- Applies to: F17, F33, F38.

### S03-E05 — NIST AI Risk Management Framework
- Class: **E1 / institutional framework**
- https://www.nist.gov/itl/ai-risk-management-framework
- Supports: risk-oriented governance/measurement/management rather than universal undifferentiated controls.
- Applies to: F14, control-effectiveness research.
- Limitation: management framework; not a tare.tools implementation spec.

### S03-E06 — FLARE: Agentic Coverage-Guided Fuzzing for LLM-Based Multi-Agent Systems
- Class: **E3 / adversarial validation**
- https://arxiv.org/abs/2604.05289
- Supports: trajectory/fault-space exploration beyond conventional line coverage.
- Applies to: F17, F38.

---

## Study 04 — Runtime, Capabilities, Isolation & Interoperability

**Living research:** [Runtime Ownership](../research/runtime/runtime-ownership-vendor-integration.md) · [Capability / Sandbox](../research/runtime/capability-sandbox-resources.md) · [Protocols & Interoperability](../research/runtime/protocols-interoperability.md)

### S04-E01 — Model Context Protocol specification, 2026-07-28
- Class: **E4 / official protocol specification**
- https://modelcontextprotocol.io/specification/2026-07-28
- Supports: protocol boundary semantics, context propagation/resource/tool interfaces.
- Applies to: F05, F20, F21.
- Limitation: MCP does not define tare canonical capability authority/effect semantics.

### S04-E02 — A2A Protocol specification
- Class: **E4 / official protocol specification**
- https://a2a-protocol.org/latest/specification/
- Supports: interoperation between independently managed/opaque agents.
- Applies to: F20, F21.
- Limitation: not evidence that A2A should be tare's internal bus.

### S04-E03 — OpenTelemetry Semantic Conventions
- Class: **E4 / observability specification**
- https://opentelemetry.io/docs/specs/semconv/
- Supports: portable telemetry projection and context propagation.
- Applies to: F21.
- Limitation: spans/events are not canonical EffectReceipt or OutcomeEvidence.

### S04-E04 — AI Code Sandboxes: A Comparative Security Study, Part 1
- Class: **E3 / sandbox security**
- https://arxiv.org/abs/2606.08433
- Supports: sandbox backends differ materially in isolation/security properties; configuration labels are insufficient.
- Applies to: F19, F22.

### S04-E05 — Confining AI Agent Code with Unprivileged Linux Primitives
- Class: **E3 / isolation research**
- https://arxiv.org/abs/2605.26298
- Supports: concrete host-primitive isolation mechanisms and their tradeoffs.
- Applies to: F19, F22.
- Limitation: Linux-specific mechanism; tare qualification must still include Windows-native paths.

### S04-E06 — Agent libOS
- Class: **E3**
- https://arxiv.org/abs/2606.03895
- Supports: runtime/capability split and long-running agent lifecycle.
- Applies to: F03, F05, F20.

### S04-E07 — Before the Tool Call: Deterministic Pre-Action Authorization
- Class: **E3 / 2026 authorization research**
- https://arxiv.org/abs/2603.20953
- Supports: policy authorization before effect execution with audit record.
- Applies to: F04, F05.

### S04-E08 — Capability Gates Are Not Authorization
- Class: **E3 / 2026 security research**
- https://arxiv.org/abs/2606.28679
- Supports: exposing a capability/tool is not equivalent to authorizing a concrete call/value set.
- Applies to: F04, F05.

### S04-E09 — CaMeL: Defeating Prompt Injections by Design
- Class: **E3 / security architecture**
- https://arxiv.org/abs/2503.18813
- Supports: separation of trusted control flow and untrusted data with capability-style constraints.
- Applies to: F04, F05.

---

## Study 05 — Routing, Adaptation, Economics & Resources

**Living research:** [Adaptive Routing](../research/routing/adaptive-routing-reputation.md) · [Economics / Resources](../research/routing/economics-resources-observability.md)

### S05-E01 — LLMRouterBench
- Class: **E1/E2 / peer-reviewed benchmark**
- https://aclanthology.org/2026.findings-acl.1881/
- Supports: sophisticated routing must be compared with simple/calibrated baselines; benchmark methodology matters.
- Applies to: F23, F24.

### S05-E02 — Agentic Harness Engineering
- Class: **E3**
- https://arxiv.org/abs/2604.25850
- Supports: harness-level adaptation can be separately measured and optimized.
- Applies to: F24, F26.
- Limitation: optimization does not bypass policy/eligibility.

### S05-E03 — Mesos
- Class: **E1 / systems scheduling**
- Hindman et al., NSDI 2011.
- https://people.eecs.berkeley.edu/~alig/papers/mesos.pdf
- Supports: explicit resource offers/constraints and separation of scheduling responsibilities.
- Applies to: resource-scheduling research in F26.

### S05-E04 — Omega: Flexible, Scalable Schedulers for Large Compute Clusters
- Class: **E1 / systems scheduling**
- https://research.google/pubs/omega-flexible-scalable-schedulers-for-large-compute-clusters/
- Supports: shared-state scheduling, conflicts and concurrency tradeoffs.
- Applies to: F26 and resource/routing coordination hypotheses.

### S05-E05 — Borg
- Class: **E1 / production systems evidence**
- https://research.google/pubs/large-scale-cluster-management-at-google-with-borg/
- Supports: resource management, priorities and operational scheduling at scale.
- Applies to: resource/economics analogies only.
- Limitation: cluster workload scheduling is not model routing semantics.

---

## Study 06 — Context, Memory, Learning & Evolution

**Living research:** [Context / Memory / Playbooks](../research/context/context-memory-playbooks.md) · [Canonical Lineage](../research/context/canonical-lineage-identity.md) · [Adaptive Learning](../research/context/adaptive-learning-cross-project-evolution.md)

### S06-E01 — Memory for Autonomous LLM Agents: Mechanisms, Evaluation, and Emerging Frontiers
- Class: **E3 / 2026 survey**
- https://arxiv.org/abs/2603.07670
- Supports: memory has moved beyond vector recall toward compression, hierarchical context, reflection/management; evaluation and contradiction remain open.
- Applies to: F27–F32.

### S06-E02 — MemoryAgentBench
- Class: **E1/E2 / ICLR 2026 benchmark**
- https://openreview.net/forum?id=DT7JyQC3MR
- Supports: memory requires dedicated incremental/multi-turn evaluation rather than anecdotal success.
- Applies to: F27, F30.

### S06-E03 — AdaCoM: Learning Agent-Compatible Context Management for Long-Horizon Tasks
- Class: **E3 / 2026 frontier**
- https://arxiv.org/abs/2605.30785
- Supports: context-management policy may need to be agent-compatible rather than globally fixed.
- Applies to: F28.

### S06-E04 — Beyond Compaction: Structured Context Eviction for Long-Horizon Agents
- Class: **E3 / 2026 frontier**
- https://arxiv.org/abs/2606.11213
- Supports: typed/dependency-aware eviction can preserve causal structure better than opaque summary compaction.
- Applies to: F27, F28.

### S06-E05 — Beyond Semantic Organization: Memory as Execution State Management for Long-Horizon Agents
- Class: **E3 / 2026 frontier**
- https://arxiv.org/abs/2606.06090
- Supports: execution-state/branch-aware memory rather than semantic-similarity-only organization.
- Applies to: F27, F28.

### S06-E06 — Contextual Drag: How Errors in the Context Affect LLM Reasoning
- Class: **E3 / 2026 context quality**
- https://arxiv.org/abs/2602.04288
- Supports: more retained context is not monotonically better; erroneous/stale context can degrade reasoning.
- Applies to: F27, F28.

### S06-E07 — Governance Decay: How Context Compaction Silently Erases Safety Constraints in Long-Horizon LLM Agents
- Class: **E3 / 2026 frontier**
- https://arxiv.org/abs/2606.22528
- Supports: lossy compaction can silently discard governance-relevant constraints.
- Applies to: F27–F29.
- Limitation: preprint evidence; project must reproduce relevant failure modes.

### S06-E08 — MemP: Exploring Agent Procedural Memory
- Class: **E3 / procedural memory**
- https://arxiv.org/abs/2508.06433
- Supports: reusable procedural memory as a separate form of agent knowledge.
- Applies to: F29, F30.

### S06-E09 — Self-Refine / CRITIC / critical survey of self-correction
- Class: **E1/E3 / self-improvement lineage**
- https://arxiv.org/abs/2303.17651
- https://openreview.net/forum?id=Sx038qxjek
- https://arxiv.org/abs/2406.01297
- Supports/challenges: iterative self-feedback may help, but autonomous self-correction is conditional and should not be conflated with independent validation.
- Applies to: F32, F33.

---

## Study 07 — Experience, Human Interface & Legacy Reconstruction

**Living research:** [TUI / REPL Experience](../research/experience/tui-repl-experience.md) · [Legacy Reconstruction](../research/experience/legacy-system-reconstruction.md)

### S07-E01 — Plover: Steering GUI Agents through Plan-Centric Interaction
- Class: **E3 / 2026 HCI frontier**
- https://arxiv.org/abs/2607.15193
- Supports: localized plan-centric steering/repair rather than full restart.
- Applies to: F34, F35.

### S07-E02 — AgentGUI: An Interface for Observing and Steering Long-Running AI Agents
- Class: **E3 / 2026 HCI frontier**
- https://arxiv.org/abs/2607.26300
- Supports: long-running agent supervision, trace comprehension and steering as explicit interface problems.
- Applies to: F34, F35.

### S07-E03 — Automata Learning versus Process Mining for User Journeys
- Class: **E3 / 2026 process reconstruction**
- https://arxiv.org/abs/2604.03686
- Supports: deriving behavioral models from event logs and combining process-mining/automata approaches.
- Applies to: F36.

### S07-E04 — TraceCompiler
- Class: **E3**
- https://arxiv.org/abs/2608.02680
- Supports: extraction of recurring procedures from traces with dependency evidence.
- Applies to: F36 and connection from legacy reconstruction to governed workflows.

---

## Study 08 — Research Methodology & Empirical Assurance

**Living research:** [Formal Research Program](../research/methodology/formal-research-program.md) · [CMRP & Epistemic Independence](../research/methodology/cmrp-and-epistemic-independence.md) · [Test Engineering](../research/assurance/test-engineering-scenario-gates.md)

### S08-E01 — RepoReason
- Class: **E2/E3 / repository-level benchmark**
- https://arxiv.org/abs/2601.03731
- Supports: repository-level reasoning requires evaluation beyond isolated snippets.
- Applies to: F37, F38.

### S08-E02 — SWE-Mutation
- Class: **E1/E2**
- https://aclanthology.org/2026.findings-acl.1976/
- Supports: discriminative oracle power matters more than test volume/coverage alone.
- Applies to: F37, F38.

### S08-E03 — When the Judge Changes, So Does the Measurement
- Class: **E3**
- https://arxiv.org/abs/2607.08535
- Supports: evaluator choice/version is part of the experimental instrument.
- Applies to: F17, F33, F38.

### S08-E04 — Agentic Harness Engineering
- Class: **E3**
- https://arxiv.org/abs/2604.25850
- Supports: evaluate harness modifications as controlled engineering changes rather than anecdotal prompt improvements.
- Applies to: F37, F38.

### S08-E05 — Critical Survey of LLM Self-Correction
- Class: **E1 / survey**
- https://arxiv.org/abs/2406.01297
- Supports: self-reflection/self-correction claims need external feedback/tooling/evaluation controls and must not be assumed generally reliable.
- Applies to: F33, F38.

---

## Experiment — Local AI Lab / recurrent memory

**Experiment:** [Recurrent Memory research line](../experiments/local-ai-lab/recurrent-memory/README.md)

This experiment intentionally uses **project-internal empirical evidence as primary evidence**. External recurrent-memory literature is discovery/interpretation context, not a substitute for the measured substrate. The live experiment therefore records exact model/runtime/config and qualified effect sizes; its historical bundles/handoffs remain recoverable outside HEAD.

---

## What is intentionally absent

The previous corpus contained many additional citations. They remain recoverable through Git/File Library and may be reintroduced when a living claim actually needs them. A source is not kept merely because it once appeared in a bibliography.

---

**Continue:** [Curated Findings →](../findings/CURATED_FINDINGS.md) · [Research Frontier](../frontier/RESEARCH_FRONTIER.md) · [Provenance Index](PROVENANCE_INDEX.md)
