# SPEC-129 — Reviewer evidence bundle (`workflow evidence`, CLI half)

Status: SPEC-129 v2, proposed 2026-07-12, amended v2 2026-07-12 (acceptance:
`testing/scenarios/eb_evidence_bundle.py`).

Door NEW (UX-GA.3 phase 1): covered-check ran `records search evidence bundle` /
`doc-find reviewer evidence` — no existing spec owns a reviewer-facing evidence
assembly; SPEC-121 (`qa-evidence-capsule.md`) stops at the per-worker capsule
contract and never aggregates across a workflow. Intake accepted 2026-07-12; its
criteria seed rules 1–5 and scenarios eb-1..eb-3 below.

**Slice boundary:** this spec covers the CLI + collector ONLY. The panel render
of the bundle is DEFERRED — shipping this spec does NOT close UX-GA.3's GUI
half; that half stays open until a panel spec/amendment lands.

## Goal

A reviewer judging one worker result today re-opens N files (workflow.json,
each result JSON, the reduce result, the records ledger). `workflow evidence
<workflow-id>` assembles the EXISTING handles into one compact deterministic
bundle — pure assembly, no re-run, no LLM — so review cost is O(bundle), and
every body stays exactly where it already lives (HANDLES-NOT-BODIES).

## Applicability

`scripts/harness_lib/evidence_bundle.py` (`bundle(root, wfid, worker_id=None)`)
and the `workflow evidence` verb in `scripts/harness.py`. Reads the workflow
dir via the `workflow_ids.safe_workflow_path` family, worker result JSONs, the
reduce artifacts under `reduce/`, and `records.search`. Does not cover the
panel/GUI render (deferred, see slice boundary), does not write any state, and
does not validate results (that stays with `validate-results`).

## Requirements / invariants (numbered, testable)

1. **Handles, not bodies.** The bundle carries paths plus the capped CQ.2
   capsule (`oracle`, `exitClass`, `artifactPath`, `rerunCmd`) — never worker
   findings, summaries, or artifact bodies. A sentinel body string planted in a
   result file must be absent from the serialized bundle.
2. **Per worker:** `{workerId, status, failureClass, resultPath,
   oracleEvidence}` — status from the workflow entry; `failureClass` and the
   capsule from the result JSON.
3. **Never a crash on absence.** A capsule-less, result-less, or corrupt-result
   worker yields null fields (`oracleEvidence`/`failureClass`/`resultPath` as
   applicable); a missing reduce result yields `riskFlags: null`; a broken
   records index yields `recordsRefs: []`.
4. **Rollup handles:** `harnessResultPath` (when `reduce/harness-result.json`
   exists), `recordsRefs` (titles/refs from `records.search(root, wfid)`), and
   `riskFlags.requiresSecurityReview` from `reduce/reducer.result.json` when
   present.
5. **Declared surface.** The verb parses (`workflow evidence --help` rc 0) and
   `"evidence"` is listed in `.harness/project.json`
   `workflows.supportedWorkflowCommands` (the `workflow-command-surface` gate
   pins CLI ↔ config agreement).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Bundle over N file opens | UX-GA.3 backlog item: reviewer cost O(bundle); CQ.2 capsule made per-worker evidence cheap, this aggregates it |
| Handles, never bodies | records ledger norm (`records._compact`: "full body lives at source+ref"), SPEC-121 rule 4, `.harness/prompts/subagent-contract.md` |
| Pure assembly, no re-run | net-cost-positive observation directive; the capsule already carries `rerunCmd` for the reviewer who wants to re-run |
| Path family reuse | `workflow_ids.safe_workflow_path` is the one WF-dir boundary (same as `harness.py workflow_dir`) |
| One `wsub.add_parser` line | the workflow CLI tree is gate-pinned (`workflow-command-surface`); existing parser literals stay byte-identical |

## Gherkin scenarios

```gherkin
Feature: Reviewer evidence bundle (CLI half)

  Scenario: [eb-1] a capsule-bearing result is bundled as handles only
    Given a fixture workflow whose worker result carries an oracleEvidence capsule and a sentinel body string
    When bundle(root, wfid) runs
    Then the worker entry carries the capsule and the result path, harnessResultPath and riskFlags are populated
    And the sentinel body string is absent from the serialized bundle

  Scenario: [eb-2] capsule-less and broken workers never crash the bundle
    Given workers without a capsule, without a result file, and with a corrupt result file
    When bundle(root, wfid) runs
    Then each worker entry appears with null oracleEvidence (and null resultPath when no file exists) and no exception is raised

  Scenario: [eb-3] the verb is declared and parses
    Given the harness CLI
    When "workflow evidence --help" runs
    Then it exits 0 and "evidence" is listed in project.json workflows.supportedWorkflowCommands
```

## Ceilings (upgrade paths)

- The panel render is deferred (slice boundary above) — the GUI half of
  UX-GA.3 adds a read-only bundle view over this same collector.
- `riskFlags` carries only `requiresSecurityReview` today; extend the dict when
  reviewers need more reduce-level flags (e.g. `requiresReview`).
- `recordsRefs` is a flat title/ref list capped by `records.search`'s default
  limit (10); add paging only if real workflows overflow it.

## Test strategy

- Behaviors to verify: capsule + paths carried; sentinel body absent
  (handles-not-bodies); null fields on capsule-less/missing/corrupt results;
  worker-id filter; determinism (same input, same bundle); CLI declaration.
- Edge cases: worker with no result file; corrupt (non-JSON) result file;
  missing reduce artifacts; empty records index on a bare fixture root.
- Regression risks: the gate-pinned workflow CLI surface — guarded by
  `workflow-command-surface` (parser ↔ `supportedWorkflowCommands`).
- Coverage impact: enforced via `eb_evidence_bundle.py`.

## Validation

- `python testing/scenarios/eb_evidence_bundle.py` — checks `eb-1`..`eb-3`
  against a temp fixture workflow dir (eb-3 shells the real CLI parser); v2 adds
  `eb-4`/`eb-5` against an in-process panel server + the real CLI on a fixture
  workflow planted in the live active dir (m5 tail-fixture pattern, scrubbed).
- `testing/scenarios/ui_e2e.py` — `[ui_e2e:evidence-drill-in]` drives the page's
  real `renderEvidence` + `#ebDlg` in a real chromium (auto-skips without it).
- `feature-spec-conformance:evidence-bundle` green in the spec-pack gate.
- `static-integrity:workflow-command-surface` green (evidence declared + parsed).

## Amendments

### v2 (2026-07-12) — panel drill-in (`GET /api/evidence`), UX-GA.3 phase 2

Supersedes the v1 slice boundary: the GUI half of UX-GA.3 now ships. The panel
gains `GET /api/evidence?workflow_id=&worker_id=` beside `/api/worker`
(token-gated like every route) and a read-only drill-in dialog (`#ebDlg`,
opened from the worker drawer's *evidence* button) that renders the bundle
AS-IS: capsule fields and every path as TEXT, records refs listed — no
client-side assembly, no polling, and the view never fetches artifact bodies
(rule 1 holds end to end). GUI writes NO state; summaries=view. Numbered
requirements continue the list.

6. **CLI ↔ API parity.** For the same `wfid` (and optional worker filter) the
   route returns exactly the bundle `workflow evidence` emits — byte-equal
   under one canonical JSON serialization — because both call
   `evidence_bundle.bundle(root, wfid, worker_id)` on the same root.
7. **Bad ids degrade, never crash.** An unknown or traversal-shaped
   `workflow_id` yields the `/api/records` error shape (`{"error": …}`, HTTP
   200) — no traceback, no 500; a token-less request stays 403 like every
   route.

```gherkin
Feature: Reviewer evidence bundle (panel half, v2)

  Scenario: [eb-4] the API returns the same bundle the CLI emits
    Given a fixture workflow in the live active dir and a running panel server
    When GET /api/evidence?workflow_id=<wfid> and `workflow evidence <wfid>` both run
    Then the two bundles are byte-equal under the same canonical JSON serialization

  Scenario: [eb-5] a bad workflow id yields the error shape, never a traceback
    Given a running panel server
    When GET /api/evidence runs with an unknown or traversal-shaped workflow_id
    Then the response is {"error": ...} with no traceback, and a token-less request is 403

  Scenario: [ui_e2e:evidence-drill-in] the drill-in opens and renders handles as text
    Given the panel page in a real browser
    When renderEvidence runs with a backend-shaped bundle and #ebDlg is shown
    Then the dialog is open and shows the result path and rerunCmd as text
```
