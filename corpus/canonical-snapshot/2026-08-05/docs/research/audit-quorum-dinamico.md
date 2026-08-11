# Research round — audit-quorum-dinamico

Owner-requested (2026-08-03, in-session): decisão (b) do `plan-audit-gate-leg.md` —
schema do VERDICT + quorum — foi julgada "não é tão simples" e mandada para research.
Cohorts FIXADOS pelo owner: geração 2× sonnet-5 high + 2× GLM-5.2 (nvidia free);
crítica INVERTIDA entre cohorts (GLM critica material sonnet e vice-versa).

## Phase 0 — Question, criteria, budget, design

**Question.** Como dimensionar dinamicamente N (número de seats de auditoria) e a
regra de quorum da perna `audit` do commit-join (gate ‖ reckon ‖ mutate ‖ audit),
em função da complexidade/tamanho/risco da demanda, com o overseer como PARTICIPANTE
que pode concordar ou discordar da auditoria (arbitragem como parte do modelo), a
custo controlado e fuel-aware?

**Success criteria** (o que uma boa resposta satisfaz):
1. Uma função N(sinais) concreta e determinística usando APENAS sinais já computáveis
   do índice staged (risk profile(s), reach do `gate_affected`, tamanho do diff) —
   sem passo de classificação humana no caminho do commit.
2. Regra de quorum definida para CADA N alcançável (o que é split, quem desempata,
   semântica do overseer-como-participante vs o fallback manual `audit record`).
3. Bandas de custo por configuração (tokens/latência), com degradação explícita
   quando um vendor está sem gás (fuel-aware).
4. Compatível com o desenho já decidido da perna: fingerprint-keyed, `verify-status`,
   `audit waive --reason`, seats via perfil `review`, config em `.harness/audit-policy.json`.
5. Toda recomendação normativa carrega `claim → fonte + data + classe de confiança`;
   alimenta a decisão (b) E o item dependente `audit-seat-sizing` (não desenhar sizing
   duas vezes).

**Declared budget.** Round max 160k planned tokens (develop ≤ 80k, refine ≤ 80k,
stop-ratio 0.6). Justificativa: 8 workers × ~12.1k required-reads calibrados + packets
+ reduces; 1 onda de divergência + 1 de crítica, sem ondas 2-3 salvo sinal forte.

**Declared width.** 4 + 4, modo custom — NÃO é o default D010 focused (1-2): o owner
FIXOU o fan-out (2 sonnet + 2 GLM por fase) para obter o sinal de desacordo
cross-vendor que pegou defeitos reais no gauntlet P6 e na auditoria dupla de hoje
(audit-dlm2m3-close: duas lentes independentes convergiram no mesmo finding). A
heterogeneidade é o objeto de estudo além de método (arXiv:2502.08788: MAD é
sobrevalorizado quando a heterogeneidade é ignorada).

**Declared experiment design.** Card `matched-budget` (docs/EXPERIMENT_METHODS.md):
a rodada produz uma política candidata de N(sinais)+quorum cujo ajuste fino virá de
um bakeoff advice-only a custo pareado (previsto como RF.1 no body do
`audit-seat-sizing`). Medível: taxa de defeito-pego por custo, por configuração.

## Phase 1 — Evidence register

`claim | source | type | year | method | limitations | confiança | maturidade`

- [repo] Duas lentes sonnet-5 high independentes convergiram no MESMO finding único
  (escopo do store no packet) e nenhuma achou defeito no código em si |
  `.harness/handoff/audit-dlm2m3-close-s{1,2}-VERDICT.md` | measurement | 2026-08-03 |
  auditoria dupla real | n=1 rodada | forte | produção.
- [repo] O padrão manual de 2 seats (opus5+sonnet5; terra+fable) pegou defeitos reais
  em 5/5 camadas do arco defect-ledger ("a fresh-eyes audit caught a real bug in 5/5
  layers") | `.harness/handoff/brief-defect-ledger-enforcement.md` §6 | measurement |
  2026-08-01 | histórico de auditorias do arco | seleção enviesada (só arcos auditados) |
  moderada | produção.
- [repo] Ciclo BLOCK→fix→re-audit com o MESMO seat convergiu (quorum de re-audit
  por-cohort) | `.harness/handoff/audit-p6s4-terra-refix-*-VERDICT.md` | measurement |
  2026-08-02 | gauntlet P6 | um vendor só | moderada | protótipo.
- [repo] O reckon (SPEC-157) prova que uma perna fingerprint-keyed com verdict humano
  único já segura o join sem custo de seats | `scripts/harness_lib/validation_stamp.py`
  `check_reckon`/`stamp_reckon` | repo | 2026-07 | código em produção | não é auditoria
  multi-seat | forte | produção.
- [repo] Sinais mecânicos disponíveis no staged: risk profile(s) via `required_profile`,
  reach via `reckon_reach` (223/223 no commit de hoje — reach alto NÃO implica revisão
  profunda quando o diff é test-only), diff via numstat | `validation_stamp.py:169/:338` |
  repo | 2026-08 | — | reach superestima em superfícies test-only | forte | produção.
- [web] Debate multi-agente melhora factualidade vs single-agent | Du et al. 2023
  (ICML 2024), composable-models.github.io/llm_debate | paper | 2023 | benchmarks de
  factualidade | tarefas ≠ code review | moderada | validado.
- [web] MAD é sobrevalorizado quando heterogeneidade de modelos é ignorada — o ganho
  vem da HETEROGENEIDADE, não do debate em si | arXiv:2502.08788 | paper | 2025 |
  ablations | benchmarks acadêmicos | moderada | validado.
- [web] LLMs não se auto-corrigem confiavelmente sem sinal externo — crítica precisa
  de verificação reproduzível, não de mais rodadas do mesmo modelo | Huang et al.,
  ICLR 2024, arXiv:2310.01798 | paper | 2024 | ablations | — | forte | validado.
- [web] Acoplamento estrutural colapsa diversidade de ideias → geração independente
  antes de exposição (fundamenta a crítica invertida) | arXiv:2604.18005 | paper |
  2026 | — | — | moderada | validado.
- [judgment] Overseer-como-seat cria conflito de interesse (ele é o autor do brief que
  a auditoria julga); overseer-como-ÁRBITRO pós-verdicts preserva independência dos
  seats e é o que `audit record` já implementa | referência: judgment | — | — | — |
  opinião | conceitual.

## Phase 2 — Define (briefs)

**B1 — política de quorum dinâmico para a perna de auditoria.**
Problema (não tech-shaped): olhares fixos custam demais em demanda trivial e não
escalam confiança em demanda arriscada; como calibrar quantos olhares independentes
uma mudança merece, e como transformar opiniões possivelmente divergentes numa decisão
de commit auditável — incluindo a voz do responsável pela integração?
Atores: overseer (integra e arbitra), seats de auditoria (independentes), owner
(política), a perna `check_audit` (consome o veredito).
Constraints: sinais só do índice staged; zero fricção abaixo do piso de trivialidade;
custo fuel-aware; verdicts tipados SHIP|BLOCK com findings file:line; o resultado é
uma POLÍTICA em `.harness/audit-policy.json`, não código novo de consenso.
Success criteria: os 5 do Phase 0.

**Human gate:** exigido pelo processo; SATISFEITO em conversa — o owner desenhou a
rodada (2026-08-03): cohorts fixados, crítica invertida, "tá bom assim". A porta de
DELIVER continua humana: `research round approve`.

## Phase 3/4 — compiled by `research round audit-quorum-dinamico compile|advance`

```json
{
  "schemaVersion": "1.0",
  "slug": "audit-quorum-dinamico",
  "question": "Como dimensionar dinamicamente N seats e a regra de quorum da perna audit do commit-join, com overseer-participante e custo fuel-aware, a partir de sinais do indice staged?",
  "successCriteria": [
    "funcao N(sinais) deterministica sobre risk profile + reach + diff size, sem classificacao humana",
    "regra de quorum e semantica de split/arbitragem definida para cada N alcancavel",
    "bandas de custo por configuracao com degradacao fuel-aware",
    "compativel com fingerprint-keyed record, verify-status, audit waive e seats via perfil review",
    "claims normativos com fonte+data+confianca; alimenta decisao (b) e audit-seat-sizing"
  ],
  "experimentDesign": {
    "card": "matched-budget",
    "why": "a politica candidata sera calibrada por bakeoff advice-only a custo pareado (RF.1 do audit-seat-sizing); a rodada define o desenho, o experimento mede defeito-pego por custo"
  },
  "budget": {"roundMaxPlannedTokens": 160000, "developStopRatio": 0.6},
  "discover": {"flows": ["repo", "web"], "evidenceSection": "Phase 1 — Evidence register"},
  "define": {
    "briefs": [
      {
        "id": "B1",
        "problem": "olhares fixos custam demais em demanda trivial e nao escalam confianca em demanda arriscada; calibrar quantos olhares independentes uma mudanca merece e como divergencia vira decisao de commit auditavel, incluindo a voz do integrador",
        "actors": ["overseer-arbitro", "seats-de-auditoria", "owner-politica", "check_audit"],
        "constraints": [
          "sinais apenas do indice staged",
          "zero friccao abaixo do piso de trivialidade",
          "custo fuel-aware",
          "verdict tipado SHIP|BLOCK com findings file:line",
          "resultado e politica em .harness/audit-policy.json, nao motor de consenso novo"
        ],
        "successCriteria": ["os cinco criterios do Phase 0"]
      }
    ],
    "humanApprovalRequired": true
  },
  "develop": {
    "profile": "research-divergence",
    "briefs": ["B1"],
    "width": {"mode": "custom", "count": 4, "why": "owner-fixed 2026-08-03: 2x sonnet-5 high + 2x GLM-5.2 para sinal de desacordo cross-vendor; heterogeneidade e objeto de estudo (arXiv:2502.08788)"},
    "budget": {"maxPlannedTokens": 80000},
    "assignment": "zip",
    "fleet": [
      {"id": "sonnet", "executor": "claude", "model": "sonnet", "effort": "high", "count": 2},
      {"id": "glm", "executor": "nvidia-compat", "model": "z-ai/glm-5.2", "effort": "high", "count": 2}
    ],
    "perspectives": [
      {"id": "custo-beneficio", "taskProfile": "plan", "title": "Contribuicao marginal de cada seat extra: bandas de custo, ponto de retorno decrescente, degradacao fuel-aware"},
      {"id": "confiabilidade-arbitragem", "taskProfile": "plan", "title": "Regras de quorum sob N variavel: split, desempate, overseer-participante vs arbitro, erros correlacionados entre seats do mesmo vendor"},
      {"id": "sinais-mecanicos", "taskProfile": "plan", "title": "N(sinais) deterministico a partir do indice staged: risk profile, reach gate_affected, diff size; escada de thresholds e casos degenerados (reach 223/223 test-only)"},
      {"id": "analogia-cross-domain", "taskProfile": "plan", "title": "Transferencia: code review humano (Google/SmartBear), redundancia aeronautica, amostragem de aceitacao (QC estatistico), quoruns bizantinos — o que sobrevive ao contexto de commit-gate?"}
    ]
  },
  "refine": {
    "profile": "research-critique",
    "width": {"mode": "custom", "count": 4, "why": "critica invertida owner-fixed: GLM critica material sonnet e vice-versa; excludeSameExecutor garante a inversao"},
    "budget": {"maxPlannedTokens": 80000},
    "assignment": "zip",
    "fleet": [
      {"id": "glm-critic", "executor": "nvidia-compat", "model": "z-ai/glm-5.2", "effort": "high", "count": 2},
      {"id": "sonnet-critic", "executor": "claude", "model": "sonnet", "effort": "high", "count": 2}
    ],
    "lenses": [
      {"id": "validade-evidencia", "taskProfile": "review", "title": "Validade e referencias do material sonnet"},
      {"id": "custo-operacao", "taskProfile": "scan", "title": "Custo/operacao do material sonnet"},
      {"id": "arquitetura-integracao", "taskProfile": "review", "title": "Arquitetura/integracao do material GLM na perna audit"},
      {"id": "risco-seguranca", "taskProfile": "security", "title": "Risco/seguranca do material GLM (gaming do quorum, seat comprometido, waive abuse)"}
    ],
    "seedPolicy": {"mode": "cross-vendor", "coverage": "balanced", "excludeSameExecutor": true, "maxFindingsPerSource": 12}
  },
  "deliver": {
    "requireOneOperationPerConcept": true,
    "requireExactlyOnePortfolioBucket": true,
    "autoPromote": false
  }
}
```

## Phase 5 — Deliver

Waves: develop `WF-20260803-060425-620300` (reduce: 15 findings, 0 blockers),
refine `WF-20260803-061139-064720` (reduce: 14 findings, 0 blockers, 4/4 críticos
válidos após retry — 2 falhas de CONTRATO de resultado na 1ª passada, classe
`wr-schema-discards-work`; gap de retomada do advance registrado no board como
`research-round-advance-nao-recupera-coho`).

### Operações por concept card

- **C1 — Escada N(sinais) por BANDAS** (ideator sinais-mecanicos + crítica arquitetura):
  **simplificada** — a fórmula de soma ponderada cai (crítica: `required_profile()` devolve
  um SET de nomes, não um escalar de risco; `reachWeight` indefinido no caso fail-open
  `None` de `reckon_reach`). Vira tabela determinística de bandas em `.harness/audit-policy.json`:
  N=0 (n/a) abaixo do piso; N=1 superfície de risco pequena; N=2 default de risco;
  N=3 diff grande/reach alto (excluído test-only). Sinais: `reckon_required`,
  numstat, changedFiles, affectedScenarios.
- **C2 — Tabela de quorum por N** (ideator confiabilidade): **mantida** — N=1: SHIP fecha,
  BLOCK → fix ou arbitragem; N=2: unanimidade pra SHIP, qualquer BLOCK bloqueia;
  N=3: qualquer BLOCK com finding blocker bloqueia (nunca maioria simples sobre blocker);
  split sempre nomeia o seat dissidente no registro.
- **C3 — Overseer é ÁRBITRO pós-verdict, nunca seat**: **mantida** — `audit collect`
  computa o veredito ANTES do overseer ver os VERDICTs; discordância do overseer =
  `audit record` (override tipado, ator SPEC-161, nunca auto-rescued). Responde a
  direção do owner: concordar/discordar existe, como override registrado — não voto.
  (Crítica derrubou o BFT do ideator analogia que fazia do overseer um nó não-confiável.)
- **C4 — Diversidade de vendor obrigatória quando N≥2**: **combinada** com C1 — a decisão
  interina (d) sozinha reproduz o blind-spot same-vendor que a própria evidência da rodada
  flagou (2 sonnet convergindo no mesmo finding). N≥2 ⇒ seats de ≥2 executors (ídiom
  cross-vendor da rule 7 do research_round); indisponibilidade vira fallback single-vendor
  REGISTRADO.
- **C5 — Degradação fuel-aware reusa SPEC-165 R13** (gas_balance/_gas_pcts): **mantida** —
  nada de lógica nova; cair abaixo do N planejado é REGISTRADO (ídiom do reckon override).
- **C6 — Campo `dissent` no ledger mesmo em SHIP resolvido**: **mantida** — é o que torna
  o bakeoff custo×defeito-pego do RF.1 mensurável.
- **C7 — Quorum bizantino formal**: **estacionada** — backbone conceitual só; a crítica de
  segurança mostrou que assume seats honestos/independentes e que o `f` derivado de sinais
  do staged é influenciável pelo próprio autor do diff.
- **C8 — Amostragem de aceitação (QC) como heurística de sample-size**: **adiada** —
  entra como desenho do bakeoff RF.1 dentro de `audit-seat-sizing`.
- **C9 — "reach 223/223 test-only ⇒ Nmax + supermajority"** (ideator sinais-mecanicos):
  **rejeitada** — contradiz a evidência do repo (commit de hoje: reach 223/223 com diff
  test-only é o caso DEGENERADO de superestimação; escalação por reach EXCLUI test-only).
- **C10 — Anti-gaming dos sinais** (crítica segurança: sinais influenciáveis pelo diff
  auditado; salami-slicing pra ficar sob o piso): **adiada** — risco real, mitigação
  mínima agora (piso por fingerprint deixa fatiamento visível no ledger); hardening
  dedicado quando a perna existir.

### Portfolio

- **núcleo**: C1, C2, C3, C4, C5, C6 — juntos são a resposta da decisão (b).
- **contingência**: fallback single-vendor registrado (C4) quando só um vendor tem gás.
- **aposta-de-fronteira**: —
- **experimentos**: RF.1 bakeoff matched-budget (custo×defeito-pego por configuração);
  registro formal via `experiment add` acontece quando `audit-seat-sizing` abrir (dono
  do bakeoff), citando esta rodada.
- **estacionadas**: C7, C8.
- **rejeitadas**: C9; fórmula de soma ponderada (shape errado dos sinais); overseer-como-
  seat/nó-BFT; Nmax 7-9 (desancorado do precedente manual — o teto interino é 3).

### Experimento (RF.1, design declarado)

`hipótese`: a escada C1 com quorum C2 pega ≥ os defeitos do fixo N=2 a custo médio menor.
`baseline`: N=2 unanimidade (precedente manual). `métricas`: defeitos-pegos/rodada,
custo/rodada (tokens+USD), taxa de split. `critérios de decisão`: adotar escada se
custo cai ≥20% sem perda de detecção em ~10 audits reais; senão manter N=2 fixo.

### Rastreabilidade (Evidência → … → Status)

| Evidência | Problema | Ideia | Experimento/ADR | Spec/Task | Status |
|---|---|---|---|---|---|
| VERDICTs dlm2m3 s1/s2 (convergência same-vendor) | blind-spot de vendor | C4 diversidade N≥2 | — | decisão (b) do plan-audit-gate-leg | núcleo |
| brief-defect-ledger §6 (2 seats, 5/5 camadas) | quantos olhares | C1 escada + teto 3 | RF.1 | plan-audit-gate-leg + audit-seat-sizing | núcleo |
| validation_stamp reckon/override idiom | como registrar degradação/dissenso | C5, C6 | — | decisão (b) | núcleo |
| arXiv:2502.08788 + Diversity Collapse | heterogeneidade > contagem | C4; crítica invertida | — | — | aplicado |
| Huang ICLR 2024 (sem auto-correção) | crítica precisa de sinal externo | C3 árbitro registrado | — | decisão (b) | núcleo |
| reach 223/223 test-only (commit ba21da3) | sinal degenerado | C9 rejeitada; exclusão test-only em C1 | — | decisão (b) | rejeitada/absorvida |
| custo do crítico descartado (USD 0.98, contrato) | seats falham por contrato | robustez do collect a seat inválido (re-spawn 1x, depois N-1 registrado) | — | plan-audit-gate-leg | núcleo (nota) |

### Decisão proposta para (b) — aguarda `research round approve` (porta humana)

VERDICT schema: como no draft do brief (1ª linha `VERDICT: SHIP|BLOCK`; findings
`F<n> — severity — file:line — evidence`; BLOCK sem finding é refused no collect).
Quorum: escada C1 (0/1/2/3, bandas versionadas em audit-policy.json, teto interino 3),
regra C2 por N, diversidade C4 quando N≥2, degradação C5 registrada, dissent C6 no
ledger, overseer-árbitro C3 via `audit record`. Após approve: amendment na seção (b)
de `.harness/handoff/plan-audit-gate-leg.md` e o brief destrava a implementação.

<!-- round-state:start -->
```json
{
  "cohorts": [
    {
      "cohortId": "develop-sonnet",
      "phase": "develop",
      "declaredExecutor": "claude",
      "executor": "claude",
      "model": "sonnet",
      "wfid": "WF-20260803-060425-620300",
      "status": "done"
    },
    {
      "cohortId": "develop-glm",
      "phase": "develop",
      "declaredExecutor": "nvidia-compat",
      "executor": "nvidia-compat",
      "model": "z-ai/glm-5.2",
      "wfid": "WF-20260803-060425-620300",
      "status": "done"
    },
    {
      "cohortId": "refine-glm-critic",
      "phase": "refine",
      "declaredExecutor": "nvidia-compat",
      "executor": "nvidia-compat",
      "model": "z-ai/glm-5.2",
      "wfid": "WF-20260803-061139-064720",
      "status": "done",
      "seed": "WF-20260803-060425-620300",
      "sourceCohortId": "develop-sonnet",
      "workerExecutors": {
        "worker-001": "nvidia-compat",
        "worker-002": "nvidia-compat"
      },
      "minSuccessConfigured": 2,
      "minSuccessEffective": 2,
      "successes": 2,
      "minSuccessMet": true
    },
    {
      "cohortId": "refine-sonnet-critic",
      "phase": "refine",
      "declaredExecutor": "claude",
      "executor": "claude",
      "model": "sonnet",
      "wfid": "WF-20260803-061139-064720",
      "status": "done",
      "seed": "WF-20260803-060425-620300",
      "sourceCohortId": "develop-glm",
      "workerExecutors": {
        "worker-003": "claude",
        "worker-004": "claude"
      },
      "minSuccessConfigured": 2,
      "minSuccessEffective": 2,
      "successes": 2,
      "minSuccessMet": true
    }
  ],
  "deliver": {
    "approvedBy": "human",
    "at": "2026-08-03T10:19:44.195203+00:00",
    "note": "Owner aprovou em sessao (2026-08-03): escada N 0-3 por bandas em audit-policy.json (teto interino 3), unanimidade pra SHIP, qualquer BLOCK blocker bloqueia, diversidade de vendor obrigatoria N>=2 com fallback single-vendor registrado, degradacao fuel via R13 registrada, dissent no ledger, overseer-arbitro via audit record. RF.1 matched-budget calibra as bandas no audit-seat-sizing.",
    "checks": {
      "stateComplete": true,
      "sections": {
        "operations": true,
        "portfolio": true,
        "experiment": true,
        "traceability": true
      }
    }
  }
}
```
<!-- round-state:end -->
