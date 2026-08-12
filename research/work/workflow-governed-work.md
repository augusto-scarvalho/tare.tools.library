# Workflow as Governed Work — preservation edition

**Status:** RESEARCH; TARGET implications require canonical reconciliation.

## Why this remains a full study

Workflow science answered a deeper question than “how to arrange agents”: how heterogeneous work progresses durably while plans, facts and executors change.

## Core thesis

**Workflow represents progression of governed work, not an agent topology.** Nodes may be deterministic code, agents, capabilities, humans, waits, approvals or subworkflows.

## Distinctions that must survive

- reusable template/procedure;
- compiled/revisioned instance for a concrete work item;
- execution trace of what actually happened;
- logical versus physical realization;
- desired versus observed progress;
- terminal task state versus demand/obligation settlement.

Graph mutation without revision identity is unsafe. Replanning/GraphPatch must pass normal Authority/Routing boundaries rather than directly changing execution truth.

## Scientific ancestry

The lineage draws on Statecharts, Petri/WF-nets, GSM/CMMN/case management, structured concurrency, Sagas, durable execution, query optimizers/PGO, process mining and recent trajectory→workflow compilation research. These form different semantic projections, not competing kernel ontologies.

## Procedural learning

Repeated successful trajectories may become procedure candidates. Hard dependencies should be compiled only when data/control dependencies are evidenced; uncertain/irreversible steps may need to remain agentic or refuse compilation. Mature learning can therefore produce **less agency**.

## Research program

Compare template/instance/trace conformance; test replanning under revision pinning; deterministic+agentic heterogeneous workflows; subworkflow cancellation/joins; durable waits; terminality/reopen; compiler alternatives and cost-to-trust; process mining versus declared process.

## OPEN

WorkflowInstance/Revision canonical roles; finality; dynamic graph constraints; backend qualification; procedural applicability and invalidation.
