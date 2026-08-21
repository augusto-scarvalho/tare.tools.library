# Security directive map — no prose-only directive merges silently

Status: proposed 2026-07-13 (acceptance: testing/scenarios/sdm_directive_map.py).

Intake (SPEC-116 door NEW): request = "directive→check conformance map (no
prose-only security directive merges silently)"
(`docs/roadmap/security-owasp-enforcement.md` Phase 3). Covered-check: the
adversarial audit's finding F2 — OWASP anchors are enforced as STRING PRESENCE
only; a directive that is not a deterministic check, a named trigger, or a
documented exemption does not hold, and nothing notices a new one. Decision:
**NEW**. The roadmap's open decision (annotate specs vs mapping-file-only) is
resolved as recommended: MAPPING-FILE-ONLY — the six universal specs are never
edited by this mechanism.

## Goal

Kill the silent-prose class structurally: every `## Invariants` bullet of the
six security universal specs carries an explicit, diff-reviewable enforcement
declaration in `testing/security-directive-map.json`
(`check:<gate-check>` / `trigger:<mechanism>` / `prose` = accepted UNENFORCED,
visible debt), and the enforcing gate check `security-directive-map` fails on
an unmapped, stale, or invalid entry — a new or edited directive forces an
enforcement decision in the same commit.

## Applicability

Applies to `scripts/harness_lib/security_directives.py` (`directives`,
`directive_id`, `evaluate`, `seed_entries`), the seeded tracked map
`testing/security-directive-map.json` (54 directives at seed time: 16 check /
3 trigger / 35 prose — the honest current posture), and one enforcing check in
`spec_test_gate.main()` beside the security block. The six specs under
`specs/00-universal/` are read, never written. Scope stays the six security
specs (the roadmap forbids generalizing yet).

## Requirements / invariants (numbered, testable)

1. **Directives = Invariants bullets.** The parser extracts `- ` bullets only
   under the `## Invariants` heading of the six named specs; other sections
   never count.
2. **Stable normalized ids.** `id = <stem>:<sha1(normalized text)[:8]>` —
   whitespace/case-insensitive, so cosmetic edits keep the id and substantive
   edits change it (forcing a mapping review, by design).
3. **Closed status vocabulary.** An entry's status must match
   `check:…`/`trigger:…`/`prose`; anything else is INVALID and fails the gate.
4. **Fail on unmapped, stale, and invalid.** The gate check names each
   problem and the fix (edit the map in the same commit as the directive
   change); a fully-mapped tree reports the byStatus counts — the prose debt
   stays visible on every run.
5. **Mapping-file-only.** The mechanism never writes or requires edits to the
   universal specs; `seed_entries` prints skeletons (status `prose`) for a
   human to upgrade — nothing auto-writes the map.

## Gherkin scenarios

```gherkin
Feature: directive-to-enforcement conformance map

  Scenario: [sdm-1] directives parse from Invariants bullets with stable ids
    Given a spec with Invariants bullets and an Agent-behavior section
    When the parser runs
    Then only the Invariants bullets count and ids are normalization-stable

  Scenario: [sdm-2] unmapped, stale and invalid entries all surface
    Given a map covering one of two directives plus a ghost and then an
      invalid status
    When evaluate runs
    Then the missing directive, the ghost id and the invalid status are named

  Scenario: [sdm-3] the live repo is fully mapped with visible prose debt
    Given this repository's six security specs and the seeded map
    When evaluate runs
    Then zero unmapped/stale/invalid and byStatus counts the prose class

  Scenario: [sdm-4] the gate enforces with a same-commit fix line
    Given the gate source
    Then the security-directive-map check consumes evaluate and names the fix
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Mapping-file-only (specs nunca editados) | roadmap open decision, resposta recomendada; specs universais são protected-adjacent |
| Id = hash normalizado do texto (edição substantiva força revisão) | mecanismo SPEC-116 Gherkin (ids estáveis → checks nomeados), aplicado a diretivas |
| `prose` é status válido e VISÍVEL, não um buraco | honest labeling (CQ round); o gate impede prose NOVA silenciosa, não reescreve história |
| Statuses seed revisados contra a tabela de enforcement do roadmap | `security-owasp-enforcement.md` DET/PARTIAL/REVIEW/PROSE audit + controles aterrissados (ratchet/routing/liveness/env-filter/isolation-audit) |
| Escopo = 6 specs de segurança apenas | roadmap Phase 3 ("do not generalize to all universal specs yet") |

## Test strategy

- Behaviors: parser scope + id stability (sdm-1); unmapped/stale/invalid on a
  fabricated root (sdm-2); live full coverage with visible prose counts
  (sdm-3); gate wiring + fix line (sdm-4).
- Edge cases: missing spec file skipped; corrupt map reads as {} (everything
  unmapped → fail-closed); bullets under other headings ignored.
- Regression net: the live spec-pack run exercises the enforcing check on
  every gate; the module self-check covers the primitives.
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/sdm_directive_map.py`.

## Validation

- `python testing/scenarios/sdm_directive_map.py` — sdm-1..sdm-4 green.
- `python scripts/harness_lib/security_directives.py` — module self-check.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  the enforcing check green on the seeded map.
