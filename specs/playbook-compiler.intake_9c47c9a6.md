# Intake refinement — door NEW checklist

## Request (verbatim)

> agora, quero que você leia um estudo que fiz a forma ideal de construção dos
> playbooks, que hoje aqui no harnes possuem um conceito distorcido
>
> bora. também faça as delegações necessárias

(Owner, 2026-07-29. The study: `docs/research/guia-playbooks-engineering-2026-07-29.html`,
63 sources. Its thesis: playbook-source ≠ final prompt — sources stay versioned, agents
consume a compiled **Effective Playbook** per task with precedence+dedup and a provenance
**lockfile**; subagents get a budgeted **Spawn Envelope**; phase 0 is a token-telemetry
baseline BEFORE any compiler; do not start with self-evolution.)

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search playbook compiler effective spawn envelope` | `[]` — no hit |
| doc-find | `python scripts/harness.py doc-find playbook compile spawn envelope lockfile` | code-embryo hits only (`playbook_registry.py`, `prompt_slots.py`, `packet_economy.py`); no covering spec |

Decision: **NEW**.

## Goal

Introduce a compile step between playbook sources and injected prompts — selective
per-task composition with precedence+dedup, per-role budgeted spawn envelopes, and a
provenance lockfile — without changing the CONTENT semantics of today's doctrine.

## Scope

In scope:
- Phase 0 telemetry baseline: injected bytes/tokens per role per session, recorded —
  ships BEFORE any compiler code. Seed numbers (audit 2026-07-29,
  `.harness/handoff/audit-playbook-injection-surfaces.md`): hook payload 6,617–9,361 B
  per role under the already-enforced `TOTAL_BUDGET=9800`; full `--compose` contracts
  26,789–53,991 B on demand; 26 distinct injection surfaces.
- Metamodel schemas for role/procedure/skill sources, RECONCILING the two parallel
  taxonomies and assemblers that exist today: `playbook_registry.compose` (32 registry
  roles) vs `harness.build_prompt`/`token_economy_line` (12 `task-profiles.json`
  profiles), plus the de-facto third assembler in
  `tools/hooks/reload_context_after_compact.py:_assemble`.
- Compiler v0: deterministic composition + dedup + precedence, emitting a lockfile via
  the existing `prompt_slots.py` identity flow (name+sha). Dedup proof of concept: the 7
  machine-detected H2 collisions on `loop-overseer` (`playbook --verify`) resolve to one
  copy.
- Spawn envelope v0 for delegated workers: budget read from `task-profiles.json`;
  overflow fails with a diagnostic — NEVER silent truncation. Role-scoped injection
  replaces today's workaround (overseer-warmup.md reaches EVERY role including workers,
  1,611 B, carrying its own "ignore this if you are a worker" disclaimer at line 3).
- Builds on existing embryos, does not replace them: `prompt_slots.py` (proto-lockfile),
  SPEC-138 warmup budget, subagent-contract packets + D038 excerpts (proto
  delegation-capsule), `capability-panels.md`/`task-profiles.json`,
  `playbook_registry.py` (SPEC-170 chain — `write_lock` already emits per-role
  `chainHash`), `packet_economy.py` (`compose_spawn` already returns
  `{env, budget, promptSuffix}`), hooks as enforcement.

Out of scope:
- Self-evolution / auto-editing of playbooks.
- Active-frame runtime paging; context GC.
- Semantic compression (LLMLingua-class); DSPy/GEPA optimization.
- New vendor renderers beyond existing adapters.
- Touching protected canonical files' CONTENT — structure/mechanism only, via the
  reviewed protected-files flow.

## Actors & surfaces

- Actors: overseer, delegated workers, hooks.
- Surfaces (CLI / GUI / API / internal): CLI + internal.
- UI surface? no → Gherkin optional.

## Proposed acceptance criteria

- [ ] `playbook <role> --compose` gains a compiled mode: byte-stable output for
  identical inputs, plus a lockfile naming every source (name, sha) — replay of the
  same lockfile reproduces the output hash-identical.
- [ ] Compiled output per role is ≤ today's concatenation, with dedup of passages
  restated across sources (audit §3 maps 7 duplication families, e.g. the Graphify
  policy on 5 surfaces, HARNESS_RESULT obligation on 4); any budget overflow FAILS
  with a diagnostic naming the overflowing source.
- [ ] Budget enforcement lives in the INJECTING path, not only in scenario asserts —
  today SPEC-138 (40 lines/3200 B) is checked solely at
  `testing/scenarios/osw_overseer_warmup.py:42` while the injecting hook never reads it.
- [ ] Worker spawn envelopes declare and respect a per-role token budget read from
  `task-profiles.json` (closing the tracked per-role enforcement gap,
  `capability-panels.md:138`).
- [ ] Phase-0 telemetry exists BEFORE the compiler ships; the compiler's token/byte win
  is measured against that baseline.
- [ ] A playbook-source change re-snapshots the lockfile in the SAME commit and a stale
  lockfile is DETECTED (hook or gate). Live escape that motivates this: commit
  `171f6c8` changed AGENTS.md without regenerating
  `.harness/routing/playbook-registry.lock.json`; `playbook --verify` reported
  lock-drift on all 32 roles and NO gate scenario failed on it.

## Risks / blast radius

- Canonical-file protection: AGENTS.md and `.harness/prompts/*` are protected
  control-plane files; all structural edits go through the reviewed
  `protect_canonical_files.py edit` flow.
- Dedup can change meaning: a precedence bug injects the WRONG doctrine — the compiler
  must prove content-equivalence per role before the concat path is retired.
- Vendor slot-machinery interplay: compiled output feeds the same slots
  `prompt_slots.py` watches; churn alarms (sec8) must distinguish recompilation from a
  genuinely new instruction.
- The registry is not the complete map: `front-desk.md` + `harness-operator.md`
  (7,747 B) belong to no role chain; the vendor SubagentStart persona block is injected
  outside repo control. The metamodel must decide whether such surfaces enter the
  compiled world or are explicitly declared external.
- Rollback: keep the literal-concat path as the default until compiled/concat parity is
  proven per role; rollback cost is a flag flip, not a revert.

## Open questions for the human

- Merge the two role taxonomies (32 registry roles vs 12 task profiles) into one
  metamodel, or keep both and compile a bridge table?
- Does phase-0 telemetry ride an existing hook (e.g. session-start/prompt-slots) or a
  new one?
- Per-role budget numbers: adopt the study's ranges (router 400–1.2k … overseer 2–6k
  tokens) or measure phase-0 first and set from data?
- When parity is proven, does compiled mode become the default for `--compose`, or stay
  opt-in behind a flag for a deprecation window?

## Owner answers (2026-07-30, amendment — all four questions closed; also D054)

1. **Taxonomies: MERGE.** One metamodel; no permanent bridge table.
2. **Telemetry: a DEDICATED meter is acceptable, but its main value is
   AFTER-vs-baseline tracking.** The owner's hypothesis — largely confirmed by the
   existing stores — is that historical data already covers the BEFORE side (the
   delegation ledger records tokens + kept/partial/rejected/reworked outcomes per
   model|agent with usefulRate). Phase 0 is therefore mostly INVENTORY + one gap-fill
   (injected-bytes-per-role, which no store captures today), not a new telemetry system.
3. **Budgets: derive from data, and measure EFFECT, not just size.** Absolute injected
   bytes say little; the spec's evaluation MUST relate the playbook policy to harness
   efficiency metrics — tokens per delegation, defect rates in delegated work
   (rejected/reworked, review findings, oracle-mutate survivals), outcome rates over
   time. The study's ranges are sanity bounds, not law.
4. **Rollout: GRADUAL, engineering-grade, not experiment-grade.** Coexistence window
   with the concat path, then a planned RETIREMENT/destruction of the old artifacts once
   stable. No formal x-y-z proof burden — the bar is "don't break the harness mid-swap",
   and rollback stays a flag flip until retirement.
