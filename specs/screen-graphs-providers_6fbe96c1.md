# Graph providers — graphify becomes ONE provider (`graph-provider-abstraction`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/gp_graph_providers.py).

Intake (SPEC-116 door NEW): request = "DESACOPLAR isso e a nossa busca do
graphify, fazendo dele apenas UM PROVEDOR disponível"
(`docs/roadmap/screens-config-graphs.md` §B1). Covered-check: four call sites
invoke `graphify_code_ast.build_graphify_code_ast` directly; everything
downstream already consumes the ARTIFACT contract (`graphify-out/` shapes the
adapter normalizes) — the coupling is only at the builder call. Decision:
**NEW**. SLICE: B1 ONLY — `graphs-metrics-cli` (B2, now unblocked) and the
Grafos GUI screen (B3) stay OPEN.

## Goal

A provider registry where the stdlib AST builder is the DEFAULT of several
possible graph producers: selection via `knowledgeGraph.provider` (per-target
override in `target.json`), config-declared external commands as additional
providers, deterministic LOUD fallback to the built-in when an external
provider fails or emits an unusable graph — and the four production call
sites all build through the registry.

## Applicability

Applies to `scripts/harness_lib/graph_providers.py` (`registry`,
`active_name`, `build`, `set_provider`, `cmd_graph`), the rewired call sites
(`discovery.py` code batch, `gate_checks_policy.py` harness freshness,
`gate_generic.py` target freshness, `harness.py` graphify_shards autobuild)
and the `graph providers|set` CLI verb (cli_registry). The
`graph-build-code-ast` verb and the graphify gate fixture deliberately stay
on the BUILT-IN (they test/name that specific builder). The text/image API
chain is untouched.

## Requirements / invariants (numbered, testable)

1. **The artifact contract is the interface.** A provider must emit
   `graph.json` in a shape `graphify_adapter.normalize_graphify_graph`
   accepts (`normalizationStatus != "unsupported"`); optional artifacts
   degrade calmly downstream as they already do.
2. **Declared in tracked config only.** External providers exist only as
   `knowledgeGraph.providers.<name>.command` in reviewed config — no plugin
   loading, no entry points; a future GUI may only SELECT among registered
   names.
3. **Selection with per-target override.** `active_name` = target.json
   override > project.json `knowledgeGraph.provider` > built-in.
4. **Loud deterministic fallback.** A failing spawn, non-zero exit,
   unreadable or unsupported graph.json, or an unregistered selection falls
   back to the built-in and the stats carry `{provider, fellBackTo, reason}`
   — never silent.
5. **Mediated spawn + stamp.** External commands run through the processes
   mediation layer (bounded, hidden console — the raw-subprocess ratchet
   holds) with the output dir as the final argv element; every successful
   build stamps `stats.generatedAt` into graph.json (metrics groundwork).
6. **Validated selection write.** `graph set <name>` refuses unknown names
   (exit 2) and writes `knowledgeGraph.provider`; `graph providers` lists the
   registry with the active marker.

## Gherkin scenarios

```gherkin
Feature: graph provider registry (B1)

  Scenario: [gp-1] the built-in default builds and stamps
    Given a temp root selecting the built-in
    When build runs
    Then artifacts land with stats.generatedAt and a target override wins in
      active_name

  Scenario: [gp-2] a declared external provider produces the artifacts
    Given a config-declared command emitting a minimal nodes/edges graph.json
    When build runs
    Then the external provider's graph passes the adapter with no fallback

  Scenario: [gp-3] broken or unregistered providers fall back loudly
    Given a provider whose command cannot spawn and then a ghost selection
    When build runs for each
    Then both fall back to the built-in carrying fellBackTo and a reason and
      the artifacts still exist

  Scenario: [gp-4] the call sites are rewired and the CLI validates
    Given the four production sources and the live CLI
    Then all four build through the registry, the builtin verb stays a
      builtin alias, providers lists with the active marker and an unknown
      set exits 2
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Contrato de artefato = interface (4 call sites, nada downstream muda) | roadmap key insight (`screens-config-graphs.md:135-138`) |
| Externos só em config rastreada (execução arbitrária = trust boundary) | roadmap risk #1 |
| Fallback determinístico e BARULHENTO para o builtin | roadmap §B1 ("never silent"); deterministic-first |
| Spawn pela camada de mediação | raw-subprocess-ratchet (batch 23) — um provider externo não pode reabrir o buraco |
| `graph-build-code-ast` fica alias do builtin; fixture idem | roadmap §B1; a fixture testa ESTE builder |
| Chaves ficam sob `knowledgeGraph.*` (compat) | roadmap open decision, lado compat |

## Test strategy

- Behaviors: builtin build + stamp + override precedence (gp-1); real
  external provider end-to-end (gp-2); spawn-failure + ghost-selection loud
  fallbacks (gp-3); rewiring + alias + CLI validation (gp-4).
- Edge cases: provider entry without command = unavailable; unreadable
  graph.json → reason; stamp tolerant of a missing graph.json.
- Regression net: gates rebuild through the registry on every stale graph
  (spec-pack exercises it live); `gate_fixtures_graphify` keeps the builtin
  covered; `cli_registry` frozen surface += graph.
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/gp_graph_providers.py`.

## Validation

- `python testing/scenarios/gp_graph_providers.py` — gp-1..gp-4 green.
- `python testing/scenarios/gm_graph_metrics.py` — the v2 metrics scenarios
  (gm-1..gm-3) green.
- `python scripts/harness_lib/graph_providers.py` — module self-check.
- `python testing/scenarios/cli_registry.py` — CLI surface intact.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  freshness rebuilds route through the registry.

## Amendments

### v2 (2026-07-13) — graphs-metrics-cli (B2): the per-subject metrics snapshot

`graph metrics [--target N] [--json]` renders one deterministic snapshot per
subject: structure stats from `graph.json.stats` (files/edges/errors/
durationS/generatedAt), FRESHNESS via the new shared
`graph_providers.staleness` — the single rule now consumed by BOTH gate
freshness checks (harness `gate_checks_policy` and per-target
`gate_generic`), so the screen and the gates can never disagree — artifact
sizes/mtimes (missing reads as null), and consumption aggregates from the
enrichment/report artifacts (enriched-file count, in/out token totals,
last-discover status counts, provider gates). Pure reads; the B3 Grafos GUI
stays OPEN and will consume this exact payload.

```gherkin
Feature: per-subject graph metrics (B2)

  Scenario: [gm-1] freshness flips with the shared rule
    Given a freshly built graph and then a newer source file
    When metrics runs before and after
    Then it reports fresh then stale with the gate rule's reason

  Scenario: [gm-2] consumption aggregates and null artifacts degrade
    Given enrichment and discover-report artifacts beside the graph
    When metrics runs
    Then token totals, enriched counts and status counts aggregate and a
      missing artifact reads null

  Scenario: [gm-3] the gates share the rule and the CLI answers
    Given both gate sources and the live CLI
    Then both consume graph_providers.staleness and graph metrics exits 0
      in text and JSON
```

v2 scenarios resolve in `testing/scenarios/gm_graph_metrics.py`.
