# CLI tool catalog — the argparse tree, demand-paged (CE.4)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/cc_cli_catalog.py).

Intake (SPEC-116 door NEW): request = "argparse-tree-as-tool-catalog —
names+short-descs upfront, full `--help`/schema on demand (demand-paged);
introspection helper in `harness_lib`, not the harness.py monolith; measure
disclosure overhead" (CE round, gap G2). Covered-check: an agent choosing a
verb today either knows it already or pays for full `--help` dumps; nothing
serves the names+short-descs page. Decision: **NEW**.

## Goal

One `catalog` verb: bare, it prints one compact row per verb (top-level +
workflow subtree — the full verb surface; `catalog` reports the live count) — the page an agent reads to CHOOSE; with a verb
argument it pages in that ONE verb's complete `--help`. The win is measured,
not claimed: the compact page is ~15% of every full help upfront
(`catalogShare` in `--json`).

## Applicability

Applies to `scripts/harness_lib/cli_catalog.py` (`catalog`, `full_help`,
`measure`, `cmd_catalog`) and its registration in `cli_registry.py`. The
helper builds the REAL parser tree exactly as `main()` does (cli_registry +
cli_workflow_tree) — introspection only, no dispatch, no argv parsing, no
second source of truth for the surface. The catalog always lists itself.

## Requirements / invariants (numbered, testable)

1. **Full coverage from the real tree.** The catalog derives from the same
   registration calls `main()` uses; every frozen top-level verb and every
   workflow subverb appears exactly once (`workflow <name>` rows).
2. **Compact rows.** Each row = verb + the first sentence of its registered
   help, capped — the choose-page, never the detail.
3. **Demand-paged detail.** `full_help(verb)` returns argparse's complete
   help for one verb (top-level or `workflow <sub>`); unknown verbs refuse
   legibly (exit 2).
4. **The win is a number.** `measure()` reports catalogChars, fullHelpChars
   and their ratio; the catalog must be strictly smaller (CE net-cost-positive
   rule: the gain ships with its measurement).
5. **TE.5.** Under `HARNESS_AGENT_OUTPUT=compact` the page emits TSV.

## Gherkin scenarios

```gherkin
Feature: demand-paged CLI tool catalog (CE.4)

  Scenario: [cc-1] the catalog covers the whole real surface
    Given the parser tree built as main() builds it
    When catalog runs
    Then every frozen top-level verb, the workflow subtree and the catalog
      itself appear as compact rows

  Scenario: [cc-2] detail pages in one verb at a time
    Given a top-level verb and a workflow subverb
    When full_help runs for each and for a ghost verb
    Then both helps carry usage and flags and the ghost refuses legibly

  Scenario: [cc-3] the disclosure win is measured and the CLI serves it
    Given the live repo
    When measure and the CLI run bare, paged and compact
    Then the catalog is a strict fraction of all helps upfront and all three
      modes exit 0
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Introspecção da árvore REAL (zero segunda fonte da superfície) | `cli_registry` scenario idiom (constrói o parser igual ao main) |
| Nomes+descs curtas primeiro, detalhe sob demanda | CE round G2 (tool-disclosure-overhead); demand-paging thesis |
| Ganho medido no payload (`catalogShare` ~15%) | regra net-cost-positive do round CE |
| Helper em `harness_lib`, nunca no monólito | CE.4 wording; MF discipline |
| TSV sob compact | TE.5 (listas agent-facing tabulares) |
| Internal workflow commands excluded from counts | Commands hidden with `argparse.SUPPRESS` are internal workflow plumbing and intentionally excluded from surface counts (rec-cli-12) |

## Test strategy

- Behaviors: frozen-list coverage + workflow subtree + self-listing (cc-1);
  top-level and subverb paging + ghost refusal (cc-2); measured ratio + live
  CLI three modes (cc-3).
- Edge cases: verbs without help text render empty strings, never crash;
  multi-word verb argument joins (`catalog workflow plan`).
- Regression net: `cli_registry.py` frozen surface += catalog; the catalog
  derives from the registries, so any future verb is covered automatically.
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/cc_cli_catalog.py` + the module self-check.

## Validation

- `python testing/scenarios/cc_cli_catalog.py` — cc-1..cc-3 green.
- `python scripts/harness_lib/cli_catalog.py` — module self-check (prints the
  measured share).
- `python testing/scenarios/cli_registry.py` — CLI surface intact.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.
