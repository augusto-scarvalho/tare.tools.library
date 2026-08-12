# Information Survival & Reconstructable Assurance — technical proposal

**Status:** PROPOSED.

## Objective

Define information homes and reconstructability without inventing Git/DB/artifact-store semantics into the kernel.

## Candidate views/contracts

Information classification/appraisal, reconstruction recipe/input manifest, artifact/evidence locator, retention/disposition metadata, evidence recall query and reconstructability qualification. Reuse existing canonical identifiers wherever possible.

## Golden properties

- irreversible governance/effect/evidence facts survive required retention;
- derived projections can be deleted and rebuilt;
- reconstructing a Project revision does not rely on hidden HOME/transcript state;
- retention/privacy deletion is explicit and does not silently falsify historical claims;
- external artifact/store identity is pinned without making its path the canonical object identity.

## BDD / Torture Lab

Clean-seed reconstruction; missing artifact; stale projection; hidden environment dependency; timezone/path variance; revoked source; intentionally scrubbed sensitive evidence; attestation signer loss; old/new runtime reconstruction.

## Migration

Start by inventorying current homes and classifying irreversibility; build read-only reconstruction checks; shadow content policy; only enforce moves/deletion after recovery has been proven.
