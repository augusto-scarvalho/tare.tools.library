# Forensics 2026-07-25 — codex `apply_patch` cannot write; the cause is a split writable-root set

**Status: root cause CONFIRMED BY PREDICTION, and fixed on our side by one config flag.**
Upstream defect, upstream issue open. This file exists because the behaviour is a
third-party bug that will change: when codex fixes it, whoever finds our config flag
needs to know why it is there and what test retires it.

## The symptom (two days of folklore)

Two `gpt-5.6-sol` lanes on 2026-07-24 returned `status: blocked` without writing. The
backlog row was named `codex-apply-patch-stage` after a *lead* — that codex stages
through a `.stage` file at the repo root — and that name then steered two days of
investigation into places the defect was not.

## Measurement (codex-cli 0.144.4, cheap `terra` tier, `--sandbox workspace-write`)

Six probes across four lanes. Every failure returned the same opaque line —
`Failed to write file <FINAL path>`, exit 1, **wall time 0s**, no OS error code:

| probe | what | result |
|---|---|---|
| A | `apply_patch` → repo root | FAILED |
| B | `apply_patch` → `docs/` | FAILED |
| C | **shell** (`Set-Content`) → repo root | **SUCCESS** (file on disk) |
| D | `apply_patch` → freshly created dir, verified WITHOUT the READONLY bit | FAILED |
| E | `apply_patch` → `docs/` | FAILED |
| F | `apply_patch` → repo root, **with `sandbox_workspace_write.exclude_slash_tmp=true`** | **SUCCESS** |

Codex self-reported, unprompted:

```
Sandbox mode:   workspace-write
Writable roots: C:\projects\universal-agent-harness-prototype, C:\tmp     <- A and B
Writable roots: C:\projects\universal-agent-harness-prototype             <- F
```

## Six hypotheses eliminated by measurement, not by argument

1. **The repo root.** A subdirectory (`docs/`) fails identically → not root-specific.
2. **The sandbox denying writes.** It declares the repo a writable root, and codex's
   OWN shell wrote inside it in the same run (probe C).
3. **The harness hooks.** `PreToolUse Completed` in the transcript, and the write
   failed anyway.
4. **The READONLY directory attribute.** This tree carries it on 76 directories
   (root, `.harness`, `scripts`, `docs`, `release`, even generated ones like
   `scripts/__pycache__`) while a freshly created directory here is plain
   `0x0010` — verified `Directory` vs `docs`'s `ReadOnly, Directory, Archive`.
   Probe D wrote into the clean one and failed identically. **The attribute is
   innocent**, recorded here as tested-and-eliminated because it is an attractive
   red herring that was nearly chased twice.
5. **The model.** Reproduces on `terra` and on `sol`.
6. **The `.stage` thesis that named the backlog row.** Not one of five errors mentions
   a staging path; every error names the FINAL path.

## Root cause

Codex injects a **second** writable root (`C:\tmp`) beside the workspace. Its Windows
unelevated restricted-token sandbox cannot enforce a *split* writable-root set, so it
refuses the sandboxed write path entirely — while codex's shell tool, which runs
outside that path, still writes. Upstream states it plainly in
[openai/codex#30712](https://github.com/openai/codex/issues/30712):

> `failed to prepare fs sandbox: failed to prepare windows sandbox wrapper: windows
> unelevated restricted-token sandbox cannot enforce split writable root sets
> directly; refusing to run unsandboxed`

Our CLI never printed that diagnostic — it swallowed the reason and emitted only
`Failed to write file`. The corroboration that made the match credible was ours: the
`C:\tmp` second root appeared in codex's own report while appearing in NO configuration
of ours (neither `.codex/config.toml` nor the user-level config declares
`writable_roots` or any tmp path). Codex adds it by itself.

**Confirmation is by prediction, which is the strong form:** the hypothesis says a
single writable root should restore `apply_patch`. Probe F set
`sandbox_workspace_write.exclude_slash_tmp=true`, the roots collapsed to one, and
`apply_patch` succeeded. Stated before the test, then observed.

## The fix (ours, today)

`.harness/routing/executors.json` → the `codex` `commandTemplate` now carries
`-c sandbox_workspace_write.exclude_slash_tmp=true`. It is load-bearing, not hygiene.

This is better than the previous workaround ("tell codex lanes to write through the
shell"): lanes get precise patch-based edits back instead of whole-file shell rewrites,
which upstream #30712 notes also *bypass the sandbox* — so the old workaround was
trading a broken tool for a weakened boundary.

**Known trade:** codex no longer has `C:\tmp` as a writable root. Nothing we run needed
it (measured: probe F succeeded), but a future codex feature that stages large content
through tmp could regress — [#15003](https://github.com/openai/codex/issues/15003)
records that Windows patch bodies still travel via argv, which is the neighbouring
constraint.

## When to retire the flag

Retire it when a codex release makes `apply_patch` succeed WITHOUT it. The retirement
test is probe A, verbatim: `apply_patch` creating a file at the repo root under
`--sandbox workspace-write` with the flag removed. If it succeeds, drop the flag and
this file's reason with it.

## Related upstream issues (all open at time of writing)

- [#30712](https://github.com/openai/codex/issues/30712) — split writable roots; the
  match. Reported for the **desktop app**; this forensics extends it to **CLI 0.144.4**.
- [#9661](https://github.com/openai/codex/issues/9661) — `apply_patch` not working at
  all on Windows.
- [#32477](https://github.com/openai/codex/issues/32477) — Windows 11, CLI **0.144.1**,
  `apply_patch` stalls.
- [#25860](https://github.com/openai/codex/issues/25860) — `apply_patch` can ADD but
  cannot UPDATE files on Windows. This answers, for free, the residual question this
  investigation had named and priced: our six probes were all creations, so the two
  halves of the operation fail under different conditions.
- [#15003](https://github.com/openai/codex/issues/15003) — patch body transported via
  argv on Windows.

## Method note, kept deliberately

The most expensive defect here was **the name of the backlog row**. It christened an
unproven lead (`.stage`) as if it were the cause, and the investigation — mine, on two
separate days — ran inside that name, hunting a staging path, then `os.access`, then a
file attribute. The raw error never mentioned staging.

What broke the loop was forbidding the workaround in the lane instruction: *"if it
fails, the failure IS the deliverable — report the verbatim error and STOP."* The
2026-07-24 lanes had returned `blocked` with no error text, which is exactly how a
diagnosis becomes folklore. One raw error outweighed six days of elegant hypotheses,
five of which were mine and wrong.
