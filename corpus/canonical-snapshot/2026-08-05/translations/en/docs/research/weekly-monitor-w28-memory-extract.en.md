# Weekly Monitor W28 (memory/context) — Harness Extract

Source: weekly GPT digest supplied by the owner (2026-07-13). This is NOT a research round
(owner instruction: do not run the skill); citations are unverified `[web]` references — the ideas below
were evaluated on their internal merit against the real harness state. If an experiment graduates, source
verification happens in that round.

## Where the harness is ALREADY ahead of the digest (no new work)

| Digest finding | Equivalent already operating here |
|---|---|
| #1 Shared Selective Memory (share specs/schemas/configs/constraints; discard session reasoning) | This is the current architecture: git-versioned `specs/` + `schemas/` + `.harness/routing` ARE the shared workspace; packets embed exactly specs/constraints; WORKER_RESULT persists claim+evidence, never CoT |
| #3 FARMA (posture) | High/blocker findings REQUIRE evidence (validator); escalations/records carry provenance; safe-action breaker limits automation fed by model-generated findings |
| #5 Governed SelfMem (propose→judge→authorize→commit→feedback) | Self-review loop (SPEC-109) has exactly that shape: findings → escalations → bounded safe-actions → breaker |
| Platform: runtime tool search | `catalog` (CE.4): name page = 15% of full helps, paging on demand |
| #4 owner_scope | `subject` dimension (self\|target) crosses records/escalations/events/calibration since isolation rounds |

## Extracted experiments (reversible; research-playbook template)

### EXP-1 — Action-preserving truncation (CoACT-inspired) · HIGH priority
- **Hypothesis:** harness observation compressors (`truncate_text` OUTPUT_CAP=8000 for panel/chat,
  `maxWorkerOutputChars`, `tail_lines`) frequently discard decision-bearing lines (`fix:`, `next:`,
  `harness error:`, traceback tail). The important metric is not compression ratio but “does the next
  action survive?”.
- **Baseline:** existing real corpus (validation-results.jsonl, worker run logs, gate outputs) truncated
  by current rules.
- **Metric:** % of samples where a decision-bearing line present in raw output disappears from truncated
  output (deterministic probe, zero LLM).
- **Phase 2 (only if metric is poor):** tail-and-signature-preserving truncation at ONE seam
  (`common.truncate_text`), behind byte-identical comparison when nothing matches. **Reversal:** one seam,
  one revert.

### EXP-2 — Compaction invariant evaluator (Distortion-inspired) · HIGH priority
- **Hypothesis:** our three compaction surfaces (checkpoint, context digest, handoff) may lose decision
  invariants unnoticed (handoff already regenerated above budget once; digest already dropped evidence in seed).
- **Baseline:** current surfaces, measured as-is.
- **Metric:** deterministic post-reinjection checklist — current item, phase, verify commands, constraints,
  open errors, approved decisions — each present/absent. Becomes advisory doctor check (intake-staleness
  pattern). **Reversal:** advisory check, remove one line.
- Note: token-audit already measures digest COST; this measures DISTORTION — the two halves of finding #2.

### EXP-3 — Evidence gate on promotion (FARMA-lite) · MEDIUM/security priority
- **Hypothesis:** the only path where model rationalization becomes actionable state without mandatory
  evidence is reduce→`workflow promote` (recommendations become tasks).
- **Baseline:** current promotes (audit how many carry evidence handles).
- **Metric/phase 2:** promoted tasks without evidence receive `quarantined: true` until verification
  (intake/escalations vocabulary already has the pattern). **Reversal:** additive ignorable flag.

## Parked (with explicit trigger)

- **#4 Full Contextual Integrity** (purpose_scope/allowed_roles/retention): trigger = harness becomes
  multi-tenant/SaaS. Today single-owner; `subject` covers existing isolation.
- **#7 Bounded-memory testbed** (full-trace/window/state/episodic matrix): cost side already exists
  (requiredReads with/without digest); behavior side costs model tokens — trigger = dedicated evaluation budget.
- **#8 Retention-policy reward:** current `delegations.byOutcome` is exactly the seed of the proposed
  reward; trigger = harness learning phase (same family as SELF_EVOLUTION I4, Deferred).
- **Platform: vendor-native compaction behind a common interface:** trigger = chat engines expose API
  compaction; today vendor CLI `/compact` covers it.

## Critical verdict on the digest

Overall direction is compatible with what our own memory G2/G3 rounds already indicated — reinforcement,
not structural novelty. The genuinely actionable and cheap insight is EXP-1+EXP-2: measure compression by
its effect on the next action/decision rather than by tokens. The FARMA warning deserves EXP-3, but the
baseline posture is already good. Nothing here justifies an architectural change before measurements exist.
