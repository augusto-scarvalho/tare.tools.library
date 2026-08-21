# Spec recovery — PLAN-shaped corpus scan (DRAFT — NON-CANONICAL)

Phase 3 of spec archaeology. Where Phase 1-2 (`INDEX.md`, `chat-mined.md`) mined
code/git/backlog/transcripts, this pass mines every place the project wrote down
**intent to build**: `tasks/**/PLAN.md`, `specs/**/*.intake.md`, `docs/roadmap/*`,
`docs/research/*`, the two `*_IDEATION.md` docs, and `.harness/context/DECISIONS.md`.
For each promised item: did it **land** (spec+code+scenario), is it **tracked** (live
backlog/intake-queue row), or did it **ESCAPE** (promised, absent everywhere)?

Nothing here edits `specs/`, `testing/`, `AGENTS.md`, `CLAUDE.md`, `.harness/`, or
other `docs/spec-recovery/*` files. Nothing here is authoritative. `= rec-X` / `= cm-X`
marks overlap with the two prior passes (not re-reported as new finds). Inferences are
marked `inferred`; every claim cites a file/commit/scenario.

Method: 4 scanner subagents, one per corpus slice (tasks+intake / roadmap batch 1 /
roadmap batch 2 + ideation + decisions / research verdict-tables), each reading source
docs against `specs/40-features/`, `testing/scenarios/`, `docs/IMPLEMENTATION_BACKLOG.md`,
`.harness/state/intake-queue.json`, and `git log`.

## Headline

**~159 planned items scanned across 39 documents. The corpus is remarkably well
reconciled** — the 2026-07-13 AFK loop mirrored nearly every roadmap doc's
"proposed-backlog-rows" table 1:1 into `IMPLEMENTATION_BACKLOG.md`, and the
intake-queue that shipped that day (= cm-6) is exactly the triage mechanism whose
absence caused this drift. Result: **only ~9 genuine escapes**, most low-risk and
clustered in the one speculative doc (`SUPERVISION_UI_IDEATION.md`) where a high escape
rate was expected. The higher-value findings are the **divergences** (shipped ≠ planned)
and one **tracked-but-unshipped P0** that the scan re-surfaced.

## Consolidated ESCAPED + landed-but-diverges — ranked by risk

| # | Item | Kind | Where promised | Risk | Why it matters / recommended action |
|---|---|---|---|---|---|
| P-1 | Leaked PrintIntel `GEMINI_API_KEY` never rotated | ESCAPED | `tasks/harness-self-improvement/PLAN.md:19` + KB:92 | **H** | A real committed credential in a target `.env` is still live; no harness task can close it (needs owner to rotate upstream), so it fell off every tracking surface. **Action: file a one-line owner-action reminder** — the only security follow-up with no home. |
| P-2 | Per-item / `--interactive` controlled-write approval (diff-by-diff) | ESCAPED | `SUPERVISION_UI_IDEATION.md §5` | **M** | Today `I_APPROVE_CONTROLLED_WRITES` approves the whole batch; no diff-by-diff stepping exists. The riskiest track (writes to target repos) has the coarsest gate — approve-all or nothing. Absent from backlog/Deferred/intake. **Action: owner keep-or-drop decision; if keep, a small Deferred row.** |
| P-3 | Black-terminal Phase-1 mechanical sweep (~20 sites → `run_quiet`) | diverges | `docs/roadmap/black-terminal-windows.md:116-128` | **M** | = cm-5 / rec-wf-19. Doc promised routing ~20 git/taskkill/records sites through `run_quiet`; shipped `no-raw-subprocess-gate` instead **baseline-froze 28 raw sites** (`targets.py:145`, `harness.py:80-82` still raw `subprocess.run`). Supervisor-console symptom is fixed, but any console-less parent (pythonw panel, IDE git hook) can still flash from a frozen site. **Action: confirm the felt bug is actually gone on the operator's machine, don't assume the ratchet closed it.** |
| P-4 | Deep-research handoff-budget generator defect | ESCAPED | `docs/research/deep-research-pipelines.md` Phase-3 finding #4 | **M** | `generate_handoff` regenerates handoffs that then fail their own `workflow:handoff-context-pack` budget gate (>maxRequiredReadTokens 5000). Phase-3 restored the passing committed handoff but only logged a draft task — no backlog row tracks the generator defect. Latent: bites whoever next regenerates a handoff. **Action: file a backlog row for the generator, not just the artifact.** `inferred` (draft-task-only). |
| P-5 | svc-autostart: workflow(target) settle-stop owner hook still OPEN | diverges | `docs/roadmap/dependency-bootstrap.md:130-133` | M | `svc-autostart-owners` (backlog:416 ✅) shipped **panel+chat only**; the doc's *primary* wiring — the workflow owner that stops services on settle — is folded-forward into the unshipped `svc-mcp-wiring` (backlog:417). **Action: confirm the workflow owner is intended for P2, or pull it forward.** |
| P-6 | Nielsen UX round — all 6 núcleo heuristics + `knowledgeDomain` profile flag | ESCAPED | `docs/research/nielsen-genai-agent-ux.md` Portfólio | L-M | The **only research round whose entire portfolio never reached the backlog** — left at "próximo: intake (decisão do dono)" that never happened. These are supervision-UX *heuristics* (probabilistic-state visibility, reversibility-proportional approval, calibrated-severity alerting), i.e. panel-design constraints, not features — so low feature-risk, but if the owner meant them as SPEC-114 design guidance they're silently lost. Also flags an untracked process bug: a `knowledgeDomain: true` profile flag to exempt knowledge rounds from scope-empty/sourceFilesVerified rules (3 false-invalidations that day). **Action: one owner triage — file as design-guidance doc-ref or explicitly drop.** |
| P-7 | `--dry-run` / preview on `workflow execute` + `apply-merge` | ESCAPED | `SUPERVISION_UI_IDEATION.md §5, Phase 1.3` | L-M | Dry-run exists for `agents pair`, `research delete`, `prune_worktrees` — but not for the two token-spending workflow verbs the ideation named ("preview packets/merge-plan/locks before spending tokens"). The GUI confirm-screen this was meant to seed will re-derive it. **Action: low-priority Deferred row.** |
| P-8 | MAST failure-class tagging on gate failures/escalations | ESCAPED | `SUPERVISION_UI_IDEATION.md §3b/§6` | L | M5.3 ranks escalations by blast-radius (landed), but the root-cause taxonomy tag (specification / misalignment / verification class) is absent everywhere. The queue groups by severity, not root-cause; trend-by-failure-mode (the doc's stated payoff) stays impossible. **Action: note as a small enhancement or drop.** |
| P-9 | en-default guard shipped ahead of the string conversions it guards | diverges | `docs/roadmap/terminology-en-default.md §3.1-3.2 vs §4` | L | = rec-gui-7. `en_default_guard.py` (SPEC-122) lands, but Phase-1/2 PAGE→EN conversions (~75-90 pt strings listed §1a) are tracked-open. Either conversions shipped alongside or the guard is narrowly scoped; if not, the gate should be red. **Action: verify guard scope vs conversion completeness.** `inferred`. |
| P-10 | Multi-model side-by-side compare (A/B spawn) | ESCAPED | `SUPERVISION_UI_IDEATION.md §3 (Conductor)` | L | No A/B spawn-compare surface; nearest is SELF_EVOLUTION I4 variant-eval, itself Deferred. Speculative. **Action: leave escaped unless a demand signal appears.** |
| P-11 | `graphify_search_guard` hook wording → "active provider" | ESCAPED | `docs/roadmap/screens-config-graphs.md §B risks` | L | After `graph-provider-abstraction` shipped (backlog:286 ✅), the search-guard hook text still says "Graphify". Cosmetic; minor operator confusion once a non-graphify provider is active. Doc named it in risks, no row. **Action: one-line doc/string fix, opportunistic.** |
| P-12 | docs-audit-refs shipped the "safe half" only | diverges | `docs/roadmap/docs-wiki.md §4.1` | L | `docs-audit-refs` (backlog:300 ✅) landed banners + B3/B4; the SPEC-105-ghost ref fix (B1) is escalated-pending (owner-decision #4), not silently dropped. **Action: none — awaiting the parked decision.** |
| P-13 | D006 per-role tailoring — two numbered token-riders unshipped | diverges | `.harness/context/DECISIONS.md D006` | L | Core landed (`rs:packet-dedupe`, `rs:openai-packet-trim`); two deferred-with-numbers extensions remain (digest→non-research profiles −7,615 tok/worker; slice HTTP contract −2,096 tok/call). Pure token optimization. **Action: leave as tracked-deferred riders inside the decision.** |

## Tracked-but-notable (not escaped, but worth the owner's eye)

- **`target-gate-env-filter` (backlog:359, P0, UNSHIPPED)** — `gate_generic.run_target_commands`
  (`scripts/harness_lib/gate_generic.py:177`) still runs target build/test with the full
  `os.environ`; a target Makefile can read every API key + sibling-target secrets. This is
  the **highest live risk in the whole scan** — but it is properly tracked as a P0 row, so
  it's a "do it" not a "find it." (Note: the isolation-roadmap `target-gate-env-filter` in
  `cross-project-isolation-data.md` was re-verified *landed* at backlog:145; this SEC-side
  row #359 is a distinct, broader instance still open — worth confirming they aren't the
  same fix double-counted. `inferred`.)
- **Backlog staleness (one-char fixes):** `spec-index` (backlog:257) and
  `security-baseline-mvp` (backlog:350) rows render unstruck though both shipped (commits
  `5842380`, `e16c0b5`). `tasks/gui-flow-composer/PLAN.md` boxes N2 and N3 are unticked
  though both demonstrably shipped (SPEC-120 / SPEC-114 v8). Cosmetic; refresh when convenient.
- **TASK-003 (`printintel-products-split`)** is wholly OPEN/unstarted (products.py = 1861
  lines, target ≤800) but correctly tracked as a live high-criticality escalation
  (`escalations.json:957`), so not escaped.

## Top-10 worth judging together (for the owner)

1. **P-1** — leaked PrintIntel `GEMINI_API_KEY` rotation: the one security item with no
   tracking home, closable only by an owner action. File it or it stays invisible.
2. **`target-gate-env-filter` P0 (backlog:359)** — tracked but unshipped; the biggest live
   secret-exfil surface. Confirm it's not the same fix as the already-landed isolation-side
   filter before scheduling.
3. **P-3 / cm-5 / rec-wf-19** — black-terminal Phase-1 diverged (ratchet-froze 28 sites
   instead of sweeping them). Verify the felt console-flash bug is actually gone, not just
   the supervisor subtree.
4. **P-2** — per-item controlled-write approval: batch-only is the coarsest gate on the
   riskiest track. The only escape with a genuine security edge. Keep-or-drop decision.
5. **P-4** — handoff-budget generator defect: latent, will bite the next regeneration;
   only a draft task tracks it. Promote to a backlog row.
6. **P-6** — the entire Nielsen UX round escaped to an owner-intake that never fired. One
   triage: adopt as SPEC-114 design guidance or explicitly drop (+ the `knowledgeDomain`
   process-bug flag riding along with it).
7. **P-5** — svc-autostart's workflow owner hook (the doc's primary wiring) is OPEN inside
   `svc-mcp-wiring`. Confirm intended deferral.
8. **P-9 / rec-gui-7** — en-default guard shipped ahead of its conversions; verify the gate
   isn't guarding an unfinished migration.
9. **P-7 / P-8 / P-10** — three low-risk SUPERVISION_UI ideation escapes (workflow dry-run,
   MAST tagging, multi-model compare): batch-decide keep-as-Deferred vs drop.
10. **Backlog/PLAN staleness** — strike shipped rows 257/350, tick PLAN boxes N2/N3. Trivial,
    but this hygiene is exactly what keeps the *next* archaeology pass from re-finding them.

---

## Per-document detail

Compact tables. ESCAPED/diverges elaborated above (referenced by P-#); here they're one line.

### tasks/gui-flow-composer/PLAN.md (TASK-004)
| item | where | status | evidence |
|---|---|---|---|
| N1 `plan --validate-only` | §N1 [x] | landed | SPEC-119 v6 r28-30; `wv_validate_only.py` |
| N2 renderer SVG DAG + forms | §N2 `[ ]` | landed (box stale) | SPEC-120 `flow-composer.md`, commit `da3ea21` |
| N2b/N2c create/discard step | §N2 [x] | landed | SPEC-120 v2 `c213a7d`; SPEC-114 v10 `discard:*` |
| N3 flight-strip attention | §N3 `[ ]` | landed (box stale) | SPEC-114 v8 r47 `attention:*` |
| N4 recovery console | §N4 [x] | landed | SPEC-114 v9 `recovery:*`; `workflow doctor` |
| E5 durable board + `workflow doctor` | Experimentos | landed | `cmd_workflow_doctor`; `async-recover` |
| E6 budget badges | Experimentos | landed | SPEC-120 v3 `e09b4d3`; `composer:budget-badges` (research-doc §5 view of this as escaped is **stale** — commit+scenario exist) |
| E7 compose-time secret-scan | Experimentos | landed | SPEC-120 inv.; `validate_workflow_plan` secret-scan |

8 items: 8 landed (2 checkbox-stale). No escapes.

### tasks/harness-self-improvement/PLAN.md (TASK-001) — status DONE, 9 phases [x]
| follow-up (line 19) | status | evidence |
|---|---|---|
| Full `bind()` inversion / workflow-state out of harness.py | tracked | backlog `self-lib-file-budget`; self-review inbox:678 |
| harness.py / spec_test_gate.py splits | tracked | MF-fragmentation rows (`maxHarnessLines` guard) |
| Live Gemini smoke w/ real key | superseded | Phase 7 deliberately off in template |
| **Rotate leaked PrintIntel `GEMINI_API_KEY`** | **ESCAPED (P-1)** | absent from specs/backlog/queue |

### tasks/m2h-hardening/PLAN.md (SPEC-108) — executed 2026-07-09
H1–H6 all shipped + self-attested; `supervision-m2h-hardening.md` exists; H3 `workflow scrub`
in `gate_checks_policy.py:117`. No open/escaped items. Historical record.

### tasks/printintel-products-split/PLAN.md (TASK-003) — wholly OPEN
AC1-AC3 all `[ ]`, unstarted (products.py=1861 lines) but tracked via live escalation
`escalations.json:957` (high criticality). No escapes.

### tasks/research-portfolio/PLAN.md (TASK-002) — status DONE, 5 items [x]
E1/E2/E3/F1/M1 all shipped (SPEC-119 v3-v5, `rs:*` checks). Drafts 8-10 (checkpoint-resume)
explicitly rejected. No escapes.

### tasks/TASKS.md — README/policy doc, no promised items. N/A.

### specs/40-features/*.intake.md (3 files)
All three (flow-composer/SPEC-120, research-skill/SPEC-119, worker-live-tail/SPEC-118) have
every acceptance criterion `[x]` with matching spec+scenario. Remaining "open questions" are
design questions deliberately deferred (editable-canvas reopen → D007; auto-trigger waves →
manual; `stream-json` default → documented ceiling). worker-live-tail overlaps rec-gui-1 (the
drawer's secret-redaction gap — already the top INDEX.md finding, not re-reported). No new escapes.

### docs/roadmap/ batch 1 (8 docs)
Every doc's "proposed central-backlog rows" table is mirrored 1:1 into backlog:234-438;
backlog:145-146 re-verifies 5 rows as landed despite open-rendering. Per-item:
- **black-terminal-windows**: Phase-0 helper + Phase-2 gate landed; **Phase-1 sweep diverged (P-3)**.
- **chat-overlays**: R1 chips + R2 plan-HUD landed; R3 gate-tracker + codex-stream-parity tracked (P2).
- **cross-project-isolation-data**: 5 landed (audit-gate, env-filter, records-subject-dim, token-calibration, subject-events); 2 tracked (workspace-state-exclusion:363, target-worker-world:365).
- **cross-project-isolation-escalation**: subject-scope + scoped-HITL landed; handoff-confinement:372 tracked.
- **dependency-bootstrap**: svc-registry landed; **svc-autostart diverged (P-5)**; svc-mcp-wiring:417 tracked.
- **docs-wiki**: docs-tree + banners landed; consolidation/wiki-sources/screen/spec-guard tracked (302-305); B1 ghost-ref escalated-pending (P-12).
- **git-onedrive-path-hygiene**: scrub+gate + doctor(SPEC-123) landed; repo-out-of-OneDrive superseded (done 2026-07-13); email-leak superseded (accepted).
- **pyo3-optimization**: perf-metrics-rung landed; hotspot-watch:294 + pyo3-accel:295 tracked; tracemalloc YAGNI'd.

35 items: 15 landed / 12 tracked / 3 diverges / 4 superseded / **0 escaped**.

### docs/roadmap/ batch 2 + ideation + DECISIONS (10 docs)
- **screens-capabilities**: CAP.1 landed; CAP.2-5 tracked (268-271).
- **screens-config-graphs**: config-keys-cli + keys-vault(=cm-8, supersedes) + graph-provider + graph-metrics landed; GUI rows tracked; **graphify_search_guard wording ESCAPED (P-11)**.
- **screens-memory-records**: mem-snapshot + commit-timeline landed; sum/target rows tracked.
- **screens-specs-research**: spec-index(`5842380`) + research-index landed; GUI/form/checkpoint rows tracked; spec-index row 257 stale.
- **screens-tasks-queue**: tasks-board + tasks-store(=owner-dec#3) + queue-view + queue-cancel landed; enqueue/target/reorder/start tracked (start=owner-dec#1 approved).
- **security-owasp-enforcement**: baseline-mvp(`e16c0b5`) + targets + diff-routing + directive-map + sdd landed (row 350 stale); **target-gate-env-filter:359 tracked P0 — see notable**.
- **terminology-en-default**: guard(SPEC-122) landed; string conversions tracked; **guard-ahead-of-conversions diverges (P-9)**.
- **SELF_EVOLUTION_IDEATION**: ~13 items — 10 landed (MAPE-K, provenance, blast-radius, skill-retrieval, KPI, replay-verify, evolution-audit, zombie-scan, MLAS map), 2 Deferred (I4/I8, trigger-gated), 0 escaped. Unusually clean for ideation.
- **SUPERVISION_UI_IDEATION**: ~17 items — 5 landed, 6 Deferred, 1 superseded (tmux→spawn-command), **4 ESCAPED (P-2, P-7, P-8, P-10)**. The speculative doc, as predicted.
- **.harness/context/DECISIONS.md**: D001-D007 all acted-on; **D006 carries 2 deferred token-riders (P-13)**; no decision is an un-started promise.

~72 items: ~34 landed / ~29 tracked / 5 escaped / 3 superseded / 2 diverges.

### docs/research/ verdict tables (12 docs)
Six "study→named-roadmap" docs mapped 1:1 to their backlog sections with **zero escapes**:
comm-protocols→CE (441-464), code-quality→CQ (504-515), code-security→SEC (529-541),
dynamic-workflows→DW (480-489), ux-ui→UX-GA (567-572), observability→OB (588-593). Two docs
landed via direct same-day commits (memory-context: G3b `4040b37`/R1/G3a/F1/M1; deep-research:
N1-3/E1/E3/seed). RESEARCH.md = pointer file. nvidia-smart-models = landed wiring (batch
rejected, 5 cards + 9 mappings shipped). Escapes:
- **nielsen-genai-agent-ux**: whole núcleo (6 heuristics) + `knowledgeDomain` flag **ESCAPED (P-6)**.
- **deep-research-pipelines**: handoff-budget generator defect **ESCAPED (P-4)**.
- **agent-gui-cli-features E6 budget badges**: research-doc read it as escaped, but it **landed** (SPEC-120 v3, `composer:budget-badges`) — reclassified, not carried as an escape.

~40 items: ~30 landed / ~7 tracked / 2 escaped / rest superseded/rejected-with-trigger.

---

## Summary

- **Documents scanned**: 39 (7 tasks/ + 3 intake + 15 roadmap + 2 ideation + 1 DECISIONS + 12 research; codex/CODEX_* roadmap files are compatibility wrappers pointing at the canonical set, no items of their own).
- **Items scanned**: ~159.
- **landed**: ~92 · **tracked** (live backlog/intake/escalation row): ~55 · **superseded**: ~10 · **ESCAPED**: ~9 (P-1, P-2, P-4, P-6, P-7, P-8, P-10, P-11, + Nielsen's `knowledgeDomain` process-flag) · **landed-but-diverges**: ~6 (P-3, P-5, P-9, P-12, P-13, + N2/N3 checkbox-stale).
- **Of the 9 escapes**: 1 high (P-1, security, owner-action-only), 2 medium (P-2, P-4), 6 low/low-med. Four of them sit in the single speculative `SUPERVISION_UI_IDEATION.md` — exactly where a higher escape rate was expected.
- **Skipped by bound**: deep literature-review prose in the research docs (only verdict/portfolio/next-step sections mined); the codex/CODEX_* wrappers (0 items); non-decision-table body of the two giant research files. Newest-plan priority applied throughout (roadmap > old ideation), per instructions.
- **Cross-pass note**: no escape here contradicts INDEX.md or chat-mined.md; the strongest corroboration is P-3 independently confirming cm-5 / rec-wf-19 as a felt, still-partial fix. The overall low escape count is itself evidence that the cm-6 intake-queue + the AFK-loop backlog-mirroring largely closed the drift this archaeology was chartered to find.
