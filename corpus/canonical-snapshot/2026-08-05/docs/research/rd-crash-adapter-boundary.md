# RD-CRASH — injeção determinística de crash na fronteira do adapter (Windows)

Dossiê de research (lane scanner, 2026-07-21), pré-requisito do EXP-21
(crash-injection recovery sem órfãos/duplicatas, ATAM A13/A6). Tudo verificado
em fonte. Persistido aqui para não morar em memória transiente (owner: as
estruturas amarram o processo, não a memória do agente).

## (a) A fronteira exata por seam

Os 3 seams compartilham o formato: **spawn → await do término → ler returnCode →
extrair/validar WORKER_RESULT → classificar**. O crash é observado no await + no
ramo "sem result / rc≠0".

- **SEAM 1 bounded** (`harness.py:1511 run_one_worker`): await em
  `processes.py:440 proc.communicate(timeout=...)`; parse `harness.py:1560
  extract_worker_result`; classificação "morreu sem receipt" a jusante em
  `harness.py:1628-1629` (`result_path.exists()` + `validate_worker_result`).
- **SEAM 2 async** (`async_runtime.py:351`): spawn `:431
  create_subprocess_exec`; await `:448 wait_for(proc.wait())`; árvore decisória
  `:523-561` — `:531 result_path.exists()` → valida; `:554 rc==0` →
  `missing`; `:558 else` → `failed` rc≠0 (**o ramo do crash**).
- **SEAM 3 detached** (`async_runtime.py:840 Popen` via `processes.py:226
  launch_detached`): SEM await; a fronteira é `workflow_async_recover`
  (`:296`) — `supervisor_alive` (:305), por tarefa `not process_alive(pid)`
  (:321), result válido → fulfilled (:314-320), supervisor morto sem result →
  `orphaned` (:329); guarda :327 evita corrida com o próprio settle.

## (b) Mecanismo recomendado: stub-worker gated por env var (funde 3a+3b)

Padrão já existente: `testing/scenarios/_rt6_stub_worker.py` spawnado pelo seam
real via `commandTemplate` do executor. Um `_exp21_crash_stub.py` gêmeo lê
`HARNESS_CRASH_AT` e crasha num ponto do **próprio código**:
- `pre_result` → `sys.exit(3)` antes do WORKER_RESULT → async:558 (rc≠0 sem
  receipt), o A13 "crash-antes-de-receipt".
- `exit0_no_result` → `sys.exit(0)` sem receipt → async:554 ("missing").
- `post_result` → escreve result válido, depois `sys.exit(3)` → idempotência
  (recover marca fulfilled sem re-spawn).
- `partial_write` → JSON truncado → `validate_worker_result` rejeita.

**Determinístico no Windows** porque o ponto de crash é uma LINHA do fluxo do
worker, disparada por env var — sem corrida de scheduler; `sys.exit(rc≠0)` dá
returncode limpo e estável que o `wait()`/`communicate()` do pai lê igual nos 3
seams, reproduzível em CI. Worker é filho real do seam real (sem mock).

**Variante** `os.abort()` (crash nativo duro, 0xC0000409): rebaixada porque o
returncode é menos limpo para asserção E dispara o Windows Error Reporting — em
CI exige `SEM_NOGPFAULTERRORBOX`/SetErrorMode. `sys.exit` é o default.

**Rejeitados:** (1) matar a árvore via `signal_process_tree` num ponto escolhido
pelo PAI = corrida de timing (o pai não sabe quando matar) — mantido SÓ para o
SEAM 3, e mesmo lá determinístico só com **sentinel-file gate** (worker escreve
sentinel; teste espera; então mata o supervisor). (2) timeout como proxy de
crash = já coberto e é sobre timing, não prova A13.

## (c) Detecção órfão/duplicata (seams verificáveis)

**Sem órfãos:** pids registrados (`task["pid"]`, `group["supervisorPid"]`) →
`processes.pid_alive(pid) is False` (`:135`, nt via OpenProcess — no Windows não
há /proc, então pid registrado é o seam). `git worktree list` limpo (write
worker usa `controlled_writes.create_temp_workspace :189`). Locks/holds:
`.harness/workflows/active` + `workflow_lock_path` + `scenario_isolation.
_recover_stale_holds :248` (o ramo N3/F2 :280 recusa pid vivo, recupera pid
morto). Grupo settled pós-`workflow_async_recover`.

**Sem duplicatas:** a idempotência já é codada keyando em `result_path.exists()`
(failover `:585`; recover `:314-320` marca fulfilled sem re-spawn). Provar:
`post_result` + recover → result escrito 1× (mtime estável); efeito externo 1×
mesmo com re-spawn; `_record_executor_outcome :336` registra 1× no breaker
(:343 garante no-double-count).

## (d) Esqueleto do exp21

`testing/scenarios/exp21_crash_injection.py` (+ `_exp21_crash_stub.py`, prefixo
`_` fora do gate-glob): para cada seam × fase → montar WF 1-worker com executor
= crash-stub, rodar pelo seam REAL, asserir classificação, rodar recover (asserir
idempotência), asserir sem-órfãos (pid/worktree/hold/settle) e sem-duplicatas
(efeito 1×, mtime estável, breaker count 1), self-check no `__main__`.

## Questões abertas ANTES de codar o EXP-21 (owner-gated)

1. **[PRÉ-REQUISITO POSSÍVEL] Ledger de efeito para contar duplicatas.** Não há
   contador de efeito único explícito no código — o teste teria que usar mtime
   do result-file + refs de record. É suficiente, OU o EXP-21 exige o enabler
   **E-EFFECTID** (idempotency-key, `article-coverage-backlog.md:393`) PRIMEIRO?
   Decisão de sequenciamento.
2. `sys.exit(3)` default vs a variante `os.abort` (crash nativo) — entra no
   EXP-21 ou fica para depois? Confirmar supressão de WER em CI.
3. Determinismo do SEAM 3: o kill do supervisor precisa de sentinel-gate +
   `signal_process_tree`. Conta como "determinístico", ou o A13 mira só
   bounded+async (crash 100% no código do worker, zero sinal externo)?
4. Quem poda a temp-workspace/worktree de um worker morto antes do merge (o
   pruner do R1)? É o que a asserção "sem worktree órfã" verifica.
5. **Alvo primário do A13:** cobrir os 3 seams parametrizados, ou só a fronteira
   async (a de produção mais quente)?

## Recomendação (arquiteto)

O mecanismo (b) está pronto para codar bounded+async SEM novo pré-requisito — o
crash é 100% no código do worker e a idempotência via `result_path.exists()` já
existe. A questão 1 (E-EFFECTID) só morde a asserção "sem duplicata" se quisermos
um contador FORTE em vez de mtime+refs; para um primeiro EXP-21 measure-only,
mtime+refs basta e o E-EFFECTID vira follow-up se a medição mostrar ambiguidade.
O SEAM 3 (detached) é o único que precisa do sentinel-gate — proponho EXP-21 fase
1 = bounded+async (determinístico puro), SEAM 3 = fase 2 com o sentinel.
