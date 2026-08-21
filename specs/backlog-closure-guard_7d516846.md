# SPEC-154 -- Backlog-closure guard (tie delivery to item closure in lockstep)

Status: SPEC-154, proposed 2026-07-19 (acceptance: `testing/scenarios/bc_backlog_closure.py`).
Door: SPEC-116 NEW (owner decision 2026-07-19 -- gate lockstep via a scenario annotation).
Mirrors the design-system-guard shape (`specs/40-features/design-system-guard.md`): a SPEC-116
door + a gate scenario (the teeth) + a delivery-bar advisory (the early nudge) + a ritual step.

## Goal

Tie the DELIVERY of a backlog item (its shipped acceptance scenario) to the
CLOSURE of its backlog row (marked done/archived), deterministically, in the
same commit -- the same lockstep discipline as the te5/cli_registry frozen
surfaces. This is the forward-looking fix for backlog rot: items that ship but
stay listed OPEN (an audited ~44). A scenario that closes an item declares it;
the gate then refuses to let the scenario land while the row is still open.

## Applicability

Applies to `testing/scenarios/bc_backlog_closure.py` (the enforcement),
`tools/hooks/delivery_bar_advisor.py` R5 (the advisory nudge, never blocks),
`.harness/prompts/overseer-loop-playbook.md` (the ship-ritual step), and the
`# closes-backlog: <slug>` convention any acceptance scenario may carry. Reads
`docs/IMPLEMENTATION_BACKLOG.md` + `docs/backlog-archive.md` and reuses
`scripts/harness_lib/tasks_board.py` (`_backlog_rows`) for the open/closed lane
derivation. Does NOT auto-close items (detection only; closing is the
human/supervisor action), does NOT edit the backlog itself (the archive sweep of
the existing drift is a separate overseer step), and does not restate the
baseline (`specs/00-universal/testing-and-quality-gates.md` is referenced).

## Requirements / invariants (numbered, testable)

1. **The annotation convention.** An acceptance scenario that closes a backlog
   item carries a top-of-file comment `# closes-backlog: <slug>` (multiple:
   `# closes-backlog: <slug1>, <slug2>`; slug charset `[A-Za-z0-9._-]`). Only a
   real leading-`#` comment line is an annotation -- a mention inside a docstring
   or string literal is not, so a scenario cannot self-trigger. The scan is over
   `testing/scenarios/*.py`, excluding the guard's own file.
2. **bc-1 -- closed-in-lockstep.** Every declared slug is CLOSED: its backlog row
   is struck/done (lane `done` in `tasks_board`) OR the slug is absent from the
   open backlog (archived). A declared slug that is still OPEN (present + not
   done) FAILS `bc-1`, naming the violators and their declaring scenarios.
   Open-ness is derived by REUSING `tasks_board._backlog_rows` -- never
   reimplemented; it is TABLE-ROW based (a slug tracked only in backlog prose
   reads as absent = archived = closed, by design; see Ceilings).
3. **bc-2 -- no ghost slug.** Every declared slug EXISTS (whole-token) in
   `docs/IMPLEMENTATION_BACKLOG.md` OR `docs/backlog-archive.md`. A declared slug
   found in neither FAILS `bc-2` (catches a typo / ghost slug). Whole-token match
   guards prefix collision (`F.1` does not satisfy on `F.10`). **bc-3 -- clean
   annotation.** A comment carrying the `closes-backlog:` marker must be a clean
   comma-separated slug list to end-of-comment; trailing prose (e.g.
   `# closes-backlog: foo -- see bar`) FAILS `bc-3` (flagged, never split into
   spurious slug-shaped words). Comments are read from real Python comment tokens
   (`tokenize`), so a marker line inside a docstring/string literal is never a
   declaration and cannot self-trigger.
4. **Advisory nudges, gate is the teeth.** `delivery_bar_advisor.py` R5 emits one
   reminder when a STAGED `testing/scenarios/*.py` declares `closes-backlog:<slug>`
   for a slug still OPEN, so the row can be closed in the same commit; it NEVER
   blocks (exit 0 always) and is fail-open. Mechanical enforcement is the gate
   scenario, not the hook.
5. **Detection only, deterministic, read-only.** The guard never auto-closes an
   item and never edits the backlog; it only DETECTS declared-but-open drift.
   Same inputs yield the same result; stdlib only.

## Gherkin scenarios

```gherkin
Scenario: [bc-1] a shipped scenario cannot close a still-OPEN backlog item
  Given an acceptance scenario declares "# closes-backlog: <slug>"
  When the guard derives open backlog rows via tasks_board
  Then bc-1 fails if that slug's row is present and not struck/done
  And bc-1 passes when the row is struck/done or absent (archived)

Scenario: [bc-2] a declared closes-backlog slug must exist in the backlog or archive
  Given an acceptance scenario declares "# closes-backlog: <slug>"
  When the guard searches IMPLEMENTATION_BACKLOG.md and backlog-archive.md
  Then bc-2 fails if the slug (whole-token) appears in neither file
  And bc-2 passes when the slug exists in either file

Scenario: [bc-3] a closes-backlog annotation must be a clean slug list
  Given a comment carries "# closes-backlog:" with trailing prose after the slugs
  When the guard parses real comment tokens with the strict slug-list grammar
  Then bc-3 fails and the prose words are not minted as slugs
  And a marker line inside a docstring or string literal is not a declaration
```

## Rationale & sources

| Decision | Sources |
|---|---|
| Lockstep delivery -> closure via a scenario annotation (R1, R2) | owner decision 2026-07-19 (`.harness/handoff/plan-closure-guard.md`); te5/cli_registry frozen-surface lockstep precedent |
| Reuse the backlog parser, never reimplement (R2) | `scripts/harness_lib/tasks_board.py` `_backlog_rows` / derived lanes (`done` = struck/done) |
| Existence check across live + archive (R3) | `docs/IMPLEMENTATION_BACKLOG.md`, `docs/backlog-archive.md` (2026-07-19 history split) |
| Advisory early, gate is the teeth (R4) | `specs/40-features/design-system-guard.md` (advisory-seed + gate-teeth shape); `tools/hooks/delivery_bar_advisor.py` R1/R4 pattern |
| Detection only, closing is human (R5) | plan MUST-NOT (no auto-close); the archive sweep of the existing ~44 drift is a separate overseer step |

## Ceilings (upgrade paths)

- Open-ness is TABLE-ROW based (the `tasks_board` parser): a slug tracked only in
  backlog prose reads as absent = archived = closed. If prose-only items must be
  guardable, promote them to rows (or extend the parser) -- a separate amendment.
- The annotation is a comment convention, not a schema; once the canonical task
  store replaces the markdown tables (`tasks_board` A1), bc-1 follows the store
  automatically because it reuses the same derivation.
- The advisory is nudge-only; the gate is the enforcement of record.

## Test strategy

- Behaviors to verify: bc-1/bc-2 pass on the current tree (no scenario declares
  `closes-backlog` yet -> empty, pass); a declared-OPEN slug turns bc-1 red; a
  declared-struck/absent slug passes bc-1; a ghost slug turns bc-2 red. Proven by
  the scenario's hermetic `_selfcheck` over an injected backlog fixture + injected
  annotations (deterministic).
- Edge cases: multi-slug annotations split correctly; a docstring/inline mention
  of the token is NOT an annotation; whole-token existence guards prefix collision.
- Regression risks: a new scenario that closes an item without striking/archiving
  its row turns bc-1 red; a typo'd slug turns bc-2 red; the R5 advisory nudges the
  same condition earlier without ever blocking.
- Coverage impact: enforced via `testing/scenarios/bc_backlog_closure.py`
  (bc-1, bc-2) and `tools/hooks/delivery_bar_advisor.py --self-check` (R5).

## Validation

- `python testing/scenarios/bc_backlog_closure.py` (bc-1/bc-2 green on the current
  tree; the hermetic self-check proves declared-OPEN fails bc-1, declared-struck/
  absent passes, and a ghost slug fails bc-2).
- `python tools/hooks/delivery_bar_advisor.py --self-check` (OK, R5 fires on a
  still-OPEN declared slug and is silent when done/absent).
- Spec-pack `feature-spec-conformance` green on this file (six required sections
  present; the Gherkin `[bc-1]`/`[bc-2]` ids resolve to `check("bc-1")`/
  `check("bc-2")` in `testing/scenarios/bc_backlog_closure.py`).

## Amendments

(none yet)

## Amendment — the guard reads the store (`backlog-json-canonical`, 2026-07-27)

bc-1 derived open-ness by parsing `docs/IMPLEMENTATION_BACKLOG.md` while the
board served the store, so the teeth and the operational surface reasoned about
different row sets. Both now read `tasks_board.task_rows` (the store when it
exists, the document on a storeless root).

- **Open-ness**: a store row not in lane `done` is open. Closing is
  `harness.py tasks close <slug>`, whose store write is staged in the same
  commit as the scenario — the invariant's meaning is unchanged.
- **Existence (bc-2)**: store ids join the document and `docs/backlog-archive.md`
  as sources. A task created by `tasks add` never had a document row, so
  without this a legitimate closure would read as a ghost slug.
- **Staged view (REQUIRED)**: `scenario_isolation._VALIDATED_DOCS` re-materializes
  the store from the git index during `validate --staged`. Without it the store
  runs at HEAD inside the wholesale-restored `.harness/state` dir, a staged
  `tasks close` is invisible, and this guard becomes **unsatisfiable by
  construction**. Pinned by `si-3e`.

## Amendment — the advisory learns the verb path (`r8-boundary-blind-to-verb-path`, 2026-07-29)

Invariant 4's advisory leg was keyed on the DECLARATION only. Every rule in
`delivery_bar_advisor.py` that means "this commit closes an item" read
`declared` — the staged `# closes-backlog:` receipts — so a row closed through
`harness.py tasks close`, with the store staged in the same commit and no receipt,
was invisible to all of them. Measured live on commit `dad0077`:

- **R8 boundary-clear** stayed silent at a real item boundary. It is the ONLY surface
  that tells the owner to `/clear` (EXP-35 reset-por-fronteira), so the boundary
  passed unmarked and the finding surfaced only because the owner asked.
- **R9 scope-creep** skipped the creep check entirely on such a commit.
- **R10 checkpoint-drift** did worse than stay silent: it ACCUSED the very commit that
  legitimately ended the item of naming a stale checkpoint.

The boundary is now the union of both closure paths — `declared | store_closed` —
consumed by R8, R9, R10 and the new R11. `store_closed` arrives as a parameter, so
`advise()` stays pure and deterministic; the git calls live in the wrapper next to
`_staged_backlog_added`, and every failure yields `[]` (fail-open, exit 0 always).

- **The predicate** is a `!done -> done` transition between the HEAD blob and the
  INDEX blob of `.harness/state/tasks.json` (the index: the commit's content is what
  is staged). `tasks_store.close` IS `move(id, "done")`, so a manual `move <id> done`
  is the same event and counts. A row ABSENT at HEAD does not (that is `tasks import`
  backfilling); nor does one that gained `archivedAt`, which the migrate/archive sweep
  sets alongside `closedAt` while a normal close sets `closedAt` alone. That signature
  is why there is no "too many closes at once" threshold: a legitimate batch of four
  closures is still four boundaries, and a three-row sweep is still a sweep.
- **R11 close-without-receipt** is a new rule, not a footnote on R8, because the
  remedies have different timing: R8 says "after it lands, /clear"; R11 says "fix THIS
  commit before it lands". It is also the only automated surface that can EVER see
  this breach — bc-1/2/3 are gated on the receipt, so no receipt means no enforcement,
  silently. That asymmetry is deliberate and unchanged: a store-only close still buys
  ZERO mechanical enforcement, and R11 says so in its own message.
- **Nothing here accepts a store close as a substitute for the receipt.** The verb
  path becomes MORE nagged than before, not less. bc-1/2/3 and "detection only" are
  untouched; only the nudge's coverage changed, which is why this is an amendment and
  not a new numbered invariant.
- **Claim/detection congruence (required, and the reason the docstring moved too).**
  The row `r7-advisory-claims-a-detection-it-does-n` closed the mirror-image defect —
  an advisory naming a condition it never evaluated — by SHRINKING the claim to fit an
  infeasible detection. Here the state is two `git show`s away, so the detection grew
  instead; shipping that while the rule list still said "carries a receipt" would have
  recreated the same defect facing the other way. That row's closing line asked for
  the siblings to be audited: R5 is unaffected (its subject IS the declaration), and
  R6 looked exposed but is enforced structurally at write time in `tasks_store.add`
  (SPEC-155 entry-groom records `noDeps`), which is stronger than any advisory.
- **Teeth**: `pvg-5` (`r8v`, `r8once`, `r11`, `r9v`, `r10v`) plus mirrored asserts in
  the advisor's own `--self-check`. Falsified by planting three mutants: reverting the
  R8 gate to `declared`, deleting the R11 block, and making R8 append on both branches
  — each turned exactly one flag red with the others still green.
