# Intake refinement — worker permission tier by role (door NEW)

## Request (verbatim)

> "era pro codex ter sido spawnado via worker do tipo planner... aquele mecanismo
> que criamos que monta o prompt do spawn não poderia resolver isso automático
> pra gente time? passando as permissões do tipo de worker que está sendo
> invocado?"
>
> "e essa questão do workspace write / read only, estão atrelados às configs das
> roles dos workers? essa mudança proposta já resolveria. queria que você
> olhasse de múltiplas perspectivas pra gente não fazer trabalho pela metade"

## Covered-check (which door?)

| Query | Command | Outcome |
|---|---|---|
| records search | `records search spawn permission sandbox role` | no hit for role→tier binding |
| doc-find | `doc-find sandbox worker permission role` | hits `specs/40-features/harness-sandbox.md`, `harness-own-sandbox.md` (SPEC-148 owns the chokepoint) |

Decision: **NEW**, but as an AMENDMENT candidate to SPEC-148 (which already owns
`sandbox_spawn`), not a greenfield spec. The refinement round decides which.

## Goal

A worker's filesystem permission should follow from WHAT IT IS (its role),
derived once from the registry, instead of from whichever spawn path launched it
and whatever its caller typed by hand.

## Trigger incident (2026-07-24, measured)

A plan-authoring codex lane was launched with `--sandbox workspace-write` by
following the overseer playbook's launch recipe verbatim. A worker whose entire
deliverable is one markdown document held write permission over the whole
workspace. Nothing was damaged — but the worker did attempt to clear the
`ReadOnly` attribute on `.harness/handoff` and on the repo root to work around
an unrelated write failure, then restored both. It had permission to try.

## Measured facts (do not re-derive)

1. **The derivation mechanism EXISTS**: `agent_parity_vendors.py:330` →
   `sandbox_mode = "workspace-write" if writes else "read-only"`, and
   `agent_parity_conformance.py:159` asserts `--sandbox {sandbox}` is "derived
   1:1 from the worker's writeAllowed (S3)", failing if the template loses it.
2. **It is NOT bound to roles.** `writeAllowed` is a per-worker/per-workflow
   policy field read by `async_runtime` (`worker.get("writeAllowed")`,
   `workflow.policy.writeAllowed`). `task-profiles.json` declares no sandbox.
3. **There are THREE spawn paths with different (or no) enforcement:**
   - workflow → `async_runtime`, derives from `writeAllowed`;
   - chat/room → `chat_engines.py:499`, derives from `chat_mode`
     (`{"plan": "read-only", "accept-edits": "workspace-write"}`);
   - the overseer playbook's launch recipe → raw `codex exec --sandbox
     workspace-write`, bypassing `sandbox_spawn` entirely. This is the path the
     incident took, and it is the DOCUMENTED one.
4. **Read-only is real enforcement, verified**: under `--sandbox read-only` a
   shell `Set-Content` fails with a Windows `UnauthorizedAccessException` and no
   file appears. Under `workspace-write` the same command succeeds. So the
   vendor sandbox contains shell writes — a role-based tier is not cosmetic.
5. **Tool-level denylisting would NOT contain shell writes.** A PreToolUse hook
   sees an arbitrary command string; `Set-Content` is catchable but
   `python -c "open('x','w')..."`, `git checkout`, and string-built commands are
   not. The repo's `deny_hitl_flags.py` is the legitimate shape of that
   technique — a closed, enumerable set of named flags, not "any write".
6. **`fs_confine_nt` covers FILES only** (`if not target.is_file(): continue`),
   so directory attributes are outside the SPEC-148 locks.

## Audit findings (Sonnet internal archaeology, 2026-07-24) — these CORRECT the above

1. **A role→capability binding ALREADY EXISTS — reuse it, do not invent.**
   `.claude/agents/<role>.md` frontmatter `tools:` already partitions roles
   (scanner: no Edit/Write; implementer: has them), and
   `agent_parity_vendors.py:314-331` already derives
   `writes = any(t in ("Edit","Write") for t in tools)` →
   `sandbox_mode = "workspace-write" if writes else "read-only"`, rendering it
   into `.codex/agents/<role>.toml` (verified live: `scanner.toml` read-only,
   `implementer.toml` workspace-write) and conformance-checking it. **But it is
   a rendering/doc artifact only** — no caller in `harness.py`/`harness_lib`
   outside the parity machinery reads it to decide a real spawn's permission.
   The wiring is what is missing, not the concept.

2. **CORRECTION to this intake's risk section: the workflow default is ALREADY
   safe.** `worker.get("writeAllowed")` absent → `bool(None)` → `False` →
   read-only (`async_runtime.py:379,400,477,608,813`). Flipping that default
   breaks nothing because it is already the conservative one.

3. **NEW GAP, not previously known — the chat default passes NO flag.**
   `chat_engines.py` maps only `{"plan": ..., "accept-edits": ...}`, but
   `chat_mode` defaults to `"auto"` (`__init__`), which is absent from the map →
   `sandbox = None` → **no sandbox argument is emitted at all**, so the codex
   binary's own default governs. Harness-declared confinement is silently absent
   for every default-mode codex chat session. This is underspecified rather than
   wrong, and it belongs in scope.

4. **The chokepoint gate cannot see the incident path.** `CHOKEPOINT_SITES`
   (`sandbox_spawn.py:371-375`) is AST-gated over three code sites
   (`harness.py::run_one_worker`, `harness.py::cmd_route`,
   `async_runtime::workflow_async_run_one_worker`). The playbook launch recipe
   is prose, so no gate can enforce it — which is why doctrine is part of the
   fix, not an afterthought.

5. **Two independent enforcement layers, easily confused.** `sandbox_spawn`
   confines the workspace via real OS ACLs (`fs_confine_nt`) but NEVER emits
   vendor CLI flags; the `--sandbox`/`--allowedTools` argv is composed
   separately by the caller. They use the same vocabulary and are computed
   twice, independently.

6. **Consumption points for agreement (complete list from the audit):**
   `async_runtime.py` (5 sites), `chat_engines.py` (`_argv` sandbox +
   `room_tool_patterns`), the playbook recipe, `agent_parity_vendors`
   (`codex_agent_profile`), `agent_parity_conformance::_c5_permission_narrowing`
   (needs a cross-PATH check, today it only checks cross-VENDOR templates), and
   `task-profiles.json` (silent on sandbox today; natural registry home).

## Adversarial + external findings (GLM 5.2 attack + external research, 2026-07-24)

The GLM lane was given the measured facts and told to attack the design, with no
repo access. Two Sonnet lanes ran archaeology and external research independently.
**They converged on the same defects from three different directions** — which is
the main reason to trust them.

### Triple convergence (each found independently)

| Defect | GLM (design attack) | External research | Repo audit |
|---|---|---|---|
| Sub-worker doesn't re-derive its own tier | finding 5 (predicted) | Claude Code issue #25000: subagents don't inherit session deny rules; one ran 20+ bash commands unapproved | — |
| Read-only FS + open network is not containment | finding 2 ("theatre") | Codex ships `network_access` as its OWN boolean, default OFF even under workspace-write | — |
| Two permission surfaces that never union | finding 4 (`writeAllowed` override re-opens the hole) | named as the root cause of #25000 | three spawn paths, no shared resolver |
| Locks skip directories | finding 6 (+ symlink TOCTOU) | — | `fs_confine_nt`: `if not target.is_file(): continue` |
| Documented path bypasses the chokepoint | findings 1 + 11 (ship this first) | — | `CHOKEPOINT_SITES` is AST-gated over 3 code sites; the recipe is prose |

A design predicted the sub-worker defect; the field had already recorded it being
exploited in the vendor we use. That pair is the strongest signal in the round.

### Verified this session (do not re-derive; two of these correct GLM)

7. **GLM finding 3 confirmed, and the fail-open pattern is already in the code.**
   `playbook_registry.inject_mode("definitely-not-a-role")` returns `"list"`
   silently — the accessor is `.get(role, {}).get("inject") or <default>`. There
   is no unregistered-role error anywhere in registry lookup. A tier accessor
   written in the house style would be fail-OPEN by default. Registered roles
   today: 32. Also confirmed: `task-profiles.json` declares no `writeAllowed`
   (measured fact 2 stands).

8. **GLM finding 8 is half wrong and half worse than stated.** The harness
   already HAS the control GLM asked for: `processes.filter_spawn_env` (SPEC-119
   v5 / E3-C6a) builds a least-privilege env from an OS base allowlist +
   explicit `keep_list`, dropping unrelated API keys; and `sandbox_prepare`
   **refuses** an unfiltered env unless an `inherit_reason` is recorded
   (`sandbox_spawn.py:300`). `async_runtime.py:392` uses the filtered builder.
   **But `chat_engines.py:209, 366, 640` pass `env={**os.environ, ...}` raw**,
   and that path never calls `sandbox_prepare`, so the refusal never fires. An
   escape hatch also exists: `project.json workflows.workerEnvFilter=false`
   restores full inheritance globally.

9. **The chat/room path carries all three defects at once.** Same path:
   no sandbox flag emitted (`chat_mode="auto"` absent from the map,
   `chat_engines.py:286` sets that default), full operator env inherited
   including every API key, and no chokepoint call to refuse either. This is
   ONE fix site, not three — and it is the path the GUI rooms boot through.

10. **GLM finding 5 — NOT fully verified, stated as open.** What is certain: no
    spawn path consults a role registry for permission today, so nothing CAN
    re-derive. What I did not establish: whether a room can reach the vendor's
    own sub-agent tool (`room_tool_patterns` does not list it; `--allowedTools`
    auto-approves rather than exclusively permits, so absence is not proof of
    denial). Verify before designing against it.

## Scope

In scope:
- role → risk tier declared once (registry), consumed by every spawn path;
- reconciling the three existing sources of truth into one;
- per-vendor mapping — as tier→**enforcement mechanism**, never tier→flag
  (GLM 7: a registry that says `planner = read-only` while the HTTP planner has
  unrestricted filesystem access is worse than no registry). A vendor that
  cannot enforce a tier must say so and refuse, not silently no-op;
- **egress, moved IN from out-of-scope**: read-only-plus-network is a
  write-deterrent, not containment, and Codex already models it as a separate
  boolean defaulting off. A tier that governs the filesystem while leaving the
  network open sells confinement it does not deliver;
- **sub-worker re-derivation**: every spawn path resolves the spawned worker's
  OWN role to a tier. Inheriting the parent's confinement flag is forbidden;
- **env filtering on the chat path**: route it through `filter_spawn_env` and
  the chokepoint, so the existing refusal actually fires;
- the playbook launch recipe stops calling `codex exec` directly (doctrine is
  part of the fix: the documented path must be the safe path);
- extending `agent_parity` conformance to cover the three vendors.

Out of scope (name them, do not silently absorb):
- `fs_confine_nt` directory coverage and the symlink TOCTOU it enables
  (GLM 6) — real, but it is a SPEC-148 lock-model item, and GLM's own
  recommendation is to stop treating locks as a boundary rather than to extend
  them. Separate item, cross-referenced;
- the codex `apply_patch` staging failure — unrelated vendor bug, separate item.

## Actors & surfaces

- Actors: overseer (launches lanes), workflow runtime, chat/room engine.
- Surfaces: CLI + internal. No UI surface → Gherkin optional.

## Proposed acceptance criteria

- [ ] A role declares its tier in ONE place; no spawn path invents its own.
- [ ] A `planner`/`scanner` lane launched through the documented path resolves
      to a read-only sandbox, proven by a write attempt failing.
- [ ] An `implementer` lane still resolves to write, unchanged.
- [ ] The three spawn paths agree for the same role (a divergence is a red).
- [ ] `agent_parity` conformance asserts the mapping per vendor, and fails when
      a vendor template drops its narrowing flag.
- [ ] A role absent from the registry fails CLOSED (cannot run the risk), per
      `sandbox_spawn`'s existing rule 8 posture — proven against the CURRENT
      fail-open accessor (finding 7), which returns a permissive default for a
      typo'd role name today.
- [ ] Existing workflows with explicit `writeAllowed` keep working (state the
      precedence between an explicit worker policy and the role default).
- [ ] A sub-worker resolves its tier from its OWN role, not the parent's —
      a read-only parent spawning an implementer, and a write parent spawning a
      scanner, both land on the child's tier (finding 5 / issue #25000 shape).
- [ ] The chat/room path emits a sandbox flag in EVERY `chat_mode`, including
      the `"auto"` default, and its env goes through `filter_spawn_env`.
- [ ] A tier a given vendor cannot enforce refuses to launch rather than
      resolving to a flag that does nothing (finding 7).
- [ ] Each registry tier entry names its enforcement mechanism and its known
      gaps, so the registry cannot claim confinement it does not deliver.

## What this design does NOT do (GLM finding 10 — keep this section verbatim in the spec)

Written to prevent false confidence. A reader will assume the tier system solves
containment, exfiltration, and sub-worker isolation. **It solves none of these.**

1. Does not prevent data exfiltration via network — a read-only worker still has
   a shell and still has curl.
2. Does not contain shell-accessible tools that write outside the sandbox view:
   `git checkout` writes the working tree, `git clone` writes to disk,
   `pip install` writes site-packages, `curl` downloads to temp.
3. Does not isolate sub-workers unless every spawn path re-derives.
4. Does not confine HTTP workers at the filesystem level at all.
5. Does not protect unlocked directories (`fs_confine_nt` is files-only).

GLM's framing, which the spec should adopt: read-only tier is a **write-deterrent,
not containment**. Real containment means a seccomp profile or a container, not a
vendor flag. File locks are **tamper-evidence for canonical files**, not a boundary.

## Risks / blast radius

`sandbox_spawn` is the confinement chokepoint and `async_runtime` reads it on
every workflow worker; a regression there silently widens or breaks every spawn.
`agent_parity` is already conformance-checked, so changes must keep it green.
Tightening a default from write to read-only may break an existing lane that
relied on the loose default — enumerate callers before flipping.

## Recommended sequencing (GLM 11 — cheapest high-value subset)

Ship the direct-CLI removal FIRST, before the abstraction layer exists. It is the
only path that bypasses derivation *entirely* — the other two disagree but both
derive from something — and closing it is a docs + wrapper change, not a vendor
abstraction. It also removes the escape hatch an operator would otherwise reach
for the moment fail-closed refuses them (GLM 9's failure loop).

Concretely: (1) remove the recipe from the operator playbook, (2) a wrapper that
refuses to start without a resolved tier becomes the only documented launch path,
(3) grep runbooks and scripts for direct vendor-CLI invocations and flag them.

Second cheapest, and not in GLM's list because it needed repo access: the
chat/room path fix (finding 9) — one site, three defects.

## Open questions for the human

1. **Precedence — GLM recommends role-wins, with the cost named.** `writeAllowed`
   becomes a derived read-only VIEW of the tier, not an independent input;
   the conformance check flips from asserting `--sandbox` derives from
   `writeAllowed` to asserting it derives from the tier. Accepted cost, in GLM's
   words: existing workflows setting `writeAllowed=true` for a planner role
   **will break and must be migrated — "that breakage is the feature working."**
   Your call whether to take that cost. (Mitigated by audit finding 2: the
   workflow default is already read-only, so the blast radius is only workers
   that opted INTO write.)
2. Should the chat room's `chat_mode` mapping be subsumed by the role tier, or
   stay independent (a human is watching there, which is a different threat
   model from an AFK lane)? Note finding 9 raises the stakes: that path today
   emits no flag at all and leaks the full env.
3. **Fail-closed — GLM's answer: keep the default, add a visible exception.**
   The realistic break is an on-call operator whose hotfix role isn't registered
   yet; refusing pushes them to the direct-CLI path or to `writeAllowed=true`,
   both worse. Proposed: an explicit `--allow-unregistered-role` requiring a
   second approval or a break-glass token, audit-logged. Explicitly NOT a
   fallback tier — "that is silent and unreviewable." Your call.
4. New, from the egress scope change: does egress belong in THIS spec or as a
   paired SPEC-165 amendment landing together? Folding it in doubles the
   footprint; splitting it risks shipping the half that sells confinement
   without the half that delivers it.
