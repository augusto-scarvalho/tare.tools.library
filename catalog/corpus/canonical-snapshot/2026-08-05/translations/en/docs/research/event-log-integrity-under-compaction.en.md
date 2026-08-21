# Research — Tamper-Evident Event-Log Integrity Under Compaction (SPEC-164 M4+M5)

Ideation round, 2026-07-21. Question: does SPEC-164 `allow_gaps` weaken the model (owner question)? Which structures from blockchain / verifiable logs / authenticated data structures solve “legitimate removal while preserving integrity evidence without false positive”? Which is PROPORTIONAL to our ceiling (no key, single tenant, LOCAL verifier, transient live log + durable record)?

Ideators (5 across 3 vendors): 2× **Sonnet 5 High** (Anthropic; cryptographic rigor and ops/cost) + 1× **Gemini** (Google) + 2× **NVIDIA** (`nemotron-3-nano-30b`; security and trust boundary). Infrastructure note: `NVIDIA_API_KEY` lives in `.env` (not keyring) and is loaded at harness boot — worker must run through harness spawn or with `.env` loaded; giant NVIDIA models (`nemotron-ultra-550b`) returned 503 under overload and nano-30b responded. Small model = shallower analysis, weighted lower.

## Verified foundations (Discover)

| Technique | Source | What it provides |
|---|---|---|
| Certificate Transparency / RFC 6962 | datatracker.ietf.org/doc/html/rfc6962 [web, strong] | Consistency proof proves tree B is a PREFIX of A (only appended, never deleted). Merkle, O(log n), Signed Tree Head + THIRD-PARTY monitor. Does NOT support deletion. |
| Crosby-Wallach 2009 (USENIX Security) | usenix.org/legacy/event/sec09 [web, strong] | Merkle history tree that SELECTIVELY DELETES old events while preserving tamper evidence (keeps internal hash, discards leaf). O(log n). Signing is orthogonal. |
| Merkle Mountain Range | eprint.iacr.org/2025/234, docs.grin.mw [web, moderate] | Append-only accumulator; pruning old leaves while roots remain. Standard pruning is PREFIX/age based and does not match our removal-by-TYPE pattern. |
| Sparse Merkle Tree / RSA-bilinear accumulator | [judgment] | (Non-)membership in keyspace; accumulator needs semi-trusted setup. Wrong tool for sequential log rather than key-value. |
| KSI / hash calendar (Guardtime) | [web, moderate] | “Keyless” means no ASYMMETRIC subscriber key, but replaces it with PERIODIC external publication broadly witnessed. The witness is the disguised “key.” |
| Rekor/Sigstore (Trillian) | [judgment] | Reuses CT tree + third-party monitors + log server + network. Disproportionate for local harness. |

## Convergence (3 ideators, 2 vendors — STRONG signal)

1. **Merkle/CT/MMR/accumulator are OVER-ENGINEERING here.** They solve three things absent from our case: (a) THIRD-PARTY verifier without raw-data access (we have ONE local verifier, `repo_health.checks`, already reading the full file → O(log n) proofs are moot); (b) BILLIONS-of-leaves scale (here tens per round); (c) RESOURCEFUL adversary + signature/witness. **Without a key or external witness, a Merkle root recomputable by the writer is as forgeable as a simple hash** — Merkle does NOT raise the ceiling without signature. [Sonnet-crypto + Sonnet-ops + Gemini, strong]
2. **The REAL effort pays off in the DURABLE RECORD (`escalations.json`), NOT the live chain.** Live chain is TRANSIENT (gates clean it) and check is ADVISORY/WARN-only → damage from gap is “doctor incorrectly says OK once.” Durable record SURVIVES gates, holds owner security decisions and has ZERO integrity today (each `resolvedRecord` overwritten by key, no chaining). Damage there is PERMANENT. [both Sonnet, strong]
3. **Crosby-Wallach = option C without the tree.** Paper solving our conceptual problem (delete while retaining evidence) is the SAME idea as “keep hash, discard content” — tree only pays with third-party verifier. [Sonnet-crypto, strong]
4. **Finding correcting my framing:** shipped `allow_gaps=True` is WEAKER than option C — it tolerates EVERY gap unconditionally AND accepts reordering of LIVE events (spec already declares this in invariant 3). It is not even option C. [both Sonnet, strong, code-verified]

## Typed divergence

| Axis | Sonnet-crypto (rigor) | Sonnet-ops (cost) |
|---|---|---|
| Is option C sufficient? | **NO** — it has a HOLE: proves existence, not adjacency. Forger can cite ANY removed hash as `prevHash` of a new line. Fix: **option C+** = pairs `{successor_hash: removed_hash}` binding exception to successor identity via SHA-256 second-preimage hardness. Closes reorder + citation forgery. Seal must ACCUMULATE, not overwrite. | **More than needed** — C only matters if there is a second removal path outside compactor (marginal in threat model). Set grows unbounded in durable file. |
| Where to invest | C+ in live chain + note durable has marginal value without witness | **Skip live chain; give SIMPLE hash chain to durable record** (`stateHash` + `prevStateHash` per `escalations.json` write). Cheaper than C, cheaper than Merkle. |
| Converge on | No Merkle; durable matters; keyless ceiling is real | same |

### CROSS-VENDOR divergence (NVIDIA vs Sonnet — owner-requested)

| | NVIDIA (`nemotron-nano`) | Sonnet 5 High (both) + Gemini |
|---|---|---|
| Durable structure | **MMR** — O(log n) inclusion proof, “strong” | **SIMPLE hash chain** — MMR over-engineering |
| Is O(log n) worth it? | YES (NVIDIA-1 said “no external witness needed,” most aggressive position) | NO — moot: verifier is LOCAL and reads whole file; O(log n) pays only with THIRD-PARTY verifier |
| Need witness? | NVIDIA-1 said no; **NVIDIA-2 corrected: pure MMR needs STH** → proposes **Git anchoring** as cheap witness | Yes — without witness/signature, recomputable Merkle root is as forgeable as hash |

**Real disagreement:** VALUE of O(log n) inclusion proof. NVIDIA thinks it justifies MMR; Sonnet+Gemini say it is moot TODAY (local verifier already has everything) and only pays when a third-party verifier exists (future CI/multi-tenant) — same trigger as key infrastructure. [Sonnet strong, NVIDIA preliminary — smaller model]

### New, strong convergence (Sonnet-crypto + NVIDIA-2, cross-vendor)

**External anchoring through Git** = CHEAP third-party witness without key infrastructure: periodically commit head-hash/seal to a git-tracked file reviewed by owner. Rewriting Git history is visible/forensic — meaningfully raises “no-key” ceiling without provisioning a key or service. Both vendors reached this independently. Best answer to “tamper-evident, not proof” ceiling. [cross-vendor, moderate]

## Recommendation (orchestrator synthesis)

**Do not move to Merkle/CT/MMR** (unanimous — over-engineering without key). Two cheap, stdlib pieces with no new dependency:

1. **Live chain → option C+ (successor→removed pairs), not current `allow_gaps`.** Closes the hole owner sensed (reorder + self-consistent edit escaping today) by binding every tolerated gap to successor identity. Direct answer to “does allow_gaps weaken it?”
2. **Durable record → simple one-link hash chain per write** (`stateHash` = sha256 canonical doc without own field; `prevStateHash` = previous write). Closes DEEPER gap: zero integrity in file surviving gates and storing security decisions. Detects point edit AND rollback to old snapshot.
3. **Git anchoring** (new piece, Sonnet-crypto + NVIDIA-2 convergence) — periodically commit durable head hash/seal into owner-reviewed git-tracked file. Cheap external witness raising ceiling WITHOUT key infra.

**Behind third-party-verifier/key-infra trigger (do not build now):** MMR (NVIDIA) or SIGNED Merkle root (Crosby-Wallach/RFC-6962). O(log n) compact-proof gain only pays when verifier DOES NOT possess full file (external CI, multi-tenant). Until then simple hash-chain + Git anchoring yields same practical ceiling for far less code. [Sonnet strong; NVIDIA disagreement is the signal to reopen when trigger arrives]

## Direct answer to owner

Yes, `allow_gaps` weakens the model — but the fix is **not** blockchain/Merkle (over-engineering without key, confirmed by two vendors). It is (1) option C+ in live chain and/or (2) simple hash chain in durable record, which is where integrity is actually absent. The ceiling “no key = tamper-evident, not tamper-proof” is intrinsic and honest; only signing + external witness raises it, behind key-infrastructure trigger.

---

# Round 2 — Double Diamond #2 (9 ideators, 9 divergences) — 2026-07-21

Owner request: deepen candidates, hunt papers CROSSING the domains, and run nine ideators (3 Sonnet 5 High × 3 NVIDIA-GLM × 3 Gemini) with nine divergences.

**Model coverage (honest):** Sonnet 5 High ×3 (Agent). NVIDIA-GLM = `z-ai/glm-5.2` all three (no fallback — GLM responded). Gemini: crypto seat ran `gemini-3-flash-preview` (owner request); other two fell to `gemini-2.5-flash` (3-flash-preview unavailable/limited). Each vendor ran three perspectives: A=minimal engineer, B=cryptographer, C=boundary architect.

## Cross-domain papers (Discover 2 — verified)

| Source | What it crosses | Finding |
|---|---|---|
| **SealFS / SealFSv2** (Computers & Security 2021; Int. J. Info. Sec. 2022) [web, strong] | secure logging single-machine × our local regime | Local tamper evidence WITHOUT hardware/network. v1 = stored keystream (theoretical security), v2 = ratchet (linear degradation) — cost↔security knob. Guarantee: attacker cannot forge data generated BEFORE system compromise. |
| **Bellare-Yee / Schneier-Kelsey / Ma-Tsudik FssAgg / Logcrypt** [web, strong] | forward integrity × evolving key | Family of symmetric MACs with ratchet+delete → forward integrity WITHOUT PKI. Ceiling: protects PAST after FUTURE compromise; needs secret and key-erasure boundary. |
| **Crosby-Wallach history trees** [web, strong] | redaction × verifiable append history | Selective deletion while retaining cryptographic digest skeleton. Again, signatures/witness needed to prevent writer from recomputing history. |
| **CT / verifiable logs / transparency systems** [web, strong] | append-only public log × third-party witness | Merkle consistency becomes meaningful because independent monitors remember prior roots. Local sole-writer regime lacks that trust split. |
| **Filesystem append/immutable controls** (`chattr +a`, Windows ACL/`icacls`, BSD `uappnd`) [repo/web/judgment] | OS boundary × local logging | Raises bar against accidental or sandboxed-worker rewrite using existing mechanism; parity differs across OS and same-user deliberate attacker can often undo controls. |

## Threat-model reframing

Round 2 stopped treating “tampering” as one class and separated adversaries:

- **T1 — sandboxed worker / unprivileged child**: cannot freely rewrite owner workspace; existing workspace boundaries matter.
- **T2 — same-user harness process with ordinary write access**: can edit files and, if it knows the scheme, recompute simple chains.
- **T3 — deliberate same-user process with source/credentials**: can re-ACL, recompute and steal same-user secrets unless an external boundary exists.
- **T4 — administrator/root/host compromise**: out of scope for local bookkeeping; only external witness/hardware can meaningfully raise ceiling.

This reframing corrected several earlier recommendations: a control can be very valuable against T1/T2-careless while worthless against T3, and calling it simply “secure” hides the real ceiling.

## Candidate leverage ladder (Round 2 synthesis)

- **L1 — simple durable hash chain + C+ seal**: cheap tamper evidence; strong against careless/unknown-scheme edits, weak against source-aware T2/T3.
- **L2 — protected-file machinery / explicit override**: leverages existing harness control-plane against workers; records deliberate bypass.
- **L3 — OS append/ACL boundary**: useful parity option, but semantics differ strongly on Windows/Linux/macOS and same-user owner may reverse ACLs/flags.
- **L4 — Git anchor**: external-ish witness when remote/review history exists; cheap, but only as strong as independent history/review.
- **L5 — forward-secure ratchet**: attractive in theory, but ephemeral CLI architecture lacks long-lived memory-only key holder; persisting ratchet key collapses boundary.
- **L6 — owner signature for ratification events**: can raise ceiling materially only when private-key use requires out-of-band owner presence; agent-triggered signing is not a trust boundary.
- **L7 — external timestamp/transparency witness (OTS/CT-style)**: strongest no-local-trust direction, but adds network/service and is disproportionate before public/multi-tenant requirements.
- **L8/L9 — dedicated writer/daemon**: potentially isolates write authority, but architectural weight is high and needs observed repeated T2 pressure.

The practical Round-2 conclusion was therefore not “choose strongest crypto.” It was **match the lever to the adversary we actually claim to resist**, and declare residual ceiling.

## Immediate implications before Round 3

1. Preserve L1/L2 because they cheaply catch the most likely accidental and repo-blind mutation classes.
2. Verify whether worker workspace can read actual `.env`/secrets; if yes, credential exposure outranks ledger tampering.
3. Treat Git anchor, forward-secure logging and owner keys as deferred behind explicit triggers rather than decorative crypto.
4. Keep OS append-only as parity option, not default, until cross-platform semantics are measured.

---

# Round 3 — FINAL CONSOLIDATION (Double Diamond #3, 2026-07-21, orchestrator Fable 5 xhigh)

Brief reframed by reassessment (layered T1–T4 model, L1–L7 levers with honest corrections, explicit anti-anchor: “attack/expand > rank”). Six-seat panel: Sonnet 5 High ×2 (RED, DECIDER), GLM-5.2 ×2 (same — no fallback), Gemini ×2 (2.5-flash; 3-flash-preview unavailable in this window). Prior Discover resolved citation (2512.17259 = Verifiability-First, verified) and multi-OS append-only asymmetry (`chattr +a` requires root to set AND unset; `icacls` per-user; `uappnd` reversible).

## Anti-anchor succeeded: three NEW leverage classes and one NEW adversary layer

1. **T1.5 “authentic garbage” (5/6 seats — strongest convergence).** Worker poisons data/results; trusted context FAITHFULLY writes a syntactically perfect entry (chain OK, ACL OK, signature OK) that is semantically malicious. GLM-RED: “the chain is witness to the attack, not a barrier.” ALL L1–L7 authenticate form, not content. Real countermeasure (Sonnet-RED): **decision provenance** — chain causal references of what produced a ratified entry (tool outputs, worker results). Harness ALREADY has skeleton: `parentEventId` causal DAG + typed actor (SPEC-161) — wiring discipline, not new structure.
2. **L10 kernel audit witness (4/6):** ETW/USN/SACL (Windows), auditd (Linux), EndpointSecurity (macOS) — trail outside adversary userland write domain; stronger than ACL/attribute; honest fix for L3 asymmetry (install once with admin, read by separate reader).
3. **Recovery/response (4/6):** detection without response is theater — quarantine read-only on mismatch, fork append point from last known-good, resume only through owner action OUTSIDE agent loop (alarm cannot depend on drifted process acting against itself).
4. **Rollback/freshness attack (Sonnet-RED):** restore an OLD validly chained (even validly signed) snapshot to erase recent ratifications without breaking anything — chain/signature authenticate content-at-a-point, not recency. Cheap countermeasure discovered in synthesis: **live↔durable cross-witness** — compaction event in live log records durable `stateHash` that produced it; doctor compares → careless backup restore is caught. (Careful T2 rewrites both — ceiling unchanged and declared.)

## Ratified matrix corrections (against Round 2 AND my brief)

- **“T2 trivially recomputes” assumes T2 KNOWS the scheme** (GLM-DECIDER). Realistic T2 (injection from tool output, without harness source) leaves stale chain → L1/L2 catch much more than previously credited. L1 rises in value.
- **L6 “unforgeable by T2+T3” is FALSE as stated** (6/6 in some form; Gemini-DECIDER strongest disagreement): key on disk under same user is stealable by T2/T3. Sonnet-RED deeper cut: **agent-triggered signature** lets T1.5 pass poison through signer with valid signature. L6 only works with (a) out-of-band signing secret (passphrase/hardware) and (b) human proof-of-presence showing LITERAL ratified text — never “agent concluded owner approved.” Without both, L6 is false confidence.
- **L5 dead in current architecture** (5/6): ephemeral CLI processes → ratchet on disk → drifted process IS key holder. Defer ≈ never until long-lived daemon with memory-only ratchet exists.
- **L3 vs T3 ~zero even on Windows** (Sonnet-RED): file owner (same user as T3) retains WRITE_DAC and can ACL back. L3 is anti-careless/anti-ignorant lever (T1, source-blind T2), never anti-deliberate-same-user. On Linux, interestingly STRONG against user-level T2 after set (unset requires root) — but setup requires root.
- **L1 without verifier running is inert** (Sonnet-DECIDER): shipping L1 = ship verify TOGETHER in existing cadence (doctor/gate), or do not ship.

## VERIFIED code findings during the round

- **`.env` is NOT excluded from workspace** (`workflow_runtime_ignore` does not list it) → NVIDIA/GEMINI keys readable by workspace worker. Panel (GLM-RED M4, Sonnet-RED) identified “inverted priority”: credential leak ≥ ledger tamper. One-line fix + fixture. CONFIRMED 2026-07-21.
- **Override is bare env** (`HARNESS_ALLOW_PROTECTED_WRITE=1` in `protect_canonical_files.py`) — harden to per-session nonce to close accidental/replay bypass (honest label: does NOT close deliberate T2).
- To verify (backlog): TOCTOU at merge seam (GLM-RED M1); env scrub at worker spawn; T1→T2 promotion via unreviewed code artifacts executed in later round (Sonnet-RED).

## FINAL DECISION CARD (for owner ratification)

**BUILD NOW (revised M4+M5 train + urgent hygiene):**

| # | Item | Against what |
|---|---|---|
| B1 | `.env` in workspace exclusion (one line + fixture) | T1 reading credentials — round’s top priority |
| B2 | L1: durable chain (`stateHash+prevStateHash`) + COUPLED C+ seal + **verify in doctor/gate** (inert without it) + **live↔durable cross-witness** (anti-careless rollback) | T2-careless AND source-blind T2 (most likely realistic case) |
| B3 | L2: `escalations.json` in protected registry (reuse SPEC-148) + override env→nonce + override emits security event | T1 escape; accidental/replay bypass |
| B4 | Decision provenance: `resolvedRecords` carry `parentEventId` chain + actor (SPEC-161/DAG skeleton already exists) | T1.5 — ONLY lever touching authentic garbage |
| B5 | Policy: ledger outside ambient backup/sync (note + cheap doctor check) | restore rollback + confidentiality leak |

**OWNER DECISION FORCED IN THIS ROUND** (Sonnet-DECIDER: “deferring decision ≠ defer because technical prerequisite missing”): L6 yes/no — owner minisign/ed25519 key ONLY for ratification events, CONDITIONED on (a) out-of-band secret at signing + (b) proof-of-presence with literal text. If either condition unacceptable → honest defer with declared ceiling (careful T2/T3 remain open on durable record).

**DEFER WITH NAMED TRIGGER:** L3 (distinct-principal decision OR formal parity downgrade to “hash-chain parity only” + Windows-only declared); L4 Git anchor (remote out-of-reach + genuinely recurring owner review); L5 (long-lived daemon with memory-only ratchet); L7 OTS (external/compliance demand or multi-tenant); L9 writer daemon (observed recurring T2); L10 kernel audit (when L3 parity judged unacceptable — replaces L3, does not stack — or first confirmed T2 incident).

**NEVER (tombstones):** MMR (9/9 Round 2 — local verifier reads all); TPM/TEE at this tier (disproportionate multi-OS); per-event signature in live log (no trust boundary for hot-path signer); bespoke WORM layer (reinvents L3); own blockchain (consensus for a hash that one append can record); SIEM-as-integrity (fleet problem, not single-machine); **signature triggered by agent inference** (T1.5 anti-pattern); cadence-as-sufficiency (verify at point of USE for decisions; cadence is floor).

**RESIDUAL CEILING AFTER BUILD-NOW (plain language):** T1 closed (residual = escape bug, same accepted today). T2: careless/source-blind caught by next gate; careful source-aware T2 still forges — becomes unforgeable ONLY on ratifications and ONLY with L6 under both conditions. T3: L1/L2/L3 ~zero (recomputes/re-ACLs everything); only well-custodied L6 + external witness (L4/L7/L10) raise ceiling. T1.5: B4 gives audit trail; prevention is human review at ratification point, not cryptography. T4: out of scope.

## If L6 — owner decision 2026-07-21: ADOPT, but only in the FUTURE

Named trigger: **before first PUBLIC release** (owner: “we’ll adopt only in the future, before a public release”). Until then declared ceiling above is honest for single-tenant/local use. When built, BOTH use conditions (out-of-band passphrase/hardware at sign + proof-of-presence showing literal ratified text — never agent-inferred signing) are mandatory, PLUS three requirements imposed by key-loss analysis:

1. **Authorized public-key list** (`authorized_keys` style), not a single key — otherwise rotation INVALIDATES all already-signed history. Old ratifications verify under old public key; new under new.
2. **Mandatory passphrase** on private key — otherwise “lost key file” becomes “silent compromise” (finder signs as owner). With passphrase, disk key is useless without secret.
3. **Documented rotation/revocation path** — treat “lost/leaked key” as NORMAL flow, not emergency.

**Loss semantics (why L6 is safe to defer AND adopt):** losing key NEVER locks harness or erases past — it only lowers ceiling of FUTURE ratifications to bookkeeping level (today’s ceiling) until rotation. Worst-case loss = “back to current ceiling.” Honest tension: passphrase protects leak but creates passphrase-loss risk; password-manager backup helps but makes key security as good as that backup (same ladder, no magic). External timestamp (L4/L7) is what could prove which signatures came before/after leak — therefore L6 and external witness reinforce each other when public trigger arrives.
