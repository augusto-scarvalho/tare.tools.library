# Holding the Standard by Protocol, Not Memory: Role-Scoped Instruction Inheritance for Multi-Vendor AI Agent Harnesses

**Companion article to** `docs/research/playbook-inheritance-round-2026-07-23.md`
(evidence round, crossed 2×2 design) and SPEC-170
(`specs/40-features/playbook-registry.md`). Authored by the session
orchestrator (Claude Fable 5) under owner direction, 2026-07-23. All claims
carry provenance tags per SPEC-119 v5: `[web]` (fetched this session by a
research lane), `[repo]` (a path/commit in this repository), `[judgment]`
(reasoned inference, unverified externally).

---

## Abstract

Multi-vendor AI agent systems accumulate operating instructions in loose
markdown files whose loading is governed by convention rather than
declaration. We report a same-day sequence of instruction-drift incidents
in a working agent harness, a survey of how nine instruction and
configuration ecosystems compose layered rules, and a structured ideation
round (4 generators, 4 critics, crossed across two model families) on
inheritance mechanisms for a role-scoped playbook registry. Three findings
recur. (1) The industry has converged on layered, scoped instruction files
composed by concatenation, but governs them by directory convention;
verification and enforcement are absent. (2) Mature configuration
ecosystems that survived a decade of layered composition all grew the same
three organs — resolution pinning (lockfiles), effective-view rendering,
and collision detection — and their documented failure modes (silent
precedence, ambiguous multiple inheritance) transfer directly. (3)
Security machinery must match operating scale: at single-owner scale,
signature chains collapse into the version-control history they duplicate,
while filesystem ACLs and content-hash snapshots do the real work. We
distill these into a design rule for agent harnesses: *an instruction
document that is not declared, resolved, and machine-verified at a choke
point is tribal knowledge, and tribal knowledge does not hold.*

## 1. Introduction

AI coding agents are configured by natural-language instruction files
(`AGENTS.md`, `CLAUDE.md`, rules directories). As one repository comes to
be operated by several agent roles — interactive overseers, autonomous
loop drivers, routers, confined implementation workers — across several
vendors, these files multiply and overlap. The failure mode is not the
absence of rules but the absence of *loading guarantees*: a rule that
lives in a file the current role never reads is indistinguishable, at run
time, from a rule that does not exist.

This paper consolidates one day of evidence from the Universal Agent
Harness prototype: (i) a case study of four instruction-drift incidents
observed live in a single session `[repo]`; (ii) a two-flow survey of
instruction and configuration ecosystems `[web]`; (iii) a 24-concept
ideation round with cross-family critique `[repo]`; and (iv) the resulting
adopted design, SPEC-170 `[repo]`.

## 2. Case study: four incidents in one session `[repo]`

All four occurred on 2026-07-23 in one working session of this repository
(commits `f10218f`, `6a0fc05`, `d3fcf92`; incident detail in the round doc
and session records).

**I1 — Stale adapter doc taught a forbidden command.** The Claude adapter
file (`CLAUDE.md`) instructed running the validation gate in a form that a
`PreToolUse` hook had since been installed to deny. The hook (protocol)
corrected what the document (memory) taught wrongly. Doc drift was
repaired only because a machine check sat at the choke point.

**I2 — Role knowledge in an unloaded file.** The session overseer operated
without knowledge of the commit join (gate ‖ reckon, SPEC-157), the
hold-swap hazard, and the detached-gate requirement — all documented, but
only in the autonomous-loop playbook that an interactive session never
loads. Every one of these bit or nearly bit during the session.

**I3 — Contract misused as playbook.** The orchestrator initially inlined
operational flow into the vendor-neutral contract (`AGENTS.md`); the owner
correction ("generic contract; discipline is role-scoped, pointed to by
role") produced the split into role playbooks and, ultimately, the
registry design. The incident shows the *absence of a declared place* for
role discipline actively invites misplacement.

**I4 — Frozen-surface landmine absent from a delegation brief.** An
implementation worker added a CLI verb without striking the repository's
frozen verb tuple; the gate caught it. The knowledge existed (in the loop
playbook's brief-writing doctrine: "pre-list the landmines") but the brief
author had never loaded that doctrine — I2 recursing into delegation.

The common structure: in each incident the standard held **only where a
deterministic mechanism (hook, gate, frozen scenario, mutation oracle)
enforced it**, and failed wherever it relied on a model having read prose.
This mirrors the harness's own prior doctrine, distilled from an earlier
12-item session: *"written so the standard holds by protocol, not by model
memory"* (`.harness/prompts/overseer-loop-playbook.md` `[repo]`).

## 3. Survey: how the field composes instructions

Method: two Discover flows (bleeding-edge and foundations) run by two
independent Sonnet lanes with mandatory provenance tagging and a
no-fabrication rule; evidence tables with per-claim confidence and
maturity classes live in the round doc. Summary of the load-bearing rows:

**Agent-instruction ecosystems.** The AGENTS.md format is an open standard
adopted at ecosystem scale (reported 60k+ repositories; secondary source,
confidence *moderada*) [1]. Claude Code's memory system is the most
completely documented composition model surveyed: a fixed precedence
hierarchy (managed policy → user → project → local), **concatenation
without override**, root-to-leaf ordering, lazy loading of subdirectory
files, an `@path` import syntax with depth cap 4 and code-fence exclusion,
and path-scoped rules via `paths:` frontmatter globs (primary vendor
docs, *forte*) [2]. Cursor (`.mdc` rules with four activation modes) [3],
Windsurf (single `trigger` field, hard character caps) [4], and Cline
(directory auto-merge, with a documented multi-root scoping bug) [5]
converge on the same shape: **scoped markdown fragments, activated by
path or intent, composed additively**. CrewAI, by contrast, defines flat
per-agent YAML with no inheritance; composition happens by assembling
agents, not by hierarchy (*preliminar*) [6].

Notably, none of the surveyed agent ecosystems has: a declared role
registry, a resolution verifier, or spawn-time enforcement. Governance is
convention.

**Configuration and policy ecosystems (the foundations flow).** Ansible's
global variable namespace produces silent collisions, a pitfall its own
ecosystem later mitigated with opt-in scoping (`public:`) (*moderada*)
[7]. Helm renders effective configuration (`helm template`) and layers
values files with declared precedence [8]; Kustomize composes by explicit
diffable patches [9]. OPA distributes policy as versioned, manifest-bearing
bundle artifacts (*forte*) [10]. Python's C3 linearization refuses class
hierarchies with no consistent method-resolution order at definition time
— fail-fast over guessing (*moderada*, secondary sources) [11].

The pattern: every ecosystem that survived layered composition at scale
grew (a) **pinning** of what was resolved, (b) **rendering** of the
effective result, and (c) **collision or ambiguity detection that refuses
rather than guesses**.

## 4. Ideation round: method and outcomes

**Design.** Owner-specified crossed 2×2: two Sonnet ideators (grounded in
the surveys above) and two GLM ideators (packet workers with embedded
context only, no repository or web access) generated 24 concept cards
independently; critique was strictly cross-family (GLM critics graded
Sonnet cards on validity and integration cost; Sonnet critics graded GLM
cards on real-world precedent and architecture fit). No family graded its
own output. The design instantiates three published findings: independent
generation before exposure (nominal groups ≈2× ideas) [12]; separation of
generation from critique [13]; and the observation that multi-agent debate
pays off through model heterogeneity rather than debate per se [14], with
structural coupling collapsing idea diversity [15]. Self-critique alone was
not trusted, consistent with evidence that LLMs cannot reliably self-correct
reasoning [16]. Convergence was set-based — options eliminated by evidence,
a live set retained — following Toyota's set-based concurrent engineering
[17]. The overall two-diamond phase structure follows the Design Council
model [18], and the orchestrator-with-parallel-workers topology follows
Anthropic's multi-agent research system report [19].

**Outcome quality.** Across all eight lanes, zero fabricated citations:
the no-web GLM lanes marked all 24 of their cards `reference: judgment`,
and one Sonnet lane explicitly omitted a system (Terraform) rather than
cite it unverified. Cross-family critique caught defects the generating
family plausibly could not: GLM critics flagged CRLF-vs-LF hash divergence
and mutable-state-in-immutable-registry conflicts in Sonnet's ops-flavored
cards; Sonnet critics, with web access, attached real precedents (RFC 5280
[20], SLSA/in-toto [21], Kubernetes namespaces / npm scopes [22], CSS
specificity [23], PMI RACI [24], FAA airworthiness-directive applicability
blocks [25], consolidated-legislation practice [26]) to GLM's
judgment-only cards and then rejected most of them on scale or
ratified-decision conflicts.

**Adopted (núcleo, W2 of SPEC-170):** an auto-generated, line-ending-
normalized chain lockfile (absorbing the signed-manifest proposal minus
its PKI, which collapses at single-owner scale — §5); an effective-view
renderer with per-line origin attribution; and simplified spawn
provenance (role + resolved-chain hash logged in existing spawn records,
the cheap 80% of an attestation ledger). **Registered experiment:** a
directive-collision linter, advisory until its false-positive rate is
measured (EXP-34) — directly motivated by Ansible's silent-collision
scar. **Rejected (10 of 24)** mostly for contradicting ratified decisions
(platform: kernel-level write-fences on a Windows-first repository;
history: amendment chains re-inventing what git already owns; scale:
per-role PKI with no durable key-holder). **Parked with named triggers
(7):** per-target namespaces, glob activation, inline imports, RACI,
taint scanning, drift detection, mixin precedence.

## 5. Discussion: three transferable principles

**P1 — Protocol over memory.** Every incident in §2 and every survey
mechanism in §3 point the same way: prose does not hold standards; choke-
point verification does. For agent harnesses the choke points are the
commit (gates) and the spawn (role resolution). SPEC-170's hard refusal of
unregistered roles extends to instructions the same guarantee the commit
gate gives to code. The corollary for documents: **an instruction file's
loading must be a declared, resolvable, verifiable property of a role —
not a habit.**

**P2 — The three organs of layered composition.** Pinning, effective
rendering, collision refusal (§3) recur across unrelated ecosystems with
a decade of production scar tissue. Agent-instruction systems are young
and have none of the three; they can import all of them cheaply (all
three adopted mechanisms are additive files or read-only CLI modes).

**P3 — Scale-matched trust machinery.** The critique round systematically
killed cryptographic proposals whose security arguments presume separation
of duties that a single-owner repository does not have. One key-holder
means a signature proves only "the owner touched this," which git history
already records. The effective protections at this scale are boring:
filesystem ACLs, content-hash snapshots, reviewed edit flows, and
append-only run records — all of which the harness had already shipped
(SPEC-148 `[repo]`) before any of the sophisticated proposals were made.
Threat models, like budgets, must be declared at the scale actually
operated.

## 6. Threats to validity

- **Single-case, single-day case study.** §2's incidents come from one
  session of one repository (n=1); the generalization to "agent harnesses"
  is analytic, not statistical.
- **LLM-gathered evidence.** All `[web]` rows were fetched and summarized
  by model workers in-session. Several rest on secondary or aggregator
  sources and are graded *moderada/preliminar* accordingly in the round
  doc's evidence tables; primary-source confirmation was obtained only
  where noted (Claude Code docs, OPA docs, Ansible docs).
- **Model-judged verdicts.** Card verdicts are named-criteria judgments by
  models, used as inputs to an orchestrator decision, not as ground truth
  (per the harness's own research playbook rule: "LLM evaluation is
  support, not truth").
- **Unverified-by-orchestrator citations.** Two security references
  surfaced by a critic lane (an agent-governance toolkit and a
  skills-security preprint) were not independently verified by the
  orchestrator and are deliberately excluded from the reference list.
- **No quantitative benchmark.** The claimed benefits of the adopted
  mechanisms (token savings from de-duplication, drift catches) are
  design-stage predictions; EXP-34 and the W2 delivery are where
  measurement begins.

## 7. Conclusion

A day that began with an untested GUI fix slipping past every gate ended
with the same repository refusing an unregistered CLI verb, catching a
weak test oracle, and rejecting 10 of 24 well-argued design proposals for
contradicting decisions an owner had ratified hours earlier. The
difference in every case was the presence of a deterministic mechanism at
a choke point. Instruction inheritance for agent roles is the next surface
to receive that treatment: declared chains, resolved and pinned, rendered
inspectable, verified continuously, enforced at spawn. What the industry
does by convention, a governance harness can do by protocol — and the
evidence of both the day's incidents and a decade of configuration-
ecosystem scar tissue says protocol is the only thing that holds.

## References

External (all accessed 2026-07-23 by session research lanes; confidence
classes per the round doc's evidence tables):

1. AGENTS.md standard overview (secondary aggregator). https://agentsstandard.com/
2. Anthropic, "Manage Claude's memory" — Claude Code docs (primary). https://code.claude.com/docs/en/memory
3. Cursor rules guides (secondary, cross-corroborated). https://www.morphllm.com/cursor-rules-best-practices ; https://techsy.io/en/blog/cursor-rules-guide
4. Windsurf rules guide + docs (secondary + vendor docs). https://www.skillwright.app/blog/windsurf-rules-guide ; https://docs.windsurf.com/windsurf/cascade/memories
5. Cline, ".clinerules" blog (vendor) + multi-root scoping issue (primary bug report). https://cline.bot/blog/clinerules-version-controlled-shareable-and-ai-editable-instructions ; https://github.com/cline/cline/issues/4642
6. CrewAI agent docs (vendor). https://docs.crewai.com/en/concepts/agents
7. Ansible role reuse docs (vendor) + variable-precedence pitfalls (secondary). https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_reuse_roles.html ; https://oneuptime.com/blog/post/2026-02-21-how-to-use-ansible-variable-precedence-rules/view
8. Helm values files & subcharts (vendor). https://helm.sh/docs/chart_template_guide/values_files/ ; https://helm.sh/docs/chart_template_guide/subcharts_and_globals/
9. Kustomize strategic merge patches (secondary; one author a former Kubernetes maintainer). https://itnext.io/kubernetes-strategic-merge-patch-4bdd19b48789
10. Open Policy Agent, bundle management (vendor, primary). https://www.openpolicyagent.org/docs/management-bundles
11. Python C3/MRO explanations (secondary, cross-corroborated). https://jakubkrajewski.substack.com/p/mastering-the-diamond-problem-how ; https://machinelearningplus.com/python/how-python-handles-multiple-inheritance-mro-explained/
12. Diehl, M. & Stroebe, W. (1987). Productivity loss in brainstorming groups. *JPSP* 53(3), 497–509. https://homepages.se.edu/cvonbergen/files/2013/01/Productivity-Loss-In-Brainstorming_Toward-the-Solution-of-a-Riddle.pdf
13. Du, Y. et al. (2023). Improving factuality and reasoning in language models through multiagent debate. https://composable-models.github.io/llm_debate/
14. "If Multi-Agent Debate is the Answer, What is the Question?" arXiv:2502.08788. https://arxiv.org/abs/2502.08788
15. "Diversity Collapse in Multi-Agent LLM Systems." arXiv:2604.18005. https://arxiv.org/pdf/2604.18005
16. Huang, J. et al. (2024). Large language models cannot self-correct reasoning yet. ICLR 2024. https://arxiv.org/abs/2310.01798
17. Sobek, D., Ward, A. & Liker, J. (1999). Toyota's principles of set-based concurrent engineering. *MIT Sloan Management Review*. https://sloanreview.mit.edu/article/toyotas-principles-of-setbased-concurrent-engineering/
18. Design Council. Framework for Innovation (Double Diamond). https://www.designcouncil.org.uk/resources/framework-for-innovation/
19. Anthropic. How we built our multi-agent research system. https://www.anthropic.com/engineering/multi-agent-research-system
20. RFC 5280 — X.509 PKI certificate and CRL profile. https://datatracker.ietf.org/doc/html/rfc5280
21. SLSA (https://slsa.dev/) ; in-toto (https://in-toto.io/)
22. Kubernetes namespaces (https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/) ; npm scopes (https://docs.npmjs.com/cli/v10/using-npm/scope)
23. MDN — CSS cascade specificity. https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_cascade/Specificity
24. PMI — RACI diagrams. https://www.pmi.org/learning/library/raci-diagrams-organizational-clarity-9207
25. FAA — Airworthiness Directives process. https://www.faa.gov/aircraft/safety/programs_initiatives/maintenance_programs/ad
26. UK legislation — understanding consolidated legislation. https://www.legislation.gov.uk/understanding-legislation

Internal `[repo]`:

27. SPEC-170 — `specs/40-features/playbook-registry.md` (commit `d3fcf92`).
28. Round doc — `docs/research/playbook-inheritance-round-2026-07-23.md` (commit `f91b563`).
29. Refinement (Q1–Q8 ratified) — `docs/research/playbook-hierarchy-refinement-2026-07-23.md` (commits `6e17daf`, `cdc1d97`).
30. Overseer-loop playbook (protocol-over-memory doctrine) — `.harness/prompts/overseer-loop-playbook.md`.
31. Session incident commits — `f10218f` (gate-caught e2e premise + inline-closure mechanization), `6a0fc05` (contract/playbook split).
