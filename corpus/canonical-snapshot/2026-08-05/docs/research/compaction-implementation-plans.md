# Planos de implementação — Automatic context compaction (N-COMPACTION-*)

Planos parqueados no backlog (owner 2026-07-19: "criar planos pra cada um e deixar em backlog").
Derivados de `compaction-round.md` (4 ondas) + D029. Cada plano é implementer-ready: reuso das
máquinas que já existem, approach, footprint, aceite, gate (measure-vs-control), dep, tamanho.

**Máquinas existentes a reusar (NÃO reinventar):**
- `tools/hooks/reload_context_after_compact.py` — reinjeta contexto canônico pós-compact.
- `scripts/harness_lib/context_checkpoint.py` + `docs/CONTEXT_CHECKPOINT.md` — checkpoint de estado.
- `scripts/harness_lib/context_diet.py` — classifica pinned/read-only/schema-trim (é o sorter de tiers).
- EXP-16 (evidence-loss) + A_ctx (contexto efetivo vs declarado) — a medição-base.
- `append_event` (hash-chain) + o experiment registry — pra logar eventos measure-only.
- `records`/delegation ledger — custo/latência/cache-hit por chamada.

---

## N-COMPACTION-CFP (EXP-23) — Context Fill Probe · BUILDÁVEL JÁ (measure-only) · tam M

**Goal:** medir a curva qualidade×fill sem NUNCA compactar, produzindo a tabela
`(modelo, role, task, fill%) → (qualidade, stdev, N, verdict: safe|degraded)` com noise-floor
gating. É o instrumento que justifica (ou não) o controller — measure-before-control (D008).

**Reuso:** EXP-16 (evidence-loss = o eixo-y natural); A_ctx (o denominador efetivo); `append_event`
(logar cada evento); o experiment registry (EXP-23 já registrado, método = confidence-sequences);
o delegation ledger (custo/latência/cache-hit por chamada).

**Approach:**
1. **Probe passivo por turno** (`testing/probes/context_fill_probe.py`, sibling do truth-divergence/
   GM-5): loga por turno/tool-call — `model, role, task_id, task_type, task_phase, fill%(declared),
   fill%(A_ctx se o bucket for conhecido), latency, tokenCost, cacheHit/miss, compactionEvent(se
   disparou, em que fill%), evidenceDensity(=pinned/total via context_diet)`. Determinístico, stdlib,
   escreve UM JSON timestamped sob `.harness/runs/`. NUNCA compacta.
2. **Canary-recall barato**: a cada M turnos, injeta um fato conhecido e checa se o agente ainda o
   recupera K turnos depois (ou se o próximo tool-call usa corretamente estado que deveria estar em
   vista). É o sinal de qualidade barato (o RULER-like caro fica pro synthetic grid).
3. **Redução por bucket**: por `(model, role, task_type)`, agrega `quality(fill%)` da produção;
   noise floor = stdev de reps no MESMO fill% baixo; cliff = 1º fill% cuja queda > noise floor L13
   por ≥2 buckets consecutivos + replicado. Emite a tabela + verdict.
4. **A_ctx como SUPERFÍCIE** (fill × posição, por causa do lost-in-the-middle): reportar por
   posição-bucket, colapsar por pior-caso quando precisar de 1 número (o harness não controla onde o
   conteúdo reinjetado cai). Estender o EXP-16 pra variar posição × fill se ainda não varia.

**Footprint:** `testing/probes/context_fill_probe.py` (novo, com self-check); um hook leve de log
por-turno no driver (ou o `append_event` num ponto que já existe); talvez um campo no delegation
ledger pra cacheHit. NÃO toca o caminho de produção de compactação (não existe ainda).

**Aceite:** o probe roda ≥20 turnos/tarefas reais + o synthetic grid, produz a tabela por bucket com
noise-floor gating, ZERO compactação disparada. Self-check (assert curva monotônica-ish, empty→zeros).
Registra o 1º data point no EXP-23.

**Gate:** measure-only, dentro da alçada measure-first (como o truth-divergence probe). Buildável
sem owner-gate. **Abandon (EXP-23):** se a qualidade não cai acima do noise floor até perto do
overflow (A_ctx ≈ declared) → o modelo usa a janela toda; o controller vira trivial (só hard-ceiling).

**Dep:** EXP-16 (existe). **Teto honesto:** o LLM-judge da qualidade degrada em transcript longo
(measurement-of-measurement); canary injetado perturba o que mede (sampling rate é tradeoff real).

---

## N-COMPACTION-CTRL — Compact Controller ativo · OWNER-GATED (controle) · tam L

**Goal:** o motor que DECIDE quando/o-quê compactar, parametrizado por modelo×role×task, com
histerese, preservação em tiers, re-sumarização depth-bound e fail-safe. É CONTROLE → só depois do
CFP (EXP-23) medir o threshold que o justifica (mesmo padrão do C9 / N-TRUTHRECON-CORE).

**Reuso:** a tabela do CFP (o threshold vem dela, não de constante); `context_diet` (o sorter de
tiers keep/summarize/drop); `context_checkpoint` (a âncora de rollback); o reload-hook (belt-and-
suspenders, NÃO load-bearing — o Tier-0 é excluído no assembly do prompt, não "recuperado depois").

**Approach:**
1. **Gatilho** = função pura pré-turno no driver (o LLM NUNCA decide compactar; só sumariza depois):
   `shouldCompact(fillPct/A_ctx, model, role, phase, evidenceDensity, state)` → hard-ceiling (0.92)
   OR (fill ≥ θ(role,phase,model) E fora do cooldown de histerese E numa fronteira de subtarefa).
   θ vem da tabela do CFP; defaults judgment (overseer 0.85×, worker 1.05×, research 0.7×).
2. **Preservação em tiers** (o `context_diet` classifica): Tier-0 verbatim never-summarize (canônico
   `.harness`, goal, plano/seam, últimos N turnos por role, pinned) — ESTRUTURALMENTE fora do input
   do sumarizador; Tier-1 summarize incremental (resumo + delta, NUNCA re-sumariza do zero); Tier-2
   drop (falsificado já capturado, tool-read duplicado, o que já está no checkpoint).
3. **Re-sumarização depth-bound=1**: sempre do último checkpoint + delta cru, nunca do resumo
   anterior (anti-telephone-game).
4. **Sumarizador desacoplado do modelo da task**, gated por evidence-loss medido por content-class
   (um modelo barato sumariza SE a perda medida < teto; senão o canônico; senão Tier-0-only).
5. **Fail-safe**: checkpoint ANTES de sumarizar; validação DETERMINÍSTICA pós-compact (as chaves/
   paths pinados do Tier-0/1 ainda aparecem no resumo? senão fail-closed → rollback → escala 1 rung →
   estrutura de escalação, nunca loop nem truncação silenciosa). Re-expandir o span específico do
   checkpoint quando algo compactado se mostrar necessário (compactação reversível no pequeno).

**Footprint (quando aberto):** `harness_lib/compaction.py` (o controller + a função pura de gatilho
+ os tiers); ponto de chamada pré-turno no driver (onde já há o token-budget check); reuso de
checkpoint/diet/reload-hook; spec door NEW (SPEC-116) + cenário (gatilho dispara na fronteira certa;
Tier-0 nunca entra no sumarizador; fail-safe recupera).

**Aceite:** o controller compacta na fronteira certa quando o CFP diz que vale, preserva o Tier-0
verbatim, valida deterministicamente, e sobrevive a uma compactação falha (rollback). Medição de
regressão: qualidade pós-compact não cai abaixo do baseline (o CFP mede).

**Gate:** OWNER-GATED. Pré-req: EXP-23 mediu o threshold. Analogias-guia: TCP (ECN/BDP/SACK/RTO) +
paging (working-set/fault-rate).

**Dep:** N-COMPACTION-CFP (EXP-23). **Tam:** L.

---

## N-COMPACTION-SECRET — secret-tier isolation · OWNER-GATED (security) · tam M

**Goal:** garantir que a compactação NÃO vira superfície de egresso de segredo (achado NVIDIA w-004).
O sumarizador lê contexto que pode ter secret/PII; o checkpoint não pode persistir resumo+segredo
juntos. Dobra o RD-TAINT (D023).

**Reuso:** o secret-scan que já existe (detecta shape na fronteira); o taint-envelope do RD-TAINT/
D023 (marca proveniência); o `context_checkpoint`.

**Approach:**
1. **Secret-tier = never-summarize/never-persist**: dado marcado secret-read (o taint-envelope do
   D023) é Tier-0-secret — NUNCA entra no input do sumarizador NEM no resumo persistido do checkpoint.
   O sumarizador é um SINK do modelo de taint (D023): dado tainted não egressa num resumo.
2. **Gatilho considera densidade de sensível**: um worker research que acumula secret deve compactar
   ANTES/diferente (não deixar segredo marinar no contexto que vai ser sumarizado).
3. **Isolamento por camada no checkpoint**: se o checkpoint persiste resumo, o resumo é scrubbed
   (reusa o secret-scan) — nunca um arquivo com resumo + segredo cru.
4. **Anti-thrash é anti-vazamento**: cada ciclo de compactação é uma nova passagem do LLM sobre o
   contexto — a histerese do CTRL reduz a superfície de exposição também.

**Footprint (quando aberto):** integra no N-COMPACTION-CTRL (o sorter de tier marca secret-tier) +
no taint-envelope do RD-TAINT; um cenário de segurança (secret marcado nunca aparece no input do
sumarizador nem no checkpoint persistido). Security review isolado (caminho de segurança).

**Aceite:** um segredo marcado no contexto NUNCA aparece (a) no input do sumarizador, (b) no resumo
persistido; um teste de fronteira prova. Fail-closed.

**Gate:** OWNER-GATED + security review. **Dep:** N-COMPACTION-CTRL + RD-TAINT/D023. **Tam:** M.

---

## Ordem sugerida
1. **N-COMPACTION-CFP (EXP-23)** — buildável já; mede o threshold. Sem ele, o resto é chute.
2. **N-COMPACTION-CTRL** — só quando o CFP mostrar que há um cliff que vale controlar (senão trivial).
3. **N-COMPACTION-SECRET** — junto/depois do CTRL, atrás do RD-TAINT, com security review.

> Nota: o mesmo tratamento (plano implementer-ready parqueado) pode se estender aos outros itens de
> pesquisa (N-TRUTHRECON-*, RD-U→U, RD-CRASH→injetor, RD-TAINT→taint) — é só pedir.
