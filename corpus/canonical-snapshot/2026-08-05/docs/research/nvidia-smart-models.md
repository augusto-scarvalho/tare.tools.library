# NVIDIA Build smart models + batch posture (round 2026-07-13)

Owner ask: (a) should the research workflow send Gemini/NVIDIA requests in
batches to consume more of their APIs? (b) prospect the best NVIDIA Build
models as the "smart tier" alternative (GLM 5.2 tip), build the model cards
and wire them as a research-workflow alternative.

## A. Batch posture — verdict: NO batch API for us, use bounded concurrency

| Provider | Finding | Consequence for the harness |
|---|---|---|
| Gemini API | Batch Mode exists: 50% of interactive price, async ≤24h target, separate rate pool (enqueued-token limits published for paid Tiers 1–3 only; free tier absent from every batch table) | **Not usable**: our Gemini policy is free-tier-only (AGENTS.md), the 50% discount is a *paid-price* discount, and ≤24h async does not fit an interactive research round. Stay interactive within free RPM/RPD. |
| NVIDIA Build | No batch endpoint at all. Account-level ~40 RPM per model baseline (community-confirmed, not an SLA); 200 RPM by request; 1,000 free credits on signup, expandable to 5,000; credits per request scale with model size | **Throughput = client-side concurrency under RPM**, which the executor card already encodes: `nvidia-compat.runtimeLimits.maxConcurrency = 4` (a 4-critic fork wave in one burst, far below 40 RPM) with 429 backoff patterns. |

Sources: ai.google.dev/gemini-api/docs/batch-api + /rate-limits;
NVIDIA developer forums (40→200 RPM threads); NIM pricing guides (2026).

## B. Smart-model prospection — live probes, 2026-07-13

Probe: critique-shaped claim verification (str.strip() whitespace claim,
expected verdict FALSE), strict JSON output, temperature 0.2, via
`integrate.api.nvidia.com/v1/chat/completions`. n=1 per model + retries on
failures; wall includes queue time on the free tier.

| Model | Wall | JSON | Verdict | Notes |
|---|---:|:-:|:-:|---|
| **z-ai/glm-5.2** | **5.8s** | ✓ | ✓ | tightest answer (58 tok) — PRIMARY smart |
| **nvidia/nemotron-3-ultra-550b-a55b** | 8.7s | ✓ | ✓ | verbose (938 tok); security-critique fit |
| **qwen/qwen3.5-397b-a17b** | 14.5s | ✓ | ✓ | tightest tokens (51) |
| mistralai/mistral-large-3-675b-instruct-2512 | 25.7s | ✓ | ✓ | most precise citation, slowest — bench alternate |
| stepfun-ai/step-3.7-flash | 15.1s | ✓ | ✓ | cheap tier; token-verbose (1.9k) |
| deepseek-ai/deepseek-v4-flash | 123.5s | ✓ | ✓ | REJECTED: queue too slow for waves |
| deepseek-ai/deepseek-v4-pro | timeout ×2 (>180s) | — | — | REJECTED (hosted queue) |
| moonshotai/kimi-k2.6 | 404 ×2 | — | — | REJECTED: in catalog, not servable |
| qwen/qwen3.5-122b-a10b | HTTP 500 | — | — | REJECTED (endpoint error) |

Catalog size at probe time: 121 models (`GET /v1/models`).

## C. What got wired

- **Executor** `nvidia-compat` (`.harness/routing/executors.json`):
  `tools/openai_worker.py` against `integrate.api.nvidia.com/v1`, key
  env-only (`NVIDIA_API_KEY`), `{model}` routed per task profile,
  maxConcurrency 4, 429/quota patterns.
- **Model cards** (engine `nvidia-compat`, `harness.py models list`):
  glm-5.2 (default), nemotron-3-ultra-550b-a55b, qwen3.5-397b-a17b,
  mistral-large-3-675b (bench), step-3.7-flash (cheap).
- **Spawn mappings** (task-profiles.json, 9 profiles): scan/cheap/
  ui-validation → step-3.7-flash; docs/plan/implementation/debug/review →
  glm-5.2; security → nemotron-3-ultra.
- **Proof**: one real worker through the runtime contract
  (`HARNESS_WORKER_PROMPT_PATH`/`RESULT_PATH`) returned a valid
  `WORKER_RESULT`, status done, on glm-5.2.

Research usage: divergence stays gemini-2.5-flash-lite (free tier,
interactive); critique now has TWO smart providers — codex (gpt-5.6 tier)
and `--executor nvidia-compat` (glm-5.2 tier). Re-probe before heavy use:
free-tier queues move (deepseek numbers may recover; kimi may come online).
