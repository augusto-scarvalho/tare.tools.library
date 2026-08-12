# Agent OS Foundations — preservation edition

**Status:** RESEARCH synthesis constrained by TARGET North Star; not canonical authority.

## Problem

The historical harness accumulated routing, agents, tools, sandboxes, workflows, policy, evidence and UX. The scientific question is not how to centralize them under a super-agent, but how to give them stable ownership and contracts while preserving vendor/runtime diversity.

## Surviving thesis

The strongest architectural analogy is **exokernel/library-OS + capability security + durable workflow**, not a reimplementation of Windows/Linux. tare.tools should own canonical meaning and governance in user space while host OSes/vendors/frameworks own mechanisms.

## Essential separations

- Model ≠ Provider ≠ Provider Route ≠ Runtime ≠ Runtime Owner ≠ Commercial Lane.
- Agent loop ownership may be vendor-local, harness-owned or vendor-remote.
- Authority is deterministic and precedes routing/intelligence.
- Capability/Effect is the effect boundary; MCP is one possible backend/protocol.
- Evidence/Provenance outlives telemetry and vendor turnover.
- Experience surfaces project canonical state; they do not own it.

## Stable incumbent and migration

The incumbent is executable historical specification. Preferred migration remains Strangler + Branch by Abstraction: introduce canonical contracts/adapters first, prove parity, shadow/canary, preserve rollback, remove legacy only against explicit evidence.

## Anti-Frankenstein test

For every external engine ask: if removed tomorrow, do we lose convenience/performance, or do we lose the ability to interpret our own Task/Authority/Effect/Evidence? The latter means semantic capture.

## Research retained

This edition preserves the North-Star reasoning from the formal architecture/routing program, the Agent OS scientific consolidation, runtime ownership archaeology and subsequent lineage/reconstructability research. The byte-preserved 2026-08-11 Agent OS scientific refresh remains under `bridge-editions/` for deeper historical comparison.

## OPEN

Constitutional/root authority; architecture epoch semantics; project inventory; trusted invocation boundary; temporal compatibility; which nouns deserve primitives versus derived roles.
