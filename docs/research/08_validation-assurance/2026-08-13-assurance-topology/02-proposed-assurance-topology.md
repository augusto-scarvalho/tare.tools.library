# 2 — Proposed architecture and migration

**Status:** `PROPOSED / RESEARCH`

**Parent:** [Assurance Topology](README.md)

## Principle

Preserve the Scenario Regression Treasury as the historical executable specification of the stable incumbent, but stop assuming that every evidence producer needs to block every PR.

The conceptual unit changes from "test" to:

```text
Change / Subject
  -> claims that matter
  -> required assurance
  -> mandatory Evidence Families
  -> evidence producers
  -> sufficiency
  -> authorized decision
```

The smallest proof layer capable of supporting the claim should win, except when policy requires independent/additional families:

`static → unit → contract → scenario → system → adversarial → agentic eval → operational evidence`.

## Evidence producer descriptor

Research shape; **not a canonical primitive** before reconciliation/ADR:

```yaml
id: stable-id
owner_context: ...
claims: [...]
evidence_family: ...
proof_layer: static|unit|contract|scenario|system|adversarial|agentic_eval|operational
subject_scope: ...
change_surfaces: [...]
platform_requirements: [...]
hermeticity: hermetic|host_bound|external
determinism: deterministic|bounded_timing|stochastic
cost_class: cheap|medium|expensive
historical_duration_ms: ...
blocking_policy:
  pr_fast: ...
  pr_impacted: ...
  promotion: ...
  qualification: ...
  reliability_scheduled: ...
  release: ...
provenance: ...
```

Unknown/unclassified metadata remains visible debt. Absence of metadata never buys `skip`.

## GatePlan in shadow

```text
Candidate identity
+ changed surfaces (Graph/AST/contracts + source verification)
+ risk/policy floor
+ mandatory Evidence Families
+ platform/runtime capability
+ duration/failure/flakiness history
        ↓
reconstructable GatePlan
```

The GatePlan is a projection of obligation/execution, **not Authority**. Model/router may in the future order additional evidence, but not lower the deterministic policy floor.

## Candidate lanes

- **PR_FAST** — compile/static/spec/product hygiene and cheap deterministic contracts.
- **PR_IMPACTED** — affected scenarios and the platform subset required by impact/risk.
- **PROMOTION_DETERMINISTIC** — broad deterministic treasury, parity and boundary invariants.
- **QUALIFICATION** — `NOT_CURRENT`, candidate experiments, runtime/model/sandbox qualification.
- **RELIABILITY_SCHEDULED** — fault/process/network/timing evidence and long-running soak when not suited to the fast path.
- **RELEASE** — ship/readiness, supply chain and release-specific closure.

"Scheduled" does not mean ignored: policy may require this evidence before promotion/release.

## Multi-target without a Cartesian product

Adopt the distinction already researched:

1. **anchor targets** — always required for critical classes;
2. **impacted targets** — expanded by change impact;
3. **sampled/combinatorial targets** — pairwise/risk sampling;
4. **full parity triggers** — Authority, Capability, runtime and canonical contracts.

Windows remains first-class; Linux/macOS/CI remain requirements. The proposal makes explicit when each target is claim-relevant.

## Migration — Strangler

- **S0 Inventory:** classify evidence producers, without changing execution.
- **S1 Shadow:** produce GatePlan; the CURRENT mega-suite remains the authority.
- **S2 Historical replay:** compare GatePlan vs known failures.
- **S3 Canary lanes:** lane split in parallel, with full-suite fallback.
- **S4 Selective PR:** only after ADR/SPEC + independent review + prospective thresholds.
- **S5 Adaptive scheduling:** only after telemetry/dataset; the policy floor remains deterministic.

Rollback: a deterministic switch returns to the CURRENT topology while parity/coverage are still in qualification.

## Scheduling / economics

Goal:

> **minimize time until there is sufficient evidence for an authorized decision.**

Metrics: time-to-first-actionable-failure, time-to-required-evidence, time-to-trust, assurance queue latency, duplicate/wasted evidence, runner-minutes and cost-to-trust.

After reliable instrumentation, consider historical duration/LPT-like ordering → compatible work stealing → resource/evidence-aware priority. Active evidence acquisition remains later research, not a requirement of the first GatePlan.

## ADOPT / ADAPT / RETIRE / OPEN

- **ADOPT:** historical treasury, independent audit, fail-closed unknowns, cross-platform qualification, deterministic policy floor.
- **ADAPT:** universal PR treasury → evidence-qualified lanes; OS matrix → anchor/impact/full-parity triggers.
- **RETIRE:** "every FAIL = candidate regression", blanket waiver, "every important test blocks every PR".
- **OPEN:** exact registry/schema, trusted authority for nonblocking policy, shadow exit threshold, impact-graph confidence, placement of intrinsically nondeterministic fault tests.
