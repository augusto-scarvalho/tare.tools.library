# Research Pointers — Recurrent Memory / RNN — 2026-08-12

**Authority:** `RESEARCH_ONLY_NO_IMPLEMENTATION_AUTHORITY`

These are continuity pointers, not tare.tools product backlog.

## OPEN / investigate after RNN-06T2

1. **Realistic high-interference long-context operating point**  
   Find a non-trivial workload in which a real recurrent LM exhibits final-state forgetting while earlier states retain recoverable information. Do not infer it from the current 768-token single-needle scout.

2. **Adaptive temporal-state selection mechanism**  
   Test the `NOT_YET_WRITTEN ↔ SEEN_AND_RETAINED ↔ ALREADY_FORGOTTEN` interpretation with prospectively frozen selectors and controls.

3. **End-to-end capture economics**  
   Measure identical semantic work for final-only and recovery-enabled paths, including snapshot production, transfer, restore and selection.

4. **Batch-shape numerical portability**  
   Investigate why official Mamba state differs across batch shapes (`max_abs_diff=0.5` observed in RNN-06T) and determine whether it matters for serving/branch semantics.

5. **Historical-state memory vs current-state expansion**  
   Compare historical recovery with StateX-like capacity expansion only if the historical path is semantically qualified but economically unattractive.

6. **GDN/hybrid transfer**  
   Qwen3.5-0.8B remains a later qualification target after Mamba transportability is independently closed.

7. **Trained state-memory attention**  
   DART-like trained retrieval is conditional on a large historical oracle ceiling plus a persistent gap that simple target-agnostic selectors cannot close.

## PARK / do not reopen by tuning

- tested TPTT configuration;
- old synthetic dense post-hoc Memory Caching recipe;
- EXT3/B4-style repeated threshold hunting.

## DEFER

- Qwen3.6-35B-A3B deployment-family transplant;
- INT8 historical archives;
- ReplaySSM;
- serving integration.
