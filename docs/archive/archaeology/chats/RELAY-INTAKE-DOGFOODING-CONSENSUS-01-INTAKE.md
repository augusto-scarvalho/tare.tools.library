# RELAY-INTAKE-DOGFOODING-CONSENSUS-01 — Asynchronous Human Intake Queue & Multi-Agent Consensus Dogfooding

## 🎯 Executive Goal & North Star
Establish a zero-touch, file-based asynchronous intake mechanism for the Human Operator and a collaborative dogfooding & consensus protocol for all swarm agents (`codex_planner`, `claude_fable_acer`, `antigravity`, `bookkeeper`), eliminating manual chat typing and intermediary toil.

---

## 🏛️ Architecture & Capabilities

### 1. Asynchronous Human Intake Queue (`relay/intake/human/` or `relay/intake/*.md`)
- **Operator Workflow:** The operator simply drops any unstructured demand, bug report, audio transcript, or feature specification as a Markdown (`.md`) or JSON (`.json`) file into the Google Drive intake directory.
- **Automated Ingestion:** The supervisor/intake worker parses the demand, extracts title, summary, priority, and exit criteria, executes `graph_ops.py intake` to register it into `work-graph.json`, and routes it directly to the backlog without requiring chat interaction.
- **Status & Receipts:** The file is moved to `relay/intake/processed/` with a generated receipt referencing the created task ID.

### 2. Multi-Agent Swarm Dogfooding & Friction Log (`relay/intake/dogfooding/`)
- **Friction Logging:** Any agent executing in the field (`claude_fable_acer` implementing, `codex_planner` planning, `antigravity` auditing) can emit a structured friction observation (e.g. protocol ambiguities, tooling papercuts, missing test utilities).
- **Consensus & Joint Refinement Protocol:**
  - When an architectural change or protocol fix is proposed, it is broadcast to the peer inboxes (`relay/inbox/*`).
  - Agents respond asynchronously with typed votes (`AGREE`, `OBJECTION`, `AMENDMENT`).
  - Upon reaching consensus (or auditor arbitration), the Planner synthesizes the agreed resolution into a canonical backlog task or protocol update.

---

## 📋 Contractual Definitions of Done (`exit_criteria`)
- [ ] `relay/intake/` directory structure created with `human/`, `dogfooding/`, `processed/`, and `quarantine/`.
- [ ] `relay/intake_processor.py` service that ingests human files, maps them to `work-graph.json` nodes via `graph_ops intake`, and notifies the Planner.
- [ ] `relay/consensus_engine.py` (or `relay/dogfooding.py`) supporting friction logging, multi-agent proposal broadcasting, and typed consensus collection.
- [ ] Supervisor integration in `watcher_daemon.py` to monitor intake directories at the 15s polling floor.
- [ ] Comprehensive test suite in `tests/test_relay_intake_and_consensus.py` covering malformed intakes, consensus quorums, objection resolution, and idempotent ingestion.
- [ ] Zero-touch human UX verified: creating a file in `relay/intake/` results in an unblocked task planned by Codex without user typing.
