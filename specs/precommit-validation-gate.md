# SPEC-137 — precommit-validation-gate: every delivery passes validation, agent-agnostic

Status: SPEC-137, proposed 2026-07-13 (acceptance: `testing/scenarios/pvg_precommit_gate.py`).

Intake (SPEC-116 door NEW, from the overseer plan
`.harness/handoff/plan-precommit-validation-gate.md`): request = a pre-commit validation
gate so no change to the product surface (`scripts`, `tools`, `testing`, `specs`) lands
without having passed the harness validation gates against the exact staged snapshot —
enforced the same way for every agent and every human, not by convention. The full gate
runner (`scripts/spec_test_gate.py`) already stamps `.harness/state/quality-state.json`;
this feature adds a *stamp check* at commit time and a `validate --staged` verb that
produces the stamp, so the check is a sub-second index read rather than a full re-run.
Decision: **ship DISABLED** (`precommitValidation.enabled: false`) as the migration
window; a separate follow-up commit flips it on after a green `validate --staged`.

## Goal

A deterministic, agent-agnostic pre-commit gate that BLOCKS a commit whenever the staged
product surface has not been validated by the harness gates. The commit-time hook never
runs validation itself — it compares a fingerprint of the staged git index against the
`quality-state.json` stamp written by `validate --staged`, and fails closed ONLY on a
real inconsistency (missing / failed / mismatched / stale stamp, or an executed profile
that does not cover the change). A shared module (`scripts/harness_lib/validation_stamp.py`)
owns the fingerprint, policy, stamp, and decision logic so the hook and the CLI cannot
drift. A `--no-verify` bypass stays observable through a post-commit audit and an advisory
gate check, so the escape hatch is recorded rather than silent.

## Applicability

Applies to the shared module `scripts/harness_lib/validation_stamp.py`
(`load_policy`, `staged_manifest`, `head_manifest`, `manifest_fingerprint`,
`validator_version`, `required_profile`, `check_staged`, `stamp_staged`,
`detect_override`, `unstaged_surface_paths`, `cmd_validate`), the policy config
`.harness/project.json#/precommitValidation`, the CLI verb `harness.py validate --staged`
(registered in `scripts/harness_lib/cli_registry.py`), the sh shim
`tools/git-hooks/pre-commit` + the Python hook `tools/hooks/precommit_validation_gate.py`,
the post-commit audit line in `tools/git-hooks/post-commit`, and the advisory gate check
`check_precommit_override` in `scripts/harness_lib/gate_checks_policy.py` (wired into
`spec-pack`). It does **not** modify the gate runner's own quality-state writer (a plain
gate run still produces a stamp without `stagedFingerprint`, which the hook correctly
treats as "not validated against the staged snapshot"), add a quality-state JSON schema
file (the shape is pinned by this spec + its writers), expose the verb to the chat-engine
allowlist, or wire CI. Deferred (recorded, not built): a changed-files-scoped scenario
subset to cut the `scenarios` gate cost, and ratcheting the override audit from advisory
to blocking — both later owner decisions over this same stamp shape.

## Requirements / invariants (numbered, testable)

1. **Fingerprint determinism.** `manifest_fingerprint` is the sha256 of the sorted
   canonical index lines (`"<mode> <sha>\t<path>"`); identical index content yields an
   identical fingerprint, and the manifest is built from git index/tree blobs
   (`git ls-files -s` / `git ls-tree`), never disk mtimes. The `exclude` globs drop
   `tools/git-hooks/**`, `**/__pycache__/**`, `**/*.pyc`, and
   `.harness/state/quality-state.json` (the stamp is mutated after fingerprinting and is
   both outside the surface roots and excluded, so it can never self-invalidate).
2. **Decision matrix, fail-closed only on real inconsistency.** `check_staged` returns
   `pass` when the policy is disabled/absent (migration window) or the staged surface
   equals the HEAD surface; otherwise it BLOCKS when any of these hold: quality-state
   missing/corrupt, no `stagedFingerprint`, `status != "pass"`, the staged fingerprint
   mismatches, `policyVersion` mismatch, `validatorVersion` mismatch, or the executed
   gates do not cover the required profile. A corrupt state with the surface untouched
   passes; a corrupt state with the surface touched blocks.
3. **Profile coverage.** `required_profile` maps each changed surface path to a profile
   by root and unions the gates; a change is refused unless the stamped `executedProfile`
   gates are a superset of the `requiredProfile` gates (a `tools/` change stamped only
   under the docs-light `specs` profile is refused; combined changes require the union).
4. **Stamp integrity + observability.** `stamp_staged` is a concurrency-guarded
   read-merge-write (a `quality-state.json.lock` held across the merge, stolen when
   stale) with a compare-and-swap that refuses to clobber a validation newer than this
   run; `validate --staged` stamps `stagedFingerprint` / `policyVersion` /
   `validatorVersion` / `requiredProfile` / `executedProfile` and appends a summary row
   to the validation history; a `--no-verify` bypass is visible to `detect_override` and
   to the advisory `precommit:override-audit` gate check.

## Rationale & sources

| Decision | Sources |
|---|---|
| One shared module for fingerprint/policy/stamp/decision so the hook and CLI cannot drift | `scripts/harness_lib/validation_stamp.py`; the hook `tools/hooks/precommit_validation_gate.py` and CLI both import it |
| Fingerprint the git INDEX (`git ls-files -s`), not disk, so OneDrive mtime noise never invalidates a stamp | `scripts/harness_lib/validation_stamp.py` (`staged_manifest`, `head_manifest`); plan landmine "Index vs worktree" |
| The hook is a stamp CHECK (one `ls-files` + one JSON read), never a validation run — the full gates run in `validate --staged` against the WORKING TREE in place (real branch/history/state), guarded by a staged==worktree equivalence check | `scripts/spec_test_gate.py` (the full runner); `validation_stamp.cmd_validate` + `unstaged_surface_paths` (working-tree validation, option-3) |
| Ship DISABLED as the migration window; flip on in a follow-up that edits only `.harness/project.json` (outside the surface roots), so no chicken-and-egg | `.harness/project.json#/precommitValidation.enabled`; the surface-unchanged pass path in `check_staged` |
| `validatorVersion` hashes only the gate runner + `gate_*.py` + `project.json`, not all of `harness_lib`, so unrelated UI/routing edits do not stale every stamp | `validation_stamp.validator_version` (`VALIDATOR_INPUTS`) |
| Override observability ships BOTH a post-commit append-only audit and an advisory gate check; the audit is `|| true` and never raises so the graph-refresh exec survives | `tools/git-hooks/post-commit`; `validation_stamp.record_override`; `gate_checks_policy.check_precommit_override` |
| `write_json` is already atomic (`os.replace`), so requirement 6 reduces to the lock + CAS, plus one retry on a OneDrive `PermissionError` | `scripts/harness_lib/common.py` (`write_json`); `validation_stamp.stamp_staged` |

## Gherkin scenarios (validation-gate behavior)

```gherkin
Feature: precommit-validation-gate — every delivery passes validation against the staged snapshot

  Scenario: [pvg-1] the fingerprint is deterministic and built from index blobs
    Given a staged surface manifest
    When manifest_fingerprint runs over identical canonical lines
    Then the sha256 is identical, and staged_manifest drops tools/git-hooks, __pycache__,
      *.pyc, and quality-state.json entries, hashing the index blobs rather than disk

  Scenario: [pvg-2] the decision matrix fails closed only on real inconsistency
    Given a staged surface that differs from HEAD
    When check_staged evaluates the quality-state stamp
    Then it blocks on a missing/failed/mismatched/stale stamp, passes on a disabled policy
      and on a surface unchanged vs HEAD, and a corrupt state blocks only when the surface
      was touched

  Scenario: [pvg-3] the executed profile must cover the required profile
    Given a tools/ change requiring the code profile gates
    When the stamp only executed the docs-light specs profile
    Then check_staged refuses the change, and a combined change requires the union of gates

  Scenario: [pvg-4] the stamp has CAS integrity and the bypass is observable
    Given a seeded quality-state and a scratch git repo
    When stamp_staged is asked to write over a newer validation, and a commit changes the
      surface without a matching stamp
    Then the compare-and-swap refuses the stale stamp, and detect_override plus the
      post-commit audit record the bypass

  Scenario: [pvg-5] the delivery-bar advisor reminds and never blocks
    Given a staged behavior change with no scenario delta, a one-vendor hook edit,
      a routing config change, and a new harness_lib module without a doc leg
    When the pre-commit chain runs the delivery-bar advisor
    Then each rule prints its one-line reminder, each counter-example stays silent,
      the gate hook wires the advisor fail-open, and the commit is never blocked
```

## Test strategy

- Behaviors to verify (hermetic, `testing/scenarios/pvg_precommit_gate.py`): the pure
  functions on canned input — `manifest_fingerprint` determinism, the `exclude` globs,
  `required_profile` unioning, and the `check_staged` decision on seeded stamp dicts —
  plus end-to-end paths against a scratch `git init` repo (init + `user.name`/`user.email`
  + a minimal `scripts/x.py`, `specs/y.md`, and `.harness/project.json` carrying the
  policy) that stage a surface change, seed the stamp JSON directly, and invoke
  `tools/hooks/precommit_validation_gate.py` with cwd = the scratch repo, asserting exit
  codes and block-message substrings.
- Edge cases: policy disabled (pass, migration window), surface unchanged vs HEAD (pass),
  quality-state missing and corrupt with the surface touched (block) vs untouched (pass),
  a fingerprint/`policyVersion`/`validatorVersion` mismatch (block), an executed profile
  that does not cover the required profile (block), a CAS attempt to overwrite a newer
  validation (refused), and a bypassed commit (`detect_override` + post-commit audit row).
- Regression risks: the gate runner's own quality-state writer is untouched (a plain gate
  run still stamps without `stagedFingerprint`); the added `precommit:override-audit`
  check is advisory (never `fail`): it degrades to `pass` under the legacy
  `HARNESS_STAGED_SNAPSHOT=1` marker (no longer set by validate --staged) and to `skip`/`pass` on
  any git error, so `spec-pack` stays green standalone or inside a working-tree validate; the
  post-commit audit is append-only, `|| true`, and preserves the graph-refresh exec.
- Coverage impact: enforced via `testing/scenarios/pvg_precommit_gate.py` (the four
  `pvg-*` checks) plus the module's own git-scratch assertions; the scenario is kept fast
  (< 30s) by seeding stamps directly and never running the real full gates inside it.

## Validation

- `python testing/scenarios/pvg_precommit_gate.py` — the `pvg-1`, `pvg-2`, `pvg-3`,
  `pvg-4` checks all green (fingerprint determinism + exclusions, the decision matrix,
  profile coverage, and stamp CAS + override observability).
- `python testing/scenarios/pss_panel_specs.py` — the sibling scenario stays green (the
  shared terminal-scenario idiom is unchanged).
- `spec-pack` feature-spec conformance for this spec (template sections + the `pvg-*`
  gherkin ids resolving in `testing/scenarios/pvg_precommit_gate.py`), and
  `check_validation_policy` over the edited `.harness/project.json`.
- `python scripts/harness.py validate --staged` — validates the staged surface snapshot;
  with a clean tree it takes the "surface unchanged" fast path and exits 0 without running
  the gates.
- `python scripts/harness.py --help` — the `validate` verb is listed; existing verbs are
  unchanged.

## Amendments

### v2 (2026-07-18) — staged `.harness` config runs at HEAD during scenarios

Incident: SPEC-148's staged `executors.json` keep-list trim passed its own gate
run, then failed `rs:env-filtered` on the NEXT run — after landing in HEAD.
Cause is by design: `scenario_isolation.hold_dirty_baseline` materializes the
held state dirs (`.harness/state|context|runtime|routing` + the backlog file)
to **HEAD** for the scenarios gate (owner-dirt protection; the index is never
touched). Consequence, now stated as a rule:

- **Staged changes under the held dirs are exercised by scenarios only after
  commit.** A scenario asserting `.harness` config content will validate the
  staged version one commit late. This is accepted (the alternative — staging
  into the materialized tree — would mix owner dirt back in).
- **The gate says so at run time**: `hold_dirty_baseline` prints a loud
  advisory listing staged paths under the held dirs. A next-run red on such a
  path is a config-vs-assert mismatch, not a flake — fix the assert and the
  config in the same commit.

| Decisão (v2) | Fontes |
|---|---|
| Advisory em runtime, não bloqueio | O shadow é inerente ao desenho HEAD-materialized (correção option-3 abaixo); bloquear staging de config puniria o fluxo normal. Incidente rs:env-filtered 2026-07-18 (commits 8206fe9→5e9544b) |

### v3 (2026-07-18) — delivery-bar advisor in the pre-commit chain

The owner's delivery bar (a shipped behavior needs a durable doc leg, wired
process legs per vendor, and a scenario-gate check) kept being enforced by
agent memory and after-the-fact audits — the 2026-07-18 audit found silent
revert paths in ~half of that morning's items. The bar itself is now a
deterministic reminder at commit time:

- **`tools/hooks/delivery_bar_advisor.py`**, called fail-open from
  `precommit_validation_gate.py`. ADVISORY ONLY: it prints reminders and can
  never block or fail a commit (rules R1/R4 have legitimate false positives —
  a pure refactor has no scenario delta; blocking would punish normal flow).
- Rules over the staged diff: R1 behavior change (`scripts/**`,
  `tools/hooks/**`) without a `testing/scenarios/` delta; R2 one-vendor hook
  wiring (`.claude/settings.json` xor `.codex/hooks.json`/capabilities) —
  the 2-legs rule; R3 `.harness/routing/*.json` change without a scenario pin
  (plus the v2 staged-vs-HEAD reminder); R4 ADDED `harness_lib` module with
  no `specs/`/`docs/` delta.
- Security-spec invariants are deliberately NOT advised on: the
  `security-directive-map` check already hard-enforces them; the advisor must
  not duplicate a blocking control as noise.
- Local-only by construction: lives in this repo's opt-in `core.hooksPath`
  chain; nothing is exported to targets.

| Decisão (v3) | Fontes |
|---|---|
| Advisory, nunca gate | FP legítimo em R1/R4 (refactor sem delta de cenário); precedente v2 (advisory staged-vs-HEAD); auditoria 2026-07-18 (abfa07b) como incidente-fonte |
| Regras derivadas da auditoria real | Os 5 gaps de abfa07b mapeiam 1:1 para R1 (S2/S3/C12/N3 sem check), R2 (matcher a882081), R3 (rs:env-filtered), R4 (doc só em round doc) |

### v4 (2026-07-27) — the gate's own control-plane, and a ledger for the short-circuit

Round `docs/research/gate-surface-definition-2026-07-26.md` (Double Diamond, 4
divergence workers + 4 critics) restated four open registrations as ONE class:
**the gate could not see, validate or remember its own substrate.** Two of the
five blind spots close here; the other three are named preconditions on the
backlog row `gate-surface-definition` and are deliberately NOT attempted yet.

**(a) The control-plane is inside the surface it enforces.** `precommitValidation.exclude`
carried `tools/git-hooks/**`. Both shims are tracked, and `tools/git-hooks/pre-commit`
is 3 lines that `exec` the gate — replacing the body with `exit 0` killed gate,
reckon and post-commit audit at once, and staled no stamp, because
`VALIDATOR_INPUTS` listed no hook. Now:

- the glob leaves `exclude`; `tools/` was already a surface root, so nothing else
  had to move. Cost measured before the change: the shims changed in **2 commits
  in the repo's whole history** (last `087a74f`, 2026-07-13).
- `VALIDATOR_INPUTS` gains `tools/git-hooks/*`, `tools/hooks/precommit_validation_gate.py`
  and `scripts/harness_lib/validation_stamp.py` — the module defining the manifest,
  the exclude matcher and the profile map did not stale a stamp when it changed.
- `gate_checks_policy.check_gate_controlplane` **enforces** it from the `spec-pack`
  tier, reading the LIVE `.harness/project.json` and the LIVE `VALIDATOR_INPUTS`.
  Not a scenario's hardcoded `POLICY` copy: every gate scenario carries its own
  dict, so asserting against one is a measured tautology. It is falsifiable and was
  falsified against the exact pre-change state (both halves red).

**(b) Every short-circuit leaves a row.** `"staged surface unchanged vs HEAD"` was a
tuple and a print; the only other observer of those paths, `delivery_bar_advisor`,
exits 0 always. Four registrations of one root cause in five days were each found
by hand. `validation_stamp.log_bypass` now appends to `.harness/runs/gate-bypass.jsonl`:

- **`.harness/runs`, never `.harness/state`** — v2 above materializes the held
  state dirs to HEAD for the scenarios gate, so a ledger in `.harness/state` would
  be erased by the very gate it audits. Same reasoning already documented for
  `reckon-results.jsonl` (`validation_stamp.py:274-283`). Cost: local-only
  (`.gitignore:38`).
- **both branches**, `staged == head` AND `policy is None` — the not-adopted path
  is the cheapest bypass of all and would otherwise stay off the record.
- an idle tree is not a bypass (nothing staged ⇒ no row); deduped on
  (kind, HEAD sha, fingerprint, staged-path digest) over a tail window, since
  `check_staged` runs on every `verify-status` too, and since the fingerprint is
  by definition unchanged across every bypass at one HEAD.
- **observation only** — no decision changes. Fail-open on any error.

| Decisão (v4) | Fontes |
|---|---|
| Control-plane enforcing, não advisory | O precedente `check_precommit_override` é advisory por decisão de release; um control-plane desligável é classe de segurança, não de aviso. Crítico de segurança Opus 5 xhigh, medido |
| Ledger antes de qualquer redesenho de superfície | A proposta de inverter a polaridade foi derrubada por 3 críticos independentes sobre fatos mensuráveis (15% dos commits viraria certificação falsa); SPEC-158/ToC — *can't exploit a constraint you can't see* |
| `.harness/runs` como destino | Emenda v2 desta mesma spec + `validation_stamp.py:274-283` |

### v5 (2026-08-03) — `ritual-enforcement-map`: every overseer ritual step names its enforcer

The `security-directive-map` idiom (v-less, `scripts/harness_lib/security_directives.py`)
generalizes to the OVERSEER RITUAL: the playbooks accumulated steps whose only proof of
enforcement was the prose that asked for them. The gate now carries a second, identical
conformance check — `ritual-enforcement-map`, `scripts/harness_lib/ritual_map.py`,
mapping file `testing/ritual-enforcement-map.json`:

- **Sources** — `.harness/prompts/overseer-playbook.md` and
  `.harness/prompts/overseer-loop-playbook.md` (session + loop). No other prompt file.
  A STEP is a top-level bullet (`- ` at column 0) or a numbered step (`^\d+[a-z]?\.`),
  running to the next step, heading, fence or blank-line-then-unindented-prose; fenced
  code and HTML comment lines never produce steps.
- **Id scheme** — SHARED with the security map, not copied: `ritual_map` imports
  `directive_id` from `security_directives`, so an id stays `<stem>:<sha1-8 of the
  whitespace/case-normalized text>`. What differs is the INPUT: the step's FULL text,
  not its first line.
- **Ratchet semantics** — the check fails on an unmapped id (a new **or reworded** step:
  editing any prose of a step retires its id and forces a fresh enforcement decision in
  the same commit) and on a stale id (a deleted step must retire its entry). Same
  fix line shape as the security map, pointing at the ritual map file.
- **Status vocabulary** — `hook:<locator>` | `gate:<check>` | `leg:<verify-leg>` |
  `doctor:<rule>` | `advisory:<what>` | `gap:<reason>`, each with a mandatory free-form
  locator after the colon (`gap:` alone is invalid). `gap:` is the honest sibling of the
  security map's `prose`: accepted UNENFORCED, counted in `byStatus`, never silent.
  Day-one baseline: 39 steps — 4 hook, 6 advisory, 1 gate, 1 leg, 27 gap.
- **Mapping-file-only** — the playbooks are read, NEVER written by this mechanism (same
  recorded decision as the security map; it also keeps the check clear of the
  protected-file and playbook chain-lock machinery).

| Decisão (v5) | Fontes |
|---|---|
| Mapping-file-only, playbooks nunca editados | Decisão idêntica já registrada para os seis specs de segurança (docstring de `security_directives`); editar o playbook para satisfazer o próprio check é a captura que o ratchet existe para impedir |
| Hash do texto COMPLETO do passo, não da primeira linha | Um passo do ritual carrega a obrigação no corpo (ex.: step 7c e o `Tie:` receipt); reescrever o corpo mantendo a abertura mudaria a obrigação sem retirar o id |
| `gap:` verde no baseline, não vermelho | Precedente `prose` na v-anterior do mapa de segurança: um baseline vermelho no dia um é entregável quebrado e vira ruído ignorado; a dívida fica VISÍVEL no `byStatus`, contada, não silenciosa |

## Corrections (plan-vs-code, pinned to reality)

- **validate --staged migrated temp-tree -> working-tree (option-3, 2026-07-14).** The original
  temp-tree (`git checkout-index` + `git init`) had no branch/HEAD, so branch-reading scenarios
  (`m5_ui_panel:panel:branch-shown`, `ui_e2e:e2e:gates-and-branch`) failed there though they pass on
  the real repo. `cmd_validate` now runs the required gates against the WORKING TREE in place, guarded
  by `unstaged_surface_paths` (the staged surface must equal the worktree surface, else it refuses so
  the validation matches the commit). `HARNESS_STAGED_SNAPSHOT` is no longer set by validate --staged;
  the advisory override-audit still honors the marker if present, else degrades to skip/pass.

- The plan brief labels this spec **"SPEC-137"** and states SPEC-136
  (`panel-experiments-screen.md`) is the current max — verified: SPEC-136 is the highest
  allocated feature id at authoring time, so **137** is the next free id. ("SPEC-116" in
  the intake line is the SDD/BDD two-door flow this spec is created *through*, not its id.)
- The plan cites the gate runner's own quality-state writer at `spec_test_gate.py`
  1503-1523 and requires it be left unmodified — confirmed unmodified; only a re-export
  line and one `results.extend(check_precommit_override())` line were added.
- `write_json` (`scripts/harness_lib/common.py`) is already atomic via `os.replace`
  (comment dated 2026-07-13), so requirement 6 reduced to the lock-file + compare-and-swap
  plus a single `PermissionError` retry, as implemented in `stamp_staged`.
- **User-origin auto-commit reduces the dirt the gate must tolerate (2026-07-15, Fase 2).**
  A successful mutating GUI action self-commits ITS OWN declared state files via
  `ui_actions.autocommit_state` (scoped `git add/commit -- <paths>`, message
  `chore(state): <action> via GUI`): routing/models edits -> `.harness/routing/*`,
  `resolve-escalation`/`intake-decide` -> their `.harness/state/*` file. Best-effort (one
  index.lock retry then skip, never blocks the action) and scoped so a room's in-flight
  staged work is never swept in. State-only commits fast-pass the pre-commit stamp hook.
  Pure-derived `workflow-state.json`/`task-state.json` are now gitignored (readers tolerate
  absence via `read_json(..., {})`).
- **Auto-commit is OPT-IN via `HARNESS_UI_AUTOCOMMIT=1`, learned the hard way.** The
  browser e2e (`testing/ui/test_panel_e2e.py`) spins up the REAL server bound to ROOT and
  drives `/api/action` (`routing-profile-save/set-role/use` on an `e2e<ts>` profile) — that
  path is `run_action(ROOT, ...)`, identical to an owner click, so an unconditional
  post-success commit made the scenarios gate commit its own test mutations to the repo (4
  junk commits, reset). `run_action` now auto-commits only when `autocommit_enabled()` sees
  `HARNESS_UI_AUTOCOMMIT=1`. The live launcher `cmd_ui` seeds it via
  `os.environ.setdefault("HARNESS_UI_AUTOCOMMIT", "1" if sys.stdout.isatty() else "0")` — the
  server's `/api/action` handler runs in cmd_ui's own process, so the seed reaches
  `run_action`; an interactive owner launch gets auto-commit with no manual export, a headless
  launch stays off, and an explicit owner export wins. Test panels build via
  `harness_ui.make_server` directly (never cmd_ui) so they never seed it — verified by running
  `ui_e2e` standalone (real browser + routing mutations) with the env unset: zero
  `chore(state)` commits, HEAD unchanged. `harness_ui.py` needed no change (in-process server).
  CLI parity remains deferred for the same hazard class: scenarios run `escalations --resolve`
  against the real ROOT, and no `harness.py ui`-style single seam gates CLI verbs.

### v5 (2026-07-27) — R7: a scenario delta with no evidence anyone tried to break it

The advisor's whole premise is that the stamp gate sees THAT a change happened,
never its SHAPE. R7 closes the shape the repo had no reminder for at all.

Measured, same day, in three checks written by an agent that believed each had
teeth — every one survived review and was revealed only by a surviving mutant:

- one proved a NEIGHBOURING mechanism (its sabotage was caught downstream by a
  name-keyed reorder, so deleting the assertion under test left it green);
- one never asserted the CALL SITE still passed its argument (the library was
  stamped and asserted correctly; deleting the caller's kwarg changed nothing);
- one asserted the exception TYPE, so an unrelated crash of the same type read
  as the refusal it was supposed to be proving.

`harness.py oracle mutate` is the only tool in the repo that sees this class, and
before this amendment the string `oracle` appeared in **no hook and no gate
check** — the ritual lived entirely in overseer prose. R7 puts the reminder in the
commit path and names the runnable command with the changed scenario filled in.

ADVISORY like every sibling: a docstring- or comment-only scenario edit is a
legitimate false positive, and blocking would punish normal flow. R7 is R1's exact
complement (R1 = behavior without a scenario; R7 = a scenario at all), and the
self-check carries counters proving neither swallows the other.

The discipline it points at is now a registered playbook,
`.harness/prompts/testing-playbook.md`, on the `review` and `implementer` chains.

| Decisão (v5) | Fontes |
|---|---|
| Advisory, never blocking | Same reasoning as v3's R1/R4: legitimate false positives exist (a comment-only scenario edit), and the reminder IS the product |
| Reminder rather than recorded mutation evidence | Binding a commit to a stored mutation verdict would need a fingerprint-keyed ledger like gate/reckon; unjustified before a measured recurrence, and it would gate the cheap path on an expensive tool |
| The playbook carries the how | A one-line reminder cannot teach the three failure modes; the rule points at the file that can |
