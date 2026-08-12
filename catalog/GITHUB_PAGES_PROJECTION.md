# GitHub Pages Reading Projection

[← Curation Catalog](README.md) · [Repository Navigation](../NAVIGATION.md) · [Study Editions](../studies/README.md)

**Status:** CURRENT for the public reading projection on `agent/semantic-preservation-curation-v2`; this does **not** promote the branch's research content to canonical `main`.

## Purpose

GitHub Pages is a **reconstructable reading projection** over the research repository. It must not become a second source of truth.

```text
Git-tracked Markdown + byte-preserved HTML + navigation metadata
                         │
                         ▼
                  Jekyll / Pages build
                         │
                         ├── SIGNAL shell for Markdown/navigation
                         ├── SIGNAL projection styling for generated HTML editions
                         └── historical Pxx reference resolution
                         │
                         ▼
             public rendered research library site
```

The site may be deleted and rebuilt without losing research knowledge. Source identity remains the Git path/blob/commit, not the generated Pages URL.

## Reuse model

- Living Markdown is rendered directly from its existing repository path.
- `jekyll-relative-links` translates repository-relative Markdown links for the site.
- `jekyll-readme-index` turns directory `README.md` files into section index pages.
- `jekyll-optional-front-matter` allows existing Markdown files to remain readable on GitHub without requiring site-only front matter everywhere.
- Byte-preserved HTML under `bridge-editions/` remains unchanged in Git.
- After Jekyll copies those HTML files to `_site/`, `scripts/apply_signal_study_projection.py` applies reading-only enhancements to the generated copies.
- `_data/navigation.yml` is projection metadata only; it does not define architecture or research truth.
- `studies/README.md` is the human index from HTML editions back into living research.

## SIGNAL research profile

The Pages projection reuses the canonical SIGNAL visual language from the tare.tools GUI without importing the React application or GUI runtime semantics.

Reused visual semantics include:

- warm-black / olive surfaces;
- lime-phosphor `accent` and teal `stream` roles;
- mono-forward instrument typography intent;
- 52px topbar density;
- restrained borders and radii;
- live-edge / active emphasis rather than decorative glow;
- scanline/vignette atmosphere;
- explicit status semantics and measurement-oriented presentation;
- reduced-motion support.

The research site deliberately does **not** reuse operational GUI components such as AppShell, Inspector, runtime actions, capability controls, or React state. Those belong to the Experience Plane application, not to a static research reader.

The canonical GUI source remains the tare.tools design system and token implementation. The research profile is a projection/adaptation, not a second design-system authority.

## Historical internal-corpus reference resolution

The byte-preserved scientific refresh HTMLs contain `Internal corpus references` entries such as `[P01]`, `[P02]`, etc. In the preserved source these entries are citation text, not hyperlinks.

Pages resolves those citations only in the generated `_site` copy. The citation wording and Pxx identity remain untouched in Git.

Resolution targets are deliberately typed:

- `living` → the best current living research continuation of the cited lineage;
- `proposal` → a current technical proposal when the citation corresponds primarily to a proposed implementation/contract;
- `evidence` → a case study or implementation-evidence record;
- `provenance` → the provenance/recovery index when an exact current artifact is not materialized as a living page.

This is a **reading resolver**, not source substitution. A link to a living successor does not assert that the successor is byte-identical to, or normatively supersedes, the historical cited artifact.

When an exact deep artifact exists only outside Git, the provenance destination preserves that distinction rather than inventing a local replacement.

## URL / source semantics

The same research object has different representations:

- Git blob/commit URL → source identity and audit/history.
- Markdown page in Pages → living reading projection.
- HTML bridge edition in Git → byte-preserved study checkpoint.
- HTML bridge edition in Pages → SIGNAL-styled generated reading projection of that checkpoint with Pxx navigation adapters.
- File Library exact artifact → source edition not yet materialized in Git where recorded by `REHYDRATION_GAPS.md`.

Pages must never erase these distinctions.

## Deployment state

The repository is public and GitHub Pages is enabled through GitHub Actions with HTTPS enforcement.

The current public preview is intentionally deployed from `agent/semantic-preservation-curation-v2` while `main` remains unchanged. This separates two decisions:

1. **publish the candidate reading experience for evaluation**;
2. **promote the semantic-preservation curation to `main`**.

The second decision has not been implied by the first.

## Site UX responsibilities

The projection owns only reading ergonomics:

- persistent navigation;
- study-edition discovery;
- responsive Markdown typography;
- local search across Markdown pages and study metadata;
- links back to the exact deployed Git source ref;
- historical Pxx citation navigation;
- source/provenance visibility;
- SIGNAL visual continuity with the tare.tools Experience Plane.

It does **not** own findings, status, architecture, evidence, design-system authority, or research promotion authority.

## Validation

CI validates:

- repository-relative documentation links;
- successful Jekyll build;
- critical site outputs;
- presence of SIGNAL shell assets;
- SIGNAL projection markers on generated Study Editions;
- every generated `Pxx` internal-corpus reference has a resolver link;
- resolver targets exist in the generated site.

The source HTML blobs are not mutated by the projection step.

## Rollback

Disable/unpublish GitHub Pages or revert the projection assets/workflow. No research content migration is required because the site has no unique semantic state.
