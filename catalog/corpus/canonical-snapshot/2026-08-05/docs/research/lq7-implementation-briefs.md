# LOOP QUEUE 7 — briefs prontos + perguntas salvas (backlog-first, pós-D012)

Índice DURÁVEL dos plan briefs. Os briefs completos vivem em `.harness/handoff/
plan-lq7-*.md` (gitignored); as decisões finais + **perguntas salvas** estão
espelhadas aqui. As 5 rodadas D012 FECHARAM; owner: "começa a elaborar os
planos, ordem sequencial por criticidade".

**Ordem de criticidade (LOOP QUEUE 7 no IMPLEMENTATION_BACKLOG.md, decidida pelo
overseer):**
1. **Q7-1 harness-own sandbox** — SPEC-151 completa (`specs/40-features/harness-own-sandbox.md`), P0 segurança.
2. **Q7-2 C1** constantes + graus de evidência (governança fundacional).
3. **Q7-3 C18 route churn + C6 CTS** (measure-only; desbloqueia histerese C9).
4. **Q7-4 C3** capability support-states.
5. **Q7-5 C2** residual risk register (consome a saída do Q7-1).
6. **Q7-6 C5** métricas de aprovação.
7. **Q7-7 C19 Π-lite + C20 recovery** (measure-only, menor urgência).

Implementação começa do topo quando o owner mandar; um item por vez.

## Q7-1 — harness-own sandbox (SPEC-151, plano = a própria spec)
Spec completa em `specs/40-features/harness-own-sandbox.md` (não é brief
gitignored — é spec committada). SB-1 Job Object + SB-2 NTFS ACL dual-mode +
SB-3 manifest de degradação = núcleo sem-admin. Perguntas salvas (Q1-Q4) na
seção final da spec.

## C1 — constantes de decisão + graus de evidência (`plan-lq7-c1`)
Tabela §6.6 (α/power/δ_Q/δ_C/δ_L/δ_V/ECE) + regra lexicográfica + graus 1-4 +
tipagem de fatores em `EXPERIMENT_METHODOLOGY.md`; campo `evidenceGrade` no
registry. Footprint: metodologia, experiment_registry.py, spec exl, cenário exl.
**Perguntas salvas:**
- Q1: `evidenceGrade` vira coluna no painel pxe agora ou follow-up?
- Q2: `_advise` sugere grau por heurística (shipped→≥3) ou só aponta a doc? (prop: só aponta)
- Q3: EXPs já shipped ganham grau retroativo numa curadoria do owner? (~10 min)

## C18 — route churn probe (`plan-lq7-c18`), measure-only
Probe `route_churn_probe.py` sobre o route ledger (churn por demandId + reversals),
Floor L13 como piso. Pré-req da histerese C9 (medir antes de controlar). Não toca
o route-loop. **Perguntas salvas:**
- Q1: "evidência material" = proxy simples (nova outcome/riskFlag) ou critério mais rico?
- Q2: tile no painel agora ou só artefato? (prop: artefato)
- Q3: churn cross-sessão ou por período? (prop: global + byRoute)

## C19+C20 — Π-lite + recovery probes (`plan-lq7-c19-c20`), measure-only
Π = ⟨1−viol, 1−overrun, 1−replay_div, recovery, 1−unknown⟩ com veto de violação
crítica (espelha a lexicográfica do C1); 4 métricas de recovery do records ledger.
Componente sem dado = n/a honesto, nunca fabricado. **Perguntas salvas:**
- Q1: Π agregado ou só vetor? (prop: vetor + flag de veto, nunca escalar sozinho)
- Q2: "último-bom" p/ recovery-point-error = último gate pass? (prop: sim)
- Q3: um probe ou dois? (prop: dois, worker unifica se o reader for o mesmo)
- Q4: acopla ao M-frame D008 ou fica artefato? (prop: artefato; acoplamento é decisão do owner)

## C6 — cost-to-success no `metrics` (`plan-lq7-c6`)
`cost_metrics.summarize()` +`costToSuccess`/`costToUsefulOutcome` + `byModelCTS`,
derivado do delegation ledger. Footprint: cost_metrics.py, cenário ob, spec cost.
**Perguntas salvas:**
- Q1: `partial` entra no denominador de costToUsefulOutcome? (prop: não)
- Q2: CTS por task-class? depende de taxonomia de task (prop: adiar)
- Q3: CTS por sessão ou só global+byModel? (prop: global+byModel)

## C3 — estados native/emulated/degraded/unsupported de capability (`plan-lq7-c3`)
Campo `supportState` em capabilities.json (formaliza a nota codex SubagentStop);
helper + audit em agent_parity.py. **capabilities.json NÃO é protegido (recon
confirmou)** → edição livre. Footprint: capabilities.json, agent_parity.py,
spec SPEC-113, cenário ap.
**Perguntas salvas:**
- Q2: `supportState` por capability ou por (capability × vendor)? (prop: por vendor quando divergem)
- Q3: `degraded` rebaixa nota de maturidade do self-assessment automaticamente? (prop: sim, follow-up)

## C2 — residual risk register + doctor advisory (`plan-lq7-c2`)
`.harness/state/residual-risk-register.json` (schema §14.7-2) + verbo `risk
list/show` + doctor `residual-risk-review-due`. Door NEW SPEC-116. **Consome a
saída da R2** (a lista-semente muda quando o sandbox fecha o risco "HTTP sem
sandbox"). Footprint: state json, repo_health.py, cli_registry, spec nova, cenário rr.
**Perguntas salvas:**
- Q1: quem é a `acceptanceAuthority` default dos riscos seed? (precisa nome/handle real)
- Q2: `risk add/accept` via CLI agora ou follow-up? (prop: follow-up — aceitação é ato de autoridade)
- Q3: eu listo os 4 riscos-semente ou o owner revisa antes? coordenar C2 DEPOIS da R2
- Q4: cadência de `reviewDate`? (prop: 90d, alinhado ao reviewBy dos EXPs)

## C5 — métricas do serviço de aprovação (`plan-lq7-c5`)
Bloco `approvals` no metrics (pending/sloBreached/median-p95 age/overrideRate/
invalidatedCount/expired), reusando `_age_fields`/`sloHours` do decision_inbox.
Footprint: cost_metrics.py ou collector do inbox, cenário di, spec.
**Perguntas salvas:**
- Q1: `overrideRate` é mensurável? só se o registro guardar o recomendado vs escolhido
  (se não guarda hoje, a métrica vira 🔬 e sai da fatia) — VERIFICAR no recon
- Q2: por sessão ou agregado? (prop: agregado)
- Q3: `post-approval incidents` exige linkar decisão→efeito → fora desta fatia

## C8 — ~~doctor advisory de EXP vencido~~ JÁ EXISTIA
Recon achou `repo_health.checks` check (6) `experiment-overdue` já fazendo isso.
Removido da fila; backlog corrigido (§6.4 → ✅ feito).
