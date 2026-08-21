# Planos de implementação — U(rota, outcome, custo) (RD-U)

Parqueado no backlog. Derivado de `rd-u-utility-function-round.md` (5 ideadores NVIDIA) + D021.
Destrava route **regret (EXP-17)** + **ECE/calibração** (hoje travados por falta de U).

**Reuso:** `route_ledger.py` (outcome kept/rejected, token-cost, latência por rota); `cost_metrics.py`
(preço); model-cards (preço-por-token); N-VENDORCREDIT (escassez S); `accountingSemantics`
(T-ADAPTERCONF: quais vendors MEDEM token vs ESTIMAM = o τ); E-ROUTESCORES (baseline de latência);
noise floor L13. EXP-17 = o consumidor do regret.

---

## N-U-FUNCTION — U como função pura measure-only · BUILDÁVEL JÁ · tam M

**Goal:** computar `U(rota) = w_q·Q·τ − w_c·C·S − w_t·T` sobre o route_ledger existente, alimentando
um probe de regret measure-only (EXP-17). Não muda routing (isso é owner-gated) — só MEDE.

**Approach (a função, D021):**
- **Q** = outcome do ledger (kept=1, reverted=0.5*, rejected=0). *`reverted=0.5` é a ÚNICA constante
  subjetiva → calibrar (EXP candidato: se revert ≈ near-failure, 0.25).
- **τ** = trust-discount do `accountingSemantics` (vendor que MEDE token τ=1; que ESTIMA τ<1).
- **C** = tokens × preço-do-vendor, normalizado por route-class (ledger + model-cards).
- **S** = escassez = `max(1, 1/(remaining/initial))` do N-VENDORCREDIT (até existir, S=1 marcado).
- **T** = latência normalizada pelo p99 da route-class (ledger + E-ROUTESCORES).
- Forma **weighted-linear** (justificada: única que dá escalar comparável + O(1) + comparação
  por-termo contra o noise floor; lexicográfica não dá ΔU; Cobb-Douglas quebra o L13 + colapsa em Q=0).
- **regret = U(best) − U(chosen)**; `|ΔU| < noiseFloor L13 → empate`. **ECE** via Q·τ como prob
  prevista (Brier score, w-005).

**Footprint:** `harness_lib/utility.py` (a função pura U + regret + a confiança-pra-ECE); um probe
`testing/probes/regret_probe.py` que roda U sobre o route_ledger e emite a distribuição de regret
(measure-only, sibling do truth-divergence). Alimenta o EXP-17.

**Aceite:** U computa determinístico sobre o ledger; regret = subtração de 2 escalares; `|ΔU|<L13` =
empate; a confiança-pra-ECE sai de Q·τ. Self-check (U monotônica nos termos; empty→0). ZERO mudança
de routing.

**Gate:** measure-only (computa número do ledger existente; não dirige rota) — alçada measure-first.
**Dep:** route_ledger (existe); S degrada pra 1 sem N-VENDORCREDIT. **Tam:** M.

---

## N-U-VARIANCE (v2) — o termo de variância (Sharpe) · ADIADA · tam M

**Goal:** o insight do w-005 (Sharpe) — penalizar a VARIÂNCIA de outcome da rota (a variância É o
noise floor L13; rota de alta variância é mais arriscada). `U = ... − (λ/2)·σ²`.

**Approach:** precisa de N observações por rota pra estimar σ² — a linear v1 não precisa. Adiar até o
corpus de route_ledger ter N suficiente por rota. Upgrade path guardado.

**Gate:** adiada (measure-first: sem corpus, sem σ²). **Dep:** N-U-FUNCTION + corpus. **Tam:** M.

---

## N-U-DRIVING — U dirigindo routing · OWNER-GATED (controle) · tam L

**Goal:** usar U pra ESCOLHER/avaliar rota (bandit/C4/RF.1 fase 2). É controle → já era owner-gated;
precisa o N-U-FUNCTION + o regret medido (EXP-17) justificando.

**Footprint (quando aberto):** liga U ao router (SPEC-144); casa com o Simulate-route da GUI (GUI-RG3).
**Gate:** OWNER-GATED. **Dep:** N-U-FUNCTION + EXP-17 corpus. **Tam:** L.

---

## Ordem sugerida
1. **N-U-FUNCTION** — buildável; destrava regret+ECE (EXP-17) sem tocar routing. + calibrar reverted=0.5.
2. **N-U-DRIVING** — só quando o regret medido justificar (owner-gated).
3. **N-U-VARIANCE** — v2, quando houver corpus por rota.
