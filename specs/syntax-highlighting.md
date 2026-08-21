# Syntax highlighting (native tree-sitter, CLI + panel)

Status: Active

## Goal

Give the harness fast, multi-language syntax highlighting in both the terminal (ANSI) and
the supervision panel (browser), using native/state-of-the-art engines and processing
only what the user is actually looking at — without compromising the zero-dependency,
pipe-safe, loopback-secure core.

## Applicability

Any code/diff the harness prints to a TTY (`emit` JSON, worker output) and any code the
panel renders (worker stdout drill-in). It is an **optional** capability: absent its
engines/assets, every surface degrades to the pre-existing plain text.

## Requirements / invariants

- **Optional + pipe-safe.** The core stays stdlib-only. `harness_lib/highlight.py` returns
  text unchanged when the engine is absent, the stream is not a TTY, or `NO_COLOR` is set;
  `common.emit` output is byte-identical off-terminal and in agent-compact mode.
- **Native engines.** CLI: `tree-sitter` + `tree-sitter-language-pack` (Rust/C, PyO3).
  Panel: `web-tree-sitter` (WASM) with the SAME grammars + `highlights.scm` queries.
- **On demand.** The panel highlights ONLY lines currently in the viewport
  (IntersectionObserver + range-limited query); grammars load lazily on first use.
- **Provisioned, not committed.** The ~21 MB of WASM is fetched + `sha256`-verified by
  `scripts/setup_highlight.py` into a gitignored `vendor/tree-sitter/`; only the pinned
  `manifest.json` is committed. Nothing untrusted (unpinned) is executed.
- **Panel security preserved.** Assets are served over a token-gated, traversal-guarded
  `/vendor/` route; the CSP keeps `default-src 'none'` + loopback, adding only `'self'`
  (same-origin module import) and `'wasm-unsafe-eval'` (WASM instantiation).
- **No HTML injection.** Every character is escaped before token spans wrap it.

## Rationale & sources

tree-sitter is the state-of-the-art incremental parser (Neovim, GitHub, VS Code); a single
grammar ecosystem serves both runtimes (C ext for Python, WASM for the browser), and its
byte-ranged queries make viewport-only highlighting natural. Detection is shebang/extension
based (the language pack has no statistical content classifier), so highlighting engages for
diffs (header path) and shebang'd output and degrades to plain otherwise. Assets: web-tree-sitter
0.26.x + @vscode/tree-sitter-wasm grammars (empirically ABI-verified) + language-pack queries
(validated to compile against each grammar). Governed per `specs/00-universal/dependency-and-supply-chain.md`.

## Test strategy

Deterministic module self-checks + scenarios: the CLI engine (gating, diff coloring,
`emit` byte-identity, engine-absent identity, multi-language coloring, detection) and the
panel wiring (page markers + CSP, the token-gated `/vendor` route, server-side language
detection). The real-browser viewport-only behavior is a Playwright test that runs where
Playwright is installed and green-skips otherwise.

```gherkin
Feature: native syntax highlighting
  Scenario: [hl:emit-byte-identical]
    Given a non-TTY stream
    When the harness emits a JSON payload
    Then the output equals the plain json.dumps (no ANSI)

  Scenario: [hl:gating-non-tty]
    Given a stream that is not a TTY
    Then color is disabled

  Scenario: [hl:diff-structural]
    Given diff-shaped text
    Then the +/-/hunk/header lines are colored without any engine

  Scenario: [hl:absent-identity]
    Given the optional engine is absent
    Then highlight returns the text unchanged

  Scenario: [hl:page-wiring]
    Given the panel page
    Then it carries the tree-sitter highlighter, the viewport observer, and the CSP for WASM

  Scenario: [hl:vendor-route]
    Given a valid session token
    When the client requests the vendor manifest
    Then it is served as JSON over the /vendor route

  Scenario: [hl:server-detect]
    Given shebang'd worker output
    Then the panel detects a vendored grammar language for it
```

## Validation

`spec-pack` runs `feature-spec-conformance:syntax-highlighting`. The Gherkin scenarios
above resolve to named checks in `testing/scenarios/hl_highlight.py` (CLI engine +
`emit`) and `testing/scenarios/m5_ui_panel.py` (panel wiring, `/vendor` route, server
detection); the browser viewport behavior is covered by `testing/ui/test_panel_e2e.py`
(`e2e:hl-renders` / `e2e:hl-on-demand` / `e2e:hl-scroll`). Provisioning is exercised by
running `scripts/setup_highlight.py` (sha256-verified fetch).
