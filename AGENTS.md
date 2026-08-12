# AGENTS.md — tare.tools.research

## Purpose

This repository is the **live research library** for tare.tools. It is not a raw archive, not an implementation repository, and not architectural authority.

## Precedence

`tare-tools` Git/source/state/ADRs/SPECs/BDDs/gates > ratified architecture > this research repository.

Always distinguish `CURRENT`, `TARGET`, `PROPOSED`, and `RESEARCH`. This repository may quote or challenge CURRENT/TARGET but does not mint them.

## Semantic curation rule

**Use reasoning before automation.** Curation is performed at the level of claims, findings, hypotheses, experiments, contradictions and lineages — never by filename, regex coverage, template compliance or document count.

Deterministic scripts/tools MAY validate syntax, links, anchors, hashes or generated projections after the intellectual work. They MUST NOT decide which research survives, which documents are equivalent, which conclusion supersedes another, or what the project should believe.

## Live-tree admission test

A file belongs in HEAD only if it has a clear current epistemic function:

- a substantive living study;
- a reproducible/meaningful experiment or empirical result;
- a curated finding/decision ledger;
- a research frontier question with actionable scientific value;
- a source/provenance record that cannot be reconstructed cheaply from Git history.

Raw chat dumps, historical snapshots, mechanical translations, format-only HTML renderings, superseded drafts, repetitive implementation deltas, generated indexes and source bundles do not belong in HEAD by default. Git history is the archive.

## Research discipline

- Preserve original conclusions when discussing historical work, but classify them `ADOPT / ADAPT / RETIRE / OPEN`.
- State conflicts and negative evidence explicitly.
- Prefer fewer high-density documents over many shallow artifacts.
- Do not create a new primitive/Plane because a historical noun appears often.
- Before implementation-facing proposals: map to canonical equivalents, bounded-context owner, CURRENT×TARGET gap, evidence/gates, migration and rollback.
- Same-model iterative review is structured test-time compute, not independent evidence.
- External papers/vendors/repos are evidence, not authority.

## Historical recovery

The pre-curation corpus is recoverable from Git commit `7ad1a71ebbad99e69bd6ba97b2ed29d78faf08de` and tag `bootstrap-v0.19.0`. Do not copy those bytes back into HEAD merely for archival comfort.
