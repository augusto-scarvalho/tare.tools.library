# Implementation Plans — RD-TAINT (Taint / CaMeL, Secret Never Egresses)

Plans parked in the backlog (owner 2026-07-19: “make the plans very detailed, prioritize RD-TAINT because
of the dependencies”). Derived from `rd-taint-camel-round.md` (5 NVIDIA ideators) + D023.
**Priority:** **N-PTC-TAINT4** (PTC’s 4th sink) EXTENDS the envelope defined here — without this, the PTC
engine reopens the secret-egress gap.

**Existing machinery to reuse (DO NOT reinvent):**
- `scripts/harness_lib/secret_scan.py` — secret scan already detects secret SHAPE at worker boundary and
  RETAINS the result. It is **half-taint** (detection at sink) — the seam extended by the sinks.
- `scripts/harness_lib/records.py` — **subject dimension** (`subject=` in records/append_event): provenance
  self vs target, already attributable.
- `.harness/routing/executors.json` — **trust tiers** (first-party/third-party) = CaMeL-like capabilities.
- GM-3 provenance firewall (`memory-context-management.md`: `authority >= signed_policy`) = control-plane
  gate reused by CaMeL.
- `append_event` (hash chain) — hook for the non-forgeable envelope to enter as a signed event.

**Honest ceiling (declared by all 5 ideators; repeat in every plan):** EXPLICIT taint marks the SOURCE,
not derived content. If the LLM PARAPHRASES a secret, taint does not follow. **Defense in depth, not proof.**
Shape-based secret scan catches patterns, not semantic laundering.

---

## N-TAINT-PROBE — “would-block” probe · BUILDABLE NOW (measure-only) · size M

**Goal:** measure HOW MANY tainted values (secret-read/web-fetch/worker-output) WOULD REACH an egress sink
today — before any enforcement. Measure-before-control: if almost nothing would egress, enforcement remains
measure-only (destination of C9); if much would, the envelope is justified.

**Reuse:** `secret_scan.py` (already detects shape at sink); `records`/`append_event` (provenance).

**Approach:**
1. **Probe** (`testing/probes/taint_reach_probe.py`, sibling of truth-divergence): over a corpus of real
   WORKER_RESULTs + vendor prompts + logs, shadow-source-stamp what IS tainted by origin (secret-read =
   matched secret scan; web-fetch = came from discovery; worker-output = subprocess) and count how many
   WOULD reach each sink (prompt/persisted/log) WITHOUT blocking today.
2. **Deterministic, zero LLM:** reuse secret scan as classifier for “is tainted”; “would reach a sink” is
   set membership (value appears in text headed for sink). Log counts + hashes/samples (NEVER raw value —
   the probe itself must not leak).
3. **Reduction:** by source type × sink, fraction that would egress; L13 noise floor; verdict.

**Footprint:** `testing/probes/taint_reach_probe.py` (new, self-check). Adds NO enforcement.

**Acceptance:** probe runs over ≥20 real WORKER_RESULTs/prompts, produces table `(source × sink) →
fraction-that-would-egress` with noise-floor gating, ZERO raw values logged, ZERO enforcement.

**Gate:** measure-only, measure-first authority. **Dependency:** secret_scan (exists). **Size:** M.

---

## N-TAINT-ENVELOPE — non-forgeable envelope · OWNER-GATED (security) · size L

**Goal:** the core — NON-FORGEABLE taint metadata injected by the HARNESS (never by worker), stamped at
source, traveling with data. This is the only way in a subprocess+JSON model (worker writes arbitrary JSON →
inline marker would be forgeable).

**Reuse:** records subject dimension (provenance exists); `append_event`/hash-chain (signed envelope);
secret scan (secret-read source detector).

**Approach:**
1. **Source stamp** at 3 origins: `secret_read` (matched secret scan when read), `web_fetch` (came from
   discovery/WebFetch), `worker_output` (produced by untrusted subprocess). HARNESS stamps — outside
   worker-controlled WORKER_RESULT (wrap/sign, not inline field).
2. **Transport:** taint travels in a harness-wrapped envelope around the value (key outside worker control).
   Optionally enters hash-chain (critical event) to resist rewriting.
3. **taint_map:** harness maintains value→{sources, at, subject} map — consulted by sinks.

**Footprint (when opened):** `harness_lib/taint.py` (envelope + source stamp + taint_map); source-stamp
points (secret-scan seam on read; discovery on web-fetch; subprocess on worker-output). NEW spec door
(SPEC-116) + scenario (worker cannot forge; stamp survives JSON).

**Acceptance:** a secret-read value carries taint envelope worker CANNOT remove/forge; taint_map resolves
source+provenance. **Gate:** OWNER-GATED + security review. **Dependency:** N-TAINT-PROBE (justifies it).
**Size:** L.

---

## N-TAINT-SINKS — fail-closed sink enforcement · OWNER-GATED (security) · size M

**Goal:** block egress — tainted data reaching a sink BLOCKS/redacts by default. **Extends secret scan**
(which is already half-taint) to check `taint_map`, not just shape.

**Reuse:** `secret_scan.py` (the seam — today detects shape; also checks taint_map).

**Approach:**
1. **Sinks (D023):** (1) prompt to vendor, (2) persisted WORKER_RESULT, (3) log. **+ PTC’s 4th sink
   (N-PTC-TAINT4): sandbox stdout/stderr** — same checker, one more call site (why this item precedes PTC engine).
2. **Fail-closed:** tainted at sink → block/redact (audited break-glass for deliberate egress, parallel to
   sandbox_prepare SPEC-151).
3. **Robustness (w-002/w-003):** check O(reachable-tainted-fields) (not O(all)); break-glass rate-limited/
   batched (avoid append_event flood); rollback partial write (no half-redacted egress); **checker itself
   fail-closed** (if taint-check crashes, unredacted data does NOT egress).

**Footprint (when opened):** extend `secret_scan.py` (check taint_map) + 3 (→4) sink call sites; security
scenario (tainted at each sink → blocked; checker crash → fail-closed).

**Acceptance:** tainted value NEVER egresses through 3 (→4) sinks without break-glass; crashing checker
fails closed. **Gate:** OWNER-GATED + security review. **Dependency:** N-TAINT-ENVELOPE. **Size:** M.
**⚠️ Key dependency:** **N-PTC-TAINT4** = 4th sink here; build this BEFORE PTC engine.

---

## N-TAINT-CAMEL — control-plane capabilities · OWNER-GATED · size M

**Goal:** CaMeL’s value WITHOUT heavy runtime — map only the split control plane (policy/capability) vs
data plane (values), reusing what is already capability-like.

**Reuse:** trust tiers (`executors.json`: first-party/third-party); GM-3 authority
(`authority >= signed_policy`) — both are already capability-like constraints.

**Approach:** control plane = which sources/tiers may produce data that egresses (policy); data plane =
values (taint_map). NOT a per-value IFC runtime — decision is GM-3 authority + executor trust tier.
Example: data from third-party worker (low trust tier) + secret-read = egress denied by policy, not flow analysis.

**Footprint (when opened):** connect taint_map to GM-3 authority + trust tiers at sink decision point;
scenario (control-plane policy denies low-tier + secret egress). **Acceptance:** egress decision is
authority/tier (control plane), not flow runtime. **Gate:** OWNER-GATED. **Dependency:** N-TAINT-SINKS + GM-3.
**Size:** M.

---

## Suggested order (and PTC dependency)
1. **N-TAINT-PROBE** — buildable; measure whether egress is real before building control.
2. **N-TAINT-ENVELOPE** — non-forgeable core.
3. **N-TAINT-SINKS** — enforcement; **includes hook for the 4th sink used by N-PTC-TAINT4** → THIS is the
   PTC engine security prerequisite (N-PTC-ENGINE does not ship without sinks + the 4th).
4. **N-TAINT-CAMEL** — control-plane policy above it.

> Cross-round dependency chain: **N-TAINT-ENVELOPE + N-TAINT-SINKS → N-PTC-TAINT4 → N-PTC-ENGINE.**
> That is why RD-TAINT was prioritized.
