# Rodada RD-TAINT — taint de dado não-confiável / CaMeL (o secret nunca egressa)

Research-gated backlog item RD-TAINT. 3ª e última das 3 rodadas de
implementação-research (owner 2026-07-19). Pré-req Q7-1 (sandbox SPEC-151) ✅
shipado. Orquestrador = esta sessão. Divergência via **NVIDIA** (`nvidia-compat`,
glm-5.2).

## Por que esta rodada existe

O artigo §7.1 o2: **um dado que foi secret-read nunca deve egressar** (sair pra um
vendor, pra web, pra um log persistido). O sandbox (Q7-1) contém o PROCESSO
(filesystem/rede por tier), mas NÃO rastreia o DADO: um worker pode ler um segredo
e, dentro do seu tier permitido, mandar ele pra API do vendor no prompt. Esse é o
gap que o sandbox não pega — precisa de **taint tracking** (marcar dado
não-confiável/sensível e barrar o egresso), estilo **CaMeL** (a linha de
capabilities/data-flow pra agentes LLM). Research de COMO IMPLEMENTAR leve, não de
medição.

## Pergunta da rodada

> Como implementar **taint tracking leve** no harness pra que um dado marcado como
> secret-read (ou não-confiável: web-fetched, worker-produced) **nunca egresse** —
> num sistema Python de subprocess/JSON, sem um runtime de dataflow pesado, reusando
> o secret-scan + o subject dimension + os trust tiers que já existem?

## Critérios de sucesso

- **Atores:** o worker (produz/lê dado tainted), o harness (barra o egresso no
  ponto de saída), o owner (break-glass auditado se PRECISAR egressar).
- **Leve e Python-real:** sem instrumentação de bytecode / dynamic taint pesada;
  algo que funcione na fronteira de I/O (o ponto onde o dado sai — prompt pro
  vendor, WORKER_RESULT persistido, log). Taint como METADADO que viaja com o
  dado, não análise de fluxo do interpretador.
- **Fail-closed no egresso:** dado tainted chegando num sink de saída → BLOQUEIA
  (ou redige) por padrão; egresso só com break-glass auditado (paralelo ao
  fail-closed do sandbox_prepare).
- **Reusa o que existe:** o **secret-scan** (já detecta shape de segredo na
  fronteira do worker — é meio-taint), o **subject dimension** (proveniência do
  dado), os **trust tiers** (first-party vs third-party do executors.json), o
  provenance firewall do GM-3 (authority). CaMeL só onde pagar.
- **Honesto sobre o teto:** taint por propagação explícita (marca na fonte, checa
  no sink) NÃO pega laundering implícito (o LLM parafraseia o segredo). Declarar
  esse limite — é defense-in-depth, não prova.

## Orçamento + largura + design declarado

- **Onda 1:** 5 ideadores NVIDIA, teto ~65k tok (free-tier). Gate a 60%.
- **Largura (D010): EXPLORATÓRIA → 5.** Taint/IFC cruza information-flow control,
  CaMeL/capabilities pra LLM, taint analysis clássico (Perl/Ruby), DLP, e
  provenance — campo amplo.
- **Design (L18):** rodada de SEGURANÇA (fecha o gap o2). Pode gerar um probe
  measure-only (quantos dados tainted chegariam a um sink hoje?) antes de enforcement
  — measure-before-control. O advisory de shadow/measure agora dispara (e5a1a4b);
  carta final na síntese.

## Fase 3 — brief da onda 1

> Projete o taint tracking LEVE do harness pra que um dado secret-read (ou
> não-confiável: web-fetched, worker-produced) NUNCA egresse (prompt pro vendor,
> WORKER_RESULT persistido, log). Contexto real: workers são subprocess Python que
> trocam JSON; já existe (1) secret-scan que detecta shape de segredo na fronteira
> do worker, (2) subject dimension (proveniência: self vs target), (3) trust tiers
> (first-party/third-party no executors.json), (4) o provenance firewall do GM-3
> (authority>=signed_policy). Precisa: (1) ser LEVE — taint como METADADO que viaja
> com o dado (marca na fonte, checa no sink de I/O), NÃO instrumentação de bytecode
> / dynamic taint do interpretador; (2) FAIL-CLOSED no egresso — dado tainted num
> sink de saída BLOQUEIA/redige por padrão, egresso só com break-glass auditado
> (paralelo ao sandbox_prepare); (3) REUSAR os 4 mecanismos acima em vez de um
> subsistema novo; (4) mapear no modelo CaMeL (capabilities/data-flow pra LLM) SÓ
> onde pagar. Entregue concretamente: o MODELO de taint (o que marca a fonte, como o
> metadado viaja pelo JSON do WORKER_RESULT, onde estão os SINKS de egresso), o
> ponto de ENFORCEMENT fail-closed, e o TETO honesto (taint explícito não pega
> laundering implícito quando o LLM parafraseia o segredo — é defense-in-depth).

---

# Fase 3-5 — resultado e síntese (RD-TAINT)

Onda 1: `WF-20260719-060140-203270`, 5 ideadores NVIDIA (glm-5.2). A convergência
mais forte das 3 rodadas — os 5 no mesmo modelo, incluindo o mesmo insight de
segurança e o mesmo teto honesto.

## Convergência unânime (5/5)

**Taint = ENVELOPE de metadado NÃO-FORJÁVEL** que:
1. **Marca na fonte** em 3 origens: `secret_read` / `web_fetch` / `worker_output`.
2. **Viaja num envelope injetado pelo HARNESS, FORA do controle do worker** — o
   insight de segurança que os 5 tiveram independentemente: como o worker escreve
   JSON arbitrário no WORKER_RESULT, um marcador de taint INLINE seria FORJÁVEL (o
   worker omite). O envelope tem que ser embrulhado/assinado pelo harness, nunca um
   campo que o worker emite.
3. **Enforcement fail-closed no sink de egresso = ESTENDER o secret-scan que já
   existe** (ele já é "meio-taint": detecção no sink). 3 sinks: prompt pro vendor,
   persistência do WORKER_RESULT, log. Bloqueia/redige por padrão; egresso só com
   **break-glass auditado** (paralelo ao sandbox_prepare SPEC-151).

**CaMeL (5/5 consistente):** mapear só o split **control-plane** (política de taint
+ capability/authority) vs **data-plane** (valores). Restringir ao control-plane
reusando trust-tiers + GM-3 authority>=signed_policy (já são capability-like); NÃO
construir um runtime de IFC por-valor (pesado demais pra nossa escala).

**Teto honesto (os 5 declararam — disciplina):** taint explícito marca a FONTE, não
o conteúdo derivado semanticamente. Se o worker lê o segredo e o LLM PARAFRASEIA num
texto novo, o taint não segue a paráfrase. **Defense-in-depth, não prova.** O
secret-scan por shape pega padrão, não laundering semântico.

## O que cada perspectiva adicionou

- **w-001 (simplicidade):** 3 partes móveis (stamp na fonte, envelope, enforcement
  no sink); footprint = 1 tipo de envelope + 1 função de check + 1 evento de auditoria.
- **w-002 (escala):** o check é **O(campos-tainted-alcançáveis)**, não O(todos os
  campos) — crítico pra resultado grande (listas de arquivo, saída de teste). O
  break-glass audit tem que ser **rate-limited/batched** (fork-join com N workers
  batendo break-glass floodaria o append_event). Custo dominante já é o shape-match
  do secret-scan; taint adiciona O(1) marginal.
- **w-003 (confiabilidade):** fail-closed no egresso precisa de **rollback de
  escrita parcial** (evitar egresso meio-redigido); se o próprio taint-check
  CRASHAR, o resultado NÃO egressa não-redigido (fail-closed no checker também);
  audit estruturado.
- **w-004 (trust-boundary):** envelope **assinado** (transporte não-forjável);
  estender o seam do secret-scan pra checar o `taint_map`, não só a shape.
- **w-005 (analogia): três referências comprovadas** — **email
  Content-Disposition/X-Header** (metadado viaja com o payload, checado na fronteira
  MTA de egresso) = isomorfismo exato; **declaração alfandegária postal** (carimbada
  na origem, checada na fronteira, imutável em trânsito) = o envelope na fonte;
  **tokens de capability OAuth/OIDC** (scopes restringem o que o token PODE FAZER, =
  data-flow capabilities do CaMeL).

## Operação

| carta | operação | por quê |
|---|---|---|
| **TAINT-ENVELOPE** (metadado não-forjável harness-injetado) | **mantida** — o núcleo | o worker não pode forjar; é o único jeito num modelo de subprocess+JSON |
| **TAINT-SINK** (estender o secret-scan pra checar taint_map, fail-closed) | **mantida** | reusa o seam que já é meio-taint; zero subsistema paralelo |
| **CaMeL control-plane-only** (trust-tiers+GM-3 como capabilities) | **mantida** | pega o valor do CaMeL sem o runtime pesado |
| **break-glass rate-limited + rollback + checker-fail-closed** | **dividida (regras de robustez)** | w-002/w-003; entram no spec |
| **IFC runtime por-valor / dynamic taint de bytecode** | **rejeitada** | pesado demais; a fronteira de I/O é onde o taint vive |

## Buildável vs owner-gated

- **Buildável (medição):** um probe measure-only — "quantos valores tainted
  ALCANÇARIAM um sink de egresso hoje?" — reusando o secret-scan (measure-before-
  control, como o truth-divergence probe). Zero enforcement.
- **Owner-gated (segurança):** o enforcement fail-closed no egresso é um CONTROLE de
  segurança + defense-in-depth → owner-gated + merece security review (como o
  N-SCANNER-FP). O desenho está pronto; o probe measure-only é o 1º passo.

## Rastreabilidade

| Evidência | Ideia | Experimento | Task | Status |
|---|---|---|---|---|
| 5/5 (envelope não-forjável) + email X-Header/MTA (w-005) | TAINT-ENVELOPE + TAINT-SINK | probe measure-only (would-block count) | RD-TAINT→taint | desenhado; probe buildável, enforcement owner-gated |
| 5/5 (teto laundering) | limite declarado | — | — | defense-in-depth, não prova |
