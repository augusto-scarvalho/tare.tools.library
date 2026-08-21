# Intake refinement -- lint/format backend shippability (door NEW)

SPEC-116 invariant 2 checklist. Seeds a future decision/spec on how the workspace
lint/format feature (SPEC-147 ruff-as-a-service, `ws_files.lint_content` /
`format_content`) is delivered WITHOUT forcing end users to weaken machine
security to run the harness.

## Request (verbatim)

Owner, 2026-08-06, after `ruff.exe` was blocked mid-session:

> me preocupa a gente fazer a entrega do harness sabendo que as pessoas terao de
> ficar adicionando excecoes no AV pra conseguir rodar [...] se tentar encontrar
> uma alternativa pra shipar com ela [a feature] e nao depender do usuario ficar
> criando regra de exclusao no AV a cada problema que tiver [...] como que as IDEs
> hoje fazem pra nao tripar o AV toda vez que rodam isso.

## Covered-check (which door?)

| Query | Command | Outcome |
|---|---|---|
| records search | `records search "ruff native binary" "smart app control" "lint format backend"` | no hit -- `[]` |
| doc-find | `doc-find "ruff binary antivirus" "vendored native executable" "lint service backend"` | no hit -- 0 files |

Adjacent: **SPEC-147 (chat-workspace)** owns the workspace file surface + the
ruff-as-a-service LINT/FORMAT feature (`ws_files.py` inv 6-9). It does NOT own the
DISTRIBUTION/AV strategy for the native binary that backs it. Decision: **NEW** --
a packaging/shippability concern cross-cutting SPEC-147, unspecified anywhere.

## Goal

One sentence: deliver the workspace lint + format feature so it works on
end-user machines WITHOUT requiring per-machine antivirus/Smart-App-Control
exceptions or a weakened security posture.

## Research findings (2026-08-06, web-sourced)

- **Root cause is Windows Smart App Control (SAC)**, not generic AV. WinError 4551
  / 0x11C7 = "An Application Control policy has blocked this file". SAC blocks
  UNSIGNED native executables with no Microsoft reputation, with extra scrutiny on
  binaries dropped into user-writable paths by scripts -- exactly
  `pip -> .venv\Scripts\ruff.exe` (a 32 MB unsigned Rust binary, the only large
  vendored native exe in the venv).
- **SAC is all-or-nothing**: no per-file exception (unlike SmartScreen's "Run
  anyway"). Historically re-enabling required a Windows reinstall; recent builds
  soften this to a "Reset this PC" flow, but the exact requirement drifts by build
  and is immaterial here -- we never toggle SAC (resolved owner note below). It
  defaults ON only on CLEAN Win11 installs (off on upgraded machines) -- which is
  why most devs never see this.
- **IDEs do NOT dodge it.** The VS Code Ruff extension bundles the SAME unsigned
  `ruff.exe` in a user path (`...\.vscode\extensions\charliermarsh.ruff-*\bundled\
  libs\bin\ruff.exe`) -- identical exposure. Users mostly don't hit it because SAC
  is usually off and the widely-downloaded extension binary accrues Microsoft
  reputation; a freshly pip-installed ruff has zero reputation. When SAC is on, VS
  Code hits the same wall.
- **The real fix is upstream code signing** (Authenticode, ideally EV cert), which
  is Astral's responsibility for ruff's binary; ruff ships GitHub attestations but
  (as of research) not Authenticode signatures. Open upstream ask:
  astral-sh/ruff#8834 "Non-PyPI/Pip Ruff distribution for Windows". We do not
  control Astral's binary.

Sources: Microsoft SAC FAQ (support.microsoft.com, re-verified 2026-08-06 -- current
wording is itself ambiguous on re-enable; see resolved owner note below);
astral-sh/ruff#8834; astral-sh/ruff-vscode bundling.

## Options (ranked, with trade-offs)

1. **Keep ruff + correct graceful degradation** -- a blocked/failed ruff must
   disable lint cleanly, never a false "no diagnostics". **DONE this session**
   (`lint_content` empty-stdout/rc>=2 guard + `ws-lint-blocked-degrades` test).
   Restores inv 9 (gate passes with or without ruff) and lets the harness RUN on a
   SAC machine -- but with lint OFF there. Table stakes, not the full answer.
2. **Pure-Python fallback backend (flake8/pyflakes lint + black format)** as the
   AV-safe path: runs in-process under the already-trusted `python.exe` (no new
   native exe for SAC to block), so the feature still WORKS on locked-down
   machines; ruff stays the default fast-path when its binary runs. Cost: two
   backends, code-space mapping (flake8 F/E-codes ~ ruff), slower, fewer rules.
   NOTE: this is NOT what IDEs do (they eat the SAC risk) and is a functional
   downgrade -- adopt as a FALLBACK, not a replacement.
3. **Bring-your-own / system ruff** via a trusted channel (winget, or install into
   `C:\Program Files\`) instead of pip-into-venv -- less SAC scrutiny (protected
   path + possible reputation). Shifts a setup step to the user/installer.
4. **Self-sign the vendored ruff** (EV cert ~$300/yr + signing infra). Heavy;
   reputation is not instant even when signed; unusual to re-sign a third-party
   binary.
5. **Document the escape hatch**: on a SAC machine, toggle SAC off (now possible
   without reinstall) or BYO signed ruff -- accept lint-off otherwise.

## Recommendation (owner to ratify)

Do NOT rip out ruff. Ship #1 (done) + adopt #2 as an OPTIONAL fallback so the
feature survives on SAC machines, with ruff as the default accelerator. Treat #3
as a packaging follow-up and #4/#5 as documentation. Encode the principle: **avoid
vendoring unsigned standalone native binaries for core features; prefer tools that
run in-process under the trusted interpreter.** (Related exposure to inventory
later: Playwright's downloaded browser binaries for UI tests -- same class, but
test-only, not core.)

## Actors & surfaces

- Actors: `ws_files.lint_content` / `format_content`, the workspace front-end that
  consumes the endpoint, the packaging/install path (pip/venv), `m_workspace`
  scenario.
- Surfaces: internal (lint/format service backend selection); packaging (which
  linters ship + how); no new user CLI surface anticipated.
- UI surface? the editor lint/format UX already exists (SPEC-147); a backend swap
  should be transparent to it -- confirm at spec time.

## Open questions for the human

1. Adopt the pure-Python fallback (#2) now, or ship #1-only (lint off on SAC
   machines) and revisit if real users hit it?
2. If #2: flake8+black, or a lighter pyflakes-only lint (no format)?
3. Packaging direction for #3 (BYO/system ruff) -- in scope or separate?

Next step: owner picks the backend direction (Q1/Q2); then spec from
`specs/SPEC_TEMPLATE.md` seeded by the chosen option. #1 already shipped.

## Update 2026-08-06 (installer / BYO-ruff probe): option #3 does NOT dodge SAC

Owner asked whether the one-click installer could install a SAC-safe ruff
("bring your own ruff"). Investigated:

- `setup.bat` installs only `requirements.txt` (keyring); it does NOT install
  ruff. ruff is lazy-installed by the lint service itself
  (`ws_files.lint_content` -> `uv pip install ruff` on first use).
- **VERIFIED**: `Get-AuthenticodeSignature .venv\Scripts\ruff.exe` -> **NotSigned**.
  ruff carries no Authenticode signature on ANY channel -- pip/uv/winget all ship
  the same unsigned binary (ruff publishes SHA256 + GitHub attestations, which SAC
  does not honor). winget's own validation even shows "[FAIL] Installer failed
  security check" for several ruff versions (microsoft/winget-pkgs).
- SAC blocks by the binary's signature/reputation, NOT by which installer placed
  it -- so installing ruff via any channel (pip, winget, or into a protected path)
  hits the same block. Self-signing in the installer is out: a self-signed cert is
  not in the Microsoft Trusted Root (SAC won't trust it), and an EV cert cannot be
  shipped (its private key can't travel in the installer).

Conclusion: **option #3 (BYO/installer-provisioned ruff) does NOT reliably pass
SAC**, because ruff is unsigned everywhere. "BYO" is useful only in the narrow
sense of PREFERRING a ruff the user has ALREADY accepted on their machine (detect
on PATH), not the installer fetching a fresh one. This STRENGTHENS option #2
(pure-Python fallback: no native exe = nothing for SAC to block) as the durable
feature-preserving path. #4 (self-sign) reconfirmed infeasible for us; the only
clean upstream fix is Astral Authenticode-signing ruff.

## Update 2026-08-06 (consented PS1 -> SAC-exclusion probe): not possible

Owner asked whether a ready-to-run PS1 (user-consented, OS elevation prompt)
could add our project paths/binaries to a SAC exclusion list on demand.
Investigated + verified on the affected machine:

- SAC is ON/enforce here: `Get-MpComputerStatus.SmartAppControlState = On`,
  registry `CI\Policy\VerifiedAndReputablePolicyState = 1`. Confirmed as the
  WinError 4551 source.
- **SAC has NO per-file/per-path exclusion or allow list** (Microsoft + community
  authoritative: "no supported way to let this one specific app through while SAC
  is on"). It is on/off/audit only, by design (tamper-resistant). So a PS1 has NO
  SAC API/list to add a path to -- the idea has nothing to call.
- What a PS1 COULD do, and why each is wrong for us: (a) **disable SAC**
  system-wide via registry+admin -- scriptable but a security ANTIPATTERN (turns
  off protection for the whole machine, not just our paths; a script that disables
  a security feature is malware-shaped, will itself be flagged, and erodes trust
  -- do NOT ship). (b) **Defender AV exclusion** (`Add-MpPreference -ExclusionPath`,
  API present here) -- valid + consentable, but the WRONG LAYER: it does not affect
  a SAC 4551 block (only helps a Microsoft Defender AV quarantine, a different
  scenario). (c) local trusted cert -- SAC does not trust an unsigned binary via a
  local cert store.

Conclusion: a consented PS1 cannot add SAC exclusions (none exist). The only SAC
levers are the user toggling SAC off themselves (now possible without reinstall)
or not running a native exe. A *Defender-AV* exclusion helper could ship for the
Defender-quarantine case, but is out of scope for the SAC block. Third
mitigation avenue closed -> option #2 (pure-Python) remains the durable answer.

## CONVERGED DIRECTION 2026-08-06 (supersedes the options ranking above)

Owner insight: pure-Python is a speed downgrade; ruff is Rust. Investigated the
distinction native-code vs standalone-exe, and found a concrete hybrid.

**Proven facts (verified on the affected machine, SAC On):**
- SAC gates standalone **.exe launches**, NOT in-process native modules. An
  UNSIGNED `_greenlet.cp313.pyd` imports fine under SAC On (numpy/cryptography
  would break everywhere otherwise). So the enemy is the standalone exe, not
  Rust/native code.
- **`ruff-api` (PyPI, PyO3/maturin) ships `_rust.pyd`** and runs IN-PROCESS:
  verified `format_string('x=1') -> 'x = 1'` with no exe spawn -> Rust-speed
  format + isort, SAC-safe. BUT `ruff-api` v0.2.1 exposes ONLY `format_string` +
  `isort_string` -- **no lint/check (diagnostics) API**. The stock `ruff` PyPI
  package is launcher+exe only (no importable module).
- ruff is used in this repo ONLY by the workspace EDITOR service
  (`ws_files.lint_content`/`format_content`) -- a SINGLE buffer, on demand. There
  is NO bulk/repo-wide ruff lint anywhere. So ruff's 25x speed edge (a bulk-run
  property) is irrelevant here; a single-file lint is milliseconds even in pure
  Python.
- Lint-rule coverage (demo on a multi-issue file): **bare pyflakes** catches only
  F-category (F401/F841) -- a real downgrade. **flake8 + flake8-bugbear +
  flake8-comprehensions** catches F + E/W (pycodestyle) + B006 + C4xx -- ruff's
  most-used categories, because ruff RE-IMPLEMENTED those exact flake8 plugins.
  Residual gaps vs ruff: `UP` (pyupgrade), some RUF-native rules; add
  flake8-simplify / pep8-naming / flake8-bandit to narrow further.

**Direction (the ratified backend):**
| Surface | Backend | Downgrade? |
|---|---|---|
| Format + isort | **`ruff-api`** (in-process `_rust.pyd`) | NONE -- it IS ruff |
| Lint fast-path | **`ruff.exe`** when runnable (not SAC-blocked) | NONE -- full 900 rules |
| Lint fallback (SAC-blocked machines) | **flake8 + bugbear + comprehensions** (optionally + simplify/naming/bandit), in-process | small: covers ruff's common categories; misses UP + some RUF-native |
| Floor (no linter at all) | graceful `{ok:false}` (shipped c45c7f6) | lint off, harness still runs |

Net: no standalone exe on the required path, no AV/SAC exception ever needed, and
NO perceptible speed loss (format is native Rust; lint is a single buffer). The
fallback's rule reduction only affects the SAC minority (everyone else keeps full
ruff) and is strictly better than the current lint-off-on-SAC. If `ruff-api` later
adds a `check` API, lint also becomes in-process Rust -- a drop-in upgrade.

**Not bare pyflakes** (owner check 2026-08-06): use flake8 + the ruff-mirrored
plugins so the SAC-fallback stays close to ruff, not a bare-F downgrade.

Next step: spec this hybrid from `specs/SPEC_TEMPLATE.md` -- backend selection in
`ws_files` (ruff-api format; ruff.exe->flake8+plugins lint chain), the linter
dependency set, and the code<->diagnostic mapping so the editor UX is backend-
agnostic. #1 (graceful floor) already shipped.

## Update 2026-08-06 (SAC cold-cache finding -- corrects the "all-or-nothing permanent" framing above)

The SAC framing earlier in this doc is INCOMPLETE and, read alone, causes the exact
failure it should prevent: an agent rebuilt the venv on Python 3.13, `import
tree_sitter` hit a SAC block, and the reflex was to UNINSTALL tree-sitter, destroying
highlighting. Simply retrying the import worked. Ground truth:

- **SAC's reputation check is ASYNC CLOUD, on FIRST TOUCH.** A freshly-installed
  native binary with a new ABI (verified: `_binding.cp313-win_amd64.pyd`) has no
  reputation yet and blocks ONCE; for a widely-deployed lib the cloud reputation
  warms within seconds and the SAME import RETRIED SUCCEEDS. So "all-or-nothing"
  applies to CONFIG (there is still no per-file exclusion list -- true), **not** to a
  binary's fate: a first block is NOT evidence of permanent unsignedness.
- **Two cases, named:** TRANSIENT (reputable-but-cold, e.g. tree-sitter) -> a retry
  resolves it; PERMANENT (`Get-AuthenticodeSignature` = NotSigned, e.g. `ruff.exe`) ->
  retry cannot help, degrade gracefully (c45c7f6). The harness now absorbs the
  TRANSIENT import case automatically via `common.import_native_retry` (bounded retry
  on the unlocalized `"DLL load failed"` prefix), used by `highlight._engine()` and
  `setup_highlight._ensure_deps()`. The `.exe`/ad-hoc/subprocess case -- which is
  never an import and often PERMANENT -- is caught by the `sac_block_advisor`
  PostToolUse hook, which does not retry but INJECTS the correct reflex so no agent
  uninstalls a working dep.
- **Anti-patterns (hard rules):** never uninstall/downgrade the dependency on a first
  block; never toggle SAC off; **Defender AV folder exclusions do NOT cover SAC** --
  PROVEN this session: the venv sat inside an already-AV-excluded folder
  (`C:\projects\universal-agent-harness-prototype`) yet the cp313 `.pyd` was still
  SAC-blocked. AV exclusions and SAC are separate subsystems (consistent with the
  no-exclusion-API probe above).
- **Owner note (RESOLVED 2026-08-06):** whether SAC-off is re-enableable without a
  reset is an EXTERNAL, drifting Windows fact -- the live Microsoft Support FAQ is
  itself ambiguous (both a "Reset this PC" flow and a Security-settings toggle appear
  across current sources) and it changes by build. It is IMMATERIAL to this repo:
  our tooling never toggles SAC, so nothing depends on the answer. We operationally
  treat SAC-off as irreversible -- the conservative assumption (assuming
  irreversibility costs nothing since we never toggle; assuming reversibility and
  being wrong would strand the owner's machine). Rule stands: never toggle SAC off.
