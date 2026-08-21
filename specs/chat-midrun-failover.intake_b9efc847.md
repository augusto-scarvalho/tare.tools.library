# Intake refinement -- chat mid-run failover (door NEW)

SPEC-116 invariant 2 checklist. Seeds SPEC-166
(`specs/40-features/chat-midrun-failover.md`). Follow-up committed in
SPEC-165's intake (owner decision 4, 2026-07-21).

## Request (verbatim)

> vamos de follow-up
> (= the follow-up spec named in `compat-executor-routing.intake.md` owner
> decision 4: "Chat mid-run failover. Follow-up spec, out of scope here" --
> the SPEC-115 gap surfaced in the 2026-07-21 fallback-chain status review:
> chains fire only at engine CONSTRUCTION; a rate-limit mid-conversation
> strands the session until a manual /config.)

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search chat midrun failover runtime` | no hit -- `[]` |
| doc-find | `python scripts/harness.py doc-find chat engine failover mid-run rate limit rebuild` | hits are chat-contract handoffs (q3/q11) and the chat-operator recovery draft -- adjacent, none owns mid-run failover |

Adjacent ground that EXISTS but does not cover: SPEC-115 (construction-time
walk only, `build_engine` chat_engines.py:842-881); SPEC-165 R7 (worker SPAWN
boundary, explicitly ceilinged "mid-run death is the workflow retry layer's");
the async origin-executor failover (workers, not chat).

Decision: **NEW**.

## Owner decisions (2026-07-22, AskUserQuestion)

1. **Cross-vendor continuity = digest re-injection.** The new engine is born
   with a BOUNDED digest of recent turns; same-vendor hops keep the native
   lossless resume (claude `--resume <session_id> --model <hop>`, codex
   `exec resume <thread_id>` -- vendor stores survive a model change within
   the vendor).
2. **Auto-retry 1x.** The unanswered turn that triggered the failover is
   re-sent ONCE on the new hop, after a one-line notice.
3. **Sticky until /model.** No automatic return to the primary; cooldown
   probing is a declared ceiling.

## Goal

One sentence: a chat turn that fails with a classified rate-limit/quota/auth
error walks the role's fallback chain MID-CONVERSATION -- native resume within
the same vendor, bounded-digest re-injection across vendors -- retries the
failed turn once on the surviving hop, tells the operator in one line, and
stays there until an explicit /model.

## Scope

In scope:
- Turn-failure classification at the operator/engine boundary reusing the
  executors' `runtimeLimits` patterns (the SPEC-165 `_classify_spawn_failure`
  precedent; lift shared logic if needed, no second pattern table).
- The mid-run walk: `chat_fallbacks(role)` hops AFTER the current one;
  same-vendor hop = rebuild with the surviving session/thread id + new model;
  cross-vendor hop = `build_engine`-style construction + digest injection.
- Digest source: the operator's own turn log (the same harness-side transcript
  the GUI chat tab renders; OpenAIEngine already proves harness-side
  transcripts -- `self.messages`). Bounded (last N turns / char cap).
- Auto-retry of the failed turn exactly once per failover event; a second
  classified failure on the retry advances to the next hop (chain exhaustion
  = the current legible error, session stays manual).
- One stderr/chat notice per hop (build_engine's `[routing]` shape) + HUD
  engine label update; SPEC-146 room tools + SPEC-118 contextDiet ride the
  rebuild (build_engine already splices both).
- Sticky semantics + /model as the return path.

Out of scope:
- Automatic return-to-primary (cooldown probing = ceiling).
- Worker/spawn failover (SPEC-165 R7 owns it) and async workers.
- New GUI surface: the notice reaches the GUI chat tab through the existing
  message plumbing; no GUI code changes -> Gherkin optional (SPEC-116 inv. 4
  judgment recorded here).
- Transport-level retries within a turn (timeouts, connection resets) --
  only CLASSIFIED failures walk; everything else keeps today's error surface.

## Actors & surfaces

- Actors: chat operator loop (`chat_operator.py`), engines
  (`chat_engines.py`: Claude/Codex/OpenAI + codex_appserver), model routing
  (`chat_fallbacks`), runtimeLimits registry.
- Surfaces: CLI chat REPL (+ GUI chat tab inherits display). UI surface?
  **no new UI code** -> Gherkin optional.

## Proposed acceptance criteria

- [ ] A turn whose failure text matches the current engine's executor
  rate-limit/quota/auth patterns triggers the walk; unclassified failures do
  NOT (today's error surface preserved).
- [ ] Same-vendor hop: the rebuilt engine keeps the vendor session/thread id
  (claude `--resume` / codex `resume`) with the hop's model/effort -- history
  lossless.
- [ ] Cross-vendor hop: the new engine receives a bounded digest of the
  operator's turn log; the digest never exceeds its declared cap.
- [ ] The failed turn auto-resends exactly once per failover event; its
  answer arrives on the new hop; a classified failure on the retry advances
  the walk.
- [ ] Chain exhausted mid-run -> legible error, engine unchanged, manual
  /config-/model recovery exactly as today.
- [ ] One notice per hop + HUD label reflects the surviving engine; room
  tool patterns and contextDiet are re-spliced on rebuild.
- [ ] Sticky: no automatic return; /model restores the primary.
- [ ] Canonical profile (empty chain) -> mid-run behavior byte-identical to
  today (no walk, no retry).

## Risks / blast radius

Medium: touches the chat operator's turn loop (central interactive surface)
and engine construction plumbing; digest injection adds a prompt-shape
surface (keep it a plain system/user preamble, no new contract). Retry loops
are bounded by construction (once per event, hops advance monotonically).
Rollback: the walk sits behind the chain being non-empty -- canonical
sessions never enter the new code path.

## Open questions for the human

None -- the three design decisions above close the ones that mattered
(continuity, retry, return). Digest cap size is an implementation constant
with a `ponytail:` ceiling note, not an owner decision.
