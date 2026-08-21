# SPEC-124 — `spec-index`: read-only spec inventory verb

Status: proposed 2026-07-12 (acceptance: testing/scenarios/si_spec_index.py).

Intake (SPEC-116 door NEW, from specs/templates/intake-refinement.md): request =
"a read-only spec inventory CLI verb — every spec, its scope, its
`Scenario:[id]`s, its legacy-frozen status" (Panel/UX Wave-0). Covered-check:
`records search spec index inventory` → no hit (`[]`); `doc-find spec index
inventory` → no enrichment hit (graphify-out absent in the worktree). Decision:
**NEW**. Surface is CLI-only.

## Goal

A supervisor can see the whole spec estate in one deterministic command:
`python scripts/harness.py spec-index` prints one row per `specs/**/*.md` —
scope, title, `Scenario:[id]`s, legacy-frozen status — and always exits 0.
Observe-only: it reads specs and `.harness/project.json`, changes nothing.

## Applicability

Applies to `scripts/harness_lib/spec_index.py` (`collect(root)`,
`cmd_spec_index`) and its one-line registration in
`scripts/harness_lib/cli_registry.py` (MF.1-r2 registry path, **zero
`scripts/harness.py` edits** — the `doctor` verb proved this path). Does not
change any existing verb, the workflow tree, gates, or state; no daemon, no
polling (observation must pay for itself).

## Requirements / invariants (numbered, testable)

1. **One row per spec.** `collect(root)` walks `specs/**/*.md` and returns one
   dict per file with keys `path` (posix, relative to `specs/`), `scope`,
   `title`, `scenarioIds`, `legacyFrozen`.
2. **Scope.** `scope` is the first path segment under `specs/`
   (`00-universal`/`40-features`/`templates`/…); `-` for files directly under
   `specs/`.
3. **Title.** `title` is the text of the first `# ` (level-1) heading; empty
   string when the spec has none.
4. **Scenario ids via the conformance parser.** `scenarioIds` reuses
   `spec_conformance._gherkin_ids` — the SPEC-116 gate's own parser — so the
   inventory and the gate never disagree about which `Scenario:[id]`s exist.
5. **Legacy-frozen.** `legacyFrozen` is true iff the spec's relpath or basename
   appears in `.harness/project.json` → `specConformance.legacy` (read via
   `read_json`, default `[]`; the live list stores basenames, matching
   `spec_conformance`'s `spec.name in legacy`).
6. **Read-only, rc 0.** `spec-index` prints a text table (or JSON with
   `--json`) and exits 0; it never writes.
7. **Registry-only surface.** The verb registers in `cli_registry.register()`;
   existing verbs' order and help text are unchanged and `harness.py` is not
   edited.

## Gherkin scenarios

```gherkin
Feature: spec-index inventory

  Scenario: [si-1] a conformant spec yields its Scenario ids
    Given a temp specs tree with one spec carrying a gherkin block
    When collect() runs against it
    Then its row lists exactly that block's Scenario ids, scope and title

  Scenario: [si-2] a legacy-listed path is flagged frozen
    Given a temp project.json whose specConformance.legacy names the spec
    When collect() runs against it
    Then the spec's row has legacyFrozen true

  Scenario: [si-3] spec-index exits 0 on this repo
    Given this repository
    When "python scripts/harness.py spec-index" runs
    Then it prints a table with at least one row and exits 0
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Reusar o parser Gherkin do gate em vez de um segundo regex | `scripts/harness_lib/spec_conformance.py` (`_gherkin_ids`, `_SCENARIO_ID`) — uma única semântica de "scenario id" |
| Semântica legacy = basename (com aceitação de relpath) | `scripts/harness_lib/spec_conformance.py:104` (`spec.name in legacy`); `.harness/project.json` `specConformance.legacy` armazena basenames |
| Registro via `cli_registry.register()`, zero edits em `harness.py` | `scripts/harness_lib/cli_registry.py` docstring (receita MF.1-r2); `specs/40-features/repo-health-doctor.md` (o verbo `doctor` provou o caminho) |
| Read-only, exit 0 sempre — observar, não controlar | memória "observation must pay for itself"; espelha o `doctor` WARN-only |

## Test strategy

- Behaviors: temp specs tree → row fields (path/scope/title/scenarioIds);
  temp `project.json` legacy entry → `legacyFrozen`; live CLI run exits 0 with
  ≥1 row (no hard row-count asserts — the spec estate grows concurrently).
- Edge cases: missing `.harness/project.json` → legacy defaults to `[]`
  (exercised by the temp tree in si-1); spec without a `# ` heading → empty
  title (rule 3, covered by collect()'s contract).
- Regression net: `testing/scenarios/cli_registry.py` frozen top-level surface
  (order preserved, `spec-index` appended before `workflow`) guards rule 7.
- Coverage: deterministic, stdlib-only, no LLM —
  `testing/scenarios/si_spec_index.py`.

## Validation

- `python testing/scenarios/si_spec_index.py` — si-1/si-2/si-3 all green.
- `python testing/scenarios/cli_registry.py` — registry surface intact with the
  new verb.
- `python scripts/harness-test.py smoke` and `spec-pack --no-project-commands` —
  template conformance + static integrity.
