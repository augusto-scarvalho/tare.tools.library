# Role 05 — Source & Identity Curator

**Run:** CMRP-2026-08-11-001

## Evidence classes used

| Source | Class | Review status / caveat | Use in this run |
|---|---|---|---|
| Madaan et al., Self-Refine, arXiv 2303.17651 | primary research preprint | influential; task-specific evaluation | supports iterative same-model refinement |
| Shinn et al., Reflexion, arXiv 2303.11366 | primary research preprint | environment feedback central | supports explicit reflection artifacts |
| Kamoi et al., TACL 2024, DOI 10.1162/tacl_a_00713 | peer-reviewed critical survey | strong synthesis; survey not direct local proof | constrains intrinsic self-correction claims |
| Tyen et al., Findings ACL 2024, DOI 10.18653/v1/2024.findings-acl.826 | peer-reviewed empirical | reasoning-error tasks | supports error-localization distinction |
| Yang et al., ACL 2025, DOI 10.18653/v1/2025.acl-long.203 | peer-reviewed empirical | self-correction decomposition | supports false-correction/confidence trade-off |
| Wu et al., arXiv 2511.07784 | preprint controlled debate | ground-truth logical task; not tare-specific | supports diversity/conformity analysis |
| Okawa, arXiv 2608.02827, accepted ICML 2026 | recent primary research | very recent; multi-agent debate contexts | supports biased-consensus risk |
| Google AI co-scientist blog/paper links | vendor research practice | not independent validation; auto-Elo caveat | supports role workflow precedent |
| MetaGPT, arXiv 2308.00352 | primary research preprint | software-specific | supports SOP/role workflow precedent |
| IF-CRITIC, ACL 2026 | peer-reviewed empirical | critic specialization | supports checklist/fine-grained critique |

## Identity notes

No source-family ambiguity discovered among the load-bearing references used for this run. arXiv papers remain version-pinned by identifier/version where relevant; ACL/TACL sources are referenced by DOI/Anthology identity. Google Research material is treated as vendor/research-practice evidence, not an independent oracle.

## Provenance rule for synthesis

Claims about the *local tare.tools method* remain inferences unless directly measured. External papers justify hypotheses and guardrails, not local PASS claims.
