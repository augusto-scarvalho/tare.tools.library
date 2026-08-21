# Proposta — o "crachá" de aprovação (acceptanceAuthority / cadeia de responsabilidade)

Deliverable do item #2 (owner: "faça propostas ou pesquise e me mostre que eu
fecho com você"). Base: D013 (owner 2026-07-18) — a autoridade depende de QUEM
aceitou (user | worker | overseer), com auto-consistência + padronização pra
seguir a cadeia de responsabilidade + data. **Você escolhe uma opção (ou mistura)
e eu implemento.**

## O que já temos no repo (não reinventar)
- **subject dimension** (`records.add_entry(subject=)`, `append_event(subject=)`):
  todo registro já é atribuível a `self` | nome-de-target. É metade do "quem".
- **C12 approval digest** (`plan_gate.planSha256`, `decision_inbox.apply_decision`
  `expected_digest`): aprovação já pode LIGAR num sha do artefato (TOCTOU fechado).
- **T-HASHCHAIN** (recém-shipado): eventos críticos já são tamper-evident por
  hash-chain — uma aprovação registrada nesse caminho já é à prova de reordenação.
- **decision_inbox / escalations**: já gravam `decidedAt`, `choice`, `note`.

Falta: um **tipo de ator** consistente + a CADEIA (proposer→reviewer→accepter),
não só um nome solto.

## Padrões de referência (o que o mundo faz)
| padrão | ideia | o que pegamos |
|---|---|---|
| git author/committer/Signed-off-by | 3 papéis numa mudança (quem escreveu, quem aplicou, quem atesta) | a ideia de MÚLTIPLOS papéis num evento, não um nome |
| W3C PROV (`wasAttributedTo`/`wasAssociatedWith`) | Agent × Activity × Entity com papéis tipados | vocabulário de ator+papel+atividade |
| in-toto / SLSA provenance | link metadata assinado: quem fez qual passo, em ordem | cadeia ordenada + binding assinado (opcional) |
| RBAC/ABAC + separation-of-duties | proposer ≠ approver; two-person control | o artigo §7.7 R2/R3 já pede isso; a cadeia torna executável |

## Proposta A — "crachá simples" (registro tipado único) · MENOR
Um campo tipado no ponto de aceite:
```json
"acceptanceAuthority": {
  "actorType": "user | worker | overseer",
  "identity": "augusto | worker:aXXXX | overseer:session_01Y8...",
  "at": "2026-07-19T...",
  "method": "cli-decide | ui-approve | auto-owner-gate"
}
```
- Reusa subject + o `decidedAt`. Aditivo. 1 helper `stamp_authority(actorType,
  identity, method)` chamado nos pontos de aceite (decide inbox, owner-gate,
  risk-accept do C2).
- **Prós:** barato, fecha D013 no essencial. **Contras:** não modela a CADEIA
  (proposer→approver) — só o último a aceitar.

## Proposta B — "cadeia de responsabilidade" (lista ordenada de papéis) · RECOMENDADA
O aceite carrega a CADEIA de quem participou, tipada por papel:
```json
"responsibilityChain": [
  {"role": "proposer", "actorType": "worker",   "identity": "worker:a78e...", "at": "..."},
  {"role": "reviewer", "actorType": "overseer",  "identity": "overseer:sess...", "at": "..."},
  {"role": "accepter", "actorType": "user",       "identity": "augusto",         "at": "..."}
]
```
- Torna EXECUTÁVEL o separation-of-duties do §7.7: um check determinístico
  `proposer.identity != accepter.identity` (Rule of Two / two-person control).
- Cada entrada reusa o subject/actorType. O C2 risk-register (D013) grava a
  cadeia inteira como `acceptanceAuthority`. O digest C12 pode ligar no sha da
  cadeia.
- **Prós:** responde "quem decidiu o quê e quando" completo; destrava R2/R3;
  base natural pro N-SECREVIEWER (D014 — o reviewer é um papel na cadeia).
  **Contras:** um pouco mais de plumbing (gravar a cadeia nos pontos multi-parte).

## Proposta C — "cadeia assinada" (B + tamper-evidence) · MAIS FORTE
Proposta B + binding de integridade: a `responsibilityChain` entra no
hash-chain do T-HASHCHAIN (é evento crítico) OU ganha um `chainDigest =
sha256(chain canônica)` no estilo C12.
- **Prós:** a cadeia de responsabilidade fica à prova de adulteração — ninguém
  reescreve "quem aprovou" sem quebrar a evidência. Fecha o §7.1 o3
  (candidate_proposed → nunca a mesma identidade aprova) de forma verificável.
  **Contras:** o teto do T-HASHCHAIN (sem assinatura real) vale aqui também;
  assinatura de verdade fica atrás do gatilho de infra-de-chave.

## Minha recomendação (arquiteto)
**Proposta B agora, com o gancho da C pronto.** A cadeia é o que o D013 realmente
pede ("entender a cadeia de responsabilidade") e destrava o separation-of-duties
executável + o papel de security-reviewer (D014) de graça. O binding assinado (C)
é um `chainDigest` aditivo que ligamos quando/se o gatilho de integridade chegar
— não custa nada deixar o campo reservado. A Proposta A é o fallback se você
quiser o mínimo absoluto.

**Onde entra no código (se for B):**
- Novo `harness_lib/responsibility.py`: o record tipado + `stamp(role, actorType,
  identity)` + `verify_separation(chain)` (proposer≠accepter, determinístico).
- Pontos de aceite: decide_inbox `apply_decision`, os owner-gates, o C2
  risk-register (`acceptanceAuthority` = a cadeia).
- Spec: door NEW SPEC-116 (responsibility-chain) + Gherkin.
- Cenário: cadeia válida grava; proposer==accepter → separation FAIL (advisory).

## Pergunta pra você fechar
1. **A, B ou C?** (recomendo B com o gancho de C.)
2. Os `actorType` são exatamente `user | worker | overseer`, ou você quer um 4º
   (ex.: `automation` pro auto-owner-gate, `external` pra um humano de fora)?
3. `identity` do user = seu handle (`augusto`)? do worker = o agentId? do
   overseer = a session ref? (proposta: sim aos três.)
