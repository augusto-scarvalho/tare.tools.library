# SPEC-130 — `config`: read-only masked inventory of expected env/config keys

Status: proposed 2026-07-12 (acceptance: testing/scenarios/ck_config_keys.py).

Intake (SPEC-116 door NEW, from specs/templates/intake-refinement.md): request =
"a read-only, MASKED inventory of which expected env/config keys are set —
presence-only, values never echoed" (P1, Wave-0, owner decision #2 scope).
Covered-check: `chat` shows a provider-key checklist only inside its setup
wizard; `targets` checks `requiresEnv` per target; no verb inventories the
harness's own expected keys on demand. Decision: **NEW**. Surface is CLI-only.
Slice: phase 1 is read-only; the `config-set` WRITE action is phase 2 and is
explicitly OUT of this spec.

## Goal

An operator can see in one command which of the env/config keys the harness
actually reads are provisioned — without any secret value ever reaching a
terminal, a log, or an agent transcript: `python scripts/harness.py config
keys` prints a masked presence table (or `--json`) and always exits 0.
Observe-only: it reads `os.environ`, OS-vault key presence and
`.harness/project.json`; it changes nothing.

## Applicability

Applies to `scripts/harness_lib/config_keys.py` (`CONFIG_KEYS`, `status(root)`,
`cmd_config`) and its one-line registration in
`scripts/harness_lib/cli_registry.py` (MF.1-r2 registry path, **zero
`scripts/harness.py` edits** — doctor/spec-index/failure-patterns/docs-tree
proved the path). Does not change any existing verb, the workflow tree, gates,
or state; no daemon, no polling (observation must pay for itself).

## Requirements / invariants (numbered, testable)

1. **Curated literal registry.** `CONFIG_KEYS` is a literal list of
   `(name, kind env|project, required, plain, description)` seeded ONLY with
   keys the harness actually reads today: the provider env keys
   (`GEMINI_API_KEY`, `GOOGLE_API_KEY`, `NVIDIA_API_KEY`, `OPENAI_API_KEY`,
   `OPENAI_BASE_URL`, `HARNESS_ALLOW_NETWORK_EXPORT`) and the
   `.harness/project.json` knobs their consumers read
   (`knowledgeGraph.llmAssisted.enabled`,
   `knowledgeGraph.apiAssistedProviders.nvidia.enabled`,
   `workflows.workerEnvFilter`,
   `workflows.budgets.tokenBudget.charsPerToken`, `coverage.enabled`,
   `intakeTriage.minPromptChars`). No invented keys.
2. **Presence detection.** `status(root)` marks an env key `set` when
   `os.environ` holds a non-empty value OR the OS vault holds it (presence
   only, the value never leaves the vault). v2 (SPEC-169, 2026-07-24) replaced
   the former `.env` name-parse with this vault probe. A project key is `set`
   when its dotted path resolves in `.harness/project.json` (via `read_json`)
   to a non-null value.
3. **Masking is a trust boundary.** A raw env/secret value NEVER appears in
   any output mode. An env key's `display` is `first2 + "…" + len` (no
   prefix at all for values shorter than 6 chars); a key known only from the
   vault displays the value-free marker `in vault`. A full value is
   shown ONLY for a `project` knob whose registry entry whitelists it as
   `plain=True`; `status()` masks env keys unconditionally, even if a
   registry entry mislabels one as plain.
4. **Read-only, rc 0.** `config keys` (masked table or `--json`) and
   `config list` (the registry itself, no values at all) always exit 0 and
   never write anything.
5. **Registry-only surface.** The verb registers in `cli_registry.register()`;
   existing verbs' order and help text are byte-identical and `harness.py` is
   not edited. (The frozen top-level list in
   `testing/scenarios/cli_registry.py` gains the `config` token — disclosed.)
6. **Write actions are out.** Phase 1 exposes no mutating action; `config-set`
   is phase 2, behind its own spec amendment.

## Gherkin scenarios

```gherkin
Feature: config keys masked inventory

  Scenario: [ck-1] a seeded env key shows as set and masked
    Given a registry env key seeded with a known fake secret in os.environ
    When status() runs
    Then the key's row has set=true and display=first2+"…"+len, never the raw value

  Scenario: [ck-2] the raw value appears nowhere in any output mode
    Given a registry env key seeded with a known fake secret in os.environ
    When "config keys" and "config keys --json" run through the real CLI
    Then the raw secret substring is absent from stdout and stderr of both

  Scenario: [ck-3] config keys exits 0
    Given this repository
    When "python scripts/harness.py config keys" runs
    Then it prints the presence table and exits 0
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Registro curado literal, só chaves que o código lê hoje | call sites `os.environ.get(` (harness.py:2528/2635, discovery.py, chat_engines.py, chat_setup.py) e consumidores de project.json (gate_generic, token_calibration, intake_triage, spec_test_gate) |
| Mascarar sempre env; valor pleno só para knob project whitelisted | decisão do owner #2 (presence-only + masked); `.harness/project.json` é commitado, não-segredo |
| `.env` parse de NOMES apenas, nunca valores | `common.load_env_file` já carrega valores no processo; o inventário nunca precisa deles |
| Registro via `cli_registry.register()`, zero edits em `harness.py` | receita MF.1-r2 na docstring de `cli_registry.py`; doctor/spec-index/failure-patterns/docs-tree provaram o caminho |
| Read-only, exit 0 sempre — observar, não controlar | memória "observation must pay for itself"; espelha `doctor`/`spec-index`/`docs-tree` |
| `config-set` fica na fase 2 | fatiamento do brief (Wave-0 = leitura); escrita exige trilha própria de aprovação |

## Test strategy

- Behaviors: seeded fake secret → row set+masked (ck-1); raw substring absent
  from `keys` AND `keys --json` stdout+stderr through the real CLI (ck-2, the
  security assertion — non-negotiable); live `config keys` exits 0 (ck-3).
- Edge cases: value shorter than 6 chars → mask carries no prefix (rule 3);
  key in the vault but absent from `os.environ` → `in vault` marker, no
  value; missing project path → unset row, empty display.
- Env hygiene: the scenario saves/restores any real value of the seeded key.
- Regression net: `testing/scenarios/cli_registry.py` frozen top-level surface
  (order preserved, `config` appended before `workflow`) guards rule 5.
- Coverage: deterministic, stdlib-only, no LLM —
  `testing/scenarios/ck_config_keys.py`.

## Validation

- `python testing/scenarios/ck_config_keys.py` — ck-1/ck-2/ck-3 all green.
- `python testing/scenarios/kv_keys_vault.py` — the v2 vault scenarios
  (kv-1..kv-4) all green.
- `python testing/scenarios/cli_registry.py` — registry surface intact with the
  new verb.
- `python scripts/harness-test.py smoke` and `spec-pack --no-project-commands` —
  template conformance + static integrity.

## Amendments

### v2 (2026-07-13) — phase 2: OS-vault backend + `keys` verb (owner decision #2)

Owner decision 2026-07-13 #2 rescoped the write path: keys go to the OS-native
vault (Windows Credential Manager / macOS Keychain / Linux Secret Service) via
the `keyring` lib (pinned **25.6.0** — the one runtime dep, justified by the
decision; supply-chain L19/L20 satisfied), NOT to `.env`. New surface, all in
`scripts/harness_lib/keys_vault.py` + one `cli_registry` line:

- **Read cascade env → vault** (v2 2026-07-24, SPEC-169: the `.env` tier was
  REMOVED): `inject_vault_keys()` runs via `common.load_ambient_keys` at
  startup, fills only registry env keys absent from the environment, and is a
  silent no-op when keyring is missing or `HARNESS_NO_VAULT=1` (the renamed
  `HARNESS_NO_DOTENV`; CI/containers provision through real env vars).
- **`keys set NAME`** reads the value from STDIN (getpass on a TTY), NEVER
  argv; `keys unset NAME` deletes. (`keys migrate` was retired with the `.env`
  tier.) Every write/delete leaves a records entry with the key NAME +
  timestamp, never the value.
- **`keys list`** = presence + `backend` column (env|keyring) +
  `lastRotated` (non-secret metadata in `.harness/state/keys-meta.json`),
  masked exactly like phase 1; TE.5 compact TSV under
  `HARNESS_AGENT_OUTPUT=compact`.
- **Doctor**: a 4th WARN-only check `keys-staleness` (vault keys not rotated
  in 90 days) — see repo-health-doctor.md v2.
- The GUI write action (`config-set` calling this same verb) stays OPEN as
  `config-keys-gui`.

```gherkin
Feature: OS-vault key backend (phase 2)

  Scenario: [kv-1] vault writes are value-free everywhere but the vault
    Given a fake keyring backend and a temp root
    When set_key stores a key and unset_key removes it
    Then metadata carries lastRotated, the records entry has the NAME never
      the value, unset removes both, and rows() shows the backend column

  Scenario: [kv-2] the read cascade is env, then vault, and .env is inert
    Given the key present in the vault and also named in a planted .env with
      a different value
    When load_ambient_keys runs with the key absent from the environment
    Then the process env receives the VAULT value, a pre-existing env value is
      never overridden, and a key named ONLY in .env stays absent

  Scenario: [kv-3] the keys verb guards its usage
    Given this repository
    When "keys list" runs plain and compact, and "keys set" runs without NAME
    Then list exits 0 (TSV under compact) and the nameless set exits 2

  Scenario: [kv-4] doctor warns on stale vault keys
    Given a temp root whose keys metadata is older than the staleness window
    When repo_health.checks runs
    Then keys-staleness reports warn naming the key, and the live doctor
      still exits 0
```

### v3 (2026-08-06) — `keys-shadow`: env-shadows-a-different-vault-value detector

Incident: a stale Windows **User**-scope env var (`GEMINI_API_KEY`, a dead 401
key) silently SHADOWED a valid key in the vault. env-wins is load-bearing
(SPEC-107: CI/containers override the vault), so the cascade is unchanged — the
gap was VISIBILITY: `keys list` showed `backend=env` with the value masked, so
the divergence was invisible and cost ~30 min to diagnose.

- **`shadow_divergences()`** (keys_vault.py): registry env keys whose PROCESS
  env value differs from the vault value for the SAME name. VALUE-FREE — NAMES
  only, values compared internally. env-set-but-vault-EMPTY is deliberately NOT
  reported (legit CI/container provisioning; flagging it cries wolf). Compares
  values RAW (a trailing space/newline that 401s while the vault is clean IS the
  incident — normalising would mask it). `HARNESS_NO_VAULT=1` suppresses it,
  mirroring `inject_vault_keys()`. Degrades to `[]` when keyring is absent.
- **`keys list`** gains a value-free `diverges` field (bool); the human line
  appends ` != vault` when set. The masked `display` is NEVER mutated (no
  value-correlated suffix on a value-masked field).
- **Doctor**: a WARN-only check `keys-shadow` — see repo-health-doctor.md v3.

**Known limitations.** The detector compares the CURRENT process env against the
vault, per registry name. It does NOT read persisted Windows env
(`HKCU\Environment` / User / Machine scope) — if it reports ok but calls still
401, open a fresh shell (or check `setx`) to inherit current env. Aliases
(`GEMINI_API_KEY` / `GOOGLE_API_KEY`) have separate vault slots and are compared
independently (no cross-alias resolution). An env var with no vault entry is not
warned — env-only provisioning has no vault backup, so clear a local-test env
var before relying on the vault.

```gherkin
  Scenario: [kv-6] keys-shadow surfaces an env var that differs from the vault
    Given a fake keyring backend holding one value for a registry key and a
      DIFFERENT value for the same key in the process environment
    When shadow_divergences and repo_health.checks run
    Then the key name is reported, the list row carries diverges=true with the
      masked value never mutated and no raw value in the row, the doctor
      keys-shadow check warns naming the key, and an env value EQUAL to the
      vault is silent
```
