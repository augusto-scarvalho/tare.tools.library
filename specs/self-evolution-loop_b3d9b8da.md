# SPEC-109 — Self-Evolution Loop (Milestone SE)

Status: **Done** (executed 2026-07-09; commits 371c9ed, 746c7ce, d583c68 + closeout).
Acceptance: `testing/scenarios/se_self_review.py` (13/13). First real run found the true debts
(harness/gate burn-down, jsonschema info). Execution notes: gate cleanup used to wipe the
escalation ledger with events.jsonl — supervision events now compact into the durable
`.harness/state/escalations.json` (also implements the Deferred compaction trigger for the
supervision slice).
User decisions: autonomy = propose + closed set of safe actions; ordering = SE before M5.

## Goal

The harness analyzes and criticizes itself: metrics from its own processes (events, gate
results, guardrail actuals, discovery cache, orchestrator friction observations) are collected
on a harness-owned cadence, evaluated against declarative rules, and turned into findings that
enter the **existing supervision funnel** (escalations CLI + M4 page + a backlog inbox). The
human stops prompting periodic reviews; triage replaces prompting.

## Grounding

- The two proactive reviews of 2026-07-09 (token economy; session retro) were human-prompted;
  every signal they used already lived in repo state — nothing observed them.
- Dormant sensors planted by earlier milestones: M3.4 assumptions registry "re-evaluate
  signals"; Deferred backlog triggers ("events.jsonl >1MB"); M3.3 `attemptSelection`; budget
  overrides; guardrail burn-down targets; ideas §J rules ("ratchets must tighten",
  "friction×2 = missing tool") — prose, not checks.
- Cadence precedent: `graphify:graph-freshness` (SPEC-108 H5) — the gate repairs/refreshes
  deterministic state; SE reuses the pattern for analysis freshness.
- Anti-Hive invariant (ideas §H): the system never rewrites its own code/topology/prompts.
  Self-evolution = automatic diagnosis + proposals; execution stays human-gated.

## Scope

1. **SE.1 collector** `harness_lib/self_review.py`: local, offline metrics from events.jsonl,
   active reduce results, quality-state, guardrail config vs actual line counts, discover
   cache age, friction observations.
2. **SE.2 rules**: declarative thresholds in `.harness/self-review.json`; `evaluate()` yields
   findings `{id, severity action|info, title, observed, threshold, proposedAction, backlogRef}`.
3. **SE.3 cadence + funnel**: `harness.py self-review` command; gate check
   `self-review:freshness` runs it when stale (>7 days or >25 commits); new action findings emit
   `self_review_finding` events that `list_escalations` reads as an additional source
   (`escalationId = self-review/<ruleId>`, `suggestedProfile: plan`, `failureClass: null`);
   existing `--resolve` works; findings appear on the M4 page for free.
4. **SE.4 friction as data**: optional `frictionObservations` (≤10 strings ≤200 chars) in
   HARNESS_RESULT/WORKER_RESULT; carried into the validation event so events.jsonl is the
   durable store; recurrence ≥2 → finding (§J rule mechanized).
5. **SE.5 safe actions** (closed set, deterministic, reversible, `autoActions` flag, all
   event-logged): tighten line ratchets (never loosen), maintain the backlog
   "Self-review inbox" section between markers, maintain its own state files.

Out of scope (deliberate refusals): auto-executing backlog items; editing code/policy/prompts/
model chains; LLM-as-judge in the loop (deterministic metrics first); network in gates;
resident daemons (cadence comes from the gate).

## Landmines (verified)

- `failureClass` enum is schema/contract-pinned — findings use `failureClass: null`.
- `escalations` golden contract requires `pending`/`count` — new source must keep the shape.
- Gate check must stay offline and fast (~seconds); events/state writes are gitignored paths
  except the backlog inbox (tracked; changes only when findings change — quality-state
  precedent).
- `.harness/state/self-review.{json,md}` are generated → gitignored (supervision.html lesson).

## Acceptance criteria

- [x] `self-review` on the real repo yields findings for known debts (harness.py over
      burn-down target; provider sweep aging) with what/cause/fix proposals.
- [x] A finding is visible in `escalations` and on the `status --html` page with zero new GUI
      code; `--resolve` clears it and it does not re-raise while resolved.
- [x] Ratchet auto-tighten fires when slack ≥15% and never loosens.
- [x] Backlog inbox section is written idempotently (second run with unchanged findings = no
      diff).
- [x] Gate check runs the review when stale, skips cheaply when fresh; commit gate green.
- [x] `frictionObservations` round-trips: result → validation event → collector → recurrence
      finding at ≥2.

## Validation (MVP gate)

Scenario `testing/scenarios/se_self_review.py` green (seeded conditions + real end-to-end run);
M4 and M3.x scenario regressions green; commit + spec-pack gates rc=0.
