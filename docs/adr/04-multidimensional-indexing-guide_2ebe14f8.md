# Comprehensive Multidimensional Indexing Guide — SpecGraph

**`tare.tools.specgraph`** is the **Spec-Driven Development (SDD)** and **Causal Traceability Matrix** engine for autonomous agent-assisted and human engineering workflows.

This guide documents how to structure, annotate, and index all 5 causal dimensions of a governed repository.

---

## 1. The 5 Indexing Dimensions

```
                            ┌─────────────────────────┐
                            │    ADRs & RFCs (Why)    │
                            └────────────┬────────────┘
                                         │ SPEC_GOVERNED_BY_ADR
                                         ▼
                            ┌─────────────────────────┐
                            │  Specifications (What)  │
                            └──────┬───────────┬──────┘
        SCHEMA_IMPLEMENTS_SPEC      │           │      API_IMPLEMENTS_SPEC / MCP_TOOL
         ┌──────────────────────────┘           └───────────────────────────┐
         ▼                                                                  ▼
┌───────────────────────────┐                                 ┌───────────────────────────┐
│  Data Schemas & Contracts │                                 │   API & MCP Interfaces    │
│(SQL DDL / JSON / Pydantic)│                                 │(FastAPI / Starlette / MCP)│
└─────────────┬─────────────┘                                 └─────────────┬─────────────┘
              │                                                             │
              │                 ┌───────────────────────────┐               │
              └────────────────►│   Python AST Source Code  │◄──────────────┘
                                └─────────────┬─────────────┘
                                              │ TEST_VERIFIES_SPEC
                                              ▼
                                ┌───────────────────────────┐
                                │   Pytest Tests & Proofs   │
                                └───────────────────────────┘
```

---

## 2. Dimension 1: Architecture and Decisions (ADRs & RFCs)

Default discovery paths: `docs/adr/`, `adrs/`, `rfcs/`, `docs/decisions/`.

### Recommended Format (`docs/adr/ADR-0046.md`)

```markdown
---
id: ADR-046
title: Content-Addressed Storage Engine
status: ACCEPTED
superseded_by: null
governed_specs:
  - SPEC-CAS-001
  - SPEC-CAS-002
decision_drivers:
  - Cryptographic block immutability
  - SQLite WAL concurrency with zero lock-stealing
---

# ADR-046: Content-Addressed Storage Engine

## Status
ACCEPTED

## Context and Decision Drivers
We need immutable storage with SHA-256 guarantees for the Agent OS.

## Consequences
- Accelerates state reconciliation;
- Requires primary keys based on payload digests.
```

> **Drift Rule:** If an ADR changes status to `SUPERSEDED` and declares `superseded_by: ADR-048`, `specgraph drift-check` flags a violation if associated specifications remain active without updates.

---

## 3. Dimension 2: Technical Specifications (Specs & SDDs)

Default discovery paths: `specs/`, `docs/specs/`.

### Recommended Format (`specs/SPEC-CAS-001.md`)

```markdown
---
id: SPEC-CAS-001
title: Atomic Leases and Transactions in CAS
status: APPROVED
implements:
  - REQ-STORAGE-01
target_symbols:
  - src/cas_store.py:CASStore.begin_immediate
acceptance_criteria:
  AC-01: Initiate IMMEDIATE transaction without residual read locks
  AC-02: Emit immutable SHA-256 digest for each written chunk
---

# SPEC-CAS-001: Atomic Leases and Transactions in CAS

## 1. Intent
Ensure ACID write isolation across multiple local processes.
```

---

## 4. Dimension 3: Data Schemas and Contracts

Default discovery paths: `src/`, `schemas/`, `sql/`, `docs/schemas/`.

### A. SQL DDL & SQLite Schemas (`src/schema.sql`)
Annotate in the comment block preceding the table:

```sql
-- @spec SPEC-CAS-001 [AC-01, AC-02]
CREATE TABLE cas_blocks (
    digest TEXT PRIMARY KEY,
    byte_size INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_blob BLOB NOT NULL
);
```

### B. JSON Schemas (`schemas/token_payload.json`)
Annotate via `$spec` property or within the description:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TokenPayload",
  "$spec": "SPEC-AUTH-001",
  "type": "object",
  "properties": {
    "sub": { "type": "string", "description": "User ID" },
    "exp": { "type": "integer", "description": "Unix timestamp" }
  },
  "required": ["sub", "exp"]
}
```

### C. Pydantic Models and Python Dataclasses (`src/models.py`)
Annotate in the class docstring:

```python
from pydantic import BaseModel
from dataclasses import dataclass

class BlockEnvelope(BaseModel):
    """
    Represents the signed envelope of a CAS block.
    @spec SPEC-CAS-001 [AC-02]
    """
    digest: str
    signature: str
```

---

## 5. Dimension 4: API Interfaces & MCP Tools

Default discovery paths: `src/`.

### A. FastAPI / Starlette / Flask Routes (`src/routes.py`)

```python
from fastapi import APIRouter

router = APIRouter()

@router.post("/v1/cas/write")
def write_blob(payload: dict) -> dict:
    """
    Write a blob into CAS and return its digest.
    @spec SPEC-CAS-001 [AC-01, AC-02]
    """
    return {"digest": "sha256:..."}
```

### B. MCP (Model Context Protocol) Tools for AI Agents (`src/agent_tools.py`)

```python
@mcp.tool()
def cas_fetch_chunk(digest: str) -> bytes:
    """
    Retrieve an immutable chunk from CAS by its digest.
    @spec SPEC-CAS-001 [AC-02]
    """
    ...
```

---

## 6. Dimension 5: Source Code and Verification Tests

### A. Python Source Code (`src/cas_store.py`)

```python
class CASStore:
    def begin_immediate(self) -> None:
        """
        Acquire exclusive write lock.
        @spec SPEC-CAS-001 [AC-01]
        """
        ...
```

### B. Pytest Test Suites (`tests/test_cas.py`)

```python
import pytest

@pytest.mark.verifies("SPEC-CAS-001", "AC-01", "AC-02")
def test_cas_atomic_write_and_digest():
    """Validate atomic write and immutable digest computation."""
    ...
```

---

## 7. CLI Command Reference

```bash
# 1. Comprehensive health diagnostic and contract counts
specgraph doctor

# 2. View the complete Causal Matrix in table or JSON format
specgraph trace --format table
specgraph trace --format json

# 3. Filter matrix view by contract type
specgraph trace --kind adrs
specgraph trace --kind schemas
specgraph trace --kind apis
specgraph trace --kind specs

# 4. Strict drift check (for CI/CD and pre-commit hooks)
specgraph drift-check --strict

# 5. Generate token-efficient Context Envelope for AI Agents
specgraph context SPEC-CAS-001
```

---

## 8. Configuration File (`specgraph.yaml`)

```yaml
schema_version: "1.0"
project_name: "tare.tools.kernel"
governed_paths:
  - "src"
spec_paths:
  - "specs"
  - "docs/specs"
test_paths:
  - "tests"
schema_paths:
  - "src"
  - "schemas"
  - "sql"
  - "docs/schemas"
api_paths:
  - "src"
adr_paths:
  - "docs/adr"
  - "adrs"
  - "rfcs"
  - "docs/decisions"
excluded_paths:
  - "__pycache__"
  - ".git"
  - ".pytest_cache"
  - "fixtures"
  - "scratch"
  - ".system_generated"
strict_orphan_check: true
```
