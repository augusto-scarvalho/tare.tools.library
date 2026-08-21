# Chat-mined spec recovery (DRAFT — NON-CANONICAL)

Recovered by pre-digesting Claude Code session JSONL transcripts (owner's own words,
Portuguese mostly, translated below) and mining them for requirement-shaped asks that
never made it into `specs/`, `testing/`, or `docs/spec-recovery/INDEX.md`'s 60 rules.
Nothing here edits `specs/`, `testing/`, `AGENTS.md`, `CLAUDE.md`, or `.harness/`.

**Method:** wrote `digest.py` (scratch, not committed) to walk every session JSONL under
the 4 named `.claude/projects/*` dirs and extract user turns + first-line assistant
replies, redacting secret-shaped strings. Found and fixed a real data bug along the way:
raw session files store some user-typed text **double-UTF-8-encoded** ("PendÃªncia" for
"Pendência") — the digester now undoes one layer before quoting, so quotes below are the
owner's actual words, not mojibake.

**Corpus:** 108 sessions (`...multi-agent-harness...` dir) spanning 2026-07-09 03:41Z
through 2026-07-13 05:42Z (the *entire* recorded project history is 5 days), plus 1
session each in the other two named dirs (both trivial, 1 real turn each — "diga um oi",
"diga ok se estiver lendo") and today's session (lower priority per instructions, its
asks are mostly already landed per HEAD commits).

**Coverage:** keyword-swept all 108 digests for requirement language (quero/não
pode/sempre/nunca/tem que/garantir/gostaria/idealmente/no futuro/etc.), which surfaced
~10 candidate-dense sessions out of 108 (most of the corpus is turn-by-turn "pode
seguir"/"continue" execution chatter with no fresh asks). Fully read the two smallest
sessions (d1, d2) plus `b07180e2` (2026-07-13, decisions session — richest single
source), `afb3599a`/`3d3b2773` (same conversation across a `/compact` boundary,
2026-07-09), and grep-scanned with context the remaining large candidates (`f7f54eb1`,
`9273e9d1` — 2025/10105 lines each — `6d9f82b6`, `dfd37ee8`, `d5c3d9de`, `a450e835`,
today's `84ccb2bf`). **Skipped**: the ~98 non-candidate sessions in the 108-session dir
(execution-only, no fresh requirement language found by the keyword sweep) and the
non-matching portions of the two giant files beyond the grepped hits — bounded by
volume per instructions, newest-first priority already applied since the corpus itself
skews recent (last 2 days = the richest decision-making, all captured).

## Recovered asks

### GUI / panel

| # | Recovered ask (owner's words → testable rule) | Source | Status today | Risk | Recommended action |
|---|---|---|---|---|---|
| cm-1 | Model/profile selector bug: owner selects a repo+profile ("printintel"/"personalizado") in the top-of-UI selector, but asks the chat "which model am I talking to" and the overseer answers a different model (fable 5); the badge above the input also shows the wrong model. Owner's words: *"acho que esse option não tá fazendo efeito quando seleciono e salvo."* | `f7f54eb1` (session, undated-within-file line ~1062) | **unclear — looks like a live correctness bug**, not found addressed in `IMPLEMENTATION_BACKLOG.md` or INDEX.md | **H** (UI lies about which model/effort is actually running — supervision-safety relevant) | Reproduce: select a non-default profile in the GUI selector, ask the chat "which model", compare against `activeProfile`/routing resolution actually used for that turn. If confirmed live, this is a correctness bug, not just a gap — file it, don't just spec it. |
| cm-2 | Plan→execution mode auto-transition: *"quando aprovarmos um plano, tiramos o modo de plan pra 'auto' ou 'aprove edits' de acordo com as configurações do usuário"* — after a plan is approved, the tool should auto-switch the permission mode per the user's own configured preference, not require a manual Shift+Tab / `/approve` every time. | `b07180e2`, 2026-07-13 04:46Z | shipped-but-diverges — commit `9c50dbf` landed the plan/question event contract + `/approve` command + `postPlanMode`, i.e. explicit approval capture, but the *automatic* mode-switch-per-user-preference (a config knob, not a manual command) isn't evidenced in the backlog or specs | M | Confirm whether `/approve` is manual-only today; if so, add the "auto per saved preference" knob as a follow-up, or document `/approve` as the deliberate final answer and close the gap |
| cm-3 | Same message, second half: owner wants plan-mode "option select" events (the ones Claude/Codex CLI show when a plan asks the user to pick between options) to become a **predictable, capturable contract** so the harness UIs can render them as a form, "replicando aquilo que hoje aparece nas telas da CLI/GUI do codex/claude." | `b07180e2`, 2026-07-13 04:46Z | **CLOSED — verified shipped (overseer Q5, 2026-07-13 PM)**: `stream_json.tool_descriptor` carries structured AskUserQuestion input → backend derives the `question` event → GUI renders sequential option modals and answers flow back as messages (`harness_ui_page.py:1441-1494`, P8/9c50dbf). Residual = codex-engine side only, already tracked as the `codex-stream-parity` backlog row | L | none — closed |
| cm-4 | Ledger UX: owner doesn't know what the ledger feature is for anymore — *"ledger ainda serve pra algo, nÃ£o tem nada entrando / sendo atualizado, atÃ© esqueci pra que serve a feature."* | `b07180e2`, 2026-07-13 04:20Z | inferred shipped (cost ledger + session dimension landed per commit `9c50dbf`/`105af37`) but the owner's *comprehension* gap (UI doesn't make the feature legible) may persist | L | Add a one-line "what is this" affordance/tooltip to the ledger panel; low-risk UX debt, not a missing feature |
| cm-5 | Stray black terminal windows spawning on the owner's machine while the harness runs (GUI, CLI, or via Claude/Codex): *"vejo que telas de terminal pretas spawnando de vez em quando no meu computador. Isso tem me atrapalhado. Quero que investigue."* | `9273e9d1` (2026-07-1x session), line ~4796 | shipped-but-diverges — `processes.py`/`async_runtime.py`/`services.py` already set `CREATE_NO_WINDOW`, but INDEX.md rec-wf-19 independently found that `workflow_writes.py` git-worktree prepare/cleanup uses **direct** `subprocess.run` outside that mediation layer — this is almost certainly the root cause the owner is seeing | M | This ask corroborates rec-wf-19 as a real, felt bug (not just a ratchet-debt curiosity) — route worktree subprocess calls through the `processes.py` CREATE_NO_WINDOW-safe layer |

### Chat / process

| # | Recovered ask | Source | Status today | Risk | Recommended action |
|---|---|---|---|---|---|
| cm-6 | Automated spec-drafting hook, **with triage**: *"quero que pesquise como seria feito um hook de marcação pra escrita de specs quando o usuário faz pedidos. lembrando que nem todo pedido vira uma spec, ele deve ser triado e só então usado para criar/atualizar artefato sdd/bdd."* | `f7f54eb1`, line ~1831 | **never-shipped** — this is precisely the gap that made this very Phase-2 archaeology task necessary (60+ asks scattered across 108 sessions, never triaged into specs as they happened) | **H** (process/meta — the absence of this is *why* spec drift accumulated) | Design a lightweight triage hook/command: after a user turn that reads as a durable requirement (not a one-off "continue"/"pode seguir"), prompt "does this belong in specs/backlog?" before landing code. Cheaper than another archaeology pass later. |
| cm-7 | Codex should join the **autonomous backlog-implementation loop**, not just be usable interactively via chat: *"quero que você resolva esses problemas com o codex antes porque queria que você adicionasse ele ao nosso loop de implementação de backlog."* | `84ccb2bf` (today's session), line ~2474 | never-shipped — `codex-stream-parity` is acknowledged in INDEX.md as an open backlog row (M/P2), but that row is scoped to chat chips/plan HUD parity; this ask is the larger "Codex as a loop worker" scope, which is a superset | M | Distinguish the two asks explicitly in the backlog: (a) chat UI parity for Codex [already tracked], (b) Codex as an autonomous-loop-eligible executor [not tracked as its own item] |
| cm-8 | Keys/secrets phase-2 acceptance criteria (fuller than the one-line backlog decision): keyring-backed vault with **cascade `env → keyring → .env`**, `keys set` **via stdin only** (never as a CLI arg, to avoid shell-history/process-list leakage), GUI write path as an **allowlisted action with confirm + audit trail in records**, and `keys list` gaining **`backend` and `lastRotated` columns**. | `b07180e2`, 2026-07-13 03:53–03:59Z | **never-shipped** — commit `32781a8` logged only the *decision* ("keys via keyring vault"); the acceptance criteria quoted here (stdin-only set, audit trail, backend/lastRotated columns, explicit cascade order) aren't restated anywhere and phase 2 is explicitly still open ("fase 2 agora é o backend keyring... a GUI depende dessa fase 2") | M | When phase 2 is implemented, use this quote as the acceptance-criteria source — the decision commit alone under-specifies it |

## Skipped / not carried forward (already covered or not durable rules)

- Browser-can-start-agent-work, security-diff-routing route + FP registry, tasks.json
  canonical + TE.5 reuse, TodoWrite headless allowlist — all decided **and logged** the
  same day in commit `32781a8`; not gaps, just decisions awaiting phase-2 implementation
  already tracked in `IMPLEMENTATION_BACKLOG.md`.
- Chat markdown rendering, multiline textarea (Shift+Enter), paste framing, model-cards
  registry, REPL onboarding/menu UX, fuzzy `@file` finder, syntax highlighting — all
  explicitly shipped per commit messages (`260a903` SPEC-111, `105af37`/`9c50dbf` P1-P8).
- "Harness rules must also apply to the target repo the agents write in, not just
  itself" (`3d3b2773`, 2026-07-09 23:22Z) — already canonical: `specs/40-features/
  harness-target-governance.md` exists and appears to cover exactly this.
- Self-evolving/self-critiquing harness framework (`afb3599a`, 2026-07-09 21:50Z) —
  the "SE" milestone is marked done in the owner's own backlog status line.
- Worker-drill-in-drawer to see live subagent activity (`9273e9d1`, early lines) — this
  is rec-gui-1 in INDEX.md (now built, but flagged there for a real secret-redaction
  bug) — duplicate, not carried forward separately.
- One-off requests with no durable rule shape: audit-effectiveness-of-opus-subagent-
  strategy, token-cost investigations, ad-hoc `/research` topic requests, "diga um oi" /
  "diga ok" liveness checks.

## Top-10 worth judging together

1. **cm-1** — model/profile selector may be silently ignoring the user's choice (UI
   shows wrong active model). Reproduce first; if real, treat as a bug, not a spec gap.
2. **cm-6** — no automated spec-triage hook exists; this is the root cause of needing
   Phase 1 + Phase 2 archaeology at all. Worth building once, even minimally.
3. **cm-5 / rec-wf-19** — stray console windows corroborated as a felt, reported
   annoyance, not just a ratchet-debt line item; raises its priority.
4. **cm-8** — keyring phase-2 acceptance criteria are richer than the logged decision;
   don't let implementation drift from what the owner actually specified.
5. **cm-7** — "Codex in the autonomous loop" is a bigger ask than the tracked
   `codex-stream-parity` backlog row; decide if it's in scope or explicitly deferred.
6. **cm-2** — confirm whether plan-mode auto-transition-per-preference was ever built,
   or whether `/approve` (manual) is the intended final answer.
7. **cm-3** — option-select-as-GUI-form: distinct from the plan/approve event contract;
   check SPEC-133 for whether this half shipped.
8. rec-gui-1 (INDEX.md, restated) — the secret-redaction gap in the worker drawer is
   still the single highest-risk finding across *both* archaeology passes.
9. rec-cli-1 (INDEX.md, restated) — exit-code contract untested end-to-end; independent
   confirmation this session corpus didn't surface a contradicting owner expectation.
10. **cm-4** — low-risk but real: the owner forgot what a shipped feature (ledger) is
    for. A UX legibility problem, not a missing-feature problem — cheap to fix, easy to
    keep deferring.

## Summary

- **Sessions processed in depth**: ~11 of 111 total (108 main + 3 satellite), prioritized
  by requirement-language density found via keyword sweep across the full 108-session
  corpus, then by recency within that set.
- **Sessions skipped**: ~97 in the main dir (keyword sweep found no fresh requirement
  language — mostly "continue"/"pode seguir" execution turns) plus the un-grepped
  remainder of the two largest files.
- **Asks recovered**: 8 (cm-1…cm-8), of which 3 look genuinely never-shipped (cm-6,
  cm-7, cm-8), 1 looks like a live correctness bug worth reproducing (cm-1), 3 are
  shipped-but-diverging in scope or UX legibility (cm-2, cm-3, cm-4), 1 corroborates an
  existing INDEX.md gap with a real user complaint (cm-5).
- **Data-quality note**: fixed a double-UTF-8-encoding bug in user-turn text during
  digesting (not present in assistant text) — worth knowing if anyone else mines these
  transcripts directly.
