# Race-mode test #1 (item #4, 2026-07-19)

Owner: "you can run something to test it" (race-mode / D016). First real run
using the E-3LANE instrument (frozen tasks + stdlib oracle) — 3 NVIDIA models
competing on the same tasks, with cost/time/correctness measured.

## Setup
- Tasks: `parse-json-total` (extract an int from JSON) + `compile-add-function`
  (write `def add(a,b)`), from E-3LANE. Deterministic stdlib oracle.
- Models (NVIDIA Build, free tier): glm-5.2, llama-3.3-70b, deepseek-coder-6.7b.
- temperature=0, max_tokens=400. Free tier (negligible cost).

## Result (2nd round, after oracle fix)
| model | correct | tokens | total time | note |
|---|---|---|---|---|
| **z-ai/glm-5.2** | **2/2** | 91 | **6.5s** | winner — fast and correct |
| meta/llama-3.3-70b | 1/2 | 80 | **53.7s** | extremely slow on the endpoint; 1 timeout |
| deepseek-ai/deepseek-coder-6.7b | 0/2 | 0 | — | HTTP 404 (id not serviceable by this endpoint) |

**Verdict:** for deterministic micro-tasks, glm-5.2 dominates (our primary
smart-tier choice was already correct). Race-mode works: same task, N brains,
a neutral oracle decides, and cost/time are comparable side by side.

## The finding that was worth more than the result
The 1st round marked glm as a "fail" on compile — but its answer was CORRECT
(`def add(a,b): return a+b`), merely wrapped in ` ```python `. **The E-3LANE
oracle did not strip the markdown fence before compiling.** The run exposed a
weakness in the instrument that I built. Fixed: `_strip_code_fence` in the
`oracle` (`testing/probes/three_lane_probe.py`); self-check green; rerun → glm
2/2. This is exactly what real testing does — the model was right, the judge
was wrong.

## Honest limits of this run
- A 402/error for an unavailable model (deepseek 404, llama timeout) becomes
  "lost" — the runner distinguishes ERR from fail, but a serious race needs a
  retry/timeout budget per model (do not penalize the model for free-tier
  endpoint latency).
- 2 tasks × 3 models is anecdotal — a production race-mode needs N tasks per
  class + repetition (the L13 noise floor applies: a difference smaller than
  jitter is not signal).
- The runner remained in the scratchpad (measure-only, throwaway). Promoting it
  to a real verb/probe is the race-mode item (D016) when desired — the E-3LANE
  instrument + this runner are the base.

## Next (real race-mode, if desired)
A real `--live` mode in E-3LANE (currently refused) that runs N tasks × M models
with retry/timeout per model, applies the noise floor, and emits a winner table
per task class. This is the owner-gated measurement for EXP-20. This test proved
the machinery and already paid for one oracle bug.
