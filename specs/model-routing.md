# SPEC-115 — Model-card management + role-based model routing with fallbacks

Status: implemented 2026-07-10 (SPEC-115; acceptance: `testing/scenarios/mr_model_routing.py`, plus `testing/scenarios/m5_ui_panel.py` for the panel and `testing/scenarios/ux_repl_onboarding.py` for the chat config chain).

Version: 1.1 — see Changelog.

## Goal

Let an operator (1) manage model cards (CRUD), (2) choose, per kind of work
(planning, implementation, file reading, and the `overseer` default the chat
REPL/GUI open with, …), a primary model card and an ordered fallback chain for
when the primary is unavailable or out of tokens, and (3) do all of it from the
CLI and from a dedicated, visual panel screen — raw JSON only as a hidden
advanced mode. Routing lives in named, per-repository profiles with a
recoverable canonical baseline.

## Applicability

Applies to how the harness selects a model/effort when it spawns a subagent
(`spawn_command`, `executor_profile_spawn`) and when it constructs the chat
engine (`chat_setup._resolve_config`, `chat_engines.build_engine`). It does not
change task classification, nor an agent's ability to change its own
model/reasoning (still forbidden by `AGENTS.md`) — the harness routes, the agent
obeys.

## Scope

In scope:

- model-card CRUD over `.harness/routing/model-cards.json` with a schema guard
  and a reference guard on removal (`scripts/harness_lib/model_routing.py`);
- a routing overlay `.harness/routing/model-routing.json` — named `profiles`, an
  `activeProfile`, `perTarget` bindings; `canonical` is a RESERVED profile name,
  never stored, always derived live from `task-profiles.json` spawn blocks;
- CLI `harness.py models …` and `harness.py routing …` (thin dispatch into the
  module);
- consumption at the three resolution points and the chat config chain;
- a dedicated panel Config view (`scripts/harness_ui.py`): model-card grid +
  routing matrix + hidden advanced JSON, all mutations routed through POST
  `/api/action` allowlisted subcommands (`scripts/harness_lib/ui_panel.py`).

Out of scope (ceilings, see below):

- per-card cost optimisation / auto-selection;
- routing for the cardless `openai` chat engine (kept on its vendor default).

## Decision → source

| Decision | Sources |
|---|---|
| Fallback chain per role (primary → fb1 → fb2), consulted at spawn and at chat-engine construction | Industry pattern: LiteLLM Router fallbacks and OpenRouter provider routing/fallbacks. Internally `executors.json.runtimeLimits` already classifies rate-limit/quota/auth (detect); the chain completes the loop (fall). |
| A new overlay (`model-routing.json`) instead of mutating `task-profiles.json` | `task-profiles.json` is consumed by classify/spawn/workflow and is canonical/versioned; an overlay preserves byte-compat and gives "restore canonical" for free (canonical = derived live from spawn blocks, never stored). |
| Roles = task-profile names (+ `overseer`) | Single source of role names; the user's request maps 1:1 (planning=plan, implementation=implementation, reading=scan). `overseer` (renamed from `chat`) is the harness's default engine/model — what the chat REPL and the GUI open with — shown FIRST in the matrix. |
| A single "default" = the `overseer` role, not a per-card star | Two defaults (a card star + a routing default) confused operators. The card `default` field survives only as a wizard-preselect fallback (no UI writes it); the visible "the harness opens with this" owner is the `overseer` primary, badged on the card it points to. |
| GUI CRUD via a role-edit `<dialog>`, enumerable fields as selectors | The read-only matrix had zero edit affordance at canonical (its only default); "só dá pra editar pelo JSON". The whole row now opens a modal chain editor; enumerable fields (card, effort, engine, model id, reasoning) are selectors per SPEC-111 R17, not free text. |
| KNOWN_MODELS catalog + `models catalog` | Cards need canonical codex/gpt entries (parity with claude fable/opus/sonnet/haiku) and the GUI dropdowns need a verified source. Sources: verdent.ai GPT-5-Codex model names; openai/codex#19319 (400K in-codex window); codex.danielvaughan.com (GPT-5.5 1M API context); developers.openai.com/api/docs/models/gpt-5-codex; live banner `model: gpt-5.5` (2026-07-10). `gpt-5-codex` excluded (EOL 2026-07-23). |
| Dedicated visual panel screen; raw JSON only in a hidden advanced mode (pre-filled with the expanded canonical resolution when empty) | Literal request; precedent OpenClaw Control UI (visual config); native `<dialog>` already adopted (SPEC-114). A generic empty template taught nothing, so the textarea seeds the real 9-role shape with real values. |
| Named profiles + per-target binding | Literal request; the targets registry (`scripts/harness_lib/targets.py`) already governs repositories. |

## Requirements / invariants

Numbered, testable normative rules:

1. **Card CRUD with schema guard.** `models add|set` validate reasoning levels
   against the known set and `defaultReasoning` against a card's reasoning list;
   `add` refuses a duplicate id within an engine.
2. **Reference guard on removal.** `models remove <id>` is refused when the card
   is referenced by a routing profile (any role's primary/fallback) or by the
   saved chat pref, unless `--force` is passed (which leaves those references
   dangling, reported in the result).
3. **Canonical is derived, never stored.** `canonical` is a reserved profile
   name resolved live from `task-profiles.json` spawn blocks. It cannot be
   saved, edited, or deleted; `routing restore-canonical` / `profile use
   canonical` returns to it. The roleless `overseer` has no task-profile, so its
   canonical primary is the R21 card-default chain (the executor's default card +
   its `defaultReasoning`); this is the single visible "default".
4. **Resolution precedence.** `resolve_role(root, role, executor, target)`
   resolves in the order perTarget > activeProfile > canonical. A non-canonical
   profile that does not define a role falls through to canonical.
5. **Byte-compat under canonical; CLI↔module consistency always.** When the
   effective profile is canonical (no `perTarget` match and `activeProfile ==
   canonical`), `spawn_command`, `executor_profile_spawn`, and the chat config
   chain produce byte-identical results to pre-SPEC-115 behavior. Under ANY
   active profile, the `spawn-command` CLI output matches the module's
   active-profile resolution (`route_spawn`), and the stderr fallback-chain
   annotation is present iff `fallback_annotation` reports a chain — the
   acceptance check asserts this consistency, never a machine-local active
   profile.

```gherkin
Scenario: [cli:spawn-command-canonical] spawn CLI matches the module's active-profile resolution
  Given the repository's routing overlay with WHATEVER profile is active (canonical or a fork)
  When `harness.py spawn-command --task <t> --executor claude` runs
  Then stdout carries `--model <m>` where <m> is the model `route_spawn` resolves for the classified task profile
  And a `fallback chain` line appears on stderr iff `fallback_annotation` reports a chain for that role
```
6. **Chat config rung.** `chat_setup._resolve_config` inserts a `routing` rung
   between saved prefs and the model-card default: flag > env > prefs > routing
   (active profile's `overseer` role) > card default > vendor default. The rung
   fires only for a non-canonical profile that explicitly sets `overseer`; under
   canonical it is inert (`source == "canonical"`) and the card-default rung wins,
   preserving the byte-compat resolution and its `card default` source label.
7. **Cheap construction failover.** `chat_engines.build_engine` walks the
   `overseer` role's fallback chain on a CONSTRUCTION failure (binary/key
   missing), emitting one notice per hop, and raises only when the chain is
   exhausted. Mid-turn behavior is untouched.
8. **CLI read-only allowlist.** `models list`, `models catalog`, `models show`,
   and `routing show` are read-only (`READ_ONLY_PREFIXES` in `chat_engines.py`);
   the chat operator and the panel read them without a confirm. Every other
   `models`/`routing` subcommand classifies as `confirm`, and any
   `--approval-token`/`--send` argument classifies `human-only`.
9. **Single GUI write path.** Every mutating panel action is an allowlisted
   `models-*` / `routing-*` entry in `ui_panel.ACTIONS` that builds argv for the
   existing subcommands, requires a deliberate browser confirm, and inherits the
   structural human-only backstop — the same invariant as SPEC-114.
10. **Advanced JSON apply.** The panel's hidden advanced mode edits the raw
    `model-cards.json` / `model-routing.json` and applies through `models
    replace --json` / `routing replace --json`, which schema-guard the payload
    (unknown card references are rejected) before writing. When the routing
    registry has no profiles, the routing textarea is pre-filled with a MEANINGFUL
    template — the full effective canonical resolution expanded into all 9 roles'
    primary + fallbacks arrays under an `exemplo` profile — not a generic stub.
11. **`overseer` is the single default.** The routing role formerly named `chat`
    is `overseer`: the harness's default engine/model. Legacy `chat` role keys are
    migrated transparently on load. It is shown FIRST in the matrix with the
    description "modelo padrão do harness (chat/GUI)". The model-card grid shows no
    per-engine default star; instead the card the `overseer` primary resolves to
    carries an `overseer` badge. No UI writes a card `default` field.
12. **GUI role CRUD via modal, with a canonical fork.** Each matrix row is a
    read-only summary of the resolved chain and the WHOLE ROW opens a role-edit
    `<dialog>` (title = role + risk + description; ordered chain with entry 0 =
    `primário`, rest = `fallback n`; per-entry card `<select>` grouped by engine
    via `<optgroup>` + effort `<select>` constrained to the card's ladder; ↑ ↓ ×
    and `+ adicionar modelo`). Saving under canonical (read-only) orchestrates
    three allowlisted actions — `routing profile save <name>` (seeded from
    canonical, name pre-filled `personalizado`) → `routing set-role` → `routing
    profile use <name>` — behind one save gesture + confirm; no composite
    subcommand is added.
13. **Enumerable card fields are selectors (SPEC-111 R17).** The card form uses an
    engine `<select>`; a model-id `<select>` fed by `KNOWN_MODELS` for the chosen
    engine plus a `custom…` free-text escape; picking a catalog id auto-fills
    name/provider/reasoning and a contextWindow placeholder (all still editable);
    reasoning is a pill multi-select over the fixed ladder low/medium/high/xhigh/
    max; `defaultReasoning` is a `<select>` constrained to the chosen reasoning
    set; contextWindow is `<input type="number" min="1">` with the catalog
    placeholder and a source/note tooltip. Client-side validation mirrors the
    server's (id + engine required, defaultReasoning ∈ reasoning).
14. **KNOWN_MODELS catalog + parity.** `model_routing.KNOWN_MODELS` is the verified
    vendor catalog (claude: fable/opus/sonnet/haiku; codex: gpt-5.5 default /
    gpt-5.4 / gpt-5.4-mini / gpt-5.3-codex / gpt-5.2-codex; `gpt-5-codex` excluded,
    EOL). `models catalog` (read-only) prints it for CLI parity with the GUI
    dropdowns, and `/api/routing` carries it as `catalog`. contextWindow is set
    only where sourced (fable 1M observed; gpt-5.5 400K in-codex, 1M via API); the
    codex reasoning ladder is low/medium/high/xhigh.
15. **Mid-workflow failover.** An async worker that lands `blocked` with
    `error == "rate_limit_or_runtime_limit"` (the existing `rateLimitDetected` +
    `stopOnRateLimit` seam — no new detection) re-spawns on the next entry of its
    role's fallback chain instead of finalizing. `async_state.workflow_next_failover`
    (pure) resolves the chain against the workflow's ORIGIN executor so the order is
    stable across hops, and returns the next `{executor, card, effort}` not already
    in the worker's `failoverHistory`, or None. Normative sub-rules:
    (a) **Trigger only.** No trigger other than that one blocked classification;
    a worker blocked for any other reason finalizes as before.
    (b) **Bounded.** At most one re-spawn per chain entry — `failoverHistory`
    advances the walk, so a worker runs at most `1 + len(fallbacks)` times.
    (c) **Canonical-inert.** Under the canonical profile the chain has no
    fallbacks, so the next entry is None and the worker finalizes `blocked` exactly
    as pre-SPEC-115 (byte-identical task/worker/run records; no `worker_failover`
    event, no `failoverHistory` key).
    (d) **Circuit interaction.** The failed executor still records a circuit
    failure; an entry whose executor circuit is open is skipped to the following
    entry (the assert-usable check applied non-fatally per candidate).
    (e) **Evidence.** Each hop appends a `worker_failover {from, to, card, reason}`
    async event and extends the worker's `failoverHistory`, which is preserved on
    the final record whether the worker recovers (`done`) or the chain is exhausted
    (`blocked`), for the postmortem.
    Grounding (decision → source): `executors.json.runtimeLimits` already classifies
    rate-limit/quota/auth (detect); LiteLLM Router fallbacks + OpenRouter provider
    routing are the fallback-chain precedent (fall).

## Ceilings (v1)

- **Cardless engines keep their vendor default.** The `openai` chat engine has
  no cards, so the routing/card rungs are inert for it (it resolves to whatever
  the endpoint serves).

## Validation

- `python scripts/harness_lib/model_routing.py` (module self-check);
- `python testing/scenarios/mr_model_routing.py` (18 checks; adds overseer
  canonical == card-default, `models catalog`, the role-modal/catalog/overseer-
  badge/fork-banner page assertions, and the canonical-fork orchestration);
- `python testing/scenarios/wf_failover.py` (6 checks; the pure
  `workflow_next_failover` decision plus end-to-end mid-workflow failover:
  chain `[fail, ok]` recovers a rate-limited worker to `done` with a
  `worker_failover` event + `failoverHistory` hop, and the canonical control
  stays `blocked`);
- `python testing/scenarios/m5_ui_panel.py` (panel intact, 29 checks);
- `python testing/scenarios/ux_repl_onboarding.py` (chat chain intact, 26 checks);
- gates `smoke`, `spec-pack`, `scenarios`.

## Relevant baselines

Inherits `specs/00-universal/` (secure engineering, configuration, testing/gates)
and the SPEC-114 panel invariant (GUI mutations are allowlisted subcommands with
human-in-the-loop). Model/reasoning policy in `AGENTS.md` is unchanged.

## Changelog

- **1.2 (2026-07-15, COVERED-door amendment — per-role contextDiet editor):** roles in a
  NAMED (non-canonical) profile may carry a `contextDiet` block (SPEC-118 v5/v6 owns the
  semantics and the vendor translation). Owner-editable surfaces: CLI `routing diet
  --profile <p> --role <r> [--keep <caps|off|''>] [--user-layer on|off] [--reinject on|off]
  [--clear]` via `model_routing.set_role_diet` (canonical refused; role must exist; unknown
  capabilities refused); `routing show` includes `contextDiet` per role; `set_role`
  preserves an existing diet on model edits and `profile save` carries diets. GUI: ✂ diet
  badge on the "Routing by role" matrix + a "Context diet" section in the role editor,
  firing the allowlisted mutating `routing-diet` action (canonical edits ride the existing
  fork flow). Acceptance: `mr:module:diet-roundtrip`, `m5:routing:diet-action`,
  `tail:readonly-trim` (SPEC-118 v6).
- **1.1 (2026-07-12, COVERED-door amendment):** `cli:spawn-command-canonical`
  reworded from "canonical active" to "CLI spawn matches the module's
  ACTIVE-profile resolution; chain annotation present iff a chain is active"
  (requirement 5 + Gherkin scenario). The check id is unchanged. Hermeticity:
  the acceptance check no longer assumes machine-local routing state (a
  committed non-canonical `activeProfile` like `fable-max` is legitimate).
- **1.0 (2026-07-10):** initial SPEC-115 implementation.
