# Research Reading Guide

**Status:** RESEARCH navigation surface. This file is an index, not a synthesis and not an authority source.

Use this page to choose a research trail. Each item links to the deeper document that owns the question.

## 1. Arquitetura e adoção do Agent OS

1. [Agent OS Foundations](../research/foundations/agent-os-foundations.md)
2. [Project / Workspace Admission & Adoption](../research/project/project-admission-adoption.md)
3. [Runtime Ownership & Vendor Integration](../research/runtime/runtime-ownership-vendor-integration.md)
4. [Protocols & Interoperability](../research/runtime/protocols-interoperability.md)

**Pergunta central:** como evoluir o stable incumbent para um Agent Operating System em user space sem semantic capture, big-bang ou monólito por vendor?

## 2. Trabalho durável, workflow e efeitos

1. [Workflow as Governed Work](../research/work/workflow-governed-work.md)
2. [Reliability Semantics & Effect Reconciliation](../research/work/reliability-effect-reconciliation.md)
3. [Information Survival & Reconstructive Assurance](../research/work/information-survival-reconstructability.md)
4. [Demand Lineage, Context Reconstruction & Settlement](../research/work/demand-lineage-settlement.md)

**Pergunta central:** como uma necessidade vira trabalho governado, efeitos observáveis e settlement sem perder identidade, causalidade ou estado sob partial failure?

## 3. Governança, assurance e ciência de testes

1. [Constitutional Governance & Decision Rights](../research/governance/constitutional-governance-decision-rights.md)
2. [Governance Assurance & Audit](../research/governance/governance-assurance-audit-metrology.md)
3. [Assurance, Testing Science & Governed Evolution](../research/governance/assurance-evolution-testing.md)
4. [Test Engineering, Scenario Gates & Regression Treasury](../research/assurance/test-engineering-scenario-gates.md)

**Pergunta central:** quem pode decidir, que evidência torna uma claim defensável, quão bons são nossos instrumentos e quem pode promover mudança?

## 4. Runtime, capabilities, sandbox e vendors

1. [Vendor CLI / Agent Runtime Landscape](../research/runtime/vendor-cli-runtime-landscape.md)
2. [Runtime Ownership & Vendor Integration](../research/runtime/runtime-ownership-vendor-integration.md)
3. [Capability, Sandbox, Resources & Isolation](../research/runtime/capability-sandbox-resources.md)
4. [Protocols & Interoperability](../research/runtime/protocols-interoperability.md)
5. [Kimi / Antigravity Capability-Parity Case Study](../case-studies/vendor-runtime/kimi-antigravity-capability-parity.md)

**Pergunta central:** o que cada runtime/vendor realmente possui e como convergir comportamentos distintos em contratos canônicos externos?

## 5. Routing, reputation, economics e resources

1. [Adaptive Routing, Reputation & Qualification](../research/routing/adaptive-routing-reputation.md)
2. [Economics, Resources & Observability](../research/routing/economics-resources-observability.md)
3. [Adaptive Routing Technical Proposal](../proposals/adaptive-routing.md)

**Pergunta central:** entre opções já autorizadas, qual realização concreta escolher e como aprender sem transformar reputação/economia em autoridade?

## 6. Context, lineage, memory e evolution

1. [Context, Memory & Playbooks](../research/context/context-memory-playbooks.md)
2. [Canonical Lineage & Compositional Identity](../research/context/canonical-lineage-identity.md)
3. [Adaptive Learning, Cross-Project Experience & Self-Evolution](../research/context/adaptive-learning-cross-project-evolution.md)
4. [Canonical Lineage Technical Proposal](../proposals/canonical-lineage.md)

**Pergunta central:** o que mostrar ao executor agora, como reconstruir a história depois e até onde uma experiência pode legitimamente alterar comportamento futuro?

## 7. Experience, TUI/REPL e reconstrução de sistemas legados

1. [TUI / REPL / Human-Agent Experience](../research/experience/tui-repl-experience.md)
2. [Executable / Cognitive System Reconstruction](../research/experience/legacy-system-reconstruction.md)

**Pergunta central:** como humanos observam e steer o sistema sem criar shadow truth, e como sistemas NLU/BPM/RPA antigos podem ser semanticamente reconstruídos?

## 8. Local inference e consumer-GPU lab

1. [Local Inference & Consumer-GPU Model Lab Methodology](../research/local-inference/local-model-lab-methodology.md)
2. [Local Model Landscape, Fine-tunes & Evidence Grading](../research/local-inference/model-landscape-finetunes.md)
3. [HumanEval Scoring Harness Failure](../case-studies/local-inference/humaneval-scoring-harness-failure.md)
4. [Recurrent Memory Research Line](../experiments/local-ai-lab/recurrent-memory/README.md)

**Pergunta central:** como qualificar modelos locais como first-class candidates sem confundir base model, quantização, runtime, kernels, hardware e benchmark harness?

## 9. Metodologia científica e independência epistêmica

1. [Formal Research Program](../research/methodology/formal-research-program.md)
2. [CMRP, Multi-Role Research & Epistemic Independence](../research/methodology/cmrp-and-epistemic-independence.md)
3. [CMRP Run 001](../experiments/research-methodology/cmrp-run-001.md)
4. [Test Engineering, Scenario Gates & Regression Treasury](../research/assurance/test-engineering-scenario-gates.md)

**Pergunta central:** como produzir e desafiar conhecimento sem confundir volume documental, same-model review, benchmark score ou test count com evidência independente?

## 10. Estado condensado e continuidade

- [Curated Findings](../findings/CURATED_FINDINGS.md) — o que a pesquisa atualmente suporta, com `ADOPT / ADAPT / RETIRE / OPEN`.
- [Research Frontier](../frontier/RESEARCH_FRONTIER.md) — perguntas ainda abertas e experimentos prioritários.
- [Selected Evidence](../sources/SELECTED_EVIDENCE.md) — evidence registry por claim.
- [Provenance Index](../sources/PROVENANCE_INDEX.md) — origem e identidade das linhas preservadas.
- [Curation Ledger](../catalog/CURATION_LEDGER.md) — o que foi preservado, absorvido, bridge ou history-only.
- [Deep-Artifact Rehydration Gaps](../catalog/REHYDRATION_GAPS.md) — estudos profundos cujos bytes exatos ainda precisam ser materializados da File Library.

## Regra de leitura

`Synthesis/Guide → Deep Research → Proposal (PROPOSED) → Experiment/Case Study → Finding → Frontier`.

Se houver conflito sobre CURRENT/TARGET, volte ao repositório canônico `tare-tools`: research informa e desafia arquitetura, mas não a promove sozinho.
