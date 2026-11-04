# tare.tools.library

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/augusto-scarvalho/tare.tools.library/actions/workflows/ci.yml/badge.svg)](https://github.com/augusto-scarvalho/tare.tools.library/actions/workflows/ci.yml)

*Uma versão em português está em [README.pt-BR.md](README.pt-BR.md).*

`tare.tools.library` is the research collection and retrieval layer of the `tare.tools` ecosystem. It does two
things:

1. **Library-owned research** in [`docs/research/`](docs/research/), indexed by [`docs/INDEX.md`](docs/INDEX.md).
2. **A derived, rebuildable retrieval index**: lexical search, and an incremental SQLite vector index fed by a local
   OpenAI-compatible embedding server. The index reads documents where they live: the Library's own, and other
   repositories' checkouts passed as `--owner-root REPOSITORY=PATH`. A document owned by another repository stays
   there; the Library keeps no copy, catalog entry or pin of it and is never an authority for grounding
   ([ADR-070](docs/adr/ADR-070_LIBRARY_AS_DERIVED_RETRIEVAL_INDEX.md)).

Its own requirements are in [`specs/SPEC-LIBRARY-001.md`](specs/SPEC-LIBRARY-001.md).

## Relation to tare.tools.os

[`tare.tools.os`](https://github.com/augusto-scarvalho/tare.tools.os) pins this repository as a Git submodule at
`satellites/tare.tools.library`. The OS grounds work on specifications and ADRs read from its own tree and its
satellites, not from the Library; its guides run `python -m tools.query` from the submodule for research and
retrieval. This repository does not import the OS; it works on its own.

## Requirements

- Python 3.10 or newer (CI uses 3.12) and Git.
- The packages in [`requirements-editorial.txt`](requirements-editorial.txt) (pytest, BeautifulSoup, PyYAML).
  Nothing else is needed for validation, lexical search or the tests.
- Optional: an OpenAI-compatible chat and embedding server (for example `llama.cpp`'s `llama-server`) for semantic
  search, summaries and vector indexing, and an SSH-reachable GPU host for heavy jobs. No command downloads a model.

## Install and test from a fresh clone

```powershell
git clone https://github.com/augusto-scarvalho/tare.tools.library.git
cd tare.tools.library
python -m venv .venv
.venv\Scripts\activate            # on Linux or macOS: source .venv/bin/activate
python -m pip install -r requirements-editorial.txt
python -m pytest tests -q
```

CI runs the same suite (`pytest tests/ -v`, and `python -m unittest discover -s tests`) and the changelog guard.

## Common commands

```powershell
python -m tools.query --search "retrieval"          # lexical search over Library-owned documents
python -m tools.query --spec SPEC-LIBRARY-001       # print a specification by id
python -m tools.query --adr ADR-070                 # print an ADR by id
python -m tools.bookkeeper.cli audit --root docs    # duplicate and single-source-of-truth audit
```

To look up a concept in another repository's domain ontology, pass its checkout:
`python -m tools.query --concept CASPersistence --owner-root tare.tools.kernel=../tare.tools.kernel`. See
[the ownership guide](docs/DOCUMENT_OWNERSHIP.md).

Semantic search and indexing need the embedding server:

```powershell
python -m tools.indexer.embed_corpus --root .       # incremental: only changed files are embedded
python -m tools.indexer.embed_corpus --root . --owner-root tare.tools.os=../tare.tools.os   # also an owner checkout
python -m tools.query --semantic "context compaction" --limit 5
```

Default retrieval reads only active Library documents and indexes identical bytes once
([`tools/document_scope.py`](tools/document_scope.py)). `--include-history` also reads `docs/archive/` and
`catalog/corpus/` when a local checkout has them; the repository itself no longer tracks either.

## Configure inference and the compute host

Addresses, users and paths belong in your environment; the code defaults to loopback and to SSH's own
configuration.

| Variable | Purpose | Default |
| --- | --- | --- |
| `LOCAL_LLM_ENDPOINT` / `SLOP_ENDPOINT` | Chat server, without `/v1` | `http://localhost:8080` |
| `LOCAL_EMBED_ENDPOINT` / `SLOP_EMBED_ENDPOINT` | Embedding server | `http://localhost:8081`; follows an explicitly selected chat server when omitted |
| `TARE_MESH_HOST` | SSH compute host or SSH alias | `localhost` |
| `TARE_MESH_USER` | SSH user | SSH configuration |
| `TARE_MESH_REMOTE_ROOT` | Library checkout on the compute host | `~/src/tare.tools.library` |
| `TARE_MESH_WSL_DISTRO` | WSL distribution on a Windows SSH host | unset (remote Linux shell) |
| `TARE_THIN_CLIENT_HOSTNAMES` | Comma-separated laptop names on which heavy batches are refused, even with CUDA | hosts without CUDA are already refused |
| `TARE_MESH_DAEMON_START` | Command that starts an existing inference server and model | required for `mesh daemon start` |

```powershell
$env:TARE_MESH_HOST = "compute-node"
$env:TARE_MESH_REMOTE_ROOT = "/srv/tare.tools.library"
$env:TARE_MESH_WSL_DISTRO = "Ubuntu-24.04"            # only for a Windows SSH host
python tools/mesh/mesh.py status
python tools/mesh/mesh.py sync                       # streams this checkout to the host over SSH
python -m tools.bookkeeper.dispatch_job --task embed-corpus
```

Constructor arguments override these variables.

## Repository layout

```text
tare.tools.library/
├── .githooks/          # pre-push changelog guard (python tools/install_git_hooks.py)
├── .github/workflows/  # CI: tests, changelog guard
├── catalog/            # capability registry, schemas
├── docs/
│   ├── adr/            # decisions that govern the Library
│   ├── assurance/      # research-protocol run records
│   ├── guides/         # repository content and private records
│   ├── policies/       # document, promotion, translation and HTML article policies
│   ├── research/       # Library-owned research
│   └── templates/      # experiment and specification templates
├── specs/              # SPEC-LIBRARY-001
├── tests/              # test suite
└── tools/              # query, indexer, bookkeeper, mesh, inference, governance
```

The test suite also enforces a 50 MB budget on tracked files and refuses tracked chat transcripts
([`tests/test_frugality_guard.py`](tests/test_frugality_guard.py)).

## Where documents go

- A tool's specifications, architecture and operations: that tool's repository.
- Ecosystem-wide governance and settlement: `tare.tools.os`.
- Research, curation, retrieval and Library tooling: here.
- External documents and ontologies: in their owners' repositories, where the index reads them.

Obsolete material is deleted rather than archived; Git history keeps it. See
[CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).

## Related repositories

| Repository | Role |
| :--- | :--- |
| [`tare.tools.os`](https://github.com/augusto-scarvalho/tare.tools.os) | Ecosystem orchestration, authority and settlement |
| [`tare.tools.kernel`](https://github.com/augusto-scarvalho/tare.tools.kernel) | Five-plane runtime |
| [`tare.tools.specgraph`](https://github.com/augusto-scarvalho/tare.tools.specgraph) | Specification traceability and impact analysis |
| [`tare.tools.backlog-graph`](https://github.com/augusto-scarvalho/tare.tools.backlog-graph) | Task graph |

## License

Apache License 2.0. See [LICENSE](LICENSE).
