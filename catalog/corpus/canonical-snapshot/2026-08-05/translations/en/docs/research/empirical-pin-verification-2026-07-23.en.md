# Reliability of Distilled Operational Knowledge: Empirical Verification of Playbook Pins

Round 2026-07-23 (owner request). Format: internal scientific report. Methodological companion to `opus-overseer-quality-2026-07-23.md` (§2.4 of that report declares the same conflict-of-interest regime; same applies here).

## Abstract

The overseer playbook accumulates "pins" — empirical claims distilled from incidents (costs, sandbox capabilities, CLI behavior) that then govern routing and spending. On 2026-07-23, three pins were refuted in sequence after direct owner challenges, all with the SAME root cause (an argument mangled by a shell layer, incorrectly attributed to a capability limitation). In response, the owner ordered a systematic audit of the remainder. We built a queue of 10 pins with pre-registered cheap tests and risk-if-false, and delegated re-verification to a Sonnet worker under a methodological isolation contract. Result: **9/10 confirmed, 1 refuted** (P7: gate duration drifted from "7–15 min" to ~5–6 min typical after parallel flip D041). Central meta-finding: the audit worker itself reproduced BOTH trap classes that had broken the original pins (stdin already at EOF; MSYS mangling of `/usage`) and converted false verdicts into correct ones by applying the required isolation discipline — evidence that the method is transferable, not idiosyncratic. Stratified falsehood rate: pins born from ONE unisolated failure observation: 3/3 false; pins born from deliberate measurement or source inspection: 9/10 true (the only false one was temporal drift, not origin error). Structural lesson: **how a pin is born predicts its reliability better than its age**.

## 1. Context and question

Pins are the harness's operational memory: "X costs ~$0.37", "Y hangs unless stdin is closed", "Z does not run in the sandbox". They decide lane routing, probe cadence and security posture. Question for this round: *how many active pins are false, and what makes them false?*

Trigger: three owner challenges on the same day, three refutations:

| refuted pin | recorded claim | real cause (probe-proven) |
|---|---|---|
| R1 | "Claude `/usage` is interactive-only; percentage impossible non-interactively" | Git Bash/MSYS mangles `/usage`→Windows path; through subprocess list-args the panel renders (and at ~$0 on pinned Haiku) |
| R2 | "Codex cannot spawn browser (EPERM)" | the `--sandbox workspace-write` flag IN OUR RECIPE blocks process spawn; owner interactive use works; proven with 2 probes (binary in-workspace still EPERM ⇒ spawn restriction, not path restriction) |
| R3 | "Codex has no network (ENOTCACHED)" | direct fetch from sandbox → HTTP 200; ENOTCACHED came from nested PowerShell→cmd quoting where `^` is an escape, mangling semver `@^6.12.2` |

All three share the same signature: **one failure observed through a shell layer; the layer mangled the argument; the mangling was attributed to the tool's capability**. None of the claims was true about the tool; all were true about the plumbing between us and it.

## 2. Methods

### 2.1 Pre-registered queue

We extracted the 10 remaining empirical pins from the playbook (`.harness/handoff/playbook-pin-audit-queue.md`), each with: literal claim, pre-specified cheap test, and risk-if-false (what it would route or spend incorrectly). Pre-registering the test BEFORE execution follows the construct-metrics R4 discipline (`construct-metrics.md`: pre-registered definition before measurement — exactly the practice whose absence produced finding F4 in the opus-overseer report).

### 2.2 Worker contract

Sonnet 5 worker (debugger), with explicit contract: (a) probes only on `gpt-5.6-terra` / `claude-haiku` ($0.05 cap; above ⇒ OWNER-GATED, do not run); (b) **mandatory isolation discipline:** never conclude from one symptom — re-probe through an alternative quoting route (subprocess list-args) before declaring the CLAIM false; (c) honest UNTESTABLE verdict preferred to guessing; (d) verbatim evidence per pin. P1 (hang claim) was tested under `timeout 60` so a real hang would not trap the worker.

### 2.3 Limitations

n=13 pins (3+10), one environment (Windows/MSYS/PowerShell — quoting traps are specific to this stack); expensive half of P3 (comparison with Fable) remained owner-gated by cost; self-audit within same session (mitigated by: external worker + owner challenges as independent trigger + every refutation re-verified at source by overseer before acceptance).

## 3. Results

### 3.1 Queue verdicts (worker, re-verified by overseer)

| pin | claim | verdict | note |
|---|---|---|---|
| P1 | open stdin hangs `codex exec` | CONFIRMED | naive probe produced a false negative (Bash-tool stdin already EOF); isolated probe confirmed hang |
| P2 | Codex ≥0.144 ignores local `.codex/config.toml` | CONFIRMED | new nuance: `--profile` reads `$CODEX_HOME/<name>.config.toml` AND requires repo in trust registry — two isolation variables beyond quoting |
| P3 | fuel probe on pinned Haiku ≈ $0 | CONFIRMED | naive probe REPRODUCED MSYS mangling live (the exact pre-fix bug); isolated probe confirmed ~0 cost |
| P4 | `codex login status` is free | CONFIRMED | no model turn |
| P5 | pw_ui_smoke kills server (no orphans) | CONFIRMED | |
| P6 | packet worker never echoes key | CONFIRMED | race with fake key; absent from stdout/logs |
| **P7** | **gate takes 7–15 min** | **REFUTED** | reality: ~5–6 min typical after parallel flip D041 (2026-07-21); contention outliers up to ~21.5 min. Corrected in CLAUDE.md via sanctioned protected-file edit |
| P8 | D039 briefs carry footprint | CONFIRMED (4/5) | one narrow exception |
| P9 | routing pin Fable/high + Sol xhigh | CONFIRMED | no drift since f69e9fb |
| P10 | `route --heartbeat` never spawns | CONFIRMED | queue PARAPHRASE was wrong (attributed claim to Conductor A) — corrected IN QUEUE; playbook was right |

### 3.2 Meta-finding

The audit worker fell into BOTH traps from that day — P1 via tool-shell stdin EOF, P3 via MSYS mangling — and in both cases executed the contract isolation step (re-probe via subprocess list-args) and reached the correct verdict. This is the most important result of the round: anti-false-pin discipline **works when required by contract**, even with a cheaper model, and the traps are REPRODUCIBLE (not bad luck from one session).

### 3.3 Stratification by pin origin

| pin origin | n | false | rate |
|---|---:|---:|---:|
| 1 failure observation, shell variable not isolated | 3 (R1–R3) | 3 | 100% |
| deliberate measurement / source inspection | 10 (P1–P10) | 1 | 10% |

The only false item in the second stratum (P7) was not wrong at birth — it was correct and **drifted** when D041 changed gate execution regime, without anyone re-measuring the constant. Distinct class: temporal decay, not origin error.

### 3.4 Round cost

Queue + contract: overseer inline. Worker: 201.7k Sonnet tokens. Probes: Terra/Haiku, cents total. No expensive-model probes.

## 4. Discussion: why pins rot

1. **Shell-boundary mangling is the dominant killer in this environment.** 4/4 refutations that day (R1–R3 + intermediate ENOTCACHED) trace to quoting layers (MSYS path mangling; cmd `^` escape; nested PowerShell), not tools. On Windows with 3 stackable shells, any failure observed THROUGH a shell is suspect until the argument is proven intact (subprocess list-args is the clean instrument).
2. **Single-symptom generalization.** All three refuted claims became "the tool cannot" from ONE failure. The opus-overseer report had already named the family (prose exceeds verification); here it appears in the epistemic direction: insufficient observation becomes operational law.
3. **Constants measure regimes, not truths.** P7 was true under serial regime; D041 changed regime and the constant became orphaned. Numeric pins need a regime stamp (what invalidates them), not just a date.
4. **Paraphrases rot too** (P10): the error was in the AUDIT QUEUE, not the playbook — verification instruments are subject to the same decay as what they verify.

## 5. Resulting mechanisms (non-prose)

| mechanism | state |
|---|---|
| R1–R3 + P7 corrections recorded as dated RETRACTIONS (never history deletion) in playbook/spec/CLAUDE.md | landed (`b309625`, `00312f2`, `ac5517d`, W3 batch) |
| Pin-audit queue as permanent reusable artifact (claim + test + pre-registered risk) | `.harness/handoff/playbook-pin-audit-queue.md` |
| Isolation contract for audit worker (proved transferable) | in queue text; reusable verbatim |
| "Probe-before-pin" as playbook practice | recorded in corrections |

Open recommendations (doors, not completed work): (a) periodic re-audit of queue (cheap: cents + one Sonnet worker); (b) pin metadata — every new pin carries date + method + evidence link + invalidating regime; (c) workaround-attempt cap in lanes (W3 wedge this afternoon: lane spent ~50 min on TEMP workaround instead of declaring HOST-LIMITED as W1/W2 lanes did — standard lane instruction should bound the loop).

## 6. Conclusion

The audit answered the owner's question with a number and a cause: **of 13 pins examined, 4 were false, and 3 of those 4 were born from the same methodological defect** (single symptom through unisolated shell). The remaining corpus is healthy (9/10), and the only decayed item was regime drift, not origin error. Cost of keeping the corpus honest proved trivial (cents per round) compared with cost of false pins it prevents — R2/R3 alone would have kept UI-test lanes away from Codex and forced unnecessary pre-installs indefinitely.

## References

Internal: `.harness/handoff/playbook-pin-audit-queue.md` (queue + outcome); `.harness/handoff/result-playbook-pin-audit.md` (verbatim evidence per pin); R1–R3 probes in session transcripts (commands + verbatim outputs, incl. NET-OK 200 and both EPERMs); `docs/research/opus-overseer-quality-2026-07-23.md` (companion; F4 = same family in metric direction); `docs/research/construct-metrics.md` (R4: pre-register definition before measurement); `docs/research/vendor-credit-tracking-log.md` (measurement honesty); commits `b309625`, `f69e9fb`, `00312f2`, `ac5517d`, `cd665dc` (D047).
External: none cited — internal corpus; §2.3 limitations apply.
