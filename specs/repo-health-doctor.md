# SPEC-123 — Repo-health `doctor`: WARN-only environment diagnostics

Status: proposed 2026-07-12 (acceptance: testing/scenarios/rh_repo_health.py).

Intake (SPEC-116 door NEW, from specs/templates/intake-refinement.md): request =
"ship a deterministic WARN-only `doctor` top-level CLI verb that makes the
OneDrive/.git-reparse/autocrlf risk visible". Covered-check: `records search
doctor repo health onedrive` → no hit (`[]`); `doc-find repo health doctor
onedrive` → no enrichment hit. Decision: **NEW**. Surface is CLI-only.

## Goal

A supervisor can see, in one deterministic command, whether the repo's physical
home is fighting git: `python scripts/harness.py doctor` prints three checks
(OneDrive path, `.git` reparse point, autocrlf-vs-`.gitattributes` conflict) and
always exits 0. Observe-only — it makes the documented corruption/index.lock/
autocrlf risk visible; it never blocks, spawns nothing, changes nothing.

## Applicability

Applies to `scripts/harness_lib/repo_health.py` (`checks(root)`, `cmd_doctor`)
and its one-line registration in `scripts/harness_lib/cli_registry.py`. This is
the first new verb shipped purely through the MF.1-r2 registry: **zero
`scripts/harness.py` edits**. Does not change any existing verb, the workflow
tree (`workflow doctor` is an unrelated subcommand), gates, or state; no daemon,
no polling (observation must pay for itself).

## Requirements / invariants (numbered, testable)

1. **Three deterministic checks.** `checks(root)` returns exactly three dicts
   `{"id","status","detail"}` with `status` in `{"ok","warn"}` and ids
   `onedrive-path`, `git-reparse-point`, `autocrlf-conflict`.
2. **onedrive-path.** Warn iff `"onedrive"` occurs in any lowercased component
   of `root.resolve().parts`.
3. **git-reparse-point.** Windows-only: warn iff `os.lstat(root/".git")
   .st_file_attributes` has `FILE_ATTRIBUTE_REPARSE_POINT` set. Non-Windows or
   no `.git` → ok ("not applicable").
4. **autocrlf-conflict.** Warn iff `git config core.autocrlf` returns `true`
   AND `.gitattributes` contains `eol=lf` (subprocess timeout 15s). Any git
   failure → ok ("unreadable") — a broken git is a non-signal, never a crash.
5. **WARN-only.** `doctor` prints one line per check and exits 0 regardless of
   warn count.
6. **Registry-only surface.** The verb registers in `cli_registry.register()`;
   existing verbs' order and help text are unchanged and `harness.py` is not
   edited.

## Gherkin scenarios

```gherkin
Feature: repo-health doctor

  Scenario: [rh-1] OneDrive path warns
    Given a directory whose resolved path contains a "OneDrive" component
    When checks() runs against it
    Then the onedrive-path check has status "warn"

  Scenario: [rh-2] clean temp path is ok
    Given a plain temp directory outside OneDrive with no .git
    When checks() runs against it
    Then every check has status "ok"

  Scenario: [rh-3] doctor exits 0 even with warns
    Given this repo (which lives under OneDrive and warns)
    When "python scripts/harness.py doctor" runs
    Then it prints the three checks and exits 0
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Os três riscos (OneDrive sync de `.git`, index.lock/corrupção, autocrlf) são reais e documentados neste repo | `docs/roadmap/git-onedrive-path-hygiene.md` (Part B: ReparsePoint em `.git`, delete-locks recorrentes); `harness_lib/common.py` `rmtree_robust` (retry por handles OneDrive/AV) |
| WARN-only, exit 0 sempre — observar, não controlar; sem daemon | memória "observation must pay for itself"; a decisão de relocar (Phase 3) é do operador, não do harness |
| Registro via `cli_registry.register()`, zero edits em `harness.py` | `scripts/harness_lib/cli_registry.py` docstring (receita MF.1-r2: handler + uma linha) |
| `doctor` top-level não colide: só existe `workflow doctor` (subcomando) | `scripts/harness.py` (`wsub.add_parser("doctor")`) |

## Test strategy

- Behaviors: OneDrive component → warn; clean temp dir → all ok; live CLI run
  exits 0 with warns present; check ids/statuses well-formed (rule 1).
- Edge cases: no `.git` (temp dir) → reparse check "not applicable"; git
  failure path returns ok "unreadable" (rule 4) — exercised implicitly on any
  machine without git.
- Regression net: `testing/scenarios/cli_registry.py` frozen top-level surface
  (order preserved, `doctor` appended) guards rule 6.
- Coverage: deterministic, stdlib-only, no LLM — `testing/scenarios/rh_repo_health.py`.

## Validation

- `python testing/scenarios/rh_repo_health.py` — rh-1/rh-2/rh-3 all green.
- `python testing/scenarios/cli_registry.py` — registry surface intact with the
  new verb.
- `python scripts/harness-test.py smoke` and `spec-pack --no-project-commands` —
  template conformance + static integrity.

## Amendments

### v2 (2026-07-13) — fourth check: `keys-staleness` (config-keys phase 2)

Invariant 1 grows from three to FOUR checks: `keys-staleness` WARNs when a
vault key's `lastRotated` (`.harness/state/keys-meta.json`, written by the
`keys` verb — see config-keys.md v2) is older than `keys_vault.STALE_DAYS`
(90). No metadata file, no keyring, or an unreadable date → ok (a missing
vault is a non-signal, never a crash). WARN-only and exit-0 semantics are
unchanged; rh-1..rh-3 assert by membership, so the existing scenario ids
hold. The staleness behavior itself is covered by `[kv-4]` in
`testing/scenarios/kv_keys_vault.py` (config-keys.md v2).

### v3 (2026-07-13) — seventh check: `precommit-gate-hookspath` (SPEC-137 wiring guard)

Invariant 1's registry is now SEVEN checks: `keys-staleness` (v2),
`intake-staleness` (cm-6), and `experiment-overdue` (SPEC-116 exl) joined since
v2, and now `precommit-gate-hookspath`. It WARNs when the SPEC-137 pre-commit
validation gate is ENABLED in policy (`validation_stamp.load_policy` non-None) but
`git config core.hooksPath` does not run this repo's `tools/git-hooks/pre-commit`
(compared via `os.path.samefile`) — the OneDrive twin desync that left the gate
silently non-enforcing on 2026-07-13. A disabled/absent policy is a non-signal
(ok), so a clean temp dir stays all-ok (rh-2 holds); WARN-only + exit-0 unchanged.
The scenario's `IDS` tuple (`rh_repo_health.py`) is the drift guard — the id list
must match `checks()` exactly.

### v4 (2026-08-06) — check `keys-shadow` (config-keys phase 2, env-shadows-vault)

Invariant 1's registry gains `keys-shadow`: it WARNs when a process env var holds
a DIFFERENT value than the vault for the same registry key — the stale-env-shadows-
vault 401 incident (config-keys.md v3). env-wins is load-bearing (SPEC-107), so
this SURFACES the divergence, never reconciles it; the detail names the diverging
keys (NAMES are value-free) and points at `clear the env var or re-run keys set`.
Values are compared inside `keys_vault.shadow_divergences()` (never surfaced).
`HARNESS_NO_VAULT=1`, absent keyring, or no divergence → ok — so a clean temp dir
stays all-ok (rh-2 holds) and `rh_repo_health.py` main() pins `HARNESS_NO_VAULT=1`
for determinism (the check reads live env+vault). WARN-only + exit-0 unchanged.
The WARN path is covered by `[kv-6]` in `testing/scenarios/kv_keys_vault.py`; the
`IDS` tuple gains `keys-shadow` (drift guard — must match `checks()` exactly).
