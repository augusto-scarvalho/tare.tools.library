# tare.tools Research Corpus

> **THIS REPOSITORY IS EVIDENCE, NOT ARCHITECTURAL AUTHORITY.**

Este repositório preserva pesquisa, fontes, experimentos, arqueologia, propostas e versões históricas do tare.tools.

Em conflito, prevalecem o repositório canônico `tare-tools`, Git, código, arquitetura ratificada, ADRs, SPECs, BDDs e gates.

English overview: **[README.en.md](README.en.md)**.

## Comece aqui

- **[Índice unificado de todos os documentos e estudos](catalog/ALL_DOCUMENTS_INDEX.md)** — 11 originals de chat, 93 cópias exatas do snapshot privado e 60 referências File Library, com origem/authority explícitas.
- **[Índice dos originals de chat materializados](catalog/DOCUMENT_INDEX.md)** — navegação PT-BR | EN por documento e por tema.
- **[Baseline histórico do GitHub privado](canonical-references/baselines/private-github-main-2026-08-05/README.md)** — snapshot exato de 05/08, não CURRENT.
- **[Índice das pesquisas presentes no snapshot privado](catalog/CANONICAL_SNAPSHOT_RESEARCH_INDEX.md)** — 93 arquivos byte-for-byte de `docs/research/`.
- **[Fila de tradução EN do snapshot privado](catalog/CANONICAL_SNAPSHOT_TRANSLATION_QUEUE.md)** — sources não-EN materializados e elegíveis para tradução.
- **[Fila de reidratação](catalog/REHYDRATION_QUEUE.md)** — File Library refs ainda sem bytes locais; tradução fica bloqueada até materialização exata.
- **[Linhagens descobertas na File Library](catalog/LIBRARY_LINEAGES.md)** — projeção de descoberta.
- **[Reconciliação de linhagens](catalog/LINEAGE_RECONCILIATION.md)** — separa ordem por versão, siblings e duplicatas ainda não provadas.
- **[Expected identity assertions](catalog/IDENTITY_ASSERTIONS.md)** — hashes/tamanhos reportados por manifests independentes para future exact-byte verification.
- **[Índice normalizado de fontes](sources/SOURCE_INDEX.md)** — URLs extraídas deterministicamente dos originals materializados.
- **[Cobertura da reidratação](catalog/REHYDRATION_COVERAGE.md)** — baseline histórico vs. estado atual, sem somar identidades não reconciliadas.
- **[Catálogo mestre](catalog/MASTER_CATALOG.md)** — tabela completa com IDs, status, contextos, links e hashes.
- **[Status das traduções](catalog/TRANSLATION_STATUS.md)** — cobertura e estado de revisão das versões inglesas.
- **[Fila de tradução EN](catalog/TRANSLATION_QUEUE.md)** — somente sources já materializados que ainda aguardam derivação inglesa.
- **[QA das traduções](catalog/TRANSLATION_QA.md)** — checks estruturais de fidelidade e provenance.
- **[Workflow de tradução no chat](CHAT_TRANSLATION_WORKFLOW.md)** — contrato operacional para traduzir durante a revisão sem reconciliar arquitetura.
- **[Status da revisão](catalog/REVIEW_STATUS.md)** — separa revisão arquivística, tradução e reconciliation arquitetural.
- **[Translation Policy](TRANSLATION_POLICY.md)** — autoridade do original e regras de fidelidade.
- **[Cronologia](catalog/CHRONOLOGY.md)** — visão temporal.
- **[Famílias de versões](catalog/VERSION_FAMILIES.md)** — lineage conhecido/pendente.
- **[Research Graph](catalog/RESEARCH_GRAPH.json)** — relações estruturadas.
- **[Coverage](catalog/COVERAGE.md)** — cobertura do corpus.

### Seed atual

Foram materializados **11 documentos** do corpus de chat nesta árvore. O baseline histórico privado acrescenta **93 cópias exatas de `docs/research/`**, mantidas em um namespace separado para não confundir origem. Veja [`ALL_DOCUMENTS_INDEX.md`](catalog/ALL_DOCUMENTS_INDEX.md).

No corpus principal, foram materializados **11 documentos** nesta árvore. Os originals PT-BR ficam em `corpus/original/`; versões EN derivadas ficam em `corpus/translations/en/`. Tradução EN disponível: **11/11**. Há **60 referências File Library** registradas; **60** ainda aguardam materialização exata, sem reconstrução a partir de snippets.

## Status permitidos

- `RESEARCH` — evidência, hipótese, revisão, investigação.
- `PROPOSED` — proposta ainda não ratificada.
- `HISTORICAL` — preservação/arqueologia.
- `EXPERIMENTAL` — resultado experimental ainda não promovido.

`TARGET` não deve nascer aqui como autoridade. Um documento pode **referenciar** TARGET canônico, mas promoção é realizada no repositório canônico.

## Estrutura

- [`research/`](research/) — índices e pesquisas temáticas.
- `findings/` — sínteses ADOPT/ADAPT/RETIRE/OPEN.
- `proposals/` — propostas ainda não ratificadas.
- `experiments/` — protocolos e resultados.
- `archaeology/` — chats, sessões e evolução histórica.
- `sources/` — bibliografia e source manifests.
- [`corpus/original/`](corpus/original/) — bytes históricos PT-BR imutáveis.
- [`corpus/translations/en/`](corpus/translations/en/) — traduções inglesas derivadas.
- `corpus/normalized/` — versões processáveis derivadas.
- [`corpus/manifests/`](corpus/manifests/) — provenance sidecars.
- [`corpus/library-references/`](corpus/library-references/) — referências File Library de descoberta.
- [`catalog/identity-crosswalk/`](catalog/identity-crosswalk/) — vínculo entre uma referência e bytes exatos materializados, sem reescrever o registro de descoberta.
- [`catalog/`](catalog/) — índices, catálogos e grafo.
- `incoming/` — staging documental antes do roteamento.
- `schemas/` — contratos de metadata/publicação/tradução.
- `tools/` — automação determinística.

## Regra de autoridade

Research / experiment / archaeology / proposal **informam**, mas não ratificam arquitetura. Tradução não altera authority/status. Promoção para TARGET exige o fluxo canônico no repositório `tare-tools`.
