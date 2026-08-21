# Intake refinement -- wiki-spec-guard (door NEW)

SPEC-116 invariant 2 checklist. Seeds SPEC-167
(`specs/40-features/wiki-spec-guard.md`). Backlog row `wiki-spec-guard`
(`docs/roadmap/docs-wiki.md` §4.6/§9) originally sketched as "SPEC-121", but
SPEC-121 is TAKEN by qa-evidence-capsule — this ships as the next free id,
**SPEC-167**.

## Request (verbatim)

> wiki-spec-guard | SPEC-121 + wiki-conformance + ref-resolution guard
> (`docs/roadmap/docs-wiki.md` §9, Phase 6): keep "sem referências quebradas pra
> trás" true forever — every wiki page summarizes+links, and every `SPEC-###`
> mention resolves to a real spec.

Precedent (roadmap §4.6): a deterministic `wiki-conformance` check beside
`feature-spec-conformance`, plus a broken-ref guard so `SPEC-###` textual refs
must resolve to a defined spec (whitelist the documented gaps).

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search wiki spec guard` | no hit -- no spec owns wiki conformance or the spec-ref guard |
| doc-find | `python scripts/harness.py doc-find wiki conformance spec ref guard` | hit on `docs/roadmap/docs-wiki.md` (the PLAN, Phase 6) only, no spec |

`docs/roadmap/docs-wiki.md` is a planning roadmap ("Status: planning only ...
Nothing here is implemented"), not a normative spec. `markdown-links` already
guards links repo-wide, but nothing pins the wiki summarize-and-link marker, the
80-line cap, or the `SPEC-###` resolution rule.

Decision: **NEW** -- the plan exists as a roadmap; no spec/check ties the wiki
content law to the machine. This spec pins the wiki-conformance + spec-ref-guard
rules a check regresses against.

## Goal

One sentence: tie the docs/wiki content law (summarize-and-link marker, resolving
relative links, defined-or-whitelisted `SPEC-###` refs, an 80-line cap) plus a
repo-wide `SPEC-###`-resolution guard to a deterministic `spec-pack` gate check,
so wiki honesty does not depend on an agent or PR reviewer remembering it.

## Scope

In scope:
- A new deterministic module `scripts/harness_lib/wiki_conformance.py`
  (`check_wiki(root)`): one `wiki-conformance:<relpath>` check per wiki page + one
  repo-wide `spec-ref-guard`.
- Wiring the checks into the `spec-pack` gate branch WITHOUT adding a line to
  `scripts/spec_test_gate.py` (gs-7 line ratchet at ceiling).
- A gate scenario (`testing/scenarios/wg_wiki_spec_guard.py`) enforcing the five
  invariants + a live 39/39 assert.

Out of scope:
- Editing `docs/wiki/**` content (the pages already pass day-one).
- Editing `spec_conformance.py`, `gate_checks_structure.py`,
  `gate_checks_content.py` (frozen surfaces) or the `gs_gate_structure` ratchet.
- The Wiki GUI screen / routes (owned by the `wiki-screen` backlog row).

## Actors & surfaces

- Actors: wiki authors (whose pages are checked), the `spec-pack` gate, the wg
  scenario.
- Surfaces (CLI / GUI / API / internal): internal (a gate check + a scenario).
  The guard GOVERNS the wiki corpus; the Panel Wiki view is a separate row.
- UI surface? the wiki is a rendered doc surface -> Gherkin included, mapping
  `[wg-1]`..`[wg-5]` to named checks.

## Proposed acceptance criteria

- [ ] wg-1: a good page (marker + resolving links + real spec-ref, <=80 lines) passes.
- [ ] wg-2: a page missing the summarize-and-link marker fails legibly.
- [ ] wg-3: a page with a broken relative link fails, naming the link.
- [ ] wg-4: a dead SPEC ref fails; a whitelisted ref (SPEC-105) does not offend.
- [ ] wg-5: an oversized (>80-line) page fails with the summarize-and-link detail.
- [ ] wg-live: the shipped docs/wiki (39/39) + the repo-wide spec-ref-guard pass today.
- [ ] The spec passes feature-spec-conformance in the same commit; no line added to
      `spec_test_gate.py`; `gs_gate_structure` + the frozen-surface modules stay green.

## Risks / blast radius

Low. Adds one stdlib module + one gate scenario + the SPEC-167 spec/intake, and a
minimal net-zero wiring touch. The check is read-only and deterministic (no LLM,
no network). Rollback = delete the two spec files, the module, the scenario, and
revert the one wiring edit. Calibration risk: the frozen whitelist {SPEC-105,
SPEC-122} tracks today's documented gaps; a new legitimately-unresolved ref turns
`spec-ref-guard` red until a reviewed whitelist line is added.

## Open questions for the human

- Wiring seam: the roadmap Phase 6 proposed adding the check inside
  `spec_conformance.py` and the ref-guard inside `spec_test_gate.py`, but the
  overseer override froze both and capped `spec_test_gate.py` at its gs-7 line
  ceiling. Confirm the chosen minimal wiring (see the implementation result's
  planDeviations).
