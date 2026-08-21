# Control-plane liveness (SEC.3)

Status: Active (v2 — seventh probe: security-diff-routing, 2026-07-13)

<!-- SPEC-116 NEW-door provenance (specs/templates/intake-refinement.md). -->

## Request (verbatim)

> A control-plane liveness healthcheck. A silently-dead control (a scrub call
> deleted in a refactor, env-filter flipped off, a protection snapshot gone) is
> the top operational vuln — today nothing notices. A deterministic registry of
> (control, probe) pairs makes "declared" mean checkable.

## Covered-check (which door?)

Lookup for an existing control-liveness / healthcheck spec (`records search` /
`doc-find` over "control liveness", "dead control", "healthcheck") returned no
hit: `security_baseline` measures findings and `protected-files` guards
instruction files, but nothing probes whether the declared controls themselves
are still wired. Decision: **NEW**.

## Goal

Give the gate a deterministic liveness probe over every declared security
control, so a control silently deleted or disabled by a refactor fails the gate
instead of dying unnoticed.

## Applicability

Runs on every gate, appended beside the security-baseline/ratchet block in
`scripts/spec_test_gate.py`. The registry covers the harness tree itself;
`evaluate` is pure reads (no writes, no subprocesses).

## Requirements / invariants

1. **Explicit registry.** `control_liveness.PROBES` is a literal list of exactly
   six `(control, kind, path, symbol)` tuples — the "what is a declared control"
   judgment is data, not heuristics.
2. **Three probe kinds.** `source` — the named symbol appears in the named
   file's text; `file` — the file exists AND `json.loads` parses it; `config` —
   the dotted `.harness/project.json` value is NOT `False` (the escape hatch;
   an absent key stays alive).
3. **The six declared controls.** `collect-secret-scrub`
   (`secret_scan.scan` in `scripts/harness_lib/workflow_reduce.py`),
   `discover-pre-egress` (`_pre_egress_reason` in
   `scripts/harness_lib/discovery.py`), `target-gate-env-filter`
   (`filter_spawn_env` in `scripts/harness_lib/gate_generic.py`),
   `security-baseline-wired` (`security_baseline.evaluate` in
   `scripts/spec_test_gate.py`), `protected-files-snapshot`
   (`.harness/protected-files.snapshot.json` parses), `worker-env-filter`
   (`workflows.workerEnvFilter` is not `false`).
4. **Enforcing, one result.** The gate appends exactly one `control-liveness`
   result; it FAILS when any probe is dead, the detail names the dead controls,
   and the fix line reads "restore the control, or update PROBES in
   control_liveness.py in the same commit as the refactor". All pre-existing
   gate results and their ordering are untouched.
5. **Green on main.** Every probe passes on the current tree; a probe that would
   be dead on main is a wrong probe, not a dead control.

## Rationale & sources

A dead control is worse than a missing one — it still appears in docs and
threat models while protecting nothing. The registry mirrors the gate's
existing explicit-data precedents (`REMEDIATION`, `security_baseline`'s scan
list) and the write-once snapshot lesson from
`gate_generic.check_protected_instructions`: declared state must be checkable
state. Pure reads keep the probe free (token-economy directive: observation
must pay for itself); the six entries were source-verified at their file:symbol
seams before landing.

## Test strategy

Module self-check (`python scripts/harness_lib/control_liveness.py`) asserts
all six probes alive on this repo. The acceptance scenario drives `evaluate` on
ROOT (all ok) and on two fabricated temp roots (a missing snapshot; a
`workerEnvFilter:false` project.json), each killing exactly the targeted probe.

```gherkin
Feature: control-plane liveness registry
  Scenario: [cl-1] all registry probes pass on this repo
    Given the six-entry PROBES registry
    When evaluate runs on the repository root
    Then every probe reports ok

  Scenario: [cl-2] a missing protection snapshot is a dead control
    Given a temp root without .harness/protected-files.snapshot.json
    When evaluate runs on that root
    Then the protected-files-snapshot probe reports dead

  Scenario: [cl-3] the worker env-filter escape hatch is a dead control
    Given a temp project.json with workflows.workerEnvFilter set to false
    When evaluate runs on that root
    Then the worker-env-filter probe reports dead
```

## Validation

`spec-pack` runs `feature-spec-conformance:control-liveness`. The Gherkin
scenarios above resolve to named checks in
`testing/scenarios/cl_control_liveness.py`. The registry's own logic is covered
by its module self-check (`python scripts/harness_lib/control_liveness.py`),
and the enforcing wiring runs on every gate (`control-liveness` result beside
the security-regression ratchet).

## Amendments

### v2 (2026-07-13) — seventh probe: `security-diff-routing`

The security-baseline v3 amendment replaced the ratchet's hard-fail with a route
to `security-triage` (owner decision 2026-07-13 #1). A silently-dead routing
call would be strictly worse than the block it superseded, so the route call is
now a declared control: probe `security-diff-routing` (`source`,
`security_routing.route` in `scripts/spec_test_gate.py`). Invariants 1/3 read
"six" as of v1; the registry now holds exactly SEVEN entries — the counting
assertions in the module self-check and `cl-1` moved with it in the same commit,
per invariant 5's rule that a refactor updates PROBES and its counts together.
