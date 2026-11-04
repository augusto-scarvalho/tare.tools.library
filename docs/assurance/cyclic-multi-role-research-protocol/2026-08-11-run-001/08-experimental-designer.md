# Role 08 — Experimental Designer

**Run:** CMRP-2026-08-11-001

## Qualification experiment

### Conditions

- **A — Single pass:** one model, one research prompt, no explicit role cycles.
- **B — Same-model CMRP:** same model, sequential functional roles, frozen artifacts, one adversarial revision cycle.
- **C — Same-model true multi-agent:** multiple isolated instances of the same model when runtime support exists.
- **D — Heterogeneous multi-agent:** different model families/runtimes for scout, critic and synthesis.
- **E — Heterogeneous + human/independent review:** strongest but most expensive reference condition.

### Task sample

Use 12–24 Research Frontier pointers stratified across:
- architecture-heavy;
- empirical/local-model;
- governance/assurance;
- protocol/current-vendor;
- cross-disciplinary bridge topics.

Plant controlled evidence conditions in a held-out benchmark:
- an authoritative source that contradicts the intuitive answer;
- duplicated source manifestations;
- a retracted/corrected source;
- a misleading vendor claim;
- a negative-result paper;
- a canonical-equivalent architectural trap;
- one seeded false CURRENT claim;
- one irrelevant but semantically similar source.

### Primary metrics

1. **Supported-claim precision** — claims with adequate source/evidence support.
2. **Contradiction recall** — planted contradictions discovered.
3. **Negative-evidence preservation** — false greens/falsifiers retained in final artifact.
4. **Source identity accuracy** — work/version/artifact correctly distinguished.
5. **Architectural duplication rate** — proposed primitives with existing canonical equivalents.
6. **False-correction rate** — initially correct claims damaged by later critique.
7. **Adversarial yield** — material defects found in the adversarial pass.
8. **Residual unsupported-claim rate** after final audit.
9. **Cost-to-trust** — tokens, calls, wall-clock and human minutes per accepted claim.
10. **Calibration** — confidence vs independently judged correctness.

### Secondary metrics

- coverage of CURRENT/TARGET/PROPOSED/RESEARCH;
- number of sources and source-family diversity;
- research-pointer quality discovered downstream;
- duplication/merge errors;
- reviewer actionability;
- cycle count and diminishing returns.

### Design

Paired repeated-measures: each research pointer is run under all conditions with frozen task/source-access constraints. Order randomized where practical. Final scoring uses hidden deterministic checks plus blinded human/heterogeneous review. Same-model role outputs are one EvidenceFamily.

### Stop rule

Do not keep cycling until the model says “done.” Stop when:
1. no new **material** evidence/contradiction is found in the last adversarial cycle;
2. all blocking checklist items are resolved or explicitly OPEN;
3. budget cap is reached; or
4. external validator/human escalation is required.

## Pilot status of this run

`RUN-001` is **methodological demonstration only (N=1)**. It can establish workflow feasibility and expose design flaws, but cannot establish comparative efficacy.
