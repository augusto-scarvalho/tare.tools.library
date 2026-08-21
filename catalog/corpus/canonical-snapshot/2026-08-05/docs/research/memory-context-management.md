# Research round — memory + context compression/cleanup for the harness

Round opened 2026-07-12 by the `research` skill (SPEC-119). Orchestrator: overseer
session (owner AFK — full autonomy: round → portfolio → backlog → sequential
implementation + commits, audited later). Primary evidence: the owner's study (121
refs; 7 compression mechanisms, 5-layer architecture, cadence policy, risks) + a
verified baseline of our CURRENT harness + spot-checked external anchors.

## Phase 0 — Question, criteria, budget

**Question.** Which memory + context-window compression/cleanup improvements should
THIS harness adopt, given (a) the study's landscape and (b) our already-mature state,
biased deterministic-first (the study's own conclusion: simple observation masking
matches LLM summarization at half the cost; folding beats summarization)?

**Success criteria.**
- Backlog of buildable items, each mapped to a NAMED gap in our baseline (below) and a
  concrete integration point (file/module).
- Deterministic-first bias: prefer masking/pruning/folding/rotation over LLM
  summarization (Complexity Trap; Prompt-Compression-in-the-Wild cost caveat).
- Every item respects our invariants: eviction ≠ deletion (canonical log kept), no
  resident daemon, stdlib-only, GUI writes no state, verify-on-demand non-authoritative.
- Critique must reject over-engineering (the study warns: compression can cost more than
  it saves; summary drift; memory poisoning; context poisoning as a security surface).

**Declared budget.** claude executor (Max window, post-diet template −41%/turn);
1 divergence wave (5 ideators) + 1 critique wave (4 critics); research-profile budgets;
no wave 3.

## Phase 1 — Evidence matrix (verified 2026-07-12)

| claim | source | type | conf | maturity |
|---|---|---|---|---|
| Simple observation masking halves cost vs raw agent, matches/exceeds LLM summarization solve-rate; hybrid +7-11%; "trend toward pure summarization is questionable" | [Complexity Trap, arXiv:2508.21433, NeurIPS'25 DL4Code](https://arxiv.org/abs/2508.21433) | paper+code | forte | validado |
| Context-folding (branch→solve→fold to result+pointers) gives 10× smaller active context, beats summarization on Deep-Research + SWE | [Context-Folding, arXiv:2510.11967](https://arxiv.org/abs/2510.11967) | paper | forte | validado |
| Context window should be working memory / cache, not the permanent memory bank; effective context << nominal | study §Intro; [Lost-in-the-Middle](https://arxiv.org/abs/2307.03172), [RULER](https://arxiv.org/abs/2404.06654) | study+papers | forte | validado |
| Eviction from prompt ≠ deletion from storage (append-only log kept, prompt trimmed) | study §2.5; MemGPT [arXiv:2310.08560](https://arxiv.org/abs/2310.08560) | study+paper | forte | produção |
| Sharing agent-specific memories verbatim hurts; memory must be distilled + governed (provenance/lineage) | study §2.4; MemCollab, Governed Collaborative Memory | study | moderada | validado |
| Compaction should fire on semantic phase boundaries (subtask done/converging), NOT mid-derivation; adaptive triggers > fixed "every N" | study §4; Self-Compacting Agents | study | moderada | validado |
| Compression is a security surface (can strip safety instructions / hide malicious content) + a poisoning surface | study §6; Black-Box Attacks on Prompt-Compressed Agents | study | moderada | preliminar |

**Baseline — what the harness ALREADY has (do NOT rebuild):** records ledger (SPEC-112:
bounded hot-window 300 + unbounded archive + FTS index + compact handles — MemGPT/
PROJECTMEM modeled); minimal-first handoff with a token-budget demotion ladder (M1);
non-authoritative sha256+mtime context digest (SPEC-119, now on all review profiles);
WORKER_RESULT/REDUCE_RESULT/reviewer contracts with no-self-waiver; token-audit +
charsPerToken calibration; evolving-store poisoning/zombie/single-writer audits
(self-review I9/I11); F1 seed-digest folding (cross-workflow); secret-scan at collect.

**Named gaps (candidate backlog anchors):**
- **G1 — raw-log rotation/retention.** `events.jsonl`/`harness-trace.jsonl`/
  `validation-results.jsonl`/`worklog-archive.json` grow unbounded; rotation is a
  DEFERRED self-review nag (`eventsLogMaxBytes`), not code. Cheapest, deterministic.
- **G2 — no compaction/folding + no context-rot loop (the study's CORE gap).** Chat
  overseer delegates all context mgmt to the vendor CLI `/compact`; no harness-side
  folding of a completed subtask → result+pointers inside a live run; token-audit sizes
  plans but never triggers runtime cleanup; effective-context is displayed, never acted on.
- **G3 — shared memory: no confidence/validity/invalidation, no consolidation/decay, no
  contradiction detection.** Provenance exists; expiry/scoring/dedup-over-time/contradiction
  do not. Summary-drift undetected (only mtime/sha256 staleness).
- **G4 — experience→SKILL promotion absent** (rule + task promotion exist; skill rung empty).
- **G5 — no task DAG / hypothesis-claim table** (evidence index exists; don't rebuild that).

## Phase 2 — Briefs and gate

**Brief 1 — deterministic context hygiene (the lazy wins).** How might we close G1 (log
rotation) and the deterministic slice of G2 (masking/pruning recoverable content;
folding a completed workflow/subtask into result+pointers as a first-class routine) —
using masking/rotation/folding, NOT LLM summarization — respecting eviction≠deletion?

**Brief 2 — memory governance + drift/contradiction guards (G3).** How might we add
confidence/validity/invalidation + consolidation/decay + contradiction/summary-drift
detection to the shared stores (records/DECISIONS/digest), building on the existing
provenance + poisoning audits, without an LLM-heavy pipeline?

**Parked (future round):** context-rot benchmark for OUR effective context (G2 deep);
experience→skill promotion (G4); task DAG (G5). Deferred — need a signal first.

**Gate.** Scope/waves/budget pre-approved by the owner (this invocation, AFK autonomy).

## Phase 3 — Wave 1 (divergence)

`WF-20260712-115756-144579`, `research-divergence`, 5 ideators (simplicity,
performance, reliability, trust-boundary, analogy), claude executor. 5/5 fulfilled;
25 deterministic concepts, **zero** proposing an LLM-summarization pipeline. Heavy
convergence on the three named gaps → the orchestrator consolidated them into **5
candidate items** (below). Raw results: `<WF>/workers/*.result.json`.

## Phase 4 — Wave 2 (critique)

`WF-20260712-122315-173205`, `research-critique`, 4 critics (validity, architecture,
cost, security), `--seed` = the divergence reduce. All 4 completed with substantive
verdicts; the collect step *rejected* all four on a soft `summary > 1000 chars`
contract check (the payload verdicts are intact on disk — the orchestrator read them
directly; see backlog **M2**, which turns that brittle whole-result rejection into a
finding worth its own item). Consensus was **unanimous across all four lenses**:

| candidate | verdict (all 4 lenses) | key changes demanded |
|---|---|---|
| **G3b** digest drift gate | **KEEP — build first** | pure integrity re-hash; fire at `collect` only first, extend to `doctor` later |
| **R1** log rotation | KEEP-WITH-CHANGES | **exclude `events.jsonl`** (SPEC-109 owns it as transient); target persistent `runs/*.jsonl`; "seal" = scanned-with-verdict, hit-bearing → quarantine flag not silent archive; **fail-open on Windows/OneDrive rename locks**; gitignore the archive dir |
| **G3a** record governance | KEEP-WITH-CHANGES, split | ship `supersedes` + early-demotion only; contradiction rule = separate warn-only pure rule; **PARK `validUntil`/TTL** (no signal); superseded entries **demote-not-delete, stay searchable below live** (anti trust-laundering) |
| **F1** fold-on-finalize | KEEP-WITH-CHANGES, **last / low** | **not** `scrub --fold` (scrub is destructive) — standalone `workflow fold` verb, manifest-first + dry-run, verify FINISHED via **state-store not dir name**, absent scan/review verdicts → mark **UNSEALED** |
| **M1** runtime masking loop | **PARK (unanimous)** | no `stdoutBytes` signal exists; masking-before-measurement risks retry-cost inversion + secrets-at-rest; ship the **measurement rung only** |

## Phase 5 — Portfolio & prioritized backlog

Build order is the critics' unanimous sequence. Each item = one auditable commit;
every item respects the invariants (eviction ≠ deletion, no daemon, stdlib-only, GUI
writes no state, verify-on-demand). Evidence anchors are symbol/line-cited from the
worker results.

- **G3b — digest drift gate** *(build 1st; cheapest, pure win)*. Add
  `check_digest_drift(root, base)` to `context_digest.py` that re-hashes the
  "## Generated from" source table and returns any source whose sha256 changed since
  the digest was stamped. Call warn-only from `workflow collect`; reuse in
  `workflow doctor`. Closes G3-drift. *Deterministic, not summarization:* it is a
  sha256 compare of the already-stamped table — no model, no re-summarization.
- **R1 — size-gated write-path log rotation** *(build 2nd)*. One
  `_spill_if_over(path, max_bytes)` helper reused by the persistent JSONL writers
  (`harness-trace.jsonl`, `validation-results.jsonl`); archive-before-recycle under a
  gitignored `.harness/runs/archive/`; pass each sealed segment through the existing
  secret-scan and record the verdict (hit-bearing → quarantine flag, never silent
  archive); **fail-open** if the rename is locked (Windows/OneDrive). **Excludes
  `events.jsonl`** (SPEC-109 transient/compacted) and `worklog-archive.json` (a
  rewritten JSON array, not appendable JSONL). Closes G1.
- **G3a — record supersession + early demotion** *(build 3rd; phase 1 only)*. Add an
  append-only `supersedes` field to the `records.py` write path; superseded entries
  demote to `worklog-archive.json` ahead of the age-based `HOT_MAX` cut, drop from the
  `CONTEXT.md` head render, and **rank below live in FTS but stay searchable**. Phase 2
  (separate item, warn-only): a `self_review_rules.py` pure rule flagging any supersede
  whose target recorded a high/blocker outcome. Closes the deterministic slice of G3.
- **F1 — `workflow fold` (manifest + dry-run)** *(build last; low priority)*. New
  standalone verb (not `scrub`) that emits `fold-manifest.json` for a FINISHED workflow
  — per-artifact `{path, sha256, workerRole, secretScan verdict, reviewerValidated}` —
  and a dry-run byte-reclaim report. The destructive spill-to-archive stays a second,
  flag-gated step deferred until the report shows non-trivial savings. Fold on a
  non-FINISHED state (verified via state-store) is a hard error; absent verdicts render
  the stub **UNSEALED**. Closes the deterministic slice of G2.
- **M1 — stdout measurement rung** *(PARKED; ship the signal only)*. Record
  `stdoutBytes` per CLI invocation in `cost_metrics.py` + a pure threshold rule in
  `self_review_rules.py`. Actual masking is built only if that rule fires on a
  repeat-offender command (avoids retry-cost inversion + a secrets-at-rest surface).

**Also surfaced (own items, not part of the 5):**
- **M2 — collect validation should not discard a whole worker result on a soft-field
  overrun.** All 4 critics were rejected for `summary > 1000 chars` while their payload
  was valid. Truncate-and-warn on soft fields (summary) instead of rejecting the result.
- **PARKED-pending-signal:** G3a `validUntil`/TTL; M1 runtime masking; the deep G2
  context-rot benchmark; G4 experience→skill; G5 task DAG (from Phase 2).

## Extensão R3 — Memória governada (rodada D012, 2026-07-18)

Rodada 3 de 5 da diretiva D012 (NVIDIA, sequencial, backlog-first). Retoma o N6
diferido ("valid-until sem trigger que dispara = teatro") e o desenho §6.2 do
artigo (lifecycle candidate→validated→active→challenged→expired; 7 camadas;
eval adversarial). WFs: divergência `WF-20260718-221656` (5 ideators, 4/5
válidos, 12 concepts), crítica focada `WF-20260718-222004` (2 críticos:
validade+arquitetura/segurança).

**O achado que fecha o N6 (convergente entre ideators):** o challenge trigger
NÃO é mtime (sempre fresco = teatro) — é ancorado a sinais determinísticos reais:
**git HEAD SHA** (contra um `anchoredCommit` gravado no item) e **SHA256 do(s)
lockfile(s)** de dependência. Ambos disparam em evento de mudança real,
verificáveis por stdlib (`subprocess git` / `hashlib`).

**O achado da crítica que corrige o desenho (BLOCKER de design, ambos críticos):**
um trigger de commit-SHA que dispara em TODO commit é **over-expiry por
construção** — expira memória ainda válida (tão ruim quanto manter obsoleta). A
correção é **scope-match**: challenge SÓ os itens cujo `scopeTag` de proveniência
intersecta `git diff --name-only` (ou o pacote afetado no lockfile). E
**challenge ≠ delete**: o estado `challenged` só pede re-validação; `expired`/
`revoked` são transições governadas separadas (o artigo já separa as operações).

**BLOCKER de segurança (crítico de arquitetura, tratado como gate de design, não
incidente):** nenhum candidato pode deixar memória recuperada adquirir autoridade
de política (OWASP poisoning). Exige o **provenance firewall**: no retrieval,
`active_memory.authority < signed_policy.authority` sempre; a tríade C4+C5+C8
(firewall + sensitivity gate + eval) é pré-requisito de qualquer trigger.

### Portfólio de design (R3)
| card | realiza | mecanismo | disparo real | controle de over-expiry |
|---|---|---|---|---|
| **GM-1 lifecycle scope-matched** | lifecycle + challenge-trigger | estados candidate→validated→active→challenged→expired; anchoredCommit por item | git HEAD SHA **∩ git diff --name-only com scopeTag** | challenge≠delete; só re-valida |
| **GM-2 lockfile-scope trigger** | challenge-trigger | SHA256 do lockfile + sub-tag por pacote | hash muda **E** item tagueado no pacote | challenge só o dep afetado |
| **GM-3 provenance firewall** | trust-layer | retrieval recusa memória com authority ≥ policy | — (invariante) | — (é a guarda de poisoning) |
| **GM-4 retrieval ordering** | retrieval-order | sort: scope→validez→challenge_state→confidence→sensitivity ANTES de similaridade | — | challenged ordena abaixo de active, acima de expired |
| **GM-5 shadow-challenge ledger** | adversarial-eval | mede error-following/stale-use/negative-transfer/recovery em shadow (measure-before-enforce, à la EXP-18) | meta (a eval é o gatilho) | graduação por métrica+threshold owner-gated |
| **GM-6 tombstone/revogação** | schema/lifecycle | revoked mantém tombstone assinado; delete físico segue privacidade | contradição/observação negativa | audita replay window |

### Operações e veredito
GM-1/2 **mantidas** com a emenda scope-match (sem ela, rejeitadas por over-expiry).
GM-3 **mantida como pré-requisito** (a tríade de segurança é mandatória antes de
qualquer trigger ir a shadow). GM-4/5/6 **mantidas**. **N6 DESBLOQUEADO em
desenho:** a peça que faltava (trigger que dispara sem teatro E sem over-expiry)
é o scope-match ancorado em SHA — mas a metade de ENFORCEMENT segue owner-gated
(gatilho N6 original: 1ª claim vencida que engane um run). O que fica pronto:
o desenho completo + o shadow ledger (measure-only) como 1º passo committável
quando o owner autorizar a fila.

**Limite honesto:** sem `scopeTag` de proveniência nos itens de memória hoje, o
scope-match exige um passo de tagueamento (gravar quais paths/deps cada memória
referencia). Isso é o custo real que o N6 original chamou de "writer changes" —
agora dimensionado: é um campo por item + o diff-intersect no challenge, não uma
reescrita. Candidato a shadow-probe measure-only (mede quantos itens SERIAM
challenged por commit) antes de qualquer enforcement.
