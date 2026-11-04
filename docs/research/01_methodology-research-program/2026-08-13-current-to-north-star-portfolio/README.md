# CURRENT → North Star — portfolio oriented to time-to-trust

- **Status:** `RESEARCH / ACTIVE / DESIGN-SCIENCE ROADMAP DRAFT`
- **Date:** 2026-08-13
- **Scope:** prioritization and sequencing methodology for the tare.tools backlog
- **Authority:** research. The proposed operational order only becomes canonical through TaskStore/Architecture/ADR/SPEC in the main repository.

## 1. Problem

tare.tools has many valid architectural lines in parallel. The naive optimization would be to maximize the number of closed features. The hypothesis of this draft is that this is suboptimal while the validation/promotion/evidence pipeline still produces a high corrective burden.

Portfolio objective:

> **minimize time-to-trust and cost-to-trust from CURRENT to the North Star, subject to Authority, safety, evidence, portability, rollback and stable-incumbent compatibility as hard constraints.**

This turns “which feature comes next?” into “which change most reduces the cost/risk of qualifying all later changes?”.

## 2. North Star as a constraint function

```text
probabilistic interpretation
+ dynamic planning
+ durable execution
+ deterministic authority
+ capability-mediated effects
+ evidence-driven learning
+ conservative evolution
```

Prioritization cannot bring adaptation/memory/evolution forward if the mechanisms that limit authority, prove effects and qualify outcomes are still circular or ambiguous.

## 3. Critical-path portfolio

```text
P0.0 truthful incumbent promotion
   ↓
P0.1 Assurance Topology / Evidence Acquisition
   ↓
P0.2 Trusted Judge / promotion provenance
   ↓
P0.3 Capability/Effect + reliability closure
   ↓
P1.0 Durable Work + Evidence backbone
   ├──────────────┐
   ↓              ↓
P1.1 Relay       P1.2 Routing/ExecutionBinding shadow
   └──────┬───────┘
          ↓
P2 Adaptive Assurance/Resources + Reputation/Qualification
          ↓
P3 Memory / Experience / Evolution Control
```

The order is dependency-oriented, not a product value judgment.

### P0.0 — truthful promotion

Finish active CI corrective, promote accepted baseline through protected PR only after exact-head evidence, then re-evaluate Q7/Q8 on the repaired baseline. While promotion evidence remains ambiguous, new broad feature trains increase rebase/audit debt.

### P0.1 — Assurance Topology

Turn the mega-treasury into evidence-qualified planning, first in shadow. This stage reduces a cost that falls on every future train. See the dossier `research/08_validation-assurance/2026-08-13-assurance-topology/`.

### P0.2 — Trusted Judge

Separate ordinary green CI from strict proof. Close trusted invocation / candidate-evaluator-promoter provenance / incumbent-N-judges-N+1 without pretending that filesystem confinement or Genesis are proven.

### P0.3 — Effects / reliability

Prioritize reconciliation-before-retry, idempotency, process/session ownership, WorkspaceLease/Permit/EffectReceipt and sandbox/confinement by risk. This makes runtime fallback and future autonomy economically safe.

### P1.0 — Durable Work + Evidence

Build on TaskStore + RunEnvelope + Q8. Do not create a parallel WorkRegistry/ExecutionAttempt without an ADR. The goal is to reconstruct task → decision → execution → effect → validation/evidence.

### P1.1 — Relay

Automate wake-up/corrective loops only after validation/effect semantics are stable. Git/GitHub/Drive are transport/projections; comments/models do not mint Authority.

### P1.2 — Routing

Promote Q7 shadow semantics and converge RouteIntent/Decision→binding without premature activation. Routing/reputation do not grant Authority.

### P2/P3

Adaptive scheduling, reputation/qualification, memory and evolution only gain safe value when the evidence backbone that feeds learning is reliable.

## 4. WIP policy

- at most **one critical implementation/promotion train** consuming the staging critical path;
- one research/documentation stream may run in parallel if it does not mutate the subject;
- same-scope bounded correctives stay in the train instead of creating an issue/branch for every small finding;
- experiments may continue in isolation, but must not claim CURRENT before the prerequisites.

This policy aims to reduce queueing, rebase debt, owner interruptions and audit context switching.

## 5. Definition of Ready for structural work

A train only enters the critical path when it has:

1. exact subject/base/ref;
2. CURRENT owner/seam archaeology;
3. bounded-context owner;
4. CURRENT × TARGET × PROPOSED × RESEARCH;
5. contracts and no-duplicate-primitive check;
6. evidence obligations/falsifiers;
7. Authority/effect ceiling;
8. compatibility + rollback;
9. explicit dependency in this portfolio;
10. small Implementation Packet boundary.

## 6. Definition of Done

Local green is not enough. Structural Done requires exact remote reconstruction, independent audit, risk-appropriate CI/cross-platform evidence, preserved negative evidence, no unauthorized effect, migration/rollback evidence and an update by the canonical single writers.

## 7. Prioritization falsifiers

Reorder if evidence shows that:

- Assurance P0 does not reduce time-to-trust/corrective burden;
- shadow selection misses failures of the CURRENT treasury;
- trusted-judge source archaeology requires a different prerequisite;
- Work/Run already has a sufficient equivalent incumbent;
- Relay automation increases ambiguous effects;
- adaptive scheduling reduces compute but worsens critical-path trust latency;
- another dependency empirically dominates the portfolio.

## 8. Relationship to the canonical backlog

In the main repository, Issue #18 was created as `PROPOSED / BACKLOG INTAKE / PORTFOLIO REPRIORITIZATION` and Issue #19 as a specific Assurance Topology candidate. This **does not replace `.harness/state/tasks.json`**.

After the active CI train, a `BACKLOG-ALIGN-01` should use the incumbent `harness.py tasks ...` to ADOPT/ADAPT existing tasks, create only genuine gaps and record dependency/priority via the single writer. Raw JSON editing is an anti-pattern.

## 9. Research-to-architecture path

```text
operational evidence
 -> Research draft
 -> Findings (ADOPT/ADAPT/RETIRE/OPEN)
 -> ADR
 -> canonical architecture / SPEC
 -> BDD
 -> Implementation Packet
 -> code/gates
 -> new evidence
```

This roadmap cannot skip this chain just because it is “newer” than already ratified architecture.

## 10. Claim ceiling

The current contribution is a **design-science roadmap informed by internal operational incidents**. There is not yet an experiment demonstrating that this global order is optimal. The most defensible thesis is local: when an assurance/promotion capability reduces the qualification cost of many descendants, it deserves priority because of its multiplicative effect, as long as it does not turn into a big-bang/platform rewrite.
