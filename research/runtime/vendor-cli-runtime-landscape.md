# Vendor CLI / Agent Runtime Landscape — comparative preservation edition

**Status:** RESEARCH / market archaeology. Current product behavior must be rechecked before operational use.

## Research question

What do Codex, Claude, Gemini/Antigravity, Kimi, Qwen/other CLIs and open meta-harnesses actually own: inference, agent loop, context, tools, process lifecycle, sandbox, approvals, UI or remote execution?

## Patterns preserved

1. **Vendor-local agent CLI:** vendor owns loop and often tool orchestration; tare needs adapter, capability/authority boundaries and runtime evidence.
2. **Inference endpoint:** provider owns model serving; tare can own HarnessAgentRuntime, making semantics more native.
3. **Managed/remote agent:** lifecycle/effects may be partly opaque; requires federation/qualification/reconciliation.
4. **Meta-harness/open runtime:** useful source of implementation mechanisms, but should not become tare's ontology by adoption.

## Comparative dimensions

Context assembly, tool schema/discovery, approval model, shell/filesystem semantics, hooks, subprocess ownership/cancellation, resumability, remote sessions, model selection, telemetry, artifact handling, MCP/A2A exposure, non-interactive/REPL interface and failure behavior.

## Architectural result

There is no need for a “winning runtime”. The useful output is a pattern→canonical-equivalent→bounded-owner→qualification matrix. `ToolBroker`-like vendor nouns converge toward Capability; vendor model/session names become ExecutionBinding/runtime metadata; wire logs normalize into HarnessEvents/evidence rather than becoming truth.

## Empirical anchor

The Kimi/Antigravity false-green case is retained separately because it demonstrated that static configuration and real runtime capability diverge.
