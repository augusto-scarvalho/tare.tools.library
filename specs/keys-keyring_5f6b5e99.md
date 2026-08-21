# SPEC-169 — keys-keyring: vendor keys move to the OS vault, write-only

Status: SPEC-169 **v2** (2026-07-24) — the `.env` tier is REMOVED; the vault is the
sole secret backend. v1 proposed 2026-07-22 (acceptance:
`testing/scenarios/kk_keys_keyring.py`).

## v2 amendment (2026-07-24) — the `.env` tier is gone

Trigger: the owner rotated every key into the vault through the GUI and deleted
`.env`. Measured before the change: the two vendor keys in `.env` DIFFERED from the
vault's (the file held the pre-rotation values), and because `inject_vault_keys()`
ran before the `.env` merge — whose semantics were setdefault — the vault was
already winning. The file was dead weight holding revoked credentials.

Decision (owner, 2026-07-24): remove the `.env` tier entirely — the loader, the
`.env.example` template, the migrate verb, and every provisioning read. The cascade
becomes `os.environ → keyring`, full stop.

What v2 changes against v1's numbered invariants:

- **Inv. 1** — `RESOLVE_SOURCES` drops `dotenv`: `environ | keyring | missing`.
- **Inv. 2** — the warn-once trigger is RE-POINTED. v1 warned only when `.env` could
  cover the gap; with the tier removed that trigger would have gone permanently
  silent, and a keyring-less host would resolve NO keys with NO warning. v2 fires on
  the gap itself: vault unreachable AND the key absent from the environment.
- **Inv. 5** (destruction is HUMAN-ONLY) — the VERB changes, the rule survives. `keys
  migrate --apply` is removed (there is no source tier to migrate from; the rule was
  also latently WRONG by then — `migrate_plan` decided by presence in `.env` alone,
  never comparing against a newer vault entry, so applying it after a rotation would
  have overwritten fresh keys with stale ones). The denial moves to `keys unset`,
  which is strictly more destructive than the v1 case: no backup, no undo, and no
  `.env` left to recover from.
- **New inv. 7** covers the removed tier.
- **Inv. 3, 4, 6** — unchanged.

`keyring` moves from `requirements-optional.txt` to a new `requirements.txt` — the
project's FIRST hard runtime dependency. This retires the stdlib-only invariant that
`docs/OPERATOR_GUIDE.md` and the research-doc premise lists had carried. The overseer
raised that collision and proposed keeping it optional; the owner overruled on
2026-07-24 ("keyrings não opcional"), and the decision stands: a sole secret backend
that might not be installed is not a backend. Recorded here so the invariant's
retirement is traceable to a decision rather than to drift.

**Making the hard dependency real.** Nothing installed `requirements-optional.txt` —
no launcher, no script, no CI — so declaring keyring required would otherwise have
left a fresh clone silently unable to resolve ANY key. `setup.sh`/`setup.bat` now
install `requirements.txt` right after creating the venv, and unlike the optional
highlight step they ABORT on failure. The SPEC-147 zero-touch launcher rule is
extended two ways: it now covers `chat.*` (previously only `ui.*` had it), and its
condition widens from "venv missing" to "venv missing OR required dep missing",
probed as `import keyring`. Widen that probe if `requirements.txt` grows.

Also deliberately kept: every DEFENSIVE `.env` exclusion stays in force —
`discovery.py`'s pre-egress denylist (files go to external APIs there),
`release_integrity.py`, `controlled_writes.py`, `artifacts.py`, the
`**/.env*` deny glob in `task-profiles.json`, and `protect_files.py`. Those never
read `.env` to provision anything; they stop a `.env` that appears from ANY source
(a subrepo, a copied tree, a future adopter) from being published, shipped, or sent
to an external API. Removing them would re-open the integrity finding recorded in
`controlled_writes.py`.

Intake (SPEC-116 door: amendment of the SPEC-130 `config`/vault surface, owner GO
2026-07-22 with the `keyring` lib approved). Trigger: the `.env`-in-explorer incident
(a pre-flip audit; the write-worker denylist already shipped as the first defense).
Decision: vendor key VALUES leave `.env` and live in the OS vault (Windows Credential
Manager / macOS Keychain / Linux Secret Service); every form is WRITE-ONLY; no surface
(GUI, API, log, argv, result) ever displays or transports a key value in the clear
beyond the existing stdin seam.

## Goal

An operator provisions and rotates vendor keys without a secret value ever reaching a
file, a log, a process listing, a result, or an agent transcript. Keys resolve at
runtime keyring-first — `os.environ` → OS vault → absent (v2: the `.env` tier was
removed) — logged only by value-free source label. Writes go through `keys set NAME`
(value read from stdin, never argv) and the allowlisted GUI form (value in one
token-gated POST body, popped before serialization, streamed to stdin, never read
back).

## Applicability

Applies to `scripts/harness_lib/keys_vault.py` (`resolved_source`, `RESOLVE_SOURCES`,
`inject_vault_keys`, `cmd_keys`), its one-line registration in
`scripts/harness_lib/cli_registry.py`, `common.load_ambient_keys` (v2: replaces
`load_env_file`) and its startup call in `scripts/harness.py`, the
`config_keys_snapshot`/`/api/routing` feed that carries per-key `source`, the
allowlisted `keys-set` action in `scripts/harness_lib/ui_actions.py`, the onboarding
checklist in `scripts/harness_lib/chat_setup.py` (v2: stores to the vault instead of
appending to `.env`), and the React Registry › Keys view
(`ui/src/domains/registry/KeysView.tsx` + `RegistryScreen.tsx` + `shell/domainMap.ts`).
It amends the SPEC-130 vault surface; it changes no other verb, gate, or state schema.
The real OS vault is out of scope.

Explicitly OUT of scope, and unchanged by v2: the defensive `.env` exclusions in
`discovery.py` (pre-egress denylist), `release_integrity.py`, `controlled_writes.py`,
`artifacts.py`, `task-profiles.json`, and `tools/hooks/protect_files.py`.

## Requirements / invariants (numbered, testable)

1. **Keyring-first resolution.** `resolved_source(name)` returns exactly one of
   `RESOLVE_SOURCES` = `environ | keyring | missing` (v2: `dotenv` removed),
   evaluated in that cascade order (os.environ wins a session override; the vault
   fills the hole). The resolution is VALUE-FREE — it returns a label, never a value.
2. **Graceful degrade, warned once.** A missing/failed keyring backend is a silent
   no-op for injection (the harness never breaks for lack of the lib); when the vault
   is unreachable AND an expected key is absent from the environment — i.e. the key is
   genuinely unobtainable — the cascade emits ONE stderr warning per process, and that
   warning never prints a value.
3. **Write via the stdin seam.** `keys set NAME` reads the VALUE from stdin (getpass on
   a TTY), never argv — the parser carries only the NAME. The vault write stamps
   `lastRotated` metadata and a records entry with the NAME + timestamp only, never the
   value; the CLI echoes that the value was not echoed.
4. **GUI form is write-only.** The `keys-set` action streams the value via `stdinParam`
   (popped from params before any serialization, S1) and shares the S2 name guard; an
   empty value is refused pre-argv ("read from stdin, never argv", S4). The value never
   lands in argv, a refusal payload, the result, an event, a record, or a readback. The
   Keys view never renders a value field — only masked presence + source.
5. **Destruction of secrets is HUMAN-ONLY.** v1 applied this to `keys migrate
   --apply`; v2 removed that verb and moved the rule to its inheritor, `keys unset`
   (owner decision 2026-07-24). `keys unset` deletes a key from the OS vault with no
   backup and no undo, and since the vault is now the SOLE backend there is no `.env`
   tier left to recover from — strictly more destructive than the v1 case, which at
   least left a `.env.bak-<ts>`. It is denied from agent shells in
   `deny_hitl_flags.py`; the owner runs it via the `!` escape
   (`HARNESS_CHAT_HITL_OK=1`). `keys list` and `keys set` stay allowed — `set` is
   additive and re-runnable.
6. **No value in any surface.** Across every write/resolve path, a key value appears
   in no file the harness writes (result, log, records), no argv, and no
   stdout/stderr — only the vault holds it.
7. **The `.env` tier is INERT (v2).** No provisioning path reads `.env`. A file
   planted at the repo root holding a registry key must: resolve `missing`, never be
   injected into `os.environ`, never mark the key `set` in `keys list` / the GUI
   snapshot, and be neither modified nor backed up. Suppressing vault injection for
   key-absent tests is `HARNESS_NO_VAULT=1` (v1's `HARNESS_NO_DOTENV`, renamed for
   what it now gates — it disabled injection only as a side effect of sitting before
   it inside the removed loader).

## Rationale & sources

Every normative decision carries a source (SPEC-116 inv. 7).

| Decisão | Fontes |
|---|---|
| Chaves saem do `.env` para o vault do OS | incidente `.env`-no-explorer (auditoria pré-flip); denylist de write-worker já shipada (SPEC-148) como 1ª defesa |
| Lib `keyring` 25.6.0, import guardado, degrade silencioso + warning UMA vez | owner GO 2026-07-22; `requirements-optional.txt`; o harness é stdlib-only e nunca quebra por falta da lib (zero-friction) |
| ~~Cascade environ → keyring → dotenv → missing~~ → **v2: environ → keyring** | decisão #3 do plano; v2 (owner 2026-07-24) removeu o tier `.env` — medido: o `.env` guardava as chaves PRÉ-rotação e o vault já vencia, então o arquivo era peso morto com credencial revogada |
| v2: gatilho do warn passa a ser o GAP (sem vault E chave ausente do env) | o gatilho v1 era "o `.env` cobriria a falta"; sem o tier ele ficaria mudo para sempre e um host sem keyring resolveria ZERO chaves em silêncio |
| v2: `keyring` vira dependência DURA (`requirements.txt`, a primeira do projeto) | decisão do owner 2026-07-24 ("keyrings não opcional"), sobrepondo a proposta do overseer de mantê-la opcional: backend único de segredo que pode não estar instalado não é backend. Aposenta a invariante stdlib-only (`docs/OPERATOR_GUIDE.md` + ~8 docs de pesquisa) — registrado para a aposentadoria ser rastreável a uma decisão, não a drift |
| v2: exclusões DEFENSIVAS de `.env` permanecem | elas não provisionam nada; barram um `.env` de QUALQUER origem de ser publicado/enviado — `discovery.py` manda arquivo pra API externa, e `controlled_writes.py` registra o achado de integridade que a criou |
| Escrita por stdin, nunca argv | valor em argv vaza para `ps`/histórico de shell; o seam de stdin já existia no `keys set` (SPEC-130 v2) |
| Form GUI write-only, valor em UM POST token-gated, popped antes de serializar (S1/S4) | contrato de allowlist `ui_actions.run_action`; a fronteira de confiança "o compilador é a fronteira" |
| ~~`migrate --apply` HUMAN-ONLY~~ → **v2: a regra passa para `keys unset`** | o verbo saiu (sem tier `.env` não há de onde migrar; e `migrate_plan` decidia só por presença no `.env`, sem comparar com entrada mais nova do vault — aplicá-la após uma rotação sobrescreveria chave nova com velha). Mas a INTENÇÃO — destruir segredo é do owner — vale mais em `unset`: sem backup, sem undo, e sem `.env` de onde recuperar (owner 2026-07-24) |

## Gherkin scenarios (UI surfaces only)

The Registry › Keys view is a UI surface (masked presence table + write-only set form),
so the acceptance is expressed as scenarios whose `[check-id]`s resolve to named checks
in `testing/scenarios/kk_keys_keyring.py`.

```gherkin
Feature: vendor keys in the OS vault, write-only

  Scenario: [kk-1] resolution is keyring-first and value-free
    Given a key present in the environment, in the vault, or only in a planted .env
    When resolved_source runs for each, and the vault is then made unavailable
    Then the source label is environ, keyring, or missing in that order
      and the .env-only key resolves missing, not dotenv
      and an unobtainable key warns exactly once, never printing a value

  Scenario: [kk-2] a key is set through the stdin seam
    Given a fake vault and a temp root
    When "keys set NAME" reads the value from stdin
    Then the value is stored, the parser carried only the NAME, and the echo
      and the records entry never contain the value

  Scenario: [kk-3] the .env tier is inert in every reader
    Given a .env planted at the root holding a real registry key, and a fake vault
    When resolved_source, inject_vault_keys, and the keys rows are all exercised
    Then the key resolves missing, is never injected, is never marked set,
      and the planted file is neither modified nor backed up

  Scenario: [kk-4] the GUI set form never leaks the value
    Given the allowlisted keys-set action
    When it runs unconfirmed with a value, then confirmed with an empty value
    Then the value is popped before serialization and absent from the refusal,
      and the empty value is refused before any argv is built

  Scenario: [kk-5] no surface carries a key value
    Given every write and resolve path exercised above
    When their outputs, files, and payloads are collected
    Then the canary secret appears in none of them
```

## Test strategy

- Behaviors: cascade order + labels + warn-once (kk-1); stdin-seam write with a
  value-free echo/record (kk-2); dry-run-vs-apply with a value-free `.env` comment and a
  single-copy backup (kk-3); the write-only action's S1/S4 seam (kk-4).
- Security tooth (non-negotiable): a canary secret threaded through every path is
  asserted ABSENT from all captured surfaces (kk-5) — the "no value anywhere" invariant.
- UI smoke: `ui/tests/pw-smoke.mjs::registry-keys-writeonly` mounts the native Keys view,
  proves the write-only password form is present and its value field carries no value,
  and never posts a secret (synthetic name, no submit).
- Isolation: a FAKE in-memory keyring backend is patched for every vault interaction —
  the real OS vault is never written; env and module ROOT are saved/restored; migrate
  runs against a temp-root `.env` fixture (the real `.env` is never touched).
- Regression net: `kv_keys_vault.py` (the SPEC-130 vault scenarios), `ck_config_keys*`,
  and `cli_registry.py` frozen surface stay green; `gs_gate_structure` ratchets unchanged.

## Validation

- `python testing/scenarios/kk_keys_keyring.py` — kk-1..kk-5 all green.
- `python scripts/harness_lib/keys_vault.py` — module self-check ok (migrate/apply,
  resolved_source, warn-once).
- `python testing/scenarios/kv_keys_vault.py` and `ck_config_keys_gui.py` — the prior
  vault + GUI-action scenarios still green.
- `cd ui && npx tsc -b --noEmit` — the Keys view + api types typecheck.
- `python scripts/harness-test.py smoke` and `spec-pack --no-project-commands` —
  template conformance + Gherkin mapping + static integrity.

## Amendments

(none yet)
