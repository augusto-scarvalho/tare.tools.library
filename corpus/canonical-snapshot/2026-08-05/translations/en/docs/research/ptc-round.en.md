# Research Round — Programmatic Tool Calling (PTC) + Tool-Calling Frontier

Owner 2026-07-19: broad research (NVIDIA + Sonnet 5 HIGH) on PTC — how the harness and repositories
benefit (focus on LATENCY, EFFICIENCY, TOKEN CONSUMPTION); how to implement across different vendors +
OpenAI-compatible open weights + PARITY; and scan the FRONTIER of tool-calling knowledge and fit it into PTC
+ the traditional tool calling we already have. Orchestrator = this session.

## What PTC is (framing)

TRADITIONAL tool calling: model emits ONE call at a time → model round trip per call; result (even huge)
returns to model context at every step. **PTC:** model writes CODE that PROGRAMMATICALLY ORCHESTRATES
multiple tools (loop/filter/composition) in a sandbox; intermediate results remain in sandbox and do not feed
back into model. Gain: fewer round trips (latency), fewer tokens (large output does not return to context),
more efficiency (model filters/aggregates in code before deciding). Anthropic (code execution / tool-as-code),
OpenAI (code interpreter + function calling) already ship; open weights (glm/llama) generally do NOT have it
natively → harness provides it.

## What the harness ALREADY has (substrate)

- **Sandbox SPEC-151** (`sandbox_spawn.py`: fs-confine + Job Object + tier) — execution substrate for
  model-emitted code. Key parity piece for open weights without native code-exec.
- **Discover chain** (`discovery.py`: Gemini→NVIDIA for bulk text/image) + **Graphify** (code AST) — bulk-read
  orchestration = PTC’s MOTHER use case (one code call iterates N reads).
- **5 executors** (`executors.json`: claude/codex CLI, openai-compat/nvidia-compat/gemini-compat HTTP) —
  PARITY surface where PTC must behave the same.
- **Adapter conformance** (T-ADAPTERCONF, `accountingSemantics`, trust tiers) — parity discipline.
- **Model economy + delegation ledger** — cost/token DNA PTC optimizes.
- **MCP** (`capabilities_view.py`, capabilities.json) — exposed tools.

## The question

> How do the harness (and repos we work on) benefit from PTC — quantifying LATENCY, EFFICIENCY and TOKEN
> CONSUMPTION? How do we IMPLEMENT PTC across vendors (native Anthropic/OpenAI) AND OpenAI-compatible open
> weights (without native PTC), with PARITY? And what does the tool-calling frontier bring that fits PTC and
> our existing traditional tool calling?

## Subquestions

1. **Where PTC wins in the harness:** which flows (bulk discover, graphify, workflow fan-out, mass reads,
   reduce) cut round trips/tokens with PTC? Quantify expected gain.
2. **Mechanism:** how model emits code calling harness tools (harness.py verbs, MCP) and runs it in SPEC-151
   sandbox; what exposes tools as functions; how results return (filtered only). Deterministic and safe.
3. **Cross-vendor parity:** vendors with NATIVE code-exec (Anthropic/OpenAI) vs open weights
   (glm/llama through nvidia/openai-compat) without it → harness runs emitted code in its own sandbox to give
   SAME capability. How adapter-conformance/accountingSemantics covers this.
4. **Security:** PTC = model writing executable code → connects to sandbox (SPEC-151) + RD-TAINT (D023,
   secret never egresses) + secret scan. What emitted code MAY touch.
5. **Frontier (Flow A web):** MCP, tool-search/RAG-over-tools (many tools), parallel tool calling,
   computer use, structured outputs, tool-result caching, “tools as code” — what is new and how each fits PTC
   vs traditional.

## Criteria (harness DNA)

- **Measure-before-control:** PTC latency/token gain is MEASURED (traditional baseline vs PTC on same task),
  not asserted. Reuse delegation ledger + accountingSemantics.
- **Real parity:** same behavior across executors, verified by adapter conformance.
- **Security:** emitted code runs contained (sandbox); secret does not egress (RD-TAINT).
- **Anti-fabrication:** citation → source + date (frontier is web; mark `[web]` untrusted-until-verified).
- **Reuse** sandbox + discover + executors + MCP — not a parallel runtime.

## Waves

- Wave A (NVIDIA, 5): design/reasoning — PTC mechanism in harness, sandbox reuse, parity abstraction,
  where latency/token improves.
- Wave B (Sonnet 5 HIGH, 3, WITH WebSearch): web frontier — (1) state of the art of PTC across vendors +
  evidence of latency/token gain; (2) parity implementation (native vs sandbox-side for open weights);
  (3) tool-calling frontier (MCP/tool search/parallel/computer use/…) + fit.

## Convergence (Phase 5)

Isolate: where PTC wins (quantified), mechanism (sandbox + tools-as-functions), cross-vendor parity abstraction,
security controls, frontier map → PTC/traditional. What is buildable now (measure-only latency/token
PTC-vs-traditional probe on a task) vs engine (owner-gated). Synthesize into design + backlog increments +
verifiable citations.

---

# Phase 5 — Convergence (4 waves: NVIDIA 5 + 3 Sonnet 5 high with WebSearch)

## What it is + the win (unanimous)

PTC = model emits CODE that orchestrates tools in sandbox; intermediate results stay LOCAL (do not feed
context); only filtered output returns. Win = fewer round trips (LATENCY, 1:1) + fewer TOKENS (large output
does not return). **Non-linear with result-set size.** Tightest analogy (NVIDIA w-005): **database query
pushdown** (MapReduce/Spark) — push imperative code to where data lives, intermediate rows stay on worker
node, only aggregate returns; PTC code = UDF.

## The REFRAME that changes the design (parity wave — load-bearing)

“Native vs sandbox” is the WRONG question. Pause/resume protocol (Anthropic, read in primary docs): execution
pauses on EACH tool_use, returns to OUR server, WE run the tool, return result. **Tool bodies ALWAYS run on
our side**; vendor container only holds orchestration LOOP. → **Route the loop through OUR `sandbox_spawn`
by default for EVERY executor** (including Claude); native container = opt-in. Gains uniform
conformance/taint/accounting.

## Fit in harness (where it wins)

- **Substrate:** SPEC-151 sandbox ALREADY is what PTC needs. Thin layer (NVIDIA w-001): a `harness_tools`
  function module (Anthropic signature async `dict → str`) injected into sandbox namespace; model emits ONE
  script; only filtered `stdout` returns.
- **Highest-gain flows:** **bulk discover** chain (MOTHER case), workflow **reduce/fan-out**, **bulk graphify**
  — many reads → one script. (Fork-join ALREADY is parallel calling at orchestration level; PTC = IN-TURN
  loop of ONE worker.)

## Cross-vendor parity

- **CodeAct (arXiv:2402.01030, ICML 2024)** = academic root + portable BEHAVIOR (+20% success vs JSON).
  HOSTED PTC infrastructure = only 2 vendors: **Anthropic (Nov/2025, Python)** + **OpenAI
  (GPT-5.6, 2026-07-09, JavaScript/V8)** — SAME `allowed_callers` (industry convergence).
  **Round premise changed mid-flight** (round doc assumed OpenAI only had code interpreter).
- **Open weights (glm/llama/deepseek/qwen/mistral + NVIDIA NIM)** = NO native hosted PTC → **emulated by OUR
  sandbox loop**: prompt contract (signatures + one ```python block) → deterministic code extraction (reuse
  `HARNESS_RESULT` idiom) → **static AST gate BEFORE execution** (reuse `ast.walk` from
  `sandbox_spawn.evaluate_chokepoint`) → `sandbox_spawn(bounded)` with injected namespace → only filtered
  output returns. Model-agnostic buildability supported by LangChain Open PTC, Cloudflare Code Mode,
  HF smolagents.

## Security (trust waves — 2 strong findings)

- **🔒 4th TAINT SINK (new, on top of D023):** D023 lists 3 sinks (prompt/persisted result/log). PTC opens a
  FOURTH: **sandbox stdout/stderr** (returns to model by design). A secret `print()`ed in script crosses
  WITHOUT touching the 3 sinks → **taint check must run on captured sandbox stdout** or PTC reopens D023 gap.
  One extra call site in existing envelope.
- **Lethal trifecta (Willison):** PTC collapses “private data + untrusted content + egress” into one script,
  removing natural per-call checkpoint → NEW invariant: stub namespace must not combine secret-reading stub +
  egress-capable stub without `declares_egress` + active 4th sink.
- Stubs only `dict → str` (NEVER `run_shell(str)` — closes command injection by construction); dangerous
  builtins absent from namespace (AST-gate backstop); `HARNESS_SANDBOX_OVERRIDE` unreachable from emitted
  code. Filtered return = only trust chokepoint.

## New failure classes (NVIDIA w-003)

- **Partial batch:** script failure loses ENTIRE BATCH (per-call retry is granular; PTC is not) →
  checkpoint/resume INSIDE sandbox.
- **CPU time = UNTRACKED cost axis:** PTC trades tokens for COMPUTE → measure sandbox CPU.
- **Liveness:** hung script yields no model turn → timeout detection.
- **Accounting blind spot:** ledger does not see tool calls internal to sandbox → close it.

## Conformance / accounting (T-ADAPTERCONF)

New `programmatic-tool-calling` capability with `supportState` (claude/openai=native, remainder=emulated).
- **c9 `ptcTokenScope`** (new subfield): Anthropic DISCOUNTS native tool-result tokens → naive comparison of
  “billed tokens” native-vs-emulated favors Claude for a reason unrelated to our design. Field
  `vendor-discounted|full-emulated|unknown`, report-only, never gates.
- **c5 no-amplification:** PTC worker stub-set must be a PROVABLE subset of already-declared tools — worker
  emitting code cannot gain reach unavailable one-call-at-a-time.

## Measure-before-control (the gate — CRITICAL)

PTC is a WORKLOAD-SHAPE BET, NOT default-on. **τ²-bench (Anthropic’s OWN data): +8% cost on short sequential
flow** (“sequential single-call workflows do not benefit”). Vendor numbers (20–98%) WITHOUT independent
replication; PointFive (arXiv:2607.12161, 2026-07): token reduction ≠ billed cost with caching (r=0.15).
Best NON-vendor number: LLMCompiler (ICML 2024) 3.7× latency/6× cost vs ReAct. → **measure-only probe FIRST:**
run discover chain TRADITIONAL vs emulated-PTC on OUR traffic, matched budget, log in `cost_metrics`
(observed vs estimated) + CPU time, gate at L13 noise floor. Break-even hypothesis to FALSIFY: N>~3–4 calls.

## Portfolio / buildable

- **BUILDABLE NOW (measure-only): N-PTC-PROBE (EXP-24)** — latency/token/CPU traditional-vs-emulated-PTC
  comparison on real task (discover), noise-floor gated. NEVER changes production path.
- **OWNER-GATED:** **N-PTC-ENGINE** (`harness_tools` module + sandbox loop + caller-tag pause/resume relay) —
  control + security → probe must justify + security review. **4th taint sink** (fold into RD-TAINT/D023).
  Conformance/accounting extension.

## Frontier that fits (Flow A web, cited + dated)

- **Tool Search / RAG-over-tools** (Gorilla arXiv:2305.15334; Anthropic Tool Search Tool, 85% reduction,
  APPEND-not-swap to preserve cache) — stacks with PTC (script finds tool before invoking). Testable WITHOUT
  engine. High value (harness already merges MCP from 5 surfaces).
- **MCP-as-code** — when `capabilities.json.mcpServers` (currently `{}`) is populated; same stub module.
- **Structured outputs / constrained code grammar** — defense in depth over sandbox (code limited to safe
  subset before execution). `[judgment]`, no shipped product.

## Traceability

| Evidence | Idea | Experiment | Task | Status |
|---|---|---|---|---|
| 4/4 (code-orchestrates-tools) + CodeAct + pushdown | harness_tools in sandbox + loop | N-PTC-PROBE = EXP-24 | N-PTC | designed; probe buildable, engine owner-gated |
| parity w-004 + NVIDIA w-004 (4th sink) | taint on sandbox stdout | — | folds RD-TAINT/D023 | designed (security) |
| vendor scan (OpenAI 2026-07-09 PTC) | premise updated; parity = sandbox only for open weights | — | N-PTC-ENGINE | [web] verify |
| τ²-bench/PointFive/LLMCompiler | PTC is workload bet; measure on our traffic | EXP-24 | — | measure-first |
