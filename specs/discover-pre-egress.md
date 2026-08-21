# SEC.1 — discover pre-egress secret gate

Status: Active (retrofit spec, 2026-07-12; behavior landed pre spec-per-item rule).

Door NEW (SPEC-116, retrofit of landed behavior): covered-check ran
`records search pre-egress` — hits are only the landed batch's commit records —
and no spec under `specs/40-features/` owns discovery egress
(`discovery-wrapper-cheap-apis.md` covers the provider chain, not the secret
gate; `doc-find` unavailable in this worktree: no graphify-out). The landed
acceptance scenario is the acceptance record; this spec maps to its existing
checks. Zero behavior change.

## Goal

`discover_paths` must block a file that matches a `secret_scan` pattern BEFORE
any provider egress — the secret value never leaves the machine, never enters
the sha256 cache, the enrichment map, or the report as a raw value.

## Applicability

`scripts/harness_lib/discovery.py` (`discover_paths`), for every discovery
subject (harness self or registered target). Applies even when NO provider is
configured: the pre-egress scan runs before the provider gate. Out of scope:
the workflow collect boundary scrub (`secret_scan` at reduce time), which is a
separate, later line of defense.

## Requirements / invariants

1. **Blocked before egress.** A file matching a `secret_scan` pattern gets
   `status == "blocked"` with no provider spawn — including when no provider
   is available at all.
2. **Pattern name only.** The blocked `reason` names the matched pattern
   (`pre-egress: <pattern-name>`), never the secret value or its length.
3. **Blocked ≠ refused.** A clean file with no provider configured is
   `refused` (provider gate), not `blocked` — the two failure modes stay
   distinguishable.
4. **No persistence of blocked files.** A blocked path appears in neither the
   sha256 discover-cache nor the docs-enrichment map.
5. **No raw value anywhere.** The secret value appears nowhere in the
   serialized report (in-memory return or `discover-report.json`).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Gate before provider spawn, not after | SEC.1 backlog item: egress is irreversible; a post-hoc scrub cannot un-send a key |
| Reuse `secret_scan` patterns | single secret vocabulary (same reuse norm as `security-baseline.md`) — no second drifting detector |
| Reason carries pattern name only | privacy-safe ids precedent (`security-baseline.md`): report must be safe to commit/share |
| Keep blocked out of cache/enrichment | a cached sha or enrichment row would silently whitelist the file on re-run |

## Gherkin scenarios

```gherkin
Feature: discover_paths pre-egress secret gate

  Scenario: [leak.md blocked pre-egress]
    Given a file whose text matches a secret_scan pattern
    When discover_paths runs with no provider configured
    Then the file's status is blocked before any provider spawn

  Scenario: [blocked reason names the pattern only]
    Given a blocked file
    Then its reason is "pre-egress: <pattern-name>" with no secret value

  Scenario: [clean.md refused (no provider), not blocked]
    Given a clean file and no provider configured
    Then its status is refused, not blocked

  Scenario: [leak.md absent from sha256 cache]
    Given a blocked file
    Then it never enters discover-cache.json

  Scenario: [leak.md absent from enrichment map]
    Given a blocked file
    Then it never enters docs-enrichment.json

  Scenario: [secret value appears nowhere in report JSON]
    Given a blocked file with a planted fake key
    Then the raw value is absent from the report and discover-report.json
```

## Test strategy

- Behaviors: planted fake key (openai-style pattern) beside a clean file in an
  isolated temp subject root; provider env vars stripped for the run so the
  no-provider path is deterministic.
- Edge case guarded: blocked-vs-refused distinction when zero providers exist.
- Scenario touches nothing under the repo (temp root only) and restores env.

## Validation

- `python testing/scenarios/sec_discover_egress.py` — checks
  `leak.md blocked pre-egress`, `blocked reason names the pattern only`,
  `clean.md refused (no provider), not blocked`,
  `leak.md absent from sha256 cache`, `leak.md absent from enrichment map`,
  `secret value appears nowhere in report JSON`.
- `feature-spec-conformance:discover-pre-egress` green in the spec-pack gate.

## Amendments

(none yet)
