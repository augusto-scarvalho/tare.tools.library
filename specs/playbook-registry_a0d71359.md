# SPEC-170 — Playbook registry & role inheritance

Status: SPEC-170, proposed 2026-07-23 (acceptance: `testing/scenarios/playbook_registry.py`).

## Goal

One declarative registry gives every agent ROLE a playbook chain by
inheritance (child reads parent's playbooks + its own), so repeated
instructions live in exactly one file, spawns reference chains instead of
pasting discipline, and the chain is tracked (existence, hash, references)
by a deterministic gate check.

## Applicability

`.harness/routing/playbook-registry.json`, the `harness.py playbook` verb,
the registry gate check, and (phase W2) every role-resolving spawn surface
(route driver, Agent-tool spawn economy, GUI room spawn, codex lane
recipes). Does NOT cover: playbook CONTENT authorship, per-target overlays
(SPEC-110), multiple inheritance, GUI (arrives as a versioned amendment
with Gherkin when the Registry->Roles slice ships).

## Requirements / invariants (numbered, testable)

1. **Registry home & shape.** `.harness/routing/playbook-registry.json`:
   `schemaVersion`, `roles{<role>: {extends?, playbooks[]}}`, plus
   `unmanaged[]` — prompt files deliberately outside role chains. Single
   parent only; `agent-base` is the root and carries the canonical
   `AGENTS.md` (owner Q3: vendor adapter files are thin shims to it).
2. **Chain resolution.** `playbook <role> --list` prints the parent→child
   ordered file paths, first-occurrence de-duplicated. Unknown role, cycle,
   or missing file is a TYPED refusal (rc != 0, `fix:` line) — never a
   partial chain.
3. **Compose is secondary.** `--compose` concatenates the same chain with a
   per-file origin header. The spawn-facing default is `--list` (owner Q2:
   cache-friendly, origin-attributable).
4. **Tracking gate check.** `playbook --verify` (wired into scenarios) is
   red on: a registered path that does not exist; a `.md` under
   `.harness/prompts/` absent from BOTH some role chain and `unmanaged[]`
   (orphan); a broken relative md cross-reference inside a registered
   playbook. Exists+sha256+updated-at are reported per file (owner Q6).
5. **Single source of values.** Model/effort/executor pins live ONLY in
   `model-routing.json` (join by role key). A registry role entry carrying
   `card`/`effort`/`executor` keys fails `--verify` (owner: zero value
   duplication).
6. **Hard enforcement (W2).** A role-resolving spawn surface given a role
   absent from the registry (or an unresolvable chain) REFUSES the spawn
   (owner Q8). Pre-flip acceptance: the registry covers every live spawn
   path; the refusal is typed like the route generic-stub refusal.
7. **Additive landing.** Absent/malformed registry file: `playbook` refuses
   gracefully with a typed error; nothing else changes behavior until the
   registry lands (transition safety for W1->W2).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Registry in `.harness/routing/`, join by role key | owner Q1 2026-07-23; model-routing.md precedent (roles already keyed there) |
| `--list` chains over composed injection | owner Q2; D038 lane-brief economy (pre-assembled context beats re-reads; prompt-cache stability) |
| Canonical AGENTS.md as `agent-base` root, vendor shims thin | owner Q3 (in-chat architecture ruling) |
| De-dup same wave as registry | owner Q4; duplicated rituals observed loop-vs-session playbook 2026-07-23 |
| exists+hash+updated-at only (no version headers) | owner Q6; git already owns history |
| Taxonomy incl. ui-overseer/security-auditor day 1 | owner Q7; D039 UI doctrine + escalation contract as inherited content |
| HARD spawn refusal from day 1 | owner Q8; mirrors route rt-13 generic-stub refusal pattern |
| Refinement trail | docs/research/playbook-hierarchy-refinement-2026-07-23.md (Q1-Q8 ratified); escalation route-432771c2 resolved by owner |

## Ceilings (upgrade paths)

Single-parent inheritance; add mixins only when a real role needs two
parents. Orphan rule scoped to `.harness/prompts/` (playbooks elsewhere are
out of scope until one exists). md cross-reference check is relative-link
resolution only, not anchor validation — upgrade if broken anchors bite.

## Test strategy

- Behaviors: chain order (loop-overseer == AGENTS.md + overseer +
  overseer-loop), unknown-role/cycle/missing-file refusals, orphan + broken-
  ref + pin-duplication verify reds, unmanaged allowlist honesty.
- Edge cases: role with no own playbooks (pure inheritor), empty registry,
  registry absent (rule 7).
- Regression risks: none until W2 (additive); W2 touches spawn paths —
  every refusal case needs a scenario before the flip.
- Coverage impact: enforced via `playbook_registry.py`.

## Validation

`python testing/scenarios/playbook_registry.py` (checks `pr-1`..`pr-6`,
hermetic fixtures + real-registry pass) + `spec-pack` green. W2 adds spawn-
refusal checks (`testing/scenarios/playbook_enforcement.py`, `pe-1`..`pe-5`).
W3 GUI: `testing/scenarios/react_smoke.py` (Gherkin ids `rs:registry-tree`,
`rs:registry-chain`, real headless chromium).

## Amendments

### v2 (2026-07-23) — W2 núcleo from the research round + chain consumption

Research trail: `docs/research/playbook-inheritance-round-2026-07-23.md`
(crossed 2×2, owner-designed) and the companion article. New rules:

8. **Chain lockfile.** `--verify` regenerates
   `.harness/routing/playbook-registry.lock.json` (auto-generated only):
   per-role resolved file list + chainHash (sha256 over LF-normalized
   concatenation). A pre-regeneration mismatch against an existing lock is
   a `lock-drift` finding (red). [research S2-C1, absorbing N1-C1 minus
   PKI]
9. **Effective view.** RETIRED by SPEC-173 rule 19 (Phase 4b, D055): the
   `--render` verb and the concat composer it printed were DELETED with the
   concat path. The effective view is now the compiled Effective Playbook
   served by `playbook <role> --compose` (banner + chainHash + per-file
   origin lines survive there). [S2-C2; helm-template precedent; superseded
   2026-07-30]
10. **Advisory collision linter (EXP-34, measure-only).** Duplicate H2
    headings with differing content inside one chain emit `advisories`
    entries in `--verify --json`; rc is NEVER affected. Gate-wiring is a
    future control change citing the experiment verdict.
    `<!-- collision-ok -->` suppresses per heading. [S2-C3; Ansible
    silent-collision failure mode]
11. **Session chain injection.** The SessionStart reinjection hook
    resolves the session role's chain (env `HARNESS_SESSION_ROLE`,
    default `overseer`) and injects the chain files' content (AGENTS.md
    skipped — vendor layer carries it; registry absent = silent skip per
    rule 7). Closes incident I2 (role knowledge in an unloaded file).
12. **Shared-ritual home.** Delegation rituals (roles, plan-brief
    doctrine, launch recipes, review ritual, failure modes, escalation
    contract, WF cycle disciplines) are canonical in
    `overseer-playbook.md` since the 2026-07-23 verbatim move;
    `overseer-loop-playbook.md` holds loop-only mechanics + pointers.

Rationale additions:

| Decisão | Fontes |
|---|---|
| Concatenate-don't-override stated explicitly (chain order = position precedence, no override mechanism) | Claude Code memory docs (concatenation hierarchy, primary); round card S1-C6 |
| v2-mixins door: C3-style fail-fast on ambiguous linearization, never guess | Python MRO precedent; round card S2-C5 |
| Lockfile LF-normalized | GLM critic catch: CRLF/POSIX hash divergence on Windows-first repo |

### v3 (2026-07-23) — W3 GUI: hierarchy panel + chain inspector (Registry -> Roles)

13. **Hierarchy panel.** Registry -> Roles renders a compact collapsible
    role tree from the registry's `extends` edges (`/api/access-matrix`
    `playbooks` block): role, own-playbook count, chainHash prefix;
    registry absent -> honest "— (no registry on disk)". Matrix-present
    roles are clickable (row select); pure inheritors render muted.
14. **Chain in the inspector.** A selected registered role's inspector
    shows extends, chainHash (lock), and the chain files in read order
    with per-file sha12 + updatedAt (Q6 tracking); own playbooks marked.

### v4 (2026-07-23) — ambient-core injection: rule 11 sized to the vendor ceiling

Same-day correction to rule 11: whole-file chain injection (25k/file cap)
emitted 36.8KB while Claude Code injects hook stdout inline only below
10,000 chars (persisted-to-file above, code.claude.com/docs/en/hooks) — the
mechanism that closed incident I2 reintroduced it; observed live 2026-07-23
(an interactive session skipped the fuel-check ritual because the chain
never entered context).

15. **Ambient core, not whole file.** The hook injects each chain file's
    `<!-- ambient:start/end -->` block; a file without markers degrades
    calmly to a head excerpt + read-the-file note (rule 7). The overseer
    playbook's block carries the non-negotiables and cites the full file
    as the contract. AGENTS.md stays skipped (codex loads it natively;
    on Claude only the CLAUDE.md shim is ambient — owner-gated intake
    tracks revisiting).
16. **Aggregate budget.** The hook's total stdout is budgeted
    (`TOTAL_BUDGET`, 9.5k chars) with a defense trim; the hib scenario
    (`testing/scenarios/hib_hook_inline_budget.py`) enforces payload
    fit, presence of state+warmup+ambient core, and the ambient block's
    share against the real repo. Individual budgets without an
    aggregate watcher were the root cause.
17. **History lives in the archive.** Playbooks carry current-state
    rules; incident narratives moved to `docs/PLAYBOOK_ARCHAEOLOGY.md`
    (doc-find indexed), cited as `(arch: <id>)` — owner directive
    2026-07-23 (rules-not-history, direct prose, TSV-over-JSON where a
    table is data).

### v5 (2026-07-23) — spawn-time composed injection, per-role knob (owner: B-com-knob)

Evidence: live room check 2026-07-23 — the route-overseer room received
neither chain content nor a chain reference (the porteiro handoff brief is
the route decision JSON only, `chat_operator.py`); the vendor SessionStart
channel is capped at 10k chars uniformly (stdout, `additionalContext`,
`systemMessage` — code.claude.com/docs/en/hooks), so the hook can never
carry a chain; owner ruled out vendor-specific escapes (CLAUDE.md imports,
multi-hook splitting) — chain delivery must be harness-owned and
vendor-neutral.

18. **Per-role injection knob.** A registry role entry MAY declare
    `"inject": "compose"` (absent = `"list"`, the Q2 status quo: spawns
    reference chains, workers read files). `--verify` is red on any other
    value. The knob is the ONLY path to composed injection, so a thin role
    (scanner, router, probes, fan-out workers) can never be fattened by
    accident (owner 2026-07-23: probes/workers stay lean).
19. **Composed injection at spawn (B).** A role-resolving spawn surface
    (GUI room spawn, route driver, Agent-tool spawn economy, codex lane
    recipes) spawning a compose-marked role injects the effective chain
    (since SPEC-173 4b: the compiled Effective Playbook — per-file origin
    headers + chainHash preserved) into the spawn
    prompt through that vendor's native prompt channel (claude
    `--append-system-prompt-file`, codex project-doc override, openai
    system message). Content enters mechanically — no read-obedience step
    (incident I2 class closed for spawned surfaces); the chainHash in the
    prompt makes the delivered chain version auditable in transcripts.
20. **Snapshot semantics.** Composed injection is a spawn-time snapshot:
    mid-session chain edits do not propagate (the chainHash betrays
    staleness, it does not refresh). One caveat, stated rather than
    engineered away: the rendered prompt is ONE file per role, so a second
    session booting that role rewrites it and — on vendors that re-read the
    prompt file per turn, claude among them — refreshes the first session
    mid-flight. Benign (deterministic from the same on-disk chain, newer
    beats staler); per-session files only if an incident needs a frozen
    chain. Compose is therefore for short-lived,
    owner-watched surfaces first (route-overseer / ui-overseer rooms);
    owner-started interactive sessions remain on ambient cores (rules
    15-16) — that residual surface is the hook's, not this rule's.

Rationale additions:

| Decisão | Fontes |
|---|---|
| B-com-knob: composed opt-in, list default | owner in-chat 2026-07-23 ("A parece ser pior que B" — a reference line still depends on read-obedience); Q2 economics preserved for thin roles |
| Hook channel ruled out for chain delivery | 10k cap is uniform across stdout/`additionalContext`/`systemMessage` (doc-confirmed 2026-07-23) |
| No vendor-specific mechanism | owner 2026-07-23 ("nada de mecanismo claude only"); CLAUDE.md `@import` and multi-hook splits rejected |

Acceptance (before the flip, mirrors rule 6 discipline): a compose role's
spawn prompt carries the chainHash + chain content; a default role's spawn
prompt carries neither; an unknown `inject` value is a `--verify` red.
Scenario: `testing/scenarios/pci_compose_inject.py` (`pci-1`..`pci-4`).

## Gherkin scenarios (UI surfaces only)

```gherkin
Feature: Playbook-registry hierarchy in the Registry screen

  Scenario: [rs:registry-tree] the role hierarchy is consultable
    Given the playbook registry declares the role taxonomy
    When the operator opens Registry Roles and expands the hierarchy panel
    Then every registered role appears in the extends tree with its playbook count

  Scenario: [rs:registry-chain] a role's playbook chain is inspectable
    Given a role that appears in the roles matrix
    When the operator picks it from the hierarchy panel
    Then the inspector shows the chain files in read order with their content hashes
```
