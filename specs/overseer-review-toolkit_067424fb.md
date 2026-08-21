# Overseer review toolkit (`ort`)

Status: proposed 2026-07-13 (acceptance: testing/scenarios/orv_overseer_toolkit.py).

Intake (SPEC-116 door NEW): owner decision — migrate the AFK-loop overseer
from Fable 5 to Opus 4.8 xhigh; the mechanical half of the review ritual must
become tooling so the cheaper overseer runs the same safety net. Grounded in
research rounds agent-communication-protocols (G1 unmeasured economy, G3
typed envelopes) and the 2026-07-13 live incidents: the blank-line burndown
fraud (gates green, diff poisoned), CP1252 rewrites, and prose-only
divergence reports.

## Goal

Three instruments: (1) `harness.py review [--plan <brief>]` — deterministic
worker-diff checks vs HEAD (footprint, blank-deletion fraud signature,
HEAD-attributed mojibake delta, removed-assertion gaming), advisory rc 0;
(2) a typed `planDeviations` field in WORKER_RESULT so plan-vs-code
divergences are machine-readable evidence; (3) an `outcome` verdict on
delegation ledger records with a `byOutcome`/`outcomeShares` rollup so lane
yield is a number.

## Applicability

Applies to `harness_lib/overseer_review.py` (+ `review` verb, frozen surface
+1), `schemas/worker-result.schema.json` + `result_contracts.py`
(`planDeviations`, hard-error shape validation), `cost_metrics.py`
(`record_delegation outcome=` + summarize rollup) and the `delegation` verb
(`--outcome`). The overseer-loop playbook v2 consumes all three.

## Requirements / invariants (numbered, testable)

1. **Review is advisory and deterministic.** `review` always exits 0; rows
   are ok/WARN/info/skip. Footprint parses backticked paths under the plan's
   `## File footprint` heading and exempts `.harness/{state,context,handoff}`
   bookkeeping; blank-fraud fires only past both thresholds (>50 blank
   deletions AND >30% of deletions); mojibake counts are HEAD-attributed
   (only positive deltas reported) and lines carrying the `mojibake-ok`
   marker are exempt (detector definitions, planted fixtures); gaming counts
   removed `assert`/`check(`/`Scenario:[` lines.
2. **planDeviations is typed evidence.** Optional, ≤10 items, each exactly
   `{planSaid, codeIs, action}`, strings 1..200 chars; malformed shape is a
   HARD validation error (unreadable evidence is worse than none); absent
   field remains valid (schema `additionalProperties: false` forces the
   declaration).
3. **Outcome feeds yield.** `delegation --outcome kept|partial|rejected|
   reworked` lands on the record; `metrics` exposes
   `delegations.byOutcome` (token stats per verdict) and `outcomeShares`;
   pre-toolkit records group under `(none)` — no migration.

## Gherkin scenarios

```gherkin
Feature: overseer review toolkit

  Scenario: [ort-1] the review verb catches all four fraud classes
    Given a repo where a worker escaped its footprint, stripped blank lines
      past both thresholds, added mojibake and deleted an assert
    When review runs with the plan brief
    Then footprint, blank-fraud, mojibake-delta and gaming all WARN, and a
      clean tree afterwards reports zero warnings

  Scenario: [ort-2] planDeviations validates as typed evidence
    Given an otherwise-valid WORKER_RESULT
    Then a well-formed deviations list passes, and wrong keys, oversize
      strings and an 11th item each fail with a planDeviations error

  Scenario: [ort-3] outcome lands on the ledger and the rollup
    Given a delegation recorded with an outcome
    Then metrics exposes it under delegations.byOutcome, and the review and
      oracle verbs answer --help on the frozen surface
```

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Advisory rc 0, nunca gate | idiom medição-antes-de-controle (security-baseline); o overseer julga, a ferramenta reporta |
| Assinatura de fraude com DOIS limiares | o incidente real: 325 brancos de 431 remoções; limiar único geraria ruído em refactors legítimos |
| Delta de mojibake atribuído por HEAD | disciplina do dia: 229 artefatos pré-existentes no backlog nunca foram culpa de worker |
| Marcador `mojibake-ok` | o detector flagrou a si mesmo no primeiro run live; exceção explícita > lista hardcoded |
| planDeviations shape-hard | evidência tipada ilegível é pior que ausente; G3 do round de comunicação |
| Evidência | incidentes 2026-07-13 (fraude burndown, reescrita CP1252); rounds agent-communication-protocols G1/G3 |

## Test strategy

- Behaviors: as quatro classes de WARN + árvore limpa (ort-1); aceitação e
  três recusas de shape (ort-2); rollup + superfície (ort-3).
- Edge cases: plano sem seção de footprint → skip legível; arquivos de
  bookkeeping do loop isentos; registros antigos sem outcome agrupam em
  `(none)`.
- Regression net: cli_registry (superfície +2), rs_research_skill +
  wf_failover (validação WORKER_RESULT inalterada nos caminhos existentes).
- Coverage: deterministic — `testing/scenarios/orv_overseer_toolkit.py`.

## Amendments

### v2 (2026-07-28) — the lane cleanup contract becomes a check

`footprint` answers "did the worker write OUTSIDE its boundary?". On 2026-07-28
a probe lane wrote a repo tarball, an extracted worktree and a UTF-16 JSON
INSIDE its declared boundary; footprint correctly reported no violation, and
nothing asked whether the box had been emptied. Four structural gate checks went
red six minutes later (`release-hygiene:generated-artifacts`,
`release-hygiene:local-absolute-paths`, `json:*`,
`directory-guide:nested-readmes`) — three of them naming symptoms, none saying a
worker left scratch behind. The obligation existed only as playbook prose
("always carry the cleanup contract"), i.e. in the overseer's memory, and the
overseer forgot. Owner: *"porque confiar em prosa? Esse processo não poderia ser
determinístico?"*

5. **Declared scratch must be gone.** A brief may declare paths under a
   `## Cleanup contract` heading. Any declared path that still EXISTS when
   `review --plan` runs is reported (`scratch:leftover`).
6. **A run-dir grant demands a contract.** A `## File footprint` entry under
   `.harness/runs/` with no `## Cleanup contract` section is reported
   (`scratch:undeclared`) — the omission itself, caught at review time in ~1s
   instead of by the gate 6 minutes later under a misleading name.
7. **Inert by default.** A brief with neither a scratch declaration nor a
   `.harness/runs/` grant gains no rows. Both rows are WARN, never fail:
   `review` reports, the overseer judges (measurement before control, unchanged).
8. **Declarations open lines; mentions do not.** Scratch paths parse only from a
   path that OPENS its line (bare or backticked, optional bullet). The
   footprint's greedy any-backtick-on-the-line rule swallowed a `.harness/runs/`
   written mid-sentence and reported the run dir itself as leftover — found by
   hand while building this, then pinned as a mutant.

| Decisão | Fontes |
|---|---|
| Check it at review time, not only at the gate | incident 2026-07-28: the gate already caught it, 6 min late and attributed to release-hygiene |
| Declared, not auto-swept | auto-deleting a worker's output before the overseer reads it destroys evidence — that lane's measurement file was recoverable only because the artifacts still existed |
| WARN, not fail | `review` is advisory by design (module contract); a false failure here would sit on every integration |
| Stricter parse than the footprint | measured: the greedy rule pulled a prose mention and produced a false leftover |

### v3 (2026-07-30) — an unparseable footprint is a WARN, not a silent skip

`check_footprint` returned status `skip` when the plan yielded zero paths. A
`skip` counts as nothing, so `review()` reported `warnings: 0` and the verdict
read *"clean: mechanical checks green — proceed to divergence judgment"* on a
plan whose boundary had never been checked at all. Silent SKIPs were observed
live on 2026-07-29 during the SPEC-173 rounds: the loudest instrument in the
ritual answered "green" precisely when it had nothing to say.

Honest fact-check of the suspicion that opened this round: the feared
`## Hard footprint` heading mismatch does **not** exist in this corpus. The
dominant form is `## File footprint (HARD)`, and the parser matches by prefix
(`line.startswith(FOOTPRINT_HEAD)`), so it already parses. **No heading alias
ships** — the real defect class was the silent pass, not the heading.

1. **(addendum)** Zero parsed footprint paths report `WARN`, never `skip`: an
   unparseable boundary is UNREVIEWABLE, not clean. The detail names both
   possible causes — heading missing/misnamed, or bullets that are not path-like
   (`/` or a `.py`/`.md`/`.json` suffix) — and states the expected heading
   literal. Review stays advisory: rc is still 0, the WARN counts toward
   `warnings` and lands on the shared defect sink as `kind: review-warn` like any
   other row. This supersedes the Test-strategy edge case "plano sem seção de
   footprint → skip legível".

| Decisão | Fontes |
|---|---|
| WARN em vez de skip | incidente 2026-07-29 (rounds SPEC-173): verdict "clean" com o check de fronteira nunca executado |
| Sem alias de heading | fact-check do corpus: `## File footprint (HARD)` já casa pelo prefixo; alias seria código para um defeito inexistente |
| rc continua 0 | invariante 1 (medição antes de controle) permanece — a ferramenta reporta, o overseer julga |
| Detail nomeia as DUAS causas | quem lê o WARN precisa saber se conserta o heading ou os bullets, sem abrir o parser |

## Validation

- `python testing/scenarios/orv_overseer_toolkit.py` — ort-1..ort-5 green
  (ort-4 covers v2: leftover WARN, ok after scrub, undeclared-grant WARN, inert
  on an ordinary brief, prose-mention not parsed as a declaration; ort-5 covers
  v3 in both directions: unparseable footprint → WARN naming the heading and
  `warnings >= 1`, well-formed footprint → not WARN). Mutation
  evidence: leftover detection stubbed → ort-4 red; undeclared detection stubbed
  → ort-4 red; greedy parser restored → ort-4 red; `skip` restored → ort-5 red.
- `python scripts/harness_lib/overseer_review.py` — module self-check.
- `python testing/scenarios/cli_registry.py` — frozen surface.
- `python scripts/spec_test_gate.py spec-pack --no-project-commands` green.
