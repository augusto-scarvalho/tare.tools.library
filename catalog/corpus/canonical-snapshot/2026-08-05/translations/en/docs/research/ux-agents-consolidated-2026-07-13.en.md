---
translation_of: docs/research/ux-agents-consolidated-2026-07-13.md
source_snapshot: 2026-08-05-private-github-snapshot
source_language: pt-BR
language: en
translation_status: MACHINE_TRANSLATED_UNREVIEWED
authority_status: DERIVED_NON_AUTHORITATIVE
editorial_migration: true
scientific_refresh: false
historical_reference_date: 2026-07-13
---

# Consolidated Research: AI Agents for Designing, Inspiring, Implementing, Testing, and Refining Interfaces

**Consolidation date:** July 13, 2026  
**Literature horizon:** July 13, 2026, including a focused scan of work published from July 6–13 and adjacent sources that materially changed the conclusions.  
**Scope:** web applications, SaaS, dashboards, GUIs, CLIs/TUIs, and adjacent interfaces produced or refined by generative-AI agents, with controlled use of websites, screenshots, moodboards, design files, and design systems as references.  
**Historical application context:** a multi-agent, multi-vendor harness intended to deliver polished and useful interfaces with progressively less human intervention without sacrificing functionality, accessibility, security, originality, maintainability, or reversibility.

> **Historical editorial English edition.** This document is an English translation and editorial migration of the exact source present in the private GitHub snapshot dated 2026-08-05. It preserves the scientific horizon, vendor state, proposals, doubts, and terminology of the July 13 research. It is **RESEARCH / historical design evidence**, not proof of CURRENT implementation and not automatic TARGET authority. No scientific refresh to August 11 has been performed silently.

## How to read this document

The source consolidated three stages of work into one large dossier:

1. the original question: how AI agents can build, test, and improve UX/UI across web apps, dashboards, GUIs, and CLIs;
2. the operational question: how those capabilities can improve *vibe-coded* SaaS products without human micromanagement;
3. the deeper reference-design question: how a system can use a list of websites as inspiration without degenerating into a screenshot-cloning pipeline.

This English edition preserves that structure. It begins with the integrated synthesis and unified Double Diamond, then preserves **Part I — Autonomous UX/UI Engineering** and **Part II — Reference-Driven UI / Inspiration Compiler** as distinct but connected research dossiers.

## Numbered index

1. Integrated premises and executive answer
2. Literature update: July 6–13, 2026
3. Autonomous improvement of vibe-coded SaaS
4. Unified Double Diamond
5. Integrated reference architecture
6. Integrated experimental program
7. Unified roadmap
8. Red team and pre-mortem
9. Integrated proposal portfolio
10. Part I — Autonomous UX/UI engineering
11. Part II — Reference-driven UI and Inspiration Compiler
12. Consolidated conclusion and TL;DR
13. Future research pointers
14. Bibliography

## Epistemic convention

- **F — observed fact:** directly supported by a source, experiment, specification, or official documentation.
- **C — supported conclusion:** synthesis consistent with multiple pieces of evidence.
- **I — inference:** plausible extrapolation for the historical harness context.
- **H — hypothesis:** claim requiring experiment in the project context.
- **S — speculation:** high-uncertainty research direction.
- **P — experimental proposal:** intervention with baseline, metric, and abandonment criteria.

Proposal labels from the historical source are preserved conceptually:

- **E1–E4:** consolidated evidence → hypothesis;
- **N1–N4:** known application → speculative proposal;
- **M1–M5:** production-proven → conceptual;
- **A1–A4:** immediately applicable → dependent on external advances.

# 1. Integrated premises and executive answer

## 1.1 Problem and objectives

The historical harness could coordinate agents, read and modify repositories, run commands, render interfaces, and operate browsers or equivalent tools. The target question was therefore not merely whether a model could generate frontend code. The research asked how to turn those capabilities into a **governed UX engineering process** that could:

- understand product and user intent rather than optimize a screenshot in isolation;
- use the local design system and component inventory before inventing replacements;
- handle states, viewports, extreme data, interaction flows, accessibility, and performance;
- use external references without leaking authority, executing hostile instructions, or copying protected material too literally;
- produce more than one plausible design direction before converging;
- evaluate functionality, usability, visual quality, originality, and security through different oracles;
- localize and repair defects instead of repeatedly regenerating whole screens;
- make autonomy proportional to risk and reversibility;
- preserve provenance and support PR, preview, canary, rollback, and evidence review;
- learn from human choices and real outcomes without turning preference optimization into dark-pattern optimization.

The historical research treats “beautiful” as **product-appropriate visual and functional quality**: hierarchy, coherence, rhythm, density, typography, content, states, accessibility, performance, and trust—not decorative polish alone.

External pages, screenshots, issues, design files, and retrieved material are untrusted inputs. They can carry prompt injection, sensitive data, protected assets, hostile instructions, or misleading design signals. Rights, trademarks, *trade dress*, terms of service, privacy, and copyright vary by jurisdiction; the system can reduce risk and preserve provenance, but it cannot manufacture a legal conclusion.

## 1.2 State of the field as of July 13, 2026

**(C)** The field had moved beyond “prompt → component.” Contemporary systems could combine text, screenshots, wireframes, Figma-like design artifacts, code, components, and visual feedback. Yet the source found a persistent asymmetry: producing a convincing-looking image or page had advanced faster than implementing complete interaction, demonstrating usability, respecting mature design systems, avoiding fixation, and operating autonomously with sufficient safety.

Benchmarks such as [Design2Code](https://aclanthology.org/2025.naacl-long.199/), [Interaction2Code](https://arxiv.org/abs/2411.03292), [FrontendBench](https://arxiv.org/abs/2506.13832), [FullFront](https://arxiv.org/abs/2505.17399), and [DesignBench](https://arxiv.org/abs/2506.06251) were important precisely because static visual similarity or compilation alone did not represent real interface engineering. In parallel, [S&UI](https://arxiv.org/abs/2501.17799), [UI Remix](https://arxiv.org/abs/2601.18759), [SpecifyUI](https://arxiv.org/abs/2509.07334), and [UIClip](https://arxiv.org/abs/2404.12500) suggested that inspiration retrieval could be semantic, multi-granular, structured, and quality-aware rather than a collection of screenshots.

## 1.3 Central thesis

The harness should not receive a list of websites and ask one model to “absorb the vibe.” The historical proposal decomposes the problem into two coupled systems:

1. **Inspiration Compiler** — transforms external and internal references into principles, structure, relative tokens, components, behavior, preferences, and provenance.
2. **UI Engineering Loop** — transforms that specification into implementation using local components, renders it, tests it, critiques it, repairs localized defects, and controls rollout.

The bridge is a versioned intermediate representation described in the source as **UI Intent IR + Design DNA**. It records:

- the user, job, task, and outcome the interface serves;
- which reference influenced which design dimension;
- local components and tokens capable of expressing that intent;
- mandatory states, viewports, extreme-data conditions, and accessibility requirements;
- which statements are facts, interpretations, hypotheses, or preferences;
- applicable risk classes and gates;
- provenance and transformation evidence;
- rollout and rollback requirements.

## 1.4 Principal conclusions

### Design system as executable grammar

A design system should not be treated as a PDF-style guide pasted into prompts. Tokens, components, variants, stories, accessibility contracts, and examples form an executable grammar. A system that ignores that grammar may produce attractive screens while increasing inconsistency and maintenance cost.

### References must be compiled, not merely attached

A URL, screenshot, or moodboard is an ambiguous signal. The system needs to separate observed structure from interpretation, global influence from local influence, transferable principles from literal assets, and intended inspiration from accidental copying.

### Diversity before convergence

One-reference/top-1 retrieval tends toward fixation. The system should intentionally retrieve diverse examples and generate several structural directions before converging. Diversity is not decorative randomness; it protects the search process from premature narrowing.

### There is no single UX oracle

Build success, visual similarity, accessibility lint, multimodal critique, synthetic-user behavior, human preference, and production metrics measure different things. No one score can safely collapse them. Earlier gates should dominate later aesthetic preferences when the dimensions are non-compensatory.

### Safe autonomy is a gradient

Low-risk reversible fixes may be automated aggressively. Authentication, payments, consent, deletion, permissions, safety-critical flows, and irreversible external publication require stronger gates and human involvement.

### Synthetic users are scouts, not real users

Synthetic personas and agent-based interaction can discover obvious problems, generate hypotheses, and expand test coverage. They are not calibrated substitutes for representative real users.

### Provenance and originality are infrastructure

Reference use requires source identity, permission/risk class, transformation record, provenance, and an originality/proximity check. These are not paperwork added after generation; they belong in the generation pipeline.

### Security starts at capture

External pages must be treated as hostile. Reference capture should use isolation, minimal privilege, no secrets, explicit network policy, taint tracking, and limited retention.

## 1.5 Product proposal: Inspiration-Grounded UX Factory

The integrated historical product proposal is a governed pipeline:

```text
Product objective / UI Contract
        +
Local codebase / design system
        +
Reference Manifest
        ↓
Safe capture and normalization
        ↓
Semantic + structural reference IR
        ↓
Diverse ideation / retrieval
        ↓
Typed composition plan
        ↓
Local component-first implementation
        ↓
Render + interaction execution
        ↓
Multi-oracle validation
        ↓
Originality / provenance firewall
        ↓
Localized repair or human checkpoint
        ↓
PR / preview / canary / rollback
        ↓
Learning from choices, edits, and real metrics
```

The source argues that this architecture is more robust than “design agent” as a monolithic role because it makes inputs, decisions, tests, and effects separately inspectable.

# 2. Literature update — July 6 to July 13, 2026

## 2.1 Method

The historical update prioritized work that changed the architectural conclusion rather than merely adding another UI-generation benchmark. Sources were separated by evidentiary strength: peer-reviewed work when available, recent preprints with clear methods/code, official vendor or standards documentation, and lower-strength community signals for hypothesis generation only.

## 2.2 UI2App: interaction changes the priority

The source identifies **UI2App** as one of the most consequential additions because it focuses on inferring executable interaction, not just visual reconstruction. The implication is direct: the pipeline cannot optimize screenshots first and interaction later. State transitions, event handlers, data dependencies, and feedback behavior must become part of the representation and evaluation contract.

**Experiment U1 — visual versus interaction objective.** Compare a screenshot-dominant generation loop against one that receives an explicit interaction contract. Measure task completion, state coverage, invalid transitions, interaction defects, and visual quality. The historical hypothesis is that interaction-aware generation will lose little visual quality while substantially reducing behavioral errors.

## 2.3 Dashboard2Code: dashboards as data-bound systems

The July update elevated **Dashboard2Code** from an emerging signal to a peer-reviewed reference. The main architectural inference is that dashboards should not be treated as generic visual pages. They bind data semantics, chart choice, layout, filters, empty/error states, density, and analytical tasks.

The derived proposal was a **Verified Dashboard Composer** that receives data schema, analytical questions, chart constraints, and accessibility rules, and is evaluated against data correctness before visual taste.

## 2.4 WUICC-bench: visual regression needs semantics

The historical analysis uses **WUICC-bench** to reinforce that visual difference is more useful when the system can explain *what changed* and whether the difference is semantically important. A raw pixel diff does not tell whether the defect is a clipped label, wrong hierarchy, missing control, intended responsive shift, or harmless antialiasing.

**Experiment U2 — semantic visual regression.** Compare pixel/perceptual diffs, multimodal captioning of changes, and combined localized evidence. Measure true-positive defect localization and repair efficiency.

## 2.5 Prismata: contextual least privilege

The source uses **Prismata** as a pointer toward a stronger capture model: not just “sanitize the page,” but constrain what information and authority are exposed according to context. This strengthens a zero-trust interpretation of reference capture.

**Experiment U3 — contextual least privilege.** Compare broad browser capture with a minimal, policy-scoped capture environment. Measure attack success, reference usefulness, and information retained.

## 2.6 Workflow-level jailbreaks: trajectory safety

The update highlights **“Refused in Chat, Written in Code”** as evidence that security cannot be evaluated only turn-by-turn. An agent may refuse a harmful instruction in natural language yet compose a harmful effect through tools or code later in the workflow.

The design consequence is **trajectory safety**: evaluation must include accumulated actions, generated artifacts, capability use, and eventual effects.

**Experiment U4 — workflow-composed harm.** Seed benign-looking reference content that attempts to redirect later implementation or tool use. Measure whether pointwise safeguards versus trajectory/effect controls prevent the composed violation.

## 2.7 Creativity: fixation and seeding can coexist

The source reconciles two seemingly conflicting literatures: examples can produce fixation, but structured co-creation and seeding can also improve ideation for some tasks and people. The implication is not “show no examples”; it is to control *when*, *how many*, *how diverse*, and *how explicitly dimensioned* the examples are.

**Experiment U5 — seeding versus fixation.** Compare no references, one dominant reference, diverse references, and staged reveal. Evaluate novelty, coherence, task fit, preference, and similarity concentration.

## 2.8 Updated synthesis

The July update broadens the initial architecture into:

> **Inspiration Compiler + Interaction Contract + Semantic Regression Mesh + Contextual Confinement + Trajectory Safety.**

This is a historical research synthesis, not a claim that all named components existed in code.

# 3. Autonomous improvement of vibe-coded SaaS

## 3.1 The real automation problem

A vibe-coded product may be visually inconsistent, structurally fragile, under-tested, over-generic, and locally optimized page by page. “Make it prettier” is therefore under-specified. The system needs to infer product intent, detect cross-page patterns, prioritize defects, respect local conventions, and improve without creating churn.

The source recommends prioritizing issues roughly by **impact × severity × confidence × reversibility**, with explicit exceptions for hard policy/security gates.

## 3.2 Recommended autonomous cycle

```text
Audit product and evidence
        ↓
Prioritize high-impact defects
        ↓
Compile task-specific UI context
        ↓
Generate 2–4 structurally distinct directions when design is underdetermined
        ↓
Converge using non-compensatory gates + preference evidence
        ↓
Implement by reusing local tokens/components
        ↓
Build / types / stories / E2E / keyboard / a11y / extreme-data / viewport / performance checks
        ↓
Critique localized defects
        ↓
Patch locally rather than regenerate globally
        ↓
PR + preview + provenance + canary + rollback
        ↓
Learn from accepted/rejected changes and field metrics
```

The source explicitly warns against an endless autonomous “beautification” loop. Each iteration needs a budget, target evidence, stopping conditions, and a change budget.

## 3.3 Autonomy contract

- **Low risk:** spacing, token normalization, obvious accessibility fixes, component reuse, copy consistency, tests, and reversible local refactors can often be fixed and proposed automatically.
- **Medium risk:** information architecture, major layout changes, new interaction patterns, or high-visibility design changes should usually produce alternatives and request approval before broad rollout.
- **High risk:** authentication, payment, consent, deletion, permissions, legal notices, safety-critical journeys, and irreversible publication require stronger authority and human review.
- **Forbidden by default:** unauthorized capture of private/authenticated sources, reuse of protected third-party assets/code/text, obedience to instructions found in untrusted reference content, or production publication without a rollback path.

# 4. Unified Double Diamond

## 4.1 Discover — signals, actors, and tensions

The historical research combines signals from multimodal UI generation, iterative render-and-repair loops, portable design context, semantic retrieval, remix/riff systems, interaction benchmarks, dashboard benchmarks, browser agents, prompt injection research, creative fixation studies, preference learning, and current vendor/product behavior.

Relevant actors include product owner/founder, end user, designer, frontend engineer, harness supervisor, reference author/owner, security reviewer, accessibility specialist, and legal/compliance stakeholders.

The source maps recurring tensions:

| Tension | Historical response |
|---|---|
| automation vs control | UI Intent IR + risk-proportional autonomy |
| inspiration vs fixation | diverse retrieval + multiple directions |
| fidelity vs originality | relative principles + provenance + similarity firewall |
| beauty vs usability | functionality/accessibility gate precedence |
| generic model vs local system | Context Compiler + local design-system grammar |
| observability vs privacy | minimal capture + TTL + provenance |
| more critics vs cost/bloat | value-of-information routing and ablation |
| personalization vs caricature | uncertainty, decay, sparse feedback |
| renewal vs brand stability | versioned Design DNA + change budget |

The source explicitly borrows useful mental models from compilers, feedback control, distributed systems, zero trust, metamorphic testing, value of information, and creative cognition.

## 4.2 Define — problem map and theses

The integrated problem is decomposed into five major theses:

- **T1 — Compiled context:** agents should receive task-specific UI context derived from product goals, code, design system, component inventory, risk, and relevant evidence.
- **T2 — Typed references:** external inspiration should be represented by influence dimension, provenance, confidence, and allowed use—not by undifferentiated screenshots.
- **T3 — Multi-oracle evaluation:** correctness, interaction, accessibility, robustness, performance, design-system fit, aesthetics, and originality need different evidence producers.
- **T4 — Graduated autonomy:** autonomy expands with reversibility, evidence quality, and policy eligibility.
- **T5 — Sparse taste learning:** human preference should be learned cautiously, with uncertainty and decay, rather than hard-coded from a few approvals.

## 4.3 Develop — architecture and portfolio

The source proposes the following core artifacts:

- `ui-contract.yaml`
- `reference-manifest.yaml`
- `reference-card.json`
- `design-dna.json` or `DESIGN.md`
- `inspiration-plan.json`
- `journey-graph.json`
- `evidence-ledger.jsonl`
- `ui-eval-report.json`

The names are historical design roles, not current canonical tare.tools primitives.

## 4.4 Deliver — gate precedence

A major historical contribution is the explicit **non-compensatory ordering** of gates:

1. policy / security / provenance;
2. build / type correctness;
3. functionality / data / interaction;
4. accessibility and sensitive-flow constraints;
5. responsive behavior / robustness;
6. performance;
7. design-system and product-intent conformance;
8. aesthetics / diversity;
9. originality / proximity;
10. human preference / behavioral outcome.

A beautiful result cannot compensate for a failed earlier gate. If subjective judges disagree at a materially important boundary, the system should abstain or escalate rather than average away uncertainty.

# 5. Integrated reference architecture

```text
Product / task intent
        ↓
Context Compiler
        ↓
UI Intent IR + risk profile
        ↓
Reference Manifest ──→ Safe Capture ──→ Reference IR
        │                                 ↓
        │                         Diverse Retriever
        │                                 ↓
        └──────────────────────→ Composition / Inspiration Plan
                                          ↓
                                  Design DNA + local design system
                                          ↓
                                Planner / Variant Explorer
                                          ↓
                                Component-First Builder
                                          ↓
                                  Sandbox Render / Execute
                                          ↓
         deterministic gates → interaction gates → a11y/perf → semantic visual regression
                                          ↓
                            localized repair / multimodal review
                                          ↓
                            originality + provenance firewall
                                          ↓
                       human checkpoint when uncertainty/risk is high
                                          ↓
                               Evidence Bundle / PR / Preview
                                          ↓
                                   Canary / Rollback
                                          ↓
                           accepted edits + field outcomes
```

The architecture intentionally keeps reference capture, generation, evaluation, and release as separable responsibilities. That makes it possible to replace models/tools without redefining the whole product process.

# 6. Integrated experimental program

The consolidated historical program includes:

| Experiment | Question | Baseline | Candidate | Primary measurements |
|---|---|---|---|---|
| Gold UX tasks | Can we evaluate anything consistently? | ad-hoc review | curated representative tasks | reproducibility, coverage, reviewer agreement |
| Reference format | What form of inspiration helps? | prompt with URLs | screenshot / structured IR / IR + local design system | task quality, novelty, similarity, cost |
| Retrieval | Does diversity help? | top-1 | top-k / MMR / typed retrieval | relevance, novelty, fixation, output diversity |
| Multi-oracle | Do combined gates catch more meaningful defects? | one judge | deterministic + agentic + human layers | false pass/fail, cost-to-detection |
| Context Compiler | Does compiled local context improve quality? | large generic prompt | task-specific local context | reuse, consistency, tokens, repair rate |
| Diff-aware repair | Is local repair better than regeneration? | full regenerate | localized diff repair | regression rate, cost, edit size |
| UX Scout | Are synthetic users useful? | no scout | grounded synthetic exploration | issue recall, false confidence, correlation with real users |
| Dashboard composer | Can data semantics constrain UI generation? | generic page generation | schema/goal-bound composer | data correctness, analytical task success |
| Originality firewall | Can we detect over-proximity without blocking legitimate inspiration? | none | multi-signal proximity/provenance gate | precision/recall, false blocks |
| Taste learning | Can sparse feedback improve preference without caricature? | static style prompt | uncertainty-aware preference model | acceptance, diversity, drift |
| Autonomous renovator | Can ongoing improvement stay bounded? | manual review | change-budgeted autonomous PR/canary | accepted value, rollback, churn, cost |
| Reference security | Can hostile sources redirect the workflow? | broad capture | contextual confinement + taint | exploit success, utility retained |

The document repeatedly insists on local baselines: external benchmark scores do not prove the same gains in the project harness.

# 7. Unified roadmap

## 7.1 0–8 weeks — foundation and observer

- create representative gold tasks and a failure taxonomy;
- inventory design tokens, components, stories, journeys, and critical flows;
- define a minimal UI Contract and UI Intent IR;
- add deterministic build/type/a11y/interaction checks;
- add isolated reference capture and provenance logging;
- run multimodal/agentic critics in observe-only or shadow mode;
- measure cost and disagreement before granting repair authority.

## 7.2 2–4 months — PR copilot

- Context Compiler for task-specific UI bundles;
- component-first generation and local reuse;
- multi-oracle evidence reports;
- diff-aware localized repair;
- typed reference retrieval and composition planning;
- PR/preview-based delivery with explicit evidence.

## 7.3 4–8 months — canary and specialization

- risk-class autonomy;
- canary rollout for eligible surfaces;
- dashboard specialization;
- semantic visual regression;
- journey-aware testing;
- calibrated originality/provenance checks.

## 7.4 8–12 months — preference and renewal

- sparse preference learning with uncertainty/decay;
- Design DNA versioning;
- bounded autonomous renovation with change budget;
- stronger production-outcome feedback.

## 7.5 Research horizon

- causal relation between aesthetic quality and user outcomes;
- independent validation of synthetic users and multimodal judges;
- originality measurement under multi-source inspiration;
- long-horizon brand stability;
- interaction- and motion-aware generation;
- economic and ecological cost of agentic UX loops.

# 8. Red team and pre-mortem

The consolidated source records the following major failure classes:

1. **Beautiful screenshot, broken journey.** The system optimizes render quality while task completion fails.
2. **Distributed copying.** No one source is copied literally, but combined fragments reproduce a recognizable protected design.
3. **Source laundering.** Multiple references obscure the provenance of a dominant borrowed pattern.
4. **Reference compromise.** A crawler or browser agent follows hostile instructions, leaks context, or reaches sensitive resources.
5. **Metric-induced dark patterns.** Preference or conversion metrics reward manipulative interface behavior.
6. **Sophisticated judge bias.** A critic prefers visually complex output even when simpler output is more usable or correct.
7. **Taste caricature.** Sparse feedback collapses into a narrow aesthetic stereotype.
8. **Reference drift.** A source changes after capture, making historical influence difficult to reconstruct.
9. **Third-party persistence.** Content survives in embeddings, caches, or generated assets after raw capture should have expired.
10. **Automation erodes brand identity.** Continuous “improvement” becomes continuous churn.
11. **Pipeline cost exceeds review value.** Too many agents, renders, and judges make automation slower or more expensive than a focused human review.
12. **Ontology becomes bureaucracy.** Rich intermediate representations become harder to maintain than the interface work they were intended to support.
13. **No evaluation truth.** The system accumulates scores without any externally grounded outcome.

Early-warning indicators include rising full-page regeneration, increasing component duplication, high judge disagreement, rollback growth, reference concentration, declining design-token reuse, unexplained originality alerts, and rising evaluation cost per accepted improvement.

# 9. Integrated proposal portfolio

| Proposal | Purpose | Historical priority |
|---|---|---|
| UI Constitution + Context Compiler | compile product/design/risk context into task-specific constraints | P0/P1 |
| Inspiration Compiler | turn references into typed, auditable design influence | strategic core |
| Multi-Oracle UX Gates | separate correctness, accessibility, interaction, aesthetics, originality | P0 |
| Diff-Aware Repair | repair localized visual/interaction defects | P1 |
| Diverse Typed RAG | reduce top-1 fixation and retrieve by influence dimension | P1/P2 |
| Originality + Provenance Firewall | limit literal proximity and preserve source lineage | P1/P2 |
| Journey Graph / UI Digital Twin | represent interaction paths/states for testing and change impact | P2 strategic |
| Personal Taste Model | learn sparse preference with uncertainty | P2/research |
| Continuous Renovator | bounded autonomous improvement under change budget | later-stage |
| Value-of-Information Router | spend expensive model/judge calls only where uncertainty warrants | research |

The source recommends building evaluation and context foundations before highly autonomous generation. The ordering is intentional: autonomy without measurement amplifies uncertainty rather than removing it.

# 10. Part I — Technical dossier: UX with generative AI in the harness

## 10.1 Historical premises

Part I examines autonomous interface engineering independently of the later Inspiration Compiler. It assumes the harness can inspect and modify code, execute tests, render pages, call multimodal models, and delegate specialized work. The objective is not to build a generic app-builder product; it is to improve the quality of interfaces in real repositories while preserving product semantics and engineering constraints.

Web/SaaS is the primary surface, but the source deliberately includes dashboards, desktop/mobile GUI, and CLI/TUI because each surface has different observability, interaction, and accessibility contracts. The historical research argues that the shared abstraction should be **interface intent and evidence**, not one universal pixel metric.

## 10.2 Executive answer

The source separates four capabilities that are often conflated:

1. **visual synthesis** — producing a plausible visual composition;
2. **frontend engineering** — translating intent into maintainable code using local components and constraints;
3. **interaction engineering** — implementing states, transitions, validation, async behavior, keyboard interaction, and data-bound behavior;
4. **demonstrated UX quality** — evidence that representative users can accomplish meaningful tasks efficiently, safely, and accessibly.

The historical conclusion is that progress in visual synthesis was ahead of interaction engineering and demonstrated UX. Therefore a harness should not infer “good UX” from a screenshot score.

Initial recommendations were:

- require a **UI Contract** before open-ended implementation;
- compile local design and product context rather than continually prepend broad documentation;
- generate two to four structural alternatives when the solution is underdetermined;
- use multi-oracle gates with deterministic checks before subjective critics;
- perform localized repair from rendered evidence;
- maintain representative gold UX tasks;
- never auto-release high-impact authentication, payment, consent, deletion, or permission changes merely because automated judges agree.

## 10.3 Foundations

### Human-centered design

The dossier draws on the human-centered design tradition around ISO 9241-210: understand context of use, specify user requirements, produce design solutions, and evaluate against those requirements. In harness terms, that argues against a one-shot generator and toward an iterative evidence loop.

### Measurement

The historical research uses established instruments and frameworks such as SUS, HEART, task completion, errors, time-on-task, accessibility, and engineering reliability. It treats these as complementary lenses rather than a universal score.

### Design system as grammar

Tokens and components constrain the solution space. The dossier points to Design Tokens Community Group work, Storybook-style executable component catalogs, and Figma Code Connect-like mappings as examples of design knowledge that can be made machine-consumable. The useful transfer is architectural: agents should reason over **available semantic components and variants** rather than repeatedly inventing markup from screenshots.

### Accessibility

WCAG 2.2 and ARIA Authoring Practices are treated as stronger external constraints than aesthetic preference. Automated accessibility tools are necessary but incomplete; keyboard navigation, focus behavior, semantics, dynamic states, screen-reader behavior, and representative human evaluation remain important.

### Perceptible technical quality

Core Web Vitals are used as examples of technical properties users experience directly. The historical source cites the then-current thresholds—LCP around 2.5 seconds, INP around 200 ms, CLS around 0.1—as operational targets, while recognizing that product-specific budgets matter.

### Surface-specific contracts

- **Web/SaaS:** responsive layout, browser semantics, forms, async data, navigation, accessibility, performance.
- **Dashboard:** data correctness, analytical intent, chart semantics, density, filtering, extreme values, export/inspection.
- **Desktop/mobile GUI:** native interaction conventions, state restoration, platform-specific accessibility, device constraints.
- **CLI/TUI:** stable textual semantics, keyboard-first interaction, scriptability, discoverability, accessible output, machine-readable modes.

## 10.4 Taxonomy of the field

### Input categories

- text/product intent;
- sketches and wireframes;
- screenshots;
- design files;
- existing code;
- component libraries and design systems;
- interaction traces;
- reference sites;
- production telemetry and user feedback.

### Generation categories

- text-to-UI;
- screenshot/design-to-code;
- component synthesis;
- layout generation;
- interaction synthesis;
- agentic code editing;
- iterative render-and-repair;
- multi-agent decomposition;
- dashboard/data-bound composition.

### Evaluation categories

- compilation/type checks;
- DOM/component structural checks;
- unit/integration/E2E tests;
- visual regression;
- multimodal critique;
- accessibility automation and manual protocols;
- interaction/task benchmarks;
- synthetic-user exploration;
- human preference and usability studies;
- production behavioral metrics.

The source warns against common category errors: visual similarity is not usability; successful build is not successful task; browser-agent success is not proof of human comprehensibility; and model preference is not product outcome.

## 10.5 State of the art and practice

The dossier reviews work such as Design2Code, Interaction2Code, FrontendBench, FullFront, DesignBench, and adjacent systems including UICoder/DCGen/UICopilot/UIOrchestra/UI2Code-style approaches. Their combined signal is that benchmark design is moving from static render similarity toward executable interaction, repository context, component reuse, and realistic frontend tasks.

It also considers agents as interface testers through environments and benchmarks such as OSWorld, VisualWebArena, WorkArena, BrowserGym, AndroidWorld, Terminal-Bench, and CLI-oriented tool benchmarks. The key inference is that a browser/computer-use agent can be a useful **evidence producer**, but the agent’s ability to solve a task is not identical to a human user’s experience.

Historical product signals from Figma, v0, Replit, Stitch, and similar tools are treated as evidence of market direction rather than independent scientific validation. Vendor behavior changes quickly; this editorial edition does not refresh those July 2026 claims.

## 10.6 Bleeding edge and emerging signals

The source highlights several frontier directions:

- generation conditioned on interaction/state rather than screenshot alone;
- agents that operate the generated interface as part of evaluation;
- repository-level frontend benchmarks;
- semantic visual regression rather than raw image distance;
- multi-agent critics and repair loops;
- synthetic users and personas;
- data-aware/dashboard-aware generation;
- agent-safe browsing and prompt-injection defenses;
- richer preference signals for aesthetics and product fit.

These are treated as research directions, not mature foundations.

## 10.7 Critiques, divergences, and negative results

### Pixel-perfect is incomplete

A pixel-perfect replica may reproduce an accessibility failure, broken responsive behavior, incorrect content hierarchy, or a design irrelevant to the product. Visual similarity is useful as one signal when fidelity is actually the goal, not as a universal UX objective.

### LLM-as-judge is not neutral

A multimodal judge can be sensitive to presentation, verbosity, visual sophistication, prompt framing, and model family. The dossier therefore recommends judge calibration, disagreement tracking, human anchors, and deterministic checks for objective properties.

### Automated accessibility is necessary and insufficient

Static scanners catch a subset of accessibility failures. Focus order, meaningful announcements, dynamic behavior, cognitive clarity, and task experience require additional methods.

### Synthetic users can create false confidence

Generated personas can produce plausible narratives with weak empirical grounding. The source uses them as scouts for hypotheses and coverage, never as a replacement for representative users.

### Multi-agent systems can amplify bloat

More specialized critics can increase tokens, latency, duplicated observations, and contradictory recommendations. The historical response is ablation plus a value-of-information policy: a new reviewer should justify its marginal evidence.

### Agent-testers expand the attack surface

A browser agent reads hostile content and has tools. Therefore a test harness can itself become a prompt-injection execution path. Isolation and capability limits are part of UX automation safety.

### Hidden cost matters

Repeated renders, multimodal calls, browser sessions, multiple judges, and broad context can make “automated review” more expensive than a focused human review. Cost-to-useful-evidence is therefore a first-class metric.

## 10.8 Double Diamond — Discover

Signals collected in the source include rapidly improving UI generation, weak interaction assurance, increasingly executable design systems, multimodal visual feedback, browser agents, data-oriented UI work, accessibility requirements, synthetic users, preference learning, and security failures in tool-using agents.

The dossier frames key jobs-to-be-done for the product owner (“improve the product without constant art direction”), user (“complete my task clearly and safely”), designer (“preserve intent and system coherence”), engineer (“receive maintainable diffs rather than regenerated sludge”), and harness supervisor (“know why a change was made and what evidence supports it”).

## 10.9 Double Diamond — Define

The source turns those signals into problems:

- agents lack a stable representation of product/UI intent;
- generic context weakens local consistency;
- evaluation is fragmented across incompatible metrics;
- visual errors are often repaired by costly global regeneration;
- representative journey evidence is sparse;
- risk is not uniform across interface surfaces;
- frontend changes can pass technical checks while harming users;
- tool-using evaluators can be compromised by the interfaces they inspect.

“How might we” questions focus on compiling context, measuring UX with multiple independent signals, localizing repairs, simulating journeys without overtrusting synthetic users, and allocating expensive evaluators only where they add information.

## 10.10 Double Diamond — Develop: proposal cards

### Proposal 1 — UI Constitution & Context Compiler

**Problem:** generic prompts and large context dumps fail to preserve project-specific design rules.  
**Proposal:** compile product intent, design tokens, components, relevant stories, accessibility requirements, risk rules, current task, and nearby code into a task-specific context bundle.  
**Evidence base:** context engineering, executable design systems, repository-aware coding agents.  
**Experiment:** generic prompt versus compiled local context on matched tasks.  
**Success:** more component reuse, fewer style deviations, lower context/token cost, fewer repair cycles.  
**Abandon/pivot:** if compilation cost exceeds gains or bundles become stale/unreliable.

### Proposal 2 — Multi-Oracle UX Gates

**Problem:** one evaluator collapses incompatible dimensions.  
**Proposal:** orchestrate deterministic tests, accessibility checks, interaction evidence, visual/semantic diff, multimodal critique, synthetic exploration, and selective human review under ordered gates.  
**Success:** higher material-defect recall without unacceptable false blocks or cost.  
**Critical constraint:** early safety/functionality gates cannot be compensated by later aesthetic scores.

### Proposal 3 — Diff-Aware Visual Repair

**Problem:** full regeneration introduces regressions and churn.  
**Proposal:** detect/localize a defect, retrieve the responsible component/style/state, and patch the smallest plausible region.  
**Experiment:** full regenerate versus localized repair on planted visual/interaction defects.  
**Metrics:** regression rate, changed lines/components, cost, repair success, time-to-green.

### Proposal 4 — Grounded Synthetic UX Scout

**Problem:** exhaustive human testing is expensive and sparse.  
**Proposal:** use constrained synthetic personas/agents to traverse representative journeys, log confusion/failure hypotheses, and propose human follow-up.  
**Boundary:** scouts generate leads, not user truth.  
**Abandon:** if correlation with real-user findings remains too low or induces systematic false reassurance.

### Proposal 5 — UI Digital Twin / Journey Graph

**Problem:** page-based validation misses cross-page state and journey dependencies.  
**Proposal:** maintain a graph of states, actions, transitions, data requirements, and critical journeys connected to executable tests/evidence.  
**Use:** change-impact analysis, test selection, missing-state detection, and repair localization.  
**Risk:** high modeling overhead; should emerge from code/traces where possible rather than become manual bureaucracy.

### Proposal 6 — Verified Dashboard Composer

**Problem:** generic UI generators may create aesthetically plausible but semantically wrong analytical interfaces.  
**Proposal:** constrain generation with schema, analytical jobs, metric definitions, chart appropriateness, data quality states, and dashboard-specific validation.  
**Gate order:** data/metric correctness before chart beauty.

### Proposal 7 — Dual-Audience CLI Contract

**Problem:** agent-oriented CLIs can become hostile to humans, while human-only interfaces are hard to automate reliably.  
**Proposal:** stable structured/machine-readable outputs plus concise human-friendly interaction, predictable exit/status semantics, keyboard accessibility, and discoverable help.  
**Historical relevance:** a bridge between UX research and the harness’s agent-facing surfaces.

### Proposal 8 — Value-of-Information Agent Router

**Problem:** sending every artifact to every critic wastes cost and often duplicates evidence.  
**Proposal:** estimate uncertainty and expected marginal information to decide whether another renderer, multimodal critic, browser agent, specialist, or human is worth calling.  
**Status:** explicitly research-oriented in the source.

## 10.11 Double Diamond — Deliver and prioritization

Historical priority:

- **P0:** Multi-Oracle UX Gates; representative gold tasks.
- **P0/P1:** UI Constitution & Context Compiler.
- **P1:** Dual-Audience CLI Contract; Diff-Aware Repair.
- **P2 controlled:** Grounded Synthetic UX Scout.
- **P2 domain:** Verified Dashboard Composer.
- **P2 strategic:** Journey Graph / Digital Twin.
- **Research:** Value-of-Information Router.

The portfolio is divided into **adopt now**, **prototype**, **monitor**, **strategic bet**, and **avoid**. The “avoid” category includes autonomous high-risk release, screenshot-only optimization, uncalibrated model judges, and multi-agent review without marginal-value measurement.

## 10.12 Red team and 12–24 month pre-mortem

The Part I pre-mortem anticipates:

- polished demos that fail real tasks;
- component/design-system erosion;
- excessive autonomous churn;
- expensive evaluation meshes nobody trusts;
- accessibility regressions hidden behind automated scores;
- synthetic-user reports becoming theater;
- UI agents following malicious content;
- dashboard visualizations that misrepresent data;
- preference optimization drifting toward dark patterns;
- multiple agents expanding code and process without measurable benefit.

The source requires each risk to have leading indicators, tripwires, and a rollback/abandon path rather than becoming a generic “risk” section.

## 10.13 Evidence gaps

The dossier explicitly records missing evidence instead of converting open questions into conclusions:

- cross-model reliability of multimodal UI judges;
- calibration of synthetic users against representative humans;
- long-horizon effect of autonomous UI refactoring on maintainability;
- reliable measurement of originality versus legitimate design-system conventions;
- causal relationship between aesthetic improvements and product outcomes;
- robust evaluation of CLI/TUI usability for both humans and agents;
- cost-effectiveness of multi-agent review versus targeted deterministic tooling.

## 10.14 Operational recommendations

### Adopt immediately

- component/design-system inventory;
- UI task contracts;
- build/type/E2E/a11y gates;
- representative critical journeys;
- render evidence and PR previews;
- explicit risk classes for UI changes;
- provenance for external references.

### Prototype

- semantic visual regression;
- task-specific Context Compiler;
- localized repair;
- interaction-aware multimodal critics;
- dashboard-specific constraints.

### Research

- synthetic-user validity;
- personal taste modeling;
- value-of-information routing;
- causal UX metrics;
- automated journey-model induction.

### Monitor

- rapidly evolving vendor UI generators;
- multimodal agent benchmarks;
- browser-agent security;
- accessibility evaluation research;
- design-system interchange standards.

### Avoid

- one aesthetic score as merge authority;
- direct capture of private/authenticated references without policy;
- unbounded autonomous “redesign everything” loops;
- copying a reference’s visual identity without transformation/provenance;
- treating generated personas as evidence of user needs.

## 10.15 Part I reference architecture

```text
Product objective / change request
        ↓
Context Compiler
        ↓
UI Intent IR + Risk Profile
        ↓
Planner / Variant Explorer
        ↓
Component-First Builder
        ↓
Sandbox Render
        ↓
Deterministic Gates
        ↓
Localized Repair? ───────────────┐
        │                         │
        no                        yes → patch → rerun affected gates
        ↓
Multimodal / Interaction / Agent Review
        ↓
High uncertainty or high risk?
        ├── yes → Human checkpoint
        └── no
        ↓
Evidence Bundle
        ↓
PR / Preview / Canary / Rollback
```

Historical supporting stores/contracts include a design registry, story graph, journey registry, evidence store, gold-task set, and model/evaluator registry.

A minimal `UI Intent IR` example from the design includes conceptual fields for actor, job, desired outcomes, data, states, actions, components, constraints, risk, and metrics. The exact schema was research material, not a ratified kernel primitive.

## 10.16 Multi-agent escalation without bloat

The source does not recommend a permanent committee of design agents. Instead it proposes progressive escalation:

1. deterministic checks first;
2. one general multimodal critic when evidence is ambiguous;
3. specialist reviewer only for a relevant dimension (accessibility, dashboard/data, security, etc.);
4. second independent critic when uncertainty remains materially high;
5. human review when risk or disagreement justifies it.

This is an early historical form of **evidence-driven evaluator selection**.

## 10.17 Part I experimental plan

- **E1 — Baseline and gold tasks:** build stable representative frontend tasks and manually characterized failure sets.
- **E2 — Multi-Oracle shadow gate:** run automated critics without blocking and compare to human/material defects.
- **E3 — Context Compiler:** compare generic versus compiled task-specific context.
- **E4 — Diff-Aware Repair:** compare localized repair against regeneration.
- **E5 — UX Scout validity:** measure synthetic findings against human or production findings.
- **E6 — Dashboard:** test data-bound generation with planted semantic traps and extreme data.

For stochastic evaluators, repeated trials and uncertainty intervals are preferred to one-shot pass/fail declarations.

## 10.18 Evaluation system

### Outcome metrics

- representative task completion;
- failure/error rate;
- human preference with calibrated protocol;
- accessibility success;
- time-on-task where measurable;
- production adoption/rollback;
- change acceptance and rework.

### Process metrics

- component reuse;
- changed lines/components;
- repair iterations;
- evaluator disagreement;
- evidence latency;
- autonomous abstention/escalation rate.

### Security/privacy

- hostile-reference attack success;
- unauthorized network/data access;
- secret exposure;
- tainted-content propagation;
- provenance coverage.

### Cost/performance

- tokens and model calls;
- browser/render time;
- wall-clock time-to-evidence;
- cost per accepted improvement;
- cost per material defect found.

### Robustness

- multiple viewports;
- localization/text expansion;
- extreme/empty/error/loading data;
- keyboard-only flow;
- browser/platform variation;
- evaluator/model variation.

Leading indicators monitor process drift; lagging indicators measure real outcome and maintainability.

## 10.19 Open questions and opportunity map

Open questions include whether visual judges generalize across product styles, how to separate brand taste from individual preference, when agentic UX testing adds enough value, how much design knowledge should be compiled versus retrieved, and how to quantify the value of an additional reviewer.

The opportunity map favors infrastructure that makes the whole loop more measurable—Context Compiler, evidence mesh, localized repair, journey/state models—over another monolithic “designer model.”

## 10.20 Part I synthesis

The historical synthesis is:

> High-quality autonomous UI engineering requires **intent + executable design system + component-first implementation + render/interaction evidence + multi-oracle gates + localized repair + risk-proportional human validation**.

Generation is only one stage in that system.

# 11. Part II — Technical dossier: Reference-Driven UI and the Inspiration Compiler

## 11.1 Executive answer

The short answer of the historical source is **yes**: there was already a meaningful body of research relevant to agents that use websites, screenshots, and other interfaces as inspiration. But it was distributed across several communities rather than organized under one “AI inspiration compiler” label:

- design by example and creativity support;
- multimodal UI retrieval;
- screenshot/specification-conditioned UI generation;
- layout and component mining;
- design analogy and remix;
- quality, similarity, and preference evaluation;
- provenance, copyright/security, and safe web-agent interaction.

The dossier’s central claim is that **references should be transformed into an auditable intermediate representation before they guide generation**. Instead of asking a model to imitate a page, the system should extract which dimensions are relevant—information hierarchy, density, rhythm, typography, navigation, interaction, component treatment, content pattern, motion, or overall product mood—and compose those influences under explicit limits.

The proposed product role is the **Inspiration Compiler**.

## 11.2 What the evidence supported

The source highlights several signals:

- **S&UI** suggests UI retrieval can use semantic representations rather than purely visual similarity ([S&UI](https://arxiv.org/abs/2501.17799)).
- **UI Remix** supports the distinction between global and local reference influence ([UI Remix](https://arxiv.org/abs/2601.18759)).
- **SpecifyUI** explores structured specifications derived from one or multiple references ([SpecifyUI](https://arxiv.org/abs/2509.07334)).
- **UIClip** investigates quality/relevance signals for UI representations ([UIClip](https://arxiv.org/abs/2404.12500)).
- creativity research shows examples can both inspire and constrain; multiple concepts can reduce narrowing, but seeding effects depend on context.

The historical conclusion is not that these systems prove the proposed architecture. They make it plausible that reference use can be decomposed into retrieval, representation, composition, evaluation, and provenance instead of remaining an opaque prompt trick.

## 11.3 Product thesis

The **Inspiration Compiler** should guarantee, as far as the evidence and policy allow:

1. understand a reference at global, region, component, and behavioral levels;
2. separate observed facts from model interpretation;
3. explain which part of a reference influenced which part of the candidate design;
4. combine several references without allowing one source to dominate silently;
5. translate influence into the project’s local tokens/components rather than copy raw visual artifacts;
6. measure task quality, diversity, and proximity to references;
7. preserve source, permission/risk class, transformation, and decision provenance;
8. support human review and rollback when uncertainty or legal/security risk is high.

It can automate audits of generic-looking pages, reference selection, multiple design directions, token/composition derivation, component refactoring, viewport/state validation, provenance reports, and bounded repair.

It should not silently automate authenticated/private capture, third-party asset/text/code reuse, sensitive-flow redesign, high-impact publication, or legal conclusions about whether copying is permissible.

## 11.4 Foundations: how designers use examples

### Inspiration is a cognitive operation

Examples do not simply provide pixels. Designers use them for framing, generation, communication, comparison, and justification. The same artifact can therefore serve different roles depending on the design question.

### Semantic retrieval before raw pixel proximity

A login page may be visually similar to another page but irrelevant to a dashboard navigation problem. The dossier therefore prefers semantic/task relevance as a first filter, then uses visual/style similarity as another dimension.

### Global and local references

A system may use one reference for macro information architecture, another for typography/density, another for a table or command palette, and a fourth as a negative example. This motivates dimension-specific influence rather than whole-page cloning.

### Intermediate representation

A **Reference IR** captures observed hierarchy, regions, relative spacing, typography roles, components, behaviors, interaction evidence, confidence, provenance, and policy status. Relative values and semantic roles are preferred to literal copied CSS values where possible.

### Reuse the local system

Reference interpretation should end by asking “which local components and tokens express this principle?” rather than “how do I recreate these foreign pixels?”

## 11.5 Taxonomy of the solution space

### Reference types

- public websites;
- screenshots;
- design-system examples;
- Figma/design files;
- product galleries and curated libraries;
- competitor/reference products;
- internal previous versions;
- component examples;
- interaction recordings;
- negative references (“avoid this”).

### Transfer modes

- global structure;
- information hierarchy;
- layout rhythm/density;
- typography roles;
- color/tokens;
- component treatment;
- microinteraction;
- navigation behavior;
- content pattern;
- motion/temporality;
- product mood/brand cues.

### Objectives that must not collapse into one score

- relevance;
- visual quality;
- task fit;
- novelty/diversity;
- brand compatibility;
- originality/proximity;
- permission/policy risk;
- implementation cost;
- accessibility and usability.

## 11.6 Historical line and state of the art

The dossier connects older example-based design/mining systems to modern multimodal retrieval and generation. Layout is treated as structure, not just image appearance. Preference learning is considered useful but underdetermined: approval history can help retrieval and ranking, but a small number of preferences should not become an immutable “taste profile.”

Historical product signals are included to illustrate market direction but are not treated as independent proof. This English edition intentionally does not update vendor capabilities beyond the July 13 source horizon.

## 11.7 Negative results, tensions, and limits

### Inspiration can reduce creativity

A prominent reference can anchor the search space. The proposed mitigation is diverse retrieval, staged reveal, negative references, and explicit generation of multiple structural alternatives.

### Remix does not guarantee coherence

Combining parts from several attractive products can produce a collage. The composition plan needs a hierarchy of design intent and consistency with local Design DNA.

### Homogenization risk

If many systems retrieve the same popular products and optimize against the same aesthetic judges, the web may converge toward a narrow SaaS template. Diversity itself therefore becomes something to measure and budget.

### One AI judge does not know what is beautiful

Aesthetic preference is contextual and partly subjective. The source rejects a universal “beauty score” as merge authority.

### Perceptual similarity is not identical to copying

Two interfaces can look similar because they use common conventions; conversely, a design can distribute borrowed distinctive elements across regions while avoiding a high global similarity score. Originality needs multiple signals plus provenance and human/legal review where material.

### Screenshot without text/context is insufficient

Content, user job, data semantics, interaction, responsive states, and product constraints affect whether a pattern is appropriate.

### References can be hostile

Web content can contain prompt injection or action-inducing instructions. Reference systems therefore need the same or stronger security discipline as general browser agents.

## 11.8 Rights, permission, and provenance

The dossier explicitly frames this as an **operational risk model, not legal advice**.

A practical source policy distinguishes public/allowed references, sources requiring terms or permission review, internal/licensed materials, authenticated/private materials, and prohibited/untrusted sources.

For each influential source the system should preserve, where feasible:

- canonical URL/source identifier;
- capture timestamp/version;
- source class and permission basis;
- regions/assets actually inspected;
- extracted observations;
- derived interpretations;
- influence dimensions;
- candidate artifacts influenced;
- transformation steps;
- proximity/originality evidence;
- reviewer/approval when required.

This is the basis of the historical **originality + provenance firewall**.

## 11.9 Double Diamond for reference-driven UI

### Discover

The source explores why teams use references, what “I like Linear/Stripe/Notion” actually communicates, where examples improve ideation, where they create fixation, how retrieval changes the search space, and what risks arise from crawling arbitrary sites.

### Define

The problem is reframed from “clone these sites” to:

> How can an agent system compile distributed, ambiguous design inspiration into explainable, diverse, locally implementable design constraints while preserving originality, provenance, security, and product fit?

Principles include semantic before literal, local system before foreign implementation, multi-source composition, explicit dominance limits, safe capture, provenance by construction, and uncertainty-aware preference.

### Develop

The source compares several solution families:

- **A — prompt with URLs:** cheapest baseline, weak provenance/structure.
- **B — VLM moodboard summary:** useful compression, still opaque and unstable.
- **C — component/reference RAG:** better retrieval, incomplete composition semantics.
- **D — Inspiration Compiler:** principal proposal; typed IR + composition + provenance.
- **E — personal taste model:** later personalization layer.
- **F — continuous renovator:** long-horizon destination requiring strong evidence and change budgets.

### Deliver

Autonomy evolves through an observer, PR copilot, limited autonomous canary, bounded renovator, and only later preference-driven renewal. The roadmap deliberately separates building trustworthy capture/evaluation from granting broader action authority.

## 11.10 Proposed architecture: Inspiration Compiler

### Logical flow

```text
Reference Manifest
        ↓
Policy / eligibility check
        ↓
Isolated Capture
        ↓
Reference IR + provenance
        ↓
Multi-granular index
        ↓
Diversity-aware retrieval
        ↓
Composition Plan
        ↓
Local Design DNA + component inventory
        ↓
Candidate generation
        ↓
Render / interaction / evaluation mesh
        ↓
Originality + provenance firewall
        ↓
PR / rollout / learning
```

### Reference Manifest

A manifest gives the system explicit source intent. Conceptual fields include source URL/id, purpose, allowed influence dimensions, negative/positive reference, permission/risk classification, capture policy, and expected freshness.

### Safe capture

The historical security posture includes:

- validate URL/domain/DNS/redirects against SSRF-style abuse;
- ephemeral browser context;
- no logged-in state, extensions, or secrets by default;
- block uploads/downloads and external mutations unless explicitly necessary;
- collect only required screenshot, accessibility tree, sanitized DOM/computed-style metadata, and bounded interaction evidence;
- taint outputs derived from untrusted sources;
- use retention/TTL for raw captures;
- never treat instructions inside a reference as harness instructions.

### Reference IR

The IR distinguishes **observed** from **interpreted** properties and records confidence. It favors relative structure—hierarchy, role, density, relationships—over unexamined literal copying.

### Index and retrieval

The source proposes a conceptual ranking objective:

```text
S(r,q) = w1·R + w2·Q + w3·N + w4·F + w5·D − w6·L − w7·K
```

where the terms represent relevance, quality, novelty, preference fit, domain compatibility, literal proximity/dominance, and policy/security risk. The formula is a research sketch, not a calibrated production model.

MMR/submodular-style selection is proposed to balance relevance and diversity. A healthy reference set may intentionally include a global-structure example, a content/hierarchy example, a local-component example, a serendipitous analog, and a negative reference.

### Composition Plan

The plan states which source can influence which dimension and how strongly. A candidate should be able to answer why its navigation came from one reference while its density or component pattern came from another. Dominance limits reduce accidental whole-product imitation.

### Local Design DNA

Design DNA represents durable local product identity: typography roles, spacing/density, shape, color semantics, component conventions, content tone, motion principles, navigation style, and explicitly protected brand invariants. It is versioned and can evolve, but references do not overwrite it implicitly.

### Generation and refinement

Candidates are implemented through local tokens/components where possible. Multiple structural directions are useful when the Composition Plan leaves real degrees of freedom. Render feedback should drive localized repair.

### Evaluation mesh

The historical mesh includes build, interaction, layout, accessibility, performance, design-system conformance, intent, diversity, originality/proximity, security, and product outcome. No single judge owns all dimensions.

### Rollout and learning

Eligible changes progress through PR/preview and, for sufficiently qualified low-risk areas, canary/feature flag. Learning comes from accepted/rejected alternatives, subsequent edits, task outcomes, and rollback—not merely from a model declaring its own design successful.

## 11.11 Proposal cards — Reference-driven UI

### Proposal 1 — Inspiration Compiler

The end-to-end typed pipeline above. Its main novelty is making inspiration **explainable and auditable** rather than prompt ambience.

### Proposal 2 — Multi-granular, diversity-aware RAG

Retrieve at page, region, component, interaction, and concept levels while explicitly rewarding useful diversity. Compare top-1, top-k, MMR, typed selection, and analogical retrieval.

### Proposal 3 — Dimension-specific Composition Planner

Bind sources to influence dimensions and dominance ceilings. Measure whether this improves coherence and reduces over-proximity versus free-form multi-reference prompting.

### Proposal 4 — Originality and Provenance Firewall

Combine provenance, asset/text reuse checks, structural/perceptual proximity, concentration of influence, and policy rules. The firewall should abstain/escalate where the metric is not reliable enough; it does not issue legal judgments.

### Proposal 5 — Secure, policy-controlled Reference Capturer

Treat arbitrary references as hostile external content. Use isolated capture, minimal network/data authority, taint, TTL, and explicit source policy.

### Proposal 6 — Personal Taste Model from Sparse Feedback

Learn preferences from choices and edits while preserving uncertainty, diversity, decay, and separation between individual taste and product/brand identity.

### Proposal 7 — Autonomous Renovator with Change Budget

Continuously identify eligible UX debt and open bounded improvements, constrained by product invariants, evidence, risk class, maximum change magnitude, canary, and rollback. This is a later-stage proposal, not an initial capability.

### Proposal 8 — Reference Evaluation Arena / Gold Set

A curated set of tasks, references, expected influence boundaries, adversarial cases, and human judgments used to evaluate retrieval, composition, originality, and safety before broad autonomy.

## 11.12 Prioritization

The source prioritizes foundations over autonomy:

1. gold evaluation arena;
2. isolated capture + source policy;
3. minimal Reference IR;
4. local Design DNA/component inventory;
5. multi-granular retrieval;
6. composition planner;
7. originality/provenance firewall;
8. calibrated taste learning;
9. bounded autonomous renovation.

It explicitly would **not** start by building a crawler that indiscriminately indexes the web, a universal beauty score, or a fully autonomous continuous redesign agent.

## 11.13 Experiments and ablations

- **Experiment 0 — Gold set:** create representative reference-driven tasks with human characterization.
- **Experiment 1 — Reference format:** URLs-only vs screenshot vs VLM summary vs structured IR vs IR + local design-system context.
- **Experiment 2 — Retrieval:** top-1 vs top-k vs MMR/diverse vs typed/multi-granular retrieval.
- **Experiment 3 — IR ablation:** remove behavior, provenance, hierarchy, confidence, or local-component mapping to identify what matters.
- **Experiment 4 — Composition/dominance:** free-form multi-reference prompting vs explicit dimension binding and dominance ceilings.
- **Experiment 5 — Firewall calibration:** planted near-copy, common convention, transformed pattern, distributed-copy, and benign-similarity cases.
- **Experiment 6 — Taste learning:** static preference prompt vs sparse uncertainty-aware model, measuring acceptance and diversity collapse.
- **Experiment 7 — Existing-SaaS autonomy:** observer vs PR copilot vs bounded canary, measuring accepted value, regressions, rollback, and churn.
- **Experiment 8 — Adversarial security:** prompt injection, redirect abuse, private-resource targeting, exfiltration attempts, malicious assets, and reference poisoning.

## 11.14 Metrics

### Retrieval

- semantic relevance;
- diversity/coverage;
- reference concentration;
- novelty;
- retrieval precision for intended influence dimensions.

### Visual and structural result

- local design-system conformance;
- layout/region correctness;
- semantic visual differences;
- cross-viewport robustness;
- human preference with uncertainty.

### UX and engineering

- task completion;
- interaction defects;
- accessibility;
- component reuse;
- repair iterations;
- maintainability/rework.

### Originality/compliance

- provenance coverage;
- asset/text copying incidents;
- structural/perceptual proximity;
- dominance concentration;
- human-review escalation quality.

### Security

- hostile-reference attack success;
- unauthorized accesses/effects;
- tainted-data propagation;
- secrets/private-data exposure.

### Economics

- model/browser calls;
- tokens;
- wall-clock time;
- cost per accepted change;
- cost per defect avoided or discovered.

## 11.15 Reference-driven red team

The source explicitly attacks the proposal from ten directions:

1. “I like Linear, Stripe, and Notion” collapses into the same generic SaaS template.
2. Distributed copying reconstructs a distinctive product from fragments.
3. Multi-source laundering hides the true dominant influence.
4. Visual/web prompt injection manipulates the agent.
5. Aesthetic metrics reward dark patterns.
6. A judge prefers a sophisticated render that is functionally broken.
7. Taste-profile poisoning or accidental feedback corrupts preference learning.
8. A reference changes after it influenced the design.
9. Third-party content persists in embeddings or caches.
10. “No intervention” becomes loss of brand identity and uncontrolled churn.

## 11.16 Pre-mortem

The system is assumed to have failed after 12–24 months. Likely causes:

- screenshots looked good but real usage was poor;
- automation cost more than focused human review;
- a copying incident destroyed trust;
- taste learning became a caricature;
- the crawler became a major attack surface;
- the reference ontology became bureaucracy;
- there was no trustworthy evaluation truth.

For each cause the source recommends an early warning metric and an abandonment/pivot trigger.

## 11.17 Reference-driven roadmap

### 0–30 days — safe proof of value

- curated gold reference tasks;
- explicit source policy;
- isolated capture proof;
- minimal Reference IR;
- provenance end-to-end;
- human-only approval for generated design changes.

### 31–90 days — implementation copilot

- typed/multi-granular retrieval;
- local Design DNA;
- composition plan;
- component-first generation;
- evidence report and PR workflow;
- originality/proximity shadow checks.

### 3–6 months — calibration and moderate scale

- retrieval/composition ablations;
- firewall calibration;
- semantic regression;
- selective automatic localized repair;
- bounded low-risk canaries.

### 6–12 months — personalization and renewal

- sparse preference learning;
- change budgets;
- bounded renovator;
- longer-horizon product outcome analysis.

### 12+ months — research

- robust originality metrics;
- causal aesthetic→behavior relationship;
- motion/temporal reference semantics;
- cross-surface transfer;
- independent evaluation of commercial design agents;
- ecological/operational economics.

## 11.18 Remaining research gaps

1. transfer from mobile-app reference research to complex web/SaaS;
2. operational definition of originality that is useful but not overblocking;
3. aesthetic quality versus behavioral outcome;
4. personal taste versus brand taste;
5. motion and temporality as first-class reference dimensions;
6. ecological and operational cost of repeated multimodal generation/evaluation;
7. adapting to design trends without eroding product identity;
8. independent product evaluation outside vendor benchmarks.

## 11.19 Practical historical recommendation

If the goal is to improve an existing SaaS immediately, the source recommends a conservative sequence:

1. inventory local design tokens/components and critical journeys;
2. define a UI Contract and protected product invariants;
3. curate a small number of public/authorized references with explicit influence roles;
4. capture them in isolation and compile a minimal Reference IR;
5. create several structural alternatives;
6. implement through local components;
7. run deterministic/interaction/a11y gates before aesthetic critique;
8. produce provenance and similarity/originality evidence;
9. ship through PR/preview and only later canary;
10. learn from accepted/rejected changes without erasing uncertainty.

The historical autonomy contract remains risk-based: reversible cosmetic/system-consistency work can progress further automatically; sensitive workflows and high-impact releases cannot.

## 11.20 Differentiation opportunities

The source records several product/research opportunities that were not central enough to become immediate implementation requirements:

- **Explainable inspiration diff:** show exactly which reference influenced which dimension and what was transformed.
- **References as tests:** references constrain or validate desired properties rather than merely seed generation.
- **Taste with uncertainty:** store preferences probabilistically and decay weak evidence.
- **Diversity budget:** explicitly control how concentrated the inspiration set and output space may become.
- **Counterfactual renewal:** ask whether a redesign would still be proposed if the fashionable references were removed.
- **Licensed/curated library:** reduce permission uncertainty and improve benchmark reproducibility.
- **Anti-template mode:** penalize overused compositions and reward useful structural novelty.

## 11.21 Part II synthesis

The historical dossier’s central product statement is:

> **Do not make references a prompt attachment. Compile them into an auditable, typed, diverse, provenance-aware design influence that is expressed through the local system and evaluated for functionality, originality, security, and product fit.**

# 12. Consolidated conclusion

The two dossiers converge on a single systems view.

A reliable agentic UI pipeline does not begin with “which model designs best?” It begins with **what work must be accomplished, what product/design knowledge is authoritative, what references are admissible, what effects are allowed, what evidence is required, and what uncertainty remains**.

The research therefore favors:

```text
Intent
  + local executable design knowledge
  + governed reference evidence
        ↓
compiled task representation
        ↓
diverse but bounded generation
        ↓
component-first implementation
        ↓
interaction-aware execution
        ↓
ordered evidence gates
        ↓
localized repair / abstention / human review
        ↓
reversible delivery
        ↓
learning from real choices and outcomes
```

Historically, the source used terms such as **Context Compiler, UI Intent IR, Design DNA, Inspiration Compiler, Multi-Oracle Gates, Journey Graph, and Originality Firewall**. In the present tare.tools program these should be treated as **historical semantic roles and research proposals** until reconciled against current canonical bounded contexts and contracts. This English edition intentionally does not perform that reconciliation.

# 13. TL;DR

- Agents can already generate attractive interface artifacts, but visual synthesis is not equivalent to demonstrated UX.
- The design system should act as executable grammar.
- External inspiration should be compiled into typed, provenance-aware design influence rather than copied or attached as raw screenshots.
- Generate diversity before convergence to reduce fixation.
- Interaction, accessibility, robustness, performance, originality, and product fit require different evidence producers.
- Functional/security gates outrank aesthetic preference.
- Synthetic users are useful scouts, not substitutes for representative users.
- Browser/reference capture is a security boundary.
- Localized repair is preferable to repeated whole-page regeneration when the defect can be isolated.
- Autonomy should scale with reversibility, evidence quality, and risk.
- Continuous autonomous renovation is a later-stage capability requiring change budgets, canary, rollback, and trustworthy outcome evidence.

# 14. Future research pointers preserved from the historical source

These pointers are preserved for later conversations. They are **historical/open research directions**, not automatically CURRENT project gaps:

1. **Interaction-aware UI generation and testing** — executable state/transition inference, UI2App-like evaluation, and state coverage.
2. **Semantic visual regression** — explaining visual changes, localizing causes, and distinguishing intended responsive changes from defects.
3. **Contextual confinement for design/reference agents** — least privilege, taint, isolation, prompt-injection resilience, and trajectory safety.
4. **Creativity, seeding, fixation, and diversity budgets** — when examples improve ideation versus narrow the search space.
5. **UX evaluator metrology** — calibration and validity of multimodal judges, accessibility scanners, browser agents, synthetic users, and humans.
6. **Journey graph / digital-twin induction** — extracting durable interaction/state models from code and traces without excessive manual modeling.
7. **Value-of-information routing for assurance** — deciding when an additional critic, browser agent, specialist, or human adds enough marginal evidence.
8. **Operational originality** — multi-source proximity, provenance, common conventions, and defensible abstention thresholds.
9. **Preference learning with uncertainty** — individual taste, brand identity, decay, disagreement, poisoning, and negative preference memory.
10. **Workflow-level UI safety** — unsafe outcomes emerging across multiple apparently benign tool/action steps.
11. **Agent-friendly + human-friendly interface contracts** — especially CLI/TUI and machine-readable operational surfaces.
12. **Causal UX outcomes** — when aesthetic or interaction changes actually improve retention, task success, trust, or business outcomes.
13. **Economic and ecological UX automation** — cost-to-trust, render/judge/model budgets, and whether automated evaluation beats focused human review.
14. **Cross-surface design transfer** — web, mobile, desktop, dashboards, CLI/TUI, and motion/temporal interaction.
15. **Independent evaluation of design-agent products** — avoiding vendor self-benchmarking as the only evidence.


# 15. Bibliography and source links preserved from the historical dossier

The following bibliography preserves the external source links embedded in the July 13, 2026 source. Titles and publication state remain historical; this editorial translation does not silently revalidate them. Duplicate URLs were collapsed for navigation.

1. [Design2Code](https://aclanthology.org/2025.naacl-long.199/)
2. [Interaction2Code](https://arxiv.org/abs/2411.03292)
3. [FrontendBench](https://arxiv.org/abs/2506.13832)
4. [FullFront](https://arxiv.org/abs/2505.17399)
5. [DesignBench](https://arxiv.org/abs/2506.06251)
6. [S&UI](https://arxiv.org/abs/2501.17799)
7. [UI Remix](https://arxiv.org/abs/2601.18759)
8. [SpecifyUI](https://arxiv.org/abs/2509.07334)
9. [UIClip](https://arxiv.org/abs/2404.12500)
10. [DTCG 2025.10](https://www.designtokens.org/TR/2025.10/format/)
11. [Storybook](https://storybook.js.org/docs/get-started/why-storybook)
12. [Figma Code Connect](https://help.figma.com/hc/en-us/articles/23920389749655-Code-Connect)
13. [v0 Design Systems 2.0](https://v0.app/docs/design-systems-2)
14. [Prototyping Dynamics](https://dl.acm.org/doi/10.1145/1978942.1979359)
15. [Design Fixation](https://arxiv.org/abs/2403.11164)
16. [OWASP Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
17. [Anthropic sandboxing](https://www.anthropic.com/engineering/claude-code-sandboxing)
18. [Dashboard2Code](https://aclanthology.org/2026.acl-long.1750/)
19. [UI2App](https://arxiv.org/abs/2607.06306)
20. [Prismata](https://arxiv.org/abs/2607.08147)
21. [Workflow-Level Jailbreak Construction](https://arxiv.org/abs/2607.03968)
22. [Two-player Alternate Uses Test](https://arxiv.org/abs/2607.07522)
23. [Beyond Pixel Diffs / WUICC-bench](https://arxiv.org/abs/2607.01728)
24. [Vibe Coding in Product Teams](https://arxiv.org/abs/2509.10652)
25. [UICoder](https://aclanthology.org/2024.naacl-long.417/)
26. [DCGen](https://arxiv.org/abs/2406.16386)
27. [UICopilot](https://arxiv.org/abs/2505.09904)
28. [UIOrchestra](https://aclanthology.org/2025.findings-emnlp.150/)
29. [UI2Code-N](https://arxiv.org/abs/2511.08195)
30. [WAFFLE](https://arxiv.org/abs/2410.18362)
31. [LLM judge position bias](https://arxiv.org/abs/2406.07791)
32. [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
33. [UXAgent](https://arxiv.org/abs/2502.12561)
34. [Lost in Simulation](https://arxiv.org/abs/2601.17087)
35. [Mind the Sim2Real Gap](https://arxiv.org/abs/2603.11245)
36. [RealUserSim](https://arxiv.org/abs/2605.20204)
37. [ARIA APG](https://www.w3.org/WAI/ARIA/apg/)
38. [WASP](https://arxiv.org/abs/2504.18575)
39. [Anthropic browser defenses](https://www.anthropic.com/research/prompt-injection-defenses)
40. [ISO 9241-210:2019](https://www.iso.org/standard/77520.html)
41. [Brooke, 1996](https://digital.ahrq.gov/sites/default/files/docs/survey/systemusabilityscale%2528sus%2529_comp%255B1%255D.pdf)
42. [Rodden, Hutchinson e Fu, 2010](https://research.google.com/pubs/archive/36299.pdf)
43. [Nielsen](https://www.nngroup.com/articles/ten-usability-heuristics/)
44. [Shneiderman](https://www.cs.umd.edu/users/ben/goldenrules.html)
45. [DTCG](https://www.w3.org/community/design-tokens/2025/10/28/design-tokens-specification-reaches-first-stable-version/)
46. [Storybook testing](https://storybook.js.org/docs/writing-tests)
47. [Figma Dev Mode](https://www.figma.com/dev-mode/)
48. [ARIA APG Patterns](https://www.w3.org/WAI/ARIA/apg/patterns/)
49. [W3C Complex Images](https://www.w3.org/WAI/tutorials/images/complex/)
50. [Web Vitals](https://web.dev/articles/vitals)
51. [Vega-Lite](https://vis.csail.mit.edu/pubs/vega-lite/)
52. [clig.dev](https://clig.dev/)
53. [Microsoft CLI guidance](https://learn.microsoft.com/en-us/dotnet/standard/commandline/design-guidance)
54. [WebSight](https://arxiv.org/abs/2403.09029)
55. [WebCode2M](https://arxiv.org/abs/2404.06369)
56. [Sketch2Code](https://aclanthology.org/2025.naacl-long.198/)
57. [FrontCoder](https://aclanthology.org/2026.findings-acl.220/)
58. [OSWorld](https://arxiv.org/abs/2404.07972)
59. [VisualWebArena](https://arxiv.org/abs/2401.13649)
60. [BrowserGym](https://arxiv.org/abs/2412.05467)
61. [WorkArena](https://arxiv.org/abs/2403.07718)
62. [AndroidWorld](https://arxiv.org/abs/2405.14573)
63. [OSWorld 2.0](https://arxiv.org/abs/2606.29537)
64. [Terminal-Bench](https://openreview.net/forum?id=a7Qa4CcHak)
65. [CISPA summary](https://cispa.de/en/research/publications/104620-terminal-bench-benchmarking-agents-on-hard-realistic-tasks-in-command-line-interfaces)
66. [v0](https://v0.app/)
67. [Vercel AI SDK](https://vercel.com/blog/ai-sdk-3-generative-ui)
68. [Google Stitch](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-ai-ui-design/)
69. [DESIGN.md do Stitch](https://blog.google/innovation-and-ai/models-and-research/google-labs/stitch-design-md/)
70. [Replit Agent 4](https://replit.com/blog/introducing-agent-4-built-for-creativity)
71. [DV-World](https://arxiv.org/abs/2604.25914)
72. [CLI-Tool-Bench](https://arxiv.org/abs/2604.06742)
73. [Context-aware prompt injection](https://arxiv.org/abs/2605.28116)
74. [VibeApps/VibeVulns](https://arxiv.org/abs/2606.23130)
75. [shortcut bias](https://arxiv.org/abs/2509.26072)
76. [benchmark validity](https://arxiv.org/abs/2509.20293)
77. [Storybook a11y](https://storybook.js.org/docs/writing-tests/accessibility-testing)
78. [CodeA11y](https://arxiv.org/abs/2502.10884)
79. [AI personas](https://arxiv.org/abs/2501.04543)
80. [Data-to-Dashboard](https://arxiv.org/abs/2505.23695)
81. [Fine-print attacks](https://arxiv.org/abs/2504.11281)
82. [Anthropic computer use](https://docs.anthropic.com/en/docs/build-with-claude/computer-use)
83. [OpenAI Operator System Card](https://openai.com/index/operator-system-card/)
84. [Playwright](https://playwright.dev/docs/test-snapshots)
85. [PersonaCite](https://arxiv.org/abs/2601.22288)
86. [Generative AI in UX Design and Research](https://dl.acm.org/doi/10.1145/3643834.3660720)
87. [Playwright accessibility](https://playwright.dev/docs/accessibility-testing)
88. [Link](https://dl.acm.org/doi/10.1145/3706599.3720079)
89. [Link](https://aclanthology.org/2025.acl-long.1208/)
90. [Link](https://arxiv.org/abs/2504.04927)
91. [Herring et al., CHI 2009](https://www.engr.psu.edu/britelab/chi2009final.pdf)
92. [Designing with Interactive Example Galleries, CHI 2010](https://hci.stanford.edu/publications/2010/examples/lee-chi2010-examples.pdf)
93. [Screen2Words](https://arxiv.org/abs/2108.03353)
94. [Bricolage, CHI 2011](https://hci.stanford.edu/publications/2011/Bricolage/Bricolage-CHI2011.pdf)
95. [LayoutNUWA](https://arxiv.org/abs/2309.09506)
96. [StructLayoutFormer](https://arxiv.org/abs/2510.26141)
97. [SlideCoder, EMNLP 2025](https://aclanthology.org/2025.emnlp-main.458.pdf)
98. [Figma: design system para IA](https://help.figma.com/hc/en-us/articles/38978644498199-AI-workflows-collection-Best-practices-to-help-Figma-AI-understand-your-design-system)
99. [Rico](https://interactionmining.org/rico)
100. [Webzeitgeist, CHI 2013](https://vis.csail.mit.edu/pubs/webzeitgeist/)
101. [DesignScape, CHI 2015](https://dl.acm.org/doi/10.1145/2702123.2702149)
102. [Scout, CHI 2020](https://arxiv.org/abs/2001.05424)
103. [Umitation, UIST 2021](https://chensivan.github.io/papers/UIST2021_umitation.pdf)
104. [GANSpiration](https://arxiv.org/abs/2203.03827)
105. [VASCAR](https://arxiv.org/abs/2412.04237)
106. [ImageRAG](https://arxiv.org/abs/2502.09411)
107. [UIDEC](https://arxiv.org/abs/2501.18748)
108. [LayoutGMN, CVPR 2021](https://openaccess.thecvf.com/content/CVPR2021/papers/Patil_LayoutGMN_Neural_Graph_Matching_for_Structural_Layout_Similarity_CVPR_2021_paper.pdf)
109. [CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/papers/Shabani_Visual_Layout_Composer_Image-Vector_Dual_Diffusion_Model_for_Design_Layout_CVPR_2024_paper.pdf)
110. [CLASS, WACV 2025](https://openaccess.thecvf.com/content/WACV2025/papers/Manandhar_CLASS_Conditional_Latent_Architecture_for_Search_and_Synthesis_of_Design_WACV_2025_paper.pdf)
111. [CHI 2026](https://arxiv.org/abs/2509.16779)
112. [Apple ML summary](https://machinelearning.apple.com/research/designer-feedback)
113. [AlignUI](https://arxiv.org/abs/2601.17614)
114. [Efficient Personalization of Generative UIs](https://arxiv.org/abs/2604.09876)
115. [Replit](https://docs.replit.com/learn/design/canvas)
116. [v0 Figma](https://v0.app/docs/figma)
117. [Figma AI](https://help.figma.com/hc/en-us/articles/23870272542231-Use-AI-tools-in-Figma-Design)
118. [Figma agent](https://help.figma.com/hc/en-us/articles/37998629035799-Work-with-the-Figma-agent-in-design-files)
119. [Inkspire](https://arxiv.org/abs/2501.18588)
120. [Rethinking Creativity through Design-by-Analogy](https://arxiv.org/abs/2602.09423)
121. [Homogenization of Web Design, CHI 2021](https://aux.engineering.ucsc.edu/publications/Goree_Doosti_Crandall_Su-HomogenizationWebDesign-CHI21.pdf)
122. [Scalable Web Environment Synthesis](https://arxiv.org/abs/2601.04126)
123. [WiserUI-Bench](https://arxiv.org/abs/2505.05026)
124. [MLLM as UI Judge](https://arxiv.org/abs/2510.08783)
125. [VisJudge-Bench](https://arxiv.org/abs/2510.22373)
126. [DreamSim](https://arxiv.org/abs/2306.09344)
127. [CLIP](https://openai.com/index/clip/)
128. [limitações geométricas de CLIP](https://arxiv.org/abs/2503.08723)
129. [visual similarity anti-phishing](https://arxiv.org/abs/2405.19598)
130. [Context Diffusion](https://arxiv.org/abs/2312.03584)
131. [Multimodal ICL](https://arxiv.org/abs/2507.15807)
132. [Visual Prompt Injection](https://arxiv.org/abs/2506.02456)
133. [WebInject](https://arxiv.org/abs/2505.11717)
134. [INPI](https://www.gov.br/inpi/en/services/software/laws-and-regulations)
135. [WIPO Lex — Lei 9.610](https://www.wipo.int/wipolex/en/legislation/details/23318)
136. [USCO Part 3, 2025](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-3-Generative-AI-Training-Report-Pre-Publication-Version.pdf)
137. [RFC 9309](https://www.rfc-editor.org/info/rfc9309/)
138. [W3C PROV-O](https://www.w3.org/TR/prov-o/)
139. [C2PA](https://spec.c2pa.org/specifications/specifications/2.4/index.html)
140. [UI-Bench](https://arxiv.org/abs/2508.20410)
141. [OpenDesign](https://arxiv.org/abs/2510.23272)
142. [PDF](https://faculty.washington.edu/ajko/papers/Swearngin2018Rewire.pdf)
143. [PDF](https://people.eecs.berkeley.edu/~bjoern/papers/duan-uicrit-uist2024.pdf)
144. [arXiv](https://arxiv.org/abs/2412.20071)
145. [arXiv](https://arxiv.org/abs/2406.13631)
146. [ACM](https://dl.acm.org/doi/10.1145/3582269.3615596)
147. [arXiv](https://arxiv.org/abs/2604.10575)
148. [arXiv](https://arxiv.org/abs/2606.05697)
149. Historical placeholder URL preserved from source: https://example.com/reference

---

**Editorial provenance note:** this English edition is derived from the private-GitHub historical source and is not a scientific refresh. A future updated research edition should revalidate source status, add newer literature, and record changes as a separate lineage rather than altering this historical translation.


## Appendix A — Historical machine-readable examples preserved from the source

The following three examples are preserved as code/configuration evidence from the historical Portuguese dossier. Keys are intentionally kept stable because they functioned as proposed schemas rather than narrative prose.

### A.1 Reference Manifest example

```yaml
version: 1
references:
  - id: linear-dashboard
    url: https://example.com/reference
    ownership: public-analysis
    allowed_use: principles-only
    roles: [density, navigation, microinteraction]
    dislikes: [dark-only, tiny-body-text]
    notes: "gosto do foco e da velocidade percebida"
capture:
  viewports: [390x844, 1440x1000]
  authenticated: false
  retain_raw_days: 7
policy:
  max_source_dominance: 0.35
  third_party_assets: deny
  require_provenance: true
```

### A.2 Reference IR example

```json
{
  "identity": {"source_id": "ref_17", "captured_at": "2026-07-12T12:00:00-03:00"},
  "policy": {"class": "C", "use": "principles-only", "retain_assets": false},
  "semantics": {"archetype": "analytics-dashboard", "audience": "ops", "mood": ["precise", "calm"]},
  "global": {"density": 0.72, "hierarchy": "sidebar+workspace", "content_rhythm": "compact"},
  "tokens_relative": {"radius": "low", "contrast": "high", "space_scale": "tight"},
  "regions": [],
  "components": [],
  "behaviors": [],
  "principles": [
    {"claim": "filters stay adjacent to affected data", "why": "reduces mapping cost"}
  ]
}
```

### A.3 Composition-plan example

```json
{
  "goal": "reduzir sensação de template no onboarding B2B",
  "directions": [
    {
      "name": "editorial-precise",
      "global": "ref_02",
      "dimensions": {
        "density": [{"source": "ref_11", "weight": 0.25}],
        "step-navigation": [{"source": "ref_08", "weight": 0.20}],
        "trust-content": [{"source": "ref_19", "weight": 0.15}]
      },
      "local_translation": ["OnboardingShell", "StepNav", "InlineHelp"],
      "forbidden": ["source logos", "source copy", "identical hero silhouette"]
    }
  ]
}
```
