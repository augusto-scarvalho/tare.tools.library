# ADR-067: New canonical repository taxonomy, removal of ghost folders and a controlled historical archive (`docs/archive/`)

## Status
**RATIFIED / RATIFIED_BY_TRIPARTITE_GOVERNANCE** (approved through `CASE-2026-08-21-RFC-008-CANONICAL-REPOSITORY-TAXONOMY-AND-GHOST-PURGE`)

## Ratification date
2026-08-21

## Deliberation quorum
- **Quorum mode:** `FRONTIER_UNANIMOUS`
- **Participating seats:**
  - Google (`gemini-3.7-flash` via `agy.EXE`)
  - OpenAI (`gpt-5.6-sol` via `codex.exe`)
  - Anthropic (`claude-fable-5-high` via `claude.exe`)
  - User and independent mediator (interactive deliberation)

---

## 1. Context and diagnosis
The `tare.tools.library` repository had built up serious layout debt because of the old defensive directive not to
change existing directories. That rigidity left dozens of folders holding only `.gitkeep`, 20 numbered research
folders with empty placeholders and duplicated staging structures.

---

## 2. Architectural decision: new canonical taxonomy

### 2.1 Approved canonical structure
The repository unifies its tree under these top-level directories:
```
tare.tools.library/
├── cases/              # Private, ignored local custody; references in docs/RECORDS_ARCHIVE.json
├── catalog/            # Master catalog, capability registries and ontology
├── docs/               # Active canonical documentation
│   ├── adr/            # ADRs 001 to 067
│   ├── architecture/   # Engineering doctrine and topology diagrams
│   ├── assurance/      # Formal validation protocols (CMRP)
│   ├── guides/         # Manuals and self-healing guides for users
│   ├── research/       # Consolidated engineering studies
│   └── archive/        # Controlled catch-all category (discontinued reference history)
├── frontier/           # Epistemic frontier pointers and advancement decisions
├── schemas/            # Canonical JSON schemas
├── specs/              # Formal SDD specifications in EARS format
├── templates/          # Canonical publication templates
├── tools/              # Runtime engines (Mesh, BYOC Router, Lean MCP, Indexer)
└── tests/              # Automated test suite and CI falsifiers
```

### 2.2 Establishing `docs/archive/` (controlled catch-all category)
- Meant for consolidated snapshots of past transitions (`refresh-editions/`), formally archived staging artifacts
  (`incoming/`) and discontinued reference studies.
- **Frugality invariant:** `docs/archive/` must never be used as a store for chat transcripts, raw log dumps or
  confidential notes (those belong only in the Sovereign Vault on the operator-configured node).

### 2.3 Ghost folder purge
- Every `.gitkeep` file and empty subfolder in `sources/`, `proposals/`, `research/00..19/` and `experiments/` was
  removed permanently.

---

## 3. Consequences
- A tidy, predictable repository without ghost artifacts.
- Clean, direct traceability for developers, autonomous agents and end users.
- 100% of the test suite (157 tests) adapted to the new canonical paths.

## Note (2026-11-03)
Section 2.2 is superseded: obsolete history is now deleted instead of archived, and `docs/archive/` was removed
together with the epistemic frontier (`catalog/frontier/`). See the 2026-11-03 amendment of
[ADR-069](ADR-069_FEDERATED_DOCUMENT_OWNERSHIP_AND_BOUNDED_INDEXING.md). The tree that is current is described in
the README.
