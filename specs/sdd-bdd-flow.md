# SDD + BDD Flow — how requests become (or amend) specs

Status: SPEC-116, adopted 2026-07-11. Formalizes the previously implicit flow that
produced SPEC-111/114/115, and adds the BDD layer for UI-facing behavior.

## Goal

Every request follows one of exactly two doors, and every spec that results is
template-conformant, source-grounded, and — when it has a UI surface — carries
behavior scenarios (Gherkin) that verifiably map to executable checks. The spec
engine stops being convention-by-imitation and becomes a checked contract, in this
repo and in every project the harness governs.

## Applies to

The harness repo and all governed targets. Feature work (`specs/40-features/`),
amendments to existing specs, and the planning phase of any agent (human-driven
plan mode, operator REPL, or panel) that turns a request into documented work.
Legacy specs are exempt until amended (conformance applies to NEW and AMENDED
specs only; the legacy list is frozen in gate config).

## Invariants

1. **Two doors, no third.** A request is either NOT covered by existing docs
   (door NEW) or covered (door COVERED). Door NEW: structured intake refinement →
   spec from template → scenario/BDD → gate. Door COVERED: mandatory lookup
   (`records search` + `doc-find`) → recap of what exists → delta analysis →
   versioned amendment of the existing spec. Duplicated specs for covered ground
   are a defect.
2. **Intake precedes spec.** Door NEW starts from `specs/templates/intake-refinement.md`:
   goal, in/out of scope, actors, proposed acceptance criteria, risks, and the
   covered-check ("did we search records/doc-find?"). A spec whose intake was
   skipped is non-conformant.
3. **Template conformance.** New/amended 40-features specs carry the template's
   required sections: Goal, Applicability, numbered testable rules, Rationale &
   sources (decisão→fonte), Test strategy, Validation; ceilings and versioned
   amendment sections where applicable. The `spec-pack` gate enforces this
   deterministically.
4. **BDD for UI surfaces.** A spec whose rules touch a UI surface includes a
   ` ```gherkin ` block of declarative scenarios (business-readable, no
   keystroke-level steps). Grammar: `Scenario: [<check-id>] <title>` — the
   bracketed id MUST resolve to a named check in the scenario file the spec's
   Validation section references. The mapping is parsed and enforced by the gate:
   spec and test stay separate files, but they cannot drift silently.
5. **Scenarios are written at refinement time, with the human** — never generated
   post-hoc from the implementation (post-hoc scenarios reflect what was built,
   and LLM-generated ones reflect training distributions rather than domain edge
   cases; see sources).
6. **Amendments are versioned sections** (v2, v3, …) appended to the existing
   spec with their own rationale rows — the SPEC-114 v2→v5 pattern, now law. An
   amendment that rewrites history instead of appending is a defect.
7. **Every normative decision carries a source** in the decisão→fonte table —
   external literature, an in-repo incident, or a measured fact. "Seemed good"
   is not a source.

## Agent behavior

- Planning agents route every request through door NEW or door COVERED before
  proposing work; the door decision (and the lookup evidence for door COVERED)
  appears in the plan/spec.
- Implementer packets reference the spec's numbered rules; deviations are
  reported against rule numbers.
- UI implementers keep Gherkin ids and check names in sync — renaming a check
  without updating the spec (or vice versa) fails the gate, which is the point.
- Target-project agents inherit this flow via the packaged templates and this
  spec; target-specific intake artifacts live in the target's own specs tree.

## Validation evidence

- `spec-pack` gate: `feature-spec-conformance` (required sections on new/amended
  40-features specs) and the Gherkin `Scenario: [id]` → named-check resolution.
- Acceptance scenario exercises the checker: conformant synthetic spec passes;
  missing-section spec fails; orphan Gherkin id fails.
- Retrofit pilot: SPEC-114's panel flows carry Gherkin blocks whose ids resolve
  to real checks in `testing/scenarios/ui_e2e.py` / `m5_ui_panel.py`.

## Escalation triggers

- A request that fits neither door cleanly (e.g., covered by docs that contradict
  each other) → escalate with profile `docs`.
- Gherkin mapping failure on a spec the agent cannot amend (legacy/frozen) →
  escalate rather than editing the frozen list.
- Repeated intake skips detected in review → process finding (self-review
  friction), not a silent pass.

## Reference anchors

| Decisão | Fontes |
|---|---|
| Fluxo em fases com artefatos que alimentam a fase seguinte (intake → spec → scenario → gate) | [GitHub Spec Kit](https://github.com/github/spec-kit) (Specify→Plan→Tasks→Implement, 93k+ stars, v0.8.7 mai/2026); [AWS Kiro](https://builder.aws.com/content/31u60Xzm1ymjMpCi5kTmFutCyiN/hands-on-project-using-kiro-spec-driven-development) (requirements→design→tasks); análise comparativa [Martin Fowler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) |
| Porta COBERTO = emenda-delta versionada, nunca spec duplicado | [OpenSpec](https://github.com/speclib/awesome-openspec) (máquina de estados proposal→apply→archive; `specs/` = estado atual como fonte de verdade, `changes/` = deltas) — validação externa do nosso padrão v2→v5 do SPEC-114 |
| Nosso `00-universal/` como "constitution" imutável por mudança | Spec Kit constitution ([docs](https://github.github.com/spec-kit/)) — mesmo papel, já existia aqui |
| Governança spec-driven para desenvolvimento AI-augmented (o porquê acadêmico) | [The Productivity-Reliability Paradox: Specification-Driven Governance (arXiv:2605.01160)](https://arxiv.org/pdf/2605.01160) |
| Gherkin declarativo, cenários curtos (<10 passos), escritos em colaboração — não gerados pós-fato | Adzic, *Specification by Example* ([10 years later](https://gojko.net/2020/03/17/sbe-10-years.html)); [Gherkin best practices](https://github.com/andredesousa/gherkin-guidelines-for-ai); alerta Tier-2: cenários gerados por LLM refletem distribuição de treino, não edge cases do domínio ([SDD+DDD+BDD 2026](https://medium.com/@mail2mhossain/your-ai-coding-agent-is-not-the-problem-ec585a31787f)) |
| Spec e teste ligados verificavelmente (anti-drift), MAS em arquivos separados com mapeamento determinístico em vez de runner BDD novo | Ideal "spec = test file" da literatura adaptado ao nosso stdlib-first: pytest-bdd/behave rejeitados (dependência + segundo runner); o parser `Scenario: [id]` → check nomeado dá a rastreabilidade sem o custo — living documentation via gate ([Adzic: specs viram documentação quando testes as mantêm honestas](https://gojko.net/2020/03/17/sbe-10-years.html)) |
