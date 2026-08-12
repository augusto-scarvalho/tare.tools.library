# Local Model Landscape, Fine-tunes & Evidence Grading

**Status:** RESEARCH / watchlist methodology; specific model availability/pricing requires freshness recheck.

## Why this survives

The local-model survey was not only a shopping list. It developed an evidence-grading method for base models, fine-tunes, distills, merges, ablations/abliterations and quantized artifacts under 24GB-class consumer GPUs.

## Evidence ladder

Distinguish vendor/model-card benchmark, reproducible independent benchmark, community bake-off with disclosed protocol, and our own qualified task/runtime evidence. Do not inherit a base model's score into a derivative/quantization automatically.

## Historical examples

ThinkingCap-Qwen3.6-27B was interesting because the model card reported large reasoning-token reductions with relatively small benchmark loss and multiple seeds, while a community agentic bake-off found it fast but with expensive outliers. This supports the category **reasoning-efficiency specialist**, not universal replacement.

Fable-family derivatives showed stronger self-reported benchmark gains but more variable community agentic behavior/tool-call discipline; evidence grade therefore remained lower. Qwopus/Fable-coder lines were interesting specifically for tool/coding behavior and thinking-off efficiency, requiring local quantization/tool-calling qualification.

## Permanent lesson

Model selection is an experimental routing/qualification problem. Track base lineage, derivative method, quantization, runtime/template and evidence provenance. A model can be best for one workload and poor for another; Pareto surfaces matter more than one leaderboard.
