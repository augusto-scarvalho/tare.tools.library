# SPEC-128 — Delegation cost + duration trend by model / agent type (OB.2)

Status: proposed 2026-07-12 (acceptance: testing/scenarios/ob_cost_trend.py).

Intake (SPEC-116 door NEW): request = "per-model/agent-type cost + duration
trend — the aggregate `delegation-cost-trend` rule watches only the summed
token series, so one model or role can drift while the mix keeps the aggregate
flat" (OB.2, P2). Covered-check: the existing rule family
(`specs/40-features/self-evolution-loop.md`, TE.2) has only the aggregate
series rule → extend, do not duplicate. Decision: **NEW** (this spec), scoped
to the deterministic half — OB.3's LLM diagnosis card stays out.

## Goal

Self-review flags a rising cost or duration trend inside one delegation group
(per `model`, per `agentType`) even when the aggregate delegation series looks
flat, using only data the cost ledger already records — no new collection, no
LLM, evaluated only when self-review runs.

## Applicability

Applies to `scripts/harness_lib/self_review.py` (`collect_metrics` attaches
`cost.delegations.rows`) and `scripts/harness_lib/self_review_rules.py` (the
per-group block after the aggregate trend rule). Does not change the existing
`delegation-cost-outlier` or aggregate `delegation-cost-trend` findings (ids,
text, thresholds stay byte-identical), the ledger writers, or any CLI surface.
OB.3 (diagnosis card / LLM half) is explicitly out of scope.

## Requirements / invariants (numbered, testable)

1. **Rows from the ledger only.** `collect_metrics` passes
   `cost.delegations.rows` = per-delegation dicts limited to `model`,
   `agentType`, `estTokens`, `durationS` — fields `record_delegation` already
   persists; nothing new is collected.
2. **Same pattern, per group.** For each group keyed by `model` and by
   `agentType`, the rule applies the exact aggregate pattern: median of the
   last 5 values > median of the previous 5 × `delegationCostTrendFactor`
   (default 1.3).
3. **Finding ids.** Rising `estTokens` fires
   `delegation-cost-trend:model:<name>` / `delegation-cost-trend:agent:<name>`;
   rising `durationS` fires `delegation-latency-trend:model:<name>` /
   `delegation-latency-trend:agent:<name>`.
4. **Sample floor per group.** A group with fewer than
   `delegationCostTrendMinSamples` (default 10) values for a field stays
   silent — sparse groups never alarm.
5. **Aggregate untouched.** The existing `delegation-cost-outlier` and
   aggregate `delegation-cost-trend` findings remain byte-identical;
   `testing/scenarios/se_self_review.py` passes unchanged.
6. **Deterministic only.** Pure stdlib over the metrics dict; no LLM, no
   daemon, no ledger writes (observation must pay for itself).
7. **Cost-to-success rollup (C6 / manuscript §9.5-b, amendment 2026-07-18).**
   `cost_metrics.summarize()` adds `delegations.costToSuccess` — additive, no
   existing key changes. Over the delegation corpus carrying an overseer
   `outcome`: `ctsTokens` = Σ estTokens ÷ #(outcome = kept) (the hard number);
   `costToUsefulOutcome` = Σ estTokens ÷ #(outcome ∈ {kept, reworked}) (rework
   is useful, with rework). `byModelCTS` applies the same calc grouped by
   `model` (the byX idiom; same `{model: {...}}` shape, no new structure). Any
   zero denominator yields `null` with a `note`, never a divide-by-zero.
   Honest limits recorded here, not silently dropped: `partial` and `rejected`
   are excluded from the useful denominator; workflows are excluded entirely
   (no per-task kept/rejected outcome — a workflow-level proxy would mislead);
   global + `byModel` only — no task-class stratification (no task taxonomy in
   the free-text `--task` log yet) and no per-session dimension (deferred until
   a consumer needs it).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Estender a MESMA família de regra, não duplicar a agregada | `scripts/harness_lib/self_review_rules.py` bloco TE.2 (o padrão last5/prev5 já existente); brief OB.2 |
| Rows vêm do ledger que já existe (`record_delegation`) | `scripts/harness_lib/cost_metrics.py` `record_delegation` persiste `model`/`agentType`/`estTokens`/`durationS` desde TE.2 |
| Knobs reutilizam `delegationCostTrendFactor`/`MinSamples` | espelham os defaults da regra agregada; um knob a menos até precisarem de tuning separado (ponytail ceiling no código) |
| Piso de 10 amostras por grupo | mesmo piso da regra agregada — grupos esparsos são ruído, não sinal |
| Sem LLM/daemon | memória "observation must pay for itself"; OB.3 é a metade LLM, fora deste slice |

## Gherkin scenarios

```gherkin
Feature: delegation cost and duration trend by group

  Scenario: [ob-1] a per-model rising series fires while the aggregate stays flat
    Given one model's delegation cost and duration rise while another's fall
      And the interleaved aggregate series stays flat
    When self-review evaluates the metrics
    Then delegation-cost-trend:model:<name> and delegation-latency-trend:model:<name> fire
      And the aggregate delegation-cost-trend does not

  Scenario: [ob-2] flat series stay silent
    Given every group's cost and duration series is flat
    When self-review evaluates the metrics
    Then no delegation finding fires

  Scenario: [ob-3] a group under the sample floor stays silent
    Given a rising group with fewer than 10 samples beside ample flat history
    When self-review evaluates the metrics
    Then no delegation finding fires

  Scenario: [ob-4-cts] cost-to-success over a corpus with overseer outcomes
    Given delegations with outcomes kept (10k), rejected (5k), reworked (8k)
    When cost_metrics.summarize computes delegations.costToSuccess
    Then ctsTokens is 23000 (Σ / 1 kept) and costToUsefulOutcome is 11500 (Σ / 2)
      And a corpus with no outcomes reports null denominators, never dividing by zero
```

## Ceilings (upgrade paths)

- Rows share `collect_metrics`' last-100-record window; widen only if a real
  group starves under the 10-sample floor while older ledger rows exist.
- Per-group knobs reuse the aggregate trend thresholds; split into dedicated
  keys only if the two ever need separate tuning.

## Test strategy

- Behaviors: mix-shift (rising model inside a flat aggregate) fires the model
  findings for cost and duration (ob-1); flat groups silent (ob-2); <10-sample
  group silent even while rising (ob-3).
- Edge cases: `rows` absent (older metrics dicts, se_self_review fixtures) →
  per-group block inert; `durationS: None` rows excluded from the duration
  series without crashing.
- Regression risks: byte-identity of the aggregate findings — guarded by
  `testing/scenarios/se_self_review.py` (unchanged, 56/56).
- Coverage impact: enforced via `testing/scenarios/ob_cost_trend.py`.

## Validation

- `python testing/scenarios/ob_cost_trend.py` — ob-1/ob-2/ob-3/ob-4-cts green.
- `python testing/scenarios/se_self_review.py` — 56/56, untouched (invariant 5).
- `python scripts/harness-test.py smoke --no-project-commands` — template
  conformance (`feature-spec-conformance:delegation-cost-trends`) + static
  integrity.

## Amendments

- 2026-07-18 (C6 / §9.5-b, LQ7-C6): added invariant 7 —
  `delegations.costToSuccess` (ctsTokens, costToUsefulOutcome, byModelCTS) in
  `cost_metrics.summarize()`. Additive/measure-only: no existing key changes,
  no CLI change (`harness.py metrics` already prints `summarize()`), no panel
  change. Acceptance: `ob-4-cts` in `testing/scenarios/ob_cost_trend.py`.

- 2026-07-31 (seat telemetry, owner demand "instrumentação e medição das cagadas
  dos overseers... vale para outras roles em geral"): added invariant 8 —
  `defectsBySeat` in `cost_metrics.summarize()`, a sibling of `trackRecord`
  (which stays byte-identical: it groups the seat that was CALLED, this one the
  seats that PRODUCED and MISSED). Additive/measure-only.
  - A SEAT is `(role, model, effort)`, all three non-empty or the row does not
    count. A partial seat is not a smaller truth, it is an unattributable one.
  - A defect is DECLARED through `harness.py defect <class> --evidence
    <commit|gate-run|audit|owner-report>:<ref> [--producer S] [--missed-by S]`,
    where `S` is `role:model:effort` or `self`. It appends `kind: "defect"` to
    the SHARED SPEC-173 sink (`.harness/state/defect-telemetry.jsonl`) — no
    second state file. At least one complete seat is required: a defect nobody
    can be attributed to is a story, not a measurement.
  - The class list is CONTROLLED (`cost_metrics.DEFECT_CLASSES`), because a
    free-text class is a column nobody can group by; `unclassified` is the
    pressure release, and a class that keeps landing there earns an amendment.
  - RATES, NOT COUNTS: a bare count measures volume, so the busiest seat looks
    worst and the idle one looks clean. Each side is divided by that seat's own
    RETAINED opportunities (the ledger is a 500-row ring) and reports `null` —
    never `0%` — when the denominator is zero.
  - Delegation rows gain nullable `effort` + `callerSeat`. The caller comes from
    `--caller-seat` or the session's `HARNESS_SESSION_ROLE/MODEL/EFFORT` triplet,
    NEVER from the routing pin: the pin says who should be seated, and this
    feature exists because the two diverge.
  - Mechanical signals (review WARNs, surviving mutants, waivers) are summarized
    UNATTRIBUTED. The tree has no trustworthy causal join from one to a seat, and
    inventing one would be the fabrication this instrument exists to expose.
  - NOT built, deliberately: no dashboard, no ranking, no score, no automatic
    blame, no `suggestedBurden` consumption (EXP-33 stays owner-gated).
  - Deviation from the plan, recorded: `chat_operator._turn_identity` was NOT
    refactored onto the shared seat builder. The builder demands a complete
    triplet; the GUI frame deliberately allows `model: null` / `effort: null`
    ("vendor default"). Merging them would either weaken the seat or break a
    frame contract that has teeth.
  - Acceptance: `ob-5-seat-attribution`, `ob-6-unknown-and-same`,
    `ob-7-denominator-honesty`, `ob-8-source-separation`,
    `ob-9-controlled-class-and-dedup`, `ob-10-delegation-caller` in
    `testing/scenarios/ob_cost_trend.py`; `telemetry_sink.py` self-check for the
    written/dropped return contract.
  - AUDIT DELTA (kimi k3-256k against the implementation, same day; it hit its
    quota mid-run and the findings below come from probes it had already run):
    * the child env splice CLEARS an unknown model/effort instead of letting it
      inherit. A child handed a new ROLE was keeping the PARENT's
      `HARNESS_SESSION_MODEL` and presenting `router|<the overseer's model>|high`
      — a seat both COMPLETE and WRONG. Every guard here tests completeness;
      none can test truthfulness, so the inherit path had to close.
    * an unparseable `--caller-seat` now REFUSES; it used to fall back to the
      session env, so a typo recorded a different seat than the one declared.
    * `record_delegation` reports whether the append landed and the CLI raises
      instead of printing `recorded` over a silent drop (the same defect the
      defect verb had already fixed, left behind in its sibling).
    * `ambiguousSeats`: one physical seat can arrive under two role words (a
      delegation says `implementer`, a defect says `worker`) and split into a
      clean-with-denominator key and an unrated-with-the-defect key. There is no
      safe automatic merge — role is a real dimension — so the split is REPORTED.
    * rates CAN exceed 100: the field is per-100-opportunities, not a percentage.
  - CONDITIONS (owner: "role, modelo, effort, capsule, etc"): the delegation row
    also carries `profile` and `packet {estTokens, budgetTokens, over}` —
    `packet_economy.compose_spawn` already computed both per spawn and discarded
    them. A seat handed an over-budget capsule under a high-risk profile errs
    more BECAUSE OF THE CONDITION; a rate that cannot see the condition bills the
    seat for it. Surfaced per seat as `conditions`, so the field is read.
  - Acceptance (delta): `ob-11-conditions-recorded`, `ob-12-ambiguous-seat-reported`
    in `testing/scenarios/ob_cost_trend.py`; the no-inherit rule is pinned in
    `chat_engines._self_check`.

- 2026-07-31 (Amendment v4 — trustworthy defect ledger, Layer 1 of 3: SEAT TRUTH.
  Backlog `session-seat-unwired` P1. The 2026-07-31 seat-telemetry amendment above
  defined the seat but left it UNWIRED on the path an overseer/worker actually runs
  harness.py from — `--producer self` was refused in a normal session, `--caller-seat`
  landed null 270/500 rows, and `--agent-type` defaulted silently to `implementer`,
  mislabelling planner/scanner lanes in the very `delegations.byModel` this feature
  calls "the audit"):
  - INVARIANT (v4.1) actual-hop seat injection. A spawned worker's
    `HARNESS_SESSION_ROLE/MODEL/EFFORT` is derived from the SAME resolved spawn as
    its command — role = `agent` > `profile` > taskProfile; model/effort = the
    resolved (override-applied) spawn — so a SPEC-115 fallback hop names the fallback
    card, never the failed primary and never the parent. The seat and the command can
    no longer describe different hops: on the async path both are persisted together
    (`sessionEnv` beside `command`) and swapped atomically on failover.
    `workflow_spawn.session_env` (a lib, kept off harness.py so the line-budget
    ratchet wt-3 stays green) is the single seat builder over the SAME `resolved_spawn`
    the command uses; `chat_engines.session_role_env` remains the only triplet
    formatter. UNKNOWN clears to "": missing, empty, or the `configured-by-executor`
    (`model_routing.CONFIGURED`) placeholder degrades the seat to unknown rather than
    presenting a fake-complete seat. SCOPE: the workflow-worker funnel (blocking +
    async). The classified/detached route-dispatch funnel is a tracked follow-up — its
    spawn 4-tuple env is the packet-economy env (`pes_packet_economy` pins it), so its
    seat must ride at that seam's `build_worker_spawn_env`, not the returned economy env.
  - INVARIANT (v4.2) `delegation --agent-type` is REQUIRED. The silent `implementer`
    default is removed: omitting the flag refuses at argument parsing (exit 2) with no
    ledger row, so a lane is never mislabelled by omission. `--effort`/`--caller-seat`
    stay nullable (honest null, never a routing-pin guess).
  - INVARIANT (v4.3) launch-seat integrity is MECHANICAL. A `codex exec` /
    `codex exec resume` command that pins neither `--model` nor
    `model_reasoning_effort` runs on the codex CLI default (measured gpt-5.5/medium)
    and `resume` silently drops the recorded seat; the `agent_spawn_economy` PreToolUse
    hook DENIES it (visible refusal), steering to `spawn-command --executor codex`,
    which pins from the routing profiles. A worker on the wrong seat corrupts
    `defectsBySeat`/`delegations.byModel`, so the guard belongs at the launch boundary,
    not in a human discipline note.
  - Acceptance: `dlc-l1-primary-seat`, `dlc-l1-fallback-seat`, `dlc-l1-unknown-clears`,
    `dlc-l1-no-parent-leak`, `dlc-l1-agent-type-required` in
    `testing/scenarios/dlc_session_seat.py`; `workflow_spawn._self_check` (resolution +
    fallback seat), `chat_engines._self_check` (sentinel clear), and
    `agent_spawn_economy._self_check` (codex seat deny).
  - Layers 2 (sink truth under gate-hold) and 3 (structured audit→record→intake) land
    as their own commits + amendment entries; this entry is the SEAT-TRUTH contract
    they build on.

- 2026-07-31 (Amendment v5 — trustworthy defect ledger, Layer 2 of 3: SINK TRUTH under
  a gate hold. Backlog `defect-sink-lost-under-gate-hold` P1. The SPEC-137 gate swaps
  the live tree for materialized HEAD while it holds `.harness/runs/gate-hold/`, so a
  `.harness/state` telemetry write DURING a hold lands on the doomed tree and is
  discarded on release. The measured incident had two halves — a `defect` row written
  under a hold vanished silently, and a READ during the hold saw the smaller
  materialized-HEAD ledger and produced a false "16 records lost" report):
  - INVARIANT (v5.1) held writes REFUSE VISIBLY, never drop silently. `common.gate_holding`
    is the SINGLE "held" predicate for every enforcement point — a gate-hold dir with at
    least one NON-`*-recovered` entry (a live OR abandoned-but-unrecovered hold; a
    `*-recovered` remnant is an ALREADY-recovered hold whose tree was restored, so it does
    NOT count — else the ledger writers refuse forever after any historical crash: audit,
    sonnet 2026-07-31). Two enforcement levels: the operator-facing CLI seam
    `scenario_isolation.hold_write_guard`/`hold_read_warning` GATE on `gate_holding`
    (`live_holds`, pid-alive, only ENRICHES the message with a pid/name — it must not
    decide the gate, or an abandoned hold's writes leak past it, which was the `chat`
    silent-loss gap), refusing `defect`/`route`/`chat` (added) alongside the existing write
    verbs before any partial effect; and the fail-safe writer layer (`telemetry_sink.sink_held`,
    the same `gate_holding` shared by `append_jsonl` and the hook writers) returns False +
    one stderr line for the non-CLI/automatic producers. A refused write creates NO byte.
  - INVARIANT (v5.2) `record_delegation` reports the TRUTH. `cost_metrics._append`
    returned None and swallowed every failure, so `record_delegation` returned `True`
    unconditionally and `cmd_delegation` printed "recorded" over a silent drop. `_append`
    now returns whether the row landed; the INTERACTIVE cost-metrics entries
    (`record_delegation` and `record_turn`/`chat`, since cost-metrics.json is held state)
    return/refuse visibly under a hold. `_append` itself stays hold-AGNOSTIC — `record_gate`
    writes through it from INSIDE the staged gate where a hold is live by construction, and
    refusing there would drop legitimate in-gate perf rows; the automatic writers
    (gate/workflow) keep ignoring the boolean.
  - INVARIANT (v5.3) held READS WARN. A read verb reaching the pre-dispatch seam during
    a live hold prints a NOTE that the `.harness/state` view is materialized HEAD, not
    live parked state, so counts can read smaller than reality. Warn, never block —
    the read is safe, only its view is stale. This is the half that turns a false
    "records lost" claim into an informed one.
  - SINK CLASSIFICATION (complete for current Python producers). Held `.harness/state`
    sinks are covered by CLI guard, a direct-writer backstop, or both: `defect-telemetry`
    + `injection-telemetry` (append_jsonl backstop); `cost-metrics` incl. delegation rows
    (`chat`/`delegation`/`workflow` CLI guard + record_delegation & record_turn backstops);
    `route-ledger` (`route` CLI + route_ledger backstop for its non-CLI callers);
    `search-telemetry` + `design-system-touches` (hook backstops — no CLI verb exists for
    these PreToolUse rotating writers); `token-calibration` + `vendor-fuel` (CLI-covered by
    `self-review` / `fuel` — now via the unified `gate_holding` seam, so live AND
    abandoned-unrecovered holds refuse; their writers return a value/path, so no data-layer
    backstop is added). `.harness/RUNS` sinks (kill-audit, validation, reckon-results,
    gate-perf, tier-level, events, trace) are deliberately OUTSIDE the hold and must NOT
    be refused.
  - Acceptance: `dlc-l2-defect-refused`, `dlc-l2-cost-route-refused`,
    `dlc-l2-hook-sinks-refused`, `dlc-l2-runs-sinks-safe`, `dlc-l2-held-read-warns`,
    `dlc-l2-abandoned-hold-refused`, `dlc-l2-recovered-not-held`, `dlc-l2-no-hold-regression`
    in `testing/scenarios/dlc_sink_hold.py`; plus the `telemetry_sink`, `cost_metrics`,
    `route_ledger`, and `scenario_isolation` self-checks — the `gate_holding` `*-recovered`
    correction is pinned by the `scenario_isolation` self-check (rename-to-recovered →
    allow) and `dlc-l2-recovered-not-held`. Layer 3 (structured audit→record→intake) lands
    as its own commit.

- 2026-07-31 (Amendment v6 — trustworthy defect ledger, Layer 3 of 3: structured audit →
  record → CLUSTERED intake. Backlog `defect-ledger-to-fix-queue` P2, depends on L1 seat
  truth + L2 sink truth. Before this an audit that named a real defect had nowhere
  structured to land — it lived in prose, was never recorded against a seat, never reached
  triage. Uses the EXISTING producer seam (`REVIEWER_RESULT.reviewFindings[]`, whose schema
  already permits additive per-finding properties), the EXISTING recorder
  (`cost_metrics.record_defect`), and the EXISTING queue (`intake_queue`) — no schema edit,
  no protected-contract edit, no third store):
  - INVARIANT (v6.1) OPTIONAL structured capsule. A review finding that is a genuine defect
    MAY carry `defect: {defectClass, evidence:{kind,ref}, producedBy, missedBy}`.
    `defectClass` must be a literal member of `cost_metrics.DEFECT_CLASSES`, `evidence.kind`
    of `EVIDENCE_KINDS`, `evidence.ref` non-empty; `producedBy`/`missedBy` are explicit
    complete `role:model:effort` seats or null with at least one complete — the literal
    `self` is FORBIDDEN in an artifact (it would resolve to the recorder, not the producer/
    reviewer). A reviewer that cannot name class/evidence/seat OMITS the capsule; an honest
    omission beats a guessed measurement. The recorder never maps title/recommendation prose
    to a class. `intake_queue` owns the validator and reuses `cost_metrics`'s controlled
    vocab (no duplicate list); the reviewer prompt block is built from that same live vocab
    so it cannot drift.
  - INVARIANT (v6.2) WHOLE-BATCH validation. One invalid capsule refuses the entire batch —
    no valid sibling records or clusters ahead of the bad row (`validate_review_defects`
    runs before any write, wired into `validate_reviewer_result` so an invalid capsule makes
    the reviewer result invalid everywhere).
  - INVARIANT (v6.3) record + CLUSTER, human-gated promotion. Each valid capsule is recorded
    via `record_defect` exactly as declared, and intake clusters by
    `(defectClass, evidence.kind, artifactRef)` where `artifactRef` is the ref before its
    first `#`. A PENDING cluster is upserted in place (sorted-unique refs); a DECIDED cluster
    is NEVER silently reopened. Ingestion writes NO `tasks.json` and creates no backlog row —
    `intake decide <id> spec|backlog|experiment|discard` is the only promotion. Idempotent:
    a rerun adds no second cluster, and a corrected re-declaration rides `record_defect`'s
    append-only latest-wins (`_defects_by_seat`) without inventing a second logical defect.
    Refused wholesale under a gate hold (L2 discipline). `workflow review-reduce
    <id> --validate-existing` transcribes on an already-run reviewer result — no second
    per-defect command.
  - Acceptance: `dlc-l3-structured-transcription`, `dlc-l3-no-prose-parser`,
    `dlc-l3-batch-refusal`, `dlc-l3-capsule-guards`, `dlc-l3-rerun-idempotent`,
    `dlc-l3-correction-latest-wins`, `dlc-l3-class-artifact-cluster`,
    `dlc-l3-human-promotion-only` in `testing/scenarios/dlc_defect_queue.py`; plus the
    `intake_queue` self-check. This closes
    the trustworthy-defect-ledger cluster (L1 seat truth + L2 sink truth + L3 pipeline).

- 2026-08-01 (Amendment v7 — seat truth reaches the ROUTE-DISPATCH funnel, resolving the
  v4.1 tracked follow-up). v4.1 scoped actual-hop seat injection to the workflow-worker
  funnel and named the classified/detached route-dispatch funnel (`harness.py cmd_route`
  `--dispatch`) as a follow-up: its spawn 4-tuple env IS the packet-economy env that
  `pes_packet_economy` pins, so an earlier attempt to inject the seat there broke pes-1/
  pes-3. Now `route_dispatcher.dispatch_command` returns the RESOLVED PROFILE (it used to
  discard it), and the detached lane's `HARNESS_SESSION_*` seat is built via
  `workflow_spawn.session_env_safe(profile, executor)` — the SAME resolution as the command
  (`executor_profile_spawn` applies the identical `route_spawn`) — and merged at the
  launch seam's `build_worker_spawn_env`, NOT into the returned packet-economy env, which
  stays seat-free. `session_env_safe` is fail-open: a seat glitch yields no seat rather than
  breaking a load-bearing AFK dispatch. Acceptance: `dlc-l1-route-dispatch-seat` in
  `testing/scenarios/dlc_session_seat.py` (profile returned, packet env seat-free, launch
  env carries the truthful seat, no parent leak) + `rt-14-dispatch-threads-profile`
  (4-tuple + seat-free packet env) + the `workflow_spawn` self-check (`session_env_safe`
  fail-open). The interactive-overseer seat (D1.3) and the codex-resume spawn-command
  builder (D1.5 half 2) remain the open follow-ups.

- 2026-08-01 (Amendment v8 — the INTERACTIVE-overseer seat, resolving D1.3). An
  owner-driven session gets no `HARNESS_SESSION_*` splice (nothing spawns it, so
  `chat_engines.session_role_env` never runs for it); `seat_from_env` then finds no
  seat and every `self` delegation/defect refuses. The one place the LIVE seat is
  recorded is the session transcript row — the same tail `overseer_model_guard`
  already reads for the live model (`message.model`), with the live effort on the
  row's top-level `effort` (empirically present, e.g. `xhigh`). So the seat is read,
  never fabricated: role = `HARNESS_SESSION_ROLE` or the `overseer` interactive
  default, model + effort colocated on one assistant row.
  - INVARIANT (v8.1) truthful-or-nothing. New hook `tools/hooks/overseer_seat_session.py`
    (SessionStart + UserPromptSubmit, paired with the model guard) writes
    `{role, model, effort, sessionId}` to `.harness/state/session-seat.json` (gitignored)
    ONLY when a COMPLETE live seat exists; no transcript / no assistant row / a row
    missing `effort` CLEARS the file, so `self` keeps refusing rather than riding a
    fabricated effort (the very defect class this ledger fights). Fail-open everywhere.
    A pre-commit sonnet audit caught the first draft treating `effort` as a reverse-scan
    SKIP filter — a newest turn without `effort` borrowed an OLDER turn's (model, effort),
    recording a model the session had dropped (e.g. the pin when a fallback actually ran);
    fixed to gate on the NEWEST real turn's own effort (synthetic markers still skipped),
    pinned by the `live_seat` borrow + skip-synthetic self-check cases and the scenario's
    borrow assertion.
  - INVARIANT (v8.2) same-session only. `seat_from_env` reads the file as a fallback
    (after the env triplet) via `_session_seat_file`, accepted ONLY when its
    `sessionId` == `CLAUDE_CODE_SESSION_ID`. A seat left by another or older session
    is never read — the exact silent mis-attribution (a fallback model wearing a
    different session's seat) that `seat_from_env`'s pin-refusal already guards. A
    complete env triplet still wins; the file is a fallback, not an override.
  - Acceptance: `dlc-l1-interactive-overseer-seat` in `testing/scenarios/dlc_session_seat.py`
    (hook writes the live seat; `self` reads it back same-session; a foreign sessionId
    refuses) + the `cost_metrics` self-check (env wins / same-session file / foreign
    refused / no-session-id) + the `overseer_seat_session` self-check (complete-writes /
    partial-clears / synthetic-skip / spawned-role-honoured). Live-verified in-session:
    the hook read this session's transcript to `overseer:claude-opus-4-8:xhigh` (the live
    fallback, not the `fable` pin) and `self` resolved. The codex-resume spawn-command
    builder (D1.5 half 2) remains the last open follow-up.

- 2026-08-01 (Amendment v9 — the codex-RESUME seat builder, closing D1.5 half 2 and the
  whole seat-truth follow-up set). v4.3 mechanized the launch-seat GUARD: the
  `agent_spawn_economy` hook DENIES a bare `codex exec resume` (which runs on the codex CLI
  default, measured gpt-5.5/medium, and silently drops the recorded seat) and steers to
  `spawn-command --executor codex`. This is the BUILDER that steer lands on.
  - INVARIANT (v9.1) the resume re-pins the routed seat BY CONSTRUCTION. `spawn-command
    --resume <SESSION_ID>` (`last` -> codex `--last`) splices `resume <id>` into the
    ALREADY-RENDERED spawn argv via `model_routing.apply_resume`, so the resume carries the
    IDENTICAL `--model` / `-c model_reasoning_effort=` / `--sandbox` pins the fresh spawn
    rendered from the routing profile — a resume can never drift onto a different (cheaper)
    seat than the fresh lane, because the two share one rendered argv. The tokens land AFTER
    every exec flag and BEFORE the trailing prompt positional: codex `exec resume` accepts
    those global seat flags ONLY before `resume` (a flag after it aborts clap with
    `unexpected argument`) — a pre-commit sonnet audit caught the first draft splicing right
    after `exec`, which left the pins after `resume` and produced a command codex REJECTS (a
    non-run, worse than a wrong seat); the fix matches the repo's own launch guard ("pin
    flags before the subcommand"), pinned by a self-check fixture that now carries the
    `--sandbox`/`--skip-git-repo-check` tokens the first draft omitted. No `--resume` -> argv
    byte-identical (every existing spawn untouched).
  - INVARIANT (v9.2) declarative per-executor, refuse-not-guess. The resume tokens are
    declared in `executors.json` (`resume.tokens`, `{sessionId}` substituted) — codex is the
    only executor with a recipe today; an executor without one REFUSES (`HarnessError`)
    rather than emit an unpinnable resume command. No codex-specific branch in `harness.py`
    (which sits at its wt-3 line budget): the change is net-zero there (signature + a render
    wrap + one kwarg), with the splice logic and its vocab in the lib.
  - Acceptance: `dlc-l1-codex-resume-seat` in `testing/scenarios/dlc_session_seat.py`
    (fresh spawn byte-untouched; `resume <id>` after `exec`; the routed card + effort ride the
    resume) + `model_routing._self_check` (splice / byte-identical no-op / `last`->`--last` /
    refuse-without-recipe). Live-verified: `spawn-command --executor codex --resume 01ABC`
    emitted `codex exec resume 01ABC --model <routed-card> -c model_reasoning_effort=<routed>`.
    This closes the trustworthy-defect-ledger seat-truth arc (L1 seat truth, L2 sink truth,
    L3 pipeline, route-dispatch seat, interactive-overseer seat, codex-resume seat).

- 2026-08-01 (Amendment v10 — the INTERACTIVE audit -> defect-ledger seam; enforcement M1 of
  3). The workflow reviewer path (v6) already validates and ingests optional
  `reviewFindings[].defect` capsules, but a DIRECT `reviewer`/`security-auditor` Agent
  returned only to the overseer and had no operator ingest seam — so an interactive audit's
  findings died in prose (measured 2026-08-01: two audits caught real defects; both recorded
  by hand only after the owner asked). The existing `defect` CLI now also accepts
  `defect ingest [PATH|-]`.
  - INVARIANT (v10.1) one pipeline, whole batch. `defect ingest` envelope-guards a UTF-8 JSON
    object with a top-level `reviewFindings[]` (the guard `validate_review_defects` lacks — it
    returns no errors for a missing/non-list field, so a malformed input must REFUSE here, not
    read as a zero-work success), whole-batch-validates, then passes the data UNCHANGED to
    `ingest_review_defects`. The CLI adds no recorder, clusterer, class-mapper, or seat
    resolver: a valid batch inherits the v6 recorder, latest-wins logical identity, PENDING
    upsert, DECIDED-never-reopen, human-only promotion, and the v5 gate-hold refusal. Missing
    PATH means stdin. The `defect <class>` declaration stays compatible (parser `--evidence`
    is now optional, so the handler owns the declaration's evidence requirement and rejects a
    stray positional path). Literal `self` remains forbidden in an artifact; only the
    single-defect declaration path resolves it. `harness.py` is byte-unchanged (net-zero,
    3234): the branch is one `cli_registry` row plus a `cmd_defect` dispatch, the handler lives
    in `intake_queue`.
  - INVARIANT (v10.2) interactive capsule contract. The canonical `reviewer` and
    `security-auditor` agent profiles now require a top-level `reviewFindings` array in the
    final HARNESS_RESULT and ask genuine attributable findings to carry the optional capsule
    defined by `intake_queue.defect_capsule_prompt_block()` (named, never copied — no vocab
    drift); uncertain class/evidence/seat means OMIT. The two Codex mirrors render from the
    Claude profiles via `agents pair`; the workflow reviewer prompt and its bytes are
    unchanged.
  - Acceptance: `dlc-l3-interactive-ingest`, `dlc-l3-interactive-stdin`,
    `dlc-l3-interactive-envelope-guard`, `dlc-l3-interactive-batch-refusal`,
    `dlc-l3-interactive-rerun`, `dlc-l3-interactive-decided-stays-decided`,
    `dlc-l3-interactive-hold-refusal`, `dlc-l3-defect-declare-regression`, and
    `dlc-l3-interactive-contract` in `testing/scenarios/dlc_defect_queue.py`, plus the
    `intake_queue` self-check (loader/envelope/stdin/held) and an `agents pair` dry run with
    `changes: 0`. This is enforcement M1; M2 (doctor ledger-health) and M3 (interactive-audit
    Stop backstop) follow as their own commits.

- 2026-08-01 (Amendment v11 — advisory defect-ledger health; enforcement M2 of 3). The
  ledger had a recorder, an ingest seam, and refusals, but nothing WATCHED the sink itself.
  A new WARN-only `doctor` row, `defect-ledger-health` (hosted by `repo_health.checks`,
  after `intake-staleness`), reads the shared sink defensively and reports four actionable
  dimensions: corrupt/undecodable JSONL lines; `kind=="defect"` rows with NEITHER a complete
  `producedBy` NOR `missedBy` seat (an unattributable defect is the exact failure the ledger
  forbids); whether the sink path is git-ignored; and whether it is accidentally tracked (a
  tracked sink leaks local telemetry).
  - INVARIANT (v11.1) advisory and fail-open. No malformed byte, JSON line, read failure,
    missing git executable, or non-git root may crash or fail `doctor`; provable health
    defects WARN and every uncertain git probe degrades to `unknown`/`n/a` (never a warning),
    with the helper's whole body wrapped fail-open to an `unreadable` OK row. `cmd_doctor`
    stays rc 0. The git probes interpret only return codes 0/1 (`check-ignore --no-index`,
    `ls-files --error-unmatch`); a non-git root is `n/a`, preserving the clean-root check.
  - INVARIANT (v11.2) attribution means at least one COMPLETE seat. The check reuses
    `cost_metrics.seat_identity`; a partial seat object does not count, and non-defect
    mutation telemetry sharing the sink (`mutate-run`/`survivor`/`waiver`, `review-warn`) is
    excluded. Intake-cluster/sink orphan checks are DEFERRED, not forgotten: manual `defect`
    declarations create no cluster, DECIDED clusters are durable, and the append-only sink
    and queue have different retention/lifecycle rules — no non-noisy invariant exists
    without a future shared correlation-id contract.
  - Acceptance: `rh-defect-ledger-health` and `rh-defect-ledger-git-hygiene` (git-repo
    fixtures: corrupt/partial-seat/non-defect rows; un-ignored and force-tracked sinks) in
    `testing/scenarios/rh_repo_health.py`, plus the pinned-`IDS` order guard, the `rh-2`
    clean-root all-OK, and the `rh-3` live-`doctor` rc-0-with-warns checks. Live-verified: the
    real sink reads `OK corrupt=0, unattributable=0, gitignored=yes, tracked=no`. Enforcement
    M2; M3 (interactive-audit Stop backstop) follows as its own commit.

- 2026-08-01 (Amendment v12 — interactive-audit Stop backstop; enforcement M3 of 3, closing
  the set). M1 gave the interactive audit a place to land and M2 watches the sink, but nothing
  reminded the overseer to actually record — the failure this whole cluster started from (the
  session's own two audit findings sat unrecorded until the owner asked). The existing
  `validate-before-stop` Stop hook (already a canonical Stop event for both adapters — no new
  hook or manifest wiring) now emits one non-blocking, idempotent reminder when a structurally
  observed completed `reviewer`/`security-auditor` Agent result carried a non-empty
  `reviewFindings` and NO `kind=="defect"` sink row was appended at or after that completion.
  - INVARIANT (v12.1) structural, low-noise signal. The detector pairs an assistant Agent
    `tool_use.id` (subagent_type in reviewer/security-auditor) with a later system-origin
    task-notification (`<tool-use-id>` match, `<status>completed</status>`) and parses the M1
    result contract from its `<result>` (html.unescape + stdlib JSON scan for a non-empty
    `reviewFindings`). Pasted prose that merely names the markers, other agent roles (e.g.
    `implementer`), failed/clean (`reviewFindings: []`) audits, and any defect row at/after the
    latest audit are all silent. The unobserved `ReportFindings` tool-use candidate is NOT
    used — no such structural row appears in live transcripts.
  - INVARIANT (v12.2) non-blocking and fail-open, exit code untouched. The M3 block runs after
    the hook's Required-files verdict has already returned; it only ever `print`s and never
    changes `stop_verdict`/the rc (the Required-files enforcement that returns 1 on a missing
    canonical file is preserved). A missing/truncated/garbled transcript, or an
    unreadable/corrupt sink, yields no nudge (uncertainty prefers a false negative — a missed
    reminder — to a false positive). `main` gained an optional `payload` (stdin fallback) so
    the self-check drives it without a terminal. The wording is a single constant.
  - Acceptance: the `validate_before_stop` self-check matrix (findings-without-record fires;
    both audit roles; prose / implementer-role / empty-findings / failed-status /
    malformed-result never fire; defect-before vs same-second vs later ordering; latest-audit
    selection; garbled transcript and corrupt sink stay silent; constant wording), executed by
    the `hk_hook_selfchecks` scenario. Note: `mutation_probe` excludes `tools/hooks/**` from AST
    mutation, so the oracle plants no mutant here — the negative self-check matrix is the proof.
    Live-verified against this session's transcript: 2 findings-carrying audits detected, and
    because the finding WAS recorded (dogfooded through M1's `defect ingest`), the backstop
    correctly stays silent. This closes the interactive-audit -> defect-ledger enforcement set
    (M1 ingest seam, M2 doctor health, M3 Stop backstop) atop the seat-truth arc.
