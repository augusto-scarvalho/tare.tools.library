# Context checkpoint + post-compact reinjection (`ckpt`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/context_checkpoint.py).

Intake (SPEC-116 door NEW): request = "precisamos de algo pra te ajudar a não
empacar quando o contexto lotar" (owner, 2026-07-13, right after a 7h
autonomous loop crossed ~5 compaction events). Covered-check: the harness HAS
a continuity layer — `.harness/context/*.md` + a SessionStart hook — but the
hook read the files and printed only a banner (hook stdout IS the injection
channel; the content was discarded), and nothing produced fresh state into
STATE.md/NEXT_STEPS.md, so they rotted as bootstrap templates. The loop
survived on the vendor summarizer alone. Decision: **NEW** — give the layer a
producer and a real delivery. SLICE: no PreCompact auto-snapshot (a hook
cannot dump the agent's head; discipline + injection is the working pair).

## Goal

An agent that hits a context compaction resumes from harness state, not from
luck: a `checkpoint` verb keeps ONE bounded in-flight block (item, phase,
verify commands, note trail) in `.harness/context/NEXT_STEPS.md`, and the
SessionStart hook prints that block's actual content plus a typed, mtime-badged
pointer to every other canonical file (v5) so the state truly enters the fresh
window and is hydrated ONCE — for any agent CLI wired to the hook (Claude,
Codex), not just one vendor's summarizer.

## Applicability

Applies to `scripts/harness_lib/context_checkpoint.py` (`write_checkpoint`,
`clear_checkpoint`, `read_checkpoint`, `render_reinjection`), the `checkpoint`
CLI verb (cli_registry; frozen surface grows by one), and
`tools/hooks/reload_context_after_compact.py` (SessionStart, both vendors via
`.harness/capabilities.json`). Writes only the inflight block in
NEXT_STEPS.md; every other canonical context file stays read-only here.

## Requirements / invariants (numbered, testable)

1. **One bounded block, carry-over updates.** The checkpoint is a single
   `<!-- inflight:start/end -->` block: rewriting with only a note preserves
   the previous item/phase/verify; the trail keeps ONLY the newest entry
   inline — older entries are appended, never deleted, to the append-only
   archive `.harness/context/checkpoint-trail.md`, and the block's Trail
   header carries the archived count + path (v4).
2. **Redacted at write.** Notes, item and verify pass
   `secret_scan.redact_text` before touching the tracked file.
3. **Clear is calm.** `--clear` removes the block and leaves the rest of
   NEXT_STEPS.md intact; clearing when absent is a no-op, rc 0.
4. **The hook injects content, not a banner — and hydrates ONCE (v5).** Its
   stdout carries exactly ONE body: NEXT_STEPS.md (first — the in-flight block
   is the payload and exists nowhere else), the block whole plus the
   surrounding file capped. Every OTHER canonical file — CONTEXT.md, STATE.md,
   LEDGER_HEAD.md, `.harness/handoff/handoff.md`,
   `.harness/state/task-state.json`, `.harness/state/quality-state.json` —
   renders as ONE typed pointer line: `- <rel> (updated <mtime>, <N> B) —
   "<lead>"; read on demand`, where `<lead>` is the file's first non-empty
   non-heading line capped at 100 chars. No head+tail dump of a pointed-at
   file. Absences read calmly (`- <rel> — absent`); missing REQUIRED context
   files (NEXT_STEPS.md, CONTEXT.md, STATE.md) exit 1, naming them.
5. **CLI parity.** Bare `checkpoint` shows the block (or a calm fix line);
   `--render` prints exactly the reinjection payload; the SessionStart hook
   prints this payload then appends the SPEC-138 warm-up doc when present
   (`specs/40-features/overseer-warmup.md`). Empty note refuses legibly.
6. **Wholesale rewriters preserve the block.** `workflow_lifecycle`
   regenerates NEXT_STEPS.md from a template on every reduce; it must route
   through `merge_preserving_inflight` so an in-flight checkpoint survives a
   workflow finishing mid-iteration.

## Gherkin scenarios

```gherkin
Feature: context checkpoint (producer + reinjection)

  Scenario: [ckpt-1] the block updates with carry-over, bounded and redacted
    Given a checkpoint with item, phase, verify and a planted key in the note
    When further notes arrive without repeating the fields
    Then one block holds the carried fields, only the newest trail entry with
      an archive pointer for the rest, and the key appears only redacted

  Scenario: [ckpt-2] clearing ends the iteration calmly
    Given a file with a checkpoint block and surrounding content
    When clear runs twice
    Then the block is gone, the rest survives, and the second clear no-ops

  Scenario: [ckpt-3] the reinjection payload is badged, ordered and pointer-first
    Given a root with an oversized CONTEXT.md and no STATE.md, handoff or
      state JSONs
    When render_reinjection runs
    Then NEXT_STEPS leads with its body, the oversized CONTEXT.md is a single
      pointer line carrying mtime, byte size and a one-line lead — with no
      body and no head+tail cap marker — and every missing file reads as absent

  Scenario: [ckpt-4] the hook and the verb are wired for real
    Given the repository's SessionStart hook and live CLI
    When the hook runs and checkpoint --help runs
    Then the hook stdout contains actual file content (not a banner) and the
      verb answers rc 0 on the frozen surface

  Scenario: [ckpt-5] a workflow rewrite does not eat the checkpoint
    Given a NEXT_STEPS.md holding an in-flight block
    When the lifecycle template rewrite merges through the preserving seam
    Then the new summary and the untouched block coexist, and the lifecycle
      writer routes through that seam
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Hook imprime CONTEÚDO (stdout = canal de injeção) | bug observado: hook antigo lia e descartava; loop de 7h sobreviveu só pelo summarizer do vendor |
| Produtor = verbo `checkpoint`, não PreCompact | um hook não extrai o estado da cabeça do agente; a disciplina de fase + injeção é o par que funciona |
| Bloco em NEXT_STEPS.md, não arquivo novo | o arquivo já existe, já é REQUIRED do hook e se declara "current dynamic next-step context" |
| Redação na escrita | arquivo tracked; mesmo seam `secret_scan.redact_text` (ui_commits, ui_memory) |
| mtime badges + caps por arquivo | STATE.md/handoff.md podem estar velhos; o leitor precisa ver a frescura, não adivinhar |
| Agent-agnostic (arquivos, não memória de vendor) | tese do harness universal; `.harness/capabilities.json` liga o mesmo hook em Claude e Codex |

## Test strategy

- Behaviors: carry-over + trail fold/pointer + redaction (ckpt-1); calm clear
  preserving the archive (ckpt-2); order/badges/pointer-lines/absences and the
  ABSENCE of a dumped body (ckpt-3, plus hib-6 on the real payload); real
  wiring (ckpt-4); lifecycle-rewrite coexistence (ckpt-5); fresh-root
  no-archive + over-cap render with pointer header (ckpt-7).
- Edge cases: empty note refuses with fix line; missing NEXT_STEPS.md is
  created on first write; block survives regex-meaningful characters.
- Regression net: cli_registry frozen-surface scenario (surface +1);
  module self-check.
- Coverage: deterministic, stdlib-only —
  `testing/scenarios/context_checkpoint.py`.

## Validation

- `python testing/scenarios/context_checkpoint.py` — ckpt-1..ckpt-7 green.
- `python scripts/harness_lib/context_checkpoint.py` — module self-check.
- `python testing/scenarios/cli_registry.py` — frozen top-level surface.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` —
  template conformance + static integrity.

## Amendments

### v2 (2026-07-13) — req 5 reworded for the SPEC-138 warm-up append

`--render` still prints exactly the reinjection payload; req 5 now records that
the SessionStart hook prints that payload and THEN appends the committed warm-up
doc when present (`specs/40-features/overseer-warmup.md`, SPEC-138). No behavior
change here: `REINJECT_RELS` and `context_checkpoint.py` are unchanged, so the
`--render` contract is untouched; only the hook composes state + discipline.
No new numbered requirement — SPEC-138 osw-2 covers the hook order.

### v3 (2026-07-23) — render budgeted to the vendor inline ceiling + dedup

Claude Code injects hook stdout inline only below 10,000 chars; the old
render (~13k state alone) was silently persisted-to-file — the checkpoint
block never reached fresh contexts, ckpt's whole purpose. Render changes
(the FILES are untouched; only the rendered working set shrinks):

- Per-file render budgets (`FILE_CAP` 1400 default, `NEXT_STEPS_CAP` 2200,
  `HANDOFF_CAP` 1300); `_cap` splits head/tail proportionally.
- The inflight block's fields (Item/Phase/Verify) always render whole
  (`_cap_block`); the trail renders newest-first within `BLOCK_CAP` 1300
  with an explicit render-cap marker — EXP-2's loss class is structurally
  closed and `reinjection_loss` now watches for regression only.
- Dedup at render: handoff.md's `## Last workflow` section becomes a
  pointer (NEXT_STEPS.md carries the identical text); the checkpoint
  block's `Note:` line is gone from the WRITE format — the trail's last
  entry was a verbatim duplicate.
- Aggregate teeth: `testing/scenarios/hib_hook_inline_budget.py` (hib-1..3)
  asserts the composed hook payload fits `TOTAL_BUDGET` (9.5k) under the
  vendor ceiling with the ambient role-chain core present
  (`specs/40-features/playbook-registry.md` v4).

### v4 (2026-07-28) — trail fold: newest entry inline, history in an append-only archive

Round `docs/research/adocao-governanca-contexto.md` (D053, backlog row
`ctx-trail-fold`): the trail had become the expensive part of every canonical
read — 6 narrative entries ≈ 10.6k chars (~3.4k tokens), of which the 5
pre-newest (~2.5k tokens) were history nobody re-read. Write-format change:

- `TRAIL_MAX = 1`: only the newest trail entry stays inline in the block;
  every older entry is APPENDED (never deleted) to the append-only, tracked
  archive `.harness/context/checkpoint-trail.md`, redacted again at append.
- The block's Trail header becomes a pointer: `Trail: N older entries in
  .harness/context/checkpoint-trail.md`, where N counts the WHOLE archive
  (a post-`--clear` restart still points at everything already folded).
- `_cap_block` partitions on the header LINE (regex), not the literal
  `"Trail:\n"`, re-emits the pointer verbatim, and falls back to `_cap` on a
  hand-edited headerless block instead of crashing the render.
- `--clear` leaves the archive intact; a fresh root's first write creates no
  archive. The archive is deliberately NOT in `REINJECT_RELS`.
- Teeth: ckpt-1 (fold + pointer count + archive verbatim-redacted), ckpt-2
  (clear preserves archive), new ckpt-7 (fresh-root no-archive; over-cap
  render keeps pointer header + whole newest entry; legacy 6-entry block
  still renders — the migration shape `_cap_block` must survive).

### v5 (2026-07-28) — single-channel hydration: one body, five pointers

Round `docs/research/adocao-governanca-contexto.md` (D053, backlog row
`ctx-hidratacao-unica`). WHY, measured 2026-07-28: the same state was paid
TWICE at every session start. The SessionStart payload emitted 9.8k chars
capped (untrimmed 10,687: head 194 + state 7,939 + protected 2,553) ≈ 3.2k
tokens, AND `AGENTS.md` §Required startup read ordered the same six files read
IN FULL = 16,404 chars ≈ 5.3k tokens — CONTEXT/STATE/NEXT_STEPS arriving twice,
~8.5k tokens per session. The head+tail dump replaced no read and is strictly
worse than a summary of the same file (study §5.5.1); hydration should be
minimal + pointers (§3.3/§6.3). Render change only — the FILES are untouched:

- `REINJECT_RELS` splits into `INLINE_RELS = (NEXT_STEPS.md,)` and
  `POINTER_RELS` (CONTEXT.md, STATE.md, LEDGER_HEAD.md, handoff.md,
  task-state.json, quality-state.json — the six of AGENTS.md's startup read,
  not four). `REQUIRED_RELS` is unchanged: the same first three, same exit 1.
- `_render_next_steps` / `_cap_block` / `NEXT_STEPS_CAP` / `BLOCK_CAP` are
  untouched, so `reinjection_loss` and the EXP-2 guarantee still hold; the
  inflight block is the one thing that exists nowhere else.
- Retired: `_render_handoff` + `_LASTWF_RE` (the Last-workflow dedup — a
  pointer cannot duplicate a body), `FILE_CAP`, `HANDOFF_CAP`. Added:
  `SUMMARY_CAP` 100 and the lead rule — first non-empty non-heading line,
  deterministic on purpose: a hand-written summary field is one more thing to
  keep fresh and a stale one is worse than none. A JSON file's lead is `{`;
  the pointer's value there is path + mtime + size.
- `TOTAL_BUDGET` stays 9,800 (the saving comes from the shape, not a lower
  ceiling) and `tools/hooks/reload_context_after_compact.py` needs no code
  change. Measured after: render 8,019 → 3,895 chars; whole hook payload
  6,566; `doctor`'s `reinjection-budget` reports ok with NO state shave (the
  shave had been the permanent designed steady state).
- Teeth: ckpt-3 rewritten (an oversized CONTEXT.md must render as a pointer
  line with mtime + bytes + lead and NO body/cap marker; absences still calm,
  including the two state JSONs) and NEW hib-6 on the real payload
  (`testing/scenarios/hib_hook_inline_budget.py`): ≥6 pointer lines, no
  pointed-at file's body, no cap marker at or after the pointer section, and
  `len(payload) <= HYDRATION_BUDGET` 7,000 — a separate knob from
  TOTAL_BUDGET, since fitting the vendor ceiling is not the same claim as
  staying pointer-shaped.
- `AGENTS.md` §Required startup read is amended in the same commit: this
  payload is the authority, pointers open on demand, and the full read is the
  fallback only for a session with no reinjection payload (no hook).
