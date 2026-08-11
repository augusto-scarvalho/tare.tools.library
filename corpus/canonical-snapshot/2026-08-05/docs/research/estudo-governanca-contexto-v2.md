

 
 
 
 Governança de Contexto em Harnesses Multiagênticos — Edição Científica Ampliada
 
 

# Context Governance in Multi-Agent Harnesses

Governança
de Contexto em Harnesses Multiagênticos de Longa Duração

Overseer
loops, subagentes, compactação, context folding, garbage collection,
memória e controle cross-vendor

Resumo

Contribuições desta edição
ampliada

Abstract

Sumário

1. Introdução

2. Questões de pesquisa e
método

2.1 Questões de pesquisa

2.2 Tipo
de revisão

2.3 Limites da comparação
cross-vendor

2.4 Estratégia
de busca e atualização do corpus

2.5 Hierarquia prática da
evidência

2.6 Corpus mínimo e corpus
estendido

3. Modelo
do problema: contexto físico, útil e confiável

3.1 Quatro limites diferentes

3.1.1 Limite
físico

3.1.2 Limite de recuperação

3.1.3 Limite de utilização

3.1.4 Limite de
interferência

3.2
Limite operacional

3.3 Contexto como cache
cognitiva

3.4 O que os benchmarks
realmente medem

3.5 Taxonomia
ampliada de falhas de contexto

3.5.1
Diluição

3.5.2 Obsolescência e
mistura temporal

3.5.3 Contaminação
por tentativa fracassada

3.5.4 Perda de autoridade

3.5.5 Corrupção do
protocolo de ferramentas

3.5.6 Deriva por resumo
sucessivo

3.5.7
Ansiedade de contexto e encerramento prematuro

3.6
Contexto longo como sistema parcialmente observável

4. Taxonomia operacional

5. Arquitetura de memória e
estado

5.1 Camadas

5.2 Task Ledger e Progress
Ledger

Task Ledger

Progress
Ledger

5.3
Trajectory Store

5.4 Context Object Model

5.5 Estado
canônico, eventos e visões materializadas

5.5.1 Por que não
basta um arquivo summary.md

5.5.2
Proveniência como requisito de compactação

5.6
Memória episódica, factual, procedimental e normativa

5.7 Memória por
projeto e isolamento multiagente

6. Overseer loop e
ciclo de vida da sessão

6.1 Entidade lógica
versus sessão física

6.2 Loop
operacional

6.3
Hidratação mínima

6.4 Checkpoint canônico

6.5
Completion Capsule

7.
Subagentes: compactação interna e folding na fronteira

7.1 Duas fronteiras
diferentes

Compactação interna

Folding
pai–filho

7.2 Classes de subagentes

S0 — Atômico

S1 — Focado

S2 —
Multifásico

S3 — Longa
duração

7.3 Não compactar raciocínio
aberto

7.4 Contrato de retorno

7.5 Subagentes recursivos

7.6
Evidência comparativa: sem compactação, compactação mid-task e
folding

7.6.1 Quando não compactar

7.6.2 Quando compactar
mid-task

7.6.3
Quando resetar

7.7
Delegação como contrato, não como mini-prompt informal

7.8 Folding recursivo e
perda cumulativa

7.9 Modelos pequenos e
microgerenciamento

8. Garbage collection de
contexto

8.1 Definição

8.2 Critério de
elegibilidade

8.3 O que remover da visão
ativa

Tool outputs persistidos

Duplicatas

Resultados superseded

Episódios concluídos

Skills e tools fora de
fase

8.4 O que
pinamos

8.5 Mark-and-sweep agêntico

Roots

Mark

Sweep

8.6 GC
geracional

Geração 0
— efêmera

Geração 1 —
fase

Geração 2 —
tarefa

Pinned
generation

8.7 Triggers

8.8
Fold, mask e prune

Fold

Mask

Prune

8.9
Cache-aware GC

8.10 Correção de protocolo

8.11
Garbage collection orientado a objetos versus trimming
cronológico

8.12 Minor GC, major GC e
final GC

Minor GC

Major GC

Final GC

8.13 Economia de
cache e momento do commit

8.14 Segurança contra
coleta maliciosa

8.15 GC de recursos não
textuais

9. Perfis de compactação

9.1 Perfil
genérico

9.2
Perfil query-aware

9.3 Perfil específico por
tarefa

Coding

Pesquisa

Incidente

9.4 Perfil adaptativo ao
conteúdo

9.5
Perfil aprendido

9.6 Compactação on-the-fly

9.7 Arquitetura híbrida

Schema

9.8
Comparação dos principais trabalhos de compactação e folding

9.9 Kernel canônico e
overlay adaptativo

9.10 Perfis canônicos
recomendados

Coding implementation

Research

Incident
response

Review

Overseer

9.11 Quando usar um
compressor separado

10. Context folding
e gestão de ramificações

10.1 Conceito

10.2 Folding em subagentes

10.3 Folding hierárquico

10.4 Folding versus reset

10.5 Folding como
estrutura de árvore

10.6 Não-estacionariedade e
FoldAct

10.7 Folding consciente de
intenção

10.8 Folding versus
artefatos tipados

11. Lost
in the Middle e empacotamento atento à posição

11.1
Não criar uma seção monolítica de “memória histórica”

Zona A —
início

Zona B

Zona C — meio

Zona D

Zona E —
final

11.2 Redundância controlada

11.3 Retrieval antes da
ordenação

11.4
Memória negativa

11.5 Estratégia de
packing em duas passagens

Passagem
1 — seleção

Passagem 2 — ordenação

11.6 Orçamento para
contraevidência

11.7 Benchmarks posicionais
próprios

12. Comparação de
vendors e modelos abertos

12.1 Comparação de
superfícies de controle

12.2 Codex

12.3 Claude Code e API
Anthropic

12.4 Kimi
Code CLI

12.5 Gemini
CLI

12.6
Modelos abertos

12.7 Protocolo justo de
comparação

Native
versus native

Compressor
comum

Mesmo modelo, perfis
diferentes

12.8 Leitura
comparativa: primitives versus política

Codex

Claude
Code/Agent SDK

Kimi Code
CLI

Gemini e
Google ADK

Modelos
abertos

12.9 O que
uma comparação cross-vendor precisa fixar

13. Lições de outros
harnesses

13.1
Magentic-One

13.2 MetaGPT

13.3
SWE-agent

13.4
Agentless

13.5
AutoCodeRover

13.6 LangChain Deep Agents

13.7
little-coder

Lições para modelos
pequenos

O que não copiar sem
experimento

13.8 Magentic-One:
ledgers e replanejamento

13.9 MetaGPT e
ChatDev: artefatos versus diálogo

13.10 SWE-agent,
Agentless e AutoCodeRover

13.11 Deep Agents e
filesystem como memória

13.12
little-coder: estudo de caso aprofundado

13.13 Outros repositórios
úteis

14. Arquitetura
proposta: Context Control Plane

14.1
Context Telemetry

14.2
Budget Controller

14.3 Compaction Profile
Compiler

14.4
Integrity Gate

Validação determinística

Validação semântica

14.5
Recovery Probe

14.6 State
machine

14.7
Pseudocódigo

14.8 Arquitetura lógica
detalhada

14.9 Componentes e
responsabilidades

Context Object Registry

Dependency
Graph

Context Budget Controller

Context
Curator

Integrity
Gate

Vendor
Adapter

14.10 Contrato de
capabilities

14.11 Algoritmo de
montagem de contexto

14.12 Algoritmo de
compaction validada

14.13 Decisão de
re-decomposição

15. Perfis por papel e
classe de tarefa

15.1 Overseer

15.2 Planner

15.3
Implementer

15.4 Reviewer

15.5
Researcher

15.6
Incident Agent

15.7 Test
Runner

15.8 Small Model Strict

16. Programa experimental

16.1
Hipóteses

16.2
Estratégias

16.3
Classes de tarefa

16.4 Benchmark posicional

16.5 Experimento de
contextual drag

16.6 Experimento de
subagente

16.7
Vendor benchmark

Trilha A —
produto

Trilha B — representação
comum

Trilha C — modelos locais

16.8 Métricas

Fidelidade

Continuidade

Economia

GC

Multiagente

16.9 ModelContextProfile

16.10 Desenho fatorial e
ablações

16.11 Benchmark de
compactação repetida

16.12 Benchmark de garbage
collection

16.13 Benchmark de
subagentes

16.14 Comparação de vendors

Trilha
produto

Trilha representação comum

Trilha modelos abertos

16.15 Métricas tardias

16.16 Reprodutibilidade

17. Segurança,
governança e auditabilidade

17.1
Context management como superfície de segurança

17.2 Separação de
autoridade

17.3 Constraint Pinning

17.4
Proveniência

17.5
Recuperabilidade

17.6
Memory promotion

17.7 Context
injection e memória contaminada

17.8 Direito
ao esquecimento versus auditabilidade

17.9 Separation of duties

18. Trade-offs,
limitações e ameaças à validade

18.1 Risco de complexidade
acidental

18.2 Preprints recentes

18.3 Judge-based evaluation

18.4 Vendor
drift

18.5 Prompt
cache

18.6
Resumo cumulativo

18.7
Raciocínio oculto

18.8 Privacidade e retenção

18.9
Transferência entre benchmarks e produção

18.10 Opacidade dos vendors

18.11 Custo de complexidade

18.12 Risco de overfitting
dos perfis

19. Roadmap de implementação

Fase 0 —
Telemetria

Fase 1 — Estado canônico

Fase 2 — Offloading e minor
GC

Fase 3 — Context packing

Fase 4 — Perfis canônicos

Fase 5 —
Folding

Fase 6 — Integrity Gate

Fase 7 — Vendor adapters

Fase 8 — Adaptive layer

Fase 9 — Learned policies

20. Agenda de pesquisa aberta

20.1 CompactionBench
agêntico

20.2 Perfis
transferíveis versus específicos

20.3 Curator pequeno
versus modelo executor

20.4 Context policies
treinadas

20.5 GC causal e static
analysis

20.6 Observabilidade
padronizada

20.7
Longitudinalidade

20.8 Harnesses para modelos
pequenos

20.9 Matriz de
validação das hipóteses centrais

21.
Conclusões

22. Referências
bibliográficas

22.1
Fundamentos, benchmarks e artigos peer-reviewed

22.2
Benchmarks e estudos fundamentais ainda em preprint

22.3
Bleeding edge: compactação, folding, execution state e GC

22.4 Documentação
oficial e engineering blogs

22.5
Repositórios, branches, releases, issues e discussões — evidência de
campo

22.6 Documento interno do
projeto

Apêndice A — Glossário
operacional

Apêndice B — Árvore
de decisão operacional

Apêndice C —
Defaults iniciais para experimentação

Apêndice D —
Schema mínimo de ModelContextProfile

Apêndice E —
Checklist de qualidade da evidência

# Governança
de Contexto em Harnesses Multiagênticos de Longa Duração

## Overseer
loops, subagentes, compactação, context folding, garbage collection,
memória e controle cross-vendor

Versão: 2.0 — edição científica ampliada

Data: 26 de julho de 2026

Idioma: Português

Natureza do documento: revisão narrativa estruturada
ampliada, síntese crítica, análise de evidências e proposta
arquitetural

Escopo: harnesses multiagênticos para engenharia de
software, pesquisa, execução de workflows e tarefas de longa duração;
inclui papers peer-reviewed, preprints recentes, documentação oficial,
engineering blogs, repositórios, branches, releases, issues e discussões
técnicas

## Resumo

Agentes baseados em modelos de linguagem executam tarefas cada vez
mais longas, intercalando raciocínio, chamadas de ferramentas, leitura e
alteração de artefatos, testes, delegação a subagentes e interação
humana. Esse modo de operação produz uma trajetória potencialmente
ilimitada sobre uma janela de contexto finita e cognitivamente
imperfeita. A janela nominal anunciada pelo fornecedor não equivale à
capacidade operacional confiável: benchmarks como Lost in the
Middle, RULER e NoLiMa demonstram degradação conforme aumentam o
comprimento, a posição intermediária da evidência, a quantidade de fatos
e a necessidade de associação sem correspondência lexical direta Liu et al., 2024; Hsieh et al., 2024; Modarressi et al., 2025. Em agentes, o
problema é ampliado por tool outputs volumosos, resultados obsoletos,
tentativas fracassadas que contaminam novas gerações, perda de
restrições durante compactação e propagação de ruído entre agentes Cheng et al., 2026; Chen, 2026.

Este documento consolida fundamentos teóricos, resultados
experimentais recentes, práticas de vendors e padrões de harnesses
multiagênticos para responder às seguintes questões: como um Overseer
deve controlar seu contexto ao processar repetidamente itens de backlog;
quando compactar, limpar, dobrar ou reiniciar uma sessão; como
subagentes devem gerenciar contexto no meio de uma tarefa; o que
constitui garbage collection; como enfrentar Lost in the
Middle; como construir perfis de compactação canônicos, específicos
por tarefa e gerados on-the-fly; e como normalizar diferenças entre
Codex, Claude Code, Kimi Code CLI, Gemini CLI e modelos abertos.

A síntese sustenta uma arquitetura em que o estado canônico permanece
fora da janela, em ledgers, Git, stores de artefatos, evidências e
trajetórias. O contexto ativo passa a ser uma visão materializada
temporária desse estado. Propõe-se um Context Control
Plane vendor-agnostic que realiza telemetria, orçamentação,
garbage collection orientado a objetos e dependências, retrieval,
empacotamento consciente de posição, folding de subtarefas, compactação
tipada, validação de integridade, reset e reidratação. O princípio
central é: o Overseer persiste como papel e estado lógico, não
como uma conversa imortal.

Palavras-chave: agentes de IA; sistemas
multiagênticos; context engineering; context compaction; context
folding; garbage collection; memória agêntica; Overseer; subagentes;
coding agents; long context; harness engineering.

### Contribuições desta edição
ampliada

Esta edição preserva o conteúdo da versão anterior e o expande em
seis direções: (1) revisão mais extensa dos benchmarks de contexto
longo; (2) análise comparativa dos mecanismos de garbage collection,
folding e compactação; (3) estudo aprofundado de subagentes e fronteiras
pai–filho; (4) comparação honesta entre vendors, separando capacidades
documentadas de desempenho comprovado; (5) estudo de evidência de
engenharia proveniente de repositórios, releases, branches, issues e
discussões; e (6) especificação de um programa experimental capaz de
validar as hipóteses no próprio harness. O documento usa referências
autor–ano clicáveis e classifica explicitamente cada tipo de
evidência.

## Abstract

Language-model agents increasingly execute long-running tasks that
combine reasoning, tool use, artifact manipulation, testing, delegation,
and human interaction. This produces potentially unbounded trajectories
over finite and cognitively imperfect context windows. Vendor-advertised
context length is not equivalent to reliable operational capacity:
Lost in the Middle, RULER, and NoLiMa show degradation with
context length, middle-positioned evidence, multiple facts, and
associative retrieval without lexical overlap Liu et al., 2024; Hsieh et al., 2024; Modarressi et al., 2025. Agentic workloads
add large tool outputs, stale results, failed-attempt interference,
governance loss during compaction, and cross-agent context pollution Cheng et al., 2026; Chen, 2026.

This document consolidates theory, recent empirical work, vendor
practices, and multi-agent harness patterns to address context
management in Overseer loops and subagents. It proposes a
vendor-agnostic Context Control Plane that externalizes
canonical state, performs object- and dependency-aware garbage
collection, retrieves and packs evidence according to attention
constraints, folds completed subtasks, applies typed compaction
profiles, validates post-compaction integrity, and resets and rehydrates
sessions at safe semantic boundaries. The central design principle is
that the Overseer persists as a logical role and external state,
not as an immortal model conversation.

Keywords: AI agents; multi-agent systems; context
engineering; context compaction; context folding; garbage collection;
agent memory; coding agents; long context; harness engineering.

## Sumário

Introdução

Questões de pesquisa e método

Modelo do problema: contexto físico, útil
e confiável

Taxonomia operacional

Arquitetura de memória e
estado

Overseer loop e ciclo de vida da
sessão

Subagentes: compactação interna e folding na
fronteira

Garbage collection de
contexto

Perfis de compactação

Context folding e gestão de
ramificações

Lost in the Middle e empacotamento
atento à posição

Comparação de vendors e modelos abertos

Lições de outros harnesses

Arquitetura proposta: Context Control
Plane

Perfis por papel e classe de
tarefa

Programa experimental

Segurança, governança e auditabilidade

Trade-offs, limitações e ameaças à
validade

Roadmap de implementação

Agenda de pesquisa aberta

Conclusões

Referências bibliográficas

# 1. Introdução

O modelo conversacional tradicional supõe uma sequência relativamente
curta de mensagens, na qual o histórico integral pode ser reenviado ao
modelo a cada turno. Um harness agêntico de longa duração rompe essa
suposição. Um Overseer pode:

ler constituições, regras e playbooks;

analisar um item do backlog;

planejar inline ou delegar a planejadores;

criar implementadores, pesquisadores e revisores;

acompanhar processos e ferramentas;

integrar resultados;

executar testes de unidade, integração e regressão;

corrigir falhas;

produzir commits e bookkeeping;

encerrar a tarefa e iniciar outra.

A trajetória resultante contém conteúdos heterogêneos, com ciclos de
vida diferentes:

instruções normativas;

objetivos e critérios de aceitação;

planos vigentes e planos substituídos;

tool calls e tool results;

conteúdos de arquivos disponíveis no workspace;

decisões e justificativas;

evidências de testes vinculadas a versões do código;

hipóteses ativas e rejeitadas;

transcripts de subagentes;

resultados externos voláteis;

estado de processos, containers e tarefas assíncronas;

memórias reutilizáveis entre sessões.

Tratar tudo isso como uma lista cronológica de mensagens produz três
erros arquiteturais. Primeiro, confunde contexto ativo
com estado persistente. Segundo, presume que toda
informação visível recebe atenção equivalente. Terceiro, transfere ao
modelo tarefas de controle de ciclo de vida que podem ser parcialmente
determinísticas.

MemGPT introduziu a analogia entre contexto de LLM e memória virtual:
uma área ativa limitada é alimentada por camadas externas maiores, e o
sistema movimenta informação entre níveis Packer et al., 2023. MemOS amplia essa
visão, tratando memória como recurso operacional com representação,
organização, governança e migração Li et al.,
2025. No domínio de coding agents, práticas recentes da OpenAI e da
Anthropic convergem para externalização do estado em arquivos, Git,
planos, listas de funcionalidades, logs de aceitação e checkpoints,
permitindo que novas sessões retomem o trabalho sem depender do
transcript integral OpenAI, 2025;
OpenAI, 2026d; Anthropic, 2026d.

A hipótese central deste documento é:

A confiabilidade de um harness multiagêntico de longa duração
depende menos de maximizar a quantidade de histórico na janela e mais de
governar o ciclo de vida de objetos de contexto, preservando estado
canônico, causalidade, autoridade e recuperabilidade.

Essa hipótese complementa o programa de pesquisa mais amplo do
projeto, que já separa working memory, session memory, run state,
project memory, experience store, policy memory e artifact history e
trata a trajetória como unidade de observabilidade e aprendizado Projeto Multi Agent Harness,
2026.

# 2. Questões de pesquisa e
método

## 2.1 Questões de pesquisa

RQ1. Qual deve ser o ciclo de vida da sessão do
Overseer ao executar repetidamente itens de backlog?

RQ2. Quando um agente deve realizar garbage
collection, folding, compactação semântica ou reset?

RQ3. Quais informações podem ser removidas da visão
ativa sem perda operacional e quais precisam ser pinadas?

RQ4. Como a política muda entre Overseer, subagentes
curtos, investigadores longos, implementadores e revisores?

RQ5. Perfis canônicos de compactação são inferiores
ou complementares a perfis adaptativos por tarefa e overlays gerados
on-the-fly?

RQ6. Como Lost in the Middle, interferência
de tentativas fracassadas e degradação de governança afetam a
organização do contexto?

RQ7. Quais mecanismos são expostos atualmente por
Codex, Claude Code, Kimi Code CLI, Gemini CLI e ecossistemas
abertos?

RQ8. Quais métricas e desenhos experimentais
permitem validar uma política de contexto sem confundir redução de
tokens com sucesso da tarefa?

## 2.2 Tipo de revisão

Este trabalho é uma revisão narrativa estruturada e
atualização rápida, não uma revisão sistemática PRISMA
completa. Foram priorizados:

artigos peer-reviewed sobre contexto longo e prompt
compression;

benchmarks reproduzíveis;

preprints de 2025–2026 diretamente relacionados a agentes de longa
duração;

documentação oficial de vendors;

repositórios e whitepapers de harnesses reproduzíveis;

documentação interna do projeto.

A evidência foi organizada em cinco níveis:

Nível | 
Evidência | 
Uso no documento | 

A | 
Artigos peer-reviewed, normas e resultados amplamente
reproduzidos | 
Fundamentos e restrições fortes | 

B | 
Benchmarks e artigos com código/dataset, ainda que preprint | 
Estado da arte operacional | 

C | 
Preprints recentes com avaliação clara | 
Bleeding edge e hipóteses experimentais | 

D | 
Documentação oficial de vendors e engineering blogs | 
Estado da prática | 

E | 
Whitepapers, repositórios e relatos de engenharia | 
Geração de hipóteses e padrões | 

Afirmações arquiteturais importantes são trianguladas, quando
possível, por: fundamento acadêmico, evidência experimental recente e
prática industrial.

## 2.3 Limites da comparação
cross-vendor

Não existe, até a data desta revisão, um benchmark independente
amplamente aceito que compare a qualidade das compactações nativas de
Claude Code, Codex, Kimi CLI e Gemini CLI mantendo constantes modelo,
prompt, trajetória, ferramenta e algoritmo. Assim, a comparação de
vendors neste documento distingue:

superfície de controle documentada;

comportamento observável do produto;

qualidade semântica da compactação, que deve ser
medida em benchmark próprio.

## 2.4 Estratégia
de busca e atualização do corpus

A atualização ampliada combinou quatro movimentos de busca. O
primeiro foi uma busca de fundamentos e benchmarks
consolidados, priorizando ACL Anthology, TACL, NeurIPS, ICLR e
OpenReview. O segundo foi uma busca de bleeding edge,
concentrada em arXiv e OpenReview para trabalhos de 2025–2026
diretamente relacionados a long-horizon agents, context folding,
execution-state memory, learned compaction e garbage collection. O
terceiro foi uma busca de estado da prática, baseada em
documentação oficial da OpenAI, Anthropic, Google, Moonshot AI e
LangChain. O quarto foi uma busca de evidência
operacional, cobrindo repositórios, branches, changelogs,
releases, issues e discussões que revelam falhas, workarounds e mudanças
ainda não refletidas em artigos formais.

A busca foi organizada em torno de famílias de termos:
("long-horizon agent" OR "long-running agent" OR "coding agent")
AND
("context compaction" OR "context folding" OR eviction
 OR "garbage collection" OR "working memory" OR "agent memory")
("Claude Code" OR Codex OR "Kimi CLI" OR "Gemini CLI")
AND
(compact OR compaction OR hooks OR subagents OR context)
("multi-agent harness" OR orchestrator OR overseer OR subagent)
AND
(ledger OR artifact OR checkpoint OR context OR memory)

Não se pretende afirmar exaustividade bibliométrica. A área teve
crescimento acelerado em 2025–2026, e vários dos mecanismos mais
próximos do problema — Self-GC, CWL, MAGE, CompactionRL e ConstraintRot
— ainda são preprints. A estratégia adotada é, portanto, uma
living review: cada afirmação é ligada à versão da
fonte usada; preprints são explicitamente rotulados; documentação de
vendor é tratada como descrição do produto e não como prova de
superioridade; e relatos de issues são usados para revelar classes de
falha, não para estimar incidência populacional.

## 2.5 Hierarquia prática da
evidência

A interpretação do corpus segue uma escala operacional:

Classe | 
Exemplo | 
O que permite concluir | 
O que não permite concluir | 

E1 — peer-reviewed | 
TACL, ACL, NeurIPS, ICLR | 
Fenômeno ou método passou por revisão formal; maior confiança
metodológica | 
Que o resultado se transfere automaticamente a todos os agentes e
vendors | 

E2 — benchmark reproduzível | 
RULER, ∞Bench, LongBench v2 | 
Compara modelos sob tarefas e métricas públicas | 
Que o benchmark representa integralmente coding agents reais | 

E3 — preprint com artefato | 
Self-GC, CWL, Context-Folding | 
Evidência direta e recente, frequentemente com código | 
Maturidade industrial ou replicação independente | 

E4 — documentação oficial | 
hooks, thresholds e context editing | 
O que a superfície do produto declara suportar | 
Qualidade semântica real da compactação | 

E5 — repositório/release/issue | 
little-coder, issues do Codex/Claude | 
Padrões de engenharia, falhas de integração e workarounds | 
Frequência geral, causalidade ou eficácia estatística | 

A regra de redação é: conclusões fortes exigem E1/E2 ou triangulação
de E3 com E4/E5; mecanismos E3 são apresentados como hipóteses
promissoras; problemas relatados em E5 são chamados de evidência
de campo, não de resultados científicos.

## 2.6 Corpus mínimo e corpus
estendido

O núcleo do corpus inclui Lost in the Middle, RULER, NoLiMa,
LongLLMLingua, LLMLingua-2, MemGPT, HiAgent, Magentic-One, SWE-agent e
MetaGPT. Esse núcleo fornece fundamentos para posição, capacidade
efetiva, prompt compression, memória hierárquica, ledgers, interface
agente–computador e artefatos tipados. O corpus estendido acrescenta
∞Bench, LongBench v2, MemGym, A-MEM, Context-Folding, FoldAct, U-Fold,
MAGE, Self-GC, CWL, ACON, SelfCompact, CompactionRL, ContextBudget e
Governance Decay. MemGym oferece uma direção específica para avaliar
memória em tarefas agênticas heterogêneas Xu
et al., 2026, enquanto surveys recentes organizam a evolução de
memória de agentes e ajudam a evitar uma leitura restrita a um único
mecanismo Luo et al., 2026. Esses
trabalhos formam o fronte atual de pesquisa em gestão ativa da
trajetória.

Do lado da engenharia, foram estudadas as superfícies oficiais de
Codex, Claude Code/Agent SDK, Kimi Code CLI, Gemini/ADK e Deep Agents,
além de repositórios como little-coder, ChatDev 2.0, MetaGPT, Agentless,
Pydantic AI Harness e implementações de agentes com offloading para
filesystem. Listas vivas como Awesome Memory for Agents e o
repositório de survey sobre long-context foram usadas como instrumentos
de descoberta, não como fontes finais de claims TsinghuaC3I, 2026; LCLM-Horizon, 2026. Essa
camada permite correlacionar mecanismos teóricos com decisões concretas
de runtime.

# 3. Modelo
do problema: contexto físico, útil e confiável

## 3.1 Quatro limites diferentes

### 3.1.1 Limite físico

É a quantidade máxima de tokens aceita pelo modelo ou API.
Ultrapassá-la causa erro, truncamento ou compactação automática.

### 3.1.2 Limite de recuperação

A informação pode estar fisicamente presente e ainda assim não ser
recuperada. Lost in the Middle demonstrou desempenho
tipicamente superior quando a evidência relevante aparece no início ou
no final, com degradação em posições intermediárias Liu et al., 2024.

### 3.1.3 Limite de utilização

Recuperar uma string não equivale a usar múltiplos fatos em
raciocínio. RULER expandiu o teste needle-in-a-haystack com
múltiplas agulhas, multi-hop tracing e agregação; muitos modelos
degradaram bem antes da janela nominal Hsieh
et al., 2024. NoLiMa removeu correspondências lexicais diretas entre
pergunta e evidência e mostrou perdas importantes já em 32 mil tokens Modarressi et al., 2025.

### 3.1.4 Limite de interferência

Conteúdo presente pode piorar o resultado. Contextual Drag
encontrou quedas de 10% a 20% quando tentativas fracassadas permanecem
no contexto e induzem novas trajetórias estruturalmente semelhantes aos
erros anteriores Cheng et al.,
2026. Esse fenômeno é particularmente relevante em loops de
correção, nos quais logs, patches rejeitados e diagnósticos incorretos
são mantidos como narrativa extensa.

## 3.2 Limite operacional

O harness deve derivar um limite operacional, e não usar diretamente
a janela anunciada:
hard_limit = janela configurada pelo vendor

safe_physical_limit =
 hard_limit
 - reserva de saída
 - reserva de tool results
 - overhead de instruções e schemas
 - margem de recuperação

reliable_attention_limit =
 maior tamanho em que o modelo mantém desempenho aceitável
 no benchmark posicional e agêntico do harness

operational_limit = min(safe_physical_limit, reliable_attention_limit)

O valor deve variar por:

modelo e snapshot;

vendor/CLI;

classe da tarefa;

tipo dos artefatos;

quantidade de tools;

idioma;

necessidade de resposta longa;

perfil de retrieval;

política de compactação.

## 3.3 Contexto como cache
cognitiva

O contexto ativo deve ser tratado como uma cache ou visão
materializada:
Estado canônico externo
 ├── Git e workspace
 ├── task ledger
 ├── progress ledger
 ├── decision records
 ├── evidence store
 ├── trajectory store
 ├── artifact store
 └── memory store
 ↓
Context builder / packer
 ↓
Janela ativa do modelo

A janela é descartável; o estado não.

## 3.4 O que os benchmarks
realmente medem

Um erro recorrente em discussões de contexto é usar um único teste de
recuperação literal como proxy de capacidade operacional. Lost in
the Middle mede sensibilidade à posição e mostra curvas
frequentemente em U: início e fim recebem uso mais confiável que o meio
Liu et al., 2024. RULER acrescenta tarefas
de múltiplas agulhas, agregação e tracing, revelando que a janela
efetiva cai conforme a tarefa exige manter relações distribuídas Hsieh et al., 2024. NoLiMa reduz pistas
lexicais e força recuperação associativa, aproximando-se de casos em que
uma decisão arquitetural precisa ser relacionada a um erro sem
compartilhar os mesmos termos Modarressi et
al., 2025.

∞Bench estende a avaliação além de 100 mil tokens e inclui tarefas de
retrieval, QA, sumarização, código e raciocínio Zhang et al., 2024. LongBench v2
introduz problemas mais difíceis e realistas, com dependências longas e
necessidade de síntese Bai et al.,
2025. Esses benchmarks mostram que “aceitar N tokens” e “usar N
tokens” são propriedades diferentes. Para harnesses, ainda há uma lacuna
adicional: os benchmarks tradicionais raramente incluem tool calls,
versões de arquivos, side effects, múltiplos agentes e compactações
repetidas.

Por isso, o benchmark interno deve medir quatro dimensões
separadas:

Dimensão | 
Pergunta | 
Exemplo no harness | 

Recuperação | 
O modelo encontra o fato? | 
Recuperar uma restrição antiga | 

Atribuição | 
Liga o fato ao objeto correto? | 
Associar teste ao commit correspondente | 

Utilização | 
Aplica corretamente o fato? | 
Não alterar API pública durante refactor | 

Continuidade | 
Mantém a regra após tools/compactação? | 
Preservar constraint após três fases | 

## 3.5 Taxonomia
ampliada de falhas de contexto

### 3.5.1 Diluição

A informação correta permanece na janela, mas compete com dezenas de
itens semanticamente próximos. A diluição aparece quando todos os fatos
são “relevantes” em algum sentido, porém poucos são úteis para a próxima
decisão. Retrieval sem reranking e memória histórica monolítica agravam
o problema.

### 3.5.2 Obsolescência e
mistura temporal

Um teste realizado no commit A não deve orientar a
decisão sobre o commit B como se ainda fosse atual. A
trajetória linear, se não carrega versionamento, transforma recência
conversacional em falsa atualidade operacional. Cada evidência precisa
de artifact_version, commit,
timestamp e relação de supersession.

### 3.5.3 Contaminação
por tentativa fracassada

Contextual Drag sugere que exemplos de falha permanecem como
padrões disponíveis e podem enviesar a próxima tentativa Cheng et al., 2026. A solução não é
simplesmente apagar toda falha: falhas úteis devem ser convertidas em
memória negativa tipada — claim rejeitado, evidência e condição que
permitiria reconsiderá-lo —, enquanto detalhes mecânicos podem ser
externalizados.

### 3.5.4 Perda de autoridade

Governance Decay/ConstraintRot testa um risco específico: restrições
presentes no contexto original podem desaparecer ou perder saliência
depois de compactação. No benchmark reportado, violações subiram de 0%
com policy integral para 30% após compaction, chegando a 59% em algumas
famílias; constraint pinning eliminou as violações naquele
conjunto Chen, 2026. Por ser
preprint, o número não deve ser universalizado, mas o mecanismo é
suficientemente plausível para justificar uma regra arquitetural forte:
governança não pertence ao heap compactável.

### 3.5.5 Corrupção do
protocolo de ferramentas

Providers frequentemente exigem pares válidos de
tool_call e tool_result. Trimming arbitrário
pode deixar uma chamada sem resultado ou remover metadados necessários à
reconstrução. GC deve operar sobre spans atômicos e usar adapters de
protocolo.

### 3.5.6 Deriva por resumo
sucessivo

Se cada compactação usa somente o resumo anterior, a representação
passa por uma cadeia de transformações lossy. O risco cresce quando o
resumo é narrativo e não possui referências para fontes brutas. A
política proposta usa checkpoints estruturados, arquivo reversível e,
quando possível, regenera resumos a partir do estado canônico e da
trajetória original, não apenas do último resumo.

### 3.5.7
Ansiedade de contexto e encerramento prematuro

A discussão de context engineering da Anthropic enfatiza
seleção, estrutura e externalização como problemas centrais, e não
apenas o tamanho bruto da janela Anthropic, 2026e.
Engineering reports da Anthropic descrevem agentes que, ao perceber
pressão de contexto, abreviam tarefas ou tentam “concluir” cedo. Mesmo
que o conceito não seja um construto científico padronizado, ele
descreve uma falha operacional observável: o modelo passa a otimizar a
sobrevivência da sessão em vez do objetivo da tarefa Anthropic, 2026d. O harness
deve esconder parte dessa pressão por meio de checkpoints automáticos e
resets previsíveis.

## 3.6
Contexto longo como sistema parcialmente observável

Um agente de longa duração opera em um ambiente parcialmente
observável. O mundo real — repositório, serviços, backlog, processos,
decisões humanas — é maior que a janela. A cada turno, o harness monta
uma observação. Context engineering, portanto, é uma política de
observação: decide que estado revelar, com qual granularidade e em que
ordem. Esse enquadramento aproxima o problema de state estimation e
memory management, não apenas de prompt writing.

A-MEM e MemOS representam a tendência de tratar memória como sistema
com operações de escrita, organização, recuperação, fusão e descarte, em
vez de um vetor estático Xu et al., 2025;
Li et al., 2025. HiAgent, por sua vez, usa
subobjetivos como unidades de working memory e resume proativamente
partes concluídas; em ACL 2025, reportou ganhos substanciais de sucesso
e redução de passos em tarefas long-horizon Hu et al., 2025. Esses trabalhos sustentam
a ideia de que a unidade de memória deve acompanhar a estrutura da
tarefa.

# 4. Taxonomia operacional

Os termos abaixo não devem ser usados como sinônimos.

Operação | 
Definição | 
Perda semântica esperada | 
Reversibilidade | 

Trimming | 
Retira mensagens ou partes por regra simples | 
Baixa a alta | 
Geralmente baixa | 

Offloading | 
Move payload para storage e deixa referência | 
Nenhuma, se byte-exact | 
Alta | 

Garbage collection | 
Remove da visão ativa objetos desnecessários, duplicados,
persistidos ou sem dependências vivas | 
Baixa | 
Média/alta | 

Masking | 
Preserva estrutura, metadados e extremidades, ocultando conteúdo
repetitivo | 
Baixa | 
Alta se houver sidecar | 

Folding | 
Fecha uma unidade causal ou subtarefa e a substitui por resultado
condensado | 
Baixa/média | 
Alta se referenciada | 

Compactação | 
Reescreve história em representação menor, normalmente por LLM | 
Média/alta | 
Baixa sem archive | 

Reset | 
Encerra sessão e cria outra a partir de checkpoint | 
Depende do checkpoint | 
Alta | 

Promoção de memória | 
Transforma aprendizado validado em memória reutilizável | 
Não é redução da mesma sessão | 
Auditável | 

Deletion | 
Remove permanentemente do storage | 
Total | 
Nenhuma | 

A ordem de preferência é:
offloading e GC determinístico
 ↓
retrieval e repacking
 ↓
folding de unidades concluídas
 ↓
compactação semântica
 ↓
reset e reidratação

A compactação é mais custosa e arriscada que GC porque cria uma nova
interpretação do passado. LongLLMLingua e LLMLingua-2 demonstram que
compressão seletiva pode melhorar densidade de informação e reduzir
custos, mas seus objetivos são prompt compression e não preservação
completa de estado agêntico, causalidade e side effects Jiang et al., 2024; Pan et al., 2024.

# 5. Arquitetura de memória e
estado

## 5.1 Camadas

Working memory
 últimas observações, hipótese atual, próxima ação

Session memory
 resumo e índices necessários durante a sessão

Run state
 estado formal da execução e do workflow

Task state
 contrato, critérios, progresso e evidências da tarefa

Project memory
 fatos e procedimentos validados do repositório

Experience store
 trajetórias, sucessos, falhas e resultados de eval

Policy memory
 constituição, permissões, invariantes e versões

Artifact history
 commits, patches, logs, relatórios, documentos e outputs

Essas camadas possuem políticas de retenção e autoridade diferentes.
Misturá-las em um único “resumo da conversa” destrói distinções
essenciais.

## 5.2 Task Ledger e Progress
Ledger

O padrão de Magentic-One, no qual o Orchestrator mantém planejamento
e acompanhamento do progresso e replana ao detectar falhas, inspira a
separação entre estado relativamente estável e estado volátil Fourney et al., 2024.

### Task Ledger

objetivo;

critérios de aceitação;

restrições;

fatos confirmados;

plano macro;

riscos;

dependências;

definição de conclusão.

### Progress Ledger

fase corrente;

responsável;

último resultado;

artefatos modificados;

jobs ativos;

testes atuais;

blockers;

número de stalls;

próxima ação.

O Task Ledger é atualizado menos frequentemente. O Progress Ledger
pode ser reconstruído após quase toda ação.

## 5.3 Trajectory Store

O trajectory store é append-only e contém a história completa:

trajectory_event:
 run_id:
 task_id:
 node_id:
 agent_id:
 event_type:
 timestamp:
 inputs: []
 outputs: []
 artifact_refs: []
 policy_decisions: []
 parent_events: []
 model:
 token_metrics: {}

GC e compactação não devem apagar automaticamente essa fonte de
auditoria. Eles apenas alteram a visão ativa.

## 5.4 Context Object Model

context_object:
 id: tool:bash:0188
 type: tool_result

 owner:
 run_id: run-82
 task_id: TASK-184
 agent_id: implementer-04

 authority:
 level: observation
 source: tool

 lifecycle:
 state: live
 generation: young
 collection_count: 0

 dependencies:
 depends_on: []
 referenced_by: []

 persistence:
 persisted: true
 artifact_ref: artifact://logs/bash-0188.txt
 byte_exact_recovery: true

 semantics:
 unique_evidence: false
 unresolved: false
 superseded_by: null

 gc:
 pinned: false
 preferred_action: fold
 earliest_safe_boundary: after_tool_cycle

Esse modelo permite decisões por objeto, não por posição
cronológica.

## 5.5 Estado
canônico, eventos e visões materializadas

A arquitetura proposta distingue três registros:

Event log/trajectory store: append-only, registra o
que aconteceu;

State stores: mantêm o estado atual de task,
artifacts, agents e policies;

Context views: projeções descartáveis montadas para
uma inferência ou fase.

Essa separação evita usar a narrativa do modelo como fonte de
verdade. Um evento de teste, por exemplo, registra comando, commit,
ambiente e artifact; o ProgressLedger aponta qual execução
é vigente; o context packer mostra ao modelo apenas o resumo da execução
vigente e referências para as demais.

trajectory_event:
 event_id: evt-007142
 run_id: run-184
 task_id: TASK-184
 agent_id: implementer-3
 type: test_run_completed
 occurred_at: 2026-07-26T18:23:14-03:00
 repository:
 commit: a81d4c2
 dirty: false
 payload_ref: artifact://tests/run-884.json
 summary:
 status: failed
 failing_tests:
 - PaymentServiceIT.shouldRollback
 provenance:
 tool_call_id: tool-337
 policy_version: policy-12

A visão ativa é recomposta:
Task contract
+ current progress state
+ latest valid evidence
+ active hypotheses
+ selected historical episodes
+ next action contract

### 5.5.1 Por que não
basta um arquivo 
### summary.md

Um único resumo mistura fatos de autoridade, estado volátil, decisões
e narrativa. Ele não permite saber facilmente se um teste foi
substituído, se uma hipótese foi rejeitada ou se uma regra veio do
usuário. A representação deve ter tipos, versões e referências.

### 5.5.2
Proveniência como requisito de compactação

Cada campo compactado deve ser ligado a fontes. Uma decisão sem
evidence_refs é uma afirmação do compressor; uma decisão
com referências pode ser auditada e reidratada. Esse princípio também
reduz o problema de resumos hierárquicos: um resumo de subagente pode
apontar diretamente para artefatos originais, evitando “resumo de resumo
de resumo” sem acesso à base.

## 5.6
Memória episódica, factual, procedimental e normativa

Tipo | 
Exemplo | 
Política de retenção | 

Episódica | 
“Tentativa X falhou no commit A” | 
Decaimento; útil para diagnóstico e replay | 

Factual | 
“O módulo usa PostgreSQL 17” | 
Validar contra fonte atual; invalidar por versão | 

Procedimental | 
“Rodar schema validation antes dos testes” | 
Promover após repetição/validação | 

Normativa | 
“Não alterar API pública” | 
Pinada; somente autoridade explícita altera | 

Negativa | 
“Hipótese H foi rejeitada por E” | 
Preservar enquanto a classe de problema for relevante | 

A memória normativa não pode ser inferida por frequência. Uma regra
humana vale por autoridade, não por quantas vezes foi observada. A
memória procedimental, ao contrário, pode nascer de experiências
repetidas, mas exige confirmação para evitar cristalizar um workaround
temporário.

## 5.7 Memória por
projeto e isolamento multiagente

A recuperação deve respeitar escopo:
organization memory
 ↓ políticas e convenções gerais
project memory
 ↓ arquitetura e rotinas do repositório
run memory
 ↓ decisões desta execução
task memory
 ↓ estado do item atual
agent working memory
 ↓ observação necessária para o próximo passo

Subagentes não recebem automaticamente memória organizacional
integral. O planner pode precisar de ADRs e roadmap; o test runner
precisa de comandos e ambiente; o reviewer precisa de invariantes e
diff. O context compiler aplica least context privilege: a
mesma lógica de menor privilégio usada em segurança, aplicada à
exposição de informação.

# 6. Overseer loop e
ciclo de vida da sessão

## 6.1 Entidade lógica
versus sessão física

O Overseer deve persistir como:

identidade de role;

políticas e permissões;

métricas acumuladas;

histórico de decisões;

memória validada;

ownership da tarefa;

estado no workflow.

Ele não precisa persistir como uma única conversa do modelo.
Overseer lógico
 ├── sessão física da Task A
 ├── sessão física da Task B
 └── sessão física da Task C

A regra recomendada é:

Cada item relevante do backlog começa em contexto novo.
Compactação é uma estratégia intra-task; não é o mecanismo principal
para arrastar dezenas de tarefas na mesma sessão.

Essa decisão é coerente com práticas de longa duração documentadas
pela OpenAI e Anthropic, que externalizam planos, requisitos, Git e
progresso para permitir retomada por sessões novas OpenAI, 2025; OpenAI, 2026d; Anthropic, 2026d.

## 6.2 Loop operacional

claim backlog item
 ↓
criar Task Ledger e sessão nova
 ↓
hidratar constituição, playbooks e estado mínimo
 ↓
planejar ou delegar
 ↓
executar / integrar / revisar
 ↓
GC incremental e folding de unidades concluídas
 ↓
testes de integração e regressão
 ↓
commit ou rollback
 ↓
completion capsule + bookkeeping
 ↓
promoção de memórias candidatas
 ↓
encerrar sessão física
 ↓
próximo item

## 6.3 Hidratação mínima

O contexto inicial deve conter:

constituição efetiva e políticas aplicáveis;

role e escopo do Overseer;

task contract;

critérios de aceitação;

estado atual do repositório;

playbooks selecionados;

dependências e decisões relevantes;

memórias recuperadas especificamente;

índice de evidências e artefatos;

próxima ação ou fase inicial.

Não deve conter, por padrão:

transcripts das tarefas anteriores;

todos os playbooks;

todo o backlog;

logs antigos;

mensagens de status;

resultados substituídos;

todas as memórias semanticamente similares.

## 6.4 Checkpoint canônico

checkpoint:
 task_id:
 objective:
 acceptance_criteria: []
 active_constraints: []
 current_phase:

 repository:
 branch:
 base_commit:
 head_commit:
 dirty_files: []

 decisions:
 - decision:
 rationale:
 evidence_refs: []

 completed_work: []
 remaining_work: []
 modified_artifacts: []

 tests:
 latest_per_suite: []
 unresolved_failures: []
 artifact_refs: []

 active_agents: []
 unresolved_questions: []
 rejected_hypotheses: []
 risks: []
 next_action:

 provenance:
 trajectory_id:
 source_event_range:
 policy_versions: []

## 6.5 Completion Capsule

Ao final:

completion:
 task_id:
 final_status:
 acceptance_criteria_results: []
 commits: []
 changed_files: []
 test_evidence: []
 known_limitations: []
 follow_up_tasks: []
 rollback_instructions:
 trajectory_ref:

A sessão é encerrada após commit, bookkeeping e persistência do
capsule.

# 7.
Subagentes: compactação interna e folding na fronteira

## 7.1 Duas fronteiras
diferentes

### Compactação interna

Permite ao subagente continuar uma tarefa que cresce além do
orçamento.

### Folding pai–filho

Protege o contexto do Overseer. Mesmo que o subagente não compacte
internamente, sua trajetória deve ser condensada ao retornar ao pai.

Codex e Claude documentam subagentes em threads/contextos isolados,
com resultados resumidos retornando ao contexto principal, evitando que
exploração, logs e tool calls contaminem a conversa do orquestrador OpenAI, 2026c; Anthropic, 2026c.

## 7.2 Classes de subagentes

### S0 — Atômico

Características:

poucas tools;

um objetivo simples;

resultado curto;

duração muito abaixo do limite operacional.

Política:
sem compactação semântica mid-task
GC de outputs grandes
fold final obrigatório
sessão destruída

### S1 — Focado

Exemplos: revisão de um módulo, investigação de uma falha,
levantamento de dependências.

Política:
minor GC contínua
offloading de logs e arquivos
preservar caminho investigativo ativo
compactar somente sob pressão real
fold final tipado

### S2 — Multifásico

Exemplos: planejar, implementar, testar e revisar uma mudança
delimitada.

Política:
checkpoint por fase
fold de fase concluída
manter fase atual em alta fidelidade
reset opcional entre fases
fold final ao Overseer

### S3 — Longa duração

Características:

múltiplas fases;

muitos módulos;

sub-subagentes;

várias compactações previstas.

Política:
re-decompor em workflow próprio
ou
checkpoint + reset + continuação

Se um subagente precisa de três ou mais compactações sem se aproximar
da conclusão, o harness deve emitir
DELEGATION_TOO_COARSE.

## 7.3 Não compactar raciocínio
aberto

Enquanto uma investigação não estiver causalmente fechada,
preservar:

active_investigation:
 hypothesis:
 supporting_evidence: []
 contradicting_evidence: []
 missing_evidence: []
 confidence:
 next_probe:

Compactar prematuramente pode transformar incerteza em falsa
conclusão. MAGE evita esse problema ao derivar o estado ativo do caminho
raiz–nó corrente, resumindo subobjetivos concluídos e isolando
ramificações erradas Chen et al., 2026.
Context-Folding abre uma subtrajetória e a dobra na conclusão da
subtarefa Sun et al., 2025.
SelfCompact também orienta o agente a compactar quando um subproblema se
resolveu ou a trajetória converge, e a evitar compactação no meio de uma
derivação Li et al., 2026.

## 7.4 Contrato de retorno

subagent_result:
 task_id:
 subtask_id:
 role:
 status: completed | partial | blocked | failed

 objective:
 conclusion:
 requirements_checked: []

 work_performed:
 files_read: []
 files_changed: []
 commands_executed: []

 decisions:
 - decision:
 rationale:
 evidence_refs: []

 findings: []

 tests:
 commit:
 executed: []
 passed: []
 failed: []
 artifact_refs: []

 rejected_hypotheses: []
 unresolved_questions: []
 risks: []
 recommended_next_action:
 confidence:
 raw_trajectory_ref:

O pai recebe o capsule; o transcript permanece recuperável.

## 7.5 Subagentes recursivos

Cada nível dobra seus próprios filhos:
Overseer
 └── Implementer
 ├── Repository Explorer
 ├── Test Analyzer
 └── Database Specialist

Evitar resumo de resumo sem fonte. Cada claim deve apontar
diretamente para evidência original.

## 7.6
Evidência comparativa: sem compactação, compactação mid-task e
folding

Não há ainda um benchmark dominante que isole apenas a variável
“compactar ou não compactar um coding subagent no meio da task”. A
evidência é indireta, mas convergente. Context-Folding compara
ramificações procedurais dobradas com ReAct e summarization tradicional
e reporta contexto ativo até dez vezes menor, com desempenho igual ou
superior em tarefas de pesquisa e software Sun et al., 2025. MAGE mantém o
caminho ativo e comprime subobjetivos concluídos, reportando ganhos de
sucesso e redução de tokens Chen et al.,
2026. HiAgent também organiza memória por subobjetivos, em vez de
intervalos fixos Hu et al., 2025.

Esses resultados não provam que toda compactação mid-task seja
melhor. Eles sustentam uma hipótese mais restrita:

compactar unidades semanticamente concluídas é mais seguro do
que compactar a trajetória ativa por idade ou threshold
isolado.

### 7.6.1 Quando não compactar

Um subagente atômico, com poucas tools e conclusão previsível, tende
a perder mais com o overhead de um resumo do que ganha em economia.
Nesses casos, offloading e truncamento tipado de tool outputs são
suficientes.

### 7.6.2 Quando compactar
mid-task

A compactação torna-se justificável quando:

há uma fronteira de subobjetivo;

o estado produzido já está persistido;

o resultado pode ser representado em schema;

o contexto projetado cruza o limite confiável;

a task continuará por várias etapas;

a continuidade depende de poucas invariantes bem identificadas.

### 7.6.3 Quando resetar

Reset é preferível quando o working set muda radicalmente, o agente
acumulou múltiplos resumos, há contradições persistentes ou a task já se
transformou em workflow multifásico. O reset não implica perda se o
estado canônico foi externalizado.

## 7.7
Delegação como contrato, não como mini-prompt informal

Cada delegação deve declarar:

delegation_contract:
 id: del-491
 parent_agent: overseer-1
 child_role: security-reviewer
 objective: "Revisar autenticação e autorização do diff atual"
 scope:
 commits: [a81d4c2]
 paths: ["src/auth/**"]
 constraints:
 - read_only
 - no_network
 expected_artifacts:
 - finding_ledger
 completion_criteria:
 - all_changed_auth_paths_reviewed
 return_schema: subagent_result/v2

Essa estrutura reduz a necessidade de transmitir o contexto completo
do pai. Também permite medir se o subagente terminou o que recebeu.

## 7.8 Folding recursivo e
perda cumulativa

Em árvores de subagentes, cada pai dobra os resultados dos filhos.
Para evitar perda cumulativa:

cada claim deve ter ID estável;

cada claim deve apontar para evidência original;

resumos intermediários não substituem artifacts;

o Overseer pode recuperar um fragmento da trajetória de qualquer
descendente;

conflitos entre filhos entram em ledger, não são resolvidos
silenciosamente pelo compactador.

raw child evidence ───────────────┐
 ↓ │
child capsule │
 ↓ │
parent synthesis │
 ↓ │
overseeer decision ◄──────────────┘ retrieval direto

## 7.9 Modelos pequenos e
microgerenciamento

Modelos pequenos devem receber tarefas menores, schemas mais rígidos
e menos liberdade para decidir o que esquecer. O little-coder é
evidência de engenharia relevante: o projeto usa budgets específicos,
skill injection seletiva, guardas de escrita/edição, watchdog de
contexto e compactação mid-run. Seu changelog mostra que não bastava
disparar a compactação; versões posteriores precisaram garantir que o
loop retomasse e medir se a compactação realmente liberou contexto. Isso
revela uma propriedade importante: context management é parte da state
machine, não um comando lateral Inbar, 2026a; little-coder changelog,
2026.

A evidência do little-coder não constitui ablação científica de cada
mecanismo. O whitepaper reporta forte ganho do mesmo modelo sob outro
scaffold, mas reconhece limitações de causalidade e transferência Inbar, 2026b. A lição
segura é que scaffold, ferramentas, budgets e context policy podem ser
variáveis de primeira ordem, principalmente em modelos menores.

# 8. Garbage collection de
contexto

## 8.1 Definição

Garbage collection de contexto é o controle de ciclo de vida de
objetos na visão ativa. Não significa apagar o trajectory store;
significa retirar da janela aquilo que não precisa continuar
presente.

Self-GC formaliza esse problema como gestão de objetos indexados e
recuperáveis, com operações de fold, mask e
prune, planejamento lateral e enforcement pelo harness Hao et al., 2026. CWL propõe episódios
tipados e ligados por dependências, com eviction determinística de ações
cujos efeitos já estão persistidos Semenov e
Dorofeev, 2026.

## 8.2 Critério de elegibilidade

Um objeto é candidato quando:
nenhuma ação futura conhecida depende dele
+
seu efeito está persistido
+
não é evidência única
+
não possui autoridade normativa
+
não representa side effect aberto
+
é recuperável ou regenerável

Idade não basta.

## 8.3 O que remover da visão
ativa

### Tool outputs persistidos

logs salvos;

conteúdo de arquivos disponíveis no workspace;

resultados de build transformados em relatório;

respostas de APIs arquivadas;

diffs recuperáveis pelo Git.

### Duplicatas

leituras repetidas do mesmo arquivo no mesmo commit;

listagens iguais;

mensagens de erro idênticas;

playbooks repetidos;

documentos semanticamente redundantes.

### Resultados superseded

teste de commit anterior;

plano substituído;

diff anterior ao patch mais recente;

snapshot de estado já atualizado;

relatório de revisão para versão antiga.

### Episódios concluídos

tool protocol de edição cujo efeito está no Git;

exploração que gerou um mapa estruturado;

subagente concluído;

polling de processo já terminado;

plano já aceito e externalizado.

### Skills e tools fora de fase

Schemas de ferramentas e playbooks devem ser progressivamente
carregados, não permanentemente mantidos.

## 8.4 O que pinamos

system/developer instructions;

constituição e políticas;

instruções humanas;

objetivo e critérios;

restrições;

side effects abertos;

hipótese ativa;

evidência conflitante não resolvida;

última execução válida de testes;

próxima ação;

rollback pendente.

Governance Decay mostra que compactações podem eliminar
restrições de segurança e elevar violações; o trabalho propõe pinning de
constraints fora da sumarização lossy Chen, 2026. Mesmo sendo preprint,
a consequência arquitetural é forte: governança não deve estar no heap
coletável.

## 8.5 Mark-and-sweep agêntico

### Roots

governance roots
 políticas e instruções

task roots
 objetivo, critérios, restrições

execution roots
 plano ativo, jobs, side effects

reasoning roots
 hipóteses e perguntas abertas

evidence roots
 evidências usadas por decisões vivas

### Mark

Percorrer dependências:
próxima ação
 → plano atual
 → decisão D12
 → test-run-44
 → commit a18f2

### Sweep

Classificar objetos não marcados:
RECOVERABLE → fold/offload
STRUCTURAL → mask
OBSOLETE → prune
UNCERTAIN → retain
AUTHORITY → pin

## 8.6 GC geracional

### Geração 0 — efêmera

Tool outputs, file reads, search results, polling e scratch. Minor GC
após tool cycles.

### Geração 1 — fase

Planos locais, resultados parciais, hipóteses e testes. Coleta em
fronteiras de subobjetivo.

### Geração 2 — tarefa

Task contract, decisões e latest validated state. Folding ao final da
tarefa.

### Pinned generation

Policies, user corrections e trust boundaries. Não coletável
automaticamente.

## 8.7 Triggers

POST_TOOL_RESULT
POST_FILE_READ
POST_TEST_RUN
POST_SUBAGENT_RESULT
SUBGOAL_COMPLETED
PHASE_COMPLETED
PRE_MODEL_CALL
PRE_COMPACTION
PRE_RESET
TASK_COMPLETED

O trigger deve usar projeção:
projected_next_context =
 active_tokens
 + expected_tool_result
 + expected_model_output
 + reserve

ContextBudget formula a decisão de compressão como problema
sequencial sob orçamento, permitindo agir antes do overflow Wu et al., 2026.

## 8.8 Fold, mask e prune

### Fold

Move o payload exato para sidecar e deixa ponteiro. Preferido quando
pode haver recuperação literal.

### Mask

Mantém estrutura, URL, título, início/fim e trechos relevantes.

### Prune

Retira integralmente da visão ativa. Só quando obsolescência e
ausência de dependências estiverem demonstradas.

Regra conservadora:
fold > mask > prune

## 8.9 Cache-aware GC

Alterar o prefixo pode invalidar prompt caches. A decisão deve
considerar:
benefício esperado =
 chamadas futuras × tokens removidos
 - custo da quebra de cache
 - custo do collector
 - custo de recuperação futura

A API da Anthropic expõe context editing com limpeza de tool results
e parâmetros de volume mínimo a remover, refletindo esse trade-off Anthropic, 2026b.

## 8.10 Correção de protocolo

Tool call e tool result formam spans atômicos. O collector não pode
quebrar a sequência exigida pelo provider. Operações válidas:

reter o span;

substituir o result por pointer válido;

normalizar call/result;

remover o span completo em fronteira segura.

## 8.11
Garbage collection orientado a objetos versus trimming cronológico

Trimming cronológico responde “quais mensagens são mais antigas?”. GC
orientado a objetos responde “quais objetos ainda são alcançáveis a
partir do estado vivo?”. Essa diferença é central. Uma constraint antiga
pode permanecer viva; um log de cinco segundos atrás pode ser
descartável após ser persistido e parseado.

Self-GC propõe indexar objetos e permitir ações como
fold, mask e prune, com planner e
enforcement do harness. O trabalho reporta reduções significativas de
tokens com taxas de no-impact superiores a heurísticas simples,
embora seja preprint e use avaliação por judge em parte dos experimentos
Hao et al., 2026. CWL adota episódios
tipados e dependências explícitas, com eviction determinística sem LLM;
reporta 89 tarefas sequenciais e 80 milhões de tokens processados sem
degradação mensurável frente a sessões isoladas Semenov e Dorofeev, 2026. Ambos sustentam o
deslocamento de “mensagens” para “objetos de contexto”.

## 8.12 Minor GC, major GC e
final GC

### Minor GC

Executado frequentemente, idealmente sem LLM:

offload de outputs grandes;

deduplicação por hash;

remoção de polling repetitivo;

substituição de conteúdo de arquivo por
path + commit + symbols;

preservação de pares de tool protocol;

atualização de latest e relações
superseded_by.

### Major GC

Executado em fronteiras:

varredura de dependências;

folding de fases concluídas;

normalização de resultados de subagentes;

conversão de hipóteses rejeitadas em memória negativa;

avaliação de cache economics;

preparação para compactação ou reset.

### Final GC

Executado no fechamento da task:

completion capsule;

promoção de memórias candidatas;

encerramento de processos/leases;

arquivamento da trajetória;

destruição da sessão física.

## 8.13 Economia de
cache e momento do commit

GC pode quebrar prefix caches. Uma pequena remoção pouco antes do fim
da task pode custar mais que economiza. Anthropic expõe parâmetros para
só limpar quando o volume removido justifica a invalidação e permite
preservar tools específicas Anthropic, 2026b. Self-GC
também considera a economia esperada antes de aplicar planos Hao et al., 2026.

O harness pode estimar:
net_value(gc_plan) =
 expected_future_calls × tokens_removed × token_cost
 - collector_cost
 - cache_rebuild_cost
 - expected_retrieval_cost
 - risk_penalty

A função não precisa ser monetariamente perfeita. Ela serve para
impedir coleta nervosa a cada pequena oportunidade.

## 8.14 Segurança contra
coleta maliciosa

Conteúdo não confiável pode tentar instruir o agente a classificar
uma policy como obsoleta ou um log como irrelevante. O collector não
deve executar instruções encontradas nos objetos. Ele opera sobre
metadados e políticas compiladas. Conteúdo de repositório, páginas web e
outputs de tools recebem trust_tier; somente fontes
autorizadas podem alterar pinned, authority ou
retenção normativa.

## 8.15 GC de recursos não
textuais

O mesmo lifecycle manager deve abranger:

worktrees;

sandboxes;

containers;

processos;

portas;

locks;

arquivos temporários;

sessões de browser;

downloads parciais;

leases de workers.

Context GC e runtime GC compartilham IDs de task e ownership. Um
processo ativo é uma root; quando o task termina, o final GC pode
encerrá-lo ou transferir ownership. Essa correlação evita “memória
limpa, runtime vazando”.

# 9. Perfis de compactação

## 9.1 Perfil genérico

Mesma política para todas as tarefas:
preservar instruções
resumir mensagens antigas
manter últimas mensagens
remover outputs extensos

LLMLingua-2 representa uma abordagem task-agnostic, extractive e
eficiente, útil como baseline e compressor geral Pan et al., 2024.

Vantagens: portabilidade, baixo custo,
comparabilidade.

Limitações: cegueira à semântica operacional, decisões
e causalidade.

## 9.2 Perfil query-aware

LongLLMLingua usa relevância para a consulta, compressão
coarse-to-fine e reordenação de documentos para aumentar a densidade de
informação importante Jiang et al.,
2024. Em agentes, a “query” pode ser a próxima decisão ou ação.

Risco: remover algo aparentemente irrelevante agora, mas necessário
depois.

## 9.3 Perfil específico por
tarefa

Cada classe possui estado essencial diferente.

### Coding

branch e commits;

arquivos e símbolos alterados;

critérios;

decisões;

último teste por suite;

failures ativos;

patches rejeitados;

próxima ação.

### Pesquisa

perguntas;

claims;

fontes favoráveis e contrárias;

nível de evidência;

lacunas;

conclusões provisórias.

### Incidente

timeline;

sistemas afetados;

intervenções;

hipótese vigente;

hipóteses rejeitadas;

estado de rollback.

## 9.4 Perfil adaptativo ao
conteúdo

A intensidade varia conforme a densidade informacional:
logs duplicados → agressivo
decisões conflitantes → conservador
arquivo persistido → offload
rationale sem artefato externo → preservar narrativa

## 9.5 Perfil aprendido

ACON otimiza guidelines de compressão a partir de pares em que
contexto completo funciona e compactado falha, e destila o compressor em
modelos menores Kang et al., 2025.
ContextBudget aprende decisões de quando e quanto comprimir sob
restrições Wu et al., 2026. NGC
aprende a evictar entradas de KV cache conjuntamente com raciocínio Li et al., 2026.

Esses métodos sugerem que políticas podem ser aprendidas, mas ainda
são bleeding edge e não substituem validação determinística.

## 9.6 Compactação on-the-fly

Três níveis:

seleção dinâmica de perfil canônico;

geração de overlay/rubrica;

política aprendida de folding/eviction.

SelfCompact mostra que modelos abertos não utilizam de forma
confiável uma ferramenta de compactação sem rubrica; combinar ferramenta
e orientação sobre momentos seguros melhora resultado e custo Li et al., 2026.

## 9.7 Arquitetura híbrida

Canonical Kernel
 campos impossíveis de remover

Task Profile
 semântica da classe de tarefa

Dynamic Overlay
 campos adicionais propostos on-the-fly

Runtime Policy
 trigger, budget, fold e reset

Integrity Gate
 validação

Raw Archive
 reversibilidade

### Schema

compaction_profile:
 id: coding-implementation-v1
 version: 1

 trigger:
 token_pressure: 0.70
 semantic_boundaries:
 - plan_completed
 - implementation_completed
 - subagents_joined

 canonical_preservation:
 policies: exact
 objective: exact
 acceptance_criteria: exact
 active_constraints: exact
 task_identity: exact

 structured_preservation:
 decisions: evidence_linked
 modified_artifacts: latest
 tests: latest_per_commit
 rejected_hypotheses: summarized
 unresolved_failures: full
 next_action: exact

 externalize:
 raw_logs: true
 subagent_transcripts: true
 superseded_file_contents: true

 dynamic_overlay:
 enabled: true
 allowed_to_add_fields: true
 allowed_to_remove_canonical_fields: false

 validation:
 schema: required
 constraint_recall: 1.0
 contradiction_count: 0
 evidence_resolution: required
 recovery_probe: required

## 9.8
Comparação dos principais trabalhos de compactação e folding

Trabalho | 
Unidade de gestão | 
Adaptação | 
Principal contribuição | 
Limitação relevante | 

LongLLMLingua | 
tokens/trechos | 
query-aware | 
Compressão orientada à consulta e reordenação | 
Não modela integralmente estado de agentes | 

LLMLingua-2 | 
tokens | 
task-agnostic | 
Compressor pequeno, eficiente e transferível | 
Pode desconhecer causalidade operacional | 

HiAgent | 
subobjetivos | 
hierárquica | 
Working memory organizada por progresso da tarefa | 
Depende de boa decomposição em subgoals | 

ACON | 
diretrizes de compactação | 
adaptativa por feedback | 
Aprende guidelines a partir de falhas | 
Preprint; políticas podem overfit ao benchmark | 

SelfCompact | 
decisão/rubrica de compactação | 
on-the-fly | 
Agente decide quando e como compactar | 
Metacognição varia fortemente por modelo | 

Context-Folding | 
ramificações procedurais | 
dinâmica | 
Isola subtarefas e retorna resultado dobrado | 
Requer runtime/árvore de contexto | 

FoldAct | 
política de atuação + folding | 
aprendida | 
Trata não-estacionariedade causada pelo folding | 
Treinamento complexo e recente | 

U-Fold | 
intenção + tool log | 
dinâmica | 
Resumo evolutivo consciente da intenção | 
Evidência ainda preprint | 

MAGE | 
árvore de execution state | 
adaptativa | 
Grow/Compress/Maintain/Revise | 
Implementação mais complexa | 

Self-GC | 
objetos indexados | 
planner + policy | 
Fold/mask/prune com sidecars e gates | 
Judge-based evaluation em parte do estudo | 

CWL | 
episódios e dependências | 
determinística | 
Eviction LLM-free e causal | 
Precisa de anotações/dependency graph | 

CompactionRL | 
atuação + resumo | 
RL | 
Treina compactação para coding/terminal | 
Resultados recentes; generalização a outros stacks aberta | 

A série LLMLingua mantém código e materiais de referência que
facilitam reproduções e extensões Microsoft Research, 2026. A tabela
mostra que “compactação” cobre mecanismos diferentes. Prompt compression
remove tokens antes da inferência; summarization reescreve história;
folding isola uma branch; eviction remove objetos recuperáveis; learned
policies alteram a decisão de retenção. Um benchmark honesto precisa
comparar mecanismos por função, não apenas pelo percentual de tokens
removidos.

## 9.9 Kernel canônico e
overlay adaptativo

O kernel canônico preserva elementos que nenhuma rubrica on-the-fly
pode remover:

canonical_kernel:
 exact:
 - task_id
 - user_objective
 - acceptance_criteria
 - active_constraints
 - policy_refs
 - current_branch
 - current_commit
 - open_side_effects
 structured:
 - decisions
 - latest_tests
 - unresolved_failures
 - active_delegations
 - next_action

O overlay adaptativo pode acrescentar campos e mudar
granularidade:

dynamic_overlay:
 proposed_by: context-curator-2
 rationale: "Início da fase de integração"
 preserve_extra:
 - API compatibility rationale
 - migration rollback sequence
 compress_more:
 - exploratory file reads
 forbidden:
 - remove canonical fields
 - rewrite human constraints

Esse desenho permite geração on-the-fly sem entregar ao modelo
autoridade irrestrita sobre a própria memória.

## 9.10 Perfis canônicos
recomendados

### Coding implementation

Preserva artifacts, símbolos, commits, critérios e testes;
externaliza file reads e logs.

### Research

Preserva claims, fontes favoráveis/contrárias, nível de evidência e
lacunas; compacta por claim, não por cronologia.

### Incident response

Preserva timeline, estado atual, intervenções, hipóteses
ativas/rejeitadas e rollback; usa política conservadora.

### Review

Preserva finding ledger ligado ao commit e resolução de cada finding;
remove discussões de versões anteriores após supersession explícita.

### Overseer

Preserva contratos de delegação, estado de integração, testes, commit
e bookkeeping; transcripts de filhos ficam externos.

## 9.11 Quando usar um
compressor separado

Um modelo pequeno pode executar compressão task-agnostic ou extração
estruturada, reduzindo custo. Porém, ele não deve validar sozinho
informação de alta autoridade. A arquitetura em camadas é:
rules/parser → limpeza lossless
small curator → candidato estruturado
strong validator → amostra ou casos de risco
harness → decisão final

Essa separação permite medir cada componente e promove apenas
políticas com evidência.

# 10. Context folding
e gestão de ramificações

## 10.1 Conceito

Folding não é resumir toda a história. É encerrar uma unidade
localizada e retornar um resultado condensado ao caminho principal.
contexto principal
 │
 ├── branch: investigar falha de banco
 │ ├── logs
 │ ├── queries
 │ ├── hipóteses
 │ └── resultado
 │
 └── recebe:
 conclusão
 evidências
 impacto
 ação recomendada

Context-Folding relata contexto ativo até dez vezes menor e
desempenho competitivo ou superior a ReAct e summarization em tarefas
longas Sun et al., 2025. FoldAct
investiga treinamento estável quando o folding altera as observações
futuras Shao et al., 2025. U-Fold adapta
o resumo a intenções que mudam ao longo de diálogos e mantém logs de
ferramentas selecionados Su et al.,
2026.

## 10.2 Folding em subagentes

O melhor ponto é uma fronteira causal:

subobjetivo concluído;

hipótese resolvida;

módulo analisado;

patch aplicado;

suite executada;

review finalizado.

Evitar folding por “a cada N mensagens” quando a unidade permanece
aberta.

## 10.3 Folding hierárquico

child trajectory
 → child result capsule
 → parent working context
 → parent final capsule
 → Overseer

Cada nível mantém referências diretas às evidências originais para
evitar perda cumulativa.

## 10.4 Folding versus reset

Condição | 
Folding | 
Reset | 

Subobjetivo fechado | 
Preferido | 
Opcional | 

Contexto alto, fase encerrada | 
Preferido | 
Pode seguir | 

Investigação aberta e degradada | 
Arriscado | 
Preferido com checkpoint | 

Mudança radical de working set | 
Útil | 
Frequentemente preferido | 

Fim da tarefa | 
Completion fold | 
Sessão deve terminar | 

## 10.5 Folding como
estrutura de árvore

Context-Folding formaliza a ideia de que uma subtarefa pode abrir uma
branch contextual, executar várias ações e retornar apenas um resultado
condensado Sun et al., 2025. A
árvore mantém a trajetória completa fora do caminho principal. Esse
desenho é particularmente adequado a sistemas multiagênticos, porque
cada subagente já é uma branch natural.
root: TASK-184
├── branch A: investigar banco
│ ├── logs
│ ├── queries
│ └── fold result A
├── branch B: revisar API
│ ├── diff
│ └── fold result B
└── active path: integrar A + B

## 10.6 Não-estacionariedade e
FoldAct

Quando o agente gera resumos que se tornam futuras observações, ele
altera a distribuição de seu próprio ambiente. FoldAct chama atenção
para essa não-estacionariedade e separa objetivos de atuação e folding,
usando treinamento e consistência para estabilizar o processo Shao et al., 2025. Para um harness sem
treinamento, a lição é operacional: comparar o capsule com o estado
canônico e não permitir que o executor seja o único juiz do resumo que
receberá depois.

## 10.7 Folding consciente de
intenção

U-Fold mantém um resumo evolutivo da intenção e um tool log compacto,
em vez de um único resumo indiferenciado Su et
al., 2026. Isso se alinha ao desenho de duas camadas deste
documento:

task capsule: fatos e estado verificável;

semantic narrative: intenção, rationale e contexto
para reconstrução cognitiva.

O capsule é autoridade operacional; a narrativa auxilia o modelo, mas
pode ser regenerada.

## 10.8 Folding versus
artefatos tipados

Folding não deve ser entendido apenas como “gerar um parágrafo”. Em
coding agents, os resultados naturais são artifacts:

plano;

patch;

test report;

finding ledger;

ADR;

evidence bundle.

O melhor fold pode ser um conjunto de objetos estruturados com um
resumo curto. MetaGPT e Magentic-One oferecem evidência complementar:
artefatos e ledgers estabilizam coordenação entre papéis Hong et al., 2024; Fourney et al., 2024.

# 11. Lost
in the Middle e empacotamento atento à posição

## 11.1
Não criar uma seção monolítica de “memória histórica”

O contexto deve ser reconstruído por fase.
┌──────────────────────────────────────┐
│ A. Autoridade e objetivo │
├──────────────────────────────────────┤
│ B. Estado operacional crítico │
├──────────────────────────────────────┤
│ C. Evidências selecionadas │
├──────────────────────────────────────┤
│ D. Índice de evidências │
├──────────────────────────────────────┤
│ E. Recência e próxima ação │
└──────────────────────────────────────┘

### Zona A — início

role;

políticas;

objetivo;

critérios;

restrições;

definição de sucesso.

### Zona B

fase;

plano vigente;

decisões;

blockers;

riscos;

working set.

### Zona C — meio

trechos de código;

evidências;

resultados selecionados;

memórias episódicas;

rationale.

### Zona D

referências para logs, transcripts e artefatos.

### Zona E — final

última observação;

estado corrente;

próxima ação;

refresh curto de constraints críticas.

## 11.2 Redundância controlada

Fatos críticos podem aparecer no início e final, renderizados da
mesma fonte canônica:

constraint:
 id: public-api-unchanged
 value: true
 source: task-spec
 version: 4

Isso aumenta saliência sem criar duas memórias divergentes.

## 11.3 Retrieval antes da
ordenação

candidatos
 ↓
filtro por projeto e trust
 ↓
validade temporal
 ↓
fase da tarefa
 ↓
reranking
 ↓
deduplicação e diversidade
 ↓
compressão por fragmento
 ↓
packing posicional

Score possível:
memory_score =
 semantic_relevance
 × scope_match
 × phase_match
 × validation_strength
 × temporal_freshness
 × dependency_relevance
 - contradiction_penalty
 - staleness_penalty
 - redundancy_penalty

## 11.4 Memória negativa

Tentativas fracassadas não devem permanecer como narrativas longas.
Transformá-las em objetos tipados:

rejected_hypothesis:
 claim: "O deadlock é causado pelo pool de conexões."
 status: disproved
 evidence_refs:
 - trace-118
 - experiment-42
 do_not_retry_without_new_evidence: true

Isso reduz contextual drag sem apagar aprendizado Cheng et al., 2026.

## 11.5 Estratégia de
packing em duas passagens

A montagem do contexto deve separar seleção de
ordenação.

### Passagem 1 — seleção

filtrar por projeto, task, commit e trust tier;

descartar superseded;

recuperar dependências de decisões ativas;

reranquear por fase e próxima ação;

garantir diversidade entre evidências;

reservar orçamento para contraevidência.

### Passagem 2 — ordenação

políticas e contrato no início;

estado ativo logo depois;

evidências detalhadas no corpo;

índice de artifacts;

última observação e próxima ação no final;

duplicação controlada de constraints críticas nas bordas.

LongLLMLingua fornece evidência de que compressão e reordenação
query-aware podem superar a preservação cronológica Jiang et al., 2024. Isso não autoriza
uma regra posicional universal, porque o perfil varia por modelo; por
isso, o harness deve medir curvas de posição próprias.

## 11.6 Orçamento para
contraevidência

Um packer puramente orientado à hipótese atual pode esconder
evidências contrárias. O budget deve reservar uma pequena fração
para:

evidência conflitante;

hipótese rejeitada mais próxima;

risco de maior severidade;

constraint potencialmente afetada.

Esse mecanismo reduz confirmação excessiva e ajuda o reviewer a
detectar que o executor está seguindo uma narrativa errada.

## 11.7 Benchmarks posicionais
próprios

Para cada modelo, variar:

posição da constraint: 1%, 10%, 25%, 50%, 75%, 90%, 99%;

tamanho total: 10K, 25K, 50K, 100K e acima, conforme suporte;

número de distractors;

correspondência lexical;

número de tool cycles posteriores;

presença de compactações.

A métrica não é apenas responder qual era a regra, mas aplicá-la
durante uma edição e preservá-la na validação final.

# 12. Comparação de
vendors e modelos abertos

## 12.1 Comparação de
superfícies de controle

Capacidade | 
Codex | 
Claude Code | 
Kimi Code CLI | 
Gemini CLI | 

Compactação automática | 
Sim | 
Sim | 
Sim | 
Sim | 

Compactação manual | 
Sim | 
Sim | 
Sim | 
Sim | 

Threshold configurável | 
Tokens e escopo | 
Toggle e controles do produto | 
Ratio + reserva absoluta | 
Percentual | 

PreCompact/PostCompact | 
Sim | 
Sim | 
Sim, beta | 
Não equivalente documentado | 

Hook pode bloquear | 
PreCompact pode | 
PreCompact pode | 
Hooks beta/fail-open em erros | 
Não equivalente | 

Subagentes isolados | 
Sim | 
Sim | 
Sim | 
Depende da superfície | 

Limite de tool output | 
Configurável/adapter | 
Context editing | 
Adapter/hook | 
Summarization de shell | 

Algoritmo semântico transparente | 
Não | 
Não | 
Parcial | 
Parcial | 

A tabela descreve capacidades documentadas em julho de 2026; não mede
qualidade do resumo.

## 12.2 Codex

Codex expõe:

model_context_window;

model_auto_compact_token_limit;

model_auto_compact_token_limit_scope;

PreCompact e PostCompact;

SubagentStop com transcript path;

controles de persistência e histórico OpenAI, 2026a; OpenAI, 2026b.

O harness pode bloquear compactação no PreCompact,
persistir checkpoint e validar depois.

model_context_window = 200000
model_auto_compact_token_limit = 120000
model_auto_compact_token_limit_scope = "total"

## 12.3 Claude Code e API
Anthropic

Claude Code possui hooks de ciclo de vida, incluindo
PreCompact e PostCompact, configuração de
auto-compaction e suporte a subagentes isolados Anthropic, 2026a; Anthropic, 2026c. A API
Anthropic oferece context editing para limpar tool results e thinking
blocks antigos Anthropic,
2026b.

Pontos fortes:

interceptação rica;

possibilidade de reinjeção;

limpeza seletiva de tipos de conteúdo.

Ponto cego: a política semântica da compactação nativa não é
suficientemente transparente para comparação causal.

## 12.4 Kimi Code CLI

Kimi permite:

[loop_control]
reserved_context_size = 50000
compaction_trigger_ratio = 0.85

A compactação é disparada pela reserva absoluta ou pelo ratio, o que
ocorrer primeiro Moonshot AI, 2026a.
Hooks PreCompact e PostCompact existem em beta
Moonshot AI, 2026b. Como erros podem
resultar em comportamento fail-open, controles críticos devem permanecer
fora do hook.

## 12.5 Gemini CLI

Gemini CLI expõe
model.chatCompression.contextPercentageThreshold, com
default documentado de 0,7, e summarization de tool output para shell
com budget configurável Google,
2026a. É uma superfície simples e previsível, porém com menos pontos
de governança semântica que Codex e Claude.

## 12.6 Modelos abertos

Modelos abertos permitem:

compressor separado;

treinamento específico de compactação;

RL para folding/eviction;

instrumentação de KV cache;

comparações controladas com mesmo executor.

SelfCompact avalia sete modelos e demonstra uma lacuna metacognitiva:
sem rubric, o uso da ferramenta de compactação é irregular Li et al., 2026. NGC aprende eviction
de KV cache conjuntamente com reasoning Li
et al., 2026. Trabalhos de compactação para SWE-agents mostram que a
representação pode ser treinada especificamente para coding, e não
apenas como resumo genérico Liu et al.,
2025.

## 12.7 Protocolo justo de
comparação

### Native versus native

Benchmark de produto; mistura modelo, CLI e algoritmo.

### Compressor comum

Mesmo checkpoint externo para todos os executores; mede
resumability.

### Mesmo modelo, perfis
diferentes

Ideal para modelos locais:
Qwen sem compactação
Qwen + resumo genérico
Qwen + checkpoint canônico
Qwen + curator separado
Qwen + folding aprendido

## 12.8 Leitura
comparativa: primitives versus política

As CLIs fornecem primitives diferentes, mas nenhuma elimina a
necessidade de política externa.

### Codex

A configuração oficial expõe model_context_window,
model_auto_compact_token_limit e escopo de contagem total
ou posterior ao prefixo compactado; hooks PreCompact e
PostCompact permitem checkpoint e validação OpenAI, 2026a; OpenAI, 2026b. Subagentes possuem
threads próprias e podem retornar resultados condensados OpenAI, 2026c. A documentação
sobre tarefas longas recomenda externalizar plano e estado em artifacts
OpenAI, 2025.

Issues e discussões do repositório revelam dificuldades práticas:
observabilidade de receipts de hooks, reinjeção pós-compaction,
necessidade de pedir compaction real por hook e propostas de memória
persistente. Esses relatos são evidência de campo, não prova de
comportamento universal OpenAI
Codex issues, 2026.

### Claude Code/Agent SDK

PreCompact pode bloquear compactação;
PostCompact observa o resumo; SessionStart
pode reinjetar contexto. A API oferece context editing para tool results
e thinking blocks, permitindo limpeza granular antes de resumo Anthropic, 2026a; Anthropic, 2026b.
Subagentes operam em conversas isoladas e retornam uma mensagem final ao
pai Anthropic, 2026c.

Issues do Claude Code relatam perda de mudanças de path, desejo de
checkpoints pré-compaction, perda de história e solicitações de
preview/restauração. Novamente, são sinais de classes de falha e
necessidades de UX, não estatística controlada Claude Code issues, 2026.

### Kimi Code CLI

Kimi expõe duas condições de auto-compaction: reserva absoluta e
proporção da janela. Hooks beta incluem PreCompact e
PostCompact, mas a documentação descreve comportamento
fail-open em falhas de hook Moonshot AI,
2026a; Moonshot AI, 2026b. Isso
torna o watchdog externo indispensável para enforcement.

### Gemini e Google ADK

Gemini CLI oferece checkpointing, enquanto o ADK documenta
compactação token-based e sliding-window, além de custom summarizer;
quando ambas estão configuradas, a token-based é a principal Google, 2026a; Google, 2026b. É importante não
confundir a CLI, o ADK e a Live API: são superfícies com mecanismos
diferentes.

### Modelos abertos

Modelos abertos permitem isolar algoritmo e pesos. SelfCompact mostra
que modelos variam na capacidade de decidir quando compactar e se
beneficiam de rubricas específicas Li et
al., 2026. CompactionRL treina conjuntamente atuação e compactação
em tarefas de coding e terminal, reportando ganhos em benchmarks, mas
ainda carece de replicação ampla Li et
al., 2026. Essa abertura torna possível construir um
ModelContextProfile empírico para Qwen, GLM e outras
famílias locais.

## 12.9 O que
uma comparação cross-vendor precisa fixar

Uma comparação de produto pode medir experiência end-to-end, mas
mistura modelo, CLI, prompt oculto e algoritmo. Uma comparação causal
precisa de três trilhas:

native vs native: mede produto;

mesmo compressor externo, executores diferentes:
mede resumability;

mesmo modelo aberto, perfis diferentes: mede efeito
da política.

Também é necessário registrar versão da CLI, snapshot do modelo,
settings, hooks, tools, cache e número de ciclos de compaction. Sem
isso, resultados não são reproduzíveis.

# 13. Lições de outros
harnesses

## 13.1 Magentic-One

O Orchestrator planeja, acompanha progresso, delega e replana Fourney et al., 2024. Lição: separar
Task Ledger de Progress Ledger e detectar estagnação explicitamente.

## 13.2 MetaGPT

MetaGPT organiza agentes por papéis e SOPs, usando artefatos
intermediários Hong et al., 2024. Lição:
agentes devem trocar objetos tipados, não transcripts integrais.
Limitação: SOP rígido pode adicionar overhead em tarefas simples.

## 13.3 SWE-agent

SWE-agent demonstra que a Agent–Computer Interface altera
materialmente o desempenho Yang et al.,
2024. Lição: ferramentas estreitas, observações estruturadas e
edição segura podem ser mais importantes que prompts extensos.

## 13.4 Agentless

Agentless mostra que um pipeline simples de localização, reparo e
validação pode superar arquiteturas mais complexas em determinados
benchmarks Xia et al., 2024. Lição:
multiagente, folding e memória sofisticada devem ser acionados por
necessidade, não por padrão.

## 13.5 AutoCodeRover

AutoCodeRover enfatiza localização estrutural e APIs sobre o código
Zhang et al., 2024. Lição:
retrieval estrutural — símbolos, chamadas, testes, ownership e Git —
deve preceder retrieval semântico genérico.

## 13.6 LangChain Deep Agents

Deep Agents realiza offloading automático de tool inputs/results
grandes, substituindo-os por referências; quando isso não basta, aplica
summarization. Subagentes usam janelas isoladas LangChain, 2026a; LangChain, 2026b. Lição:
offloading deve ocorrer antes da compactação.

## 13.7 little-coder

little-coder é um harness adaptado para modelos locais pequenos Inbar, 2026a; Inbar, 2026b. Seus
mecanismos incluem perfis por modelo, ferramentas mais estreitas,
skill/knowledge injection com budget, parser de output, guards
determinísticos, thinking budget e compactação antecipada.

O whitepaper reporta melhora do mesmo modelo Qwen 9,7B de cerca de
19,11% para 45,56% no Aider Polyglot ao trocar o scaffold; o autor
reconhece ausência de ablações formais para atribuir causalidade a cada
mecanismo Inbar, 2026b.
Logo, o caso é evidência de engenharia forte de que scaffold–model fit
importa, mas não prova isoladamente cada heurística.

### Lições para modelos pequenos

menor número de objetivos ativos;

tools e schemas menores;

output parsing determinístico;

menos liberdade para sumarização;

re-decomposição antecipada;

modelo mais forte ou regras como validator;

budgets específicos por modelo.

### O que não copiar sem
experimento

threshold universal;

truncamento genérico por início/fim;

prompts calibrados para um benchmark;

resumo livre como fonte canônica;

confiança automática em memória recente.

## 13.8 Magentic-One:
ledgers e replanejamento

Magentic-One separa Task Ledger e Progress Ledger. O primeiro reúne
fatos, hipóteses e plano macro; o segundo acompanha progresso e
delegações. Essa distinção reduz churn: o estado estável não precisa ser
reescrito a cada ação. O orchestrator pode replanejar ao detectar
estagnação Fourney et al., 2024.
Discussões do AutoGen registram falhas de parsing do ledger com modelos
menores, lembrando que schemas precisam de reparo e fallback AutoGen discussion, 2026.

## 13.9 MetaGPT e
ChatDev: artefatos versus diálogo

MetaGPT usa SOPs e papéis para produzir artifacts intermediários;
ChatDev organiza colaboração em diálogos entre papéis Hong et al., 2024; Qian et al., 2023. Para governança de
contexto, a lição é que diálogo deve ser transitório, enquanto o produto
da fase deve ser um artifact tipado. O branch principal do ChatDev
evoluiu para ChatDev 2.0, enquanto a versão anterior foi preservada em
branch específica; essa evolução do repositório mostra que a topologia e
o runtime continuam mudando ChatDev
repository, 2026.

## 13.10 SWE-agent,
Agentless e AutoCodeRover

SWE-agent demonstra que a Agent–Computer Interface altera
materialmente o desempenho: comandos e observações desenhados para
edição e navegação podem ser tão importantes quanto prompting Yang et al., 2024. Agentless mostra que
um pipeline simples de localização, reparo e validação pode competir com
sistemas muito mais autônomos Xia et al.,
2024. AutoCodeRover usa estrutura do código para localizar contexto
antes de reparar Zhang et al.,
2024.

A correlação é direta: uma boa política de contexto não é apenas
compressão; ela inclui uma interface que evita produzir lixo e retrieval
estrutural que reduz a necessidade de carregar o repositório
inteiro.

## 13.11 Deep Agents e
filesystem como memória

Deep Agents combina offloading de grandes tool inputs/results,
filesystem, skills progressivas, subagentes e summarization LangChain, 2026b. A sequência
“offload antes de summarize” está alinhada à taxonomia deste documento.
O repositório deep-agents-from-scratch torna esses mecanismos
mais inspecionáveis e útil para ablações LangChain, 2026c.

## 13.12
little-coder: estudo de caso aprofundado

O little-coder é relevante porque parte da hipótese de que modelos
pequenos exigem um ambiente mais estrito. O repositório implementa
seleção de skills, budgets, parser, guards e um watchdog que verifica o
contexto durante a execução autônoma. Releases recentes passaram a medir
o efeito real da compactação e pausar quando o ganho foi inferior a um
limiar, prevenindo loops de compactação sem progresso Inbar, 2026a; little-coder releases,
2026.

Três lições são transferíveis:

o trigger precisa rodar mid-loop, não apenas quando o agente volta
ao prompt;

depois de compactar, a state machine deve retomar
explicitamente;

o harness deve medir before/after, não presumir que
/compact funcionou.

Não devemos importar automaticamente o threshold de 80% ou
heurísticas específicas. Elas foram calibradas para aquele runtime e
modelo. O que deve ser copiado é a disciplina de telemetria, guardas e
perfis por modelo.

## 13.13 Outros repositórios
úteis

Pydantic AI Harness explora workflows dinâmicos e evita encaminhar
todo resultado intermediário pelo contexto do orchestrator; UniHarness e
outros projetos documentam pipelines de compactação em fases. Esses
repositórios são sinais do estado da prática, mas suas claims devem ser
validadas antes de adoção Pydantic
AI Harness, 2026; UniHarness,
2026.

# 14. Arquitetura
proposta: Context Control Plane

 ┌─────────────────────────┐
 │ Vendor Agent Adapter │
 │ Codex / Claude / Kimi │
 └────────────┬────────────┘
 │
 telemetry, hooks, events
 │
 ┌─────────────────────▼─────────────────────┐
 │ CONTEXT CONTROL PLANE │
 ├───────────────────────────────────────────┤
 │ 1. Context Telemetry │
 │ 2. Budget Controller │
 │ 3. Object Registry & Dependency Graph │
 │ 4. Artifact / Evidence / Trajectory Store │
 │ 5. Garbage Collector │
 │ 6. Retrieval & Reranking │
 │ 7. Attention-Aware Packer │
 │ 8. Context Curator │
 │ 9. Folding Orchestrator │
 │10. Compaction Profile Compiler │
 │11. Integrity Gate │
 │12. Reset & Rehydration │
 │13. Memory Promotion │
 └─────────────────────┬─────────────────────┘
 │
 minimum sufficient context
 │
 ┌────────────▼────────────┐
 │ Overseer / Subagent │
 └─────────────────────────┘

## 14.1 Context Telemetry

context_usage:
 vendor:
 agent:
 model:
 physical_limit:
 safe_limit:
 reliable_limit:
 operational_limit:
 current_tokens:
 system_tokens:
 tool_tokens:
 conversation_tokens:
 summary_tokens:
 reserved_output:
 projected_next_tokens:
 pressure_ratio:

## 14.2 Budget Controller

Exemplo inicial:

context_budget:
 authority: 5%
 task_contract: 8%
 active_state: 12%
 retrieved_evidence: 35%
 code_and_tool_results: 25%
 conversation_tail: 5%
 output_and_recovery_reserve: 10%

Percentuais devem ser calibrados.

## 14.3 Compaction Profile
Compiler

Combina:

kernel canônico;

perfil da tarefa;

profile do modelo;

estado de runtime;

overlay proposto pelo modelo;

políticas de segurança.

O modelo não pode remover campos canônicos.

## 14.4 Integrity Gate

### Validação determinística

task ID;

objetivo;

critérios;

constraints;

branch/commits;

arquivos e artifact refs;

último teste por suite;

jobs ativos;

dependências;

próxima ação.

### Validação semântica

Compara checkpoint anterior, trajectory range e resultado
compactado.

compaction_validation:
 goal_fidelity:
 constraint_recall:
 decision_recall:
 evidence_recall:
 contradiction_count:
 unsupported_claims:
 resumability:

Política mínima:
constraint_recall < 1.0 → rejeitar
contradiction_count > 0 → rejeitar
unsupported_claims > 0 → reparar/rejeitar
resumability != pass → reset + reidratação

## 14.5 Recovery Probe

Após compactação:

context_probe:
 task_id:
 objective:
 mandatory_constraints: []
 current_phase:
 latest_test_status:
 biggest_open_risk:
 next_action:

A resposta é comparada ao run state; não é usada como única
fonte.

## 14.6 State machine

HYDRATED
 ↓
ACTIVE
 ├── minor_gc ───────────────┐
 ├── fold_completed_unit ────┤
 ├── checkpoint ─────────────┤
 ├── compact ── validate ────┤
 ├── reset ─── rehydrate ────┤
 └── complete ─ final_gc ─ CLOSED

## 14.7 Pseudocódigo

while backlog.has_eligible_items():
 task = backlog.claim_next()

 session = overseer.new_session(
 constitution=load_effective_constitution(task),
 playbooks=retrieve_playbooks(task),
 project_context=retrieve_project_context(task),
 task_capsule=create_task_capsule(task),
 )

 while not task.is_terminal:
 event = execute_next_overseer_step(session, task)
 ingest_and_persist(event)
 run_minor_gc(session)

 pressure = predict_context_pressure(session)

 if task.has_completed_subgoal and pressure > FOLD_THRESHOLD:
 fold_completed_subgoal(session, task)

 if pressure > MAJOR_GC_THRESHOLD and at_safe_boundary(task):
 run_major_gc(session)

 if pressure > COMPACTION_THRESHOLD and at_semantic_boundary(task):
 checkpoint = create_checkpoint(task, session)
 compact_with_effective_profile(session, checkpoint)
 validate_context_integrity(session, checkpoint)

 if pressure > RESET_THRESHOLD or behavioral_degradation(session):
 checkpoint = create_validated_checkpoint(task, session)
 session = reset_and_rehydrate(checkpoint)

 run_integration_and_regression_gates(task)
 commit_or_rollback(task)
 write_completion_capsule(task)
 propose_memory_delta(task)
 perform_bookkeeping(task)
 session.close()

## 14.8 Arquitetura lógica
detalhada

┌─────────────────────────────────────────────────────────────┐
│ POLICY / AUTHORITY PLANE │
│ Constitution compiler · permissions · pinned constraints │
└──────────────────────────────┬──────────────────────────────┘
 │
┌──────────────────────────────▼──────────────────────────────┐
│ CONTEXT CONTROL PLANE │
│ Telemetry · budget · object registry · dependency graph │
│ GC · retrieval · packer · profiles · folding · integrity │
└──────────────┬──────────────────────────────┬───────────────┘
 │ │
┌──────────────▼──────────────┐ ┌────────────▼──────────────┐
│ Vendor adapters │ │ Canonical stores │
│ Codex/Claude/Kimi/Gemini │ │ trajectory/artifact/state│
└──────────────┬──────────────┘ └────────────┬──────────────┘
 │ │
┌──────────────▼──────────────────────────────▼───────────────┐
│ Overseer, workers e subagentes │
└─────────────────────────────────────────────────────────────┘

## 14.9 Componentes e
responsabilidades

### Context Object Registry

Indexa objetos com lifecycle, authority, dependencies, persistence e
token estimate.

### Dependency Graph

Permite mark-and-sweep causal. Uma decisão ativa mantém vivas suas
evidências; um processo ativo mantém vivo seu handle; um finding aberto
mantém vivo o diff correspondente.

### Context Budget Controller

Usa o ModelContextProfile e previsão da próxima ação.
Pode negar iniciar uma operação grande quando não há reserva
suficiente.

### Context Curator

Propõe folding e compaction overlays. Pode ser modelo pequeno, regras
ou híbrido.

### Integrity Gate

Compara resultado com kernel canônico, ledger e artifact refs.
Rejeita perda de constraints, contradições e referências quebradas.

### Vendor Adapter

Normaliza telemetria, hooks e comandos; registra capacidades e
limitações.

## 14.10 Contrato de
capabilities

context_capabilities:
 provider: codex
 version: "2026-07"
 usage_observation: exact_or_estimated
 native_compaction:
 manual: true
 automatic: true
 configurable_threshold: true
 hooks:
 pre_compact: blocking
 post_compact: observational
 subagents:
 isolated_threads: true
 transcript_ref: true
 context_editing:
 selective_tool_result_eviction: external

O policy engine escolhe estratégias compatíveis. Em Kimi, por
exemplo, um hook fail-open não pode ser usado como único gate; em
Claude, PreCompact pode bloquear; em ADK, custom summarizer
pode ser configurado.

## 14.11 Algoritmo de
montagem de contexto

def build_context(agent, task, next_action):
 profile = profiles.resolve(agent.role, task.family, task.phase)
 budget = budgets.compute(agent.model_profile, profile, next_action)

 roots = state.load_pinned_roots(task)
 active = state.load_active_state(task, agent)
 candidates = retrieval.query(task, next_action, profile)

 candidates = filter_by_scope_version_trust(candidates, task)
 candidates = remove_superseded(candidates)
 candidates = add_dependencies(candidates, active)
 candidates = rerank_with_counterevidence(candidates, next_action)

 packed = packer.layout(
 authority=roots,
 active_state=active,
 evidence=candidates,
 budget=budget,
 model_profile=agent.model_profile,
 )
 return integrity.validate_pre_inference(packed)

## 14.12 Algoritmo de
compaction validada

def compact_session(session, trigger):
 before = checkpoint.create(session)
 assert integrity.validate_checkpoint(before)

 profile = profile_compiler.compile(
 canonical=before.canonical_kernel,
 task_profile=profiles.for_task(before.task),
 dynamic_overlay=curator.propose(before, trigger),
 )
 profile = policy.constrain(profile)

 result = vendor.compact(session, profile)
 validation = integrity.compare(before, result)

 if not validation.pass_all:
 repaired = repair.from_canonical_state(before, result)
 if not integrity.compare(before, repaired).pass_all:
 return reset_and_rehydrate(before)
 return repaired
 return result

## 14.13 Decisão de
re-decomposição

O harness registra compaction_count,
gc_yield, recovery_reads e
stalls. Uma subtarefa que cruza várias compactações com
pouco progresso recebe sinal DELEGATION_TOO_COARSE. O
Overseer converte o estado restante em novas subtarefas, evitando uma
cadeia indefinida de resumos.

# 15. Perfis por papel e
classe de tarefa

## 15.1 Overseer

overseer_profile:
 preserve:
 - task_contract
 - workflow_phase
 - active_agents
 - delegation_contracts
 - decisions
 - integration_state
 - latest_tests
 - commit_state
 - bookkeeping_state
 - unresolved_conflicts
 - next_control_action

 externalize:
 - subagent_transcripts
 - raw_logs
 - file_contents
 - superseded_plans

## 15.2 Planner

Preservar objetivo, constraints, arquitetura atual, opções
consideradas, decisão e riscos. Foldar exploração após plano aceito.

## 15.3 Implementer

Preservar arquivos/símbolos alterados, base/HEAD, rationale, failures
e próximo patch. GC agressivo de file reads e tool protocol já
persistido.

## 15.4 Reviewer

Findings independentes e vinculados a commit:

finding:
 id:
 severity:
 file:
 lines:
 claim:
 evidence_refs: []
 proposed_fix:
 commit_reviewed:
 status:

## 15.5 Researcher

Compactar por claim, não por ordem de páginas consultadas. Preservar
evidência contraditória e qualidade das fontes.

## 15.6 Incident Agent

Perfil conservador. Timeline, sistema atual, intervenções, rollback e
cadeia causal ativa não são coletáveis.

## 15.7 Test Runner

Pode ser agressivo:

test_result:
 command:
 commit:
 status:
 failures: []
 relevant_stacks: []
 raw_ref:

## 15.8 Small Model Strict

small_model_profile:
 maximum_active_goals: 1
 maximum_open_hypotheses: 3
 maximum_inline_evidence_items: 5
 skill_budget: small
 tool_output_budget: strict
 reasoning_budget: explicit
 task_schema: mandatory
 response_schema: mandatory

 compaction:
 deterministic_cleanup_first: true
 freeform_summary: restricted
 validator: stronger_model_or_rules
 max_compactions_per_subtask: 1

# 16. Programa experimental

## 16.1 Hipóteses

H1. Checkpoint canônico + GC + folding supera
compactação nativa isolada em fidelidade e estabilidade.

H2. Reset por backlog item reduz confusão cross-task
sem aumentar excessivamente custo-to-success.

H3. Perfis específicos por tarefa superam perfil
genérico em tarefas heterogêneas.

H4. Overlay on-the-fly melhora compressão, mas
apenas quando campos canônicos são imutáveis e há integrity gate.

H5. Garbage collection orientado a dependências
remove menos tokens que oldest-first, mas preserva melhor resultados
downstream.

H6. Subagentes com contexto isolado e fold contract
reduzem poluição do Overseer e melhoram integração.

H7. Memória negativa estruturada reduz contextual
drag comparada a transcript integral de tentativas falhas.

H8. Modelos pequenos apresentam ganho marginal maior
com microgerenciamento, tool guards e schemas obrigatórios.

## 16.2 Estratégias

A0 transcript integral
A1 truncamento oldest-first
A2 compactação nativa default
A3 resumo genérico externo
A4 checkpoint canônico
A5 checkpoint + GC estrutural
A6 perfil por tarefa
A7 perfil on-the-fly
A8 folding por subobjetivo
A9 híbrido completo + integrity gate
A10 reset por fase/tarefa

## 16.3 Classes de tarefa

bug fix;

feature longa;

refactoring;

migração de schema;

revisão de segurança;

diagnóstico de CI;

pesquisa técnica;

incidente;

documentação;

Overseer com múltiplos subagentes.

## 16.4 Benchmark posicional

Posicionar a mesma constraint ou evidência em:
1%, 5%, 10%, 25%, 50%, 75%, 90%, 95%, 99%

Volumes:
8K, 16K, 32K, 64K, 128K, 256K, 1M quando suportado

Medir recuperação literal, associação semântica, aplicação de regra,
atribuição tool–result, retenção após compactação e consistência na
revisão final.

## 16.5 Experimento de
contextual drag

Comparar:

tentativa falha integral;

resumo narrativo;

remoção total;

memória negativa tipada;

referência externa recuperável.

## 16.6 Experimento de subagente

S0 sem GC
S1 minor GC
S2 fold por fase
S3 compactação por threshold
S4 checkpoint + reset
S5 re-decomposição

## 16.7 Vendor benchmark

### Trilha A — produto

Claude native, Codex native, Kimi native, Gemini native.

### Trilha B — representação
comum

Todos recebem o mesmo checkpoint.

### Trilha C — modelos locais

Mesmo modelo com diferentes políticas.

## 16.8 Métricas

### Fidelidade

goal recall;

acceptance criteria recall;

constraint recall;

decision recall;

negative-memory recall;

evidence attribution accuracy.

### Continuidade

resume success;

unnecessary re-read count;

repeated failure rate;

stale-plan execution;

contradiction rate;

premature completion.

### Economia

peak active tokens;

total input tokens;

tool output tokens;

compaction cost;

retrieval cost;

latency;

cost-to-success.

### GC

tokens reclaimed;

critical-object false-positive rate;

future-dependency preservation;

artifact recovery success;

cache invalidation cost.

### Multiagente

cross-agent duplication;

parent re-query rate;

capsule sufficiency;

finding deduplication;

error propagation depth;

marginal gain per agent.

## 16.9 ModelContextProfile

model_context_profile:
 vendor:
 model:
 cli_version:
 advertised_window:
 safe_physical_limit:

 reliable_limits:
 code_editing:
 log_analysis:
 architecture_review:
 research:

 position_profile:
 beginning:
 early_middle:
 middle:
 late_middle:
 end:

 metacognition:
 autonomous_compaction_reliability:
 rubric_required:
 schema_compliance:

 recommended:
 minor_gc_at:
 major_gc_at:
 compact_at:
 reset_at:
 maximum_subtask_compactions:

## 16.10 Desenho fatorial e
ablações

A avaliação completa é cara. Recomenda-se começar com fractional
factorial e ablações pareadas. Fatores:
context strategy × model × task family × task length × tool volume
× subagent topology × compaction cycles × policy strictness

Um primeiro conjunto controlado pode fixar modelo e tasks e
variar:

transcript integral;

minor GC;

GC + checkpoint canônico;

resumo genérico;

perfil por tarefa;

perfil por tarefa + overlay;

folding por subobjetivo;

checkpoint + reset.

## 16.11 Benchmark de
compactação repetida

Criar uma trajetória sintética e uma real, aplicar 1, 3, 5 e 10
ciclos e medir:

recall de constraints;

decisão/justificativa;

evidências conflitantes;

atribuição teste–commit;

próxima ação;

unsupported claims;

tamanho;

sucesso de retomada.

O teste deve comparar resumo recursivo com regeneração a partir do
estado canônico.

## 16.12 Benchmark de garbage
collection

Objetos são rotulados por humanos ou por regras verificáveis:
LIVE / PINNED / FOLDABLE / MASKABLE / PRUNABLE

Métricas:

false positive crítico: objeto vivo removido;

false negative: lixo retido;

tokens reclaimed;

future dependency preservation;

artifact recovery success;

cache-adjusted savings.

A função de utilidade deve penalizar falsos positivos muito mais que
falsos negativos.

## 16.13 Benchmark de subagentes

Comparar:

filho sem compactação;

minor GC;

compaction por threshold;

folding por subobjetivo;

reset por fase;

re-decomposição.

Tasks devem incluir exploração, implementação, review, incidente e
pesquisa. Medir também a suficiência do capsule para o pai e quantas
vezes o Overseer precisa reabrir a trajetória.

## 16.14 Comparação de vendors

### Trilha produto

Executa cada CLI com defaults e settings recomendados. Mede
experiência end-to-end.

### Trilha representação comum

O mesmo checkpoint externo é entregue a todos. Mede capacidade de
retomar.

### Trilha modelos abertos

Mesmo modelo e runtime, políticas diferentes. Mede causalidade da
estratégia.

## 16.15 Métricas tardias

A compactação pode parecer correta imediatamente e causar erro cinco
passos depois. Portanto, avaliação deve incluir delayed outcomes:

regressão posterior;

reabertura da task;

finding perdido;

memória promovida incorretamente;

rollback;

intervenção humana.

## 16.16 Reprodutibilidade

Registrar:

commit do harness e repositório;

snapshot do modelo;

versão da CLI;

prompt/profile/policy versions;

trajectory IDs;

settings de cache;

seeds quando disponíveis;

budgets e timeouts;

artifacts completos.

# 17. Segurança,
governança e auditabilidade

## 17.1
Context management como superfície de segurança

Compaction, GC, retrieval e packing podem:

remover policies;

priorizar conteúdo adversarial;

ocultar evidência contrária;

transportar instruções maliciosas de repositório;

promover memória contaminada;

perder o vínculo entre teste e commit;

apagar o estado de side effects.

A pesquisa sobre Governance Decay torna explícito que a camada de
compactação é uma superfície de governança Chen, 2026.

## 17.2 Separação de autoridade

proposal_agent != approval_authority
compressor != sole_validator
memory_writer != policy_authority

## 17.3 Constraint Pinning

Constraints são renderizadas de fonte canônica em todas as
reidratações e nunca entram na sumarização livre.

## 17.4 Proveniência

provenance:
 trajectory_id:
 source_events:
 from:
 to:
 compressor:
 model:
 profile_version:
 source_hash:
 created_at:
 validator:
 validation_result:

## 17.5 Recuperabilidade

Todo fold deve possuir:

artifact ref;

escopo;

preview;

hash;

permissões;

retenção;

forma de recuperação.

## 17.6 Memory promotion

Memórias candidatas precisam de:

evidência;

escopo;

confiança;

validade temporal;

ausência de conflito;

confirmação por execuções posteriores ou revisão.

memory_candidate:
 type:
 statement:
 evidence_refs: []
 project_scope:
 confidence:
 validation_status:
 expires_at:

## 17.7 Context
injection e memória contaminada

Conteúdo de repositório, web e tools pode tentar alterar a política
de retenção. O Context Curator deve tratar payload como dados. Somente o
control plane pode mudar authority, pinned,
trust_tier e retention_class.

Memórias recuperadas também podem estar obsoletas ou contaminadas.
Cada item precisa de provenance, scope, version range, confidence e
revocation status. Uma memória não deve ser promovida porque foi
repetida pelo modelo; precisa de evidência externa ou validação em
múltiplas runs.

## 17.8 Direito
ao esquecimento versus auditabilidade

Trajectory store e context cache têm políticas diferentes. Um objeto
pode sair da janela sem ser deletado. A exclusão permanente deve seguir
retention policy, privacidade e requisitos legais. Para manter
auditabilidade, registros revogados podem receber tombstones sem
preservar conteúdo sensível.

## 17.9 Separation of duties

executor != curator, quando risco alto
curator != validator
proposal_agent != approval_authority

Em tasks de baixo risco, papéis podem ser combinados por economia. Em
mudanças de policy, segurança ou autoevolução, a separação deve ser
obrigatória.

# 18. Trade-offs,
limitações e ameaças à validade

## 18.1 Risco de complexidade
acidental

Um Context Control Plane completo pode custar mais do que economiza
em tarefas curtas. Agentless demonstra que pipelines simples permanecem
competitivos em classes importantes Xia et
al., 2024. O harness deve possuir níveis de maturidade e bypass para
tarefas atômicas.

## 18.2 Preprints recentes

Self-GC, CWL, MAGE, SelfCompact, Governance Decay, ContextBudget, NGC
e U-Fold são recentes. Resultados devem ser reproduzidos em:

outros modelos;

outros harnesses;

tarefas reais;

diferentes idiomas;

execuções longas com side effects;

múltiplas compactações sucessivas.

## 18.3 Judge-based evaluation

Alguns trabalhos usam LLM judges para avaliar impacto da remoção. É
necessário complementar com:

critérios determinísticos;

sucesso real da tarefa;

testes;

hashes e referências;

revisão humana amostral.

## 18.4 Vendor drift

CLIs e modelos mudam frequentemente. O benchmark deve registrar
versões e snapshots.

## 18.5 Prompt cache

GC eficiente em tokens pode piorar custo e latência se invalidar
caches frequentemente.

## 18.6 Resumo cumulativo

Compactações sucessivas podem acumular distorção. A reversibilidade e
referências para fontes originais são obrigatórias.

## 18.7 Raciocínio oculto

Nem todos os vendors expõem thinking ou permitem transportar cadeias
internas. A arquitetura deve depender de estado operacional verificável,
não de acesso a chain-of-thought.

## 18.8 Privacidade e retenção

Trajectory stores integrais podem reter dados sensíveis. O harness
precisa de políticas próprias de redaction, criptografia, TTL,
tombstones e acesso.

## 18.9
Transferência entre benchmarks e produção

Benchmarks de retrieval não capturam side effects e colaboração;
benchmarks de coding não capturam pesquisa; demos de vendor usam stacks
específicos. Resultados devem ser tratados como evidência localizada. O
programa experimental interno precisa incluir repositórios reais,
tarefas longas e falhas de ambiente.

## 18.10 Opacidade dos vendors

A ausência de transparência sobre prompt, modelo e algoritmo usados
na compactação nativa impede atribuir causalidade. Mudanças silenciosas
de produto podem alterar resultados. O harness deve logar outputs,
versões e comportamento observável e manter um compressor externo como
baseline.

## 18.11 Custo de complexidade

Um Context Control Plane completo pode se tornar mais complexo que o
problema em tarefas curtas. A arquitetura deve ser progressiva:
simple task → offload + minor GC
medium task → checkpoint + profile
long task → folding + reset + validator
high-risk task → separation of duties + full provenance

## 18.12 Risco de overfitting
dos perfis

Perfis derivados de uma família de tasks podem prejudicar outras.
Mudanças persistentes exigem replay suite cross-task e rollback. Learned
policies entram primeiro em shadow mode.

# 19. Roadmap de implementação

## Fase 0 — Telemetria

normalizar uso de contexto por vendor;

registrar tokens, tools e fases;

versionar modelos, CLIs e prompts;

detectar outputs grandes.

## Fase 1 — Estado canônico

Task Ledger;

Progress Ledger;

trajectory store;

artifact/evidence store;

completion capsule.

## Fase 2 — Offloading e minor
GC

file/log offloading;

deduplicação por hash;

latest-per-suite;

supersession graph;

tool span normalization.

## Fase 3 — Context packing

retrieval por fase;

trust e temporal filters;

attention-aware layout;

constraint pinning;

budget envelopes.

## Fase 4 — Perfis canônicos

coding;

review;

research;

incident;

Overseer;

small model strict.

## Fase 5 — Folding

delegation capsules;

child result contracts;

fold por subobjetivo;

folding hierárquico.

## Fase 6 — Integrity Gate

schema validation;

evidence resolution;

recovery probes;

semantic validator independente;

rejeição e reparo.

## Fase 7 — Vendor adapters

Codex hooks/config;

Claude hooks/context editing;

Kimi loop control/hooks;

Gemini thresholds;

providers OpenAI-compatible locais.

## Fase 8 — Adaptive layer

seleção de perfil;

overlay on-the-fly;

Context Curator;

shadow mode;

A/B tests.

## Fase 9 — Learned policies

distillation de compressor;

RL/folding em modelos abertos;

evolução de guidelines;

promotion pipeline governado.

# 20. Agenda de pesquisa aberta

## 20.1 CompactionBench agêntico

A área precisa de um benchmark que preserve trajetória, tools,
commits, subagentes e compactações repetidas. O dataset deve conter
dependências futuras rotuladas, constraints, evidências conflitantes e
tarefas de retomada.

## 20.2 Perfis
transferíveis versus específicos

Investigar quanto um perfil de coding transfere entre Java, Python e
Solidity; quanto um perfil de research transfere entre revisão
científica e pesquisa de mercado; e quando o overlay adaptativo supera
um kernel canônico bem projetado.

## 20.3 Curator pequeno
versus modelo executor

Comparar regras, compressor pequeno, mesmo modelo e frontier
validator. Medir custo, fidelidade e viés de autojustificação.

## 20.4 Context policies
treinadas

CompactionRL, FoldAct e ContextBudget indicam que atuação e memory
management podem ser aprendidos. Precisamos testar se políticas
treinadas em benchmarks preservam governança, generalizam a repositórios
diferentes e permanecem estáveis após atualização do modelo.

## 20.5 GC causal e static
analysis

Para coding agents, o dependency graph pode incorporar AST, call
graph, test coverage, Git e workflow state. Isso permitiria marcar
contexto vivo com mais precisão que embeddings isolados.

## 20.6 Observabilidade
padronizada

Definir eventos comuns para context_object_created,
gc_committed, compaction_started,
fold_completed, integrity_failed e
session_rehydrated, compatíveis com OpenTelemetry e W3C
PROV.

## 20.7 Longitudinalidade

Avaliar não apenas uma task, mas semanas de backlog: memória
contaminada, drift de perfis, custo acumulado, reuso de artifacts,
regressões e capacidade de reproduzir decisões.

## 20.8 Harnesses para modelos
pequenos

O little-coder sugere que microgerenciamento pode elevar modelos
menores. A agenda deve decompor causalmente guards, tool interface,
skill budgets, context watchdog, compactação e retry policy em vários
modelos abertos.

## 20.9 Matriz de
validação das hipóteses centrais

Hipótese | 
Evidência favorável | 
Evidência/limitação contrária | 
Situação | 

Estado canônico deve ficar fora do transcript | 
MemGPT, OpenAI, Anthropic, ledgers | 
Custo de infraestrutura e retrieval | 
Forte | 

Reset por task é melhor que conversa imortal | 
long-running harnesses, artifacts | 
CWL sugere continuidade possível com eviction estruturada | 
Forte como default, não universal | 

GC deve preceder compactação | 
context editing, Deep Agents, Self-GC | 
Poucas ablações cross-vendor | 
Forte arquiteturalmente | 

Folding por subobjetivo supera periodic summarization | 
HiAgent, Context-Folding, MAGE | 
Dependência de decomposição correta | 
Média-alta | 

Perfis por tarefa superam perfil genérico | 
TACO/ATA/ACON e lógica operacional | 
Comparações ainda heterogêneas | 
Média | 

Overlay on-the-fly é útil | 
SelfCompact, U-Fold | 
Metacognição varia e cria autoavaliação | 
Promissor, requer gates | 

Policies devem ser pinadas | 
Governance Decay | 
Benchmark ainda preprint | 
Forte por princípio de segurança | 

Modelos pequenos precisam de scaffold mais estrito | 
little-coder, SWE-agent, Agentless | 
Ablações insuficientes para cada mecanismo | 
Média-alta | 

Threshold deve vir de benchmark próprio | 
Lost in Middle, RULER, NoLiMa | 
Custo de manter perfis por snapshot | 
Forte | 

Transcripts de subagentes não devem poluir pai | 
subagents de Claude/Codex, folding | 
Pai pode precisar reabrir evidência | 
Forte com retrieval disponível | 

# 21. Conclusões

A literatura e as práticas de harnesses convergem em uma mudança de
abstração: contexto não deve ser tratado como uma conversa que cresce
até exigir um resumo emergencial. Ele deve ser tratado como um conjunto
governado de objetos com autoridade, dependências, persistência e ciclo
de vida.

Para o Overseer:

reset por item relevante do backlog é o padrão; compactação é
intra-task; o estado reside no harness.

Para subagentes:

preservar o caminho ativo, coletar o rastro mecânico, dobrar
subobjetivos concluídos e retornar um capsule tipado ao
pai.

Para garbage collection:

idade não implica inutilidade; fold precede prune; políticas
e side effects são roots pinadas.

Para perfis:

kernel canônico + perfil por tarefa + overlay adaptativo +
validação é superior à escolha binária entre resumo genérico e autonomia
irrestrita.

Para Lost in the Middle:

retrieval, seleção e organização posicional precisam ser
explícitos; uma janela maior não garante uso confiável.

Para vendors:

triggers e hooks nativos são primitives, não a política
completa. O harness deve normalizar telemetria, checkpoints, validação e
reidratação.

A formulação final é:

A janela de contexto é uma cache cognitiva sujeita a limite
físico, viés posicional, interferência, obsolescência e perda semântica.
O Context Control Plane deve construir, monitorar, limpar, dobrar,
compactar, validar e substituir essa cache a partir de um estado
canônico externo, tipado, recuperável e auditável.

# 22. Referências
bibliográficas

## 22.1
Fundamentos, benchmarks e artigos peer-reviewed

Liu, N. F.; Lin, K.; Hewitt, J.;
Paranjape, A.; Bevilacqua, M.; Petroni, F.; Liang, P. (2024).
Lost in the Middle: How Language Models Use Long Contexts.
Transactions of the Association for Computational Linguistics, 12,
157–173. ACL
Anthology.

Jiang, H. et al.
(2024). LongLLMLingua: Accelerating and Enhancing LLMs in
Long Context Scenarios via Prompt Compression. ACL 2024. ACL Anthology.

Pan, Z. et al.
(2024). LLMLingua-2: Data Distillation for Efficient and
Faithful Task-Agnostic Prompt Compression. Findings of ACL 2024. ACL
Anthology.

Zhang, X.; Chen, Y.; Hu,
S.; Xu, Z.; Chen, J.; Hao, M.; Han, X.; Thai, Z.; Wang, S.; Liu, Z.;
Sun, M. (2024). ∞Bench: Extending Long Context Evaluation
Beyond 100K Tokens. ACL 2024. ACL
Anthology.

Bai, Y. et al.
(2025). LongBench v2: Towards Deeper Understanding and
Reasoning on Realistic Long-Context Multitasks. ACL 2025. ACL
Anthology.

Hu, M.; Chen, T.; Chen, Q.; Mu,
Y.; Shao, W.; Luo, P. (2025). HiAgent: Hierarchical Working
Memory Management for Solving Long-Horizon Agent Tasks with Large
Language Model. ACL 2025, p. 32779–32798. ACL
Anthology.

Hong, S. et al. (2024).
MetaGPT: Meta Programming for Multi-Agent Collaborative
Framework. ICLR 2024. OpenReview.

Yang, J. et al.
(2024). SWE-agent: Agent–Computer Interfaces Enable
Automated Software Engineering. NeurIPS 2024. Proceedings.

Xu, W. et al. (2025).
A-MEM: Agentic Memory for LLM Agents. NeurIPS 2025. OpenReview · arXiv.

Qian, C. et al. (2023).
ChatDev: Communicative Agents for Software Development. arXiv:2307.07924.

Xia, C. S. et al.
(2024). Agentless: Demystifying LLM-Based Software
Engineering Agents. arXiv:2407.01489 · GitHub.

Zhang, Y. et al.
(2024). AutoCodeRover: Autonomous Program Improvement.
ISSTA 2024. arXiv:2404.05427.

## 22.2
Benchmarks e estudos fundamentais ainda em preprint

Hsieh, C.-P. et al.
(2024). RULER: What’s the Real Context Size of Your
Long-Context Language Models? arXiv:2404.06654.

Modarressi, A. et al.
(2025). NoLiMa: Long-Context Evaluation Beyond Literal
Matching. arXiv:2502.05167.

Packer, C. et al.
(2023). MemGPT: Towards LLMs as Operating Systems. arXiv:2310.08560.

Li, Z. et al. (2025).
MemOS: An Operating System for Memory-Augmented Generation in Large
Language Models. arXiv:2507.03724.

Fourney, A. et al.
(2024). Magentic-One: A Generalist Multi-Agent System for
Solving Complex Tasks. arXiv:2411.04468.

Cheng, Y. et al.
(2026). Contextual Drag: How Errors in the Context Affect
LLM Reasoning. Preprint. arXiv:2602.04288.

## 22.3
Bleeding edge: compactação, folding, execution state e GC

Chen, S.
(2026). Governance Decay: How Context Compaction Silently
Erases Safety Constraints in Long-Horizon LLM Agents. Preprint. arXiv:2606.22528.

Sun, W. et al.
(2025). Scaling Long-Horizon LLM Agent via
Context-Folding. Preprint. arXiv:2510.11967 · GitHub.

Shao, J. et al. (2025).
FoldAct: Efficient and Stable Context Folding for Long-Horizon
Agents. Preprint. arXiv:2512.22733 · GitHub.

Su, J. et al. (2026).
U-Fold: Dynamic Intent-Aware Context Folding for User-Centric
Agents. Preprint. arXiv:2601.18285.

Chen, Y. et al. (2026).
Beyond Semantic Organization: Memory as Execution State Management
for Long-Horizon Agents. Preprint. arXiv:2606.06090.

Hao, X. et al. (2026).
Self-GC: Self-Governing Context for Long-Horizon LLM Agents.
Preprint. arXiv:2607.00692.

Semenov, A.; Dorofeev, S.
(2026). Beyond Compaction: Structured Context Eviction for
Long-Horizon Agents. Preprint. arXiv:2606.11213.

Kang, M. et al. (2025).
ACON: Optimizing Context Compression for Long-Horizon LLM
Agents. Preprint. OpenReview · arXiv:2510.00615.

Li, T. et al.
(2026). Self-Compacting Language Model Agents.
Preprint. arXiv:2606.23525.

Li, M. et al.
(2026). CompactionRL: Jointly Learning Task Execution and
Context Compaction for Long-Horizon Agents. Preprint. arXiv:2607.05378.

Wu, Y. et al.
(2026). ContextBudget: Budget-Aware Context Management for
Long-Horizon Search Agents. Preprint. arXiv:2604.01664.

Li, M. et al. (2026).
Neural Garbage Collection: Learning to Forget while Learning to
Reason. Preprint. arXiv:2604.18002.

Liu, S. et al.
(2025). Context Management for Long-Horizon
SWE-Agents. Preprint. arXiv:2512.22087.

Xu, et al. (2026).
MemGym: Benchmarking Memory Systems for Agentic Tasks.
Preprint. arXiv:2605.20833.

Luo, J. et al.
(2026). A Survey on the Evolution of LLM Agent Memory.
Findings of ACL 2026. ACL
Anthology.

## 22.4 Documentação
oficial e engineering blogs

OpenAI (2026a).
Codex Hooks. Documentação oficial. OpenAI
Developers.

OpenAI (2026b).
Codex Configuration Reference. Documentação oficial. OpenAI
Developers.

OpenAI
(2026c). Codex Subagents. Documentação oficial. OpenAI
Developers.

OpenAI (2026d).
Building Reliable Agents: Memory and Compaction. Cookbook. OpenAI
Developers.

OpenAI (2025).
Using PLANS.md for Multi-Hour Problem Solving / Long-Horizon
Tasks. OpenAI
Developers.

Anthropic
(2026a). Claude Code Hooks Reference. Documentação
oficial. Claude Code
Docs.

Anthropic
(2026b). Context Editing. Documentação oficial. Claude
Platform Docs.

Anthropic
(2026c). Subagents in Claude Code and Agent SDK.
Documentação oficial. Claude
Code Docs.

Anthropic
(2026d). Effective Harnesses for Long-Running Agents.
Engineering article. Anthropic
Engineering.

Anthropic
(2026e). Effective Context Engineering for AI Agents.
Engineering article. Anthropic
Engineering.

Moonshot AI
(2026a). Kimi Code CLI — Configuration Files.
Documentação oficial. Kimi
CLI Docs.

Moonshot AI (2026b).
Kimi Code CLI — Hooks (Beta). Documentação oficial. Kimi
CLI Docs.

Google (2026a).
Gemini CLI Configuration. Documentação oficial. Gemini
CLI Docs.

Google (2026b).
Agent Development Kit — Context Compaction. Documentação
oficial. ADK
Docs.

LangChain
(2026a). Context Engineering. Documentação oficial. LangChain
Docs.

LangChain
(2026b). Context Engineering in Deep Agents.
Documentação oficial. LangChain
Docs.

LangChain
(2026c). Deep Agents from Scratch. Repositório
educacional. GitHub.

Microsoft Research
(2026). LLMLingua Series. Projeto e implementações. Microsoft
Research.

## 22.5
Repositórios, branches, releases, issues e discussões — evidência de
campo

Os itens desta subseção ajudam a compreender comportamento de
runtime, bugs e decisões de engenharia. Não devem ser interpretados como
benchmarks controlados.

Inbar, I.
(2026a). little-coder: A Harness Optimized for Smaller
LLMs. GitHub.

Inbar, I.
(2026b). Honey, I Shrunk the Coding Agent. Whitepaper.
Substack.

little-coder
contributors (2026). CHANGELOG — context watchdog,
compaction resume and loop guards. GitHub.

little-coder
contributors (2026). Releases. GitHub.

OpenAI Codex
community (2026). Issues e discussões sobre hooks, compaction,
reinjeção e memória persistente. Issue #28633 ·
Issue #28736
· Issue
#22861 · Issue #23153 ·
Discussion
#31085.

Claude Code
community (2025–2026). Issues sobre perda de contexto,
checkpoints e compactação. Issue
#36573 · Issue
#33026 · Issue
#27293 · Issue
#10727 · Issue
#6066.

AutoGen community
(2026). Magentic-One ledger parsing with smaller
models. GitHub
Discussion #6600.

OpenBMB (2026).
ChatDev repository; main branch and chatdev1.0 branch. GitHub.

Pydantic
(2026). Pydantic AI Harness. GitHub.

UnicomAI (2026).
UniHarness. GitHub.

TsinghuaC3I
(2026). Awesome Memory for Agents. Living
bibliography. GitHub.

LCLM-Horizon
(2026). A Comprehensive Survey for Long-Context Language
Modeling. Living repository. GitHub.

## 22.6 Documento interno do
projeto

Projeto Multi Agent
Harness (2026). Plano formal de pesquisa: Harnesses
multiagênticos adaptativos, governados e orientados a projetos.
Documento interno, 14 jul. 2026. Arquivo
local.

# Apêndice A — Glossário
operacional

Termo | 
Definição adotada | 

Contexto ativo | 
Conteúdo efetivamente enviado ao modelo numa inferência | 

Estado canônico | 
Dados externos autoritativos usados para reconstruir o contexto | 

Garbage collection | 
Retirada segura de objetos desnecessários da visão ativa | 

Offloading | 
Movimento de payload para storage, deixando referência | 

Folding | 
Fechamento de uma unidade/branch em resultado condensado
recuperável | 

Compactação | 
Reescrita lossy de trajetória para reduzir tokens | 

Reset | 
Encerramento da sessão física e criação de nova sessão | 

Reidratação | 
Reconstrução da sessão a partir do estado canônico | 

Capsule | 
Objeto estruturado que representa estado ou resultado | 

Overlay | 
Ajuste adaptativo aplicado sobre perfil canônico | 

Pinned root | 
Informação não coletável por autoridade ou dependência viva | 

# Apêndice B — Árvore
de decisão operacional

O objeto é policy, instrução humana, critério ou side effect ativo?
 └─ sim → PIN
 └─ não
 O payload está persistido e é recuperável byte-a-byte?
 └─ sim → FOLD/OFFLOAD
 └─ não
 Está superseded e sem dependentes vivos?
 └─ sim → PRUNE
 └─ não
 Pertence a subobjetivo concluído?
 └─ sim → FOLD
 └─ não
 Está no caminho investigativo ativo?
 └─ sim → RETAIN
 └─ incerto → RETAIN + reavaliar na fronteira

# Apêndice C —
Defaults iniciais para experimentação

Pressão sobre
operational_limit | 
Overseer | 
Subagente | 

0–40% | 
normal + minor GC | 
normal + offload | 

40–55% | 
deduplicação/offload | 
minor GC mais agressivo | 

55–65% | 
major GC na fronteira | 
fold de subobjetivo concluído | 

65–75% | 
checkpoint preventivo | 
não iniciar fase grande | 

75–85% | 
compactar validando ou resetar | 
checkpoint/reset em safe point | 

>85% | 
bloquear operação grande; reset | 
devolver partial result e re-decompor | 

Esses números são hipóteses iniciais. Cada
ModelContextProfile deve substituí-los por limites
empíricos.

# Apêndice D —
Schema mínimo de 
# ModelContextProfile

model_context_profile:
 id: qwen36-35b-a3b-local-v1
 model_snapshot:
 runtime:
 advertised_window:
 safe_physical_limit:
 reliable_limits:
 coding:
 research:
 log_analysis:
 position_curve:
 beginning:
 middle:
 end:
 compaction:
 autonomous_reliability:
 recommended_trigger:
 reset_trigger:
 max_cycles_per_task:
 tool_output:
 inline_limit:
 preferred_parsers: []
 schemas:
 compliance_rate:
 benchmark_version:

# Apêndice E —
Checklist de qualidade da evidência

[ ] A afirmação está ligada a uma fonte?
[ ] A fonte é peer-reviewed, preprint, vendor ou evidência de campo?
[ ] O texto deixa essa classe explícita?
[ ] Há código ou dataset?
[ ] Existe replicação independente?
[ ] O benchmark mede recuperação ou atuação real?
[ ] O resultado foi obtido com o mesmo modelo/harness comparado?
[ ] A claim do repositório possui ablação?
[ ] A data e a versão estão registradas?
[ ] Há uma fonte contrária ou uma limitação relevante?

