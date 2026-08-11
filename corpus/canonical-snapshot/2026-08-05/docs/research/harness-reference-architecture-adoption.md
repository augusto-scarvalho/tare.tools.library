# Rodada — adoção do artigo de referência de harness multi-agente

Estudo "o que devemos adotar de X" (playbook `.harness/prompts/research-playbook.md`).
Fonte externa: *Adaptive, Project-Oriented Multi-Agent Harness Architectures with
Dynamic Routing, Self-Correction, and Governed Self-Evolution* — manuscrito v1.6,
cutoff 2026-07-17, síntese multivocal + protocolo DSR (lido integralmente,
2.414 linhas). Fonte interna: inventário de capacidades do repo (scanner, 2026-07-17).

**Status: GATE APROVADO pelo owner em 2026-07-17** ("aprovado tudo; começar pelo
mais crítico; revisitar o artigo conforme evoluirmos"). Decisões: núcleo N1-N6 na
ordem proposta; EXP-15/16/17 registrados (E1-E3); EXP-1 fase 2 com luz verde;
promoção direta sem wave de crítica; visão M0-M7 vira D008 em DECISIONS.md.

**Execução (iteração 1, 2026-07-17):** N1 verificado JÁ ENTREGUE (CE.1 corrigido
em 2026-07-12 — seam `_record_executor_outcome`, cenário `ce1_containment.py` 5/5;
a linha do backlog estava desatualizada e foi riscada). N2 SHIPPED: fallback
genérico `*_escalation` em `compact_supervision_events` (CE.8-lite; check essc-6)
— qualquer raise com escalationId sobrevive ao wipe sem branch por tipo.

## ATUALIZAÇÃO DE FATO 2026-07-18 — o codex alcançou o claude (doc estava velho)

Owner sinalizou; investigado por fontes primárias (Codex CLI 0.143–0.144, 8–9
jul 2026). **Várias suposições desta rodada sobre "codex = vendor mais fraco"
ficaram FALSAS.** O que o codex ganhou nativo esta semana:

- **Subagents GA** — `.codex/agents/*.toml` (campos `name`/`description`/
  `developer_instructions` + `model`/`model_reasoning_effort`/`sandbox_mode`/
  `mcp_servers`/`skills.config` por agente). `[agents]` config: `max_threads`=6,
  `max_depth`=1. **Estrutura irmã do `.claude/agents/*.md`.**
- **Fork-join nativo** — paralelo com "waits until all results available, then
  returns a consolidated response"; `spawn_agents_on_csv` (map por linha com
  `output_schema`). Multi-agent **v2** sob namespace `collaboration`.
- **Dynamic workflows** — thread forking ("fork history through a specific turn").
- **Hooks completos** — SessionStart, PreToolUse, PermissionRequest, PostToolUse,
  UserPromptSubmit, **SubagentStart, SubagentStop, Stop**, PreCompact, PostCompact.
- **Sandbox** — "writes app approval mode" + worktrees (`.worktreeinclude`).
- **Nosso CE.1 consertado nativamente**: julho — "parent agents now receive
  terminal subagent errors instead of an empty successful completion".

Fontes: learn.chatgpt.com/docs/agent-configuration/subagents ; .../changelog ;
developers.openai.com/codex/hooks.

**Correções pendentes (fila de decisão nova):** (A) `capabilities.json` nota
"codex síncrono, sem SubagentStop, sem mirror" agora é FALSA — codex tem
SubagentStop; re-avaliar a perna codex do gate-wait hook (commit f016aa9). (B)
`agent_spawn_economy` casa `multi_agent_v1` — verificar rename p/ v2. (C) esta
seção. Apostas p/ direção do owner: (D) adotar fork-join/subagents nativos do
codex; (E) paridade SPEC-113 nativa via `.codex/agents/*.toml`. Ressalva a
confirmar antes de mexer em hook: o SubagentStop do codex dispara no runtime
INTERNO de multi-agente dele; nós invocamos `codex exec` single-shot — se esse
caminho dispara os eventos é o que decide a perna codex do gate-wait.

### Investigação experimental 2026-07-18 — "codex tem hooks" ≠ "codex enforça"

Rodei codex 0.144.4 DE VERDADE (5 execs) pra testar, não só ler docs. Achado que
inverte o otimismo: **o enforcement de escrita dos nossos codex workers está
INERTE, e não conserta só por wiring.** Três gaps, todos provados ao vivo:

1. **Trust** — `codex exec` só dispara hooks com `--dangerously-bypass-hook-trust`
   (ou trust persistido). Experimento 1 (sem flag): NENHUM hook disparou.
   Experimento 3 (com flag): SessionStart/PreToolUse/Stop dispararam. Nosso
   template não passa o flag → hooks do codex worker hoje são **mudos**.
2. **Matcher** — `protect-files` tinha matcher `Edit|Write|MultiEdit` sem
   `apply_patch` (a ferramenta de edição nativa do codex). CORRIGIDO nesta sessão
   (capabilities.json + vendor files, timeouts preservados; `agents pair --apply`
   é lossy nesses campos — intake).
3. **Payload-shape (o matador)** — mesmo com trust + matcher, o `protect_files`
   NÃO negou: `codex exec` editou o AGENTS.md protegido com o hook totalmente
   ligado. Raiz: o `apply_patch` do codex embute o path no CORPO do patch
   (`*** Update File: <path>`), não num campo `file_path`; `protect_files.
   candidate_paths()` (e o `workflow_write_guard`) só leem `file_path`/`path` →
   não acham o alvo → fail-open. O deny por exit-2 do hook é honrado pelo codex
   (a doc confirma), mas o hook nunca chega a negar porque não vê o alvo.

**Consequência:** codex workers podem escrever em qualquer lugar (incl. arquivos
canônicos protegidos) hoje. Corrigir exige um **parser do corpo do apply_patch**
em `protect_files` + `workflow_write_guard` (extrair `*** Update/Add/Delete File:`
e `+++ b/<path>`), MAIS o flag de trust — não só espelhar o hook. NÃO ativei o
trust (daria falsa segurança com o gap 3 aberto). O que fica correto e commitado:
o matcher fix (pré-requisito) + as notas corrigidas. Intake capturado. Implicação
p/ D/E: a contenção de codex worker deve vir do **sandbox NATIVO** dele
(`sandbox_mode` read-only/workspace-write, "writes app approval"), NÃO dos nossos
hooks path-based — o S3 (sandbox nativo por role) é a alavanca certa pro codex.

### CONCLUSÃO DECISIVA 2026-07-18 (parser construído + provado; sandbox é o requisito)

Continuei experimentando (8 execs no total). Fatos provados ao vivo:
- Capturei o payload real do apply_patch: alvo em `tool_input.command` como
  `*** Update File: <path abs>` (não em `file_path`). **Construí o parser**
  (`protect_files.apply_patch_paths` + `candidate_paths`, self-check verde) —
  extrai o alvo corretamente.
- **MAS mesmo com parser + matcher + trust, o `protect_files` NÃO bloqueou** o
  codex editando AGENTS.md (3 testes). O payload mostra `permission_mode:
  bypassPermissions` — o codex **não honra o deny de hook** nesse caminho.
- **`--sandbox read-only` BLOQUEOU** ("No file change was possible"). → o
  sandbox nativo é o controle CONFIÁVEL de escrita no codex; **hooks no codex são
  advisory, não enforcement.**

**Arquitetura de contenção que cristaliza (o requisito multi-vendor + open models
do §5.9/§7.4/§7.5):**
| Camada | claude | codex | open models (HTTP) |
|---|---|---|---|
| Vendor-nativa (inner) | allowedTools + permission-mode (deny honrado) | `sandbox_mode` (S3) — ÚNICO controle confiável de escrita | **NENHUMA** |
| Hooks path-based | enforça (deny honrado) | **advisory só** (deny ignorado) | não roda |
| **Harness-own sandbox (REQUISITO)** | reforço | cobre "protegido off-limits" que o workspace-write não cobre | **A ÚNICA contenção possível** |

**Requisito confirmado:** os open-model workers (openai-compat/nvidia/gemini) não
têm sandbox nem hooks — só um **sandbox do harness** (fs/proc/net confinado no
spawn, vendor-agnóstico; §5.9 runtime plane MANDATÓRIO) os torna seguros. É
pré-requisito pra multi-vendor + open models juntos. O parser fica commitado como
**building block** do harness-own sandbox (feed do que o worker tenta escrever),
não como enforcement de hook no codex. Próximo: desenhar o harness-own sandbox
(SPEC-116 door NEW) + estender S3 pro `sandbox_mode` por role nativo do codex.

**EXP-1 fase 2 (mesma sessão): implementada, medida e REVERTIDA** — os candidatos
head+tail perderam MAIS linhas decisivas que o head-only no corpus real (345 e
335 vs 312; única amostra firing é um gate doc gigante com head denso em paths).
Primeira aplicação viva da disciplina D008: a métrica decide, o candidato não
embarca; ficou preservado no probe (`truncate_text_head_tail`) com o achado de
validade da métrica e o caminho de re-teste (enriquecer corpus com outputs
OUTPUT_CAP de chat/ui, ou métrica ponderada de cauda pré-registrada).
**N3 SHIPPED (mesma sessão, escopo mínimo pós fan-out de 3 recons):** o "epoch
geral" foi honestamente descartado — nenhuma identidade é compartilhada entre os
5 ledgers, e só os dois gaps COM incidente foram fechados: (F1) guard de
dispatch duplicado no `tasks_board._dispatch` — o fix do incidente a6c9af5 só
tinha sido aplicado no caminho de experimento, o irmão dos task cards ficou
aberto; (F2) `_recover_stale_holds` agora recusa (alto) recuperar hold de pid
VIVO — vira também o mutex entre gates concorrentes que faltava. Diferidos com
registro (sem incidente, C-level): fencing do breaker por executor (last-write-
wins entre runs), lost-updates dos ledgers (experiments/tasks/handoff), lock
presence-only do route-loop (teto aceito, sobre-bloqueia). U1/U2 shipped em
2af7787 (delegação Opus xhigh + ritual).
Próximos: N4 como probe read-only de regret retrospectivo (alimenta EXP-17,
zero mudança de comportamento), N5/N6.

## Trilha S — contenção, isolamento e reforço de roles (pedido do owner 2026-07-17)

Releitura do artigo com foco em sandbox/capacidades (§5.5 delegação por
capacidade; §5.7 semântica de recursos; §7.3 trust zones; §7.4 defesa em
profundidade; §7.7/SF-5e contenção > fadiga de aprovação; Rule of Two [119];
CaMeL [118]) × 2 recons fan-out (enforcement de roles; sandbox/env/egress).

Diagnóstico: o reforço de role era ~todo prosa (SPEC-140/142/143 auto-declarados
não-aplicáveis; 1 de 9 perfis com teto `tools:`); o único bloqueio real era o
glob do ui-overseer (Edit/Write via allowedTools — Bash segue não confinado por
path); o filtro least-privilege de env (SPEC-119 `filter_spawn_env`) existia mas
só no caminho workflow-worker — dispatch detached e rooms herdavam o env
completo com todos os segredos.

| ID | Item | Status |
|---|---|---|
| S1 | Env least-privilege no dispatch detached (`cmd_route` → `build_worker_spawn_env`; escape hatch `workerEnvFilter=false` mantido) | **shipped nesta sessão** |
| S2 | Teto `tools:` nos 8 perfis restantes de `.claude/agents/` (leitura: sem Edit/Write; escrita: sem spawn; enforcement = runtime do Claude) | **shipped nesta sessão** |
| S3 | Sandbox codex dirigido pela classe da role: `--sandbox {sandbox}` no template + `writeAllowed` do worker decide read-only/workspace-write nos 3 pontos de render (worker, spawn_command, triage router). Descoberta: o hardcode read-only quebrava roles de ESCRITA em codex — paridade era nos dois sentidos. Perna claude: constraint MEDIDA do SPEC-118 v6 mantida (não negar Edit/Write em worker — WORKER_RESULT vai por arquivo); teto claude = frontmatter S2 + hook `workflow_write_guard` já existente. Nenhum hook novo necessário (argv cobre); candidato a hook que segue diferido: path-guard de Bash p/ rooms confinadas | **shipped nesta sessão** |
| S6 | Rule-of-Two no floor do porteiro: 2-de-3 de {untrusted-input, sensitive-access, external-effect} → flag `rule-of-two` no `deterministic_floor` → escalate (route_decision já honra qualquer riskFlag; net de keywords, só RAISE). Bi-vendor por construção (pré-spawn, vendor-agnóstico); sem hook/perna codex — é decisão de rota, não flag de argv | **shipped nesta sessão** |
| — | Diferidos com registro: egress geral de workers (SEC.1 cobre só discover; MCP/A2A doc-only), Bash não-path-confinado do ui-overseer (`git add -A` — contenção social + gate), env das rooms interativas (quebra engines sem teste por engine), workers HTTP crus sem sandbox algum | — |

Limite honesto (o artigo idem): teto de tools com Bash liberado não é read-only
estrito — remove a via primária de escrita, o gate pega o resto; container/chroot
real é aposta futura (gatilho: multi-tenant ou incidente de escape).

## Fase 0 — Pergunta, critérios, orçamento

- **Pergunta:** quais mecanismos do artigo de referência fecham lacunas reais do
  nosso harness, em ordem de criticidade para o core (roteamento, delegação,
  validação, evolução governada), sem importar over-engineering acadêmico?
- **Critérios de sucesso:** (a) cada item do roadmap rastreia para uma claim do
  artigo COM estado atual do repo apontado; (b) contra-evidência do artigo vira
  bucket `rejeitadas` explícito; (c) itens caros só entram como aposta com gatilho;
  (d) experimentos seguem o template do registry (hipótese/baseline/métrica/decisão).
- **Orçamento declarado:** rodada executada inline (artigo ~90k tokens de leitura +
  1 scanner ~52k). Waves de Develop/Critique: **0 gastas** — o artigo já é o produto
  de uma divergência+crítica externa (evidência estratificada A–E, 46 hipóteses);
  re-gerar ideias seria custo sem informação nova. Wave de crítica opcional fica
  cotada no gate (1 wave research-critique ≈ 60k tokens).

### Natureza da fonte (limite de confiança)

O artigo é **síntese conceitual + protocolo**, não resultados originais: as claims
citam evidência A (padrões/seminais), B (peer-reviewed), C (preprints 2025-26),
D (vendor). Preprints C são hipóteses, não lei. O artigo é honesto sobre isso — e
nós herdamos o mesmo dever: nada abaixo vira "verdade", vira mecanismo + gatilho.

## Fase 1 — Matriz de evidências (claims que dirigem o roadmap)

Formato: `claim | fonte | confiança | estado no repo`. Prefixos [web] = artigo
(untrusted-until-verified nos primários), [repo] = apontador verificado, [judgment].

| # | Claim | Fonte (nível do artigo) | Confiança | Estado no repo |
|---|---|---|---|---|
| C1 | Comando emitido ≠ efeito observado; todo efeito externo exige receipt tipado, falha reconciliada ou estado `unknown` — nunca inferido do rc | [web] §5.7, invariante 18, H19 (A: Sagas; D: runtimes duráveis) | forte | [repo] **violado**: CE.1 P0 — worker failed/rejected com rc=0 grava *success* (`async_runtime.py:505-524`) |
| C2 | Eventos de trajetória são append-only; evento sem pai é quarentenado, nunca descartado | [web] §8.1 regras 1/6 (A: PROV, OTel) | forte | [repo] **violado**: CE.8 — events.jsonl transiente derruba SECURITY_ALERT/FAILURE em wipe |
| C3 | Cada task tem exatamente um dono; epoch monotônico de ownership age como fencing token — run velho não commita | [web] §5.7 (A: leases/fencing, Gray) | forte | [repo] parcial ad-hoc: lock por pid vivo no card (incidente 4 do dispatch), gate-hold, stop-hook fail-open; sem epoch geral |
| C4 | Routers sofisticados frequentemente empatam com baselines simples; medir regret/calibração ANTES de sofisticar | [web] §4.2, SF-2/3a (B: LLMRouterBench; C: kNN-router) | moderada | [repo] SPEC-144 router live sem feedback de outcome; RF.1 fase 2 owner-gated; zero logging contrafactual |
| C5 | Ganho multi-agente pode ser artefato de sampling: exige baseline single-agent com orçamento igualado | [web] §4.4, SF-5a (C: 180-config scaling study; equal-budget 2026) | moderada | [repo] ausente: waves map-reduce sem controle single-worker de mesmo budget |
| C6 | Contexto de repo gerado automaticamente REDUZ sucesso e sobe custo 20-23%; contexto mínimo curado por dev ganha | [web] §4.1, SF-1a (C: AGENTS.md study, Python-centric) | moderada | [repo] **alinhado**: context budget policy + CONTEXT.md enxuto já são a prática |
| C7 | Memória append-only propaga erro/obsolescência; lifecycle com challenge/expiry/deleção governada supera | [web] §6.2, H16 (B: MemoryAgentBench; ACL 2026) | moderada | [repo] parcial: memórias e NEXT_STEPS sem valid-until/challenge; staleness já observada (nota OneDrive) |
| C8 | Correção sem evidência externa nova = auto-confirmação; taxonomia de falha + evidence delta por correção | [web] §6.1 (B: TACL intrinsic self-correction) | forte | [repo] **alinhado** no ritual (review/oracle/gate); failure-patterns SPEC-126 cobre taxonomia parcial |
| C9 | Loop interno (correção transiente) e loop externo (mudança persistente) exigem autoridades e critérios separados | [web] §3.4, SF-6 (C: misevolution) | forte | [repo] **alinhado**: SPEC-109 anti-Hive invariant (ações fechadas reversíveis, nunca edita código/prompt/rotas) |
| C10 | Evolução persistente = experimento adaptativo: pré-registro, menor efeito relevante, separação descoberta/confirmação | [web] §6.5-6.6 (A: DOE; C: EDC proposto) | moderada | [repo] parcial forte: SPEC-116 registry já pré-registra hipótese/baseline/critérios; sem blocos de ruído nem split confirmação |
| C11 | Façade única accountable + workers inspecionáveis é o default; topologia explícita só quando muda decisão humana | [web] §4.5/5.8, SF-5d (B/C: Magentic-UI, Codellaborator) | moderada | [repo] **alinhado**: porteiro + rooms + tag [live rooms] + decide inbox ≈ AHHI; "sumiu do chat" ainda é estado real (C3) |
| C12 | Aprovação vincula digest do artefato/args canônicos; mutação invalida a aprovação (TOCTOU) | [web] §7.7 (A: reference monitor) | forte | [repo] ausente: decide inbox aprova sem binding de versão |
| C13 | Rota é tupla versionada (vendor, snapshot, harness, effort, contexto, tools, permissões, topologia, adapter); labels de effort não são comparáveis entre vendors | [web] §3.5, SF-3b (C: C3VR; D: accounting docs) | moderada | [repo] parcial: model-cards + engine por sessão nas rooms; sem pin de tupla completa nos records de delegação |
| C14 | Instrução guia; política autoriza — enforcement executável (hooks) e não prosa | [web] SF-1 (A: OPA; D: Claude hooks docs) | forte | [repo] **alinhado**: gate SPEC-137, protected-files, hooks, security-directive-map |
| C15 | Diferenças menores que o ruído de infraestrutura não replicam; medir noise floor antes de acreditar em ganhos pequenos | [web] §9.7, H20 (D: vendor infra evidence) | moderada | [repo] parcial: gate-flake lição (watchdog sob carga) já documentada; sem noise floor formal |
| C16 | Maturidade M0-M7 cumulativa: evoluir sem observabilidade/governança (M1/M2) é mutação opaca | [web] §11.3 (A: maturity-model method) | forte | [judgment] repo ≈ M2-M3 sólido, M5 parcial (priors não aprendidos), M6 embrionário (EXP registry) |

### Contra-sinais — o que o artigo manda NÃO construir agora

1. **Router aprendido/LLM-router** sem loop de feedback e catálogo curado — empata com regra/kNN (C4).
2. **Gerar AGENTS.md/CONTEXT.md por LLM** — evidência de dano líquido (C6). Valida nossa política atual.
3. **Mais agentes por default / vozes múltiplas no transcript** — amplificação de erro correlacionado (C5, C11).
4. **Memória append-only "neutra"** — propaga erro (C7).
5. **Auto-evolução ampla antes de M1/M2 completos** — misevolution (C9, C16).

## Fase 2 — Lacunas por tema (artigo × repo)

| Tema | Onde já estamos alinhados | Lacuna material |
|---|---|---|
| Efeitos/durabilidade | worktrees + merge choreography ≈ integração condicional CAID-style | **C1 receipts** (CE.1), **C2 append-only** (CE.8) |
| Ownership | pid-lock no card, gate-hold recovery | **C3 epoch/fencing geral** para runs despachados e rooms |
| Roteamento | SPEC-144 dois níveis, escalation ledger, model routing frozen | **C4 ledger de outcome/regret** (pré-req do RF.1 fase 2) |
| Orquestração | map-reduce/fork-join/rooms multi-vendor | **C5 baseline single-agent** de orçamento igualado |
| Contexto | budget policy, packet economy, calibração 3.1, EXP-1/2 | **C7 lifecycle de claims** + métrica de evidence-loss em handoff |
| Governança | gate, protected-files, owner-gated ladder, anti-Hive | **C12 approval-digest**; tiers R0-R3 implícitos, não nomeados |
| Evolução | SPEC-116 pré-registro, probes determinísticos | **C10** blocos de ruído (não comparar através de troca de snapshot) |
| UX | porteiro/rooms/decide-inbox/plan HUD ≈ AHHI | estados de lifecycle de room visíveis; takeover card L0 |
| Multi-vendor | rooms com engine por sessão, executors.json | **C13 pin da tupla de rota** nos records |
| Avaliação | token-audit, delegation trends, gate-flake lição | **C15 noise floor** formal para claims de melhoria |

## Portfólio proposto (aguardando gate — nada registrado/promovido ainda)

### Núcleo (ordem de criticidade)

| ID | Item | Evidência | Footprint estimado |
|---|---|---|---|
| N1 **P0** | Receipt discipline no async runtime: resultado de worker vira `success` só com receipt válido (schema ok + rc + result-validity); senão `failed`/`unknown` — nunca re-run silencioso a preço cheio | C1 + CE.1 já P0 no backlog | `async_runtime.py:505-524`, amendment em `agentic-async-await.md`, 1 fixture |
| N2 **P0** | Events.jsonl com classe append-only para SECURITY_ALERT/FAILURE (quarentena, não wipe) | C2 + CE.8 deferido | seam do event log + doctor check |
| N3 **P1** | Ownership epoch leve: todo run despachado/room carrega epoch monotônico; commit/record de epoch velho é rejeitado (generaliza o pid-lock do incidente 4) | C3 + 4 incidentes documentados | dispatch card + route_handoff + records guard |
| N4 **P1** | Route outcome ledger: porteiro grava {candidatos, rota escolhida, outcome final} por demanda — medir regret ANTES de sofisticar RF.1 fase 2 | C4 | `route` verb + records; zero mudança de comportamento |
| N5 **P2** | Tiers R0-R3 explícitos no vocabulário de rota/owner-gate (observacional/reversível/material/crítico) | C12, §3.5 | amendment docs + brief do router |
| N6 **P2** | Lifecycle de claims de contexto: `valid-until`/`challenged` em NEXT_STEPS/memória + advisory do doctor para claim vencida | C7 | doctor advisory (padrão EXP-2 já shipped) |

### Experimentos (template do registry; registrar como EXP-N só pós-gate)

| ID | Hipótese | Baseline | Métrica | Decisão |
|---|---|---|---|---|
| E1 | Parte do ganho de waves multi-worker é sampling, não coordenação | mesma task, 1 worker, mesmo budget de tokens (token-audit) | qualidade aceita + custo-por-sucesso vs wave | se single empata em ≥50% das classes de task → default single p/ essa classe |
| E2 | Handoff por evidence-envelope perde claims decisivos (irmão do EXP-1) | transcript bruto do worker | fração de claims/refs decisivos que sobrevivem ao reduce (evidence-loss) | perda relevante → prioriza EXP-1 fase 2 + envelope schema |
| E3 | Classificação do porteiro tem regret mensurável | "sempre inline" e "sempre room" retrospectivos | rota escolhida vs melhor rota retrospectiva, semanal | regret baixo → RF.1 fase 2 desnecessário por ora (economia) |

### Apostas de fronteira (só com gatilho)

- **A1 DGIOTS-lite:** reducer determinístico para a máquina de estados dispatch/gate-hold. Gatilho: 2+ incidentes novos de estado em 30 dias após N3.
- **A2 C3VR-lite:** pin da tupla completa de rota nos records de delegação; drift de snapshot re-abre shadow. Gatilho: 2º vendor em produção nas rooms.
- **A3 Noise floor:** controles pinados repetidos para calibrar o que é "melhoria real" no gate/bench. Gatilho: primeira claim de ganho <10% que quisermos promover. **SHIPPED 2026-07-18** (measure-only) — `testing/probes/noise_floor_probe.py` mede o Floor A (jitter de duração por cenário no `gate-perf.jsonl`: MAD + spread p95-p5) e o Floor B (spread cross-WF de uniqueRate/convergence e dos 3 scores do EXP-18); wiring de processo em `docs/EXPERIMENT_METHODOLOGY.md`.

### Contingência

- ~~Approval-digest binding no decide inbox (C12)~~ **SHIPPED nesta sessão** —
  `decision_inbox`: cada row do pending carrega `digest = sha256(kind + conteúdo
  raw)` (intake liga no `ask`, escalation em `reason`+`subject`), `apply_decision`
  ganha `expected_digest` que RECUSA em mismatch (`invalidated`), flag CLI
  `decide --expected-digest`. Fecha o TOCTOU do §7.7 sem novo estado (padrão
  `plan_gate.planSha256` portado). Follow-up (UI, candidato Opus): o card
  Decisions do painel auto-passar o digest renderizado — hoje o mecanismo existe
  e é opt-in via CLI; a perna que o torna enforcement-por-default no painel é
  mudança de UI. Vendor-agnóstico (harness-core; sem perna codex, sem hook).

## Prospecção 2ª leva (recon fan-out 2026-07-18) — veredito

Duas ideias do artigo prospectadas contra o código real:

- **Approval-digest binding (C12, §7.7) → PROMOVIDO a núcleo (próximo, P1).** O
  mecanismo já existe e funciona: `tools/plan_gate.py:118` grava
  `planSha256 = sha256(plan.read_bytes())` no grant e re-checa na consumação. O
  decide inbox (`decision_inbox.apply_decision`) e o resolve de escalation gravam
  só id+choice+note — zero binding, TOCTOU aberto. Seam barato: portar o
  one-liner sha256 para `apply_decision`, mesma forma do grant, sem novo estado.
- **ContextLedger-lite / A_ctx (§4.1/§6.2) → DIFERIDO com gatilho.** CE.2
  (`cost_metrics.record_workflow`) já está shipped mas mede `communicationAmplification =
  input/output tokens` — ratio DIFERENTE do A_ctx do artigo (presented/unique). O
  denominador "unique logical tokens" não existe em lugar nenhum: `context_digest.py`
  deduplica read-lists por identidade, não conta bytes/tokens por item único. Custo
  real (contagem de tokens por entrada única no digest), não zero-state como o CE.2.
  Gatilho para retomar: pressão de budget de contexto medida, ou multi-worker onde
  a duplicação de contexto vira custo dominante (já há sinal em delegation-cost-trend).

### Estacionadas (over-engineering no estágio atual; o próprio artigo é evidence-gated)

Effective Constitution Compiler completo; workflow IR tipado com prova de soundness;
EDC completo (designs fatoriais, sealed holdouts); AHHI profiles dinâmicos por task;
ATP completo com assinatura/hash-chain. Revisitar quando houver multi-tenant real.

### Rejeitadas (contra-evidência)

Router aprendido agora; geração automática de context files; multi-agente por
default; memória append-only; auto-evolução além do anti-Hive invariant.

## Loop AFK 2026-07-18 — fila do núcleo esgotada; N5/N6 diferidos por disciplina

O loop overseer varreu a fila aprovada. Shipped: N1-N4, U1-U2, S1-S3, S6, C12
(8 commits: 4a326c5, 5b82952, 2af7787, 5e7091f, 6ca15dd, 8bec647, 7c1c960,
1f963c0); EXP-1 fase 2 medida-e-revertida; EXP-15/16/17 registrados. Os dois
últimos itens do núcleo diferiram por decisão evidence-gated (não por bloqueio):

- **N5 (tiers R0-R3 no vocabulário) — DIFERIDO.** Vocabulário puro sem consumidor
  = no-behavior-change → exit "no artifact" do SPEC-116. A escala já está
  referenciada aqui via artigo. Gatilho: um gate/owner-gate que consuma o tier.
- **N6 (lifecycle de claims + doctor advisory) — DIFERIDO.** Recon confirmou: não
  há campo de data de claim confiável; proxy por mtime de NEXT_STEPS = teatro
  (reescrito a cada workflow, sempre fresco → nunca dispara); a versão real
  (`valid-until` + mudança nos writers) é maior e especulativa sem incidente.
  Seam mapeado e clonável (padrão EXP-2 em `repo_health.checks`, id em
  `rh_repo_health.py` IDS). Gatilho: primeira claim vencida que enganar um run.

**Achado do próprio loop (intake capturado):** o hook `subagent_gate_wait.py`
(SubagentStop) segura recon read-only até o gate settlar mesmo sem tocar
`.harness` — 3 stalls medidos (~660s/32k tokens cada). Fix proposto: liberar
imediatamente subagente sem writes/mutação em `.harness`.

### Próxima leva de prospecção (candidatos, aguardando direção do owner)

> **SUPERSEDIDA 2026-07-18:** a cobertura TOTAL do manuscrito (todo item, não só
> os críticos) vive em `docs/research/article-coverage-backlog.md` — use aquele
> doc para a próxima fila. Os 4 itens abaixo ficam como histórico (1 prospectado,
> 2-3 shipped como L3/L2, 4 shipped como L4).

Itens do artigo ainda não tocados, do mais barato-e-real ao mais especulativo:

1. ~~**Co-failure reporting no reduce**~~ **PROSPECTADO E RE-ESCOPADO 2026-07-18.**
   Recon matou o β_C literal aqui por DOIS motivos honestos: (a) sem oráculo —
   status é 100% auto-reportado, "errado" não é mensurável; (b) nossos workers de
   fork-join são role-diferenciados (ideator-*, critic-*), não N tentativas
   role-simétricas da mesma tarefa que o β_C [101] pressupõe. Um "probe β_C" seria
   teatro. **Entregue a versão honesta:** `testing/probes/exp15_fanout_convergence_probe.py`
   — mede CO-DETECÇÃO de findings (via `sourceWorkerIds` que o reduce já computa),
   a pergunta de contribuição marginal (§5.5a), explicitamente NÃO β_C. Medição no
   EXP-15 (ativado): **unique-rate=1.0, convergência=0.0** nos 5 fork-joins (83
   findings, TODOS de 1 só worker). Duas leituras que o probe não desambigua: (a)
   fan-out compra cobertura pura; (b) a chave de dedup é estrita demais p/
   concordância semântica.
   **PROBE DE CANDIDATOS 2026-07-18 (LOOP QUEUE 4 L6, measure-only): hipótese de
   normalização REFUTADA.** Dois keyings candidatos medidos no corpus real (83
   findings, 5 fork-joins): `normalizedTitleCategory` (strip de prefixos
   enumerativos) fundiu **ZERO pares** — os títulos convergentes são PARÁFRASES
   ("Mock-vs-real matrix" ⇔ "flight simulator vs wind tunnel"), não enumerações;
   `categoryFirstEvidence` fundiu 1/83 (par genuíno, mas imaterial). Distância à
   verdade manual: 1.0 para os três (baseline incluso). Conclusão pro item
   OWNER-GATED: mudança de chave string em `normalize_finding_key` NÃO recupera
   convergência semântica — recomendação vira NÃO MEXER no reduce; o caminho real
   seria matching semântico (custo alto, sem gatilho). Artifact:
   `.harness/runs/exp15-dedup-candidates-*.json`.
   **DESAMBIGUADO 2026-07-18 (amostra manual do WF-...162849): (b) confirmada.**
   Os 5 workers surfaçaram AS MESMAS 5 ideias (Mock-vs-real matrix, never-failed
   inventory, weak-assert detector, BDD tightening, info-per-check) com prefixos
   diferentes — "Option A-E" / "PERF-OPT-N" / plano puro. O dedup
   (`normalize_finding_key` title+category+evidence, `workflow_reduce.py:224`) não
   fundiu porque os TÍTULOS diferem. Logo `unique-rate=1.0` é INFLADO; convergência
   real é quase-total → nesse fork-join o fan-out comprou **redundância, não
   cobertura** (sinal a favor de single-agent p/ essa classe; EXP-15). **Item
   concreto derivado (OWNER-GATED — muda comportamento do core reduce):** normalizar
   prefixos enumerativos antes de keyar, OU dedup por categoria+evidência sem
   título. Risco a decidir: over-merge de findings genuinamente distintos. Intake
   capturado. É a recomendação nº 1 para a direção do owner.
2. **Replay-class nos eventos** (§8.2) — campo aditivo `exact|approximate|external`
   por evento; barato, alinha com a disciplina de replay do ATP.
3. **Approval SLO/expiry no decide inbox** (§7.7) — aprovação expira; sem revisor
   no SLO → pausa segura. Estende o C12 recém-shipado (já temos expiry em
   plan-gate grants).
4. **Trace-completeness report** (§8.1) — R2/R3 bloqueado por evidência de
   autorização/efeito/validação ausente. Maior; depende de nomear R0-R3 (N5).

## UX (validação + 2 itens)

O desenho atual (porteiro façade → rooms explícitas quando topologia importa,
decide inbox tipado, plan HUD) **converge com AHHI de forma independente** — é
confirmação externa da direção, não lacuna. Itens novos: (U1) estados de lifecycle
de room/worker visíveis — "sumiu do chat não é estado" (junto com N3); (U2) takeover
card nível-0: objetivo, dono, próximo efeito, caminho de recovery — extensão do plan
HUD já existente.

## Visão de negócio

1. **Categoria nomeada:** o artigo estabelece "harness engineering" como objeto
   arquitetural avaliável e multi-vendor — exatamente o produto deste repo. A tese
   central do artigo (adaptação probabilística dentro de espaço de ação
   determinístico validado) é a nossa arquitetura já hoje (gate + hooks + owner-gates).
2. **Diferenciais defensáveis à luz do artigo:** camada canônica vendor-neutral
   (`.harness/`), economia cheap-first (discover/doc-find), anti-Hive invariant
   (evolução com autoridade separada — o artigo dedica seções ao risco que nós já
   fechamos por design), rooms multi-vendor (C3VR — ver atualização 2026-07-18:
   codex alcançou paridade nativa de subagents/workflows, então o C3VR deixa de
   ser embrionário e vira campo de disputa real entre dois vendors capazes).
3. **Instrumento M0-M7 como produto:** o assessment de maturidade (§11.3) é um
   framing comercializável para o `targets` verb (SPEC-110): avaliar a maturidade de
   harness de um repo adotante e prescrever o caminho. Hoje: nós ≈ M2-M3; roadmap
   núcleo fecha M2 de verdade (C1/C2 são pré-requisitos de "governed").
4. **Credibilidade por avaliação honesta:** matched-budget (E1) e noise floor (A3)
   viram material de marketing técnico raro no mercado — quase ninguém publica
   controle de sampling e ruído.

## Rastreabilidade

| Evidência | Problema | Item | Destino pós-gate |
|---|---|---|---|
| C1 + CE.1 | falha silenciosa vira sucesso caro | N1 | amendment `agentic-async-await.md` + fix |
| C2 + CE.8 | alerta de segurança some em wipe | N2 | seam event log + doctor |
| C3 + incidentes 2026-07 | run velho commita estado | N3 | spec curto ownership-epoch |
| C4 | router sem medição | N4 | amendment SPEC-144 |
| C7 | claims de contexto apodrecem | N6 | doctor advisory |
| C5/C35-36 | custo multi-agente não provado | E1/E2 | `experiment add` |
| C4 | RF.1 fase 2 sem justificativa | E3 | `experiment add` |
| C16 | posicionamento | negócio §3 | DECISIONS.md |

## GATE HUMANO — decisões pedidas ao owner

1. **Aprovar buckets?** Núcleo N1-N6 na ordem proposta (N1/N2 são os P0 que o
   backlog já reconhece — o artigo só lhes dá o princípio e o fix certo)?
2. **Registrar E1-E3** no experiment registry (`experiment add`)?
3. **EXP-1 fase 2** (truncamento preservador de cauda, hoje owner-gated) ganha luz
   verde? E2 depende dele em parte.
4. **Wave de crítica** (research-critique, ~60k tokens) sobre este portfólio antes
   de promover, ou promover direto (o artigo já embute crítica externa)?
5. **Visão de negócio §3** (M-scale como instrumento para targets) entra em
   DECISIONS.md como direção?
