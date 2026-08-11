# Audit: prompt-injection surfaces (phase-0 baseline for playbook-compiler)

Read-only inventory, 2026-07-29. Method: `harness.py playbook <role> --verify/--compose`, direct
execution of the SessionStart hooks with stdout byte counts, `.claude/settings.json` hook
enumeration, targeted source reads. Counts are UTF-8 bytes/chars as emitted.

## 1. Surface table

| # | Source file | Injection mechanism | Consumer role | Bytes |
|---|---|---|---|---|
| S1 | `AGENTS.md` | codex loads it natively; on Claude it is NOT ambient (the hook skips it, `tools/hooks/reload_context_after_compact.py:158`) - it reaches the model only via `playbook --compose` or an explicit read | every role (nominally) | 12991 |
| S2 | `CLAUDE.md` | vendor-native ambient (Claude project memory), always on | every Claude session | 3309 |
| S3 | `.harness/prompts/overseer-warmup.md` | SessionStart hook `_assemble()` appends it for EVERY role (`reload_context_after_compact.py:95-99`) | all roles, incl. delegated workers | 1572 (1611 with the `## <rel>` header) |
| S4 | `.harness/prompts/overseer-playbook.md` | ambient-core block via `_role_chain_parts()` (`:139-176`); FULL text only via `--compose` | overseer + all overseer-derived | 22924 file / 1579 injected |
| S5 | `.harness/prompts/overseer-loop-playbook.md` | chain member; NO ambient block -> 1200-char head fallback (`_CHAIN_HEAD_FALLBACK`, `:137`) | loop-overseer | 10136 / ~1330 |
| S6 | `.harness/prompts/research-playbook.md` | chain member, head fallback | research | 17600 / ~1330 |
| S7 | `.harness/prompts/subagent-contract.md` | chain member (head fallback) + named for reading in `build_prompt` (`scripts/harness.py:548`) | worker + all 20 worker-class roles | 13465 / 1325 |
| S8 | `.harness/prompts/testing-playbook.md` | chain member, head fallback | implementer, review | 11586 / ~1330 |
| S9 | `.harness/prompts/implementer-packet.md` | chain member, head fallback | implementer | 2101 / ~1330 |
| S10 | `.harness/prompts/backlog-groom-playbook.md` | chain member | groom-miner | 4635 |
| S11 | `.harness/prompts/router-playbook.md` | chain member | router | 2282 |
| S12 | `.harness/prompts/room-overseer.md` | chain member | room-overseer | 2570 |
| S13 | `.harness/prompts/ui-overseer-playbook.md` | chain member | ui-overseer | 703 |
| S14 | `.harness/prompts/security-auditor-playbook.md` | chain member | security-auditor | 764 |
| S15 | `.harness/prompts/front-desk.md`, `.harness/prompts/harness-operator.md` | NOT in `playbook-registry.json` roles -> reach no model via any chain (read-on-demand only) | none | 3649 + 4098 |
| S16 | `.harness/prompts/task/00-start-here.md`, `01-execute-task.md`, `02-review.md` | task-prompt templates, read on demand | worker | 228 / 259 / 308 |
| S17 | canonical state files (`context_checkpoint.REQUIRED_RELS`: NEXT_STEPS.md, handoff.md, checkpoint-trail.md + 2 pointers) | SessionStart hook, `render_reinjection` (`scripts/harness_lib/context_checkpoint.py:242`), per-file `FILE_CAP = 4000` (head 3200 + tail 600, middle dropped) | every non-worker session | 3326 today |
| S18 | `tools/hooks/acceptances_session_surface.py` | SessionStart stdout | owner/overseer | 471 |
| S19 | `tools/hooks/prompt_slots_session_surface.py` | SessionStart stdout (silent when no drift) | overseer | 0 today |
| S20 | `tools/hooks/overseer_model_guard.py` | SessionStart + UserPromptSubmit stdout | overseer | 0 today |
| S21 | `tools/hooks/spec_intake_triage.py` | UserPromptSubmit stdout, per turn, conditional | overseer | 0 on empty input |
| S22 | PreToolUse guard denials/reminders (10 hooks, e.g. `graphify_search_guard.py` before Glob/Grep) | tool-result text, per call | any role that trips them | variable, unmeasured |
| S23 | `.claude/agents/*.md` (10 profiles) | Claude spawn system prompt: frontmatter pins model/effort/tools, body is the packet preamble | the spawned subagent | 441-1568 each, 7418 total |
| S24 | `build_prompt()` (`scripts/harness.py:542-553`) + `token_economy_line` + `ACCEPTANCE_CONTRACT_PROMPT` / `PLANNER_GUARDRAIL_PROMPT` + the `packet_economy` output-cap suffix | harness-composed spawn packet (argv, or a packet file the worker is told to read) | external/dispatched worker | 425 (scan) - 1147 (plan) |
| S25 | `.harness/routing/task-profiles.json` `tokenEconomy.allowedSkills/allowedMcp` | rendered to ONE prompt line by `token_economy_line` (`scripts/harness.py:524-540`) | dispatched worker | 21493 file, ~1 line injected |
| S26 | vendor/plugin `SubagentStart` context (observed live: a persona block prepended to this scanner run) | vendor-side; NOT wired in `.claude/settings.json` | every subagent | not repo-controlled, unmeasurable here |

Notable: `harness-operator.md` + `front-desk.md` (7747 bytes) are prompt files that no registered
role chain references - dead injection surface, or evidence that the registry is not the complete map.

### Budget enforcement sites (file:line)

- SPEC-138 warm-up budget (40 lines / 3200 bytes) is NOT enforced in the code that injects it.
  It is enforced only by a scenario assertion: `testing/scenarios/osw_overseer_warmup.py:42`
  (`text.isascii() and len(lines) <= 40 and len(raw) <= 3200`); spec
  `specs/40-features/overseer-warmup.md:68` (`[osw-1]`); the doc self-declares the budget at
  `.harness/prompts/overseer-warmup.md:5`. Current size 1572 bytes - under half the budget.
- Aggregate SessionStart inline budget: `TOTAL_BUDGET = 9_800`
  (`tools/hooks/reload_context_after_compact.py:50`; vendor inline ceiling 10000 chars, 200 margin).
  Enforced at emit time in `main()` (`:75`) via priority-aware `_fit()` (`:114-131`), which shaves
  ONLY the state part and never the discipline parts; `_BLOWN_LINE` (`:110`) fires when the
  discipline parts alone overflow. Re-checked in-process by the repo_health `reinjection-budget`
  check against `_assemble()` (`:78`).
- Chain-file fallback cap: `_CHAIN_HEAD_FALLBACK = 1_200` (`:137`).
- Per-delegation token budget: `packet_economy._budget_tokens` (`:41`) and `budget_for_agent` (`:80`);
  output-cap contract line in `compose_spawn` (`:51-79`).

## 2. Embryo mechanisms a compiler would build on

- `scripts/harness_lib/playbook_registry.py` - the closest thing to a compiler that already exists:
  `load` (:45), `resolve` (:56, chain via `extends`), `compose` (:87, concatenation +
  `_origin_header` :106), `render` (:111, banner "EFFECTIVE VIEW - inspection only, never a spawn
  input"), `inject_mode` (:125, per-role `compose` vs default list, SPEC-170 rule 18),
  `spawn_compose` (:132), `verify` (:287) with `_lock_drift` (:199), `_h2_sections` (:220) and
  `_collisions` (:250) - the collision detector is already a duplication finder. `write_lock` (:275)
  produces a per-role `chainHash`, i.e. an effective-prompt identity primitive.
  STATE TODAY: `playbook --verify` returns ok=false with `lock-drift` on ALL 32 roles
  (`.harness/routing/playbook-registry.lock.json` is stale) plus 7 `collision` advisories on
  `loop-overseer`. A compiler inherits a registry whose lock is already untrusted.
- `tools/hooks/reload_context_after_compact.py` - the de-facto per-role effective-prompt assembler:
  `_assemble()` (:78), `_role_chain_parts()` (:139) with `_AMBIENT_RE` (:136), and priority-aware
  `_fit()` (:114). Compilation-by-hook: role in, budgeted payload out. `HARNESS_SKIP_REINJECT=1`
  (:63) is the worker opt-out (0 bytes emitted). Only ONE ambient block exists in the whole repo
  (`.harness/prompts/overseer-playbook.md:8`), so every other chain file ships a blind 1200-char head.
- `scripts/harness_lib/prompt_slots.py` - vendor-slot identity: `_sha` (:49, sha256[:16] of scalar
  values), `read_slots` (:54, hashes and shapes only, never text), identity is the `(name, sha)` PAIR
  and never the opaque slot key (:113-117), `diff` (:111) tri-state new/changed/removed,
  `alerts` (:140), `record_drift` (:149), `doctor_check` (:166). Directly reusable as the
  "did my effective prompt change" primitive.
- `scripts/harness_lib/packet_economy.py` - `compose_spawn` (:51) already returns
  `{env, budget{estTokens,budgetTokens,over}, promptSuffix}`: the seam where a compiled prompt would
  be sized and capped. `_self_check` (:101) is the existing test hook.
- `scripts/harness.py:542` `build_prompt` + `:524` `token_economy_line` - a SECOND, independent
  prompt assembler (profile-driven, not registry-driven). A compiler must reconcile the two:
  registry chains and `task-profiles.json` profiles are parallel role taxonomies (32 roles vs 12
  profiles).
- Capability-panels role scoping: `specs/40-features/capability-panels.md:138` ("READ-ONLY /
  ADVISORY: CAP.3 only SURFACES the gap. It adds NO ... enforcement/blocking") and `:159-161`
  ("The badge is advisory, not enforcing ... Discovery != grant != enforcement"). GAP CONFIRMED,
  and independently restated at `.harness/prompts/overseer-warmup.md:10` ("per-role ENFORCEMENT is a
  TRACKED GAP (only graphify is role-gated today)"). The declared allowlist lives in
  `.harness/routing/task-profiles.json` `tokenEconomy`; on the Claude side the only real ceiling is
  `.claude/agents/*.md` frontmatter `tools:` (e.g. `scanner.md:6`) - `token_economy_line` itself
  states "Enforcement is contractual (prompt text)".

## 3. Duplication map (rules restated across more than one injected surface)

Quoted by first line + file:line.

1. **Standing delegation grant / delegation discipline** - 3 surfaces:
   - `AGENTS.md:74` "**STANDING DELEGATION GRANT (owner, ratified 2026-07-29 - SEC.8 counter-lever).**"
   - `.harness/prompts/overseer-warmup.md:14` "6. Standing owner grant (SEC.8): delegation to subagents/workflows/deep research ..."
   - `.harness/prompts/overseer-playbook.md:61` "## Delegation fuel check (owner 2026-07-23 - every delegation, loop or not)"
2. **Graphify policy** - 5 surfaces, four of them restatements:
   - `AGENTS.md:45` "## Mandatory structural discovery: Graphify" (canonical, 8 numbered rules)
   - `CLAUDE.md:17` "Claude must follow the mandatory Graphify-code-AST-first Graphify policy in `AGENTS.md`."
   - `.harness/prompts/subagent-contract.md:68` "For non-trivial repository search or cross-file reasoning, report Graphify ..."
   - `.claude/agents/*.md:15` - the SAME paragraph "Follow the Graphify policy in `AGENTS.md`. For broad or cross-file discovery ..." duplicated VERBATIM in all 10 spawn profiles
   - `tools/hooks/graphify_search_guard.py` - a PreToolUse reminder saying it again at Glob/Grep time
3. **HARNESS_RESULT envelope obligation** - `AGENTS.md:80` "End non-trivial work with a `HARNESS_RESULT` JSON block as described in ..." vs `.harness/prompts/subagent-contract.md:8` "## HARNESS_RESULT" (the schema) vs every `.claude/agents/*.md:10` ("... and end with HARNESS_RESULT") vs `scripts/harness.py:548` (build_prompt telling the worker to read the contract). Four statements of one rule.
4. **Escalation instead of scope widening** - `AGENTS.md:76` "If escalation is needed, return `requiresEscalation: true` ..." and `AGENTS.md:102` "If the task touches auth, secrets, dependencies ..." vs `CLAUDE.md:11` "If a task appears under-scoped or risky, return a structured escalation request ..." vs `scripts/harness.py:520` (`ACCEPTANCE_CONTRACT_PROMPT` tail) "If no approval channel is available, return status blocked with requiresEscalation true".
5. **`.harness/` is canonical / no canonical state in `.claude/`** - AGENTS.md doctrine, restated at `CLAUDE.md:7-9` and again at `CLAUDE.md:17` (".harness/ remains the source of truth").
6. **loop-overseer chain self-collisions (7, machine-detected by `playbook --verify`)** - identical H2 headings in BOTH `.harness/prompts/overseer-loop-playbook.md` and `.harness/prompts/overseer-playbook.md`: "Roles (non-negotiable)", "Plan-brief template (every brief has exactly these sections)", "Launch recipes", "The review ritual (per completion - never skip a step, never trust a report)", "Known failure modes (all observed live 2026-07-13)", "Escalation contract (when the overseer STOPS instead of deciding)", "WF cycle-time disciplines (workflow-efficiency round 2026-07-20)". A `loop-overseer --compose` ships both copies.
7. **Warm-up injected to workers that are told to ignore it** - `.harness/prompts/overseer-warmup.md:3` "If you were spawned as a delegated worker, obey your packet + subagent-contract; the discipline below is the OVERSEER-s, not yours." The hook appends this file unconditionally for EVERY `HARNESS_SESSION_ROLE` (measured: 1611 chars inside the `worker` payload). The disclaimer is the workaround for the missing role scoping.

## 4. Totals: bytes injected per role at session start

Method: ran `tools/hooks/reload_context_after_compact.py` with `HARNESS_SESSION_ROLE=<role>` and
counted stdout bytes (that IS what enters the window); separately called `_assemble()` in-process for
the part breakdown; ran `playbook <role> --compose` for the full-contract cost the head directive
instructs the session to pay. CLAUDE.md is counted at file size (vendor-native ambient); the vendor
SubagentStart persona is noted as unmeasurable from the repo.

| Role | hook stdout | head | state | protected parts |
|---|---|---|---|---|
| overseer | 6854 | 194 | 3326 | 1611 (warm-up) + 1579 (overseer-playbook ambient core) |
| worker | 6617 | 192 | 3326 | 1611 + 1325 (subagent-contract head) |
| implementer | 9361 | 197 | 3326 | 1611 + 1330 + 1331 + 1329 (4 chain heads) |
| research | 8225 | 194 | 3326 | 1611 + 2 chain parts |

`playbook <role> --compose` sizes (the full contract, on demand): overseer 36342, worker 26789,
scanner 26789, implementer 40790, research 53991.

**Overseer session (owner, today), at session start: ~10,634 bytes**

- SessionStart reinjection 6854 + `acceptances_session_surface` 471 + prompt-slots 0 + model guard 0
- CLAUDE.md vendor-ambient 3309
- AGENTS.md (12991) is NOT injected on Claude; the head directive instead tells the session to run
  `playbook overseer --compose` = 36342. If obeyed, the real overseer session-start cost is
  ~46,976 bytes (~12k tokens).

**Delegated worker (Claude subagent): ~10,000-13,000 bytes, bimodal**

- SessionStart reinjection 6617 when the spawn does NOT set `HARNESS_SKIP_REINJECT=1`; 0 when it does
  (`reload_context_after_compact.py:63`). Both paths exist in the repo, so this is a range.
- `.claude/agents/<profile>.md` body 441-1568 (scanner 645)
- CLAUDE.md vendor-ambient 3309
- vendor SubagentStart persona block: observed non-trivial (a whole persona doc), not repo-measurable
- harness-composed packet when dispatched via `spawn_command`: 425-1147 (`build_prompt`) plus the
  hand-written task text from the overseer
- `worker --compose` if the contract is actually read: 26789

## Confidence / limits

- Measured, not estimated: all hook stdout, `--compose` sizes, `_assemble()` parts, file sizes.
- Not measured: PreToolUse guard reminder volume per session (S22), the vendor SubagentStart payload
  (S26), and UserPromptSubmit hooks under real non-empty input (S21).
- `playbook --verify` is currently RED (32 lock-drift findings): treat registry hashes as stale.
