# SPEC-171 — Conditional codex hook-trust bypass (verify-then-spawn)

Status: SPEC-171, proposed 2026-07-28 (acceptance: `testing/scenarios/chb_codex_hooks_bashfree.py`).

## Goal

Harness-spawned codex lanes run the harness's own hooks without a per-change
human trust acceptance, by passing codex's `--dangerously-bypass-hook-trust`
flag — but ONLY after proving, at spawn time, that `.codex/hooks.json` is
exactly the committed canonical render of `.harness/capabilities.json`. The
trust decision moves from "owner eyeballs each hooks.json change in a TUI
prompt" to "the harness's own gated pipeline vouches for its own output";
anything the pipeline did not produce keeps today's behavior (codex skips it).

## Applicability

The programmatic codex spawn seam (`workflow_spawn_command_for_prompt` in
`scripts/harness.py`) and hand-typed codex recipes via `harness.py agents
codex-trust`. Does not cover: interactive human codex sessions (codex's own
trust prompt remains their path), claude-side hooks (no trust gating exists),
and persisting codex `trusted_hash` entries (undocumented recipe — explicitly
out of scope).

## Requirements / invariants (numbered, testable)

1. **Grant needs all three legs.** The flag is added to a codex spawn argv only
   when (a) `.codex/hooks.json` re-renders to itself from `capabilities.json`
   (`_render_vendor_hooks` fixed point), (b) every wired inner hook command's
   `_script_of` is a manifest-managed script, and (c) `git diff --quiet HEAD`
   is clean for BOTH `.harness/capabilities.json` and `.codex/hooks.json`.
2. **Leg (b) reads raw commands.** The render preserves non-managed entries and
   the row normalizer drops commands with no `.py` token, so (a) alone or a
   normalized-row scan would bless hand-added entries (including e.g.
   `cmd /c evil.bat`). Raw command strings are checked.
3. **Fail-closed.** Missing/unreadable manifest or hooks file, git absent,
   subprocess timeout — every error path denies the flag. This is the inverse
   of the parity audit's degrade-open collectors, on purpose: the audit
   observes, this check arms an unsandboxed execution path.
4. **Loud deny.** A denied spawn emits one stderr line naming the reason; the
   lane still launches (hooks silently skipped — today's behavior).
5. **Root of trust protected.** `.harness/capabilities.json` is in the
   protected-files registry (SPEC-148 OS locks in write workspaces; merge plan
   blocks `protected-path-modified`).
6. **One shared implementation.** The spawn seam and the `agents codex-trust`
   verb call the same `agent_parity.codex_trust_grant`; the verb's `--flag`
   mode prints the flag (or nothing) for hand-typed recipes.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Bypass flag instead of writing trusted_hash | codex offers no CLI trust verb; the hash recipe is undocumented (`collect_codex_trust` docstring); flag help text names this exact use ("automation that already vets hook sources") |
| Conditional, never blanket | owner decision 2026-07-28: "não podemos dar bandeira branca pra algo estranho que não seja nosso" |
| Clean-vs-HEAD leg | only gate+review+committed wiring counts as pipeline output; uncommitted edits are unvetted by construction |
| Fail-closed stance | SessionStart hooks run BEFORE the codex sandbox is applied (measured 2026-07-28, two probe lanes): a wrong grant executes repo-supplied commands unsandboxed as the user |
| Raw-command leg (R2) | `_render_vendor_hooks` deliberately preserves non-managed entries (pair-renderer-metadata); `_normalize_settings_hooks` drops `.py`-less commands — both are grant-check blind spots found at design time |
| Protect capabilities.json | it is the root the check derives trust from; an unprotected root moves the tamper target one file up |

## Ceilings (upgrade paths)

- `adopt()` (fresh-repo seeding) writes `capabilities.json`, which is now
  registry-protected: bootstrap on a brand-new adoption goes through
  `protect_canonical_files.py edit`. Acceptable — adoption is one-time and
  owner-driven; automate if adoption frequency ever grows.
- The grant reads working-tree state at spawn time; a tamper in the window
  between check and codex reading the file is not defended. Same TOCTOU class
  as every advisory guard here; revisit only with evidence.

## Test strategy

- Behaviors to verify: grant on a clean canonical root; deny on committed
  non-manifest entry; deny on managed-hook placement drift; deny on dirty
  files; spawn argv consistency with the grant verdict.
- Edge cases: command with no `.py` token; unreadable hooks.json; empty
  manifest.
- Regression risks: `agents pair` idempotency (the check must hold exactly on
  pair's own output); spawn builder argv shape (flag spliced before `{prompt}`).
- Coverage impact: enforced via `chb_codex_hooks_bashfree.py`.

## Validation

`python testing/scenarios/chb_codex_hooks_bashfree.py` — checks `chb-5`
(grant), `chb-6` (deny: tampered wiring, both variants), `chb-7` (deny: dirty
vs HEAD), `chb-8` (spawn argv ↔ grant verdict consistency) — plus `spec-pack`
green. Hand-mutation evidence: builder splice removed → chb-8 red; leg (b)
removed → chb-6 red; leg (c) removed → chb-7 red.

## Amendments

### v2 (2026-07-28) — the claude leg: pre-seeded workspace trust

Owner reframed the goal: the harness is meant to become the daily driver, so
*any* hand-accepted vendor dialog is friction to remove, not just codex's.
Measured first (`claude --help`, `~/.claude.json`, 2026-07-28): harness-spawned
claude lanes already have zero friction — `claude -p` skips the workspace trust
dialog outright — and claude's trust is per-DIRECTORY (`hasTrustDialogAccepted`
in `~/.claude.json`), accepted once, not per-hook-hash like codex. So the
remaining friction is exactly one interactive acceptance per fresh
clone/machine. Owner asked for it to be pre-seeded anyway.

7. **Same grant, second vendor.** `vendor_trust_grant(root, vendor)` holds R1-R3
   for `.claude/settings.json` too (the renderer already preserves the
   `permissions` block); `codex_trust_grant` is its codex leg. The harness
   answers a vendor security prompt on the operator's behalf ONLY for wiring it
   can prove is its own committed render.
8. **Both separator forms.** The write targets `<root>` spelled with `/` AND
   `\`. `~/.claude.json` carries both for one project (measured: two PrintIntel
   entries); every recent entry uses `/`, so that is the live form and the
   backslash twin is legacy. Writing one form only risks a silent no-op after a
   vendor change.
9. **Denied writes nothing.** A denied grant leaves `~/.claude.json`
   byte-identical and the dialog exactly as today: the fail-closed path degrades
   to the status quo, never to a blind trust. Applies only with `--apply`
   (dry-run reports).

| Decisão | Fontes |
|---|---|
| Do it for claude even though lanes need nothing | owner 2026-07-28: harness as daily driver, "é um trabalho a menos para o usuário" |
| NOT via `--dangerously-skip-permissions` | measured: that flag bypasses ALL tool permission checks, not hook/workspace trust — a far wider blast radius than codex's hook-scoped flag; it blocked two commands in this very session |
| Gate the write on the same three legs | consistency with R1-R3; a fresh clone (the target case) passes by construction, so the gate costs nothing where it is meant to be used |
| Both path spellings | measured duplicate-form entries in the live `~/.claude.json` |

Ceiling: a LIVE claude session holds `~/.claude.json` state in memory and may
rewrite it, so the intended moment is adoption/bootstrap (fresh clone, no
session open); the call is idempotent, so re-running repairs a clobber. Upgrade
path if that ever bites: detect a running session and refuse.

Validation: `chb-9` (claude leg grants clean / denies tampered), `chb-10`
(apply writes both forms, preserves unrelated state, idempotent), `chb-11`
(denied grant leaves the user state byte-identical) — hermetic temp repo + temp
HOME, the operator's real `~/.claude.json` untouched by the scenario. Mutation
evidence: single-path-form → chb-10 red; grant gate bypassed → chb-11 red;
vendor param ignored → chb-9 red.
