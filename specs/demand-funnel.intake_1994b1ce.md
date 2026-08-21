# Intake refinement — demand-funnel: um funil, uma porta de commit

<!-- SPEC-116 door NEW checklist (specs/templates/intake-refinement.md).
     Consolida o fio de 2026-07-30 18:31–18:43 (intake ids bc90258f56d2,
     3a52ace24abc, 1c76fd571125, 6c6842a71a3e — a última é a entry mestre). -->

## Request (verbatim)

> outra coisa que me preocupa aqui é que nem tudo parece estar entrando pelo
> mesmo funil de demandas. algumas seções nascem com o overseer fazendo tudo
> certinho e criando a demanda e resolvendo ela no backlog / intake, outras ele
> só comita solto, sem nada. aproveita e já reveja tudo isso junto. tá meio
> zoado. principalmente quando estamos pegando o opus 5 de overseer

Fio anterior (mesma demanda, mesma tarde): "não seria o caso de disponibilizar
tools padrão para que os agentes não trunquem essa parte?" e "e se a gente não
permitir que o agente use o git commit e só permita usando nossas tools de
commit? porque tá parecendo que não tem padrão, cada agente tá fazendo de um
jeito". Gatilho concreto: o R8 boundary-clear disparou no pre-commit de
1d3ad53 e o agente o descartou com `git commit | tail -5` — o sinal viajava só
no stdout truncável.

## Covered-check (which door?)

| Query | Command | Outcome (hit / no hit) |
|---|---|---|
| records search | `harness.py records search commit door funnel intake enforcement` | `[]` — no hit |
| doc-find | `harness.py doc-find commit verb deny funnel demand intake decide` | só a maquinaria existente (route_loop, decision_inbox, iq_intake_queue) — nenhuma spec cobre porta de commit ou amarração intake→entrega |

Decision: **NEW**.

## Goal

Toda demanda entra, é decidida e fecha pelo MESMO funil — e todo commit de
agente sai pela MESMA porta, que carrega proveniência da demanda e entrega os
sinais de fronteira por canal que um pipe não trunca.

## Evidência medida (2026-07-30)

- Boca do funil OK: 191/200 entries do intake-queue vêm do prompt-hook —
  captura automática funciona.
- Meio quebrado: **121/200 pending** (mais antigo 2026-07-23); 73 discard,
  6 backlog, 0 spec via verbo. Ninguém roda `intake decide` no fluxo normal.
- Saída desamarrada: trabalho inline fecha por checkpoint+commit e a entry
  fica pending para sempre (ex.: dock-fold entregue em 1d3ad53, entry
  cc36ddb022ff seguia pending; accept-hooks entregue em 1ef9de6/9af9e10,
  entries c82f0075e053/6d5fd0d39954 idem).
- Sinal truncável: delivery-bar/R8 imprime no stdout do `git commit`; um
  `| tail -5` o engoliu em sessão real. Advisory que depende do agente
  repassar não é enforcement (a lição já mecanizada em 1838ac0, faltando
  esta perna).
- Dois funis de fato: SPEC-173 entrou certinho (intake doc → backlog row →
  fases → row closed); TODO o trabalho owner-demand da mesma semana (accept,
  fuel, gui, dock) commitou solto — 14 commits em 07-30 contra 2 rows
  fechadas. Com Opus 5 de overseer, regra de prosa degrada mais rápido.

## Scope

In scope:
- Verbo `harness.py commit` (porta única): recusa sem `verify-status`
  readyToCommit; valida `Tie:`; registra proveniência da demanda; persiste as
  advisories da delivery-bar em `.harness/state/` além de imprimir.
- PreToolUse deny de `git commit` cru em contexto de agente (molde
  deny_hitl_flags), com tratamento explícito de `--amend`/`merge --continue`/
  `cherry-pick --continue` e escape deliberado documentado.
- PostToolUse (leg Claude) que reentrega advisories não-consumidas como hook
  feedback — canal intruncável; perna codex registrada em
  `.harness/capabilities.json` como gap contratual se não-implementável.
- Amarração do fechamento: fechar item (checkpoint done / closes-backlog /
  tasks close) decide a entry de intake correspondente; a porta de commit
  pede/registra o id da demanda (intake id, task id ou owner-direct).
- Penteada no estoque: triagem dos 121 pending (backlog-groom) + vocabulário
  para prompt conversacional não apodrecer como pending.

Out of scope:
- Mudar a captura (prompt-hook) — funciona.
- Workflow/route mechanics (SPEC-144) — o funil usa, não reescreve.
- Commits do dono humano fora do Bash tool (hooks de agente não o gateiam).

## Actors & surfaces

- Actors: overseer (qualquer modelo — o alvo é Opus 5 aguentar sem disciplina
  de prosa), workers (que hoje nem deviam commitar), o dono (via `!`, fora do
  gate), hooks PreToolUse/PostToolUse, CLI harness.
- Surfaces: CLI (`harness.py commit`, `intake`), hooks (tools/hooks/*,
  `.claude/settings.json`), estado (`.harness/state/`). UI surface? **no** →
  Gherkin opcional.

## Proposed acceptance criteria

- [ ] `harness.py commit` recusa quando `verify-status` não está
      readyToCommit e quando a mensagem não valida `Tie:` — e o motivo da
      recusa nomeia o passo faltante.
- [ ] `git commit` cru pelo Bash tool de agente é negado com mensagem
      apontando a porta; `--amend`/`--continue` têm caminho definido; o deny
      tem self-check no molde dos hooks existentes.
- [ ] As advisories da delivery-bar persistem com o hash do commit; um
      PostToolUse as reentrega como hook feedback enquanto não consumidas —
      teste: commit com stdout totalmente descartado ainda faz o R8 chegar à
      conversa.
- [ ] Fechar um item por qualquer via (checkpoint done, closes-backlog,
      tasks close) resolve a entry de intake correspondente; uma entry de
      trabalho entregue não permanece pending após o commit de fechamento.
- [ ] A porta de commit grava proveniência (intake id / task id /
      owner-direct) consultável depois (records ou store).
- [ ] O estoque de pending volta a zero na penteada inicial e o queue
      distingue demanda de conversa (novo status ou expiração) — cenário
      iq_intake_queue estendido pina o vocabulário.
- [ ] Perna codex: deny/reentrega equivalentes OU gap registrado em
      capabilities.json — o cenário de paridade de vendor falha se nenhum dos
      dois existir.

## Risks / blast radius

Caminho de commit de TODAS as sessões futuras: um deny com regex frouxa
bloqueia trabalho legítimo (falso positivo em `git commit` dentro de string,
lição documentada no próprio deny_hitl_flags sobre segmentar comandos);
fail-open obrigatório nos hooks novos (advisory nunca vira block por
acidente). O verbo não pode reimplementar o ritual — compõe verify-status/
gate existentes, senão vira segunda fonte de verdade. Rollback barato: deny é
um hook removível; o verbo é aditivo.

## Open questions for the human

- Vocabulário do intake para entrega inline: novo status (`shipped`?) ou
  `discard --note` com o hash? (hoje só spec|backlog|discard|experiment)
- O deny vale para worker lanes também (mecanizando "worker não commita")?
- Pending conversacional: expira sozinho (prazo?) ou exige decisão humana?
