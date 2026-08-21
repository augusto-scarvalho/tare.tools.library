# SPEC-103 — Trustworthy Evaluation (Backlog M3)

Status: **Done** (executed 2026-07-09; M3.0–M3.5). Acceptance ran as rerunnable scenarios under
`testing/scenarios/` (m2_mvp_scenario 18/18, m3_1_skeptical_reviewer 13/13,
m3_2_preimplementation_contracts 10/10, m3_3_nonlinear_reduce 7/7,
m3_4_5_registry_and_planner 7/7). Execution note: the M3.3 premise "intermediates already on
disk" was false — `workflow retry` deleted them; archiving was added as part of the milestone.

Supervision series (SPEC-101…105). Independent of the GUI track; can run in parallel with M4
planning. Evidence base: `docs/HARNESS_IMPROVEMENT_IDEAS.md` §B1/§A1/§B2/§C1/§A2.

## Goal

Evaluation the supervisor can trust: reviewers that do not talk themselves into approving, "done"
agreed before implementation instead of reconstructed after, and reduce steps that pick by
criteria rather than recency.

## Grounding (research and evidence)

- **Anthropic long-running-apps article (primary source):**
  - *Self-evaluation bias:* agents "confidently praise the work — even when the quality is
    obviously mediocre"; separation of generation from evaluation is necessary but not
    sufficient — the external evaluator must be tuned toward skepticism.
  - *"Out of the box, Claude is a poor QA agent":* early evaluators identified legitimate issues,
    then decided they weren't a big deal and approved anyway. Fixes that worked: hard thresholds
    per criterion (fail one → fail the sprint), prompts demanding proactive edge-case testing.
  - *Sprint contracts:* generator proposes implementation + success criteria; evaluator reviews
    the proposal *before code is written* — bridges spec and implementation without early
    over-specification. Over-detailed planner specs cause cascading errors.
  - *Non-linear improvement:* later iterations were sometimes worse than middle ones; never
    assume the last attempt is the best.
  - *Capability assumptions:* every harness component encodes an assumption about what the model
    can't do (context resets: essential for Sonnet 4.5, dead weight for Opus 4.6). Backed
    academically by arXiv 2606.25447 (harness scaffolding interacts with post-training; not a
    fixed engineering detail).
- **MAST (arXiv 2503.13657):** specification and verification dominate the 14 empirical failure
  modes — this milestone attacks both heads directly.

## Applicability

Spawn-profile prompts, `.harness/prompts/subagent-contract.md` result contracts, workflow reduce
logic, `HARNESS_ARCHITECTURE.md`. Not gate mechanics (SPEC-101), not new subcommands (SPEC-102).

## Scope

In scope:
1. Skeptical evaluator: reviewer profile tuning + `REVIEWER_RESULT` with named criteria,
   pass/fail threshold each, a mandatory "issues found and why each does/doesn't block" section,
   and an explicit prohibition on approving with unresolved blockers.
2. Pre-implementation contracts: worker's first deliverable is proposed acceptance criteria;
   approval precedes implementation; `acceptanceCriteria` field in `HARNESS_RESULT`; gated by
   task classification (small tasks skip it).
3. Non-linear reduce: reducer compares retry-chain intermediates by criteria, not recency.
4. Assumptions registry section in `HARNESS_ARCHITECTURE.md` (component → capability assumption →
   re-evaluate signal), seeded with packet sizing, reset-per-packet, reviewer pass, classifier
   thresholds.
5. Planner guardrail: product context and architecture, not implementation detail.

Out of scope: capability-edge evaluation axis (B3 — deferred, needs a difficulty signal);
changing which tasks get reviewers at all.

## Requirements / invariants

- `REVIEWER_RESULT` remains backward compatible: new fields optional, old results still validate.
- Anti-leniency wording is testable: the prompt must contain the explicit instruction that
  identified blockers cannot be waived by the reviewer itself — waiving is a human decision
  (escalate, don't approve).
- Acceptance-criteria round-trip is visible in run artifacts: proposed → approved → graded
  against, all three recorded.
- Reduce keeps intermediates comparable (already on disk under `WF-*/`); selection rationale is
  recorded in `REDUCE_RESULT`.
- No agent self-modifies scope/profile — failed contracts escalate (existing invariant, restated
  because Hive's self-evolving-graph anti-pattern is the tempting shortcut here).

## Design anchors (verified 2026-07-09)

- `.harness/prompts/subagent-contract.md` defines `HARNESS_RESULT`, `WORKER_RESULT`,
  `REDUCE_RESULT`, `REVIEWER_RESULT` — **protected file**: `HARNESS_ALLOW_PROTECTED_WRITE=1` +
  snapshot regen (`tools/hooks/protect_canonical_files.py snapshot`) required, and the edit is
  deliberately review-worthy.
- `.harness/prompts/task/00-start-here.md` — also protected; touch only if the pre-implementation
  step changes the task entry flow.
- Task classification (which profile a task gets) already exists — the pre-implementation
  contract gate reuses it; do not build a second classifier.
- Loaded-language audit (F3): while editing reviewer/planner prompts, strip superlatives and
  aesthetic adjectives — "museum quality"-class phrases converge outputs (Anthropic article).
- Assumptions registry goes in `docs/HARNESS_ARCHITECTURE.md` — not protected; plain docs change.

## Acceptance criteria

- [x] Reviewer prompt contains named criteria with thresholds and the no-self-waiver rule.
- [x] Replayed known-bad diff (seed from a past fixed defect) is blocked with named criteria
      (the CRLF fixture-restore defect, commit 7846524, is the seed).
- [x] A medium task runs the full acceptance-criteria round-trip, visible in artifacts.
- [x] A small task skips the contract step (classification gate works).
- [x] Reduce over a seeded retry chain (best result in the middle) picks the middle one and
      records why (`REDUCE_RESULT.attemptSelection`).
- [x] `HARNESS_ARCHITECTURE.md` has the registry with 7 seeded components.
- [x] Protected-file snapshot regenerated; `--fixture protected-files` green.

## Test strategy

- Acceptance mechanism (M3.0 retro, 2026-07-09): each M3.x acceptance runs as a script under
  `testing/scenarios/` following the `m2_mvp_scenario.py` pattern — subprocess-CLI only
  (operator-faithful), byte-restored configs, `workflow scrub` cleanup, scenario events
  filtered from `events.jsonl`/`harness-trace.jsonl`, per-check scorecard, exit 0 = green.
  That pattern proved itself: 18/18 checks and a clean tree on the first full run.
- Behaviors: the replay scenario is the core regression asset — keep the bad diff as a fixture.
- Edge cases: reviewer finds zero issues (must still enumerate criteria, not just approve);
  contract proposal rejected (worker revises, does not implement); reduce with a single result.
- Regression risks: existing workflows parsing `REVIEWER_RESULT`/`REDUCE_RESULT`; prompt-length
  effects on small-model profiles.
- Coverage impact: enforced for reduce selection logic; informational for prompt content.

## Validation (MVP gate)

Known-bad diff blocked by the skeptical reviewer with named criteria; one medium task end-to-end
with the contract round-trip visible. Then `python scripts/harness-test.py commit` and
`--fixture protected-files` green.

## Universal baseline impact

`specs/00-universal/code-quality.md`, `coverage-and-regression.md`,
`software-engineering-guardrails.md`, `ai-agent-safety.md` (evaluator autonomy limits).

## Escalation triggers

Any change to result-contract required fields; any temptation to let the reviewer waive its own
thresholds; classifier changes that alter which profiles existing tasks get.

## Amendments

### v2 — review-gate freshness + testimony cross-check, observe-only (W29.N3), 2026-07-28

"Reviewer approve sem evidência fresca" was unobservable: nothing tied the
approving testimony to the sha the workflow's evidence was produced at, and an
approve could sit on top of a worker capsule whose own oracle said `failed`.
Two observe-only blocks now ride `workflow_review_gate_status` (persisted via
`workflow["reviewGate"]` at finalize; they NEVER flip `approved`/`errors` —
enforcement is a future owner decision, EXP-31 consumes the flags):

- **freshness** — the reviewer echoes `capsuleHeadSha` (optional field, schema
  + manual shape check; the packet prompt prints the workflow's N1 `headSha`
  anchor and instructs "never echo blindly"). The block stamps
  `anchorMatch` (echo vs `workflow.headSha`; null when either side is
  missing), the `evidence_decay.assess` verdict for the anchor, and `events`
  using the W29.N2 shared vocabulary (`head-move` when decay reads
  aging/stale — never a minted string).
- **testimonyCrossCheck** — approve × `oracleEvidence.exitClass` ∈
  {failed, error, timeout} per worker (via `evidence_bundle`, handles-only).
  Cross-check APENAS: no recompute (SEC.7 stays out of scope, conflict C4 of
  the W29 round). Empty when the review does not approve or capsules are
  unreadable (fail-open: measurement never breaks the gate).

Teeth: `m3_1_skeptical_reviewer.py` §5 — anchor line in the prompt, malformed
echo rejected, anchored approve validates, flags stamped, and the invariant
`observe:flags-never-flip-approved`.
