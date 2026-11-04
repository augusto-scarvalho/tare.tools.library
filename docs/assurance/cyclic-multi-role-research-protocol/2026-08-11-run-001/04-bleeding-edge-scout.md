# Role 04 — Bleeding-edge / Contradiction Scout

**Run:** CMRP-2026-08-11-001

## Recent evidence that strengthens the proposal

### Google AI co-scientist (2025–2026)
Google reports a research system using specialized Generation, Reflection, Ranking, Evolution, Proximity and Meta-review agents managed by a supervisor, with iterative feedback and tool use. The system is notable as an industrial research workflow precedent, while its internal auto-evaluation remains only one evidence source and some claims require expert/experimental validation.

### Review-/critic-specific work (2025–2026)
Review-Instruct, IF-CRITIC, RbtAct and reviewer-question work show active research toward structured, fine-grained and actionable critique. A recurring pattern is decomposition into checklists/perspectives and validation against human/external signals.

**Implication:** a generic “Reviewer” prompt is weak. Functional review dimensions should be explicit and measurable.

## Recent evidence that challenges naive multi-role reasoning

### Controlled multi-agent debate (Wu et al., 2025)
A controlled logical-reasoning study finds intrinsic reasoning strength and group diversity dominate debate success; majority pressure can suppress independent correction.

### Biased consensus (Okawa, ICML 2026)
Interaction can amplify collective bias; agent heterogeneity reduces the emergence of biased consensus in the studied settings.

### Persona-assigned motivated reasoning (Dash et al., 2025)
Persona assignment can induce motivated reasoning and reduce evidence evaluation quality on some tasks.

**Implication:** tare.tools should avoid theatrical personas as a substitute for real diversity. Roles should be functional contracts/checklists, not identities designed to simulate human factions.

## Contradiction discovered

Early hypothesis: “role separation itself creates enough adversarial diversity to approximate subagents.”

Bleeding-edge correction: **role separation may create procedural diversity, but genuine cognitive/epistemic diversity remains unproven and can be undermined by conformity or persona effects.**

## New falsifier

If a same-model cyclic method converges rapidly to consensus while failing seeded contradictions that heterogeneous reviewers catch, it should be treated as a coverage aid rather than an assurance mechanism.
