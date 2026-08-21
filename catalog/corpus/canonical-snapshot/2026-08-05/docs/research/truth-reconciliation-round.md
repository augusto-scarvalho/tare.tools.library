# Rodada #3 — motor de reconciliação de fontes da verdade (N-TRUTHRECON)

Rodada de pesquisa do item #3 do owner (2026-07-19): "a 'fonte da verdade' — bora
pesquisar e montar, é importante". Base: D015 + o achado do GM-5. Orquestrador =
esta sessão (não worker). Fase 0 aqui; onda de divergência via **NVIDIA**
(`nvidia-compat`, glm-5.2 smart tier — venceu o race-mode test #1).

## O problema (enquadrado como problema, não como solução — Fase 2 job-to-be-done)

O owner (D015): "múltiplas fontes da verdade — o código, a documentação, o
histórico empilhado, as documentações de terceiros. Um sistema sempre falha; o
que importa é estarmos preparados para quando ele falhar." A dor real não é
"escolher a fonte certa" — é **o que o harness faz quando as fontes DIVERGEM ou
uma delas cai**, sem que a decisão seja arbitrária ou silenciosa.

Fontes da verdade no harness hoje (o inventário real, `[repo]`):
- **código** — git é a fonte da verdade do código (CONTEXT.md).
- **harness** — fonte da verdade de estado de tarefa/continuidade/routing/handoff.
- **documentação** — specs (`specs/`), AGENTS.md/CLAUDE.md, docs de pesquisa.
- **histórico empilhado** — records ledger (SPEC-112), git log, event log
  (agora hash-chained + causal-DAG: T-HASHCHAIN/T-CAUSALPARENT).
- **documentações de terceiros** — docs de vendor (o que a rodada #5 mostrou:
  frequentemente erradas/ausentes — ex.: balance API que retorna 404).

Já existe uma fatia disso resolvida: **GM-3 provenance firewall** (retrieval de
memória governada só confia em item com `authority >= signed_policy`) e o
**GM-5** shadow-challenge (mede divergência doc↔código por commit). N-TRUTHRECON
é a **direção-mãe**: GM-3 vira uma fatia dela.

## Pergunta da rodada

> Quando duas ou mais fontes da verdade do harness (código, doc, histórico,
> vendor) **discordam** sobre um mesmo fato — ou uma fonte fica **indisponível** —
> qual mecanismo produz uma resposta **auditável, determinística e degradável**,
> com a doc como fonte preferida por padrão mas sem confiar cegamente nela?

## Critérios de sucesso (o que uma boa resposta precisa satisfazer)

- **Atores:** o harness (leitor de fato), o owner (ratificador de divergência
  não-resolúvel), workers (produtores de fato potencialmente conflitante).
- **Determinístico:** dada a mesma entrada de fontes, a reconciliação produz o
  mesmo veredito + a mesma trilha de auditoria (sem "vibes" de LLM no caminho).
- **Degradável (a exigência-MÃE do owner):** com N-1 fontes disponíveis o motor
  ainda responde, marcando a resposta como degradada e dizendo QUAL fonte faltou.
  "Preparado para quando falhar" = a falha de uma fonte é um estado de 1ª classe,
  não uma exceção não-tratada.
- **Doc-preferida mas auditável:** quando a doc é escolhida sobre o código, o
  motor grava POR QUÊ (a regra de precedência aplicada), não só o resultado.
- **Não reinventa:** reusa subject dimension, o hash-chain (T-HASHCHAIN), o
  provenance de GM-3, os confidence classes da pesquisa. Mede antes de controlar
  (D008): se a divergência real for ~zero (como o churn do C9), o motor não
  ganha enforcement — só instrumentação.

## Orçamento declarado (por onda)

- **Onda 1 (divergência):** 5 ideadores NVIDIA, ~12k tok required-reads/worker +
  ~740 tok packet ⇒ teto ~65k tok. Free-tier NVIDIA (custo desprezível em $;
  o custo real é tempo/RPM ~40/min por modelo). Gate de orçamento a 60%.
- **Onda 2 (crítica/convergência):** só com sinal forte + headroom. 4 críticos
  (validade, arquitetura, custo, segurança). Provável rodar com claude Max-window
  (crítica precisa ler o repo de verdade), NÃO NVIDIA.

## Largura declarada (D010)

**EXPLORATÓRIA → 5 ideadores.** Justificativa: é varredura de um campo
(reconciliação de fontes divergentes cruza sistemas distribuídos, proveniência,
CRDT/consenso, source-of-truth patterns, tolerância a falha) SEM alvo de
implementação fixo ainda. É exatamente o caso onde a diversidade de grupo nominal
paga (Diehl & Stroebe 1987) — o oposto do EXP-15, que puniu over-fan num tema
único já definido. Cada ideador ataca uma perspectiva distinta (o profile
research-divergence já traz: simplicidade, performance, confiabilidade,
trust-boundary, analogia cross-domain).

## Design declarado (L18)

A rodada FEEDA um experimento (EXP-22): medir divergência real entre fontes antes
de construir enforcement. Carta de método (**corrigida 2026-07-19 após cobrança do
owner** — a citação anterior, "measure-before-control + noise floor", era o
PRINCÍPIO D008, não uma carta do livro): **Confidence sequences**
(`docs/EXPERIMENT_METHODS.md#confidence-sequences`) + **Evidence grades**
(`#evidence-grades`). É a carta certa porque o probe é um experimento SHADOW:
sequência de confiança anytime-valid, **alpha budget α=0.05**, atualiza a cada
batch de `experiment record`, e assenta o veredito quando o intervalo cai TODO
abaixo do noise floor L13 (abandon → measure-only pra sempre, destino do C9) ou
todo acima de um nível enforce-worthy — sem penalidade de peek por espiar o número
ao vivo. Grade atual 2 (attributive); o flip pra enforcement exige
confirmatory-or-better + limpar o noise floor. O deliverable primário da rodada é o
DESENHO + a decisão de qual fatia é measure-only vs enforce.

> Nota de processo: o advisory L18 (`experiment_registry._METHOD_HINTS`) NÃO
> disparou pra este experimento — a tabela de keywords não tinha família pro
> padrão shadow/measure. Consertado no commit `e5a1a4b` (agora shadow/measure/
> canary/divergen/noise-floor → confidence-sequences+evidence-grades+noise-floor);
> `exl-5` cobre a regressão.

## Fase 1 — evidência (prep)

`doc-find "truth source reconciliation divergence"` → 0 hits (nada re-derivado).
Inventário de fontes acima é `[repo]`. Evidência externa a colher na síntese
pós-onda (Flow A/B): source-of-truth patterns, event-sourcing/CQRS reconciliation,
CRDT merge, W3C PROV para proveniência divergente, quorum/consenso degradável.

## Fase 3 — onda de divergência (a rodar)

`workflow plan --profile research-divergence --task "<brief truth-recon>"` →
`workflow run --executor nvidia-compat` → `collect` → `reduce --agent`.

### Brief da onda 1
> Projete o mecanismo pelo qual o harness reconcilia fontes da verdade
> divergentes (código, doc, histórico empilhado, docs de terceiros) e continua
> respondendo quando uma fonte cai. Restrições: determinístico e auditável (mesma
> entrada → mesmo veredito + trilha); doc como preferida por padrão mas com
> deução registrada; degradação de 1ª classe (N-1 fontes → resposta marcada
> degradada nomeando a fonte ausente); reusar subject dimension + hash-chain +
> provenance de GM-3; medir divergência antes de impor enforcement. Entregue: o
> modelo de precedência, o formato do registro de reconciliação, e o ponto de
> instrumentação measure-only que prova se vale enforcement.

## Próximos passos

Onda 1 → reduce → sintetizar em incrementos do backlog (novos N-* / fatias de
N-TRUTHRECON) → trazer o portfólio pro owner (o build é owner-gated: #3 é
"pesquisar E montar", e o montar depende da revisão conjunta).

---

# Fase 3-5 — resultado, convergência e portfólio (síntese do orquestrador)

Onda 1 rodou: `WF-20260719-050502-817281`, 5 ideadores NVIDIA (glm-5.2). Os 5
entregaram ideias fortes e DISTINTAS (a diversidade de grupo nominal pagou, como
previsto pro caso exploratório). O auto-reduce foi bloqueado (`canReduce=false`)
por dois motivos que NÃO invalidam o conteúdo — o orquestrador sintetiza à mão
(é o papel dele) e documenta o porquê:
- worker-003: `sourceFilesVerified required when high/blocker findings present` —
  um ideador de divergência marcou finding "high" sem verificar arquivo (esperado:
  ele não lê o repo). Conteúdo válido, gate de reduce estrito.
- worker-004 e worker-005: **falso-positivo do secret-scan** — o padrão
  `openai-style-key` (`sk-…`) casou DENTRO da palavra "ta**sk-**reconciliation-…"
  / "ta**sk-**truth-source-…" (um slug de task-id, não uma chave). Ver o item
  derivado N-SCANNER-FP abaixo. Os resultados são limpos; foram lidos e julgados.

## Convergência independente (o sinal mais forte — 3+ workers, sem se verem)

1. **Precedência = FUNÇÃO PURA, sem LLM no caminho** (w-001, w-003, w-005). Mesma
   entrada de fontes → mesmo veredito + mesma trilha. É o núcleo. `(sources:
   Map<SourceId, SourceState>) -> ReconciliationRecord`, zero estado, zero efeito.
2. **Probe measure-only ANTES de enforcement** (TODOS os 5). Um contador
   `divergenceCount`, zero bloqueio. Prova empírica se enforcement se justifica —
   confirma o D008/measure-before-control. Virou **EXP-22** (registrado).
3. **Degradação é EMERGENTE, não uma feature** (w-001, w-003, w-005). Com a fonte
   ausente o resolver simplesmente a pula (chave ausente no Map) e marca degradado
   nomeando-a — sem handler separado. Responde ao critério-mãe do owner.
4. **Reusar T-HASHCHAIN + GM-3 provenance firewall** (w-001, w-003, w-004, w-005).
   O gate `authority>=signed_policy` do GM-3 é o mesmo padrão de "validar antes de
   aceitar" — GM-3 vira a fatia de trust da reconciliação (confirma o backlog).

## Cartas de conceito + operação (Fase 4 — set-based, sem colapsar num score)

| carta | fonte | operação | por quê |
|---|---|---|---|
| **TR-CORE** — PrecedenceResolver função pura, 2 tiers | w-001+w-003 | **mantida+simplificada** | o núcleo. Simplificação do w-001: colapsar 4 fontes em **2 tiers** — AUTORITATIVO = git+records (compartilham hash-chain/T-HASHCHAIN) · ADVISORY = specs/AGENTS+vendor (sem proveniência cripto). "doc-preferida" vira um **mapeamento de tier** (specs no tier alto), não uma regra de runtime. |
| **TR-RECORD** — formato do registro de reconciliação | w-001(7 campos)+w-003(9 campos)+w-004 | **combinada** | campos convergidos: `{fact, winningSource, loserSources[], precedenceRuleApplied, tier, degraded:bool, absentSources[], inputHashes{}, at, subject}` + herda metadata do provenance-firewall (w-004). A `precedenceRuleApplied` é o "nunca cego": grava POR QUÊ a doc venceu. |
| **TR-PROBE** — instrumentação measure-only (divergenceCount) | todos | **experimento → EXP-22** | mede divergência real por commit/retrieval antes de qualquer enforcement. Se ≤ noise floor L13, o motor fica measure-only pra sempre (destino do C9). GM-5 já mede uma fatia (doc↔código). |
| **TR-DNS** — DNS como arquitetura de referência | w-005 | **mantida (esqueleto de projeto)** | DNS já resolveu ISTO: reconciliar zonas autoritativas + cache + histórico de resolver + upstream, determinístico e degradável, RFC-fundamentado. Mapa 1:1 → DNSSEC=GM-3; SOA-serial-compare=TR-PROBE (medir drift); TTL-freshness=confidence classes (rótulo de degradação); NXDOMAIN negative-cache=gravar precedência doc>código nunca em silêncio. De-risca o design inteiro. |
| **TR-TRUST** — hardening de fronteira de confiança | w-004 | **dividida (alimenta N-SECREVIEWER)** | 3 achados reais: (a) `absentSourceName` é um **side-channel** que vaza qual subsistema caiu — expor só a papéis autorizados; (b) **vendor/3rd-party docs = input não-confiável** → parsing sandboxed; (c) o TR-PROBE vira um **sink de dado sensível** se logar CONTEÚDO da divergência — logar contagem/hashes, nunca conteúdo. |
| **TR-PERF** — pipeline O(S×R)+cache+paralelo+backpressure | w-002 | **adiada (YAGNI até volume medido)** | performance só importa se o TR-PROBE mostrar volume. Same measure-first: não otimizar um caminho cujo volume ainda não medimos. Guardada como upgrade path. |
| **N-SCANNER-FP** — secret-scan casa `sk-` dentro de "task-…" | achado da rodada | **experimento/task** | bug real: o padrão `openai-style-key` precisa de âncora de word-boundary antes de `sk-` pra não casar "ta**sk-**slug". Custou 2 resultados válidos. Fix próprio (caminho de segurança — merece review isolado), não inline. |

## Portfólio (Fase 5)

- **núcleo:** TR-CORE (resolver 2-tier função pura) + TR-RECORD (registro) + TR-DNS
  (esqueleto/nomenclatura de referência).
- **experimentos:** TR-PROBE = **EXP-22** (measure-before-control; o único que
  posso CONSTRUIR já, pois é medição, não controle).
- **contingência:** TR-TRUST (hardening) — dobra no N-SECREVIEWER quando o owner
  abrir aquele papel (D014).
- **estacionadas:** TR-PERF (volume não medido).
- **derivadas:** N-SCANNER-FP (bug de segurança achado de brinde, como o oráculo
  do #4).
- **rejeitadas:** nenhuma — as 5 perspectivas foram complementares, não
  concorrentes (o que valida a largura exploratória do D010 aqui).

## O que é owner-gated vs o que posso construir já

- **Posso construir já (measurement):** TR-PROBE/EXP-22 — o probe measure-only que
  mede divergência entre as fontes (estende o GM-5 pras 4 fontes). Sem enforcement.
- **Owner-gated (o "montar" do #3):** TR-CORE + TR-RECORD como mecanismo ATIVO de
  reconciliação (é controle — precisa da medição do EXP-22 justificando primeiro,
  exatamente como C9). E N-SCANNER-FP (toca caminho de segurança).

## Matriz de rastreabilidade

| Evidência | Problema | Ideia | Experimento/ADR | Spec | Task | Status |
|---|---|---|---|---|---|---|
| w-001/003/005 (função pura) + DNS RFC1035/2181/4035/2308 (w-005) | fontes divergem/caem, resposta tem que ser determinística+degradável | TR-CORE 2-tier + TR-DNS | D020 | (owner-gated) | N-TRUTHRECON-CORE | desenhado |
| todos os 5 (measure-first) + GM-5 | não construir controle sem medir divergência | TR-PROBE | **EXP-22** | — | N-TRUTHRECON-PROBE | registrado, buildável |
| w-004 (trust boundary) | registro/probe/degradação são superfícies sensíveis | TR-TRUST | D020 | (contingência) | dobra N-SECREVIEWER | desenhado |
| achado da rodada | secret-scan casa `sk-` em "task-…" | N-SCANNER-FP | — | (owner-gated, security) | N-SCANNER-FP | achado |

## Fontes (Fase 1 pós-onda, `[web]` a verificar contra primária)
- DNS como reconciliador determinístico degradável: RFC 1035 (resolução iterativa),
  RFC 2181 §9 (trust ranking), RFC 4035 (DNSSEC validation), RFC 2308 (negative
  caching). `[web]` citados pelo w-005 — âncoras primárias fortes (IETF), a
  reconferir na promoção. Confiança: moderada; maturidade: **produção** (DNS roda o
  mundo há 40 anos).
- Internas `[repo]`: T-HASHCHAIN, GM-3 provenance firewall, GM-5 shadow-challenge,
  D008 measure-before-control, noise floor L13.
