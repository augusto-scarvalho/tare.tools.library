# SPEC-125 — `research`: research-round admin (list + guarded delete)

Status: Active (v2 — research-index `show` amendment, 2026-07-13; acceptance:
testing/scenarios/ra_research_admin.py + testing/scenarios/ri_research_index.py).

Intake (SPEC-116 door NEW, from specs/templates/intake-refinement.md): request =
"research-admin — `research list` + a GUARDED `research delete`; throwaway
research rounds (docs/research/*.md + lingering WFs + records refs) accumulate
with no cleanup; deterministic list + dry-run-default delete" (RF.2, owner
backlog refinement). Covered-check: `records search research round delete
cleanup` → one hit, and it is the RF.2 request commit itself, not an existing
capability; `doc-find research round delete cleanup` → no enrichment
(graphify-out absent in the worktree). Decision: **NEW**. Surface is CLI-only.

## Goal

An operator can see every research round and remove a throwaway one safely:
`research list` prints one deterministic row per `docs/research/*.md` round
(git-tracked flag, linked active workflows, records references), and
`research delete <slug>` is dry-run by default — it deletes nothing until
`--apply`, and refuses a git-tracked round without `--allow-committed`.

## Applicability

Applies to `scripts/harness_lib/research_admin.py` (`rounds(root)`,
`delete_round(root, slug)`, `cmd_research`) and its one-line registration in
`scripts/harness_lib/cli_registry.py` (MF.1-r2 registry path, **zero
`scripts/harness.py` edits** — the `doctor`/`spec-index` verbs proved this
path). Reuses `workflow scrub --force` for linked-WF cleanup and
`records.add_entry`/`records.search` for the ledger — no second lifecycle or
ledger implementation. Does not change any existing verb, the workflow tree,
gates, or state shapes; no daemon, no polling.

## Requirements / invariants (numbered, testable)

1. **One row per round.** `rounds(root)` iterates `docs/research/*.md` MINUS
   `RESEARCH.md` (the index) and returns one dict per round with keys `slug`,
   `path`, `tracked`, `linkedWfs`, `recordsRefs`.
2. **Tracked, fail-closed.** `tracked` comes from
   `git ls-files docs/research/<file>` (subprocess, timeout 15 s): non-empty
   output → true. When git cannot answer (rc != 0, missing binary, timeout),
   `tracked` is **true** — fail closed so delete refuses rather than
   destroying committed history.
3. **Linked workflows.** `linkedWfs` lists the workflow ids under
   `.harness/workflows/active/` whose `workflow.json` `task` string contains
   the slug.
4. **Records references.** `recordsRefs` is the count returned by
   `records.search(root, slug)` (derived, gitignored index; canonical state
   untouched).
5. **Dry-run by default.** `research delete <slug>` WITHOUT `--apply` prints
   the doc, linked WFs, and records refs it WOULD remove and performs ZERO
   writes/deletes — no doc unlink, no scrub, no records write.
6. **Tracked rounds are guarded.** `--apply` on a `tracked` round without
   `--allow-committed` is refused with a message naming `--allow-committed`
   (CLI exit 2 via HarnessError).
7. **Apply semantics.** `--apply` unlinks the round doc, runs
   `python scripts/harness.py workflow scrub <wfid> --force` (the EXISTING
   scrub, via subprocess) for each linked WF, and writes a tombstone via
   `records.add_entry(root, "note", "research round <slug> deleted",
   tags=["research", "tombstone"])`.
8. **Path confinement.** The slug is untrusted input: the delete target must
   `resolve()` to a path DIRECTLY under `docs/research/` (prefix check);
   traversal, nesting, and `RESEARCH.md` itself are refused before any lookup.
9. **Registry-only surface.** The verb registers in `cli_registry.register()`;
   existing verbs' order and help text are unchanged and `harness.py` is not
   edited (frozen-list token disclosed in `testing/scenarios/cli_registry.py`).

## Gherkin scenarios

```gherkin
Feature: research-round admin

  Scenario: [ra-1] list shows rounds with tracked flags
    Given a temp root with two round docs, one committed in a temp git repo,
      and an active workflow whose task names the committed round
    When rounds() runs against it
    Then RESEARCH.md is excluded, the committed round is tracked with the
      linked WF listed, and the scratch round is untracked

  Scenario: [ra-2] delete without --apply changes nothing
    Given the same temp root
    When delete_round runs on the scratch round without apply
    Then the report says dry-run naming the doc it would remove
      and the doc, the workflow dir, and the canonical worklog are untouched

  Scenario: [ra-3] --apply removes the doc and writes a tombstone
    Given the same temp root
    When delete_round runs on the untracked scratch round with apply
    Then the doc is gone and the worklog holds a note tagged research/tombstone

  Scenario: [ra-4] a tracked round is refused without --allow-committed
    Given the same temp root
    When delete_round runs on the committed round with apply only
    Then it is refused with a reason naming --allow-committed
      and the doc still exists
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Dry-run por default, ato só com `--apply` | `agents pair --apply` (`scripts/harness_lib/cli_registry.py`) — o padrão guarded-apply já existente na superfície |
| Reusar `workflow scrub --force` em vez de segunda lifecycle | `scripts/harness_lib/workflow_lifecycle.py:267` (`workflow_scrub` é dono das regras de segurança de fase/lock) |
| Tombstone via `records.add_entry`, nunca ledger markdown | `specs/40-features/records-ledger.md` (SPEC-112: único write path sancionado) |
| `tracked` fail-closed quando git falha | delete destrutivo: na dúvida, recusar (espelha o fail-closed do gate de secrets) |
| Confinamento de path resolve()+prefixo para slug não confiável | `scripts/harness_lib/ui_panel.py` (validação de wfid antes do scrub — trust boundary antes do argv) |
| Registro via `cli_registry.register()`, zero edits em `harness.py` | `scripts/harness_lib/cli_registry.py` docstring (receita MF.1-r2); `specs/40-features/spec-index.md` |

## Test strategy

- Behaviors: temp root with two fabricated rounds (one committed via a temp
  `git init`) + one fabricated active WF → ra-1 inventory fields; ra-2 dry-run
  zero-change (doc + WF dir + worklog byte-identical); ra-3 apply unlink +
  tombstone entry; ra-4 tracked refusal naming `--allow-committed`.
- Edge cases: traversal slugs (`../x`, nested) refused by path confinement
  (rule 8, asserted beside ra-2); missing slug → HarnessError (rule 6 path);
  `RESEARCH.md` never listed nor deletable (rules 1, 8).
- Regression net: `testing/scenarios/cli_registry.py` frozen top-level surface
  (order preserved, `research` appended before `workflow`) guards rule 9.
- Coverage: deterministic, stdlib-only, no LLM —
  `testing/scenarios/ra_research_admin.py`.

## Validation

- `python testing/scenarios/ra_research_admin.py` — ra-1/ra-2/ra-3/ra-4 green.
- `python testing/scenarios/ri_research_index.py` — the v2 show/index
  scenarios (ri-1..ri-3) green.
- `python testing/scenarios/cli_registry.py` — registry surface intact with the
  new verb.
- `python scripts/harness.py research list` on this repo; a dry-run
  `research delete <slug>` leaves `git status` clean.
- `python scripts/harness-test.py smoke` — template conformance + static
  integrity (`feature-spec-conformance:research-admin`).

## Amendments

### v2 (2026-07-13) — research-index R0: the `show` action

The `research` verb grows a read-only `show <slug>` action backed by the new
`scripts/harness_lib/research_index.py` (roadmap `screens-specs-research.md`
R0). `parse_round` derives, best-effort, the gallery-grade shape of one
hand-written round doc — phases present, question, declared budget, evidence
rows counted by confidence class (forte/moderada/fraca), wave WF-ids,
experiment headings — with a `parseErrors` field instead of ever crashing;
`research_snapshot(root)` joins the parsed rounds with the v1 admin fields
(tracked/linkedWfs) plus LIVE workflows whose profile starts with
`research-`, and `research show --json` (no slug) prints it — the feed the
future `gui-research-screen` (OPEN) consumes. Every rendered view names the
round doc as the source of truth (derived, non-authoritative — the
context-digest stance). `list`/`delete` semantics are unchanged.

```gherkin
Feature: research index (R0 show action)

  Scenario: [ri-1] a real round parses into the gallery shape
    Given the memory-context-management round doc
    When parse_round runs
    Then phases 0-5 are present, evidence rows count by confidence class,
      both wave WF-ids surface and there are no parse errors

  Scenario: [ri-2] hand-written garbage degrades to parseErrors, never a crash
    Given a broken round doc and a live research workflow on a temp root
    When research_snapshot runs
    Then the index excludes RESEARCH.md, carries admin fields per round and
      joins the live research workflow

  Scenario: [ri-3] the CLI show surface is live and honest
    Given this repository
    When research show runs for a real and an unknown slug plus research list
    Then the real one exits 0 naming the derived stance, the unknown exits 2
      listing known rounds, and the v1 list output is unchanged
```
