# SPEC-164 — Event hash-chain: production verification + compaction seal (SECREV M4+M5)

Status: SPEC-164 **v2** (C+ + durable self-chain), proposed 2026-07-21 (acceptance:
`testing/scenarios/thc_hash_chain.py` + `rh_repo_health.py` extensions). Origin:
/security-review M4+M5, owner-ratified D043; v2 = the 3-round Double-Diamond
consolidation (`docs/research/event-log-integrity-under-compaction.md`, owner-ratified
B2 2026-07-21) that REPLACED the round-1 `allow_gaps` (found to be a regression: it
tolerated EVERY gap, surrendering reorder/removal detection). relates-to: T-HASHCHAIN,
SPEC-109 (compaction), SPEC-161 (typed actor), observability-and-operability.md.

## Goal

The event hash-chain (`append_event` writes tamper-evidence on critical rows;
`verify_event_chain` checks it) is written but **never verified in production** — its
only callers are two scenarios (M4). And `compact_supervision_events` folds critical
events into the durable `escalations.json` WITHOUT any hash, and strips them from the
live log, so the durable record inherits no tamper-evidence and the strip breaks the
live chain (M5). A witness that never runs catches nothing, and the durable record of
owner security decisions has no integrity at all. This closes both, as one coherent
pair (they are coupled: compaction legitimately breaks the live chain, so verification
must anchor to what compaction seals).

## Applicability

`scripts/harness.py` (`verify_event_chain` takes a `seal` instead of `allow_gaps`),
`escalations_lib.py` (`compact_supervision_events` writes a C+ `chainSeal` + a durable
self-chain + a cross-witness row; `verify_durable_ledger` helper), `repo_health.py`
(`checks` gains `event-chain-integrity` + `durable-ledger-integrity`). Additive; nothing
enforces (the doctor is WARN-only).

## Requirements / invariants (numbered, testable)

1. **C+ seal on compaction (M5, v2).** When `compact_supervision_events` strips critical
   rows carrying a `hash`, it records a `chainSeal` in `escalations.json`:
   `{lastHash, sealedAt, count, removed}` where `removed` is the C+ binding map
   `{removed_hash: successor_hash}` — for each KEPT hashed row whose `prevHash` points at
   a stripped hash, the stripped hash maps to that kept row's own hash. `lastHash`/`count`
   pin the removed segment for durable evidence; `removed` is what makes gap-tolerance
   SAFE (invariant 2). Additive: a compaction that removes no hashed row leaves any prior
   seal untouched.
2. **C+ gap-tolerant live verification (M4, v2 — replaces `allow_gaps`).** Compaction
   removes SCATTERED critical rows while KEEPING others, so the live chain has REAL gaps.
   `verify_event_chain(events, seal=seal)` flags a content edit (`hash != _chain_hash`)
   AND an UNEXPLAINED gap: a `prevHash` mismatch is tolerated ONLY when
   `seal.removed[prevHash] == row.hash` (the seal binds the removed hash this row links
   across to THIS row as its successor). This RESTORES the reorder/removal + forge-by-
   citation detection that the abandoned `allow_gaps=True` had surrendered (it tolerated
   EVERY mismatch). `seal=None` → strict walk (the thc-1a..1d callers); `genesis` param
   unchanged (back-compat).
3. **Durable self-chain (L1, v2).** `compact_supervision_events` writes `prevStateHash`
   (the previous ledger's `stateHash`, or genesis) and `stateHash` = sha256 over the
   canonical doc EXCLUDING `stateHash`. `verify_durable_ledger(doc)` recomputes and
   compares. The durable side only ever APPENDS (no strip), so it has NO gap problem —
   the compaction-gap headache is purely a live-log concern. A silent content edit of a
   past ratified decision leaves `stateHash` stale → caught.
4. **Cross-witness live↔durable (anti-rollback, v2).** After writing the ledger,
   compaction appends a NON-critical `supervision_compacted` row to the live log carrying
   `durableStateHash`. A careless WHOLE-FILE rollback of the ledger to an older valid
   snapshot has a `stateHash` the live witness won't match → caught. Bounded window: the
   live log is transient (gate-wiped), so after a wipe the witness is gone — declared,
   not hidden.
5. **Production verification (M4, v2).** `repo_health.checks` gains TWO advisory
   (WARN-only) checks: `event-chain-integrity` (reads the live log + the seal from the
   ledger, runs `verify_event_chain(seal=…)`, WARN on a content edit OR an unexplained
   gap) and `durable-ledger-integrity` (WARN on a `verify_durable_ledger` mismatch, else
   cross-witnesses against the live log's last `supervision_compacted`). The
   tamper-evidence now COMPARECE at every `harness.py doctor`.
6. **Honest ceiling.** Referential integrity (equality-of-hashes), not signed: an
   attacker who rewrites the live log AND the seal-carrying ledger (both class-B state)
   can still forge — the T-HASHCHAIN no-key ceiling stands. v2 raises the realistic bar
   MEANINGFULLY over round-1: a prompt-injection-shaped drift (the round-3 T2, driven by
   tool output not harness source) does NOT know to recompute the C+ seal + durable chain
   + witness in concert → leaves a break the doctor catches. Careful/source-aware drift
   (and any T3) still forges; that closes only with an out-of-band-keyed signature (L6,
   owner-gated) or an external witness (git/OTS, deferred). Declared, not hidden.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| C+ over allow_gaps | 3-round Double-Diamond consolidation: allow_gaps was a REGRESSION (silences the only alarm for row-stripping); C+ binds each tolerated gap to its successor, restoring detection at ~zero cost |
| durable self-chain is the real gap | escalations.json (owner's ratified decisions) survives gates and had ZERO integrity; the durable side only appends, so no gap problem — unanimous across 15 ideators |
| cross-witness is bounded | live log is transient; catches careless rollback within a session, declared honest for after-wipe |
| doctor (WARN-only), not a gate | measure-before-enforce; advisory follow-up |
| no MMR/blockchain/forward-MAC | over-engineering without a key/witness (round 2, 9/9); real signing rides the L6 owner-key trigger |

## Test strategy

- `thc_hash_chain.py`: (thc-2a) compaction writes a C+ `chainSeal` with correct
  `lastHash`/`count` AND the `removed` successor-binding, and the ledger self-chains
  (`stateHash` present + `verify_durable_ledger` true); (thc-2b) `verify_event_chain(seal
  =seal)` ok across the bound gap, content edit → WARN/brokenAt; (thc-2c) KEEP-then-FOLD
  end-to-end through `repo_health.checks` stays ok before AND after compaction;
  (thc-2d, the C+ WIN) a forge-by-citation row citing a removed hash it isn't bound to →
  BREAK (what allow_gaps waved through).
- `rh_repo_health.py`: the 12-check registry includes `durable-ledger-integrity`;
  rh-chain exercises intact/tamper/sealed via `repo_health.checks`.
- Regression: `thc-1a..1d` (strict, `seal=None`) green; `di_decision_inbox`,
  `se_self_review`, `es_subject_scope`, `rt_route_dispatcher` (compaction consumers) green.

## Operational policy (B5 — ledger durability hygiene)

The durable ledger (`.harness/state/escalations.json`) must stay OUT of ambient
backup/sync surfaces, for two reasons the round-3 panel named: (a) a synced/backed-up
copy is a ROLLBACK vector (restore an older valid ledger over the hardened one), and (b)
it is a CONFIDENTIALITY surface (the owner's ratified security decisions). Coverage,
mostly by EXISTING machinery (verified 2026-07-21 — B3/B5 are largely already covered):
- **Sync leak:** the `onedrive-path` doctor check already WARNs when the repo (hence the
  ledger) sits under a OneDrive-synced folder; `.gitignore` keeps it untracked.
- **Rollback within a session:** the cross-witness (invariant 4) catches a careless
  whole-file rollback while the live log still holds the witness.
- **T1 worker reach (B3/L2):** ALREADY COMPLETE without new ACLs — `.harness/state` is
  excluded from worker workspace copies (`workflow_runtime_ignore`), is not lockable so a
  worker-created ledger is never merged back (`workflow_merge_plan` merges only
  declared-locked paths), and is egress-denied (`discovery`). Adding escalations.json to
  the STATIC `protected_files` snapshot registry would be WRONG (it changes every
  compaction) and redundant. The env-override→nonce hardening the panel proposed applies
  to the protected-INSTRUCTION-files path (AGENTS.md etc.), a separate security-sensitive
  change that rides its own focused follow-up + reckon, not this spec.

## Validation

- `python testing/scenarios/thc_hash_chain.py` green.
- `python testing/scenarios/rh_repo_health.py` green (both doctor checks).
- `spec-pack` green.
