# SPEC-167 — Wiki-spec guard: docs/wiki conformance + repo-wide spec-ref resolution

Status: SPEC-167, proposed 2026-07-22 (acceptance: `testing/scenarios/wg_wiki_spec_guard.py`).

## Goal

Keep the fragmented `docs/wiki/` surface honest forever, not just once: every
wiki page must summarize-and-link (never inline canonical text), resolve its own
relative links, and reference only real specs — and no `SPEC-###` mention
anywhere under `specs/**`/`docs/**` may point at a spec that does not exist.
The guard is deterministic (pure stdlib, zero LLM, zero network) so conformance
does not depend on an agent remembering the wiki content law
(`docs/HARNESS_CONTENT_GUIDE.md`) or on a human PR reviewer catching a stale
`SPEC-###` back-reference.

## Applicability

`scripts/harness_lib/wiki_conformance.py`, wired into the `spec-pack` gate branch
(alongside `markdown-links` + `feature-spec-conformance`). It governs
`docs/wiki/**.md` pages and reads spec definitions from `specs/**`. It does NOT
edit wiki content, does NOT own the general markdown link check (that stays
`check_markdown_links`, repo-wide), and does NOT replace `feature-spec-conformance`
(SPEC-116 template/Gherkin shape). The `spec-ref-guard` half additionally scans
all of `specs/**` + `docs/**` for textual `SPEC-###` references.

## Requirements / invariants (numbered, testable)

1. **Summarize-and-link marker.** Every `docs/wiki/**.md` page contains the marker
   prefix `<!-- wiki-sources: summarize-and-link`; a page missing it fails
   `wiki-conformance:<relpath>` with a legible "missing marker" detail.
2. **Relative links resolve.** Every relative markdown link on a wiki page resolves
   to an existing file (external `http(s)`/`mailto:`/anchor/autolink targets are
   out of scope); a dangling link fails the page's check, naming the link.
3. **Spec-refs defined-or-whitelisted (per page).** Every `SPEC-###` textual ref on
   a wiki page resolves to a spec defined under `specs/**` (a `# SPEC-###` heading
   or a `Status: SPEC-###` line), or is in the frozen whitelist {SPEC-105,
   SPEC-122}, or matches the exempt patterns SPEC-000 / SPEC-9xx.
4. **80-line page cap.** A wiki page over 80 lines fails its check with the detail
   telling the author to summarize and link rather than inline canonical text —
   the wiki summarizes; specs stay whole (SPEC-116 owns their shape).
5. **Repo-wide spec-ref-guard.** One `spec-ref-guard` check scans every `.md` under
   `specs/**` + `docs/**`; it fails, naming the offending file(s) and ref(s), if
   any `SPEC-###` mention is neither defined, whitelisted, nor exempt — so no stale
   forward/back reference survives ("sem referências quebradas pra trás").

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Wiki summarizes + links, never duplicates normative text | `docs/HARNESS_CONTENT_GUIDE.md` anti-duplication law; roadmap `docs/roadmap/docs-wiki.md` §4.4/§4.6 |
| Whitelist exactly {SPEC-105, SPEC-122} | `docs/roadmap/docs-wiki.md` §2 B1/B2 (105 = documented gap; 114 shipped the panel) and gate-structure-checks tracking SPEC-122 by name with no own spec file |
| Deterministic gate, no LLM/network | roadmap §7 "All checks deterministic — no LLM (net-cost-positive rule)" |
| 80-line cap as the summarize-and-link forcing function | roadmap §4.4 (topics are short leigo→técnico summaries; specs stay whole under SPEC-116) |

## Gherkin scenarios (UI surfaces only)

Included because the wiki is a rendered surface (a Panel Wiki view / doc corpus);
the ids map to named checks in `testing/scenarios/wg_wiki_spec_guard.py`.

```gherkin
Feature: Wiki-spec guard keeps docs/wiki honest

  Scenario: [wg-1] a well-formed page passes
    Given a wiki page with the marker, resolving links and a real spec ref under 80 lines
    When the wiki-spec guard runs
    Then that page's conformance check passes

  Scenario: [wg-2] a page missing the summarize-and-link marker fails legibly
    Given a wiki page without the wiki-sources marker
    When the guard runs
    Then the page fails and the detail says the marker is missing

  Scenario: [wg-3] a broken relative link fails, naming it
    Given a wiki page linking to a file that does not exist
    When the guard runs
    Then the page fails and the detail names the dangling link

  Scenario: [wg-4] a dead spec ref fails but a whitelisted ref does not
    Given a wiki page mentioning an undefined SPEC and the whitelisted SPEC-105
    When the guard runs
    Then the page fails naming the undefined SPEC and never flags SPEC-105

  Scenario: [wg-5] an oversized page fails with the summarize-and-link detail
    Given a wiki page longer than 80 lines
    When the guard runs
    Then the page fails and the detail tells the author to summarize and link
```

## Ceilings (upgrade paths)

- 3-digit `SPEC-###` matching (`SPEC-\d{3}`); revisit if the repo ever reaches
  `SPEC-1000`.
- The whitelist is a frozen literal set; a legitimate new unresolved ref needs a
  reviewed one-line addition with its reason (never silent growth).
- `spec-ref-guard` rescans `specs/**`+`docs/**` each run (single pass, <1s at the
  current corpus); move to a changed-files pre-filter only if it is ever measured
  slow.

## Test strategy

- Behaviors to verify: marker presence, link resolution, per-page + repo-wide
  spec-ref resolution, whitelist/exempt handling, the 80-line cap detail.
- Edge cases: whitelisted ref must not offend; external links skipped; a page that
  is itself a link target still needs its own marker.
- Regression risks: the frozen-surface modules (`spec_conformance.py`,
  `gate_checks_structure.py`, `gate_checks_content.py`) and the `gs-*` line ratchet
  must stay green — the guard adds no line to `scripts/spec_test_gate.py`.
- Coverage impact: enforced via `testing/scenarios/wg_wiki_spec_guard.py` and the
  `spec-pack` gate.

## Validation

- `python testing/scenarios/wg_wiki_spec_guard.py` — checks `wg-1`..`wg-5` (the
  five invariants over fixtures) plus `wg-live` (the shipped `docs/wiki` 39/39 and
  the repo-wide `spec-ref-guard` are green today).
- `python scripts/harness_lib/wiki_conformance.py` — the module tempdir self-check.
- `spec-pack` gate green: emits `wiki-conformance:<relpath>` per page + one
  `spec-ref-guard`, alongside `feature-spec-conformance:wiki-spec-guard`.

## Amendments

(none yet)
