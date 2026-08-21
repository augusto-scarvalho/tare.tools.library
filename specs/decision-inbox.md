# SPEC-145 — Decision inbox: plain-language human decisions in CLI + GUI

Status: SPEC-145, proposed 2026-07-15 (acceptance: `testing/scenarios/di_decision_inbox.py`).

## Goal

Every pending human decision in the harness — triage an intake demand
(`spec`/`backlog`/`discard`/`experiment`/`done`), or resolve an escalation —
must surface as a plain question with selectable answers ("Discard demand
e487ab73d144? [Yes][No]") in BOTH the CLI and the browser panel, so the owner
never has to compose raw harness subcommand grammar. The decision inbox is a
read-only collector over the existing state plus one allowlisted apply path; it
reuses the intake queue, the escalation ledger, and prompt_kit — it invents no
new store and no new write path.

## Applicability

`scripts/harness_lib/decision_inbox.py` (the collector + apply path), the
`harness.py decide` CLI verb, and the panel Decisions card
(`ui_panel.state_snapshot` source, `ui_actions.ACTIONS["intake-decide"]` gate,
`harness_ui_page.py` render). It covers the two v1 decision sources: pending
intake entries and pending escalations. It does NOT cover owner-typed approval
tokens (`--approve-writes`) or any `--force`/`scrub` variant — those stay
CLI-only and typed — nor i18n (question strings are plain English v1), nor
remote/multi-user surfaces.

## Requirements / invariants (numbered, testable)

1. **Read-only collector.** `pending_decisions(root)` returns one row per pending
   decision — escalations first (they block), then intake by `askedAt` ascending
   — as `{id, kind, question, detail, options:[{value,label,hint}], askedAt,
   subject?}`. It mutates nothing and never dumps file contents (excerpts capped).
2. **Intake options are the decision vocab.** An intake row's options are exactly
   `intake_queue.DECISIONS`, each with a one-line plain-English hint.
3. **Escalation options are resolve/keep.** `keep` is a no-op (stays pending) and
   renders no button in the GUI.
4. **Single apply path, never raises through the JSON contract.**
   `apply_decision(root, id, choice, note)` always returns a dict: intake →
   `intake_queue.decide`; escalation+resolve → the durable escalation resolve
   (reusing `escalations_lib.compact_supervision_events`); escalation+keep,
   unknown id, or off-vocab choice → a structured refusal (`ok:false`).
5. **No-input safety.** In no-input mode bare `decide` behaves as `--list`
   (lists, mutates nothing); it never prompts and never mutates without an
   explicit `<id> <choice>`.
6. **Panel write path stays single and gated.** The GUI writes only through the
   allowlisted `ACTIONS` → `run_action` → harness subcommand path. The
   `intake-decide` action is refused unless `id` names a currently-pending intake
   entry and `choice ∈ intake_queue.DECISIONS` (approval-as-record, validated
   against real state before argv is built); the id shape check forecloses argv
   flag-injection / path traversal. Escalations reuse the untouched
   `resolve-escalation` action.
7. **Notes record the surface.** Every applied decision records a note naming HOW
   a human decided ("via panel" / "via harness.py decide"), for the ledger.
8. **Owner tokens never become buttons.** Approval tokens and `--force`/`scrub`
   variants are absent from the option vocab, so they can never surface as a
   decision or a one-click option.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Surface decisions as plain questions | Owner incident 2026-07-15: an escalated route demand + two hook-captured intake entries could not be closed because the subcommands are unguessable |
| Reuse intake_queue / escalations_lib / prompt_kit, no new store | SPEC-111 (prompt ladder), cm-6 intake queue, SPEC-109 escalation ledger; ponytail ladder rung 2 (reuse what already lives here) |
| Gate the panel action against real pending state | SPEC-114 N4 `_recovery_reason` "compiler is the trust boundary" pattern (approval-as-record) |
| Owner tokens stay CLI-only, typed | SPEC-114 K5: `scrub`/`--force` deliberately absent from ACTIONS |

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: Decision inbox — plain human decisions in the CLI and panel

  Scenario: [di-1] the collector lists pending decisions escalations-first
    Given two pending intake demands and one pending escalation
    When the owner asks for the pending decisions
    Then three decisions appear, the escalation first, each with its answer options

  Scenario: [di-2] a one-shot decision applies and refuses safely
    Given a pending intake demand
    When the owner decides it discard, then tries an unknown id and an off-vocab choice
    Then the demand flips to discarded with the surface note, and the bad calls are refused

  Scenario: [di-3] no-input mode lists and never mutates
    Given no-input mode and pending decisions
    When the owner runs bare decide
    Then the pending decisions are listed and nothing is mutated

  Scenario: [di-4] the panel decide action is gated against real state
    Given a pending intake demand
    When the panel fires intake-decide for a foreign id, an off-vocab choice, and the real id
    Then the foreign id and off-vocab choice are refused and only the real pending id + vocab choice is accepted

  Scenario: [di-5] display-only demojibake repairs cp1252-captured mojibake read-only
    Given a queue whose ask text carries one- and two-level cp1252 mojibake
    When the collector renders the decision for display
    Then the text is repaired to correct UTF-8, clean text passes through, and the queue bytes are untouched

  Scenario: [di-6] the intake hook captures a UTF-8 prompt without mojibake
    Given the UserPromptSubmit hook driven with UTF-8 stdin containing "implementação"
    When the hook captures the feature-shaped prompt into a hermetic temp queue
    Then the captured ask contains the correct UTF-8 and no "Ã" mojibake
```

## Ceilings (upgrade paths)

- **Two sources only (intake, escalation).** New human-decision kinds join by
  adding a branch to `pending_decisions` + `apply_decision`; no framework needed.
- **Read-only escalation source reads `raised` directly** (like
  `ui_panel._escalations`) rather than `list_escalations`, so the collector never
  folds events (a write). Workflow-result-derived escalations without a `raised`
  entry are out of scope for v1; promote to `list_escalations` if that gap bites.
- **English-only questions.** i18n is out of scope; add a message catalog when a
  non-English operator surface is needed.

## Test strategy

- Behaviors to verify: collector shape + ordering + options (di-1); one-shot
  apply flips state and records the surface note, refusals never raise (di-2);
  no-input lists and never mutates (di-3); panel gate refuses foreign/off-vocab
  and accepts a real pending id (di-4).
- Edge cases: empty inbox; unknown/already-decided id; `keep` no-op; id-shape
  injection (`-`-prefixed / path separators) refused by the panel gate.
- Regression risks: the panel write path must stay single (allowlisted ACTIONS);
  the collector must stay read-only (no state mutated on `decide --list`).
- Coverage impact: enforced via `testing/scenarios/di_decision_inbox.py` +
  the `decision_inbox.py` module self-check.

## Validation

- `python testing/scenarios/di_decision_inbox.py` — the `di-1`..`di-4` checks
  (hermetic temp state, no live server).
- `python scripts/harness_lib/decision_inbox.py` — module self-check.
- `python scripts/harness-test.py spec-pack` green (template + Gherkin mapping).
- Live read-only smoke: `python scripts/harness.py decide --list --json`.

## Amendments

### v2 — decision-card UI polish + capture-encoding root fix (2026-07-15)

Owner tested the panel Decisions card live and asked for four fixes (acceptance:
di-5, di-6 added to `testing/scenarios/di_decision_inbox.py`):

1. **Compact colored pill badges** replace the big action buttons, one color per
   choice: `done` dark gray, `discard` red (the escalation red `#a33b38` family),
   `spec` purple, `experiment` green, `backlog` light blue, escalation `resolve`
   neutral/dark gray. Unknown choice falls back to the neutral base `.abadge`.
   Rendered as `<button>` so the single gated write path (data-di → confirm modal
   → `intake-decide`/`resolve-escalation`) is unchanged.
2. **Two-card scroll cap.** `#decs` is capped (`max-height` ≈ two cards) with
   `overflow-y:auto`, so the section never eats the right column.
3. **Question clamp + full text on demand.** The card question is clamped to two
   lines (`-webkit-line-clamp`); the FULL question is carried in the element
   `title` tooltip AND in the confirm modal. Server-side the ask excerpt cap
   `ASK_EXCERPT` rose 140 → 600 so tooltip + modal actually carry the text (JSON
   shape unchanged; the clamp is client-side only).
4. **Mojibake fixed at the root + repaired for display.**
   - **Root cause / root fix:** the UserPromptSubmit hook
     (`tools/hooks/spec_intake_triage.py`) read stdin without forcing UTF-8, so on
     Windows a prompt's UTF-8 bytes were decoded as cp1252 (`ç` → `Ã§`) at capture.
     The hook now forces `sys.stdin.reconfigure(encoding="utf-8", errors="replace")`
     before reading (guarded for non-reconfigurable streams). `validate_before_stop.py`
     reads no stdin (it shells `git`), so it needs no change.
   - **Display repair:** `decision_inbox._demojibake(s)` re-encodes cp1252 then
     decodes UTF-8, strict-roundtrip-and-shrink gated, at most two rounds (repairs
     one- and two-level mojibake). **Ceiling:** heuristic and DISPLAY-ONLY — it is
     never written back to the queue or any state file, and clean text (a genuine
     `ç`, `café`, a non-latin string) passes through untouched because it round-trips
     to a decode error or does not shrink. cp1252 (not latin-1) is required: the
     two-level form carries chars in 0x80–0x9F (e.g. U+0192) that latin-1 cannot
     encode.

Frozen surfaces are untouched: no new panel action, CLI verb, or TSV opt-in (the
`intake-decide` action, the decide verb, and the ACTIONS set are byte-identical).

### v4 — approval-service metrics (C5 / manuscript §7.7) (2026-07-18)

The decision inbox now feeds a derived, read-only **approval-service metrics**
block so the owner can see the approval backlog as numbers, not a feeling.
Additive and measure-only: no new state, no new panel UI, no new CLI verb.

- **Seam (pinned).** `cost_metrics.summarize()` gains an `approvals` block, so
  the existing `harness.py metrics` surface prints it with no new verb. It is
  computed by `cost_metrics._approvals(root)`, which **reuses**
  `decision_inbox.pending_decisions` + `decision_inbox._limits` verbatim — the
  panel and this metric therefore read ONE age/SLO source and can never diverge
  (`_age_fields`/`sloHours` are never re-implemented).
- **Derived fields (all read-only, zero new state):**
  - `pending` — count of pending human decisions (intake + escalation);
  - `sloBreached` — pending rows past `sloHours` (default 48h);
  - `medianAgeHours` / `p95AgeHours` — over the pending rows' ages;
  - `expired` — pending rows past `expiryHours` (default 168h), the L2 safe-pause
    that `apply_decision` refuses until an explicit `--allow-expired`;
  - `resolved` — intake decisions grouped by recorded choice
    (`intakeByChoice`, a bounded window: the queue trims oldest decided first)
    plus `escalationsResolved` (from the ledger `resolvedIds`) and their `total`.
- **Omitted on purpose (🔬 — not fabricated).** `overrideRate` and
  `invalidatedCount` are NOT emitted, because the recon showed the ledger stores
  neither:
  - `overrideRate` would need the recommended-vs-chosen split, but
    `intake_queue.decide` records only `status`/`decidedAt`/`note` — no
    recommendation is captured at ask- or decide-time;
  - `invalidatedCount` would need a durable digest-mismatch record, but the C12
    `invalidated` verdict is a transient `apply_decision` refusal that is never
    written to any state file.
  Both become measurable only once a writer records the recommendation at ask
  time / logs the digest-mismatch refusal; until then they stay out of this
  slice rather than reporting a fixture-only number.

**Ceilings (upgrade paths).**
- **Aggregate only** (Q2): no per-session/per-subject stratification yet; add a
  `bySession` grouping when SPEC-133 per-session cost lands.
- **No post-approval-incident view** (Q3, §7.7): crossing an approval with a
  later incident needs a decision→effect link that the trace-completeness work
  does not yet provide; out of scope for this slice.
- **`resolved` intake counts are a bounded window** (the 200-entry queue trims
  oldest decided first), so they are a recent-history view, not a lifetime total.

```gherkin
Feature: Decision inbox — approval-service metrics (CLI metrics surface)

  Scenario: [di-9] the metrics block derives approval health read-only
    Given two pending intake demands (one older than the SLO), one discarded demand, and one resolved escalation
    When the approval-service metrics block is derived from the decide inbox
    Then it reports pending=2, sloBreached=1, resolved counts by choice, and omits overrideRate and invalidatedCount (not stored)
```

### v3 — decision question drops the "Decide demand <id>:" prefix (2026-07-15)

Owner's visual pass round 2: an intake decision's question read `Decide demand
<id>: "<ask>"?`, but the card already shows the id in its `eid` chip, so the
prefix was noise. The intake question is now just the quoted ask excerpt + `?`
(`"<excerpt>"?`) — server-side in `pending_decisions` (`decision_inbox.py`). The
`id` field stays in the JSON row (contract unchanged), so the card chip, the
panel gate, and `apply_decision`'s id lookup are all unaffected. Escalation
questions keep their `Resolve escalation <id> (<title>)?` shape (only decide
cards were flagged). The interactive CLI `decide` menu, which relied on the
prefix to show the id, now surfaces the id via each option's `description`. The
module `__main__` self-check and `di-1` pin the new bare-excerpt shape. No new
panel action, CLI verb, or TSV opt-in — the frozen surfaces stay byte-identical.

### v5 — a third source (vendor acceptances) + the digest the client never sent (2026-07-29)

Two changes, one surface. SPEC-172 owns the acceptance semantics; this amendment
records what they change **here**, and fixes a gap they exposed by contrast.

**A third decision kind.** The ceiling "two sources only (intake, escalation)"
above is now three, exactly by the upgrade path it described — a branch in
`pending_decisions` (`_acceptance_rows`) plus a branch in `apply_decision`
(`_accept_vendor`), no framework. Consequences for the invariants as written:

- **Ordering (inv. 1)**: acceptances lead, then escalations, then intake by
  `askedAt`. A vendor refusing to run this repo's hooks is why the guards behind
  the other rows may have been silent, so it is not a row to scroll to.
- **Options (inv. 3's shape, reused)**: `accept` / `keep`, with `keep` a no-op that
  renders no button — the escalation convention, deliberately.
- **Dispatch (inv. 4)**: `acceptance` + `accept` → `acceptances.acceptance_plan` in
  `headless` mode; `keep` → structured refusal. Still never raises through the JSON
  contract, which is why an unknown vendor in the cache is dropped at COLLECTION
  (it would reach a `PROBES[vendor]` KeyError) rather than at apply.
- **Panel path (inv. 6)**: its own allowlisted action, `acceptance-decide`, gated by
  `_acceptance_reason`. It is the narrowest of the family — `id`, `choice`, digest,
  and nothing else — because its apply ends in a vendor's TUI; vendor and mode are
  read/fixed server-side rather than validated as parameters.
- Unlike intake and escalation, this row's source is a CACHE FILE
  (`.harness/state/acceptances.json`), so the collector treats its contents as
  untrusted input. The other two read canonical state written only by the harness.

**The C12 digest binding was dead code in the browser.** Every row has carried a
content `digest` since the ref-arch round, `apply_decision` has honored
`expected_digest`, `_decide_reason` has validated its shape, `intake-decide` has
built `decide --expected-digest`, and `di-10` has proved the server refuses a stale
one. The panel's `renderDecisions` never SENT it: intake decisions from the browser
were unbound in practice, while the action's own comment stated the opposite. Both
decide-verb kinds now forward it (`di-13` pins the client, since a server-side check
cannot notice a client that stays silent).

**Known asymmetry, deliberately not "fixed" here.** Escalation resolves from the
panel remain unbound: `resolve-escalation` calls the `escalations` verb directly,
not `decide`, so there is nowhere to put the digest. Routing them through `decide`
would drop the subject-scoped resolve check (`esc-scoped-hitl-view`) that
`_resolve_escalation` does not carry — a security regression traded for a TOCTOU
guard. Binding them properly means teaching the `escalations` verb the digest, which
is its own change with its own review.
