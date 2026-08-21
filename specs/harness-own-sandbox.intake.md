# Intake refinement — door NEW checklist — harness-own sandbox

<!-- Preparado pela rodada R2 (D012). NÃO implementar antes das 5 rodadas D012
fecharem. Fonte: docs/research/harness-own-sandbox.md (portfólio de design). -->

## Request (verbatim)

> [D012 / backlog P0] "harness-own sandbox — qual contenção fs/proc/net
> vendor-agnóstica no spawn cobre open models + reforça claude/codex?"
> (article-coverage-backlog.md rodada nº 2; §5.9 runtime plane, §7.4 s5, CaMeL).

## Covered-check (which door?)

| Query | Command | Outcome |
|---|---|---|
| records search | `harness.py records search sandbox containment spawn` | no hit (contenção existente é hook/env-filter/codex-nativo, não sandbox-own) |
| doc-find | `harness.py doc-find sandbox containment runtime plane` | hit em docs de pesquisa (trilha S, round de adoção) — DESIGN, nenhuma spec de capability |

Decision: **NEW** — a contenção existente (hooks path-based, env allowlist S1,
sandbox nativo codex S3) não cobre o worker HTTP open-model, que não tem hook
nem sandbox. Nenhuma spec possui essa capability.

## Goal

Uma camada de contenção aplicada no SPAWN do worker que confina filesystem e
process-tree de qualquer vendor (claude/codex/open-model) com primitivas Windows
sem-admin, degradando egress de forma legível quando o kernel-block exige admin.

## Scope

In scope:
- SB-1: Job Object (ctypes) com KILL_ON_JOB_CLOSE + BREAKAWAY_OK=0 nos 3 seams
  de spawn (`run_one_worker`, `workflow_async_run_one_worker`, dispatch).
- SB-2: confinamento de fs por NTFS ACL (icacls) dual-mode — read worker: escopo
  read-only + result gravável; write worker: worktree dedicado.
- SB-3: confinement manifest `{fsEnforced, egressEnforced, reason}` por spawn +
  probe de capacidade no workflow start; degradação legível (nunca roda
  silenciosamente sem contenção).

Out of scope (contingência, atrás de gatilho):
- SB-4 WFP egress (exige admin+driver) — gatilho: sessão elevada ou multi-tenant.
- SB-5 netsh firewall (advisory-por-imagem) — camada de degradação, não fronteira.
- SB-6 CaMeL token — só observability/defense-in-depth, NUNCA enforcement primário.
- SB-7 reconciliação pós-execução — detecção (reusa apply_patch_paths + diff),
  complementa mas não substitui contenção pré-spawn.

## Actors & surfaces

- Actors: o orquestrador/runtime no spawn; os workers confinados.
- Surfaces: internal (spawn wrapper) + CLI (probe/manifest em status). Sem GUI.
- UI surface? no → Gherkin opcional.

## Proposed acceptance criteria

- [ ] Um worker open-model spawnado sob SB-1 é morto quando o Job fecha (nenhum
      processo filho sobrevive ao workflow) — testável via processo-zumbi.
- [ ] SB-2: um read worker NÃO consegue escrever fora do result path (icacls
      deny-write provado); um write worker AINDA escreve seu worktree.
- [ ] SB-3: quando o egress não pode ser confinado (sem admin), o manifest grava
      `egressEnforced:false` com reason, e o spawn NÃO prossegue silenciosamente
      como se estivesse confinado.
- [ ] Degradação: numa máquina sem a primitiva, o probe reporta e o spawn ou
      degrada declarado ou recusa — nunca roda unconfined em silêncio.
- [ ] Zero quebra: `workflow run` de read + write workers segue verde sob a camada.

## Risks / blast radius

Toca os 3 seams de spawn (núcleo do runtime). Risco de quebrar fan-out se o Job
Object matar workers legítimos; mitigar com probe + flag de bypass declarado
(`workerSandbox=false` escape hatch, como o `workerEnvFilter`). ctypes Win32 é
frágil a versões — isolar num módulo com fallback. Rollback: flag off = comportamento atual.

## Open questions for the human

- Q1: escape hatch `workerSandbox=false` no project.json (paridade com
  `workerEnvFilter`)? (proposta: sim.)
- Q2: sem admin, task open-model que EXIGE rede → recusar spawn ou rodar com
  egress advisory + SB-7 detecção? (proposta: recusar se a task declara egress;
  senão rodar declarado.)
- Q3: SB-1 Job Object aplica a claude/codex também (reforço) ou só open-model
  (o buraco)? (proposta: os 3 — paridade D009; claude/codex ganham lifecycle
  containment de graça.)
- Q4: a camada é pré-requisito de multi-vendor+open-models juntos (round de
  adoção) — priorizar SB-1/2/3 juntos ou SB-1 sozinho primeiro como MVP?
