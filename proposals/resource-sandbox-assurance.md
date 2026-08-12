# Resources, Sandbox & Assurance — technical proposal

[← Adaptive Routing proposal](adaptive-routing.md) · [Research basis](../research/runtime/capability-sandbox-resources.md) · [Navigation](../NAVIGATION.md)

**Status:** PROPOSED.

## Problem-specific integration

Resource constraints, workspace isolation and assurance meet at execution eligibility but should not become one monolithic Plane.

## Semantics

- resource inventory/state constrains scheduling;
- WorkspaceLease constrains ownership/scope/lifetime;
- sandbox backend enforces isolation mechanism;
- Authority decides whether an effect is permitted;
- evidence proves what confinement/effect actually occurred.

## Candidate experiments

Windows-native vs POSIX sandbox profiles; deep-path behavior; process-tree cancellation; filesystem writable-root leakage; secret/path filtering; local GPU headroom under concurrent work; offline durable execution; container/WASM backends; evidence that config/load/enforcement/effect all align.

## Gate

“Sandbox enabled” or “containerized” is not a proof claim. Qualification must state which confinement properties were actually exercised and observed.

---

**Previous:** [Adaptive Routing proposal](adaptive-routing.md) · **Next evidence:** [Kimi/Antigravity capability case →](../case-studies/vendor-runtime/kimi-antigravity-capability-parity.md) · **Back to proposal index:** [Technical Proposals](README.md)
