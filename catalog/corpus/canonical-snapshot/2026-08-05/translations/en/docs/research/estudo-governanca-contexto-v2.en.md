---
translation_of: docs/research/estudo-governanca-contexto-v2.md
source_snapshot: 2026-08-05-private-github-snapshot
source_language: pt-BR
language: en
translation_status: MACHINE_TRANSLATED_UNREVIEWED
authority_status: DERIVED_NON_AUTHORITATIVE
editorial_migration: true
scientific_refresh: false
historical_reference_date: 2026-07-26
---

# Context Governance in Long-Running Multi-Agent Harnesses

## Overseer loops, subagents, compaction, context folding, garbage collection, memory, and cross-vendor control

**Version:** 2.0 — expanded scientific edition  
**Historical date:** July 26, 2026  
**Original language:** Portuguese  
**Document nature:** expanded structured narrative review, critical evidence synthesis, and architectural proposal  
**Scope:** multi-agent harnesses for software engineering, research, workflows, and long-running tasks; peer-reviewed papers, recent preprints, official documentation, engineering blogs, repositories, branches, releases, issues, and technical discussions.

> **Historical editorial English edition.** This is a translation and editorial migration of the exact 2026-07-26 source found in the private GitHub snapshot. It preserves historical claims and proposals. It is **RESEARCH**, not proof of CURRENT implementation and not automatic TARGET authority. Vendor facts have not been silently refreshed to 2026-08-11.

## Abstract

Language-model agents increasingly execute long-running tasks that combine reasoning, tool use, artifact manipulation, testing, delegation, and human interaction. This produces potentially unbounded trajectories over finite and cognitively imperfect context windows. Vendor-advertised context length is not equivalent to reliable operational capacity: *Lost in the Middle*, RULER, and NoLiMa show degradation with context length, middle-positioned evidence, multiple facts, and associative retrieval without lexical overlap (Liu et al., 2024; Hsieh et al., 2024; Modarressi et al., 2025). Agentic workloads add large tool outputs, stale results, failed-attempt interference, governance loss during compaction, and cross-agent context pollution (Cheng et al., 2026; Chen, 2026).

This document consolidates theory, recent empirical work, vendor practices, and multi-agent harness patterns to address context management in Overseer loops and subagents. It proposes a vendor-agnostic **Context Control Plane** that externalizes canonical state, performs object- and dependency-aware garbage collection, retrieves and packs evidence according to attention constraints, folds completed subtasks, applies typed compaction profiles, validates post-compaction integrity, and resets and rehydrates sessions at safe semantic boundaries.

> **Central design principle:** the Overseer persists as a logical role and external state, not as an immortal model conversation.

**Keywords:** AI agents; multi-agent systems; context engineering; context compaction; context folding; garbage collection; agent memory; Overseer; subagents; coding agents; long context; harness engineering.

### Contributions of the expanded edition

The source says this edition preserves the preceding version while expanding it in six directions: (1) broader review of long-context benchmarks; (2) comparison of garbage collection, folding, and compaction mechanisms; (3) deeper treatment of subagents and parent-child boundaries; (4) cross-vendor comparison that separates documented capability from proven performance; (5) engineering evidence from repositories, releases, branches, issues, and discussions; and (6) an experimental program intended to validate the hypotheses in the harness itself.

## Numbered contents

1. Introduction
2. Research questions and method
3. Problem model: physical, useful, and trustworthy context
4. Operational taxonomy
5. Memory and state architecture
6. Overseer loop and session lifecycle
7. Subagents: internal compaction and boundary folding
8. Context garbage collection
9. Compaction profiles
10. Context folding and branch management
11. Lost in the Middle and position-aware packing
12. Vendor and open-model comparison
13. Lessons from other harnesses
14. Proposed Context Control Plane architecture
15. Profiles by role and task class
16. Experimental program
17. Security, governance, and auditability
18. Trade-offs, limitations, and threats to validity
19. Implementation roadmap
20. Open research agenda
21. Conclusions
22. Bibliography

# 1. Introduction

Traditional conversational systems assume a relatively short message sequence whose complete history can be resent on each turn. A long-running agentic harness breaks that assumption. An Overseer may read constitutions/rules/playbooks; analyze backlog work; plan or delegate; create implementers, researchers, and reviewers; supervise tools/processes; integrate results; run unit/integration/regression tests; repair failures; produce commits and bookkeeping; close one task and start the next.

The resulting trajectory mixes objects with very different lifecycles:

- normative instructions;
- objectives and acceptance criteria;
- active and superseded plans;
- tool calls/results;
- workspace file contents;
- decisions and rationales;
- test evidence bound to code versions;
- active and rejected hypotheses;
- subagent transcripts;
- volatile external results;
- process/container/asynchronous-task state;
- memories intended for reuse across sessions.

Treating all of this as one chronological message list creates three architectural errors. It conflates **active context** with **persistent state**; assumes every visible item receives equivalent attention; and delegates lifecycle control to the model even when much of that control can be deterministic.

MemGPT introduced the analogy between an LLM context and virtual memory: a bounded active region is fed by larger external layers and information moves between them (Packer et al., 2023). MemOS extends the framing toward memory as an operational resource with representation, organization, governance, and migration (Li et al., 2025). The document observes a parallel in coding-agent practice: plans, Git state, requirements, acceptance logs, and checkpoints are externalized so new sessions can resume work without the entire transcript.

> **Central hypothesis:** reliability in a long-running multi-agent harness depends less on maximizing how much history remains in the model window and more on governing the lifecycle of context objects while preserving canonical state, causality, authority, and recoverability.

# 2. Research questions and method

## 2.1 Research questions

- **RQ1.** What session lifecycle should an Overseer use when repeatedly executing backlog items?
- **RQ2.** When should an agent garbage-collect, fold, semantically compact, or reset?
- **RQ3.** Which information can leave the active view without operational loss, and which must be pinned?
- **RQ4.** How should policy differ across Overseers, short subagents, long investigators, implementers, and reviewers?
- **RQ5.** Are canonical compaction profiles inferior to, or complementary with, task-adaptive profiles and on-the-fly overlays?
- **RQ6.** How do Lost in the Middle, failed-attempt interference, and governance degradation affect context organization?
- **RQ7.** What mechanisms were exposed at the historical reference date by Codex, Claude Code, Kimi Code CLI, Gemini CLI, and open ecosystems?
- **RQ8.** What metrics and experimental designs can validate a context policy without confusing token reduction with task success?

## 2.2 Review type

This is a **structured narrative review and rapid update**, not a complete PRISMA systematic review. The source prioritizes peer-reviewed long-context/prompt-compression work, reproducible benchmarks, 2025–2026 long-horizon agent preprints, official vendor documentation, reproducible harness repositories/whitepapers, and internal project documents.

| Evidence class | Examples | Intended use |
|---|---|---|
| A | Peer-reviewed work, standards, widely reproduced results | Foundations and stronger constraints |
| B | Benchmarks/papers with code or datasets | Operational state of the art |
| C | Recent preprints with clear evaluation | Bleeding edge and experiment hypotheses |
| D | Official vendor docs and engineering blogs | State of practice |
| E | Repositories, whitepapers, issues, engineering reports | Hypothesis generation and implementation patterns |

Strong architectural claims should, when possible, triangulate academic foundations, recent empirical evidence, and industrial practice.

## 2.3 Limits of cross-vendor comparison

At the date of the source, the authors did not identify a broadly accepted independent benchmark comparing native compaction quality across Claude Code, Codex, Kimi CLI, and Gemini CLI while holding model, prompt, trajectory, tools, and algorithm constant. The document therefore separates:

1. documented control surface;
2. observable product behavior;
3. semantic compaction quality—which requires a harness-owned benchmark.

## 2.4 Search and corpus-update strategy

The expanded update combines four search modes: established benchmark/foundation search; bleeding-edge 2025–2026 work on long-horizon agents, context folding, execution-state memory, learned compaction, and GC; state-of-practice vendor documentation; and operational evidence from repositories/releases/issues/discussions.

Representative query families were combinations of long-running/coding/agent terms with context compaction, context folding, eviction, garbage collection, working memory, and agent memory; vendor names with compaction/hooks/subagents; and multi-agent harness/orchestrator terms with ledgers, artifacts, checkpoints, context, and memory.

The source explicitly does **not** claim bibliometric exhaustiveness. It treats itself as a living review: every claim should be tied to the version consulted; preprints remain labeled as such; vendor docs describe product surfaces rather than prove superiority; issue reports expose failure classes rather than population incidence.

## 2.5 Practical evidence hierarchy

| Class | Example | Supports | Does not support by itself |
|---|---|---|---|
| E1 — peer-reviewed | TACL, ACL, NeurIPS, ICLR | Formally reviewed phenomenon/method | Automatic transfer to all agents/vendors |
| E2 — reproducible benchmark | RULER, ∞Bench, LongBench v2 | Public comparative evidence | Complete representation of real coding agents |
| E3 — preprint + artifact | Self-GC, CWL, Context-Folding | Direct recent evidence | Industrial maturity / independent replication |
| E4 — official documentation | hooks, thresholds, context editing | Declared product capability | Real semantic quality |
| E5 — repo/release/issue | little-coder, Codex/Claude issues | Engineering patterns and failure modes | General frequency, causality, statistical efficacy |

The writing rule is conservative: strong conclusions require E1/E2 or triangulation; E3 mechanisms are promising hypotheses; E5 problems are field evidence rather than scientific estimates.

## 2.6 Minimum and extended corpus

The core corpus includes *Lost in the Middle*, RULER, NoLiMa, LongLLMLingua, LLMLingua-2, MemGPT, HiAgent, Magentic-One, SWE-agent, and MetaGPT. The extended set includes ∞Bench, LongBench v2, MemGym, A-MEM, Context-Folding, FoldAct, U-Fold, MAGE, Self-GC, CWL, ACON, SelfCompact, CompactionRL, ContextBudget, and Governance Decay. The engineering corpus includes Codex, Claude Code/Agent SDK, Kimi Code CLI, Gemini/ADK, Deep Agents, little-coder, ChatDev 2.0, MetaGPT, Agentless, Pydantic AI Harness, and filesystem-offloading implementations.

# 3. Problem model: physical, useful, and trustworthy context

## 3.1 Four different limits

### 3.1.1 Physical limit

The maximum token volume accepted by model/API. Exceeding it causes errors, truncation, or automatic compaction.

### 3.1.2 Retrieval limit

Information may be physically present but not reliably retrieved. *Lost in the Middle* reported better performance when relevant evidence is near the beginning or end and degradation in middle positions (Liu et al., 2024).

### 3.1.3 Utilization limit

Finding a string is not the same as using multiple distributed facts in reasoning. RULER extends needle tests with multiple needles, multi-hop tracing, and aggregation; NoLiMa removes direct lexical overlap and forces associative retrieval (Hsieh et al., 2024; Modarressi et al., 2025).

### 3.1.4 Interference limit

Present context can make performance worse. Contextual Drag reports degradation when failed attempts remain visible and bias later trajectories toward structurally similar mistakes (Cheng et al., 2026). This matters especially in repair loops retaining long logs, rejected patches, and incorrect diagnoses.

## 3.2 Operational limit

The harness should derive an operational limit rather than copy the advertised window:

```text
hard_limit = vendor configured window

safe_physical_limit =
    hard_limit
  - output reserve
  - tool-result reserve
  - instruction/schema overhead
  - recovery margin

reliable_attention_limit =
    largest size at which the model remains acceptable
    on harness positional + agentic benchmarks

operational_limit = min(safe_physical_limit, reliable_attention_limit)
```

It should vary by model snapshot, vendor/CLI, task class, artifact type, tool volume, language, output requirements, retrieval profile, and compaction policy.

## 3.3 Context as cognitive cache

```text
External canonical state
 ├── Git / workspace
 ├── task ledger
 ├── progress ledger
 ├── decision records
 ├── evidence store
 ├── trajectory store
 ├── artifact store
 └── memory store
        ↓
Context builder / packer
        ↓
Active model window
```

> The window is disposable; the state is not.

## 3.4 What long-context benchmarks actually measure

The source rejects literal needle retrieval as a sufficient proxy. It separates four dimensions for an internal harness benchmark:

| Dimension | Question | Harness example |
|---|---|---|
| Retrieval | Does the model find the fact? | Recover an old constraint |
| Attribution | Does it bind the fact to the right object/version? | Associate a test with the corresponding commit |
| Utilization | Does it apply the fact correctly? | Preserve a public API during refactoring |
| Continuity | Does it retain the rule after tools/compaction? | Preserve a constraint across three phases |

∞Bench and LongBench v2 broaden long-context evaluation toward QA, summarization, code, reasoning, and long dependencies, but traditional benchmarks rarely include tool calls, file versions, side effects, multiple agents, or repeated compaction.

## 3.5 Expanded failure taxonomy

### Dilution

Correct information remains visible but competes with many semantically adjacent items. Monolithic historical memory and retrieval without reranking worsen the problem.

### Staleness and temporal mixing

Evidence from commit A must not silently govern commit B. Evidence should carry artifact version, commit, timestamp, and supersession relationships.

### Failed-attempt contamination

Failures should not simply remain as rich narratives. Useful failures can become typed **negative memory**—rejected claim + evidence + reconsideration conditions—while mechanical details are externalized.

### Authority loss

Governance Decay/ConstraintRot is cited as evidence that compaction can erase or de-emphasize safety constraints. The source does not universalize its reported rates because it is a preprint, but draws a strong architectural rule: **governance does not belong to the compactable heap**.

### Tool-protocol corruption

Provider protocols may require valid `tool_call`/`tool_result` pairs. Arbitrary trimming can break them. GC must treat protocol spans atomically through vendor adapters.

### Successive-summary drift

Repeatedly summarizing only the prior summary creates a lossy transformation chain. The proposed policy prefers structured checkpoints plus reversible archives and, where possible, regenerates summaries from canonical state and original trajectory rather than from the previous summary alone.

### Context anxiety / premature completion

The source uses this operational label for cases where agents under context pressure shorten or prematurely close work. Harness-managed checkpoints and predictable resets should reduce pressure to optimize “session survival” rather than task completion.

## 3.6 Long context as partial observability

A long-running agent operates in a world larger than its window. Every model call receives an observation assembled by the harness. **Context engineering is therefore an observation policy**: what state to reveal, at what granularity, and in what order. A-MEM, MemOS, and HiAgent support the broader direction of structured memory operations and task/subgoal-aligned working memory rather than static history.

# 4. Operational taxonomy

These operations are not synonyms:

| Operation | Definition | Expected semantic loss | Recoverability |
|---|---|---:|---|
| Trimming | Removes messages/parts by simple rule | Low to high | Usually low |
| Offloading | Moves payload to storage and leaves a reference | None if byte-exact | High |
| Garbage collection | Removes unnecessary/duplicate/persisted/unreachable objects from active view | Low | Medium/high |
| Masking | Keeps structure/metadata/edges while hiding repetitive body | Low | High with sidecar |
| Folding | Closes a causal unit/subtask and replaces it with a condensed result | Low/medium | High if referenced |
| Compaction | Rewrites history into a smaller representation, often with an LLM | Medium/high | Low without archive |
| Reset | Ends the session and creates another from a checkpoint | Depends on checkpoint | High |
| Memory promotion | Turns validated learning into reusable memory | Not session reduction | Auditable |
| Deletion | Permanently removes storage | Total | None |

Preferred order:

```text
offloading + deterministic GC
        ↓
retrieval + repacking
        ↓
fold completed units
        ↓
semantic compaction
        ↓
reset + rehydrate
```

The source argues that compaction is more expensive and epistemically risky than GC because it creates a new interpretation of the past.

# 5. Memory and state architecture

## 5.1 Layers

- **Working memory:** latest observations, current hypothesis, next action.
- **Session memory:** summaries/indices needed within the physical session.
- **Run state:** formal execution/workflow state.
- **Task state:** contract, criteria, progress, evidence.
- **Project memory:** validated repository facts/procedures.
- **Experience store:** trajectories, successes, failures, eval outcomes.
- **Policy memory:** constitution, permissions, invariants, versions.
- **Artifact history:** commits, patches, logs, reports, documents, outputs.

These layers have different retention and authority rules. Collapsing them into one “conversation summary” destroys necessary distinctions.

## 5.2 Task Ledger and Progress Ledger

Inspired by Magentic-One, the source separates relatively stable task state from volatile progress.

**Task Ledger:** objective, acceptance criteria, constraints, confirmed facts, macro plan, risks, dependencies, definition of done.

**Progress Ledger:** current phase, owner, latest result, modified artifacts, active jobs, current tests, blockers, stall count, next action.

Task Ledger changes less often; Progress Ledger can be reconstructed after almost every action.

## 5.3 Trajectory Store

The trajectory is append-only and remains the full audit source. GC/compaction alter only the active view.

```yaml
trajectory_event:
  run_id:
  task_id:
  node_id:
  agent_id:
  event_type:
  timestamp:
  inputs: []
  outputs: []
  artifact_refs: []
  policy_decisions: []
  parent_events: []
  model:
  token_metrics: {}
```

## 5.4 Context Object Model

```yaml
context_object:
  id: tool:bash:0188
  type: tool_result
  owner:
    run_id: run-82
    task_id: TASK-184
    agent_id: implementer-04
  authority:
    level: observation
    source: tool
  lifecycle:
    state: live
    generation: young
    collection_count: 0
  dependencies:
    depends_on: []
    referenced_by: []
  persistence:
    persisted: true
    artifact_ref: artifact://logs/bash-0188.txt
    byte_exact_recovery: true
  semantics:
    unique_evidence: false
    unresolved: false
    superseded_by: null
  gc:
    pinned: false
    preferred_action: fold
    earliest_safe_boundary: after_tool_cycle
```

This enables object-based rather than chronology-based decisions.

## 5.5 Canonical state, events, and materialized views

The architecture separates:

1. **Event log / trajectory store:** append-only record of what happened.
2. **State stores:** current task/artifact/agent/policy state.
3. **Context views:** disposable projections assembled for an inference/phase.

A test event records command, commit, environment, and artifact; the Progress Ledger identifies which run is current; the context packer shows the model the current summary plus references to historical runs.

A single `summary.md` is insufficient because it mixes authority, volatile state, decisions, and narrative. Typed/versioned references are needed to distinguish superseded tests, rejected hypotheses, and human-originated rules.

### Provenance as a compaction requirement

Every compacted field should remain linked to sources. A decision without `evidence_refs` is a compressor assertion; a referenced decision can be audited and rehydrated. This also prevents “summary of summary of summary” from becoming the only accessible basis.

## 5.6 Episodic, factual, procedural, normative, and negative memory

| Type | Example | Retention policy |
|---|---|---|
| Episodic | “Attempt X failed on commit A” | Decay; useful for diagnosis/replay |
| Factual | “Module uses PostgreSQL 17” | Validate against current source; invalidate by version |
| Procedural | “Run schema validation before tests” | Promote after repetition/validation |
| Normative | “Do not change public API” | Pinned; only explicit authority changes it |
| Negative | “Hypothesis H was rejected by evidence E” | Preserve while problem class remains relevant |

Normative memory cannot be inferred from frequency; authority, not observation count, gives it force. Procedural memory may emerge from repeated experience but needs validation to avoid fossilizing temporary workarounds.

## 5.7 Project scope and multi-agent isolation

```text
organization memory
      ↓
project memory
      ↓
run memory
      ↓
task memory
      ↓
agent working memory
```

Subagents should not automatically receive the whole organizational corpus. A planner may need ADRs/roadmap; a test runner needs commands/environment; a reviewer needs invariants/diff. The source calls this **least context privilege**.

# 6. Overseer loop and session lifecycle

## 6.1 Logical entity versus physical session

The Overseer may persist as role identity, policies/permissions, accumulated metrics, decision history, validated memory, task ownership, and workflow state. It does **not** need to persist as one model conversation.

```text
Logical Overseer
 ├── physical session for Task A
 ├── physical session for Task B
 └── physical session for Task C
```

Historical recommendation: **each meaningful backlog item starts with a fresh context**. Compaction is primarily intra-task, not a mechanism for dragging dozens of tasks through one session.

## 6.2 Operational loop

```text
claim backlog item
  ↓
create Task Ledger + fresh session
  ↓
hydrate constitution, playbooks, minimum state
  ↓
plan / delegate
  ↓
execute / integrate / review
  ↓
incremental GC + fold completed units
  ↓
integration / regression tests
  ↓
commit or rollback
  ↓
completion capsule + bookkeeping
  ↓
propose memory promotions
  ↓
close physical session
  ↓
next item
```

## 6.3 Minimum hydration

Include effective constitution/policies, Overseer role/scope, task contract and acceptance criteria, current repository state, selected playbooks, relevant dependencies/decisions, specifically retrieved memories, evidence/artifact index, and next action/initial phase.

Do **not** include by default: prior-task transcripts, all playbooks, whole backlog, old logs/status messages, superseded results, or every semantically similar memory.

## 6.4 Canonical checkpoint

```yaml
checkpoint:
  task_id:
  objective:
  acceptance_criteria: []
  active_constraints: []
  current_phase:
  repository:
    branch:
    base_commit:
    head_commit:
    dirty_files: []
  decisions:
    - decision:
      rationale:
      evidence_refs: []
  completed_work: []
  remaining_work: []
  modified_artifacts: []
  tests:
    latest_per_suite: []
    unresolved_failures: []
    artifact_refs: []
  active_agents: []
  unresolved_questions: []
  rejected_hypotheses: []
  risks: []
  next_action:
  provenance:
    trajectory_id:
    source_event_range:
    policy_versions: []
```

## 6.5 Completion Capsule

```yaml
completion:
  task_id:
  final_status:
  acceptance_criteria_results: []
  commits: []
  changed_files: []
  test_evidence: []
  known_limitations: []
  follow_up_tasks: []
  rollback_instructions:
  trajectory_ref:
```

The session closes only after commit/rollback decision, bookkeeping, and persisted completion capsule.

# 7. Subagents: internal compaction and folding at the boundary

## 7.1 Two distinct boundaries

**Internal compaction** lets a subagent continue a task that exceeds its budget. **Parent-child folding** protects the Overseer from the child’s exploratory trajectory. Even if a child never compacts internally, its return should be condensed and typed.

## 7.2 Subagent classes

- **S0 — Atomic:** few tools, simple objective, short output. No semantic mid-task compaction; GC large outputs; mandatory final fold; destroy session.
- **S1 — Focused:** e.g. module review or failure investigation. Continuous minor GC/offloading; preserve active investigative path; compact only under genuine pressure; typed final fold.
- **S2 — Multi-phase:** e.g. plan/implement/test/review a bounded change. Checkpoint by phase; fold completed phase; keep current phase high-fidelity; optional reset between phases.
- **S3 — Long-running:** multiple phases/modules/sub-subagents and expected repeated compactions. Re-decompose into its own workflow or checkpoint/reset/continue.

If a child needs three or more compactions without approaching completion, emit `DELEGATION_TOO_COARSE`.

## 7.3 Do not compact open reasoning state

While an investigation is causally open, preserve structured uncertainty:

```yaml
active_investigation:
  hypothesis:
  supporting_evidence: []
  contradicting_evidence: []
  missing_evidence: []
  confidence:
  next_probe:
```

MAGE, Context-Folding, and SelfCompact are cited as convergent evidence for compacting around semantic boundaries/subproblems rather than blindly by age or token threshold.

## 7.4 Return contract

```yaml
subagent_result:
  task_id:
  subtask_id:
  role:
  status: completed | partial | blocked | failed
  objective:
  conclusion:
  requirements_checked: []
  work_performed:
    files_read: []
    files_changed: []
    commands_executed: []
  decisions:
    - decision:
      rationale:
      evidence_refs: []
  findings: []
  tests:
    commit:
    executed: []
    passed: []
    failed: []
    artifact_refs: []
  rejected_hypotheses: []
  unresolved_questions: []
  risks: []
  recommended_next_action:
  confidence:
  raw_trajectory_ref:
```

The parent receives the capsule; raw trajectory remains retrievable.

## 7.5 Recursive subagents

Each level folds its own children, but intermediate summaries must not become the only source. Claims should point directly to original artifacts/evidence.

## 7.6 Comparative evidence: no compaction, mid-task compaction, folding

The source states that no dominant benchmark isolates just “compact or do not compact a coding subagent mid-task.” Evidence was indirect but convergent: Context-Folding, MAGE, and HiAgent report benefits from structuring memory around completed branches/subgoals rather than arbitrary intervals. The safe hypothesis is narrower than “compaction is always good”:

> **Compacting semantically completed units is safer than compacting the active trajectory solely by age or threshold.**

**Do not compact** short atomic work where summary overhead exceeds savings. **Compact mid-task** when a subgoal is closed, produced state is persisted, result is schematizable, context pressure is real, and continuity depends on a small set of explicit invariants. **Reset** when the working set changes radically, multiple summaries accumulate, contradictions persist, or the “subtask” has become a multi-phase workflow.

## 7.7 Delegation is a contract, not an informal mini-prompt

```yaml
delegation_contract:
  id: del-491
  parent_agent: overseer-1
  child_role: security-reviewer
  objective: "Review authentication and authorization in the current diff"
  scope:
    commits: [a81d4c2]
    paths: ["src/auth/**"]
  constraints:
    - read_only
    - no_network
  expected_artifacts:
    - finding_ledger
  completion_criteria:
    - all_changed_auth_paths_reviewed
  return_schema: subagent_result/v2
```

## 7.8 Recursive folding and cumulative loss

To limit cumulative loss in agent trees:

- every claim gets a stable ID;
- every claim references original evidence;
- intermediate summaries do not replace artifacts;
- the Overseer can retrieve descendant trajectory fragments;
- conflicts between children enter a ledger rather than being silently resolved by the compressor.

## 7.9 Small models and micro-management

The historical analysis of little-coder treats model/harness fit as a first-order variable. Small models should get smaller tasks, stricter schemas, and less discretion over forgetting. The engineering lesson is not to copy its exact thresholds but to copy the discipline of telemetry, guards, selective skill injection, context watchdogs, state-machine resume after compaction, and measurement of whether compaction actually reclaimed context.

# 8. Context garbage collection

## 8.1 Definition

Context garbage collection is lifecycle control over objects in the active view. It does **not** erase the trajectory store; it removes from the model window what no longer needs to remain actively present.

Self-GC frames the problem in terms of indexed/retrievable objects with fold, mask, and prune operations, planning, and harness enforcement (Hao et al., 2026). CWL proposes typed dependency-linked episodes with deterministic eviction when effects have already been persisted (Semenov & Dorofeev, 2026).

## 8.2 Eligibility criterion

An object is a candidate when:

```text
no known future action depends on it
+ its effect is persisted
+ it is not unique evidence
+ it has no normative authority
+ it does not represent an open side effect
+ it is recoverable or regenerable
```

**Age alone is insufficient.**

## 8.3 What should leave the active view

**Persisted tool outputs:** saved logs, workspace file contents, build results converted into reports, archived API responses, Git-recoverable diffs.

**Duplicates:** repeated reads of the same file/commit, identical listings/errors, repeated playbooks, semantically redundant documents.

**Superseded results:** tests from older commits, replaced plans/diffs/state snapshots/reviews.

**Completed episodes:** edit-protocol exchanges whose effects are already in Git, exploration converted into a structured map, completed subagents, completed process polling, accepted/externalized plans.

**Out-of-phase skills/tools:** schemas and playbooks should be progressively disclosed rather than permanently resident.

## 8.4 What must be pinned

- system/developer instructions;
- constitution and policy;
- human instructions;
- objective and criteria;
- constraints;
- open side effects;
- active hypothesis;
- unresolved counterevidence;
- latest valid test execution;
- next action;
- pending rollback.

The Governance Decay preprint is used not as a universal quantitative truth but as evidence for a strong principle: **governance is not collectible heap state**.

## 8.5 Agentic mark-and-sweep

### Roots

- **Governance roots:** policies/instructions.
- **Task roots:** objective, criteria, constraints.
- **Execution roots:** active plan, jobs, side effects.
- **Reasoning roots:** open hypotheses/questions.
- **Evidence roots:** evidence supporting live decisions.

### Mark

Traverse dependencies, e.g.:

```text
next action
 → current plan
 → decision D12
 → test-run-44
 → commit a18f2
```

### Sweep

Classify unmarked objects:

```text
RECOVERABLE → fold/offload
STRUCTURAL  → mask
OBSOLETE    → prune
UNCERTAIN   → retain
AUTHORITY   → pin
```

## 8.6 Generational GC

- **Generation 0 — ephemeral:** tool outputs, file reads, search results, polling, scratch. Minor GC after tool cycles.
- **Generation 1 — phase:** local plans, partial results, hypotheses, tests. Collect at subgoal boundaries.
- **Generation 2 — task:** task contract, decisions, latest validated state. Fold at task completion.
- **Pinned generation:** policies, user corrections, trust boundaries. Never automatically collectible.

## 8.7 Triggers

```text
POST_TOOL_RESULT
POST_FILE_READ
POST_TEST_RUN
POST_SUBAGENT_RESULT
SUBGOAL_COMPLETED
PHASE_COMPLETED
PRE_MODEL_CALL
PRE_COMPACTION
PRE_RESET
TASK_COMPLETED
```

Use predicted pressure rather than waiting for overflow:

```text
projected_next_context =
    active_tokens
  + expected_tool_result
  + expected_model_output
  + reserve
```

ContextBudget is cited as a research direction that frames compression as sequential decision-making under budget (Wu et al., 2026).

## 8.8 Fold, mask, prune

- **Fold:** move exact payload to a sidecar/artifact and leave a pointer; preferred when literal recovery may be needed.
- **Mask:** retain structure, URL/title, boundaries, and relevant snippets while hiding repetitive body.
- **Prune:** remove entirely from active view only when obsolescence and lack of live dependencies are established.

Conservative preference: `fold > mask > prune`.

## 8.9 Cache-aware GC

Changing a prefix can invalidate prompt caches. The proposed decision function is qualitative/quantitative rather than “collect whenever possible”:

```text
expected benefit =
    future_calls × tokens_removed
  - cache_break_cost
  - collector_cost
  - future_retrieval_cost
```

The historical Anthropic context-editing surface is used as an example of this trade-off rather than as proof of an optimal policy.

## 8.10 Protocol correctness

Tool call and result are atomic spans. The collector may keep the span, replace a result with a valid pointer, normalize call/result, or remove the complete span at a safe boundary—but must not leave malformed protocol state.

## 8.11 Object-oriented GC versus chronological trimming

Chronological trimming asks *which messages are oldest?* Object GC asks *which objects are still reachable from live state?* An old constraint may remain live; a five-second-old log may be disposable once persisted and parsed.

Self-GC and CWL are used as convergent research signals for moving from message-centric to object/dependency-centric context management. Their reported numbers remain scoped to their experimental setups.

## 8.12 Minor, major, and final GC

### Minor GC

Frequent, preferably non-LLM: large-output offload, hash deduplication, repeated-poll removal, replace file content with `path + commit + symbols`, preserve protocol pairs, update `latest` and `superseded_by` relations.

### Major GC

At boundaries: dependency sweep, completed-phase folding, normalize subagent results, turn rejected hypotheses into negative memory, evaluate cache economics, prepare for compaction/reset.

### Final GC

At task closure: completion capsule, candidate-memory promotion, close processes/leases, archive trajectory, destroy physical session.

## 8.13 Cache economics and commit timing

A small cleanup immediately before completion may cost more than it saves. The harness can estimate:

```text
net_value(gc_plan) =
    expected_future_calls × tokens_removed × token_cost
  - collector_cost
  - cache_rebuild_cost
  - expected_retrieval_cost
  - risk_penalty
```

It need not be a perfect monetary model; its purpose is to prevent nervous GC on every small opportunity.

## 8.14 Malicious collection resistance

Untrusted repository/web/tool content may try to persuade the model that a policy is obsolete or a log irrelevant. The collector must operate on compiled metadata/policy rather than execute instructions found inside payloads. Only authorized sources can change `pinned`, `authority`, or normative retention.

## 8.15 Non-text resource GC

The same lifecycle discipline should cover worktrees, sandboxes, containers, processes, ports, locks, temporary files, browser sessions, partial downloads, and worker leases. A live process is a root; final task GC closes or transfers ownership. This avoids “clean context, leaking runtime.”

# 9. Compaction profiles

## 9.1 Generic profile

A generic profile applies the same rules to every task: keep instructions, summarize older messages, retain a recent tail, remove large outputs. LLMLingua-2 is cited as an efficient task-agnostic/extractive baseline (Pan et al., 2024).

**Advantages:** portability, low cost, comparability.  
**Limitation:** blindness to operational semantics, decisions, and causality.

## 9.2 Query-aware profile

LongLLMLingua uses query relevance, coarse-to-fine compression, and document reordering (Jiang et al., 2024). In an agent, the “query” may be the next decision/action. The risk is removing something irrelevant *now* but necessary later.

## 9.3 Task-specific profiles

**Coding:** branch/commits, changed files/symbols, criteria, decisions, latest test per suite, active failures, rejected patches, next action.

**Research:** questions, claims, supporting/opposing sources, evidence grade, gaps, provisional conclusions.

**Incident:** timeline, affected systems, interventions, active/rejected hypotheses, rollback state.

## 9.4 Content-adaptive profile

Intensity varies with information density: duplicate logs → aggressive; conflicting decisions → conservative; persisted file → offload; rationale without external artifact → retain narrative.

## 9.5 Learned profile

ACON, ContextBudget, and Neural Garbage Collection are treated as research signals that compression/eviction policies can be learned. Because these are bleeding-edge methods, the source does not let learned policy replace deterministic validation.

## 9.6 On-the-fly compaction

Three levels are distinguished:

1. dynamically select a canonical profile;
2. generate an overlay/rubric;
3. learn a folding/eviction policy.

SelfCompact is cited for evidence that models vary in their ability to use a compaction tool effectively and may need explicit safe-boundary guidance.

## 9.7 Hybrid architecture

```text
Canonical Kernel
  fields no overlay may remove

Task Profile
  semantics of the task class

Dynamic Overlay
  additional on-the-fly fields/granularity

Runtime Policy
  trigger, budget, fold, reset

Integrity Gate
  validation

Raw Archive
  reversibility
```

Example historical schema:

```yaml
compaction_profile:
  id: coding-implementation-v1
  version: 1
  trigger:
    token_pressure: 0.70
    semantic_boundaries:
      - plan_completed
      - implementation_completed
      - subagents_joined
  canonical_preservation:
    policies: exact
    objective: exact
    acceptance_criteria: exact
    active_constraints: exact
    task_identity: exact
  structured_preservation:
    decisions: evidence_linked
    modified_artifacts: latest
    tests: latest_per_commit
    rejected_hypotheses: summarized
    unresolved_failures: full
    next_action: exact
  externalize:
    raw_logs: true
    subagent_transcripts: true
    superseded_file_contents: true
  dynamic_overlay:
    enabled: true
    allowed_to_add_fields: true
    allowed_to_remove_canonical_fields: false
  validation:
    schema: required
    constraint_recall: 1.0
    contradiction_count: 0
    evidence_resolution: required
    recovery_probe: required
```

## 9.8 Comparing compaction and folding research

| Work | Managed unit | Adaptation | Main contribution | Relevant limitation |
|---|---|---|---|---|
| LongLLMLingua | tokens/spans | query-aware | query-guided compression/reordering | not full agent-state model |
| LLMLingua-2 | tokens | task-agnostic | small transferable compressor | may miss operational causality |
| HiAgent | subgoals | hierarchical | working memory by task progress | depends on good decomposition |
| ACON | compaction guidelines | feedback-adaptive | learns guidelines from failures | preprint / overfitting risk |
| SelfCompact | compaction decision/rubric | on-the-fly | agent decides when/how | model metacognition varies |
| Context-Folding | procedural branches | dynamic | isolates subtasks, returns folded result | needs context-tree runtime |
| FoldAct | action + folding policy | learned | addresses non-stationarity after folding | recent/complex training |
| U-Fold | intent + tool log | dynamic | intent-aware evolving summary | preprint evidence |
| MAGE | execution-state tree | adaptive | Grow/Compress/Maintain/Revise | more complex runtime |
| Self-GC | indexed objects | planner + policy | fold/mask/prune + sidecars/gates | partial judge-based evaluation |
| CWL | episodes/dependencies | deterministic | LLM-free causal eviction | needs dependency metadata |
| CompactionRL | acting + summarization | RL | joint compaction/execution for coding/terminal | generalization open |

The key point is categorical: *prompt compression*, *summarization*, *folding*, *eviction*, and *learned retention policy* solve different problems and should not be compared only by “percent tokens removed.”

## 9.9 Canonical kernel + adaptive overlay

```yaml
canonical_kernel:
  exact:
    - task_id
    - user_objective
    - acceptance_criteria
    - active_constraints
    - policy_refs
    - current_branch
    - current_commit
    - open_side_effects
  structured:
    - decisions
    - latest_tests
    - unresolved_failures
    - active_delegations
    - next_action
```

The overlay may preserve extra fields or compress more aggressively but cannot remove canonical fields or rewrite human constraints.

## 9.10 Recommended canonical profiles

- **Coding implementation:** preserve artifacts/symbols/commits/criteria/tests; externalize file reads/logs.
- **Research:** preserve claims, supporting/opposing sources, evidence grade, and gaps; compact by claim rather than chronology.
- **Incident response:** preserve timeline, current state, interventions, active/rejected hypotheses, rollback; conservative policy.
- **Review:** finding ledger tied to commit and finding resolution; remove old-version discussion only after explicit supersession.
- **Overseer:** delegation contracts, integration state, tests, commit/bookkeeping; child transcripts remain external.

## 9.11 When to use a separate compressor

A smaller model may perform task-agnostic compression or structured extraction cheaply, but it should not be sole validator of high-authority content. Proposed layers:

```text
rules/parser      → lossless cleanup
small curator     → structured candidate
strong validator  → samples / risky cases
harness           → final decision
```

# 10. Context folding and branch management

## 10.1 Concept

Folding is not “summarize all history.” It closes a localized causal unit and returns a condensed result to the main path.

```text
main context
  │
  ├── branch: investigate database failure
  │    ├── logs
  │    ├── queries
  │    ├── hypotheses
  │    └── result
  │
  └── receives:
       conclusion
       evidence
       impact
       recommended action
```

Context-Folding, FoldAct, and U-Fold are cited as early evidence for branch-aware and intent-aware folding.

## 10.2 Fold at causal boundaries

Good boundaries include closed subgoal, resolved hypothesis, analyzed module, applied patch, executed suite, or completed review. Avoid “every N messages” while the unit remains open.

## 10.3 Hierarchical folding

```text
child trajectory
  → child result capsule
  → parent working context
  → parent final capsule
  → Overseer
```

Each level retains direct references to original evidence.

## 10.4 Folding versus reset

| Condition | Folding | Reset |
|---|---|---|
| Subgoal closed | Preferred | Optional |
| High context, phase closed | Preferred | May follow |
| Open investigation degraded | Risky | Preferred with checkpoint |
| Radical working-set shift | Useful | Often preferred |
| Task end | Completion fold | Physical session should end |

## 10.5 Context tree

The source models task context as a tree of branches whose complete trajectories remain outside the main active path. Subagents are naturally branches in this model.

## 10.6 Non-stationarity and FoldAct

Folding changes future observations, so a learned policy that acts before and after folding faces a non-stationary environment. FoldAct is cited as an attempt to train this interaction rather than treating summarization as an independent preprocessor.

## 10.7 Intent-aware folding

For interactive agents, what matters can change with user intent. U-Fold is cited as a dynamic approach retaining selected tool logs and adapting summaries to changing intent.

## 10.8 Folding versus typed artifacts

When a subtask can be represented exactly by a typed artifact—patch, test report, dependency map, finding ledger—the artifact should carry the ground truth while the fold carries the compact interpretation and references.

# 11. Lost in the Middle and position-aware packing

## 11.1 Do not create a monolithic “historical memory” section

The source proposes position-aware packing, roughly distinguishing beginning, early-middle, middle, late-middle, and end. High-authority and task-defining material belongs in reliable positions; retrieved evidence should be selected and arranged, not dumped chronologically.

## 11.2 Controlled redundancy

Critical constraints may be represented both in a canonical pinned block and near the action/output contract. Redundancy is deliberate when it protects high-authority information from positional loss.

## 11.3 Retrieval before ordering

First decide *what* belongs in the observation; then decide *where* it should go. Attention-aware packing cannot rescue a retrieval set dominated by irrelevant history.

## 11.4 Negative memory

Rejected hypotheses should be compact but retrievable, so the model does not repeat known failures while also not letting failed trajectories dominate attention.

## 11.5 Two-pass packing

1. **Selection:** scope, version, trust, dependencies, relevance, counterevidence.
2. **Ordering:** authority and objective early, active state and evidence in structured regions, current action/output contract late.

## 11.6 Counterevidence budget

A packer should reserve capacity for evidence that contradicts the current hypothesis rather than optimizing only for supportive relevance.

## 11.7 Harness-owned positional benchmarks

The experimental program later places the same rule/evidence at multiple positions and volumes to measure literal retrieval, semantic association, rule application, tool-result attribution, post-compaction retention, and final-review consistency.

# 12. Vendor and open-model comparison

## 12.1 Compare control surfaces separately from semantic quality

The source compares documented primitives, not just “who has the biggest context.” Native vendor behavior mixes model, hidden prompt, CLI runtime, compaction algorithm, and cache behavior, so product comparisons and causal comparisons require different tracks.

## 12.2 Codex — historical reading

The source records Codex configuration around model context, auto-compaction thresholds/counting, PreCompact/PostCompact hooks, isolated subagent threads, and externalized planning/state for long-running work. It also records issue/discussion signals around hook receipts, post-compaction reinjection, explicit compaction control, and persistent memory. Those issues are field evidence, not universal claims.

## 12.3 Claude Code / Anthropic API — historical reading

PreCompact/PostCompact and SessionStart-style reinjection, context editing for tool results/thinking blocks, and isolated subagents are treated as primitives useful to an external policy. Reported issues about lost paths/history/checkpoints motivate validation and restore UX but are not controlled statistics.

## 12.4 Kimi Code CLI — historical reading

The source records auto-compaction triggers and beta PreCompact/PostCompact hooks, noting fail-open behavior in the cited documentation. The architectural conclusion is that fail-open hooks cannot be the sole enforcement boundary.

## 12.5 Gemini CLI / Google ADK — historical reading

Gemini CLI checkpointing and ADK token/sliding-window/custom summarizer mechanisms are treated as separate surfaces; the document warns against conflating CLI, ADK, and Live API behavior.

## 12.6 Open models

Open models allow model weights/runtime to be held fixed while policy changes. SelfCompact and CompactionRL are cited as early evidence that compaction behavior can be explicitly guided or trained, enabling empirical `ModelContextProfile`s for local model families.

## 12.7 Fair comparison protocol

- **Native vs native:** product benchmark; mixes model + CLI + algorithm.
- **Common external checkpoint/compressor:** measures resumability across executors.
- **Same open model, different profiles:** best causal route for policy ablations.

A reproducible result also records CLI version, model snapshot, settings, hooks, tools, cache, and compaction-cycle count.

# 13. Lessons from other harnesses

## 13.1 Magentic-One

Separate Task Ledger from Progress Ledger; detect stagnation and replan explicitly (Fourney et al., 2024).

## 13.2 MetaGPT

Roles/SOPs and intermediate artifacts motivate exchange of typed objects rather than whole transcripts. Rigid SOPs can still add overhead in simple work.

## 13.3 SWE-agent

Agent-Computer Interface design materially changes performance; narrow tools, structured observations, and safe editing can matter more than large prompts.

## 13.4 Agentless

Simple localization→repair→validation pipelines remain competitive in important classes. Multi-agent/folding/memory machinery should be activated by need rather than by default.

## 13.5 AutoCodeRover

Use code structure—symbols, calls, tests, ownership, Git—to localize context before generic semantic retrieval.

## 13.6 LangChain Deep Agents

Offload large tool inputs/results first, use filesystem and progressive skills, isolate subagent windows, and summarize later. The source explicitly prefers **offload before summarize**.

## 13.7 little-coder

The case study is used as engineering evidence that scaffold-model fit matters, especially for smaller models: model-specific budgets, narrower tools, selective skill injection, deterministic output parsing, guards, thinking budgets, and compaction watchdogs. The source refuses to import its exact thresholds as universal rules.

### Transferable lessons for small models

- fewer active goals;
- smaller tool/schema surfaces;
- deterministic output parsing;
- less discretion over free-form summarization;
- earlier re-decomposition;
- stronger model/rules as validator;
- model-specific budgets.

### Do not copy without experiments

Universal thresholds, generic head/tail truncation, benchmark-specific prompts, free-form summaries as canonical truth, or automatic trust in recent memory.

## 13.8–13.13 Broader synthesis

The document revisits the same projects through a context-governance lens: ledgers reduce churn; artifacts should outlive dialogue; ACI design avoids generating unnecessary context; structural retrieval reduces repository loading; filesystem offload improves reversibility; and runtime context management must be an observable state-machine operation, not a side command presumed to have worked.

# 14. Proposed architecture: Context Control Plane

> **Historical PROPOSED architecture.** This is not automatically the current tare.tools bounded-context model.

```text
┌─────────────────────────┐
│ Vendor Agent Adapter    │
│ Codex / Claude / Kimi   │
└────────────┬────────────┘
             │ telemetry / hooks / events
┌────────────▼────────────────────────────────┐
│ CONTEXT CONTROL PLANE                       │
├─────────────────────────────────────────────┤
│ 1. Context Telemetry                        │
│ 2. Budget Controller                        │
│ 3. Object Registry & Dependency Graph       │
│ 4. Artifact / Evidence / Trajectory Store   │
│ 5. Garbage Collector                        │
│ 6. Retrieval & Reranking                    │
│ 7. Attention-Aware Packer                   │
│ 8. Context Curator                          │
│ 9. Folding Orchestrator                     │
│10. Compaction Profile Compiler              │
│11. Integrity Gate                           │
│12. Reset & Rehydration                      │
│13. Memory Promotion                         │
└────────────┬────────────────────────────────┘
             │ minimum sufficient context
┌────────────▼────────────┐
│ Overseer / Subagent     │
└─────────────────────────┘
```

## 14.1 Context telemetry

```yaml
context_usage:
  vendor:
  agent:
  model:
  physical_limit:
  safe_limit:
  reliable_limit:
  operational_limit:
  current_tokens:
  system_tokens:
  tool_tokens:
  conversation_tokens:
  summary_tokens:
  reserved_output:
  projected_next_tokens:
  pressure_ratio:
```

## 14.2 Budget Controller

A historical starting example allocates rough percentages across authority, task contract, active state, retrieved evidence, code/tool results, conversation tail, and output/recovery reserve. The source says these percentages require calibration rather than hard-coding as universal constants.

## 14.3 Compaction Profile Compiler

Combines canonical kernel, task profile, model profile, runtime state, model-proposed overlay, and security policy. The model cannot remove canonical fields.

## 14.4 Integrity Gate

**Deterministic checks:** task ID, objective, criteria, constraints, branch/commits, artifacts, latest test per suite, active jobs, dependencies, next action.

**Semantic checks:** compare prior checkpoint, trajectory range, and compacted output.

```yaml
compaction_validation:
  goal_fidelity:
  constraint_recall:
  decision_recall:
  evidence_recall:
  contradiction_count:
  unsupported_claims:
  resumability:
```

Historical minimum policy:

```text
constraint_recall < 1.0  → reject
contradiction_count > 0  → reject
unsupported_claims > 0   → repair/reject
resumability != pass     → reset + rehydrate
```

## 14.5 Recovery Probe

```yaml
context_probe:
  task_id:
  objective:
  mandatory_constraints: []
  current_phase:
  latest_test_status:
  biggest_open_risk:
  next_action:
```

The answer is compared with canonical run state and is not itself sole truth.

## 14.6 State machine

```text
HYDRATED
   ↓
ACTIVE
 ├── minor_gc ──────────────┐
 ├── fold_completed_unit ───┤
 ├── checkpoint ────────────┤
 ├── compact → validate ────┤
 ├── reset → rehydrate ─────┤
 └── complete → final_gc → CLOSED
```

## 14.7 Historical pseudocode

```python
while backlog.has_eligible_items():
    task = backlog.claim_next()
    session = overseer.new_session(
        constitution=load_effective_constitution(task),
        playbooks=retrieve_playbooks(task),
        project_context=retrieve_project_context(task),
        task_capsule=create_task_capsule(task),
    )

    while not task.is_terminal:
        event = execute_next_overseer_step(session, task)
        ingest_and_persist(event)
        run_minor_gc(session)

        pressure = predict_context_pressure(session)

        if task.has_completed_subgoal and pressure > FOLD_THRESHOLD:
            fold_completed_subgoal(session, task)

        if pressure > MAJOR_GC_THRESHOLD and at_safe_boundary(task):
            run_major_gc(session)

        if pressure > COMPACTION_THRESHOLD and at_semantic_boundary(task):
            checkpoint = create_checkpoint(task, session)
            compact_with_effective_profile(session, checkpoint)
            validate_context_integrity(session, checkpoint)

        if pressure > RESET_THRESHOLD or behavioral_degradation(session):
            checkpoint = create_validated_checkpoint(task, session)
            session = reset_and_rehydrate(checkpoint)

    run_integration_and_regression_gates(task)
    commit_or_rollback(task)
    write_completion_capsule(task)
    propose_memory_delta(task)
    perform_bookkeeping(task)
    session.close()
```

## 14.8–14.10 Logical components and capability contract

Historical component roles include Context Object Registry, Dependency Graph, Context Budget Controller, Context Curator, Integrity Gate, and Vendor Adapter. The vendor capability contract records whether usage is exact/estimated; whether native compaction is manual/automatic/configurable; hook semantics; isolated subagent threads; transcript references; and selective context-editing support.

The safe rule is capability-aware policy: a fail-open hook cannot serve as the sole gate; a blocking hook can participate in stronger enforcement; a provider-specific summarizer remains an adapter capability rather than architectural truth.

## 14.11 Context assembly algorithm

```python
def build_context(agent, task, next_action):
    profile = profiles.resolve(agent.role, task.family, task.phase)
    budget = budgets.compute(agent.model_profile, profile, next_action)

    roots = state.load_pinned_roots(task)
    active = state.load_active_state(task, agent)
    candidates = retrieval.query(task, next_action, profile)

    candidates = filter_by_scope_version_trust(candidates, task)
    candidates = remove_superseded(candidates)
    candidates = add_dependencies(candidates, active)
    candidates = rerank_with_counterevidence(candidates, next_action)

    packed = packer.layout(
        authority=roots,
        active_state=active,
        evidence=candidates,
        budget=budget,
        model_profile=agent.model_profile,
    )
    return integrity.validate_pre_inference(packed)
```

## 14.12 Validated compaction algorithm

```python
def compact_session(session, trigger):
    before = checkpoint.create(session)
    assert integrity.validate_checkpoint(before)

    profile = profile_compiler.compile(
        canonical=before.canonical_kernel,
        task_profile=profiles.for_task(before.task),
        dynamic_overlay=curator.propose(before, trigger),
    )
    profile = policy.constrain(profile)

    result = vendor.compact(session, profile)
    validation = integrity.compare(before, result)

    if not validation.pass_all:
        repaired = repair.from_canonical_state(before, result)
        if not integrity.compare(before, repaired).pass_all:
            return reset_and_rehydrate(before)
        return repaired
    return result
```

## 14.13 Re-decomposition decision

Track `compaction_count`, `gc_yield`, `recovery_reads`, and stalls. A subtask that repeatedly compacts with little progress receives `DELEGATION_TOO_COARSE`, and the Overseer converts remaining state into smaller tasks rather than creating an indefinite chain of summaries.

# 15. Profiles by role and task class

## 15.1 Overseer

```yaml
overseer_profile:
  preserve:
    - task_contract
    - workflow_phase
    - active_agents
    - delegation_contracts
    - decisions
    - integration_state
    - latest_tests
    - commit_state
    - bookkeeping_state
    - unresolved_conflicts
    - next_control_action
  externalize:
    - subagent_transcripts
    - raw_logs
    - file_contents
    - superseded_plans
```

## 15.2 Planner

Preserve objective, constraints, current architecture, considered options, selected decision, and risks. Fold exploration after a plan is accepted.

## 15.3 Implementer

Preserve changed files/symbols, base/HEAD, rationale, failures, and next patch. Aggressively GC recoverable file reads and already-persisted tool-protocol material.

## 15.4 Reviewer

Findings should be independent and commit-bound:

```yaml
finding:
  id:
  severity:
  file:
  lines:
  claim:
  evidence_refs: []
  proposed_fix:
  commit_reviewed:
  status:
```

## 15.5 Researcher

Compact by claim, not page chronology. Preserve contradictory evidence and evidence quality.

## 15.6 Incident Agent

Use a conservative profile. Timeline, current system state, interventions, rollback, and active causal chain are not automatically collectible.

## 15.7 Test Runner

Can be aggressive because raw output is highly externalizable:

```yaml
test_result:
  command:
  commit:
  status:
  failures: []
  relevant_stacks: []
  raw_ref:
```

## 15.8 Small Model Strict

```yaml
small_model_profile:
  maximum_active_goals: 1
  maximum_open_hypotheses: 3
  maximum_inline_evidence_items: 5
  skill_budget: small
  tool_output_budget: strict
  reasoning_budget: explicit
  task_schema: mandatory
  response_schema: mandatory
  compaction:
    deterministic_cleanup_first: true
    freeform_summary: restricted
    validator: stronger_model_or_rules
    max_compactions_per_subtask: 1
```

# 16. Experimental program

## 16.1 Hypotheses

- **H1.** Canonical checkpoint + GC + folding outperforms native compaction alone on fidelity and stability.
- **H2.** Reset per backlog item reduces cross-task confusion without excessive cost-to-success.
- **H3.** Task-specific profiles outperform generic profiles on heterogeneous tasks.
- **H4.** On-the-fly overlays improve compaction only when canonical fields are immutable and an integrity gate exists.
- **H5.** Dependency-oriented GC may reclaim fewer tokens than oldest-first but better preserve downstream outcomes.
- **H6.** Isolated subagents + fold contract reduce Overseer pollution and improve integration.
- **H7.** Structured negative memory reduces contextual drag relative to full transcripts of failed attempts.
- **H8.** Smaller models obtain larger marginal benefit from micro-management, tool guards, and mandatory schemas.

## 16.2 Strategies

```text
A0 full transcript
A1 oldest-first truncation
A2 native default compaction
A3 generic external summary
A4 canonical checkpoint
A5 checkpoint + structural GC
A6 task-specific profile
A7 on-the-fly profile
A8 subgoal folding
A9 full hybrid + integrity gate
A10 phase/task reset
```

## 16.3 Task classes

Bug fix, long feature, refactoring, schema migration, security review, CI diagnosis, technical research, incident, documentation, and an Overseer coordinating multiple subagents.

## 16.4 Positional benchmark

Place the same constraint/evidence at 1%, 5%, 10%, 25%, 50%, 75%, 90%, 95%, and 99% of the context, at volumes from 8K through the maximum supported window. Measure literal retrieval, semantic association, rule application, tool-result attribution, retention after compaction, and consistency in final review.

## 16.5 Contextual-drag experiment

Compare: full failed attempt; narrative summary; complete removal; typed negative memory; recoverable external reference.

## 16.6 Subagent experiment

Compare S0 no GC, S1 minor GC, S2 fold by phase, S3 threshold compaction, S4 checkpoint+reset, S5 re-decomposition.

## 16.7 Vendor benchmark

- **Track A — product:** Claude native, Codex native, Kimi native, Gemini native.
- **Track B — common representation:** same external checkpoint delivered to every executor.
- **Track C — local models:** same model with different context policies.

## 16.8 Metrics

**Fidelity:** goal/criterion/constraint/decision/negative-memory recall; evidence-attribution accuracy.  
**Continuity:** resume success; unnecessary rereads; repeated failure; stale-plan execution; contradictions; premature completion.  
**Economics:** peak active tokens; total input/tool tokens; compaction/retrieval cost; latency; cost-to-success.  
**GC:** tokens reclaimed; critical-object false-positive rate; future-dependency preservation; artifact recovery; cache-invalidation cost.  
**Multi-agent:** cross-agent duplication; parent re-query rate; capsule sufficiency; finding deduplication; error-propagation depth; marginal gain per agent.

## 16.9 ModelContextProfile

```yaml
model_context_profile:
  vendor:
  model:
  cli_version:
  advertised_window:
  safe_physical_limit:
  reliable_limits:
    code_editing:
    log_analysis:
    architecture_review:
    research:
  position_profile:
    beginning:
    early_middle:
    middle:
    late_middle:
    end:
  metacognition:
    autonomous_compaction_reliability:
    rubric_required:
    schema_compliance:
  recommended:
    minor_gc_at:
    major_gc_at:
    compact_at:
    reset_at:
    maximum_subtask_compactions:
```

## 16.10 Factorial design and ablations

Begin with paired/fractional-factorial experiments rather than the full combinatorial matrix. Relevant factors include strategy × model × task family × task length × tool volume × subagent topology × compaction cycles × policy strictness.

A useful first controlled set keeps model/tasks fixed and varies: full transcript, minor GC, GC+canonical checkpoint, generic summary, task profile, task profile+overlay, subgoal folding, checkpoint+reset.

## 16.11 Repeated-compaction benchmark

Run 1, 3, 5, and 10 compaction cycles over synthetic and real trajectories. Measure constraint recall, decisions/rationales, conflicting evidence, test-commit attribution, next action, unsupported claims, size, and resume success. Compare recursive summary with regeneration from canonical state.

## 16.12 Garbage-collection benchmark

Label objects `LIVE / PINNED / FOLDABLE / MASKABLE / PRUNABLE`. Penalize critical false positives far more than false negatives. Measure tokens reclaimed, future dependency preservation, artifact recovery, and cache-adjusted savings.

## 16.13 Subagent benchmark

Compare child without compaction, minor GC, threshold compaction, subgoal folding, phase reset, and re-decomposition across exploration, implementation, review, incident, and research. Also measure how often the parent has to reopen child trajectory.

## 16.14 Vendor comparison

Product track measures end-to-end experience; common-representation track measures resume capability; open-model track provides stronger causal attribution to policy.

## 16.15 Delayed metrics

Compaction may look correct immediately and cause an error five steps later. Track later regression, task reopening, lost findings, wrong memory promotion, rollback, and human intervention.

## 16.16 Reproducibility

Record harness/repository commit, model snapshot, CLI version, prompt/profile/policy versions, trajectory IDs, cache settings, seeds where available, budgets/timeouts, and complete artifacts.

# 17. Security, governance, and auditability

## 17.1 Context management is a security surface

Compaction, GC, retrieval, and packing can remove policies, prioritize adversarial content, hide counterevidence, carry malicious repository instructions, promote contaminated memory, detach tests from commits, or lose open side-effect state.

## 17.2 Separation of authority

```text
proposal_agent != approval_authority
compressor != sole_validator
memory_writer != policy_authority
```

## 17.3 Constraint pinning

Constraints are rendered from canonical source on every rehydration and never delegated to free-form summarization.

## 17.4 Provenance

```yaml
provenance:
  trajectory_id:
  source_events:
    from:
    to:
  compressor:
  model:
  profile_version:
  source_hash:
  created_at:
  validator:
  validation_result:
```

## 17.5 Recoverability

Every fold should have artifact reference, scope, preview, hash, permissions, retention, and recovery method.

## 17.6 Memory promotion

Candidate memories require evidence, scope, confidence, temporal validity, conflict checks, and confirmation by later runs or review.

```yaml
memory_candidate:
  type:
  statement:
  evidence_refs: []
  project_scope:
  confidence:
  validation_status:
  expires_at:
```

## 17.7 Context injection and contaminated memory

Repository/web/tool payloads are data, not authority. Only the control plane may change authority/pinned/trust/retention metadata. Retrieved memories also require provenance, scope, version range, confidence, and revocation status.

## 17.8 Right to erasure versus auditability

Active context, trajectory storage, and long-term retention are separate concerns. Permanent deletion follows privacy/retention/legal policy; revocation may preserve tombstone metadata without retaining sensitive content.

## 17.9 Separation of duties

For high-risk work: executor ≠ curator, curator ≠ validator, proposal agent ≠ approval authority. Low-risk tasks may combine roles for economy; policy/security/self-evolution changes require stronger separation.

# 18. Trade-offs, limitations, and threats to validity

1. **Accidental complexity:** a full Context Control Plane can cost more than it saves on short tasks. Agentless motivates progressive complexity and atomic-task bypasses.
2. **Recent preprints:** Self-GC, CWL, MAGE, SelfCompact, Governance Decay, ContextBudget, NGC, U-Fold, and related work require replication across models, harnesses, languages, side effects, and repeated compaction.
3. **Judge-based evaluation:** supplement LLM judges with deterministic criteria, real task success, tests/hashes, and sampled human review.
4. **Vendor drift:** record versions and snapshots.
5. **Prompt-cache effects:** token-efficient GC may hurt latency/cost through cache invalidation.
6. **Cumulative summary distortion:** require references/reversibility.
7. **Hidden reasoning:** architecture must depend on verifiable operational state, not access to private chain of thought.
8. **Privacy/retention:** full trajectories may contain sensitive data; require redaction, encryption, TTL, tombstones, access control.
9. **Benchmark→production transfer:** retrieval benchmarks omit side effects/collaboration; coding benchmarks omit research; vendor demos are stack-specific.
10. **Vendor opacity:** hidden model/prompt/compaction changes make causal attribution difficult; retain external baselines and observable behavior logs.
11. **Complexity cost:** use progressive profiles—simple task→offload/minor GC; medium→checkpoint/profile; long→fold/reset/validator; high-risk→separation/provenance.
12. **Profile overfitting:** persistent learned profiles require cross-task replay and rollback; learned policy starts in shadow mode.

# 19. Historical implementation roadmap

- **Phase 0 — Telemetry:** normalize vendor context usage; record tokens/tools/phases; version model/CLI/prompt; detect large outputs.
- **Phase 1 — Canonical state:** Task Ledger, Progress Ledger, trajectory store, artifact/evidence store, completion capsule.
- **Phase 2 — Offloading/minor GC:** file/log offload, hash dedup, latest-per-suite, supersession graph, tool-span normalization.
- **Phase 3 — Context packing:** phase-aware retrieval, trust/temporal filters, attention-aware layout, constraint pinning, budget envelopes.
- **Phase 4 — Canonical profiles:** coding, review, research, incident, Overseer, small-model strict.
- **Phase 5 — Folding:** delegation capsules, child result contracts, subgoal and hierarchical folding.
- **Phase 6 — Integrity Gate:** schema validation, evidence resolution, recovery probes, independent semantic validation, reject/repair.
- **Phase 7 — Vendor adapters:** hooks/config/context editing and local OpenAI-compatible providers.
- **Phase 8 — Adaptive layer:** profile selection, on-the-fly overlay, Context Curator, shadow/A-B tests.
- **Phase 9 — Learned policies:** compressor distillation/RL/evolved guidelines through a governed promotion pipeline.

> This roadmap is historical research. A current tare.tools implementation plan must first reconcile these roles against the modern canonical bounded contexts and primitives rather than instantiate a parallel Context Control Plane by name.

# 20. Open research agenda

## 20.1 Agentic CompactionBench

A benchmark should preserve trajectory, tools, commits, subagents, repeated compactions, future-dependency labels, constraints, conflicting evidence, and resume tasks.

## 20.2 Transferable versus task-specific profiles

Measure transfer across languages/domains and when an adaptive overlay beats a well-designed canonical kernel.

## 20.3 Small curator versus executor model

Compare deterministic rules, small compressor, same model, and frontier validator for cost, fidelity, and self-justification bias.

## 20.4 Trained context policies

Test whether learned compaction/folding policies preserve governance, generalize across repositories, and remain stable after model upgrades.

## 20.5 Causal GC and static analysis

For coding, enrich dependency graphs with AST/call graph/test coverage/Git/workflow state rather than relying only on embeddings.

## 20.6 Standardized observability

Candidate events: `context_object_created`, `gc_committed`, `compaction_started`, `fold_completed`, `integrity_failed`, `session_rehydrated`, with OTel/W3C PROV projections.

## 20.7 Longitudinal evaluation

Evaluate weeks of backlog, not one task: memory contamination, profile drift, accumulated cost, artifact reuse, regressions, and decision reproducibility.

## 20.8 Harnesses for smaller models

Decompose the causal effects of guards, tool interface, skill budgets, context watchdog, compaction, and retry policy across open models.

## 20.9 Historical hypothesis matrix

| Hypothesis | Favorable evidence | Limitation | Historical status |
|---|---|---|---|
| Canonical state should live outside transcript | MemGPT, vendor long-running guidance, ledgers | infra/retrieval cost | Strong |
| Reset per task beats immortal conversation by default | long-running harness practice, artifacts | CWL suggests structured continuity can work | Strong default, not universal |
| GC should precede compaction | context editing, Deep Agents, Self-GC | limited cross-vendor ablation | Architecturally strong |
| Subgoal folding beats periodic summarization | HiAgent, Context-Folding, MAGE | depends on decomposition | Medium-high |
| Task profiles beat generic profile | operational logic, adaptive research | heterogeneous comparisons | Medium |
| On-the-fly overlays can help | SelfCompact, U-Fold | metacognition/self-evaluation risk | Promising; gated |
| Policies must be pinned | Governance Decay | preprint benchmark | Strong security principle |
| Small models need stricter scaffolds | little-coder, SWE-agent, Agentless | insufficient mechanism-level ablations | Medium-high |
| Thresholds should come from harness benchmarks | Lost in the Middle, RULER, NoLiMa | maintenance cost per snapshot | Strong |
| Child transcripts should not pollute parent | isolated subagents, folding | parent may need evidence retrieval | Strong with retrieval |

# 21. Conclusions

The literature and harness practice converge on a change of abstraction: **context should not be treated as a conversation that grows until emergency summarization is required. It should be treated as a governed set of objects with authority, dependencies, persistence, and lifecycle.**

For the Overseer, the historical default is a fresh physical session per meaningful backlog item, with compaction intra-task and state held by the harness. For subagents, preserve the active causal path, collect mechanical trace, fold completed subgoals, and return a typed capsule. For GC, age does not imply uselessness; folding precedes pruning; policy and open effects are pinned roots. For compaction profiles, the proposal favors `canonical kernel + task profile + adaptive overlay + validation` over either generic summarization or unrestricted self-management. For Lost in the Middle, retrieval, selection, and positional organization must be explicit. For vendors, native triggers and hooks are primitives, not the complete policy.

> **Final historical formulation:** the context window is a cognitive cache subject to physical limits, positional bias, interference, staleness, and semantic loss. A context-control mechanism should build, monitor, clean, fold, compact, validate, and replace that cache from external canonical state that is typed, recoverable, and auditable.

# 22. Bibliography

The bibliography below preserves the historical source’s evidence groups. Titles and publication metadata are retained; vendor documentation reflects the source’s 2026-07-26 view and should be revalidated before contemporary use.

## 22.1 Foundations, benchmarks, and peer-reviewed work

- Liu, N. F.; Lin, K.; Hewitt, J.; Paranjape, A.; Bevilacqua, M.; Petroni, F.; Liang, P. (2024). **Lost in the Middle: How Language Models Use Long Contexts.** *Transactions of the Association for Computational Linguistics*, 12, 157–173.
- Jiang, H. et al. (2024). **LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios via Prompt Compression.** ACL 2024.
- Pan, Z. et al. (2024). **LLMLingua-2: Data Distillation for Efficient and Faithful Task-Agnostic Prompt Compression.** Findings of ACL 2024.
- Zhang, X. et al. (2024). **∞Bench: Extending Long Context Evaluation Beyond 100K Tokens.** ACL 2024.
- Bai, Y. et al. (2025). **LongBench v2: Towards Deeper Understanding and Reasoning on Realistic Long-Context Multitasks.** ACL 2025.
- Hu, M. et al. (2025). **HiAgent: Hierarchical Working Memory Management for Solving Long-Horizon Agent Tasks with Large Language Model.** ACL 2025.
- Hong, S. et al. (2024). **MetaGPT: Meta Programming for Multi-Agent Collaborative Framework.** ICLR 2024.
- Yang, J. et al. (2024). **SWE-agent: Agent–Computer Interfaces Enable Automated Software Engineering.** NeurIPS 2024.
- Xu, W. et al. (2025). **A-MEM: Agentic Memory for LLM Agents.** NeurIPS 2025.
- Qian, C. et al. (2023). **ChatDev: Communicative Agents for Software Development.** arXiv:2307.07924.
- Xia, C. S. et al. (2024). **Agentless: Demystifying LLM-Based Software Engineering Agents.** arXiv:2407.01489.
- Zhang, Y. et al. (2024). **AutoCodeRover: Autonomous Program Improvement.** ISSTA 2024.

## 22.2 Benchmarks and foundational preprints

- Hsieh, C.-P. et al. (2024). **RULER: What’s the Real Context Size of Your Long-Context Language Models?** arXiv:2404.06654.
- Modarressi, A. et al. (2025). **NoLiMa: Long-Context Evaluation Beyond Literal Matching.** arXiv:2502.05167.
- Packer, C. et al. (2023). **MemGPT: Towards LLMs as Operating Systems.** arXiv:2310.08560.
- Li, Z. et al. (2025). **MemOS: An Operating System for Memory-Augmented Generation in Large Language Models.** arXiv:2507.03724.
- Fourney, A. et al. (2024). **Magentic-One: A Generalist Multi-Agent System for Solving Complex Tasks.** arXiv:2411.04468.
- Cheng, Y. et al. (2026). **Contextual Drag: How Errors in the Context Affect LLM Reasoning.** arXiv:2602.04288.

## 22.3 Bleeding edge: compaction, folding, execution state, and GC

- Chen, S. (2026). **Governance Decay: How Context Compaction Silently Erases Safety Constraints in Long-Horizon LLM Agents.** arXiv:2606.22528.
- Sun, W. et al. (2025). **Scaling Long-Horizon LLM Agent via Context-Folding.** arXiv:2510.11967.
- Shao, J. et al. (2025). **FoldAct: Efficient and Stable Context Folding for Long-Horizon Agents.** arXiv:2512.22733.
- Su, J. et al. (2026). **U-Fold: Dynamic Intent-Aware Context Folding for User-Centric Agents.** arXiv:2601.18285.
- Chen, Y. et al. (2026). **Beyond Semantic Organization: Memory as Execution State Management for Long-Horizon Agents.** arXiv:2606.06090.
- Hao, X. et al. (2026). **Self-GC: Self-Governing Context for Long-Horizon LLM Agents.** arXiv:2607.00692.
- Semenov, A.; Dorofeev, S. (2026). **Beyond Compaction: Structured Context Eviction for Long-Horizon Agents.** arXiv:2606.11213.
- Kang, M. et al. (2025). **ACON: Optimizing Context Compression for Long-Horizon LLM Agents.** arXiv:2510.00615.
- Li, T. et al. (2026). **Self-Compacting Language Model Agents.** arXiv:2606.23525.
- Li, M. et al. (2026). **CompactionRL: Jointly Learning Task Execution and Context Compaction for Long-Horizon Agents.** arXiv:2607.05378.
- Wu, Y. et al. (2026). **ContextBudget: Budget-Aware Context Management for Long-Horizon Search Agents.** arXiv:2604.01664.
- Li, M. et al. (2026). **Neural Garbage Collection: Learning to Forget while Learning to Reason.** arXiv:2604.18002.
- Liu, S. et al. (2025). **Context Management for Long-Horizon SWE-Agents.** arXiv:2512.22087.
- Xu et al. (2026). **MemGym: Benchmarking Memory Systems for Agentic Tasks.** arXiv:2605.20833.
- Luo, J. et al. (2026). **A Survey on the Evolution of LLM Agent Memory.** Findings of ACL 2026.

## 22.4 Official documentation and engineering sources in the historical corpus

- OpenAI (2026a). **Codex Hooks.**
- OpenAI (2026b). **Codex Configuration Reference.**
- OpenAI (2026c). **Codex Subagents.**
- OpenAI (2026d). **Building Reliable Agents: Memory and Compaction.**
- OpenAI (2025). **Using PLANS.md for Multi-Hour Problem Solving / Long-Horizon Tasks.**
- Anthropic (2026a). **Claude Code Hooks Reference.**
- Anthropic (2026b). **Context Editing.**
- Anthropic (2026c). **Subagents in Claude Code and Agent SDK.**
- Anthropic (2026d). **Effective Harnesses for Long-Running Agents.**
- Anthropic (2026e). **Effective Context Engineering for AI Agents.**
- Moonshot AI (2026a). **Kimi Code CLI — Configuration Files.**
- Moonshot AI (2026b). **Kimi Code CLI — Hooks (Beta).**
- Google (2026a). **Gemini CLI Configuration.**
- Google (2026b). **Agent Development Kit — Context Compaction.**
- LangChain (2026a). **Context Engineering.**
- LangChain (2026b). **Context Engineering in Deep Agents.**
- LangChain (2026c). **Deep Agents from Scratch.**
- Microsoft Research (2026). **LLMLingua Series.**

## 22.5 Repositories, releases, issues, and field evidence

The historical source additionally catalogs little-coder repository/whitepaper/changelog/releases; Codex and Claude Code issues/discussions around hooks, compaction, reinjection, checkpoints, and memory; AutoGen/Magentic-One discussions; ChatDev/MetaGPT/Agentless/AutoCodeRover repositories; Deep Agents; Pydantic AI Harness; UniHarness; and living discovery lists. These entries are explicitly classified as **field evidence**, not controlled benchmark results.

## 22.6 Internal project source

- **Multi Agent Harness (2026).** Formal research program and internal architecture/research artifacts used as project context for this historical edition.

# Appendix A — Glossary

- **Active context:** observation currently exposed to the model.
- **Canonical state:** external typed state that remains authoritative across model sessions.
- **Context object:** typed unit with ownership, lifecycle, dependencies, persistence, semantics, and GC metadata.
- **Folding:** close a causal/subtask unit and replace active trajectory with a referenced condensed result.
- **Compaction:** lossy rewriting of history into a smaller representation.
- **GC:** lifecycle-driven removal of unnecessary objects from active view.
- **Rehydration:** reconstruct a new active context from canonical state/checkpoint.
- **Negative memory:** typed record of a rejected hypothesis/failure and its evidence.
- **Pinned constraint:** high-authority content excluded from lossy compaction.

# Appendix B — Research pointer tree

```text
long context limits
 ├── retrieval / utilization / interference
 ├── object-oriented context GC
 ├── folding and branch management
 ├── canonical state + materialized views
 ├── integrity after compaction
 ├── model-specific context profiles
 ├── vendor adapter qualification
 └── learned policies under deterministic gates
```

# Appendix C — Editorial status

This English edition preserves the historical research framing. Terms such as **Context Control Plane**, `Task Ledger`, `Progress Ledger`, or `Context Curator` should be reconciled against the current tare.tools canonical equivalents before any implementation. The modern North Star may compose these responsibilities across Project, Workflow, Memory/Context, Runtime, Capability/Effects, Evidence, Assurance, and Governance rather than ratifying the historical component boundaries verbatim.

---

**Translation note:** machine-translated/editorially normalized derivative; not human-reviewed; no scientific refresh; no change of architectural authority.
