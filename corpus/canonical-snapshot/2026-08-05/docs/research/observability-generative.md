# Research round — generative AI applied to observability (ALT PROVIDER: gemini→codex)

Round opened 2026-07-13 by the `research` flow, on the alternative provider pipeline (divergence
= gemini-2.5-flash-lite, critique = codex gpt-5.6). In parallel with the claude loop + Round 1.

## Phase 0 — Question, criteria, budget

**Question.** How should generative AI help the harness OBSERVE and DIAGNOSE its own operation
(cost anomalies, workflow/agent health, drift, failure patterns) — deterministic-first, so the
LLM is used only where deterministic detection/aggregation genuinely falls short, and always
evidence-grounded (points at a real metric/trace/record, never a hallucinated cause)?

**Success criteria.**
- Buildable items, each mapped to a real observability seam (`cost_metrics`/CE.2 economy meter /
  DW.3 graph metrics / `trace`+events.jsonl / records ledger / self-review / control-liveness /
  the escalation ledger) + the observability problem it solves.
- Deterministic-first: prefer a deterministic detector/aggregator over an LLM; when an LLM helps
  (diagnosis narrative, trace summarization), it is a VIEW over already-computed signals, cited.
- Invariants: no resident daemon (verify-on-demand), summaries are a view, eviction≠deletion,
  observation must pay for itself (net-cost-positive).
- DE-DUP: the harness already has cost_metrics + CE.2 economy meter + DW.3 graph-shape metrics +
  the self-review cost-outlier detector + control-liveness + trace/trace-export. Do NOT re-propose
  those — attack the DISTINCT gen-AI-observability angle they don't cover.

**Declared budget.** alt provider (gemini divergence 5 / codex critique 4); no wave 3.

## Phase 1 — Grounding + named gaps

**Has:** `cost_metrics` (per-workflow cost/tokens, costBasis) + CE.2 economy meter (amplification,
in/out split) + DW.3 graph-shape (fan-out/depth/makespan/critical-path); the self-review
**cost-outlier detector** (median×3 threshold — it raised a real escalation this session);
control-liveness (6 declared controls); `trace`/`trace-export`/events.jsonl; records ledger +
subject; the escalation blast-radius ledger. **Distinct gap area:** the harness DETECTS point
anomalies (a single costly workflow) but does not DIAGNOSE (why / what pattern / what to change),
SUMMARIZE a trace, or spot MULTI-run drift — and has no gen-AI layer that turns raw signals into
an operator-legible, evidence-cited diagnosis.

**Named gaps (anchors — refine in divergence):**
- **OB1** no cross-run DRIFT/trend detection (a role/profile/model getting slower or costlier over
  time) — cost_metrics has the history but nothing trends it.
- **OB2** no DIAGNOSIS layer on an anomaly — the cost-outlier escalation names the WF but not the
  likely cause (bad split? wrong profile? a runaway worker?); a deterministic feature-extract +
  an optional evidence-cited LLM explanation.
- **OB3** no TRACE SUMMARIZATION — a long workflow trace/events stream has no compact "what
  happened + where it went wrong" view (evidence-linked, not a re-dump of logs).
- **OB4** no FAILURE-PATTERN clustering across runs (which failureClass/role/executor repeats) —
  records/escalations have the data; nothing aggregates the pattern.
- **OB5 (likely PARK)** predictive/agentic auto-remediation — bleeding-edge + violates human-gated
  routing; deterministic detection + diagnosis first.

## Phase 2 — Brief

**Divergence brief (gemini tier).** Generate concrete, deterministic-first gen-AI observability
patterns attacking OB1-OB4, each tied to a real signal source (cost_metrics/DW.3/trace/records),
deterministic-detector-first, LLM only as an evidence-cited VIEW, no daemon, net-cost-positive.

## Phase 3 — divergence (gemini) — done

`WF-20260713-001057-249717`, gemini-2.5-flash-lite, 4 of 5 fulfilled (worker-005 absent — a
cheap-tier reliability blip). Drafts converged on OB1 trend + OB2 diagnosis; "directionally
valid but unbuildable as written" (no sources, unjustified k-means/time-series/LLM-causal) per
the codex critique. Usable raw material.

## Phase 4 — critique/synthesis (codex) — done

`WF-20260713-001154-747986`, codex gpt-5.6, 4 critics fulfilled. Source-verified again: the
existing cost ledger / CE.2 economy / DW.3 graph metrics / cost-outlier review / trace-export /
escalation ledger are SIGNAL SOURCES, not new proposals; the existing **delegation-cost-trend**
already covers a narrow OB1 slice → do not duplicate. Consensus: keep FOUR bounded, verify-on-
demand, DETERMINISTIC views; any LLM output is an opt-in, evidence-cited, redacted VIEW only —
no daemon, no network, no render-loop. Cut generic dashboards/daemons + raw-summary re-dumps.
Build order (security lens): failure-pattern clustering → trend → diagnosis → trace digest.

## Phase 5 — portfolio & backlog

Portfolio → the **OB — Generative-AI observability roadmap** in `docs/IMPLEMENTATION_BACKLOG.md`.
Alt-provider verdict (2nd round): confirmed — gemini breadth, codex verified against source, cut
the unbuildable/duplicate drafts, returned a deterministic-first portfolio. Every survivor is a
verify-on-demand deterministic aggregation of already-durable signals; the ONLY LLM use is an
opt-in evidence-cited explanation over a deterministic feature card.
