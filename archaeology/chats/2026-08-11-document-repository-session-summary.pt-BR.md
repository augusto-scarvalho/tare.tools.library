## Rodada local concluída

Concluí **tudo que é possível concluir nesta superfície sem inventar evidência, sem acesso ao Git real do tare.tools e sem executar efeitos remotos no GitHub**.

O bootstrap está agora em **v0.9.0**, foi zipado, restaurado em uma árvore limpa e revalidado a partir do ZIP — ou seja, não estou considerando apenas a árvore de trabalho como prova.

**Checkpoint:** `cp-20260811T165725Z-eb8eafac6838`  
**Tree SHA-256:** `eb8eafac68382a65ff90dd60c9693161dabd5a44e4aa53ea831a95abe5a93f26`  
**ZIP SHA-256:** `2a20db3405417e196e3d47c6feda70a93220981f952dbc0111588b6c878ffdbe`  
**Arquivos na árvore:** 248

[**Baixar — tare.tools Document Repository Bootstrap LATEST v0.9.0**](sandbox:/mnt/data/tare-tools-document-repository-bootstrap-LATEST.zip)

[**Manifest LATEST**](sandbox:/mnt/data/tare-tools-document-repository-bootstrap-LATEST.json)

[**Attestation da restauração e revalidação do ZIP**](sandbox:/mnt/data/tare-tools-v0.9.0-restore-verification.json)

### O que ficou efetivamente pronto

Os **11 documentos materializados têm original preservado + tradução completa para inglês**, com hashes e provenance separados. O QA estrutural foi reexecutado sobre a árvore restaurada: **11/11 PASS**, incluindo estabilidade dos hashes. As versões inglesas permanecem corretamente marcadas como derivadas e não autoritativas.

A navegação também está fechada: README geral, índice clicável PT/EN, catálogo, cronologia e **20 índices temáticos**. O gate restaurado retornou:

`documents=11 · translations=11 · library_refs=60 · topics=20 · links=valid`

[**README da biblioteca**](sandbox:/mnt/data/tare-tools-research-README.md)  
[**Índice navegável de documentos**](sandbox:/mnt/data/tare-tools-document-index.md)

A arqueologia da File Library está formalizada em **60 referências**, sem reconstruir originals usando snippets. A fila distingue o que é referência, o que precisa de bytes exatos e o que depois precisa de tradução.

[**Rehydration Queue**](sandbox:/mnt/data/tare-tools-rehydration-queue.md)

Melhorei também a identidade futura desses arquivos: para Governance/Audit, Interoperability e Reliability recuperamos manifests independentes que registram os hashes e tamanhos exatos de seis HTMLs. fileciteturn14file0 fileciteturn14file1 fileciteturn14file2 Esses valores agora são **expected identity constraints**, não falsamente tratados como hashes de bytes que possuímos.

[**Identity Assertions**](sandbox:/mnt/data/tare-tools-identity-assertions.md)

A reconciliação de lineage também avançou. Temos **22 famílias identificadas**, mas o sistema deliberadamente não cria `supersedes` apenas por filename/data. Há quatro grupos de títulos duplicados mantidos como ambíguos até podermos comparar os conteúdos exatos.

[**Lineage Reconciliation**](sandbox:/mnt/data/tare-tools-lineage-reconciliation.md)

Também construí o primeiro catálogo normalizado de fontes: os 11 originals materializados produziram **86 URLs externas únicas**, com normalização de parâmetros como `utm_*`. Isso é índice/provenance — não declaração automática de que uma fonte continua vigente.

[**Source Index**](sandbox:/mnt/data/tare-tools-source-index.md)

### Publisher

A infraestrutura de publicação está bem além do skeleton inicial.

Já temos:

```text id="dgcj4x"
Publication Packet
        ↓
schema / policy
        ↓
deterministic routing
        ↓
filesystem backend
        │
        ├── local Git backend
        │      ├── dry-run
        │      ├── frozen base SHA
        │      ├── disposable worktree
        │      ├── isolated branch
        │      ├── local commit
        │      └── idempotent replay
        │
        └── GitHub CLI backend
               ├── dry-run by default
               ├── explicit repo identity
               ├── explicit remote-effect authorization
               ├── origin verification
               ├── push branch
               └── PR only — never auto-merge
```

Na árvore restaurada, o publisher passou **9/9 testes**.

Os gates continuam preservando:

```text id="kupwf7"
RESEARCH → research repo         ALLOW

TARGET → research repo           DENY

canonical change
sem Promotion Packet             DENY

GitHub remote effect
sem --apply                      DENY

GitHub remote effect
sem --allow-remote-effects       DENY
```

Portanto, o futuro backend GitHub não permitirá que “fechar uma pesquisa” signifique silenciosamente alterar North Star, ADR ou SPEC.

### Baseline canônico

Também deixei pronto um `pin_canonical_baseline.py`.

Quando recebermos o Git real do `tare-tools`, ele poderá registrar:

```text id="5r10ep"
repository identity
HEAD
branch
selected canonical paths
file SHA-256s
baseline timestamp
```

Assim um estudo futuro poderá dizer concretamente:

> “esta pesquisa foi produzida contra canonical commit X”

em vez de apenas “North Star de agosto”.

---

## O que ainda ficou faltando

Neste ponto os blockers são **externos**, não trabalho local incompleto:

1. **60 referências da File Library ainda não têm bytes brutos materializáveis nesta runtime.** Dessas, 41 são PT-BR e portanto continuam bloqueadas para tradução. Não vou fabricar originals a partir de snippets.
2. **O antigo Master Research Corpus ZIP ainda não foi recuperado como bytes.** Temos apenas o registro histórico de seu SHA-256 `7b655e2879a3033d2d2162fa82f77bb4e8ffc38f365d24ed7a00b077b0cd5ce3`.
3. **O Git real do `tare-tools` não está montado aqui.** Portanto não posso ainda fazer reconciliation real `research → CURRENT/TARGET` nem pin do baseline canônico.
4. **GitHub ainda não foi ativado.** Nesta runtime não há `gh` autenticado e eu não criei repos, não fiz push e não abri PR.
5. **Revisão editorial humana das traduções EN é opcional e continua pendente.** A tradução automática e o QA estrutural estão concluídos.

Isso também está registrado dentro do próprio bootstrap:

[**Completion Status**](sandbox:/mnt/data/tare-tools-document-repository-completion-status.md)

[**Blockers — JSON machine-readable**](sandbox:/mnt/data/tare-tools-document-repository-blockers.json)

[**Review Status**](sandbox:/mnt/data/tare-tools-review-status.md)

### Estado final desta etapa

Eu classificaria assim:

```text id="bq5ezi"
Document repository architecture       COMPLETE
Research repository skeleton           COMPLETE
Publisher repository skeleton          COMPLETE

11 seed originals                      COMPLETE
11 English translations                COMPLETE
Translation structural QA              COMPLETE

Human navigation                       COMPLETE
Machine catalog                        COMPLETE
Topic organization                     COMPLETE

File Library discovery                 COMPLETE for current pass
Exact-byte historical rehydration      BLOCKED externally
Lineage metadata reconciliation        COMPLETE
Content-level lineage proof            BLOCKED by missing bytes

External source index                  COMPLETE for materialized corpus

Filesystem publication                 COMPLETE
Local Git publication                  COMPLETE
GitHub dry-run adapter                  COMPLETE
GitHub remote publication              NOT ACTIVATED

Canonical tare.tools baseline tooling  COMPLETE
Real canonical baseline                BLOCKED by repo availability

Checkpoint / ZIP / restore proof       COMPLETE
```

Então, **a etapa offline/local está concluída**. O próximo salto útil já não é “escrever mais infraestrutura”: é dar ao sistema **os dois recursos externos que faltam** — o Git real do `tare-tools` e uma superfície GitHub autenticada — e continuar exportando/materializando os documentos históricos que ainda estão apenas na File Library.

A partir daí conseguimos finalmente passar de:

**biblioteca construída**

para:

**biblioteca privada persistida no GitHub + publicação praticamente automática a partir dos nossos chats**.