# tare.tools.library

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/augusto-scarvalho/tare.tools.library/actions/workflows/ci.yml/badge.svg)](https://github.com/augusto-scarvalho/tare.tools.library/actions/workflows/ci.yml)

*The English version is [README.md](README.md); this file mirrors it.*

`tare.tools.library` é o acervo de pesquisa e a camada de busca do ecossistema `tare.tools`. Ele faz duas coisas:

1. **Pesquisa própria da Library** em [`docs/research/`](docs/research/), indexada por [`docs/INDEX.md`](docs/INDEX.md).
2. **Um índice de busca derivado e reconstruível**: busca léxica e um índice vetorial incremental em SQLite alimentado
   por um servidor local de embeddings compatível com OpenAI. O índice lê os documentos onde eles moram: os da
   própria Library e os checkouts de outros repositórios passados como `--owner-root REPOSITORIO=CAMINHO`. Um
   documento de outro repositório fica lá; a Library não guarda cópia, entrada de catálogo nem fixação dele e nunca é
   autoridade para ancorar trabalho ([ADR-070](docs/adr/ADR-070_LIBRARY_AS_DERIVED_RETRIEVAL_INDEX.md)).

Os requisitos da própria Library estão em [`specs/SPEC-LIBRARY-001.md`](specs/SPEC-LIBRARY-001.md).

## Relação com o tare.tools.os

O [`tare.tools.os`](https://github.com/augusto-scarvalho/tare.tools.os) fixa este repositório como submódulo Git em
`satellites/tare.tools.library`. O OS ancora o trabalho em especificações e ADRs lidos da própria árvore e dos
satélites, não da Library; seus guias executam `python -m tools.query` a partir do submódulo para pesquisa e busca.
Este repositório não importa o OS; ele funciona sozinho.

## Requisitos

- Python 3.10 ou mais novo (o CI usa 3.12) e Git.
- Os pacotes de [`requirements-editorial.txt`](requirements-editorial.txt) (pytest, BeautifulSoup, PyYAML).
  Nada mais é necessário para validação, busca léxica ou os testes.
- Opcional: um servidor de chat e embeddings compatível com OpenAI (por exemplo o `llama-server` do `llama.cpp`) para
  busca semântica, resumos e indexação vetorial, e um host com GPU acessível por SSH para tarefas pesadas. Nenhum
  comando baixa modelos.

## Instalar e testar a partir de um clone novo

```powershell
git clone https://github.com/augusto-scarvalho/tare.tools.library.git
cd tare.tools.library
python -m venv .venv
.venv\Scripts\activate            # no Linux ou macOS: source .venv/bin/activate
python -m pip install -r requirements-editorial.txt
python -m pytest tests -q
```

O CI executa a mesma suíte (`pytest tests/ -v` e `python -m unittest discover -s tests`) e o guarda do changelog.

## Comandos comuns

```powershell
python -m tools.query --search "retrieval"          # busca léxica nos documentos próprios da Library
python -m tools.query --spec SPEC-LIBRARY-001       # mostra uma especificação pelo id
python -m tools.query --adr ADR-070                 # mostra um ADR pelo id
python -m tools.bookkeeper.cli audit --root docs    # auditoria de duplicatas e de fonte única da verdade
```

Para consultar um conceito na ontologia de domínio de outro repositório, passe o checkout dele:
`python -m tools.query --concept CASPersistence --owner-root tare.tools.kernel=../tare.tools.kernel`. Veja
[o guia de propriedade](docs/DOCUMENT_OWNERSHIP.md).

Busca semântica e indexação precisam do servidor de embeddings:

```powershell
python -m tools.indexer.embed_corpus --root .       # incremental: só arquivos alterados são vetorizados
python -m tools.indexer.embed_corpus --root . --owner-root tare.tools.os=../tare.tools.os   # também um checkout dono
python -m tools.query --semantic "context compaction" --limit 5
```

A busca padrão lê apenas documentos ativos da Library e indexa bytes idênticos uma única vez
([`tools/document_scope.py`](tools/document_scope.py)). `--include-history` também lê `docs/archive/` e
`catalog/corpus/` quando um checkout local os tem; o repositório em si não versiona mais nenhum dos dois.

## Configurar inferência e o host de computação

Endereços, usuários e caminhos pertencem ao seu ambiente; o código usa loopback e a configuração do próprio SSH por
padrão.

| Variável | Finalidade | Padrão |
| --- | --- | --- |
| `LOCAL_LLM_ENDPOINT` / `SLOP_ENDPOINT` | Servidor de chat, sem `/v1` | `http://localhost:8080` |
| `LOCAL_EMBED_ENDPOINT` / `SLOP_EMBED_ENDPOINT` | Servidor de embeddings | `http://localhost:8081`; segue um servidor de chat selecionado explicitamente quando omitido |
| `TARE_MESH_HOST` | Host de computação SSH ou alias SSH | `localhost` |
| `TARE_MESH_USER` | Usuário SSH | configuração do SSH |
| `TARE_MESH_REMOTE_ROOT` | Checkout da Library no host de computação | `~/src/tare.tools.library` |
| `TARE_MESH_WSL_DISTRO` | Distribuição WSL em um host SSH Windows | não definida (shell Linux remoto) |
| `TARE_THIN_CLIENT_HOSTNAMES` | Nomes de laptops, separados por vírgula, em que lotes pesados são recusados, mesmo com CUDA | hosts sem CUDA já são recusados |
| `TARE_MESH_DAEMON_START` | Comando que inicia um servidor de inferência e modelo já existentes | obrigatório para `mesh daemon start` |

```powershell
$env:TARE_MESH_HOST = "compute-node"
$env:TARE_MESH_REMOTE_ROOT = "/srv/tare.tools.library"
$env:TARE_MESH_WSL_DISTRO = "Ubuntu-24.04"            # só para um host SSH Windows
python tools/mesh/mesh.py status
python tools/mesh/mesh.py sync                       # envia este checkout ao host por SSH
python -m tools.bookkeeper.dispatch_job --task embed-corpus
```

Argumentos de construtor têm precedência sobre estas variáveis.

## Estrutura do repositório

```text
tare.tools.library/
├── .githooks/          # guarda de changelog no pre-push (python tools/install_git_hooks.py)
├── .github/workflows/  # CI: testes, guarda do changelog
├── catalog/            # registro de capacidades, schemas
├── docs/
│   ├── adr/            # decisões que regem a Library
│   ├── assurance/      # registros de execução de protocolos de pesquisa
│   ├── guides/         # conteúdo do repositório e registros privados
│   ├── policies/       # políticas de documentos, promoção, tradução e artigos HTML
│   ├── research/       # pesquisa própria da Library
│   └── templates/      # modelos de experimento e de especificação
├── specs/              # SPEC-LIBRARY-001
├── tests/              # suíte de testes
└── tools/              # busca, indexador, bookkeeper, mesh, inferência, governança
```

A suíte de testes também impõe um orçamento de 50 MB para os arquivos versionados e recusa transcrições de chat
versionadas ([`tests/test_frugality_guard.py`](tests/test_frugality_guard.py)).

## Onde cada documento fica

- Especificações, arquitetura e operação de uma ferramenta: no repositório dela.
- Governança e liquidação de todo o ecossistema: `tare.tools.os`.
- Pesquisa, curadoria, busca e ferramentas da Library: aqui.
- Documentos e ontologias externos: nos repositórios donos, onde o índice os lê.

Material obsoleto é apagado em vez de arquivado; o histórico do Git o preserva. Veja
[CONTRIBUTING.md](CONTRIBUTING.md) e [AGENTS.md](AGENTS.md).

## Repositórios relacionados

| Repositório | Papel |
| :--- | :--- |
| [`tare.tools.os`](https://github.com/augusto-scarvalho/tare.tools.os) | Orquestração, autoridade e liquidação do ecossistema |
| [`tare.tools.kernel`](https://github.com/augusto-scarvalho/tare.tools.kernel) | Runtime de cinco planos |
| [`tare.tools.specgraph`](https://github.com/augusto-scarvalho/tare.tools.specgraph) | Rastreabilidade de especificações e análise de impacto |
| [`tare.tools.backlog-graph`](https://github.com/augusto-scarvalho/tare.tools.backlog-graph) | Grafo de tarefas |

## Licença

Apache License 2.0. Veja [LICENSE](LICENSE).
