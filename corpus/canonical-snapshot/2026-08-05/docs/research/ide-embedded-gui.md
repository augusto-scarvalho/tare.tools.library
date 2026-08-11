# Research round — embedded IDE/editor for the chat GUI (vibe + copilot modes)

Status: Phase 1 (Discover) in progress. Owner request 2026-07-17; extends
`docs/roadmap/chat-workspace.md` (the claim on the freed side columns).

## Question

Which editing surface should power the chat workspace's two modes —
**vibe** (3/5 chat + 2/5 advanced diff viewer, opened from diff chips) and
**copilot** (1/2 chat + 1/2 full IDE: syntax highlight, lint, diffs, real
editing, floating file explorer at 1/4 overlay) — adopt an existing embeddable
editor or build on our vendored tree-sitter stack from scratch?

## Success criteria (from owner + existing constraints)

1. **Responsividade first**: fast load, fast typing latency, handles big files;
   the panel is a single self-contained page — startup weight matters.
2. **CSP-compatible vendoring**: `default-src 'none'; connect-src 'self';
   style-src 'unsafe-inline'; script-src 'self' 'unsafe-inline'
   'wasm-unsafe-eval'` — no CDN, assets pinned under `vendor/` behind the
   token-gated `/vendor/` route (tree-sitter precedent).
3. **Extensibilidade**: room to grow (LSP later, more languages, themes).
4. **AI autocomplete path**: inline/ghost-text completions feedable by our own
   backend in copilot mode.
5. **Diff parity**: one surface serves both the vibe-mode diff viewer (chip →
   full diff) and copilot-mode editing; unified + side-by-side.
6. **Write discipline**: editing routes through an allowlisted server path with
   `/api/action`-style token confirm (roadmap constraint — unchanged).
7. **Linter**: project's ruff via server endpoint surfaced as editor
   diagnostics (roadmap constraint — no JS reimplementation).

## Declared budget

Single-orchestrator round (no worker waves): Phase 1 web discovery + Phase 2
matrix ≈ 60k tokens. Develop/critique waves only if the Define gate demands a
deeper bake-off (not expected for a lib-adoption question).

## Evidence register (Phase 1, 2026-07-17)

| claim | source | type | year | method | limitations | confidence | maturity |
|---|---|---|---|---|---|---|---|
| [web] Monaco = 5-10MB uncompressed; CM6 core ≈300KB, tree-shakeable from ~50KB | pkgpulse.com/guides/monaco-editor-vs-codemirror-6-vs-sandpack-in-browser-2026 + npm-compare.com/codemirror,monaco-editor | guide/registry | 2026 | secondary comparison | not a measured benchmark by us | moderada | produção |
| [web] Monaco is unusable on mobile; CM6 has native touch/screen-reader support | agenthicks.com/research/codemirror-vs-monaco-editor-comparison + replit blog code-editors | comparison/blog | 2023-2025 | vendor experience reports | secondary | moderada | produção |
| [web] Sourcegraph dropped Monaco: −43% JS (6MB→3.4MB), Monaco was 2.4MB = 40% of search-page JS; global config blocks multi-instance; theming needs hard-coded hex | sourcegraph.com/blog/migrating-monaco-codemirror | blog (primary migration report) | 2022 | production migration | one org's stack | forte | produção |
| [web] Monaco under strict CSP needs: self-hosted codicon font (`font-src`), worker config via `MonacoEnvironment.getWorker`, and has open inline-style CSP violations (#4927); keycloak considered replacing it over CSP (#32901) | github.com/microsoft/monaco-editor/issues/4927 + github.com/keycloak/keycloak/issues/32901 | issue tracker | 2024-2025 | reported defects | workaroundable | forte | produção |
| [web] @codemirror/merge ships BOTH side-by-side MergeView and unifiedMergeView with per-chunk accept/reject (`acceptChunk`/`rejectChunk`, buttons on by default, `accept`/`revert` user events) | github.com/codemirror/merge + npmjs.com/package/@codemirror/merge | repo/docs | 2025 | official docs | — | forte | produção |
| [web] CM6 handles multi-million-line docs by design (viewport rendering, work-limited parser, "avoid performance cliffs" philosophy) | codemirror.net/examples/million/ + marijnhaverbeke.nl/blog/codemirror-6-beta.html | official demo + author blog | 2022-2025 | live demo | demo ≠ our workload | forte | produção |
| [web] Ghost-text AI completion over a custom backend exists as ≥3 independent CM6 extensions (asadm/codemirror-copilot, marimo-team/codemirror-ai w/ next-edit prediction, val-town/codemirror-codeium) | github repos cited | repo | 2023-2025 | community impls | community-maintained | moderada | protótipo→validado |
| [web] Official @codemirror/lsp-client exists (completion, hover, diagnostics via setDiagnostics/@codemirror/lint); plus mature community codemirror-languageserver | github.com/codemirror/lsp-client + FurqanSoftware/marimo forks | repo | 2025 | official + community | young official pkg | moderada | protótipo (official) / validado (community) |
| [repo] Panel CSP: `default-src 'none'; connect-src 'self'; style-src 'unsafe-inline'; script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'` — no fonts, no CDN; token-gated `/vendor/` static route + pinned manifest already serve tree-sitter WASM | scripts/harness_ui_page.py:14-15, scripts/harness_ui.py:140-173, vendor/tree-sitter/manifest.json | repo | 2026 | read | — | forte | produção |
| [repo] Roadmap constraints pre-exist: vendoring precedent, editor-as-WRITE-surface token discipline, ruff-via-endpoint linter | docs/roadmap/chat-workspace.md | repo | 2026-07-17 | read | — | forte | — |
| [judgment] CM6 highlight uses Lezer, not tree-sitter — vendored tree-sitter stays for chat chips; CM6 brings its own per-language grammar bundles (tens of KB each); a tree-sitter→CM6 bridge exists in community but is not needed for v1 | referência: judgment | — | — | — | duplication of grammar assets, small | teórica | — |

## Evidence matrix → decision (Phase 2)

| criterion | CodeMirror 6 | Monaco | from scratch (tree-sitter) | Ace |
|---|---|---|---|---|
| responsividade (load) | ~300KB core, modular | 5-10MB + workers + font | n/a (years of work) | mid |
| responsividade (typing/large files) | million-line by design | good | unknown, ours to build | weaker |
| CSP/vendoring fit | styles inline-injected (allowed), no fonts, no required workers; one esbuild pin under `vendor/codemirror/` | needs `font-src 'self'` + worker env + known inline-style violations | already fits | fits |
| diff (vibe mode) | side-by-side + unified + chunk accept/reject built-in | DiffEditor built-in | build it | plugin, weak |
| edição (copilot mode) | full editing surface | full editing surface | IME/undo/a11y = ours | dated |
| AI autocomplete path | ghost-text ext + 3 reference impls, custom-fetch friendly | inline completions API (mature) | ours | none |
| extensibilidade (LSP/lint) | @codemirror/lint + official lsp-client | monaco-languageclient | ours | poor |
| mobile/touch | native | unusable | ours | poor |
| license | MIT | MIT | — | BSD |

**Operations** (set-based): CodeMirror 6 → **núcleo**. Monaco → **rejeitada**
(CSP friction + 10-20× asset weight buys nothing we need; its one edge —
TS IntelliSense — is off-mission). From scratch → **rejeitada** (editing
surface = IME/undo/selection/a11y years; violates responsividade). Ace →
**rejeitada** (legacy, weak diff/AI ecosystem). Contingência real if CM6
fails validation: Monaco self-hosted is the fallback, documented here.

## Briefs (Define output — human gate)

1. **Diff-in-chat (vibe mode)**: user clicks a diff chip → 2/5 right pane
   renders the full diff (unified default, side-by-side toggle) without
   leaving the chat. Actors: owner reviewing turns. Constraints: read-only,
   reuse turn-diff events, CSP-vendored assets. Success: chip→pane <100ms
   perceived, byte-parity with `git diff` content.
2. **Edit-in-chat (copilot mode)**: 1/2 IDE pane with highlight, ruff
   diagnostics, real editing; saves route through an allowlisted token-gated
   write endpoint. Success: type latency imperceptible; a save is auditable
   like `/api/action`; lint markers from the project's real ruff.
3. **Project navigation (floating explorer)**: toggle button inside the IDE
   pane edge; expanded = 1/4-screen overlay; tree navigation + open/create/
   rename/delete with the same write discipline. Success: full file ops
   without leaving chat; every mutating op token-confirmed.
4. *(extension of 2, later)*: **AI ghost-text autocomplete** fed by our own
   backend via the CM6 inline-completion extension pattern.

## Gate status

Awaiting owner approval of: núcleo = CodeMirror 6 (vendored, esbuild-pinned),
briefs 1-3 to SPEC-116 intake as one write-capable spec. Develop/critique
waves judged unnecessary for a lib-adoption question — evidence converged
(uma fonte primária de migração em produção + issues oficiais + docs oficiais).
