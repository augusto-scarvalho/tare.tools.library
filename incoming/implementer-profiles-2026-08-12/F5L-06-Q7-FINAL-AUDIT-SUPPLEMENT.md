# F5L-06 / RELAY-Q7 — Final Audit Supplement

**Status:** EXPERIMENTAL / RESEARCH  
**Date:** 2026-08-12  
**Canonical change:** false

This supplement closes the freeze-point gap in the initial implementer-profile draft. It supersedes only the draft statements that `RELAY-Q7-CORRECTIVE-001` was still running; it does not rewrite the historical first RESULT or first independent audit.

## Final DEV subject

- ref: `refs/heads/dev/relay-q7-frontdoor-shadow-binding`
- frozen base: `185179b0a5691f3bd606f9226e15423d1e1ab2b5`
- first Q7 candidate: `65ca9eb7a8bd569f1260ac433194a89dd791a337`
- final corrective candidate: `b0dea202e29e418fc0de04db826c5917cd851ed9`
- final tree: `710fd333c49b8b0cb61326484e10c3cfc43b895d`
- final candidate direct parent: `65ca9eb7a8bd569f1260ac433194a89dd791a337`
- `main = staging = 477bea0d915dfde5e9e92fce68be0a42154a31f9` remained unchanged.

## Independent final verdict

`ACCEPTED_AS_A2_DEV_SHADOW_CANDIDATE`

- activation eligible: **false**
- A2 packet-decomposition capability: **STRONG_POSITIVE_SIGNAL**
- A2 semantic/conformance result for this train: **ACCEPTED**
- A2 global/default qualification: **NOT_YET**
- second real A2 probe: **AUTHORIZED**, with **no Authority expansion**

Issue #11 was closed as completed after the final independent audit.

## Corrective findings closed

1. **Cloud evidence completion:** closed.
2. **Deterministic taskProfile ownership:** closed. Semantic triage cannot steer room specialization by supplying a taskProfile; mismatch survives only as non-authoritative `triageTaskProfileIgnored` evidence.
3. **WORKFLOW_INTENT false concreteness:** closed. Unvalidated workflow intent remains `resolved:false` until the CURRENT workflow compiler validates a profile.
4. **Model/executor declaration concreteness:** closed. The shadow projection reuses the incumbent model-routing validation owner and rejects placeholder/non-runnable executor lanes.
5. **trustTier / Commercial Lane conflation:** closed. `trustTier` remains fan-out trust classification; Commercial Lane is not synthesized.

The projection remains an effect-free compatibility/shadow record and is **not** canonical `ExecutionBinding`.

## Independent Drive verification

The auditor independently inspected the Google Drive relay tree and verified two packages under `relay-q7/dispatch/`.

### Original package

Manifest SHA-256:

`6eb78e3bb55bbdc74d962b97b2654352f364793efb1b9ec603348608d24b7cce`

All **8/8** payloads were independently downloaded and matched the manifest byte sizes and SHA-256 entries.

### Corrective package

Manifest SHA-256:

`d1004b5d403b9e8e2e0a8e427dc801fb883436a9cf7c5a9a9513fe9f77f79eb6`

All **7/7** payloads were independently downloaded and matched the manifest byte sizes and SHA-256 entries.

The historical RESULT-001 evidence-publication miss remains preserved in the Issue/audit lineage rather than being rewritten away.

## A2 interpretation

The corrected Q7 episode is stronger qualification evidence than a clean first pass would have been. Fable designed CP1–CP6 itself, independent audit falsified semantic/completion claims, and Fable then self-decomposed CC1–CC6 and closed the findings in one bounded corrective commit without redesigning the architecture.

This supports the narrower conclusion:

> Fable 5 low shows strong bounded packet-decomposition capability under independent audit, but one corrected A2 episode is not sufficient for a global/default A2 qualification.

## Preserved non-blocking debt

- `shadow_selection` currently reuses private `model_routing._validate_entry`; consider a public read-only validation seam before canonicalization/activation.
- `rt6_route_writechain` remains a disclosed pre-existing environmental negative.
- Work Registry × Relay × Kanban Projection remains a separate ADR/reconciliation after Q7.
- No live model/runtime activation occurred in Q7 (`modelDecisionCount=0`, `runtimeInvocationCount=0`).

## Publication note

The PT/EN review HTMLs in this draft branch were initially rendered before corrective closure. This supplement is the authoritative incremental draft update for Q7 until those derived renders are regenerated during publication validation. Publication in `tare.tools.research` remains EXPERIMENTAL evidence and does not mint CURRENT or TARGET.