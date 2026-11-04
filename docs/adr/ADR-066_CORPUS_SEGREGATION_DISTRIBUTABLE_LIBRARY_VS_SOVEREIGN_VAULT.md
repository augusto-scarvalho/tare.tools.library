# ADR-066: Architectural segregation of the knowledge collection: distributable substrate (tare.tools.library) vs. private Sovereign Vault

## Status
**RATIFIED / RATIFIED_BY_TRIPARTITE_GOVERNANCE** (approved through `CASE-2026-08-21-RFC-007-CORPUS-SEGREGATION-DISTRIBUTABLE-LIBRARY-VS-SOVEREIGN-VAULT`)

## Ratification date
2026-08-21

## Deliberation quorum
- **Quorum mode:** `FRONTIER_UNANIMOUS`
- **Participating seats:**
  - Google (`gemini-3.7-flash` via `agy.EXE`)
  - OpenAI (`gpt-5.6-sol` via `codex.exe`)
  - Anthropic (`claude-fable-5-high` via `claude.exe`)
  - Independent mediator (autonomous dialectical synthesis)

---

## 1. Context and diagnosis
The `tare.tools.library` repository had accumulated artifacts of conflicting kinds: on one side, the canonical
software substrate, SDD specifications and runtime tools that end users need; on the other, raw AI chat
transcripts, heavy benchmarking logs and proprietary formulations. That overlap carried a risk of intellectual
property leaks, hypertrophy and RAG pollution.

---

## 2. Architectural decision: the two-layer doctrine

### 2.1 Layer 1: distributable substrate (`tare.tools.library` on GitHub)
The Git-tracked repository contains strictly the runtime package:
1. **`docs/` and `docs/adr/`:** architectural decisions (ADRs 001-066), engineering doctrine and manuals.
2. **`specs/`:** formal SDD specifications in EARS format for mechanical conformance and self-healing.
3. **`tools/`:** runtime engines (`mesh/`, `governance/`, `policy/`, `discovery/`, `inference/`, `indexer/`).
4. **`catalog/`:** curated master catalog of capabilities and indexes.
5. **Maximum repository budget:** kept under a strict ceiling (< 50 MB tracked in total).

### 2.2 Layer 2: Sovereign Vault and cold storage (`tare.tools.vault` / operator-configured node)
Private, cryptographically verified storage on the operator-configured node (`<operator-vault>/corpus_archive/`
with `MANIFEST.sha256`):
1. **`archaeology/chats/`:** conversation history, raw mining and prompts from past sessions.
2. **Proprietary studies and secret sauce:** confidential formulations and business strategies.
3. **Extensive benchmarking logs:** heavy stress-test dumps.

### 2.3 Executable enforcement mechanisms
1. **Quarantine through `.gitignore`:** permanently ignores `archaeology/chats/`, `experiments/`, `vault/`,
   `_handoff/` and scraping artifacts.
2. **Continuous falsifiers in CI (`tests/test_frugality_guard.py`):**
   - `test_repo_tracked_size_budget`: checks the < 50 MB ceiling.
   - `test_no_raw_chat_dumps_tracked`: fails immediately if any chat dump or transcript is tracked in Git.
   - `test_gitignore_quarantines_archaeology_and_experiments`: checks that the quarantine rules are present.

---

## 3. Consequences
- A repository free of secrets, drafts and chat transcripts.
- The end user's RAG stays clean and focused strictly on runtime value and canonical specifications.
- Full preservation of the project history in the Sovereign Vault on the operator-configured node.

## Note (2026-11-03)
The ADRs listed in 2.1 now live with their owners (ADR-069); this repository keeps only ADR-058, ADR-066,
ADR-067 and ADR-069. The imported chat transcripts that remained under `catalog/corpus/` were deleted, which
completes the separation this decision asked for. The test
`test_gitignore_quarantines_archaeology_and_experiments` no longer exists; the `.gitignore` rules and the other two
tests remain.
