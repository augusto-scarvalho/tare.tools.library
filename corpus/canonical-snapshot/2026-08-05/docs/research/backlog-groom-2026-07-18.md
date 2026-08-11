# Backlog groom — fila de intake, 2026-07-18

Rodada report-only executada por worker Sonnet (playbook
`.harness/prompts/backlog-groom-playbook.md`), auditada e aplicada pelo
overseer com digest binding (`apply_decision --expected-digest` por linha;
`allow_expired` para as 2 SLO-breached). 125 asks pendentes → **123 decididos,
2 mantidos pendentes** (verificação ao vivo antes de decidir). Spot-check de
auditoria: 8/8 shas de evidência "done" conferidos no git log antes do batch.

## Clusters (12) e padrão de decisão

| Cluster | N | Decisão dominante |
|---|---|---|
| A. Packets de execução colados como ask | 15 | discard (instrução, não feature) |
| B. Diretrizes de modelo/custo | 6 | discard (codificadas em CLAUDE.md) |
| C. Bugs/pedidos GUI chat/rooms | 22 | ~12 done · 5 backlog · restante discard |
| D. IDE-mode / design system | 10 | done (SPEC-147 + fase 1 ce1dc54) |
| E. UX página de experimentos | 9 | done (2f056bb, 1c4b091, 51e9686) |
| F. Sandbox/isolamento | 7 | done (SPEC-148 hoje) |
| G. Pings automáticos gov:flake-reopen | 4 | discard (artefato de tracker, não ask) |
| H. Loop do artigo / EXPs | 12 | done (LOOP QUEUE 4 + EXP-15/16/17/18) |
| I. Achados hooks/parity/graph | 8 | 3 done · 4 backlog/spec · 1 discard |
| J. Meta de backlog/arquitetura | 8 | 2 backlog · resto discard |
| K. Q&A puro | 12 | discard (respondido inline) |
| L. Smoke tests de render/append | 4 | discard |

## Promovidos (backlog/spec) — os que valem atenção

1. **SPEC candidato — codex hook-trust + write-enforcement gap** (d77116ead917):
   achado de segurança verificado experimentalmente, ainda sem fix (a contenção
   real hoje é SPEC-148 + S3; isto é a perna de hooks).
2. `agents pair --apply` perde campos não-rastreados (timeout/statusMessage) —
   bug de data-loss no sync (46afc2ccdca3).
3. Unificação do backlog (JSON/MD duais → sqlite?) — dívida estrutural
   apontada pelo owner (1a45713b7104).
4. Stop button GUI + Esc-Esc CLI + bug streaming-não-para (d303a18496c1 +
   01983640330b; duplicata 806964ccefab descartada).
5. Drag-drop/upload no compose do chat (a06ba0abcc30).
6. codex app-server como transporte default + approvals interativos
   (e86672c43942); issue upstream unified_diff (3f2eeb5a6b2a).
7. Enforcement real de graph-navigation p/ workers + audit de grep do codex
   (bc19d9361c04, af2eb9143447).
8. Indicador de latência/vida do porteiro (9ebfa6c638b9 — reclamação recorrente).

## Pendentes deliberados (verificar ao vivo antes de decidir)

- 11d53f79b03e — jobs agendados órfãos sem remoção pela UI (pode já estar fixo).
- c1eb5b0da00c — anexo de screenshot renderizando estranho (idem).

## Errata honesta

- O overseer trocou dois ids no batch: 9619f9bed62b (Q&A, deveria ser discard)
  recebeu `backlog`; corrigido no alvo certo (9ebfa6c638b9 → backlog). O
  journal da fila carrega ambos os registros; dano: um Q&A a mais no bucket
  backlog.
- Miner-precision guard aplicado: apenas "done" com sha verificável; 8/8
  amostrados conferiram.
