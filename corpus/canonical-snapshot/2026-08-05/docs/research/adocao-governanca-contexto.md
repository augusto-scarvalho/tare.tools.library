# Rodada de pesquisa: adoção do estudo "Governança de Contexto em Harnesses Multiagênticos" (v2)

Data: 2026-07-28 | Orquestrador: sessão Fable (overseer) | Fase atual: 0→2 (Discover/Define)

## Questão

O que devemos adotar do estudo `docs/research/estudo-governanca-contexto-v2.md`
(uploaded pelo dono, 26/07/2026, revisão narrativa estruturada com ~60 fontes)
para tornar o gerenciamento de contexto do harness mais eficiente — sabendo que
o dono declara o gerenciamento atual "pouco eficiente"?

## Critérios de sucesso

1. Cada adoção proposta mapeia para um gap REAL do harness (evidência: path,
   medição ou incidente registrado) — nada adotado "porque o estudo manda".
2. Toda claim carrega prefixo de proveniência: `[estudo] §N`, `[repo] path`,
   `[judgment]`.
3. Saída em portfolio (núcleo | experimentos | estacionadas | rejeitadas) com
   esforço e risco declarados por item.
4. Mecanismo que JÁ existe no harness (mesmo parcial) é reconhecido antes de
   propor substituto.
5. Para na porta do human gate (Phase 2): briefs para aprovação do dono, sem
   wave Develop nesta rodada.

## Largura declarada (D010)

2 lentes, pedido explícito do dono ("você e o codex, usando vieses diferentes")
e pesquisa FOCADA (fonte única fixa, alvo definido — EXP-15 mediu que fan-out
maior aqui gera redundância, não cobertura):

- **Lente A — Claude/Fable (orquestrador, inline):** arquitetura & risco de
  complexidade acidental. Viés conservador: o que já temos, o que é gap real,
  o que é YAGNI para um harness deste porte (estudo §18.1/§18.11 admite que o
  Control Plane completo pode custar mais do que economiza).
- **Lente B — codex (gpt-5.6-sol high, lane read-only):** eficiência de tokens
  & operação. Viés agressivo de adoção: onde o harness desperdiça contexto
  HOJE, ranking ganho/esforço, cética quanto a proteger o design atual.

## Budget declarado

- Lane codex: 1 worker, sem fan-out; teto ~80k tokens (estudo ~41k tokens
  calibrados a 3.1 chars/token + leituras de repo + saída ≤500 linhas).
- Lente A: inline no orquestrador (sessão já paga).
- Sem waves 2-3; convergência é síntese manual do orquestrador (2 workers
  cabem num contexto — reduce single-pass desnecessário).

## Design declarado (L18)

Rodada Discover/Define — não produz experimento nesta fase. Cards que caírem
no bucket `experimentos` seguem o template hipótese/baseline/métricas/critérios
e só existem quando registrados via `harness.py experiment add` (Phase 5, após
o gate humano).

## Fase 0 — o que o repo já sabe (records/doc-find, 2026-07-28)

`records search` vazio para os termos; `doc-find context compaction checkpoint
reinjection` retorna as superfícies vivas:

- `[repo] scripts/harness_lib/context_checkpoint.py` — checkpoint in-flight +
  reinjeção pós-compact (o estudo chama de checkpoint canônico + reidratação).
- `[repo] scripts/harness_lib/context_diet.py` — SPEC-118 dieta de contexto
  por role (o estudo chama de least context privilege, §5.7).
- `[repo] tools/hooks/reload_context_after_compact.py` — reinjeção com partes
  protegidas nunca aparadas (o estudo chama de constraint pinning, §17.3);
  budget 9.8k chars, duas exaustões de margem (2026-07-24, 2026-07-27).
- `[repo] .harness/handoff/plan-reinj-recalibrate.READY` — check de budget da
  reinjeção grita no estado projetado (cry-wolf) — pendente.
- `[repo] scripts/harness_lib/result_contracts.py` + worker-result.schema.json
  — capsule tipado de retorno com tetos (o estudo chama de fold contract §7.4).
- `[repo] .harness/prompts/research-playbook.md §Budget` — required-reads ≈
  12.1k tokens POR WORKER duplicados em cada fork-join (~60k num 5-worker);
  sharedContextDigest existe como mitigação opt-in.
- `[repo] harness.py workflow fold` (F1) — fold manifest não-destrutivo de
  workflow FINALIZADO; `workflow evidence` — evidence bundles determinísticos.

## Artefatos da rodada

- Estudo (entrada): `docs/research/estudo-governanca-contexto-v2.md`
- Packet lente B: `.harness/handoff/packet-analise-codex-governanca.md`
- Resultado lente B: `.harness/handoff/analise-codex-governanca-contexto.md`
- Síntese + portfolio: seção final deste doc (preenchida na convergência)

## Lente A — arquitetura & risco de complexidade (Claude/Fable, inline)

### A1. O que o estudo prescreve e JÁ EXISTE aqui (não reconstruir)

| Mecanismo do estudo | Onde já vive | Estado |
|---|---|---|
| Estado canônico fora da janela (§3.3, §5.5) | git + backlog JSON + records + NEXT_STEPS/STATE/LEDGER_HEAD + handoff + `.harness/runs/` | existe |
| Constraint pinning (§17.3, Governance Decay) | `[repo] tools/hooks/reload_context_after_compact.py::_fit` — partes de disciplina NUNCA aparadas; só o estado cede | existe |
| Checkpoint canônico + reidratação (§6.4) | `[repo] scripts/harness_lib/context_checkpoint.py` — bloco inflight + render por arquivo com caps | existe |
| Capsule tipado de retorno (§7.4) | `[repo] scripts/harness_lib/result_contracts.py` + `schemas/worker-result.schema.json` (tetos: ≤50 findings, evidence ≤20×500, recommendation ≤1000) | existe |
| Least context privilege (§5.7) | `[repo] scripts/harness_lib/context_diet.py` SPEC-118 — medido 40.264→16.520 tok/turn (-59%) com dieta cheia | existe |
| Contrato de delegação (§7.7) | `[repo] .harness/prompts/subagent-contract.md` + plan briefs com footprint HARD | existe |
| Digest de wave compartilhado (anti required-reads, §11) | `sharedContextDigest: true` na maioria dos perfis de `.harness/workflows/workflow-profiles.json` | existe |
| GC de recursos não textuais (§8.15) | workspace cleanup pós-gate, kill-audit.jsonl, gate-hold, cleanup-worktrees | existe |
| Proveniência de claims (§17.4) | prefixos `[web]/[repo]/[judgment]` (SPEC-119 v5) | existe |
| Orçamento honesto (§14.2) | token-audit + calibração 3.1 chars/token + fuel show | existe |
| Fold de workflow terminado (§10) | `harness.py workflow fold` (F1, manifest não-destrutivo) + `workflow evidence` | parcial |

Conclusão A1: o harness já implementou, em forma embrionária, ~60% do que o
estudo chama de Fases 0-5 do roadmap (§19). O gap não é "construir o Control
Plane"; é fechar 4-5 buracos específicos.

### A2. Gaps reais, com a dor medida

- **G1 — A reinjeção empurra ESTADO para a janela em dumps, e perde a guerra
  do teto.** `[repo]` FILE_CAP 1400 bytes/arquivo (head+tail), teto vendor 10k,
  TOTAL_BUDGET 9.800; duas exaustões de margem (2026-07-24 em 9,5k;
  2026-07-27 em 9.933; untrimmed hoje 10.746). O estudo diz que a janela é
  visão materializada e a hidratação deve ser mínima com ponteiros (§3.3,
  §6.3, §5.5.1 — "não basta um summary.md", e um dump head+tail é PIOR que um
  summary). Adoção: reinjeção pointer-first — bloco inflight INTEIRO + próxima
  ação + ponteiros tipados por arquivo; parar de inline-ar head+tail de
  CONTEXT/STATE/LEDGER_HEAD (conteúdo estável, legível on-demand). Esforço M.
  Obs: `plan-reinj-recalibrate.READY` já ataca o sintoma (cry-wolf do check);
  G1 ataca a causa.
- **G2 — Não existe PreCompact.** `[repo] tools/hooks/` não tem hook de
  PreCompact; o checkpoint é disciplina do agente (`harness.py checkpoint` por
  fase). Compact no meio de uma fase ⇒ a reinjeção entrega checkpoint VELHO
  como se fosse atual (§3.5.2 mistura temporal, exatamente a falha que o
  estudo descreve). Adoção mínima: PreCompact TELEMÉTRICO — carimba
  compaction_count por sessão + alerta se o checkpoint está stale (idade >
  fase corrente); alimenta o sinal DELEGATION_TOO_COARSE (§14.13) de graça.
  NÃO bloquear compact (sessão presa em janela cheia é pior). Esforço S.
- **G3 — Overseer roda como sessão longa multi-item; o estudo recomenda reset
  por item (§6.1, H2).** A infra já existe (checkpoint, reinjeção, handoff,
  resume-*.md manuais em `.harness/handoff/`). Falta formalizar: item fechado
  → completion capsule → sessão nova. Tensão honesta: prompt cache de 1h
  empurra na direção oposta (§8.13 cache economics) — reset joga fora prefixo
  quente. Não decidir por fé: é o experimento H2 (baseline barato: comparar
  custo/qualidade de N itens em sessão contínua vs N itens com reset, usando
  os records que já existem). Esforço S no playbook + 1 experimento.
- **G4 — Lições viram prosa, não memória tipada (§11.4, H7).** O trail do
  checkpoint carrega entradas narrativas de ~2.5k chars (PT-BR livre); o
  render corta em BLOCK_CAP 1300 — ou seja, a lição mais nova compete com o
  cap e as antigas somem. Memória negativa tipada (claim rejeitado +
  evidence_refs + condição de reabertura) custa um campo no checkpoint/backlog
  row. Esforço S-M. Experimento H7 depois.
- **G5 — Zero telemetria de pressão de contexto por lane (§14.1; Fase 0 do
  roadmap §19).** fuel show dá usedPct de sessão do claude e gas do codex, mas
  nenhum record por lane registra pressure/compaction_count/tokens-pico. O
  próprio estudo ordena: telemetria ANTES de qualquer política. Sem G5, G1-G4
  não têm baseline. As superfícies já existem (rollout jsonl do codex,
  transcript do claude, stamps do runner). Esforço S.

### A3. YAGNI — rejeitar para o nosso porte (o estudo concorda em §18.1/§18.11)

- **Context Object Model + dependency graph + mark-and-sweep (§5.4, §8.5,
  §14.9):** somos consumidores de CLIs vendor; a janela viva não nos dá seam
  de GC por objeto. Custo enorme, ganho inacessível. O único seam real é o
  http-family (`tools/openai_worker.py`) — e é one-POST, sem sessão longa.
- **Compaction Profile Compiler + Integrity Gate semântico (§14.3/14.4):** a
  compactação nativa é opaca e não a controlamos; nosso contra-ataque
  (reinjeção + checkpoint + kernel protegido) já é a versão barata disso.
  Recovery probe = mais chamadas de modelo para validar resumo que o vendor
  vai reescrever no próximo compact.
- **Benchmark posicional próprio (§11.7, §16.4):** waves de eval caras;
  adotar os defaults do Apêndice C e recalibrar por incidente real.
- **Learned policies / curator model (§9.5, Fases 8-9):** fronteira de
  pesquisa, nenhuma dor atual que justifique.

### A4. Tensões estudo × design atual

1. Estudo: hidratação mínima com retrieval por fase (§6.3). Harness: reinjeção
   FIXA de 5 arquivos (REINJECT_RELS) sempre, independente de fase — um
   "sempre-tudo" em miniatura. A dieta corta por ROLE, não por FASE.
2. Estudo: reset por item como default (§6.1). Harness: sessão AFK longa +
   compact — e a economia de prompt cache do vendor recompensa isso (§8.13
   admite o trade-off; só experimento resolve).
3. Estudo: capsule tipado > narrativa (§10.7). Harness: o artefato de
   continuidade mais valioso (trail do inflight) é narrativa livre.

### Priorização da lente A (ganho ÷ complexidade)

G5 telemetria (S) → G2 PreCompact telemétrico (S) → G3 reset-por-item como
experimento H2 (S+EXP) → G1 reinjeção pointer-first (M) → G4 memória negativa
tipada (M, EXP H7).

## Lente B — eficiência de tokens & operação (codex gpt-5.6-sol high)

Resultado completo: `.harness/handoff/analise-codex-governanca-contexto.md`
(terminou com `ANALISE-COMPLETA`; claims ancoradas com [repo]/[estudo]/
[judgment] conforme o packet). Achados que a lente A NÃO tinha:

- **B1 (o desperdício nº 1, medido):** `WF-20260727-010246` pagou ~42.979
  tokens de stdout + ~14.125 de result JSON e aceitou **0 de 3 capsules** —
  todos estouraram `maxWorkerOutputChars` e foram INVALIDADOS inteiros. O
  contrato de retorno hoje é um gate de descarte, não um mecanismo de
  folding/offload (tensão direta com estudo §7.4/§10.8).
- **B2:** o digest de wave é compartilhado NO DISCO mas duplicado na janela
  de cada worker (~5.115 tokens × N workers), e carrega contrato que o papel
  não consome (~956 tokens/worker removíveis só de contratos inaplicáveis).
- **B3:** parent task + seed integrais interpolados em TODO packet
  (`worker_prompt.py:60-75`) — ~7.944 tokens repetidos na onda de 3.
- **B4:** a sessão proprietária paga hidratação DUPLA: reinjeção (~3.205
  tokens medidos) E releitura integral obrigatória dos 6 arquivos do
  AGENTS.md (~8.415 tokens) — ~11,6k tokens por início de sessão nos dois
  canais somados.
- **B5:** `context_diet` é no-op no caminho codex (sem knob de keepTools) —
  a dieta de -59% só existe no vendor claude.
- **Baseline proposta (determinística, zero chamadas de modelo):** tokens
  estimados por WORKER_RESULT VÁLIDO, computável de artefatos que já existem
  (`token-audit.json` + `validation.json` + stdout logs), com regra para
  denominador zero.

Rejeições da lente B coincidem com as da lente A: Control Plane integral,
learned policies/RL, compactação semântica com validator, object registry +
dependency graph.

## Convergência das duas lentes

| Tema | Lente A | Lente B | Veredito |
|---|---|---|---|
| Telemetria/baseline primeiro | G5 | ranking #6 + §5 baseline | CONVERGE — 1ª adoção |
| Trail do checkpoint é história cara | G4 (prosa) | desperdício #5 (~2,5k tok foldáveis) | CONVERGE |
| Hidratação dupla / reinjeção-dump | G1 | desperdício #6 + adoção #4 | CONVERGE (sequenciar após reinj-recalibrate) |
| Reset por item | G3 (experimento) | adoção #7 (sem estimativa) | CONVERGE — vira EXP, não fé |
| Capsule descarta em vez de degradar | — | B1 (dor nº 1 medida) | SÓ B — entra como núcleo |
| Digest por papel | — | B2 | SÓ B — núcleo (S/M) |
| PreCompact telemétrico | G2 | — | SÓ A — núcleo (S, telemetria) |
| YAGNI: Control Plane, RL, COM | A3 | §3 | CONVERGE — rejeitadas |

## Portfolio (Phase 2 — PARADO NO GATE HUMANO)

### núcleo (propostas para aprovação — briefs abaixo)

1. **BRIEF-1 Baseline & telemetria de contexto.** Métrica
   custo-por-capsule-válido computada de artefatos existentes + carimbo
   PreCompact (compaction_count por sessão, alerta de checkpoint stale).
   Critério de sucesso: todo workflow terminado ganha a métrica nos records;
   nenhuma chamada de modelo nova. Atores: implementer S. Restrição: só ler
   superfícies que já existem (token-audit, validation, rollout/transcript).
2. **BRIEF-2 Capsule degrada, não descarta.** Resultado acima do teto é
   offloaded para arquivo + ponteiro e o capsule entra truncado-válido
   (marcado `degraded`), nunca invalidado inteiro. Critério: o caso
   WF-20260727-010246 re-simulado produz 3 capsules degradados utilizáveis.
   Atores: implementer S/M. Restrição: schema aditivo, sem quebrar reduce.
3. **BRIEF-3 Trail fold.** Só a entrada mais nova do trail permanece inline;
   anteriores vão para arquivo de trilha com ponteiro. Critério: NEXT_STEPS
   cai de ~4,1k para <1,5k tokens de leitura integral sem perda de acesso.
   Atores: implementer S. Restrição: `checkpoint` CLI mantém contrato.
4. **BRIEF-4 Digest por papel.** O digest materializa autoridade comum + só o
   contrato que o papel consome. Critério: ≥956 tokens/worker a menos na onda
   de 3 medida, sem worker inválido novo. Atores: implementer S/M.

### experimentos (registrar via `experiment add` SÓ após aprovação)

- **EXP reset-por-item (H2 do estudo):** hipótese: reset físico por item
  reduz custo-to-success vs sessão contínua com compact. Baseline: métrica do
  BRIEF-1 em N itens de cada modo. Métricas: tokens/item, re-reads,
  retrabalho. Decisão: adotar reset como default do overseer-loop se custo
  ≤ +10% e qualidade ≥ igual. Card metodológico: matched-budget.
- **EXP memória negativa tipada (H7):** hipótese: campo tipado de hipóteses
  rejeitadas reduz retrabalho vs prosa no trail. Depende de BRIEF-3.

### estacionadas (reavaliar quando o baseline existir / o vendor destravar)

- Hidratação única pointer-first da sessão proprietária (A-G1 + B4) — M;
  sequenciar DEPOIS de `plan-reinj-recalibrate` e do BRIEF-1 provar o custo.
- Briefing branch-specific (B3) — M; mexe em worker_prompt, medir antes.
- Packing posicional por fase (B #8) — ganho de utilização não mensurável
  sem baseline.
- Dieta no caminho codex (B5) — bloqueada por superfície do vendor.

### rejeitadas (ambas as lentes, estudo §18 concorda)

- Context Object Model + dependency graph + mark-and-sweep agêntico.
- Compaction Profile Compiler + Integrity Gate semântico + recovery probes.
- Learned policies / RL / curator on-the-fly (Fases 8-9 do roadmap).
- Benchmark posicional próprio completo (usar defaults do Apêndice C).

## Rastreabilidade

`Evidência → Problema → Proposta`:

- token-audit + validation.json de WF-20260727-010246 → 43k tokens/0 capsules
  → BRIEF-2 (estudo §7.4, §10.8).
- Medições do codex em NEXT_STEPS.md (~3,4k tok de trail) → leitura canônica
  cara → BRIEF-3 (estudo §8.3, §8.12).
- token-audit digest (14.997 tok c/ digest numa onda de 3) + trecho de
  contrato inaplicável (~956 tok/worker) → BRIEF-4 (estudo §6.3, §9.10).
- Exaustões de reinjeção 2026-07-24/27 + dupla hidratação (~11,6k tok) →
  estacionada hidratação única (estudo §3.3, §6.3) — após BRIEF-1.
- Ausência de PreCompact + risco de checkpoint stale (§3.5.2) → BRIEF-1.

## Status da rodada

Phase 2 concluída em 2026-07-28. GATE HUMANO PASSOU (questionário, 2026-07-28):

- BRIEF-1..4 aprovados; execução DELEGADA (plan-role drafts → overseer
  finaliza → lanes com ritual completo).
- EXP-35 (reset-por-item, H2) e EXP-36 (memória negativa, H7) registrados.
- Adiados MANTIDOS adiados, mas ENCADEADOS no backlog para logo em seguida:
  `ctx-hidratacao-unica` e `ctx-briefing-por-ramo` (depends-on
  `ctx-medidor-custo`); dieta codex segue bloqueada por vendor.

Phase 5 executada: decisão D053 em `.harness/context/DECISIONS.md`; backlog
rows `ctx-medidor-custo` (P1), `ctx-capsule-degrada` (P1), `ctx-trail-fold`
(P2), `ctx-digest-por-papel` (P2) + as duas encadeadas acima.
