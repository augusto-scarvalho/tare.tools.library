# SPEC-161 — responsibilityChain: o crachá tipado de decisão/aprovação/aceite (N-AUTHCHAIN)

Status: SPEC-161, proposed 2026-07-21 (acceptance: `testing/scenarios/nac_authority_chain.py`).
Origin: D013 (owner 2026-07-18) via `docs/research/acceptance-authority-proposals.md`
(Proposta B com gancho C — recomendação do arquiteto, fechos D042). Door: NEW —
nenhuma superfície grava ator tipado hoje (mapa 2026-07-21: 8 sites, zero atores).
relates-to: decision-inbox (C12 digest), T-HASHCHAIN, N-SECREVIEWER (D014).

## Goal

Toda gravação de decisão/aprovação/aceite passa a creditar um ATOR TIPADO — e,
onde há múltiplas partes, a CADEIA ordenada de papéis — em vez do padrão atual
(timestamp + prosa livre; aprovação booleana; "reviewer sem reviewer" no reckon).
Torna executável o separation-of-duties (proposer ≠ accepter) e dá base ao papel
security-reviewer (D014: o reviewer é um papel na cadeia).

## Applicability

Novo `scripts/harness_lib/responsibility.py` (record + stamp + verify + digest +
self-check). Fase 1 injeta o ator nos 3 pontos de maior alavancagem do mapa:
(1) `decision_inbox._resolve_escalation` / `apply_decision` (+ fold em
`escalations_lib.compact_supervision_events`); (2) `validation_stamp.cmd_reckon`
→ `stamp_reckon`; (3) `result_contracts.acceptanceCriteria.approvedBy` (validador
tolerante) + `workflow_writes` mergeReview. Campos ADITIVOS; leitores toleram
entradas legadas sem ator. Não toca T-HASHCHAIN (o chainDigest é gancho local).

## Requirements / invariants (numbered, testable)

1. **Record tipado.** Um ator é `{role, actorType, identity, at, sessionRef?}`;
   `actorType ∈ {user, worker, overseer, automation}`; `role` livre mas os
   canônicos são proposer|reviewer|accepter. `automation` credita owner-gates
   determinísticos — NUNCA se apresenta como humano.
2. **Inferência com override.** `make_actor(role, ...)` infere de env
   (`HARNESS_ACTOR_TYPE`/`HARNESS_ACTOR_IDENTITY`; `HARNESS_WORKER_ID` ⇒
   worker:<id>) com fallback user + git user.name; params explícitos vencem env.
   Nunca levanta — inferência falha ⇒ `{actorType: "user", identity: "unknown"}`
   honesto, não crash.
3. **Cadeia ordenada + separation executável.** `stamp(chain, actor)` appenda
   preservando ordem; `verify_separation(chain)` retorna (ok, detail) com
   ok=False quando proposer.identity == accepter.identity (two-person control,
   §7.7 R2/R3). Advisory: quem decide o que fazer com o False é o chamador.
4. **Gancho C.** `chain_digest(chain)` = sha256 do JSON canônico (sort_keys,
   separators compactos) — aditivo, determinístico, reservado para o binding
   assinado futuro. Digest de cadeias iguais é igual; de cadeias diferentes,
   diferente.
5. **Fase-1 writers.** (a) resolver escalation grava `actor` (role=accepter) no
   payload do evento e no `resolvedRecords`; (b) `reckon --record` grava `actor`
   (role=reviewer) em `lastReckon` + linha JSONL — fecha o "reviewer sem
   reviewer"; (c) `acceptanceCriteria.approvedBy` aceita o record tipado OU a
   string legada (validador promove string a `{actorType:"user", identity:<s>}`
   na LEITURA, sem reescrever estado); mergeReview ganha `actor` ao aprovar.
6. **Aditivo/tolerante.** Nenhum leitor existente quebra com entradas sem ator;
   nenhum estado legado é reescrito em massa.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| Proposta B (cadeia) e não A (crachá único) | D013 pede "entender a CADEIA de responsabilidade"; doc de propostas §B; destrava D014 e separation-of-duties executável |
| gancho C = digest, não assinatura | mesmo teto declarado do T-HASHCHAIN; assinatura real atrás do gatilho de infra-de-chave |
| 4º actorType `automation` | mapa 2026-07-21 achou owner-gates automáticos; creditar automação como humano seria fabricação |
| Fase 1 = 3 sites, não os 8 | pontos de alavancagem do mapa (menor churn, writers únicos); os demais sites migram quando tocados |

## Ceilings (upgrade paths)

- Identidade é DECLARADA (env/git), não autenticada — igual a todo o resto do
  harness local-first. Assinatura criptográfica da cadeia = gancho C + infra de
  chave (gatilho: primeiro deploy multi-operador).
- `sessionRef` é opcional e best-effort (env `CLAUDE_SESSION_ID` quando existir).
- A cadeia completa multi-papel entra por site conforme os fluxos multi-parte
  forem tocados; Fase 1 grava o ator do ato (role único por site).

## Test strategy

- `nac_authority_chain.py`: make_actor (inferência env worker/overseer/fallback,
  override explícito, nunca-levanta), stamp/ordem, verify_separation (viola /
  ok / cadeia sem proposer), chain_digest (estável/sensível), e os writers da
  fase 1 em raiz temp (resolver escalação grava actor; reckon grava actor;
  validador aceita string legada E record tipado).
- Regression: cenários existentes (di_decision_inbox, pvg, dw_workflow_schema,
  se_self_review) continuam verdes — campos aditivos.

## Validation

- `python testing/scenarios/nac_authority_chain.py` green.
- `python scripts/harness_lib/responsibility.py` self-check green.
- `spec-pack` green.
