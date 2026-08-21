# SPEC-120 — Renderer-first flow composer (derived DAG + validate-only)

Status: SPEC-120, proposed 2026-07-12 (acceptance: testing/scenarios/m5_ui_panel.py).

## Goal

The supervision panel gains a "Compose" view that renders any workflow profile as a
READ-ONLY derived SVG DAG (source → one node per branch → reduce) and lets the user edit
the branch composition through structured forms. A "Compile" button validates the
browser-composed candidate via `workflow plan --validate-only` (N1, SPEC-119 v6 rules
28-30) and shows the verdict inline. The profile JSON stays the single source of truth;
the GUI writes nothing. This is the renderer-first MVP adjudicated in D007 — explicitly
NOT a draggable node canvas.

## Applicability

Applies to `scripts/harness_lib/ui_panel.py` (`composer_snapshot`, `_dag_for`,
`_normalize_profile`, `compile_candidate`), `scripts/harness_ui.py` (the
`GET /api/composer` and `POST /api/compile` routes), and `scripts/harness_ui_page.py`
(the Compose nav view: DAG render + branch forms + inline report). It reuses the N1
compile core (`harness.validate_workflow_plan`) and the closed vocabularies in
`.harness/workflows/workflow-profiles.json`, `.harness/routing/task-profiles.json`, and
`.harness/routing/executors.json`. N2 does NOT add an apply/materialize/start action (v2
adds a create-only `composer-create` action — never start; see Amendments), a draggable
canvas, persisted layout state, or per-branch object overrides for map-reduce profiles
(shards are derived at compile).

## Requirements / invariants (numbered, testable)

1. **GUI writes no state.** The composer edits live in browser memory only. `/api/compile`
   is read-shaped (it runs `validate_workflow_plan`, which materializes nothing), is NOT
   an entry in `ui_panel.ACTIONS`, and does not route through the mutating write path; the
   allowlisted mutating ACTIONS set is unchanged by this feature. No apply/start action is
   added to the panel in N2.
2. **Derived layout, no persisted state.** The DAG (nodes + edges) is computed from the
   profile / current form state at render, every time — no coordinates and no layout cache
   are stored anywhere. `_dag_for` (server) and `dagFor` (front-end) are pure derivations,
   so a text-edited profile still renders and the view cannot drift.
3. **Compiler is the trust boundary.** `/api/compile` rejects any profile not in the closed
   profile set, and any composed branch taskProfile not in the closed task-profile set,
   BEFORE compiling. The compile is an in-process call to `validate_workflow_plan`, so no
   subcommand argv is ever constructed from browser input; the N1 core re-enforces the
   closed vocabularies and secret-scans the candidate content.
4. **Compile = validate-only, writes nothing.** A compile returns the N1 report verbatim
   (valid, workers with per-worker prompt tokens, tokenAudit, errors, warnings) and creates
   no `active/WF-*` directory, token-audit file, digest, or event.
5. **Token-gated.** Every composer route is behind the per-session token check (`_authed`
   precedes routing in both `do_GET` and `do_POST`).
6. **Renderer-first, not a draggable canvas.** Branch composition is edited through
   structured forms (title, taskProfile dropdown from the closed vocab, workerRole); there
   is no node dragging and no stored positions. Editing a branch re-derives the DAG live.
7. **Closed-vocabulary read view.** `/api/composer` returns the closed vocabularies
   (profiles, executors, taskProfiles) and a normalized DAG view per profile; branch
   objects are resolved with the compiler's own `default_fork_branches` so the rendered
   view matches what would compile.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Renderer-first read-only SVG DAG + structured forms; litegraph.js rejected | `D007` (`.harness/context/DECISIONS.md`); round-2 K1 verdict (`docs/research/agent-gui-cli-features.md` Phase 4/5): graphs token-bounded ~12 nodes, Comfy fork archived |
| Derived layout, no persisted coordinates (a fully derived view cannot drift) | round-2 convergence "layout = derived, netlist model"; PLAN.md N2 binding condition |
| Compiler as trust boundary; validate against closed profile/executor/taskProfile vocabularies | K1 "compiler-as-trust-boundary = existing allowlist model"; N1 already raises on unknown taskProfile + secret-scans (SPEC-119 v6 rules 28-30) |
| Compile = `plan --validate-only` (writes nothing); apply is a separate gated action, out of N2 | K1 "`--validate-only` is the one unbuilt piece"; PLAN.md N2 "apply = separate gated action" |
| GUI writes no state; every mutating action stays an allowlisted subcommand | fixed design premise (`docs/research/agent-gui-cli-features.md` Phase 0); SPEC-114 single-write-path |
| Runtime inter-worker messaging rejected → plan-time seeded digest edges (rendered as seed edges) | K3 unanimous; F1 seeded digest already shipped |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: Renderer-first flow composer

  Scenario: [composer:renders-dag] a profile renders as a derived DAG
    Given the supervisor opens the Compose view
    When the composer reads the workflow profiles
    Then each profile shows a source → branch → reduce DAG built from the closed vocabularies

  Scenario: [composer:compile-validates] compiling a valid composition returns a verdict
    Given a known profile with its composed branches
    When the supervisor clicks Compile
    Then the inline report shows the plan is valid and no workflow directory was created

  Scenario: [composer:compile-rejects-unknown] an unknown profile is rejected at the boundary
    Given a profile name outside the closed profile set
    When the supervisor clicks Compile
    Then the report is an error, no subcommand runs, and no workflow directory is created

  Scenario: [composer:no-write-path] the composer writes no state
    Given the compile endpoint takes browser input
    When a composition is compiled
    Then the endpoint is not an allowlisted action and the mutating action set is unchanged

  Scenario: [composer:create-gated] create is refused unless a valid compile
    Given a composition with an unknown profile or a secret-shaped branch title
    When the supervisor confirms Create
    Then creation is refused before any workflow plan runs and no workflow directory is created

  Scenario: [composer:create-materializes] a valid composed plan creates but does not start
    Given a valid composed fork-join plan
    When the supervisor confirms Create
    Then a workflow directory is created whose branches are the composed objects and it is not started

  Scenario: [composer:create-needs-confirm] an unconfirmed create is refused
    Given a valid composition
    When Create is invoked without confirmation
    Then it is refused at the confirm gate and no workflow directory is created
```

## Ceilings (upgrade paths)

- **Editable node canvas deferred.** Structured forms now; reopen a draggable canvas only
  on the D007 trigger (real workflow graphs > ~12 nodes or measured N2 editing friction).
- **Per-branch object overrides for map-reduce deferred.** Fork-join branches compose as
  objects (title/taskProfile/workerRole) through the in-process call; map-reduce shards are
  derived from the split strategy at compile, so a map-reduce compile validates the named
  profile only. Add per-shard editing when a use case needs it.
- **Two `dagFor` implementations (Python + JS).** The Python `_dag_for` serves the endpoint
  contract; the JS `dagFor` re-derives on live edit without a round-trip (the no-drift
  proof). Collapse to one only if the two ever disagree in practice.
- **In-process compile, not a subprocess.** Chosen over building a `workflow plan …
  --validate-only` argv because it is both simpler and strictly safer (no argv to escape);
  the CLI `--branch` remaining string-only is therefore moot for N2. Revisit if the
  composer must ever compile against a governed target repo rather than this repo.

## Test strategy

- Behaviors to verify: `/api/composer` returns profiles + closed vocab + derived DAG
  nodes/edges; a valid composed profile compiles to `valid:true` with per-worker rows and
  no `active/WF-*` dir; an unknown profile (or taskProfile) is rejected before compiling
  with no dir; `/api/compile` is not an ACTIONS entry and the mutating ACTIONS set is
  unchanged; the PAGE carries `navCompose` + the SVG render functions; a live browser can
  open Compose, see the DAG, edit a branch (DAG re-derives), and Compile to a verdict.
- Edge cases: map-reduce profile (no editable branches; single derived `map` node);
  empty-title branch (a compile error, not a crash); seeded digest → seed edges.
- Regression risks: the N1 compile core is reused verbatim — `wv_validate_only.py` is the
  net; the mutating write path is asserted unchanged (`composer:no-write-path`).
- Coverage impact: enforced via `testing/scenarios/m5_ui_panel.py` (in-process) +
  `testing/scenarios/ui_e2e.py` (Playwright, auto-skip). Deterministic, no LLM.

## Validation

- `python testing/scenarios/m5_ui_panel.py` — the seven Gherkin ids resolve to named
  checks here: `composer:renders-dag`, `composer:compile-validates`,
  `composer:compile-rejects-unknown`, `composer:no-write-path`, and (v2)
  `composer:create-gated`, `composer:create-materializes`, `composer:create-needs-confirm`
  (all green).
- `python testing/scenarios/ui_e2e.py` — `e2e:composer` drives the live compile flow and
  `e2e:composer-create` drives the create flow (green compile → Create enables → confirm →
  a new WF id shows, scrubbed after); green-skips without chromium.
- `python testing/scenarios/wv_validate_only.py` — the N1 compile core the composer reuses
  stays green (regression net).
- `python scripts/harness-test.py spec-pack --no-project-commands` — template + Gherkin
  conformance for this spec.

## Amendments

### v2 (2026-07-12) — the deferred Create step (`composer-create`, TASK-004 N2b)

TASK-004 N2b (`tasks/gui-flow-composer/PLAN.md`). N2 shipped Compose as validate-only with no
way to act on a green compile (the owner's N2 gap). v2 adds the CREATE step — create-only, never
start. Numbered requirements continue the list.

8. **`composer-create` is create-only, gated by a valid compile.** A new `ui_panel.ACTIONS`
   entry `composer-create` (`mutating`, `composerCreate`) whose build lambda is
   `workflow plan --profile <p> --branch-json <json> [--task <t>]` — it materializes a WF dir +
   prompts (via SPEC-119 v7 `--branch-json`) and **never starts**: no `start`/`async`/`run` verb
   is in the argv (spawns no agent, burns no tokens). A `composerCreate` pre-check in `run_action`
   runs the SAME in-process compile the Compose screen uses (`compile_candidate` →
   `validate_workflow_plan`) BEFORE building any argv and REFUSES unless it is valid — so an
   unknown profile/taskProfile, a token-budget breach, or a secret-shaped value blocks creation
   before `workflow plan` ever runs (**you can only CREATE what would VALIDATE**; the same
   closed-vocab + secret-scan + budget trust boundary as Compile). Mutating → the browser confirm
   + the `classify_command` human-only backstop are inherited. `/api/compile` stays read-only and
   is still NOT an ACTIONS entry; the ONLY new write path is this single allowlisted subcommand.
   The front-end enables "Criar workflow" ONLY after a green compile (re-disabled on any edit) and
   confirms naming what runs; on success it shows the new WF id and a create-only hint. Checks:
   `composer:create-gated`, `composer:create-materializes`, `composer:create-needs-confirm`
   (`testing/scenarios/m5_ui_panel.py`) + `e2e:composer-create` (`ui_e2e.py`).

| Decisão | Fontes |
|---|---|
| Create-only (materializa), nunca start — start continua um passo separado | owner decision (TASK-004 N2b): create é não-destrutivo (escreve dir + prompts, zero agente/token); o operador inicia pela CLI/painel depois |
| Pre-check compile-must-be-valid é a guarda load-bearing: só cria o que validaria | N2b security: `composer-create` leva input composto no browser para uma materialização REAL; reusa o validador N1 in-process (fecha vocabulário + secret-scan + budget) antes de qualquer subprocess |
| Única superfície de escrita nova = a ACTION allowlisted; `/api/compile` continua read-only | premissa fixa (SPEC-114 single-write-path); Compile ainda não escreve nada, só o Create confirmado materializa |
| Honrar edições de branch → `--branch-json` materializa os OBJETOS compostos | owner decision: título/taskProfile/workerRole editados no form precisam materializar (SPEC-119 v7) |

### v3 (2026-07-12) — budget badges on the DAG nodes (round-2 portfolio E6)

Round-2 portfolio E6. The Compose DAG rendered plain even after a Compile, so the per-worker
token cost the N1 report already carries stayed buried in the report table. v3 surfaces it ON
the graph. Front-end only (`scripts/harness_ui_page.py`); no new route, no server change.
Numbered requirements continue the list.

9. **Budget badges render the compile report, never recompute.** After a successful Compile,
   `renderDag` stashes the N1 report (`cmState.lastReport`, set by `doCompile`) and draws each
   branch node's `estimatedPromptTokens` + `promptTokenBudgetStatus` as a node badge, mapping
   `report.workers[i]` to branch node `i` (branch order — the same order `harness.py plan`
   enumerates workers). The numbers are rendered VERBATIM from the report; the front-end never
   recomputes tokens (the round-2 condition). Badges appear ONLY after a compile and are CLEARED
   on any edit (branch title/taskProfile/workerRole, profile change, or task edit — the same
   `renderDag` → `invalidateCreate` lifecycle that re-disables Create), because the stashed report
   no longer matches the edited composition; a recompile draws fresh badges. A branch node with no
   matching worker (count mismatch, e.g. a map-reduce single `map` node) renders plain. Checks:
   `composer:budget-badges` (`testing/scenarios/m5_ui_panel.py`, PAGE-content) + `e2e:budget-badges`
   (`testing/scenarios/ui_e2e.py`, Playwright auto-skip).

```gherkin
Feature: Budget badges on the composer DAG

  Scenario: [composer:budget-badges] a compile badges the DAG nodes with the token audit
    Given a compiled composition whose report carries per-worker prompt tokens
    When the DAG renders after the compile
    Then each branch node shows its estimatedPromptTokens and budget status, and a branch edit clears the badges
```

| Decisão | Fontes |
|---|---|
| Badges renderizam o token-audit EXISTENTE do report N1, nunca recomputam no cliente | round-2 E6 condition; o report N1 já carrega `estimatedPromptTokens` + `promptTokenBudgetStatus` por worker (rule 4) — a GUI só desenha |
| `report.workers[i]` → branch node i (ordem de branch) | workers são enumerados em ordem de branch por `harness.py plan`; o DAG desenha os branch nodes na mesma ordem |
| Badges limpam em qualquer edição (mesmo ciclo do Create) | a composição editada não corresponde mais ao report stashed; segue o lifecycle de `invalidateCreate` já existente (rule 8 front-end) |
| Count mismatch → node plain (ex.: map-reduce, 1 map node vs N shards) | fork-join tem branch↔worker 1:1; map-reduce deriva shards no compile (Ceilings), sem mapeamento 1:1 — não inventar badges |

### v4 (2026-07-29) — the reducer ceiling joins the compile verdict (row wf-validate-only-reducer-ceiling)

`--validate-only` said `valid: true` while the on-disk token-audit later
failed the reducer prompt at 2089/2000 (measured 2026-07-27; two replans) —
the same check-covers-less-than-it-appears disease as the
`gate-surface-definition` class, one layer up. `_validate_token_verdict`
already ESTIMATED the reducer prompt (`reducer_prompt_text`, byte-parity
with the audit's on-disk read) but only fed it into the 32k TOTAL; the
per-reducer ceiling (`maxReducerPromptTokens`, same
`token_budget_limit` default 1500 the audit uses) was never consulted.

10. **Reducer ceiling at compile time.** The verdict's check table gains
    `reducerPrompt:max` (value = the estimated reducer prompt tokens, limit
    = `maxReducerPromptTokens`), the report carries
    `reducerPromptTokens`/`maxReducerPromptTokens`, and the compile-error
    breach message names the reducer numbers. Same fail->error /
    warn->warning wiring as the existing checks; `--override-budget` keeps
    its escape. Check: `validate:reducer-ceiling`
    (`testing/scenarios/wv_validate_only.py`) — a reducer-only breach fails
    the verdict in-process, and a tiny task passes the same check.
