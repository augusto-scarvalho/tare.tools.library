# Backlog de cobertura TOTAL do artigo de referência (manuscrito v1.6)

Varredura exaustiva de `docs/research/sources/adaptive-project-oriented-multi-agent-harness-architectures.md`
(3.218 linhas, §1-§15 + apêndices A-I) → todo item acionável do artigo com o estado
REAL no repo. Pedido do owner 2026-07-18: "destrinchar esse artigo inteiro em um
backlog enorme — o que já fizemos, o que não fizemos, o que vai pra research".

**Método:** 6 extratores Sonnet (fatias disjuntas do manuscrito, extração cega ao
repo) + consolidação do overseer Fable cruzando: rodada de adoção
(`harness-reference-architecture-adoption.md`, C1-C16/N/S/E/A), DECISIONS
D008-D011, experiment registry EXP-1..19, records de milestones, LOOP QUEUEs 1-6.
A rodada de adoção foi a leitura SELETIVA (o que fecha lacuna crítica); esta é a
COBERTURA (nada do artigo fica sem linha). Supersede a seletiva onde conflitar.

**Legenda de status:**

| status | significado |
|---|---|
| ✅ feito | mecanismo entregue com evidência (commit/spec/check) |
| 🟡 parcial | slice entregue; o que falta está nomeado |
| ⬜ aberto | buildável hoje, sem research; candidato a LOOP QUEUE |
| 🔬 research | precisa de rodada de research/experimento antes de construir |
| 📏 regra | disciplina adotada como lei viva (playbook/spec/gate), não é artefato |
| 🚫 contra-sinal | o artigo manda NÃO construir; registrado como guarda |
| ⛔ rejeitado | rejeitado por contra-evidência nossa (decisão registrada) |
| 🅿️ parked | estacionado com gatilho de revisita registrado |
| — n/a | não se aplica ao nosso envelope (single-tenant, local, 2 vendors) |

## §3 — Fundações conceituais

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| §3.1 | Ownership: 1 dono por task | ✅ feito | SPEC-149 ownership epoch (75ccda1) + pid-lock dispatch + gate-hold |
| §3.1 | Handoff vs agent-as-tool explícito | 📏 regra | contrato subagent + WORKER_RESULT; transferências via briefs versionados |
| §3.1 | Taxonomia de papéis | ✅ feito | 9 perfis `.claude/agents/` c/ teto S2 + espelhos codex (L17 413965a) |
| §3.2 | Metamodelo H=⟨I,C,P,R,W,X,S,M,O,E⟩ | 📏 regra | mapeia 1:1 na arquitetura `.harness/` (descritivo; sem artefato novo) |
| §3.3 | 4 graus de dinamismo de workflow | 🟡 parcial | static+selected ✅ (profiles/composer); generated/runtime-edited 🅿️ (SF-4: só com evidência de necessidade) |
| §3.4 | MAPE-K / loops interno-externo separados | ✅ feito | SPEC-109 anti-Hive invariant (C9 alinhado na rodada) |
| §3.5 | Envelope operacional versionado | 🟡 parcial | route-tuple C13 (L9 8732dbb) + risk tiers; falta declarar o envelope como doc versionado único → ⬜ candidato barato |
| §3.5 | Regra do estado indeterminado → deny | ✅ feito | N1 receipts (CE.1): sem receipt válido ≠ success; escalation em unknown |
| §3.5 | Perfil de previsibilidade Π | 🔬 research | métrica composta; pré-requisito: noise floor (L13 ✅) + trace completeness (L4 ✅); rodada p/ definir os 5 componentes no nosso corpus |
| §3.5 | Construtos-métricas (12: autonomy, governance, route churn, context footprint, delegation economy, contention, trace completeness…) | 🟡→**DESENHADO R4** | medidos: context footprint (CE.2), delegation economy (OB.2), trace completeness (L4), regret (EXP-17 probe); R4 pré-registrou fórmulas measure-only p/ route churn/CTS/Π-lite/recovery (→ C18/C19/C20 ⬜) e nomeou o que falta p/ regret/ECE/A_ctx (função U + predictedP — decisão de owner). Ver `construct-metrics.md` |
| §3.5 | Risk tiers R0-R3 | ✅ feito | L1 (fba2fe2) + riskTier no dispatch emit (L4); R3 pinado como unreachable na nossa escala |
| §3.5 | Project Context Profile (YAML por run) | ⬜ aberto | temos project.json + model-cards; falta o profile por-target no formato do artigo — barato via SPEC-110 targets |
| §3.5 | Predicado de compatibilidade de transferência | 🅿️ parked | gatilho: 2º target real em produção (hoje single-project) |
| §3.5 | Tupla de rota r (9 campos) | ✅ feito | C13/L9: pin da tupla nos records de delegação |
| §3.5 | Effort labels não comparáveis entre vendors | 📏 regra | model-cards por vendor; L17 NÃO mapeia model claude→codex (unportable note) |
| §3.5 | Resource manifest por nó paralelo | 🟡 parcial | footprints HARD nos briefs + write choreography; falta manifest TIPADO por worker no workflow.json → ⬜ |
| §3.5 | Conservadorismo do manifest (só expande) | 📏 regra | review ritual: mudança fora do footprint = revert |

## §4 — Síntese crítica do estado da arte

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| §4.1 | Harness pinado como tratamento experimental | 📏 regra | D008 + EXPERIMENT_METHODOLOGY (blocos de ruído, snapshot pinado) |
| §4.1 | Contexto ≠ enforcement (hooks antes de tools) | ✅ feito | C14: gate SPEC-137, protected-files, hooks PreToolUse |
| §4.1 | Effective Constitution Compiler | 🅿️ parked | estacionada na rodada (over-eng no estágio); gatilho: multi-tenant |
| §4.1 | Precedência deny-overrides | 🟡 parcial | protected-files + deny hooks ✅; sem compilador formal de precedência (parked junto acima) |
| §4.1 | Dano de contexto auto-gerado | 🚫 contra-sinal | C6: política de CONTEXT.md mínimo curado é lei; NUNCA gerar por LLM |
| §4.1 | Minimização de contexto c/ expiry de claims | 🟡 parcial | budget policy ✅; lifecycle/valid-until (N6) DIFERIDO c/ gatilho (1ª claim vencida que enganar um run) |
| §4.1 | Compressão orientada a relevância (LongLLMLingua) | ⛔ rejeitado (por ora) | EXP-1 fase 2 head+tail: MEDIDA E REVERTIDA (perdeu mais linhas decisivas); re-teste só com corpus enriquecido (caminho registrado no probe) |
| §4.1 | Context diet | ✅ feito | SPEC-118 v6 tool-schema trim (−2.670 tok/turn medido) |
| §4.1 | Baseline single-agent matched-budget | 🔬 research | EXP-15 ATIVO; medições dedup/convergência feitas; falta o braço matched-budget de verdade |
| §4.1 | Briefs de delegação explícitos | ✅ feito | plan-brief template do playbook overseer (footprint/decisões/verify) |
| §4.1 | Experimento confirmatório 4×2 de contexto | 🔬 research | candidato a rodada futura (grande); pré-req: EXP-16 evidence-loss |
| §4.1 | Ledgers separados: tokens billed vs bytes lógicos | 🟡 parcial | token-audit (billed) + CE.2; sem ledger de bytes lógicos → 🔬 (A_ctx diferido c/ gatilho na rodada) |
| §4.2 | Router aprendido / LLM-router | ⛔ rejeitado | C4 + contra-sinal 1 da rodada; kNN/regra empata — SPEC-144 é regra+floor |
| §4.2 | Ledger de outcome de rota + regret | ✅ feito | N4 + L7 route ledger durável (8732dbb) + EXP-17 probe (corpus acumulando) |
| §4.2 | Estágios do router: filtro determinístico | ✅ feito | deterministic_floor + rule-of-two S6 (só RAISE) |
| §4.2 | Estágios: classificador de task | ✅ feito | SPEC-144 tier-1 router (sonnet, 1 demanda → rota+escalação) |
| §4.2 | Estágios: calibração/abstenção | 🟡 parcial | escalation ledger ✅; sem medida de calibração do router → alimenta EXP-17 |
| §4.2 | Estágios: histerese (anti route-churn) | ⬜ aberto | barato: cooldown/deadband no route-loop; medir churn antes (🔬 métrica route churn acima) |
| §4.2 | Estágios: counterfactual logging | 🟡 parcial | route ledger grava candidatos; falta formato contrafactual (rotas não escolhidas c/ propensity) → ⬜ |
| §4.2 | Roteamento de effort por passo (Ares) | 🅿️ parked | gatilho: pressão de custo em sessões longas; hoje effort é por perfil/role |
| §4.2 | Escada C3VR de fallback gated | 🟡 parcial | failover chains (SPEC-115 r15) + escalation ✅; falta o degrau "abstain/escalate effort ANTES de escalar modelo" explícito → ⬜ |
| §4.2 | Exploração banida em R2/R3 | 📏 regra | RF.1 fase 2 owner-gated; tiers L1 dão o vocabulário |
| §4.2 | Teto de co-falha β_C | ⛔ rejeitado (honesto) | recon 2026-07-18: sem oráculo + workers role-diferenciados → β_C não identificável; probe EXP-15 mede co-detecção (o que dá) |
| §4.3 | Workflow IR tipado + compiler checks | 🟡 parcial | DW.2 IR ✅ + compile: schema/budget/secret/permission ✅ (rules 28-30); ciclos/reachability — n/a (só fork-join/map-reduce); compensation 🅿️ |
| §4.3 | Geração de workflow por busca (AFlow/EvoAgentX) | 🚫 contra-sinal | auto-evolução de topologia sem M1/M2 completos = misevolution (C9/C16) |
| §4.3 | Scheduling de modelo por trajetória (EvoRoute) | 🅿️ parked | gatilho: custo de wave dominado por 1 modelo; hoje routing por role resolve |
| §4.3 | Gate leve de intensidade (LLM-as-Scheduler) | 🅿️ parked | primo do effort-por-passo acima; mesmo gatilho |
| §4.3 | Escalação progressiva de dinamismo (SF-4) | 📏 regra | composer = selected; generated/runtime-edited exigem evidência (D008) |
| §4.4 | Taxonomia de topologias | ✅ feito | map-reduce, fork-join, rooms multi-vendor, fork-join NATIVO codex (EXP-19/D009) |
| §4.4 | Evidence envelope por agente | ✅ feito | WORKER_RESULT schema + oracleEvidence (CQ.2); perda medida no EXP-16 |
| §4.4 | Lease + fencing (epoch monotônico) | ✅ feito | SPEC-149 (L11): chokepoint único workflow_update sync+async |
| §4.4 | Single committer + idempotência + receipt p/ efeitos externos | ✅ feito | N1 receipts + merge choreography (overseer único integra) + SF-5b write policy |
| §4.4 | CRDTs / coordination avoidance formal | — n/a | escala atual não tem replicação concorrente de estado mutável |
| §4.4 | LLM não autoriza commit | 📏 regra | gate SPEC-137 + owner-gates + approval digest C12 |
| §4.4 | Topologia por estágio (discovery fan-out, impl single-owner, review independente, approval determinístico) | ✅ feito | D010 largura paramétrica (L16) + waves de crítica independentes + decide inbox |
| §4.4 | Reconstrução de topologia por rodada (DyTopo) | 🅿️ parked | estacionada na rodada; gatilho: multi-tenant/escala |
| §4.5 | Façade única + workers inspecionáveis (AHHI) | ✅ feito | C11: porteiro + rooms + tag [live rooms] + decide inbox + task cards |
| §4.5 | Compact state account (objetivo/dono/frontier/recovery) | ✅ feito | U2 takeover card L0 (2af7787) + plan HUD |
| §4.5 | Perfil de interação task-scoped | 🟡 parcial | headless governance + postPlanMode prefs; sem perfil dinâmico por task (🅿️ AHHI profiles estacionado) |
| §4.5 | Regras locais evolutivas (Hedwig/ZORO) | 🔬 research | toca N6 lifecycle de claims + memória; rodada de memória já tem doc (memory-context-management.md) — refinar lá |
| §4.5 | Guards de ação + digest de aprovação | ✅ feito | C12 approval-digest binding no decide inbox (TOCTOU fechado) |
| §4.5 | Autorização fina de lifecycle (SAGA) | 🅿️ parked | single-user hoje; gatilho: multi-tenant |
| §4.5 | "Esconder até falhar" é inseguro | 📏 regra | estados de lifecycle visíveis (U1) — "sumiu do chat não é estado" |
| §4.5 | Effective autonomy = min(desejo, política, evidência) | 📏 regra | owner-gates não-renunciáveis; containment > fadiga (S-trail) |

## §5 — Arquitetura de referência proposta

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| §5.1 | 10 planos da arquitetura | 🟡 parcial | mapeamento 1:1: control (project.json+hooks+gates), routing (SPEC-144), workflow compiler (DW.2), runtime (async+SPEC-148), capability (executors+SPEC-113), trajectory (events+records), experimental (SPEC-116+métodos), interaction (panel/rooms), evolution (SPEC-109). GAP do runtime plane **DESENHADO na R2** (harness-own sandbox SB-1/2/3, intake pronto `harness-own-sandbox.intake.md`); constitution compiler 🅿️ |
| §5.2 | DGIOTS (kernel formal de transições) | 🅿️ parked | "workflow IR tipado com prova de soundness" estacionada na rodada; DW.2 IR + gates são a versão lite; gatilho: multi-tenant |
| §5.2 | Ponto determinístico de decisão de política pré-execução | 🟡 parcial | claude: hooks deny honrado ✅; codex: hooks advisory → contenção via sandbox nativo S3 ✅; open models: NADA → harness-own sandbox ⬜ |
| §5.3 inv.1-2 | Deny final + autorização pré-ação | 🟡 parcial | idem acima (matriz de contenção por vendor no round doc) |
| §5.3 inv.3 | Proposer ≠ approver | ✅ feito | worker nunca commita; overseer revisa; owner-gates |
| §5.3 inv.4 | Replay antes de persistir | 🟡 parcial | gate SPEC-137 + probes determinísticos; sem replay formal (junto do DGIOTS 🅿️) |
| §5.3 inv.5 | Mudança de kernel só com humano | ✅ feito | protected-files + hook + OS-lock (SPEC-148) |
| §5.3 inv.6 | Ownership único | ✅ feito | SPEC-149 epoch |
| §5.3 inv.7 | Handoff com contrato de evidência | ✅ feito | WORKER_RESULT + handoff budget (M1) + packet economy |
| §5.3 inv.8 | Budgets duros fora do contexto do LLM | ✅ feito | token budgets enforçados no plan/start (rule 29) |
| §5.3 inv.9 | Gate proporcional ao risco | ✅ feito | R0-R3 (L1) + rule-of-two (S6) + owner-gates |
| §5.3 inv.10 | Memória→política só via pipeline de promoção | 🟡 parcial | D008 porta de experimento ✅; lifecycle de memória (N6) diferido c/ gatilho |
| §5.3 inv.11 | Disciplina de logs sensíveis | ✅ feito | secret_scan/redact nos 2 seams + records name-only |
| §5.3 inv.12 | Classes de replay por evento | ✅ feito | L3 replay-class (exact/approximate/external) |
| §5.3 inv.13-15 | Disciplina experimental (sem auto-promoção, desenho congelado, claim causal) | ✅ feito | D008 + livraria de métodos (L18) + prática viva (EXP-18 pré-registro honrado hoje) |
| §5.3 inv.16-17 | Reducer determinístico + fail-closed em colisão de regra | 🅿️ parked | corpo do DGIOTS; nossa versão: gate determinístico + append-only |
| §5.3 inv.18 | Receipt-gated effect truth | ✅ feito | N1 (CE.1): success só com receipt válido |
| §5.3 inv.19-20 | UI não infla teto; controles = eventos tipados | ✅ feito | GUI-writes-no-state + action allowlist + digest no decide |
| §5.4 | Session coordinator ≠ root of trust | 📏 regra | porteiro/façade; autoridade fica nos gates/owner |
| §5.5 | 12 boundaries de adapter estáveis | 🟡 parcial | capabilities.json + SPEC-113 (agora com agent profiles L17) cobrem hooks/mcp/skills/agents; accounting-semantics disclosure ⬜ barato (campo no executor card) |
| §5.5 | Capability delegation contract | ✅ feito | plan briefs (footprint/tools/verify/budget/schema de retorno) + packets |
| §5.5 | Retorno = evidence delta, nunca transcript | ✅ feito | WORKER_RESULT bounded + OUTPUT_CAP + S4 delegation output cap |
| §5.6 | ECA (constituição compilada assinada) | 🅿️ parked | Effective Constitution Compiler estacionado; nossa versão: precedência de protected-files + hooks + specs |
| §5.7 | Máquina de ownership com lease + duas fases de transferência | 🟡 parcial | epoch+recovery ✅; transferência 2-fases explícita não existe (não houve demanda; gatilho: 1º incidente de transferência) |
| §5.7 | Reclamação só pelo runtime | ✅ feito | `_recover_stale_holds` recusa pid VIVO (N3/F2) |
| §5.7 | Tabela de concorrência por semântica de recurso | ✅ feito | SF-5b: worktrees isolados + merge condicional + single committer + write choreography |
| §5.7 | Lifecycle de efeito + outbox + idempotency keys | 🟡 parcial | receipts N1 + records ✅; outbox/idempotency keys formais — n/a na escala (efeitos externos raros e single-committer) |
| §5.7 | Pontos de crash + reconciliação (6 casos) | 🟡 parcial | gate-hold auto-recovery + scenario forensics + breaker; unknown-state effects: escalation ✅ |
| §5.7 | Métricas de recovery (duplicate-effect, orphaned work, time-to-resume…) | 🔬 research | rodada de métricas de construto (junto §3.5) |
| §5.8 | Modos de interação (Assist→Orchestrator) | 🟡 parcial | rooms+panel+composer cobrem Guided/Delegated/Orchestrator de facto; perfis dinâmicos por task 🅿️ (AHHI profiles) |
| §5.8 | Progressive disclosure L0-L3 | ✅ feito | L0 takeover card (U2) / L1 plan HUD / L2 task cards+queue / L3 evidence drill-in (UX-GA.3) |
| §5.8 | Attention inbox tipado + batching | ✅ feito | decide inbox + escalations por blast radius (M5.3); batching é o default do painel |
| §5.8 | Máquina de estados de aprovação + consumo single-use + invalidação | ✅ feito | C12 digest + L2 SLO/expiry + `apply_decision` recusa mismatch |
| §5.8 | Perfil durável interaction_profile | 🅿️ parked | AHHI profiles dinâmicos estacionados (gatilho: multi-tenant) |
| §5.9 | Tabela de planos = contrato mínimo + testes por plano | 🔬 research | **rodada proposta nº 1: self-assessment de conformidade** — mapear nossos gates/cenários aos testes por plano (§5.9 + App F) e publicar matriz de gaps |

## §6 — Autocorreção, memória de projeto, autoevolução governada

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| §6.1 | Taxonomia de falha (11 classes) + router diagnóstico por sintomas | 🟡 parcial | SPEC-126 failure-patterns (clustering) cobre parte; router diagnóstico consome sintomas nos recovery paths do async; taxonomia completa → ⬜ alinhar SPEC-126 às 11 classes |
| §6.1 | Utilidade de recovery + bloqueio de repetição sem evidência nova | 🟡 parcial | breaker + maxRounds + `--force-round` exige diagnóstico escrito 📏; utilidade formal 🔬 |
| §6.1 | Modos de correção (self-critique ≠ evidência; tool feedback = evidência) | 📏 regra | C8: review/oracle/gate; self-critique nunca é evidência (ritual) |
| §6.2 | 7 camadas de memória com regras de confiança | 🟡 parcial | mapeadas de facto (runtime/checkpoint/workflow.json/CONTEXT/records/EXPs/specs/git); regras de confiança POR camada não declaradas → ⬜ doc barato |
| §6.2 | ContextLedger (objeto por fonte/versão/hash/validade) | 🅿️ parked | A_ctx diferido c/ gatilho (rodada 2ª leva); CE.2 mede o proxy |
| §6.2 | Métricas de contexto (F_logical, A_ctx, D_ctx, precision/recall, evidence loss) | 🔬 research | EXP-16 (evidence loss) ATIVO; demais entram na rodada de métricas |
| §6.2 | Lifecycle de memória (candidate→validated→active→challenged→expired) | 🔬→**DESENHADO R2/R3** | N6 DESBLOQUEADO em desenho: trigger scope-matched ancorado em git HEAD SHA ∩ diff (resolve o "teatro mtime" E o over-expiry) + provenance firewall + shadow ledger measure-only. Enforcement segue owner-gated (gatilho N6). Portfólio GM-1..6 em `memory-context-management.md` §R3 |
| §6.2 | Poisoning: memória nunca vira política | ✅ feito | untrusted-derived marks + D008 porta + anti-Hive |
| §6.2 | Eval adversarial de memória (4 condições) | 🔬→**DESENHADO R3** | GM-5 shadow-challenge ledger mede error-following/stale-use/negative-transfer/recovery; graduação por métrica+threshold owner-gated (measure-before-enforce à la EXP-18) |
| §6.2 | 7 camadas de memória c/ trust rules | 🟡→**DESENHADO R3** | GM-3 provenance firewall (active_memory.authority < signed_policy) fecha a regra de confiança que faltava; poisoning coberto |
| §6.3 | ProjectRoutingProfile / bandit constrained | ⛔ rejeitado (por ora) | C4 + RF.1 fase 2 owner-gated; pré-req: EXP-17 regret acumular corpus |
| §6.3 | Shadow-mode p/ priors + drift → shadow-only | 📏 regra | D008; C3VR drift rule citada no round doc (correção A pendente da seção codex) |
| §6.4 | Escada de evolução níveis 0-5 + registry de candidatos | ✅ feito | SPEC-109 (nível 1 fechado-reversível) + experiment registry + intake + DECISIONS; kernel nível 5 = protected+owner |
| §6.4 | Pipeline de promoção c/ monitoramento atrasado | ✅ feito | portas SPEC-116 + reviewBy + doctor `experiment-overdue` (check 6, WARN em stale_active) — o monitoramento atrasado lite JÁ existe |
| §6.4 | AHE: predição antes da observação | ✅ feito | pré-registro é prática viva (EXP-18 medição 2 desta sessão) |
| §6.5 | EDC completo (design selector, sealed partitions, racing/BO) | 🅿️ parked | estacionado na rodada; nossa versão EDC-lite: livraria de métodos (L18) + registry + noise floor (L13) + Taguchi (hoje) |
| §6.5 | Separação search vs inference; alias publicado | 📏 regra | livraria de métodos (Taguchi card cita a crítica estatística) |
| §6.6 | Constantes default (α=.05, power .80, δ_Q/δ_C/δ_L/δ_V, ECE≤.05) | ⬜ aberto | **barato e valioso: adotar a tabela de constantes em EXPERIMENT_METHODOLOGY.md** como defaults de promoção |
| §6.6 | 8 requisitos de promoção + rollout staged + rollback triggers | 🟡 parcial | D008 door + gate + reversalPlan obrigatório ✅; sequential testing/alpha-spending 🔬 (só se volume de EXPs crescer) |
| §6.6 | Proibição de auto-modificação de evidência/rollback | ✅ feito | anti-Hive + protected files + proposer≠approver |

## §7 — Governança, métodos formais, segurança

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| §7.1 r1 | Deny em diretórios protegidos | ✅ feito | protected-files hook + OS-lock + parser apply_patch (building block) |
| §7.1 r2 | Fluxo sensível gated por aprovação (secret→egress) | 🟡 parcial | SEC.1 pre-egress + scrub nos seams ✅; egress geral declare-only (teto honesto, rule 27) → depende do harness-own sandbox ⬜ |
| §7.1 r3 | Limites de COMBINAÇÃO de tools | ✅ feito | rule-of-two S6 (2-de-3 untrusted/sensitive/external → escalate) |
| §7.1 r4 | Delegação não escala privilégio | ✅ feito | env allowlist E3/S1 + sandbox tiers S3 + spawn economy |
| §7.1 r5 | Validador independente antes de merge | ✅ feito | review ritual + gate SPEC-137 + oracle mutate |
| §7.1 r6 | Limites cumulativos de custo/agentes | ✅ feito | token budgets + maxWorkers + delegation ledger |
| §7.1 r7 | Proposer não aprova a própria proposta | ✅ feito | idem inv.3 |
| §7.1 o1-o5 | Políticas de CAMINHO (obrigações temporais) | 🟡 parcial | o1 plan-gate digest ✅; o3 ✅; o4 C12 ✅; o5 reversalPlan ✅; o2 (secret_read → nunca egress até declassificar) 🟡 — taint tracking não existe; entra no design do harness-own sandbox |
| §7.2 | Métodos formais (Petri/TL/type systems/refinement) | 🅿️ parked | junto do DGIOTS; nossa camada: property-based via cenários + mutation |
| §7.2 p1-p8 | 8 propriedades verificáveis | 🟡 parcial | safety/non-bypass/separation/termination cobertas por gates+hooks+budgets; liveness = watchdog/timeout; provas formais 🅿️ |
| §7.2 | Mutation testing de política | 🟡 parcial | oracle mutate ✅ (código); mutação de POLÍTICA (negar guards, spoof epoch) → ⬜ estender red-team fixture |
| §7.2 | Estimativa estatística nunca sobrepõe deny | 📏 regra | OB.3 anomaly card é advisory-only por design |
| §7.3 | Hierarquia de trust zones (10 zonas); repo content é UNTRUSTED | ✅ feito | trustTier (DW.1) + untrusted-derived marks + seed provenance + prompt-injection posture nos packets |
| §7.4 s1-s10 | Defense stack 10 camadas | 🟡 parcial | s1✅ s2🟡(scrub+marks) s3✅(S1/S2/S3) s4✅claude/🟡codex s5🟡→**DESENHADO R2** (harness-own sandbox SB-1/2/3 intake pronto; egress kernel atrás de gatilho admin) s6✅gates s7🟡(OB.3) s8✅ s9✅ s10🟡(red-team fixture; contínuo 🔬) |
| §7.4 | Rule of Two | ✅ feito | S6 no floor do porteiro |
| §7.4 | CaMeL (separar controle confiável de dado não-confiável) | 🟡 parcial | citado na trilha S; realização plena = harness-own sandbox |
| §7.4 | Avaliação adversarial task-bearing (AgentDojo etc.) | 🔬 research | rodada de red-team contínuo; hoje: red-team fixture pontual |
| §7.5 | Threat model 7 adversários + cobertura 4-partes (prevenção/detecção/resposta/dono) | 🟡 parcial | security-directive-map + fixtures cobrem parte; **⬜ barato: residual risk register** (schema §14.7-2) por ameaça |
| §7.5 | SLSA / in-toto (supply chain) | — n/a | single-dev local; gatilho: distribuição do harness como produto |
| §7.6 | Classificações de dados + non-exfiltration flow invariant | 🟡 parcial | secret scrub + keys vault + redaction ✅; classificação formal por item 🅿️ (multi-tenant) |
| §7.7 | Aprovação = compreensão + chance real de rejeitar; anti-fadiga | ✅ feito | decide inbox tipado c/ digest + expiry/SLO + containment-over-fatigue (S-trail) |
| §7.7 | Formas inválidas de aprovação (blanket/retroativa/self/sem expiry) | ✅ feito | C12+L2 fecham as 4 |
| §7.7 | Métricas do serviço de aprovação | ⬜ aberto | barato: stats do decide inbox (volume/latência/override) no metrics |
| §7.7 | Estudos humanos de oversight | — n/a | pesquisa acadêmica; fora do envelope |

## §8 — Proveniência, observabilidade, interoperabilidade

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| §8.1 | ATP (evento tipado, DAG causal, append-only) | 🟡 parcial | events.jsonl + N2 classe append-only + quarentena ✅; DAG causal explícito (parent ids) ⬜; assinatura/hash-chain 🅿️ (estacionado) |
| §8.1 ir1 | Eventos imutáveis, correção por supersessão | ✅ feito | N2 + G3a record supersession |
| §8.1 ir6 | Quarentena de evento órfão | ✅ feito | N2 (CE.8): SECURITY_ALERT/FAILURE sobrevivem a wipe |
| §8.1 ir8 | Trace completeness POR risk tier | ✅ feito | L4 (feb73f3): doctor check 9 + riskTier no emit |
| §8.1 ir9 | Reconciliação de usage por chamada de modelo | 🟡 parcial | delegation ledger + token-audit; reconciliação por chamada ⬜ (campo no executor result) |
| §8.1 ir2-5,10-14 | Demais integrity rules | 🟡 parcial | refs de merge/failover/decisão existem nos records; cluster completo entra no self-assessment (rodada nº 1) |
| §8.2 | Replay classes declaradas | ✅ feito | L3 |
| §8.2 | Replay contrafactual de UMA variável | 🔬 research | candidato a EXP (trocar router/modelo/memória num WF congelado); pré-req: corpus de WFs congelados (já temos 5) |
| §8.3 | MCP como boundary; A2A | 🟡 / n/a | MCP declarado em capabilities.json ✅; A2A sem caso de uso |
| §8.3 | Matriz de capacidade por adapter + conformance suite | 🟡 parcial | capabilities.json + correção pendente (A) da seção codex; suite de conformance → junto do self-assessment |
| §8.4 | Estados de suporte native/emulated/degraded/unsupported | ⬜ aberto | barato e útil: vocabulário nos cards de capabilities.json (a nota codex SubagentStop é exatamente isso) |
| §8.4 c1-c14 | 14 testes de conformance de adapter | 🔬 research | subconjunto aplicável entra no self-assessment; esh (executor-spawn-hygiene) já cobre c2 parcial |
| §8.4 | Avaliação 3-lanes cross-vendor (sem pooling) | 🔬→**DESENHADO R5 = EXP-20 proposed** | pré-registro completo (`exp20-three-lane-design.md`): 3 lanes sem pooling, split-plot (vendor=whole-plot), matched-budget por tokens observados, gap codex-nativo tratado como EMULATED. Medição OWNER-GATED (porta SPEC-116) |

## §9 — Avaliação científica e programa experimental

O grosso do §9 é o programa de pesquisa DO ARTIGO (benchmarks acadêmicos, estudos
humanos A-L, modelos hierárquicos). Adotamos a DISCIPLINA, não o programa. Linhas
n/a agrupadas honestamente.

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| §9.1 | Tupla de configuração experimental; nenhum benchmark único basta | ✅ feito | C13 route tuple + D008 (harness pinado como tratamento) |
| §9.2 | Baseline matched-budget OBRIGATÓRIO p/ claims multi-agente | 🔬 research | EXP-15 ATIVO — é exatamente o braço que falta medir |
| §9.2 | Famílias de baselines (routing, concorrência, evolução, AHHI, DGIOTS) | 📏 regra | referência p/ quando compararmos; maioria fora do envelope hoje |
| §9.3 | Benchmarks públicos (SWE-bench, OSWorld, WebArena…) | — n/a | não somos lab de benchmark; nossos "frozen tasks" = cenários+fixtures ✅ |
| §9.3 | Task snapshot congelado + exclusão de dados de desenvolvimento | ✅ feito | cenários determinísticos + WFs congelados (corpus EXP-15/18) |
| §9.4 | Classes de fatores (control/noise/hard-to-change/nuisance/prohibited) | 🟡 parcial | livraria de métodos (L18) tem Taguchi/screening; tipagem formal de fatores → ⬜ adotar no EXPERIMENT_METHODOLOGY junto das constantes §6.6 |
| §9.4 | ≥5 repetições / poder simulado; partições discovery/confirmation/promotion | 🟡 parcial | pré-registro ✅ prática; partições e floor de repetições → mesma adoção ⬜ |
| §9.5 | Famílias de métricas (routing/contexto/concorrência/economia/governança) | 🔬 research | temos: regret (EXP-17), evidence loss (EXP-16), noise floor (L13), Δ_m (probe EXP-15), CTS ⬜ barato (delegation ledger já tem custo+outcome); resto → rodada de métricas |
| §9.5 | β_C / co-failure | ⛔ rejeitado (honesto) | sem oráculo + roles diferenciadas (recon 2026-07-18) |
| §9.6 | Modelos hierárquicos / split-plot / confidence sequences | — n/a | volume experimental não justifica; revisitar se EXPs/semana ≥ ~10 |
| §9.7 | Noise floor local + resultados negativos publicados | ✅ feito | L13 + prática viva (EXP-1 fase 2 medida-e-revertida; probes refutados registrados) |
| §9.7 | Pacote de reprodução completo | 🅿️ parked | gatilho: publicação externa/multi-org |
| §9.8 | Hierarquia de oráculos O1-O5; O5 (LLM-judge) nunca é oráculo único | ✅ feito | O1=cenários/gates, O2=checks estáticos, O3/O4=owner; C8 + abandonCriteria do EXP-18 citam auditoria de viés p/ LLM-judge |
| §9.8 | Registro DUPLO: agent_reported vs oracle_observed | ✅ feito | CE.1/N1 é literalmente isso (a lição fundadora) |
| §9.9 | Graus de replay contrafactual; só 1-2 sustentam claim causal | 📏 regra | metodologia; replay contrafactual de 1 variável 🔬 (EXP candidato) |
| §9.10 | TCO + regra lexicográfica (segurança primeiro, nunca trocada) | 🟡 parcial | cost ledger + OB.2 trends ✅; regra lexicográfica → ⬜ declarar na metodologia (1 parágrafo) |
| §9.11-12 | Estudos A-L (simuladores, estudos humanos) | — n/a | programa do artigo; exceções que nos servem: Study G ≈ família EXP-15/16; Study K alimenta o self-assessment (rodada nº 1) |

## §10 — RQs e hipóteses falsificáveis (H1-H46) — as que NOS tocam

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| H1 | Router híbrido (regras+adaptativo) < regret | 🟡 parcial | SPEC-144 é regras+floor; EXP-17 mede o regret; fase adaptativa segue owner-gated (C4) |
| H4 | Ownership único reduz conflito/rework | ✅ feito | 4 incidentes documentados motivaram N3/L11; evidência interna forte |
| H6 | Separação dos 2 loops evita mutação persistente | ✅ feito | SPEC-109 anti-Hive |
| H7 | Enforcement executável > prosa | ✅ feito | C14 + achado codex (hooks advisory ≠ enforcement) REFORÇA: enforcement precisa ser da camada certa por vendor |
| H14 | Contexto mínimo curado ≥ contexto gerado | ✅ feito | C6 adotado como lei |
| H15 | Catálogo pequeno diverso ≥ catálogo grande correlacionado | 🔬 research | model-cards + delegation trends dão o corpus; rodada de catálogo se surgir pressão |
| H16 | Lifecycle governado de memória > append-only | 🔬 research | rodada nº 3 (memória) |
| H17 | Correção com evidência externa > self-critique | 📏 regra | C8; ritual review/oracle/gate |
| H19 | Ledger durável + receipts elimina efeitos duplicados/unknown | ✅ feito | N1 + F1/F2 (dispatch guard, stale holds) |
| H20 | Diferenças < noise floor não replicam | ✅ feito | L13 + regra da metodologia (delta < floor ≠ evidência) |
| H21 | Grading por estado ≠ auto-relato | ✅ feito | CE.1; validation.json vs claims |
| H24-H29 | Família EDC (DOE > OFAT; robustez control×noise; confirmação independente) | 🟡 parcial | livraria de métodos + Taguchi EXP-18 rodada hoje = primeira instância viva; EDC completo 🅿️ |
| H30 | Labels de effort não equivalem entre vendors | ✅ feito | adotado (model-cards; L17 unportable note) |
| H31 | Ranking inverte entre lane normalizado e nativo | 🔬→**DESENHADO R5** | EXP-20 registrado (proposed): Kendall tau intra-lane vs Floor B detecta a inversão = interação model×harness. Medição owner-gated |
| H32 | Controlador de effort por passo | 🅿️ parked | gatilho: pressão de custo |
| H35 | Delegação escopada ≥ herança de transcript | ✅ feito | E1 digest (−63%) + E3 env + S4 output cap + M1 handoff budget — todos medidos |
| H36 | Redução de trajetória sem perder evidência | 🔬 research | EXP-1 (fase 2 revertida c/ caminho de re-teste) + EXP-16 |
| H37 | Concorrência por semântica de recurso elimina stale/conflito | ✅ feito | worktrees + merge choreography + epoch; zero stale R2/R3 aceito até hoje |
| H38 | Reparo semântico ADVISORY (validador determinístico comita) | 🟡 parcial | EXP-18 shadow detector É a instância (advisory, nunca funde); medição 2: recall 0.6 < barra 0.8 → segue shadow |
| H39-H46 | Família AHHI/DGIOTS (estudos humanos + formal) | — n/a / 🅿️ | fora do envelope; App I invariantes viram lei onde já batem (ver App I abaixo) |

## §11 — Qualidade arquitetural, trade-offs, maturidade

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| §11.1 | 10 atributos de qualidade | 📏 regra | rubrica p/ o self-assessment (rodada nº 1) |
| ATAM 1-24 | 24 cenários de mudança/estresse | 🔬 research | insumo DIRETO da rodada nº 1: cada cenário vira um teste de mesa contra o repo (vários já passam: worktree pruner, failover, gate-hold recovery, C12 invalidation, quarentena N2…) |
| M0-M7 | Modelo de maturidade cumulativo | ✅ feito | D008 frame interno; D011 versão-produto parkeada; nossa posição ≈ M2-M3 sólido, M5 parcial, M6 embrionário |
| §11.3-c | Escala de evidência 0-3 por capacidade | ⬜ aberto | adotar como coluna do self-assessment (barato, dá rigor ao M-frame) |
| §11.3-g/h | Confiabilidade 2-raters / validação multi-org | — n/a | single-org; gatilho D011 |
| §11.4 | Matriz de cobertura SDKs/runtimes/protocolos vs harness | ✅ feito | visão de negócio da rodada de adoção (categoria "harness engineering") |

## §12-§15 — Discussão, roadmap, ameaças, conclusão

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| §12.2 | 7 anti-padrões de multi-agente (quando NÃO usar) | ✅ feito | D010 + EXP-15 são a versão operacional; playbook Phase 0 exige justificar largura |
| §12.3 | Transferência de ownership + estado durável + envelopes | ✅ feito | briefs/WORKER_RESULT/records — é o desenho vigente |
| §12.4 | Self-regulation ≠ soberania; verifiable improvement > change-rate | 📏 regra | anti-Hive + D008 |
| §12.5 | Repo machine-readable p/ agentes (SDD/BDD/CI/policy-as-code) | ✅ feito | é o produto inteiro (specs+gates+graphify+records) |
| §12.6 | Façade não pode apagar revisão independente / consenso falso | 📏 regra | reduce preserva conflitos (`preserveConflicts`) + sourceWorkerIds = proveniência correlacionada |
| §12.7-8 | P1-P28 (princípios) | ✅ feito (maioria) | 24/28 são lei viva citável (decisões+specs); abertos: P12 diversidade-por-falha (🔬 catálogo), P19 ledger reconciliado (🅿️ A_ctx) |
| §13 | Fases 0-10 + gates de saída do programa | 📏 regra | régua de posição: estamos ≈ fases 0-6 "lite" (protocolo/arquitetura/routing/IR/correção/aprendizado local) com gates informais; fases 7-10 = programa acadêmico |
| §14.1-6 | Ameaças a validade + mitigation bundles | ✅ feito (subset) | noise floor (L13), D-level labeling (📏), pré-registro, corpus congelado; **⬜ residual risk register** (§14.7-2) é o gap barato |
| §14.7 | Claim de assurance limitado + registro de risco residual | ⬜ aberto | schema pronto no artigo; 1 arquivo em .harness/state + doctor advisory |
| §15 | Princípio central (probabilístico onde julga, determinístico onde limita) | ✅ feito | é a tese da nossa arquitetura (gate+hooks+owner-gates) — validação externa |

## Apêndices A-I

| ref | item | status | evidência / próximo passo |
|---|---|---|---|
| App A | Formulário de extração p/ living review | — n/a | não somos o living review; nosso equivalente: research playbook + records |
| App B | Evidence envelope completo (claims/artifacts/validations/approvals/effects/costs + hash) | 🟡 parcial | WORKER_RESULT cobre claims/artifacts/validations; **⬜ barato: blocos costs (tokens por worker já existem no token-audit — juntar) e approvals refs**; hash/assinatura 🅿️ |
| App C | Grafo de evidência tipado | 🅿️ parked | records ledger + doc-find conceitos são a versão lite; gatilho: escala de queries |
| App D | Compilação de constituição (deny-overrides) | 🅿️ parked | junto do ECA §5.6; deny-overrides já é real em protected-files/hooks |
| App E | Contrato de pré-registro + partições de evidência | 🟡 parcial | registry cobre hipótese/baseline/critérios/reversal ✅; **⬜ adotar: tipagem de fatores + partições discovery/confirmation (lite)** |
| App F | 16 suites de conformance (uma por plano) | 🔬 research | ESPINHA DA RODADA Nº 1: mapear nossos gates/cenários/fixtures às 16 suites; F-17/18 (suite falha → capa a dimensão de maturidade) adotar como regra do self-assessment |
| App G | Critérios de fechamento da tese bounded-control | 📏 regra | referência; G-5 (terceiro reconstrói decisões do pacote) é norte p/ records |
| App H | Gatilhos de seleção EDC + graus de evidência 1-4 | ⬜ aberto | **adotar vocabulário "grau 1-4" (exploratório/atributivo/confirmatório/qualificado-a-promoção) no EXPERIMENT_METHODOLOGY + campo no registry** — barato, muda conversa de promoção |
| App I | Perfil normativo AHHI-DGIOTS (schemas de evento/regra/aprovação/worker) | 🅿️ parked | kernel formal; MAS I.8-1..11 (invariantes finais) já são lei nossa em 8 de 11 casos (documentar equivalências no self-assessment) |

---

## Rollup (contagem por status, itens consolidados)

| status | ~itens | leitura |
|---|---|---|
| ✅ feito | ~78 | o núcleo do artigo (ownership, receipts, enforcement, envelopes, tiers, aprovação, noise floor, anti-Hive, contexto mínimo) JÁ É o repo |
| 📏 regra | ~24 | disciplina adotada como lei (decisões/playbooks/ritual) |
| 🟡 parcial | ~38 | slice entregue com o resto nomeado |
| ⬜ aberto | ~16 | buildáveis baratos — candidatos diretos a LOOP QUEUE 7 |
| 🔬 research | ~18 | precisam de rodada/experimento antes de construir |
| 🅿️ parked | ~17 | gatilho registrado (maioria: multi-tenant/escala/formal kernel) |
| ⛔ rejeitado | 4 | router aprendido; compressão head+tail; β_C; bandit §6.3 (por ora, evidência própria) |
| 🚫 contra-sinal | 3 | contexto gerado; workflow auto-gerado; append-only memory |
| — n/a | ~12 | fora do envelope (benchmarks acadêmicos, estudos humanos, multi-org) |

## Rodadas de research propostas (o bucket "vamos rodar research em cima")

Ordem por (valor × desbloqueio), cada uma com pergunta e produto definidos:

1. **Self-assessment de conformidade** (§5.9 + App F 16 suites + ATAM 1-24 + escala 0-3 do §11.3-c). Pergunta: que fração do contrato mínimo do artigo nossos gates/cenários JÁ provam, e onde está o gap real? Produto: matriz suite×evidência com nota 0-3, gaps viram intake. Interna, zero web, ~2 workers focados (D010: focada). É o mapa que torna todas as outras rodadas endereçáveis.
2. **Harness-own sandbox — design round** (§5.9 runtime plane, §7.4 s5, CaMeL, o REQUISITO da investigação codex 2026-07-18). Pergunta: qual contenção fs/proc/net vendor-agnóstica no spawn cobre open models + reforça claude/codex? Produto: SPEC via porta NEW + o parser apply_patch como building block. **P0 — já era o próximo antes deste backlog.**
3. **Memória governada** (§6.2 completo + H16 + eval adversarial 4-condições). Refina `docs/research/memory-context-management.md` com lifecycle candidate→…→expired, trust rules por camada e o eval adversarial. Gatilho N6 continua valendo para a parte enforcement.
4. **Métricas de construto** (§3.5 + §9.5): route churn, CTS, Π-lite, autonomy/governance observáveis. Produto: 2-3 probes measure-only + rodada de definição pré-registrada. CTS sai quase de graça do delegation ledger.
5. **3-lanes cross-vendor / EXP-20** (§8.4, §9.4-t, H31): fork-join harness vs fork-join NATIVO codex vs híbrido governado, no MESMO task class com budget igualado. D009 deu a direção; EXP-19 deu o maquinário; pré-registrar antes de integrar aposta D no core.

## Candidatos a LOOP QUEUE 7 (⬜ baratos, aguardando sua ordem)

| # | item | ref | tamanho |
|---|---|---|---|
| C1 | Constantes de decisão (α, power, δ_Q/δ_C/δ_L/δ_V, ECE) + regra lexicográfica + graus de evidência 1-4 + tipagem de fatores → EXPERIMENT_METHODOLOGY.md + campo `evidenceGrade` no registry | §6.6, §9.10-g, App E/H | S |
| C2 | Residual risk register (.harness/state, schema §14.7-2) + doctor advisory; casa com security-directive-map | §7.5, §14.7 | S |
| C3 | Estados native/emulated/degraded/unsupported por capability no capabilities.json (formaliza a correção pendente (A) da nota codex SubagentStop) | §8.4 | S |
| C4 | WORKER_RESULT: bloco costs (ligar token-audit por worker) + refs de approval | App B | S-M |
| C5 | Métricas do decide inbox (volume/latência/override/expiry) no `metrics` | §7.7 | S |
| C6 | CTS (cost-to-success) no `metrics` a partir do delegation ledger (custo+outcome já gravados) | §9.5-b | S |
| C7 | Trust rules por camada de memória (doc curto mapeando as 7 camadas ao que já existe) | §6.2 | S |
| ~~C8~~ ✅ | ~~Doctor advisory: EXP com reviewBy vencido~~ JÁ SHIPADO — `repo_health.checks` check (6) `experiment-overdue` (WARN em `stale_active`); item fantasma removido da fila LQ7 no recon 2026-07-18 | §6.4 | — |
| C9 | Histerese/cooldown no route-loop — **desbloqueado por R4**: a fórmula de route churn está pré-registrada (`construct-metrics.md`), buildável já como probe; C9 controle só DEPOIS de medir o churn | §4.2 | M |
| C18 | probe measure-only de route churn (fórmula R4 + Floor L13); pré-req de C9 | §3.5 | S |
| C19 | probe measure-only de Π-lite (perfil de previsibilidade §3.5; casa com regra lexicográfica do C1) | §3.5 | S |
| C20 | probes measure-only de recovery (orphaned work, time-to-resume, provenance continuity, recovery-point error) do records ledger | §5.7 | S-M |
| C10 | Resource manifest tipado por worker no workflow.json (footprint declarado hoje só no brief) | §3.5 | M |
| C11 | Envelope operacional como doc versionado único (task classes, vendors, budgets, tiers — hoje espalhado) | §3.5 | S |
| C12b | Reconciliação de usage por chamada (campo no executor result vs delegation ledger) | §8.1 ir9 | M |
| C13b | Alinhar SPEC-126 failure-patterns às 11 classes do §6.1 | §6.1 | M |
| C14b | Red-team fixture: mutação de POLÍTICA (spoof epoch, guard negado, digest trocado) | §7.2 | M |
| C15b | Parent ids causais nos eventos (DAG explícito, campo aditivo) | §8.1 | M |
| C16b | Accounting-semantics disclosure no executor card (native/emulated/unknown) | §5.5 | S |

| C17 | ATAM mesa-test checklist: os 15 cenários "desconhecido" do R1 viram testes de mesa documentados (prioridade: A13 crash-antes-de-receipt, A14 revogação de memória envenenada, A18 oracle-gaming) | R1 self-assessment | S |

**Não iniciar sem ordem do owner:** tudo acima de S/M aqui é pós-rodadas; o P0
continua sendo a rodada nº 2 (harness-own sandbox). Este doc supersede a lista
"Próxima leva de prospecção" do round doc de adoção (que cobria só 4 itens).

## Incremento R1 — self-assessment executado (2026-07-18, D012)

Rodada 1 CONCLUÍDA via NVIDIA (round doc: `docs/research/conformance-selfassessment.md`;
WFs `...215453` + follow-up B3 `...220210`). Resultado em uma linha: **nota 2
(implementado+testado internamente) em ~70% do contrato mínimo; nota 3 em NADA;
os 5 buracos nomeados são os já-parkeados (ECA, hash-chain, privacy formal,
interop conformance) + 1 correção a nosso favor (F15 promotion = 2).**

- Rollup App F: 11 suites nota 2; 5 suites nota 1 (F1, F12, F13, F15→2 corrigida, F16).
- Planos §5.9/I.8: maioria 2; gaps em P5 (accounting por chamada → C12b) e I10 (formal 🅿️).
- ATAM: 9 provável-passa, 15 desconhecido (→ C17 novo), 0 falha confirmada.
- Regra de capa F-17/18 adotada: M-interna confirmada M2-M3; subir exige os
  slices nomeados de F1/F12, não média.
- Novo 🔬: crash-injection na fronteira do adapter (A13/§5.7) — candidato a
  fixture; entra na rodada de métricas/recovery (R4) como desenho.

---

# ORDEM DE EXECUÇÃO DO BACKLOG INTEIRO (arquiteto, 2026-07-18)

Owner: "derive mais pesquisas e insira no backlog; depois pega o backlog INTEIRO
(não só o das pesquisas) e ordena ele todinho pra gente começar a trabalhar, na
ordem mais eficiente — sem criar features sem dependência pronta, sem priorizar
o que seria muito mais rápido se tivéssemos feito as tasks certas primeiro."

## Parte 1 — itens NOVOS derivados das rodadas R1-R5 (inseridos no backlog)

### Enablers (pequenos, destravam famílias inteiras — o coração da eficiência)
| id | item | destrava | fonte | tam |
|---|---|---|---|---|
| **E-ROUTESCORES** | persistir os `scores` que o router JÁ emite (`route_dispatcher.py:131`) na row do route ledger + `predictedP` = score normalizado | ECE (calibração) + route regret + RF.1 fase 2 | R4 (needs-new-state era MENOR que campo novo) | S |
| **E-SCOPETAG** | campo `scopeTag` (paths/deps que a memória referencia) por item de memória | TODO o track de memória governada (GM-1/2/5, N6) + scope-match | R3 (o "writer changes" do N6, agora dimensionado) | S |
| **E-UNIQTOK** | contador de tokens por item ÚNICO no `context_digest` (hoje só hasheia por arquivo) | A_ctx amplification + ctx recall + ContextLedger + amplificação real do CE.2 | R4 (denominador que não existe) | S |
| **E-3LANE** | instrumento de teste 3-lanes: task set congelado + oráculo stdlib (parse/compile) + tabela de gap | EXP-20 medição + EXP-15 matched-budget (mesmo instrumento) | R5 | M |
| **E-EFFECTID** | effect-id/idempotency-key nos records de efeito externo | duplicate-effect + compensation metrics (§5.7) + effect lifecycle | R4 | M |

### Tasks novas (fecham gaps nota-1 do R1)
| id | item | fecha | tam |
|---|---|---|---|
| **T-HASHCHAIN** | hash-chain + assinatura nos eventos críticos (§8.1 ir4) | App F F12 (trajectory) nota 1→2 | M |
| **T-ADAPTERCONF** | suite de conformance por adapter (subconjunto §8.4 c1-c14) + C16b accounting-semantics | App F F16 (interop) nota 1→2 | M |
| **T-CAUSALPARENT** | = C15b: parent ids causais nos eventos (DAG explícito) | §8.1 DAG + habilita replay contrafactual | M |

### Experimentos novos registrados
| id | status | o que | fonte |
|---|---|---|---|
| **EXP-21** | proposed | crash-injection na fronteira do adapter (recovery sem órfãos/duplicatas, ATAM A13/A6) | R1/R4 |
| **EXP-20** | proposed (R5) | 3-lane harness vs codex nativo | R5 |

### Rodadas de RESEARCH novas derivadas (o owner pediu pesquisas, não só tasks)
| id | pergunta | destrava | gatilho |
|---|---|---|---|
| **RD-U** | qual a função de utilidade `U(rota, outcome, custo)` do harness? | route regret + ECE viram buildáveis (hoje needs-new-state por falta de U) | antes de qualquer métrica de regret/calibração |
| **RD-CRASH** | como injetar crash deterministicamente na fronteira do adapter no Windows? | EXP-21 + fixture de recovery + duplicate-effect | antes de EXP-21 |
| **RD-TAINT** | taint de dado-não-confiável / CaMeL (§7.1 o2: secret_read nunca egressa) | fecha o gap o2 que nem o sandbox pega | depois do Q7-1 |
| **RD-ECA** | ECA-lite: vale precedência compilada na nossa escala, ou fica parked? | App F F1 (constitution, nossa MENOR nota) | trigger: 2ª disputa de precedência real |

## Parte 2 — ORDEM DO BACKLOG INTEIRO (fases por dependência)

Regra: enabler barato ANTES do que destrava; near-bug real ANTES de feature nova;
medir ANTES de controlar; owner-gate/pesquisa atrás do seu pré-requisito. Cada
fase é um lote; dentro da fase a ordem é livre.

### FASE 0 — near-bugs reais + enablers baratos (dias, destrava tudo)
**Correção do overseer (loop 2026-07-18): os 3 near-bugs JÁ ESTAVAM SHIPADOS** —
linhas herdadas dos roadmaps de jul/12, verificadas como done:
1. ~~`path-hygiene-scrub-and-gate`~~ ✅ regex `LOCAL_ABSOLUTE_PATH_PATTERNS` já cobre doubled-backslash/`/c/`/`/mnt/c/`; gate `release-hygiene:local-absolute-paths` + `ph_path_hygiene.py`; zero leaks vivos; `harness.py:308` usa basename
2. ~~`win-hidden-spawn-helper`~~ ✅ `processes.py` tem o helper CREATE_NO_WINDOW; supervisor async usa `process_group_kwargs` (async_runtime:402,789), NÃO DETACHED_PROCESS
3. ~~`target-gate-env-filter`~~ ✅ `gate_generic.py:187` aplica `filter_spawn_env` deny-by-default + escape hatch `workerEnvFilter`
Trabalho REAL da Fase 0 (enablers, disjuntos → paralelizáveis):
4. **C1** constantes + `evidenceGrade` — governança fundacional de TODO experimento
5. **E-ROUTESCORES** — enabler (scores já existem; persistir)
6. **C3** capability support-states — enabler (EXP-20 lane + manifest do sandbox + F16)

### FASE 1 — o P0 de segurança
7. **Q7-1 harness-own sandbox SB-1/2/3** (SPEC-151) — ESTENDE o `sandbox_spawn` que já existe (SPEC-148: `risk_tier`, `fs_confine_nt` via icacls, Job Object caps) → cobrir o worker HTTP open-model + manifest + honestidade de egress. `/verify` em máquina Windows real
8. **C2** residual risk register — consome a saída do Q7-1

### FASE 2 — probes measure-only (medir antes de controlar)
9. **C18** route churn (pré-req de C9) · 10. **C6** CTS · 11. **C19 Π-lite + C20 recovery** · 12. **C5** decide-inbox metrics · 13. **E-UNIQTOK** → probe A_ctx

### FASE 3 — memória governada (RE-ESCOPADA pelo overseer 2026-07-18)
**Correção de dependência:** NÃO existe um store de itens de memória governada
hoje (`ui_memory` é read-only snapshot; auto-memory é escrita pelo runtime, não
pelo harness; N6 foi diferido justamente porque o store/campo não existe). Então
E-SCOPETAG NÃO é "campo num store existente" — o 1º artefato da Fase 3 tem que
BOOTSTRAPAR o registro mínimo de item.
14. **GM-5 shadow-challenge ledger (measure-only) — INCLUI o bootstrap do registro
    mínimo de item COM `scopeTag`** (E-SCOPETAG folda aqui): define o record, mede
    quantos itens SERIAM challenged por commit (scope-match contra `git diff
    --name-only`), zero enforcement. É o 1º passo committável da R3.
15. **GM-3 provenance firewall** — aplica quando o retrieval de itens governados
    existir; enforcement owner-gated (gatilho N6).

### FASE 4 — hardening trajetória/adapter + instrumento
17. **T-HASHCHAIN** (F12) · **T-CAUSALPARENT/C15b** · **T-ADAPTERCONF+C16b** (F16) · 18. **E-3LANE** (instrumento de EXP-20 E EXP-15)

### FASE 5 — controles que a medição justificou
19. **C9** histerese — **DIFERIDO com gatilho (overseer 2026-07-19)**: o C18
    probe mediu route churn ~zero (corpus de route ledger transiente/vazio — zeros
    honestos). Construir a histerese agora seria controle SEM a medição que o
    justifica — o anti-padrão measure-before-control que a pesquisa (e o nosso
    D008) condenam. **Gatilho de revisita: primeira medição de churn acima do
    noise floor L13.** O probe (C18) está pronto e mede continuamente. · 20. o que
    a Fase 2 provar que vale (ex.: A_ctx dominante → CE.7) — mesmo gatilho de sinal.

### LOOP QUEUE 7 — FECHADA (2026-07-19): fila buildável ZERADA
Fases 0-4 entregues (14 itens, 13 delegações kept ~1.66M tok). Restam apenas
owner-gated + N-* de design (que dependem de decisão do owner) + C9 diferido por
medição. Ver o summary de fecho no IMPLEMENTATION_BACKLOG.md.

### RESEARCH (rodar quando o pré-requisito chegar)
RD-U ✅ CONCLUÍDA (rodada rd-u-utility-function-round.md, D021: U weighted-linear) → destrava regret/ECE (buildável measure-only). RD-CRASH ✅ CONCLUÍDA (rd-crash-injection-round.md, D022: injetor híbrido) → habilita EXP-21 (injetor buildável com o EXP-21, owner-gated). RD-TAINT ✅ CONCLUÍDA (rd-taint-camel-round.md, D023: envelope não-forjável no seam do secret-scan) → fecha o gap o2 (probe buildável; enforcement owner-gated+security-review). Resta só RD-ECA (trigger: 2ª disputa de precedência real — não bateu). As 3 rodadas de implementação-research (RD-U/RD-CRASH/RD-TAINT) estão FECHADAS.

### OWNER-GATED (fora da fila até você decidir)
EXP-20 medição · EXP-21 execução · enforcement de memória · route regret/ECE ·
RF.1 fase 2 · CQ.1 enforce · DW.4 auto-fork · target-worker-world.

### Itens NOVOS derivados das decisões do owner D013-D017 (2026-07-18)
| id | item | fonte | tam |
|---|---|---|---|
| **N-AUTHCHAIN** (C2-v2) | acceptanceAuthority vira registro TIPADO de cadeia de responsabilidade `{actorType: user\|worker\|overseer, identity, at, sessionRef?}`; padrao unificado de credito de decisao/aprovacao/aceite (casa com subject dimension + C12 digest). Upgrada o brief do C2. | D013 | M |
| **N-SECREVIEWER** | perfil de agente `security-reviewer` (.claude/agents + espelho codex) + fluxo de parecer que o humano RATIFICA. Escala expertise; humano vira ratificador. | D014 | M |
| **N-TRUTHRECON** | motor de reconciliacao de FONTES DA VERDADE (codigo/docs/historico/3os): doc como fonte preferida; deducao auditavel quando diverge. Direcao-MAE da memoria governada -- GM-3 vira uma fatia. Confirma o achado do GM-5. | D015; GM-5 | L (research->spec) |
| **N-RACEMODE** | topologia de workflow opt-in "race mode": varios modelos correm na mesma task+contexto pra achar o melhor. EXP-20 valida. | D016 | M |
| **N-VENDORCREDIT** | tracking de credito/quota restante por vendor + U(custo_tokens ponderado por preco, tempo, escassez) -- alimenta routing/regret/ECE. | D017 | M |

### N-TRUTHRECON decomposto pela rodada #3 (2026-07-19, WF-...050502, 5 ideadores NVIDIA)
Rodada `docs/research/truth-reconciliation-round.md`. **Planos detalhados: `docs/research/truth-reconciliation-implementation-plans.md`** (N-TRUTHRECON-PROBE já CONSTRUÍDO = EXP-22/truth-divergence probe). Convergencia independente: precedencia = funcao pura, probe measure-only antes de enforcement, degradacao emergente, reusa T-HASHCHAIN+GM-3. DNS (RFC 1035/2181/4035/2308) e a arquitetura de referencia (w-005). Fatiado:
| id | item | fonte | tam | gate |
|---|---|---|---|---|
| **N-TRUTHRECON-PROBE** (EXP-22) | probe measure-only: mede `divergenceCount` entre as 4 fontes por commit/retrieval (estende o GM-5 doc↔codigo pras 4 fontes). ZERO enforcement. Log = contagem/hashes, NUNCA conteudo (w-004 sink-risk). O UNICO buildavel ja (medicao, nao controle). | rodada #3; EXP-22; D008 | M | **buildavel** |
| **N-TRUTHRECON-CORE** | motor ATIVO: PrecedenceResolver funcao pura 2-tier (autoritativo=git+records / advisory=specs+vendor; doc-preferida = mapeamento de tier) + ReconciliationRecord `{fact,winningSource,loserSources,precedenceRuleApplied,tier,degraded,absentSources,inputHashes,at,subject}`. Nomenclatura DNS (TR-DNS). | rodada #3; D020 | L | **owner-gated** (e controle: precisa EXP-22 justificar, como C9) |
| **N-TRUTHRECON-TRUST** | hardening (w-004): `absentSourceName` e side-channel (expor so a papel autorizado); vendor docs = input nao-confiavel (parsing sandboxed); registro herda provenance-firewall do GM-3. Dobra no N-SECREVIEWER. | rodada #3; D014 | M | owner-gated (contingencia) |
| **N-SCANNER-FP** | bug achado pela rodada: o `openai-style-key` do secret-scan casa `sk-` DENTRO de "ta**sk**-slug" -> withheld 2 resultados validos. Fix = ancora word-boundary antes de `sk-`. Caminho de seguranca -> review isolado. | achado rodada #3 | S | owner-gated (security path) |
| ~~N-TRUTHRECON-PERF~~ | pipeline O(S×R)+cache+paralelo+backpressure (w-002). ESTACIONADO: YAGNI ate o EXP-22 medir volume. Upgrade path guardado. | rodada #3 | — | estacionado (measure-first) |

### N-COMPACTION — compactação automática de contexto (rodada compaction-round.md, 2026-07-19)
Convergência 4 ondas (NVIDIA 5 + Sonnet 3): A_ctx-watermark+histerese, tiers-GC, measure-first.
**Planos de implementação detalhados (implementer-ready): `docs/research/compaction-implementation-plans.md`.**
| id | item | fonte | tam | gate |
|---|---|---|---|---|
| **N-COMPACTION-CFP** (EXP-23) | Context Fill Probe: loga fill%(declared+A_ctx)/canary-recall/latência/custo/cache-hit/compact-events+outcome; tabela (modelo,role,task,fill%)→qualidade com noise-floor gating. NUNCA compacta. | rodada; EXP-23; D008 | M | **buildável** |
| **N-COMPACTION-CTRL** | Compact Controller: gatilho A_ctx×role×task + histerese + snap-em-fronteira; preservação tiers keep-GC/summarize/drop; re-sumarização depth-bound=1; fail-safe por checkpoint + validação determinística. | rodada; D029 | L | **owner-gated** (controle: precisa EXP-23) |
| **N-COMPACTION-SECRET** | secret-tier never-summarize/never-persist no checkpoint; dobra o RD-TAINT/D023 (o taint-envelope marca Tier-0-secret; o sumarizador é sink). | rodada NVIDIA w-004; D023 | M | owner-gated (security review) |

### N-PTC — Programmatic Tool Calling (rodada ptc-round.md, 2026-07-19)
Convergência 4 ondas (NVIDIA 5 + 3 Sonnet high WebSearch): loop no nosso sandbox p/ todo vendor, probe-first.
**Planos de implementação detalhados (implementer-ready): `docs/research/ptc-implementation-plans.md`.**
| id | item | fonte | tam | gate |
|---|---|---|---|---|
| **N-PTC-PROBE** (EXP-24) | probe measure-only: latência/token/CPU tradicional-vs-PTC-emulado na cadeia discover, matched-budget, noise-floor gated. NUNCA muda produção. | rodada; EXP-24; D008 | M | **buildável** |
| **N-PTC-ENGINE** | módulo harness_tools (funções dict→str no sandbox) + loop pause/resume + code-extraction + gate AST estático + return filtrado; rota o loop pelo nosso sandbox p/ todo executor. | rodada; D030 | L | **owner-gated** (controle+segurança: precisa EXP-24 + security review) |
| **N-PTC-TAINT4** | 4º sink de taint = o stdout/stderr do sandbox; dobra o RD-TAINT/D023 (o check roda no stdout capturado). + lethal-trifecta invariant. | rodada parity+NVIDIA w-004; D023 | M | owner-gated (security) |
| **N-PTC-CONFORMANCE** | capability programmatic-tool-calling + supportState + c9 ptcTokenScope + c5 no-amplification (stub-set ⊆ tools declaradas). | rodada; T-ADAPTERCONF | M | owner-gated |
| **N-TOOLSEARCH** (fronteira) | tool-search/RAG-sobre-tools: carregar só os schemas relevantes (append-not-swap p/ cache) quando há muitas tools/MCP. Testável SEM o PTC engine. | rodada fronteira; Gorilla arXiv:2305.15334 | M | buildável (mede token) |

### N-U — função de utilidade U(rota,outcome,custo) (rodada rd-u, D021)
**Planos detalhados: `docs/research/rd-u-implementation-plans.md`.** Destrava regret (EXP-17) + ECE.
| id | item | fonte | tam | gate |
|---|---|---|---|---|
| **N-U-FUNCTION** | U = w_q·Q·τ − w_c·C·S − w_t·T como função pura sobre o route_ledger → probe de regret measure-only (EXP-17). + calibrar reverted=0.5. | rodada; D021 | M | **buildável** |
| **N-U-DRIVING** | U dirigindo routing (bandit/C4/RF.1). | rodada; SPEC-144 | L | owner-gated (controle) |
| ~~N-U-VARIANCE~~ | termo de variância Sharpe (σ²=noise floor). ADIADO até corpus por-rota. | rodada w-005 | M | adiado |

### N-CRASH — crash injection determinística (rodada rd-crash, D022)
**Planos detalhados: `docs/research/rd-crash-implementation-plans.md`.** Habilita EXP-21.
| id | item | fonte | tam | gate |
|---|---|---|---|---|
| **N-CRASH-INJECTOR** | injetor híbrido: cooperativo HARNESS_CRASH_AT (a/c/d) + Job-Object (b hang), contador determinístico, guard no entrypoint do worker. Windows-real. | rodada; D022 | M | buildável test-infra (com EXP-21) |
| **N-CRASH-EXP21** | a medição de recovery (duplicate-effect/orphaned-work/time-to-resume) por modo. | rodada; EXP-21 | M | owner-gated (medição) |

### N-TAINT — taint / CaMeL (rodada rd-taint-camel-round.md, D023) — PRIORIZADO (dep do PTC)
**Planos detalhados: `docs/research/rd-taint-implementation-plans.md`.** Cadeia cross-rodada:
**N-TAINT-ENVELOPE + N-TAINT-SINKS → N-PTC-TAINT4 → N-PTC-ENGINE** (por isso priorizado).
| id | item | fonte | tam | gate |
|---|---|---|---|---|
| **N-TAINT-PROBE** | would-block probe: quantos valores tainted (secret-read/web-fetch/worker-output) egressariam num sink hoje. Reusa secret_scan. NUNCA enforça. | rodada; D008 | M | **buildável** |
| **N-TAINT-ENVELOPE** | o metadado de taint NÃO-forjável harness-injetado (source-stamp nas 3 origens; taint_map; opcional no hash-chain). | rodada; D023 | L | owner-gated (security) |
| **N-TAINT-SINKS** | enforcement fail-closed nos 3 sinks (prompt/persistido/log) + **o 4º (PTC stdout)** estendendo o secret-scan; O(campos-tainted), break-glass rate-limited, checker fail-closed. | rodada; D023 | M | owner-gated (security) — **pré-req do PTC engine** |
| **N-TAINT-CAMEL** | control-plane capabilities (trust-tiers + GM-3 authority), sem IFC runtime por-valor. | rodada; GM-3 | M | owner-gated |

### Backlog clássico não-artigo (interleave por prioridade própria)
Verificado 2026-07-18: CE.2/CE.3/OB.1/OB.2 JÁ SHIPADOS (cenários existem). Abertos:
- **P1:** en-gui-strings + en-lib-strings + en-default-guard (terminologia EN); security-baseline-sdd.
- **P2:** DW.5 (re-decomposition at settle), SEC.4 (hash-pin admission), CQ.1-enforce (owner-gated), CQ.4 (precisa oracle-runner), codex-stream-parity, config-keys-gui, graphs-screen-gui, M5.sum, records-subject-dimension, workspace-state-exclusion, handoff-subject-confinement, svc-mcp-wiring (owner MCP-transport decision).
- **P3/parked:** wiki-sources/screen/spec-guard, docs-consolidation, en-docs/en-comments, pyo3, UX-GA.4, CE.5-9, DW.6-8, SEC.5-7, CAP.4/5, tasks-enqueue, queue-reorder/start-action, research-run-form.

## Porquê desta ordem (lógica de arquiteto)
1. **Enablers custam uma tarde e pagam semanas.** E-ROUTESCORES (10 linhas) destrava regret+ECE; E-SCOPETAG destrava o track de memória inteiro; E-3LANE serve DOIS experimentos.
2. **O sandbox parecia greenfield e NÃO é** — `sandbox_spawn` (SPEC-148) já tem tier+icacls+Job Object. Esse recon mudou o Q7-1 de "L do zero" para "estender um M". Sem ele, re-planejaríamos 60% de algo que já existe.
3. **Medir antes de controlar** (C18→C9, GM-5→enforcement, A_ctx→CE.7): controle sem a medição que o justifica é o anti-padrão que a própria pesquisa condena.
4. **Owner-gate e research atrás do pré-requisito, nunca na frente** — regret não entra na fila porque needs U (RD-U); EXP-21 não roda sem RD-CRASH. É literalmente "não criar feature sem dependência pronta".
