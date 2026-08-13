# Provenance inventory — bounded implementer profiles

**Status:** `RESEARCH / PROVENANCE`  
**Rule:** a locator or digest identifies evidence; it does not imply the source bytes are independently materialized in this packet.

## 1. Canonical/reference boundary

Stable tare.tools incumbent architecture reference for this edition:

`477bea0d915dfde5e9e92fce68be0a42154a31f9`

This is a reference baseline, not a claim that later DEV evidence has been promoted into CURRENT. Later implementation episodes are bound below to their exact branch/candidate identities.

## 2. Primary Fable operational evidence

| Episode | Primary locator | Exact subject / audit identity | Availability in this packet |
|---|---|---|---|
| Q6 / F5L-01 | tare.tools Issue #6 | candidate `8f4f5162a683f65345796384e5e557857e476475` | locator only; exact repo remains externally retrievable |
| Q6C / F5L-02 | Issue #7 | `bddcce338acc29f215fe58e90899738c1338957a` | locator only |
| Q6C2 / F5L-03 | Issue #8 | `2ad0e579cf272cccb54387c3d39b759ca35fc685` | locator only |
| Q6C3 / F5L-04 | Issue #9 | `34f1559299c5084c7f5ceb2aea72fae0b2475506` | locator only |
| Q6C4 / F5L-05 | Issue #10 | `185179b0a5691f3bd606f9226e15423d1e1ab2b5` | locator only |
| Q7 / F5L-06 | Issue #11 | final `b0dea202e29e418fc0de04db826c5917cd851ed9`, tree `710fd333c49b8b0cb61326484e10c3cfc43b895d` | locator + exact Git identity |
| Q8 / F5L-07 | Issue #12 | final `eb08cd6228596b3b3c97f841442b7a362a9e2aef`, tree `bc496cc3c353cb535f123e3cd1133f475bc8431b` | locator + exact Git identity |
| BASELINE-CI-01 | Issue #14 | accepted scoped repair lineage ending `8f0ab5a4f2d02ce840a473f8bd9a17ca6c9c5b8c` | locator + Git identity |
| BASELINE-CI-02 | Issue #15 | final corrective `46d97a17aa2c25acaa6a2fda1b6847ef6eec64ff` | locator + Git identity |
| CI-REGRESSION-01 | Issue #17 | functional `20100fa49424fda3e6ed41792d09faa3e45a9fbf`; final `8d040aac19ab7661b4c032d417b0b9fb76310372`; tree `7fcc86578e81b2b8af976eef4cc4142424da8f90`; final audit `AUDIT-CI-REGRESSION-01-003` | locator + exact Git/audit identity |
| CI-REGRESSION-02 | Issue #23 | source `8d040aac19ab7661b4c032d417b0b9fb76310372`; ACK/PLAN only at freeze | running evidence; no outcome materialized |

GitHub Issues are coordination/provenance surfaces, not canonical architecture authority. The operational repository and exact Git objects remain the primary subject evidence.

## 3. Q7 Drive evidence digests

Earlier independent audits recorded:

- original Q7 evidence manifest SHA-256: `6eb78e3bb55bbdc74d962b97b2654352f364793efb1b9ec603348608d24b7cce`;
- corrective Q7 evidence manifest SHA-256: `d1004b5d403b9e8e2e0a8e427dc801fb883436a9cf7c5a9a9513fe9f77f79eb6`.

The payloads were independently read back during the operational audit, but their exact bytes are **not copied into this submission packet**. Therefore the packet preserves identity/provenance, not independent offline reproduction of those Drive payloads.

## 4. Derived study lineage already materialized in tare.tools.research

This submission derives from the currently materialized research documents:

- `research/01_methodology-research-program/2026-08-13-bounded-implementer-profile-longitudinal-study.md`;
- `research/01_methodology-research-program/2026-08-13-implementer-observed-evidence-ledger.md`.

Those files are research artifacts, not canonical tare.tools architecture. This submission is a new dated publication packet and does not silently rewrite their historical Git versions.

## 5. Historical report/ledger artifacts not materialized here

Historical continuity records refer to:

- `tare_tools_implementer_profiles_empirical_report_v1.2_post_q7_final_audit_2026-08-12.md`;
- `tare_tools_implementer_observation_ledger_v1.2_post_q7_final_audit_2026-08-12.json`;
- earlier PT/EN implementer-profile integration-review and technical-delta editions.

These artifacts informed the longitudinal reconstruction but their exact bytes are not all part of this submission. The previous PR branch contained stale HTML copies; this revision removes them from the current artifact set instead of treating old derived renders as authoritative after later audits.

Where a claim depends on a more recent Issue/Git audit, the exact operational evidence listed in §2 supersedes the older summary as the load-bearing source.

## 6. External theoretical evidence

The study cites published work by DOI/title rather than vendoring copyrighted paper bytes. Core source identities are enumerated in `study.md`; the longer bibliographic tiering remains in the already-materialized theoretical study.

No external paper is used as normative tare.tools Authority. Literature supports constructs/hypotheses; current architecture remains owned by canonical tare.tools contracts.

## 7. Verification limitations

A reviewer should distinguish:

- **materialized in this packet:** current Markdown synthesis, evidence annex, peer-review protocol, metadata and this provenance inventory;
- **retrievable from GitHub:** operational Issues, commits, diffs and audit comments where permissions allow;
- **digest-bound but not copied here:** historical Drive evidence payloads;
- **historically referenced but not independently materialized here:** some earlier study bundles/ledgers;
- **bibliographic locator only:** external literature.

Consequently this submission supports an auditable research argument but is not a self-contained archival mirror of every underlying operational byte.
