# EXP-21 probe P1 — do real vendor workers orphan their tool children at timeout?

Run 2026-07-27 on the owner's nt machine. Owner-ratified; the measurement is in
`EXP-21.measurements[]` (`harness.py experiment show EXP-21`). Design: probe P1 of
`docs/research/plan-job-lifetime-DRAFT.md` section 3. This file is the durable
record; the 26 workflow directories the run produced were scrubbed after it was
written.

## Verdict

**The nt async timeout kill leaves the vendor's TOOL CHILDREN alive. The bounded
seam does not.** Both vendors, three counted repetitions per cell, **zero
within-cell variance** — this is deterministic behaviour, not a noisy rate.

| seam | codex | claude |
|---|---|---|
| **async** (timeout kill) | **3, 3, 3** orphans | **5, 5, 5** orphans |
| **bounded** (control) | 0, 0, 0 | 0, 0, 0 |

The vendor CLI itself always died — `vendor-internal` survivors were 0 in every
arm. Only its grandchildren survived. On codex the survivors were a `powershell`
plus the two pythons it had spawned; the sleeper this probe asked for was among
them every time.

The kill was verified to be the TIMEOUT branch, not the cancellation branch:
`returnCode 15`, `run.timeout: true`, `cancellation.requested: false`. This
mattered because the async classification tree matches a cancelled worker and a
crashed one on the same shape (no result + non-zero exit), and a probe that landed
on the wrong branch would have measured the wrong mechanism.

The plan's decision rule, committed before the run — *any nonzero on async with
bounded zero → control justified* — has fired.

## Method

One arm = one vendor × one seam. A 1-worker workflow is planned, its packet
replaced with an instruction to run one long silent command via the agent's own
shell tool, and the workflow is driven through the real seam (`workflow start` =
async, `workflow run` = bounded) with a small `--timeout`. The harness kills the
worker; anything of the worker's still alive after settle is an ORPHAN.

Classification is **by command line, not by tree walking**: Windows keeps stale
`ParentProcessId` links after a parent dies, so a ppid closure taken after the
kill is not trustworthy. The sleeper is identified by its own argv.

The cheapest card is pinned without touching routing config: the active `baseline`
profile already maps role `cheap` to codex `gpt-5.6-luna` and claude `sonnet`, and
the shard's `taskProfile` is a field of the disposable workflow artifact.

**Pre-committed discard rule (owner, before the run):** a round whose pre-timeout
snapshot does not show the child is DISCARDED, never counted as zero. Zero by
model disobedience is not zero.

## Per-arm record (26 arms, 64 minutes)

| # | vendor | seam | timeout | verdict | orphans | first child seen |
|---|---|---|---|---|---|---|
| 1 | codex | async | 90s | counted | 3 | — |
| 2 | codex | bounded | 90s | counted | 0 | — |
| 3 | claude | async | 90s | discarded | — | — |
| 4 | claude | bounded | 90s | discarded | — | — |
| 5 | codex | async | 90s | discarded | — | — |
| 6 | codex | bounded | 90s | discarded | — | — |
| 7 | codex | async | 90s | discarded | — | — |
| 8 | codex | bounded | 90s | counted | 0 | — |
| 9 | claude | async | 180s | discarded | — | — |
| 10 | claude | bounded | 180s | discarded | — | — |
| 11 | claude | async | 180s | discarded | — | — |
| 12 | claude | bounded | 180s | counted | 0 | — |
| 13 | claude | async | 180s | discarded | — | — |
| 14 | claude | bounded | 180s | discarded | — | — |
| 15 | claude | async | 120s | discarded | — | — |
| 16 | claude | async | 120s | **counted** | **5** | 24.7s |
| 17 | claude | async | 120s | discarded | — | — |
| 18 | claude | async | 120s | discarded | — | — |
| 19 | claude | async | 120s | **counted** | **5** | 31.5s |
| 20 | claude | bounded | 120s | counted | 0 | 24.6s |
| 21 | codex | async | 120s | **counted** | **3** | 35.1s |
| 22 | claude | async | 120s | **counted** | **5** | 42.3s |
| 23 | claude | bounded | 120s | discarded | — | — |
| 24 | claude | bounded | 120s | counted | 0 | 28.1s |
| 25 | codex | async | 120s | **counted** | **3** | 24.6s |
| 26 | codex | bounded | 120s | counted | 0 | 59.4s |

26 arms for 12 counted. **The 14 discards are the most useful part of this
record**, so they are accounted for individually rather than summarised as noise.

## The discard accounting — three wrong diagnoses before the right one

Every discard had a nameable cause. None was randomness.

**7 arms — the packet was under-specified (arms 3-4, 9-15).** The first packet was
three lines with no `WORKER_RESULT` contract. The claude worker read it, decided
the instruction looked like a test rather than a job, and went looking for the work
it thought it was missing — `ls` on the workflow directory, then `scope.json` —
finishing `success` in 9 turns without ever running the command. Reasonable
behaviour from the agent; a bad packet from the overseer.

**3 arms — permission denial (arm 15 and siblings).** With the packet fixed, the
worker obeyed exactly and its Bash call came back `This command requires
approval`. A `-p` worker has nobody to approve, so the tool call died and the
worker exited `success`, `is_error: false`. What caught it was not the vendor but
the harness's own receipt contract, which recorded `missing result`. The fix was
not to widen policy: `.claude/settings.local.json` already allows
`Bash(./.venv/Scripts/python.exe *)`, and the probe had used an absolute path,
which does not match that rule.

**4 arms — the window was too short (arms 5-8).** The first tool child appears
24.6–42.3s after launch; at a 90s timeout the margin was thin enough to lose
several rounds outright.

Two of these three diagnoses were wrong when first made. The initial reading was
"claude starts slowly", which produced a 180s timeout that fixed nothing — the
vendor process was in fact visible at 3.6s every time. The measurement only became
possible after reading what the worker actually did, rather than inferring it from
the absence of a result.

**Why this matters more than the numbers:** without the discard rule, the first
seven claude arms would have entered the record as *claude leaks nothing* — the
exact inverse of the measured 5, 5, 5. The rule the owner demanded before the run
is the only reason the claude column is not confidently backwards.

## Not measured — stated, not implied

- **The `mcp` class.** It needs a fabricated target `mcp-config`, and the plan
  itself calls it a future-live population (no target config exists on disk). Not
  measured is not zero.
- **The cancellation branch.** Every counted arm landed on the timeout branch by
  construction. Cancel-branch incidence is argued a-fortiori from mechanism
  identity elsewhere; it was not measured here.
- **POSIX.** nt only. POSIX already reaps via `killpg` and ships no behaviour
  change in the control that follows.

## Deviations from the plan as written

- **Effort `high`, not `low`.** Role `cheap` already routes codex to luna; using it
  costs zero config mutation, and reasoning effort cannot affect process survival.
- **Timeout 90-180s, not ~60s.** The measured 24.6-42.3s first-sight makes ~60s
  unreliable; a future round can use 60s only with that number in hand.
- **Group timeout, not per-worker.** `--timeout` sets `groupTimeoutSeconds`; the
  worker's own record still carries `timeout: true` and `returnCode 15`, so the
  seam's kill is what was exercised.

## Reproducing

The rig lived in the session scratchpad and is not part of the repo (the plan
specifies P1 as owner-run with zero repo code). Its shape, if it is ever needed
again: plan a 1-worker workflow, overwrite `workers/worker-001.prompt.md`, set the
shard's `taskProfile` to `cheap`, drive it through `workflow start` / `workflow
run` with a small `--timeout`, snapshot `Get-CimInstance Win32_Process` every ~3s
during the window and again after settle, and diff by command line against a
baseline taken before launch.

That snapshot primitive is worth remembering for another reason: it enumerates the
full cross-process pid/ppid/command map on nt, which is exactly what the harness
cannot do today (`process_children_map` returns `{}` on nt) and exactly what the
`proc-cancel-graded-destruction` row needs in order to warn an operator what a
cancel is about to destroy.
