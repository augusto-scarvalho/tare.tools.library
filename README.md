# tare.tools.research

**A living research library for the tare.tools Agent Operating System.**

This repository preserves the scientific, empirical, and technical knowledge that informs tare.tools without turning research into architectural authority.

> **Canonical authority lives elsewhere.** `tare-tools` source code, Git state, ratified architecture, ADRs, SPECs, BDDs, and executable gates define CURRENT/TARGET. This repository contains **RESEARCH**, **PROPOSED** designs, experiments, findings, evidence, and research history.

## Why this repository exists

The tare.tools project began as a governed multi-vendor multi-agent harness and is evolving toward a **user-space Agent Operating System**: vendor-neutral, auditable, modular, evidence-driven, and conservative about self-evolution.

That evolution created a large body of work: scientific studies, vendor/runtime archaeology, architecture proposals, test and reliability research, local-model experiments, routing research, governance work, interface studies, and implementation evidence.

The repository went through several editorial phases:

1. **Historical corpus phase** — research accumulated as many independent studies, snapshots, translations, refreshes, implementation deltas, and generated projections.
2. **Compaction attempt** — redundant projections were removed, but the intellectual corpus was compressed too aggressively.
3. **Semantic curation v1** — eight concise syntheses preserved many conclusions but removed too much argumentation, bibliography, experimental context, and dissent surface.
4. **Semantic preservation v2** — the current candidate structure restores distinct research questions and deep lineages while keeping raw archival duplication out of HEAD.

The governing lesson is now explicit:

> **Remove redundancy, not knowledge.**

## Start here

If you are new to the repository, use this order:

1. **[Repository Navigation](NAVIGATION.md)** — the complete knowledge graph and all major reading paths.
2. **[Study Editions](studies/README.md)** — the shortest route to full HTML research editions and their living successors.
3. **[Agent OS Knowledge Map](syntheses/agent-os-knowledge-map.md)** — the conceptual spine of tare.tools research.
4. **[Research Reading Guide](syntheses/research-reading-guide.md)** — choose a research trail by question.
5. **[Living Research Index](research/README.md)** — all deep studies grouped by bounded context.
6. **[Curated Findings](findings/CURATED_FINDINGS.md)** — what the research currently supports.
7. **[Research Frontier](frontier/RESEARCH_FRONTIER.md)** — what remains unresolved.

## Web reading experience

The GitHub repository is the **source/audit view**. The same content can also be rendered as a GitHub Pages reading projection with persistent navigation, local search, responsive Markdown typography, direct access to rendered HTML study editions, and links back to the Git source.

The web projection does **not** duplicate the research corpus:

- Markdown is rendered from the files already tracked here;
- repository-relative links are reused by the Pages/Jekyll build;
- byte-preserved HTML studies remain unchanged and are served as real HTML pages instead of GitHub blob/source views;
- site navigation is projection metadata and has no architectural authority;
- deleting the generated site loses no research knowledge.

See **[GitHub Pages Reading Projection](catalog/GITHUB_PAGES_PROJECTION.md)** for the design and deployment safety rules. Deployment is deliberately gated because this repository is private.

## The research model

```text
Historical sources / experiments / external literature
                    │
                    ▼
                RESEARCH
                    │
             findings & tensions
                    │
                    ▼
          PROPOSED technical designs
                    │
             independent review
                    │
                    ▼
   canonical tare-tools ADR / SPEC / BDD / code
                    │
             gates & outcome evidence
                    │
                    └──────────────► new research
```

Research may **challenge** architecture. It does not silently promote itself into architecture.

## How the library is organized

| Area | Purpose | Where to continue |
|---|---|---|
| [`studies/`](studies/README.md) | Direct entry point to full HTML study editions | Living studies / sources |
| [`syntheses/`](syntheses/README.md) | Cross-lineage maps and reading guides | Deep research |
| [`research/`](research/README.md) | Living studies that retain arguments, literature, open questions, and scientific framing | Proposals / experiments / findings |
| [`proposals/`](proposals/README.md) | Problem-specific implementation research; always **PROPOSED** until reconciled | Canonical repo, not direct implementation |
| [`experiments/`](experiments/README.md) | Protocols, results, falsifications, and next gates | Related research and findings |
| [`case-studies/`](case-studies/README.md) | Concrete failures, false greens, runtime archaeology, and operational evidence | Research claims they support |
| [`findings/`](findings/README.md) | Condensed supported conclusions | Source studies / frontier |
| [`frontier/`](frontier/README.md) | Explicit unanswered questions | Next research/experiments |
| [`sources/`](sources/README.md) | Evidence registry, provenance, and source-edition map | HTML source editions / rehydration gaps |
| [`catalog/`](catalog/README.md) | Curation lineage, quality review, projection design, and known gaps | Historical recovery |
| [`bridge-editions/`](bridge-editions/README.md) | Byte-preserved scientific refresh checkpoints | Living studies that supersede them as reading surface |

## Core research spine

```text
Project / Demand
      │
      ▼
Governed Work / Workflow
      │
      ▼
Policy / Authority / Permit
      │
      ▼
RouteIntent → RouteDecision → ExecutionBinding
      │
      ▼
Runtime + Capability / ActionRequest
      │
      ▼
Logical Effect → Reconciliation → EffectReceipt
      │
      ▼
Validation / Assurance / OutcomeEvidence
      │
      ▼
Attribution / Qualification / Reputation
      │
      ▼
Context / Memory / Procedure / Learning
      │
      ▼
Evolution candidate → independent evaluation → governed promotion
```

Two cross-cutting research lines run through the whole spine:

- **Canonical Lineage** asks whether identity, provenance, causation, and historical reconstruction survive every boundary.
- **Information Survival** asks what must persist, what may be reconstructed, and which physical store is appropriate without letting storage technology own semantics.

## Status vocabulary

Every document should make its epistemic role clear:

- **CURRENT** — verified implemented state in the canonical tare-tools system.
- **TARGET** — ratified desired architecture in the canonical repository.
- **PROPOSED** — design or implementation research not yet ratified.
- **RESEARCH** — evidence, hypothesis, synthesis, experiment, or scientific interpretation.
- **BRIDGE EDITION** — preserved scientific checkpoint useful for comparison/history.
- **HISTORY ONLY** — recoverable through Git/File Library but intentionally absent from the live reading surface.

## Navigation convention

A living research document should never be a dead end. Each maintained Markdown study is expected to expose:

- a link back to **[Repository Navigation](NAVIGATION.md)** or its local index;
- its relevant **HTML/source edition** when available;
- related research;
- the corresponding technical proposal, experiment, or case study when one exists;
- a clear **previous / next / continue** path.

Byte-preserved HTML checkpoints are intentionally immutable. Their surrounding directory indexes and the **[Study Editions](studies/README.md)** page provide the return path to the living library.

## Preservation and provenance

Git remains the archaeological history. HEAD is the current study surface.

Several deepest 2026-08-10/12 HTML studies still exist exactly in File Library rather than as Git blobs. Their identities and hashes are tracked in **[Deep-Artifact Rehydration Gaps](catalog/REHYDRATION_GAPS.md)**. The Markdown preservation editions are authored reconciliations and must never be misrepresented as byte-identical originals.

For the curation rules, read **[Document Policy](DOCUMENT_POLICY.md)** and **[Agent Instructions](AGENTS.md)**.

---

**Next:** [Study Editions →](studies/README.md) · [Repository Navigation →](NAVIGATION.md)
