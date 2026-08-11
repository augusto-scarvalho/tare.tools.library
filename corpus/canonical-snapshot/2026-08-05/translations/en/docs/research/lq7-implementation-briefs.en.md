# LOOP QUEUE 7 — Ready Briefs + Saved Questions (Backlog-First, Post-D012)

DURABLE index of the plan briefs. Full briefs live under `.harness/handoff/plan-lq7-*.md` (gitignored); final decisions + **saved questions** are mirrored here. All 5 D012 rounds CLOSED; owner: "start drafting the plans, sequential order by criticality."

**Criticality order (LOOP QUEUE 7 in `IMPLEMENTATION_BACKLOG.md`, decided by the overseer):**
1. **Q7-1 harness-own sandbox** — SPEC-151 complete (`specs/40-features/harness-own-sandbox.md`), P0 security.
2. **Q7-2 C1** decision constants + evidence grades (foundational governance).
3. **Q7-3 C18 route churn + C6 CTS** (measure-only; unlocks hysteresis C9).
4. **Q7-4 C3** capability support states.
5. **Q7-5 C2** residual risk register (consumes Q7-1 output).
6. **Q7-6 C5** approval metrics.
7. **Q7-7 C19 Π-lite + C20 recovery** (measure-only, lower urgency).

Implementation starts from the top when the owner authorizes it; one item at a time.

## Q7-1 — harness-own sandbox (SPEC-151, plan = the spec itself)
Complete spec at `specs/40-features/harness-own-sandbox.md` (not a gitignored brief — committed spec). SB-1 Job Object + SB-2 dual-mode NTFS ACL + SB-3 degradation manifest = no-admin core. Saved questions (Q1-Q4) are in the final section of the spec.

## C1 — decision constants + evidence grades (`plan-lq7-c1`)
Table §6.6 (α/power/δ_Q/δ_C/δ_L/δ_V/ECE) + lexicographic rule + grades 1-4 + factor typing in `EXPERIMENT_METHODOLOGY.md`; `evidenceGrade` field in registry. Footprint: methodology, `experiment_registry.py`, exl spec, exl scenario.
**Saved questions:**
- Q1: should `evidenceGrade` become a column in the pxe panel now or as follow-up?
- Q2: should `_advise` suggest a grade heuristically (shipped→≥3) or only point to the document? (proposal: only point)
- Q3: should already-shipped EXPs receive a retroactive grade in an owner curation pass? (~10 min)

## C18 — route churn probe (`plan-lq7-c18`), measure-only
`route_churn_probe.py` over the route ledger (churn per `demandId` + reversals), Floor L13 as threshold. Prerequisite for C9 hysteresis (measure before control). Does not touch route-loop.
**Saved questions:**
- Q1: should "material evidence" use a simple proxy (new outcome/riskFlag) or a richer criterion?
- Q2: panel tile now or artifact only? (proposal: artifact)
- Q3: cross-session churn or period-based? (proposal: global + byRoute)

## C19+C20 — Π-lite + recovery probes (`plan-lq7-c19-c20`), measure-only
Π = ⟨1−viol, 1−overrun, 1−replay_div, recovery, 1−unknown⟩ with critical-violation veto (mirrors C1 lexicographic rule); 4 recovery metrics from the records ledger. A component with no data = honest n/a, never fabricated.
**Saved questions:**
- Q1: aggregate Π or vector only? (proposal: vector + veto flag, never scalar alone)
- Q2: "last-good" for recovery-point-error = last gate pass? (proposal: yes)
- Q3: one probe or two? (proposal: two; worker unifies if reader is the same)
- Q4: couple to D008 M-frame or remain artifact? (proposal: artifact; coupling is an owner decision)

## C6 — cost-to-success in `metrics` (`plan-lq7-c6`)
`cost_metrics.summarize()` + `costToSuccess`/`costToUsefulOutcome` + `byModelCTS`, derived from delegation ledger. Footprint: `cost_metrics.py`, ob scenario, cost spec.
**Saved questions:**
- Q1: does `partial` enter the `costToUsefulOutcome` denominator? (proposal: no)
- Q2: CTS by task class? depends on task taxonomy (proposal: defer)
- Q3: CTS per session or global+byModel only? (proposal: global+byModel)

## C3 — capability states native/emulated/degraded/unsupported (`plan-lq7-c3`)
`supportState` field in `capabilities.json` (formalizes Codex SubagentStop note); helper + audit in `agent_parity.py`. **`capabilities.json` is NOT protected (recon confirmed)** → free edit. Footprint: `capabilities.json`, `agent_parity.py`, SPEC-113, ap scenario.
**Saved questions:**
- Q2: `supportState` per capability or per (capability × vendor)? (proposal: per vendor when they diverge)
- Q3: should `degraded` automatically lower the maturity score in self-assessment? (proposal: yes, follow-up)

## C2 — residual risk register + doctor advisory (`plan-lq7-c2`)
`.harness/state/residual-risk-register.json` (schema §14.7-2) + `risk list/show` verb + doctor `residual-risk-review-due`. NEW SPEC-116 door. **Consumes R2 output** (seed list changes once the sandbox closes the "HTTP without sandbox" risk). Footprint: state json, `repo_health.py`, cli_registry, new spec, rr scenario.
**Saved questions:**
- Q1: who is the default `acceptanceAuthority` for seed risks? (requires real name/handle)
- Q2: `risk add/accept` via CLI now or follow-up? (proposal: follow-up — acceptance is an authority act)
- Q3: should I list the 4 seed risks or should owner review first? coordinate C2 AFTER R2
- Q4: `reviewDate` cadence? (proposal: 90d, aligned with EXP `reviewBy`)

## C5 — approval-service metrics (`plan-lq7-c5`)
`approvals` block in metrics (`pending`/`sloBreached`/median-p95 age/`overrideRate`/`invalidatedCount`/`expired`), reusing `_age_fields`/`sloHours` from `decision_inbox`. Footprint: `cost_metrics.py` or inbox collector, di scenario, spec.
**Saved questions:**
- Q1: is `overrideRate` measurable? only if the record stores recommended vs chosen (if not stored today, the metric becomes 🔬 and leaves this slice) — VERIFY in recon
- Q2: per-session or aggregate? (proposal: aggregate)
- Q3: `post-approval incidents` requires linking decision→effect → outside this slice

## C8 — ~~doctor advisory for expired EXP~~ ALREADY EXISTED
Recon found `repo_health.checks` check (6) `experiment-overdue` already doing this. Removed from queue; backlog corrected (§6.4 → ✅ done).
