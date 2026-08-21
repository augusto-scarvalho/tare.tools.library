# SEC.8 — non-local system-prompt slots: detect + surface, never edit

Status: proposed 2026-07-29 (acceptance: `testing/scenarios/sec8_prompt_slots.py`).
Door NEW: owner request 2026-07-26 (SEC roadmap, backlog row `SEC.8`); no
existing spec owns vendor-injected prompt state — it sits outside BOTH the
canonical layer (`.harness/`) and the adapter layer (`.claude/`), which is
the finding.

## Goal

Vendor-delivered instruction slots (`~/.claude.json`
`.clientDataCacheSlots.<opaque-key>.data.<name>`) alter session behavior
invisibly — one live slot suppressed plan-role delegation for a whole session
while neither owner nor ledger could say why. Control means DETECT + SURFACE
+ RECORD, never edit: the slot is server cache under an opaque key (not a
durable write target); the durable counter-lever is owner awareness, because
the observed slots are conditional ("unless the user requested it").

## Applicability

- `scripts/harness_lib/prompt_slots.py` — reader, baseline, diff, doctor row,
  ledger record; the only code that touches `~/.claude.json`, read-only.
- `scripts/harness_lib/repo_health.py` — carries `prompt_slots.doctor_check`
  into `checks()` (fail-open).
- `.harness/runs/prompt-slots-baseline.json` — class-D machine-local baseline.

Does not cover: editing the account file (never), hook-leg SessionStart
surfacing (deferred, owner-gated — see Ceilings), slot-text classification.

## Requirements / invariants (numbered, testable)

1. **Privacy floor.** `~/.claude.json` is account state. `prompt_slots` reads
   it and emits field paths, sha256 prefixes, kinds and lengths ONLY — slot
   TEXT never reaches the baseline, the diff, the doctor detail, the ledger,
   or any output. (sec8-1 fixture assert + sec8-3 live assert.)
2. **Baseline = reviewed set.** `snapshot()` adopts the current scalar
   entries into `.harness/runs/prompt-slots-baseline.json` (class-D,
   machine-local, gitignored). Adopting IS the owner's review act.
3. **Drift surfaces in the doctor.** `repo_health.checks` carries a
   `prompt-slots` row: missing baseline -> warn (adopt nag — an unreviewed
   instruction channel is the disease); new/changed/removed vs baseline ->
   warn naming entry ids; match -> ok. Fail-open at every layer: an
   unreadable account file or a broken reader is a non-signal, never a raise.
4. **Drift is recorded.** A detected drift appends ONE ledger note (tags
   `prompt-slots`+`sec8`) with entry ids and counts only, so behavior later
   attributable to a slot is explainable after the fact.
5. **Never edit.** No code path writes to `~/.claude.json`. Counteracting a
   slot is an owner decision (a standing grant in owned instruction files),
   out of scope here.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Detect+surface, never edit | backlog `SEC.8` (owner 2026-07-26): slot é cache servida sob chave opaca — escrever nela não é alavanca durável; o grant local do dono neutraliza slots condicionais |
| Hashes/ids only, nunca texto | `~/.claude.json` é estado de conta; o piso de privacidade espelha o padrão do secret_scan (redigir, nunca ecoar) |
| Baseline snapshot+diff | padrão de `protect_canonical_files.py` + `.harness/protected-files.snapshot.json` — o mesmo desenho para a mesma doença |
| Surfacing via doctor WARN | idioma de `tools/hooks/overseer_model_guard.py`: doutrina sem mecanismo deriva invisível; o doctor é a superfície sem tocar hooks protegidos |

## Test strategy

- Behaviors: fixture claude.json (self-check tempdir) exercita read/snapshot/
  diff/doctor nos braços missing-baseline, clean, changed, new, removed;
  privacy floor assertado no fixture E na superfície viva (sec8-3).
- Edge cases: arquivo ausente/ilegível (fail-open []), data não-dict, valores
  aninhados (ignorados por desenho), bool/num como scalar hasheado.
- Regression risks: vazamento de texto em qualquer output (assertado duas
  vezes); doctor raise (shape fail-open com try/except no repo_health).
- Coverage: `sec8_prompt_slots.py` sec8-1..sec8-3 no gate de cenários.

## Ceilings (upgrade paths)

- ~~SessionStart surfacing (hook leg) DEFERRED~~ — SHIPPED via amendment v2
  (owner authorized 2026-07-29).
- Entry classification (instruction-bearing vs flags) is deliberately NOT
  built: hashes treat every scalar equally; the owner judges on review.

## Validation

- `python scripts/harness_lib/prompt_slots.py` — module self-check.
- `python testing/scenarios/sec8_prompt_slots.py` — sec8-1..sec8-3.
- `python scripts/harness_lib/prompt_slots.py --snapshot` / `--diff` — the
  operator surface (adopt / inspect).

## Amendments

### v3 — value identity, tri-state read, one predicate (2026-07-29)

Alarm fatigue was killing the control: the client mints a fresh opaque
`bi1-*` key per session/model and evicts old ones, so key churn around an
IDENTICAL value warned every session (live case: 12 keys carrying the same
`cedar_basin` sha), and a torn read of `~/.claude.json` surfaced as
"removed=21". Changes, all inside the existing surfaces:

1. **Identity is the value pair `(name, sha)`, never the slot key.**
   `diff()` reports `new`/`removed` at name granularity and `changed` as
   `name@sha` (a known name under a sha the baseline has never reviewed).
   Pure key churn — same pair under a fresh key — is TOTAL silence: no warn,
   no ledger note, no re-snapshot needed. Ceiling, declared: eviction of one
   key while the same pair persists elsewhere is invisible by design (cache
   semantics, not an instruction change).
2. **Unreadable ≠ empty.** `read_slots` is tri-state: missing file → `[]`
   (legitimate no-slots), any read/parse failure → `None` (torn in-place
   rewrite by the client). `diff` marks `unreadable: true` with empty lists
   (non-signal), and `snapshot()` REFUSES to adopt an unreadable read so a
   torn moment never clobbers the reviewed baseline (extends rule 2).
3. **One predicate.** `alerts(delta)` is the single drift interpretation both
   surfaces consume (doctor row + SessionStart hook); each keeps only its
   wording.
4. **Counter-lever ratified.** The owner's standing delegation grant
   (AGENTS.md "Model/reasoning policy" + `overseer-warmup.md` anchor 6)
   satisfies vendor slots that gate subagent/workflow use on a user request —
   the durable revert for the 2026-07-26 suppression incident; the `changed`
   warn on that slot's name is the signal this amendment preserves.

Teeth: self-check arms (churn-silent, unreadable-silent, snapshot-refusal,
`name@sha` warn, name-level removed) in `prompt_slots.py` `_demo` + the hook
`--self-check`; `sec8-5` pins baseline byte-identity across a doctor warn.
Mutants (2026-07-29, each red in one check): key-identity revert → churn arm;
tri-state removed → torn arm; doctor self-adopt → sec8-5; `alerts` dropping
`changed` → hook drift arm.

### v2 — the push half: SessionStart surfacing, owner-authorized (2026-07-29)

The doctor row is pull (someone must run doctor); the owner ratified the
baseline and authorized the push half in the same decision:
`tools/hooks/prompt_slots_session_surface.py` runs at SessionStart on BOTH
vendor legs (manifest entry `prompt-slots-session-surface` in the protected
`capabilities.json`, edited via the sanctioned
`protect_canonical_files.py edit` flow and rendered with `agents pair
--apply`; the owner reviewed the diff live). Behavior: SILENT when the live
slots match the reviewed baseline (zero context cost) or on any error
(fail-open); on drift it prints entry IDS only (privacy floor holds) and
records the drift in the ledger — so an injected instruction is surfaced in
the very session whose behavior it might alter. Teeth: hook `--self-check`
(adopt-nag, silence-when-clean, drift wording, no-text-leak, torn-baseline
fail-open) wired into `hk_hook_selfchecks._TARGETS`; `sec8-4` pins the
manifest entry + both legs; the SPEC-113 parity gate check owns
manifest↔adapter render equality.
