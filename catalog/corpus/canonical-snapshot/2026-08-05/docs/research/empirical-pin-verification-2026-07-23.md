# Confiabilidade de conhecimento operacional destilado: verificação empírica dos pins do playbook

Rodada 2026-07-23 (pedido do owner). Formato: relatório científico interno.
Companheiro metodológico de `opus-overseer-quality-2026-07-23.md` (§2.4 daquele
relatório declara o mesmo regime de conflito de interesse; idem aqui).

## Abstract

O playbook do overseer acumula "pins" — claims empíricas destiladas de
incidentes (custos, capacidades de sandbox, comportamentos de CLI) que passam a
governar roteamento e gasto. Em 2026-07-23, três pins foram refutados em
sequência por contestações diretas do owner, todos com a MESMA causa-raiz
(argumento mutilado por camada de shell, atribuído erroneamente a uma limitação
de capacidade). Em resposta, o owner ordenou auditoria sistemática do restante.
Construímos uma fila de 10 pins com teste-barato e risco-se-falso pré-registrados
e delegamos a re-verificação a um worker Sonnet sob contrato de isolamento
metodológico. Resultado: **9/10 confirmados, 1 refutado** (P7: duração do gate
driftou de "7-15min" para ~5-6min típicos desde o flip paralelo D041). Achado
meta central: o próprio worker de auditoria reproduziu ao vivo AMBAS as classes
de armadilha que derrubaram os pins originais (stdin-já-em-EOF; mangle MSYS de
`/usage`) e converteu falsos vereditos em corretos aplicando a disciplina de
isolamento exigida pelo contrato — evidência de que o método é transferível,
não idiossincrático. Taxa de falsidade estratificada: pins nascidos de UMA
observação de falha não isolada: 3/3 falsos; pins nascidos de medição
deliberada ou inspeção de fonte: 9/10 verdadeiros (o único falso foi por drift
temporal, não por erro de origem). A lição estrutural: **o modo de nascimento
do pin prediz sua confiabilidade melhor do que sua idade**.

## 1. Contexto e pergunta

Pins são a memória operacional do harness: "X custa ~$0,37", "Y trava sem
stdin fechado", "Z não roda no sandbox". Eles decidem roteamento de lanes,
cadência de probes e postura de segurança. A pergunta desta rodada: *quantos
pins vigentes são falsos, e o que os torna falsos?*

Gatilho: três contestações do owner no mesmo dia, três refutações:

| pin refutado | claim registrada | causa real (probe-proven) |
|---|---|---|
| R1 | "claude `/usage` é interactive-only; pct impossível não-interativo" | Git-Bash/MSYS mutila `/usage`→path Windows; via subprocess list-args o painel renderiza (e a ~$0 no pin haiku) |
| R2 | "codex não consegue spawnar browser (EPERM)" | a flag `--sandbox workspace-write` DA NOSSA RECEITA bloqueia spawn de processo; o uso interativo do owner funciona; provado com 2 sondas (binário in-workspace ainda EPERMa ⇒ restrição de spawn, não de path) |
| R3 | "codex não tem rede (ENOTCACHED)" | fetch direto do sandbox → HTTP 200; o ENOTCACHED veio de quoting aninhado powershell→cmd onde `^` é escape, mutilando o semver `@^6.12.2` |

As três compartilham a assinatura: **falha observada uma vez através de uma
camada de shell; a camada mutilou o argumento; a mutilação foi atribuída à
capacidade da ferramenta**. Nenhuma das três claims era verdadeira sobre a
ferramenta; todas eram verdadeiras sobre o encanamento entre nós e ela.

## 2. Métodos

### 2.1 A fila pré-registrada

Extraímos do playbook os 10 pins empíricos remanescentes
(`.harness/handoff/playbook-pin-audit-queue.md`), cada um com: a claim
literal, o teste barato pré-especificado, e o risco-se-falso (o que roteia ou
gasta errado). Pré-registro do teste ANTES da execução segue a disciplina da
rodada R4 de métricas de construto (`construct-metrics.md`: definição
pré-registrada antes da medição — exatamente a prática cuja ausência produziu
o finding F4 do relatório opus-overseer).

### 2.2 Contrato do worker

Worker Sonnet 5 (debugger), com contrato explícito de: (a) probes só em
gpt-5.6-terra / claude-haiku (cap de $0,05; acima ⇒ OWNER-GATED, não rodar);
(b) **disciplina de isolamento obrigatória**: nunca concluir de um sintoma
único — re-sondar por rota de quoting alternativa (subprocess list-args) antes
de declarar a CLAIM falsa; (c) veredito honesto UNTESTABLE preferível a chute;
(d) evidência verbatim por pin. O P1 (claim de travamento) foi testado sob
`timeout 60` para que um travamento real não prendesse o worker.

### 2.3 Limitações

n=13 pins (3+10), um ambiente (Windows/MSYS/PowerShell — as armadilhas de
quoting são específicas dessa pilha); a metade cara do P3 (comparação com
Fable) ficou owner-gated por custo; auto-auditoria da mesma sessão (mitigada:
worker externo + contestações do owner como gatilho independente + toda
refutação re-verificada na fonte pelo overseer antes de aceita).

## 3. Resultados

### 3.1 Vereditos da fila (worker, re-verificados pelo overseer)

| pin | claim | veredito | nota |
|---|---|---|---|
| P1 | stdin aberto trava `codex exec` | CONFIRMADO | o probe ingênuo deu falso-negativo (stdin do Bash-tool já em EOF); o probe isolado confirmou o travamento |
| P2 | codex ≥0.144 ignora `.codex/config.toml` local | CONFIRMADO | nuance nova: `--profile` lê `$CODEX_HOME/<name>.config.toml` E exige o repo no trust registry — duas variáveis de isolamento além do quoting |
| P3 | fuel probe no pin haiku ≈ $0 | CONFIRMADO | o probe ingênuo REPRODUZIU o mangle MSYS ao vivo (o exato bug pré-fix); o isolado confirmou custo ~0 |
| P4 | `codex login status` é grátis | CONFIRMADO | sem turn de modelo |
| P5 | pw_ui_smoke mata o servidor (sem órfãos) | CONFIRMADO | |
| P6 | worker de packet nunca ecoa key | CONFIRMADO | corrida com key falsa; ausente de stdout/logs |
| **P7** | **gate leva 7-15min** | **REFUTADO** | real: ~5-6min típico desde o flip paralelo D041 (2026-07-21); outliers de contenção até ~21,5min. Corrigido no CLAUDE.md via edição sancionada de arquivo protegido |
| P8 | briefs D039 carregam footprint | CONFIRMADO (4/5) | uma exceção estreita |
| P9 | pin de routing fable/high + sol xhigh | CONFIRMADO | sem drift desde f69e9fb |
| P10 | `route --heartbeat` nunca spawna | CONFIRMADO | a PARÁFRASE da fila estava errada (atribuía a claim ao Conductor A) — corrigida NA FILA; o playbook estava certo |

### 3.2 O achado meta

O worker de auditoria caiu nas DUAS armadilhas do dia — P1 pelo stdin-EOF do
shell da ferramenta, P3 pelo mangle MSYS — e em ambos os casos executou o
passo de isolamento do contrato (re-probe via subprocess list-args) e chegou
ao veredito correto. Isto é o resultado mais importante da rodada: a
disciplina anti-falso-pin **funciona quando exigida por contrato**, inclusive
em um modelo mais barato, e as armadilhas são REPRODUTÍVEIS (não foram azar de
uma sessão).

### 3.3 Estratificação por origem do pin

| origem do pin | n | falsos | taxa |
|---|---|---|---|
| 1 observação de falha, variável de shell não isolada | 3 (R1-R3) | 3 | 100% |
| medição deliberada / inspeção de fonte | 10 (P1-P10) | 1 | 10% |

O único falso do segundo estrato (P7) não nasceu errado — nasceu certo e
**driftou** quando o D041 mudou o regime de execução do gate, sem que ninguém
re-medisse a constante. Classe distinta: decaimento temporal, não erro de origem.

### 3.4 Custo da rodada

Fila + contrato: overseer (inline). Worker: 201,7k tokens Sonnet. Probes:
terra/haiku, centavos no total. Nenhum probe em modelo caro.

## 4. Discussão: por que pins apodrecem

1. **Mutilação na fronteira de shell é o assassino dominante neste ambiente.**
   4 das 4 refutações do dia (R1-R3 + o ENOTCACHED intermediário) rastreiam a
   camadas de quoting (MSYS path-mangle; cmd `^`-escape; PowerShell aninhado),
   não às ferramentas. Em Windows com 3 shells empilháveis, qualquer falha
   observada ATRAVÉS de um shell é suspeita até que o argumento seja provado
   intacto (subprocess list-args é o instrumento limpo).
2. **Generalização de sintoma único.** As três claims refutadas viraram "a
   ferramenta não consegue" a partir de UMA falha. O relatório opus-overseer
   já tinha nomeado a família (prosa excede verificação); aqui ela aparece na
   direção epistêmica: observação insuficiente vira lei operacional.
3. **Constantes medem regimes, não verdades.** P7 era verdade no regime
   serial; o D041 mudou o regime e a constante ficou órfã. Pins numéricos
   precisam de carimbo de regime (o que os invalida), não só de data.
4. **Paráfrase também apodrece** (P10): o erro estava na FILA de auditoria,
   não no playbook — instrumentos de verificação estão sujeitos ao mesmo
   decaimento que verificam.

## 5. Mecanismos resultantes (não-prosa)

| mecanismo | estado |
|---|---|
| Correções R1-R3 + P7 gravadas como RETRATAÇÕES datadas (nunca deleção de história) no playbook/spec/CLAUDE.md | landado (b309625, 00312f2, ac5517d, batch W3) |
| Fila de pin-audit como artefato permanente e reutilizável (claim + teste + risco pré-registrados) | `.harness/handoff/playbook-pin-audit-queue.md` |
| Contrato de isolamento pro worker de auditoria (provou-se transferível) | no texto da fila; reutilizável verbatim |
| "Probe-before-pin" como prática de playbook | registrado nas correções |

Recomendações abertas (portas, não trabalho feito): (a) re-auditoria periódica
da fila (barata: ~centavos + 1 worker Sonnet); (b) metadados de pin — todo pin
novo carrega data + método + link de evidência + regime que o invalida; (c)
cap de tentativas de workaround em lanes (o wedge da W3 desta tarde: a lane
insistiu ~50min num workaround de TEMP em vez de declarar HOST-LIMITED como as
lanes W1/W2 fizeram — a instrução padrão de lane deve limitar o loop).

## 6. Conclusão

A auditoria respondeu a pergunta do owner com um número e uma causa: **dos 13
pins examinados, 4 eram falsos, e 3 dos 4 nasceram do mesmo defeito de método**
(sintoma único através de shell não isolado). O acervo restante está saudável
(9/10), e o único decaído era drift de regime, não erro. O custo de manter o
acervo honesto provou-se trivial (centavos por rodada) comparado ao custo dos
pins falsos que ele previne — R2/R3 sozinhos teriam mantido lanes de teste de
UI fora do codex e forçado pre-installs desnecessários indefinidamente.

## Referências

Internos: `.harness/handoff/playbook-pin-audit-queue.md` (fila + desfecho);
`.harness/handoff/result-playbook-pin-audit.md` (evidência verbatim por pin);
probes R1-R3 nos transcripts da sessão (comandos + saídas verbatim, incl.
NET-OK 200 e os dois EPERM); `docs/research/opus-overseer-quality-2026-07-23.md`
(companheiro; F4 = a mesma família na direção métrica);
`docs/research/construct-metrics.md` (R4: pré-registro de definição antes da
medição); `docs/research/vendor-credit-tracking-log.md` (medição-honestidade);
commits `b309625`, `f69e9fb`, `00312f2`, `ac5517d`, `cd665dc` (D047).
Externos: nenhum citado — corpus interno; as limitações da §2.3 se aplicam.
