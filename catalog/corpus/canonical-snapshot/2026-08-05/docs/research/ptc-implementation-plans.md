# Planos de implementação — Programmatic Tool Calling (N-PTC-*)

Planos parqueados no backlog (owner 2026-07-19: "refinar os resultados da pesquisa com planos bem
detalhados"). Derivados de `ptc-round.md` (4 ondas) + D030. Cada plano é implementer-ready.

**Máquinas existentes a reusar (NÃO reinventar):**
- `scripts/harness_lib/sandbox_spawn.py` — SPEC-151 (fs-confine + Job Object + risk-tier). O
  SUBSTRATO de execução do código emitido. `evaluate_chokepoint` já faz `ast.walk` (o idiom do gate).
- `scripts/harness_lib/discovery.py` — a cadeia discover (bulk reads) = o alvo do probe.
- `scripts/harness_lib/cost_metrics.py` + `route_ledger.py` — o ledger (observed vs estimated;
  `_extract_harness_result` = o idiom de extração determinística de bloco).
- `scripts/harness_lib/agent_parity.py` — `conformance_report`, `supportState`, `accountingSemantics`
  (T-ADAPTERCONF/C16b) — onde a capability PTC declara/verifica.
- `.harness/capabilities.json` (`mcpServers` hoje `{}`) — as tools/MCP expostas.
- O envelope de taint (RD-TAINT / D023) — o modelo de secret-nunca-egressa que o 4º sink estende.
- `tools/openai_worker.py` — o worker HTTP dos open-weights (onde o loop emulado se pluga).

---

## N-PTC-PROBE (EXP-24) — probe measure-only · BUILDÁVEL JÁ · tam M

**Goal:** medir latência/token/CPU de PTC-emulado vs tradicional numa tarefa REAL, no NOSSO tráfego,
sem mudar produção. É o que justifica (ou mata) o engine — PTC é aposta de workload-shape (τ²-bench:
+8% em sequencial; números de vendor não-replicados).

**Reuso:** a cadeia discover (`discovery.discover_paths`) como alvo (o caso-mãe); `cost_metrics.
record_workflow` pra logar (com `costBasis: observed|estimated`); o sandbox pra o leg PTC-emulado.

**Approach:**
1. **Probe** (`testing/probes/ptc_probe.py`, sibling do truth-divergence/CFP): pega UM conjunto de
   inputs discover reais e roda 2 legs na MESMA entrada — (a) TRADICIONAL: o loop per-file atual
   (N reads = N passos); (b) PTC-EMULADO: um script único que itera os reads no sandbox e retorna só
   o agregado filtrado. Loga por leg: round-trips, tokens billed (observed do endpoint; estimated
   marcado), latência wall-clock, **CPU-time do sandbox** (o eixo de custo novo do PTC), por fan-out N.
2. **Matched-budget:** mesma entrada, mesmo modelo, mesmo teto — senão o delta confunde "melhor" com
   "gastou mais" (a carta matched-budget-controls do EXP_METHODS).
3. **Redução:** por task-shape (fan-out N), agrega o delta; noise floor = stdev de reps; verdict só
   se o delta > noise floor L13 por ≥2 buckets. Break-even N (hipótese N>3-4 a falsificar).
4. **Só trafego confiável:** só compara legs cujo `accountingSemantics` é native/emulated (não
   unknown) — a regra C16b vale pro delta do probe também.

**Footprint:** `testing/probes/ptc_probe.py` (novo, self-check); talvez um campo `cpuMs` no record
do ledger. NÃO toca o caminho de produção do discover (o leg PTC roda isolado no probe).

**Aceite:** o probe roda a cadeia discover 2x (trad vs PTC) em ≥2 fan-out shapes, produz a tabela
`(shape N) → (Δround-trip, Δtoken, Δlatência, ΔCPU)` com noise-floor gating, ZERO mudança de produção.
Registra o 1º data point no EXP-24. **Abandon:** se o ganho fica no noise floor (ou o CPU come o
ganho de token) → PTC fica measure-only, não vale o engine.

**Gate:** measure-only, alçada measure-first (como o truth-divergence probe). Buildável.
**Dep:** discover chain (existe). **Tam:** M.

---

## N-PTC-ENGINE — o motor PTC (loop no nosso sandbox) · OWNER-GATED · tam L

**Goal:** o motor que dá PTC a TODO executor roteando o loop de orquestração pelo NOSSO sandbox
(nativo = opt-in). Controle + segurança → só depois do EXP-24 justificar + security review.

**Reuso:** `sandbox_spawn` (o substrato); o idiom `ast.walk` do `evaluate_chokepoint` (o gate);
`_extract_harness_result` (a extração de bloco); `openai_worker.py` (o pluga dos open-weights).

**Approach (o loop emulado, preciso):**
1. **`harness_tools` (o stub module):** por sessão PTC, gerar UM módulo de funções `async def
   harness_<verb>(args: dict) -> str` (assinatura Anthropic: dict-in, string-out, await-able) — UMA
   por tool JÁ declarada e narrowed do worker (c5: o stub-set ⊆ tools do worker). Injetado no
   namespace do sandbox.
2. **Prompt-contract:** o system prompt declara as assinaturas + instrui o modelo a emitir UM bloco
   ```python com o script de orquestração, terminando num `print()` do resultado FILTRADO só.
3. **Code-extraction determinística:** parse do bloco (reusa o idiom `_extract_harness_result`). Sem
   bloco → sem PTC → fallback pro tool-call tradicional (fail-closed ao caminho barato já verificado).
4. **Gate AST estático ANTES de executar:** `ast.parse` + `ast.walk` — rejeita qualquer Call/Import
   que não seja (a) um stub injetado, ou (b) uma allowlist stdlib mínima (`json,re,itertools,
   statistics,asyncio`). Reusa a técnica de self-check do `evaluate_chokepoint`.
5. **Execução:** o código vetado roda via `sandbox_spawn(mode=bounded)` com o namespace injetado —
   mesmo Job Object / fs-confine / risk-tier de qualquer worker (R0 default; R1+ só se o stub-set tem
   tool write-capable). Builtins perigosos AUSENTES do namespace (backstop do gate).
6. **Pause/resume relay (o corpo da tool roda no NOSSO lado):** quando o código chama um stub, o
   sandbox pausa, o harness roda o verbo REAL, devolve o resultado string, o código resume. (Igual o
   protocolo Anthropic — o vendor nativo faz o mesmo; nós fazemos p/ todos.)
7. **Return filtrado:** só o `stdout`/return final cruza pro contexto do modelo (envelope vendor-
   agnóstico — mesma shape do `code_execution_result.stdout`).
8. **Fail-safe (NVIDIA w-003):** checkpoint/resume p/ partial-batch (falha do script não perde o batch
   todo); timeout de liveness (script travado); o CPU-time entra no ledger.

**Footprint (quando aberto):** `harness_lib/ptc.py` (o stub-gen + o loop + o gate + o relay); pluga no
`openai_worker.py` (emulado) + no adapter claude (opt-in nativo); spec door NEW (SPEC-116) + cenário
(gate AST rejeita código malicioso; stub-set ⊆ tools; return filtrado; fallback sem bloco).

**Aceite:** um open-weight emite código que orquestra N discover reads no sandbox, o gate AST rejeita
`open()/socket/subprocess`, só o agregado volta, o CPU entra no ledger, e sem-bloco cai no tradicional.

**Gate:** OWNER-GATED (controle + segurança). Pré-req: EXP-24 + N-PTC-TAINT4 + security review.
**Dep:** N-PTC-PROBE, N-PTC-TAINT4. **Tam:** L.

---

## N-PTC-TAINT4 — o 4º sink de taint · OWNER-GATED (security) · tam M

**Goal:** fechar o buraco que PTC abre: o D023 lista 3 sinks (prompt/result-persistido/log); o
stdout/stderr do sandbox é um QUARTO (volta pro modelo por design). Um secret `print()`-ado atravessa
sem tocar os 3.

**Reuso:** o envelope de taint / o check de sink do RD-TAINT (D023) — mesmo mecanismo, novo call-site.

**Approach:**
1. **4º sink:** o taint-sink check roda no `stdout`/`stderr` CAPTURADO do sandbox ANTES de devolver
   como resultado do código. Dado tainted (secret-read) no stdout → fail-closed (bloqueia/redige).
2. **Lethal-trifecta invariant:** um namespace de stub não combina stub-que-lê-secret + stub-com-
   egresso sem `declares_egress=True` E o 4º-sink ativo (PTC remove o checkpoint natural per-call).
3. **Sem escape:** stubs `dict → str` só (nunca `run_shell(str)` — fecha command-injection por
   construção); `HARNESS_SANDBOX_OVERRIDE` inalcançável de dentro do código (env do processo OUTER,
   strip pelo envKeepList).

**Footprint (quando aberto):** integra no N-PTC-ENGINE (o relay chama o taint-check no stdout) + no
envelope do RD-TAINT; cenário de segurança (secret no stdout → bloqueado; namespace secret+egresso
sem declares_egress → recusado). Security review isolado.

**Aceite:** um script que `print()` um secret marcado NUNCA entrega o secret ao modelo (fail-closed);
namespace secret+egresso sem declares_egress é recusado. **Gate:** OWNER-GATED + security review.
**Dep:** RD-TAINT/D023 + N-PTC-ENGINE. **Tam:** M.

---

## N-PTC-CONFORMANCE — capability + accounting · OWNER-GATED · tam M

**Goal:** declarar/verificar PTC por executor com a disciplina do T-ADAPTERCONF (nativo vs emulado;
accounting honesto).

**Reuso:** `agent_parity.py` (`supportState`, `conformance_report`, `accountingSemantics`).

**Approach:**
1. **Capability `programmatic-tool-calling`** com `supportState` (claude=native, openai/codex=native-
   se-o-CLI-adotar [verificar], resto=emulated). Declara CAPACIDADE, não a escolha de rota.
2. **c9 `ptcTokenScope`** (novo sub-campo, report-only): `vendor-discounted|full-emulated|unknown`.
   A Anthropic DESCONTA os tokens de tool-result nativos → comparação naive native-vs-emulated
   favorece o claude por motivo que não é design nosso. Default unknown, nunca gateia.
3. **c5 no-amplification:** um cenário prova que o stub-set gerado é subconjunto das tools declaradas
   do worker (um worker que emite código não ganha alcance que não teria 1-call-por-vez).

**Footprint (quando aberto):** campo em `capabilities.json`/`agent_parity.py`; cenário de conformance
(c5 subset + c9 scope). **Aceite:** o conformance report mostra supportState+ptcTokenScope por
executor; c5 falha se o stub-set excede as tools declaradas. **Gate:** OWNER-GATED. **Dep:** N-PTC-ENGINE. **Tam:** M.

---

## N-TOOLSEARCH — tool-search / RAG-sobre-tools (fronteira) · BUILDÁVEL (mede token) · tam M

**Goal:** quando há muitas tools/MCP, carregar só os schemas relevantes por turno (não empilhar todos
no contexto — custo grande de token). Stacka com PTC mas é testável SEM o engine.

**Reuso:** `capabilities_view.py` (mescla MCP de 5 surfaces — a superfície candidata); o cost ledger.

**Approach:** um retrieval (bm25/regex ou embedding) sobre o catálogo de tools; carrega só o subset
relevante à demanda; **APPEND-not-swap** (adiciona, não troca — preserva o prefix-cache, como o
Anthropic Tool Search Tool faz). Measure-only primeiro: quanto token economiza vs empilhar tudo.

**Footprint:** `harness_lib/tool_search.py` + um probe measure-only (token com-vs-sem search).
**Aceite:** com N tools declaradas, o search carrega só os relevantes e mede a economia de token
(noise-floor gated). **Gate:** buildável (measure-only). **Dep:** —. **Tam:** M. Ref: Gorilla
(arXiv:2305.15334), Anthropic Tool Search Tool.

---

## Ordem sugerida
1. **N-PTC-PROBE (EXP-24)** + **N-TOOLSEARCH** — buildáveis, medem o ganho antes de tudo.
2. **N-PTC-TAINT4** — o controle de segurança tem que existir ANTES do engine (o 4º sink não é opcional).
3. **N-PTC-ENGINE** — só quando o probe mostrar ganho acima do noise floor + o taint4 pronto + security review.
4. **N-PTC-CONFORMANCE** — junto/depois do engine.

> Nota: o mesmo tratamento (plano implementer-ready) já foi feito pra N-COMPACTION; pode se estender
> aos outros itens de pesquisa (N-TRUTHRECON-*, RD-U→U, RD-CRASH→injetor, RD-TAINT→taint) — é só pedir.
