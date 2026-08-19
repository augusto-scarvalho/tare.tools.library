# 📚 tare.tools.library — Central Technical Library, SSOT of Memory & Knowledge

[![CI Validation](https://github.com/augusto-scarvalho/tare.tools.research/actions/workflows/validate.yml/badge.svg)](https://github.com/augusto-scarvalho/tare.tools.research/actions)
[![Bookkeeper Compliance](https://img.shields.io/badge/bookkeeper-100%25%20compliant-brightgreen)](#-bookkeeping-engine--hygiene)
[![ADRs](https://img.shields.io/badge/ADRs-ADR--001%20..%20ADR--052-blue)](docs/adr/)
[![Ecosystem](https://img.shields.io/badge/ecosystem-TARE%202.0-orange)](https://github.com/augusto-scarvalho/tare.tools.os)

> **The Central Repository of Architectural Knowledge, Historical Memory, and Specifications for the TARE Ecosystem.**  
> Formally ratified by **ADRs 043 through 052** as the *Single Source of Truth (SSOT)* for Architectural Decisions, Forensic Post-Mortems, Empirical Benchmarks, and Historical Corpus.

---

## 🏛️ The Triple Axis of Autonomous Engineering (ADR-051)

Autonomous intelligence across the TARE ecosystem is structured in a clear, non-overlapping tripartite model:

```mermaid
flowchart TD
    subgraph Axis1 ["1. Knowledge & Memory Axis (The Why)"]
        Library["📚 tare.tools.library (Canonical SSOT)<br/>• Global ADRs (ADR-001 through ADR-052)<br/>• Incident Post-Mortems & RCA<br/>• Empirical Experiments (EXP-01..05)<br/>• Hybrid Substrate: Ontology & Dense Vectors"]
    end

    subgraph Axis2 ["2. Order & Execution Axis (The When & What)"]
        Backlog["📊 tare.tools.backlog-graph<br/>• Task DAG decomposed from ADRs<br/>• O(1) Execution Frontier<br/>• Atomic Concurrency Control (CAS)"]
    end

    subgraph Axis3 ["3. Topology & Code Axis (The Where & How)"]
        Spec["🔍 tare.tools.specgraph<br/>• Substrate Admission Gate (SAG)<br/>• Live Causal Indexing (ADR ➔ AST ➔ Tests)<br/>• Incremental Blast Radius sub-5ms<br/>• Surgical Context Envelopes (< 4k tokens)"]
    end

    subgraph Execution ["4. Zero-Cost Execution Substrate ($0)"]
        ZeroCost["⚡ Triple Zero-Cost Substrate<br/>• Local slop.cpp @ aaaaa (RTX 3090): 24/7 Bookkeeper & Implementers<br/>• Gemini API Free Tier (1M+ tokens): Massive Chat Ingestion<br/>• NVIDIA Build NIMs: Dense Embeddings & Reranking"]
    end

    Library -->|Requirements & DoD| Backlog
    Backlog -->|Ready Task Dispatch| Spec
    Spec -->|SAG Validated + Context Envelope| ZeroCost
    ZeroCost -->|Test Receipts & Evidence| Library

    classDef lStyle fill:#2d1b4e,stroke:#cba6f7,stroke-width:2px,color:#cdd6f4;
    classDef bStyle fill:#1e1e2e,stroke:#89b4fa,stroke-width:2px,color:#cdd6f4;
    classDef sStyle fill:#182820,stroke:#a6e3a1,stroke-width:2px,color:#a6e3a1;
    classDef zStyle fill:#2d201b,stroke:#f9e2af,stroke-width:2px,color:#cdd6f4;

    class Library lStyle;
    class Backlog bStyle;
    class Spec sStyle;
    class ZeroCost zStyle;
```

---

## 🧭 Repository Navigation

The library is partitioned into strict governance zones (ADR-052):

### 1. 📁 [`docs/`](docs/) — Active Knowledge & SSOT
* **[`docs/adr/`](docs/adr/):** Canonical Architectural Decision Records ([ADR-043](docs/adr/ADR-043_NORTH_STAR_V2_AND_ECOSYSTEM_SPLIT.md) through [ADR-052](docs/adr/ADR-052_IDENTITY_TRANSITION_TO_LIBRARY_AND_CORPUS_GOVERNANCE.md)).
* **[`docs/ARCHITECTURAL_QA_LEDGER.md`](docs/ARCHITECTURAL_QA_LEDGER.md):** Architectural Ledger logging all 24 questions, directives, and decisions from the Human Operator.
* **`docs/post-mortems/`:** Forensic Root Cause Analysis (RCA) reports with empirical measurements.
* **[`docs/templates/EXP-template.md`](docs/templates/EXP-template.md):** Lean template for empirical benchmarks.

### 2. 🧪 [`experiments/`](experiments/) — Empirical Experiments & Benchmarks
* **[`experiments/README.md`](experiments/README.md):** Central registry table of experiments with verdicts (`ADOPT`, `ADAPT`, `RETIRE`).
* **[`experiments/local-llm/`](experiments/local-llm/):** Local `slop.cpp` runtime benchmarks, KV-cache retention, and VRAM placement on the RTX 3090 (`EXP-01` through `EXP-05`).

### 3. 🏺 [`archaeology/`](archaeology/) — Fossil Memory & Archaeology
* **[`archaeology/README.md`](archaeology/README.md):** Immutable archive (`status: archived_immutable`) containing 93 pre-consolidated documents and historical chat transcripts under cryptographic custody.

### 4. 🛠️ [`tools/bookkeeper/`](tools/bookkeeper/) — Bookkeeping & Hygiene Engine
* Automated continuous curation utilities:
  * `dedup_detector.py`: Near-duplicate detection via token n-grams and Jaccard similarity.
  * `ssot_registry.py`: Single `CANONICAL_SSOT` status validation per topic.
  * `tombstone_manager.py`: Creation and verification of Tombstone pointers.
  * `cli.py`: Command-line tool for local and CI audits.

---

## ⚡ Bookkeeper Engine (CLI Usage)

```powershell
# Run full library audit suite
python -m tools.bookkeeper.cli audit --root docs

# Scan for duplicates or semantic drift (>70%)
python -m tools.bookkeeper.cli dedup --root docs --threshold 0.70

# Audit SSOT uniqueness
python -m tools.bookkeeper.cli ssot --root docs

# Verify tombstone link integrity
python -m tools.bookkeeper.cli tombstone --verify --root docs
```

---

## 🎯 Agile Documentation Mandate (Constitutional Invariant)

Per **ADR-051**:
* **Human Prerogative:** Formal academic papers are produced exclusively upon demand by the Human Operator.
* **AI Agent Mandate:** *“Document the right thing, in the right place, at the right time”*:
  1. *In Code Satellites:* Only direct operational docs for APIs, CLI, and tests.
  2. *In Incidents:* RCA post-mortems with measurements and commit hashes in `docs/post-mortems/`.
  3. *In Benchmarks:* Hardware logs and empirical numbers in `experiments/`.
  4. *In Global Decisions:* Canonical ADRs consolidated in `docs/adr/`.

---

## 🧪 Test Suite

```powershell
# Run all tests (71+ automated tests)
pytest
```

---
*Maintained by the TARE ecosystem under the direction of the Human Operator.*
