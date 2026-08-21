# Rodada — dedup semântico de findings no reduce (pós-EXP-15)

Estudo "investigar opções" (playbook `.harness/prompts/research-playbook.md`).
Gatilho: owner 2026-07-18 — "investigue soluções pra isso no artigo e nas fontes
dele; se não houver, faz research com nvidia". Artigo verificado ANTES da rodada:
a destilação integral (`harness-reference-architecture-adoption.md`) contém só o
DIAGNÓSTICO (C5 sampling §4.4; contribuição marginal §5.5a) — nenhuma técnica de
fusão semântica. Condição "não houver" satisfeita → wave NVIDIA (diretriz owner:
research com modelo barato).

## Fase 0 — Pergunta, critérios, orçamento

- **Pergunta:** como DETECTAR (e opcionalmente fundir) findings semanticamente
  equivalentes — paráfrases da mesma ideia — produzidos por workers paralelos,
  dentro do reduce single-pass do harness?
- **Evidência-mãe (measurement, forte):** [repo] EXP-15 + probe de candidatos
  (`.harness/runs/exp15-dedup-candidates-*.json`, commit c6d92b4): chave string
  não recupera convergência — normalização de prefixos fundiu 0/83; a
  convergência real é parafrástica ("Mock-vs-real matrix" ⇔ "flight simulator
  vs wind tunnel"); dedup por categoria+evidência fundiu 1/83.
- **Critérios de sucesso:** (a) roda no reduce (single-pass, ≤50 findings/wave,
  Windows, stdlib-first — dependência nova só com caso forte); (b) custo por
  reduce ≪ custo de 1 worker; (c) determinístico preferido, ou pelo menos
  auditável (pares candidatos visíveis, nunca fusão silenciosa); (d) controle
  explícito de over-merge (falso-merge é pior que duplicata: perde finding);
  (e) shadow-mode primeiro (medir antes de mudar o reduce — disciplina D008).
- **Orçamento declarado:** 1 wave research-divergence em `nvidia-compat`
  (~5 posts HTTP, packets trimados, ~15-25k tokens NVIDIA) + reduce + síntese
  do orquestrador inline. Wave de crítica: NÃO gasta — pergunta estreita, a
  crítica é do orquestrador contra a evidência medida (registrado; re-abre se
  a divergência trouxer candidato que exija validação externa).

## Fase 1 — Discover (interno feito; externo via wave + verificação pós-wave)

[repo] EXP-15/probe: acima. [repo] restrições do reduce:
`workflow_reduce.normalize_finding_key` (title+category+evidence), findings
`additionalProperties: true` (cartões podem carregar campos extras).
[judgment] técnicas candidatas nomeadas na largada (a wave gera livre, isto não
é seed): embeddings+clustering, MinHash/SimHash, cross-encoder, LLM-judge
pairwise barato, canonicalização estruturada, two-stage blocking.
Workers HTTP não navegam: referências citadas pela wave são memória de modelo —
tratadas como `preliminar` até verificação do orquestrador; inverificável vira
`referência: judgment` (anti-fabricação).

## Fase 2 — Define (gate humano: a diretriz do owner É a aprovação da rodada)

Brief único (problema, não tecnologia): "No reduce de um fork-join, 5 workers
reportam em ~40% dos casos A MESMA ideia com títulos/frases diferentes. O
harness precisa saber QUANDO dois findings são a mesma ideia, com custo mínimo,
zero dependência pesada, e sem fundir ideias genuinamente distintas. Como?"
Atores: reducer determinístico; orquestrador (pode gastar 1 chamada de modelo
barato); owner (aprova mudança de comportamento). Restrições: critérios (a)-(e).

## Fase 3 — Develop

- Wave 1 (research-divergence, nvidia-compat): `WF-20260718-162602-104095`.
- **Diagnóstico revisado p/ --force-round (exigência do maxRounds):** rodada 1
  teve 1/5 sucesso; os 4 restantes falharam TODOS com `transport error: The
  read operation timed out` (stderr de worker-002..005) = o timeout de leitura
  hardcoded de 120s no `openai_worker._post` estrangulou gerações lentas do
  endpoint NVIDIA — não é flake de conteúdo nem breaker (zero
  executor-circuit-*.json). Fix aplicado antes do retry: literal 300s
  (tools/openai_worker.py, comentário aponta este WF). Rounds foram consumidos
  por erros de VERBO do orquestrador ("round"/"retry sem worker" — o CLI real é
  `retry <wf> <worker>` + run only-missing), não por falhas de modelo.

- Resultado wave 1: 5/5 workers (após retry com timeout 300s), reduce `partial`
  (4 válidos + 1 schema-inválido), 24 findings deduplicados.
- **Manuscrito minerado em paralelo (6 chunks × Sonnet; fonte agora versionada em
  `docs/research/sources/adaptive-project-oriented-multi-agent-harness-architectures.md`,
  sha256 5EEACC88...D69465C7064):** o artigo NÃO prescreve técnica de dedup —
  prescreve a GOVERNANÇA: [repo/manuscrito ~l.2313, prop. 22] "A semantic repair
  agent may propose a merge, but only a deterministic validator and authorized
  owner may commit it" (forte); [~l.861] proveniência correlacionada é MARCADA,
  consenso aparente nunca é fusão silenciosa (forte); [~l.1722-1740]
  OracleRecall/CoFailure/Δ_m como métricas formais de convergência [101 =
  arXiv:2606.27288, preliminar/C]; envelopes de evidência com claims
  estruturados [~l.995] (o dedup deve keyar CAMPOS estruturados, não títulos);
  LLM-judge com auditoria de viés obrigatória [130 = arXiv:2406.07791, moderada/B].
  Pistas-solução citadas: DyTopo matching semântico [25], CoAgent reparo
  semântico advisory [191] — ambas `preliminar`.

## Fase 4 — Refine (crítica do orquestrador vs critérios (a)-(e))

Operações por cartão (24 findings → 4 famílias):
- **Two-stage lexical candidate detection (SimHash/MinHash/Jaccard-shingles +
  multi-scorer 2-de-3) → MANTIDA/COMBINADA** no núcleo: stdlib puro,
  determinístico, auditável. Sanity vs ground truth EXP-15: o par-verdade
  conhecido compartilha âncoras concretas na EVIDÊNCIA ("m4_status_html",
  "mock", "real") — keying por título+categoria+evidência tem recall plausível;
  é exatamente o que categoryFirstEvidence (1/83) já indicou.
- **Shadow-mode JSONL + false-pair rate antes de qualquer merge → MANTIDA**
  (converge com D008 e com a prop. 22 do artigo).
- **Embeddings/sentence-transformers → REJEITADA agora** (dependência pesada,
  não-determinismo; a própria wave argumentou contra; critério (a)).
- **LLM-judge pairwise → CONTINGÊNCIA** (só borderline pairs, 1 POST barato,
  com auditoria de viés [130]; entra apenas se o recall lexical medir baixo).

## Fase 5 — Deliver

**Portfólio:** núcleo = detector shadow-mode de pares candidatos no caminho do
reduce (advisory, zero merge — EXP-18); contingência = LLM-judge borderline;
rejeitadas = embeddings-agora, auto-merge silencioso; estacionada = matching
semântico DyTopo-style (gatilho: multi-tenant/escala).

**Recomendação ao owner:** implementar o EXP-18 (measure-only): estágio 1
Jaccard de shingles sobre título+categoria+evidência normaliza-dos; estágio 2
concordância 2-de-3 (Jaccard, containment, TF-IDF cosine — tudo stdlib);
pares candidatos vão para `merge-candidates.jsonl` + marcados ADVISORY no
reduce output (proveniência correlacionada à la artigo — nunca fundidos).
Promoção a merge real: SÓ com false-pair rate <5% em amostra revisada E recall
capturando o truth-set do EXP-15 — e mesmo então, via porta SPEC-116 owner-gated
(prop. 22: commit de merge é autoridade determinística+owner).

**Rastreabilidade:** EXP-15 (medição) → pergunta desta rodada → wave NVIDIA
24 findings + manuscrito 6 chunks → EXP-18 (registro no experiment registry) →
spec futura owner-gated se promovido.

**Implementação + medição 1 (2026-07-18, commit 7ad5321):** detector shipped
como `scripts/harness_lib/merge_candidates.py` + emissão fail-open no
`workflow_reduce` (advisory no dict de retorno + `merge-candidates.jsonl`;
artefato em disco byte-idêntico — schema `additionalProperties:false`).
Cenário `mc_merge_candidates` 4/4. **Medição 1 no card (EXP-18 ativo):**
truth-run 29 findings → 0 pares, recall 0/5; TODO paráfrase verdadeiro dispara
no eixo cosine (0.57–0.66) e nenhum alcança containment/jaccard — a regra
2-de-3 está estrita; próxima iteração de MEDIÇÃO registrada no card
(cosine-forte ≥0.55 + 1-de-2, re-medindo false-pair) — thresholds inalterados
até lá (measure-only; promoção segue prop. 22 owner-gated).

**Medição 2 (2026-07-18, grade Taguchi pré-registrada):** probe committável
`testing/probes/exp18_taguchi_grid_probe.py` (30 avaliações determinísticas;
asserção diferencial: célula A@0.50 == detector shipped, verde). Regra A
(2-de-3) recall 0.0 em todo T_COSINE — confirma medição 1. Regra B
(cosine-forte ≥T + 1-de-2 fraco a meio-limiar 0.175/0.30) em T=0.50/0.55:
**recall 0.6** (recupera mock-vs-real, never-failed, weak-assert; perde
bdd-tightening e info-per-check), false-pair proxy 0.0; T=0.60 degrada para
0.2. O delta 0→0.6 excede o spread cross-WF (pairRate stdev 0.012; floor L13).
**Veredito:** abaixo do critério de promoção (recall ≥0.8) — detector segue
measure-only com thresholds shipped inalterados; célula flat candidata = B@0.55.
Acima do critério de abandono. Artefato:
`.harness/runs/exp18-taguchi-grid-2026-07-18T205026Z.json`.

**Incidentes de processo da rodada (honestidade):** timeout 120s do
openai_worker estrangulou 4/5 workers (fix: 300s, commitado); maxRounds
consumido por erro de verbo do orquestrador (CLI é `retry <wf> <worker>` +
`run --force-round`, playbook diz "round" em prosa — correção candidata ao
playbook); executor-state restaurado a generic pós-rodada.
