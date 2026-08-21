# Commit-tie receipt — every shipping commit names what now enforces it

Status: proposed 2026-07-27 (acceptance: testing/scenarios/ct_commit_tie.py).

Intake: R4 delivery-bar advisory fired on commit `6c62827` — a new module
(`scripts/harness_lib/commit_tie.py`) shipped with no specs amendment or docs
entry. Backlog row: `commit-tie-has-no-spec-leg`. This spec is the missing
leg; the mechanism itself was already ratified and shipped in `6c62827` after
an adversarial critique (`.harness/handoff/critique-overseer-iteration-SOL.md`,
"codex sol xhigh critique" in the ship commit) ranked it above an iteration
ledger and a checkpoint checklist. Covered-check: no prior spec in
`specs/40-features/` names `Tie:` trailers or `commit_tie.py`. Decision:
**NEW**.

## Goal

Every normal (non-merge) shipping commit in this repo carries a durable,
Git-native receipt naming the mechanism that now enforces what it shipped —
or an honest `Tie: none:<reason>` when no mechanism is owed. The receipt
rides inside the commit message itself: no parallel state file, no
ambient-budget cost, identical for the autonomous loop and an interactive
session, and it survives a compact. A `commit-msg` hook blocks a missing or
malformed receipt at write time; `doctor`'s `commit-tie` check WARNs on what
the hook cannot see — `--no-verify` bypasses and history rewrites — and on
the hook being unwired in the first place.

The problem this closes: three shipped capabilities in five days whose only
proof was prose (`.harness/handoff/critique-overseer-iteration-SOL.md`
§ Executive verdict) — a playbook edited without its lock (`b716261`), a
backlog row closed three commits late (`b53c32e`), an obligation enforced at
the wrong edge. A checklist can claim all three happened without making any
of them true; the receipt instead ties the claim to something that already
exists (a scenario, a doctor check, a hook, a gate, a playbook line, or a
backlog row) and blocks the commit when that tie is missing in form.

## Applicability

Applies to `scripts/harness_lib/commit_tie.py` (`validate_message`,
`audit_records`, `_hook_main`, the `KINDS`/`AUDIT_SINCE`/`AUDIT_LIMIT`/
`LOG_FORMAT`/`LOG_ARGS` constants), `tools/git-hooks/commit-msg` (the shim
that runs it as `commit-msg`), the `commit-tie` check inside
`scripts/harness_lib/repo_health.py:checks()`, and ritual step 7c of
`.harness/prompts/overseer-playbook.md` (cited here, not duplicated — see
"Playbook tie" below). Does not change any other hook, any gate check, or
any existing doctor check.

## Requirements / invariants (numbered, testable)

1. **Trailer grammar (EBNF).** A `Tie:` line matches
   `tie-line = "Tie:" , SP , kind , ":" , value` where `kind` is exact-case
   lowercase from `{hook, gate, doctor, playbook, backlog, scenario, none}`
   and `value` is any non-empty (post-strip) string. `Tie:` is the literal,
   exact-case prefix (`scripts/harness_lib/commit_tie.py:46`,
   `_TIE = re.compile(r"^Tie:\s*(?P<payload>.*)$")`); a stray `tie:` or `TIE:`
   line does not match and is not a receipt.
2. **Kind set is closed.** The six mechanism kinds are
   `hook | gate | doctor | playbook | backlog | scenario`; `none` is a
   seventh value reserved for the honest exemption, never counted as a
   mechanism. A payload with no second `:` separator, or a kind outside this
   set (including a plural or wrong-case spelling), is `tie-bad-kind`.
3. **Non-empty value.** A mechanism line (`hook`..`scenario`) with an
   empty/whitespace-only locator after the second `:` is `tie-empty-locator`.
   A `none` line with an empty/whitespace-only reason is
   `tie-empty-none-reason`.
4. **`none` cannot mix.** If any `Tie: none:...` line is present alongside
   any other `Tie:` line in the same trailer block — including a malformed
   one — the commit is `tie-none-mixed`: a `none` exemption sharing a commit
   with a line the author meant as something else is no longer an honest
   exemption (`commit_tie.py:144-148`).
5. **Trailer-block rule: the LAST paragraph, normalized.** A `Tie:` line
   counts only inside the final paragraph of the message. Before the
   paragraph split, the text is normalized: `\r\n` and lone `\r` both become
   `\n`; any line at or after the `git --verbose` scissors marker
   (`# ------------------------ >8 ------------------------`) is dropped;
   any line starting with `#` (an editor comment/hint line) is stripped;
   trailing blank lines are trimmed before the paragraph split
   (`_trailer_split`, `commit_tie.py:77-110`). A `Tie:` line found in an
   EARLIER paragraph (not the last) is `tie-outside-trailers` — a distinct
   error from `tie-missing`, so an author who wrote a receipt in the wrong
   place is told to move it, not told they wrote nothing.
6. **Missing.** No `Tie:` line anywhere in the final trailer paragraph, and
   none found earlier either, is `tie-missing`.
7. **Every typed error carries a `fix:` line.** Each of the six errors above
   (`tie-missing`, `tie-bad-kind`, `tie-empty-locator`,
   `tie-empty-none-reason`, `tie-none-mixed`, `tie-outside-trailers`) is a
   two-line string: the error id and detail, then a `fix:` line naming the
   exact remedy. `validate_message` never emits an error without one
   (asserted by `ct-grammar`'s `every_fix` check).
8. **Semantic adequacy is never machine-judged.** `validate_message` checks
   FORM only — that a `Tie:` line exists, is well-shaped, and sits in the
   trailer block. Whether the cited locator (e.g. `doctor:commit-tie`) is the
   RIGHT mechanism for the diff it rides with is left to the human/overseer
   reviewing the commit, by design: a parser that tried to judge relevance
   would only teach people to write receipts that please the parser, not
   receipts that are true (`commit_tie.py:116-118`).
9. **Merge exemption.** A merge in progress (`MERGE_HEAD` present in the
   resolved git dir) is exempt from validation — a merge commit's message
   carries no receipt of its own, and `commit-msg` still fires for merges so
   the exemption lives in `_is_merge`, not in the hook's caller. An
   unresolvable git dir (I/O error, unexpected layout) is treated as "not a
   merge" — the safe direction, because it keeps validation ON rather than
   silently exempting an ordinary commit (`commit_tie.py:202-211`).
10. **Fail-open on internal error.** Any unexpected exception inside
    `_hook_main` (reading the message file, or a bug in validation itself) is
    caught, reported to stderr as `commit-msg tie gate: internal error
    (...); passing fail-open`, and returns 0 (allow). A broken guard must
    never wedge every commit in the repo; typed validation errors are the
    ONLY path that returns 1, and that reporting sits outside the fail-open
    `try` so a print failure cannot turn a real block into a silent pass
    (`commit_tie.py:234-253`).
11. **Zero harness_lib imports, zero process spawns.** `commit_tie.py` is
    stdlib-only. The hook runs it as a bare script from the repo top level
    with nothing of `scripts/` on `sys.path`; `repo_health.py` imports it as
    `from harness_lib import commit_tie`. Both paths only work while the
    module stays self-contained. It spawns nothing: the merge probe resolves
    `.git` by reading it (a directory, or a `gitdir: <path>` file for a
    worktree/submodule) rather than shelling out to `git rev-parse`, and the
    `git log` call for the audit lives in `repo_health.py` (already a
    mediated/baselined call site there) which hands the raw stdout to
    `commit_tie.audit_records` for pure parsing.
12. **Doctor `commit-tie` check — two arms.** `repo_health.checks()` adds a
    `commit-tie` id with two ordered arms:
    - **Wiring arm.** If the repo's own hook file
      (`tools/git-hooks/commit-msg`) exists but `git config
      core.hooksPath` does not resolve (via `os.path.samefile`) to it, WARN
      with detail `"commit-msg hook present but core.hooksPath=<value> does
      not run it — receipts are NOT being collected; fix: git config
      core.hooksPath tools/git-hooks"` and return early — auditing receipts
      is worthless while nothing is collecting them.
    - **Audit arm.** Otherwise, count non-merge commits since `AUDIT_SINCE`
      (capped display at `AUDIT_LIMIT`) and run `commit_tie.audit_records`
      over `git log` output built from `commit_tie.LOG_ARGS`/`LOG_FORMAT`.
      Zero commits since the anchor → ok, `"no commits after the audit
      anchor (<AUDIT_SINCE>)"`. All audited commits carry receipts → ok,
      `"<n> audited commit(s) since <AUDIT_SINCE> carry Tie receipts"`. Any
      failures → warn, `"<k> of <n> commit(s) since <AUDIT_SINCE>
      missing/malformed Tie receipt: <sha8, sha8, ...> [...] — --no-verify
      bypass or rewrite; amend, or carry the reason in the next commit"`
      (first 5 shas, `...` suffix if more). Any exception anywhere in the
      check → ok, `"unreadable"` — an audit that could not read is not an
      audit that found something, so it never manufactures a false warn.
13. **WARN-only, never blocking.** `commit-tie` never returns a non-zero exit
    from `doctor`; it is a backstop surface, consistent with the doctor
    charter (`specs/40-features/repo-health-doctor.md`). A receipt audit
    that BLOCKED would just be a second commit gate; the reason `commit-msg`
    fails open on internal error is precisely that doctor stands behind it.
14. **AUDIT_SINCE is a timestamp anchor, not a sha anchor.** The audit window
    starts at a fixed committer-date timestamp
    (`AUDIT_SINCE = "2026-07-28T00:00:00-03:00"`), chosen because a
    timestamp is knowable at write time (a sha anchor would need a
    self-referential two-step ship commit), it survives history rewrites
    that orphan a sha, and it buys day-one silence — every commit predating
    the rule sits before the anchor and never cries wolf. The tradeoff: a
    forged pre-anchor committer date on a later commit escapes the audit.
    This is accepted because the audit is WARN-only and a backstop, not the
    control (`commit_tie.py:36-43`).
15. **Bounded audit window.** `AUDIT_LIMIT = 20` — the audit reads at most
    the 20 most recent non-merge commits since the anchor; it is a backstop,
    not a full-history report.

## Block-vs-warn split

`commit-msg` (the hook, run at commit time) BLOCKS on FORM ONLY — missing
receipt, bad kind, empty locator/reason, mixed `none`, or a receipt outside
the trailer block. It never judges whether the cited mechanism is the right
one; that stays reviewer/overseer judgment for the reasons in requirement 8.
`doctor`'s `commit-tie` check WARNS, never blocks, on what the hook structurally
cannot see: a `--no-verify` bypass, a history rewrite/squash that dropped the
trailer, or the hook being present in the tree but not wired into
`core.hooksPath` at all. The split is deliberate: a hard-blocking form check
is cheap and unambiguous to run on every commit; a semantic-adequacy check
would require a classifier for "does this locator actually cover this
diff", which the earlier candidate ranking rejected as mechanically
undetectable (see "Rejected alternatives" below).

## Fail-open posture

`_hook_main` catches every unexpected exception and returns 0 (allow),
logging `"internal error (...); passing fail-open"` to stderr. This is
deliberate, not an oversight: a bug in the tie parser must never be able to
wedge every commit in the repo, because the parser runs on every normal
commit unconditionally. `doctor`'s `commit-tie` audit is the named backstop
for exactly this failure mode — if the hook silently fails open on many
commits, the audit still catches the resulting missing receipts on its next
run. Only a TYPED validation error (a real, well-formed judgment that the
receipt is missing or malformed) returns 1.

## Merge exemption and the audit anchor tradeoff

A merge commit's message carries no receipt of its own and is exempt via the
`MERGE_HEAD` probe (requirement 9). Separately, `AUDIT_SINCE` anchors the
doctor audit by committer-date timestamp rather than by a ship sha
(requirement 14). The accepted tradeoff on the timestamp anchor: a
`GIT_COMMITTER_DATE` forged to predate the anchor lets a commit escape the
audit permanently, even though the commit itself lands after the anchor in
real history. This is accepted because `commit-tie` is a WARN-only backstop,
not the control that decides whether a commit is allowed to exist — the
control is the `commit-msg` block, which runs at commit time regardless of
any date field.

## Rejected alternatives and deliberate postponements

The mechanism in this spec is `.harness/handoff/critique-overseer-iteration-SOL.md`'s
"B-prime + D-prime" (§ 8, ranked #1), chosen over:

- **An iteration ledger (candidate A).** Rejected: NO BUILD. It would create
  a second truth source next to route/fuel/delegation/gate/mutation/reckon/
  task-closure/checkpoint, each of which already writes authoritative state
  that a ledger row could disagree with; auto-write-through cannot safely
  assign causality under WIP pipelining (`WIP ~= 2`, one demand can span
  multiple commits, one commit can close a task while another stays open); a
  checked box is not evidence quality (`oracle mutate` can report "nothing
  to probe", `review` can pass with WARN rows unjudged); its readers sit at
  the wrong edges (Stop is legitimately mid-flight); and its own lifecycle
  becomes a new orphan class (abandoned rows, two simultaneously open
  demands, rewritten commits) needing its own doctor policy (§ 3).
- **A checklist in the checkpoint (candidate C).** Rejected: NO BUILD. It
  would compete for the checkpoint's own tight state budget (already over
  budget at critique time); it cannot represent WIP pipelining with one
  checkpoint block; the checkpoint already has structured `Item/Phase/
  Verify` fields, so more fields is not the missing piece; its evidence diff
  (delegation logs, `verify-status`, mutation runs) is not durably available
  to check against; the writer (`write_checkpoint`) is a non-transactional
  read/replace/write, so concurrent transitions can overwrite each other;
  and Stop being advisory means a blocking checklist there would trap
  legitimate mid-flight pauses (§ 5).
- **A separate `tie --record` verb / result ledger (an earlier shape of
  B).** Rejected: it duplicates the strongest parts of `reckon` (actor,
  time, staged fingerprint, durable history, commit join already exist in
  `validation_stamp`) and a separate ledger can be lost to gate holds, stale
  fingerprints, or cleanup unless it reimplements reckon's durability and
  rescue logic — the Git trailer avoids this because the receipt and the
  change it describes cannot have different fingerprints (§ 4).
- **Extending `reckon --record` instead of a Git trailer (B-double-prime,
  the runner-up fallback).** Not chosen as v1: `validation_stamp.check_reckon()`
  deliberately exempts tests, specs, and docs, while the observed omissions
  included exactly a playbook edit and a backlog-closure commit — surfaces
  reckon does not cover. Expanding reckon to every commit would recreate the
  ceremony this mechanism exists to avoid (§ 7).
- **Doctor as the primary/only mechanism (candidate D, unnarrowed).**
  Rejected as primary: doctor is explicitly WARN-only and only helps when
  someone runs it, so it cannot be the mechanism that forces a close-time
  decision. Narrowed to **D-prime** (WARN-only backstop) after B-prime
  exists to give it concrete facts to audit (§ 6).

Named failure modes carried forward as accepted, not solved:

- a rubber-stamped `Tie: none:<reason>` cannot be eliminated mechanically
  without an unreliable capability classifier; mitigation is doctor WARN
  plus human review, never a heuristic block;
- a syntactically valid but semantically irrelevant locator (requirement 8);
- `--no-verify` bypass and history-rewrite/squash trailer loss, covered by
  the doctor audit within its bounded window;
- the hook not being installed/wired, covered by the wiring arm;
- non-commit discoveries (an insight that never lands as a Git or backlog
  artifact) are explicitly out of scope for v1.

**Explicitly postponed, with a reopen trigger.** The critique names five
postponements: an iteration ID or lifecycle ledger; route/fuel/brief/launch/
review step accounting; hard semantic judgment that a cited mechanism truly
covers the claim; durable mutation-evidence recording and auditing; and
orchestration of insights that never become a Git/backlog artifact.
Suspicious-`none` heuristics and dangling-locator existence checks (does the
cited backlog row/path still exist) are named in D-prime's candidate list
(§ 6) but were not built into the shipped `commit-tie` doctor check either —
only the wiring arm and the missing/malformed audit arm shipped. **Reopen
trigger** (§ 9, verbatim intent): reopen the iteration-ledger question only
after this receipt has shipped and there are at least two further measured
omissions of DIFFERENT mechanically observable ritual steps that cannot be
placed at their own correct edges. Until then, a ledger is speculative
machinery.

## Defects the gate caught while shipping this

Named directly in the ship commit (`6c62827`), because they are this spec's
real edge cases, not incidental history:

1. **`route_loop` composed machine commits with no receipt.** The armed hook
   would have killed the harness's own commit stage for autonomous-loop
   commits, since `rt6` commits for real. Fixed by having machine commits
   tie to the route entry that authorized them — `Tie: backlog:<entry id>` —
   a locator that exists by construction rather than one a human has to
   invent per commit.
2. **`commit_tie.py` itself opened a raw-spawn site the ratchet forbids.**
   The named remedy for a new raw-subprocess site is `processes.py`
   (`specs/40-features/raw-subprocess-ratchet.md`), which is exactly the one
   import `commit_tie.py` may never have (requirement 11 exists because of
   this). The spawns were designed away instead: the merge probe reads
   `.git` directly, and the `git log` call for the audit moved into
   `repo_health.py`, leaving `commit_tie.py` a pure parser.
3. **`ct-live` asked a live-repo question from inside a detached worktree
   copy.** The scenarios gate runs each shard in a detached worktree pinned
   to a commit, so "does `core.hooksPath` wire the real hook?" is a question
   about a repo the process is not in. Moved to doctor's `commit-tie` check,
   which runs on the real root every time; the `ct-live` scenario clause is
   quarantined under `HARNESS_PARALLEL_COPY=1` (the ratified EXP-30
   quarantine marker) with an explicit detail string rather than reading as
   a defect (`testing/scenarios/ct_commit_tie.py:206-229`).

A fourth, smaller trap surfaced after the ratified fixes: the hook refused
the ship commit's OWN message for putting the `Tie:` lines in a paragraph
above the `Co-Authored-By`/`Claude-Session` block, which is the default
trailer shape here. Ritual step 7c (below) now says the `Tie:` lines join
that same trailer block, no blank line before it.

## Playbook tie

Ritual step 7c of `.harness/prompts/overseer-playbook.md` is the human-facing
half of this contract — composing the receipt BEFORE the commit, choosing
which kind fits the change, and the ONE TRAILER BLOCK rule (the `Tie:` lines
sit inside the same final paragraph as `Co-Authored-By`/`Claude-Session`, no
blank line between them). This spec does not restate that guidance; see the
playbook directly.

## Gherkin scenarios

```gherkin
Feature: commit-tie receipt

  Scenario: [ct-grammar] validate_message is the whole form contract
    Given the fixed set of message cases (valid single/repeated/none/CRLF/
      lone-CR/one-paragraph/other-trailers/prose-mention/stray-plus-trailer/
      editor-template, and each of the six typed-error triggers)
    When validate_message runs on each
    Then every VALID case returns no errors, every INVALID case returns
      exactly its expected error id(s), and every returned error carries a
      "fix:" line

  Scenario: [ct-red] the real commit-msg hook blocks malformed receipts
    Given a hermetic throwaway repo wired to the real tools/git-hooks/commit-msg
      via core.hooksPath
    When a commit is attempted with no Tie line, a bad kind, an empty none
      reason, or a mixed none
    Then each commit is rejected (non-zero exit) and the typed error id
      appears in the hook's output

  Scenario: [ct-green] the hook passes honest receipts
    Given the same hermetic repo
    When a commit carries a single "Tie: none:<reason>" or repeated
      mechanism Tie lines
    Then the commit succeeds

  Scenario: [ct-merge] a merge commit is exempt
    Given two branches each with a valid Tie receipt
    When they are merged with --no-ff and no Tie line in the merge message
    Then the merge commit succeeds with two parents

  Scenario: [ct-audit] a --no-verify bypass is invisible to the hook and
    caught by doctor
    Given the hermetic repo's doctor commit-tie check is "ok" beforehand
    When a commit with no receipt is made with --no-verify
    Then commit_tie.audit_records finds exactly that commit with a
      tie-missing error, and the doctor check flips to "warn" naming its sha

  Scenario: [ct-live] the live repo's hooksPath actually wires the real hook
    Given the real repository root (not a parallel worktree copy)
    When git config core.hooksPath is read
    Then it resolves (via samefile) to tools/git-hooks/commit-msg
    And under HARNESS_PARALLEL_COPY=1 this scenario clause is quarantined,
      loudly, and the live question is left to doctor's commit-tie check on
      the real root
```

## Rationale & sources

| Decision | Sources |
|---|---|
| Git trailer, not a parallel state file | `.harness/handoff/critique-overseer-iteration-SOL.md` § 4 ("Why Git trailers instead of another harness state file") |
| Block form only, never semantics | `scripts/harness_lib/commit_tie.py:116-118`; critique § 4 requirement 4 |
| Fail-open on internal error, doctor is the backstop | `commit_tie.py:234-253`; `repo_health.py` commit-tie check comment (line 526) |
| Timestamp anchor over sha anchor, tradeoff accepted | `commit_tie.py:36-43` |
| B-prime + D-prime ranked over ledger/checklist/reckon-extension | `.harness/handoff/critique-overseer-iteration-SOL.md` §§ 3, 5, 7, 8 |
| Zero harness_lib imports, zero spawns | `commit_tie.py:14-25`; ship commit `6c62827` body ("commit_tie opened a raw-spawn site...") |
| Reopen trigger for the ledger question | critique § 9 ("Reopen the iteration-ledger question only after...") |

## Test strategy

- Behaviors: full grammar coverage via `ct-grammar` (all six errors plus
  every documented VALID shape); real-hook block/pass behavior via
  `ct-red`/`ct-green`; merge exemption via `ct-merge`; bypass detection via
  `ct-audit`; live wiring via `ct-live`.
- Edge cases: CRLF and lone-CR normalization, `git --verbose` scissors
  truncation, editor `#`-comment stripping, a stray `Tie:` in an earlier
  paragraph (`tie-outside-trailers`) versus a stray `Tie:` with no trailer
  block at all (`tie-missing`), a `none` mixed with a malformed line.
- Regression net: `ct-grammar`'s `every_fix` assertion guards against a
  future typed error shipping without a `fix:` line; `ct-live`'s quarantine
  clause guards against the detached-worktree false negative recurring.
- Coverage: deterministic, stdlib-only, no LLM —
  `testing/scenarios/ct_commit_tie.py`.

## Validation

- `python testing/scenarios/ct_commit_tie.py` — ct-grammar/ct-red/ct-green/
  ct-merge/ct-audit/ct-live all green (ct-live quarantined under
  `HARNESS_PARALLEL_COPY=1`).
- `python scripts/harness.py doctor` — `commit-tie` reports `ok` on this
  repo's own recent history.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.
