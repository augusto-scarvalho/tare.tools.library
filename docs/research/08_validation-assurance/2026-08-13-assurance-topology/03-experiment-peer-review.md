# 3 — Experimental program, falsifiers and peer review

**Status:** `RESEARCH / PROSPECTIVE PROTOCOL`

**Parent:** [Assurance Topology](README.md)

## Hypotheses

- **H1:** evidence-qualified selection reduces median time-to-first-actionable-failure without reducing recall of the materially relevant failures of the CURRENT corpus.
- **H2:** separating qualification/reliability from ordinary PR regression reduces false blocking due to nondeterminism without erasing negative evidence.
- **H3:** ownership/hermeticity/determinism metadata reduces corrective burden by revealing fixture debt before cross-platform promotion.
- **H4:** mandatory Evidence Families provide a more robust assurance floor than "run every file in the directory".
- **H5:** scheduling by critical path/time-to-trust improves promotion throughput more than optimizing only the total suite duration.

## Initial design

- **Baseline:** `CURRENT_FULL` — complete historical topology.
- **Treatment:** `SHADOW_EVIDENCE_PLAN` — same exact candidate identity, read-only GatePlan, with no authority over the verdict.

The initial dataset must include green and red commits/PR states, BASELINE-CI, CI-REGRESSION fixture debt, NOT_CURRENT evidence, platform-specific failures, fault/timing failures, Authority/Capability/runtime boundary changes and docs-only/low-risk changes.

Record per subject:

- exact commit/tree;
- changed surfaces;
- GatePlan version;
- selected/deferred evidence producers and justification;
- mandatory Evidence Families;
- CURRENT outcomes;
- shadow outcomes;
- OS/runtime identity;
- duration/cost;
- first actionable failure;
- final independent audit/promotion decision.

## Falsifiers

Reject/weaken the proposal if:

1. GatePlan does not select, before the decision, a historical failure that should protect it;
2. lane split increases escaped regressions;
3. stale/missing Graph metadata can lower the mandatory floor;
4. unknown metadata buys skip/nonblocking;
5. a candidate can self-classify a CURRENT regression as harmless evidence;
6. cross-platform bugs systematically appear only in the full suite after being removed from the PR path;
7. planner overhead exceeds the time/evidence saved;
8. reviewers cannot deterministically explain selection/deferment.

## Outcomes

Primary:

- historical/prospective failure recall;
- false-negative / escaped-regression rate;
- time-to-required-evidence;
- time-to-promotable-state / time-to-trust;
- runner-minutes / cost-to-trust.

Secondary:

- flake/nondeterminism rate;
- duplicate/wasted evidence;
- platform coverage;
- explanation coverage;
- corrective burden.

## Peer review / independence

The auditor/author of this line took part in creating the taxonomy and in investigating the incidents. Before strong claims:

1. freeze the codebook;
2. a second reviewer classifies a sample of evidence producers without taking part in the implementation;
3. measure/resolve disagreements;
4. a reviewer verifies a sample of raw CI/run evidence;
5. a prospective canary is analyzed before changing blocking authority;
6. publish negative results and escaped failures.

## Threats to validity

- **Construct:** faster feedback may hide lower assurance; that is why recall/family coverage are mandatory outcomes.
- **Internal:** the repo and fixtures evolve during the study; matched exact-subject replay is preferable.
- **External:** a Python/Windows-first harness does not automatically generalize.
- **Researcher coupling:** taxonomy and audit share an author.
- **Instrumentation drift:** CI-REGRESSION-01 is changing the measurement substrate itself.
- **Survivorship:** CURRENT full-suite failures do not cover bugs that no suite detects.
- **Temporal:** runner load may confound fault-injection conclusions.

## Supporting literature and corpus

1. Spieker, H. et al. (2018). *Reinforcement Learning for Automatic Test Case Prioritization and Selection in Continuous Integration*. arXiv:1811.04122.
2. Abbondante, L.; Canfora, G. (2026). *Commit-Aware Learning-Based Test Case Prioritization for Continuous Integration*. arXiv:2604.25363.
3. Plyusnin, P. et al. (2025). *Targeted Test Selection Approach in Continuous Integration*. arXiv:2509.10279.
4. Sayedsalehi, A.; Rigby, P.; Mierzwinski, G. (2026). *Risk-Aware Batch Testing for Performance Regression Detection*. arXiv:2604.00222.
5. pytest-dev/pytest-xdist — work-stealing scheduler implementation/history.
6. NASA — *Understanding and Evaluating Assurance Cases*.
7. Messick / ETS — construct underrepresentation and construct-irrelevant variance.
8. tare.tools — *Resource Management, Scheduling, Sandbox & Assurance* (2026-08-09), `RESEARCH`.
9. tare.tools — *Assurance & Evolution* (2026-08-09), `RESEARCH`.
10. tare.tools formal research programme v1.6 (2026-07-14), `HISTORICAL/RESEARCH`.
11. tare.tools canonical private repo PR #16 / Issue #17 / GitHub Actions — `INTERNAL OPERATIONAL EVIDENCE`.

## Publication plan

Working title:

> **From Regression Treasury to Evidence Acquisition: Designing Promotion-Safe Assurance for an Agent Operating System**

A publishable version requires a sanitized/reproducible subject dataset, frozen codebook, independent second-review coding, historical replay, prospective canary and explicit publication of failures/negative evidence.

Current claim ceiling: **design-science + longitudinal internal case evidence**. It is not yet a causal benchmark nor external validation.
