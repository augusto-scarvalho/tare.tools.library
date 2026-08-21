# SPEC-119 — Double Diamond research skill over the harness fork-join

Status: SPEC-119, proposed 2026-07-11 (acceptance: `testing/scenarios/rs_research_skill.py`).

## Goal

An activatable, cross-vendor research skill that runs the user's evidence-driven Double
Diamond process (diverge→converge, two research flows, independent ideation waves,
multi-agent critique, set-based convergence, portfolio + traceability) on the harness's
existing fork-join/map-reduce machinery. One canonical playbook drives the orchestrator;
two read-only fork-join profiles supply the divergence and critique waves; an
OpenAI-compatible HTTP worker lets any chat endpoint run a worker without a vendor CLI.

## Applicability

Applies to `.harness/prompts/research-playbook.md` (canonical), the vendor pointers
`.claude/skills/research/SKILL.md` + `codex/prompts/research.md`, `.harness/capabilities.json`
(skill declaration), the `research-divergence` / `research-critique` profiles in
`.harness/workflows/workflow-profiles.json`, the `openai-compat` executor in
`.harness/routing/executors.json` with `tools/openai_worker.py`, and the branch-object
support in `default_fork_branches` (`scripts/harness.py`) + the repo-scoped-skill branch
of `_skill_status` (`scripts/harness_lib/agent_parity.py`). It does not change await/
cancellation/scheduling/failover, the worker-result schema, or task-profiles/model-cards.

## Requirements / invariants (numbered, testable)

1. **One canonical playbook.** `.harness/prompts/research-playbook.md` is the single
   source; both vendor surfaces are thin pointers to it and add no divergent process.
2. **Skill declared + audited.** `capabilities.json` declares the repo-scoped `research`
   skill; `agents audit` reports it `present` for claude and codex with no new gap.
3. **Divergence profile.** `research-divergence` is a read-only fork-join with 5 ideator
   branches, `writeAllowed: false`, `maxWorkerOutputChars: 5000`, `minSuccess: 3`,
   `preserveConflicts: true`, and the declared token budget.
4. **Critique profile.** `research-critique` is a read-only fork-join with 4 critic
   branches, `writeAllowed: false`, `minSuccess: 2`, `securityBlockerBlocksWorkflow: true`,
   and the declared token budget.
5. **One packet per branch.** Planning a profile emits exactly one worker packet per
   branch, each carrying only its own branch text (independent prompts, no leakage).
6. **Executor registered + routable.** `openai-compat` is a runnable executor whose
   every task profile resolves a spawn via `defaultSpawn` (`executor validate` valid).
7. **Worker contract.** `openai_worker.py` reads the packet from
   `HARNESS_WORKER_PROMPT_PATH`, does one POST to `{base}/chat/completions`, and writes
   exactly one WORKER_RESULT to `HARNESS_WORKER_RESULT_PATH`; a failure is exit ≠ 0 with
   no result file written.
8. **Key hygiene.** The API key is read only from an env var (name via `--api-key-env`,
   default `OPENAI_API_KEY`) and never appears in argv, stdout, stderr, or the result.
9. **Round outputs.** A round writes `docs/research/<slug>.md` and appends decisions to
   `.harness/context/DECISIONS.md`; it creates no new top-level directory, no nested
   README, and no hand-maintained markdown ledger.
10. **Source per claim.** Every normative claim in the playbook carries a source + date +
    confidence class; an unverifiable technique is marked `judgment`, never fabricated.
11. **Explicit branch roles.** Fork-join `branches` may be objects declaring
    `taskProfile`/`workerRole` (validated against `task-profiles.json` — unknown fails at
    plan time); string branches keep the keyword fallback. Research roles map through this
    structure (ideador→`plan`, validade/arquitetura→`review`, custo→`scan`,
    segurança→`security`).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Skill implementa exatamente o processo Double Diamond do usuário | pedido do usuário (intake `research-skill.intake.md`, request verbatim) |
| Orquestrador-worker com 3-5 subagentes paralelos + passe de citação separado; perspectivas guiam as branches | Anthropic multi-agent research system (fonte 2); STORM perspective-guided (fonte 3) |
| Geração independente antes de exposição (5 ideadores sem se ver) | Diehl & Stroebe 1987, production blocking, nominal ≈2× ideias (fonte 5) |
| Convergência set-based (manter um conjunto vivo, eliminar por evidência) | Sobek, Ward & Liker 1999 (fonte 8) |
| `pair` só renderiza skills user-scope → skill repo-local precisa de adaptador à mão + patch `_skill_status` | `agent_parity.py:95-114` (teto do pair SPEC-113) |
| Calibração de orçamento: custo real ≈ (packet + required-reads) × 1.3; required-reads ~9.371 tok/worker (~16× o packet; ~46.855 tok num fork-join de 5) | auditoria interna 2026-07-11 (medição em packets reais) |

## Ceilings (upgrade paths)

- **No retry/streaming in the worker.** The async scheduler owns backoff + the
  per-executor circuit breaker; add streaming only when a worker needs progress before
  settle.
- **One executor per group.** Cross-vendor is per-wave, not per-worker; upgrade = a
  per-branch executor binding.
- **`pair` does not render the repo-scoped skill.** The codex adapter is hand-authored and
  kept in sync by hand; upgrade = extend `pair`'s source resolution to repo-scoped skills.
- **Single-pass reduce.** No tree/hierarchical reduce; worker counts stay within one
  reducer's context (profiles cap at 4-5).
- **Egress is declare-only, not enforced (E3 / C6a).** A worker's outbound network traffic
  happens inside the vendor CLI or `openai_worker.py`, outside harness control, so the
  harness cannot block a worker from reaching an arbitrary host. The honor-system limit:
  research workers should reach only their configured model endpoint and the sources they
  cite. The least-privilege env (rule 24) and the collect-boundary secret-scrub (rule 25)
  reduce what a rogue egress could carry, but they do not stop the connection itself.
  Upgrade path = an executor that accepts and enforces an egress allowlist.

## Test strategy

- Behaviors to verify: both profiles load with the declared shape; a divergence plan emits
  5 isolated packets; branch objects map `taskProfile`/`workerRole` and unknown profiles
  fail at plan time while legacy strings keep the keyword fallback; the worker round-trips
  a stub `chat/completions` into a valid result with the key absent from stdout/stderr;
  fail-fast exit codes (2/3/4); `executor validate openai-compat` is valid; `agents audit`
  shows the skill present with no new gap; the playbook contains the phase headings, the
  anti-fabrication rule, the concept-card mapping, and a `docs/research/` reference; an
  e2e smoke runs `research-critique` through `openai-compat` against a local stub.
- Edge cases: missing env/packet (exit 2), missing key (exit 3, names the var), non-JSON
  prose reply (exit 4, no result written).
- Regression risks: `default_fork_branches` (shared by every fork-join) — net is
  `wf_failover.py`; `_skill_status` — net is `ap_agent_parity.py`.
- Coverage impact: enforced via `testing/scenarios/rs_research_skill.py` (deterministic,
  no real LLM — a local `http.server` stub).

## Validation

- `python testing/scenarios/rs_research_skill.py` — all `rs:*` checks green
  (profiles-load, plan-distinct-prompts, branch-role-mapping, worker-stub-roundtrip,
  worker-fail-fast, executor-routable, parity-no-regress, playbook-contract, e2e-smoke).
- `python testing/scenarios/wf_failover.py` — the `default_fork_branches` / settle
  regression net stays green.
- `python testing/scenarios/ap_agent_parity.py` — the `_skill_status` parity net.
- `python scripts/harness.py executor validate openai-compat` and
  `python scripts/harness.py agents audit`.
- `python scripts/harness-test.py spec-pack --no-project-commands` — template conformance
  (this spec has no Gherkin: CLI/runtime/internal surface, non-UI).

## Amendments

### v2 (2026-07-11) — first-real-round calibration and validator conformance

The first live round (`docs/research/deep-research-pipelines.md`, 2 waves, 9 claude
workers) exposed three machinery defects and one calibration miss; this amendment
records the corrections. Numbered requirements continue the list.

12. **Evidence may be URLs or prose.** `validate_worker_result` existence-checks only
    path-like strings — no `://`, no whitespace (`result_contracts._pathish`); dot-dir
    paths (`.harness/...`) validate correctly (the old `lstrip("./")` ate the leading
    dot) and the URL guard in `existing_rel_path` runs before the `:line` split. A
    genuinely missing repo path still fails. Regression: `rs:evidence-urls-valid`.
13. **Calibrated output caps.** Rule 3's `maxWorkerOutputChars` is 9000 for
    `research-divergence` and 10000 for `research-critique` — measured on round 1:
    honest concept/critique payloads ran 5.3–9k chars and the 5000/8000 caps rejected
    7 of 9 valid results. `rs:profiles-load` pins the new values.
14. **Headless claude spawn.** The `claude` executor template carries `-p` (print
    mode) and every spawn argv resolves argv[0] via `shutil.which`
    (`harness._resolve_argv0`) — Windows npm shims (`claude.cmd`) are not resolvable
    by `CreateProcess` without it. Validated live by round-1 workers.

| Decisão | Fontes |
|---|---|
| URLs/prosa são evidência legítima; só path-like é checado | rodada 1: 5/5 ideators rejeitados pelo validador em URLs e paths dot-dir reais (docs/research/deep-research-pipelines.md, Phase 3) |
| Caps 9000/10000 | medição da rodada 1: payloads honestos de 5.3–9k chars; 7/9 resultados válidos rejeitados pelos caps originais |
| `-p` + which-resolution no spawn | WinError 2 no smoke; claude.ps1/.cmd shim npm; memória da máquina: headless exige print mode |

### v3 (2026-07-11) — estimator calibration + rebase (E2) and wave-shared context digest (E1)

TASK-002 E2/E1 (`tasks/research-portfolio/PLAN.md`). E2 calibrates the token estimator
and rebases every budget so effective ceilings are unchanged; E1 adds an opt-in
wave-shared context digest. Numbered requirements continue the list.

15. **Calibrated estimator + rebased budgets.** `tokenBudget.charsPerToken` is `3.1`
    (was `4`) in `.harness/project.json`, `token_economics.DEFAULT_TOKEN_BUDGET`, and it
    flows through `estimate_tokens_from_text`/`estimate_tokens_from_chars` and the
    `cost_metrics` estimator fallback. Every profile `tokenBudget` in
    `workflow-profiles.json` is rebased ~1.3× (round numbers) so the effective char
    ceilings are unchanged (e.g. `research-divergence.maxTotalWorkerPromptTokens`
    14000→18000, `research-critique` 11200→14500). `token-audit` on a fresh plan of every
    profile stays non-failing (`research-divergence` keeps its pre-existing perWorker-output
    `warn`; all others `pass`). `rs:profiles-load` pins the rebased values.
16. **Wave-shared context digest (opt-in).** A profile may set `sharedContextDigest: true`
    (`research-divergence`, `research-critique`). At plan time the harness builds one
    `<WF>/context-digest.md` (gitignored runtime) by deterministic, headings-based section
    extraction from the worker's required-read files — stdlib only, no LLM. The WORKER_RESULT
    contract section from `subagent-contract.md` is copied **verbatim** (a lossy contract
    yields invalid results). The digest header lists each source with `mtime`+`sha256` (a
    stale digest must not propagate silently) and an explicit NON-AUTHORITATIVE note:
    canonical files remain the source of truth and workers may open originals on demand
    (same invariant as Graphify structural discovery, `specs/00-universal/structural-discovery.md`).
17. **Digest packet, non-opted-in byte-identical.** For opted-in profiles the packet's
    `## Required reads` lists the digest FIRST, then the canonical paths marked
    `verify-on-demand`. For every other profile the packet is byte-for-byte unchanged.
18. **Measured saving.** `token-audit` reports `requiredReads` estimated tokens per worker
    and per wave, with and without the digest, so the input-token cut is a measured number.
    Regressions: `rs:calibration-ratio`, `rs:digest-built`, `rs:digest-packet`,
    `rs:digest-optout`, `rs:digest-savings`.

| Decisão | Fontes |
|---|---|
| `charsPerToken` 3.1 (≈ 4/1.3); rebase ~1.3× mantém tetos efetivos | E2: heurística punct/path-aware vs `chars/4` em packets+required-reads reais = 1.31× (3.05 chars/token), na banda 1.29-1.35× da auditoria; dominante required-reads 3.073 ≈ 3.1 |
| Digest é NÃO-autoritativo; originais sob demanda; contrato WORKER_RESULT verbatim | crítica C1 (Phase 4): multiplier reproduzível, digest não-autoritativo, risco de falha correlacionada; `subagent-contract.md` (contrato lossy → resultados inválidos → custo-negativo) |
| Digest só em perfis opt-in; demais packets byte-idênticos | crítica C1: required-reads é um choke point hardcoded; zero superfície de regressão fora dos perfis de pesquisa |

### v4 (2026-07-11) — seeded convergence waves (F1) and handoff self-consistency (M1)

TASK-002 F1/M1 (`tasks/research-portfolio/PLAN.md`). F1 adds a plan-time `--seed` seam
for convergence waves; M1 makes `generate_handoff` fit its own required-read budget.
Numbered requirements continue the list.

19. **Seeded convergence wave (`workflow plan --seed <prior-WF>`).** A plan-time-only
    seam: the planner reads the prior workflow's `reduce/reducer.result.json`, builds a
    compact seed digest (top deduped findings, `title` + `recommendation`, bounded chars),
    and **copies** it INTO the new workflow — `<WF>/seed-context.md` and appended to every
    packet's Parent task section — so a scrubbed/gitignored prior WF dir never dangles (the
    seed content is self-contained; the prior WFID appears only as a non-load-bearing
    provenance note). `workflow.json`/`plan.json` record `seed: {workflowId, depth}`.
20. **Untrusted-derived provenance.** The seeded packet marks the seed section
    `untrusted-derived` with a one-line note (`seeded from <WF> reduce; verify claims against
    sources`) — injection-laundering mitigation; the digest is leads, not facts.
21. **Convergence-only (hard-forbid divergence).** `--seed` raises `HarnessError` when the
    target profile sets `seedForbidden: true` (added to `research-divergence`) or is named
    `research-divergence`, naming the independence evidence (Diehl & Stroebe 1987; Diversity
    Collapse arXiv:2604.18005): seeding a divergence wave collapses the independent generation
    the round depends on. `research-critique` allows it.
22. **Depth bound (≤2), planner-enforced.** Seeding increments depth (unseeded prior = depth 0
    → new depth 1); seeded-from-seeded chains refuse at depth > 2 with a `HarnessError` naming
    the bound. Enforced by the planner, never by worker discipline. A prior WF with no
    `reduce/reducer.result.json` raises a legible error (fix: run reduce first).
23. **Handoff fits its own budget.** `generate_handoff` runs the *same* demotion ladder on its
    large canonical required reads (`AGENTS.md`, `subagent-contract.md`) that it already runs on
    conditional/spec reads: the tiny state/context heads stay required; a big doc that would push
    `contextBudget.estimatedRequiredReadTokens` past `handoffBudget.maxRequiredReadTokens` (5000)
    is demoted to a verify-on-demand pointer in `conditionalReads`/`budgetDemotedReads`. A freshly
    generated handoff always passes `workflow:handoff-context-pack` under the calibrated
    `charsPerToken 3.1` (the defect: the pre-fix generator only demoted conditional reads, so the
    ~8.2k-token required set overflowed). Regressions: `rs:seed-critique`, `rs:seed-divergence-refused`,
    `rs:seed-depth-bound`, `rs:seed-missing-reduce`, `rs:handoff-fits-budget`.

| Decisão | Fontes |
|---|---|
| `--seed` é convergence-only; seed copiado (não referência a dir scrubável); profundidade ≤2 imposta pelo planner | crítica C3 (Phase 4): convergence-only, dangling seeds após scrub, injection-laundering; independência das ondas (Diehl & Stroebe 1987; Diversity Collapse arXiv:2604.18005) |
| Nota de proveniência untrusted-derived no packet semeado | crítica C3: risco injection-laundering / autonomy-creep — seed é lead verificável, nunca fato |
| Handoff usa a mesma escada de rebaixamento para required-reads grandes | M1 (round finding 4): required-set ≈25.4KB (~8.2k tok em `charsPerToken 3.1`) > `maxRequiredReadTokens` 5000; gerador só rebaixava conditional reads → todo handoff fresco falhava `workflow:handoff-context-pack` |

### v5 (2026-07-11) — least-privilege worker env + secret-scrub (E3 / C6a) — profile `security`

TASK-002 E3 (`tasks/research-portfolio/PLAN.md`), the security slice of critique cluster
C6. The finding: workflow workers inherited the FULL parent environment (every API key
included). The split adopted the least-privilege-env + secret-scrub half and parked the
egress-allowlist + provenance-quarantine half. Numbered requirements continue the list.

24. **Least-privilege spawn env (allowlist).** Both worker-spawn paths — the blocking
    `run_one_worker` (`scripts/harness.py`) and the async `workflow_async_run_one_worker`
    (`harness_lib/async_runtime.py`) — build the child env through ONE shared helper
    (`processes.filter_spawn_env`, resolved by `build_worker_spawn_env`). The child gets:
    (a) a minimal OS base allowlist (`processes.OS_BASE_ALLOWLIST` — `PATH`, `SYSTEMROOT`,
    `TEMP`/`TMP`, `USERPROFILE`/`APPDATA`/`LOCALAPPDATA` so vendor CLIs find auth/config,
    `HOME`/`LANG`/`SHELL`/`LC_*`, …); (b) the per-executor `envKeepList` in
    `.harness/routing/executors.json` (`openai-compat`: `OPENAI_BASE_URL`, `OPENAI_MODEL`,
    `OPENAI_API_KEY`, `NVIDIA_API_KEY`, `GEMINI_API_KEY` — the HTTP worker's base/model +
    the key named by `--api-key-env`; `claude`: `ANTHROPIC_*`, `CLAUDE_*`; `codex`: `CODEX_*`,
    `OPENAI_API_KEY`; `generic`: none); (c) the `HARNESS_*` vars the runtime sets, plus any
    target env (SPEC-110 deny-by-default). Everything else — a `GEMINI_API_KEY` in a `claude`
    worker, unrelated tokens/secrets — is DROPPED. Escape hatch: `project.json`
    `workflows.workerEnvFilter = false` restores full inheritance (OFF is a break-glass, not
    the norm). Regression: `rs:env-filtered`.
25. **Deterministic secret-scrub at the collect boundary.** `workflow_validate_results`
    scans each `result.json` (and `workflow_reduce` scans the reduce output) via
    `harness_lib/secret_scan.py` for structure-anchored secret shapes (`sk-…`, `nvapi-…`,
    `AIza…`, `gh[pousr]_…`, `xox[baprs]-…`, JWT, `Bearer …`, PEM private-key headers). A hit
    marks the result invalid with a legible error naming the JSON location (e.g.
    `findings[0].evidence[1]`), redacted to first-4-chars + length — the secret value is
    never echoed — and sets the workflow `requiresSecurityReview`. Patterns are anchored on a
    fixed prefix/marker, so a bare 64-hex sha256 digest stamp or a git hash (legitimate in
    `context-digest.md` and evidence) is never flagged. Regression: `rs:secret-scrub`.
26. **Provenance prefix (convention only).** The research playbook's evidence-entry format
    gains a `[web]`/`[repo]`/`[judgment]` prefix so the trust boundary of each claim is
    legible. No schema change and no quarantine machinery (both explicitly rejected by the
    critics); a `[web]` claim is still verified against a primary source before it drives a
    decision.
27. **Egress allowlist: declare-only (honor-system ceiling).** The harness cannot enforce
    per-worker network egress without executor support (a worker's outbound HTTP happens
    inside the vendor CLI / `openai_worker.py`, outside harness control). The limit is
    declared, not enforced: research workers should reach only their model endpoint and
    cited sources. Upgrade path = an executor that accepts an egress allowlist. See the
    Ceilings section.

| Decisão | Fontes |
|---|---|
| Env allowlist (base OS + per-executor keepList + HARNESS_*), demais chaves DROPPED; flag `workerEnvFilter` como break-glass | crítica C6 (Phase 4): full-env inheritance é gap REAL (high — workers herdam env do pai incl. API keys); split adota least-privilege-env slice |
| Secret-scrub determinístico no collect; padrões ancorados em prefixo; sha256/hex nu NÃO sinalizado; erro redigido; `requiresSecurityReview` | crítica C6: secret-scrub slice; falso-positivo em sha256 stamps é inaceitável → só shapes ancorados; `secrets-and-configuration.md` (nunca ecoar segredo) |
| Provenance `[web]`/`[repo]`/`[judgment]` só convenção; egress declare-only | crítica C6: quarantine schema + egress enforcement PARKED (needs platform support) — implementar só a metade sourced |

### v6 (2026-07-11) — zero-materialization compile loop (`workflow plan --validate-only`, TASK-004 N1)

TASK-004 N1 (`tasks/gui-flow-composer/PLAN.md`), from research round 2 (K1 composer,
`docs/research/agent-gui-cli-features.md` Phase 5). The renderer-first flow composer (N2)
needs to validate a candidate plan without paying to materialize it. The seam is
`plan_workflow`, refactored so the pure "resolve + build" core (`_compile_workflow_plan`)
is shared by the real plan path (materializes) and the compile loop (does not). Numbered
requirements continue the list.

28. **Validate-only writes nothing.** `workflow plan --validate-only` resolves the profile,
    builds the branch/shard units and per-worker packets in memory (same
    `estimatedPromptTokens` estimator as the materializing path), and prints a JSON report
    `{validateOnly, profile, type, workers[], tokenAudit, valid, errors, warnings}` WITHOUT
    creating any `.harness/workflows/active/WF-*` directory, prompt/scope file, `workflow.json`,
    `branches.json`/`shards.json`, `context-digest.md`, `reduce/token-audit.json`, state-store
    entry, or event. The materializing plan path is byte-for-byte unchanged (single shared
    core, no drift). Regressions: `wv:no-materialization`, `wv:real-plan-unchanged`.
29. **Budget breach is a compile error.** The report's `tokenAudit` reuses the token-audit
    verdict logic (worker-prompt max/total + planned-total vs the profile `tokenBudget`, via
    the shared `token_budget_status`). A `fail` status makes `valid: false` with the breach in
    `errors` — a budget breach is a COMPILE error, not just a warning. `--override-budget`
    preserves the existing escape: the breach moves to `warnings` and `valid` returns to true.
    An unknown profile / unknown branch `taskProfile` (rule 11) is caught and reported as an
    error, never a crash. Regressions: `wv:budget-breach-errors`, `wv:unknown-profile-errors`.
30. **Compile-time secret-scan (N2/E7 trust boundary).** Before any render/materialize,
    `--validate-only` runs `secret_scan.scan()` (rule 25) over the candidate content supplied
    on argv (task + branch/shard strings); a hit makes `valid: false` with the location + the
    redacted match (first-4 + length — the secret is never echoed, same contract as the collect
    boundary). This wires the compose-time scanner call site (E7) now, so N2's future prompt
    overrides inherit it. Regression: `wv:secret-scan`.

| Decisão | Fontes |
|---|---|
| Compile loop separa validação de materialização; core `_compile_workflow_plan` compartilhado (real path adiciona só as escritas) | K1 (Phase 4): `--validate-only` é a única peça não construída; compiler-as-trust-boundary = modelo de allowlist existente; N2 chama isto via CLI |
| Budget breach = erro de compilação (escape `--override-budget` vira warning) | N1 acceptance (`tasks/gui-flow-composer/PLAN.md`); reusa o verdict do token-audit (SPEC-102) sem escrever o arquivo |
| Secret-scan no conteúdo candidato em compile time (não só no collect) | K6/E7 (Phase 4/5): secret-scan não tinha call site de compose-time; habilita prompts-as-data com segurança para N2 |

### v7 (2026-07-12) — composed branch OBJECTS on the CLI (`workflow plan --branch-json`, TASK-004 N2b)

TASK-004 N2b (`tasks/gui-flow-composer/PLAN.md`). The composer's deferred "Create workflow"
step must materialize the *composed* branch objects (title/taskProfile/workerRole edited in
the form), not just a profile's default branches. `plan_workflow`/`default_fork_branches`
already accept branch OBJECTS internally (rule 11); `--branch` was string-only, so the CLI
gained one flag. Numbered requirements continue the list.

31. **`--branch-json` materializes composed branch objects.** `workflow plan --branch-json
    <json>` parses a JSON array of `{title, taskProfile?, workerRole?}` objects and passes it
    as `branches=` to `plan_workflow` (real materialize *and* `--validate-only`). Parse failure
    is a legible `HarnessError` (`--branch-json is not valid JSON: …`); a non-array is rejected;
    it is **mutually exclusive with `--branch`** (both given → `HarnessError`, not a silent
    precedence). The closed vocabulary is enforced by the existing `default_fork_branches` raise
    — an unknown `taskProfile` fails at plan time (no new validator added). This is the single
    CLI seam the composer-create action (SPEC-120 v2) builds. Regression:
    `plan:branch-json-materializes` (`testing/scenarios/wv_validate_only.py`): composed objects
    land in `branches.json` verbatim; an unknown `taskProfile` → non-zero + legible.

| Decisão | Fontes |
|---|---|
| `--branch-json` só parseia + repassa como `branches=`; sem novo validador (default_fork_branches já é a fronteira de vocabulário fechado) | N2b build (`tasks/gui-flow-composer/PLAN.md`): plan_workflow/default_fork_branches já aceitam objetos internamente (rule 11); a CLI só precisava do parse |
| Mutuamente exclusivo com `--branch` (erro, não precedência silenciosa) | N2b: `--branch` é string-only e `--branch-json` é objeto — dois formatos no mesmo slot exigem uma escolha explícita e legível |

### v8 (2026-07-12) — a raised branch resolution leaves no partial WF dir (B2)

32. **A `--branch-json` plan that raises during branch resolution leaves no partial
    `active/WF-*` dir.** In `_compile_workflow_plan` the `active/WF-*` mkdir moved to *after*
    `default_fork_branches`/`make_map_shards` resolve (they raise on an unknown `taskProfile`),
    so a rejected raw-CLI plan mkdir's nothing. Happy-path materialization is byte-identical
    (same `workflow.json`/`branches.json`/`workers/`/`reduce/`). Regression:
    `plan:branch-json-no-partial-dir` (`testing/scenarios/wv_validate_only.py`).

| Decisão | Fontes |
|---|---|
| mkdir do `active/WF-*` desce para depois da resolução (não antes) | B2: `default_fork_branches` já levanta em `taskProfile` inválido (rule 31); mover o mkdir para dentro dos blocos `if materialize:` por-tipo mantém a resolução como fronteira e não deixa dir parcial |

### v9 (2026-07-12) — research output cap raised to 12000 for dual-brief rounds (I1)

33. **`research-divergence` and `research-critique` `maxWorkerOutputChars` = 12000.**
    Round 2 ran two briefs per worker; honest concept/critique payloads reached
    9.8-11.7k chars and breached the round-1 caps (9000/10000) — the operator raised
    the frozen-WF cap to 12000 **twice**. Codified in the profiles; `rs:profiles-load`
    pins 12000. Token budgets (`maxTotalWorkerPromptTokens` 18000/14500) unchanged —
    this is output room, not prompt budget.

| Decisão | Fontes |
|---|---|
| cap 12000 (era 9000/10000) | 2 rodadas com o operador elevando o cap na WF congelada (docs/research/deep-research-pipelines.md §Phase 3; agent-gui-cli-features.md §Phase 3) — dual-brief estoura o cap calibrado em single-brief |

### v10 (2026-07-12) — openai_worker inlines only the WORKER_RESULT contract section (I2)

34. **System message carries only the WORKER_RESULT section.** `openai_worker._read_contract`
    slices `subagent-contract.md` to just the `## WORKER_RESULT for workflow workers` section
    (new `_keep_section`, the inverse of `_drop_section`) instead of inlining the whole file
    capped at `MAX_CONTRACT_CHARS`. A single-shot openai-compat worker never reduces or reviews,
    so the reducer/reviewer/HARNESS_RESULT sections were ~2k tokens/call of dead weight (measured:
    8000 → 1506 chars, −6494). A missing file OR a renamed/missing section falls back to the
    existing terse WORKER_RESULT-keys summary (never the whole contract). The section is still
    bounded by `MAX_CONTRACT_CHARS` as a safety cap. Regression: `rs:openai-contract-sliced`
    (the returned contract contains `WORKER_RESULT` but not `REDUCE_RESULT for reducers` /
    `REVIEWER_RESULT`).

| Decisão | Fontes |
|---|---|
| Fatiar o contrato para só a seção WORKER_RESULT (não o arquivo inteiro) | I2: worker single-shot openai-compat só produz WORKER_RESULT, nunca reduz/revê; medição 8000→1506 chars (−6494 ≈ −2.1k tok em `charsPerToken 3.1`) |
| Fallback inalterado em arquivo/seção ausente | `openai_worker.py` já resume as chaves de WORKER_RESULT na string de fallback — consistente quando o arquivo ou a seção não existe |

### v11 (2026-07-12) — wave-shared digest extended to the 8 read-only review profiles (I3)

I3 (`tasks/research-portfolio/PLAN.md`). The digest mechanism (rules 16-18) is
profile-agnostic: `context_digest.build_digest` derives the required-reads from the
workflow `type`, and both `_compile_workflow_plan` (digest build) and
`write_worker_prompt` (packet reference + reminder dedupe) guard purely on
`workflow["sharedContextDigest"]` — nothing branches on "research". The opt-in is
therefore extended from research-only to every read-only review profile. Highest
blast-radius change of the round (it alters the worker packet for every review
workflow) but a pure-JSON seam. Numbered requirement continues the list.

35. **Digest on all read-only review profiles.** `sharedContextDigest: true` is set on the
    8 `writeAllowed: false` review profiles (`repository-review`, `diff-review`,
    `spec-consistency-review`, `graph-impact-map`, `pre-release-review`, `security-triage`,
    `coverage-gap-inventory`, `migration-impact-map`) in addition to the two research
    profiles. Each replaces the per-worker 5-file required-reads block (~9.4k tok/worker)
    with ONE non-authoritative digest reference (~1.8k tok) plus the canonical paths marked
    `verify-on-demand` — a measured −7.6k tok/worker on a review profile (`token-audit
    requiredReads` reports `perWorkerWithoutDigest` vs `perWorkerWithDigest`;
    `repository-review` measures ~12.8k→~4.5k, a >0.64 input cut under `charsPerToken 3.1`).
    The digest carries the WORKER_RESULT contract **verbatim** and is non-authoritative
    (verify-on-demand, rule 16), so review workers lose nothing. The opt-out guarantee
    (rule 17) still holds for any workflow **without** the key: no digest built,
    Required-reads listed inline byte-identical. Regressions: `rs:digest-review-profiles`
    (digest built + packet references it digest-first on `repository-review`) and
    `rs:digest-optout` (rewritten to a keyless workflow dict — proving the mechanism, not a
    named profile that now carries the key).

| Decisão | Fontes |
|---|---|
| Digest estendido aos 8 perfis de review read-only (não só pesquisa) | I3: `build_digest`/`_compile_workflow_plan`/`write_worker_prompt` são profile-agnostic (guard só em `workflow["sharedContextDigest"]`, `scripts/harness.py:1445`/`:1522`/`:1177`); nenhum branch em "research"; maior blast-radius mas seam pura JSON |
| Corte medido −7.6k tok/worker; contrato verbatim; não-autoritativo | I3: required-reads 5 arquivos (~9.4k tok) → 1 referência de digest (~1.8k tok); `token-audit requiredReads` mede o corte (`repository-review` ~12.8k→~4.5k, cut >0.64); digest carrega WORKER_RESULT verbatim → review workers não perdem nada |
| Opt-out provado com workflow keyless (não perfil nomeado) | I3: todos os 10 perfis agora têm a chave; `rs:digest-optout` reescrito para um dict sem `sharedContextDigest` — prova o guard-on-key, robusto a mudanças futuras de perfil |

### v12 (2026-07-18) — parametric fan-out width in `workflow plan` (D010)

DECISIONS.md **D010** (2026-07-18): fan-out width is PARAMETRIC, not fixed — a focused
question wants 1-2 workers, an exploratory one 4-5, and the number must be *justified*
(Delta_m, the marginal-idea gain, arbitrates). The playbook already carries the operating
rule ("No width written = do not start the wave"); this amendment plumbs the contract into
`workflow plan`. Numbered requirement continues the list.

36. **Declared width on research plans.** `workflow plan` accepts `--width-mode
    {focused,exploratory,custom}` and `--width-why TEXT`. There is no `--width` flag: the
    width IS the final worker count (existing `--max-workers`/branch trimming). For a profile
    with `widthDeclarationRequired: true` (`research-divergence`, `research-critique`) OR any
    `research-*` profile, BOTH flags are mandatory — a plan missing either raises a
    `HarnessError` naming **D010** and the playbook line "No width written = do not start the
    wave" (dual flag+name guard, cloned from the `seedForbidden` pattern). When a declaration
    is present the plan records a `declaredWidth` stamp `{mode, width, justification, band,
    withinBand}` — bands `focused=[1,2]`, `exploratory=[4,5]`, `custom=[1,maxWorkers]`.
    Out-of-band is **allowed** (D010 is a rule of thumb, and the justification is mandatory
    by construction): the stamp records `withinBand: false`, it never blocks. Non-research
    profiles: the flags are optional, recorded only when present, zero behavior change when
    absent (no `declaredWidth`). `--validate-only` threads the same flags and its report
    surfaces `declaredWidth` (or the refusal). An EXPLICIT branch list
    (`--branch`/`--branch-json`/composed GUI branches) is a width **declared by
    construction** — the caller chose exactly N branches — so it needs no flags and the
    plan auto-stamps `declaredWidth` as `custom` with a by-construction justification;
    the refusal fires only when a research plan falls back to the profile's DEFAULT
    branch fan-out (the EXP-15 redundancy trap D010 targets). Regressions:
    `rs:width-required`, `rs:width-stamped`, `rs:width-out-of-band`,
    `rs:width-by-construction`, `rs:width-optional-elsewhere`.

```gherkin
Scenario: [rs:width-required] a research plan with no declared width refuses, naming D010
  Given the research-divergence profile requires a declared width
  When I run workflow plan --profile research-divergence without --width-mode/--width-why
  Then the plan is invalid and the error names D010 and "No width written = do not start the wave"

Scenario: [rs:width-stamped] a focused declaration stamps declaredWidth in band
  Given a research-divergence plan with --width-mode focused --width-why "..." --max-workers 2
  When I validate the plan
  Then declaredWidth is {mode: focused, width: 2, band: [1,2], withinBand: true} with the justification

Scenario: [rs:width-out-of-band] a focused label at width 5 succeeds but is flagged out-of-band
  Given a research-divergence plan with --width-mode focused and 5 workers
  When I validate the plan
  Then the plan is valid and declaredWidth.withinBand is false

Scenario: [rs:width-by-construction] an explicit branch list declares its width by construction
  Given a research-divergence plan passing two explicit --branch entries and no width flags
  When I validate the plan
  Then the plan is valid and declaredWidth is {mode: custom, width: 2} with a by-construction justification

Scenario: [rs:width-optional-elsewhere] a non-research profile needs no width declaration
  Given a repository-review plan with no width flags
  When I validate the plan
  Then the plan is valid and carries no declaredWidth (zero behavior change)
```

### Corrections to earlier text

The v1 Validation note "this spec has no Gherkin: CLI/runtime/internal surface, non-UI" is
superseded for rule 36: the four scenarios above are the SPEC-116 conformance mapping for the
declared-width contract, each `[id]` resolving to a `check(...)` in
`testing/scenarios/rs_research_skill.py` (the file the Validation section already references).

D010's schema seam is a pin-to-reality note: `schemas/workflow.schema.json` sets
`additionalProperties: false` at the top level, so the durable stamp lives under the
schema-sanctioned `slots` object (`workflow["slots"]["declaredWidth"]`) rather than as a new
top-level key — no schema change, and every materialized research plan still validates.

| Decisão | Fontes |
|---|---|
| Largura de fan-out é paramétrica (foco 1-2, exploração 4-5), número justificado; Delta_m arbitra | D010 (DECISIONS.md, 2026-07-18); playbook "No width written = do not start the wave" (`research-playbook.md`) |
| Fora-de-banda é permitido (regra de bolso), justificativa obrigatória por construção | D010: a declaração torna a largura uma escolha consciente; bloquear a banda puniria escolhas legítimas fora do padrão |
| Declaração obrigatória só em perfis de pesquisa; demais perfis inalterados | EXP-15 (5 workers → as mesmas 5 ideias): largura mal calibrada gasta orçamento sem ganho marginal — o custo real que a declaração força a justificar |
| Stamp sob `slots` (não chave top-level) | `schemas/workflow.schema.json` `additionalProperties:false` no topo; `slots` é o ponto de extensão sancionado (DW.2), fora do footprint do schema |

### 2026-07-27 — the WORKER_RESULT access class: declared on the executor, never in the packet

Row `wr-schema-discards-work` measured the cost: a wave the owner paid for in
frontier tokens had **100% of its results formally discarded**, and the three
blockers that killed the proposal survived only because the orchestrator read the
files by hand. Part of that was field bounding (shipped earlier). This closes the
other part, which was worse than a rejection rule — it was an INCENTIVE.

`sourceFilesVerified` is required when a result carries a high/blocker finding. A
packet-only HTTP worker has no repo, so it can never fill that field legitimately.
The rule therefore either made the cheap multi-vendor leg useless for serious
findings, or **pressured the worker into claiming verification it never performed**
— which is exactly what happened: NVIDIA workers tagged packet-derived evidence
`[repo]`. A contract that manufactures false provenance is worse than one that
merely rejects.

Owner decision (2026-07-27), asked where the access class should be declared —
packet or executor config: **"na configuração do executor"**. That placement is
the security property, not a filing preference: the card is HARNESS-owned and the
packet is WORKER-owned, so a worker can never assert its own exemption.

1. **Declared per executor.** Each card in `.harness/routing/executors.json` carries
   `repoAccess: "repo" | "none"`. The three `type: http` packet workers declare
   `none`; the cli-agent executors declare `repo`.
2. **Resolution defaults STRICT.** `result_contracts.executor_repo_access` returns
   `"repo"` for an unknown executor, an undeclared card, or a missing/corrupt
   registry. The relaxation must be EARNED by a declaration — it is the only
   default that cannot be obtained by deleting a config file.
3. **The waiver arrives with two TIGHTENINGS**, so this is a net narrowing:
   a packet-only result declaring `graphify.status=used` is now an ERROR (it never
   had a repo to graph), and a packet-only result with a NON-EMPTY
   `sourceFilesVerified` is now an ERROR (it cannot have read those files). The
   incentive is inverted: claiming repo work you could not do is now the failure.
4. **Unwired seams keep today's behavior BY CONSTRUCTION.** Because the default is
   strict, a validation site that does not pass `repo_access` is unchanged. Wired
   today: the REDUCER and the async SETTLE — the executor is a property of the
   WORKFLOW/round, which is what those two hold. The runnable-workers probe in
   `async_state` was deliberately left UNWIRED: reaching the registry there needs
   `ROOT` on that module's bind surface, and widening a module's bound-name surface
   costs more than the probe is worth when the strict default already makes it a
   no-op. Consequence, stated rather than hidden: a packet-only result is judged
   by the old rule at that ONE probe, so it can be re-run once; the reducer and
   settle — where results are accepted or discarded — are correct.

Acceptance: `rs:packet-only-access-class`. Falsified 4/4 — flipping the default to
lax, allowing either lie, and relaxing on a missing registry all go red.

| Decisão | Fontes |
|---|---|
| Executor card, not packet | Owner 2026-07-27; the card is harness-owned, so the exemption cannot be self-asserted — the packet is the worker's own output |
| Strict default on every unknown | A default that relaxes on a missing/corrupt registry is obtainable by deleting a file; the only safe direction is the one that fails toward the existing rule |
| Waiver ships WITH two new errors | A pure relaxation would leave the false-provenance incentive intact for anyone who wanted to claim repo work; inverting it is what makes the change a tightening |

### v13 (2026-08-01) — P0: `minSuccess` clamped to the runnable group; reduce validates `repoAccess` per worker

DD-mechanization P0 (`design-dd-mechanization.md` §4/§8; dual plan codex gpt-5.6-sol +
kimi k3). Two latent bugs in the async workflow machinery surfaced when the mixed-fleet
research round ran homogeneous per-executor waves.

37. **`minSuccess` clamps to the runnable group, ROUND-SCOPED, at `workflow start`.** Each
    round's async group `settlementPolicy` carries `max(1, min(minSuccess, len(runnable)))` —
    the value the detached supervisor and `workflow await` settle THIS round on. The clamp is
    NOT written onto the workflow's cross-round `awaitPolicy`/`settlementPolicy` default:
    persisting it there would make it sticky across rounds, because
    `workflow_effective_await_policy` merges `workflow["awaitPolicy"]` LAST — a later, larger
    round would inherit the shrunk bound and never heal to the profile's intent (a workflow
    that requires 3 could silently settle at 2/2 forever after one small round). `workflow
    await` therefore seeds `minSuccess` from the round's group `settlementPolicy`, not the
    workflow default; an explicit `workflow await --min-success N` remains an honored operator
    override. A profile `minSuccess` above the group size (e.g. `research-divergence`'s 3 on a
    2-worker wave) previously made **quorum-mode** unreachable on a healthy run (3 of 2). The
    bug was LATENT: the live rounds ran `all-settled`, where `minSuccess` is inert. Correction
    to the v1 Applicability line: this spec now DOES touch await-policy semantics (effective
    `minSuccess` only); mode, timeout, cancellation, scheduling, and failover are unchanged.
38. **Reduce-time `repoAccess` is judged by each worker's effective executor.** Each worker
    carries `resolvedExecutor`, stamped at spawn on BOTH run paths (async: the
    `workflow_start` queued-stamp; blocking: the `workflow_run` queued-stamp, reusing the
    SPEC-165 R10 per-worker resolution). `workflow_validate_results` validates each result
    with `worker.get("resolvedExecutor") or workflow.get("executor")`. Scope, stated
    precisely: `workflow.get("executor")` is NEVER populated on a real workflow (it is `None`
    → the strict `"repo"` default), so BEFORE this the reducer judged EVERY worker as `repo`,
    regardless of the executor that actually ran it. AFTER it: an unstamped worker still falls
    back to `None` → `repo` (v12 parity); a stamped repo-class worker stays `repo`; a stamped
    packet-only (`repoAccess: none`) worker — including EVERY worker of a HOMOGENEOUS
    packet-only wave (`nvidia-compat`/`local-llama`/`gemini-compat`), not only a mixed fleet —
    is now judged `none`, correctly rejecting a repo-work claim it could not have performed and
    aligning the reducer with the settle-time validation (`async_runtime.py` per-worker
    `executor_name`) that always used the real executor. The 2026-07-27 amendment's rule 4
    ("the executor is a property of the WORKFLOW/round") is **superseded for the reducer**: the
    access class now follows the WORKER's seat when stamped. Known gap, stated not hidden:
    async mid-workflow failover re-spawns a worker on a fallback executor WITHOUT updating
    `resolvedExecutor`, so P0b NEWLY narrows a failed-over worker's reduce judgment to its
    PRIMARY seat — which can wrongly reject legit work done on the fallback (over-strict, never
    accepts a lie); left as a P1 follow-up (a backlog row exists), not P0 scope.

Acceptance: `rs:min-success-clamped-to-runnable` (round-scoped clamp on the group; cross-round
workflow default preserved at the profile intent; end-to-end `workflow await` reaches quorum at
2/2; a 5-worker control is not over-clamped) and `rs:reduce-per-worker-access-class` (mixed wave
catches the packet-only lie and allows the unstamped-fallback worker; a homogeneous unstamped
wave stays valid; a homogeneous packet-only wave flips every worker to rejected) — both in
`testing/scenarios/rs_research_skill.py`. Mutants each go RED: persisting the clamp onto the
workflow default (the sticky regression) trips `crossRoundStays3`; dropping the `workflow await`
group-seed reports `quorum impossible: 2/3` (`awaitQuorum2of2`); reverting the reduce read to
`workflow.get("executor")` lets the packet-only lie pass as repo-class.

| Decisão | Fontes |
|---|---|
| Clamp is ROUND-SCOPED (group `settlementPolicy` only); the workflow's cross-round default stays at profile intent | sonnet-5 audit 2026-08-01: persisting the clamp onto `workflow["awaitPolicy"]` makes it sticky across rounds (last-merge), silently ratcheting a later larger round's quorum bar down; `workflow await` seeds from the round group instead |
| Per-worker stamp with strict fallback; the change is not limited to mixed fleets | `brief-ddmech-p0.md` P0b + opus-5/sonnet-5 audit: `workflow.get("executor")` is always `None`, so every homogeneous packet-only wave now correctly validates `none`, aligning reduce with settle-time |
| harness.py net-zero preserved | wt-3 ratchet (`wt_workflow_tree.py`): both stamps are kwargs added to existing `set_worker_status` calls, so the file stays at 3234 lines despite the blocking stamp living in `harness.py` |

### v14 (2026-08-01) — P2: zero-materialization `research round <slug> compile`

DD-mechanization P2 (`design-dd-mechanization.md` sections 2, 4, and 8; overseer brief
`brief-ddmech-p2.md`) adds a compiler for the strict JSON round specification embedded in
the canonical `docs/research/<slug>.md` document. `research show <slug>` and the existing
list/delete calls keep their positional CLI contract; the new family is namespaced as
`research round <slug> compile`. `advance` and `approve` remain explicitly unavailable
until P3/P5.

39. **The round specification is strict at compile time and lenient in the index.**
    `research_index.parse_round` exposes the first fenced JSON object containing
    `schemaVersion` as `roundSpec`; malformed hand-written content becomes a field-scoped
    `parseErrors` entry and never crashes the index. Compile validates the object against
    draft-2020-12 `schemas/research-round.schema.json` through the existing
    `workflow_schema.validate_packet` seam. The schema fixes the closed object vocabulary,
    required declaration fields, phase/profile names, fleet seats, zip assignments, seed
    policy, and delivery policy. Executor and model values remain strings because their
    authority is the live routing/executor configuration, not a duplicated schema enum.
40. **Compile enforces the eight logical-wave rules before child validation.** (1) each
    fleet count sums to its phase width; (2) zip has exactly one perspective/lens per seat;
    (3) every executor/model tuple and task-profile seat resolves from the live executor,
    task-profile, routing, and model-card configurations; (4) the logical budget is the sum
    of every child `tokenAudit.totalPlanned`; (5) each child reports
    `minSuccessEffective = min(profile.minSuccess, childWorkerCount)`; (6) develop children
    never carry a seed; (7) every critique edge crosses executors; and (8) every source
    develop cohort has a cross-vendor critic. Refusals name the first violated rule.
41. **Every physical child is compiled through the existing validator.** Develop
    perspectives and refine lenses are assigned by fleet order/count, grouped into one
    homogeneous executor/model cohort, rendered as branch objects, and passed to
    `validate_workflow_plan` with the declared research profile. The compiler does not own a
    second workflow validator, token estimator, model table, or branch renderer.
42. **Compile is observational.** Success and failure create no workflow directory, token
    audit file, context digest, state-store entry, event, or worker process. The returned
    plan contains the develop/refine child validation reports, effective quorum per cohort,
    cross-vendor critique edges, and aggregate logical token budget. Only a later approved
    materialization rung may turn those logical children into workflows.

Acceptance: `ri-4-round-spec` covers qualifying/malformed/missing fenced blocks.
`rs:round-compile-zero-materialization` compiles two develop plus two crossed refine cohorts,
checks the 2-of-2 clamp and aggregate budget, and snapshots both real and fabricated workflow
trees across compile. `rs:round-compile-rules-1-8` shows RED mutants for rules 1, 2, 3, 4, 6,
7, and 8 while the successful fixture pins rule 5's clamp. `ra_research_admin.py` preserves
the pre-existing list/show/delete surface. `harness.py` remains net-zero.

### v15 (2026-08-01) — P3: develop materialization and resume

DD-mechanization P3 (`design-dd-mechanization.md` sections 3, 4, 6, and 8; overseer brief
`brief-ddmech-p3.md`) activates `research round <slug> advance`. The command materializes and
drives only the compile plan's Develop cohorts; Refine/cross-vendor critique remains P4 and
`approve` remains unavailable until P5.

43. **Advance reuses the workflow runtime.** For each Develop cohort, advance calls the existing
    materializing `plan_workflow` with the compiled branches/profile and a task containing the
    round slug, then drives `workflow_start` → bounded `workflow_await` → collect →
    `workflow_reduce`. It passes the cohort's exact model/effort through
    `spawn_override_from_flags` and its `minSuccessEffective` to async start/await. It owns no
    second planner, runner, poller, collector, or reducer.
44. **Generated round state is canonical and idempotent.** Advance appends or replaces exactly one
    `<!-- round-state:start -->` / `<!-- round-state:end -->` fenced JSON block in
    `docs/research/<slug>.md`. Its shape is `{"phase":"develop","cohorts":[{"cohortId",
    "executor","model","wfid","status"}]}` with no `schemaVersion`. The index exposes it as
    lenient `roundState` (parse failures become `parseErrors`), while the existing WFID scan and
    task-slug inventory discover its child handles without another registry.
45. **Resume uses registered children.** A cohort WFID is persisted immediately after
    materialization. Re-running advance skips `done`, `partial`, or `reduced` children and resumes
    only incomplete children through the async runtime's `only_missing=True` path. A second run
    after settlement creates no workflow directory and retains the same WFID/status.
46. **P3 is Develop-only with a run-executor escape hatch.** Advance never materializes a Refine
    cohort. By default each Develop cohort runs on its declared executor. Optional
    `--executor <id>` overrides only the runtime executor for every child (operator/test escape
    hatch); compile validation and generated state retain the declared cohort executor/model.

Acceptance: `rs:round-advance-materializes-develop` pins one materialized slug-linked Develop WF
and the generated state/WFID scan; `rs:round-advance-lifecycle-settled` pins await/collect/reduce;
`rs:round-advance-resume-idempotent` proves a second advance creates no WF; and
`rs:round-advance-develop-only` proves zero Refine materialization. The fixture compiles a single
`nvidia-compat` / `z-ai/glm-5.2` Develop cohort, then uses `--executor local-llama` against the
loopback OpenAI stub. `rs:round-advance-seat-and-clamp` verifies the declared seat, runtime
override, exact model/effort, and effective quorum. Scenario cleanup scrubs every slug-linked WF,
removes the local-llama circuit file, and deletes the fixture document in `finally`.

| Decision | Sources |
|---|---|
| Homogeneous child WFs plus existing lifecycle instead of a heterogeneous runtime | `design-dd-mechanization.md` sections 3-4 and P3 ladder; `brief-ddmech-p3.md` D-C |
| Marker-delimited generated state, lenient index parse, no schema | `brief-ddmech-p3.md` D-A, D-B, D-F |
| Develop-only boundary and runtime-only executor override | `brief-ddmech-p3.md` D-D and round-2 deviation resolution R2 |
| Exact spawn pin and quorum clamp reuse | SPEC-119 v13 and `brief-ddmech-p3.md` P1/P0 seam requirements |

### v16 (2026-08-01) — P4: reduced, cross-vendor seeded Refine materialization

DD-mechanization P4 (`design-dd-mechanization.md` sections 3, 5, and 8-P4; overseer brief
`brief-ddmech-p4.md`) extends `research round <slug> advance` with the compiled Refine pass.
`approve` remains unavailable until P5. Multi-seed and heterogeneous child workflows remain out
of scope. SPEC-119 rule 46 ("Advance never materializes a Refine cohort") is **SUPERSEDED by
P4**: advance now materializes Refine after its source Develop workflow is reduced.

47. **Refine follows settled Develop.** After the Develop loop, advance iterates the compiled
    Refine cohorts. It resolves each cohort's `sourceCohortId` to the current Develop row and
    delegates seed readiness to `plan_workflow`, whose state-store-aware `load_workflow` recovers
    mirrored workflow/reducer artifacts when needed. If the planner reports that the source has
    no reduce result, advance keeps the planned Refine row and waits for a later resume.
48. **Exactly one compiled seed per critique cohort.** Refine calls the existing materializing
    `plan_workflow` with the cohort branches, the compiled `research-critique` profile, and one
    `seed=<source-develop-WFID>`, then reuses the unchanged `_run_child` lifecycle. Matching is
    not recomputed at runtime: compile rules 7 and 8 remain authoritative for cross-vendor edges
    and source coverage.
49. **The seed chain stays grounded.** A Refine workflow's seed provenance names a Develop
    workflow with no seed and records depth 1. Advance never seeds from a Refine workflow, so the
    P4 path cannot create divergence-to-divergence critique chains.
50. **Round state is uniform by cohort.** The generated block is now
    `{"cohorts":[{"cohortId","phase","executor","model","wfid","status","seed"?,
    "sourceCohortId"?}]}`. `phase` is `develop` or `refine`; only Refine rows carry `seed` and
    `sourceCohortId`. Both phases retain their WFIDs and settled statuses across advance calls,
    so a second call creates no workflow.

Acceptance: `rs:round-advance-refine-seeded` pins the state row and workflow seed linkage;
`rs:round-advance-source-reducer-present` is the happy-path presence check, while
`rs:round-advance-unreduced-seed-waits` pins the hard reducer precondition and deferred resume;
`rs:round-advance-refine-row-survives-source-scrub` proves a settled Refine row survives source
hygiene; `rs:round-advance-no-divergence-chain` pins the unseeded
Develop source and depth-1 Refine provenance; `rs:round-advance-declared-cross-vendor` pins the
compiled executor distinction; and `rs:round-advance-resume-idempotent` proves both phase WFIDs
remain stable on the second call. The loopback scenario scrubs every slug-linked workflow, removes
the local-llama circuit file, and deletes its fixture document in `finally`.

| Decision | Sources |
|---|---|
| Delegate source readiness/recovery to `plan_workflow`; wait on its missing-reduce error | `scripts/harness.py` `build_seed_context`; `brief-ddmech-p4.md` D-A |
| Consume compiled cross-vendor matching without runtime re-derivation | SPEC-119 v15 compile rules 7-8; `brief-ddmech-p4.md` D-C |
| One Develop seed per Refine child, depth 1, no multi-seed | `design-dd-mechanization.md` sections 3, 5, and 8-P4; `brief-ddmech-p4.md` D-D |
| Uniform per-cohort state and unchanged child lifecycle | `brief-ddmech-p4.md` D-B and D-E |

### v17 (2026-08-02) — P5: explicit human delivery approval

DD-mechanization P5 (`design-dd-mechanization.md` sections 6 and 8-P5; overseer brief
`brief-ddmech-p5.md`) activates `research round <slug> approve [--note <text>]` as the
human Deliver gate. The P3/P4 statements that `approve` is unavailable are superseded.
Approval verifies completeness and records a decision; it does not score the research or judge
the quality of operations, portfolio choices, experiments, or traceability.

51. **Approval requires settled state for every compiled cohort.** The gate compiles the round
    through the existing compiler, then requires every Develop and Refine `cohortId` to have a
    round-state row whose status is `done`, `partial`, or `reduced`. A refusal names every missing
    or unsettled cohort. It creates no workflow and runs no worker.
52. **Delivery checks Markdown section presence, not content quality.** When
    `requireOneOperationPerConcept` is true, an operations heading at level 1-3 must have a
    non-empty body. When `requireExactlyOnePortfolioBucket` is true, a portfolio heading at level
    1-3 must have a non-empty body. When `experimentDesign` is declared, an experiment heading
    with a non-empty body or a round-linked registered experiment must exist. A traceability
    heading with a non-empty body is always required. Headings are anchored at line start and use
    one to three `#` characters followed by a space; level 4+ headings and `#` lines inside
    triple-backtick fenced code blocks (including normal zero-to-three-space indentation) do not
    qualify. A section body extends through deeper
    subsections and ends only at the next heading of equal or shallower level. The gate does not
    parse per-concept counts, bucket cardinality, prose quality, or experimental validity.
53. **The human decision round-trips in canonical round state.** Passing approval writes the
    top-level `deliver` entry alongside `cohorts`: `approvedBy: human`, an ISO-8601 UTC timestamp,
    optional note (empty when omitted and capped at 400 characters), and checks containing
    `stateComplete: true` plus the four section-presence flags. Notes containing either round-state
    marker or a triple-backtick fence are refused before writing. Re-approval replaces that entry
    with a new timestamp and note; the single marker-delimited state block and cohort rows remain
    intact. A later `advance` rebuilds `cohorts` while carrying every other top-level state key,
    including `deliver`, forward unchanged.
54. **Promotion remains explicit.** MVP round specs use `autoPromote: false`. Approval never
    creates a SPEC-116 spec or task and prints `specs/templates/intake-refinement.md` as the path
    for explicit promotion. `autoPromote: true` is refused as not yet implemented rather than
    silently promoting or pretending success.

Acceptance: `rs:round-approve-refuses-incomplete` names an unsettled Refine cohort;
`rs:round-approve-refuses-missing-section` removes traceability and gets a named refusal;
`rs:round-approve-ignores-fenced-and-level-four-headings` proves code comments and level 4+
headings cannot satisfy a required section; `rs:round-approve-keeps-deeper-subsection-body` proves
a deeper subsection remains inside its parent body; `rs:round-approve-rejects-structural-note-injection`
proves marker/fence notes cannot corrupt the state block; `rs:round-approve-refuses-auto-promote-not-yet`
pins the unimplemented promotion refusal;
`rs:round-approve-registered-experiment` proves an unmatched registry entry does not satisfy the
gate while a referenced registered experiment does; `rs:round-approve-records-human-decision`
verifies the UTC timestamp, 400-character note cap, state-complete flag, and all four section flags; and
`rs:round-approve-idempotent-no-promotion` re-approves while retaining one state block, emitting
the intake pointer, creating no spec/task, and materializing no workflow. The
`research_round.py` self-check separately proves an extra top-level `deliver` key round-trips
through `_write_round_state` and `research_index.parse_round`.

| Decision | Sources |
|---|---|
| Completeness gate over compiled Develop and Refine cohorts | `brief-ddmech-p5.md` D-A; SPEC-119 v16 settled-state vocabulary |
| Presence-only delivery checks on free-form Markdown | `design-dd-mechanization.md` section 6; `brief-ddmech-p5.md` D-B |
| Human decision in the existing state block | `brief-ddmech-p5.md` D-C; SPEC-119 v15-v16 round-state contract |
| No automatic promotion in P5 | `brief-ddmech-p5.md` D-D; SPEC-116 intake path |

### v19 (2026-08-02) - P6 Slice 3 correction: resolved-seat isolation and distinct seeds

DD-mechanization P6 Slice 3 makes `workflow plan --seed` repeatable for one critic
workflow. It does not rewire `research_round.py`, change map-reduce seeding, or change
the seed limits. The single-seed F1 path remains byte-identical.

55. **Repeatable, reduced sources with one global cap.** Two or more `--seed <WFID>`
    arguments require every source to have `reduce/reducer.result.json`. The planner
    selects at most 12 findings globally, taking one finding from each source in CLI
    order until the cap or exhaustion. Multi-seed metadata records ordered
    `workflowIds`, source attribution, per-source distribution, and
    `depth = max(source.depth) + 1`; depth above 2 is refused naming the deepest
    source. Divergence profiles are refused before any source is loaded with the same
    Diehl/Diversity Collapse error as single-seed. Duplicate `--seed` workflow IDs are
    refused explicitly before round-robin selection; multi-seed sources must be distinct.
56. **Homogeneous single-seed compatibility.** Zero seeds retain the unseeded path.
    Exactly one seed whose source has at most one executor across ALL its workers
    (`sourceExecutors`, rule 63 — not merely its selected-finding union) calls the
    existing `build_seed_context`, folds the digest into the shared task, writes the
    existing `seed-context.md`, and retains the `{workflowId, depth}` metadata shape
    and packet bytes. Attributed seeds use the new metadata and pointer delivery.
57. **Physical per-branch INV-1 isolation.** For a fork-join branch with
    `spawn.executor`, the planner removes every selected finding attributed to that
    executor and writes `workers/<workerId>.seed-context.md` with a withheld count.
    Attribution is the source workflow executor plus each selected finding's
    `sourceWorkerIds` resolved through `workers[].resolvedExecutor`. Because real
    workflow packets do not stamp top-level `executor`, source-workflow attribution
    falls back to the latest `roundHistory.executor`; reducer access-class fallback
    semantics from v13 remain unchanged. An empty filtered branch file remains valid
    and explicitly says the wave adds no cross-executor finding. Plan-time branch
    executor IDs are validated configured IDs and use the same explicit identity as
    run-time resolution.
58. **Runtime refusal follows the resolved executor.** A branch without `spawn.executor`
    receives a full per-branch digest with a deferred-isolation warning. At both the
    blocking and async per-worker resolution seams, an executor matching any selected
    seed-source attribution is refused before dry-run return, task creation, or worker
    spawn. The error names the worker, executor, conflicting source WFID, and INV-1.
    A pinned branch skips this tooth only when its resolved executor equals its plan-time
    pin. A run-level `--executor` override that resolves the branch away from its pin is
    reclassified and refused on conflict, fail-closed.
59. **Seed files remain inside the trust and budget boundaries.** The merged
    `seed-context.md` and every per-branch seed file are rendered before dispatch and
    included in the DW.1 secret-scan surface; a hit scrubs the partial workflow.
    `--validate-only` renders the same branch texts and pointer-bearing worker prompts
    in memory without creating a workflow directory. Multi-seed map-reduce packets use
    the merged digest pointer and do not apply fork-branch executor filtering.

Acceptance: `rs:seed-multi-round-robin`, `rs:seed-multi-depth`,
`rs:seed-multi-divergence-refused`, `rs:seed-multi-own-executor`,
`rs:seed-multi-run-refusal`, `rs:seed-multi-pinned-override-refused`,
`rs:seed-multi-pinned-own-pin`, `rs:seed-multi-dup-refused`, and
`rs:seed-single-unchanged` in
`testing/scenarios/rs_research_skill.py`. The existing single-seed checks remain
unchanged. `sg_spawn_economy.py`, `bs_branch_spawn.py`, and
`wt_workflow_tree.py` guard the shared spawn, branch-seat, and router boundaries.

### v20 (2026-08-02) - P6 Slice 3 fix round 2: failover-time INV-1

This amendment closes three failover and validation gaps without changing SPEC-115
failover triggers, classification, chain order, circuit handling, or retry semantics.

60. **INV-1 is checked at every failover hop.** Before either the blocking
    `run_one_worker` chain or the async worker accepts a failover executor, it applies
    the same `seed_isolation_conflicts(worker, executor, workflow)` predicate used at
    origin resolution. A conflicting hop is skipped as unusable; the selector may
    continue to the next existing SPEC-115 target. Exhaustion is fail-closed: blocking
    raises the existing chain-exhausted error with an INV-1 reason, while async settles
    the worker blocked and emits an INV-1 failover-refusal event. Acceptance:
    `rs:seed-multi-failover-refused`.
61. **Failover-terminal executor owns finding attribution.** For a reduced finding's
    `sourceWorkerIds`, seed construction prefers the terminal executor persisted in
    `workers[].run.fellBackTo.executor` (blocking) or the last
    `workers[].run.failoverHistory[].executor` (async) over `resolvedExecutor`; the
    source workflow executor remains the existing fallback. Thus plan-time filtering
    and runtime refusal classify a fell-back finding by the executor that produced it.
    Acceptance: `rs:seed-multi-failover-attribution`.
62. **Validate-only shares the rendered seed secret surface.** The in-memory merged
    multi-seed digest and per-branch seed texts pass through the same redacting
    `secret_scan` verdict used by materialization. A secret-shaped seed makes the
    validate-only report invalid without echoing the secret or creating a workflow
    directory. Acceptance: `rs:seed-multi-validate-secretscan`.

### v21 (2026-08-02) - P6 INV-1 heterogeneous single-seed isolation

This amendment closes the single-seed heterogeneous attribution leak while retaining
rule 56's byte and metadata compatibility for homogeneous or unattributable sources.

63. **A heterogeneous single seed is an attributed seed, classified worker-level.**
    Heterogeneity is decided by the source's FULL worker-executor set
    (`sources[].sourceExecutors`, built from every worker that produced material in the
    source workflow, terminal/post-failover per rule 61) — NOT by which executors
    happen to appear in the selected (<=12) findings union (`sources[].executors`).
    A source is attributed whenever `len(sourceExecutors) > 1`, even if a skewed
    top-<=12 reduce selection attributes entirely to one executor. When attributed, the
    planner uses `workflowIds` and `sources` metadata, pointer delivery, per-branch
    INV-1 filtering from rule 57 (which still keys on each selected finding's own
    `executors` — a critic is withheld/refused only for material actually delivered to
    it), runtime override refusal from rule 58, and failover re-checks from rule 60 with
    one source. The runtime guard keys on the presence of a non-empty
    `seed.workflowIds` list, not its count. Legacy singular `{workflowId}` metadata is
    homogeneous by construction and remains unrefused.

Acceptance: `rs:seed-single-hetero-filtered`,
`rs:seed-single-hetero-skewed-selection`, and
`rs:seed-single-hetero-override-refused` in
`testing/scenarios/rs_research_skill.py`.
