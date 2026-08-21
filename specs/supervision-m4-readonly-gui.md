# SPEC-104 — Read-Only GUI Snapshot (Backlog M4)

Status: **Done** (executed 2026-07-09; retrofitted to the SPEC-116 template 2026-07-13 —
owner decision #4, exiting the legacy freeze). Acceptance:
`testing/scenarios/m4_status_html.py` (seeded state, degradation, invariants, empty state).
**M4.2 verdict: no data gaps found** — all five answers came from existing state sources
(escalations reader, workflow.json + plan.json tokenAudit, quality-state,
protected_files.compare_snapshot, handoff.json); the state layer is sufficient for the
interactive panel, which shipped as **SPEC-114** (planned at the time under the working
number SPEC-114 — that number was never assigned to a document).

Supervision series (SPEC-101…104; the interactive panel followed as SPEC-114). Depends on
SPEC-102 (renders only what the CLI/state already exposes). Evidence base:
`docs/SUPERVISION_UI_IDEATION.md` §4a/§8 Phase 2.

## Goal

`harness.py status --html` generates one static, self-contained HTML page answering the five
supervisor questions at a glance: what is running, what waits on a human, is the last gate green,
is anything drifted, what is the next handoff. Zero new capability — rendering only. Its second
job is adversarial: prove the state files are complete enough for any future panel.

## Rationale & sources

- **Phase discipline (`SUPERVISION_UI_IDEATION.md` §8):** a read-only page has no server, no
  actions, no security surface — the cheapest possible test that the read API (state files) is
  sufficient. Data gaps found here are CLI-layer regressions and must be fixed there (M4.2), not
  patched in the page; otherwise the page becomes a second source of truth.
- **AutoGen Studio (arXiv 2408.15247):** profiling views — message flow, per-agent cost, tool
  invocations — are empirically useful for *debugging*, not just monitoring; include cost data in
  the workflow section from day one.
- **Dark-patterns oversight study (arXiv 2509.10723):** categorize, don't stream; the page groups
  by supervision point, never renders a raw event log.
- **Vibe Kanban:** column/state grouping maps 1:1 onto our workflow states — use that grouping,
  skip the kanban interactivity.

## Applicability

One new rendering path in `scripts/harness.py`. No hooks, no contracts, no state changes.

## Scope

In scope: static HTML from existing state (escalations via the SPEC-102 read path, active
workflows + cost, gate/health from `quality-state.json` + `task-state.json`, protected-file
drift, current handoff summary). Timestamp of generation prominently displayed (it is a
snapshot, not live).

Out of scope: server, polling, buttons, auth, JavaScript beyond trivial collapsing, theming
frameworks, live updates — all SPEC-114 territory (planned then as SPEC-114) or rejected
outright.

## Requirements / invariants

- Self-contained single file (inline CSS, no external requests), writable anywhere via
  `--output <path>`, default under `.harness/state/`.
- Read-only: generation mutates nothing; running it twice on unchanged state yields identical
  content (except the timestamp).
- Degrades calmly: missing/corrupt state file renders as a labeled "unavailable" section, never a
  crash.
- Every datum on the page must come from a documented state source (the §2 table in
  `SUPERVISION_UI_IDEATION.md`); if the page needs something not there, stop and extend the CLI
  first (that is M4.2, and it is the point).

## Gherkin scenarios

```gherkin
Feature: read-only supervision snapshot page

  Scenario: [seeded:running] the five questions answer from seeded state
    Given a state tree with an active workflow, a pending escalation and drift
    When status --html generates the page
    Then the workflow id, escalation and gate status all render

  Scenario: [page:no-external-refs] the page is self-contained
    Given a generated page
    Then it contains no external http(s) references

  Scenario: [invariant:generation-adds-no-git-entries] generation is read-only
    Given a clean working tree
    When the page generates twice
    Then git status is unchanged and content is stable except the timestamp

  Scenario: [degrade:section-unavailable] corrupt state degrades calmly
    Given one corrupted state file
    When the page generates
    Then it still renders with that section labeled unavailable
```

## Design anchors (verified 2026-07-09)

- Read sources: `.harness/state/{task,quality,workflow}-state.json`,
  `.harness/workflows/active/WF-*/`, `.harness/runs/`, `.harness/handoff/`, and
  `tools/hooks/protect_canonical_files.py check` (subprocess, JSON output `{"ok":..., "errors":[...]}`).
- Escalation data: reuse SPEC-102's `escalations` reader — same module, not a reimplementation.
- Windows note: gate output forced UTF-8 (`spec_test_gate.py:33-36` reconfigures streams); do the
  same for the HTML writer (`encoding="utf-8"` explicitly).
- Stdlib-only is a hard constraint (repo-wide policy; the harness is dependency-free).

## Acceptance criteria

- [x] Page renders the five questions' answers with seeded state (≥1 active WF, 1 pending
      escalation, 1 drifted file).
- [x] With `.harness/state/` intact but one file corrupted, page still renders, section marked
      unavailable.
- [x] Generation leaves `git status` and all state files unchanged.
- [x] No external network references in the HTML (grep for `http` in the output, allow only
      documented in-page anchors).
- [x] Any data gap discovered is logged as a SPEC-102 follow-up (none were found), not worked around in the page.

## Test strategy

- Behaviors: golden-ish test — generate against a fixture state tree, assert key strings present
  (WF id, escalation id, gate status, drift path).
- Edge cases: empty state (fresh adoption) renders a meaningful "nothing yet" page; very large
  run history (cap rendered items, state the cap).
- Regression risks: none on existing paths (new subcommand flag only).
- Coverage impact: informational.

## Validation

- `python testing/scenarios/m4_status_html.py` — seeded/degrade/invariant/empty checks green.
- MVP gate: open the generated page and answer, without touching a terminal: what is running,
  what is waiting on a human, is the last gate green, is anything drifted, what is the next
  handoff. All five answerable → done.
- `python scripts/spec_test_gate.py smoke --no-project-commands` green.

## Universal baseline impact

`specs/00-universal/observability-and-operability.md`; `data-protection-and-privacy.md` (the page
may contain repo paths/task text — it stays local, is never published, and lands under
`.harness/state/` which release packaging already excludes — verify against
`scripts/package-release.py` excludes).

## Escalation triggers

Any pressure to add actions/server to this page (that is SPEC-114, the interactive panel);
any data need that would create a new state file.
