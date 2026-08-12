# Deep-Artifact Rehydration Gaps — Semantic Preservation v2

**Purpose:** make incompleteness explicit. The preservation editions in `research/` retain the major intellectual content and structure, but several deepest 2026-08-10/12 HTML artifacts are still exact only in File Library, not materialized as Git blobs in this branch.

They are **not lost** and must not be reconstructed from snippets and labeled “original”. When a connector/export path exposes exact bytes, materialize them as source editions and verify identity before changing this status.

## P0 exact artifacts to rehydrate

| Artifact | File Library / identity evidence | Current V2 treatment |
|---|---|---|
| `tare_tools_reliability_effect_reconciliation_scientific_research_2026-08-10.html` | `file_00000000f928820eaa8932ec2a898510`; SHA-256 `6b283ea7962780410952f1ae12a0d08ba4b86837471f4a09489deb60f15ca419`; 72,526 B / 43 sections / 70 refs | preservation edition + bridge runtime/reliability refresh |
| `tare_tools_reliability_effect_reconciliation_implementation_proposal_2026-08-10.html` | manifest SHA-256 `0baad9fa4d517ba8826bcdd2b5af2609abe34c1a973978f9a146d117af3ce622`; 65,552 B / 48 sections | specific proposal preserved |
| `tare_tools_governance_assurance_audit_scientific_research_2026-08-10.html` | `file_00000000df4c820e80676f9df313a47f`; SHA-256 `f3986251f7cf83bcd5b92a35a95820866e254865fc8ec38458b3aed8dfa44ff3`; 82,228 B | preservation edition + assurance bridge |
| `tare_tools_governance_assurance_audit_implementation_proposal_2026-08-10.html` | SHA-256 `fd2c543fbad2d18ed0e630ad65ea74bd9e166495bc5e3e237c33365457a64492`; 61,936 B | specific proposal preserved |
| `tare_tools_workflow_governed_work_scientific_research_2026-08-11.html` | File Library `file_000000005d90820e8a116006ddc0c53c`; historical package reports 36 content chapters + bibliography / 81 references | preservation edition + workflow bridge |
| `tare_tools_workflow_governed_work_implementation_proposal_2026-08-11.html` | referenced as P0 exact-source-not-materialized in historical catalog | specific proposal preserved |
| `tare_tools_canonical_lineage_identity_governance_scientific_research_2026-08-12.html` | `file_00000000c4a8820eb800aa8529b7bcbc`; SHA-256 `6763f042d36b71a9b803891d141df161c6d1b70f8e97c9e4cca5f40d5c6dc05f` | preservation edition |
| `tare_tools_adaptive_learning_cross_project_evolution_scientific_research_2026-08-12.html` | package SHA-256 `4b165123cf0f32084df30bf11f1fef6d5456e504b913f9adaef69e8318055264` | preservation edition |
| `tare_tools_information_survival_reconstructability_scientific_research_2026-08-12.html` | `file_00000000a0dc820eb1ec12531be3783e` | preservation edition |
| `tare_tools_demand_lineage_context_learning_scientific_research_2026-08-12.html` | exact File Library package member | preservation edition `demand-lineage-settlement.md` |
| `tare_tools_interoperability_learning_evolution_scientific_research_2026-08-10.html` | historical corpus reference; exact bytes in File Library | preservation edition + protocol bridge |
| `local_ai_lab_recurrent_memory_empirical_history_2026-08-12.html` and companion science/backlog | exact File Library research pack | split preservation experiment docs |

## Correct future operation

1. obtain exact bytes from File Library/export surface;
2. verify known SHA/manifest identity when available;
3. place under a clearly marked `source-editions/` or equivalent location;
4. compare preservation edition against exact source for false-negative omissions;
5. keep one preferred living study plus exact source edition only when the latter adds inspectable scientific depth;
6. never promote research status during rehydration.

Until then, V2 is **semantically preserved but not byte-complete for the newest deep-study generation**.
