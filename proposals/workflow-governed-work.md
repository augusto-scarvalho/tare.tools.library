# Workflow as Durable Governed Work — technical proposal

**Status:** PROPOSED; reconcile before code.

## Problem-specific roles

`WorkflowTemplate`, `WorkflowRevision/CompiledWorkflow`, `WorkflowTrace`, heterogeneous node role, subworkflow contract, durable wait, GraphPatch/replan request, terminality/finality and invalidation are **semantic roles** until canonical equivalence is checked.

## Required invariants

1. Work identity survives runtime/session replacement.
2. A materially changed plan gets revision identity.
3. GraphPatch/replan cannot bypass Authority/Routing.
4. Retry/reroute/resume/replan/reconcile are distinct transitions.
5. Deterministic nodes are first-class and do not require an agent wrapper.
6. Durable waits and human approval survive process restart.
7. Effect-producing nodes obey Effect/Reconciliation semantics.
8. Trace never retroactively changes the compiled revision that was attempted.

## Compiler pipeline candidate

Project/Demand facts → logical work requirements → dependency/applicability analysis → Authority/capability constraints → candidate realizations → cost/assurance plan → revisioned physical workflow → execution trace.

## Qualification/BDD

Heterogeneous workflow; revisioned replan; subworkflow cancellation/join; durable restart; stale plan rejection; deterministic↔agentic substitution parity; terminal task with unsettled demand; process-mined deviation requiring explicit disposition.

## Migration

Adapt incumbent workflow APIs behind roles first; preserve behavior; add read-only revision/event evidence; shadow compiler alternatives; qualify one vertical slice; keep rollback to incumbent.
