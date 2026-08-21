# Naming Round — Naming the Harness/Project

Owner 2026-07-19: "our harness still has no name. run broad research (NVIDIA ideators + some Sonnet 5 medium), supplement with the project and differentiators, ask for names+explanations, converge."
Orchestrator = this session. Cross-vendor divergence (NVIDIA wide + Sonnet 5).

## What the project IS (seed for ideators)
A **project-oriented, agent-agnostic multi-agent harness** — an "operating system for agentic engineering." The canonical `.harness/` layer owns state (task/continuity/routing/handoff); agents (Claude, Codex, Gemini, NVIDIA) are only adapters. It derives from a reference manuscript ("adaptive project-oriented multi-agent harness architectures") — the manuscript becomes law.

## The DIFFERENTIATORS (the distinctive DNA — what the name should honor)
1. **Measure-before-control:** never introduce a control without the measurement that justifies it. Measure-only probes, noise floors, pre-registered experiments. Scientific rigor, not vibes.
2. **Anti-fabrication / measurement honesty:** `—` for a gap, drop an unmeasurable metric, NEVER invent a number. A system that prefers to say "I don't know" rather than pretend.
3. **Tamper-evident trajectory:** hash-chained event log + causal DAG; provenance firewall; reconciliation of sources of truth (code/docs/history/vendor).
4. **Overseer loop with a hard review ritual:** overseer plans (HARD footprint), workers implement, mandatory review (footprint, gaming hunt, oracle-mutate, verify-before-dispatch).
5. **Gate discipline:** `validate --staged` (scenarios + spec-pack) before every integration.
6. **Cost awareness:** model economy (cheap model for fan-out), delegation ledger, utility function U(route, outcome, cost).
7. **SIGNAL aesthetic:** instrument/mission-control — phosphor, measurement, oscilloscope, rigor.

## Criteria for a good name
- **Evokes:** rigor/measurement + orchestration/harness/control + trust/provenance.
- **Distinctive and ownable:** short, pronounceable, memorable; works as a CLI command + namespace.
- **NOT AI slop:** ban -GPT/-AI suffixes and clichés such as Agent*/`*Flow`/`*Nexus`/`*Forge`/`Orchestr*`/`Synth*`. Nothing generic "on distribution".
- **Fits SIGNAL:** belongs on a mission instrument (phosphor/telemetry/measurement).

## The ask (for each ideator)
Generate **10–15 candidates**, each with: **name** · **what it evokes** (1 line) · **why it fits THIS project** (connect to a differentiator above) · **honest downside** (known collision, ambiguity, pronunciation difficulty). Vary the register (literal, metaphorical, scientific/instrument, mythological/cultural, coined neologism). Avoid the obvious; surprise us.

## Waves
- Wave A (NVIDIA, wide): 5 GLM-5.2 ideators, research-divergence.
- Wave B (Sonnet 5 medium): 3 ideators, distinct perspectives (scientific-instrument, mythological-cultural, coined-neologism).

## Convergence (Phase 5)
Cluster candidates, score distinctiveness × DNA-fit × ownability, cut obvious collisions, and converge on a shortlist + 1 recommendation with rationale.

---

# Phase 5 — Convergence (4 waves: NVIDIA 5 + Sonnet 3)

## Cross-wave frequency (what emerged independently)
NVIDIA strongly converged on: **Caliper 4x · Tare 4x · Nullpoint 4x · Ledger 4x · Plumb 2x · Metron 2x · Assay 2x**. Sonnet brought the "reference standard" cluster: **Fiducial · Etalon · Datum · Timebase** (scientific), **Lachesis · Gnomon · Escapement** (mythological), and weaker coinages (Probemark/Vergauge/Catenal).

## The meta-theme (strongest — appeared in all 4 waves)
**"The zero / reference standard against which everything is measured before acting."** That is the DNA: measure-before-control (measure first) + anti-fabrication (measure only what is real) + reconciliation of sources of truth (the standard that reconciles). The best names EMBODY this in one word.

## Shortlist (distinctiveness × DNA-fit × ownability)

| # | name | what it embodies | why it is strong | honest downside |
|---|---|---|---|---|
| **1** | **Tare** | zeroing a scale to discard container weight and measure ONLY what is real | anti-fabrication + measure-first in one syllable; perfect CLI (`tare run`); distinctive, ownable, zero AI-slop; independently found by 4 ideators | obscure (brand strength, like Vercel); spoken homophone ambiguity (tear/tar) — written form is clean; verify availability |
| **2** | **Assay** | the test that determines the REAL composition of a sample — or reports the gap | literal anti-fabrication (quantifies reality, never invents); distinctive, low collision, clean CLI | less common word; verify availability |
| **3** | **Caliper** | the caliper — measure precisely before cutting | MAXIMUM convergence (4x NVIDIA); recognizable, evocative, CLI-clean | collision: an ed-tech "Caliper" standard + hardware; less ownable |
| **4** | **Etalon** | the Fabry–Pérot reference standard everything is calibrated against | near-perfect fit for source-of-truth reconciliation; distinctive, low collision | obscure/pronunciation (also an asset for branding) |
| **5** | **Fiducial** | the reference mark; from Latin *fiducia* = "trust" | etymology LITERALLY names provenance/trust; distinctive | 3 syllables, pronunciation (fi-DOO-shul); sounds like statistical jargon to some |

Character mentions: **Gnomon** (the sundial rod = the probe that generates the reading — short, distinctive, silent G); **Lachesis** (the Moira who measures the thread = measure-before-control personified — poetic but long/pronunciation); **Datum** (short but reads as "singular of data").

## Architect recommendation
**TARE** — the only one that captures the soul of the project (measure only what is real, discard the rest, never pretend) in ONE syllable; a perfect CLI verb/namespace; genuinely distinctive (not "on distribution"); and independently emerged from several ideators. Its obscurity is a branding asset.
Strong alternatives: **Assay** (more immediately readable, same DNA) and **Caliper** (safe/recognizable choice). If source-of-truth reconciliation should LEAD: **Etalon/Fiducial**.

## Next step (before closing)
Check availability (domain .dev/.io, npm/PyPI, GitHub org, trademark) for the 2–3 favorites — this can be verified once the preferred candidates are selected.
