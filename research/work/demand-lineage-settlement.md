# Demand Lineage, Context Reconstruction & Settlement

**Status:** RESEARCH / OPEN primitive question.

## Why this is distinct from Workflow

Workflow explains progression once work exists. Demand lineage asks whether the system can reconstruct **why** the work exists and whether the original need was actually satisfied.

## Chain

```text
Raw Intake
 → Grounded Demand
 → Requirements / Constraints
 → Disposition / Admission
 → Durable Work
 → Context Materialization
 → Execution / Effects
 → Evidence
 → Outcome
 → Settlement
 → Learning
```

Issue text, prompt text and final patch are incomplete views. Requirements may be clarified progressively and outcomes may reveal that terminal tasks only partially satisfied the obligation.

## Golden questions

- What user/project need caused Work W?
- Which requirements were known when revision R was compiled?
- Which constraints were added/removed and by whom?
- Did the effect satisfy the original demand or only finish a task?
- Can later incidents reopen settlement without rewriting historical task completion?

## Discipline

Do **not** create `Demand` as a primitive merely because the research uses the noun. First test whether existing Project/Task/Workflow/Outcome relations answer the golden questions without ambiguity. Only a demonstrated gap justifies ADR/SPEC work.

## Cross-links

Feeds context compilation, outcome evaluation, product/user research and learning eligibility. Closely coupled to Information Survival because losing demand/requirement history makes later evaluation impossible.
