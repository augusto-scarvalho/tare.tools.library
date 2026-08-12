# tare.tools Research Corpus

> **ESTE REPOSITÓRIO É MEMÓRIA DE PESQUISA/EVIDÊNCIA, NÃO AUTORIDADE ARQUITETURAL.**

Em conflito, prevalecem o repositório canônico `tare-tools`, Git, código, arquitetura ratificada, ADRs, SPECs, BDDs e gates.

## Comece aqui

1. **[Scientific Refresh 2026-08-11](refresh-editions/2026-08-11/README.md)** — superfície compacta de leitura do corpus histórico: 93 artefatos reconciliados em 9 linhagens, com scientific refresh e implementation-research deltas.
2. **[Research Frontier](frontier/README.md)** — continuidade de perguntas de pesquisa; não é backlog nem autoridade de implementação.
3. **[Índice de documentos](catalog/DOCUMENT_INDEX.md)** e **[catálogo mestre](catalog/MASTER_CATALOG.md)** — navegação e identidade documental.
4. **[Canonical Snapshot Research Index](catalog/CANONICAL_SNAPSHOT_RESEARCH_INDEX.md)** — índice dos bytes históricos preservados do snapshot de 2026-08-05.
5. **[Research lineage & influence](catalog/RESEARCH_LINEAGE_AND_INFLUENCE.md)** — relações entre pesquisas e linhagens.

## Três classes que não devem ser confundidas

### 1. Evidence / originals — append-only

Bytes primários e históricos permanecem preservados. Em especial:

- `corpus/original/`
- `corpus/canonical-snapshot/`
- `corpus/source-bundles/`
- `corpus/manifests/`
- `canonical-references/`

Esses artefatos não são reescritos ou apagados para deixar o corpus mais limpo.

### 2. Research synthesis / refresh — tracked

Sínteses, revisões científicas e deltas técnicos continuam versionados quando carregam interpretação, reconciliation, decisões `ADOPT / ADAPT / RETIRE / OPEN`, provenance ou novos findings.

A principal superfície histórica consolidada é `refresh-editions/2026-08-11/`.

### 3. Presentation projections — reconstructible

HTMLs editoriais que apenas reformatam ou traduzem bytes já preservados são **build artifacts reconstruíveis**. Eles podem ser gerados localmente pelas ferramentas do repositório, mas não precisam permanecer commitados na árvore viva.

A antiga árvore `editorial-editions/2026-08-05-private-github-snapshot/` foi retirada da branch de compactação por esse motivo. Seus bytes continuam recuperáveis no histórico Git; o padrão editorial e o relatório de gaps foram preservados junto ao Scientific Refresh.

## Estrutura operacional

- `research/` — índices/projeções temáticas.
- `refresh-editions/` — pesquisas consolidadas e refreshes científicos.
- `findings/` — sínteses e findings.
- `proposals/` — propostas ainda não ratificadas.
- `experiments/` — protocolos e resultados.
- `archaeology/` — chats, sessões e evolução histórica.
- `sources/` — bibliografia e source manifests.
- `corpus/` — evidence, originals, snapshots, translations e manifests.
- `frontier/` — Research Pointers e continuidade científica.
- `catalog/` — identidade, lineage, índices, provenance e maintenance records.
- `incoming/` — staging documental antes do roteamento.
- `schemas/`, `tools/`, `tests/` — contratos e automação determinística.

## Regra de autoridade

`RESEARCH`, `EXPERIMENTAL`, `HISTORICAL` e `PROPOSED` informam; não ratificam arquitetura. `TARGET` e `CURRENT` pertencem ao fluxo canônico do `tare-tools` e à evidence correspondente.

## Compactação

A política aplicada em 2026-08-12 é **negative archive para derivatives, append-only para evidence**: não duplicar arquivos em `/archive`; usar Git para recuperar projections retiradas e manter live somente evidence irreversível, research com valor semântico e machinery necessária para reconstrução.

Veja [`catalog/CORPUS_COMPACTION_2026-08-12.md`](catalog/CORPUS_COMPACTION_2026-08-12.md).
