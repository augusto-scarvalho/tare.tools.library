# Weekly monitor W28 (memória/contexto) — extrato para o harness

Fonte: digest semanal GPT fornecido pelo dono (2026-07-13). NÃO é uma rodada
de research (ordem do dono: não rodar o skill); citações são `[web]`
não-verificadas — as ideias abaixo foram avaliadas pelo mérito interno contra
o estado real do harness. Se um experimento graduar, a rodada de verificação
de fontes acontece aí.

## Onde o harness JÁ está à frente do digest (sem trabalho novo)

| Achado do digest | Equivalente já operante aqui |
|---|---|
| #1 Shared Selective Memory (compartilhar specs/schemas/configs/constraints; descartar raciocínio de sessão) | É a arquitetura vigente: `specs/` + `schemas/` + `.harness/routing` versionados em git SÃO o workspace compartilhado; packets embutem exatamente specs/constraints; WORKER_RESULT persiste claim+evidence, nunca CoT |
| #3 FARMA (postura) | Findings high/blocker EXIGEM evidence (validador); escalations/records carregam proveniência; o safe-action breaker limita automação alimentada por findings do próprio modelo |
| #5 SelfMem governado (propose→judge→authorize→commit→feedback) | O self-review loop (SPEC-109) tem exatamente essa forma: findings → escalations → safe-actions bounded → breaker |
| Plataforma: runtime tool search | `catalog` (CE.4): página de nomes = 15% dos helps completos, paging sob demanda |
| #4 owner_scope | A dimensão `subject` (self\|target) atravessa records/escalations/events/calibration desde os rounds de isolamento |

## Experimentos extraídos (reversíveis; template do research-playbook)

### EXP-1 — Truncamento preservador-de-ação (CoACT-inspired) · prioridade ALTA
- **Hipótese**: os compressores de observação do harness (`truncate_text`
  OUTPUT_CAP=8000 do painel/chat, `maxWorkerOutputChars`, `tail_lines`)
  descartam com frequência as linhas decisórias (`fix:`, `next:`, `harness
  error:`, tail de traceback) — a métrica que importa não é taxa de
  compressão e sim "a próxima ação sobrevive?".
- **Baseline**: corpus real já existente (validation-results.jsonl, run-logs
  de workers, saídas de gate) truncado pelas regras atuais.
- **Métrica**: % de amostras em que uma linha decisória presente no bruto
  some no truncado (probe determinístico, zero LLM).
- **Fase 2 (só se a métrica for ruim)**: truncamento tail-e-assinatura-
  preservante em UM seam (`common.truncate_text`), atrás de comparação
  byte-idêntica quando nada casa. **Reversão**: um seam, um revert.

### EXP-2 — Avaliador de invariantes de compactação (Distortion-inspired) · prioridade ALTA
- **Hipótese**: nossas três superfícies de compactação (checkpoint,
  context-digest, handoff) podem perder invariantes decisórios sem ninguém
  notar (o handoff já regenerou acima do budget uma vez; o digest já dropou
  evidence no seed).
- **Baseline**: as superfícies atuais, medidas como estão.
- **Métrica**: checklist determinística pós-reinjeção — item atual, fase,
  comandos de verify, constraints, erros abertos, decisões aprovadas — cada
  um presente/ausente. Vira check advisory no doctor (padrão
  intake-staleness). **Reversão**: check advisory, remove-se uma linha.
- Nota: o token-audit já mede o lado CUSTO do digest; isto mede o lado
  DISTORÇÃO — as duas metades do achado #2.

### EXP-3 — Portão de evidência na promoção (FARMA-lite) · prioridade MÉDIA/segurança
- **Hipótese**: o único caminho onde racionalização de modelo vira estado
  acionável sem evidence obrigatória é reduce→`workflow promote`
  (recommendations viram tasks).
- **Baseline**: promotes atuais (auditar quantos carregam evidence handles).
- **Métrica/fase 2**: tasks promovidas sem evidence ganham
  `quarantined: true` até verificação (o vocabulário do intake/escalations
  já tem o padrão). **Reversão**: flag aditiva, ignorável.

## Estacionados (com gatilho explícito)

- **#4 Contextual Integrity completo** (purpose_scope/allowed_roles/retention):
  gatilho = o harness virar multi-tenant/SaaS. Hoje é single-owner; `subject`
  cobre o isolamento existente.
- **#7 Testbed bounded-memory** (matriz full-trace/window/state/episodic):
  o lado custo já existe (requiredReads with/without digest); o lado
  comportamento custa tokens de modelo — gatilho = orçamento dedicado de
  avaliação.
- **#8 Reward de política de retenção**: o `delegations.byOutcome` de hoje é
  a semente exata do reward proposto; gatilho = fase de aprendizado do
  harness (mesma família do SELF_EVOLUTION I4, Deferred).
- **Plataforma: compaction nativa por vendor** atrás de interface comum:
  gatilho = engines chat expondo compaction de API; hoje o /compact do
  vendor CLI cobre.

## Veredito crítico do digest

Direção geral compatível com o que os nossos próprios rounds (memory G2/G3)
já apontavam — reforço, não novidade estrutural. O insight realmente
acionável e barato é o par EXP-1+EXP-2: medir compressão pelo efeito na
próxima ação/decisão em vez de por tokens. O alerta FARMA merece o EXP-3
mas a postura base já é boa. Nada aqui justifica mudança arquitetural antes
das medições.
