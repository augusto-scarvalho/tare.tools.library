# Weekly monitor W28 (comunicação multi-agêntica) — extrato para o harness

Fonte: digest semanal GPT fornecido pelo dono (2026-07-13). NÃO é uma rodada
de research; citações são `[web]` não-verificadas — ideias avaliadas pelo
mérito interno contra o estado real do harness. Terceiro da série
(`weekly-monitor-w28-memory-extract.md`,
`weekly-monitor-w28-code-quality-extract.md`); numeração continua
(EXP-7..8).

## Onde o harness JÁ cobre o digest (sem trabalho novo)

| Achado do digest | Equivalente já operante aqui |
|---|---|
| #1 Shared Selective Persistent Memory (Apple) | MESMO paper já mapeado no extrato de memória (achado #1 lá): specs/ = task specifications, schemas/ = data schemas, .harness/routing + capabilities.json = tool configurations, subagent-contract + schema WORKER_RESULT = output constraints; traces de sessão deliberadamente NÃO promovidos (checkpoint é bounded). Os 5 namespaces sugeridos já existem com outros nomes |
| LDT-Coord ("LLM propõe; runtime coordena") | É a tese da arquitetura: workers devolvem WORKER_RESULT tipado, reduce é determinístico, plan briefs declaram footprint HARD e o overseer impõe disjunção para paralelizar. O que resta manual é a checagem de disjunção → EXP-7 |
| AutoWorldBuilder (localidade semântica na montagem de contexto) | Packets embutem só spec/constraints da tarefa; requiredReads com demotion por budget; context-digest por workflow. O que NUNCA medimos é a utilização real do contexto enviado → EXP-8 |
| ARCANA (blackboard estruturado) | O diretório do workflow (workers/, reduce/, trace.jsonl, seed-context.md) É o blackboard: artefatos compartilhados tipados, não diálogo. Meta-controller aprendido = fora do perfil (sem treino próprio) |
| GRACE (deltas verificados localmente em vez de revalidar o monólito) | Parcial: o pack de instruções é validado por gates determinísticos baratos (spec-pack em segundos) — a dor que o GRACE resolve (revalidação LLM de prompt monolítico) não existe aqui. A parte aproveitável (referências cruzadas de arquivos de instrução) vira rider do EXP-4, não experimento novo |

## Experimentos extraídos (reversíveis; template do research-playbook)

### EXP-7 — Pre-flight de conflito de footprint (LDT-Coord-inspired) · prioridade ALTA, minúscula
- **Hipótese**: a única etapa de coordenação do loop paralelo ainda feita
  de cabeça é a disjunção de footprints entre briefs simultâneos; um erro
  meu aqui é exatamente a classe "paralelização ferrando algo" que o dono
  vetou. Mecanizar custa quase nada: `parse_footprint` já existe
  (`overseer_review.py:50`).
- **Fase única**: `review --plans <briefA> <briefB> [...]` — interseção de
  footprints entre todos os pares; qualquer path em comum → WARN com o par
  conflitante. Advisory rc 0 (o overseer decide). Mesmo seam do
  `--preflight` do EXP-6 — se ambos graduarem, é um modo só.
- **Baseline/métrica**: rodar contra os 12+ briefs históricos de
  2026-07-13 em pares reais lançados juntos — esperado 0 conflitos (as
  ondas foram planejadas disjuntas); qualquer >0 é bug retroativo achado.
- **Reversão**: flag advisory num verbo já existente.

### EXP-8 — Auditoria de localidade semântica (AutoWorldBuilder-inspired) · prioridade MÉDIA/ALTA
- **Hipótese**: parte relevante do contexto embutido nos packets nunca é
  citada pelo worker — pagamos tokens de montagem sem retorno. O digest
  chama de "semantic locality"; nós nunca medimos (o token-audit mede
  CUSTO do que foi enviado, não USO).
- **Baseline**: os pares já retidos em disco por workflow —
  `workers/worker-NNN.prompt.md` (arquivos/seções embutidos) vs
  `worker-NNN.result.json` (`sourceFilesVerified` + `itemsAnalyzed`).
  Probe determinístico, zero LLM, só artefatos existentes.
- **Métrica**: % de arquivos/seções embutidos jamais citados, por perfil
  de worker e por workflow; distribuição, não média (um research worker
  legitimamente cita menos).
- **Fase 2 (só se o desperdício for grosso)**: política de montagem por
  workstream (o packet ganha só o subconjunto do escopo declarado) — mas
  isso é mudança de comportamento, decidida com o número na mão.
- **Reversão**: fase 1 é read-only; fase 2 seria config de montagem
  revertível.

## Estacionados (com gatilho explícito)

- **KV-PRM (verificação via KV cache)**: exige acesso ao serving; somos
  multi-vendor de API fechada. Gatilho = lane de serving próprio com open
  weights. O digest mesmo aponta a inaplicabilidade direta.
- **GRACE como grafo tipado de instruções**: gatilho = a validação do pack
  de instruções ficar cara ou virar LLM; hoje o pack determinístico roda em
  segundos — verificação por vizinhança resolveria um custo que não pagamos.
  Rider imediato: arquivos de instrução (.harness/context, prompts,
  playbooks) entram no inventário declarado-vs-real do EXP-4 como classe de
  par (paths/comandos citados existem).
- **ARCANA (blackboard diferenciável + meta-controller aprendido)**:
  gatilho = fase de aprendizado do harness (família SELF_EVOLUTION I4,
  Deferred) — mesmo balde do reward de retenção do extrato de memória.
- **Revisão MCP de 2026-07-28** (núcleo stateless, capability discovery,
  multi round-trip): data conhecida — checar impacto nos nossos usos de MCP
  quando sair; nada a fazer antes.

## Veredito crítico do digest

A tese da semana — "não transportar conversas; transportar memória
selecionada, deltas estruturados, constraints e referências a estado já
computado" — é literalmente a arquitetura em produção aqui: packets +
WORKER_RESULT tipado + canon versionado em git + reduce determinístico. Dos
seis papers, quatro confirmam decisões já tomadas (um deles repetido do
digest de memória). O aproveitável genuíno são duas medições: EXP-7
mecaniza a última checagem manual da coordenação paralela (custo ~zero,
parser pronto), e EXP-8 mede a localidade semântica que sempre presumimos
e nunca contamos — com os artefatos que já retemos por workflow. Nenhum
protocolo novo na janela; nada justifica grafo de instruções ou KV sharing
antes desses números existirem.
