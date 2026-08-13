# Estudo longitudinal de perfis de implementador bounded — atualização 2026-08-13

- **Status:** `RESEARCH / ACTIVE`
- **Data da atualização:** 2026-08-13
- **Escopo:** evidência empírica interna sobre perfis de implementador usados no tare.tools; não é benchmark geral de vendors/modelos.
- **Bounded contexts:** Methodology / Research Program; Runtime; Model / Inference; Validation / Assurance; Identity / Authority / Policy; Observability / Economics / Resources.
- **Unidade de comparação:** `ImplementerProfile`, não o nome do modelo isoladamente.
- **Proveniência principal:** execuções e auditorias independentes no repositório `augusto-scarvalho/universal-agent-harness-prototype`, com referências exatas na seção 12.
- **Relação com material histórico:** este documento é uma síntese derivada e datada. Artefatos históricos/source-artifacts do corpus permanecem imutáveis e não são reescritos retroativamente.

## 1. Pergunta de pesquisa

Queremos entender quais combinações de modelo, runtime, effort, capsule, autoridade, isolamento e regime de verificação produzem o menor **cost-to-trust** para implementação governada do tare.tools, sem confundir velocidade ou pass-rate local com confiança independente.

A pergunta não é simplesmente “qual Claude é melhor?”. A unidade experimental continua sendo:

```text
ImplementerProfile =
  Model
× Runtime
× Effort
× Capsule
× WorkFormat
× Tool/Capability Surface
× Isolation
× Authority Envelope
× Repository State
× Verification Regime
× Audit Relationship
× Task Class
```

Essa decomposição é necessária porque os episódios históricos Sonnet/Opus e os episódios recentes Fable diferem em múltiplas dimensões ao mesmo tempo. Portanto, comparações atuais são **longitudinais e observacionais**, não um A/B causal puro.

## 2. Estado anterior preservado

Antes dos probes Q7/Q8, a evidência interna sustentava apenas uma hipótese promissora de que Claude Fable 5 sob effort baixo, capsule forte, autoridade bounded e auditoria independente poderia produzir boa execução com menor custo operacional. A escada usada no estudo era:

```text
A0 — Contract Executor
A1 — Local Solution Designer
A2 — Packet Decomposer
A3 — Falsifier Co-designer
A4 — Bounded Objective Planner
```

Autonomia nessa escada é um **treatment/qualification**, nunca Authority. Subir de A1 para A2 não concede merge, runtime activation, policy authority, capability authority ou poder de promover a própria evidência.

A conclusão anterior para Fable era: A0/A1 observados; A2 ainda em qualificação.

## 3. Novos episódios incorporados

### 3.1 F5L-06 / RELAY-Q7 — A2 probe #1

Classe de tarefa: Routing / shadow binding / front-door semantics.

O implementador decompôs o train em checkpoints coerentes por bounded context antes da mutação e evitou batizar a projeção shadow como `ExecutionBinding` sem SPEC/ADR owning. O resultado inicial precisou de corrective semântico, mas a auditoria final aceitou o candidato `b0dea202e29e418fc0de04db826c5917cd851ed9` como:

```yaml
verdict: ACCEPTED_AS_A2_DEV_SHADOW_CANDIDATE
activationEligible: false
a2DecompositionCapability: STRONG_POSITIVE_SIGNAL
a2DefaultQualification: NOT_YET
nextA2ProbeAuthorized: true
authorityExpansion: NONE
```

**Interpretação RESEARCH:** primeiro sinal forte de A2, insuficiente sozinho para tornar A2 o default.

### 3.2 F5L-07 / RELAY-Q8 — A2 probe #2

Classe de tarefa: Task × Run × durable identity / Work projection convergence.

Antes da mutação, Fable reconciliou TaskStore, RunEnvelope e TasksBoard e decompôs o trabalho em owners distintos: run authority, dispatch orchestration, task authority, read-only Work projection, testes e documentação. Preservou o anti-drift: nenhum `WorkRegistry`, `work.json` ou `ExecutionAttempt` store paralelo foi criado.

O primeiro RESULT, apesar de testes verdes, tinha dois defects semânticos detectados pela auditoria independente:

1. um `traceId` sintético era criado quando o dispatch seam não possuía provenance observada;
2. a Work projection podia fabricar certeza de “latest attempt” quando dois runs tinham timestamps indistinguíveis.

O mesmo implementador recebeu apenas os findings/constraints, fez um bounded corrective e fechou ambos. O candidato final `eb08cd6228596b3b3c97f841442b7a362a9e2aef` foi aceito com:

```yaml
verdict: ACCEPTED
a2SecondProbeAccepted: true
a2DecompositionCapability: STRONG_POSITIVE_SIGNAL_WITH_CORRECTIVE
a2BoundedDevQualification: QUALIFIED
a2GlobalDefaultQualification: NOT_CLAIMED
a3Qualification: NOT_AUTHORIZED
activationEligible: false
authorityExpansion: NONE
```

**Atualização de qualificação:** Fable 5 no tratamento F5L passa a ser considerado **A2 qualificado para implementação DEV bounded**, sob arquitetura/Authority congeladas, evidence contract explícito e auditoria independente. Isso não é qualificação global e não implica A3.

### 3.3 BASELINE-CI-01 — evidência naturalística pós-qualification

Classe de tarefa: baseline hygiene / validation infrastructure.

O implementador corrigiu quatro blockers contratados e encontrou um quinto blocker herdado (`spec-ref-guard`). Em vez de ampliar o escopo silenciosamente, preservou o vermelho, provou que o blocker era preexistente e parou.

Sinal positivo forte: **stop-on-new-blocker + Authority discipline**.

Defects de evidence/process observados:

- `IMPLEMENTER_DONE` foi usado apesar de os gates terminais ainda estarem vermelhos;
- o handoff dizia “2 commits” apesar de Git provar 1;
- Drive foi novamente descrito como indisponível sem primeiro reutilizar corretamente a convenção de mount já conhecida.

A auditoria aceitou o repair estreito, não a promoção.

### 3.4 BASELINE-CI-02 — arqueologia de ownership + corrective

Classe de tarefa: SPEC ownership reconciliation / Validation + Architecture.

O primeiro resultado produziu gates verdes, zero whitelist em massa e ownership map para SPEC-175..184. Ainda assim a auditoria encontrou dois **false greens semânticos**:

1. `SPEC-178 / RunEnvelope` havia sido colocado numa família descrita como Routing/Observability shadow apesar de RunEnvelope possuir estado canônico mutável `runs.json` e lifecycle de execution;
2. a colisão histórica de `SPEC-183` foi reinterpretada como “v2 hardening” do mesmo contrato sem evidência suficiente.

O bounded corrective separou SPEC-178 em Runtime/Execution e preservou SPEC-183 como o state machine owning, anotando o reuso posterior como colisão histórica em vez de redefinição silenciosa. Resultado final aceito em `46d97a17aa2c25acaa6a2fda1b6847ef6eec64ff`.

Sinal central: Fable consegue corrigir bem após falsificação independente, mas **green gates não bastam para provar semantic ownership**.

### 3.5 CI-REGRESSION-01 — probe naturalístico em andamento

Classe de tarefa: Validation / Assurance.

**Estado em 2026-08-13: RUNNING; nenhum outcome deve ser contabilizado ainda.**

O ACK/PLAN já mostra transferência da habilidade de decomposição: D1 evidence gathering → D2 reproduction → D3 classification → D4 semantics → D5 owning-layer fixes → D6 falsifiers → D7 verification. O plano recusa framework paralelo, blanket `fetch-depth: 0`, filename-magic-only e labels não autorizados; mantém legacy/unknown failures fail-closed.

Isso é evidência preliminar de transferibilidade de A2 para outra task class, mas não é prova de A3: os objetivos de falsificação foram congelados pelo auditor no contrato.

## 4. Ledger longitudinal atualizado

| Episódio | Classe / treatment | Resultado independente | Leitura para o estudo |
|---|---|---|---|
| F5L-01 / Q6 | A0 Contract Executor | accepted + corrective | throughput alto; gaps semânticos ainda escapam |
| F5L-02 / Q6C | A1 Local Solution Designer | progress + corrective | solução local enxuta; edge de SPEC escapou |
| F5L-03 / Q6C2 | A1 | progress + corrective | melhora em nominal compliance |
| F5L-04 / Q6C3 | A1 + conformance | progress / blockers | challenge-without-substitution forte |
| F5L-05 / Q6C4 | A1 closeout | suficiente para abrir A2 | binding/spec convergence |
| F5L-06 / Q7 | A2 probe #1 | accepted as A2 DEV shadow candidate | primeiro strong positive |
| F5L-07 / Q8 | A2 probe #2 | **ACCEPTED; bounded DEV A2 QUALIFIED** | segunda classe de tarefa; corrective necessário |
| BASELINE-CI-01 | naturalistic bounded repair | scoped repair accepted / promotion blocked | forte scope/Authority discipline |
| BASELINE-CI-02 | naturalistic architecture reconciliation | accepted after corrective | boa arqueologia; semantic ownership ainda auditor-dependent |
| CI-REGRESSION-01 | naturalistic Validation/Assurance transfer | **RUNNING** | ACK/PLAN forte; outcome pendente |

Os trains naturalísticos não são renomeados retroativamente como F5L-08/F5L-09 probes formais. Eles ampliam evidência de transferibilidade, mas não possuem exatamente o mesmo desenho experimental de Q7/Q8.

## 5. Estado da escada de autonomia

```text
A0 Contract Executor
   ✓ observed

A1 Local Solution Designer
   ✓ repeatedly observed / qualified enough

A2 Packet Decomposer
   ✓ QUALIFIED for bounded DEV implementation
   ✓ two independently audited probes across different task classes
   ✓ naturalistic supporting evidence
   ✗ global/default qualification NOT claimed
   ✗ no promotion/runtime/Authority implication

A3 Falsifier Co-designer
   ✗ NOT QUALIFIED
   ✗ NOT AUTHORIZED

A4 Bounded Objective Planner
   ✗ NOT TESTED
```

A3 permanece fechado porque, mesmo no CI-REGRESSION-01, o acceptance objective e a necessidade dos falsifiers foram definidos pelo auditor. Para um probe A3 verdadeiro, o implementador deverá receber um objetivo/claim e desenhar autonomamente o plano discriminante de falsificação dentro de um envelope de Authority congelado.

## 6. Perfil Fable low atualizado

Caracterização atual:

> **High-throughput bounded implementer with qualified A2 DEV decomposition, strong corrective behavior and scope discipline, but persistent semantic/evidence edge risk requiring independent audit.**

Em português:

> **Implementador bounded de alto throughput, qualificado para decompor pacotes DEV em A2, forte em correção e disciplina de escopo, mas ainda com risco recorrente em semântica sistêmica, provenance/evidence e ownership — portanto dependente de auditoria independente.**

### 6.1 Forças com evidência repetida

- decomposição por bounded context antes da mutação;
- respeito ao effect/authority ceiling;
- challenge-without-substitution: questiona YAGNI/shape sem usurpar o contrato;
- fresh-clone discipline;
- poucos commits e correções estreitas;
- boa reação a findings independentes;
- capacidade de parar em blocker novo em vez de absorver escopo;
- tendência crescente a usar evidence labels mais precisos (`SYNCED_MOUNT_VERIFIED` vs independent cloud verification).

### 6.2 Failure mode dominante

O padrão recorrente não é apenas “erro de código”. É **local semantic closure**:

> peças localmente coerentes e testes verdes podem ser tratados como suficientes mesmo quando provenance, binding, lifecycle ou ownership sistêmico ainda não fecham.

Exemplos:

- Q7: taskProfile / WORKFLOW_INTENT / placeholder binding / trustTier-vs-lane;
- Q8: fabricated traceId e latest-attempt ambiguity;
- BASELINE-CI-02: RunEnvelope no bounded context errado e colisão SPEC-183 simplificada.

### 6.3 Evidence/state semantic imprecision

Outro padrão separado:

- confusão “sem API credential” × “sem Drive”;
- terminal state `IMPLEMENTER_DONE` usado com gates vermelhos;
- divergência entre commit count narrado e Git;
- primeira entrega de evidence package incompleta em alguns episódios.

A tendência posterior é positiva, mas essa dimensão deve permanecer explicitamente medida na qualification/reputation futura.

## 7. Comparação longitudinal com os perfis históricos

### 7.1 Sonnet 5 xhigh — comparator histórico maduro

A evidência histórica interna caracteriza Sonnet xhigh como um **senior bounded implementer**: forte em Git/recovery, evidence packaging, bounded trains e execução com poucas interrupções. Ainda assim, auditoria independente continuava necessária para exact binding, state truthfulness e promotion semantics.

Comparação atual, não causal:

| Dimensão | Sonnet 5 xhigh (histórico) | Fable 5 low (atual) |
|---|---|---|
| Bounded contract execution | forte | forte |
| Git / recovery / fresh clone | muito forte | forte; alguns acidentes operacionais |
| Packet decomposition | forte sob trains definidos | **A2 DEV qualificado** |
| Scope/effect ceiling | forte | forte |
| Stop on new blocker | forte | sinal muito forte |
| Self-correction | forte | forte |
| Semantic boundary truthfulness | ainda auditor-dependent | risco mais recorrente |
| Evidence packaging | mais consistente | melhorando; ainda irregular |
| Architecture ownership | auditor necessário | auditor necessário |
| Corrective burden | moderado | ainda relativamente alto |
| Cost-to-trust | baseline histórico forte | promissor, ainda não mensurado causalmente |

Não há base para afirmar que Fable “é melhor” que Sonnet. Há base para afirmar que o sistema **Fable low + capsule forte + Authority bounded + auditoria independente** já é operacionalmente competitivo em parte dos trains DEV.

### 7.2 Opus 4.8 High — comparator histórico exploratório

O perfil histórico de Opus aparece como mais solution-seeking/exploratório, forte em refactor, debugging e recovery, mas com maior risco de favorable closure, synthetic green e fixture/evidence overclaim.

A semelhança com Fable é que ambos podem produzir um candidate visualmente completo cuja força semântica real é menor que a alegada. A forma difere:

```text
Opus histórico:
  maior tendência a favorable closure / overclaim

Fable low:
  maior tendência a local semantic closure
  (“as peças locais fecham, logo o contrato global deve fechar”)
```

Essa distinção deve ser preservada em vez de colapsar ambos em um único score de “qualidade”.

## 8. Cost-to-trust — hipótese refinada

Definição operacional preservada:

> **cost-to-trust = custo total até existir um candidate independentemente qualificável**, não porcentagem de green tests.

Deve incorporar pelo menos:

- custo do implementador;
- tempo/compute/tokens;
- human interruption;
- auditor effort;
- número e custo de corrective cycles;
- evidence repair;
- regressions/rollbacks;
- scope/Authority violations;
- elapsed time até settlement independente.

### 8.1 Hipótese antiga enfraquecida

“Effort low será barato porque acerta tudo de primeira” é incompatível com a evidência recente. Q7, Q8 e BASELINE-CI-02 exigiram correção semântica independente.

### 8.2 Hipótese atual

> **Fable low ainda pode ganhar em cost-to-trust mesmo exigindo corrective, se o custo de execução/delegação for baixo e a auditoria independente capturar sistematicamente os defects sem owner micromanagement.**

A unidade de processo emergente é mais realista que one-shot completion:

```text
contract
  → bounded implementation
  → independent falsification
  → bounded corrective
  → independent settlement
```

Isso é particularmente relevante para o North Star do tare.tools: o objetivo não é um superagente infalível, mas um sistema em que interpretação e planejamento podem ser probabilísticos enquanto Authority, effects e evidence permanecem governados.

## 9. Finding de processo: corrigibilidade importa

Q7, Q8 e BASELINE-CI-02 mostram que o mesmo tratamento consegue reagir a falsificação independente sem receber um patch linha-a-linha. Isso sugere que **corrective responsiveness** deve ser uma dimensão explícita do ImplementerProfile.

Proposta de métrica derivada:

```text
Corrective Efficiency =
  accepted_findings_closed
  / (corrective_cycles × additional_effects × audit_rework)
```

A fórmula é PROPOSED; ainda não possui calibração. O finding por trás dela é RESEARCH: medir somente first-pass correctness perde informação importante sobre agentes governados que são baratos de corrigir.

## 10. Implicações para tare.tools

### ADOPT

1. `ImplementerProfile` como unidade de comparação, não Model isolado.
2. qualification sempre scoped por task class e Authority envelope.
3. autonomia e Authority como eixos independentes.
4. independent audit como parte do regime de qualificação, não fallback excepcional.
5. cost-to-trust como métrica superior a pass-rate bruto.
6. corrective loop como unidade legítima de avaliação.

### ADAPT

1. A2 deve ser registrado como `bounded DEV`, não reputação global.
2. qualification/reputation deve separar implementação correta de **evidence semantics / terminal-state truthfulness**.
3. green gates devem ser tratados como evidence de implementação, não como prova suficiente de semantic architecture correctness.
4. episódios naturalísticos devem contribuir com evidência de transferibilidade sem serem confundidos com matched experimental probes.

### RETIRE

1. first-pass green como proxy principal de qualidade do implementador;
2. ranking global de modelos a partir dessas sessões confounded;
3. “agent said done” como settlement;
4. uso de número de correções isoladamente como sinal de baixa qualidade sem contabilizar custo e taxa de fechamento.

### OPEN

1. Sonnet 5 xhigh × Fable 5 low no **mesmo frozen packet**, mesmo capsule/Authority/base/verification;
2. Fable low × Fable xhigh para isolar o efeito de effort;
3. repetição A2 formal em Validation / Assurance;
4. probe A3 deliberado em que o implementador desenha os falsifiers a partir do acceptance objective;
5. medição formal de tokens/custo/elapsed/auditor effort/human interruption/corrective burden por candidate aceito;
6. determinar quanto da diferença histórica Sonnet↔Fable vem do modelo e quanto vem da maturidade posterior do capsule/harness.

## 11. Conclusão atual

A conclusão de 2026-08-13 é mais forte, porém ainda conservadora:

> **Fable 5 low deixou de ser apenas um treatment promissor. Ele possui dois probes A2 independentes em classes diferentes e está qualificado para decomposição de implementação DEV bounded sob contrato/Authority/evidence/auditoria explícitos.**

Ao mesmo tempo:

> **A qualificação não deve ser generalizada para A3, promoção, runtime activation ou arquitetura autônoma. Os defects recorrentes mostram que semantic provenance, system-level ownership e evidence/terminal-state truthfulness ainda exigem auditor independente.**

O principal finding para a arquitetura do tare.tools não é “Fable venceu Sonnet”. É que o sistema composto abaixo está funcionando de forma empiricamente plausível:

```text
model capability
× bounded autonomy
× deterministic Authority
× capability/effect ceiling
× explicit evidence contract
× independent falsification
× bounded corrective
→ candidate settlement / cost-to-trust
```

Isso oferece evidência interna a favor do próprio desenho do tare.tools: não precisamos tornar inteligência probabilística a fonte de autoridade para obter implementação útil e crescente autonomia.

## 12. Proveniência e evidência interna

### Evidência recente primária — harness repo

- **RELAY-Q7 / F5L-06 A2:** `universal-agent-harness-prototype` Issue #11 — final audited candidate `b0dea202e29e418fc0de04db826c5917cd851ed9`, verdict `ACCEPTED_AS_A2_DEV_SHADOW_CANDIDATE`.
  - https://github.com/augusto-scarvalho/universal-agent-harness-prototype/issues/11
- **RELAY-Q8 / F5L-07 A2:** Issue #12 — final audited candidate `eb08cd6228596b3b3c97f841442b7a362a9e2aef`, `a2BoundedDevQualification: QUALIFIED`.
  - https://github.com/augusto-scarvalho/universal-agent-harness-prototype/issues/12
- **BASELINE-CI-01:** Issue #14 — scoped repair + inherited blocker discovery.
  - https://github.com/augusto-scarvalho/universal-agent-harness-prototype/issues/14
- **BASELINE-CI-02:** Issue #15 — ownership archaeology + semantic corrective; final candidate `46d97a17aa2c25acaa6a2fda1b6847ef6eec64ff` accepted.
  - https://github.com/augusto-scarvalho/universal-agent-harness-prototype/issues/15
- **Baseline promotion:** PR #16 — exact-head CI exposed regression-suite contract problem; promotion remains blocked/draft at this snapshot.
  - https://github.com/augusto-scarvalho/universal-agent-harness-prototype/pull/16
- **CI-REGRESSION-01:** Issue #17 — `RUNNING`; only ACK/PLAN is evidence at esta data, sem outcome contabilizado.
  - https://github.com/augusto-scarvalho/universal-agent-harness-prototype/issues/17

### Evidência histórica no tare.tools.research

Comparadores Sonnet/Opus e os episódios iniciais Fable permanecem nos snapshots/source-artifacts históricos já preservados pelo repositório. Este documento não altera esses bytes e não transforma observações de sessões privadas em afirmações vendor-wide.

## 13. Próxima atualização prevista

Atualizar este estudo quando ocorrer qualquer um destes eventos:

1. settlement independente do CI-REGRESSION-01;
2. primeiro matched packet Sonnet xhigh × Fable low;
3. primeiro Fable low × xhigh effort-controlled;
4. primeiro probe A3 formal;
5. disponibilidade de dados de economics suficientes para calcular cost-to-trust em vez de apenas inferi-lo qualitativamente.
