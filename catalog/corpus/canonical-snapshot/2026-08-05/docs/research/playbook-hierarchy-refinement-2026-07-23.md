# Intake refinement — playbook hierarchy & role registry (door NEW)

## Request (verbatim)

> quero um sistema de controle, atualização, herança (pra não consumir
> instruções repetidas) dos playbooks. por exemplo, loop overseer é um classe
> de overseer, então lê loop playbook + overseer playbook, devemos ter outros
> cenários assim. Quero ter um tracking desses arquivos, herança de
> valores/atributos e referências/links. Talvez a gente precise já pensar
> nesses papéis e roles para os tipos de workflows que temos e já prepará-los
> e organizarmos isso. depois quero uma tela ds GUI que permita consulta e
> visão hierarquica dos papéis e rulebooks. veja se não dá pra deixar junto
> com a tela de gerenciamento de recursos por tipo de worker, era algo que
> tinha na GUI legado, mas precisa ser melhor elaborado aqui

## Covered-check (which door?)

| Query | Command | Outcome |
|---|---|---|
| records search | `harness.py records search playbook inheritance role` | no hit (only today's 6a0fc05 refactor commit) |
| doc-find | `harness.py doc-find playbook role hierarchy inheritance` | no covering spec; research-playbook.md top hit (concept only) |

Decision: **NEW**. Route (SPEC-144): `pre-defined-profile security`, risk flag
`security` (instruction control-plane) — escalation WITHHELD to the owner
decision inbox; implementation only through that decision.

## Goal

One registry declares role→playbook chains with inheritance (child reads
parent's playbooks + its own), tracked (hash/existence/links) and rendered
composably for spawns and for a GUI hierarchy view — repeated instructions
live in exactly one file.

## Scope

In scope:
- `playbook-registry.json`: roles as classes, `extends` (single-parent v1),
  ordered `playbooks[]` per role, cycle/missing detection.
- CLI: `harness.py playbook <role>` (`--list` file chain in read order /
  `--compose` concatenated), consumed by spawn prompts and vendor shims.
- Tracking gate check: registry paths exist; md cross-references resolve;
  no orphan playbook under `.harness/prompts/` absent from the registry.
- Role taxonomy for current workflow types (draft below) ratified by owner.
- GUI (second slice): hierarchy view inside Registry → Roles (RG4/RG5
  matrix+inspector), playbook chain in the role inspector. Gherkin required.
- De-dup pass: shared rituals move OUT of overseer-loop-playbook.md into
  overseer-playbook.md once composition exists (intake 363806c8c975).

Out of scope:
- Multiple inheritance / mixins; per-target playbook overlays (SPEC-110)
  — doors for v2.
- Rewriting playbook CONTENT beyond the de-dup moves.
- Autogenerating playbooks from specs.

## Actors & surfaces

- Actors: overseer sessions (any vendor), route/loop drivers, spawn recipes,
  GUI Registry screen, gate.
- Surfaces: CLI + internal (spawn prompt assembly) + GUI (Registry → Roles).
- UI surface? **yes → Gherkin required** in the resulting spec.

## Draft taxonomy (ratify/edit)

```
agent-base (AGENTS.md — contract, implicit root; Q3)
├─ overseer            overseer-playbook.md
│  ├─ loop-overseer    + overseer-loop-playbook.md      (AFK loop)
│  ├─ route-overseer   + feature-delivery briefs        (SPEC-144 tier-2)
│  ├─ room-overseer    + room-overseer.md               (GUI chat rooms)
│  └─ research         + research-playbook.md           (double diamond)
├─ router              router-playbook.md               (SPEC-144 tier-1)
└─ worker              subagent-contract.md
   ├─ implementer      + implementer-packet.md          (write packets)
   ├─ groom-miner      + backlog-groom-playbook.md §1   (report-only miner)
   └─ packet-analyst   (GLM/nvidia embedded-content lanes)
```

Model/effort pins stay SOLELY in `.harness/routing/model-routing.json`
(same role keys join the two registries — no value duplication).

## Proposed acceptance criteria

- [ ] `playbook <role> --list` prints the parent→child file chain; unknown
      role/cycle/missing file is a typed refusal.
- [ ] Registry gate check red on: dangling path, orphan playbook, broken md
      cross-reference.
- [ ] Spawn recipes (Agent-tool prompts, codex lane briefs, GUI room spawn)
      reference the chain instead of pasting duplicated discipline.
- [ ] Loop playbook contains ONLY loop mechanics after the de-dup pass; the
      composed loop-overseer output is a superset of today's guidance.
- [ ] GUI: Registry → Roles renders the hierarchy and the per-role playbook
      chain (hash + updated-at), honest "—" when unregistered; scenarios
      per Gherkin.

## Risks / blast radius

Control-plane surface (`.harness/prompts/`, protected registry) — route
already escalated `security`; every edit through the reviewed protected
flow. Spawn-prompt assembly touches all vendors: composition must be
additive-first (registry absent ⇒ today's behavior byte-identical). GUI
slice is additive on the existing Registry screen.

## Decisions (owner-ratified 2026-07-23, in-chat Q1-Q8)

- **Q1** registry home: `.harness/routing/playbook-registry.json` (joins
  model-routing by role key).
- **Q2** spawn consumption: `--list` — the spawn receives the ordered file
  chain and reads it; no concatenated injection.
- **Q3** (owner architecture, supersedes both drafted options): every VENDOR
  adapter file (CLAUDE.md, codex-side surface, etc.) becomes a GENERIC shim
  pointing at the central canonical `AGENTS.md`, which carries the true
  harness content — and that canonical file IS in the chain as `agent-base`,
  root of every role. Vendor shims stay thin so chain membership does not
  double-pay content.
- **Q4** de-dup of shared rituals: same wave as the registry.
- **Q5** GUI: inside Registry → Roles (hierarchy panel + playbook chain in
  the role inspector).
- **Q6** tracking v1: exists + hash + updated-at; gate check for dangling
  paths, orphan playbooks, broken md cross-references. No version headers.
- **Q7** taxonomy: draft ratified PLUS `ui-overseer` and `security-auditor`
  as overseer children on day 1 (their own playbooks may start near-empty;
  ui-overseer inherits D039/UI-brief doctrine, security-auditor inherits the
  escalation contract).
- **Q8** enforcement: **HARD** — a spawn declaring a role absent from the
  registry (or an unresolvable chain) is REFUSED from day 1. Delivery
  consequence: the registry must cover EVERY live spawn path (Agent-tool
  profiles, codex lanes, GLM packet workers, GUI rooms, route tiers) in the
  same wave, else legitimate spawns break — this becomes an acceptance
  criterion and a pre-flip inventory task in the plan.

Implementation remains gated on the `security` escalation in the owner
decision inbox (route 2026-07-23). Next artifact: spec from
`specs/SPEC_TEMPLATE.md` with Gherkin for the GUI surface.

## Open questions for the human (superseded by Decisions above)

- Q1 registry home: `.harness/routing/playbook-registry.json` (joins
  model-routing by role key; recommended) or `.harness/prompts/`?
- Q2 composition default for spawns: `--list` (agent reads files, cheaper
  cache reuse; recommended) or `--compose` single doc?
- Q3 does AGENTS.md participate as implicit root of every chain, or stay a
  contract outside the registry (recommended: outside, contract ≠ playbook)?
- Q4 de-dup timing: move shared rituals in the same wave as the registry
  (recommended) or a later wave?
- Q5 GUI placement: inside Registry → Roles matrix+inspector (recommended,
  legacy resource-mgmt heir) or a separate screen?
- Q6 tracking depth v1: exists+hash+updated-at (recommended) or version
  headers/changelog per playbook file?
- Q7 taxonomy above: ratify as-is? names to change? roles missing
  (security-auditor? ui-overseer as overseer child?)?
- Q8 enforcement: spawn paths REFUSE an unregistered role (hard) or warn
  (soft, v1 recommended)?
