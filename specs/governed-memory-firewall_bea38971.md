# SPEC-162 — Governed-memory item registry + GM-3 provenance firewall (measure-only bootstrap)

Status: SPEC-162, proposed 2026-07-21 (acceptance: `testing/scenarios/gmf_memory_firewall.py`).
Origin: R3 memory-governance round (`docs/research/memory-context-management.md`),
owner-gated item "GM-3 provenance firewall" destravado 2026-07-21. Door: NEW.
relates-to: SPEC-161 (responsibility actorType vocabulary), T-HASHCHAIN.

## Goal

O firewall GM-3 ("retrieval recusa memória cuja authority ≥ a da política") é o
BLOCKER de segurança de poisoning (OWASP) de toda a memória governada. Mas ele
"aplica quando o retrieval de itens governados existir" — e esse registro ainda
não existe no código. Este spec entrega o **1º passo committável da R3** (o
bootstrap do GM-5): o RECORD mínimo de item governado com `authority` tier e
`scopeTag` desde o nascimento, MAIS a função de firewall pura e testável — em
modo **measure-only** (mede quantos itens SERIAM recusados/challenged; ZERO
enforcement de retrieval, que não existe). O enforcement liga owner-gated no
gatilho N6, sem reescrever nada.

## Applicability

Novo `scripts/harness_lib/governed_memory.py` (record + firewall + scope-match +
shadow-measure + self-check). NÃO toca `ui_memory.py` (a view de snapshot atual)
nem cria caminho de retrieval. NÃO enforça: `firewall_verdict` é uma função pura
que um retrieval FUTURO chamará; hoje só o shadow-measure a exercita sobre um
registro de fixture. Vocabulário de authority alinhado ao actorType do SPEC-161.

## Requirements / invariants (numbered, testable)

1. **Record governado tipado.** Um item é `{id, content, authority, scopeTag,
   provenance, state, at}`. `authority ∈ AUTHORITY_TIERS` (ordenado:
   `untrusted < active_memory < worker < overseer < signed_policy`); `state ∈
   {candidate, validated, active, challenged, expired, revoked}`; `scopeTag` =
   lista de path globs de proveniência; `provenance` = actor record do SPEC-161
   (quem introduziu o item) OU `{source}` livre. Construtor com defaults seguros
   (state=candidate, authority=active_memory — o MENOR tier de memória viva).
2. **Firewall GM-3 (puro, o invariante de poisoning).** `firewall_verdict(item,
   policy_authority) -> (admit: bool, reason)`: admit=False sse
   `tier_rank(item.authority) >= tier_rank(policy_authority)` — memória
   recuperada NUNCA adquire autoridade ≥ política. Determinístico, sem estado.
   Um item `revoked`/`expired` também é negado (state gate), com reason distinta.
   **FAIL-CLOSED em tier não-reconhecido** (item OU política): uma authority
   inválida/corrompida é NEGADA com reason `authority-invalid`, NUNCA tratada
   como o tier mais fraco e admitida (2026-07-21 reckon reproduziu o bypass em
   toda política) — um firewall anti-poisoning falha fechado. `make_item`
   sanitiza na construção, mas o firewall é a função que um retrieval futuro
   chama com linhas CARREGADAS/à-mão, então ela mesma falha fechado.
3. **Scope-match (challenge-trigger, não delete).** `scope_challenged(item,
   changed_paths) -> bool`: True sse algum glob de `scopeTag` casa algum path de
   `changed_paths` (o `git diff --name-only`). Um True marca o item como
   CANDIDATO a `challenged` (re-validação), NUNCA a exclusão — challenge ≠
   delete (invariante do artigo).
4. **Shadow measure (measure-before-enforce, à la EXP-18/SPEC-159).** `shadow_scan
   (registry, policy_authority, changed_paths) -> dict`: sobre um registro,
   conta `admitted`, `wouldRefuse` (split em `refuseByAuthority`, `refuseByState`,
   `refuseByInvalid`), e `wouldChallenge` (scope-match), SEM mudar estado nem
   recusar nada. `refuseByInvalid` é um SINAL DISTINTO de risco de poisoning que
   o owner lê antes de habilitar enforcement — a linha de authority inválida
   NUNCA é contada como `admitted` (a medição tem que EXPOR essa classe, não
   escondê-la). Fail-open: linha corrompida (chaves faltando) → `malformed`,
   nunca levanta.
5. **Sem enforcement, sem retrieval.** Este spec não cria caminho de retrieval,
   não filtra nenhuma leitura de memória real, não muda `ui_memory`. O único
   consumidor de `firewall_verdict`/`scope_challenged` é o shadow_scan e o
   cenário. O enforcement de retrieval é um follow-up owner-gated (N6).
6. **Aditivo/isolado.** Módulo novo + cenário novo; nenhum leitor existente
   muda. A tríade de segurança (C4 firewall + C5 sensitivity + C8 eval) tem aqui
   só o C4; C5/C8 seguem como follow-ups declarados antes de qualquer trigger ir
   a shadow-real.

## Rationale & sources

| Decisão | Fontes |
|---|---|
| GM-5 bootstrap (registro + measure) ANTES do GM-3 enforcement | R3: "GM-5 é o 1º passo committável; enforcement owner-gated no N6"; measure-before-control (SPEC-159/EXP-18) |
| authority tiers alinhados ao actorType do SPEC-161 | um vocabulário de ator no harness inteiro (D013/D042); signed_policy > toda memória |
| challenge ≠ delete; scope-match | R3 emenda anti-over-expiry (sem ela GM-1/2 rejeitadas) |
| firewall é função PURA, não um gate ligado | o retrieval de itens governados não existe; ligar enforcement sem ele seria controle sem superfície |

## Ceilings (upgrade paths)

- `provenance`/assinatura: o `provenance` é DECLARADO (actor do SPEC-161), não
  assinado — mesmo teto do T-HASHCHAIN; o chainDigest do SPEC-161 é o gancho.
- C5 sensitivity gate + C8 adversarial eval (as outras 2 pernas da tríade) são
  follow-ups declarados; o shadow-scan mede o C4 isolado por enquanto.
- Enforcement de retrieval (recusar de fato uma leitura) liga no N6, owner-gated,
  quando existir um retrieval de memória governada para interceptar.

## Test strategy

- `gmf_memory_firewall.py`: record defaults + validação de vocabulário;
  firewall_verdict (admite authority < policy; nega ≥; nega revoked/expired com
  reason distinta; ordem dos tiers correta); scope_match (glob casa/não-casa,
  vazio); shadow_scan (contadores corretos sobre um registro misto, fail-open em
  item corrompido, ZERO mutação de estado). + self-check do módulo.
- Regression: nenhum cenário de memória existente muda (módulo isolado).

## Validation

- `python testing/scenarios/gmf_memory_firewall.py` green.
- `python scripts/harness_lib/governed_memory.py` self-check green.
- `spec-pack` green.
