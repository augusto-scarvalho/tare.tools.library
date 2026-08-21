# Weekly monitor W28 (workflows dinâmicos) — extrato para o harness

Fonte: digest semanal GPT fornecido pelo dono (2026-07-13). NÃO é uma rodada
de research; citações são `[web]` não-verificadas — ideias avaliadas pelo
mérito interno contra o estado real do harness. Quarto da série W28
(memória, qualidade de código, multi-agente); numeração continua (EXP-9).

## Onde o harness JÁ cobre o digest (sem trabalho novo)

| Achado do digest | Equivalente já operante aqui |
|---|---|
| "Orquestração de conveniência delegável; orquestração de controle fica no harness" | É a doutrina em produção: `codex exec` JÁ é orquestração hospedada um nível abaixo (inner loop opaco atrás de contrato WORKER_RESULT tipado); budget/política/evidência/review ficam aqui (blocos budgets do workflow.json, delegation ledger, `review` verb) |
| Topology Cascade Router (prioridade nº 1 do digest) | Meio construído, em shadow mode: `workflow.json.topologyRouter` registra `wouldFork`/`recommendedWorkers`/`reasons` (incl. circuit breakers abertos) por workflow, sem agir — observe-only aguardando DW.4 (OWNER-GATED). Adicionar `hosted_multi_agent` à taxonomia é 1 valor de enum no dia em que a fase de controle for autorizada |
| Dinamismo confinado (SpaCellAgent) + "não promover workflows aprendidos automaticamente" (prioridade nº 7) | Regra universal: agentes não mutam o próprio modelo/effort — o harness spawna perfis de um catálogo (task-profiles + model cards); autoevolução está em SELF_EVOLUTION I4 (Deferred); o portão de promoção com quarentena é o EXP-3 já na fila |
| Disciplina de snapshot atômico (lição LangGraph) | Parcial: `write_json` via os.replace (fix de torn-read de hoje), checkpoint bounded com reinjeção. O que NUNCA testamos é a PROPRIEDADE "estado materializado == event log == replay" → EXP-9 |
| Evidence ledger sobrevivendo à opacidade | records/escalations/delegation ledger existem; a lacuna de proveniência (servedModel) já está na fila como EXP-5 — subagentes hospedados a tornariam PIOR, o que reforça EXP-5 antes de qualquer trial hospedado |

## Experimento extraído (reversível; template do research-playbook)

### EXP-9 — Probe de conformidade de transições de estado (LangGraph-inspired) · prioridade ALTA
- **Hipótese**: presumimos, sem testar, que as três vistas do estado de um
  workflow contam a mesma história — `workflow.json` (materializado),
  `trace.jsonl` (event log) e `async/` (runtime). Os bugs do DeltaChannel
  são exatamente a classe que já nos mordeu (torn reads, placebo hook,
  bounded-replay banner) — checkpoint parcial fingindo ser snapshot.
- **Invariantes candidatos** (verificados nos artefatos reais 2026-07-13):
  todo `workersPlanned` tem evento queued + terminal no trace; status do
  workflow consistente com os status dos workers sob o joinPolicy;
  timestamps monótonos (createdAt ≤ worker started ≤ finished ≤ updatedAt);
  `asyncGroupId` idêntico em workflow.json/trace/async-group.json;
  `async/tasks/AT-*.json` ↔ workers 1:1; `phase` compatível com o último
  evento do trace.
- **Baseline**: rodar o probe sobre TODOS os workflows retidos (incl.
  WF-E2E-TAIL) — zero-LLM, read-only; qualquer violação viva é achado.
- **Fase 2**: check advisory no doctor — irmão do EXP-2 (invariantes de
  compactação) e do EXP-4 (declarado-vs-real): mesma família, superfície
  diferente (estado de workflow). **Reversão**: probe read-only; advisory
  de uma linha.

## Item de DECISÃO (não é experimento — vai à fila para o dono)

- **Multi-agente hospedado da OpenAI como topologia**: comoditiza o
  fan-out, mas (a) conflita com a doutrina overseer-plans — a decomposição
  migraria para dentro do vendor, e o dono determinou que o plano é sempre
  do overseer; (b) reduz proveniência/auditabilidade — exatamente a lacuna
  EXP-5, e o grafo realizado fica opaco; (c) nossa lane codex é CLI de
  assinatura — o beta é Responses API (custo API real); (d) roteamento
  dinâmico é território DW.4 (OWNER-GATED). Se um dia o trial for
  autorizado, os limiares de abandono do digest são bons defaults: ganho
  de latência <20%, custo +50% ou auditabilidade insuficiente → não vira
  default.

## Estacionados (com gatilho explícito)

- **A/B hosted fan-out vs DAG próprio** (4 configurações): gatilho =
  recurso disponível na lane de assinatura + decisão do dono acima.
- **Adapters de observabilidade para subagentes hospedados**: mesmo
  gatilho — sem trial autorizado, é infraestrutura para um backend que não
  usamos.
- **Catálogo de analisadores com seleção adaptativa (SpaCellAgent aplicado
  a auditoria de código)**: reforça o Oracle Action Router já estacionado
  (extrato de qualidade) — mesmo gatilho: semanas de telemetria
  byOutcome/oracle.
- **Semântica formal de snapshot/delta/patch (AWIR)**: gatilho = o dia em
  que workflows mutarem mid-flight (replan, inserção de branch). Hoje o
  ciclo é plan→run→reduce sem patching — formalizaria operações que não
  executamos. A lição prática do LangGraph entra via EXP-9.

## Veredito crítico do digest

A comoditização do fan-out hospedado não muda nossa arquitetura — confirma
a separação que já operamos (vendor pode ter o inner loop; controle,
orçamento e evidência ficam no harness) e o próprio digest chega à mesma
conclusão. O detalhe que o digest não sabia: nosso topology router já
existe em shadow mode dentro de cada workflow.json, esperando a decisão de
controle do dono. O aproveitável genuíno da semana é um só e é barato:
EXP-9 testa como propriedade a consistência de estado que hoje presumimos
— a única lição do episódio LangGraph que se aplica a quem NÃO usa
LangGraph. O trial hospedado fica corretamente atrás de decisão do dono,
com os limiares de abandono do digest anotados.
