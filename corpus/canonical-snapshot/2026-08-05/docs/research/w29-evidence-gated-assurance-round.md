# Rodada de pesquisa — W29: evidence-gated assurance (monitor semanal 13–20 jul 2026)

Owner 2026-07-21: rodada Double Diamond sobre o feed do monitor semanal de qualidade de
código agêntico. Executores: **NVIDIA (nvidia-compat) + Sonnet 5** (padrão D012 /
compaction-round). Orquestrador = esta sessão (Fable). Fontes primárias VERIFICADAS via
WebFetch nos abstracts do arXiv em 2026-07-21 (números do digest conferem).

## Fase 1 — Evidência (verificada)

| claim | source | prov | conf | maturity |
|---|---|---|---|---|
| Transições de estado gated por evidência mecânica reduzem false-pass 31→2 em 1.800 células injetadas; 18 classes de adulteração rejeitadas; revisor sem gate ≠ gate (14 vs 2 falhas) | Proof-or-Stop, arXiv:2607.14890 (2026-07-16) | [web] verificado | moderada (1 família de modelo; corpus self-hosted) | protótipo |
| Testes agênticos: melhor variedade de edge cases (0,62 vs 0,32) e null-safety (13,4% vs 8,3%), MAS mais flakiness-candidates (0,41 vs 0,30) e assertions levemente mais fracas (85,4% vs 88,1%); 204.673 artefatos, proxies AST estáticos, Python-only | Beyond Test Presence, arXiv:2607.12068 (2026-07-13) | [web] verificado | forte (escala) / moderada (proxies, não execução) | validado (estático) |
| E3 (Estimate→Execute→Expand-on-failure): −85% custo, −91% tokens, −92% arquivos lidos com 100% de sucesso mantido em MSE-Bench (121 edições, simulador; validação real = 1 agente/1 lib) | E3, arXiv:2607.13034 (2026-07-14) | [web] verificado | moderada (benchmark controlado, tarefas simples) | protótipo |
| Avaliar a CADEIA de artefatos (requisitos→modelo→validação→relatório) em vez do output final: 56,8%→88,6% pass em 10 combos agente-modelo | StructureClaw, arXiv:2607.14896 (2026-07-16) | [web] verificado | moderada (domínio: eng. estrutural) | protótipo |
| Qualidade em camadas (estática→funcional→semântica→hardening); skill especializada +10,31pp de rubric pass rate médio, 6 modelos | Alipay-PIBench, arXiv:2607.14573 (2026-07-16/17) | [web] verificado | moderada (18 instâncias, 1 ecossistema; rubric parcialmente LLM = pseudo-oráculo) | protótipo |
| Digest completo (análises, tabelas de impacto, experimentos recomendados) | monitor GPT do dono, 2026-07-21 | [web] NÃO-verificado além dos 5 primários | relato | — |

## O que o harness JÁ tem (mapa portfólio-do-feed → estado real; não re-propor)

- **Gates adaptativos por risco** → CQ.1 risk-tier gate selection SHIPPED (consome
  `security['new']`; fail-closed unknown→medium); intake-triage por perfil de request.
- **Evidence bundles** → CQ.2 QA evidence capsule + `rerunCmd` SHIPPED (handles-not-bodies);
  fold/handles/digest. Falta: FRESCOR/invalidação e gate que BLOQUEIA transição.
- **Quality debt ledger** → CQ.3 provenance record SHIPPED (records + subject). Falta:
  flakiness/assertion-quality como dívida registrada; acompanhamento pós-merge.
- **Mesh de oráculos** → spec_test_gate heterogêneo + `oracle mutate`/`mutation_probe.py`
  SHIPPED (observe-only, cap 3, exit-classes honestos). CQ.4 (oracle-replay) e CQ.5
  DEFER no shared oracle runner (não construído).
- **Proof-carrying patches** → SEC.7 admitter DEFER (recompute determinístico no finalize;
  "reviewer.result.json é testemunho, não prova").
- **E3-adjacente** → economia TE.1–TE.5, doc-find-first (search guard), context diet
  (−59%/turno), D010 largura declarada. Falta: ladder de execução mínima POR TAREFA com
  expand-on-failure; effort é hoje escolhido pelo overseer, não estimado/escalonado.
- **Validade temporal de evidência** → convergência INTERNA independente: a onda
  WF-20260720-175712 (THEME1 safe-skip) já propôs invalidation-events (gate-version bump,
  graph rebuild, flaky scenario) + gate-state manifest — o feed chega ao mesmo lugar.
- **Shadow benchmark / hidden checks** → NÃO existe (park anterior: benchmark privado é
  rodada própria).
- **Sentinel arquitetural** → parcial (Graphify + checks estruturais do spec_test_gate).

## Fase 0 — Pergunta, critérios, budget, largura, design

**Pergunta.** Dado o que já está shipped acima, O QUE o harness deve adotar do W29:
(a) transições de estado gated por evidência fresca/vinculada (Proof-or-Stop),
(b) qualidade de teste como sinais separados alimentando o ledger (Beyond Test Presence),
(c) execução mínima suficiente com expansão por falha (E3) — e como, sem violar os
invariantes (deterministic-first, sem daemon, stdlib-core, observe→enforce, fail-closed,
net-cost-positive, evidência≠prova formal)?

**Critérios de sucesso.** Itens buildáveis mapeados a seam VERIFICADO (arquivo/módulo);
cada um move UMA métrica nomeada; distinção honesta evidence-carrying vs proof-carrying;
nada re-propõe o shipped; críticas citam fonte/medição; incerteza registrada.

**Budget declarado.** 1 onda de divergência dual-vendor: NVIDIA 5 ideadores
(research-divergence, créditos livres, D012) + Sonnet 5 3 ideadores (subagentes bounded,
1 por brief). Convergência pelo orquestrador com verificação determinística de seams.
Onda de crítica só com headroom + sinal forte (default: não).

**Largura declarada (D010).** Exploratory — 3 temas independentes vindos de 5 papers,
sem alvo de implementação único; NVIDIA 5 lentes + Sonnet 3 lentes; Δm justificado pela
verificação cruzada vendor-independente (padrão das rodadas compaction/ptc).

**Design declarado (L18).** Experimentos prováveis → cards de EXPERIMENT_METHODS.md:
false-DONE probe → **Oracle recall**; comparação E3-ladder vs full → **Matched-budget
controls**; flakiness por repetição → **Noise floor** + **Confidence sequences**;
promoção de gate observe→enforce → **Evidence grades**.

## Fase 2 — Briefs (gate: escopo/ondas/budget pré-aprovados pela invocação do owner)

**Brief 1 — Transição só com evidência (Proof-or-Stop → harness).** Como as transições de
estado do workflow (fulfilled → reviewed → finalize/DONE) poderiam EXIGIR evidência atual,
vinculada ao commit e mecanicamente re-checável (CQ.2 capsule + rerunCmd + SEC.7 recompute),
com eventos de invalidação explícitos (rebase, dep change, test edit — dobra com THEME1
safe-skip) — atores: overseer/reviewer/gate; restrições: recompute determinístico, sem
alegar prova formal, fail-closed, custo O(capsule)?

**Brief 2 — Qualidade do teste como sinal, não presença (Beyond Test Presence → harness).**
Como medir a qualidade dos testes/self-checks escritos por agentes — força de assertion,
hermeticidade (fs/rede/relógio/ordem), flakiness sob repetição, mutant-kill — como sinais
SEPARADOS (nunca um score único) alimentando o provenance record CQ.3 como dívida — proxies
AST stdlib primeiro, repetição com budget, observe-first?

**Brief 3 — Execução mínima suficiente com guardrails (E3 → harness).** Como escalonar o
esforço por tarefa (estimar → caminho mínimo → expandir SÓ em falha de verificação) numa
ladder que preserve um conjunto pequeno de invariantes globais baratos SEMPRE (tensão
E3 × sentinel) — encaixe: intake-triage, tiers CQ.1, effort/model do spawn economy;
métrica: custo/rodada sem aumento de retrabalho?

---

# Fase 3 — Ondas (dual-vendor, independentes)

- **Onda A (NVIDIA)**: `WF-20260721-205509-246398`, research-divergence, 5 ideadores
  glm (nvidia-compat), packet auto-contido. Round 1: 3/5 válidos; retry: worker-004
  (trust-boundary) recuperou; worker-004 falhara por contrato (finding high sem
  `sourceFilesVerified`), worker-005 (analogia) foi RETIDO 2× pelo secret-scan do
  collect (escreveu exemplos com formato de API key; boundary WITHHOLDS por design —
  não contornado). Reduce parcial: **4/5 válidos, 22 findings dedup, 0 conflitos**.
- **Onda B (Sonnet 5)**: 3 ideadores independentes (1 por brief), read-only com
  verificação de seam linha-a-linha no código real. 18 concept cards (B1-1..6,
  B2-1..6, B3-1..6).
- **Correção load-bearing da Onda B** ao baseline da Fase 0: CQ.1 está shipped
  **observe-only** (`spec_test_gate.py:1226` emite tier; nenhum consumidor decide
  execução com ele) — vira o argumento central de F3.

## Onda 2 (especulativa, owner 2026-07-21: "sem a âncora não-re-proponha")

Waves 2-3 do playbook (técnicas estruturadas de geração; SEM --seed, geração continua
independente). **Largura declarada (D010):** exploratory — NVIDIA 5 branches-técnica
(inversão de premissas, contradição TRIZ, provocação, transferência analógica,
recombinação morfológica) + Sonnet 3 lentes livres (inversão/futuro, analogia selvagem,
auto-evolução). Δm: cada branch é uma TÉCNICA distinta, não uma perspectiva — overlap
esperado baixo. **Budget:** research-divergence + 3 subagentes bounded; convergência
pelo orquestrador. Regras frouxas de propósito: pode colidir com o que existe (dedup na
convergência), seam não obrigatório, especulação marcada [judgment] bem-vinda; maturidade
declarada por ideia.

### Resultado da Onda 2 (2026-07-21)

`WF-20260721-212457-539637`: 5/5 branches-técnica NVIDIA (25 findings dedup, reduce
done; worker-morfologia precisou de 1 retry por resultado ausente) + 3 Sonnet (21
ideias). Total 46 ideias brutas. **Clusters de convergência vendor-independente:**

1. **Evidência que apodrece** — mark-to-market (Sonnet analogia) + PROVA-QUE-APODRECE
   (NVIDIA morfologia) + validade temporal do feed: frescor CONTÍNUO precificado
   (churn-distance), não só invalidação binária. Upgrade conceitual direto de N2/N3.
2. **Confiança como moeda dinâmica** — o maior cluster: mercado de apostas + seguro de
   código (NVIDIA provocação), mercado de confiança 2028 (Sonnet), ônus da prova
   deslocável (Sonnet analogia), DEPRECIACAO-REPUTACIONAL/VETO-CADUCO/IMUNIDADE-
   CONTESTADA (morfologia), curva custo-qualidade (auto-evolução). Rigor por track
   record, não por regra estática.
3. **Autor ≠ atestador radical** — evidência-capturada-por-terceiro (NVIDIA inversão),
   AUDITOR-FANTASMA (adversário durante execução), tribunal de agentes, timo de agente.
4. **Gate dissolvido no tempo** — gate-adiante-contínuo (mid-generation), gate ambiente
   (LSP de invariantes), gate escalonado/pré-validação em cache (TRIZ).
5. **Promoção por estágios com vigilância** — fases clínicas I-IV (NVIDIA) ↔ probation
   automática de regra + reversão por métrica (Sonnet auto-evolução, com salvaguardas
   nomeadas p/ os limites deliberados).
6. **Inválido irrepresentável** — jardim murado (constrained decoding), repo-que-se-
   recusa (footprint como capability do SO — semente JÁ existe: locks OS do SPEC-148),
   contra-poder determinístico, cofre transacional.
7. **Memória/imunidade do harness longevo** — imunidade adquirida (assinaturas de
   classes de falha), tolerância adaptativa self/non-self de findings, arquivo de
   ancestrais de config (melhor ancestral ≠ mais recente, Darwin Gödel).

**Singletons notáveis:** partidas dobradas no ledger (todo evento com débito+crédito
reconciliáveis); MEL de gates (degradação declarada com prazo+compensação, nunca
silenciosa); cordão andon (qualquer worker para a linha); postmortem blameless (ledger
registra tentativas descartadas); perturbação intermediária (chaos calibrado);
tempo-até-triagem como KPI do próprio loop; contexto-contrátil com GC semântico
fidelity-gated; confiança espectral com orçamento de risco por workflow.

**Status:** colheita entregue; owner escolheu 3 apostas (2026-07-21) e elas SHIPARAM
observe-first no mesmo dia: **prova-que-apodrece** (`evidence_decay.py` + `headSha` no
plan + sha no provenance do finalize = fecha W29.N1), **rigor por track record**
(`track_record.py` + seção `trackRecord` no `metrics`, info-only), **canário
adversarial permanente** (`oracle canary`/`--trend`/`mutate --record` = fecha a metade
persistência do W29.N4). Backlog: linhas W29.A1–A3. Demais ideias seguem estacionadas
aqui aguardando escolha.

# Fase 4 — Convergência cross-vendor + operações explícitas

## Convergências (vendor-independentes = o sinal de validação da rodada)

1. **Enum ÚNICO de invalidation-events** — 3 fontes independentes: NVIDIA
   (F1-INCR-01 registry; eventos model-swap/secret-rotation do trust-boundary),
   Sonnet B1-3 (promover a taxonomia de `gate-affected-cache.md:57-60` a módulo
   compartilhado), e a convergência INTERNA prévia (WF-20260720-175712 THEME1).
   A mais forte da rodada.
2. **Evidência vinculada a commit por content-hash + SHA** — NVIDIA F1-PERF (cache
   de verdict keyed por content-hash+SHA) + F1-INCR-02 (staleness TTL) ↔ Sonnet
   B1-1 (capsuleHeadSha no review gate), B1-2 (fechar o TODO de sha no CQ.3,
   `workflow_lifecycle.py:108`), B1-4 (hash de teste editado pós-execução).
3. **Proxies AST stdlib como dívida no ledger, sinais SEPARADOS** — unânime
   (NVIDIA w-001/002/003 + Sonnet B2-1/2/5). Sonnet acha o que worker cego não vê:
   o fio CQ.5→CQ.3 está SOLTO (mutation probe calcula killed/survived e não persiste
   nada; `cli_registry.py:96` é o único caller).
4. **Flakiness: candidato estático → confirmação dinâmica bounded (cap ~3)** —
   NVIDIA F2-INCR-02 ↔ Sonnet B2-2/B2-3 (mesma filosofia do MAX_MUTANTS=3).
5. **Ladder E3 com conjunto PEQUENO de invariantes sempre-ativos, estimador
   DETERMINÍSTICO já existente** — NVIDIA F3 (ladder + invariantes como checkpoint
   pré-fixo) ↔ Sonnet B3-1 (consumidor do tier CQ.1), B3-4 (invariantes = os 3
   mecanismos não-puláveis JÁ existentes; não inventar lista nova), B3-5 (TE.7 é o
   expand-on-failure já desenhado). Ambos vendors: NÃO adicionar estimador LLM.

## Conflitos/tensões (registrados, não escondidos)

- **C1**: dono do executionLevel — consumidor downstream do CQ.1 (B3-1, acoplamento
  frouxo) vs campo no wire contract do router SPEC-144 (B3-2). Decisão: B3-1
  primeiro; B3-2 estacionado (mesmo padrão leve-vs-pesado das rodadas anteriores).
- **C2**: flakiness por amostragem estatística (NVIDIA F2-PERF) vs cap determinístico
  fixo (Sonnet B2-3). DNA deterministic-first → cap fixo; amostragem estacionada.
- **C3**: cache de verdict de evidência (NVIDIA F1-PERF) é OTIMIZAÇÃO sobre o check
  de frescor simples (B1-1) — só se o freshness check medir caro. Contingência.
- **C4** (da própria onda): B1-5 (cross-check testemunho×capsule) tem risco de scope
  creep para recompute total (= SEC.7, deferido). Mantido como cross-check APENAS.

## Operações explícitas por conceito

| Conceito | Operação | Destino |
|---|---|---|
| B1-2 fechar TODO de sha no provenance (CQ.3) | mantida | núcleo N1 |
| B1-3 + NVIDIA registry + w-004 model-swap → enum único de invalidação | combinada | núcleo N2 |
| B1-1 capsuleHeadSha + B1-5 cross-check testemunho×exitClass | combinada | núcleo N3 |
| B1-4 hash de teste pós-execução | combinada (evento no N2, check no N3) | núcleo N2/N3 |
| B2-4 fio mutation-probe→ledger + B2-5 schema único de sinais | combinada | núcleo N4 |
| B2-1 + B2-2 proxies AST (+ NVIDIA F2 unânime) | mantida | núcleo N5 |
| B2-6 superfície observe-only no gate | mantida (depende N4/N5) | núcleo N6 |
| B3-1 consumidor tier→nível (+ NVIDIA F3 ladder) | mantida | núcleo N7 |
| B3-4 nomear/congelar os 3 invariantes existentes como piso | simplificada (doc, não código) | núcleo N8 |
| Probe false-DONE (feed + Proof-or-Stop) | experimento | EXP-31 |
| B2-3 repetição bounded p/ flakiness | experimento | EXP-32 |
| B3-5 promover TE.7 como ladder (A/B já prescrito) | experimento | EXP-33 |
| NVIDIA F1-PERF cache de verdict | adiada | contingência (gatilho: freshness check custa caro) |
| B3-3 eixo diff_scope (tamanho) | adiada | contingência (gatilho: EXP-33 mostra subestimação em diff broad) |
| B1-6 servedModel como invalidação | adiada | aposta-de-fronteira (pré-requisito: classificar evidência LLM-judged vs determinística; dobra com EXP-5) |
| B3-2 executionLevel no wire do router | adiada | estacionada (C1) |
| NVIDIA F2-PERF amostragem estatística | adiada | estacionada (C2) |
| B3-6 regra de não-rebaixamento (ESI) | adiada | estacionada (até a ladder existir) |
| w-004 hermeticidade de egress + secret-in-fixture | adiada | estacionada (sobrepõe agenda SEC; sem gatilho novo) |
| PERF-CROSS early-exit por token bound | adiada | estacionada (território TE; exige medição própria) |
| Score único de qualidade de teste | rejeitada | (por instrução do brief + paper) |
| Estimador LLM de complexidade | rejeitada | (ambos vendors: função computável) |

# Fase 5 — Portfólio

- **Núcleo** (ordem de build; todos observe-first, seams verificados): N1 sha no
  CQ.3 (`workflow_lifecycle.py:108`, TODO marcado) → N2 enum de invalidation-events
  compartilhado (dobra gate-affected-cache + THEME1) → N3 frescor no review gate
  (capsuleHeadSha + cross-check exitClass, `workflow_reduce.py:488-528`) → N4 fio
  mutation-probe→records + schema único de sinais (`result_contracts.py:18` reusado)
  → N5 `test_quality_ast.py` proxies (assertion/edge/null/flaky-candidate, sinais
  separados) → N6 check_* observe-only no gate → N7 consumidor tier→nível
  (`spec_test_gate.py:1226`) → N8 doc "piso universal" (floor router + _RISK_HIGH_FILES
  + HARD footprints).
- **Experimentos** (registrados no registry): EXP-31 false-DONE probe (card
  método: Oracle recall), EXP-32 flakiness bounded repetition (cards: Noise floor +
  Confidence sequences), EXP-33 ladder A/B TE.7 (card: Matched-budget controls).
- **Contingência**: cache de verdict; diff_scope.
- **Aposta-de-fronteira**: servedModel/model-swap enforcement (dobra EXP-5).
- **Estacionadas**: B3-2, amostragem estatística, não-rebaixamento ESI, egress/
  fixture-hermeticidade, early-exit por token.
- **Rejeitadas**: score único; estimador LLM.

## Rastreabilidade

`Evidência → Problema → Ideia → Experimento/ADR → Spec → Task → Status`:
- arXiv:2607.14890 → transição por testemunho → N2/N3 (+EXP-31) → DECISIONS D-w29 → backlog EG.* → proposto
- arXiv:2607.12068 → qualidade de teste invisível → N4/N5/N6 (+EXP-32) → DECISIONS D-w29 → backlog TQ.* → proposto
- arXiv:2607.13034 → esforço máximo por default → N7/N8 (+EXP-33) → DECISIONS D-w29 → backlog EL.* → proposto
- StructureClaw/PIBench → reforço (cadeia de artefatos; qualidade em camadas) → sem item próprio (já coberto por capsules/tiers) → — → coberto
