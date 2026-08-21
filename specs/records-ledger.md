# SPEC-112 — Records ledger

Status: implemented 2026-07-10 (SPEC-112; acceptance: `testing/scenarios/rl_records_ledger.py`). Migrated `docs/CHANGELOG.md` (deleted by SPEC-112) and the Done history of `docs/IMPLEMENTATION_BACKLOG.md` / `docs/VV_PLAN.md` into the worklog.

## Goal

Give the project one durable, queryable memory instead of hand-maintained
markdown ledgers. Historical records live in a canonical, git-diffable JSON
worklog; a derived SQLite/FTS5 index makes the whole corpus searchable on
demand; a small always-in-context "head" keeps the latest records in front of
every agent without loading the mass.

## Applicability

Applies to how the harness records and retrieves project history (milestones,
changes, decisions, releases, notes) and how it surfaces related state
(escalations, validations, cost records, self-review findings, spec status,
commits). It does not change any agent's model/reasoning policy, and it does
not replace git — git remains the source of truth for code.

## Scope

In scope:
- canonical worklog `.harness/state/worklog.json` (+ `worklog-archive.json`) and the `harness.py log` write path;
- derived index `.harness/state-store/records.db` (gitignored, rebuildable) and `harness.py records search|recent|rebuild`;
- the always-in-context head section in `.harness/context/CONTEXT.md` (`render_head`);
- migration of `docs/CHANGELOG.md` (deleted by SPEC-112), the Done history in `docs/IMPLEMENTATION_BACKLOG.md`, and the `VV_PLAN.md` results record into the worklog.

Out of scope:
- a new judgment/criticality layer (self-review SPEC-109 already owns that);
- retrieval ranking beyond FTS5 rank / recency;
- network sync, remote stores, or a GUI over the ledger.

## Requirements / invariants

Numbered, testable normative rules:

1. **Single write path.** New historical records enter ONLY through
   `harness.py log <kind>` (`add_entry`). Hand-authored markdown ledgers are
   prohibited; `docs/CHANGELOG.md` (deleted by SPEC-112) is retired by migration.
2. **Canonical is tracked JSON.** The worklog is `{"schemaVersion": 1,
   "entries": [...]}`; each entry is `{at, kind, title, body, refs, tags}`
   with `kind ∈ {milestone, change, decision, release, note}`.
3. **Bounded hot file + archive spill.** The hot worklog holds ≤ 300 entries;
   on overflow the OLDEST entries spill into `worklog-archive.json` (same
   schema, unbounded, tracked). No record is ever dropped.
4. **Derived index is rebuildable and gitignored.** `records.db` under
   `.harness/state-store/` is dropped and recreated from `collect_records`; it
   is never the source of truth and is rebuilt on demand when stale or missing.
   The module works with or without FTS5 (plain-LIKE fallback, same API).
5. **Retrieval returns handles, never large bodies.** `search`/`recent`
   truncate title/body to ~200 chars and always carry `source`+`ref` so the
   full record is dereferenced just-in-time.
6. **Small head, one writer.** The `<!-- ledger:head:start -->…end -->` section
   of `CONTEXT.md` is ≤ 30 lines, written only by `render_head`, byte-stable
   when inputs are unchanged, and never touches text outside its markers.
7. **Every reader degrades.** A missing or corrupt source (worklog, escalations,
   cost, self-review, quality, specs, git) is skipped, never raised; writers
   never crash a caller.

## Acceptance criteria

- [x] `records recent` returns ≥ 1 record with rc 0 on the real repo.
- [x] `records search bind` finds the migrated QA record (title/body mentions "bind").
- [x] Adding 305 records leaves the hot worklog at exactly 300 and the archive at 5 (oldest spilled).
- [x] `render_head` is byte-idempotent, ≤ 30 lines, and preserves text outside the markers.
- [x] `records rebuild` returns rc 0 and reports the row count.
- [x] FTS5 and forced plain-LIKE search both find a seeded term.
- [x] `docs/CHANGELOG.md` (deleted by SPEC-112) is deleted and every reference to it is repointed at the ledger.

## Test strategy

- Behaviors to verify: kind validation, 300-bound + archive spill, collect
  shapes across sources, FTS + LIKE parity, staleness-triggered rebuild, head
  idempotency/cap/marker-safety, kind filter.
- Edge cases: corrupt/missing sources, git absent, OneDrive write locks (one
  retry), empty terms, FTS5 unavailable.
- Regression risks: `harness.py` line ceiling (≤ 2961), `records.py` lib budget
  (< 900), every `subprocess.run` bounded by `timeout=`, `state-store/`
  staying gitignored.
- Coverage impact: enforced via the module self-check and the acceptance scenario.

## Validation

- `./.venv/Scripts/python.exe scripts/harness_lib/records.py` — module self-check.
- `./.venv/Scripts/python.exe testing/scenarios/rl_records_ledger.py` — acceptance scenario.
- `harness-test.py smoke|spec-pack|scenarios --no-project-commands` — gates green.

## Universal baseline impact

- `specs/00-universal/software-engineering-guardrails.md`: bounded modules
  (records.py < 900, harness.py ≤ 2961) and startup-context economy (the head
  keeps required reads small).
- `specs/00-universal/testing-and-quality-gates.md`: self-check + acceptance
  scenario as the proportional evidence.
- No security/privacy/dependency surface: stdlib only, local, no network.

## Escalation triggers

- Any demand to add a network-backed or remote records store, or to make the
  derived index authoritative → `review`.
- Any change that would let something other than `add_entry` write historical
  records, or that widens the head beyond 30 lines / writes outside its markers.
- A new judgment/criticality mechanism on records (would overlap SPEC-109) → human decision.

## v2 amendment — class-B storage split (2026-07-16)

Supersedes the storage clauses of invariants 2, 3 and 6; every other invariant
(single write path, bounded hot+archive, derived index, handles-only retrieval,
readers degrade) is unchanged.

- **Canonical is git-diffable JSON on disk, no longer tracked by the project
  repo.** `worklog.json`, `worklog-archive.json`, `escalations.json`,
  `intake-queue.json` and `experiments.json` are class-B internal journals:
  gitignored here, mirrored durably into the private state home
  (`tools/state_home_sync.py` → `$HARNESS_STATE_HOME` or `~/.harness-home/<repo>`,
  itself a git repo — history and diffability move there). Rationale: exports and
  a future client-facing remote must not carry the team's internal work trail
  (see `release_integrity.PRIVATE_FILES`).
- **The head renders to `.harness/context/LEDGER_HEAD.md`** (untracked, injected
  at session start as an optional file), not into `CONTEXT.md` — CONTEXT.md is
  pure class-A documentation. Marker format, 30-line cap, single writer and
  byte-stability are unchanged (`records.LEDGER_HEAD_REL`).
- **Absence is a first-class state.** A fresh clone has none of these files;
  invariant 7 (every reader degrades) is what makes that legal, and
  `testing/scenarios/pc_post_clone.py` locks it.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Ledger canônico append-only; views derivadas | PROJECTMEM (arXiv:2606.12329); OpenHands/OpenCode na taxonomia de harnesses (arXiv:2604.03515); event sourcing c/ SQLite (sqliteforum.com/p/event-sourcing-with-sqlite) |
| Índice SQLite/FTS5 derivado e reconstruível; canônico segue JSON rastreado | PROJECTMEM (views regeneráveis); precedente interno graphify-out/symbols.json; política git do repo |
| Cabeça pequena sempre-em-contexto + massa consultável via tool | MemGPT (arXiv:2310.08560, core vs archival); agentic-design.ai/patterns/memory-management (Hierarchical Memory); Anthropic effective-context-engineering (JIT handles) |
| Retrieval devolve handles, nunca corpos grandes | Generative Agents (arXiv:2304.03442, memory stream recency/relevance); agentic-design.ai (MRWO) |
| Hot bounded + archive; compaction | agentic-design.ai (Memory Consolidation); OpenHands condensation-by-marker; precedente interno events.jsonl→escalations.json |
| Sem novo judgment layer | PROJECTMEM judgment ≈ self-review SPEC-109 (reusar) |
