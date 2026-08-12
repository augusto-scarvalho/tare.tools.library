# Curated Findings — Semantic Preservation v2

[← Findings Index](README.md) · [Repository Navigation](../NAVIGATION.md) · [Living Research](../research/README.md) · [Research Frontier](../frontier/RESEARCH_FRONTIER.md)

`ADOPT / ADAPT / RETIRE / OPEN` are research dispositions, not canonical promotion. Follow the linked primary study before using a finding to justify architecture or implementation.

| ID | Finding | Disposition | Primary study |
|---|---|---|---|
| F01 | user-space Agent OS is a better North-Star frame than super-agent | ADOPT | [Agent OS Foundations](../research/foundations/agent-os-foundations.md) |
| F02 | stable incumbent is an executable compatibility oracle | ADOPT | [Agent OS Foundations](../research/foundations/agent-os-foundations.md) |
| F03 | vendor-local / harness-owned / vendor-remote converge by external contracts | ADOPT | [Runtime Ownership](../research/runtime/runtime-ownership-vendor-integration.md) |
| F04 | Authority precedes routing/reputation/economics | ADOPT | [Foundations](../research/foundations/agent-os-foundations.md) / [Routing](../research/routing/adaptive-routing-reputation.md) |
| F05 | Capability/Effect is semantic boundary; MCP is backend/protocol | ADOPT | [Capability/Sandbox](../research/runtime/capability-sandbox-resources.md) / [Protocols](../research/runtime/protocols-interoperability.md) |
| F06 | Project is governance/applicability namespace, not just repo path | ADAPT | [Project Admission](../research/project/project-admission-adoption.md) |
| F07 | Project identity and revision are distinct | ADOPT | [Project Admission](../research/project/project-admission-adoption.md) / [Canonical Lineage](../research/context/canonical-lineage-identity.md) |
| F08 | Workflow represents governed work, not agent topology | ADOPT | [Workflow](../research/work/workflow-governed-work.md) |
| F09 | template, compiled/revisioned instance and trace are different roles | ADOPT | [Workflow](../research/work/workflow-governed-work.md) |
| F10 | deterministic work is first-class; agents are one executor type | ADOPT | [Workflow](../research/work/workflow-governed-work.md) |
| F11 | graph mutation/replan needs revision identity and normal Authority/Routing paths | ADOPT | [Workflow](../research/work/workflow-governed-work.md) |
| F12 | Work identity should outlive runtime/session/model | ADOPT | [Workflow](../research/work/workflow-governed-work.md) / [Lineage](../research/context/canonical-lineage-identity.md) |
| F13 | attempt, logical effect, receipt, outcome and settlement are different claims | ADOPT | [Reliability](../research/work/reliability-effect-reconciliation.md) |
| F14 | ambiguous completion reconciles before retry | ADOPT | [Reliability](../research/work/reliability-effect-reconciliation.md) |
| F15 | exactly-once should be framed as one logical effect, not transport magic | ADAPT | [Reliability](../research/work/reliability-effect-reconciliation.md) |
| F16 | compensation is a governed new effect, not perfect undo | ADOPT | [Reliability](../research/work/reliability-effect-reconciliation.md) |
| F17 | Authority freshness at commit is distinct from historical Permit validity | OPEN/high | [Reliability](../research/work/reliability-effect-reconciliation.md) / [Governance](../research/governance/constitutional-governance-decision-rights.md) |
| F18 | observer/scanner is a measurement instrument requiring qualification | ADOPT | [Reliability](../research/work/reliability-effect-reconciliation.md) / [Audit/Metrology](../research/governance/governance-assurance-audit-metrology.md) |
| F19 | information survival is appraisal/reconstructability, not keep-everything-in-Git | ADOPT | [Information Survival](../research/work/information-survival-reconstructability.md) |
| F20 | Reconstructive Closure differs from bit reproducibility | ADOPT | [Information Survival](../research/work/information-survival-reconstructability.md) |
| F21 | physical storage path/backend does not own object identity/semantics | ADOPT | [Information Survival](../research/work/information-survival-reconstructability.md) |
| F22 | Demand/requirement lineage is needed to judge actual settlement | ADAPT/OPEN | [Demand / Settlement](../research/work/demand-lineage-settlement.md) |
| F23 | Governance is transversal; do not create monolithic GovernancePlane by default | ADOPT | [Constitutional Governance](../research/governance/constitutional-governance-decision-rights.md) |
| F24 | decision rights are distinct from capability and concrete Authority | ADOPT research | [Constitutional Governance](../research/governance/constitutional-governance-decision-rights.md) |
| F25 | root/constitutional amendment semantics remain open | OPEN | [Constitutional Governance](../research/governance/constitutional-governance-decision-rights.md) |
| F26 | expiring scoped waivers/emergency authority beat silent permanent exceptions | ADOPT research | [Constitutional Governance](../research/governance/constitutional-governance-decision-rights.md) |
| F27 | Validation, Assurance, Audit, Evidence, Authority and Observability have distinct ownership | ADOPT | [Governance Assurance & Audit](../research/governance/governance-assurance-audit-metrology.md) |
| F28 | finding from agent/auditor is hypothesis until supported/confirmed | ADOPT | [Governance Assurance & Audit](../research/governance/governance-assurance-audit-metrology.md) |
| F29 | EvidenceFamily should represent effective independence, not vendor count | ADOPT | [Governance Assurance & Audit](../research/governance/governance-assurance-audit-metrology.md) |
| F30 | evaluator/judge/test suite is a measurement instrument needing metrology | ADOPT | [Audit/Metrology](../research/governance/governance-assurance-audit-metrology.md) / [Research Method](../research/methodology/formal-research-program.md) |
| F31 | manual verdict cannot mint mechanized proof | RETIRE old semantics | [Governance Assurance & Audit](../research/governance/governance-assurance-audit-metrology.md) |
| F32 | test/check count is not discriminative power | RETIRE proxy | [Test Engineering](../research/assurance/test-engineering-scenario-gates.md) |
| F33 | candidate must not solely control evaluator/promotion proof | ADOPT | [Assurance / Evolution](../research/governance/assurance-evolution-testing.md) |
| F34 | deterministic evidence reuse requires subject/dependency/oracle identity and freshness | ADAPT | [Assurance / Evolution](../research/governance/assurance-evolution-testing.md) |
| F35 | protocol nouns do not automatically become kernel nouns | ADOPT | [Protocols & Interoperability](../research/runtime/protocols-interoperability.md) |
| F36 | ExecutionBinding is likely primary seam for concrete runtime/protocol realization | ADAPT | [Runtime Ownership](../research/runtime/runtime-ownership-vendor-integration.md) / [Protocols](../research/runtime/protocols-interoperability.md) |
| F37 | compile smallest sufficient context/capability/authority view for each boundary | ADAPT/strong | [Protocols](../research/runtime/protocols-interoperability.md) / [Context](../research/context/context-memory-playbooks.md) |
| F38 | static/config capability parity does not prove runtime effectiveness | ADOPT empirical | [Kimi/Antigravity case](../case-studies/vendor-runtime/kimi-antigravity-capability-parity.md) |
| F39 | declared→rendered/configured→loadable→enforced→effective is useful qualification model | ADAPT | [Kimi/Antigravity case](../case-studies/vendor-runtime/kimi-antigravity-capability-parity.md) |
| F40 | sandbox/config label is not confinement proof | ADOPT | [Capability/Sandbox](../research/runtime/capability-sandbox-resources.md) / [Kimi case](../case-studies/vendor-runtime/kimi-antigravity-capability-parity.md) |
| F41 | Windows/local-first and POSIX/CI both belong in qualification | ADOPT | [Runtime Ownership](../research/runtime/runtime-ownership-vendor-integration.md) / [Local Model Lab](../research/local-inference/local-model-lab-methodology.md) |
| F42 | provider/model/runtime owner/commercial lane are distinct identities | ADOPT | [Adaptive Routing](../research/routing/adaptive-routing-reputation.md) |
| F43 | RouteDecision should be persisted before spawn | ADOPT | [Adaptive Routing](../research/routing/adaptive-routing-reputation.md) |
| F44 | reputation is evidence-derived view and never grants eligibility | ADOPT | [Adaptive Routing](../research/routing/adaptive-routing-reputation.md) |
| F45 | global priors + project-local posteriors is safer than one global score | ADAPT | [Adaptive Routing](../research/routing/adaptive-routing-reputation.md) / [Adaptive Learning](../research/context/adaptive-learning-cross-project-evolution.md) |
| F46 | cross-project transfer requires applicability/transportability + negative-transfer measurement | ADOPT research | [Adaptive Learning](../research/context/adaptive-learning-cross-project-evolution.md) |
| F47 | cost-to-trust is more useful than token cost alone | ADOPT research | [Economics / Resources](../research/routing/economics-resources-observability.md) |
| F48 | context is a projection; Project truth must survive outside context window | ADOPT | [Context / Memory](../research/context/context-memory-playbooks.md) |
| F49 | prefer durable refs/rehydration to opaque summaries where possible | ADOPT | [Context / Memory](../research/context/context-memory-playbooks.md) |
| F50 | more context is not monotonically better; stale/wrong context can harm | ADOPT | [Context / Memory](../research/context/context-memory-playbooks.md) |
| F51 | skills/playbooks/procedures inform but do not grant Authority | ADOPT | [Context / Memory](../research/context/context-memory-playbooks.md) |
| F52 | mature procedural learning can reduce agency by compiling proven structure | ADOPT | [Workflow](../research/work/workflow-governed-work.md) / [Adaptive Learning](../research/context/adaptive-learning-cross-project-evolution.md) |
| F53 | scope of evidence bounds scope of learning | ADOPT | [Adaptive Learning](../research/context/adaptive-learning-cross-project-evolution.md) |
| F54 | agent feedback is sensor/hypothesis, not learned truth | ADOPT | [Adaptive Learning](../research/context/adaptive-learning-cross-project-evolution.md) |
| F55 | learning loop cannot promote itself | ADOPT | [Adaptive Learning](../research/context/adaptive-learning-cross-project-evolution.md) |
| F56 | lineage is compositional; no Identity Plane is justified by research alone | ADOPT/RETIRE monolith | [Canonical Lineage](../research/context/canonical-lineage-identity.md) |
| F57 | chronological trace/provenance does not prove causation | ADOPT | [Canonical Lineage](../research/context/canonical-lineage-identity.md) |
| F58 | Experience/TUI projects canonical state and emits governed steering | ADOPT | [TUI / REPL Experience](../research/experience/tui-repl-experience.md) |
| F59 | Stable REPL is valuable semantic interface for humans/automation/accessibility | ADOPT | [TUI / REPL Experience](../research/experience/tui-repl-experience.md) |
| F60 | legacy NLU systems contain semantic/procedural/transactional knowledge worth reconstructing | ADOPT | [Legacy Reconstruction](../research/experience/legacy-system-reconstruction.md) |
| F61 | research quality is not template compliance, source count or document volume | RETIRE proxy | [Formal Research Program](../research/methodology/formal-research-program.md) |
| F62 | same-model cyclic roles are structured test-time compute, not independent EvidenceFamily | ADOPT empirical | [CMRP research](../research/methodology/cmrp-and-epistemic-independence.md) / [CMRP Run 001](../experiments/research-methodology/cmrp-run-001.md) |
| F63 | negative evidence and false greens are first-class research assets | ADOPT | [Case Studies](../case-studies/README.md) |
| F64 | verifier may execute right bytes while enumerating wrong candidate test universe | ADOPT empirical | [FSV/MXC case](../case-studies/validation/fsv-mxc-staged-candidate-enumeration.md) |
| F65 | enumeration and execution must use same frozen candidate identity | ADOPT empirical | [FSV/MXC case](../case-studies/validation/fsv-mxc-staged-candidate-enumeration.md) |
| F66 | external evidence backend can remove manual ZIP relay without becoming semantic authority | ADOPT empirical | [Agent Relay Q0](../case-studies/evidence-exchange/agent-relay-q0.md) |
| F67 | local mount path is observation, not evidence identity | ADOPT empirical | [Agent Relay Q0](../case-studies/evidence-exchange/agent-relay-q0.md) |
| F68 | synthetic dense post-hoc Memory Caching remains PARKED | RETIRE active hypothesis | [Recurrent Memory experiments](../experiments/local-ai-lab/recurrent-memory/README.md) |
| F69 | historical recurrent-state information presence is qualified on exact substrate | ADOPT empirical/local | [Recurrent Memory experiments](../experiments/local-ai-lab/recurrent-memory/README.md) |
| F70 | historical-state recovery utility remains NOT_TESTED | OPEN | [RNN-06D](../experiments/local-ai-lab/recurrent-memory/backlog-rnn-06d.md) |
| F71 | semantic curation must remove redundancy without erasing study depth | ADOPT dogfood | [Semantic Curation V1 failure](../case-studies/research-repository/semantic-curation-v1-failure.md) |

---

**Continue:** [Research Frontier →](../frontier/RESEARCH_FRONTIER.md) · [Selected Evidence](../sources/SELECTED_EVIDENCE.md) · [Living Research](../research/README.md)
