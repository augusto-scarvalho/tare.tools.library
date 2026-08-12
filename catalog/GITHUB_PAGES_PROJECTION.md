# GitHub Pages Reading Projection

[← Curation Catalog](README.md) · [Repository Navigation](../NAVIGATION.md) · [Study Editions](../studies/README.md)

**Status:** PROPOSED/IMPLEMENTED-IN-CANDIDATE for the site projection; **DEPLOYMENT NOT ENABLED by this document.**

## Purpose

GitHub Pages is a **reconstructable reading projection** over the research repository. It must not become a second source of truth.

```text
Git-tracked Markdown + byte-preserved HTML + navigation metadata
                         │
                         ▼
                  Jekyll / Pages build
                         │
                         ▼
             rendered research library site
```

The site may be deleted and rebuilt without losing research knowledge. Source identity remains the Git path/blob/commit, not the generated Pages URL.

## Reuse model

- Living Markdown is rendered directly from its existing repository path.
- `jekyll-relative-links` translates repository-relative Markdown links for the site.
- `jekyll-readme-index` turns directory `README.md` files into section index pages.
- `jekyll-optional-front-matter` allows existing Markdown files to remain readable on GitHub without requiring site-only front matter everywhere.
- Byte-preserved HTML under `bridge-editions/` is copied as static HTML and therefore renders as a real study in Pages without changing the source bytes.
- `_data/navigation.yml` is projection metadata only; it does not define architecture or research truth.
- `studies/README.md` is the human index from HTML editions back into living research.

## URL / source semantics

The same research object has different representations:

- Git blob/commit URL → source identity and audit/history.
- Markdown page in Pages → living reading projection.
- HTML bridge edition in Pages → rendered historical study checkpoint.
- File Library exact artifact → source edition not yet materialized in Git where recorded by `REHYDRATION_GAPS.md`.

Pages must never erase these distinctions.

## Deployment safety

The repository is currently private and owned by a personal GitHub account. Private Pages access control is not assumed. Deployment therefore MUST NOT be automatic from a merge until site visibility has been deliberately reviewed.

The deployment workflow is intentionally manual and requires all of:

1. execution from `main`;
2. GitHub Pages configured to use GitHub Actions;
3. repository Actions variable `PAGES_PUBLISH_ACK=true`;
4. an explicit `workflow_dispatch` invocation.

If private authenticated publishing is required, re-evaluate hosting/access-control options before setting the acknowledgment variable.

## Site UX responsibilities

The projection owns only reading ergonomics:

- persistent navigation;
- study-edition discovery;
- responsive Markdown typography;
- local search across Markdown pages and study metadata;
- links back to Git source;
- source/provenance visibility.

It does **not** own findings, status, architecture, evidence, or publication authority.

## Rollback

Disable/unpublish GitHub Pages or remove the Pages deployment workflow. No research content migration is required because the site has no unique semantic state.
