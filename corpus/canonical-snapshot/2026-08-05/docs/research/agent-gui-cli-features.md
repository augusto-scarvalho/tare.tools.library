# Research round — GUI/CLI feature gaps vs peer agent tools + node-based flow composer

Round opened 2026-07-11 by the `research` skill (SPEC-119). Orchestrator: overseer
session. Scope set by the owner: compare our harness GUI/CLI against Claude Code,
Codex, Hermes, OpenClaw and other tools; mandatory deep-dive on a Blender-nodes-style
flow-composition GUI (user picks workers/roles, prompts, tools, and how workers
connect). 1 divergence + 1 critique wave on the claude executor (Max window); waves
held until the in-flight implementer releases `executors.json`.

## Phase 0 — Question, criteria, budget

**Question.** Which GUI/CLI capabilities do peer agent tools ship that our
supervision panel + `harness.py` CLI lack and should adopt — and how should a
node-based flow composer (Blender-nodes UX) let users visually assemble worker
graphs (roles, prompts, tools, connections) under our constraints?

**Constraints (fixed design premises).** stdlib-only runtime; no resident daemon;
GUI never writes state — every action is an allowlisted `harness.py` subcommand;
CLI-first (a panel feature must exist as a command first); no external hosts in the
panel (vendored single-file MIT lib = decision point, not automatic).

**Success criteria.**
- Feature-gap matrix: ours vs ≥5 peers, each gap classified adopt/adapt/reject with
  reasoning under the constraints.
- Node-composer concept concrete enough to spec: node/edge vocabulary mapped to the
  EXISTING compile target (workflow-profiles.json profiles + branch objects
  `{title, taskProfile, workerRole}` + executors + awaitPolicy), compile→validate
  via `workflow plan`, never direct state writes.
- Counter-evidence considered (when node UIs fail: spaghetti graphs, drift from the
  text source of truth).
- ≥2 actionable outcomes (tasks/specs).

**Declared budget.** Waves: divergence 5 workers + critique 4 (claude, Max window,
post-diet template −41%/turn); ≤ the research-profile tokenBudgets; no wave 3.

**Internal baseline** (flow B): `docs/SUPERVISION_UI_IDEATION.md` (2026-07-09 survey:
OpenRig tmux-attach, OpenHarness per-action approvals, Vibe Kanban board, claude-squad
list+diff+attach, Conductor checkpoints, OpenClaw chat-control, Hive intervention
nodes + budgets); SPEC-114 v1-v7 (our panel: dashboard cards, escalations, records,
metrics, chat bridge, routing config, worker drill-in + last-activity); SPEC-118 v1-v4
(live tail, stream-json activity); CLI surface: status/workflow*/tail/escalations/
records/discover/agents/models/routing. The compile target for a flow composer
ALREADY exists: fork-join branch objects with explicit roles (SPEC-119 R11) +
per-profile policies — a canvas only needs to emit that JSON.

## Phase 1 — Evidence matrix (flow A, verified 2026-07-11)

| claim | source | type | year | limitations | confidence | maturity |
|---|---|---|---|---|---|---|
| Claude Code ships Agent Teams (experimental): lead session coordinates teammates with own contexts, inter-agent messaging; user watches and steers | [Agent Teams docs](https://code.claude.com/docs/en/agent-teams) | docs | 2026 | experimental, off by default | forte | adoção inicial |
| Claude Code is multi-surface: CLI, VS Code/JetBrains, desktop, web, SDK, GitHub Action | [features ref](https://hidekazu-konishi.com/entry/claude_code_features_settings_reference_2026.html) | docs/blog | 2026 | — | forte | produção |
| Codex app manages multiple agents in parallel with built-in worktrees; cloud tasks run fire-and-forget on managed infra and open PRs | [OpenAI Codex app](https://openai.com/index/introducing-the-codex-app/), [Codex cloud](https://developers.openai.com/codex/cloud) | vendor docs | 2026 | vendor-managed infra | forte | produção |
| Hermes ships a SQLite-backed kanban board (drag-drop, run history, worker logs, live WebSocket updates) + mission-control dashboard | [Hermes multi-agent](https://hermes-agent.ai/features/multi-agent), [mission control](https://asadtinkers.com/guides/hermes-agentos-mission-control-dashboard/) | docs/guide | 2026 | resident daemon + DB | moderada | produção |
| OpenClaw Gateway serves a Control UI (Overview/Agents/Channels/Logs + exec approvals) and WebChat over WebSocket RPC | [Control UI docs](https://docs.openclaw.ai/web/control-ui), [Dashboard](https://docs.openclaw.ai/web/dashboard) | docs | 2026 | always-on gateway | forte | produção |
| Rivet: developer-first visual graph IDE for agents — prompt nodes, LLM calls, conditionals, loops, subgraph references; executes via SDK | [Rivet (Ironclad)](https://rivet.ironcladapp.com/) via [survey](https://www.vellum.ai/blog/top-ai-agent-frameworks-for-developers) | repo/survey | 2023-26 | TS ecosystem | moderada | produção |
| Langflow pattern: visual canvas that COMPILES to production code (not a runtime of its own) | [survey](https://www.aiagentshub.net/blog/dify-vs-flowise-vs-wordware-vs-lindy) | survey | 2026 | LangChain-coupled | moderada | produção |
| Flowise/Dify/n8n: drag-drop LLM app builders; breadth over depth; agent node at the center of service automations | [Flowise](https://flowiseai.com/), surveys above | docs/survey | 2026 | own runtimes (second brain) | moderada | produção |
| litegraph.js: dependency-free JS node engine + Canvas2D editor (Blueprints/PD-style), exports graphs as JSON; the engine ComfyUI forked for its UI | [litegraph.js](https://github.com/jagenjo/litegraph.js/), [ComfyUI fork note](https://github.com/Comfy-Org/litegraph.js/) | repo | 2015-26 | Canvas2D; upstream low-activity (ComfyUI fork active) | forte | produção |
| ComfyUI proved Blender-style node UX works for non-programmer composition of complex pipelines at scale | ComfyUI frontend monorepo (fork note above) | repo | 2023-26 | image-gen domain | forte | produção |

## Phase 2 — Briefs and gate

**Brief 1 — feature gaps.** How might we close the highest-value supervision and
orchestration gaps between our panel/CLI and the peers (agent-teams-style
inter-worker visibility, fire-and-forget long tasks, board-style at-a-glance state,
inline exec approvals, multi-surface reach) for the solo human supervisor, under
stdlib/no-daemon/CLI-first — without adopting the peers' resident-process
architectures? Success: each gap → adopt/adapt/reject with a named integration point.

**Brief 2 — node-based flow composer (the owner's deep-dive).** How might a user
visually compose a worker flow — choose workers/roles, edit their prompts, pick
tools/executors, and wire how workers connect (fan-out branches, reduce, seeded
next waves) — in a Blender-nodes canvas that COMPILES to the existing
`workflow-profiles.json` + branch-object vocabulary and validates via `workflow plan`
(GUI writes no state; the profile JSON stays the single source of truth, canvas is a
view/editor of it)? Decision point for critics: vendored litegraph.js (MIT, one file,
CSP-compatible) vs hand-rolled SVG mini-editor vs no canvas (structured forms).
Success: node/edge vocabulary + compile/roundtrip contract + drift story
(text-edited profiles must still render).

**Gate.** Scope, waves and budget pre-approved by the owner in the /research
invocation (this round). Recorded per playbook Phase 2.

## Phase 3 — Wave 1 (divergence) — done

`WF-20260712-004425-895025`, 5 ideators on the post-diet claude template (first
production run of SPEC-118 v4), 4/5 valid (worker-001 breached `summary ≤ 1000`),
20 deduplicated concepts. Calibration lesson: a DUAL-brief round yields 9.8-11.7k-char
results vs the 9000 cap calibrated on single-brief round 1 — frozen WF limit raised
to 12000 (operator action, disclosed; outputs untouched). Third occurrence → profile
amendment.

**Independent convergence:** 3 ideators independently REJECTED vendoring litegraph.js
(workflow graphs are token-bounded to ~12 nodes; the Comfy fork is archived) in favor
of renderer-first SVG + forms; 2 independently rejected runtime inter-worker
messaging in favor of plan-time seeded digest edges. Cross-domain transfer: EDA
netlist/schematic (profile JSON = netlist, canvas = view, layout = hash-keyed
sidecar) and ATC flight strips (attention-ordered, not status-ordered).

## Phase 4 — Wave 2 (critique) — done

`WF-20260712-010733-205220`, planned with **`--seed` from the wave-1 reduce** (first
production use of F1: seed digest copied into packets, provenance note, depth 1).
2/4 formally valid (two critics breached `summary ≤ 1000`; their verdicts recovered
from the raw result files and marked auxiliary — the formal reduce used the 2 valid).
All four perspectives converge: every cluster **viável com condições**; no rejection
of the wave-1 rejections.

| Cluster | Verdict (4 critics) | Binding conditions |
|---|---|---|
| K1 composer | viável | anti-litegraph adjudicated CORRECT (source-verified, over-determined); renderer-first read-only SVG is the MVP; `--validate-only` is the one unbuilt piece; compiler-as-trust-boundary = existing allowlist model; netlist = the workflow artifact set |
| K2 board + doctor | viável / doctor experimento (cost critic) | pull-based, no persistent daemon; doctor is diagnose-only, a thin aggregator that consolidates, never accretes |
| K3 messaging rejection | sound, unanimous | seeded digest edges already shipped (F1); scrubbed-mailbox stays OUT (reopens the write surface; experimento only if audit-priced) |
| K4 flight-strip + alarms | viável | ordering derived at render, never cached; generalizes the panel's criticality-sorted idiom; anchors honestly classed [judgment] |
| K5 approvals + recovery | viável | approval-as-record is the shipped ACTIONS pattern generalized; scrub/`--force` stay CLI-only |
| K6 prompts + budget badges | condicionado | compose-time secret-scan has NO call site today (scanner fires at collect only); badges must render the existing token-audit, never recompute; committed prompt templates = second prompt source vs the generator (experimento) |

**Meta-finding on our own machinery** (validity critic): the deterministic reducer
silently dropped the active-vs-archived litegraph fork CONFLICT between two workers —
a live instance of the known F3 design limit (dedupe merges same-title findings,
conflicts only tracked on recommendation divergence). Recorded for the reduce backlog.

## Phase 5 — Portfolio & traceability

**Núcleo:**
- N1 `workflow plan --validate-only` (zero-materialization compile loop) — prerequisite
  of everything below; the one unbuilt cost-saver. Integration: `plan_workflow` seam.
  **Shipped 2026-07-11** (TASK-004 N1): shared `_compile_workflow_plan` core (real path
  materializes, validate path writes nothing) + compile-time `secret_scan` on candidate
  content + budget-breach-as-compile-error; SPEC-119 v6 rules 28-30; acceptance
  `testing/scenarios/wv_validate_only.py`.
- N2 Renderer-first flow composer: read-only SVG DAG of profiles/workflows in the
  panel (derived layout, no layout state), netlist mental model; editing via
  structured FORMS over branch objects; "Compile" button = `plan --validate-only`;
  apply = separate gated action. GUI writes nothing (compiler is the trust boundary).
- N3 Flight-strip attention ordering + alarm rationalization (every signal names an
  operator action) in the panel; ordering derived at render.
- N4 Recovery console + approval-as-record generalization (panel ACTIONS +
  pre-registered escalation IDs; force variants CLI-only).

**Experimentos:** E5 fire-and-forget durable board + `workflow doctor` (diagnose-only);
E6 budget badges rendering token-audit output; E7 compose-time secret-scan call site.

**Estacionadas:** editable node canvas (only after measured friction with N2);
committed prompt templates (second-source conflict unresolved); scrubbed mailbox.

**Rejeitadas (com gatilho):** litegraph.js vendoring (trigger: real workflow graphs
exceeding ~12 nodes or measured N2 editing friction); runtime inter-worker messaging
(trigger: a use case seeded edges provably cannot express).

### Traceability matrix

| Evidência | Problema | Ideia/Decisão | Artefato | Status |
|---|---|---|---|---|
| Agent Teams docs (matriz Fase 1) | visibilidade inter-worker | K3: rejeitar runtime msg, adaptar como seed edges (F1 já entregue) | SPEC-119 v4 `--seed` | núcleo (shipped) |
| Codex cloud tasks | tarefas fire-and-forget | K2 board pull-based + doctor | draft tasks | experimento |
| Hermes kanban / OpenClaw Control UI | board + approvals | K4 flight-strips + K5 approval-as-record | draft tasks | núcleo |
| litegraph/ComfyUI + fork arquivado | canvas Blender-nodes | K1 renderer-first SVG + forms; litegraph rejeitado | draft tasks + futura spec do composer | núcleo |
| Rivet/Langflow "compila para código" | canvas como view | netlist model + plan/apply split + `--validate-only` | draft tasks | núcleo |
| 2 críticos estourando summary ≤1000 (2ª rodada seguida) | disciplina de contrato | ênfase do limite no packet/digest | friction log | registrado |
| reducer descartou conflito fork ativo-vs-arquivado | perda de informação no dedupe | F3 design-limit confirmado ao vivo | backlog reduce | registrado |

**Round cost:** 2 waves (9 workers, post-diet template), seeded critique via F1;
within budget.
