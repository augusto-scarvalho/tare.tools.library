# Intake refinement — door NEW checklist (live worker/subagent output)

## Request (verbatim)

> clicar num background agent = ver o que ele está fazendo ao vivo, na UI e na CLI.
> Por que isso nunca foi implementado?

## Covered-check (which door?)

The mandatory lookup that decides door NEW vs door COVERED. Commands were actually
run on 2026-07-11 (HEAD aa9fff9); outcomes recorded verbatim.

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search worker tail live output` | **no hit** — `[]` (empty ledger result) |
| doc-find | `python scripts/harness.py doc-find live tail stdout` | **partial** — surfaced `tasks/harness-self-improvement/PLAN.md` (Gemini smoke, unrelated), `supervision-m2h-hardening.md`, `docs/ARCHITECTURE.md`; **no** hit on the M5 panel spec or any live-worker-output doc |

Interpretation: the *runtime + CLI* ground (live log redirect, `workflow tail`) is
genuinely uncovered — both queries return no relevant spec → **door NEW → SPEC-118**.
The *Agents panel* ground is already owned by SPEC-114
(`supervision-m5-interactive-panel.md`, R11 workers column, R107 documented ceiling
"only harness workers appear; no intra-turn streaming") — duplicating it would be a
defect (SPEC-116 inv. 1), so the panel drill-in ships as a **versioned amendment
(v6)** of SPEC-114, not a new spec.

Decision: **NEW** for runtime/CLI (SPEC-118) **+ COVERED** for the panel (amend SPEC-114 v6).

## Goal

Let a human see, on demand, what a background worker/subagent is actually doing —
its live stdout/stderr — from both the CLI (`workflow tail`) and the GUI (a panel
drill-in drawer opened by clicking a worker card).

## Scope

In scope:
- Redirect worker stdout/stderr to the run-log files at spawn time so they grow
  live (root-cause fix of the PIPE+communicate buffering).
- `workflow tail <WF> [--worker-id] [--lines] [--follow]` — read-only.
- `GET /api/worker` + a panel drawer with human-initiated 1.5s polling.
- Progressive rendering of claude `--output-format stream-json` lines.

Out of scope:
- SSE for logs (polling suffices; upgrade path = the chat SSE channel).
- Vendor-CLI internal subagents (no per-session data source; upgrade = switch the
  claude executor template to `-p --output-format stream-json --verbose`, opt-in).
- Ambient/auto streaming on the dashboard (M5.3 "panels categorize, never stream").

## Actors & surfaces

- Actors: a human supervisor (CLI operator and/or panel viewer).
- Surfaces (CLI / GUI / API / internal): CLI (`workflow tail`), runtime (log
  redirect), API (`GET /api/worker`), GUI (panel drawer).
- UI surface? **yes** → Gherkin required — in the SPEC-114 **v6 amendment** (the UI
  ground it covers); the SPEC-118 CLI/runtime spec is non-UI and carries no Gherkin.

## Proposed acceptance criteria

- [x] Worker logs exist and grow while `status == "running"`.
- [x] Settle semantics (result extraction, rate-limit, returnCode, truncation cap,
      timeout marker, cancel) are byte-compatible with the pre-change PIPE path.
- [x] `workflow tail` returns last-N JSON; unknown WF/worker exits non-zero; a
      never-started worker reports `exists:false` at exit 0; `--follow` streams new
      lines until the group settles.
- [x] `tail` and `/api/worker` are read-only and never probe outside the WF dir.
- [x] Clicking a worker card opens a live drawer; a finished worker still opens
      (post-mortem) with capped logs + task + events.
- [x] `/api/worker` refuses malformed/unknown ids with an error payload (never 500).

## Risks / blast radius

- Touches `async_runtime.workflow_async_run_one_worker` (the settle path shared by
  every async workflow) — regression net: `wf_failover.py` + the async-workflow
  fixture. Child stdout redirected to a file is block-buffered in many CLIs (live
  growth shows only flushed bytes) — documented ceiling, not hidden. Windows: the
  supervisor holds the inherited handles (same proven pattern as
  `supervisor.stdout.log`); concurrent `open("rb")` never blocks the writer.

## Open questions for the human

- Should the claude executor template opt into `stream-json` by default so live
  activity is structured (currently a documented ceiling; on this machine headless
  runs also need an explicit `--permission-mode`)?
