# Runtime Ownership & Vendor Integration

**Status:** RESEARCH with strong TARGET alignment.

## Three runtime classes

- **vendor-local:** vendor owns the agent loop; tare adapts/governs/observes.
- **harness-owned:** provider supplies inference; tare owns agency via HarnessAgentRuntime + ModelProviderAdapter.
- **vendor-remote:** managed/remote agent runtime with its own lifecycle; tare federates.

The classes converge through external canonical contracts, not identical internals.

## Why this matters

CLIs and HTTP endpoints are not asymmetric defects. A CLI can bring its own loop and tools; an inference endpoint can become more tare-native precisely because the harness owns context, tools, cancellation, Authority and evidence.

## Candidate/binding identity

Model, Provider, Provider Route, Runtime, Runtime Owner and Commercial Lane remain distinct. ExecutionBinding is the likely seam where a RouteDecision becomes concrete: runtime/adapter/provider versions, qualification refs, authority refs and protocol metadata are pinned there.

## Qualification progression

Runtime capability should be evidenced beyond static config. Historical vendor archaeology suggested levels such as declared/rendered/loadable/enforced/effective. Treat this as a qualification concept, not yet a mandatory canonical enum.

## Windows/local first

Windows-native behavior and POSIX/CI are both requirements. Local HTTP inference and consumer-GPU runtimes are first-class, not fallback curiosities.

## OPEN

Trusted invocation seam; process/filesystem confinement proof; remote lifecycle semantics; candidate identity for quantized/local configs; degraded/offline qualification.
