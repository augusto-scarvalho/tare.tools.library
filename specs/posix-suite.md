# POSIX suite over WSL — dated record, doctor staleness, linux arm only

Status: proposed 2026-07-29 (acceptance: `testing/scenarios/rh_repo_health.py`
doctor row + `posix_suite` self-check).
Door NEW: row `the-posix-suite-is-runnable-via-wsl-but-` (2026-07-27) — the
capability existed only as prose in two places, which is the exact
capability-decay failure the harness keeps fixing elsewhere.

## Goal

The POSIX suite runs today on this machine via WSL2 (clone into the WSL
filesystem, NEVER over /mnt/c, so scenarios cannot write the live Windows
`.harness/`); its first real run found a P1 cross-platform defect. Make that
repeatable and DATED so "we ran it" cannot decay into "someone ran it once":
a runner that records {at, sha, results}, and a doctor row that notices decay.

## Applicability

- `scripts/harness_lib/posix_suite.py` — `run` (clone + named scenario subset
  + record), `last_run`, `doctor_check`, `wsl_available` (probe gated by
  `HARNESS_POSIX_PROBE`), module entry points `--run` / `--status`.
- `scripts/harness_lib/repo_health.py` — carries the `posix-suite` doctor row.
- `.harness/runs/posix-suite.json` — class-D machine-local record.

Does not cover: darwin (see Non-goal), a `harness.py` verb (module entry
point is the surface; a registry bump is deliberate scope another day), CI.

## Requirements / invariants (numbered, testable)

1. **Never over /mnt/c.** The run clones into `~/harness-posix` inside the
   WSL filesystem; the Windows tree is source-only. A scenario running there
   cannot touch the live `.harness/`.
2. **Dated record.** Every run writes `{at, arm: "linux-wsl", sha, cloneRc,
   scenarios: {name: rc}, pass, fail, tail}` to `.harness/runs/posix-suite.json`.
3. **Doctor decay row.** `posix-suite`: WSL available + no record -> warn
   (run it); record > STALE_COMMITS behind HEAD -> warn (re-run); fresh ->
   ok naming the sha. No WSL / probe disabled -> ok "not probed". Fail-open
   at every layer.
4. **Deterministic in fixtures.** `HARNESS_POSIX_PROBE=0` disables the
   machine probe; `rh_repo_health` sets it so no scenario ever spawns wsl.
5. **Non-goal, enforced by wording.** WSL has /proc, so `_kill_platform()`
   reads "linux" and every darwin arm stays unexercised. The record's `arm`
   field and BOTH doctor details say "linux" explicitly — a green run here
   must never read as POSIX coverage. darwin needs a real macOS host
   (`proc-darwin-*` rows stay parked).

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Record + doctor, não só runbook | a própria row: "leaving it in prose repeats the pattern being fixed"; mesmo desenho de graph-staleness/release-staleness (contrapeso WARN datado) |
| Clone dentro do WSL FS | medição 2026-07-27: rodar sobre /mnt/c arriscaria escrever no .harness vivo do Windows; o clone isola por construção |
| Entry point de módulo, sem verbo | precedente test_quality_ast --record / prompt_slots --snapshot; bump do cli_registry é escopo deliberado |
| Probe com kill-switch | lição SEC.8/rh na mesma noite: check machine-scoped sem env-gate quebra fixtures em qualquer outra máquina |

## Test strategy

- Behaviors: self-check hermético (kill-switch, doctor arms sem WSL, record
  round-trip, conversão /mnt/<drive>, parse de rc); rh pina a row na IDS com
  probe desligado; um `--run` real cunhou o record no ship (sha do HEAD,
  smoke 3/3).
- Edge cases: sem git (sha None -> warn "no recorded run"), record rasgado
  (last_run None), wsl ausente/pendurado (timeout 15s -> not available).
- Regression risks: doctor raise (fail-open shape testado), scenario spawn de
  wsl (proibido via env no rh).
- Coverage: rh-1/rh-2 (IDS + statuses) + self-check subprocess-free.

## Validation

- `python scripts/harness_lib/posix_suite.py` — self-check hermético.
- `python scripts/harness_lib/posix_suite.py --run [nomes...]` — corrida real
  (smoke default `cec_exit_codes`); `--status` — record + doctor.
- `python testing/scenarios/rh_repo_health.py` — a row `posix-suite` na IDS.

## Ceilings (upgrade paths)

- Verbo `harness.py posix-check` + frozen bump quando a rotina merecer CLI.
- Subset maior que o smoke (lista nomeada por perfil) quando o custo/valor da
  bateria completa em WSL for medido.
- darwin: fora daqui por definição; exige host macOS real ou remoto.

## Amendments

(none yet)
