# SPEC-172 — Vendor environment acceptances (ask the vendor, drive the yes)

Status: SPEC-172, proposed 2026-07-29 (acceptance: `testing/scenarios/vf_acceptances.py`).

## Goal

Surface, inside the harness, every guard a vendor is SILENTLY skipping until the
owner accepts it — and let the owner give that acceptance without opening a TUI
they do not know how to drive.

The motivating fact (2026-07-29): codex had been running this repo's hand-typed
lanes with EVERY one of its 12 hooks inert — `agent_spawn_economy` (the
cost-incident guard) and `gate_hold_guard` (the write-during-gate guard) among
them — and the only surface that said so was an interactive prompt the owner had
never opened. **An acceptance nobody can see is an acceptance nobody gives.**

## Applicability

- `scripts/harness_lib/acceptances.py` — the probe, the drive loop, the plan.
- `scripts/harness_lib/screen_reader.py` — the generic screen reader and
  `authorize_keystroke`, the single authority that may permit a keystroke.
- `scripts/harness_lib/pty_drive.py` — the OPTIONAL pty transport.
- `scripts/harness_lib/processes.popen_with_tty` — the POSIX half of that transport.
- The `acceptances` verb (registered thin in `harness_lib/cli_registry.py`).

Sibling, not overlap: **SPEC-171** solves the same skipping for *harness-spawned*
codex lanes by proving `.codex/hooks.json` is the harness's own gated render and
passing `--dangerously-bypass-hook-trust`. SPEC-171 explicitly leaves interactive
human sessions and hand-typed recipes to "codex's own trust prompt". SPEC-172 is
that leftover path — and it is the path this session's lanes actually used.

## Requirements / invariants (numbered, testable)

1. **Ask the vendor; never re-derive.** Pendency comes from the vendor's own
   non-interactive interface — `hooks/list` over the `codex app-server` JSON-RPC
   transport `codex_appserver.py` already uses. Zero new dependencies, no pty for
   the read. A first draft diffed `~/.codex/config.toml` by hand and reported 3
   pending of 12; the vendor's answer was **12 of 12** (3 `untrusted`, 9
   `modified`), because a stale `trusted_hash` is indistinguishable from a live
   one from outside and the hash recipe is undocumented (SPEC-171 puts persisting
   it out of scope for the same reason).
2. **Classification.** `trustStatus ∈ {trusted, managed}` runs; `untrusted`
   (never accepted) and `modified` (accepted once, hook changed since) do not.
   Hooks whose `sourcePath` is not inside this repo are out of scope, tested by
   PATH semantics — a `startswith` also matches a sibling `…-prototype-EVIL`
   checkout. A DISABLED hook is counted separately and never reported as pending:
   accepting it would not make it run.
3. **Two mechanisms, one consent.** `visible` hands the owner the exact command;
   `headless` types the yes into a hidden pty. Consent is the owner's click, given
   before either runs. The drive NEVER decides to accept anything.
4. **The screen reader is deliberately dumb.** It receives raw screen text plus a
   generic intent and returns literal options. It is told nothing about codex, or
   hooks, or this repo. The screen is HOSTILE third-party DATA — described, never
   obeyed — sanitized of ANSI and Unicode `C*` categories, NFKC-normalized and
   capped at 8000 chars before the model or the rail sees it.
5. **`authorize_keystroke` is the only authority, and it is grounded.** A safe key
   alphabet alone is NOT a consent binding: the authorized alphabet *is* the
   confirm alphabet, so an adversarial reader could answer yes to whatever prompt
   is up, one key per iteration. So the verdict's `questionText` and the matched
   option's `label` must appear LITERALLY in the sanitized screen, and the drive
   carries a send budget. Both fail closed: no screen and no budget mean no key.
6. **Normalization happens on the way IN.** A live TUI advertises `Enter`, not
   `enter`. The reader PROMPT asks for a normalized key from a fixed vocabulary;
   the check itself is never loosened. Widening the accepted alphabet in
   `authorize_keystroke` is a SECURITY change requiring a fresh audit.
7. **Every key vocabulary has an encoding.** `pty_drive.KEYS ∪ {y, n}` equals
   `screen_reader._SAFE_KEY_NAMES` exactly. Drift would make the transport type a
   literal word (`pgup`) into a vendor prompt, and is otherwise live-only.
8. **The answered screen is forgotten, BEFORE the key goes out.** `PtySession.clear()`
   is a rail, not housekeeping: a carried-forward screen would let text the owner
   already dismissed ground a verdict about a LATER question. It runs before `send()`
   because the pump thread can capture the vendor's reply in the gap between the two,
   and clearing afterwards would wipe the screen the next iteration must read.
9. **Success is re-asked, not assumed — after EVERY keystroke.** The drive re-probes
   `hooks/list` following each authorized key and stops the instant the answer is
   "nothing pending". What a screen appeared to say and what the vendor recorded are
   different facts; only `verified` reports `accepted`. Probing only at the end let
   the drive keep answering screens after its objective was already met.
10. **The budget bounds keys spent WITHOUT progress.** Because invariant 9 stops the
    drive on success, `DRIVE_BUDGET` is not "how long the job takes" — it is the
    ceiling on answering screens that are NOT the one the owner consented to, and is
    kept small for that reason. See Ceilings: the reader is generic by design, so
    any confirm-shaped screen resembles the target one.
11. **Visible is the floor.** Any other outcome — no pty, unreachable reader,
    denied verdict, exhausted budget, vendor still pending — returns the visible
    plan as `fallback`. There is no dead end.
12. **Optional by design.** POSIX drives the pty with the stdlib; nt needs
    `pywinpty` and falls back to visible when it is absent. Never a hard
    dependency, never an error. `popen_with_tty` refuses legibly on nt instead of
    surfacing a bare `No module named 'fcntl'`. The requirements marker
    (`pywinpty; os_name == "nt"`) is load-bearing: pywinpty wraps Windows' own
    ConPTY and has no Linux or macOS wheel, so an unmarked line breaks the CI matrix.
12b. **"Painted" means VISIBLE text, not bytes.** ConPTY opens every session with a
    handshake of pure escape sequences and delivers the child's real output on its
    own repaint cadence — measured up to ~8s later, not on the child's write. A
    screen is settled only once `sanitize()` finds text in it, or the vendor is gone.
    Counting handshake bytes as a screen made the headless flow fall back to visible
    on Windows EVERY time, silently, because a blank screen is refused for the same
    reason a finished one is. Found by running it live, not by reading it.
13. **Provenance, or an honest admission.** Every drive writes
    `.harness/runs/acceptance-<vendor>-<ts>-<pid>.json` with each step's SANITIZED
    screen, verdict and decision — the exact text the rail judged. When the record
    cannot be made durable, `transcript` is `null` and a `transcriptWarning` says so:
    reporting a path that did not survive is worse than admitting nothing was kept.
    The pid is in the name because two drives in the same second must not overwrite
    each other's only audit record.
14. **Never drive into a held gate — checked twice.** `common.gate_holding` refuses
    the drive at the start AND again immediately before the transcript write: the
    hold swaps the live tree, and a hold that begins mid-drive would otherwise
    discard the record of keystrokes that really happened.
15. **The launch argv is absolute.** Windows `CreateProcess` searches the app dir
    and cwd before PATH, so a `codex.bat` dropped in the repo would win over the
    real binary. The bare vendor name is a last resort only.
16. **`--dry-run` short-circuits ahead of every action path.** The one flag whose
    whole contract is "sends nothing" must not inherit a false promise from a
    later branch.
17. **Pendency is PUSHED at session start, not only pulled.** The `acceptances`
    verb made the question answerable; `tools/hooks/acceptances_session_surface.py`
    (SessionStart, both adapters, rendered from `.harness/capabilities.json`) makes
    the answer arrive in the session whose guards are missing, naming the inert
    hooks by script — a session running without `agent_spawn_economy` otherwise
    looks identical to a healthy one. It SURFACES and never grants: an agent that
    accepted on the owner's behalf would make the harness the grantor of trust in
    its own hooks, which is exactly what invariant 3 exists to prevent, so the line
    names both commands and says whose call it is. Silent when clear, when the
    vendor is absent or unreachable, and under a gate hold — there the live tree is
    the STAGED one, so a `modified` trustStatus is an artefact of the hold, not
    news. Fail-open always. The round trip carries a seconds-scale `budget_s` (ONE
    total wall clock split across the two RPC legs; `budget_s=0` must not fall back
    to the default) because the CLI's generous ceiling is a hang at session start.
18. **The panel asks, and the click IS the consent.** The decision inbox
    (`decision_inbox._acceptance_rows`) carries one row per vendor with inert hooks —
    the owner's original ask, *"na tela do usuário aparece a pergunta de se ele aceita
    os hooks"*. Four rules make it safe to answer from a browser:
    - **Never probe to be read.** The collector runs on every panel poll and every
      `decide`, so it reads the CACHED probe (`.harness/state/acceptances.json`,
      written ONLY by `acceptances.refresh`) — never an app-server per poll. Both live
      probers park their answer, which is what keeps the card fresh without anything
      polling the vendor: opening a session refreshes the panel.
    - **An absent cache yields NO row.** "Nobody has asked the vendor yet" and "the
      vendor has nothing pending" are different facts, and only the second may render
      a clear inbox. A torn cache degrades to unknown as well — this file is read by
      every `decide`, so a half-written one must not take down the decisions surface.
    - **The digest binds WHICH hooks.** The row's digest covers the pending set
      (trustStatus, event, matcher, command; sorted), so one more inert hook since the
      card was drawn refuses the click as invalidated rather than spending the yes on
      a set the owner never saw. The panel forwards it as `--expected-digest`.
    - **The cache is a FILE, so its contents are untrusted.** The collector accepts a
      report only when its `vendor` is a registered probe, because an unknown one would
      reach `acceptance_plan` with no probe (a `KeyError` through a contract that
      promises never to raise) and, with codex off PATH, put a cache-supplied string in
      `argv[0]` of a real spawn. A non-numeric `running` must not raise either. The
      browser was never allowed to name a vendor; neither is a file.
    - **Vendor and mode are not the clicker's to choose.** `acceptance-decide` accepts
      exactly `id`, `choice ∈ {accept, keep}` and an optional 64-hex digest, gated by
      `_acceptance_reason` against the LIVE pending inbox before any argv exists. The
      vendor is read off the pending row inside `apply_decision`; the mode is fixed to
      `headless` there. A validated parameter is still a parameter — the way a clicker
      cannot steer a vendor argv is for the argv not to be theirs to steer. A gate in
      flight refuses the click outright, one window wider than the drive's own hold
      check. `keep` is a no-op, and the probe is re-parked after every attempt so a
      finished acceptance stops offering its own button.

## Rationale & sources

- The probe reuses the `vendor_fuel` principle from **SPEC-168**: ask the vendor's
  own non-interactive surface, never fabricate or re-derive. Here that is
  `hooks/list`, over the JSON-RPC transport `codex_appserver.py` already speaks.
- **SPEC-171** covers the harness-spawned half of the same problem and explicitly
  scopes out interactive sessions; this spec is the complement, not an overlap.
- The keystroke rail's shape comes from the R2 security audit (2026-07-29,
  finding H2): a safe key ALPHABET is not a consent binding, because the authorized
  alphabet is the confirm alphabet. Grounding plus a budget is what binds it.
- The second audit (2026-07-29, findings 1–4) produced invariants 9, 10, 13 and 14
  and the screen-tail truncation. Its residual finding is recorded under Ceilings.
- Owner directives, 2026-07-29: both mechanisms with a fallback; the screen read
  dynamically by an agent and filled parametrically; *"probe sempre burrinho, prompt
  genérico, ele não precisa saber o que está fazendo, só ler a tela"*.

## Test strategy

Hermetic and offline. `vf_acceptances.py` never spawns a vendor and never opens a
real TUI: the vendor's `hooks/list` answer is injected as a fixture, the screen
reader is injected as a callable, and the pty session is injected as a fake that
records the ORDER of `clear`/`send` (order is the difference between a rail and a
race, and is invisible unless asserted). Denial conditions are each isolated from
one known-good verdict so a single check cannot pass for six reasons.

Two things cannot be faked and are split accordingly: the pty TRANSPORT is proven
per platform — a real `/bin/echo` round trip on POSIX, a legible `NotImplementedError`
on nt — while the drive LOOP is proven against the fake. Mutation coverage is the
falsifier of record: `harness.py oracle mutate --scenario testing/scenarios/vf_acceptances.py`
caught the `_find_codex() or vendor` → `and` regression (which reopens the bare-name
`CreateProcess` hole of invariant 15) that no assertion had been watching.

## Validation

- `testing/scenarios/vf_acceptances.py` — 45 checks: the rails (invariants 4–8),
  the drive (9–11), degradation and fallback (11–12), provenance and the gate
  double-check (13–14), the launch argv (15), `--dry-run` (16) and the probe budget
  (17) — `vfa-37` proves the budget with a CLOCK against a vendor that connects and
  then says nothing, since a forwarded budget and an ignored one differ only in time.
- `testing/scenarios/hk_hook_selfchecks.py` — runs the session surface's
  `--self-check` inside the gate (invariant 17): silence on clear/absent/failed/held,
  the named-hooks line, ASCII-only output, a raising probe staying silent, and the
  probe actually being PARKED where the panel reads it.
- `testing/scenarios/di_decision_inbox.py` — `di-12` covers invariant 18 with the
  vendor spawn made FATAL during collection (a per-poll app-server is the failure this
  design exists to avoid, and only a fatal stub proves it never happens), absent cache
  yielding no row, the digest invalidating a drifted approval, `keep` as a no-op, the
  four panel-gate refusals, and the built argv carrying neither vendor nor mode.
- `testing/scenarios/m5_ui_panel.py` — the ACTIONS ratchet: `acceptance-decide` is
  declared in the pinned allowlist, so a future browser write path cannot slip in.
- `vfa-38` / `vfa-39` — the cache round trip (including a hold refusing to park and a
  torn file degrading to unknown) and the shared label rule.
- `testing/scenarios/vf_bg_tooling.py` — `vf-bg-6` pins the `gate_holding` guard's
  DIRECTION deterministically, which invariant 14 leans on.
- `python scripts/harness.py oracle mutate --scenario testing/scenarios/vf_acceptances.py`
  must report no survivors before this spec's implementation changes.

## Ceilings (deliberately NOT built)

- **Scope of consent is bounded, not proven.** The drive launches the vendor's full
  interactive CLI, and the reader is generic by design (invariant 4), so it cannot
  tell the hook-trust dialog from any other confirm-shaped screen. Invariant 9 stops
  the drive the moment the vendor reports nothing pending, and invariant 10 caps what
  can be spent without progress — but within that small budget, a screen that is not
  the target one could still be answered. Headless is opt-in (`visible` is the CLI
  default) and always behind an explicit owner click. Closing this properly needs a
  vendor-scoped launch surface, which codex does not currently expose.
- **The codex leg of the session surface is one of the hooks it reports.** Until the
  owner accepts, codex will not run it, so in a codex session it is silent for
  precisely the reason it exists; the claude leg is what gets the word out. Wiring it
  anyway is deliberate — parity is rendered from the manifest, and once accepted the
  leg works — but it is not a surface to rely on in a codex-only session.
- **The panel makes the scope residual reachable by one click.** Invariant 18 does not
  widen what the drive may do — the rails, the budget and the per-key re-probe are
  unchanged, and the panel cannot pick a mode or a vendor. What it changes is the
  DISTANCE: the first ceiling above (a screen that is not the target one could still be
  answered within the small budget) used to sit behind the owner typing a command, and
  now sits behind a confirmed button. That is a deliberate trade for the surface the
  owner asked for, and it is why the mode is fixed server-side rather than offered.
  Closing it still needs a vendor-scoped launch, which codex does not expose.
- **The card's age is the PROBE's age, not the pendency's.** The vendor does not report
  when trust lapsed, so `askedAt` is when the harness last asked. A cache that stops
  being refreshed ages into the expiry refusal — the safe direction (re-read, never
  auto-apply), but it means the row cannot tell the owner how long the hooks have
  actually been inert.
- **The nt transport is only proven where pywinpty is installed.** `vf_acceptances`
  runs a real ConPTY round trip when `pty_drive.available()` says yes and falls back
  to asserting the legible refusal when it does not — so a host without the optional
  dependency still gates green, and covers correspondingly less. On such a host
  `PtySession.__init__`'s platform branch is unreachable and the mutation oracle
  reports it as a survivor; that is accurate, not a gap to paper over.
- **No overall wall clock.** Every leg is bounded (screen 15s, reader 45s, reprobe
  ~65s, close ~10s), so the drive cannot hang — but there is no single number to
  point an operator at. Worst case with the defaults is several minutes.
- **The transcript is not rotated or redacted.** It durably stores whatever a hook's
  `command`/`matcher` renders on screen — the same content `hooks/list` already
  surfaces, now written under `.harness/runs/` (gitignored, so no commit leak).
- **No trust granting via protocol.** The vendor exposes none, on purpose. If one
  ever appears, it replaces the pty transport entirely — invariants 3–14 exist
  only because typing into a screen is the last resort.
- **Codex only.** `PROBES` is a registry; other vendors need their own
  non-interactive question, not a scraped screen.
