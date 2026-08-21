# Planos de implementação — RD-TAINT (taint / CaMeL, o secret nunca egressa)

Planos parqueados no backlog (owner 2026-07-19: "faz os planos bem detalhados, prioriza o RD-TAINT
por causa das dependências"). Derivados de `rd-taint-camel-round.md` (5 ideadores NVIDIA) + D023.
**Prioridade:** o **N-PTC-TAINT4** (o 4º sink do PTC) ESTENDE o envelope daqui — sem isto, o PTC
engine reabre o gap de egresso de segredo.

**Máquinas existentes a reusar (NÃO reinventar):**
- `scripts/harness_lib/secret_scan.py` — o secret-scan que já detecta SHAPE de segredo na fronteira
  do worker e RETÉM o resultado. É **meio-taint** (detecção no sink) — o seam que os sinks estendem.
- `scripts/harness_lib/records.py` — o **subject dimension** (`subject=` em records/append_event):
  proveniência self vs target, já atribuível.
- `.harness/routing/executors.json` — os **trust tiers** (first-party/third-party) = capabilities CaMeL.
- GM-3 provenance firewall (`memory-context-management.md`: `authority >= signed_policy`) = o gate
  control-plane que o CaMeL reusa.
- `append_event` (hash-chain) — pra o envelope não-forjável entrar como evento assinado (gancho).

**Teto honesto (declarado pelos 5 ideadores, repetir em todo plano):** taint EXPLÍCITO marca a
FONTE, não o conteúdo derivado. Se o LLM PARAFRASEIA o segredo, o taint não segue. **Defense-in-depth,
não prova.** O secret-scan por shape pega padrão, não laundering semântico.

---

## N-TAINT-PROBE — "would-block" probe · BUILDÁVEL JÁ (measure-only) · tam M

**Goal:** medir QUANTOS valores tainted (secret-read/web-fetch/worker-output) ALCANÇARIAM um sink de
egresso hoje — antes de qualquer enforcement. Measure-before-control: se quase nada egressaria, o
enforcement fica measure-only (destino do C9); se muito, justifica o envelope.

**Reuso:** `secret_scan.py` (já detecta shape no sink); `records`/`append_event` (a proveniência).

**Approach:**
1. **Probe** (`testing/probes/taint_reach_probe.py`, sibling do truth-divergence): sobre um corpus de
   WORKER_RESULTs reais + prompts de vendor + logs, marca (source-stamp shadow) o que É tainted por
   origem (secret-read = casou o secret-scan; web-fetch = veio de discovery; worker-output = do
   subprocess) e conta quantos CHEGARIAM a cada sink (prompt/persistido/log) SEM bloqueio hoje.
2. **Determinístico, zero-LLM:** reusa o secret-scan como o classificador de "é tainted"; o "chegaria
   a um sink" é set-membership (o valor aparece no texto que iria pro sink). Log = contagem + hashes/
   samples (NUNCA o valor cru — o probe não pode ele mesmo vazar).
3. **Redução:** por tipo de fonte × sink, a fração que egressaria; noise floor L13; verdict.

**Footprint:** `testing/probes/taint_reach_probe.py` (novo, self-check). NÃO adiciona enforcement.

**Aceite:** o probe roda sobre ≥20 WORKER_RESULTs/prompts reais, produz a tabela `(fonte × sink) →
fração-que-egressaria` com noise-floor gating, ZERO valor cru logado, ZERO enforcement.

**Gate:** measure-only, alçada measure-first. **Dep:** secret_scan (existe). **Tam:** M.

---

## N-TAINT-ENVELOPE — o envelope não-forjável · OWNER-GATED (security) · tam L

**Goal:** o núcleo — um metadado de taint NÃO-FORJÁVEL injetado pelo HARNESS (nunca pelo worker),
marcado na fonte, que viaja com o dado. É o único jeito num modelo de subprocess+JSON (o worker
escreve JSON arbitrário → marcador inline seria forjável).

**Reuso:** `records` subject dimension (a proveniência já existe); `append_event`/hash-chain (o
envelope assinado); o secret-scan (o detector de fonte secret-read).

**Approach:**
1. **Source-stamp** em 3 origens: `secret_read` (casou o secret-scan ao ler), `web_fetch` (veio da
   discovery/WebFetch), `worker_output` (produzido por subprocess não-confiável). O HARNESS carimba —
   fora do WORKER_RESULT que o worker controla (embrulha/assina, não um campo inline).
2. **Transporte:** o taint viaja num envelope harness-wrapped ao redor do valor (chave fora do
   controle do worker). Opcional: entra no hash-chain (evento crítico) pra ser à prova de reescrita.
3. **taint_map:** o harness mantém o mapa valor→{sources, at, subject} — o que os sinks consultam.

**Footprint (quando aberto):** `harness_lib/taint.py` (o envelope + o source-stamp + o taint_map);
pontos de source-stamp (o seam do secret-scan na leitura; a discovery no web-fetch; o subprocess no
worker-output). Spec door NEW (SPEC-116) + cenário (worker não consegue forjar; o stamp sobrevive ao JSON).

**Aceite:** um valor secret-read carrega o envelope de taint que o worker NÃO consegue remover/forjar;
o taint_map resolve fonte+proveniência. **Gate:** OWNER-GATED + security review. **Dep:** N-TAINT-PROBE
(justifica). **Tam:** L.

---

## N-TAINT-SINKS — enforcement fail-closed nos sinks · OWNER-GATED (security) · tam M

**Goal:** barrar o egresso — dado tainted chegando num sink BLOQUEIA/redige por padrão. **Estende o
secret-scan** (que já é meio-taint) pra checar o `taint_map`, não só a shape.

**Reuso:** `secret_scan.py` (o seam — hoje detecta shape; passa a checar taint_map também).

**Approach:**
1. **Os sinks (D023):** (1) prompt pro vendor, (2) WORKER_RESULT persistido, (3) log. **+ o 4º sink do
   PTC (N-PTC-TAINT4): o stdout/stderr do sandbox** — o mesmo checker, mais um call-site (é por isso
   que este item precede o PTC engine).
2. **Fail-closed:** tainted no sink → bloqueia/redige (break-glass auditado pra egresso deliberado,
   paralelo ao sandbox_prepare SPEC-151).
3. **Robustez (w-002/w-003):** check O(campos-tainted-alcançáveis) (não O(todos)); break-glass rate-
   limited/batched (senão floda o append_event); rollback de escrita parcial (sem egresso meio-
   redigido); **o próprio checker fail-closed** (se o taint-check crashar, NÃO egressa não-redigido).

**Footprint (quando aberto):** estende `secret_scan.py` (checar taint_map) + os 3 (→4) call-sites de
sink; cenário de segurança (tainted em cada sink → bloqueado; checker-crash → fail-closed).

**Aceite:** um valor tainted NUNCA egressa nos 3 (→4) sinks sem break-glass; o checker que crasha
falha fechado. **Gate:** OWNER-GATED + security review. **Dep:** N-TAINT-ENVELOPE. **Tam:** M.
**⚠️ Dependência-chave:** o **N-PTC-TAINT4** = o 4º sink daqui; construir este ANTES do PTC engine.

---

## N-TAINT-CAMEL — control-plane capabilities · OWNER-GATED · tam M

**Goal:** o valor do CaMeL SEM o runtime pesado — mapear só o split control-plane (política/capability)
vs data-plane (valores), reusando o que já é capability-like.

**Reuso:** trust-tiers (executors.json: first-party/third-party); GM-3 authority (`authority >=
signed_policy`) — ambos já são restrições capability-like.

**Approach:** o control-plane = quais fontes/tiers podem produzir dado que egressa (a política);
o data-plane = os valores (o taint_map). NÃO um IFC runtime por-valor — a decisão é a authority do
GM-3 + o trust-tier do executor. Ex.: dado de um worker third-party (trust-tier baixo) + secret-read
= egresso negado por política, não por análise de fluxo.

**Footprint (quando aberto):** liga o taint_map à authority do GM-3 + trust-tiers no ponto de decisão
do sink; cenário (política control-plane nega egresso de tier baixo + secret). **Aceite:** a decisão
de egresso é a authority/tier (control-plane), não um runtime de fluxo. **Gate:** OWNER-GATED.
**Dep:** N-TAINT-SINKS + GM-3. **Tam:** M.

---

## Ordem sugerida (e a dependência do PTC)
1. **N-TAINT-PROBE** — buildável; mede se o egresso é real antes de construir controle.
2. **N-TAINT-ENVELOPE** — o núcleo não-forjável.
3. **N-TAINT-SINKS** — o enforcement; **inclui o gancho do 4º sink que o N-PTC-TAINT4 usa** → ESTE é
   o pré-requisito de segurança do PTC engine (N-PTC-ENGINE não sobe sem os sinks + o 4º).
4. **N-TAINT-CAMEL** — a política control-plane por cima.

> Cadeia de dependência cross-rodada: **N-TAINT-ENVELOPE + N-TAINT-SINKS → N-PTC-TAINT4 → N-PTC-ENGINE.**
> É por isso que o RD-TAINT foi priorizado.
