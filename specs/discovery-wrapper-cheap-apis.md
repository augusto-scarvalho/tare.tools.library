# SPEC-107 — Cheap Discovery Wrapper (Backlog M2W)

Priority milestone (jumps M2H/M3; user decision 2026-07-09). Evidence base:
`docs/HARNESS_IMPROVEMENT_IDEAS.md`, recon of the LLM-assist plumbing (same date).

## Goal

One entrypoint — `python scripts/harness.py discover <paths...>` — that routes discovery to the
cheapest capable layer: **code → local pure-AST graph (never an API)**; **text and images →
third-party APIs, Gemini free tier first, NVIDIA Build free credits second**. Its explicit
anti-goal: the expensive coder LLM (Claude/Codex) must never become the de-facto reader of bulk
text/images. When every cheap layer is unavailable, the wrapper does not degrade silently — it
returns a what/cause/fix message (SPEC-101 format) telling the supervisor model or human exactly
which dependency to provision, and the sanctioned manual fallback remains *focused* raw search.

## Grounding (research and evidence)

- **Cost policy already in spec:** `specs/00-universal/structural-discovery.md:74-79` — API
  assistance is optional, disabled by default, text/image only, free-tier only, never primary
  code graphing. The wrapper operationalizes this instead of leaving it prose.
- **Recon findings (2026-07-09):** no file-type routing exists anywhere; the Gemini path
  delegates to `graphify.llm`, which is not importable from the project venv (graphify is a uv
  tool in its own environment) — so text enrichment likely never ran on this machine; no image
  handling exists despite `inputKinds: ["text","image"]`; no NVIDIA plumbing exists (greenfield).
- **NVIDIA Build (verified 2026-07-09):** OpenAI-compatible `/v1/chat/completions` at
  `https://integrate.api.nvidia.com/v1`, key prefix `nvapi-`, free tier ~1000 credits + 40 RPM,
  no credit card; vision via `meta/llama-3.2-11b/90b-vision-instruct`. Gemini exposes the same
  OpenAI-compatible shape at `https://generativelanguage.googleapis.com/v1beta/openai/` — one
  stdlib client serves both providers.
- **Token economics (this repo's own history):** a mute dependency error costs an exploration
  cycle (F4); the wrapper's refusal messages are the supervision surface for API dependencies.

## Applicability

Discovery of repository content. Not a replacement for the graph (`graph-build-code-ast` stays
authoritative for code), not an orchestrator, not used inside gates (gates never do network).

## Scope

In scope: router subcommand; stdlib OpenAI-compatible client with vision (base64 image parts)
and secret redaction; `nvidia_extract_fallback.py` provider script mirroring the Gemini one;
direct-stdlib fallback + `--kind image` in the Gemini script; sibling config block
`knowledgeGraph.apiAssistedProviders`; policy-surface updates (guard hook message,
GRAPHIFY_INTEGRATION.md, structural-discovery addendum, additive AGENTS.md/CLAUDE.md lines);
no-network fixture.

Out of scope: retries/backoff beyond model-chain fallthrough (add when a rate limit actually
bites — 40 RPM is generous for our volume); caching; OCR/PDF; paid tiers; any use of executor
LLMs as a discovery layer (forbidden, not deferred).

## Requirements / invariants

- **Routing:** `.py` → AST layer only, even with providers enabled (`forbiddenInputKinds`
  honored in code, not just config). Text extensions → provider chain in
  `apiAssistedProviders.order`. Image extensions (png/jpg/jpeg/webp/gif) → same chain, vision
  payload. Anything else → `refused` with reason.
- **Never executor fallback:** on total API unavailability the per-file status is `refused`
  with a fix line naming both remedies (Gemini key / NVIDIA key + config flag); the wrapper
  never suggests "let the agent read everything" — it names `focused-raw-search` with the
  specific paths as the manual step.
- **Fail-safe chain:** provider errors (network, HTTP, quota) → next provider; all failed →
  per-file `failed` with the last redacted error and fix line. Exit 0 with per-file statuses;
  exit 1 only for total config failure (also what/cause/fix).
- **Secrets:** all provider exception/stderr text passes through
  `observability_exporters.redact_string` before printing (closes the historical
  GEMINI_API_KEY leak vector). Keys are read from env only (`GEMINI_API_KEY`/`GOOGLE_API_KEY`,
  `NVIDIA_API_KEY`), never echoed, never in URLs we build.
- **Config is additive:** `llmAssisted` block stays byte-identical; new sibling block only.
- **Gates never network:** the fixture tests refusal paths exclusively; `networkDefault: false`
  everywhere.

## Design anchors (verified 2026-07-09 — re-verify before editing)

- Existing gating messages to imitate: `harness.py:2820-2823`
  (`{"status":"refused","reason":"knowledgeGraph.llmAssisted.enabled is false; enable it..."}`).
- Provider script contract to mirror: `tools/graphify/gemini_extract_fallback.py` — `--out`,
  positional paths, model chain fallthrough (lines 70-103), stderr prefix, exit 0/1. Sidecar
  shape `{nodes, edges, hyperedges, input_tokens, output_tokens}`.
- Redaction helpers: `scripts/harness_lib/observability_exporters.py:37` (`redact_string`),
  `:55` (`redact_url`).
- `graphify_status()`: `scripts/harness.py:233-283` — expose the new block here.
- Timeout helper: `bounded_timeout` (`harness_lib.common`).
- `discover` is a **top-level** subcommand (like `escalations`) — exempt from both
  workflow-command lists.

### Landmines (gate pins — break any of these and the gate goes red)

- `spec_test_gate.py:768` pins `policy == "graphify-code-ast-first-source-verified"` exactly.
- `:770` pins `discoveryOrder[:3]` exactly — append new steps at index 3+, never insert before.
- `:779` and `:1830-1831` pin the `llmAssisted` block (provider/usagePolicy/inputKinds/models
  intersection/forbiddenInputKinds) — do not mutate it; add a sibling.
- `:775` forbids the substring `localAst` anywhere in serialized `knowledgeGraph`.
- `:785-787` require AGENTS.md to keep containing `Graphify`, `source-verified`,
  `Graphify code AST`, `Gemini API`, `text/image`; CLAUDE.md to keep `Graphify`, `AGENTS.md`.
  Additive edits only; both files are protected (bytes edit + snapshot regen + fixture green).
- New fixture must be registered in the `FIXTURES` map (~`:2779`) and the CI fixture list
  (`:873`).

## Acceptance criteria

- [ ] `discover` on a `.py` routes to the AST layer and makes zero network attempts even with
      providers enabled.
- [ ] `discover README.md` with no keys → per-file `refused`, ≤3 lines, naming both provider
      remedies and the config flag.
- [ ] `discover <image>.png` same, via the vision route.
- [ ] Unknown extension → `refused` with reason.
- [ ] Config: `llmAssisted` byte-identical; `discoveryOrder[:3]` unchanged; new step at 3+.
- [ ] All provider stderr/exception text passes redaction; no key substring can be printed.
- [ ] Fixture `graphify-api-providers` green without network; all `graphify:*` checks green;
      protected-files fixture green after snapshot regen.
- [ ] Live smoke (optional, operator-provided key, outside gates): one text call succeeds and
      writes the sidecar.

## Test strategy

- Refusal paths are the tested surface (no network in gates). Edge cases: mixed path list
  (code+text+image+unknown) yields per-file statuses; empty path list → legible error; provider
  order respected (config order flipped → chain order flips).
- Regression risks: the pinned gate checks above; `graphify_status()` consumers (status output
  gains keys — additive-safe for golden subset check).
- Coverage impact: enforced for the router's classification and refusal-message paths.

## Validation

MVP scenario = acceptance criteria 1-4 run as commands; then `spec-pack` + `commit` gates and
`--fixture protected-files` + `--fixture graphify-api-providers`, all rc=0.

## Universal baseline impact

`specs/00-universal/structural-discovery.md` (extended additively for the second provider),
`api-and-interface-security.md` (outbound calls: allowlisted endpoints from config only),
`secrets-and-configuration.md` (env-only keys, redaction), `dependency-and-supply-chain.md`
(stdlib-only client, no new packages).

## Escalation triggers

Any pressure to add a paid tier, to widen inputKinds to code, to call providers from gates, or
to add an executor-LLM fallback → human decision. Model-id churn (providers deprecate models) is
config-only maintenance, not an escalation.

## Operational findings (live sweep 2026-07-09)

Facts learned running the wrapper for real — they govern chain maintenance:

- **Catalog listing ≠ availability.** `GET /v1/models` returned ids that 404 on
  `/chat/completions` (kimi-k2.6, gemma-3-12b-it, cosmos-reason2-8b). Only a real extraction
  call with the wrapper's own prompt proves a model works.
- **Empty graph is its own failure mode.** Some models answer fast but never produce nodes
  (llama-3.2-90b-vision, phi-4-multimodal, qwen3.5-122b, minimax-m3). The chain's
  "no nodes → try next" rule handles it; such models must not occupy chain slots.
- **Chains are probe-derived and latency-ordered.** The configured
  `apiAssistedProviders.nvidia` chains come from a 22-candidate one-by-one sweep; entries
  rotted within ~24h of the initial research (llama-3.3-70b went from documented to
  timing out >180s). Treat model lists as perishable, measurement-derived config.
- **Client retry earns its keep.** 429/5xx/timeout retries with `Retry-After` support
  (`GRAPHIFY_API_RETRIES`, `GRAPHIFY_API_TIMEOUT`) turned two would-be chain failures into
  successes on the first live day.
- Re-measurement is backlog item **P1 `providers probe`**
  (`docs/IMPLEMENTATION_BACKLOG.md`, M2W follow-ups); until it lands, re-run the sweep
  manually when a chain starts falling through. Last full sweep: 2026-07-09.
