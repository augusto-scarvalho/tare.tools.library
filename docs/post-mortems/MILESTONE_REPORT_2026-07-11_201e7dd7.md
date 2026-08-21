# Milestone report — 2026-07-11: live worker observability + research skill

Closed record of the 2026-07-11 session (pattern: `SELF_EVOLUTION_REPORT.md` — compact
status + links to evidence, no duplicated logs). History lives in the commits and the
records ledger; the living artifacts are linked, not copied.

## What shipped (5 commits)

| Commit | Delivery | Spec artifacts |
|---|---|---|
| `dd5179b` | **SPEC-118 live worker observability** — worker stdout/stderr stream to `run-logs/*.log` while running (root-cause fix of PIPE+communicate buffering); read-only `workflow tail [--follow]`; panel agent cards → live-output drawer (`GET /api/worker`, stream-json progressive rendering, post-mortem) | intake + `specs/40-features/worker-live-tail.md` (SPEC-118) + `supervision-m5-interactive-panel.md` v6; 17 new deterministic checks |
| `41e9277` | **Perf polish** — mtime-cached panel ticks (idle tick = 2 stats, not ~120KB re-parse); bounded `events.jsonl` reads; `--follow` made strictly read-only (rule-6 conformance) + exit footer; last-activity on agent cards; acceptance fixture 37.9s→29.0s | SPEC-118 v2 + SPEC-114 v7 |
| `3cd100e` | **SPEC-119 research skill** — Double Diamond playbook (`.harness/prompts/research-playbook.md`) over harness fork-join; cross-vendor surfaces (`.claude/skills/research/`, `codex/prompts/research.md`, `capabilities.json`); explicit per-branch roles `{title, taskProfile, workerRole}`; `openai-compat` executor + `tools/openai_worker.py`; 2 research profiles | intake + SPEC-119 (11 rules); 9-check scenario incl. local-stub e2e |
| `005c38d` | **First-round machinery fixes** — validator accepted URLs/prose evidence (dead URL guard + `lstrip("./")` ate dot-dirs); headless claude spawn on Windows (`_resolve_argv0` which-resolution + `-p` template); output caps calibrated (9000/10000) | SPEC-119 v2 (rules 12-14) |
| `7d6f6a3` | **Research round executed** — 5 ideators → 25 concepts / 9 clusters; 4 role-routed critics → 36 verdicts; portfolio + traceability matrix; decisions D002-D004; 10 draft tasks promoted | `docs/research/deep-research-pipelines.md` |

Pre-work: bounded correctness/efficiency audit of the fork-join machinery — sound
(7 scenarios green, 3 suspected bugs refuted); quantified: required-reads ≈ 16× the
packet per worker, `chars/4` underestimates ~30% (both now drive TASK-002 E1/E2).

## Round outcome (portfolio, short form)

- **Núcleo:** estimator calibration ("run it, not build it"); citation-verification
  duty on the validity critic; effort-scaling guidance.
- **Experimentos:** E1 digest A/B (≥40% input cut, no quality drop), E2 calibration
  measurement, E3 least-privilege env + secret-scrub (critics found workers inherit
  the full parent env, API keys included).
- **Aposta:** `plan --seed` convergence-only, depth-bounded.
- **Rejeitadas com gatilho:** checkpoint-resume (~10× cost trigger), hierarchical
  reduce (join non-associative), mid-wave early-stopping, decision telemetry as stated.

Full evidence matrix, genealogy, verdicts and the traceability matrix:
`docs/research/deep-research-pipelines.md`.

## Closure actions (this report's commit)

- **Escalation `self-review/target/PrintIntel/file-budget` (high, 2026-07-10)
  resolved** → `tasks/printintel-products-split/PLAN.md` (TASK-003): plan-first
  fragmentation of `products.py` (1861 → ≤800-line modules) in the PrintIntel target;
  actual refactor is a separate engagement in that repo.
- **Draft tasks curated** (10 → 5): `tasks/research-portfolio/PLAN.md` (TASK-002)
  carries E1/E2/E3 + the seeded-wave bet + the `generate_handoff` budget defect,
  each with the critics' mandatory conditions; the 3 checkpoint-resume drafts were
  closed as recorded rejections, not tasks.

## Known-open

- TASK-002 items (E2 ordered first — calibration rebases every profile budget).
- TASK-003 PrintIntel fragmentation (needs a run against the target repo).
- `generate_handoff` cannot regenerate a passing handoff today (TASK-002 M1).
- OneDrive sync churn on live-growing logs (operational; consider excluding
  `.harness/workflows/` from sync).

Gates at close: spec-pack 322 pass / smoke 313 pass, 0 fail.
