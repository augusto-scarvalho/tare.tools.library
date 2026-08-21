# Role 01 — Research Planner

**Run:** CMRP-2026-08-11-001  
**Role:** Research Planner  
**Executor:** GPT-5.6 Sol, same-model sequential role  
**Epistemic independence:** `NOT_INDEPENDENT`  
**Authority:** `RESEARCH_ONLY`

## Mission

Design a falsifiable investigation of whether a single model, executing explicit research roles sequentially and cyclically, can produce better research artifacts than a monolithic single pass without being misrepresented as a genuinely independent multi-agent system.

## Forbidden moves

- do not claim role separation creates independent EvidenceFamilies;
- do not choose architecture before the literature/corpus passes;
- do not treat self-critique as ground truth;
- do not promote the method to TARGET or implementation authority;
- do not erase negative evidence discovered later.

## Research questions

**RQ1.** Does staged same-model role decomposition plausibly improve completeness, contradiction discovery, traceability and actionability compared with one-pass research?

**RQ2.** Which improvements can reasonably be attributed to decomposition/test-time compute, and which would require genuinely independent or heterogeneous reviewers?

**RQ3.** Under what conditions does self-critique help, fail or actively degrade correctness?

**RQ4.** Which protocol guards reduce correlated error, confirmation bias, persona effects, majority/conformity effects and circular evaluation?

**RQ5.** How should outputs from sequential same-model roles be represented in tare.tools.research so that provenance is useful without overstating independence?

**RQ6.** What experimental design could compare single-pass, same-model cyclic, same-model multi-agent, heterogeneous multi-agent and human-reviewed research workflows?

## Initial hypotheses — frozen before external review

- **H1:** explicit functional decomposition plus frozen intermediate artifacts improves research completeness and auditability on complex research tasks.
- **H2:** same-model roles remain one correlated epistemic family; role count must never be used as independence count.
- **H3:** externalized/verifiable feedback improves correction more reliably than ungrounded self-critique.
- **H4:** adversarial roles with explicit falsification duties reduce silent confirmation relative to generic “review this” prompts.
- **H5:** heterogeneous/human review should outperform same-model cycles on epistemic independence, at higher cost.
- **H6:** stopping on evidence delta / unresolved material findings is safer than stopping because the model reports satisfaction.

## Planned passes

1. Corpus Archaeologist.
2. Consolidated Literature Scout.
3. Bleeding-edge / contradiction Scout.
4. Source & Identity Curator.
5. Evidence Analyst.
6. Architecture Reconciler.
7. Experimental Designer.
8. Adversarial Reviewer.
9. Revision Delta.
10. Final Audit.

## Falsifiers

The proposed protocol should be weakened or rejected if evidence shows that role prompting merely rephrases the same errors, systematically increases false corrections, causes persona/conformity bias, or provides no measurable gain over a simpler one-pass + external-check strategy.
