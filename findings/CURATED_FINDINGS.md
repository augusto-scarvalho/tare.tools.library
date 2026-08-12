# Curated Findings — Semantic Preservation v2

`ADOPT / ADAPT / RETIRE / OPEN` are research dispositions, not canonical promotion.

| ID | Finding | Disposition | Primary study |
|---|---|---|---|
| F01 | user-space Agent OS is a better North-Star frame than super-agent | ADOPT | foundations |
| F02 | stable incumbent is an executable compatibility oracle | ADOPT | foundations |
| F03 | vendor-local / harness-owned / vendor-remote converge by external contracts | ADOPT | runtime |
| F04 | Authority precedes routing/reputation/economics | ADOPT | foundations/routing |
| F05 | Capability/Effect is semantic boundary; MCP is backend/protocol | ADOPT | runtime |
| F06 | Project is governance/applicability namespace, not just repo path | ADAPT | project |
| F07 | Project identity and revision are distinct | ADOPT | project/lineage |
| F08 | Workflow represents governed work, not agent topology | ADOPT | workflow |
| F09 | template, compiled/revisioned instance and trace are different roles | ADOPT | workflow |
| F10 | deterministic work is first-class; agents are one executor type | ADOPT | workflow |
| F11 | graph mutation/replan needs revision identity and normal Authority/Routing paths | ADOPT | workflow |
| F12 | Work identity should outlive runtime/session/model | ADOPT | workflow/lineage |
| F13 | attempt, logical effect, receipt, outcome and settlement are different claims | ADOPT | reliability |
| F14 | ambiguous completion reconciles before retry | ADOPT | reliability |
| F15 | exactly-once should be framed as one logical effect, not transport magic | ADAPT | reliability |
| F16 | compensation is a governed new effect, not perfect undo | ADOPT | reliability |
| F17 | Authority freshness at commit is distinct from historical Permit validity | OPEN/high | reliability/governance |
| F18 | observer/scanner is a measurement instrument requiring qualification | ADOPT | reliability/assurance |
| F19 | information survival is appraisal/reconstructability, not keep-everything-in-Git | ADOPT | information survival |
| F20 | Reconstructive Closure differs from bit reproducibility | ADOPT | information survival |
| F21 | physical storage path/backend does not own object identity/semantics | ADOPT | information survival |
| F22 | Demand/requirement lineage is needed to judge actual settlement | ADAPT/OPEN | demand |
| F23 | Governance is transversal; do not create monolithic GovernancePlane by default | ADOPT | governance |
| F24 | decision rights are distinct from capability and concrete Authority | ADOPT research | governance |
| F25 | root/constitutional amendment semantics remain open | OPEN | governance |
| F26 | expiring scoped waivers/emergency authority beat silent permanent exceptions | ADOPT research | governance |
| F27 | Validation, Assurance, Audit, Evidence, Authority and Observability have distinct ownership | ADOPT | assurance |
| F28 | finding from agent/auditor is hypothesis until supported/confirmed | ADOPT | audit |
| F29 | EvidenceFamily should represent effective independence, not vendor count | ADOPT | assurance |
| F30 | evaluator/judge/test suite is a measurement instrument needing metrology | ADOPT | assurance/method |
| F31 | manual verdict cannot mint mechanized proof | RETIRE old semantics | assurance case study |
| F32 | test/check count is not discriminative power | RETIRE proxy | assurance |
| F33 | candidate must not solely control evaluator/promotion proof | ADOPT | assurance/evolution |
| F34 | deterministic evidence reuse requires subject/dependency/oracle identity and freshness | ADAPT | assurance |
| F35 | protocol nouns do not automatically become kernel nouns | ADOPT | interoperability |
| F36 | ExecutionBinding is likely primary seam for concrete runtime/protocol realization | ADAPT | runtime/interop |
| F37 | compile smallest sufficient context/capability/authority view for each boundary | ADAPT/strong | interoperability/context |
| F38 | static/config capability parity does not prove runtime effectiveness | ADOPT empirical | vendor case study |
| F39 | declared→rendered/configured→loadable→enforced→effective is useful qualification model | ADAPT | vendor case study |
| F40 | sandbox/config label is not confinement proof | ADOPT | resources/case study |
| F41 | Windows/local-first and POSIX/CI both belong in qualification | ADOPT | runtime/resources |
| F42 | provider/model/runtime owner/commercial lane are distinct identities | ADOPT | routing |
| F43 | RouteDecision should be persisted before spawn | ADOPT | routing |
| F44 | reputation is evidence-derived view and never grants eligibility | ADOPT | routing |
| F45 | global priors + project-local posteriors is safer than one global score | ADAPT | routing/learning |
| F46 | cross-project transfer requires applicability/transportability + negative-transfer measurement | ADOPT research | learning |
| F47 | cost-to-trust is more useful than token cost alone | ADOPT research | economics |
| F48 | context is a projection; Project truth must survive outside context window | ADOPT | context |
| F49 | prefer durable refs/rehydration to opaque summaries where possible | ADOPT | context |
| F50 | more context is not monotonically better; stale/wrong context can harm | ADOPT | context |
| F51 | skills/playbooks/procedures inform but do not grant Authority | ADOPT | context |
| F52 | mature procedural learning can reduce agency by compiling proven structure | ADOPT | workflow/learning |
| F53 | scope of evidence bounds scope of learning | ADOPT | learning |
| F54 | agent feedback is sensor/hypothesis, not learned truth | ADOPT | learning |
| F55 | learning loop cannot promote itself | ADOPT | evolution |
| F56 | lineage is compositional; no Identity Plane is justified by research alone | ADOPT/RETIRE monolith | lineage |
| F57 | chronological trace/provenance does not prove causation | ADOPT | lineage |
| F58 | Experience/TUI projects canonical state and emits governed steering | ADOPT | experience |
| F59 | Stable REPL is valuable semantic interface for humans/automation/accessibility | ADOPT | experience |
| F60 | legacy NLU systems contain semantic/procedural/transactional knowledge worth reconstructing | ADOPT | reconstruction |
| F61 | research quality is not template compliance, source count or document volume | RETIRE proxy | methodology |
| F62 | same-model cyclic roles are structured test-time compute, not independent EvidenceFamily | ADOPT empirical | CMRP |
| F63 | negative evidence and false greens are first-class research assets | ADOPT | methodology |
| F64 | verifier may execute right bytes while enumerating wrong candidate test universe | ADOPT empirical | FSV/MXC case |
| F65 | enumeration and execution must use same frozen candidate identity | ADOPT empirical | FSV/MXC case |
| F66 | external evidence backend can remove manual ZIP relay without becoming semantic authority | ADOPT empirical | Agent Relay |
| F67 | local mount path is observation, not evidence identity | ADOPT empirical | Agent Relay |
| F68 | synthetic dense post-hoc Memory Caching remains PARKED | RETIRE active hypothesis | RNN lab |
| F69 | historical recurrent-state information presence is qualified on exact substrate | ADOPT empirical/local | RNN lab |
| F70 | historical-state recovery utility remains NOT_TESTED | OPEN | RNN lab |
| F71 | semantic curation must remove redundancy without erasing study depth | ADOPT dogfood | repo curation |
