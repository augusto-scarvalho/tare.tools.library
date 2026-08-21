# Canonical file protection

## Goal

Protect the harness control-plane files that define agent behavior from silent overwrites during script installation, skill/plugin sync, MCP setup, template adoption, or executor-specific adapter updates.

## Applies to

This spec applies to canonical root instruction files, executor shims, generated-handoff entry points, and harness prompt contracts, including at minimum:

- `AGENTS.md`
- `CLAUDE.md`
- `AGENT_HANDOFF.md`
- `CODEX_HANDOFF.md`
- `AGENT_IMPLEMENTATION_ROADMAP.md`
- `CODEX_IMPLEMENTATION_ROADMAP.md`
- `.harness/prompts/subagent-contract.md`
- `.harness/prompts/task/00-start-here.md`
- `.harness/HARNESS.md`
- `.kiro/KIRO.md`

Project adopters may add their own protected files, but must not remove these defaults without recording an explicit deviation.

## Market-recognized agent instruction files

The protection policy must also maintain a versioned registry of common agent instruction/control files used by current coding assistants. The registry is not a prompt-loading contract; it is a supply-chain and installer-safety contract. If any of these files already exists, or if an installer/sync step creates one, the file must be treated as reviewed source and protected from blind overwrite.

Minimum registry entries:

| Tool family | Files / patterns to protect when present |
| --- | --- |
| OpenAI Codex | `AGENTS.md`, `AGENTS.override.md` |
| Claude Code | `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md` |
| GitHub Copilot / VS Code | `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.vscode/*.instructions.md`, `*.instructions.md`, `*.agent.md` |
| Cursor | `.cursor/rules/*.mdc`, `.cursor/rules/*.md`, `.cursorrules`, `AGENTS.md` |
| Gemini CLI | `GEMINI.md`; configured names such as `AGENTS.md` or `CONTEXT.md` must be opted into the protected list when used |
| Cline | `.clinerules/*.md`, `.clinerules/*.txt`, `.cursorrules`, `.windsurfrules`, `AGENTS.md` |
| Devin Desktop / Windsurf Cascade | `.devin/rules/*.md`, `.windsurf/rules/*.md`, `.windsurfrules`, `AGENTS.md`, `agents.md` |
| Roo Code | `AGENTS.md`, `AGENT.md`, `AGENTS.local.md`, `AGENT.local.md`, `.roorules`, `.roo/rules/*.md`, `.roo/rules/*.txt` |
| Harness adapters | root handoff/roadmap shims, `.harness/HARNESS.md`, `.harness/prompts/**/*.md`, `.kiro/KIRO.md` |

Optional market files are snapshot-if-present: absent files do not fail CI, but a new file matching a protected pattern fails until it is intentionally reviewed and added to the snapshot. This prevents plugin installers from creating new always-on agent instruction files invisibly.

## Invariants

- Installer, plugin, skill, MCP, and adapter setup steps must preserve existing protected files by default.
- Protected files are not generic generated artifacts. They are part of the harness control plane and may affect tool permissions, security posture, context loading, and task execution.
- A setup step that wants to change a protected file must run as a reviewed harness change, not as a blind install side effect.
- Protected files must have a versioned hash snapshot so release gates can detect accidental drift.
- Pre/post-install protection must be dependency-free and offline-safe.
- Executor-specific directories such as `.claude/`, `.codex/`, `.agents/`, `.cursor/`, `.devin/`, `.windsurf/`, `.clinerules/`, `.roo/`, or `tools/agent-sync/` must not become alternate sources of truth for canonical instructions.
- Market-recognized instruction files are protected through exact required paths plus snapshot-if-present glob patterns.

## Agent behavior

Agents working on installers, skills, plugins, MCP configuration, adapters, or root instruction files must:

1. Treat protected files as control-plane inputs, not generated setup outputs.
2. Capture and check snapshots around setup/sync/install work.
3. Stop and escalate if protected-file drift appears without an explicit reviewed task.
4. Keep canonical state in `.harness/` and root shims, not executor-local copies.
5. Record intentional changes in `HARNESS_RESULT.universalSpecsApplied` and regenerate release evidence.

## Required behavior

Before running any installer or synchronizer that might touch agent instructions:

```bash
python tools/hooks/protect_canonical_files.py snapshot --output /tmp/harness-protected-before.json
```

After the installer or synchronizer finishes:

```bash
python tools/hooks/protect_canonical_files.py check --snapshot /tmp/harness-protected-before.json
```

For ordinary CI/release validation:

```bash
python tools/hooks/protect_canonical_files.py check
python scripts/harness-test.py --fixture protected-files
```

The check must fail if any protected file is missing, overwritten, or changed relative to the expected snapshot.

## Allowed changes

Protected files may change only when all of the following are true:

1. The task explicitly authorizes harness instruction changes.
2. The diff is reviewed as a source change, not hidden inside an installer.
3. Specs/docs/gates affected by the new instruction behavior are updated.
4. `.harness/protected-files.snapshot.json` is regenerated after the reviewed change.
5. Release integrity artifacts are regenerated.

## Disallowed changes

- A plugin installer that overwrites `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/*.mdc`, `.clinerules/*.md`, `.devin/rules/*.md`, `.windsurf/rules/*.md`, or `.roorules` with a generic template.
- A skill installer that appends broad permissions or tool-use guidance without review.
- An MCP sync step that replaces root instructions while configuring local tools.
- A script install that mutates protected files and only documents the change in stdout.
- Any adapter-local copy that claims to be canonical while `.harness/` still defines the control plane.

## Validation evidence

Minimum validation for this spec:

```bash
python tools/hooks/protect_canonical_files.py check
python scripts/harness-test.py --fixture protected-files
python scripts/harness-test.py --fixture engineering-guardrails
```

## Evidence requirements

Changes touching protected files or installer behavior must report:

- which protected files changed;
- why the change was intentional;
- the pre/post protection check result;
- regenerated snapshot and release integrity evidence;
- any remaining `universalSpecDeviations`.

## Escalation triggers

Escalate to security/review when:

- a protected-file check fails after a setup/install step;
- a plugin/skill installer requests permission to rewrite root instruction files;
- protected-file snapshot drift appears without a matching reviewed diff;
- protected files start carrying project secrets, local credentials, or runtime state.

## Reference anchors

- `.harness/protected-files.json`
- `.harness/protected-files.snapshot.json`
- `.harness/protected-files.json#/knownAgentInstructionFiles`
- `.harness/protected-files.json#/protectedPatterns`
- `scripts/harness_lib/protected_files.py`
- `tools/hooks/protect_canonical_files.py`
- `testing/engineering-guardrails.json`


## Market-doc review metadata

The protected-file registry must record the last market-documentation review and reference URLs for known agent instruction families where public docs exist. The registry is intentionally fail-closed: installer-created files matching known instruction names or globs must be reviewed and snapshotted before release.

## Amendments

### v2 — the sibling lists reconcile against the registry, or say why not (row protection-lists-reconcile), 2026-07-29

Three-plus lists named "protected" without anything forcing agreement
(drift found 2026-07-27): the registry
(`.harness/protected-files.json#/protectedFiles` — CANONICAL, the only list
hooks and CLI consume), `project.json#/protectedFiles/defaultProtectedFiles`
(config bootstrap, consumed by nothing at runtime), the code fallback
`protected_files.DEFAULT_PROTECTED_FILES` (used only when the registry file
is missing), and `protectedPatterns` (a DIFFERENT axis — installer-write
blocks — reconciled only against exact path collisions).

`protected_files.reconcile(root)` now enforces the relationship, and
`evaluate()` carries it into the gate as `protected-files:lists-reconciled`:
a registry-only path must be DECLARED in
`reconciliation.registryOnly: {path: reason}` inside the registry; project
defaults must be a subset of the registry; the fallback must never protect
more than the registry; a declaration for a non-divergent path reads stale
(declarations stay honest); a pattern string equal to a protected path is a
collision. Teeth: `pf_protect_files.py` pf-5 (live repo reconciled, >=3
declared) and pf-6 (hermetic: undeclared flagged -> declared clears -> stale
detected).
