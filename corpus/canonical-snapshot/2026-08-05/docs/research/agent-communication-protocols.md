# Research round — efficient communication protocols for agents, systems & tools

Round opened 2026-07-12 by the `research` skill (SPEC-119). Orchestrator: overseer session
(running in parallel with 5 worktree implementers). Primary evidence: the owner's study
(July 2026; 61 refs; protocols MCP/A2A/AG-UI/ACP/NLIP/AGNTCY, coordination architectures,
context-efficiency techniques, latent/KV-cache comm, security, a §12 4-plane architecture
recommended FOR THIS harness + §12.3 15 context invariants + §13 10 metrics) + a verified
baseline of our CURRENT harness + spot-checked external anchors.

## Phase 0 — Question, criteria, budget

**Question.** Which communication-efficiency improvements should THIS harness adopt, given
(a) the study's landscape and (b) our already-substantial state, biased deterministic-first
(the study's OWN conclusion: protocols don't save tokens — architecture does; a deterministic
runtime owns DAG/queues/budgets/schemas/permissions, the LLM only the semantically hard
decisions)?

**Success criteria.**
- Backlog of buildable items, each mapped to a NAMED gap + a concrete integration point
  (file/module) + ONE of the study's metrics it moves.
- Deterministic-first: prefer measurement, progressive disclosure, references-not-payloads,
  deltas-not-states, targeted routing over LLM-in-the-loop or bleeding-edge latent comm.
- Every item respects our invariants: eviction ≠ deletion, no resident daemon, stdlib-only
  core, GUI writes no state, verify-on-demand, summaries are a view not the source of truth.
- Critique must reject over-engineering: the study warns multi-agent HURTS on sequential/
  coupled tasks (fragmentation, error propagation, coordination overhead); single-agent is
  always the baseline; observation must pay for itself.

**Declared budget.** claude executor (Max window, digest −64% required-reads); 1 divergence
wave (5 ideators) + 1 critique wave (4 critics); research-profile budgets; no wave 3.

## Phase 1 — Evidence matrix (verified 2026-07-12)

| claim | source | prov | conf | maturity |
|---|---|---|---|---|
| Progressive disclosure (tool NAMES + 60-char descs upfront; full schema on demand) + execute-in-code returning only summaries cut a benchmark 150k→2k tokens (98.7%); ~55k tokens burned by 5 MCP servers before the first message; intermediate data stays OUT of model context (privacy) | [web] [Anthropic — Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) | web | forte | validado (vendor eng) |
| One-shot pruning of the spatio-temporal message graph (AgentPrune) → 28.1–72.8% token reduction at comparable quality; $5.6 vs $43.7; +3.5–10.8% vs adversarial msgs | [web] [Cut the Crap, arXiv:2410.02506, ICLR'25](https://arxiv.org/abs/2410.02506) | web | forte | validado |
| Multi-agent consumed ~15× tokens of a single chat (subagents ~4× each); worth it ONLY for parallelizable research, not sequential/coupled tasks | [web] study §2; [Anthropic multi-agent research](https://www.anthropic.com/engineering/multi-agent-research-system) | web | forte | produção (relato) |
| Multi-agent benefit depends on task decomponibility/topology/model; sequential configs can DEGRADE (fragmentation, error propagation, overhead) | [web] study §2; [Towards a Science of Scaling Agent Systems, arXiv:2512.08296](https://arxiv.org/html/2512.08296v1) | web | moderada | preliminar |
| Protocols (MCP/A2A/AG-UI/ACP) standardize interfaces but do NOT reduce tokens; a naive MCP client loads all schemas + all intermediate results into the prompt | [web] study §1,§3; [MCP spec](https://modelcontextprotocol.io/specification/2025-11-25) | web | forte | validado |
| Artifacts by reference (subagents write to persistent store, pass lightweight refs to the coordinator) cut fidelity loss + the "telephone game" | [web] study §4.3; Anthropic multi-agent | web | forte | produção (relato) |
| Compression is NOT semantically neutral — fact substitution, semantic inversion; single-shot compression doesn't transfer to multi-step agentic coding | [web] study §6.4; arXiv:2602.09789, arXiv:2605.11051 | web | moderada | preliminar |
| Latent/KV-cache comm (LatentMAS, KVCOMM >70% reuse, TokenDance 11–17×) is the token frontier but opaque/unauditable, arch-coupled, a security surface (KV-cache integrity attacks) | [web] study §10; arXiv:2511.20639, 2510.12872 | web | moderada | demonstração conceitual |
| Communication should be a costed ACTION, not a free side-effect (MARL heritage: who/when/what/to-whom/how-aggregated) | [web] study §7; IC3Net/TarMAC/SchedNet/IMAC | web | forte | validado (adjacent field) |

**Baseline — what the harness ALREADY has (do NOT rebuild):** records ledger (SPEC-112:
blackboard-shaped shared memory + FTS + 200-char HANDLES = artifact-by-reference, source+ref
dereferenced on demand); `workflow fold` F1 (result + pointers, eviction≠deletion); handoff
minimal-first + token-budget demotion ladder; non-authoritative sha-stamped context digest
(−64% required-reads) with drift detection (this session); workflow DAG (fork-join/map-reduce)
+ async supervisor + circuit breaker + locks/leases + controlled-writes = a **deterministic
control plane** (matches the study's §12.1); token-audit + budgets per profile; typed RESULT
contracts (WORKER_RESULT/REDUCE_RESULT/reviewer, no-self-waiver); cache-stable delegation
packet (TE.6 = prefix-caching adjacency); events.jsonl (a log, not pub/sub); the `subject`
dimension (landed this session) = per-record scoping; MCP config exists but has **NO consumer**
(dependency-bootstrap round).

**Named gaps (candidate backlog anchors):**
- **G1 — the communication economy is UNMEASURED.** token-audit sizes a *plan*; none of the
  study's §13 system metrics exist: communication-amplification, context-utilization,
  duplicate-context ratio, tool-disclosure-overhead, useful-fan-out, handoff-loss, stale-
  context ratio. You cannot optimize what you don't measure. Deterministic; reuses the M1
  stdout rung + the (planned) perf-metrics rung pattern.
- **G2 — no progressive tool/MCP disclosure + no execute-in-code (the study's #1 token win).**
  MCP is config-only with no consumer; there is no "names+short-desc upfront → 1–5 schemas on
  demand → run the composition in code → return a compact summary" path (Anthropic 150k→2k).
- **G3 — typed message envelope + provenance/security is partial.** Results are typed, but
  there's no FIPA-ACL-style act vocabulary (COMMAND/OBSERVATION/DECISION/COMPLETION/FAILURE/
  BUDGET_ALERT/SECURITY_ALERT…) with a signed provenance envelope (message_id, trace_id,
  sender, capability, content_hash, hop_limit, classification) the runtime can route WITHOUT
  an LLM. Agent-in-the-Middle + protocol-composition are unmodeled trust boundaries. Adjacent
  to the isolation round's `subject`.
- **G4 — no adaptive fan-out / marginal-contribution / diversity policy.** Branch count is
  fixed at plan time; there is no §12.4 activation policy (single-agent baseline → estimate
  decomponibility → fan-out only if independent subtasks → terminate low-contribution agents),
  no useful-fan-out signal, no message pruning (AgentPrune). Needs G1's metrics first.
- **G5 — event log is not pub/sub; broadcast-by-default.** events.jsonl is append-only but has
  no typed-topic subscription/targeted routing (only the consumers that depend on an event
  get it) nor sparse-communication pruning (who actually needs this observation?).
- **G6 (bleeding edge, likely PARK) — latent/KV-cache communication.** Prefix caching / KV
  reuse / latent channel — study marks it bleeding-edge with interop/auditability/security
  caveats. TE.6 cache-stable packets are the only safe adjacency today.

## Phase 2 — Briefs and gate

**Brief 1 — measure the communication economy (deterministic foundation).** How might we
instrument the study's §13 metrics — communication-amplification, context-utilization,
duplicate-context, tool-disclosure-overhead, useful-fan-out, handoff-loss, stale-context — so
the harness can SEE where tokens are wasted and gate/guide the other cuts, deterministically
(reusing token-audit + the M1/perf-metrics rung), net-cost-positive, no LLM in the measurement
loop? (You can't optimize what you don't measure; this unblocks G4.)

**Brief 2 — cut amplification at the two biggest sinks (architecture, deterministic).** How
might we close the two highest-leverage gaps — (a) progressive tool/MCP disclosure +
execute-in-code-return-compact (the 150k→2k pattern; MCP has no consumer today; ties to the
Skills/MCP panel + dependency-bootstrap), and (b) enforce references-not-payloads + deltas-not-
states + typed/targeted messages (build on the records handles, fold F1, handoff ladder, the
`subject` dimension, events.jsonl) — WITHOUT the bleeding-edge latent stuff, respecting
summaries-are-a-view and single-agent-baseline?

**Parked (future round / needs a signal):** G6 latent/KV-cache (bleeding-edge; needs open-
weights/homogeneous infra + a security model); G4 adaptive fan-out + diversity (needs G1's
useful-fan-out/marginal-contribution signal first); the full G3 security envelope (partial —
ride the isolation round's `subject`/provenance work).

**Gate.** Scope/waves/budget pre-approved by the owner (this invocation). Deterministic-first
+ single-agent-baseline + net-cost-positive are hard constraints on the critique wave.

## Phase 3 — Wave 1 (divergence)

`WF-20260712-173852-771172`, `research-divergence`, 5 ideators (simplicity, performance,
reliability, trust-boundary, analogy), claude executor. 3 fulfilled + 2 length-rejected
(`>12000 chars` — content valid, read off disk). 23 deterministic concepts, heavy
convergence on the named gaps. Standout novel adaptations: the **argparse subcommand tree
IS the tool catalog** (progressive disclosure with no MCP client — w1), demand-paged
(page-fault) schema disclosure (w5), a double-entry per-edge token ledger yielding
communication-amplification (w5), content-hash closed-loop readback as a handoff-loss
detector (w5), CAN-bus acceptance-filter → typed subscription without a broker (w5).
Orchestrator consolidated the 23 into **5 candidates**:
- **C1 communication-economy meter** (G1) — metrics at `workflow_finalize` from on-disk
  artifacts (amplification/stale-context/handoff-loss); reuses fold F1 + cost_metrics + M1.
- **C2 progressive tool disclosure** (G2, #1 token win) — argparse tree as catalog +
  demand-paged schema + execute-in-code-return-compact; the first real MCP consumer.
- **C3 references-not-payloads gate + content-addressed deltas** (G5) — a collect/DLP gate
  check + content-addressed packet sections (deltas-not-states).
- **C4 typed event envelope + read-time topic routing** (G3+G5) — provenance envelope on
  events.jsonl + filter-not-bus subscription + subject-scoping (ties the isolation round).
- **C5 containment feedback loop** (reliability) — worker-failure→breaker, observed-vs-
  estimated budget feedback, wave-reliability rollup + selective re-dispatch, egress scrub.

## Phase 4 — Wave 2 (critique) — done

`WF-20260712-180613-842598`, `research-critique`, 4 critics (validity/architecture/cost/
security), `--seed` = the divergence reduce, critiquing the 5 candidates. All 4 fulfilled.
Verified anchors (validity): `cost_metrics.record_workflow` (cost_metrics.py:108), 
`workflow_finalize` (workflow_lifecycle.py:55/98), `append_event` (harness.py:127), 
`check_digest_drift` (context_digest.py:125), 75 `add_parser` calls in harness.py, 
`secret_scan.py`, `spec_test_gate.py`. External 150k→2k anchor re-verified via WebSearch 
(real, Anthropic eng — but vendor's own single example, **not** a benchmark; measure locally).

**The one confirmed live bug (all four flagged C5 as highest-value):** the circuit breaker's
containment gap is real and **worse than the divergence stated** — `async_runtime.py:505-524`
records breaker **success** for a schema-valid worker result whose `status='failed'`, and
rejects invalid/missing results at rc=0 **without** ever calling
`workflow_executor_record_failure`. A worker exiting 0 with a rejected/failed WORKER_RESULT
never trips containment → failed waves silently re-run at full price.

**Cross-lens verdicts (keep / keep-with-changes / cut + what to SPLIT/PARK):**

| cand | validity | architecture | cost | security | net |
|---|---|---|---|---|---|
| C1 economy meter | keep¹ | **keep** (lowest coupling; view-only extension of an existing seam) | build #2 | keep | **KEEP** (ship subset; ¹handoff-loss needs a `contextEcho` field absent from WORKER_RESULT → PARK that one metric) |
| C2 progressive disclosure | ext-claim verified | keep-w/-changes (split; helper in `harness_lib`, not the monolith) | argparse half only | keep-w/-changes (MCP half crosses trust boundary) | **KEEP-CHANGES** (ship argparse-catalog + introspection; **PARK** MCP-consumer half until hash-pin fail-closed) |
| C3 refs-not-payloads | keep | keep-w/-changes (split; lint observe-only first) | lint half only | keep-w/-changes (sha-index must be subject-scoped or it's a cross-project oracle) | **KEEP-CHANGES** (ship handles-lint observe-only; **PARK** content-addressed deltas) |
| C4 typed envelope | keep (HPACK/CAN = analogy) | keep-w/-changes (events.jsonl has 8+ readers → additive-only + ONE shared read-filter; build when C5a is first consumer) | minimal fields only | keep-w/-changes (transient log drops SECURITY_ALERT on wipe → route alert acts to durable escalations ledger) | **KEEP-CHANGES, DEFERRED** (with C5) |
| C5 containment loop | **gap CONFIRMED, worse** | keep-w/-changes/split | **build #1** | keep, **highest security value** | **KEEP** (C5a = the fix; b/c/d split out) |

**Unanimous build order:** C5a (the bug) → C1 (measurement rung; nothing else is provable
without baselines) → C3-lint / C2-argparse (independent, cheap, observe-only) → C4 (only when
C5a needs the envelope as its first consumer).

## Phase 5 — Portfolio & backlog

Deterministic-first held: every survivor is a gate/ledger/read-time extension of an existing
seam — **zero** new daemons, brokers, LLM-in-the-loop, or bleeding-edge latent comm. The
critique cut the over-built halves (edge ledger, MCP consumer, delta packets, full envelope)
to PARK, leaving a spine of cheap, measurable, single-writer changes. Portfolio → the
**Communication efficiency roadmap** section in `docs/IMPLEMENTATION_BACKLOG.md` (CE.1–CE.9),
each row = named gap + verified seam + the one §13 metric it moves + ship/PARK disposition.

**Ship spine (P0→P2):** CE.1 containment-gap fix (C5a) · CE.2 economy meter subset (C1) ·
CE.3 handles-lint observe-only (C3) · CE.4 argparse-catalog + introspection (C2).
**Parked with an explicit unblock signal:** CE.5 double-entry edge ledger (needs CE.2 live) ·
CE.6 MCP-consumer half (needs hash-pin fail-closed) · CE.7 content-addressed delta packets
(needs subject-scoped sha-index) · CE.8 typed envelope (build additive-only when CE.1's
follow-on needs it; route alerts to the durable ledger) · CE.9 adaptive fan-out (G4; needs
CE.2's useful-fan-out signal). Full detail + verdict table above.
