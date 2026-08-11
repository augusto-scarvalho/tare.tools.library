# Implementation Plans — Programmatic Tool Calling (N-PTC-*)

Plans parked in the backlog (owner 2026-07-19: “refine research results with very detailed plans”).
Derived from `ptc-round.md` (4 waves) + D030. Each plan is implementer-ready.

**Existing machinery to reuse (DO NOT reinvent):**
- `scripts/harness_lib/sandbox_spawn.py` — SPEC-151 (fs-confine + Job Object + risk tier). EXECUTION
  SUBSTRATE for model-emitted code. `evaluate_chokepoint` already uses `ast.walk` (gate idiom).
- `scripts/harness_lib/discovery.py` — discover chain (bulk reads) = probe target.
- `scripts/harness_lib/cost_metrics.py` + `route_ledger.py` — ledger (observed vs estimated;
  `_extract_harness_result` = deterministic block-extraction idiom).
- `scripts/harness_lib/agent_parity.py` — `conformance_report`, `supportState`, `accountingSemantics`
  (T-ADAPTERCONF/C16b) — where PTC capability is declared/verified.
- `.harness/capabilities.json` (`mcpServers` currently `{}`) — exposed tools/MCP.
- Taint envelope (RD-TAINT / D023) — secret-never-egresses model extended by 4th sink.
- `tools/openai_worker.py` — HTTP worker for open weights (where emulated loop plugs in).

---

## N-PTC-PROBE (EXP-24) — measure-only probe · BUILDABLE NOW · size M

**Goal:** measure latency/token/CPU of emulated PTC vs traditional on a REAL task, in OUR traffic, without
changing production. This justifies (or kills) the engine — PTC is a workload-shape bet (τ²-bench: +8% in
sequential; vendor numbers not independently replicated).

**Reuse:** discover chain (`discovery.discover_paths`) as target (mother case); `cost_metrics.record_workflow`
for logging (`costBasis: observed|estimated`); sandbox for emulated-PTC leg.

**Approach:**
1. **Probe** (`testing/probes/ptc_probe.py`, sibling of truth-divergence/CFP): take ONE set of real discover
   inputs and run 2 legs on SAME input — (a) TRADITIONAL: current per-file loop (N reads = N steps);
   (b) EMULATED-PTC: one script iterates reads inside sandbox and returns only filtered aggregate. Log per
   leg: round trips, billed tokens (observed from endpoint; estimated marked), wall-clock latency,
   **sandbox CPU time** (PTC’s new cost axis), by fan-out N.
2. **Matched budget:** same input, same model, same ceiling — otherwise delta confounds “better” with
   “spent more” (EXP_METHODS matched-budget-controls card).
3. **Reduction:** by task shape (fan-out N), aggregate delta; noise floor = rep stdev; verdict only if delta
   > L13 noise floor in ≥2 buckets. Break-even N (hypothesis N>3–4 to falsify).
4. **Trusted traffic only:** compare only legs whose `accountingSemantics` is native/emulated (not unknown) —
   C16b applies to probe delta too.

**Footprint:** `testing/probes/ptc_probe.py` (new, self-check); perhaps `cpuMs` field in ledger record.
Does NOT touch production discover path (PTC leg isolated in probe).

**Acceptance:** probe runs discover chain 2× (traditional vs PTC) in ≥2 fan-out shapes, produces table
`(shape N) → (Δround-trip, Δtoken, Δlatency, ΔCPU)` with noise-floor gating, ZERO production change.
Records first EXP-24 data point. **Abandon:** if gain stays in noise floor (or CPU consumes token gain) →
PTC remains measure-only; engine not worth it.

**Gate:** measure-only, measure-first authority (like truth-divergence probe). Buildable.
**Dependency:** discover chain (exists). **Size:** M.

---

## N-PTC-ENGINE — PTC engine (loop in our sandbox) · OWNER-GATED · size L

**Goal:** engine that gives PTC to EVERY executor by routing orchestration loop through OUR sandbox
(native = opt-in). Control + security → only after EXP-24 justification + security review.

**Reuse:** `sandbox_spawn` substrate; `evaluate_chokepoint` `ast.walk` idiom (gate);
`_extract_harness_result` (block extraction); `openai_worker.py` (open-weight plug-in).

**Approach (precise emulated loop):**
1. **`harness_tools` (stub module):** per PTC session generate ONE module of functions
   `async def harness_<verb>(args: dict) -> str` (Anthropic signature: dict-in, string-out, awaitable) —
   ONE per tool ALREADY declared and narrowed for worker (c5: stub-set ⊆ worker tools). Inject into sandbox
   namespace.
2. **Prompt contract:** system prompt declares signatures + instructs model to emit ONE ```python block with
   orchestration script, ending in a `print()` of FILTERED result only.
3. **Deterministic code extraction:** parse block (reuse `_extract_harness_result` idiom). No block → no PTC →
   fallback to traditional tool call (fail-closed to already-verified cheaper path).
4. **Static AST gate BEFORE execution:** `ast.parse` + `ast.walk` — reject any Call/Import not (a) injected
   stub or (b) minimal stdlib allowlist (`json,re,itertools,statistics,asyncio`). Reuse
   `evaluate_chokepoint` self-check technique.
5. **Execution:** vetted code runs through `sandbox_spawn(mode=bounded)` with injected namespace — same Job
   Object / fs-confine / risk tier as any worker (R0 default; R1+ only if stub-set contains write-capable
   tool). Dangerous builtins ABSENT from namespace (gate backstop).
6. **Pause/resume relay (tool body runs on OUR side):** when code calls a stub, sandbox pauses, harness runs
   REAL verb, returns string result, code resumes. (Same Anthropic protocol — native vendor does this; we do
   it for all.)
7. **Filtered return:** only final `stdout`/return crosses to model context (vendor-agnostic envelope — same
   shape as `code_execution_result.stdout`).
8. **Fail-safe (NVIDIA w-003):** checkpoint/resume for partial batch (script failure does not lose whole
   batch); liveness timeout (hung script); CPU time enters ledger.

**Footprint (when opened):** `harness_lib/ptc.py` (stub-gen + loop + gate + relay); plug into
`openai_worker.py` (emulated) + Claude adapter (native opt-in); NEW spec door (SPEC-116) + scenario
(AST gate rejects malicious code; stub-set ⊆ tools; filtered return; no-block fallback).

**Acceptance:** an open-weight model emits code orchestrating N discover reads in sandbox, AST gate rejects
`open()/socket/subprocess`, only aggregate returns, CPU enters ledger, no-block falls back to traditional.

**Gate:** OWNER-GATED (control + security). Prerequisites: EXP-24 + N-PTC-TAINT4 + security review.
**Dependencies:** N-PTC-PROBE, N-PTC-TAINT4. **Size:** L.

---

## N-PTC-TAINT4 — 4th taint sink · OWNER-GATED (security) · size M

**Goal:** close the hole PTC opens: D023 lists 3 sinks (prompt/persisted-result/log); sandbox stdout/stderr
is a FOURTH (returns to model by design). A `print()`ed secret crosses without touching the 3.

**Reuse:** RD-TAINT taint envelope / sink check (D023) — same mechanism, new call site.

**Approach:**
1. **4th sink:** taint-sink check runs on CAPTURED sandbox `stdout`/`stderr` BEFORE returning as code result.
   Tainted data (secret-read) on stdout → fail-closed (block/redact).
2. **Lethal-trifecta invariant:** a stub namespace may not combine secret-reading stub + egress-capable stub
   without `declares_egress=True` AND active 4th sink (PTC removes natural per-call checkpoint).
3. **No escape:** stubs only `dict → str` (never `run_shell(str)` — closes command-injection by
   construction); `HARNESS_SANDBOX_OVERRIDE` unreachable from emitted code (OUTER process env, stripped by
   envKeepList).

**Footprint (when opened):** integrate into N-PTC-ENGINE (relay invokes taint check on stdout) + RD-TAINT
envelope; security scenario (secret on stdout → blocked; secret+egress namespace without declares_egress →
refused). Isolated security review.

**Acceptance:** script that `print()`s a marked secret NEVER delivers secret to model (fail-closed);
secret+egress namespace without declares_egress is refused. **Gate:** OWNER-GATED + security review.
**Dependencies:** RD-TAINT/D023 + N-PTC-ENGINE. **Size:** M.

---

## N-PTC-CONFORMANCE — capability + accounting · OWNER-GATED · size M

**Goal:** declare/verify PTC per executor with T-ADAPTERCONF discipline (native vs emulated; honest accounting).

**Reuse:** `agent_parity.py` (`supportState`, `conformance_report`, `accountingSemantics`).

**Approach:**
1. **Capability `programmatic-tool-calling`** with `supportState` (claude=native,
   openai/codex=native-if-CLI-adopts [verify], remainder=emulated). Declares CAPABILITY, not route choice.
2. **c9 `ptcTokenScope`** (new report-only subfield): `vendor-discounted|full-emulated|unknown`. Anthropic
   DISCOUNTS native tool-result tokens → naive native-vs-emulated comparison favors Claude for a reason that
   is not our design. Default unknown, never gates.
3. **c5 no-amplification:** scenario proves generated stub-set is subset of worker’s declared tools (worker
   emitting code does not gain reach it would lack one-call-at-a-time).

**Footprint (when opened):** field in `capabilities.json`/`agent_parity.py`; conformance scenario
(c5 subset + c9 scope). **Acceptance:** report shows supportState+ptcTokenScope by executor; c5 fails if
stub-set exceeds declared tools. **Gate:** OWNER-GATED. **Dependency:** N-PTC-ENGINE. **Size:** M.

---

## N-TOOLSEARCH — tool search / RAG-over-tools (boundary) · BUILDABLE (measures tokens) · size M

**Goal:** when many tools/MCP exist, load only relevant schemas per turn (do not stack all into context —
large token cost). Stacks with PTC but testable WITHOUT engine.

**Reuse:** `capabilities_view.py` (merges MCP from 5 surfaces — candidate surface); cost ledger.

**Approach:** retrieval (BM25/regex or embedding) over tool catalog; load only subset relevant to request;
**APPEND-not-swap** (add, do not replace — preserves prefix cache, as Anthropic Tool Search Tool does).
Measure-only first: token savings vs stacking everything.

**Footprint:** `harness_lib/tool_search.py` + measure-only probe (tokens with vs without search).
**Acceptance:** with N declared tools, search loads only relevant ones and measures token savings
(noise-floor gated). **Gate:** buildable (measure-only). **Dependency:** —. **Size:** M. Ref: Gorilla
(arXiv:2305.15334), Anthropic Tool Search Tool.

---

## Suggested order
1. **N-PTC-PROBE (EXP-24)** + **N-TOOLSEARCH** — buildable, measure gain before anything else.
2. **N-PTC-TAINT4** — security control must exist BEFORE engine (4th sink is non-optional).
3. **N-PTC-ENGINE** — only when probe shows gain above noise floor + taint4 ready + security review.
4. **N-PTC-CONFORMANCE** — with/after engine.

> Note: same treatment (implementer-ready plan) already exists for N-COMPACTION; it can extend to other
> research items (N-TRUTHRECON-*, RD-U→U, RD-CRASH→injector, RD-TAINT→taint) — on request.
