# SPEC-173 — Playbook compiler (Effective Playbook + Spawn Envelope + lockfile)

Status: SPEC-173, proposed 2026-07-30 (acceptance: `testing/scenarios/pbc_*.py` — one file per phase, named in Test strategy).

## Goal

Introduce a compile step between playbook sources and injected prompts: sources stay
versioned; every role consumes a compiled Effective Playbook produced by deterministic
composition with precedence and dedup; provenance is carried by a lockfile; delegated
workers receive a budgeted Spawn Envelope whose budget is enforced in the injecting
path. The compiler changes structure and mechanism only — never the CONTENT semantics
of doctrine. Owner decisions D054 (2026-07-30) are encoded here as final: one merged
role metamodel, inventory-plus-gap-fill phase 0 against a frozen baseline, effect-based
evaluation, and gradual engineering-grade rollout ending in planned retirement of the
concatenation path.

## Applicability

Applies to: `scripts/harness_lib/playbook_registry.py` (compose/verify/write_lock),
`scripts/harness.py` (`build_prompt`, `token_economy_line`, `playbook` CLI),
`tools/hooks/reload_context_after_compact.py` (`_assemble`),
`scripts/harness_lib/prompt_slots.py`, `scripts/harness_lib/packet_economy.py`,
`.harness/routing/playbook-registry.json` + `.lock.json`,
`.harness/routing/task-profiles.json`, and the 26 injection surfaces inventoried in
`docs/research/audit-playbook-injection-surfaces.md` (S1-S26).

Explicitly NOT covered: self-evolution/auto-editing of playbooks; active-frame runtime
paging or context GC; semantic compression (LLMLingua-class) and DSPy/GEPA
optimization; new vendor renderers; the CONTENT of protected canonical files
(structural edits only, via the reviewed `tools/hooks/protect_canonical_files.py edit`
flow); vendor-side surfaces outside repo control (S26 SubagentStart persona) — these
are classified explicitly-external, not compiled.

## Requirements / invariants (numbered, testable)

Phases are independently shippable (SPEC-116 door NEW). Each rule is testable on its
own; implementers report deviations against these numbers.

### Phase 0 — baseline + meters (inventory + gap-fill, NOT a telemetry system)

1. **Frozen BEFORE baseline.** The BEFORE side of every compiler comparison is the
   frozen export `docs/research/baseline-delegations-frozen-2026-07-30.json`
   (251 delegation rows, 2026-07-13..2026-07-30). It is never re-derived from
   `.harness/state/cost-metrics.json`, which is a 500-row live-evicting ring.
2. **Injected-bytes sink (gap d).** A new append-only jsonl
   `.harness/state/injection-telemetry.jsonl` records one line per role-prompt
   injection: `ts, role, session, bytesInjected, sourceCount`. The append happens
   inside the injecting hook (`reload_context_after_compact.py`) at the point where the
   payload is already assembled — no second assembly pass. Format mirrors
   `search-telemetry.jsonl`.
3. **Defect-series sink (gap b).** `review --plan` WARN rows (assembled in memory by
   `overseer_review.py`) and oracle-mutate survivors are persisted to an append-only
   jsonl sink at the point where each is already computed. No new computation — only
   persistence of existing in-memory verdicts.
4. **Meters are non-fatal and append-only.** A failed telemetry append never blocks or
   alters the injection/review/mutate flow it observes; sinks are plain append-only
   jsonl, never ring buffers.
5. **Effect-based evaluation.** The compiler's success metrics are deltas against the
   frozen baseline in: tokens per delegation (`byModelCTS` exists), defect rates in
   delegated work (outcome labels plus the rule-3 series), and outcome rates over
   time. The owner study's per-role budget ranges are sanity bounds only — never
   acceptance thresholds.

### Phase 1 — unified metamodel

6. **One role metamodel.** A single schema-validated role model subsumes both
   taxonomies — the 32 `playbook-registry.json` roles and the 12 `task-profiles.json`
   profiles. No permanent bridge table exists after this phase ships.
7. **Three assemblers converge.** `playbook_registry.compose`, `harness.build_prompt`,
   and `reload_context_after_compact._assemble` all resolve roles, chains, and budgets
   through the unified metamodel — no assembler keeps a private role taxonomy.
8. **Lockfile is the compiled-identity carrier.**
   `.harness/routing/playbook-registry.lock.json` (per-role `chainHash` via the
   existing `write_lock`) extends to name every compiled source as a `(name, sha)`
   pair per role — the provenance record a replay consumes.
9. **Every surface classified.** The metamodel classifies each of the 26 audited
   injection surfaces as either `compiled` (enters the compiler) or
   `explicitly-external` with a stated reason (e.g. `CLAUDE.md` vendor-ambient, S26
   vendor persona). No surface is unclassified; `front-desk.md` and
   `harness-operator.md` (chain-orphans today) must resolve to one of the two classes
   or be scheduled for deletion in Phase 4.

### Phase 2 — compiler v0 (deterministic composition, precedence, dedup)

10. **Byte-stable output.** Compiled output for identical inputs is byte-identical;
    replaying a lockfile reproduces the output hash-identical.
11. **Dedup with the canonical test case.** Precedence+dedup resolves passages restated
    across sources to one copy per compiled output. The 7 machine-detected H2
    collisions on `loop-overseer` (`playbook loop-overseer --verify`) are the canonical
    case: compiled `loop-overseer` contains exactly one copy of each colliding section.
    Compiled size per role is <= today's concatenation.
12. **Lockfile regenerated in the same commit; staleness gated.** Any change to a
    compiled source regenerates the lockfile in the SAME commit, and a stale lockfile
    is detected by a gate scenario that FAILS (not advises). Motivating live escape:
    commit `171f6c8` changed `AGENTS.md` with a stale lock, `--verify` reported
    lock-drift on all 32 roles, and no scenario failed — a diagnostic-never-silent
    overflow of the same class this spec closes.
13. **Content-semantics invariant.** The compiler never changes doctrine CONTENT
    semantics. Per-role content-equivalence between compiled and concat output
    (same normative passages present, dedup and ordering aside) is a checkable property
    and a precondition for Phase 4 rule 18.
14. **Recompilation is NO-CHANGE.** `prompt_slots` `(name, sha)` identity is the
    change-detection primitive. Recompiling without any source change yields identical
    `(name, sha)` pairs, and churn alarms treat it as NO-CHANGE — never as a new
    instruction.

### Phase 3 — spawn envelope v0

15. **Budget enforced in the injecting path.** Per-role byte/token budgets come from
    the unified metamodel and are enforced by the code that injects — not only by
    scenario asserts. (Today SPEC-138's 40-line/3,200 B budget is checked solely at
    `testing/scenarios/osw_overseer_warmup.py:42`; the injecting hook never reads it.)
16. **Overflow is a diagnostic failure.** Budget overflow FAILS with a diagnostic
    naming the overflowing source. Silent truncation is prohibited.
17. **Role-scoped injection.** Sources are injected only to the roles whose chains
    include them. The overseer-warmup "ignore this if you are a worker" workaround
    retires: worker-class payloads no longer carry `overseer-warmup.md` (1,611 B to
    every role today, disclaimer at line 3).

### Phase 4 — retirement (gradual, engineering-grade)

18. **Flagged coexistence, then flip.** Compiled mode ships behind a flag; the concat
    path stays default until per-role parity (rule 13 content-equivalence) is shown;
    then the default flips. Rollback is a flag flip — no revert — until retirement
    completes. No experiment-registry proof burden: the bar is "don't break the
    harness mid-swap".
19. **Planned retirement deletes the old world.** After a stable window on the flipped
    default, the concat path and dead surfaces are DELETED (not archived in place).
    Chain-orphan prompts (`front-desk.md`, `harness-operator.md`) are deleted or
    re-homed per their rule-9 classification. No surface is deleted while unclassified.
20. **Protected-files flow.** Every structural edit this spec causes to `AGENTS.md` or
    `.harness/prompts/*` goes through `tools/hooks/protect_canonical_files.py edit` —
    the compiler grants no bypass.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Compile step: source != final prompt; Effective Playbook + lockfile + Spawn Envelope | Owner study `docs/research/guia-playbooks-engineering-2026-07-29.html` (63 sources); intake `specs/40-features/playbook-compiler.intake.md` |
| Merge the two taxonomies into one metamodel, no bridge table (rules 6-7) | Owner decision D054 item 1 (final, 2026-07-30); measured split: 32 registry roles vs 12 profiles, three parallel assemblers (`docs/research/audit-playbook-injection-surfaces.md` sec.2) |
| Phase 0 = inventory + gap-fill against a FROZEN export, not a telemetry system (rules 1-5) | D054 item 2; `docs/research/audit-playbook-metrics-baseline.md` sec.3 verdict — (a)/(c) already answered by 251 delegation rows; the ring is live-evicting (chat-turn already 7 days stale); (b)/(d) are the only genuine gaps |
| Injected-bytes sink shape and placement (rule 2) | `audit-playbook-metrics-baseline.md` sec.2(d): zero time-series history, one manual snapshot; minimal-meter recipe sec.3 mirroring `search-telemetry.jsonl` |
| Defect-series sink (rule 3) | `audit-playbook-metrics-baseline.md` sec.2(b): WARN rows and mutate survivors computed in memory, never persisted — persistence-only gap |
| Effect-based evaluation; study ranges as sanity bounds only (rule 5) | D054 item 3; `byModelCTS`/`usefulRate` already computed (`audit-playbook-metrics-baseline.md` sec.1, track_record row) |
| Lockfile as compiled-identity carrier (rule 8) | Existing `write_lock` per-role `chainHash` (SPEC-170 chain; `audit-playbook-injection-surfaces.md` sec.2) |
| Classify every surface compiled/external (rule 9) | `audit-playbook-injection-surfaces.md` S15/S26 + "registry is not the complete map" finding (7,747 B of chain-orphan prompts) |
| Byte-stable, hash-replayable output (rule 10) | Intake acceptance criterion 1; `prompt_slots.py` `(name, sha)` identity flow |
| Dedup canonical case = 7 loop-overseer H2 collisions (rule 11) | `playbook loop-overseer --verify` machine-detected collisions; duplication map `audit-playbook-injection-surfaces.md` sec.3 item 6 (also: Graphify policy restated on 5 surfaces, HARNESS_RESULT on 4) |
| Lock staleness must FAIL a gate scenario (rule 12) | Live escape: commit `171f6c8` shipped an `AGENTS.md` edit with a stale lock, 32 lock-drift findings, zero scenario failures (intake criterion 6) |
| Content-semantics invariant + parity gate before flip (rules 13, 18) | Intake risk "dedup can change meaning — a precedence bug injects the WRONG doctrine"; D054 item 4 |
| Recompilation-without-source-change is NO-CHANGE (rule 14) | Intake risk: churn alarms must distinguish recompilation from a genuinely new instruction; `prompt_slots.py` tri-state diff |
| Budget enforcement in the injecting path (rules 15-16) | Intake criterion 3; measured gap: SPEC-138 enforced only at `osw_overseer_warmup.py:42` (`audit-playbook-injection-surfaces.md` sec.1, budget-enforcement sites) |
| Role-scoped injection retires the warmup disclaimer (rule 17) | `audit-playbook-injection-surfaces.md` sec.3 item 7: 1,611 B injected to EVERY role, disclaimer-as-workaround at `overseer-warmup.md:3` |
| Gradual rollout, flag rollback, planned retirement (rules 18-19) | D054 item 4 (final); intake rollback note "rollback cost is a flag flip, not a revert" |
| Protected-files flow (rule 20) | Intake risk "canonical-file protection"; AGENTS.md protected-files doctrine + `CLAUDE.md` shim |

No UI surface — Gherkin scenarios omitted (SPEC-116 inv. 4; intake: "UI surface? no").

## Ceilings (upgrade paths)

- Injected-bytes meter counts bytes and source count only; add token estimates when a
  compiled-vs-concat token claim needs more precision than bytes/4.
- Content-equivalence check is normalized-text set comparison per role; upgrade to a
  semantic diff only if a real precedence bug slips past it.
- Dedup operates on H2-section identity (the existing `_collisions` detector); finer
  passage-level dedup (e.g. the 4-way HARNESS_RESULT restatement across different
  files) waits until section-level wins are measured against the baseline.
- Surface classification is a static field in the metamodel; no runtime discovery of
  new injection surfaces — re-run the audit method when hooks change.

## Test strategy

- Behaviors to verify (one acceptance scenario per phase, `testing/scenarios/pbc_*.py`):
  - `pbc_meters.py` (Phase 0): running the injecting hook appends a well-formed
    `ts/role/session/bytesInjected/sourceCount` line (rule 2); WARN/mutate sinks
    receive rows where the verdicts are computed (rule 3); a simulated append failure
    does not alter hook output (rule 4); the frozen baseline file exists, parses, and
    holds the 251 delegation rows (rule 1).
  - `pbc_metamodel.py` (Phase 1): the metamodel validates against its schema; all 32
    registry roles and all 12 profiles resolve through it (rules 6-7); every S1-S26
    surface carries a compiled/explicitly-external classification, none missing
    (rule 9); lockfile entries carry per-source `(name, sha)` (rule 8).
  - `pbc_compile.py` (Phase 2): two compilations of identical inputs are
    byte-identical and lockfile replay reproduces the hash (rule 10); compiled
    `loop-overseer` contains exactly one copy of each of the 7 colliding H2 sections
    and compiled size <= concat size per role (rule 11); per-role content-equivalence
    holds (rule 13); recompilation without source change yields identical
    `(name, sha)` pairs and no churn alarm (rule 14).
  - `pbc_lock_stale.py` (Phase 2, gate scenario): mutating a compiled source in a
    scratch copy WITHOUT regenerating the lock makes the check FAIL — the `171f6c8`
    escape class reproduced and closed (rule 12).
  - `pbc_envelope.py` (Phase 3): an over-budget source produces a diagnostic failure
    naming that source in the INJECTING path, with no truncated payload emitted
    (rules 15-16); a worker-role payload contains no `overseer-warmup.md` bytes
    (rule 17).
  - `pbc_retire.py` (Phase 4): flag off serves concat output; flag on serves compiled
    output; after retirement the concat code path and chain-orphan files are absent
    and every deleted surface was classified (rules 18-19).
- Edge cases: a role present in only one taxonomy pre-merge; an empty chain; a source
  file with no H2 headings (head-fallback surfaces S5-S9); lockfile missing entirely
  vs stale; budget exactly at the boundary.
- Regression risks: SPEC-138 (`osw_overseer_warmup.py`) and SPEC-170 registry
  scenarios must stay green through every phase; prompt-slots churn alarms must not
  fire on recompilation (rule 14 guards this).
- Spec-pack conformance: this document keeps the REQUIRED headings verbatim
  (feature-spec-conformance gate).
- Coverage impact: enforced (each phase is gated by its `pbc_*` scenario before the
  next phase ships).

## Validation

With `HARNESS_QUIET=1` and `HARNESS_AGENT_OUTPUT=compact` exported before every
`harness.py` call:

- `python scripts/harness.py playbook loop-overseer --verify` — 0 collision advisories
  and 0 lock-drift findings once Phase 2 lands (today: 7 collisions; the lock-drift
  half was already zeroed by the fa57612 regen).
- `python testing/scenarios/pbc_meters.py`, `python testing/scenarios/pbc_metamodel.py`,
  `python testing/scenarios/pbc_compile.py`, `python testing/scenarios/pbc_lock_stale.py`,
  `python testing/scenarios/pbc_envelope.py`, `python testing/scenarios/pbc_retire.py` —
  the acceptance files the numbered rules map to, per phase.
- `python scripts/harness.py gate-staged` (detached; poll
  `python scripts/harness.py verify-status`) — spec-pack green including
  feature-spec-conformance on this file, and `pbc_lock_stale.py` wired into the gate
  so lock staleness fails, not advises.

## Amendments

**A1 (2026-07-30) — rule 11 addendum: a tombstone stub is not an override.**
Incident `758d900`: 7 canonical `loop-overseer` sections had been reduced to 121 B
"moved verbatim to overseer-playbook.md" stubs. Leaf-wins precedence made each stub
supersede the 1.4-5.3 KB section it pointed at, the compiled view lost 17,041 B of
doctrine, and rule 13 tolerated it because the HEADING was still present
(superseded-not-lost reads identical to compiled-correctly). Rule 11 therefore also
requires that the winner of a dedup collision be a plausible override: when a winning
segment is smaller than `INVERSION_RATIO = 0.10` of the segment it displaces
(LF-normalized, as compiled), `playbook_registry.verify` emits an rc-bearing
`dedup-inversion` finding naming role, heading, and both sides with their byte sizes,
computed by the pure helper `playbook_compiler.dedup_inversions`. Explicit NON-change:
`compile_role` output is untouched — the ratio is a read-only grader, no compiled byte
and no `compiledSha` moves, so rule 10 stands. Acceptance: `pbc_compile.py` pc-6
(hermetic tombstone fires, comparable-size override stays silent, real repo at zero).
