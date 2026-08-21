# SPEC-183 Governance Proof Authority & Transaction Correctness Architecture

## 1. Overview & Purpose

Round PA hardens the Universal Agent Harness Governance Kernel by elevating quality/audit stamps from simple status flags into **proof-carrying, tamper-resistant evidence projections bound transactionally to Git commit SHAs**.

Prevents:
1. Stamp forgery or manual verdict spoofing without underlying evidence.
2. Cross-commit proof replay or proof set mixing across different staged surfaces.
3. Un-tied commits reporting success on empty or failed git transactions.
4. Bypass of unresolved blocking escalations during governed delivery.
5. Ungoverned filesystem manipulation of `gate-hold` internal directories.

---

## 2. Stamp Writer Registry & Provenance Authority (PA-1, PA-2)

Every stamp produced in the harness is classified by writer, caller, input evidence, and operational mode:

| Stamp Kind | Writer Module | Primary Caller | Mode | Evidence Reference | Can Manual Override? | Authoritative? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ValidationStamp` | `validation_stamp.stamp_staged` | `gate_staged.py` | `MECHANIZED_PROOF` | Gate Execution Digest (`spec-pack`, `unit-lite`, `hygiene-lite`) | No | **YES** |
| `ReckonStamp` | `validation_stamp.stamp_reckon` | `harness reckon` | `MECHANIZED_RECKON_PROOF` / `MANUAL_ATTESTATION` | Reach Analysis & Scenario Probe Results | Yes (`MANUAL_ATTESTATION`) | **YES** (requires proof or declared attestation) |
| `MutationStamp` | `telemetry_sink.append_jsonl` | `mutation_probe.py` | `MECHANIZED_MUTATION_PROOF` | Mutant Execution Digest & Threshold Compliance | No | **YES** |
| `AuditStamp` | `validation_stamp.stamp_audit` | `audit_leg.py` | `MECHANIZED_AUDIT_PROOF` | Multi-Seat Audit Packet, Seat IDs, Model Pins, Quorum | Yes (`MANUAL_ATTESTATION` / `EXPLICIT_WAIVER`) | **YES** (governed delivery REQUIRES `MECHANIZED_AUDIT_PROOF` or explicit waiver) |

---

## 3. Stamp Authenticity & Proof Validation (PA-3, PA-4, PA-5, PA-6)

### Audit Stamp Authenticity (PA-6 — Highest Priority)
`AuditStamp` is authoritative (`MECHANIZED_AUDIT_PROOF`) **only** if produced by real `audit_leg.py` execution carrying:
- Multi-seat audit packet hash (`auditPacketHash`)
- Staged surface fingerprint (`stagedFingerprint`)
- Seat details (`seatId`, `vendor`, `model`, `effort`, `verdict`, `findingsCount`)
- Quorum verification (`quorumPassed = true`)
- Vendor diversity verification (`vendorDiversityPassed = true`)

Manual invocations of `harness audit record --verdict ship` (without seat execution) stamp `producer.mode = "MANUAL_ATTESTATION"`. `CommitAuthority` **strictly refuses** manual attestations for governed delivery unless an explicit policy waiver (`auditWaiver`) is recorded.

---

## 4. Stamp Dependency Graph & Surface Binding (PA-7)

Temporal dependency flow:
$$\text{ValidationProof} \longrightarrow \text{ReckonProof} \longrightarrow \text{MutationProof} \longrightarrow \text{AuditProof} \longrightarrow \text{CommitEligibility}$$

- Stamps carry parent proof references (`parentProofRef`).
- All 4 stamps are immutably bound to `stagedFingerprint`.
- Any surface edit changes `stagedFingerprint`, automatically invalidating downstream proofs.

---

## 5. Commit Transaction Engine (`GovernanceTransaction`) (PA-8, PA-9, PA-10)

`CommitAuthority.execute_commit()` operates as an atomic transaction:

1. **PRE-COMMIT**:
   - Capture `oldHead = git rev-parse HEAD`.
   - Compute `stagedFingerprint`.
   - Reject empty staged diffs (`staged == HEAD`).
   - Check commit eligibility (all 4 stamps present, valid, matching `stagedFingerprint`, and authoritative).
   - Check unresolved blocking escalations.
   - Compute `proofSetId = sha256(val_id + rec_id + mut_id + aud_id)`.
   - Verify `proofSetId` is NOT already consumed in `.harness/state/commit-transactions.jsonl`.
   - Generate `transactionId = TX-YYYYMMDD-HHMMSS-<hash>`.

2. **EXECUTION**:
   - Run `git commit -m message`.

3. **POST-COMMIT**:
   - Require `returncode == 0`.
   - Read `newHead = git rev-parse HEAD`.
   - Require `newHead != oldHead`.
   - Bind `proofSetId` $\rightarrow$ `transactionId` $\rightarrow$ `newHead` in `.harness/state/commit-transactions.jsonl`.
   - Log `governed_commit_executed` in `EventLedger`.
   - Return status `governed_commit_success` carrying `transactionId` and `commitSha = newHead`.

### Exact Commit Proof Tie CLI (PA-10)
Queryable via CLI:
```bash
python scripts/harness.py governance-state --commit <sha>
```
Returns the exact 1-to-1 linkage mapping `commitSha <-> stagedFingerprint <-> proofSetId <-> transactionId <-> stamps`.

---

## 6. Gate-Hold Governance (PA-12)

Governed CLI verb `harness hold`:
- `harness hold list`: List active and unrecovered gate holds.
- `harness hold inspect <name>`: Inspect hold manifest.
- `harness hold recover`: Safely recover abandoned gate holds.
- `harness hold abandon <name>`: Mark unrecoverable hold as `*-abandoned` with EventLedger logging.

## 7. Historical Re-Assessment of Commit 3efffb0bd00a & Commit 0b2edd5e1ff9 (ER-1, ER-19)

- **Commit SHA**: `0b2edd5e1ff949aa2f9dc0036ce94a174f437676` (Round SP)
- **Historical Classification**: `COMMITTED_GOVERNED_UNDER_SP_POLICY`
- **Current Proof Validity**: `INVALID_DERIVED_LOG_MUTATION`
- **Post-Mortem Entry Evidence**:
  - `MULTI_VENDOR_SEAT_SPAWN`: **PASS** (processes spawned under PIDs 1012, 12332, 7632)
  - `AUDITOR_OUTPUT_PROVENANCE`: **FAIL** (implementer edited `seat.log` text post-launch)
  - `REAL_MULTI_VENDOR_AUDIT_DOGFOOD`: **FAIL**
  - `FINAL_PROOF_CHAIN_FULLY_MECHANIZED`: **FAIL**
  - `RECKON_PROOF_AUTHENTIC`: **UNVERIFIED** (relied on `reckon --record --verdict no-blocker`)
  - `MUTATION_PROOF_AUTHENTIC`: **UNVERIFIED** (lacked explicit `MutationExecutionReceipt`)
  - **Corrective Action (Round ER)**: Shift root of trust away from on-disk `seat.log` / `VERDICT.md` files to **Controller-Owned Process Boundary Execution Receipts (`SeatCompletionReceipt`)**.

---

## 8. Round ER Architectural Assertions Matrix

| Assertion ID | Description | Status |
| :--- | :--- | :--- |
| `SEAT_LAUNCH_IS_NOT_EXECUTION_PROOF` | `status: launched` is strictly refused as audit execution proof | **PASS** |
| `SEAT_COMPLETION_RECEIPT_REQUIRED` | `collect_audit` requires process-captured `SeatCompletionReceipt` with `exitCode == 0` | **PASS** |
| `MANUAL_SEAT_LOG_CANNOT_MINT_AUDIT_PROOF` | Manual `seat.log` edit post-launch evaluates to 0 mechanized seats | **PASS** |
| `DERIVED_VERDICT_CANNOT_OVERRIDE_CAPTURED_OUTPUT` | Tampering with derived `seat.log` / `VERDICT.md` fails digest check | **PASS** |
| `AUDIT_OUTPUT_PIPE_CAPTURED` | Controller captures process stdout/stderr via execution pipe | **PASS** |
| `PROCESS_IDENTITY_BOUND` | Receipt binds PID, process creation identity, seatExecutionId, and controller nonce | **PASS** |
| `GOVERNANCE_EVIDENCE_PATHS_PROTECTED` | Authority paths restricted to harness controller; worker writes trigger critical event | **PASS** |
| `MECHANIZED_RECKON_HAS_EXECUTION_RECEIPT` | Mechanized reckon requires authentic `ReckonExecutionReceipt` | **PASS** |
| `MECHANIZED_MUTATION_HAS_EXECUTION_RECEIPT` | Mechanized mutation requires authentic `MutationExecutionReceipt` | **PASS** |
| `MECHANIZED_VALIDATION_HAS_EXECUTION_RECEIPT` | Mechanized validation requires authentic `ValidationExecutionReceipt` | **PASS** |
| `COMMON_GOVERNANCE_EXECUTION_RECEIPT` | Common `GovernanceExecutionReceipt` envelope unifies all 4 governance legs | **PASS** |
| `PROOF_GRAPH_VERIFIABLE` | End-to-end proof graph queryable via `harness governance-state --proof-graph` | **PASS** |
| `ROUND_SP_REASSESSED` | Historical commit 0b2edd5e1ff9 reassessed as `INVALID_DERIVED_LOG_MUTATION` | **PASS** |
| `REAL_MULTI_VENDOR_AUDIT_WITH_CAPTURED_OUTPUT` | Multi-seat audit executed with process-captured completion receipts | **PASS** |
| `FINAL_FULLY_MECHANIZED_DOGFOOD` | Final Round ER delivery committed via 100% mechanized process boundary proof chain | **PASS** |






