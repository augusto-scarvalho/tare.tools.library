# Round — Defining the Gate Surface (2026-07-26)

Double Diamond over SPEC-137. Orchestrator: overseer session (Opus 5, fallback recorded). Playbook: `.harness/prompts/research-playbook.md`.

## Question

The **gate surface** (`precommitValidation.surfaceRoots` — what the gate observes) and the **risk surface** (what can break the system) disagree. Why does this defect class recur — four open records in five days, none closed — and what design makes the two agree **without** paying for the DRUM (scenario battery, 5–27 min) on every docs edit?

Explicit problem framing, not solution framing: “widen `surfaceRoots`” is the tech-shaped answer that already failed to close the class (it was applied to `ui/` on 21 Jul and the same form reappeared three more times).

## Success criteria

A good answer must simultaneously:

1. **Close the class, not the instance.** A design that requires editing a list every time a new file becomes machine input has already failed — that is how the four records were born.
2. **Name the price.** Cost in seconds per commit, by file class, against two measured numbers: spec-pack 19.5s / scenarios 5–27min.
3. **Do not deadlock the gate.** `unstaged_surface_paths` blocks `validate --staged` when any tracked file under a surface root is dirty — and `.harness/context/NEXT_STEPS.md` + `handoff.*` are dirty in every session.
4. **Falsifiable tooth.** Proposed check must FAIL today and pass afterward while reading the LIVE policy (`.harness/project.json`), not a hard-coded scenario copy — every gate scenario currently uses its own `POLICY` copy in a scratch repo, so a tooth against the copy is measured tautology.
5. **Cover the self-referential case.** `project.json` defines the surface and is outside it; any design must say what happens to it.

## Actors and constraints

- Actors: overseer (commits), implementer/worker (edits), pre-commit hook (blocks), gate runner (runs), owner (decides widening).
- Hard constraints: fingerprint is index-based (`git ls-files -s`, immune to mtime); `validator_version` hashes `project.json` → changing policy invalidates every stamp; `spec-pack` does **not** run `testing/scenarios/*.py`; SPEC-159 Phase 2 (affected-scenario selector) has narrowing=0, so no cheap battery exists today.

## Declared width (D010)

**4 workers, `custom`, in 2 waves of 2 — owner request (Sonnet 5 High ×2 + NVIDIA ×2).** Rationale (Δm — every extra worker must earn its keep):

- Theme is **one** (surface definition), pulling toward FOCUSED (1–2). But solution space is open (four competing framings, no design selected), pulling toward EXPLORATORY. Four sits in a justified middle band rather than a default.
- Width is deliberately **cross-vendor**: model heterogeneity is what makes the panel valuable (arXiv:2502.08788 — MAD is overrated when heterogeneity is ignored). Two vendors ≠ two workers from one model.
- **Perspectives follow access, not taste.** HTTP workers (`nvidia-compat`, through `tools/openai_worker.py`) cannot read the repo — the packet is all they see. The two perspectives requiring code verification (simplicity/reduction, reliability/ops) therefore go to Sonnet 5 High with repo access; conceptual perspectives (trust boundary, cross-domain analogy) go to NVIDIA, where lack of access costs less. Both receive the SAME embedded evidence floor.
- Separate waves are also what the machinery allows: `--executor` fixes an entire run to one executor, and no routing role points to `nvidia-compat`. Independent waves = nominal generation without cross-talk (Diehl & Stroebe 1987).

## Declared budget

- Wave A (Sonnet 5 High ×2) + Wave B (NVIDIA ×2): ceiling via `workflow token-audit` before each `run`; playbook 60% gate applies.
- NVIDIA is free tier (NVIDIA Build) — gas cost ~0.
- CLAUDE 99% remaining (probe 26 Jul 20:24). CODEX 1% — **no leg goes to Codex in this round**.
- No structured-technique waves 2–3 unless strong signal. One divergence (×2 waves) + one critique, per playbook.

## Experiment design (L18)

This round does **not** itself produce a measurable claim — it produces design options. If an option becomes a default promotion (widen surface and measure false blocking), applicable cards from `docs/EXPERIMENT_METHODS.md` are **matched-budget** (compare gate cost by file class under equal budget) + **evidence grades** for promotion. Register through `experiment add` only when a claim exists; today it does not.

## Evidence floor (embedded in every packet)

Measured in this session, `[repo]` except where marked:

- `precommitValidation.surfaceRoots = [scripts, tools, testing, specs, ui]` (`.harness/project.json`).
- Short-circuit appears in three consumers of the same definition: `validation_stamp.check_staged:212`, `check_reckon:337`, `cmd_validate:714` — all `staged == head` → `"surface unchanged"`, exit 0.
- Structural proof: 0 of 792 manifest entries are outside the five roots. Manifest is built with `git ls-files -s -- <roots>`, so outside paths are not overlooked: they do not exist for the fingerprint.
- 326 of 1120 tracked files (29%) are outside. 32 of last 120 commits (27%) touched zero surface files → entered with no gate and green join.
- Outside surface: `docs/` (183), `.harness/` (44, incl. `project.json` that DEFINES policy, `routing/`, `prompts/`), `.claude/`, `.codex/`, `codex/`, `schemas/` (12), `tasks/`, `release/`, `.github/`, `requirements*.txt`, `setup.sh|bat`, `skills-lock.json`, `AGENTS.md`, `CLAUDE.md`.
- 11 of 12 files from `protected-files.json` are outside the surface.
- `.harness/project.json`: outside surface, outside protected-files, and no scenario asserts its live content (all use hard-coded `POLICY` in scratch repo). `enabled:false` would commit with battery green.
- Four open records of same cause: `wf-policy-self-coverage` (21 Jul, P1), intake `d783b80d7748` (23 Jul, HIGH), `gate-docsonly-skips-lockfile-inputs` (25 Jul, P2), `gate-surface-shortcircuit` + intake `caa593befe98` (26 Jul, P1).
- Measured prices: `spec-pack` 19.5s / 1055 checks; scenarios 5–27min. `spec-pack` does **not** run `testing/scenarios/*.py`, where the teeth for these files live (`playbook_registry` lock drift, `eg_entry_groom` malformed row).
- Precedent: `400e302` closed the same form for `ui/` in three layers — policy + profile, pin in `gate_affected.py`, proof in `pvg_precommit_gate.py`.
- Partial mitigation exists: `delivery_bar_advisor` SEES these paths (R2/R3/R6) and prints pre-commit warning — but never blocks, and R3 becomes silent if any scenario is staged alongside it.

## Briefs (Phase 2)

**Brief 1 — the class, not the instance.** Why does surface definition recur as a defect? What design makes “what the gate observes” derive from “what is machine input” rather than a curated list? Criteria 1, 4, 5.

**Brief 2 — price of agreement.** If surface widens, who pays and how much? What cost gradation by file class is defensible, and what to do while no cheap battery exists (narrowing=0)? Criteria 2, 3.

## Waves

| Wave | Executor | Workers | Perspectives | Status |
|---|---|---|---|---|
| A | `--executor claude` (`WF-20260727-003307-162394`) | 2 | simplicity-reduction; reliability-ops | reduced, 2/2 valid |
| B | direct `openai_worker.py`, `z-ai/glm-5.2` (`WF-20260727-003327-207241`) | 2 | trust boundary; cross-domain analogy | ran 2/2, **reduce rejected by schema** |
| C | `research-critique` (seeded) | — | TBD | not planned |

Deviations from default path, all measurement-driven:

- `--executor` fixes whole run and no routing role points to `nvidia-compat`; without it resolution falls to `generic`, `runnable:false`. Hence two waves.
- Wave B used overseer-playbook packet-worker recipe instead of `workflow run`: `--executor nvidia-compat` would resolve to `stepfun-ai/step-3.7-flash` (cheap `defaultSpawn`) and `run` exposes no model flag. Direct call used `z-ai/glm-5.2`, “primary smart” tier.
- Playbook recipe says read key from `.env`; `.env` no longer exists — `keys-keyring v2` moved to OS vault. Used `keys_vault.vault_get`. **Playbook recipe is stale.**

## Results

### Independent convergence — strongest finding

All four workers, across two vendors, reached the same CLASS diagnosis: defect is not list content but **polarity**. Wave A called it “allowlist polarity”; Wave B “enumeration vs derivation” (Bazel-hermeticity analogy: input set derives from transitive closure, not enumeration). Convergence between models that never saw each other is the strongest signal produced by the round.

### Surviving proposal (worker A-001, simplicity lens)

**Invert polarity**: surface = tracked tree MINUS existing `exclude` glob in policy. Kill `surfaceRoots`-as-curated-list rather than widen it.

- `project.json` becomes covered **by construction**, not special case — closes `wf-policy-self-coverage` without dedicated rule.
- Paths without explicit profile fall to `other` → `[spec-pack]` (19.5s), never the scenario DRUM.
- Chronic dirt becomes **two NAMED excludes**; precedent already exists: `.harness/state/quality-state.json` is excluded by exact path, not root. File-level excludes are accepted repo pattern, not new exception.

### Mechanism nobody had noticed (worker A-001)

`validation_stamp.VALIDATOR_INPUTS` **already includes** `.harness/project.json` — intent that policy change invalidates old stamps is declared at `:34-39`. But the line reading it (`:229`) is **unreachable** while `project.json` sits outside its own `surfaceRoots`: short-circuit at `:212` happens first. The repo already wanted the right behavior; the short-circuit swallows it.

### New requirement (worker A-002, reliability lens)

Bypass is **invisible to the gate’s own observability**. `"staged surface unchanged vs HEAD"` is tuple return + print — nothing is persisted to `quality-state.json`. Only other observer is `delivery_bar_advisor`, whose exit code is always 0. **There is no ledger.** Recurrence was visible only through manual archaeology, explaining four records in five days without connection. Fix therefore needs a **bypass record**, not only wider surface — otherwise next regression is archaeology-only again.

### Honest counterargument (worker A-002)

Widening surface **increases exposure frequency to two already-known partial failures** of `gate_staged`, both tied to real incidents: orphan gate hold after foreground timeout (`gate_staged.py` docstring) and 2026-07-22 `gate-while-dirty` guard (`_staged_but_modified`). More surface = more gates = more chances to touch both.

### Falsifiable tooth already has a precedent

`gate_checks_policy.py:89-129` and `:262-283` **already read live `.harness/project.json`** with `json.loads`. Check-against-live-policy mechanism exists and runs in 19.5s tier; only not applied to `precommitValidation`. This removes “new mechanism” objection and avoids criterion-4 tautology (every gate scenario currently uses hard-coded `POLICY`, e.g. `pvg_precommit_gate.py:32`).

### Evidence-floor correction

Worker A-001 flagged an inconsistency in my floor: I said “11 of 12 protected outside surface”; it counted 10. Reconciled — there are **two lists**: `project.json#/protectedFiles/defaultProtectedFiles` (10) and `.harness/protected-files.json#/protectedFiles` (12, superset adding `harness-operator.md` and `py-run.sh`). My number was correct for the second, worker’s for the first. But divergence is real and latent: **nothing forces them to agree**, and there is a third mechanism (`protectedPatterns`, 24 entries) nobody reconciled. Candidate own record.

### Defects found in the research machinery itself

1. **`workflow plan --validate-only` says `valid:true` without checking REDUCER prompt ceiling.** `token-audit` later failed (2089/2000). Two replans needed. Same disease as topic: existing check does not cover what it appears to cover.
2. **Divergence profile does not prevent diversity collapse.** `concurrency:1` + shared WF directory caused A-002 to **read A-001 result before writing** — declared in its own summary. Playbook bans `--seed` for divergence to preserve independent generation, but ban covers flag only, not filesystem. Wave B, two isolated POSTs, was the only genuinely independent generation.
3. **WORKER_RESULT contract effectively prevents packet-only worker from emitting `high`/`blocker`.** It requires `sourceFilesVerified`, a field an HTTP worker without repo access cannot legitimately fill. Whole Wave B was rejected (`"sourceFilesVerified required when high/blocker findings are present"`), discarding 12 real findings from reduce. Worse, this explains improper `[repo]` tags by NVIDIA workers on packet evidence — contract **pressures** them to claim verification they did not perform. Cheap multi-vendor leg is currently either useless for serious findings or provenance-fabricating.
4. Smaller: an otherwise valid result (four verified findings) rejected because **one** advisory metadata string was 284 chars vs 200 ceiling — and it was worker honestly stating what it could not reverify. Trimmed to 195 and revalidated; original preserved in round record.

## Phase 4 — Critique

Panel: one validity critic on **Sonnet 5 High** (same-model control) + three critics on **Opus 5 xhigh** (architecture, cost, security), with `--allow-frontier` authorized. Identical brief for all four, no findings shared between them: model convergence becomes signal, not echo.

Routing note: no role has Opus at `high`; every `claude-opus-5` pin is `xhigh`. It ran xhigh — more effort than requested, not less.

### Verdict: P1 does NOT close the class. Three independent critics overturn central claim.

**Blocker 1 — gate control-plane itself is excluded by glob, before and after P1.** `exclude` contains `tools/git-hooks/**`; `git ls-files tools/git-hooks` returns tracked `pre-commit` and `post-commit`. “Tree minus exclude” inherits exclusion intact. `tools/git-hooks/pre-commit` has three lines and `exec`s the gate — replacing with `exit 0` disables gate, reckon and post-commit audit at once. `VALIDATOR_INPUTS` does not list hooks, so edit invalidates no stamp. *(security critic, strong confidence, measured)*

**Blocker 2 — `other` profile is not config, and with `gates: []` gate stamps green after zero checks.** Allowlist does not die; it migrates from `surfaceRoots` to `profiles.roots`, and `required_profile()` needs CODE change. Worse, empty gate list turns visible bypass (`"surface unchanged"`) into **invisible bypass** (green stamp claiming validation). *(architecture critic)*

**Blocker 3 — P1 would create FALSE CERTIFICATION in 15% of commits.** `scenario_isolation.py:167-184` documents that held directories *“run at HEAD content during the scenarios gate”*; only `docs/IMPLEMENTATION_BACKLOG.md` is rematerialized from index. Critic measured **108 of 710 commits in 30 days (15%)** staging both surface files and `.harness/{state,context,runtime,routing,handoff}` paths. Today this prints warning. With `.harness/` inside surface, `stamp_staged` would claim those files were validated while battery actually ran HEAD. This materializes sibling intake `d783b80d7748` as a consequence of the fix. *(cost critic, strong)*

### Concrete encoding traps

- **`surfaceRoots: []`**, natural encoding for “whole tree,” is falsy in Python and silently falls to `SURFACE_DEFAULT` (`:28`), which **does not contain `ui`**, reopening hole fixed by `400e302`. Three call sites use same `or`: `:101`, `:117`, `:685`. Encode `["."]` and delete/repoint `SURFACE_DEFAULT` in same commit.
- **Two named excludes are insufficient** — found independently by Sonnet and Opus: gate declares **20 tracked volatile files**, and highest-churn outside surface is `docs/IMPLEMENTATION_BACKLOG.md`. Blocking still falls AFTER launch.
- **`validation_stamp.py` is not in `VALIDATOR_INPUTS`** — module defining manifest, exclude matcher and profile map does not invalidate stamp when changed.
- **P1 degrades SPEC-159 narrowing metric**: `surfaceRoots` is not local to gate; it is the input domain of Phase-2 shadow.

### P2 and P3 also corrected

- **P2 ledger has a location trap**: `.harness/state` sits INSIDE hold restored by gate — exact precedent documented in `validation_stamp.py:274-283` (`reckon-results.jsonl` lives in `.harness/runs` for that reason). Writing bypass ledger to `.harness/state` makes gate erase its own audit trail. Correct target `.harness/runs/`, with local-only cost (`.gitignore:38`). Must log `policy is None` branch too (`:209`/`:334`), not only `staged==head` — otherwise cheapest bypass is outside record.
- **P3 can be satisfied with destroyed surface** and cited precedent is advisory that never fails. As stated, tooth does not pin what it should.

### Reversibility (measured)

Rolling back P1 is cheap; rolling back P3 is not — and rollback stales every existing stamp. P3 tooth can even **block its own rollback** if `project.json` is reverted alone.

### Operations by card (post-critique)

| Card | Origin | Operation |
|---|---|---|
| Invert polarity (tree-minus-exclude) | A-001 | **split** — idea survives, proposal does not. Becomes four named preconditions below. |
| Bypass ledger | A-002 | **kept with correction** — target `.harness/runs/`, log `policy is None` too |
| Gate control-plane inside surface | security critic | **NEW, precedes everything** — without it, “close the class” is false |
| Index rematerialization for held paths | cost critic | **NEW, precedes P1** — otherwise stamp becomes false certification in 15% commits |
| `["."]` + death of `SURFACE_DEFAULT` | cost critic | **NEW** — otherwise obvious encoding reopens `ui` hole |
| `other` profile | A-001 | **reclassified** — engine change, not config; never with `gates: []` |
| Manifest auto-inclusion | B-002 | **rejected** — policy is read from WORKTREE and fails open; manifest membership does not close self-reference |
| Content-addressed graph (Bazel) / cquery | B-002 | **deferred** — retained; critique did not promote them |
| `.gitattributes`-style annotation | B-002 | **rejected** — `exclude` already does it |
| Reconcile three protection lists | orchestrator | **split** — own record |

**No implementation recommended in this round.** Deliverable is a much more precise problem statement and four preconditions any fix must satisfy before touching `surfaceRoots`.

### Defect 5 in research machinery — the most expensive

**Of eight workers run, six had results rejected by schema — and all eight produced usable content.** Wave B: 2/2 (`sourceFilesVerified` required for high/blocker, impossible for packet-only worker). Wave A: 1/2 (84-char metadata string above ceiling). Opus critique: **3/3** (`maxWorkerOutputChars` 15371>12000 + `frictionObservations`). Thus the frontier wave the owner paid for had 100% of results formally discarded; blocker findings in this section survived only because orchestrator read files manually. Ceilings exist for good reason (reducer-context cost), but system currently discards ENTIRE work rather than degrade — no truncation, spill, or “partial accept with warning.” Candidate own record, not a gate issue.

## Phase 5 — Synthesis

### What the round actually discovered

Defect is not `surfaceRoots`. Five blind spots below are **one problem**: gate cannot see, validate, or remember its own substrate.

| Layer | Mechanism | Where gate is blind |
|---|---|---|
| Execution | `tools/git-hooks/pre-commit` (3 lines, `exec` gate) | excluded by glob; absent from `VALIDATOR_INPUTS` |
| Configuration | `.harness/project.json` defines surface | outside own surface; read from worktree, fail-open |
| Implementation | `validation_stamp.py` defines manifest, exclude and profiles | absent from `VALIDATOR_INPUTS` |
| Memory | short-circuit persists nothing | no ledger; sole observer (`delivery_bar_advisor`) fixed exit 0 |
| Validation | held paths run with HEAD content (`scenario_isolation.py:167-184`) | battery does not validate what stamp would claim |

**Each hole came from a locally correct decision.** Excluding `tools/git-hooks/**` avoids installed-artifact churn; holding `.harness/` prevents scenarios seeing owner live state; `.harness/state` is held because runtime; allowlist exists so docs do not spin the DRUM. Each defensible alone. Composition produces a gate that does not validate itself — which is why the class recurs **without anyone being careless**. More care cannot fix it.

### Larger pattern (orchestrator synthesis, not worker finding)

The round found the same disease across six independent layers: **checks that appear to cover what they do not cover.**

| Instance | Appearance | Reality |
|---|---|---|
| `check_staged` / `check_reckon` | `pass` | no check ran |
| `workflow plan --validate-only` | `valid:true` | reducer prompt ceiling not checked (later failed 2089/2000) |
| `WORKER_RESULT` contract | “0 valid workers” | 8/8 produced usable content; 6 discarded on format ceiling |
| `delivery_bar_advisor` | warnings R1-R6 | exit code always 0 |
| SPEC-159 Phase 2 | affected selector | `narrowing=0` in SHADOW; selects nothing |
| `spec-pack` in `project.json` | declared scope includes “routing consistency” | not wired to this surface |

Most transferable claim of the round, and it is not about gates. Confidence **moderate** (six measured instances in this session; generalization is judgment).

### Traceability matrix

| Evidence | Problem | Idea | Spec/ADR | Task | Status |
|---|---|---|---|---|---|
| `exclude` contains `tools/git-hooks/**`; tracked pre/post hooks; only 2 churn commits in whole history | gate control-plane can be disabled without stamp invalidation | remove from exclude + add hooks and `validation_stamp.py` to `VALIDATOR_INPUTS` | SPEC-137 amendment | `gate-controlplane-excluded` | **shipped 2026-07-27** |
| short-circuit is tuple+print; nothing persisted; 4 records in 5 days only via archaeology | recurrence undetectable | bypass ledger in `.harness/runs/`, logging `staged==head` AND `policy is None` | SPEC-137 amendment | `gate-bypass-ledger` | **shipped 2026-07-27** |
| `scenario_isolation.py:167-184` runs held paths at HEAD; 108/710 commits stage surface + `.harness/` together | wider surface becomes false certification | rematerialize index for held paths | — | class-row precondition 2 | open (was intake `d783b80d7748`) |
| `SURFACE_DEFAULT` lacks `ui`; three `or` call sites | `surfaceRoots: []` falsy reopens `400e302` hole | encode `["."]` and kill default same commit | — | class-row precondition 3 | open |
| `required_profile()` matches `profiles.roots`; `gates: []` stamps green | `other` profile is engine, not config | code change; never `gates: []` | — | class-row precondition 4 | open |
| 6/8 workers rejected by schema; 8/8 useful | contract discards instead of degrading | truncation/spill/partial accept with warning | — | `wr-schema-discards-work` | open |
| `project.json` 10 protected vs `protected-files.json` 12 vs 24 `protectedPatterns` | three unreconciled lists | reconciliation + tooth | — | `protection-lists-reconcile` | open |
| `concurrency:1` + shared WF dir → A-002 read A-001 result | `--seed` ban covers flag, not filesystem | isolate worker dir in divergence | — | `wf-divergence-shared-dir` | open |
| `token-audit` failed what `--validate-only` approved | reducer ceiling absent from validate | same check in both | — | `wf-validate-only-reducer-ceiling` | open |
| GLM recipe reads `.env`; keys-keyring v2 moved to OS vault | broken playbook recipe | point to `keys_vault.vault_get` | — | fixed inline in this sitting | closed |

### Recommended sequence

1. **No surface change yet.** Every proposal in this round was wrong about measurable facts; obvious fix would have created false certification in 15% of commits.
2. **Ledger first** — only component that survived critique intact; reversible, does not touch `surfaceRoots`. Repo’s own doctrine (`wf-gate-observability`, SPEC-158): *can’t exploit a constraint you can’t see*.
3. **Control-plane** — independent security fix.
4. **Only then surface**, using ledger data and four preconditions as acceptance criteria.
