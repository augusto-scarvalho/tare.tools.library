# Rodada RD-CRASH — injeção de crash determinística na fronteira do adapter (Windows)

Research-gated backlog item RD-CRASH. 2ª das 3 rodadas de implementação-research
(owner 2026-07-19). Orquestrador = esta sessão. Divergência via **NVIDIA**
(`nvidia-compat`, glm-5.2).

## Por que esta rodada existe

**EXP-21** (medir recovery: duplicate-effect, orphaned work, time-to-resume) e a
fixture de recovery precisam de um jeito de FAZER o worker/adapter crashar de forma
**determinística e reprodutível** — senão a medição de recovery é flaky (um crash
que às vezes acontece não é um experimento). O harness roda em **Windows**
(PowerShell + subprocess), onde os sinais POSIX (SIGKILL/SIGSEGV) não existem do
mesmo jeito. Research de COMO IMPLEMENTAR o injetor, não de medição.

## Pergunta da rodada

> Como injetar um crash **determinístico e reprodutível** na fronteira
> adapter/worker do harness no **Windows** (subprocess criado via
> `harness_lib/processes.py` / `sandbox_spawn.py`), de forma que EXP-21 possa medir
> recovery sem flakiness — cobrindo os modos de crash que importam (morte abrupta
> do processo, hang/timeout, saída parcial/truncada, exit-code não-zero) e sem
> contaminar o harness pai?

## Critérios de sucesso

- **Atores:** o EXP-21 (dispara o crash num ponto controlado e mede recovery), a
  fixture de recovery (regressão), o harness pai (deve sobreviver + recuperar).
- **Determinístico:** o mesmo gatilho produz o mesmo crash no mesmo ponto — um
  "crash na chamada N" ou "crash após emitir K bytes", não um kill aleatório.
- **Windows-real:** funciona com o modelo de processo do Windows (sem depender de
  SIGKILL/SIGSEGV POSIX). Reusa o `subprocess`/Job Object que o `sandbox_spawn` já
  monta (SPEC-148/151).
- **Cobre os modos que importam:** (a) morte abrupta (processo some), (b) hang
  (nunca retorna → timeout), (c) saída parcial (stdout truncado no meio do
  WORKER_RESULT), (d) exit-code sujo. Cada um exercita um caminho de recovery
  diferente.
- **Não contamina:** o crash fica CONTIDO no worker; o harness pai não morre junto,
  e o injetor é opt-in (só em EXP-21/fixture, nunca em produção). Reusa o breaker +
  gate-hold auto-recovery que já existem.

## Orçamento + largura + design declarado

- **Onda 1:** 5 ideadores NVIDIA, teto ~65k tok (free-tier). Gate a 60%.
- **Largura (D010): EXPLORATÓRIA → 5.** Fault-injection cruza chaos engineering,
  modelo de processo Windows (Job Objects, TerminateProcess, exit codes), seams de
  teste (fault points determinísticos), e emulação de sinais — campo técnico amplo.
- **Design (L18):** a rodada FEEDA o EXP-21 (medição de recovery, owner-gated).
  Carta de método candidata (advisory dispara pós-e5a1a4b): a família crash/recovery
  não tem carta própria ainda; o design experimental do EXP-21 usa noise-floor +
  matched controls. A carta final entra na síntese.

## Fase 3 — brief da onda 1

> Projete o mecanismo de injeção de crash determinística na fronteira adapter/worker
> do harness no Windows. O harness cria workers via subprocess (Python/PowerShell,
> com Job Object do sandbox_spawn SPEC-148/151). Precisa: (1) ser DETERMINÍSTICO —
> o mesmo gatilho crasha no mesmo ponto (ex.: "morre na chamada N", "morre após K
> bytes de stdout"), reprodutível entre execuções; (2) funcionar no modelo de
> processo do WINDOWS sem depender de SIGKILL/SIGSEGV POSIX (usar
> TerminateProcess/Job Object/exit codes, ou um fault-point cooperativo dentro do
> worker via env var); (3) cobrir 4 modos: morte abrupta, hang/timeout, saída
> parcial/truncada, exit-code sujo — cada um exercita um caminho de recovery
> diferente; (4) ficar CONTIDO (o harness pai sobrevive e recupera) e ser opt-in
> (só EXP-21/fixture, jamais produção); (5) reusar o breaker + gate-hold
> auto-recovery + o Job Object do sandbox que já existem. Entregue: o MECANISMO
> (fault-point cooperativo via env vs kill externo via Job Object — com trade-off),
> como cada um dos 4 modos é disparado deterministicamente, e o ponto exato de
> instrumentação no processes.py/sandbox_spawn.py.

---

# Fase 3-5 — resultado e síntese (RD-CRASH)

Onda 1: `WF-20260719-055620-000806`, 5 ideadores NVIDIA (glm-5.2).

## Convergência independente

**Mecanismo = HÍBRIDO** (w-001, w-003, w-004, w-005 convergem):
- **Fault-point COOPERATIVO via env `HARNESS_CRASH_AT`** DENTRO do worker, para os
  modos (a) morte abrupta, (c) truncado, (d) exit sujo — porque só o cooperativo
  garante o PONTO EXATO. Razão técnica dura (w-002): um kill EXTERNO **não** garante
  truncar no meio do JSON — o OS pode dar flush no buffer do pipe antes do
  TerminateProcess pegar. Determinismo exige o worker se matar no ponto.
- **Kill EXTERNO via Job Object** (o do sandbox_spawn SPEC-151) só para o modo (b)
  hang — um worker travado não se mata sozinho; o Job Object do pai o ceifa no
  timeout. Zero runtime de processo novo.

**Gatilhos determinísticos — TODOS por contador, nunca probabilístico** (w-005
contrasta explícito com o `FAIL_MAKE_REQUEST` probabilístico do kernel Linux):
| modo | gatilho | ação no worker |
|---|---|---|
| (a) abrupta | `HARNESS_CRASH_AT=abrupt:call=N` | `os._exit()`/`os.abort()` na chamada N, sem flush |
| (b) hang | `HARNESS_CRASH_AT=hang:after=N` | bloqueia pra sempre → Job Object do pai mata no timeout |
| (c) truncado | `HARNESS_CRASH_AT=partial:bytes=K` | escreve K bytes de stdout, aí `os._exit()` — JSON cortado no meio |
| (d) exit sujo | `HARNESS_CRASH_AT=dirty:code=N` | `sys.exit(N)` não-zero + stderr |

## Ponto de instrumentação — a tensão que a rodada expôs (e resolveu)

Os workers DISCORDARAM de onde mora o guard (sinal honesto):
- w-002: "processes.py é o caminho de PRODUÇÃO — instrumentar lá vaza lógica de
  crash pra produção." w-003: "no bootstrap do WORKER, NÃO no processes.py."
- **Resolução (síntese):** o crash cooperativo mora no **entrypoint do worker**
  (lê `HARNESS_CRASH_AT` no startup — self-contained, custo ZERO quando o env está
  ausente). O `processes.py` só **propaga** a env var (~3 linhas) e lê exit/stdout
  como já faz. O `sandbox_spawn.py` **não muda** — só provê o Job Object pro modo
  (b). Isso satisfaz o w-002 (nada de lógica de crash no caminho de produção
  compartilhado) E o "JAMAIS em produção" (guard por ausência de env).

## Armadilhas reais (w-004 segurança + w-002 escala)

- **Exit codes (w-004):** o modo (d) NÃO pode colidir com códigos de falha real do
  Windows (ex.: `0xC0000005` = access violation) — senão o pai lê um crash FAKE
  como falha OS real. Usar códigos reservados do harness, não-colidentes.
- **Scrub do truncado (w-004):** o modo (c) corta stdout no meio do JSON, que pode
  conter campo de secret PARCIAL — o pai NÃO pode persistir o buffer truncado cru;
  scrub antes de logar. Reusa o secret-scan que já existe.
- **Env scoping (w-002):** Windows herda env por padrão — `HARNESS_CRASH_AT` no
  processo PAI faria TODOS os workers paralelos crasharem. Tem que ser escopado ao
  dict de env do subprocess ESPECÍFICO, nunca no pai.
- **maxWorkerOutputChars (w-002):** o ponto de truncagem do modo (c) tem que ficar
  DENTRO do limite, senão o recovery não distingue crash-truncado de oversize-reject
  normal.
- **Job Object no modo (b) (w-004):** o kill externo tem que ir pelo Job Object
  (mata a árvore toda), não TerminateProcess no PID do worker direto.

## Analogias comprovadas (w-005)

- **SQLite crash-injection VFS shim** (`sqlite3_crash.c` intercepta I/O em offsets
  determinísticos) = o fault-point cooperativo no byte K. Referência forte (o
  crash-testing do SQLite é lendário).
- **Netflix Chaos Monkey** opt-in por flag, só em ambiente de teste = o gate
  `HARNESS_CRASH_AT` (jamais produção).
- **Disjuntor + fusível elétrico:** disjuntor protege o upstream (pai), fusível é a
  falha deliberada (worker) — mapeia no breaker que já temos.

## Operação

| carta | operação | por quê |
|---|---|---|
| **CRASH-HYBRID** (cooperativo a/c/d + Job-Object b) | **mantida** — o núcleo | só o híbrido cobre os 4 modos com determinismo real |
| **CRASH-COOP-WORKER** (guard no entrypoint do worker) | **mantida** | mantém lógica de crash FORA do caminho de produção (resolve a tensão w-002/w-003) |
| **exit-code não-colidente + scrub do truncado** | **dividida (regras de segurança)** | dobram no spec do injetor; achado do w-004 |
| **injetor probabilístico** | **rejeitada** | EXP-21 precisa determinístico; probabilístico (kernel Linux) é o anti-padrão aqui |

## Buildável vs owner-gated

- **Buildável (test-infra) quando o owner abrir EXP-21:** o módulo cooperativo
  `HARNESS_CRASH_AT` no entrypoint do worker + a propagação de 3 linhas no
  processes.py + a fixture de recovery. É tooling de teste, opt-in, zero-custo em
  prod. Mas só faz sentido COM a medição.
- **Owner-gated:** o EXP-21 em si (medir duplicate-effect/orphaned-work/
  time-to-resume) já era owner-gated. RD-CRASH entrega o injetor que ele precisa.

## Rastreabilidade

| Evidência | Ideia | Experimento | Task | Status |
|---|---|---|---|---|
| 4/5 (híbrido) + w-002 (flush-race) + SQLite VFS (w-005) | CRASH-HYBRID + CRASH-COOP-WORKER | habilita EXP-21 | RD-CRASH→injetor | desenhado (build com EXP-21, owner-gated) |
| w-004 (exit-code/scrub/Job-Object) | regras de segurança do injetor | — | parte do spec | desenhado |
