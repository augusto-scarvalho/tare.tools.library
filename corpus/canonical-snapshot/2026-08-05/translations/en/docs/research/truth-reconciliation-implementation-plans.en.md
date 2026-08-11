# Implementation Plans — Truth-source Reconciliation (N-TRUTHRECON-*)

Parked in the backlog. Derived from `truth-reconciliation-round.md` (5 NVIDIA ideators) + D020.
**Already built:** N-TRUTHRECON-PROBE = EXP-22 = the truth-divergence probe (`testing/probes/
truth_divergence_probe.py`, commit `6dd9472`) — measures doc↔code divergence; NOT listed here.

**Reuse:** git (`git ls-files` = authoritative tier); `records` (history); `specs/` + vendor docs
(advisory tier); GM-3 provenance firewall (`authority>=signed_policy`); T-HASHCHAIN (tamper evidence);
`secret_scan.py` (for N-SCANNER-FP). DNS (RFC 1035/2181/4035/2308) = reference architecture.

---

## N-TRUTHRECON-CORE — reconciliation engine · OWNER-GATED (control) · size L

**Goal:** the PrecedenceResolver — a PURE function that deterministically reconciles divergent sources.
It is control → only after EXP-22 demonstrates that the divergence is material (destination of C9).

**Approach:**
1. **2 TIERS (w-001):** AUTHORITATIVE = git+records (share hash-chain); ADVISORY = specs+vendor
   (without cryptographic provenance). “preferred doc” = tier mapping (specs in the high tier), NOT a
   runtime rule. `resolve(sources: Map<SourceId, SourceState>) -> ReconciliationRecord` — zero state,
   zero LLM (same input → same verdict + trace; the LLM helped DESIGN it, never compute it).
2. **ReconciliationRecord** (fields converged from w-001+003+004): `{fact, winningSource, loserSources[],
   precedenceRuleApplied, tier, degraded:bool, absentSources[], inputHashes{}, at, subject}` + inherits
   metadata from the provenance firewall (GM-3). `precedenceRuleApplied` is the “never blind” field
   (records WHY).
3. **Emergent degradation:** missing source = skipped (absent key in Map) + recorded in `absentSources`.
4. **DNS terminology (w-005):** SOA-serial=divergence; TTL=confidence; NXDOMAIN-negative-cache=never
   record doc>code precedence silently; DNSSEC=GM-3 gate.

**Footprint (when opened):** `harness_lib/reconciliation.py` (pure resolver + record); consultation points
(where the harness reads a “fact” from multiple sources); NEW spec door + scenario (same input → same
record; missing source → degraded naming it; doc>code → applied precedence rule recorded).

**Acceptance:** resolver is deterministic (same input → byte-identical record); degradation names the
missing source; applied precedence is recorded. **Gate:** OWNER-GATED (control; EXP-22 must justify it).
**Dependency:** N-TRUTHRECON-PROBE (EXP-22, done). **Size:** L.

---

## N-TRUTHRECON-TRUST — boundary hardening · OWNER-GATED · size M

**Goal:** address the 3 security findings from w-004 (record/probe/degradation are sensitive surfaces).
Fold into N-SECREVIEWER (D014).

**Approach:** (a) `absentSourceName` is a **side channel** (reveals which subsystem failed) → expose only
to an authorized role; (b) **vendor/third-party docs = UNTRUSTED input** → sandboxed parsing (reuse
SPEC-151); (c) ReconciliationRecord inherits provenance-firewall metadata from GM-3.

**Footprint (when opened):** integrate with N-TRUTHRECON-CORE (record + vendor parsing); security scenario
(absentSource only visible to authorized role; vendor doc parsed in containment).
**Acceptance:** absentSource side channel is gated; vendor docs are parsed in containment. **Gate:**
OWNER-GATED. **Dependency:** N-TRUTHRECON-CORE. **Size:** M.

---

## N-SCANNER-FP — secret-scan fix (bonus finding from the round) · OWNER-GATED (security path) · size S

**Goal:** the secret-scan `openai-style-key` pattern matches `sk-` INSIDE “ta**sk-**slug” → it swallowed
2 valid results from round #3. Fix = word-boundary-style anchor before `sk-`.

**Approach:** in `secret_scan.py`, add `(?<![\w-])` before `sk-` in the `openai-style-key` regex (or an
equivalent) so it does not match inside “task-”/“disk-”/etc. A test with “task-reconciliation” (the real
false positive) proves it no longer matches; a realistic `sk-<20+>` still matches.

**Footprint (when opened):** `secret_scan.py` regex + one test. **Acceptance:** “task-slug” is no longer
flagged; a real key still is. **Gate:** OWNER-GATED (security path → isolated review; do not loosen it so
real keys slip through). **Dependency:** —. **Size:** S.

---

## Suggested order
1. **N-SCANNER-FP** — trivial, removes the FP that interferes with rounds (but security path → review).
2. **N-TRUTHRECON-CORE** — only when EXP-22 (already measuring) shows divergence above the noise floor.
3. **N-TRUTHRECON-TRUST** — with/after CORE, folding into N-SECREVIEWER.
