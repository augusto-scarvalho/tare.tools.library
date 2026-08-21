# RD-TAINT Round — Untrusted-Data Taint / CaMeL (Secret Never Egresses)

Research-gated backlog item RD-TAINT. Third and final of the 3 implementation-research rounds
(owner 2026-07-19). Prerequisite Q7-1 (sandbox SPEC-151) ✅ shipped. Orchestrator = this session.
Divergence via **NVIDIA** (`nvidia-compat`, glm-5.2).

## Why this round exists

Article §7.1 o2: **data that has been secret-read must never egress** (leave for a vendor, the web, or a
persistent log). The sandbox (Q7-1) contains the PROCESS (filesystem/network by tier), but does NOT track the
DATA: a worker can read a secret and, inside its permitted tier, send it to the vendor API in the prompt.
This is the gap the sandbox does not catch — it needs **taint tracking** (mark untrusted/sensitive data and
block egress), in the style of **CaMeL** (capabilities/data-flow line for LLM agents). Research on HOW TO
IMPLEMENT lightly, not measurement.

## Round question

> How do we implement **lightweight taint tracking** in the harness so that data marked secret-read (or
> untrusted: web-fetched, worker-produced) **never egresses** — in a Python subprocess/JSON system, without a
> heavy dataflow runtime, reusing the existing secret scan + subject dimension + trust tiers?

## Success criteria

- **Actors:** worker (produces/reads tainted data), harness (blocks at egress point), owner (audited
  break-glass if egress is REQUIRED).
- **Lightweight and Python-real:** no bytecode instrumentation / heavy dynamic taint; something that works at
  the I/O boundary (where data exits — prompt to vendor, persisted WORKER_RESULT, log). Taint as METADATA
  traveling with data, not interpreter-flow analysis.
- **Fail-closed at egress:** tainted data reaching an output sink → BLOCK (or redact) by default; egress only
  with audited break-glass (parallel to sandbox_prepare fail-closed).
- **Reuse what exists:** **secret scan** (already detects secret shape at worker boundary — half-taint),
  **subject dimension** (data provenance), **trust tiers** (first-party vs third-party in executors.json),
  GM-3 provenance firewall (authority). Use CaMeL only where it pays.
- **Honest ceiling:** explicit propagation taint (mark at source, check at sink) DOES NOT catch implicit
  laundering (LLM paraphrases the secret). Declare this limit — defense in depth, not proof.

## Budget + breadth + declared design

- **Wave 1:** 5 NVIDIA ideators, ceiling ~65k tokens (free tier). Gate at 60%.
- **Breadth (D010): EXPLORATORY → 5.** Taint/IFC crosses information-flow control, CaMeL/capabilities for
  LLMs, classic taint analysis (Perl/Ruby), DLP and provenance — broad field.
- **Design (L18):** SECURITY round (closes o2 gap). May generate a measure-only probe (“how many tainted data
  items would reach a sink today?”) before enforcement — measure-before-control. Shadow/measure advisory now
  fires (e5a1a4b); final card in synthesis.

## Phase 3 — wave-1 brief

> Design LIGHTWEIGHT harness taint tracking so that secret-read data (or untrusted: web-fetched,
> worker-produced) NEVER egresses (prompt to vendor, persisted WORKER_RESULT, log). Real context: workers are
> Python subprocesses exchanging JSON; we already have (1) secret scan detecting secret shape at worker
> boundary, (2) subject dimension (provenance: self vs target), (3) trust tiers (first-party/third-party in
> executors.json), (4) GM-3 provenance firewall (`authority>=signed_policy`). It must: (1) be LIGHT — taint as
> METADATA traveling with data (mark at source, check I/O sink), NOT bytecode instrumentation / interpreter
> dynamic taint; (2) FAIL-CLOSED at egress — tainted data at an output sink BLOCKS/redacts by default, egress
> only with audited break-glass (parallel to sandbox_prepare); (3) REUSE those 4 mechanisms instead of a new
> subsystem; (4) map into CaMeL (LLM capabilities/data-flow) ONLY where it pays. Deliver concretely: TAINT
> MODEL (what marks source, how metadata travels through WORKER_RESULT JSON, where EGRESS SINKS are),
> fail-closed ENFORCEMENT point, and honest CEILING (explicit taint does not catch implicit laundering when
> LLM paraphrases a secret — defense in depth).

---

# Phases 3–5 — Result and Synthesis (RD-TAINT)

Wave 1: `WF-20260719-060140-203270`, 5 NVIDIA ideators (glm-5.2). Strongest convergence of the 3 rounds —
all 5 on the same model, including the same security insight and honest ceiling.

## Unanimous convergence (5/5)

**Taint = NON-FORGEABLE metadata ENVELOPE** that:
1. **Marks at source** in 3 origins: `secret_read` / `web_fetch` / `worker_output`.
2. **Travels in an envelope injected by the HARNESS, OUTSIDE worker control** — the security insight all 5
   reached independently: because worker writes arbitrary JSON in WORKER_RESULT, an INLINE taint marker is
   FORGEABLE (worker omits it). The envelope must be wrapped/signed by harness, never a worker-emitted field.
3. **Fail-closed enforcement at egress sink = EXTEND existing secret scan** (already “half-taint”: detection
   at sink). 3 sinks: prompt to vendor, WORKER_RESULT persistence, log. Block/redact by default; egress only
   through **audited break-glass** (parallel to sandbox_prepare SPEC-151).

**CaMeL (consistent 5/5):** map only the **control-plane** split (taint policy + capability/authority) vs
**data-plane** (values). Restrict to control plane by reusing trust tiers + GM-3
`authority>=signed_policy` (already capability-like); DO NOT build per-value IFC runtime (too heavy at our
scale).

**Honest ceiling (all 5 declared — discipline):** explicit taint marks SOURCE, not semantically derived
content. If worker reads the secret and LLM PARAPHRASES it into new text, taint does not follow paraphrase.
**Defense in depth, not proof.** Shape-based secret scan catches patterns, not semantic laundering.

## What each perspective added

- **w-001 (simplicity):** 3 moving parts (source stamp, envelope, sink enforcement); footprint = 1 envelope
  type + 1 check function + 1 audit event.
- **w-002 (scale):** check is **O(reachable-tainted-fields)**, not O(all fields) — critical for large results
  (file lists, test output). Break-glass audit must be **rate-limited/batched** (fork-join with N workers
  hitting break-glass would flood append_event). Dominant cost already shape-match from secret scan; taint
  adds O(1) marginally.
- **w-003 (reliability):** fail-closed egress needs **partial-write rollback** (avoid half-redacted egress);
  if taint checker itself CRASHES, result does NOT egress unredacted (checker itself fails closed); structured
  audit.
- **w-004 (trust boundary):** **signed** envelope (non-forgeable transport); extend secret-scan seam to check
  `taint_map`, not just shape.
- **w-005 (analogy): three proven references** — **email Content-Disposition/X-Header** (metadata travels
  with payload, checked at egress MTA boundary) = exact isomorphism; **postal customs declaration**
  (stamped at origin, checked at border, immutable in transit) = source envelope; **OAuth/OIDC capability
  tokens** (scopes restrict what token CAN DO = CaMeL data-flow capabilities).

## Operation

| card | operation | why |
|---|---|---|
| **TAINT-ENVELOPE** (non-forgeable harness-injected metadata) | **kept** — core | worker cannot forge it; only workable model for subprocess+JSON |
| **TAINT-SINK** (extend secret scan to check taint_map, fail-closed) | **kept** | reuses seam already half-taint; zero parallel subsystem |
| **CaMeL control-plane-only** (trust-tiers+GM-3 as capabilities) | **kept** | captures CaMeL value without heavy runtime |
| **rate-limited break-glass + rollback + checker-fail-closed** | **split (robustness rules)** | w-002/w-003; enter spec |
| **per-value IFC runtime / bytecode dynamic taint** | **rejected** | too heavy; I/O boundary is where taint should live |

## Buildable vs owner-gated

- **Buildable (measurement):** measure-only probe — “how many tainted values WOULD REACH an egress sink
  today?” — reusing secret scan (measure-before-control, like truth-divergence probe). Zero enforcement.
- **Owner-gated (security):** fail-closed egress enforcement is a SECURITY CONTROL + defense in depth →
  owner-gated + deserves security review (like N-SCANNER-FP). Design is ready; measure-only probe is step 1.

## Traceability

| Evidence | Idea | Experiment | Task | Status |
|---|---|---|---|---|
| 5/5 (non-forgeable envelope) + email X-Header/MTA (w-005) | TAINT-ENVELOPE + TAINT-SINK | measure-only probe (would-block count) | RD-TAINT→taint | designed; probe buildable, enforcement owner-gated |
| 5/5 (laundering ceiling) | declared limit | — | — | defense in depth, not proof |
