# Review: Consolidated UX-Agents Report (2026-07-13)

Source: `docs/research/ux-agents-consolidated-2026-07-13.md` (consolidated GPT report supplied by the
owner, ~230KB — two dossiers + 06–13/07 update). This is NOT a research round (owner instruction);
`[web]` citations are unverified. Fifth document in the W28 series, but DIFFERENT in nature: the four
digests were operational findings; this is the **product blueprint for a future phase** (reference-guided UX
factory for polishing vibe-coded SaaS products).

## Assessment of the report itself

Quality is above the digests: explicit epistemic convention (F/C/I/H/S/P), abandonment criterion for every
proposal, red team + premortem, and a “what I would NOT build first” section matching our discipline point by
point (no mass crawler, no own fine-tuning, no universal beauty score, no agent publishing directly,
“multi-agent with decorative roles” vetoed). Its patterns are those of our research-playbook — proposal cards
can almost be consumed as plan briefs.

## The distinction that organizes everything

Most of the report (Inspiration Compiler, Reference IR, originality firewall, secure site capture, taste
model, autonomous renovator) assumes a harness operating ON external UI targets — the **target-worker-world
family, which is OWNER-GATED**. None of this is today’s backlog; it is the manual for the phase when the owner
opens it. This review separates three buckets:

### 1. Already operating in today’s harness (internal surface)

| Report proposal | Live equivalent |
|---|---|
| Dual-Audience CLI Contract (its P1) | This is house style: `--json`, documented exit codes, `catalog`, frozen surface, `common.emit`, `--help` goldens in cli_registry scenario, `--validate-only` in curation. Its “simple alternative” fallback is what we already do end-to-end |
| UI Constitution + golden tasks (its P0), at our panel scale | SPEC-134 ui_specs + ui_e2e flows (27/27) + qol_panel_chat (12 checks) — miniature golden arena for the only UI we operate |
| “Visual diff needs semantics; pixel diff is noise” (WUICC) | We never built pixel diff — e2e is DOM/assertion-based. A win through parsimony, now with literature support |
| Diversity before convergence (CHI 2024 fixation) | Round methodology: divergence wave (cheap Gemini) → critique wave (NVIDIA), exactly as in Nielsen-heuristics round |
| Functional gates precede aesthetics; non-compensable security as constraint | Our gate doctrine + owner’s pending decision on security-baseline |
| F/C/I/H/S/P convention | Our research packets already require honest confidence class; adopting labels in extract docs costs zero — adopted from this doc onward |

### 2. Converges with existing queue/decisions (reinforcement, not a new item)

- **Workflow-level jailbreak (816/816 composed of benign steps)** → new evidence for the OWNER-GATED
  decision to expand security-baseline (same bucket as SecureVibeBench in code-quality extract). Does not
  open an experiment; informs owner decision.
- **Prismata (trust labels, downgrade-only, tainted lineage)** → our posture is already deny-by-default
  (GLM toolless, third-party trustTier, allowedWritePaths, seed contexts marked `untrusted-derived`); the
  link where untrusted content becomes actionable state is exactly what **EXP-3 (quarantined on promote)**
  covers. Reinforces EXP-3; formal trust lattice waits for external-reference capture phase.
- **VoI Agent Router (it routes itself as “Research”, E4, risk 5)** → it is the Oracle Action Router we
  parked TWICE (quality and dynamic workflows). Three independent documents, same conclusion: without
  calibrated history, no. Its “simple alternative” (deterministic matrix by type/risk) is what we already
  operate via task-profiles.
- **UI2App/screenshot-is-not-spec** → irrelevant today (we do not generate reference UI), but records a
  future-phase principle: app reference enters as a coherent set of states, never a loose image.

### 3. Blueprint of future phase (no action now)

Its P0s for the UX factory — UI Contract, executable design system, isolated capture, multi-oracle mesh,
golden arena — plus the three hardenings from the 13/07 update (Journey Graph for cross-page state,
downgrade-only trust labels, trajectory-level security). When owner opens target/UX phase, this report + this
review are the triage starting point; its U1–U5 and E0–E8 experiments already come with
baseline/metric/abandonment in our format.

## What I did NOT extract as an experiment — and why

Zero new EXPs from this report. Every cheap candidate is either already queued (EXP-3, security decision,
parked router) or belongs to OWNER-GATED phase. Extracting “UX factory experiments” now would violate the
rule followed by the four extracts: measure what we operate, do not build for a product not yet authorized.
Immediate value is reference and independent convergence with already-made decisions.

## Verdict

The report is the best artifact in the series and the least actionable today — for the right reason: it
describes the next phase, not the current one. Recommendation: (a) retain it as the canonical blueprint for
UX-factory phase (intake queue entry points here); (b) use the composed-jailbreak finding as input when owner
decides security-baseline expansion; (c) adopt F/C/I/H/S/P labels in future research docs; (d) no new code
because of this report.
