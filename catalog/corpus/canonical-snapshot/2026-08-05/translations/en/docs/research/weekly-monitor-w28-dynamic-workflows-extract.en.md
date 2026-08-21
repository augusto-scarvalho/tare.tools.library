# Weekly Monitor W28 (Dynamic Workflows) — Harness Extract

Source: weekly GPT digest supplied by the owner (2026-07-13). This is NOT a research round; citations are
unverified `[web]` references — ideas evaluated on internal merit against the real harness state. Fourth in
the W28 series (memory, code quality, multi-agent); numbering continues (EXP-9).

## Where the harness ALREADY covers the digest (no new work)

| Digest finding | Equivalent already operating here |
|---|---|
| “Convenience orchestration may be delegated; control orchestration stays in the harness” | This is production doctrine: `codex exec` ALREADY is hosted orchestration one level below (opaque inner loop behind typed WORKER_RESULT contract); budget/policy/evidence/review stay here (`workflow.json` budget blocks, delegation ledger, `review` verb) |
| Topology Cascade Router (digest priority #1) | Half-built, in shadow mode: `workflow.json.topologyRouter` records `wouldFork`/`recommendedWorkers`/`reasons` (including open circuit breakers) per workflow without acting — observe-only awaiting DW.4 (OWNER-GATED). Adding `hosted_multi_agent` to the taxonomy is one enum value when control phase is authorized |
| Confined dynamism (SpaCellAgent) + “do not auto-promote learned workflows” (priority #7) | Universal rule: agents do not mutate their own model/effort — harness spawns profiles from a catalog (task-profiles + model cards); self-evolution is SELF_EVOLUTION I4 (Deferred); promotion quarantine gate is EXP-3 already queued |
| Atomic snapshot discipline (LangGraph lesson) | Partial: `write_json` via os.replace (today’s torn-read fix), bounded checkpoint with reinjection. What we have NEVER tested is the PROPERTY “materialized state == event log == replay” → EXP-9 |
| Evidence ledger surviving opacity | records/escalations/delegation ledger exist; provenance gap (servedModel) is already queued as EXP-5 — hosted subagents would make it WORSE, reinforcing EXP-5 before any hosted trial |

## Extracted experiment (reversible; research-playbook template)

### EXP-9 — State-transition conformance probe (LangGraph-inspired) · HIGH priority
- **Hypothesis:** we assume, without testing, that three views of workflow state tell the same story —
  `workflow.json` (materialized), `trace.jsonl` (event log) and `async/` (runtime). DeltaChannel bugs are
  exactly the class that already bit us (torn reads, placebo hook, bounded-replay banner) — partial
  checkpoint pretending to be a snapshot.
- **Candidate invariants** (verified against real artifacts 2026-07-13): every `workersPlanned` has queued +
  terminal event in trace; workflow status consistent with worker statuses under joinPolicy; monotonic
  timestamps (createdAt ≤ worker started ≤ finished ≤ updatedAt); identical `asyncGroupId` in
  workflow.json/trace/async-group.json; `async/tasks/AT-*.json` ↔ workers 1:1; `phase` compatible with last
  trace event.
- **Baseline:** run probe across ALL retained workflows (including WF-E2E-TAIL) — zero LLM, read-only; any
  live violation is a finding.
- **Phase 2:** advisory doctor check — sibling of EXP-2 (compaction invariants) and EXP-4
  (declared-vs-real): same family, different surface (workflow state). **Reversal:** read-only probe;
  one-line advisory.

## DECISION item (not an experiment — goes to owner queue)

- **OpenAI hosted multi-agent as topology:** commoditizes fan-out, but (a) conflicts with overseer-plans
  doctrine — decomposition would move inside vendor, while owner decided plan is always overseer-owned;
  (b) reduces provenance/auditability — exactly EXP-5 gap, and realized graph becomes opaque; (c) our codex
  lane is subscription CLI — beta is Responses API (real API cost); (d) dynamic routing is DW.4 territory
  (OWNER-GATED). If a trial is ever authorized, digest abandonment thresholds are good defaults: latency gain
  <20%, cost +50%, or insufficient auditability → do not make default.

## Parked (with explicit trigger)

- **A/B hosted fan-out vs own DAG** (4 configurations): trigger = feature available in subscription lane +
  owner decision above.
- **Observability adapters for hosted subagents:** same trigger — without authorized trial, this is
  infrastructure for a backend we do not use.
- **Analyzer catalog with adaptive selection (SpaCellAgent applied to code audit):** reinforces already
  parked Oracle Action Router (code-quality extract) — same trigger: weeks of byOutcome/oracle telemetry.
- **Formal snapshot/delta/patch semantics (AWIR):** trigger = day workflows mutate mid-flight (replan,
  branch insertion). Today cycle is plan→run→reduce with no patching — it would formalize operations we do
  not execute. Practical LangGraph lesson enters through EXP-9.

## Critical verdict on the digest

Hosted fan-out commoditization does not change our architecture — it confirms the separation already in
operation (vendor may own inner loop; control, budget and evidence stay in harness), and the digest itself
reaches the same conclusion. The detail the digest did not know: our topology router already exists in
shadow mode inside every workflow.json, awaiting owner’s control decision. The genuinely useful weekly item
is one and cheap: EXP-9 tests as a property the state consistency we currently assume — the only lesson from
the LangGraph episode that applies to someone who does NOT use LangGraph. Hosted trial correctly remains
behind owner decision, with digest abandonment thresholds recorded.
