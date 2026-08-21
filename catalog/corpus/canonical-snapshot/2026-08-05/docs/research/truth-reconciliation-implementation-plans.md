# Planos de implementação — Truth-source reconciliation (N-TRUTHRECON-*)

Parqueado no backlog. Derivado de `truth-reconciliation-round.md` (5 ideadores NVIDIA) + D020.
**Já construído:** N-TRUTHRECON-PROBE = EXP-22 = o truth-divergence probe (`testing/probes/
truth_divergence_probe.py`, commit `6dd9472`) — mede a divergência doc↔código; NÃO listado aqui.

**Reuso:** git (`git ls-files` = tier autoritativo); `records` (histórico); `specs/`+vendor docs
(tier advisory); GM-3 provenance firewall (`authority>=signed_policy`); T-HASHCHAIN (tamper-evidence);
`secret_scan.py` (pro N-SCANNER-FP). DNS (RFC 1035/2181/4035/2308) = a arquitetura de referência.

---

## N-TRUTHRECON-CORE — o motor de reconciliação · OWNER-GATED (controle) · tam L

**Goal:** o PrecedenceResolver — função PURA que reconcilia as fontes divergentes deterministicamente.
É controle → só depois do EXP-22 mostrar que a divergência vale (destino do C9).

**Approach:**
1. **2 TIERS (w-001):** AUTORITATIVO = git+records (compartilham hash-chain); ADVISORY = specs+vendor
   (sem proveniência cripto). "doc-preferida" = mapeamento de tier (specs no tier alto), NÃO regra de
   runtime. `resolve(sources: Map<SourceId, SourceState>) -> ReconciliationRecord` — zero estado, zero
   LLM (mesma entrada → mesmo veredito + trilha; o LLM ajudou a DESENHAR, nunca a computar).
2. **ReconciliationRecord** (campos convergidos w-001+003+004): `{fact, winningSource, loserSources[],
   precedenceRuleApplied, tier, degraded:bool, absentSources[], inputHashes{}, at, subject}` + herda
   metadata do provenance-firewall (GM-3). `precedenceRuleApplied` = o "nunca cego" (grava POR QUÊ).
3. **Degradação emergente:** fonte ausente = pulada (chave ausente no Map) + marcada em `absentSources`.
4. **Nomenclatura DNS (w-005):** SOA-serial=divergência; TTL=confidence; NXDOMAIN-negative-cache=gravar
   precedência doc>código nunca em silêncio; DNSSEC=o gate do GM-3.

**Footprint (quando aberto):** `harness_lib/reconciliation.py` (o resolver puro + o record); pontos de
consulta (onde o harness lê um "fato" de múltiplas fontes); spec door NEW + cenário (mesma entrada →
mesmo record; fonte ausente → degraded nomeando-a; doc>código → precedenceRuleApplied gravado).

**Aceite:** o resolver é determinístico (mesma entrada → mesmo record byte-idêntico); degradação
nomeia a fonte ausente; a precedência aplicada fica gravada. **Gate:** OWNER-GATED (controle; precisa
EXP-22 justificar). **Dep:** N-TRUTHRECON-PROBE (EXP-22, feito). **Tam:** L.

---

## N-TRUTHRECON-TRUST — hardening de fronteira · OWNER-GATED · tam M

**Goal:** os 3 achados de segurança do w-004 (o registro/probe/degradação são superfícies sensíveis).
Dobra no N-SECREVIEWER (D014).

**Approach:** (a) `absentSourceName` é um **side-channel** (vaza qual subsistema caiu) → expor só a
papel autorizado; (b) **vendor/3rd-party docs = input NÃO-confiável** → parsing sandboxed (reusa
SPEC-151); (c) o ReconciliationRecord herda metadata do provenance-firewall do GM-3.

**Footprint (quando aberto):** integra no N-TRUTHRECON-CORE (o record + o parsing de vendor);
cenário de segurança (absentSource só a papel autorizado; vendor doc parseado sandboxed).
**Aceite:** o side-channel do absentSource é gated; vendor docs parseiam contidos. **Gate:**
OWNER-GATED. **Dep:** N-TRUTHRECON-CORE. **Tam:** M.

---

## N-SCANNER-FP — fix do secret-scan (achado de brinde da rodada) · OWNER-GATED (security path) · tam S

**Goal:** o padrão `openai-style-key` do secret-scan casa `sk-` DENTRO de "ta**sk-**slug" → engoliu
2 resultados válidos da rodada #3. Fix = âncora de word-boundary antes de `sk-`.

**Approach:** em `secret_scan.py`, o regex do `openai-style-key` ganha um `(?<![\w-])` antes de `sk-`
(ou equivalente) pra não casar dentro de "task-"/"disk-"/etc. Um teste com "task-reconciliation" (que
disparou o FP) prova que não casa mais; um `sk-<20+ realistas>` ainda casa.

**Footprint (quando aberto):** `secret_scan.py` (o regex) + um teste. **Aceite:** "task-slug" não é
mais flagged; uma key real ainda é. **Gate:** OWNER-GATED (caminho de segurança → review isolado; não
afrouxar pra deixar passar key real). **Dep:** —. **Tam:** S.

---

## Ordem sugerida
1. **N-SCANNER-FP** — trivial, tira o FP que atrapalha as rodadas (mas é caminho de segurança → review).
2. **N-TRUTHRECON-CORE** — só quando o EXP-22 (feito, medindo) mostrar divergência > noise floor.
3. **N-TRUTHRECON-TRUST** — junto/depois do CORE, dobrando no N-SECREVIEWER.
