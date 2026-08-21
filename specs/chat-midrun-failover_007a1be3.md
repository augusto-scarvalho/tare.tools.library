# SPEC-166 — Chat mid-run failover: the chain completes the loop

Status: SPEC-166, proposed 2026-07-22 (acceptance:
`testing/scenarios/cmf_chat_midrun_failover.py`, lands with the
implementation).

Intake (SPEC-116 door NEW, from
`specs/40-features/chat-midrun-failover.intake.md`): the follow-up committed
in SPEC-165's intake (owner decision 4). Three owner decisions
(2026-07-22) govern it: cross-vendor continuity = bounded digest
re-injection; auto-retry exactly once; sticky until /model. Closes the
SPEC-115 gap its own docstring promised away: `executors.json.runtimeLimits`
classifies rate-limit/quota/auth (detect), and until now the chain only
"completed the loop" at engine CONSTRUCTION — a mid-conversation rate-limit
stranded the session until a manual /config.

## Goal

A chat turn that fails with a classified rate-limit/quota/auth error walks
the role's fallback chain mid-conversation — native session resume within the
same vendor, bounded-digest re-injection across vendors — retries the failed
turn once on the surviving hop, tells the operator in one line, and stays
there until an explicit /model.

## Applicability

`harness_lib/chat_operator.py` (turn loop), `harness_lib/chat_engines.py`
(engine rebuild seams; Claude/Codex/OpenAI + codex_appserver),
`harness_lib/model_routing.py` (`chat_fallbacks` consumption — read-only),
the executors' `runtimeLimits` registry (read-only). Explicitly NOT covered:
worker/spawn failover (SPEC-165 R7), async workers, automatic
return-to-primary (ceiling), transport-level retry within a turn
(unclassified failures keep today's error surface), new GUI code (the notice
reaches the GUI chat tab through existing message plumbing — Gherkin
optional, judgment in the intake).

## Requirements / invariants (numbered, testable)

1. **Classified failures only.** A turn whose failure text matches the
   CURRENT engine's executor `runtimeLimits` rate-limit/auth/quota patterns
   (the SPEC-165 classification precedent — one shared pattern table, never a
   second) triggers the walk. Unclassified failures surface exactly as
   today.
2. **Walk order.** Hops come from the role's chain (`chat_fallbacks`)
   AFTER the current hop; each hop is attempted at most once per failover
   event; the walk never revisits an earlier hop.
3. **Same-vendor continuity is lossless.** A hop on the same engine vendor
   rebuilds with the surviving native session (claude `--resume
   <session_id>`, codex `resume <thread_id>`) and the hop's model/effort —
   conversation history preserved by the vendor store.
4. **Cross-vendor continuity is a bounded digest.** A hop on a different
   vendor constructs the engine `build_engine`-style and injects a digest of
   the operator's own turn log, capped (turns + chars) by a declared
   constant; the digest is plain preamble content, never a new contract
   surface.
5. **Auto-retry once.** The unanswered turn re-sends exactly once per
   failover event on the surviving hop; a classified failure on that retry
   advances the walk (which re-arms the single retry for the NEXT hop);
   anything else is that turn's answer.
6. **Exhaustion is legible and inert.** A chain exhausted mid-run yields the
   legible error, keeps the current engine, and leaves recovery manual
   (/config, /model) — exactly today's stranded-state UX, minus silence.
7. **Notice + label.** One `[routing]`-shaped notice per hop; the HUD engine
   label reflects the surviving hop; SPEC-146 room tool patterns and
   SPEC-118 contextDiet are re-spliced on every rebuild (build_engine
   already owns both splices).
8. **Sticky.** No automatic return to the primary; /model (or /config)
   restores it. Cooldown probing is a declared ceiling, not behavior.
9. **Canonical byte-compat.** Under the canonical profile the chain is empty:
   no walk, no retry, mid-run behavior byte-identical to pre-SPEC-166.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Classified-only trigger, one shared pattern table | `executors.json.runtimeLimits` (SPEC-115 grounding line: "detect… the chain completes the loop"); SPEC-165 `_classify_spawn_failure` precedent (harness.py) |
| Same-vendor native resume | `ClaudeEngine.session_id` + `--resume` (chat_engines.py:264-322), `CodexEngine.thread_id` + `exec resume` (:457-516) — vendor stores survive a model change within the vendor |
| Cross-vendor digest re-injection | Owner decision 1 (2026-07-22); `OpenAIEngine.self.messages` (chat_engines.py:741) proves harness-side transcripts; digest over replay = bounded cost |
| Auto-retry once | Owner decision 2; a failover that drops the triggering turn forces the user to repeat themselves — one bounded retry, monotone hop advance prevents loops |
| Sticky until /model | Owner decision 3; automatic return risks engine ping-pong under flapping providers |
| Construction walk precedent | `build_engine` (chat_engines.py:842-881): hop loop, one notice per hop, room/diet splices |

## Ceilings (upgrade paths)

- Digest cap is a constant (`ponytail:` note at the definition); make it
  configurable only if a real transcript overflows it usefully.
- Cooldown probing / automatic return: add only with evidence of long
  sessions stranded on expensive fallbacks.
- Transport-error (timeout/reset) failover: deliberately excluded; revisit
  with evidence of provider flaps that classification misses.

## Test strategy

- Behaviors: classified trigger walks / unclassified does not; same-vendor
  resume carries session id + new model into the rebuilt argv; cross-vendor
  digest present + capped; single retry per event; exhaustion legible +
  engine unchanged; notice per hop; sticky; canonical no-op.
- Edge cases: failure on the retry itself (advances walk); chain with only
  same-vendor hops; empty turn log at digest time; classified failure text
  arriving via stderr vs finalText.
- Regression risks: chat construction walk (build_engine) untouched
  semantics; REPL error surface for unclassified failures; codex_appserver
  transport variant.
- Coverage impact: enforced via the new scenario + existing chat batteries.

## Validation

- `python testing/scenarios/cmf_chat_midrun_failover.py` — the acceptance
  scenario (checks `cmf-*` covering rules 1-9), landing WITH the
  implementation; stub engines / temp-root routing per the cer2/cer5
  hermetic patterns.
- Existing chat batteries rerun green: the chat-contract scenarios named in
  Test strategy, `m5_ui_panel`, `mr_model_routing`.

## Amendments

(none yet)
