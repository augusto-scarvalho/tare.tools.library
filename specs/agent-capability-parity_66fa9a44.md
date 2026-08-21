# SPEC-113 — Agent capability parity

Status: Accepted (HT — audit + pair, read-only audit / render-from-canonical pair)

## Goal

Keep every supported agent CLI (Claude Code, OpenAI Codex, and future vendors)
at capability parity: the same hooks, MCP servers and skills, wired the same
way. One canonical manifest (`.harness/capabilities.json`) declares what the
harness expects; each vendor's surface is a rendered adapter, and drift between
them is detected and repairable instead of silently accumulating (the "ponytail
skill exists for Claude but nowhere for Codex" failure).

## Applicability

Applies to the harness's own vendor adapters: `.claude/settings.json`,
`.codex/hooks.json`, `.codex/config.toml`, `codex/prompts/*`, plus the
user-scope skills/plugins the harness relies on. It does not manage
`.claude/settings.local.json` (user-local) and does not manage a target
repository's own agent surfaces (SPEC-110 owns targets).

## Scope

In scope:
- A canonical manifest of hooks / MCP servers / skills, vendor-agnostic.
- `agents audit`: read-only comparison of each vendor surface against the
  manifest, incl. user-scope skills; reports `present` / `drifted` / `missing`
  / `unportable` gaps with a nearest-equivalent fix.
- `agents pair`: deterministic change plan that renders the vendor adapters
  back from the manifest; `--apply` executes it, idempotently, writing only
  inside the repo root.
- Gaps surface as self-review findings in the existing supervision funnel.

Out of scope:
- Auto-applying parity changes without a human (pair is human-invoked; the
  self-review finding proposes, never executes).
- Editing canonical/protected files (AGENTS.md, prompts, shims) — the manifest
  renders non-protected adapters only; protected targets are refused with a
  pointer to the sanctioned wrapper.
- Installing user-scope plugins/skills (unportable gaps are reported, not
  auto-installed).

## Requirements / invariants

1. **Single source of hook wiring.** The manifest is the only source of hook
   wiring; both `.claude/settings.json` and `.codex/hooks.json` are derived
   from it. Editing wiring means editing the manifest, then `pair --apply`.
2. **Audit is read-only, incl. user scope.** `audit` reads vendor files and the
   user's Claude plugin/skill directories and never writes anything.
3. **Pair never writes outside the repo root.** Every write path is asserted to
   resolve under root; an escaping path raises.
4. **Unportable gaps are always reported with a nearest equivalent.** A
   user-scope skill with no vendor equivalent (e.g. Codex lacks Claude's
   ponytail plugin) yields an `unportable` gap naming the closest fix — render a
   repo adapter from the readable SKILL.md, or a manual fix when unreadable.
   Never silent (SPEC-111 R23/R24: explicit degradation, never silence).
5. **Idempotent apply.** Running `pair --apply` twice produces an empty plan on
   the second run; the rendered adapters are byte-stable.
6. **No second funnel.** High-severity gaps enter the existing self-review /
   escalation funnel with criticality, not a parallel reporting path.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Manifesto canônico → adapters renderizados por vendor → drift check | Ruler (github.com/intellectronica/ruler); rulesync (github.com/dyoshikawa/rulesync); agentsync (github.com/dallay/agentsync); precedente interno targets_lib.sync_adapter |
| AGENTS.md como raiz cross-tool | padrão AGENTS.md (oss-ai-swe.org/ruler discovery order); HARNESS_ARCHITECTURE ".harness canônico, .claude/.codex adapters" |
| Matriz vendor→arquivos | precedente interno knownAgentInstructionFiles (protected-files.json) |
| Drift por hash/shape + baseline | precedente interno check_protected_instructions (gate_generic) |
| Gap não-portável sempre reportado com equivalente-mais-próximo | Ruler agent-specific sections; SPEC-111 R23/R24 (degradação explícita, nunca silêncio) |
| Findings no funil existente com criticidade | SPEC-109 self-review + R28 usage boost — sem segundo funil |

## Acceptance criteria

- [ ] `agents audit` reports the real Claude×Codex hook wiring drift and the
      absence of a Codex ponytail equivalent.
- [ ] `agents pair` (dry-run) prints a plan; `--apply` rewires `.codex/hooks.json`
      to the manifest and renders `codex/prompts/ponytail.md` from the readable
      user-scope SKILL.md.
- [ ] A second `agents pair --apply` yields an empty change plan.
- [ ] `agents audit` after pairing shows only legitimately-manual gaps remaining.
- [ ] A high-severity parity gap raises a `capability-parity-gap` self-review
      finding.

## Test strategy

- Behaviors to verify: seed-from-Claude adopt; drift/missing/unportable
  detection; idempotent render for both vendors; adapter generation from a
  readable SKILL.md; graceful degradation on missing/unreadable user dirs;
  out-of-root write refusal.
- Edge cases: no manifest (audit/summary skip cleanly); corrupt manifest
  (degrades to {}); protected pair target (refused, not written).
- Regression risks: harness.py CLI table growth; self-review collect_metrics
  reading the user home each run.
- Coverage impact: informational (stdlib-only; behavior covered by the module
  self-check and the `ap_agent_parity` scenario).

## Validation

- `python scripts/harness_lib/agent_parity.py` (module self-check).
- `python testing/scenarios/ap_agent_parity.py` (acceptance scenario).
- `python scripts/harness.py agents audit` / `agents pair [--apply]` on the repo.
- Gate: `smoke`, `spec-pack`, `scenarios`.

## Universal baseline impact

- `specs/00-universal/canonical-file-protection.md` — pair renders only
  non-protected adapters; protected targets route through the sanctioned
  wrapper, never a blind write.
- SPEC-109 (self-evolution loop) — parity gaps are one more diagnostic finding
  in the same funnel, human-gated.
- SPEC-110 (target governance) — same render-from-canonical + drift-baseline
  precedent applied to the harness's own vendor surfaces instead of a target.

## Escalation triggers

- A parity gap that requires editing a protected/canonical file → `review`.
- Installing or removing a user-scope plugin/skill → human decision (pair only
  reports these).
- Any manifest change that alters a security hook's wiring (deny_hitl_flags,
  protect_files, workflow_write_guard) → `security`.

## Agent-profile parity (aposta E — amendment, DECISIONS D009 + EXP-19)

Status: Accepted. Extends this spec from hook/MCP/skill parity to **agent
profiles**: the roster of spawnable roles (`implementer`, `reviewer`, `scanner`,
…) must be reachable on Codex the same way it is on Claude.

### Canon and render direction

- **Canon = `.claude/agents/*.md`** — the nine Claude frontmatter profiles. The
  Codex surfaces are RENDERED from them (same render-from-canonical invariant as
  the hook wiring); there is no second copy in `.harness/capabilities.json` (the
  manifest stays hooks/MCP/skills), so a profile edit can never drift a manifest
  duplicate. One shared derivation, `codex_agent_profile(profile)`, feeds both
  the toml render and the exec call-params leg — parity by construction.

- **Derivation** (`.claude/agents/*.md` → codex profile):
  - `name`: lowercased, `[^a-z0-9_]` → `_` (the naming law below);
  - `description`: passthrough;
  - `developer_instructions`: the markdown body verbatim, whitespace-normalized
    at line ends only (no reflow);
  - `model_reasoning_effort`: Claude `effort` passthrough with the single map
    `max → xhigh`; an absent effort omits the key;
  - `sandbox_mode`: `workspace-write` when the Claude `tools` list contains
    `Edit` or `Write`, else `read-only` (the same S3 derivation as
    `workflow_spawn_command_for_prompt`);
  - **no `model` key**: Claude tier names (opus/haiku/fable/sonnet) do not
    translate to Codex model ids — the executor route-tuple (C13) owns Codex
    model choice at spawn time. Recorded once in the audit as an `unportable`
    note, not per-profile.

### EXP-19 findings (the redesign that this section encodes)

1. **Naming law.** Codex agent names accept lowercase letters, digits, and
   underscores ONLY. A hyphen is rejected — the invisible blocker of EXP-19
   v1–v3. `cheap-editor` renders to `cheap_editor.toml`.
2. **`.toml` profiles do NOT load under `codex exec`.** They serve interactive /
   app-server Codex. On the `exec` surface parity therefore rides in CALL PARAMS:
   `codex_exec_call_params(root, name)` returns `{name,
   developer_instructions, model_reasoning_effort?, sandbox_mode}` from the same
   derivation as the toml (minus `description`). This is the translation a future
   native `exec` fork-join spawn will pass to `spawn_agent`; today's consumers
   are the audit and the acceptance scenario (no live spawn path is in scope).

### Audit / pair behaviour

- `agents audit` gains a `matrix.agents` section: per canonical profile
  `present` (rendered text == existing `.codex/agents/<name>.toml` bytes) /
  `drifted` (exists, differs) / `missing`. Tomls not derived from any canonical
  profile (today `reader_a/b/c.toml`, the EXP-19 smoke fixtures) are `extra` and
  are NEVER written or deleted. `missing`/`drifted` become medium-severity gaps
  in the existing self-review funnel; `extra` is info-only, never a finding.
- `agents pair` plans and (`--apply`) writes `.codex/agents/<name>.toml`,
  root-scoped; the render is byte-stable, so a second apply is an empty plan.

### Acceptance criteria (aposta E)

- [ ] `agents pair --apply` renders one `.codex/agents/<name>.toml` per Claude
      profile, each with a codex-legal (`^[a-z][a-z0-9_]*$`) name.
- [ ] A second `agents pair --apply` yields an empty agent plan.
- [ ] Mutating a rendered toml flips its audit status to `drifted`; restoring it
      returns `present`.
- [ ] A stray `.codex/agents/*.toml` with no canonical source is `extra` and is
      byte-identical after apply.
- [ ] `codex_exec_call_params` matches the rendered toml's name / effort /
      sandbox derivation.
- [ ] `Edit`/`Write` in a profile's tools ⇒ `workspace-write`; a read-only tool
      set ⇒ `read-only`.

```gherkin
Feature: Codex agent-profile parity rendered from .claude/agents/*.md

  Scenario: [ap:agents-rendered] pair --apply renders a codex-legal profile toml
    Given a .claude/agents/cheap-editor.md canonical profile
    When agents pair --apply runs on the repo root
    Then .codex/agents/cheap_editor.toml exists with a ^[a-z][a-z0-9_]*$ name

  Scenario: [ap:agents-idempotent] a second apply plans no agent toml writes
    Given the profile tomls were already rendered
    When agents pair --apply runs again
    Then the plan contains no .codex/agents/ rows

  Scenario: [ap:agents-sandbox-derivation] tools drive the sandbox mode
    Given one profile lists Edit/Write and one lists only read tools
    When the profiles are derived
    Then the first renders sandbox_mode workspace-write and the second read-only

  Scenario: [ap:exec-call-params] the exec bridge matches the toml derivation
    Given a rendered profile toml
    When codex_exec_call_params is read for the same name
    Then its name, effort and sandbox equal the toml's and it omits description

  Scenario: [ap:agents-drift] a hand-edited toml is reported drifted then present
    Given a rendered profile toml
    When it is mutated and audited, then restored and audited
    Then audit reports drifted and then present

  Scenario: [ap:agents-extra-untouched] a stray toml is extra and never rewritten
    Given a reader_x.toml with no canonical source
    When agents audit and pair --apply run
    Then it is reported extra and its bytes are unchanged
```

### Corrections (aposta E)

- The plan named the S3 sandbox helper `workflow_spawn_command_for_prompt`
  (`scripts/harness.py`), which derives the sandbox from the worker's
  `writeAllowed`; `route_tuple._sandbox` carries the same rule on the codex
  route-tuple leg. This module mirrors the RULE via the profile's `tools`
  ceiling (Edit/Write present → `workspace-write`) rather than calling either
  symbol — a plan-time proxy for the same S3 classification, not a new policy.
- The `.codex/agents/` directory and the acceptance spec file already existed
  (the tomls were `reader_a/b/c.toml` only); this amendment adds the nine
  rendered profile tomls beside them and leaves the readers byte-untouched.

## Capability support states (LQ7-C3 — amendment, DECISIONS D012; §8.4)

Status: Accepted. Extends this spec with a declared **support state** per
capability so the matrix says not just *is it wired* but *how well the vendor
supports it*. Formalizes the codex SubagentStop gate-wait note as structured
data instead of prose.

### The field

Each capability entry in `.harness/capabilities.json` MAY carry a
`supportState` (`native | emulated | degraded | unsupported`) with §8.4
semantics: `native` = direct; `emulated` = passes the same observable tests;
`degraded` = changes one guarantee, not implicitly selectable; `unsupported` =
out of the route set. **Additive / retro-compat: an absent field is treated as
`native`, and adding the field re-renders nothing** (it is read + report only,
never part of the hook-render path).

Per D012 (Q2) the field is per **capability × vendor** when legs diverge: it may
be a scalar (applies to every vendor) or a `{vendor: state}` dict. An optional
`degradationReason` (short) names the containment/matrix that covers the
degraded leg. Example — the `subagent-gate-wait` hook is `native` on claude and
`degraded` on codex: a harness-spawned `codex exec` worker is a top-level session
that fires Stop (not SubagentStop) and never runs the harness gate, and codex
hook deny is advisory only; containment rides native `--sandbox` (S3) + the
SPEC-148 `sandbox_spawn` OS lock.

### Reader and audit behaviour

- One helper `capability_support_state(caps, name, vendor=None)` in
  `agent_parity.py` resolves the state (default `native`); it is the single
  reader used by `audit` and available to C16b (accounting-semantics) and R5
  (3-lanes must know native-vs-emulated per vendor). `degraded → maturity
  self-assessment` coupling (Q3, App F-17/18) is a deliberate follow-up, not
  this item.
- `agents audit` gains `matrix.supportState` = `{capability: {vendor: state[,
  degradationReason]}}` for every declared hook/skill (native surfaces there).
- `parity_gate_findings` NEVER fails on `degraded` — it is an honest declaration,
  not a gap; it is reported, not red. An `unsupported` leg the manifest still
  wires for that vendor (a route depends on it) is the one reportable case: a
  medium `support-state` gap in the existing self-review funnel.

### Acceptance criteria (LQ7-C3)

- [ ] A capability with no `supportState` reports `native` in the audit.
- [ ] The codex `subagent-gate-wait` leg reports `degraded` with a
      `degradationReason` and produces NO gap finding.
- [ ] An `unsupported` leg the manifest still wires becomes a medium
      `support-state` gap; `degraded`/`native`/`emulated` never do.

```gherkin
Feature: Declared capability support states (native/emulated/degraded/unsupported)

  Scenario: [ap:support-state-default] a field-less capability defaults to native
    Given a capability with no supportState in .harness/capabilities.json
    When agents audit runs
    Then matrix.supportState reports it native for every vendor

  Scenario: [ap:support-state-degraded] the codex gate-wait reports degraded, not a gap
    Given the subagent-gate-wait hook declares codex supportState degraded
    When agents audit runs
    Then matrix.supportState shows codex degraded with a degradationReason
    And no support-state gap is raised for it
```

## Adapter conformance suite + accounting semantics (T-ADAPTERCONF / C16b — amendment, §8.4)

Status: Accepted. Extends this spec with the second half of §8.4 (Adapter and
protocol conformance): a **per-executor** conformance report, and a declared
per-executor **accounting-semantics** field. This section governs
`.harness/routing/executors.json` (the spawn-side vendor cards route_tuple.py
and workflow_spawn_command_for_prompt read) — a different registry from
`.harness/capabilities.json` above, which governs hooks/skills/agent
profiles.

### Applicable c-test subset

§8.4 defines fourteen conformance tests (c1–c14). This amendment ships the
subset that applies to our local/HTTP executors, pinned by the overseer plan
(`plan-t-adapterconf.md`):

- **c1** schema validation and unknown-field behavior;
- **c2** cancellation, timeout, retry, streaming, backpressure;
- **c4** argument normalization and side-effect declaration;
- **c5** permission narrowing and no-amplification of delegated authority;
- **c7** error taxonomy (rejection / failure / unknown effect);
- **c9** provider-usage reconciliation (tokens);
- **c10** reasoning-effort support and model-specific fallback.

c3 (identity/trace-context propagation), c6 (artifact integrity), c8
(deterministic replay), c11 (context-window/compaction semantics), c12
(base-version/ownership-epoch propagation), c13 (redaction/classification),
and c14 (vendor-extension isolation) are out of scope for this suite — they
describe protocol/runtime concerns this harness's local CLI/HTTP executors do
not yet expose a comparable surface for, not a gap in the applicable seven.

### `conformance_report` / `conformance_findings`

`agent_parity.conformance_report(executor, root) -> {test_id: 'pass'|'skip'|'fail'}`
is deterministic (static source/config inspection only — no live vendor call,
no token spend) and never a crash: an unknown or placeholder/non-runnable
executor card skips every test with one reason. `conformance_findings(root)`
returns the human-readable `(executor/test, status, detail)` companion rows
consumed by the self-review-shaped reporting path.

**Report semantics (never fails the gate):**
- `pass` — the mechanism the test checks for is present and verifiable in this
  checkout;
- `skip` — the test does not apply to this executor/adapter family (a
  placeholder card, or no comparable mechanism exists to check), always with a
  reason, never silent;
- `fail` — real signal that the mechanism is declared but absent or broken
  (e.g. c9 on `codex`/`openai-compat`: no per-worker usage reconciliation
  reaches the cost ledger today, even where the vendor's own API reports
  usage natively). A `fail` is informative, not a defect in the checker, and
  by design **never turns a gate red** — same honesty stance as C3
  `supportState`.

### `accountingSemantics` (C16b)

Each executor card in `.harness/routing/executors.json` MAY carry
`accountingSemantics` (`native | emulated | degraded | unknown`) declaring how
the **vendor** reports token usage — not whether the harness currently
reconciles it (that is c9's concern, and the two can legitimately disagree:
an executor can be `accountingSemantics: native` while its c9 result is
`fail`, meaning the vendor reports tokens natively but our adapter does not
yet read them). `native` = the endpoint returns usage in its own native
protocol; `emulated` = usage is translated through a compatibility shim from
a different native schema (may lose fidelity on some fields); `degraded` =
usage is present but a documented guarantee is reduced; `unknown` = no
verified reporting mechanism (a placeholder card, or a vendor mode whose
granularity is unverified, e.g. per-subagent totals under a fork-join
session).

**Default differs from `supportState` on purpose:** an executor with no
declared field defaults to `unknown`, not `native`. `supportState`'s
retro-compat default favors "assume it works" for already-wired capabilities;
`accountingSemantics` favors "assume it is NOT trustworthy for spend
tracking" until declared, because a future N-VENDORCREDIT (D017) consumer
must never silently trust an undeclared number. Additive: adding the field
re-renders nothing (read + report only, exactly like `supportState`).

### `agents audit` / gate integration

- `agents audit` gains `matrix.adapterConformance = {executor: {test_id:
  status}}` and `matrix.accountingSemantics = {executor: state}` for every
  executor declared in `executors.json`. Both are purely observational: unlike
  `supportState`'s "unsupported-wired" case, NEITHER section ever appends to
  `gaps` — a `fail` test result or an `unknown` accounting declaration is an
  honest report, never a gate-affecting finding.
- `parity_gate_findings` gains an `agent-parity:adapter-conformance` row:
  `pass` when no executor has a `fail` test, `skip` (never `fail`) with a
  short list of `executor/test` fails otherwise.

### Acceptance criteria (T-ADAPTERCONF / C16b)

- [ ] `conformance_report` returns exactly the seven applicable test ids for a
      runnable executor card, and an all-`skip` map for a placeholder/unknown
      executor.
- [ ] An executor with no declared `accountingSemantics` reports `unknown`
      (not `native`) via `executor_accounting_semantics`.
- [ ] `agents audit` exposes `matrix.adapterConformance` and
      `matrix.accountingSemantics`; neither ever contributes a `gaps` entry.
- [ ] `parity_gate_findings` reports adapter-conformance fails as `skip`
      (never `fail`) at the row level.
- [ ] c5 (permission narrowing / no-amplification) passes for every runnable
      executor family this repo declares today (claude-stream-json,
      codex-exec, openai-compat-http).

```gherkin
Feature: Per-executor §8.4 adapter conformance + C16b accounting semantics

  Scenario: [ap:conformance-report-shape] the report covers exactly the applicable c-tests
    Given a runnable executor card in .harness/routing/executors.json
    When conformance_report(executor, root) runs
    Then it returns exactly {c1, c2, c4, c5, c7, c9, c10} each mapped to pass, skip, or fail

  Scenario: [ap:accounting-unknown-not-a-gap] an unknown accountingSemantics is reported, not a gap
    Given an executor whose card declares no accountingSemantics field
    When agents audit runs
    Then matrix.accountingSemantics reports it "unknown"
    And no gaps entry is produced for it

  Scenario: [ap:conformance-c5-no-amplification] every declared executor family passes c5
    Given the claude, codex, and openai-compat executor cards
    When conformance_report runs for each
    Then each reports c5 (permission narrowing / no-amplification) as pass
```

## Kimi vendor leg (KIMI-V1 — amendment, 2026-07-28)

The kimi cli-agent adoption (compat-executor-routing v3) was "pure config" and
left kimi INVISIBLE to this spec's machinery: no manifest leg, no audit row,
every vendor loop hardcoded `("claude", "codex")`. This amendment records the
measured kimi capability surface and ships the minimal visibility leg; adapter
RENDERING is a named follow-up, not silently absent.

### Measured contract (kimi-code 0.29.2, probed live 2026-07-28)

- **Hooks exist and deny is REAL.** `[[hooks]]` entries (fields `event`,
  `matcher`, `command`, `timeout`) fire in `-p` non-interactive mode; exit 2
  BLOCKS the tool call (probe: `Write` denied, model fell back to `Bash`,
  denied again, file never created). Stronger than codex, whose hook deny is
  advisory (protect-files note). Other non-zero exits fail-open. Blockable
  events: `PreToolUse`, `UserPromptSubmit`, `Stop`; the rest observe-only.
- **Payload is claude-shaped.** snake_case JSON on stdin: `hook_event_name`,
  `session_id`, `cwd`, `tool_name`, `tool_input` — and tool NAMES match
  claude's (`Write`, `Bash`), so the repo's hook scripts parse it as-is.
- **Hook wiring is USER-scope only.** Hooks load from `~/.kimi-code/
  config.toml` exclusively; a project-scope `.kimi-code/config.toml` is NOT
  read (probed: hook did not fire; `kimi doctor` lists only user files).
  `KIMI_CODE_HOME` relocates the whole home INCLUDING the OAuth store, so it
  is not a per-repo wiring seam (rejected: credentials would ride along).
- **Skills and agents DO have project-scope discovery.** `.kimi-code/skills/
  <name>/SKILL.md` (YAML frontmatter + body) and `.kimi-code/agents/*.md`
  (frontmatter: `name`, `description`, `tools`, `disallowedTools`,
  `model_preference`; body = system prompt) — near-claude format, far closer
  than the codex toml derivation.

### What this amendment ships (visibility leg)

- Manifest: `vendorNotes.kimi` records the measured contract verbatim-adjacent;
  the four repo skills declare a kimi adapter path
  (`.kimi-code/skills/<name>/SKILL.md`).
- `audit`: the skills loop covers kimi; a missing kimi adapter is `unportable`
  whose nearest-equivalent names THIS amendment's follow-up (never `agents
  pair --apply`, which cannot render kimi yet). `matrix.vendorNotes` is
  surfaced verbatim. Hook loops are UNCHANGED for kimi — no events legs are
  declared, so no fabricated hook gaps.
- `parity_gate_findings`: one `agent-parity:kimi` row, `pass`/`skip` only
  (observe-only, same law as every parity row).
- `rs_research_skill`'s `rs:parity-no-regress` guard stays scoped to the
  RENDERABLE vendors (claude/codex): a kimi `unportable` row is the tracked
  KIMI-V1 follow-up and must not hard-fail the gate — the same advisory law
  the parity rows follow.

### Follow-ups (tracked, not shipped here)

1. **Skill/agent adapter rendering** — `pair` legs for `.kimi-code/skills/`
   and `.kimi-code/agents/` (frontmatter-preserving renderer; the codex
   `_adapter_content` header would corrupt SKILL.md frontmatter).
   **SHIPPED 2026-08-07 — see the KIMI-V1-FU amendment below.**
2. **Operator-owned hook wiring doc** — user-scope `[[hooks]]` with
   repo-relative script commands self-scope (script absent in a non-harness
   cwd → non-2 exit → fail-open allow), so one operator wiring covers every
   harness clone; needs its own doc + doctor-style advisory, never a pair
   render into operator config.
   **SHIPPED 2026-08-07 — `docs/KIMI_HOOK_WIRING.md` + the doctor
   `kimi-hooks-wired` advisory.**
3. **executors.json cross-link** — the kimi card's containment note should
   cite this amendment once hook wiring lands (today containment = harness
   sandbox_spawn OS lock + merge gate only).
   **SHIPPED 2026-08-07 — the card cites this amendment + the wiring doc.**

## KIMI-V1 follow-up shipment (KIMI-V1-FU — amendment, 2026-08-07)

Ships follow-ups 1–3 above; kimi becomes the third RENDERABLE vendor.

### Decisions

- **Skill render = canonical text fidelity (LF-normalized), frontmatter-
  preserving, NO header.** Kimi skills are near-claude (YAML frontmatter +
  body); a codex-style `_adapter_content` header would corrupt the
  frontmatter. The TRANSITIONAL compatibility source is the claude leg of the
  manifest (`vendors.claude` repo path for repo-scoped skills, the installed
  user-scope SKILL.md for user-scoped ones) — `.claude/*` is NOT the
  canonical IR; it is the interim source until the debt
  `canonical-ir-vendor-adapters` (canonical harness IR → vendor adapters)
  ships. Comparison law: both sides are LF-normalized before compare
  (`write_text` pins `\n`), so Windows/Linux checkouts compare equal —
  "canonical text fidelity", NOT byte-copy. Content drift is `drifted` and
  pair repairs it — stronger than the codex skill leg, which only renders
  absence.
- **Agent render = frontmatter (name/description/tools) + body, with NO
  model/effort.** Same law as the codex `_AGENT_UNPORTABLE`: model choice is
  the executor route-tuple's at spawn time; kimi's own `model_preference` is
  a primary/secondary binding, not a tier name, so mapping tiers into it
  would be fiction. Names pass through unchanged — kimi accepts hyphens, the
  codex underscore law does not apply. **Optional kimi fields pass through
  verbatim (KIMI-V1-FU hardening, 2026-08-07):** `whenToUse`, `override`,
  `model_preference`, `disallowedTools`, `subagents` are preserved from the
  source profile when present (`profile["kimi_optional"]`), so the adapter
  collector does not assume `{name, description, tools, body}` is the whole
  schema; `model`/`effort` are still NEVER translated.
- **Kimi hooks are NEVER pair-rendered** (unchanged law): they load from
  `~/.kimi-code/config.toml` only. The wiring is operator-owned, documented
  in `docs/KIMI_HOOK_WIRING.md` (self-scoping repo-relative commands), and
  surfaced by the doctor `kimi-hooks-wired` advisory (machine-local, never
  fails).
- **Decl-gating extends to agents via opt-in.** A manifest that never opted
  into kimi (no `vendorNotes.kimi`, no `vendors.kimi` skill decl) grows NO
  kimi gaps and no `kimiAgents` matrix section — the KIMI-V1 no-fabricated-
  gaps law preserved.
- **Hook enforcement evidence is scoped, not general.** The one REAL deny
  proven on kimi is: kimi-code 0.29.2, 2026-08-07, PreToolUse→Write→
  `protect_files`→exit-2 (live probe, AGENTS.md byte-identical after).
  Several kimi hook events are observation-only and hook failure/timeout is
  fail-open — hooks are NOT the single security boundary (sandbox_spawn OS
  lock + merge gate remain the containment floor).
- **Readiness is tri-eixo (doctor `kimi-readiness`, 2026-08-07):**
  execution-ready (binary + `--version`), parity-clean (audit sem kimi gaps),
  governance-ready (hooks wirados). A kimi sem hooks segue utilizável para
  execução normal mas NÃO é equivalente para tarefas protegidas.
- **KIMI-V1 is a measured baseline, not an immutable contract.** Capability
  probing distinguishes installed-binary capability vs enabled feature flag
  (e.g. `KIMI_CODE_EXPERIMENTAL_SECONDARY_MODEL`) vs session tool-schema
  exposure; the audit reports what THIS install measured.

### What changes vs the KIMI-V1 visibility leg

- An absent declared kimi skill adapter is now `missing` (was `unportable`)
  whose fix names `agents pair --apply`; `unportable` survives only for the
  honest case of an unreadable canonical source. The KIMI-V1 acceptance
  criterion "audit reports each declared-but-absent kimi skill adapter as
  `unportable`..." is SUPERSEDED by this paragraph (the other three KIMI-V1
  criteria still hold).
- `rs:parity-no-regress` (rs_research_skill) now holds hard for the kimi leg
  too — the kimi exclusion is dropped.
- `parity_gate_findings`' `agent-parity:kimi` row stays observe-only
  (pass/skip, never fail) — unchanged law.

### Acceptance criteria (KIMI-V1-FU)

- [x] `agents pair --apply` renders `.kimi-code/skills/<name>/SKILL.md` with
      canonical text fidelity (LF-normalized) to the source skill (no header)
      and `.kimi-code/agents/<name>.md` with frontmatter
      name/description/tools + body and NO model/effort keys; hyphenated
      names are preserved. Optional kimi fields (whenToUse/override/
      model_preference/disallowedTools/subagents) pass through verbatim.
- [x] A second `pair --apply` is a no-op (idempotent); a hand-edited adapter
      audits `drifted` and is repaired by pair.
- [x] `audit` reports kimi skill adapters present/drifted/missing and a
      `kimiAgents` matrix section; a repo with no kimi opt-in grows no kimi
      gaps.
- [x] `docs/KIMI_HOOK_WIRING.md` exists; doctor `kimi-hooks-wired` warns with
      a pointer to it when the user config wires no harness hooks.
- [x] `parity_gate_findings` keeps `agent-parity:kimi` observe-only
      (pass/skip, never fail).
- [x] Doctor `kimi-readiness` reports the tri-eixo (execution/parity/
      governance) and the secondary-model feature-flag state (2026-08-07).
- [x] The hook acceptance matrix in `docs/KIMI_HOOK_WIRING.md` covers every
      installed hook with event/matcher/script/payload/probe-result
      (2026-08-07 hardening).

```gherkin
Feature: Kimi rendering leg (KIMI-V1-FU)

  Scenario: [ap:kimi-no-decl-no-gaps] no kimi opt-in, no kimi noise
    Given a manifest with no vendorNotes.kimi and no vendors.kimi skill decl
    When agents audit runs
    Then there are no kimi gaps and no kimiAgents matrix section

  Scenario: [ap:kimi-skill-rendered] pair byte-copies the canonical skill
    Given a declared kimi skill adapter path that is absent
    And a readable canonical skill source
    When agents pair --apply runs
    Then .kimi-code/skills/<name>/SKILL.md is a byte-copy of the canonical skill (no header)

  Scenario: [ap:kimi-agents-rendered] pair renders agent markdown without model pins
    Given a canonical .claude/agents/cheap-editor.md with model/effort frontmatter
    When agents pair --apply runs
    Then .kimi-code/agents/cheap-editor.md keeps the hyphenated name
    And its frontmatter carries name/description/tools but no model/effort keys

  Scenario: [ap:kimi-drift-repaired] a hand-edited adapter is drifted, then repaired
    Given a rendered kimi skill adapter that was hand-edited
    When agents audit runs
    Then the kimi skill status is "drifted"
    And agents pair --apply restores it to "present"

  Scenario: [ap:kimi-gate-row-never-fails] the kimi row is observe-only
    Given any manifest with a vendorNotes.kimi entry
    When parity_gate_findings runs
    Then the agent-parity:kimi row status is "pass" or "skip", never "fail"
```

### Acceptance criteria (KIMI-V1) — historical, see KIMI-V1-FU above

- [x] ~~`audit` reports each declared-but-absent kimi skill adapter as
      `unportable` with a kimi-specific nearest-equivalent (not `agents pair`).~~
      SUPERSEDED by KIMI-V1-FU (2026-08-07): absent is now `missing`, fix names
      `agents pair --apply`; `unportable` survives only for an unreadable
      canonical source.
- [x] `matrix.vendorNotes.kimi` is exposed verbatim by `audit`.
- [x] `parity_gate_findings` emits `agent-parity:kimi` as `pass`/`skip` only.
- [x] No kimi hook gap is ever fabricated while the manifest declares no kimi
      events leg.

(The original KIMI-V1 Gherkin block was replaced by the KIMI-V1-FU scenarios
above: `ap:kimi-skill-unportable` described the pre-rendering law and is
retired; `ap:kimi-gate-row-never-fails` lives on there.)

### Amendment: AGY-V1 — Antigravity Overseer Adapter & Capability Parity (2026-08-07)

```gherkin
Feature: Antigravity rendering & readiness leg (AGY-V1)

  Scenario: [ap:antigravity-hooks-rendered] pair renders workspace hooks.json
    Given a manifest with antigravity vendor notes or skill declarations
    When agents pair --apply runs
    Then .agents/hooks.json is created with PreToolUse, Stop, and PreInvocation hooks

  Scenario: [ap:antigravity-agents-rendered] pair renders agent markdown profiles
    Given canonical agent profiles in .claude/agents/*.md
    When agents pair --apply runs
    Then .agents/agents/*.md profiles are created with model tier mapping (inherit/flash/pro)

  Scenario: [ap:antigravity-readiness] doctor reports antigravity readiness axes
    Given Antigravity CLI 1.1.11 and .agents/hooks.json wired
    When harness doctor runs
    Then antigravity-hooks-wired reports ok and antigravity-readiness reports execution/parity/governance ready
```

