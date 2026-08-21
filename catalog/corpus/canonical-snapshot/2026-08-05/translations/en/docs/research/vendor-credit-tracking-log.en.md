# Research Log — Vendor Credit Meter (N-VENDORCREDIT / D017)

Item #5 (owner: “research vendor docs + test empirically; keep testing and taking notes; when we get
somewhere, we review together”). Incremental log — every research/test round appends here.

## Increment 1 (2026-07-19) — docs for 3 vendors: FINDING THAT CHANGES THE DESIGN

I researched all 3 vendor docs. **Key conclusion: 2 of 3 vendors DO NOT expose credit balance
programmatically.** The “fuel gauge” we imagined (ask “how much is left?”) largely DOES NOT EXIST:

| vendor | balance via API? | usage via API? | exhaustion signal | source |
|---|---|---|---|---|
| **Anthropic** (claude) | **NO** — `GET /v1/organizations/balance` → 404; open feature request (#47574) | YES — Usage & Cost Admin API (requires Admin key, ≠ normal key) | quota error | platform.claude.com/docs/en/manage-claude/usage-cost-api |
| **NVIDIA Build** (nvidia-compat) | **NO** — no endpoint; users report balance not even visible in UI | undocumented | **HTTP 402** with clear exhaustion message | forums.developer.nvidia.com |
| **OpenAI** (openai-compat) | partial — `GET /v1/dashboard/billing/credit_grants` (dashboard, usually session token, NOT API key; unstable) | `GET /v1/usage?start_date&end_date` | auth/quota error | community.openai.com |

## The reframe (architect)

Because balance cannot be QUERIED reliably, the robust N-VENDORCREDIT design is NOT “read the gauge” — it
is **estimate the tank + detect empty**:

1. **Track local SPEND** (already have: delegation ledger). T-ADAPTERCONF delivered prerequisite:
   `accountingSemantics` says which vendors report tokens RELIABLY (codex + openai-compat family fail c9 →
   their number is estimated, not measured — so their tank estimate is coarser).
2. **Owner-declared initial balance** per vendor (e.g. “NVIDIA: 1000 credits”; “Anthropic: $X”) — a number
   YOU provide (because vendor does not), decremented by tracked spend. It is an honest ESTIMATE, labeled as
   such (not vendor truth).
3. **Empirical exhaustion detection** through error codes — NVIDIA 402, OpenAI auth/quota, existing
   `rateLimitPatterns`/`authFailurePatterns` in executor cards (`executors.json`). When error matches, the
   tank REALLY is empty (vendor truth, even if late). Breaker already reacts.
4. **Low-tank alert** = estimate (spend vs declared balance) crossing threshold → warning before 402,
   explicitly caveated as estimate.

This fits D017 (U weighted by scarcity): scarcity ruler uses the tank ESTIMATE, and breaker/402 is the
truth backstop.

## Empirical tests to run (next increments — “keep testing and noting”)
- [ ] Prove NVIDIA 402: capture exact exhaustion response shape (only happens when credits actually end —
      or force with expensive paid model; otherwise record when it naturally occurs during a wave).
- [ ] Test whether Anthropic Usage & Cost Admin API responds with our key (is it an Admin key? do we have
      one?) — if yes, reconcile real Claude spend.
- [ ] Test `GET /v1/dashboard/billing/credit_grants` against OpenAI proper (if we have a real OpenAI key,
      not only NVIDIA/Gemini compat) — note whether API key works or session-token is required.
- [ ] Confirm current `authFailurePatterns`/`rateLimitPatterns` in executors.json cover real exhaustion
      messages for all 3.

## Increment 2 (2026-07-19) — owner’s `/usage` idea: BETTER than the reframe

Owner: “each provider has a `/usage` shortcut; we could spawn very cheap specific workers to use it and
report how much remains from time to time.” **This works better than estimating the tank** — instead of
calling a nonexistent balance API, use the VENDOR’S OWN TOOL that ALREADY shows what remains:

- **claude** (Claude Code): has `/usage` — shows session/org usage/limits. A cheap worker (Haiku, minimal
  prompt) runs and reports. WORKS for CLI vendors.
- **codex:** likely has a usage equivalent in CLI — test empirically.
- **NVIDIA/gemini** (pure HTTP, no CLI): DO NOT have `/usage` — retain increment-1 reframe
  (spend tracking + 402/error). Therefore **HYBRID approach by vendor class** — CLI vendors use native
  `/usage`; HTTP vendors use spend+error.

**Revised N-VENDORCREDIT design (with owner idea):**
1. **CLI vendors (claude, codex):** periodic probe spawns a cheap worker that runs native `/usage` and
   parses output → REAL vendor number, cheaply, without estimate. This is the real “fuel gauge” for them.
2. **HTTP vendors (nvidia, gemini, openai-compat):** local spend tracking (delegation ledger +
   T-ADAPTERCONF accountingSemantics) + 402/quota detection. Estimate + backstop.
3. **Cadence:** “from time to time” — lightweight schedule/loop (harness already has `/schedule` and
   `/loop`) runs usage probe, records in ledger, alerts on low tank.

Empirical tests: [ ] confirm `claude /usage` output shape (what to parse); [ ] find codex equivalent;
[ ] measure cost of a usage worker (should be cents-scale).

## What I need from you (when we review together)
- **Declared initial balance** of each vendor you want tracked (the number vendor does not provide). With
  that, tank estimate becomes real enough to operate.
- Confirm whether we have an **Anthropic Admin key** (≠ normal key) — the only way to reconcile real
  Claude spend through that API.

## Sources
- Anthropic Usage & Cost API: https://platform.claude.com/docs/en/manage-claude/usage-cost-api ; balance 404 / feature request: https://github.com/anthropics/claude-code/issues/47574
- NVIDIA Build credits + 402: https://forums.developer.nvidia.com/t/api-credit-balance/309857 ; https://decodethefuture.org/en/nvidia-nim-api-explained/
- OpenAI billing endpoints: https://community.openai.com/t/get-the-remaining-credits-via-the-api/18827
