# Intake refinement — door NEW checklist

## Request (verbatim)

> "Todas as 4 falhas são artefatos da lane do codex — zero falhas de cenário.
> RL, rt6 e pw todos passaram. O erro é meu: meu briefing autorizou escrita em
> .harness/runs/probe-gate-isolation/ sem exigir o contrato de limpeza que o
> playbook manda. Limpa"
>
> Aqui, porque confiar em prosa? Esse processo não poderia ser deterministico?

(Owner, 2026-07-28, then: "bora em seguida deixar aquele ritual deterministico".)

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search footprint scratch cleanup lane` | no hit for a cleanup/scratch contract |
| doc-find | intake-triage hook ran it on the prompt | "covered-doc candidates: none found (likely a NEW door)" |

Decision: **NEW**. `specs/40-features/overseer-review-toolkit.md` owns the review
checks; this adds a check to that surface, so the spec amendment lands there —
but the capability (a declared, enforced scratch lifecycle) is new.

## Goal

A lane's obligation to clean up after itself becomes a deterministic check that
fails at review time, instead of prose in a playbook that the overseer must
remember.

## Scope

In scope:
- A `## Scratch` declaration in the plan-brief format.
- `review --plan` gains: (a) a declared scratch path that STILL EXISTS after the
  lane is a failure; (b) granting write to a path under `.harness/runs/` WITHOUT
  a scratch declaration is a failure (closes the omission that happened).
- Brief-template documentation of the section.

Out of scope:
- Auto-sweeping scratch dirs (rejected by design: deleting a worker's output
  before the overseer reads it destroys evidence — the measurement file from the
  2026-07-28 lane was only recoverable because the artifacts still existed).
- Changing the gate's structural checks (they already catch the symptom, just
  6 minutes later and with misleading attribution).

## Actors & surfaces

- Actors: the overseer running the per-completion review ritual.
- Surfaces: CLI (`harness.py review --plan <brief>`), plan-brief format.
- UI surface? no → Gherkin optional.

## Proposed acceptance criteria

- [ ] A brief declaring a scratch path that no longer exists → the check passes.
- [ ] A brief declaring a scratch path that still exists → the check FAILS and
      names the path.
- [ ] A brief whose footprint grants a write path under `.harness/runs/` with no
      `## Scratch` section → the check FAILS naming the missing contract.
- [ ] A brief with neither scratch declaration nor `.harness/runs/` grant →
      unchanged behaviour (no new row, no false failure on the existing briefs).
- [ ] The existing footprint/blank-fraud/mojibake/gaming rows are untouched.

## Risks / blast radius

`review --plan` is the ritual every lane completion passes through; a false
failure there is friction on every integration. Mitigation: the check is inert
unless a brief opts in by declaring scratch or by granting `.harness/runs/`
writes. `review` remains advisory (always exits 0) — it reports, the overseer
judges, same as every other row. Touches `scripts/harness_lib/overseer_review.py`
+ `testing/scenarios/orv_overseer_toolkit.py`.

## Open questions for the human

- (resolved by the incident) Should cleanup be automatic instead of declared?
  No — see Out of scope: auto-deletion destroys evidence the overseer may still
  need to read.
