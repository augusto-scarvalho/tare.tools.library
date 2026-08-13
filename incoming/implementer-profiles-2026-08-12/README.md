# Submission packet — bounded implementer profiles

**Status:** `DRAFT SUBMISSION / RESEARCH`  
**Document ID:** `implementer-profiles-longitudinal-2026-08-13`  
**Freeze point:** independent settlement of `CI-REGRESSION-01` / Issue #17 plus ACK/PLAN-only observation from active Issue #23  
**Canonical tare.tools incumbent reference:** `477bea0d915dfde5e9e92fce68be0a42154a31f9`

This directory is a **submission packet** under the current `tare.tools.research` publisher workflow. It is evidence staging, not a publication destination and not architecture authority.

Read in this order:

1. `PUBLISH_MANIFEST.json` — exact publisher entry point and artifact inventory.
2. `document-metadata.json` — schema-valid identity, lineage and canonical reference.
3. `study.md` — longitudinal research synthesis and current claim ceiling.
4. `evidence-annex.md` — auditable task → treatment → behavior → result → audit → classification chain.
5. `peer-review-protocol.md` — independent review, validity argument, replication and falsification protocol.
6. `provenance.md` — source availability, exact Git identities, Drive digests and verification limits.

## Editorial change from the earlier draft

The earlier packet was shaped as one `EXPERIMENTAL` Q7-era publication with four PT/EN HTML renders plus a corrective supplement. That representation became stale after Q8 and subsequent audited trains. This revision deliberately:

- classifies the **longitudinal synthesis** as `RESEARCH`, while preserving individual implementation episodes as experimental/operational evidence;
- uses Markdown source-of-truth documents instead of stale pre-corrective HTML editions;
- removes the hard-coded publication destination — routing belongs to the publisher/validator;
- uses the exact-case `PUBLISH_MANIFEST.json` required by `CONTRIBUTING.md`;
- lists `document-metadata.json` as a publication artifact;
- materializes provenance and evidence limitations instead of treating digests as equivalent to source-byte availability;
- advances the empirical freeze point through the independent settlement of CI-REGRESSION-01;
- records CI-REGRESSION-02 only as an active ACK/PLAN observation: no outcome is inferred while it is still running.

The previous draft files remain recoverable in Git history; they are removed from the current submission rather than silently rewritten as if they had been current all along.

## Current claim ceiling

The strongest internal claim this packet supports is:

> **Claude Fable 5 low × Claude Code, under the observed tare.tools capsule/Authority/evidence regime, is `A2 / bounded DEV qualified` for packet decomposition, with a positive naturalistic transfer signal into Validation/Assurance; independent audit remains necessary because semantic/evidence edge defects and corrective burden continue to occur.**

This packet does **not** support:

- A3 qualification;
- global/default A2 across task classes/projects/runtimes;
- causal superiority over Sonnet/Opus;
- activation/promotion Authority;
- a global model leaderboard;
- autonomous protected effects.

## Publication boundary

Publication in `tare.tools.research` does not mint `CURRENT` or `TARGET`. Any canonical adoption still requires the normal Findings → ADR → SPEC → BDD → Implementation Packet → code/gates/evidence path in the canonical tare.tools repository.
