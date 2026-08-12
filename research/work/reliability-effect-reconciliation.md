# Reliability Semantics & Effect Reconciliation — preservation edition

**Status:** RESEARCH / PROPOSED semantics. Derived from the 43-section, 70-source reliability study and its technical proposal.

## Central problem

Partial failure is normal. A client can time out after an external commit; observers can be stale; cancellation can race commit; retries can duplicate real-world effects. Therefore transport/process success cannot be treated as effect truth.

## Canonical reasoning chain

```text
Logical Effect Intent
   ├─ Attempt 1
   └─ Attempt N
        ↓
External world
        ↓ observations
Reconciliation
        ↓
EffectReceipt
        ↓
OutcomeEvidence
        ↓
Attribution / Qualification / Learning
```

This preserves the difference between **doing**, **knowing what happened**, and **judging whether it was good**.

## Key findings

- “Exactly once” for arbitrary external effects should not be promised as transport magic.
- Prefer one logical effect over durable identity + idempotency/dedup/CAS when available + reconciliation.
- `AMBIGUOUS/UNKNOWN` is a legitimate epistemic state; reconcile before retry.
- Compensation is a new governed effect, not perfect undo.
- Historical Permit validity and **Authority freshness at commit** are separate questions.
- WorkspaceLease/owner epoch/fencing may be required to stop stale actors committing.
- Observer/scanner APIs are measurement instruments; freshness, latency and false results matter.
- EffectReceipt is not reward and telemetry is not proof.

## Effect Torture Lab

Preserve a tare-owned fake external system with ground truth and deterministic fault injection: commit_then_drop_reply, drop_before_commit, delayed commit, duplicate delivery, stale observer, cancel/commit race, stale owner, supersession and failed compensation.

## Interdisciplinary findings preserved

STPA/unsafe control actions, High Reliability Organizations/near misses, resilience engineering, accounting settlement/reconciliation, pharmacovigilance/delayed harm, partial observability/active sensing and queueing/triage all informed the reliability model.

## OPEN

LogicalEffect identity; reconciliation authority; effect groups/multi-effect transactions; stale Permit semantics; durable backend qualification; observer metrology; settlement/materiality.
