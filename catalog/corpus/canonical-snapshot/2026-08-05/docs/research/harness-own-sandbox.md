# Rodada R2 — Harness-own sandbox (design round)

Rodada 2 de 5 da diretiva **D012** (NVIDIA, sequencial, backlog-first). P0 da
fila do artigo. Gate humano de fase 2 pré-aprovado pela D012.

## Fase 0 — Pergunta, critérios, budget, largura

- **Pergunta:** qual desenho de contenção fs/proc/net vendor-agnóstico no SPAWN
  (o "runtime plane" §5.9; camada s5 do defense stack §7.4; separação
  CaMeL controle-confiável/dado-não-confiável) torna seguros os workers de
  open models (HTTP, zero contenção própria) e REFORÇA claude (deny honrado)
  e codex (sandbox nativo S3), em Windows 11 single-tenant, sem quebrar os
  fluxos vivos (workflows, rooms, gate)?
- **Contexto duro (da investigação codex 2026-07-18, round doc de adoção):**
  matriz de contenção — claude: hooks deny ✅; codex: hooks ADVISORY (deny
  ignorado), sandbox nativo é o único controle confiável; open models: NADA.
  Building block já commitado: parser `apply_patch_paths` (feed do que o worker
  tenta escrever). Diferidos relacionados: egress geral declare-only (rule 27),
  Bash não-confinado por path, workers HTTP crus.
- **Critérios de sucesso:** (a) cobre os 3 vendors com UMA semântica declarada
  (native/emulated/degraded por capability — vocabulário C3); (b) enforcement
  REAL para o caso open-model (não advisory); (c) Windows-first (sem chroot;
  o que existe: AppContainer/Job Objects/restricted tokens/firewall rules/
  worktree+ACL); (d) integra nos 3 pontos de spawn existentes sem reescrever
  executors; (e) plano de teste determinístico (fixture red-team de escape).
- **Largura (D010): EXPLORATÓRIA — 5 ideators** (research-divergence completo).
  Justificativa: espaço de design aberto (OS-level vs process-level vs
  proxy-level vs fs-overlay), múltiplas fontes possíveis, sem alvo de
  implementação fechado — é exatamente o caso (b) da D010; diversidade nominal
  paga (Diehl & Stroebe).
- **Budget declarado:** wave divergência ≤ 40k tokens + wave crítica seeded
  ≤ 30k (4 críticos). Executor `nvidia-compat`. Override de prompt-cap
  esperado (conteúdo embutido, D012 — precedente R1).
- **Design declarado (L18):** rodada produz DESIGN + spec door NEW (não é
  experimento de medição); a fixture de escape citada nos critérios usará o
  cartão red-team/fault-injection quando implementada.

## Execução

- Divergência: `WF-20260718-220802-675372` (5 ideators, GLM, 5/5 válidos, 15
  concepts). Convergência natural em 5 primitivas: Job Object, WFP/netsh
  (egress), restricted token, NTFS ACL, `sys.audit` hook.
- Crítica seeded: `WF-20260718-221100-955934` (4 críticos). INVÁLIDOS no contrato
  de transporte (alucinaram paths em `sourceFilesVerified` — é design de algo que
  não existe, não há arquivo real p/ citar; lição: crítica de DESIGN dispensa
  sourceFilesVerified). Conteúdo extraído direto dos results — coerente entre os
  4 críticos, sem contradição material. `securityBlockerBlocksWorkflow` não
  disparou porque a wave ficou inválida antes do reduce, mas 3 críticos
  levantaram `blocker` de segurança sobre a MESMA questão (egress) — tratados
  como blocker de design abaixo.

## Portfólio de design (auditado localmente; primitivas Windows verificadas)

Verificação local das primitivas (marcadas `[repo]/[judgment]`):
- Job Object via ctypes `CreateJobObjectW`/`AssignProcessToJobObject` +
  `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` — `[judgment]` API Win32 estável, sem
  admin, mata a árvore no close. Referência: docs Microsoft Job Objects.
- NTFS ACL via `icacls` (subprocess) — `[judgment]` deny-write ACE em paths de
  escopo, allow só no result/worktree; sem admin se o dir é do usuário.
- WFP (`FwpmEngineOpen`…) — `[judgment]` kernel-enforced MAS exige admin +
  driver; rejeitado pelo crítico de segurança p/ o caso comum.
- `netsh advfirewall` — `[judgment]` user-mode, mas regra é POR IMAGE-PATH, não
  por-PID → advisory-por-imagem, não contenção por-processo.
- `sys.addaudithook` (stdlib) — `[repo]` existe em py3.8+; intercepta
  `open`/`socket`/`subprocess` DENTRO do worker Python, mas o worker é um
  processo filho (não confia em si mesmo) → observabilidade, não enforcement.

### Núcleo (o desenho que fecha o P0)
| card | primitiva | cobre | força | onde |
|---|---|---|---|---|
| **SB-1 Job Object baseline** | ctypes Job Object + KILL_ON_JOB_CLOSE, BREAKAWAY_OK=0 | os 3 vendors (envelopa o spawn) | real-block (lifecycle/árvore de processo), sem admin | os 3 seams de spawn |
| **SB-2 NTFS ACL fs-confinement** | icacls deny-write em escopo + allow no result; dual-mode (read worker = escopo read-only + result gravável; write worker = worktree dedicado) | os 3 vendors | real-block (escrita), sem admin | wrapper de spawn, pós-worktree |
| **SB-3 confinement manifest + degradação legível** | campo `{fsEnforced, egressEnforced, reason}` gravado por spawn; probe de capacidade no workflow start | os 3 | declaração honesta | async_state/records |

### Contingência (egress — o ponto duro, admin-dependente)
| card | primitiva | veredito da crítica |
|---|---|---|
| SB-4 WFP per-spawn egress | FwpmEngine (admin+driver) | real-block MAS admin — só quando elevado; degrada p/ SB-5 |
| SB-5 netsh firewall por image-path | `netsh advfirewall` (user-mode) | advisory-por-imagem, teardown crash-safe obrigatório (SetConsoleCtrlHandler+atexit, nome idempotente) |
| SB-6 CaMeL capability-token gate | token no worker | **RECLASSIFICADO**: defense-in-depth/observability, NUNCA a fronteira primária de egress (3 críticos concordam) |

### Fronteira / detecção
- SB-7 reconciliação pós-execução (o `apply_patch_paths` já commitado + diff do
  worktree) = detecção, complementa mas NÃO substitui contenção pré-spawn.

### Operações por card (set-based)
SB-1 **mantida** (fundação, unânime) · SB-2 **mantida** (dual-mode resolve o
"não quebrar write worker") · SB-3 **mantida** (é o requisito de degradação
legível) · SB-4 **experimento/adiada** (só com admin; gatilho) · SB-5
**simplificada** (aceita como camada de degradação legível, não fronteira) ·
SB-6 **rejeitada como enforcement**, mantida como observability · SB-7
**mantida** como detecção.

**Blocker de design honesto (o limite que o artigo também tem):** egress
real-block por-processo em Windows SEM admin não existe com stdlib — a fronteira
de rede confiável exige WFP (admin). Para o worker HTTP open-model o controle
CONFIÁVEL disponível hoje é: **negar o spawn** se egress não pode ser confinado
E a task exige rede, OU rodar sob SB-1+SB-2 com `egressEnforced:false` declarado
+ SB-5 advisory + SB-7 detecção. Isso é o que fecha o P0 honestamente; egress
kernel fica atrás do gatilho de admin.

## Entrega — intake preparado (SEM implementar)

Door NEW SPEC-116 rascunhado em `specs/40-features/harness-own-sandbox.intake.md`
(SB-1/2/3 núcleo; SB-4..7 contingência/detecção com gatilhos). Implementação só
pós-D012 (diretiva do owner). Fecha o item ⬜ P0 "harness-own sandbox" e o gap
do runtime plane (§5.9) / defense-stack s5 (§7.4) no backlog de cobertura.
