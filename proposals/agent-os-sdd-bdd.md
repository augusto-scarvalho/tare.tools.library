# Agent OS Architecture — preserved SDD/BDD proposal

**Status:** PROPOSED TARGET / historical implementation research.

## Purpose

Preserve the specific contract vocabulary and migration decomposition that emerged from the Agent OS North-Star work without pretending the proposal is canonical.

## Candidate canonical vocabulary

TaskEnvelope; RouteContract; RouteIntent; Candidate/CandidateKey; RouteDecision; ExecutionBinding; RuntimeContext/RuntimeState; Authority; Permit; WorkspaceLease; Capability; ActionRequest; EffectReceipt; HarnessEvent; OutcomeEvidence; EvidenceFamily; Attribution; ReputationSnapshot.

Model, Provider, Provider Route, Runtime, Runtime Owner and Commercial Lane remain distinct.

## Runtime interfaces

- RuntimeAdapter SPI for vendor-local/vendor-remote integration.
- HarnessAgentRuntime for tare-owned agency.
- ModelProviderAdapter for inference endpoints/local models.
- Capability boundary for tools/effects.

## Migration logic retained

Introduce causal IDs/events/receipts and canonical routing contracts before replacing incumbents; then WorkspaceLease/Capability; HarnessAgentRuntime; runtime state/fallback; reputation shadow; Qualification Lab; low-risk adaptive routing; attribution; governed memory; evolution shadow/canary; contextual bandits/OPE.

The sequence is an implementation-research roadmap, not evidence that these waves are already implemented.

## BDD themes worth retaining

Decision persisted before spawn; policy/authority cannot be bypassed by routing; capability execution requires authorized request; effect receipt has causal identity; runtime owners produce externally conformant evidence; replay/reducers are idempotent; reputation path is read-only in hot routing; candidate cannot self-promote evolution.
