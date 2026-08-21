# CQ.1 — per-patch risk-tier classifier (observe-only)

Status: Active (retrofit spec, 2026-07-12; behavior landed pre spec-per-item rule).

Door NEW (SPEC-116, retrofit of landed behavior): covered-check ran
`records search "risk tier"` — hits are only the landed batch's commit
records — and no spec under `specs/40-features/` owns patch risk
classification (`security-baseline.md` v2 consumes the changed-files manifest
but does not own the tier rule table; `doc-find` unavailable in this worktree:
no graphify-out). The landed acceptance scenario is the acceptance record;
this spec maps to its existing checks. Zero behavior change.

## Goal

Classify every patch into a risk tier (`low` / `medium` / `high`) from a pure,
deterministic rule table over (changed files, new security findings, sinks in
changed files) — an observe-only signal for routing review effort, never a
gate verdict.

## Applicability

`scripts/spec_test_gate.py` — `risk_tier(changed, new_findings, sink_hits)`
(pure) and `collect_risk_tier` (git-backed collector). Observe-only: the tier
is reported, not enforced (the enforcing consumer is the separate
`security-regression-ratchet`, see `security-baseline.md` v2).

## Requirements / invariants

1. **First match wins**, in order: `high` when there are new findings, or
   sinks in changed files, or security-sensitive paths changed (gate code,
   prompt contracts); `low` when the diff is empty or docs/markdown-only;
   `medium` for everything else.
2. **Markdown is low anywhere.** `low` covers markdown files outside `docs/`
   too (e.g. `README.md`).
3. **Fail-closed collector.** ANY git failure makes `collect_risk_tier` return
   `("medium", "unclassifiable (fail-closed)", [])` — never an exception,
   never a gate fail, never a spurious `low`.
4. **Live totality.** On a real repo the collector always yields a tier in
   `{low, medium, high}` and a list of changed files.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Pure rule table, no LLM | CQ.1 backlog item + deterministic-first directive (observation must pay for itself) |
| Fail-closed to `medium`, not `low` | an unclassifiable patch must not inherit the cheapest review lane |
| Observe-only | measurement-before-control precedent (`security-baseline.md`): report tiers before any consumer routes on them |

## Gherkin scenarios

```gherkin
Feature: per-patch risk tier (first match wins)

  Scenario: [docs-only:low] a docs-only diff is low
  Scenario: [md-outside-docs:low] markdown outside docs/ is still low
  Scenario: [empty-diff:low] an empty diff is low
  Scenario: [plain-code:medium] a plain code change is medium
  Scenario: [new-finding:high] a new security finding forces high
  Scenario: [sink-in-changed:high] a sink inside a changed file forces high
  Scenario: [gate-file:high] touching the gate itself forces high
  Scenario: [prompt-contract:high] touching a prompt contract forces high

  Scenario: [collector:fail-closed] git failure degrades to medium
    Given the git runner raises
    When collect_risk_tier runs
    Then it returns ("medium", "unclassifiable (fail-closed)", []) without raising

  Scenario: [collector:live] the live collector is total
    Given the real repository
    Then the collector yields a valid tier and a changed-files list
```

## Test strategy

- Behaviors: the eight rule-table cases above driven directly through
  `risk_tier` (pure, no repo state); collector fail-closed via a monkeypatched
  git runner; live collector run on the real repo.
- Regression risk guarded: reordering the rule table (first-match-wins) or
  softening the fail-closed default.
- Read-only scenario: imports the gate module, leaves the repo untouched.

## Validation

- `python testing/scenarios/cq_risk_tier.py` — the rule-table ids above
  resolve as the case labels of the `rule:<label>` checks; the collector ids
  are the literal check names `collector:fail-closed` and `collector:live`.
- `feature-spec-conformance:risk-tier-routing` green in the spec-pack gate.

## Amendments

### v3 — the universal floor: three non-skippable invariants, named and frozen (W29.N8), 2026-07-29

The E3 ladder (v2's execution levels, EXP-33) exists to spend LESS on
verification — which is exactly why the floor under it must be named before
anyone builds on the levels. These THREE existing mechanisms are the
universal floor; no execution level, ladder rung, router verdict, or
overseer judgment skips them, and none may be reimplemented as a second
list ("0 listas paralelas" — a parallel rule-table is how invariants drift):

1. **Router risk-flag floor** — `route_dispatcher.py` invariant 2: a
   deterministic security/risk flag forces escalation; the model may RAISE
   severity, never lower it. Even a `light` item escalates when flagged.
2. **`_RISK_HIGH_FILES` tier floor** — `spec_test_gate.py`: changes to the
   gate itself, the security baseline, the secret scanner or prompt
   contracts are tier `high` regardless of diff size. Defined ONCE; the
   teeth below red a second definition anywhere under `scripts/`.
3. **HARD footprint discipline** — `overseer-playbook.md` Roles: parallel
   lanes only with disjoint HARD footprints, one integration at a time.
   Procedure, not code — its single home is the playbook chain (SPEC-170
   lock), and the doc you are reading POINTS at it rather than restating it.

Frozen means: adding a fourth floor invariant or moving one is a versioned
amendment HERE — never an inline list in a new module. Teeth:
`cq_risk_tier.py` `floor:single-definition` (exactly one
`_RISK_HIGH_FILES =` assignment under `scripts/`) and `floor:doc-names-three`
(this section keeps naming all three anchors and each anchor file exists).

### v2 — tier -> execution-level consumer, observe-first (W29.N7), 2026-07-28

CQ.1 computed a tier nobody consumed. The gate now carries the deterministic
map `EXECUTION_LEVELS = {low: light, medium: standard, high: heavy}` +
`execution_level()` (unknown tier -> standard, the fail-closed middle) — the
pair lives in `harness_lib.gate_perf` (the gs-7 line ratchet keeps logic out
of the gate file) and is imported into `spec_test_gate` beside `risk_tier` —
deliberately reusing `track_record.suggestedBurden`'s vocabulary
so the overseer reads ONE burden language across tier and track record and
calibrates review depth from it (changed hunks are ALWAYS read; the level
scales everything else). The `risk-tier` check detail now stamps
`level=<level>`, and every gate run appends one `(at, gate, tier, level,
status, failCount)` line to `.harness/runs/tier-level.jsonl` via
`log_tier_level` (fail-open; append-only ~90B/run) — the series EXP-33 reads
to measure expand-on-failure rate per tier. Observe-first: nothing branches
on the level; no LLM estimator (both vendors rejected it in the W29 round).
Teeth: `cq_risk_tier.py` `level:map-total`, `level:unknown-fail-closed`,
`level:vocabulary-shared`, `level:log-shape`, `level:log-fail-open`.
