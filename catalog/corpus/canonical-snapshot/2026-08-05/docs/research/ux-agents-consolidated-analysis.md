# Parecer: relatório consolidado UX-agentes (2026-07-13)

Fonte: `docs/research/ux-agents-consolidated-2026-07-13.md` (relatório GPT
consolidado fornecido pelo dono, ~230KB — dois dossiês + atualização
06–13/07). NÃO é rodada de research (ordem do dono); citações `[web]`
não-verificadas. Quinto documento da série W28, mas de natureza DIFERENTE:
os quatro digests eram achados operacionais; este é o **blueprint de
produto de uma fase futura** (fábrica de UX guiada por referências para
polir SaaS vibe-coded).

## Avaliação do relatório em si

Qualidade acima dos digests: convenção epistemológica explícita (F/C/I/H/S/P),
critério de abandono em toda proposta, red team + premortem, e uma seção
"o que eu NÃO construiria primeiro" que coincide ponto a ponto com nossa
disciplina (sem crawler em massa, sem fine-tuning próprio, sem score
universal de beleza, sem agente publicando direto, "multiagente com papéis
decorativos" vetado). Os padrões dele são os do nosso research-playbook —
dá para consumir as fichas de proposta quase como plan briefs.

## A distinção que organiza tudo

O grosso do relatório (Compilador de Inspiração, Reference IR, firewall de
originalidade, captura segura de sites, modelo de gosto, renovador
autônomo) pressupõe um harness operando SOBRE alvos de UI externos — a
família **target-worker-world, que é OWNER-GATED**. Nada disso é backlog
de hoje; é o manual da fase quando o dono abri-la. O parecer separa três
baldes:

### 1. Já operante no harness de hoje (superfície interna)

| Proposta do relatório | Equivalente vivo |
|---|---|
| Dual-Audience CLI Contract (P1 dele) | É o house style: `--json`, exit codes documentados, `catalog`, superfície congelada, `common.emit`, goldens de `--help` no cenário cli_registry, `--validate-only` em curadoria. A "alternativa simples" que ele oferece como fallback é o que já fazemos por inteiro |
| UI Constitution + golden tasks (P0 dele), na escala do nosso painel | SPEC-134 ui_specs + fluxos ui_e2e (27/27) + qol_panel_chat (12 checks) — arena dourada em miniatura para a única UI que operamos |
| "Visual diff precisa de semântica, pixel diff é ruído" (WUICC) | Nunca construímos pixel diff — os e2e são DOM/assertion-based. Acerto por parcimônia, agora com literatura |
| Diversidade antes de convergência (fixação CHI 2024) | A metodologia dos rounds: onda de divergência (Gemini barato) → onda de crítica (NVIDIA), exatamente como no round de heurísticas de Nielsen |
| Gates funcionais têm precedência sobre estética; segurança não-compensável como restrição | Doutrina dos nossos gates + a decisão pendente do dono sobre security-baseline |
| Convenção F/C/I/H/S/P | Nossos packets de research já exigem classe de confiança honesta; adotar os rótulos nos docs de extract custa zero — adotado deste doc em diante |

### 2. Converge com a fila/decisões existentes (reforço, não item novo)

- **Workflow-level jailbreak (816/816 composto de etapas benignas)** →
  evidência nova para a decisão OWNER-GATED de expandir o security-baseline
  (mesmo balde do SecureVibeBench no extrato de qualidade). Não abre
  experimento: alimenta a decisão do dono.
- **Prismata (trust labels, downgrade-only, lineage tainted)** → nossa
  postura já é deny-by-default (GLM toolless, trustTier third-party,
  allowedWritePaths, seed contexts marcados `untrusted-derived`); o elo
  onde conteúdo não-confiável vira estado acionável é exatamente o que o
  **EXP-3 (quarantined no promote)** cobre. Reforça EXP-3; o trust lattice
  formal fica para a fase de captura de referências externas.
- **VoI Agent Router (ele mesmo rota como "Pesquisa", E4, risco 5)** → é o
  Oracle Action Router que estacionamos DUAS vezes (qualidade e workflows
  dinâmicos). Três documentos independentes, mesma conclusão: sem
  histórico calibrado, não. A "alternativa simples" dele (matriz
  determinística por tipo/risco) é o que já operamos via task-profiles.
- **UI2App/screenshot-não-é-spec** → irrelevante para hoje (não geramos UI
  de referência), mas grava um princípio para a fase futura: referência de
  app entra como conjunto coerente de estados, nunca imagem solta.

### 3. Blueprint da fase futura (nenhuma ação agora)

Os P0 dele para a fábrica de UX — UI Contract, design system executável,
captura isolada, malha multi-oráculo, arena dourada — mais os três
endurecimentos da atualização de 13/07 (Journey Graph para estado
cross-page, trust labels downgrade-only, segurança por trajetória). Quando
o dono abrir a fase target/UX, este relatório + este parecer são o ponto
de partida da triagem; os experimentos U1–U5 e E0–E8 dele já vêm com
baseline/métrica/abandono no nosso formato.

## O que NÃO extraí como experimento — e por quê

Zero EXPs novos deste relatório. Todo candidato barato ou já está na fila
(EXP-3, decisão de segurança, router estacionado) ou pertence à fase
OWNER-GATED. Extrair "experimentos de UX factory" agora violaria a regra
que os quatro extratos seguiram: medir o que operamos, não construir para
um produto que ainda não foi autorizado. O valor imediato do documento é
de referência e de convergência independente com decisões já tomadas.

## Veredito

O relatório é o melhor artefato da série e o menos acionável hoje — pela
razão certa: descreve a fase seguinte, não a atual. Recomendação: (a)
mantê-lo como blueprint canônico da fase UX-factory (entrada na fila de
intake aponta para cá); (b) usar o achado de jailbreak composto como
insumo quando o dono for decidir a expansão do security-baseline; (c)
adotar os rótulos F/C/I/H/S/P nos próximos docs de research; (d) nenhum
código novo por causa dele.
