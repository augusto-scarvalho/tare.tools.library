# Economics, Resources & Observability for Routing

**Status:** RESEARCH companion to adaptive routing.

## Cost-to-trust

Token price alone is a poor optimization target. More useful is total cost until a defensible outcome: inference + retries + validation + human interruption + latency + scarce local/cloud resources.

## Commercial/resource identity

Provider/model identity must not be collapsed with quota pool/commercial lane. A vendor subscription, API key pool, local GPU or remote runtime may impose independent limits and failure modes.

## Hot / warm / cold paths

- hot path: compact read-only snapshots for decisions;
- warm path: update qualification/reputation/resource state;
- cold path: causal analysis, delayed outcomes and controlled experiments.

This reduces coupling and supports replay.

## Observability

Telemetry should explain resource/runtime behavior but remain a projection. Scheduling should use stable snapshots/receipts where decisions need replay/auditability.

## Research program

Compare tokens/s and benchmark scores with cost-to-trust; measure human attention; simulate quota exhaustion/fallback; investigate local GPU scheduling and resource contention; test whether dynamic scheduling actually improves trust latency versus simple queues.
