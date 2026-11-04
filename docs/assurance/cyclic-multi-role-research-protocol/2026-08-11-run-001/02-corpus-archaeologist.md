# Role 02 — Corpus Archaeologist

**Run:** CMRP-2026-08-11-001  
**Epistemic independence:** `NOT_INDEPENDENT`  
**Scope:** internal tare.tools.research corpus only.

## Canonical internal anchors consulted

- `refresh-editions/2026-08-11/research-methodology-evidence/research-methodology-evidence-scientific-refresh-2026-08-11.html`
- `refresh-editions/2026-08-11/assurance-governance-quality/assurance-governance-quality-scientific-refresh-2026-08-11.html`
- `refresh-editions/2026-08-11/research-knowledge-substrate/research-knowledge-substrate-scientific-ideation-2026-08-11.html`
- `frontier/FRONTIER_MODEL.md`
- `frontier/decisions/2026-08-11-frontier-registry-adoption.md`
- `DOCUMENT_POLICY.md`
- `PROMOTION_POLICY.md`

## CURRENT supported by the local research repository

1. tare.tools.research already separates immutable historical material from derivative refreshes and proposals.
2. Research does not outrank Git/ADRs/SPECs/BDD/code; promotion is a separate boundary.
3. The methodology lineage already requires negative evidence, evaluator identity/qualification, candidate identity, delayed outcomes and epistemic-independence awareness.
4. `EvidenceFamily` is used conceptually to avoid counting nominally different evaluators as independent when they share a failure domain.
5. Research Frontier already distinguishes Pointer → Research Question → Hypothesis → Study → Finding → Gap → Task.
6. The current ChatGPT runtime cannot spawn general subagents; sequential same-model role execution is available as an operating technique but is not current tare.tools runtime capability.

## Historical/corpus ideas that support the investigation

- independent audit must not become management/approval;
- proposal agent should not be its own promotion authority;
- evaluator metrology matters more than judge count;
- static capability claims must be distinguished from runtime/effective proof;
- research artifacts should expose lineage, source quality, counter-evidence and ADOPT/ADAPT/RETIRE/OPEN status;
- intermediate artifacts and causal provenance are preferable to an opaque “final answer appeared” workflow.

## Canonical-equivalent check

No new Agent OS primitive is needed. If eventually executed by tare.tools, the method can be represented as a research Workflow composed of role-scoped work, artifacts, external capability use, validation/evidence and human/independent review. `ResearchRole`, `ResearchAgent` or `DebateAgent` should not become kernel primitives merely because this method uses those words.

## Main corpus tension

The corpus values independent validation, yet the proposed operating technique uses one model for all roles. Therefore the correct interpretation is:

> role separation may improve **process structure and coverage**, but it does not prove **epistemic independence**.

Any documentation that says “independent reviewers” for same-model sequential passes would contradict the existing EvidenceFamily/assurance direction.
