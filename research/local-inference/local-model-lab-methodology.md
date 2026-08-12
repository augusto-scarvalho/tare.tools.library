# Local Inference & Consumer-GPU Model Lab Methodology

[← Legacy System Reconstruction](../experience/legacy-system-reconstruction.md) · [Navigation](../../NAVIGATION.md) · [All Research](../README.md)

**Status:** EXPERIMENTAL RESEARCH / infrastructure methodology.

**Empirical companions:** [HumanEval scoring-harness failure](../../case-studies/local-inference/humaneval-scoring-harness-failure.md) · [Recurrent Memory research line](../../experiments/local-ai-lab/recurrent-memory/README.md)

## Scope

Local models are first-class tare.tools candidates, not merely offline fallbacks. Their identity and qualification include quantization, runtime, kernels, context/cache configuration, hardware headroom and tool/agent behavior — not just a base model name.

## Historical lab findings preserved

On consumer GPUs, VRAM headroom, CPU-MoE placement, mmap/nommap, KV cache format, context length and engine build can change throughput/stability materially. A configuration that maximizes benchmark throughput may be operationally unacceptable if it leaves insufficient VRAM for workstation/browser/IDE/Docker coexistence.

The local lab also produced an important test-method negative: a HumanEval scoring-harness bug once inverted the apparent quality conclusion for ThinkingCap. After fixing sample construction/cache behavior, a previously reported 0/60 result became ~93.3%. This is evidence that **benchmark harness correctness is part of model qualification**.

## Qualification dimensions

- exact model/revision/quantization;
- engine commit/build flags/kernel path;
- prompt/tool template and context limits;
- generation/prefill throughput and latency distributions;
- RAM/VRAM/headroom and failure behavior;
- long-context/cache correctness;
- code/tool-calling/agentic task quality;
- repeated runs and uncertainty;
- workstation coexistence;
- Windows/WSL/native boundary;
- evidence grade of upstream/community benchmarks.

## Research discipline

Official/model-card, independent benchmark and local repeated evaluation are separate EvidenceFamilies only when methods/data are sufficiently independent. Fine-tune self-reports remain hypotheses until local/independent qualification.

## Cross-links

Routing uses these qualification snapshots; Resource scheduling uses hardware constraints; Runtime ownership determines the agent loop; Local recurrent-memory experiments live under `experiments/local-ai-lab/` because their questions are architectural to model memory rather than fleet benchmarking.

---

## Continue this trail

**Previous:** [Legacy System Reconstruction](../experience/legacy-system-reconstruction.md)  
**Next:** [Local Model Landscape / Fine-tunes →](model-landscape-finetunes.md)  
**Experiment line:** [Recurrent Memory](../../experiments/local-ai-lab/recurrent-memory/README.md)  
**Routing application:** [Adaptive Routing / Reputation](../routing/adaptive-routing-reputation.md)
