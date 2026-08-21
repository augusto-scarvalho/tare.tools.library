# Round — a definição de superfície do gate (2026-07-26)

Double Diamond sobre SPEC-137. Orquestrador: sessão overseer (Opus 5, fallback
registrado). Playbook: `.harness/prompts/research-playbook.md`.

## Pergunta

A **superfície do gate** (`precommitValidation.surfaceRoots` — o que o gate
observa) e a **superfície de risco** (o que pode quebrar o sistema) discordam.
Por que essa classe de defeito reincide — quatro registros abertos em cinco dias,
nenhum fechado — e qual desenho faz as duas concordarem **sem** pagar o DRUM
(bateria de cenários, 5-27min) a cada edição de doc?

Enquadramento explícito do problema, não da solução: a resposta "alargue
`surfaceRoots`" é a tech-shaped answer que já falhou em fechar a classe (foi
aplicada para `ui/` em 21/07 e a mesma forma reapareceu três vezes depois).

## Critérios de sucesso

Uma boa resposta precisa satisfazer, simultaneamente:

1. **Fecha a classe, não a instância.** Um desenho que exija editar uma lista
   toda vez que um arquivo novo vira insumo de máquina já falhou — foi assim que
   os quatro registros nasceram.
2. **Preço nomeado.** Custo em segundos por commit, por classe de arquivo, contra
   os dois números medidos: spec-pack 19,5s / cenários 5-27min.
3. **Não trava o gate.** `unstaged_surface_paths` bloqueia `validate --staged`
   quando qualquer arquivo rastreado sob uma raiz de superfície está sujo — e
   `.harness/context/NEXT_STEPS.md` + `handoff.*` estão sujos em toda sessão.
4. **Dente falsificável.** O check proposto tem que FALHAR hoje e passar depois,
   lendo a policy VIVA (`.harness/project.json`), não uma cópia hardcoded de
   cenário — todo cenário de gate hoje usa cópia própria em repo scratch, então
   um dente contra a cópia é tautologia medida.
5. **Cobre o caso auto-referencial.** `project.json` define a superfície e está
   fora dela; qualquer desenho tem que dizer o que acontece com ele.

## Atores e restrições

- Atores: overseer (commita), implementer/worker (edita), hook de pre-commit
  (bloqueia), gate runner (roda), dono (decide alargamento).
- Restrições duras: fingerprint é index-based (`git ls-files -s`, imune a mtime);
  `validator_version` hasheia `project.json` → mudar a policy reata todo stamp;
  `spec-pack` **não** roda `testing/scenarios/*.py`; SPEC-159 Fase 2 (seletor de
  cenários afetados) está com narrowing=0, então não há hoje bateria barata.

## Largura declarada (D010)

**4 workers, `custom`, em 2 waves de 2 — pedido do dono (Sonnet 5 high ×2 +
NVIDIA ×2).** Justificativa (Δm — cada worker extra tem que se pagar):

- O tema é **um** (definição de superfície), o que puxa para FOCUSED (1-2). Mas
  o espaço de solução está aberto (quatro enquadramentos concorrentes, nenhum
  desenho escolhido), o que puxa para EXPLORATORY. 4 fica na banda intermediária
  justificada por complexidade, não por default.
- A largura é **cruzada por vendor** de propósito: heterogeneidade de modelo é o
  que faz o painel valer (arXiv:2502.08788 — MAD é supervalorizado quando a
  heterogeneidade é ignorada). Dois vendors ≠ dois workers do mesmo modelo.
- **A divisão de perspectivas segue o acesso, não o gosto.** Workers HTTP
  (`nvidia-compat`, via `tools/openai_worker.py`) **não leem o repo** — o packet
  é tudo que veem. Então as duas perspectivas que precisam verificar código
  (simplicidade/redução, confiabilidade/ops) vão para Sonnet 5 high com acesso ao
  repo; as duas conceituais (fronteira de confiança, analogia cross-domain) vão
  para NVIDIA, onde a falta de acesso custa menos. Ambos recebem o MESMO piso de
  evidência embutida no brief.
- Duas waves separadas também é o que a máquina permite: `--executor` fixa a run
  inteira num executor, e nenhum papel de roteamento aponta para `nvidia-compat`.
  Waves independentes = geração nominal sem cross-talk (Diehl & Stroebe 1987).

## Orçamento declarado

- Wave A (Sonnet 5 high ×2) + Wave B (NVIDIA ×2): teto por `workflow token-audit`
  antes de cada `run`; gate de 60% do playbook vale.
- NVIDIA é tier gratuito (NVIDIA Build) — custo de gás ~0.
- CLAUDE 99% restante (sonda 26/07 20:24). CODEX 1% — **nenhuma perna vai para
  codex nesta rodada**.
- Sem wave 2-3 de técnicas estruturadas salvo sinal forte. 1 divergência (×2
  waves) + 1 crítica, conforme o playbook.

## Design de experimento (L18)

Esta rodada **não** produz por si uma alegação mensurável — ela produz opções de
desenho. Se uma opção virar promoção de default (alargar a superfície e medir
falso-bloqueio), o card aplicável de `docs/EXPERIMENT_METHODS.md` é
**matched-budget** (comparar custo de gate por classe de arquivo sob orçamento
igual) + **evidence grades** para a promoção. Registro via `experiment add` só
quando houver alegação; hoje não há.

## Piso de evidência (embutido em todos os packets)

Medido nesta sessão, `[repo]` salvo onde marcado:

- `precommitValidation.surfaceRoots = [scripts, tools, testing, specs, ui]`
  (`.harness/project.json`).
- O curto-circuito aparece em 3 consumidores da mesma definição:
  `validation_stamp.check_staged:212`, `check_reckon:337`, `cmd_validate:714` —
  todos `staged == head` → `"surface unchanged"`, exit 0.
- Prova estrutural: 0 de 792 entradas do manifesto ficam fora das 5 raízes. O
  manifesto é montado com `git ls-files -s -- <roots>`, então caminhos fora não
  passam despercebidos: não existem para o fingerprint.
- 326 de 1120 arquivos rastreados (29%) estão fora. 32 dos últimos 120 commits
  (27%) tocaram zero arquivos de superfície → entraram sem gate, join verde.
- Fora da superfície: `docs/` (183), `.harness/` (44, incl. `project.json` que
  DEFINE a policy, `routing/`, `prompts/`), `.claude/`, `.codex/`, `codex/`,
  `schemas/` (12), `tasks/`, `release/`, `.github/`, `requirements*.txt`,
  `setup.sh|bat`, `skills-lock.json`, `AGENTS.md`, `CLAUDE.md`.
- 11 dos 12 arquivos de `protected-files.json` estão fora da superfície.
- `.harness/project.json`: fora da superfície, fora de protected-files, e nenhum
  cenário assere seu conteúdo (todos usam cópia `POLICY` hardcoded em repo
  scratch). `enabled:false` commitaria com a bateria verde.
- Quatro registros abertos da mesma causa: `wf-policy-self-coverage` (21/07, P1),
  intake `d783b80d7748` (23/07, HIGH), `gate-docsonly-skips-lockfile-inputs`
  (25/07, P2), `gate-surface-shortcircuit` + intake `caa593befe98` (26/07, P1).
- Preços medidos: `spec-pack` 19,5s / 1055 checks; cenários 5-27min. `spec-pack`
  **não** roda `testing/scenarios/*.py`, onde vivem os dentes desses arquivos
  (`playbook_registry` lock-drift, `eg_entry_groom` row malformada).
- Precedente: `400e302` fechou a mesma forma para `ui/` em 3 camadas — policy +
  perfil, pin em `gate_affected.py`, prova em `pvg_precommit_gate.py`.
- Mitigação parcial existente: `delivery_bar_advisor` VÊ esses caminhos (R2/R3/R6)
  e imprime aviso no pre-commit — mas nunca bloqueia, e R3 silencia se houver
  qualquer cenário estagiado junto.

## Briefs (Phase 2)

**Brief 1 — a classe, não a instância.** Por que a definição de superfície
reincide como defeito? Que desenho faz "o que o gate observa" derivar de "o que
é insumo de máquina" em vez de ser uma lista curada? Critérios 1, 4, 5.

**Brief 2 — o preço da concordância.** Se a superfície alargar, quem paga e
quanto? Que gradação de custo por classe de arquivo é defensável, e o que fazer
enquanto não existe bateria barata (narrowing=0)? Critérios 2, 3.

## Waves

| Wave | Executor | Workers | Perspectivas | Status |
|---|---|---|---|---|
| A | `--executor claude` (WF-20260727-003307-162394) | 2 | simplicidade-redução; confiabilidade-ops | reduzida, 2/2 válidos |
| B | `openai_worker.py` direto, `z-ai/glm-5.2` (WF-20260727-003327-207241) | 2 | fronteira de confiança; analogia cross-domain | rodou 2/2, **reduce rejeitado no schema** |
| C | `research-critique` (seeded) | — | a decidir | não planejada |

Desvios do caminho default, todos por medição:

- `--executor` fixa a run inteira e nenhum papel de roteamento aponta para
  `nvidia-compat`; sem `--executor` a resolução cai em `generic`, que é
  `runnable: false`. Daí duas waves.
- Wave B foi pela receita de packet-worker do overseer-playbook em vez de
  `workflow run`: `--executor nvidia-compat` resolveria para
  `stepfun-ai/step-3.7-flash` (o `defaultSpawn` barato) e não há flag de modelo
  no `run`. Chamada direta deu `z-ai/glm-5.2`, o tier "primary smart".
- A receita do playbook manda ler a chave de `.env`; `.env` não existe mais —
  `keys-keyring v2` moveu para o vault do OS. Usei `keys_vault.vault_get`.
  **A receita do playbook está desatualizada.**

## Resultados

### Convergência independente (o achado forte)

Os quatro workers, em dois vendors, chegaram ao mesmo diagnóstico de CLASSE: o
defeito não é o conteúdo da lista, é a **polaridade**. Wave A chamou de
"polaridade allowlist"; wave B, de "enumeração vs. derivação" (analogia com a
hermeticidade do Bazel: o conjunto de entradas é derivado do fecho transitivo,
não enumerado). Convergência entre modelos que não se viram é o sinal mais forte
que esta rodada produziu.

### Proposta sobrevivente (worker A-001, lente simplicidade)

**Inverter a polaridade**: superfície = árvore rastreada MENOS o glob `exclude`
que **já existe** na policy. Mata o conceito de `surfaceRoots`-como-lista-curada
em vez de alargá-lo.

- `project.json` fica coberto **por construção**, não por caso especial — fecha
  `wf-policy-self-coverage` sem regra dedicada.
- Caminhos sem profile explícito caem num profile `other` → `[spec-pack]`
  (19,5s), nunca no DRUM de cenários.
- A sujeira crônica vira **2 excludes NOMEADOS**, e o precedente já está no
  arquivo: `.harness/state/quality-state.json` já é excluído por caminho exato,
  não por raiz. Exclude-por-arquivo é padrão aceito no repo, não exceção nova.

### O mecanismo que ninguém tinha visto (worker A-001)

`validation_stamp.VALIDATOR_INPUTS` **já inclui** `.harness/project.json` — a
intenção de que uma mudança de policy invalide todo stamp antigo já está
declarada no código, em `:34-39`. Mas a linha que a lê (`:229`) é **inalcançável**
enquanto `project.json` estiver fora do próprio `surfaceRoots`: o curto-circuito
de `:212` acontece antes. O repo já quis o comportamento certo; o curto-circuito
o engole.

### O requisito novo (worker A-002, lente confiabilidade)

O bypass é **invisível à observabilidade do próprio gate**. `"staged surface
unchanged vs HEAD"` é um retorno de tupla e um print — nada é persistido em
`quality-state.json` quando acontece. O único outro observador desses caminhos é
o `delivery_bar_advisor`, cujo exit code é sempre 0. **Não existe ledger.** A
única forma de notar a recorrência foi esta arqueologia manual, e é por isso que
foram quatro registros em cinco dias sem ninguém ligar os pontos. Portanto o
conserto precisa de um **registro de bypass**, não só de superfície mais larga —
senão a próxima regressão também só aparecerá por arqueologia.

### Contra-argumento honesto (worker A-002)

Alargar a superfície **aumenta a frequência de exposição a duas falhas parciais
já conhecidas** do próprio `gate_staged`, ambas com incidente real citado no
código: o gate-hold órfão de um foreground morto por timeout (`gate_staged.py`
docstring) e o guard `gate-while-dirty` de 2026-07-22 (`_staged_but_modified`).
Mais superfície = mais gates = mais chances de encostar nesses dois.

### O dente falsificável já tem precedente pronto (worker A-001)

`gate_checks_policy.py:89-129` e `:262-283` **já leem `.harness/project.json` ao
vivo** via `json.loads`. O mecanismo de check-contra-policy-viva existe e roda no
tier de 19,5s; só não está aplicado a `precommitValidation`. Isso mata a objeção
"é mecanismo novo" e evita a armadilha de tautologia do critério 4 (todo cenário
de gate hoje usa `POLICY` hardcoded — `pvg_precommit_gate.py:32`).

### Correção do piso de evidência desta rodada

O worker A-001 flagou uma inconsistência **minha**: eu disse "11 de 12 protegidos
fora da superfície"; ele contou 10. Reconciliado — são **duas listas**:
`project.json#/protectedFiles/defaultProtectedFiles` (10) e
`.harness/protected-files.json#/protectedFiles` (12, superset que adiciona
`harness-operator.md` e `py-run.sh`). Meu número estava certo para a segunda, o
dele para a primeira. Mas a divergência é real e latente: **nada força as duas a
concordarem**, e existe ainda um terceiro mecanismo (`protectedPatterns`, 24
entradas) que ninguém reconciliou. Candidato a registro próprio.

### Defeitos da própria máquina de pesquisa (achados por rodá-la)

1. **`workflow plan --validate-only` diz `valid: true` sem checar o teto do
   prompt do REDUCER.** O `token-audit` reprovou depois (2089/2000). Duas
   replanejadas até caber. Mesma doença do tema investigado: o check que existe
   não cobre o que parece cobrir.
2. **O perfil de divergência não impede colapso de diversidade.** `concurrency:1`
   + diretório de WF compartilhado fizeram o worker A-002 **ler o result do
   A-001 antes de escrever** — ele próprio declarou isso no summary. O playbook
   proíbe `--seed` em divergência exatamente para preservar geração
   independente (Diehl & Stroebe 1987; Diversity Collapse arXiv:2604.18005), mas
   a proibição cobre só a flag, não o sistema de arquivos. A wave B, por rodar
   como dois POSTs isolados, foi a única geração genuinamente independente.
3. **O contrato WORKER_RESULT proíbe na prática que um worker packet-only emita
   finding `high`/`blocker`**: exige `sourceFilesVerified`, campo que um worker
   HTTP sem acesso ao repo nunca pode preencher legitimamente. A wave B inteira
   foi rejeitada por isso (`"sourceFilesVerified required when high/blocker
   findings are present"`), com 12 findings de conteúdo real descartados do
   reduce. Pior: isso **explica** as tags `[repo]` indevidas que os workers
   NVIDIA colocaram em evidência vinda do packet — o contrato **pressiona** o
   worker a alegar uma verificação que ele não fez. A perna barata multi-vendor
   hoje é ou inútil para achado sério, ou uma fábrica de procedência falsa.
4. Menor: um result inteiro e válido (4 findings verificados) foi rejeitado
   porque **uma** string de metadado advisory tinha 284 chars contra teto de 200 —
   e o conteúdo dela era o worker sendo honesto sobre o que não conseguiu
   reverificar. Aparei o campo para 195 chars e revalidei; o original está
   preservado no registro desta rodada.

## Phase 4 — Crítica (WF-20260727-005548-798831 parcial + WF-20260727-010246-293733)

Painel: 1 crítico de validade em **Sonnet 5 high** (controle mesmo-modelo — é o
tier que gerou a proposta) + 3 críticos em **Opus 5 xhigh** (arquitetura, custo,
segurança), com `--allow-frontier` autorizado pelo dono. Brief **idêntico** para
os quatro, sem repassar achados entre eles: convergência entre modelos vira
sinal, não eco.

Nota de roteamento: não existe role com opus em `high` — todo pin de
`claude-opus-5` é `xhigh`. Rodou em xhigh, mais esforço que o pedido, não menos.

### Veredito: P1 NÃO fecha a classe. Três críticos independentes derrubaram a alegação central.

**Blocker 1 — o control-plane do próprio gate está excluído por glob, antes e
depois de P1.** `exclude` contém `tools/git-hooks/**`; `git ls-files
tools/git-hooks` retorna `pre-commit` e `post-commit`, **rastreados**. O modelo
"árvore menos exclude" herda essa exclusão intacta. `tools/git-hooks/pre-commit`
tem 3 linhas e faz `exec` do gate — trocar por `exit 0` desliga gate, reckon e
auditoria pós-commit de uma vez. E `VALIDATOR_INPUTS` (`validation_stamp.py:34-39`)
não lista hook nenhum, então a edição também não invalida stamp algum. *(crítico
segurança, confiança forte, medido)*

**Blocker 2 — o profile `other` não é config, e com `gates: []` o gate carimba
verde tendo rodado zero checks.** A allowlist não morre: migra de `surfaceRoots`
para `profiles.roots`, e `required_profile()` precisa de mudança de CÓDIGO. Pior,
o caminho de lista de gates vazia transforma um bypass **visível**
(`"surface unchanged"`) num bypass **invisível** (um stamp verde afirmando
validação). *(crítico arquitetura)*

**Blocker 3 — P1 criaria CERTIFICAÇÃO FALSA em 15% dos commits.**
`scenario_isolation.py:167-184` documenta no próprio comentário que caminhos sob
os diretórios segurados *"run at HEAD content during the scenarios gate"*; só
`docs/IMPLEMENTATION_BACKLOG.md` é re-materializado do índice (`:202-204`).
Medido pelo crítico: **108 de 710 commits em 30 dias (15%)** estagiam
simultaneamente arquivos de superfície e caminhos sob
`.harness/{state,context,runtime,routing,handoff}`. Hoje isso é um aviso
impresso. Com `.harness/` DENTRO da superfície, `stamp_staged` (`:748-755`)
passa a **afirmar** que esses arquivos foram validados — quando a bateria
provadamente rodou contra HEAD. É o intake irmão `d783b80d7748` (23/07)
materializado como consequência do conserto. *(crítico custo, forte)*

### Armadilhas na codificação concreta

- **`surfaceRoots: []` — a codificação natural de "árvore inteira" — é falsy em
  Python e cai silenciosamente em `SURFACE_DEFAULT` (`:28`), que **não tem
  `ui`**, reabrindo exatamente o buraco que `400e302` fechou. Três call sites com
  o mesmo `or`: `:101`, `:117`, `:685`. Codificar como `["."]` e deletar/repontar
  `SURFACE_DEFAULT` no mesmo commit.
- **Os 2 excludes nomeados não bastam** — achado por Sonnet e por Opus
  independentemente (convergência): o gate declara **20 arquivos rastreados**
  voláteis, e o de maior churn fora da superfície é o próprio
  `docs/IMPLEMENTATION_BACKLOG.md`. O bloqueio ainda cai DEPOIS do launch.
- **`validation_stamp.py` não está em `VALIDATOR_INPUTS`** — o módulo que define
  o manifesto, o matcher de exclude e o mapa de profiles não invalida stamp quando
  muda.
- **P1 degrada a métrica de narrowing do SPEC-159**: `surfaceRoots` não é local ao
  gate, é domínio de entrada do shadow da Fase 2.

### P2 e P3 também levaram correção

- **P2 (ledger) tem armadilha de localização**: `.harness/state` está DENTRO do
  hold que o gate restaura — e o precedente exato está documentado em
  `validation_stamp.py:274-283` (o `reckon-results.jsonl` vive em `.harness/runs`
  justamente por isso). Gravar o ledger de bypass em `.harness/state` = o gate
  apaga a própria trilha de auditoria. Destino correto é `.harness/runs/`, com o
  custo de ser local-only (`.gitignore:38`). E precisa logar **também** o ramo
  `policy is None` (`:209`/`:334`), não só `staged==head` — senão o bypass mais
  barato fica fora do registro.
- **P3 é satisfazível com a superfície destruída** e seu precedente citado é um
  advisory que nunca falha. O dente, como enunciado, não pina o que deveria.

### Reversibilidade (medida)

Voltar P1 é barato; voltar P3 não — e a volta stala todo stamp existente. O dente
P3 chega a **bloquear o próprio rollback** se `project.json` for revertido
sozinho.

### Operações por card (pós-crítica)

| Card | Origem | Operação |
|---|---|---|
| Inverter polaridade (tree-minus-exclude) | A-001 | **dividida** — a ideia sobrevive, a proposta não. Vira 4 pré-condições nomeadas abaixo. |
| Ledger de bypass | A-002 | **mantida com correção** — destino `.harness/runs/`, e logar o ramo `policy is None` também |
| Control-plane do gate na superfície | crítico segurança | **NOVA, precede tudo** — sem ela, "fecha a classe" é falso |
| Re-materialização do índice para caminhos segurados | crítico custo | **NOVA, precede P1** — senão o stamp vira certificação falsa em 15% dos commits |
| `["."]` + morte do `SURFACE_DEFAULT` | crítico custo | **NOVA** — sem ela a codificação óbvia reabre o buraco do `ui` |
| Profile `other` | A-001 | **reclassificada** — mudança de motor, não de config; nunca com `gates: []` |
| Auto-inclusão do manifesto | B-002 | **rejeitada** — a policy é lida do WORKTREE e falha aberta; pertencer ao manifesto não fecha o caso auto-referencial |
| Grafo content-addressed (Bazel) / cquery | B-002 | **adiadas** — mantidas; nada na crítica as promoveu |
| Anotação estilo `.gitattributes` | B-002 | **rejeitada** — `exclude` já faz isso |
| Reconciliar as 3 listas de proteção | orquestrador | **dividida** — registro próprio |

**Nenhuma implementação recomendada nesta rodada.** O que a rodada entrega é um
enunciado de problema muito mais preciso e quatro pré-condições que qualquer
conserto tem que satisfazer antes de tocar em `surfaceRoots`.

### Defeito 5 da máquina de pesquisa (o mais caro)

**Dos 8 workers rodados, 6 tiveram o result rejeitado no schema** — e os 8
produziram conteúdo utilizável. Wave B: 2/2 (`sourceFilesVerified` exigido para
`high`/`blocker`, impossível para worker packet-only). Wave A: 1/2 (string de
metadado 84 chars acima do teto). Crítica Opus: **3/3** (`maxWorkerOutputChars`
15371>12000 + `frictionObservations`). Ou seja: a onda que o dono pagou em
frontier teve 100% dos results formalmente descartados, com os achados blocker
desta seção salvos apenas porque o orquestrador leu os arquivos à mão. Os tetos
existem por boa razão (custo de contexto do reducer), mas hoje eles descartam o
trabalho INTEIRO em vez de degradá-lo — não há truncamento, spill nem "aceite
parcial com aviso". Candidato a registro próprio, e não é sobre gates.

## Phase 5 — Síntese

### O que a rodada realmente descobriu

O defeito não é `surfaceRoots`. Os cinco pontos cegos abaixo são **um só**: o
gate não enxerga, não valida e não lembra nada do próprio substrato.

| Camada | Mecanismo | Onde o gate é cego |
|---|---|---|
| Execução | `tools/git-hooks/pre-commit` (3 linhas, `exec` do gate) | excluído por glob; ausente de `VALIDATOR_INPUTS` |
| Configuração | `.harness/project.json` define a superfície | fora da própria superfície; lida do worktree, falha aberta |
| Implementação | `validation_stamp.py` define manifesto, exclude e profiles | ausente de `VALIDATOR_INPUTS` |
| Memória | o curto-circuito não persiste nada | nenhum ledger; único observador (`delivery_bar_advisor`) tem exit 0 fixo |
| Validação | caminhos segurados rodam com conteúdo de HEAD (`scenario_isolation.py:167-184`) | a bateria não valida o que o stamp afirmaria |

**Cada buraco veio de uma decisão local correta.** Excluir `tools/git-hooks/**`
evita churn de artefato instalado; segurar `.harness/` impede que cenário veja o
estado vivo do dono; `.harness/state` está no hold porque é runtime; a allowlist
existe para doc não girar o DRUM. Todas defensáveis isoladamente. A composição é
um gate que não se valida — e é por isso que a classe reincide **sem que ninguém
tenha errado**. Não se conserta sendo mais cuidadoso.

### O padrão maior (síntese do orquestrador, não achado de worker)

A rodada encontrou a mesma doença em seis camadas independentes: **checks que
parecem cobrir o que não cobrem.**

| Instância | Aparência | Realidade |
|---|---|---|
| `check_staged` / `check_reckon` | `pass` | nenhum check rodou |
| `workflow plan --validate-only` | `valid: true` | teto do prompt do reducer não é checado (reprovou depois em 2089/2000) |
| Contrato `WORKER_RESULT` | "0 workers válidos" | 8/8 produziram conteúdo utilizável; 6 descartados por teto de formato |
| `delivery_bar_advisor` | avisos R1-R6 | exit code sempre 0 |
| SPEC-159 Fase 2 | seletor de afetados | `narrowing=0` em SHADOW; não seleciona nada |
| `spec-pack` no `project.json` | escopo declarado inclui "routing consistency" | não está ligado a essa superfície |

Esta é a alegação mais transferível da rodada e ela não é sobre gates.
Classe de confiança: **moderada** (seis instâncias medidas nesta sessão;
generalização é `judgment`).

### Matriz de rastreabilidade

| Evidência | Problema | Ideia | Spec/ADR | Task | Status |
|---|---|---|---|---|---|
| `exclude` tem `tools/git-hooks/**`; `git ls-files` mostra `pre-commit`+`post-commit` rastreados; 2 commits de churn na história inteira | control-plane do gate desligável sem invalidar stamp | tirar do exclude + `VALIDATOR_INPUTS` ganha hooks e `validation_stamp.py` | emenda SPEC-137 | `gate-controlplane-excluded` | **shipped 2026-07-27** |
| curto-circuito é tupla+print; nada persistido; 4 registros em 5 dias só por arqueologia | recorrência indetectável | ledger de bypass em `.harness/runs/` (hold-imune, precedente `:274-283`), logando `staged==head` E `policy is None` | emenda SPEC-137 | `gate-bypass-ledger` | **shipped 2026-07-27** |
| `scenario_isolation.py:167-184` "run at HEAD content"; 108/710 commits (15%) estagiam superfície + `.harness/` juntos | alargar a superfície viraria certificação falsa | re-materializar o índice para caminhos segurados | — | pré-condição 2 da row de classe | aberto (era intake `d783b80d7748`) |
| `SURFACE_DEFAULT` (`:28`) sem `ui`; 3 call sites com `or` (`:101/:117/:685`) | `surfaceRoots: []` é falsy e reabre o buraco de `400e302` | codificar `["."]` e matar o default no mesmo commit | — | pré-condição 3 da row de classe | aberto |
| `required_profile()` casa por prefixo de `profiles.roots`; `gates: []` carimba verde | profile `other` é motor, não config | mudança de código, nunca `gates: []` | — | pré-condição 4 da row de classe | aberto |
| 6 de 8 workers rejeitados no schema, 8/8 com conteúdo utilizável | o contrato descarta em vez de degradar | truncar/spill/aceite parcial com aviso | — | `wr-schema-discards-work` | aberto |
| `project.json` 10 protegidos vs `protected-files.json` 12 vs 24 `protectedPatterns` | três listas, nada as reconcilia | reconciliação + dente | — | `protection-lists-reconcile` | aberto |
| `concurrency:1` + dir de WF compartilhado → A-002 leu o result de A-001 | proibição de `--seed` cobre a flag, não o filesystem | isolar dir de worker em divergência | — | `wf-divergence-shared-dir` | aberto |
| `token-audit` reprovou o que `--validate-only` aprovou | teto do reducer fora do validate | mesma checagem nos dois | — | `wf-validate-only-reducer-ceiling` | aberto |
| receita GLM manda ler `.env`; `keys-keyring v2` moveu para o vault do OS | receita quebrada no playbook | apontar para `keys_vault.vault_get` | — | corrigido inline nesta sentada | fechado |

### Recomendação de sequência

1. **Nada de superfície ainda.** Toda proposta desta rodada estava errada sobre
   fatos que dava para medir; a correção óbvia teria criado certificação falsa
   em 15% dos commits.
2. **Ledger primeiro** — única peça que saiu inteira da crítica, reversível, não
   toca em `surfaceRoots`. Doutrina do próprio repo (`wf-gate-observability`,
   SPEC-158: *can't exploit a constraint you can't see*).
3. **Control-plane** — fix de segurança independente do redesenho.
4. **Só então a superfície**, com dados do ledger e as 4 pré-condições como
   critério de aceitação.
