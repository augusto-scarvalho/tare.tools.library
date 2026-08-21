# SPEC-127 — `docs-tree`: read-only docs+specs inventory verb

Status: proposed 2026-07-12 (acceptance: testing/scenarios/dt_docs_tree.py).

Intake (SPEC-116 door NEW, from specs/templates/intake-refinement.md): request =
"a deterministic, scope-tagged read-only inventory of `docs/` + `specs/`"
(P1, Wave-0). Covered-check: `spec-index` covers `specs/**/*.md` only — no
verb inventories `docs/`, no verb shows the tree shape or non-md files.
Decision: **NEW**. Surface is CLI-only.

## Goal

A supervisor can see the whole documentation estate in one deterministic
command: `python scripts/harness.py docs-tree` prints an indented tree of
`docs/` and `specs/` — every directory, markdown file (with its title) and
other file, each tagged with its top-level scope — and always exits 0.
Observe-only: it reads the two trees, changes nothing.

## Applicability

Applies to `scripts/harness_lib/docs_tree.py` (`collect(root)`,
`cmd_docs_tree`) and its one-line registration in
`scripts/harness_lib/cli_registry.py` (MF.1-r2 registry path, **zero
`scripts/harness.py` edits** — doctor/spec-index/failure-patterns proved the
path). Does not change any existing verb, the workflow tree, gates, or state;
no daemon, no polling (observation must pay for itself).

## Requirements / invariants (numbered, testable)

1. **One row per entry.** `collect(root)` walks `docs/` and `specs/` ONLY
   (depth-first, children sorted by name) and returns one dict per directory
   and file with keys `path` (posix, relative to the repo root), `depth`,
   `kind`, `title`, `tag`.
2. **Depth.** `depth` is the number of path segments minus one (`docs` → 0,
   `docs/OPERATOR_GUIDE.md` → 1, `specs/40-features/docs-tree.md` → 2).
3. **Kind.** `kind` is `dir` for directories, `md` for `*.md` files (case-
   insensitive suffix), `other` for everything else.
4. **Title.** `title` is the text of the first `# ` (level-1) heading of an
   `md` file, read with `errors="ignore"`; empty string when absent and for
   non-md entries. The heading regex is `spec_conformance._HEADING` — the
   same parser `spec-index` uses.
5. **Tag.** `tag` is the entry's scope: its containing directory (the entry
   itself for dirs) truncated to at most two segments — `docs`,
   `docs/roadmap`, `docs/research`, `specs`, `specs/00-universal`,
   `specs/40-features`, ...
6. **Deterministic and byte-stable.** Two runs over the same tree produce
   byte-identical output (rows and rendered tree): ordering comes only from
   sorted directory listings, never from filesystem iteration order or time.
7. **Read-only, rc 0.** `docs-tree` prints an indented text tree (or JSON
   with `--json`) and exits 0; it never writes. A missing `docs/` or `specs/`
   contributes no rows instead of failing.
8. **Registry-only surface.** The verb registers in `cli_registry.register()`;
   existing verbs' order and help text are unchanged and `harness.py` is not
   edited.

## Gherkin scenarios

```gherkin
Feature: docs-tree inventory

  Scenario: [dt-1] a nested tree yields rows with correct depth, title and tag
    Given a temp tree with docs/roadmap/plan.md, docs/notes.txt and specs/40-features/demo.md
    When collect() runs against it
    Then each row carries the expected depth, kind, first-heading title and scope tag

  Scenario: [dt-2] output is byte-stable across two runs
    Given the same temp tree
    When collect() and the rendered outputs run twice
    Then both runs are byte-identical

  Scenario: [dt-3] docs-tree exits 0 on this repo
    Given this repository
    When "python scripts/harness.py docs-tree" runs
    Then it prints a tree containing docs/ and specs/ rows and exits 0
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Reusar o parser de heading do gate em vez de um segundo regex | `scripts/harness_lib/spec_conformance.py` (`_HEADING`); `scripts/harness_lib/spec_index.py` (mesmo reuso) |
| Registro via `cli_registry.register()`, zero edits em `harness.py` | `scripts/harness_lib/cli_registry.py` docstring (receita MF.1-r2); doctor/spec-index/failure-patterns provaram o caminho |
| Read-only, exit 0 sempre — observar, não controlar | memória "observation must pay for itself"; espelha `doctor`/`spec-index` |
| Ordenação por nome via `sorted(iterdir)` — nunca ordem do filesystem | invariante 6 (byte-stability) |

## Test strategy

- Behaviors: temp tree → row fields (path/depth/kind/title/tag) for nested md,
  non-md and dir entries; double run → byte-identical rows and rendered text;
  live CLI run exits 0 printing both scopes.
- Edge cases: file without a `# ` heading → empty title (rule 4); non-md file
  → kind `other`, empty title; missing `docs/`/`specs/` → no rows (rule 7).
- NO fixed file-count asserts against the real repo — siblings add docs and
  specs concurrently.
- Regression net: `testing/scenarios/cli_registry.py` frozen top-level surface
  (order preserved, `docs-tree` appended before `workflow`) guards rule 8.
- Coverage: deterministic, stdlib-only, no LLM —
  `testing/scenarios/dt_docs_tree.py`.

## Validation

- `python testing/scenarios/dt_docs_tree.py` — dt-1/dt-2/dt-3 all green.
- `python testing/scenarios/cli_registry.py` — registry surface intact with the
  new verb.
- `python scripts/harness-test.py smoke` and `spec-pack --no-project-commands` —
  template conformance + static integrity.
