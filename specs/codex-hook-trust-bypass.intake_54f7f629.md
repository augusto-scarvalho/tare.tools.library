# Intake refinement — door NEW checklist

## Request (verbatim)

> a gente poderia ter uma lista de hooks do harness e fazer esse allow de forma
> autônoma toda vez que algum novo entrar
>
> o problema de rodar essa flag é que não sabemos quais outros hooks o usuário
> pode ter colocado no harness. nao podemos dar bandeira branca pra algo
> estranho que nao seja nosso

(Owner, 2026-07-28, following the codex-stop-hook-fails-silently ship: codex
skips untrusted hook entries silently, and the interactive trust prompt is the
only persistence path — no CLI verb exists.)

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `python scripts/harness.py records search codex trust bypass hook` | no hit for this capability — only the 2026-07-18 parity commit (context, not coverage) |
| doc-find | `python scripts/harness.py doc-find codex trust bypass spawn flag` | no covering doc — hits are the modules this change touches (agent_parity, harness.py spawn builder) |

Decision: **NEW**.

## Goal

Harness-spawned codex lanes run the harness's own hooks autonomously (no
per-change human trust acceptance), without ever white-flagging hook content
that did not come from the harness's canonical pipeline.

## Scope

In scope:
- A fail-closed grant check: `--dangerously-bypass-hook-trust` is added to a
  codex spawn ONLY when `.codex/hooks.json` provably IS the committed canonical
  render of `.harness/capabilities.json`.
- Wiring into the one programmatic spawn seam (`workflow_spawn_command_for_prompt`)
  plus a CLI verb for hand-typed recipes.
- `.harness/capabilities.json` (the root of trust) enters the protected-files
  registry (SPEC-148 OS locks in write workspaces).

Out of scope:
- Persisting codex's own trusted_hash entries (undocumented recipe; the
  interactive prompt remains the path for human codex sessions).
- Claude-side hooks (no trust gating exists there).
- Reverse-engineering codex internals.

## Actors & surfaces

- Actors: harness spawn builder (workflows/lanes), overseer hand-typed recipes.
- Surfaces (CLI / GUI / API / internal): CLI + internal spawn seam.
- UI surface? no → Gherkin optional.

## Proposed acceptance criteria

- [ ] A codex spawn argv carries the bypass flag when hooks.json == canonical
      render, every wired command's script is manifest-managed, and both files
      are clean vs HEAD.
- [ ] A hand-added hook entry (managed-script drift, non-manifest script, or a
      command with no .py token at all) denies the flag even when committed.
- [ ] Uncommitted changes to either file deny the flag.
- [ ] Any error reading state (git absent, unreadable JSON) denies the flag
      (fail-closed — inverse of the audit's degrade-open stance).
- [ ] The deny path is loud (one stderr line with the reason).

## Risks / blast radius

SessionStart hooks run BEFORE the codex sandbox is applied (measured
2026-07-28), so a wrong grant executes repo-supplied commands unsandboxed as
the user. Mitigations are the three check legs + protecting the root of trust
(capabilities.json) + the existing gate pins (chb/cap-5/audit). Touches:
`agent_parity.py`, `harness.py` (spawn builder + cmd_agents), `cli_registry.py`,
`chb` scenario, protected-files registry. Rollback: remove the splice; lanes
revert to silently-skipped hooks (today's behavior).

## Open questions for the human

- (resolved 2026-07-28) Blanket flag? NO — owner: "não podemos dar bandeira
  branca pra algo estranho que não seja nosso". Grant is conditional on the
  canonical-render proof; this is the accepted design.
