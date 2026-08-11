# Research round — instruction/playbook inheritance & composition for agent roles

Phase 0 (prep). Owner-commissioned 2026-07-23; vendors PINNED by owner:
NVIDIA (GLM z-ai/glm-5.2 via `nvidia-compat`) + Sonnet medium.

## Question

What should the harness adopt — mechanics, guardrails, and failure modes —
for role-scoped instruction inheritance/composition (SPEC-170: registry,
`extends` chains, tracking, hard spawn enforcement), from how real agent
frameworks, config systems, and policy systems solve the same problem?

## Success criteria

- Survey of >=6 real systems' composition mechanics with primary sources
  (agent-instruction: AGENTS.md standard, Claude Code memory imports,
  Cursor/Windsurf/Cline rules dirs, CrewAI/AutoGen/LangGraph role configs;
  config/policy analogs: Ansible roles, Helm values layering, OPA/Rego,
  OOP mixin lessons) — each claim `source + date + confidence + maturity`.
- Documented failure modes of inheritance in instruction/config systems
  (diamond problem, override ambiguity, drift between layers, context
  bloat) mapped to SPEC-170 doors (mixins, per-target overlays, GUI).
- Portfolio bucketed `núcleo | contingência | aposta | experimentos |
  estacionadas | rejeitadas`; recommendations scored novelty × maturity
  (never collapsed).

## Covered-check (Phase 0)

records search + doc-find run 2026-07-23 (recorded in
`docs/research/playbook-hierarchy-refinement-2026-07-23.md`): no covering
spec; SPEC-170 owns the feature; this round informs W2/GUI + v2 doors.

## Declared budget & width (D010)

- Total round ceiling: **200k tokens**. Lanes: sonnet discovery ~60k; GLM
  divergence wave ~40k (embedded packets, no repo access); critique ~40k;
  orchestrator synthesis ~40k; reserve 20k. Budget gate at 60% before any
  extra wave.
- Width: FOCUSED research (feature defined, SPEC-170 shipped W1) -> **2
  directed lanes per wave** (owner vendor pin; EXP-15: over-fanning focused
  rounds yields redundancy, not coverage).
- Experiment design (L18): N/A — this round feeds spec doors, not a
  measurable threshold change; no EXPERIMENT_METHODS card required.

## Vendor mechanics (pinned, with honest caveats)

- Sonnet lane: Agent-tool `scanner`-class spawn, `model: sonnet` explicit
  (spawn-economy pin). CAVEAT: the Agent tool exposes no per-spawn effort
  knob — "medium" honored where the executor exposes it; deviation noted
  here rather than silently dropped.
- NVIDIA lane: `workflow plan --profile research-divergence` +
  `--executor nvidia-compat` (`tools/openai_worker.py`, one POST per
  worker, `NVIDIA_API_KEY` env-only) — the http family validated by
  `rs_research_skill.py`. Packet workers get EMBEDDED context only (no
  repo access): the packet carries a digest of SPEC-170 + the ratified
  refinement.
- No wave launches while a gate run is in flight (hold-swap guard).

## Phase 2 briefs (owner-adjusted 2026-07-23: crossed 2x2 design)

Owner ruling at the human gate: **mixed crossed waves** — 2 Sonnet ideators
critiqued by 2 NVIDIA critics; 2 NVIDIA ideators critiqued by 2 Sonnet
critics. Generation stays independent (nominal groups); critique is
CROSS-VENDOR only (a vendor never grades its own family — model
heterogeneity is the point, arXiv:2502.08788).

- **Wave 1 — generation (4 independent ideators, distinct perspectives):**
  - S1 (sonnet): simplicity/DX — grounded in the agent-instruction field
    survey (AGENTS.md standard, Claude Code imports, Cursor/Windsurf/Cline
    rules, CrewAI/AutoGen/LangGraph), primary sources, provenance prefixes.
  - S2 (sonnet): reliability/ops + tracking — grounded in config/policy
    analogs (Ansible roles, Helm layering, OPA/Rego, OOP mixin lessons).
  - N1 (GLM, embedded digest, no repo/web): trust-boundary/security
    mechanisms for instruction inheritance.
  - N2 (GLM, embedded digest, no repo/web): cross-domain analogies
    (biology, law, org charts — provocations) for composition/versioning.
- **Wave 2 — critique (crossed):**
  - N-crit x2 (GLM): validity/assumptions + integration-cost lenses over
    S1+S2 outputs (embedded).
  - S-crit x2 (sonnet): validity/references (verify S-claims impossible —
    these grade N1+N2) + architecture-fit lens over N1+N2 outputs.
- Survey deliverable folds into S1/S2 evidence sections (no separate B1
  lane — owner width ruling supersedes the draft).

## Phase 3+4 results (crossed 2x2, all lanes settled 2026-07-23 ~17:00)

Generation: S1 (sonnet, 11 evidence rows + 6 cards), S2 (sonnet, 7 evidence
rows + 6 cards), N1/N2 (GLM via nvidia-compat, 6+6 cards, all honest
`reference: judgment`). Critique crossed: GLM critics graded the 12 Sonnet
cards (validity + integration/ops); Sonnet critics graded the 12 GLM cards
(validity/real-precedent via web + architecture-fit). One packet-contract
retry (GLM critics needed top-level `findings` key — wrapper contract).
Raw worker outputs: session scratchpad `glm-*.json` + agent transcripts;
condensed verdicts below are the orchestrator's synthesis.

### Operations per card (set-based, multi-dimension)

| Card | Op | Ground |
|---|---|---|
| S2-C1 chain lockfile | **mantida (núcleo, W2)** | GLM-A sólida; auto-regen only + LF-normalized hash (CRLF risk named); ABSORBS N1-C1 (approved-manifest value without PKI — single-owner key collapse, S-critA) |
| S2-C2 `--render` origin-annotated | **mantida (núcleo, W2)** | sólida+sim both critics; inspection-only, never spawn input |
| N1-C3 provenance token | **simplificada (núcleo, W2)** | SLSA/in-toto precedent real; S-critB simplification adopted: spawn logs carry {role, chainHash} — no new ledger |
| S1-C6 concatenate-not-override + S2-C5 C3 fail-fast | **mantida (spec amendment, doc-only)** | validated by Claude Code memory docs precedent; v2-mixins door note |
| S2-C3 directive-collision linter | **experimento** | condicional×2: needs suppression syntax + allowlist; measure false-positive rate before gate-wiring |
| S1-C1 paths-glob activation | **adiada** | spawn surfaces don't declare file sets pre-resolution today (GLM-A frágil) |
| S1-C2 `@path` imports | **adiada** | no current playbook needs sub-file granularity; depth/drift risk (GLM-B alto) |
| S2-C6 spawn-prompt drift grep | **adiada (pós-W2)** | only meaningful after hard enforcement covers spawn surfaces |
| N1-C4 per-repo namespaces | **estacionada** | premature for single repo, but the ratified shape for the SPEC-110 per-target overlay v2 door (k8s/npm-scope precedent) |
| N2-C1 specificity precedence | **estacionada (v2 mixins)** | linear chain has no conflict class today; if mixins land, simple order not CSS math (S-critB) |
| N2-C4 RACI | **estacionada** | real precedent (PMI), no consumer; taskTypes fuzzy under SPEC-144 |
| N1-C5 taint scan | **estacionada** | threat model mismatch (self-authored playbooks); relevant only if third-party playbooks ever enter |
| S1-C3 symlink shim | **rejeitada** | Windows-first; both critics; dual-codebase burden |
| S1-C4 per-role enforcement enum | **rejeitada** | contradicts owner Q8 (recorded as the softening path IF hard-refusal bites) |
| S1-C5 adhoc/ auto-include | **rejeitada** | bypasses hash-snapshot/protection model (GLM-A) |
| S2-C4 canary rollout | **rejeitada** | mutable state in an immutable-by-snapshot registry; git branch IS the rollout mechanism |
| N1-C1 signed manifest | **combinada→S2-C1** | see lockfile row |
| N1-C2 trustWeight | **rejeitada** | decorative at 1-owner scale; contradicts binary refusal (rule 2/Q8) |
| N1-C6 SELinux/FUSE fence | **rejeitada** | Windows-incompatible; SPEC-148 ACL is the shipped native equivalent |
| N2-C2 amendment chain | **rejeitada** | contradicts Q6 (git owns history); unresolved same-date conflict semantics |
| N2-C3 X.509 role keys | **rejeitada** | no durable per-role key-holder; PKI cost, zero adversary gain at this scale |
| N2-C5 DNS delegation | **rejeitada** | removal semantics regress the additive inheritance design |
| N2-C6 vendor-staggered revisions | **rejeitada** | Q3 thin shims → one canonical source, nothing to stagger |

### Portfolio

- **núcleo**: S2-C1 (+N1-C1 absorbed), S2-C2, N1-C3-simplified → SPEC-170
  W2 scope; S1-C6/S2-C5 → spec amendment (doc-only).
- **experimentos**: S2-C3 collision linter (hipótese: detecta colisões
  reais com FP<20%; baseline: 0 colisões conhecidas; métricas: FP rate,
  colisões reais achadas; decisão: gate-wire se FP<20% e >=1 catch real).
- **estacionadas**: S1-C1, S1-C2, S2-C6, N1-C4, N2-C1, N2-C4, N1-C5.
- **rejeitadas**: S1-C3, S1-C4, S1-C5, S2-C4, N1-C2, N1-C6, N2-C2, N2-C3,
  N2-C5, N2-C6.
- **contingência**: S1-C4 (per-role enforcement enum) é o plano-B nomeado
  caso o hard-refusal Q8 gere fricção real pré-inventário.

### Traceability

Evidência (S1/S2 tables + critic precedents) → Problema (herança de
instruções SPEC-170) → Ideias (24 cards) → Operações (acima) →
Spec (SPEC-170 amendment W2) → Tasks (intake 2c51bf0af0e3 wave W2) →
Status: síntese entregue; W2 pendente de plan brief.

### Companion article

Consolidated scientific write-up (case study + survey + round + threats to
validity, full citations): `docs/research/playbook-inheritance-article-2026-07-23.md`.

### Budget settle

Sonnet lanes ≈116k tokens (S1 42k, S2 27k, S-critA 25k, S-critB 22k);
GLM/nvidia free-tier (4 calls, 1 contract retry); orchestrator synthesis
inline. Under the 200k declared ceiling; no extra waves taken (budget gate
respected).
