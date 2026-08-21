# SPEC-147 — Chat workspace: CM6 diff pane (vibe) + IDE (copilot)

Status: SPEC-147, proposed 2026-07-17 (acceptance:
`testing/scenarios/m_workspace.py`; intake: `chat-workspace.intake.md`;
research: `docs/research/ide-embedded-gui.md`; supersedes the roadmap claim
`docs/roadmap/chat-workspace.md`).

## Goal

The chat panel's empty side space becomes an IDE-grade workspace on a vendored
CodeMirror 6 surface. Three view modes on one pillbtn: **chat** (today's
panel, untouched default), **vibe** (3/5 chat + 2/5 diff pane opened from diff
chips), **copilot** (1/2 chat + 1/2 editor with syntax highlight, ruff
diagnostics, editing, and a floating project explorer overlay at 1/4 screen).
Everything provisions itself: the end user only launches `ui.bat`/`ui.sh`.

## Applicability

`scripts/harness_ui_page.py` (markup, importmap boot, mode state, chip ⧉),
NEW `scripts/harness_ui_page_workspace.py` (WS_JS/WS_CSS, spliced like MD_JS),
`scripts/harness_ui.py` (routes: `/vendor/` widening, `/api/chat/diff`,
`/api/ws/file`, `/api/ws/tree`, `/api/lint`), `scripts/harness_lib/ui_actions.py`
(`ws-file-*` verbs + in-process `ws:` handler), NEW
`scripts/harness_lib/ws_files.py` (path confinement + file ops),
`scripts/harness_lib/stream_json.py` (`diffFull`), `scripts/harness_lib/chat_engines.py`
(diff ring), `scripts/setup_highlight.py` (generalized provisioner +
`ensure_vendor()`), `ui.bat`/`ui.sh`, `vendor/codemirror/` (manifest +
gitignored assets). Does NOT change: chat transport contracts, the router,
tree-sitter chip highlighting, any CLI verb.

## Requirements / invariants (numbered, testable)

1. **Additive modes.** `harness.panel.wsMode ∈ {chat, vibe, copilot}`,
   persisted in localStorage, default `chat`; in chat mode the panel DOM and
   behavior are unchanged. Splits: vibe 60/40, copilot 50/50 (flex-basis),
   user-resizable via the reattached `setupSplit` divider, per-mode keys.
2. **Vendored, pinned, CSP-clean.** All CM6/lezer assets fetched from the npm
   registry at provision time, per-file sha256 pins in
   `vendor/codemirror/manifest.json`, gitignored on disk, served ONLY via the
   token-gated `/vendor/codemirror/` route (first path segment allowlisted to
   `{tree-sitter, codemirror}`; traversal guard and ext allowlist stay). The
   page keeps `connect-src 'self'` — zero external requests at runtime.
3. **No-build importmap.** Bare specifiers resolve via a STATIC
   `<script type="importmap">` in the page `<head>` (a map inserted after any
   module load is ignored by Chromium), its URLs token-spliced server-side;
   all CM6 loads are lazy dynamic imports (HL-IIFE pattern). No node/esbuild
   toolchain enters the repo.
4. **Zero-touch bootstrap.** `ui.bat`/`ui.sh` run setup when `.venv` is
   missing. `harness.py ui` startup calls `ensure_vendor()`: satisfied
   `resolved.json` ⇒ no network, ~ms; otherwise auto-provision every
   `vendor/*/manifest.json`. Provisioning failure NEVER blocks serving —
   degrade mode + retry next launch. Optional IDE deps (ruff) auto-install
   with the same graceful-offline rule.
5. **Full diff, not the chip cap.** `_attach_render_fields` emits uncapped
   `diffFull {file, old, new}`; the session bridge strips it from SSE into a
   bounded per-session ring (last 50 tool ids); `GET /api/chat/diff?session=&id=`
   serves it. Chips keep DIGEST_CAP/DIFF_CAP payloads. Pane miss ⇒ degrade to
   the capped chip diff + truncation notice.
6. **Write discipline.** Editor/explorer mutations are ACTIONS verbs
   (`ws-file-save`, `ws-file-create`, `ws-file-rename`, `ws-file-delete`),
   `mutating: True`, executed by an in-process `ws:` handler (rerun-gate
   precedent) — inheriting `confirm: true`, the human-only backstop, and the
   gate-in-flight guard. Every ACTIONS change updates `m5_ui_panel.py`
   head_actions in the SAME commit.
7. **Confinement.** `ws_files.resolve_confined`: repo-relative POSIX input
   only; symlink-resolved result must land under repo root; deny `.harness/`,
   `.git/`, `vendor/`, and the protected-instruction registry (reuse the
   `tools/hooks/protect_canonical_files.py` matcher). `testing/` remains
   writable. Reads refuse >2MB or binary.
8. **Conflict-safe saves.** Save carries `baseSha` (sha256 of the loaded
   content); disk mismatch ⇒ `{ok:false, conflict:true}` and the front offers
   reload or explicit second-confirm overwrite. No silent clobber of
   agent-made edits.
9. **Ruff as a service.** `POST /api/lint` (read-shaped, no ACTIONS entry):
   `{path, content}` → `python -m ruff check --output-format json
   --stdin-filename <path> -` on stdin, 10s timeout, `.py` only →
   `{ok, diagnostics[{line,col,endLine,endCol,code,message}], ruff}`. Ruff
   absent ⇒ `{ok:false}` and the editor disables lint. The gate never
   requires ruff.
10. **Graceful degrade everywhere.** Assets unprovisioned: vibe pane renders
    the capped colorized diff; copilot editor is inert with a "run ./setup"
    hint; the panel never bricks. Asserted in e2e.
11. **Autocomplete seam only.** Extension assembly stays in one
    `buildExtensions(lang)`; ghost text later = one extension + one
    read-shaped POST. Nothing else built now.

## Rationale & sources

- Editor selection (CM6 over Monaco/from-scratch/Ace): evidence matrix in
  `docs/research/ide-embedded-gui.md` — Sourcegraph production migration
  (−43% JS), Monaco CSP issues (#4927, keycloak #32901), CM6 million-line
  design, @codemirror/merge chunk accept/reject, ghost-text reference impls.
- No-build importmap vendoring: repo is Python-only (no package.json);
  tree-sitter precedent is fetch+sha256, zero build; importmaps are baseline
  in all supported browsers.
- Writes as ACTIONS verbs: inherits confirm/backstop/gate-guard from
  `run_action` and keeps the write surface under the m5 frozen set;
  in-process handler follows the `rerun-gate` no-argv precedent (argv would
  hit the Windows ~32KB cap on file content).
- Zero-touch bootstrap: owner requirement 2026-07-17 (intake follow-up) —
  parity with how the harness already self-manages Python deps.

## Gherkin scenarios

```gherkin
Feature: chat workspace modes

  Scenario: [ws-1] vibe mode opens a full diff from a chip
    Given the panel in vibe mode and a turn that edited a file
    When the user clicks the chip's open-in-pane button
    Then the 2/5 pane renders the uncapped diff in the CM6 merge view
    And the chip's own collapsed preview is unchanged

  Scenario: [ws-2] pane miss degrades to the capped diff
    Given a diff chip whose id is no longer in the session diff ring
    When the user clicks open-in-pane
    Then the pane shows the chip's capped diff with a truncation notice

  Scenario: [ws-3] copilot save requires confirm and detects conflicts
    Given a file opened in the copilot editor with baseSha S
    When the file changes on disk and the user saves
    Then the save returns a conflict instead of writing
    And a save without confirm:true is refused

  Scenario: [ws-4] zero-touch launch
    Given a fresh clone with no vendor assets provisioned
    When the user runs ui.bat or ui.sh
    Then setup and vendor provisioning run automatically before serve
    And if provisioning fails the panel still serves in degrade mode

  Scenario: [ws-5] explorer file ops are confined
    Given the copilot explorer overlay expanded to 1/4 screen
    When the user creates, renames, and deletes a file under a repo subdir
    Then each op requires confirm:true and succeeds
    And the same ops on .harness/, .git/, vendor/ or a protected file are refused
```

## Milestones

M1 vibe (vendoring + bootstrap + pane, no ACTIONS change) → M2 copilot
(editor + `ws-file-save` + `/api/lint`; first m5-coupled commit) → M3 explorer
(`/api/ws/tree` + create/rename/delete; second m5-coupled commit). One
revertable commit per milestone, each through `validate --staged`.
Gherkin ids are tagged (`[ws-N]`) in the same commit that lands the matching
`check()` in `m_workspace.py`/`ui_e2e.py` — M1: ws-1/ws-2/ws-4; M2: ws-3;
M3: ws-5 (spec-pack's orphan-id check enforces this pairing).

## Test strategy

- Behaviors to verify: mode additivity + persisted splits (ws-1 context, inv 1);
  full-diff pane vs capped chips (ws-1/ws-2, inv 5); vendor route widening +
  pins + importmap ordering (inv 2-3); zero-touch bootstrap fast-path/offline
  (ws-4, inv 4); save confirm/conflict/confinement (ws-3, inv 6-8); ruff
  endpoint degrade (inv 9); explorer ops confinement (ws-5, inv 6-7).
- Edge cases: diff-ring eviction (miss ⇒ degrade); provisioning failure
  offline; binary/>2MB reads; symlink escape; save mid-gate; ruff absent.
- Regression risks: PAGE splice ordering (string-asserted); m5 head_actions
  drift (same-commit rule); stream_json caps self-check (:578-583 pattern)
  must keep chips capped while diffFull is uncapped; chat mode byte-compat.
- Coverage impact: enforced via `testing/scenarios/m_workspace.py` (grows per
  milestone: M1 ws-1/2/4, M2 ws-3, M3 ws-5) + `ui_e2e.py` additions.

## Validation

- `python testing/scenarios/m_workspace.py` green (checks tagged `ws-1..ws-5`
  as milestones land) + `spec-pack` green (this spec's `:sections`/`:gherkin`).
- `python testing/scenarios/m5_ui_panel.py` green after every ACTIONS change
  (head_actions same-commit rule).
- `python testing/scenarios/ui_e2e.py` green (green-skips without Playwright);
  full CM6 interaction e2e is local-only — the gate stays hermetic/offline.
- Manual per milestone: launch `ui.bat`, drive chip→pane (M1), edit→save +
  lint markers (M2), explorer create/rename/delete (M3) in the real panel.
- Each milestone lands through `validate --staged` (background) + one
  revertable commit.

## Amendments

### v2 — chat-tab hosting + split mode selector (owner feedback 2026-07-17)

- There is NO header mode button (the M1 pillbtn is removed). The nav's
  leftmost tab is labeled **Chat** (it was never "Panel") and HOSTS the
  workspace: clicking it while the chat view is already showing toggles the
  pane, restoring the last vibe/copilot mode (`harness.panel.wsLast`,
  default vibe); ✕ still closes; chip ⧉ still auto-opens vibe.
- The vibe/copilot toggle is a VISUAL split selector `#wsModeSel` at the
  right end of the wsbar (after ⇔ and ✕): one pill split in half, the active
  half visually prominent, one distinct accent color per mode; keyboard
  operable with `aria-pressed` semantics. Contract: halves carry
  `data-mode="vibe|copilot"`, a click calls `WS.setMode(mode)`, and the host
  calls the global `syncModeSel(mode)` on every non-chat mode change.
- Per owner instruction, the selector widget itself is authored by
  **gpt-5.6-sol (xhigh)** via the codex executor; the overseer integrates and
  reviews. Acceptance: e2e:ws-modes drives tab-toggle + selector flip.

### v3 — equal split, strict mode surfaces, IDE minimum kit (owner 2026-07-17)

- **Both modes split 1/2 chat + 1/2 IDE** (amends inv 1's 60/40 vibe).
- **Strict surfaces**: vibe is READ-ONLY diffs — flipping copilot→vibe clears
  any open editor (never an editable surface in vibe) and the file-selection
  bar + explorer toggle are unreachable outside copilot; flipping
  vibe→copilot clears any stale diff; chip ⧉ enters vibe from ANY mode.
- **Selector diagonal cut**: the split seam is diagonal (clip-path overlap on
  the Sol widget), not a straight divider.
- **IDE minimum kit** (all assembled in `buildExtensions` per inv 11):
  syntax highlight per language (one-dark highlight style, vendored
  `@codemirror/theme-one-dark` — also applied to vibe diff views);
  Tab indents / Shift-Tab dedents (`indentWithTab`); find & replace with
  text + regex (`@codemirror/search` panel, Mod-f); formatting — .py via
  read-shaped `POST /api/format` (`ruff format` on stdin, same graceful
  contract as `/api/lint`), other languages reindent the selection
  client-side (Mod-Shift-f); per-language linters — .py via ruff,
  .json via `jsonParseLinter`; plus bracket matching, close-brackets,
  fold gutter, active-line and selection-match highlights.
- Ceiling: other-language linters/formatters = LSP lane, fase 2 with
  autocomplete.

### v3.1 — boot in vibe, one shared width, true toggle (owner 2026-07-17)

- The panel **boots with the workspace open in vibe** (chat-tab toggle and ✕
  still close it; reopen restores the last ws mode within the session).
- **One shared pane width** for both modes (`harness.panel.wsW`): the
  per-mode keys made the split visibly jump on vibe↔copilot flips (stale
  60/40-era values persisted per mode). Equal halves stay equal.
- The selector is a **true toggle**: clicking EITHER half — active or not —
  alternates vibe↔copilot (physical-switch semantics); visuals unchanged.

### v4 — IDE shard write path (owner-approved 2026-07-23)

- Invariants 6-8 now land workspace mutations in the IDE shard; see SPEC-114's
  2026-07-23 amendment. The existing invariants remain unchanged.
