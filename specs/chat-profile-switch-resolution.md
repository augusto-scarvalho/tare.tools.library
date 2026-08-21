# Chat profile switch resolves its own overseer (`cm1`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/cm1_profile_switch.py).

Intake (SPEC-116 door NEW, corrective): recovered ask cm-1 from the chat-mined
spec archaeology — owner: *"acho que esse option não tá fazendo efeito quando
seleciono e salvo"*. Confirmed live: the panel selector applied the routing
profile and restarted the chat session (R38) as designed, but the SPEC-111
R9/R21 precedence (`flag > env > saved prefs > routing > card default`) let a
stale saved chat `model` pref (written once by the setup wizard) veto the
routing rung forever — `_resolve_config` only consults routing when no saved
model exists, so every restart resurrected the old model. Covered-check: the
R21 chain lives in legacy-frozen `repl-ux-onboarding.md`; the corrected
interaction is NEW contract, sliced here rather than exiting that freeze.

## Goal

Switching the active routing profile is the user's newest intent and must
win: `profile_use` demotes the saved chat `model`/`effort` prefs (engine,
target and postPlanMode survive) so the next session resolution falls through
to the new profile's overseer rung instead of a stale pref.

## Applicability

Applies to `model_routing.profile_use` (+ `_demote_chat_model_prefs`) — the
single seam behind CLI `routing profile use`, the panel `routing-profile-use`
action, and the onboarding selector. `chat_setup._resolve_config` precedence
itself is UNCHANGED: a model chosen explicitly after the switch still sticks.

## Requirements / invariants (numbered, testable)

1. **Demotion on switch.** `profile_use` nulls `model` and `effort` in
   `.harness/runtime/chat-prefs.json` when either is set, and reports it
   (`chatPrefsDemoted: true`).
2. **Survivors.** `engine`, `target`, `endpoint` and `postPlanMode` prefs are
   preserved verbatim by the demotion.
3. **Resolution lands on the profile.** After a switch to a non-canonical
   profile with an explicit overseer, `_resolve_config` resolves that
   overseer's card/effort with source `routing`.
4. **Calm paths.** Missing prefs file, corrupt prefs, or nothing-to-demote:
   the switch succeeds with `chatPrefsDemoted: false`; corrupt prefs never
   block a profile switch (R10 idiom).

## Gherkin scenarios

```gherkin
Feature: profile switch resolves its own overseer

  Scenario: [cm1-1] a stale model pref no longer vetoes the switch
    Given saved chat prefs carrying model and effort plus engine/target/postPlanMode
    When profile_use switches to another profile
    Then model and effort are demoted, the switch reports it, and the other
      prefs survive verbatim

  Scenario: [cm1-2] resolution lands on the new profile's overseer
    Given a non-canonical profile with an explicit overseer binding
    When the chat config resolves after the switch
    Then the overseer's card and effort win with source routing

  Scenario: [cm1-3] calm paths never block a switch
    Given a missing prefs file, then a corrupt one, then one with no model
    When profile_use runs in each state
    Then every switch succeeds and reports chatPrefsDemoted false
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Demover pref no switch, não inverter a precedência R21 | escolha explícita de modelo pós-switch deve continuar valendo; só a pref VELHA perde para a intenção mais NOVA |
| Fix no seam `profile_use` | cobre CLI + ação do painel + onboarding com um guard (ponytail root-cause) |
| Evidência do bug | chat-mined cm-1 (sessão f7f54eb1) + prefs vivas com `model: fable` + `chat_setup.py:124` guard |
| Não sair do freeze do repl-ux-onboarding.md | SPEC-116: fatia nova de contrato > retrofit de spec legada inteira |

## Test strategy

- Behaviors: demotion + survivors (cm1-1); routing rung breathes (cm1-2);
  calm degradation (cm1-3).
- Edge cases: corrupt JSON prefs; prefs file absent; canonical→canonical
  switch (no-op demotion).
- Regression net: mr_model_routing (routing machinery), m5_ui_panel
  (selector action allowlist), spec-pack.
- Coverage: deterministic, stdlib-only, temp roots —
  `testing/scenarios/cm1_profile_switch.py`.

## Validation

- `python testing/scenarios/cm1_profile_switch.py` — cm1-1..cm1-3 green.
- `python testing/scenarios/mr_model_routing.py` — routing regression net.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.
