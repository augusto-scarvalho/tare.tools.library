# Intake refinement — door NEW checklist

<!--
SPEC-116 invariant 2. Fill this ONE page before writing a spec from
specs/SPEC_TEMPLATE.md. A spec whose intake was skipped is non-conformant.
Its accepted acceptance criteria seed BOTH the numbered rules AND the Gherkin
scenarios of the resulting spec. Copy this file per request; keep it with the
work (target-project intake lives in the target's own specs tree).
-->

## Request (verbatim)

> Paste the request exactly as received. Do not paraphrase.

## Covered-check (which door?)

The mandatory lookup that decides door NEW vs door COVERED. Record the queries
run and what they returned — a duplicated spec for covered ground is a defect.

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search <terms>` | |
| doc-find | `python scripts/harness.py doc-find <terms>` | |

Decision: **NEW** (not covered → continue below) / **COVERED** (→ stop; amend the
existing spec with a versioned section instead).

## Goal

One sentence: the behavior/capability this request asks for.

## Scope

In scope:
- …

Out of scope:
- …

## Actors & surfaces

Who/what acts, and on which surface. **If any surface is UI, Gherkin scenarios
are required** in the resulting spec (SPEC-116 inv. 4).

- Actors:
- Surfaces (CLI / GUI / API / internal): 
- UI surface? yes → Gherkin required / no → Gherkin optional

## Proposed acceptance criteria

Testable statements. These seed the spec's numbered rules and, for UI surfaces,
its Gherkin scenarios — write them so a check can pass or fail on each.

- [ ] …
- [ ] …

## Risks / blast radius

What could this break; which modules/call sites it touches; rollback cost.

## Open questions for the human

- …
