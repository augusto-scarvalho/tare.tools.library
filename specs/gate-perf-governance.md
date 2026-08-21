# Gate performance governance (B4) — metric → suggestion → decision

Status: v1 (advisory-only). Origin: owner ask 2026-07-16 ("essas revisões sendo
sugeridas de forma automatizada / escaladas para o humano em forma de decision"),
designed by research waves `WF-20260716-162857-157371` (divergence) with the
security critique's constraints; intake `020dfc7b4e7c`.

## Goal

The gate-perf research round (docs/research/gate-perf-fail-fast-2026-07-16.md)
was started manually by the owner noticing slowness. Make that vigilance
mechanical: deterministic rules over metrics the harness already records open
INTAKE items for the human to triage. The engine never applies an optimization,
never blocks a gate, and never calls a model.

## Applicability

Every `scenarios` gate run on this repo (`subject=self`). v1 explicitly does
NOT evaluate target-repo data: target gate runs stamp their own rows via
`run_target_gate`; when the multi-repo era lands (intake E7 family) the same
engine runs per-target against that target's ledgers and writes to that
target's queue — same code, different roots, decisions never mix. Mixing self
and target rows in one evaluation is a defect.

## Requirements / invariants

Engine: `scripts/harness_lib/gate_governance.py`, invoked at the end of every
`scenarios` gate run (post-release, same flush point as the EXP-12 sidecar).
All rules read ONLY existing artifacts:

| ruleId | metric source | trigger (defaults) |
|---|---|---|
| `flake-reopen` | `.harness/runs/gate-perf.jsonl` first-attempt rc per scenario | scenario failed its FIRST attempt in >= 2 of the last 5 gate runs (the owner's ">=2/5 = reopened bug, not noise" rule — the rs_research_skill lesson) |
| `scenario-hot` | latest gate-perf run rows | scenario `subprocessS` > 45s (the m4 lesson: one hot scenario hid a systemic bug) |
| `gate-degraded` | cost-metrics gate records (`kind=gate`, scenarios) | median wall of last 3 runs > 1.25x median of the 10 before them |

Invariants:

- **Advisory surface = the intake queue.** A triggered rule adds ONE intake
  entry (source `governance`) whose ask starts with the dedup marker
  `[gov:<ruleId>:<subject-or-scenario>]` followed by a templated,
  metric-quoting sentence. No env vars, no paths beyond repo-relative, no log
  excerpts ride along (redaction by construction).
- **Anti-noise, zero new state.** Before adding, the engine scans the intake
  queue itself: same marker still `pending` -> skip (dedup); same marker
  decided less than `cooldownDays` (default 7) ago -> skip (cooldown). The
  queue is the only store.
- **Config integrity.** Thresholds come from `project.json` key
  `gateGovernance` (absent = defaults; the tracked, reviewed config file is
  the integrity boundary the security critique demanded — never a
  runtime-writable file).
- **Model policy.** The engine is zero-LLM by design. If a future layer
  summarizes or triages advisories with a model, it MUST use the cheap routing
  tier (sonnet-class — owner sizing 2026-07-16); never an overseer-class model.
- **Never:** auto-apply an optimization or config change; block or fail the
  gate (fail-open like the sidecar writer); write during the hold window
  (post-release only).

## Rationale & sources

- Owner ask + cost rule, 2026-07-16 session (gate-perf round).
- Divergence wave `WF-20260716-162857-157371`: post-gate hook over cron,
  flat threshold rules with cooldown, ledger separation at collection time,
  advisory-first rollout, never auto-apply.
- Security critique (same wave): env-data redaction in auto-opened decisions;
  the thresholds file is a trust surface; dedup keys must include
  subject+scenario so suppression can't mask a real degradation elsewhere.
- Live lessons encoded: rs_research_skill (>=2/5 reopened-bug rule),
  m4_status_html/EXP-13 (a hot scenario hid a systemic defect),
  EXP-12 sidecar (the metric substrate).

## Test strategy

`testing/scenarios/gg_gate_governance.py` pins, on synthetic data (pure
functions, no live intake writes): each rule's trigger and non-trigger, dedup
against a pending marker, cooldown against a fresh decision and expiry after
it, and the fail-open live invariant (`advise` on an empty root opens nothing,
writes nothing, never raises).

## Validation

- `python scripts/harness_lib/gate_governance.py` (self-check) and
  `python testing/scenarios/gg_gate_governance.py` green.
- SPEC-137 staged gate green with the engine wired (the gate run itself
  exercises `advise` against real ledgers).
- Rollout check: the first real advisory must arrive as a triageable intake
  item in the panel; `gateGovernance.enabled=false` in project.json silences
  the engine byte-identically.
