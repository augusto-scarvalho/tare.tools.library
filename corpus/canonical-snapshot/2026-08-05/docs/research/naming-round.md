# Rodada de naming — batizar o harness/projeto

Owner 2026-07-19: "nosso harness ainda não tem nome. pesquisa ampla (ideadores NVIDIA + alguns
Sonnet 5 medium), suplementa com o projeto e os diferenciais, pede nomes+explicações, converge."
Orquestrador = esta sessão. Divergência cross-vendor (NVIDIA wide + Sonnet 5).

## O que o projeto É (seed pros ideadores)
Um **harness multi-agente agent-agnóstico, orientado a projeto** — um "sistema operacional para
engenharia agêntica". A camada canônica `.harness/` é dona do estado (tarefa/continuidade/routing/
handoff); os agentes (Claude, Codex, Gemini, NVIDIA) são só adapters. Deriva de um manuscrito de
referência ("adaptive project-oriented multi-agent harness architectures") — o manuscrito vira lei.

## Os DIFERENCIAIS (o DNA distintivo — o que o nome deve honrar)
1. **Measure-before-control:** nunca um controle sem a medição que o justifica. Probes measure-only,
   noise floors, experimentos pré-registrados. Rigor científico, não vibe.
2. **Anti-fabricação / honestidade de medida:** `—` pra gap, dropa métrica não-mensurável, JAMAIS
   inventa número. Um sistema que prefere dizer "não sei" a fingir.
3. **Trajetória à prova de adulteração:** event log hash-chained + DAG causal; provenance firewall;
   reconciliação de fontes da verdade (código/doc/histórico/vendor).
4. **Overseer-loop com ritual de review duro:** overseer planeja (footprint HARD), workers
   implementam, review obrigatório (footprint, gaming hunt, oracle-mutate, verify-before-dispatch).
5. **Disciplina de gate:** `validate --staged` (cenários + spec-pack) antes de toda integração.
6. **Consciência de custo:** economia de modelo (modelo barato pro fan-out), delegation ledger,
   função de utilidade U(rota, outcome, custo).
7. **Estética SIGNAL:** instrumento/mission-control — phosphor, medição, osciloscópio, rigor.

## Critérios de um bom nome
- **Evoca:** rigor/medição + orquestração/harness/controle + confiança/proveniência.
- **Distintivo e ownable:** curto, pronunciável, memorável; funciona como comando de CLI + namespace.
- **NÃO é AI-slop:** proibido sufixo -GPT/-AI, e clichês tipo Agent*/`*Flow`/`*Nexus`/`*Forge`/
  `Orchestr*`/`Synth*`. Nada genérico "on distribution".
- **Combina com SIGNAL:** cabe num instrumento de missão (phosphor/telemetria/medição).

## O ask (pra cada ideador)
Gere **10-15 candidatos**, cada um com: **nome** · **o que evoca** (1 linha) · **por que cabe NESTE
projeto** (liga a um diferencial acima) · **downside honesto** (colisão conhecida, ambiguidade,
dificuldade de pronúncia). Varie o registro (literal, metafórico, científico/instrumento,
mitológico/cultural, neologismo cunhado). Evite o óbvio; surpreenda.

## Ondas
- Onda A (NVIDIA, wide): 5 ideadores glm-5.2, research-divergence.
- Onda B (Sonnet 5 medium): 3 ideadores, perspectivas distintas (científico-instrumento,
  mitológico-cultural, neologismo-cunhado).

## Convergência (Fase 5)
Clusterizar os candidatos, pontuar por distinção × fit-ao-DNA × ownability, cortar colisões
óbvias, e convergir num shortlist + 1 recomendação com justificativa.

---

# Fase 5 — convergência (4 ondas: NVIDIA 5 + Sonnet 3)

## Frequência cross-wave (o que emergiu sozinho)
NVIDIA convergiu forte em: **Caliper 4x · Tare 4x · Nullpoint 4x · Ledger 4x · Plumb 2x ·
Metron 2x · Assay 2x**. Sonnet trouxe o cluster "padrão de referência": **Fiducial · Etalon ·
Datum · Timebase** (científico), **Lachesis · Gnomon · Escapement** (mitológico), e coinages
mais fracos (Probemark/Vergauge/Catenal).

## O meta-tema (o mais forte — apareceu nas 4 ondas)
**"O zero / o padrão de referência contra o qual tudo é medido antes de agir."** É o DNA:
measure-before-control (mede antes) + anti-fabricação (mede só o que é real) + reconciliação de
fontes da verdade (o padrão que reconcilia). Os melhores nomes ENCARNAM isso numa palavra.

## Shortlist (distinção × fit-ao-DNA × ownability)

| # | nome | o que encarna | por que é forte | downside honesto |
|---|---|---|---|---|
| **1** | **Tare** | zerar a balança pra descartar o peso do recipiente e medir SÓ o que é real | anti-fabricação + measure-first numa sílaba; CLI perfeito (`tare run`); distintivo, ownable, 0 AI-slop; 4 ideadores acharam sozinhos | obscuro (força de marca, tipo Vercel); homófono falado (tear/tar) — escrito é limpo; verificar disponibilidade |
| **2** | **Assay** | o ensaio que determina a composição REAL de uma amostra — ou reporta o gap | anti-fabricação literal (quantifica o real, nunca inventa); distintivo, baixa colisão, CLI limpo | palavra menos comum; verificar disponibilidade |
| **3** | **Caliper** | o paquímetro — medir com precisão antes de cortar | convergência MÁXIMA (4x NVIDIA); reconhecível, evocativo, CLI-clean | colisão: existe um padrão ed-tech "Caliper" + hardware; menos ownable |
| **4** | **Etalon** | o padrão Fabry-Pérot que TUDO calibra contra | encaixe quase exato na reconciliação de fontes da verdade; distintivo, colisão baixa | obscuro/pronúncia (é ativo pra marca também) |
| **5** | **Fiducial** | a marca de referência; do latim *fiducia* = "confiança" | etimologia LITERALMENTE nomeia proveniência/trust; distintivo | 3 sílabas, pronúncia (fi-DOO-shul); soa a jargão de estatística pra alguns |

Menções de caráter: **Gnomon** (a haste do relógio de sol = o probe que gera a leitura — curto,
distintivo, G-mudo); **Lachesis** (a Moira que mede o fio = measure-before-control personificado —
poético mas longo/pronúncia); **Datum** (curto mas lê como "singular de data").

## Recomendação do arquiteto
**TARE** — é o único que captura a alma do projeto (medir só o que é real, descartar o resto,
nunca fingir) em UMA sílaba, é um verbo/namespace de CLI perfeito, é genuinamente distintivo (não
"on distribution"), e emergiu de vários ideadores independentes. A obscuridade é ativo de marca.
Alternativas fortes: **Assay** (mais legível, mesmo DNA) e **Caliper** (a escolha segura/
reconhecível). Se o ângulo de reconciliação-de-fontes-da-verdade deve LIDERAR: **Etalon/Fiducial**.

## Próximo passo (antes de fechar)
Checar disponibilidade (domínio .dev/.io, npm/PyPI, GitHub org, trademark) dos 2-3 favoritos —
posso rodar essa verificação quando você apontar os que quer.
