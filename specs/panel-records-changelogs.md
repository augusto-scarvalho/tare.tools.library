# Panel records & changelogs — M5.rec commit timeline + diff viewer

Status: proposed 2026-07-13 (acceptance: testing/scenarios/rec_changelog_panel.py).

Intake (SPEC-116 door NEW): request = "tela de registros e changelogs: painel
com changelogs organizados por commit, filtros por branch, hash, etc,
visualizador do que foi feito (CÓDIGO), e um resumo geral da rodada SOB
DEMANDA (LLM barata)" (`docs/roadmap/screens-memory-records.md` §B).
Covered-check: the ledger ingests commits but the panel exposes only flat
records search — no timeline, no filters, no code view. Decision: **NEW**.
SLICE: M-B1 (timeline + filters) + M-B2 (diff viewer) ONLY — the LLM round
summary is `M5.sum` and target timelines are `M5.tgt`, both OPEN; ledger rows
stay covered by the existing Records dialog (timeline merge deferred with the
gallery polish).

## Goal

A Changelog panel view: commit timeline with branch/text/hash filters, one
click opening the commit's `--stat --patch` body rendered through the
EXISTING diff colorizer — with every byte leaving the API secret-redacted
server-side and every filter validated before it approaches argv.

## Applicability

Applies to `scripts/harness_lib/ui_commits.py` (`commits_snapshot`,
`commit_detail`, `branches`), the `GET /api/commits` / `GET /api/commit`
routes and the `viewChangelog` PAGE section (+ `commitDlg` dialog reusing
`colorizeDiff`). CLI parity is deliberate reuse — `git log` and
`records recent --kind commit` already cover the read path; no new verb.
GUI writes no canonical state.

## Requirements / invariants (numbered, testable)

1. **Validated filters, never flags.** `branch` must match a name regex (no
   leading `-`, no `..`), `sha` must be 7-40 hex; failures degrade to an
   `error` field (HTTP 200, legible), never argv; free-text lands only inside
   a single `--grep=<q>` argv element.
2. **Handles in the timeline.** Rows carry sha/date/author/subject/
   decorations only; subjects are redacted and truncated.
3. **Redacted, capped detail.** `commit_detail` validates the sha, caps the
   body at ~200 KB with an honest `…[truncated]` marker, and rewrites every
   anchored secret shape to first-4+len BEFORE the payload leaves the server
   — the client is never trusted with the raw value.
4. **Reuse the diff renderer.** The dialog body goes through the existing
   `colorizeDiff`; zero new highlight code.
5. **Fail-soft git.** A failing/missing git yields empty lists or a legible
   `unknown commit` error, never a crash (`git -C` degrade pattern).

## Gherkin scenarios

```gherkin
Feature: commit timeline + secret-redacted diff viewer (M5.rec)

  Scenario: [rc-1] the timeline lists, filters and refuses bad filters
    Given a temp repo with three commits
    When commits_snapshot runs bare, with --grep, and with hostile
      branch/sha filters
    Then the full list and the grep hit return, and both hostile filters
      degrade to error fields without reaching argv

  Scenario: [rc-2] the detail is validated, capped and redacted
    Given a commit containing a seeded fake key and one oversized commit
    When commit_detail runs for each plus a flag-shaped and an unknown sha
    Then the patch shows the key only as first-4+len, the oversized body
      truncates with the marker, and both bad shas refuse legibly

  Scenario: [rc-3] the panel reuses the existing diff machinery
    Given the server and page sources
    Then /api/commits and /api/commit route to ui_commits and the Changelog
      view renders the dialog body through colorizeDiff with the filter bar
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Redação server-side em TODO byte da API (nunca confiar no client) | roadmap risk ("diffs and commit bodies can contain keys"); `secret_scan` anchored patterns + first-4+len convention |
| Filtros validados por regex antes do argv | roadmap ("argv injection via filters"); `_WORKER_ID_RE` discipline |
| Reuso do `colorizeDiff`/dialog existentes, zero highlight novo | roadmap M-B2 ("REUSE the highlighter") |
| Formato `%x1f/%x1e` do git, e strip explícito no parse | records.py precedent; bug real: `str.strip()` come `\x1f` (é whitespace em Python) |
| CLI read path = reuso (`git log`, `records recent --kind commit`) | roadmap M-B1 ("no new subcommand for the read path"); ladder rung 2 |
| Resumo LLM (M5.sum) e target (M5.tgt) fora desta fatia | slice discipline; M5.sum gasta dinheiro → trilha ACTIONS própria |

## Test strategy

- Behaviors: temp 3-commit repo — list/grep/hostile filters (rc-1); seeded
  fake key redaction + 300 KB cap + sha refusals (rc-2); wiring + colorizeDiff
  reuse asserts (rc-3).
- Edge cases: empty repo → empty lists; commit with empty decorations parses
  (the `\x1f`-strip bug's regression); limit clamped to [1, 300].
- Regression net: m5_ui_panel + ui_e2e rc0 (panel untouched behaviors);
  module self-check.
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/rec_changelog_panel.py`.

## Validation

- `python testing/scenarios/rec_changelog_panel.py` — rc-1..rc-3 green.
- `python scripts/harness_lib/ui_commits.py` — module self-check.
- `python testing/scenarios/m5_ui_panel.py` + ui_e2e rc0 — panel regression net.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.
