# Executable / Cognitive System Reconstruction

[← TUI / REPL Experience](tui-repl-experience.md) · [Navigation](../../NAVIGATION.md) · [All Research](../README.md)

**Status:** RESEARCH; derived from NLU/state-machine modernization work.

**Related HTML checkpoint:** [Experience / UX scientific refresh](../../bridge-editions/2026-08-11/experience-ux-scientific-refresh.html)

## Thesis

A legacy conversational/cognitive system's valuable asset is often the **semantic, procedural and transactional knowledge** accumulated around NLU, not the classifier alone. Modernization should extract that knowledge rather than “LLMify everything”.

## Reconstruction pipeline

```text
intents/entities/variables/pages/handlers/APIs/knowledge/logs
 → semantic reconstruction
 → domain/service ontology + declared control graph
 → data/capability/knowledge/response-policy maps
 → observed journey graph
 → Project Model
 → procedure/subworkflow candidates
 → governed Workflow/Capability execution
```

## Hybrid execution

Language understanding may use rules/NLU/small models/frontier models according to ambiguity/value. Known business logic and irreversible transactions remain deterministic where possible. Generative response is bought only where it adds marginal value.

## Evidence sources

Configured state machine and production traces are both needed: declared design may drift from real journeys. Process mining/automata learning can reconstruct observed procedures; trajectory compilation can identify repeatable deterministic fragments.

## Safety

Irreversible effects, prompt injection, stale conversational state and business constraints need explicit controls rather than relying on generative compliance.

## Generalization

The method extends beyond chatbots to BPM, RPA, IVR, case-management and low-code/state-machine systems.

---

## Continue this trail

**Previous:** [TUI / REPL Experience](tui-repl-experience.md)  
**Next:** [Local Inference / Model Lab Methodology →](../local-inference/local-model-lab-methodology.md)  
**Project integration:** [Project Admission](../project/project-admission-adoption.md)  
**Workflow integration:** [Workflow as Governed Work](../work/workflow-governed-work.md)
