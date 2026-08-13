# Contributing Research Publications

This repository is a research publisher: it preserves evidence and editorial
editions; it does not grant `CURRENT` or `TARGET` architectural authority.
Read [DOCUMENT_POLICY.md](DOCUMENT_POLICY.md) and
[PROMOTION_POLICY.md](PROMOTION_POLICY.md) first. This guide defines the PR
process around those policies; it does not replace them.

## Publication lifecycle

```text
Submission PR (draft packet in incoming/)
  -> editorial decision: accept | revise | reject | park
  -> accepted packet is retained in incoming/ on main
  -> Publication PR (router output from a pinned main base)
  -> integrity and catalogue checks
  -> merge as research publication
```

A rejected or parked submission is closed without a merge. Merging an accepted
submission retains evidence for publication; it is not an architectural
ratification. A separate Promotion Packet and the canonical `tare-tools`
process remain required for a `TARGET`, `CURRENT`, ADR, SPEC, BDD, or
implementation packet.

## 1. Submission PR

Open a **draft** PR containing one packet at
`incoming/<document-id>/`. Its required entry point is exactly
`PUBLISH_MANIFEST.json` (upper case). The packet must contain:

- `PUBLISH_MANIFEST.json`, valid under the publisher policy, listing every
  artifact that publication will copy;
- `document-metadata.json`, conforming to
  [`schemas/document.schema.json`](schemas/document.schema.json), and listed
  as an artifact;
- a canonical HTML primary artifact following
  [HTML_PUBLICATION_STANDARD.md](HTML_PUBLICATION_STANDARD.md), and, when applicable, its protocol,
  result ledger, audit, or source material;
- a provenance statement for every evidence item: original location, digest
  when known, availability, and whether its exact bytes were materialized;
- known lineage (`derived_from`, `supersedes`, or `superseded_by`) and bounded
  contexts;
- for substantial research, the canonical `tare-tools` commit and architecture
  epoch against which conclusions were produced.

For new packets use `packet_version: "1.1"`, declare `primary_artifact`, and
include `document-metadata.json`. `requested_channels: ["pages"]` requests a
Signal Pages projection; it is not approval. Only editorial review may set
`pages_approved: true` in the publication record.

Never overwrite an original in `corpus/original/`. Preserve historical
receipts, audits, and negative results; publish a new correction, delta, or
superseding record instead.

Hashes identify an unavailable source but do not make it independently
reproducible. State that limitation plainly. Do not claim local verification,
complete evidence, `CURRENT`, or `TARGET` unless the corresponding bytes or
canonical authority actually exist.

## 2. Editorial review

Reviewers classify the submission as `accept`, `revise`, `reject`, or `park`.
They check:

- authority and status are permitted in this repository;
- the packet is complete and its manifest accounts for every proposed artifact;
- sources, hashes, availability, lineage, and limitations are explicit;
- results, hypotheses, negative evidence, and prospective work are distinct;
- derived editions agree with the current source and audit state;
- the requested destination is left to the publisher router, rather than a
  hand-written taxonomy or a PR-specific routing convention.

An accepted submission may be merged only as evidence staging under `incoming/`.
It must not directly modify a publication destination in the same PR.

## 3. Publication PR

Create the Publication PR only after acceptance. Start from a pinned `main`
base and use `tools/publisher` to validate and calculate the destination.
The PR contains only router-produced publication changes and generated indexes
required by the existing repository checks. Preserve the accepted incoming
packet and historical receipts; do not rewrite them to make the publication
look cleaner.

Before requesting review, run:

```powershell
python tools/tare_docs.py validate-repo .
python tools/tare_docs.py rebuild-catalog .
git diff --exit-code -- catalog/MASTER_CATALOG.json
```

Commit any intended catalog regeneration. A clean command after rebuilding is
evidence that the committed catalogue matches the repository; it is not a
substitute for editorial or canonical review.

## 4. Maintenance PRs

Maintenance-only PRs may bypass `incoming/`, but must use the PR template and
must not silently alter document authority, source bytes, lineage, or a
published conclusion. If a maintenance change changes evidence meaning, submit
it as a publication packet instead.
