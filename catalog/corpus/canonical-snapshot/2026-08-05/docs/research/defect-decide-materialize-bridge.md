# Research round — bridging `intake decide` → materialization

Slug: `defect-decide-materialize-bridge` · opened 2026-08-01 · orchestrator: overseer (opus-4-8 fallback)

## Question

The defect/intake pipeline is automatic from `audit → defect ingest → sink + intake-pending`
up to `intake decide`. But `decide` (`intake_queue.py:97-111`) is **only a status flip**:
it stamps `status`/`decidedAt`/`note` and writes the queue. Nothing downstream is created:

- `decide backlog` → no `tasks_store` row
- `decide spec` → no spec file / no SPEC-116 intake
- `decide experiment` → no `experiment add` / registry row
- and there is **no enforcement** that a `decide spec` is ever followed by a real spec.

Acting on a decided defect is 100% human (via `backlog-groom`). The decided entry then ages
out of the bounded queue (`cost_metrics.py:603` trims oldest DECIDED first), read only by
`_approvals` as a by-choice counter.

**HMW:** How (if at all) should the harness bridge a `decide <choice>` to a durable downstream
artifact — or deliberately keep it manual — such that decisions don't rot into "decided but
never acted on" with no trace?

## Success criteria (what a good answer must satisfy)

Actors: overseer (runs `decide`), backlog-groom human, workers (would consume any created row),
`doctor` (staleness nag), `_approvals` metric.

Constraints (hard):
- No hand-written markdown ledgers (SPEC-112); canonical state is the registry/store, not a doc.
- Materialization must be **gate-hold-safe** — like `ingest`, refuse/defer when `.harness` is held.
- **Idempotent** — re-deciding or a rerun must not spawn duplicate tasks/specs.
- Must not manufacture **orphan/spam artifacts** (an auto-created spec/task nobody vetted is worse
  than the current gap — the intake `ask` is a cluster header, not a spec body).
- Reversible: a wrong `decide` must be recoverable without leaving a dangling downstream row.
- Cheap: this is low-volume triage; no heavy new subsystem for a handful of decisions.

A good answer addresses BOTH gaps: (1) `decide` creates nothing durable downstream;
(2) nothing enforces that a decision is honored. "Deliberately don't bridge" is a valid answer
if it closes gap (2) another way (e.g. make the un-acted decision visible/nagged).

## Declared budget & width (Phase 0)

- **Width: 4 ideators** — owner-specified fleet: 2× Anthropic Sonnet 5 + 2× NVIDIA (z-ai/glm-5.2).
  In-between complexity: single theme but a real option space incl. "don't bridge". Vendor
  heterogeneity is deliberate (independent generation across two providers — Diversity Collapse
  arXiv:2604.18005; MAD-heterogeneity arXiv:2502.08788). One run = one executor, so the fleet is
  split into two divergence workflows (2+2), reduced together by the orchestrator.
- **Budget:** `research-divergence` profile, `maxTotalPlannedTokens ≤ 32000` per workflow (× 2 waves).
  1 divergence pass per vendor; a critique wave only on strong signal + headroom (60% budget gate).
- **Perspectives (4 of the 5 canonical; dropped performance/escala — low-volume triage):**
  - sonnet · `ideator-simplicity` — fewest moving parts; maybe the answer is *don't* create rows.
  - sonnet · `ideator-reliability` — partial-failure/gate-hold/idempotency/orphan-row operation.
  - nvidia · `ideator-analogy` — transfer a proven triage→work-item mechanism (issue trackers,
    SARIF/code-scanning, linter autofix queues) from another field.
  - nvidia · `ideator-trust-boundary` — the enforcement gap: force a decision to yield an artifact
    without auto-spamming canonical state; trust of materializing from a defect capsule.
- **Experiment design (if this feeds an EXP):** candidate card = default-promotion / evidence-grades
  (does auto-materialization reduce "decided-but-un-acted" rot without raising orphan-artifact rate?).
  Named now per L18; registered only if a card lands in the `experimentos` bucket.

## Genealogy / results

Two divergence waves, blocking `workflow run` + manual collect; orchestrator-reduced (I folded
the 4 results directly instead of 2× `reduce --agent` — saves 2 reducer spawns; the cross-worker
synthesis is the orchestrator's job anyway). 12 concept cards, 4 lenses, 3 distinct models
(sonnet ×2 lenses, glm-5.2 ×2 lenses). All `done`, 0 failed.

### The 12 cards → one ladder (least-bridge → most-bridge)

The cards collapse onto a single spectrum from "don't materialize, just make intent visible" to
"fully auto-create the downstream row":

- **Rung 0 — gate-hold correctness (prerequisite, not a bridge).**
  `R1 gate-hold-guard-decide` [sonnet/reliability]: `decide()` today has NO gate-hold guard —
  unlike `ingest_review_defects`, it will mutate `.harness` under a live hold. Latent bug the
  round surfaced. Do regardless of any bridge decision.
- **Rung 1 — durable intent, zero new state.**
  `S1 note-is-the-trace` [sonnet]: make `--note` mandatory on `decide spec|backlog|experiment`;
  the existing `note` field IS the trace (3-line guard). `S2 decided-list-surface` [sonnet]:
  `intake list --decided` read-only view of `decidedAt`+`note` (already durable, never surfaced).
- **Rung 2 — nag the un-acted decision (closes gap 2 without touching gap 1).**
  Independent convergence: `R3 doctor-decided-unactioned` [sonnet] ≈ `S3 decided-noteless` [sonnet]
  ≈ `T1 deferred-intent + doctor intent-staleness` [nvidia] — a `doctor` WARN mirroring the
  just-shipped `defect_ledger_health` shape. `A3`/`T2` [nvidia] are the Stop-hook variant
  (enforce decide→materialize at workflow-run end).
- **Rung 3 — orphan-safe partial bridge (nvidia's signature move).**
  `A2 pending-spec row` / `T3 decide spec --materialize → DRAFT row` [nvidia]: create a DRAFT /
  `pending-spec` `tasks_store` row (title+evidenceRefs from the cluster), NEVER a spec file. The
  trust-graded boundary: "the capsule's evidence is trusted enough to seed a title, not to write
  a spec body." `A1`/`T4` [nvidia] add a receipt/reconciliation row that flips `intentFulfilled`
  when a real artifact later appears.
- **Rung 4 — full auto-materialize (most power, most risk).**
  `R4 materialize-on-decide-idempotent` [sonnet]: `decide spec|backlog` → `tasks add`,
  `decide experiment` → `experiment add`, store `materializedRef` back on the entry for dedupe.
  `R2 decide-toctou-history` [sonnet]: append-only `history[]` + optional `expected_status`
  guard (mirrors `decision_inbox --expected-digest`) so a racing second decide fails loud.
  (`tasks add` / `experiment add` are confirmed real verbs — `experiment_registry.py:446` — so
  this is store REUSE, not a new subsystem.)

### Cross-vendor divergence (the point of the mixed fleet)

The two providers did NOT return the same ideas reworded — they explored different axes:

- **What sonnet uniquely brought** (glm-5.2 never reached these): the *correctness* lens — spotted
  the live gate-hold bug (`R1`) and the concurrency/TOCTOU race (`R2`), neither of which nvidia
  flagged (nvidia treated gate-hold-safety as a constraint to satisfy, not a current defect); and
  the *laziest* path — reuse the existing `note` field as the trace (`S1`) instead of any new row.
- **What nvidia uniquely brought** (sonnet never reached these): the *cross-domain analogies* that
  justify a middle path — SARIF suppression-receipts, linter autofix-queues, issue-tracker
  auto-transition; and from them the *trust-graded DRAFT row* (`A2`/`T3`) — materialize a
  placeholder, not a spec — plus the *reconciliation* loop (`T4`, flip `intentFulfilled` later).
  Sonnet's materialize card (`R4`) jumped straight to a full row; nvidia found the orphan-safe
  half-step between "nothing" and "full row."
- **Where they independently CONVERGED** (highest-confidence signal): the `doctor` WARN for
  decided-but-unactioned entries — reached by BOTH vendors, three cards, same "mirror
  `defect_ledger_health`" shape. When two independent providers land on the same cheap mechanism,
  that is the strongest evidence in this round.

Net: sonnet = conservative/minimal + found the bug; nvidia = mechanism-borrowing + found the
orphan-safe middle. Neither fleet alone yields the full ladder — the heterogeneity paid.

### Portfolio (set-based; each card in exactly one bucket)

| Bucket | Cards | Operation |
|---|---|---|
| **núcleo** (do regardless) | `R1` gate-hold guard | mantida — it's a bug fix, not a bridge |
| **núcleo** (cheapest gap-close) | `S1` mandatory `--note`, `S2` `--decided` view, `R3`≈`S3`≈`T1` doctor WARN | combinada — one small PR: durable intent + surface + nag |
| **contingência** (if núcleo's nag proves too weak) | `A2`/`T3` DRAFT `pending-spec` row | mantida — orphan-safe, escalate only on evidence |
| **experimentos** | "does visibility+nag (rungs 1-2) reduce decided-but-unacted rot, or is a DRAFT row (rung 3) needed?" | experimento |
| **aposta-de-fronteira** | `T4` receipt + reconciliation | adiada — nice once rung-3 rows exist |
| **estacionadas** | `A3`/`T2` Stop-hook enforcement | adiada — doctor WARN covers gap 2 more cheaply first |
| **rejeitada (for now)** | `R4` full auto-materialize, `R2` TOCTOU history | rejeitada — over-engineered for low-volume triage until the experiment says otherwise |

### Second diamond — crossed critique (cross-vendor, non-frontier)

Two mirrored critique waves, `research-critique --seed`, critics on a DIFFERENT vendor than the cards
they judged (bipartite crossing; divergent→critic-of-other-vendor, never divergent→divergent):

- **C1 — NVIDIA critics ← sonnet's 7 cards** (glm-5.2/step/nemotron): 2/4 valid (validity missing,
  security partial — the cheap nvidia models were less reliable on the capsule contract). Verdicts were
  coarse but aligned: kept the cheap cards (`S2` --decided, `R1` gate-hold, doctor WARN = *mantida*),
  pushed the expensive ones down (`R4` materialize → *dividida*, `R2` history → *simplificada*,
  `S1` --note → *experimento*).
- **C2' — sonnet critics ← nvidia's 7 cards** (all sonnet, non-frontier): 4/4 valid, and SHARP — it
  found nvidia's cards rest on **false repo premises**:
  - `cost_metrics._approvals` is NOT a store → the receipt cards (`A1`/`T4`/`CC-TB-04`) have nowhere to
    append; the fallback sink would be unredacted + uncapped (security finding).
  - `tasks_store.add_draft(originRef, DRAFT lane)` **does not exist** → the nvidia "orphan-safe DRAFT
    row" middle-path (`A2`/`T3`) assumes an API that isn't there — it is NOT the cheap half-step it looked.
  - blocking Stop-hook (`A3`/`T2`/`CONCEPT-003`) **fights the shipped Stop-hook's fail-open + gate-hold-skip
    contract**.
  - `CC-TB-01`'s premise that decide already runs under a hold check is FALSE — corroborates `R1` and the
    recorded frontier-adjacent gate-hold gap.

**Headline (the payoff of the mixed fleet): asymmetry.** The cheap nvidia ideators generated
plausible-but-ungrounded mechanisms (hallucinated repo facts); it took the stronger sonnet CRITICS to
catch it. Novelty ≠ maturity (playbook principle 2); verifiable-feedback-only (principle 4) is what
separated the grounded cards from the hallucinated ones. The crossing CORRECTED the first-pass synthesis:
nvidia's "signature middle path" was over-credited because its API premise went unverified until C2'.

### Portfolio (REVISED after crossed critique; set-based, each card one bucket)

| Bucket | Cards | Operation |
|---|---|---|
| **núcleo** (do regardless) | `R1` gate-hold guard on `decide()` | mantida — both waves confirm `decide()` LACKS the guard; it's a bug |
| **núcleo** (cheapest gap-close) | `S2` `--decided` view, `R3`≈`T1` doctor WARN decided-unactioned | combinada — read-only + one advisory; both vendors' critics left these standing |
| **contingência** | `S1` mandatory `--note` | experimento — sonnet-cheap, but nvidia critic flags it may break existing automation; gate on that check |
| **rejeitada / heavy-rework** | `A2`/`T3` DRAFT row (nonexistent `add_draft` API), `A1`/`T4`/`CC-TB-04` receipt (`_approvals` not a store) | rejeitada — false repo premise; would need new store API + schema, not the cheap half-step claimed |
| **estacionadas** | `A3`/`T2` blocking Stop-hook | rejeitada — fights the shipped fail-open Stop-hook; doctor WARN covers gap 2 |
| **rejeitada** | `R4` full auto-materialize, `R2` TOCTOU history | rejeitada — over-engineered + unbounded state for low-volume triage |

### Recommendation (ponytail, post-critique)

The crossed critique made the answer LAZIER, not bigger. **núcleo = one small PR**: fix the gate-hold guard
(`R1`, a real bug both waves confirm), add `intake list --decided` (`S2`, read-only), and one `doctor` WARN
for decided-but-unactioned (`R3`/`T1`). That is ~15 lines, no new state, no orphan risk, and it closes the
exact thing that worried the owner — "decided but never acted on, with no trace." `S1` (--note) rides an
experiment (does it break existing automation?). Everything nvidia proposed above that — DRAFT rows,
receipts, blocking hooks — is rejected until its false repo premises are fixed; it is NOT the cheap
half-step it first looked like.

### Spinoff experiment — EXP-37: cheap independent auditor for a "carimbo" (owner idea, 2026-08-01)

Born from decision 4 (a cheap, on-the-fly independent auditor that reviews an intake decision / defect
stamp). Design card: **split-plot** (model snapshot = whole-plot; effort + context-mode = sub-plots) +
**matched-budget controls** (docs/EXPERIMENT_METHODS.md).

- **Question.** At what model TIER + EFFORT do we pin a vendor auditor for the carimbo-audit task, and
  which API-inference (http) models can actually complete it?
- **The load-bearing constraint (owner).** [repo] `.harness/routing/executors.json` — every http executor
  (`nvidia-compat`/GLM-5.2, `gemini-compat`, `local-llama`) is `repoAccess: none`: it cannot read files,
  call tools, or verify a claim against source. Only cli-agent executors (`claude`/`codex`/`kimi`) are
  `repoAccess: repo`. So an http auditor needs the evidence **pre-sliced into its prompt** — a preparation
  step that ~doubles the effort. This is the experiment's independent variable: **self-serving cli-agent
  auditor vs. http-inference auditor + slicing step.**
- **Hypothesis.** A cheap cli-agent auditor with repo access (haiku, low effort) beats http models
  (GLM-5.2/gemini/step-flash + sliced context) on grounding at lower TOTAL effort — because http models
  can't verify and hallucinate, and slicing doubles the work. **Direct prior evidence (this session):** the
  http nvidia critics invented `tasks_store.add_draft` and treated `cost_metrics._approvals` as a store;
  the cli-agent sonnet critics caught it. `[judgment]` H0 alt: some http model on free-tier clears the
  grounding bar cheaply enough ($0) to be worth the slicing.
- **Baseline.** haiku (cli, repo-access) @ low effort — cheapest self-serving auditor.
- **Arms (whole-plot).** cli: haiku, sonnet(ceiling ref). http+sliced: GLM-5.2 (nvidia free-tier),
  gemini-flash (free), nvidia step-flash. **Sub-plots:** effort ∈ {low,med,high}; context ∈ {self-serve, sliced}.
- **Gold set.** a small fixed set of carimbos with KNOWN verdicts: ≥1 with a PLANTED false premise (a fake
  API, like the one C2' caught), ≥1 sound decision, ≥1 real-but-weak evidence.
- **Metrics.** (1) grounding rate = % of auditor claims that hold against source; (2) catch rate on the
  planted false-premise carimbo + false-positive rate on the sound one; (3) TOTAL cost = model tokens×price
  **plus the slicing-step cost** for http arms (free-tier model ≠ free total); (4) effort floor per model;
  (5) latency.
- **Decision criteria.** pick the cheapest (model tier + effort + path) with grounding ≥ threshold and catch
  ≥ threshold at false-positive ≤ threshold on the gold set. **If no http model clears grounding even with
  slicing → decision is "auditors must be cli-agent repo-access cheap models (haiku)", and the
  slicing-doubles-effort path is abandoned** — a clean, decision-useful negative result.

### Traceability

`Evidência(decide:97-111 flip-only + this-session http-hallucination) → Problema(gap1/gap2 + auditor-model-tier)
→ Ideia(ladder rungs 0-4 + cheap-auditor) → Experimento(EXP-37 auditor tiering) → Spec/Task(3 backlog rows: núcleo P1,
frontier-pin P1, research-P0 P2) → Status(routed 2026-08-01)`.
