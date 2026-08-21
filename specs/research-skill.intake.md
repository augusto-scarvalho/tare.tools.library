# Intake refinement — door NEW checklist (Double Diamond research skill)

## Request (verbatim)

> Quero uma skill ativável (ou usada automaticamente em conversas de pesquisa) que
> implemente o processo Double Diamond orientado por evidências que defini
> (divergir→convergir, 2 fluxos de pesquisa, ideação independente em ondas, crítica
> multiagente, convergência set-based, portfólio + rastreabilidade), compatível com
> Claude / Codex / APIs OpenAI-compatible, usando a maquinaria de workflows do harness
> para fan-out/fan-in e delegação. Criar e aplicar (primeira rodada: "o que nosso
> harness deve adotar de pipelines de deep research multi-agente").

## Covered-check (which door?)

Run on 2026-07-11 (clean tree at HEAD aa9fff9); outcomes recorded verbatim.

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search research double diamond ideation skill` | **no hit** — `[]` (empty ledger result) |
| doc-find | `python scripts/harness.py doc-find research double diamond ideation multi-agent` | **partial** — surfaced `docs/HARNESS_IMPROVEMENT_IDEAS.md` and `docs/IMPLEMENTATION_BACKLOG.md` (backlog ideas + MAST/Anthropic anchors), **no** existing spec or playbook for a research skill |

Interpretation: the backlog *mentions* multi-agent research anchors but no spec, skill,
or playbook owns the Double Diamond research process → **door NEW → SPEC-119**. The
fork-join/map-reduce machinery it rides (SPEC-115/agentic workflows) already exists and
is reused, not duplicated.

Decision: **NEW** → SPEC-119 (`research-skill.md`).

## Goal

An activatable research skill that runs the user's evidence-driven Double Diamond
process over the harness's fork-join/map-reduce machinery, cross-vendor, with a single
canonical playbook and an OpenAI-compatible HTTP worker so any chat endpoint can run a
worker.

## Scope

In scope:
- One canonical playbook (`.harness/prompts/research-playbook.md`); vendor surfaces are
  thin pointers (`.claude/skills/research/SKILL.md`, `codex/prompts/research.md`).
- Two read-only fork-join profiles: `research-divergence` (5 ideators), `research-critique`
  (4 critics), branch roles declared as objects (Phase 0b).
- `openai-compat` executor + `tools/openai_worker.py` (one POST → one WORKER_RESULT,
  env-only key).
- Round outputs under `docs/research/<slug>.md`, decisions in `.harness/context/DECISIONS.md`.

Out of scope:
- Per-worker cross-vendor (one executor per group; upgrade = per-branch executors).
- Retry/streaming in the worker (the scheduler owns backoff + circuit breaker).
- Rendering the repo-scoped skill via `agents pair` (documented ceiling).

## Actors & surfaces

- Actors: a human requester + the orchestrator agent (Claude/Codex); workers are
  read-only sub-executions.
- Surfaces (CLI / GUI / API / internal): CLI (`workflow` commands + the two profiles),
  runtime (`openai_worker.py`), internal (the playbook the orchestrator follows).
- UI surface? **no** → the SPEC-119 spec carries **no Gherkin** (CLI/runtime/internal only).

## Proposed acceptance criteria

- [x] One canonical playbook; both vendor surfaces point to it and never diverge from it.
- [x] `research` skill declared in `capabilities.json`; `agents audit` shows it present
      for both vendors with no new gap.
- [x] Both profiles load with `writeAllowed: false` and the declared budgets/branches.
- [x] Each divergence branch yields exactly one packet carrying only its own branch text.
- [x] Branch objects can declare `taskProfile`/`workerRole`; unknown `taskProfile` fails
      at plan time; legacy string branches keep the keyword fallback.
- [x] `openai-compat` is registered and routable via `defaultSpawn`.
- [x] The worker does one POST → one WORKER_RESULT; failure = exit ≠ 0 with no result file.
- [x] The API key is env-only — never in argv, stdout, stderr, or the result file.
- [x] Every normative claim in the playbook has a source; unverifiable = `judgment`.

## Risks / blast radius

- Touches `default_fork_branches` (harness.py) — shared by every fork-join plan; regression
  net: `wf_failover.py` + `rs_research_skill.py`. `_skill_status` patch is scoped to
  repo-scoped skills; `ap_agent_parity.py` is the net. New executor + profiles are additive.

## Open questions for the human

- Should Waves 2-3 (structured techniques) be auto-triggered on a novelty signal, or stay
  manual with the 60% budget gate as the only guard (current: manual)?
