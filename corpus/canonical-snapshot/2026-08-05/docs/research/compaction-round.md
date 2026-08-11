# Rodada de pesquisa — Automatic context compaction

Owner 2026-07-19: pesquisa ampla (NVIDIA + Sonnet 5 medium) pra definir o mecanismo de
compactação AUTOMÁTICA de contexto: modelos/papéis, % ideal de compactação, problemas de
não/cedo/tarde, e como achar o sweet spot por modelo × capacidade × tarefa × role.
Orquestrador = esta sessão. Divergência cross-vendor.

## O que o harness JÁ tem (plumbing, não política)
- `tools/hooks/reload_context_after_compact.py` — reinjeta o contexto canônico após um compact.
- `scripts/harness_lib/context_checkpoint.py` + `docs/CONTEXT_CHECKPOINT.md` — checkpoint de estado.
- `scripts/harness_lib/context_diet.py` — trim de tool-schema pra worker read-only (economia).
- EXP-16 (evidence loss) + A_ctx (effective vs declared context) — já MEDIMOS perda de evidência e
  contexto efetivo (construct-metrics.md, memory-context-management.md).
- **Falta: a POLÍTICA** — QUANDO auto-compactar, O QUÊ preservar, e o sweet spot por modelo/role/task.

## A pergunta
> Qual mecanismo de compactação AUTOMÁTICA de contexto o harness deve implementar — que decida
> QUANDO compactar (o % de fill ideal como GATILHO), O QUÊ preservar vs sumarizar, e como achar o
> SWEET SPOT por (a) modelo [janela declarada + capacidade EFETIVA de processar], (b) papel/role
> [overseer longevo / worker bounded / research one-shot / chat], (c) tarefa atual [fase, densidade
> de evidência] — minimizando os custos de NÃO-compactar, compactar CEDO e compactar TARDE?

## Sub-perguntas (o owner pediu explicitamente)
1. **% ideal de gatilho:** em qual fração de fill compactar? É fixo, ou função de modelo/role/task?
2. **Problemas de NÃO compactar:** overflow/truncação, degradação de qualidade ("lost in the
   middle"), custo por token subindo, cliff de qualidade.
3. **Problemas de compactar CEDO demais:** perder contexto ainda necessário, thrash (compacta e
   re-expande), custo de re-sumarização repetida, perda de evidência (EXP-16).
4. **Problemas de compactar TARDE demais:** truncação dura, cliff de qualidade, crash de overflow.
5. **Sweet spot por dimensão:** como parametrizar por modelo (janela + A_ctx efetivo), role, task.

## Critérios de sucesso (o DNA do harness)
- **Measure-before-control:** o sweet spot vem de MEDIÇÃO (a curva qualidade × fill, a perda de
  evidência), não de chute. Reusa EXP-16 (evidence loss) + A_ctx + o noise floor L13.
- **Determinístico onde der:** o gatilho é uma regra/medição reproduzível; o LLM pode sumarizar,
  mas a DECISÃO de compactar é uma função computável.
- **Parametrizável** por modelo × role × task (como o U(rota) é por termos).
- **Reusa** o checkpoint + o reload-hook + o context_diet que já existem — não um subsistema novo.
- **Anti-fabricação:** onde a capacidade efetiva de um modelo não é medida, marca como estimada.
- **Degradação de 1ª classe:** compactação que falha não pode derrubar o agente (fail-safe).

## Ondas
- Onda A (NVIDIA, wide): 5 ideadores glm-5.2, research-divergence.
- Onda B (Sonnet 5 medium): 3 ideadores — (1) empírico/medição do sweet spot; (2) desenho da
  POLÍTICA de decisão (a função quando/o-quê por modelo×role×task); (3) failure-modes + analogias
  cross-domain (OS paging/GC, checkpoint de DB, keyframe/delta de vídeo, working memory humana).

## Convergência (Fase 5)
Clusterizar mecanismos, isolar o gatilho (%/função), o modelo de preservação (o quê fica), o
método de achar o sweet spot (measure-first), e o que é buildável já (probe measure-only da curva
qualidade×fill) vs o motor ativo (owner-gated). Sintetizar num desenho + incrementos de backlog.

---

# Fase 5 — convergência (4 ondas: NVIDIA 5 + Sonnet 3)

## Convergência UNÂNIME (todas as 4 ondas, independentes)
1. **Denominar o fill pela janela EFETIVA (A_ctx), NÃO a declarada.** O reframe #1 — impede
   "chutar um % do número do vendor". A_ctx é uma SUPERFÍCIE (fill × posição, por causa do
   Lost-in-the-Middle), não um escalar; colapsar por pior-caso de posição quando precisar de 1 número.
2. **Gatilho = watermark/threshold em fillRatio, parametrizado por modelo×role×task** — não uma
   constante global. Default ~72-75% (judgment), afinado contra a curva qualidade×fill do EXP-16.
3. **Histerese / dual-zone (soft+hard, ou banda H/L)** pra impedir thrash. Universal.
4. **Measure-before-control:** o sweet spot vem de MEDIR a curva qualidade×fill (EXP-16 + noise
   floor), não de chute. **Construir um probe measure-only PRIMEIRO** — é a peça buildável.
5. **Preservação em TIERS:** keep-verbatim (canônico/plano/decision-records/pinned = raízes-GC,
   NUNCA sumarizado — enforced estruturalmente: nem entra no input do sumarizador) / summarize / drop.
6. **Re-sumarização depth-bound=1** (do checkpoint, NUNCA do resumo anterior → anti-telephone-game).
7. **Fail-safe por checkpoint** (âncora de rollback ANTES de compactar) + validação determinística
   (as chaves pinadas sobreviveram no resumo?).
8. **Snap em fronteira de subtarefa** (não dispara no meio de uma sequência de tool-call).

## Parametrização convergida
- **Por modelo:** A_ctx (efetivo). **Por role:** overseer mais cedo (~0.85-0.9× — a evidência dele
  É o deliverable), worker mais tarde/raro (~1.05× — perto do fim, deixa terminar), research
  agressivo (~0.7× — filler de baixa densidade), chat N mais largo (perda de coerência incomoda o
  usuário). **Por fase:** executing = mais tarde (não interromper transação), reporting = livre.
- **Densidade de evidência** = citações/tokens: alta-densidade exige margem de noise-floor MAIOR
  (custo assimétrico — dropar evidência load-bearing é bug de correção, não de qualidade).

## Achados ÚNICOS de alto valor
- **🔒 Compaction é SUPERFÍCIE DE EGRESSO DE SEGREDO (NVIDIA w-004).** O sumarizador LÊ contexto que
  pode ter secret/PII; se o checkpoint PERSISTE o resumo + segredos juntos, vira arquivo de alto
  risco. Secrets-tier NUNCA sumarizado/persistido; o gatilho considera densidade de sensível;
  thrash MULTIPLICA a superfície de vazamento (cada ciclo = nova passagem do LLM sobre segredos).
  **Conecta direto ao RD-TAINT (D023):** o sumarizador é um SINK — dado tainted não pode egressar
  num resumo persistido. O taint-envelope do D023 deve marcar Tier-0-secret como never-summarize.
- **💸 Custo de invalidação de cache (empírica).** Todo compact reseta o prefix do prompt-cache — o
  custo escondido DOMINANTE de compactar cedo num harness tagarela de muitos turnos curtos (maior
  que a própria chamada de sumarização). Medir cache-hit antes/depois de cada compact.
- **🔗 Cross-hop compounding (empírica).** Específico de multi-agente: um worker que compacta tarde
  entrega output degradado que vira input do overseer (que também pode estar cheio). Métrica nova:
  "evidence survival rate across N hops". Sem baseline publicado — 1ª medição = baixa confiança.

## Duas arquiteturas de referência COMPROVADAS (control loops)
- **OS paging / working-set (Sonnet failure-modes):** working set = residência garantida; page-fault
  = re-expandir algo compactado (evento binário barato); thrashing = compactar-cedo. Fix clássico:
  dimensionar pelo working set real, detectar por fault-rate (não schedule fixo).
- **TCP congestion control / CUBIC (NVIDIA w-005):** adapta a janela à capacidade OBSERVADA, não
  declarada. Mapa: **ECN (marca antes do overflow) = evidence-loss do EXP-16 como early-signal**;
  **BDP (bw×RTT) = A_ctx**; **SACK (retransmite só o gap) = re-expandir só o span necessário**;
  **RTO (reset conservador) = fail-safe**. Fit apertadíssimo — é literalmente measure-before-control.

## Portfólio / o que é buildável
- **BUILDÁVEL JÁ (measure-only) — o Context Fill Probe (CFP):** loga por turno fill%(declared+A_ctx),
  canary-recall, latência, custo, cache-hit, eventos de compact + outcome; produz a tabela
  `(modelo,role,task,fill%)→(qualidade, verdict: safe/degraded)` com noise-floor gating. **NUNCA
  compacta.** É o instrumento measure-first (como o truth-divergence probe / GM-5). → **EXP-23**.
- **OWNER-GATED (o controle ativo):** o Compact Controller (gatilho A_ctx×role×task + histerese +
  snap-em-fronteira), a preservação em tiers + o sumarizador, o fail-safe por checkpoint. É CONTROLE
  → precisa das medições do CFP justificando o threshold (igual C9 / N-TRUTHRECON-CORE). + o
  secret-tier isolation (segurança → security review, casa com RD-TAINT).

## Rastreabilidade
| Evidência | Ideia | Experimento | Task | Status |
|---|---|---|---|---|
| 4/4 (A_ctx + watermark+histerese) + TCP/paging | CFP + Compact Controller | CFP = EXP-23 | N-COMPACTION | desenhado; CFP buildável, controle owner-gated |
| NVIDIA w-004 (secret egress) | secret-tier never-summarize | — | dobra RD-TAINT/D023 | desenhado |
| empírica (cache-invalidation, cross-hop) | custos escondidos + métrica multi-hop | entra no CFP | — | measure |
