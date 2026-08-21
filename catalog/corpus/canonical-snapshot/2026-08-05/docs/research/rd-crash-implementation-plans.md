# Planos de implementação — Crash injection determinística (RD-CRASH)

Parqueado no backlog. Derivado de `rd-crash-injection-round.md` (5 ideadores NVIDIA) + D022.
Habilita **EXP-21** (medir recovery: duplicate-effect, orphaned-work, time-to-resume) + a fixture
de recovery. Windows-real (sem SIGKILL/SIGSEGV POSIX).

**Reuso:** `scripts/harness_lib/processes.py` (o spawn de subprocess — propaga a env); `sandbox_spawn.py`
(o Job Object SPEC-151 — mata o modo hang); o circuit breaker + gate-hold auto-recovery (já reagem);
o secret-scan (scrub do stdout truncado). Analogia: SQLite crash-VFS + Chaos Monkey + disjuntor/fusível.

---

## N-CRASH-INJECTOR — o injetor híbrido · BUILDÁVEL (test-infra, com EXP-21) · tam M

**Goal:** crashar o worker de forma DETERMINÍSTICA e reprodutível no Windows, cobrindo 4 modos, opt-in
(só EXP-21/fixture, JAMAIS produção). É test-infra measure-supporting — buildável quando o owner abrir
o EXP-21 (a medição em si é owner-gated).

**Approach (híbrido, D022):**
- **Cooperativo via env `HARNESS_CRASH_AT`** DENTRO do worker (modos a/c/d — só o cooperativo garante o
  ponto EXATO; kill externo race o flush do pipe):
  - (a) abrupta: `abrupt:call=N` → `os._exit()` na chamada N, sem flush.
  - (c) truncado: `partial:bytes=K` → escreve K bytes de stdout, aí `os._exit()` (JSON cortado no meio).
  - (d) exit sujo: `dirty:code=N` → `sys.exit(N)` não-zero + stderr.
- **Kill externo via Job Object** (o do sandbox_spawn) só p/ (b) hang: `hang:after=N` → bloqueia pra
  sempre → o Job Object do pai ceifa no timeout.
- **Gatilhos por CONTADOR, nunca probabilístico** (contraste com FAIL_MAKE_REQUEST do kernel Linux).
- **Guard mora no ENTRYPOINT do worker** (lê `HARNESS_CRASH_AT` no startup — custo ZERO sem env). O
  `processes.py` só PROPAGA a env (~3 linhas). O `sandbox_spawn.py` NÃO muda (só provê o Job Object).

**Armadilhas (w-004, obrigatórias):** exit codes NÃO-colidentes com `0xC0000005` (access violation) —
senão o pai lê crash FAKE como falha OS real; **scrub do stdout truncado** (pode ter secret parcial —
reusa o secret-scan); env escopado ao subprocess ESPECÍFICO (Windows herda env → senão TODOS os
workers crasham); truncagem DENTRO do `maxWorkerOutputChars` (senão recovery não distingue crash de
oversize-reject); o kill do modo (b) vai pelo Job Object (mata a árvore), não TerminateProcess no PID.

**Footprint (quando aberto):** módulo cooperativo `HARNESS_CRASH_AT` no entrypoint do worker + a
propagação de ~3 linhas no `processes.py` + a fixture de recovery; cenário (cada modo dispara
deterministicamente; o pai SOBREVIVE e recupera; guard off sem env).

**Aceite:** cada um dos 4 modos crasha no ponto exato reprodutível; o harness PAI sobrevive + recupera;
sem `HARNESS_CRASH_AT` o guard é no-op (zero custo em produção); exit codes não colidem com OS.

**Gate:** buildável test-infra QUANDO o owner abrir EXP-21 (só faz sentido COM a medição). O EXP-21
(a medição de recovery) segue OWNER-GATED. **Dep:** processes.py + sandbox_spawn (existem). **Tam:** M.

---

## N-CRASH-EXP21 — a medição de recovery · OWNER-GATED · tam M

**Goal:** com o injetor, medir duplicate-effect / orphaned-work / time-to-resume por modo de crash —
o EXP-21.

**Approach:** dispara cada modo do N-CRASH-INJECTOR num WF controlado e mede: houve efeito duplicado
(a tarefa rodou 2x?), trabalho órfão (worker morto deixou lixo?), time-to-resume (quanto até o
gate-hold auto-recovery retomar?). Reusa o breaker + gate-hold que já reagem.

**Footprint (quando aberto):** registra EXP-21 no registry; roda o injetor + mede via o event log +
o recovery existente. **Aceite:** a tabela `(modo de crash) → (duplicate-effect, orphaned-work,
time-to-resume)`. **Gate:** OWNER-GATED (medição). **Dep:** N-CRASH-INJECTOR. **Tam:** M.

---

## Ordem sugerida
1. **N-CRASH-INJECTOR** — a test-infra; construir quando o owner abrir o EXP-21 (não antes — sem a
   medição, o injetor é código sem consumidor).
2. **N-CRASH-EXP21** — a medição de recovery, owner-gated, logo em seguida.

> Nota: o injetor é rejeitado como probabilístico — o EXP-21 precisa DETERMINÍSTICO (o padrão do
> kernel Linux FAIL_MAKE_REQUEST é o anti-exemplo).
