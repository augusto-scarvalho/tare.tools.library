# Curated Findings — 2026-08-12

Este ledger registra conclusões que sobreviveram ao pente-fino sem exigir que o leitor abra dezenas de versões históricas. `ADOPT/ADAPT/RETIRE/OPEN` aqui é classificação de pesquisa; não ratifica TARGET.

| ID | Finding | Status | Principal sucessor |
|---|---|---|---|
| F01 | tare.tools é melhor modelado como Agent OS em user space, não super-agent | ADOPT | Study 01 |
| F02 | stable incumbent é compatibility oracle e deve ser estrangulado incrementalmente | ADOPT | Study 01 |
| F03 | vendor-local / harness-owned / vendor-remote convergem por contracts externos | ADOPT | Study 01/04 |
| F04 | Authority precede routing/reputation/economics | ADOPT | Study 01/05 |
| F05 | Capability/Effect é boundary semântico; MCP é backend/protocol | ADOPT | Study 01/04 |
| F06 | Work identity deve sobreviver a Agent/Model/runtime attempts | ADOPT | Study 02 |
| F07 | Workflow representa progressão de governed work, não agent graph | ADOPT | Study 02 |
| F08 | Template/compiled instance/trace são roles diferentes | ADOPT | Study 02 |
| F09 | attempt, logical effect, evidence, outcome e settlement são claims distintos | ADOPT | Study 02 |
| F10 | completion ambígua exige reconciliation antes de retry | ADOPT | Study 02 |
| F11 | authority freshness no commit é separada da validade histórica do Permit | OPEN→high priority | Study 02/03 |
| F12 | information survival é problema de appraisal/reconstructability, não “guardar tudo no Git” | ADOPT | Study 02 |
| F13 | Reconstructive Closure é distinta de bit reproducibility | ADOPT | Study 02 |
| F14 | Governance é transversal; não precisa de GovernancePlane monolítico | ADOPT | Study 03 |
| F15 | claim→oracle→evidence é unidade de assurance melhor que gate/tool count | ADOPT | Study 03 |
| F16 | EvidenceFamily deve medir independência efetiva, não vendor count | ADOPT | Study 03 |
| F17 | auditor/judge/test suite é instrumento e requer metrology/calibration | ADOPT | Study 03/08 |
| F18 | manual verdict não pode mintar mechanized proof | RETIRE old semantics | Study 03 |
| F19 | static/config capability parity não prova runtime effectiveness | ADOPT empirical negative | Study 03/04 |
| F20 | external dependency saudável precisa passar semantic exit test | ADOPT | Study 04 |
| F21 | OTel/OpenLineage/SLSA/in-toto são projections/attestations, não canonical truth | ADOPT | Study 04 |
| F22 | Windows/local-first e POSIX/CI devem fazer parte de qualification | ADOPT | Study 04 |
| F23 | routing deve persistir RouteDecision antes do spawn | ADOPT | Study 05 |
| F24 | global priors + project-local posteriors é direção mais segura que score global | ADAPT/OPEN | Study 05/06 |
| F25 | provider, model, runtime owner e commercial lane não são a mesma identidade | ADOPT | Study 05 |
| F26 | cost-to-trust é objetivo econômico mais útil que token cost isolado | ADOPT for research | Study 05 |
| F27 | context é projection temporária; project truth precisa sobreviver fora dela | ADOPT | Study 06 |
| F28 | compaction deve preferir durable refs/rehydration a opaque summaries | ADOPT | Study 06 |
| F29 | skills/playbooks/procedures não concedem authority | ADOPT | Study 06 |
| F30 | scope of evidence bounds scope of learning | ADOPT | Study 06 |
| F31 | agent feedback é sensor/hipótese, não learned truth | ADOPT | Study 06 |
| F32 | learning loop não pode promover a si próprio | ADOPT | Study 06 |
| F33 | same-model cyclic roles não são independent EvidenceFamily | ADOPT empirical/methodological | Study 06/08 |
| F34 | Experience deve projetar state canônico e emitir governed steering | ADOPT | Study 07 |
| F35 | Stable REPL é interface semântica útil para humanos/máquinas/accessibility | ADOPT | Study 07 |
| F36 | sistemas NLU legados contêm conhecimento semantic/procedural/transactional; não devem ser apenas “LLMificados” | ADOPT | Study 07 |
| F37 | research quality não pode ser inferida de template/source count/recency | RETIRE | Study 08 |
| F38 | negative evidence e measurement validity são first-class | ADOPT | Study 08 |
| F39 | synthetic dense post-hoc Memory Caching permanece PARKED | RETIRE from active hypothesis | Experiment recurrent memory |
| F40 | historical recurrent state information presence foi qualificada; recovery utility permanece NOT_TESTED | OPEN | Experiment recurrent memory |
