<div align="center">

# tare.tools.harness (Legacy Prototype)

**Historical Monolithic Research Prototype for Multi-Agent Coding Swarms (July – August 2026).**

[![Status: Frozen & Archived](https://img.shields.io/badge/Status-FROZEN%20%26%20ARCHIVED-critical.svg)](#archival-and-post-mortem-notice)
[![Succeeded by tare.tools.os](https://img.shields.io/badge/Successor-tare.tools.os%20(Agent%20OS)-blue.svg)](https://github.com/augusto-scarvalho/tare.tools.os)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Architecture: Legacy Monolith](https://img.shields.io/badge/Architecture-Monolithic%20Harness%20(Deprecated)-inactive.svg)](#why-the-monolith-was-deprecated)
[![Post-Mortem](https://img.shields.io/badge/Post--Mortem-Forensic%20Audit%20Complete-purple.svg)](docs/POST_MORTEM_AND_ARCHITECTURAL_PIVOT.md)

<p align="center">
  <a href="#archival-and-post-mortem-notice">Archival Notice</a> •
  <a href="#evolutionary-timeline">Evolution Timeline</a> •
  <a href="#why-the-monolith-was-deprecated">Post-Mortem & Failures</a> •
  <a href="#the-golden-heritage-what-was-reused-vs-retired">Golden Heritage Matrix</a> •
  <a href="#the-modern-federated-architecture">Successor Architecture</a> •
  <a href="#ecosystem-family">Ecosystem Family</a> •
  <a href="#license">License</a>
</p>

</div>

---

> [!WARNING]
> ### 🛑 ARCHIVAL & POST-MORTEM NOTICE
> **`tare.tools.harness` is formally frozen, deprecated, and preserved strictly for historical, forensic, and scientific research purposes.**
>
> All active development has migrated to the **decentralized, 5-plane federated Agent Operating System ([`tare.tools.os`](https://github.com/augusto-scarvalho/tare.tools.os))** governed by **ADR-044 through ADR-050**.

---

## Evolutionary Timeline

During July and August 2026, `tare.tools.harness` served as our testbed to validate multi-agent autonomous engineering pipelines (*Planner $\rightarrow$ Implementer $\rightarrow$ Auditor $\rightarrow$ Gatekeeper*). The lessons gathered across four intense development phases led directly to the modern federated Agent OS:

```mermaid
flowchart LR
    T1["📅 July 14<br/>Phase 1: Theoretical Foundation<br/>Adaptive harness & multi-agent routing research"]
    --> T2["📅 July 27<br/>Phase 2: Context Crisis<br/>42.9k tokens/run for 0 accepted capsules"]
    --> T3["📅 August 9-12<br/>Phase 3: Vendor Hook Fatigue<br/>Maintenance fragility of CLI-specific terminal hooks"]
    --> T4["📅 August 15<br/>Phase 4: Cartorial Gridlock<br/>44 ceremony tokens per 1 code token (MWR = 44.05)"]
    --> T5["🚀 August 19<br/>The Definitive Pivot<br/>7 North Stars (ADRs 044-050) & 5 decoupled satellites"]

    classDef stageStyle fill:#1e1e2e,stroke:#89b4fa,stroke-width:2px,color:#cdd6f4;
    classDef pivotStyle fill:#182820,stroke:#a6e3a1,stroke-width:2px,color:#a6e3a1;

    class T1,T2,T3,T4 stageStyle;
    class T5 pivotStyle;
```

---

## Why the Monolith was Deprecated (Post-Mortem)

As documented in the comprehensive forensic audit ([`docs/POST_MORTEM_AND_ARCHITECTURAL_PIVOT.md`](docs/POST_MORTEM_AND_ARCHITECTURAL_PIVOT.md)), five systemic flaws made the monolithic harness unsustainable:

### 1. Chronic Context Bloat (42.9k tokens per run)
* **The Symptom:** Workers spent 90%+ of their LLM context window re-reading global digests, `AGENTS.md` manuals, and tool catalogs (~15k fixed tokens per boot) before receiving task instructions.
* **The Resolution:** Replaced by **surgical Context Envelopes (< 4,000 tokens)** generated on demand by [`tare.tools.specgraph`](https://github.com/augusto-scarvalho/tare.tools.specgraph).

### 2. The Vendor Hook Maintenance Trap (*Whack-a-Mole*)
* **The Symptom:** Intercepting LLM CLIs (Codex, Claude Code, Kimi) via regex monkeypatching broke on every vendor CLI update and leaked unneeded schemas into prompt contexts.
* **The Resolution:** Replaced by **Anti-Corruption Layers (ACL)** and process-isolated workers in [`tare.tools.kernel`](https://github.com/augusto-scarvalho/tare.tools.kernel).

### 3. Cartorial Hypertrophy & Governance Deadlocks (MWR = 44.05)
* **The Symptom:** Over-accumulated validation gates created a cartorial spiral where a 6-word markdown fix required an 8.6 KB permit, SHA-256 signatures, and 14 manual approval steps.
* **The Resolution:** Replaced by **bounded $O(1)$ Compare-And-Swap (CAS) transitions** in [`tare.tools.backlog-graph`](https://github.com/augusto-scarvalho/tare.tools.backlog-graph).

### 4. Filesystem Race Conditions without CAS
* **The Symptom:** Co-coordinating multiple agents via raw JSON files on shared disks caused lost updates, write collisions, and corrupted task states.
* **The Resolution:** Replaced by **SQLite 3 Write-Ahead Logging (WAL)** with `BEGIN IMMEDIATE` single-writer CAS concurrency.

### 5. Research & Engineering Domain Entanglement
* **The Symptom:** Exploratory research trials, benchmark rounds (CMRP, token audits), and runtime engineering code were co-located in the same monolith, creating confusion between disposable experimental probes and production software.
* **The Resolution:** Clear separation of concerns: engineering engines operate in focused satellites, while empirical research orchestration, experimental protocols, and knowledge curation live in [`tare.tools.research`](https://github.com/augusto-scarvalho/tare.tools.research).

---

## The Golden Heritage: What was Reused vs. Retired

No valuable engineering discovery was discarded. The brilliant concepts proven in the harness were extracted, hardened, and graduated into dedicated repositories:

```mermaid
flowchart LR
    subgraph Monolith ["Legacy Prototype (tare.tools.harness)"]
        H_SDD["Spec-Driven Development"]
        H_DAG["Task Backlog Graph"]
        H_AST["Dialog Statecharts"]
        H_SBX["Execution Sandboxing"]
        H_RT["Tripartite Deliberation"]
        H_EXP["Empirical Research Orchestration"]
    end

    subgraph Satellites ["Modern Federated Satellites"]
        S_SPEC["tare.tools.specgraph<br/>(Tree-Sitter Causal Matrix)"]
        S_BACK["tare.tools.backlog-graph<br/>(Deterministic DAG Engine)"]
        S_DIAL["tare.tools.dialog-engine<br/>(Universal Dialog AST)"]
        S_KERN["tare.tools.kernel<br/>(5-Plane Microkernel & bwrap)"]
        S_OS["tare.tools.os<br/>(Tripartite Swarm Orchestration)"]
        S_RES["tare.tools.research<br/>(Scientific Protocols & Empirical Hub)"]
    end

    H_SDD -->|"Graduated to"| S_SPEC
    H_DAG -->|"Graduated to"| S_BACK
    H_AST -->|"Graduated to"| S_DIAL
    H_SBX -->|"Graduated to"| S_KERN
    H_RT -->|"Graduated to"| S_OS
    H_EXP -->|"Graduated to"| S_RES

    classDef monStyle fill:#2d1b20,stroke:#f38ba8,stroke-width:2px,color:#cdd6f4;
    classDef satStyle fill:#182820,stroke:#a6e3a1,stroke-width:2px,color:#cdd6f4;

    class H_SDD,H_DAG,H_AST,H_SBX,H_RT,H_EXP monStyle;
    class S_SPEC,S_BACK,S_DIAL,S_KERN,S_OS,S_RES satStyle;
```

---

## What was Retired

| Retired Anti-Pattern | Reason for Retirement | Modern Replacement |
|---|---|---|
| ❌ **186-Module Mega Monolith** | Context pollution and coupling | 5 focused satellite repositories federated by Git Submodules |
| ❌ **Vendor CLI Monkeypatching** | Fragile regex hooks breaking on CLI updates | Process isolation & ACL drivers in `tare.tools.kernel` |
| ❌ **Boot Prompt Stuffing (`AGENTS.md`)** | Instruction dilution & token waste | Surgical Context Envelopes (< 4k tokens) via `specgraph` |
| ❌ **Unsynchronized Shared JSON Files** | Lost updates and race conditions | SQLite 3 WAL CAS engine with `BEGIN IMMEDIATE` |
| ❌ **Infinite Cartorial Permit Loops** | High Meta-Work Ratio (MWR = 44.05) | Atomic $O(1)$ state transitions and 1-click landing |

---

## The Modern Federated Architecture

The modern architecture separates concerns into specialized, autonomous repositories coordinated by [`tare.tools.os`](https://github.com/augusto-scarvalho/tare.tools.os):

```mermaid
flowchart TD
    OS["🏛️ tare.tools.os (Agent Operating System)<br/>Central Orchestrator, Tripartite Round Table, Submodule Federation"]

    Kernel["⚙️ tare.tools.kernel<br/>5-Plane Microkernel, SQLite WAL, bwrap Sandboxes"]
    SpecGraph["🔍 tare.tools.specgraph<br/>Tree-Sitter SDD & Living Causal Traceability Matrix"]
    Backlog["📊 tare.tools.backlog-graph<br/>Deterministic DAG Task Engine & CAS Transitions"]
    Dialog["💬 tare.tools.dialog-engine<br/>Universal Conversational AST & 12-Phase Validator"]
    Research["🔬 tare.tools.research<br/>Scientific Hub, ADRs & Hardware Lab Experiments"]

    OS --> Kernel
    OS --> SpecGraph
    OS --> Backlog
    OS --> Dialog
    OS --> Research

    classDef osStyle fill:#1e1e2e,stroke:#89b4fa,stroke-width:2px,color:#cdd6f4;
    classDef satStyle fill:#1e2a3a,stroke:#74c7ec,stroke-width:2px,color:#cdd6f4;

    class OS osStyle;
    class Kernel,SpecGraph,Backlog,Dialog,Research satStyle;
```

---

## Ecosystem Family

| Repository | Role | Technology | Status |
|---|---|---|---|
| **[`tare.tools.os`](https://github.com/augusto-scarvalho/tare.tools.os)** | Central Agent Operating System & Swarm Orchestrator | Python, AsyncIO, Submodules | 🟢 **ACTIVE** |
| **[`tare.tools.kernel`](https://github.com/augusto-scarvalho/tare.tools.kernel)** | 5-Plane Microkernel Runtime & Sandboxing | Python, SQLite WAL, bwrap | 🟢 **ACTIVE** |
| **[`tare.tools.specgraph`](https://github.com/augusto-scarvalho/tare.tools.specgraph)** | Spec-Driven Development & Causal Matrix | Python AST, Tree-Sitter, Schemas | 🟢 **ACTIVE** |
| **[`tare.tools.backlog-graph`](https://github.com/augusto-scarvalho/tare.tools.backlog-graph)** | Deterministic DAG Task Backlog Engine | Python (Pure Stdlib), CAS | 🟢 **ACTIVE** |
| **[`tare.tools.dialog-engine`](https://github.com/augusto-scarvalho/tare.tools.dialog-engine)** | Topological Interaction & AST Dialog Graphs | Python, Statecharts, orjson | 🟢 **ACTIVE** |
| **[`tare.tools.research`](https://github.com/augusto-scarvalho/tare.tools.research)** | Scientific Papers, ADRs & Knowledge Hub | Markdown, GitHub Pages, Jekyll | 🟢 **ACTIVE** |
| **[`tare.tools.harness`](https://github.com/augusto-scarvalho/tare.tools.harness)** | Monolithic Research Prototype (This Repo) | Python (Legacy Monolith) | 🔴 **FROZEN / ARCHIVED** |

---

## Documentation Archive

The full documentation archive and post-mortem analyses are organized under [`docs/`](docs/):
* **[`docs/POST_MORTEM_AND_ARCHITECTURAL_PIVOT.md`](docs/POST_MORTEM_AND_ARCHITECTURAL_PIVOT.md):** Complete forensic post-mortem and migration audit.
* **[`docs/INDEX.md`](docs/INDEX.md):** Master index of all historical research papers and architecture notes.
* **[`docs/HARNESS_ARCHITECTURE.md`](docs/HARNESS_ARCHITECTURE.md):** Legacy prototype architecture and layer diagrams.
* **[`docs/HARNESS_TECHNICAL_DEBT.md`](docs/HARNESS_TECHNICAL_DEBT.md):** Legacy technical debt registry.

---

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
