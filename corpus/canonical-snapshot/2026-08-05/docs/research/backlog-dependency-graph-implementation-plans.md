# Backlog dependency + provenance graph — implementation plans

Deliverable of the research round `docs/research/backlog-dependency-graph-round.md` (Double Diamond).
Phase 3 divergence ran **balanced cross-vendor**: Sonnet 5 (6 lenses, ~31 cards, via `model:sonnet`
subagents — the workflow's `claude`/"plan" leg maps to Fable, so subagents are the reliable Sonnet-5
path) + NVIDIA (`nvidia-compat` workflow WF-20260719-152134-492945, 5 lenses, ~22 cards). Phase 4
convergence + Phase 5 plans channelled by the orchestrator (this session). **No Fable credits spent**
(nothing ran on the `claude` executor; the planned Sonnet-workflow WF was cancelled before any run).

## The convergent architecture (near-unanimous across 53 cards, BOTH vendors)

Independent generation, two vendors, eleven lenses — they landed on the SAME backbone. That agreement
is the round's strongest evidence signal (heterogeneous generators converging, not one model's bias):

1. **Cheap-first, measure-gated pipeline.** embeddings + ANN top-k candidate gen (cuts O(n^2)->O(n*k))
   -> LLM-judge typed edge {blocks/depends-on/relates-to/duplicates}+confidence, ontology-constrained
   -> **independent Grounder audit** (never the same call self-checking) -> promote. Gate the whole
   thing on a **measure-only probe** that beats the classic **Kahn/keyword noise floor** FIRST.
2. **Derived-not-stored graph.** Regenerated fresh each pass from existing signals; minimal PROV
   backbone (Entity=item, Activity=round, Agent=decider); full PROV-O over-models. Reuses the
   `tasks_board` derive-fresh idiom + git-as-DAG + `DECISIONS.md` tokens + the traceability matrix.
3. **Edge = CLAIM, never fact.** Every inferred edge carries status (PROPOSED/VERIFIED/REJECTED),
   confidence, source, provenance tag (`[web]`/`[repo]`/`[judgment]`). Downstream (ripple/sequencing/
   retrieval) reads VERIFIED only by default. Promotion needs the independent audit. This is the
   measure-honesty invariant made structural — the schema has no field for "fact".
4. **Ripple = conflict-color inline flags, no hairball.** A new item ripples via bounded-hop BFS;
   affected plans get a conflict-color flag (repurpose Jira red-line -> "premise invalidated");
   the raw graph is NEVER rendered — a task-specific subgraph is derived on demand + discarded.
5. **Lazy retrieval.** LazyGraphRAG deferred (query-time, ~900 vs ~40k tokens); genealogy edges
   (CHIMERA descends-from) are the pre-computed hot path (prevent re-proposing dead branches).
6. **Trust layer (cross-cutting, non-optional given external-API egress).** Redact before egress;
   confine the inference worker; PROPOSED-until-audited promotion gate; tag-laundering guard.
7. **The wedge (why this is OURS): STALENESS is the universal gap no tool solves — answered by
   derive-fresh + edge-as-claim + measure-honesty, all existing house idioms.**

## Portfolio (Phase 5 buckets)

| Bucket | Items |
|---|---|
| **núcleo** (build, staged by dependency) | P0 measure-probe · P1 deps-tags+Kahn floor · P2 derived graph + edge-as-claim · P3 ripple flags · P4 lazy retrieval + genealogy |
| **contingência / cross-cutting** | P5 trust+egress layer (gates any external-API inference; ships WITH P0) |
| **aposta-de-fronteira** (experiment/park, triggered) | F1 Uzzi Z-score novelty confidence · F2 W3C PROV `wasInvalidatedBy` ripple primitive · F3 GNN link-prediction (cold-start — park) |
| **experimentos** (register) | EXP-BDG-1 edge-inference precision vs noise floor (P0) · EXP-BDG-2 incremental-derive correctness (P2/P5-scale) |
| **estacionadas** | raw-graph render UI (C-I4 — riskiest, cut from v1); GraphRAG eager summaries (E11 cost) |
| **rejeitadas** | continuous production LLM edge-inference before the probe clears the floor; a stored/materialized graph artifact (staleness rot) |

---

## P0 — Measure-first edge-inference probe + noise floor  [DO FIRST; gates all AI]

**Goal.** Before ANY auto-linking acts, prove (or disprove) that AI-inferred typed edges beat the
classic floor on OUR backlog — and build the labeled set that makes every later confidence score mean
something (E8: no backlog benchmark exists). Read-only; nothing is written to the backlog.
**Mechanism.** On a FROZEN slice of ~50-200 audited items: (a) classic floor = literal `blocks:/
depends-on:` keyword scan + Kahn topo (E1); (b) candidate gen = embed items once + ANN top-k
(k=10-20) to cut O(n^2)->O(n*k) (P1/PC-1); (c) LLM-judge each candidate pair -> {edge-type,
confidence}, ontology-constrained to E3; (d) independent Grounder audit (evidence-check vs the cited
source span — grep/diff, not another LLM opinion) (E7/R-2/CARD-T3). Grade precision/recall/F1 vs the
floor + repeated-run confidence stability (the LLM's own noise floor, R-1). Classify each miss into a
failure-mode taxonomy (false-block, type-confusion, relates-to dumping — R1/E6).
**Footprint.** New `testing/probes/edge_inference_probe.py` (measure-only, like the existing
`testing/probes/*`); a frozen fixture slice under `testing/probes/fixtures/`; grading in stdlib.
Reuses the `backlog-groom` Mine->Audit split (miner proposes, orchestrator audits) — point one miner
at the "edges" corpus (SIM-5). NO writes to `.harness` or the backlog.
**Experiment.** EXP-BDG-1 (measure-before-control + noise-floor + evidence-grades): hypothesis "LLM-
judge precision beats the keyword/Kahn floor by >X% on the frozen slice"; baseline = the floor;
metric = precision/recall/F1 + confidence stability; decision = auto-linking stays OFF until the delta
clears the floor at a confirmatory evidence grade. Reversal = Kahn-only mode.
**Depends on.** nothing (this is step 0). **Novelty** baixa · **Maturity** conceitual.
**Descends from.** SIM-1/SIM-5, R-1/R-2, PC-1, P1/P4, CARD-005-A (gene-regulatory measure-first),
S1, E1/E5/E6/E7/E8.

## P1 — deps-as-tags + Kahn topo floor in `tasks_board` [classic, cheapest, no AI, ship now]

**Goal.** Make the classic dependency floor real and immediately useful (sequencing + cycle
detection) with zero AI and zero new storage — this IS the noise floor P0 grades against.
**Mechanism.** Parse an inline convention LEGAL in today's free text (no schema migration): `blocks:ID
/ depends-on:ID / relates-to:ID / duplicates:ID` tokens (E3) from the three corpora `tasks_snapshot`
already reads (backlog md, `tasks.json`, `intake-queue.json`). Emit one derived key per row
`deps:{blocks,dependsOn,relatesTo,duplicates}` + a stdlib Kahn function -> topo order + hard-cycle
list, exposed as `tasks list --topo`.
**Footprint.** `scripts/harness_lib/tasks_board.py` (same module, derive-never-store + never-crash-
per-row idiom, ~30 lines); one `cli_registry.register()` verb flag. GUI-writes-no-state preserved.
**Depends on.** nothing. **Novelty** baixa · **Maturity** produção (Kahn 1962 + E3 taxonomy).
**Descends from.** SIM-1, S1, PC-3, P3, E1/E3.

## P2 — Derived provenance+dependency graph + edge-as-claim schema [Brief B]

**Goal.** One derived-fresh graph unifying dependencies (P1) + provenance (where each item came from),
queryable, never a stored decaying artifact.
**Mechanism.** A read-only `deriveGraph(signals)` (git-blame analogy, CARD-005-B): minimal PROV
backbone Entity=item / Activity=round / Agent=session-or-decider, built from signals we ALREADY keep —
`DECISIONS.md` reference tokens (`EXP-N/SPEC-N/D0xx/T-xxx`, co-occurrence = edges, SIM-2), git commit
trailers (session/decision refs — git IS the provenance DAG, XD1/CARD-005-B), the per-round
traceability matrix, `tasks.json`/experiments/intake. Every edge is a CLAIM record: `{type, from, to,
confidence, status:PROPOSED|VERIFIED|REJECTED, source, provenanceTag, inferredBy, lastVerifiedAt}`
(R-3/TB-2). Incremental at scale: content-hash items, dirty-item one-hop recompute + per-pair cache
keyed by (hashA,hashB), whole-pass hash short-circuit (P2/P5-Sonnet, PC-3); a periodic full-recompute-
on-a-sample self-check keeps "derived-fresh" honest (catches removed-edge drift). Expose `harness.py
provenance <token>` -> "what cites this / what this cites" (bounded slice, never the whole graph).
**Footprint.** New `scripts/harness_lib/dep_graph.py` (pure derive, stdlib) + one `cli_registry` verb;
optional: ONLY genealogy edges (descends-from) persisted (E10) if a measured retrieval win justifies
it (else fully derived). No 2nd write path; no new canonical store.
**Experiment.** EXP-BDG-2 (incremental-derive correctness): the dirty-set recompute must equal a full
recompute on a sample (guards the "looks-fresh-but-stale" failure R-2/P2 flags).
**Depends on.** P1 (dependency edges). **Novelty** média · **Maturity** conceitual.
**Descends from.** SIM-2, R-2/R-5, XD1/XD4, CARD-005-B, PC-4, T2, E9/E10/E15.

## P3 — Ripple -> plan-revision flags, conflict-color, no hairball [Brief C]

**Goal.** When a new item lands, flag which plans need revision — legibly, without a graph hairball.
**Mechanism.** Bounded-hop BFS (depth D~3, P3-Sonnet) from the changed item along blocks/depends-on
edges only -> the affected set (compiler-error-cascade analogy: propagate to break-sites, don't render
the graph — CARD-005-C). Surface as ONE new `StatusKind` `needs-revision` (a 12th state, distinct
glyph, tone=danger — reuse the F4 Status pill/rail: color+icon+text, daltonic-safe; this is the design
law's ESCALATE-to-a-primitive path, NOT new CSS — C-I2). The flag inherits the MIN confidence along
the chain (propagate, don't launder — R-5) and shows a truncation notice past depth D ("N more hops",
P3). Escalation to a derived 1-hop subgraph is an explicit action, rendered in a Drawer, discarded on
close (C-I4 — but this render is the RISKIEST card, parked to a later slice; C-I1/C-I3 answer
"what's linked / why" without ever drawing a graph).
**Footprint.** `dep_graph.py` ripple fn + `/api/tasks` (+experiments/research) derived `rippleFlag`
key; F5 Status amendment for the new kind (spec'd, not a silent edit to the frozen primitive — C-I2).
**Depends on.** P1 + P2. **Novelty** média · **Maturity** conceitual.
**Descends from.** SIM-3, R-5, C-I1/C-I2/C-I3, XD2 (dirty-propagation, hard vs soft edges),
CARD-005-C, T5, E12/E13.

## P4 — Lazy retrieval over the graph + genealogy edges [Brief D]

**Goal.** Make the NEXT groom/research round retrieve over what we already learned instead of
re-mining raw history — cheaply.
**Mechanism.** Genealogy edges (CHIMERA descends-from/recombined-from, E10) are the hot path: a query
"what killed lineage does this idea belong to" prunes dead branches before candidate gen. Retrieval is
LazyGraphRAG (deferred query-time summaries, ~900 tokens, E11) — NEVER eager (~40k). Formalize the
Phase-0 "grep DECISIONS/INDEX/prior rounds first" habit into `doc-find` as the mandatory first call of
any groom/research orchestration (SIM-4). A query-planner cost model picks the cheapest traversal
(CARD-005-D). Cache keyed to graph-state hash (fresh, not recomputed when nothing changed; R-4).
**Footprint.** `doc-find` grep-target widening (DECISIONS/INDEX/experiment+intake titles); a lazy
summarize-on-query fn in `dep_graph.py`; staleness stamp + cache-invalidation (R-4).
**Depends on.** P2 (the graph). **Novelty** média · **Maturity** conceitual.
**Descends from.** SIM-4, R-4, XD5, CARD-005-D, PC-2, S4, E10/E11.

## P5 — Trust + egress layer [cross-cutting; ships WITH P0's first external-API call]

**Goal.** Edge inference sends work-item text to an EXTERNAL API (NVIDIA/OpenAI). Keep that trust
boundary honest: nothing sensitive egresses, an inferred edge never silently gains authority.
**Mechanism.** (a) **Egress scope card** (TB-1): before egress, reduce each item to {id, type,
redacted-summary} with secret-shaped tokens masked using the detectors `protect_files` already carries;
allow-list exactly the inference endpoint (sandbox network allow-list, not model good behavior). (b)
**Inference-worker confinement** (TB-4): run the miner as an R1 `sandbox_spawn` (SPEC-148) — isolated
cwd, deny-write on protected paths, endpoint-scoped network, no graph-write path (only a proposal
file the audit consumes). (c) **Promotion gate** (TB-2): edges are PROPOSED until the independent
audit attaches a `[repo]` citation or the owner signs off via the intake queue; revocable to REJECTED.
(d) **Tag-laundering guard** (TB-3): a write-time validator rejects a `[repo]` tag with no resolvable
file+line, or an upgrade of `[web]`/`[judgment]`->`[repo]` without a fresh direct read. (e) verified-
only default retrieval (TB-5).
**Footprint.** reuse `discover` pre-egress + `sandbox_spawn` (SPEC-148) + `protect_files` detectors +
the `[web]/[repo]/[judgment]` convention + intake as the promotion gate. Mostly wiring/config + the
tag-laundering validator (new, small).
**Depends on.** P0 (the first external-API inference). **Novelty** média · **Maturity** protótipo
(sandbox/detectors exist; the wiring is new). **Descends from.** TB-1..5, CARD-T1..T5.

---

## Frontier bets (park with a trigger; do NOT build first)

- **F1 — Uzzi atypical-combination Z-score as the measure-first confidence number** (XD3). Novelty
  ALTA / maturity conceitual. A statistic over a degree-preserving randomized null of the tag-
  cooccurrence graph gives a citable novelty/conventionality number (vs an LLM vibe). **Trigger:** P0
  ships + the backlog/tag vocabulary is large enough for a null model to have power. Goodhart risk if
  ideators learn it's scored.
- **F2 — W3C PROV `wasInvalidatedBy` as the formal ripple primitive** (XD4/CARD-T2). Novelty ALTA /
  maturity conceitual (PROV-DM is produção AS A STANDARD; the transplant is untested). Borrow the
  VOCABULARY onto flat JSON (not RDF machinery). **Trigger:** P2's ad-hoc edge schema starts needing a
  standard invalidation semantics; adopt the vocabulary, not the triple-store.
- **F3 — GNN link-prediction over the backlog graph.** Novelty alta / maturity conceitual — COLD-START
  loser (needs a populated labeled graph to train). **Trigger:** the audited-edge corpus grows large
  enough to be training data; until then LLM few-shot judgment wins.

## Traceability matrix

| Evidência | Problema (JTBD) | Ideia (cards) | Experimento/ADR | Plano | Status |
|---|---|---|---|---|---|
| E1/E5/E6/E7/E8 | J1 sequence | SIM-1/5, R-1/2, PC-1, 005-A, P1/4 | EXP-BDG-1 | P0, P1 | plano |
| E9/E10/E15 | J1/J3/J4 graph+genealogy | SIM-2, R-2/5, XD1/4, 005-B, PC-4 | EXP-BDG-2 | P2, P4 | plano |
| E12/E13 | J2 ripple | SIM-3, R-5, C-I1/2, XD2, 005-C | — | P3 | plano |
| E11 | J4 retrieve cheaper | SIM-4, R-4, XD5, 005-D, PC-2 | — | P4 | plano |
| E6/E7 + egress | trust boundary | TB-1..5, CARD-T1..5 | — | P5 | plano |
| Uzzi/PROV/GNN | frontier | XD3/4, F3 | (park) | F1/F2/F3 | estacionado |

## Sequencing (the dependency chain the owner asked to make explicit)

`P0 (measure) + P1 (classic floor) do-first, independent` -> `P2 (graph) needs P1` -> `P3 (ripple)
needs P1+P2` and `P4 (retrieval) needs P2` -> `P5 (trust) ships WITH P0's first external call`.
Frontier F1/F2/F3 park behind their triggers. Nothing AI auto-links until P0 clears the noise floor.
