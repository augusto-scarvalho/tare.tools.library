# Research round — UX/UI design with generative AI (ALT PROVIDER: gemini→codex)

Round opened 2026-07-12 by the `research` flow (SPEC-119), running on the **alternative
provider pipeline**: divergence tier = `gemini-2.5-flash-lite` (cheap generation), critique
tier = `codex gpt-5.6` (smart synthesis). In parallel with the claude implementation loop.
Primary lens: this harness IS a multi-agent supervision tool — its hardest UX problem is making
PARALLEL agent work legible without streaming firehoses; generative-AI UX patterns should serve
that, not add novelty for its own sake.

## Phase 0 — Question, criteria, budget

**Question.** Which generative-AI UX/UI patterns should the harness's OWN supervision surfaces
(the `harness_ui` panel + the chat REPL) adopt to make multi-agent/multi-vendor work legible,
auditable, and cheap-to-review — deterministic-first, GUI-writes-no-state, summaries-are-a-view?

**Success criteria.**
- Buildable UX items, each mapped to a real surface (`harness_ui_page.py` panel section / chat
  engine) + a named UX problem (legibility of parallel work / evidence-not-logs / review cost).
- Deterministic-first + invariants: GUI writes no canonical state (allowlisted run_action only),
  panels CATEGORIZE never STREAM (human-factors rule), summaries are a view not the source.
- DE-DUP: do NOT re-propose the existing **Panel/UX roadmap** (41 items: chat-overlays,
  panel screens, PyO3, docs/Wiki) — attack the DISTINCT gen-AI-UX angle those don't cover.

**Declared budget.** alt provider (gemini divergence 5 / codex critique 4); no wave 3.

## Phase 1 — Grounding (harness UX today)

**Has:** `harness_ui.py` (loopback http.server, token-gated, GET state + allowlisted run_action
POST) + `harness_ui_page.py` (self-contained PAGE, escalation-queue-first, categorize-not-stream);
chat REPL (SPEC-111/114) with tool chips, HUD, stream-json; records/memory tabs; the shipped
syntax highlighter + `/vendor` route; SPEC-110 harness-vs-target subject selector. Ethos:
`docs/SUPERVISION_UI_IDEATION.md`. **Distinct gap area (this round):** the panel shows STATE
(queues, results) but does little to help a human COMPREHEND a wave of parallel agents at a
glance, or to let gen-AI summarize/explain/triage the supervision surface itself.

**Named gaps (anchors — refine in divergence):**
- **UX1** no gen-AI-generated at-a-glance SUMMARY of "what are my N agents doing / where's the
  risk" (the review-cost problem; must be evidence-linked, not a hallucinated narrative).
- **UX2** parallel-work legibility: no visual grammar for a fan-out (who/what/cost/status) that
  scales past a handful of workers without streaming.
- **UX3** no adaptive/risk-ranked surfacing (the escalation queue ranks by blast radius; extend
  the idea to the whole panel — surface what needs a human, hide the rest).
- **UX4** no gen-AI-assisted triage/explain action ON a result/diff (explain-this-failure,
  summarize-this-worker) that stays a VIEW (no state write) + cites evidence handles.
- **UX5 (likely PARK)** fully generative UI (LLM renders the panel) — breaks self-contained CSP
  + determinism; the deterministic patterns above come first.

## Phase 2 — Brief

**Divergence brief (gemini tier).** Generate concrete, deterministic-first gen-AI UX patterns for
THIS harness's panel + chat that attack UX1-UX4, each tied to a real surface, respecting GUI-
writes-no-state + categorize-not-stream + evidence-not-logs. De-dup vs the existing Panel/UX
roadmap.

## Phase 3 — divergence (gemini) — done

`WF-20260712-235736-807892`, gemini-2.5-flash-lite (cheap tier), 5 workers fulfilled. Output was
usable but low-diversity: all 5 converged on UX1 (a "risk radar / agent heatmap" summary), under-
exploring UX2-4 — the expected ceiling of the cheap generation tier. Raw material for the smart
tier to elevate.

## Phase 4 — critique/synthesis (codex) — done

`WF-20260713-000021-215114`, codex gpt-5.6 (smart tier), 4 critics fulfilled. Codex did real
grounding work the cheap tier could not: it VERIFIED the harness source and found several drafts
already exist (the N3 attention/flight-strips, the flat worker cards, the composer), CUT the
duplicates + over-builds (a second dashboard, a new state store, a render-loop LLM), and made
evidence-links a PREREQUISITE for any AI explanation. Cross-critic consensus:
- **validity:** keep two small deterministic views; cut duplicate N3 work; evidence links first.
- **architecture:** build on the existing state snapshot + worker drill-in; no second dashboard /
  state store / render-loop LLM.
- **cost:** existing N3 attention + flat worker cards already cover part of UX1-3 → EXTEND them;
  reserve LLM for an explicit read-only explain action, never polling/rendering.
- **security:** order = extend deterministic Attention (UX1+UX3) → grouped fan-out cards (UX2) →
  deterministic evidence bundles BEFORE any optional LLM explanation (UX4). No render-loop LLM.

**Alt-provider verdict:** the gemini→codex pipeline worked — cheap tier generated breadth, smart
tier verified against source, cut ~half the drafts as already-built or over-built, and returned a
deterministic-first buildable portfolio. A claude round would likely have reached the same
portfolio faster/deeper, but the two-tier split delivered a correct, grounded result at lower cost.

## Phase 5 — portfolio & backlog

Portfolio → the **UX-GA — Generative-AI supervision UX roadmap** section in
`docs/IMPLEMENTATION_BACKLOG.md`. Every survivor EXTENDS an existing deterministic surface (no new
dashboard/state/render-loop-LLM); the only LLM use is one optional, read-only, evidence-gated
explain action. Build order: UX-GA.1 (extend Attention) → UX-GA.2 (grouped cards) → UX-GA.3
(evidence bundle) → UX-GA.4 (optional explain, gated on the bundle).
