# Universal Spec — Observability and Operability

## Goal

Make software understandable in operation, recoverable from failure, and safe to run without assuming a specific platform.

## Applies to

Runtime behavior, services, scripts, CLIs, jobs, queues, daemons, scheduled tasks, agents, deployments, migrations, observability, logging, metrics, tracing, error handling, backups, and rollback paths.

## Invariants

- Failures should be diagnosable without exposing sensitive data.
- Logs/status/errors should be actionable, bounded, and appropriately redacted.
- External, long-running, or asynchronous operations should consider timeouts, retries, cancellation, idempotency, and failure modes.
- Background work must have clear lifecycle, ownership, and recovery behavior.
- Avoid noisy logs, unbounded output, unbounded retries, and unbounded resource use.
- Avoid silent degradation unless it is explicitly designed and observable.
- Document operational commands when adding services, scripts, migrations, or deployment steps.
- Changes to startup/shutdown, health, rollback, or migration behavior require validation or review.

## Agent behavior

- Note operational impact in `HARNESS_RESULT` when runtime behavior changes.
- Add observability only when it improves diagnosis; do not create log spam.
- Keep sensitive data out of diagnostics.
- Request review if safe rollback/recovery is unclear.

## Validation evidence

Use available checks:

- command/runbook verification;
- health/status output check;
- tests for timeout/retry/idempotency paths;
- log redaction review;
- migration/rollback dry run when supported.

## Escalation triggers

Request `review` when changing:

- startup/shutdown behavior, daemons, jobs, queues, schedulers, service lifecycle;
- monitoring, tracing, logging, alerts, health checks;
- deployment/runtime behavior, migrations, backups, rollback paths;
- resource limits, concurrency, retries, or rate controls.

## Reference anchors

- NIST SSDF: operational vulnerability response and secure release practices.
- OWASP SAMM: implementation and operations maturity.

## Amendment v-next -- Event replay classification (article Section 8.2)

Source: article Section 8.2. Every trajectory event row carries an additive
`replayClass` field describing its replay semantics:

- `exact` -- deterministic state/bookkeeping transition, replayable from its
  inputs.
- `approximate` -- model or heuristic output was involved. This is the DEFAULT:
  any unknown event name classifies as `approximate`, never `exact`, and
  classification never fails.
- `external` -- the event crossed a process or network boundary, or ran a
  vendor/model effect; a replay re-executes that effect.

L3 is observe-first: the field is additive and no consumer changes behavior
based on it yet. The classifier `replay_class` lives in
`scripts/harness_lib/common.py` and is applied at the event-append chokepoints
(`append_event` and the async event appender), not at emit call sites.

## Amendment v-next -- Trace-completeness advisory (article Section 8.1)

Source: article Section 8.1. An R2/R3 route decision without its full evidence
chain (authorization -> effect -> validation) is an incomplete trajectory. The
`riskTier` vocabulary this reads was shipped with route decisions (fba2fe2).

`repo_health.trace_completeness` scans the last 500 rows of
`.harness/runs/events.jsonl` for route rows carrying `riskTier` in {R2, R3} and
reports any whose chain is incomplete: authorization evidence (a
decide/escalation-resolve or WITHHELD marker anywhere in the window) or
validation evidence (a gate/validate event after the route row) that is absent.
It surfaces as the WARN-only `trace-completeness` check of the `doctor`
repo-health surface.

This is observe-first and REPORT-ONLY (doctor observes, never blocks): no R2/R3
rows means healthy silence, and no blocking control is implied. Any enforcing
control is a later, evidence-gated spec.

## Amendment v-next -- Event tamper-evidence hash-chain (article Section 8.1 ir4)

Source: article Section 8.1 ir4 (R1 self-assessment App F F12). Closes the
tamper-evidence gap of the trajectory plane. Every CRITICAL trajectory event row
appended through the `append_event` chokepoint carries two ADDITIVE fields:

- `prevHash` -- the `hash` of the previous critical row, or the genesis constant
  (64 zeros) for the first;
- `hash` -- `sha256` of this row's canonical serialization (sorted keys,
  `hash` excluded, `prevHash` and `timestamp` included -- timestamp is part of
  the order evidence).

CRITICAL is a CLOSED, NAMED set of event types -- the security / approval /
authority decisions routed through this chokepoint:
`escalation_resolved`, `route_escalation`, `route_withheld_escalation`,
`security_routing_escalation`, `epoch_fence_overridden`,
`workflow_budget_overridden`. NON-critical rows stay BYTE-IDENTICAL (no chain
fields) -- the change is purely additive and carries zero regression.

`verify_event_chain(events)` (deterministic, stdlib) reconstructs the chain over
the subsequence of rows carrying a `hash` and returns
`{ok, brokenAt, reason, chainLength}`, pointing `brokenAt` at the first row whose
link (prevHash) or content (hash) fails. It detects reorder, edit, and removal of
a critical row. It is advisory (a `doctor` follow-up), never a blocking gate --
legitimate compaction/rotation of the transient log will itself break the live
chain, which is why verification runs against a corpus, not as an invariant.

**Ceiling (declared).** This is tamper-EVIDENT, not tamper-proof: with no signing
key an attacker who can rewrite the whole file can recompute the chain, and
truncating the tail leaves no witness. A signature lifts this ceiling and stays
behind a key-infra trigger. **Single chokepoint:** only `append_event` computes
the hash. The known DIRECT `.harness/runs/events.jsonl` writers that bypass it --
`security_routing.route`, `decision_inbox._resolve_escalation`,
`epoch.record_override`, and the `subagent_gate_wait` fail-open log -- emit
UN-hashed rows that the verifier transparently skips; their rows are outside the
chain by design (folding them in requires routing them through `append_event`, a
separate change).

```gherkin
Feature: Tamper-evident critical-event hash-chain

  Scenario: [thc-1a] critical events link into a valid chain
    Given critical and non-critical events appended through the chokepoint
    When the chain is verified
    Then it is intact, its length counts only critical rows, and each critical
      row links to the previous one

  Scenario: [thc-1b] the chain fields are additive
    Given a mix of critical and non-critical event rows
    When the rows are inspected
    Then non-critical rows carry no chain fields and critical rows carry both
      plus their caller payload

  Scenario: [thc-1c] tampering is detected
    Given a valid critical-event chain
    When a critical row is edited, two are reordered, or one is removed
    Then verification points at the first broken row

  Scenario: [thc-1d] parallel un-hashed writers do not break the chain
    Given a critical-typed row written without a hash by a direct writer
    When the chain is verified
    Then that row is skipped and the chain stays intact
```

Acceptance: `testing/scenarios/thc_hash_chain.py` (checks `thc-1a`..`thc-1d`).

## Amendment v-next -- Causal parent ids on events (article Section 8.1 DAG)

Source: article Section 8.1 (causal DAG, not wall-clock) + R1 App F F12. SERIAL
after the hash-chain amendment (same `append_event` chokepoint). The trajectory
order is a causal DAG: timestamps support the order but never override the
explicit parent link. Every event row MAY carry one ADDITIVE field:

- `parentEventId` -- the `eventId` of the event that CAUSED this one. Absent when
  a caller passes no parent; parents are never inferred from a timestamp.

**One identity per row (`eventId`).** A critical row already carries the
T-HASHCHAIN `hash`; that IS its eventId (no second identity is minted). A
non-critical row (no hash) gets a short deterministic sha over its canonical
serialization. `append_event(event, payload, parent=...)` returns the row's
eventId so a caller can name it as a later event's parent; `orphan_events`
recomputes ids identically, so appender and verifier never drift.

**Hash-chain interaction (landmine).** `parentEventId` is set BEFORE the critical
row's `hash` is computed, so a critical event's causal link is part of its signed
evidence. Critical rows WITHOUT a parent stay BYTE-IDENTICAL (no field added ->
same hash -> the existing chain stays valid); the field is purely additive.

`orphan_events(events)` (deterministic, stdlib) returns the `parentEventId`
values that point at no event present in the corpus -- dangling causal parents.
It only DETECTS (a `doctor` follow-up); it does NOT quarantine. Active quarantine
would change behavior and stays owner-gated.

**Wiring (demonstrative).** One spawn->worker edge is wired: `route_triage`
(the routing decision) is the parent of the `route_dispatched` row for the worker
it launches. The remaining append call sites are a DECLARED follow-up -- not swept
here.

**Ceiling (declared).** Non-critical eventIds are a 16-hex truncated sha; ample
for the transient log's row count, widen if a corpus grows enough for a birthday
collision to matter. Orphan detection is advisory, never a blocking gate.

```gherkin
Feature: Causal parent ids on trajectory events

  Scenario: [tcp-1a] a parent is recorded, absence is byte-identical
    Given an event appended with the eventId of a causing event as its parent
    When the row is inspected
    Then it carries that parentEventId, and an event appended with no parent
      carries no parentEventId field at all

  Scenario: [tcp-1b] a dangling causal parent is detected
    Given an event whose parentEventId points at no event in the corpus
    When orphan_events scans the corpus
    Then it reports that missing parent id, and reports none when the parent is present

  Scenario: [tcp-1c] a causal DAG reconstructs the order
    Given three events linked a<-b<-c by parentEventId
    When the parent links are walked
    Then the causal order a,b,c is reconstructed and no orphans are reported

  Scenario: [tcp-1d] parentEventId does not break the hash-chain
    Given a critical event appended with a parent and one without
    When the chain is verified
    Then it stays intact, the parented critical row's parentEventId is inside its
      signed hash, and the un-parented critical row is byte-identical
```

Acceptance: `testing/scenarios/tcp_causal_parent.py` (checks `tcp-1a`..`tcp-1d`).
