---
translation_of: docs/research/guia-playbooks-engineering-2026-07-29.html
source_snapshot: 2026-08-05-private-github-snapshot
source_language: pt-BR
language: en
translation_status: MACHINE_TRANSLATED_UNREVIEWED
authority_status: DERIVED_NON_AUTHORITATIVE
editorial_migration: true
scientific_refresh: false
historical_reference_date: 2026-07-29
---

# Playbook Engineering for Multi-Agent Harnesses

**Multi Agent Harness — Playbook Engineering Guide**  
**Reference date:** July 29, 2026  
**Target project:** Multi Agent Harness  
**Format:** Practical guide + reference architecture  
**Evidence base:** 63 academic, official, and engineering sources

> **Historical editorial English edition.** This document translates and reformats the 2026-07-29 project artifact. It does not silently refresh vendor facts, research claims, or architectural authority. Any later reconciliation with the tare.tools Agent OS North Star must be performed separately.

## Central conclusion

Playbooks should continue to exist as human-versioned sources—Markdown, YAML, schemas, policies, scripts, and references—but the agent should consume a **compiled effective playbook** for the current task. For subagents, the runtime should derive an even smaller capsule, the **Spawn Envelope**, and page only the active procedure frame.

## 1. How to use this document

This guide turns research on roles, SOPs, skills, prompt programming, context engineering, and runtime enforcement into an implementable proposal for the harness. It assumes the project architecture defined at the time: an intermediate layer between models, agents, tools, repositories, and users, with a probabilistic intelligence plane constrained by a deterministic control plane. [1]

**For architecture:** read Sections 3–7: metamodel, compiler, IR, lockfile, and runtime pager.  
**For prompts and cost:** read Sections 8–11: spawn, budgets, caching, pruning, and compression.  
**For implementation:** read Sections 12–17 and the appendices: schemas, code, evals, and roadmap.

**Freshness warning.** Vendor documentation and 2026 preprints may change quickly. The historical source distinguishes living documentation, recent preprints, and established references and proposes revalidation rather than assuming permanence.

## 2. Definitions and mental model

### 2.1 A playbook is not the same thing as a prompt

In contemporary practice, *playbook* is an umbrella term. The literature uses SOP, role profile, agent skill, instruction set, workflow, scaffold, policy, prompt program, and orchestration prompt. MetaGPT consolidated the idea of encoding SOPs as prompt sequences; MASAI and AgentCoder showed that useful roles differ in strategies, tools, and feedback; SWE-agent showed that the interface presented to an agent can shape behavior as much as textual instructions. [2][3][4][5]

> **Playbook Source ≠ Final Prompt ≠ Workflow ≠ Policy ≠ Execution State**

### 2.2 Five different artifacts

| Artifact | Function | Mutability | Consumer |
|---|---|---|---|
| **Playbook Source** | Human source: role, procedure, domain, references | Versioned | Compiler and maintainers |
| **Playbook Package** | Normalized, validated source with dependencies and compatibility | Immutable per version | Registry |
| **Effective Playbook** | Composition for task, project, path, risk, model, and vendor | Per execution | Runtime |
| **Spawn Envelope** | Minimum perspective given to a subagent at birth | Per delegation | Subagent |
| **Execution Frame** | Current step, tools, and expected output | Per transition | Model in the current call |

### 2.3 The operational equation

```text
EffectivePlaybook =
    GlobalConstitution
  + OrganizationRules
  + RoleCharter
  + TaskProcedure
  + DomainSkills
  + ProjectProfile
  + PathScopedRules
  + RiskPolicy
  + CapabilityBinding
  + ModelAdapter
  + OutputContract
  + EvaluationProfile
```

The Agent Skills pattern materializes part of this composition through progressive disclosure: metadata is discovered first, the main body is loaded when activated, and resources are read on demand. The specification cited by the historical document recommends a focused main body of roughly fewer than 5,000 tokens. [15][16]

## 3. Evolution of the pattern: from persona to operational program

### 2023 — SOPs and roles

MetaGPT and AgentCoder encode human processes and separate implementation, test design, and execution. The durable contribution is responsibility separation and executable feedback—not theatrical job titles. [2][3]

### 2024 — Strategies and interfaces

MASAI uses subagents with different objectives and strategies; SWE-agent demonstrates that commands, editing operations, and observations form an Agent-Computer Interface that materially conditions performance. [4][5]

### 2025 — Structured SOPs, policy, and context engineering

SOP-Agent represents procedures as pseudocode/graphs; AgentSpec turns restrictions into executable rules; vendors increasingly emphasize progressive disclosure, minimal context, and deterministic workflows where possible. [41][43][27][28]

### 2026 — Compilation, benchmarks, and economics

Compile, Then Page and SkillSmith study compilation of SOPs/skills; AOrchestra models a created agent as a composition of Instruction, Context, Tools, and Model; SkillsBench, SWE-Skills-Bench, and SkillReducer measure utility and cost. [42][44][47][48][49][50]

> **Distilled pattern:** useful specialization changes the operational contract—inputs, tools, strategy, authority, artifacts, verification, and stopping conditions—not merely the text “you are a specialist.”

## 4. Source model: what should remain fixed

The compiler does not eliminate documents. It lets every source have its own responsibility and lifecycle.

| Source | Content | Example | Change frequency |
|---|---|---|---|
| Constitution | Invariants, separation of authority, global principles | `constitution/global.yaml` | Low |
| Role charter | Mission, ownership, non-ownership, escalation | `roles/implementer.yaml` | Low/medium |
| Task procedure | Sequence, branches, gates, retry, completion | `procedures/bugfix.yaml` | Medium |
| Domain skill | Procedural knowledge and references | `skills/react-accessibility/` | Medium/high |
| Project profile | Commands, architecture, conventions, environments | `projects/checkout.yaml` | High |
| Path rule | Local rules and risks for a code surface | `paths/payment.yaml` | High |
| Policy | Executable allow/deny/approval/budget | `policies/tools.rego` | Medium |
| Contract | Input, output, evidence, and handoff schema | `contracts/result.v2.json` | Medium |
| Eval suite | Tasks, fixtures, graders, thresholds, regressions | `evals/frontend/` | Continuous |

Codex, Copilot, and Claude already load instructions by scope and layer; GitHub supports path-specific rules, while Codex recommends short, practical AGENTS.md files at different levels of the tree. [17][34][25]

## 5. Playbook Compiler architecture

### 5.1 Compiler, linker, and renderer

The proposed component combines three traditional responsibilities:

- **Compiler:** parses, normalizes, types, validates, and converts sources into an IR.
- **Linker:** resolves versions, dependencies, precedence, imports, and capabilities.
- **Renderer:** produces vendor-specific prompts, schemas, tool bindings, and payloads.

GitHub Agentic Workflows is cited as a clear industrial example of separating human source from executable artifact: Markdown is compiled into `.lock.yml` after parsing, validation, job construction, dependency resolution, and hardening. [13][14] Compile, Then Page and SkillSmith show the same research direction: compile procedures or skills before execution instead of reinjecting raw documents on every turn. [42][47]

### 5.2 Recommended pipeline

```text
Parse
  → Normalize
  → Resolve
  → Type check
  → Policy check
  → Lowering
  → Lock
```

- **Parse:** Markdown frontmatter, YAML, JSON Schema, and policy modules.
- **Normalize:** convert synonyms, defaults, and versions into a canonical AST.
- **Resolve:** select role, procedure, skills, project, and affected paths.
- **Type check:** verify handoffs, state schemas, tool arguments, and outputs.
- **Policy check:** apply deny-overrides, approvals, and budgets before the model.
- **Lowering:** generate workflow graph, prompt plan, capabilities, and adapters.
- **Lock:** produce a manifest containing hashes, provenance, and effective configuration.

### 5.3 Intermediate representation

```yaml
EffectivePlaybookIR:
  identity:
  authority:
  activation:
  taskContract:
  contextPlan:
  procedures:
  decisionGraph:
  workflowGraph:
  capabilities:
  toolBindings:
  policies:
  validators:
  outputContracts:
  budgets:
  modelBinding:
  provenance:
```

PDL, LMQL, and DSPy illustrate complementary styles: PDL keeps declarative structure and prompts visible; LMQL compiles constraints/control into restricted generation; DSPy describes contracts and optimizes instructions/demonstrations against metrics. [7][8][9][10][11][12] None replaces the harness compiler, but each can inform or back parts of the IR.

### 5.4 Mandatory diagnostics

Compilation should fail diagnostically for at least:

- two exclusive owners for the same artifact;
- a cycle without an exit condition;
- a missing or incompatible tool;
- violation of an explicit deny policy;
- incompatible output schema;
- expired or version-mismatched skill;
- reviewer with inappropriate write authority;
- prompt exceeding adapter limits;
- ambiguous path rule;
- missing mandatory gate.

## 6. Effective Playbook Lockfile

The lockfile is the immutable record of everything actually applied. It supports replay, audit, version comparison, cache keys, and behavior explanation.

```yaml
apiVersion: harness.ai/v1
kind: EffectivePlaybook
metadata:
  taskId: TASK-142
  compilerVersion: 0.4.0
  sourceHash: sha256:8de...
  generatedAt: 2026-07-29T22:03:00-03:00
binding:
  role: implementer@2.1.0
  procedure: bugfix@1.4.0
  domains: [frontend@3.2.0]
  project: checkout-web@17
  pathRules: [payment@4]
  modelProfile: coding-high-reasoning
effectiveTools:
  allow: [repository.read, repository.search, repository.edit, test.run]
  deny: [network.external, production.deploy, secrets.read]
verification:
  required: [typecheck, component-tests, browser-e2e, independent-review]
provenance:
  - roles/implementer.yaml@2.1.0
  - procedures/bugfix.yaml@1.4.0
  - skills/react-state-debugging@2.0.1
  - projects/checkout-web.yaml@17
  - paths/payment.yaml@4
```

The `.md → .lock.yml` pattern in GitHub Agentic Workflows demonstrates the practical value of retaining both source and compiled artifact under version control. [13][14]

## 7. Compiling the initial prompt: Spawn Envelope

### 7.1 Why not copy the parent context

AOrchestra explicitly compares subagents with no context, full context, and curated context; its abstraction creates each executor as an Instruction/Context/Tools/Model tuple. PerspectiveGap shows that deciding which information belongs to which role is a separate and difficult capability. AgentSpawn studies selective memory transfer during spawning. [44][45][46]

**Anti-pattern:**

```text
spawn_prompt = parent_transcript + all_tools + full_playbook
```

This duplicates cost, propagates noise, expands prompt-injection surface, and blurs ownership.

### 7.2 Recommended structure

```text
SpawnEnvelope =
    RoleKernel
  + DelegationCapsule
  + RelevantBindingState
  + CapabilityIndex
  + CurrentExecutionFrame
  + ReturnContract
```

| Block | Should contain | Should not contain |
|---|---|---|
| Role Kernel | Mission, ownership, authority, boundaries | Biography and encyclopedic best practices |
| Delegation Capsule | Local objective, criteria, non-goals, dependencies | Entire overseer conversation |
| Binding State | Confirmed facts, binding decisions, active risks | Refuted hypotheses and raw logs |
| Capability Index | Loaded, discoverable, and forbidden tools | Entire schema catalog |
| Current Frame | Current step, immediate instruction, expected output | Detailed full future workflow |
| Return Contract | Schema, evidence, stop, escalation | Unstructured narrative report |

### 7.3 Example

```yaml
apiVersion: harness.ai/v1
kind: SpawnEnvelope
metadata:
  taskId: TASK-142
  agentId: frontend-implementer-07
  parentAgentId: overseer-01
  estimatedTokens: 1840
role:
  mission: Implement the delegated frontend fix.
  owns: [patch, related-tests, evidence]
  doesNotOwn: [final-approval, requirements, deploy]
task:
  objective: Fix button duplication after retry.
  acceptanceCriteria:
    - only one payment can be submitted
    - retry does not duplicate the button
    - keyboard navigation remains functional
activeState:
  knownFacts:
    - the issue requires failure followed by retry
    - PaymentForm controls pending
  bindingDecisions:
    - use the existing design system
    - do not introduce global state
contextReferences:
  - uri: repo://src/frontend/payment/PaymentButton.tsx
  - uri: artifact://TASK-142/reproduction.md
capabilities:
  loaded: [repository.read, repository.search, test.run]
  discoverable: [repository.edit, browser.inspect, accessibility.scan]
  denied: [production.deploy, network.external, secrets.read]
activeFrame:
  step: inspect
  instructions:
    - locate owners of pending, retry, and submission
    - do not edit during this step
returnContract:
  finalSchema: implementation-result/v2
  escalateWhen: [backend-change-needed, protected-path, policy-conflict]
```

### 7.4 Cache-aware and attention-aware layout

- **Static/cacheable prefix:** role, authority, policies, common tools.
- **Dynamic body:** task, facts, artifacts, references.
- **Terminal frame:** current step, output, stop, escalation.

OpenAI and Anthropic documentation cited by the source emphasize identical prefixes for cache hits: static content first, variable content later. Cached tokens still occupy the context window, so caching reduces prefill latency/cost but does not replace selection or pruning. [24][31][32]

## 8. Vendor limits and injection budget

The document distinguishes four constraints: model context window, platform limit, instruction/file limit, and a healthy attention budget. The compiler should record all four per adapter.

| Surface | Historical limit observed on 2026-07-29 | Implication |
|---|---|---|
| GitHub Copilot custom agent | Markdown prompt up to 30,000 characters | Compile and diagnose overflow; never silently truncate. [33] |
| Codex AGENTS.md | `project_doc_max_bytes` default 32,768 bytes | Local guidance should be short and hierarchical. [18] |
| Agent Skills | Small metadata; SKILL.md recommended around <5k tokens / 500 lines | Load references/scripts on demand. [15][16] |
| Claude Code skills after compaction | Up to 5,000 tokens reattached per skill and 25,000 aggregate budget | Put essential content early; old skills can be dropped. [26] |

### 8.1 Initial budgets for evaluation

These are engineering heuristics from the historical guide, not universal scientific limits.

| Role | Suggested initial spawn | Strategy |
|---|---:|---|
| Router / gatekeeper | 400–1,200 tokens | Typed output, few tools, abstention |
| Read-only explorer | 700–1,800 | Discovery objective + evidence contract |
| Reviewer | 800–2,000 | Diff, requirements, local rules, rubric |
| Implementer | 1,500–4,000 | Minimum procedure + references on demand |
| Overseer | 2,000–6,000 | Compact global state, budgets, dependencies |

```text
B_spawn = min(vendor_limit, role_limit, task_budget)
          - tool_schema_tokens
          - output_schema_tokens
          - safety_margin
```

Even with long context windows, information position and density matter. Lost in the Middle reported degradation when relevant evidence is buried in the middle of context. [6]

## 9. Token-reduction strategy

### 9.1 Recommended order

1. **Deduplicate:** remove repeated rules, backstory, and equivalent examples.
2. **Compose selectively:** load only applicable role, procedure, domain, and path material.
3. **Reference:** replace long documents with retrievable URIs.
4. **Discover tools on demand:** expose a small index; load schemas when needed.
5. **Filter observations:** summarize logs/lists/results deterministically.
6. **Materialize state:** keep decisions and artifacts outside the transcript.
7. **Remove expired trajectory:** discard redundant or superseded outputs.
8. **Task-aware pruning:** preserve syntax, IDs, and required relationships.
9. **Semantic compression:** last resort for prose and narrative documentation.

### 9.2 What recent evidence reported

| Work | Technique | Reported result | Caution |
|---|---|---|---|
| AgentDiet [52] | Removes useless, redundant, expired trajectory | 39.9–59.7% fewer input tokens in reported experiments | Limited model/agent/benchmark scope |
| SWE-Pruner [53] | Task-guided line pruning | 23–54% reduction in reported agentic tasks | Must preserve code structure |
| SWE-Pruner Pro [54] | Head over coder-model internal representations | Up to 39% prompt/completion savings | Requires open models/internal access |
| LLMLingua / LongLLMLingua [55][56] | Coarse-to-fine, query-aware compression | High compression in non-agentic tasks | Do not blindly compress policies/code/schemas/tool grammar |
| AGORA [58] | Observation-action retention | Shows generic token compressors can destroy operational structure | Preserve IDs/brackets/tools/arguments |
| SkillReducer [50] | Structural skill compression | Significant body reductions in SkillsBench | Validate by task/model |
| Cost-aware skill rewriting [51] | Retains API/workflow/rule anchors | Shorter can increase downstream cost | Optimize total cost, not initial length |

### 9.3 Content protected from compression

**Preserve literally:** policies/prohibitions, acceptance criteria, tool names/arguments, schemas/types, IDs/paths/commands, state transitions, relevant diffs/patches.

**May be condensed:** narrative documentation, old exploration already materialized elsewhere, logs after error extraction, duplicate explanations, history of refuted hypotheses, long results with a saved artifact.

AgentFold and budget-aware context approaches treat context as a workspace that must be continuously restructured rather than as an append-only log. [57][59][60]

## 10. Tools, schemas, and observations: the hidden token sink

In real agents, tool definitions and raw results may cost more context than instructions. The recommendation is to keep a small set of common tools loaded and allow discovery of the rest.

### 10.1 Tool discovery

```yaml
capabilities:
  loaded:
    - repository.read
    - repository.search
    - test.run
  discoverable:
    - browser.inspect
    - accessibility.scan
    - git.history
  denied:
    - production.deploy
    - secrets.read
```

The Anthropic engineering example cited by the historical source reported a specific workflow in which navigating MCP servers and loading only required definitions reduced 150,000 tokens to 2,000. The guide explicitly treats this as an illustrative case, not a universal expectation. [30]

### 10.2 Deterministic filtering

```python
raw = tool.get_test_log()
result = {
    "exit_code": raw.exit_code,
    "failed_tests": extract_failed_tests(raw.stdout),
    "error_signatures": classify_errors(raw.stderr),
    "artifact_uri": save_full_log(raw),
}
return result
```

The model receives an actionable summary plus a reference to the complete log, reducing tokens without destroying auditability.

### 10.3 A tool is a contract, not documentation

Interfaces should use non-overlapping names, typed arguments, declared side effects, actionable errors, and dense outputs. SWE-agent reinforces that the ACI must be designed for agent capabilities, while Google ADK supports callbacks before/after model and tool calls for observation or blocking. [5][35][37]

## 11. Role-specific playbooks

### 11.1 Overseer

```yaml
mission:
  owns: [global-outcome, decomposition, delegation, integration, closure]
procedure:
  - understand-objective
  - classify-complexity-and-risk
  - construct-work-graph
  - delegate-with-boundaries
  - monitor-evidence
  - replan-when-needed
  - integrate
  - request-independent-validation
invariants:
  - do-not-spawn-unbounded-workers
  - do-not-accept-assertion-as-evidence
  - do-not-approve-own-governance-change
```

Anthropic’s reported multi-agent research experience suggests that delegation should specify objective, expected format, sources/tools, boundaries, and effort; vague delegation causes duplication and gaps. [29]

### 11.2 Router / gatekeeper

```yaml
mission:
  objective: Select an eligible route or abstain.
  doesNotOwn: [task-execution, implementation, policy-modification]
tools:
  allow: [capability-registry.read, project-profile.read, routing-history.read]
  deny: [repository.edit, shell.run, agent.create-unregistered]
output:
  schema: routing-decision/v2
control:
  abstainBelowConfidence: 0.70
  requireReasonCodes: true
```

The router should have a small prompt, limited memory, structured output, and the ability to abstain. PerspectiveGap motivates evaluating both omission and leakage of information belonging to other roles. [45]

### 11.3 Implementer

```yaml
mission:
  owns: [patch, related-tests, evidence]
  doesNotOwn: [final-approval, requirements, deploy]
procedure:
  - inspect-existing-patterns
  - map-criteria-to-changes-and-tests
  - implement-minimal-coherent-change
  - verify
  - handoff
```

MASAI supports specialization of strategies by subproblem, while AgentCoder demonstrates value in separating test design/execution from programming. [3][4]

### 11.4 Reviewer

```yaml
mission:
  owns: [independent-findings]
  doesNotOwn: [silent-patch-rewrite]
tools:
  defaultMode: read-only
procedure:
  - reconstruct-intended-behavior
  - inspect-diff-and-impact-surface
  - attempt-to-refute-correctness
  - verify-tests-cover-risk
  - classify-findings-by-severity
```

The reviewer should receive requirements, diff, evidence, and local rules, but not an implementer’s private chain of thought.

## 12. Domain packs for coding agents

### 12.1 Composition, not an explosion of agent types

```text
Frontend Implementer =
  role/implementer
  + procedure/feature
  + domain/frontend
  + framework/react-19
  + skill/accessibility
  + project/checkout-web
  + path/payment
  + risk/high
```

Focused skills can be more useful than universal documentation. SkillsBench reported substantial average gains but also large variance and negative cases; SWE-Skills-Bench found smaller gains in software engineering and regressions caused by version/context incompatibility. [48][49]

### 12.2 Frontend pack

```yaml
frontend:
  architecture:
    - preserve-component-boundaries
    - prefer-existing-primitives
    - avoid-duplicated-state
  designSystem:
    - inspect-existing-tokens-and-components
    - justify-new-primitives
  accessibility:
    - semantic-html-first
    - keyboard-navigation
    - visible-focus
    - accessible-names
  states: [loading, empty, error, success]
  conditionalVerification:
    layoutChanged: [visual-regression]
    interactionChanged: [browser-e2e, keyboard-check]
    semanticChanged: [accessibility-scan]
```

### 12.3 Backend pack

```yaml
backend:
  apiContracts:
    - preserve-backward-compatibility
    - validate-error-semantics
  persistence:
    - inspect-transaction-boundaries
    - migration-order-and-rollback
    - avoid-unbounded-queries
  concurrency:
    - idempotency
    - retries
    - locking
    - duplicate-delivery
  observability:
    - structured-logs
    - metrics
    - traces
```

### 12.4 Compatibility manifest

```yaml
compatibility:
  frameworks:
    react: ">=18 <20"
  testedWith:
    - react: 19.1
      harness: 0.9.0
      models: [gpt-codex-current, claude-code-current]
  revalidateOn:
    - framework-major-change
    - model-snapshot-change
    - tool-schema-change
```

Compatibility needs to be executable. The historical source highlights SWE-Skills-Bench results where skills reduced performance when they conflicted with project versions/context. [49]

## 13. Workflow compiler and runtime pager

The playbook compiler emits two connected artifacts: an effective manifest and an executable workflow. Google ADK offers deterministic sequence/loop/parallel workflow agents; LangGraph recommends keeping raw state and formatting prompts on demand, with checkpointers for persistence and replay. [36][39][40]

```yaml
workflow:
  nodes:
    - route
    - explore
    - reproduce
    - implement
    - verify
    - review
  edges:
    - route -> explore
    - explore -> reproduce
    - reproduce -> implement
    - implement -> verify
    - verify.pass -> review
    - verify.fail -> implement
  termination:
    maxRepairLoops: 2
  gates:
    - before: protected-write
      require: approval
```

### 13.1 Paging the active frame

Compile, Then Page recommends compiling first and enabling paging only after evaluating whether a model can follow state discipline; some guidance modes harmed weaker models in the reported study. [42]

The guide therefore proposes three per-model modes:

- `full-program`
- `active-frame + program-index`
- `active-frame-only`

Select by eval rather than architectural preference.

## 14. Security and governance

### 14.1 Prompt text is not enforcement

Natural-language instructions guide behavior; policies, callbacks, sandboxes, and tool gates constrain actions. AgentSpec proposes rules with trigger/predicate/enforcement; VIGIL extends the idea to temporal policies and value flows over agent-tool events. Google ADK recommends callbacks/plugins for pre-validation of tool calls. [41][61][37]

```yaml
policy:
  id: protect-production
  trigger:
    tool: deploy
  predicate:
    environment: production
  enforce:
    requireApproval: release-manager
```

### 14.2 Trust boundaries

The historical proposal distinguishes, among others:

- untrusted repository documents;
- signed/versioned playbooks;
- quarantined third-party skills;
- tools with declared side effects;
- policy engines independent of the model;
- reviewers without promotion power;
- proposal agent ≠ approval authority;
- lockfiles with provenance.

### 14.3 Precedence rules

1. **Explicit deny** overrides allow and natural-language instructions.
2. **Higher authority** overrides local rules in security conflicts.
3. **More specific rules** override only within the space allowed by higher rules.
4. **Obligation** creates a gate, not just a textual reminder.
5. **Unresolvable conflict** fails compilation.

## 15. Evals: prove that the playbook helps

OpenAI guidance cited by the document recommends converting traces and feedback into evals before changing the harness; Google ADK separates trajectory/tool-use evaluation from final-result evaluation. SkillsBench uses containerized tasks, deterministic verifiers, and with/without-skill comparison. [22][23][48][63]

### 15.1 Experimental unit

```text
EvalCase =
  Task
  + RepositorySnapshot
  + EffectivePlaybookVersion
  + ModelSnapshot
  + ToolsetVersion
  + Budget
  + TrialSeed
  + Verifier
```

### 15.2 Baselines

| Variant | Purpose |
|---|---|
| No playbook | Measure base model/harness capability |
| Simple persona | Isolate role-labeling effect |
| Raw playbook | Compare full document with compilation |
| Compiled playbook | Measure selective composition and policies |
| Full-context spawn | Baseline for copied context |
| Curated spawn | Measure context slicing |
| Oracle capsule | Upper bound with ideal minimal context |

### 15.3 Metrics

- **Outcome:** success, acceptance coverage, regressions, human rework.
- **Trajectory:** first-action correctness, tool selection, retries, route churn.
- **Context:** injected tokens, critical-fact recall, leakage, compression ratio.
- **Economics:** cost-to-success, TTFT, total latency, cache-hit rate.
- **Governance:** policy violations, denied calls, approval frequency, trace completeness.
- **Maintenance:** regression rate, compatibility failures, rollback rate.

### 15.4 Promotion gates

```yaml
promotion:
  require:
    passRateDelta: ">= 0"
    criticalPolicyRecall: "= 1.0"
    noHighSeverityRegression: true
    costToSuccessDelta: "<= +5%"
    minimumTrialsPerClass: 10
  rollout:
    - shadow
    - canary: 10%
    - staged: 50%
    - full
```

The historical guide cites OpenAI guidance to pin model snapshots and keep eval suites while changing prompts/models because small model changes can alter instruction following. [62]

## 16. Proposed implementation architecture

```text
Source Registry
roles • procedures • skills • policies • schemas • projects • path rules
        ↓
Static Compiler
parse • validate • type • package
        ↕
Compatibility Index
versions • vendors • tools • models
        ↓
Effective Playbook Compiler
resolve • policy • capabilities • context plan • provenance
      ↙                           ↘
Workflow Compiler              Spawn Compiler
graph • gates • retry          perspective • budget
• checkpoints                  • cache • rendering
      ↘                           ↙
Runtime Pager + Policy Interceptor
active frame • tool gates • observation filter • state
        ↓
Vendor Adapters
OpenAI • Claude • Gemini/ADK • Copilot • Kimi • GLM • OpenAI-compatible local
```

### 16.1 Proposed directory structure

```text
agent-system/
├── constitution/
├── roles/
│   ├── overseer/
│   ├── router/
│   ├── implementer/
│   └── reviewer/
├── procedures/
│   ├── feature/
│   ├── bugfix/
│   ├── migration/
│   └── review/
├── skills/
│   ├── frontend/
│   ├── backend/
│   ├── database/
│   └── security/
├── contracts/
├── policies/
├── projects/
├── paths/
├── adapters/
├── compiler/
│   ├── parser/
│   ├── resolver/
│   ├── ir/
│   ├── lowering/
│   └── diagnostics/
└── evals/
```

### 16.2 Main interfaces

- `PlaybookSourceRepository`
- `PlaybookPackageRegistry`
- `CompatibilityResolver`
- `EffectivePlaybookCompiler`
- `WorkflowCompiler`
- `SpawnEnvelopeCompiler`
- `TokenBudgetAllocator`
- `ContextSelector`
- `PolicyEngine`
- `VendorRenderer`
- `RuntimePager`
- `PlaybookTraceRecorder`
- `EvaluationRunner`

> These names are historical design roles from the 2026-07-29 artifact. They are not automatically canonical tare.tools primitives.

## 17. Incremental roadmap

| Phase | Deliverables | Exit criterion |
|---|---|---|
| 0 — Baseline | Inventory current prompts, token telemetry, traces | Costs and failures observable |
| 1 — Metamodel | Schemas for role, procedure, skill, policy, handoff | Static validation and fixtures |
| 2 — Compiler v0 | Deterministic composition + lockfile | Identical replay by hash |
| 3 — Spawn v0 | Role kernel + task capsule + return contract | Fewer tokens without success drop |
| 4 — Progressive disclosure | Reference index, tool discovery, artifact URIs | Reduced schemas/initial context |
| 5 — Runtime pager | Frames, state machine, checkpoints | Long tasks without invariant loss |
| 6 — Context GC | Expiration, observation filtering, folding | Reduced cost-to-success |
| 7 — Optimization | DSPy/GEPA or offline optimizer | Promotion only through evals |
| 8 — Multi-vendor | Renderers and budget profiles by model | Measured behavioral parity |

**Do not start with self-evolution.** First build provenance, lockfiles, evals, rollback, policy enforcement, and observability. Only later should agents be allowed to *propose* playbook changes.

## 18. Anti-patterns

- **God prompt:** one universal Markdown containing every practice, tool, and exception.
- **Theatrical persona:** long biography with no operational-contract change.
- **Blind concatenation:** `global + role + skill + repo` without IR, precedence, or deduplication.
- **Full-context spawn:** copy all overseer memory into every worker.
- **Full tool catalog:** load hundreds of schemas on every turn.
- **Silent truncation:** cut the end when a vendor limit is reached.
- **Grammar compression:** remove tokens from paths, IDs, code, schemas, or tool calls.
- **Textual policy:** say “do not” while the dangerous tool remains available.
- **Skill without compatibility:** framework practices without versions/revalidation.
- **Self-edit after one failure:** mutate a playbook without eval, comparison, and canary.

## 19. Healthy implementation checklist

- [ ] Every role has explicit ownership and `does-not-own` boundaries.
- [ ] Skills are modular and loaded on demand.
- [ ] Compiler has a typed IR.
- [ ] Conflicts and overflows fail with diagnostics.
- [ ] Lockfile records hashes and provenance.
- [ ] Spawn does not copy the parent transcript.
- [ ] Tools are bound through capability and policy.
- [ ] Large observations become artifacts + summaries.
- [ ] Critical policies are enforced at runtime.
- [ ] Every skill has compatibility and freshness metadata.
- [ ] Evals measure trajectory, outcome, and cost.
- [ ] Changes pass through shadow, canary, and rollback.

## 20. Research agenda for the Multi Agent Harness

The original guide leaves the following research questions open:

1. What minimum composition of `RoleKernel + TaskCapsule + ActiveState` maximizes success per token?
2. For which models does active-frame paging help or hurt?
3. What is the gain from curated context versus full context for each role?
4. When should a specialist be a separate agent versus a skill?
5. Which pruning policy preserves invariants in coding agents?
6. How should multi-vendor adapters be compared without conflating model and harness?
7. Which playbook fields are stable across models, and which need tuning?
8. How should context leakage among overseer, implementer, and reviewer be measured?
9. What is the effect of tool discovery on success rate and time to first useful action?
10. How can total cost be optimized without removing procedural anchors that prevent unnecessary exploration?

These are preserved as **historical research pointers**, not as automatically-open CURRENT tare.tools gaps.

# Appendix A — Playbook schema

```yaml
apiVersion: harness.ai/v1alpha1
kind: Playbook
metadata:
  id: frontend-implementer
  version: 1.0.0
  owner: frontend-platform
  status: active
  lastValidatedAt: 2026-07-25
  revalidateAfter: 2026-10-25
compatibility:
  harness: ">=0.8 <1.0"
  frameworks:
    react: ">=18 <20"
activation:
  taskTypes: [frontend-feature, frontend-bugfix]
  pathPatterns: ["src/frontend/**"]
mission:
  objective: Implement frontend behavior with executable evidence.
  owns: [implementation-patch, relevant-tests, evidence]
  doesNotOwn: [requirements-approval, final-review, deployment]
context:
  required: [task-spec, acceptance-criteria, repository-profile]
  retrieveOnDemand: [nearby-components, nearby-tests, design-system]
  excluded: [unrelated-history, private-agent-scratchpads]
procedure:
  - inspect-existing-patterns
  - reproduce-current-behavior
  - map-criteria-to-changes-and-tests
  - implement-minimal-change
  - verify
  - produce-evidence
tools:
  allow: [repository.read, repository.search, repository.edit, command.test]
  deny: [production.deploy, secrets.read, policy.modify]
verification:
  required: [typecheck, relevant-tests]
handoff:
  outputSchema: implementation-result/v2
control:
  maxRetries: 2
  retryRequiresNewStrategy: true
evaluation:
  suite: frontend-implementer-evals/v3
```

# Appendix B — Compiler skeleton

```python
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class CompilationContext:
    task: dict[str, Any]
    project: dict[str, Any]
    selected_role: str
    selected_model: str
    vendor: str

@dataclass(frozen=True)
class EffectivePlaybook:
    manifest: dict[str, Any]
    workflow: dict[str, Any]
    prompt_plan: dict[str, Any]
    provenance: list[str]

class PlaybookCompiler:
    def compile(self, context: CompilationContext) -> EffectivePlaybook:
        sources = self.registry.resolve(context)
        ast = self.parser.parse_all(sources)
        normalized = self.normalizer.normalize(ast)
        self.schema_validator.validate(normalized)
        compatible = self.compatibility.filter(normalized, context)
        merged = self.precedence.resolve(compatible)
        capabilities = self.capability_binder.bind(merged, context)
        policy = self.policy_engine.evaluate(context, capabilities)
        policy.raise_if_denied()
        workflow = self.workflow_compiler.compile(merged, policy)
        prompt_plan = self.context_compiler.plan(merged, workflow, context)
        manifest = self.lock_builder.build(
            context, merged, capabilities, policy, workflow, prompt_plan
        )
        return EffectivePlaybook(
            manifest=manifest,
            workflow=workflow,
            prompt_plan=prompt_plan,
            provenance=[s.uri for s in sources],
        )
```

# Appendix C — Spawn algorithm

```python
def compile_spawn_envelope(parent_state, delegated_task, profile, vendor):
    role_kernel = resolve_role_kernel(profile)
    task_capsule = build_task_capsule(delegated_task)

    relevant_state = select_state(
        parent_state,
        preserve=[
            "binding_decisions",
            "open_dependencies",
            "known_evidence",
            "active_risks",
        ],
        exclude=[
            "private_reasoning",
            "unrelated_workstreams",
            "expired_tool_outputs",
        ],
    )

    capabilities = bind_capabilities(
        profile=profile,
        task=delegated_task,
        common_tool_limit=3,
        defer_remaining=True,
    )

    envelope = assemble(
        static_prefix=role_kernel,
        dynamic_body=[task_capsule, relevant_state, capabilities.index],
        terminal_frame=[delegated_task.current_step,
                        delegated_task.return_contract],
    )

    envelope = reduce_to_budget(
        envelope,
        tokenizer=vendor.tokenizer,
        budget=vendor.spawn_budget,
        protected_sections=[
            "authority",
            "objective",
            "acceptance_criteria",
            "policies",
            "active_state",
            "output_contract",
        ],
    )

    validate_no_silent_truncation(envelope)
    return envelope
```

## 21. Bibliography and sources

The dates below preserve the original document’s publication/consultation dates. Recent preprints are useful as bleeding-edge evidence but were explicitly not intended to justify irreversible decisions without reproduction.

1. **Internal project document (2026-07-14).** *Architectures for Adaptive Multi-Agent Harnesses with Project-Aware Routing, Dynamic Workflows, Self-Correction, and Self-Evolution under Deterministic Control.* Historical internal research plan.
2. [MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework](https://arxiv.org/abs/2308.00352)
3. [AgentCoder: Multi-Agent-based Code Generation with Iterative Testing and Optimisation](https://arxiv.org/abs/2312.13010)
4. [MASAI: Modular Architecture for Software-engineering AI Agents](https://arxiv.org/abs/2406.11638)
5. [SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering](https://arxiv.org/abs/2405.15793)
6. [Lost in the Middle: How Language Models Use Long Contexts](https://arxiv.org/abs/2307.03172)
7. [Prompting Is Programming: A Query Language for Large Language Models (LMQL)](https://arxiv.org/abs/2212.06094)
8. [PDL: A Declarative Prompt Programming Language](https://arxiv.org/abs/2410.19135)
9. [Prompt Declaration Language — Tutorial e documentação](https://ibm.github.io/prompt-declaration-language/)
10. [DSPy — Program, don’t prompt](https://dspy.ai/)
11. [DSPy Signatures in Depth](https://dspy.ai/diving-deeper/signatures-in-depth/)
12. [DSPy GEPA Optimization](https://dspy.ai/getting-started/gepa-optimization/)
13. [GitHub Agentic Workflows — Overview](https://github.github.com/gh-aw/)
14. [GitHub Agentic Workflows — Compilation Process](https://github.github.com/gh-aw/reference/compilation-process/)
15. [Agent Skills Specification](https://agentskills.io/specification)
16. [Best Practices for Skill Creators](https://agentskills.io/skill-creation/best-practices)
17. [Codex Best Practices](https://developers.openai.com/codex/learn/best-practices)
18. [Codex Sample Configuration — project_doc_max_bytes](https://developers.openai.com/codex/config-sample)
19. [Build Skills](https://developers.openai.com/codex/build-skills)
20. [Run Long-Horizon Tasks with Codex](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)
21. [Shell + Skills + Compaction: Tips for Long-Running Agents](https://developers.openai.com/blog/skills-shell-tips)
22. [Testing Agent Skills Systematically with Evals](https://developers.openai.com/blog/eval-skills)
23. [Build an Agent Improvement Loop with Traces, Evals, and Codex](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)
24. [Prompt Caching](https://developers.openai.com/api/docs/guides/prompt-caching)
25. [Create Custom Subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
26. [Extend Claude with Skills](https://docs.anthropic.com/en/docs/claude-code/skills)
27. [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
28. [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
29. [How We Built Our Multi-Agent Research System](https://www.anthropic.com/engineering/multi-agent-research-system)
30. [Code Execution with MCP: Building More Efficient AI Agents](https://www.anthropic.com/engineering/code-execution-with-mcp)
31. [Prompt Caching](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
32. [Context Windows](https://docs.anthropic.com/en/docs/build-with-claude/context-windows)
33. [Creating Custom Agents for Copilot Cloud Agent](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents)
34. [Adding Repository Custom Instructions for GitHub Copilot](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
35. [Simple Agents with LlmAgent](https://google.github.io/adk-docs/agents/llm-agents/)
36. [Template Agent Workflows](https://google.github.io/adk-docs/agents/workflow-agents/)
37. [Safety and Security for AI Agents](https://google.github.io/adk-docs/safety/)
38. [Skills for ADK Agents](https://google.github.io/adk-docs/skills/)
39. [Thinking in LangGraph](https://docs.langchain.com/oss/python/langgraph/thinking-in-langgraph)
40. [LangGraph Persistence and Checkpointers](https://docs.langchain.com/oss/python/langgraph/persistence)
41. [AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents](https://arxiv.org/abs/2503.18666)
42. [Compile, Then Page: Executable SOP Programs and a Capability-Gated Runtime for Procedural LLM Agents](https://arxiv.org/abs/2607.11346)
43. [SOP-Agent: Empower General Purpose AI Agent with Domain-Specific SOPs](https://arxiv.org/abs/2501.09316)
44. [AOrchestra: Automating Sub-Agent Creation for Agentic Orchestration](https://arxiv.org/abs/2602.03786)
45. [PerspectiveGap: A Benchmark for Multi-Agent Orchestration Prompting](https://arxiv.org/abs/2606.08878)
46. [AgentSpawn: Adaptive Multi-Agent Collaboration Through Dynamic Agent Spawning](https://arxiv.org/abs/2602.07072)
47. [SkillSmith: Compiling Agent Skills into Boundary-Guided Runtime Interfaces](https://arxiv.org/abs/2605.15215)
48. [SkillsBench: Benchmarking How Well Agent Skills Work Across Diverse Tasks](https://arxiv.org/abs/2602.12670)
49. [SWE-Skills-Bench: Do Agent Skills Actually Help in Real-World Software Engineering?](https://arxiv.org/abs/2603.15401)
50. [SkillReducer: Optimizing LLM Agent Skills for Token Efficiency](https://arxiv.org/abs/2603.29919)
51. [What Should a Skill Remember? Quality-Cost Trade-offs in Cost-Aware Skill Rewriting](https://arxiv.org/abs/2606.09421)
52. [Reducing Cost of LLM Agents with Trajectory Reduction (AgentDiet)](https://arxiv.org/abs/2509.23586)
53. [SWE-Pruner: Self-Adaptive Context Pruning for Coding Agents](https://arxiv.org/abs/2601.16746)
54. [SWE-Pruner Pro: The Coder LLM Already Knows What to Prune](https://arxiv.org/abs/2607.18213)
55. [LLMLingua: Compressing Prompts for Accelerated Inference of Large Language Models](https://arxiv.org/abs/2310.05736)
56. [LongLLMLingua: Accelerating and Enhancing LLMs in Long Context Scenarios](https://arxiv.org/abs/2310.06839)
57. [AgentFold: Long-Horizon Web Agents with Proactive Context Folding](https://arxiv.org/abs/2510.24699)
58. [AGORA: Adapter-Grounded Observation-Action Retention for Efficient Agent Contexts](https://arxiv.org/abs/2605.26596)
59. [Budget-Aware Context Management for Long-Horizon Agents](https://arxiv.org/abs/2604.01664)
60. [Agentic Context Management for Long-Horizon Tasks](https://arxiv.org/abs/2607.23809)
61. [VIGIL: Runtime Enforcement of Behavioral Specifications in AI Agent Skills](https://arxiv.org/abs/2606.26524)
62. [Prompt Engineering](https://developers.openai.com/api/docs/guides/prompt-engineering)
63. [Why Evaluate Agents](https://google.github.io/adk-docs/evaluate/)

---

**Translation note:** English derivative generated from the exact historical source. No scientific refresh or architectural ratification is implied.
