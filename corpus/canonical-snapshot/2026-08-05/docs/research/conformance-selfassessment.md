# Rodada R1 — Self-assessment de conformidade (artigo §5.9 + App F + ATAM)

Rodada 1 de 5 da diretiva **D012** (owner 2026-07-18: todas as rodadas via NVIDIA,
sequenciais, incrementando `docs/research/article-coverage-backlog.md` antes de
qualquer implementação). Gate humano de fase 2 pré-aprovado pela D012.

## Fase 0 — Pergunta, critérios, budget, largura

- **Pergunta:** que fração do contrato mínimo do artigo (16 suites App F, testes
  por plano §5.9, 24 cenários ATAM, invariantes App I.8) nossos gates/cenários/
  hooks/probes JÁ provam, com que nota na escala de evidência 0-3 (§11.3-c), e
  onde estão os gaps reais?
- **Critérios de sucesso:** (a) cada requisito do artigo recebe nota 0-3 + item de
  evidência do inventário OU gap nomeado; (b) claims dos workers sobre o repo são
  HIPÓTESES até auditoria local do orquestrador (D012; precisão de miner ~75%);
  (c) regra App F-17/18 adotada: suite falha/ausente CAPA a dimensão de
  maturidade — sem média compensando; (d) saída = incremento do backlog de
  cobertura (linhas novas/status corrigidos/intakes).
- **Largura (D010):** 3 workers POR CONSTRUÇÃO — mapeamento particionado em 3
  fatias disjuntas (B1 App F F1-F16; B2 §5.9 planos + App I.8; B3 ATAM 1-24).
  É cobertura por partição, não redundância — o modo focado não se aplica a
  split disjunto; Δ_m de cada worker = sua fatia inteira.
- **Budget declarado:** wave única ≤ 45k tokens (3 × ~10k input + ~5k output).
  Executor `openai-compat` (NVIDIA Build, D012). Sem wave de crítica: a
  convergência é a auditoria LOCAL do orquestrador (evidência é verificável
  determinísticamente no repo — modelo criticando modelo não paga aqui).
- **Design declarado (L18):** não é experimento de medição — é auditoria com
  rubrica fechada (escala 0-3 do §11.3-c + regra de capa F-17/18). Cartão de
  métodos: n/a; o produto alimenta o M-frame interno (D008/D011).

## Fase 1-2 — Evidência embutida

Workers NVIDIA não leem o repo (D012): o packet embute (a) o lado-requisito
(one-liners extraídos do manuscrito pela varredura de 2026-07-18, 6 extratores)
e (b) o lado-evidência (inventário determinístico gerado nesta sessão: 138
cenários com check-ids, 32 fixtures do gate, 13 hooks, 7 probes, 11 kinds de
gate). Proveniência: requisitos `[repo]` (extração auditada), inventário
`[repo]` (gerado por script), mapeamentos dos workers `[judgment]` até
auditoria.

## Execução

- Wave 1 tentativa 1: `WF-20260718-215103-726280` — 3/3 workers responderam mas
  INVÁLIDOS por contrato de transporte: fork-join sem profile capou
  `maxWorkerOutputChars=4000` (auditoria produz 7-10k) e o GLM marcou severidade
  `high` sem os campos de evidência exigidos. Lição p/ waves NVIDIA de auditoria:
  usar profile com cap 12000 + rubrica fixando `severity: info`. Mantido p/
  forense; não reduzido.
- Wave 1 v2: `WF-20260718-215453-361908` (profile `research-divergence` com
  branches EXPLÍCITOS — 1º consumo vivo da regra por-construção do L16;
  `slots.declaredWidth` auto-stampado custom/3). Executor `nvidia-compat`
  (GLM z-ai/glm-5.2). Task embutido: 13.4k chars (~4.3k tok) — requisitos
  B1/B2/B3 + inventário (138 cenários, 32 fixtures, 13 hooks, 7 probes) +
  rubrica 0-3 + regra severity=info.
- Follow-up B3: `WF-20260718-220210-201111` (1 worker por construção) — a wave
  v2 teve furo de cobertura: w2 E w3 processaram o B2 (instrução de bloco por
  branch-title tem aderência fraca no GLM effort-baixo); B3 re-rodado isolado,
  24/24 vereditos. Lição p/ waves NVIDIA: 1 BLOCO POR WAVE quando a partição
  importa, ou repetir o bloco no topo do task (feito no follow-up).
- **Override de budget declarado:** `maxWorkerPromptTokens=3900` assume worker
  que LÊ o repo (required-reads fora do prompt). Worker HTTP NVIDIA não lê
  arquivo (D012) → o conteúdo vai embutido por desenho, ~4.3k tok/worker.
  Total da wave (~15k in + ~9k out) fica DENTRO de `maxTotalPlannedTokens`
  (42k). Override honesto via `workflow start --override-budget` (trilha
  gravada; caminho testado `budget:override-recorded` no m2).

## Síntese (auditada pelo orquestrador — mapeamentos verificados contra o inventário real)

Auditoria anti-fabricação: 8 nomes fora do vocabulário em 63 achados — TODOS
abreviações legítimas do bloco de maquinário embutido (ex.: `noise_floor` vs
`noise_floor_probe`, `N1 receipts`); precisão de citação ≈ 100% no que importa.
Vereditos de nota são hipóteses do GLM ajustadas pelo orquestrador onde indicado.

**App F (16 suites):** nota 2 em 11 suites (F2-F11, F14); nota 1 em 5:
- F1 Constitution — sem constituição compilada/assinada (🅿️ ECA); o real é
  protected-files+deny hooks (slice de deny-overrides).
- F12 Trajectory — ir1/ir6/ir8 valem 2 (N2, L3, L4); hash-chain/assinatura = 0 (🅿️).
- F13 Privacy — scrub/redaction/vault reais; classificação formal por item ausente.
- F15 Promotion — CORREÇÃO do orquestrador: 1→**2** (registry D008 + portas
  SPEC-116 + exl 5/5 + gg governança são teste interno real; o GLM só mapeou gg).
- F16 Interop — esh cobre spawn-hygiene; suite de conformance por adapter ausente
  (→ C3/C16b já ⬜ no backlog).
- **ZERO nota 3 em todo o assessment** — honesto: nada tem evidência
  independente/externa ao longo do tempo (multi-org é gatilho D011).

**Planos §5.9 + App I.8 (23 linhas):** maioria nota 2; nota 1 concentrada em:
P5 context-economy (reconciliação de accounting por chamada — C12b ⬜) e
I10 (counterexamples como trace — formal 🅿️).

**ATAM (24 cenários):** 9 provável-passa (A1 router swap, A2 provider outage
[failover r15], A6 crash-resume, A10 reprodução [records+route tuple], A12
catálogo, A20 aprovação stale [C12], A21 pause worker [qcw], A22*, A23*) |
15 desconhecido | 0 falha-hoje confirmada. Os 15 desconhecidos são o produto:
viram checklist de teste-de-mesa (abaixo).

**Incrementos aplicados ao backlog de cobertura:**
1. Linha nova ⬜ "ATAM mesa-test checklist" (15 desconhecidos → 15 testes de
   mesa baratos, 1 doc; prioriza A13 crash-antes-de-receipt e A14 revogação de
   memória envenenada).
2. Linha nova 🔬 "crash-injection na fronteira do adapter" (A13/§5.7: nenhum
   teste crasha entre efeito externo e receipt; candidato a fixture).
3. F15 corrigida para 🟡→nota 2 no self-assessment (evidência registry/portas).
4. Regra App F-17/18 adotada: dimensão de maturidade capada pela pior suite
   mandatória → nossa M-interna segue M2-M3 (F1/F12 nota 1 capam M2 "governed"
   na dimensão constitution/trajectory até os slices nomeados subirem).
