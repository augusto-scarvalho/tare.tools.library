# Reliability & Effect Reconciliation — technical proposal

**Status:** PROPOSED implementation research.

## Semantic roles to reconcile

LogicalEffect identity, EffectAttempt, ambiguous/unknown effect status, Reconciliation observation/result, compensation relation, owner/lease epoch, effect settlement and observer qualification.

Do not create these as primitives before proving existing contracts cannot represent the required golden queries.

## Invariants

- timeout/process failure does not imply external non-effect;
- ambiguous completion reconciles before retry;
- attempts sharing one logical effect cannot create duplicate outcome silently;
- compensation is a separately authorized effect linked to its predecessor;
- historical Permit validity does not automatically authorize late commit after relevant revocation/lease supersession;
- observer result carries identity/freshness sufficient for the claim it supports;
- EffectReceipt never becomes reward by itself.

## Fault matrix

Commit then drop reply; drop before commit; delayed commit; duplicate delivery; stale observer; inconsistent observers; cancel/commit race; stale owner; supersession; failed compensation; network partition/recovery.

## Backend qualification

Temporal/Restate/DBOS/Dapr/cloud durable mechanisms may be compared behind the same tare semantics: history/replay, activity identity, cancellation, external-effect behavior, Windows/local viability, upgrade drift and semantic exit test.

## Gate

No durable backend wins merely because its API is convenient. Qualification must prove failure semantics on the Effect Torture Lab.
