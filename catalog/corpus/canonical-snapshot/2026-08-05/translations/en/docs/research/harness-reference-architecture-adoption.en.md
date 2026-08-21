# Round — Adoption of the Multi-Agent Harness Reference Article

Study of “what should we adopt from X” (playbook `.harness/prompts/research-playbook.md`). External source: *Adaptive, Project-Oriented Multi-Agent Harness Architectures with Dynamic Routing, Self-Correction, and Governed Self-Evolution* — manuscript v1.6, cutoff 2026-07-17, multivocal synthesis + DSR protocol (read in full, 2,414 lines). Internal source: repo capability inventory (scanner, 2026-07-17).

**Status: GATE APPROVED by owner on 2026-07-17** (“approved everything; start with the most critical; revisit the article as we evolve”). Decisions: core N1–N6 in proposed order; EXP-15/16/17 registered (E1–E3); EXP-1 phase 2 greenlit; M0–M7 vision becomes D008 in `DECISIONS.md`.

**Execution (iteration 1, 2026-07-17):** N1 verified ALREADY DELIVERED (CE.1 fixed on 2026-07-12 — seam `_record_executor_outcome`, scenario `ce1_containment.py` 5/5; backlog row was stale and crossed out). N2 SHIPPED: generic `*_escalation` fallback in `compact_supervision_events` (CE.8-lite; essc-6 check) — any raise with escalationId survives wipe without a type-specific branch.

## FACT UPDATE 2026-07-18 — Codex caught up with Claude (document was stale)

Owner flagged this; investigated through primary sources (Codex CLI 0.143–0.144, Jul 8–9 2026). **Several assumptions from this round about “Codex = weaker vendor” became FALSE.** Native capabilities gained that week:

- **Subagents GA** — `.codex/agents/*.toml` (`name`/`description`/`developer_instructions` + per-agent `model`/`model_reasoning_effort`/`sandbox_mode`/`mcp_servers`/`skills.config`). `[agents]`: `max_threads`=6, `max_depth`=1. **Sibling structure to `.claude/agents/*.md`.**
- **Native fork-join** — parallel execution that waits for all results then returns consolidated response; `spawn_agents_on_csv` (map per row with `output_schema`). Multi-agent **v2** under `collaboration` namespace.
- **Dynamic workflows** — thread forking (“fork history through a specific turn”).
- **Full hooks** — SessionStart, PreToolUse, PermissionRequest, PostToolUse, UserPromptSubmit, **SubagentStart, SubagentStop, Stop**, PreCompact, PostCompact.
- **Sandbox** — “writes app approval mode” + worktrees (`.worktreeinclude`).
- **Our CE.1 fixed natively**: July — parent agents now receive terminal subagent errors rather than empty successful completion.

Sources: learn.chatgpt.com/docs/agent-configuration/subagents; changelog; developers.openai.com/codex/hooks.

**Pending corrections:** (A) `capabilities.json` note “Codex synchronous, no SubagentStop, no mirror” is now FALSE — re-evaluate Codex leg of gate-wait hook (commit f016aa9). (B) `agent_spawn_economy` matches `multi_agent_v1` — verify rename to v2. (C) this section. Bets aligned to owner direction: (D) adopt native Codex fork-join/subagents; (E) native SPEC-113 parity via `.codex/agents/*.toml`. Caveat before changing hook: Codex SubagentStop fires in its INTERNAL multi-agent runtime; we invoke single-shot `codex exec` — whether that path emits events determines Codex gate-wait leg.

### Experimental investigation 2026-07-18 — “Codex has hooks” ≠ “Codex enforces”

Ran Codex 0.144.4 FOR REAL (five execs), rather than trusting docs. Finding reversing optimism: **write enforcement for our Codex workers is INERT, and wiring alone does not fix it.** Three live-proven gaps:

1. **Trust** — `codex exec` only fires hooks with `--dangerously-bypass-hook-trust` (or persisted trust). Experiment 1 without flag: NO hook fired. Experiment 3 with flag: SessionStart/PreToolUse/Stop fired. Our template does not pass flag → Codex worker hooks are **silent** today.
2. **Matcher** — `protect-files` had `Edit|Write|MultiEdit`, excluding native Codex `apply_patch`. FIXED in-session (capabilities.json + vendor files, timeouts preserved; `agents pair --apply` is lossy for these fields — intake).
3. **Payload shape (the killer)** — even with trust + matcher, `protect_files` DID NOT deny: `codex exec` edited protected `AGENTS.md` with hook fully enabled. Root: Codex `apply_patch` embeds path in patch BODY (`*** Update File: <path>`), not `file_path`; `protect_files.candidate_paths()` and `workflow_write_guard` only read `file_path`/`path` → target unseen → fail-open. Codex honors hook deny exit-2 according to docs, but hook never reaches deny because it cannot see target.

**Consequence:** Codex workers can write anywhere, including protected canonical files, today. Fix requires an `apply_patch` body parser in `protect_files` + `workflow_write_guard` (extract `*** Update/Add/Delete File:` and `+++ b/<path>`), PLUS trust flag — not merely hook mirroring. Trust was NOT activated, because doing so with gap 3 open would create false security. Matcher fix and corrected notes were committed. Intake captured. Implication for D/E: Codex-worker containment should come from **NATIVE sandbox** (`sandbox_mode` read-only/workspace-write, “writes app approval”), NOT our path-based hooks — S3 (native sandbox by role) is the right lever for Codex.

### DECISIVE CONCLUSION 2026-07-18 (parser built and proven; sandbox is the requirement)

Continued experimenting (eight execs total). Live-proven facts:
- Captured real `apply_patch` payload: target in `tool_input.command` as `*** Update File: <absolute path>` rather than `file_path`. **Built parser** (`protect_files.apply_patch_paths` + `candidate_paths`, self-check green) extracting target correctly.
- **BUT even with parser + matcher + trust, `protect_files` DID NOT block** Codex editing `AGENTS.md` (three tests). Payload shows `permission_mode: bypassPermissions` — Codex **does not honor hook deny** on this path.
- **`--sandbox read-only` BLOCKED** (“No file change was possible”). → native sandbox is RELIABLE Codex write control; **Codex hooks are advisory, not enforcement.**

**Containment architecture crystallized (multi-vendor + open-model requirement from §5.9/§7.4/§7.5):**

| Layer | Claude | Codex | Open models (HTTP) |
|---|---|---|---|
| Vendor-native inner control | allowedTools + permission mode (deny honored) | `sandbox_mode` (S3) — ONLY reliable write control | **NONE** |
| Path-based hooks | enforce (deny honored) | **advisory only** (deny ignored) | do not run |
| **Harness-owned sandbox (REQUIREMENT)** | reinforcement | covers “protected off-limits” beyond workspace-write | **ONLY possible containment** |

**Confirmed requirement:** open-model workers (`openai-compat`/NVIDIA/Gemini) have no sandbox or hooks — only a **harness-owned sandbox** (fs/proc/net constrained at spawn, vendor-agnostic; §5.9 runtime plane MANDATORY) makes them safe. This is prerequisite for multi-vendor + open models together. Parser remains committed as a **building block** for harness-owned sandbox (observation of what worker attempts to write), not Codex-hook enforcement. Next: design harness-owned sandbox (SPEC-116 door NEW) + extend S3 to Codex native `sandbox_mode` per role.

**EXP-1 phase 2 (same session): implemented, measured and REVERTED.** Head+tail candidates lost MORE decisive lines than head-only in real corpus (345 and 335 vs 312; only firing sample is a giant gate doc with path-dense head). First live application of D008 discipline: metric decides, candidate does not ship; preserved in probe (`truncate_text_head_tail`) with metric-validity finding and retest path (enrich corpus with OUTPUT_CAP chat/ui outputs or preregister tail-weighted metric).

**N3 SHIPPED (same session, minimum scope after fan-out of three recons):** “general epoch” was honestly discarded — no identity shared among five ledgers, and only two gaps WITH incidents were closed: (F1) duplicate-dispatch guard in `tasks_board._dispatch` — fix from incident a6c9af5 existed only in experiment path, sibling task-card path remained open; (F2) `_recover_stale_holds` now refuses (high) to recover a hold belonging to LIVE pid — also becomes missing mutex between concurrent gates. Deferred with record (no incident, C-level): breaker fencing by executor (last-write-wins across runs), lost updates in experiments/tasks/handoff ledgers, presence-only lock in route-loop (accepted ceiling, over-blocks). U1/U2 shipped in 2af7787 (Opus xhigh delegation + ritual).

Next: N4 as read-only retrospective regret probe (feeds EXP-17, zero behavior change), then N5/N6.

## Track S — containment, isolation, and role hardening (owner request 2026-07-17)

Re-read article focused on sandbox/capabilities (§5.5 capability-scoped delegation; §5.7 resource semantics; §7.3 trust zones; §7.4 defense in depth; §7.7/SF-5e containment > approval fatigue; Rule of Two [119]; CaMeL [118]) × two fan-out recons (role enforcement; sandbox/env/egress).

Diagnosis: role enforcement was ~all prose (SPEC-140/142/143 self-declared non-applicable; only 1/9 profiles with `tools:` ceiling); only real block was ui-overseer glob (Edit/Write through allowedTools — Bash remained unconstrained by path); least-privilege env filter (SPEC-119 `filter_spawn_env`) existed only in workflow-worker path — detached dispatch and rooms inherited full env with all secrets.

| ID | Item | Status |
|---|---|---|
| S1 | Env least-privilege in detached dispatch (`cmd_route` → `build_worker_spawn_env`; keep `workerEnvFilter=false` escape hatch) | **shipped in this session** |
| S2 | Add `tools:` ceilings to remaining eight `.claude/agents/` profiles (read roles: no Edit/Write; write roles: no spawn; role-shaped least privilege) | **shipped** |
| S3 | Codex native sandbox mode per role; do not pretend hook parity is enforcement | **promoted after live tests** |
| S4/S5 | Path/egress hardening through harness-owned substrate rather than vendor-only rules | **research/build prerequisite** |
| S6 | Preserve observable escape hatches and fail-closed behavior rather than silent permissive fallback | **shipped/minimalized** |

The key architectural correction from this track is historical but important: “same hook file on two vendors” is not equivalent capability. The actual security property is effect containment, and its trusted substrate differs by runtime.

## Second prospecting wave (recon fan-out 2026-07-18) — verdict

Two article ideas prospected against real code:

- **Approval-digest binding (C12, §7.7) → PROMOTED to core (next, P1).** Mechanism already exists and works: `tools/plan_gate.py:118` writes `planSha256 = sha256(plan.read_bytes())` into grant and rechecks on consumption. Decide inbox (`decision_inbox.apply_decision`) and escalation resolve write only id+choice+note — zero binding, TOCTOU open. Cheap seam: port one-line sha256 into `apply_decision`, same grant form, no new state.
- **ContextLedger-lite / A_ctx (§4.1/§6.2) → DEFERRED with trigger.** CE.2 (`cost_metrics.record_workflow`) already shipped but measures `communicationAmplification = input/output tokens` — DIFFERENT ratio from article A_ctx (presented/unique). Denominator “unique logical tokens” exists nowhere: `context_digest.py` deduplicates read lists by identity, does not count bytes/tokens per unique item. Real cost requires token count per unique digest input, not zero-state like CE.2. Revisit trigger: measured context-budget pressure or multi-worker duplication becoming dominant cost (signal already in delegation-cost-trend).

### Parked (over-engineering at current stage; article itself is evidence-gated)

Full Effective Constitution Compiler; typed workflow IR with soundness proof; full EDC (factorial designs, sealed holdouts); dynamic AHHI profiles by task; full ATP with signature/hash-chain. Revisit with real multi-tenant.

### Rejected (counter-evidence)

Learned router now; automatic generation of context files; multi-agent by default; append-only memory; self-evolution beyond anti-Hive invariant.

## AFK loop 2026-07-18 — core queue exhausted; N5/N6 deferred by discipline

Overseer loop swept approved queue. Shipped: N1–N4, U1–U2, S1–S3, S6, C12 (8 commits: 4a326c5, 5b82952, 2af7787, 5e7091f, 6ca15dd, 8bec647, 7c1c960, 1f963c0); EXP-1 phase 2 measured-and-reverted; EXP-15/16/17 registered. Last two core items deferred by evidence-gated decision, not blockage:

- **N5 (R0–R3 tiers in vocabulary) — DEFERRED.** Pure vocabulary without consumer = no-behavior-change → SPEC-116 “no artifact” exit. Scale already referenced here through article. Trigger: a gate/owner-gate consuming tier.
- **N6 (claim lifecycle + doctor advisory) — DEFERRED.** Recon confirmed no trustworthy claim-date field; proxy via NEXT_STEPS mtime is theater (rewritten every workflow, always fresh → never fires); real version (`valid-until` + writer changes) is larger and speculative without incident. Seam mapped and clonable (EXP-2 pattern in `repo_health.checks`, id in `rh_repo_health.py` IDS). Trigger: first expired claim that misleads a run.

**Loop finding captured as intake:** `subagent_gate_wait.py` (SubagentStop) holds read-only recon until gate settles even without touching `.harness` — three stalls measured (~660s/32k tokens each). Proposed fix: immediately release subagent without writes/`.harness` mutation.

### Next prospecting batch

> **SUPERSEDED 2026-07-18:** TOTAL manuscript coverage (every item, not just critical ones) lives in `docs/research/article-coverage-backlog.md` — use that document for next queue. Four items below remain historical.

1. ~~**Co-failure reporting in reduce**~~ **PROSPECTED AND RESCOPED 2026-07-18.** Recon killed literal β_C here for two honest reasons: (a) no oracle — status is 100% self-reported, so “wrong” is unmeasurable; (b) our fork-join workers are role-differentiated (`ideator-*`, `critic-*`), not N role-symmetric attempts at same task assumed by β_C [101]. A β_C probe would be theater. **Honest version delivered:** `testing/probes/exp15_fanout_convergence_probe.py` measures CO-DETECTION of findings (`sourceWorkerIds` already computed by reduce), the marginal-contribution question (§5.5a), explicitly NOT β_C. Measurement on activated EXP-15: **unique-rate=1.0, convergence=0.0** in five fork-joins (83 findings, ALL from one worker). Two interpretations probe cannot disambiguate: (a) fan-out buys pure coverage; (b) dedup key is too strict for semantic agreement.
   **Candidate probe 2026-07-18 (LOOP QUEUE 4 L6, measure-only): normalization hypothesis REFUTED.** Two candidate keyings measured on real 83-findings corpus: `normalizedTitleCategory` (strip enumerative prefixes) merged ZERO pairs — convergent titles are PARAPHRASES (“Mock-vs-real matrix” ⇔ “flight simulator vs wind tunnel”), not enumeration; `categoryFirstEvidence` merged 1/83 (genuine but immaterial). Distance to manual truth: 1.0 for all three including baseline. Conclusion: string-key change in `normalize_finding_key` does NOT recover semantic convergence without semantic matching (high cost, no trigger). Artifact `.harness/runs/exp15-dedup-candidates-*.json`.
   **DISAMBIGUATED 2026-07-18** by manual sample of WF-...162849: (b) confirmed. Five workers surfaced SAME five ideas with different prefixes. `normalize_finding_key` title+category+evidence did not merge because TITLES differ. `unique-rate=1.0` is INFLATED; real convergence nearly total → on this fork-join fan-out bought **redundancy, not coverage** (signal for single-agent on this class; EXP-15). Concrete owner-gated derivative: normalize enumerative prefixes before keying OR dedup by category+evidence without title; risk: over-merge genuinely distinct findings.
2. **Replay-class in events** (§8.2) — additive `exact|approximate|external` per event; cheap, aligns with ATP replay discipline.
3. **Approval SLO/expiry in decide inbox** (§7.7) — approval expires; no reviewer within SLO → safe pause. Extends shipped C12 (plan-gate grants already have expiry).
4. **Trace-completeness report** (§8.1) — R2/R3 blocked by missing authorization/effect/validation evidence. Larger; depends on naming R0–R3 (N5).

## UX (validation + two items)

Current design (gatekeeper façade → explicit rooms when topology matters, typed decide inbox, plan HUD) **independently converges with AHHI** — external confirmation of direction, not gap. New items: (U1) visible room/worker lifecycle states — “disappeared from chat is not a state” (with N3); (U2) level-0 takeover card: objective, owner, next effect, recovery path — extension of existing plan HUD.

## Business view

1. **Named category:** article establishes “harness engineering” as evaluable, multi-vendor architectural object — exactly this repo’s product. Article thesis (probabilistic adaptation inside deterministic validated action space) already matches current architecture (gate + hooks + owner gates).
2. **Defensible differentiators in article’s light:** vendor-neutral canonical layer (`.harness/`), cheap-first economy (discover/doc-find), anti-Hive invariant (evolution with separate authority — risk article discusses and we close by design), multi-vendor rooms. With 2026-07-18 update, Codex reached native parity for subagents/workflows, making C3VR a real competitive field between two capable vendors rather than embryonic feature.
3. **M0–M7 instrument as product:** maturity assessment (§11.3) is commercial framing for `targets` verb (SPEC-110): assess adopting repo’s harness maturity and prescribe path. Today: us ≈ M2–M3; core roadmap closes M2 for real (C1/C2 are prerequisites of “governed”).
4. **Credibility through honest evaluation:** matched-budget (E1) and noise floor (A3) become rare technical-marketing material — few competitors publish sampling/noise controls.

## Traceability

| Evidence | Problem | Item | Post-gate destination |
|---|---|---|---|
| C1 + CE.1 | silent failure becomes expensive success | N1 | `agentic-async-await.md` amendment + fix |
| C2 + CE.8 | security alert disappears on wipe | N2 | event-log seam + doctor |
| C3 + Jul-2026 incidents | stale run commits state | N3 | short ownership-epoch spec |
| C4 | router without measurement | N4 | SPEC-144 amendment |
| C7 | context claims rot | N6 | doctor advisory |
| C5/C35-36 | multi-agent cost unproven | E1/E2 | `experiment add` |
| C4 | RF.1 phase 2 unjustified | E3 | `experiment add` |
| C16 | positioning | business §3 | `DECISIONS.md` |

## HUMAN GATE — decisions requested from owner

1. **Approve buckets?** Core N1–N6 in proposed order (N1/N2 are P0 already recognized by backlog — article supplies principle and correct fix)?
2. **Register E1–E3** in experiment registry (`experiment add`)?
3. **EXP-1 phase 2** (tail-preserving truncation, currently owner-gated) greenlit? E2 partly depends on it.
4. **Critique wave** (`research-critique`, ~60k tokens) over portfolio before promotion, or promote directly (article already embeds external critique)?
5. **Business vision §3** (M-scale as instrument for targets) enters `DECISIONS.md` as direction?
