# Research round — backlog dependency + provenance graph (AI-assisted grooming)

Double Diamond over the harness (`.harness/prompts/research-playbook.md`). Orchestrator: this session
(Opus overseer). Executors this round: **NVIDIA** (openai-compat, divergence fan-out) + **Sonnet 5 high**
(claude, discovery + critique — the stronger role). Started 2026-07-19.

> **Sequencing note (discipline):** the `design-system-guard` `validate --staged` gate is IN FLIGHT.
> Phases 0-2 write only `docs/` (safe). Phases 3-5 use `workflow plan` (writes `.harness/workflows/`)
> and `.harness/context/DECISIONS.md` / registry — those START ONLY AFTER the gate passes and the
> guard feature is committed (SPEC-137: never write `.harness/` or commit while a gate runs).

## Question

How do we make backlog grooming **automatically discover and map DEPENDENCIES** across the backlog
(and across the experiment + research boards), using generative AI **and** classic techniques — so
that the harness tracks (a) which items depend on / block which, (b) the PROVENANCE of each idea
(where it came from: which chat, research finding, experiment, spec, decision), (c) how a NEW idea
RIPPLES through the dependency chain to flag plans that need revision, and (d) how this graph makes
information-seeking (the next groom, the next research round) more efficient. Unite the knowledge
frontier with agile frameworks and our CURRENT structure (the `backlog-groom` skill, the derived
`panel-tasks-board` kanban, the `research` traceability matrix, the experiment registry, the intake
queue) — not a greenfield tool.

## Success criteria (what a good answer must satisfy)

- **Actors:** the groom orchestrator (auto edge-inference), the overseer (reads the graph to sequence
  work + catch ripple), the owner (sees provenance + why-this-now), a research/experiment round
  (feeds ideas into the graph with genealogy), the derived kanban (renders edges + lanes).
- **Constraints (our invariants):** harness-native (canonical state in `.harness/`, git source of truth);
  derived-not-duplicated where possible (the tasks-board is pure-derived — a graph should reuse that);
  GUI-writes-no-state; measure-honesty (no fabricated edges — an inferred edge is a CLAIM with a
  confidence + source, never asserted as truth); AI is SUPPORT not verdict (LLM-inferred edges get
  audited, like the groom miner-audit split); cheap-first (Gemini/NVIDIA discover before frontier);
  offline/zero-friction unaffected.
- **A good answer delivers:** a portfolio of edge-inference techniques (classic + AI) scored on
  novelty × maturity; a board/kanban design that shows dependency + provenance edges; a ripple/change-
  impact mechanism that flags plans needing revision; a data model that unifies backlog + experiments
  + research + intake provenance WITHOUT a second write path; and at least one measurable experiment
  (inference precision vs a classic baseline) registered per the methods library.

## Declared budget + width (Phase 0 gate — no budget/width => no wave)

- **Phase 1 Discover (now):** 4 background discovery workers, **Sonnet 5 high**, WebSearch/WebFetch,
  EXPLORATORY. Each returns an evidence table only (claim | source | type | year | confidence |
  maturity), `[web]`/`[repo]`/`[judgment]` prefixed. Budget: web-research (no harness token accounting
  for subagents); each bounded to ~a dozen primary sources, no code writes.
- **Width justification (D010):** EXPLORATORY — scanning a whole field (dependency modeling + KG
  inference + provenance + change-impact + agile boards), no implementation target yet → scale to 4-5
  perspectives; nominal-group diversity pays here (Diehl & Stroebe 1987). Not the FOCUSED 1-2 (this is
  the opposite of a single defined feature). 4 workers, one perspective-cluster each (below).
- **Phase 3 Develop (post-commit):** 1 divergence wave, 5 ideators, **NVIDIA** (openai-compat, cheap
  fan-out), independent generation. Budget per `research-divergence` profile; 60%-budget gate honored.
- **Phase 4 Refine (post-commit):** 1 critique wave, 4 critics by role (validity / architecture-fit /
  cost / security-privacy), **Sonnet 5 high**, `--seed` from Wave-1 (convergence-only). Cross-vendor
  is per-WAVE (generator NVIDIA != evaluator Sonnet) — satisfies "separate generation from critique".

## Declared design (L18 — this round feeds experiments)

Measurable claims this round will produce (named methods from `docs/EXPERIMENT_METHODS.md`):
- **Edge-inference precision** (LLM-inferred dependency edges vs a classic baseline, e.g. shared-file /
  shared-symbol / co-citation): **measure-before-control** — build a measure-ONLY probe that emits
  candidate edges + a human/oracle-graded precision/recall on a frozen backlog slice, BEFORE any
  auto-linking acts; **noise-floor** calibration (what precision does a trivial keyword-overlap baseline
  already give?) so we never credit the LLM for the floor.
- **Vendor comparison** (NVIDIA vs Sonnet edge inference, if pursued): **matched-budget** + split-plot.
- Any auto-promotion of an edge into canonical state: **evidence grades + confidence sequences**
  (an edge is proposed advisory-first; promotion needs accumulated evidence, like the groom audit gate).

## Phase 0 prep — prior art in-repo (avoid re-derivation)

`[repo]` grounding read this round (native tools, gate-safe):
- `[repo] .harness/prompts/backlog-groom-playbook.md` — current groom: Mine (Sonnet miners/corpus) →
  Audit (H/M claims verified; live-behavior 75% precision) → Triage (intake) → Consolidate (SPEC-116).
  Finds ESCAPED requirements; **no dependency mapping** — serialization is decided by hand in plans.
- `[repo] specs/40-features/panel-tasks-board.md` — derived read-only kanban over
  `docs/IMPLEMENTATION_BACKLOG.md` + `.harness/state/tasks.json` + escalations + live workers; lanes
  backlog/running/review/done, categories feature/bug/ideation/chore. **No edges** (flat rows).
- `[repo] .harness/prompts/research-playbook.md` Phase 5 — a traceability matrix
  (Evidência→Problema→Ideia→Experimento→ADR→Spec→Task→Status) + idea GENEALOGY in divergence waves.
  Provenance already exists per-round but is NOT a queryable cross-round graph.
- `[repo]` experiment registry (`experiment add` EXP-N, method advisory) + intake queue
  (`intake add/decide`, SPEC-116 door provenance) — the other two boards; today unlinked to the backlog.
- `[repo]` Graphify code-AST graph (`graphify-out/GRAPH_REPORT.md`) — we ALREADY build a code
  dependency graph; the question is a graph over WORK ITEMS, and whether the two can share machinery.

The gap = a unified **work-item dependency + provenance graph** with AI-assisted edge inference,
ripple/change-impact detection, and a board that renders it — reusing the derived-not-stored idiom.

## Phase 1 discovery perspectives (the 4 workers)

1. **Classic dependency modeling & scheduling** — DSM (Design Structure Matrix) + clustering/partitioning,
   PERT/CPM critical path, requirement traceability matrices, issue-tracker link taxonomies
   (Jira blocks/relates/duplicates), topological sort for sequencing, change-impact analysis in SE.
2. **AI / LLM dependency + knowledge-graph inference** — LLM relation/edge extraction from issue &
   plan text, GraphRAG / knowledge-graph construction, embedding similarity + clustering for candidate
   links, automatic issue-linking, entity-relation extraction, dedup (we have `semantic-finding-dedup`).
3. **Provenance, idea genealogy & efficient retrieval** — W3C PROV / lineage models, citation &
   idea-genealogy graphs in innovation mgmt, provenance-aware retrieval, how a provenance graph makes
   the NEXT groom/research cheaper (retrieval over the graph vs re-mining), memory/context reuse.
4. **Agile frameworks + board/kanban design + ripple** — SAFe program board / dependency boards,
   Scrum-of-Scrums dependency management, Kanban dependency visualization + WIP, change-driven
   re-planning triggers, connecting a research/experiment board to a delivery board, and the UX of
   showing edges + provenance + "these plans need revision" without card-soup.

## Phase 1 — evidence synthesis (4 Sonnet 5 workers, WebSearch, 2026-07-19)

Curated cross-worker matrix (the load-bearing claims; each `[web]` primary-sourced unless marked
`[judgment]`). Full per-worker tables are in the worker transcripts; this is the deduped register.

| # | Claim (synthesized) | Source (primary) | year | confidence | maturity |
|---|---|---|---|---|---|
| E1 | DAG + Kahn topological sort = the cheapest dependency baseline: adjacency list from literal "blocks:/depends-on:" mentions → indegree queue → execution order + hard cycle detection | Kahn, CACM 5(11) | 1962 | forte | produção |
| E2 | CPM forward/backward pass gives per-item slack; zero-slack items = the ripple-risk set to flag; PERT is provably biased (underestimates duration) — don't build naive CPM/PERT math | Kelley&Walker 1959; MacCrimmon&Ryavec, Op.Res. 12 (1964) | 1959/64 | forte | produção |
| E3 | Issue-trackers converge on a small typed-edge ontology: blocks / is-blocked-by / relates-to / duplicates / clones / parent-child / causes. GitLab's minimal 3 (relates/blocks/is-blocked-by) is the cheapest bucket; GitHub GA'd blocked-by/blocking Aug 2025 | Atlassian, GitLab, MS Learn, GitHub changelog | 2025-26 | forte | produção |
| E4 | DSM partition→tear→sequence handles CYCLIC backlogs (real backlogs have cycles) where Kahn halts; tear the lowest-cost cycle edge | Steward 1981; Eppinger&Browning 2012 | 1981/2012 | forte | validado |
| E5 | Cheapest AI edge pipeline: embeddings+clustering (candidate gen, SemDeDup-style) → LLM-as-judge structured output {edge-type}+confidence → ontology-constrained (not free-form) → independent 2nd-pass "Grounder" audit | SemDeDup arXiv:2303.09540; ODKE+ arXiv:2509.04696; KGGen 2502.09956 | 2023-25 | forte→moderada | produção→protótipo |
| E6 | LLMs OVER-predict relations without textual cues → PRECISION problem (not recall); "Relate" becomes a dumping-ground; typed-link confusion is unsolved | survey arXiv:2311.07914; MSR'22 2204.12893; RE'22 2206.07182 | 2022-23 | forte | validado |
| E7 | LLMs cannot intrinsically self-correct → the audit MUST be an independent judge / evidence-check / human, never the same call re-checking itself | Huang et al., ICLR 2024, arXiv:2310.01798 | 2024 | forte | validado |
| E8 | No backlog-specific benchmark exists (CUPID 0.59-0.67 R@10, BERT typed-link 0.64 macro-F1, ODKE+ 98.8% prec — all OTHER domains) → any confidence score is unvalidated for us until we build a labeled set from our own audited history | CUPID 2308.10022; RE'22 2206.07182; ODKE+ 2509.04696 | 2022-25 | forte | — |
| E9 | Our traceability matrix is ALREADY PROV-shaped (Evidence=Entity, round=Activity, decision=Agent). Formalize a MINIMAL backbone (bound traversal to declared connectors) — full PROV-O over-models: the graph grows "multiple times bigger than the data" | W3C PROV-DM/O 2013; Wittner et al., Sci.Data (2022) | 2013/22 | forte | produção/validado |
| E10 | CHIMERA-style idea-genealogy edges (descends-from / recombined-from between Ideas) prevent re-proposing dead branches — "the single biggest retrieval win for a grooming round" | Sternlicht&Hope, arXiv:2505.20779 | 2025 | moderada | protótipo |
| E11 | GraphRAG community-summaries speed retrieval BUT eager summarization is token-expensive (~40k vs ~900 tokens flat RAG) → use LazyGraphRAG (deferred, query-time) or the graph costs more than the rework it saves | Edge et al. (MS) 2024; "When to use Graphs in RAG" 2506.05690; LazyGraphRAG 2024-25 | 2024-25 | forte/moderada | produção/protótipo |
| E12 | Never render the raw graph: compute a task-specific DERIVED subgraph on demand ("what does X touch downstream") + discard; typed edges as inline card flags; escalate to a graph only on demand. Every de-hairball technique is lossy by design | Cambridge Intelligence; Schulz&Hurter IEEE VIS 2013; Linear/GitHub badges | 2013-25 | forte | validado/produção |
| E13 | Conflict-COLOR is the ripple notification: Jira Advanced Roadmaps turns a dependency line red on a date conflict — repurpose "date conflict" → "a new finding invalidates a plan's premise". One color on an existing edge = "this plan needs revision", no separate screen | Atlassian Advanced Roadmaps docs | 2025 | forte→conceitual | produção (sched)/conceitual (our repurpose) |
| E14 | Automated trace-link recovery (embedding similarity, T-SimCSE) as a periodic maintenance backstop keeps the graph from rotting — RTM staleness ("a stale matrix is worse than none") is the #1 documented failure of hand-maintained link tables | T-SimCSE arXiv:2603.11800; IEEE 830; RTM literature | 2026/1998 | moderada/forte | protótipo/produção |
| E15 | **The UNIVERSAL gap (all 4 workers converge):** no surveyed tool/technique has a maintained, verified answer to "does this edge STILL reflect reality." Lineage/governance initiatives are widely abandoned (~18% adoption). Staleness is THE open problem | TDWI survey (relato); SAFe retro; Wittner 2022; RTM lit | 2022-26 | forte (as a gap) | — |

**The convergent picture.** The technique shape is settled and CHEAP-FIRST (E5); the classic noise floor
is concrete (E1-E4); the viz answer is derived-not-rendered (E12) with conflict-color ripple (E13); the
provenance model is a bounded PROV backbone we're 80% to already (E9) plus idea-genealogy (E10). The one
thing NObody solves is STALENESS (E15) — and it is exactly what our house idioms already answer:
**derive fresh each pass (never a stored, decaying artifact) + measure-honesty (an edge is a CLAIM with
confidence+source, audited like a groom miner, never asserted as truth) + cheap-first (Gemini/NVIDIA
before frontier).** That is the round's central thesis and the wedge that makes this OURS, not a
me-too dependency board.

## Phase 2 — Define (problem framing + briefs) · HUMAN GATE

**Jobs-to-be-done (the problems, not a tech):**
- **J1 (sequence):** "When I pick what to build next, tell me what it blocks / is blocked by, and what
  ripples — without me re-reading every plan." Today: prose-only ("prioriza RD-TAINT por causa das
  dependências"; "serializar T-HASHCHAIN→T-CAUSALPARENT"), decided by hand.
- **J2 (ripple):** "When something NEW lands (an idea, a finding, a shipped change), tell me which
  existing plans need revision and which items now depend on it." Today: the overseer notices manually
  (e.g. this session's doc↔§7 divergence surfacing).
- **J3 (don't repeat):** "Don't let me re-propose an idea whose lineage was already killed." Today: no
  genealogy of dead branches.
- **J4 (retrieve cheaper):** "Make the next groom/research round retrieve over what we already learned
  instead of re-mining raw history." Today: each round re-mines from scratch; provenance is per-round.

**Briefs (each → success criteria + actors + constraints). Set-based: keep the SET alive to critique.**

- **Brief A — Auto-inferred dependency edges, MEASURE-FIRST (serves J1).**
  *Success:* a measure-ONLY probe emits candidate typed edges (E3 taxonomy) with confidence+source over a
  FROZEN backlog slice, graded precision/recall against the Kahn/keyword noise floor (E1) BEFORE any
  auto-linking acts. *Actors:* groom orchestrator (proposes), overseer (audits+uses), the measure harness.
  *Constraints:* cheap-first pipeline (E5); edges are CLAIMS (measure-honesty); independent audit not
  self-correct (E7); must BEAT the classic floor (E1) net of the noise floor; no fabricated edge.

- **Brief B — Unified provenance+dependency GRAPH, derived + PROV-backbone (serves J1+J3+J4).**
  *Success:* a DERIVED-not-stored graph over existing signals (backlog rows, `tasks.json`, experiments,
  intake, per-round traceability matrices, DECISIONS, commits) with a minimal PROV backbone (E9) + ADR
  decision nodes + CHIMERA idea-genealogy edges (E10); queryable ("what evidence led to Task X", "what
  killed lineage does this idea belong to"); REGENERATED fresh each pass (E15 answer). *Actors:* groom
  orchestrator, overseer, a research round, the kanban. *Constraints:* derived-not-duplicated (reuse the
  tasks-board idiom); bounded backbone, don't over-model (E9/Wittner); no 2nd write path; git as history.

- **Brief C — Ripple → plan-revision flags, conflict-color, no hairball (serves J2).**
  *Success:* when a new item lands, traverse the graph to flag downstream plans needing revision, surfaced
  as a conflict-color edge / inline card flag (E12/E13) with the provenance of WHY — no separate ripple
  screen, no raw-graph render. *Actors:* overseer, owner, the board. *Constraints:* on-demand derived
  subgraph (E12); a flagged ripple is a CLAIM; reuse existing visual language (SIGNAL tokens, status pills).

- **Brief D — Retrieval over the graph, LAZY (serves J4).**
  *Success:* the next groom/research round retrieves over lazy (query-time) community summaries of the
  provenance graph instead of re-mining raw history; MEASURED token/time saving vs re-mining. *Actors:*
  groom/research orchestrator. *Constraints:* LazyGraphRAG only — eager summarization costs more than it
  saves (E11); summaries are non-authoritative entry points (like `GRAPH_REPORT.md`); cheap-first.

*Staging:* A and B are independent starting points; C depends on A+B (needs edges + graph); D depends on B.
*Human gate:* the owner authorized the full round → plans; proceeding to Develop, briefs surfaced here for
redirect. Develop runs on **NVIDIA** (divergence), Refine on **Sonnet 5** (critique, seeded) — cross-vendor
per wave so the generator is never its own critic.

## Phases 3-5 — Develop / Refine / Deliver (channelled 2026-07-19)

**Divergence (balanced cross-vendor, both vendors IDEATED).** Sonnet 5 — 6 lenses, ~31 cards (via
`model:sonnet` subagents; the workflow's `claude`/"plan" leg maps to **Fable**, so subagents are the
reliable Sonnet-5 path — see the executor note below). NVIDIA — 5 lenses, ~22 cards
(`nvidia-compat` workflow WF-20260719-152134-492945, all 5 workers `done`, real grounded content).
**No Fable credits spent:** nothing ran on the `claude` executor; the planned Sonnet-workflow WF was
cancelled before any run. **Executor guard rule (operant):** a `research-divergence`/"plan"-profile
`workflow run` WITHOUT `--executor` (or `--executor claude`) burns Fable xhigh — these waves run ONLY
on `--executor nvidia-compat` or via `model:sonnet` subagents.

**Convergence + Deliver.** Both vendors independently landed the SAME backbone (heterogeneous
generators converging = the strongest signal). Portfolio + detailed staged plans (P0-P5 + frontier
bets F1-F3) live in **`docs/research/backlog-dependency-graph-implementation-plans.md`** — the round's
deliverable. Experiments EXP-BDG-1 (edge-inference precision vs the Kahn/keyword noise floor) and
EXP-BDG-2 (incremental-derive correctness) registered in the experiment registry. Decisions in
`.harness/context/DECISIONS.md`. Each plan routes through SPEC-116 intake when it is picked up to build
(the plans are backlog, not yet approved builds).

## Traceability matrix

Filled in the plans doc (`backlog-dependency-graph-implementation-plans.md` §"Traceability matrix"):
`Evidência → Problema → Ideia → Experimento/ADR → Plano → Status`.
