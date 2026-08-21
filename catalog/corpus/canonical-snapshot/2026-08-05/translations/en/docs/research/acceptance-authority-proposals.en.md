# Proposal — the approval "badge" (acceptanceAuthority / chain of responsibility)

Deliverable for item #2 (owner: "make proposals or research them and show me so I can decide with you"). Basis: D013 (owner 2026-07-18) — authority depends on WHO accepted (`user | worker | overseer`), with self-consistency + standardization to follow the chain of responsibility + date. **You choose an option (or mix them) and I implement it.**

## What we already have in the repository (do not reinvent)
- **subject dimension** (`records.add_entry(subject=)`, `append_event(subject=)`): every record is already attributable to `self | target-name`. This is half of the "who".
- **C12 approval digest** (`plan_gate.planSha256`, `decision_inbox.apply_decision` `expected_digest`): approval can already BIND to an artifact SHA (TOCTOU closed).
- **T-HASHCHAIN** (recently shipped): critical events are already tamper-evident through a hash chain — an approval recorded through this path is already resistant to reordering.
- **decision_inbox / escalations**: already record `decidedAt`, `choice`, `note`.

What is missing: a consistent **actor type** + the CHAIN (`proposer → reviewer → accepter`), not just a loose name.

## Reference patterns (what the world does)
| pattern | idea | what we take from it |
|---|---|---|
| git author/committer/Signed-off-by | 3 roles in a change (who wrote it, who applied it, who attests it) | the idea of MULTIPLE roles in an event, not one name |
| W3C PROV (`wasAttributedTo`/`wasAssociatedWith`) | Agent × Activity × Entity with typed roles | actor + role + activity vocabulary |
| in-toto / SLSA provenance | signed link metadata: who performed which step, in order | ordered chain + signed binding (optional) |
| RBAC/ABAC + separation-of-duties | proposer ≠ approver; two-person control | article §7.7 R2/R3 already asks for this; the chain makes it executable |

## Proposal A — "simple badge" (single typed record) · SMALLEST
A typed field at the acceptance point:
```json
"acceptanceAuthority": {
  "actorType": "user | worker | overseer",
  "identity": "augusto | worker:aXXXX | overseer:session_01Y8...",
  "at": "2026-07-19T...",
  "method": "cli-decide | ui-approve | auto-owner-gate"
}
```
- Reuses subject + `decidedAt`. Additive. One helper `stamp_authority(actorType, identity, method)` called at acceptance points (decision inbox, owner gate, C2 risk acceptance).
- **Pros:** cheap, closes the essential part of D013. **Cons:** does not model the CHAIN (`proposer → approver`) — only the final accepter.

## Proposal B — "chain of responsibility" (ordered list of roles) · RECOMMENDED
Acceptance carries the CHAIN of participants, typed by role:
```json
"responsibilityChain": [
  {"role": "proposer", "actorType": "worker",   "identity": "worker:a78e...", "at": "..."},
  {"role": "reviewer", "actorType": "overseer",  "identity": "overseer:sess...", "at": "..."},
  {"role": "accepter", "actorType": "user",       "identity": "augusto",         "at": "..."}
]
```
- Makes the separation-of-duties rule in §7.7 EXECUTABLE: a deterministic check `proposer.identity != accepter.identity` (Rule of Two / two-person control).
- Each entry reuses subject/actorType. The C2 risk register (D013) records the entire chain as `acceptanceAuthority`. The C12 digest can bind to the chain SHA.
- **Pros:** fully answers "who decided what and when"; unlocks R2/R3; natural basis for N-SECREVIEWER (D014 — reviewer becomes a role in the chain).
- **Cons:** slightly more plumbing (recording the chain at multi-party points).

## Proposal C — "signed chain" (B + tamper evidence) · STRONGEST
Proposal B + integrity binding: `responsibilityChain` enters the T-HASHCHAIN hash chain (as a critical event) OR gets a `chainDigest = sha256(canonical chain)` in the C12 style.
- **Pros:** the chain of responsibility becomes tamper-evident — nobody can rewrite "who approved" without breaking evidence. Closes §7.1 o3 (`candidate_proposed → never the same identity approves`) in a verifiable way.
- **Cons:** the T-HASHCHAIN ceiling (no real signature) applies here as well; real signatures stay behind the key-infrastructure trigger.

## My recommendation (architect)
**Proposal B now, with the hook for C ready.** The chain is what D013 actually asks for ("understand the chain of responsibility") and it unlocks executable separation-of-duties + the security-reviewer role (D014) almost for free. The signed binding (C) is an additive `chainDigest` we can connect when/if the integrity trigger arrives — reserving the field costs nothing. Proposal A is the fallback if you want the absolute minimum.

**Where it enters the code (if B):**
- New `harness_lib/responsibility.py`: typed record + `stamp(role, actorType, identity)` + `verify_separation(chain)` (`proposer ≠ accepter`, deterministic).
- Acceptance points: `decision_inbox.apply_decision`, owner gates, C2 risk register (`acceptanceAuthority` = the chain).
- Spec: NEW SPEC-116 door (responsibility-chain) + Gherkin.
- Scenario: valid chain records successfully; `proposer == accepter` → separation FAIL (advisory).

## Questions for you to close
1. **A, B, or C?** (I recommend B with the C hook.)
2. Should `actorType` be exactly `user | worker | overseer`, or do you want a 4th type (e.g. `automation` for auto-owner-gate, `external` for an outside human)?
3. User `identity` = your handle (`augusto`)? worker = agentId? overseer = session ref? (proposal: yes to all three.)
