# Security baseline (observe-only evaluator)

Status: Active (v4 — dual-subject targets amendment, 2026-07-13)

<!-- SPEC-116 NEW-door provenance (specs/templates/intake-refinement.md). -->

## Request (verbatim)

> Ship a baseline security evaluator that REPORTS. Today no gate result can ever
> demand security review — `requiresSecurityReview` is hardcoded `False`.
> Measurement before control: the block-vs-route decision stays open.

## Covered-check (which door?)

Lookup for an existing security-evaluation spec (`records search` / `doc-find`
over "security baseline", "secret scan gate") returned no hit: `secret_scan.py`
exists but is scoped to the workflow collect boundary, not a tree/gate evaluator.
Decision: **NEW**.

## Goal

Give the gate a deterministic, stdlib-only security evaluator that REPORTS new vs
baselined findings across three scan signals, without ever failing the gate — so
the harness can measure its security posture before anyone wires a block or route.

## Applicability

Runs beside `check_release_hygiene()` on every gate (unconditional call site), over
the harness tree itself. Observe-only: `security-baseline` is always `pass`; the
`requiresSecurityReview` flag in `quality-state.json` now reports `bool(new)` and
nothing consumes it as a block yet.

## Requirements / invariants

- **Three scan signals.** (a) tree secret-scan REUSING `harness_lib/secret_scan.py`
  (its anchored patterns, not re-implemented); (b) stdlib-`ast` sink-scan over
  `scripts/` for `eval(` / `exec(` / `subprocess(..., shell=True)` / `pickle.loads`;
  (c) config hygiene — a tracked `.env`.
- **Day-one green.** Snapshot at `.harness/state/security-baseline.json` is
  write-once (mirrors the `gate_generic` snapshot precedent): the first run records
  ALL findings and returns `new == []`; later runs report only findings ABSENT from
  the snapshot. The `security-baseline` check status is always `pass`.
- **Reports, never blocks.** `requiresSecurityReview = bool(new)` — a signal, not a
  gate. Gate exit code is unchanged on a clean tree.
- **Privacy-safe ids.** Finding ids are pattern-name/path-based, never the secret
  value or its length, so the snapshot is safe to commit and never self-triggers.

## Rationale & sources

Measurement before control (`.harness/context` token-economy + observation-pays
directives): a hardcoded `requiresSecurityReview = False` cannot even surface a
regression. Reusing `secret_scan.py`'s anchored patterns avoids a second, drifting
secret detector; `ast` (stdlib) gives structural sink detection without a
dependency. The write-once snapshot mirrors `gate_generic.check_protected_instructions`
so day one is green and only NEW drift surfaces.

## Test strategy

Module self-check (`security_baseline._demo`) plus a scenario that drives
`evaluate` on an isolated temp tree: a planted fake key, an `eval(` sink, and a
tracked `.env` baseline on the first run (new == 0), then a second planted key
surfaces as exactly one new finding (new == 1), and the `requiresSecurityReview`
flag is asserted True only when new > 0.

```gherkin
Feature: observe-only security baseline
  Scenario: [security-baseline:secret-scan]
    Given a tree with a planted fake API key
    When evaluate runs
    Then the reused secret-scan reports it as a finding

  Scenario: [security-baseline:sink-scan]
    Given an eval( sink under scripts/
    When evaluate runs
    Then the ast sink-scan reports it as a finding

  Scenario: [security-baseline:config-hygiene]
    Given a tracked .env file
    When evaluate runs
    Then config hygiene reports it as a finding

  Scenario: [security-baseline:day-one-green]
    Given a first evaluate on a fresh tree
    Then all findings are baselined and new is empty

  Scenario: [security-baseline:new-finding]
    Given a second planted key after the baseline snapshot exists
    When evaluate runs again
    Then exactly one new finding is reported

  Scenario: [security-baseline:requires-review]
    Given the new-finding count
    Then requiresSecurityReview is True only when new > 0
```

## Validation

`spec-pack` runs `feature-spec-conformance:security-baseline`. The Gherkin scenarios
above resolve to named checks in `testing/scenarios/sb_security_baseline.py`; the v2
ratchet scenarios resolve in `testing/scenarios/sr_security_ratchet.py`; the v3
routing scenarios resolve in `testing/scenarios/sdr_security_routing.py`; the v4
dual-subject scenarios resolve in `testing/scenarios/sbt_baseline_targets.py`. The
evaluator's own logic is covered by its module self-check
(`python scripts/harness_lib/security_baseline.py`), the router's by
`python scripts/harness_lib/security_routing.py`, and the wiring is exercised by
every gate (`security-baseline` + `security-regression-ratchet` results beside
release hygiene), with the route call itself guarded by the `security-diff-routing`
control-liveness probe.

## Amendments

### v2 (2026-07-12) — SEC.2 security-regression ratchet (enforcing) — *fail behavior superseded by v3: the join stays, hits now ROUTE instead of failing the gate*

The evaluator stays observe-only (`security-baseline` is always `pass`), but the
gate now joins the two signals it already computes — the baseline's `new` diff and
the risk-tier changed-files manifest — into one ENFORCING check,
`security-regression-ratchet` (`spec_test_gate.ratchet_hits`): a NEW (non-baselined)
finding in a file the current patch touched fails the gate. Baseline-only findings
and new findings in untouched files never trip it; on git failure the collector
fail-closes to `changed=[]`, so the ratchet passes (never a false red). Escape
hatch for an intentional finding: delete `.harness/state/security-baseline.json`
to re-baseline.

```gherkin
Feature: security-regression ratchet
  Scenario: [sr-1] a new finding in a changed file fails the ratchet
    Given a new security finding whose file appears in the changed-files manifest
    When the gate joins the baseline diff with the manifest
    Then security-regression-ratchet fails and names the escape hatch

  Scenario: [sr-2] a new finding in an unchanged file stays baseline-only
    Given a new security finding whose file is absent from the changed-files manifest
    When the gate joins the baseline diff with the manifest
    Then security-regression-ratchet passes
```

### v3 (2026-07-13) — security-diff-routing: ROUTE, not block (owner decision #1)

Owner decision 2026-07-13 #1 resolved the block-vs-route question left open in v1:
a confirmed hit (the v2 join, unchanged) **escalates to the `security-triage`
specialist instead of hard-failing the gate**. `security_routing.route(root, hits)`
(`scripts/harness_lib/security_routing.py`) is the NAMED entry point between the
join and the consumer — a future security-verification pipeline replaces the
consumer inside `route()` without touching the gate seam.

Mandatory companion (same decision): the **known-false-positive exemption
registry** at `.harness/state/security-exemptions.json`. Entries are
`{pattern, reason, reviewedAt}`, fnmatch'd against finding ids; a matching hit is
exempted so a reviewed FP never re-spends triage tokens/time. An entry missing any
field is INVALID — reported, never applied, and the ONLY thing that now fails the
`security-regression-ratchet` check (a silent exemption would be prose, not
control). Escalations stay single-writer and durable: `route()` appends a
`security_routing_escalation` event and immediately compacts it into
`.harness/state/escalations.json` (SPEC-109). The escalation id is a stable hash
of the routed finding set — re-runs are idempotent and a RESOLVED id is never
re-raised. The route call itself is declared in the SEC.3 control-liveness
registry (`security-diff-routing` probe): deleting it fails every gate.

```gherkin
Feature: security-diff-routing (route, not block)
  Scenario: [sdr-1] a registry-exempted hit is filtered; the rest routes durably
    Given a valid exemption entry whose pattern matches one of two hits
    When route() runs
    Then the matching hit is exempted and the other raises one durable
      security-triage escalation in the SPEC-109 ledger

  Scenario: [sdr-2] an invalid exemption entry is reported and never applied
    Given a registry entry missing reason and reviewedAt
    When route() runs on a hit its pattern would match
    Then the entry is reported invalid and the hit still routes

  Scenario: [sdr-3] routing is idempotent and a resolved id stays resolved
    Given the same hits routed twice and then resolved in the ledger
    When route() runs a third time
    Then all three runs share one escalation id and the resolved id is not re-raised

  Scenario: [sdr-4] no hits, no escalation
    Given an empty hit list
    When route() runs
    Then no escalation is raised and nothing is written
```

### v4 (2026-07-13) — security-baseline-targets: the same evaluator, per subject

`gate_generic.run_target_gate` now appends an observe-only
`target:<name>:security-baseline` row (`check_security_baseline`) running the
SAME `security_baseline.evaluate` over the governed target's tree, with two
dual-subject parameters added to the evaluator:

- **`snapshot_path`** relocates the write-once snapshot to the HARNESS side
  (`targets.state_dir(name)/security-baseline.snapshot.json`) — a harness flow
  must leave the target tree byte-clean (the isolation-audit invariant); the
  harness's own call sites are unchanged (default path preserved).
- **`sink_scope="tree"`** widens the AST sink scan to every tracked `.py`
  (targets have no `scripts/` convention); the harness subject keeps the
  original `scripts/`-only scope, so no retroactive finding appears. The scan
  stays tracked-only (`git ls-files`) by design.

The per-target `quality-state.json` gains `requiresSecurityReview =
bool(new)` — the same signal the harness quality-state carries (v1 F1 fix,
now per subject). Observe-only for targets: no ratchet, no routing (those are
harness-subject controls; a per-target changed-files manifest does not exist
at this seam). A broken scan reports itself in the row detail, never crashes
the gate.

```gherkin
Feature: dual-subject security baseline (targets)
  Scenario: [sbt-1] a target baselines day-one green with a harness-side snapshot
    Given a target tree with a planted key and an eval sink outside scripts/
    When evaluate runs with snapshot_path on the harness side and tree sink scope
    Then all findings are baselined, the snapshot lands outside the target
      and the target tree gains no file

  Scenario: [sbt-2] a tracked post-snapshot key is a new finding
    Given the snapshot exists and a new key is staged in the target
    When evaluate runs again
    Then exactly that finding is reported as new

  Scenario: [sbt-3] the target gate carries the row and the review signal
    Given a registered temp target
    When run_target_gate runs
    Then the observe-only security-baseline row reports, quality-state carries
      requiresSecurityReview and the target's git status stays byte-clean
```

v4 scenarios resolve in `testing/scenarios/sbt_baseline_targets.py`.
