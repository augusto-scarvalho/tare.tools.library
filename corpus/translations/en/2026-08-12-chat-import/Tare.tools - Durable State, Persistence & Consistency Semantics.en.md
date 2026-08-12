# tare.tools — Durable State, Persistence & Consistency Semantics

**English derivative of the recovered chat research summary**  
**Status:** `MACHINE_TRANSLATED_UNREVIEWED` · `DERIVED_NON_AUTHORITATIVE`  
**Source:** `Tare.tools - Durable State, Persistence & Consistency Semantics.txt`  
**Authority:** RESEARCH / PROPOSED only. This translation does not promote historical claims to CURRENT or TARGET.

I closed this round as a **new cross-lineage formal research pack for tare.tools**, following the editorial pattern already used for Workflow, Reliability, and Identity: numbered sidebar index, in-text references, bibliography, explicit `CURRENT × TARGET × PROPOSED × RESEARCH`, ADOPT/ADAPT/RETIRE/OPEN, falsifiable hypotheses, research pointers, and a separate technical document that **does not present itself as ratified implementation**.

The research was deliberately divided because the topic revealed four related but epistemically distinct problems:

1. **Master Index — Information Survival, Demand Lineage & Reconstructable Assurance** — entry point and recovery map.
2. **Scientific Research — Information Survival, Repository Boundaries & Reconstructive Assurance** — Git × state × artifacts × research × projections, Reconstructive Closure, records/archival science, reproducible builds, provenance, retention, Evidence Recall, semantic compaction, and distribution.
3. **Scientific Research — Demand Lineage, Context Reconstruction & Governed Learning** — `Intake → Demand → Work → Context → Effect → Evidence → Outcome → Settlement → Learning`, requirements traceability, Task revision, interactive coding, self-evolving skills, and cross-Project learning.
4. **Technology Landscape — Reconstructability, Verification & Evidence** — OCI/ORAS, SLSA/in-toto/Sigstore, BuildKit/Bazel, OpenTelemetry, OpenLineage, GUAC, Temporal/Restate/DBOS, MLflow, OpenFeature, Jujutsu, lakeFS, and related inspiration.
5. **Technical Proposal — Information Survival & Reconstructable Assurance** — contracts/views, golden queries, BDDs, fault matrix, qualification packs, Strangler slices, rollback, and candidate Implementation Packets.

The research bundle was structurally validated as five HTML documents with no duplicate IDs, no broken internal anchors, no apparent UTF-8 corruption, and bibliographies. The reported bundle SHA-256 is `0c2968f472d5f88c7fa403799b5e2afa7846c3c34653489d60e3ddfc7b3a756e`.

## What the research changed or strengthened

The first important result is that **“Git hygiene” is demoted from an architectural problem to a symptom**. The broader issue is *information survival*: owner, authority, semantic home, identity, reconstructability, freshness, retention, privacy, distribution, proof role, and disposition. The resulting direction is selective preservation of irreversible facts and relationships, aggressive reconstruction of derived representations, governed retention, and refusal to let a physical store own the meaning of the object.

The second strong conclusion is **Reconstructive Closure**. A Project revision should be able to materialize an operationally equivalent system from a seed and declared inputs, without depending on agent memory, private HOME state, or an old projection. The research explicitly distinguishes *reconstructible*, *deterministically reproducible*, *bit reproducible*, and *independently reproducible*.

The third conclusion is that **Demand Conservation is not only an analogy**. Requirements-traceability research and interactive coding benchmarks show a real gap between “issue text” and reconstructed need. SWE-Together preserves intention/interventions in reproducible tasks; SWE-INTERACT exposes requirements progressively; SWE-RPG introduces intermediate ground truth for Requirement Clarification and Implementation Planning; ClarifyCodeBench evaluates ambiguity clarification.

The resulting chain is:

```text
Raw Intake
    ↓
Grounded Demand
    ↓
Requirements / Constraints
    ↓
Disposition / Admission
    ↓
Durable Work
    ↓
Context Materialization
    ↓
Execution / Effects
    ↓
Evidence
    ↓
Outcome
    ↓
Settlement
```

The technical proposal deliberately **does not create `Demand` as a primitive**. It first asks whether existing canonical seams can answer the required golden queries. An ADR gap exists only if origin/disposition cannot be represented unambiguously.

## August frontier evidence

**RETRACE** independently verifies a generated patch through bidirectional reconstruction, including inferring from the patch what problem it appears to solve and reconciling that with the original demand. It is not a replacement for tests or Assurance; it is a candidate independent semantic signal and supports the principle that **the generator should not own the entire interpretation used to judge it**.

**RepoProbe** evaluates architecture-aware repository understanding and exposes *edit bias*: models tend to edit before sufficiently understanding architecture. It uses checklists of atomic verifiable facts rather than a single opaque judge score, connecting to Graphify/source verification and Proof of Understanding Before Write.

**EA-Graph** anchors verification claims to the exact artifacts used to establish them and keeps **evidence strength distinct from freshness**. If upstream support disappears, a claim can become `unprovable` rather than having continuity invented. This strongly aligns with `subject identity + freshness/invalidation + historical verdict preservation`.

**From Agent Traces to Trust** frames agent provenance as a typed graph linking evidence, tool outputs, memory, observations, claims, and actions, shifting evaluation from final-answer correctness toward process-level accountability.

## Learning and evolution

The second research document does not equate “self-learning” with saving chats. The 2026 skill frontier increasingly explores **external procedural state with an explicit lifecycle**: AutoSkill, SkillOpt, SkillOS, SkillsVote, MUSE-Autoskill, SkillWiki, and related systems.

The tare.tools synthesis is more conservative:

```text
Experience
   ↓
Finding / Hypothesis
   ↓
Attribution
   ↓
Learning Eligibility
   ↓
Procedure / Memory / Strategy Candidate
   ↓
Replay / holdout / shadow
   ↓
Independent Evidence
   ↓
Promotion
```

And it preserves the rule:

> **Agents discover structure; proven structure may be compiled into deterministic machinery.**

Mature learning can therefore result in **less agency**, not necessarily more.

## Technology landscape discipline

The technology document introduces a **semantic exit test**:

> If we remove a technology tomorrow, do we lose only mechanics/convenience, or do we lose the ability to interpret our own concepts?

OCI/ORAS therefore appears as a strong laboratory candidate for content-addressed payloads; SLSA/in-toto/Sigstore as projection/attestation; OpenTelemetry as observability projection; OpenLineage as interchange; GUAC as inspiration for reverse blast-radius; BuildKit/Bazel for content-addressed execution/cache; Temporal/Restate/DBOS as durable-runtime candidates; and MLflow as an experiment lab. None receives ownership of `Task`, `Authority`, `EffectReceipt`, or `OutcomeEvidence`.

The OpenTelemetry GenAI work on Task and long-running-agent lifecycle semantics is treated as evolving RESEARCH/interchange, not as a reason to remodel tare contracts.

## Deliberately low-authority technical path

The proposal starts with:

```text
S0  Repository Boundary Audit read-only
S1  Canonical Lineage golden queries read-only
S2  Clean Project Seed reconstruction lab
S3  Context Reconstruction View
S4  VerificationEnvironment façade over incumbent
S5  ArtifactBackend SPI + OCI laboratory
S6  OTel / OpenLineage / SLSA projections
S7  Repository Content Policy in shadow
S8  one low-risk independent qualification
S9  Evidence Recall read-only
S10 Evidence Reuse shadow
S11 promote one proven optimization only
```

This preserves Strangler migration, the stable incumbent, and rollback. The proposal also includes BDD candidates for Demand Conservation, session loss/rehydration, reviewer information boundaries, delayed reopening, Evidence Recall, private→distribution conflicts, generated-product exceptions, target fidelity, and candidate-not-controlling-judge.

## Research pointers worth preserving

Large branches intentionally left for later work include:

- **Archival Science & long-term executability**
- **Semantic Compaction with Preserved Golden Queries**
- **Bitemporal Artifact/Evidence Semantics**
- **Evidence Reuse / invalidation calculus**
- **Windows-native ephemeral verification**
- **Demand Accounting & Settlement Science**
- **Task Revision & Scope Change Semantics**
- **Adaptive Assurance / Value of Information**
- **Causal Attribution & Counterfactual Replay**
- **Experience Transportability & Project Archetypes**
- **Federated Experience**
- **Adaptive Retention / Survival Value**
- **Content-Addressed Storage / GC**

Three especially valuable new pointers are:

> **Artifact-Anchored Verification Memory & Upstream Drift** — connect EA-Graph, Canonical Lineage, Graphify/source identity, Evidence Reuse, and requalification.

> **Independent Semantic Verification of Agent Work** — combine RETRACE, deterministic tests, independent runtime, and EvidenceFamily diversity.

> **Requirement Clarification as Governed Intake** — connect SWE-RPG, ClarifyCodeBench, Demand Conservation, and Task revision.

The pack was intentionally written so these pointers can be recovered without replaying the entire conversation.
