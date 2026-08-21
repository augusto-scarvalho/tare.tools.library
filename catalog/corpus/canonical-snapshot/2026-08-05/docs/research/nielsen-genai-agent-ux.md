# Heurísticas de Nielsen × UX de IA Generativa e Agentes (round 2026-07-13)

Owner ask: rodada em background — divergência nos modelos simples (Gemini
free tier), crítica nos modelos inteligentes da NVIDIA Build (glm-5.2 /
nemotron-ultra / step-flash, prospectados em `nvidia-smart-models.md`).

## Pergunta

Como as 10 heurísticas de usabilidade de Nielsen se **traduzem, quebram ou
se estendem** quando a interface inclui IA generativa (saída não
determinística, incerteza, geração aberta) e agentes (ações autônomas em
nome do usuário, supervisão humana, HITL)? Que heurísticas novas ou
reformuladas o harness deveria adotar nos seus painéis de supervisão
(SPEC-114) e no chat operator?

## Critérios de sucesso

1. Cada heurística candidata mapeia explicitamente para uma heurística de
   Nielsen (mantida / reformulada / nova), com o PORQUÊ da mudança.
2. Cada claim normativo carrega fonte + data + classe de confiança
   (`forte…promocional`); sem fonte verificável → `referência: judgment`.
3. Pelo menos 3 candidatas acionáveis no harness (painel/chat/escalações),
   com anti-padrão correspondente.
4. Novidade e maturidade pontuadas em eixos separados (playbook princípio 2).

## Orçamento declarado

- Onda 1 (divergência, 5 ideadores, `gemini-compat` / gemini-2.5-flash-lite,
  free tier interativo — sem batch, ver `nvidia-smart-models.md` §A): ≤30k
  tokens estimados (packet-only: workers HTTP não leem o repo).
- Onda 2 (crítica seedada, 4 críticos, `nvidia-compat`: validity/architecture
  → glm-5.2, cost → step-3.7-flash, security → nemotron-3-ultra): ≤30k tokens
  (~4-6 créditos NVIDIA).
- Gate de 60%: sem onda 3 salvo sinal forte + folga.

## Evidência âncora (Fase 1, Flow A — 2026-07-13)

| claim | source | type | year | confiança |
|---|---|---|---|---|
| As 10 heurísticas seguem canônicas e ativamente mantidas pela NN/g | nngroup.com/articles (Ten Usability Heuristics) | docs | 2024+ | forte |
| Análise dedicada das heurísticas para agentes GenAI existe (Agent Experience) | Goldenberg & Goldenberg, researchgate 392368707 | paper | 2025 | moderada (não peer-review confirmado) |
| Princípios de design para aplicações GenAI (IBM) formalizados | arXiv:2401.14484 | paper | 2024 | forte |
| Heurísticas aumentadas para computer-use agents propostas | arXiv:2605.02729 | paper | 2026 | preliminar |
| Avaliação heurística sintética (IA avaliadora) comparada a humana | arXiv:2507.02306 | paper | 2025 | preliminar |

## Fases 3-4 (preenchido pelo orquestrador ao coletar as ondas)

- Wave 1 (ABORTADA, lição de processo): `WF-20260713-122514-240276` — 2 falhas
  compostas: (a) Gemini free tier em episódio 503 (sonda de saúde recuperou em
  ~4min; 3 retries queimaram os maxRounds); (b) **todos os 4 resultados vieram
  ocos (0 findings)** — causa raiz: a regra do packet "scope sem material →
  done com findings vazios" (correta para análise de código) instrui a saída
  preguiçosa em briefs de conhecimento puro, que não têm arquivos em escopo.
  Fix: onda nova com override explícito no brief (tarefa = GERAÇÃO; 4-8
  findings `category: concept` obrigatórios; vazio = falha). Follow-up de
  harness anotado: perfil de divergência knowledge-domain merece um packet
  próprio sem a regra de escopo-vazio.
- Wave 1b: `WF-20260713-123540-504689` — o override do brief FUNCIONOU
  (worker-001/simplicidade: 5 findings reais), mas o Gemini free tier entrou
  em throttle sustentado (sonda de 25min: maioria 429, 503/200 intermitentes
  — as próprias tentativas comeram o RPM). 1 resultado válido aproveitado.
- Wave 1c: `WF-20260713-130602-119672` — divergência movida pra
  `nvidia-compat` (outage do provedor barato). DESVIO REGISTRADO: branches
  de perfil `plan` roteiam pra glm-5.2 (ideação em modelo smart, não cheap);
  mitigação da regra "gerador nunca é o único avaliador": críticos em
  nemotron-ultra (security) + step-flash (cost) + síntese pelo orquestrador
  (Fable), e o resultado gemini da 1b entra na síntese (sangue cross-provider).
- Wave 2 (crítica): `WF-20260713-131740-274585` — 4/4 críticos entregaram
  (validity/architecture no glm-5.2, cost no step-3.7-flash, security no
  nemotron-3-ultra). O reduce invalidou os 4 pela régua code-oriented
  (`sourceFilesVerified` exigido em findings high) — mesma família do bug do
  escopo-vazio; síntese feita pelo orquestrador direto dos WORKER_RESULTs.

## Síntese (orquestrador, 2026-07-13)

Fontes: 25 conceitos de 4 ideadores GLM (waves 1c) + 5 do ideador Gemini
(wave 1b) + 23 findings de 4 críticos. Convergência forte: 4/4 ideadores
independentes propuseram variações de "visibilidade de estado probabilístico"
e "aprovação em camadas por reversibilidade" — sinal de robustez (nominal
groups). Ressalva dos críticos, aceita: as referências das candidatas são
majoritariamente `judgment` (o seed digest comprime evidence; e os workers
HTTP não acessam web) — as âncoras bibliográficas da Fase 1 sustentam o
mapeamento a Nielsen, não as candidatas individualmente.

### Portfólio (operações por card)

**Núcleo** (adotar nos painéis SPEC-114 / chat operator):
1. `H-visibilidade-probabilistica` (reformula Nielsen #1) — estado do sistema
   inclui incerteza + fonte, com CALIBRAÇÃO explícita (crítico security:
   confiança não-calibrada gera falsa confiança). Ops: reformulada.
2. `H-aprovacao-por-reversibilidade` (reformula #3+#5; merge de 3 candidatas
   sobrepostas apontado pelo crítico validity) — granularidade de aprovação
   proporcional à irreversibilidade da ação; anti-padrão: diálogo constante.
   Ops: combinada.
3. `H-auditoria-persistente` (reformula #6, reconhecimento>recordação) — o
   harness JÁ TEM o records ledger; a heurística é expô-lo como timeline de
   supervisão. Ops: mantida (baixo custo, infra existente).
4. `H-custo-visivel` (nova, deriva #1) — crítico cost pediu telemetria "não
   existente"; ela EXISTE no harness (cost ledger R26) — o crítico não vê o
   repo (packet sem escopo, limitação registrada). Ops: mantida.
5. `H-carga-calibrada-por-severidade` (nova, #6+#8; análogo EHR) — alertas de
   fronteira separados do ruído operacional (painel já agrupa por tier).
   Ops: mantida.
6. `H-consistencia-de-template` (reformula #4) — voz/formato estáveis sobre
   conteúdo variável. Ops: mantida.

**Contingência**: `H-presets-de-autonomia` (depende de classificação de dados
confiável — crítico security); `H-validacao-de-fronteira` (consentimento de
dados pré-envio; parcialmente coberto pelo classify_command HITL).

**Experimentos** (template hipótese/baseline/métricas no doc antes de adotar):
`H-emergency-stop-com-revogacao` (1 blocker de custo do crítico cost;
mecanismo de revogação não especificado — hipótese: suspender + revogar sem
perda de contexto; baseline: taskkill atual; métrica: tempo-até-parada e
integridade pós-parada); `H-undo-semantico-checkpoint` (exige estado
transacional; rollback externo infeasível → compensating transactions).

**Já-produção (mantidas, reconhecidas no harness)**: circuit breaker com
cooldown (safe-action breaker) — a analogia financeira do ideador descreve o
que o SPEC-109 já faz; validação de saída pré-commit (gates SDD).

**Rejeitadas**: rollback granular de superfícies externas como heurística
standalone (crítico security: infeasível; vira parte do experimento de
compensating transactions).

### Follow-ups de harness desta rodada (processo, não tema)

1. **Perfis knowledge-domain**: a regra "scope vazio → findings vazios" e o
   lint "sourceFilesVerified em findings high" são code-oriented e invalidam
   rodadas de conhecimento (3 ocorrências hoje). Candidato: flag de perfil
   `knowledgeDomain: true` que troca as duas réguas.
2. **Seed digest comprime evidence** — críticos de validade não veem as
   referências dos conceitos; carregar evidence no seed (cap por item).
3. Gemini free tier: 429/503 sob rajada mesmo a concorrência 1; sonda de
   saúde + resume funcionou (recuperou 3 workers), mas o RPM é frágil de
   manhã — preferir NVIDIA p/ ondas >3 workers no free tier.

### Rastreabilidade

Evidência (Fase 1, 5 âncoras) → Problema (supervisão de agentes viola/estende
Nielsen) → Ideias (30 conceitos, genealogia por workerRole/wave nos WFs) →
Crítica (23 findings, 4 modelos) → Portfólio acima → Próximo: intake SPEC-116
das heurísticas núcleo no backlog do painel (decisão do dono).
