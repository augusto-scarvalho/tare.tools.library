# Research round — pipeline-metamodel (Double Diamond curto)

Aberto: 2026-08-04. Orquestrador: overseer (Fable). Origem: row `pipeline-metamodel`
(P1/L, arco esteira-de-auditoria-mecanizada item 6; dono mandou ROUTE research primeiro).

## Pergunta

O blueprint da esteira de entrega por TIPO de workflow (inline, lane delegada,
fork-join, research round) deve virar objeto canônico
(`.harness/routing/pipeline-metamodel.json`) com derivações — (a) seções de playbook
compiladas, (b) delivery-bar gerada, (c) conformance-check — ou o valor já está
coberto pelos mecanismos existentes (ritual-enforcement-map + delivery-bar advisor +
directive-maps)?

## Critérios de sucesso (o que uma boa resposta satisfaz)

1. **Uma só fonte de verdade por informação.** Se o objeto nasce, fica decidido o que
   acontece com o ritual-enforcement-map (derivado, aposentado, ou escopado) — nunca
   dois cânones para "quem cobra o passo X".
2. **Direção declarada.** Bottom-up (prosa → mapping, estilo directive-map) vs
   top-down (objeto → prosa compilada, estilo SPEC-173) — com custo de migração e
   risco de drift de cada direção.
3. **Cada derivação tem consumidor nomeado** e o delta vs o que existe hoje
   (teste YAGNI explícito por derivação).
4. **Blast radius honesto**: a escada de estágios é parametrizável por tipo, ou N
   tipos divergentes viram pântano de config?

## Orçamento e largura declarados (D010)

- Research **FOCADA** (uma decisão de forma, feature já esboçada na row) → largura
  **2 workers POR wave** (perspectivas: simplicidade/YAGNI vs
  confiabilidade/enforcement), justificativa: EXP-15 mediu redundância com 5 workers
  em tema único; 2 bastam para tensionar as direções por brief.
- **Gate humano 2026-08-04: dono aprovou os 3 briefs** — 1 wave de divergência por
  brief (A, B, C; largura 2 cada) + 1 wave de crítica seedada. Budget revisado do
  round: **≤200k tokens** (gate de 60% do playbook por wave).
  `workflow token-audit` antes de cada start.
- Design de experimento (L18): N/A nesta fase — a saída é decisão de forma, não
  claim mensurável; se uma derivação for promovida, ela ganha cenário (gate), não EXP.

## Fase 1 — Evidências (todas [repo], colhidas 2026-08-04)

| claim | fonte | tipo | método | limitações | confiança | maturidade |
|---|---|---|---|---|---|---|
| Precedente top-down existe e está em produção: objeto canônico GERADO das fontes legadas, projeções congeladas byte-identical, drift-check, playbook compilado por UM assembler | `scripts/harness_lib/role_metamodel.py:1-40`, `playbook_compiler.py:1-25` (SPEC-173) | repo | leitura direta | metamodel de ROLES, não de estágios de pipeline | forte | produção |
| Precedente bottom-up existe e está em produção: fontes de prosa permanecem canônicas, mapping declara enforcement por id-hash, gate falha em item sem mapping | `scripts/harness_lib/security_directives.py:1-25` | repo | leitura direta | cobre directives de segurança | forte | produção |
| O item 5 do arco JÁ entrega "todo passo do playbook do overseer nomeia quem cobra" — statuses hook/gate/leg/doctor/advisory/gap, gate `ritual-enforcement-map`, id = hash do texto do passo | `scripts/harness_lib/ritual_map.py:1-25` (a731198) | repo | leitura direta | bottom-up: não DERIVA playbook nem delivery-bar; escopo = 2 playbooks do overseer | forte | produção |
| Delivery-bar hoje é advisory hand-written (R1-R11) sobre a surface staged; nunca bloqueia | `tools/hooks/delivery_bar_advisor.py:1-42` | repo | leitura direta | regras têm lógica própria por rule (não só "estágio presente") | forte | produção |
| Os tipos de workflow do runner são `map-reduce`/`fork-join` + profiles; os "tipos" da row (inline, lane, fork-join, research round) são tipos da ESTEIRA DE ENTREGA, um nível acima do runner | `.harness/workflows/WORKFLOWS.md:5-15` vs row `pipeline-metamodel` | repo | leitura direta | taxonomia da row ainda não existe em lugar nenhum como objeto | forte | produção |
| Não há registro prévio de round/decisão sobre pipeline-metamodel | `records search` (vazio) + `doc-find` | repo | busca | — | moderada | — |

### Flow A — estado da arte externo (colhido 2026-08-04, pós-gate, a pedido do dono)

| claim | source | tipo | limitações | confiança | maturidade |
|---|---|---|---|---|---|
| [web] SPEM (OMG) é amplamente usado para MODELAR processo de software mas "lacks built-in enactment capabilities — no tool or process engine executes it"; não cobre execução/monitoramento; adoção dispersa. Metamodelo descritivo sem engine que o EXECUTE drifta da prática | ResearchGate "Software Process Engineering Metamodel (SPEM)"; scirp.org "Comparative Analysis BPMN vs SPEM"; omg.org/spec/SPEM/2.0 (primária) | paper/spec | análises acadêmicas, não medição industrial | moderada | validado |
| [web] Pipeline-as-code em CI (GitHub Actions/GitLab) FUNCIONA como objeto canônico — mas porque o objeto é ENACTADO por engine (o YAML É o pipeline, não descrição dele); enforcement é automático por construção | TechTarget "Pipeline as Code"; harness.io academy | docs/vendor | fontes vendor/promocionais | moderada | produção |
| [web] Lição PaC: complexidade do objeto vira "pipeline debt"; enforcement "is rarely binary" — desvio aceitável em dev pode ser bloqueante em prod (gradação de status é necessária) | Puppet "Policy as Code Beyond the Pipeline"; TechTarget | blog/vendor | promocional | preliminar | produção |

### Flow A — literatura científica comparativa (colhida 2026-08-04, ordem do dono: comparativo com trabalhos científicos)

| claim | source | tipo | ano | método | limitações | confiança | maturidade |
|---|---|---|---|---|---|---|---|
| [web] Tese top-down original: "software processes are software too" — processo codificado em linguagem executável (process programming) deveria ser o centro da engenharia de software | Osterweil, ICSE 9 (1987); "Revisited" ICSE 19 (1997) — dl.acm.org/doi/10.1145/253228.253440 | paper | 1987/1997 | posição + protótipos (Arcadia/Little-JIL) | tese de pesquisa, não estudo empírico de adoção | forte (como fonte da tese) | demonstração conceitual |
| [web] A geração que implementou a tese (PSEEs: Marvel, SPADE, EPOS...) teve BAIXA adoção industrial; a literatura aponta "lack of flexibility in software process modeling" como causa principal, e "the highly dynamic nature of the software process" como razão documentada para as poucas aplicações comerciais | Fuggetta et al., "PSEEs: A Brief History and Future Challenges", Annals of SE (2002); "Comparative Review of PSEEs", Annals of SE (2002); Matinnejad & Ramsin, IEEE ECBS 2012 | survey/review | 1997-2012 | revisão comparativa multi-sistema | era pré-DevOps; sistemas acadêmicos | forte (convergência de 3+ surveys) | validado |
| [web] Sobreviver à rigidez exigiu DESVIO como cidadão de primeira classe: deviation-tolerance model formal (aceitar/rejeitar violação de constraint no enactment); "sem gerenciar a evolução durante o enactment, PSEEs estão condenados a falhar na adoção" | Cugola, deviation management (IEEE TSE 1998 / Springer); "Review of Detecting and Correcting Deviations on Software Processes" (2015) | paper | 1998-2015 | formalização + estudos de caso | validação limitada a casos | moderada | protótipo→validado |
| [web] O ramo científico que VINGOU para "declarado vs praticado" é conformance checking (process mining): modelo normativo × log de eventos observado, alinhamento e diagnóstico de desvio — detecção a posteriori, não prescrição a priori | van der Aalst, "Process Mining" (Springer, 2ª ed. 2016); tutorial "Process Mining in the Large" (vdaalst.rwth-aachen.de/publications/p775.pdf) | livro/paper | 2011-2016 | formal + ferramentas maduras (ProM etc.) | domínio BPM, não esteiras de agentes | forte | produção |
| [web] Pipeline-as-code enactado, medido em escala: 49K+ repos, 267K+ históricos, 3.4M+ versões de workflow (2019-2025) — mediana 3 workflows/repo, **7.3% dos workflow files mudam POR SEMANA**, ~3/4 dos commits de workflow têm UMA só mudança, maioria em task configuration | Mazrae, Decan, Mens, Wessel, "An Empirical Study of the Evolution of GitHub Actions Workflows", arXiv:2602.14572 / JSS 2026 | paper empírico | 2026 | mineração em larga escala | OSS público apenas | forte | validado |
| [web] Manutenção do objeto de pipeline tem custo real e contínuo ("hidden costs of automation"; bug fixing e melhoria de CI/CD como drivers principais); complexidade/heterogeneidade/compliance de workflows é objeto de estudo próprio | arXiv:2409.02366 (workflow maintenance, ~200 projetos maduros); arXiv:2507.18062 (complexity/compliance) | paper empírico | 2024-2025 | mineração + análise qualitativa | OSS público | moderada | validado |

### Flow A — bleeding edge 24-36 meses (colhido 2026-08-04, ordem do dono)

| claim | source | tipo | ano | método | limitações | confiança | maturidade |
|---|---|---|---|---|---|---|---|
| [web] Workflow de agentes LLM como OBJETO declarativo (DAG, "workflows as data rather than code") em produção no PayPal: -60% tempo de dev, 3× velocidade de deploy, 50 linhas de DSL vs 500+ imperativas — objeto canônico ENACTADO por engine, no domínio exato deste repo | Daunis, "A Declarative Language for Building And Orchestrating LLM-Powered Agent Workflows", arXiv:2512.19769 (dez/2025) | paper industrial | 2025 | caso de produção | single-company, sem peer review confirmado | moderada | produção |
| [web] Enforcement em RUNTIME por regras declaradas: DSL leve com trigger + predicado + mecanismo de enforcement por regra; previne >90% de execuções inseguras em code agents, overhead de ms — estruturalmente idêntico ao vocabulário check:/trigger: dos directive-maps deste repo | Wang et al., "AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents", arXiv:2503.18666 (2025) | paper | 2025 | avaliação multi-domínio | benchmarks, não produção | moderada | validado |
| [web] Conformidade PROCEDURAL de trajetórias de agentes como verificação de traces (LTL): medir, enforçar E TREINAR compliance de processo em agentes tool-using — conformance checking chegando ao domínio de agentes | "AgentLTL: A Trace-Verification Framework...", arXiv:2607.02599 (2026); PMAx arXiv:2603.15351 (EMMSAD 2026); MANTRA arXiv:2605.06334 (SMT-validated compliance) | papers | 2026 | formal + benchmarks | pré-print/tool-demo, sem peer review | preliminar | protótipo |
| [web] Métrica emergente "workflow fidelity" (além de task success): a esteira SEGUIDA importa tanto quanto o resultado, medida por replay/alignment contra modelo normativo — em sistemas agentic de pagamento | "Beyond Task Success: Measuring Workflow Fidelity in LLM-Based Agentic Payment Systems", arXiv:2605.06457 (2026) | paper | 2026 | replay/conformance | domínio pagamentos | preliminar | protótipo |

**Padrão da ponta (fato, não opinião):** as TRÊS formas em disputa neste round
existem simultaneamente na literatura de agentes 2025-26 — (i) objeto declarativo
enactado (arXiv:2512.19769), (ii) regras de enforcement bottom-up com
trigger/predicado (AgentSpec), (iii) conformance de traces a posteriori
(AgentLTL/PMAx/MANTRA). Nenhuma venceu ainda; a (i) só aparece ENACTADA por engine,
nunca como documentação derivadora. Questão adicionada à crítica: qual das três é
isomórfica ao que a row propõe, e o que o repo já tem de cada uma?

**Mapeamento literatura → briefs (QUESTÕES para a wave de crítica, não conclusões):**
- Brief A: a trajetória Osterweil→PSEE→rigidez-mata-adoção é análoga ao top-down aqui,
  ou a analogia falha porque o consumidor do objeto seria um gate determinístico e não
  humanos? Conformance checking (normativo × observado) é o análogo científico do
  mapping bottom-up + gate — ou é uma terceira via (detecção a posteriori) distinta
  das duas direções postas?
- Brief B: o achado GitHub Actions (7.3%/semana de churn, mudanças pequenas,
  task-config dominante) transfere para a esteira deste repo (3 mudanças/semana
  medidas)? Isso fortalece ou enfraquece o corte das derivações?
- Brief C: o deviation-tolerance de Cugola implica que QUALQUER schema por tipo
  precisa de status graduado de desvio (o vocabulário advisory/gap do ritual_map
  cobre isso?) — e o custo de manutenção empírico dos papers de 2024-26 calibra o
  "pântano de config"?

**Síntese flow A (Define, revisada):** o eixo discriminante externo é **enactment**:
objeto canônico de pipeline dá certo quando um ENGINE o executa (CI-as-code) e
falha como documentação sincronizada à mão (SPEM). A proposta da row é um objeto
DESCRITIVO (deriva playbooks/delivery-bar) — regime SPEM, não regime CI —, o que
corrobora o veredito bottom-up das waves A/B por uma rota independente. O
contra-caso honesto: se um dia o harness ENACTAR os estágios (o driver
`route --loop` já executa uma choreografia de estágios hard-coded), o objeto
deixaria de ser descrição e viraria programa — esse é o trigger de revisita
externo, somado ao trigger interno do FINDING-010. A gradação de enforcement da
lição PaC já existe no vocabulário do ritual_map (advisory/gap).

**Achado central (Define):** os dois precedentes apontam em direções OPOSTAS e o
ritual-enforcement-map recém-shipado já ocupa parte do território. Se o objeto
top-down nasce e COMPILA seções de playbook, os ids do ritual-map (hash da prosa)
passam a rastrear texto gerado — os dois mecanismos colidem. A decisão real não é
"ter ou não um JSON", é **direção + reconciliação**.

## Fase 2 — Briefs (aguardando gate humano)

### Brief A — direção e reconciliação
Problema: duas arquiteturas canônicas coexistem no repo (bottom-up directive-map,
top-down SPEC-173). Qual direção minimiza drift e custo de migração para a esteira,
e o que acontece com o ritual-enforcement-map em cada uma?
Atores: overseer (consome playbook), gate (cobra conformidade), dono (audita diffs).
Restrições: nunca duas fontes de verdade; migração estilo SPEC-173 exige projeções
congeladas + drift-check; mapping-file-only exige que a prosa continue canônica.
Sucesso: uma direção recomendada com plano de reconciliação explícito e reversível.

### Brief B — valor marginal por derivação (teste YAGNI)
Problema: o que o objeto entrega que ritual-map + delivery-bar + directive-maps NÃO
entregam hoje? Por derivação — (a) seções de playbook adaptáveis por role, (b)
delivery-bar gerada, (c) conformance-check estilo spec_conformance — nomear o
consumidor concreto e o delta. Derivação sem delta = cortada.
Atores: cada consumidor nomeado. Restrições: R1-R11 têm lógica por regra que um
"estágio declarado" não expressa; playbook compilado já existe por outra rota.
Sucesso: lista derivação → consumidor → delta → veredito (vale/não vale).

### Brief C — parametrização por tipo vs pântano de config
Problema: a escada (route → brief → implement → verify → gate‖reckon‖mutate‖audit →
commit → close-out) é UMA com estágios opcionais por tipo, ou os 4 tipos divergem a
ponto de virar 4 pipelines mantidos à mão? Custo de manutenção em cada forma.
Atores: quem edita o objeto a cada mudança de ritual. Restrições: o arco acabou de
mudar a esteira 3× em uma semana — objeto rígido demais vira atrito.
Sucesso: forma do schema recomendada com exemplo concreto dos 4 tipos.

## Gate humano (Fase 2 → 3)

**PARADO AQUI para aprovação do dono** antes de gastar a wave de Develop
(research-divergence, largura 2, budget acima). Opções na mesa: aprovar os 3 briefs,
cortar para A+B, ou decidir inline sem wave (a evidência acima já tensiona bastante
as direções — o dono pode julgar direto e pular para Deliver).

## Fase 4 — Crítica e operações (join manual, 2026-08-04)

Crítica: WF-20260804-092656-940830, 4 críticos cross-vendor (validade sonnet·xhigh,
arquitetura nvidia·glm-5.2, custo nvidia·glm-5.2 — respawn após gemini 401
(row `gemini-compat-chat-401`); INV-1 vetou claude no retry —, segurança
sonnet·xhigh). Zero blockers de segurança.

**Provenance do join:** o artefato de reduce do WF EXCLUIU os workers 002/003 em
silêncio (seats http sem `sourceFilesVerified` com findings high — bug registrado
`reduce-drops-repo-blind-highs`, P1). Este join foi feito pelo orquestrador sobre os
QUATRO results crus; nada foi perdido.

**O que a crítica mudou:**
1. (validade, high) A convergência 6/6 das waves geradoras é **corpus-shaped**: mesmo
   modelo + evidência PRÉ-ENQUADRADA pelos briefs do orquestrador. Não invalida a
   direção — a própria crítica cross-vendor (sonnet+glm) endossou bottom-up
   independentemente — mas rebaixa a classe: direção = **moderada-forte**, não
   "unânime". Controle positivo: claims numéricos [repo] verificados exatos.
2. (validade, high) As tabelas de literatura têm verificação assimétrica:
   arXiv:2602.14572 verificado na fonte primária pelo orquestrador (números conferidos);
   PSEE/rigidez corroborado por 3+ surveys via busca; demais = snippet de busca.
   Classes de confiança da tabela ajustadas para não misturar "concordância entre
   fontes" com "existência verificada". Nenhuma decisão desta rodada depende de claim
   somente-snippet.
3. (arquitetura, high) A forma da wave C (base-ladder+overlays) **arrisca recriar o
   objeto canônico pela porta dos fundos** → operação da C3 rebaixada para estacionada.
4. (arquitetura+custo, high) **Conformance a posteriori sobre traces** (AgentLTL/PMAx/
   process mining) é uma terceira via genuína não considerada pelas geradoras — com
   overhead de infraestrutura de observação não custeado (custo). Vira aposta-de-fronteira.
5. (segurança, medium) Locators de enforcement (hook:/gate:/check:/trigger:) nos maps
   EXISTENTES são texto livre auto-atestado sem check de vida — pointer stale passa em
   silêncio. Vira task própria (vale independente desta rodada).

**Operações por conceito:**

| id | conceito | operação | fundamento |
|---|---|---|---|
| C1 | Direção bottom-up: NÃO criar `.harness/routing/pipeline-metamodel.json`; prosa dos playbooks permanece canônica | **mantida** | waves A/B + crítica arq/custo; PSEE-rigidez; sem taxonomia-máquina legada p/ consolidar; AgentSpec-isomorfismo do que já existe |
| C2 | Derivações (a) playbook compilado do objeto, (b) delivery-bar gerada, (c) conformance-check como derivação | **rejeitadas** | YAGNI (wave B): delta zero/negativo por derivação; R1-R11 irredutíveis; ritual-map já é o dente de (c) |
| C3 | Forma base-ladder+overlays esparsos (schema da wave C) | **estacionada** | direction-neutral, mas sem consumidor hoje + risco porta-dos-fundos (crítica arq); registrada aqui p/ o dia em que um consumidor nascer |
| C4 | Conformance a posteriori de traces da esteira (workflow fidelity) | **aposta-de-fronteira** | terceira via real (AgentLTL/PMAx/MANTRA, 2026); overhead de observação não custeado; maturidade protótipo |
| C5 | Extensão de ESCOPO do ritual-enforcement-map aos demais playbooks que definem esteira (route/research/workflow) | **mantida → task** | único delta sobrevivente de B/C: mecanismo é source-genérico; extensão = RITUAL_SOURCES + mappings no mesmo commit |
| C6 | Check de vida dos locators de enforcement nos maps existentes | **mantida → task** | achado de segurança da crítica; vale para ritual-map + security-directive-map já shipados |

## Fase 5 — Deliver (portfólio)

- **núcleo:** C5 (`ritual-map-scope-extension`), C6 (`enforcement-locator-liveness`)
- **contingência:** C3 (forma registrada; ativa SE um consumidor per-spawn nascer)
- **aposta-de-fronteira:** C4 (conformance de traces; sem EXP — nenhum claim mensurável ainda)
- **estacionadas:** objeto canônico top-down — triggers de revisita: (i) prosa da esteira
  estável <1 edit estrutural/mês (hoje ~3/semana) E ≥2 consumidores per-spawn nomeados;
  OU (ii) um engine passa a ENACTAR os estágios (ex.: `route --loop` generalizado) — aí
  o objeto é programa, não documentação (regime CI/PayPal, não regime SPEM)
- **rejeitadas:** derivações (a)/(b)/(c) como derivadas de objeto canônico
- Decisão canônica: DECISIONS.md **D056**. Row `pipeline-metamodel` fecha nesta rodada.

## Rastreabilidade

| Evidência | Problema | Ideia | Decisão | Task |
|---|---|---|---|---|
| ritual_map/role_metamodel/security_directives [repo] + PSEE-rigidez + AgentSpec [web] | duas direções canônicas colidindo | bottom-up, prosa canônica | D056 | — |
| R1-R11 irredutíveis [repo] + delta-zero por derivação | derivações especulativas | cortar (a)(b)(c) | D056 | — |
| B: "extend RITUAL_SOURCES" + escopo 2/8 playbooks | passos de esteira fora do overseer sem dente | estender escopo do map | D056 | ritual-map-scope-extension |
| crítica segurança: locator stale passa em silêncio | enforcement auto-atestado | liveness probe de locators | D056 | enforcement-locator-liveness |
| AgentLTL/PMAx/MANTRA + workflow fidelity [web] | conformidade declarado-vs-praticado a posteriori | conformance de traces | D056 (fronteira) | — |
| WF-092656 reduce excluiu seats http | cidadania de seats compat no reduce | validador único + summary honesto | — | reduce-drops-repo-blind-highs |
