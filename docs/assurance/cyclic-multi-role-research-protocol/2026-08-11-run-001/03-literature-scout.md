# Role 03 — Consolidated Literature Scout

**Run:** CMRP-2026-08-11-001  
**Mission:** search for established evidence on iterative refinement, critique and structured role workflows before considering tare.tools architecture.

## Positive evidence

### Self-Refine — Madaan et al. (2023)
A single model alternates generation, feedback and refinement. Across seven tasks, the paper reports improvements over one-step generation, especially where outputs have multiple constraints or subjective quality dimensions. The same underlying model performs all phases.

**Implication:** single-model iterative role separation can add value; multi-agent independence is not necessary for every improvement.

### Reflexion — Shinn et al. (2023)
Language agents use verbal reflections over task feedback stored as episodic memory to improve later trials.

**Implication:** explicit intermediate feedback artifacts can be operationally useful, particularly when grounded in environment feedback rather than introspection alone.

### MetaGPT — Hong et al. (2023)
Encodes standardized operating procedures and role separation to reduce inconsistency in collaborative software work.

**Implication:** explicit workflow/role contracts can improve coordination, but the result does not prove that nominal roles are independent evaluators.

### Critique/review specialization
CritiqueLLM and later reviewer/critic work show that informative critique itself is a capability that can be trained/evaluated rather than assumed from general model quality.

**Implication:** tare.tools should qualify a research role by observed performance, not by its prompt label.

## Negative/limiting evidence

### Critical survey of self-correction — Kamoi et al. (TACL 2024)
The survey concludes that prompted intrinsic self-correction lacks robust evidence of success except in unusually suitable tasks, while reliable external feedback substantially improves the picture.

### Error localization — Tyen et al. (ACL Findings 2024)
Models often struggle to find logical mistakes but can correct them when the mistake location is supplied.

**Implication:** the critic role should focus on evidence acquisition/error localization and checklist-based falsification, not assume that “think harder” creates a reliable oracle.

### Confidence vs Critique — Yang et al. (ACL 2025)
Self-correction contains distinct confidence-preservation and critique/correction behaviors that can trade off under prompting.

**Implication:** cycles can damage correct outputs as well as repair incorrect ones; we need false-correction metrics.

## Consolidated interpretation after this pass

The literature supports **iterative decomposition** and **feedback-driven refinement**, but it does not support equating same-model role switches with independent review. The method should be framed as structured test-time research compute whose reliability depends heavily on feedback quality, task type and external verification.
