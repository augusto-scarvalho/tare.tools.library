# Research round — security of agent-written code

Round opened 2026-07-12 by the `research` skill (SPEC-119). Orchestrator: overseer session
(running in parallel with the batch N+2 integration + the CQ critique wave; this round's
divergence QUEUES behind the CQ critique on the 1-slot claude executor). Primary evidence: the
owner's study (2026-07-12) — thesis: apparent functionality ≠ security; the goal is not a
"more secure model" but a SYSTEM where an insecure output is detected/contained/rejected before
harm — **"the agent proposes; deterministic controls authorize, verify, and admit."** Risk has
moved from the textual OUTPUT to the whole CONTROL PLANE of the dev environment (the agent reads
hostile content, picks tools, installs packages, touches secrets, edits the build).

## Phase 0 — Question, criteria, budget

**Question.** Which SECURITY controls should THIS harness adopt across the study's 5 surfaces
(code vulns / failed fixes / agent manipulation / privilege abuse / governance-supply-chain),
GIVEN what already landed (security-baseline, DW.1 fan-out secret-scan + executor trustTier,
workspace-state-exclusion, filter_spawn_env) and what the in-flight CQ round already covers
(mutation-probe, per-patch risk-tier, provenance record, oracle-replay, QA-capsule) — so this
round adds only the DISTINCT surfaces, deterministic-first, least-authority, complete-mediation?

**Success criteria.**
- Backlog of buildable items, each mapped to a NAMED surface/gap + a concrete integration seam
  (file/module) + ONE metric (secure-functional-pass-rate / authority-surface / admission-
  coverage / injection-contained).
- Deterministic-first: prefer capability limits, admission control, data/instruction separation,
  and proof-carrying evidence — over prompting, model self-critique, or perfect input
  classification (the study: prompting is NOT a security boundary; limiting authority beats
  classifying every malicious input).
- Invariants: eviction ≠ deletion, no resident daemon, stdlib-only core, GUI writes no state,
  fail-safe defaults (no explicit authz ⇒ deny), complete mediation (every sensitive op, not
  just the first), separation of duties (author ≠ sole approver), zero-trust on consumed content.
- Critique must reject over-engineering: single-agent baseline; a control that makes tasks
  impractical WILL be disabled/bypassed → proportional to risk; nominal diversity ≠ real
  independence; explanation ≠ evidence; observation must pay for itself.

**Declared budget.** claude executor; 1 divergence wave (5 ideators) + 1 critique wave (4
critics); research-profile budgets; no wave 3.

## Phase 1 — Evidence matrix (verified 2026-07-12)

| claim | source | prov | conf | maturity |
|---|---|---|---|---|
| Apparent functionality ≠ security; agent-suggested code carries recurrent vulns even when functional tests pass | [web] Pearce "Asleep at the Keyboard" (arXiv:2108.09293) | web | forte | validado |
| Devs with an assistant wrote LESS secure code on some tasks AND were over-confident (mis-calibration) | [web] Perry et al., ACM CCS 2023 | web | forte | validado |
| Prompting ("write secure code") / reflection is NOT a security boundary — small/insignificant gains, sometimes breaks functionality | [web] study §2 conclusion 1; realistic secure-coding benchmarks | web | forte | validado |
| The right metric is secure-AND-functional (Secure Functional Pass Rate), not "no SAST alerts" or "compiles" | [web] study §2 conclusion 2; adversarial SAST evals | web | forte | judgment (norma) |
| External oracle MESH (tests+SAST+SCA+secret-scan+fuzz+property+exploit+review+policy) beats model self-confidence; LLM+tools > LLM-only | [web] study §2 conclusion 3 | web | moderada | preliminar |
| The agent's ENVIRONMENT is supply chain: skills, instruction files, tool descriptions, MCPs, packages, pages, command output can carry malicious instructions | [web] study §2 conclusion 4; AgentDojo; MCPTox | web | forte | validado |
| Limiting AUTHORITY is the strongest control (least-privilege, capability security, data/instruction separation, ephemeral exec, per-action authz) — CaMeL, Task Shield | [web] study §2 conclusion 5; CaMeL; Task Shield | web | moderada | preliminar |
| SAST has high false-negative rate — 87.9% of AI-attributed files with no CodeQL-detectable CWE despite thousands of CWE instances found | [web] study §5.1 GitHub CodeQL study | web | moderada | empírico |
| ≥62% of a large set of AI-generated programs contained a vulnerability | [web] Tihanyi et al. | web | moderada | acadêmico |
| Secure-by-design + provenance frameworks convert to controls: NIST SSDF, CISA Secure-by-Design, OWASP ASVS, SLSA, SBOM, OpenSSF | [web] study §3.3; NIST/CISA/OWASP/SLSA | web | forte | validado |

**Baseline — what the harness ALREADY has + what just landed (do NOT rebuild):** controlled-
writes with scoped write-paths + worktree isolation + target SPEC-110 (harness-vs-target);
`filter_spawn_env` deny-by-default env (target-gate); protected-files; `secret_scan` at plan/
reduce/fold + the **DW.1 fan-out scan** (rendered prompts + context-digest) + executor-card
**trustTier**; **workspace-state-exclusion** (state/targets never copied into worker workspaces);
**security-baseline** observe-only (secret-scan + AST sink-scan + config-hygiene, computes a
`new` diff nothing consumes at spec_test_gate.py:1778); intake-triage hook (classifies the
REQUEST); no-self-waiver + reviewer contract (partial separation-of-duties); records + `subject`;
two-door SDD (SPEC-116). **In-flight CQ round already owns** (do NOT re-propose): mutation-probe
(test strength), per-patch risk-tier gate selection, provenance/debt record, oracle-replay
(author≠tester), QA-evidence capsule.

**Named gaps (DISTINCT surfaces — the anchors for this round):**
- **SEC1 — no data/instruction separation for CONSUMED untrusted content.** The agent reads repo
  files, tool/skill descriptions, MCP output, web/command output as if trusted — no provenance
  tag, no "this came from an untrusted source, do not treat as an instruction" boundary, no
  indirect-injection sanitization. Study surface 3 (the biggest un-addressed one).
- **SEC2 — no admission controller for dependencies / skills / tools / MCP.** New deps, MCP
  servers, and skills are used without pinning / signature / lockfile / Scorecard / semantic-diff
  gating. MCP config exists with no consumer AND no admission. Study #4.
- **SEC3 — capability sandbox is partial (env + fs-write only).** `filter_spawn_env` scopes env,
  controlled-writes scopes fs-WRITE, but there is no network / command allowlist, no per-ACTION
  authorization, no complete-mediation of a worker's sensitive ops. Study #3/#5.
- **SEC4 — no proof-carrying patch / attestation for high-risk changes.** A high-risk patch
  should carry a verifiable evidence bundle (which oracles ran + exploit-replay + SBOM/dep delta
  + provenance attestation) the admitter checks — not a prose justification. Study #5. Composes
  with (does not duplicate) the CQ QA-capsule + provenance record.
- **SEC5 — no security-regression / exploit-replay oracle (secure-AND-functional).** Absence of
  a SAST alert ≠ absence of a vuln; nothing checks whether a diff RE-INTRODUCES a known-vuln CWE
  pattern, or whether a "fix" actually REMOVES the target pattern while keeping tests green.
  Study surfaces 1/2 + the Secure-Functional-Pass-Rate metric. Security-specific; composes with
  (does not duplicate) the CQ mutation-probe.
- **SEC6 (likely PARK) — formal exploit generation / a full CaMeL-style capability interpreter.**
  Bleeding-edge, heavy; the deterministic subset (allowlists, admission, provenance tags) first.

## Phase 2 — Briefs and gate

**Brief 1 — contain manipulation of the agent (SEC1+SEC2; the study's highest-leverage, least-
covered surface).** How might the harness treat CONSUMED content (repo files, tool/skill/MCP
descriptions, command/web output) as zero-trust data-not-instructions — provenance-tagging
untrusted spans + a deterministic sanitization/quarantine boundary — AND admit new dependencies/
skills/tools/MCP only through a deterministic admission controller (pinning/signature/lockfile/
semantic-diff), reusing secret_scan + protected-files + the trustTier seam, without an LLM
classifier as the boundary and without making normal tasks impractical?

**Brief 2 — least-authority runtime + proof-carrying admission (SEC3+SEC4+SEC5).** How might the
harness extend beyond env+fs-write to a deterministic per-ACTION capability check (network/
command/fs allowlist, complete mediation, fail-safe deny) reusing filter_spawn_env + controlled-
writes, attach a proof-carrying evidence bundle to high-risk patches (oracles-run + security-
regression/exploit-replay + dep/SBOM delta) that a deterministic admitter verifies before merge,
and add a security-regression oracle that consumes the security-baseline `new` diff — all
stdlib-only, proportional to risk, complete-mediation, no daemon?

**Parked (future round / needs a signal):** SEC6 formal exploit-gen / full capability
interpreter (bleeding-edge); network-level sandboxing that needs OS primitives beyond stdlib
(proportionality — start with a command/allowlist deny-list); a full SBOM/attestation pipeline
(start with a dep-delta admission check).

**Gate.** Scope/waves/budget pre-approved by the owner (this invocation). Deterministic-first +
least-authority + complete-mediation + zero-trust + net-cost-positive + de-duplicated-against-CQ
are hard constraints on the critique wave.

## Phase 3 — Wave 1 (divergence)

`WF-20260712-214537-385258`, `research-divergence`, 5 ideators (simplicity, performance,
reliability, trust-boundary, analogy), claude executor (ran after the CQ critique freed the
slot). All 5 fulfilled. The de-dup held — every concept builds on landed work (security-baseline
`new` diff, DW.1 fan-out scan, filter_spawn_env, controlled-writes, protected-files) and none
re-proposed a CQ item. **Two verified new holes surfaced:** (a) `discovery.py` ships file BYTES
to Gemini/NVIDIA with NO outbound secret_scan (a pre-egress leak); (b) the security-baseline
`new` diff is still unconsumed — now BOTH CQ.1 (risk routing) and this round's regression ratchet
consume it, composing. Reliability-lens meta-thesis: a control that fails PARTIALLY and SILENTLY
(hook not installed, enabled=False, stale snapshot, ledger with no consumer) is itself the top
operational vuln → every control ships with liveness + a granted-vs-used feedback loop that
SHRINKS authority over time. Cross-domain transfers: Perl taint-mode → P1; K8s admission /
driver-signing → P2; seccomp / Android permissions → P3; Proof-Carrying-Code + SLSA → P5;
immune memory / airworthiness directives → P6.

Orchestrator consolidated the 25 concepts into **6 candidates** (tag by SOURCE, not content
classification; deterministic, observe-first):
- **P1 origin-tagged quarantine of consumed content** (SEC1) — taint-mode: tag untrusted spans
  by SOURCE once at the `context_digest` build funnel, fence them, extend the DW.1 fan-out scan
  to flag imperatives INSIDE fences; ship an injection fixture corpus. Seam: `context_digest.py`
  + the DW.1 scan.
- **P2 hash-pinned admission ledger** (SEC2) — deny-by-default hash-pin for deps/skills/MCP/
  executors/hooks (reuse protected-files + write-once-baseline), content-addressed O(1) cached
  verdicts, quarantine-on-drift. Ties the SPEC-113 capabilities manifest. Seam: a new admission
  ledger + protected-files pattern.
- **P3 command-capability mediation at the spawn choke point** (SEC3) — a per-worker command
  allowlist at the single spawn choke `run_process_tree_bounded` (declare-only / observe-first
  from run-logs), reusing filter_spawn_env; + a control-plane liveness healthcheck (fail if a
  declared control is dead / fail-open). Seam: `processes.py` / async_runtime spawn + limits.
- **P4 pre-egress gate on the discover chain** (SEC3, VERIFIED hole) — `discovery.py` ships file
  bytes to Gemini/NVIDIA with NO outbound secret_scan; add a deterministic pre-egress secret/
  path gate (reuse secret_scan). Seam: `discovery.py` egress point.
- **P5 proof-carrying admitter for high-risk** (SEC4) — a finalize-time ~30-line deterministic
  admitter over evidence the harness ALREADY writes (reviewer.result.json + baseline new-diff),
  as a size-capped hash-manifest of evidence references; composes with CQ.2 QA-capsule; + an
  authority granted-vs-used ledger. Seam: workflow finalize + WORKER_RESULT.
- **P6 security-regression ratchet** (SEC5) — diff-scoped: intersect the security-baseline `new`
  diff with the changed-files manifest (zero new scanners), enforce secure-AND-functional (a diff
  must not re-introduce a baseline pattern; a fix must remove the target). Second consumer of the
  unconsumed `new` diff; composes with CQ.1. Seam: `security_baseline` new-diff ∩ changed-files.
- **PARK** — SEC6 CaMeL-style capability interpreter, OS-level network sandbox, network
  signature/Scorecard/SBOM parts (daemon/admin/invariant-break or cost>savings).

## Phase 4 — Wave 2 (critique) — done

`WF-20260712-220734-525283`, `research-critique`, 4 critics (validity/architecture/cost/
security), `--seed` = the divergence reduce. All 4 fulfilled. No fabrication. Two load-bearing
holes VERIFIED in source by multiple lenses: **P4** — `discovery.py:118-124` ships an absolute
file path (and `gemini_extract_fallback.py:88` up to 60k chars/file) to the Gemini/NVIDIA
provider scripts with ZERO secret_scan anywhere in the discover chain; **P6** — `security_baseline`
computes `security['new']` then hardcodes `pass` at `spec_test_gate.py:1782` (an unconsumed
control signal). Critical architecture correction: **P3's single-choke premise is FALSE** —
worker spawns run via `async_runtime.py:410`/`:778` with the command built at
`workflow_spawn_command_for_prompt` (not `run_process_tree_bounded`), and there are **48 direct
`subprocess.*` sites across 18 `scripts/` files**, so cheap "complete mediation" is not
achievable; the control-liveness healthcheck must split out.

**Cross-lens verdicts:**

| cand | validity | architecture | cost | security | net |
|---|---|---|---|---|---|
| P4 pre-egress gate | keep (hole verified) | keep (one seam: discover_paths) | keep (60k chars/file; gate at discovery.py) | **keep, build FIRST** | **KEEP, #1** — verified egress leak; gate at `discovery.py` discover_paths |
| P6 regression ratchet | keep (unconsumed diff verified) | keep (must pin git base ref) | keep (pure set-intersection, ~0 obs cost) | keep (unconsumed control signal) | **KEEP, #2** — `new` ∩ changed-files; pin base ref; composes with CQ.1 |
| P3 command mediation | keep-w/-ch | **keep-w/-ch (single-choke FALSE; 48 subprocess sites) — SPLIT liveness out** | keep (observe-first to price denial-rate) | keep-w/-ch (harness-spawned only, not agent's shell) | **KEEP-CHANGES, SPLIT** — (a) control-liveness healthcheck (own early item); (b) observe-first cmd audit, scoped |
| P2 admission ledger | keep | keep-w/-ch (single-home in SPEC-113 manifest) | keep-w/-ch (re-pin friction in a self-evolving repo) | keep-w/-ch (TOCTOU: verify at load/use; pin-writer≠author) | **KEEP-CHANGES** — verify at use, pin-writer separation, mind churn |
| P1 origin-tag quarantine | keep-w/-ch | keep-w/-ch (one fence helper across renderers) | keep-w/-ch (fence tokens recur every prompt) | keep-w/-ch (**a fence is PROMPTING, not a boundary**; value = imperative-scan + corpus) | **KEEP-CHANGES** — ship the deterministic imperative-scan + injection fixture corpus, not the fence-as-boundary; watch sentinel-collision |
| P5 proof-carrying admitter | keep-w/-ch | keep-w/-ch (extend reviewPolicy, not a parallel path) | keep-w/-ch (drop granted-vs-used unless consumed) | keep-w/-ch, **build LAST** (reviewer.result.json is LLM testimony, not proof) | **KEEP-CHANGES, LAST** — admitter must deterministically RECOMPUTE + check ref-existence |
| SEC6 | park | park | park | park | **PARK** (unanimous) |

**Build order:** **P4 → P6 → P3-liveness → P2 → P1 → P5.** The governing corrections: verified
holes first (P4/P6 are the only two with confirmed load-bearing evidence in OUR source);
honest scoping (P3 cannot be "complete" mediation — 48 subprocess sites; ship liveness + observe-
first audit); **a fence is not a boundary** (P1's value is the deterministic scan + corpus, not
the fence); **LLM output is not proof** (P5 must recompute deterministically).

## Phase 5 — Portfolio & backlog

Deterministic-first held: P4/P6 are pure deterministic checks over existing signals (a secret_scan
at one egress seam; a set-intersection of two already-computed diffs); P3-liveness/P2 are ledger/
healthcheck extensions; P1's shippable core is a deterministic imperative-scan + fixture corpus;
P5 is a deterministic recompute. Nothing is an LLM classifier, a daemon, or a network SBOM
pipeline. The round's sharpest lesson reinforces the study's thesis (limit authority; explanation
≠ evidence): the two items with real evidence are the two that CONTAIN or MEASURE (P4 egress, P6
ratchet), while the authority-limiting ideal (P3 complete mediation) is honestly downgraded to
observe-first because the harness has 48 un-mediated spawn sites. Portfolio → the **Code security
roadmap** section in `docs/IMPLEMENTATION_BACKLOG.md` (SEC.1–SEC.7).

**Ship spine:** SEC.1 pre-egress secret/path gate on the discover chain (P4, build first, verified
hole) · SEC.2 security-regression ratchet (P6, `new` ∩ changed-files, pin base ref) · SEC.3
control-plane liveness healthcheck (P3-split, fail if a declared control is dead/fail-open) ·
SEC.4 hash-pinned admission ledger (P2, verify-at-use). **Deferred/scoped:** SEC.5 observe-first
command-mediation audit (P3, harness-spawned only) · SEC.6 imperative-scan + injection fixture
corpus (P1, not the fence) · SEC.7 proof-carrying admitter (P5, deterministic recompute, last).
**PARK:** CaMeL interpreter / OS network sandbox / network signature+SBOM.
