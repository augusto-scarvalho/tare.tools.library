# Capability panels — CAP.1 scoped inventory + `agents skills`/`agents mcp`

Status: proposed 2026-07-13 (acceptance: testing/scenarios/cap_capabilities.py).

Intake (SPEC-116 door NEW): request = "painel de controle de skills/mcps:
instaladas, visualizador de prompt/código, papéis/workflows que usam;
POLÍTICA de separação harness vs repositório trabalhado"
(`docs/roadmap/screens-capabilities.md`). Covered-check: the only inventory is
`capabilities.json` (2 skills) + `agents audit` drift rows; nothing shows
scope/content/consumers in one place. Decision: **NEW**. SLICE: CAP.1 ONLY —
backend snapshots + CLI. CAP.2 (GUI grids/`/api/capabilities`), CAP.3
(target-repo discovery + undeclared badges), CAP.4 (introspect) and CAP.5
(enable/disable) stay OPEN in the backlog.

## Goal

One deterministic inventory of the capability surface, grouped by the three
policy scopes (harness / user / target/<name>), answering from the terminal:
what is installed, in which scope, with what parity status, who references
it, and what a skill actually contains — plus the MCP declaration map with an
empty state that teaches the grant paths before any server exists.

## Applicability

Applies to `scripts/harness_lib/capabilities_view.py` (`skills_snapshot`,
`mcp_snapshot`, `referenced_by`, `skill_file`, the two cmd handlers) and two
`agents` sub-parsers in `cli_registry.py` (zero `harness.py` edits). Statuses
come from `agent_parity._skill_status` — reused, never re-derived. Read-only
everywhere; no GUI change in this slice.

## Requirements / invariants (numbered, testable)

1. **Scoped ids, computed not physical.** Rows carry `harness:<name>` /
   `user:<name>` (target scope arrives with CAP.3); the prefix derives from
   which canonical file declares the item; no file moves.
2. **Discovery ≠ grant.** User-profile skills absent from the manifest render
   with status `undeclared` — visible, never loaded, never auto-granted.
3. **referencedBy is exact-form only.** Consumers are found by matching
   `/name`, `skills/<name>/`, `prompts/<name>.md` over agents/prompts/
   workflow-profiles — misses accepted over noise (roadmap risk #3).
4. **The viewer is a trust boundary.** `skill_file` resolves strictly inside
   the skill's own directory; a `..` escape and an unknown id both refuse
   legibly (exit 2 via HarnessError).
5. **MCP rows merge the five declaration points** (capabilities.json, codex
   config, agent-sync manifest, per-target target.json, svc-registry
   services.json `mcp` entries) with env reduced to key NAMES — a secret
   value never appears in any output mode. The empty state prints the grant
   paths.
6. **CLI parity + TE.5.** `agents skills [list|show]` and `agents mcp` exit
   0; under `HARNESS_AGENT_OUTPUT=compact` lists emit TSV.

## Gherkin scenarios

```gherkin
Feature: CAP.1 scoped capability inventory

  Scenario: [cap-1] the skills snapshot classifies scopes and consumers
    Given the live repo manifest and user profile
    When skills_snapshot runs
    Then research is harness-scope with parity statuses and exact-form
      references, ponytail is user-scope, and undeclared profile skills are
      visible with the undeclared status

  Scenario: [cap-2] the skill viewer refuses escapes
    Given the research skill
    When SKILL.md is read, a ../ escape is attempted and an unknown id is asked
    Then the content returns and both refusals are legible

  Scenario: [cap-3] MCP declarations merge with masked env
    Given fabricated declaration points across harness, target and services
    When mcp_snapshot runs on that root
    Then rows carry scope-prefixed ids and declaredIn, env appears as key
      names only and the secret value appears nowhere

  Scenario: [cap-4] the CLI is live in both output modes
    Given this repository
    When agents skills and agents mcp run (plus compact mode)
    Then both exit 0, the empty MCP state teaches the grant paths and compact
      emits TSV
```

## CAP.2 — GUI capability panels (amendment 2026-07-14)

CAP.2 lifts the CAP.1 inventory into the panel with ZERO new backend logic: two
read-only card grids in the existing Config view, fed by one cached
`GET /api/capabilities` (the `capabilities_view` skills + MCP snapshots in one
payload, mtime-cached on the manifest like `/api/metrics`). Read-only only —
introspect (CAP.4) and enable/disable (CAP.5) stay OPEN; NO `/api/action` entry
is added.

Requirements (numbered, testable — extend CAP.1's list):

7. **One cached read-only feed.** `GET /api/capabilities` returns
   `{skills, mcp}` from `capabilities_view` verbatim, token-gated, cached by the
   manifest mtime, degrading to empty lists (never a 500). No mutation route is
   added in this slice.
8. **Two scope-grouped grids in the Config view.** Skills group by scope
   (harness / target/<name> / user) with parity statuses + `referencedBy` chips;
   MCP groups by scope with env shown as key NAMES only, and renders a grant-path
   empty-state table when zero servers are declared. No new nav entry — the grids
   live in the existing Config view.
9. **The file viewer is a closed-set trust boundary.** `GET
   /api/capabilities/file?id=<skill-id>` serves ONE skill's SKILL.md/script
   through `capabilities_view.skill_file`, closed to the snapshot inventory and
   path-confined (unknown id / `..` escape refuse via the error shape, never a
   500). MCP has NO file route: its already-masked row renders client-side, so a
   declaration file's secret VALUES are never read.

## CAP.2 Gherkin scenarios

```gherkin
Feature: CAP.2 read-only capability panels GUI

  Scenario: [cap2-1] the cached feed serves the grouped inventory
    Given the live repo manifest
    When capabilities_snapshot runs
    Then it carries skills grouped by scope and the mcp list, reusing the CAP.1
      snapshots, and a repeat call hits the manifest-mtime cache

  Scenario: [cap2-2] the grids and routes are wired into the panel
    Given the built harness_ui.PAGE and harness_ui.py source
    When the Config view is inspected
    Then the skills and mcp grids are present with /api/capabilities and the
      closed-set /api/capabilities/file viewer, and no /api/action entry is added

  Scenario: [cap2-3] the file viewer refuses an out-of-inventory path
    Given the capability file route
    When an unknown skill id and a path escape are requested
    Then both refuse with the error shape and no file outside a declared skill
      directory is ever read
```

## CAP.3 — target capability discovery + undeclared badges (amendment 2026-07-14)

CAP.3 extends the CAP.1/CAP.2 inventory to DISCOVER a registered target's OWN
capability tree — its `.claude/skills/` and its `.mcp.json` servers — and mark
any item absent from that target's separation policy (`target.json`) with an
`undeclared` advisory badge. READ-ONLY / ADVISORY: CAP.3 only SURFACES the gap.
It adds NO mutating action, NO enforcement/blocking, and NO `/api/action` entry —
the "policy" is documentation of the declared set; the badge does not disable,
gate, or deny anything. The discovery REUSES the CAP.1 skill discovery
(`agent_parity._claude_user_skills`) and the CAP.2 grids/snapshot verbatim;
nothing is re-implemented.

Requirements (numbered, testable — extend CAP.1/CAP.2's list):

10. **Target discovery is scope- and undeclared-tagged.** `skills_snapshot` /
    `mcp_snapshot` append rows for a governed target's own skills
    (`<target_root>/.claude/skills/`) and `.mcp.json` servers with
    `scope: "target/<name>"` and `undeclared: bool` — true when the item is NOT
    in that target's `target.json` (`skills` list / `mcp.servers`). A declared,
    present item is `undeclared: false`.
11. **The target tree is a trust boundary.** Reads are path-confined under the
    resolved `target_root` (the CAP.1 confinement); a target with NO capability
    tree degrades calmly to zero rows (never a crash). MCP env is masked to key
    NAMES only — a secret VALUE is never read or echoed (same rule as CAP.2);
    MCP keeps NO file route.
12. **The badge is advisory, not enforcing.** Target-scoped cards with
    `undeclared: true` render an `undeclared` badge in the CAP.2 grids and
    nothing else changes: no new endpoint, no dialog, no mutation. Discovery ≠
    grant ≠ enforcement.

## CAP.3 Gherkin scenarios

```gherkin
Feature: CAP.3 target capability discovery + undeclared badges

  Scenario: [cap3-1] a target's own skill and mcp server are discovered and tagged
    Given a registered target with an undeclared .claude/skills skill and an
      undeclared .mcp.json server
    When skills_snapshot and mcp_snapshot run on that harness root
    Then both carry scope target/<name> rows flagged undeclared, and the mcp
      server's env appears as key names only with the secret value nowhere

  Scenario: [cap3-2] a target with no capability tree degrades calmly
    Given a registered target with neither .claude/skills nor .mcp.json
    When the snapshots run
    Then no target-scoped rows are produced and nothing crashes

  Scenario: [cap3-3] the undeclared badge is wired into the grids, advisory only
    Given the built harness_ui.PAGE
    When the skills and mcp grid renderers are inspected
    Then an undeclared badge is rendered on undeclared cards and no /api/action
      entry was added
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Reuso do motor de paridade (statuses nunca re-derivados) | policy rule 6 (`screens-capabilities.md`); `agent_parity.audit/_skill_status` |
| Escopos computados por arquivo canônico declarante | policy rules 1/3; SPEC-113 manifest + SPEC-110 target.json |
| Discovery ≠ grant (undeclared visível, nunca carregado) | policy rule 2 |
| referencedBy por formas exatas de invocação | roadmap risk #3 (aceitar misses sobre ruído) |
| Viewer path-confined (trust boundary testado) | roadmap risk #2 |
| services.json como 5º ponto de declaração MCP | svc-registry P0 (`service-bootstrap.md` — entradas `mcp`) |
| GUI fica no CAP.2 | slice discipline; Config-section proposal (open decision #6) decide lá |

## Test strategy

- Behaviors: live snapshot scopes/statuses/refs (cap-1); viewer trust
  boundary both refusals (cap-2); fabricated 3-point MCP merge + secret
  absent from serialized output (cap-3); live CLI + TSV (cap-4).
- Edge cases: broken target.json skipped; empty manifest degrades to {};
  skill without scripts → hasScripts false.
- Regression net: `agents audit`/`pair` untouched (same group, new
  sub-parsers); `cli_registry.py` scenario (top-level surface unchanged —
  `agents` already existed).
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/cap_capabilities.py` + the module self-check.

## Validation

- `python testing/scenarios/cap_capabilities.py` — cap-1..cap-4 green.
- `python testing/scenarios/cap2_capability_panels_gui.py` — cap2-1..cap2-3
  green (snapshot grouping + manifest-mtime cache, panel/route wiring,
  closed-set viewer refusal).
- `python testing/scenarios/cap3_target_discovery.py` — cap3-1..cap3-3 green
  (target skill/.mcp.json discovery tagged scope+undeclared with masked env,
  calm degrade for a target-less tree, undeclared badge wired advisory-only).
- `python scripts/harness_lib/capabilities_view.py` — module self-check
  (includes the escape refusal).
- `python testing/scenarios/cli_registry.py` — CLI surface intact.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.
